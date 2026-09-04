# Indian Bengali mathematics translation

Locale: `bn-Beng-IN`. Rank 4 assignment: full assigned A00–A20 collections, selected A30 and a distinct AX-3 recovery workflow, focused on Indian/West Bengal Bengali. The recovery pathway centres on Grades 3–8; advanced assigned content is not dropped. This is not a certified curriculum or validated diagnostic test.

The entire assignment is ongoing. Eight of242 collection-module references have full learner-text coverage: m81285–m81292, including the short decimal chapter introduction. U01 commit `713370c` was only the first checkpoint. Consult [full module/block progress](progress.json) and [current work cursor](NEXT.md); partial later sections do not imply a complete module or book.

## Read the actual output

- [Offline reading index](reader/index.html).
- [চিত্রের সাহায্যে ভগ্নাংশ বোঝা](reader/modules/m81285.html): complete m81285, including objectives, readiness, seven instructional sections, summary,76 section exercises and glossary;510 preserved MathML expressions and100 image occurrences.
- [ভগ্নাংশের গুণ ও ভাগ](reader/modules/m81286.html): complete m81286, including objectives, readiness, four instructional sections, summary,99 section exercises and glossary;495 preserved MathML expressions and38 image occurrences.
- [মিশ্র ভগ্নাংশ ও জটিল ভগ্নাংশের গুণ ও ভাগ](reader/modules/m81287.html): complete m81287, including objectives, readiness, four lessons, summary,78 section exercises and glossary;318 MathML expressions and3 image occurrences.
- [একই হরযুক্ত ভগ্নাংশের যোগ ও বিয়োগ](reader/modules/m81288.html): complete m81288, including objectives, readiness, four lessons, summary and62 section exercises;245 MathML expressions and22 image occurrences.
- [আলাদা হরযুক্ত ভগ্নাংশের যোগ ও বিয়োগ](reader/modules/m81289.html): complete m81289, including objectives, readiness, six lessons, summary,120 section exercises and glossary;574 MathML expressions and50 image occurrences.
- [মিশ্র ভগ্নাংশের যোগ ও বিয়োগ](reader/modules/m81290.html): complete m81290, including objectives, readiness, five lessons, summary and62 section exercises;248 MathML expressions and56 image occurrences. Model review closed the initial full59desktop+2narrow pass and21finaldesktop+2narrow affected spots; human review remains pending.
- [ভগ্নাংশযুক্ত সমীকরণের সমাধান](reader/modules/m81291.html): complete13-block module,593MathML expressions and97image occurrences; includes section exercises, chapter review and chapter practice test. Full model review is active.
- [দশমিক সংখ্যার পরিচয়](reader/modules/m81292.html): complete short3-block introduction with one original price photograph; historical/currency context and original photographer credit retained. Parent inspected both desktop captures and narrow endpoints.
- [U05: গোটা ও ভগ্নাংশ](reader/U05-companion.html): separate new/adapted AX-3 companion on mixed-number addition/subtraction, carrying, regrouping, negative-sign scope and a length problem;6 preparation questions,7 worked explanations,6 exit questions and full answers.
- [U04: একই মাপের ভাগ](reader/U04-companion.html): separate new/adapted AX-3 companion on same/different-denominator addition/subtraction, operation choice and complex fractions;6 preparation questions,7 worked explanations,6 exit questions and full answers.
- [U03: মিশ্র ভগ্নাংশ, বন্ধনী ও জটিল ভগ্নাংশ](reader/U03-companion.html): separate new/adapted AX-3 companion,6 preparation questions,7 worked explanations,6 exit questions, full answers and an explicitly labelled variable-domain extension.
- [U02: লঘিষ্ঠ আকার, গুণ ও ভাগ](reader/U02-companion.html): separate new/adapted AX-3 companion,6 preparation questions,7 worked explanations,6 exit questions, full answers and provisional error-based routing.
- [U01: ভগ্নাংশ থেকে সমীকরণ — separate AX-3 companion](reader/U01-companion.html): 6 placement questions, 7 worked examples, 6 exit/practice questions, complete solutions and provisional teacher routing.
- [U01: সমতুল ভগ্নাংশ নির্ণয় — source-faithful subsection](reader/U01-source-faithful.html): A00 `m81285 / fs-id1726667`, including 2 source examples, 4 additional practice exercises, their solutions and 5 source images.
- [Editable companion](translations/U01-companion.md), [translation overlay](translations/m81285-fs-id1726667.bn-Beng-IN.json) and [generated CNXML](translations/m81285-fs-id1726667.bn-Beng-IN.cnxml).

