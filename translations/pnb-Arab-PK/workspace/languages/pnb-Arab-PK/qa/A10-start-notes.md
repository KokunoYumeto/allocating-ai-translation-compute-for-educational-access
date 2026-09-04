# A10 opening-source analysis

This is a planning checkpoint, not a translation or a completed assignment. A10, A20, A30, B10 and B40 remain whole-work assignments. The exact mapping, selected file hashes, source IDs, counts, asset dimensions and canon receipt are in `../plans/A10-start.json`. Paths there are relative to the workspace root.

## Canonical order and proposed start

A10's own `SOURCE_AUTHORITY.md` identifies **col31130**, `elementary-algebra-2e.collection.xml`, at upstream commit `38cae454e644abf9f0a623e876994553881597c9`. The actual collection contains 82 distinct module IDs. Their complete order matches the A10 `SOURCE_AUTHORITY_MANIFEST.csv`; all 82 Indonesian module paths exist. This was not inferred from A20, whose shared repository name is not a sufficient collection identifier.

The beginning is:

1. `m82630`, **Preface**: the first canonical module, front matter. Its title/class and opening structure were inspected, not its full prose reviewed.
2. `m82451`, **Introduction**, in **Foundations**: the first pedagogical chapter-opening module. Its complete English and Indonesian text was read. It consists of one splash figure/caption and one paragraph: 3 source IDs, 0 MathML, 0 tables, 1 image. It is a suitable tiny preceding production unit and remains untranslated.
3. `m82452`, **Introduction to Whole Numbers**: the first arithmetic lesson. Its first section is `fs-id1170655083568`, **Use Place Value with Whole Numbers**.

For the initial arithmetic unit, include the two pre-section content nodes (`fs-id1170655158095`, the be-prepared note, and `fs-id1170655154091`, the introduction), followed by the first section's title and its first twelve content children. End after the complete second Try It, `fs-id1170654885628`; stop before `fs-id1170655113270`, which begins writing numbers in words. This preserves the introductory material and completes counting/whole numbers, ellipsis, number line, place value, the worked example and both practice answers.

The proposed lesson selection has **43 IDs, 2 spacing-only MathML trees, 0 CNXML tables, 2 figure elements, 3 images, 2 links, 1 worked example and 2 Try Its**. The full first section is larger: 33 direct children, 147 IDs including its section ID, 16 MathML trees, 3 CNXML tables and 17 images. The chosen prefix must never be reported as the whole section. The chapter introduction and preface must remain explicit pending work, not disappear from coverage.

## Byte provenance and format

The canonical LF module at `downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml` is 113,967 bytes, SHA-256 `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`. It matches A10's bundled English authority copy and its selected manifest row. The Indonesian comparison is `downloads/extracted/A10/translated/modules/m82452/index.cnxml`, SHA-256 `940ad448d8b2788984f386405131866fe32abb95f0f9c2a901ca1f4e3619a6fb`.

The convenient sparse Windows checkout has CRLF and therefore different raw hashes. For the collection and first three modules, replacing only CRLF with LF gives exact text equality with complete-upstream bytes. No file was normalized. Future frozen witnesses should use the complete-upstream LF bytes; a differing checkout hash must not be mistaken for a new edition.

The source is readable UTF-8 CNXML with embedded MathML; no OCR is needed. The selected English and Indonesian tag/ID/image-src/link-target sequences are identical. Counts were derived from parsed source elements, not independent fixtures. The two selected MathML trees contain only `mrow/mspace width="1.5em"`; nearly all mathematical content here lives in prose and JPEGs. There are two *pictures of tables*, but no source CNXML table in the prefix.

## Renderer findings

Read-only inspection of `scripts/build.py` found concrete A10 reuse blockers:

- The example number parser assumes an underscore-numbered A30 ID. It cannot parse `fs-id1170654981807`.
- Text-only note `fs-id1166423891565` would vanish because the note renderer renders child elements only.
- Worked-example media `fs-id1170655112880` is nested in paragraph `fs-id1170654968077`, after a newline. Current child placeholders exclude media. Simply adding media would still generate block `div`/`p` markup inside a `p`; a mixed-content-safe container is necessary to prevent browser reparenting.
- The source's explicit Solution title would duplicate the automatically inserted solution heading.
- Five term IDs, separate English plural-s emphasis, five-part labels, newline-separated answers, both captions and both links require faithful handling. Punjabi must not inherit the English suffix mechanically.
- Current CLI choices and header attribution remain tied to PNB-001–004 and `A30 / m49301`. A10 needs explicit work/module configuration and a source-bound asset/reference manifest.

No renderer changes or A10 builds were made. A read-only peer independently confirmed the selection boundary and these risks.

## Mathematical and visual findings

The three existing selected JPEGs were inspected at original detail, without editing or copying them. The number line runs 0–6 with **smaller to the left** and **larger to the right**. The two charts show `5,278,194` and `63,407,218`. Preserve their LTR geometry and original bytes; use Punjabi alt and clearly labeled original bilingual keys. Do not mirror them for RTL prose.

Two accessibility discrepancies must be logged during translation:

- `fs-id1170655200451/@alt` agrees with the chart/caption numerals but ends by spelling **seventy-nine thousand**, inconsistent with `5,278,194`. Indonesian spells seventy-eight, agreeing with image/caption. Preserve the English witness and disclose any reader correction explicitly.
- `fs-id1170655112880/@alt` claims a top **Place Value** title row, but the actual worked-example image starts at the grouped Trillions/Billions/Millions/Thousands/Ones row. Indonesian repeats that overdescription.

Keep counting/natural numbers starting at 1 and whole numbers including 0, distinct from all integers. Keep the source's three-digit comma grouping and million/billion/trillion scale; lakh/crore explanation, if useful, must be a labeled addition. Distinguish a digit's place from its numerical contribution: zero still occupies the ten-thousands place in `63,407,218`. Later QA must bind all worked/practice digit-place answers to the actual source, not only compare MathML.

The activity note names **Manipulative Mathematics, Number Line-Part 1** but supplies neither a link nor the activity itself. Preserve the reference without claiming the activity is included.

## Canon reading and limits

The actual script was run at source-analysis time:

`python languages/pnb-Arab-PK/scripts/read_canon.py --stage next-unit --unit A10-start --ids C01 C02 C03 C04 C09`

The script has no `source-analysis` stage, so its supported `next-unit` stage was used. The actual receipt is `canon/receipts/A10-start-next-unit-20260830T212513827741Z.json`, SHA-256 `1edc645b181dc07ce8c290b636ab9c1564a7e0c5dbd4fa27fd64bcceeddf5492`. All local HTML snapshots already existed; the script displayed passages, regenerated ignored text snapshots and wrote this unique receipt. No network acquisition was needed.

The passages read were C01 (Punjabi ability syntax), C02 (reader instruction), C03 (ordinary sequence wording), C04 (plural/quantity-change agreement) and C09 (reminder wording). Their prospective A10 applications are explicitly recorded in the plan. Some receipt application strings are inherited from the existing index and refer to older PNB units; they are not an A10 decision log. This is source analysis only, not a claim that drafting, revision or language QA have happened.

The canon remains a starter prose register reference, not mathematical terminology authority. Punjabi terms for counting/whole numbers, digit, place value and periods need careful provisional choices and topic-specific evidence where available. Native-speaker certification and rendered RTL/mobile review remain pending. Existing supply/license audits were not repeated, and no training data was created.
