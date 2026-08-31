"""Export immutable Git checkpoints into a single review repository.

This performs artifact generation, never edits worker trees or publishes Git.
Inventory is local configuration; its Worktree identifiers are not published.
All output is confined to destination/translations, a publisher-owned namespace.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

try:
    from portable_transform import transform as code_transform
except ImportError:
    def code_transform(path, data):
        return data, []

HOST = re.compile(r"(?i)[A-Z]:[\\/]+Users[\\/]+(?:memo_|memo)(?=[\\/]|$)")
TASK = re.compile(r"(?<![0-9a-f])01a0[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?![0-9a-f])", re.I)
RAW_QUOTES = [re.compile(r'There\s+are\s+idle\s+sessions\..{0,700}?all\s+of\s+them\s+now\.', re.S), re.compile(r'You\s+send\s+the\s+global\s+question.{0,500}?If\s+not,\s+check\s+against\s+your\s+source\s+canon\.', re.S)]
SECRET = re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)")
RAW_NAMES = {'USER_INSTRUCTIONS.md', 'USER_INSTRUCTIONS_VERBATIM.md', 'USER_UPDATES.md', 'MANAGEMENT_USER_REQUEST.md'}
CODE = {'.py', '.js', '.cjs', '.mjs', '.ps1', '.sh'}

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])

def sha(data):
    return hashlib.sha256(data).hexdigest()

def text_transform(path, data):
    labels = []
    if SECRET.search(data):
        raise ValueError(f'Possible credential in project file: {path}; review locally before export')
    if Path(path).suffix in CODE:
        data, labels = code_transform(path, data)
    if b'\x00' in data[:8192]:
        return data, labels
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        return data, labels
    if HOST.search(text):
        if Path(path).suffix in CODE and path != 'te-Telu-IN/scripts/seal_archives.py':
            raise ValueError(f'Unparameterized private host path in code: {path}')
        text = HOST.sub('[local-home]', text)
        labels.append('private home prefix replaced with [local-home]; historical input hashes remain original')
    if TASK.search(text):
        text = TASK.sub('[local-task-id]', text)
        labels.append('operational task identifiers removed')
    for pattern in RAW_QUOTES:
        text, count = pattern.subn('[Operational message omitted from public export; full-assignment and continual canon-consultation requirements remain in the project workflow.]', text)
        if count:
            labels.append('embedded verbatim operational chat omitted; surrounding linguistic evidence retained')
    return text.encode('utf-8'), labels

def transform(path, data):
    if Path(path).suffix.lower() in {'.zip', '.epub', '.docx'}:
        buf = io.BytesIO(data)
        if not zipfile.is_zipfile(buf):
            raise ValueError(f'Invalid archive: {path}')
        changes = []
        members = []
        with zipfile.ZipFile(buf) as source:
            for info in source.infolist():
                name = PurePosixPath(info.filename)
                if name.is_absolute() or '..' in name.parts:
                    raise ValueError(f'Unsafe archive member: {path}:{name}')
                payload = source.read(info)
                if name.name in RAW_NAMES:
                    changes.append(f'excluded raw operational instruction member {name}')
                    continue
                edited, labels = text_transform(str(name), payload)
                if labels:
                    changes.extend(f'{name}: {label}' for label in labels)
                members.append((info, edited))
        if changes:
            from archive_transform import repair_archive
            members, repair_labels = repair_archive(members)
            changes.extend(repair_labels)
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w') as target:
                for info, payload in members:
                    target.writestr(info, payload)
            return out.getvalue(), changes
        return data, []
    return text_transform(path, data)

class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        if tag not in {'img', 'script', 'link'}:
            return
        for key, value in attrs:
            if key in {'href', 'src'} and value:
                self.refs.append(value)

OUTPUT_ROOT = None
PREVIOUS_HASHES = {}

def write_if_changed(path, data, generated=False):
    if OUTPUT_ROOT is None or OUTPUT_ROOT.resolve() not in path.resolve().parents:
        raise ValueError(f'Output escapes publisher namespace: {path}')
    for ancestor in [path, *path.parents]:
        if ancestor.is_symlink() or getattr(ancestor, 'is_junction', lambda: False)():
            raise ValueError(f'Redirected output path: {path}')
        if ancestor == OUTPUT_ROOT:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != data:
        previous_hash = PREVIOUS_HASHES.get(path)
        if path.exists() and previous_hash is None and not generated:
            raise ValueError(f'Unregistered destination file would be overwritten: {path}')
        if path.exists() and previous_hash and sha(path.read_bytes()) != previous_hash:
            raise ValueError(f'Review edit conflicts with new export; preserve and resolve before retrying: {path}')
        path.write_bytes(data)

def main():
    global OUTPUT_ROOT, PREVIOUS_HASHES
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--worktrees', type=Path, default=Path.home()/'.codex'/'worktrees')
    args = parser.parse_args()
    destination = args.destination.resolve()
    if git(destination, 'rev-parse', '--show-toplevel').decode().strip().replace('\\', '/') != str(destination).replace('\\', '/'):
        raise ValueError('Destination must be an existing Git repository root')
    if git(destination, 'branch', '--show-current').decode().strip() != 'codex/additional-translations-review':
        raise ValueError('Wrong destination branch')
    if shutil.disk_usage(destination).free < 700_000_000:
        raise ValueError('Less than 700 MB disk free; stop without cleanup')
    target = destination/'translations'
    OUTPUT_ROOT = target
    inventory = json.loads(args.inventory.read_text(encoding='utf-8-sig'))
    previous_path = target/'EXPORT_MANIFEST.json'
    previous = json.loads(previous_path.read_text('utf-8')) if previous_path.exists() else None
    PREVIOUS_HASHES = {target/record['path']:record['export_sha256'] for record in previous['files']} if previous else {}
    manifest = {'schema':'translation-review-export-v1', 'snapshot_policy':'Immutable committed checkpoints; not a claim of linguistic approval. Uncommitted work remains with its owner until a consistent checkpoint.', 'lanes':[], 'files':[], 'excluded':[], 'limitations':['No full clean-PC builds or native/educator/assistive-technology approval asserted.', 'Transformed exports are derivatives: original QA hashes describe original bytes, not transformed files.', 'Ignored bulk source/canon inputs are not copied; reacquire the exact worker pins when required.', 'Javanese sources.lock redaction changes its hash; hash-bound validators require reviewed derivative rebinding before a full rebuild. Offline reader bytes remain unchanged.']}
    expected = set()
    for lane in inventory['lanes']:
        source = args.worktrees/lane['Worktree']/'LAN ALLOC'
        prefix = lane['LocaleRoot']
        locale = PurePosixPath(prefix).name
        head = git(source, 'rev-parse', 'HEAD').decode().strip()
        root = target/locale/'workspace'
        tree = git(source, 'ls-tree', '-r', '-z', head, '--', prefix).split(b'\0')
        blobs = {}
        for entry in tree:
            if not entry: continue
            meta, name = entry.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            if kind != 'blob' or mode == '120000':
                raise ValueError(f'Unsupported tree entry {name!r}')
            blobs[name.decode('utf-8')] = oid
        # Attributes are root-relative and must remain at the same workspace depth.
        extras = ['.gitattributes'] if git(source, 'ls-tree', head, '--', '.gitattributes') else []
        proc = subprocess.Popen(['git','-C',str(source),'archive','--format=tar',head,prefix,*extras], stdout=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=proc.stdout, mode='r|') as archive:
                for member in archive:
                    if member.isdir(): continue
                    path = PurePosixPath(member.name)
                    if not member.isfile() or path.is_absolute() or '..' in path.parts:
                        raise ValueError(f'Unsafe archive entry {member.name}')
                    data = archive.extractfile(member).read()
                    rel = (Path(locale)/'workspace'/member.name).as_posix()
                    if path.name in RAW_NAMES:
                        manifest['excluded'].append({'locale':locale,'path':member.name,'source_sha256':sha(data),'reason':'raw operational user/task instructions; not translation content'})
                        continue
                    exported, labels = transform(member.name, data)
                    if len(exported) > 95_000_000:
                        raise ValueError(f'Individual file exceeds review Git size policy: {rel}')
                    write_if_changed(root/member.name, exported)
                    expected.add(rel)
                    record = {'path':rel,'source_path':member.name,'source_commit':head,'source_blob':blobs.get(member.name) or git(source,'rev-parse',f'{head}:{member.name}').decode().strip(),'source_sha256':sha(data),'export_sha256':sha(exported),'bytes':len(exported)}
                    if labels: record['transformations'] = labels
                    manifest['files'].append(record)
            if proc.wait() != 0: raise ValueError(f'git archive failed for {locale}')
        finally:
            if proc.poll() is None: proc.kill()
            proc.stdout.close()
        dirty = git(source,'status','--porcelain=v1','--untracked-files=all','--',prefix).decode('utf-8').splitlines()
        manifest['lanes'].append({'locale':locale,'original_prefix':prefix,'source_commit':head,'source_commit_time':git(source,'show','-s','--format=%cI',head).decode().strip(),'workspace':f'{locale}/workspace','uncommitted_paths_not_exported':len(dirty),'status':'saved review checkpoint; unfinished assignment; see original scoped QA and export limitations'})
        print(f'{locale}: {head} exported; {len(dirty)} changing/uncommitted paths deferred',flush=True)
    # Remove only obsolete files previously registered by this publisher. Never
    # recursively delete a workspace or any original worker path.
    if previous:
        for record in previous['files']:
            rel = record['path']
            if rel in expected: continue
            candidate = (target/rel).resolve()
            if target.resolve() not in candidate.parents:
                raise ValueError('Previous manifest path escapes export root')
            if candidate.is_file():
                if sha(candidate.read_bytes()) != record['export_sha256']:
                    raise ValueError(f'Locally changed obsolete export: {rel}')
                candidate.unlink()
    html_count = refs_count = 0
    for record in manifest['files']:
        path = target/record['path']
        if sha(path.read_bytes()) != record['export_sha256']:
            raise ValueError(f'Export verification mismatch: {path}')
        if path.suffix == '.py':
            compile(path.read_bytes(), str(path), 'exec')
        if path.suffix.lower() == '.html':
            html_count += 1
            reader = Resources()
            reader.feed(path.read_text('utf-8'))
            for ref in reader.refs:
                parsed = urlsplit(ref)
                if parsed.scheme or parsed.netloc or not parsed.path: continue
                refs_count += 1
                resource = (path.parent/unquote(parsed.path)).resolve()
                if not resource.is_file():
                    raise ValueError(f'Missing HTML resource: {record["path"]} -> {ref}')
    manifest['validation'] = {'sha256_all_exported_files':True,'python_syntax':True,'html_readers':html_count,'local_img_script_link_resources':refs_count,'limits':'No browser, full builds, CSS url/srcset, anchor, native-language or accessibility review performed by exporter.'}
    # Content-derived timestamp allows unchanged runs to avoid pointless commits.
    manifest['snapshot_latest_commit_time'] = max(x['source_commit_time'] for x in manifest['lanes'])
    write_if_changed(previous_path, (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'), generated=True)
    rows = '\n'.join(f'| {x["locale"]} | `{x["source_commit"][:12]}` | [Workspace]({x["workspace"]}/{x["original_prefix"]}/) | {x["uncommitted_paths_not_exported"]} |' for x in manifest['lanes'])
    text = f'''# Additional mathematics translations — review branch

Actual saved translation sources, offline readers/assets, tools, and scoped provenance/QA for all nine language tasks. This is a continuing **review branch**, not a production release and not nine completed assignments. Download once and review what is ready; the coordinator updates this branch as tasks save further consistent checkpoints.

[Other-PC download and rebuild guide](../review-management/REVIEW_GUIDE.md) · [Upstream changes](../review-management/UPSTREAM_CHANGES.md) · [File/hash manifest](EXPORT_MANIFEST.json)

| Language/locale | Original local checkpoint | Files | Changing/uncommitted paths deferred |
|---|---|---|---:|
{rows}

Captured {len(manifest['files'])} files / {sum(x['bytes'] for x in manifest['files']):,} bytes. {html_count} HTML files and {refs_count} local img/script/link references checked. Original reader QA describes its original checkpoint and declared scope, not blanket publication approval. Newer inconsistent work remains local until its owner checkpoints it; counts above are paths, not translation volume.

Raw operational user instructions are excluded. Private host/task locators in useful records are redacted; executable donor/runtime paths are parameterized where necessary. EXPORT_MANIFEST.json records original Git blob and SHA-256, export SHA-256, every transformation and excluded instruction file. Historical locks/QA are not silently rewritten to certify changed bytes. Javanese lock-bound checks in particular require deliberate derivative rebinding before full rebuild; saved offline readers remain available unchanged.

Ignored upstream/canon corpora are not duplicated. Keep each workspace's original nesting and byte-preservation attributes. Follow its exact source locks and the guide's rebuild limits rather than substituting current upstream main. Continuously reconsult readable target-language canon during further drafting, revision and review.
'''
    write_if_changed(target/'README.md',text.encode('utf-8'), generated=True)
    # Copy the small, explicitly public management packet as generated artifacts.
    staging = Path(__file__).resolve().parent
    OUTPUT_ROOT = destination/'review-management'
    for name in ('REVIEW_GUIDE.md','HOURLY_WORKFLOW.md','UPSTREAMS.json','UPSTREAM_CHANGES.md'):
        source_file = staging/name
        payload, labels = text_transform(name, source_file.read_bytes())
        if labels:
            raise ValueError(f'Unexpected private material in reviewed management packet: {name}')
        write_if_changed(OUTPUT_ROOT/name,payload,generated=True)
    for name in ('export_translations.py','portable_transform.py','archive_transform.py'):
        write_if_changed(OUTPUT_ROOT/'tools'/name,(staging/name).read_bytes(),generated=True)
    goal = staging.parent/'TRANSLATION_MANAGEMENT_GOAL.md'
    if goal.exists():
        payload, _ = text_transform('TEAM_GOAL.md',goal.read_bytes())
        write_if_changed(OUTPUT_ROOT/'TEAM_GOAL.md',payload,generated=True)
    print(json.dumps({'files':len(manifest['files']),'bytes':sum(x['bytes'] for x in manifest['files']),'transformed':sum('transformations' in x for x in manifest['files']),'excluded':len(manifest['excluded']),'validation':manifest['validation']},indent=2),flush=True)

if __name__ == '__main__':
    main()
