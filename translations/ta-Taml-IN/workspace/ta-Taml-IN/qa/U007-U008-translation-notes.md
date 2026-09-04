# U007–U008 source translation and review notes

Tamil AI source draft and checks dated 2026-08-31. Owned files are `translation/m81243-fs-id2296006.cnxml`, `translation/m81243-fs-id2279009.cnxml` and these notes. The separate figure worker owns the five U008 SVGs; U007 reuses the already-authored U003 place-value chart. No missing source solution is supplied inside either CNXML file. No reader/PDF build, commit, shared-log edit or full-module educational-workflow completion is claimed. Native/specialist linguistic, teacher, curriculum and efficacy approval remain absent.

## Actual source spans and inventories

Read both complete English and Indonesian witnesses, including the final self-check paragraphs and the document-level material that follows content. Recursive source comparison gives:

| Unit / root ID | Elements | Unique IDs | MathML | Exercises | Supplied solution nodes | Media |
|---|---:|---:|---:|---:|---:|---:|
| U007 `fs-id2296006`, Key Concepts | 24 | 7 | 0 | 0 | 0 | 1 |
| U008 `fs-id2279009`, Section Exercises | 659 | 273 | 57 | 58 | 29 | 5 |

U007 contains the original chart and three nested procedure lists. Its last named source node is `eip-id1170195386333`; its next sibling is **`m81243#fs-id2279009`**.

U008 contains the four original child sections: practice `fs-id2318815`, everyday math `fs-id1717629`, writing `fs-id1345943`, and self-check `eip-823`. The last exercise is `fs-id1258379` (no source solution), but the actual span ends later, at self-check paragraph **`eip-id1168466338968`**. U008 is the final child of `<content>`. A separate document-level `<glossary>` follows, with seven definitions beginning at **`fs-id2642858`** and ending at `fs-id4338000`; those definitions are not included here and were assigned separately by parent. Do not mistake end-of-content for end-of-document or completed recovery delivery.

## Canon consultation at drafting, revision and QA

Used existing readable references rather than acquiring a new corpus. Read the current canon locators and relevant actual OCR for:

- PDF page 35 / printed 29, C08/C09: the counting convention starts at 1 and the whole-number set includes 0. This supports the classification questions and the supplied qualitative difference answer. The reference's distinction from integers remains in the page-175 glossary; do not translate whole numbers as முழுக்கள்.
- PDF pages 11–12 / printed 5–6, C13/C14: separated tens/unit names, place-value grouping, writing and reading numerals, and explicit worked examples. At revision/QA, reread these actual passages alongside all 22 Tamil full-number word strings extracted from the new file. Retain the source's international periods rather than substituting the canon's Indian grouping.
- PDF page 20 / printed 14, C05/C06, already consulted across the source strand: இடமதிப்பு, இலக்கங்கள் and தீர்வு. Continue the digit-position distinction in the ten supplied place-name answers.
- PDF pages 30–31 / printed 24–25, just OCRed and visually checked during U006: approximate-value language and the four-step round-half-up process. Reread the actual page-31 rule for the U007 summary and U008 rounding answers. Page 175 attests முழுமையாக்கல். No further OCR/download was needed for these two review sections.

The reference remains Government of Tamil Nadu / SCERT, Class 6 Term 1 Mathematics, first edition 2018. It supports register choices, not present-day syllabus, board alignment or linguistic certification. Mathematical OCR noise was not copied: the previously inspected page images resolve the number-name and inequality passages.

## Translation and representation decisions

