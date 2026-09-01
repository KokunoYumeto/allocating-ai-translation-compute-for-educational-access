# Indian Bengali mathematics translation

Locale: `bn-Beng-IN`. Rank 4 assignment: full assigned A00–A20 collections, selected A30 and a distinct AX-3 recovery workflow, focused on Indian/West Bengal Bengali. The recovery pathway centres on Grades 3–8; advanced assigned content is not dropped. This is not a certified curriculum or validated diagnostic test.

The entire assignment is ongoing. Four of242 collection-module references have full learner-text coverage: m81285–m81288. U01 commit `713370c` was only the first checkpoint. Consult [full module/block progress](progress.json) and [current work cursor](NEXT.md); partial later sections do not imply a complete module or book.

## Read the actual output

- [Offline reading index](reader/index.html).
- [চিত্রের সাহায্যে ভগ্নাংশ বোঝা](reader/modules/m81285.html): complete m81285, including objectives, readiness, seven instructional sections, summary,76 section exercises and glossary;510 preserved MathML expressions and100 image occurrences.
- [ভগ্নাংশের গুণ ও ভাগ](reader/modules/m81286.html): complete m81286, including objectives, readiness, four instructional sections, summary,99 section exercises and glossary;495 preserved MathML expressions and38 image occurrences.
- [মিশ্র ভগ্নাংশ ও জটিল ভগ্নাংশের গুণ ও ভাগ](reader/modules/m81287.html): complete m81287, including objectives, readiness, four lessons, summary,78 section exercises and glossary;318 MathML expressions and3 image occurrences.
- [একই হরযুক্ত ভগ্নাংশের যোগ ও বিয়োগ](reader/modules/m81288.html): complete m81288, including objectives, readiness, four lessons, summary and62 section exercises;245 MathML expressions and22 image occurrences.
- [U03: মিশ্র ভগ্নাংশ, বন্ধনী ও জটিল ভগ্নাংশ](reader/U03-companion.html): separate new/adapted AX-3 companion,6 preparation questions,7 worked explanations,6 exit questions, full answers and an explicitly labelled variable-domain extension.
- [U02: লঘিষ্ঠ আকার, গুণ ও ভাগ](reader/U02-companion.html): separate new/adapted AX-3 companion,6 preparation questions,7 worked explanations,6 exit questions, full answers and provisional error-based routing.
- [U01: ভগ্নাংশ থেকে সমীকরণ — separate AX-3 companion](reader/U01-companion.html): 6 placement questions, 7 worked examples, 6 exit/practice questions, complete solutions and provisional teacher routing.
- [U01: সমতুল ভগ্নাংশ নির্ণয় — source-faithful subsection](reader/U01-source-faithful.html): A00 `m81285 / fs-id1726667`, including 2 source examples, 4 additional practice exercises, their solutions and 5 source images.
- [Editable companion](translations/U01-companion.md), [translation overlay](translations/m81285-fs-id1726667.bn-Beng-IN.json) and [generated CNXML](translations/m81285-fs-id1726667.bn-Beng-IN.cnxml).

