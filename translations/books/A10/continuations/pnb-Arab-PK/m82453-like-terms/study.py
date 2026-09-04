"""Freeze only the next complete A10 section from an exact read-only predecessor."""
from pathlib import Path
import hashlib,json,copy,urllib.request
import xml.etree.ElementTree as E
from PIL import Image
import sys
B=Path(__file__).resolve().parent
P=Path(sys.argv[1])
C='{http://cnx.rice.edu/cnxml}'; M='{http://www.w3.org/1998/Math/MathML}'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,b):
 p=B/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes) else b.encode())
def dump(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def tag(n):return n.tag.split('}')[-1]
raw=(P/'source/m82453.en.cnxml').read_bytes()
assert sha(raw)=='a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed'
start=raw.rfind(b'<section',0,raw.index(b'fs-id1170655163482'))
end=raw.rfind(b'<section',0,raw.index(b'fs-id1170654942537'))
section=raw[start:end]
wrapped=b'<?xml version="1.0" encoding="utf-8"?>\n<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML" id="a10-unit-009-excerpt">'+section+b'</document>\n'
write('source/m82453.en.cnxml',raw);write('source/a10-unit-009.cnxml',wrapped)
for src,dst in [('source/collection.xml','source/collection.xml'),('LICENSE.txt','LICENSE.txt'),('provenance/A10-release/NOTICE.txt','provenance/A10-notice.txt'),('styles/reader.css','reader.css'),('source/recovered-renderer.py','renderer_base.py')]:write(dst,(P/src).read_bytes())
root=E.fromstring(wrapped); parents={c:p for p in root.iter() for c in p}; paths={}
def walk(n,p):
 paths[n]=p
 for i,c in enumerate(n):walk(c,p+'/'+str(i))
walk(root,'document')
keys={}; english={}
def template(n):
 out=n.text or ''; mi=ci=li=0
 for c in n:
  t=tag(c)
  if t=='math':out+='{{math:'+str(mi)+'}}';mi+=1
  elif t=='link':out+='{{link:'+str(li)+'}}';li+=1
  elif t in {'table','list','media','para','note','figure'}:out+='{{child:'+str(ci)+'}}';ci+=1
  elif t=='emphasis':
   ht='strong' if c.get('effect')=='bold' else 'em';out+='<'+ht+'>'+template(c)+'</'+ht+'>'
  elif t=='term':out+="<span id='"+c.get('id')+"' class='source-term'>"+template(c)+'</span>'
  elif t=='newline':out+='<br />'
  elif t=='span':out+="<bdi dir='ltr'>("+'abcde'['ⓐⓑⓒⓓⓔ'.index(c.text)]+')</bdi>'
  else:raise ValueError(t)
  out+=c.tail or ''
 return out
for n in root.iter():
 t=tag(n);par=parents.get(n)
 key=None
 if t=='title':key=par.get('id')+'/title'
 elif t=='para':key=n.get('id')
 elif t=='item':key=par.get('id')+'/item/'+str(list(par).index(n)+1)
 elif t=='media':key=n.get('id')+'/alt'
 if key:
  keys[key]=paths[n];english[key]=n.get('alt') if t=='media' else template(n)
images=[]
for n in root.iter(C+'media'):
 im=n[0];filename=Path(im.get('src')).name;p=B/'assets'/filename
 url='https://raw.githubusercontent.com/openstax/osbooks-prealgebra-bundle/38cae454e644abf9f0a623e876994553881597c9/media/'+filename
 b=p.read_bytes() if p.exists() else urllib.request.urlopen(url,timeout=45).read();write('assets/'+filename,b)
 with Image.open(p) as image:w,h=image.size;fmt=image.format
 assert fmt=='JPEG'
 images.append({'media_id':n.get('id'),'source_cnxml_src':im.get('src'),'path':'assets/'+filename,'url':url,'bytes':len(b),'sha256':sha(b),'width':w,'height':h,'source_declared_mime':im.get('mime-type'),'original_bilingual_key_id':'image-key','source_alt_override':None})
counts={}
for n in root[0].iter():counts[tag(n)]=counts.get(tag(n),0)+1
exercises=[{'id':n.get('id'),'solution_id':n.find(C+'solution').get('id') if n.find(C+'solution') is not None else None} for n in root.iter(C+'exercise')]
plan={'unit':'A10-009','module':'m82453','source_commit':'38cae454e644abf9f0a623e876994553881597c9','source_sha256':sha(raw),'source_bytes':len(raw),'section_id':'fs-id1170655163482','section_title':'Identify and Combine Like Terms','byte_range':{'start':start,'end_exclusive':end,'bytes':len(section),'sha256':sha(section)},'excerpt_sha256':sha(wrapped),'source_keys_to_paths':keys,'source_ids':[n.get('id') for n in root[0].iter() if n.get('id')],'source_blocks':len(keys),'counts':counts,'images':images,'exercises':exercises,'next_anchor':'fs-id1170654942537','next_title':'Translate an English Phrase to an Algebraic Expression','last_descendant_id':[n.get('id') for n in root[0].iter() if n.get('id')][-1],'tables':[],'example_labels':[{'id':n.get('id'),'local_label':'E'+str(i)} for i,n in enumerate(root.iter(C+'example'),1)],'token_owners':[{'key':k,'group_short_parts':False} for k in keys]}
dump('source/SELECTION.json',plan);dump('source/ENGLISH_BLOCKS.json',english)
print(json.dumps({'range':plan['byte_range'],'blocks':len(keys),'counts':counts,'images':images,'exercises':exercises},ensure_ascii=False))
