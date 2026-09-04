"""Complete source-bound Gujarati translation of A10 m82461.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82461/index.cnxml'
MAP=Path(__file__).with_name('a10-m82461.slots.json')
TSV=Path(__file__).with_name('a10-m82461.gu.tsv')
OUT=Path(__file__).with_name('a10-m82461.gu.cnxml')
SHA='df82cee2f1a278bb88f392572457ee679bc09d108962a9b6c72ba5bb0084655e'
CNX='http://cnx.rice.edu/cnxml';MATH='http://www.w3.org/1998/Math/MathML'
def slots(root):
    for e in root.iter():
        local=e.tag.rsplit('}',1)[-1]
        if local in {'content-id','uuid'}:continue
        for attr in ['text','tail']:
            value=getattr(e,attr)
            if value and re.search('[A-Za-z]',value) and not(e.tag.startswith('{'+MATH+'}')and attr=='text'and local!='mtext'):
                yield e,attr,value.strip()
        for attr in ['alt','summary','aria-label','title']:
            value=e.get(attr)
            if value and re.search('[A-Za-z]',value):yield e,'@'+attr,value.strip()
def polish(root,source):
    c='{'+CNX+'}';m='{'+MATH+'}'
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==c+'emphasis' and a.get('effect')=='italics' and re.fullmatch('[A-Za-z]',(a.text or '').strip()):b.text=a.text
    errata=Path(__file__).with_name('a10-m82461-errata.gu.json')
    if errata.exists():
        for i,entry in json.loads(errata.read_text(encoding='utf8'))['entries'].items():
            for attr in ['alt','summary','aria-label','title']:
                if entry.get(attr+'_gu'):byid[i].set(attr,entry[attr+'_gu'])
            for old,new in entry.get('text_replacements_gu',{}).items():
                matches=0
                for e in byid[i].iter():
                    for attr in ['text','tail']:
                        value=getattr(e,attr)
                        if value and old in value:setattr(e,attr,value.replace(old,new));matches+=1
                assert matches==1,(i,old,matches)
    # Gujarati word order sometimes crosses fixed inline MathML/xref boundaries.
    # These source-ID-bound adjustments change prose/tails only; mathematical
    # tokens, hierarchy and identifiers remain byte-for-byte source-faithful.
    temperature=byid['fs-id1170653807898']
    temperature_math=temperature.findall(m+'math')
    assert len(temperature_math)==2
    temperature_math[1].tail=' લખાય છે. '
    temperature.find(c+'link').tail='માં બંને પદ્ધતિ વચ્ચેનો સંબંધ બતાવ્યો છે.'

    metric_intro=byid['fs-id1170653741424']
    metric_emphasis=metric_intro.findall(c+'emphasis')
    assert len(metric_emphasis)==2
    metric_emphasis[0].tail='નો અર્થ '
    metric_emphasis[1].tail=' છે. એક સેન્ટિમીટર એ મીટરનો '

    quotient=byid['fs-id1170653880536'].find(c+'problem/'+c+'para')
    quotient_terms=quotient.findall(c+'emphasis')
    quotient_math=quotient.find(m+'math')
    assert len(quotient_terms)==2 and quotient_math is not None
    quotient.text='આ બે સંખ્યાઓનો તફાવત '
    quotient_terms[0].tail=' અને '
    quotient_terms[1].tail=' છે; એ તફાવતનો '
    quotient_math.tail=' સાથેનો ભાગફળ.'

    nested_sum=byid['fs-id1170654233240'].find(c+'problem/'+c+'para')
    nested_terms=nested_sum.findall(c+'emphasis')
    assert len(nested_terms)==2
    nested_sum.text='આ ભાગફળમાં ભાજ્ય '
    nested_terms[0].tail=' છે અને ભાજક આ બે સંખ્યાનો સરવાળો છે: '
    nested_terms[1].tail=' અને 9.'

    line_problem=byid['fs-id1170652618714'].find(c+'problem/'+c+'para')
    conjunction=next(e for e in line_problem.iter(m+'mtext') if (e.text or '').strip()=='અને')
    conjunction.text=' અને '

    # Repair missing source whitespace at sentence boundaries in the Gujarati
    # assembled reading without altering the corresponding source structures.
    newline=c+'newline'
    gallon_newlines=[e for e in byid['fs-id1170654204715'].iter(newline) if e.tail]
    assert [e.tail for e in gallon_newlines if 'સાદું રૂપ' in e.tail]==['સાદું રૂપ આપો.']
    next(e for e in gallon_newlines if 'સાદું રૂપ' in e.tail).tail=' સાદું રૂપ આપો.'
    assert [e.tail for e in gallon_newlines if '1 ગૅલનમાં' in e.tail]==['1 ગૅલનમાં 128 ઔંસ હોય છે.']
    next(e for e in gallon_newlines if '1 ગૅલનમાં' in e.tail).tail='. 1 ગૅલનમાં 128 પ્રવાહી ઔંસ હોય છે.'

    plank_newline=next(e for e in byid['fs-id1170653910861'].iter(newline) if e.tail and 'ફૂટ ઉમેરો' in e.tail)
    plank_newline.tail=' ફૂટ ઉમેરો.'
    baby_newline=next(e for e in byid['fs-id1170653775700'].iter(newline) if e.tail and 'બાળકનું વજન' in e.tail)
    baby_newline.tail='. બાળકનું વજન 3.2 કિલોગ્રામ હતું.'

def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
    tree=ET.parse(SRC);root=tree.getroot();unique=list(dict.fromkeys(t for _,_,t in slots(root)))
    if MAP.exists():data=json.loads(MAP.read_text(encoding='utf8'))
    else:data={'source_sha256':SHA,'slots':[]}
    assert data['source_sha256']==SHA
    rows=data['slots'];assert[x['en']for x in rows]==unique[:len(rows)]
    for i in range(len(rows),len(unique)):rows.append({'n':i,'en':unique[i],'gu':None})
    authored={}
    if TSV.exists():
        for line in TSV.read_text(encoding='utf8').splitlines():
            if not line.strip():continue
            n,gu=line.split('\t',1);n=int(n);assert n not in authored;authored[n]=gu
    for row in rows:row['gu']=authored.get(row['n'])
    MAP.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    missing=[r['n']for r in rows if r['gu']is None]
    if missing:print('Source slots',len(rows),'authored',len(rows)-len(missing),'next',missing[0]);return
    trans={r['en']:r['gu']for r in rows}
    for e,attr,src in slots(root):
        value=trans[src]
        if attr.startswith('@'):e.set(attr[1:],value)
        else:
            old=getattr(e,attr);setattr(e,attr,old[:len(old)-len(old.lstrip())]+value+old[len(old.rstrip()):])
    polish(root,ET.parse(SRC).getroot())
    root.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
    ET.register_namespace('',CNX);ET.register_namespace('m',MATH);ET.register_namespace('md','http://cnx.rice.edu/mdml')
    tree.write(OUT,encoding='utf-8',xml_declaration=True)
    print('Translated',len(rows),'slots')
if __name__=='__main__':main()
