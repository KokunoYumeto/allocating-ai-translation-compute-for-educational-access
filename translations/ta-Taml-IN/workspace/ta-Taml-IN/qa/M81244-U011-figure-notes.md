# M81244 U011 figure redraw notes

Date: 2026-08-31. Bounded scope: the five media in `m81244#fs-id1385496` (“Add Whole Numbers Without Models”). These SVGs preserve the source's models and column-addition stages. They are not a new recovery companion or a complete learner workflow.

## Ownership and current status

Authored only `assets/u011/*.svg` and this note. No source/translation/companion, shared CSS/builders/logs, delivered reader, EPUB or PDF was edited. Source-pixel inspection, arithmetic/count/column checks and local font-metric checks pass. Actual SVG rendering, reader integration, browser/EPUB/PDF/AT and native Tamil review are not claimed and remain pending/root-owned.

The five final paths were coordinated directly with root and the source translator. Original filename stems were retained. There was no new acquisition, audit, raster generation, PDF operation or commit. Disk free was 4,816,506,880 bytes at U011 start and 4,728,762,368 bytes at revision; these five SVGs total 24,517 bytes.

## Witnesses and translation snapshot

- English source: `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81244/index.cnxml`, pinned commit `38cae454e644abf9f0a623e876994553881597c9`, module SHA-256 `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b`.
- Indonesian source: `downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml`, selected v0.2.7 / commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`, module SHA-256 `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6`.
- Final checked translation: `translation/m81244-fs-id1385496.cnxml`, SHA-256 `dd3d4e473f5468cff9737a01d3968f60b0dd5102fb791fff529eab43ec0ddaff`, 57,548 bytes. The translator confirmed this final identity and that all five alts remained unchanged. Initial desc extraction used dcbdb15aadea49ce225b16a863d80ff545037f8a03f390554681387e938062e0; intermediate checks at 032c62af2887bdb2e8b0c71ba1ca3d0377845409407dcee7b76edd2409b937bc and the final hash above passed. The rerunnable code was extracted from this actual Markdown note and executed against the final source; all checks and desc/@alt equality passed.
- Read the full section text from both witnesses and all five actual source images. A first overlong XML dump was truncated; a subsequent complete compact text traversal supplied the entire subsection. All five English/Indonesian image pairs are byte-identical. This figure task checks the mathematics depicted in these five images, not every other source exercise.

## Actual canon consultation

Drafting used actual `downloads/tamil-canon/ocr/page-020.txt` (C05/C06, PDF p20 / printed p14) and viewed its complete existing PNG. The page directly attests இடமதிப்பு, ஒன்றுகள் இடம் and aligning a digit's named place; its image resolves the OCR's corrupted digits/operators. These reference numerals were not imported into the source figures.

The just-consulted complete page-036 OCR/PNG (C11) supplied கூட்டல் / சமன்பாடு / மொத்தம் and count-preserving model register. Revision/QA reread the actual page-020 and page-036 OCR and the relevant existing terminology entries, rather than relying on a ledger-only citation. The p175 glossary's கிடைமட்ட பட்டைகள் was consulted during the immediately preceding U010 work and informs the existing ledger; it is not falsely counted as a new U011 carry-term attestation.

The translator's descriptions retain ஒன்றுகள் கட்டங்கள், பத்துகள் பட்டைகள் and கொண்டு செல்லப்பட்ட சிறிய 1. The first two are established provisional compounds; no exact canon attestation or native approval is claimed for a carry/regrouping technical term. The image titles use the attested operation/place register: கூட்டல், ஒன்றுகள், பத்துகள், நூறுகள். No graphic-language prose required translation because the originals show numeric labels only; Tamil titles/descriptions supply accessible context.

## Canonical media order and exact mapping

All filenames have prefix `CNX_BMath_Figure_01_02_`; targets are `assets/u011/<full-stem>.svg`. Source 001 is JPG; 020-01/02/03/04 are PNG.

| Order | Suffix | Media ID | Pixel-checked representation |
|---|---|---|---|
| 1 | 001 | fs-id1231518 | Left 17 = 1 ten + 7 ones; left 26 = 2 tens + 6 ones. Right 43 = 4 tens + 3 ones. Boxed 1 + 1 + 2 = 4; right vertical 17 + 26 = 43 with small red 1 above the tens column. |
| 2 | 020-01 | eip-id1168289818410 | 324 above +586 and sum rule. No carry or result digits yet. |
| 3 | 020-02 | eip-id1168287268641 | Same addends; small carry 1 above the 2 (tens); result 0 in ones only. |
| 4 | 020-03 | eip-id1168287196613 | Same addends; small carry 1 above 3 (hundreds) and above 2 (tens); partial result 10. |
| 5 | 020-04 | eip-id1168287121476 | Same addends and two small carry marks; completed result 910. |

For 001, the seven ones belonging to 17 are arranged 2+5; the six belonging to 26 are arranged 5+1; the final three ones form one top row. Left rods occupy rows 35, 82 and 105 in source-coordinate units; right rods occupy 35, 58, 81 and 105. The central separator and rightward exchange arrow separate the two equivalent states. There are 86 drawn unit rectangles across both states, not a represented sum of 86.

The 020 sequence is deliberately incomplete until its fourth image. No 910 answer is added to the first three stages. Carry digits are small, above their target columns, with no fraction bars. The underlying instructional table remains semantic source structure; it is not rasterized into these individual diagrams.

## Source-alt/pixel discrepancies

- EN 020-03/04 call the marks “fractions 1/3 and 1/2.” Actual pixels show the ordinary addend 324 with small carry 1s above 3 and 2; there are no fraction bars. The Indonesian witness correctly describes carry marks. The Tamil alts and SVGs follow the pixels and ID witness.
- The source 001 alts omit the visible boxed 1 + 1 + 2 = 4, horizontal exchange arrow, diagonal pointer and small red carry 1. The Tamil alt describes all of them. Its wording also describes the actual vertical 17 / +26 / 43 arrangement, rather than treating the source alt's equation paraphrase as a literal horizontal label.
- 020-02's descriptive 4 + 6 = 10 explains the depicted transition. The original image does not visibly print that horizontal equation; the SVG does not add it.
- The original pale model fill and turquoise arrows were redrawn with a pale-blue/dark-outline block palette and darker teal arrows. The small red carry in 001 stays red. These are visible contrast/style changes, not mathematical changes.

## Design and checks

Every SVG has `u011-f<suffix>-` IDs, role=img, Tamil lang/xml:lang, title + desc referenced by aria-labelledby, and the source media ID in data-source-media. Each desc equals the corresponding current Tamil media/@alt exactly. The drawing subtree is aria-hidden; the complete description carries the logical reading. Reader integration must preserve a usable alternative and avoid duplicating IDs if an asset is inserted twice.

Geometry uses `translate(24 24) scale(4)`; viewBoxes equal source canvas dimensions times four plus 48. Original relative layout and stage order are preserved with added external padding. Digits are separate vector text nodes with explicit row/place metadata, not fractions or positional superscript tokens. Source rectangles, rule lines, separator and arrows are native SVG, with no embedded bitmap/font, script, foreignObject, href or network resource.

Verified:

- Five well-formed SVGs; 172 globally unique IDs within this set; all accessible-name targets resolve.
- 86 actual unit rectangles in 001, including seven rods of ten contiguous cells. Components are exactly (1 ten,7 ones), (2 tens,6 ones), (4 tens,3 ones). Group totals and source row geometry were independently checked.
- 51 visible text nodes across the five files. Source arithmetic is exact: 7+6=13; 1+1+2=4; 17+26=43; 4+6=10; 1+2+8=11; 1+3+5=9; 324+586=910.
- Column alignment checked by actual text x-coordinates; first/second/result digits share their named place, carries lie above those columns, and the only 020 path is the correct sum rule below the second addend. Intermediate result/carry sets match the four source stages.
- All unit-cell bounds (with stroke margin) are inside their padded viewBox. All 51 text bounds were measured with Pillow using the actual local NotoSansTamil.ttf at scaled declared sizes: no viewBox clipping, text/unit overlap or text/text overlap. The boxed equation also fits inside its box. This is a geometry/font-metric check, not an SVG/browser render.
- All five source-image pairs are byte-identical and all five final description strings match.
- Nine in-memory negative fixtures rejected: four wrong-place carry mutations, four invented fraction-bar paths, and one removed actual model cell. Fixtures never altered any file.
- An early draft ID collision between a model-group name and a digit name was caught by the global ID check and corrected to distinct model-group IDs before these final checks/hashes.

No unseen page, actual SVG render or AT interaction is reported as passed. Small-phone readability, scaling, focus/panning and screen-reader behavior require integration review. No native-speaker, board-alignment, grade-placement or educational-efficacy approval is claimed.

## Exact image and output hashes

Source image hashes below apply identically to the EN and ID witnesses.

| Suffix | Source image SHA-256 | SVG SHA-256 |
|---|---|---|
| 001 | `7cedd9c42784d4cccdc101879364b3ed30ac082030079d420862a1d2451d4876` | `49a1e4b853feff76027afddd534703eaa7d095a4e4ab5f3e63e41e809bf64615` |
| 020-01 | `85ae456c3b28cbe11cf193c48daecf7bbfc82b41f21757498a3a3dc3d2b85c23` | `050eb554730a493db0aa131fbaf912f88dc46978ba331276f5c5d0c32d7bb437` |
| 020-02 | `059f2bca323b8cfa28127a182b74806dde32a8d61a22699d08d3efc85d55b247` | `052440f57da0a1ac242acfa573253f070a5ed5d7e7da1ea2800ef99cb735a3d7` |
| 020-03 | `5bdb22c2893abc46ab172d8ace24519813191b091767986f4545a6e30c778614` | `efacbf07d122eccc74f27b4df9b4f0554c91e26d0563b4da5dda59cc53d8e8c0` |
| 020-04 | `7fa3e376086a57ab464e73c00c6130c5a0fd34bd3759d367823cc9b7290ef7a2` | `de7d24d110f98a79fb8cd192c4284c7647489b43d7a9ce2b5cb6a23b4f4919e0` |

## Rerunnable core QA

Run this read-only Python from the repository root with the normal PATH Python (Pillow is installed). It validates current file content rather than a stored receipt; later source changes must be rechecked. It does not certify a reader build or actual rendering.

```python
import sys,json,hashlib
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from xml.etree import ElementTree as E
from copy import deepcopy
from PIL import ImageFont,Image
base=Path("ta-Taml-IN")
ns={"c":"http://cnx.rice.edu/cnxml","s":"http://www.w3.org/2000/svg"}
en=Path("downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81244/index.cnxml")
ind=Path("downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml")
tp=base/"translation/m81244-fs-id1385496.cnxml"
tm=E.parse(tp).getroot().findall(".//c:media",ns)
sm=E.parse(en).getroot().find(".//c:section[@id='fs-id1385496']",ns).findall(".//c:media",ns)
im=E.parse(ind).getroot().find(".//c:section[@id='fs-id1385496']",ns).findall(".//c:media",ns)
expected=[
 {"first":{"tens":"1","ones":"7"},"second":{"tens":"2","ones":"6"},"result":{"tens":"4","ones":"3"},"carry":{"tens":"1"}},
 {"first":{"hundreds":"3","tens":"2","ones":"4"},"second":{"hundreds":"5","tens":"8","ones":"6"},"result":{},"carry":{}},
 {"first":{"hundreds":"3","tens":"2","ones":"4"},"second":{"hundreds":"5","tens":"8","ones":"6"},"result":{"ones":"0"},"carry":{"tens":"1"}},
 {"first":{"hundreds":"3","tens":"2","ones":"4"},"second":{"hundreds":"5","tens":"8","ones":"6"},"result":{"tens":"1","ones":"0"},"carry":{"hundreds":"1","tens":"1"}},
 {"first":{"hundreds":"3","tens":"2","ones":"4"},"second":{"hundreds":"5","tens":"8","ones":"6"},"result":{"hundreds":"9","tens":"1","ones":"0"},"carry":{"hundreds":"1","tens":"1"}}]
