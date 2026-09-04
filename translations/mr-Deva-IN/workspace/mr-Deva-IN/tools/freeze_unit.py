"""Freeze selected A20/A30 members for a new unit, never extract a whole corpus.

The existing sources.lock.json supplies immutable archive pins. Original module
bytes and serialized XML selections are identified separately. All selected
rasters receive ignored review copies. Only explicitly referenced asset: images
are also pinned and copied, unchanged, from the canonical English archive into
the reader's small committed asset directory.
"""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

BASE = Path(__file__).resolve().parents[1]
CN = '{http://cnx.rice.edu/cnxml}'
MATH = '{http://www.w3.org/1998/Math/MathML}math'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_selected(outputs):
    """Stage all selected bytes before replacing any existing checkpoint file."""
    staged = []
    try:
        for destination, data in outputs:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent,
                                             prefix=destination.name+'.',
                                             suffix='.tmp', delete=False) as handle:
                staged.append((Path(handle.name), destination))
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        for temporary, destination in staged:
            os.replace(temporary, destination)
    finally:
        for temporary, _ in staged:
            if temporary.exists():
                temporary.unlink()


def review_images(unit, course, names):
    """Copy only named pinned source rasters into the same ignored QA directory."""
    if not re.fullmatch(r'MR-BRIDGE-\d{3}', unit) or course not in ('A20', 'A30'):
        raise ValueError('invalid unit/course')
    if not names or any(not re.fullmatch(r'[A-Za-z0-9_.-]+\.(jpg|png)', name) for name in names):
        raise ValueError('invalid image names')
    master = json.loads((BASE/'sources.lock.json').read_bytes())
    pins = {item['id']: item for item in master['archives']}
    pending = []
    for locale in ('en', 'id'):
        pin = pins[f'{course}-{locale}']
        archive_path = BASE.parent/pin['path']
        if archive_path.stat().st_size != pin['bytes']:
            raise ValueError('archive byte count drift')
        with archive_path.open('rb') as handle:
            if hashlib.file_digest(handle, 'sha256').hexdigest() != pin['sha256']:
                raise ValueError('archive hash drift')
        with zipfile.ZipFile(archive_path) as archive:
            for name in names:
                candidates = [n for n in archive.namelist() if n.endswith('/media/'+name)]
                if course == 'A30' and locale == 'id':
                    candidates = [n for n in candidates if n.startswith('repo/source/')]
                if len(candidates) != 1:
                    raise ValueError('ambiguous image member: '+name)
                data = archive.read(candidates[0])
                destination = BASE.parent/'downloads/mr-Deva-IN/source-image-qa'/unit/f'{locale}-{name}'
                pending.append((destination, data, locale, candidates[0]))
    write_selected([(destination, data) for destination, data, _, _ in pending])
    for destination, data, locale, member in pending:
        print(json.dumps({'locale':locale, 'member':member, 'sha256':sha(data),
                          'bytes':len(data), 'review_path':str(destination)}))


