"""Build and verify the explicitly authored U02 AX-3 companion."""
import json,re
from fractions import Fraction as F
import build
from qa import Page

L=build.LANG

def main():
    source=L/'translations/U02-companion.md'
    md=source.read_text(encoding='utf-8')
    assert len(re.findall(r'^\d+\. P\d\.',md,re.M))==6
    assert len(re.findall(r'^\d+\. E\d\.',md,re.M))==6
    assert len(re.findall(r'^## W\d —',md,re.M))==7
    q=md.split('## A —')[0];key=md.split('## A —')[1].split('## R —')[0]
    cases=[
        ('P1','6/8','P1. 3/4',F(6,8),F(3,4)),
        ('P2','2/3','P2. 8/12',F(2,3),F(8,12)),
        ('P3','3/5 × 10/9','P3. 30/45 = 2/3',F(3,5)*F(10,9),F(2,3)),
        ('P4','2/7','P4. 7/2',1/F(2,7),F(7,2)),
        ('P5','3/4 ÷ 1/2','P5. 3/4 × 2/1 = 3/2',F(3,4)/F(1,2),F(3,2)),
        ('P6','(−2/3) × 3/4','−6/12 = −1/2',F(-2,3)*F(3,4),F(-1,2)),
        ('E1','42/56','E1. 3/4',F(42,56),F(3,4)),
        ('E2','5/12 × 8/15','E2. 40/180 = 2/9',F(5,12)*F(8,15),F(2,9)),
        ('E3','−7/9','E3. −9/7',1/F(-7,9),F(-9,7)),
        ('E4','7/10 ÷ 14/15','105/140 = 3/4',F(7,10)/F(14,15),F(3,4)),
        ('E5','(−4/9) ÷ 2/3','−12/18 = −2/3',F(-4,9)/F(2,3),F(-2,3)),
        ('E6','3/2 × 4/5 = 6/5','10/12 = 5/6',F(2,3)/F(4,5),F(5,6))]
    for label,question,answer,actual,expected in cases:
        assert question in q and answer in key and actual==expected,label
    worked=[(F(30,36),F(5,6)),(F(2,3)*F(9,10),F(3,5)),(F(3,8)*F(4,9),F(1,6)),
            (F(4,7)*F(7,4),F(1)),(F(-3,5)*F(-5,3),F(1)),(F(3,4)/F(2,5),F(15,8)),
            (F(15,8)*F(2,5),F(3,4)),(F(-5,6)/F(5,12),F(-2)),(F(-2)*F(5,12),F(-5,6)),
            (F(-2,3)*F(2,3),F(-4,9)),(F(3,2)*F(4,5),F(6,5))]
    assert all(a==b for a,b in worked)
    assert 'শূন্যের গুণাত্মক বিপরীত নেই' in md and 'প্রথম ভগ্নাংশটিকে উল্টে দিও না' in md
    assert 'সাময়িক সম্পাদকীয় প্রস্তাব' in md and '1 ছাড়া' in md
    trace='<footer><p>উৎস-অনুগত মডিউলের পৃথক পাঠ: <a href="sections/m81286-fs-id1408851.html">লঘিষ্ঠ আকার</a> · <a href="sections/m81286-fs-id2081411.html">গুণ</a> · <a href="sections/m81286-fs-id1390478.html">গুণাত্মক বিপরীত</a> · <a href="sections/m81286-fs-id2700526.html">ভাগ</a>। <a href="index.html">পাঠসূচি</a>।</p><p>OpenStax, Rice University · Prealgebra 2e · Lynn Marecek, MaryAnne Anthony-Smith, Andrea Honeycutt Mathis। <a href="../provenance/pilot/m81241.source.cnxml">পূর্ণ উৎস-স্বীকৃতি</a> · <a href="../provenance/A00/repository/LICENSE">CC BY-NC-SA 4.0 ও উপাদানভিত্তিক শর্ত</a>। অনানুষ্ঠানিক বাংলা অভিযোজন; মূল প্রকাশকের অনুমোদন দাবি করা হচ্ছে না।</p></footer>'
    output=L/'reader/U02-companion.html'
    content=build.page('U02 · ভগ্নাংশের লঘিষ্ঠ আকার, গুণ ও ভাগ',build.render_markdown(md)+trace)
    output.write_text(content,encoding='utf-8')
    before=build.sha(output);output.write_text(content,encoding='utf-8');assert before==build.sha(output)
    page=Page();page.feed(content)
    assert page.lang=='bn-Beng-IN' and not page.scripts and len(page.ids)==len(set(page.ids))
    for href in page.links:
        if href.startswith('#'):assert href[1:] in page.ids
        else:assert (output.parent/href).is_file(),href
    canon=L/'canon/U02-consultations.json'
    assert len(json.loads(canon.read_text(encoding='utf-8'))['consultations'])>=3
    receipt={'result':'pass','unit':'U02','kind':'separate original/adapted AX-3 companion',
             'inputs':{p.relative_to(L).as_posix():build.sha(p) for p in [source,canon,L/'scripts/build_companions.py',L/'scripts/build.py']},
             'reader':'reader/U02-companion.html','reader_sha256':build.sha(output),'placement':6,'worked_examples':7,'exit_items':6,
             'actual_answer_key_regressions':len(cases),'rational_checks':len(cases)+len(worked),'source_trace_sections':4,
             'deterministic_rebuild':'byte-identical','visual_review':'pending','independent_teacher_language_review':'pending',
             'learner_and_assistive_technology_review':'pending','routing_validation':'pending; no validated score thresholds claimed'}
    (L/'qa/U02-companion.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ['unit','result','rational_checks','actual_answer_key_regressions','placement','worked_examples','exit_items']}))

def build_all():
    main()
    import build_u03
    build_u03.main()
    import build_u04
    build_u04.main()
    import build_u05
    build_u05.main()
    import build_u06
    build_u06.main()

if __name__=='__main__':build_all()
