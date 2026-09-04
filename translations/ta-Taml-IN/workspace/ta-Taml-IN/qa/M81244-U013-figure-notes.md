# M81244 U013 — source-faithful application/perimeter figures

Status: bounded figure authoring and code/font-metric QA passed on 2026-08-31. This is not native-speaker approval, browser/EPUB/PDF/assistive-technology validation, a learner-efficacy result, or completion of the full assignment. Only the three SVGs under `assets/u013/` and this note were authored for this task. The source CNXML, builders, readers, companions, shared styles/logs and PDFs were not changed.

## Source and target scope

The complete English and Indonesian `m81244#fs-id2197427` sections were read, including the three image-containing problem/solution contexts. All three original English JPEGs were individually viewed. The English source pixels control the geometry and printed labels; the Indonesian witness supports interpretation, but its first SVG is a localized redraw rather than a substitute pixel authority. No new source or canon download, general audit, browser operation or PDF operation was needed. Disk space was checked before authoring (4,343,316,480 bytes free on C:).

The English bundle is pinned at `38cae454e644abf9f0a623e876994553881597c9`. The Indonesian witness is the existing v0.2.7 / `3de9207f56f8b5c57c017abf973fb04e00d740f1` selection. Existing source attribution and license decisions remain binding; these are model-authored vector translations/redraws of the identified OpenStax figures, not new canonical examples.

| Original stem | Source media ID | Geometry and clockwise side order, starting at the indicated left side | Visible target text |
|---|---|---|---|
| CNX_BMath_Figure_01_02_002 | fs-id588598 | Six-sided patio; full-height left side first: 4, 9, 2, 3, 2, 6 feet | All six numbers followed by அடி |
| CNX_BMath_Figure_01_02_003 | fs-id2175999 | Eight-sided outline with middle-bottom notch; left side first: 4, 9, 4, 3, 2, 3, 2, 3 inches | Numbers only, exactly as printed in the source image |
| CNX_BMath_Figure_01_02_004 | fs-id1381557 | Eight-sided stepped outline; upper-left short vertical side first: 2, 12, 6, 4, 2, 4, 2, 4 inches | Numbers only, exactly as printed in the source image |

The actual source 002 prints the word “feet”, not “ft”. The original 003/004 pixels print no inch words or abbreviations; their problem paragraphs specify inches. Earlier coordination shorthand using ft/in was corrected before drafting. No SI conversion, unit substitution, new side label or perimeter answer was added to a figure.

## Pixel/alt discrepancies and decisions

1. The original 002 has a pale turquoise diagonal leader and arrowhead pointing toward the inner vertical two-foot edge. Its English and Indonesian prose alts omit that leader. The Tamil media alt describes the observed pointer, and the SVG preserves it; it does not introduce another number or an extra boundary side.
2. The Indonesian first image is `CNX_BMath_Figure_01_02_002.jpg.id-ID.svg`. Its complete SVG was read: it uses a 320×150 viewBox, an inner vertical at x=178 and a horizontal arrow, whereas the English JPEG is 304×138 with the inner vertical near x=185 and a diagonal arrow. The Tamil SVG follows the English outline and diagonal pointer, not that differing Indonesian layout.
3. For 003/004, both witnesses' alts describe the measurements as inches. The final Tamil descriptions explicitly separate bare visible numerals from the inches unit supplied in the question. The drawing itself therefore remains numeric-only.
4. Source solution totals are independently consistent: 4+9+2+3+2+6=26 feet; 4+9+4+3+2+3+2+3=30 inches; 2+12+6+4+2+4+2+4=36 inches. These are QA observations of supplied source solutions, not content added to titles, descriptions or graphic text. In particular, the two assessment diagrams do not disclose their supplied answers.
5. Source vertices were quantized to the original raster's visible edge coordinates, then placed inside a 24-unit margin with a uniform ×4 drawing transform. Each side is a native SVG path, not an embedded screenshot. Pixel length / labelled length ratios within each figure differ by less than 3%; the figures are not asserted to be exact-scale measurement tools.
6. Text anchors follow the source label locations with margins for Tamil. A first font-metric pass found the lower strokes of the inner “2 அடி” label overlapping the pointer shaft at its source-like baseline y=76. That label alone was raised to y=72. Side vertices and pointer coordinates were not moved. The corrected label now clears both outline and pointer. The initial check did not claim pointer clearance until the general segment/rectangle test was added and passed.
7. The pointer uses pale turquoise `#71e6d1`; the outlines/text are dark on white. Pointer color is supplementary: the desc identifies the target side. The source geometry, not color alone, carries the mathematical information.

## Actual canon consultation loop

