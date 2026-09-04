# Addition-core original companion notes

Date: 2026-08-31. Draft 0.1.0. Scope: original teacher-independent recovery work accompanying the first three instructional sections of m81244: U009 notation, U010 models, U011 whole-number addition without models. This is not source translation, a replacement for the named source worksheet, completion of m81244, or a validated grade-placement instrument.

## Owned output and identity

Authored only:

- `translation/recovery-addition-core.xhtml`: 81,562 bytes; SHA-256 `a3d8da4ea8c24697a11f921d0ff928e925f0c2feae2e83e90b82490b587aa813`.
- This QA/design note.

No source fragment, witness, shared terminology/log, builder, asset, reader, EPUB or PDF was edited. No new acquisition, audit, browser operation, PDF operation or commit was performed. Disk was checked above 4 GB free at authoring. The draft uses only local fragment links and inline MathML/semantic tables; it requires no external worksheet, image, font file or JavaScript at the companion-source level. Packaging and actual rendering remain integration tasks.

## Actual input boundaries

Read the actual full English and Indonesian section text for fs-id2601285, fs-id2145437 and fs-id1385496, plus the actual Tamil fragments and translator's source notes. The U010/U011 source models were also directly viewed during the immediately preceding figure tasks (all 19 and all 5 images). U009 has no media. An overlong earlier XML display was not treated as a full read: compact complete text traversals supplied the whole section content, with source MathML/carry annotations separately inspected where layout matters.

The source translator confirmed that the U009 tasks request two word forms, not numerical evaluation; the broad source expression definition stays in the source strand. The source's carrying terminology is provisional, and carrying starts at 10, not 9. A carry can be 2 with three addends. Source internal/partial zeros, including 0814, are meaningful positional displays. The separate new explanation can make all carry steps explicit without modifying source MathML.

The next source section fs-id2691382 (word phrases to notation) and later estimation/application/exercise sections are outside this companion's instructional scope. Source front matter/readiness notes are not relabeled as this companion's diagnostic.

| Input | SHA-256 |
|---|---|
| English m81244, pinned commit 38cae454e644abf9f0a623e876994553881597c9; local downloaded module | `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b` |
| Indonesian m81244, v0.2.7 / commit 3de9207f56f8b5c57c017abf973fb04e00d740f1; local downloaded module | `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6` |
| `translation/m81244-fs-id2601285.cnxml` (9,108 bytes) | `83b547490aab15c693225a832c9d03e14f2bf1ac8d4cde105470a6e2c601b313` |
| `translation/m81244-fs-id2145437.cnxml` (29,981 bytes) | `b1cd67ced5430ef3de73f8a6483a09849ac1523180f2ff26b468d8ba64620ee1` |
| `translation/m81244-fs-id1385496.cnxml` (57,548 bytes) | `dd3d4e473f5468cff9737a01d3968f60b0dd5102fb791fff529eab43ec0ddaff` |

The two witness locations are `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81244/index.cnxml` and `downloads/openstax-prealgebra-2e-id-ID/modules/m81244/index.cnxml`. Hashes were rechecked during final QA; the three source translations remained unchanged.

## Actual canon loop and terminology

Used the existing readable Tamil reference, not a new corpus acquisition:

- Actual OCR p20 (C05/C06, printed14) and complete PNG: இடமதிப்பு, ஒன்றுகள் இடம், digit/place alignment; read for drafting and reread relevant passages in revision/QA. The page's damaged OCR numerals/operators were resolved from its image, not imported into the new problems.
- Actual OCR p36 (C11, printed30), complete PNG viewed during the preceding figure work and its actual text reread for this companion: கூட்டல், கூடுதல், மொத்தம், சமன்பாடு, கூட்டலின் பரிமாற்றுப் பண்பு. Final QA returned to the sum/order and equal-value passages.
- Actual OCR p175 (C12, printed169), read in full and complete PNG viewed during final wording QA: குறியீடு, இயற்கணித கோவைகள் / இயற்கணித கூற்று, சமன்பாடு, கூட்டல் சமனி, கிடைமட்ட பட்டைகள், முழு எண்கள் / முழுக்கள். The image resolves OCR குறிமீடு to குறியீடு.
- Focused existing p38 (printed32), full OCR read before drafting, complete PNG inspected, and actual lines30–34 reconsulted at revision/QA: adding zero preserves the number; 0 is கூட்டல் சமனி. Multiplication/distributive material elsewhere on that page was not added to this companion.

