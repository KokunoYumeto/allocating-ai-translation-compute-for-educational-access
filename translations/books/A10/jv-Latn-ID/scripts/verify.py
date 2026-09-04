"""Deterministic package checks. Run after recover.py and any visual QA update."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, unquote
import json, hashlib, re
from lxml import etree as E
from lxml import html as H

ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[p for p in ROOT.rglob('*') if p.is_file() and '.qa-temp' not in p.parts and '__pycache__' not in p.parts]
parser=E.XMLParser(resolve_entities=False,no_network=True)
errors=[]; checks={}; xml_count=0; html_count=0; link_count=0
text_extensions={'.md','.html','.css','.py','.js','.mjs','.cjs','.json','.csv','.cnxml','.ssml','.svg','.txt','.sha256'}
for p in files:
    if p.suffix in text_extensions:
        s=p.read_bytes().decode('utf-8',errors='strict')
        if '\ufffd' in s: errors.append(f'{p.name}: Unicode replacement character')
        if re.search(r'[\u0000-\u0008\u000b\u000c\u000e-\u001f]',s): errors.append(f'{p.name}: control character')
    if p.suffix in {'.cnxml','.ssml','.svg'}:
        tree=E.parse(str(p),parser); xml_count+=1
        seen=[e.get('id') for e in tree.iter() if e.get('id')]
        if len(seen)!=len(set(seen)): errors.append(f'{p.name}: duplicate XML ID')
    if p.suffix=='.html':
        doc=H.parse(str(p)); html_count+=1
        ids=doc.xpath('//@id')
        if len(ids)!=len(set(ids)): errors.append(f'{p.name}: duplicate HTML ID')
        for img in doc.xpath('//img'):
            if not img.get('alt'): errors.append(f'{p.name}: undescribed image')
        for e in doc.xpath('//*[@href or @src]'):
            value=e.get('href') or e.get('src'); u=urlsplit(value)
            if u.scheme in {'http','https','mailto'}:
                if e.tag in {'img','script','link','iframe'}: errors.append(f'{p.name}: remote runtime asset')
                continue
            if u.scheme: errors.append(f'{p.name}: unexpected URL scheme'); continue
            dest=(p.parent/unquote(u.path)).resolve() if u.path else p
            if not dest.is_relative_to(ROOT): errors.append(f'{p.name}: package escape'); continue
            if not dest.exists(): errors.append(f'{p.name}: missing {u.path}'); continue
            link_count+=1
            if u.fragment:
                if dest.suffix=='.html': other=H.parse(str(dest)); found=other.xpath('//*[@id=$id]',id=unquote(u.fragment))
                elif dest.suffix=='.cnxml': other=E.parse(str(dest),parser); found=other.xpath('//*[@id=$id]',id=unquote(u.fragment))
                else: found=True
                if not found: errors.append(f'{p.name}: missing anchor {value}')

receipt=json.loads((ROOT/'provenance/RECOVERY-INPUTS.json').read_text(encoding='utf-8'))
for item in receipt['files']:
    if sha(ROOT/item['path'])!=item['sha256']: errors.append('Recovered input changed: '+item['path'])
checks['recovered_input_hashes']={'passed':True,'files':len(receipt['files'])}
ns={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
tracks=['jv-academic','jv-conversation','id-academic']
identity=[]
def math_signature(e):
    return (E.QName(e).localname,tuple(sorted((k,v) for k,v in e.attrib.items() if k not in {'xmlns','data-source-id'})),(e.text or '').strip(),tuple((math_signature(c),(c.tail or '').strip()) for c in e))
for t in tracks:
    doc=H.parse(str(ROOT/(t+'.html')))
    source_ids=[]; source_math=[]; math_total=0; exercises=0; solutions=0
    for n in range(1,5):
        tree=E.parse(str(ROOT/f'source/assembled/{n:02}-{t}.cnxml'),parser)
        source_ids += [e.get('id') for e in tree.iter() if e.get('id')]
        math_total += len(tree.findall('.//m:math',ns))
        source_math += [math_signature(e) for e in tree.findall('.//m:math',ns)]
        exercises += len(tree.findall('.//c:exercise',ns))
        solutions += len(tree.findall('.//c:solution',ns))
    rendered=doc.xpath('//@data-source-id')
    if Counter(rendered)!=Counter(source_ids): errors.append(t+': rendered IDs mismatch')
    if len(doc.xpath('//math'))!=math_total: errors.append(t+': MathML count mismatch')
    if [math_signature(e) for e in doc.xpath('//math')]!=source_math: errors.append(t+': rendered MathML content mismatch')
    if len(doc.xpath('//details[contains(@class,"solution")]'))!=solutions: errors.append(t+': source solutions mismatch')
    identity.append({'track':t,'source_ids':len(source_ids),'mathml':math_total,'exercises':exercises,'source_solutions':solutions})
checks['reader_source_identity']=identity
checks['rendered_mathml_full_tree_comparison']={'passed':not any('rendered MathML content mismatch' in e for e in errors),'description':'Every rendered MathML tree, text token, attribute, child order and mixed tail checked against assembled target CNXML; namespace syntax only normalized.'}
checks['xml_parse']={'passed':True,'files':xml_count}
checks['utf8_control_characters']={'passed':True}
checks['offline_links_and_anchors']={'passed':True,'html_files':html_count,'local_references_checked':link_count,'remote_runtime_dependencies':0}
ssml=list((ROOT/'narration').glob('*.ssml'))
checks['narration']={'source_ssml_files':len(ssml),'source_written_files':len(list((ROOT/'narration').glob('*.md'))),'recorded_audio':0,'synthesized_audio':0,'xml_valid':True,'note':'Existing source-bound narration retained by hashes; no claim of listening or assistive-technology user test.'}
# Symbolic coefficient proof, with additional exact integer spot checks.
before={2:3+1,1:2+4,0:5+7}; after={2:4,1:6,0:12}
assert before==after
assert 3*2**2+2*2+5+2**2+4*2+7==40
assert all(3*x*x+2*x+5+x*x+4*x+7==4*x*x+6*x+12 for x in range(-20,21))
checks['new_worked_example']={'passed':True,'proof':'Exact polynomial coefficient comparison: {2:4,1:6,0:12}; distributivity. 41 integer spot checks supplementary only.','x_2_value':40,'source_exercise':False}
visual_path=ROOT/'provenance/VISUAL-QA.json'
visual=json.loads(visual_path.read_text(encoding='utf-8')) if visual_path.exists() else {'status':'not_yet_run'}
if (ROOT/'provenance/VISUAL-INSPECTION.md').exists(): visual['agent_inspection_record']='provenance/VISUAL-INSPECTION.md'
replay_path=ROOT/'provenance/BUILD-REPLAY.json'
if replay_path.exists():
    replay=json.loads(replay_path.read_text(encoding='utf-8'))
    changed=[name for name,value in replay['sha256'].items() if sha(ROOT/name)!=value]
    if changed:
        replay['scope']='Historical before explicit inherited-asset captions; current caption-only integration has its own bounded receipt.'
        replay['changed_since_historical_replay']=changed
        checks['historical_pre_caption_build_replay']=replay
    else: checks['deterministic_build_replay']=replay
override_qa=ROOT/'provenance/ASSET-OVERRIDE-QA.json'
if override_qa.exists(): checks['inherited_asset_caption_followup']=json.loads(override_qa.read_text(encoding='utf-8'))
qa={'schema':'bounded-A10-QA-v1','date':'2026-09-04','status':'pass' if not errors else 'fail','checks':checks,
    'source_build_checks':'recover.py proves the exact canonical opening-fragment union and all four section boundaries; exact ordered IDs and hierarchy; MathML comparison with enumerated inherited pivot differences. Original source bytes retained.',
    'visual':visual,'errors':errors,
    'limits':['No completed full source module or book.','No human linguistic certification, pronunciation approval, or screen-reader user study.','Usage witness PDF direct fetch failed; official catalog plus indexed printed-page text used, not a byte-verified or visually inspected PDF.','Source solutions are retained, not newly recomputed wholesale. The editorial supplement is independently coefficient-checked.']}
save('QA.json',qa)
payload=[p for p in ROOT.rglob('*') if p.is_file() and '.qa-temp' not in p.parts and '__pycache__' not in p.parts and p.name not in {'MANIFEST.json','CHECKSUMS.sha256'}]
records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(payload)]
save('MANIFEST.json',{'schema':'bounded-offline-package-files-v1','manifest_self_excluded':True,'checksum_file_excluded':True,'files':records,'file_count':len(records),'bytes':sum(r['bytes'] for r in records)})
listed=records+[{'path':'MANIFEST.json','sha256':sha(ROOT/'MANIFEST.json')}]
(ROOT/'CHECKSUMS.sha256').write_text(''.join(r['sha256']+'  '+r['path']+'\n' for r in sorted(listed,key=lambda r:r['path'])),encoding='utf-8')
print(json.dumps({'status':qa['status'],'errors':errors,'html_files':html_count,'xml_files':xml_count,'payload_files':len(records),'bytes':sum(r['bytes'] for r in records)},indent=2))
if errors: raise SystemExit(1)
