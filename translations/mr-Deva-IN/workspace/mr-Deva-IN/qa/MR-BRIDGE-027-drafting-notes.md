# MR-BRIDGE-027 drafting record

2026-09-02. Writer: `mr027_writer`. Status: source-faithful Marathi draft of the complete m81427 elimination section. The writer independently recomputed every supplied answer and inspected every bounded EN/ID original, but this is not a freeze, build, rendered-reader approval, human Marathi-teacher approval, publication, or module/book-completion claim. This worker owned only the 027 XML, config, this record, and the 54 bounded ignored review copies. Root owns freeze/assets, independent integration review, build/render QA, shared ledgers, staging and branch export.

## Pinned sources and exact boundary

Both complete pinned module members and both complete selected section subtrees were read directly. No HEAD checkout, bulk extraction, browser/PDF work or new corpus acquisition was used.

|Source|Archive pin|Exact member|Member bytes|Member SHA256|
|---|---|---|---:|---|
|EN|`A20-canonical.zip`, commit `38cae454e644abf9f0a623e876994553881597c9`, archive SHA256 `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`|`osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81427/index.cnxml`|166406|`2f3b5391a9845dc34cccb4c903ee25f2b4f23eceef25ee574d36ebe224b163e5`|
|ID|`A20-v0.3.0-source.zip`, archive SHA256 `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7`|`source/modules/m81427/index.cnxml`|168909|`2efbe62eb5cc35c1e1b51cf591cd52f234d8241c368e86573a3bcb350661c112`|

Metadata agrees: content-id `m81427`; UUID `b9f8475e-9490-4f24-995f-2923b1ed9644`; EN module title `Solve Systems of Linear Equations with Two Variables`; ID module title `Menyelesaikan Sistem Persamaan Linear dengan Dua Variabel`; ID records `xml:lang="id-ID"`.

The assigned boundary is the complete wrapper `fs-id1167834222378`, EN “Solve a System of Equations by Elimination”; stop before sibling `fs-id1167826783829`, EN “Choose the Most Convenient Method to Solve a System of Linear Equations”. The 38 direct non-title selectors, in exact source order, are:

```text
fs-id1167834132598
fs-id1167834132604
fs-id1167835510985
fs-id1167832055312
fs-id1167831911684
fs-id1167835376848
fs-id1167835340855
fs-id1167831847197
fs-id1167835338949
fs-id1167834376400
fs-id1167834063624
fs-id1167835336856
fs-id1167834195035
fs-id1167834193440
fs-id1167828420195
fs-id1167828420197
fs-id1167826997236
fs-id1167831031275
fs-id1167834324678
fs-id1167834121134
fs-id1167834121139
fs-id1167834413553
fs-id1167831031022
fs-id1167831921387
fs-id1167835347820
fs-id1167831835904
fs-id1167831835910
fs-id1167826996182
fs-id1167835163286
fs-id1167830757705
fs-id1167834535350
fs-id1167835309662
fs-id1167831890568
fs-id1167831163799
fs-id1167831163806
fs-id1167832138940
fs-id1167835357545
fs-id1167835379282
```

The EN and ID wrappers each contain 966 XML nodes, 128 canonical IDs, 38 direct selectors, 37 MathML nodes, 12 exercises and 12 supplied solutions, 27 media/images, zero links, and three tables. Their ID order and nearest-selector ancestry are identical. Parsed MathML structures agree apart from localized `mtext`. The target preserves all 128 canonical IDs in exact order and canonical ancestry, plus only article/credits IDs. The 38 `data-source` blocks are direct children of the retained wrapper in the exact order above. The wrapper itself keeps its canonical ID, title, complete content, ancestry and `data-kind="translation"`, with no redundant `data-source` attribute. Config `source_count` is 38.

Coverage is exact: four worked examples; eight Try It exercises; 12 supplied solutions; one seven-step how-to; all 37 source MathML meanings; all 27 source images; and source tables `fs-id1167834536402` at 10 rows/20 entries, `fs-id1167834464514` at 10/20, and `fs-idm340185024` at 5/10. The target adds only 24 bidirectional question/solution links, six local navigation links and two usual external source/licence links. All 30 local links resolve. No source question has an empty or missing supplied solution, and no new question or answer was invented.

