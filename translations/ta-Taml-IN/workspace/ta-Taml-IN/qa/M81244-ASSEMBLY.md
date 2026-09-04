# M81244 source-module assembly and structural QA

Date: 2026-09-01

## Result and boundary

**PASS for the exact, source-faithful Tamil m81244 CNXML assembly and its closed review-source package.** The assembled source contains every canonical m81244 node in source order, retains the exact Tamil title and metadata, preserves the titleless `fs-id2263283` wrapper, retains every source answer and every source omission, resolves the admitted local/module-qualified links, and closes over 50 exact Tamil SVGs.

This is deliberately narrower than a learner release. It is not a rendered reader, EPUB, PDF, diagnostic, mastery route, answer-complete companion, native-speaker approval, current-board-alignment approval, or completion of A00/A10/A20/AX-1/AX-3 or the Grades 2–8 assignment. Frontmatter and readiness content are admitted only as exact pinned source fragments; their presence is not evidence of readiness, grade placement, or demonstrated mastery. The source confidence chart remains a self-estimate rather than a mastery gate.

The assembler changed no translation or asset file. Its only persistent output is `reader-m81244-review/`; default builds and `--check` use a sibling lock, and default builds use a fresh sibling staging tree. Those transient paths are removed on success and retained only when an interrupted state must remain fail-closed. This QA record and the assembler are the only authored control files in this lane.

## Exact final artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `scripts/assemble_m81244.py` | 83,867 | `78b93b01f215550fb89bb0e2f78f0c31dd810fc3d358bda3757b5208d052002a` |
| `reader-m81244-review/source/m81244.cnxml` | 194,499 | `563dc10f207a09b919e28a0ea535848e244e7c5b4bbbcca5d2f588746ab38b50` |
| `reader-m81244-review/manifest.json` | 40,848 | `cad9226386091f04f213a4413b701c961a1bf66b7d14280a5e314fbb75e52908` |
| `reader-m81244-review/LICENSE.txt` | 21,442 | `ab1a44bbba58252630134574d7b2534813339240eb645825ffcc2487dbe8114a` |
| `reader-m81244-review/ATTRIBUTION.en.cnxml` | 3,955 | `a5f7b832d22ea14425050743b74deedc8a1037821d6592aa84e7540940db95c5` |

The package contains exactly 54 regular, non-reparse files and 542,725 bytes in the exact expected directory tree: one assembled source, 50 SVGs, the manifest, the retained CC BY-NC-SA 4.0 notice, and an exact asset-free extract of the pinned OpenStax `About the Authors` / reviewer credits. Extra empty directories fail as well as extra files. The manifest records every fragment and SVG hash separately.

Pinned source witnesses:

- English `provenance/m81244.en.cnxml`: `b32058ce714e5fd43b010ccc81b2ae00a11567b229e9f96dda7b85b3cd82ba6b`.
- Indonesian `provenance/m81244.id-ID.cnxml`: `d23343f302c34436169e88ffdbc4eab37baabf0a3d1134755b2f5676c75e1cc6`.
- Cross-module link target witness `translation/m81243.cnxml`: `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959`.

Exact Tamil fragment pins, in assembly order:

