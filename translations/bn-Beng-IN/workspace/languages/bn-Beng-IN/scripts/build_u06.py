"""Build the original/adapted decimals, fractions and equations companion."""
import html,json,re,xml.etree.ElementTree as ET
from decimal import Decimal as D,ROUND_HALF_UP
from fractions import Fraction as F
import build
from qa import Page
from build_u03 import fraction as frac,number as num,row

L=build.LANG

def main():
    source=L/'translations/U06-companion.md'
    md=source.read_text(encoding='utf-8')
    q,key=md.split('## A —',1);key=key.split('## R —',1)[0]
    questions=dict(re.findall(r'^\d+\. ([PE]\d)\. (.*)$',q,re.M))
    answers=dict(re.findall(r'\b([PE]\d)\.\s*(.*?)(?=\b[PE]\d\.|\Z)',key,re.S))
    assert set(questions)==set(answers)=={c+str(i) for c in 'PE' for i in range(1,7)}
    expected={
        'P1':('4.099','চার দশমিক শূন্য নয় নয়; একক 4, দশাংশ 0, শতাংশ 9, সহস্রাংশ 9'),
        'P2':('0.375','375/1000 = 3/8'),'P3':('0.46 এবং 0.406','0.460 > 0.406'),
        'P4':('3.748','3.75'),'P5':('x + 3/5 = 1','x = 2/5 = 0.4'),
        'P6':('20.00 ডলার থেকে 13.46 ডলার','6.54 ডলার'),
        'E1':('10.023','দশ দশমিক শূন্য দুই তিন; দশাংশ 0'),
        'E2':('0.625','625/1000 = 5/8'),'E3':('−0.63 এবং −0.6','−0.63 < −0.6'),
        'E4':('6.995','7.00'),'E5':('y − 1/4 = 1/2','y = 3/4 = 0.75'),
        'E6':('12.30 ডলার থেকে 8.75 ডলার','3.55 ডলার')}
    for label,(prompt,answer) in expected.items():
        assert prompt in questions[label] and answer in answers[label],label
    assert len(re.findall(r'^## W\d —',md,re.M))==7

    exact=[
        (F(375,1000),F(3,8)),(F(625,1000),F(5,8)),(F(25,100),F(1,4)),
        (F(375,1000),F(3,8)),(F(340,100),F(34,10)),(F(2,5),F(4,10)),
        (F(3,4),F(75,100)),(F(3,5),F(6,10)),(F(1)-F(3,5),F(2,5)),
        (F(1,2)+F(1,4),F(3,4)),(F(20)-F(1346,100),F(654,100)),
        (F(1230,100)-F(875,100),F(355,100)),(F(1346,100)+F(654,100),F(20)),
        (F(875,100)+F(355,100),F(1230,100)),(F(4,10)+F(6,10),F(1)),
        (F(3,4)-F(1,4),F(1,2))]
    assert all(a==b for a,b in exact)
    comparisons=[D('0.460')>D('0.406'),D('-0.63')<D('-0.60'),D('3.40')==D('3.4'),D('4.099')!=D('4.99')]
    assert all(comparisons)
    rounding={'3.748':'3.75','6.995':'7.00','2.724':'2.72','2.725':'2.73','9.999':'10.00','0.004':'0.00','0.005':'0.01'}
    for value,want in rounding.items():assert format(D(value).quantize(D('0.01'),rounding=ROUND_HALF_UP),'f')==want
    assert D('-1.25').quantize(D('0.1'),rounding=ROUND_HALF_UP)==D('-1.3')
    worked=[
        '10.023 পড়ি “দশ দশমিক শূন্য দুই তিন”','0.375 = 375/1000','3.40 = 3 + 40/100 = 3 + 2/5 = 3.4',
        '1/4 = 25/100 = 0.25','0.460 > 0.406','−0.63 < −0.60','3.748-কে নিকটতম শতাংশ',
        '6.995-কে নিকটতম শতাংশ','2/5 + 3/5 = 5/5 = 1','13.46 + 6.54 = 20.00']
    assert all(text in q for text in worked)
    for text in ['সাময়িক সম্পাদকীয় পথনির্দেশ','পৃ. 57-এর ভুল 12.74 ছকটি ব্যবহার করা হয়নি','প্রত্যয়িত পরীক্ষা',
                 'ভগ্নাংশকে লঘিষ্ঠ আকারে লেখার পর হরের মৌলিক গুণনীয়ক শুধু 2 ও/বা 5 হলে',
                 'দশমিক বিন্দুর ডান দিকে কেবল শূন্য থাকা 3.0-এর মান পূর্ণসংখ্যা 3',
                 'পুনরাবৃত্ত দশমিকের আলাদা পাঠ নেওয়া হচ্ছে না']:
        assert text in md,text

    body=build.render_markdown(md)
    displays=[
        ('সূত্র: 0.375 = 375/1000 = 3/8।',num('0.375')+'<mo>=</mo>'+frac(num(375),num(1000))+'<mo>=</mo>'+frac(num(3),num(8)),'শূন্য দশমিক তিন সাত পাঁচ সমান, লব ৩৭৫ ও হর ১০০০-এর ভগ্নাংশ; সমান, লব ৩ ও হর ৮-এর ভগ্নাংশ।'),
        ('সূত্র: x = 1 − 3/5 = 2/5 = 0.4।','<mi>x</mi><mo>=</mo>'+num(1)+'<mo>−</mo>'+frac(num(3),num(5))+'<mo>=</mo>'+frac(num(2),num(5))+'<mo>=</mo>'+num('0.4'),'এক্স সমান ১ বিয়োগ তিন-পঞ্চমাংশ; সমান দুই-পঞ্চমাংশ; সমান শূন্য দশমিক চার।'),
        ('সূত্র: 20.00 − 13.46 = 6.54।',num('20.00')+'<mo>−</mo>'+num('13.46')+'<mo>=</mo>'+num('6.54'),'বিশ দশমিক শূন্য শূন্য বিয়োগ তেরো দশমিক চার ছয়; সমান ছয় দশমিক পাঁচ চার।')]
    for plain,formula,label in displays:
        math='<math xmlns="'+build.M+'" display="block" aria-label="'+html.escape(label,quote=True)+'"><mrow>'+formula+'</mrow></math>'
        ET.fromstring(math);old='<p>'+html.escape(plain)+'</p>';assert body.count(old)==1
        body=body.replace(old,'<div class="companion-formula">'+math+'</div>')
    trace='<footer><p><a href="modules/m81291.html">উৎস-অনুগত ভগ্নাংশযুক্ত সমীকরণের পাঠ</a> · <a href="modules/m81293.html">উৎস-অনুগত দশমিক পাঠ</a> · <a href="../canon/U06-consultations.json">U06 পরামর্শ-নথি</a> · <a href="U05-companion.html">আগের সহায়িকা U05</a> · <a href="index.html">পাঠসূচি</a>।</p><p>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অভিযোজন; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</p></footer>'
    content=build.page('U06 · দশমিক, ভগ্নাংশ ও সমীকরণ',body+trace).replace('</style>','.companion-formula{padding:16px 0;margin:16px 0;background:#eff8f4}.companion-formula math{font-size:1.3em}</style>')
    output=L/'reader/U06-companion.html';output.write_text(content,encoding='utf-8')
    page=Page();page.feed(content)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        else:assert (output.parent/href).is_file(),href
    canon=L/'canon/U06-consultations.json';assert len(json.loads(canon.read_text(encoding='utf-8'))['consultations'])==3
    receipt={'result':'pass','unit':'U06','kind':'separate original/adapted AX-3 companion',
        'inputs':{p.relative_to(L).as_posix():build.sha(p) for p in [source,canon,L/'scripts/build_u06.py',L/'scripts/build_u03.py',L/'scripts/build.py']},
        'reader':'reader/U06-companion.html','reader_sha256':build.sha(output),'placement':6,'worked_examples':7,'exit_items':6,
        'actual_answer_key_regressions':len(expected),'exact_rational_checks':len(exact),'decimal_comparison_checks':len(comparisons),
        'decimal_rounding_checks':len(rounding)+1,'worked_text_regressions':len(worked),'original_mathml_displays':len(displays),
        'source_trace':{'modules':{'m81291':build.sha(build.module_source('m81291')),'m81293':build.sha(build.module_source('m81293'))},'content':'equation solving/checking plus decimal naming, conversion, order and rounding'},
        'visual_review':'qa/U06-visual-review.md; all 6 desktop tiles and 2 narrow endpoints on exact reader bytes',
        'independent_teacher_language_review':'pending','learner_and_assistive_technology_review':'pending','routing_validation':'pending; no validated score thresholds claimed'}
    (L/'qa/U06-companion.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['unit','result','actual_answer_key_regressions','exact_rational_checks','decimal_rounding_checks','worked_text_regressions']}))

if __name__=='__main__':main()
