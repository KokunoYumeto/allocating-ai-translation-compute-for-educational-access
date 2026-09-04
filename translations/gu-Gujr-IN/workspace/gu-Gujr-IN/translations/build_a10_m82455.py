"""Complete source-bound Gujarati translation of A10 m82455.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82455/index.cnxml'
MAP=Path(__file__).with_name('a10-m82455.slots.json')
TSV=Path(__file__).with_name('a10-m82455.gu.tsv')
OUT=Path(__file__).with_name('a10-m82455.gu.cnxml')
SHA='794635f93249017847f2646910d007e9de53b00ee6037133aa5c3edb7c2b88ec'
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
    """Apply only explicit source-ID-keyed descriptive corrections."""
    c='{'+CNX+'}';m='{'+MATH+'}'
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    def rewrite(i,text,tails):
        e=byid[i];assert len(e)==len(tails),(i,len(e),len(tails));e.text=text
        for child,tail in zip(e,tails):child.tail=tail
    rewrite('fs-id1170654069120','આ વિભાગના વિષયોનો વધુ વિગતવાર પરિચય ',[' પુસ્તકના આ પ્રકરણમાં મળે છે: ','.'])
    rewrite('fs-id1170654047593','ગુણાકાર એટલે પુનરાવર્તિત સરવાળાનું ટૂંકું ગાણિતિક સ્વરૂપ. તેથી આ નિરૂપણથી આપણે ',[' એવી સંખ્યાઓ માટે દર્શાવી શકીએ છીએ જે ',' હોય. ચાલો આ મૂર્ત નિરૂપણમાં કઈ ભાત દેખાય છે તે જોઈએ. સરવાળા અને બાદબાકી માટે વાપરેલાં એ જ ઉદાહરણો અહીં લઈશું. અહીં નિરૂપણનો ઉપયોગ માત્ર ભાત શોધવામાં મદદ માટે કરીશું.'])
    rewrite('fs-id1170654027710','આપણે યાદ કરીએ કે ',[' એટલે ','ને ',' વખત ઉમેરવું.'])
    rewrite('fs-id1170653806855','કોઈ સંખ્યાનો ',[' વડે ગુણાકાર કરતાં તેની વિરોધી સંખ્યા મળે છે.'])
    rewrite('fs-id1170654238524','આ પદાવલીમાં ',[' અને ','નો યોગ્ય ક્રમ રાખવાની કાળજી લો!'])
    rewrite('fs-id1170653881059','અંગ્રેજી શબ્દસમૂહોને બીજગણિતમાં ફેરવવાનું અગાઉનું કાર્ય પૂર્ણાંકોના ગુણાકાર અને ભાગાકારવાળા શબ્દસમૂહોને પણ લાગુ પડે છે. યાદ રાખો કે ',[' માટે મુખ્ય શબ્દ ‘','’ છે અને ',' માટે ‘','’ છે.'])
    for i in ['fs-id1170653880566','fs-id1170652622738']:
        rewrite(i,'ભાગાકાર: ',['ને ',' અને ','ના સરવાળા વડે ભાગો.'])
    for i in ['fs-id1170654159480','fs-id1170653879559']:
        rewrite(i,'ગુણાકારનું પરિણામ: ',['ને ','ના તફાવત વડે ગુણો.'])
    rewrite('fs-id1170654285039','બાદ કરો: ',['ને આ સંખ્યામાંથી: ','.'])
    e=byid['fs-id1170654149979'];e[0].tail=' જાન્યુઆરીની તારીખ ';e[1].tail=' કેલિફોર્નિયાના ઍનહાઇમમાં મહત્તમ તાપમાન હતું ';e[2].tail=' એ જ દિવસે મિનેસોટાના ઍમ્બૅરસમાં મહત્તમ તાપમાન હતું ';e[3].tail=' ઍનહાઇમ અને ઍમ્બૅરસના તાપમાન વચ્ચે કેટલો તફાવત હતો?'
    e=byid['fs-id1170652622020'];e[0].tail=' જાન્યુઆરીની તારીખ ';e[1].tail=' કેલિફોર્નિયાના પામ સ્પ્રિંગ્સમાં મહત્તમ તાપમાન હતું ';e[2].tail=' અને ન્યૂ હૅમ્પશાયરના વ્હાઇટફીલ્ડમાં મહત્તમ તાપમાન હતું ';e[3].tail=' પામ સ્પ્રિંગ્સ અને વ્હાઇટફીલ્ડના તાપમાન વચ્ચે કેટલો તફાવત હતો?'
    # Clarify the four source subtraction wordings without reversing any letter.
    e=byid['fs-id1170654190232'].find('.//'+c+'tbody/'+c+'row/'+c+'entry');assert len(e)==11
    e[2].tail='તફાવત: ';e[3].tail=' અને ';e[4].tail='નો તફાવત';e[5].tail='';e[6].tail='ને આમાંથી બાદ કરેલું: ';e[7].tail='';e[8].tail='';e[9].tail=' જેટલું આ કરતાં ઓછું: ';e[10].tail=''
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==c+'item'and (a.text or '').strip().startswith('signs are'):
            for child in b:
                if child.tail and child.tail.startswith('હોય'):child.tail=' '+child.tail
            b[-1].tail=' છે.'
    for e in root.iter():
        if not e.tag.startswith(m):
            for child in e:
                if child.tail and child.tail.startswith('વિશે શું'):child.tail=' '+child.tail
    # English articles and prepositions in MathML mtext are prose, not tokens.
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==m+'mtext':
            if (a.text or '').strip()=='the':b.text=''
            if (a.text or '').strip()=='of':b.text=':'
    e=byid['eip-929'].findall('.//'+c+'entry')[1];e.text='આ સંખ્યાઓનો '
    assert e[0].tag==c+'emphasis'
    e[0].tail=' લો: 8 અને ';e[1].tail=' પછી તેમાં 3 ઉમેરો.'
    e=byid['fs-id1170654164395'];e.text='આપેલી કિંમત '
    e[0].find('.//'+m+'mtext').text='આ ચલની જગ્યાએ મૂકો:'
    for e in byid['eip-651'].iter(c+'entry'):
        if (e.text or '').startswith('પદાવલીમાં ફેરવો. યાદ રાખો:'):
            e.text=e.text.replace('‘બાદ કરો','બાદ કરો')
    errata=Path(__file__).with_name('a10-m82455-errata.gu.json')
    if errata.exists():
        byid={e.get('id'):e for e in root.iter() if e.get('id')}
        for i,entry in json.loads(errata.read_text(encoding='utf8'))['entries'].items():
            for attr in ['alt','summary','aria-label','title']:
                if entry.get(attr+'_gu'):byid[i].set(attr,entry[attr+'_gu'])
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
