# MR-BRIDGE-013 drafting handoff

Drafted 2026-08-31 by the source-review worker. This completes this selected teaching section, not m81374, A20, or the five-book assignment. Root owns freeze/build/independent and format-specific visual review after handoff. No browser, HTML inspection, PDF generation, build, commit, publication, large acquisition, shared-tool edit, or source-pin change was performed by this worker for 013.

## Exact selection and boundary

The whole A20:m81374 section `fs-id1167836522816`, **Identify Graphs of Basic Functions**, is translated in source order. Its wrapper ID/title are retained but the wrapper has no `data-source`; each of its 47 direct non-title children is selected exactly once. Those children contain 167 IDs; the uncounted wrapper brings retained source IDs to 168. EN and ID have identical ordered IDs and the same 47-child boundary. There is no overlap with the 012 selection. A reference to 012's prior figure is not a new selection or duplicate media count.

- 20 prose blocks, one source figure, eight concept notes, six worked examples and twelve Try Its = 47 blocks.
- The eight concept notes comprise the graph definition and seven basic-function definition/summary boxes. `translated_definitions: 8` includes those seven boxes, not eight prose-only formal definitions.
- `translated_worked_examples: 6`, `translated_practice_items: 12`, `translated_resource_notes: 0`, `original_practice_items: 0`, `question_ids: []`.
- 18 source problems and 18 supplied solutions; all solutions include original canonical diagrams. No new answer is passed off as a supplied solution.
- 26 distinct canonical images, each used once. Five image tables are also transcribed accessibly: line 007, square 013, cube 015, square-root 017, absolute-value 019. They have 5+7+5+4+7 = 28 data rows, not additional questions or source blocks.
- Final selected block: note `fs-id1167836389848` (Absolute Value Function), including media `fs-id1167836335262`.
- **NEXT:** A20:m81374 section `fs-id1167836386547`, **Read Information from a Graph of a Function**; first prose `fs-id1167833022366`, followed by `fs-id1167836620724`. No part of that section is selected here.

Exact direct-block order:

```text
fs-id1167836293187
fs-id1167833020798
fs-id1167836685520
CNX_IntAlg_Figure_03_06_007
fs-id1167829598148
fs-id1167836321563
fs-id1167836665565
fs-id1167836480334
fs-id1167836692114
fs-id1167833049966
fs-id1167836755080
fs-id1167825091753
fs-id1167829754438
fs-id1167833128828
fs-id1167833054733
fs-id1167836602424
fs-id1167836494179
fs-id1167833142741
fs-id1167836481166
fs-id1167836558185
fs-id1167836528178
fs-id1167824674086
fs-id1167826171267
fs-id1167836683384
fs-id1167836310060
fs-id1167829624689
fs-id1167829783193
fs-id1167829853073
fs-id1167824617137
fs-id1167829738598
fs-id1167832966170
fs-id1167836485775
fs-id1167832982045
fs-id1167836598078
fs-id1167836787693
fs-id1167829687218
fs-id1167833023152
fs-id1167836512756
fs-id1167829930477
fs-id1167836341594
fs-id1167836650089
fs-id1167836664843
fs-id1167836299963
fs-id1167829879306
fs-id1167833350872
fs-id1167836625638
fs-id1167836389848
```

## Actual sources inspected

Full pinned EN section read as three bounded in-memory CNXML blocks, then a complete non-media text/cross-reference pass during revision. Full ID section likewise read in three untruncated bounded reads; an earlier combined/truncated output was not treated as full coverage. MathML `msqrt` and `msup`, rather than flattened itertext, determine square roots/powers. Full section IDs and children independently compared. Collections were independently opened in memory and confirm **m81373 → m81374 → m81375**, not an inferred next-module boundary.

| Witness | Exact archive member | SHA-256 |
|---|---|---|
| EN module | `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml` | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID module | `source/modules/m81374/index.cnxml` | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |
| EN collection | `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/collections/intermediate-algebra-2e.collection.xml` | `993990c353220be879928579c1393ced90c8b54764b4ba1182ba660b54e8ce32` |
| ID collection | `source/collections/intermediate-algebra-2e-checkpoint-0030.collection.xml` | `00d67af8787dd882c59c000f98fc0ac0e7b4f01c2820c108ac0da1a8ccbee744` |

