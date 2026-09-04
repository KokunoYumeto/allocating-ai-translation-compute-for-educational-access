# Vietnamese working canon

These are 12 concrete, located language-use examples from two readable Vietnamese
mathematical references, not 12 whole books. They guide terminology and exposition;
they do not replace the pinned mathematical source and are not a training dataset.
No external reference exercise is copied into the pilot. Full reference files and
OCR stay under ignored `downloads/vi-canon/`; hashes and locators are committed.

## Sources and reading

- C-VI-01: Bùi Xuân Diệu, *Bài giảng Giải tích I*, Hanoi University of Science
  and Technology, 2009, departmental PDF. [Official copy](https://fami.hust.edu.vn/wp-content/uploads/Giai-tich-1.pdf).
  Downloaded whole PDF (98 pages). Native text extracted. PDF pages 7–10 (printed
  pages 6–9) rasterized, OCRed with Tesseract `vie`, read, and visually compared.
  OCR damages formula symbols and some accents; it is a prose-navigation aid,
  not formula authority. No redistribution license is assumed for this witness.
- C-VI-02: *Bài 15: Ánh xạ tuyến tính*, the author's Vietnamese teaching page at
  [daisotuyentinh.com](https://www.daisotuyentinh.com/2023/08/anh-xa-tuyen-tinh_21.html).
  The downloaded HTML has readable Vietnamese and literal LaTeX. Read §15.1,
  Definition 15.1, Example 15.2, and Proposition 15.3 with its proof.
  This is a terminology witness, not an incorporated textbook component.

## Twelve starting examples

| ID | Located example | Short language form | Production use |
|---|---|---|---|
| VI-C01 | C-VI-01, printed p.6, §3(1) mapping/formula distinction | tập xác định | Prefer this school-facing term; retain miền xác định as an accepted synonym. |
| VI-C02 | C-VI-01, p.6, immediately after §3(1) | tập giá trị | Range means values attained, not codomain. |
| VI-C03 | C-VI-01, p.7, Exercise 1.1 | TXĐ | Expand abbreviations for a beginning self-study reader. |
| VI-C04 | C-VI-01, p.7, Exercise 1.2 | miền giá trị | Recognize the variant but use the ledger's range term consistently. |
| VI-C05 | C-VI-01, p.7, Exercise 1.3 | — | Preserve f and its argument while translating the instruction to find the function. |
| VI-C06 | C-VI-01, p.7, Exercise 1.4(a) | hàm ngược | Keep inverse-function conditions separate from reversing a relation. |
| VI-C07 | C-VI-01, p.8, continuation of 1.4(c) | đơn ánh | Reserve for one-to-one, not for the basic definition of function. |
| VI-C08 | C-VI-01, p.8, Exercise 1.5 | — | Distinguish parity of functions from parity labels for numbers in U001. |
| VI-C09 | C-VI-01, p.8, Exercise 1.6 | Chứng minh | Use for proof prompts, not finite computational checks. |
| VI-C10 | C-VI-01, p.8–9, Exercise 1.7 | — | Explain assumptions, then conclusion; do not copy its formula derivation. |
| VI-C11 | C-VI-02, §15.1, Definition 15.1 | ánh xạ tuyến tính | Future B40 term; retain linearity hypotheses. |
| VI-C12 | C-VI-02, §15.1, Example 15.2 | ánh xạ đồng nhất | Do not confuse identity with constant maps. |

The short quotations from C-VI-01 above total fewer than 25 words. Other cells
are our descriptions of use, not reproduced passages.

## Mandatory per-unit loop

1. Before drafting, open the relevant original/reference pages and the terminology
   ledger. Record IDs and exact local source hashes in `review-<unit>.json`.
2. While translating definitions, exercises, answers, and computing commentary,
   return to the relevant examples. Log decisions and conflicts in DECISIONS.md.
3. After drafting, reread those examples and review term consistency and scope.
   Bind the review to the final translation SHA-256. A build fails if the draft
   changes without a matching canon-review receipt.
4. Add targeted examples only when a new topic needs them. Do not endlessly reread
   or restart a supply audit. If an adequate witness is absent, record an original
   terminology decision honestly and flag it for native review.

## Limits discovered while actually reading

The HUST notes contain mathematical slips, e.g. printed p.9 Exercise 1.8's
reported affine coefficient does not satisfy its given value at 3. The pilot
does not reuse that answer or any HUST exercise. This confirms why a language
witness cannot override the canonical OpenStax/CLP/Hefferon mathematics.
The downloaded assigned A30 control/terminology files and B20/B80 material
checked so far contain no reusable Vietnamese text; no broad external inventory
is inferred from that limited check.
