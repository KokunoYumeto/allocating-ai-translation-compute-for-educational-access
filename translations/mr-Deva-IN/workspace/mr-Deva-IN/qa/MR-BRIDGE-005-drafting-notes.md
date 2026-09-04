# MR-BRIDGE-005 drafting notes

Status: complete selected 12-question topic group drafted and text/config handed to parent for freezing, build and render QA. This subagent wrote only the MR-BRIDGE-005 XML, JSON and this note. The explicitly authorized review-images command copied eight individual EN/ID rasters to ignored scratch; no full extraction, downloads, shared-tool changes, source-lock changes, build, deletion or commit was performed. This checkpoint does not complete the module, A20, or the ongoing five-book assignment.

## Exact scope and cursor

Inspected the complete contiguous group in both pinned archives, in memory:

- EN: downloads/mr-Deva-IN/releases/A20-canonical.zip; member osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml.
- ID: downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip; member source/modules/m81373/index.cnxml.

Selection begins at A20:m81373#fs-id1167836513559, Determine if a Relation is a Function, and ends with exercise fs-id1167833212947. There are four ordered-pair exercises, four mapping exercises, and four exercises containing three equations each. All 12 source exercises and all six supplied solutions are translated. Answers for source questions 2, 4, 6, 8, 10 and 12 are newly authored and visibly labeled; they are not new questions. Additional explanations and source-correction notes are marked data-kind=original.

NEXT is exactly A20:m81373#fs-id1167836714017, Find the Value of a Function. Its instruction is fs-id1167829717540, asking for f(2), f(−1), f(a); first exercise fs-id1167823013283 gives f(x)=5x−3. Both archives agree on this boundary. That next topic has not been translated by this checkpoint.

Config classifications: source_count 16; translated_practice_items 12; translated_worked_examples, translated_definitions, translated_resource_notes and original_practice_items all 0; question_ids empty. The four heading/instruction blocks remain unclassified source blocks under the generic builder's scheme. No untranscribed parent section is selected or counted.

Ordered data-source locators:

1. A20:m81373#fs-id1167836513559 — topic heading.
2. A20:m81373#fs-id1167833060894 — ordered-pair instructions.
3. A20:m81373#fs-id1167829666517 — question 1, supplied solution.
4. A20:m81373#fs-id1167836688996 — question 2, new answer.
5. A20:m81373#fs-id1167829745706 — question 3, supplied solution.
6. A20:m81373#fs-id1167833138708 — question 4, new answer.
7. A20:m81373#fs-id1167836552752 — mapping instructions.
8. A20:m81373#fs-id1167829742787 — question 5, supplied solution.
9. A20:m81373#fs-id1167829741614 — question 6, new answer.
10. A20:m81373#fs-id1167836697708 — question 7, supplied solution.
11. A20:m81373#fs-id1167833024527 — question 8, new answer.
12. A20:m81373#fs-id1167836705602 — equation instructions.
13. A20:m81373#fs-id1167836705606 — question 9, supplied solution.
14. A20:m81373#fs-id1167836480280 — question 10, new answer.
15. A20:m81373#fs-id1167836526018 — question 11, supplied solution.
16. A20:m81373#fs-id1167833212947 — question 12, new answer.

All 56 original paragraph, exercise, problem, solution and media IDs are retained exactly in source order. The new answer anchors are mr-answer-fs-id... containing the full corresponding source exercise ID. Questions link to original solution IDs or these explicitly original answer anchors, and answers return to original problem IDs. Local labels 1–12 do not claim the rendered book's numbering.

## Source fidelity, discrepancies and mathematical decisions

