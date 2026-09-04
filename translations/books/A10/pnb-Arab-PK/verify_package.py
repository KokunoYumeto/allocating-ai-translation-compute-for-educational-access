"""Independent bounded source, math, HTML, asset and coverage checks.
No renderer imported. Run after build and visual_qa.cjs. No network is used.
"""
import collections, copy, hashlib, json, re
from pathlib import Path
from urllib.parse import urlsplit,unquote
from lxml import etree as E, html as H

B=Path(__file__).resolve().parent
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tag(n): return E.QName(n).localname
def xml(p): return E.fromstring(p.read_bytes(),E.XMLParser(resolve_entities=False,no_network=True))
def desc(n,math=False):
    attrs=dict(n.attrib)
    if math and tag(n)=='math': attrs.pop('dir',None)
    return (n.tag,sorted(attrs.items()),n.text,[(desc(c,math),c.tail) for c in n])
def normalized(n,math=False):
    attrs=dict(n.attrib)
    if math and tag(n)=='math':attrs.pop('dir',None)
    return (n.tag,sorted(attrs.items()),(n.text or '').strip(),[(normalized(c,math),(c.tail or '').strip()) for c in n])
def dump(p,v): (B/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def check(v,label):
    checks.append({'check':label,'pass':bool(v)})
    return bool(v)
units=['a10-preface','a10-introduction']+['a10-unit-%03d'%i for i in range(1,9)]
sources={u:xml(B/'source-excerpts'/f'{u}.cnxml') for u in units}
canonical={m:xml(B/'source'/f'{m}.en.cnxml') for m in ['m82630','m82451','m82452','m82453']}
check(desc(sources['a10-preface'])==desc(canonical['m82630']),'complete preface expanded tree exact')
check(desc(sources['a10-introduction'])==desc(canonical['m82451']),'complete introduction tree exact; final file newline differs only')
# Reassemble exact Whole Numbers from fixed disjoint partitions. Preserve text,
# tails, namespace, all attributes and anonymous source nodes (not just IDs).
parts=[sources['a10-unit-%03d'%i] for i in range(1,6)]
rebuilt=copy.deepcopy(parts[4]); del rebuilt.attrib['id']
content=rebuilt.find('c:content',NS)
final=list(content)
for n in list(content):content.remove(n)
for n in parts[0]: content.append(copy.deepcopy(n))
split=content[-1]
for n in parts[1][0]: split.append(copy.deepcopy(n))
for p in parts[2:4]:
    for n in p:content.append(copy.deepcopy(n))
for n in final:content.append(copy.deepcopy(n))
check(desc(rebuilt)==desc(canonical['m82452']),'complete Whole Numbers exact source reassembly including anonymous nodes')
# Partial m82453 must match its opening and the first three complete sections.
covered=set()
for u in ['a10-unit-006','a10-unit-007','a10-unit-008']:
    for n in sources[u].iter():
        if n is sources[u]:continue
        if n.get('id'):covered.add(n.get('id'))
cn_content=canonical['m82453'].find('c:content',NS)
for i,u in [(2,'a10-unit-007'),(3,'a10-unit-008')]:
    check(desc(sources[u][0])==desc(cn_content[i]),u+' complete canonical section exact')
next_anchor=cn_content[4].get('id')
check(next_anchor=='fs-id1170655163482' and next_anchor not in covered,'contiguous next section excluded')
# m82453 opening excerpt includes title/metadata + first two content children.
p6=sources['a10-unit-006']
for child in p6:
    if tag(child)=='content':
        check(len(child)==2 and all(desc(x)==desc(y) for x,y in zip(child,cn_content[:2])),'006 exact module opening and first instructional section')
    else:
        matches=[n for n in canonical['m82453'] if n.tag==child.tag]
        check(len(matches)==1 and desc(child)==desc(matches[0]),'006 module '+tag(child)+' exact')
rows=[]
for u in units:
    source=sources[u]; p=B/'reader'/f'{u}.html'; text=p.read_text(encoding='utf-8'); html=H.fromstring(text)
    ids=html.xpath('//@id'); expected=[n.get('id') for n in source.iter() if n is not source and n.get('id')]
    check(len(ids)==len(set(ids)),u+' unique HTML IDs')
    check([v for v in ids if v in set(expected)]==expected,u+' all source IDs in order')
    raw_maths=re.findall(r'<math\b[^>]*>[\s\S]*?</math>',text)
    actual_math=[E.fromstring(x.encode()) for x in raw_maths]
    expected_math=source.xpath('.//m:math',namespaces=NS)
    check([desc(n,True) for n in actual_math]==[desc(n,True) for n in expected_math],u+' exact MathML trees and order (dir=ltr wrapper only)')
    check(not re.search(r'\{\{(?:math|child|link):\d+\}\}|\\n',text),u+' no unresolved draft placeholders')
    check(not re.search('[\ufffd\u0a00-\u0a7f\u061c\u200b-\u200f\u202a-\u202e\u2060-\u206f]',text),u+' UTF-8 Shahmukhi without replacement/Gurmukhi/hidden bidi controls')
    check(html.get('lang')=='pnb-Arab-PK' and html.get('dir')=='rtl',u+' declared language and RTL')
    check(not html.xpath('//script|//iframe'),u+' no executable runtime or remote frame')
    # In renderer-bound pages, exercises/solutions must remain exact associations.
    exercises=source.xpath('.//c:exercise',namespaces=NS); solutions=source.xpath('.//c:solution',namespaces=NS)
    for ex in exercises:
        sid=ex.get('id'); output=html.xpath('//*[@id=$v]',v=sid)
        if output:
            for sol in ex.xpath('./c:solution',namespaces=NS):
                check(bool(output[0].xpath('.//*[@id=$v]',v=sol.get('id'))),u+' supplied solution association '+sol.get('id'))
    tr=json.loads((B/'translations'/f'{u}.json').read_bytes())
    rows.append({'unit':u,'reader':f'reader/{u}.html','title':tr.get('title'), 'source_ids':len(expected),'mathml_trees':len(expected_math),'exercises':len(exercises),'source_supplied_solutions':len(solutions),'tables':len(source.xpath('.//c:table',namespaces=NS)),'images':len(source.xpath('.//c:image',namespaces=NS)),'translated_blocks':len(tr.get('source_blocks',{})),'reader_sha256':sha(p),'source_excerpt_sha256':sha(B/'source-excerpts'/f'{u}.cnxml')})
# Every image matches its source-selection pin (old or new) and real dimensions.
from PIL import Image
asset_checks=[]
for p in (B/'source-excerpts').glob('manifest-a10*.json'):
    man=json.loads(p.read_bytes())
    for row in man.get('images',[]):
        rel=row.get('path') or row.get('reader_path') or row.get('local_path')
        if not rel:
            rel='assets/a10/'+Path(row.get('source_path',row.get('src',''))).name
        if rel.startswith('../'):rel=rel[3:]
        q=B/rel
        if not q.exists():
            matches=[x for x in (B/'assets/a10').iterdir() if x.name==Path(rel).name]; q=matches[0] if matches else q
        good=q.is_file() and (not row.get('sha256') or sha(q)==row['sha256'])
        check(good,'pinned image '+str(rel)); asset_checks.append({'path':q.relative_to(B).as_posix(),'pass':good})
plan=json.loads((B/'source-excerpts/selection-a10-008.json').read_bytes())
for row in plan['images']:
    q=B/row['future_reader_path']; check(sha(q)==row['sha256'],'008 canonical JPEG '+q.name)
    with Image.open(q) as im:check(im.size==(row['width'],row['height']) and im.format=='JPEG','008 actual JPEG dimensions '+q.name)
# Links are allowed to external citation targets, but no network-dependent assets.
for p in [B/'index.html']+list((B/'reader').glob('*.html')):
    d=H.fromstring(p.read_bytes()); page_ids=set(d.xpath('//@id'))
    for e in d.xpath('//*[@href or @src]'):
        for a in ['href','src']:
            target=e.get(a)
            if not target:continue
            url=urlsplit(target)
            if url.scheme or url.netloc:
                check(a=='href' and url.scheme in {'http','https'},p.name+' citation-only remote '+target);continue
            q=(p.parent/unquote(url.path)).resolve() if url.path else p
            check(q.is_relative_to(B) and q.is_file(),p.name+' offline link '+target)
            if url.fragment:
                ids=page_ids if q==p else set(H.fromstring(q.read_bytes()).xpath('//@id')) if q.suffix=='.html' else set()
                check(unquote(url.fragment) in ids,p.name+' fragment '+target)
# Source-correlated arithmetic: manually encoded source problems, not invented exercises.
arithmetic=[('fs-id1170654889274',[7*5-4,7*1-4],[31,3]),('fs-id1170654920156',[8*2-3,8*1-3],[13,5]),('fs-id1170654928390',[4*3-4,4*5-4],[8,16]),('fs-id1170655213476',[4**2,3**4],[16,81]),('fs-id1170655120539',[3**2,4**3],[9,64]),('fs-id1170655353751',[6**3,2**6],[216,64]),('fs-id1170655171252',[2*4**2+3*4+8],[52]),('fs-id1170655160609',[3*3**2+4*3+1],[40]),('fs-id1170655197217',[6*2**2-4*2-7],[9])]
for ex,result,expected in arithmetic:check(result==expected,'008 arithmetic '+ex)
# Detached adversaries prove that critical validators notice representative damage.
mutations=[]
bad=copy.deepcopy(rebuilt); bad.xpath('.//m:mn',namespaces=NS)[0].text='999'
mutations.append({'mutation':'whole-number formula numeral changed','rejected':desc(bad)!=desc(canonical['m82452'])})
bad=copy.deepcopy(rebuilt); node=bad.xpath('.//c:entry',namespaces=NS)[0]; node.getparent().remove(node)
mutations.append({'mutation':'anonymous source table cell omitted','rejected':desc(bad)!=desc(canonical['m82452'])})
bad=copy.deepcopy(sources['a10-unit-008'][0]); bad[1].set('id','wrong')
mutations.append({'mutation':'evaluation source ID changed','rejected':desc(bad)!=desc(cn_content[3])})
bad=copy.deepcopy(sources['a10-unit-008'][0]); sol=bad.xpath('.//c:solution',namespaces=NS)[0]; sol.getparent().remove(sol)
mutations.append({'mutation':'source supplied solution removed','rejected':desc(bad)!=desc(cn_content[3])})
for row in mutations:check(row['rejected'],'detached adversary: '+row['mutation'])
visual=json.loads((B/'visual/browser-results.json').read_bytes())
inspection=json.loads((B/'visual/INSPECTION.json').read_bytes())
check(inspection['status']=='pass' and len(inspection['inspected'])==10 and all((B/'visual'/p).is_file() for p in inspection['inspected']),'actual visual inspection and ten screenshot artifacts present')
for row in visual['results']:
    check(row['documentWidth']<=row['width']+1 and not row['brokenImages'] and not row['nonLtrMath'] and not row['clippedSourceBoxes'],'offline browser '+row['file']+' '+str(row['width']))
fail=[c for c in checks if not c['pass']]
package={'schema':'recovered-elementary-algebra-reader-v1','locale':'pnb-Arab-PK','book':'OpenStax Elementary Algebra 2e','entrypoint':'index.html','date':'2026-09-04','source_commit':plan['canonical_commit'],'collection':{'id':'col31130','modules':82,'file':'source/collection.xml','sha256':sha(B/'source/collection.xml')},'full_book_complete':False,'complete_modules':[{'id':m,'source':'source/'+m+'.en.cnxml','sha256':sha(B/'source'/f'{m}.en.cnxml')} for m in ['m82630','m82451','m82452']],'partial_modules':[{'id':'m82453','opening_metadata_and_objectives':True,'complete_instructional_sections':['fs-id1170655160858','fs-id1170654953465','fs-id1170654889475'],'section_id_note':'First instructional section ID is recomputed below from canonical source.','through':'fs-id1170655106384','next_anchor':next_anchor,'next_title':'Identify and Combine Like Terms','source':'source/m82453.en.cnxml','sha256':sha(B/'source/m82453.en.cnxml')}],'reading_pages':rows,'new_completion':{'unit':'A10-008','status':'recovered complete draft revised, source-bound built, verified','source_blocks':91,'source_ids':83,'mathml_trees':38,'exercises':9,'source_supplied_solutions':9,'tables':5,'rows':21,'cells':42,'empty_cells':7,'canonical_images':16,'new_answers':0,'original_material':'Clearly separated reader guidance and accessibility/source-error notes.'},'excluded_longer_scope':'Remaining m82453 instructional/review/exercise/glossary content, then m82454 and all remaining A10 modules. No other textbook, corpus, control lane or its assets are included. This checkpoint does not reduce the full-book scope.','native_language_evidence':'LANGUAGE_NOTES.md: separately classified university mathematical dictionary observations; native Pakistani classroom authority not claimed. Urdu and English are distinct bridges.','shared_canon':'provenance/SHARED_CANON_PINS.json, unchanged','qa':'QA.json','checksums':'SHA256SUMS','release_payload_excludes':['BUILD_LOG.md'],'publication':'Package owner performs publication; this helper made no remote writes.'}
package['partial_modules'][0]['complete_instructional_sections']=[n.get('id') for n in cn_content[:4] if tag(n)=='section']
package['partial_modules'][0].pop('section_id_note')
dump('PACKAGE.json',package)
dump('QA.json',{'schema':'bounded-recovery-qa-v1','status':'pass' if not fail else 'fail','checks_total':len(checks),'checks_passed':len(checks)-len(fail),'failed_checks':fail,'checks':checks,'coverage':rows,'arithmetic':[{'exercise_id':e,'computed':r,'source_result':s} for e,r,s in arithmetic],'detached_mutations':mutations,'visual':{'automated_browser_results':'visual/browser-results.json','actual_inspection':{'status':inspection['status'],'record':'visual/INSPECTION.json','screenshots_actually_inspected':len(inspection['inspected']),'observations':inspection['observations']},'viewports':[1280,390],'network_blocked':True},'limitations':['Structural and equation preservation is not comprehensive linguistic certification.','Native-Pakistani classroom specialist usage is not established by the paired-script university dictionary.','Screen-reader output was not measured; semantic/alt checks and browser rendering were checked.','Historical immutable source-selection receipts are retained as evidence, not silently upgraded.'],'tex_processes_launched':0})
print(json.dumps({'checks':len(checks),'failures':fail,'counts':rows},ensure_ascii=False))
if fail:raise SystemExit(1)