The existing terminology entries were compared with the actual passages at drafting and revision. Keep கூட்டல் for the operation, கூடுதல்/மொத்தம் for its result, கூட்டப்படும் எண்கள் for addends, and கோவை / சமன்பாடு distinct in the examples. The singular arithmetic கோவை usage is a transparent extension from the algebraic glossary, not an exact elementary-definition quotation. “அடுத்த இடத்திற்குக் கொண்டு செல்லுதல்” and “சம மதிப்புள்ள குழுக்களாக மாற்றி அமைத்தல்” remain provisional descriptive choices. They do not mean a fraction, a remainder, a new digit of an original addend, or merely reversing addend order.

The 2018 reference supports register, not current curriculum alignment. Native-language review remains pending. No claim of native approval or pedagogical efficacy is made.

## Authored scope and route

There are 16 answered items: D4/P4/M4/T4. Four explanations map to four recurring domains:

| Explanation | Items | Required evidence |
|---|---|---|
| R1 | D1/P1/M1/T1 | Read the expression; describe the result using both addends; distinguish + and =, expression/equation/result; explain reversed operand order and adding zero. |
| R2 | D2/P2/M2/T2 | Model before addition, after combining, and after replacing 10 ones by one ten; keep pre-existing tens; explain unchanged value. |
| R3 | D3/P3/M3/T3 | Align unequal-length operands from ones, preserve internal zero, explain all three place calculations. |
| R4 | D4/P4/M4/T4 | Sum three addends, include incoming carries, distinguish write/carry values, carry 2 where required, preserve zeros/new leading place. |

The one-file paper route is:

D1–D4 → flagged R explanations (or skip to P if all correct) → all P1–P4 with correct answers/reasons → all M1–M4 in one answer-hidden attempt. An M failure sends the learner through the matching R and T. Every R explicitly links its P and T item. All required T items must be correct with reasons, then ALL four M items are retaken; prior partial passes are not combined. Only a fully correct M attempt reaches finish.

Links are executable local targets; no teacher-only judgment or external confidence checklist controls progress. The criterion is each requested numerical answer, place/model stage and reasoning component, with meaning-equivalent wording accepted. Speed is not assessed. Looking at an answer and then correcting it is not recorded as an independent pass. Reusing the M set after recovery is declared practice/self-check, not an unseen standardized test or validated placement result.

The model activity needs only paper; R2 also permits a written/spoken account of every before/combined/regrouped state when drawing is not possible. The final number alone is insufficient. This alternative does not establish actual AT usability, but it avoids making successful drawing the sole response mode.

## Mathematical and instructional decisions

