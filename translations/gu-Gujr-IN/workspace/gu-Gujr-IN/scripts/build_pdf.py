"""Build print PDFs with Gujarati shaping. HTML is the primary semantic format.

Requires reportlab and uharfbuzz. Never claim PDF/UA conformance.
"""
from functools import partial
import json
import os
from pathlib import Path
import sys
from xml.sax.saxutils import escape

LANG = Path(__file__).resolve().parents[1]
ROOT = LANG.parent
sys.path.insert(0, str(ROOT / 'downloads/gu-Gujr-IN/python-deps'))
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether

UNIT = json.loads((LANG/'translations/unit01.gu.json').read_text(encoding='utf-8'))
pdfmetrics.registerFont(TTFont('Gujarati', str(LANG/'assets/NotoSansGujarati.ttf'), shapable=True))
FONT_CODEPOINTS = set(pdfmetrics.getFont('Gujarati').face.charToGlyph)
STYLES = {name: ParagraphStyle(name, fontName='Gujarati', fontSize=size, leading=leading,
                              textColor=colors.HexColor('#182c35'), spaceAfter=space, shaping=True,
                              alignment=TA_LEFT, splitLongWords=False, keepWithNext=(name in ('h1','h2','h3')))
          for name,size,leading,space in [('h1',23,34,18),('h2',17,26,12),('h3',12,21,7),('body',11,20,9),('small',8,14,6)]}


class ActualTextParagraph(Paragraph):
    def __init__(self,text,*args,**kwargs):
        super().__init__(text,*args,**kwargs)
        self._logical_text=self.getPlainText()

    def draw(self):
        # HarfBuzz's shaped ligatures use private glyph codes. Retain the logical
        # Unicode text for extraction without altering the printed glyphs.
        assert not any('\ue000'<=c<='\uf8ff' for c in self._logical_text), 'Logical text must precede glyph shaping'
        logical=self._logical_text.encode('utf-16-be').hex().upper()
        self.canv._code.append('/Span << /ActualText <FEFF'+logical+'> >> BDC')
        try:
            super().draw()
        finally:
            self.canv._code.append('EMC')


def para(text,style='body'):
    # Preserve subpart letters using supported print glyphs; the editable source
    # and HTML retain their original circled labels.
    text = text.translate({0x24D0+i: '('+chr(97+i)+')' for i in range(26)})
    missing = sorted({ord(c) for c in text if not c.isspace() and ord(c) not in FONT_CODEPOINTS})
    if missing:
        raise ValueError('Gujarati print font lacks: '+', '.join(f'U+{c:04X}' for c in missing))
    return ActualTextParagraph(escape(text),STYLES[style])


def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#708d91'));canvas.line(42,36,553,36)
    canvas.setFont('Helvetica',8);canvas.drawString(42,24,'GU-NUM-01 | CC BY-NC-SA 4.0 | Unofficial Gujarati pilot')
    canvas.drawRightString(553,24,str(doc.page));canvas.restoreState()


def title(text):
    return [para('ગુજરાતી · GU-NUM-01','small'),para(text,'h1'),para(UNIT['subtitle']),
            para('પ્રારંભિક આવૃત્તિ. ગુજરાતી શિક્ષકની સમીક્ષા બાકી છે. આ પ્રમાણિત કસોટી નથી.','small')]


