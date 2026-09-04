# A10-004 source and language notes

## Exact bounded coverage

Translate the complete next section `fs-id1170655247410`, “Find Prime Factorizations and Least Common Multiples,” and its immediately following complete Key Concepts section `fs-id1170655222085`. These are canonical `m82452` content children 5 and 6 (zero-based), with 46 and 2 direct children including their titles. No standalone node is skipped.

The last instructional child is media-resource note `fs-id1170655222063`; the review ends at list `fs-id1166421706953`. Stop **before** `fs-id1170655190123`, class `section-exercises`. That required next section contains 82 exercises, 359 IDs and 5 MathML trees. It is not optional, not included here, and not evidence of a completed module/book. Earlier collection modules m82630 and m82451 have separate checkpoints maintained by the parent.

The canonical collection is A10/col31130, Elementary Algebra 2e, in the pinned prealgebra bundle; do not infer the A10 source from the bundle name or A20 mapping. Canonical source:
`downloads/complete-upstream/osbooks-prealgebra-bundle/modules/m82452/index.cnxml`
SHA-256 `0eaf5db27fd4e16e70d34d4b936abe173b93699e267b519e449c7b56f7233310`; commit `38cae454e644abf9f0a623e876994553881597c9`.

Indonesian comparison:
`downloads/extracted/A10/translated/modules/m82452/index.cnxml`
SHA-256 `940ad448d8b2788984f386405131866fe32abb95f0f9c2a901ca1f4e3619a6fb`.
The full selected English and Indonesian prose, alts, summaries, math and source hierarchy were read. Revision reread the missing24, composite definition, mislabeled method, both erroneous worked-table summaries, review carry claim and historical Java instruction directly from Indonesian CNXML; mathematical data remains canonical English.

## Input-freeze evidence

- Frozen excerpt: 36,694 bytes; SHA-256 `ee9de86ade422d18c55dfc103dde31cb017419e668ea3d66cc89f9ae41805686`.
- Translation after draft/revision/pre-render QA: 74604 bytes; SHA-256 `ee1223a7574b2a7de9adf47df6c42a5a9dd3204dbf124ba9838d243e180c0bc2`.
- Exactly 150 keys in canonical document order: 52 paragraphs, 16 titles, 15 image alts, 3 table summaries, 14 cells (including 1 empty), 48 list items and 2 direct-text notes.
- 168 retained source IDs, 15 MathML trees, 15 original JPEGs totaling 1,015,473 bytes, one numbered figure, 3 tables, 13 lists, 5 worked examples and 10 Try It exercises.
- Exactly 15 math, 12 child and 3 link placeholders; 6 explicit source newlines become 6 br elements. Four child placeholders own nested cell media; eight own nested lists.
- Read-only recursive expanded-name/attribute/text/descendant/tail comparison confirms both excerpt subtrees exactly equal the canonical source. All selected Indonesian tag/ID/image-src/link-target/url sequences match.
- All 488 Arabic-digit occurrences outside MathML are retained with exact per-block multisets. Only `fs-id1170654905180/alt`, `fs-id1170655083625/alt` and `fs-id1167826967413/summary` reorder those occurrences: English “first2 in factorization of12” naturally becomes Punjabi “12 دی صورت دا پہلا2.” Owner/position relations are retained, not swapped. All other prose numeral sequences match exactly.
- All 12 term IDs remain in order. No Gurmukhi, replacement characters or prohibited bidi controls occur. Target fragments and bridge parse as XML-compatible HTML; every correction target exists in the bridge.
- This is pre-render input evidence, not a claim that a reader or independent structural/browser QA already exists. Later code/receipt records supersede only that workflow status.

## Actual canon consultations

The real `scripts/read_canon.py` was invoked at each stage and displayed the readable R1/R2/R3 passages. No missing-stage receipt was invented. The same relevant loci were used for distinct source-analysis, draft, revision and QA decisions, not a reading loop.

- draft: `canon/receipts/A10-004-draft-20260831T020645303990Z.json`; SHA-256 `06d7693d43bb94d80bb6310e70cb55767d224929e2bac940b821163060d56131`.
- next-unit: `canon/receipts/A10-004-next-unit-20260831T015559315572Z.json`; SHA-256 `04088fbfb66963376036208fe497f0b4a145b874692fdf2f044d108935de46e1`.
- qa: `canon/receipts/A10-004-qa-20260831T023432429586Z.json`; SHA-256 `9b478d4b48919f5bac72943a32c1b14119923bc7a34d41238db05b39a6275b78`.
- revision: `canon/receipts/A10-004-revision-20260831T022459924305Z.json`; SHA-256 `9bc0c54dec02748444342798213a7abde0e91dcda5f41b6af036d013ab1ab05f`.

