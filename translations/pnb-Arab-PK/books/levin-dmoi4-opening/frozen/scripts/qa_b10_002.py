"""Independent source-bound QA for B10-002; detached mutations never edit real files.

Shared pinned-input helpers are reused read-only. Reader rendering is not called.
Handwritten mathematical expectations do not import the TeX mapper.
"""
import ast
import copy
import html as H
import json
import re
from lxml import etree as E, html as LH
from prepare_b10_002 import *
from b10_002_math_expected import expected, EXPECTED
from b10_002_tex import convert, TexError, FALLBACK_RAW
MATH='http://www.w3.org/1998/Math/MathML'
NS={'m':MATH}
FRAME_SEAL='2ed02df05ac9f8cceb2afd4965bcafffea82876fc38898d22bd4aa34fc26bf5a'
EXPECTED_NOTICE=None
WITNESS_DIR='provenance/b10-unit-002-components/'
OPL_PREFIX='Contrib/DMOI/0-Introduction_and_Preliminaries/0_2-Mathematical_Statements/'
WITNESS_EXPECTED=[
    ('OPL_LICENSE','opl',1310,'42f623d31af8c3ee30acf0c16f8dbae37e16350352efdf3a186afab63685dcaf','13b672dbdbb05036f983304b73fbe229b9e4646a'),
    (OPL_PREFIX+'0_2_1.pg','opl',3580,'d9ed29e0541b3adadf21765c7d655cb9946d9a8be079cd9c5c96e0dc314db9a0','a400b21aa3bda2a7eba76ac4c93e9f1ae6027990'),
    (OPL_PREFIX+'0_2_2.pg','opl',3348,'1e85f23b0493ed3e766f80ecc1e7cdb4008fbec5ca5e56a3f11d4a4bc924b5bf','5a490e9e637adc7c9d4ff945ea21bb24d797eb51'),
    (OPL_PREFIX+'0_2_4.pg','opl',3011,'9490f3eda74dd81c53484a7bc927bd63c952ba975faa63c39ec88945a1139da7','d7208400a0940f758646acc355879640bb0c976f'),
    (OPL_PREFIX+'0_2_15.pg','opl',2067,'b8e71d208a7f2f7a9da673da96cb140f83659c6aaeb7fc3ca6ac26d9773688ba','64884168dcc8ef518812a4ebf236c9d15f1a1852'),
    ('source/practice/wwpg/statements-quant1.pg','dmoi-local-pg',4199,'659b1ec51f8bd668c90c446495c85179a7051589e1f6b5c7cc75b171e43bab3e','38498d5c55cc1e1699407b17ff304acc29d58bbe'),
    ('source/practice/wwpg/statements-quant2.pg','dmoi-local-pg',4198,'3160b52ef7b9658f5b0922567d5f2957716a0d8c8caaf253a7d2c99eb513a892','9a0c9b064add5a36b2bed4d8f7acde87f03c58b5'),
]
PRODUCTION_CANON='canon/receipts/B10-002-production-qa-20260831T140105847321Z.json'
PENDING={'sec_logic-implications':'استلزام','sec_logic-rules':'منطق دے اصول','sec_logic-proofs':'ثبوت','sec_logic-structures':'ڈسکریٹ بناوٹاں بارے ثبوت'}
HEADINGS={'objectives':'سکھن دے مقصد','investigation':'کھوج لاؤ!','definition':'تعریف','example':'مثال','aside':'نالے ایہہ وی…','remark':'اک ہور گل','worksheet':'مل کے مشق','reading-questions':'پڑھن بارے سوال','exercise':'مشق','assemblage':'خلاصہ'}
DISCLOSURES={'solution':'ماخذ دا حل — کھولو','answer':'ماخذ دا جواب — کھولو','feedback':'ماخذ دی رہنمائی — کھولو','hint':'ماخذ دا اشارہ — کھولو'}

class Checks:
    def __init__(self):self.count=0
    def ok(self,value,label):
        self.count+=1
        if not value:raise AssertionError(label)

