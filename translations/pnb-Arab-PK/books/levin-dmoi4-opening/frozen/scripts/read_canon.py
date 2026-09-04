"""Read real Shahmukhi reference passages at each production stage; log usage."""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import datetime
import hashlib
import json
import re
import urllib.request
import sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--stage', required=True, choices=['draft','revision','qa','next-unit'])
parser.add_argument('--ids', nargs='*')
parser.add_argument('--unit', default='PNB-001')
args = parser.parse_args()
index = json.loads((BASE/'canon/examples.json').read_text(encoding='utf-8'))
DL = ROOT/'downloads/canon/pnb-Arab-PK'
DL.mkdir(parents=True,exist_ok=True)

class Visible(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ['script','style']: self.skip+=1
        if tag in ['p','br','div','h1','h2','h3']: self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ['script','style']: self.skip=max(0,self.skip-1)
        if tag in ['p','div','h1','h2','h3']: self.parts.append('\n')
    def handle_data(self,text):
        if not self.skip: self.parts.append(text)

sources={}
for source in index['sources']:
    path=DL/(source['id']+'.html')
    if not path.exists():
        request=urllib.request.Request(source['url'],headers={'User-Agent':'Translation-reference-reader/1.0'})
        with urllib.request.urlopen(request,timeout=60) as response: path.write_bytes(response.read())
    raw=path.read_bytes()
    p=Visible(); p.feed(raw.decode('utf-8'))
    paragraphs=[' '.join(s.split()) for s in ''.join(p.parts).splitlines() if s.strip()]
    (DL/(source['id']+'.txt')).write_text('\n'.join(paragraphs)+'\n',encoding='utf-8')
    sources[source['id']]={'paragraphs':paragraphs,'sha256':hashlib.sha256(raw).hexdigest(),'url':source['url']}

records=[]
for item in index['examples']:
    if args.ids and item['id'] not in args.ids: continue
    s=sources[item['source']]
    matches=[p for p in s['paragraphs'] if item['quote'] in p]
    assert matches, f'Unreadable or missing canon locus: {item["id"]}'
    passage=matches[0]
    assert re.search('[\u0600-\u06ff]',passage)
    at=passage.index(item['quote'])
    window=passage[max(0,at-180):at+len(item['quote'])+250]
    print(f'\n{item["id"]} | {item["focus"]}\n{window}\nApply: {item["application"]}')
    records.append({'id':item['id'],'source_sha256':s['sha256'],'paragraph_sha256':hashlib.sha256(passage.encode()).hexdigest(),'source_url':s['url'],'application':item['application']})
now = datetime.datetime.now(datetime.timezone.utc)
assert re.fullmatch(r'[A-Za-z0-9-]+',args.unit), 'Unsafe unit identifier'
receipt={'stage':args.stage,'unit':args.unit,'read_at':now.isoformat(),'examples':records,'claim':'Passages displayed for agent reading; receipt alone is not evidence of linguistic correctness.'}
(BASE/'canon/receipts').mkdir(exist_ok=True)
(BASE/f'canon/receipts/{args.unit}-{args.stage}-{now.strftime("%Y%m%dT%H%M%S%fZ")}.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
