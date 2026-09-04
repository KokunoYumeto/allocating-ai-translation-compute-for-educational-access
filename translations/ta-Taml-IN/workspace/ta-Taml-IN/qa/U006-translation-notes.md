# U006 source translation and review notes

Complete source scope: `m81243#fs-id2472737`, Round Whole Numbers. Tamil AI draft/review completed 2026-08-31, following work begun on 2026-08-30. This bounded subtask owns only the new source CNXML and these notes. Parent owns the future U006 SVGs and integration. No learner PDF, companion, build or commit was created here. This checkpoint does not complete the module or the full assignment. No native-speaker, teacher, board-alignment, grade-placement or efficacy approval is claimed.

## Actual boundary and inventory

Read the complete English and Indonesian subsection in the pinned `provenance/m81243.en.cnxml` and `provenance/m81243.id-ID.cnxml` witnesses. Read-only inventory and recursive comparison agree:

- **462 elements, 104 unique source IDs, 69 MathML expressions, 23 media elements, 9 exercises and 9 solutions.**
- Worked exercises: `fs-id3298586` (843); `fs-id1788778` (23,658 and 3,978); `fs-id1951300` (147,032 and 29,504). These five worked subanswers and their complete source reasoning remain.
- Practice exercises: `fs-id1312230`, `fs-id2648829`, `fs-id1288049`, `fs-id1153191`, `fs-id3447872`, `fs-id1371038`, all with their existing answers. Together the subsection contains **11 assessment answers**.
- The final assessment is `fs-id1371038`, solution `fs-id1251048`, answer paragraph `fs-id2174049` (156,000).
- The actual subsection continues after that answer: final note `fs-id3323694`, list `fs-id1881276`, with the two original OpenStax external resource links. The last named source node is therefore **`fs-id1881276`**, not the last assessment answer.
- The immediately following sibling is exactly **`m81243#fs-id2296006` — Key Concepts**. It is not included in U006; do not claim the entire module has been translated.

All source MathML text, numbers, operators, formatting, punctuation, circled subpart markers, ordered IDs and structural attributes are unchanged. There are no currency or converted measurement-unit exercises in U006; the source U.S./New York population context, year 2013 and international number grouping remain unchanged.

## Actual canon consultation and focused extension

Searched the existing readable OCR first, rather than acquiring more material by default. Existing PDF pages 32, 34 and 175 already attest rounding exercises and terminology. Read page 32's **அருகில் உள்ள பத்துகள்**, **நூறுகள்**, **ஆயிரங்கள்** and **முழுமையாக்குக** prompts, page 34's specified-place practice, and page 175's **முழுமையாக்கல் — Rounding off** glossary entry. The existing samples do not fully display the four-step worked rounding rule, so a focused extension was warranted.

Used the PDF skill's read-only workflow and the existing `scripts/ocr_canon.py --pages 30 31` to OCR just two nearby pages of the already-downloaded Government of Tamil Nadu / SCERT Class 6 Term 1 Mathematics, first edition 2018. No new book was downloaded. The two PNG/OCR pairs remain ignored under `downloads/tamil-canon/ocr/`; no learner PDF or authoring script was made. Poppler reported display-font substitution warnings; the relevant Tamil prose, tables and numerical examples were then inspected visually on both complete page images.

- **PDF page 30 / printed 24:** explains **சுமார்**, **அருகில்**, **தோராயம்** and **உத்தேச மதிப்பு**. A rounded value can be slightly above or below the exact value. This supports the translated “approximately” explanation and distinguishes exact from approximate counts. Its Indian place-name contexts are not substituted for OpenStax's international numbers.
- **PDF page 31 / printed 25, example 1.11:** rounds **8,436 to 8,400** at the hundreds place. The table locates the hundreds digit, checks the tens digit, explicitly distinguishes less than 5 from equal to or greater than 5, and replaces right-hand digits with zeros. The page image resolves the OCR's lost inequality/operator signs.
- **PDF page 31 / printed 25, example 1.12:** rounds **78,794 to 79,000** at the thousands place. Visually verified the 7 comparison, addition to the retained part and final zero replacement. OCR strings such as “76,194” were not copied.

