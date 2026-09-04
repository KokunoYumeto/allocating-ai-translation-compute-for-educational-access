# U002 source translation notes

Scope: A00 `m81243#fs-id2340048`, Model Whole Numbers. Drafted 2026-08-30 by an AI assistant; no native-speaker, educator or educational-efficacy approval is claimed. This file records this bounded translation subtask; build and rendered-output QA belong to the parent task.

## Source and structure

- Read the complete subsection in both committed witnesses, `provenance/m81243.en.cnxml` and `provenance/m81243.id-ID.cnxml`, including the final manipulative-mathematics note. Preserve original element order, identifiers, mathematical numbers/operators, examples and answers. Language-bearing MathML text is translated; the currency text `$100`, `$10`, `$1`, `$374` remains exact. No dollar-to-rupee substitution is made.
- Nine images reference Tamil SVG equivalents under `assets/u002/` with original basenames. The parent task's asset worker owns their geometry and visual verification; this draft does not assert that an SVG has passed review before it exists.
- The two short source solutions remain `176` and `237`. Extra reasoning must stay in the explicitly new companion.
- The final note names the source's Number Line-Part 1 manipulative activity but supplies no activity body or link in this subsection. The translated note is retained, not silently removed or replaced. The parent should identify this dependency or provide a clearly separate self-contained alternative; the note alone does not prove offline activity availability.

## English source accessibility errata

Both English table descriptions are inaccurate: `fs-id1714120` and `fs-id1785447` say there are 3 columns and describe a different header order. Their actual XML has `tgroup cols="5"`, five `colspec` children, and headers Digit / Place value / Number / Value / Total value, followed by three place-value rows and a total row (5 rows including the header).

The Indonesian witness already corrects these descriptions to five columns. Tamil follows the actual table XML and that correction. The first Tamil description identifies the 1/3/8 digits, contributions 100/30/8 and total 138; the second identifies 2/1/5, contributions 200/10/5 and total 215. No table values or cells are changed to fit the old English labels.

## Canon consultation and terminology

Before drafting, read `canon/README.md`, actual Tamil OCR pages 20, 35 and 175, and visually inspected pages 20 and 175 to resolve OCR uncertainty. The reference is SCERT Tamil Nadu Class 6 Term 1 Mathematics, first edition 2018, not an assertion of current syllabus alignment.

- C05/C06, page 20 (printed 14): the actual example uses இடமதிப்பு, இலக்கங்கள் and தீர்வு. Retain ledger forms இடமதிப்பு, இலக்கம் and தீர்வு. Use full terms instead of the reference's abbreviated table headings; no reference numbers or OCR equations are imported.
- C08/C09/C12, pages 35 and 175: retain இயல் எண்கள் and முழு எண்கள் in the final source note. Do not substitute முழுக்கள் (integers).
- Page 175 visually confirms இடமதிப்பு அட்டவணை (Place Value Chart), குறியீடு (Notation), and கிடைமட்டப் பட்டைகள் (Horizontal Bars). These support the ordinary words in இடமதிப்புக் குறியீட்டு முறை and கிடைமட்டப் பட்டை, but do not establish an official compound term for base-ten manipulatives.
- Provisional compounds for parent-led ledger review: இடமதிப்பு முறை (place value system), இடமதிப்புக் குறியீட்டு முறை (place value notation), அடிமானம்-10 கட்டங்கள் (base-10 blocks), நூறுகள் சதுரம் (hundreds square), பத்துகள் பட்டை (tens rod), ஒன்றுகள் கட்டம் (ones block). The source explanation states the 10-to-1 relationships, rather than relying on the unfamiliar compound alone.
- Use நூறுகள் / பத்துகள் / ஒன்றுகள் in table place labels. The third header remains எண் for source Number; a companion may separately clarify that these entries count the groups. கூட்டுத்தொகை translates Sum, retaining the existing equals sign inside `mtext`.
- Sentence order within prose was adjusted around source MathML periods, so punctuation and mathematical-tree order remain intact without Tamil suffixes appearing after a full stop.

## Revision and structural checks

After drafting, reread the actual OCR text for pages 20 and 175 and read the extracted Tamil prose in source order. Retained the attested digit/place-value wording; the manipulative-specific compounds above remain provisional rather than being falsely attributed to the canon.

Read-only comparison passed against both English and Indonesian witnesses: 310 ordered elements, 43 ordered IDs, 51 MathML expressions, 3 source exercises, 9 image references. Non-language attributes remain equal except the declared image source/MIME changes and root language declaration. Mathematical numeric/operator text and attributes are unchanged; the translated `mtext` retains all numeric, currency, hyphen and equals tokens. Both table descriptions name the real five-column layout, and the two short source answers are exactly 176 and 237.

Translation SHA-256 at this check: `a0d56878deb6f36694bf5c54a8aa12710166bbf9a36d758497ece0220360d80b`.

