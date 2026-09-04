# MR-BRIDGE-026 drafting record

2026-09-01. Writer: unit26_writer. Status: source-faithful Marathi translation draft of the complete m81427 substitution section; not independently reviewed, frozen, built, rendered, teacher-approved, published, or a module/book-completion claim. This worker owned only the026 XML/config/this record and bounded ignored original-image review copies. Root owns freeze/assets, independent review, build/render QA, shared ledgers, staging and any branch export.

## Pinned source and exact boundary

Both complete pinned module members and both complete selected section subtrees were read directly. No HEAD checkout, bulk extraction or new corpus acquisition was used.

|Source|Exact member|Bytes|SHA256|
|---|---|---:|---|
|EN|`osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81427/index.cnxml`|166406|`2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5`|
|ID|`source/modules/m81427/index.cnxml`|168909|`2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112`|

Metadata agrees: content-id `m81427`; UUID `b9f8475e-9490-4f24-995f-2923b1ed9644`; EN title `Solve Systems of Linear Equations with Two Variables`; ID title `Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel`; ID records `xml:lang="id-ID"`.

The assigned boundary is the complete section wrapper `fs-id1167834233994`, EN “Solve a System of Equations by Substitution”, ID “Menyelesaikan Sistem Persamaan dengan Substitusi”; stop before sibling `fs-id1167834222378`. Its 14 direct non-title selectors, in exact source order, are:

```text
fs-id1167834234000
fs-id1167835334266
fs-id1167835334269
fs-id1167827943012
fs-id1167834063721
fs-id1167834301188
fs-id1167835328722
fs-id1167834099143
fs-id1167835363503
fs-id1167830925047
fs-id1167835415479
fs-id1167835415482
fs-id1167826782993
fs-id1167834536415
```

Those selections contain 57 descendant source IDs; including the section wrapper gives 58 source IDs. EN and ID have the same ID order and nearest-selector ancestry. The target has exactly those 58 source IDs in source order plus its own article and credits IDs, so 60 target IDs total, all unique. It has 14 exact `data-source` references, one for each direct selector; the wrapper is retained structurally without a nested source label. All 58 source IDs resolve to the same nearest selected ancestor as in the source.

Coverage is exact: six exercises and six supplied solutions; two worked examples; four Try It notes; one how-to note with six steps; 17 MathML nodes; 12 media/images; one table with eight rows and 16 entries; zero source links. No selected problem lacks a supplied source solution. The target has 14 exact `data-source` references, one for each direct selector. The wrapper retains its canonical source ID, title, content and ancestry without a nested `data-source` marker, matching the established builder convention. The target adds only bidirectional local problem/solution links, four local navigation links, and the usual two external source/licence links in its original-labelled credits.

## Complete mathematical and table checks

All 17 EN/ID MathML nodes were read in order and compared after XML parsing. They encode the repeated opening/example system, four Try It systems and answers, the second worked system, two substitution expressions, `x=5/4`, the first equation, and the repeated solution pair `(5/4,−1/2)`. EN and ID agree on the expressions, signs, fractions, answers and order.

Every supplied result was independently substituted into both equations:

|Item|Supplied pair|Left sides after substitution|Required right sides|Result|
|---|---|---|---|---|
|Worked example 1|`(4,−1)`|`7, 6`|`7, 6`|PASS|
|Try It 1|`(6,1)`|`−11, 9`|`−11, 9`|PASS|
|Try It 2|`(−3,5)`|`−1, 3`|`−1, 3`|PASS|
|Worked example 2|`(5/4,−1/2)`|`4, 8`|`4, 8`|PASS|
|Try It 3|`(2,3/2)`|`−4, 0`|`−4, 0`|PASS|
|Try It 4|`(−1/2,−2)`|`0, 5`|`0, 5`|PASS|

The target has 49 exact checked math strings: all 17 source MathML meanings plus 32 accessible transcriptions from the image-only worked steps. Every `data-check` key occurs exactly once and matches its config value byte-for-byte.

The source table `fs-id1167826998205` remains one eight-row/two-column table with 16 cells. Its image order is deliberately non-lexical and remains exact:

```text
010b, 010c, 010d, 010e, 010f, 010a
```

Rows remain: system image; solve/substitute instruction plus010c; replacement plus010d; solve for x plus010e; substitute `x=5/4` plus010f; ordered pair; check plus010a; final solution. Nothing was sorted by filename.

No numerical or answer correction to either source was required. During final writer QA, one target-only alt transcription was caught and corrected from the impossible intermediate `15/4` to the pixel-accurate `15/2` in figure010a; the following source line `16/2=8` and all target/config checked mathematics were already correct. This is disclosed as a draft repair, not a source correction.

