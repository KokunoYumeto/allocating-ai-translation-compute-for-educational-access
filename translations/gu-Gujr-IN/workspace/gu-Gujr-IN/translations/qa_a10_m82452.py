"""Independent structural and exact-arithmetic checks for the Gujarati module."""
from pathlib import Path
import xml.etree.ElementTree as E
import hashlib, json, math, re
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82452/index.cnxml'
GU=Path(__file__).with_name('a10-m82452.gu.cnxml')
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
def numbers(text):return [int(x.replace(',','')) for x in re.findall(r'\d[\d,]*',text)]
def flat(e):return ''.join(e.itertext())
def main():
    s=E.parse(SRC).getroot();g=E.parse(GU).getroot();se=list(s.iter());ge=list(g.iter())
    assert [e.tag for e in se]==[e.tag for e in ge]
    assert [e.get('id') for e in se]==[e.get('id') for e in ge]
    for a,b in zip(se,ge):
        for k,v in a.attrib.items():
            if k not in {'alt','aria-label','summary'}:assert b.get(k)==v,(a.get('id'),k)
        if a.tag.startswith('{'+NS['m']+'}') and not a.tag.endswith('mtext'):
            assert a.text==b.text,(a.tag,a.text,b.text)
        for field,value in [('text',b.text),('tail',b.tail),('alt',b.get('alt')),('aria',b.get('aria-label'))]:
            if value and b.tag.rsplit('}',1)[-1] not in {'uuid','content-id'}:
                assert not set(re.findall('[A-Za-z]{2,}',value))-{'LCM'},(b.get('id'),field,value)
    ex={e.get('id'):e for e in s.findall('.//c:exercise',NS)}
    gx={e.get('id'):e for e in g.findall('.//c:exercise',NS)}
    checked=[]
    def supplied(id):return flat(ex[id].find('c:solution',NS)).strip()
    def mark(id,expected):
        assert numbers(supplied(id))==expected,(id,supplied(id),expected)
        assert numbers(flat(gx[id].find('c:solution',NS)))==expected,id
        checked.append(id)
    lcm_ids=['fs-id1170655206433','fs-id1170655206454','fs-id1170655195919','fs-id1170655195940','fs-id1170655222005','fs-id1170655222026','fs-id1170655165800','fs-id1170655165832','fs-id1170655170797','fs-id1170655170833','fs-id1170655170865','fs-id1170655170897']
    for id in lcm_ids:
        a,b=numbers(flat(ex[id].find('c:problem',NS)));mark(id,[math.lcm(a,b)])
    prime_ids=['fs-id1170655219563','fs-id1170655206365','fs-id1170655229693','fs-id1170655270011','fs-id1170655196095','fs-id1170655196146','fs-id1170655209552','fs-id1170655209624','fs-id1170655165701']
    for id in prime_ids:
        n=numbers(flat(ex[id].find('c:problem',NS)))[0];f=numbers(supplied(id))
        assert math.prod(f)==n
        assert all(p>1 and all(p%d for d in range(2,math.isqrt(p)+1))for p in f)
        mark(id,f)
    div_ids=['fs-id1170655196870','fs-id1170655200183','fs-id1170655198403','fs-id1170655198436','fs-id1170655198468','fs-id1170655195988','fs-id1170655196020','fs-id1170655196053']
    for id in div_ids:
        n=numbers(flat(ex[id].find('c:problem',NS)))[0]
        mark(id,[d for d in [2,3,5,6,10]if n%d==0])
    rounds={
        'fs-id1170655207341':([17852],[100]),'fs-id1170655221973':([468751],[100]),
        'fs-id1170655175048':([206981]*3,[100,1000,10000]),
        'fs-id1170655083618':([784951]*3,[100,1000,10000]),
        'fs-id1170655194765':([386,2931],[10,10]),
        'fs-id1170655194803':([13748,391794],[100,100]),
        'fs-id1170655194842':([1492,1497],[10,10]),
        'fs-id1170655194881':([63994,63940],[100,100]),
        'fs-id1170655198328':([392546]*3,[100,1000,10000]),
        'fs-id1170655198360':([2586991]*3,[100,1000,10000]),
        'fs-id1170655194285':([24493]*4,[10,100,1000,10000]),
        'fs-id1170655194330':([1339724852]*3,[10**9,10**8,10**6])}
    for id,(values,places) in rounds.items():mark(id,[((n+p//2)//p)*p for n,p in zip(values,places)])
    mark('fs-id1170655194373',[math.lcm(10,8)])
    # Original incomplete factor list deliberately remains; the correction is separate.
    for a,b in zip(se,ge):
        if a.get('id')=='fs-id1170655223714':
            assert numbers(flat(a))==numbers(flat(b))
    media=[e for e in ge if e.tag.endswith('media')]
    assert len(media)==35 and all(re.search('[\u0a80-\u0aff]',e.get('alt',''))for e in media)
    report={'result':'pass','module':'m82452','elements':len(ge),'source_ids':sum(e.get('id')is not None for e in ge),'exercises':len(ex),'source_solutions':sum(e.find('c:solution',NS)is not None for e in ex.values()),'mathml':len(g.findall('.//m:math',NS)),'translated_media_alt':len(media),'translated_table_aria_labels':sum(e.get('aria-label')is not None for e in ge),'independent_supplied_answer_checks':len(checked),'checked_exercises':checked,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'translation_sha256':hashlib.sha256(GU.read_bytes()).hexdigest()}
    supplements=json.loads(Path(__file__).with_name('a10-m82452-added-solutions.gu.json').read_text(encoding='utf-8'))
    omitted={id for id,e in ex.items() if e.find('c:solution',NS)is None}
    assert supplements['schema']=='gujarati-worked-supplement-v1'
    assert {x['source_exercise']for x in supplements['items']}==omitted
    assert len(supplements['items'])==len(omitted)==41
    for item in supplements['items']:
        assert item['question_gu'].strip() and item['answer'].strip()
        assert len(item['steps'])>=2 and len(set(item['steps']))==len(item['steps'])
        assert all(re.search('[\u0a80-\u0aff]',x) for x in item['steps'])
        c=item['check'];typ=c['type']
        if typ=='place_names':
            ds=str(c['number']); powers=[]
            for digit in c['digits']:
                assert ds.count(str(digit))==1
                powers.append(len(ds)-1-ds.index(str(digit)))
            assert powers==c['powers']
            assert all(label in item['answer']for label in c['labels'])
        elif typ in {'number_words','from_words'}:
            groups=c['groups'];value=sum(v*1000**(len(groups)-1-i)for i,v in enumerate(groups))
            assert value==c.get('number',c.get('result'))
            assert f'{value:,}' in item['answer']
        elif typ=='round':
            results=[((n+p//2)//p)*p for n,p in zip(c['numbers'],c['places'])]
            assert results==c['results']
            assert all(f'{n:,}' in item['answer']for n in results)
        elif typ=='divisibility':
            yes=[d for d in c['divisors']if c['number']%d==0]
            assert yes==c['yes'] and sorted(set(c['yes']+c['no']))==sorted(c['divisors'])
            assert c['digit_sum']==sum(map(int,str(c['number'])))
        elif typ=='prime_factorization':
            assert math.prod(c['factors'])==c['number']
            assert all(p>1 and all(p%d for d in range(2,math.isqrt(p)+1))for p in c['factors'])
        elif typ in {'lcm_listing','lcm_primes'}:
            assert math.lcm(*c['numbers'])==c['result']
            if typ=='lcm_listing':
                assert all(row==list(range(n,c['result']+1,n))for n,row in zip(c['numbers'],c['lists']))
            else:
                assert math.prod(c['lcm_factors'])==c['result']
        elif typ=='packs_lcm':
            assert math.lcm(*c['pack_sizes'])==c['result']
            assert [c['result']//x for x in c['pack_sizes']]==c['packs']
        elif typ=='sample_divisibility_reason':
            assert math.prod(c['divisors'])==c['product'] and c['example']==c['product']*c['cofactor']
        elif typ=='sample_factorization':
            assert math.prod(c['factors'])==c['number'] and c['sample_answer']
        else:raise AssertionError(typ)
    report['source_omitted_answer_count']=len(omitted)
    report['independent_added_solution_checks']=len(supplements['items'])
    report['added_solutions_sha256']=hashlib.sha256(Path(__file__).with_name('a10-m82452-added-solutions.gu.json').read_bytes()).hexdigest()
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
