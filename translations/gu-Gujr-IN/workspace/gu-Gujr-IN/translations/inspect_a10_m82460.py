"""Generate compact, source-paired review records; does not change translation."""
from pathlib import Path
import xml.etree.ElementTree as E
import json
ROOT=Path(__file__).resolve().parents[2]
C='{http://cnx.rice.edu/cnxml}';M='{http://www.w3.org/1998/Math/MathML}'
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82460/index.cnxml'
GU=Path(__file__).with_name('a10-m82460.gu.cnxml')
def flat(e):
 t=e.tag.rsplit('}',1)[-1]
 if t=='msqrt':return 'sqrt('+''.join(flat(x)for x in e)+')'
 if t=='mfrac':return '(('+flat(e[0])+')/('+flat(e[1])+'))'
 if t=='msup':return '('+flat(e[0])+')^('+flat(e[1])+')'
 if t=='mover':return 'overbar('+flat(e[0])+')'
 if t=='media':return '[IMAGE '+e.get('id','')+' '+e.find(C+'image').get('src')+']'
 if t in ['xref','link'] and not(e.text or len(e)):return '[REF '+str(e.attrib)+']'
 if t in ['mspace']:return ' '
 return (e.text or '')+''.join(flat(x)+(x.tail or '')for x in e)
def text(e):return ' '.join(flat(e).split())if e is not None else None
def main():
 s=E.parse(SRC).getroot();g=E.parse(GU).getroot();parents={e:p for p in s.iter()for e in p};rows=[];ex=[]
 for a,b in zip(s.iter(),g.iter()):
  if a.tag==C+'exercise':
   ex.append({'index':len(ex),'id':a.get('id'),'source_question':text(a.find(C+'problem')),'gu_question':text(b.find(C+'problem')),'source_solution':text(a.find(C+'solution')),'gu_solution':text(b.find(C+'solution'))})
  if a.tag not in [C+'para',C+'title',C+'item',C+'meaning']:continue
  if any(x.tag in [C+'para',C+'item',C+'meaning']for x in a.iter()if x is not a):continue
  p=a;is_ex=False
  while p in parents:
   p=parents[p]
   if p.tag==C+'exercise':is_ex=True
  if not is_ex:rows.append((a.get('id'),text(a),text(b)))
 for name,data in [('paired-prose',rows),('paired-exercises',ex)]:
  (ROOT/('gu-Gujr-IN/reviews/a10-m82460-'+name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Prose blocks:',len(rows),'Exercises:',len(ex))
if __name__=='__main__':main()
