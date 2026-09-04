"""Source-bound B10-001 QA; handwritten MathML fixtures never call the converter.

All mutations are detached copies or strings. Real source/reader files are not
mutated. The sole output is the deterministic structural QA receipt.
"""
import copy
import ast
import hashlib
import html as H
import json
import re
from pathlib import Path
from lxml import etree as E, html as LH
from prepare_b10_001 import (BASE, ROOT, MANIFEST, TRANSLATION, EXCERPT, NOTICES,
    OUTPUT, XID, key, load_inputs, notice_record, file_hash, digest, jhash)
from b10_001_math_expected import expected, normalized, EXPECTED
from b10_001_tex import convert, TexError

RECEIPT=BASE/'qa/structural-b10-001.json'
MATH='http://www.w3.org/1998/Math/MathML'
NS={'m':MATH}
FOOTER_SEAL='5ed5845099d8c7d16efda0c9403a21656db83eb392c3b58bd5172dabc2431b14'
HEADER_SEAL='7dc55b72cc2f47baebbf80ebb9571b25313c1a36144f860f78eef217b1d6e9b4'


def parse_reader(raw):
    fixed=re.sub(r'<(meta|img|col|input)\b([^<>]*?)(?<!/)>',r'<\1\2/>',raw.replace('<!doctype html>',''))
    return E.fromstring(fixed.encode(),E.XMLParser(resolve_entities=False,no_network=True))


def fragment(raw):return E.fromstring(('<fragment>'+raw+'</fragment>').encode())
def plain(raw):return ''.join(fragment(raw).itertext())
def canonical(node):return E.tostring(node,method='c14n')
def desc(node):return [E.QName(node).localname,dict(node.attrib),node.text,[desc(c) for c in node]]
def strip_tree(node):return [node.tag,dict(node.attrib),node.text,[[strip_tree(c),c.tail] for c in node]]


class Checks:
    def __init__(self):self.count=0
    def ok(self,value,message):
        if not value:raise AssertionError(message)
        self.count+=1


def owner(node):
    return next((p.get('data-source-node') for p in node.iterancestors() if p.get('data-source-node')),None)


def expected_html_tag(e):
    if e.tag in ['m','me','fn','midpoint','ellipsis','h','see','term']:return 'span'
    if e.tag=='alert':return 'strong'
    if e.tag in ['q','em','ol','li','blockquote']:return e.tag
    if e.tag=='title':return 'h1' if e.getparent().tag=='chapter' else 'h2' if e.getparent().tag=='section' else 'h3'
    if e.tag=='xref':return 'a' if e.get('ref')=='sec_intro-structures' else 'span'
    if e.tag in ['idx','setup','latex-image']:return 'details'
    if e.tag=='tabular':return 'table'
    if e.tag=='col':return 'col'
    if e.tag=='row':return 'tr'
    if e.tag=='cell':return 'td'
    if e.tag=='chapter':return 'article'
    if e.tag=='var' and e.getparent().tag=='p':return 'span'
    if e.tag in ['section','subsection','investigation','exercise','aside','example','reading-questions']:return 'section'
    return 'div'


def block_fragment(actual,spec,source,checks):
    slots={s['source_path']:s['token'] for s in spec['slots']}
    inline={s['path']:s for s in spec['inline_markup']}
    term_index={s['path']:i for i,s in enumerate([x for x in spec['inline_markup'] if x['tag']=='term'])}
    def escaped(text):return H.escape(text or '',quote=False)
    def render(node,isroot=False):
        children=list(node);head=node.text or ''
        if isroot and source.tag=='fn':
            mark=children.pop(0)
            checks.ok(mark.tag=='sup' and mark.get('data-origin')=='renderer-ui' and not len(mark),'footnote generated marker exact shape')
            number=list(source.getroottree().getroot().iter('fn')).index(source)+1
            checks.ok(mark.text=='['+str(number)+']' and (mark.tail or '').startswith(' '),'footnote marker number/prefix')
            head+=mark.tail[1:]
        out=escaped(head)
        for child in children:
            path=child.get('data-source-node')
            if path in slots:part=slots[path]
            elif path in inline:
                item=inline[path];tag={'term':'span','alert':'strong'}.get(item['tag'],item['tag'])
                attrs={'data-source-term':str(term_index[path])} if item['tag']=='term' else {'data-source-tag':'alert'} if item['tag']=='alert' else {}
                checks.ok(child.tag==tag,'exact source inline tag')
                if item['tag']=='term':checks.ok(child.get('data-source-term')==attrs['data-source-term'],'exact term local index')
                part='<'+tag+''.join(' '+a+'="'+H.escape(v,quote=True)+'"' for a,v in attrs.items())+'>'+render(child)+'</'+tag+'>'
            else:
                checks.ok(child.tag=='bdi' and dict(child.attrib)=={'dir':'ltr','lang':'en'},'no unowned source prose/wrapper')
                part='<bdi dir="ltr" lang="en">'+render(child)+'</bdi>'
            out+=part+escaped(child.tail)
        return out
    return fragment(render(actual,True))


