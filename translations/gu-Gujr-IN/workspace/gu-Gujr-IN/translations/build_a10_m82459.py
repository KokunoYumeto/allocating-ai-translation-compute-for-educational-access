"""Complete source-bound Gujarati translation of A10 m82459.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82459/index.cnxml'
MAP=Path(__file__).with_name('a10-m82459.slots.json')
TSV=Path(__file__).with_name('a10-m82459.gu.tsv')
OUT=Path(__file__).with_name('a10-m82459.gu.cnxml')
SHA='730f4347e986d692a35dbecd7d22a68b461de068dafe077809c9f37844ab2fb0'
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
    # Source inline order is fixed. Recast Gujarati around the same nodes;
    # no variables, mathematical punctuation, IDs or hierarchy are moved.
    def replace(i,old,new):
        found=0
        for e in byid[i].iter():
            for attr in ['text','tail']:
                v=getattr(e,attr)
                if v and old in v:setattr(e,attr,v.replace(old,new));found+=1
        assert found==1,(i,old,found)
    e=byid['fs-id1170654963188'];e[1].tail=' અને તેને “nનો વર્ગ” વાંચીએ. મળતું પરિણામ કહેવાય છે '
    e[2].tail='; અહીં મૂળ સંખ્યા છે ';e[3].tail='. ઉદાહરણ તરીકે,'
    e=byid['fs-id1170655000967'];e[1].tail=' એ ';e[2].tail=' છે; મૂળ સંખ્યા છે ';e[3].tail='.'
    e=byid['fs-id1170655007029'];e[0].tail=' એટલે આપણે 100ને 10નો વર્ગ કહીએ છીએ. આપણે એમ પણ કહીએ છીએ કે 10 એ 100નું '
    e[1].tail=' છે. જે સંખ્યાનો વર્ગ ';e[2].tail=' હોય, તેને ';e[3].tail=' કહીએ છીએ; મૂળ હેઠળની સંખ્યા છે ';e[4].tail='.'
    e=byid['fs-id1170654952190'];e[1].tail=' એ ';e[2].tail=' છે; મૂળ હેઠળની સંખ્યા છે ';e[3].tail='.'
    e=byid['fs-id1170655111452'];e[0].tail=' ને “';e[1].tail='નું વર્ગમૂળ” વાંચીએ છીએ.'
    e=byid['fs-id1170655207964'];e[1].tail=' અહીં શરત છે: '
    e=byid['fs-id1170654872607'];e.text='સંખ્યા ';e[0].tail='નું વર્ગમૂળ, ';e[-1].tail=' હોય.'
    e=byid['fs-id1170654928833'];e.text='આપણે જોયું છે કે પૂર્ણાંક સંમેય સંખ્યાઓ છે. પૂર્ણાંક ';e[0].tail='ને દશાંશ તરીકે લખી શકાય છે: '
    e=byid['fs-id1170655196916'];e[0].text='દરેક સંમેય સંખ્યાને પૂર્ણાંકોના ગુણોત્તર તરીકે લખી શકાય છે';e[2].text='જ્યાં p અને q પૂર્ણાંક છે અને';e[4].text='તેમ જ અંત આવતો હોય કે આવર્તન થતું હોય એવા દશાંશ સ્વરૂપમાં લખી શકાય છે.'
    e=byid['fs-id1170654972004'];e.text='શું આનું સાદું રૂપ આપી શકીએ: ';e[0].tail=' શું એવી કોઈ સંખ્યા છે જેનો વર્ગ આ હોય: '
    e=byid['fs-id1170654936768'];e.text='અત્યાર સુધી આપણે જે સંખ્યાઓ જોઈ છે તેમાંની કોઈનો વર્ગ આ નથી: ';e[0].tail=' કેમ? કોઈ પણ ધન સંખ્યાનો વર્ગ ધન હોય છે. કોઈ પણ ઋણ સંખ્યાનો વર્ગ પણ ધન હોય છે. તેથી આની બરાબર કોઈ વાસ્તવિક સંખ્યા નથી: '
    # English plural-s is explicit instructional source text, not a variable.
    # Retain the literal source s, with its Gujarati explanation in its owner.
    e=byid['fs-id1170654983255'];e.text='અગાઉ આપણે સંખ્યાઓને આ પ્રકારોમાં વર્ણવી છે: '
    for term in list(e)[:2]:
        term[0].text='ગણતરીની સંખ્યાઓ'if term.get('id')=='term-00005'else'પૂર્ણ સંખ્યાઓ'
        term[0].tail=' (અંગ્રેજી બહુવચન પ્રત્યય ';term[1].tail=')'
    e=byid['fs-id1170654905314'];e[-1].tail=' માટે આ સાચું છે. દશાંશબિંદુ અને શૂન્ય ઉમેરીને કોઈ પણ પૂર્ણાંકને દશાંશ સ્વરૂપમાં પણ લખી શકીએ છીએ.'
    e=byid['fs-id1170654963379'];e[0].tail=' જોઈ ત્યારે તેના પર માત્ર ધન અને ઋણ પૂર્ણાંક હતા. હવે આપણે તેના પર ';e[1].tail=' અને દશાંશ સંખ્યાઓ પણ દર્શાવીશું.'
    e=byid['fs-id1170655203491'];e.text='સૌથી સરળ હોવાથી પહેલાં આ પૂર્ણ સંખ્યાઓનાં સ્થાન દર્શાવીએ: ';e[1].tail=' જુઓ '
    e=byid['fs-id1170655188953'];e[0].tail=' માટે છેડાની સંખ્યાઓ છે 0 અને ';e[1].tail=' એકમ અંતરને 5 સરખા ભાગમાં વહેંચ્યા પછી દર્શાવીએ: '
    e=byid['fs-id1170655133440'];e.text='ઉદાહરણ ';e[0].tail='માં અપૂર્ણાંકોને ક્રમમાં ગોઠવવા અસમાનતાનાં ચિહ્નો વાપરીશું. અગાઉનાં પ્રકરણોમાં સંખ્યાઓને ક્રમમાં ગોઠવવા સંખ્યારેખાનો ઉપયોગ કર્યો હતો.'
    for i in ['fs-id1166425210298','fs-id1166422832290']:
        for item in byid[i].findall('.//'+c+'item'):
            x=list(item);assert len(x)==5
            less='<'in x[0].text
            x[0].tail=' એટલે “';x[1].tail=' એ ';x[2].tail=(' કરતાં નાનું છે'if less else' કરતાં મોટું છે')+'”; ત્યારે સંખ્યારેખા પર '
            x[3].tail='નું સ્થાન ';x[4].tail=('ની ડાબે હોય છે.'if less else'ની જમણે હોય છે.')
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==c+'entry' and 'is to the right of'in ''.join(a.itertext()):
            maths=b.findall(m+'math');assert len(maths)==2
            maths[0].tail='નું સ્થાન ';maths[1].tail='ની જમણે છે, સંખ્યારેખા પર.'
        if a.tag==c+'entry' and 'There is no real number whose square'in ''.join(a.itertext()):
            for e in b.iter():
                if e.text and 'એવી કોઈ વાસ્તવિક સંખ્યા નથી' in e.text:e.text=e.text.replace('એવી કોઈ વાસ્તવિક સંખ્યા નથી જેનો વર્ગ','એવી કોઈ વાસ્તવિક સંખ્યા નથી જેનો વર્ગ આ હોય:')
                if e.tail and 'હોય. તેથી' in e.tail:e.tail=e.tail.replace('હોય. તેથી','તેથી')
    e=byid['fs-id1170654943214'];e[0].tail='નું સ્થાન ';e[1].tail='ની જમણે છે, તેથી ';e[3].tail='નું સ્થાન ';e[4].tail='ની ડાબે છે, તેથી '
    e=byid['fs-id1170655257932'];e[-1].tail=' આ માપક્રમ પર ચકાસણીયાદીના તમારા જવાબો ધ્યાનમાં રાખીને આ વિભાગમાં તમારી નિપુણતાને કેટલા ગુણ આપશો? તેમાં સુધારો કેવી રીતે કરશો?'
    e=byid['fs-id1166424794538'];e[-1].tail=' છે. સંમેય સંખ્યાને બે પૂર્ણાંકોના ગુણોત્તર તરીકે લખી શકાય છે. તેના દશાંશ સ્વરૂપનો અંત આવે છે અથવા આવર્તન થાય છે.'
    e=byid['fs-id1166422865557'];e[0].tail=' હોય, તો '
    # Repeated summary notation has a different source parent structure.
    for a,b in zip(source.iter(),root.iter()):
        if a.tail and a.tail.strip()=="is read ‘the square root of":
            b.tail=' ને વાંચીએ “'
        if a.tail and a.tail.strip()==".’ If":b.tail='નું વર્ગમૂળ”. જો '
        if a.tail and a.tail.strip()=='for':b.tail=' અહીં શરત છે: '
    errata=Path(__file__).with_name('a10-m82459-errata.gu.json')
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
            if entry.get('entry_direction_overrides_gu'):
                cells=[e for e in byid[i].iter(c+'entry')if len(e.findall(m+'math'))==2]
                assert len(cells)==4
                for j,direction in entry['entry_direction_overrides_gu'].items():
                    cells[int(j)].findall(m+'math')[1].tail='ની '+direction+' છે, સંખ્યારેખા પર.'

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
