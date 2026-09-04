# Acquisition and production receipt — 2026-08-30

## Acquired

- Five pinned repositories: program catalog, A00 Indonesian, A10 Indonesian
  release metadata, shared canonical OpenStax bundle, AX-2 educational-access
  dossier. Exact commits and tree witnesses are in `../sources.lock.json`.
- A00 Indonesian: complete repository checkout, 75 source-ordered module
  references. Canonical English module hashes verified for all 75.
- A10 Indonesian: corrected v1.0.2 editable source archive, 6,397,865 bytes,
  SHA-256 `6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456`.
  All 408 manifest entries and all 82 canonical English modules verified.
  Reader PDF and large backend archive were not needed or downloaded here.
- Canonical bundle: sparse Git checkout of modules/collections/root notices,
  plus complete 537,455,794-byte pinned ZIP available through a read-only NTFS
  hard link. All 13,987 ZIP entries passed CRC. SHA-256
  `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`.
  The hard link shares physical storage; it is not an independent archive copy.
- AX-2: catalog authority snapshot and source dossier, with exact hash matches
  for the portfolio and accessibility-derivative specification files. AX-2 is
  not an independent textbook repository.
- Target-language canon: 36 official KBJI entries downloaded as readable HTML
  and extracted text. Brief quotations and stage-specific consultation notes
  committed; full consultation pages remain ignored. No PDF OCR was necessary.

## Translated and built

- A00 `m81243/fs-id1830385`: complete first instructional subsection, 44 source
  IDs, 17 MathML expressions, one number line, one worked example, two practice
  exercises, and all three solutions.
- A10 `m82453/fs-id1170655150800`: contiguous opening through the constant
  definition, 13 source IDs, nine MathML expressions, and the Greg/Alex table.
  This is not a completed A10 subsection or module.
- Each has unchanged Indonesian pivot plus separate conversational-ngoko and
  provisional academic Javanese CNXML: six excerpt files total.
- One self-contained offline HTML reader with 78 rendered MathML instances,
  localized SVG labels, visible register/language labels, and source links.
- Six complete narration transcripts and six well-formed, locale-labeled SSML
  files. **Zero synthesized or recorded audio files.**
- 25 terminology decisions; persistent goal, direct instruction transcript,
  decision log, stage-by-stage canon consultations, and next-source marker.

## QA and outstanding work

`receipt.json` records 11 passing structural/build check groups, including exact
source/provenance hashes, hierarchy/ID/math preservation, answer recomputation,
SVG geometry, HTML links/languages/headers, narration fixtures, and two
byte-identical builds. Eleven adversarial regression tests also pass, covering
changed source IDs/numbers/operators, unknown translation/media, unsupported
narration syntax, solution cues, and preservation of an old generated file when
a replacement write fails. These are not human language or accessibility
certification.

An independent read-only agent review found a missing spoken answer cue for the
two untitled practice solutions. Both now start with Wangsulan/Jawaban in the
appropriate language. The existing worked-solution titles are not duplicated.
Unsupported MathML structures/operators now raise errors instead of being
silently flattened. The review found no further discrepancy in the inspected
pilot mathematics, source boundaries, answer sets, and age table; it was not
native-language certification.

Visual browser review could not initialize (`VISUAL_REVIEW.md`). Native Javanese
educator review, social-register review, and pronunciation/listening review are
pending. Academic compounds and extended numeral forms remain explicitly
provisional. Do not describe this as a production-complete textbook.

Current next work: A00 `m81243/fs-id1339359` (writing whole numbers), followed by
A10 exponent work from `fs-id1170654982105`. Read `../NEXT_UNIT.md` before
resuming. Reuse the verified archives rather than duplicating them. After the
coordinator's external space recovery, this task first restored
the disk-full-truncated STATUS.md and verified all 21 existing output hashes
before rebuilding. No storage cleanup or source deletion was performed here.

## Second source-bound checkpoint — continued work, not completion

