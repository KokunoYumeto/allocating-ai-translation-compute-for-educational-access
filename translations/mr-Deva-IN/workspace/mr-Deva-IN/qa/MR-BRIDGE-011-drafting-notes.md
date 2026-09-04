# MR-BRIDGE-011 drafting and source-fidelity record

2026-08-31. This draft supplies the complete source working for the four m81373 blocks previously condensed in the historical MR-BRIDGE-001 pilot. It is a replacement representation for prospective module assembly, not new unique source coverage, not a whole-module completion claim, and not a ready-reader claim. The full five-book assignment remains active.

## Exact scope and intentional overlap

Canonical source order, independently read from both pinned module members:

| Source selector | Content | Original IDs |
| --- | --- | ---: |
| A20:m81373#fs-id1167836692527 | Relation example: domain and range of five ordered pairs | 10 |
| A20:m81373#fs-id1167836521479 | f(x)=2x²+3x−1 evaluated at 3, −2 and a | 26 |
| A20:m81373#fs-id1167829859398 | g(x)=3x−5 evaluated at h² and x+2, then g(x)+g(2) | 27 |
| A20:m81373#fs-id1167833175472 | Complete relation glossary definition and meaning | 2 |

All 65 original IDs occur exactly once and in original relative order. This restores the 61 nested identities not present in MR001's condensed representations, while preserving their four selected outer IDs. There are three original exercise/problem/solution trees, six tables, 28 media identities and the glossary meaning `fs-id1167833175475`.

The local config correctly reports four selected blocks, three worked examples and one definition for this unit. Its contribution to the already-selected module's unique-selector count is **zero**, not four. The three source solutions are preserved supplied solutions, not newly authored answers. No practice items are added. Module assembly must choose MR011 for these four blocks and exclude the corresponding MR001 adaptations from the assembled source representation; it must not concatenate both or count them twice. MR001's other six selections and its original bridge questions are outside this replacement. That future assembly is root-owned and not performed here.

Legacy XML remains SHA-256 `367314e8948ae28ba17de187ebca4e09d294e2c472a20c433538adb8dd06aac9`, matching the existing receipt. No legacy XML, output, config, CSS or build file was edited or rebuilt.

## Source reads and authority

Selected reads only; no archive was downloaded or fully extracted.

- EN: `downloads/mr-Deva-IN/releases/A20-canonical.zip`, member `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`; verified module SHA-256 `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID: `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip`, member `source/modules/m81373/index.cnxml`; verified module SHA-256 `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.
- Read the complete selected EN and ID questions, solution prose, nonempty table-row instructions, table accessibility descriptions, MathML, media attributes, final comparison and glossary meaning. The compact final source read printed every selected semantic paragraph and all row entries without truncation.
- Derived 28 exact image basenames from these selected EN blocks. With the parent's explicit authorization, the existing `freeze_unit.py --review-images MR-BRIDGE-011 A20 ...` helper copied only those 28 EN and 28 ID rasters to the ignored review directory. This did not freeze the unit or edit its config.
- Personally opened all 56 images using filesystem image inspection, in paired groups 015a–e, 016a–f, 017a–c, 018a–c, 019a–d and 020a–g. Existing historical review claims and alt text were not substitutes for this inspection. A subsequent read-only check compared every copied file with its exact ZIP member.
- EN images total 752063 bytes; ID images total 2899820 bytes. The original English pixels govern the transcription. All numerical results and variable roles agree; notation/presentation differences are recorded below.

## Translation and representation decisions