## Actual original-image reading

After exact filenames were established, the only helper write was the permitted named-original review mode:

```powershell
python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-026 A20 CNX_IntAlg_Figure_04_01_009a_img_new.jpg CNX_IntAlg_Figure_04_01_009b_img_new.jpg CNX_IntAlg_Figure_04_01_009c_img_new.jpg CNX_IntAlg_Figure_04_01_009d_img_new.jpg CNX_IntAlg_Figure_04_01_009e_img_new.jpg CNX_IntAlg_Figure_04_01_009f_img_new.jpg CNX_IntAlg_Figure_04_01_010b_img.jpg CNX_IntAlg_Figure_04_01_010c_img.jpg CNX_IntAlg_Figure_04_01_010d_img.jpg CNX_IntAlg_Figure_04_01_010e_img.jpg CNX_IntAlg_Figure_04_01_010f_img.jpg CNX_IntAlg_Figure_04_01_010a_img.jpg
```

All 24 EN/ID originals were personally opened at original detail, not inferred from source alt text or the helper receipt. Review-copy hashes match the extracted exact members.

|Image|EN bytes / pixels / SHA256|ID bytes / pixels / SHA256|
|---|---|---|
|009a|41822 / 818×146 / `e60e5f1ceceae3b4e0d699baeeee3312261e3a869a2582c4fb59e28a2f70fc6c`|88070 / 1540×500 / `1715d39200f25311444a902b703d00021a0638e4aa0240e6ed2ddf393d39274f`|
|009b|38626 / 818×95 / `57d7b4a848363c90cd25c828455afd01da0c27a42591989867d4e42048bc0d07`|85264 / 1540×460 / `95c3d2c8ede0cc819288eac847c95b159789dc192b5f95a5fcefd702c7ff85be`|
|009c|41821 / 818×157 / `5a0f118bcdace3e96db74aa5b94bc84654232cacc92d80dd6fc21f84f5bc7918`|88961 / 1540×520 / `6513c95ac493bf42dc54744ce48ebfc2fff875efa703ff11f09b91c3feea6ca3`|
|009d|43604 / 818×157 / `95771946cbd1901b365d5e9320b3b09036231012bcedcf4468d400f779c10e9a`|93224 / 1540×500 / `8a98759c5aa2c796c567a5ee9155c9e01c101e156f378e34bed990168787d077`|
|009e|28967 / 818×72 / `ed24eb754a4b1a395292ae29c675ed4144f59a4856718299c083f73c2021a489`|65336 / 1540×340 / `6ccac607289a38358df64857985e17649f97b69f085a22ed8eafd2ac952c2ba3`|
|009f|56413 / 818×199 / `5a1505b1327c9aecc2b54c6f74a609b6125434dd2fbaa97f7e3986fd7dc5e9ed`|125663 / 1540×640 / `ee6fa89a39da77c10648d3ab49467b0725dd2c3866223ada83e460366a4bc45e`|
|010b|17872 / 195×43 / `255356d19663a7d38445cf7669ab437ff3a1fb854ddf7a76cb5058c7999d9af6`|64546 / 1240×776 / `66e5303ed5468fefee90dc0a19a5a17b72e40ad3513a76265e9c825ca51290b6`|
|010c|35148 / 195×100 / `cc11a5a5a0cfe2fcf9a990a52e790d7835db49c6ccceb0f2b9dd6026ca612f43`|94727 / 1240×960 / `c56cb21370bdcbd13e2a44336cdf09b3dbecebcf118c7fa719a23d8caa8cc578`|
|010d|18145 / 195×15 / `cba1f32666b3947d745103afff99d2b128c664a6fccff89a35cd97fe57062ef9`|38273 / 1240×448 / `8ca2c74ade8f3a567e3f68d00e08fe41c8a04688dab5d2a600fec304a759927b`|
|010e|35533 / 195×111 / `92e3719364ef59ef144496c2b839e6a71b86747284a987974ea524e3f4e930ef`|104434 / 1240×1092 / `e1d7e60ce393477b2867b3b92c9d7275790696eb2a34f425080eec191827e3ba`|
|010f|33127 / 195×130 / `70a8e249ca6fca1d96566c939fc5bc855b57215e7258c284d14047755ae1e249`|104521 / 1200×1240 / `7a89a70aefb72876bc193cc7ad58f3c71f629dc08820de86669f432cbd7406c0`|
|010a|45701 / 323×179 / `7adfc3ac37e9aa83f9c477d05c6b31830fabab442758a97771f23e3a1a8948f5`|78481 / 1240×815 / `72231763f88d78317148eb6015d3f25cf388d6512709de25bb58c2445f009973`|

