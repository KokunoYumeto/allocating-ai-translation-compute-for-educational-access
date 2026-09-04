# MR-BRIDGE-020 independent source and mathematics review

Date: 2026-08-31. Result: PASS for the bounded independent source/mathematics review and all 30 regression tests, with zero skips. No new translation correction is requested. The visible figure 234/237 notes correctly describe the independently observed source differences.

Role: independent reviewer and regression author, not the MR020 drafting author. I read the complete Marathi XML/config, both actual EN/ID source topic trees and the relevant source-backreference metadata, and personally inspected all eight original rasters. The 66 frozen fragments and 79 witnesses were separately parsed, compared and hashed. This is not HTML/PDF visual acceptance, native-speaker or teacher approval, accessibility certification, or whole-module/book completion. Only this report and tools/test_unit20_math.py were authored. No source/config/lock/shared-ledger edit, build, browser, PDF, download, bulk extraction, deletion, staging or publication was performed.

## Frozen scope and source identity

MR020 represents the complete fifth Chapter Review topic in A20:m81374, Relations and Functions, fs-id1167826172554, inside chapter wrapper fs-id1167836524742. Both actual source modules put it after fs-id1167836570304 and before fs-id1167836699953, the sixth and final Chapter Review topic. The later Practice Test fs-id1167836628671 is not selected.

The direct non-title source run has 33 blocks, beginning fs-id1167836486019 and ending exercise fs-id1167829786785. It contains 21 exercises and 12 paragraph blocks: three bold subheadings, eight instruction-prose paragraphs and one separate three-call input line. There are no source XML tables, formal-definition blocks, worked-example blocks or resource-note blocks. The three mapping diagrams contain visually tabular columns but remain source media, not additional XML table selections.

Ten source solutions occur on local questions 2, 4, 6, 8, 10, 12, 14, 16, 18 and 20. Eleven odd-numbered questions have no source solution, including question 21. Each omission is explicit and visibly original; no replacement answer has been invented or counted as translated. Questions 14/16 supply three evaluation subanswers each and 18/20 supply one each: eight supplied evaluation results in total, not eight additional exercises.

There are 96 original identities inside the selections, plus the topic and chapter wrappers: 98 original IDs. The target has 100 unique IDs, with only MR-BRIDGE-020 and credits added. Source IDs are checked in preorder with nearest-preserved-ID ancestry against both EN and ID sources. This retains all original exercise, problem, solution, paragraph and media identities, not merely their names in an unordered inventory.

| Frozen input | Bytes | SHA-256 |
| --- | ---: | --- |
| translations/MR-BRIDGE-020.xml | 31,109 | 29bd937f6d0e23cd68a6c4a1061d7115cc4a5838fa50373a405e951aaf6f57c7 |
| units/MR-BRIDGE-020.json | 4,285 | 22051ef0fa149c8a4e0f432a7172d2d23159d08224beb0014f5be1c352fbbe36 |
| provenance/MR-BRIDGE-020.lock.json | 89,571 | 6ce2fc3934f8c3b27c229dd0c5623b4bf37893c6ad54e9708f10c53e1c1b2382 |

All 66 frozen fragment files total 47,046 bytes. Their hashes and parsed elements agree with the actual named source members, including tags, attributes, text, child order and child tails; a fragment root's serialization tail is outside that comparison. Every one of the 79 distinct witness files is read and hashed. Four committed canonical assets total 255,055 bytes, and eight EN/ID original review files total 494,828 bytes. Missing inputs fail; none are skipped.

The config's source_count=33 and translated_practice_items=21 describe this topic only. Its zero worked-example/definition/resource-note/original-practice counts and empty original question_ids are accurate. Empty original question_ids does not mean the 21 source questions or their ten bidirectional answer pairs are absent.

## Actual readings and source authority

