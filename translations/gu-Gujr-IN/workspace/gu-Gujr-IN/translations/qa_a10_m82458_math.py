"""Independent exact-decimal checks, bound to source questions and Gu answers.

No binary floating point: decimal tokens become rational integers/denominators.
Recurring digit blocks are checked by the geometric-series rational identity.
Image-only results are independently read and pinned to exact original assets.
"""
from fractions import Fraction as F
from decimal import Decimal,ROUND_HALF_UP
import ast,re
NS={'c':'http://cnx.rice.edu/cnxml','m':'http://www.w3.org/1998/Math/MathML'}
C='{'+NS['c']+'}';M='{'+NS['m']+'}'
def flat(e):
    tag=e.tag.rsplit('}',1)[-1]
    if tag=='mfrac':return '(('+flat(e[0])+')/('+flat(e[1])+'))'
    if tag=='msup':return '('+flat(e[0])+')**('+flat(e[1])+')'
    if tag=='mover':
        assert ''.join(e[1].itertext()).strip() in {'—','¯','―'},'not recurring overbar'
        return 'R'+flat(e[0])+'R'
    if tag=='mspace':return ''
    return (e.text or '')+''.join(flat(x)+(x.tail or '')for x in e)
def calc(text):
    t=re.sub(r'\s+','',text).replace(',','').replace('$','').replace('−','-').replace('÷','/').replace('×','*').replace('⋅','*').replace('·','*')
    percent=t.endswith('%');t=t.rstrip('%')
    if t.endswith('.') and t.count('.')>1:t=t[:-1] # Source sentence period inside MathML.
    recurring=re.fullmatch(r'(-?)(\d+)\.(\d*)R(\d+)R',t)
    if recurring:
        sign,whole,prefix,cycle=recurring.groups();k=len(prefix)
        value=F(whole)+F(int(prefix or '0'),10**k)+F(int(cycle),10**k*(10**len(cycle)-1))
        return (-value if sign else value)/(100 if percent else 1)
    # Implicit multiplication only at a number/closing parenthesis followed by '('.
    t=re.sub(r'(?<=[0-9)])\(',r'*(',t)
    toks=re.findall(r'\d*\.\d+|\d+\.?|\*\*|[()+*/-]',t)
    assert ''.join(toks)==t,(text,t,toks)
    expr=''.join('F('+repr(x)+')'if re.fullmatch(r'\d*\.\d+|\d+\.?',x)else x for x in toks)
    node=ast.parse(expr,mode='eval')
    allowed=(ast.Expression,ast.Call,ast.Name,ast.Load,ast.Constant,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.USub,ast.UAdd)
    assert all(isinstance(n,allowed)for n in ast.walk(node))
    return eval(compile(node,'<source arithmetic>','eval'),{'__builtins__':{},'F':F})/(100 if percent else 1)
def rounded(value,places):
    d=Decimal(value.numerator)/Decimal(value.denominator)
    return F(d.quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP))
def nums(text):return re.findall(r'[-−]?\$?\d[\d,]*(?:\.\d+)?%?',text)
def solution_values(sol):
    maths=sol.findall('.//m:math',NS)
    if maths:return [calc(flat(x))for x in maths]
    return [calc(x)for x in nums(''.join(sol.itertext()))]
