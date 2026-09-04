# Intermediate Algebra 2e: Shahmukhi Punjabi preface

Open [the offline HTML reader](index.html) or [the PDF reader](output/pdf/a20-preface-shahmukhi.pdf).

This is the complete recovered **preface m81357 only**, not a complete textbook, chapter, or translated version of the later chapter summaries. It contains 89 source text owners, 66 source IDs, 26 sections, 33 paragraphs, 25 list items and four original images. The module contains no MathML, exercises or supplied solutions. No new questions or answers are added.

The local-needs direction remains a Shahmukhi Punjabi secondary-to-undergraduate bridge into Urdu and English. Punjabi is the reader language; Urdu/English are explicitly marked terminology bridges. The wider assigned A10/A20/A30/discrete/linear-algebra programme remains unfinished and outside this package. Acquired sources and future Bengali, Telugu or Tamil scope are not translated-content credit.

## What changed in recovery

- Preserved all 89 faithful source blocks and all four exact source images.
- Corrected the separate Urdu bridge's `دو رقمی قضیہ` (two-digit wording) to `دو رکنی قضیہ` (two-term wording) for binomial theorem. The Punjabi source wording `دو رکنی کلیہ` was already appropriate and unchanged.
- Added standalone offline font-backed HTML, mobile reflow, a print reader and bounded source/asset/structure/encoding/visual QA.
- Preserved original source discrepancies as separately labeled notes, all author/reviewer credits, and component rights.
- Kept inherited canon/style bytes pinned; only this book's style and correction records are new.

The historical Indonesian comparison checkpoint is preserved as historical evidence in `source/recovered-manifest.json`; its old WIP label does not reopen or describe the current completed Indonesian book.

## Provenance and reproducibility

Source: OpenStax col31234 / m81357 at upstream commit `38cae454e644abf9f0a623e876994553881597c9`. Intake: public `ed6f2e2020118723c2a12fe3377d2273c3d8ec50` revision of the existing translation-compute repository. See `source-pins.json`, `checksums.sha256` and `qa/verification.json` for exact bytes, scope and limitations.

Run `python scripts/build_reader.py`, then `node scripts/build_pdf.cjs`. The latter requires Playwright and a Chromium browser; set `A20_PLAYWRIGHT_MODULE` and `A20_CHROMIUM_PATH` if needed. It performs offline resource/viewport checks and prints only this reader. No TeX is used. `python scripts/verify.py` runs independent source/DOM/PDF and manifest checks. PDF byte identity is frozen in the release manifest; content, layout and HTML reproducibility are the deterministic checks, not an unsupported promise of identical Chromium PDF timestamps across machines.

The PDF contains structural tags and bookmarks, but is not PDF/UA-certified. Arabic presentation forms in extracted text require Unicode NFKC normalization, and mixed-direction reading order can vary by PDF tool. The static-font edition eliminates the missing/null-character extraction seen in the rejected variable-font build. The semantic HTML is the primary accessible alternative. Native Shahmukhi terminology consensus and screen-reader pronunciation are not claimed.

## Rights and credits

OpenStax / Rice University; senior contributing authors Lynn Marecek and Andrea Honeycutt Mathis, with all source reviewers retained. CC BY-NC-SA 4.0 subject to component exceptions. Bundled Noto font: SIL OFL 1.1. Canon quotations: attributed linguistic evidence, not a claim of CC licensing. See `LICENSE.txt`.

Produced with OpenAI Codex assistance at the user's direction. Recovery model identification: **OpenAI Codex gpt-5.6-sol, Ultra**. Preserved human-contributor credits are not replaced by model credit.

Next executable source anchor: **m81358, Introduction**, followed by its first mathematical section, under the canonical owner's separate continuation scope. It is not translated here.