## Independent mathematics

Every finite supplied pair was solved independently with exact rational arithmetic and substituted into both equations. The determinant is included to distinguish each unique solution from the dependent cases.

|Item|Supplied result|Determinant|Residuals in equations 1, 2|Result|
|---|---|---:|---|---|
|Worked example 1|`(4,−1)` (image-only source answer)|`−5`|`0, 0`|PASS|
|Try It 1|`(2,−1)`|`−11`|`0, 0`|PASS|
|Try It 2|`(−2,3)`|`−6`|`0, 0`|PASS|
|Worked example 2|`(0,−3)`|`29`|`0, 0`|PASS|
|Try It 3|`(1,3)`|`29`|`0, 0`|PASS|
|Try It 4|`(4,−3)`|`−59`|`0, 0`|PASS|
|Worked example 3|`(3,6)`|`−1/12`|`0, 0`|PASS|
|Try It 5|`(6,2)`|`1/24`|`0, 0`|PASS|
|Try It 6|`(1,−2)`|`−11/30`|`0, 0`|PASS|

The other three systems have determinant zero and all three coefficient/constant ratios equal: worked example 4 ratio `4`, Try It 7 ratio `−3`, and Try It 8 ratio `2`. Each second equation is therefore an exact nonzero scalar multiple of the first and each supplied result “infinitely many solutions” passes. No numerical correction to EN or ID is required.

The target/config expose 64 unique exact `data-check` strings: all 37 source MathML meanings plus 27 accessible transcriptions of image-only mathematics. Every key occurs once and its target text matches the config byte-for-byte. In particular, the non-lexical worked-image sequences preserve `(4,−1)`, `(0,−3)` and `(3,6)` and their checks.

## Parallel-source discrepancies handled visibly

- ID `fs-id1167835338949` joins `y` and `saling` without a space. The Marathi sentence restores the spacing/meaning and an adjacent `data-kind="original"` note names the exact ID and join.
- In ID table `fs-id1167834536402`, `y` and `yang` are joined. The retained 10/20 table restores clear spacing and its visible original-labelled layout note names the exact table, tokens and repair.
- Canonical EN `fs-id1167831163799` contrasts same-line/infinite/consistent with parallel/no-solution/inconsistent. Canonical EN `fs-id1167831163806` then contrasts a true terminal statement (consistent dependent, infinitely many solutions) with a false terminal statement (inconsistent, no solution). ID reorganizes those facts into the first paragraph and compresses the second to the dependent/same-line branch, dropping the false/inconsistent branch there. Marathi preserves both complete canonical EN branches in their canonical IDs. A visible original-labelled note discloses the ID reorganization/contraction and explicitly says it is not a numerical source correction.

## Actual original-image reading

After exact filenames were established, the only helper write was the permitted named-original review mode:

```powershell
python -B mr-Deva-IN/tools/freeze_unit.py --review-images MR-BRIDGE-027 A20 CNX_IntAlg_Figure_04_01_011_img_new.jpg CNX_IntAlg_Figure_04_01_012_img_new.jpg CNX_IntAlg_Figure_04_01_013_img_new.jpg CNX_IntAlg_Figure_04_01_014a_img_new.jpg CNX_IntAlg_Figure_04_01_014b_img_new.jpg CNX_IntAlg_Figure_04_01_014c_img_new.jpg CNX_IntAlg_Figure_04_01_014d_img_new.jpg CNX_IntAlg_Figure_04_01_014e_img_new.jpg CNX_IntAlg_Figure_04_01_014f_img_new.jpg CNX_IntAlg_Figure_04_01_014g_img_new.jpg CNX_IntAlg_Figure_04_01_015b_img.jpg CNX_IntAlg_Figure_04_01_015c_img.jpg CNX_IntAlg_Figure_04_01_015d_img.jpg CNX_IntAlg_Figure_04_01_015e_img.jpg CNX_IntAlg_Figure_04_01_015f_img.jpg CNX_IntAlg_Figure_04_01_015g_img.jpg CNX_IntAlg_Figure_04_01_015h_img.jpg CNX_IntAlg_Figure_04_01_015a_img.jpg CNX_IntAlg_Figure_04_01_016b_img.jpg CNX_IntAlg_Figure_04_01_016c_img.jpg CNX_IntAlg_Figure_04_01_016d_img.jpg CNX_IntAlg_Figure_04_01_016e_img.jpg CNX_IntAlg_Figure_04_01_016f_img.jpg CNX_IntAlg_Figure_04_01_016g_img.jpg CNX_IntAlg_Figure_04_01_016h_img.jpg CNX_IntAlg_Figure_04_01_016i_img.jpg CNX_IntAlg_Figure_04_01_016a_img.jpg
```

