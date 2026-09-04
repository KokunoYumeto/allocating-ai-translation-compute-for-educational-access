# A20:m81374 complete-source assembly — author review and reproducibility handoff

Date: 2026-09-01. Status: **assembled translation draft; independent assembly review and reader-format QA pending**. This report and `test_assemble_m81374.py` record assembler-author checks. They are not independent review, browser/HTML/PDF inspection, accessibility certification, native-Marathi or mathematics-teacher approval, completion of A20, or completion of the five-book assignment. No browser or PDF path was used.

## Exact source identity and closed coverage

The output title is **“फलनांचे आलेख”**, for English “Graphs of Functions”, Indonesian “Grafik Fungsi”, content ID `m81374`, UUID `4b2bbf1b-2df7-4b9a-9933-dd70d1fd8ada`. The two raw witnesses were captured once from only their exact already-pinned ZIP members; default rebuilding no longer reads archives.

| Witness | Bytes | SHA-256 |
| --- | ---: | --- |
| `provenance/A20-m81374-assembly/en-m81374.cnxml` | 247,327 | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| `provenance/A20-m81374-assembly/id-m81374.cnxml` | 247,303 | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |

Both witnesses independently parse to **7,223 elements and the same 1,366 IDs in the same order**. Stable, independently source/math-reviewed MR-BRIDGE-012–022 provide respectively `18, 47, 12, 63, 40, 50, 35, 21, 33, 31, 30` nonnested selectors: **380 unique selectors**. Their source subtrees cover 1,352 IDs exactly once, with no overlap. The remaining 14 IDs are structural section wrappers, not untranslated substantive elements.

The assembler hard-pins each of the 11 stable target XMLs, configs and locks by bytes and SHA-256 before using them. It then checks every EN/ID frozen fragment against the complete raw module trees. A changed unit, config, lock, source witness, fragment, notice or asset fails instead of being silently absorbed.

## Wrapper, authored-note, header and footer policy

All 14 source wrappers are rebuilt in source order with one reviewed Marathi heading shell each. The repeated Chapter Review `fs-id1167836524742` is deliberately collapsed to the single MR016 shell; its six topic children come from MR016–021 in their actual source order:

1. Graph Linear Equations in Two Variables
2. Slope of a Line
3. Find the Equation of a Line
4. Graph Linear Inequalities in Two Variables
5. Relations and Functions
6. Graphs of Functions

The complete closed audit found **26 `data-kind="original"` nodes outside selected subtrees, unit headers/footers and other original-role nodes**. Every one is copied exactly once at an explicit before/after source-ID anchor; none is silently dropped or rewritten. These include domain/range qualifications, graph-reading guidance, source-alt corrections, vertical-line/slope/inequality exceptions, contextual nonnegative-domain constraints, supplied-answer counts and attribution boundaries. Their input hashes, anchors and output-signature hashes are in the receipt.

MR013 also has one substantive graph/domain clarification in its unit header. It is outside the 26-node census but is retained explicitly after the objectives. Its two checks—`(−∞, ∞)` and `[0, ∞)`—bring the exact target-check census from 683 selected/outer checks to the audited **685**. This distinction is explicit in the receipt rather than hidden by changing the 26-node count.

Eleven excerpt headers and eleven excerpt footers have individual hashed dispositions. Exactly one module header and one module footer replace them. The module footer preserves author/publisher attribution, the settled CC BY-NC-SA 4.0/component-notice relationship, image and table roles, and the nonreader/nonbook limits. Frozen notice files remain reconstruction inputs; no supply or license audit was repeated.

## Exercises, tables, mathematics and role preservation

All **255 source exercises** retain their original exercise/problem IDs. All **141 supplied solutions** remain source solutions and retain reciprocal local question/answer links. The other **114 questions** retain exactly one explicit source-answer-omission note each. No authored answer is fabricated and no omission is counted as an answer.

The complete source has **481 MathML trees**. The assembled target retains **685 exact reviewed mathematical strings**, with every check key namespaced by its origin unit. Selected-subtree signatures are compared after undoing only documented transport: authored-ID/check namespacing, canonical-asset routing and deliberate same-module link localization. This preserves translation/original/adaptation, source-correction, attribution and answer-role distinctions.

The source has two calculation tables, IDs `fs-id1167836688758` and `fs-id1167836560655`, totaling **7 rows and 14 entries**. Stable MR013 had already represented them as linear paragraph/figure adaptations. The assembly retains those reviewed adaptations, exact canonical table IDs and checked values (`m = −2`, `b = −4`, `(0, 4)`); it does not miscount their rows as exercises or pretend to restore a new table layout.