def attribution():
    return [PageBreak(),para('સ્રોત અને શ્રેય','h2'),
            para('OpenStax Prealgebra 2e અને Elementary Algebra 2e; Rice University. મૂળ લેખકો: Lynn Marecek, MaryAnne Anthony-Smith અને Andrea Honeycutt Mathis.'),
            para('Indonesian adaptations: KokunoYumeto repositories, A00 v0.2.7 અને A10 v1.0.2; produced with OpenAI Codex gpt-5.6-sol, Ultra. Gujarati translation and separate diagnostic companion: Language Allocation, OpenAI Codex, 2026-08-30.'),
            para('Canonical OpenStax commit: 38cae454e644abf9f0a623e876994553881597c9. Gujarati material adapts A00 m81243 and selected A10 m82452; original identifiers and source-faithful text are in source.html. Added explanations and diagnostics are explicitly separate.'),
            para('https://github.com/openstax/osbooks-prealgebra-bundle'),
            para('https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID'),
            para('https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id'),
            para('CC BY-NC-SA 4.0, subject to component-specific credits and restrictions. https://creativecommons.org/licenses/by-nc-sa/4.0/ . Unmodified licenses and prior notices accompany the offline package. This adaptation is not endorsed by OpenStax or Rice University. Names, logos and marks are not licensed. Content is provided as-is, without warranty.'),
            para('Noto Sans Gujarati: SIL Open Font License; assets/OFL.txt. Gujarati school-reference materials informed language only; they are not reproduced in this PDF.'),
            para('સુલભતા: આ PDF છાપવા માટે છે. ગુજરાતી અક્ષરો માટે ફોન્ટ જોડેલો છે. મૂળ HTML માં શીર્ષકો, MathML અને ચિત્રના લખાણરૂપ વર્ણનો છે. PDF/UA પ્રમાણન કે માનવી દ્વારા સ્ક્રીન-રીડર પરીક્ષણ થયું નથી.')]


def write_pdf(name,story):
    path=LANG/'output/pdf'/name;path.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=48,
                          title=UNIT['title'],author='Language Allocation / OpenAI Codex',lang='gu-Gujr-IN')
    doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=partial(Canvas,invariant=1))
    print(path.relative_to(ROOT))


def build():
    student=title(UNIT['title'])+[para(t) for t in UNIT['intro']]
    student += [PageBreak(),para('પહેલી તપાસ','h2')]
    for item in [i for i in UNIT['items'] if i['phase']=='placement']:
        block=[para(f'{item["id"]} · {item["prompt"]}','h3')]
        block += [para(f'{chr(65+j)}. {o}') for j,o in enumerate(item['options'])]
        block += [para('જવાબ: __________________________','small'),Spacer(1,9)]
        student.append(KeepTogether(block))
    student += [PageBreak(),para('ક્યાંથી શરૂ કરવું?','h2')]+[para(t) for t in UNIT['routing']]
    for route in UNIT['routes']:
        student += [PageBreak(),para(route['id']+' · '+route['title'],'h2'),para(route['trigger'])]
        student += [para(t) for t in route['paragraphs']]
        student += [para('સાથે ઉકેલીએ','h3'),para(route['worked']['prompt'])]
        student += [para(f'{i+1}. {s}') for i,s in enumerate(route['worked']['steps'])]
        student += [para(route['worked']['math']),para('હવે અભ્યાસ: '+', '.join(route['practice']))]
    for phase,label in [('practice','અભ્યાસ'),('exit','છેલ્લી તપાસ')]:
        student += [PageBreak(),para(label,'h2')]
        for item in [i for i in UNIT['items'] if i['phase']==phase]:
            student.append(KeepTogether([para(item['id']+' · '+item['prompt'],'h3'),
                                        para('જવાબ અને કારણ: __________________________________________','small'),Spacer(1,24)]))
    write_pdf('unit01-student-print.pdf',student+attribution())
    answers=title('ઉકેલ અને પ્રતિસાદ')+[para('પહેલાં બાળકને પોતે વિચારવા દો. જવાબ સાથે કારણ પણ સાંભળો.')]
    for item in UNIT['items']:
        block=[para(item['id']+' · '+item['prompt'],'h3'),para('જવાબ: '+item['answer'])]
        block += [para(f'{i+1}. {s}') for i,s in enumerate(item['steps'])]
        block += [para(o+': '+f,'small') for o,f in item.get('feedback',{}).items()]
        block += [para('વધુ મદદ: '+item['route']+' (વિદ્યાર્થી પાનું).','small'),Spacer(1,12)]
        answers.append(KeepTogether(block))
    answers += [PageBreak(),para('મૂળ ઉદાહરણો માટે વધારાની સમજ','h2')]
    for w in UNIT['source_worked_companion']:
        answers.append(KeepTogether([para(w['title'],'h3'),para('સ્રોત ઓળખ: '+w['source_exercise'],'small')]
                                   +[para(f'{i+1}. {s}') for i,s in enumerate(w['steps'])]+[para(w['answer'])]))
    write_pdf('unit01-teacher-print.pdf',answers+attribution())


if __name__ == '__main__':build()