def validate_structure(root,m,t,source,checks):
    expected_nodes={key(e):e for e in source.iter()};actual_nodes=root.xpath('//*[@data-source-node]')
    checks.ok([x.get('data-source-node') for x in actual_nodes]==list(expected_nodes),'all492 source nodes in exact preorder')
    actual={e.get('data-source-node'):e for e in actual_nodes}
    checks.ok([e.get('data-source-key') for e in root.xpath('//*[@data-source-key]')]==m['expected_source_keys'],'all157 block keys once in order')
    protected=[]
    for path,e in expected_nodes.items():
        n=actual[path]
        checks.ok(n.get('data-source-tag')==e.tag and json.loads(n.get('data-source-attributes'))==dict(e.attrib),'source tag/attributes '+path)
        checks.ok(n.tag==expected_html_tag(e),'source HTML element '+path)
        parent=e.getparent();checks.ok(owner(n)==(key(parent) if parent is not None else None),'exact source ancestry '+path)
        children=[x.get('data-source-node') for x in n.iterdescendants() if x.get('data-source-node') and owner(x)==path]
        checks.ok(children==[key(c) for c in e],'source ordered direct children '+path)
        ident=e.get(XID) or e.get('label')
        checks.ok(n.get('id')==ident,'source ID/label anchor identity '+path)
        if e.get('label'):checks.ok(n.get('data-anchor-origin')=='source-label','label not misrepresented as XML ID')
        checks.ok(not any(k in n.attrib for k in ['hidden','style','aria-hidden','href']) or (e.tag=='xref' and set(n.attrib)&{'href'} and not set(n.attrib)&{'hidden','style','aria-hidden'}),'no hidden/source style/link injection '+path)
        if ident:protected.append(ident)
    checks.ok(len(protected)==19,'12 XML IDs plus7 original label anchors')
    answer_row='sec_intro-structures.ptx#/section/reading-questions[1]/exercise[2]/statement[1]/p[2]'
    checks.ok({key(e.getparent()) for e in source.iter('var') if e.getparent().tag=='p'}=={answer_row},'only one source mathematical answer-row owner')
    source_row=expected_nodes[answer_row]
    checks.ok((source_row.text or '').strip()=='1, 3,' and len(source_row)==3 and all(e.tag=='var' and dict(e.attrib)=={'width':'1'} and not len(e) and e.text is None for e in source_row) and [(e.tail or '').strip() for e in source_row]==[',',',',', ...'],'source-derived pure numeral/answer/ellipsis row shape')
    checks.ok(actual[answer_row].get('dir')=='ltr' and actual[answer_row].get('class')=='source-p source-math-answer-row' and len(root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," source-math-answer-row ")]'))==1,'mathematical answer row LTR isolation class on exact owner only')
    checks.ok(all(n.get('dir') is None for p,n in actual.items() if expected_nodes[p].tag=='p' and p!=answer_row),'surrounding source prose retains inherited RTL')
    for spec in m['source_blocks']:
        normalized_block=block_fragment(actual[spec['key']],spec,expected_nodes[spec['key']],checks)
        checks.ok(strip_tree(normalized_block)==strip_tree(fragment(t['source_blocks'][spec['key']])),'exact translated own block '+spec['key'])
    generated_headings={'investigation':'کھوج لاؤ!','aside':'نالے ایہہ وی…','example':'مثال','reading-questions':'پڑھن بارے سوال'}
    slot_keys=set(m['expected_source_keys'])
    for path,e in expected_nodes.items():
        n=actual[path]
        if path in slot_keys or e.tag in ['term','q','em','alert','m','me']:continue
        if e.tag not in ['midpoint','ellipsis','xref']:
            checks.ok(n.text in [None,''],'no structural own-text injection '+path)
        if e.tag!='xref':checks.ok(all(c.tail in [None,''] for c in n),'no structural tail injection '+path)
        if e.tag in generated_headings:
            h=n[0];checks.ok(h.tag=='h4' and dict(h.attrib)=={'data-origin':'renderer-ui'} and h.text==generated_headings[e.tag] and not len(h),'exact generated source-type heading')
            checks.ok(list(n)[1:]==[actual[key(c)] for c in e],'exact container children after heading')
        elif e.tag=='idx':
            checks.ok(n[0].tag=='summary' and dict(n[0].attrib)=={'data-origin':'renderer-ui'} and n[0].text=='اشاریہ' and not len(n[0]),'index summary exact')
            checks.ok(list(n)[1:]==[actual[key(c)] for c in e],'index full h/see child order')
        elif e.tag=='image':
            ident=e.get(XID) or e.find('latex-image').get('label');spec=next(s for s in m['declared_assets'] if s['id']==ident)
            checks.ok([c.tag for c in n]==['img']+[actual[key(c)].tag for c in e]+['p','p'],'bounded image children')
            img=n[0];alt=plain(t['source_blocks'][key(e.find('shortdescription'))]);descid='original-image-description-'+ident
            checks.ok(dict(img.attrib)=={'data-rendered-source-image':ident,'src':'../'+spec['planned_reader_path'],'width':spec['width'],'height':spec['height'],'alt':alt,'data-source-alt':e.findtext('shortdescription'),'data-alt-origin':'translated-source-shortdescription','aria-describedby':descid},'exact source SVG/alt/dimensions binding')
            checks.ok(list(n)[1:1+len(e)]==[actual[key(c)] for c in e],'source image child order')
            original=n[-2]
            expected_p=fragment('<p id="'+descid+'" data-origin="original-accessibility-description" class="original-image-description"><span data-origin="renderer-ui">مترجم دی اپنی تصویری وضاحت: </span>'+t['original_image_descriptions'][ident]['html']+'</p>')[0]
            checks.ok(strip_tree(original)==strip_tree(expected_p),'original image description visibly labeled and exact')
            hint=fragment('<p data-origin="renderer-ui" class="scroll-hint"><a href="../'+spec['planned_reader_path']+'">اصل تصویر وکھری کھولو</a> · <a href="#original-b10-001-graphs">گراف بارے وکھرا نوٹ</a></p>')[0]
            checks.ok(strip_tree(n[-1])==strip_tree(hint),'exact image fallback/correction links')
        elif e.tag=='latex-image':
            checks.ok(len(n)==2 and n[0].tag=='summary' and ''.join(n[0].itertext())=='اصل تصویری TeX — بغیر چلائے','inert TikZ disclosure shape')
            checks.ok(n[1].tag=='pre' and dict(n[1].attrib)=={'dir':'ltr','data-source-opaque-text':'true'} and len(n[1])==1 and n[1][0].tag=='code' and not n[1][0].attrib and n[1][0].text==e.text and not len(n[1][0]),'exact inert TikZ text')
        elif e.tag=='tabular':
            checks.ok([c.tag for c in n]==['colgroup','tbody'],'valid table wrappers')
            for wrapper in n:checks.ok(dict(wrapper.attrib)=={'data-origin':'renderer-ui-wrapper'} and wrapper.text is None and all(c.tail is None for c in wrapper),'no table wrapper text')
            checks.ok(n.get('dir')=='ltr','table direction')
        elif e.tag=='row':
            checks.ok(n.get('data-source-bottom')==e.get('bottom','') and list(n)==[actual[key(c)] for c in e],'exact row cells/border')
        elif e.tag=='xref':
            ref=e.get('ref');spec=next(x for x in t['reference_labels'].values() if x['source_ref']==ref)
            if ref=='sec_intro-structures':checks.ok(n.get('href')=='#sec_intro-structures','local Section0.2 target')
            else:checks.ok(n.get('href') is None and n.get('data-reference-status')=='pending-untranslated','forward reference visibly pending, no broken local link')
            expected_text=plain(spec['html'])+(' ('+spec['pending_notice']+')' if spec['resolution']!='local' else '')
            checks.ok(''.join(n.itertext())==expected_text,'exact reference label/availability')
            expected_inner=fragment(spec['html']+(' <span class="pending-marker" data-origin="renderer-ui">('+H.escape(spec['pending_notice'])+')</span>' if spec['resolution']!='local' else ''))
            checks.ok(n.text==expected_inner.text and [[strip_tree(c),c.tail] for c in n]==[[strip_tree(c),c.tail] for c in expected_inner],'exact reference inline labels/isolation')
        elif e.tag in ['midpoint','ellipsis']:
            # These nodes have own symbol text; checked below, not as a container.
            pass
        elif e.tag=='var' and e.getparent().tag=='p':
            slot=next(s for s in m['answer_slots'] if s['source_path']==path)
            checks.ok(len(n)==1 and n[0].tag=='input' and dict(n[0].attrib)=={'class':'source-var-input','data-origin':'renderer-ui','type':'text','inputmode':'numeric','dir':'ltr','size':'1','aria-label':'خالی تھاں '+str(slot['index']+1),'data-source-answer-index':str(slot['index'])},'source answer input association')
        elif e.tag=='response':
            expected_response=fragment('<div><label data-origin="renderer-ui">اپنا جواب<textarea aria-label="اپنا جواب" data-origin="renderer-ui"/></label><p data-origin="renderer-ui" class="scroll-hint">ایہہ جواب ایتھے محفوظ یا خودکار جانچ نہیں ہُندا۔</p></div>')[0]
            checks.ok([strip_tree(c) for c in n]==[strip_tree(c) for c in expected_response],'ungraded response UI exact and no answer inserted')
        elif e.tag=='setup':
            checks.ok(len(n)==2+len(e) and n[0].tag=='summary' and n[0].text=='ماخذ دے جواب تے رہنمائی — کھولھن توں پہلاں آپ آزما لو' and not len(n[0]) and dict(n[0].attrib)=={'data-origin':'renderer-ui'},'static source answer disclosure')
            checks.ok(n[1].tag=='p' and n[1].text=='ایہہ ماخذ دیاں شرطاں تے جواب نیں؛ ایتھے خودکار نمبر نہیں لگدے۔' and not len(n[1]) and dict(n[1].attrib)=={'data-origin':'renderer-ui'} and list(n)[2:]==[actual[key(c)] for c in e],'setup warning/vars exact')
        elif e.tag=='condition':
            text='ایس عدد لئی: '+e.get('number') if e.get('number') else 'ہور جواب لئی'
            checks.ok(len(n)==1+len(e) and n[0].tag=='p' and dict(n[0].attrib)=={'data-origin':'renderer-ui'} and ''.join(n[0].itertext())==text and list(n)[1:]==[actual[key(c)] for c in e],'condition value/feedback association')
        else:
            expected_children=[]
            for child in e:
                rendered=actual[key(child)]
                if child.tag=='tabular':
                    wrapper=rendered.getparent()
                    checks.ok(wrapper.tag=='div' and dict(wrapper.attrib)=={'class':'source-table-scroll','data-origin':'renderer-ui-wrapper','tabindex':'0'} and wrapper.text is None and list(wrapper)==[rendered] and rendered.tail is None,'bounded table scroll wrapper')
                    expected_children.append(wrapper)
                else:expected_children.append(rendered)
            checks.ok(list(n)==expected_children,'no unowned structural child '+path)
    for e in source.xpath('.//midpoint|.//ellipsis'):
        n=actual[key(e)];checks.ok(n.text==('·' if e.tag=='midpoint' else '…') and not len(n) and n.get('dir')=='ltr','exact source symbol mapping')
    return actual


