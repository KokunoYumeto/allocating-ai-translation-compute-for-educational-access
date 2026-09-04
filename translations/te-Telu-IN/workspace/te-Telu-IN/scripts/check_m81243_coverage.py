"""Read-only coverage check of one translated module, not a corpus audit.

Requires its already acquired canonical module plus the ten frozen fragments.
No network, extraction, source mutation or training export. This proves source
coverage and receipt consistency; it does not replace linguistic/visual review.
"""
import json
import re
import xml.etree.ElementTree as ET
from prepare_auxiliary import BASE,module_input,sha
from inspect_source import CN,slots


def graph(node):
    clean=lambda s:s if s and s.strip() else ""
    return (node.tag,sorted(node.attrib.items()),clean(node.text),clean(node.tail),[graph(c) for c in node])


def check():
    module,record=module_input()
    content=module.find(CN+"content")
    assert not content.attrib and not (content.text or "").strip(),"Uncovered content wrapper"
    frozen=[ET.parse(BASE/"sources"/f"TE-B{i:03}.en.cnxml").getroot() for i in range(1,11)]
    assert len(content)==8 and [e.get("id") for e in content]==[e.get("id") for e in frozen[:8]],"Missing/reordered subsection"
    for actual,part in zip(content,frozen):
        assert graph(actual)==graph(part),"Subsection source mismatch"
    assert graph(module.find(CN+"glossary"))==graph(frozen[8]),"Glossary mismatch"
    assert module.tag==frozen[9].tag and module.attrib==frozen[9].attrib
    assert [e.tag for e in frozen[9]]==[CN+"title",CN+"metadata"]
    for node in frozen[9]:assert graph(module.find(node.tag))==graph(node),"Opening mismatch"
    original_ids=[e.get("id") for e in module.iter() if e.get("id")]
    fragment_ids=[e.get("id") for part in frozen for e in part.iter() if e.get("id")]
    assert len(fragment_ids)==len(set(fragment_ids)) and set(fragment_ids)==set(original_ids),"Source ID closure mismatch"
    assert len(list(slots(module)))==sum(len(list(slots(p))) for p in frozen),"Uncovered text slot"
    progress=json.loads((BASE/"units.json").read_text("utf-8"))
    receipts=[]
    for i in range(1,11):
        unit=f"TE-B{i:03}"
        row=next(u for u in progress["units"] if u["unit"]==unit)
        assert row["status"]=="editorially_checked" and (BASE/row["qa"]).is_file(),"Unit review incomplete"
        qa=BASE/"qa"/("build-receipt.json" if i==1 else unit+".build.json")
        build=json.loads(qa.read_text("utf-8"))
        visual=json.loads((BASE/"qa"/("visual-render-receipt.json" if i==1 else unit+".visual.json")).read_text("utf-8"))
        target=BASE/"generated"/(unit+".te.cnxml")
        reader=BASE/row["reader"]
        assert sha(target.read_bytes())==build["target_sha256"],"Stale target receipt"
        # The original B001 visual schema predates reader fingerprints. Its
        # separately committed final manual review explicitly binds the hash.
        visual_hash=visual.get("reader_sha256")
        if i==1:
            reviewed=re.search(r"Reader SHA256: `([0-9a-f]{64})`",(BASE/row["qa"]).read_text("utf-8"))
            assert reviewed,"Legacy final-review fingerprint missing"
            visual_hash=reviewed.group(1)
        assert sha(reader.read_bytes())==build["reader_sha256"]==visual_hash,"Stale reader/visual receipt"
        receipts.append({"unit":unit,"source_sha256":build["source_sha256"],"target_sha256":build["target_sha256"],"reader_sha256":build["reader_sha256"]})
    return {"status":"PASS","module":"m81243","source_sha256":record["sha256"],
            "source_elements":len(list(module.iter())),"source_ids":len(original_ids),
            "source_text_slots":len(list(slots(module))),"checked_fragments":10,"content_sections":8,
            "auxiliary_parts":["complete glossary","module title and complete metadata/objectives"],
            "coverage":"All canonical module source content represented across ten checked readers; no assembled single-reader claim.",
            "untranslated_prior_modules":["m81241","m81242"],"full_assignment_complete":False,"units":receipts}


if __name__=="__main__":print(json.dumps(check(),ensure_ascii=False,indent=2))
