# m81243 front matter and source assembly

Date: 2026-08-31. Scope: source-faithful module-level title/metadata translation and deterministic assembly of the existing source fragments. This is not a claim that the learner workflow, A00 course, A10/A20 translations, accessibility validation, or whole Grades 2-8 assignment is complete.

## Front-matter witnesses and wording

Both complete source witnesses were read directly at lines 1-16:

- `provenance/m81243.en.cnxml`, SHA-256 `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`, canonical commit `38cae454e644abf9f0a623e876994553881597c9`.
- `provenance/m81243.id-ID.cnxml`, SHA-256 `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251`, pinned A00 repository commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`, source release v0.2.7.

Output: `translation/m81243-frontmatter.cnxml`, SHA-256 `190a493d146d8e943038c9c507cdb2d04042f85886ec7ebe06a22c06e22473b0`.

The file is explicitly marked as a front-matter fragment. Its document root contains only the original root title and metadata; no content or glossary is represented as already present inside this fragment. The original root has no non-language attributes, and none was invented. Only `xml:lang="ta-Taml-IN"` was added. CNXML/MDML element hierarchy and attributes are preserved; source IDs `para-00001` and `list-00001`, content ID `m81243`, and UUID `7cbc90c7-60c8-4211-bffe-b77aadc95509` are unchanged.

| Field | Exact English witness | Exact Indonesian witness | Tamil decision |
|---|---|---|---|
| Root title and metadata title | Introduction to Whole Numbers | Pengantar Bilangan Cacah | `முழு எண்கள்: ஓர் அறிமுகம்` in both locations. `முழு எண்கள்` retains the established whole-number convention; `அறிமுகம்` is attested in canon page 7. |
| Abstract opener | By the end of this section, you will be able to: | Pada akhir bagian ini, Anda akan mampu: | `இந்தப் பகுதியின் முடிவில், உங்களால் பின்வருவனவற்றைச் செய்ய முடியும்:`. This preserves a source learning objective, not a claim of demonstrated learner mastery. |
| Objective 1 | Identify counting numbers and whole numbers | Mengidentifikasi bilangan asli dan bilangan cacah | `இயல் எண்களையும் முழு எண்களையும் அடையாளம் காணுதல்` |
| Objective 2 | Model whole numbers | Memodelkan bilangan cacah | `முழு எண்களை மாதிரிகளால் காட்டுதல்` |
| Objective 3 | Identify the place value of a digit | Mengidentifikasi nilai tempat sebuah digit | `இலக்கத்தின் இடமதிப்பை அடையாளம் காணுதல்` |
| Objective 4 | Use place value to name whole numbers | Menggunakan nilai tempat untuk menyebutkan bilangan cacah | `இடமதிப்பைப் பயன்படுத்தி முழு எண்களின் பெயர்களைக் கூறுதல்` |
| Objective 5 | Use place value to write whole numbers | Menggunakan nilai tempat untuk menulis bilangan cacah | `இடமதிப்பைப் பயன்படுத்தி முழு எண்களை எழுதுதல்` |
| Objective 6 | Round whole numbers | Membulatkan bilangan cacah | `முழு எண்களை முழுமையாக்குதல்` |

Each objective is identical to its corresponding current translated section title, preserving terminology across the source module. No additional objective, grade placement, assessment criterion, or answer was added.

## Canon consultation and revision

Before drafting, actual `downloads/tamil-canon/ocr/page-007.txt` was read and `page-007.png` was visually inspected. PDF page 7 / printed page 1 uses `கற்றல் நோக்கங்கள்` with parallel verbal-noun objectives and the heading `அறிமுகம்`. That informed the parallel `-தல்` endings in the six source objectives without replacing the source opener with a new heading. The actual OCR excerpt was reread during revision and checked against the translated opener/objectives.

Page 7 OCR SHA-256: `bcfa25c16296d82b8c9b6d8c15e6d982225b966387ff45cc99f1fe20f2af242f`.

Relevant pages 35, 175, and 20 had also been read as actual OCR and images during the immediately preceding glossary task. Page 175's actual rounding/whole-number glossary excerpt was reread during this revision: `முழுமையாக்கல்` remains distinct from general `தோராயம்`, and `முழு எண்கள்` remains distinct from `முழுக்கள்`. The existing terminology ledger and all six section titles were consulted directly. The U006/U007/U008 translator confirmed that all eight content fragments were source-ready and confirmed rounding terminology compatibility.

This note carries the bounded task's consultation record; shared logs and the terminology ledger were not edited. Native-speaker or official-board approval is not claimed.

## Assembler

`scripts/assemble_m81243.py` SHA-256: `abd9fbad914c9af6382c4f8a0c86609dbd385696b045314fbc51d4b4a2918282`.

Commands:

```powershell
python ta-Taml-IN/scripts/assemble_m81243.py --check-only
python ta-Taml-IN/scripts/assemble_m81243.py
```

The script joins front matter, the eight content sections below, and the glossary in exact canonical order. It refuses missing/invalid fragments, changed pinned witnesses, unhandled root-level source material, element/ID/attribute drift, mathematical drift, unresolved source targets, missing/remote media, obvious unresolved-authoring markers, or an input change during assembly. Validation precedes output writes. More than 100 MiB free disk space is required for writing.

`--check-only` validates the current candidate inputs and computes candidate bytes without writing. It does **not** compare or certify any previously written assembled-source or receipt file. Its console status says `candidate-inputs-validated-existing-output-not-verified`, labels the digest as `candidate_source`, and reports `existing_output_verified: false`. The written-output identities below were checked separately after normal assembly runs by hashing the actual output files.

1. `fs-id1830385`
2. `fs-id2340048`
3. `fs-id1883656`
4. `fs-id1321580`
5. `fs-id1339359`
6. `fs-id2472737`
7. `fs-id2296006`
8. `fs-id2279009`

Both full witnesses, not just the fragments, are compared with the assembled and reparsed XML. Matching preorder tags **and child counts at every node** establishes the hierarchy, so reparenting with unchanged preorder cannot pass. Language changes are limited to translatable prose/metadata/terms/labels and `xml:lang`; documented media adaptations are the existing local SVG paths/MIME types and Tamil alternatives, including table `aria-label`. Linguistic MathML `mtext` labels may be translated while numeric punctuation/operators and all other MathML structure/tokens remain checked. Tamil prose may move around unchanged inline children; comparing individual XML `text`/`tail` slots would incorrectly reject ordinary Tamil word order. Three-dot and U+2026 prose ellipses are normalized as equivalent typography, including U008's final self-check prompt. Mathematical MathML ellipses are still checked directly.

SVG checks require local files inside `assets`, SVG XML, viewBox, title/description, unique local IDs, and closed local SVG references. They reject `script`, `foreignObject`, and case-insensitive event-handler attributes whose local names begin with `on`, including `onload`. These checks do not replace the separate figure author's visual/mathematical review. The script records all source links and every media occurrence/hash rather than claiming every external source link is available offline.

## Assembly result and tests

- Assembled source: `translation/m81243.cnxml`, 169,344 bytes, SHA-256 `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959`.
- Source receipt: `qa/M81243-source-receipt.json`, SHA-256 `03452c0b3b68b845dde144e45ae1e8081151667cac9a01269859b288e11803e6`.
- Counts: 8 content sections, 6 objectives, 7 glossary definitions, 2,122 elements, 628 unique source IDs, 249 MathML expressions, 88 exercises, 59 source-supplied solutions, 47 image occurrences using 46 unique local SVGs, and 10 source links.
- All canonical source nodes are included. Full source hierarchy/order, stable attributes, MathML signatures, and numeric/ellipsis sequence checks pass against both witnesses. The exact serialized bytes were reparsed and checked again.
- Two consecutive assembly runs produced identical assembled-source and receipt hashes.
- `py_compile` passed.
- Ten in-memory negative cases were rejected: missing fragment, duplicate source ID, changed MathML numeral, missing media, unresolved authoring marker, missing objective, invented solution, unresolved source target, reparenting that preserves preorder/attributes, and an SVG `onload` event handler. These tests did not edit fragment or SVG files. The latter two cases were added after the coordinator's independent review and the final assembly/receipt were regenerated and repeated afterward.

## Source omissions and honest status

The 29 exercises lacking solution nodes in both witnesses are retained without invented answers. Their exact exercise/problem/section IDs are listed in `qa/M81243-source-receipt.json`. They are all in `fs-id2279009`; the other 59 source solutions remain present. A source omission is inventoried rather than treated as an assembly error or silently repaired. Any new answer and reasoning must remain a separately identified companion addition before those items are admitted to a teacher-independent assessment route.

The front-matter pending entries in the earlier `M81243-glossary-notes.md` inventory are now closed at the source-fragment/assembly level. Full-module learner reader integration, answer-complete companion routing, EPUB/PDF production, native-speaker review, external schema validation, and assistive-technology/user checks remain separate. No reader, EPUB, PDF, or commit was produced during this bounded assembly task. Other agents' fragments, shared logs, builders, CSS, and `qa_source_coverage.py` were not edited.