At drafting, consulted these actual OCR passages and images. At revision/QA, reread the page-31 worked tables alongside the actual Tamil rule, carry explanation and worked table text; the decision remained to use the canon's full rounding term and nearby-place wording. The reference is first edition 2018, not a claim about the current syllabus. Parent was informed of the two-page extension so the shared canon log can be updated without competing edits.

## Linguistic and convention decisions

- Use **முழுமையாக்குதல் / முழுமையாக்கல்**, with normal inflected forms, for rounding. Both forms are actually attested. Continue the established **முழு எண்கள்**, **இலக்கம்**, **இடமதிப்பு**, **பூச்சியம்**, **எண் கோடு**, **தீர்வு** and international scale terminology.
- Use **அருகிலுள்ள பத்துகளுக்கு / நூறுகளுக்கு / ஆயிரங்களுக்கு முழுமையாக்குங்கள்**, following the readable exercise register. It means rounding to the nearest multiple of the named place value, not merely selecting a number of digits.
- **கீழ்நோக்கி முழுமையாக்குதல்** and **மேல்நோக்கி முழுமையாக்குதல்** are provisional compounds for round down/up. The adjacent source rule states the operative digit comparison and the worked examples show the action, so the directional wording is not the only explanation. These exact compounds were not attested in the selected pages.
- **மறுதொகுப்புச் செய்தல்** is provisional for regrouping. The source's explicit equality in words remains: 10 thousands become 1 ten-thousand and 0 thousands. The term is not falsely presented as a glossary quotation.
- The English general rule says “number to the right”; the Indonesian clarifies digit. Tamil uses **உடனே வலப்புறத்தில் உள்ள இலக்கம்**, avoiding a whole-number/digit ambiguity. Likewise, the how-to's “given place value is a 9” is rendered as the **digit in that position** being 9, not the place value itself equalling 9.
- The halfway rule is **this source's round-half-up convention for nonnegative whole numbers**: an adjacent digit equal to 5 goes upward. Retain the source's explanation about an agreed convention while saying it is used **இங்கு**. Do not recast it as a theorem that all rounding systems universally use the same tie rule. No alternative tie algorithm or negative-number lesson is inserted into the source.
- The English definition loosely calls the process of approximating a number rounding. Tamil says **இந்தச் செயல்முறை**, tying the term to the specific place-value process just described instead of implying that every possible estimation method is rounding.
- `fs-id2966405` explicitly retains nearest tens and the unchanged mathematical `10`. Tamil identifies 10 as the tens-place value so the sentence remains understandable with the source's embedded MathML full stop. The Indonesian sentence says a multiple of 10 without explicitly repeating “nearest”; Tamil follows the complete English meaning.
- **அமெரிக்க மக்கள்தொகைக் கணக்கெடுப்பு அலுவலகம்** is a contextual translation of U.S. Census Bureau, not an attested glossary term. The 2013 population figure remains an attributed historical source exercise datum, not a newly verified or current population claim.

## Source discrepancies and declared alternative changes