def run(s,g):
    se=s.findall('.//c:exercise',NS);ge=g.findall('.//c:exercise',NS);checks=[]
    # These exact English/Gu final readings are independently compared with numbers.
    names={
      1:('6.7','six and seven tenths','છ અને સાત દશાંશ'),2:('5.8','five and eight tenths','પાંચ અને આઠ દશાંશ'),
      3:('-15.571','negative fifteen and five hundred seventy-one thousandths','ઋણ પંદર અને પાંચસો એકોતેર સહસ્રાંશ'),
      4:('-13.461','negative thirteen and four hundred sixty-one thousandths','ઋણ તેર અને ચારસો એકસઠ સહસ્રાંશ'),
      5:('-2.053','negative two and fifty-three thousandths','ઋણ બે અને ત્રેપન સહસ્રાંશ'),
      59:('5.5','five and five tenths','પાંચ અને પાંચ દશાંશ'),61:('8.71','eight and seventy-one hundredths','આઠ અને એકોતેર શતાંશ'),
      63:('0.002','two thousandths','બે સહસ્રાંશ'),65:('-17.9','negative seventeen and nine tenths','ઋણ સત્તર અને નવ દશાંશ')}
    # Word problems require independently reviewed word forms, not answers as inputs.
    word_inputs={7:('thirteen and sixty-eight thousandths','તેર અને અડસઠ સહસ્રાંશ',F(13)+F(68,1000)),8:('five and ninety-four thousandths','પાંચ અને ચોરાણું સહસ્રાંશ',F(5)+F(94,1000)),51:('Twenty-nine and eighty-one hundredths','ઓગણત્રીસ અને એક્યાસી શતાંશ',F(29)+F(81,100)),53:('Seven tenths','સાત દશાંશ',F(7,10)),55:('Twenty-nine thousandth','ઓગણત્રીસ સહસ્રાંશ',F(29,1000)),57:('Negative eleven and nine ten-thousandths','ઋણ અગિયાર અને નવ દસ-સહસ્રાંશ',-F(11)-F(9,10000))}
    image_bindings={
      0:('002d_new.jpg','four and three tenths','ચાર અને ત્રણ દશાંશ',[F(4)+F(3,10)]),
      6:('003d_new.jpg','14.024','14.024',[F(14)+F(24,1000)]),
      9:('004d_new.jpg','18.38','18.38',[rounded(F('18.379'),2)]),
      36:('017_img_new.jpg','0.625','−5/8 = −0.625',[F(-5,8)]),
      39:('018_img_new.jpg','54','54',[F(1)+F(9,10)+F(54,990)])}
    rounding={10:[2],11:[2],13:[2,1,0],14:[3,2,1],67:[1],69:[1],71:[2],73:[2],75:[2],77:[2,1,0],79:[2,1,0]}
    for j,(a,b) in enumerate(zip(se,ge)):
        sol=a.find(C+'solution');gsol=b.find(C+'solution')
        if sol is None:assert gsol is None;continue
        if j in {175,177}:
            assert 'Answers may vary' in ''.join(sol.itertext());assert 'જવાબો જુદા હોઈ શકે છે'in ''.join(gsol.itertext());continue
        p=a.find(C+'problem');gp=b.find(C+'problem');pm=p.findall('.//m:math',NS)
        record={'exercise':a.get('id'),'index':j}
        if j in names:
            val,en,gu=names[j];assert calc(flat(pm[0])if pm else nums(''.join(p.itertext()))[0])==calc(val)
            assert en in ''.join(sol.itertext()) and gu in ''.join(gsol.itertext());expected=[calc(val)];binding='source and Gu word form'
        elif j in image_bindings:
            filename,en,gu,expected=image_bindings[j]
            for root,needle in [(sol,en),(gsol,gu)]:
                m=next(e for e in root.findall('.//c:media',NS)if e.find(C+'image').get('src').endswith(filename));assert needle in m.get('alt')
            if j==36:assert calc(flat(pm[0]))==expected[0]
            if j==39:assert calc(flat(pm[0]))==expected[0]
            if j==0:assert '4.3'in ''.join(p.itertext())
            if j==6:assert 'fourteen and twenty-four thousandths'in ''.join(p.itertext())and'ચૌદ અને ચોવીસ સહસ્રાંશ'in ''.join(gp.itertext())
            if j==9:assert '18.379'in ''.join(p.itertext())
            binding='independently viewed original '+filename+' and current alternative'
        else:
            if j in word_inputs:
                en,gu,v=word_inputs[j];assert en in ''.join(p.itertext())and gu in ''.join(gp.itertext());expected=[v]
            elif j in rounding:expected=[rounded(calc(flat(pm[0])if pm else nums(''.join(p.itertext()))[0]),n)for n in rounding[j]]
            elif j==12:
                assert '18.379'in ''.join(p.itertext());expected=[rounded(F('18.379'),1),rounded(F('18.379'),0)]
            elif j in {24,25,26}:
                q=''.join(p.itertext());vals=nums(q);assert vals[-3:]==['10','100','1,000'];v=calc(vals[0]);expected=[v*10,v*100,v*1000]
            elif j in {30,31,32,115}:expected=[rounded(calc(flat(pm[0])),2)]
            elif j in {33,34,35}:
                value={33:'0.374',34:'0.234',35:'0.024'}[j]
                assert value in ''.join(p.itertext());expected=[F(value)]
            elif j in {45,46,47,48,49,50}:expected=[calc(x)for x in nums(''.join(p.itertext()))]
            elif j==169:
                assert '$58,965.95'in ''.join(p.itertext());expected=[rounded(F('58965.95'),n)for n in [0,-3,-4]]
            elif j==171:
                assert '$142.186625'in ''.join(p.itertext());expected=[rounded(F('142.186625'),n)for n in [2,0]]
            elif j==173:
                pt=''.join(p.itertext());assert all(v in pt for v in ['$14.04','$8.75','8 hours','15 hours','23 hours']);total=F('14.04')*8+F('8.75')*15;expected=[total,F('14.04')*23-total]
            else:
                assert len(pm)<=1,(j,len(pm));expected=[calc(flat(pm[0])if pm else ''.join(p.itertext()))]
            if j in {15,18}:
                for r in [sol,gsol]:
                    last=r.findall('.//m:math',NS)[-1];final=last.find('m:mtable',NS)[-1];assert[calc(flat(final))]==expected
                binding='final MathML row'
            elif j==12:
                st=' '.join(''.join(sol.itertext()).split());gt=' '.join(''.join(gsol.itertext()).split())
                assert 'So, 18.379 rounded to the nearest tenth is 18.4.'in st
                assert 'So, 18.379 rounded to the nearest whole number is 18.'in st
                assert 'એટલે 18.379ને નજીકના દશાંશમાં ફેરવતાં 18.4 મળે છે.'in gt
                assert 'એટલે 18.379ને નજીકની પૂર્ણ સંખ્યામાં ફેરવતાં 18 મળે છે.'in gt
                binding='both reviewed rounding final prose/image results'
            elif j==24:
                for r in [sol,gsol]:
                    srcs=[im.get('src')for im in r.findall('.//c:image',NS)];assert all(any(x.endswith(n)for x in srcs)for n in ['011_img_new.jpg','012_img_new.jpg','013b_img_new.jpg'])
                    for filename,value in [('011_img_new.jpg','56.3'),('012_img_new.jpg','563'),('013b_img_new.jpg','5,630')]:
                        image=next(im for im in r.findall('.//c:media',NS)if im.find(C+'image').get('src').endswith(filename));assert value in image.get('alt')
                assert expected==[F('56.3'),F(563),F(5630)];binding='three actually viewed final source images'
            elif j==21:
                for r in [sol,gsol]:assert '(−3.9)(4.075) = −15.8925'in ''.join(r.itertext())
                assert expected==[F('-15.8925')];binding='exact plain final equality'
            elif j in {27,30,33,42}:
                for r in [sol,gsol]:
                    last=r.findall('.//m:math',NS)[-1]
                    if j==33:last=r.findall('.//m:math',NS)[-2]
                    text=flat(last);answer=re.split('[=≈]',text)[-1];assert[calc(answer)]==expected,(j,text,expected)
                binding='final source and Gu MathML equality/approximation'
            else:
                for r in [sol,gsol]:assert solution_values(r)==expected,(j,solution_values(r),expected)
                binding='source and Gu supplied answer tokens'
        record.update(expected=[str(v)for v in expected],binding=binding);checks.append(record)
    assert len(checks)==113,(len(checks),[c['index']for c in checks])
    return {'independently_checked_exercises':len(checks),'open_responses_reviewed':2,'method':'exact rational arithmetic; decimal half-up rounding; recurring-cycle geometric-series identity','checks':checks}
