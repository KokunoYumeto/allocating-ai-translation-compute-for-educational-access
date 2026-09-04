# Independent integration review — m81243 learning edition

Date: 2026-08-31. Reviewer: `u002_figures`. This bounded task owns only this note. The reviewer did not edit the builder, inputs, assets, HTML, EPUB or earlier readers. The parent made the package-gate correction described below. No browser, PDF, EPUBCheck or native-language approval is claimed by this review.

## Final outcome

No actionable integration finding remains within the tested scope. The actual final HTML and EPUB preserve the source and all seven companion inputs, except for the declared renderer-only editorial adaptations and reversible long-MathML wrappers. Original source solutions and omissions remain distinct from newly authored answers. The integrated route, confidence warning and local resources pass the independent checks below.

One actionable package-validation gap was found with in-memory negative probes. The parent corrected it, and the same probes now fail for the intended reasons. This was a validation robustness defect; the actual inspected output never contained the injected faults.

## Exact final snapshot

All SHA256 values below refer to the final retested files, not the initial intermediate EPUB before the parent's readable-license spine correction.

| File | Bytes | SHA256 |
|---|---:|---|
| `scripts/build_m81243_learning.py` | 34,171 | `def5ce61b5ec76070d46dff2a6287cb72077b9933b0bfb6680fbd2d7e61b2078` |
| `assets/m81243-learning.css` | 1,242 | `d74be543e8ed0257e5640a054402df4e42cf6b0cc1d33af83130c9ffeddc9f91` |
| `reader-m81243-learning/index.html` | 923,178 | `cfe15686bb3e3cd2a2f428c7b1e2529553ad85326eeb9ee992db16a8184db7c2` |
| `reader-m81243-learning/ta-Taml-IN-A00-m81243.epub` | 384,355 | `c9c944533946c3720b36d36435b41a21e8f90bc0c2ddc0efede2a7d2f0da4d16` |
| `reader-m81243-learning/LICENSE.xhtml` | 23,526 | `a5d668bb3232b7ac48d31973c836a6febd0563e596c80750e1bcfabb00a2c2cd` |
| `reader-m81243-learning/build-manifest.json` | 37,300 | `13f229f198b8afada8c83c0f996faac3106c3894cb9006ca7ff5ddc044ee06e4` |

The final manifest records all 79 input hashes and all 55 non-manifest output hashes. The independent audit recomputed every one of them; the output directory has exactly 56 files including the manifest. Important content inputs:

| Input | SHA256 |
|---|---|
| `translation/m81243.cnxml` | `699a12c0c3db042fe83262b7f38b6bc1504bad7a660478f090106593f7ced959` |
| `translation/recovery-m81243-route.xhtml` | `a2fc64c525af6c3f21630075aa0c4fcac4a08dda209a54cdf7dad2746f1f7618` |
| `translation/recovery.xhtml` | `4116b42e061de2e8a5693e62fdb7ee36d8f8615ab922d485288df4b4e4e92f45` |
| `translation/recovery-u002.xhtml` | `b61edfe7fe1084267b322ae7d9c5bc10694f069e0557cf2f9906fe7b552da463` |
| `translation/recovery-large-numbers.xhtml` | `37f05038e4c238ca0e7a0951f2b136e84aa7c6391a6acac7da7678498361baf8` |
| `translation/recovery-rounding.xhtml` | `84fe718d7fd236bbe943753b4bedad5ad1041856b15343498e653c1de8132ab3` |
| `translation/recovery-m81243-missing-answers.xhtml` | `bae2e03c4757dc2693e8727de667266eb2138ba3f31c2adbd1fe8662a8efc8aa` |
| `translation/recovery-m81243-supplied-reasoning.xhtml` | `8decc79dab1d138b315dd8505b899e7c4893678de2dc23689b72c17066460fb5` |

Thus both answer companions include the final, narrowly qualified M21/S21 feedback fixes. The separate source-review HTML was read as a rendering baseline, alongside the actual CNXML; it was not rewritten by this task.

## R1 — medium robustness finding, resolved

Initial location: `validate()` and `make_epub()`. The first function inspected the main book and CSS, while the second parsed other documents and checked ZIP bytes without recursively validating their resource references or active content. Four deliberately invalid in-memory inputs were accepted:

1. Change `LICENSE.xhtml`'s stylesheet to `assets/no-such-style.css`.
2. Change that stylesheet to `https://invalid.example/license.css`.
3. Add a script element to `LICENSE.xhtml`.
4. Add an EPUB TOC item pointing at `book.xhtml#not-a-real-anchor`.