The self-check retains its original figure and the Marathi accessible adaptation. All **nine rating cells remain empty**; the assembly does not mark a learner's self-assessment.

## Images and link safety

All **149 distinct source image uses** occur once in canonical source order. Each target image name matches the corresponding English source image name. The frozen canonical EN assets total **9,908,130 bytes**; every repository-relative path, byte count, SHA-256 and MIME type is pinned. No external or traversal image route is accepted.

The 15 source links have an explicit policy:

- Six same-module references are local fragments in this complete assembly. Existing local links are retained; MR013's prior cross-unit HTTPS figure link and MR021's module-self link are localized. Every prior href remains a provenance attribute.
- Eight links to m81422/m81423/m81425/m81369–m81373 remain HTTPS and internet-dependent; content not in this module is not falsely localized.
- The one source URL `https://openstax.org/l/37domainrange` remains external.

All other local question/answer routes must resolve to an existing ID; all other accepted outbound routes must be HTTPS. Mutation regressions reject unsafe link and image routes.

## Canon continuity

For this mechanical integration I reread the relevant durable canon-consultation entries for C18/C19/C20/C22 rather than performing a new broad retrieval. They preserve these already-reviewed distinctions: coordinate orientation and graph window versus domain; function/domain/codomain versus actual image set; interval endpoint notation; and finite slope language with separate vertical-line exceptions. I did not promote `मूल्यसंच`, `उभ्या रेषेची कसोटी`, full slope-intercept compounds or other authored classroom phrases to newly attested status, and did not recast prior reviewers' actual external readings as my own fresh retrieval. No translation term or exercise was changed during assembly.

## Deterministic reconstruction and negative tests

Normal commands from the repository root are:

```powershell
python -B mr-Deva-IN/tools/assemble_m81374.py
python -B mr-Deva-IN/tools/assemble_m81374.py --check
python -B -m unittest discover -s mr-Deva-IN/tools -p test_assemble_m81374.py -v
```

`--capture-source` is a bounded bootstrap only and is not part of normal rebuilding once the two raw witnesses exist. The current receipt lists **954 repository-relative reconstruction inputs totaling 13,527,010 bytes**. The portability regression copies exactly those inputs to a temporary language root, confirms there is no `downloads/` tree, forbids `zipfile.ZipFile`, and reproduces exact XML and receipt bytes. It then mutates the raw witness and proves pin drift fails.

The 21-test suite independently covers exact current bytes/status, both raw source trees and metadata, all ID order/ancestry, selector nonoverlap/coverage, every translated selection, wrapper collapse, all 26 outer notes plus the header clarification, exercise/answer roles, MathML/checks, assets, blank ratings, table adaptations, link policy, header/footer dispositions, archive-free portability, pin drift, and staged-write failure behavior. Negative mutations separately reject missing, extra/duplicate and reordered canonical IDs; broken answer navigation and omission roles; changed checked mathematics; changed image routes; unsafe URL/path schemes; duplicate JSON keys; and nonunique IDs.

The first complete run passed 20 tests and exposed one overly strict **test-only** expectation that the nested adapted-table node itself carried the selector root's `data-origin-unit`; content and assembly validation had passed. That assertion was removed without changing assembler/output/receipt bytes, and the corrected table test passed in isolation. The subsequent complete run passed **21/21 in 326.277 seconds, zero skips**.

## Current exact artifact pins

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `translations/A20-m81374.xml` | 588,465 | `c629adb12dd6381b9d219d783f4af055aa1a8c060a9b36dce3bfcb5a39c1172d` |
| `qa/A20-m81374-assembly-receipt.json` | 333,290 | `b9ba76426ed17552d523f6ad192cbb11944efcd85483cfef88289c98f646df16` |
| `tools/assemble_m81374.py` | 48,826 | `3220e1a0164c1a6af71066d3250952cc7773a70a1f6095c0a5fbc3548274b54d` |
| `tools/test_assemble_m81374.py` | 19,452 | `fc564533efd30dbe33d1de50aae1acdae9abbb9fa50ca90857e768594013be00` |

This is complete **source representation for m81374**, not reader acceptance and not a complete assigned book. Independent assembly review, a separately authorized format build and all required format-specific inspection remain separate. The five-book goal stays active.
