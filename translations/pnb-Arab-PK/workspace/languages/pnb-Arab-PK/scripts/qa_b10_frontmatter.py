"""Independent source-bound DOM QA for B10-frontmatter; detached mutations only."""
from pathlib import Path
import copy
import hashlib
import json
import re
from lxml import etree as E
from PIL import Image
from prepare_b10_frontmatter import (BASE, ROOT, MANIFEST, TRANSLATION, EXCERPT, NOTICES,
    XID, XI, load_inputs, notice_record, source_path, file_hash, tree, digest)

OUTPUT = BASE/'reader/b10-frontmatter.html'
RECEIPT = BASE/'qa/structural-b10-frontmatter.json'
FOOTER_SHA = '0f0f07cf561efce55f6ec5bd2184cae99af1476835cc88ee20d2af69e05420a8'
HEADER_SHA = '573956d3812711b49b09dff15ea645d9cd6976c96d12c1d58518522a0d6c2fa4'
STYLE_SHA = 'de13362968ddeea2e969832a90e3b8e8e68c6d38907f7399cd4675886aacee31'
SOURCE_LABEL = 'ایتھے اصل کتاب دی مُڈھلی معلومات تے دو پورے دیباچے نیں؛ ایہہ پوری کتاب یا باب صفر دا ترجمہ نہیں۔'
STATUS = 'ابتدائی ترجمہ · پنجابی دے ماہر تے ریاضی دے استاد دی جانچ ہن تک نہیں ہوئی۔'
PENDING = 'باب صفر تے باقی پنجاں کتاباں دا پورا کم ہن وی جاری اے۔'
HEADINGS = {'docinfo':'کتاب بارے اصل معلومات','titlepage':'سرورق دی لکھت','colophon':'اشاعت تے لائسنس','dedication':'نذر','acknowledgement':'شکریہ'}
META_LABELS = {'macros':'اصل ریاضی دے ماکروز — صرف متن، بغیر چلائے','latex-image-preamble':'اصل تصویری تیاری دا متن — بغیر چلائے'}


def jhash(obj):
    return digest(json.dumps(obj,ensure_ascii=False,separators=(',',':')).encode())


def parse_html(text):
    # XML inspection avoids silently repairing invalid p/ul or other source hierarchy.
    return E.fromstring(re.sub(r'<(meta|img|br)\b([^<>]*?)(?<!/)>',r'<\1\2/>',text.replace('<!doctype html>','')).encode())


def fragment(text):
    return E.fromstring(('<fragment>'+text+'</fragment>').encode())


def text(node):
    return ''.join(node.itertext())


def key(file,node):
    return file+'#'+source_path(node)


def expected_source(roots):
    dmoi=roots['dmoi.ptx'];book=dmoi.find('book')
    return [(key('dmoi.ptx',dmoi),dmoi)]+[(key('bookinfo.ptx',n),n) for n in roots['bookinfo.ptx'].iter()]+[(key('dmoi.ptx',book),book)]+[(key('dmoi.ptx',book.find(t)),book.find(t)) for t in ('title','subtitle')]+[(key('frontmatter.ptx',n),n) for n in roots['frontmatter.ptx'].iter()]


def source_display(e):
    if e.tag=='url' and not text(e).strip():
        return e.get('visual',e.get('href',''))
    if e.tag=='ndash':
        return '–'
    if e.tag=='pretext':
        return 'PreTeXt'
    return (e.text or '')+''.join(('{{child:0}}' if c.tag=='ul' else source_display(c))+(c.tail or '') for c in e)


def source_parent(k,e):
    file=k.split('#')[0]
    if file=='bookinfo.ptx' and e.getparent() is None:
        return 'dmoi.ptx#/pretext'
    if file=='frontmatter.ptx' and e.getparent() is None:
        return 'dmoi.ptx#/pretext/book[1]'
    return key(file,e.getparent()) if e.getparent() is not None else None


