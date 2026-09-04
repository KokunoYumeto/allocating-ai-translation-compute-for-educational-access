"""Replay the authorized seven small component witnesses; never execute PG.

Only --retrieve permits five exact-commit GitHub file requests. Existing files
are compared, never overwritten. The two DMOI files come from pinned local Git.
This is dependency retention under existing notices, not a new rights audit.
"""
import argparse
import base64
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
DEST = BASE / 'provenance/b10-unit-002-components'
OPL_COMMIT = '521448225da9a2dc4ebf1ed6258f7afe2f1b5eac'
DMOI_COMMIT = '82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799'
ID_COMMIT = 'e94905932301e699b7c4d44e88ec54e972b886b6'
OPL_DIR = 'Contrib/DMOI/0-Introduction_and_Preliminaries/0_2-Mathematical_Statements/'
PAIRS = 'backend/manifests/authority_target_pairs.tsv'
EXPECTED = {
    '0_2_1.pg': (3580, 'd9ed29e0541b3adadf21765c7d655cb9946d9a8be079cd9c5c96e0dc314db9a0'),
    '0_2_2.pg': (3348, '1e85f23b0493ed3e766f80ecc1e7cdb4008fbec5ca5e56a3f11d4a4bc924b5bf'),
    '0_2_4.pg': (3011, '9490f3eda74dd81c53484a7bc927bd63c952ba975faa63c39ec88945a1139da7'),
    '0_2_15.pg': (2067, 'b8e71d208a7f2f7a9da673da96cb140f83659c6aaeb7fc3ca6ac26d9773688ba'),
}

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def admit(path, raw):
    assert path.resolve().is_relative_to(DEST.resolve()), 'Out-of-scope output'
    if path.exists():
        assert path.read_bytes() == raw, 'Refusing to overwrite changed witness ' + str(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

def main(retrieve=False):
    idrepo = ROOT / 'downloads/discrete-mathematics-open-introduction-id'
    authority = git(idrepo, 'show', ID_COMMIT + ':' + PAIRS)
    pairs = [line.split('\t') for line in authority.decode().splitlines()]
    priorpath = DEST / 'acquisition.json'
    prior = json.loads(priorpath.read_text('utf-8')) if priorpath.exists() else None
    records = []
    for path in ['OPL_LICENSE'] + [OPL_DIR + name for name in EXPECTED]:
        local = DEST / 'OPL' / path
        endpoint = 'https://api.github.com/repos/openwebwork/webwork-open-problem-library/contents/' + path + '?ref=' + OPL_COMMIT
        if retrieve:
            request = urllib.request.Request(endpoint, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'pnb-B10-002-pinned-component-retention'})
            with urllib.request.urlopen(request, timeout=30) as response:
                assert response.url == endpoint, 'Unexpected retrieval redirect'
                body = response.read(150001)
                assert len(body) <= 150000, 'Bounded witness response exceeded limit'
                remote = json.loads(body)
            assert remote['type'] == 'file' and remote['path'] == path and remote['encoding'] == 'base64'
            raw = base64.b64decode(remote['content'], validate=False)
            assert len(raw) == remote['size'] and blob(raw) == remote['sha'], 'Pinned API blob mismatch'
        else:
            assert prior is not None, 'Use --retrieve for the authorized first acquisition'
            raw = local.read_bytes()
            old = next(row for row in prior['files'] if row['kind'] == 'opl' and row['repository_path'] == path)
            assert (len(raw), sha(raw), blob(raw)) == (old['bytes'], old['sha256'], old['git_blob_sha1']), 'Retained OPL witness differs'
        row = {'kind': 'opl', 'repository': 'https://github.com/openwebwork/webwork-open-problem-library', 'commit': OPL_COMMIT, 'repository_path': path, 'local_path': local.relative_to(BASE).as_posix(), 'bytes': len(raw), 'sha256': sha(raw), 'git_blob_sha1': blob(raw), 'pinned_contents_api': endpoint, 'pinned_raw_url': 'https://raw.githubusercontent.com/openwebwork/webwork-open-problem-library/' + OPL_COMMIT + '/' + path}
        if path != 'OPL_LICENSE':
            expected = EXPECTED[Path(path).name]
            match = next(values for values in pairs if values[7:] == ['opl', path])
            assert (int(match[5]), match[6]) == expected, 'Existing authority record differs'
            assert (len(raw), sha(raw)) == expected, 'Canonical OPL file does not match existing manifest'
            row['existing_comparison_authority_row'] = {'columns_verbatim': match, 'meaning': 'Indonesian target columns are comparison only; canonical bytes are columns 6 and 7.'}
        else:
            row['hash_origin'] = 'First observed at this exact pinned retrieval; not an expectation from the earlier lookup.'
        admit(local, raw)
        records.append(row)
    manifest = json.loads((BASE / 'source-excerpts/manifest-b10-unit-002.json').read_text('utf-8'))
    repo = ROOT / 'downloads/upstream/discrete-book'
    for name in ['statements-quant1.pg', 'statements-quant2.pg']:
        path = 'source/practice/wwpg/' + name
        expected = next(row for row in manifest['source_files'] if row['role'] == 'canonical' and row['repository_path'] == path)
        raw = git(repo, 'show', DMOI_COMMIT + ':' + path)
        assert (len(raw), sha(raw), blob(raw)) == (expected['bytes'], expected['sha256'], expected['git_blob_sha1'])
        local = DEST / 'dmoi4' / path
        admit(local, raw)
        records.append({'kind': 'dmoi-local-pg', 'repository': 'https://github.com/oscarlevin/discrete-book', 'commit': DMOI_COMMIT, 'repository_path': path, 'local_path': local.relative_to(BASE).as_posix(), 'bytes': len(raw), 'sha256': sha(raw), 'git_blob_sha1': blob(raw), 'acquisition': 'Copied exact Git blob from already acquired pinned local checkout; not executed.'})
    receipt = {'schema': 'b10-002-scoped-component-acquisition-v1', 'observed_date': '2026-08-31', 'unit': 'B10-002', 'authorization': 'Coordinator/parent authorized five exact-commit small OPL witness retrievals after bounded existing-cache lookup; two existing local PG blobs retained. No new rights assessment.', 'byte_policy': 'Verbatim binary writes; no line-ending normalization or PG execution.', 'existing_authority': {'repository': 'https://github.com/KokunoYumeto/discrete-mathematics-open-introduction-id', 'commit': ID_COMMIT, 'repository_path': PAIRS, 'git_blob_sha1': blob(authority), 'git_logical_lf_sha256': sha(authority)}, 'files': records, 'scope_limit': 'Four selected remote OPL source files, root OPL notice and two selected local PG source files only. Not the complete OPL library or release provenance package.'}
    admit(priorpath, (json.dumps(receipt, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'files': len(records), 'bytes': sum(row['bytes'] for row in records), 'receipt_sha256': sha(priorpath.read_bytes()), 'license': records[0]}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retrieve', action='store_true', help='Permit only the five authorized exact-commit GitHub file requests.')
    main(parser.parse_args().retrieve)