I read both complete topic trees directly from the pinned archive members, including all source headings, subpart instructions, ordered pairs, equations, function definitions, numeric/symbolic answers and media alternative descriptions. All Marathi lines, including the lead, original reminders, omissions, figure notes, question-direction note, rational-domain note, links and credits, were read. The initial large display's later XML portion was reread in a bounded chunk. An initial source-print attempt failed on the console's encoding of a subpart marker; it was rerun successfully with explicit UTF-8 before the complete EN/ID reading. Neither truncation nor the failed print is counted as a completed reading.

The EN archive is downloads/mr-Deva-IN/releases/A20-canonical.zip, with prefix osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9. Its recorded archive SHA-256 is effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917. The ID archive is downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip, with prefix source and recorded SHA-256 a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7. These existing A20 authority pins were not migrated.

| Actual member, relative to its prefix | Locale | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| modules/m81374/index.cnxml | EN | 247,327 | 021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a |
| modules/m81374/index.cnxml | ID | 247,303 | d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e |
| modules/m81373/index.cnxml | EN | 151,578 | 2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c |
| modules/m81373/index.cnxml | ID | 143,952 | e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee |

For the original title backreference, I read the actual m81373 title/metadata and its three objectives in each locale. Both have UUID 59fe6dc4-6e09-4a88-aa1c-b5f72bd79a20. This does not claim a new complete reading or translation of that teaching module. The target retains data-source-document=m81373 and its official section URL, explicitly requiring Internet and not claiming the link is local even though separate Marathi material exists.

The suite rereads only these four small module members and eight named image members in memory, plus existing frozen files. It verifies selected member SHA-256 values and benefits from ZIP member CRC checks. Archive SHA fields are compared with the recorded pins, not freshly computed over either whole archive on every test run. No whole-archive extraction, corpus copy or new source acquisition is needed.

## Finite relations: complete data, domains and ranges

Local numbers 1–21 are target labels, not asserted original textbook numbering. The following finite checks use all 51 ordered pairs across questions 1–8, not samples from an assumed continuous curve. Answers to questions without supplied source solutions are reviewer calculations only and have not been inserted into the target.

| Question | Relation data / representation | Exact domain | Exact range |
| ---: | --- | --- | --- |
| 1 | {(5,−2),(5,−4),(7,−6),(8,−8),(9,−10)} | {5,7,8,9} | {−10,−8,−6,−4,−2} |
| 2 | {(−3,7),(−2,3),(−1,9),(0,−3),(−1,8)} | {−3,−2,−1,0} | {−3,3,7,8,9} |
| 3 | Figure 234: (1,20),(2,25),(3,30),(4,35),(5,40),(6,45),(7,50) | {1,2,3,4,5,6,7} | {20,25,30,35,40,45,50} |
| 4 | Figure 235: (−3,1),(−2,−1),(−2,−3),(0,−1),(0,4),(4,3) | {−3,−2,0,4} | {−3,−1,1,3,4} |
| 5 | {(9,−5),(4,−3),(1,−1),(0,0),(1,1),(4,3),(9,5)} | {0,1,4,9} | {−5,−3,−1,0,1,3,5} |
| 6 | {(−3,27),(−2,8),(−1,1),(0,0),(1,1),(2,8),(3,27)} | {−3,−2,−1,0,1,2,3} | {0,1,8,27} |
| 7 | Figure 236: x⁴ at the seven listed inputs −3,…,3 | {−3,−2,−1,0,1,2,3} | {0,1,16,81} |
| 8 | Figure 237: x⁵ at the seven listed inputs −3,…,3 | {−3,−2,−1,0,1,2,3} | {−243,−32,−1,0,1,32,243} |

The four actual supplied finite-relation answers, on questions 2, 4, 6 and 8, agree with these sets in both sources and the target. Target source-answer order is retained: for example question 2's range is printed {7,3,9,−3,8}, not silently reordered. Question 4's supplied pair list retains (4,3),(−2,−3),(−2,−1),(−3,1),(0,−1),(0,4), including its harmless trailing comma. Set semantics are checked separately from literal ordering.

