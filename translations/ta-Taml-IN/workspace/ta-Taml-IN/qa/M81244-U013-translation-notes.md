# M81244 U013 translation notes

## Bounded source and ownership

- Date: 2026-08-31. Owned source: `translation/m81244-fs-id2197427.cnxml`; this note is the only owned QA file.
- Both actual complete witnesses were read for `m81244#fs-id2197427`, **Add Whole Numbers in Applications**.
- English: `provenance/m81244.en.cnxml`, whole-module SHA-256 `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b`.
- Indonesian: `provenance/m81244.id-ID.cnxml`, whole-module SHA-256 `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6`.
- The final title **பயன்பாட்டுக் கணக்குகளில் முழு எண்களைக் கூட்டுதல்** matches the separately authored fifth module objective exactly; no metadata edit was made here.
- The parent assigned `assets/u013/` and a separate figure note to `pilot_review`. This translator did not author or edit the three SVGs.
- No witness, companion, builder, CSS, shared ledger/log or goal file was edited. During this work the parent separately authorized a narrow late-peer-review correction to U012's increased-by wording; that change is recorded in `M81244-U012-translation-notes.md`, with a new source hash and repeat QA. No other earlier source was altered. No new source/corpus download, learner-PDF build or commit was performed. The parent explicitly approved the narrow ignored reference-cache extension described below.
- Free space was checked before source authoring and before the approved OCR operation; both checks exceeded 4 GB. No disk-full error occurred.

## Canon: actual drafting, revision and QA consultation

Reference: the already acquired Tamil Nadu/SCERT Class 6 Term 1 Mathematics, first edition 2018, `downloads/tamil-canon/tn-scert-6-term1-maths-2018.pdf`. It is a register reference, not a replacement mathematical source, alignment assertion or current-syllabus claim.

### Drafting and focused extension

- Read actual existing OCR page 024, including applied questions with named lengths/units and a square-mile example; did not copy any of its questions, answers or units into this source. Existing page-036 addition and page-028 simplification models continue the established **கூட்டல்**, **கூடுதல்**, **சுருக்குதல்**, and **தீர்வு** register. Their actual page images were already inspected in the immediately preceding unit, resolving OCR errors such as கூருதல் for கூடுதல்.
- Searched the existing OCR for perimeter/foot/inch terms. It did not provide a direct perimeter example. The contents and the same PDF's text index were used only to locate a relevant page, not to claim a readable new attestation from an unverified text layer.
- First rendered/OCRed PDF page 46 in memory using Tesseract Tamil and read the actual OCR. Attempts to forward the in-memory PNG/JPEG for inspection failed with an image-processing omission; those failed attempts are **not** counted as visual review. They did not create files or change the source.
- The parent then explicitly authorized `python ta-Taml-IN/scripts/ocr_canon.py --pages 46`. The existing script was read before execution. This created **only** the ignored `downloads/tamil-canon/ocr/page-046.png` and `page-046.txt` reference caches. The script exited successfully; Poppler emitted fallback-font warnings. The completed actual OCR was read and the entire PNG was viewed with the image-inspection tool; relevant Tamil text was legible. The OCR still mangles some unrelated mathematical operators, so they were not adopted.
- **New locator: PDF page 46 / printed page 40**, in the introduction to algebra. The actual page uses **அன்றாட வாழ்க்கையில்**, **மைல்களைக்**, and **சுற்றளவின்** in a string-measurement/fenced-garden context. A separate bullet uses **பரப்பளவு** for a park. This supports the circumference/perimeter-versus-area distinction and the everyday-application register. It does not itself supply the source's formal perimeter definition or attest the exact foot/inch headwords.
- OCR SHA-256: `b7955cfbf49c5321874771aa26755d1e4ecfad0031ada9ed034d479bfdefda89`.
- PNG SHA-256: `c208f8b59c7a2747171152f4e53198c48aae52858a24f76880cd9f024cdfb229`.
- The locator and hashes were sent to the parent and figure worker for their independent consultation and the parent's shared canon-log integration.

### Revision and QA

- During revision, reread the actual page-046 application/perimeter/area passage, the page-028 worked simplification example, and the page-036 addition passage while reviewing the complete translated paragraphs and table cells. The source's length-summing definition remained authoritative; the canon's conversion example was not used to convert source miles into kilometres.
- The three source JPEGs were visually inspected in full before writing their Tamil alternatives. These inspections are distinct from the Tamil canon review.
- At QA, source sums, carry notation, diagram side lengths and units were checked against the complete source witnesses and actual images. Relevant actual canon passages were reconsulted to check that சுற்றளவு denotes boundary length, not area, and that the translation preserves operation/result and worked-solution language.
- Consultation is recorded here because the parent owns the shared log. No fluent-Tamil or board approval is claimed.

