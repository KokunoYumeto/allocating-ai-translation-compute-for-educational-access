"""Freeze acquired source identities and materialize reviewable provenance/crosswalks.

Does not download, extract, translate, or audit rights. Requires existing release
materializations; verifies their archive bytes before copying reviewable notices.
All corpus-sized files remain in downloads/. Run after acquisition, then use --verify.
"""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import seal_archives

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
DL = ROOT / "downloads"
CN = "{http://cnx.rice.edu/cnxml}"
COL = "{http://cnx.rice.edu/collxml}"
MD = "{http://cnx.rice.edu/mdml}"
XML = "{http://www.w3.org/XML/1998/namespace}"


def module_translation_status(course,module):
    """Unit progress must survive regeneration of the acquisition crosswalk."""
    progress=json.loads((BASE/"units.json").read_text(encoding="utf-8"))
    selected=[u for u in progress["units"] if u["course"]==course and u["module"]==module]
    if not selected:
        return "not_started"
    coverage=next((m for m in progress.get("module_coverage",[]) if m["course"]==course and m["module"]==module),None)
    complete=(coverage and coverage["status"]=="all_source_parts_editorially_checked"
              and set(coverage["required_units"])=={u["unit"] for u in selected}
              and all(u["status"]=="editorially_checked" for u in selected)
              and (BASE/coverage["qa"]).is_file())
    suffix="; all module source parts checked across fragments" if complete else "; module incomplete"
    return "; ".join(f'{u["unit"]}: source part {u["section"]} {u["status"]}' for u in selected)+suffix


REPOS = {
    "catalog":"program-matematika-indonesia", "A00-id":"openstax-prealgebra-2e-id-ID",
    "A10-id":"openstax-elementary-algebra-2e-id", "A20-id":"openstax-intermediate-algebra-2e-id",
    "A30-id":"openstax-precalculus-2e-id", "B10-id":"discrete-mathematics-open-introduction-id",
    "OpenLogic-id-supplement":"OpenLogic-id", "A00-A20-en":"upstream-prealgebra",
    "A30-en":"upstream-precalculus", "B10-en":"upstream-discrete", "OpenLogic-en-supplement":"upstream-openlogic",
}
PINS = {"A00-A20-en":"38cae454e644abf9f0a623e876994553881597c9",
        "A30-en":"789b54099106b071d1d32bfcee454fed72eb4768",
        "B10-en":"82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799",
        "OpenLogic-en-supplement":"9620cc73f9c8e0ad003c514a5d3748f29611c4c0"}
PACKS = [
    ("A10","v1.0.2","elementary-algebra-2e-id-ID-1.0.2-source.zip","6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456"),
    ("A20","v0.3.0-wip","openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip","a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7"),
    ("A30","v0.1.0-alpha.58-reader.1","precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip","9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca"),
]
BOOKS = [
    ("A00","prealgebra-2e",75,"A00-A20-en",DL/REPOS["A00-id"]/"modules"),
    ("A10","elementary-algebra-2e",82,"A00-A20-en",DL/"releases/A10/extracted/translated/modules"),
    ("A20","intermediate-algebra-2e",83,"A00-A20-en",DL/"releases/A20/extracted/source/modules"),
    ("A30","precalculus-2e",87,"A30-en",DL/"releases/A30/extracted/repo/source/modules"),
]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def git(path, *args):
    return subprocess.check_output(["git","-C",str(path),*args]).decode("utf-8").strip()