Questions 5–8 explicitly ask whether the relation is a function. The answers are no, yes, yes, yes. Question 5 has the same input 1 with outputs −1 and 1; the pairs with inputs 4 and 9 provide additional such witnesses. Questions 6 and 7 legitimately send different inputs to the same output. The target and tests do not confuse a function with a one-to-one function. Question 6's positive outputs for negative inputs are preserved; they are not silently changed into the values of unrestricted x³.

As an additional reviewer check, relations 1, 2 and 4 are also non-functions, whereas relation 3 is a function on the finite listed input set. That is not an extra translated subquestion or answer. Explicit witnesses are input 5 with −2/−4, input −1 with 9/8, and input −2 with −1/−3 respectively.

The graph's −6…6 window is not its domain or range. In particular neither an entire interval nor all points between plotted pairs are introduced. Figure 235 contains six isolated points, without joining lines. Figure 234's seven ages do not establish a continuous growth law; its arithmetic pattern is checked only for the seven observed arrows. The original age/weight units remain years and pounds, with no kilogram conversion. The target explicitly treats it as a source exercise picture rather than an up-to-date clinical child-weight table.

## Five equation/function judgments

The target's original note correctly states the direction: whether y is a function of x, not whether x is a function of y.

| Question | Preserved equation | Independent reasoning | Supplied source answer |
| ---: | --- | --- | --- |
| 9 | 2x+y=−3 | y=−2x−3 gives exactly one real output for each real input. | None |
| 10 | y=x² | A specified square is a single output for each real x; inverse ambiguity is irrelevant. | Yes / ya / होय |
| 11 | y=3x−5 | One affine expression defines one output for every real x. | None |
| 12 | y=x³ | A specified cube is a single output for every real x. | Yes / ya / होय |
| 13 | 2x+y²=4 | At x=0, both y=2 and y=−2 satisfy the equation. Thus y is not a function of x. | None |

The positive judgments are verified by exact polynomial form: after bringing both sides together, the coefficient of y is a nonzero constant, and the remaining terms depend only on x. Solving that coefficient relation gives the displayed polynomial output. This structural argument applies to all real inputs; a finite numerical grid is not used as a universal proof.

For question 13, the same-input/two-output counterexample is sufficient. The additional coefficient check y²=4−2x shows that its actual real relation has x≤2 as domain, with y=0 at x=2 and no real output for x>2. Neither that endpoint nor the reversed statement x=(4−y²)/2 changes the required non-function judgment. These are reviewer calculations, not new answers filling a source omission.

## All evaluation prompts and supplied results

The common instruction for questions 14–17 is exactly f(−2), f(3), f(a), in that order. Its separate pure-mathematics paragraph retains all three calls and subpart markers. A source line without prose is not a missing Marathi translation.

| Question | Preserved definition and input(s) | Independently computed result(s) | Source disposition |
| ---: | --- | --- | --- |
| 14 | f(x)=3x−4; −2,3,a | −10; 5; 3a−4 | All three supplied |
| 15 | f(x)=−2x+5; −2,3,a | 9; −1; −2a+5 | All absent; reviewer-only calculations |
| 16 | f(x)=x²−5x+6; −2,3,a | 20; 0; a²−5a+6 | All three supplied |
| 17 | f(x)=3x²−2x+1; −2,3,a | 17; 22; 3a²−2a+1 | All absent; reviewer-only calculations |
| 18 | g(x)=3x²−5x; g(2) | 2 | Supplied |
| 19 | F(x)=2x²−3x+1; F(−1) | 6 | Absent; reviewer-only calculation |
| 20 | h(t)=4|t−1|+2; h(−3) | 18 | Supplied |
| 21 | f(x)=(x+2)/(x−1); f(3) | 5/2, with x≠1 | Absent; reviewer-only calculation |

All eight supplied evaluation subanswers are retained exactly and independently recomputed. For the symbolic f(a) answers, substitution renames the input variable in a polynomial coefficient dictionary and compares every coefficient; equality is not inferred from a few values of a. Negative inputs retain their sign and grouping. In question 20, |−3−1|=4, then 4·4+2=18. The incorrect regrouping 4(|−3|−1)+2 is explicitly distinguished by a negative control.

