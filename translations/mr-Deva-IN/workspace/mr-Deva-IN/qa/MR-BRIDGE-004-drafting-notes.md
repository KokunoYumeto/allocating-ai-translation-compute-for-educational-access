# MR-BRIDGE-004 drafting notes

Status: full 12-question group drafted and all reported canonical raster corrections incorporated; text/config handed to parent for image freezing and integration. Parent reports that an independent QA agent also viewed all eight canonical rasters and confirmed the data. No build, asset extraction, source freezing, rendered review or commit performed by this subagent. Parent owns the assets, source lock, generic builder/CSS and integration logs.

## Scope, boundaries and classification

The complete first domain/range topic group in A20:m81373 was inspected in both pinned archives, in memory. It has exactly 12 exercises: four explicit ordered-pair sets, four mappings and four point graphs. Selection starts at heading fs-id1167833041789 and ends at exercise fs-id1167836509162, immediately before heading fs-id1167836513559 (Determine if a Relation is a Function). It does not complete Practice Makes Perfect, the module, A20 or the five-book assignment.

Config source_count = 16: one topic heading, three instruction paragraphs and twelve exercise blocks. translated_practice_items = 12; all worked-example, formal-definition, source-resource and original-practice counts are 0. question_ids is empty because the questions are translated source exercises. Six answers newly supplied for source exercises are not new questions or source-authored solutions. The four heading/instruction source blocks remain unclassified_source_blocks under the generic builder's current count scheme.

No untranscribed parent section is selected or claimed. Ordered data-source locators to freeze:

1. A20:m81373#fs-id1167833041789 — topic heading.
2. A20:m81373#fs-id1167836701331 — instructions for explicit pairs.
3. A20:m81373#fs-id1167836694560 — question 1, supplied solution.
4. A20:m81373#fs-id1167829738657 — question 2, new answer.
5. A20:m81373#fs-id1167836289174 — question 3, supplied solution.
6. A20:m81373#fs-id1167836513003 — question 4, new answer.
7. A20:m81373#fs-id1167836309438 — mapping instructions.
8. A20:m81373#fs-id1167824736897 — question 5, supplied solution.
9. A20:m81373#fs-id1167836600990 — question 6, new answer.
10. A20:m81373#fs-id1167833128978 — question 7, supplied solution.
11. A20:m81373#fs-id1167829590523 — question 8, new answer.
12. A20:m81373#fs-id1167825791209 — graph instructions.
13. A20:m81373#fs-id1167836621459 — question 9, supplied solution.
14. A20:m81373#fs-id1167833274699 — question 10, new answer.
15. A20:m81373#fs-id1167836707143 — question 11, supplied solution.
16. A20:m81373#fs-id1167836509162 — question 12, new answer.

Each source paragraph, exercise, problem, solution and media ID is preserved. Navigation uses the full source problem and solution IDs. New answers have mr-answer-fs-id... identifiers containing their source exercise ID and are marked data-kind=original with visible new-answer labels. Numbers 1–12 are local reader labels, not an assertion about original rendered exercise numbering.

## Source inspection and media authority

Inspected full selected text, IDs, MathML values, media descriptions and supplied solutions from:

- downloads/mr-Deva-IN/releases/A20-canonical.zip; root osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/; modules/m81373/index.cnxml.
- downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip; source/modules/m81373/index.cnxml.

The eight unchanged English canonical JPEGs are referenced with asset: names for the parent's restricted offline-asset builder. They are NOT replaced by coordinate lists in the visual question text. Parent will freeze exact bytes/path/hash/MIME and copy only these small selected assets. Every image has Marathi alt and an explicitly original caption explaining English labels. No original mapping/graph is redrawn by this subagent.

