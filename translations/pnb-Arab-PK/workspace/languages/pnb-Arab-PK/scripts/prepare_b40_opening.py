"""Prepare exact B40-opening PDF components, transparent PNG previews and notices.

Pinned Git blobs are data only. Poppler rasterizes the two existing one-page PDFs;
no TeX, Asymptote, upstream script, network service or font build is executed.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
from PIL import Image
from b40_opening_tex import convert

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[1]
MANIFEST=BASE/"source-excerpts/manifest-b40-opening.json"
TRANSLATION=BASE/"translations/b40-opening.json"
WITNESS=BASE/"source-excerpts/b40-opening.json"
NOTICES=BASE/"provenance/b40-opening-component-notices.json"
CANON="df2262e089a02651c127f1dd12649c4622ee1383"
FROZEN={
 MANIFEST:"a3430810fd1f3259587b5581980280ac78ff2520148c227d677798b5e3eb1239",
 TRANSLATION:"45352c7245ff69768f97dbb12ca0e8926fa25ded46bed2169c62779984daf173",
 WITNESS:"560a16023aa2e93d5f47236320ef5740090b2d786d9f506b6f68d05ac01315f5"}
ASSETS=[
 ("shadow","src/cover/asy/shadow.pdf","b40-opening-shadow.pdf","b40-opening-shadow-transparent.png"),
 ("axesgraphic","src/cover/asy/axesgraphic.pdf","b40-opening-axesgraphic.pdf","b40-opening-axesgraphic-transparent.png")]
MACRO_RANGES=[(93,94),(167,174),(183,200),(223,230),(260,274),(298,299)]

def require(value,message):
    if not value:raise ValueError(message)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def file_hash(path):return digest(path.read_bytes())
def git(repo,*args):return subprocess.check_output(["git","-C",str(repo),*args])
def load():
    for path,h in FROZEN.items():require(file_hash(path)==h,"Frozen input differs: "+path.name)
    m=json.loads(MANIFEST.read_text(encoding="utf-8"));t=json.loads(TRANSLATION.read_text(encoding="utf-8"))
    require(m["canonical"]["commit"]==CANON and m["unit"]=="B40-opening","Canonical scope differs")
    repo=ROOT/m["canonical"]["local_path"]
    require(git(repo,"rev-parse",CANON+"^{tree}").decode().strip()==m["canonical"]["tree"],"Canonical tree differs")
    return m,t,repo

def macro_evidence(m,repo):
    row=next(x for x in m["source_files"]["canonical"] if x["repository_path"]=="src/sty/linalgjh.sty")
    raw=git(repo,"show",CANON+":"+row["repository_path"])
    require(digest(raw)==row["sha256"] and blob(raw)==row["git_blob_sha1"],"Macro style differs")
    lines=raw.decode("utf-8").splitlines(keepends=True)
    pieces=[]
    for a,b in MACRO_RANGES:
        text="".join(lines[a-1:b])
        pieces.append({"lines":[a,b],"raw":text,"sha256":digest(text.encode())})
    marks=git(repo,"show",CANON+":src/sty/bookans.sty")
    mr=next(x for x in m["source_files"]["canonical"] if x["repository_path"]=="src/sty/bookans.sty")
    require(digest(marks)==mr["sha256"],"Mark style differs")
    marklines=marks.decode().splitlines(keepends=True)
    marktext="".join(marklines[301:305])
    return {"file":row,"selected_ranges":pieces,
            "standard_tex_symbols":["Greek control words","\\vec"],
            "standard_symbol_limit":"Their observed presentation meaning is mapped; this is not a full LaTeX implementation.",
            "mark_file":mr,"mark_lines":[302,305],"mark_raw":marktext,"mark_sha256":digest(marktext.encode())}

def render_preview(source,target):
    with tempfile.TemporaryDirectory(prefix="b40-opening-",dir=None) as td:
        prefix=Path(td)/"page"
        subprocess.check_call(["pdftocairo","-png","-singlefile","-transp","-r","144",str(source),str(prefix)],
                              stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        made=prefix.with_suffix(".png");raw=made.read_bytes()
        with Image.open(made) as im:
            require(im.mode=="RGBA","Transparent derivative must be RGBA")
            dims=im.size
            alpha=im.getchannel("A").getextrema()
        require(alpha[0]<255,"Derivative lacks transparent pixels")
        if target.exists():require(target.read_bytes()==raw,"Refusing to overwrite changed derivative")
        else:target.write_bytes(raw)
    return {"path":target.relative_to(BASE).as_posix(),"sha256":digest(raw),"bytes":len(raw),
            "width":dims[0],"height":dims[1],"mode":"RGBA","alpha_extrema":list(alpha),
            "derivative":"Poppler 144-dpi transparent raster of the exact one-page PDF; not an exact reconstruction of TeX cover offsets."}

def notice_record(m,t,repo,prepared,previews):
    formulas=[];n=0
    for block in m["source_blocks"]:
        for slot in block["slots"]:
            if slot["kind"]=="tex":
                n+=1;_,record=convert(slot["value"])
                formulas.append({"number":n,"owner":block["key"],"slot_token":slot["token"],
                                 "source_delimiters":slot["delimiters"],"source_raw":slot["raw"],**record})
    require(n==76,"Expected 76 TeX owners")
    source_assets={x["repository_path"]:x for x in m["source_assets"]}
    return {"schema":"b40-opening-retained-component-evidence-v1","unit":"B40-opening",
      "work":"Linear Algebra","author":"Jim Hefferon","edition":"Fourth edition, second printing",
      "canonical":m["canonical"],"comparison":m["comparison"],
      "manifest_sha256":file_hash(MANIFEST),"translation_sha256":file_hash(TRANSLATION),
      "witness_sha256":file_hash(WITNESS),
      "scope":"Complete default cover/notation/full preface opening only; generated contents and starred-subsection note remain next.",
      "source_specific_license":"Creative Commons Attribution-ShareAlike 2.5",
      "existing_notice_policy":m["retained_notices"],
      "rights_status":"Existing B40 dual-license/component evidence retained; no new rights, supply or image-clearance audit.",
      "component_limit":"Exact byte/blob evidence and transparent preview derivation do not create a new clearance or endorsement.",
      "non_endorsement":"No endorsement by Jim Hefferon or Saint Michael's College is implied.",
      "components":[{"id":ident,"source_path":src,"source_sha256":spec["sha256"],
          "source_git_blob_sha1":spec["git_blob_sha1"],"source_bytes":spec["bytes"],
          "prepared_path":pdf.relative_to(BASE).as_posix(),"prepared_sha256":file_hash(pdf),
          "source_alt":None,"preview":preview,
          "treatment":"Exact PDF copied from pinned Git; unedited original linked. Preview is an explicitly described transparent derivative and not a source alt or exact TeX composition."}
          for (ident,src,_,_),pdf,preview in zip(ASSETS,prepared,previews)
          for spec in [source_assets[src]]],
      "source_layer_order":[{"path":"src/cover/asy/shadow.pdf","put":["-0.0","-6.9"]},
                            {"path":"src/cover/asy/axesgraphic.pdf","put":["0","-6.5"]}],
      "preview_policy":"Each component is previewed separately in source layer order because executing the upstream TeX/Asymptote composition is forbidden. No mirror, crop, recolor or fabricated exact composite.",
      "math_policy":"Strict finite nonexecuting mapper for these 76 owners only. Unknown syntax fails closed; exact raw TeX/delimiters, token ledger and application/x-tex annotation retained.",
      "macro_evidence":macro_evidence(m,repo),"math_records":formulas,
      "runtime":"Only pinned Git byte reads and Poppler PDF-to-PNG rasterization. No TeX, Asymptote, Sage, upstream code, network, analytics or grading runtime.",
      "whole_frontmatter_complete":False,"whole_book_translation_complete":False,"whole_assignment_complete":False}

def prepare():
    m,t,repo=load();out=BASE/"assets/b40";out.mkdir(parents=True,exist_ok=True)
    prepared=[];previews=[]
    specs={x["repository_path"]:x for x in m["source_assets"]}
    for ident,src,pdfname,pngname in ASSETS:
        spec=specs[src];raw=git(repo,"show",CANON+":"+src)
        require(digest(raw)==spec["sha256"] and len(raw)==spec["bytes"] and blob(raw)==spec["git_blob_sha1"],"PDF source differs")
        pdf=out/pdfname
        if pdf.exists():require(pdf.read_bytes()==raw,"Refusing to overwrite changed exact PDF")
        else:pdf.write_bytes(raw)
        require(file_hash(pdf)==spec["sha256"],"Prepared PDF differs")
        preview=render_preview(pdf,out/pngname)
        prepared.append(pdf);previews.append(preview)
    notice=notice_record(m,t,repo,prepared,previews)
    NOTICES.parent.mkdir(parents=True,exist_ok=True)
    NOTICES.write_text(json.dumps(notice,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print("Prepared B40-opening: 2 exact PDFs, 2 transparent component previews, 76 reversible math records; no upstream engine.")

if __name__=="__main__":prepare()
