# Source discrepancies and explicit corrections

These are production findings in already pinned inputs, not a new source/license audit. Original files, hashes and notices remain unchanged. The canonical source is A20 EN commit 38cae454e644abf9f0a623e876994553881597c9; the comparison is Indonesian v0.3.0-wip. Unit locks retain both selected CNXML variants and image metadata. Raster filenames below share the prefix `CNX_IntAlg_Figure_03_05_` and suffix `_img_new.jpg`.

## MR-BRIDGE-004 / A20 m81373

| Evidence | Canonical reading | Conflicting reading | Applied treatment |
|---|---|---|---|
| Figure 202; media fs-id1167829614618 | Amy → February 24 | Indonesian raster and EN/ID alt say February 14 | Embed EN; Marathi alt and new answer use 24 फेब्रुवारी |
| Figure 205; media fs-id1167836623119 | Point (-2,-1); both supplied EN and ID answers agree | EN/ID alt and Indonesian raster show (-3,-1) | Preserve EN image and supplied answer; correct Marathi alt |
| Figure 208; media fs-id1167836546296 | Points (-1,-3) and (2,6) | EN/ID alt and Indonesian raster substitute (-2,-3) and (3,6) | Marathi alt and new answer follow EN pixels |
| Figure 203 source solution | +100 is the same numeric value as 100; decimal labels use points | Indonesian normalizes the sign/decimal separator; EN has internal decimal spacing artifacts | Retain +100 in translated supplied answer; normalize typographic spaces and explain equivalence |

Both rasters for all eight figures were visually compared by the primary agent. A second agent independently inspected all eight EN rasters. Figures 201, 203, 204, 206 and 207 have no observed mathematical raster discrepancy; differing bytes alone are not described as a data error. Figure 206 was rechecked after an initial suspicion and matches. Corrected draft-only alt extents: 205 has labels -5…5, 208 -7…7; 206/207 -6…6.

For figure 208 the full canonical set is {(-2,-6),(-1,-3),(0,0),(0.5,1.5),(1,3),(2,6)}. Its six-value domain is {-2,-1,0,0.5,1,2}; do not reconstruct a five-value domain from the misleading alt text.

The canonical 208 relation is a function; the ID redraw repeats x=-2 at different y-values and therefore changes that result. Neither exercise 202 nor 208 supplies a source answer: their Marathi answers are labeled original work derived from the canonical pixels. The coordinating task independently checked all six affected fragments and six images against their pins and confirmed these distinctions on 2026-08-30.

### Separated BMI context correction