def normalized_block(element):
    n=copy.deepcopy(element)
    for child in list(n):
        if child.get('data-source-tag')=='ul':
            i=n.index(child);s='{{child:0}}'+(child.tail or '')
            if i:
                n[i-1].tail=(n[i-1].tail or '')+s
            else:
                n.text=(n.text or '')+s
            n.remove(child)
    for el in n.iter():
        el.attrib.pop('data-source-node',None)
        el.attrib.pop('data-source-attributes',None)
        if el.tag in ('q','em','a'):
            el.attrib.pop('data-source-tag',None)
    n.tag='fragment';n.attrib.clear();n.tail=None
    return n


def html_tag(k,e,t):
    tag=e.tag
    if tag==XI:
        return 'p'
    if k=='dmoi.ptx#/pretext':
        return 'article'
    if tag in ('q','em'):
        return tag
    if tag=='pretext':
        return 'bdi'
    if tag=='ndash':
        return 'span'
    if tag=='url':
        return 'a'
    if tag in ('brandlogo','image','author','website','copyright','attribution','sidebyside'):
        return 'div'
    if tag in ('macros','latex-image-preamble'):
        return 'details'
    if tag in ('document-id','cross-references'):
        return 'p'
    if tag=='blurb':
        return 'section'
    if k in t['source_blocks']:
        if tag=='title':
            return 'h1' if k.startswith('dmoi.ptx') else 'h3' if e.getparent().tag=='paragraphs' else 'h2'
        return 'div' if e.find('ul') is not None else 'p'
    return tag if tag in ('ul','li') else 'section'


def expected_attributes(k,e,t,m):
    tag='include' if e.tag==XI else e.tag
    a={'data-source-node':k,'data-source-tag':tag,'data-source-attributes':json.dumps(dict(e.attrib),ensure_ascii=False,sort_keys=True,separators=(',',':'))}
    if e.get(XID):
        a['id']=e.get(XID)
    if k=='dmoi.ptx#/pretext':
        a['id']='b10-frontmatter-source'
    elif e.tag in ('q','em','ndash'):
        pass
    elif e.tag=='pretext':
        a.update(dir='ltr',lang='en')
    elif e.tag=='url':
        u=next(v for v in m['original_urls'] if v['source_key']==k)
        a.update(href=e.get('href'))
        a['data-source-url']=u['source_url_id']
    elif e.tag=='brandlogo':
        a['class']='source-brandlogo'
    elif e.tag=='image':
        a['class']='source-image'
    elif e.tag in ('document-id','cross-references',XI):
        a['class']='source-raw-setting'
        if e.tag=='document-id':
            a.update(dir='ltr',lang='en')
    elif e.tag in ('macros','latex-image-preamble'):
        pass
    elif e.tag=='blurb':
        a['class']='source-blurb'
    elif k in t['source_blocks']:
        a['data-source-key']=k
        a['class']='source-mixed-para' if e.find('ul') is not None else 'source-'+e.tag
    else:
        a['class']='source-'+e.tag
    return a


