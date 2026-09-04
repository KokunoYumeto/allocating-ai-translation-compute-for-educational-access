"""Complete source-bound Gujarati translation of A10 m82456.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82456/index.cnxml'
MAP=Path(__file__).with_name('a10-m82456.slots.json')
TSV=Path(__file__).with_name('a10-m82456.gu.tsv')
OUT=Path(__file__).with_name('a10-m82456.gu.cnxml')
SHA='1d3b69d74603175eb3c8aae95319b14bee988a56345c67384c0090b29995ab33'
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
    """Apply explicit source-ID-bound prose/description revisions."""
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    c='{'+CNX+'}';m='{'+MATH+'}'
    def rewrite(i,text,tails):
        e=byid[i];assert len(e)==len(tails),(i,len(e),len(tails));e.text=text
        for child,tail in zip(e,tails):child.tail=tail
    rewrite('fs-id1170652618788','આ વિભાગના વિષયોનો વધુ વિગતવાર પરિચય ',[' પુસ્તકના આ પ્રકરણમાં મળે છે: ','.'])
    e=byid['fs-id1170652621648'];e[3].tail=' ત્રણ સરખા ભાગોમાંના બે ભાગ દર્શાવે છે. આ અપૂર્ણાંકમાં, ';e[4].tail=' 2ને ';e[5].tail=' અને 3ને ';e[6].tail=' કહે છે.'
    e=byid['fs-id1170653761458'];e[0].tail='માં બે ચિત્રો છે: ડાબે એક પિઝાના બે સરખા ભાગ કર્યા છે અને જમણે તે જ કદના બીજા પિઝાના આઠ ભાગ કર્યા છે. આ રીતે જોઈ શકાય છે કે ';e[-2].tail='. બીજા શબ્દોમાં, તેઓ ';e[-1].tail=' છે.'
    rewrite('fs-id1170654030781','ગણિત વડે આ અપૂર્ણાંકને કેવી રીતે બદલીએ: ',['? બીજો અપૂર્ણાંક છે ', ' બે ટુકડા કરેલા પિઝાના આઠ ટુકડા કેવી રીતે કરી શકાય? બે મોટા ટુકડામાંથી દરેકના ચાર નાના ટુકડા કરીએ! તેથી આખા પિઝાના ટુકડા થાય ', ' એટલે કે માત્ર 2ને બદલે 8 ટુકડા. આ વાતને ગણિતમાં આ રીતે લખી શકાય: ',' જુઓ ','.'])
    e=byid['fs-id1170654125509'];e.text='આપેલો અપૂર્ણાંક છે ';e[0].tail=' તેના સમ અપૂર્ણાંક શોધવા અંશ અને છેદને એક જ સંખ્યા વડે ગુણીએ છીએ. શૂન્ય સિવાયની કોઈ પણ સંખ્યા પસંદ કરી શકાય. ચાલો તેમને 2, પછી 3 અને પછી 5 વડે ગુણીએ.'
    for i in ['fs-id1170654116001','fs-id1170654037932']:
        e=byid[i];e.text='અપૂર્ણાંક ';e[0].tail=' ગણાય, '+e[0].tail.strip()
    e=byid['fs-id1170654203066'];e.text='અંગ્રેજી શબ્દસમૂહ ‘reduce a fraction’ (';e[0].tail=') '+e[0].tail.strip()
    rewrite('fs-id1170654060626','ક્યારેક અંશ અને છેદના સામાન્ય અવયવો સહેલાઈથી મળતા નથી. ત્યારે અંશ અને છેદને ',['ઓના ગુણાકાર તરીકે લખવું સારું રહે. પછી સમ અપૂર્ણાંકોના ગુણધર્મ વડે સામાન્ય અવયવોનો ભાગાકાર કરીને તેમને દૂર કરો.'])
    e=byid['fs-id1170654066406'];e[0].tail=' '+e[0].tail.lstrip();e[1].tail=e[1].tail.lstrip()
    rewrite('fs-id1170654185172','અપૂર્ણાંકનો ',[' મેળવવા તેને ઊલટાવીએ છીએ: અંશને છેદમાં અને છેદને અંશમાં મૂકો. આ અપૂર્ણાંક ', 'નો વ્યસ્ત છે ',None])
    rewrite('fs-id1170653770746','બે સંખ્યાઓના ગુણાકારથી ',[' ધન 1 મળે તે માટે બંને સંખ્યાઓનાં ચિહ્નો સરખાં હોવાં જોઈએ. તેથી સંખ્યા અને તેના વ્યસ્તનાં ચિહ્નો સરખાં હોય છે.'])
    rewrite('fs-id1170654128489',None,['નો વ્યસ્ત છે ', ' કારણ કે ',None])
    rewrite('fs-id1170653743664','આનો ',[' જુઓ: ', 'નો વ્યસ્ત છે ',None])
    rewrite('fs-id1170653890410','અંગ્રેજીમાં ‘quotient’ એટલે ',[' અને ‘ratio’ એટલે ','. આ શબ્દો ઘણી વાર અપૂર્ણાંકનું વર્ણન કરવા વપરાય છે. ‘ભાગફળ’ શબ્દ ', 'નું પરિણામ દર્શાવે છે. આ બેનું ભાગફળ: ', ' અને ', ' એ ભાગાકારનું પરિણામ છે. ભાગીએ ', 'ને આના વડે: ', ' અથવા ',None])
    for i in ['fs-id1170654281374','fs-id1170652623005']:
        rewrite(i,'આ શબ્દસમૂહને બીજગણિતીય પદાવલીમાં લખો: ',[' અને ', 'ના તફાવતને ', ' વડે ભાગતાં મળતું ભાગફળ.'])
    rewrite('fs-id1170654150368','આ શબ્દસમૂહને બીજગણિતીય પદાવલીમાં લખો: ',[' અને ', 'ના સરવાળાને ', ' વડે ભાગતાં મળતું ભાગફળ.'])
    rewrite('fs-id1170654235420','આપણે ',[' શોધીએ છીએ—', '', ' અને ', 'ના તફાવતને ', '', ' વડે ભાગતાં મળતું પરિણામ. એટલે ભાગાકાર કરીએ: ',None])
    byid['fs-id1170654235420'][1].text='';byid['fs-id1170654235420'][4].text=''
    math=byid['fs-id1170654235420'].find(m+'math');texts=list(math.iter(m+'mtext'));texts[0].text='અને';texts[1].text='ના તફાવતને આના વડે ભાગો:'
    rewrite('fs-id1170654293053',None,['ને ', ' અને 10ના સરવાળા વડે ભાગતાં મળતું ભાગફળ'])
    rewrite('fs-id1170654293089',None,['ને 3 અને ', 'ના તફાવત વડે ભાગતાં મળતું ભાગફળ'])
    for i,kind in [('fs-id1170654285559','તફાવત'),('fs-id1170654285614','સરવાળા')]:
        e=byid[i];e.text='ભાગફળ મેળવવા આ ભાગાકાર કરો: ';mt=list(e.iter(m+'mtext'));mt[0].text='અને';mt[1].text='તેમના '+kind+'ને આના વડે ભાગો:'
    for e in root.iter(c+'meaning'):
        if (e.text or '').strip()=='આનો વ્યસ્ત,':
            e.text='';e[0].tail='નો વ્યસ્ત છે '
        if (e.text or '').strip()=='એક અપૂર્ણાંક આ રીતે લખાય છે:':e.text='અપૂર્ણાંક આ રીતે લખાય છે: '
    # Inline italic single letters are source algebra variables, even A, which
    # would otherwise share a prose slot with the English indefinite article.
    for a,b in zip(source.iter(),root.iter()):
        if a.tag==c+'emphasis' and a.get('effect')=='italics' and re.fullmatch('[A-Za-z]',(a.text or '').strip()):b.text=a.text
    e=byid['fs-id1166424908857'].find(c+'item');assert len(e)==4
    e[0].tail=' ';e[1].tail=' છે અને ';e[2].tail=' ';e[3].tail=' છે.'
    # Fraction-of-whole correction is in keyed errata; grammatical agreement
    # follows after the corrected unit is applied below.
    # Generic standalone definition entries a is numerator / b is denominator.
    for e in root.iter(c+'entry'):
        if len(e)==2 and e[1].tag==c+'emphasis' and e[1].text in ['અંશ','છેદ']:
            e[0].tail=' ';e[1].tail=' છે.'
    errata=Path(__file__).with_name('a10-m82456-errata.gu.json')
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

    mt=byid['fs-id1170652648188'].find('.//'+m+'mtext');assert mt is not None;mt.text='બરાબર છે'
    e=byid['fs-id1170654211143'];e.text='જો પાઈના ';e[0].tail=' ટુકડા કર્યા હોય અને આપણે બધા 6 ખાઈએ, તો આપણે ખાધો '
    e[1].tail=e[1].tail.replace('આપણે ખાધા','આપણે ખાધો')

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
