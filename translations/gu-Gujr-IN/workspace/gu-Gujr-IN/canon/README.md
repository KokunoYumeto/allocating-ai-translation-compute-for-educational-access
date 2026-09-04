# Gujarati usage canon: read at each production stage

The user clarified that canon means readable target-language examples as well as source authority. The starting canon has **13 specific examples**, selected from Gujarati school materials hosted by Samagra Shiksha Gujarat. These are linguistic reference examples, not replacement translation sources or a training dataset. Four reference PDFs are downloaded under ignored `downloads/gu-Gujr-IN/gujarati-canon/`; the 13 admitted examples come from two of them.

PDFs are scanned/legacy-encoded. Ran Gujarati Tesseract OCR on selected pages **before reading their text**, then checked the admitted example pages against rendered page images. Some initially selected pages belonged to English or Gujarati language sections and were rejected. Do not cite those as mathematics evidence. OCR is fallible: it confused ૮/૯, plus signs, and numeral grouping. Numeric values and wording in the notes were checked against page images; OCR is not mathematical authority.

`examples.csv` identifies each example by PDF page (1-based), printed page and question. The notes record a linguistic/structural observation rather than copying exercises into the Gujarati package. `reference-lock.json` pins PDF, OCR and rendered-page hashes. Original PDFs and full OCR text remain ignored. Read the relevant local OCR **and** page image when a decision depends on a symbol, number or uncertain character.

Mandatory workflow, repeated for each new translation unit:

1. Before drafting: read the relevant canon examples; select explicit example IDs in the unit log. Do not merely list sources.
2. During translation: compare terms, command forms and explanation register with those examples. Record adoption, rejection or missing coverage in terminology and decisions.
3. Before build: reread the selected examples against the actual Gujarati draft. Record corrections and preserve the source/companion boundary.
4. Before acceptance: check rendered Gujarati output against the same references and record unresolved linguistic issues. Add topic-specific examples when the existing canon does not cover the next material; do not loop on indiscriminate reading.

The initial draft preceded this clarification. Its first canon pass was a corrective review; no pre-draft canon consultation is claimed retroactively. This packet supports numeral/place-value/order register. It does not fully resolve natural-number, coordinate or fraction terminology; those remain explicit review items and need additional references when expanded.

Sources: [Std 5 Week 1](https://ssagujarat.org/StudyFromHome/Std%205-Week1.pdf), [Std 6 Week 1](https://ssagujarat.org/StudyFromHome/Std%206-Week1.pdf). Inbound reference acquisition does not change their copyright or license; only brief terms and original notes are retained here.
