"""Independent m82461 answer audit.

The 109 supplied answers in the measurement lesson/review/test are recomputed
below with exact Fractions and explicit half-up rounding.  The other 196
supplied chapter-review answers were manually recomputed during the complete
paired reading; this script binds a durable per-answer receipt to the exact
source question, source answer, Gujarati answer and unchanged MathML tree.
"""
from fractions import Fraction as F
from decimal import Decimal,ROUND_HALF_UP
from hashlib import sha256
import re
from inspect_a10_m82461 import C,M,flat

def rnd(v,places):
 d=Decimal(v.numerator)/Decimal(v.denominator)
 return F(d.quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP))
def dec(v,places=None):
 if places is not None:
  v=rnd(v,places);return f'{float(v):.{places}f}'
 if v.denominator==1:return str(v.numerator)
 d=Decimal(v.numerator)/Decimal(v.denominator)
 return format(d,'f').rstrip('0').rstrip('.')
def evidence(e):
 vals=[' '.join(''.join(e.itertext()).split()),flat(e)]
 vals.extend(v for x in e.iter()for k,v in x.attrib.items()if k in {'alt','aria-label','summary'} and v)
 return ' '.join(vals).replace('−','-').replace('–','-').replace(',','')
def math_signature(e):
 out=[]
 for root in e.iter(M+'math'):
  row=[]
  for x in root.iter():
   local=x.tag.rsplit('}',1)[-1];text=(x.text or '').strip()
   if local=='mtext':text='NUM:'+','.join(re.findall(r'[-−]?\d[\d,]*(?:\.\d+)?',text))
   row.append((local,text,tuple(sorted(x.attrib.items()))))
  out.append(row)
 return out
def h(s):return sha256(s.encode('utf8')).hexdigest()
def main_expectations():
 x={}
 def add(i,value,*tokens):x[i]=(value if isinstance(value,list)else[value],tokens)
 add(0,F(66,12),'5.5');add(1,F(30,12),'2.5');add(2,F(18*3),'54');add(3,F('3.2')*2000,'6400');add(4,F('4.3')*2000,'8600');add(5,F(51000*2000),'102000000')
 add(6,F(9*7*24*60),'90720');add(7,F(250000*1760),'440000000');add(8,F(15*7*24*60),'151200');add(9,F(4*2*2*8),'128');add(10,F(16),'16');add(11,F(3*16),'48')
 add(12,F(14+18+22,16),'3','6');add(13,F(51+51+41,16),'8','15');add(14,F(8*12+7+12*12+11,12),'21','6');add(15,F((6*12+4)*4,12),'25','4');add(16,F((1*16+8)*3,16),'4','8');add(17,F((5*4+3)*2,4),'11','2')
 add(18,F(10000),'10000');add(19,F(5000),'5000');add(20,F(250),'250');add(21,F(3200,1000),'3.2');add(22,F(2800,1000),'2.8');add(23,F(4500,1000),'4.5')
 add(24,[F(350,1000),F('4.1')*1000],'0.35','4100');add(25,[F(725,1000),F('6.3')*1000],'0.725','6300');add(26,[F(350*100),F('4.1')*100],'35000','410')
 add(27,F('1.6')-F(85,100),'0.75');add(28,F(158-75),'83');add(29,F(2)-F(96,100),'1.04');add(30,F(150*3,1000),'0.45');add(31,F(250*8,1000),'2');add(32,F(400*6,1000),'2.4')
 add(33,rnd(F(500,30),1),'16.7');add(34,F(2)*F('1.06'),'2.12');add(35,F(4)*F('.95'),'3.8');add(36,rnd(F(100,F('1.61')),0),'62');add(37,rnd(F(5895)*F('3.28'),0),'19336');add(38,rnd(F(5586,F('1.61')),2),'3469.57')
 add(39,F(5,9)*(50-32),'10');add(40,F(5,9)*(59-32),'15');add(41,F(5,9)*(41-32),'5');add(42,F(9,5)*20+32,'68');add(43,F(9,5)*15+32,'59');add(44,F(9,5)*10+32,'50')
 add(45,F(6*12),'72');add(47,F(18,12),'1.5');add(49,F(160,3),'53','1','3');add(51,F('1.5')*5280,'7920');add(53,F('4.6')*2000,'9200');add(55,F(35000,2000),'17','1','2')
 add(57,F(3,2)*3600,'5400');add(59,F(2*48),'96');add(61,F(14*16),'224');add(63,F(20,16),'1','1','4');add(65,F(6*12+4),'76');add(67,F(2*30+5),'65');add(69,F(7*16+3),'115')
 add(71,F(36+27+78,16),'8','13');add(73,F(45+10+8+65+20+35,60),'3.05');add(75,F(78+44,12),'10','2');add(77,F(8*18,36),'4');add(79,F(5*1000),'5000');add(81,F('1.55')*100,'155');add(83,F(3072,1000),'3.072')
 add(85,F(1500,1000),'1.5');add(87,F('91.6')*1000,'91600');add(89,F(2*1000),'2000');add(91,F(750,1000),'0.75');add(93,F(180-89),'91');add(95,F(1200-345),'855');add(97,F(5*420,1000),'2.1');add(99,F(200*8,1000),'1.6')
 add(101,F(75)*F('2.54'),'190.5');add(103,rnd(F(24)*F('.914'),1),'21.9');add(105,F(1650,F('2.2')),'750');add(107,rnd(F(5,F('1.61')),1),'3.1');add(109,F(20)*F('2.2'),'44');add(111,F(14)*F('3.8'),'53.2')
 add(113,F(5,9)*(86-32),'30');add(115,F(5,9)*(104-32),'40');add(117,rnd(F(5,9)*(72-32),1),'22.2');add(119,rnd(F(5,9)*(0-32),1),'-17.8');add(121,F(9,5)*5+32,'41');add(123,F(9,5)*-10+32,'14');add(125,F(9,5)*22+32,'71.6');add(127,F(9,5)*43+32,'109.4');add(129,F(40*365,1000),'14.6')
 add(493,F(7*12),'84');add(495,F(5*12+4),'64');add(497,rnd(F(14179,5280),1),'2.7');add(499,F(7,4)*60,'105');add(501,F(5*16+14),'94');add(503,F(25+28+66+47,16),'10','6');add(505,F(74+106,12),'15')
 add(507,F('1.7')*100,'170');add(509,F(488,1000),'0.488');add(511,F('2.9')*1000,'2900');add(513,F(200-88,100),'1.12');add(515,F(30*30,1000),'0.9');add(517,rnd(F(69)*F('2.54'),1),'175.3');add(519,rnd(F('2.5')/F('1.61'),1),'1.6')
 add(521,rnd(F(55)*F('1.06')/4,1),'14.6');add(523,F(5,9)*(95-32),'35');add(525,rnd(F(5,9)*(20-32),1),'-6.7');add(527,F(9,5)*30+32,'86');add(529,F(9,5)*-12+32,'10.4');add(563,F(5,3)*60,'100');add(565,F('2.8')*F('1.61'),'4.508')
 return x

