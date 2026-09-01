"""Produce shaped Bengali screen/print reading copies from the verified HTML.

Requires reportlab 4.4.9 and uharfbuzz 0.55.0. HTML remains the semantic,
screen-reader-preferred edition; these PDFs do not claim PDF/UA conformance.
"""
from pathlib import Path
import copy, hashlib, html, json, re, shutil, xml.etree.ElementTree as ET
from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

L=Path(__file__).resolve().parents[1]
R=L.parent
rl_config.invariant=1
def tag(e): return e.tag.rsplit('}',1)[-1]
def plain(e):
    if tag(e)=='mfrac': return plain(e[0])+'/'+plain(e[1])
    if tag(e)=='mspace': return ' '
    return (e.text or '')+''.join(plain(c)+(c.tail or '') for c in e)
def normalized(s):
    return s.replace('—','-').replace('–','-').replace('ⓐ','(a)').replace('ⓑ','(b)').replace('‑','-')
def main():
    assets=L/'assets';assets.mkdir(exist_ok=True)
    for name in ('NotoSansBengali-Regular.ttf','NotoSans-Regular.ttf','Noto-LICENSE.txt'):
        if not (assets/name).exists(): shutil.copyfile(R/'vendor/bn-Beng-BD'/name,assets/name)
    font=TTFont('Bengali',str(assets/'NumeracyBangla.ttf'),shapable=True)
    pdfmetrics.registerFont(font)
    assert font.shapable, 'HarfBuzz shaping is required, not optional.'
    doc=ET.fromstring((L/'output/u01-number-sense.html').read_text(encoding='utf-8').split('\n',1)[1])
    main_node=doc.find('.//main')
    source_text=normalized(plain(main_node))
    missing=sorted({ord(c) for c in source_text if not c.isspace() and ord(c) not in font.face.charToGlyph})
    assert not missing, 'Font lacks: '+repr(missing)
    result=[]
    for kind,fontsize in [('print',12),('screen',16)]:
        out=L/'output/pdf'/('u01-'+kind+'.pdf');out.parent.mkdir(parents=True,exist_ok=True)
        styles={
            'p':ParagraphStyle('body',fontName='Bengali',fontSize=fontsize,leading=fontsize*1.65,spaceAfter=fontsize*.55,shaping=True,splitLongWords=False),
            'h1':ParagraphStyle('h1',fontName='Bengali',fontSize=fontsize*1.7,leading=fontsize*2.35,spaceAfter=14,keepWithNext=True,shaping=True),
            'h2':ParagraphStyle('h2',fontName='Bengali',fontSize=fontsize*1.28,leading=fontsize*1.9,spaceBefore=16,spaceAfter=9,keepWithNext=True,shaping=True,textColor=HexColor('#174f47')),
            'h3':ParagraphStyle('h3',fontName='Bengali',fontSize=fontsize*1.05,leading=fontsize*1.7,spaceBefore=10,spaceAfter=6,keepWithNext=True,shaping=True),
            'label':ParagraphStyle('label',fontName='Bengali',fontSize=fontsize*.85,leading=fontsize*1.4,spaceBefore=8,spaceAfter=5,keepWithNext=True,shaping=True),
        }
        story=[];emitted=[]
        def para(text,style='p'):
            emitted.append(normalized(text))
            return Paragraph(html.escape(normalized(text)),styles[style])
        def visit(e):
            t=tag(e)
            if t in ('nav','header'): return
            if e.get('id')=='faithful': story.append(PageBreak())
            if t in ('h1','h2','h3','p','li','figcaption') or (t=='span' and e.get('class')=='media-description') or (t=='aside' and len(e)==0):
                txt=plain(e).strip()
                style='label' if e.get('class')=='source-label' else (t if t in styles else 'p')
                if txt: story.append(para(txt,style))
                return
            if t=='table':
                cap=e.find('caption')
                if cap is not None: story.append(para(plain(cap),'h3'))
                rows=[[para(plain(c)) for c in row] for row in e.findall('.//tr')]
                width=A4[0]-100
                table=Table(rows,colWidths=[width/len(rows[0])]*len(rows[0]),repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,HexColor('#60736d')),('BACKGROUND',(0,0),(-1,0),HexColor('#eaf1ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
                story.extend([table,Spacer(1,12)]);return
            if t=='math': story.append(para(plain(e)));return
            for c in e: visit(c)
        visit(main_node)
        expected=copy.deepcopy(main_node)
        for child in list(expected):
            if tag(child) in ('nav','header'):expected.remove(child)
        squash=lambda text: re.sub(r'\s+','',normalized(text))
        assert squash(plain(expected))==squash(''.join(emitted)), 'PDF renderer dropped or duplicated semantic text'
        def footer(canvas,doc):
            canvas.setFont('Helvetica',9)
            canvas.setFillColor(HexColor('#425650'))
            canvas.drawString(50,28,'bn-Beng-BD | U01 | '+kind+' | '+str(doc.page),shaping=True)
        pdf=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=44,bottomMargin=48,title='Bangladesh Bangla Numeracy U01 - '+kind,author='Language Allocation; adapted from OpenStax / Rice University',lang='bn-Beng-BD')
        pdf.build(story,onFirstPage=footer,onLaterPages=footer)
        result.append({'file':str(out.relative_to(L)).replace('\\','/'),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'font_size_pt':fontsize,'shaping':'HarfBuzz','semantic_text_coverage_verified':True,'tagged':False,'PDF_UA_claim':False,'content':'Faithful extract and separate companion; figures are text equivalents; fractions rendered as a/b; circled labels as (a)/(b).'})
    (L/'output/pdf/build-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