def validate(root,m,t,roots,notice,prepared,asset_overrides=None):
    checks=[]
    def ok(value,label):
        if not value:
            raise AssertionError(label)
        checks.append(label)
    ok(root.tag=='html' and root.attrib=={'lang':'pnb-Arab-PK','dir':'rtl'},'target locale/RTL')
    ok([n.tag for n in root]==['head','body'],'exact page skeleton')
    ok(root.text is None and [n.tail for n in root]==['\n',None],'root text/tails')
    body=root.find('body');main=body.find('main');article=main.find('article')
    ok(body.attrib=={'class':'b10-frontmatter'} and [n.tag for n in body]==['header','main','footer'],'body skeleton')
    ok(body.text is None and [n.tail for n in body]==['\n',None,None],'body own text/tails')
    ok(jhash(tree(body.find('header')))==HEADER_SHA,'reviewed complete header/status/navigation')
    head=root.find('head')
    ok([n.tag for n in head]==['meta']*9+['title','style'],'head has no extra resource or runtime')
    ok(head.text is None and all(n.tail is None for n in head),'head own text/tails')
    ok([dict(n.attrib) for n in head[:3]]==[{'charset':'utf-8'},{'name':'viewport','content':'width=device-width, initial-scale=1'},{'name':'description','content':'Complete canonical fourth-edition B10 frontmatter in Punjabi; not a complete textbook'}],'charset viewport bounded description')
    ok(all(n.text is None and not list(n) for n in head[:9]) and not head[-1].attrib and not head[-2].attrib,'head leaf shapes')
    ok([n.get('id') or n.get('class') for n in main]==['source-label','b10-frontmatter-source-context','b10-frontmatter-source','b10-frontmatter-bridge','status'],'exact main siblings')
    ok(main.text is None and all(n.tail is None for n in main),'main own text/tails')
    ok(text(main[0])==SOURCE_LABEL and main[0].attrib=={'class':'source-label','data-origin':'renderer-ui'},'exact source label')
    ok(text(main[-1])==PENDING and main[-1].attrib=={'class':'status','data-origin':'renderer-ui'},'exact pending statement')
    for i,field in [(1,'bridge_before_html'),(3,'bridge_after_html')]:
        ok(tree(main[i])==tree(E.fromstring(t[field].encode())),'original bridge exact/separate '+field)
    ids=[n.get('id') for n in root.iter() if n.get('id')]
    ok(len(ids)==len(set(ids)),'unique IDs')
    expected_ids=['dmoi4','frontmatter','preface','pref_editions']
    ok([i for i in ids if i in expected_ids]==expected_ids,'four original ID order')
    sources=expected_source(roots);source_map=dict(sources)
    source_nodes=article.xpath('.//*[@data-source-node]')
    source_nodes=[article]+source_nodes
    ok([n.get('data-source-node') for n in source_nodes]==[k for k,e in sources],'all 101 source nodes in exact order')
    ok(len(source_nodes)==101,'101 original elements')
    bynode={n.get('data-source-node'):n for n in source_nodes}
    for k,e in sources:
        n=bynode[k]
        ok(n.tag==html_tag(k,e,t),'source HTML element '+k)
        ok(n.attrib==expected_attributes(k,e,t,m),'all source attributes '+k)
        ancestor=next((a.get('data-source-node') for a in n.iterancestors() if a.get('data-source-node')),None)
        ok(ancestor==source_parent(k,e),'nearest source parent '+k)
    blocks=root.xpath('//*[@data-source-key]')
    ok([n.get('data-source-key') for n in blocks]==m['source_keys']==list(t['source_blocks']),'50 exact translation keys/order')
    for n in blocks:
        k=n.get('data-source-key');expected=fragment(t['source_blocks'][k])
        ok(tree(normalized_block(n))==tree(expected),'exact translated own block '+k)
        file,xp=k.split('#')
        attr='/@' in xp;e=roots[file].xpath(xp.rsplit('/@',1)[0] if attr else xp)[0]
        s=e.get(xp.rsplit('/@',1)[1]) if attr else source_display(e)
        strip=lambda value:re.sub(r'\{\{child:\d+\}\}','',value)
        plain=text(normalized_block(n))
        ok(re.findall('[0-9]+',strip(s))==re.findall('[0-9]+',strip(plain)),'source digits '+k)
        for sub in normalized_block(n).iter():
            for val,ancestors in [(sub.text,[sub]+list(sub.iterancestors())),(sub.tail,list(sub.iterancestors()))]:
                if val and re.search('[A-Za-z0-9]',strip(val)):
                    ok(any(a.tag=='bdi' and a.get('dir')=='ltr' for a in ancestors),'source Latin/digit isolation '+k)
    # Exact direct children/own slots prevent unkeyed content injected between source blocks.
    for k,e in sources:
        n=bynode[k]
        if (k in t['source_blocks'] and e.tag!='blurb') or e.tag in ('q','em','url','ndash','pretext') and k!='dmoi.ptx#/pretext':
            continue
        if e.tag in ('brandlogo','image'):
            continue
        ok(n.text is None and all(c.tail is None for c in n) if e.tag!='document-id' else n.text==e.text and not list(n),'container own text/tails '+k)
        if e.tag=='document-id':
            continue
        def descriptor(c):
            if c.get('data-source-node'):
                return ('source',c.get('data-source-node'))
            if c.get('data-source-key'):
                return ('block',c.get('data-source-key'))
            if c.get('data-origin')=='renderer-ui':
                return ('ui',c.tag,text(c),tuple(sorted(c.attrib.items())))
            if c.get('data-source-text-slot'):
                return ('raw',c.get('data-source-text-slot'),c.text,tuple(sorted(c.attrib.items())))
            return ('unexpected',c.tag,dict(c.attrib),text(c))
        ui=lambda tag,txt,attrs=None:('ui',tag,txt,tuple(sorted((attrs or {'data-origin':'renderer-ui'}).items())))
        if k=='dmoi.ptx#/pretext':
            exp=[('source','bookinfo.ptx#/docinfo'),('source','dmoi.ptx#/pretext/book[1]')]
        elif k=='dmoi.ptx#/pretext/book[1]':
            exp=[('source',key('dmoi.ptx',e.find(tag))) for tag in ('title','subtitle')]+[('source','frontmatter.ptx#/frontmatter')]
        elif e.tag=='blurb':
            exp=[('block',k+'/@shelf'),('block',k)]
            ok(n[0].attrib=={'class':'source-attribute','data-source-key':k+'/@shelf','data-source-attribute':'shelf'} and n[1].attrib=={'data-source-key':k},'blurb wrappers exact')
        elif e.tag in META_LABELS:
            exp=[ui('summary',META_LABELS[e.tag]),('raw','own',e.text or '',(('data-source-text-slot','own'),('dir','ltr')))]
            for c in e:
                exp += [('source',key(k.split('#')[0],c)),('raw','tail',c.tail or '',(('data-source-text-slot','tail'),('dir','ltr')))]
        elif e.tag==XI:
            exp=[ui('bdi',e.get('href')+' (parse='+e.get('parse')+')',{'dir':'ltr','lang':'en','data-origin':'renderer-ui'})]
        elif e.tag=='cross-references':
            exp=[ui('bdi','cross-references: '+e.get('text'),{'dir':'ltr','lang':'en','data-origin':'renderer-ui'})]
        else:
            label=HEADINGS.get(e.tag)
            if e.tag=='preface' and e.find('title') is None:
                label='دیباچہ'
            exp=([ui('h2',label)] if label else [])+[('source',key(k.split('#')[0],c)) for c in e]
        ok([descriptor(c) for c in n]==exp,'exact structural children/UI/raw slots '+k)
    # Raw metadata is source data, not active math or code.
    ok(len(article.xpath('.//details'))==2 and len(article.xpath('.//pre'))==3,'inert metadata containers')
    ok(not root.xpath('//script|//iframe|//object|//embed|//math|//table|//figure|//figcaption|//br'),'no inferred math/table/figure/newline/runtime')
    ok(not article.xpath('.//p//ul|.//p//div|.//p//p'),'valid mixed-content paragraph container')
    for n in root.iter():
        ok(not any(a.lower().startswith('on') for a in n.attrib),'no event handler')
    for u in m['original_urls']:
        n=bynode[u['source_key']]
        ok(n.get('href')==u['attributes']['href'] and n.get('data-source-url')==u['source_url_id'],'exact source link '+u['source_url_id'])
        if not u['text']:
            ok(text(n)==u['attributes']['visual'],'source visible URL '+u['source_url_id'])
    ok(len(article.xpath('.//*[@data-source-url]'))==4,'four URL nodes separate from brandlogo')
    for spec,target,data in prepared:
        ident=spec['id'];n=bynode[spec['source_key']];imgs=n.xpath('.//img')
        ok(len(imgs)==1,'single original image '+ident);im=imgs[0];url='../'+spec['planned_reader_path']
        expected={'src':url,'alt':t['original_image_alt_overrides'][ident],'width':str(spec['width']),'height':str(spec['height']),'data-alt-origin':'original-accessibility-description'}
        if ident=='qrcode':
            expected.update({'data-source-alt':spec['source_alt'],'data-translated-source-alt':text(fragment(t['source_blocks'][m['source_keys'][-1]])),'data-source-alt-owner':'sidebyside','aria-describedby':'b10-frontmatter-qr-note'})
        else:
            expected['data-source-alt-present']='false'
        ok(im.attrib==expected and im.text is None and not list(im),'exact image alt/identity attributes '+ident)
        raw=(asset_overrides or {}).get(ident,target.read_bytes())
        ok(digest(raw)==spec['sha256'] and len(raw)==spec['bytes'],'actual PNG bytes '+ident)
        with Image.open(target) as image:
            ok(image.size==(spec['width'],spec['height']),'actual PNG dimensions '+ident)
        ok(n.text is None and all(c.tail is None for c in n),'image wrapper own text/tails '+ident)
        ok([c.tag for c in n]==(['a','p'] if ident=='cover4' else ['img','p']),'image wrapper children '+ident)
        if ident=='cover4':
            ok(n[0].attrib=={'data-source-brandlogo-url':'true','href':spec['source_attributes']['url']} and list(n[0])==imgs and n[0].text is None and imgs[0].tail is None,'exact source logo link')
        hint=n[-1]
        ok(hint.attrib=={'class':'scroll-hint','data-origin':'renderer-ui'} and hint.text is None,'image hint wrapper '+ident)
        expected_hrefs=[url]+(['#b10-frontmatter-qr-note'] if ident=='qrcode' else [])
        ok([c.tag for c in hint]==['a']*len(expected_hrefs) and [c.get('href') for c in hint]==expected_hrefs,'image hint links '+ident)
        ok([text(c) for c in hint]==['اصل تصویر وکھری کھولو']+(['تصویری وضاحت دا وکھرا نوٹ'] if ident=='qrcode' else []),'image hint labels '+ident)
        ok([c.tail for c in hint]==([' · ',None] if ident=='qrcode' else [None]),'image hint tails '+ident)
    ok(jhash(tree(root.find('body/footer')))==FOOTER_SHA,'reviewed full credit/footer contract')
    ok(digest(root.find('head/style').text.encode())==STYLE_SHA,'reviewed source/local CSS including unmirrored images')
    metadata={n.get('name'):n.get('content') for n in root.findall('head/meta') if n.get('name','').startswith('source-')}
    ok(metadata=={'source-book-id':'dmoi4','source-document-id':'dmoi-4','source-author':'Oscar Levin','source-edition':'Fourth Edition','source-date':'Fall 2024','source-copyright':'2013–2025 Oscar Levin'},'head source metadata exact')
    ok(text(root.find('head/title'))==t['title']+' — B10 front matter','page title')
    ok(text(body.find('header/p[@class="status"]'))==STATUS,'status not inflated')
    ok(not root.xpath('//img[starts-with(@src,"http")]'),'no remote image substitution')
    for a in root.iter('a'):
        href=a.get('href','')
        if href.startswith('#'):
            ok(href[1:] in ids,'live local anchor '+href)
        elif href and not re.match(r'[A-Za-z][A-Za-z0-9+.-]*:',href):
            ok((OUTPUT.parent/href.split('#')[0]).resolve().is_file(),'local file link '+href)
    ok(notice==notice_record(m,prepared),'deterministic exact component notice')
    ok(notice['source_specific_license']=='Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International' and notice['source_copyright']=='2013–2025 Oscar Levin','retained active edition notice')
    ok(notice['whole_book_translation_complete'] is False and 'not canonical' in notice['comparison_additions'],'coverage/comparison limits')
    return checks