All four consultations read C01, C02, C03, C04, C06, C07, C09, C10, C11 and C12 from the actual locally readable essays. Canon index SHA-256 `734bb92da5edb28f084ef589bbd5af7e4ac40b823036e460073266f63eb30f9c`; reader script SHA-256 `6b5468010e54ae1468d29a6c9fd52cf7b9544ef91b18ef74067a9ac814e7dce2`.

Concrete influence and limits:

- C01/C04: ability and plural agreement: “لکھیا جا سکدا اے”, “دَسی جا سکدی اے”, “دونوں … نیں”, and plural branch/row descriptions. Revision changed cumbersome circled-prime phrasing to “گھیرے والے اوّلی عدد.”
- C02: direct Punjabi instructions “لبھو”, “لکھو”, “گھیرا پاؤ”, “پرکھو”; avoid replacing Punjabi verbal syntax with nominalized Urdu.
- C03/C07: sequential branches and first/second/third arrows, “ترتیب وار”, “دوجے خانے …”, “اُتے/تھلے”; preserve the distinction between column order, factor occurrence and multiplicity.
- C06/C10: alternatives and qualification. Source errors remain faithful source blocks; the correction is explicitly “ساڈی اپنی وضاحت.” Distinguish an error from a scoped convention and from an ordinary spelling typo.
- C09/C11: “چیتے رہوے”, “چیتے رکھو” and “کیوں جے” support reminders and reasons, notably the positive-number convention, carries and missing factor24.
- C12: a clear transition between listing multiples and prime-factor methods, then the explicit still-required exercises cursor.
- The receipt’s legacy `application` descriptions mention earlier PNB examples. They are generic catalog annotations, not claims that those examples were translated in this unit; the decisions above are the actual A10-004 uses.

This is a narrow three-essay Shahmukhi prose canon, not ten mathematical works or specialist terminology certification. No scanned PDF was relied on, no OCR was needed for this born-digital CNXML/HTML task, and no additional corpus was downloaded.

## Provisional vocabulary and source form

“ضربی جزو / ضربی اجزا” (factor/factors), “اوّلی عدد” (prime), “مرکب عدد” (composite), “اوّلی اجزا دی ضرب والی صورت” (prime factorization), and “گھٹ توں گھٹ سانجھا مضاعف” (LCM) are explicit provisional educational choices. The original bridge supplies English and Urdu equivalents without claiming that Urdu prose is Punjabi. Existing “مضاعف”, “ضرب دا حاصل”, “نال پورا ونڈیا جاندا اے”, “گنتی دے عدد”, “صحیح عدد”, “پیریڈ” and “جگہ دی قدر” remain consistent with earlier A10 units.

The long factorization phrase is descriptive rather than an asserted standardized Shahmukhi term; native-speaker and educator review should assess readability. Latin variables, numbers and English tokens in visible prose are LTR-isolated; image alts/summaries are plain text attributes with no injected direction controls.

All 15 source MathML trees must be copied, not retyped. No punctuation relocation is needed: Punjabi clauses end or pause around source terminal punctuation. Source English `and` remains in its MathML mtext; a labeled original key says it means “تے.” Indonesian `dan` and `KPK` are not substituted into the English mathematics or original images. LCM remains the English bridge abbreviation.

Source `prime number` term plus a separately bold English plural `s` has no equivalent separable Punjabi suffix. The target keeps `term-00015` and bolds the full plural term. Source `denominator` plus `s` becomes “مخرجاں” with `term-00020`. This is morphology, not ID deletion.

## Discrepancies and original treatment