1. Preserve every original paragraph identity. CNXML paragraphs containing tables become identified HTML-compatible div wrappers; their subpart markers and complete tables remain within them. Preserve all six table IDs and every media ID on the corresponding text or instruction element.
2. Preserve all 26 source body rows: f(3) five; f(−2) five; f(a) three; g(h²) three; g(x+2) four; g(x)+g(2) six. Repeated definitions and apparently repeated calculation lines are not merged.
3. The source declares two columns but some tables contain extra empty spacer entries/colspecs. Normalize only those empty presentation spacers into two meaningful columns, keeping every nonempty cell and row in sequence. Mark tables `data-kind="adaptation"`; new captions/column headings are `data-kind="original"`. The reader visibly discloses this repair rather than silently claiming identical layout.
4. The two prose rasters are actual source instructions: 016a tells the reader to substitute −2 for x to find f(−2); 020a tells the reader to find g(x)+g(2). Translate them under original media IDs `fs-id1171792372816` and `fs-id1167836693279`. They are not discarded as decorative images.
5. Transcribe 020e's blue underbraces as explicit Marathi prose under `fs-id1167836322927`: 3x−5 comes from g(x), and 1 comes from g(2). Keep its equation and the following unannotated 020f equation as separate source rows.
6. English 017b shows `f(a)=2(a)²+3·a−1`; the ID redraw already shows `f(a)=2a²+3a−1`. These are equal but the latter collapses the visible substitution step. Keep the exact EN intermediate grouping/multiplication and the separate 017c simplified line. This difference is explicitly disclosed in the reader.
7. English 016c uses `3(−2)`, not an added multiplication dot. Preserve that grouping. English 015b/c and 017b do contain multiplication dots; retain them. Signs, parentheses, exponents and repeated function names were checked against pixels.
8. Both 018b and 018c have `g(h²)=3h²−5`, without a printed multiplication dot. Their difference is the substitution highlight. The EN table aria description says “Simplify” where the visible last row has no prose cell. Retain both identical equation rows, retain the source's blank prose cell, and disclose the accessibility-description/highlight distinction in a separate original note. Do not manufacture a different algebraic intermediate line.
9. Translate every original “substitute” instruction as “x च्या जागी ... ठेवा”; “Simplify” becomes “सोपी करा”. The original supplementary explanation introduces प्रतिस्थापन, a previously provisional working term. Values are “मूल्ये काढा”, not a claim that the reader is solving for an unknown input.
10. The relation retains its five listed pairs, repeated relation in the solution, both domain/range explanations and both complete answer sets. An explicitly original note prevents extending the finite relation merely because its pairs exhibit a pattern.
11. Preserve the final source comparison `g(x+2)≠g(x)+g(2)`. An original clarification limits that claim to the supplied g, not every function.
12. Keep glossary last in source order. Translate the complete meaning: any set of ordered pairs; all first-coordinate values form the domain; all second-coordinate values form the range. Do not replace this relation definition with the narrower function definition.
13. No embedded assets are needed: all 28 media identities now have complete accessible transcriptions. Config deliberately has no assets object. Exact source rasters remain independent provenance evidence, not automatically fetched runtime dependencies.
14. Three original question/solution pairs have local forward and return anchors. New local navigation and HTTPS credit/canon citations are separate from source coverage. The selected source fragments have no outgoing source links. No new cross-unit link mechanism, module wrapper or reader assembly was created.
15. Unit-local example numbers 1–3 are explicitly not asserted to be original textbook numbering. Scope notes, bridges, credits, captions and navigation are new additions rather than falsely attributed source prose. Existing attribution and the settled CC BY-NC-SA 4.0 notice are retained without reopening the supply/license audit.

## Actual Marathi canon consultation