The locales are deliberately not byte-identical. EN009a–f are compact English three-column strips with some red circles/arrows/highlight; ID009a–f are larger Indonesian redraws with the same steps and mathematics but without those red emphasis marks. EN/ID010 images have radically different pixel dimensions and resampling/layout, but both show the same expressions, red-highlighted substitutions/results, fractions and final checks. The target references canonical EN filenames and supplies pixel-accurate Marathi alts/visible captions. Config intentionally has no `assets` field before root's freeze.

## Stage-specific Marathi canon use and limits

The current user workflow, canon index, consultation log and terminology ledger were read directly. Canon work was targeted to the exact topic rather than a fresh broad acquisition.

Selection: read C12 local OCR `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt` and personally inspected its physical page image at original detail. The readable text defines `उकल` as the value making both sides equal, defines solving as finding that solution, and requires the same operation on both sides, with a nonzero divisor. Read C13 OCR `balbharati8-86.txt` and its physical page image; the image clearly gives multi-step equation solutions and fractional answers by more than one valid method. Its OCR formulas are corrupt in places, so the physical page and selected mathematical sources, not garbled OCR, govern formulas.

Drafting: reread the complete C12/C13 OCR and the relevant terminology rows T011/T013/T014/T016. Concrete effects were to retain `समीकरण`, `उकल`, `सत्य`, `चल` and `क्रमित जोडी`; distinguish a solution value from the working; make every check explicitly require both equations; and keep fractional operations visible. T014 records `प्रतिस्थापन` only as a provisional working term and requires it to be explained as replacing a variable by a value/expression. The translation does that in the opening prose and six-step note.

Revision/final: reopened and reread both C12/C13 physical pages at original detail after completing source/math/image validation. This final pass retained the two-sided-equation logic and did not silently turn a displayed ordered pair into a proved solution. `रेषीय समीकरणांची प्रणाली`, `प्रतिस्थापन पद्धत` and the complete classroom compound in the title remain transparently authored translations: neither C12 nor C13 attests those full compounds. A visible original-labelled terminology note in the target states that limit. `क्रमित जोडी` and `राशी` remain working ledger terms. No provisional item was silently promoted, no new canon locator was claimed, and no shared canon/terminology file was edited.

## Exact next boundary and writer checks

The immediate next sibling in both sources is section `fs-id1167834222378`, EN “Solve a System of Equations by Elimination”, ID “Menyelesaikan Sistem Persamaan dengan Eliminasi”. Its first direct non-title selector is `fs-id1167834132598`. No elimination content, image or translation was copied into026.

Read-only assertions currently pass:

- parseable XML and JSON; 60 unique target IDs;
- 58/58 exact source IDs in source order and exact nearest-source ancestry;
- 14 unique exact source references for the ordered direct selectors; the canonical wrapper remains structurally present without a nested source label;
- six exercises, six supplied solutions and six bidirectional problem/solution link pairs;
- 49/49 exact config math checks and all six independent equation-pair evaluations;
- 12 exact canonical image references in required source order;
- one table, eight rows, 16 cells, exact non-lexical image sequence;
- required terms present, local anchors resolve, and config has no premature assets field.

No main `freeze_unit.py UNIT`, asset freeze, build, browser, renderer, PDF, shared-ledger/helper/status edit, stage, commit, push, deletion, cleanup or general licence audit was performed. This is writer verification, not independent mathematical or human-language approval. Root must freeze, independently review, build and perform reader QA. The full five-book assignment continues.

Root pre-freeze integration note: after writer release, the shared builder's source-label ordering rule was proven on the immediately preceding section. Root therefore removed only the wrapper's redundant nested `data-source` attribute before freezing this unit. The wrapper ID, title, content, canonical ancestry, all 14 direct selectors, all 58 source IDs, prose, mathematics, answers, images and table are unchanged; config `source_count` correctly remains 14.

Final corrected pre-freeze pins: XML 26973 bytes, SHA256 `f90d539d816a180694a3bca98f128de26ae6d66f21ca90eb8f68b8d6e86c328d`; config 2649 bytes, SHA256 `9760631cd8c11182c0379b86ae7caa0664d2ae007267286c4463f54f41a1d7cb`. Latest observed free space was 5,689,159,680 bytes. This worker performed no cleanup, deletion or move and draws no conclusion from shared-disk changes.