def validate_math(root,m,notices,actual,checks):
    records=notices['math_conversion']['records']
    checks.ok(len(root.findall('.//m:math',NS))==len(records)==105,'all105 derived MathML roots')
    checks.ok(len({s['raw_tex'] for s in m['tex_slots']})==78,'78 raw mathematical forms')
    fallback=root.xpath('//*[@id="b10-001-source-math"]')[0]
    panels=fallback.xpath('./details[@data-tex-owner]')
    checks.ok(len(panels)==105,'all105 expandable raw TeX panels')
    checks.ok(dict(fallback.attrib)=={'id':'b10-001-source-math','data-origin':'renderer-ui'} and len(fallback)==108 and fallback.text is None and all(c.tail is None for c in fallback),'exact fallback appendix boundary')
    top=fragment('<h2>اصل فارمولے — <bdi dir="ltr" lang="en">TeX</bdi> متن</h2><p>ایہہ اصل متن جیویں دا تیویں اے۔ اُتّے دکھائے فارمولے ایس دے محدود، بغیر <bdi dir="ltr" lang="en">TeX</bdi> چلائے بنائے گئے <bdi dir="ltr" lang="en">MathML</bdi> روپ نیں۔</p>')
    checks.ok([strip_tree(x) for x in list(fallback)[:2]]==[strip_tree(x) for x in top],'exact original fallback introduction')
    command_symbols={'\\N':('mi','ℕ'),'\\st':('mo',':'),'\\cdot':('mo','⋅'),'\\ge':('mo','≥'),'\\in':('mo','∈'),'\\infty':('mo','∞'),'\\ldots':('mo','…'),'\\lt':('mo','<'),'\\ne':('mo','≠'),'\\to':('mo','→'),'\\{':('mo','{'),'\\}':('mo','}')}
    for number,(s,r,panel) in enumerate(zip(m['tex_slots'],records,panels),1):
        n=actual[s['source_path']];raw=s['raw_tex'];target=expected(raw)
        checks.ok(n.get('data-source-tex')==raw and n.get('data-source-tex-sha256')==digest(raw.encode()) and n.get('dir')=='ltr' and n.get('data-derived-mathml')=='true','exact raw TeX owner/dir')
        checks.ok(n.text is None and len(n)==2 and n[0].tag=='{'+MATH+'}math' and n[1].tag=='a' and all(c.tail is None for c in n),'exact math wrapper children/text')
        math=n[0];display='block' if s['source_tag']=='me' else 'inline'
        checks.ok(dict(math.attrib)=={'dir':'ltr','display':display} and math.text is None and len(math)==1 and math[0].tag=='{'+MATH+'}semantics','math root display/semantics')
        sem=math[0];checks.ok(not sem.attrib and sem.text is None and len(sem)==2,'exact semantics children')
        checks.ok(desc(sem[0])==target,'handwritten expected complete MathML tree '+s['source_path'])
        checks.ok(sem[1].tag=='{'+MATH+'}annotation' and dict(sem[1].attrib)=={'encoding':'application/x-tex'} and sem[1].text==raw and not len(sem[1]),'exact source annotation')
        checks.ok(all(c.tail is None for c in math.iter()),'no MathML hidden/tail text')
        checks.ok(dict(n[1].attrib)=={'class':'tex-link','data-origin':'renderer-ui','href':'#source-tex-'+str(number).zfill(3),'aria-label':'اصل فارمولا ویکھو','lang':'en','dir':'ltr'} and n[1].text=='TeX' and not len(n[1]),'exact fallback link')
        checks.ok(dict(panel.attrib)=={'id':'source-tex-'+str(number).zfill(3),'class':'raw-tex-fallback','data-tex-owner':s['source_path']} and panel.text is None and [x.tag for x in panel]==['summary','p','pre'] and all(c.tail is None for c in panel),'raw TeX disclosure exact owner/shape')
        checks.ok(''.join(panel[0].itertext())=='فارمولا '+str(number)+' — اصل متن کھولو','fallback display label')
        checks.ok(panel[1].text==s['source_path'] and not len(panel[1]),'fallback owner label')
        checks.ok(len(panel[2])==1 and panel[2][0].tag=='code' and dict(panel[2][0].attrib)=={'data-source-tex-fallback':'true'} and panel[2][0].text==raw and not len(panel[2][0]),'exact visible fallback source text')
        expected_panel=fragment('<details id="source-tex-'+str(number).zfill(3)+'" class="raw-tex-fallback" data-tex-owner="'+H.escape(s['source_path'],quote=True)+'"><summary>فارمولا <bdi dir="ltr" lang="en">'+str(number)+'</bdi> — اصل متن کھولو</summary><p class="tex-owner" dir="ltr" lang="en">'+H.escape(s['source_path'])+'</p><pre dir="ltr"><code data-source-tex-fallback="true">'+H.escape(raw,quote=False)+'</code></pre></details>')[0]
        checks.ok(strip_tree(panel)==strip_tree(expected_panel),'exact raw fallback presentation/own text')
        for field,value in [('number',number),('source_path',s['source_path']),('owner_key',s['owner_key']),('token',s['token']),('source_tag',s['source_tag']),('source_attributes',s['source_attributes']),('source_tex',raw),('source_tex_sha256',digest(raw.encode())),('display',display),('tree',target),('tree_sha256',jhash(target))]:checks.ok(r[field]==value,'math record '+field)
        paths={};leaf_paths=[]
        def walk(d,path):
            paths[path]=d
            if not d[3]:leaf_paths.append(path)
            counts={}
            for c in d[3]:counts[c[0]]=counts.get(c[0],0)+1;walk(c,path+'/'+c[0]+'['+str(counts[c[0]])+']')
        walk(target,'/math/semantics/mrow[1]')
        reconstructed='';cursor=0;mapped_leaves=[]
        for tok in r['tokens']:
            checks.ok(tok['start']==cursor and tok['end']==cursor+len(tok['raw']) and raw[tok['start']:tok['end']]==tok['raw'],'complete contiguous source-token coverage')
            cursor=tok['end'];reconstructed+=tok['raw'];v=tok['raw'];bound=tok['mathml_paths']
            kind='space' if v.isspace() else 'command' if v.startswith('\\') else 'number' if v.isdigit() else 'variable' if v.isalpha() else 'syntax'
            checks.ok(tok['kind']==kind,'independent token classification')
            checks.ok(all(p in paths for p in bound) and len(bound)<=1 and bool(tok['effect']),'token tree-path/effect bound')
            if v.isspace() and not bound:checks.ok(tok['kind']=='space' and tok['effect']=='TeX presentation whitespace; raw retained','exact nonprinting source whitespace')
            elif bound:
                path=bound[0];d=paths[path]
                if d[0]=='mtext':
                    checks.ok(d[2]==' and ' and tok['effect'] in ['literal source text','nonprinting text group boundary','literal mtext content including exact spacing'],'exact source text/space token')
                    if not mapped_leaves or mapped_leaves[-1]!=path:mapped_leaves.append(path)
                elif v in ['{','}']:checks.ok(d[0]=='mrow' and tok['effect']=='nonprinting TeX group boundary','group boundary ledger')
                elif v in ['_','^']:checks.ok(d[0] in ['msub','msup','msubsup'] and tok['effect']=='script binding','script operator binding ledger')
                elif v=='\\frac':checks.ok(d[0]=='mfrac','fraction command binding')
                else:
                    typ,text=command_symbols[v] if v in command_symbols else ('mn',v) if v.isdigit() else ('mi',v) if re.fullmatch('[A-Za-z]',v) else ('mo','−' if v=='-' else v)
                    checks.ok((d[0],d[2])==(typ,text),'exact source-token glyph mapping')
                    if v=='\\N':checks.ok(d[1]=={'mathvariant':'normal'} and tok['effect']=='source \\N / mathbb N to U+2115 DOUBLE-STRUCK CAPITAL N for MathML Core','explicit reversible double-struck Unicode mapping')
                    mapped_leaves.append(path)
            else:checks.ok(False,'unbound printing source token')
        checks.ok(reconstructed==raw and cursor==len(raw),'exact raw TeX reverse ledger')
        checks.ok(mapped_leaves==leaf_paths,'source token order bound to every MathML leaf path')
    macro=fallback.xpath('./details[@id="b10-001-source-macros"]')
    checks.ok(len(macro)==1 and macro[0].xpath('./pre/code[@data-source-macros="true"]')[0].text==m['source_macros'],'exact inert custom macro fallback')
    expected_macro=fragment('<details id="b10-001-source-macros"><summary>اصل ماکروز — صرف متن، بغیر چلائے</summary><pre dir="ltr"><code data-source-macros="true">'+H.escape(m['source_macros'],quote=False)+'</code></pre></details>')[0]
    checks.ok(strip_tree(macro[0])==strip_tree(expected_macro),'exact macro disclosure boundary/own text')