The actual local OCR and complete readable page image for SCERT/Tamil Nadu Class 6 Term 1 Mathematics (first edition 2018), PDF page 46 / printed page 40, were consulted before drafting and during revision/QA. This focused extension uses the already-downloaded reference. It contains the fenced-garden/string-measurement use of சுற்றளவின், a separate பரப்பளவு example, and மைல்களைக். It directly supports the perimeter register and the distinction from area; it does not attest the exact foot/inch headwords.

Actual page-175 OCR was read during drafting and reread at revision/QA; its complete image had also been inspected in the immediately preceding addition-core work. Its glossary supports அளவீடு, அலகு முறை and vertical/horizontal/line-segment terminology. Existing terminology.tsv was checked rather than treated as a replacement for the readable canon.

The actual selected examples do **not** supply direct headword evidence for “foot” → அடி or “inch” → அங்குலம். These remain documented plain-language translation choices shared with the U013 translator, not fabricated canon quotations or native-speaker approval. Retaining the imperial values is a source-fidelity decision; the reference's conversion activity was not imported into this source strand. Parent coordination owns the shared canon consultation log; this note records the worker's actual reading and decisions.

## Accessibility and rendering contract

Each file has `role="img"`, `lang="ta-Taml-IN"`, matching `xml:lang`, and unique `aria-labelledby` references to its title and complete description. Each `desc` is an exact copy of the corresponding current Tamil media `alt`; the visible drawing group is `aria-hidden="true"`. IDs use distinct `u013-f002-`, `u013-f003-` and `u013-f004-` prefixes, so they do not collide when inlined together. Source-media IDs are retained as data attributes, not copied as global SVG IDs.

The SVGs contain only native vector/text elements. They have no raster image, script, foreignObject, event handler, network reference or external-resource dependency. The text font stack is the established `TamilBook, 'Nirmala UI', sans-serif`; the reader must supply its existing offline TamilBook font. These assets do not package their own separate font or alter shared CSS.

## Executed checks and limits

Normal PATH Python 3.12.10, Pillow 12.3.0, and the exact existing NotoSansTamil.ttf below were used. The read-only test reads the real files, not an in-memory authoring draft. It passed:

- 3 parseable SVGs, 54 globally unique IDs, 22 actual side paths and 22 actual labels.
- Exact expected side order, path vertices, label text, label-to-side association and imperial unit data; closed axis-aligned simple outlines with the source clockwise ordering.
- The original two/three-unit notch and step arrangements, not merely equality of total perimeters.
- Exact desc/current-media-alt equality, two valid title/desc references per image, Tamil language metadata, source-media identity and local-only allowed elements/attributes.
- Perimeters 26/30/36 from actual side data, with none of those answer totals in graphic title/desc/visible text.
- Every label's measured font box inside the viewBox; no label/label overlap, no label/outline collision including half-stroke clearance, and no label/pointer collision including pointer half-stroke clearance.
- 16 in-memory negative fixtures rejected: for each image, swap two distinct labels while preserving their sum, remove a side, change a unit to metre, inject an event handler, or drift a label anchor; plus send the patio pointer to the wrong side.

The three **original source raster images** and the relevant canon page were visually inspected. The newly authored SVGs were checked structurally and with actual-font metrics, but were **not** browser-rendered or screen-reader tested by this worker. Font metrics do not establish actual browser shaping, responsive legibility, keyboard scrolling, print pagination, EPUB reader behavior, or assistive-technology announcement quality. Those integration checks remain parent-owned and pending here.

## Exact checked identities

The translator confirmed final U013 source SHA `8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb` and no alt changes after the three descriptions were copied. The actual embedded checker was extracted from this note and executed successfully against that source and all three SVGs. If a future revision changes an alt, rerun the checker and resynchronize the affected desc; a prose-only source change still needs an updated identity record.

| Authored SVG | Bytes | SHA-256 |
|---|---:|---|
| CNX_BMath_Figure_01_02_002.svg | 3,245 | `9e7ba0e663a9fac7d3d801b8c14e9572a31482c872f521d7ca9ddde44671e249` |
| CNX_BMath_Figure_01_02_003.svg | 3,349 | `15c5db825e70164c99083bd70dbd184ada8d805fe9cc3f94ccae44d20022c67d` |
| CNX_BMath_Figure_01_02_004.svg | 3,454 | `fe97fdf9a9d0fc68890f683d4a0454829fa1165b375aed8d294d159b170fa911` |