The first console prose-review command encountered the Windows cp1252 output limit after the structural assertions had passed; the prose review was rerun successfully with Python UTF-8 output. No input or output artifact was truncated, and this was not a disk-full failure. Available C: space was checked before authoring (1,424,949,248 bytes) and after the check (1,312,870,400 bytes); no large acquisition, deletion, commit or shared-log edit was performed by this subtask.

Parent next check: validate and render the nine actual SVGs with this translation, include them in the offline reader, and inspect the built Tamil pages. No rendered-output or screen-reader claim is made here.

## U002 recovery companion — 2026-08-30

Created the separate `translation/recovery-u002.xhtml`. Reconsulted actual C05/C06 OCR page 20 before drafting and again during revision; retained இலக்கம், இடமதிப்பு, தீர்வு and explicit worked steps. Read the extracted new Tamil explanations and source-help after writing. The companion is original instructional material, not a substitute translation of the source.

- Four diagnostic items distinguish digit count, digit place/value, grouped quantity, and a zero placeholder. Repair routes select R1 (digit/place/value), R2 (group models) or R3 (zero). No grade placement claim is made.
- Four practice, four mastery and four retry items each have full answer/reasoning and links to the relevant explanation. Every part of a multi-part question must be correct, not merely its final number. The local four-of-four criterion is explicitly not school placement or full-course certification.
- Mastery genuinely infers information from numbers: M1 asks the place and value of 8 in 582; M2 asks the place of 0 and value of 4 in 406, its expansion, and why 46 differs; M3 compares the value of 7 in 271 and 217; M4 constructs a model of 132 without supplying its group counts. Retry uses 376, 508/58, 461/416 and 124.
- The grouping tasks P4/M4/T4 explicitly require fewer than ten ones (and fewer than ten tens where relevant). This makes the canonical-place-value answer unambiguous while avoiding a false claim that alternate regroupings have different values. R3 explicitly allows one hundred to be regrouped as ten tens; it prohibits treating one hundred as just one ten, not valid regrouping.
- R2 supplies executable paper-and-pencil steps for two ten-dot rows plus four dots (24), and a ten-by-ten set of dots (100). Small stones/seeds are optional. Shorter labelled sketches are permitted after explaining what 100/10/1 represent. Speaking aloud, purchasing manipulatives or obtaining an external worksheet is not required; written/model-list alternatives are accepted.
- Source-help explains exactly 176 = 100 + 70 + 6 and 237 = 200 + 30 + 7, linked to the original source exercises. The original short source answers stay unchanged. The US-dollar example remains US dollars; no currency conversion or paid activity is introduced.
- The named source Number Line-Part 1 worksheet is expressly not included or silently reconstructed. Original companion activities are separately identified and fully specified locally. Availability of the named external source worksheet remains a provenance/coverage issue, not a prerequisite for these companion activities.

Read-only checks passed: well-formed XHTML; 45 unique IDs, all prefixed `ta2-`; 16/16 assessment-answer pairs with repair links; 43 fragment links resolved against companion/source IDs; six MathML sum identities and all plain-text additive identities numerically verified; arithmetic-derived digit/place/value spot fixtures for ten answer items and model fixtures for 132/124 checked. There are no new images, scripts, forms or external dependencies. The whole learner path is present, but rendered layout and assistive-technology testing remain parent-task checks.

Companion SHA-256 after the regrouping clarification: `7d2251764964c13308b93c1e7577ef2a956d19619726e89ae3a3cf3be514f75c`.

## Declared visual-adaptation alternative text

The parent requested correction of four alternatives after reviewing the finished SVG redraws. Inspected the actual SVG `title`, `desc` and geometry/text markup for `_002`, `_003_img`, `_006_img`, `_008_img` before editing:

- `fs-id1302206`: the image now uses separate schematic rectangular banknote representations, not overlapping stacks. The Tamil alternative now says three groups of simple rectangular American-banknote models, retaining all source denominations, counts and totals.
- `fs-id2438560`, `fs-id2387933`, `fs-id2164193`: the redraws color matching digits in both upper expressions and lower totals dark red. Arrows are dark teal; other text is dark blue-gray, not literally black. Removed the inaccurate “other parts are black” claim and state that connected upper/lower digits are dark red, while retaining the quantities and exact arrow relationships. The alternatives need not enumerate decorative arrow color to explain the mathematics.
- Only these four language-bearing `media/@alt` values changed in this revision. Recursive comparison against both canonical witnesses was rerun and passed for tree shape, stable attributes, mathematical tokens and values. The witnesses, source IDs and numeric/operator content were not altered.

Current source translation SHA-256 after alt alignment: `fbcfba620c006ba97bb90f15ee6e598ae65953bc7d29a0959b6d80c48e8e7caa`. The earlier source hash above remains the recorded pre-alignment checkpoint, not the current value.

Storage check before companion work: 1,206,550,528 bytes free; before revision: 2,258,550,784 bytes free. This subtask performed no deletion, download, extraction, copy, commit or shared-log edit.
