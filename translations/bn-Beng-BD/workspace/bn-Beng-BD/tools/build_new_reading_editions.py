"""New front-matter/addition reading PDFs; old U01/U02 editions never touched.

PDF-only presentation transforms are explicit and checked before font encoding.
Actual page-image inspection is required separately before delivery.
"""
import argparse, copy, html, json, re, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from build import L, write, sha, local

JOBS={
    'm81241':('output/m81241/index.html','Preface'),
    'm81242':('output/m81242/index.html','Whole Numbers introduction'),
    'm81244':('output/m81244/index.html','Complete addition source'),
    'u03a-lesson':('output/U03A/index.html','Addition child lesson'),
    'u03a-answers':('output/U03A/answers.html','All addition worked answers')
}
BLOCK={'header','footer','article','section','aside','div','figure','table','p','li','ul','ol','dl','dt','dd','figcaption','h1','h2','h3','h4','h5','h6'}


def normalized(text):
    for char in '—–‑‐‒―':text=text.replace(char,'-')
    for i,char in enumerate('ⓐⓑⓒⓓⓔ'):text=text.replace(char,'('+chr(97+i)+')')
    return text


def plain(e):
    tag=local(e)
    if tag in ('br','newline'):return '\n'
    if tag=='mspace':return ' '
    if tag=='mfrac':return '('+plain(e[0])+')/('+plain(e[1])+')'
    if tag=='mover':return plain(e[0])+' [ওপরে '+plain(e[1])+']'
    if tag=='munder':return plain(e[0])+'\n'+plain(e[1])
    if tag=='mtable':
        rows=[' | '.join(plain(c) for c in row) for row in e]
        return '\n'.join(row for row in rows if row.strip())
    text=(e.text or '')+''.join(plain(n)+(n.tail or '') for n in e)
    # Adjacent inline MathML nodes may have only source whitespace between
    # them.  Give each expression an explicit PDF boundary so identities such
    # as a + 0 = a and 0 + a = a cannot visually join.
    if tag=='math':text=' '+text+' '
    if tag=='li' and e.get('data-pdf-omit-bullet')!='true':text='- '+text
    if e.get('class')=='media-description':text=' '+text+' '
    return text


def prepare(path, identifier):
    root=ET.fromstring(path.read_text(encoding='utf-8').split('\n',1)[1])
    main=copy.deepcopy(root.find('body/main'))
    removed_nav=0; compact_grids=0; omitted_table_bullets=0
    for parent in list(main.iter()):
        for child in list(parent):
            if local(child)=='nav':parent.remove(child);removed_nav+=1
        if parent.get('class')=='media-description' and parent.find('.//table') is not None:
            descriptions=[n for n in parent if n.tag=='p']
            assert len(descriptions)==1
            descriptions[0].text='চিত্রের সংখ্যাগুলো নিচের সম্পূর্ণ ছকে আছে; ফাঁকা ঘরও চিহ্নিত।'
            compact_grids+=1
        if local(parent)=='li' and not (parent.text or '').strip() and len(parent) and local(parent[0])=='table':
            parent.set('data-pdf-omit-bullet','true');omitted_table_bullets+=1
    note=ET.Element('p',{'class':'pdf-note'})
    note.text='এটি দৃশ্যমান PDF পড়ার কপি, ট্যাগযুক্ত PDF/UA নয়। বাংলা কপি বা খোঁজার পাঠ নির্ভরযোগ্য নাও হতে পারে; পাঠ্য ও লিংকের জন্য সঙ্গে থাকা HTML ব্যবহার করুন।'
    if identifier in ('m81244','u03a-answers'):
        note.text+=' ওপর-নিচে সাজানো যোগে একই ঘরের অঙ্ক একই কলামে আছে। হাতে রাখা ছোট অঙ্ক সংশ্লিষ্ট অঙ্কের ওপরে আছে; এগুলো ভগ্নাংশ নয়।'
    for parent in main.iter():
        headings=[n for n in parent if n.tag=='h1']
        if headings:
            parent.insert(list(parent).index(headings[0])+1,note);break
    else:raise AssertionError('Missing title')
    license_note=ET.SubElement(main,'p',{'class':'pdf-note'})
    license_note.text='Source/adaptation: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . Component notices apply. Noto-derived fonts: SIL OFL 1.1. Original author/reviewer credits: accompanying m81241 preface. No OpenStax or Rice University endorsement.'
    return main,{'navigation_blocks_omitted':removed_nav,'verbose_grid_alternatives_presented_as_tables':compact_grids,'redundant_standalone_table_bullets_omitted':omitted_table_bullets}