| Checked input | Bytes | SHA-256 |
|---|---:|---|
| downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81244/index.cnxml | 119,141 | `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b` |
| downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml | 123,306 | `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6` |
| ta-Taml-IN/translation/m81244-fs-id2197427.cnxml | 16,980 | `8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb` |
| ta-Taml-IN/assets/fonts/NotoSansTamil.ttf | 340,668 | `aa3a9b321f4b0bb2c40203ffbde9af89713227866e0e13f76e5b9eeea727cf88` |
| downloads/tamil-canon/ocr/page-046.txt | 3,565 | `b7955cfbf49c5321874771aa26755d1e4ecfad0031ada9ed034d479bfdefda89` |
| downloads/tamil-canon/ocr/page-046.png | 347,230 | `c208f8b59c7a2747171152f4e53198c48aae52858a24f76880cd9f024cdfb229` |
| downloads/tamil-canon/ocr/page-175.txt | 5,569 | `17546f2815c3077bf5fc2d90d1fca376b6aa4a83fd664e01907b3e5969b2d999` |
| downloads/tamil-canon/ocr/page-175.png | 571,667 | `a4790fc94ecf2b3b4af3bab80f383e5383ef60e9e65ff8f72df8bc4d49437679` |
| downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_BMath_Figure_01_02_002.jpg | 32,643 | `aaced737e0448c122d0c5df06df1fa0cb401c19630f0840973fb1f65b6edbd28` |
| downloads/openstax-prealgebra-2e-id-ID/media/CNX_BMath_Figure_01_02_002.jpg.id-ID.svg | 1,345 | `3ac8ea1250b92b521477d90aeecad130ac8494d43de804fd1a6d6e0bbea864e8` |
| downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_BMath_Figure_01_02_003.jpg | 24,976 | `a2f3145a692006fe3af33dcb894b00bc03bfcc18370fab367f2bd9316d646137` |
| downloads/openstax-prealgebra-2e-id-ID/media/CNX_BMath_Figure_01_02_003.jpg | 24,976 | `a2f3145a692006fe3af33dcb894b00bc03bfcc18370fab367f2bd9316d646137` |
| downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/CNX_BMath_Figure_01_02_004.jpg | 24,911 | `ac6856ba7f2d69c05a1a7396c339ece3c6ce6a0d5af3174888b41e9050188ef8` |
| downloads/openstax-prealgebra-2e-id-ID/media/CNX_BMath_Figure_01_02_004.jpg | 24,911 | `ac6856ba7f2d69c05a1a7396c339ece3c6ce6a0d5af3174888b41e9050188ef8` |

## Reproducible read-only checker

Run the following Python block from the repository root with Python UTF-8 mode. It creates no files. One PowerShell way to execute this exact embedded block is:

```powershell
@'
from pathlib import Path
note = Path("ta-Taml-IN/qa/M81244-U013-figure-notes.md").read_text(encoding="utf-8")
check = note.split("\x60\x60\x60python\n", 1)[1].split("\n\x60\x60\x60", 1)[0]
exec(compile(check, "U013-figure-check", "exec"))
'@ | python -X utf8 -
```

