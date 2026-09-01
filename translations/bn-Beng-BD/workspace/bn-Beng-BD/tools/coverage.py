"""Inventory the entire assigned A00 collection; partial lessons are not full modules."""
from pathlib import Path
import hashlib, json, xml.etree.ElementTree as ET
L=Path(__file__).resolve().parents[1]
R=L.parent
C='http://cnx.rice.edu/cnxml'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    collection=R/'downloads/bn-Beng-BD/a00-id/collections/prealgebra-2e.collection.xml'
    refs=[e.get('document') for e in ET.parse(collection).iter() if e.get('document')]
    assert len(refs)==len(set(refs))
    partial={'m81243':[{'unit':'U01','sections':['fs-id1830385','fs-id2340048'],'receipt':'output/qa-receipt.json'}]}
    for path in sorted((L/'units').glob('*.json')):
        unit=json.loads(path.read_text(encoding='utf-8'))
        receipt=L/'output'/unit['id']/'qa-receipt.json'
        if receipt.exists():
            result=json.loads(receipt.read_text(encoding='utf-8'))
            assert result['status']=='structural_math_pass'
            assert sha(L/unit['translation'])==result['translation_sha256']
            partial.setdefault(unit['module'],[]).append({'unit':unit['id'],'sections':unit['sections'],'receipt':receipt.relative_to(L).as_posix()})
    modules=[]
    for specpath in sorted((L/'modules').glob('m[0-9][0-9][0-9][0-9][0-9].json')):
        spec=json.loads(specpath.read_text(encoding='utf-8'))
        receipt_path=L/'output'/spec['module']/'qa-receipt.json'
        if 'content_prefix_count' not in spec or not receipt_path.exists():continue
        result=json.loads(receipt_path.read_text(encoding='utf-8'))
        assert result['spec_sha256']==sha(specpath)
        assert result['strings_sha256']==sha(L/spec['strings'])
        assert result['translation_sha256']==sha(L/result['translation_path'])
        assert result['html_sha256']==sha(receipt_path.parent/'index.html')
        if spec.get('image_tables_path'):
            assert result['image_tables_sha256']==sha(L/spec['image_tables_path'])
        if result['status']!='partial_source_translation_structural_math_pass':continue
        partial.setdefault(spec['module'],[]).append({'source_draft':spec['module']+'-prefix',
            'content_nodes':result['selected_content_ids'],'includes_all_metadata':True,
            'receipt':receipt_path.relative_to(L).as_posix()})
    for module in refs:
        canonical=R/'downloads/bn-Beng-BD/openstax-canonical/modules'/module/'index.cnxml'
        indonesian=R/'downloads/bn-Beng-BD/a00-id/modules'/module/'index.cnxml'
        root=ET.parse(canonical).getroot()
        source_ids={e.get('id') for e in root.iter() if e.get('id')}
        coverage=partial.get(module,[])
        anchors=[a for item in coverage for a in item.get('sections',item.get('content_nodes',[]))]
        assert set(anchors)<=source_ids
        complete=L/'translations/complete_modules'/module/'index.cnxml'
        # Completion requires the whole original document, not a subset wrapper.
        done=False
        if complete.exists():
            receipt_path=L/'output'/module/'qa-receipt.json'
            receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
            assert receipt['status']=='complete_source_translation_structural_math_pass'
            assert receipt['translation_sha256']==sha(complete) and receipt['source_sha256']==sha(canonical)
            translated=ET.parse(complete).getroot()
            assert len(list(root.iter()))==len(list(translated.iter()))
            assert source_ids=={e.get('id') for e in translated.iter() if e.get('id')}
            for a,b in zip(root.iter(),translated.iter()):
                assert a.tag==b.tag
                if a.tag.rsplit('}',1)[-1] in ('mn','mo','mspace'):assert a.text==b.text
            done=True
        modules.append({'module':module,'title':root.findtext('{'+C+'}title'),
                        'canonical_sha256':sha(canonical),'indonesian_sha256':sha(indonesian),
                        'whole_document_elements':len(list(root.iter())),
                        'partial_units':coverage,'whole_module_complete':done})
    companions=['U01']+[p.stem for p in sorted((L/'units').glob('*.json')) if (L/'output'/p.stem/'qa-receipt.json').exists()]
    for path in sorted((L/'companions').glob('*.json')):
        spec=json.loads(path.read_text(encoding='utf-8'))
        receipt_path=L/'output'/spec['id']/'qa-receipt.json'
        if not receipt_path.exists():continue
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        assert receipt['status']=='companion_structural_math_pass'
        assert receipt['companion_spec_sha256']==sha(path)
        assert receipt['lesson_sha256']==sha(L/spec['lesson'])
        source_receipt=json.loads((L/'output'/spec['module']/'qa-receipt.json').read_text(encoding='utf-8'))
        assert receipt['source_translation_sha256']==source_receipt['translation_sha256']
        assert receipt['source_spec_sha256']==source_receipt['spec_sha256']
        for name,digest in receipt['html_sha256'].items():assert sha(receipt_path.parent/name)==digest
        stem=spec['id'].lower()
        assert sha(L/'translations'/(stem+'-answers.json'))==receipt['answer_records_sha256']
        assert sha(L/'translations'/(stem+'-worked-answers.xhtml'))==receipt['answer_xhtml_sha256']
        companions.append(spec['id'])
    result={'schema':'bn-Beng-BD.entire-assignment-coverage.v1',
            'scope':'Complete A00 collection plus selected foundational A10 and the AX-1/AX-3 workflow. The child-facing map does not truncate source coverage.',
            'collection_path':collection.relative_to(R).as_posix(),'collection_sha256':sha(collection),
            'A00':{'assigned_modules':len(modules),'fully_translated_modules':sum(x['whole_module_complete'] for x in modules),'modules':modules},
            'A10':{'scope':'Selected foundational content in module-map.json; full source release acquired. Precise selection anchors not yet assigned for every planned subset.','translation_complete':False},
            'AX-1':{'U01':'HTML, print/screen PDF and offline package verified; accessibility review limits recorded','remaining_units_complete':False},
            'AX-3':{'completed_companion_drafts':companions,'entire_assignment_complete':False},
            'backfill_before_A00_completion':[x['module']+' '+x['title'] for x in modules if x['module'] in ('m81241','m81242') and not x['whole_module_complete']],
            'completion_semantics':'fully_translated_modules counts complete source-translation drafts with structural/math QA; it does not certify teacher/visual/PDF QA or whole-workflow completion.',
            'entire_assignment_complete':False}
    (L/'assignment-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'A00_modules':len(modules),'fully_translated_modules':result['A00']['fully_translated_modules'],'partial_units':partial,'entire_assignment_complete':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
