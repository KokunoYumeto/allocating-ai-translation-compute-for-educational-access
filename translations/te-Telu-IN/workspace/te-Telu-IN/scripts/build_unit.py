"""Strict next-unit compiler. Does not weaken the separately frozen TE-B001 build.

Each new source structure requires explicit support and tests. No full-book CNXML
conformance claim; no downloads, network assets, training export or learner data.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import html
import json
import re
import shutil
import xml.etree.ElementTree as ET
from build import atomic_write, HTMLCheck, local, serialize
from inspect_source import slots, CN, MATH
from naming_checks import validate_b004
from writing_checks import validate_b005
from rounding_checks import validate_b006
from recap_checks import validate_b007
from practice_checks import validate_b008
from auxiliary_checks import validate_auxiliary
from readiness_checks import validate_readiness
from addition_checks import validate_b013
from addition_model_checks import validate_b014
from addition_algorithm_checks import validate_b015
from phrase_addition_checks import validate_b016
from application_addition_checks import validate_application_target,validate_application_bridge
from addition_recap_checks import validate_b018
from chapter_review_checks import validate_b019

BASE=Path(__file__).resolve().parents[1]
XML="{http://www.w3.org/XML/1998/namespace}"
MD="{http://cnx.rice.edu/mdml}"
PROTECTED_METADATA_TAGS={MD+"content-id",MD+"uuid"}
MATH_PROSE={"Sum = ":"మొత్తం = "}
SCOPED_MATH_PROSE={
    "TE-B017":{"s013":("and","మరియు"),"s068":("and","మరియు")},
    "TE-B019":{"s422":("16-ounce","16 ఔన్సుల"),
                "s430":("16-ounce","16 ఔన్సుల"),
                "s438":("12-oz","12 ఔన్సుల"),
                "s446":("12-oz","12 ఔన్సుల"),
                "s463":("and"," మరియు "),
                "s482":("and"," మరియు ")}}
MATH_PASSTHROUGH={"base-10"}
MATH_IDENTIFIERS={"TE-B015":{"a","b"},"TE-B018":{"a","b"}}
TABLE_COLUMN_CORRECTIONS={"fs-id1171100715908":(3,2),
                          "eip-659":(3,2),"eip-493":(3,2),"eip-379":(3,2),
                          "eip-695":(3,2),"eip-596":(3,2),"eip-951":(3,2),
                          "eip-id1168287208889":(3,2),"eip-id1168288224694":(3,2),
                          "eip-id11688224694":(3,2),"eip-id1168288293873":(3,2),
                          "eip-id1168287505854":(3,2),"eip-id1168287251210":(3,2),
                          "eip-id1168288687380":(3,2),"eip-id1168288531101":(3,2),
                          "fs-id1826990":(5,4),"eip-id1168288294973":(3,2),
                          "eip-id1168288520954":(3,2),
                          "eip-id1168288617772":(3,2),"eip-id1168289453960":(3,2)}
TABLE_EDITORIAL_LABELS={"fs-id2300206":{
    "en":"Addition table: row and column addends run from 0 to 9; each body cell gives their sum.",
    "te":"సంకలన పట్టిక: అడ్డ, నిలువు వరుసల కలిపే సంఖ్యలు 0 నుంచి 9 వరకు; ప్రతి లోపలి గడిలో ఆ రెండు సంఖ్యల మొత్తం ఉంది."}}
TABLE_ROW_HEADERS={"fs-id2300206"}
SOURCE_TABLE_LINKS={"fs-id2300206","fs-id1826990"}
SOURCE_URL_LINKS={"https://www.openstax.org/l/24detplaceval",
                  "https://www.openstax.org/l/24numdigword",
                  "https://www.openstax.org/l/24add2blocks",
                  "https://www.openstax.org/l/24add3blocks",
                  "https://www.openstax.org/l/24addwhlnumb"}
SOURCE_INLINE_BASE10_LINKS={"https://www.openstax.org/l/24add2blocks",
                            "https://www.openstax.org/l/24add3blocks"}
SOURCE_DOCUMENT_LINKS={
    ("m81243","fs-id2222880"):"TE-B002.html",
    ("m81243","fs-id3202693"):"TE-B005.html",
}
COLLAPSED_SOURCE_ANSWERS={"TE-B008","TE-B011","TE-B012","TE-B019"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unit_inputs(unit):
    assert re.fullmatch(r"TE-B\d{3}",unit)
    raw=(BASE/"sources"/(unit+".en.cnxml")).read_bytes()
    metadata=json.loads((BASE/"sources"/(unit+".source.json")).read_text(encoding="utf-8"))
    catalog=json.loads((BASE/"translations"/(unit+".te.json")).read_text(encoding="utf-8"))
    assert sha(raw)==metadata["source_sha256"],"Frozen unit changed"
    assert catalog["unit_id"]==metadata["unit"]==unit
    assert catalog["source_commit"]==metadata["source_commit"]
    assert catalog["module_id"]==metadata["module"] and catalog["section_id"]==metadata["section"]
    lock=json.loads((BASE/"sources.lock.json").read_text(encoding="utf-8"))
    assert metadata["source_module"] in lock["source_files"]
    collection=next(c for c in lock["collections"] if c["course"]==metadata["course"])
    repo=next(r for r in lock["repositories"] if r["id"]==collection["upstream_repository_id"])
    assert repo["commit"]==metadata["source_commit"]
    assert catalog.get("protected_slots",{})==metadata.get("protected_slots",{}),"Protected metadata declaration drift"
    return ET.fromstring(raw),metadata,catalog


def asset_map(unit):
    manifest=json.loads((BASE/"assets"/unit.replace("TE-","")/"manifest.json").read_text(encoding="utf-8"))
    mapping={}
    for asset in manifest["assets"]:
        assert asset["original_src"] not in mapping
        for key,digest in [("original_path","original_sha256"),("localized_path","localized_sha256")]:
            path=(BASE/asset[key]).resolve()
            assert path.is_relative_to(BASE.resolve()) and path.is_file()
            assert sha(path.read_bytes())==asset[digest],str(path)
        mapping[asset["original_src"]]=asset
    return mapping


def localize(source,catalog,assets):
    target=copy.deepcopy(source)
    all_slots=list(slots(target))
    assert len(all_slots)==catalog["expected_text_slot_count"],"Source slot drift"
    used=set()
    protected=catalog.get("protected_slots",{})
    assert not set(protected)&set(catalog["translations"]),"Protected metadata cannot be translated"
    protected_used=set()
    for i,(element,key,value) in enumerate(all_slots,1):
        name=f"s{i:03d}"
        is_math=element.tag.startswith(MATH) and key=="text"
        if name in protected:
            declaration=protected[name]
            assert element.tag in PROTECTED_METADATA_TAGS and key=="text","Only registered metadata identifiers may pass through"
            assert declaration["tag"]==element.tag and declaration["value"]==value and declaration["reason"],"Protected metadata value/tag drift"
            protected_used.add(name)
        elif name in catalog["translations"]:
            translated=catalog["translations"][name]
            assert re.search(r"[\u0c00-\u0c7f]",translated),name
            if is_math:
                scoped=SCOPED_MATH_PROSE.get(catalog.get("unit_id"),{}).get(name)
                assert local(element.tag)=="mtext" and (MATH_PROSE.get(value)==translated or scoped==(value,translated)),"Math token changed"
            if key in ("alt","aria-label","summary"):
                element.set(key,translated)
            else:
                setattr(element,key,translated)
            used.add(name)
        elif re.search(r"[A-Za-z]",value):
            passthrough=(local(element.tag)=="mtext" and value in MATH_PASSTHROUGH)
            identifier=(local(element.tag)=="mi" and value in MATH_IDENTIFIERS.get(catalog.get("unit_id"),set()))
            assert is_math and (passthrough or identifier),f"Untranslated prose {name}: {value}"
    assert used==set(catalog["translations"]),"Unused translation slot"
    assert protected_used==set(protected),"Unused protected metadata slot"
    images=list(target.iter(CN+"image"))
    assert {e.get("src") for e in images}==set(assets),"Source/asset mapping mismatch"
    for image in images:
        image.set("src",assets[image.get("src")]["localized_path"])
        image.set("mime-type","image/svg+xml")
    target.set(XML+"lang","te-Telu-IN")
    return target


def math_signature(root):
    reverse={v.strip():k.strip() for k,v in MATH_PROSE.items()}
    if root.get("id")=="fs-id2197427":reverse["మరియు"]="and"
    if root.get("id")=="fs-id2263283":
        reverse.update({"16 ఔన్సుల":"16-ounce","12 ఔన్సుల":"12-oz","మరియు":"and"})
    return [(local(e.tag),sorted(e.attrib.items()),reverse.get((e.text or "").strip(),(e.text or "").strip())) for e in root.iter() if e.tag.startswith(MATH)]


def structural_signature(root):
    def walk(element,depth):
        yield (element.tag,depth,element.get("id"))
        for child in element:
            yield from walk(child,depth+1)
    return list(walk(root,0))


def validate_b002_bridge(bridge):
    """Check the actual added explanations, not merely hard-coded arithmetic."""
    required={
        "B002-usd-context":["3 × $100 = $300","7 × $10 = $70","4 × $1 = $4","$300 + $70 + $4 = $374"],
        "B002-table-guide":["3 × 10 = 30"],
        "B002-zero-place":["107","100 + 0 + 7","17"],
        "B002-worked-176":["1 × 100 = 100","7 × 10 = 70","6 × 1 = 6","100 + 70 + 6 = 176","1 + 7 + 6 = 14"],
        "B002-worked-237":["2 × 100 = 200","3 × 10 = 30","7 × 1 = 7","200 + 30 + 7 = 237"]}
    by_id={e.get("id"):e for e in bridge.iter() if e.get("id")}
    for ident,expressions in required.items():
        assert ident in by_id,"Missing worked explanation: "+ident
        text=" ".join("".join(by_id[ident].itertext()).split())
        for expression in expressions:
            assert expression in text,"Worked expression changed: "+ident+": "+expression


def render_bridge(bridge):
    """Add local table scrolling without altering the authored bridge source."""
    bridge=copy.deepcopy(bridge)
    for e in bridge.iter():
        e.tag=local(e.tag)
    # The practice author supplies circled part labels. Do not add a second
    # automatic a./b. marker; source XHTML and all part IDs remain unchanged.
    if bridge.get("id")=="B008-bridge":
        for listing in bridge.iter("ol"):
            if len(listing) and all(child.tag=="li" and re.match(r"[ⓐ-ⓩ]", "".join(child.itertext()).lstrip()) for child in listing):
                listing.set("class","labeled-list")
    parents={child:parent for parent in bridge.iter() for child in parent}
    for table in list(bridge.iter("table")):
        rows=list(table.iter("tr")); assert rows
        count=len(rows[0]); assert count>0 and all(len(row)==count for row in rows)
        for head in table.findall("thead/tr/th"):
            head.set("scope","col")
        parent=parents[table]; index=list(parent).index(table)
        hint=f"చిన్న తెరపై {count} నిలువు వరుసలూ చూడటానికి పట్టికను అడ్డంగా జరపండి."
        para=ET.Element("p",{"class":"scroll-hint"}); para.text=hint
        wrapper=ET.Element("div",{"class":"table-scroll","tabindex":"0","role":"region","aria-label":hint})
        parent.remove(table); parent.insert(index,para); parent.insert(index+1,wrapper)
        wrapper.append(table)
    return ET.tostring(bridge,encoding="unicode",method="html")


def validate_b003_bridge(bridge):
    by_id={e.get("id"):e for e in bridge.iter() if e.get("id")}
    for kind in ("D","R"):
        for i in range(1,5):
            assert f"B003-{kind}{i:02d}" in by_id
            assert f"B003-S-{kind}{i:02d}" in by_id
    required={
        "B003-convention":["0 × 10,000 = 0","63,407,218"],
        "B003-indian-grouping":["5,278,194","52,78,194","1,000,000 = 10,00,000","10,000,000 = 1,00,00,000"],
        "B003-S-D01":["0 × 10,000 = 0"],
        "B003-S-D02":["3 × 100,000 = 300,000"],
        "B003-S-D03":["8 | 205 | 041","205 × 1,000 = 205,000","820541"],
        "B003-S-D04":["6 × 1,000 = 6,000","6 × 10,000 = 60,000","60,000 = 10 × 6,000"],
        "B003-S-R01":["0 × 10,000 = 0"],
        "B003-S-R02":["4 × 100,000 = 400,000"],
        "B003-S-R03":["6 | 307 | 052","307 × 1,000 = 307,000","630752"],
        "B003-S-R04":["8 × 100,000 = 800,000","8 × 1,000,000 = 8,000,000","8,000,000 = 10 × 800,000"]}
    for ident,expressions in required.items():
        text=" ".join("".join(by_id[ident].itertext()).split())
        assert all(s in text for s in expressions),"B003 worked expression changed: "+ident
    cases=[(27493615,"B003-S-fs-id1573052",[(2,7,"ten millions"),(1,1,"tens"),(4,5,"hundred thousands"),(7,6,"millions"),(5,0,"ones")]),
           (519711641328,"B003-S-fs-id1518735",[(9,9,"billions"),(4,4,"ten thousands"),(2,1,"tens"),(6,5,"hundred thousands"),(7,8,"hundred millions")])]
    for number,ident,expected in cases:
        rows=[e for e in by_id[ident].iter() if local(e.tag)=="tr"][1:]
        assert len(rows)==len(expected)==5
        for row,(digit,power,name) in zip(rows,expected):
            cells=["".join(e.itertext()).strip() for e in row]
            assert len(cells)==4 and cells[0].endswith(str(digit))
            assert cells[1]==f"{power+1}వ" and name in cells[2],"Wrong place in bridge table"
            assert number//(10**power)%10==digit
            match=re.fullmatch(r"([0-9,]+) × ([0-9,]+) = ([0-9,]+)",cells[3])
            assert match,"Invalid worked product"
            values=tuple(int(s.replace(",","")) for s in match.groups())
            assert values==(digit,10**power,digit*10**power),"Wrong contribution in bridge table"


def render(root,assets,prefix="",english=False,collapse_solutions=False):
    esc=html.escape
    tag=local(root.tag)
    ident=f' id="{esc(prefix+root.get("id"))}"' if root.get("id") else ""
    if root.tag.startswith(MATH):
        node=copy.deepcopy(root); node.tail=None
        for e in node.iter():
            e.tag=local(e.tag)
        node.set("xmlns",MATH[1:-1])
        return ET.tostring(node,encoding="unicode")
    if root.tag.startswith(MD):
        assert tag in {"content-id","uuid","title","abstract"},"Unsupported metadata element"
        if tag in {"content-id","uuid"}:
            assert not len(root),"Nested metadata identifier"
            label="Source module ID" if tag=="content-id" else "Source UUID"
            return f'<p{ident} class="meta">{label}: <code>{esc(root.text or "")}</code></p>'
    if root.tag==CN+"definition":
        assert [e.tag for e in root]==[CN+"term",CN+"meaning"],"Unexpected glossary definition structure"
        term,meaning=root
        return (f'<div{ident} class="cn-definition"><dt>'
                +render(term,assets,prefix,english,collapse_solutions)+esc(term.tail or "")
                +'</dt>'+render(meaning,assets,prefix,english,collapse_solutions)+'</div>')
    if tag=="media":
        image=root.find(CN+"image"); assert image is not None
        if english:
            path=assets[image.get("src")]["original_path"]
        else:
            path=image.get("src")
        alt=root.get("alt","")
        assert alt
        asset=assets[image.get("src")] if english else next(a for a in assets.values() if a["localized_path"]==path)
        min_width=int(asset.get("recommended_min_width_px",0))
        assert 0<=min_width<=4000
        if min_width:
            hint="Scroll sideways to inspect every column." if english else "అన్ని నిలువు వరుసలను చూడటానికి పటాన్ని అడ్డంగా జరపండి."
            style=f' style="min-width:{min_width}px"'
            return f'<p class="scroll-hint">{hint}</p><div{ident} class="cn-media media-scroll" tabindex="0" role="region" aria-label="{esc(hint)}"><img{style} src="../{esc(path)}" alt="{esc(alt)}"/></div>'
        return f'<div{ident} class="cn-media"><img src="../{esc(path)}" alt="{esc(alt)}"/></div>'
    if tag=="link":
        if root.get("url"):
            url=root.get("url")
            assert url in SOURCE_URL_LINKS and not root.get("target-id"),"Unregistered source URL"
            if url in SOURCE_INLINE_BASE10_LINKS:
                assert len(root)==1 and root[0].tag==MATH+"math","Unsupported inline source link label"
                math=list(root[0].iter())
                assert [(e.tag,e.attrib,(e.text or "").strip()) for e in math]==[
                    (MATH+"math",{},""),(MATH+"mrow",{},""),(MATH+"mtext",{},"base-10")],"Inline base-10 source link changed"
                assert not any((e.tail or "").strip() for e in math[1:]),"Unexpected inline MathML tail"
                assert (root.text or "").strip() and (root[0].tail or "").strip(),"Incomplete inline source link label"
                return f'<a{ident} href="{esc(url)}">{esc(root.text)}'+render(root[0],assets,prefix,english,collapse_solutions)+esc(root[0].tail)+"</a>"
            assert not len(root) and (root.text or "").strip(),"Unsupported source link label"
            return f'<a{ident} href="{esc(url)}">{esc(root.text)}</a>'
        target=root.get("target-id"); assert target
        if root.get("document"):
            key=(root.get("document"),target)
            assert key in SOURCE_DOCUMENT_LINKS,"Unregistered cross-module source link"
            label="Referenced example" if english else "సంబంధిత ఉదాహరణ"
            return f'<a{ident} href="{SOURCE_DOCUMENT_LINKS[key]}#{prefix}{esc(target)}">{label}</a>'
        if target in SOURCE_TABLE_LINKS:
            label="Referenced table" if english else "సంబంధిత పట్టిక"
        else:
            label="Referenced figure" if english else "సంబంధిత పటం"
        return f'<a{ident} href="#{prefix}{esc(target)}">{label}</a>'
    if tag=="table":
        group=root.find(CN+"tgroup"); assert group is not None
        declared=int(group.get("cols")); count=declared
        if root.get("id") in TABLE_COLUMN_CORRECTIONS:
            expected,count=TABLE_COLUMN_CORRECTIONS[root.get("id")]
            assert declared==expected,"Registered table source changed"
        assert 1<=count<=20
        headings=[" ".join(e.itertext()).strip() for e in group.findall(CN+"thead/"+CN+"row/"+CN+"entry")]
        assert not headings or len(headings)==count
        aria=root.get("aria-label") or root.get("summary")
        if not aria and root.get("id") in TABLE_EDITORIAL_LABELS:
            assert count==11 and headings==["+"]+[str(i) for i in range(10)],"Registered addition-table header changed"
            aria=TABLE_EDITORIAL_LABELS[root.get("id")]["en" if english else "te"]
        image_steps=count==2 and any(True for _ in root.iter(CN+"media"))
        if english and root.get("id") in {"fs-id1714120","fs-id1785447"}:
            assert count==5
            aria="Place-value table with five columns: "+", ".join(headings)+". Three place rows and a total row."
        assert aria
        parts=[]
        for area in ["thead","tbody"]:
            region=group.find(CN+area)
            if region is None:
                assert area=="thead"
                continue
            rows=[]
            for row in region:
                assert local(row.tag)=="row" and len(row)==count
                cells=[]
                for column,entry in enumerate(row):
                    assert local(entry.tag)=="entry"
                    content=esc(entry.text or "")+"".join(render(c,assets,prefix,english,collapse_solutions)+esc(c.tail or "") for c in entry)
                    row_header=area=="tbody" and column==0 and root.get("id") in TABLE_ROW_HEADERS
                    element="th" if area=="thead" or row_header else "td"
                    scope=' scope="col"' if area=="thead" else (' scope="row"' if row_header else "")
                    align=' class="right"' if entry.get("align")=="right" else ""
                    readable=' style="min-width:300px;text-align:left"' if image_steps and column==0 else ""
                    cells.append(f'<{element}{scope}{align}{readable}>{content}</{element}>')
                rows.append("<tr>"+"".join(cells)+"</tr>")
            parts.append(f'<{area}>'+"".join(rows)+f'</{area}>')
        # Media/inline descendants render recursively with their own IDs. These
        # structural wrappers are the only source nodes not rendered directly.
        skipped=[group]+list(root.findall(CN+"label"))+[
            e for e in group.iter() if local(e.tag) in {"thead","tbody","row","entry"}]
        assert all(not e.get("id") for e in skipped),"Table wrapper ID would be discarded"
        hint=("On a narrow screen, scroll sideways to see all five columns." if english else "చిన్న తెరపై ఐదు నిలువు వరుసలూ చూడటానికి పట్టికను అడ్డంగా జరపండి.") if count==5 else (f"Scroll sideways to see all {count} content columns." if english else f"చిన్న తెరపై {count} నిలువు వరుసలూ చూడటానికి పట్టికను అడ్డంగా జరపండి.")
        return f'<p class="scroll-hint">{hint}</p><div class="table-scroll" tabindex="0" role="region" aria-label="{esc(hint)}"><table{ident} aria-label="{esc(aria)}">'+"".join(parts)+"</table></div>"
    if tag=="newline":
        return f'<br{ident}/>'
    if tag=="label":
        assert not "".join(root.itertext()).strip() and not root.get("id")
        return ""
    content=esc(root.text or "")+"".join(render(c,assets,prefix,english,collapse_solutions)+esc(c.tail or "") for c in root)
    if tag=="solution" and collapse_solutions:
        label="Show the source-supplied answer" if english else "మూలంలో ఇచ్చిన జవాబును చూడండి"
        return f'<details{ident} class="cn-solution"><summary>{label}</summary>{content}</details>'
    if tag=="emphasis":
        effect=root.get("effect","bold")
        assert effect in {"bold","italics"},effect
        element="em" if effect=="italics" else "strong"
        return f'<{element}{ident}>{content}</{element}>'
    if tag=="list":
        kind=root.get("list-type","bulleted")
        assert kind in {"bulleted","enumerated","labeled-item"},kind
        element="ol" if kind=="enumerated" else "ul"
        # Circled labels are explicit source tokens; do not duplicate them.
        labeled=kind=="labeled-item" or root.get("class")=="circled"
        cls="cn-list labeled-list" if labeled else "cn-list"
        return f'<{element}{ident} class="{cls}">{content}</{element}>'
    mapping={"section":"section","title":"h3","para":"p","term":"dfn","figure":"figure","caption":"figcaption","example":"section","exercise":"section","problem":"div","solution":"div","note":"aside","list":"ul","item":"li","span":"span","equation":"div","glossary":"dl","meaning":"dd","document":"section","metadata":"section","abstract":"section"}
    assert tag in mapping,f"Unsupported CNXML element: {tag}"
    element=mapping[tag]
    if tag=="para" and any(local(c.tag) in {"media","table","figure","list","equation"} for c in root):
        element="div"  # HTML cannot nest a block-level diagram inside a <p>.
    return f'<{element}{ident} class="cn-{tag}">{content}</{element}>'


def validate_reader_link(link, current_ids):
    """Resolve local file fragments as well as same-page targets."""
    if link.startswith("#"):
        assert link[1:] in current_ids, link
    elif not re.match(r"https?://", link):
        filename, separator, fragment = link.partition("#")
        path = (BASE / "reader" / filename).resolve()
        assert path.is_relative_to(BASE.resolve()) and path.is_file(), link
        if separator:
            assert fragment and path.suffix == ".html", link
            other = HTMLCheck()
            other.feed(path.read_text(encoding="utf-8"))
            assert fragment in other.ids, link


def reader_title(target, catalog):
    """An untitled source stays untitled; navigation headings are disclosed."""
    title = target.findtext(CN + "title")
    if title:
        return title, ""
    title = catalog.get("editorial_title_te")
    english = catalog.get("editorial_title_en")
    assert isinstance(title, str) and re.search(r"[\u0c00-\u0c7f]", title), "Missing editorial Telugu title"
    assert isinstance(english, str) and re.search(r"[A-Za-z]", english), "Missing editorial English title"
    note = ('<p class="meta">మూల భాగానికి ప్రత్యేక శీర్షిక లేదు; పాఠాన్ని గుర్తించడానికి '
            'పైన సంపాదకీయ శీర్షిక ఇచ్చాం. <span lang="en">Editorial navigation title: '
            + html.escape(english) + '. The frozen source has no title.</span></p>')
    return title, note


def build(unit):
    assert shutil.disk_usage(BASE).free>=32*1024*1024,"Insufficient free space"
    source,meta,catalog=unit_inputs(unit)
    assets=asset_map(unit)
    target=localize(source,catalog,assets)
    assert structural_signature(source)==structural_signature(target),"Source structure changed"
    assert math_signature(source)==math_signature(target),"Source math changed"
    target_bytes=serialize(target)
    bridge=ET.parse(BASE/"translations"/(unit+".bridge.xhtml")).getroot()
    if unit=="TE-B002":
        validate_b002_bridge(bridge)
    elif unit=="TE-B003":
        validate_b003_bridge(bridge)
    elif unit=="TE-B004":
        validate_b004(target,bridge)
    elif unit=="TE-B005":
        validate_b005(target,bridge)
    elif unit=="TE-B006":
        validate_b006(target,bridge)
    elif unit=="TE-B007":
        validate_b007(target,bridge)
    elif unit=="TE-B008":
        validate_b008(target,bridge)
    elif unit in {"TE-B009","TE-B010"}:
        validate_auxiliary(unit,source,target,meta,catalog,bridge)
    elif unit in {"TE-B011","TE-B012"}:
        validate_readiness(unit,target,bridge)
    elif unit=="TE-B013":
        validate_b013(target,bridge)
    elif unit=="TE-B014":
        validate_b014(target,bridge)
    elif unit=="TE-B015":
        validate_b015(target,bridge)
    elif unit=="TE-B016":
        validate_b016(target,bridge)
    elif unit=="TE-B017":
        validate_application_target(target)
        validate_application_bridge(bridge,source)
    elif unit=="TE-B018":
        validate_b018(target,bridge)
    elif unit=="TE-B019":
        validate_b019(target,bridge)
    bridge_html=render_bridge(bridge)
    title,title_note=reader_title(target,catalog)
    previous=f'TE-B{int(unit[-3:])-1:03d}.html'
    context_note='<p>సేతువు గమనిక: మూలంలోని డబ్బు ఉదాహరణలో $ అంటే అమెరికా డాలర్. ఇక్కడ ఆ విలువలను రూపాయలుగా మార్చలేదు.</p>' if unit=="TE-B002" else ''
    scope_note=f"One complete subsection: {meta['module']}#{meta['section']}. Not a complete module or a validated grade-level assessment."
    image_note="Telugu diagrams are new code-native redraws; the English column retains original images. Corrected accessibility descriptions do not change the frozen source."
    if meta.get("selection"):
        scope_note=html.escape(meta["scope"])+" Source selection: "+html.escape(", ".join(meta["selection"]["selected_paths"]))+". Not a complete module or a validated grade-level assessment."
        image_note="This source selection has no images. Original source identifiers and structure are retained."
    if source.tag==CN+"note":
        scope_note=f"One complete readiness note: {meta['module']}#{meta['section']}. Not a complete module or a validated grade-level assessment."
    if not assets:
        image_note="This source selection has no images. Original source identifiers and structure are retained."
    if unit=="TE-B010":
        context_note='<p>ఇవి పాఠభాగపు ప్రారంభ లక్ష్యాలు. నేర్చుకోవడానికి ముందు ఈ జాబితాను చూడవచ్చు; B010 అనేది తయారీ క్రమంలో ఇచ్చిన గుర్తింపు మాత్రమే. <span lang="en">Module opening objectives; production numbering is not teaching order.</span></p>'
    source_url=f'https://github.com/openstax/osbooks-prealgebra-bundle/blob/{meta["source_commit"]}/modules/{meta["module"]}/index.cnxml'
    page=f'''<!doctype html><html lang="te-Telu-IN"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/><title>{html.escape(title)} · {unit}</title><link rel="stylesheet" href="../assets/reader.css"/></head><body>
<header><p class="meta">తెలుగు–English mastery bridge · {unit} · editorial draft</p><h1>{html.escape(title)}</h1>
<nav><a href="{previous}">ముందటి పాఠం / Previous</a><a href="#source-te">తెలుగు పాఠం</a><a href="#source-en">English source</a><a href="#attribution">మూలాలు / Credits</a></nav>
<p class="meta">{scope_note}</p>
{context_note}{title_note}</header>
<main><section id="source-te"><h2>మూలపాఠం అనువాదం · Telugu source translation</h2>{render(target,assets,collapse_solutions=unit in COLLAPSED_SOURCE_ANSWERS)}</section>
{bridge_html}<details id="source-en" class="english" lang="en"><summary>Read the parallel canonical English subsection</summary>{render(source,assets,'en-',True,collapse_solutions=unit in COLLAPSED_SOURCE_ANSWERS)}</details></main>
<footer id="attribution" lang="en"><p>Adapted from OpenStax <em>Prealgebra 2e</em>, Rice University. Senior contributing authors: Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis. <a href="{source_url}">Pinned canonical source</a>. Indonesian structural reference is identified in the source lock.</p>
<p>CC BY-NC-SA 4.0, subject to retained component notices. <a href="../ATTRIBUTION.md">Credits and change disclosure</a> · <a href="../notices/A00-LICENSE.txt">License</a> · <a href="../qa/{unit}.source-notes.md">Source corrections and limits</a>. {image_note} Supplemental explanations are original additions.</p>
<p>Prepared with OpenAI Codex assistance at the user's request; no author, state-government or OpenStax endorsement. AP terminology and fluent-Telugu review remain open. No telemetry, external scripts, remote fonts, learner-data storage or training export.</p></footer></body></html>'''
    check=HTMLCheck(); check.feed(page)
    assert len(check.ids)==len(set(check.ids)),"Duplicate reader IDs"
    for e in source.iter():
        if e.get("id"):
            assert e.get("id") in check.ids and "en-"+e.get("id") in check.ids
    for link in check.links:
        validate_reader_link(link,check.ids)
    for image in check.images:
        assert (BASE/"reader"/image).resolve().is_file(),image
    assert check.math==2*len(list(source.iter(MATH+"math")))+sum(local(e.tag)=="math" for e in bridge.iter())
    assert "\ufffd" not in page and "TODO" not in page
    if unit=="TE-B002":
        assert 3*100+7*10+4==374
        assert 100+30+8==138 and 200+10+5==215
        assert 100+70+6==176 and 200+30+7==237
        assert len(list(source.iter(CN+"table")))==2
        assert len(assets)==9
    output=page.encode("utf-8")
    receipt={"schema":"te-unit-qa-v2","unit":unit,"scope":meta["scope"],"source_sha256":meta["source_sha256"],"target_sha256":sha(target_bytes),"reader_sha256":sha(output),
             "source_elements":len(list(source.iter())),"source_ids":sum(bool(e.get("id")) for e in source.iter()),"math_expressions":len(list(source.iter(MATH+"math"))),"translated_slots":len(catalog["translations"]),"localized_images":len(assets),
             "checks":{"source_pin_and_hash":"PASS","structure_and_nesting":"PASS","math_tokens":"PASS; only registered mathematical prose may localize","prose_coverage":"PASS","ids_links_images":"PASS","source_tables":"PASS" if list(source.iter(CN+"table")) else "not applicable: no source tables","explicit_numeric_cases":"PASS" if unit in {"TE-B002","TE-B003","TE-B004","TE-B005","TE-B006","TE-B007","TE-B008","TE-B009","TE-B010","TE-B011","TE-B012","TE-B013","TE-B014","TE-B015","TE-B016","TE-B017","TE-B018","TE-B019"} else "pending unit-specific checks"},
             "limitations":["Editorial draft until separate content and visual review", "Not native-speaker approval", "Not entire-module translation", "Not whole-book schema validation"]}
    atomic_write(BASE/"generated"/(unit+".te.cnxml"),target_bytes)
    atomic_write(BASE/"reader"/(unit+".html"),output)
    atomic_write(BASE/"qa"/(unit+".build.json"),(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps(receipt,ensure_ascii=True,indent=2))
    return receipt


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unit")
    build(parser.parse_args().unit)
