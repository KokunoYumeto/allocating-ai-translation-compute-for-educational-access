# m81243 glossary translation and outside-content inventory

Date: 2026-08-31. This is a separately scoped seven-definition source translation, not a complete-module or whole-assignment completion claim.

## Witnesses and output

- English: `provenance/m81243.en.cnxml`, SHA-256 `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`; canonical OpenStax commit `38cae454e644abf9f0a623e876994553881597c9`, as recorded in `sources.lock.json`. Glossary starts at line 1148.
- Indonesian: `provenance/m81243.id-ID.cnxml`, SHA-256 `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251`; pinned A00 repository commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`, source release v0.2.7. Glossary starts at line 1133.
- Tamil fragment: `translation/m81243-glossary.cnxml`, SHA-256 `b5076a0b8a1d7a4a375e9d55e16f823480f8d1cc193afe48885e9731f3e86c15`.

Both complete witness roots were inspected, including every child outside `<content>`. The fragment preserves the original `<glossary>/<definition>/<term>/<meaning>` hierarchy, source definition order, and IDs. The only added attribute is root `xml:lang="ta-Taml-IN"`. No source answers, explanations, or additional definition nodes were invented.

## Exact glossary witnesses and decisions

### 1. Coordinate / ஆயம்

Definition `fs-id2642858`; meaning `fs-id2145854`; English meaning line 1151, Indonesian line 1136.

- English term: `coordinate`. Meaning: “A number paired with a point on a number line is called the coordinate of the point.”
- Indonesian term: `koordinat`. Meaning: “Suatu bilangan yang berpasangan dengan suatu titik pada suatu garis bilangan disebut koordinat titik tersebut.”
- Decision: retain the existing U001/terminology-ledger `ஆயம்`, with the defining number-point relationship explicitly stated. The selected canon does not attest this coordinate term; it remains provisional, not native-speaker-approved.

### 2. Counting numbers / இயல் எண்கள்

Definition `fs-id2935860`; meaning `fs-id2567732`; English meaning line 1155, Indonesian line 1140.

- English term: `counting numbers`. Meaning: “The counting numbers are the numbers 1, 2, 3, ….”
- Indonesian term: `bilangan asli`. Meaning: “Bilangan asli adalah bilangan 1, 2, 3,….”
- Decision: retain `இயல் எண்கள்`, matching U001 and canon PDF page 35 / printed page 29. The exact starting sequence is `1, 2, 3, …`; no zero was added and the ellipsis remains.

### 3. Number line / எண் கோடு

Definition `fs-id2711214`; meaning `fs-id2443061`; English meaning line 1159, Indonesian line 1144.

- English term: `number line`. Meaning: “A number line is used to visualize numbers. The numbers on the number line get larger as they go from left to right, and smaller as they go from right to left.”
- Indonesian term: `garis bilangan`. Meaning: “Garis bilangan digunakan untuk memvisualisasikan bilangan. Bilangan-bilangan pada garis bilangan membesar dari kiri ke kanan dan mengecil dari kanan ke kiri.”
- Decision: retain the existing two-word `எண் கோடு`; preserve both directions and both larger/smaller relationships. `காட்சிப்படுத்த` translates the visualization purpose without adding a new activity or constraint.

### 4. Origin / தொடக்கப்புள்ளி

Definition `fs-id3330600`; meaning `fs-id2284600`; English meaning line 1163, Indonesian line 1148.

- English term: `origin`. Meaning: “The origin is the point labeled 0 on a number line.”
- Indonesian term: `titik awal`. Meaning: “Titik awal adalah titik berlabel 0 pada garis bilangan.”
- Decision: retain provisional U001/ledger `தொடக்கப்புள்ளி` and explicitly anchor it to the point labeled `0`. Do not substitute an unattested specialist alternative or imply that every number line begins at zero.

### 5. Place value system / இடமதிப்பு முறை

Definition `fs-id1336470`; meaning `fs-id2263265`; English meaning line 1167, Indonesian line 1152.

- English term: `place value system`. Meaning: “Our number system is called a place value system because the value of a digit depends on its position, or place, in a number.”
- Indonesian term: `sistem nilai tempat`. Meaning: “Sistem bilangan kita disebut sistem nilai tempat karena nilai suatu digit bergantung pada posisi, atau tempat, digit tersebut dalam suatu bilangan.”
- Decision: reuse the corresponding U002 sentence and ledger compound `இடமதிப்பு முறை`. Distinguish `இலக்கம்` (digit) from `எண்` (number) and retain the causal dependency on position. Canon PDF page 20 / printed page 14 attests the component vocabulary; the exact compound remains the existing provisional project choice.

### 6. Rounding / முழுமையாக்கல்

Definition `fs-id2263270`; meaning `fs-id2326485`; English meaning line 1171, Indonesian line 1156.

- English term: `rounding`. Meaning: “The process of approximating a number is called rounding.”
- Indonesian term: `pembulatan`. Meaning: “Proses memperkirakan suatu bilangan disebut pembulatan.”
- Decision: `ஓர் எண்ணின் தோராய மதிப்பைப் பெறும் செயல்முறை முழுமையாக்கல் எனப்படும்.` Canon PDF page 175 / printed page 169 visually confirms `தோராய மதிப்பு` / Estimated Value, `தோராயம்` / Estimation, and `முழுமையாக்கல்` / Rounding off. The U006 translator confirmed compatibility with the current U006 noun and inflection choices.
- Source limitation retained: this terse English/Indonesian definition is broad; not every estimation method is rounding. Do not silently rewrite the glossary into a new rounding algorithm or add a half-way rule here. The source's whole-number half-up procedure belongs to U006, not to an invented glossary node.

### 7. Whole numbers / முழு எண்கள்

Definition `fs-id4338000`; meaning `fs-id1934263`; English meaning line 1175, Indonesian line 1160.

- English term: `whole numbers`. Meaning: “The whole numbers are the numbers 0, 1, 2, 3, ….”
- Indonesian term: `bilangan cacah`. Meaning: “Bilangan cacah adalah bilangan 0, 1, 2, 3, ….”
- Decision: preserve `0, 1, 2, 3, …` and `முழு எண்கள்`. Canon pages 35 and 175 distinguish whole numbers from integers (`முழுக்கள்`); no negative numbers or integer equivalence was introduced.

## Canon consultation record for this bounded work

Read `AGENTS.md`, `USER_INSTRUCTIONS_VERBATIM.md`, `GOAL.md`, `canon/README.md`, and the current `terminology.tsv` before drafting. Actual OCR for pages 35, 175, and 20 was read, then all three corresponding page PNGs were visually inspected to resolve OCR corruption and English/Tamil alignment. The relevant actual OCR excerpts were reread during revision/QA and compared directly with the draft.

| Stage | Actual canon consulted | Use |
|---|---|---|
| Draft | PDF 35 / printed 29 | `இயல் எண்கள்` starts at 1; adding 0 produces `முழு எண்கள்`; continuation is unbounded. |
| Draft | PDF 175 / printed 169 | Confirm whole/integer distinction and the rounding/estimated-value terms from the image, not noisy English OCR. |
| Draft | PDF 20 / printed 14 | Check `இடமதிப்பு`, `இலக்கம்`, and positional-value phrasing against the worked chart. |
| Revision/QA | Actual OCR excerpts from the same three pages, compared with the draft and both glossary witnesses | Recheck terminology, zero inclusion/exclusion, directional wording, and no source-number drift. |

OCR input hashes: page 35 `af5415d3885e7bd4aa096edfab7a9073d39151c048a38b204c2d798987f0cc6b`; page 175 `17546f2815c3077bf5fc2d90d1fca376b6aa4a83fd664e01907b3e5969b2d999`; page 20 `c76fc7d9b9c95a59e0c485f23a948bb1291452a2b67926478fbb42ec74f0f0c3`.

This note holds the consultation/decision record for the subtask because its permitted write scope excludes shared logs and the terminology ledger.

## Structural and mathematical checks

Passed against both witnesses:

- 7 definitions, 7 terms, 7 meanings; 22 elements including the glossary root.
- All 14 source IDs unique, unchanged, and in the same order.
- Element hierarchy and non-language attributes identical to both source glossaries.
- Same mathematical/numeric token sequence: `1, 2, 3, …; 0; 0, 1, 2, 3, …`.
- No MathML, links, images, or source solutions occur in either glossary; none was added.
- XML parses successfully. Native-speaker review and built-reader/render integration are not performed or claimed by this fragment-only task.

## Other material outside content: pending inventory only

The two witness documents each have exactly four root children, in order: `title`, `metadata`, `content`, `glossary`. Outside `<content>`, no further substantive section, footnote, answer set, or media node exists beyond those inventoried below.

| Source location (both files) | Exact material | Disposition |
|---|---|---|
| Root `title`, line 2 | English `Introduction to Whole Numbers`; Indonesian `Pengantar Bilangan Cacah` | Module-level title translation/assembly still pending outside this glossary task. Existing per-unit titles do not themselves constitute assembled module metadata. |
| `metadata/md:title`, line 5 | Same source title in metadata | Pending alongside root title; keep both consistent at assembly. |
| `metadata/md:abstract/para`, line 6, ID `para-00001` | English `By the end of this section, you will be able to:`; Indonesian `Pada akhir bagian ini, Anda akan mampu:` | Opener translation/assembly pending. |
| Abstract `list`, line 7, ID `list-00001` | Six source objectives: identify counting/whole numbers; model whole numbers; identify a digit's place value; use place value to name whole numbers; use place value to write whole numbers; round whole numbers. | All six opener items pending as a separately scoped module-level fragment; no item was added here. |
| `metadata/md:content-id`, line 4 | `m81243` | Preserve unchanged during assembly; not linguistic content to translate. |
| `metadata/md:uuid`, line 15 | `7cbc90c7-60c8-4211-bffe-b77aadc95509` | Preserve unchanged during assembly; not linguistic content to translate. |
| Root `glossary`, English line 1148 / Indonesian line 1133 | Seven definitions, first `fs-id2642858`, last `fs-id4338000` | Tamil fragment drafted and structurally checked; reader/module integration and human linguistic review pending. |

The `<content>` end-of-section material is not “outside content” and was not modified or claimed complete here. No missing source answer was supplied. Only the glossary fragment and this note were authored for this bounded task.