def validate_global(root,m,t,source,notices,prepared,checks):
    checks.ok(root.tag=='html' and root.get('lang')=='pnb-Arab-PK' and root.get('dir')=='rtl','reader locale/RTL')
    checks.ok([c.tag for c in root]==['head','body'] and [c.tag for c in root.find('body')]==['header','main','footer'],'exact document/header/main/footer shape')
    checks.ok(dict(root.attrib)=={'lang':'pnb-Arab-PK','dir':'rtl'} and dict(root.find('body').attrib)=={'class':'b10-001'} and root.text is None and root.find('body').text is None and [c.tail for c in root]==['\n',None] and [c.tail for c in root.find('body')]==['\n',None,None],'no document/body own-text or attribute injection')
    checks.ok(digest(canonical(root.find('body/header')))==HEADER_SEAL,'approved complete header/navigation boundary')
    module=ast.parse((BASE/'scripts/build_b10_001.py').read_text(encoding='utf-8'))
    local_css=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='LOCAL_CSS' for x in n.targets))
    checks.ok(len(root.findall('head/style'))==1 and root.find('head/style').text==(BASE/'styles/reader.css').read_text(encoding='utf-8')+local_css,'exact shared/read-only and scoped stylesheet')
    checks.ok('.b10-001 mtext { white-space:pre; }' in root.find('head/style').text,'source mtext spacing has explicit HTML MathML presentation guard')
    checks.ok('.b10-001 .source-math-answer-row { direction:ltr; unicode-bidi:isolate; text-align:left; }' in root.find('head/style').text,'source sequence answer row has explicit isolated LTR layout')
    checks.ok(len(root.findall('.//style'))==1 and not root.findall('.//link') and not root.xpath('//*[@style]') and '@import' not in local_css and not re.search(r'url\s*\(',local_css),'no external or injected style runtime')
    checks.ok(not root.xpath('//script|//iframe|//object|//embed|//*[@hidden]|//*[@aria-hidden]') and not any(k.startswith('on') for e in root.iter() for k in e.attrib),'no executable/hidden source injection')
    for e in root.find('body').iter():
        for value,parent in [(e.text,e),(e.tail,e.getparent())]:
            if re.search('[A-Za-z0-9]',value or ''):
                checks.ok(parent is not None and any(a.get('dir')=='ltr' for a in [parent]+list(parent.iterancestors())),'all visible ASCII isolated LTR')
    ids=root.xpath('//@id');checks.ok(len(ids)==len(set(ids)),'unique reader IDs')
    for a in root.xpath('//a[starts-with(@href,"#")]'):checks.ok(a.get('href')[1:] in ids,'no broken local anchor')
    main=root.find('body/main');checks.ok(len(main)==5 and main[2].get('id')=='ch_intro','exact main source/original boundaries')
    for i,field in [(1,'bridge_before_html'),(3,'bridge_after_html')]:checks.ok(strip_tree(main[i])==strip_tree(fragment(t[field])[0]),'original bridge separate/exact '+field)
    checks.ok(main.text in [None,''] and all(c.tail in [None,''] for c in main),'no unkeyed main text')
    checks.ok(main[0].tag=='p' and dict(main[0].attrib)=={'class':'source-label','data-origin':'renderer-ui'} and main[0].text=='ایتھے باب صفر دے دوویں حصے پورے نیں۔ اگلے باب تے پوری کتاب ہن وی کم وچ نیں۔' and not len(main[0]),'exact source coverage label')
    meta={e.get('name'):e.get('content') for e in root.findall('head/meta') if e.get('name')}
    checks.ok(all(meta.get(k)==v for k,v in {'source-author':'Oscar Levin','source-edition':'Fourth Edition','source-book-id':'dmoi4','source-document-id':'dmoi-4','source-copyright':'2013–2025 Oscar Levin'}.items()),'retained source metadata')
    footer=root.find('body/footer');checks.ok(digest(canonical(footer))==FOOTER_SEAL,'approved complete source credit/scope footer')
    checks.ok(len(root.xpath('//img'))==2,'only two source images')
    for spec,target,raw in prepared:checks.ok(target.read_bytes()==raw and file_hash(target)==spec['sha256'],'unchanged canonical SVG bytes '+spec['id'])
    checks.ok(notices['source_specific_license']=='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International' and notices['source_copyright']=='2013–2025 Oscar Levin','existing active edition credit')
    checks.ok(notices['existing_notice_policy']==m['existing_notice_policy'] and notices['inert_source_macros']==m['source_macros'] and notices['whole_book_translation_complete'] is False,'notice policy/macros/scope')
    for p,field in [(MANIFEST,'manifest_sha256'),(TRANSLATION,'translation_sha256'),(EXCERPT,'excerpt_sha256')]:checks.ok(notices[field]==file_hash(p),'notice input '+field)


