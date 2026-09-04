"""Print complete m49304 final Real-World category, including its inactive comment.

No writes or downloads. Normalize CRLF to LF, including inside the comment;
retain all other comment characters, XML entities and inactive status.
Active content stops after exercise61 and before
the outer Section Exercises/content closing tags and the document glossary.
"""
from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SECTION = "fs-id1165137832031"
PARENT = "fs-id1165135176628"
PREVIOUS = "fs-id1165137733672"
GLOSSARY_FIRST = "fs-id1165135445751"
EXERCISES = ("fs-id1165135511303", "fs-id1165137406705")
INACTIVE_IDS = ("fs-id1165137446701", "fs-id1165137758760")
ORIGINALS = (
    ("downloads/upstream-openstax/modules/m49304/index.cnxml",
     "0e230c4c96d46e7962dcb3afa1f1630718f7e1cdfae9e665d640690ab6ace19c"),
    ("downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml",
     "a341bb8c05830b95c865b18d64b186fc9a88a08640bbb12f030879faa90b7539"),
)


def extract(path):
    raw = path.read_text(encoding="utf-8")
    document = ET.fromstring(raw)
    content = document.find(CN+"content")
    parent = next(n for n in content if n.get("id")==PARENT)
    assert content[-1] is parent
    section = parent[-1]
    assert section.get("id")==SECTION and parent[-2].get("id")==PREVIOUS
    assert [n.get("id") for n in section.iter(CN+"exercise")]==list(EXERCISES)
    assert section[-1].get("id")==EXERCISES[-1]
    assert section[-1][-1][-1].get("id")=="fs-id1165137862357"
    glossary = document.find(CN+"glossary")
    assert glossary[0].get("id")==GLOSSARY_FIRST
    assert list(document).index(glossary)==list(document).index(content)+1
    marker = f'<section id="{SECTION}">'
    assert raw.count(marker)==1
    start = raw.index(marker)
    end = raw.index("</section>",start)+len("</section>")
    body = raw[start:end]
    assert body.count("<section ")==1
    assert raw[end:].lstrip().startswith("</section></content>")
    comments = re.findall(r"<!--[\s\S]*?-->",body)
    assert len(comments)==1
    assert all(f'id="{identity}"' in comments[0] for identity in INACTIVE_IDS)
    result = ('<document xmlns="http://cnx.rice.edu/cnxml" '
              'xmlns:m="http://www.w3.org/1998/Math/MathML">\n'
              '<content>\n'+body+'\n</content>\n</document>\n')
    active = ET.fromstring(result)
    assert len([n for n in active.iter() if n.get("id")])==8
    assert len(list(active.iter(M+"math")))==7
    assert not list(active.iter(CN+"solution"))
    assert not list(active.iter(CN+"image"))
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,default=ROOT.parent/ORIGINALS[0][0])
    sys.stdout.reconfigure(encoding="utf-8")
    print(extract(parser.parse_args().source),end="")