All 54 EN/ID copies were personally opened at original detail during selection and again after the XML/config draft. They were not inferred from CNXML alt text or a helper receipt. A final post-revision 54-image pass is recorded below. Exact source-order aggregate evidence:

|Locale|Files|Aggregate bytes|SHA256 over ordered file bytes|
|---|---:|---:|---|
|EN|27|910269|`1a44d00f87c76983b3e23e69d65c0d276d6f58ed383aa11b462d4de43e8765d1`|
|ID|27|2033984|`a009e225f44082b2c332d77473f14ed481ad4e591e23d923c3ac0444fab026df`|

The exact source order is `011, 012, 013; 014a–014g; 015b–015h, 015a; 016b–016i, 016a`. All 54 review files match their extracted exact archive members. There are zero byte-equal EN/ID pairs and zero dimension-equal EN/ID pairs. EN 011–013 are compact 138×52, 104×52 and 110×72 equation crops; ID redraws are 1240 pixels wide. EN 014a–g are 839-pixel-wide English three-column strips; ID 014a–g are 1540-pixel-wide Indonesian redraws. EN 015b–h are 141-pixel-wide equation crops and 015a is 303×60; all ID 015 images are 1240 pixels wide. EN 016b–i are 162-pixel-wide crops and 016a is 289×205; all ID 016 images are 1240 pixels wide.

The pixels agree semantically: 011–013 multiply the first equation by `−2`, rewrite, and obtain `−3y=−6`; 014a–g show all seven elimination steps and the checked image-only result `(4,−1)`; 015b–h,015a show multiplication by 2 and 3, `29x=0`, `x=0`, `y=−3`, and both checks; 016b–i,016a clear denominators with 2 and 6, eliminate `y`, obtain `x=3`, `y=6`, and check both fractional equations. Target image references use the canonical EN basenames in this exact order, with 27 nonempty pixel-accurate Marathi alts and visible captions. Config intentionally has no `assets` field before root's freeze.

## Stage-specific Marathi canon consultation and effects

The user workflow, canon catalog, consultation log, witness lock and durable terminology decisions were read first. Canon consultation stayed narrow to equation-solving and graph/line language and remained separate from source/math/pixel evidence.

