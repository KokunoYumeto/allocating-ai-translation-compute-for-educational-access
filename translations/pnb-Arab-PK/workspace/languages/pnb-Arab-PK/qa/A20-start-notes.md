# A20 opening source study

Status: source study and next-unit canon consultation only. No A20 source excerpt, translation, copied asset, reader or production QA was created. The full A10/A20/A30/B10/B40 workflow remains active.

## Complete opening boundary

The first A20 production unit should be the **complete canonical module `m81357`, Preface**. It is the first module of `col31234`, Intermediate Algebra 2e, and it ends cleanly before `m81358`, the Foundations chapter introduction. Do not shrink it to a short welcome paragraph or attribution footer.

The module contains 194 elements and 66 unique source IDs: 26 sections, 28 title nodes, 33 paragraphs, three lists with 25 items, 38 emphasis nodes, 27 newline nodes and four media/image nodes. It has no MathML, source table, figure wrapper, exercise, solution or link. Under the proposed owner policy there would be 90 text/alt owners—28 titles, 33 paragraphs, 25 items and four alts—but that is a planning count, not a frozen translation manifest.

The entire English module and the admitted Indonesian comparison were read. Their ordered element-name, non-alt attribute, ID and image-src sequences match exactly. Structural equality does not make Indonesian wording canonical.

## Authority and partial comparison coverage

Canonical authority remains OpenStax `osbooks-prealgebra-bundle` commit `38cae454e644abf9f0a623e876994553881597c9`, tree `7907e4c81d43de1c3b6da173f0eb273c01dc5b55`. The canonical collection has 83 unique modules. The admitted Indonesian editable checkpoint is v0.3.0-wip and contains the exact first **48/83** modules through the complete Chapter 7 boundary at `m81441`; its next absent module is `m81442`. Do not regress to the older 28/83 repository manifest and do not claim the comparison is a complete book.

The coordinator reports that research-methodology v1.1.0 withdrew the old global ranking as non-objective. The commissioned translations remain in scope. This source plan does not use the withdrawn ranking as evidence, change the assignment, or auto-replace the pins with the newer catalog candidate.

Existing lock, archive, collection, module and manifest hashes are recorded in `../plans/A20-start.json`. Existing supply and rights evidence is relied on without repeating an audit.

## Asset findings

All four canonical assets were viewed at original detail.

- `tryit.png` is a 34×34 right-pointing chevron. `media.png` is a 34×34 right-pointing play triangle. `howtoicon.png` is a 59×55 person/avatar with a three-dot speech bubble. These three files are byte-identical in the admitted Indonesian tree. Keep their LTR icon geometry; do not mirror them merely because the surrounding prose is RTL.
- `CNX_ElemAlg_Figure_05_01_015_img.jpg` is a 791×257 CMYK JPEG with three panels labelled **Intersecting**, **Parallel** and **Coincident**. The Indonesian file is a different 1600×620 RGB redraw labelled **Berpotongan**, **Sejajar** and **Berimpit**. Its graph geometry and panel order agree, but it is not a canonical-byte substitute.

The graph alt in both editions says full explanatory sentences appear under the panels. The inspected pixels contain only the one-word labels. Preserve the faithful source-alt witness and separately identify any pixel-faithful Punjabi accessibility description; do not claim that the longer sentences are visible image text.

## Source/comparison qualifications

The Indonesian opening adds that the book is a Bahasa Indonesia translation. That phrase is absent from the canonical English source and must not become canonical Punjabi source text. Renderer-authored context may separately identify the Punjabi adaptation.

The chapter outline says `Chapter 8: Roots and Radical`, while the canonical collection says `Roots and Radicals`. Preserve the exact witness and keep any copy clarification separate. Statements about web/PDF access, low-cost print, accounts, partners and instructor resources are dated source voice, not independently refreshed 2026 availability claims.

The future renderer must preserve all reviewer names/institutions, the twelve chapter outline items, answer-availability distinctions, inline icons, emphasis and newline boundaries. Media inside paragraphs needs mixed-content-safe HTML. The wide graph needs a local narrow-screen scroller. No new exercises, answers, service claims or rights determinations belong in the translation.

## Canon reading and limits

The actual supported command was run:

`python -X utf8 languages/pnb-Arab-PK/scripts/read_canon.py --stage next-unit --unit A20-start --ids C01 C02 C04 C09 C10 C11`

Receipt: `../canon/receipts/A20-start-next-unit-20260901T111134877990Z.json`, SHA-256 `fb4490adc562cdb1a5a21b9827bd61c0d782de45f93dcd10bbffd291c8a76cf1`.

C01/C02 informed ordinary Punjabi ability and reader-instruction grammar; C04 plural agreement; C09 reminder wording; C10 separate qualification of source/comparison/image issues; C11 ordinary reason-giving. The inherited application strings inside the starter index are not A20 decisions. This one-author prose canon is not algebra terminology, institutional, mathematical or rights authority. Draft, revision and QA readings, native-speaker review, educator review, assistive-technology review and browser QA remain future work.
