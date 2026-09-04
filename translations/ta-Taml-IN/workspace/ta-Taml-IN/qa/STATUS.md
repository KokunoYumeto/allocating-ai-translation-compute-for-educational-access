# Current status - 2026-09-01

Whole assignment: active and incomplete. No claim that a pilot closes the Grades 2-8 gap.

## Current M81244/M81245 source admission and M81243 PDF repair

M81244 is now complete only as a checked source-review package. Root and an independent reviewer reran `scripts/assemble_m81244.py --check-only` and `--check` on the exact current bytes; both pass 33 negative fixtures. `reader-m81244-review/` has 54 regular files / 542,725 bytes, all 14 canonical fragments, 50 exact SVGs, 3,576 elements, 756 source IDs, 401 MathML trees, 129 exercises and 89 source solutions. Its source SHA-256 is `563dc10f207a09b919e28a0ea535848e244e7c5b4bbbcca5d2f588746ab38b50`; manifest SHA-256 is `cad9226386091f04f213a4413b701c961a1bf66b7d14280a5e314fbb75e52908`. The titleless section-exercise wrapper and final glossary node are preserved exactly. See `M81244-ASSEMBLY.md` and the superseding note in `M81244-SOURCE-PROGRESS.md`.

Exactly 40 source omissions remain unchanged: 38 U015 exercises / 120 response parts, Fred's absent total, and one open reflection. A separately marked companion for the 120 response parts plus Fred's independently computed 1,230 is active; the open reflection must remain learner-authored. The separate U012–U013 phrase/application companion has 12 answered D/P/M/T items, 42 IDs, 60 closed links and 60 MathML roots. Root QA and a full independent content/language audit both pass all 10 negative fixtures. This companion is still unrendered and unintegrated; its finishing condition is local to that narrow strand.

M81245 U019 `fs-id1799687` is independently admitted at bounded source-fragment level: 133 elements, 28 IDs, 14 MathML trees, three supplied exercises/solutions, one 2×5 table and no media. Tamil SHA-256 is `04f58da6e1560160273afcb18161dbfb8f5d955ef0e4f1eed577ef6393524883`; independent report SHA-256 is `d51581515b5762966b2cc489a474963b0bd41a2b7ffa8c70eab64cfa631223a2`. U020 `fs-id1824154`, Model Subtraction of Whole Numbers, is the active next contiguous source span.

The latest corrected M81243 PDFs remain an uncommitted review lane, not final outputs. Print is 224 pages / SHA-256 `941fdf36d583221a5caf22e1fb5a031421cdc787e5c188f0859c4c0147cad40c`; screen is 262 pages / SHA-256 `faee100963e823bdd28415b49a920a4e64e71cc4acbc6775a56377833c4587d0`. Both re-pass exact Tamil/ASCII/numeric/operator/link/destination/tag/ActualText/page-bound checks, and fresh rasters exist for every page. Root targeted views confirm that answer-opening groups, the five-choice source prompt, the prior feedback widow, M18 and the number-line arrows are intact. Two low-priority sentence-final periods remain on their own lines after block MathML in F5/T5, and independent all-page final review is still active. Exclude the PDF/CSS/export/receipt/review lane from the immediate coherent Git checkpoint and takeover bundle; no current PDF is released or cited as final.

The root has re-read actual canon OCR and complete images during this admission stage; the latest bounded consultation is recorded in `canon/CONSULTATION_LOG.md`. Passing source and model reviews do not imply native-speaker, educator, learner, assistive-technology, board-alignment, efficacy, PDF/UA, publication or full-assignment approval. Latest stable Git commit remains `0f96e7f`; the work above is uncommitted until a new exact checkpoint.

## Latest correction and addition checkpoint

2026-08-31: stableaddition-source commit`0f96e7f` adds readiness/U011–U014 and an unintegrated16-item recoverycore. The nine-fragmentboth-witness gate checks2,554nodes/388IDs/266MathML/47sourceexercises+solutions/28SVGs. See `M81244-SOURCE-PROGRESS.md`; sectionexercises/glossary/module2reader remainunfinished.

Newly found visualerratum: historicalU001figure1.1 lacks itsupperright directionarrowhead. Its priorvisualapproval is nowqualified; unchangedU001HTML/EPUB/PDFs are not production-ready. Rootchecked actualsourcepixels, fixed the asset's compoundpath, added twonegativeregressions and visuallyconfirmedthecorrectedfull-modulereader. The sourceCNXML isunchanged. A focusedscan foundnoother currentlypresentassetpath withmultiplemoveto commands andmarker-end; this isnotfullfigurefidelitycertification. Currentfull-modulereaders/EPUBrebuilds pass; modulePDFs need re-export afterarrow/layoutrepairs. Read `M81243-LEARNING-INTEGRATION.md` and `M81243-PDF-QA.md` for latestexactidentities andlimits; oldhashesbelowarehistorical.

## Latest integrated module checkpoint

This section supersedes older in-progress descriptions below. `reader-m81243-learning` now contains the complete translated m81243source plus all7separate learning companions: four recovery segments, missing/supplied source-answer supports and a final/retry route hub. All88source exercises have original or explicitly new companion answers; all75new questions have answers/reasons. The source's59solutions/29omissions are unchanged. The58final-source supports cover96responseparts; the confidence checklist is not an assessment gate.

The56-file HTML/EPUB build is repeatable from committed local inputs. Final EPUBCheck5.3.0passes0errors/warnings. Targeted375/320phone and1285desktop checks show contained document width and loaded Tamil font. Actual M19→source and checkpoint→rounding links work. Long math has32focusable scroll regions; keyboard panning and full wide-figure/native/learner/AT review remain unverified. No new module PDF is claimed. See `M81243-LEARNING-INTEGRATION.md` and independent review for exact final hashes and scope.

