"""Download HTML-only reference witnesses and readable text; no learner data."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import hashlib, json, urllib.request
L=Path(__file__).resolve().parents[1]
D=L.parent/'downloads/bn-Beng-BD/canon'
class Readable(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,t,a):
        if t in ('script','style','svg'): self.skip+=1
        if t in ('p','h1','h2','h3','h4','h5','li','tr','br'): self.parts.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style','svg'): self.skip=max(0,self.skip-1)
    def handle_data(self,d):
        if not self.skip: self.parts.append(d)
def fetch(s):
    try:
        raw=urllib.request.urlopen(urllib.request.Request(s['url'],headers={'User-Agent':'LanguageAllocation-reference-reader/1.0'}),timeout=45).read()
        D.mkdir(parents=True,exist_ok=True)
        (D/(s['id']+'.html')).write_bytes(raw)
        p=Readable();p.feed(raw.decode('utf-8'))
        txt='\n'.join(' '.join(line.split()) for line in ''.join(p.parts).splitlines() if line.strip())
        (D/(s['id']+'.txt')).write_text(txt,encoding='utf-8',newline='\n')
        return {'id':s['id'],'url':s['url'],'status':'downloaded','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'text_sha256':hashlib.sha256(txt.encode()).hexdigest(),'text_chars':len(txt),'ocr':'not_applicable_native_HTML'}
    except Exception as e: return {'id':s['id'],'url':s['url'],'status':'failed','error':str(e)}
def main():
    sources=json.loads((L/'canon/register.json').read_text(encoding='utf-8'))['sources']
    receipt_path=L/'canon/download-receipt.json'
    locked={x['id']:x for x in json.loads(receipt_path.read_text(encoding='utf-8'))} if receipt_path.exists() else {}
    results=[];missing=[]
    for source in sources:
        if source['id'] not in locked:
            assert not (D/(source['id']+'.html')).exists(), 'Inspect unreceipted reference before replacing it'
            missing.append(source);continue
        item=locked[source['id']]
        assert item['url']==source['url'] and item['status']=='downloaded'
        assert hashlib.sha256((D/(source['id']+'.html')).read_bytes()).hexdigest()==item['sha256']
        text=(D/(source['id']+'.txt')).read_text(encoding='utf-8')
        assert hashlib.sha256(text.encode('utf-8')).hexdigest()==item['text_sha256']
        results.append(item)
    with ThreadPoolExecutor(max_workers=3) as pool: results.extend(pool.map(fetch,missing))
    assert all(x['status']=='downloaded' for x in results),results
    results.sort(key=lambda x:x['id'])
    (L/'canon/download-receipt.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'preserved_existing':len(locked),'newly_acquired':[x for x in results if x['id'] not in locked]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
