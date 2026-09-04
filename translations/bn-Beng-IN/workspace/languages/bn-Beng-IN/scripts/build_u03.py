"""Build the separate U03 companion; verify authored keys and display equations."""
import html,json,re,xml.etree.ElementTree as ET
from fractions import Fraction as F
import build
from qa import Page

L=build.LANG

def fraction(top,bottom):
    return '<mfrac>'+top+bottom+'</mfrac>'

def number(n):return '<mn>'+str(n)+'</mn>'
def row(s):return '<mrow>'+s+'</mrow>'

def main():
    source=L/'translations/U03-companion.md'
    md=source.read_text(encoding='utf-8')
    assert len(re.findall(r'^\d+\. P\d\.',md,re.M))==6
    assert len(re.findall(r'^\d+\. E\d\.',md,re.M))==6
    assert len(re.findall(r'^## W\d —',md,re.M))==7
    q=md.split('## A —')[0];key=md.split('## A —')[1].split('## R —')[0]
    cases=[
        ('P1','2 1/3','P1. 7/3',2+F(1,3),F(7,3)),
        ('P2','9/4','P2. 2 1/4',F(9,4),2+F(1,4)),
        ('P3','2/5 ÷ 3/10','20/15 = 4/3',F(2,5)/F(3,10),F(4,3)),
        ('P4','(3 + 5)/4','P4. 2',F(3+5,4),F(2)),
        ('P5','−1 1/2','P5. −3/2',-(1+F(1,2)),F(-3,2)),
        ('P6','(1/2)/(3/4)','1/2 × 4/3 = 2/3',F(1,2)/F(3,4),F(2,3)),
        ('E1','1 1/2 × 2 2/5','18/5 = 3 3/5',(1+F(1,2))*(2+F(2,5)),F(18,5)),
        ('E2','3 3/4 ÷ 1 1/4','15/4 × 4/5 = 3',(3+F(3,4))/(1+F(1,4)),F(3)),
        ('E3','(−2 1/3) × 3/7','E3. (−7/3) × 3/7 = −1',-(2+F(1,3))*F(3,7),F(-1)),
        ('E4','2 ও 5-এর যোগফলকে 4 দিয়ে','E4. (2 + 5)/4 = 7/4',F(2+5,4),F(7,4)),
        ('E5','(5/6)/(10/9)','45/60 = 3/4',F(5,6)/F(10,9),F(3,4)),
        ('E6','(8 + 4)/(7 − 3)','12/4 = 3',F(8+4,7-3),F(3))]
    for label,question,answer,actual,expected in cases:
        question_line=next(line for line in q.splitlines() if re.match(r'^\d+\. '+label+r'\. ',line))
        assert question in question_line and answer in key and actual==expected,label
    worked=[(1+F(3,4),F(7,4)),(2+F(2,3),F(8,3)),(F(7,4)*F(8,3),F(14,3)),
        (2+F(1,4),F(9,4)),(1+F(1,2),F(3,2)),(F(9,4)/F(3,2),F(3,2)),
        (F(3,2)*F(3,2),F(9,4)),(-(1+F(2,3)),F(-5,3)),(F(-5,3)*F(3,10),F(-1,2)),
        (F(4+7,3),F(11,3)),(4+F(7,3),F(19,3)),(F(3,5)/F(9,10),F(2,3)),
        (F(2,3)*F(9,10),F(3,5)),(F(2+3,8-6),F(5,2)),(3*F(5,4),F(15,4))]
    assert all(a==b for a,b in worked)
    worked_regressions=[
        '1 3/4 = (1 × 4 + 3)/4 = 7/4','2 2/3 = (2 × 3 + 2)/3 = 8/3',
        '7/4 × 8/3 = 56/12 = 14/3 = 4 2/3','2 1/4 = 9/4','1 1/2 = 3/2',
        '9/4 ÷ 3/2 = 9/4 × 2/3 = 18/12 = 3/2 = 1 1/2','3/2 × 3/2 = 9/4',
        '−(1 + 2/3) = −5/3','(−5/3) × 3/10 = −15/30 = −1/2',
        '(4 + 7)/3 = 11/3','4 + 7/3 = 12/3 + 7/3 = 19/3',
        '3/5 ÷ 9/10 = 3/5 × 10/9 = 30/45 = 2/3','2/3 × 9/10 = 18/30 = 3/5',
        '(2 + 3)/(8 − 6) = 5/2','3 × 5/4 = 15/4',
        '(x/3)/(xy/9) = x/3 × 9/(xy) = 3/y']
    assert all(s in md for s in worked_regressions),'Authored worked-step regression'
    # Exact monomial cancellation: x/3 * 9/(xy) = 3/y under x*y != 0.
    assert F(9,3)==3 and (1-1,0-1)==(0,-1)
    assert all(s in md for s in ['x ≠ 0','y ≠ 0','0/0—সংজ্ঞায়িত নয়','সাময়িক সম্পাদকীয় প্রস্তাব'])
    f=fraction;n=number
    diagrams=[
        ('সূত্র: (3/5)/(9/10) = 2/3।',f(f(n(3),n(5)),f(n(9),n(10)))+'<mo>=</mo>'+f(n(2),n(3)),
         'প্রধান লবে তিন-পঞ্চমাংশ এবং প্রধান হরে নয়-দশমাংশ; পুরো ভগ্নাংশের মান দুই-তৃতীয়াংশ।'),
        ('সূত্র: (2 + 3)/(8 − 6) = 5/2।',f(row(n(2)+'<mo>+</mo>'+n(3)),row(n(8)+'<mo>−</mo>'+n(6)))+'<mo>=</mo>'+f(n(5),n(2)),
         'লবে দুই যোগ তিন এবং হরে আট বিয়োগ ছয়; পুরো ভগ্নাংশের মান পাঁচ-দ্বিতীয়াংশ।'),
        ('সূত্র: (x/3)/(xy/9) = 3/y।',f(f('<mi>x</mi>',n(3)),f(row('<mi>x</mi><mi>y</mi>'),n(9)))+'<mo>=</mo>'+f(n(3),'<mi>y</mi>'),
         'প্রধান লব x ভাগ তিন এবং প্রধান হর x গুণ y ভাগ নয়; x ও y শূন্য নয় হলে মান তিন ভাগ y।')]
    body=build.render_markdown(md)
    for plain,formula,label in diagrams:
        old='<p>'+html.escape(plain)+'</p>';assert body.count(old)==1
        math='<math xmlns="'+build.M+'" display="block" aria-label="'+html.escape(label,quote=True)+'"><mrow>'+formula+'</mrow></math>'
        ET.fromstring(math)
        body=body.replace(old,'<div class="companion-formula">'+math+'</div>')
    trace='<footer><p>উৎস-অনুগত পূর্ণ পাঠ: <a href="modules/m81287.html">মিশ্র ভগ্নাংশ, জটিল ভগ্নাংশ ও ভগ্নাংশ-রেখা</a>। <a href="U02-companion.html">আগের সহায়িকা U02</a> · <a href="index.html">পাঠসূচি</a>।</p><p>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অভিযোজন; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</p></footer>'
    content=build.page('U03 · মিশ্র ভগ্নাংশ ও ভগ্নাংশ-রেখা',body+trace).replace('</style>','.companion-formula{padding:16px 0;margin:16px 0;background:#eff8f4}.companion-formula math{font-size:1.3em}</style>')
    output=L/'reader/U03-companion.html';output.write_text(content,encoding='utf-8')
    page=Page();page.feed(content)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        else:assert (output.parent/href).is_file(),href
    canon=L/'canon/U03-consultations.json'
    assert len(json.loads(canon.read_text(encoding='utf-8'))['consultations'])>=3
    receipt={'result':'pass','unit':'U03','kind':'separate original/adapted AX-3 companion',
        'inputs':{p.relative_to(L).as_posix():build.sha(p) for p in [source,canon,L/'scripts/build_u03.py',L/'scripts/build.py']},
        'reader':'reader/U03-companion.html','reader_sha256':build.sha(output),'placement':6,'worked_examples':7,'exit_items':6,
        'actual_answer_key_regressions':len(cases),'actual_worked_step_regressions':len(worked_regressions),'rational_checks':len(cases)+len(worked),'exact_symbolic_monomial_checks':1,
        'original_mathml_displays':3,'source_trace_sections':4,'visual_review':'pending','independent_teacher_language_review':'pending',
        'learner_and_assistive_technology_review':'pending','routing_validation':'pending; no validated score thresholds claimed'}
    (L/'qa/U03-companion.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['unit','result','rational_checks','actual_answer_key_regressions','placement','worked_examples','exit_items']}))

if __name__=='__main__':main()
