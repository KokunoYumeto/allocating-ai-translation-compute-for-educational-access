"""Build the original/adapted mixed-number companion with exact text/math checks."""
import html,json,re,xml.etree.ElementTree as ET
from fractions import Fraction as F
from math import lcm
import build
from qa import Page
from build_u03 import fraction as frac,number as num,row

L=build.LANG

def main():
    source=L/'translations/U05-companion.md'
    md=source.read_text(encoding='utf-8')
    q,key=md.split('## A —',1);key=key.split('## R —',1)[0]
    questions=dict(re.findall(r'^\d+\. ([PE]\d)\. (.*)$',q,re.M))
    answers=dict(re.findall(r'\b([PE]\d)\.\s*(.*?)(?=\b[PE]\d\.|\Z)',key,re.S))
    assert set(questions)==set(answers)=={c+str(i) for c in 'PE' for i in range(1,7)}
    expected={
        'P1':('2 3/4','11/4'),'P2':('1 + 2/5','5/5 + 2/5 = 7/5'),
        'P3':('4/6 + 5/6','9/6 = 1 + 3/6 = 1 1/2'),'P4':('5 = 4 + ?/8','4 + 8/8 = 5'),
        'P5':('1/2 + 1/3','3/6 + 2/6 = 5/6'),'P6':('−(1 + 1/4) এবং −1 + 1/4','প্রথমটি −5/4, দ্বিতীয়টি −3/4'),
        'E1':('2 3/5 + 1 4/5','3 + 7/5 = 4 2/5'),
        'E2':('6 − 2 2/3','(5 + 3/3) − (2 + 2/3) = 3 1/3'),
        'E3':('4 1/5 − 1 4/5','21/5 − 9/5 = 12/5 = 2 2/5'),
        'E4':('1 3/4 + 2 5/6','3 + 9/12 + 10/12 = 4 7/12'),
        'E5':('3 1/6 − 1 3/4','19/6 − 7/4 = 38/12 − 21/12 = 17/12'),
        'E6':('1 1/2 − 3 1/4','6/4 − 13/4 = −7/4 = −(1 + 3/4)')}
    for label,(prompt,answer) in expected.items():
        assert prompt in questions[label] and answer in answers[label],label
    assert len(re.findall(r'^## W\d —',md,re.M))==7
    checks=[
        (2+F(3,4),F(11,4)),(1+F(2,5),F(7,5)),(F(4,6)+F(5,6),1+F(1,2)),(4+F(8,8),5),
        (F(1,2)+F(1,3),F(5,6)),(-(1+F(1,4)),F(-5,4)),(-1+F(1,4),F(-3,4)),
        (2+F(3,5)+1+F(4,5),4+F(2,5)),(6-(2+F(2,3)),3+F(1,3)),
        (4+F(1,5)-(1+F(4,5)),2+F(2,5)),(F(21,5)-F(9,5),F(12,5)),
        (1+F(3,4)+2+F(5,6),4+F(7,12)),(3+F(1,6)-(1+F(3,4)),1+F(5,12)),
        (F(19,6)-F(7,4),F(17,12)),(1+F(1,2)-(3+F(1,4)),-(1+F(3,4))),
        (F(-7,4)+F(13,4),1+F(1,2))]
    worked=[
        ('2 3/4 = 2 + 3/4 = 8/4 + 3/4 = 11/4',2+F(3,4),F(11,4)),
        ('1 1/4 + 2 1/4 = 3 + 2/4 = 3 1/2',1+F(1,4)+2+F(1,4),3+F(1,2)),
        ('2/3 = 4/6',F(2,3),F(4,6)),('4/6 + 5/6 = 9/6',F(4,6)+F(5,6),F(9,6)),
        ('4 + 9/6 = 4 + 1 + 3/6 = 5 1/2',4+F(9,6),5+F(1,2)),
        ('11/3 + 11/6 = 22/6 + 11/6 = 33/6 = 5 1/2',F(11,3)+F(11,6),5+F(1,2)),
        ('2 − 3/5 = 1 + 2/5 = 1 2/5',2-F(3,5),1+F(2,5)),
        ('1 2/5 + 3/5 = 1 + 5/5 = 2',1+F(2,5)+F(3,5),2),
        ('1/4 − 3/4 = −1/2',F(1,4)-F(3,4),F(-1,2)),
        ('5 + 1/4 = 4 + 4/4 + 1/4 = 4 + 5/4',5+F(1,4),4+F(5,4)),
        ('(4 + 5/4) − (2 + 3/4) = 2 + 2/4 = 2 1/2',4+F(5,4)-(2+F(3,4)),2+F(1,2)),
        ('21/4 − 11/4 = 10/4 = 2 1/2',F(21,4)-F(11,4),2+F(1,2)),
        ('5 3/4 − 2 3/4 = 3',5+F(3,4)-(2+F(3,4)),3),
        ('1/6 = 2/12',F(1,6),F(2,12)),('3/4 = 9/12',F(3,4),F(9,12)),
        ('4 + 2/12 = 3 + 14/12',4+F(2,12),3+F(14,12)),
        ('(3 + 14/12) − (1 + 9/12) = 2 + 5/12 = 2 5/12',3+F(14,12)-(1+F(9,12)),2+F(5,12)),
        ('25/6 − 7/4 = 50/12 − 21/12 = 29/12 = 2 5/12',F(25,6)-F(7,4),2+F(5,12)),
        ('7/3 − 19/4 = 28/12 − 57/12 = −29/12',F(7,3)-F(19,4),F(-29,12)),
        ('−29/12 = −(2 + 5/12)',F(-29,12),-(2+F(5,12))),
        ('−2 + 5/12 নয়; সেই আলাদা রাশির মান −19/12',-2+F(5,12),F(-19,12)),
        ('−29/12 + 19/4 = −29/12 + 57/12 = 28/12 = 7/3',F(-29,12)+F(19,4),F(7,3)),
        ('7/2 − 7/4 = 14/4 − 7/4 = 7/4 = 1 3/4',F(7,2)-F(7,4),1+F(3,4)),
        ('1 3/4 + 1 3/4 = 3 1/2',1+F(3,4)+1+F(3,4),3+F(1,2))]
    for text,actual,result in worked:assert text in q and actual==result,text
    assert all(a==b for a,b in checks)
    assert lcm(3,6)==6 and lcm(6,4)==12 and lcm(4,6)==12
    assert -(1+F(1,4))!=-1+F(1,4) and F(-29,12)!=-2+F(5,12)
    for text in ['2/12','9/12','14/12','28/12','57/12','সাময়িক সম্পাদকীয় পথনির্দেশ','কোনো দৈর্ঘ্য নষ্ট হয়নি']:
        assert text in md,text
    body=build.render_markdown(md)
    displays=[
        ('সূত্র: 5 + 1/4 = 4 + 5/4।',num(5)+'<mo>+</mo>'+frac(num(1),num(4))+'<mo>=</mo>'+num(4)+'<mo>+</mo>'+frac(num(5),num(4)),'পাঁচ যোগ এক-চতুর্থাংশ সমান চার যোগ পাঁচ-চতুর্থাংশ; মোট মান অপরিবর্তিত।'),
        ('সূত্র: −29/12 = −(2 + 5/12)।',frac(row('<mo>−</mo>'+num(29)),num(12))+'<mo>=</mo><mo>−</mo><mo>(</mo>'+num(2)+'<mo>+</mo>'+frac(num(5),num(12))+'<mo>)</mo>','ঋণাত্মক ঊনত্রিশ-দ্বাদশাংশ সমান দুই যোগ পাঁচ-দ্বাদশাংশের পুরো পরিমাণের ঋণাত্মক মান।')]
    for plain,formula,label in displays:
        math='<math xmlns="'+build.M+'" display="block" aria-label="'+html.escape(label,quote=True)+'"><mrow>'+formula+'</mrow></math>'
        ET.fromstring(math);old='<p>'+html.escape(plain)+'</p>';assert body.count(old)==1
        body=body.replace(old,'<div class="companion-formula">'+math+'</div>')
    trace='<footer><p><a href="modules/m81290.html">উৎস-অনুগত পূর্ণ মিশ্র-ভগ্নাংশের পাঠ</a> · <a href="U04-companion.html">আগের সহায়িকা U04</a> · <a href="index.html">পাঠসূচি</a>।</p><p>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অভিযোজন; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</p></footer>'
    content=build.page('U05 · মিশ্র ভগ্নাংশের যোগ ও বিয়োগ',body+trace).replace('</style>','.companion-formula{padding:16px 0;margin:16px 0;background:#eff8f4}.companion-formula math{font-size:1.3em}</style>')
    output=L/'reader/U05-companion.html';output.write_text(content,encoding='utf-8')
    page=Page();page.feed(content)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        else:assert (output.parent/href).is_file(),href
    canon=L/'canon/U05-consultations.json'
    assert len(json.loads(canon.read_text(encoding='utf-8'))['consultations'])>=3
    receipt={'result':'pass','unit':'U05','kind':'separate original/adapted AX-3 companion',
        'inputs':{p.relative_to(L).as_posix():build.sha(p) for p in [source,canon,L/'scripts/build_u05.py',L/'scripts/build_u03.py',L/'scripts/build.py']},
        'reader':'reader/U05-companion.html','reader_sha256':build.sha(output),'placement':6,'worked_examples':7,'exit_items':6,
        'actual_answer_key_regressions':len(expected),'actual_worked_step_regressions':len(worked),'rational_checks':len(checks)+len(worked),
        'exact_lcm_checks':3,'negative_sign_contrast_checks':2,'original_mathml_displays':len(displays),
        'source_trace':{'module':'m81290','source_sha256':build.sha(build.module_source('m81290')),'sections':['fs-id1946649','fs-id2833156','fs-id4155624','fs-id1377484','fs-id1752471']},
        'visual_review':'pending','independent_teacher_language_review':'pending','learner_and_assistive_technology_review':'pending',
        'routing_validation':'pending; no validated score thresholds claimed'}
    (L/'qa/U05-companion.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['unit','result','rational_checks','actual_answer_key_regressions','actual_worked_step_regressions']}))

if __name__=='__main__':main()