| Source ID | SHA-256 |
|---|---|
| `frontmatter` | `c568bfc0cd596439c1097e4bdc37ce0ef8ea6d48de22c0d47a3c3fec7286552f` |
| `fs-id2299412` | `f6a28fbc919f8fe1f6c3207c9d85cdb6f99a115cfc3dd54fa52f5eb9327a0edb` |
| `fs-id1122444` | `178f0294d076dbc50c03f802d3d4e3fbee550d4f84c7b6f53fa6bec0b0aea12a` |
| `fs-id2601285` | `83b547490aab15c693225a832c9d03e14f2bf1ac8d4cde105470a6e2c601b313` |
| `fs-id2145437` | `b1cd67ced5430ef3de73f8a6483a09849ac1523180f2ff26b468d8ba64620ee1` |
| `fs-id1385496` | `dd3d4e473f5468cff9737a01d3968f60b0dd5102fb791fff529eab43ec0ddaff` |
| `fs-id2691382` | `1bb36df94ec4db85db15a2b07985070532955e54f4e15edb94b15c8f39839c30` |
| `fs-id2197427` | `8e7aeb7d3d537466c4b98c902016f61ba4ff2f65b48f1c078c1d41029f8b5ceb` |
| `fs-id1611455` | `12d98d249c3b940dc3372e5d781b0d92d012041a3a5bbf1b4d673ed102e64f99` |
| `fs-id2150139` | `4b6e7ee11d47eca9f7318b5c7b82add16b306012cbaaf7ffa678479d5ab93f0a` |
| `fs-id2280700` | `7d8abec4d0cc0ad191e124b94d935bf9b8d42ea283604f23f1b368f50f7df7ea` |
| `fs-id1405751` | `e4527c03e1c98627a713afde6d6d199e97f04fe33b28afac7020fc60fc3225b2` |
| `eip-985` | `ba06b9c41e5913ba2e26dae36bd6cc6bc9fd862c18d7e4ad862150f3509836f4` |
| `glossary` | `8d01abdc05c079b6f2752066bb699d7d89df015e653eb6afde4440730761e258` |

## Canonical structure preserved

- Exact root and metadata title: `முழு எண்களைக் கூட்டுதல்`.
- Metadata content ID: `m81244`; UUID: `8069044b-6fb1-49bf-b03a-64988f9b1ddd`.
- Root children: `title`, `metadata`, `content`, `glossary`.
- Direct `content` IDs, in order: `fs-id2299412`, `fs-id1122444`, `fs-id2601285`, `fs-id2145437`, `fs-id1385496`, `fs-id2691382`, `fs-id2197427`, `fs-id1611455`, `fs-id2263283`.
- `section#fs-id2263283.section-exercises` has no direct title. Its exact direct-child order is `fs-id2150139`, `fs-id2280700`, `fs-id1405751`, `eip-985`.
- The glossary is the final document child. It has definition `fs-id1226736`, and meaning `fs-id1245763` is the final source node.
- All original source IDs and the complete 401-tree MathML inventory are retained. Linguistic MathML `mtext` is checked against the exact mathematical payload admitted by either pinned language witness; all other MathML tokens, tails, attributes, hierarchy, and module-specific content models are strict.

Final counts: 3,576 elements; 756 unique source IDs; 401 MathML roots; 129 exercises; 89 solution nodes; 50 media; nine direct content children; four outer-wrapper children; five objectives; one glossary definition; 1,464 globally unique SVG IDs.

## Fail-closed gates

The assembler requires the exact discovered 14-file `translation/m81244*.cnxml` inventory, every fragment hash above, both witness hashes, the linked m81243 hash, all 50 asset paths and hashes, four actual-canon OCR/PNG pairs, the license, and the credits witness. Every pinned input is read into one lstat-stable byte snapshot, hashed, and parsed or derived only from that same snapshot; final pathname repins remain. Missing, extra, changed, unreferenced, non-regular, symlink, junction, or reparse-point entries fail.

Structural comparison is performed against both witnesses and again after serialization. A separate exact-tree comparison against the pinned Tamil fragments rejects inserted or altered prose even where a broad source/translation comparison would still be nonempty. Ordered Unicode numeral, mathematical-symbol, percent, and currency payload is retained. Canonical figure basename identity is checked per media ID, and table accessible-label presence is retained.

CNXML links are local or module-qualified and must resolve to admitted IDs. The three exact canonical OpenStax URLs `/24add2blocks`, `/24add3blocks`, and `/24addwhlnumb` are the sole nonlocal exception because they are original source links. They are recorded as optional source references, not packaged offline dependencies. Any other URI scheme, protocol-relative value, `href`, or nonlocal attribute fails.