Selection: read complete local C12 OCR `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt` and C13 OCR `balbharati8-86.txt`, then personally inspected both locked physical-page images `pages/balbharati8-85.png` and `pages/balbharati8-86.png` at original detail. C12 defines `उकल`, solving, and equal operations on both sides; C13 shows multi-step solutions and clearing fractions. Formula OCR is garbled in places, so the page pixels and selected EN/ID mathematics govern formulas. Fresh readable official search results for C18 [आलेख](https://vishwakosh.marathi.gov.in/24316/) were read through the coordinate-axis and graph prose; fresh C22 [भूमिती](https://vishwakosh.marathi.gov.in/28194/) results were read through “रेषेचा उतार व दोन रेषांमधील कोन”, including parallel lines. These support `आलेख`, `रेषा` and `उतार`, not the complete elimination-system compounds.

Drafting: reread both complete C12/C13 OCR witnesses and their relevant page text, then freshly reread the relevant official C18/C22 search-reader prose. Concrete effects were to retain `समीकरण`, `उकल`, `आलेख`, `उतार`, and the C12-style explicit operation on both sides; keep Latin `x,y` and exact fractions; require every ordered-pair check to satisfy both original equations; and distinguish one solution, no solution and infinitely many solutions. `विलोपन पद्धत`, `समतेचा बेरीज-गुणधर्म`, `सुसंगत/विसंगत प्रणाली`, `अवलंबित प्रणाली`, `रेषीय समीकरणांची प्रणाली`, `क्रमित जोडी`, `विरुद्ध सहगुणक`, `लघुतम सामाईक छेद` and `प्रमाणित रूप` remain authored working classroom compounds unless separately attested. The target's visible original-labelled terminology note says so rather than silently promoting them.

Revision: after complete source, exact-rational, structural and drafting-pixel checks, reread both complete C12/C13 OCR files and reopened both physical pages at original detail. Fresh direct C18/C22 opens returned HTTP 502, so no direct-page reading is claimed; fresh official-domain search results were readable and the relevant complete graph/axis and slope/parallel-line paragraphs were actually read. This pass changed the addition-property sentence to the clearer C12-compatible “दोन्ही बाजूंमध्ये … राशी मिळवली” wording, kept `आलेख`/`रेषा`, improved the coincident-line sentence, made both ID token joins explicit, and retained full canonical EN true/false branches.

Final QA: reread both complete C12/C13 OCR witnesses and reopened both locked physical pages at original detail after the final wording revision. Fresh official-domain search results for C18 and C22 were again readable; the exact axis/graph prose and the slope/parallel-line passage were read, while no inaccessible image formula or unrelated advanced assertion was imported. This final pass confirmed the revised “दोन्ही बाजूंमध्ये” sentence, `समीकरण`/`उकल`/`आलेख`/`रेषा` continuity and the visible limit on authored full compounds. All 54 EN/ID review copies were then reopened once more at original detail in six exact-order batches. Every sign, fraction, step, terminal pair and check still agrees with the target alts/captions and config; no further target change was required.

## Writer checks and exclusions

The first complete structural audit before wording-only revision returned zero errors: source wrappers 966/128/38/37/12+12/27/0; exact 128 target source IDs/order/ancestry; exact 38 direct selectors; wrapper without `data-source`; 12 bidirectional pairs; 27 canonical images; 10/20, 10/20, 5/10 tables; 64 unique target/config math checks; 11 required terms; no `assets`; no duplicate IDs/JSON keys; all local links resolve. A separate read-only audit independently returned the same result and made no edits. The suite is rerun after final wording/notes work.

The next sibling `fs-id1167826783829` and all its descendants are absent as target IDs and source selections. Its literal ID occurs only in the visible original-labelled exclusion disclosure. No main `freeze_unit.py UNIT`, asset freeze, build, browser, renderer, PDF, shared tool/asset/lock/output/ledger/status edit, stage, commit, push, deletion, move or cleanup was performed. The full five-book assignment continues.

Final post-revision read-only assertions pass with zero errors: parseable XML/JSON; source shape 966 nodes/128 IDs; exact 128 target source IDs and ancestry; exact 38 direct selectors; wrapper attributes exactly canonical ID plus `data-kind="translation"` and no `data-source`; 12/12 answer pairs; 64/64 config math checks; 27 nonempty image alts in exact source order; tables 10/20, 10/20 and 5/10; 30 resolving local links plus two external links; all 11 required terms; explicit `saling`, `yang` and EN false-branch disclosures; no premature assets; and exact-rational revalidation of all 12 supplied answers. Final pre-freeze pins are:

- XML: 47,593 bytes, SHA256 `f74b8545d83dc6dc0a3c35a5a77a8e300a229760cb5caeeae984436c793d97f64`
- config: 4,099 bytes, SHA256 `4e7de3df03ee91eeb124197eb9099d28133654a852d1e1b74b367567fe9c97cf`
- review copies: 54 files; EN 910,269 bytes / aggregate SHA256 `1a44d00f87c76983b3e23e69d65c0d276d6f58ed383aa11b462d4de43e8765d1`; ID 2,033,984 bytes / aggregate SHA256 `a009e225f44082b2c332d77473f14ed481ad4e591e23d923c3ac0444fab026df`