- The notation tasks are new companion items. They do not replace the U009 source word-reading answers with numerical sums. Prompts explicitly require the result description to mention both addends, so writing only the numerical result in words is not ambiguously treated as satisfying the second word form.
- R1 uses 5+2 as an expression and 5+2=7 / 7=5+2 as equations. It explains equality as equal values, not just “write the answer next.” It does not assert that a lone number can never be an expression.
- Zero as an addend and zero as a positional placeholder are separately explained. Examples such as 7+0 versus70, and506 versus56, do not silently change operations or place values.
- The base-ten paper model is an explicitly new alternative, not a claimed copy of the source's externally named manipulatives worksheet. Ten ones and one ten are equal-valued representations; grouped units must not be double-counted.
- The exact boundary is 9 (no carry) versus10 (carry), with 5+5=10 leaving zero ones. Carry 2 is taught using three-addend458+267+89=814, including incoming carry in the next column.
- R4's999+2=1,001 makes each carry explicit and explains the intermediate processed columns001. P4/M4/T4 carry2 twice and then create a new thousands place; required zero/new-leading1 are not omitted.
- All addition is nonnegative whole-number arithmetic in the source's decimal-free/fraction-free notation. Commas retain the source's international three-digit grouping. This does not claim that later integrated source material never mentions nonwhole numbers.
- Original examples and diagnostic/routing scaffolding are clearly labeled as new. Some basic operand pairs also occur in the source table/examples; no claim is made that every pair is unseen or that these are newly discovered canonical examples.

## Exact assessment arithmetic

Each row has one linked answer with reasoning and misconception feedback. Items1 also contain reversed-order/zero questions; all are answered in their respective response.

| Item | Primary operands | Correct total | Additional required work |
|---|---|---|---|
| D1 | 6 + 2 | 8 | Two word forms, +/= meanings, reversed-order and zero reasons |
| D2 | 8 + 7 | 15 | Before/combined/regrouped model and equal-value reason |
| D3 | 304 + 25 | 329 | Right alignment, internal zero, three place calculations |
| D4 | 286 + 157 + 68 | 511 | Every column, write/carry values, final place layout |
| P1 | 9 + 4 | 13 | Two word forms, +/= meanings, reversed-order and zero reasons |
| P2 | 26 + 8 | 34 | Before/combined/regrouped model and equal-value reason |
| P3 | 407 + 52 | 459 | Right alignment, internal zero, three place calculations |
| P4 | 687 + 258 + 76 | 1,021 | Every column, write/carry values, final place layout |
| M1 | 7 + 5 | 12 | Two word forms, +/= meanings, reversed-order and zero reasons |
| M2 | 38 + 7 | 45 | Before/combined/regrouped model and equal-value reason |
| M3 | 603 + 45 | 648 | Right alignment, internal zero, three place calculations |
| M4 | 689 + 276 + 57 | 1,022 | Every column, write/carry values, final place layout |
| T1 | 8 + 6 | 14 | Two word forms, +/= meanings, reversed-order and zero reasons |
| T2 | 47 + 8 | 55 | Before/combined/regrouped model and equal-value reason |
| T3 | 502 + 36 | 538 | Right alignment, internal zero, three place calculations |
| T4 | 768 + 187 + 69 | 1,024 | Every column, write/carry values, final place layout |

## Completed source-level checks

The actual authored XML was reparsed after revisions; R1/R4 and all four gates were reread from the file. Wording fixes made before the final hash: corrected பத்தைக் நினைவில் to பத்தை நினைவில்; made feedback/remediation conditional on an error; added explicit R→T links; clarified the two-addend result-description requirement; added the non-drawing all-stages model response option. No mathematical operand/result changed in those revisions.

Passing checks at the identity above:

- Well-formed XHTML + MathML; original-companion label; correct Tamil lang/xml:lang.14sections,51unique ta-add-* IDs,79local links with all targets present.
- D/P/M/T each4items;16unique one-to-one answers. Every answer has nonempty reasoning and misconception feedback; every item and answer connects to the correct R, with P/M/T return/retry links as appropriate.
- 101MathML roots:71exact numerical equalities independently evaluated from actual XML tokens and30addition expressions. All71equalities are true. All16main question operands and their first final-answer equations match exactly.
- All extra notation-item expressions have their own correct equations/reasons; eight model Tamil word phrases were independently decoded to the ordered operand pairs.
- All24assessment column rows were recalculated from actual question operands, including incoming carry and padded missing high places; exact equation operand sequence/result matched. Final totals independently recombined from column digits/carry.
- All four model final tens/ones pairs match quotient/remainder by10; the multidigit model before/combined states also match their operands.
- Two semantic four-column worked tables each have a caption, col-scoped headers and row-scoped labels. The506+31 place matrix and458+267+89 write/carry cells match arithmetic.
- Allowed-element/attribute check found no active content or src resource. All links are fragment-local. No image, CSS, font or network resource is required by this source fragment.
- Three in-memory negative fixtures rejected: an incorrect answer equality; an arithmetically true but wrong column (altered operand and matching altered total); a misdirected remediation route. Fixtures were never written to disk.

