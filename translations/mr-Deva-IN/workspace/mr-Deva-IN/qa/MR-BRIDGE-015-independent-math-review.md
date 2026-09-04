# MR-BRIDGE-015 — independent source, mathematics and original-image review

2026-08-31. **PASS: 23/23 independent tests, zero skips. No translation correction requested.** This review is independent of the drafting author. It establishes source/math readiness for this bounded selection, not acceptance of a rendered reader, a complete module/book, or the full five-book assignment.

Only `tools/test_unit15_math.py` and this report were authored by this reviewer. The translation, config, source locks, media, shared tools and generated readers were not edited. No download, extraction, browser, HTML geometry inspection, PDF operation, build, deletion or commit was performed. About 4.60 GB was free before the small test-file write.

## Exact reviewed inputs and reproduction

| Input | SHA-256 |
| --- | --- |
| `translations/MR-BRIDGE-015.xml` | `ec72c545cc5d3e34446d2875c48778c69cd51bf631598842f35f1f740bc8865e` |
| `units/MR-BRIDGE-015.json` | `dd6b3e480731effcf5c285adbc019bf26941e2ed7aa86a974244c2f289a9f9e0` |
| `provenance/MR-BRIDGE-015.lock.json` | `96b15c6573e559e6ed0735aa37ca40da93c565f8fa23d49ead836616a373fc06` |
| Existing HTML, opaque-byte currency check only | `42fff2491ad3081060b6b7d007881572952091bdcb766260d1aea69456ba1a4c` |
| `tools/test_unit15_math.py` | `c888279b757a2eac6e47bac570297a2b44f7a2107e3c6aa8e0bf315487a77f9d` |

Run from the workspace root with Python 3:

```text
python -B mr-Deva-IN/tools/test_unit15_math.py
```

The actual run used the bundled Python at `[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`. The suite is standard-library-only apart from importing the existing local markup validator. It reads the pinned ZIP members in memory and performs no writes or regeneration. All 23 tests passed against the real frozen files. There are no missing-freeze skips.

The first test run exposed two reviewer-harness mistakes, not translation defects: most domain/range answers are mixed CNXML prose rather than standalone MathML; q47(e)'s five pairs are split across two MathML nodes. The harness was revised to read the actual mixed content, preserve implicit `mfenced` delimiters, and concatenate both source components. It was not relaxed to ignore those answers.

## Source scope, order and completeness

Personally read the complete selected EN and Indonesian prose, all questions and subparts, every supplied answer, recap MathML/table text and all image descriptions directly from the existing archives. The compact reading preserved fractions, exponents, roots and implicit fences; selected raw MathML was reopened for the nontrivial mixed/fenced cases. The author's note was used as a list of things to verify, not as proof.

EN is `A20-canonical.zip`, member `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml`, module SHA `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a`. ID is `A20-v0.3.0-source.zip`, member `source/modules/m81374/index.cnxml`, module SHA `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e`. Both module hashes are checked against the actual bytes. Existing archive identities are retained, not moved.

The selection is the whole Key Concepts section `fs-id1167836597228` plus the whole Section Exercises section `fs-id1167836310305`. The latter contains Practice Makes Perfect `fs-id1167836300671`, Writing Exercises `fs-id1167836602786`, and Self Check `fs-id1167833057322`. It immediately follows the graph-information teaching section and ends before Chapter Review Exercises `fs-id1167836524742`; that next section's first child is `fs-id1167824674139`. Practice Test `fs-id1167836628671` is later and excluded. No detached root glossary is implied or counted.

| Verified property | Result |
| --- | ---: |
| Source selectors in exact source order | 63 |
| Original source IDs, preserved once with every ancestor relationship | 268 |
| Additional authored IDs / total IDs | 3 / 271 |
| Mathematical questions / writing questions | 50 / 4 |
| Mathematical subparts, including inherited group instructions | 122 |
| Supplied source solutions / explicitly absent source solutions | 25 / 29 |
| New questions / newly supplied solution containers | 0 / 0 |
| Displayed mathematical checks | 143 |
| EN/ID Section Exercises MathML trees, exactly equal | 71 per locale |
| Key Concepts MathML expressions/table per locale | 4 |
| Frozen source fragments / media witnesses / all file witnesses | 126 / 88 / 179 |
| Local links / optional HTTPS links | 55 / 7 |
| Empty learner-rating cells | 9 |

