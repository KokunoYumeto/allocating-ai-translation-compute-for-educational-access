# m81286 Bengali integration peer review

Review date: 2026-08-31. Reviewer: model peer agent `improper_fractions`.

Status: bounded module review complete; R1–R3 corrected by main and verified below. Only this review record is edited by this reviewer. This is not human Bengali teacher, learner, or assistive-technology certification. The reviewer authored Divide Fractions (`fs-id2700526`) and Section Exercises (`fs-id3215450`); those blocks are explicitly self-review. Other module blocks receive model-peer review. The whole language assignment remains in progress.

## Bound inputs and initial checks

- Current reader and browser capture receipt agree on SHA-256 `391dd3dc7126cf3cf7cd0a16ad003b26c22885901f43e8c48a708d8925b2c017`.
- Assembled CNXML receipt SHA-256: `84faf783c1e1cf2719484bf09e323b82c229a6e17ad8decf0543fbd5e43b9dc0`.
- Pinned source SHA-256: `7dab4be4d267ccd47f23df46e9b6a4b90a25c5d8b371e14b5947846af126b249`.
- Module receipt: 12 overlays, 5,491 source elements, 931 IDs, 495 MathML expressions, 38 images. Independent preservation rerun and source/overlay content comparison remain in progress.
- Existing browser receipt reports widths/scroll widths 1200/1200 and 390/390, heights 65,090 and 79,563; all 38 images loaded at both widths; no reported overflow/errors or nonempty zero-size math. These are automated receipt observations, not a substitute for actual visual review.
- Desktop capture set is 1–73. Narrow set contains top and bottom only, not a complete mobile sweep.

## Visual review log

- Desktop 1–6: directly opened all six captures. Readiness arithmetic, fraction-circle count, equivalent examples, simplest-form definition and early signed reduction steps are legible. Question/answer boundaries and labels are visible. No blocking layout or mathematical discrepancy found in this batch. No conclusion about unviewed captures.
- Desktop 7–12: directly opened all six captures. Signed reductions and the final lowest-terms check are legible. The missing-negative-sign source images in tile 8 have prominent visible Bengali warnings and the final answer retains its negative sign. The 210/385 factor trees match their detailed Bengali description and reduce correctly to 6/11. Variable-domain warning is visible before 5xy/(15x). Investigating whether intended cancellation strokes render in that worked table; no conclusion yet.
- Desktop 13–18: directly opened all six captures. Fraction-tile and shaded-grid models agree with 1/2 × 3/4 = 3/8, 1/2 × 3/5 = 3/10 and 1/2 × 5/6 = 5/12. Equal-part conditions and product rule are explicit. Signed multiplication begins with the correct positive product of two negative factors. No new layout discrepancy in this batch.
- Desktop 19–24: directly opened all six captures. Both multiplication-before-reduction and reduction-before-multiplication approaches agree; signed products and integer/algebraic examples are correct in the visible steps. The explanation uses the numerical coefficient's sign for variable products, avoiding the claim that −48x itself must be negative for every x. No new actionable discrepancy.
- Desktop 25–30: directly opened all six captures. Reciprocal pairs multiply to 1, nonzero restrictions are explicit, and the zero/opposite/absolute-value distinction is accurate. Reciprocal calculations and the three-column worked table match the questions. No new actionable discrepancy.
- Desktop 31–36: directly opened all six captures. Both reciprocal-table answer images match their immediate questions, including image 040 in its original correct context. Division tile counts agree with all visible quotients. Self-review identified two prose/retained-MathML punctuation collisions (R2 below); no altered mathematical value.
- Desktop 37–42: directly opened all six captures. Three wholes contain six halves; the US quarter example preserves the original currency and quantity. The division rule keeps all three nonzero restrictions. Signed and variable quotients, including 10/(3n), 21/(5p), 15/(8q) and 6/7, agree with their questions; variable nonzero warnings are visible. No new actionable discrepancy.
- Desktop 43–48: directly opened all six captures. The source bitmap visibly cancels 7 and 9 and gives 3/4; remaining division answers agree. Key concepts preserve domain conditions. Practice begins with the original pattern of provided and absent answers. No new actionable discrepancy.
- Desktop 49–54: directly opened all six captures. Variable reductions, signed products and the two rectangular practice models agree with the Bengali descriptions and numeric answers. No new actionable discrepancy.
- Desktop 55–60: directly opened all six captures. Integer/variable products, powers and reciprocal answers agree. Tile 60's question and preserved answer bitmap intentionally differ; the Bengali caption identifies the actual image values and introduces the separately labelled editorial correction. This is an already documented source erratum, not a newly discovered translation error.
- Desktop 61–66: directly opened all six captures. The corrected rows remain clearly distinguished from the source answer. The second practice table correctly uses 9/14, and its image matches. Division models and signed/variable quotients agree. No new actionable discrepancy.
- Desktop 67–73: directly opened all seven captures. Final sequential division, baking and ribbon quantities, writing prompts, self-check and glossary reviewed. Retained US units are not silently converted. The self-check's English source pixels have a complete visible Bengali description. No new actionable discrepancy.
- Narrow 1–2: directly opened both supplied captures. Top and bottom Bengali text, glossary MathML and footer wrap legibly without visible clipping. This is only a top/bottom narrow-screen sample, not full mobile visual coverage.