Selection: read fresh search-reader prose from [C14–C16, फलन](https://marathivishwakosh.org/21979/) and [C19, फलन](https://vishwakosh.marathi.gov.in/27548/). Used the distinctions between a relation and a function, permitted input set, and actual image set. Retained प्रांत and फलन; kept the existing provisional मूल्यसंच while recording the attested synonym कक्षा. The consulted passages do not independently attest every working term.

Drafting: read the existing OCR for C12/C13, BB8 physical pages85/86 (printed75/76), then personally inspected both original page PNGs. C12 distinguishes a solution of an equation from substitution/evaluation; this informed the explicitly original explanation. C13's stepwise explanations support preserving the source's intermediate rows instead of merging them into final answers. OCR formula defects were not copied: for example p75 visibly has x−2=7, not OCR x−2=17. The p76 two-method example visibly begins 2/3+5a=4 and ends a=2/3; those numbers are not imported into this unit.

Revision/final source read: reread the relevant C12/C13 OCR prose and compared it with the already inspected pages while checking the Marathi “मूल्ये काढा” versus “उकल” distinction. Reopened both Vishwakosh pages; direct retrieval failed (timeout and502), so this is not claimed as a successful direct-page fetch. Fresh targeted official-domain search then returned the readable C14–C16/C19 prose again. The actual-output-set distinction was checked against both finite answer sets and the glossary. This confirmed the existing wording; no unrelated advanced claims or missing QuickLaTeX image formulas were used.

Canon files actually read/inspected, SHA-256:

- `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt`: `f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b`.
- `downloads/mr-Deva-IN/canon/ocr/balbharati8-86.txt`: `497332d70fb096c86e468261e37186b888099b86830234a26d5c86253188ee57`.
- `downloads/mr-Deva-IN/canon/pages/balbharati8-85.png`: `284d9c7e4dc21f183189750421e65c97acfae02fd642df0457321cfe627a7f69`.
- `downloads/mr-Deva-IN/canon/pages/balbharati8-86.png`: `87e2c859c7d3445466e28b1050bb86bc52b1014fb6f2dd2c75d356dda620ce49`.

No new canon locator or shared consultation ledger was written under this delegated ownership. These stage-specific details are handed to root for integration. No native-speaker, Marathi-teacher or human-expert approval is claimed.

## Bounded checks actually run

Read-only inline Python checks against actual XML/config and the pinned archives:

- Valid XML, article ID/locale, NFC, no replacement character, 67 unique target IDs.
- All65 original IDs exactly once/in source order in each corresponding target subtree, checked independently for EN and ID.
- Four canonical-order source locators; classifications3 worked+1 definition; no original or translated practice items.
- Six tables and all26 body rows preserved; all28 media IDs preserved; all56 review-image copies byte-equal to original selected ZIP members.
- Three real source question/solution forward-and-return pairs; all11 local links resolve; three HTTPS citations; zero images, scripts or runtime network dependencies.
- All54 unique displayed-math keys exactly match config. These are regression checks, not independent mathematics proofs.
- Separately evaluated all30 displayed equality chains using the existing narrow Fraction/polynomial AST interpreter (no eval). Every left/right coefficient map agrees. Source question formulas were independently read from MathML and compared.
- Recomputed the finite relation's domain/range from its five actual pairs. Confirmed f(3)=26, f(−2)=1, f(a)=2a²+3a−1, g(h²)=3h²−5, g(x+2)=3x+1 and g(x)+g(2)=3x−4.
- The last two symbolic polynomials differ by the exact nonzero constant5. This is a coefficient identity, not a universal claim inferred from finite samples.
- Personally reread the complete finished Marathi XML and config after the source/image/math checks. No arithmetic correction was needed.

These checks are not a standalone newly committed test suite. An independent reviewer may reuse the actual source and current draft; root owns that integration. No build, freeze, browser action, render, PDF conversion, shared-script edit or commit was performed by this drafting worker. Reader layout remains unverified here; existing browser-policy restrictions remain binding.

Stable handoff bytes:

- XML: 24755 bytes; SHA-256 `1a5a8cca15aa154ca15f24ec2708502cd1837f4a3714d9e781483d956e1573f1`.
- Config: 2827 bytes; SHA-256 `8755902abf15d4729374d5a853f7d64a105a3040de2ebe3065899e1e3e94591c`.

## Exact source-image evidence

Review directory: `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-011`; files are named `en-` or `id-` followed by the basename below. Original members use the EN bundle's `media/` or ID `source/media/` prefix. Each row gives both byte counts and complete SHA-256 values. All56 pixels were inspected, not merely hashed.

| Basename | Preserved media ID | EN bytes · SHA-256 | ID bytes · SHA-256 |
| --- | --- | --- | --- |
| CNX_IntAlg_Figure_03_05_015a_img.jpg | fs-id1167836293439 | 15367 · `8f1b6c07e3d47ec44fddac1710fcf1513cfca5245ae08191c9492c54f8ea4a6b` | 100413 · `81052eb83990c61b4e6b13e7ebf709d37780ed6f2b008155b35749770d5b28bf` |
| CNX_IntAlg_Figure_03_05_015b_img.jpg | fs-id1167832999716 | 18937 · `359b2e4e54522093bd60797b67f67018be4336dc7fbedf050988e43905e4d4b5` | 113851 · `93658d54ab37fdaa21b011b9fe8e37b8d5f219d672ab5109f53ce2de220d850a` |
| CNX_IntAlg_Figure_03_05_015c_img.jpg | fs-id1167836520086 | 16552 · `6d6b68e0e5dc808e6aed805a1ed9faff82e13acb17b2f4e5874b2df77689c99d` | 92972 · `f064dca4b6e9d51f043884a5c2e9605907cc10c4784f0b0e24407837a4073b89` |
| CNX_IntAlg_Figure_03_05_015d_img.jpg | fs-id1167832980523 | 15085 · `f5461ae79095dfdddbc37ce8bf4135be0c423a8ffca557b6afff390ef40bbe0f` | 97670 · `6f2a500d9d68277211c30c9fd25b4c47d9973611497e233ab12c5b84a7035427` |
| CNX_IntAlg_Figure_03_05_015e_img.jpg | fs-id1167829852974 | 13623 · `acb9fe8cd2f31c9e922a01dcbaa55364dc7ee4b5c2aef224cc09f6d177e3e233` | 95313 · `35121858482a1f85e84e75166988efb14417cefbe720488f7d022cf15e24046c` |
| CNX_IntAlg_Figure_03_05_016b_img.jpg | fs-id1167829853948 | 16289 · `d538961c2ef43f2ba6da6d34f41b8f716c53d5cba3c5da31822008b26ab108df` | 100413 · `81052eb83990c61b4e6b13e7ebf709d37780ed6f2b008155b35749770d5b28bf` |
| CNX_IntAlg_Figure_03_05_016a_img.jpg | fs-id1171792372816 | 20349 · `f65fe4a22c4f3b0b9b2f95b23e58645fbc1ffe672d927e1919d6198299981b35` | 105553 · `0772c90625436daca2fa190e5de0b96ce5dadb01b3f8ba6ccdfabe243bb04de7` |
| CNX_IntAlg_Figure_03_05_016c_img.jpg | fs-id1167829694507 | 20585 · `458fb33dc44fa8abc07662e13fb2177ab5efbfc7ce0d435afcc6dd582b8bab5e` | 113313 · `7bd6496230a37b9861dc60bdde1635841202f4faf4833d86ae4f7e3f37cfa41d` |
| CNX_IntAlg_Figure_03_05_016d_img.jpg | fs-id1167829715540 | 18058 · `b4d4600de5f8567c9be1661d2c6132c56a01170dcd1847292bcfe5cfcd703b08` | 91508 · `e5f5549aa7c1e5a7feff180699a899aa06963917a6e8fe94166325ed59be82f4` |
| CNX_IntAlg_Figure_03_05_016e_img.jpg | fs-id1167836532685 | 17757 · `3eff490c0168eb4c9d2917adb55dad31ea99cf6b0f4c518f07e1a76c4d41d09f` | 95076 · `0eb8ff9c1807f7648ad307b22739317242f7a9a14904d408e322c1c02205f997` |
| CNX_IntAlg_Figure_03_05_016f_img.jpg | fs-id1167829695370 | 15369 · `2fa9375d50a0a044838414225329621e0321419da7976d7f7678c5a3940dd86d` | 78863 · `70b5026129e04e4377fa91ab9c8199fde85fe7bc0990f2e9b4186c062703efbd` |
| CNX_IntAlg_Figure_03_05_017a_img.jpg | fs-id1167836685384 | 16171 · `3b8d6c664d1d49b9e85533f28a4b6509aa1518f93c0d42b87b5e5f028c798377` | 100413 · `81052eb83990c61b4e6b13e7ebf709d37780ed6f2b008155b35749770d5b28bf` |
| CNX_IntAlg_Figure_03_05_017b_img.jpg | fs-id1167836362257 | 19671 · `db6bf8be9c9de10d3c480236f6e0c90db68b964088f6b3fb461e58ecd5a600a7` | 116601 · `67ae824733d69059d6f87e6749741fa087805fdf3b4fe2541a147de9992b2855` |
| CNX_IntAlg_Figure_03_05_017c_img.jpg | fs-id1167836320903 | 16584 · `f4055edec6085409e5236489f1522012f47869b9a945f58f37c98cfe1e865e0c` | 101030 · `fe0b4609f0b75c4c4c21e6aef2d95134c4b1a2a66615d2120ea22f8d68b697d3` |
| CNX_IntAlg_Figure_03_05_018a_img_new.jpg | fs-id1171792580809 | 56113 · `d18703b19db2fac32e0b5fae1f8e3bdc2947b11f33048127c0ef1ad753a46523` | 99634 · `d912c774516dfae5bc6f233448ca83c61bd2ba5a6608ed698f6cc269412a88d6` |
| CNX_IntAlg_Figure_03_05_018b_img_new.jpg | fs-id1171790163372 | 58333 · `e4ea8561d40216adac5be0d5bcc3d695c5d4eb7780eb49fea2d2704104dda048` | 129283 · `3ebb6028f3c171555af8b5c6c45cea917287817969530737bcaa6acfa1b4727b` |
| CNX_IntAlg_Figure_03_05_018c_img_new.jpg | fs-id1171792588637 | 57001 · `6fbb37a4d5d9f2d14f158ca37920dc1116fc6751b3b3b958798e0c0c10025821` | 109691 · `35016e73dc698c9ca99df0cb843f7e4433b86e9524c5c24830d90b2afd2b2ca1` |
| CNX_IntAlg_Figure_03_05_019a_img_new.jpg | fs-id1171792545190 | 54018 · `98b70a1d2c74c50c17ee5dc969913998e313f47067c1cdc3f2b1e71bc39ff168` | 99634 · `d912c774516dfae5bc6f233448ca83c61bd2ba5a6608ed698f6cc269412a88d6` |
| CNX_IntAlg_Figure_03_05_019b_img_new.jpg | fs-id1171792543055 | 58311 · `ab65dff5052d3b41ef03e1ad0e2d91fb50740153376b7c3935e8a934aac98ccb` | 122710 · `b625e6f9d33b8196bd46179f5ca2bb3660c246a09b13b7f394ad931d5d7d0ee3` |
| CNX_IntAlg_Figure_03_05_019c_img_new.jpg | fs-id1171792802121 | 55773 · `26d267fbc8675435cba7beb9176b4a34a5f8cf1c91e4734b19b3eee025ac1b0a` | 99285 · `0c1542a9a53df43c57e05ec529efc26cfa4a56333dec252dc85d9e35fcd8e7b5` |
| CNX_IntAlg_Figure_03_05_019d_img_new.jpg | fs-id1171790304229 | 54945 · `3169c52d29ce4906c8040350fdaa03f0770e2a26fa55c4bef71067026cf3651d` | 99632 · `5746d7914f5e885fe9ab7ead2147f4477312191efe7f0f6e13de2521d09bfcd1` |
| CNX_IntAlg_Figure_03_05_020b_img.jpg | fs-id1167829839522 | 13957 · `6c298044579d841ff8313d8f490ca76549e06265211dfd44d59363aba765c677` | 99634 · `d912c774516dfae5bc6f233448ca83c61bd2ba5a6608ed698f6cc269412a88d6` |
| CNX_IntAlg_Figure_03_05_020c_img.jpg | fs-id1167836635207 | 15937 · `459612b52038e313e604659b3b0ef963d3c3fac56bb220c61e72a554b57ad00b` | 113398 · `b483fc3c1f45233ec231f66620b9aee4303e74d47dba1760329ad4cca3032d6e` |
| CNX_IntAlg_Figure_03_05_020d_img.jpg | fs-id1167829685715 | 12545 · `a903bf6744258a0142ecdbd1156ab75f7f30e7461a8792e81c91416c4bb73080` | 81161 · `a86d7515f7f57b0cbc1090e8596c270582e1d03cbf8da574174d43b72da168d1` |
| CNX_IntAlg_Figure_03_05_020a_img.jpg | fs-id1167836693279 | 18404 · `6f5f87c52e715e3cbab86cfee2fee903bc107b1212afa550c092819f81fb708c` | 113971 · `fda012e6d2636b27a978a9bfc34b5284f36a9325bc512ec94d320a8c391d8e2a` |
| CNX_IntAlg_Figure_03_05_020e_img.jpg | fs-id1167836322927 | 24117 · `6c22d32a9792fa72309e276df9be254d66cf7053846b78ced0f1be79505ffbe0` | 117159 · `0dbd49fa0ac613e72436b95ed5ed8061e17e223bbdb04d051c6c6648db4cb29f` |
| CNX_IntAlg_Figure_03_05_020f_img.jpg | fs-id1167824734809 | 16557 · `200407430ae157c57ca3263b194a148cd3e91ece4106155f94b18bd5d2b727a5` | 102150 · `ec707b726d5007d7b31e9ffad800ccf32a87dbd9cea62d2aa7e71095990b3b39` |
| CNX_IntAlg_Figure_03_05_020g_img.jpg | fs-id1167836539801 | 15655 · `6bdacac4f846e8400a3bb483bfc5e80d8ed5ee7c08ebc7353602b0c4c4f40052` | 109489 · `b12b042f5470be476f7c1ce4b2387f35eced76d3e8fb7e18a1a9d3184ac7f195` |

Primary integration update,2026-08-31: freezing/build and the19 drafting-author regressions passed. A separate independent source reviewer then read all56 original rasters and all26 rows, independently checked mathematics, and reran those tests. Root read that full review and reran the suite.011 remains an unreviewed reader-format replacement with zero new unique selections, not another completed module.