These are meaningful failures of the package guard even though current generation produced none of them: a later license/navigation adaptation could create an offline, active-content or navigation defect without this validation catching it.

The parent added `package_gate(files)` before ZIP creation. The reviewer read the actual new function and retested through the actual `validate()` + `make_epub()` path. All four now reject, respectively, with `Unpackaged resource in package`, `Remote package dependency`, `Active content in packaged document` and `Unresolved package fragment`. The final HTML and EPUB hashes remain unchanged by this guard-only correction.

A fifth exploratory mutation changed only the license's text. The low-level packager still structurally accepts that well-formed document; the package-reference gate is not a semantic text-comparison function. This is not counted among the four closure/active-content faults. The production builder separately asserts exact license text at construction, and the independent actual-output check verifies both the final XHTML text and raw TXT against the source bytes. No altered license text is present in the delivered artifacts. This distinction prevents claiming the package gate validates every possible content change.

## Independent preservation checks

The reviewer read the complete learning-builder implementation and relevant rendering/validation helpers, inspected the actual route hub, and used separate XML traversal and comparison code. Positive checks did not merely repeat the manifest's numerical claims.

- All **628 source IDs** occur once and in their original source order. All **249 source MathML trees** compare exactly with the actual CNXML, including attributes, text, descendants and tails. All **573 nonempty CNXML text/tail fragments** remain within their closest original source-ID boundary.
- The source still contains **88 exercises**, **59 original solutions** and **29 original omissions**. Each of the 59 rendered original solution trees equals its source-review baseline tree. The newly authored missing answers are not inserted as original source solutions.
- An independently restored copy of the generated source region equals the original rendering baseline after removing precisely the declared adaptations: the 58 appended support-link paragraphs, the changed text of 29 omission notes, and the three renderer-only notes `mr-confidence-warning`, `mr-confidence-help`, `mr-unbundled-activity`. All other source blocks remain unchanged. Added cover/attribution wording is outside the translated source boundary and visibly identifies original companions.
- Every one of the **seven companion trees** compares exactly with its raw XHTML input after reversing only the renderer's **32 long-MathML wrappers**. Each wrapper contains one MathML tree, has the declared `math-scroll` / focusable-region attributes, and wraps a MathML text length greater than 18. Reversal restores the original child tail and full tree; the check covers prose, numbers, IDs, attributes, links and answer metadata, not just mathematical tokens.
- The final document has **2,002 unique IDs**, **334 MathML expressions** and **49 SVG occurrences**. The latter are the source's 47 occurrences plus two original companion counting models. Assessment counting explicitly selects XHTML `data-kind` elements; source SVG model-piece metadata does not inflate the 75-question total.

Question and answer accounting:

| Companion | New question cards | Answer cards |
|---|---:|---:|
| Module route hub | 12 | 12 |
| U001 | 15 | 15 |
| U002 | 16 | 16 |
| U003–U005 | 16 | 16 |
| U006 rounding | 16 | 16 |
| Missing source answers | 0 | 29 |
| Supplied source-answer reasoning | 0 | 29 |
| Total | 75 | 133 |

Each new question has exactly one separately located answer; none has an answer card nested inside it. These are question-card counts, not a claim that multipart cards contain only one scalar response. The other 58 answer cards map exactly to the 58 U008 exercises, with the correct problem IDs and, for the supplied cohort, solution IDs. Every source exercise in that cohort has exactly one added link to its corresponding support card, and every card links back to the actual source exercise. The 29 missing and 29 supplied-support cohorts are not conflated.

## Route and confidence behavior

Read the actual route hub, its checkpoint/final/retry gates, the four underlying companion gates, and the renderer's changed confidence/worksheet notes.

- `ta-route-checkpoint-table` has four rows pointing to the actual U001, U002, large-number and rounding starts, mastery sets, answers and retry sets. Every referenced mastery section contains the intended four M cards. The hub requires a complete four-of-four M attempt with all requested parts and reasons; it does not add isolated successes from different attempts.
- The hub explicitly requires returning to the full M1–M4 set after remediation before progression. This matters where an older standalone retry section uses different item/response accounting. The introductory and hub text clearly supersede stale standalone publication-status comments while preserving those original companion inputs.
- The six F and six T cards map in order to objectives 1–6 and the six actual remedy IDs. Final progression requires a complete same-attempt six-of-six F or T set, with reasoning, plus all four earlier checkpoint records. Failed attempts lead to executable paper activities and another complete check, not an instructor-approval dependency.
- The focused hub examples read correctly: 241 and 305 as models; 7 in 40,706,052 contributes 700,000 and 3 in 8,304,071 contributes 300,000; grouped names/digits preserve 008/045/070/009 and 030/006/005/020; 49,650 rounds to 50,000 at thousands and the tie 999,500 to 1,000,000 with explicit carry. This is a bounded hub spot-check, not a fresh mathematical or native-language audit of every sentence in all 75 questions.
- The source confidence alternative remains six skill rows by three **blank** response cells: 18 cells with screen-reader-only labels saying they are blank, not selected answers. There is no form. Both renderer notes retain the statement that confidence is not proof of mastery and now link to `ta-route-checkpoints`.
- All three dense place-chart alternatives retain 15 semantic rows. The source worksheet remains expressly optional and unbundled; the new explanatory route links to local U002 content instead. The cover labels the edition as a review edition, not a full curriculum, grade placement or validated learning outcome.