## Exact inventory and continuation

| Item | Count |
|---|---:|
| Elements including section root | 210 |
| Ordered unique source IDs including root | 46 |
| MathML expressions | 16 |
| MathML `mrow` / `mn` / `mo` | 11 / 36 / 17 |
| MathML `mspace` / `mtext` | 9 / 5 |
| MathML `mtable` / `mtr` / `mtd` | 1 / 9 / 6 |
| MathML `mover` / `munder` | 1 / 1 |
| Examples / exercises / supplied solutions | 2 / 6 / 6 |
| Tables / rows / entries | 2 / 11 / 22 |
| Media / images | 3 / 3 |
| Notes / list / list items / external links | 5 / 1 / 3 / 3 |

- The last worked/practice solution is `fs-id2136690`, with paragraph `fs-id1613173`.
- It is followed by the retained additional-online-resources note **`fs-id719196`**, whose last ID-bearing node is list **`fs-id1176422`**. All three list items and their link nodes are included, including the final “Adding Whole Numbers” link.
- Exact next sibling: **`m81244#fs-id1611455`, Key Concepts**. It is outside U013. This checkpoint does not claim the module or full assignment complete.

## Source contexts, quantities and language decisions

- Hao → **ஹாவோ**, Mark → **மார்க்**, Lincoln Middle School → **லிங்கன் நடுநிலைப் பள்ளி**. These are provisional name/register renderings; no people, country or school system were replaced with local examples.
- The five test grades/points are **மதிப்பெண்கள்**. The three school grades are **வகுப்பு நிலைகள்**. These distinct senses of “grade” are not collapsed into one term or confused with the grade level of this learning product.
- The semester remains a **கல்விப் பருவம்**. No calendar year, number of weeks, 365-day assumption, maximum score, percentage, average or local three-term school calendar is introduced. In particular, 432 is a total number of points, not a percentage.
- Mark remains training for a bicycle race; his distances stay attached to Monday, Wednesday, Friday, Saturday and Sunday in that order. “Last week” is preserved. No values for unmentioned days are invented.
- **மைல்கள்** retains miles, supported by actual page 046. **அடி** retains feet and **அங்குலம்** retains inches. The latter two exact unit headwords were not found in the consulted passages and are recorded as provisional Tamil equivalents, not newly attested canon entries. No metric conversion, currency substitution or rounding occurs. This section contains no currency or numerical calendar year.
- **சுற்றளவு** is now directly supported by the actual new reference page. The source's definition is faithfully translated as the distance around a geometric figure and the sum of its side lengths. It is not area. The source examples of fencing a garden and framing a picture are both retained.
- Patio → **முற்றம்**, a provisional plain-language rendering of the open outdoor area. The source's six-sided outline and feet remain unchanged; no house, paving material, garden shape or local architectural context is added.
- The English worked-table phrase “sum of the sides” is translated **பக்கங்களின் நீளங்களின் கூடுதல்**, making “lengths” explicit as in the preceding source definition and the Indonesian table. It means adding measured lengths, not adding a number of sides; it is a semantic clarification, not a new calculation or changed answer.
- The five-step source plan remains: identify what is sought, write a phrase, translate to notation, simplify, and answer in a sentence with appropriate units. Existing source worked steps and terse try-item answers are retained; no new recovery explanation is inserted into the source.

### MathML language exceptions only

- Two `mtext` nodes `and` / `dan` → **மற்றும்**.
- Two `mtext` nodes `base-10` / `Basis-10` → **அடிமானம்-10**; their hyphen and numeral are retained.
- The fifth `mtext`, **`____`**, is an underline representation and is unchanged.
- All other mathematical content, whitespace, layout attributes, rows, operators, punctuation and order are unchanged. In particular, the carry **3** above the **8** of **87** is retained; it is neither a numerator nor part of the base numeral. All three initial empty `mtr` nodes remain.

## Exact source-image mapping and accessibility decisions

Canonical raster directory: `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`. All three JPEGs were actually viewed. The matching JPEG files in the Indonesian repository are byte-identical, but the Indonesian CNXML already selects an SVG for the first image.

