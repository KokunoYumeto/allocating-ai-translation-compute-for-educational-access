"""Complete source-bound Gujarati translation of A10 m82454.

Reproduce with this script; missing numbered prose slots prevent output. The
source hash, hierarchy, identifiers and non-prose MathML are fixed inputs.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82454/index.cnxml'
MAP=Path(__file__).with_name('a10-m82454.slots.json')
TSV=Path(__file__).with_name('a10-m82454.gu.tsv')
OUT=Path(__file__).with_name('a10-m82454.gu.cnxml')
SHA='4483b9df8736598af20287450b89cf367728da04c697f85f1abb64bbeffb092f'
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
    """Explicit source-context sentence/alt revisions are added after reread."""
    c='{'+CNX+'}';m='{'+MATH+'}'
    byid={e.get('id'):e for e in root.iter() if e.get('id')}
    def rewrite(i,text,tails):
        e=byid[i];assert len(e)==len(tails),(i,len(e),len(tails))
        e.text=text
        for child,tail in zip(e,tails):child.tail=tail
    # Gujarati postpositions require sentence-context translation. No element,
    # math token or hierarchy is moved: only prose boundaries are rewritten.
    rewrite('fs-id1170654901053',None,[' > ',' (વાંચીએ: “',' એ ',' કરતાં મોટું છે”), જ્યારે સંખ્યારેખા પર ',' એ ','ની જમણી બાજુએ હોય.'])
    rewrite('fs-id1170655114791','તમે ધ્યાન આપ્યું હશે કે ',[' પર ઋણ સંખ્યાઓ ધન સંખ્યાઓના અરીસામાં દેખાતા પ્રતિબિંબ જેવી છે અને વચ્ચે શૂન્ય છે. 2 અને ',' શૂન્યથી સરખા અંતરે હોવાથી તેઓ એકબીજાની ','',' છે. 2ની વિરોધી સંખ્યા ',' અને ','ની વિરોધી સંખ્યા 2 છે.'])
    byid['fs-id1170655114791'].find(c+'emphasis').text='ઓ'
    rewrite('fs-id1170655000824','સંખ્યાની ',[' એ એવી સંખ્યા છે જે સંખ્યારેખા પર આપેલી સંખ્યાથી શૂન્યની બીજી બાજુએ હોય અને શૂન્યથી સરખા અંતરે હોય.'])
    rewrite('fs-id1170655174724',None,[' એટલે ', 'ની વિરોધી સંખ્યા.'])
    rewrite('fs-id1170655160739','આ સંકેતલિપિ ',['ને “','ની વિરોધી સંખ્યા” તરીકે વાંચીએ છીએ.'])
    rewrite('fs-id1170654999979','કોઈ ',['ની વિરોધી સંખ્યાની કિંમત શોધતી વખતે ખૂબ કાળજી રાખવી પડે છે. ચલ ધન કે ઋણ સંખ્યા દર્શાવે છે તે જાણ્યા વિના આપણે કહી શકતા નથી કે ',' ધન છે કે ઋણ. તે ', 'માં જોઈ શકાય છે.'])
    rewrite('fs-id1170655354299','સંખ્યાનું ',[' એ સંખ્યારેખા પર તેનું 0થી અંતર છે.'])
    byid['fs-id1170654916082'][0].tail=' બધી સંખ્યાઓ માટે લાગુ પડે છે.'
    rewrite('fs-id1170655067279','તેથી ',['નો સરવાળો છે: ',None])
    rewrite('fs-id1170654962732','અલબત્ત, માત્ર ધન સંખ્યાઓવાળો બાદબાકીનો દાખલો હોય, જેમ કે ',[' તો સીધી બાદબાકી કરો. ',' જેવી બાદબાકી કરતાં તમે ઘણા સમયથી જાણો છો. પરંતુ ', ' કે ',' અને ',' સમાન જવાબ આપે છે—આ વાત ઋણ સંખ્યાઓની બાદબાકીમાં મદદરૂપ થાય છે. ',' અને ',' કેવી રીતે સમાન પરિણામ આપે છે તે બરાબર સમજી લો!'])
    byid['fs-id1170654962732'].find(c+'emphasis').text='સમજી રાખો'
    meaning=byid['fs-id1166422694262'];meaning[0].tail=' એ આપેલી સંખ્યાની વિરોધી સંખ્યા દર્શાવે છે. આ લખાણ ';meaning[1].tail='ને “';meaning[2].tail='ની વિરોધી સંખ્યા” તરીકે વાંચીએ છીએ.'
    table=byid['eip-36'];entries=table.findall('.//'+c+'row/'+c+'entry')[1::2]
    e=entries[0];e.text='બે સંખ્યાઓની વચ્ચે તે ';e[0].tail='ની ક્રિયા દર્શાવે છે.';e[1].tail='આપણે ';e[2].tail='ને “10 ઓછા 4” તરીકે વાંચીએ છીએ.'
    e=entries[1];e.text='સંખ્યાની આગળ તે ';e[0].tail=' સંખ્યા દર્શાવે છે. '
    e=entries[2];e.text='ચલની આગળ તે ';e[0].tail=' દર્શાવે છે. આપણે ';e[1].tail='ને “';e[2].tail='ની વિરોધી સંખ્યા” તરીકે વાંચીએ છીએ.'
    e=entries[3];e.text='અહીં બે “−” ચિહ્નો છે. કૌંસની અંદરનું ચિહ્ન જણાવે છે કે સંખ્યા ઋણ 2 છે. કૌંસની બહારનું ચિહ્ન −2ની ';e[0].tail=' લેવાનું કહે છે. ';e[1].tail='આપણે ';e[2].tail='ને “ઋણ બેની વિરોધી સંખ્યા” તરીકે વાંચીએ છીએ.'
    for item in root.iter(c+'item'):
        if any((x.tail or '').strip()=='એકમ દૂર છે' for x in item):
            math=item.findall(m+'math');assert len(math)==3
            math[0].find('.//'+m+'mtext').text='એ'
            math[0].tail=' એકમ દૂર છે, જો અંતર અહીંથી માપીએ: '
            math[1].tail=' તેથી '
    for i in ['fs-id1170654921213','fs-id1170654939339','fs-id1170654936713']:
        e=byid[i];math=e.findall(m+'math');assert len(math)==3
        math[1].tail='માંથી દૂર કરો: '
        if i=='fs-id1170654921213':math[0].tail='ને આ રીતે વાંચ્યું હશે: '
    e=byid['fs-id1170654943182'];e[0].tail='? ';e[1].tail='માં ';e[-1].tail=' તરીકે આ રીતે લખેલો જોવા મળશે:'
    # Preserve source order 90°, 0° inside MathML while making its relation clear.
    e=byid['fs-id1170655224555'];math=e.findall(m+'math');math[0].tail=' સેલ્સિયસ હતું. નોંધાયેલું સૌથી નીચું તાપમાન: '
    math[1].find('.//'+m+'mtext[.="નીચે"]').text='નીચે (આધાર:'
    math[1].tail=' સેલ્સિયસ).'
    for e in root.iter():
        if e.tag.startswith(m):continue
        for child in e:
            if child.tail and child.tail.startswith(('થશે.','વાપરવી પડશે.','તરીકે આ રીતે')):child.tail=' '+child.tail
    errata=Path(__file__).with_name('a10-m82454-errata.gu.json')
    if errata.exists():
        byid={e.get('id'):e for e in root.iter() if e.get('id')}
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