Source problems fs-id1167833128980 and fs-id1167829590525 call BMI a body-fat measure and describe the stated band as healthy. Their numbers and source-attributed wording are preserved. An explicitly original note explains the limitations of that description, using [CDC's BMI overview](https://www.cdc.gov/bmi/about/index.html) and [CDC's interpretation FAQ](https://www.cdc.gov/bmi/faq/), both actually read on 2026-08-30. The note is contextual correction, not personal medical advice; no health values are recomputed or added.

No whole-module correctness certification or upstream issue submission is implied by these findings.

## MR-BRIDGE-005 / A20 m81373

| Evidence | Verified reading | Source defect or conflict | Applied treatment |
|---|---|---|---|
| Exercise fs-id1167829745706, supplied range | {0, 1, 8, 27} | EN omits the opening brace; ID includes it | Restore only the brace with a visible correction note; preserve positive outputs for negative inputs |
| Mapping instruction fs-id1167836552752 | A relation has a domain/range even if it is not a function | Both source instructions call all requested sets those of a function | Translate that wording and add a clearly original clarification |
| Exercise fs-id1167836697708 / figure 211 | Canonical pixels and ID agree on Randy, RHernandez, DBrown, jenny@aol.com and Randy@gmail.com | EN answer has R and y, RHern and ez, DBroen, jenny@aol.cvom and R and y@gmail.com | Keep the source answer ID; visibly identify all five corrected strings |
| Figure 212 / media fs-id1167833256812 | Canonical EN uses lowercase rachel@state.edu | Both source alts and ID raster use uppercase Rachel | Marathi alt/new answer follow EN pixels; caption states lowercase r |
| Figure 212 / Matt label | mattg@gmail.com | EN image has a typographic gap after @ | Normalize the gap in text and explicitly state that choice in the caption |

Primary, drafting and independent mathematical reviewers each read the EN/ID images 209–212. All arrow endpoints agree between the raster editions. The email strings are printed mathematical examples, not contact links. The six omitted answers in this group are new labeled answers to existing source questions, not supplied-source translations.

## MR-BRIDGE-006 / A20 m81373

Printing-cost exercise fs-id1167833380107 defines C(x), but its EN supplied solution prints N(0) and N(1000). ID already corrects those to C. The Marathi draft retains the original answer ID, uses C, preserves the values 1500 and 4750, and visibly attributes the symbol correction to the EN source. Original EN/ID witnesses remain unchanged. The independent source/math reviewer checked this correction; primary PDF review is now complete, while revised HTML visual QA remains separate and unresolved.

## MR-BRIDGE-007 and008 / A20 m81373

Unit007 preserves the canonical self-check image, all nine empty rating cells and the unanswered personal reflection prompts. These must not be filled with invented learner responses. The clipped rightmost HTML phone column is an artifact-layout issue, not a source-data discrepancy; it remains open despite the separately reviewed PDF's complete table.

For008, the primary read the EN/ID mapping rasters and selected text, then checked the PDF's preserved data. Figure001 shows Liz mapped to August2; the EN alt instead says July24. Figure002's canonical label is Khan Nguyen, whereas the EN/ID text and ID redraw use Khanh; the EN supplied-answer split “JoseHern and ez” is corrected to the label Hernandez. Figure003 similarly has an “Arm and o” split corrected to Armando. The visible Marathi notes identify these differences; supplied answer IDs remain intact. The finite point diagrams are not extended by interpolation or confused with their displayed axis windows. Exact literals, full mapping data and scope are recorded in008's primary and independent reviews, not reconstructed from this abbreviated ledger.

## MR-BRIDGE-009 / A20 m81373

The independent reviewer actually read all26 EN/ID images, including ten equation-image pairs; only three mappings are embedded. Root read the complete findings and reran all19 tests. These are independently observed source discrepancies, not a claim that root repeated every pixel reading.

| Evidence | Defect or conflict | Explicit treatment |
|---|---|---|
| Try It2(a), solution fs-id1167836798080 | EN range lists2 twice and omits1 | Preserve the source answer identity but use the pair-derived set{−3,−2,−1,0,1,2,3}, corroborated by ID, with a correction note |
| Try It1 wording | Calls the requested sets those of a function even though part(b) is not a function | Use relation with the source wording disclosed |
| Figure009 | Pixels give123-567-4839 and753-469-9731; EN alt gives4389 and EN answer gives743 | Preserve literal pixel labels, explicitly correct the text; these are mathematical labels, not phone links |
| Figure008 | Canonical pixels use “Love It or List It”; EN alt/answer use lowercase “it” | Disclose capitalization normalization; preserve all arrows |
| After x+y²=3, paragraph fs-id1167836539656 | Both sources claim two real outputs for everyx | Explain x<3 gives two, x=3 one and x>3 none; one valid repeated-input counterexample already disproves being a function |

The three original backreferences into008 remain explicit HTTPS English-source links in this standalone draft. Full m81373 assembly can localize them only because their exact targets are then present; this is an assembly obligation, not another source exercise or a claimed live-link check.

## MR-BRIDGE-010 / A20 m81373

The independent reviewer read both sources and all12 original equation strips; root read the full review and reran18 tests. EN answer fs-id1167836732807 omits thef in f(2)=13; the translated supplied answer restores it visibly, agreeing with ID and exact substitution. EN013b's garbled alt is replaced by the actually pictured y=4·2−5. EN/ID013c's horizontal-line wording is qualified: y=3 is the evaluated result at input2, not a claim that the original function is constant.014b's EN raster colors only the substituted right-hand2, unlike ID's two red2s; the Marathi alt follows EN. The source's “constant input” transition is qualified because the preceding selected example also evaluatesf(a). All corrections remain distinct from original source text and do not add newly selected worked examples.

## MR-BRIDGE-011 and complete-module assembly / historical adaptations

These are completeness repairs to earlier Marathi adaptations, not newly discovered incorrect source mathematics.011 preserves all65 source identities and all26 rows of six tables for the four m81373 blocks already selected in001. Original017b's unsimplified canonical expression is kept despite ID's simplified redraw;018b/018c's repeated equation rows and the final blank explanatory cell are retained;020e's underbrace meanings and separate unannotated020f row survive. All28 media identities remain on readable transcriptions. The independent reviewer inspected all56 EN/ID images.011 adds zero unique selectors and leaves historical001 unchanged.

The following full-module assembler also found historical002's Sylvia solution compressed four source rows into three paragraphs and attached021a's media identity under the problem. Its new assembly restores all four rows, correct solution ancestry and the separate “Simplify” instruction after actual reading of all eight EN/ID021a–d images. Historical002 remains the documented condensed adaptation, unchanged and reproducible. Primary source integration subsequently passed after direct raw-table/target reading, complete ID/answer/input checks and17tests. New reader QA remains a distinct obligation; presence of625 IDs alone is not complete-module acceptance.

## MR-BRIDGE-012 / A20 m81374

The independent reviewer read both sources, all36 fragments and all12 original images; root read the full review and reran19 tests. Here the raster prefix is `CNX_IntAlg_Figure_03_06_`.

- Figures002(a) and003 show axis marks−6…6, not the EN/ID alts'−10…10;006(b) likewise shows−6…6 rather than−12…12. Marathi captions/alts match the actual pixels.
- Figure004's rightmost dashed line isx=2. EN alt contradicts itself with a laterx=3; both rasters and ID confirm2. Do not invent exact intersection ordinates from the image.
- The absolute-value readiness backlink m81423#fs-id1167835365552 actually points to integer addition. Keep the original reference, disclose its mismatch and give the needed absolute-value explanation locally. Other readiness references retain their correct original operations/square-root targets.
- The initial authored footer's CC-BY link was corrected by root to the already pinned component's CC BY-NC-SA4.0 wording. This is a footer repair against existing evidence, not a new general license audit or a source-pin change.

The vertical-line criterion remains every vertical line and at most one intersection; zero intersections outside the actual domain are allowed. Positive graph judgments use the source-declared line/parabola geometry, not a theorem inferred from a few sampled points. All six supplied solutions and12 subparts remain source-attributed; extra reasoning is original.

## MR-BRIDGE-013 / basic functions

The independent reviewer personally read all52 EN/ID originals, complete selected prose and all28 raster-table rows. Primary read the complete report and reran22tests; this is not a claim that primary repeated every pixel reading.

- Figure008 EN permits all real m,b but claims all-real range; ID adds m≠0. Both preceding prose versions omit the restriction. The Marathi qualification distinguishes nonzero slope from m=0, whose range is{b}; canonical EN pixels remain unchanged.
- Figure010 EN pixels already show{b}; only its EN alt drops the braces. Do not relabel that as a raster error. Identity naming remains a descriptive authored phrase, not a claimed exact canon term.
- Figure306 opens downward, contrary to the source alts' upward description. Source table/graph extents and mislabeled windows in009a/013/014/015/016/017/018 and the absolute-value graphs are individually corrected or qualified in the unit's captions and independent report. Formula points outside a smaller visible window are not asserted to be visible dots.
- Source Try6 and example5 omit an explicit graphing verb; the short added instruction is labeled original. Finite table samples do not prove the entire graph/range; the family-specific arguments remain separate.

## MR-BRIDGE-014 / reading a graph

All12 EN/ID originals and58source MathML trees were independently read. Primary read the complete findings and reran19tests. Figures021/023/024 have source-described axis windows that differ from actual pixels; the target follows the actual window without substituting it for domain/range. The malformed source `f = (π/2) = 2` and `f = (−3π/2) = 2` are visibly repaired as function application, with arguments/results unchanged.

Independent review caught a Marathi attribution defect: unlike024/026, neither EN025 nor ID025 expressly says its wave repeats; both say the line extends indefinitely. Primary read all three source descriptions and corrected the intro,025alt and TryIt3's added global-family explanation. Source answers remain unchanged. The extra `(nπ,0)` family and repeated-wave rationale are explicitly conditional/authored, not conclusions from arrows or a finite window. Closed-window source requests and unconstrained source prompts remain distinguished.

## MR-BRIDGE-015 / recap and section exercises

The independent reviewer personally read all88 original files, all54questions/122math subparts and25supplied answers. Primary read the complete report and reran23tests;29source omissions remain reader-visible, not invented answers.

- EN027 repeats the unqualified all-real affine-range claim; ID includes m≠0. EN028 shows bareb while ID shows{b}. The Marathi notes explicitly correct the range-as-set issue and distinguish intercept valueb from point(0,b).
- Figure317's pixels and question are `−2x+2`; both source alts give coordinates for `−2x−2`. The corrected target description follows the unchanged image/question, with the source error disclosed.
- Figures202/203/205 contain incorrect source-alt coordinate signs; actual pixels govern. Axis/window differences, off-window cubic points and exact versus approximate branch readings are explicitly qualified, as detailed in the complete independent report.
- Both source215/216 descriptions do state continuing patterns. The extra global zero/intercept explanation forq47 remains visibly separate from the five finite source-listed values. Unlike014/025, this source premise is actually present.
- All nine learner ratings remain empty; the four writing prompts have no fabricated supplied responses.

## MR-BRIDGE-016 / linear-equation Chapter Review

The independent reviewer read all24original images and both complete source topics. Primary read the full report and reran26tests. Both locales' figure351 alts give(1,−1),(2,3), which fail the actual equation y=4x−3; the pixels agree with(1,1),(2,5). Both figure366 alts give opposite-slope pairs(−1,4),(1,−4), while pixels/question are y=4x and agree with(−1,−4),(1,4). Each discrepancy is reader-visible and the original JPEGs remain unchanged.

Forq27 the two intercepts coincide at the origin. A clearly original note supplies the distinct point(1,4) and verifies4=4·1; a single intercept cannot determine the line. This supplements a supplied graphical answer, not one of the13missing source answers. Figure349's four dots remain a finite unjoined relation; vertical x=3 is not described as a function y(x).

## MR-BRIDGE-017 / slope Chapter Review

The independent reviewer personally inspected all18 original rasters and both full source topics. Primary read the complete report and reran28tests, without claiming a new primary pixel reading. Figures222–225 actually show axes−8…8; both source alts say−6…6. The target corrects the axis descriptions visibly and keeps original JPEGs. Figure376 actually labels the axes h/P rather than the source alts' generic x/y; the target explicitly maps graphh to the question's lesson-counts and retains unequal numerical scales.

Both sources really print `y = (2/2)x + 2` atq29. That unsimplified display is intentionally preserved; its slope is1. The method answers are examples of convenient methods, not unique mathematical possibilities. Piano lessons are counted, not distinct students, and the graph's visible window is not the whole permitted count domain. All18 omitted solutions remain omissions; review-only calculations are not added as source answers. No new defect was found in the reviewed target.

## MR-BRIDGE-018 / finding a line equation

The independent reviewer read both complete source topics and all eight original images. Primary read the complete report and reran27tests, without claiming its own fresh pixel inspection. Both source alts for226–229 give axes−10…10; pixels show−6…6. Figure228's alt point(8,4) satisfies its line but is outside that frame; the target describes the actual highlighted(4,1) and intercept(0,−2), preserving the distinction between wrong and merely off-frame data.

Generic source slope–intercept instructions govern vertical-resultq15,19,23. A clearly original qualification retains the instructions, names the exception and gives genericx=c, without inventing the missing answersx=3,−2,−1. All twelve supplied equations satisfy their actual constraints. Point–slope and perpendicular formulas retain their nonzero/finite-slope conditions. No target correction was requested.

## MR-BRIDGE-019 / graphing linear inequalities

The independent reviewer read the complete topic and both locale copies of all eight rasters; primary read the complete report and reran29tests. Figure378's actual boundary is solid, as the inclusive inequality requires, although the EN alternative description says dashed; ID omits the line-style word. Figures380/382 are visibly dashed, while their ID descriptions again omit that fact. The target distinguishes an omitted description from a changed raster and leaves every canonical image unchanged.

Figure384's axes visibly run0…60 by tens, not0…50 as both source descriptions claim. The target reports the actual window and explicitly does not turn that viewing frame into a bound on the mathematical model. Seven genuinely absent source answers remain absent; reviewer computations are not inserted or counted as source answers.

## MR-BRIDGE-020 / relations and functions review

Figure234's EN right-hand rows are visually ordered20,35,30,45,40,25,50; the Indonesian redraw sorts those rows. Tracing the arrows yields the same seven age→weight pairs in both. The target describes the unchanged EN layout and separately discloses the redraw difference; pairing rows merely by height would change the relation. Figure237's EN alternative description says−1→+1, but both actual rasters, the ID description and the supplied ranges require−1→−1. The visible target correction follows the pixels without altering the original file.

The rational exercise retains the whole denominatorx−1 and an explicitly originalx≠1 clarification. Eleven missing source solutions remain visibly missing; independent calculations are review evidence only. Primary read the complete report and reran30tests.

## MR-BRIDGE-021 / graphs of functions review

Three source defects are preserved as visible corrections. Q11's formula and raster are the constant−6, but EN prints range`(6)` and ID prints`{6}`; the target gives`{−6}` and, for the source's interval-notation request, the equivalent degenerate interval`[−6,−6]`. Q23 asks forf(0), whereas both answers printf(x); the target givesf(0)=0. The same supplied domain closes infinity delimiters; the target restores open infinite endpoints without changing any finite source value.

Q23's broader zero familyx=kπ and intercept family(kπ,0) remain explicitly authored and conditional on the pattern continuing everyπ with no additional zeros. They are not presented as a theorem derived from arrows or a finite raster. Source-alt window mismatches and the curved, not straight, shapes in245/394 are disclosed in the unit. Primary read the complete independent report and reran29tests.

## MR-BRIDGE-022 / Practice Test

The independent reviewer read the complete Practice Test, both locale copies of all12 rasters and every frozen witness; primary read the complete report and reran25tests. Source-described axis windows disagree with pixels for250,251,253,254,397,398 and407; the target follows the exact observed windows and scale increments. EN403 says dashed while ID403 omits that word, though both pixels are dashed. Both405 descriptions call the boundary/shading red, but the actual boundary is solid dark blue and the solution region pink; the target corrects color while preserving inclusion and solution direction.

Q18's nonnegative-hour constraints are a clearly original domain clarification after an explicit missing-source-answer notice; they do not fill the requested model or example pairs. Q25 preserves the literal supplied coordinate-value answers and separately adds complete intercept points as authored explanation. Thirteen supplied answers and twelve source omissions remain exactly distinguished. No XML/config correction was requested by independent review.

## MR-BRIDGE-023 and024 / next-chapter transition

The complete m81375 Introduction's “at the moment” vehicle-autonomy statement is retained as source-era wording and explicitly not asserted as current2026 fact. The source supplies no publication date, separate photo-page URL or individual photo-license statement; none is invented. Both source photo files are byte-identical and the exact `jingoba/Pixabay` credit remains visible.

In024 the two EN equation images remain canonical. Their Indonesian counterparts are distinct larger redraws: the first omits the separate top system but preserves the substitution checks; the second preserves both true equalities and conclusion. The target embeds unchanged EN bytes, provides pixel-accurate Marathi alternatives/transcripts and discloses the layout difference without calling it a mathematical correction. The ID prose has two joins `ydari` and one `Linearkita`; Marathi naturally restores word separation. All six supplied problem/solution outcomes independently pass, so no answer correction is made. The compound for a system of linear equations remains an explicitly authored working choice rather than a claimed verbatim canon term.

## MR-BRIDGE-025 / graphing systems

The independent reviewer read the complete EN/ID section and all46 original image files. Primary read the complete report/test and reran31 independent tests plus the17 freezer and52 generic build/security tests. All15 supplied answers recompute correctly; no answer correction was made.

- Canonical EN figure006e's alternative description says the red line has y-intercept `−4`. The actual pixels, displayed equation and Indonesian redraw all show the red intercept `−3`; the blue intercept is `−2`. The Marathi description follows the pixels/equations and visibly records the EN alt defect.
- ID `fs-id1167832060470` duplicates `y`; five other ID fragments join `y` to the following word. Marathi removes the duplicate and restores natural spacing without changing mathematics.
- Three canonical EN grammar defects are naturalized and disclosed rather than copied as target-language errors.
- ID figure004a omits the intermediate `y=−2x+7`, `m=−2`, `b=7` working that is present in canonical EN. The target retains the complete canonical working and distinguishes the redraw/layout difference.
- The source classifications and solutions remain exact: intersecting systems have one solution, parallel distinct lines have none, and coincident lines have infinitely many. Review-only recomputation is not added as a new source answer.

## Complete A20:m81374 source integration

The complete assembly introduced no new source defect. It preserves the already documented unit-level corrections/disclosures,141 supplied solutions,114 explicit source omissions, nine blank learner ratings and all149 canonical asset bytes. The independent integration reviewer checked source identity, structure, selections, answers, mathematics and all954 input pins, but did not reopen every one of the298 EN/ID rasters. Exact byte preservation is therefore not recast as a fresh semantic pixel review. No HTML/PDF/reader acceptance follows from source integration alone.

## MR-BRIDGE-026 / figure010a correction gate

Both canonical EN and Indonesian figure010a rasters visibly print the erroneous intermediate `15/4`, then jump to `16/2 = 8`. From `6(5/4) − (−1/2)` the correct intermediate is `15/2 − (−1/2)`, so the target's `15/2` is a mathematical accessibility correction, not a pixel-accurate transcription or a target-only typo repair. Independent review stopped acceptance until the alternative description and drafting note explicitly distinguish the embedded source pixels from the correction and the unit is refrozen/rebuilt/retested. No MR026 answer or accepted-working total is advanced while that gate is open.