The three uncounted section wrappers retain their IDs. None is falsely added as a whole independent source selection over already selected children. The 54 exercise/problem identities, all 25 solution IDs, media/paragraph/list/table identities, original traversal order and full preserved-ID containment relationships agree with both source trees. All 25 source solutions have forward and return links. The 29 unanswered exercises remain explicitly unanswered; no supplied-answer total is inflated by the author's q47 explanatory note.

All source links in the selected CNXML were inventoried: there are none. The 55 local links resolve; all seven external links are the explicit optional license/canon references. Link syntax, identity and placement were checked; network availability is not promised, and the failed optional reference retrievals below remain disclosed. CC BY-NC-SA 4.0, original author credits, third-party notice qualifications and the no-training/fine-tuning-use statement are present. The settled upstream license audit was not repeated.

## Independent mathematical findings

No source-fidelity, arithmetic, interval, graph-reading or Marathi mathematical-meaning defect was found in this snapshot.

- The 143 checks are not accepted solely because XML equals config: 33 recap checks are tied to the source/pixel statements and explicit corrections; all 36 q5–40 formulas are independently represented by their actual affine/constant, square/cube, square-root or absolute-value family; all 42 supplied domain/range checks and all 32 graph-reading checks have source/semantic assertions.
- Every one of the 18 formula solutions has the correct graph and domain/range. Exact rational substitutions validate all caption coordinates, including fractional coefficients. The entire ranges follow from the function families: nonzero affine and cubic functions take every real value; constants give singleton sets; squares and absolute values have their stated extrema and direction; real square roots require the stated nonnegative radicand. Finite point sampling is not asserted to prove a whole range.
- The two supplied vertical-test answers, q1 and q3, are both (a) no, (b) yes. The actual circle/right-opening parabola give repeated inputs with distinct outputs; the upward parabola/cubic do not. q2 and q4 are retained without invented source answers. A sideways V is not mislabeled as a function in the Marathi question.
- The three supplied graph-only interval pairs, q41/q43/q45, agree with the actual ray, V and upper semicircle. Their domains/ranges are not the bounds of the displayed grids.
- q47's eight answers agree with the downward-at-origin wave. The exact evaluations are 0, −1, −1; the source lists five visible zeros/intercepts. The source question does not restrict the input interval, and the explicit original note accurately separates the visible `[−2π,2π]` list from the `nπ` family under the source-described repeating continuation. Unlike the prior MR014/025 issue, both actual 215 and 216 source descriptions explicitly say the pattern continues without bound. No unstated trigonometric formula is introduced.
- q49's upper semicircle has centre `(0,2)`, radius 3, endpoint heights 2 and maximum 5. Its eight supplied answers, including no zero or x-intercept, domain `[−3,3]`, and range `[2,5]`, are correct. q50 has six parts, not eight, and remains without a supplied answer.
- The four writing prompts and two self-check instructions preserve the source requests. Every one of the nine rating cells is genuinely empty; no checkbox/mark/hidden selected value was inserted.

## Actual 88-file pixel inspection

Personally opened all 44 EN and all 44 ID original JPG files with the permitted filesystem image viewer, in these groups: 027–030; 031–033 and219; 201–204; 205–208; 313/315/317/319; 321/323/325/327; 329/331/333/335/337; 339/341/343/345/347; 209–213; 214–218. These were original files, not source alt text or an uninspected contact sheet. No extraction or image alteration was needed.

Each basename is `CNX_IntAlg_Figure_03_06_NNN_img_new.jpg`. Every inspected review copy under `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-015/` was then compared byte-for-byte with its precise EN/ID ZIP media member. Every committed asset is the unchanged EN member and matches its configured SHA/MIME. Total bytes are 2,694,271 EN and 2,606,257 ID. Thirty-six pairs are byte-identical; 027–033 and219 differ. The ordered 88-entry manifest digest is `73f67ec9eec6d0e0b2fd99a911e3c21a4f1026b4248bc6e41191c1b8e26f4da8`; the test documents the manifest encoding. Individual full hashes remain in the frozen source-image records and the author's exact inventory, now independently checked against actual bytes.

Confirmed pixel/source distinctions:

- EN027 omits `m≠0`; ID027 includes it. The English all-real range needs the explicitly supplied zero-slope exception. EN028 shows bare `b`; ID028 shows `{b}`. The Marathi correction treats range as a set, and distinguishes intercept value `b` from point `(0,b)`.
- EN/ID031 display only y=−4…4. The cubic points `(±2,±8)` are correctly described as outside that visible window, not as visible dots.
- 201–208 use both axes −8…8. The 202 negative-x point, 203 negative y value and 205 right-branch coordinates agree with the Marathi corrections; the erroneous EN alt entries are not copied silently. 207's noninteger approximate branch readings remain explicitly approximate.
- 317 actually represents `−2x+2`, matching the question, not the `−2x−2` coordinates in both source descriptions. The Marathi notes make that difference explicit without modifying the canonical image.
- 313/315/317/319/323/337/339 have both axes ±8; 329/331/333/335/345/347 have x±8. 341/343 show x=−2…10 and y=−2…8. The graph-only 209–214 and217/218 windows likewise match their Marathi captions, including209's x maximum12,210's x minimum−4, and217/218's y window−2…10.
- 215/216 show x labels from −2π to2π, y labels±6, and wave extrema±1; finite visible coordinates and the stated continuation remain separate. The upper semicircle endpoints/maxima in213/214/217/218 agree. Both original219 rating tables have nine empty cells, as does the Marathi adaptation.

## Actual Marathi canon and workflow consultations

Read `USER_INSTRUCTIONS_VERBATIM.md`, the active workflow and relevant consultation ledger; refreshed the durable goal and current decision/update context. At handoff directly paged the coordinating task's actual turns, including user turn `[local-task-id]` renewing the instruction to check canon. Newer turns concerned ongoing checkpoint reports and the shared-storage notice; they did not authorize deletion or pause the five-book task.

These were this reviewer's actual readable passages, not merely remembered references or another agent's reports:

- During source reading, [C14-family फलन](https://marathivishwakosh.org/21979/) returned readable prose about dependency, the real-number square example and the final constant-function paragraph. Effect: check that one fixed output means a singleton range, not a bare scalar or arbitrary codomain. QuickLaTeX image placeholders were not claimed as read formulas.
- During source reading, [C18 आलेख](https://vishwakosh.marathi.gov.in/24316/) returned the actual जात्याक्ष construction: perpendicular axes, signed directions, possibly different scales, ordered coordinates, and the distinction between plotted samples and the equation's intervening points. Effect: read the correct coordinate order and grid scales, without treating finite points as a proof of a whole curve or its continuation.
- During interval checking and again at final revision, [C20 notation](https://vishwakosh.marathi.gov.in/21279/) returned its actual open/closed/half-open interval and bracket rows. Effect: independently check endpoint inclusion, singleton brace notation, and the stated working compound अंतराल-संकेतलेखन. The successful retrieval was the official search-reader text; a direct open returned502. The fresh targeted absolute-value search did not expose the absolute-value row, so that row is not newly claimed as read in this review. The existing term केवल मूल्य was retained consistently, with the actual absolute-value meaning independently checked mathematically.
- During semantic revision, [C19 फलन](https://vishwakosh.marathi.gov.in/27548/) returned the opening exactly-one correspondence, प्रांत/सहप्रांत distinction and actual-image-set passage using कक्षा. Effect: accept the explicitly acknowledged working term मूल्यसंच while checking that output set, codomain and viewport are not conflated. An earlier targeted query returned no result; the later exact-locator query succeeded.
- At final revision, [C21 गणितीय प्रतिरूपे](https://vishwakosh.marathi.gov.in/21277/) returned the शंकुच्छेद paragraph naming अन्वस्त/पॅराबोला and the opening distinction between illustrating a theorem and establishing one. Effect: confirm the parabola label and keep family arguments distinct from pixel samples.

The optional additional locator `https://vishwakosh.marathi.gov.in/32824/` returned502 in this review. No fresh successful reading, title verification or canon promotion is claimed for it. C20 supplies directly readable interval evidence. No new canonical item, glossary promotion, OCR or native-speaker approval was made. The complete vertical-line-test and descriptive identity phrases remain honestly identified as authored working forms.

## Handoff limits

Primary rendered-reader inspection remains pending. This reviewer did not open the denied HTML, use an alternate browser/local-server surface, inspect layout geometry, or generate/read a new PDF. The existing structural receipt and HTML hash were checked only for currency. Long captions and the self-rating table still require the parent's permitted format-specific visual workflow; source-image review cannot certify their layout. Optional reference availability and human/native-Marathi review are not guaranteed.

The parent retains integration ownership. The next source production continues beyond this checkpoint; no full-module, book or five-book completion state is changed by these 23 passing tests.