```python
import copy, hashlib, json, math, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import ImageFont, __version__ as pillow_version

BASE = Path("ta-Taml-IN")
EN = Path("downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9")
ID = Path("downloads/openstax-prealgebra-2e-id-ID")
TA = BASE / "translation/m81244-fs-id2197427.cnxml"
S = "{http://www.w3.org/2000/svg}"
FONT = BASE / "assets/fonts/NotoSansTamil.ttf"
font = ImageFont.truetype(str(FONT), 72)
EXPECTED = {
 "002": ("fs-id588598", [4,9,2,3,2,6], "foot", [(52,112),(52,23),(251,23),(251,68),(185,68),(185,112)], [(22,72),(152,14),(282,49),(215,89),(153,72),(119,134)], (1264,600), 26),
 "003": ("fs-id2175999", [4,9,4,3,2,3,2,3], "inch", [(15,109),(15,20),(214,20),(214,109),(148,109),(148,64),(81,64),(81,109)], [(5,68),(115,14),(224,68),(181,126),(159,92),(115,82),(71,92),(48,126)], (964,568), 30),
 "004": ("fs-id1381557", [2,12,6,4,2,4,2,4], "inch", [(14,53),(14,20),(213,20),(213,119),(147,119),(147,86),(80,86),(80,53)], [(5,40),(114,14),(224,100),(180,137),(156,108),(114,104),(91,73),(47,70)], (960,612), 36),
}
alts = {e.get("id"):e.get("alt") for e in ET.parse(TA).iter() if e.tag.endswith("}media")}
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def fail_mutation(root, suffix, change):
    clone = copy.deepcopy(root)
    change(clone)
    try:
        check(clone, suffix)
    except AssertionError:
        return
    raise AssertionError("negative fixture not rejected")
def bbox_line(box, a, b):
    l,t,r,bot=box
    if a[0] == b[0]:
        return l <= a[0] <= r and max(t,min(a[1],b[1])) <= min(bot,max(a[1],b[1]))
    assert a[1] == b[1]
    return t <= a[1] <= bot and max(l,min(a[0],b[0])) <= min(r,max(a[0],b[0]))
def segment_box(box,a,b):
    lo,hi=0.0,1.0
    for axis in (0,1):
        delta=b[axis]-a[axis]
        mn,mx=box[axis],box[axis+2]
        if delta==0:
            if not mn<=a[axis]<=mx:
                return False
            continue
        p,q=(mn-a[axis])/delta,(mx-a[axis])/delta
        lo,hi=max(lo,min(p,q)),min(hi,max(p,q))
        if lo>hi:
            return False
    return True
def segments_meet(a,b,c,d):
    box = (min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
    return bbox_line(box,c,d)
def check(root,suffix):
    media,values,unit,verts,anchors,size,total=EXPECTED[suffix]
    prefix="u013-f"+suffix+"-"
    elements=list(root.iter())
    allowed={"svg","title","desc","rect","g","path","text"}
    assert all(e.tag.startswith(S) and e.tag[len(S):] in allowed for e in elements)
    assert all(not k.split("}")[-1].lower().startswith("on") and k.split("}")[-1] not in {"href","src"} and "url(" not in v for e in elements for k,v in e.attrib.items())
    ids=[e.get("id") for e in elements if e.get("id")]
    assert len(ids)==len(set(ids)) and all(i.startswith(prefix) for i in ids)
    assert root.get("role")=="img" and root.get("lang")=="ta-Taml-IN"
    assert root.get("{http://www.w3.org/XML/1998/namespace}lang")=="ta-Taml-IN"
    assert root.get("data-source-media")==media
    assert root.get("aria-labelledby").split()==[prefix+"title",prefix+"desc"]
    assert root.find(S+"title").get("id")==prefix+"title"
    assert root.find(S+"desc").get("id")==prefix+"desc"
    assert root.find(S+"desc").text==alts[media]
    assert list(map(float,root.get("viewBox").split()))==[0,0,*size]
    drawing=next(e for e in elements if e.get("id")==prefix+"drawing")
    assert drawing.get("transform")=="translate(24 24) scale(4)"
    assert drawing.get("aria-hidden")=="true" and drawing.get("font-weight")=="400"
    edges=root.findall(".//"+S+"path[@data-side]")
    labels=root.findall(".//"+S+"text")
    assert len(edges)==len(labels)==len(values)
    ratios=[]
    for i,(edge,label,value,a,b,anchor) in enumerate(zip(edges,labels,values,verts,verts[1:]+verts[:1],anchors),1):
        assert edge.get("id")==prefix+"side-"+str(i) and edge.get("data-side")==str(i)
        assert edge.get("data-length")==str(value) and edge.get("data-unit")==unit
        assert edge.get("d")==f"M{a[0]} {a[1]} L{b[0]} {b[1]}"
        assert (a[0]==b[0]) != (a[1]==b[1])
        ratios.append((abs(b[0]-a[0])+abs(b[1]-a[1]))/value)
        assert label.get("id")==prefix+"label-"+str(i) and label.get("data-side")==str(i)
        assert (float(label.get("x")),float(label.get("y")))==anchor
        assert label.text==str(value)+(" அடி" if unit=="foot" else "")
    assert max(ratios)/min(ratios) < 1.03
    # Each actual geometry edge must meet its next, and non-adjacent edges must not cross.
    for i,(a,b) in enumerate(zip(verts,verts[1:]+verts[:1])):
        for j,(c,d) in enumerate(zip(verts,verts[1:]+verts[:1])):
            if j<=i or j==i+1 or (i==0 and j==len(verts)-1):
                continue
            assert not segments_meet(a,b,c,d)
    assert sum(verts[i][0]*verts[(i+1)%len(verts)][1]-verts[(i+1)%len(verts)][0]*verts[i][1] for i in range(len(verts)))>0
    assert sum(int(e.get("data-length")) for e in edges)==total
    boxes=[]
    for label in labels:
        x,y=float(label.get("x"))*4+24,float(label.get("y"))*4+24
        l,t,r,b=font.getbbox(label.text,anchor="ms")
        box=(x+l,y+t,x+r,y+b)
        assert box[0]>=0 and box[1]>=0 and box[2]<=size[0] and box[3]<=size[1], (suffix,label.text,box)
        for other in boxes:
            assert min(box[2],other[2])<=max(box[0],other[0]) or min(box[3],other[3])<=max(box[1],other[1])
        # Expand text by half the outline stroke (0.8 source px = 3.2 SVG px).
        expanded=(box[0]-1.6,box[1]-1.6,box[2]+1.6,box[3]+1.6)
        for a,b in zip(verts,verts[1:]+verts[:1]):
            assert not bbox_line(expanded,tuple(z*4+24 for z in a),tuple(z*4+24 for z in b)), (suffix,label.text,"text/outline")
        boxes.append(box)
    pointers=root.findall(".//"+S+"path[@data-target-side]")
    assert len(pointers)==(1 if suffix=="002" else 0)
    if pointers:
        p=pointers[0]
        assert p.get("data-target-side")=="5"
        assert p.get("d")=="M162 81 L176 87 M174 83 L183 90 L172 89 Z"
        assert p.get("fill")==p.get("stroke")=="#71e6d1"
        assert abs(183-verts[4][0])<=2 and verts[4][1]<90<verts[5][1]
        for a,b in [((162,81),(176,87)),((174,83),(183,90)),((183,90),(172,89)),((172,89),(174,83))]:
            for box in boxes:
                expanded=(box[0]-1.2,box[1]-1.2,box[2]+1.2,box[3]+1.2)
                assert not segment_box(expanded,tuple(z*4+24 for z in a),tuple(z*4+24 for z in b)), "text/pointer"
    assert len(root.findall(".//"+S+"path"))==len(edges)+len(pointers)
    assert not re.search(r"\b(?:26|30|36)\b"," ".join(e.text or "" for e in [root.find(S+"title"),root.find(S+"desc"),*labels]))
    return ids, boxes

all_ids=[]; output=[]; negative=0
for suffix,cfg in EXPECTED.items():
    p=BASE / f"assets/u013/CNX_BMath_Figure_01_02_{suffix}.svg"
    root=ET.parse(p).getroot()
    ids,boxes=check(root,suffix)
    all_ids+=ids
    def swapped(c):
        a,b=c.findall(".//"+S+"text")[:2]
        a.text,b.text=b.text,a.text
    fail_mutation(root,suffix,swapped)
    def removed(c):
        g=next(e for e in c.iter() if e.find(S+"path[@data-side]") is not None)
        g.remove(g.find(S+"path[@data-side]"))
    fail_mutation(root,suffix,removed)
    fail_mutation(root,suffix,lambda c:c.find(".//"+S+"path[@data-side]").set("data-unit","metre"))
    fail_mutation(root,suffix,lambda c:c.set("onclick","alert(1)"))
    fail_mutation(root,suffix,lambda c:c.find(".//"+S+"text").set("y","23"))
    negative+=5
    if suffix=="002":
        fail_mutation(root,suffix,lambda c:c.find(".//"+S+"path[@data-target-side]").set("data-target-side","3"))
        negative+=1
    output.append({"file":str(p),"sha256":sha(p),"bytes":p.stat().st_size,"sides":len(cfg[1]),"labels":len(boxes),"perimeter":cfg[-1],"unit":cfg[2],"ids":len(ids)})
assert len(all_ids)==len(set(all_ids))
inputs=[]
for p in [EN/"modules/m81244/index.cnxml",ID/"modules/m81244/index.cnxml",TA,FONT,
          Path("downloads/tamil-canon/ocr/page-046.txt"),Path("downloads/tamil-canon/ocr/page-046.png"),
          Path("downloads/tamil-canon/ocr/page-175.txt"),Path("downloads/tamil-canon/ocr/page-175.png")]:
    inputs.append({"file":str(p),"sha256":sha(p),"bytes":p.stat().st_size})
for suffix in EXPECTED:
    p=EN/f"media/CNX_BMath_Figure_01_02_{suffix}.jpg"
    q=ID/f"media/CNX_BMath_Figure_01_02_{suffix}.jpg"
    inputs.append({"file":str(p),"sha256":sha(p),"bytes":p.stat().st_size})
    if suffix!="002":
        assert p.read_bytes()==q.read_bytes()
    else:
        q=ID/"media/CNX_BMath_Figure_01_02_002.jpg.id-ID.svg"
    inputs.append({"file":str(q),"sha256":sha(q),"bytes":q.stat().st_size})
print(json.dumps({"status":"pass","python":sys.version.split()[0],"pillow":pillow_version,"svg_count":3,"side_count":22,"label_count":22,"unique_ids":len(all_ids),"negative_fixtures_rejected":negative,"outputs":output,"inputs":inputs},ensure_ascii=False,indent=2))
```
