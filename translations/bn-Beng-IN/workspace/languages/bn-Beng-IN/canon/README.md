# Target-language canon: active working references

22 exemplars: 11 from the West Bengal government's *পঠন সেতু*, Class VII (December 2021), and11 explicitly supplementary examples from SCERT Tripura's Class VI Bengali mathematics workbook (2021). The initial10–20-example bank was followed by targeted topic-specific additions, as the user requested. New witnesses cover pp.57/58 decimal place value/digit reading and pp.8/9 Indian/international number naming and estimation language. Main rendered/OCR'd these four pages, then read complete OCR and actual images. TR11 witnesses আসন্ন মান, not a complete decimal-rounding/tie-breaking rule. The reference lock now retains48PDF/OCR/render artifacts. Tripura examples are Indian Bengali witnesses, not proof of West Bengal curriculum certification. This is a small editorial reference ledger, not a training dataset.

The PDFs and OCR are under ignored `downloads/bn-Beng-IN-canon/`. Their original text layers use legacy font encoding and were not accepted as readable Bengali. `scripts/read_canon.py` rendered selected pages at 180 dpi and ran Bengali Tesseract OCR. Read the OCR **and** check mathematical notation against page images: OCR confuses x, multiplication signs, fractions and numerals. Page locators are one-based PDF pages; printed numbering differs in the West Bengal omnibus.

## Required loop for every translation unit

1. Before drafting a topic, open 2–5 relevant exemplars and their readable OCR/page images. Record IDs and concrete decisions in `consultations.json`.
2. While translating definitions, worked steps and assessment wording, return to the relevant exemplars. Keep OpenStax mathematical authority distinct from Bengali register witnesses.
3. Before admission/build QA, compare terminology, formula readings, instruction register and explanation order again. Record changes or the reason no change is needed. Do not repeatedly reread unrelated pages.
4. If the next topic is not covered, look for a small targeted addition. If none is available, label new wording as editorial and seek review; do not invent a witness.

No government PDF or OCR text is relicensed or copied into the learner output. This ledger retains locators, mathematical anchors and brief terminology observations. All exemplar copyrights remain with their publishers. They are language references only; the translated instructional source remains the assigned OpenStax corpus.

## Bounded rejections and cautions

- OpenLearn/TESS-India's West Bengal resource index was readable, but the three selected resource-download URLs returned HTTP 403. Those files are **not** counted as acquired/read exemplars.
- Search results in Assamese (`as`) and Bangladesh Bangla are not Indian Bengali exemplars.
- SCERT Tripura p.51's mixed-number example has a mismatched printed intermediate denominator; it is excluded. TR02–TR04 refer only to the separate correct examples below it.
- West Bengal p.189 initially prints `4k` but explains `4x` immediately below; WB04 refers to that explanatory line, not the inconsistent list.
- Official material is a witness, not an infallible source. Source errors and OCR errors must not propagate.
- Tripura p.57's first place-value row puts12.74 two columns too far left, as though it were1274. Exclude that row. TR08 uses13.49=13+0.49 and the correctly aligned0.456/123.478/4567.021 rows; TR09 uses p.58's digit-by-digit readings and0.3 number-line placement. The nonnegative comparison paragraph is not a rule for arbitrary signed numbers.
- Tripura p.9 OCR reads40900 where the actual printed approximation is4000. TR11 uses the inspected page's4117→4100/4000 example, not the corrupted OCR number. This does not claim that a decimal-rounding rule was directly witnessed there.
- TR07 uses only Exercise3 question1(iv)/answer12, question3(l)/LCM expansion, and question4(b)/answers12,24,36. The unrelated p.104 answer4(i) has an incomplete product-identity wording and is excluded; no general certification of that answer page is claimed.