Open the index in a modern browser with Bengali fonts. Readers, images and local notices work offline; labelled external source links require internet. Keep the whole language folder together, including `provenance/`. Source-absent solutions remain absent (38,48,39 and31 questions in the four modules' section exercises respectively); original wrong/English raster content is preserved with accurate Bengali descriptions and explicit editorial warnings. The source-faithful edition does not silently invent answers or alter image pixels.

## Acquired source coverage

All five assigned Indonesian repositories (catalog plus four courses) are downloaded. All four release source ZIPs under ignored `downloads/` are SHA-256 matched to the recorded expected digests and CRC checked. Full duplicate extraction was stopped/skipped when the coordinator reported critically low disk space; the pilot uses small canonical source witnesses instead. Exact URLs, sizes, commits, inventories and notices are in [sources.lock.json](sources.lock.json) and [release lock](provenance/releases.lock.json).

| Input | Indonesian release coverage | Canonical text acquired for assignment | Bengali production |
|---|---|---|---|
| A00 Prealgebra 2e | v0.2.7, 75/75 | 75 collection modules | Four complete modules; m81289 in progress |
| A10 Elementary Algebra 2e | corrected v1.0.2, 82/82 | 82 collection modules | Acquired; translation not started |
| A20 Intermediate Algebra 2e | v0.3.0-wip, 48/83 | 83 collection modules | Acquired; translation not started |
| A30 Precalculus 2e | alpha.58-reader.1, 58/87 | selected m49301 and m49324, with 74 referenced media files | Acquired for future prerequisites |
| AX-3 | Catalog specification | Definitions, summaries and worked explanations; separate from source edition | U01–U03 companions; full workflow ongoing |

A20's repository README is stale; the newer release manifest establishes 48/83. Full A30 media acquisition is not claimed. The A00–A20 canonical bundle pin is `38cae454e644abf9f0a623e876994553881597c9`; A30 is `789b54099106b071d1d32bfcee454fed72eb4768`. Shared sparse checkouts were insufficient for media, so the complete pinned A00–A20 archive extraction supplied missing files read-only. A30 selected images were fetched at its exact pin and verified against Git blob IDs.

## Canon use is part of translation

[18 readable target-language exemplars](canon/examples.tsv) are drawn from OCR-checked West Bengal Class VII material and explicitly supplementary Tripura Class VI Bengali material. Targeted additions support like terms and LCM terminology/answers. See [mandatory consultation loop](canon/README.md), [U01 consultations](canon/consultations.json), [U02 consultations](canon/U02-consultations.json), [U03 consultations](canon/U03-consultations.json), per-section records in canon/sections, [reference/OCR hashes](canon/references.lock.json), and [40-term ledger](terminology.tsv). Government PDFs remain local reference inputs; their prose is not copied into this derivative. These sources are language witnesses, not mathematical or curricular certification.

The user clarified this requirement after the initial draft. It was applied during revision and QA; the log does not pretend those earlier drafting stages had consultations that did not occur.

## Build and verification

From the project root, using Python 3.12 or newer (standard library only for the pilot):

```powershell
python -X utf8 -B languages/bn-Beng-IN/scripts/build.py
python -X utf8 -B languages/bn-Beng-IN/scripts/qa.py
python -X utf8 -B languages/bn-Beng-IN/scripts/qa_checkpoint.py m81285 m81286 m81287 m81288
```

Frozen module witnesses, [media lock](provenance/media.lock.json) and small preserved images support offline builds without the large ignored downloads/shared corpora. New source freezing still uses pinned-source verification. Acquisition scripts describe the original local process; `stage_shared_canonical.py` intentionally names this machine's read-only donor paths and is not a universal bootstrap script.

The four complete modules preserve17274 source nodes,3100 IDs and1568 MathML expressions. Exactly31 linguistic mtext labels are translated through an explicit reversible exception; numbers, operators, order and mathematical structure stay unchanged. [Checkpoint QA](qa/checkpoint.json) compares164 outputs across two builds. U02 adds23 exact-rational checks and12 actual answer-key regressions; U03 adds27 rational checks,12 answer-key regressions,16 worked-step text regressions and one exact monomial check. Browser receipts under qa/browser are reader-hash-bound. Module model peer reviews under qa distinguish actual visual coverage, corrections and self-review from independent human validation. The earlier two-module commit35b8743 also passed an isolated87-output Git-archive rebuild with donor/download roots deliberately unavailable; later replay evidence is recorded separately in DECISIONS.md.

[Acquisition verification](qa/acquisition-check.json) checked242 canonical module references and11,046 referenced media files against the pinned Git objects, with A00–A20 media accessed read-only from the shared complete extraction. Its historical receipt covers34 reference artifacts; the targeted LCM addition brings the current reference lock to40. This does not claim that the interrupted local bulk media snapshot is complete. [Pilot QA](qa/status.json) passes20 exact-rational checks and12 answer-key regressions. Browser checks cover1200px and390px widths, images, MathML, Bengali font availability and horizontal overflow. The in-app runtime was unavailable; an isolated local Edge render was used without external requests or access to user sessions. Renderer-only fallbacks preserve long-division brackets and cancellation strokes without altering source MathML.

Original image pixels are preserved, including the English word "so" in one formula image; its full mathematical meaning is supplied in the Bengali description. Source-image color discrepancies are recorded in DECISIONS.md. The small pilot rebuild is self-contained; the optional full acquisition verifier requires the ignored local/shared corpora.

Independent West Bengal Bengali language review, teacher review, learner comprehension testing and screen-reader validation remain pending. Provisional learning routes must not be used for high-stakes placement. Source-faithful and companion progress markers remain separate in [NEXT.md](NEXT.md).

## Attribution and durable workflow

OpenStax, Rice University, *Prealgebra 2e*, Lynn Marecek, MaryAnne Anthony-Smith and Andrea Honeycutt Mathis; full contributor acknowledgements remain in [source preface](provenance/pilot/m81241.source.cnxml). Indonesian inputs: KokunoYumeto's repositories and release notices under `provenance/`. Bengali translation/adaptation is unofficial, assisted by OpenAI Codex, with no endorsement claimed. Preserve [CC BY-NC-SA 4.0](provenance/A00/repository/LICENSE), upstream notices and component exceptions. No training/fine-tuning dataset was created, and nothing was pushed or published.

Resume by reading [WORK_GOAL.md](WORK_GOAL.md), [DECISIONS.md](DECISIONS.md), [NEXT.md](NEXT.md), the locks and QA records. Verify actual files and Git state; treat conversation summaries as untrusted retrieval hints. Read the user's messages in the coordinating task specified in `COORDINATING_TASK.md` before relying on relayed workflow changes.