Open the index in a modern browser with Bengali fonts. Readers, images and local notices work offline; labelled external source links require internet. Keep the whole language folder together, including `provenance/`. Source-absent solutions remain absent (38,48,39,31,60 and31 questions in the six modules' section exercises respectively); original wrong/English raster content is preserved with accurate Bengali descriptions and explicit editorial warnings. The source-faithful edition does not silently invent answers or alter image pixels.

## Acquired source coverage

All five assigned Indonesian repositories (catalog plus four courses) are downloaded. All four release source ZIPs under ignored `downloads/` are SHA-256 matched to the recorded expected digests and CRC checked. Full duplicate extraction was stopped/skipped when the coordinator reported critically low disk space; the pilot uses small canonical source witnesses instead. Exact URLs, sizes, commits, inventories and notices are in [sources.lock.json](sources.lock.json) and [release lock](provenance/releases.lock.json).

| Input | Indonesian release coverage | Canonical text acquired for assignment | Bengali production |
|---|---|---|---|
| A00 Prealgebra 2e | v0.2.7, 75/75 | 75 collection modules | Eight complete modules; m81293 in progress |
| A10 Elementary Algebra 2e | corrected v1.0.2, 82/82 | 82 collection modules | Acquired; translation not started |
| A20 Intermediate Algebra 2e | v0.3.0-wip, 48/83 | 83 collection modules | Acquired; translation not started |
| A30 Precalculus 2e | alpha.58-reader.1, 58/87 | selected m49301 and m49324, with 74 referenced media files | Acquired for future prerequisites |
| AX-3 | Catalog specification | Definitions, summaries and worked explanations; separate from source edition | U01–U05 companions; full workflow ongoing |

A20's repository README is stale; the newer release manifest establishes 48/83. Full A30 media acquisition is not claimed. The A00–A20 canonical bundle pin is `38cae454e644abf9f0a623e876994553881597c9`; A30 is `789b54099106b071d1d32bfcee454fed72eb4768`. Shared sparse checkouts were insufficient for media, so the complete pinned A00–A20 archive extraction supplied missing files read-only. A30 selected images were fetched at its exact pin and verified against Git blob IDs.

## Canon use is part of translation

[22 readable target-language exemplars](canon/examples.tsv) are drawn from OCR-checked West Bengal Class VII material and explicitly supplementary Tripura Class VI Bengali material. Targeted additions after the initial bank support like terms, LCM, decimal place value/readings, Indian/international number naming and estimation terminology. See [mandatory consultation loop](canon/README.md), [U01 consultations](canon/consultations.json), [U02 consultations](canon/U02-consultations.json), [U03 consultations](canon/U03-consultations.json), [U04 consultations](canon/U04-consultations.json), [U05 consultations](canon/U05-consultations.json), per-section records in canon/sections, [reference/OCR hashes](canon/references.lock.json), and [52-term ledger](terminology.tsv). Government PDFs remain local reference inputs; their prose is not copied into this derivative. These sources are language witnesses, not mathematical or curricular certification.

The user clarified this requirement after the initial draft. It was applied during revision and QA; the log does not pretend those earlier drafting stages had consultations that did not occur.

## Build and verification

From the project root, using Python 3.12 or newer (standard library only for the pilot):

```powershell
python -X utf8 -B languages/bn-Beng-IN/scripts/build.py
python -X utf8 -B languages/bn-Beng-IN/scripts/qa.py
python -X utf8 -B languages/bn-Beng-IN/scripts/qa_checkpoint.py m81285 m81286 m81287 m81288 m81289 m81290 m81291 m81292
```

Frozen module witnesses, [media lock](provenance/media.lock.json) and small preserved images support offline builds without the large ignored downloads/shared corpora. New source freezing still uses pinned-source verification. Acquisition scripts describe the original local process; `stage_shared_canonical.py` intentionally names this machine's read-only donor paths and is not a universal bootstrap script.

The eight complete modules preserve33684 source nodes,6150 IDs and2983 MathML expressions. Exactly35 linguistic mtext labels are translated through an explicit reversible exception; numbers, operators, order and mathematical structure stay unchanged. A separate narrow caption-only exception preserves exact original photographer names, with six regression tests preventing other English from bypassing translation checks. [Checkpoint QA](qa/checkpoint.json) compares303 outputs across two builds. U02/U03/U04/U05 add23/27/37/40 exact-rational checks and12 actual answer-key regressions each, plus unit-specific worked-step, coefficient, LCM and sign-scope checks. Browser receipts under qa/browser are reader-hash-bound. Module model peer reviews under qa distinguish actual visual coverage, corrections and self-review from independent human validation. The two-module commit35b8743 passed an isolated87-output Git-archive rebuild; four-module cbc493d passed164checkpoint plus24partial-section outputs, each twice, with donor/download roots deliberately unavailable. Newer replay evidence is recorded separately in DECISIONS.md.

[Acquisition verification](qa/acquisition-check.json) checked242 canonical module references and11,046 referenced media files against the pinned Git objects, with A00–A20 media accessed read-only from the shared complete extraction. Its historical receipt covers34 reference artifacts; targeted additions bring the current reference lock to48. This does not claim that the interrupted local bulk media snapshot is complete. [Pilot QA](qa/status.json) passes20 exact-rational checks and12 answer-key regressions. Browser checks cover1200px and390px widths, images, MathML, Bengali font availability and horizontal overflow. The in-app runtime was unavailable; an isolated local Edge render was used without external requests or access to user sessions. Renderer-only fallbacks preserve long-division brackets and cancellation strokes without altering source MathML; a narrowly scoped mixed-number table rule separates prose from tall inline mathematics.

Original image pixels are preserved, including the English word "so" in one formula image; its full mathematical meaning is supplied in the Bengali description. Source-image color discrepancies are recorded in DECISIONS.md. The small pilot rebuild is self-contained; the optional full acquisition verifier requires the ignored local/shared corpora.

Independent West Bengal Bengali language review, teacher review, learner comprehension testing and screen-reader validation remain pending. Provisional learning routes must not be used for high-stakes placement. Source-faithful and companion progress markers remain separate in [NEXT.md](NEXT.md).

## Attribution and durable workflow

OpenStax, Rice University, *Prealgebra 2e*, Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis; full contributor acknowledgements remain in [source preface](provenance/pilot/m81241.source.cnxml). Indonesian inputs: KokunoYumeto's repositories and release notices under `provenance/`. Bengali translation/adaptation is unofficial, assisted by OpenAI Codex, with no endorsement claimed. Preserve [CC BY-NC-SA 4.0](provenance/A00/repository/LICENSE), upstream notices and component exceptions. No training/fine-tuning dataset was created. The coordinator now manages a single authorized GitHub review branch; the initial upload is incomplete and exact remote coverage must be checked centrally. This language task does not independently push, merge to main or publish a final production release.

Resume by reading [WORK_GOAL.md](WORK_GOAL.md), [DECISIONS.md](DECISIONS.md), [NEXT.md](NEXT.md), the locks and QA records. Verify actual files and Git state; treat conversation summaries as untrusted retrieval hints. Read the user's messages in the coordinating task specified in `COORDINATING_TASK.md` before relying on relayed workflow changes.