| Question | Canonical archive member after root | Preserved media ID |
|---|---|---|
| 5 | media/CNX_IntAlg_Figure_03_05_201_img_new.jpg | fs-id1167829693415 |
| 6 | media/CNX_IntAlg_Figure_03_05_202_img_new.jpg | fs-id1167829614618 |
| 7 | media/CNX_IntAlg_Figure_03_05_203_img_new.jpg | fs-id1167829850494 |
| 8 | media/CNX_IntAlg_Figure_03_05_204_img_new.jpg | fs-id1167836328549 |
| 9 | media/CNX_IntAlg_Figure_03_05_205_img_new.jpg | fs-id1167836623119 |
| 10 | media/CNX_IntAlg_Figure_03_05_206_img_new.jpg | fs-id1167836599640 |
| 11 | media/CNX_IntAlg_Figure_03_05_207_img_new.jpg | fs-id1167836524483 |
| 12 | media/CNX_IntAlg_Figure_03_05_208_img_new.jpg | fs-id1167836546296 |

### Material source discrepancies: canonical pixels govern

The parent directly inspected all eight EN rasters and compared relevant ID redraws. This subagent did NOT personally view those pixels; the following production corrections use the parent's explicit pixel-reading reports. Do not downgrade them to an alt-text-only check or claim independent visual confirmation by this subagent.

- Graph 205: both EN and ID alt say (-3,-1), while the supplied source solution says (-2,-1). Parent confirms EN raster has (-2,-1); ID redraw actually has (-3,-1). Marathi alt now follows EN pixels and the supplied solution. Full canonical set: (-3,4),(-2,-1),(0,-3),(2,3),(4,-1),(4,-3).
- Graph 208: both EN and ID alt suggest (-2,-3) and (3,6); the ID redraw actually contains those changed points. Parent confirms EN raster instead has (-1,-3) and (2,6). Canonical points: (-2,-6),(-1,-3),(0,0),(0.5,1.5),(1,3),(2,6). Marathi alt, newly authored answer and domain now follow EN pixels. Fractional coordinates 0.5 and 1.5 remain. This changes the correct domain from the misleading five-value alt-derived set to {-2,-1,0,0.5,1,2}.
- Mapping 202: parent confirms EN Amy maps to February 24 whereas ID redraw maps to February 14, which also occurs in the original EN/ID alt. Question 6 alt, newly authored pairs and range are corrected to 24 फेब्रुवारी. All remaining EN202 mappings were confirmed individually by parent: Carol-May30, Devon-Jan5, Harrison-Jan7, Jackson-Nov26, Labron-Apr7, Mason-Jul20, Natalie-Mar1, Paul-Aug1, Sylvester-Nov13.
- Parent independently reread graph 206 and confirms EN/ID both match (-3,4),(-3,-4),(-2,0),(-1,3),(1,5),(4,-2). The suspected additional 206 raster discrepancy was NOT substantiated and must not be reported as an error.
- Parent confirms BMI203/204 domain/range values agree with the records used here. Parent explicitly reconfirmed all EN201 mappings: Rebecca-Jan18, Jennifer-Apr1, John-Jan18, Hector-Jun23, Luis-Feb15, Ebony-Apr7, Raphael-Nov6, Meredith-Aug19, Karen-Aug19, Joseph-Jul30. Those match the draft and supplied source answer; no change was required.
- Independent QA, relayed by parent, identified two more alt-only axis-label errors: EN205 axes are labeled -5 through5, not -6 through6; EN208 axes are labeled -7 through7, not -10 through10. Marathi alt is corrected accordingly. EN206/207 labels -6 through6 are confirmed. These are labeled axis extents, not the relations' domains or ranges.
- BMI 203 source English answer has +100 and typographic spaces inside 17. 2; Indonesian uses 100 and decimal commas. Draft preserves +100 in the supplied answer, explains +100=100 in prose, uses ordinary decimal points consistently, and removes internal decimal-space artifacts. BMI decimals are labels supplied in this mapping exercise, not recomputed clinical measurements.

No canonical archive, Indonesian file, pin, or existing source notice has been altered to hide a discrepancy.

## Canon consultation: actual reads and concrete effects

### Selection and initial drafting

Read actual MR-BRIDGE-001 relation/domain/range definition, its five-pair example and the function/unique-output clarification. This keeps terms consistent and prevents inferring an all-real domain from finite data.