def dump(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def tsv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def file_record(path):
    return {"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":sha(path)}


def preserve(path, name):
    destination = BASE / "notices" / name
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(path.read_bytes())
    return file_record(destination)


def existing_release_packages():
    """Read-only preflight: never re-extract a large release on a freeze rerun."""
    records = []
    for code, tag, filename, expected in PACKS:
        archive = DL / "releases" / code / filename
        if sha(archive) != expected:
            raise ValueError("Release hash mismatch: " + filename)
        destination = archive.parent / "extracted"
        if not destination.is_dir():
            raise FileNotFoundError(f"Missing existing release materialization: {destination}; "
                                    "freeze_sources.py never downloads or extracts")
        root = destination.resolve()
        with zipfile.ZipFile(archive) as package:
            names = set()
            for member in package.infolist():
                if member.filename in names:
                    raise ValueError("Duplicate release member: " + member.filename)
                names.add(member.filename)
                target = (root / member.filename).resolve()
                if not target.is_relative_to(root):
                    raise ValueError("Unsafe archive member: " + member.filename)
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink archive member: " + member.filename)
                if member.is_dir():
                    continue
                if not target.is_file() or target.stat().st_size != member.file_size:
                    raise ValueError("Missing or wrong-size materialized release file: " + str(target))
                with package.open(member) as stream:
                    archived_sha = hashlib.file_digest(stream, "sha256").hexdigest()
                if sha(target) != archived_sha:
                    raise ValueError("Materialized release file differs from archive: " + str(target))
            count = len(names)
        records.append({"course": code, "tag": tag,
                        "url": f"https://github.com/KokunoYumeto/{REPOS[code+'-id']}/releases/download/{tag}/{filename}",
                        **file_record(archive), "zip_entries": count, "crc": "PASS"})
    return records


def freeze():
    # Complete all corpus preflights before writing any reviewable output. The
    # archive records are preserved verbatim, including acquisition provenance.
    lock_path = BASE / "sources.lock.json"
    previous = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    archives = previous.get("canonical_archives")
    archives = (seal_archives.verify_registered_archives(archives) if archives is not None
                else seal_archives.verified_records())
    packages = existing_release_packages()
    lock = {"schema":"te-translation-sources-lock-v1","locale":"te-Telu-IN","acquired_on":"2026-08-30",
            "purpose":"translation inputs only; not training or fine-tuning data", "repositories":[],"release_packages":packages,
            "canonical_archives":archives,
            "notices":[],"collections":[],"source_files":[],"catalog_resolution_notes":[
                "B10 is DMOI4 in catalog; Open Logic retained only as supplemental dispatch reference.",
                "A10 1.0.2 and A30 alpha.58 override older catalog summaries.",
                "A20 0.3.0-wip release assets contain 48/83; repository root is stale at 28/83 and catalog at 41/83.",
                "OpenStax canonical checkouts remain sparse, excluding bulk media/cover after full-fetch connection resets. Complete pinned canonical ZIPs are local and verified against every Git blob and ZIP CRC, including media/cover; they have not been extracted. See canonical_archives for exact hashes and acquisition provenance. Indonesian source packages retain their admitted media."]}
    for rid, dirname in REPOS.items():
        directory = DL/dirname
        commit = git(directory,"rev-parse","HEAD")
        if rid in PINS:
            assert commit == PINS[rid], rid
        record = {"id":rid,"path":directory.relative_to(ROOT).as_posix(),"url":git(directory,"remote","get-url","origin"),
                  "commit":commit,"tree":git(directory,"rev-parse","HEAD^{tree}"),"shallow":git(directory,"rev-parse","--is-shallow-repository")=="true"}
        sparse = subprocess.run(["git","-C",str(directory),"config","--get","core.sparseCheckout"],capture_output=True,text=True).stdout.strip()=="true"
        record["materialization"] = "sparse_no_media_or_cover" if sparse else "full_checkout"
        lock["repositories"].append(record)
    for code, book, count, rid, target_dir in BOOKS:
        upstream=DL/REPOS[rid]
        path=upstream/"collections"/(book+".collection.xml")
        collection=ET.parse(path).getroot()
        ids=[e.get("document") for e in collection.iter(COL+"module")]
        assert len(ids)==count and len(set(ids))==count
        lock["collections"].append({"course":code,"upstream_repository_id":rid,"slug":book,"module_count":count,**file_record(path)})
        group={}
        for sub in collection.iter(COL+"subcollection"):
            title=sub.findtext(MD+"title",default="")
            for mod in sub.iter(COL+"module"):
                group[mod.get("document")]=title
        rows=[]
        for order,mid in enumerate(ids,1):
            sp=upstream/"modules"/mid/"index.cnxml"
            sr=ET.parse(sp).getroot()
            tp=target_dir/mid/"index.cnxml"
            title=sr.findtext(CN+"title",default="")
            lock["source_files"].append({"course":code,"module":mid,"role":"canonical_english",**file_record(sp)})
            if tp.exists():
                lock["source_files"].append({"course":code,"module":mid,"role":"indonesian_reference",**file_record(tp)})
            rows.append({"course":code,"order":order,"source_id":mid,"chapter":group.get(mid,"Front/back matter"),
                         "title_en":title,"canonical_path":sp.relative_to(ROOT).as_posix(),"source_sha256":sha(sp),
                         "indonesian_path":tp.relative_to(ROOT).as_posix() if tp.exists() else "NOT_IN_RELEASE_PREFIX",
                         "bridge_lane":code+"-prerequisites" if code=="A00" else code+"-later-extension",
                         "telugu_status":module_translation_status(code,mid)})
        tsv(BASE/"crosswalk"/(code+"-modules.tsv"),rows)
        lock["collections"][-1]["indonesian_modules_acquired"]=sum(1 for row in rows if row["indonesian_path"]!="NOT_IN_RELEASE_PREFIX")
    # Use the owner's frozen include closure, verifying every canonical file hash.
    manifest=DL/REPOS["B10-id"]/"backend/manifests/authority_book_closure_dfs.tsv"
    b10=[]
    for order,line in enumerate(manifest.read_text(encoding="utf-8").splitlines(),1):
        path,size,expected=line.split("\t")
        sp=DL/"upstream-discrete"/path
        assert sp.stat().st_size==int(size) and sha(sp)==expected, path
        tp=DL/REPOS["B10-id"]/path
        lock["source_files"].append({"course":"B10","module":path,"role":"canonical_english",**file_record(sp)})
        title=""; ids=[]
        if sp.suffix==".ptx":
            try:
                tree=ET.parse(sp).getroot()
                title=" ".join(next(iter(tree.iter("title")),ET.Element("title")).itertext())
                ids=[x.get(XML+"id") for x in tree.iter() if x.get(XML+"id")]
            except ET.ParseError:
                title="PreTeXt fragment; parsed within canonical inclusion context"
        b10.append({"course":"B10","order":order,"source_id":path,"title_en":title,"xml_ids":";".join(ids),
                    "canonical_path":sp.relative_to(ROOT).as_posix(),"source_sha256":expected,
                    "indonesian_path":tp.relative_to(ROOT).as_posix() if tp.exists() else "missing",
                    "bridge_lane":"B10-proof-discrete-after-A30","telugu_status":"not_started"})
        assert tp.exists(), path
        lock["source_files"].append({"course":"B10","module":path,"role":"indonesian_reference",**file_record(tp)})
    tsv(BASE/"crosswalk/B10-source-closure.tsv",b10)
    lock["collections"].append({"course":"B10","upstream_repository_id":"B10-en","entry":"source/dmoi.ptx","source_closure_files":len(b10),"closure_manifest":file_record(manifest)})
    # Supplemental Open Logic closure is verified, but is not a B10 crosswalk substitute.
    olmanifest=DL/REPOS["OpenLogic-id-supplement"]/"evidence/CLOSURE_0722.csv"
    olrows=list(csv.DictReader(olmanifest.open(encoding="utf-8-sig",newline="")))
    crlf_matches=0
    for row in olrows:
        sp=DL/"upstream-openlogic"/row["source_path"]
        if sha(sp)!=row["source_sha256"]:
            # Owner inventory was computed on a Windows CRLF materialization.
            assert hashlib.sha256(sp.read_bytes().replace(b"\r\n",b"\n").replace(b"\n",b"\r\n")).hexdigest()==row["source_sha256"],row["source_path"]
            crlf_matches+=1
    lock["supplemental_openlogic"]={"role":"dispatch_reference_not_B10","verified_canonical_files":len(olrows),"owner_crlf_materialization_matches":crlf_matches,"checkout_line_endings":"canonical Git LF; never rewritten to make a hash pass","closure":file_record(olmanifest)}
    for code, path in [
        ("A00-LICENSE.txt",DL/REPOS["A00-id"]/"LICENSE"),
        ("A00-README-upstream.md",DL/"upstream-prealgebra/README.md"),
        ("A00-README-id.md",DL/REPOS["A00-id"]/"README.md"),
        ("A10-LICENSE.txt",DL/"releases/A10/extracted/LICENSE.txt"),
        ("A10-NOTICE.txt",DL/"releases/A10/extracted/NOTICE.txt"),
        ("A20-LICENSE.txt",DL/"releases/A20/extracted/LICENSE.txt"),
        ("A30-LICENSE.txt",DL/"releases/A30/extracted/LICENSE.txt"),
        ("B10-LICENSE.txt",DL/REPOS["B10-id"]/"LICENSE"),
        ("B10-THIRD_PARTY_NOTICES.md",DL/REPOS["B10-id"]/"THIRD_PARTY_NOTICES.md"),
        ("OpenLogic-LICENSE.txt",DL/REPOS["OpenLogic-id-supplement"]/"LICENSE"),
    ]:
        lock["notices"].append({"original_path":path.relative_to(ROOT).as_posix(),**preserve(path,code)})
    # Byte-preserve manifests; not a new audit or rights decision.
    evidence_paths=[DL/REPOS["A10-id"]/"SOURCE_AUTHORITY.md",DL/REPOS["A20-id"]/"RELEASE_MANIFEST.json",
        DL/"releases/A10/elementary-algebra-2e-id-ID-1.0.2-release-manifest.json",
        DL/"releases/A20/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-release-manifest.json",
        DL/REPOS["A30-id"]/"RELEASE_MANIFEST.json",DL/REPOS["OpenLogic-id-supplement"]/"evidence/SOURCE_AUTHORITY.json"]
    lock["evidence"]=[]
    for i,path in enumerate(evidence_paths,1):
        dest=BASE/"evidence"/f"{i:02d}-{path.name}"
        dest.parent.mkdir(exist_ok=True); dest.write_bytes(path.read_bytes())
        lock["evidence"].append({"original_path":path.relative_to(ROOT).as_posix(),**file_record(dest)})
    s=(DL/REPOS["catalog"]/"docs/courses.js").read_text(encoding="utf-8")
    courses=json.JSONDecoder().raw_decode(s[s.index("["):])[0]
    dump(BASE/"evidence/catalog-assigned-courses.json",[c for c in courses if c["id"] in ("A00","A10","A20","A30","B10")])
    source=ET.parse(DL/"upstream-prealgebra/modules/m81243/index.cnxml").getroot()
    unit=next(e for e in source.iter() if e.get("id")=="fs-id1830385")
    unit.tail=None
    ET.register_namespace("",CN[1:-1]); ET.register_namespace("m","http://www.w3.org/1998/Math/MathML")
    dest=BASE/"sources/TE-B001.en.cnxml"; dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(ET.tostring(unit,encoding="utf-8",xml_declaration=True)+b"\n")
    lock["pilot_source"]=file_record(dest)
    dump(BASE/"sources.lock.json",lock)
    print(json.dumps({"repositories":len(lock["repositories"]),"packages":len(lock["release_packages"]),"collections":lock["collections"],"source_file_records":len(lock["source_files"]),"supplemental_openlogic":lock["supplemental_openlogic"]},indent=2))


def verify():
    lock=json.loads((BASE/"sources.lock.json").read_text(encoding="utf-8"))
    archives = seal_archives.verify_registered_archives(lock.get("canonical_archives", []))
    for repo in lock["repositories"]:
        assert git(ROOT/repo["path"],"rev-parse","HEAD")==repo["commit"]
        assert git(ROOT/repo["path"],"rev-parse","HEAD^{tree}")==repo["tree"]
    records=lock["source_files"]+lock["notices"]+lock["release_packages"]+lock["evidence"]+[lock["pilot_source"]]
    for record in records:
        path=ROOT/record["path"]
        assert path.stat().st_size==record["bytes"] and sha(path)==record["sha256"], record["path"]
    print(f"PASS: {len(records)} file records and {len(lock['repositories'])} exact Git commits/trees; "
          f"{len(archives)} complete canonical archives with {sum(r['git_blob_count'] for r in archives)} verified Git blobs/ZIP CRCs")


if __name__=="__main__":
    verify() if "--verify" in sys.argv else freeze()
