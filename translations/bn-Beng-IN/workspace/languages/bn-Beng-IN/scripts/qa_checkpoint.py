"""Replay explicitly named translated modules; unrelated drafts stay outside the gate."""
import json,sys
import build,build_sections,build_modules,build_companions

L=build.LANG

def run(modules):
    build_modules.catalog()
    receipts=[build_modules.build_one(m) for m in modules]
    build_companions.build_all()
    build_modules.catalog()
    paths=[]
    for r in receipts:
        m=r['module']
        paths += [L/r['reader'],L/'translations'/f'{m}.bn-Beng-IN.cnxml',L/'qa/modules'/f'{m}.json']
        for ident in r['blocks']:
            stem=f'{m}-{ident}'
            paths += [L/'reader/sections'/f'{stem}.html',L/'translations'/f'{stem}.bn-Beng-IN.cnxml',L/'qa/sections'/f'{stem}.json']
            canon=L/'canon/sections'/f'{stem}.json'
            if ident=='fs-id1726667':canon=L/'canon/consultations.json'
            data=json.loads(canon.read_text(encoding='utf-8'))
            entries=data if isinstance(data,list) else data.get('consultations',data.get('stages',[]))
            assert len(entries)>=3,(canon,'Required actual recurring reference consultation record missing')
    paths += [L/'reader/index.html']
    for unit in ['U02','U03','U04','U05','U06']:
        paths += [L/'reader'/f'{unit}-companion.html',L/'qa'/f'{unit}-companion.json']
    return receipts,{p.relative_to(L).as_posix():build.sha(p) for p in paths}

if __name__=='__main__':
    modules=sys.argv[1:]
    assert modules,'Name complete modules explicitly'
    first,hashes=run(modules)
    second,replayed=run(modules)
    assert hashes==replayed,'Non-deterministic checkpoint output'
    browser={}
    for module in modules:
        path=L/'qa/browser'/f'modules_{module}.json'
        r=next(r for r in second if r['module']==module)
        browser[module]='not current' if not path.is_file() else ('pass' if json.loads(path.read_text(encoding='utf-8'))['input_sha256']==r['reader_sha256'] else 'stale; rerender required')
    receipt={'result':'pass','module_translation_coverage':modules,'scope':'incremental checkpoint; entire assignment incomplete',
             'deterministic_replay':'all module/section CNXML, readers, structural receipts and U02/U03/U04/U05/U06 byte-identical across two builds',
             'verified_output_files':len(hashes),'outputs':hashes,'browser_at_time_of_check':browser,
             'module_mathml':{r['module']:r['mathml'] for r in second},'module_images':{r['module']:r['images'] for r in second},
             'independent_teacher_language_review':'pending','learner_validation':'pending','screen_reader_review':'pending'}
    (L/'qa/checkpoint.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['result','module_translation_coverage','verified_output_files','browser_at_time_of_check']}))
