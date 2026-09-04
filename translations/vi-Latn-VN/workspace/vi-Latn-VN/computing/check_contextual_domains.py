"""Read-only U031 active-source, archival-comment and contextual-domain checks.

Default requires only committed U031 files and Python's standard library.
--originals verifies the two pinned local originals, including the inactive
comment and the exact final-category boundary. Time-domain samples are not
proofs on all real numbers; the written factor/sign argument supplies that.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CN = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
EXCERPT_SHA = "77fe2d5222c63f6f2643e4790d97c6246c46c0bad791daf28f51b23c1d511b7e"
COMMENT_SHA = "a72eaf7912e9f39f5e1fd1aeff9c25e8a0827069c52ee3553740dc3034cbee64"
ACTIVE_IDS = (
    "fs-id1165137832031", "fs-id1165135511303", "fs-id1165135511305",
    "fs-id1165135336103", "fs-id1165137406705", "fs-id1165137406708",
    "fs-id1165133045371", "fs-id1165137862357",
)
INACTIVE_IDS = ("fs-id1165137446701", "fs-id1165137758760")


def height(t):
    return -16*t*t + 96*t


def cost(x):
    return 10*x + 500


def item_domain(x):
    return x.denominator == 1 and x >= 0 and cost(x) <= 1500


def time_domain(t):
    return t >= 0 and height(t) >= 0


def math_text(node):
    return (node.text or "").strip() + "".join(math_text(n) for n in node)


def signature(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple((signature(c), (c.tail or "").strip()) for c in node))


def comment_xml(comment):
    return ET.fromstring(
        '<document xmlns="http://cnx.rice.edu/cnxml" '
        'xmlns:m="http://www.w3.org/1998/Math/MathML">'
        + comment.decode("utf-8")[4:-3] + "</document>")


def tests(originals=False, details=False):
    counts = Counter()

    def check(condition, message, kind="source_structure"):
        assert condition, message
        counts[kind] += 1

    data = (ROOT/"sources/m49304-contextual-domains-source.cnxml").read_bytes()
    source = ET.fromstring(data)  # Normal XML parsing deliberately ignores comments.
    md = (ROOT/"translation/A30-U031-contextual-domains.vi.md").read_text("utf-8")
    by_id = {n.get("id"): n for n in source.iter() if n.get("id")}
    anchors = re.findall(r"\{#([^}]+)\}",md)
    check(sha256(data).hexdigest()==EXCERPT_SHA, "exact LF-normalized excerpt")
    check(md==unicodedata.normalize("NFC",md), "Vietnamese NFC")
    check(tuple(by_id)==ACTIVE_IDS, "eight active module-qualified source IDs in order")
    check(len(anchors)==len(set(anchors)), "explicit anchors unique")
    for identity in ACTIVE_IDS:
        check(anchors.count(identity)==1, f"active anchor once:m49304/{identity}")
    for identity in INACTIVE_IDS:
        check(identity not in by_id and identity not in anchors,
              f"inactive comment ID not activated:{identity}")
    for tag,expected in (("section",1),("exercise",2),("problem",2),("para",2),
                         ("solution",0),("list",1),("item",3),("image",0),("example",0)):
        check(len(list(source.iter(CN+tag)))==expected, f"active source {tag}:{expected}")
    check(re.findall(r"^### Bài (\d+) ",md,re.M)==["60","61"], "original numbering60–61")
    maths = list(source.iter(M+"math"))
    check(len(maths)==7, "seven active source MathML expressions")
    captures = []
    for owner,index in re.findall(r"\{\{math:([^:}]+):(\d+)\}\}",md):
        check(owner in by_id, "MathML owner is active, not a comment")
        options = list(by_id[owner].iter(M+"math"))
        check(int(index)<len(options), "valid active source MathML index")
        captures.append(options[int(index)])
    check(Counter(map(id,captures))==Counter(map(id,maths)), "all seven active maths once")
    check(not list(source.iter(M+"mtext")), "zero active source mtext payloads")
    for identity,numerals in (
        ("fs-id1165135336103",["−16","2","96"]),
        ("fs-id1165133045371",["10","500."]),
        ("fs-id1165137862357",[]),
    ):
        check([n.text for n in by_id[identity].iter(M+"mn")]==numerals,
              f"source numerals including punctuation preserved:{identity}")
    check([n.text for n in source.iter(CN+"span")]==["ⓐ","ⓑ","ⓒ"],
          "all three source subpart glyphs")
    check(all(md.count(glyph)==2 for glyph in ("ⓐ","ⓑ","ⓒ")),
          "each subpart appears in source prompt and new solution")
    listing=by_id["fs-id1165137862357"]
    check(listing.attrib.get("list-type")=="enumerated" and
          listing.attrib.get("number-style")=="arabic" and
          listing.attrib.get("class")=="circled", "original list attributes")
    check("25 items" in "".join(listing[1].itertext()), "source25items preserved")
    check("$1500" in "".join(listing[2].itertext()), "source1500dollar ceiling preserved")
    check("foot (ft)" in md and "giây" in md and "1500 đô la" in md,
          "source units feet/seconds/dollars not silently converted")
    local=re.findall(r"\]\(#([^)]*)\)",md)
    check(len(local)==4 and all(anchors.count(t)==1 for t in local), "four local jumps/backlinks")
    check(not re.findall(r"\]\(A30-",md) and "![" not in md, "zero cross-reader links/images")
    check("Đáp án nguồn:" not in md, "no published source solution invented")
    plain=" ".join(md.split())
    check(plain.count("**Lời giải bổ sung — phần nội dung hiển thị của nguồn không kèm đáp án.**")==2,
          "both detailed explanations explicitly new")

    comments=re.findall(rb"<!--[\s\S]*?-->",data)
    check(len(comments)==1, "one archival XML comment")
    comment=comments[0]
    check(sha256(comment).hexdigest()==COMMENT_SHA and len(comment)==421,
          "exact LF comment payload/entities retained")
    archival=comment_xml(comment)
    check(tuple(n.get("id") for n in archival.iter() if n.get("id"))==INACTIVE_IDS,
          "two archival IDs counted separately")
    check(len(list(archival.iter(M+"math")))==1, "one archival math excluded from seven active")
    check([n.text for n in archival.iter(M+"mtext")]==["\u2009","\u00a0","\u2009"],
          "three archival spacing-only mtexts, not active translation entries")
    check(math_text(next(archival.iter(M+"math")))=="[0,6];",
          "archival answer states closed domain0to6")
    check("it takes 6 seconds for the projectile to leave the ground and return to the ground"
          in comment.decode("utf-8"), "archival English explanation retained")
    for phrase in ("nằm trong chú thích XML", "không thuộc nội dung đang hiển thị",
                   "không được chuyển thành đáp án nguồn đang hiển thị",
                   "Lập luận chi tiết ở trên do bản dịch bổ sung",
                   "tập xác định lớn nhất trong các số thực là",
                   "khi lấy cả hai thời điểm biên", "không chỉ các giây nguyên",
                   "Trong cách hiểu đếm từng sản phẩm nguyên chiếc",
                   "Không có giới hạn công suất nào khác",
                   "Phương án mô hình hóa bổ sung",
                   "Đây là một giả thiết mô hình hóa khác"):
        check(phrase in plain, f"explicit material qualification:{phrase}")
    for formula in (
        r"h(t)=-16t^2+96t=16t(6-t)", r"D=[0,6]",
        r"C(0)=10\cdot0+500=500", r"C(25)=10\cdot25+500=750",
        r"10x+500\le1500\quad\Longleftrightarrow\quad x\le100",
        r"D=\{0,1,2,\ldots,100\}", r"\{x\in\mathbb Z\mid0\le x\le100\}",
        r"R=\{500,510,520,\ldots,1500\}",
        r"R=\{500+10n\mid n\in\mathbb Z,\ 0\le n\le100\}",
        r"x=(y-500)/10\in[0,100]",
    ):
        check(formula in md, f"reviewed new result retained:{formula}")

    # Exact coefficient identity 16*t*(6-t) == -16*t^2+96*t.
    coefficients=[0,16*6,16*(-1)]
    check(coefficients==[0,96,-16], "exact height factorization coefficients", "exact_math")
    check(height(F(0))==height(F(6))==0, "launch/landing heights exactlyzero", "exact_math")
    check(cost(F(0))==500 and cost(F(25))==750 and cost(F(100))==1500,
          "fixed cost,25items,and inclusive ceiling", "exact_math")
    check(F(1500-500,10)==100, "exact algebraic production upperbound", "exact_math")
    check(not item_domain(F(-1)) and not item_domain(F(101)),
          "outside integer endpoint candidates excluded", "exact_math")
    check(cost(F(1,2))==505 and not item_domain(F(1,2)),
          "505dollars would require halfanitem; not discrete range", "exact_math")

    # This is exhaustive on the entire101-element prescribed integer domain.
    values=[]
    for n in range(101):
        y=cost(F(n))
        check(item_domain(F(n)) and y==F(500+10*n) and 500<=y<=1500,
              f"complete admissible discrete input:{n}", "exhaustive_discrete")
        values.append(y)
    check(set(values)==set(map(F,range(500,1501,10))) and len(set(values))==101,
          "exact complete discrete image set", "exact_math")
    check(all((y-500)/10 in range(101) for y in values),
          "every discrete output has an admissible integer preimage", "exact_math")
    check(505 not in values, "discrete image is not the continuousinterval", "exact_math")

    for t in map(F,("-10","-0.1","0","0.1","0.5","1","3","5.9","6","6.1","10")):
        check(time_domain(t)==(0<=t<=6) and (height(t)>0)==(0<t<6),
              f"time sign/domain witness:{t}", "finite_continuous")
    for y in map(F,("500","505","750","1000","1499","1500")):
        x=(y-500)/10
        check(0<=x<=100 and cost(x)==y,
              f"continuous relaxation preimage witness:{y}", "finite_continuous")
    # Algebraic composition identity for all real y, not only the six witnesses:
    check(F(10)*F(1,10)==1 and F(10)*F(-500,10)+500==0,
          "C((y-500)/10)=y by exact affine coefficients", "exact_math")

    if originals:
        sys.path.insert(0,str(ROOT/"tools"))
        from extract_contextual_domains import ORIGINALS,extract
        for relative,digest in ORIGINALS:
            path=ROOT.parent/relative
            original_bytes=path.read_bytes()
            check(sha256(original_bytes).hexdigest()==digest,"pinned module hash","originals")
            reproduced=extract(path)
            original=ET.fromstring(reproduced)
            check(tuple(n.get("id") for n in original.iter() if n.get("id"))==ACTIVE_IDS,
                  "both originals have same eight active IDs","originals")
            check([signature(n) for n in original.iter(M+"math")]==
                  [signature(n) for n in maths],"all seven original active maths identical","originals")
            check(not list(original.iter(CN+"solution")),"no active source solution in either edition","originals")
            raw_comment=re.findall(rb'<!--<solution id="fs-id1165137446701">[\s\S]*?-->',
                                   original_bytes)
            check(len(raw_comment)==1 and raw_comment[0].replace(b"\r\n",b"\n")==comment,
                  "archival original comment exact apart from declared lineending normalization","originals")
            if "upstream-openstax" in relative:
                check(reproduced.encode("utf-8")==data,"entire EN category reproduced after LFnormalization","originals")
    return dict(counts) if details else sum(counts.values())


if __name__=="__main__":
    result=tests(originals="--originals" in sys.argv,details=True)
    print(f"PASS: {sum(result.values())} mixed assertions; {result}; finite time probes are not proofs")