Actual source translation continues in m81244. U009addition notation and U010model addition are drafted:465elements,116IDs,49MathML,12exercises/solutions,19localSVGredraws across the two spans. `scripts/qa_m81244.py` checks both newly preserved pinned witnesses, hierarchy, digit/MathML sequences and exact media-alt closure, with3targeted negatives. U010source/figure author checks are documented separately; root has not claimed a full rendered review. U011`fs-id1385496` is active. m81244frontmatter/readiness, later sections and recovery workflow remain pending.

## U001 reading edition

- Complete source span: A00 `m81243#fs-id1830385`; 204 source elements, 44 IDs, 17 MathML expressions, three exercises/solutions.
- Separate recovery companion: 15 new answered items, including diagnostic routing, explanations, practice, mastery and retry. Independent model review findings were corrected and rechecked against companion SHA-256 `4116b42e061de2e8a5693e62fdb7ee36d8f8615ab922d485288df4b4e4e92f45`.
- Mastery/retry now test actual depicted counts, not totals supplied in questions. This is local learning feedback, not validated grade placement.
- HTML/EPUB deterministic builds and structural/numerical/link/local-asset checks pass. EPUBCheck 5.3.0 reports zero errors/warnings. Current HTML SHA-256: `26663c054138cbece00f7a17b24e07bb9369aab8ca3ee1c6a214cfe6f5981f01`; EPUB: `fd63837b2679d0a57fbfefdb33a810eeddbd6e4f644e21bf5da428444a3f687d`.
- Browser inspection confirms real SVG namespace, six mastery circles and three retry ellipses, loaded fonts and no document horizontal overflow at 1265 or 375 CSS pixels. The new counting diagram is visibly usable at phone width; temporary viewport overrides were reset.
- Print and screen PDFs each have 20 pages, all visually reviewed. Fresh Poppler UTF-8 checks recover every authored Tamil token with no NUL or replacement character. The earlier broad corruption diagnosis is retracted: pypdf 6.14.2 does not recover contextual `/ActualText` correctly here. Both unchanged U001 PDF hashes match the visual review. Production font files were not replaced. See `PDF-font-investigation.md` and `pdf-receipt.json`; this is not PDF/UA or arbitrary-extractor certification.

## U002 and remaining assignment

U002 `m81243#fs-id2340048` source translation and nine small Tamil SVG redraws are drafted. Its 310 elements, 43 IDs, 51 MathML expressions, currency tokens, three source exercises and two tables pass structural checks. English table-label errors are already corrected in the Indonesian witness; Tamil descriptions follow actual five-column data. Source text alternatives are being aligned with the declared schematic redraws.

U002 now includes16answered companion items, semantic tables and nine independently scrollable diagram panels. Browser inspection verifies the nine correct diagrams, readable phone labels and contained overflow; actual keyboard panning remains unverified. Final print/screen PDFs each have24pages, with every page visually reviewed and all2,303authored Tamil tokens recovered exactly by Poppler. The print example/table splits and screen spillover pages were corrected without changing content or13pt screen body size. Final nine-file repeat build and EPUBCheck5.3.0pass with zero errors/warnings. See current `U002-VISUAL_REVIEW.md` and receipts for exact hashes; no broader PDF/UA or AT certification is implied.

All8m81243content spans pass both-witness source structure/math checks and have their media present. The complete source is now assembled with title, six objectives and seven glossary definitions: 2,122elements,628IDs,249MathMLexpressions,88exercises,59source solutions and29source omissions. See `M81243-source-receipt.json`; root rerun matched actual source/receipt hashes. U003-U005 source-review HTML passes static checks and limited narrow-screen browser checks; complete wide-figure visual review and a recovery companion remain pending. U006 has23SVGs; U008has5newSVGs. Separate missing-answer, large-number and rounding recovery companions are being authored. No complete module recovery workflow is claimed; A10/A20translation and whole-course routing remain pending. See `NEXT_UNIT.md` and `source-coverage.json` for exact markers and remaining work.

## New U003-U005 recovery-review segment

`reader-large-recovery` now combines the three source sections with16new answered items, four explicit remedial explanations and executable local practice/mastery/retry routes. Its141source IDs,55source MathML expressions and15source exercises remain intact; the integrated document has535IDs,56MathML,8SVGs and6semantic tables. Repeatable16-file HTML/EPUB build, independent arithmetic/number-name checks and EPUBCheck5.3.0pass. Targeted phone/desktop screens and actual diagnostic/source links were inspected; a long numeral wrapping defect was corrected and rechecked at375and320content pixels. See `LARGE_NUMBER-INTEGRATION.md` for final hashes and explicit full-wide-figure/native/AT limits. This is not a complete module/course or a new PDF edition.

The separate29missing-answer/48response-part companion and16-item rounding companion are drafted and checked at source level; their complete integration/root wording review is pending. Further reasoning for the other29supplied section answers and the whole-module source-review reader are active independent work.

## Storage and review limits

The disk-full blocker cleared after user-authorized coordinator cleanup of unrelated archived logs. No source archive, translation or task log was deleted by this task. U001 hashes were verified before writes resumed. Large duplicate acquisitions stay paused; the necessary source/media corpus is already local. PDF export has a free-space guard and uses stable task-owned print caches.

Native-speaker/educator review, learner validation, assistive-technology testing and PDF/UA validation remain pending. PDF tagging, correct XML or EPUB conformance does not prove those broader requirements.