The archive paths are `downloads/mr-Deva-IN/releases/A20-canonical.zip` and `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip`. Source-image preparation used existing `freeze_unit.py --review-images MR-BRIDGE-013 A20 ...`, after a disk check showing 13,865,771,008 free bytes. It validated the existing pinned archives and copied only the 26 selected EN and 26 selected ID members, 3,242,112 bytes total, into ignored `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-013/`. No extraction of the whole archive occurred.

All **52 local source-image files were personally viewed** with the permitted filesystem image viewer, not browser/HTML, and not merely by reading alt text. Their filenames are `en-` or `id-` followed by `CNX_IntAlg_Figure_03_06_` and the suffix below. Canonical EN members live in the archive prefix above under `media/`; ID members under `source/media/`.

```text
007_img_new.jpg 008_img_new.jpg 009a_img.jpg 301_img_new.jpg
302_img_new.jpg 010_img_new.jpg 011a_img.jpg 303_img_new.jpg
304_img_new.jpg 012_img_new.jpg 013_img_new.jpg 305_img_new.jpg
306_img_new.jpg 014_img_new.jpg 015_img_new.jpg 307_img_new.jpg
308_img_new.jpg 016_img_new.jpg 017_img_new.jpg 309_img_new.jpg
310_img_new.jpg 018_img_new.jpg 019_img_new.jpg 311_img_new.jpg
312_img_new.jpg 020_img_new.jpg
```

Only seven corresponding EN/ID image pairs differ in bytes: 008, 010, 012, 014, 016, 018, 020 (the translated summary graphics). The other 19 pairs are byte-identical; all were nevertheless viewed in both versions. Use canonical EN image bytes unchanged. Root inserts exact path/hash/MIME records into the currently empty `assets` object and pins all selected media/fragment witnesses.

## Source discrepancies, pixel findings and explicit additions

1. **Linear range, substantive EN/ID difference.** Prose `fs-id1167836692114` claims all-real range without excluding m=0 in both locales. Canonical 008 graphic also allows all real m and b while claiming all-real range. ID 008 graphic and its revised alt add `m ≠ 0`. Preserve the EN image and original claim as attributed source text; immediately add the necessary condition separately. For m=0, range is `{b}`, not all reals. Both cases have real domain. Distinguish scalar b from the actual intercept point `(0,b)`.
2. **Constant range.** EN 010 alt describes range as b, but canonical pixels already show `{b}`; ID graphic and alt also have braces. This is a description/notation mismatch, not an EN pixel correction. Marathi accessible text gives `{b}` and explains singleton braces.
3. **009a, 301, 302:** actual axes are −8…8, not the inherited alt/aria −6…6. Line rules and their intercepts/points remain correct. 009a is f=−2x−4, 301 f=−3x−1, 302 f=−4x−5.
4. **011a:** original media alt says x −7…7/y −1…11 while table aria says x −6…6/y −2…10. Canonical and ID pixels have printed x numerals −6…6 and y numerals 0…10, with grid continuing beyond them (x ±7, bottom y −2, top y 11). Target describes the printed marks and does not confuse grid edges with labeled values. Horizontal y=4 is unchanged.
5. **013:** actual square-example plot has x −6…6, y −2…10, and table points `(±3,9)` are visibly within it. Both source alts give other axes. Do not carry the earlier unverified assumption that the ±3 points are outside this particular plot. The smaller 014 square-summary image has x ±4/y −2…6, as described.
6. **305/306:** no adjacent table exists in either image, despite both locale descriptions. Actual 305 opens upward with x ±4/y −2…6. Actual 306 opens **downward**, x ±4/y −6…2; the source descriptions wrongly say upward and give different extents. The target's f=−x² and points `(±2,−4),(±1,−1),(0,0)` agree with canonical pixels. Original explanation distinguishes `−x²` from `(−x)²`.
7. **015,307,308:** actual axes ±8, not alt ±4 (015) or ±6 (307/308). Cube-example table is x=−2,−1,0,1,2 and y=−8,−1,0,1,8. Negative-cube answer reverses those y signs. Smaller 016 recap really has axes ±4; target explicitly distinguishes the displayed curve from valid but off-window points `(±2,±8)`.
8. **017:** actual square-root example axes extend to 10; source alt says 8. Table is `(0,0),(1,1),(4,2),(9,3)` and all are visible. Smaller 018 recap uses 0…8 and has correct domain/range `[0,∞)`.
9. **309/310:** function domains are x≥0, but the diagram windows include some negative x. 309 grid is x −2…10/y −2…8, not both 0…10. 310 grid is x −2…10/y −10…2, not only the fourth quadrant. Target separates the window from the actual curve and preserves the origin endpoint. The outside negative sign in −√x is explicitly distinguished from √(−x).
10. **311:** actual x window ±8, not alt ±6; y window −2…10. 312's ±6 x and −8…4 y are correct. Both are two straight rays, not rounded parabola-like curves. 019/020's y-grid extends to −1 but the printed y numerals start at 0; target says this accurately. Source 020 alt calls the origin a vertex, though no vertex label is actually printed in the image; target attributes that term to the description, not a pixel label.
11. **303/304:** ±12 axes really are correct; do not “correct” them to ±6. Horizontal values are −2 and 3. Identity 012 axes also are ±12; slope1/intercept0/all-real domain/range are intact.
12. Source Try It `fs-id1167829624689` and worked example `fs-id1167829930477` lack an explicit “Graph” instruction in both locales. Source formulas/IDs are preserved, with visibly original short graphing instructions rather than silently inventing source wording.
13. Source cube-range justification based only on positive/negative values is incomplete. Separately explain every real y has a real cube root, including 0. Similarly the added square-range explanation establishes all nonnegative outputs are attained. No finite plotted sample alone proves a full domain/range.
14. Explicit original learning notes: `[0,∞)` includes zero; infinity is not a real endpoint; perfect squares are convenient sample inputs, not the entire square-root domain; √ means the one nonnegative root, not ±; point plotting of these continuous functions is not permission to join all finite-source dot relations. The square-function range assertion is not generalized to all quadratics.

