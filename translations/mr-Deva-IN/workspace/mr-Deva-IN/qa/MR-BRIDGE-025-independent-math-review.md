# MR-BRIDGE-025 independent source and mathematics review

Date: 2026-09-01
Reviewer: independent MR025 review lane
Status: **PASS — no source, mathematics, image-description, boundary, provenance, or structural-release correction requested**

This review independently compared the released MR025 Marathi XML and configuration with the complete selected graphing section in both pinned m81427 source modules. I directly read all 39 source selections in both languages, their complete wrapper and next sibling, all 15 supplied problem/solution pairs, all 32 MathML nodes, all six tables, and all 46 original-resolution EN/ID images. I also checked the final lock, canonical EN assets, structural HTML, build receipt, and relevant locked Marathi canon witnesses. The drafting record was consulted only after the independent findings had been established; it was not treated as source or mathematical authority. I did not edit any released unit, configuration, lock, asset, output, receipt, or shared ledger.

## Exact reviewed pins

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `translations/MR-BRIDGE-025.xml` | 62,861 | `a585a299dc9fc23a22fb2735f239a497b28653947a4cc894fe40bf821deeb072` |
| `units/MR-BRIDGE-025.json` | 9,394 | `e78b3bf238c93bfb6871c300ca93df6b336c7b89487cd6c3ccc9f2eac03ecf8c` |
| `provenance/MR-BRIDGE-025.lock.json` | 137,115 | `6d7b76030c218a42dab05e307b06a33d0ddb6d0126912c935b667133072d8878` |
| `output/MR-BRIDGE-025.html` | 1,449,777 | `035ba56c25a5dcfb3655e0f7c0f1473d9916fe5cf36aba037f061589d9d02405` |
| `qa/MR-BRIDGE-025-build-receipt.json` | 9,243 | `78b783c72e76031367551d0a7f3d65839403cab48c25aac6559df7684ede7f67` |
| `qa/MR-BRIDGE-025-drafting-notes.md` | 18,785 | `e42519c35d9959d2436732e304dd02b57a3d1ae4cc332650c3ef13295e0d6e8a` |
| `tools/test_unit25_math.py` | 45,258 | `6af5d511943ef3af9ac635ac333ba3e6574be075d71c0d4f39029359197ecabb` |

The two complete source archives and their exact m81427 members were hashed directly:

| Source | Archive bytes / SHA-256 | m81427 member bytes / SHA-256 |
|---|---|---|
| EN canonical | 537,455,794 / `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917` | 166,406 / `2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5` |
| ID v0.3.0 | 106,658,915 / `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7` | 168,909 / `2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112` |

Both modules identify content-id `m81427` and UUID `b9f8475e-9490-4f24-995f-2923b1ed9644`. Their module titles are “Solve Systems of Linear Equations with Two Variables” and “Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel”.

## Boundary, selectors, IDs, and ancestry

The reviewed source wrapper is `fs-id1167832086919`, titled “Solve a System of Linear Equations by Graphing” / “Menyelesaikan Sistem Persamaan Linear dengan Menggambar Grafik”. Its exact 39 direct non-title children are the 39 ordered lock selections. Across the whole wrapper, the EN and ID trees each have 1,191 elements and the same ordered 154 unique IDs, tags, and nearest-ID ancestry. The Marathi target preserves those 154 source IDs in preorder and nearest-source-ID ancestry; its only additional IDs are `MR-BRIDGE-025` and `credits`, giving 156 unique target IDs.

The corrected final release intentionally has no `data-source` on the wrapper itself because a source-bearing wrapper cannot contain the 39 ordered source-bearing children in the builder. The wrapper otherwise retains its ID, title, content, ancestry, and `data-kind="translation"`; the 39 direct blocks retain the exact `A20:m81427#…` locator order. This is a build-order representation detail, not a scope loss. The final lock contains 39 selections, 78 exact EN/ID serialized fragments, and 110 distinct pinned witnesses; every recorded fragment, source-MathML hash, and local witness was rechecked.

