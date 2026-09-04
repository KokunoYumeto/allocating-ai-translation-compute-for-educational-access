# m81243 integrated learning review edition

2026-08-31. This is one complete source module with a connected, answer-complete local learning route, **not the complete A00–A20 assignment or a validated Grades2–8 course**. Native/Tamil-educator/learner/assistive-technology review and a new module PDF remain pending. Earlier U001/U002 PDF files are unchanged.

## Contents and preserved boundaries

`reader-m81243-learning/index.html` and `ta-Taml-IN-A00-m81243.epub` combine the full translated source with seven separately labelled original companions: route hub, U001, U002, U003–U005, U006rounding, missing-answer support and supplied-answer reasoning. The source-only52-file reviewer remains separate. This56-file reader includes local font/CSS/SVGs, verbatim source/font notices and a readable license XHTML. It has no account, script, form or required remote resource.

- Source:628original IDs,249MathML roots,88exercises,59original solutions and29original omissions, including all metadata/objectives/glossary. Original source XML SHA256 remains `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959`.
- New learning questions:75with75answers (15U001,16U002,16large-number,16rounding,12hub final/retry). The58source section-exercise supports cover96requested response parts; they are not58additional assessed questions.
- Integrated document:2,002unique IDs,334MathML roots,49SVG occurrences (47source +2new counting diagrams),133answer elements (75new-item answers +58source supports),92navigation entries.
- The four-stage route requires complete local M1–M4 attempts, then one complete F1–F6 or T1–T6 attempt with all requested answers/reasons. It never adds partial successes from different attempts. Wrong answers have numbered repair and retry routes. This local rule is not psychometric mastery evidence.
- The original confidence checklist remains6×3blank responses with its source advice. Renderer-added warnings now link to the independent learning route and still state that confidence does not prove mastery. Original teacher-dependent wording is not secretly rewritten. The hub explicitly supersedes older standalone release-status notes for navigation.

Source adaptation changes only identified renderer-added notices (confidence, missing answers and unbundled worksheet) and appends58labelled support links. Every source block is compared with its expected rendered baseline, and every original solution/MathML tree is preserved. The7companion source files are not flattened: root IDs remain intact. Long companion MathML receives32focusable inline scrolling wrappers; reversing those wrappers reproduces the complete original companion trees exactly. No number, operator or wording was shortened to fit.

## Content review

The main task read the complete rounding companion, route hub, U009source and their notes, and consulted actual canon as recorded in `canon/CONSULTATION_LOG.md`. The independent answer review checked all58mappings/96parts, all20digit places, compositional number names,30rounded responses and60endpoint distances. Focused complete-card reading is precisely bounded in `M81243-answer-independent-review.md`; do not claim a complete native review of every sentence.

One feedback ambiguity was corrected in M21/S21: replacing trillion with billion changes value **if the count is not also changed**. Final missing-answer companion SHA256 `bae2e03c4757dc2693e8727de667266eb2138ba3f31c2adbd1fe8662a8efc8aa`; supplied-reasoning companion `8decc79dab1d138b315dd8505b899e7c4893678de2dc23689b72c17066460fb5`. Reversal of exactly those sentences reproduces the earlier hashes. The actual final files are inputs to this reader.

## Build, package and negative checks

`scripts/build_m81243_learning.py` uses only Python's standard library and committed inputs. It validates both pinned witnesses via the full assembler, requires the actual assembled source to equal that candidate, checks source/companion/math/ID/reference/asset closure, builds twice in memory, and refuses unexpected output files or path escapes. `--check` compares every output filename and byte, without rewriting. Inputs are rehashed before returning the payload.

The source renderer's21negative cases run on every integrated build. Ten additional integration/package cases reject changed ordinary source prose, changed companion prose, broken local links, duplicate IDs, missing font, remote CSS, missing/remote license stylesheet, active license content and a dangling EPUB TOC fragment. Independent review found that the initial package check covered only book.xhtml; the root added a recursive check for **every** packaged XHTML/SVG, CSS dependency, IDREF and OPF manifest/spine reference. Actual published-to-disk content had no such corruption; this fixed a verifier gap. See the separate independent integration review for its rerun and limits.

Two real EPUBCheck failures were fixed before this final edition: RSC-010 for linking directly to plain-text LICENSE.txt, then RSC-011 because the readable LICENSE.xhtml needed a nonlinear spine entry. The final license page preserves the exact notice text, including CRcharacters as XML character references; the raw notice remains byte-for-byte bundled. Final EPUBCheck5.3.0reports0fatals/0errors/0warnings/0infos in `M81243-learning-epubcheck.json`.

Run from the repository root:

```powershell
python ta-Taml-IN/scripts/build_m81243_review.py --check
python ta-Taml-IN/scripts/build_m81243_learning.py --check
java -jar downloads/qa-tools/epubcheck-5.3.0/epubcheck.jar ta-Taml-IN/reader-m81243-learning/ta-Taml-IN-A00-m81243.epub
```

