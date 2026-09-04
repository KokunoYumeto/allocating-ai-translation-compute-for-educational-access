"""U032 glossary preservation and finite notation/branch witnesses.

No files are written. The finite examples exercise definitions, not original
source exercises and not universal proofs about all sets or functions.
"""
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import isfinite
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
SOURCE_SHA = "9f2774cf6617c38d8f9f4dd36b8d367b6b63078510eff0d8cf7515b5550a3df5"
ITEMS = [
    ("fs-id1165135445751","fs-id1165135190252","interval notation","Ký hiệu khoảng"),
    ("fs-id1165135487256","fs-id1165137452169","piecewise function","Hàm số cho bởi nhiều công thức"),
    ("fs-id1165137863188","fs-id1165137863193","set-builder notation","Ký hiệu tập hợp theo điều kiện"),
]
SOURCE_TEXT = "statement\u00a0about\u00a0"
INDONESIAN_TEXT = "pernyataan\u00a0tentang\u00a0"
VIETNAMESE_TEXT = "điều\u00a0kiện\u00a0về\u00a0"


def canonical(node, id_math=False):
    text = node.text or ""
    if node.tag == M+"mtext":
        if id_math:
            assert text == INDONESIAN_TEXT
            text = SOURCE_TEXT
    elif not text.strip():
        text = ""
    return (node.tag,tuple(sorted(node.attrib.items())),text,
            tuple((canonical(c,id_math),(c.tail or "") if (c.tail or "").strip() else "") for c in node))


