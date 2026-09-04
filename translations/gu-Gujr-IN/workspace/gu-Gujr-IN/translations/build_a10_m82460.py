"""Complete source-bound Gujarati translation of A10 m82460.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82460/index.cnxml'
MAP=Path(__file__).with_name('a10-m82460.slots.json')
TSV=Path(__file__).with_name('a10-m82460.gu.tsv')
OUT=Path(__file__).with_name('a10-m82460.gu.cnxml')
SHA='ee089e74a6609868c94808e624d57016de348a791b577458c539c93584bba9a5'
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
    # Recast split prose around preserved inline terms, variables and MathML.
    e=byid['fs-id1170654013661'];e[0].tail='. સરવાળો કે ગુણાકાર કરતી વખતે ';e[1].tail=' બદલવાથી પણ પરિણામ સરખું મળે છે.'
    e=byid['fs-id1170653758644'];e[0].tail=' અને ';e[1].tail=' બંને માટે પરિણામ સરખું મળે છે?'
    for i in ['fs-id1170654073759','fs-id1170654014513']:
        e=byid[i];e[0].tail=' કહે છે કે કોઈ પણ વાસ્તવિક સંખ્યા '
    e=byid['fs-id1170654036118'];e.text='';e[0].tail='ને ';e[1].tail=' કહીએ છીએ આ સંખ્યાની: ';e[2].tail='. ';e[3].text='કોઈ સંખ્યાની વિરોધી સંખ્યા એ તેની સરવાળા માટેની વિરોધી સંખ્યા છે.';e[3].tail=' સંખ્યા અને તેની વિરોધી સંખ્યાનો સરવાળો શૂન્ય થાય છે, જે સરવાળા માટેની તટસ્થ સંખ્યા છે. આથી ';e[4].tail=' મળે છે; કોઈ પણ વાસ્તવિક સંખ્યા માટે ';e[5].tail=' યાદ રાખો: સંખ્યા અને તેની વિરોધી સંખ્યાનો સરવાળો શૂન્ય થાય છે.'
    e=byid['fs-id1170654030286'];e.text='';e[0].tail='ને ';e[1].tail=' કહીએ છીએ આ સંખ્યાની: ';e[2].tail='. ';e[3].text='શૂન્ય સિવાયની ';e[3][0].tail=' સંખ્યાની વ્યસ્ત સંખ્યા એ તેની ગુણાકાર માટેની વ્યસ્ત સંખ્યા છે.';e[3].tail=' સંખ્યા અને તેની વ્યસ્ત સંખ્યાનો ગુણાકાર એક થાય છે, જે ગુણાકાર માટેની તટસ્થ સંખ્યા છે. આથી ';e[4].tail=' મળે છે; તે કહે છે કે કોઈ પણ વાસ્તવિક સંખ્યા ';e[5].tail=''
    e=byid['fs-id1170654014737'];e.text='કઈ સંખ્યાનો ';e[0].tail=' સાથે ગુણાકાર કરતાં ગુણાકાર માટેની તટસ્થ સંખ્યા 1 મળે? બીજા શબ્દોમાં, ';e[1].tail='ને શેનાથી ગુણતાં 1 મળે?'
    e=byid['fs-id1170653800775'];e.text='હવે ';e[0].text='શૂન્ય ધરાવતા ભાગાકાર';e[0].tail=' વિશે શું કહી શકાય? ';e[1].tail='નું મૂલ્ય શું છે? એક રોજિંદું ઉદાહરણ વિચારો: બરણીમાં એક પણ બિસ્કિટ નથી અને 3 લોકોમાં બિસ્કિટ વહેંચવાનાં છે, તો દરેકને કેટલાં બિસ્કિટ મળે? વહેંચવા એક પણ બિસ્કિટ નથી, એટલે દરેકને 0 બિસ્કિટ મળે છે. તેથી,'
    e=byid['fs-id1170654076171'];e.text='હવે ';e[0].text='શૂન્ય વડે ભાગવાનો';e[0].tail=' વિચાર કરીએ. 4ને 0 વડે ભાગતાં શું મળે? સંબંધિત ગુણાકારની હકીકતનો વિચાર કરો: ';e[1].tail='નો અર્થ છે ';e[2].tail='. શું એવી કોઈ સંખ્યા છે જેને 0 વડે ગુણતાં 4 મળે? કોઈ પણ વાસ્તવિક સંખ્યાને 0 વડે ગુણતાં 0 મળે છે, એટલે 0 વડે ગુણવાથી 4 મળે એવી કોઈ વાસ્તવિક સંખ્યા નથી.'
    e=byid['fs-id1170653991470'];e.text='આપણે તારણ કાઢીએ છીએ કે ';e[0].tail='નું કોઈ વાસ્તવિક સંખ્યારૂપ પરિણામ નથી. તેથી શૂન્ય વડે ભાગાકાર અવ્યાખ્યાયિત છે.'
    byid['fs-id1170654074022'][0].tail=' વપરાય છે.'
    byid['fs-id1170654077971'][0].tail=' વાપરીએ છીએ.'
    byid['fs-id1170654067898'][0].tail=' વાપરવો પડશે. પહેલાં કૌંસની અંદર જુઓ. જો તેની અંદરની પદાવલીને વધુ સાદું રૂપ ન આપી શકાય, તો આગળ વિભાજનના ગુણધર્મથી ગુણાકાર કરીને કૌંસ દૂર કરો. આગળનાં બે ઉદાહરણો આ સમજાવશે.'
    byid['fs-id1170654068703'][0].tail='માં આપ્યો છે.'
    replacements={
      'ગુણાકાર વિશે શું કહી શકાય? લઈએ':'ગુણાકારમાં પણ આ જ તપાસીએ:',
      'હવે શું થાય ભાગાકાર માં શૂન્ય હોય ત્યારે? આનું મૂલ્ય શું છે?':'હવે શૂન્ય ધરાવતા ભાગાકાર વિશે શું કહી શકાય? આનું મૂલ્ય શું છે:',
      'હવે ભાગવાનો વિચાર કરીએ આના વડે: શૂન્ય.':'હવે શૂન્ય વડે ભાગવાનો વિચાર કરીએ.',
      'આનો કોઈ જવાબ નથી:':'આનું કોઈ વાસ્તવિક સંખ્યારૂપ જવાબ નથી:',
      'સરવાળા માટેની વિરોધી સંખ્યા જોઈએ છે આ સંખ્યાની:':'આ સંખ્યાની સરવાળા માટેની વિરોધી સંખ્યા:',
      'ગુણાકાર માટેની વ્યસ્ત સંખ્યા જોઈએ છે આ સંખ્યાની:':'આ સંખ્યાની ગુણાકાર માટેની વ્યસ્ત સંખ્યા:',
      'તે છે આની વિરોધી સંખ્યા:':'એ તેની વિરોધી સંખ્યા છે:',
      'તે છે આની વ્યસ્ત સંખ્યા:':'એ તેની વ્યસ્ત સંખ્યા છે:',
      'આની વિરોધી સંખ્યા લખીએ:':'આ સંખ્યાની વિરોધી સંખ્યા લખીએ:',
      'આની વ્યસ્ત સંખ્યા:':'આ સંખ્યાની વ્યસ્ત સંખ્યા:',
      'એ છે સરવાળા માટેની વિરોધી સંખ્યા છે આ સંખ્યાની:':'એ તેની સરવાળા માટેની વિરોધી સંખ્યા છે:',
      'એ છે ગુણાકાર માટેની વ્યસ્ત સંખ્યા છે આ સંખ્યાની:':'એ તેની ગુણાકાર માટેની વ્યસ્ત સંખ્યા છે:',
      'સંખ્યા અને તેની વિરોધી સંખ્યા નો':'સંખ્યા અને તેની વિરોધી સંખ્યાનો',
      'સંખ્યા અને તેની વ્યસ્ત સંખ્યા નો':'સંખ્યા અને તેની વ્યસ્ત સંખ્યાનો',
      'એ છે સરવાળા માટેની તટસ્થ સંખ્યા':'એ સરવાળા માટેની તટસ્થ સંખ્યા છે',
      'એ છે ગુણાકાર માટેની તટસ્થ સંખ્યા':'એ ગુણાકાર માટેની તટસ્થ સંખ્યા છે',
      'પહેલાં ગુણો બંને અપૂર્ણાંકને':'પહેલાં બંને અપૂર્ણાંકોનો ગુણાકાર કરો',
      'તેથી વાપરો સરવાળાનો':'તેથી સરવાળાનો',
      'તેથી વાપરો ગુણાકારનો':'તેથી ગુણાકારનો',
      'ગુણધર્મ અને પદોનો':'ગુણધર્મ વાપરી પદોનો',
      'ગુણધર્મ અને અવયવોનો':'ગુણધર્મ વાપરી અવયવોનો',
      '0 વડે ભાગાકાર':'શૂન્ય વડે ભાગાકાર',
      '0 વડે ગુણાકાર':'શૂન્ય વડે ગુણાકાર',
    }
    for e in root.iter():
        for attr in ['text','tail']:
            value=getattr(e,attr)
            if value:
                for old,new in replacements.items():value=value.replace(old,new)
                setattr(e,attr,value)
    errata=Path(__file__).with_name('a10-m82460-errata.gu.json')
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