Two additional contiguous excerpts have review builds. A00
`m81243/fs-id2340048` is the complete place-value modeling subsection: 43 source
IDs, 51 MathML expressions, nine media references, two place-value tables, the
374-dollar model, and practice answers 176 and 237. A10 continues the same
opening section through children `[7:13]`: 12 output IDs including parent
context, 11 MathML expressions, the operation table, five multiplication forms,
four division forms, examples, and the multiplication-cross warning. The exact
next excluded A10 source child is retained above.

Each excerpt has three CNXML tracks, a standalone offline reader, three complete
text transcripts, and three locale-labeled SSML files. A00 embeds 15 verified
asset derivatives/source images; linguistic SVG labels changed without altering
numeric labels or model geometry. A10 uses 11 exact source-tree narration
fixtures and fails closed on unknown notation. No synthesized/recorded audio
exists. No visual browser, screen-reader, native-language, educator, regional,
pronunciation, or listening pass is claimed.

The canon shelf now has 23 entries. Topic-driven C19–C23 support hundreds/place
sense and multiplication/division/sum vocabulary, while new mathematical
compounds and spoken formula composition remain provisional. Structural QA has
11 passing pilot groups and 12 pilot regression tests. The post-pilot workflow
adds 17 passing fixture/build regressions. Its receipts bind exact draft, asset,
rules, reader, transcript, and SSML hashes and verify deterministic regeneration.

Full-assignment coverage remains **0 completed modules, 2 partial modules, and
155 untranslated modules**. The four reviewable excerpts do not complete either
partial module, either textbook, or AX-2. Continue after this checkpoint.

## Third source-bound checkpoint — 2026-08-31

Two more excerpts are integrated: A00 `m81243/fs-id1883656` (31 IDs, 40 MathML,
two fifteen-column charts, fifteen digit-place answers), and A10 equality/
inequality children `[13:23]` (35 new IDs plus shared parent, 23 MathML, two
numeric point-order diagrams, worked example and both practices). Exact finite
fixtures preserve numbers through 519,711,641,328, relation operands, linguistic
MathML text, source punctuation, and diagram facts. Empty leading chart cells
are distinct from a written zero; source-only spacing is not invented speech.

All six excerpt builds together contain 18 CNXML tracks, 18 transcripts, 18
SSML files, and five offline HTML readers, with 151 source MathML expressions
(453 rendered track instances). The canon now contains 28 readable entries;
C24–C28 changed digit-place spelling to éwu/éwuan and support yuta, wolu, sanga,
and sewidak. Forty-four terminology rows record evidence and provisional forms.

Current automated checks pass: 11 pilot check groups and 12 pilot regressions,
17 earlier-unit regressions, 18 digit-place regressions, and 18 equality
regressions. `THIRD_CHECKPOINT_REVIEW.md` independently witnesses source replay,
all 63 new MathML fixtures, embedded assets, chart/diagram facts, and aligned
transcript/SSML text. Its recorded hashes identify that review snapshot.

No human native/register, visual, screen-reader, pronunciation, or listening
approval is claimed. Zero recorded/synthesized audio files exist. Counts remain
**0 complete modules, 2 partial, 155 untranslated**. Next drafts for whole-number
names and grouping symbols are not yet production builds. Continue the full
assignment using `../NEXT_UNIT.md`; neither this commit nor six excerpts finish it.

## Fourth source-bound checkpoint — 2026-08-31

A00 whole-number naming (`fs-id1321580`) and A10 grouping (`[23:28]`) now add
53 + 7 new source IDs and 9 + 2 MathML expressions. Three new charts retain
their source geometry and every printed group, including 098. The headerless
number-name table and quoted-word paragraph have full source-tree fixtures;
four untitled answers have spoken cues. Naming prompts now read printed digits
and comma separators, so they do not give away the word-form answers. Grouping
speaks every bracket type/nesting level and five implied multiplications.