1. **Wrong rounding place in English alternative `eip-id1168289428689` (036_img-02):** it says “nearest thousand,” but the problem, worked table, actual image's instruction to write 0 in the **hundreds** place, and Indonesian alternative all show rounding **3,978 to the nearest hundred**, with carrying to 4,000. Tamil describes nearest hundreds. The English alternative also incorrectly identifies 9 as underlined; the figure worker's pixel review confirms the actual short underline is beneath 7. Tamil includes that actual detail. The answer is unchanged.
2. **Wrong rounding place in English alternative `eip-id1168288313851` (038_img-03):** it says “nearest ten thousand,” but the problem, table, actual image and Indonesian alternative show rounding **29,504 to the nearest thousand**, with carrying into the ten-thousands place to produce 30,000. Tamil describes nearest thousands. The actual answer is unchanged.
3. **Color discrepancy in 019/020/021 alternatives in both witnesses:** the canonical images mark 76/72/75 with a teal point, not the asserted orange point; the selected numeral is also blue/dark teal rather than black. Tamil accurately states the interval, unit spacing, red endpoints and marked value without the false point-color or all-other-numerals-black claims. The future redraw may use a contrast-adjusted palette; the mathematical meaning must not depend on color.
4. **031_img contains an actual visible sentence omitted from its source alternative:** “76 rounded to the nearest ten is 80.” Parent was asked to retain its Tamil equivalent; the Tamil alternative also includes that real diagram content. No new mathematical example is added.
5. Label-only diagrams 022/032 are described by their actual labeled digit targets rather than enforcing the English alternatives' vague blue designation against the cyan/turquoise original. All mathematical labels are translated and retained. The figure worker's independent visual/pixel review confirmed the small underlines beneath 6 in 022 and 2 in 032, which both source alternatives omit; the Tamil alternatives now include those real visual details. This is a declared alternative adaptation, not a changed rounding rule.
6. All five worked CALS tables (`eip-659`, `eip-493`, `eip-379`, `eip-695`, `eip-596`) declare **`cols="3"` while every actual row has two entries**. Both source witnesses have this mismatch; their alternatives accurately describe two content columns. Preserve the source declaration and actual entries. Tamil says two content columns; no cell is invented or dropped. The renderer must handle the actual row content deliberately.
7. English typographical forms “thousands pace” and “place all digits ... with zeros” are translated by their clear intended meanings, place and replace. Some PNG sources carry an incorrect image/jpeg MIME declaration; the deliberately substituted SVGs are referenced as image/svg+xml, not mislabeled copies of those PNGs.

The above changes affect explanation/alternatives, not source IDs, mathematical expressions, exercise data or solutions.

## Exact figure mapping handed to parent

All **23 canonical images were visually inspected**, including the small underline-only images and the carrying instructions. Every target uses `../assets/u006/` plus the original basename with its final extension replaced by `.svg`. Prefix below is `CNX_BMath_Figure_01_01_`. Preserve the source order: the 035 and 036 groups deliberately use **01, 03, 02**, not filename-sort order.

| Source suffix | Content to preserve in target SVG |
|---|---|
| `019.jpg` | Number line 70–80, unit spacing, point at 76, red endpoints. |
| `020.jpg` | Same line, point at 72. |
| `021.jpg` | Same line, point at 75, exact midpoint. |
| `022.jpg` | 76; tens-place label points to 7; greater-than-5 label points to 6. |
| `031_img.jpg` | 76 → 80; add 1 to 7, cross out/replace 6 with 0; final nearest-ten sentence. |
| `032_img.jpg` | 72; tens-place label points to 7; less-than-5 label points to 2. |
| `033_img.jpg` | 72 → 70; do not add 1 to 7, cross out/replace 2 with 0. |
| `034_img-01.png` | 843; tens-place label points to 4. |
| `034_img-02.png` | 843; underline 3. |
| `034_img-03.png` | 843; underline 3 again, distinct source media ID. |
| `034_img-04.png` | 840; underline 0. |
| `035_img-01.png` | 23,658; hundreds-place label points to 6. |
| `035_img-03.png` | 23,658; underline 5. |
| `035_img-02.png` | Add 1 to 6, replace 58 with 00, downward arrow to 23,700. |
| `036_img-01.png` | 3,978; hundreds-place label points to 9. |
| `036_img-03.png` | 3,978; underline 7. |
| `036_img-02.png` | 9 + 1 = 10; write 0 in hundreds, add 1 in thousands; replace 78 with 00; 4,000. |
| `037_img-01.png` | 147,032; thousands-place label points to 7. |
| `037_img-02.png` | 147,032; underline the hundreds digit 0. |
| `037_img-03.png` | 147,000. |
| `038_img-01.png` | 29,504; thousands-place label points to 9. |
| `038_img-02.png` | 29,504; underline the hundreds digit 5. |
| `038_img-03.png` | 9 + 1 = 10; write 0 in thousands, add 1 in ten-thousands; replace 504 with 000; 30,000. |

