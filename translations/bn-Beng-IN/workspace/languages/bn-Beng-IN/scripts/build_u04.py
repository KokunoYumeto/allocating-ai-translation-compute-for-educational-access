"""Build U04 and check its authored questions, answers and worked expressions."""
import html,json,re,xml.etree.ElementTree as ET
from fractions import Fraction as F
from math import lcm
import build
from qa import Page
from build_u03 import fraction as frac,number as num,row

L=build.LANG

def main():
    source=L/'translations/U04-companion.md'
    md=source.read_text(encoding='utf-8')
    q,key=md.split('## A —',1);key=key.split('## R —',1)[0]
    questions=dict(re.findall(r'^\d+\. ([PE]\d)\. (.*)$',q,re.M))
    answers=dict(re.findall(r'\b([PE]\d)\.\s*(.*?)(?=\b[PE]\d\.|\Z)',key,re.S))
    assert set(questions)==set(answers)=={c+str(i) for c in 'PE' for i in range(1,7)}
    expected={
        'P1':('3/8 + 2/8','5/8'),
        'P2':('7/9 − 4/9','3/9 = 1/3'),
        'P3':('6 ও 8','24'),
        'P4':('2/3 = ?/12','2/3 = 8/12'),
        'P5':('−5/7 + 2/7','−3/7'),
        'P6':('1/2 × 1/3','গুণফল 1/6, যোগফল 3/6 + 2/6 = 5/6'),
        'E1':('4/9 + 2/9','6/9 = 2/3'),
        'E2':('5/6 − 1/4','10/12 − 3/12 = 7/12'),
        'E3':('−3/8 + 1/6','−9/24 + 4/24 = −5/24'),
        'E4':('3/10 ও 7/15','3/10 = 9/30 এবং 7/15 = 14/30, যোগফল 23/30'),
        'E5':('3/4 + 1/2 = (3 + 1)/(4 + 2)','3/4 + 2/4 = 5/4'),
        'E6':('(2/3 − 1/6)/(1/2 + 1/4)','1/2 × 4/3 = 2/3')}
    for label,(prompt,answer) in expected.items():
        assert prompt in questions[label] and answer in answers[label],label
    assert '3/8' in answers['E5']
    assert len(re.findall(r'^## W\d —',md,re.M))==7
    checks=[
        (F(3,8)+F(2,8),F(5,8)),(F(7,9)-F(4,9),F(1,3)),(F(2,3),F(8,12)),
        (F(-5,7)+F(2,7),F(-3,7)),(F(1,2)*F(1,3),F(1,6)),(F(1,2)+F(1,3),F(5,6)),
        (F(4,9)+F(2,9),F(2,3)),(F(5,6)-F(1,4),F(7,12)),(F(-3,8)+F(1,6),F(-5,24)),
        (F(3,10),F(9,30)),(F(7,15),F(14,30)),(F(3,10)+F(7,15),F(23,30)),
        (F(3,4)+F(1,2),F(5,4)),(F(3,4)*F(1,2),F(3,8)),
        ((F(2,3)-F(1,6))/(F(1,2)+F(1,4)),F(2,3)),(F(7,12)+F(1,4),F(5,6))]
    worked=[
        ('3/10 + 4/10 = 7/10',F(3,10)+F(4,10),F(7,10)),
        ('7/10 − 3/10 = 4/10 = 2/5',F(7,10)-F(3,10),F(2,5)),
        ('5/6 = (5 × 4)/(6 × 4) = 20/24',F(5,6),F(20,24)),
        ('3/8 = (3 × 3)/(8 × 3) = 9/24',F(3,8),F(9,24)),
        ('20/24 + 9/24 = 29/24 = 1 5/24',F(20,24)+F(9,24),1+F(5,24)),
        ('40/48 + 18/48 = 58/48 = 29/24',F(40,48)+F(18,48),F(29,24)),
        ('7/12 = 21/36',F(7,12),F(21,36)),('5/18 = 10/36',F(5,18),F(10,36)),
        ('7/12 − 5/18 = 21/36 − 10/36 = 11/36',F(7,12)-F(5,18),F(11,36)),
        ('11/36 + 5/18 = 11/36 + 10/36 = 21/36 = 7/12',F(11,36)+F(5,18),F(7,12)),
        ('−2/3 = −8/12',F(-2,3),F(-8,12)),('1/4 = 3/12',F(1,4),F(3,12)),
        ('−2/3 + 1/4 = (−8 + 3)/12 = −5/12',F(-2,3)+F(1,4),F(-5,12)),
        ('2/5 + 1/3 = 6/15 + 5/15 = 11/15',F(2,5)+F(1,3),F(11,15)),
        ('2/5 × 1/3 = 2/15',F(2,5)*F(1,3),F(2,15)),
        ('2/5 ÷ 1/3 = 2/5 × 3/1 = 6/5',F(2,5)/F(1,3),F(6,5)),
        ('3/6 + 2/6 = 5/6',F(3,6)+F(2,6),F(5,6)),('2/4 = 1/2',F(2,4),F(1,2)),
        ('(5/6)/(1/2) = 5/6 × 2/1 = 5/3 = 1 2/3',F(5,6)/F(1,2),1+F(2,3)),
        ('−2/4 + (−6)/8 = −1/2 − 3/4 = −5/4',F(-2,4)+F(-6,8),F(-5,4)),
        ('−10/8 = −5/4',F(-10,8),F(-5,4))]
    for text,actual,result in worked:
        assert text in q and actual==result,text
    assert all(a==b for a,b in checks)
    lcms=[(6,8,24),(12,18,36),(10,15,30)]
    assert all(lcm(a,b)==d for a,b,d in lcms)
    # Literal displayed denominators are checked separately from reduced equality.
    for text in ['20/24','9/24','21/36','10/36','9/30','14/30']:
        assert text in md
    # Exact polynomial coefficients, not a finite-substitution proof.
    assert F(1,4)+F(3,8)==F(5,8)
    assert (F(1,4),F(1,8))==(F(2,8),F(1,8))
    assert all(t in q for t in ['x/4 + 3x/8 = (2x + 3x)/8 = 5x/8','x/4 + 1/8 = (2x + 1)/8','x শূন্য হলেও রাশি সংজ্ঞায়িত থাকে'])
    assert F(3,4)-F(3,4)==0
    assert 'ভাজক শূন্য হলে ভাগ করা যায় না' in md and 'সাময়িক সম্পাদকীয় পথনির্দেশ' in md
    body=build.render_markdown(md)
    plain='সূত্র: (1/2 + 1/3)/(3/4 − 1/4) = 5/3।'
    formula=frac(row(frac(num(1),num(2))+'<mo>+</mo>'+frac(num(1),num(3))),row(frac(num(3),num(4))+'<mo>−</mo>'+frac(num(1),num(4))))+'<mo>=</mo>'+frac(num(5),num(3))
    label='প্রধান লবে এক-দ্বিতীয়াংশ যোগ এক-তৃতীয়াংশ; প্রধান হরে তিন-চতুর্থাংশ বিয়োগ এক-চতুর্থাংশ। পুরো ভগ্নাংশের মান পাঁচ-তৃতীয়াংশ।'
    math='<math xmlns="'+build.M+'" display="block" aria-label="'+html.escape(label,quote=True)+'"><mrow>'+formula+'</mrow></math>'
    ET.fromstring(math)
    old='<p>'+html.escape(plain)+'</p>';assert body.count(old)==1
    body=body.replace(old,'<div class="companion-formula">'+math+'</div>')
    trace='<footer><p>উৎস-অনুগত পূর্ণ পাঠ: <a href="modules/m81288.html">একই হরের যোগ-বিয়োগ</a> · <a href="modules/m81289.html">আলাদা হরের যোগ-বিয়োগ ও প্রক্রিয়া</a>। <a href="U03-companion.html">আগের সহায়িকা U03</a> · <a href="index.html">পাঠসূচি</a>।</p><p>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অভিযোজন; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</p></footer>'
    content=build.page('U04 · ভগ্নাংশের যোগ ও বিয়োগ',body+trace).replace('</style>','.companion-formula{padding:16px 0;margin:16px 0;background:#eff8f4}.companion-formula math{font-size:1.3em}</style>')
    output=L/'reader/U04-companion.html';output.write_text(content,encoding='utf-8')
    page=Page();page.feed(content)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        else:assert (output.parent/href).is_file(),href
    canon=L/'canon/U04-consultations.json'
    assert len(json.loads(canon.read_text(encoding='utf-8'))['consultations'])>=3
    receipt={'result':'pass','unit':'U04','kind':'separate original/adapted AX-3 companion',
        'inputs':{p.relative_to(L).as_posix():build.sha(p) for p in [source,canon,L/'scripts/build_u04.py',L/'scripts/build_u03.py',L/'scripts/build.py']},
        'reader':'reader/U04-companion.html','reader_sha256':build.sha(output),'placement':6,'worked_examples':7,'exit_items':6,
        'actual_answer_key_regressions':len(expected),'actual_worked_step_regressions':len(worked),
        'rational_checks':len(checks)+len(worked),'exact_lcm_checks':len(lcms),'exact_symbolic_coefficient_checks':2,
        'original_mathml_displays':1,'source_trace_sections':10,'visual_review':'pending',
        'independent_teacher_language_review':'pending','learner_and_assistive_technology_review':'pending',
        'routing_validation':'pending; no validated score thresholds claimed'}
    (L/'qa/U04-companion.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['unit','result','rational_checks','actual_answer_key_regressions','exact_lcm_checks']}))

if __name__=='__main__':main()