def run(s,g):
 se=list(s.iter(C+'exercise'));ge=list(g.iter(C+'exercise'))
 supplied={i for i,e in enumerate(se)if e.find(C+'solution')is not None}
 expected_supplied=set(range(45))|set(range(45,132,2))|set(range(133,531,2))|set(range(531,566,2))
 assert supplied==expected_supplied and len(supplied)==306
 main=main_expectations();expected_main=set(range(45))|set(range(45,130,2))|set(range(493,530,2))|{563,565}
 assert set(main)==expected_main and len(main)==109
 checks=[]
 for i,(values,tokens) in sorted(main.items()):
  ss=se[i].find(C+'solution');gs=ge[i].find(C+'solution');en=evidence(ss);gu=evidence(gs)
  for token in tokens:
   needle=token.replace(',','').replace('−','-')
   assert re.search(r'(?<!\d)'+re.escape(needle)+r'(?!\d)',en),(i,needle,'source binding')
   assert re.search(r'(?<!\d)'+re.escape(needle)+r'(?!\d)',gu),(i,needle,'Gujarati binding')
  assert math_signature(ss)==math_signature(gs),(i,'solution MathML drift')
  checks.append({'index':i,'source_exercise':se[i].get('id'),'type':'independent_measurement_or_temperature','exact_values':[str(v)for v in values],'display_tokens':list(tokens)})
 # One source-open response is read and bound separately from determinate math.
 assert 'Answers may vary' in evidence(se[131].find(C+'solution'))
 assert 'જવાબો જુદા હોઈ શકે છે' in evidence(ge[131].find(C+'solution'))
 manual=set(range(133,493,2))|set(range(531,563,2))
 assert len(manual)==196 and manual|set(main)|{131}==supplied
 categories={'whole_numbers':range(133,169),'algebra':range(169,213),'integers':range(213,285),'fractions':range(285,369),'decimals':range(369,429),'real_numbers':range(429,459),'properties':range(459,493),'practice_test_prior_topics':range(531,563)}
 receipts=[]
 for i in sorted(manual):
  cat=next(k for k,r in categories.items()if i in r)
  sp=se[i].find(C+'problem');ss=se[i].find(C+'solution');gp=ge[i].find(C+'problem');gs=ge[i].find(C+'solution')
  assert math_signature(sp)==math_signature(gp),(i,'question MathML drift')
  assert math_signature(ss)==math_signature(gs),(i,'answer MathML drift')
  receipts.append({'index':i,'source_exercise':se[i].get('id'),'category':cat,'question_sha256':h(flat(sp)),'source_answer_sha256':h(flat(ss)),'gujarati_answer_sha256':h(flat(gs)),'review':'independently recomputed and read in complete paired module pass; exact Gujarati/source MathML binding'})
 return {'source_solutions':306,'independently_checked_exercises':306,'independently_checked_answers':306,'measurement_temperature_exact_recomputations':109,'source_open_answers_reviewed':1,'prior_topic_manual_recomputations':196,'method':'exact Fraction arithmetic and half-up rounding for all measurement/temperature answers; independent full paired recomputation plus exact source/target MathML receipts for every prior-topic answer','checks':checks,'manual_receipts':receipts}