Canonical raster identities checked read-only:

- 002: 304 by 138 pixels; SHA-256 `aaced737e0448c122d0c5df06df1fa0cb401c19630f0840973fb1f65b6edbd28`.
- 003: 229 by 130 pixels; SHA-256 `a2f3145a692006fe3af33dcb894b00bc03bfcc18370fab367f2bd9316d646137`.
- 004: 228 by 141 pixels; SHA-256 `ac6856ba7f2d69c05a1a7396c339ece3c6ce6a0d5af3174888b41e9050188ef8`.

| Media ID | English canonical filename | Indonesian witness `src` suffix | Tamil path |
|---|---|---|---|
| `fs-id588598` | `CNX_BMath_Figure_01_02_002.jpg` | `CNX_BMath_Figure_01_02_002.jpg.id-ID.svg` | `../assets/u013/CNX_BMath_Figure_01_02_002.svg` |
| `fs-id2175999` | `CNX_BMath_Figure_01_02_003.jpg` | `CNX_BMath_Figure_01_02_003.jpg` | `../assets/u013/CNX_BMath_Figure_01_02_003.svg` |
| `fs-id1381557` | `CNX_BMath_Figure_01_02_004.jpg` | `CNX_BMath_Figure_01_02_004.jpg` | `../assets/u013/CNX_BMath_Figure_01_02_004.svg` |

- **002:** six sides, source-alt order 4, 9, 2, 3, 2, 6 feet. Every visible measurement spells out **feet**. The SVG must retain the unit as **அடி** on every corresponding label. The actual pale turquoise pointer toward the inner vertical side is included in the Tamil alternative although omitted from the source prose alternative. Its description adds no numerical label or answer.
- **003:** eight sides, source-alt order 4, 9, 4, 3, 2, 3, 2, 3 inches. The image itself contains **numbers only**; inches is specified by the source question. The Tamil alternative explicitly distinguishes these two facts instead of implying that the word “inches” is visibly printed. The actual side values and order are retained.
- **004:** eight sides, clockwise source-alt order 2, 12, 6, 4, 2, 4, 2, 4 inches. Again, the visible labels are numbers only. The Tamil alternative explicitly says where the unit comes from and identifies the starting side as the short upper-left side, resolving an otherwise ambiguous starting point among several sides labelled 2.
- The 003/004 source alternatives loosely call labels “4 inches”, etc.; the explicit separation of numeric labels from the question-supplied unit is a declared visual-accessibility clarification based on actual pixels, not a unit correction.
- Original Arabic numerals, including the English alternatives' numeric side ordinals, remain in order. Indonesian writes several ordinals as words, so side-length comparison is semantic rather than a false all-digit-string equivalence between the two languages.
- No perimeter total is added to any source image alternative. In particular, the 30/36 answers remain only in their source solutions, not in question descriptions. No total is requested for the figure labels themselves.
- The parent authorized these exact Tamil SVG paths. SVG authorship, geometry, visible text, font checking and figure notes belong to the separate worker; translator-side closure is recorded at handoff below.

## Source declaration inconsistencies preserved

Both tables declare `cols="3"` while having exactly two cells in every actual row:

| Table ID | Rows | Actual cells per row |
|---|---:|---:|
| `eip-id1168288617772` | 5 | 2 |
| `eip-id1168289453960` | 6 | 2 |

No extra columns/cells were invented and no structural attribute was repaired. Their two language-bearing summaries are translated. A reader may accommodate actual row widths, but that is outside this source-edit scope.

## Complete six-exercise answer check

| Exercise ID | Problem ID | Solution ID | Source quantities and result |
|---|---|---|---|
| `fs-id1899571` | `fs-id4300687` | `fs-id1944399` | `87+93+68+95+89 = 432` points |
| `fs-id1564459` | `fs-id2176012` | `fs-id2146653` | `18+15+26+49+32 = 140` miles |
| `fs-id1761942` | `fs-id1294758` | `fs-id2296132` | `230+165+325 = 720` students |
| `fs-id1628979` | `fs-id1511502` | `fs-id1568241` | `4+6+2+3+2+9 = 26` feet |
| `fs-id2483376` | `fs-id1542511` | `fs-id2284683` | side lengths `4,9,4,3,2,3,2,3`; perimeter `30` inches |
| `fs-id2427950` | `fs-id1225224` | `fs-id2136690` | side lengths `2,12,6,4,2,4,2,4`; perimeter `36` inches |