Fresh web search returned readable MV-F prose (https://marathivishwakosh.org/21979/) for C14-C16. Read its exactly-one correspondence, domain/codomain and constant-function prose, not only the shared terminology ledger. Kept प्रांत and मूल्यसंच. Added the narrowly relevant reminder that a relation need not be a function for its domain/range to exist. Repeated first or second values are deduplicated only in sets, not by dropping source pairs; different names sharing a birthday remain valid mappings. No image-only formula in the entry was treated as read.

### Revision after source-image evidence

Read actual C18 prose from https://vishwakosh.marathi.gov.in/24316/, जात्याक्ष आलेख paragraphs: horizontal/vertical axes, positive/negative orientation and ordered coordinate construction. Added an original x-first/y-second reading reminder, retained source x/y identifiers rather than replacing them with the witness's क्ष/य, and explicitly prohibited joining the finite source dots. The witness's examples of line joining/interpolation do not authorize adding points to these finite relations. No formula or illustration from the Marathi canon is reproduced.

Read actual C19 opening two paragraphs from https://vishwakosh.marathi.gov.in/27548/ via search-reader prose after direct reopen returned 502. Its range name कक्षा and later स्वयंचल/परचल are recorded as variants, not silently substituted for established मूल्यसंच and other workflow terminology. The opening range-as-image-set distinction confirms deduplicating actual output values, not copying an entire displayed codomain. Later advanced content was not used for this task. This is a reference consultation, not a new local HTML download.

## BMI source wording and separated correction

The original two BMI problems describe BMI as body-fat measurement and call 18.5–24.9 healthy. The draft preserves that wording explicitly as a statement of the original source, then links to a separate original correction rather than silently rewriting the source as if it already said something different. Source heights, weights, BMI labels and stated band remain unchanged; neither health classification nor a request to calculate a reader's own BMI is added.

Actually consulted primary-source prose:

- https://www.cdc.gov/bmi/about/index.html (December 16, 2025): BMI does not directly measure body fat; individual interpretation uses other information.
- https://www.cdc.gov/bmi/faq/ (June 28, 2024): BMI interpretation differs for children and adults and is not a standalone health determination.

Parent also directly checked these pages. The correction is short, explicitly original, and not medical advice. The Marathi expression शरीरद्रव्यमान निर्देशांक and प्रतिचित्रण remain provisional wording here; no uninspected Marathi terminology witness is claimed.

## Checks and remaining integration work

Read-only checks passed: NFC/XML/exact locale and unit ID; all 60 selected original IDs preserved in original order; 72 unique total IDs; 30 local links; 40 exact math strings; 16 ordered source selections; 12 source exercises; eight unique asset references; empty original-question inventory. Independently projected each of the 12 displayed pair collections to its domain and range and checked that each displayed answer set is correct and deduplicated. After final 202 correction the projection/check-string checks were repeated. These checks verify text/math consistency; raster verification is the parent's separately recorded work. No build or cache-writing import was used.

The parent's tasks remain: freeze all eight images, populate config.assets, make restricted image support available, freeze the 16 selections, build and visually review the complete reader, then integrate decisions/canon consultations into shared logs. The draft must not be reported built or reader-verified before that work. At handoff this subagent releases ownership of all three004files and will not make further edits without coordination.

## Exact next cursor

Resume at A20:m81373#fs-id1167836513559, the next topic heading, followed by instruction fs-id1167833060894 and first exercise fs-id1167829666517 (problem fs-id1167833059308; paragraph fs-id1167833059310; supplied solution fs-id1167833137411; solution paragraph fs-id1167833137413). Those EN/ID blocks were inspected to establish the boundary, not translated in this unit. The next exercise relation is {(-3,9),(-2,4),(-1,1),(0,0),(1,1),(2,4),(3,9)}; its source asks whether it is a function and for its domain/range. No graph-section jump is implied by this cursor.

Before first writes C: AvailableFreeSpace was 3,851,988,992 bytes. Only this file, translations/MR-BRIDGE-004.xml and units/MR-BRIDGE-004.json were created/edited. No downloads, full archive extraction, deletion, source mutation, build, cache generation or commit was performed by this subagent.