def freeze(unit):
    if not re.fullmatch(r'MR-BRIDGE-\d{3}', unit):
        raise ValueError('invalid unit name')
    master_raw = (BASE/'sources.lock.json').read_bytes()
    master = json.loads(master_raw)
    archive_pins = {item['id']: item for item in master['archives']}
    root = ET.parse(BASE/'translations'/f'{unit}.xml').getroot()
    requested_assets = set()
    for image in root.iter('img'):
        source = image.get('src', '')
        if not re.fullmatch(r'asset:[A-Za-z0-9][A-Za-z0-9_.-]{0,199}\.(jpg|jpeg|png)', source):
            raise ValueError('unsupported image reference: '+source)
        name = source[6:]
        if '..' in name:
            raise ValueError('unsafe image name')
        requested_assets.add(name)
    selected = [e for e in root.iter() if e.get('data-source')]
    if not selected:
        raise ValueError('no source selections')
    if (len({e.get('data-source') for e in selected}) != len(selected)
            or len({e.get('id') for e in selected}) != len(selected)):
        raise ValueError('duplicate source selection or target ID')
    selections = []
    witnesses = [{'path': 'sources.lock.json', 'sha256': sha(master_raw),
                  'bytes': len(master_raw), 'source': 'existing corpus lock'}]
    # Preserve the applicable original notice files without copying or editing them.
    courses = {e.get('data-source').split(':')[0] for e in selected}
    for item in master['witnesses']:
        if any(item['path'].startswith(f'provenance/notices/{course}-') or
               item['path'].startswith(f'provenance/{course}-v0.3.0/')
               for course in courses):
            if sha((BASE/item['path']).read_bytes()) != item['sha256']:
                raise ValueError('original notice drift: '+item['path'])
            witnesses.append(item)
    archives = {}
    modules = {}
    images = []
    pending = {}
    pending_images = {}
    with ExitStack() as stack:
        for block in selected:
            locator = block.get('data-source')
            match = re.fullmatch(r'(A20|A30):(m\d+)#([A-Za-z0-9_-]+)', locator)
            if not match:
                raise ValueError('unsupported source locator: '+locator)
            course, module, source_id = match.groups()
            if block.get('id') != source_id:
                raise ValueError('source wrapper ID must be preserved')
            record = {'locator': locator, 'target_id': source_id, 'sources': []}
            for locale in ('en', 'id'):
                key = f'{course}-{locale}'
                pin = archive_pins[key]
                if key not in archives:
                    path = BASE.parent/pin['path']
                    if path.stat().st_size != pin['bytes']:
                        raise ValueError('archive byte count drift: '+key)
                    with path.open('rb') as handle:
                        if hashlib.file_digest(handle, 'sha256').hexdigest() != pin['sha256']:
                            raise ValueError('archive hash drift: '+key)
                    archives[key] = stack.enter_context(zipfile.ZipFile(path))
                archive = archives[key]
                module_key = (key, module)
                if module_key not in modules:
                    candidates = [n for n in archive.namelist()
                                  if n.endswith(f'/modules/{module}/index.cnxml')]
                    if key == 'A30-id':
                        candidates = [n for n in candidates if n.startswith('repo/source/')]
                    if len(candidates) != 1:
                        raise ValueError('ambiguous module member: '+str(candidates))
                    member = candidates[0]
                    raw = archive.read(member)  # selected-member CRC is checked by zipfile
                    modules[module_key] = (member, raw, ET.fromstring(raw))
                member, raw, tree = modules[module_key]
                matches = [e for e in tree.iter() if e.get('id') == source_id]
                if len(matches) != 1:
                    raise ValueError('missing/duplicate source ID: '+locator)
                fragment = matches[0]
                data = ET.tostring(fragment, encoding='utf-8', xml_declaration=True)
                relative = f'provenance/{unit}/{locale}-{module}-{source_id}.xml'
                pending[relative] = data
                witnesses.append({'path': relative, 'sha256': sha(data), 'bytes': len(data),
                                  'source': f'{pin["path"]}:{member}#{source_id}',
                                  'serialization': 'ElementTree XML, not original byte slice'})
                source_record = {
                    'locale': locale, 'archive': pin['path'], 'archive_sha256': pin['sha256'],
                    'member': member, 'module_sha256': sha(raw), 'fragment_path': relative,
                    'fragment_sha256': sha(data),
                    'math_sha256': [sha(ET.tostring(e, encoding='utf-8'))
                                    for e in fragment.iter(MATH)],
                    'outgoing_urls': [e.get('url') for e in fragment.iter(CN+'link') if e.get('url')],
                }
                record['sources'].append(source_record)
                for element in fragment.iter(CN+'image'):
                    source = element.get('src', '')
                    if not source or '\\' in source or ':' in source:
                        raise ValueError('unsafe archive image source')
                    image_member = posixpath.normpath(posixpath.join(posixpath.dirname(member), source))
                    if image_member.startswith('../') or image_member.startswith('/'):
                        raise ValueError('unsafe archive image member')
                    if sum(item.filename == image_member for item in archive.infolist()) != 1:
                        raise ValueError('missing/duplicate archive image member: '+image_member)
                    content = archive.read(image_member)
                    filename = PurePosixPath(image_member).name
                    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', filename) or '..' in filename:
                        raise ValueError('unsafe archive image basename: '+filename)
                    scratch_relative = f'downloads/mr-Deva-IN/source-image-qa/{unit}/{locale}-{filename}'
                    if scratch_relative in pending_images and pending_images[scratch_relative] != content:
                        raise ValueError('conflicting image basename: '+filename)
                    pending_images[scratch_relative] = content
                    images.append({'locator': locator, 'locale': locale, 'archive': pin['path'],
                                   'archive_sha256': pin['sha256'], 'member': image_member,
                                   'sha256': sha(content), 'bytes': len(content),
                                   'review_copy': scratch_relative,
                                   'visual_review': 'not asserted by acquisition script'})
            selections.append(record)
    assets = {}
    for name in sorted(requested_assets):
        matches = [item for item in images if item['locale'] == 'en'
                   and PurePosixPath(item['member']).name == name]
        identities = {(item['archive'], item['member'], item['sha256']) for item in matches}
        if len(identities) != 1:
            raise ValueError('asset must identify one selected canonical English image: '+name)
        item = matches[0]
        data = pending_images[item['review_copy']]
        mime = 'image/png' if name.endswith('.png') else 'image/jpeg'
        signature = b'\x89PNG\r\n\x1a\n' if mime == 'image/png' else b'\xff\xd8\xff'
        if not data.startswith(signature):
            raise ValueError('image extension/signature mismatch: '+name)
        relative = f'assets/{unit}/{name}'
        pending[relative] = data
        assets[name] = {'path': relative, 'sha256': item['sha256'], 'mime': mime}
        witnesses.append({'path': relative, 'sha256': item['sha256'], 'bytes': len(data),
                          'mime': mime, 'source': item['archive']+':'+item['member'],
                          'serialization': 'unchanged original canonical image bytes'})
        for match in matches:
            match['committed_asset'] = relative
    config_output = []
    config_path = BASE/'units'/f'{unit}.json'
    if assets or config_path.is_file():
        config = json.loads(config_path.read_bytes())
        if assets:
            config['assets'] = assets
        elif 'assets' in config:
            config.pop('assets')
        else:
            config = None  # Preserve byte-identical image-free configs.
        if config is not None:
            config_output.append((config_path, (json.dumps(config, ensure_ascii=False, indent=2)+'\n').encode('utf-8')))
    lock = {'schema': 1, 'unit': unit, 'locale': 'mr-Deva-IN',
            'purpose': 'translation provenance only, never training/fine-tuning data',
            'parent_lock': 'sources.lock.json', 'source_selections': selections,
            'witnesses': witnesses, 'source_images': images,
            'verification': 'pinned archive SHA-256 and selected-member CRC; no new full-corpus extraction'}
    destination = BASE/'provenance'/f'{unit}.lock.json'
    # No large corpus extraction. All validation precedes staging, and a staging
    # failure leaves existing files intact. Replacements are not a transaction;
    # lock/config/receipt hashes detect interruption between individual replaces.
    outputs = [(BASE/relative, data) for relative, data in pending.items()]
    outputs += [(BASE.parent/relative, data) for relative, data in pending_images.items()]
    outputs += config_output
    outputs.append((destination, (json.dumps(lock, ensure_ascii=False, indent=2)+'\n').encode('utf-8')))
    write_selected(outputs)
    print(json.dumps({'unit': unit, 'selections': len(selections), 'witnesses': len(witnesses),
                      'selected_fragment_bytes': sum(len(data) for name, data in pending.items()
                                                     if name.startswith('provenance/')),
                      'committed_assets': len(assets),
                      'committed_asset_bytes': sum(len(data) for name, data in pending.items()
                                                  if name.startswith('assets/')),
                      'review_image_bytes': sum(map(len, pending_images.values()))}, indent=2))


if __name__ == '__main__':
    if len(sys.argv) >= 5 and sys.argv[1] == '--review-images':
        review_images(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif len(sys.argv) == 2:
        freeze(sys.argv[1])
    else:
        raise SystemExit('Usage: python -B freeze_unit.py UNIT | --review-images UNIT COURSE IMAGE...')
