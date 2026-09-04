#!/usr/bin/env python3
"""Independent source-bound QA for the rendered B40 opening.

No imports from the preparer, builder or converter. The only local import is a
separate handwritten expected-math fixture module. Detached mutations never
write the reader, inputs, assets or notices.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from lxml import etree as E
from PIL import Image
from b40_opening_math_expected import expected as expected_math

BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[1]
MANIFEST=BASE/"source-excerpts/manifest-b40-opening.json"
TRANSLATION=BASE/"translations/b40-opening.json"
WITNESS=BASE/"source-excerpts/b40-opening.json"
NOTICE=BASE/"provenance/b40-opening-component-notices.json"
READER=BASE/"reader/b40-opening.html"
RECEIPT=BASE/"qa/structural-b40-opening.json"
PRODUCTION_CANON=BASE/"canon/receipts/B40-opening-production-20260901T112205453Z.json"
EN="df2262e089a02651c127f1dd12649c4622ee1383";ID="e84ce2956a7304830c42eba70106f940fefee7c4"
FROZEN={MANIFEST:"a3430810fd1f3259587b5581980280ac78ff2520148c227d677798b5e3eb1239",
 TRANSLATION:"45352c7245ff69768f97dbb12ca0e8926fa25ded46bed2169c62779984daf173",
 WITNESS:"560a16023aa2e93d5f47236320ef5740090b2d786d9f506b6f68d05ac01315f5"}
MATH="http://www.w3.org/1998/Math/MathML";TOKEN=re.compile(r"\{\{(?:tex|url|include|mark):\d+\}\}")
TABLES=[("src/cover/symlist.tex",1,20,2,"table"),("src/cover/symlist.tex",2,13,4,"table"),
 ("src/pref/pref.tex",1,15,2,"table"),("src/pref/pref.tex",2,4,1,"blockquote"),
 ("src/pref/pref.tex",3,5,1,"blockquote"),("src/pref/pref.tex",4,7,1,"address")]

def sha(raw):return hashlib.sha256(raw.encode() if isinstance(raw,str) else raw).hexdigest()
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def jload(path):return json.loads(path.read_text(encoding="utf-8"))
def local(node):return E.QName(node).localname

class Failure(AssertionError):pass
class C:
 def __init__(self):self.n=0
 def eq(self,a,b,label):
  self.n+=1
  if a!=b:raise Failure(label)
 def yes(self,a,label):self.eq(bool(a),True,label)

def parse_reader(text):
 try:
  fixed=re.sub(r"<(meta|img|mspace)\b([^<>]*?)(?<!/)>",r"<\1\2/>",text.replace("<!doctype html>",""))
  return E.fromstring(fixed.encode())
 except E.XMLSyntaxError as exc:raise Failure("html.parse") from exc

def merge(events):
 out=[]
 for e in events:
  if e[0]=="text" and not e[1]:continue
  if e[0]=="text" and out and out[-1][0]=="text":out[-1]=["text",out[-1][1]+e[1]]
  else:out.append(e)
 return out

def events(node,actual=False):
 if actual and node.get("data-source-slot-token"):
  return [["text",node.get("data-source-slot-token")]]
 attrs0={k:v for k,v in node.attrib.items()}
 content=[]
 if node.text:content.append(["text",node.text])
 for child in node:
  content+=events(child,actual)
  if child.tail:content.append(["text",child.tail])
 return [["node",local(node),sorted(attrs0.items()),merge(content)]]

def content_events(container,actual):
 result=[]
 if container.text:result.append(["text",container.text])
 for child in container:
  result+=events(child,actual)
  if child.tail:result.append(["text",child.tail])
 return merge(result)

def math_descriptor(node):
 return [local(node),{k:v for k,v in node.attrib.items()},node.text,
         [math_descriptor(c) for c in node]]

def git(repo,pin,path):return subprocess.check_output(["git","-C",str(repo),"show",pin+":"+path])

def context(m):
 c=C();files={}
 for role,pin in [("canonical",EN),("comparison",ID)]:
  a=m[role];c.eq(a["commit"],pin,"pin.commit");repo=ROOT/a["local_path"]
  c.eq(subprocess.check_output(["git","-C",str(repo),"rev-parse",pin+"^{tree}"]).decode().strip(),a["tree"],"pin.tree")
  for row in m["source_files"][role]:
   raw=git(repo,pin,row["repository_path"]);c.eq(sha(raw),row["sha256"],"pin.source-sha")
   c.eq(len(raw),row["bytes"],"pin.source-bytes");c.eq(blob(raw),row["git_blob_sha1"],"pin.source-blob")
   c.eq((repo/row["repository_path"]).read_bytes().replace(b"\r\n",b"\n"),raw,"pin.working-LF")
   files[(role,row["repository_path"])]=raw
  if role=="canonical":
   for asset in m["source_assets"]:
    raw=git(repo,pin,asset["repository_path"]);c.eq(sha(raw),asset["sha256"],"pin.asset-sha")
    c.eq(len(raw),asset["bytes"],"pin.asset-bytes");c.eq(blob(raw),asset["git_blob_sha1"],"pin.asset-blob")
    files[(role,asset["repository_path"])]=raw
 return {"checks":c.n,"files":files}

def expected_visual_order(m):
 cover=["src/cover/covernew.tex#metadata/title","src/cover/covernew.tex#metadata/author"]+[
  "src/sty/covergraphic.sty#visible/"+x for x in ["title","author","edition","webaddress"]]
 sy=sorted([b for b in m["source_blocks"] if b["source_file"]=="src/cover/symlist.tex"],key=lambda b:b["source_start"])
 pf=sorted([b for b in m["source_blocks"] if b["source_file"]=="src/pref/pref.tex"],key=lambda b:b["source_start"])
 out=cover+[b["key"] for b in sy]
 include="src/pref/pref.tex#table/4/row/6/cell/1"
 for b in pf:
  out.append(b["key"])
  if b["key"]==include:out.append("src/publicationdate.tex#date")
 return out

def validate(reader_text,m,t,n,ctx):
 c=C();root=parse_reader(reader_text)
 c.eq(root.get("lang"),"pnb-Arab-PK","html.lang");c.eq(root.get("dir"),"rtl","html.dir")
 body=root.find("body");c.eq(body.get("class"),"b40-opening","html.body")
 c.eq(root.xpath("//script|//iframe|//object|//embed"),[],"html.no-runtime")
 css="\n".join(root.xpath("//style/text()"))
 c.yes("@media(max-width:600px){" in css,"css.mobile-media-query")
 mobile=css.rsplit("@media(max-width:600px){",1)[1].split("\n}",1)[0]
 compact=re.sub(r"\s+","",mobile)
 c.yes(".b40-opening.b40-cover-components{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));align-items:end}" in compact,
       "css.mobile-grid-minmax")
 c.yes(".b40-opening.source-cover-component{min-width:0;max-width:100%}" in compact,
       "css.mobile-component-min-width")
 c.yes(".b40-opening.source-cover-componentimg,.b40-opening.source-cover-component:first-childimg{min-width:0;width:auto;max-width:100%;height:auto;max-height:15rem}" in compact,
       "css.mobile-image-min-width")
 c.yes("min-width:640px" not in compact,"css.mobile-no-inherited-640")
 ids=root.xpath("//@id");c.eq(len(ids),len(set(ids)),"html.unique-ids")
 c.eq(root.xpath("//meta[@name='source-author']/@content"),["Jim Hefferon"],"metadata.author")
 c.eq(root.xpath("//meta[@name='source-edition']/@content"),["Fourth edition, second printing"],"metadata.edition")
 c.eq(root.xpath("//meta[@name='source-publication-date']/@content"),["2021-Oct-12"],"metadata.date")
 article=root.xpath("//*[@id='b40-opening-source']");c.eq(len(article),1,"source.article")
 article=article[0];c.eq(article.xpath(".//*[@data-origin='original-bridge']"),[],"source.no-original-injection")
 nodes=article.xpath(".//*[@data-source-key]")
 c.eq([x.get("data-source-key") for x in nodes],expected_visual_order(m),"source.visual-order")
 c.eq(len(nodes),174,"source.174-once")
 blocks={b["key"]:b for b in m["source_blocks"]}
 for key in m["expected_source_keys"]:
  got=article.xpath(".//*[@data-source-key=$k]",k=key);c.eq(len(got),1,"source.owner-once:"+key)
  node=got[0];b=blocks[key]
  c.eq(node.get("data-source-kind"),b["kind"],"source.kind:"+key)
  c.eq(node.get("data-source-file"),b["source_file"],"source.file:"+key)
  c.eq(node.get("data-source-start"),str(b["source_start"]),"source.start:"+key)
  c.eq(node.get("data-source-end"),str(b["source_end"]),"source.end:"+key)
  c.eq(node.get("data-source-raw-sha256"),b["source_raw_sha256"],"source.raw-hash:"+key)
  source=ctx["files"][("canonical",b["source_file"])].decode()
  c.eq(source[b["source_start"]:b["source_end"]],b["source_raw"],"source.raw-slice:"+key)
  containers=node.xpath("./span[@class='source-content']");c.eq(len(containers),1,"source.content:"+key)
  expected=E.fromstring(("<fragment>"+t["source_blocks"][key]+"</fragment>").encode())
  c.eq(content_events(containers[0],True),content_events(expected,False),"source.target-exact:"+key)
 slots=[(b,s) for b in m["source_blocks"] for s in b["slots"]]
 rendered=article.xpath(".//*[@data-source-slot-token]")
 c.eq(len(rendered),len(slots),"slots.count")
 expected_slots=[(b["key"],s["token"],s["kind"]) for b,s in slots]
 actual_slots=[]
 for e in rendered:
  owner=next(x.get("data-source-key") for x in e.iterancestors() if x.get("data-source-key"))
  actual_slots.append((owner,e.get("data-source-slot-token"),e.get("data-source-slot-kind")))
 c.eq(actual_slots,expected_slots,"slots.owner-order")
 mathslots=[(b,s) for b,s in slots if s["kind"]=="tex"]
 formulas=article.xpath(".//*[@data-source-slot-kind='tex']");c.eq(len(formulas),76,"math.owners76")
 records=n["math_records"];c.eq(len(records),76,"math.notice76")
 fallbacks=root.xpath("//*[@data-source-tex-fallback='true']");c.eq(len(fallbacks),76,"math.fallback76")
 for i,((b,s),e,rec,fb) in enumerate(zip(mathslots,formulas,records,fallbacks),1):
  c.eq(rec["number"],i,"math.number");c.eq(rec["owner"],b["key"],"math.record-owner")
  c.eq(rec["slot_token"],s["token"],"math.record-token");c.eq(rec["source_raw"],s["raw"],"math.record-raw")
  c.eq(rec["source_tex"],s["value"],"math.record-tex");c.eq(rec["source_delimiters"],s["delimiters"],"math.record-delimiters")
  c.eq(e.get("data-source-tex"),s["value"],"math.dom-tex");c.eq(e.get("data-source-tex-raw"),s["raw"],"math.dom-raw")
  c.eq(e.get("data-source-tex-sha256"),sha(s["value"]),"math.dom-hash")
  children=list(e);c.eq([local(x) for x in children],["math","a"],"math.wrapper-shape")
  c.eq(children[0].tail,None,"math.wrapper-tail");c.eq(children[1].tail,None,"math.link-tail")
  math=children[0];c.eq(math.get("dir"),"ltr","math.ltr");c.eq(math.get("display"),"inline","math.inline")
  sem=list(math);c.eq(len(sem),1,"math.semantics-one");c.eq(local(sem[0]),"semantics","math.semantics")
  payload=list(sem[0]);c.eq(len(payload),2,"math.payload-two");c.eq(local(payload[1]),"annotation","math.annotation")
  c.eq(payload[1].get("encoding"),"application/x-tex","math.annotation-encoding");c.eq(payload[1].text,s["value"],"math.annotation-raw")
  tree=math_descriptor(payload[0]);fixture=expected_math(s["value"])
  c.eq(tree,fixture,"math.handwritten-tree");c.eq(rec["tree"],fixture,"math.notice-tree")
  c.eq(rec["tree_sha256"],sha(json.dumps(fixture,ensure_ascii=False,separators=(",",":"))),"math.tree-hash")
  c.eq("".join(x["raw"] for x in rec["tokens"]),s["value"],"math.reversible-ledger")
  c.yes(all(x["effect"] for x in rec["tokens"]),"math.token-effects")
  c.yes(all(x["mathml_paths"] or x["kind"]=="space" or x["effect"].startswith("nonprinting") for x in rec["tokens"]),"math.token-paths")
  c.eq(fb.text,s["raw"],"math.raw-fallback")
  detail=fb.getparent().getparent() if local(fb.getparent())=="pre" else None;c.yes(detail is not None,"math.fallback-shape")
  c.eq(detail.get("data-tex-owner"),b["key"],"math.fallback-owner")
  link=children[1];c.eq(link.get("href"),"#source-tex-"+str(i).zfill(3),"math.link-target")
 c.eq(sum(bool(x["normalizations"]) for x in records),4,"math.nbym-normalization-owners")
 c.eq([x["normalizations"][0]["command"] for x in records if x["normalizations"]],["\\nbym","\\nbym","\\nbym","\\nbyn"],"math.normalization-order")
 # Other source slots: exact URL, mark and include rendering.
 bykey={(b["key"],s["token"]):(b,s) for b,s in slots}
 for e in article.xpath(".//*[@data-source-slot-kind='url']"):
  owner=next(x.get("data-source-key") for x in e.iterancestors() if x.get("data-source-key"))
  s=bykey[(owner,e.get("data-source-slot-token"))][1];value=s["value"]
  c.eq(e.get("data-source-url"),value,"url.source");c.eq(e.get("href"),value if value.startswith("http") else "https://"+value,"url.href")
  c.eq("".join(e.itertext()),value,"url.label")
 for e in article.xpath(".//*[@data-source-slot-kind='mark']"):
  owner=next(x.get("data-source-key") for x in e.iterancestors() if x.get("data-source-key"))
  s=bykey[(owner,e.get("data-source-slot-token"))][1]
  c.eq(e.get("data-source-mark"),s["value"],"mark.source");c.eq("".join(e.itertext()),"?" if s["value"]=="puzzlemark" else "✓","mark.glyph")
 inc=article.xpath(".//*[@data-source-slot-kind='include']");c.eq(len(inc),1,"include.once")
 c.eq(inc[0].get("data-source-include"),"publicationdate","include.target")
 c.eq(inc[0].xpath(".//*[@data-source-key]/@data-source-key"),["src/publicationdate.tex#date"],"include.date-owner")
 # Six source tabular environments retain meaning; only three are HTML tables.
 c.eq(len(article.xpath(".//table")),3,"tables.only-three-semantic")
 for file,num,rows,cols,tag in TABLES:
  x=article.xpath(f".//{tag}[@data-source-file=$f][@data-source-table=$n]",f=file,n=str(num));c.eq(len(x),1,"table.owner")
  e=x[0]
  if tag=="table":
   rr=e.xpath("./thead/tr|./tbody/tr");c.eq(len(rr),rows,"table.rows")
   c.eq([r.get("data-source-row") for r in rr],[str(i) for i in range(1,rows+1)],"table.row-order")
   c.eq([len(r.xpath("./th|./td")) for r in rr],[cols]*rows,"table.columns")
  else:
   rr=e.xpath("./p");c.eq(len(rr),rows,"lineated.rows")
   c.eq([r.get("data-source-row") for r in rr],[str(i) for i in range(1,rows+1)],"table.row-order")
 c.eq(len(article.xpath(".//table[@class='source-notation']/thead")),0,"notation.no-invented-header")
 c.eq(len(article.xpath(".//table[@class='source-greek']/thead/tr/th")),4,"greek.headers4")
 c.eq(len(article.xpath(".//table[@class='source-schedule']/thead/tr/th")),2,"schedule.headers2")
 c.eq(len(article.xpath(".//blockquote[@class='source-quote']")),2,"quotes.not-numeric")
 c.eq(len(article.xpath(".//address[@class='source-credit']/p")),7,"credits.address7")
 # Source punctuation roles.
 schedule=["".join(x.itertext()) for x in article.xpath(".//table[@class='source-schedule']//td[last()]")]
 for value in schedule:
  c.yes("−" not in value and "—" not in value and "--" not in value,"punct.schedule-not-minus-em")
 c.eq(sum(v.count("–") for v in schedule),17,"punct.schedule-en-dashes")
 prose=["".join(article.xpath(".//*[@data-source-key=$k]//span[@class='source-content']",k=k)[0].itertext()) for k in
        ["src/pref/pref.tex#paragraph/2","src/pref/pref.tex#paragraph/18"]]
 c.eq([x.count("—") for x in prose],[1,1],"punct.prose-em-dash")
 pure=[t["source_blocks"][f"src/cover/symlist.tex#table/1/row/{r}/cell/1"] for r in range(1,21)]
 c.yes(all("،" not in TOKEN.sub("",x) for x in pure),"punct.pure-math-ascii")
 # Exact assets, links, alts and component evidence.
 c.eq(n["schema"],"b40-opening-retained-component-evidence-v1","notice.schema")
 c.eq(n["source_specific_license"],"Creative Commons Attribution-ShareAlike 2.5","notice.license")
 c.eq(n["canonical"],m["canonical"],"notice.canonical");c.eq(n["comparison"],m["comparison"],"notice.comparison")
 c.eq(n["manifest_sha256"],sha(MANIFEST.read_bytes()),"notice.manifest")
 c.eq(n["translation_sha256"],sha(TRANSLATION.read_bytes()),"notice.translation")
 c.eq(n["witness_sha256"],sha(WITNESS.read_bytes()),"notice.witness")
 c.eq(n["whole_frontmatter_complete"],False,"scope.frontmatter");c.eq(n["whole_book_translation_complete"],False,"scope.book");c.eq(n["whole_assignment_complete"],False,"scope.assignment")
 c.eq([x["source_path"] for x in n["components"]],["src/cover/asy/shadow.pdf","src/cover/asy/axesgraphic.pdf"],"assets.layer-order")
 alts={x["repository_path"]:x for x in t["original_accessibility_alts"]}
 figures=article.xpath(".//figure[@data-source-component]");c.eq(len(figures),2,"assets.figures2")
 for comp,figure in zip(n["components"],figures):
  src=ctx["files"][("canonical",comp["source_path"])];pdf=BASE/comp["prepared_path"];png=BASE/comp["preview"]["path"]
  c.eq(pdf.read_bytes(),src,"assets.exact-pdf");c.eq(sha(src),comp["source_sha256"],"assets.pdf-sha")
  c.eq(blob(src),comp["source_git_blob_sha1"],"assets.pdf-blob");c.eq(len(src),comp["source_bytes"],"assets.pdf-bytes")
  c.eq(sha(png.read_bytes()),comp["preview"]["sha256"],"assets.preview-sha");c.eq(len(png.read_bytes()),comp["preview"]["bytes"],"assets.preview-bytes")
  with Image.open(png) as im:
   c.eq(im.mode,"RGBA","assets.preview-RGBA");c.eq(list(im.size),[comp["preview"]["width"],comp["preview"]["height"]],"assets.preview-dim")
   c.eq(list(im.getchannel("A").getextrema()),comp["preview"]["alpha_extrema"],"assets.preview-alpha")
  img=figure.find("img");a=alts[comp["source_path"]]
  c.eq(img.get("src"),"../"+comp["preview"]["path"],"assets.image-src");c.eq(img.get("alt"),a["alt_pnb"],"assets.original-alt")
  c.eq(img.get("data-alt-origin"),"original-accessibility-description","assets.alt-origin")
  c.eq(img.get("data-source-alt-present"),"false","assets.no-source-alt");c.eq(img.get("data-source-pdf-sha256"),comp["source_sha256"],"assets.dom-pdf-hash")
  links=figure.xpath(".//a/@href");c.eq(links,["../"+comp["prepared_path"]],"assets.pdf-link")
 c.eq(n["source_layer_order"],[{"path":"src/cover/asy/shadow.pdf","put":["-0.0","-6.9"]},{"path":"src/cover/asy/axesgraphic.pdf","put":["0","-6.5"]}],"assets.offset-ledger")
 # Actual readable canon was consulted again during production QA.
 canon=jload(PRODUCTION_CANON);c.eq(canon["stage"],"production-qa","canon.production-stage")
 c.eq([x["example"] for x in canon["examples"]],["C01","C02","C03","C04","C09"],"canon.production-loci")
 for x in canon["examples"]:
  raw=(ROOT/x["path"]).read_bytes();c.eq(sha(raw),x["text_raw_sha256"],"canon.file-hash")
  line=raw.decode("utf-8").splitlines()[x["line"]-1];c.eq(sha(line),x["paragraph_sha256"],"canon.paragraph-hash")
  c.yes(bool(x["application"]),"canon.application")
 # Existing notice bytes and distinct B40 license.
 c.eq(m["retained_notices"]["selected_license"],"CC-BY-SA-2.5","notice.selected")
 for r in m["retained_notices"]["inputs"]:
  raw=(BASE/r["path"]).read_bytes();c.eq(sha(raw),r["raw_sha256"],"notice.input-raw");c.eq(sha(raw.replace(b"\r\n",b"\n")),r["logical_lf_sha256"],"notice.input-LF")
 # Original bridge is separate and source article contains no anonymous authored node.
 notes=root.xpath("//*[@id='b40-opening-original-notes']//*[@data-origin][starts-with(@data-origin,'original-')]")
 c.eq(len(notes),5,"original.notes5")
 c.eq([x.get("id") for x in notes],[x["id"] for x in t["original_notes"]],"original.note-order")
 allowed_struct={"article","section","div","table","thead","tbody","tr","blockquote","address","figure","figcaption"}
 for e in article.iterdescendants():
  inside_content=any("source-content" in (x.get("class") or "").split() for x in [e]+list(e.iterancestors()))
  inside_slot=any(x.get("data-source-slot-token") for x in [e]+list(e.iterancestors()))
  inside_math=any(local(x)=="math" for x in [e]+list(e.iterancestors()))
  inside_component=any(x.get("data-source-component") for x in [e]+list(e.iterancestors()))
  inside_table_group=local(e) in {"thead","tbody"} and any(x.get("data-source-table") for x in e.iterancestors())
  identified=(e.get("data-source-key") or e.get("data-source-section") or e.get("data-source-table") or
              e.get("data-source-row") or e.get("data-source-component") or e.get("data-origin") or
              "source-content" in (e.get("class") or "").split())
  if not (inside_content or inside_slot or inside_math or inside_component or inside_table_group or identified):
   c.yes(local(e) in allowed_struct and (e.get("class")=="b40-cover-components"),"source.no-anonymous-injection")
 c.eq(root.xpath("//article[@id='b40-opening-source']//text()[contains(.,'{{')]"),[],"source.no-placeholder-text")
 c.yes("tableofcontents" not in reader_text and "Starred subsections are optional" not in reader_text,"scope.stops-before-TOC")
 return c.n

def mutate(reader,m,t,n,ctx):
 results=[]
 def test(name,change,prefix):
  rr=reader;mm=copy.deepcopy(m);tt=copy.deepcopy(t);nn=copy.deepcopy(n)
  changed=change(rr,mm,tt,nn)
  if isinstance(changed,str):rr=changed
  try:validate(rr,mm,tt,nn,ctx)
  except Failure as e:
   if not str(e).startswith(prefix):raise Failure(f"mutation {name}: {e}; expected {prefix}")
   results.append({"name":name,"rejected_by":str(e)})
  else:raise Failure("MUTATION ACCEPTED: "+name)
 def rep(a,b):return lambda rr,mm,tt,nn:rr.replace(a,b,1)
 test("source-paragraph-text",rep("ایہہ کتاب طالب علماں","ایہہ پوری کتاب مکمل اے تے طالب علماں"),"source.target-exact")
 test("source-owner-key",rep('data-source-key="src/pref/pref.tex#paragraph/1"','data-source-key="src/pref/pref.tex#paragraph/999"'),"source.visual-order")
 test("source-owner-omission",rep(' data-source-key="src/pref/pref.tex#paragraph/1"',''),"source.visual-order")
 test("source-raw-hash",rep('data-source-raw-sha256="62247f89cded3313859de7fea8ad3cc63a3b981db21209711a64af58ce4e3e11"','data-source-raw-sha256="'+"0"*64+'"'),"source.raw-hash")
 test("table-cell-data",rep("قدرتی عدد ","منفی عدد "),"source.target-exact")
 test("table-cell-tag",rep('<td data-source-key="src/cover/symlist.tex#table/1/row/2/cell/1"','<th data-source-key="src/cover/symlist.tex#table/1/row/2/cell/1"'),"html.parse")
 test("table-row-regroup",rep('data-source-row="2"','data-source-row="22"'),"table.row-order")
 test("quote-as-numeric-table",rep('<blockquote class="source-quote"','<table class="source-quote"'),"html.parse")
 test("credit-not-address",rep('<address class="source-credit"','<div class="source-credit"'),"html.parse")
 test("publication-date",rep("2021-Oct-12","2026-Sep-01"),"metadata.date")
 test("credit-name",rep("Stephen Jay Gould","James Joyce"),"source.target-exact")
 test("schedule-range-minus",rep("One.I.1–2","One.I.1−2"),"source.target-exact")
 test("prose-em-to-en",rep("طریقہ اپناؤندی اے—","طریقہ اپناؤندی اے–"),"source.target-exact")
 test("source-url-target",rep('href="https://hefferon.net/linearalgebra"','href="https://example.invalid"'),"url.href")
 test("source-mark-glyph",rep('data-source-mark="puzzlemark" dir="ltr">?</span>','data-source-mark="puzzlemark" dir="ltr">!</span>'),"mark.glyph")
 test("math-source-variable",rep('data-source-tex=" h_{i,j} "','data-source-tex=" h_{j,i} "'),"math.dom-tex")
 test("math-wrapper-extra-text",rep('</math><a class="tex-link"','</math>999<a class="tex-link"'),"math.wrapper-tail")
 test("math-annotation",rep('encoding="application/x-tex"> \\Re </annotation>','encoding="application/x-tex"> R </annotation>'),"math.annotation-raw")
 test("math-unicode-R-erasure",rep('mathvariant="normal">ℝ</mi>','mathvariant="normal">R</mi>'),"math.handwritten-tree")
 test("math-greek-case",rep(">Γ</mi>",">γ</mi>"),"math.handwritten-tree")
 test("math-operator",rep(">≅</mo>",">=</mo>"),"math.handwritten-tree")
 test("math-script-group",rep("<msub><mi>h</mi><mrow>","<msub><mi>h</mi>"),"html.parse")
 test("math-spacing-erasure",rep('<mspace width="0.1667em"/>',''),"math.handwritten-tree")
 test("math-fallback-raw",rep(r'<code data-source-tex-fallback="true">\( \Re \)</code>',r'<code data-source-tex-fallback="true">\( R \)</code>'),"math.raw-fallback")
 def ledger(rr,mm,tt,nn):
  nn["math_records"][0]["tokens"][0]["raw"]="X";return None
 test("math-ledger",ledger,"math.reversible-ledger")
 def tree_notice(rr,mm,tt,nn):
  nn["math_records"][0]["tree"][3][0][2]="R";return None
 test("math-notice-tree",tree_notice,"math.notice-tree")
 def normalization(rr,mm,tt,nn):
  nn["math_records"][20]["normalizations"]=[];return None
 test("math-normalization-erasure",normalization,"math.nbym-normalization-owners")
 test("image-src",rep("b40-opening-shadow-transparent.png","missing-shadow.png"),"assets.image-src")
 test("image-pdf-hash",rep('data-source-pdf-sha256="f352c409ac0c97112b2844217b8b34c90562e616c7426f18bc188bc90473fd5a"','data-source-pdf-sha256="'+"0"*64+'"'),"assets.dom-pdf-hash")
 test("image-invented-source-alt",rep('data-source-alt-present="false"','data-source-alt-present="true"'),"assets.no-source-alt")
 test("pdf-link-target",rep("../assets/b40/b40-opening-shadow.pdf","../assets/b40/b40-opening-axesgraphic.pdf"),"assets.pdf-link")
 def comp(rr,mm,tt,nn):
  nn["components"][0]["source_sha256"]="0"*64;return None
 test("component-source-hash",comp,"assets.pdf-sha")
 def license(rr,mm,tt,nn):
  nn["source_specific_license"]="CC-BY-NC-SA-4.0";return None
 test("wrong-license",license,"notice.license")
 def scope(rr,mm,tt,nn):
  nn["whole_frontmatter_complete"]=True;return None
 test("false-frontmatter-complete",scope,"scope.frontmatter")
 test("original-bridge-inside-source",rep('</article><section id="b40-opening-original-notes"','<aside data-origin="original-bridge">مصنف نے ثابت کیا۔</aside></article><section id="b40-opening-original-notes"'),"source.no-original-injection")
 test("anonymous-source-injection",rep('</article><section id="b40-opening-original-notes"','<p>999</p></article><section id="b40-opening-original-notes"'),"source.no-anonymous-injection")
 test("TOC-overreach",rep('<article id="b40-opening-source">','<article id="b40-opening-source"><p data-origin="renderer-ui">Starred subsections are optional</p>'),"scope.stops-before-TOC")
 test("mobile-cover-grid-min-content-regression",
      rep("grid-template-columns:repeat(2,minmax(0,1fr))","grid-template-columns:1fr 1fr"),
      "css.mobile-grid-minmax")
 test("mobile-cover-inherited-640-regression",
      rep("min-width:0;width:auto;max-width:100%;height:auto;max-height:15rem",
          "width:auto;max-width:100%;height:auto;max-height:15rem"),
      "css.mobile-image-min-width")
 return results

def main():
 if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
 for p,h in FROZEN.items():
  if sha(p.read_bytes())!=h:raise Failure("frozen.input:"+p.name)
 m,t,n=jload(MANIFEST),jload(TRANSLATION),jload(NOTICE);reader=READER.read_text(encoding="utf-8")
 ctx=context(m);checks=ctx["checks"]+validate(reader,m,t,n,ctx);mutations=mutate(reader,m,t,n,ctx)
 paths=[MANIFEST,TRANSLATION,WITNESS,NOTICE,READER,Path(__file__).resolve(),
        BASE/"scripts/b40_opening_tex.py",BASE/"scripts/b40_opening_math_expected.py",
        BASE/"scripts/prepare_b40_opening.py",BASE/"scripts/build_b40_opening.py",
        BASE/"qa/b40-opening-language-notes.md",PRODUCTION_CANON]
 receipt={"schema":"pnb-b40-opening-source-bound-reader-qa-v1","unit":"B40-opening",
  "status":"passed production checkpoint","checks":checks,"detached_mutation_count":len(mutations),
  "counts":{"source_keys":174,"math_owners":76,"source_tabular_environments":6,
            "semantic_html_tables":3,"lineated_quotes":2,"credit_address_blocks":1,
            "source_pdf_components":2,"transparent_component_previews":2},
  "source_pins":{"canonical":EN,"comparison":ID},
  "production_canon_receipt":{"path":PRODUCTION_CANON.relative_to(BASE).as_posix(),"sha256":sha(PRODUCTION_CANON.read_bytes())},
  "file_hashes":{p.relative_to(BASE).as_posix():sha(p.read_bytes()) for p in paths},
  "asset_hashes":{p.relative_to(BASE).as_posix():sha(p.read_bytes()) for p in sorted((BASE/"assets/b40").glob("b40-opening-*"))},
  "detached_mutations":mutations,
  "limits":["The finite parser covers only the 76 observed B40-opening formulas; it is not universal TeX support. Unknown syntax fails closed.",
   "Hefferon nbym/nbyn negative thin spaces are explicit normalization records; MathML Core handles multiplication spacing while raw TeX and macro evidence remain exact.",
   "The two PNGs are transparent Poppler component previews, displayed separately in source layer order. They are not an exact upstream TeX cover composite.",
   "Punjabi source-block seals and exact DOM comparisons detect changes after actual source/canon review; they do not establish native-language or educator certification.",
   "No TeX, Asymptote, upstream code, network service, analytics or grading runtime ran. Browser, mobile and assistive-technology review remain parent work.",
   "The reader stops before generated contents and the starred-subsection explanation. Neither whole front matter, B40, nor the five-work assignment is complete."],
  "whole_frontmatter_complete":False,"whole_book_translation_complete":False,"whole_assignment_complete":False}
 RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(json.dumps({"status":"passed","checks":checks,"detached_mutations":len(mutations),
                   "reader_sha256":sha(READER.read_bytes()),"notice_sha256":sha(NOTICE.read_bytes()),
                   "receipt_sha256":sha(RECEIPT.read_bytes())}))

if __name__=="__main__":main()