def stacked_rows(table):
    """Read numeric source MathML stacks, retaining carry positions."""
    rows=[]
    for row in table:
        assert local(row)=='mtr'
        if not len(row):continue
        assert len(row)==1 and local(row[0])=='mtd' and row[0].get('columnalign') in ('left','right')
        chars=[];carries=[];rule=False
        def walk(e):
            nonlocal rule
            tag=local(e)
            if tag=='mspace':return
            if tag=='munder':
                assert len(e)==2 and local(e[1])=='mtext' and re.fullmatch('_+',plain(e[1]))
                walk(e[0]);rule=True;return
            if tag=='mover':
                assert len(e)==2
                base=plain(e[0]);over=plain(e[1])
                assert re.fullmatch('[0-9],?',base) and re.fullmatch('[0-9]+',over)
                carries.append((len(chars),over));chars.extend(base);return
            if tag in ('mn','mo'):
                value=(e.text or '').strip();assert re.fullmatch('[0-9,+]+',value),value
                chars.extend(value);return
            assert tag in ('mtd','mrow') and not (e.text or '').strip(),tag
            for child in e:walk(child)
        walk(row[0]);assert chars
        rows.append({'text':''.join(chars),'carries':carries,'underlined':rule})
    assert len(rows)>=2 and any(r['underlined'] for r in rows)
    verify_stack(rows)
    return rows


def verify_stack(rows):
    """Independently check every displayed carry and partial/final sum."""
    rules=[i for i,row in enumerate(rows) if row['underlined']]
    assert len(rules)==1
    end=rules[0];assert end>=1 and len(rows) in (end+1,end+2)
    numbers=[int(row['text'].lstrip('+').replace(',','')) for row in rows[:end+1]]
    total=sum(numbers)
    if len(rows)==end+2:
        digits=rows[-1]['text'].replace(',','')
        assert int(digits)==total%(10**len(digits)),(numbers,digits,total)
        assert int(digits)<=total
    for row in rows:
        for index,value in row['carries']:
            assert row is rows[0]
            power=sum(c.isdigit() for c in row['text'][index+1:])
            assert power>0
            place=10**power
            assert int(value)==sum(n%place for n in numbers)//place,(numbers,index,value)
    return total