- Continue **இயல் எண்கள்**, **முழு எண்கள்**, **இலக்கம்**, **இடமதிப்பு**, **முழுமையாக்கல் / முழுமையாக்குதல்** and the existing provisional international **இடமதிப்புத் தொகுதி**, **மில்லியன்**, **பில்லியன்**, **டிரில்லியன்** register.
- Use the same explicit period-count plus scale-word style as U004/U005, with separated tens/unit words and English-source commas between periods. **ஓர் ஆயிரம்** and **ஒரு பில்லியன்** are inflected singular count-1 phrases, not a changed value. Zero-valued trailing periods are not spoken in names, but remain present in the source numeral answers.
- Preserve the language-bearing MathML node in `eip-954`: English **base-10** / Indonesian **basis-10** becomes **அடிமானம்-10**. The numeric 10 and ASCII hyphen remain; this is the single translated MathML text string. All remaining MathML, including four dollar mtext values, is unchanged.
- Preserve international grouping, all dates, decimal points, fractions, currency symbols and original unit quantities. Feet become **அடி**, hours **மணிநேரங்கள்**, minutes **நிமிடங்கள்**, years **ஆண்டுகள்**, gallons **கேலன்**, kilometers **கிலோமீட்டர்கள்** and dollars **டாலர்கள்**; no units or currencies are converted. Missing units in source numeral-only answers are not silently supplied as extra source text.
- Geographic/name choices are contextual, provisional transliterations, not canon quotations: Rainier **ரெய்னியர்**, Adams **ஆடம்ஸ்**, Miami-Dade county **மயாமி-டேட் கவுண்டி**, Chicago **சிகாகோ**, California **கலிஃபோர்னியா**, Tahoe **டாஹோ**, Jorge **ஹோர்ஹே**, Marissa **மரிசா**. The original people/places are not replaced by local examples. **வரவு செலவுத் திட்டத் தொகை** continues U005's plain budget wording.
- **Practice Makes Perfect** is rendered idiomatically as **பயிற்சி திறனை வளர்க்கும்**. **Writing Exercises** means **எழுதி விளக்கும் பயிற்சிகள்**, not handwriting practice. **Self Check** is **சுய மதிப்பீடு**; its confidence categories are not represented as validated test scores.
- U007 repeats the source half-up carry procedure and its distinction between the target digit and the digit immediately to its right. As in U006, “place value is a 9” means the digit in that place is 9. Normalized the English summary's doubled punctuation after the Step 3 reference; no numeric or structural content changes.

## Source limitations, assumptions and discrepancies

- The two witnesses supply solutions for exactly alternating exercise nodes: **29 supplied, 29 absent**. Keep these absences visible. New learner-ready completions belong in a separate companion, with explanations and routes, not in source solution nodes.
- The one-year/70-year statements assume **365 days per year**: `70 × 365 × 24 = 613,200` hours and `365 × 24 × 60 = 525,600` minutes. The source does not discuss leap years. Retain the values and note the assumption for a companion rather than silently changing either question.
- Population, enrollment, vehicle, astronomical-age, mountain-height, water-capacity, budget and distance quantities remain **source exercise data**, not newly verified current facts. In particular, the 2016 China forecast and July 1, 2014 India estimate are not current predictions/counts. “In five years” and “about twelve years ago” have no explicit base date in these exercise sentences; do not re-anchor them to 2026. Tamil past-report wording preserves the forecast/estimate character where appropriate.
- The source self-check says that mostly “Confidently” selections mean the section's objectives have been achieved. This is preserved as source material, **not adopted as an evidence-based mastery gate** for the recovery product. Confidence and demonstrated correctness are different. Parent's separate companion must provide executable checks and answer-based routing.
- The source self-check also relies on classmates, an instructor and campus tutors, with urgent advice to seek help. These paragraphs are faithfully retained; they are **not teacher-independent recovery instructions** by themselves. Do not silently erase them or claim their mere translation closes the access gap. A separate self-contained route must accompany any learner release.
- The U007 carry summary, like U006, does not explicitly state how to create a new leading 1 after carrying through an all-9 prefix. Keep its source boundary and use a separate recovery explanation for that case.
- Several Indonesian number names omit the English source's period commas. Tamil retains the explicit source comma convention without changing values. No supplied numerical answer discrepancy was found in the 29 source solutions.

## Figure mapping and accessibility

U007 reuses `../assets/u003/CNX_BMath_Figure_01_01_011.svg`, corresponding to the same canonical `CNX_BMath_Figure_01_01_011.png`. Preserve U007's distinct figure/media IDs `eip-id1170196618448` / `eip-id1170196618449`; asset reuse must not collapse source nodes. The full Tamil alternative lists all 15 place labels, five groups, eight leading blanks and the exact 5,278,194 value, matching the existing U003 chart.

All five U008 canonical rasters were visually inspected. Targets under `../assets/u008/` are:

