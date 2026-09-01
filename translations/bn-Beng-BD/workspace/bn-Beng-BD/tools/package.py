"""Build a small deterministic offline pilot package, never the reference corpora."""
from pathlib import Path, PurePosixPath
import hashlib, io, json, posixpath, re, zipfile

L = Path(__file__).resolve().parents[1]

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    required = [
        'README.md', 'STATUS.md', 'GOAL.md', 'DECISIONS.md', 'NEXT_UNIT.json', 'USER_UPDATES.md',
        'sources.lock.json', 'terminology.json', 'module-map.json',
        'canon/register.json', 'canon/CONSULTATIONS.md', 'canon/download-receipt.json',
        'translations/u01-text.bn.json', 'translations/u01-companion.xhtml',
        'translations/modules/m81243/index.cnxml', 'provenance/u01-source-extract.cnxml',
        'provenance/AX-specifications.json', 'output/u01-number-sense.html',
        'output/build-receipt.json', 'output/qa-receipt.json',
        'output/pdf/u01-print.pdf', 'output/pdf/u01-screen.pdf',
        'output/pdf/build-receipt.json', 'output/pdf/qa-receipt.json',
        'output/pdf/visual-qa.json', 'output/reproducibility.json',
    ]
    files = {name: (L/name).read_bytes() for name in required}
    for folder in ('assets', 'provenance/notices', 'translations/media'):
        for path in sorted((L/folder).iterdir()):
            if path.is_file(): files[path.relative_to(L).as_posix()] = path.read_bytes()
    visual = json.loads(files['output/pdf/visual-qa.json'])
    reproducibility = json.loads(files['output/reproducibility.json'])
    qa = json.loads(files['output/qa-receipt.json'])
    assert qa['status'] == reproducibility['status'] == 'pass'
    for name, expected in reproducibility['sha256'].items():
        assert digest(files[name]) == expected, 'Reproducibility receipt is stale: '+name
    for name, expected in qa['translation_inputs_sha256'].items():
        assert digest(files[name]) == expected, 'Translation QA is stale: '+name
    assert digest(files['output/u01-number-sense.html']) == qa['html_sha256']
    for item in visual['artifacts']:
        assert item['all_pages_inspected'] and item['visual_defects_found'] == 0
        assert digest(files[item['file']]) == item['sha256'], 'Visual QA is stale'
    html = files['output/u01-number-sense.html'].decode('utf-8')
    resources = re.findall(r'url\(["\']?([^"\')]+)', html)
    resources += re.findall(r'\bsrc=["\']([^"\']+)', html)
    for resource in resources:
        assert '://' not in resource and not resource.startswith(('data:', '/'))
        target = posixpath.normpath(posixpath.join('output', resource))
        assert target in files, (resource, target)
    manifest = {'schema': 'bn-Beng-BD.offline.v1', 'unit': 'U01',
                'entrypoint': 'output/u01-number-sense.html',
                'purpose': 'Reading and translation review, not model training.',
                'files': [{'path': name, 'bytes': len(data), 'sha256': digest(data)}
                          for name, data in sorted(files.items())]}
    files['MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    def archive():
        memory = io.BytesIO()
        with zipfile.ZipFile(memory, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in sorted(files.items()):
                assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
                info = zipfile.ZipInfo('bn-Beng-BD/'+name, date_time=(2026,8,30,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                z.writestr(info, data, compresslevel=9)
        return memory.getvalue()
    data = archive()
    assert data == archive(), 'Nondeterministic ZIP'
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None
        for name, content in files.items(): assert z.read('bn-Beng-BD/'+name) == content
    out = L/'output/bn-Beng-BD-U01-offline.zip'
    out.write_bytes(data)
    receipt = {'file': out.relative_to(L).as_posix(), 'bytes': len(data), 'sha256': digest(data),
               'files': len(files), 'all_member_hashes_verified': True,
               'local_runtime_resources_verified': resources, 'deterministic_zip': True,
               'reference_corpora_included': False}
    (L/'output/package-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__': main()