## Findings

### R1 — Invisible cancellation strokes in native MathML

Desktop tile 12, example `fs-id2462323`, exercise `fs-id1569561`, table `eip-id1168469401986`: the remove-common-factors row displays `5·x·y/(3·5·x)` identically to the preceding uncancelled row. Directly inspected source XML contains four `menclose notation="updiagonalstrike"` wrappers around the common 5 and x factors. The diagonal strokes are not visible in the supplied screenshot, although the final `y/3` answer is correct.

Reported immediately to main. Suggested renderer-only fallback for `updiagonalstrike`, analogous to the prior long-division enclosure fix, with source MathML unchanged. Other occurrences should be checked. Disposition pending; remainder of review continues.

Follow-up: main supplied a renderer-only CSS-gradient fallback. Directly opened new `sections_m81286-fs-id1408851-1200-10.png`; strokes now appear in the cancellation row. The new section receipt is bound to HTML SHA-256 `ec09ec5139f760e6cfa4b6f2d282c6d67f92476d0aba1439f181d6ca7c4d8f8a`; it reports nonzero bounds and gradient backgrounds on all four enclosures at both widths. An independent source enumeration found six `menclose` nodes in this module: four 5/x factors in table `eip-id1168469401986`, plus two 4 factors in table `eip-id1168467263034`, exercise `fs-id2370170`, example `fs-id1549882`. Full-module refresh and the latter pair remain to be verified. Original capture findings remain tied to the original hash above.

### R2 — Two self-authored prose/MathML punctuation collisions

Desktop 34, paragraph `fs-id1885595`: the second retained MathML expression ends in a period, followed by Bengali `হয়।`, visibly producing `1/4. হয়।`. Rephrase the preceding slots so the verb comes before that expression, and begin the next slot with `প্রথমে`.

Desktop 36, paragraph `fs-id1738644`: the last MathML expression begins with `2,` before the division equation. The preceding Bengali `অর্থাৎ,` leaves that initial 2 grammatically stranded. Introduce the preserved whole number and division equation explicitly in the preceding slot.

These are translation self-review findings, not independent peer certification. Both were reported to main for slot-only correction without changing MathML. Disposition pending.

Follow-up: main reports both slot corrections applied and source MathML inspected. Full-module reader/capture refresh and visual recheck remain pending. Earlier translation-stage punctuation checks did not catch these defects; this review supersedes any broader implication of complete punctuation success.

### R3 — Further self-authored retained-period boundaries

