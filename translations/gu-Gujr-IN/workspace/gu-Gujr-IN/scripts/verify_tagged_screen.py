"""Inspect real PDF tags, marked content, logical text, fonts and destinations."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
import subprocess

from lxml import html
from pypdf import PdfReader
from pypdf._font import Font
from pypdf.generic import ContentStream
from tagged_screen_pipeline import digest, norm, struct_walk


def compact(s): return re.sub(r"\s+", "", s)


def decode_raw(value, font):
    if isinstance(value, str): return value
    if isinstance(font.encoding, str):
        s = bytes(value).decode(font.encoding, errors="replace")
    else:
        s = "".join(font.encoding.get(b, chr(b)) for b in value)
    return "".join(font.character_map.get(c, c) for c in s)


def replacement(value):
    if isinstance(value, str): return value
    b = bytes(value)
    return b.decode("utf-16" if b.startswith((b"\xfe\xff", b"\xff\xfe")) else "utf-8")


def marked_text(reader, page, font_cache):
    fonts={}
    for k,v in page["/Resources"].get("/Font",{}).items():
        if v.idnum not in font_cache:font_cache[v.idnum]=Font.from_font_resource(v.get_object())
        fonts[str(k)]=font_cache[v.idnum]
    stream = ContentStream(page.get_contents(), reader, "bytes")
    texts = defaultdict(str); stack=[]; seen=[]; font=None; actual_count=0; unmarked=[]
    def current_mcid(): return next((s[0] for s in reversed(stack) if s[0] is not None), None)
    def has_actual(): return any(s[1] for s in stack)
    for operands, op in stream.operations:
        if op in (b"BDC", b"BMC"):
            props = operands[1] if op == b"BDC" and len(operands)>1 else {}
            if not hasattr(props,"get"): props={}
            mid=props.get("/MCID"); actual=props.get("/ActualText")
            if mid is not None: seen.append(int(mid))
            parent_actual=has_actual()
            stack.append((int(mid) if mid is not None else None,actual is not None,str(operands[0])=='/Artifact'))
            if actual is not None:
                actual_count+=1
                if not parent_actual and current_mcid() is not None: texts[current_mcid()]+=replacement(actual)
        elif op == b"EMC":
            if not stack: raise ValueError("Unbalanced marked-content close")
            stack.pop()
        elif op == b"Tf": font=fonts[str(operands[0])]
        elif op in (b"Tj",b"TJ",b"'",b'"') and font and not has_actual():
            values=operands[0] if op==b"TJ" else [operands[-1]]
            value="".join(decode_raw(v,font) for v in values if isinstance(v,(str,bytes)))
            mid=current_mcid()
            if mid is None:
                if value.strip() and not any(s[2] for s in stack): unmarked.append(value)
            else: texts[mid]+=value
    if stack: raise ValueError("Unclosed marked-content sequence")
    return dict(texts), seen, actual_count, unmarked


def number_tree(node):
    node=node.get_object();out={}
    nums=node.get("/Nums",[])
    for i in range(0,len(nums),2):out[int(nums[i])]=nums[i+1].get_object()
    for child in node.get("/Kids",[]):out.update(number_tree(child))
    return out


def verify(pdf, manifest_path, print_path, receipt, text_path):
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    printed=json.loads(print_path.read_text(encoding="utf-8"))
    r=PdfReader(pdf);root=r.trailer["/Root"];tree=root["/StructTreeRoot"]
    parents=number_tree(tree["/ParentTree"])
    page_index={p.indirect_reference.idnum:i for i,p in enumerate(r.pages)}
    marked={};content_ids={};actual_count=0;unmarked=[];font_info={};font_cache={}
    for i,p in enumerate(r.pages):
        text, mids, actual, untagged=marked_text(r,p,font_cache)
        marked[i]=text;content_ids[i]=mids;actual_count+=actual
        unmarked.extend({"page":i+1,"text":x} for x in untagged)
        for ref in p["/Resources"].get("/Font",{}).values():
            f=ref.get_object();sub=str(f.get("/Subtype"));desc=f.get("/FontDescriptor")
            if not desc and f.get("/DescendantFonts"):desc=f["/DescendantFonts"][0].get_object().get("/FontDescriptor")
            embedded=(bool(f.get("/CharProcs")) if sub=="/Type3" else bool(desc and any(k in desc.get_object() for k in ("/FontFile","/FontFile2","/FontFile3"))))
            font_info[ref.idnum]={"subtype":sub,"name":str(f.get("/BaseFont","Type3 embedded glyph programs")),"embedded":embedded,"to_unicode":"/ToUnicode" in f}
    structure_refs=[];heading_rows=[];figure_rows=[];formula_rows=[]
    def walk(item, inherited_pg=None, owner=None):
        if isinstance(item,list):return "".join(walk(c,inherited_pg,owner) for c in item)
        if isinstance(item,int):
            if inherited_pg is None:raise ValueError("MCID without page")
            pi=page_index[inherited_pg.idnum];mid=int(item)
            structure_refs.append((pi,mid,owner))
            return marked[pi].get(mid,"")
        if not hasattr(item,"get_object"):return ""
        obj=item.get_object()
        if not hasattr(obj,"get"):return ""
        pg=obj.raw_get("/Pg") if "/Pg" in obj else inherited_pg
        if obj.get("/Type")=="/MCR":return walk(int(obj["/MCID"]),pg,owner)
        if obj.get("/Type")=="/OBJR":return ""
        role=str(obj.get("/S",""));ref=getattr(obj,"indirect_reference",None)
        own=ref.idnum if ref else owner
        body=walk(obj.get("/K",[]),pg,own)
        if re.fullmatch(r"/H[1-6]",role):heading_rows.append({"level":role[1:],"text":norm(body)})
        if role=="/Figure":figure_rows.append({"alt":str(obj.get("/Alt","")),"children_text":norm(body)[:100]})
        if role=="/Formula":formula_rows.append(str(obj.get("/Alt","")))
        if role in {"/Figure","/Formula"} and obj.get("/Alt"):body=str(obj["/Alt"])
        return body+ ("\n" if role in {"/P","/H1","/H2","/H3","/LI","/TR","/Caption"} else "")
    logical=walk(tree["/K"])
    errors=[]
    for pi,mid,owner in structure_refs:
        if mid not in content_ids[pi]:errors.append(f"Tree points at absent page {pi+1} MCID {mid}")
        arr=parents[int(r.pages[pi]["/StructParents"])]
        if mid>=len(arr) or not hasattr(arr[mid],"idnum") or arr[mid].idnum!=owner:
            errors.append(f"ParentTree mismatch page {pi+1} MCID {mid} owner {owner}")
    refset={(p,m) for p,m,_ in structure_refs}
    contentset={(p,m) for p,ms in content_ids.items() for m in ms}
    if refset!=contentset:errors.append(f"MCID coverage mismatch: content-only {len(contentset-refset)}, tree-only {len(refset-contentset)}")
    if len(structure_refs)!=len(refset):errors.append('Duplicate MCID references in structure tree')
    if sum(len(ms) for ms in content_ids.values())!=len(contentset):errors.append('Duplicate page MCID definitions')
    dom_headings=[{"level":h["level"],"text":norm(h["text"])} for h in printed["dom"]["headings"]]
    if heading_rows!=dom_headings:errors.append("Heading text/order differs from printed HTML")
    if Counter(formula_rows)!=Counter(f["alt"] for f in manifest["formulas"]):errors.append("Formula alternative mismatch")
    if not all(f["embedded"] for f in font_info.values()):errors.append("Unembedded font")
    if unmarked:errors.append(f"{len(unmarked)} text runs have neither MCID nor explicit Artifact marking")
    if any(not f['alt'] for f in figure_rows):errors.append("Figure without alternative")
    if "\x00" in logical or "\ufffd" in logical:errors.append("Replacement/NUL in structure-order logical extraction")
    subprocess.run(["pdftotext","-enc","UTF-8",str(pdf),str(text_path)],check=True)
    poppler=text_path.read_text(encoding="utf-8")
    if "\x00" in poppler or "\ufffd" in poppler:errors.append("Replacement/NUL in Poppler extraction")
    prepared=html.fromstring(Path(manifest["prepared_html"]).read_bytes())
    fragments=[]
    for e in prepared.xpath('//p[contains(concat(" ",normalize-space(@class)," ")," source-paragraph ")]'):
        for node in e.xpath('.//text()[not(ancestor::math) and not(ancestor::svg)]'):
            s=norm(str(node))
            if len(re.findall(r"[\u0a80-\u0aff]",s))>=4:fragments.append({"id":e.get("id"),"text":s})
    missing=[f for f in fragments if compact(f["text"]) not in compact(poppler)]
    if missing:errors.append(f"{len(missing)} Gujarati prose fragments absent from Poppler extraction")
    def outlines(items):
        rows=[]
        for i in items:
            if isinstance(i,list):rows.extend(outlines(i))
            else:rows.append({"title":i.title,"page":r.get_destination_page_number(i)+1})
        return rows
    bookmarks=outlines(r.outline)
    if [b["title"] for b in bookmarks]!=[h["text"] for h in dom_headings]:errors.append("Bookmark hierarchy/order titles differ from headings")
    links=[];linked_annotations=0
    for i,p in enumerate(r.pages):
        for a in p.get("/Annots",[]):
            a=a.get_object()
            if a.get("/Subtype")=="/Link":
                links.append({"page":i+1,"action":str(a.get("/A",{})),"dest":str(a.get("/Dest",""))})
                key=a.get('/StructParent')
                if key is None or int(key) not in parents:errors.append(f'Link annotation on page{i+1} lacks ParentTree entry')
                else:
                    owner=parents[int(key)]
                    if owner.get('/S')!='/Link':errors.append(f'Annotation ParentTree owner is not Link on page{i+1}')
                    else:linked_annotations+=1
    header_scopes=Counter()
    for e in struct_walk(tree['/K']):
        if e.get('/S')=='/TH':
            attrs=e.get('/A',[]);attrs=attrs if isinstance(attrs,list) else [attrs]
            scopes=[str(a.get_object().get('/Scope')) for a in attrs if hasattr(a.get_object(),'get') and a.get_object().get('/O')=='/Table' and a.get_object().get('/Scope') is not None]
            if not scopes:errors.append('Table header lacks explicit Scope attribute')
            header_scopes.update(scopes)
    result={"pdf":str(pdf.resolve()),"pdf_sha256":digest(pdf),"pages":len(r.pages),"language":str(root.get("/Lang")),
            "marked_flag":bool(root.get("/MarkInfo",{}).get("/Marked")),"structure_tags":dict(Counter(str(e.get('/S')) for e in struct_walk(tree['/K']))),
            "content_mcid_count":len(contentset),"structure_mcid_count":len(refset),"parent_tree_errors":errors,
            "actual_text_spans":actual_count,"headings":heading_rows,"bookmarks":bookmarks,
            "formula_alternatives":len(formula_rows),"figures":figure_rows,
            "fonts":list(font_info.values()),"unmarked_text_runs":unmarked,
            "gujarati_prose_fragments_checked":len(fragments),"missing_prose_fragments":missing,
            "poppler_text_sha256":digest(text_path),"structure_logical_text_has_nul_or_replacement":("\x00" in logical or "\ufffd" in logical),
            "links":links,"link_annotation_parent_tree_matches":linked_annotations,"table_header_scopes":dict(header_scopes),"errors":errors,
            "not_certified":"No PDF/UA or screen-reader conformance claim; actual viewer/assistive-technology testing is still required."}
    receipt.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    receipt.with_suffix('.logical.txt').write_text(logical,encoding='utf-8')
    print(json.dumps({"pages":len(r.pages),"mcids":len(contentset),"formulas":len(formula_rows),"prose":len(fragments),"errors":errors},ensure_ascii=False))
    if errors:raise SystemExit(1)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    for arg in ("pdf","manifest","print_receipt","receipt","text"):p.add_argument(arg,type=Path)
    a=p.parse_args();verify(a.pdf,a.manifest,a.print_receipt,a.receipt,a.text)