All 25 naming tests and 19 grouping tests pass without skips. The complete eight
excerpt builds contain 24 CNXML tracks, 24 transcripts, 24 SSML files, seven
offline readers, and 162 source MathML expressions (486 rendered instances).
There are 30 readable canon entries and 51 terminology rows. Numeric/linguistic
source text remains explicitly separated from provisional Javanese registers.

The naming SVGs have renderer-specific static clipping/overlap inspection;
see `a00-name-whole.ASSETS.md` for the exact limits and inherited geometry
discrepancy. This does not establish browser layout or whole-reader visual
approval. Native language, educator/register, screen-reader, pronunciation and
listening review remain pending; zero audio is synthesized. Full assignment
counts remain 0 complete, 2 partial, 155 untranslated modules. Continue with
the writing-numbers and expression/equation units in `../NEXT_UNIT.md`.

## Fifth integration checkpoint — 2026-08-31

A10 expression/equation children `[28:40]` add 33 new IDs, 21 exact formulas,
three complete tables and eight classifications. All three tracks now have
CNXML, offline reader, transcript and SSML drafts. Nine focused regression
tests verify source bounds, independent finite formula readings, unchanged
operands and power/fraction scope, table labels and summary, classifications,
answer cues and deterministic replay. There is no expression evaluation.

The shared renderer's numbered-list defect is repaired: source enumerated
lists use `ol`, including Arabic/letter numbering, while labeled items retain
their explicit source labels without extra bullets. Source circled typography
is not a browser-verified visual match. Source table summaries now translate
and supply a nonempty accessible label where needed. Exact translated MathML
replay replaces permissive mtext masking in narration dispatch; currency-only
mtext cannot silently change symbols. Seven shared regression tests pass,
including actual digit-place lists with explicit circled labels; native list
markers are suppressed there to avoid duplicated labels.
All eight earlier readers were rebuilt (seven HTML files), and the new reader
adds an eighth HTML file. Earlier independent hash snapshots remain historical.

Current nine units contain 27 CNXML, 27 transcript and 27 SSML files, with
183 source MathML expressions and 549 rendered track instances. The canon has
34 acquired/readable entries and the terminology ledger 57 decisions. Full
rounding, writing, exponent and end-exercise phrase drafts are tracked separately
from integrated production. No complete module, audio synthesis, native/teacher,
integrated-browser, screen-reader or listening approval is claimed.

## Whole-number writing integration — 2026-08-31

The entire writing section fs-id1339359 adds 57 IDs, six MathML, three charts,
two worked examples and four practice solutions. Its three CNXML tracks, reader,
transcripts and SSML are generated and source-bound. Six exact prose fixtures
preserve all four literal-digit answers plus complete budget/weight prompts;
required formula contexts cannot fall back to detached coefficient speech.
Seven digit-form answers retain every grouping comma and zero. Inline part b
is spoken once, rather than duplicated by the generic list-part convention.

All 136 tests pass at the initial integration snapshot (125 earlier production,
three writing-asset and eight writing-workflow tests). Current production totals:
ten bounded units, nine HTML files, 30 CNXML, 30 transcripts and 30 SSML files;
189 source MathML / 567 rendered track instances, 60 embedded media instances.
36 canon entries are acquired and actually readable. Independent writing-unit
review is pending; static SVG evidence remains separate from integrated visual
approval. Full-module status remains 0 complete / 2 partial / 155 untranslated.

## Sixth checkpoint — independent writing review completed

The post-fix independent review passed 140 tests without skips and checked the
actual complete writing source, all three transcripts/SSML, reader MathML and
embedded assets. It reproduced a helper-level loss of mandatory quantity context
through a plain dictionary copy; the typed-map guard now rejects that case.
Saved writing speech was correct throughout. All nine prior unit packages and
eight prior readers remain byte-identical to the fifth reviewed snapshot.
See WRITING_CHECKPOINT_REVIEW.md for the final hashes and review limits.
The pending-review statements above describe earlier snapshots.