All formula displays and source graph tasks remain in original order. Problem and solution IDs are full upstream IDs, with bidirectional local reader links. The five accessible table transcriptions are source data, not newly authored examples. General navigation, captions explaining access, checks, and mathematical corrections are clearly marked `data-kind="original"` where new reasoning is supplied.

## Actual Marathi canon and workflow consultation

At selection the worker read `USER_INSTRUCTIONS_VERBATIM.md`, `WORKFLOW.md`, `GOAL.md`, `USER_UPDATES.md`, the canon README and consultations, and current012 drafting/config/XML pattern. The user explicitly requires repeated actual canon use, not merely a glossary lookup. Initial source-list/status reads which were truncated are not claimed as complete. Instructions persist across this bounded handoff. The coordinating task's actual latest user message was read at selection; it asked the coordinator to organize/consolidate cross-PC work, not to stop workers. Latest milestone task-state read showed subsequent published-snapshot updates and continued translation; no worker publication was performed.

During final handoff root relayed the new user wording verbatim: “[Operational message omitted from public export; full-assignment and continual canon-consultation requirements remain in the project workflow.]” The worker explicitly confirmed the actual EN/ID and stage-specific Marathi reads below; this was not treated as a request for a new audit or as a stopping point.

| Stage | Actual readable witness | Concrete effect |
|---|---|---|
| Selection and drafting refresh | C14–C16, [MV-F / फलन](https://marathivishwakosh.org/21979/), definition, domain/codomain paragraph, real-number/square example and final **स्थिर फलन** prose | Retain प्रांत, distinguish actual output set from सहप्रांत, allow many inputs to one output; use attested स्थिर फलन. Inline QuickLaTeX image formulas were not inspected or claimed as read; the readable prose supplied these decisions. |
| Drafting | C18, [आलेख](https://vishwakosh.marathi.gov.in/24316/), complete जात्याक्ष आलेख paragraphs and समीकरणाचा निदर्शक आलेख paragraphs | Use x/y-सहनिर्देशक and signed coordinate order; explicitly distinguish axis scale/window from mathematical domain. The actual equation-graph paragraph distinguishes smooth interpolation under a continuity assumption from straight joining; this changed the original graphing note. A direct reopen returned502; successful search-reader text supplied the actual complete selected paragraphs. |
| Selection, drafting refresh, revision | C20, [गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/), absolute-value/infinity rows, braces and interval rows | Retain केवल मूल्य; `[0,∞)` consistently includes0, `{b}` remains a set. Revision reread the open/closed/half-closed interval rows rather than inferring them from the glossary. |
| Drafting | C21, [गणितीय प्रतिरूपे](https://vishwakosh.marathi.gov.in/21277/), actual शंकुच्छेद paragraph | Retain अन्वस्त (parabola), not a guessed transliteration. The incidental [अन्वस्त](https://vishwakosh.marathi.gov.in/26599/) result also supplied actual prose using शिरोबिंदू and उतार; no advanced conic content was imported. |
| Revision | C19, [फलन](https://vishwakosh.marathi.gov.in/27548/), complete opening definition/image-set paragraph | Reaffirm actual output set versus declared codomain. Record कक्षा as attested variant, but retain established working मूल्यसंच. The opening prose does not establish that exact working word; no false attestation. |

Narrow primary-source searches for an identity-function Marathi term did not return a relevant attestation. Use the unambiguous descriptive **प्रत्येक संख्या तशीच देणारे फलन (identity function)**, not an invented claim of a standard term. वर्ग फलन, घन फलन, वर्गमूळ फलन and the combined केवल मूल्य फलन are transparent working combinations; only the underlying relevant terms above are claimed as witnessed. The choice was sent to the next worker so later recap vocabulary stays consistent. No new corpus or unrelated reference audit was started.

## Links, notices, checks and remaining work

Four source cross-references retained with exact `data-source-target-id` values: previous `CNX_IntAlg_Figure_03_06_001`, current `CNX_IntAlg_Figure_03_06_007`, square example `fs-id1167836683384`, cube example `fs-id1167832966170`. The previous figure is in012, so it is linked to the official HTTPS source page with `data-source-document="m81374"`; three others are local. Existing builder's HTTPS/# restriction respected. No attempt to route the denied HTML through another surface; local cross-unit reader linking remains a disclosed workflow limitation.

Settled licensing copied from current012: **CC BY-NC-SA4.0**, preserving third-party component notices, attribution to OpenStax/Lynn Marecek/Andrea Honeycutt Mathis, unchanged canonical EN graphics, and no training/fine-tuning dataset. No additional component-license/credit element occurs inside this selected section. No replacement with CC-BY, repeated license audit, or upstream-pinning change.

Worker read-only checks pass:

- XML parsing; unique authored IDs; all168 source IDs retained; all47 block selectors match exact source order.
- EN/ID selected-ID parity and independently read collection adjacency.
- 18 problem/solution pairs and bidirectional links; 48 total local links resolve; six HTTPS links.
- Allowed markup check using a **keys-only image stub**, not a frozen-asset or production build claim;26 image references all accounted for.
- 80 displayed-math regression strings exactly match config; target text NFC. These checks are regression checks, not independent proof of their own contents.
- Personally checked source table rows and every source graph against actualpixels; documented source-description differences above.
- A separate read-only arithmetic pass recomputed all28 table outputs from their actual x cells using `2*x-3`, `x*x`, `x*x*x`, square root and absolute value, and matched each ordered-pair cell. All28 pass. Another source-bound pass paired each of the18 original problem IDs with its actual sibling source solution ID and checked both target navigation directions; all18 pass.

Draft XML SHA-256: `aff28c7c2fe88ea2f638c6a19c5555a043e43bba6f7d67285d46ab20cee6ae06`.
Draft config SHA-256 before root's asset insertion: `887e5685bead959d20a901d8ba78138783ea0f7f42c4ebc13e1a81b764af736d`.

Pending root workflow: independent mathematics/source/Marathi review; source freeze and26 asset records; final build and format-specific visual checks; global canon/decision/coverage updates; future local cross-unit links; human Marathi mathematics-teacher review. This note does not certify HTML appearance or any PDF. The five-book goal remains active.