The refreshed desktop 36 exposed `2.-এর মধ্যে।` in paragraph `fs-id1398050`. A systematic module-wide scan of every MathML expression ending in `.`, `?`, `,` or `;` and its following Bengali tail also identified paragraph `fs-id2340005`: a retained period after 1/2 split `আছে এই … অর্থাৎ অর্ধেক মাপের অংশটিতে`, and a later retained comma was poorly anticipated by the sentence. Reported these exact IDs immediately. Main has applied slot-only rewrites which put the verb before the period-bearing quantity and explain the following fraction independently. Final capture verification remains pending. No other actionable punctuation-boundary collision was identified in this systematic scan. This finding narrows, rather than repeats, any earlier broad claim of clean punctuation.

## Source, overlay and structural review

Completed paired reading of the original and Bengali non-MathML text/tails, translated alt, ARIA and summary attributes, and linguistic MathML exceptions across all twelve overlays. This includes the full practice workflow and self-check, not only worked examples. Mathematical displays and all 38 images were covered in the original 73-tile visual sweep; pre-existing arithmetic/image corrections were kept distinct from new review findings.

Independently reran `build.translated` without writing generated files for all twelve overlays. All gates passed; each translated subtree matched the assembled CNXML at the time checked. Independently compared complete source and assembled module: all 5,491 element tags and 931 IDs have the same order; all 495 MathML expressions match after reversing exactly two explicitly allowed English `and` → Bengali `এবং` mtext substitutions. Source image and link attribute sequences match exactly. Both trees contain 156 exercises, 108 solutions and 48 exercises without source solutions. HTML has 931 unique IDs, no broken local fragment target, 38 images and no empty image alt.

A receipt/read hash mismatch observed during main's concurrent R3 rebuild was not accepted as final evidence. The final bound capture/hash check remains pending below.

## Canon consultation

Before the detailed source/overlay terminology comparison, reread `canon/README.md` and actual Tripura p.051 and West Bengal p.181 OCR; opened both corresponding full page images during this review. Returned to the same OCR and page images at the end of the visual sweep, before completing the paired source/overlay check. TR02/TR03 and WB01/WB02 support equivalent-value language, numerator/denominator factors and the explicit exclusion of 1 in the simplest-form definition. The faulty Tripura mixed-number intermediate denominator and faulty WB ratio-example intermediate steps are not accepted as arithmetic evidence. The current reciprocal and fraction-tile terminology remains explicitly editorial/provisional; WB p.181 is not misrepresented as a direct number-reciprocal terminology witness. No new terminology change was required by this reread. Previous translation consultations are not counted as fresh review evidence.

## Final bound verification and limits

Final reader SHA-256 and refreshed browser receipt agree exactly: `119e1ba78619104af5f9691372251d396d978ac3b582cdc86df5148cc2892409`. Final CNXML SHA-256: `a6e56a985182c5ae5fe7707e6b63d4d414ea78cbd9ba0259e5f01af12709d8e1`. Source hash remains unchanged. The final Divide overlay matches its assembled subtree and retains identical source MathML.

Directly re-opened final desktop 12, 33, 34, 36 and 41, plus both final narrow captures. The four 5/x cancellation strokes and two 4 cancellation strokes are now present; the latter pair is in **Divide**, not Multiply (an earlier message shorthand was corrected after inspecting full XML ancestry). Final browser receipts independently report six nonzero-size gradient enclosures at both widths. All four affected prose paragraphs now anticipate the retained mathematical punctuation; R2 and R3 are closed. Final automated widths are 1200/1200 and 390/390, heights 65,090 and 79,596, 495 mathematical displays and 38 images at each width, with no reported overflow/errors.

The original desktop review covered every tile 1–73; subsequent correction verification was targeted, not a second complete 73-tile sweep. Capture filenames were regenerated by main, so chronological observations above are bound to their stated reader hashes. Narrow visual coverage is only the two available top/bottom images, with automated whole-document geometry checks; it does not establish full narrow-screen usability. English original image pixels remain intact with Bengali descriptions, and documented source errors are visibly distinguished from editorial corrections. No additional actionable finding remains from this review. Independent human locale, learner and assistive-technology review is still required; no universal language, mathematical or accessibility certification is claimed.