## Independent offline EPUB and license checks

The reviewer opened the actual ZIP bytes without writing or extracting a new artifact. Checks covered every packaged XHTML and SVG, all CSS, navigation, container and OPF—not only the main book.

- **58 unique ZIP entries**, including a first, uncompressed `mimetype` with exactly `application/epub+zip`; ZIP CRC checks pass.
- **55 unique OPF manifest items** exactly cover the packaged OEBPS resources other than the package document. Manifest resources exist and both spine IDs resolve. The main book is the primary spine entry; readable `LICENSE.xhtml` is a non-linear spine entry.
- All **92 navigation links** have the same ordered targets/titles as the HTML navigation and resolve to actual book IDs.
- Independently resolved **818 XML resource/fragment links**, **682 IDREF tokens**, **96 SVG paint references** and the CSS font dependency. Relative paths, cross-document fragments and SVG `xlink:href` were considered. All resolve within the actual archive. Five external anchor occurrences are optional links, not remote runtime dependencies.
- `OEBPS/book.xhtml` equals the HTML output byte-for-byte. Every packaged local asset equals its generated-reader counterpart. The EPUB contains the local Tamil font and stylesheet dependencies; no external stylesheet/font is needed.
- The actual readable license's parsed `pre` text equals `LICENSE.txt` and the original `provenance/A00-LICENSE.txt` decoded text exactly, including CRLF characters preserved through `&#13;`. Raw TXT remains bundled. The book points to readable XHTML rather than the raw text document.

The parent's earlier EPUBCheck license/spine repair is present in the actual final archive. This review does not claim to have run EPUBCheck; its own evidence is the independent package and text checks above.

## Reproducibility and negative probes

Ran the actual builder with `python -B scripts/build_m81243_learning.py --check`. This invokes two in-memory builds, compares them, and checks the entire existing output set without writing. The final command passed. An independent before/after snapshot of all **135 input/output files** showed unchanged byte lengths, SHA256 hashes and modification times. No source, output, cache or builder write was required by the reviewer.

The final builder's built-in record contains 21 source-renderer negatives and 10 integration negatives. Separately, the reviewer ran these **20 in-memory fault cases**, all rejected on final retest:

| Fault class | Cases | Observed rejection |
|---|---:|---|
| Change/remove an original solution; remove an omission label; redirect a support link; prefill confidence; reverse confidence warning | 6 | Rendered source block changed |
| Redirect a hub checkpoint; remove a new answer; change a wrapped MathML digit | 3 | Companion content changed |
| Duplicate a source SVG/document ID | 1 | Duplicate document ID |
| Remote main stylesheet; missing font; remote CSS import | 3 | Remote/unpackaged dependency checks |
| Duplicate new-answer mapping; wrong supplied-solution mapping; corrupt ordered missing-source coverage | 3 | Companion mapping/coverage checks |
| Missing license stylesheet; remote license stylesheet; license script; dangling EPUB TOC target | 4 | New recursive package-gate checks |

The text-only license probe described under R1 is separately classified, not falsely counted as a rejected fault. These tests are focused regressions, not exhaustive fuzzing, a security certification, or a replacement for EPUBCheck.

## Scope limits and handoff

This review establishes integration fidelity, source/support distinction, route-link closure and repeatable local packaging for the stated hashes. It does not provide native-speaker approval, a fresh all-sentence translation review, a full re-audit of every educational answer, browser/assistive-technology results, print/PDF approval or evidence of learner efficacy. Actual canon p12/p31 consultation and number/rounding reasoning remain documented in the preceding answer review; no new Tamil terminology or source prose was authored here, and that earlier consultation is not relabeled as a new complete linguistic review.

Only this note was written by the reviewer, using apply_patch. The parent owns the package-gate change and final browser/EPUBCheck records. The wider A00/A10/A20 and whole-assignment workflow remain active; successful integration of m81243 is not completion of that assignment.