The capital F in question 19 appears twice in each source's MathML and stays capital in both target definition and call. The exact-case parser rejects evaluating that definition through f(−1); it does not silently equate separate names f,F,g,h.

The rational function is parsed as a quotient whose entire numerator is x+2 and entire denominator is x−1. Its coefficient structure identifies the one excluded input x=1. The asked input 3 is valid and evaluates to the exact Fraction 5/2. The visually authored x≠1 note explains the domain without falsely providing a source solution. The misparenthesized expression x+2/x−1 is not accepted as equivalent. The unchanged source omission remains explicit.

## All eight original rasters and observed discrepancies

I personally viewed each EN and each ID original at original detail using existing filesystem image files. No target reader, browser or contact-sheet substitute was used. All eight review copies were byte-compared with the actual named ZIP members; the four committed assets equal their canonical EN originals. Figures 235–237 have identical EN/ID bytes. Figure 234 is a different Indonesian redraw, inspected separately.

Filenames are CNX_IntAlg_Figure_03_06_NUMBER_img_new.jpg. Review copies are downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-020/en-NAME and id-NAME. Canonical assets are assets/MR-BRIDGE-020/NAME relative to the locale root.

| Figure / locale | Bytes | SHA-256 |
| --- | ---: | --- |
| 234 EN | 64,160 | cd7fa2289ce16fa4d23665f4a818a268cbec29417e95f122f7975d24bc471c17 |
| 234 ID | 48,878 | d44704c739145fc582b783a84efe51803e1fa3946744660b203435cd812d208d |
| 235 EN | 64,448 | 6bb7f78ff8c0d1dc3024dfc28f6865d3913e02a4f0497d386ceac61d66857e31 |
| 235 ID | 64,448 | 6bb7f78ff8c0d1dc3024dfc28f6865d3913e02a4f0497d386ceac61d66857e31 |
| 236 EN | 59,305 | b22f9f064d0a5ae59fc27c4cfa6c1bbf07ce274d1751eec2891b0d9c903c0a47 |
| 236 ID | 59,305 | b22f9f064d0a5ae59fc27c4cfa6c1bbf07ce274d1751eec2891b0d9c903c0a47 |
| 237 EN | 67,142 | 67d75bb3b5ba3975b3ad5a6ccd19044025c0faf9f5ec3ad81332f59dd6a3f511 |
| 237 ID | 67,142 | 67d75bb3b5ba3975b3ad5a6ccd19044025c0faf9f5ec3ad81332f59dd6a3f511 |

Figure 234: the actual EN headers are Age (years) and Weight (pounds); the source alternative description abbreviates the first unit as yrs. The EN right-column rows are 20,35,30,45,40,25,50 from top to bottom. Tracing each arrow gives 1→20,2→25,3→30,4→35,5→40,6→45,7→50. The ID redraw has Usia (tahun)/Berat (pon) headers and ascending right rows 20,25,30,35,40,45,50, with horizontal arrows that give the same relation. The target correctly describes the unchanged EN row order and separately explains the ID rearrangement. Pairing rows by height would be wrong for the EN image.

Figure 235: both actual images show x/y axes marked −6 through 6 and the six isolated points recorded above. In particular the two x=−2 points and two x=0 points are distinct plotted outputs, not a continuous graph. Both source descriptions and the supplied ordered-pair/domain/range answer agree with the pixels.

Figure 236: both images have left header x and right header x⁴. The left rows are −3,−2,−1,0,1,2,3; the right rows are 0,1,16,81. All seven arrow endpoints agree with fourth powers of those finite inputs. Multiple inputs legitimately converge on the same output. Both source descriptions and the Marathi alternative description agree.

