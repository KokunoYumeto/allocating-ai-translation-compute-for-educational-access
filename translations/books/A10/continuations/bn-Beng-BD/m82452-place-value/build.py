"""Rebuild one selected Bangladesh Bengali A10 section from hash-locked inputs."""
from pathlib import Path
from lxml import etree as E, html as H
from html import escape
import copy, hashlib, json, re

P=Path(__file__).resolve().parent
M='http://www.w3.org/1998/Math/MathML'
def sha(b): return hashlib.sha256(b).hexdigest()
def write(name,data):
    path=P/name; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data.encode('utf8') if isinstance(data,str) else data)
def dump(name,obj): write(name,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

lock=json.loads((P/'SOURCE_RECOVERY.json').read_text(encoding='utf8'))
raw=(P/'source/place-value.en.cnxml').read_bytes()
assert sha(raw)==lock['section_sha256']
assert sha((P/'source/m82452.en.cnxml').read_bytes())==lock['source_sha256']
source=E.fromstring(raw); target=copy.deepcopy(source)
catalog=json.loads((P/'source/translation-catalog.json').read_text(encoding='utf8'))
translations=json.loads((P/'translation.json').read_text(encoding='utf8'))
assert set(translations)=={row['key'] for row in catalog}
nodes=list(target.iter()); segments=[]
for row in catalog:
    node=nodes[row['node_ordinal']]; field=row['field']
    old=getattr(node,field) if field in ('text','tail') else node.get(field)
    assert old==row['source'] and sha(old.encode())==row['source_sha256']
    value=translations[row['key']]; assert value.strip() and '\ufffd' not in value
    if field in ('text','tail'): setattr(node,field,value)
    else: node.set(field,value)
    segments.append({'segment_id':'A10:m82452:fs-id1170655083568:'+row['key'], 'unit_id':'A10:m82452:fs-id1170655083568', 'locale':'bn-Beng-BD', 'source_anchor':row['anchor'], 'source_sha256':row['source_sha256'], 'target_sha256':sha(value.encode()), 'source':old, 'target':value, 'field':field, 'status':'translated_structurally_checked'})
punctuation=json.loads((P/'punctuation.json').read_text(encoding='utf8'))
for key,row in punctuation.items():
    ordinal=int(key[1:5]); field=key[6:]
    node=nodes[ordinal]; old=getattr(node,field)
    assert old==row['source']
    setattr(node,field,row['target'])
    segments.append({'segment_id':'A10:m82452:fs-id1170655083568:'+key, 'unit_id':'A10:m82452:fs-id1170655083568', 'locale':'bn-Beng-BD', 'source_anchor':lock['section'], 'source_sha256':sha(old.encode()), 'target_sha256':sha(row['target'].encode()), 'source':old, 'target':row['target'], 'field':field, 'status':'translated_punctuation'})
target.set('{http://www.w3.org/XML/1998/namespace}lang','bn-BD')
assert source.xpath('//@id')==target.xpath('//@id')
assert len(list(source.iter()))==len(list(target.iter()))
def maths(root): return [E.tostring(n,method='c14n',exclusive=True,with_comments=False) for n in root.xpath('//*[local-name()="math"]')]
assert maths(source)==maths(target)
for a,b in zip(source.iter(),target.iter()):
    assert a.tag==b.tag
    ignored=('alt','aria-label','{http://www.w3.org/XML/1998/namespace}lang')
    assert {k:v for k,v in a.attrib.items() if k not in ignored}=={k:v for k,v in b.attrib.items() if k not in ignored}
for asset in lock['assets']:
    b=(P/asset['path']).read_bytes(); assert sha(b)==asset['sha256'] and len(b)==asset['bytes']
images={Path(n.get('src')).name:n for n in source.xpath('//*[local-name()="image"]')}
rights_assets=[]; format_mismatches=[]
for asset in lock['assets']:
    name=Path(asset['path']).name; node=images[name]; media=node.getparent(); b=(P/asset['path']).read_bytes()
    actual='image/jpeg' if b.startswith(b'\xff\xd8\xff') else 'image/png' if b.startswith(b'\x89PNG\r\n\x1a\n') else 'unknown'
    row={'media_id':media.get('id'),'source':asset['source'],'path':asset['path'],'bytes':asset['bytes'],'sha256':asset['sha256'],'declared_mime':node.get('mime-type'),'actual_mime':actual,'declaration_matches_bytes':node.get('mime-type')==actual,'component_override_found':False,'license':'CC BY-NC-SA 4.0'}
    rights_assets.append(row)
    if not row['declaration_matches_bytes']: format_mismatches.append(row)
expected_mismatches=lock['asset_format_audit']['recorded_inherited_mismatches']
assert [(r['media_id'],r['path'],r['bytes'],r['sha256'],r['declared_mime'],r['actual_mime']) for r in format_mismatches]==[(r['media_id'],r['path'],r['bytes'],r['sha256'],r['declared_mime'],r['actual_mime']) for r in expected_mismatches]
assert len(rights_assets)-len(format_mismatches)==lock['asset_format_audit']['matching_declarations']
override_names=set(lock['component_rights_evidence']['local_override_elements_checked'])
full_source_root=E.parse(str(P/'source/m82452.en.cnxml')).getroot()
overrides=[n for n in full_source_root.iter() if E.QName(n).localname.lower() in override_names]
assert len(overrides)==lock['component_rights_evidence']['local_override_elements_found']==0
write('source/place-value.bn-BD.cnxml',E.tostring(target,encoding='utf-8',xml_declaration=True,pretty_print=True))
dump('backend/segments.json',segments)
dump('backend/unit.json',{'unit_id':'A10:m82452:fs-id1170655083568','collection_id':'col31130','module_id':'m82452','source_root_id':lock['section'],'locale':'bn-Beng-BD','source_commit':lock['canonical_commit'],'source_section_sha256':lock['section_sha256'],'original_selection':['U01','U02'],'full_module_translated':False,'prerequisite_concepts':['counting','zero','digit'],'concepts':['place-value','international-number-grouping','rounding-whole-numbers'],'source_exercise_ids':lock['exercise_ids'],'supplied_solution_ids':lock['solution_ids'],'added_assessments_file':'../support.json','corrections_file':'../editorial.json','expert_review_log':'../EXPERT_REVIEW_LOG.json','source_asset_records':lock['assets']})
dump('backend/rights.json',{'schema':'a10.component-rights.v1','collection_id':'col31130','module_id':'m82452','section_id':lock['section'],'collection_license':lock['license_evidence'],'component_rights_evidence':lock['component_rights_evidence'],'canonical_bytes_unchanged':True,'assets':rights_assets,'recorded_inherited_mime_mismatches':len(format_mismatches)})

def math_html(node):
    def clone(n,isroot=False):
        z=E.Element(n.tag,nsmap={None:M} if isroot else None); z.attrib.update(n.attrib); z.text=n.text; z.tail=n.tail
        for c in n: z.append(clone(c))
        return z
    z=clone(node,True); z.tail=None
    return E.tostring(z,encoding='unicode')
def render(n):
    q=E.QName(n); tag=q.localname
    if q.namespace==M: return math_html(n)
    nid=' id="'+escape(n.get('id'),quote=True)+'"' if n.get('id') else ''
    inner=escape(n.text or '')+''.join(render(c)+escape(c.tail or '') for c in n)
    if tag=='media':
        im=n.find('{http://cnx.rice.edu/cnxml}image'); assert im is not None
        src='assets/'+Path(im.get('src')).name; alt=n.get('alt','')
        return '<div class="media"'+nid+'><div class="image-explanation"><strong>চিত্রের বাংলা পাঠ:</strong> '+escape(alt)+'</div><details><summary>মূল ইংরেজি চিত্র দেখো</summary><img loading="lazy" src="'+escape(src)+'" alt="'+escape(alt,quote=True)+'"></details></div>'
    if tag=='image': return ''
    if tag=='link':
        ref=n.get('target-id'); href='#'+ref if ref else n.get('url','')
        return '<a'+nid+' href="'+escape(href,quote=True)+'">'+(inner or 'সংশ্লিষ্ট চিত্র')+'</a>'
    if tag=='title':
        h='h2' if E.QName(n.getparent()).localname=='section' else 'h3'
        return '<'+h+nid+'>'+inner+'</'+h+'>'
    if tag=='newline': return '<br'+nid+'>'
    if tag=='emphasis':
        t={'bold':'strong','italics':'em','underline':'u'}.get(n.get('effect'),'span')
        return '<'+t+nid+'>'+inner+'</'+t+'>'
    if tag=='list':
        t='ol' if n.get('list-type')=='enumerated' else 'ul'; cl=' class="circled"' if n.get('class')=='circled' else ''
        return '<'+t+nid+cl+'>'+inner+'</'+t+'>'
    if tag=='table': return '<div class="table-wrap"><table'+nid+' aria-label="'+escape(n.get('aria-label',''),quote=True)+'">'+inner+'</table></div>'
    if tag in ('colspec','label','tgroup'): return inner
    mapping={'section':'section','para':'div','figure':'figure','caption':'figcaption','example':'section','exercise':'section','problem':'div','solution':'section','note':'aside','term':'strong','item':'li','span':'span','tbody':'tbody','thead':'thead','row':'tr','entry':'td'}
    t=mapping.get(tag,'div'); classes=tag+(' '+n.get('class') if n.get('class') else '')
    label='<div class="kind">মূল বইয়ের উদাহরণ</div>' if tag=='example' else '<div class="kind">নিজে করো · মূল বইয়ের অনুশীলন</div>' if tag=='note' and n.get('class')=='try' else '<h4>মূল বইয়ের উত্তর</h4>' if tag=='solution' and n.find('{http://cnx.rice.edu/cnxml}title') is None else ''
    return '<'+t+nid+' class="'+escape(classes,quote=True)+'">'+label+inner+'</'+t+'>'

editorial=json.loads((P/'editorial.json').read_text(encoding='utf8'))
corrections='<section id="edition-notes"><h2>অনুবাদ ও উৎসের সংশোধন নোট</h2><ul>'+''.join('<li><a href="#'+escape(c['anchor'])+'">'+escape(c['label'])+'</a>: '+escape(c['bn'])+'</li>' for c in editorial['corrections'])+'</ul></section>'
head='<!doctype html><html lang="bn-BD"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>স্থানীয় মান · বাংলাদেশের বাংলা · OpenStax A10</title><link rel="stylesheet" href="assets/reader.css"></head><body><main>'
intro='<header><p class="eyebrow">OpenStax · Elementary Algebra 2e · নির্বাচিত অংশ</p><h1>স্থানীয় মান ও আসন্ন মান</h1><p>বাংলাদেশের বাংলা · মূল বইয়ের সম্পূর্ণ নির্বাচিত উপবিভাগ; পুরো বইয়ের অনুবাদ নয়।</p><nav><a href="#source-reading">মূল পাঠ</a> · <a href="companion.html">সহজ ব্যাখ্যা, অনুশীলন ও উত্তর</a> · <a href="#edition-notes">সংশোধন নোট</a></nav></header><aside class="scope"><h2>পড়ার আগে</h2><p>মূল পাঠে আন্তর্জাতিক তিন-অঙ্কের দল, মিলিয়ন, বিলিয়ন ও ট্রিলিয়ন রাখা হয়েছে। আলাদা সহায়ক পাঠে বাংলাদেশের হাজার-লক্ষ-কোটি রীতির সঙ্গে সম্পর্ক দেখানো হয়েছে। বড় সংখ্যার সব অনুশীলন ছোট শিশুর শুরু করার শর্ত নয়। এখানে স্বাভাবিক সংখ্যা 1 থেকে শুরু; whole numbers বলতে শূন্যসহ স্বাভাবিক সংখ্যা বোঝায়, ঋণাত্মক পূর্ণসংখ্যা নয়। মূল অঙ্ক ও MathML অপরিবর্তিত।</p><p>ছবির বাংলা অর্থ সরাসরি পড়া যায়; অপরিবর্তিত মূল ইংরেজি ছবি খুলেও দেখা যায়। নিবন্ধিত সংশোধনগুলো নিচে দেওয়া আছে।</p></aside>'
footer='<footer><p>মূল রচনা: Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis এবং OpenStax-এর অবদানকারীরা। <a href="source/m82452.en.cnxml">অপরিবর্তিত মূল মডিউল</a> · <a href="source/place-value.bn-BD.cnxml">বাংলা CNXML</a> · <a href="backend/rights.json">উৎস ও উপাদানের অধিকার</a> · <a href="LICENSE.txt">CC BY-NC-SA 4.0</a>। পৃথক উপাদানের নোট প্রযোজ্য।</p><p>বাংলা অনুবাদ ও সহায়ক সংযোজনের মডেল: OpenAI Codex gpt-5.6-sol, Ultra. এটি মানব-যাচাইকৃত বা NCTB-অনুমোদিত পাঠ্যক্রমের দাবি নয়।</p></footer></main></body></html>'
write('index.html',head+intro+'<article id="source-reading">'+render(target)+'</article>'+corrections+footer)
support=json.loads((P/'support.json').read_text(encoding='utf8')); parts=['<header><p class="eyebrow">পৃথকভাবে রচিত সহায়ক পাঠ · AX-1 / AX-3</p><h1>একই সংখ্যা, ভিন্নভাবে লেখা</h1><p><a href="index.html">মূল অনুবাদে ফিরি</a></p></header>',support['lesson_html']]
for group,title in [('diagnostic','আগে নিজে যাচাই করি'),('practice','ব্যাখ্যাসহ অনুশীলন'),('recheck','আবার যাচাই করি')]:
    parts.append('<section><h2>'+title+'</h2>')
    for item in support[group]: parts.append('<article class="exercise" id="'+item['id']+'"><h3>'+escape(item['question'])+'</h3><details><summary>উত্তর ও কারণ</summary><p>'+escape(item['answer'])+'</p><p>'+escape(item['reasoning'])+'</p></details></article>')
    parts.append('</section>')
parts.append('<section><h2>এরপর কোন পথে যাব?</h2>'+support['routing_html']+'</section>')
write('companion.html',head+''.join(parts)+footer)

pages=[]
for filename in ('index.html','companion.html'):
    b=(P/filename).read_bytes(); tree=H.fromstring(b); ids=tree.xpath('//@id'); assert len(ids)==len(set(ids))
    for val in tree.xpath('//a/@href | //img/@src | //link/@href'):
        if val.startswith('#'): assert val[1:] in ids,val
        elif not re.match(r'https?://',val): assert (P/val.split('#')[0]).is_file(),val
    assert '\ufffd' not in b.decode('utf8'); pages.append({'path':filename,'bytes':len(b),'sha256':sha(b),'ids':len(ids)})
assert 'সংশ্লিষ্ট চিত্র চিত্রে' not in (P/'index.html').read_text(encoding='utf8')
css=(P/'assets/reader.css').read_text(encoding='utf8')
assert '1080px' not in css and 'max-width:none' in css and 'width:calc(100% - 32px)' in css
dump('PACKAGE.json',{'schema':'a10.selected-learning-packet.v1','package_id':'A10:bn-Beng-BD:m82452:fs-id1170655083568','title':'OpenStax Elementary Algebra 2e — selected Bangladesh Bengali place-value packet','locale':'bn-Beng-BD','coverage':{'module':'m82452','section':'fs-id1170655083568','complete_selected_subsection':True,'full_module':False,'full_book':False,'remaining_selected_a10_work':'unfinished and separately tracked'},'source':{'repository':'openstax/osbooks-prealgebra-bundle','commit':lock['canonical_commit'],'collection':'col31130','module_sha256':lock['source_sha256'],'section_sha256':lock['section_sha256']},'entrypoints':['index.html','companion.html'],'machine_readable':['source/place-value.bn-BD.cnxml','backend/segments.json','backend/unit.json','backend/rights.json'],'learning_support':{'role':'separate authored AX-1/AX-3 support','diagnostic':len(support['diagnostic']),'practice':len(support['practice']),'recheck':len(support['recheck'])},'license':lock['license_evidence'],'model_provenance':'OpenAI Codex gpt-5.6-sol, Ultra','human_or_board_certification':False,'publication_status':'not_published','quality_state':'built; sealing requires independent and browser QA receipts'})
checks=[]
def check(name,value,expected): assert value==expected,(name,value,expected); checks.append({'id':name,'actual':value,'expected':expected,'pass':True})
def rnd(n,place): return ((n+place//2)//place)*place
def bd_group(n):
    digits=str(n); tail=digits[-3:]; head=digits[:-3]; groups=[]
    while head:
        groups.insert(0,head[-2:]); head=head[:-2]
    return ','.join(groups+[tail]) if groups else tail
for n,p,v in [(23658,100,23700),(17852,100,17900),(468751,100,468800),(103978,100,104000),(103978,1000,104000),(103978,10000,100000),(206981,100,207000),(206981,1000,207000),(206981,10000,210000),(784951,100,785000),(784951,1000,785000),(784951,10000,780000)]: check(f'source-round-{n}-{p}',rnd(n,p),v)
for n,pos,d in [(63407218,3,7),(63407218,4,0),(63407218,1,1),(63407218,7,6),(63407218,6,3),(27493615,7,2),(27493615,1,1),(27493615,5,4),(27493615,6,7),(27493615,0,5),(519711641328,9,9),(519711641328,4,4),(519711641328,1,2),(519711641328,5,6),(519711641328,8,7)]: check(f'source-place-{n}-{pos}',n//10**pos%10,d)
for label,groups,value in [('8-165-432-098-710',[8,165,432,98,710],8165432098710),('9-258-137-904-061',[9,258,137,904,61],9258137904061),('17-864-325-619-004',[17,864,325,619,4],17864325619004),('9-246-073-189',[9,246,73,189],9246073189),('2-466-714-051',[2,466,714,51],2466714051),('11-921-830-106',[11,921,830,106],11921830106)]:
    actual=0
    for g in groups: actual=actual*1000+g
    check('source-group-'+label,actual,value)
for group in ('diagnostic','practice','recheck'):
    for item in support[group]:
        c=item['check']; op=c['operation']
        if op=='regroup':
            expected_grouped=bd_group(c['expected'])
            check(item['id']+'-bd-grouping',c['grouped'],expected_grouped)
            assert re.fullmatch(r'\d{1,2}(?:,\d{2})*,\d{3}',c['grouped']),c['grouped']
            displayed=re.search(r'[০-৯]{1,2}(?:,[০-৯]{2})*,[০-৯]{3}',item['answer'])
            assert displayed,item['answer']
            displayed_ascii=displayed.group(0).translate(str.maketrans('০১২৩৪৫৬৭৮৯','0123456789'))
            check(item['id']+'-display-bd-grouping',displayed_ascii,expected_grouped)
            actual=int(c['grouped'].replace(',',''))
        else:
            actual={'digit':lambda:c['number']//10**c['power']%10,'place_value':lambda:(c['number']//10**c['power']%10)*10**c['power'],'round':lambda:rnd(c['number'],c['place']),'sum':lambda:sum(c['terms']),'member':lambda:int(c['number']>=c['start'])}[op]()
        check(item['id'],actual,c['expected'])
dump('QA.json',{'schema':'a10-bn-bd-section-qa.v2','source_ids_unchanged':True,'nonlanguage_attributes_unchanged':True,'mathml_unchanged':True,'mathml_count':len(maths(source)),'source_elements':len(list(source.iter())),'source_ids':len(source.xpath('//@id')),'language_slots_translated':len(catalog),'punctuation_slots_translated':len(punctuation),'segment_records':len(segments),'source_exercises':len(lock['exercise_ids']),'supplied_solutions':len(lock['solution_ids']),'assets_verified':len(lock['assets']),'asset_mime_matches':len(rights_assets)-len(format_mismatches),'recorded_inherited_asset_mime_mismatches':len(format_mismatches),'component_rights_record':'backend/rights.json','bangladesh_grouping_display_bound':True,'mathematical_checks':checks,'pages':pages,'browser_visual_qa':'pending','independent_semantic_review':'pending','status':'structural_and_authored_math_pass_not_release_ready'})
print(json.dumps({'translation_slots':len(segments),'elements':len(list(source.iter())),'ids':len(source.xpath('//@id')),'mathml':len(maths(source)),'math_checks':len(checks),'pages':pages,'status':'built_for_visual_review'}))
