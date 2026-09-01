"""Deterministic, hash-gated offline reading snapshot; no large corpora."""
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
import hashlib, io, json, posixpath, re, zipfile
import xml.etree.ElementTree as ET
from build import L, write

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    names=set(['README.md','STATUS.md','GOAL.md','DECISIONS.md','NEXT_UNIT.json','USER_UPDATES.md',
        'sources.lock.json','terminology.json','module-map.json','assignment-coverage.json',
        'canon/register.json','canon/download-receipt.json','canon/CONSULTATIONS.md',
        'provenance/AX-specifications.json','provenance/u01-source-extract.cnxml',
        'translations/u01-text.bn.json','translations/u01-companion.xhtml',
        'translations/modules/m81243/index.cnxml','translations/complete_modules/m81243/index.cnxml',
        'translations/m81243-extras.bn.json','translations/u02e-answers.json',
        'output/u01-number-sense.html','output/build-receipt.json','output/qa-receipt.json',
        'output/m81243/index.html','output/m81243/qa-receipt.json',
        'output/U02/index.html','output/U02/build-receipt.json','output/U02/reproducibility.json',
        'output/pdf/u01-print.pdf','output/pdf/u01-screen.pdf','output/pdf/visual-qa.json',
        'output/pdf/u02-complete-print.pdf','output/pdf/u02-complete-screen.pdf',
        'output/pdf/u02-build-receipt.json','output/pdf/u02-visual-qa.json',
        'output/pdf/u02-visual-v3-print.json','output/pdf/u02-visual-v3-screen.json'])
    for suffix in 'ABCDE':
        unit='U02'+suffix;stem=unit.lower()
        names.update([f'units/{unit}.json',f'translations/{stem}-text.bn.json',
            f'translations/{stem}-companion.xhtml',f'translations/modules/m81243/{stem}.cnxml',
            f'provenance/{stem}-source-extract.cnxml',f'output/{unit}/index.html',f'output/{unit}/qa-receipt.json'])
    for folder in ('assets','provenance/notices','translations/media'):
        names.update(p.relative_to(L).as_posix() for p in (L/folder).iterdir() if p.is_file())
    files={name:(L/name).read_bytes() for name in sorted(names)}
    def data(name):return json.loads(files[name])
    def check(name,value):assert sha(files[name])==value,'Stale receipt: '+name
    repro=data('output/U02/reproducibility.json');assert repro['status']=='pass'
    for name,value in repro['sha256'].items():check(name,value)
    for name,value in repro['tools_sha256'].items():
        assert sha((L/'tools'/name).read_bytes())==value,'Changed build/QA tool: '+name
    module=data('output/m81243/qa-receipt.json')
    assert module['status']=='complete_source_translation_structural_math_pass'
    check('translations/complete_modules/m81243/index.cnxml',module['translation_sha256'])
    check('output/m81243/index.html',module['html_sha256'])
    check('translations/m81243-extras.bn.json',module['extra_input_sha256'])
    for name,value in module['section_input_sha256'].items():check(name,value)
    edition=data('output/U02/build-receipt.json');check('output/U02/index.html',edition['html_sha256'])
    for name,value in edition['inputs'].items():check(name,value)
    for suffix in 'ABCDE':
        unit='U02'+suffix;spec=data(f'units/{unit}.json');qa=data(f'output/{unit}/qa-receipt.json')
        assert qa['status']=='structural_math_pass'
        check(f'units/{unit}.json',qa['unit_specification_sha256'])
        for field,value in qa['input_sha256'].items():check(spec[field],value)
        if 'practice_answer_input_sha256' in qa:
            check(qa['practice_answers']['answer_inputs'],qa['practice_answer_input_sha256'])
        check(spec['translation'],qa['translation_sha256']);check(spec['witness'],qa['witness_sha256'])
        check(f'output/{unit}/index.html',qa['html_sha256'])
        for image in qa['media']:check(image['path'],image['sha256'])
    for notice in data('sources.lock.json')['preserved_notices']:check(notice['copy'],notice['sha256'])
    for label in ('visual-qa.json','u02-visual-qa.json'):
        visual=data('output/pdf/'+label)
        for artifact in visual['artifacts']:
            assert artifact['all_pages_inspected']
            check(artifact['file'],artifact['sha256'])
            if 'page_record' in artifact:
                page_record=data(artifact['page_record'])
                assert page_record['pdf_sha256']==artifact['sha256'] and page_record['all_pages_inspected']
                assert len(page_record['inspected_png_sha256'])==artifact['pages']
                assert artifact['clipping_overlap_or_unreadable_glyph_defects']==0
    resources=[];external=[]
    for name,raw in sorted(files.items()):
        if not name.endswith('.html'):continue
        root=ET.fromstring(raw.decode('utf-8').split('\n',1)[1])
        references=[e.get(a) for e in root.iter() for a in ('src','href') if e.get(a)]
        references+=re.findall(r'url\(["\']?([^"\')]+)',raw.decode('utf-8'))
        for reference in references:
            parsed=urlsplit(reference)
            if parsed.scheme in ('http','https'):
                external.append(reference);continue
            assert not parsed.scheme and not parsed.netloc and not parsed.path.startswith('/')
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(parsed.path))) if parsed.path else name
            assert target in files,(name,reference,target)
            if parsed.fragment:
                target_root=ET.fromstring(files[target].decode('utf-8').split('\n',1)[1])
                assert unquote(parsed.fragment) in {e.get('id') for e in target_root.iter()},(name,reference)
            resources.append({'from':name,'reference':reference,'target':target})
    manifest={'schema':'bn-Beng-BD.offline.v2','unit':'U01-U02-m81243',
        'entrypoint':'output/U02/index.html','purpose':'Reading/translation review, never model training.',
        'files':[{'path':n,'bytes':len(b),'sha256':sha(b)} for n,b in sorted(files.items())]}
    files['MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
    def archive():
        memory=io.BytesIO()
        with zipfile.ZipFile(memory,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,raw in sorted(files.items()):
                assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
                info=zipfile.ZipInfo('bn-Beng-BD/'+name,date_time=(2026,8,31,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=0o100644<<16
                z.writestr(info,raw,compresslevel=9)
        return memory.getvalue()
    blob=archive();assert blob==archive()
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        assert z.testzip() is None
        for name,raw in files.items():assert z.read('bn-Beng-BD/'+name)==raw
    out=L/'output/bn-Beng-BD-U02-offline.zip';out.write_bytes(blob)
    receipt={'file':out.relative_to(L).as_posix(),'bytes':len(blob),'sha256':sha(blob),'files':len(files),
        'all_member_hashes_verified':True,'local_html_references_checked':len(resources),
        'external_optional_links':sorted(set(external)),'deterministic_zip':True,
        'reference_corpora_or_raw_canon_included':False,'entire_assignment_complete':False}
    write(L/'output/U02/package-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
