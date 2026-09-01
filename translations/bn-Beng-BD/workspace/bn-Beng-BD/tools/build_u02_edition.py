"""Consolidate distinct companions plus one full source module; emit shaped PDFs.

U01 outputs are never overwritten. PDF page-image review remains a separate gate.
"""
from pathlib import Path
import argparse, copy, hashlib, html, json, re
import xml.etree.ElementTree as ET
from build import L,STYLE,write
from build_pdf import tag
from assemble_m81243 import assemble

def sha(data):return hashlib.sha256(data).hexdigest()
def plain(e):
    if tag(e)=='mfrac':return plain(e[0])+'/'+plain(e[1])
    if tag(e)=='mspace':return ' '
    text=(e.text or '')+''.join(plain(child)+(child.tail or '') for child in e)
    # A text-equivalent figure is a separate semantic unit, even in a table
    # cell. Do not glue its last number to the following prose sentence.
    if e.get('class')=='media-description':return ' '+text+' '
    return text
def normalized(text):
    text=text.replace('—','-').replace('–','-').replace('‑','-')
    for index,char in enumerate('ⓐⓑⓒⓓⓔ'):text=text.replace(char,'('+chr(97+index)+')')
    return text

def edition():
    module=assemble()
    docs=[];inputs={}
    for unit in ('u02a','u02b','u02c','u02d','u02e'):
        path=L/'translations'/(unit+'-companion.xhtml');inputs[path.relative_to(L).as_posix()]=sha(path.read_bytes())
        article=ET.parse(path).getroot()
        article.set('data-pdf-break-before','true')
        for title in article.findall('h1'):title.tag='h2'
        docs.append(article)
    full_path=L/'output/m81243/index.html';inputs[full_path.relative_to(L).as_posix()]=sha(full_path.read_bytes())
    full=ET.fromstring(full_path.read_text(encoding='utf-8').split('\n',1)[1]).find('body/main')
    full.tag='section';full.set('id','bd-u02-complete-source');full.set('data-pdf-break-before','true')
    for title in full.findall('./header/h1'):title.tag='h2'
    docs.append(full)
    header='''<header><p class="kicker">bn-Beng-BD · U02 · সম্পূর্ণ খসড়া পাঠসংকলন</p>
<h1>সংখ্যা পড়ি, লিখি ও আসন্ন মান বুঝি</h1>
<p>এই সংকলনে আছে চারটি সহজ পাঠ, উৎসের সব অনুশীলনের আলাদা উত্তর-সহায়িকা এবং পুরো m81243 মডিউলের বিশ্বস্ত অনুবাদ। প্রতিটি উৎস-অংশ একবারই দেওয়া হয়েছে।</p>
<p>শিক্ষক শিশুর প্রস্তুতি অনুযায়ী পাঠ বাছবেন। ভগ্নাংশ, দশমিক ও বিলিয়ন-ট্রিলিয়নের সব কাজ দ্বিতীয় শ্রেণির জন্য বাধ্যতামূলক নয়। এটি AI-সহায়তায় তৈরি বাংলাদেশ বাংলা খসড়া; বাংলাদেশের শিক্ষকের পর্যালোচনা বাকি।</p>
<nav aria-label="সংকলনের অংশ"><ol><li><a href="#bd-u02a-companion">অঙ্কের স্থান</a></li><li><a href="#bd-u02b-companion">সংখ্যা কথায় লেখা</a></li><li><a href="#bd-u02c-companion">কথা থেকে অঙ্ক</a></li><li><a href="#bd-u02d-companion">আসন্ন মান</a></li><li><a href="#bd-u02e-companion">সব অনুশীলনের উত্তর</a></li><li><a href="#bd-u02-complete-source">সম্পূর্ণ উৎস-মডিউল</a></li></ol></nav>
<p>ডিজিটাল সংস্করণে পাঠের অংশ বেছে নেওয়া ও মূল সূত্রে যাওয়ার লিংক আছে। PDF একটি পড়ার কপি; এটি ট্যাগযুক্ত PDF/UA নথি নয়।</p></header>'''
    content=header+'\n'.join(ET.tostring(e,encoding='unicode') for e in docs)
    page='<!DOCTYPE html>\n<html lang="bn-Beng-BD"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>U02 সংখ্যা পড়ি, লিখি ও আসন্ন মান বুঝি</title><style>'+STYLE.replace('../assets/','../../assets/').replace('NumeracyBangla.ttf','NumeracyBanglaMath.ttf')+'\n.circled{list-style:none}dd{margin-bottom:1rem}</style></head><body><main>'+content+'</main></body></html>\n'
    root=ET.fromstring(page.split('\n',1)[1]);ids=[e.get('id') for e in root.iter() if e.get('id')]
    assert len(ids)==len(set(ids))
    for link in root.iter('a'):
        href=link.get('href','')
        if href.startswith('#'):assert href[1:] in ids,href
        elif href and not href.startswith(('http://','https://')):
            path,_,anchor=href.partition('#');file=(L/'output/U02'/path).resolve();assert file.is_file()
            if anchor:assert 'id="'+anchor+'"' in file.read_text(encoding='utf-8')
    write(L/'output/U02/index.html',page)
    receipt={'edition':'U02','html_sha256':sha(page.encode()),'inputs':inputs,'complete_source_module_sha256':module['translation_sha256'],'unique_html_ids':len(ids),'semantic_html':'local fonts; no scripts; complete source appears once','pdf_visual_status':'pending'}
    write(L/'output/U02/build-receipt.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return root,receipt

def build_pdfs(root):
    from reportlab import rl_config
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
    import fitz
    rl_config.invariant=1
    font=TTFont('BengaliU02',str(L/'assets/NumeracyBanglaMath.ttf'),shapable=True);pdfmetrics.registerFont(font)
    assert font.shapable
    main=root.find('body/main')
    missing={ord(c) for c in normalized(plain(main)) if not c.isspace() and ord(c) not in font.face.charToGlyph}
    assert not missing,missing
    results=[]
    for kind,size in [('print',12),('screen',16)]:
        styles={
          'p':ParagraphStyle('body',fontName='BengaliU02',fontSize=size,leading=size*1.65,spaceAfter=size*.55,shaping=True,splitLongWords=True),
          'h1':ParagraphStyle('h1',fontName='BengaliU02',fontSize=size*1.7,leading=size*2.35,spaceAfter=14,keepWithNext=True,shaping=True),
          'h2':ParagraphStyle('h2',fontName='BengaliU02',fontSize=size*1.28,leading=size*1.9,spaceBefore=16,spaceAfter=9,keepWithNext=True,shaping=True,textColor=HexColor('#174f47')),
          'h3':ParagraphStyle('h3',fontName='BengaliU02',fontSize=size*1.05,leading=size*1.7,spaceBefore=10,spaceAfter=6,keepWithNext=True,shaping=True),
          'label':ParagraphStyle('label',fontName='BengaliU02',fontSize=size*.85,leading=size*1.4,spaceBefore=8,spaceAfter=5,keepWithNext=True,shaping=True)}
        story=[];emitted=[]
        def para(text,style='p'):
            emitted.append(normalized(text));return Paragraph(html.escape(normalized(text)),styles[style])
        def visit(e):
            t=tag(e)
            if t=='nav':return
            if e.get('data-pdf-break-before')=='true':story.append(PageBreak())
            if t in ('h1','h2','h3','p','li','figcaption','dt','dd') or (t=='span' and e.get('class')=='media-description') or (t in ('aside','div','section') and len(e)==0):
                text=plain(e).strip();style='label' if e.get('class')=='source-label' else t if t in styles else 'p'
                if text:story.append(para(text,style))
                return
            if t=='table':
                caption=e.find('caption')
                if caption is not None:story.append(para(plain(caption),'h3'))
                rows=[[para(plain(cell)) for cell in row] for row in e.findall('.//tr')]
                table=Table(rows,colWidths=[(A4[0]-100)/len(rows[0])]*len(rows[0]),repeatRows=1 if e.find('thead') is not None else 0,hAlign='LEFT',splitInRow=1)
                table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,HexColor('#60736d')),('BACKGROUND',(0,0),(-1,0),HexColor('#eaf1ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
                story.extend([table,Spacer(1,12)]);return
            if t=='math':story.append(para(plain(e)));return
            for child in e:visit(child)
        visit(main)
        expected=copy.deepcopy(main)
        for parent in expected.iter():
            for child in list(parent):
                if tag(child)=='nav':parent.remove(child)
        squash=lambda s:re.sub(r'\s+','',normalized(s))
        expected_text=squash(plain(expected));emitted_text=squash(''.join(emitted))
        if expected_text!=emitted_text:
            index=next((i for i,(a,b) in enumerate(zip(expected_text,emitted_text)) if a!=b),min(len(expected_text),len(emitted_text)))
            raise AssertionError(('Semantic text dropped/duplicated',index,expected_text[max(0,index-80):index+180],emitted_text[max(0,index-80):index+180]))
        out=L/'output/pdf'/('u02-complete-'+kind+'.pdf');out.parent.mkdir(parents=True,exist_ok=True)
        def footer(canvas,doc):
            canvas.setFont('Helvetica',9);canvas.setFillColor(HexColor('#425650'))
            canvas.drawString(50,28,'bn-Beng-BD | U02 + m81243 | '+kind+' | '+str(doc.page))
        pdf=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=44,bottomMargin=48,title='Bangladesh Bangla U02 and complete m81243 - '+kind,author='Language Allocation; adapted from OpenStax / Rice University',lang='bn-Beng-BD')
        pdf.build(story,onFirstPage=footer,onLaterPages=footer)
        doc=fitz.open(out);text='\n'.join(p.get_text() for p in doc)
        assert '\ufffd' not in text
        module=ET.parse(L/'translations/complete_modules/m81243/index.cnxml').getroot()
        exercises=[e.get('id') for e in module.iter() if tag(e)=='exercise']
        for marker in exercises+['OpenStax','Rice University']:assert marker in text,(kind,marker)
        overflow=[]
        for i,p in enumerate(doc):
            assert len(p.get_text())>80
            for block in p.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    x0,y0,x1,y1=line['bbox']
                    if x0<43 or y0<25 or x1>p.rect.width-43 or y1>p.rect.height-18:overflow.append((i+1,line['bbox'],''.join(s['text'] for s in line['spans'])))
        assert not overflow,overflow[:10]
        pua=sum(0xE000<=ord(c)<=0xF8FF for c in text)
        results.append({'file':out.relative_to(L).as_posix(),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'pages':len(doc),'font_size_pt':size,'semantic_flowable_text_coverage_verified':True,'semantic_check_scope':'HTML text equals PDF flowable input before font encoding; not a Unicode extraction guarantee.','all_88_source_exercise_ids_found':True,'all_pages_bounds_checked':True,'text_extraction_chars':len(text),'private_use_extracted_chars':pua,'bengali_copy_search_text_reliable':False,'tagged':False,'PDF_UA_claim':False,'visual_review':'pending actual page-image inspection','normalization':'Unicode dashes to ASCII hyphens; circled a-e to (a)-(e); MathML fractions to a/b; spaces around figure text equivalents.'})
    write(L/'output/pdf/u02-build-receipt.json',json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    return results

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--html-only',action='store_true');args=p.parse_args()
    root,receipt=edition();print(json.dumps(receipt,ensure_ascii=False,indent=2))
    if not args.html_only:print(json.dumps(build_pdfs(root),ensure_ascii=False,indent=2))