def column_check(r,i):
 actual={row:{} for row in ["first","second","result","carry"]}
 coord={}
 for t in r.findall(".//s:text[@data-row]",ns):
  row,place=t.get("data-row"),t.get("data-place")
  assert place not in actual[row]
  actual[row][place]=t.text
  coord[row,place]=(float(t.get("x")),float(t.get("y")))
 assert actual==expected[i]
 if i:
  rules=r.findall(".//s:path",ns)
  assert len(rules)==1 and rules[0].get("data-kind")=="sum-rule"
  assert rules[0].get("d")=="M1 "+("44" if i==1 else "53")+" H72"
 for (row,place),(x,y) in coord.items():
  assert x==coord["first",place][0]
  if row=="carry":assert y<coord["first",place][1]
 order=["hundreds","tens","ones"]
 xs=[coord["first",p][0] for p in order if ("first",p) in coord]
 assert xs==sorted(xs)
 for rule in r.findall(".//s:path[@data-kind='sum-rule']",ns):
  if i:
   y=float(rule.get("d").split()[1]); assert max(v[1] for k,v in coord.items() if k[0]=="second")<y
   if actual["result"]:assert min(v[1] for k,v in coord.items() if k[0]=="result")>y
def model_check(r):
 models={}; components={}; row_counts={}; rod_rows={}
 for g in r.findall(".//s:g[@data-model]",ns):
  units=g.findall("s:rect[@data-unit='1']",ns)
  kind=g.get("data-kind"); assert len(units)==int(g.get("data-count"))*(10 if kind=="tens" else 1)
  model=g.get("data-model")
  models[model]=models.get(model,0)+len(units)
  pair=components.setdefault(model,[0,0]);pair[0 if kind=="tens" else 1]+=1 if kind=="tens" else len(units)
  if kind=="ones":
   by_y={}
   for u in units:by_y[float(u.get("y"))]=by_y.get(float(u.get("y")),0)+1
   row_counts[model]=sorted(by_y.items())
  else:rod_rows.setdefault(model,[]).append(float(units[0].get("y")))
  assert all((float(u.get("x"))>353 if model=="result" else float(u.get("x"))+float(u.get("width"))<353) for u in units)
  if kind=="tens":
   assert len(units)==10 and len({u.get("y") for u in units})==1
   for a,b in zip(units,units[1:]):assert float(a.get("x"))+float(a.get("width"))==float(b.get("x"))
 assert models=={"first-addend":17,"second-addend":26,"result":43}
 assert components=={"first-addend":[1,7],"second-addend":[2,6],"result":[4,3]}
 assert row_counts=={"first-addend":[(35,2),(58,5)],"second-addend":[(105,5),(128,1)],"result":[(35,3)]}
 assert rod_rows=={"first-addend":[35],"second-addend":[82,105],"result":[35,58,81,105]}