1. **72 factors:** canonical and Indonesian lists omit24 although the same source formula contains3·24. Faithful list remains omitted; original full positive-factor list includes24.
2. **Composite definition:** first sentence lacks the condition greater than1 in both languages. Original correction says1 is neither prime nor composite; no silent definition change.
3. **Factor-tree scope:** original note limits the lesson to positive factors, while the earlier integer-factor definition can include negatives. Each branch split must use factors greater than1; otherwise1×n repeats the branch. Uniqueness is up to order with multiplicities retained.
4. **015 classification image:** actual pixels have two panels, each three columns and ten rows (one header plus nine data rows). Sourcealt incorrectly says eleven rows and the right header Factor singular. Both actual headers say Factors. Indonesian retains the eleven-row claim. The full source description is preserved; corrected accessible text has its own provenance and visible advisory.
5. **016a/020a step-image scope:** each file shows only the first step of a four-image sequence. Its sourcealt describes a whole four-row table. Original alt clarifies current-image scope without dropping the following images or silently changing sourcealt.
6. **016c circle:** actual first2 is circled, not underlined as both source languages say. Original alt also clarifies the instruction/tree column positions.
7. **252 stop rule:** “Continue until all primes are factored” is wrong. Preserve it in source cell/summary; original correction stops when all remaining factors are prime. The Indonesian cell and summary already correct this. Original accessible summary announces the corrected rule first.
8. **Method label:** source/Indonesian procedure introduction calls the preceding listing-multiples work the prime-factors method. Original note identifies the listing method; source sentence stays unchanged.
9. **LCM convention/multiplicity:** original note specifies the least positive common multiple. “Each common prime factor once” means one per matched occurrence, not one per distinct prime; repeated2 and3 remain in36.
10. **021 third arrow:** source summary says12/18/second2. Actual cells/pixels and Indonesian show24/36/third2; original accessible summary corrects those three relations and retains the faithful summary trace.
11. **Review carry:** source and Indonesian repeat the all-left-digits-unchanged claim. Original note links the previous source103,978→104,000 example and explains carry changing3to4.
12. **Historical Java instruction:** preserve exact source URL and instruction, visibly labeled as historical, not a recommendation to enable/install a legacy plugin, weaken browser safety or execute a runtime. The original link’s functionality was not established. The browsing tool refused it as unsafe-to-open; that is not proof the public page is dead. [Oracle Java help](https://www.java.com/en/download/help/chrome.html), read at this stage, states the specific Chrome45+ NPAPI/Java-applet limitation; the original warning does not generalize to every Java program.

Ordinary spelling errors `intwo`, `coulmns`, `elipsis`, and `bank` for blank have clear meanings and are translated normally. Exact witness spelling remains. The original020b image says “Math primes vertically”; its sourcealt and Indonesian mean Match. The pixels remain unchanged; the bilingual key gives the intended matching instruction. The018 LCM highlight is aqua/lightblue; the source describes blue. There is no numerical error requiring an added override there.

There are exactly 12 correction/qualification records, 4 separately declared image-alt overrides and 2 table-summary overrides. Use corrected visible alt/aria-label first, preserve faithful translated values in data-source-alt/data-source-summary, and bind both visible links and aria-describedby to real bridge IDs. Source prose error advisories must be adjacent to their owning key, outside the translated text, not anonymous injected source prose.

## Image and mathematics inspection

All15 original JPEGs were opened in original-detail view; the three critical015/016c/021a images were revisited for revision, and the other twelve for final source QA. No image was redrawn, translated in-place, mirrored or recompressed. The manifest records each exact path, byte count, SHA-256, dimensions, existing media-authority row/Git blob and visual observation. Four declarations are image/png despite actual JPEG bytes:017,019,021a,021b. Preserve that source metadata discrepancy, serve the unchanged JPEG, and do not infer a new rights grant from a media-identity row.

The5worked examples remain source module ordinals7–11:48=2·2·2·2·3;252=2·2·3·3·7;LCM(15,20)=60;LCM(12,18)=36;LCM(24,36)=72. Original pixels, source arithmetic and the first two symbolic source results agree.

All10TryIt answers were independently recalculated from the actual source question:
- `fs-id1170655189535` → `fs-id1170655189542`: 80 → 2 · 2 · 2 · 2 · 5.
- `fs-id1170655206369` → `fs-id1170655206375`: 60 → 2 · 2 · 3 · 5.
- `fs-id1170655229697` → `fs-id1170655229704`: 126 → 2 · 3 · 3 · 7.
- `fs-id1170655270016` → `fs-id1170655270022`: 294 → 2 · 3 · 7 · 7.
- `fs-id1170655206437` → `fs-id1170655206444`: 9, 12 → 36.
- `fs-id1170655206459` → `fs-id1170655206465`: 18, 24 → 72.
- `fs-id1170655195923` → `fs-id1170655195929`: 9, 12 → 36.
- `fs-id1170655195944` → `fs-id1170655195950`: 18, 24 → 72.
- `fs-id1170655222009` → `fs-id1170655222015`: 21, 28 → 84.
- `fs-id1170655222030` → `fs-id1170655222056`: 24, 32 → 96.

The actual488-numeral comparison does not prove native-language correctness; long possessive descriptions still require human review.

## Renderer and rights constraints

Use an isolated004 prepare/build/QA pipeline. Retain source mixed-content/tails, direct-text notes, all48items in13lists, four nested cell images and eight nested lists. All3tables have14data cells and no source headers. Keep their empty label metadata and one empty lower-left cell; do not infer a six-header pattern from a different unit. The source review’s place-value link must reach the existing A10-001 figure, with local labelA10-001.2; the current figure usesA10-004.1. The external source URL remains exact and inert until a user follows it.

Use prior A10 natural-width images and a table width that fits the first instruction column in a narrow scroll viewport. Do not edit shared CSS or earlier frozen units. Reject unresolved placeholders, swapped nested media, source-text/anonymous injection, math/number changes and fabricated correction destinations.

Existing A10 notice/license policy is binding, not re-audited. Authors are Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis, not A30 authors. Retain CC BY-NC-SA4.0 subject to component-specific credits/restrictions, nonendorsement and unlicensed-marks notice. Notice hashes use only CRLF→LF normalization; image bytes are exact. No new component-specific clearance is inferred.

At this input freeze, preparation, build, independent structural QA and browser review follow next. Native-speaker, educator and assistive-technology review remain pending. No entire-book, entire-module or entire five-work completion is claimed.