| Media ID | Target basename | Actual content |
|---|---|---|
| `fs-id1393361` | `CNX_BMath_Figure_01_01_201_img.svg` | Five hundreds squares, six tens rods, one single block. |
| `fs-id1284927` | `CNX_BMath_Figure_01_01_202_img.svg` | Three hundreds squares, eight tens rods, four single blocks. |
| `fs-id2675330` | `CNX_BMath_Figure_01_01_203_img.svg` | Four hundreds squares, no tens rods, seven single blocks. |
| `fs-id2716627` | `CNX_BMath_Figure_01_01_204_img.svg` | Six hundreds squares, two tens rods, no single blocks. |
| `eip-id1165721974707` | `CNX_BMath_Figure_AppB_001.svg` | Four columns: ability plus three confidence choices; six ability rows and 18 empty response cells. |

The block alternatives preserve each 10-by-10 hundred structure and 10-block rod structure, rather than only a total. Explicit absence of tens/singles agrees with the actual images and the Indonesian alternatives. The alternatives and future SVG titles/descriptions must not add unsolicited computed assessment totals.

The self-check alternative is expanded from the source's brief summary to transcribe all six actual skills and all three choices. Coordinated headings are **என்னால்…**, **நம்பிக்கையுடன்**, **சிறிது உதவியுடன்**, **இல்லை—எனக்குப் புரியவில்லை!**. The visible row predicates end in **முடியும்**; the alternative lists the equivalent skills as noun phrases. No selections, example checks or confidence results are invented. Figure creation and final rendered/alternative matching remain the figure/integration owners' checks.

## Explicit missing-answer inventory

These 29 exercise/problem pairs lack a `<solution>` in **both** actual witnesses and in the Tamil source. Together they contain 48 requested response parts, counting each labeled subpart and the final open-ended prompt. The self-check's unscored reflective questions are additional source material, not included in this exercise count.

| Exercise ID | Problem ID | Task / response parts |
|---|---|---|
| `fs-id834824` | `fs-id1566499` | Counting/whole-number classification; 2. |
| `fs-id2134956` | `fs-id1367088` | Counting/whole-number classification; 2. |
| `fs-id2646862` | `fs-id2805128` | Base-ten block model 202; 1. |
| `fs-id1339977` | `fs-id1577980` | Base-ten block model 204; 1. |
| `fs-id1522372` | `fs-id1684233` | Digit places in 398,127; 5. |
| `fs-id1350682` | `fs-id1464316` | Digit places in 78,320,465; 5. |
| `fs-id1190749` | `fs-id1629686` | Name 5,902; 1. |
| `fs-id1822153` | `fs-id2276526` | Name 146,023; 1. |
| `fs-id1798411` | `fs-id1946634` | Name 1,458,398; 1. |
| `fs-id1166761301603` | `fs-id1020409` | Name 62,008,465; 1. |
| `fs-id3014390` | `fs-id1213910` | Name the Mount Adams height; 1. |
| `fs-id1300121` | `fs-id2223819` | Name the one-year minute count; 1. |
| `fs-id1386002` | `fs-id1172613` | Name the Chicago population; 1. |
| `fs-id1362934` | `fs-id1239323` | Name the California vehicle count; 1. |
| `fs-id1544452` | `fs-id2443426` | Name the India population estimate; 1. |
| `fs-id1384471` | `fs-id1221829` | Write the three-digit word name as digits; 1. |
| `fs-id2760170` | `fs-id1265455` | Write the thousand-group word name as digits; 1. |
| `fs-id2353124` | `fs-id1387432` | Write the million-group word name as digits; 1. |
| `fs-id2241247` | `fs-id1892005` | Write the billion-group word name as digits; 1. |
| `fs-id2926292` | `fs-id1863618` | Write the solar-system-age word name as digits; 1. |
| `fs-id1572155` | `fs-id2261957` | Write the federal-budget word name as digits; 1. |
| `fs-id1621308` | `fs-id1190161` | Round to tens; 2. |
| `fs-id2240116` | `fs-id1573732` | Round to hundreds; 2. |
| `fs-id1516723` | `fs-id2926660` | Round to thousands; 2. |
| `fs-id1372149` | `fs-id1605093` | Round to thousands; 2. |
| `fs-id2610406` | `fs-id1899511` | Kitchen-cost check amount in words; 1. |
| `fs-id1604312` | `fs-id1166211` | Kitchen-cost rounding at four places; 4. |
| `fs-id1806959` | `fs-id1792359` | Earth–Sun distance rounding at three places; 3. |
| `fs-id1258379` | `fs-id4295295` | Original everyday rounding example; 1 open-ended response. |

