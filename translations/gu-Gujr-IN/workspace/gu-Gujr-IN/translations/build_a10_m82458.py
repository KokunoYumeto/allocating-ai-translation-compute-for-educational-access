"""Complete source-bound Gujarati translation of A10 m82458.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82458/index.cnxml'
MAP=Path(__file__).with_name('a10-m82458.slots.json')
TSV=Path(__file__).with_name('a10-m82458.gu.tsv')
OUT=Path(__file__).with_name('a10-m82458.gu.cnxml')
SHA='678dc0c3ae2aad0192c0314395541720d6c6eb97f56d2f4d169f056fe1e630cb'
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
    """Apply explicit source-ID-bound corrections and linguistic revisions."""
    c='{'+CNX+'}';m='{'+MATH+'}'
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==c+'emphasis' and a.get('effect')=='italics' and re.fullmatch('[A-Za-z]',(a.text or '').strip()):b.text=a.text
    def rewrite(i,text,tails):
        e=byid[i];assert len(e)==len(tails),(i,len(e),len(tails));e.text=text
        for child,tail in zip(e,tails):child.tail=tail
    rewrite('fs-id1170655162670','',[' એ એવા ', 'ને લખવાની બીજી રીત છે, જેમના છેદ 10ની ઘાત હોય છે.'])
    rewrite('fs-id1170655192852','',['ને શબ્દોમાં લખવાનાં જરૂરી પગલાંનો સારાંશ નીચે આપ્યો છે.'])
    rewrite('fs-id1170654928706','',['ને અંકોમાં લખવાનાં પગલાંનો સારાંશ નીચે આપ્યો છે.'])
    rewrite('fs-id1170655029280','',['ને નજીકની આપેલી સ્થાનકિંમતમાં ફેરવવાનાં પગલાંનો સારાંશ નીચે આપ્યો છે.'])
    rewrite('fs-id1170655121723','બે સંખ્યાનો ',[' ત્યારે,'])
    byid['fs-id1170654932294'].text=''
    byid['fs-id1170655090844'].text=''
    for a,b in zip(source.iter(),root.iter()):
        if (a.text or '').startswith('A more thorough introduction'):
            b.text='આ વિભાગના વિષયોનો વધુ વિગતવાર પરિચય ';b[0].tail=' પુસ્તકના આ પ્રકરણમાં મળે છે: ';b[1].tail='.'
        if (a.text or '').strip()=='Write' and a.tag==c+'para':
            b.text='';b[-1].tail='ને દશાંશ તરીકે લખો.'
        if (a.text or '').strip()=='Change' and a.tag==c+'entry':
            b.text='';b[0].tail='ને દશાંશમાં ફેરવો.'
    errata=Path(__file__).with_name('a10-m82458-errata.gu.json')
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
    MAP.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
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