Every supplied value is correct. There are no missing source solutions in this section. The arithmetic above is review evidence, not new material inserted into the source try-item solutions.

## Machine and independent checks

Read-only Python/lxml checks were run on the actual authored source and both witnesses. No helper or receipt outside the owned files was written.

1. Recursive element hierarchy and stable attributes match; allowed differences are root locale, three translated `alt` strings, two translated table summaries, and the three explicitly mapped image paths/MIME types.
2. All 46 IDs are unique and retained in source order. The 16 MathML trees match exactly apart from the four documented language-only `mtext` values. All 36 `mn`, 17 `mo`, nine `mspace`, carry/underline structures and empty rows are retained.
3. Document-text Arabic numeral sequences match both witnesses by individual text slot. Every source-alternative side length matches both languages in order. English alternative side-ordinal digit sequences also match exactly. An initial raw-digit comparison against Indonesian correctly exposed its written-out ordinals; the check was refined to compare actual measured lengths, not to treat equivalent ordinal spelling as changed data.
4. Every exercise is paired with its own problem and supplied solution. The first three numerical lists were read from their problem MathML. Diagram side lengths were read from the checked alternatives and visually verified against the canonical images. Each result was recomputed using direct integer addition and an independent decimal-column carry algorithm; all six passed with the correct unit.
5. The vertical score table was parsed using only the base of `mover` and `munder`, not their annotation/underline. It contains `87,93,68,95,89` and final `432`. Ones sum to `32`, producing the displayed carry `3`; tens plus that carry sum to `43`. The source is not misread as the flat text string `837...`.
6. The three perimeter diagrams were independently reconstructed as closed rectilinear polygons with the given dimensions. Manhattan edge-length sums are respectively 26, 30 and 36, agreeing with the source arithmetic. This is a mathematical feasibility/answer check, not a claim that raster pixel lengths are drawn to scale.
7. All three original external URLs are unchanged: `https://www.openstax.org/l/24add2blocks`, `https://www.openstax.org/l/24add3blocks`, and `https://www.openstax.org/l/24addwhlnumb`. The titles are translated without changing their two-/three-digit or base-10 subjects. The links were preserved, not newly fetched or certified as offline resources.
8. No residual Latin prose remains. The locale-specific title exactly matches metadata objective five. Grade scores and school grade levels, miles and inches/feet, and perimeter and area were separately reviewed for meaning.

**Final source SHA-256:** `8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb` (16,980 bytes). Initial source QA preceded the figure worker's completion; the final closure below supersedes that initial asset-pending state.

Final repeat source checks on this exact file passed against both witnesses: 210 nodes, 46 IDs, 16 MathML trees with only the four named language exceptions, stable structure/attributes and body numeral order. The exact source hash is unchanged from the six-answer/two-method arithmetic and carry/perimeter checks above. Actual page-046 perimeter/area and miles passages were reread again at final QA.

Translator-side final asset closure:

| SVG | IDs | SHA-256 |
|---|---:|---|
| `CNX_BMath_Figure_01_02_002.svg` | 16 | `9e7ba0e663a9fac7d3d801b8c14e9572a31482c872f521d7ca9ddde44671e249` |
| `CNX_BMath_Figure_01_02_003.svg` | 19 | `15c5db825e70164c99083bd70dbd184ada8d805fe9cc3f94ccae44d20022c67d` |
| `CNX_BMath_Figure_01_02_004.svg` | 19 | `fe97fdf9a9d0fc68890f683d4a0454829fa1165b375aed8d294d159b170fa911` |

All three files exist and parse. Each has a title and a description exactly equal to the corresponding final Tamil `media/@alt`; each `aria-labelledby` target resolves. All **54 SVG IDs are unique across the three files**. Visible numeric-label multisets match all source side lengths; 002 has six **அடி** labels, while every 003/004 visible label is numeric-only. No question's perimeter total is inserted into the corresponding title/description. These are closure/content checks, not a substitute for the figure worker's geometry/font review or a rendered assistive-technology test. No SVG was edited by this translator. Final disk check: 3,824,758,784 bytes free.

## Limits

No rendered learner reader/PDF or assistive-technology inspection is claimed here. Fluent-Tamil review remains needed for provisional name, patio and unit wording. Source-faithful worked answers are not a claim that the diagnostic/mastery/retry route is complete. The next source node remains `m81244#fs-id1611455`.