ids=set();labels=0;units_n=0;rows=[];carry_fixtures=0;fraction_fixtures=0
assert len(tm)==len(sm)==len(im)==5
for i,(m,e,d) in enumerate(zip(tm,sm,im)):
 stem=Path(m.find("c:image",ns).get("src")).stem
 p=base/"assets/u011"/(stem+".svg");r=E.parse(p).getroot()
 assert r.find("s:desc",ns).text==m.get("alt")
 assert r.get("data-source-media")==m.get("id")==e.get("id")==d.get("id")
 sp=en.parent/e.find("c:image",ns).get("src");dp=ind.parent/d.find("c:image",ns).get("src")
 assert sp.read_bytes()==dp.read_bytes()
 own=[x.get("id") for x in r.iter() if x.get("id")]
 assert len(own)==len(set(own)) and ids.isdisjoint(own);ids.update(own)
 assert set(r.get("aria-labelledby").split())<=set(own)
 assert r.get("role")=="img" and r.get("lang")=="ta-Taml-IN"
 for x in r.iter():
  assert x.tag.rsplit("}",1)[-1] in {"svg","title","desc","rect","g","path","text"}
  assert not any(k.rsplit("}",1)[-1].lower().startswith("on") or k.rsplit("}",1)[-1]=="href" for k in x.attrib)
 column_check(r,i)
 if i:
  bad=deepcopy(r);E.SubElement(bad,"{http://www.w3.org/2000/svg}path",{"d":"M33 12 H39","data-kind":"fraction-bar"})
  try:column_check(bad,i)
  except AssertionError:fraction_fixtures+=1
  else:raise AssertionError("invented fraction bar accepted")
 carry=r.find(".//s:text[@data-row='carry']",ns)
 if carry is not None:
  bad=deepcopy(r);bad.find(".//s:text[@data-row='carry']",ns).set("data-place","ones")
  try:column_check(bad,i)
  except AssertionError:carry_fixtures+=1
  else:raise AssertionError("wrong-place carry accepted")
 w,h=map(float,r.get("viewBox").split()[2:])
 assert (w,h)==tuple(x*4+48 for x in Image.open(sp).size)
 boxes=[]
 units=r.findall(".//s:rect[@data-unit='1']",ns);units_n+=len(units)
 for u in units:
  x,y,bw,bh=(float(u.get(k)) for k in ["x","y","width","height"])
  b=(24+4*x,24+4*y,24+4*(x+bw),24+4*(y+bh));boxes.append(b)
  assert 0<=b[0]-4 and 0<=b[1]-4 and b[2]+4<=w and b[3]+4<=h
 texts=[]
 for t in r.findall(".//s:text",ns):
  labels+=1
  font=ImageFont.truetype(str(base/"assets/fonts/NotoSansTamil.ttf"),round(float(t.get("font-size"))*4))
  x,y=24+4*float(t.get("x")),24+4*float(t.get("y"))
  a,b,c,d=font.getbbox(t.text,anchor="ms");box=(x+a,y+b,x+c,y+d)
  assert min(box[:2])>=0 and box[2]<=w and box[3]<=h,(stem,t.text,"clipping",box)
  overlap=lambda q:box[0]<q[2] and box[2]>q[0] and box[1]<q[3] and box[3]>q[1]
  assert not any(overlap(q) for q in boxes),(stem,t.text,"cell overlap")
  assert not any(overlap(q) for q in texts),(stem,t.text,"text overlap")
  texts.append(box)
  if t.get("id")=="u011-f001-tens-equation":
   q=r.find(".//s:rect[@data-kind='equation-box']",ns)
   bx,by,bw,bh=(float(q.get(k)) for k in ["x","y","width","height"])
   assert box[0]>24+4*bx and box[2]<24+4*(bx+bw) and box[1]>24+4*by and box[3]<24+4*(by+bh)
 if i==0:
  model_check(r)
  bad=deepcopy(r);g=bad.find(".//s:g[@data-model]",ns);g.remove(g.find("s:rect",ns))
  try:model_check(bad)
  except AssertionError:pass
  else:raise AssertionError("removed model cell accepted")
  assert r.find(".//s:text[@id='u011-f001-tens-equation']",ns).text=="1 + 1 + 2 = 4"
  assert 17+26==43 and 7+6==13 and 1+1+2==4
  assert r.find(".//s:text[@data-row='carry']",ns).get("fill")=="#b34329"
  assert len(r.findall(".//s:path[@data-kind='exchange-arrow']",ns))==1
  assert len(r.findall(".//s:path[@data-kind='carry-pointer']",ns))==1
 else:assert not units
 rows.append({"stem":stem,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size})
assert 4+6==10 and 1+2+8==11 and 1+3+5==9 and 324+586==910
assert units_n==86 and carry_fixtures==4 and fraction_fixtures==4
print(json.dumps({"status":"PASS","translation_sha":hashlib.sha256(tp.read_bytes()).hexdigest(),"svg":5,"unique_ids":len(ids),"unit_rectangles":units_n,"visible_text_nodes":labels,"negative_wrong_carry_fixtures":carry_fixtures,"negative_removed_cell_fixtures":1,"negative_fraction_bar_fixtures":fraction_fixtures,"rows":rows},ensure_ascii=False))
```

Observed result at the checked translation hash above: PASS; SVG=5; unique_ids=172; unit_rectangles=86; visible_text_nodes=51; negative_wrong_carry_fixtures=4; negative_fraction_bar_fixtures=4; negative_removed_cell_fixtures=1.
