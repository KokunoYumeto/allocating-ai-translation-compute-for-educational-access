# Indonesian mathematics program: bounded public-state audit

**Audit date:** 2026-08-30  
**Scope:** read-only audit of public GitHub and linked immutable public editions; no local corpus scan, no repository mutation, and no publication action.  
**Primary program commit:** [`a6ae2e3c9a1abb77132a0028414780c9976e48e4`](https://github.com/KokunoYumeto/program-matematika-indonesia/commit/a6ae2e3c9a1abb77132a0028414780c9976e48e4), committed 2026-08-29T23:22:36Z; tree `8af14afd24bdac9334a1afcd9e09125acae9639f`.  
**Primary Open Logic commit:** [`07b25e1329a95a0ace266533f32f3671c2cef95e`](https://github.com/KokunoYumeto/OpenLogic-id/commit/07b25e1329a95a0ace266533f32f3671c2cef95e), committed 2026-08-18T19:40:00Z; tree `8f226083b69c305fe12532ae0ad4072d4ea8b4a0`.

## Executive result

1. **This is an Indonesian mathematics program, not an Indonesian “pilot.”** The pinned public repository defines a 40-role open mathematics curriculum from foundations through research preparation. All 40 roles have selected corpora or frozen original specifications and none is unresolved. The word *pilot* in a few machine records names bounded backend-schema trials, not the educational program or its Indonesian-language corpus.
2. **The current live public state is 27/40 complete course roles and 13/40 production roles.** That is **67.5% complete by course-role count**, which substantiates “about 70%.” There are no `planned` or unresolved roles in the effective 40-role map.
3. **The static v0.62.0 catalog is an older boundary, not the current live boundary.** It records 21 published and 19 production roles. Applying the public live-publication overlay at the pinned commit changes six roles to `published`: A10, B50, C90, D50, D70, and D80. The deterministic result is therefore 27 published and 13 production.
4. **The repository README is itself one role behind the executable public data.** At the same commit, prose says 26 complete roles, while `docs/courses.js` materialized with `docs/live-course-publications.js` yields 27. The executable overlay and its exact role states are used below; the 26-role prose count is treated as stale.
5. **The public page claim is verified and conservative.** Distinct publicly readable PDF editions/checkpoints with exact page evidence sum to **26,286 rendered pages** when every distinct reader, problem book, workbook, and donor PDF is counted once. A stricter content-overlap-safe lower bound is **26,031 pages**, obtained by omitting the separate 255-page Random mathematical-statistics donor PDF because 27 source pages from that donor are also incorporated into the D30 composite reader. Both totals exceed 25,000.
6. **Open Logic is publicly closed at 722/722 editable targets.** The exact manifest contains 722 ordered rows, `OLP-0001` through `OLP-0722`, with source and target paths, byte counts, line counts, and SHA-256 values. The linked canonical reader reaches 642 of those modules; the other 80 are non-reader source modules retained in the editable source package. The public PDF has 1,116 pages.

## 1. Authority and reconciliation method

The effective course map was reconstructed from two exact files at the program commit:

- Base generated course projection: [`docs/courses.js`](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/a6ae2e3c9a1abb77132a0028414780c9976e48e4/docs/courses.js), Git blob `49b3cb1316972a1c73e968264e1aee2de53e7480`, 60,649 bytes, SHA-256 `a2da8a4165326dc64acb5ddd9b1bc227980d48b5e28928d927ec35c1cbc001a5`.
- Live owner-publication overlay: [`docs/live-course-publications.js`](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/a6ae2e3c9a1abb77132a0028414780c9976e48e4/docs/live-course-publications.js), Git blob `f30347d448941713080c0e486dd616e8205030c7`, 31,062 bytes, SHA-256 `2af9c3b703673cc598bf23ec3baac51cf14171e8f41dbc10c04bb69a8e6b9684`.

The overlay's own `materializeLiveCourses()` function was applied to the 40 base records. This produces 27 `published` and 13 `production` records. The older snapshot authorities remain useful for provenance:

- [`backend/authority/catalogs/program-matematika-indonesia-catalog-v0.62.0.json`](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/a6ae2e3c9a1abb77132a0028414780c9976e48e4/backend/authority/catalogs/program-matematika-indonesia-catalog-v0.62.0.json), Git blob `d3e3dc0c5b07f077d98341bd16beb3990d06d8b7`, 61,557 bytes, SHA-256 `3b3c14bbc66b1c7d64c1d43edb0382e21149f1f7746d8c26748e8a89908a5bd7`.
- [`backend/authority/curriculum-authority-v1.json`](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/a6ae2e3c9a1abb77132a0028414780c9976e48e4/backend/authority/curriculum-authority-v1.json), Git blob `bb8e8b032abcea1effc8edb859e9554ca9c28365`, 81,771 bytes, SHA-256 `d36c6efda20720dd3e0b4a78ee8d33fcd5764014a4fba6a4bb27419ba2dfc7c4`.
- [`README.md`](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/a6ae2e3c9a1abb77132a0028414780c9976e48e4/README.md), Git blob `b58849b29e2f5d2edcbed742a8c81b14038e659c`, 9,601 bytes, SHA-256 `972a9b6d203adb6aeb68c3b0604999efb1cdfb523017206848ed7a66df2fa914`.

## 2. Exact 40-role state and public page extent

### Counting rule

- A public PDF is counted once by exact edition identity.
- A distinct problem book, worked-answer book, laboratory manual, workbook, or donor reader is counted when it contains distinct learner material.
- C30 and C40 share one Judson PDF; its 392 pages are counted once under C30 and as `+0 shared` under C40.
- D40's 42-page HTML/MathML pagination and D80's 864-page offline-HTML pagination are alternative renderings of already-counted PDF content and are not added.
- ZIP/source/backend entries carrying a UI `pages: 1` sentinel are not learner-page counts and are not added.
- D100's 554 pages are 504 pages for the complete first volume plus a distinct 50-page second-volume checkpoint; the overlay's aggregate is not added again.
- The table's main total omits the separate 255-page C140 Random donor PDF because part of that donor is embedded in D30. Adding that distinct physical PDF gives the artifact total.
- Unpublished translated units, local canonical candidates beyond the public boundary, HTML-only surfaces without a page count, and source modules outside a reader build contribute zero here. Consequently the result is a public rendered-page lower bound, not an estimate of all work performed.

| Role | Effective state | Course role | Exact public boundary at pinned commit | Non-overlap page contribution |
|---|---|---|---|---:|
| A00 | published | Praaljabar dan Fondasi Kuantitatif | Complete OpenStax Prealgebra 2e reader | 3,016 |
| A10 | published | Aljabar Dasar | Complete 82/82 modules | 2,154 |
| A20 | production | Aljabar Menengah | 48/83 public modules; 66 translation-bearing | 1,977 |
| A30 | production | Prakalkulus dan Trigonometri | 49/87 public modules; 87 translation-bearing | 1,501 |
| B10 | published | Pembuktian, Logika, dan Struktur Diskrit | Complete seven-chapter reader | 613 |
| B20 | published | Kalkulus Diferensial | 442-page text + 646-page problem/solution book | 1,088 |
| B30 | production | Kalkulus Integral | Public WIP.18 through §3.7 | 1,203 |
| B40 | published | Aljabar Linear | 580-page text + 435-page worked answers + 109-page Sage lab | 1,124 |
| B50 | published | Kalkulus Multivariabel | 410-page text + 534-page problem book | 944 |
| B60 | published | Kalkulus Vektor | 316-page text + 486-page problem book | 802 |
| B70 | production | PDB dan Sistem Dinamika Pengantar | Nonlinear-systems chapter checkpoint; not full B70 | 40 |
| B80 | published | Komputasi Matematis dan Eksperimen Reprodusibel | Complete 14-unit reader | 159 |
| B90 | published | Probabilitas Berbasis Kalkulus | Complete Grinstead–Snell edition | 554 |
| B95 | production | Statistika Terapan dan Analisis Data | Public boundary B024, through §6.3 | 253 |
| C10 | published | Analisis Real I | Complete Volume I | 334 |
| C20 | production | Analisis Real II | Through §11.8.1 | 226 |
| C30 | published | Aljabar Abstrak I | Shared complete Judson edition | 392 |
| C40 | published | Aljabar Abstrak II | Same 392-page Judson PDF as C30 | +0 shared |
| C50 | production | Analisis Kompleks | 50 public units, but no standalone reader/page extent | 0 |
| C60 | published | Teori Bilangan dan Kriptologi | Complete reader | 138 |
| C70 | published | Kombinatorika Terapan | Complete reader | 350 |
| C80 | published | Logika Matematis, Teori Himpunan, dan Komputabilitas | Open Logic 722/722 source targets; 1,116-page linked reader | 1,116 |
| C90 | published | Topologi Himpunan-Titik | Complete 20/20 chapters + eight supplements | 645 |
| C100 | published | Geometri | 226-page main course + distinct 276-page workbook | 502 |
| C110 | published | Analisis Numerik | Complete 31/31-unit reader | 387 |
| C120 | published | Pemodelan Matematis dan Dinamika Nonlinear | Complete 22-source-unit + four-bridge reader | 355 |
| C130 | published | Optimisasi Linear dan Integer / Riset Operasi | Complete reader | 666 |
| C140 | production | Statistika Matematis | 219-page main reader; 255-page Random donor omitted from non-overlap total | 219 |
| D10 | production | Ukuran dan Integrasi | 509/672 official source pages represented in 545-page reflow reader | 545 |
| D20 | published | Analisis Fungsional | Complete 17/17 chapters | 298 |
| D30 | production | Probabilitas Teoretis-Ukuran dan Proses Stokastik | Checkpoint 35 composite reader | 340 |
| D40 | production | Persamaan Diferensial Parsial | Unit-13 PDF; alternative 42-page HTML pagination excluded | 193 |
| D50 | published | Lipatan Mulus dan Geometri Diferensial | Complete corrected edition | 712 |
| D60 | production | Topologi Aljabar | Roberts 30/30, Fomberg §§1.1–1.13, labs 4/4; capstone/metadata remain | 558 |
| D70 | published | Aljabar Pascasarjana | Complete four-component package | 716 |
| D80 | published | Teori Kategori dan Metode Homologis | Complete 146/146-unit PDF; duplicate offline HTML excluded | 864 |
| D90 | published | Optimisasi Lanjut dan Analisis Konveks | Complete integrated reader | 141 |
| D100 | production | Jembatan Geometri Aljabar | 504-page first volume + 50-page BGK checkpoint | 554 |
| D110 | published | Matematika Terformalisasi dalam Lean | Complete reader | 219 |
| D120 | published | Membaca Riset, Eksposisi, dan Kerja Matematis Reprodusibel | Complete nine-unit PDF | 133 |
| **Total** | **27 published / 13 production** | **40 roles** | **Known public pages, content-overlap-safe lower bound** | **26,031** |

### Page totals

| Total | Pages | Interpretation |
|---|---:|---|
| Published-role pages | 18,422 | Distinct public material assigned to the 27 complete roles, with C30/C40 and alternative renderings de-duplicated. |
| Production-role pages, strict | 7,609 | Current public checkpoints for the 13 production roles, excluding the separately published 255-page C140 donor. |
| **Strict non-overlap public lower bound** | **26,031** | Recommended conservative figure when discussing extant program pages. |
| Separate C140 Random donor PDF | +255 | A distinct physical reader, omitted above because D30 explicitly incorporates 27 source pages from this donor family. |
| **Distinct-public-artifact total** | **26,286** | Every distinct public learner PDF counted once; no identical file, mirror, shared role edition, or backend/source ZIP counted twice. |

The strict result is 1,031 pages above 25,000; the distinct-artifact result is 1,286 pages above 25,000. Thus “roughly 25,000 pages” is supported by public evidence and is slightly conservative. The count does **not** include unpaged HTML-only material, 80 non-reader Open Logic modules, or translated/integrated work beyond each public boundary.

### Page-count evidence added outside the central overlay

Most page counts are explicit in the pinned live overlay. Four central entries required direct public-edition verification, and one C140 donor required its own exact receipt:

- **B10:** 613 pages. Public PDF `00_MATEMATIKA_DISKRET_EDISI_KEEMPAT_BAHASA_INDONESIA_READER.pdf`, 3,766,386 bytes, SHA-256 `13d977bcd23ade780379e385499a2afa7d344900efdcbdd0eb56401120594bc0`. The independent repository README at commit [`e94905932301e699b7c4d44e88ec54e972b886b6`](https://github.com/KokunoYumeto/discrete-mathematics-open-introduction-id/commit/e94905932301e699b7c4d44e88ec54e972b886b6), 2026-08-22T20:03:44Z, states the same page count; README blob `1160f8b633d3ddf71a5284218f4d3ea84401b0b4`.
- **C30/C40:** one shared 392-page PDF, counted once. GitHub release asset `ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.21.1.pdf`, 1,841,875 bytes, SHA-256 `578ae35cbfd6032dc9a3b4196523c7d2a85dc380ac65e213a005f0422fcf7183`; source repository commit [`2a733794113add911052a8975c3bb9612bfdb137`](https://github.com/KokunoYumeto/abstract-algebra-theory-and-applications-id/commit/2a733794113add911052a8975c3bb9612bfdb137), 2026-08-21T12:47:33Z.
- **C80:** 1,116 pages. Public PDF 5,593,664 bytes, SHA-256 `bf538d5e1994a7a7600703c9d24616696f77e43e9312fb51078095ff0c963c0a`; details in §3.
- **D120:** 133 pages. PDF `kerja-matematika-yang-dapat-ditelusuri-id-2026.08.24.pdf`, 590,742 bytes, SHA-256 `2bfda5d095913829da095ac930d8f1aa61613bfb46c2375970183cb77acdefbb`. The exact page count and hash are in [`qa/PDF_QA.json`](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/blob/cea42b799b038fcac6f9762386d2e8eecd5b1372/qa/PDF_QA.json), blob `9b3e1f44ba6a9716e78fde43c7024a555cd0e5e7`, and [`qa/PDF_VISUAL_QA.md`](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/blob/cea42b799b038fcac6f9762386d2e8eecd5b1372/qa/PDF_VISUAL_QA.md), blob `71cff2f77615233a30e2bca6974cb18f2b0a0b80`, at commit [`cea42b799b038fcac6f9762386d2e8eecd5b1372`](https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id/commit/cea42b799b038fcac6f9762386d2e8eecd5b1372), 2026-08-24T02:55:09Z.
- **C140 Random donor:** 255 pages, 118,920,837 bytes, SHA-256 `556a589cfdd54c9a7e7b5022976371ce31b68e11f947484bbc40cf7a6849a5bc`. Exact evidence is in [`build/PDF_READER_RECEIPT.json`](https://github.com/KokunoYumeto/mathematical-statistics-id/blob/5f595cc1055ddf3e6f3bf303666bba19662df573/build/PDF_READER_RECEIPT.json), blob `28ffea9eb4641e13fda707677162c998ff803f63`, at commit [`5f595cc1055ddf3e6f3bf303666bba19662df573`](https://github.com/KokunoYumeto/mathematical-statistics-id/commit/5f595cc1055ddf3e6f3bf303666bba19662df573), 2026-08-24T06:35:40Z. It is included only in the 26,286 distinct-artifact total.

## 3. Open Logic 722/722 audit

### Exact closure evidence

- [`source/locale/id/TRANSLATION_MANIFEST.csv`](https://github.com/KokunoYumeto/OpenLogic-id/blob/07b25e1329a95a0ace266533f32f3671c2cef95e/source/locale/id/TRANSLATION_MANIFEST.csv): Git blob `ea24d3be4c58ecf61a72596c92c76e10dc364b28`, 251,763 bytes, SHA-256 `3019e1a0b4831e1f6d8e55bf3b3021d9858cd5eb7f0ac482510c30f65337b067`.
- The manifest parses to exactly **722 data rows**.
- First row: `closure_id=OLP-0001`, `stable_order=1`, source `content/open-logic-about.tex`, target `locale/id/content/open-logic-about.tex`.
- Last row: `closure_id=OLP-0722`, `stable_order=722`, source `content/sets-functions-relations/size-of-sets/size-of-sets.tex`, target `locale/id/content/sets-functions-relations/size-of-sets/size-of-sets.tex`.
- Every row records the exact frozen source commit `9620cc73f9c8e0ad003c514a5d3748f29611c4c0`, source and target SHA-256, bytes, and physical line counts.
- [`evidence/COMPLETE_0722_CLOSURE_REPLAY.json`](https://github.com/KokunoYumeto/OpenLogic-id/blob/07b25e1329a95a0ace266533f32f3671c2cef95e/evidence/COMPLETE_0722_CLOSURE_REPLAY.json): Git blob `e77e55ab80adc08bfa1fc29558a432aafd20cf35`, 3,169 bytes, SHA-256 `9a4d4b42140108666db2a50dd26868f6f70d7295e672cf3dc5a51bc2f6fb6d1b`.
- Replay results: 0 missing targets, 0 source-hash mismatches, 0 target-inventory-hash mismatches, 0 control-character files, 0 brace-delta mismatches, and 0 localized `olfileid` policy failures. The replay retains enumerated structural/semantic-difference review surfaces rather than silently discarding them.
- [`evidence/QA_STATE.json`](https://github.com/KokunoYumeto/OpenLogic-id/blob/07b25e1329a95a0ace266533f32f3671c2cef95e/evidence/QA_STATE.json): Git blob `873f1ab20ebfce25a417f5ad6de3eb8ba78d3f26`, 4,318 bytes, SHA-256 `70d0edd51c34b617a336f41336241c72dab9134144814ad0d6165aa3ee36fdce`. It records `coverage=OLP-0001 through OLP-0722`, 722 manifest rows, translation/writer batch checks 722/722, and the exact public reader identity below.

### Reader identity and scope distinction

- [`reader/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf`](https://github.com/KokunoYumeto/OpenLogic-id/blob/07b25e1329a95a0ace266533f32f3671c2cef95e/reader/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf): Git blob `40c268a1fd1f63e0d90c2c91577b20afe892a8d9`, 5,593,664 bytes.
- Public PDF SHA-256: `BF538D5E1994A7A7600703C9D24616696F77E43E9312FB51078095FF0C963C0A`.
- Public PDF extent: **1,116 pages**.
- The repository's pinned [`README.md`](https://github.com/KokunoYumeto/OpenLogic-id/blob/07b25e1329a95a0ace266533f32f3671c2cef95e/README.md), Git blob `dda666bce26b123b324c4bf50e1a151a75a038d2`, 5,187 bytes, SHA-256 `ce1be7d8904f38a3c6bac41ce1b2ac369aad963e2db7644dc3eff07bf2c8f821`, distinguishes **722/722 editable translation targets** from **642 modules reached by the canonical linked-reader build**. The remaining 80 are deliberately retained non-reader modules, not missing translations.
- A historical local package receipt at the same repository records an earlier pre-publication PDF identity (5,591,857 bytes and a different SHA-256) and explicitly says it does not claim publication/readback. It must not supersede the current public PDF. The direct public bytes, current README, repository blob, and current QA state all agree on 5,593,664 bytes and the `BF538…` SHA-256 above.

## 4. What “complete program” can and cannot mean at this public boundary

The public evidence supports three separate completion statements:

1. **Curriculum design completion:** 40/40 course roles have selected corpora or frozen original specifications; 0 unresolved roles. This part of the program map is complete.
2. **Open Logic translation completion:** 722/722 editable targets exist and replay against the frozen source closure.
3. **Public course-edition completion:** 27/40 course roles are marked published after applying the live overlay; 13/40 remain production. The exact share is 67.5%, or approximately 70%.

It would therefore be inaccurate to describe the overall undertaking as a small pilot. It is a large, public, multi-course Indonesian mathematics program with more than 26,000 auditable public rendered pages. It would also be inaccurate to claim that all 40 course editions are already complete: the live state still marks A20, A30, B30, B70, B95, C20, C50, C140, D10, D30, D40, D60, and D100 as production.

The backend files that use labels such as `pilot_validated` describe experimental federation/schema layers over selected courses. Those labels do not downgrade the program, translations, or published readers to pilot status.

## 5. Explicit unknowns and nonclaims

- This audit does not estimate token use. Public curriculum catalogs and edition manifests do not expose session-level cached/fresh token accounting, so a token figure must come from task/provider usage receipts rather than page counts.
- The 26,031-page strict total excludes unpaged HTML-only material and all nonpublic/local production beyond the public course boundary; it is a lower bound on extant program material.
- The 26,286-page artifact total counts distinct public PDFs, not unique mathematical propositions. It removes known identical/shared/mirrored artifacts; topical overlap between different textbooks is not treated as duplication.
- C50 has 50 public units but no standalone page extent in the pinned catalog/overlay, so it contributes zero rather than an invented page estimate.
- Page counts are physical rendered pages. Different reflow systems produce different pagination and should not be converted directly into source-word or token counts.
- Course-role count and page count measure different things. A 67.5% role-completion rate does not imply 67.5% of all source pages, translation tokens, exercises, or QA effort.

## 6. Reproducible arithmetic

The exact table contribution vector has 40 entries and sums as follows:

```text
published roles: 18,422 pages
production-role public checkpoints, with C140 donor omitted: 7,609 pages
strict non-overlap total: 18,422 + 7,609 = 26,031 pages
distinct C140 donor reader: 255 pages
distinct-public-artifact total: 26,031 + 255 = 26,286 pages
```

The completion arithmetic is:

```text
published: 27 / 40 = 67.5%
production: 13 / 40 = 32.5%
planned or unresolved: 0 / 40 = 0%
```