def run():
    m,t,source,roots,prepared=load_inputs()
    notice=json.loads(NOTICES.read_text(encoding='utf-8'))
    root=parse_html(OUTPUT.read_text(encoding='utf-8'))
    checks=validate(root,m,t,roots,notice,prepared)
    mutations=[]
    def trial(name,change):
        r=copy.deepcopy(root);n=copy.deepcopy(notice);assets={}
        change(r,n,assets)
        try:
            validate(r,m,t,roots,n,prepared,assets)
        except AssertionError as err:
            mutations.append({'mutation':name,'rejected_by':str(err)})
            return
        raise AssertionError('Mutation not rejected: '+name)
    def src(r,k):
        return r.xpath('//*[@data-source-node=$key]',key=k)[0]
    def block(r,k):
        return r.xpath('//*[@data-source-key=$key]',key=k)[0]
    p=m['source_keys'][20];numeral=m['source_keys'][26];mixed=m['source_keys'][25]
    trial('drop complete source paragraph',lambda r,n,a:src(r,p).getparent().remove(src(r,p)))
    trial('inject unkeyed source paragraph',lambda r,n,a:src(r,'frontmatter.ptx#/frontmatter/preface[1]').append(E.fromstring('<p>All answers are guaranteed; 999.</p>')))
    trial('alter translated own paragraph text',lambda r,n,a:setattr(block(r,p),'text','بدلّی ہوئی عبارت'))
    trial('750 changed to 751',lambda r,n,a:setattr(block(r,numeral).xpath('.//bdi')[1],'text','751'))
    trial('remove copyright dash',lambda r,n,a:setattr(src(r,'frontmatter.ptx#/frontmatter/colophon[1]/copyright[1]/year[1]/ndash[1]'),'text','-'))
    trial('source ID altered',lambda r,n,a:src(r,'frontmatter.ptx#/frontmatter/preface[1]').set('id','preface-wrong'))
    trial('source list child order reversed',lambda r,n,a:src(r,mixed+'/ul[1]').insert(0,src(r,mixed+'/ul[1]')[-1]))
    trial('mixed source paragraph invalid HTML p',lambda r,n,a:setattr(src(r,mixed),'tag','p'))
    trial('original claim mixed into source',lambda r,n,a:src(r,p).append(E.fromstring('<span>Current legal clearance is confirmed.</span>')))
    trial('source proper name altered',lambda r,n,a:setattr(block(r,m['source_keys'][8])[0],'text','Oscar Lewis'))
    trial('LTR isolation removed',lambda r,n,a:block(r,numeral)[0].set('dir','rtl'))
    trial('source URL target swapped',lambda r,n,a:r.xpath('//*[@data-source-url="u4"]')[0].set('href','https://kokunoyumeto.github.io/discrete-mathematics-open-introduction-id/'))
    trial('source URL label altered',lambda r,n,a:setattr(r.xpath('//*[@data-source-url="u1"]')[0][0],'text','different.invalid'))
    trial('cover image substituted',lambda r,n,a:r.xpath('//img')[0].set('src','../assets/b10/qrcode.png'))
    trial('QR source alt discrepancy erased',lambda r,n,a:r.xpath('//img')[1].set('data-source-alt','QR Code to https://discrete.openmathbooks.org/'))
    trial('QR alt falsely certifies payload',lambda r,n,a:r.xpath('//img')[1].set('alt','Verified QR to https://discrete.openmathbooks.org/'))
    trial('QR correction association removed',lambda r,n,a:r.xpath('//img')[1].attrib.pop('aria-describedby'))
    trial('actual PNG bytes changed in detached buffer',lambda r,n,a:a.__setitem__('qrcode',b'not a PNG'))
    trial('inert preamble text changed',lambda r,n,a:setattr(r.xpath('//pre')[1],'text','execute something'))
    trial('inert include parse changed',lambda r,n,a:r.xpath('//*[@data-source-tag="include"]')[0].set('data-source-attributes','{"href":"assets/tikz-defs.tex","parse":"xml"}'))
    trial('executable script added',lambda r,n,a:r.find('body').append(E.fromstring('<script>run()</script>')))
    trial('metadata edition changed',lambda r,n,a:r.find('head/meta[@name="source-edition"]').set('content','Third Edition'))
    trial('notice changed to stale root license',lambda r,n,a:n.__setitem__('source_specific_license','CC BY-SA 4.0'))
    trial('copyright credit changed',lambda r,n,a:setattr(r.find('body/footer/p'),'text','Copyright belongs to someone else.'))
    trial('original qualification removed',lambda r,n,a:r.find('body/main').remove(r.find('body/main')[1]))
    trial('image mirroring CSS injected',lambda r,n,a:setattr(r.find('head/style'),'text',r.find('head/style').text+' img { transform:scaleX(-1); }'))
    trial('source sidebyside falsely made figure',lambda r,n,a:setattr(r.xpath('//*[@data-source-tag="sidebyside"]')[0],'tag','figure'))
    trial('invented line break inserted',lambda r,n,a:src(r,p).append(E.fromstring('<br/>')))
    trial('source q content altered',lambda r,n,a:setattr(r.xpath('//*[@data-source-tag="q"]')[1],'text','غلط'))
    trial('standalone source website removed',lambda r,n,a:r.xpath('//*[@data-source-url="u1"]')[0].getparent().remove(r.xpath('//*[@data-source-url="u1"]')[0]))
    trial('header asserts whole book complete',lambda r,n,a:r.find('body/header').append(E.fromstring('<p>The complete book has been translated.</p>')))
    trial('external stylesheet runtime added',lambda r,n,a:r.find('head').append(E.fromstring('<link rel="stylesheet" href="https://example.invalid/extra.css"/>')))
    trial('unkeyed own text in source container',lambda r,n,a:setattr(src(r,'frontmatter.ptx#/frontmatter/acknowledgement[1]'),'text','999 extra'))
    trial('unkeyed tail after source paragraph',lambda r,n,a:setattr(src(r,p),'tail','999 extra'))
    scoped=[MANIFEST,TRANSLATION,EXCERPT,OUTPUT,NOTICES,BASE/'styles/reader.css',Path(__file__),BASE/'scripts/prepare_b10_frontmatter.py',BASE/'scripts/build_b10_frontmatter.py']+[target for spec,target,data in prepared]
    record={'schema':'pnb-source-bound-reader-qa-v1','unit':'B10-frontmatter','status':'passed','assertions':len(checks),'detached_mutations':mutations,
            'counts':{'source_keys':50,'source_elements':101,'original_ids':4,'prefaces':2,'paragraphs':25,'list_items':4,'source_urls':4,'brandlogo_urls':1,'original_images':2,'q':8,'em':5,'math':0,'tables':0,'footnotes':0,'explicit_source_newlines':0},
            'scoped_hashes':{p.relative_to(BASE).as_posix():file_hash(p) for p in scoped},
            'limitations':['Independent source-bound DOM checks plus exact reviewed footer/CSS regression guards; assertion count is not a linguistic quality score.',
                          'No browser/assistive-technology/native educator certification is claimed by this suite.',
                          'No QR payload decoding, present external service/legal verification, new clearance or source audit.',
                          'All source metadata and parse=text TeX dependency remain inert; no source runtime execution.',
                          'Complete frontmatter checkpoint only; full B10 and all five assigned works remain unfinished.']}
    RECEIPT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'passed','assertions':len(checks),'detached_mutations':len(mutations),'reader_sha256':file_hash(OUTPUT),'receipt_sha256':file_hash(RECEIPT)}))


if __name__=='__main__':
    run()