Every SVG must be UTF-8, well formed, local, hash-pinned, single-use, and description-equal to its current CNXML alternative. IDs must be unique within and across assets. The validator uses the exact current eight-element SVG vocabulary (`svg`, `title`, `desc`, `g`, `rect`, `path`, `text`, `tspan`), exact current attribute and XML-declaration allowlists, and global resolution of every `aria-labelledby`/CSS ID reference; every other element and every foreign namespaced attribute except `xml:lang` fails. DTDs, entities, processing instructions, `xml:base`, scripts, SVG Tiny handlers/listeners, style elements/attributes, animation, `foreignObject`, raster images, foreign namespaces, event attributes, unresolved references, and external `href`/CSS URLs fail. The exact scoped asset directories are enumerated before and after assembly; all 50 expected files must be direct children of those scopes, so an unexpected empty subdirectory also fails.

Package writes use an exclusive build marker, a fresh checked sibling staging tree, and a fail-closed in-progress manifest installed before payload replacement. All payload bytes and the staged final manifest are reverified while that incomplete sentinel remains visible; atomic promotion of the final manifest is the last commit. A separately retained recovery sentinel revokes the completion claim if post-commit verification detects interference. Interrupted staging is retained for inspection rather than recursively deleted, and later builds/checks refuse any retained stage. `--check` takes the same exclusive lock, rejects live/orphan transaction state, hashes the exact file-and-directory tree before validation and again afterward, and requires the two snapshots to agree. Successful builds/checks leave no lock or staging directory.

Thirty-three in-memory negative fixtures were rejected: duplicate module ID; invented outer title; outer-child reorder; MathML token change; `mtext` mathematical-payload change; foreign or unknown/malformed MathML; unexpected prose and symbol insertion; media/source swap; table-label removal; insertion of a solution at a canonical omission; unapproved nonlocal link; SVG script, SVG Tiny handler/event content, `foreignObject`, duplicate SVG ID, external href, `xml:base`, animation, style attribute, external CSS URL, unresolved descendant ARIA reference, style element, stylesheet PI both before a declared SVG and before a declaration-free SVG, and DTD/entity declaration; extra asset file; unexpected scoped-asset subdirectory; changed fragment bytes; changed asset bytes; extra package file; and extra empty package directory. A filesystem fixture also confirmed that `--check` rejects a retained sibling stage and releases its lock on that early refusal.

## Explicit source omissions

Both witnesses and the assembly have exactly 40 exercises without a solution node. No answer was invented:

- 38 are the source omissions in `fs-id2150139` (U015). The independent response audit counts 120 unanswered response parts inside those exercises.
- `fs-id1215287` in `fs-id2280700` omits Fred's total. The independently computed review key is 1,230, but it is not inserted into source CNXML.
- `fs-id1827602` in `fs-id1405751` is an open model-reflection prompt and remains without a source solution.

The manifest records every omitted exercise ID, problem ID, section path, and omission status. These omissions prevent this source package from being treated as teacher-independent or answer-complete; any later answers and reasoning belong in a separately marked companion.

## Continual actual Tamil canon consultation

The assembly lane used actual OCR and full textbook page images during drafting, revision, and final QA; the canon index and terminology ledger were not treated as substitutes for the pages.

| Locator | OCR SHA-256 | PNG SHA-256 | Exact evidence used |
|---|---|---|---|
| C11, PDF 36 / printed 30, §1.15.1 | `0729f5fab7454c703a640ed3817f0ddfb9c8e8f3a763ed3c449e312076b0ed16` | `f51ec4222c04debe338f7565f8d9d6eab9dd5be56b22716bcb688c9fa78c1c1c` | The image visibly resolves `அவற்றின் கூடுதலைப்` for the result of addition; OCR line 14's `கூருதலைப்` is corrupt. It also distinguishes operation `கூட்டல்` and uses `மொத்தம்`. |
| C17, PDF 38 / printed 32, §1.15.4 | `14565da267984e61411efda2d54e77aa9041f0b7d099d335795238043b1a6297` | `ec91d59f4a408ed9aadea9d543a61b6158f11151be451ac0d4b7d947937941b8` | Heading `கூட்டல் மற்றும் பெருக்கல் சமனி`; the paragraph visibly calls 0 `கூட்டல் சமனி`. OCR lines 30 and 33–34 were checked against the image. |
| C18, PDF 46 / printed 40 | `b7955cfbf49c5321874771aa26755d1e4ecfad0031ada9ed034d479bfdefda89` | `c208f8b59c7a2747171152f4e53198c48aae52858a24f76880cd9f024cdfb229` | The visible application bullets distinguish boundary-length/string/fence measurement (`சுற்றளவின் நீளங்கள்`) from finding a park's area (`பரப்பளவு`). OCR lines 13–28 were checked against the image. |
| C12, PDF 175 / printed 169 glossary | `17546f2815c3077bf5fc2d90d1fca376b6aa4a83fd664e01907b3e5969b2d999` | `a4790fc94ecf2b3b4af3bab80f383e5383ef60e9e65ff8f72df8bc4d49437679` | The image, not corrupt OCR, visibly resolves `குறியீடு` / Notation and `கூட்டல் சமனி` / Additive Identity, and distinguishes `முழு எண்கள்` / Whole Numbers from `முழுக்கள்` / Integers. |