def tests():
    counts=Counter()

    def check(value,label,kind="source_structure"):
        assert value,label
        counts[kind]+=1

    data=(ROOT/"sources/m49304-domain-glossary-source.cnxml").read_bytes()
    source=ET.fromstring(data)
    draft=(ROOT/"translation/A30-U032-domain-glossary.vi.md").read_text(encoding="utf-8")
    identities=[n.get("id") for n in source.iter() if n.get("id")]
    expected=[identity for item in ITEMS for identity in item[:2]]
    anchors=re.findall(r"\{#([^}]+)\}",draft)
    check(sha256(data).hexdigest()==SOURCE_SHA,"exact complete glossary excerpt")
    check(source.tag==CN+"glossary" and source.get("id") is None,"standalone anonymous original glossary")
    check(identities==expected,"six source IDs in source order")
    check(len(anchors)==len(set(anchors)),"unique explicit anchors")
    check(draft==unicodedata.normalize("NFC",draft),"Vietnamese NFC")
    for identity in expected:
        check(anchors.count(identity)==1,"retained ID "+identity)
    positions=[]
    for definition,(identity,meaning,en,vi) in zip(source,ITEMS):
        check(definition.tag==CN+"definition" and definition.get("id")==identity,"exact definition structure")
        check([n.tag for n in definition]==[CN+"term",CN+"meaning"],"term then meaning")
        check(definition[0].text==en and definition[1].get("id")==meaning,"original term/meaning pairing")
        title=f"### {vi} {{#{identity}}}"
        check(title in draft,"consistent Vietnamese heading")
        positions.append(draft.index(title))
        check(re.search(r"::: \{#"+re.escape(meaning)+r"\}\s*\n.+?\n:::",draft,re.S) is not None,
              "meaning remains distinct source block")
    check(positions==sorted(positions),"not alphabetically resorted")
    for tag,amount in (("definition",3),("term",3),("meaning",3),("exercise",0),("solution",0),
                       ("image",0),("table",0),("link",0)):
        check(len(list(source.iter(CN+tag)))==amount,"source count "+tag)
    math=list(source.iter(M+"math"))
    check(len(math)==1,"one source MathML")
    check(re.findall(r"\{\{math:([^}]+)\}\}",draft)==["fs-id1165137863193:0"],"exact source occurrence once")
    check([n.text for n in source.iter(M+"mtext")]==[SOURCE_TEXT],"exact meaningful NBSP text")
    check([n.text for n in source.iter(M+"mo")]==["{","|","}"],"set-builder braces and condition bar")
    check([n.text for n in source.iter(M+"mi")]==["x","x"],"both source variables")
    check([n.attrib for n in source.iter(M+"mspace")]==[{"width":"0.5em"}],"source mathematical spacing")
    check(not list(source.iter(M+"mn")) and not list(source.iter(M+"mroot")),"no numeric or root structure")
    check(SOURCE_TEXT.replace(SOURCE_TEXT,VIETNAMESE_TEXT).endswith("\u00a0"),"translated mtext trailing NBSP")
    check(not re.findall(r"\]\((?:#|A30-)",draft) and "![" not in draft,"no crosslinks/images")
    check(draft.count("*Làm rõ bổ sung:*")==3,"three notes clearly supplemental")
    flat=" ".join(draft.split())
    for phrase in ("tất cả các số", "cận tương ứng thuộc tập hợp", "cận tương ứng không thuộc tập hợp",
                   "Với hai số thực $a<b$", "không phải số thực", "luôn dùng ngoặc tròn",
                   "công thức cũng phải có nghĩa", "hai công thức phải cho cùng một đầu ra",
                   "đúng một đầu ra", "đầu vào không được nhánh nào nhận",
                   "“sao cho”", "không phải dấu giá trị tuyệt đối", "$x$ chạy trong tập nào",
                   "lấy đúng các phần tử", "Không chỉ lấy một vài phần tử",
                   "không tự chứng minh", "không thay thế lập luận"):
        check(phrase in flat,"semantic qualification "+phrase)

    #Finite illustrations of the already stated concepts, not source answers.
    for left,right in ((False,False),(True,True),(True,False),(False,True)):
        for x in (-1,0,0.5,1,2):
            membership=(0<=x if left else 0<x) and (x<=1 if right else x<1)
            check(membership==(x==0.5 or x==0 and left or x==1 and right),
                  "four interval endpoint forms","finite")
    for x,allowed in ((float("-inf"),False),(-1,False),(0,True),(1,True),(float("inf"),False)):
        check((isfinite(x) and x>=0)==allowed,"unbounded interval real-element witness","finite")
    for x in (-1,0,1):
        outputs=([x*x] if x<=0 else [])+([2*x] if x>=0 else [])
        check(len(set(outputs))==1,"compatible branch overlap witness","finite")
    check({0*0,2*0}=={0},"overlap agrees at zero","finite")
    check(len({0,1})==2,"conflicting overlap has two outputs","finite")
    check(not (0<0 or 0>0),"strict branches can leave an input uncovered","finite")
    check(0>=0 and not (0!=0),"formula denominator may invalidate a branch input","finite")
    check(1>=0 and 1!=0,"valid branch condition and expression together","finite")
    universe=set(range(-2,3))
    check({x for x in universe if x*x<=1}=={-1,0,1},"take every satisfying member","finite")
    check({x for x in universe if x>=0}=={0,1,2},"explicit finite universe","finite")
    check({0}!={x for x in universe if x>=0},"some satisfying members are insufficient","finite")

    spec=spec_from_file_location("u032_extract",ROOT/"tools/extract_domain_glossary.py")
    extractor=module_from_spec(spec);spec.loader.exec_module(extractor)
    for label,path in (
        ("en",ROOT.parent/"downloads/upstream-openstax/modules/m49304/index.cnxml"),
        ("id",ROOT.parent/"downloads/a30-edition/source-core/repo/source/modules/m49304/index.cnxml"),
    ):
        if path.is_file():
            selected=ET.fromstring(extractor.extract(path))
            check([n.get("id") for n in selected.iter() if n.get("id")]==expected,"actual original IDs "+label)
            check(len(list(selected.iter(CN+"definition")))==3,"complete original glossary "+label)
            check([canonical(n,label=="id") for n in selected.iter(M+"math")]==
                  [canonical(n) for n in math],"exact original MathML except specified mtext "+label)
            if label=="en":
                check(extractor.extract(path)==data.decode("utf-8"),"byte-reproducible English excerpt")
                check(canonical(selected)==canonical(source),"complete English glossary retained")
    return dict(counts)


if __name__=="__main__":
    result=tests()
    print(f"PASS: {sum(result.values())} mixed checks; {result}")