EPUBCheck/Java are separate QA dependencies; the HTML/EPUB rebuild itself does not need ignored corpora, the donor PC's absolute paths or third-party Python libraries. No new PDF was created.

## Actual browser checks and limits

The in-app browser loaded the local reader. At375content pixels it initially overflowed to576because long answer equations escaped their paragraphs. Added the32focusableMathML scrolling regions; reloading gives375/375client/scroll width with no overflowing non-scroll-region element. At320content pixels the complete document again measured320/320. The bundled font loaded, and browser DOM inventories show334MathML,49SVG,75new questions and133answers. At1285desktop content pixels it measured1285/1285; normal viewport was restored afterward.

Inspected the route start, confidence-table alternative, M19number-name/zero-padded answer, and the large-number guide. Clicked M19's actual source-exercise link to `fs-id2241247`, confirmed its preserved missing-source-answer notice and exact support target, then clicked the checkpoint table's U006start link to the rounding companion. Four checkpoint rows were inspected in the DOM. An initial guessed M19anchor did not move the page; the actual DOM ID was then used and verified. Do not count the failed navigation as a pass.

These are targeted phone/desktop screens and actual navigation checks, not a screenshot of every part of the long phone page. Full wide-SVG review, actual keyboard panning, screen-reader behavior, EPUB-app testing and human language/learner validation remain outstanding. CSS containment and `tabindex` alone are not keyboard/AT certification.

## Final identities

| Artifact | SHA256 |
|---|---|
| HTML | `cfe15686bb3e3cd2a2f428c7b1e2529553ad85326eeb9ee992db16a8184db7c2` |
| EPUB | `c9c944533946c3720b36d36435b41a21e8f90bc0c2ddc0efede2a7d2f0da4d16` |
| Build manifest | `13f229f198b8afada8c83c0f996faac3106c3894cb9006ca7ff5ddc044ee06e4` |
| Builder | `def5ce61b5ec76070d46dff2a6287cb72077b9933b0bfb6680fbd2d7e61b2078` |
| Learning CSS | `d74be543e8ed0257e5640a054402df4e42cf6b0cc1d33af83130c9ffeddc9f91` |
| EPUBCheck JSON | `670aad771d50f2d84473f807fe8072e765ce26b37ee571fb0cdda774c117a9be` |

The manifest inventories every actual input/output hash. PDF/native/AT/educational validation is not implied by these byte identities.

## 2026-08-31 — number-line fidelity correction, superseding product hashes above

IndependentPDFvisualreview found that the firstnumberline's upperrightdirection had noarrowhead. Root checked the pinnedEnglishJPEG and confirmed itshouldexist. In `assets/number-line.ta.svg`, split the compoundupperpath into independentright/leftpaths, eachwithmarker-end. This changes the graphic only, not sourceCNXML, mathematicalvalues or wording. The currentSVG SHA256 is`4f7ffd3e22918701100f2586d9bbf3b5c809790ee7db83bdcad2ba9c1a639d47`. `build_m81243_review.py` nowchecks the separate directionalpaths/baseline/marker/labels and rejects both a removedrightmarker and the oldcompoundpath, bringing itsnegativecases to23. Root visuallyconfirmedbothupperarrows in the actualbrowser atfs-id2316516; 0–6ticks/lowerarrows andTamil labels remainintact. This is targetedcorrectedfigurereview, not a newallfigure/ATcertification.

Bothfull-modulereaders rebuilt and passed read-onlybytechecks; the learningbuilder repeated its entirepayload identically and retained all10integration/package negatives. Current56-filelearningHTML`8f424a0b8d31f472d1b82a5a2e36053b6c00d558d1c40aa8e80e782510be45f6`; EPUB`ced73e55085c0b6e6bf089ea28ff497d3c4b7da84735fcb9a990254e0b4213ad`; manifest`63ebb9a39609645d4ae76f21b00b5cb184e4b5425427049bc4141cfa6b065c25`. EPUBCheck5.3.0againreports0fatals/errors/warnings/infos, receipt`ee4d97cf157a31790d1318d2c03e49c177547dd9d01ee14a96e6c0c9b87096ab`. Source-reviewHTMLis`0fd273a860e5be916a1fc00fe8437bfc2bff5dc24414bd5af30bcf68f0a277ba`; newsourceassetreceiptis`3e25a5bfb4080e3cc32dccba1aa26c10ffa261dd6afc8cf4cb113ab011f4b6be`. SourceCNXMLremains699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959.

HistoricalstandaloneU001renditions remainunchanged andinherit the missingarrowhead. Their priorvisualapproval is nowqualifiedbythiserratum, even though logicalTamil extraction stillpasses. The newmodulePDFs require re-export/reviewagainstthese correctedinputs; stalePDFreceipts cannotcertifythem.