Drafting opened and read the complete C17, C18, and C12 OCR and PNG pages while defining the assembly evidence boundary. Revision reopened their targeted lines and full images while hardening terminology-sensitive checks. Final QA reopened all four OCR/PNG pairs after package assembly, adding C11 because it directly bears on the final glossary result term `கூடுதல்`; the full four-page image set was reopened once more after the final fail-closed transaction/security revisions. This evidence supports register distinctions only; it is not native-language, current-syllabus, or official-terminology approval.

Independent source/asset admissions also used actual canon:

- `qa/M81244-U015-independent-review.md`: PASS, SHA-256 `3325d5b68d1114aaa1f1dbfd667fcf09ad95a815e87e6b69f27325f9f96cc6d2`; it reopened 14 actual OCR/PNG pairs, recomputed all 38 supplied solutions, checked all 21 canonical rasters and Tamil SVGs, and retained all 38 U015 omissions.
- `qa/M81244-tail-independent-review.md`: PASS, SHA-256 `1c9867f9e977569763591d27de074831ab96461b695051e0380374946df0e35d`; it checked the tail structure, arithmetic, omissions, self-check meaning, and glossary semantics.
- `qa/M81244-tail-figure-notes.md`: final tail SVG handoff, SHA-256 `93ccade359c2ba68ff81474ab57bf56de936788f58449de849324666af416eb9`; exact SVG SHA-256 `cd0294912322fca86eeb73681c7f769f6ff86620c250e2f8dbb47ffe09bc8ae3`.

The bounded editorial risk `கூடுதல்` versus the earlier project-used `கூட்டுத்தொகை` remains documented. Actual page 36 supports current m81244 `கூடுதல்`; final cross-module harmonization still requires qualified Tamil review.

## Reproducible final checks

From the repository root, all of the following completed with exit code 0:

```text
python -X utf8 ta-Taml-IN/scripts/assemble_m81244.py --check-only
python -X utf8 ta-Taml-IN/scripts/assemble_m81244.py
python -X utf8 ta-Taml-IN/scripts/assemble_m81244.py --check
python -X utf8 ta-Taml-IN/scripts/assemble_m81244.py --check
```

The two final `--check` runs independently rebuilt the expected bytes in memory under the exclusive build lock, required exact equality with all 54 packaged files and the exact directory tree, and required identical pre/post package snapshots. The assembled-source hash remained `563dc10f207a09b919e28a0ea535848e244e7c5b4bbbcca5d2f588746ab38b50`; no build lock or staging directory remained.

## Remaining limits

- The package is CNXML plus SVG source assets. No integrated HTML/browser, EPUB, PDF, narrow-screen, keyboard, screen-reader, Braille-math, or PDF/UA result is claimed here.
- U015 SVGs have a separate standalone-Chrome PASS. The tail figure note records geometry/raster checks but explicitly lacks final bundled-font browser approval. This source-only package does not upgrade that evidence.
- Structural, arithmetic, link, MathML, and SVG closure checks do not substitute for native-speaker, educator, learner, assistive-technology, efficacy, or placement review.
- Forty canonical source omissions and the confidence-only self-check remain. A separately marked companion and executable mastery/routing evidence are still required before teacher-independent use.
- This m81244 source assembly is one bounded artifact inside the much larger assignment and is not a global completion claim.
