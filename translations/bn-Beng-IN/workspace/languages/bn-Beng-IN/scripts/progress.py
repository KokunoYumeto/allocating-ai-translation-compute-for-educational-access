"""Full-assignment coverage inventory; existing drafts never imply completed modules."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import build

L=build.LANG;ROOT=L.parents[1]
def required_blocks(root):
    blocks=[('__module_title__','title',root.find(f'{{{build.C}}}title'))]
    abstract=root.find(f'{{{build.C}}}metadata/{{{build.D}}}abstract')
    if abstract is not None and ''.join(abstract.itertext()).strip():blocks.append(('__abstract__','abstract',abstract))
    for e in root:
        kind=build.local(e)
        if kind in ('title','metadata'):continue
        items=list(e) if kind=='content' else [e]
        for i,block in enumerate(items):blocks.append((block.get('id') or f'__{kind}_{i}__',build.local(block),block))
    return blocks

def main():
    lock=json.loads((L/'sources.lock.json').read_text(encoding='utf-8'))
    passes={}
    for p in (L/'qa/sections').glob('*.json'):
        r=json.loads(p.read_text(encoding='utf-8'))
        overlay=L/'translations'/f'{r["module"]}-{r["section"]}.bn-Beng-IN.json'
        if r['result']=='pass' and overlay.is_file() and build.sha(overlay)==r['translation_sha256'] and build.sha(L/r['reader'])==r['reader_sha256'] and all(build.sha(L/n)==h for n,h in r.get('builders',{}).items()):
            passes[(r['module'],r['section'])]=r
    pilot=json.loads((L/'qa/status.json').read_text(encoding='utf-8'))
    pilot_path=L/'translations/m81285-fs-id1726667.bn-Beng-IN.json'
    if pilot['result']=='pass' and build.sha(pilot_path)==pilot['inputs']['translations\\m81285-fs-id1726667.bn-Beng-IN.json']:
        passes[('m81285','fs-id1726667')]={'reader':'reader/U01-source-faithful.html','visual_review':'pass','mathml':46}
    modules=[]
    for c in lock['collections']:
        for m in c['source_modules']:
            root=ET.parse(ROOT/m['path']).getroot()
            blocks=[]
            for ident,kind,block in required_blocks(root):
                passed=passes.get((m['module'],ident))
                blocks.append({'id':ident,'kind':kind,'source_title':block.text if kind=='title' else block.findtext(f'{{{build.C}}}title'),
                               'status':'translated_structure_checked' if passed else 'pending',
                               'reader':passed.get('reader') if passed else None,
                               'visual_review':passed.get('visual_review','pending') if passed else 'pending'})
            modules.append({'course':c['course'],'module':m['module'],'source_title':m['title'],'source_sha256':m['sha256'],
                            'complete':all(b['status']=='translated_structure_checked' for b in blocks),'blocks':blocks})
    result={'locale':'bn-Beng-IN','scope':'ENTIRE A00/A10/A20 collections, selected A30 m49301/m49324, and aligned AX-3 workflow',
            'assignment_complete':False,'required_collection_module_references':len(modules),
            'complete_modules':sum(m['complete'] for m in modules),'required_source_blocks':sum(len(m['blocks']) for m in modules),
            'translated_structure_checked_blocks':sum(b['status']=='translated_structure_checked' for m in modules for b in m['blocks']),
            'companion':{'verified_checkpoints':['U01']+[unit for unit in ['U02','U03','U04','U05'] if (L/'qa'/f'{unit}-companion.json').is_file() and json.loads((L/'qa'/f'{unit}-companion.json').read_text(encoding='utf-8'))['reader_sha256']==build.sha(L/'reader'/f'{unit}-companion.html')],'full_assignment_workflow_complete':False},
            'independent_language_teacher_review':'pending','learner_validation':'pending','assistive_technology_review':'pending',
            'rules':'No module is complete until its learner title and every required source block are translated and verified. Partial block/companion checkpoints are not assignment completion. Metadata/notices are retained as provenance, not silently relicensed.',
            'modules':modules}
    (L/'progress.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['required_collection_module_references','required_source_blocks','complete_modules','translated_structure_checked_blocks','assignment_complete']}))
if __name__=='__main__':main()