Three subsequent exponent-asset tests also pass separately. Those two source
JPEGs and four Javanese SVGs are preparation only, not an integrated exponent
reader. Complete source-phrase drafts now additionally cover A00 metadata,
summary/glossary and the whole addition module, plus A10 evaluation and like
terms. Complete end-exercise narration rules are also saved as draft inputs;
their nested-block assembly and self-check asset integration remain pending.
None advances a whole module to complete. Native, educator, integrated-browser,
screen-reader and listening review remain pending; synthesized audio is zero.

## Full exponent integration — initial producer verification

The entire A10 exponent remainder [40:53] now has three source-bound CNXML
tracks, an offline reader, and three transcript/SSML pairs. All 32 MathML,
two charts, two tables, six whole-prose fixtures and the real reference are
checked. Ten workflow tests pass, including 63 detached context calls, finite
power/answer checks, mutations, MIME-correct embedded JPEG/SVG and deterministic
prior-output replay. Independent integration review is pending.

Totals now: eleven bounded units, ten readers, 33 CNXML, 33 transcripts and
33 SSML; 221 source MathML / 663 displayed track instances, 66 embedded media
instances. The readable canon has 39 entries. Whole-module status remains
0 complete / 2 partial / 155 untranslated. The entire subtraction-module
phrase draft is also saved separately, not integrated production.

## Seventh checkpoint — independent exponent review completed

Root read the full final EXPONENT_CHECKPOINT_REVIEW.md. Its final independent
154-test suite passed without skips, alongside 204 direct/full-path rejection
probes and 15 valid controls. A copied-node helper gap was found and fixed;
saved exponent output was correct before and after that fix. All ten earlier
units' 90 content files and nine readers remain unchanged. Source-ID alt
inaccuracies are retained and explicitly disclosed, not approved as correct.

Whole rounding and order-of-operations AX-2 inputs are saved as drafts, not
production builds. The canon now has 43 actually readable locked entries.
Workers continue full multiplication translation, evaluation AX-2 and complete
addition-module AX-2. Full-module and human-review counts have not advanced.

## Rounding asset preparation after the seventh checkpoint

All 23 media are now represented by exact ID sources and Javanese derivatives:
12 unchanged ID SVGs, 24 translated/repaired SVGs, eleven retained numeric
rasters. Five new asset tests and all 159 regressions pass (32.612 seconds for
the combined run). Root inspected all distinct standalone rendered variants,
with seven register pairs verified pixel-identical. Source geometry defects are
explicitly repaired only in the Javanese derivatives; see the complete asset
record and 24-preview receipt. Full rounding reader/narration integration and
independent integration review remain pending, as does its orange-alt update.
Whole multiplication text is handed off as a draft, and division drafting is active.

## Complete rounding integration after cce2ca1

Full rounding now has three CNXML tracks, one offline reader, three transcripts
and three SSML files: 104 IDs, 69 source MathML, 23 media, five tables and all
nine exercise/solution pairs. All 169 tests passed in 135.351 seconds, including
ten new production tests. A subsequently added coverage test passed separately
after fixing the derived anonymous-title bookmark's list/section bookkeeping.
Coverage write and read-only verification pass: ten additional built units,
47 canon entries, still zero complete modules, two partial and 155 untranslated.

Three target-only point-color alts and the 033 quoted SVG label are aligned.
Both corrected 033 variants were rendered and inspected; eight register pairs
are now pixel-identical and four differ. ID audio/reader explicitly disclose
inherited redraw defects; the unchanged ID source is not endorsed as accurate.
All nine solution boundaries and eleven context-only formulas are enforced.
The two original optional external resource links are retained but not fetched.
Independent rounding review is next; no human/native, integrated-browser,
screen-reader, pronunciation, synthesis or listening approval is claimed.

Full multiplication/subtraction and evaluation AX-2 are saved input drafts.
Addition AX-2, division translation and like-term AX-2 continue. Coordinator's
review-branch upload is still partial; no independent lane push or full-public
snapshot claim. Current whole-assignment goal remains active.