Coordinated labels: **பத்துகள் இடம்**, **நூறுகள் இடம்**, **ஆயிரங்கள் இடம்**; **5-ஐ விடப் பெரியது**, **5-ஐ விடச் சிறியது**; **1-ஐக் கூட்டுங்கள்**, **1-ஐக் கூட்ட வேண்டாம்**, **0-ஆல் மாற்றுங்கள்**, **0-களால் மாற்றுங்கள்**. Carry instructions explicitly name the retained and next-left positions. These strings and the two source-alt repairs were sent to parent before figure authoring.

## Independent checks and present limits

Passed read-only checks against both source witnesses:

- Recursive element/child-order/stable-attribute equality, all 104 ordered IDs unique, all 69 MathML trees and mathematical text unchanged, all circled markers retained, all 9 source solution nodes present.
- Body numeral token order also matches both sources, including comma-grouped numbers. Ordinary prose punctuation and Tamil inflection are not treated as changed numeric values. Two “add 1 to 9” clauses were phrased as **1-ஐ 9-உடன் கூட்டி** to retain source numeric-token order without changing the operation.
- Recalculated **all 11 assessment answers** independently by finding the lower and upper multiples and comparing distances, with ties going to the upper multiple: 843→840; 157→160; 884→880; 23,658→23,700; 3,978→4,000; 17,852→17,900; 4,951→5,000; 147,032→147,000; 29,504→30,000; 63,921→64,000; 156,437→156,000, at their respective source places.
- Checked the six introductory rounding pairs: 76→80, 72→70 and 75→80 at tens; 19,651,127→20,000,000 at millions, →19,700,000 at hundred-thousands and →19,650,000 at ten-thousands.
- Independently implemented digit inspection/zero replacement/repeated 9-carry, and compared it with nearest-distance tie-up and the integer formula `((n + base//2)//base)*base` for every integer 0–9,999 at bases 10, 100 and 1,000: **30,000 cases passed**. No floating-point/banker's-rounding function was used. Edge checks include 999→1,000 at all three places, 9,999→10,000 at tens, 995→1,000 versus 994→990, and 950→1,000 versus 949→900. These are QA cases only, not added source exercises.
- The source how-to tells the reader to repeat carrying across 9s but does not explicitly spell out creating a new leading 1 when every affected left-hand digit is 9. Its worked carry examples use an already-written left neighbour. Preserve that source scope; a separate recovery explanation should make the 999→1,000 new-leading-digit case explicit. The QA algorithm handles that case, which does not imply the source already explains it fully.
- All 21 rows across the five tables still have exactly two entries under the original three-column declarations. Three internal figure links resolve to unchanged source IDs. The two external URLs and their ordering remain exact: `https://www.openstax.org/l/24detplaceval` and `https://www.openstax.org/l/24numdigword`. Their displayed link text is translated; their live availability/offline content was not verified or invented here.
- Every image reference matches the agreed basename-to-SVG mapping. At the source QA check all 23 target files were still pending parent authoring, so **asset closure, actual redraw/alternative matching and rendered accessibility are not yet passed**. Their eventual presence alone will not prove visual correctness.
- Current source SHA-256 after the three underline-detail alternative additions: **`5ae5553b9ea293ff95e910eb36689c524faaf89954cbdf88d350f302cb7b7a3c`**, 45,409 bytes. Only those three alternative attributes changed after the structural/numerical run; no mathematical or structural node changed.

The source's embedded MathML punctuation is retained even where Tamil sentence order would ordinarily place it differently. Native/specialist review of sentence cadence, provisional compounds and learner readability remains open. The present checks prove structural/numerical correspondence, not educational efficacy. Disk free space was above 11 GB at task start; no disk-full error occurred.

Next contiguous source marker: **`m81243#fs-id2296006` — Key Concepts**.