- Question 3's EN supplied range is `0, 1, 8, 27}`: the opening brace is absent. ID has `{0, 1, 8, 27}`. Marathi restores only the opening brace and explains the correction next to the retained source solution ID. The positive outputs at negative inputs are deliberate source data; do not replace this relation with x cubed. Question 4 instead has negative outputs at negative inputs.
- The mapping instruction calls every requested domain/range that of a function, although question 7 is not a function. The translated source wording keeps फलनाचा, followed by an explicitly original note explaining that the relation's domain and range still exist. This is not silently reattributed corrected wording.
- Question 7's EN supplied answer corrupts Randy as `R and y`, RHernandez as `RHern and ez`, DBrown as `DBroen`, and `jenny@aol.com` as `jenny@aol.cvom`; it also corrupts Randy's email. The original EN raster and ID text agree on the correct names/addresses. Marathi gives the readable corrected answer under the original solution ID, labels the corrections, and preserves the erroneous source strings in its visible correction note. Original archive bytes and source provenance remain authoritative witnesses, not overwritten files.
- Figure 212's EN pixels contain lowercase `rachel@state.edu`, whereas both source alts and the ID redraw use uppercase `Rachel@state.edu`. Canonical EN pixels govern the Marathi alt and new answer. The EN Matt label visibly contains a typographic space after @; the text normalizes it to `mattg@gmail.com`, agreeing with source alt and ID. The caption explicitly records both the lowercase r and spacing normalization. Neither is an arrow change.
- Mappings remain visual questions using unchanged canonical EN rasters, not replacement coordinate/pair-list problems. Alt text describes arrows for accessibility; original Marathi caption keys explain unchanged English headers. The source names and email labels are not translated into different identities, and are not mailto/contact links.
- Repeated inputs are tested for different outputs; repeated outputs alone are allowed. The question 2 no-answer is witnessed by 9 mapping to −3 and 3. Jenny and Raul each have two different email outputs in question 7. Both absolute-value and square mappings are functions despite shared outputs.
- All finite relation domains/ranges contain only given values, deduplicated. No inferred all-real domain or extra pairs are introduced from an apparent pattern. Range remains the actual output set, distinct from a declared codomain.
- The equation instruction is rendered as whether the equation represents a function. An original scope note makes the conventional interpretation explicit: real variables, y as a function of x. No negative y branch is discarded and no new sign restriction is imposed to force a yes-answer.
- Answers for questions 9–12 are respectively (yes, yes, no), (yes, yes, no), (yes, no, yes), (yes, yes, no). Explicit no-answer witnesses: question 9(c), x=−6 and y=±1; 10(c), x=0 and y=±2; 11(b), x=2 and y=±1; 12(c), x=4 and y=±1. Yes-answers use unique formulas; in particular 12(b) is y=x²+4, not x²−4.
- New rearrangements name the same operation on both sides, including division by nonzero −2 or −4. Superscripts ²/³, mathematical minus signs and Unicode sets adapt source MathML typography without altering variables, signs, quantities or subparts. Source line breaks between halves of one ordered-pair set are not separate relations.
- The selected blocks have no outgoing source link or separate embedded notice. General source/publisher/license attribution follows the existing unit pattern; parent owns freezing inherited notices. No source/license re-audit or change to pins was undertaken.

## Personally inspected source media

Read the existing freezer and used only its authorized `--review-images MR-BRIDGE-005 A20` path for filenames 209–212. Personally viewed every EN and ID result with the image viewer. Each mapping's arrow endpoints and labels were read from pixels, not inferred from alt. The independent second_unit_builder agent subsequently reported its own inspection of all eight images and source blocks, confirming the math and the above case/spacing findings.

The XML references the following four EN assets. Parent will mechanically copy/freeze these selected bytes and insert config.assets; config ownership is released at handoff. Do not substitute ID redraws.

| Local question | Canonical member after EN root | Preserved media ID | EN bytes | EN SHA-256 |
|---|---|---|---:|---|
| 5 | media/CNX_IntAlg_Figure_03_05_209_img_new.jpg | fs-id1167833056754 | 60691 | 2c4708d126a4b2973f8d66f6bbcee026342764f917a1a911d47f5498521ffa08 |
| 6 | media/CNX_IntAlg_Figure_03_05_210_img_new.jpg | fs-id1167829908274 | 60534 | 2ca4bbd57f42b6014a93278db4f373b36f4c8d83daf79f21fa22f414a7e5ff69 |
| 7 | media/CNX_IntAlg_Figure_03_05_211_img_new.jpg | fs-id1167832930332 | 78808 | 580ca185896cb8c30325548d4cacb9fc058c14b36b45d9faf2703f1026d7b6e9 |
| 8 | media/CNX_IntAlg_Figure_03_05_212_img_new.jpg | fs-id1167833256812 | 80398 | 899112b8cfcff1d6049555fcccac5d6d4a1a293f431ae44caf7246b59e36e172 |

No media is omitted. Images 209/210 show −3 through 3 mapping to absolute values/squares. Image 211's seven arrows are Jenny→JKim@gmail.com, Jenny→jenny@aol.com, Randy→Randy@gmail.com, Dennis→DBrown@aol.com, Emily→ESmith@state.edu, Raul→RHernandez@state.edu, Raul→Raul@gmail.com. Image 212's seven arrows are Jon→jong@gmail.com, Rachel→rachel@state.edu, Matt→mattg@gmail.com, Leslie→leslie@aol.com, Chris→chrisg@gmail.com, Beth→bethc@gmail.com, Liz→lizzie@aol.com. The two number mappings and all arrow endpoints agree between EN and ID.

