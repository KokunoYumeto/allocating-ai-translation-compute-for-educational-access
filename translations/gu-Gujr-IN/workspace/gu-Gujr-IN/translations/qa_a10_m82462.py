"""Independent structural/accessibility QA for the complete A10 m82462 translation."""
from pathlib import Path
import hashlib
import json
import re
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
REVIEWS = HERE.parent / "reviews"
SRC = ROOT / "downloads/gu-Gujr-IN/a10-release/source/authority/source/modules/m82462/index.cnxml"
GU = HERE / "a10-m82462.gu.cnxml"
ERRATA = HERE / "a10-m82462-errata.gu.json"
OUT = REVIEWS / "a10-m82462-qa.json"
SOURCE_SHA256 = "7f29e8b9558d6d37553e5991cfffc7cc27c320e2a92ed98db563e76a90e8a51e"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qname(elem):
    value = etree.QName(elem)
    return value.namespace, value.localname


def main():
    assert sha(SRC) == SOURCE_SHA256
    source = etree.parse(str(SRC)).getroot()
    target = etree.parse(str(GU)).getroot()
    source_elems = list(source.iter())
    target_elems = list(target.iter())
    assert len(source_elems) == len(target_elems) == 13
    assert [qname(x) for x in source_elems] == [qname(x) for x in target_elems]
    assert [x.get("id") for x in source_elems] == [x.get("id") for x in target_elems]
    assert target.get("{http://www.w3.org/XML/1998/namespace}lang") == "gu-Gujr-IN"
    assert target.get("class") == source.get("class") == "introduction"
    for a, b in zip(source_elems, target_elems):
        for attr, value in a.attrib.items():
            if etree.QName(attr).localname in {"alt", "aria-label", "summary", "title"}:
                continue
            assert b.get(attr) == value, (qname(a), attr, value, b.get(attr))
    ns = {"c": "http://cnx.rice.edu/cnxml", "md": "http://cnx.rice.edu/mdml"}
    assert target.xpath("string(c:title)", namespaces=ns) == "પરિચય"
    assert target.xpath("string(c:metadata/md:title)", namespaces=ns) == "પરિચય"
    assert target.xpath("string(c:metadata/md:content-id)", namespaces=ns) == "m82462"
    assert target.xpath("string(c:metadata/md:uuid)", namespaces=ns) == "c591f886-799f-41d7-b3de-c43a547ed8ed"
    media = target.xpath("//c:media", namespaces=ns)
    assert len(media) == 1
    alt = media[0].get("alt")
    assert alt == "સંતુલન જળવાય તે રીતે ખૂબ કાળજીથી એક ઉપર એક ગોઠવેલા અનેક પથ્થરોનો ફોટો."
    assert not re.search(r"[A-Za-z]", alt)
    image = target.xpath("//c:image", namespaces=ns)[0]
    assert image.get("src") == "../../media/CNX_ElemAlg_Figure_02_00_001_img_new.jpg"
    assert image.get("mime-type") == "image/jpeg"
    caption = target.xpath("string(//c:caption)", namespaces=ns)
    para = target.xpath("string(//c:para)", namespaces=ns)
    assert "સંતુલિત" in caption and "કેન્દ્ર" in caption
    assert "સમીકરણની બંને બાજુએ સમાન રાશિ" in para
    assert "પદાવલીઓ" in para and "સમીકરણો ઉકેલીશું" in para
    assert not re.search(r"[A-Za-z]", caption + para)
    errata = json.loads(ERRATA.read_text(encoding="utf-8"))
    assert errata["entries"] == {}
    receipt = {
        "result": "pass",
        "module": "m82462",
        "source_sha256": sha(SRC),
        "translation_sha256": sha(GU),
        "errata_sha256": sha(ERRATA),
        "elements": len(target_elems),
        "source_ids": sum(x.get("id") is not None for x in target_elems),
        "prose_slots": 4,
        "exercises": len(target.xpath("//c:exercise", namespaces=ns)),
        "source_solutions": len(target.xpath("//c:solution", namespaces=ns)),
        "mathml": len(target.xpath("//*[namespace-uri()='http://www.w3.org/1998/Math/MathML']")),
        "media": len(media),
        "translated_alt": 1,
        "translated_aria_labels": 0,
        "translated_summaries": 0,
        "translated_title_attributes": 0,
        "errata_entries": len(errata["entries"]),
        "checks": [
            "source pin",
            "XML parse",
            "stable element hierarchy and identifiers",
            "non-prose attributes unchanged",
            "complete metadata, caption, paragraph and alt translation",
            "actual media reference retained",
            "no residual Latin prose"
        ]
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