These are source/XML/arithmetic/author checks, not a rendered-layout audit, independent native/human review or learning-outcome study.

## Remaining integration and review

Root owns combining the source/companion strands, entry/return navigation, table overflow behavior, font/CSS packaging, EPUB validation, actual narrow/wide-screen layouts, PDF outputs and their complete visual/text QA. No reader/EPUB/PDF was built here. AT/keyboard/screen-reader behavior and native Tamil review remain pending.

This16item set is not exhaustive practice of all100one-digit addition facts, every multidigit combination, the whole module's later word-phrase/estimation/application objectives, or the whole Grades2–8 allocation. Self-checking supplied reasons is an explicit local activity, not external certification. The canonical worksheet remains a source reference; the new paper route makes no claim to supply that original worksheet.

## Rerunnable read-only check

Run this Python from the repository root. It uses only the standard library, checks actual current bytes, and creates no artifact. It validates the authored companion—not a previously built reader or future changes.

```python
import sys,json,re,hashlib
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from xml.etree import ElementTree as E
from collections import Counter
from copy import deepcopy
p=Path("ta-Taml-IN/translation/recovery-addition-core.xhtml")
ns={"h":"http://www.w3.org/1999/xhtml","m":"http://www.w3.org/1998/Math/MathML"}
root=E.parse(p).getroot()
def content(e):return " ".join("".join(e.itertext()).split())
def maths(e):return e.findall(".//m:math",ns)
def parts(m):
 out=[]
 for e in m.iter():
  tag=e.tag.rsplit("}",1)[-1]
  if tag=="mn":
   assert re.fullmatch(r"[0-9]+(?:,[0-9]{3})*",e.text),e.text
   out.append(int(e.text.replace(",","")))
  elif tag=="mo":
   assert e.text in ["+","="],e.text
   out.append(e.text)
 return out
def side(tokens):
 assert tokens and all(isinstance(t,int) if i%2==0 else t=="+" for i,t in enumerate(tokens))
 assert len(tokens)%2==1
 return sum(tokens[::2])
def check_math(r):
 equalities=expressions=0
 for m in maths(r):
  ts=parts(m)
  if "=" in ts:
   assert ts.count("=")==1
   at=ts.index("=");assert side(ts[:at])==side(ts[at+1:]),ts
   equalities+=1
  else:side(ts);expressions+=1
 return equalities,expressions
def routes_check(r):
 for item in r.findall(".//h:div[@data-kind]",ns):
  assert item.get("data-remediation")=="ta-add-R"+item.get("id")[-1]
routes_check(root)
ids=[e.get("id") for e in root.iter() if e.get("id")]
assert len(ids)==len(set(ids))==51 and all(i.startswith("ta-add-") for i in ids)
byid={e.get("id"):e for e in root.iter() if e.get("id")}
links=root.findall(".//h:a",ns)
assert all(a.get("href","").startswith("#") and a.get("href")[1:] in byid for a in links)
assert not root.findall(".//h:img",ns) and not root.findall(".//h:script",ns)
for e in root.iter():
 assert e.tag.rsplit("}",1)[-1] in {"div","section","h2","h3","p","a","nav","ul","li","table","caption","thead","tbody","tr","th","td","math","mrow","mn","mo"}
 assert not any(k.rsplit("}",1)[-1].lower().startswith("on") or k.rsplit("}",1)[-1]=="src" for k in e.attrib)
assert root.get("data-strand")=="original-companion" and root.get("lang")=="ta-Taml-IN"
assert len(root.findall("h:section",ns))==14
items=root.findall(".//h:div[@data-kind]",ns)
answers=root.findall(".//h:div[@data-answer-for]",ns)
assert Counter(i.get("data-kind") for i in items)==dict(diagnostic=4,practice=4,mastery=4,retry=4)
assert len(answers)==16 and {a.get("data-answer-for") for a in answers}=={i.get("id") for i in items}
assert all(sum(a.get("data-answer-for")==i.get("id") for a in answers)==1 for i in items)
expected_inputs={
"D1":[6,2],"D2":[8,7],"D3":[304,25],"D4":[286,157,68],
"P1":[9,4],"P2":[26,8],"P3":[407,52],"P4":[687,258,76],
"M1":[7,5],"M2":[38,7],"M3":[603,45],"M4":[689,276,57],
"T1":[8,6],"T2":[47,8],"T3":[502,36],"T4":[768,187,69]}
checked=[]
def column_rows(addends):
 carry=0;place=1;rows=[]
 while place<=max(addends):
  digits=[a//place%10 for a in addends]
  terms=([carry] if carry else [])+digits
  total=sum(terms);carry=total//10
  rows.append((terms,total,total%10,carry))
  place*=10
 return rows,carry
def check_item_columns(code,answer,addends):
 rows,carry=column_rows(addends)
 actual=maths(answer)[1:]
 assert len(actual)==len(rows),(code,len(actual),len(rows))
 for m,(terms,total,digit,outgoing) in zip(actual,rows):
  ts=parts(m);at=ts.index("=")
  assert ts[:at:2]==terms and ts[at+1:]==[total],(code,ts,terms,total)
 assert sum(addends)==int(str(carry or "")+"".join(str(row[2]) for row in reversed(rows)))
for code,expected in expected_inputs.items():
 item=byid["ta-add-"+code];answer=byid["ta-add-"+code+"-answer"]
 first=parts(maths(item)[0]);assert first[::2]==expected and all(t=="+" for t in first[1::2])
 final=parts(maths(answer)[0]);assert final==[t for j,a in enumerate(expected) for t in ((["+",a] if j else [a]))]+["=",sum(expected)]
 route="ta-add-R"+code[-1]
 assert item.get("data-remediation")==route
 reason=answer.find("h:p[@class='reason']",ns);feedback=answer.find("h:p[@class='feedback']",ns)
 assert reason is not None and feedback is not None and len(content(reason))>80 and len(content(feedback))>50
 assert feedback.find("h:a[@href='#"+route+"']",ns) is not None
 if code[0]=="P":assert feedback.find("h:a[@href='#ta-add-"+code+"']",ns) is not None
 if code[0]=="M":assert feedback.find("h:a[@href='#ta-add-T"+code[-1]+"']",ns) is not None
 if code[0]=="T":assert feedback.find("h:a[@href='#ta-add-"+code+"']",ns) is not None
 if code[-1] in "34":check_item_columns(code,answer,expected)
 if code[-1]=="1":
  exprs=[parts(m) for m in maths(item) if "=" not in parts(m)]
  eqs=[parts(m) for m in maths(answer)]
  for exp in exprs:assert exp+["=",side(exp)] in eqs
  phrases=re.findall("“([^”]+)”",content(answer))
  assert len(phrases)==2
  words={"இரண்டு":2,"நான்கு":4,"ஐந்து":5,"ஆறு":6,"ஏழு":7,"எட்டு":8,"ஒன்பது":9}
  for phrase in phrases:
   got=[words[w] for w in phrase.split() if w in words]
   assert got==expected,(code,phrase,got,expected)
 if code[-1]=="2":
  pairs=[tuple(map(int,x)) for x in re.findall(r"(\d+) பத்து(?:கள்)? மற்றும் (\d+) ஒன்றுகள்",content(answer))]
  assert pairs and pairs[-1]==divmod(sum(expected),10),(code,pairs)
  if code!="D2":
   assert pairs[0]==divmod(expected[0],10)
   assert pairs[1]==(expected[0]//10,expected[0]%10+expected[1])
 checked.append((code,expected,sum(expected)))
for i in range(1,5):
 lesson=byid["ta-add-R"+str(i)]
 for target in ["ta-add-P"+str(i),"ta-add-T"+str(i)]:
  assert lesson.find(".//h:a[@href='#"+target+"']",ns) is not None
for gate,targets in {
"ta-add-diagnostic-gate":["ta-add-practice"],
"ta-add-practice-gate":["ta-add-practice","ta-add-mastery"],
"ta-add-mastery-gate":["ta-add-finish","ta-add-retry"],
"ta-add-retry-gate":["ta-add-retry","ta-add-mastery","ta-add-mastery-gate"]}.items():
 section=next(s for s in root.findall("h:section",ns) if byid[gate] in list(s))
 assert set(targets)<=set(a.get("href")[1:] for a in section.findall(".//h:a",ns))
tables=root.findall(".//h:table",ns)
assert len(tables)==2
for t in tables:
 assert t.find("h:caption",ns) is not None
 assert len(t.findall("h:thead/h:tr/h:th[@scope='col']",ns))==4
 for row in t.findall("h:tbody/h:tr",ns):
  assert len(row)==4 and row[0].tag=="{"+ns["h"]+"}th" and row[0].get("scope")=="row"
matrix=[[int(content(c)) for c in row[1:]] for row in tables[0].findall("h:tbody/h:tr",ns)]
assert matrix==[[5,0,6],[0,3,1],[5,3,7]]
assert 506+31==537
rows,carry=column_rows([458,267,89]);assert carry==0
for row,expected in zip(tables[1].findall("h:tbody/h:tr",ns),rows):
 terms,total,digit,outgoing=expected;ts=parts(maths(row)[0]);assert ts[:ts.index("="):2]==terms and ts[-1]==total
 assert int(re.search(r"\d+",content(row[2])).group())==digit
 got=re.search(r"\d+",content(row[3]));assert (int(got.group()) if got else 0)==outgoing
eq_count,expr_count=check_math(root)
bad=deepcopy(root)
bad.find(".//h:div[@id='ta-add-M4-answer']//m:mn",ns).text="690"
try:check_math(bad)
except AssertionError:pass
else:raise AssertionError("incorrect equality fixture accepted")
bad=deepcopy(byid["ta-add-M4-answer"]);m=maths(bad)[1];numbers=m.findall(".//m:mn",ns)
numbers[0].text=str(int(numbers[0].text)+1);numbers[-1].text=str(int(numbers[-1].text)+1)
check_math(bad)
try:check_item_columns("M4",bad,expected_inputs["M4"])
except AssertionError:pass
else:raise AssertionError("true-but-wrong column fixture accepted")
bad=deepcopy(root);bad.find(".//h:div[@id='ta-add-M2']",ns).set("data-remediation","ta-add-R3")
try:routes_check(bad)
except AssertionError:pass
else:raise AssertionError("wrong remediation route accepted")
print(json.dumps({"status":"PASS","sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size,"items":len(items),"answers":len(answers),"sections":14,"unique_ids":len(ids),"links":len(links),"mathml":eq_count+expr_count,"equalities":eq_count,"expressions":expr_count,"tables":2,"word_phrases":8,"assessment_column_rows":24,"negative_fixtures":3,"assessment_sums":checked},ensure_ascii=False))
```

Observed output: PASS; items16; answers16; sections14; unique_ids51; links79; MathML101 (71equalities/30expressions); tables2; word_phrases8; assessment_column_rows24; negative_fixtures3.