def fragment(v):return E.fromstring(('<fragment>'+v+'</fragment>').encode())
def canonical(n):return E.tostring(n,method='c14n',with_comments=False)
def desc(n):return [E.QName(n).localname,dict(n.attrib),n.text,[desc(c) for c in n]]
def esc(v):return H.escape(str(v),quote=True)
def aj(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def inner(n):return [n.text,[[tree(c),c.tail] for c in n]]
def nearest(n):
    return next((a.get('data-source-node') for a in n.iterancestors() if a.get('data-source-node')),None)
def markup(n):
    return H.escape(n.text or '',quote=False)+''.join(E.tostring(c,encoding='unicode') for c in n)
def stub(k):return '<source-slot key="'+esc(k)+'"/>'
def frame_hash(root):
    c=copy.deepcopy(root)
    for e in list(c.xpath('//*[@data-source-node]')):
        if not any(a.get('data-source-node') for a in e.iterancestors()):
            s=E.Element('source-slot',key=e.get('data-source-node'));s.tail=e.tail;e.getparent().replace(e,s)
    return digest(canonical(c))

def source_sequence(roots,cache,keys):
    def walk(e):
        yield keys[e]
        if e.tag==XI and e.get('parse')!='text':
            yield from walk(roots['source/'+e.get('href')])
        else:
            for c in e:yield from walk(c)
        if e.tag=='chapter':yield from walk(roots[SECTION])
    return list(walk(roots[CHAPTER]))+[keys[e] for c in cache for e in c.find('static').iter()]

def expected_attrs(e,k,t,m):
    a={'data-source-node':k,'data-source-tag':e.tag,'data-source-attributes':aj(dict(e.attrib))}
    if e.get(XID):a['id']=e.get(XID)
    elif e.get('label') and e.tag=='exercise':a.update(id=e.get('label'),**{'data-anchor-origin':'source-label'})
    if k in t['source_blocks']:a['data-source-key']=k
    warns=[x['id'] for x in t['original_notes'] if x['kind']!='original-clarification' and k in x['source_keys']]
    if warns:a['aria-describedby']=' '.join(warns)
    return a,warns

def warning_html(k,warns):
    return '' if not warns else '<span class="source-warning" data-origin="original-note-link">ماخذ دے ایس متن بارے وکھری درستی: '+''.join('<a href="#'+w+'" data-correction-for="'+esc(k)+'">نوٹ کھولو</a>' for w in warns)+'</span>'

def collapse_container(n):
    c=copy.deepcopy(n)
    for e in list(c.iterdescendants()):
        if e.getparent() is None:continue
        if e.get('data-source-node') and not any(a is not c and a.get('data-source-node') for a in e.iterancestors()):
            s=E.Element('source-slot',key=e.get('data-source-node'));s.tail=e.tail;e.getparent().replace(e,s)
    return inner(c)

def expected_structural_content(e,k,roots,cache,keys,raws,m):
    def child(c):
        s=stub(keys[c])
        return '<div class="source-table-scroll" data-origin="renderer-ui-wrapper">'+s+'</div>' if c.tag=='tabular' else s
    children=H.escape(e.text or '',quote=False)+''.join(child(c)+H.escape(c.tail or '',quote=False) for c in e)
    tag=e.tag
    if tag=='idx':
        body='<span class="index-marker" tabindex="0" data-origin="renderer-ui" aria-label="ماخذ دا فہرستی لفظ">فہرست</span><span class="index-content" data-origin="renderer-ui-wrapper">'+children+'</span>'
    elif tag=='tabular':
        body='<colgroup data-origin="renderer-ui-wrapper">'+''.join(stub(keys[c]) for c in e if c.tag=='col')+'</colgroup><tbody data-origin="renderer-ui-wrapper">'+''.join(stub(keys[c]) for c in e if c.tag=='row')+'</tbody>'
    elif tag=='col':body=''
    elif tag in DISCLOSURES:body='<summary data-origin="renderer-ui">'+DISCLOSURES[tag]+'</summary>'+children
    elif tag=='response':
        body='<label data-origin="renderer-ui">آپ جواب لکھ کے آزما لو — ایہہ خانہ محفوظ نہیں ہُندا<textarea aria-label="اپنا عارضی جواب" data-origin="renderer-ui" rows="3"></textarea></label>'
    elif tag=='choice':
        flag=e.get('correct','unspecified')
        body=children+'<details data-origin="renderer-ui" class="source-choice-flag"><summary>ماخذ دے اختیار دا نشان</summary><p>اصل نشان: <bdi dir="ltr" lang="en">'+flag+'</bdi>۔ ایہہ خودکار جانچ نہیں؛ درستی دے وکھرے نوٹ وی ویکھو۔</p></details>'
    elif tag==XI:
        if e.get('parse')=='text':
            f='source/practice/'+e.get('href')
            body='<summary data-origin="renderer-ui">اصل مقامی سوال دا کوڈ — صرف متن، نہیں چلایا گیا</summary><pre dir="ltr"><code data-source-inert-pg="'+esc(f)+'">'+H.escape(raws[f].decode(),quote=False)+'</code></pre>'
        else:body=stub(keys[roots['source/'+e.get('href')]])
    elif tag=='webwork':
        i,b=next((i,b) for i,b in enumerate(m['cached_static_bindings'],1) if b['owner']==k)
        body='<p data-origin="renderer-ui" class="snapshot-label">ایس مشق دی اک مقرر محفوظ صورت: <a data-cache-owner="'+esc(k)+'" href="#'+b['cache_xml_id']+'"><bdi dir="ltr" lang="en">'+b['cache_ww_id']+'</bdi> — بیج <bdi dir="ltr">'+b['seed']+'</bdi> کھولو</a>۔ سوال خودکار طور اُتے نواں نہیں بنے گا؛ نمبر نہیں لگن گے۔</p>'+children
    else:
        body=('<h4 data-origin="renderer-ui">'+HEADINGS[tag]+'</h4>' if tag in HEADINGS and e.find('title') is None else '')+children
        if tag=='chapter':body+='<div data-origin="expanded-section" data-expanded-source="'+SECTION+'">'+stub(keys[roots[SECTION]])+'</div>'
    return inner(fragment(body))

def validate_structure(root,args,c):
    m,t,roots,cache,nodes,keys,raws=args
    rendered=root.xpath('//*[@data-source-node]');wanted=source_sequence(roots,cache,keys)
    c.ok([n.get('data-source-node') for n in rendered]==wanted and len(wanted)==1602,'exact1602 DOM source node order')
    actual={n.get('data-source-node'):n for n in rendered};c.ok(len(actual)==1602,'unique source nodes')
    c.ok([n.get('data-source-key') for n in root.xpath('//*[@data-source-key]')]==m['expected_source_keys'],'559 exact translated blocks/order')
    block_specs={b['key']:b for b in m['source_blocks']}
    inlinekeys={x['path'] for b in m['source_blocks'] for x in b['inline_markup']}
    for k,e in nodes.items():
        n=actual[k];base,warns=expected_attrs(e,k,t,m)
        for a,v in base.items():c.ok(n.get(a)==v,'source node attribute '+a+' '+k)
        parent=e.getparent()
        if e is roots[SECTION]:owner=keys[roots[CHAPTER]]
        elif parent is None and k!=keys[roots[CHAPTER]]:
            owner=next(keys[x] for x in roots[SECTION] if x.tag==XI and 'source/'+x.get('href')==k.split('#')[0])
        elif e.tag=='static':owner=None
        else:owner=keys.get(parent)
        c.ok(nearest(n)==owner,'source node exact ancestor '+k)
        if k in inlinekeys:
            c.ok(n.tag=={'term':'span','alert':'strong','foreign':'span'}.get(e.tag,e.tag),'inline source tag')
            allowed=set(base)|({'data-source-term'} if e.tag=='term' else set())
            c.ok(set(n.attrib)==allowed,'inline no injected attrs');continue
        if k in block_specs:
            expectedtag={'title':'h1' if parent.tag=='chapter' else 'h2' if parent.tag=='section' else 'h3','cell':'th' if parent.get('header')=='yes' else 'td','li':'li','caption':'figcaption','h':'span','see':'span','fn':'span'}.get(e.tag,'div')
            cls='source-index-'+e.tag if e.tag in {'h','see'} else 'source-'+e.tag
            base['class']=cls
            if e.tag=='cell':
                base['dir']='rtl' if re.search('[\u0600-\u06ff]',t['source_blocks'][k]) else 'ltr'
                if expectedtag=='th':base['scope']='col'
            c.ok(n.tag==expectedtag and dict(n.attrib)==base,'block HTML type/full attrs '+k)
            cl=copy.deepcopy(n)
            if warns:
                ws=cl.xpath('./span[@class="source-warning"]')
                c.ok(len(ws)==1 and tree(ws[0])==tree(fragment(warning_html(k,warns))[0]),'exact visible correction links')
                cl.remove(ws[0])
            for slot in block_specs[k]['slots']:
                hits=cl.xpath('.//*[@data-source-node=$key]',key=slot['source_path']);c.ok(len(hits)==1,'exact own-block slot '+slot['source_path'])
                s=hits[0];p=s.getparent();idx=p.index(s);text=slot['token']+(s.tail or '')
                if idx:p[idx-1].tail=(p[idx-1].tail or '')+text
                else:p.text=(p.text or '')+text
                p.remove(s)
            for d in cl.iterdescendants():
                if d.tag!='bdi':
                    for a in list(d.attrib):
                        if a!='data-source-term':del d.attrib[a]
            c.ok(inner(cl)==inner(fragment(t['source_blocks'][k])),'exact translated own-text, punctuation, numbers, inline/slot order '+k)
            for bdi in cl.iter('bdi'):c.ok(bdi.get('dir')=='ltr','exact target numeral/English isolation')
            continue
        if e.tag in {'m','me'}:continue
        if e.tag=='xref':
            ref=e.get('ref')
            if ref in PENDING:
                base.update({'class':'pending-reference','data-reference-status':'pending'})
                wantedtext=PENDING[ref]+' <span class="pending-marker" data-origin="renderer-ui">(اگلا حصہ؛ پنجابی متن ہن موجود نہیں)</span>'
                typ='span'
            else:
                target=next(v for v in nodes.values() if v.get(XID)==ref);label=''.join(fragment(t['source_blocks'][keys[target.find('title')]]).itertext())
                base.update(href='#'+ref,**{'data-reference-status':'available'});wantedtext=H.escape(label,quote=False);typ='a'
            c.ok(n.tag==typ and dict(n.attrib)==base and inner(n)==inner(fragment(wantedtext)),'exact source xref target/status/local label');continue
        if e.tag in {'ellipsis','lq','rq'}:
            base['class']='source-symbol';c.ok(n.tag=='span' and dict(n.attrib)==base and n.text=={'ellipsis':'…','lq':'“','rq':'”'}[e.tag] and not len(n),'exact source punctuation symbol');continue
        tag=e.tag
        typ={'chapter':'article','blockquote':'blockquote','ol':'ol','ul':'ul','li':'li','figure':'figure','idx':'span','tabular':'table','col':'col','row':'tr'}.get(tag,'section' if tag in {'section','subsection','exercise','definition','example','exercises','static'} else 'div')
        cls={'idx':'source-index','tabular':'source-tabular'+(' prose-table' if '/example[1]/statement[1]/tabular[' in k else ''),'response':'source-empty-response'}.get(tag,'source-'+tag)
        if tag in DISCLOSURES:typ='details'
        if tag==XI:
            if e.get('parse')=='text':typ='details';cls='source-inert-pg'
            else:cls='source-expanded-include';base['data-expanded-source']='source/'+e.get('href')
        if tag=='webwork':base['id']='webwork-owner-'+str(next(i for i,b in enumerate(m['cached_static_bindings'],1) if b['owner']==k))
        if tag not in {'col','row'}:base['class']=cls
        if tag=='tabular':base['dir']='ltr'
        if tag=='row':base['data-source-bottom']=e.get('bottom','')
        if tag=='col':base['data-source-right']=e.get('right','')
        if tag=='ol' and e.get('label')=='a.':base['type']='a'
        c.ok(n.tag==typ and dict(n.attrib)==base,'exact structural HTML mapping/attrs '+k)
        c.ok(collapse_container(n)==expected_structural_content(e,k,roots,cache,keys,raws,m),'exact container own text/tails/children and bounded generated UI '+k)
    for tab in m['source_tables']:
        n=actual[tab['source_path']]
        rows=n.xpath('./tbody/tr');c.ok([len(r) for r in rows]==tab['row_cell_counts'],'source table physical row/cell shape')
        c.ok([x.get('data-source-node') for r in rows for x in r]==[keys[x] for r in nodes[tab['source_path']].findall('row') for x in r],'all table cells exact order')
    c.ok(len(root.xpath('//table'))==8 and len(root.xpath('//table//td|//table//th'))==104,'8tables104cells exact')
    c.ok(len(root.xpath('//*[@data-source-tag="exercise"]'))==23,'23authored exercise nodes')
    c.ok(len(root.xpath('//*[@data-source-tag="choice"]'))==34 and len(root.xpath('//*[@data-source-tag="match"]'))==8,'source choice/match count')
    c.ok(len(root.xpath('//textarea'))==2,'two source empty-response boxes only')
    lettered=root.xpath('//ol[@type="a"]')
    c.ok(len(lettered)==2 and [len(n.findall('li')) for n in lettered]==[3,3],'two source a/b/c cached lists; no invented numbering')
    return actual

def validate_math(root,m,notices,actual,c):
    rows=notices['math_conversion']['records'];c.ok(len(rows)==337,'337mathrecords')
    c.ok(len(root.findall('.//m:math',NS))==336,'336reviewed MathML roots')
    c.ok(len(root.xpath('//*[@class="tex-unreviewed"]'))==1,'one explicit raw spacing fallback')
    panels=root.xpath('//*[@data-tex-owner]');c.ok(len(panels)==337,'all337 raw panels')
    symbols={'therefore':'∴','cdot':'⋅','cdots':'⋯','ldots':'…','wedge':'∧','vee':'∨','imp':'→','iff':'↔','neg':'¬','forall':'∀','exists':'∃','ge':'≥','gt':'>','le':'≤','lt':'<'}
    for number,(s,r,panel) in enumerate(zip(m['tex_slots'],rows,panels),1):
        raw=s['raw_tex'];target=expected(raw);n=actual[s['source_path']];status='source-tex-fallback' if raw==FALLBACK_RAW else 'derived-mathml'
        base={'data-source-node':s['source_path'],'data-source-tag':s['source_tag'],'data-source-attributes':aj(s['source_attributes']),'class':'source-math'+(' source-display-math' if s['source_tag']=='me' else ''),'dir':'ltr','data-source-tex':raw,'data-source-tex-sha256':digest(raw.encode()),'data-math-status':status}
        c.ok(n.tag=='span' and dict(n.attrib)==base and n.text is None and len(n)==2 and all(x.tail is None for x in n),'exact math owner/wrapper source text/attrs')
        link=fragment('<a class="tex-link" data-origin="renderer-ui" href="#source-tex-'+str(number).zfill(3)+'" aria-label="اصل فارمولا ویکھو" lang="en" dir="ltr">TeX</a>')[0]
        c.ok(tree(n[1])==tree(link),'exact math fallback link')
        display='block' if s['source_tag']=='me' else 'inline'
        if target is None:c.ok(tree(n[0])==tree(fragment('<code class="tex-unreviewed" dir="ltr">'+H.escape(raw,quote=False)+'</code>')[0]),'exact unreviewed negative space fallback')
        else:
            math=n[0];c.ok(math.tag=='{'+MATH+'}math' and dict(math.attrib)=={'dir':'ltr','display':display} and math.text is None and len(math)==1,'MathML root/isolation')
            sem=math[0];c.ok(sem.tag=='{'+MATH+'}semantics' and not sem.attrib and sem.text is None and len(sem)==2,'exact semantics shape')
            c.ok(desc(sem[0])==target,'independent handwritten full mathematical tree '+s['source_path'])
            ann=sem[1];c.ok(ann.tag=='{'+MATH+'}annotation' and dict(ann.attrib)=={'encoding':'application/x-tex'} and ann.text==raw and not len(ann),'exact source TeX annotation')
            c.ok(all(x.tail is None for x in math.iter()),'no math tail text')
        fields={'number':number,'source_path':s['source_path'],'owner_key':s['owner_key'],'token':s['token'],'source_tag':s['source_tag'],'source_attributes':s['source_attributes'],'source_tex':raw,'source_tex_sha256':digest(raw.encode()),'display':display,'status':status,'tree':target,'tree_sha256':jhash(target) if target is not None else None}
        for f,v in fields.items():c.ok(r[f]==v,'source math record '+f)
        c.ok(panel.get('data-tex-owner')==s['source_path'] and panel.get('id')=='source-tex-'+str(number).zfill(3),'exact raw fallback owner')
        code=panel.find('pre/code');c.ok(code is not None and code.text==raw and not len(code),'full unchanged raw TeX fallback')
        paths={};leaves=[]
        def walk(d,path):
            paths[path]=d
            if not d[3]:leaves.append(path)
            counts={}
            for ch in d[3]:counts[ch[0]]=counts.get(ch[0],0)+1;walk(ch,path+'/'+ch[0]+'['+str(counts[ch[0]])+']')
        if target is not None:walk(target,'/math/semantics/mrow[1]')
        cursor=0;read_leaves=[]
        for tok in r['tokens']:
            v=tok['raw'];bound=tok['mathml_paths']
            c.ok(tok['start']==cursor and tok['end']==cursor+len(v) and raw[cursor:tok['end']]==v,'exact contiguous source token offsets')
            cursor=tok['end'];kind='space' if v.isspace() else 'command' if v.startswith('\\') else 'number' if v.isdigit() else 'variable' if v.isalpha() else 'syntax'
            c.ok(tok['kind']==kind and len(bound)<=1 and all(p in paths for p in bound),'token kind/independent path')
            if target is None:c.ok(not bound and tok['effect']=='Unreviewed negative-spacing form: unchanged source TeX fallback','raw fallback retains every spacing token');continue
            if not bound:
                c.ok(v.isspace() and tok['effect']=='TeX presentation whitespace; exact raw retained','exact source whitespace ledger');continue
            path=bound[0];d=paths[path]
            if d[0]=='mtext':
                c.ok(tok['effect'] in {'literal source text command','nonprinting text boundary','exact literal mtext payload including spaces'},'literal mtext exact spacing ledger')
                if not read_leaves or read_leaves[-1]!=path:read_leaves.append(path)
            elif v in {'{','}'}:c.ok(d[0]=='mrow' and tok['effect']=='nonprinting source group boundary','exact invisible group boundary')
            elif v=='^':c.ok(d[0]=='msup' and tok['effect']=='whole preceding atom superscript binding','whole base superscript ledger')
            else:
                typ,text=('mo',symbols[v[1:]]) if v.startswith('\\') else ('mn',v) if v.isdigit() else ('mi',v) if v.isalpha() else ('mo','−' if v=='-' else v)
                c.ok((d[0],d[2])==(typ,text),'exact independently mapped variable/number/operator')
                effect='whitelisted source symbol or inert macro expansion' if v.startswith('\\') else 'unchanged numeric token' if v.isdigit() else 'unchanged variable token' if v.isalpha() else 'visible source opening fence' if v in {'(','['} else 'visible source closing fence' if v in {')',']'} else 'ASCII source minus to U+2212' if v=='-' else 'unchanged operator/separator'
                c.ok(tok['effect']==effect,'exact reversible operator/fence ledger effect');read_leaves.append(path)
        c.ok(cursor==len(raw) and ''.join(x['raw'] for x in r['tokens'])==raw,'reverse full source TeX')
        if target is not None:c.ok(read_leaves==leaves,'all source token leaves exact order')
    c.ok(root.xpath('//*[@data-source-macros]')[0].text==m['source_macros'],'full inert macros retained')

def validate_components(root,m,notice,c,byte_overrides=None):
    """Independent exact-byte/path/header/owner checks; overrides are detached only."""
    package=notice['selected_component_witnesses'];rows=package['files'];overrides=byte_overrides or {}
    c.ok(package['acquisition_path']==WITNESS_DIR+'acquisition.json' and package['acquisition_sha256']=='193867036f31da9ddb10ce1b89f47a08078d9d7a7e643098176fc6d462b2ed51','scoped acquisition identity')
    c.ok(file_hash(BASE/package['acquisition_path'])==package['acquisition_sha256'],'exact acquisition record retained')
    c.ok(len(rows)==7 and len(root.xpath('//*[@data-component-witness]'))==7,'exact seven retained witness links/records')
    links=root.xpath('//*[@data-component-witness]')
    for row,link,(source,kind,size,sha,blob) in zip(rows,links,WITNESS_EXPECTED):
        local=WITNESS_DIR+('OPL/' if kind=='opl' else 'dmoi4/')+source
        c.ok((row['repository_path'],row['kind'],row['local_path'],row['bytes'],row['sha256'],row['git_blob_sha1'])==(source,kind,local,size,sha,blob),'independent selected component identity '+source)
        raw=overrides[local] if local in overrides else (BASE/local).read_bytes()
        c.ok(isinstance(raw,bytes),'selected witness is present '+source)
        c.ok((len(raw),digest(raw),hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())==(size,sha,blob),'exact selected witness bytes/line endings/blob '+source)
        commit='521448225da9a2dc4ebf1ed6258f7afe2f1b5eac' if kind=='opl' else '82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799'
        repository='https://github.com/openwebwork/webwork-open-problem-library' if kind=='opl' else 'https://github.com/oscarlevin/discrete-book'
        c.ok(row['commit']==commit and row['repository']==repository,'exact component pin/repository '+source)
        c.ok(dict(link.attrib)=={'data-component-witness':source,'href':'../'+local} and link.text==Path(source).name and len(link)==0,'offline original witness link/label '+source)
        if source=='OPL_LICENSE':c.ok(row['verbatim_notice']==raw.decode(),'OPL terms retained verbatim, not silently relicensed')
        else:
            c.ok(row['source_header_verbatim']==raw.decode().split('DOCUMENT();',1)[0],'exact attribution/header retains source Edition3 and English language '+source)
            c.ok('## Author(Oscar Levin)' in row['source_header_verbatim'] and '## Institution(University of Northern Colorado)' in row['source_header_verbatim'],'named author/institution retained '+source)
    c.ok(root.xpath('//*[@data-component-acquisition]')[0].get('href')=='../'+WITNESS_DIR+'acquisition.json','export receipt link exact')
    associations=package['source_cache_associations'];c.ok(len(associations)==6,'exact six cache-to-code witness associations')
    for record,b in zip(associations,m['cached_static_bindings']):
        source=b['source'] or b['parse_text_source'];row=next(x for x in rows if x['repository_path']==source)
        c.ok(record=={'owner':b['owner'],'cache_xml_id':b['cache_xml_id'],'seed':b['seed'],'repository_path':source,'local_path':row['local_path'],'sha256':row['sha256']},'exact authored owner/seed/cache/source component association')

def validate_global(root,args,notice,c):
    m,t,roots,cache,nodes,keys,raws=args
    c.ok(frame_hash(root)==FRAME_SEAL,'reviewed full frame/cache metadata/original-note/raw-fallback seal')
    c.ok(dict(root.attrib)=={'lang':'pnb-Arab-PK','dir':'rtl'},'locale RTL')
    c.ok([x.tag for x in root]==['head','body'] and [x.tag for x in root.find('body')]==['header','main','footer'],'exact document boundary')
    ids=root.xpath('//@id');c.ok(len(ids)==len(set(ids)),'all IDs unique')
    for a in root.xpath('//a[starts-with(@href,"#")]'):c.ok(a.get('href')[1:] in ids,'all local anchors resolve')
    c.ok(not root.xpath('//script|//iframe|//img|//object|//embed|//link|//*[@hidden]|//*[@aria-hidden]|//*[@style]'),'no unexpected runtime/image/hidden/style')
    c.ok(not any(a.lower().startswith('on') for n in root.iter() for a in n.attrib),'no event execution')
    module=ast.parse((BASE/'scripts/build_b10_002.py').read_text('utf-8'));css=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='LOCAL_CSS' for x in n.targets))
    c.ok(root.find('head/style').text==(BASE/'styles/reader.css').read_text('utf-8')+css and '.b10-002 mtext{white-space:pre}' in css,'exact stylesheet and literal MathML text spacing')
    c.ok('.b10-002 ol[type="a"],.b10-002 ol[type="a"]>li{list-style-type:lower-alpha}' in css,'explicit source alphabetic-list style overrides inherited decimal CSS')
    c.ok(not re.search(r'@import|url\s*\(',css),'no style network')
    for n in root.find('body').iter():
        for value,p in [(n.text,n),(n.tail,n.getparent())]:
            if re.search('[A-Za-z0-9]',value or ''):c.ok(p is not None and any(x.get('dir')=='ltr' for x in [p]+list(p.iterancestors())),'visible ASCII LTR isolation')
    meta={n.get('name'):n.get('content') for n in root.findall('head/meta') if n.get('name')}
    c.ok(all(meta.get(k)==v for k,v in {'source-author':'Oscar Levin','source-edition':'Fourth Edition','source-book-id':'dmoi4','source-document-id':'dmoi-4','source-copyright':'2013–2025 Oscar Levin'}.items()),'exact edition metadata')
    records=root.xpath('//*[@data-cache-record]');c.ok(len(records)==6,'six separate fixed snapshots')
    for i,(n,b,source) in enumerate(zip(records,m['cached_static_bindings'],cache),1):
        c.ok(n.get('id')==b['cache_xml_id'] and n.get('data-cache-owner')==b['owner'] and n.get('data-cache-record')==str(i),'fixed snapshot association/order')
        c.ok(n.get('data-cache-attributes')==aj(dict(source.attrib)) and n.get('data-cache-tree-sha256')==m['cache_record_tree_sha256'][i-1],'cache attrs/record provenance')
        c.ok(json.loads(n.xpath('.//*[@data-cache-metadata]')[0].text)=={s.tag:tree(s) for s in source if s.tag!='static'},'all inert cache rendering-data and PG retained')
        c.ok(n.xpath('.//*[@data-cache-return]')[0].get('href')=='#webwork-owner-'+str(i),'exact static return link')
    c.ok(len(records[3].xpath('./p[@class="cache-warning"]/a[@href="#b10-002-cache-parity"]'))==1,'bad cache parity warning always visible outside answer disclosure')
    notes=root.xpath('//*[@id="b10-002-original-notes"]/section');c.ok([n.get('id') for n in notes]==[n['id'] for n in t['original_notes']],'all10 original notes separate/order')
    for n,s in zip(notes,t['original_notes']):
        c.ok(n.get('data-origin')=='original' and n.get('data-note-kind')==s['kind'] and n.findtext('h3')==s['title'],'source correction identity')
        c.ok(inner(n.find('div'))==inner(fragment(s['html'])) and not n.xpath('.//*[@data-source-node]'),'exact original content not source')
    c.ok(notice['existing_notice_policy']==retained_policy() and notice['images']==[] and notice['whole_book_translation_complete'] is False,'retained notices/noassets/incomplete')
    c.ok('six authored WeBWorK owners' in notice['existing_notice_policy']['components'] and 'historical_scope_context' in notice['existing_notice_policy'],'current six-component inventory explicitly distinguished from historical zero claim')
    c.ok(notice['source_specific_license']=='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International' and notice['source_copyright']=='2013–2025 Oscar Levin','active edition rights retained')
    for p,f in [(MANIFEST,'manifest_sha256'),(EXCERPT,'excerpt_sha256'),(CACHE,'cache_excerpt_sha256'),(TRANSLATION,'translation_sha256')]:c.ok(notice[f]==file_hash(p),'notice frozen input '+f)
    c.ok(notice['cached_static_bindings']==m['cached_static_bindings'] and notice['inert_metadata_dependencies']==m['metadata_files'],'cache metadata sourcebinding')
    validate_components(root,m,notice,c)