def validate(root,m,t,source,notices,prepared):
    checks=Checks();validate_global(root,m,t,source,notices,prepared,checks)
    actual=validate_structure(root,m,t,source,checks);validate_math(root,m,notices,actual,checks)
    return checks.count


def main():
    m,t,source,prepared=load_inputs();raw=OUTPUT.read_text(encoding='utf-8');root=parse_reader(raw);notices=json.loads(NOTICES.read_text(encoding='utf-8'))
    count=validate(root,m,t,source,notices,prepared)
    browser_parse=LH.fromstring(raw)
    expected_paths=[key(e) for e in source.iter()]
    assert [e.get('data-source-node') for e in browser_parse.xpath('//*[@data-source-node]')]==expected_paths,'HTML parser reparented/lost source nodes'
    html_checks=1
    originals={key(e):e for e in source.iter()}
    for e in browser_parse.xpath('//*[@data-source-node]'):
        original=originals[e.get('data-source-node')]
        assert owner(e)==(key(original.getparent()) if original.getparent() is not None else None),'HTML mixed-content ancestry differs'
        html_checks+=1
        if original.tag in ['m','me']:
            assert e.get('data-source-tex')==original.text,'HTML parser changed exact TeX attribute whitespace'
            html_checks+=1
    count+=html_checks
    mutations=[]
    def mutation(name,change):
        copyroot=copy.deepcopy(root);copynotice=copy.deepcopy(notices);change(copyroot,copynotice)
        try:validate(copyroot,m,t,source,copynotice,prepared)
        except (AssertionError,KeyError,IndexError,ValueError,TypeError,E.XMLSyntaxError) as exc:mutations.append({'name':name,'rejected_by':str(exc)})
        else:raise AssertionError('Surviving detached mutation '+name)
    def source_node(r,path):return r.xpath('//*[@data-source-node=$p]',p=path)[0]
    k=m['expected_source_keys']
    mutation('translated numeral',lambda r,n:source_node(r,k[94])[0].__setattr__('text','9'))
    mutation('translated own prose',lambda r,n:source_node(r,k[0]).__setattr__('text','غلط عنوان'))
    mutation('unkeyed source structural injection',lambda r,n:source_node(r,'ch_intro.ptx#/chapter').append(E.fromstring('<p>f(2)=999</p>')))
    mutation('main source/original injection',lambda r,n:r.find('body/main').append(E.fromstring('<p>نواں نتیجہ</p>')))
    mutation('missing source node',lambda r,n:source_node(r,k[46]).getparent().remove(source_node(r,k[46])))
    mutation('original ID changed',lambda r,n:source_node(r,'sec_intro-intro.ptx#/section').set('id','wrong-section'))
    mutation('label owner false XML identity',lambda r,n:source_node(r,'sec_intro-structures.ptx#/section/subsection[6]/image[2]/latex-image[1]').set('data-anchor-origin','source-xml-id'))
    mutation('table row order',lambda r,n:r.xpath('//tbody')[0].insert(0,r.xpath('//tbody/tr')[1]))
    mutation('source term index',lambda r,n:r.xpath('//*[@data-source-term]')[0].set('data-source-term','999'))
    mutation('inline child ownership',lambda r,n:r.xpath('//*[@data-source-term]')[0].set('data-source-node','fabricated'))
    mutation('nested emphasis removed',lambda r,n:r.xpath('//*[@data-source-tag="em"]')[0].__setattr__('tag','span'))
    mutation('footnote text erased',lambda r,n:r.xpath('//*[@data-source-tag="fn"]')[0][0].__setattr__('tail',' '))
    mutation('local link target',lambda r,n:r.xpath('//*[@data-source-tag="xref" and @href]')[0].set('href','#ch_intro'))
    mutation('forward link falsely available',lambda r,n:r.xpath('//*[@data-source-tag="xref" and not(@href)]')[0].set('href','#ch_sequences'))
    mutation('reference numeral isolation changed',lambda r,n:r.xpath('//*[@data-source-tag="xref"]//bdi')[0].set('dir','rtl'))
    mutation('answer index swap',lambda r,n:r.xpath('//input')[0].set('data-source-answer-index','1'))
    mutation('mathematical answer row reversed to RTL',lambda r,n:r.xpath('//*[@class="source-p source-math-answer-row"]')[0].set('dir','rtl'))
    mutation('surrounding source question incorrectly LTR',lambda r,n:r.xpath('//*[@class="source-p source-math-answer-row"]')[0].getprevious().set('dir','ltr'))
    mutation('feedback replaced',lambda r,n:source_node(r,k[151]).__setattr__('text','درست'))
    mutation('source condition number',lambda r,n:r.xpath('//*[@data-source-tag="condition"]')[0].set('data-source-attributes','{"number":"7"}'))
    mutation('source image swap',lambda r,n:r.xpath('//img')[0].set('src',r.xpath('//img')[1].get('src')))
    mutation('source alt erased',lambda r,n:r.xpath('//img')[0].set('data-source-alt',''))
    mutation('unlabeled original image text',lambda r,n:r.xpath('//*[@class="original-image-description"]')[0].remove(r.xpath('//*[@class="original-image-description"]')[0][0]))
    mutation('TikZ text edited',lambda r,n:r.xpath('//*[@data-source-opaque-text]/code')[0].__setattr__('text','\\draw fake;'))
    mutation('source metadata credit',lambda r,n:r.xpath('//meta[@name="source-author"]')[0].set('content','Unknown'))
    mutation('footer rights text',lambda r,n:r.find('body/footer')[2].__setattr__('text','CC0'))
    mutation('source correction erased',lambda r,n:r.xpath('//*[@id="original-b10-001-function"]')[0].__setattr__('text',''))
    mutation('stylesheet hides source',lambda r,n:r.find('head/style').__setattr__('text',r.find('head/style').text+'\n.source-p {display:none;}'))
    mutation('source mtext visible spacing rule erased',lambda r,n:r.find('head/style').__setattr__('text',r.find('head/style').text.replace('.b10-001 mtext { white-space:pre; }','')))
    mutation('unkeyed header claim',lambda r,n:r.find('body/header').append(E.fromstring('<p>نواں نتیجہ</p>')))
    mutation('body own-text injection',lambda r,n:r.find('body').__setattr__('text','نواں نتیجہ'))
    mutation('secondary stylesheet injection',lambda r,n:r.find('head').append(E.fromstring('<style>.source-p {display:none;}</style>')))
    mutation('inline style injection',lambda r,n:r.find('body/main').set('style','display:none'))
    mutation('unowned fallback prose injection',lambda r,n:r.xpath('//*[@id="b10-001-source-math"]')[0].append(E.fromstring('<p>extra claim</p>')))
    mutation('macro disclosure unkeyed claim',lambda r,n:r.xpath('//*[@id="b10-001-source-macros"]')[0].append(E.fromstring('<p>نواں نتیجہ</p>')))
    mutation('raw fallback misleading summary',lambda r,n:r.xpath('//*[@data-tex-owner]')[0][0].set('aria-label','بدلیا فارمولا'))
    mathnode=lambda r:r.findall('.//m:math',NS)[0]
    mutation('interval opening fence',lambda r,n:mathnode(r).find('.//m:mo',NS).__setattr__('text','('))
    mutation('math root RTL',lambda r,n:mathnode(r).set('dir','rtl'))
    mutation('math annotation source whitespace',lambda r,n:mathnode(r).find('.//m:annotation',NS).__setattr__('text',' '+mathnode(r).find('.//m:annotation',NS).text))
    mutation('math wrapper hidden text',lambda r,n:mathnode(r).getparent().__setattr__('text',' +1'))
    mutation('math wrapper tail text',lambda r,n:mathnode(r).__setattr__('tail',' -1'))
    mutation('raw data-source-tex changed',lambda r,n:mathnode(r).getparent().set('data-source-tex','[0,1)'))
    mutation('math owner swapped',lambda r,n:mathnode(r).getparent().set('data-source-node',m['tex_slots'][1]['source_path']))
    mutation('source minus changed to plus',lambda r,n:r.xpath('//m:mo[text()="−"]',namespaces=NS)[0].__setattr__('text','+'))
    def plain_n_disguised(r,n):
        item=r.xpath('//m:mi[text()="ℕ"]',namespaces=NS)[0]
        item.text='N';item.set('mathvariant','double-struck')
    mutation('plain N disguised by unsupported double-struck variant',plain_n_disguised)
    mutation('subscript variable changed',lambda r,n:r.find('.//m:msub/m:mi',NS).__setattr__('text','z'))
    mutation('fraction denominator changed',lambda r,n:r.find('.//m:mfrac/m:mrow[2]/m:mn',NS).__setattr__('text','3'))
    mutation('English text spacing erased',lambda r,n:r.find('.//m:mtext',NS).__setattr__('text','and'))
    mutation('script grouping flattened',lambda r,n:r.find('.//m:msub',NS).__setattr__('tag','{'+MATH+'}mrow'))
    def wrong_whole_base(r,n):
        item=r.xpath('//m:msub[m:*[1][self::m:mrow]]',namespaces=NS)[0]
        item.replace(item[0],copy.deepcopy(item[0][-1]))
    mutation('whole sequence base attached only to closing fence',wrong_whole_base)
    mutation('raw TeX fallback edited',lambda r,n:r.xpath('//*[@data-source-tex-fallback]')[0].__setattr__('text','[0,1)'))
    mutation('custom macro source erased',lambda r,n:r.xpath('//*[@data-source-macros]')[0].__setattr__('text',''))
    mutation('reverse token ledger altered',lambda r,n:n['math_conversion']['records'][0]['tokens'][0].update(raw='('))
    mutation('ledger tree path changed',lambda r,n:n['math_conversion']['records'][0]['tokens'][0].update(mathml_paths=['/wrong']))
    mutation('ledger hidden spacing altered',lambda r,n:next(x for x in n['math_conversion']['records'][1]['tokens'] if x['kind']=='space').update(raw='  '))
    rejected=[]
    for bad in [r'\sqrt{x}',r'\input{file}',r'\write18{bad}',r'\unknown',r'f_{n-1',r'(a_n)_{n\ge0',r'\frac{n}{2',r'\text{and}',r'\text{ dan }','x_10','x^^2','x/2','',r'[0,\infty]']:
        try:convert(bad)
        except TexError:rejected.append(bad)
        else:raise AssertionError('Unsupported syntax accepted: '+bad)
    valid_but_wrong=[('f_n','f_{n-1}'),('f_4=3','f_3=3'),('f(n)=2\\cdot f(n-1)','f(n)=2\\cdot f(n+1)'),('(a_n)_{n\\ge0}','a_n'),('a_n=\\frac{n(n+1)}{2}','a_n=\\frac{n(n+1)}{3}'),('[0,\\infty)','(0,\\infty)'),('3^2+4^2=5^2','3^2+4^2=6^2')]
    for original,bad in valid_but_wrong:
        # f_n is not a standalone owner; its expected source AST is explicit here.
        target=expected(original) if original!='f_n' else ['mrow',{},None,[['msub',{},None,[['mi',{},'f',[]],['mi',{},'n',[]]]]]]
        assert convert(bad)[1]['tree']!=target,'Plausible wrong mathematical tree accepted'
    assert notices==notice_record(m,prepared),'Derived component record is stale after independent checks'
    result={'schema':'pnb-source-bound-qa-v1','unit':'B10-001','passed':True,'checks':count,'detached_reader_mutations':len(mutations),'mutations':mutations,
        'parser_unknown_syntax_rejections':rejected,'parser_valid_but_wrong_tree_mutations':len(valid_but_wrong),
        'coverage':{'source_keys':157,'source_nodes':492,'xml_ids':12,'source_labels':7,'derived_mathml_owners':105,'unique_raw_tex_forms':78,'handwritten_normalized_tree_fixtures':len(EXPECTED),'source_images':2,'source_exercises':6},
        'artifacts':{p.relative_to(BASE).as_posix():file_hash(p) for p in [MANIFEST,TRANSLATION,EXCERPT,OUTPUT,NOTICES,BASE/'styles/reader.css',BASE/'scripts/prepare_b10_frontmatter.py',BASE/'scripts/prepare_b10_001.py',BASE/'scripts/build_b10_001.py',BASE/'scripts/b10_001_tex.py',BASE/'scripts/b10_001_math_expected.py',Path(__file__)]},
        'limits':['Handwritten expected descriptors are independent of converter output; normalized whitespace keys cover78 raw strings, all exact raw bytes checked separately.','Strict parser covers only the observed grammar; not universal LaTeX support. No upstream code/TeX/TikZ/network runtime executed.','Source-owned prose is checked exactly against frozen reviewed translation, not automatically proven linguistically correct.','Response fields are unsaved scratch space; source feedback is static, not automated grading.','Parent browser/critical math review and native/educator/assistive-technology review remain separate.','Existing notices retained; no new rights or image-clearance audit. Whole books remain incomplete.']}
    RECEIPT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'unit':'B10-001','passed':True,'checks':count,'detached_reader_mutations':len(mutations),'unsupported_parser_inputs':len(rejected),'valid_wrong_tree_mutations':len(valid_but_wrong),'reader_sha256':file_hash(OUTPUT),'notice_sha256':file_hash(NOTICES),'qa_sha256':file_hash(RECEIPT)}))


if __name__=='__main__':main()
