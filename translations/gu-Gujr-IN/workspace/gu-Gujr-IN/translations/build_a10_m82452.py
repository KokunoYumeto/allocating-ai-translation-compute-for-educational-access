"""Source-bound Gujarati translation of A10 m82452; no source corpus changes."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json, re, hashlib

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82452/index.cnxml'
MAP = Path(__file__).with_name('a10-m82452.slots.json')
OUT = Path(__file__).with_name('a10-m82452.gu.cnxml')
SHA = '0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310'
CNX = 'http://cnx.rice.edu/cnxml'
MATH = 'http://www.w3.org/1998/Math/MathML'
def slots(root):
    for e in root.iter():
        local = e.tag.rsplit('}',1)[-1]
        if local in {'content-id','uuid'}: continue
        for attr in ['text','tail']:
            value = getattr(e,attr)
            if value and re.search('[A-Za-z]',value) and not (e.tag.startswith('{'+MATH+'}') and attr == 'text' and local != 'mtext'):
                yield e,attr,value.strip()
        for attr in ['alt','summary']:
            value=e.get(attr)
            if value and re.search('[A-Za-z]',value): yield e,'@'+attr,value.strip()
    # Append ARIA labels after the original 448 text/alt slots, keeping their stable numbers.
    for e in root.iter():
        if e.get('aria-label') and re.search('[A-Za-z]',e.get('aria-label')):
            yield e,'@aria-label',e.get('aria-label').strip()

def main():
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
    tree=ET.parse(SRC); root=tree.getroot()
    unique=list(dict.fromkeys(t for _,_,t in slots(root)))
    if not MAP.exists():
        MAP.write_text(json.dumps({'source_sha256':SHA,'slots':[{'n':i,'en':s,'gu':None} for i,s in enumerate(unique)]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Created',len(unique),'source slots');return
    data=json.loads(MAP.read_text(encoding='utf-8'))
    assert data['source_sha256']==SHA
    rows=data['slots']
    assert [x['en'] for x in rows]==unique[:len(rows)]
    for i in range(len(rows),len(unique)): rows.append({'n':i,'en':unique[i],'gu':None})
    authored={}
    for line in Path(__file__).with_name('a10-m82452.gu.tsv').read_text(encoding='utf-8').splitlines():
        n,gu=line.split('\t',1);assert int(n) not in authored
        authored[int(n)]=gu
    for row in rows: row['gu']=authored.get(row['n'])
    MAP.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    missing=[x['n'] for x in rows if x['gu'] is None]
    assert not missing,missing
    trans={x['en']:x['gu'] for x in rows}
    for e,attr,src in slots(root):
        value=trans[src]
        if attr.startswith('@'): e.set(attr[1:],value)
        else:
            old=getattr(e,attr); prefix=old[:len(old)-len(old.lstrip())];suffix=old[len(old.rstrip()):]
            setattr(e,attr,prefix+value+suffix)
    # Gujarati grammatical order is reviewed at paragraph level: keep every
    # element/ID and mathematical child, while joining their prose naturally.
    by_id={e.get('id'):e for e in root.iter() if e.get('id')}
    def wording(id,text,tails):
        e=by_id[id]; assert len(e)==len(tails),(id,len(e),len(tails))
        e.text=text
        for child,tail in zip(e,tails):child.tail=tail
    wording('fs-id1170655207891','કોઈ સંખ્યાને ',[
        ' કહેવાય, જો તે ',
        ' અને ગણતરીની કોઈ સંખ્યાનો ગુણાકાર હોય. એટલે તે ',
        'નો અવયવી છે.'
    ])
    wording('fs-id1170655228596','જો સંખ્યા ',[
        ' એ ', 'નો અવયવી હોય, તો ', ' એ ', ' છે ', ' વડે.'
    ])
    e=by_id['fs-id1170655247415']
    e[0].tail=' એ ';e[1].tail='નો અવયવી હોય, તો કહી શકીએ કે '
    e[2].tail=' વિભાજ્ય છે ';e[3].tail=' વડે. '+e[3].tail.lstrip('. ')
    wording('fs-id1166421632723','જો સંખ્યા ',[
        ' એ ', 'નો અવયવી હોય, તો ', ' વિભાજ્ય છે ',
        ' વડે. (6 એ 3નો અવયવી હોય તો 6 એ 3 વડે વિભાજ્ય છે.)'
    ])
    wording('fs-id1166421632833','ગણતરીની કોઈ સંખ્યા અને ',[
        'નો ગુણાકાર કરવાથી મળતી સંખ્યા એ ', 'નો અવયવી છે.'
    ])
    wording('fs-id1170655247310','પદાવલી ',[
        'માં ', ' અને ', 'ને કહે છે ', '. જો ', ' હોય અને ',
        ' તથા ', ' પૂર્ણાંકો હોય, તો ', ' અને ', ' એ ',
        ' તરીકે ઓળખાય છે; સંબંધિત સંખ્યા છે ', '.'
    ])
    wording('fs-id1166421632755','જો ',[
        ', તો ', ' અવયવો તરીકે ઓળખાય છે; સંબંધિત સંખ્યા છે ',
        '. કારણ કે 3 · 4 = 12, તેથી 3 અને 4 એ 12ના અવયવો છે.'
    ])
    # This paragraph explicitly discusses the English plural suffix: retain s
    # inside its source emphasis. Do not change the separate Gujarati plural below.
    e=by_id['fs-id1170655113270']
    assert e[0].tag=='{'+CNX+'}emphasis' and e[0].get('effect')=='italics'
    assert e.text.endswith('અક્ષર ઉમેરશો નહીં. ')
    e.text=e.text[:-len('ઉમેરશો નહીં. ')]
    e[0].text='s';e[0].tail=' ઉમેરશો નહીં. '+e[0].tail.lstrip()
    # The empty English plural-s emphasis remains in place; the Gujarati plural
    # belongs on its term, rather than in a visibly separated suffix.
    by_id['term-00015'].text='અવિભાજ્ય સંખ્યાઓ'
    e=by_id['fs-id1170655219626'];e.text='20 કરતાં નાની '
    e[1].tail=' છે: 2, 3, 5, 7, 11, 13, 17 અને 19. ધ્યાન આપો કે એકમાત્ર બેકી અવિભાજ્ય સંખ્યા 2 છે.'
    by_id['term-00004'].tail=by_id['term-00004'].tail.lstrip()
    by_id['term-00016'].tail=by_id['term-00016'].tail.lstrip()
    by_id['term-00017'].tail=by_id['term-00017'].tail.lstrip()
    by_id['fs-id1170655195905'][-1].tail=' છે.'
    # Correct source descriptive errors only via the explicit, source-ID keyed
    # errata file. Original numbers, MathML and original factor lists stay intact.
    errata=json.loads(Path(__file__).with_name('a10-m82452-errata.gu.json').read_text(encoding='utf-8'))
    for id,record in errata['entries'].items():
        for change in record.get('edits',[]):
            e=by_id[id]
            if 'selector' in change:
                e=e.find(change['selector'],{'c':CNX});assert e is not None
            if 'child' in change:e=e[change['child']]
            if change['field'].startswith('@'):e.set(change['field'][1:],change['value'])
            else:setattr(e,change['field'],change['value'])
    root.set('{http://www.w3.org/XML/1998/namespace}lang','gu-Gujr-IN')
    ET.register_namespace('',CNX);ET.register_namespace('m',MATH);ET.register_namespace('md','http://cnx.rice.edu/mdml')
    tree.write(OUT,encoding='utf-8',xml_declaration=True)
    print('Translated',len(rows),'unique prose slots to',OUT)

if __name__=='__main__':main()