def validate(root,args,notice):
    c=Checks();validate_global(root,args,notice,c)
    actual=validate_structure(root,args,c);validate_math(root,args[0],notice,actual,c)
    if EXPECTED_NOTICE is not None:c.ok(notice==EXPECTED_NOTICE,'complete source-specific notice contract, supplemental to independent math checks')
    return c.count

def main():
    global EXPECTED_NOTICE
    args=load_inputs();m,t=args[:2];raw=OUTPUT.read_text('utf-8');root=E.fromstring(raw.replace('<!doctype html>','').encode());notice=json_read(NOTICES)
    EXPECTED_NOTICE=notice_record(m)
    canon=json_read(BASE/PRODUCTION_CANON)
    assert canon['stage']=='production-qa' and canon['unit']=='B10-002'
    for row in canon['examples']:
        data=(ROOT/row['path']).read_bytes()
        assert digest(data)==row['text_raw_sha256'] and digest(data.decode('utf-8').splitlines()[row['line']-1].encode())==row['paragraph_sha256'],'Production canon locus changed'
    count=validate(root,args,notice)
    browser=LH.fromstring(raw);src=source_sequence(args[2],args[3],args[5])
    assert [n.get('data-source-node') for n in browser.xpath('//*[@data-source-node]')]==src,'HTML parser source order differs'
    for n in browser.xpath('//*[@data-source-node]'):
        xml=root.xpath('//*[@data-source-node=$k]',k=n.get('data-source-node'))[0]
        assert nearest(n)==nearest(xml),'HTML parser reparents source child'
        if n.get('data-source-tex') is not None:assert n.get('data-source-tex')==xml.get('data-source-tex'),'HTML parser source TeX changes'
    count+=1+1602+337
    mutations=[]
    def mutation(name,change):
        r=copy.deepcopy(root);n=copy.deepcopy(notice);change(r,n)
        try:validate(r,args,n)
        except (AssertionError,ValueError,KeyError,IndexError,TypeError,E.XMLSyntaxError) as exc:mutations.append({'name':name,'rejected_by':str(exc)})
        else:raise AssertionError('Surviving detached mutation: '+name)
    def sn(r,k):return r.xpath('//*[@data-source-node=$k]',k=k)[0]
    keys=m['expected_source_keys']
    mutation('translated title replaced',lambda r,n:setattr(sn(r,keys[0]),'text','نواں عنوان'))
    mutation('prose numeral changed',lambda r,n:setattr(sn(r,keys[135]).xpath('.//bdi')[0],'text','6'))
    mutation('unkeyed chapter conclusion injection',lambda r,n:sn(r,CHAPTER+'#/chapter').append(E.fromstring('<p>All statements are true.</p>')))
    mutation('unkeyed statement own text injection',lambda r,n:setattr(r.xpath('//*[@data-source-tag="statement"]')[0],'text','نواں نتیجہ'))
    mutation('structural child tail injection',lambda r,n:setattr(r.xpath('//*[@data-source-tag="statement"]')[0][0],'tail','نواں نتیجہ'))
    mutation('main extra bridge conclusion',lambda r,n:r.find('body/main').append(E.fromstring('<p>نواں نتیجہ</p>')))
    mutation('source term key changed',lambda r,n:r.xpath('//*[@data-source-term]')[0].set('data-source-term','8'))
    mutation('emphasis shape changed',lambda r,n:setattr(r.xpath('//*[@data-source-tag="em"]')[0],'tag','span'))
    mutation('nested footnote omitted',lambda r,n:sn(r,keys[146]).remove(sn(r,keys[146]).xpath('./span[@data-source-tag="fn"]')[0]))
    mutation('mixed child notation order',lambda r,n:sn(r,keys[146]).append(sn(r,keys[146]).xpath('./*[@data-source-tag="notation"]')[0]))
    mutation('source XML ID changed',lambda r,n:r.xpath('//*[@id="def-argument"]')[0].set('id','wrong-definition'))
    mutation('exercise label changed',lambda r,n:r.xpath('//*[@data-anchor-origin="source-label"]')[0].set('id','wrong-exercise'))
    mutation('local source xref swapped',lambda r,n:r.xpath('//*[@data-source-tag="xref" and @href]')[0].set('href','#ch_logic'))
    mutation('pending source xref falsely linked',lambda r,n:r.xpath('//*[@data-reference-status="pending"]')[0].set('href','#ch_logic'))
    mutation('pending source label erased',lambda r,n:setattr(r.xpath('//*[@data-reference-status="pending"]')[0],'text',''))
    mutation('table cell T changed',lambda r,n:setattr(r.xpath('//td//bdi[text()="T"]')[0],'text','F'))
    mutation('table cell order',lambda r,n:r.xpath('//tbody/tr')[0].insert(0,r.xpath('//tbody/tr')[0][-1]))
    mutation('table row order',lambda r,n:r.xpath('//tbody')[0].insert(0,r.xpath('//tbody')[0][-1]))
    mutation('table column source rule changed',lambda r,n:r.xpath('//col')[0].set('data-source-right','medium'))
    mutation('blank negation cell falsely spanning',lambda r,n:r.xpath('//td[not(node())]')[0].set('colspan','2'))
    mutation('source correct flag reversed',lambda r,n:r.xpath('//*[@data-source-tag="choice"]')[0].set('data-source-attributes','{"correct":"no"}'))
    mutation('source displayed correct flag falsified',lambda r,n:setattr(r.xpath('//*[@class="source-choice-flag"]//bdi')[0],'text','no'))
    mutation('match ordering changed',lambda r,n:r.xpath('//*[@data-source-tag="match"]')[0].set('data-source-attributes','{"order":"99"}'))
    mutation('source feedback injected',lambda r,n:r.xpath('//*[@data-source-tag="feedback"]')[0].append(E.fromstring('<p>ہر جواب درست اے</p>')))
    mutation('cache source owner swapped',lambda r,n:r.xpath('//*[@data-cache-record]')[0].set('data-cache-owner',m['cached_static_bindings'][1]['owner']))
    mutation('cache seed changed',lambda r,n:r.xpath('//*[@data-source-tag="static"]')[0].set('data-source-attributes','{"seed":"9"}'))
    mutation('cache return target changed',lambda r,n:r.xpath('//*[@data-cache-return]')[0].set('href','#webwork-owner-2'))
    mutation('cache PG evidence altered',lambda r,n:setattr(r.xpath('//*[@data-cache-metadata]')[3],'text','{}'))
    mutation('local inert PG altered',lambda r,n:setattr(r.xpath('//*[@data-source-inert-pg]')[0],'text','print("wrong")'))
    mutation('source parity answer erased',lambda r,n:setattr(sn(r,keys[505]),'text','سچ نہیں'))
    mutation('visible parity correction erased',lambda r,n:r.xpath('//*[@class="cache-warning"]')[0].getparent().remove(r.xpath('//*[@class="cache-warning"]')[0]))
    mutation('quantifier warning removed',lambda r,n:sn(r,keys[398]).remove(sn(r,keys[398]).xpath('./span[@class="source-warning"]')[0]))
    mutation('original correction overreach',lambda r,n:r.xpath('//*[@id="b10-002-between-qualification"]/div')[0].append(E.fromstring('<p>سارے دو عدد وکھرے ہُندے نیں۔</p>')))
    mutation('source correction relabeled source',lambda r,n:r.xpath('//*[@id="b10-002-missing-predicate"]')[0].set('data-origin','source'))
    mutation('metadata author changed',lambda r,n:r.xpath('//meta[@name="source-author"]')[0].set('content','Unknown'))
    mutation('footer license invented',lambda r,n:setattr(r.find('body/footer')[2],'text','CC0'))
    mutation('shared style source hidden',lambda r,n:setattr(r.find('head/style'),'text',r.find('head/style').text+'\n.source-p{display:none}'))
    mutation('literal math spacing style removed',lambda r,n:setattr(r.find('head/style'),'text',r.find('head/style').text.replace('.b10-002 mtext{white-space:pre}','')))
    mutation('alphabetic cache list style erased',lambda r,n:setattr(r.find('head/style'),'text',r.find('head/style').text.replace('.b10-002 ol[type="a"],.b10-002 ol[type="a"]>li{list-style-type:lower-alpha}','')))
    mutation('source alphabetic list misnumbered decimal',lambda r,n:r.xpath('//ol[@type="a"]')[0].set('type','1'))
    mutation('source prose digit direction reversed',lambda r,n:sn(r,keys[135]).xpath('.//bdi')[0].set('dir','rtl'))
    mutation('table RTL reverses physical data',lambda r,n:r.xpath('//table')[0].set('dir','rtl'))
    math=lambda r:r.findall('.//m:math',NS)[0]
    mutation('math wrapper own text',lambda r,n:setattr(math(r).getparent(),'text','+1'))
    mutation('math wrapper tail text',lambda r,n:setattr(math(r),'tail','-1'))
    mutation('math source annotation edited',lambda r,n:setattr(math(r).find('.//m:annotation',NS),'text','[0,1)'))
    mutation('interval fence changed',lambda r,n:setattr(math(r).find('.//m:mo',NS),'text','('))
    mutation('superscript exponent changed',lambda r,n:setattr(r.find('.//m:msup/m:mn',NS),'text','3'))
    mutation('superscript base changed',lambda r,n:setattr(r.find('.//m:msup/m:mi',NS),'text','x'))
    mutation('whole superscript flattened',lambda r,n:setattr(r.find('.//m:msup',NS),'tag','{'+MATH+'}mrow'))
    mutation('quantifier order marker changed',lambda r,n:setattr(r.xpath('//m:mo[text()="∀"]',namespaces=NS)[0],'text','∃'))
    mutation('conjunction changed to disjunction',lambda r,n:setattr(r.xpath('//m:mo[text()="∧"]',namespaces=NS)[0],'text','∨'))
    mutation('implication reversed',lambda r,n:setattr(r.xpath('//m:mo[text()="→"]',namespaces=NS)[0],'text','←'))
    mutation('source negation erased',lambda r,n:setattr(r.xpath('//m:mo[text()="¬"]',namespaces=NS)[0],'text',''))
    mutation('math variable changed',lambda r,n:setattr(r.xpath('//m:mi[text()="x"]',namespaces=NS)[0],'text','z'))
    mutation('source mtext answer changed',lambda r,n:setattr(r.xpath('//m:mtext[text()="False"]',namespaces=NS)[0],'text','True'))
    mutation('source mtext choice spacing erased',lambda r,n:setattr(r.xpath('//m:mtext[text()="Choice 1"]',namespaces=NS)[0],'text','Choice1'))
    mutation('raw spacing fallback silently simplified',lambda r,n:setattr(r.xpath('//*[@class="tex-unreviewed"]')[0],'text',r'\lt(y,x)'))
    mutation('raw TeX attribute changed',lambda r,n:math(r).getparent().set('data-source-tex','[0,1)'))
    mutation('raw fallback source altered',lambda r,n:setattr(r.xpath('//*[@data-source-tex-fallback]')[0],'text','[0,1)'))
    mutation('inert macros erased',lambda r,n:setattr(r.xpath('//*[@data-source-macros]')[0],'text',''))
    mutation('ledger source token changed',lambda r,n:n['math_conversion']['records'][0]['tokens'][0].update(raw='('))
    mutation('ledger path swapped',lambda r,n:n['math_conversion']['records'][0]['tokens'][0].update(mathml_paths=['/wrong']))
    mutation('ledger source spacing effect changed',lambda r,n:n['math_conversion']['records'][1]['tokens'][2].update(effect='ignored'))
    mutation('notice cache seed changed',lambda r,n:n['cached_static_bindings'][0].update(seed='99'))
    mutation('notice false completion claim',lambda r,n:n.update(scope='Complete Chapter1 and whole book.'))
    mutation('notice reviewed math count overstated',lambda r,n:n['math_conversion'].update(derived_mathml_count=337,source_tex_fallback_count=0))
    mutation('notice source macro silently replaced',lambda r,n:n.update(inert_source_macros=''))
    mutation('OPL notice replaced by book license',lambda r,n:n['selected_component_witnesses']['files'][0].update(verbatim_notice='CC BY-NC-SA 4.0'))
    mutation('original OPL source replaced with Indonesian adapted hash',lambda r,n:n['selected_component_witnesses']['files'][1].update(sha256='9ca20bff298b54c231f3cb4b0aa9a792ef20926aa98f6e2f075556456421dbce'))
    mutation('OPL author header erased',lambda r,n:n['selected_component_witnesses']['files'][1].update(source_header_verbatim=''))
    mutation('selected component cache owner swapped',lambda r,n:n['selected_component_witnesses']['source_cache_associations'][0].update(cache_xml_id='extracted-webwork-2'))
    mutation('witness link points to adapted PG',lambda r,n:r.xpath('//*[@data-component-witness]')[1].set('href','../adapted.pg'))
    mutation('component acquisition receipt omitted',lambda r,n:n['selected_component_witnesses'].update(acquisition_path=''))
    for name,local,alter in [
        ('detached OPL license omitted',WITNESS_DIR+'OPL/OPL_LICENSE',lambda raw:None),
        ('detached OPL author erased',WITNESS_DIR+'OPL/'+OPL_PREFIX+'0_2_1.pg',lambda raw:raw.replace(b'## Author(Oscar Levin)',b'## Author(Unknown)')),
        ('detached PG numeral changed',WITNESS_DIR+'OPL/'+OPL_PREFIX+'0_2_2.pg',lambda raw:raw.replace(b'## Problem1(2)',b'## Problem1(9)')),
        ('detached original witness line endings normalized',WITNESS_DIR+'OPL/OPL_LICENSE',lambda raw:raw.replace(b'\n',b'\r\n')),
        ('detached local PG credit erased',WITNESS_DIR+'dmoi4/source/practice/wwpg/statements-quant1.pg',lambda raw:raw.replace(b'University of Northern Colorado',b'Unknown')),
    ]:
        try:validate_components(root,m,notice,Checks(),{local:alter((BASE/local).read_bytes())})
        except AssertionError as exc:mutations.append({'name':name,'rejected_by':str(exc)})
        else:raise AssertionError('Surviving detached component mutation: '+name)
    unsupported=[r'\frac{1}{2}',r'\input{secret}',r'\unknown',r'x_1',r'x^{2',r'x^',r'(x]',r'[0,1)',r'x^^2',r'\text{Maybe}',r'\text{True }',r'\!x',r'x\!y',r'x^23','',r'\forall{x','x$y',r'\text{Choice {1}}']
    for rawbad in unsupported:
        try:convert(rawbad)
        except TexError:pass
        else:raise AssertionError('Unsupported grammar accepted '+repr(rawbad))
    valid_changes=[(r'\forall x P(x)',r'\exists x P(x)'),(r'P\wedge Q',r'P\vee Q'),(r'x\lt y',r'x\le y'),(r'\forall x\exists y P(x,y)',r'\exists x\forall y P(x,y)'),(r'\forall x\exists y(y^2=x)',r'\forall x\exists y(y^3=x)'),('P(x,y)','P(y,x)'),(r'\neg(P\wedge Q)\imp Q',r'\neg P\wedge Q\imp Q'),(r'\text{False}',r'\text{True}')]
    for original,changed in valid_changes:
        _,result=convert(changed);assert result['tree']!=expected(original),'Changed mathematical source not detected'
    result={'schema':'pnb-source-bound-structural-qa-v1','unit':'B10-002','status':'pass','source_bound_checks':count,'detached_mutations':mutations,'detached_mutation_count':len(mutations),'unsupported_mapper_tests':unsupported,'valid_changed_math_tests':valid_changes,'source_keys':559,'source_nodes':1602,'source_tex_owners':337,'unique_raw_forms':123,'normalized_handwritten_fixtures':len(EXPECTED),'derived_mathml':336,'explicit_raw_fallback':1,'tables':8,'cells':104,'authored_exercises':23,'fixed_cache_records':6,'reader_sha256':file_hash(OUTPUT),'component_notice_sha256':file_hash(NOTICES),'input_sha256':{p.name:file_hash(p) for p in FROZEN},'script_sha256':{f:file_hash(BASE/'scripts'/f) for f in ['prepare_b10_002.py','build_b10_002.py','b10_002_tex.py','b10_002_math_expected.py','qa_b10_002.py']},'source_math_order_policy':'Actual source-tree preorder, including nested notation owners; manifest math numbering groups by translation-own-block. Every owner maps exactly; fallback numbering is ledger order.','limitations':['Shared pinned-input/parsing helpers are reused read-only; this is not an independent implementation of Git or XML.','Handwritten finite mathematical fixtures and independent token/leaf binding are not universal TeX verification. One exact negative-thin-space form remains visibly unreviewed raw TeX.','The reviewed frame seal rejects change but is not linguistic proof; exact frozen target seals do not establish naturalness or educator approval.','Fixed source caches are not newly executed, randomized or exhaustive; retained incorrect source answers require original correction warnings.','Browser, native Punjabi, educator and assistive-technology review remain separate. Only full Section1.1 plus earlier Chapter1 opening; chapter/book/fullassignment incomplete.'],'whole_book_translation_complete':False}
    result['production_canon_receipt']={'path':PRODUCTION_CANON,'sha256':file_hash(BASE/PRODUCTION_CANON)}
    result['selected_component_acquisition']={'path':WITNESS_DIR+'acquisition.json','sha256':file_hash(BASE/(WITNESS_DIR+'acquisition.json')),'exact_witness_files':7,'remote_opl_pg':4,'local_pg':2,'verbatim_opl_notice':1,'scope':'Selected unit witnesses only; existing component policy retained, no new audit/PG execution.'}
    result['script_sha256']['fetch_b10_002_components.py']=file_hash(BASE/'scripts/fetch_b10_002_components.py')
    result['source_witness_boundary']={'authored':m['excerpt_composition'],'cache':m['cache_excerpt_composition'],'first_outside':m['first_outside']}
    RECEIPT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'pass','checks':count,'mutations':len(mutations),'reader_sha256':result['reader_sha256'],'receipt_sha256':file_hash(RECEIPT)}))

if __name__=='__main__':main()