The exact next sibling in both modules is `fs-id1167834233994`, titled “Solve a System of Equations by Substitution” / “Menyelesaikan Sistem Persamaan dengan Substitusi”. It is absent as a target element and as a `data-source` locator. MR025 stops before that sibling.

The source/config accounting is consistent: five worked examples, three definitions, ten Try Its, 15 translated practice items, no original practice items, and no missing-source-answer placeholder. The graphing how-to preserves five top-level steps and all three nested substeps.

## Fifteen supplied answers and independent mathematics

All 15 exercises in each source have a problem and supplied solution. The target retains every exercise/problem/solution ID, one problem-to-answer link, and one solution backlink. I recomputed every system with exact integer/rational determinant arithmetic:

| Pair(s) | Independent result |
|---|---|
| 1–6 | Unique intersections `(4, −1)`, `(3, 2)`, `(2, 3)`, `(−1, 2)`, `(3, 4)`, `(5, −4)` |
| 7–9 | No solution: each pair is parallel with unequal intercepts/constants |
| 10–12 | Infinitely many solutions: each second equation is an exact scalar multiple of the first |
| 13 | (a) no solution; (b) one solution `(-10/11, -13/11)` |
| 14 | (a) no solution; (b) one solution `(0, 1)` |
| 15 | (a) no solution; (b) one solution `(0, 3)` |

These results agree with every supplied EN answer, every supplied ID answer, and every Marathi conclusion/classification. In particular, the final three two-system items correctly distinguish inconsistent/independent systems from consistent systems with one solution. No answer correction is needed.

There are exactly 32 MathML nodes in each source wrapper. With element tails excluded and XML canonicalization applied, the ordered EN and ID concatenations are byte-identical: 19,562 bytes, SHA-256 `3be6e9e04d6225dea6a712fcaa22c4f21b9c8bc612639808e3b3cf920168c12a`. Their mathematical content maps in order to target checks `src-m01` through `src-m32`, including the multirow derivations and slope/intercept comparison tables. The target/config have 58 unique and exactly equal `data-check` values: those 32 source values plus 26 values transcribed from raster equations, intercepts, checks, and conclusions. The raster-derived values were independently compared with the actual pixels and recomputed where applicable.

## Tables, ordered media, and original-image findings

The six source tables occur with these exact row/entry counts, identically in EN, ID, and target structure:

| Table ID | Rows | Entries |
|---|---:|---:|
| `fs-id1167826993913` | 9 | 18 |
| `fs-id1167834537193` | 6 | 12 |
| `fs-id1167835327859` | 6 | 12 |
| `fs-id1167832096973` | 4 | 16 |
| `fs-idm341212944` | 4 | 8 |
| `fs-idm341515088` | 4 | 8 |

The exact 23-image source/target filename order is:

`003_img_new`, `004a_img_new`, `004b_img_new`, `004c_img_new`, `004d_img_new`, `005b`, `005c`, `005d`, `005e`, `005f`, `005g`, `005a`, `006a`, `006b`, `006c`, `006d`, `006e`, `007a`, `007b`, `007c`, `007d`, `007e`, `008_img_new` (all `.jpg` with their full `CNX_IntAlg_Figure_04_01_` prefixes).

I opened all 46 EN/ID originals at original detail. Every source-image record and bounded review copy is byte-exact to its ZIP member. The 23 EN members total 1,035,840 bytes; their ordered concatenation has SHA-256 `8e632558cd50df91bbe6f6cfb71114078de5a3d3e13b9aa1773c3aae45259d5f`. The 23 ID members total 2,119,298 bytes; their ordered concatenation has SHA-256 `fa9eb1e2e8ed58bda192436f934dff180ed58ded32dc1075918824e60965fd79`.

All 23 locale pairs differ in bytes and dimensions and are visually distinct redraws/layouts, not interchangeable duplicates. The ID files are higher-resolution localized redraws/upscales. Images 003, 004a–d, and 008 include Indonesian prose or headings; the other redraws preserve the equation, table, or graph meaning. A concrete layout difference is 004a: the ID pixels omit intermediate formula/slope/intercept working that appears in EN, even though the ID source alt still describes it. The target correctly retains the 23 canonical EN asset bytes, while the Marathi alts transcribe the canonical pixels and disclose genuine locale/layout differences. All 23 committed assets match the EN archive, lock, config, structural HTML data payloads, and JPEG MIME expectations.