## Independent rounding review and remaining-module component preparation

The full ROUNDING_CHECKPOINT_REVIEW.md is now saved and root has read it.
Its independent post-repair run passes 174 tests with no skips, plus 24 intact
controls and 234 rejected direct/full-context probes. The mutable helper cache
gap is corrected; saved rounding outputs were correct and remain unchanged.
All three actual transcripts, 90 SSML block/mark correspondences, 69 embedded
media and standalone visual evidence were reviewed. Integrated-browser, native,
screen-reader and listening approval remain pending.

Root then added seven tests for four distinct first-module components: outer
title, metadata/six objectives, recap, and outer seven-definition glossary.
Twelve three-track CNXML roots plus four English witnesses retain original paths
[0], [1], [2,6], [3]; no wrapper ID, moved glossary or complete module is invented.
The independent coverage ledger verifies these separately from reader builds.
The later full producer suite passes 181 tests in 65.379 seconds. Summary AX-2
and combined reader assembly are pending; twelve existing bounded units remain.

Complete addition/like-terms AX-2 and division translation inputs are saved.
Workers immediately continue whole subtraction AX-2, complete summary AX-2,
and the next algebra chapter introduction followed by entire m81268. New C48
basa and C49 tembung were acquired as small readable pages and actually read
for the chapter framing. The shelf now has 49 entries; no earlier rule snapshot
is retroactively claimed to have consulted them. Full-module counts remain
0 complete / 2 partial / 155 untranslated; no synthesized audio or publication
completion is claimed.

## Complete final exercise section — initial producer verification

The entire final `m81243` section now has three exact-source CNXML tracks, one
standalone reader, three transcripts and three SSML files. All four nested
subsections, 58 exercises, 29 supplied and 29 absent solutions, 273 IDs, 57
MathML roots, five media references and 80 narration blocks are retained. Four
model JPEGs are canonical/ID-byte-identical; the exact ID self-check SVG has two
text-only localized derivatives. Both localized checklists were rendered and
viewed separately, but integrated-browser, screen-reader and human visual
approval remain pending.

The first coverage write exposed a mismatch between the generic direct-child
mark assumption and this nested section's 80 source-bound marks. Coverage now
reads the exact digest-bound `generated_mark` sequence from all 80 block
fixtures, rejects incomplete/duplicate/cross-module contracts, and has a direct
regression test. Coverage write/check now agree: eleven additional built unit
drafts, 50 canon entries, and still 0 complete / 2 partial / 155 untranslated.
The current production inventory is thirteen bounded units, twelve HTML files,
39 CNXML, 39 transcripts and 39 SSML files; 347 source MathML / 1,041 displayed
track instances and 150 embedded media instances. The full producer suite passes
189 tests. No human-language, native, listening, synthesis or publication
completion is claimed.

## Source-positioned title/metadata/recap/glossary build

The four exact roots at original paths `[0]`, `[1]`, `[2,6]` and `[3]` now
feed one standalone reader, three transcripts and three SSML files without a
synthetic source wrapper. All 23 IDs, six objectives, seven definitions, the
2/3/4 procedure steps, 35 spoken text fixtures, three explicitly nonspoken
metadata slots, nine step cues and 14 exact marks are freshly rebound on every
build. The one recap SVG is embedded in each track through its exact asset
manifest; eight leading cells remain blank and the visible digits recompute to
5,278,194.

Coverage verifies this separately from the eleven ordinary excerpt builds and
does not change the baseline module ledger. Current inventory: fourteen bounded
units, thirteen HTML files, 51 target CNXML component files, 42 transcripts and
42 SSML files; 347 source MathML / 1,041 displayed instances and 153 embedded
media instances. The full producer suite passes 194 tests in 324.238 seconds.
Standalone asset inspection is retained, but native/educator, integrated
browser, screen-reader, pronunciation, listening, synthesis and publication
approval remain pending. `m81243` still requires complete assembly and a
cross-component audit before any module-completion decision.