Do not mark these unanswered source exercises as independently usable assessments until a separately identified companion supplies each answer or example response, relevant reasoning and a usable route.

## Independent checks completed

- Both XML files parse. Recursive tag/child-order/stable-attribute comparison against both witnesses passes, as do ordered ID lists and whole-body numerical token order. Root language, translated alternatives, image path/MIME and the one language-bearing mtext are declared differences.
- The exact exercise IDs with no solution match both witnesses. No solution node was inserted, deleted or moved. The 29 supplied solution nodes represent 48 answer parts: 4 classification lists, 2 model totals, 10 digit-place names, 10 full number names (including the check), 6 numeral-from-word answers, 15 rounding results and 1 qualitative counting/whole-number explanation.
- Reconstructed **22 complete Tamil number names** using an atomic Tamil units/teens/tens/hundreds vocabulary and explicit scale multipliers. Independently decoded the corresponding English number words. Every ordered `(period count, multiplier)` pair matches, not merely its overall sum. For the 10 supplied name answers, also compared with the actual source question numeral; for the six supplied digit answers, compared with the actual solution numeral. The six word questions without solutions were checked for semantic equivalence only; no new solution was inserted.
- Used exact rational arithmetic for the two supplied classification exercises: counting lists 5,125 and 50,221; whole-number lists additionally include 0. Nonintegral fractions/decimals stay excluded. This follows the explicit source/canon convention, not a universal claim that every curriculum defines natural numbers identically.
- Independently calculated the supplied models: `5×100 + 6×10 + 1 = 561` and `4×100 + 0×10 + 7 = 407`. Visually checked all four source block images, including the two with no solution.
- Reconstructed every supplied digit-place answer from its digit's position in 579,601 or 56,804,379; all ten match. The 0 digit's **position** is not confused with its numerical contribution of zero.
- Recalculated all 15 supplied rounding subanswers by comparing distances to lower/upper multiples with the source half-up convention. This includes the source carrying outcomes 1,497→1,500 and 63,994→64,000, all four dollar-place answers for $24,493, and all three China-population answers. Dollar signs and original amounts are preserved.
- Checked the qualitative source answer against the actual page-35 set convention: whole numbers add zero to counting numbers. Checked both time-conversion assumptions explicitly as recorded above.
- U007 reuses an existing SVG; U008's five target SVGs were still pending figure-worker authoring at the numerical QA check. No final asset-closure, rendered typography, PDF, accessibility or standalone learner-readiness pass is claimed here.

Current hashes:

- U007 CNXML: **`b6bb8fb852553579c5d60112fa72ea4acf789e592a2ecbcf7a392d2734f8fbe1`**, 6,700 bytes.
- U008 CNXML: **`d5f6b6de6bd0273f9b0a525af429ec296703502bdb4b4a5d04bc985429fb6f57`**, 40,016 bytes.

The checks establish source/number correspondence, not native idiom or validated mastery. Some compound international number names and proper-name renderings remain provisional. Embedded source MathML punctuation is preserved even where Tamil word order would ordinarily place punctuation differently. Disk space remained above 10 GB during drafting/QA; no disk-full error occurred.

Continuation: end of U008 is `eip-id1168466338968`, then end of `<content>`; the next document-level named source node is glossary definition **`m81243#fs-id2642858`**, owned separately. Reader integration, missing-answer recovery completion, real mastery routing, linguistic/accessibility review and broader A00–A20 coverage remain ongoing work.

### Later asset receipt and final handoff — 2026-08-31

All five U008 SVG targets now exist. A read-only XML comparison confirms each SVG description exactly equals its current CNXML media alternative. The figure worker separately reports the four block counts, six self-check ability rows, 18 blank response cells and font/cell bounds checked, with no assessment totals added to block titles/descriptions. U007's reused chart also exists: its SVG description and source alternative are differently worded but contain the same 15 place labels, five groups, eight leading blanks and 5,278,194; byte-for-byte equality is not claimed for that reused asset. The U007/U008 source hashes above are unchanged. This closes this translation handoff's target-existence and description-content check, not rendered integration, native-language approval or standalone learner-readiness. Actual canon page-35 whole-number wording and page-175 glossary OCR were reconsulted at this final receipt. Available disk space remained above 10 GB.