The 006e discrepancy is resolved correctly. Both original graphs show the blue line with y-intercept `−2` and the red line/equation with y-intercept `−3`. The canonical EN alt incorrectly says the red intercept is `−4`; the ID alt correctly says `−3`. The target keeps the canonical EN image bytes, gives the pixel-accurate Marathi values `−2` and `−3`, excludes `−4` from the alt, and expressly discloses that source-alt correction. This is the only source image-description correction found; it does not alter the mathematics.

The ID prose defects were also independently located: five missing-space joins after emphasized `y` (`dari` and `yang` in `fs-id1167835418145`, `yang` in each of `fs-id1167831954237` and `fs-id1167835530462`, and `berbeda` in `fs-id1167834191318`) plus duplicated `y` in `fs-id1167832060470` (`x dan y dan y keduanya`). Marathi naturally restores the intended spacing and two-variable meaning, and the target discloses both correction classes without importing the duplicated variable.

## Links, canon, terminology, and released structure

All 41 local target anchors resolve to retained IDs. The only three HTTPS links are the CC BY-NC-SA page and the recorded Marathi Vishwakosh graph and geometry pages; no unexpected source URL was introduced. The required-term list has exactly 13 entries and matches the target/config.

I reread the complete local C12/C13 OCR witnesses and inspected their locked Balbharati physical-page 85/86 PNGs. They support `समीकरण`, `उकल`, applying equal operations to both sides, and explicit equation-solving language. I also checked the local canon catalog, consultation records, and terminology rows for locked C18/C22 evidence supporting `आलेख`, `सहनिर्देशक`, `उतार`, and `संपाती`. No fresh web retrieval was performed in this no-browser lane.

The terminology disclosure is appropriately limited. Full compounds such as `रेषीय समीकरणांची प्रणाली`, `सुसंगत/असुसंगत समीकरण-प्रणाली`, and `स्वतंत्र/अवलंबी समीकरणे` are presented as authored, source-meaning-based working translations, not as verbatim canon attestations. The target explicitly says that human Marathi mathematics-teacher review remains necessary. This PASS therefore does **not** claim native-speaker, teacher, accessibility-specialist, or pedagogical approval.

The final receipt records PASS with 39 selected blocks, 110 witnesses, 58 displayed checks, 41 local links, three optional HTTPS links, 156 unique IDs, and 23 embedded/distinct assets. Structural parsing of the pinned HTML independently found the same 39 source labels and 156 unique IDs; all 23 embedded JPEG payloads decode byte-exactly to the canonical EN sources, and no unresolved `asset:` reference or script element remains. This is structural evidence only.

## Executed regression

Command:

```powershell
python mr-Deva-IN\tools\test_unit25_math.py
```

Final result: **31 tests passed, 0 failures, 0 errors, 0 skips**, in 32.169 seconds on the final recorded run. The suite reopens and hashes both complete archives, reads both complete wrapper scopes, checks all selectors/IDs/ancestry/fragments/witnesses, recomputes all 15 answers, canonicalizes and compares all 32 source MathML nodes, pins all 58 target/config values, validates all six tables and 46 source images, resolves all local links, and binds the final lock/assets/HTML/receipt to the exact release hashes. It also includes adversarial checks for duplicate JSON keys, path escape, invalid JPEG data, unsupported MathML, false system equivalence, Unicode replacement characters, and prohibited active-content elements.

## Limits and conclusion

This PASS establishes source fidelity, exact mathematics, image semantics, provenance integrity, link integrity, correction disclosure, and structural build consistency for the pinned release. In accordance with the assignment, I performed no browser, responsive-layout, PDF, render, typography, clipping, or interactive accessibility review, and I did not freeze or rebuild the unit. The HTML is structurally verified but not visually accepted. MR025 is a bounded graphing-section translation, not the complete m81427 module, chapter, book, or five-book assignment. Within those limits, the released MR025 artifacts require no correction and the next substitution section remains cleanly excluded.
