"""Freeze one exact canonical subsection for translation, never a corpus export."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from build import atomic_write
from inspect_source import slots, CN, MATH

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parent


def select_source_unit(root,section):
    selected=[e for e in root.iter() if e.tag in {CN+"section",CN+"note"} and e.get("id")==section]
    assert len(selected)==1,"Missing or ambiguous source section/readiness note"
    selected[0].tail=None
    return selected[0]


def prepare(unit,course,module,section):
    assert re.fullmatch(r"TE-B\d{3}",unit)
    assert shutil.disk_usage(BASE).free >= 32*1024*1024
    lock=json.loads((BASE/"sources.lock.json").read_text(encoding="utf-8"))
    records=[r for r in lock["source_files"] if r["course"]==course and r["module"]==module and r["role"]=="canonical_english"]
    assert len(records)==1
    record=records[0]
    raw=(ROOT/record["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==record["sha256"]
    root=ET.fromstring(raw)
    selected=[select_source_unit(root,section)]
    ET.register_namespace("",CN[1:-1]); ET.register_namespace("m",MATH[1:-1])
    source=ET.tostring(selected[0],encoding="utf-8",xml_declaration=True)+b"\n"
    destination=BASE/"sources"/(unit+".en.cnxml")
    if destination.exists():
        assert destination.read_bytes()==source,"Existing frozen unit differs"
    collection=next(c for c in lock["collections"] if c["course"]==course)
    repo=next(r for r in lock["repositories"] if r["id"]==collection["upstream_repository_id"])
    meta={"schema":"te-source-unit-v1","unit":unit,"course":course,"module":module,"section":section,
          "title_en":selected[0].findtext(CN+"title"),"source_commit":repo["commit"],"source_module":record,
          "source_sha256":hashlib.sha256(source).hexdigest(),"text_slots":len(list(slots(selected[0]))),
          "element_count":len(list(selected[0].iter())),"scope":("one complete canonical readiness note; not a module/book" if selected[0].tag==CN+"note" else "one complete canonical subsection; not a module/book"),
          "purpose":"human-reviewable translation input; never model training data"}
    atomic_write(destination,source)
    atomic_write(BASE/"sources"/(unit+".source.json"),(json.dumps(meta,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps(meta,ensure_ascii=False,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for field in ["unit","course","module","section"]:
        p.add_argument("--"+field,required=True)
    a=p.parse_args(); prepare(a.unit,a.course,a.module,a.section)
