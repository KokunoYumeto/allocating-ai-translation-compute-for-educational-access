"""Package the reachable static reader with local assets and exact hash checks."""
import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

LANG=Path(__file__).resolve().parents[1]
OUT=LANG/'output'
DEST=LANG/'dist/gujarati-current-draft-offline.zip'


class References(HTMLParser):
    def __init__(self):
        super().__init__();self.local=[];self.remote=[];self.ids=[];self.embedded=[]

    def handle_starttag(self,tag,attributes):
        a=dict(attributes)
        if a.get('id'):self.ids.append(a['id'])
        assert tag not in ('script','iframe'), 'Unexpected remote or active runtime'
        for attr in ('src','href'):
            if not a.get(attr):continue
            value=a[attr];url=urlsplit(value)
            if url.scheme=='data':
                header,payload=value.split(',',1)
                assert tag in ('image','img') and header in ('data:image/jpeg;base64','data:image/png;base64'),('Unsupported embedded resource',tag,header[:100])
                raw=base64.b64decode(payload,validate=True)
                assert (header=='data:image/jpeg;base64' and raw.startswith(b'\xff\xd8') and raw.endswith(b'\xff\xd9')) or (header=='data:image/png;base64' and raw.startswith(b'\x89PNG\r\n\x1a\n'))
                self.embedded.append({'mime':header[5:-7],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                continue
            if url.scheme:
                assert tag=='a',('Remote runtime dependency',tag,value[:120])
                self.remote.append(value)
            else:self.local.append(value)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def target(base,reference):
    u=urlsplit(reference)
    path=posixpath.normpath(posixpath.join(posixpath.dirname(base),unquote(u.path))) if u.path else base
    assert not path.startswith('../') and not PurePosixPath(path).is_absolute(), ('Escaping package',path)
    return path,unquote(u.fragment)


def main():
    inputs=['index.html','pdf/unit01-student-print.pdf','pdf/unit01-teacher-print.pdf']
    content={};pending=list(inputs);external=set();embedded={}
    while pending:
        name=pending.pop()
        if name in content:continue
        file=(OUT/name).resolve()
        assert file.is_relative_to(OUT.resolve()) and file.is_file(), name
        data=file.read_bytes();content[name]=data
        references=[]
        if name.endswith('.html'):
            parser=References();parser.feed(data.decode('utf-8'))
            references=parser.local;external.update(parser.remote)
            for item in parser.embedded:embedded[item['sha256']]=item
        elif name.endswith('.css'):
            references=re.findall(r'url\([\'"]?([^\)\'";]+)[\'"]?\)',data.decode('utf-8'))
            assert all(not urlsplit(r).scheme for r in references)
        for ref in references:
            dest,fragment=target(name,ref)
            if dest not in content:pending.append(dest)
    # Include current coverage and source identities without copying upstream
    # corpora or unreferenced obsolete generated images into the portable reader.
    for name in ('COVERAGE.json','sources.lock.json'):
        content[name]=(LANG/name).read_bytes()
    content['READ-ME.txt']=('ગુજરાતી ગણિત — ચાલુ અનુવાદનો ઑફલાઇન પ્રારૂપ\n\n'
        'ZIPને સંપૂર્ણ રીતે બહાર કાઢો અને index.html બ્રાઉઝરમાં ખોલો. પુસ્તકની સૂચિ library/index.htmlમાં છે. ફૉન્ટ, ચિત્રો અને શૈલીઓ સાથે જ રાખો. પાઠ વાંચવા ઇન્ટરનેટ કે ખાતું જરૂરી નથી. બાહ્ય સંદર્ભોની મુલાકાત માટે ઇન્ટરનેટ જોઈએ.\n\n'
        'આખા157 પાઠોની સોંપણી ચાલુ છે; COVERAGE.jsonમાં પૂર્ણ અને બાકી કામ જુઓ. ગુજરાતી શિક્ષક અને સહાયક ટેકનોલોજીની સમીક્ષા બાકી છે. ઉમેરેલા ઉકેલો અલગ પૂરક છે.\n\n'
        'pdf/માં પ્રથમ સહાયક એકમની વિદ્યાર્થી અને શિક્ષકની પ્રિન્ટ ફાઇલો છે. તે આખાં પુસ્તકોની PDF નથી અને tagged PDF/UA નથી. સ્ક્રીન વાંચન માટે અર્થપૂર્ણ HTML/MathML ઉપલબ્ધ છે.\n\n'
        'tagged-screen-pdf/માં હોય તે ફાઇલ તકનીકી પ્રારૂપ છે. PDF.jsમાં કેટલાક ગુજરાતી અક્ષરો ગુમાવાની મર્યાદા નોંધેલી છે. તેને પ્રમાણિત સુલભ PDF ન માનો; HTML પાઠને પ્રાથમિકતા આપો.\n\n'
        'શ્રેય અને શરતો notices.htmlમાં છે. OpenStax/Rice University; Indonesian adaptation KokunoYumeto; Gujarati Language Allocation/OpenAI Codex. CC BY-NC-SA4.0; component notices apply. No endorsement.\n').encode('utf-8')
    manifest={'schema':'gujarati-offline-manifest-v1','assignment_complete':False,'entrypoint':'index.html','library':'library/index.html','files':{name:{'bytes':len(data),'sha256':digest(data)} for name,data in sorted(content.items())}}
    content['MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    DEST.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(DEST,'w') as z:
        for name,data in sorted(content.items()):
            info=ZipInfo(name,date_time=(2026,8,30,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data,compresslevel=9)
    # Verify the actual archive and every internal link/fragment, not only the
    # file list assembled before writing it.
    with ZipFile(DEST) as z:
        assert z.testzip() is None
        names=set(z.namelist());assert names==set(content)
        pages={}
        for name in names:
            data=z.read(name);assert digest(data)==digest(content[name])
            if name.endswith('.html'):
                p=References();p.feed(data.decode('utf-8'));pages[name]=p
        for name,page in pages.items():
            assert len(page.ids)==len(set(page.ids)),name
            for ref in page.local:
                dest,fragment=target(name,ref)
                assert dest in names,(name,ref)
                if fragment and dest in pages:assert fragment in pages[dest].ids,(name,ref)
    receipt={'schema':'gujarati-offline-package-qa-v1','result':'pass','assignment_complete':False,'path':DEST.relative_to(LANG).as_posix(),'bytes':DEST.stat().st_size,'sha256':digest(DEST.read_bytes()),'files':len(content),'html_pages_checked':len(pages),'remote_runtime_dependencies':0,'optional_external_reference_count':len(external),'checks':['ZIP CRC','All archived bytes match source hashes','All internal links and fragments','No remote runtime resources','No script or iframe','Reachable local CSS and font closure','Current coverage and attribution included'],'limitations':['Draft package; full assignment remains in progress.','Pilot PDFs are untagged print files.','The full-module tagged technical draft has a recorded PDF.js Gujarati extraction failure; prefer HTML.','Native educator and real assistive-technology review remain pending.']}
    receipt['embedded_raster_images']=list(embedded.values())
    receipt['checks'].append('Strict base64 JPEG/PNG embedding validated and covered by HTML file hashes')
    (LANG/'OFFLINE_QA.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