Ignored review copies live at downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-005 with en-/id- filename prefixes. Canonical EN copies total 280431 bytes; ID copies total 1102745 bytes; combined 1383176 bytes. ID SHA-256s for 209–212, in order: 1aa4dc4069e1cb7aef0e52f07622ef9f175fedc21a70b25caf12d42d55c19dc6; 9b189ee9307ff2c615fdb567d4a74609395a694ab8ca35f1936508b867eb70eb; 2b37ef257a0399d3c659f08c9bd0769c5771dd7cf2db58a89ef8dfd62fc28bfc; 8381f42858196422ed75f9c6740ccadb95174f062a918a84f543f8eb3d3c33dc. Different hashes do not themselves establish mathematical differences; pixel comparison does.

## Canon consultation at selection, drafting and revision

Selection/drafting: actually read the existing pilot's relation, finite-domain example and unique-output prose (MR-BRIDGE-001.xml, source IDs fs-id1167833175472, fs-id1167836692527, fs-id1165137932580 and adjacent original clarification). This prevents changing established terms or enlarging finite relations. Read actual C14–C16 prose returned by the initial search retrieval of [फलन](https://marathivishwakosh.org/21979/): exactly-one correspondence, domain/codomain, constant function, and its people-to-work example. Those witnesses guide the distinction between many inputs sharing an output and one input having several outputs. No image-only canon formula was treated as read.

Drafting: read the existing C12 OCR prose in downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt, first 18 lines, on an equation's solution and equal operations on both sides. Used that wording in the new rearrangement explanations. No new PDF download/OCR/page rendering occurred here, and no potentially corrupt OCR formula was used as mathematical authority. The actual exercise equations come from the pinned CNXML MathML.

Revision: reread C12's actual prose and the pilot definitions after the full draft existed. Fresh search-reader retrieval of [फलन, प्रथमावृत्ती](https://vishwakosh.marathi.gov.in/27548/) supplied the opening paragraphs on exactly-one correspondence, domain, codomain and actual image set, plus the square-function example. Retained established मूल्यसंच rather than silently switching to the witnessed variant कक्षा. Checked every finite output set and the shared-output explanations against these distinctions. A fresh direct reopen of the newer 21979 page timed out, and later searches did not successfully recover that page; do not claim a successful fresh final retrieval there. The earlier selection/drafting retrieval and the successful current C12/C19 reads are distinct records.

Targeted terminology expansion during final revision: the starter canon lacked an actually read absolute-value label. Read [गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/) directly, particularly its |क्ष| entry (lines 144–146) and brace entry (230–234). It names केवल मूल्य, explains sign-independent value, and names महिरपी कंस. Changed the provisional label निरपेक्ष मूल्य to witnessed केवल मूल्य in the original caption key, retained the accurate brace-repair wording, and added the source link to credits. The parent was notified of this candidate additional canon witness; this subagent did not assign a shared canon ID or edit the shared ledger. No unrelated advanced notation was imported.

These are active reading records, not claims of Marathi teacher/native-speaker validation. The XML states that limitation. C18 graph-coordinate prose was not needed for this mapping/equation group and is not newly claimed as consulted.

## Read-only verification and remaining workflow

Python -B in-memory checks passed: well-formed NFC XML; 67 unique total IDs; all 56 original source IDs in exact order against both archives; 16 data-source locators matching the complete selected sibling group; 12 exercises and six supplied solutions in each archive; all source problem pairs/equations matched after whitespace/Unicode formatting; 61 exact data-check/config regressions; ten required terms; four asset references; all 28 internal links resolve. There are 32 links overall after adding the targeted terminology witness, none originally outgoing from selected source blocks.

Separately recalculated finite domains/ranges and function status for the four pair sets and four pixel-read mappings. Verified all four two-output counterexamples. Checked the true linear/polynomial rearrangements algebraically and with exact Fraction substitutions from −20 through 20; finite substitution is only a regression check, not the proof of uniqueness. Independent reviewer reports no mathematical or mapping error and is adding repository tests under its own ownership.

Small-write disk check before initial drafting: 6713577472 bytes free on C. Revision check: 11259015168 bytes free. This agent did not free disk space or change storage policy.

Parent's remaining checkpoint work: freeze 16 selected source fragments and four canonical images; insert assets into JSON; run generic builder and test suite; inspect desktop/phone output and correct any layout issues; integrate actual canon/source-discrepancy decisions into shared logs; continue from the exact next cursor. This note is not a build receipt or whole-assignment completion claim. Text/config ownership is released at handoff; coordinate any later edits with parent.