## Complete-source `m81243` candidate — repaired rereview pending

The exact title, metadata, eight content sections and outer glossary now form a
complete-source assembly candidate with 628 unique IDs, 249 MathML roots, 47
media references, 88 exercises, 59 supplied and 29 source-absent solutions,
eight tables and seven definitions. Its three target CNXML roots retain exact
component order and tree boundaries. The complete reader contains 1,884 unique
track-prefixed IDs, 747 MathML instances, 141 embedded images and 33 track
panels. Each transcript/SSML pair retains the same 183 source-positioned marked
bodies as its reviewed component inputs.

The first independent cross-component audit did not close: it found that the
complete aggregate dropped the bounded rounding component's unmarked Indonesian
accessibility notice and reader-only offline-link sentence. The repaired output
now carries the accessibility notice exactly once in the complete reader, ID
transcript and ID SSML, and the offline-link sentence once in the reader, outside
all 183 marks. Both Javanese narration tracks contain neither notice.

An independent coherent-mutation probe then showed that hashes read from a
mutable component receipt were not a sufficient dependency boundary. The second
repair pins all eight reviewed component audio/build receipt hashes and all
seven asset-manifest hashes before use. A coordinated changed rounding reader
plus refreshed receipt hash and a changed manifest are installed rejection
tests. Nine focused complete-assembly/workflow tests pass in 275.246 seconds;
coverage write/check agrees at 0 complete / 2 partial / 155 untranslated.

Fresh independent rereview of the second repair was pending at this snapshot.
The candidate remained `whole_module_complete: false`, its effect on baseline
module counts remained none, and all native-language, educator/register,
integrated-browser, visual, screen-reader, pronunciation, listening, synthesis
and publication gates remained explicitly open.

## Complete-source `m81243` candidate — exact automated rereview passed

The separate rereview of the repaired snapshot passed its bounded automated
cross-component gate. It independently replayed exact source/target trees,
assets, reader structure, Indonesian-only unmarked notices, all 183 narration
marks and pinned dependencies; its 203-test regression passed, 52/52 broad and
23/23 pin-specific mutations rejected, and all controls passed. The preserved
first failed report and the second passing report are distinct evidence.

Coverage now requires the exact passing report SHA-256
`adfe7d63fe3325906f6dc7c7d259c9b5f92a297b702b12c72467cae5f5977218`
and reviewed build-receipt SHA-256
`94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099`.
Its state is automated-cross-component-review-passed but human-review-pending;
`whole_module_complete` remains false and counts remain 0 complete / 2 partial /
155 untranslated. No native-language, educator/register, integrated-browser,
visual, screen-reader, pronunciation, listening, synthesis, publication, module
completion or assignment completion follows. Parallel production continues on
A10 order/evaluation/like terms and A00 addition/subtraction/m81268.

## Complete-source `m81243` candidate — coverage pin repair

The first independent coverage adjudication remained open after reproducing a
coherent producer-plus-saved-receipt mutation that the initial ledger rule
accepted under the unchanged rereview report. That failed report is preserved at
SHA-256 `456de47a4bacdfe69110d33ff09f9ade8af13dbcc5afc04a58e0aec00b8c83f7`.
Coverage now directly requires its current generated receipt to equal the exact
reviewed SHA `94f1f1f1…`; a dedicated regression patches both producer output and
saved bytes and requires rejection.

Separate readjudication passes/closes only this exact automated coverage snapshot:
the former coherent mutation, a report-only mutation and a receipt-only mutation
all reject (3/3); both focused tests pass; and coverage stays 0 complete / 2
partial / 155 untranslated. The passing report SHA-256 is
`e4ed12f769096db63d5741d7d1ff31c11d27be91706304b13339fb9e80bf4ee9`.
Every human/native, educator/register, integrated browser/visual, screen-reader,
pronunciation, listening, synthesis, publication, module and assignment gate
remains open; `whole_module_complete` remains false.