Figure 237: both images have right header x⁵ and right rows 0,1,32,243,−1,−32,−243. I traced all seven arrows, especially −1→−1. The EN alternative description incorrectly says the third arrow goes from −1 to +1. The ID description correctly says −1→−1. The actual pixels and both supplied range answers include −1 as required. The target's visibly original correction is accurate and preserves the unchanged EN image; it does not silently repair an archive or copy the erroneous alt as mathematical data.

Image appearance and arrow readings are manual observations bound to exact bytes. The suite rechecks those pins and their relation/alt consequences; it is not automated vision, proof of pixel recognition, or a fresh reader-layout inspection. No image was generated, edited, redrawn or newly copied by this reviewer.

## Actual Marathi-canon consultation and effects

At the beginning of this review I retrieved and read current official search-reader prose for C14–C16, the function-definition/domain-codomain paragraphs and final constant-function paragraph. The complete relevant prose was read despite equation-image placeholders, which were not treated as read formulas. These passages support one output per permitted input, the domain/codomain naming and the fact that shared outputs do not disqualify a function. They guided the repeated-output checks and the direction of the equation question. The formula-specific proofs above remain independent mathematics. [Marathi Vishwakosh: फलन (Function)](https://marathivishwakosh.org/21979/).

I separately read C19's actual opening definition through the image-set/subset sentence, and revisited it during assertion revision. It supports कक्षा as an attested range synonym and keeps the actual image set distinct from the codomain; it does not attest the exact working word मूल्यसंच. During rational-domain review I also read its paragraph excluding denominator-zero inputs. I did not use the adjacent inverse-function wording, unrelated advanced claims or imperfectly extracted formulas as authority. No new global term was promoted. [Marathi Vishwakosh: फलन](https://vishwakosh.marathi.gov.in/27548/).

The fresh C18 coordinate paragraph was read through ordered coordinate construction and sign/axis conventions. It supports reading the actual x/y positions in figure 235; its contextual line-joining example is not permission to interpolate this finite relation. C20's actual vertical-bar row, read at selection and again during final arithmetic revision, supports केवल मूल्य / चिन्ह निरपेक्ष मूल्य. It names the notation but does not substitute for calculating h(−3). [Marathi Vishwakosh: आलेख](https://vishwakosh.marathi.gov.in/24316/), [गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/).

I reread C12's existing OCR opening on physical PDF page 85 / printed page 75 through the solution definition and equal-operation rules, including nonzero division. This reinforced separating evaluation from equation solving and preserving a denominator restriction. I did not use its garbled formula OCR, render a new PDF page, or claim new visual inspection of the canon PDF. The witness is downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt, 2,474 bytes, SHA-256 f9bf9c42edb3e126573bc14f4671aa5c062920ee145c50590fdac6733af52a9b. [Balbharati Standard VIII mathematics PDF](https://books.ebalbharati.in/pdfs/801020004.pdf).

The successful web evidence was search-reader text, not a downloaded local HTML witness. An initial search used an incorrect remembered locator for C14; it did not establish a C14 reading. I checked the actual canon catalog, used its correct marathivishwakosh.org/21979 locator and then read the returned definition, naming and constant-function prose. Large combined output was retained and its relevant passages printed separately before being counted read. No failed fetch or another agent's reading is claimed as my consultation. The record here describes actual reads and effects; shared canon/terminology ledgers were not edited.

## Regression coverage and link integrity

The 49 unique target math keys equal the exact frozen config. Of these, 34 correspond to every original MathML occurrence in each source locale; 11 represent literal source-answer quantities/sets/pairs, and four are clearly original notation/correction/domain keys. Each source MathML occurrence is matched by its original containing ID and occurrence order. Whitelisted serialization preserves power and whole-fraction grouping, and exact polynomial/Fraction calculations separately verify mathematical content. A string or hash match alone is called regression evidence, not independent proof.

All ten supplied source answers have direct problem→solution and solution→problem anchors, 20 directions. All 24 local links resolve, including the four other navigation links. The three external anchors are HTTPS: the original m81373 section backreference, the chapter introduction and the preserved CC BY-NC-SA 4.0 link. The backreference title and UUID were checked against both pinned source modules. Live website availability was not tested, and no offline localization is falsely claimed. Credits retain the component-notice qualification; no new general license audit was conducted.

Run from the workspace root:

~~~powershell
python -B mr-Deva-IN/tools/test_unit20_math.py
~~~

| Tests | Bounded checks |
| --- | --- |
| 01–07 | Exact frozen pins/locale/NFC, source-module pins, all 33 selectors and boundaries, 66 fragments, 98 source IDs/ancestry, all 12 paragraph roles and subparts, all 49 strings and 34 source MathML occurrences. |
| 08–13 | Complete four textual relations, 21 mapping arrows, six plotted points, all eight finite domains/ranges, supplied finite answers, repeated-output and same-input/different-output checks. |
| 14–16 | All five equation constraints, four coefficient-based function arguments and an exact non-function counterexample. |
| 17–23 | Common inputs, all eight function definitions, eight supplied evaluation results, reviewer-only missing results, symbolic coefficient identities, absolute-value grouping, rational domain and case-sensitive F. |
| 24–30 | Ten original answer pairs/eleven omissions, authored-note separation, four assets/eight source-image pins, visible source corrections, all links/backreference, 79 witnesses/offline XML media and parser negative controls. |

The standard-library suite uses Fraction, explicit polynomial coefficient dictionaries and a whitelisted AST; it never calls eval. It rejects unknown functions/attributes/indexing, unbalanced or unsupported input, zero denominators, unsupported polynomial forms and powers, malformed pairs, duplicate set values and duplicate JSON keys. Negative controls distinguish lost minus signs, −x² from (−x)², incorrect absolute-value grouping, misparenthesized rational expressions, and lower-case f from upper-case F.

The first suite run had one test-author defect: a blanket Marathi-character requirement incorrectly rejected the source's pure f(−2),f(3),f(a) input line. The correction is limited to that exact original paragraph ID and explicitly requires its three source and target math occurrences. No translation byte changed. The next run passed all 30 tests, zero skips, in 0.450 seconds. That elapsed time is observational, not a deterministic requirement or a claim that the initial failed run passed.

Test file: tools/test_unit20_math.py, 50,564 bytes, SHA-256 6a780a006d76bf9639d3695015d4d0d981c96d20c74cb5da3e625654c31a3734.

The inventory digests use sorted UTF-8 rows separated by LF and a final LF:

- Fragments, target_id|locale|fragment_sha256: 4df9fd350ea71db18111de191212ed9d55ad930ed6fc9162c661b27539da2842.
- Math, key|text: 9afa5503d7e4d178b9529c684b3c2abf899129148c050b87193a8c714caeec6e.
- Images, locale|filename|sha256|bytes: 4c3a36a4f7dc0f20e64afae147054b9cb820f57f2d3715fd09818c38611867f8.
- Witnesses, path|sha256: e377cf07f4d0acf4562f930619f9fa4898f850ced4ccecaa9c6f1a4c539052f3.

## Handoff limits and continuation

No new source/math defect was found in these frozen bytes. Preserve the visible EN/ID figure 234 distinction, figure 237 alt correction, explicit rational denominator condition and all eleven genuine source-answer omissions. Reviewer-only calculations above must not be silently counted as newly translated or source-supplied answers.

This source regression requires the ignored pinned archives and existing eight original review copies as well as committed witnesses/assets. Missing dependencies cause failure, not skipped success. The report is not permission to treat rebuilt or edited XML/config/lock bytes as already reviewed; intentional changes need new verification and pins.

No target HTML/PDF was accessed, no reader was built or rendered, and no typography, responsive geometry, assistive-technology, native-speaker or teacher approval is claimed. Parent integration, permitted format-specific QA and coordinator-managed publication remain separate. This report does not change shared ready counts.

The exact next source topic is A20:m81374#fs-id1167836699953, Graphs of Functions, followed by Practice Test fs-id1167836628671. This identifies the boundary of MR020, not another worker's current completion. The complete five-book assignment and its supporting workflow remain active.