def stack_layout(rows,advance,gap):
    """Place digits by numeric rank; punctuation never consumes a rank."""
    columns=max(sum(char.isdigit() for char in row['text']) for row in rows)
    separators=(columns-1)//3
    # Reserve one operator position on the left even for result rows.
    width=4+(columns+1)*advance+separators*gap
    def digit_x(rank):
        assert 0<=rank<columns
        return 2+(columns-rank+.5)*advance+(separators-rank//3)*gap
    layouts=[]
    for row in rows:
        text=row['text'];digit_count=sum(char.isdigit() for char in text)
        assert digit_count and digit_count<=columns
        glyphs=[];positions={}
        for index,char in enumerate(text):
            if char.isdigit():
                rank=sum(c.isdigit() for c in text[index+1:])
                x=digit_x(rank)
            elif char==',':
                right=sum(c.isdigit() for c in text[index+1:])
                assert right and right%3==0 and right<digit_count
                x=(digit_x(right)+digit_x(right-1))/2
            elif char=='+':
                x=2+.5*advance
            else:raise AssertionError(('Unexpected stack glyph',char))
            glyphs.append((char,x));positions[index]=x
        carries=[(positions[index],value) for index,value in row['carries']]
        layouts.append({'glyphs':glyphs,'carries':carries})
    return {'columns':columns,'width':width,'rows':layouts}


def paragraph_style_key(e,styles):
    """Class-specific pagination rules take priority over the HTML tag."""
    if e.get('class')=='source-label':return 'label'
    tag=local(e)
    if tag in styles:return tag
    if e.get('class')=='pdf-note':return 'pdf-note'
    return 'p'


def build(identifier, kinds=('print','screen')):
    from reportlab import rl_config
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Flowable
    import fitz
    source,title=JOBS[identifier]; path=L/source
    main,transforms=prepare(path,identifier)
    fontpath=L/'assets/NumeracyBanglaMath.ttf'
    rl_config.invariant=1
    fontname='BengaliNewEditions'
    if fontname not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(fontname,str(fontpath),shapable=True))
    font=pdfmetrics.getFont(fontname);assert font.shapable
    missing={ord(c) for c in normalized(plain(main)) if not c.isspace() and ord(c) not in font.face.charToGlyph and ord(c) not in (0x200c,0x200d)}
    assert not missing,('Missing glyphs',identifier,missing)
    result=[]
    for kind in kinds:
        size={'print':12,'screen':16}[kind]
        styles={'p':ParagraphStyle('body',fontName=fontname,fontSize=size,leading=size*1.6,spaceAfter=size*.5,shaping=True,splitLongWords=True),
                'pdf-note':ParagraphStyle('note',fontName=fontname,fontSize=size*.85,leading=size*1.4,spaceAfter=10,shaping=True,textColor=HexColor('#425650'))}
        # Source labels retain the established body appearance; only their
        # pagination contract differs.
        styles['label']=ParagraphStyle('label',parent=styles['p'],keepWithNext=True)
        # Do not let ReportLab split a shaped Bangla word inside a grapheme
        # cluster merely to fit an equal-width table cell.  Screen tables use
        # a still-large 14 pt setting to give compounds safe wrap points.
        styles['table-cell']=(ParagraphStyle('table-cell',parent=styles['p'],fontSize=14,leading=14*1.45,splitLongWords=False)
                              if identifier=='m81244' and kind=='screen' else styles['p'])
        styles['list-lead']=ParagraphStyle('list-lead',parent=styles['p'],keepWithNext=True)
        styles['credit-line']=ParagraphStyle('credit-line',parent=styles['p'],spaceAfter=0)
        for level in range(1,7):
            scale={1:1.7,2:1.28,3:1.08}.get(level,1)
            styles['h'+str(level)]=ParagraphStyle('h'+str(level),fontName=fontname,fontSize=size*scale,leading=size*scale*1.45,spaceBefore=14 if level>1 else 0,spaceAfter=8,keepWithNext=True,shaping=True,textColor=HexColor('#174f47'))
        story=[]; emitted=[];stacked_contracts=[]
        class StackedAddition(Flowable):
            def __init__(self,rows):
                super().__init__();self.rows=rows
                self.advance=max(pdfmetrics.stringWidth(c,fontname,size) for c in '0123456789')
                self.layout=stack_layout(rows,self.advance,self.advance*.35)
                self.width=self.layout['width']
                self.height=sum(size*1.6+(size*.7 if row['carries'] else 0) for row in rows)+4
            def draw(self):
                top=self.height-2
                for row,layout in zip(self.rows,self.layout['rows']):
                    carry_space=size*.7 if row['carries'] else 0
                    baseline=top-carry_space-size
                    self.canv.setFont(fontname,size)
                    for char,x in layout['glyphs']:
                        self.canv.drawCentredString(x,baseline,char)
                    if row['underlined']:
                        self.canv.setLineWidth(.6)
                        self.canv.line(2,baseline-size*.23,self.width-2,baseline-size*.23)
                    self.canv.setFont(fontname,size*.6)
                    for x,value in layout['carries']:
                        self.canv.drawCentredString(x,baseline+size*.95,value)
                    top-=size*1.6+carry_space
        def para(text,style='p'):
            value=normalized(text).strip(); emitted.append(value)
            return Paragraph(html.escape(value).replace('\n','<br/>'),styles[style])
        def add_text(text,style='p'):
            if text.strip():story.append(para(text,style))
        def table_cell(cell):
            children=list(cell)
            if len(children)==1 and local(children[0])=='math' and not (cell.text or '').strip() and not (children[0].tail or '').strip():
                maths=list(children[0])
                if len(maths)==1 and local(maths[0])=='mtable' and any(local(n)=='munder' for n in maths[0].iter()):
                    rows=stacked_rows(maths[0]);emitted.append(normalized(plain(cell)).strip())
                    stacked_contracts.append(rows)
                    return StackedAddition(rows)
            return para(plain(cell),'table-cell')
        def visit(e):
            tag=local(e)
            if tag=='table':
                caption=e.find('caption')
                if caption is not None:add_text(plain(caption),'h3')
                source_rows=e.findall('.//tr'); assert source_rows
                columns=len(source_rows[0]);assert all(len(row)==columns for row in source_rows)
                rows=[[table_cell(cell) for cell in row] for row in source_rows]
                table=Table(rows,colWidths=[(A4[0]-100)/columns]*columns,repeatRows=1 if e.find('thead') is not None else 0,hAlign='LEFT',splitInRow=1)
                pad=3 if columns>=8 else 6
                commands=[('GRID',(0,0),(-1,-1),.5,HexColor('#60736d')),('BACKGROUND',(0,0),(-1,0),HexColor('#eaf1ef')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),pad),('RIGHTPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]
                if any(cell.get('scope')=='row' for row in source_rows for cell in row):commands.append(('BACKGROUND',(0,1),(0,-1),HexColor('#f3f6f5')))
                table.setStyle(TableStyle(commands));story.extend([table,Spacer(1,10)]);return
            nested=any(local(n) in BLOCK for n in list(e.iter())[1:])
            if identifier=='m81241' and tag=='p' and not nested and e.find('br') is not None:
                # Separate credit lines can paginate after their heading; a giant
                # hard-break Paragraph otherwise leaves almost empty pages.
                lines=plain(e).split('\n')
                for index,line in enumerate(lines):
                    add_text(line,'p' if index==len(lines)-1 else 'credit-line')
                return
            if re.fullmatch('h[1-6]',tag) or tag=='math' or (tag in ('p','li','dt','dd','figcaption') and not nested):
                style=paragraph_style_key(e,styles)
                add_text(plain(e),style);return
            buffer=('- ' if tag=='li' and e.get('data-pdf-omit-bullet')!='true' else '')+(e.text or '')
            for child in e:
                if local(child) in BLOCK:
                    add_text(buffer,'list-lead' if identifier=='m81241' and tag=='li' else 'p');buffer='';visit(child)
                else:buffer+=plain(child)
                buffer+=child.tail or ''
            add_text(buffer)
        visit(main)
        squash=lambda s:re.sub(r'\s+','',normalized(s))
        expected=squash(plain(main));actual=squash(''.join(emitted))
        if expected!=actual:
            index=next((i for i,(a,z) in enumerate(zip(expected,actual)) if a!=z),min(len(expected),len(actual)))
            raise AssertionError(('PDF semantic input mismatch',identifier,index,expected[max(0,index-70):index+150],actual[max(0,index-70):index+150]))
        out=L/'output/pdf'/(identifier+'-'+kind+'.pdf');out.parent.mkdir(parents=True,exist_ok=True)
        def footer(canvas,doc):
            canvas.setFont('Helvetica',9);canvas.setFillColor(HexColor('#425650'))
            canvas.drawString(50,28,'bn-Beng-BD | '+identifier+' | '+kind+' | '+str(doc.page))
        pdf=SimpleDocTemplate(str(out),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=44,bottomMargin=48,title='Bangladesh Bangla '+title+' - '+kind,author='Language Allocation; adapted from OpenStax / Rice University',lang='bn-Beng-BD')
        pdf.build(story,onFirstPage=footer,onLaterPages=footer)
        doc=fitz.open(out);text='\n'.join(page.get_text() for page in doc)
        assert '\ufffd' not in text
        markers=['OpenStax','Rice University']
        if identifier in ('m81244','u03a-answers'):
            source_root=ET.parse(L/'translations/complete_modules/m81244/index.cnxml').getroot()
            markers += [n.get('id') for n in source_root.iter() if local(n)=='exercise']
        for marker in markers:assert marker in text,(identifier,kind,marker)
        overflow=[]
        for index,page in enumerate(doc,1):
            assert len(page.get_text())>70,(identifier,index)
            for block in page.get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    x0,y0,x1,y1=line['bbox']
                    if x0<43 or y0<25 or x1>page.rect.width-43 or y1>page.rect.height-18:overflow.append((index,line['bbox'],''.join(s['text'] for s in line['spans'])))
        assert not overflow,(identifier,kind,overflow[:10])
        result.append({'file':out.relative_to(L).as_posix(),'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'pages':len(doc),'font_size_pt':size,'input_html':source,'input_html_sha256':sha(path.read_bytes()),'font_sha256':sha(fontpath.read_bytes()),'pdf_transformations':transforms,'semantic_flowable_input_coverage_pass':True,'semantic_input_sha256':sha(expected.encode()),'stacked_additions':stacked_contracts,'source_identifier_markers_verified':len(markers)-2,'all_pages_bounds_checked':True,'bengali_copy_search_text_reliable':False,'private_use_extracted_chars':sum(0xe000<=ord(c)<=0xf8ff for c in text),'tagged':False,'PDF_UA_claim':False,'visual_review':'pending actual PNG inspection','normalization':'ASCII dashes; circled a-e to (a)-(e); fractions to parenthesized a/b; inline MathML gets visible boundary spaces; numeric stacked additions align digits by numeric rank while preserving source commas/carries and drawn rules; semantic comparison represents mover as base [above value]; verbose duplicate image-grid descriptions replaced by complete visible tables.'})
        doc.close()
    receipt=L/'output/pdf'/(identifier+'-build-receipt.json')
    write(receipt,json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('jobs',nargs='*',default=list(JOBS));parser.add_argument('--isolated-job',action='store_true',help=argparse.SUPPRESS);args=parser.parse_args()
    if args.isolated_job:assert len(args.jobs)==1
    for job in args.jobs:
        assert job in JOBS
        if args.isolated_job:
            result=build(job)
            print(json.dumps({'job':job,'outputs':[{k:r[k] for k in ('file','pages','bytes','sha256')} for r in result]},ensure_ascii=False),flush=True)
        else:
            # ReportLab's process-global shaping/font state can otherwise make
            # later documents depend on which other job was built first.
            subprocess.run([sys.executable,'-B',str(Path(__file__).resolve()),job,'--isolated-job'],check=True)
