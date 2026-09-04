# Andhra Pradesh acquisition gap and verified Telangana Class 6 witness

Checked 2026-08-30. This is a bounded regional terminology investigation, not a
new supply or licence audit. No Andhra Pradesh PDF was successfully acquired in
this attempt. The successful Telangana witness is recorded separately; it must
not be relabelled as Andhra Pradesh evidence.

## Acquired witness

- Witness ID: `TS6-2018`.
- Title: *గణితం*, Class 6, Government of Telangana, Hyderabad.
- [Official source PDF](https://www.scert.telangana.gov.in/PDF/publication/ebooks/6TM_MAT.pdf).
- Working file: `downloads/canon/ap/TS-6TM-MAT.pdf`.
- Bytes: `20725077`.
- SHA-256: `3faa1f0551382ea25853d62604c63aa27034c6c07f7d56ce016c83d36b6f90ee`.
- PDF pages: `226`.
- Edition evidence, visually read at PDF pages 3-4: first published 2012;
  impressions listed through 2018; footer identifies free distribution 2018-19.
  This is the file currently obtained from the official endpoint, not a claim
  that its content is a newly revised 2026 edition.
- Preserve the Government of Telangana attribution and the existing notice at
  PDF page 4. Full PDF, renderings, and raw OCR remain ignored reference inputs;
  this record provides short terminology citations and original analytical notes.

The first transfer timed out after 35 seconds at 4,931,072 bytes. A range-resumed
transfer completed the 20,725,077-byte file. Two redundant incomplete copies were
removed after the complete file was validated. They are not additional acquired
books.

## Reading and OCR receipt

Before using the witness for terminology, rendered pages with Poppler and OCRed
them with Tesseract (`tel+eng`, using `downloads/canon/tessdata`). Read the OCR and
then inspected the page PNGs, correcting OCR against the visible typography and
mathematics. Commands used this pattern:

```powershell
pdftoppm -f 26 -l 28 -scale-to 2200 -png downloads/canon/ap/TS-6TM-MAT.pdf downloads/canon/ap/TS6-sets
pdftoppm -f 83 -l 85 -scale-to 2200 -png downloads/canon/ap/TS-6TM-MAT.pdf downloads/canon/ap/TS6-sets
& 'C:/Program Files/Tesseract-OCR/tesseract.exe' downloads/canon/ap/TS6-sets-026.png downloads/canon/ap/TS6-sets-026 -l tel+eng --tessdata-dir downloads/canon/tessdata
```

The same OCR command pattern was run for every selected page. Working outputs:

| PDF page | Printed page / locator | Render and OCR basenames | Use |
| --- | --- | --- | --- |
| 3-4 | i-ii, title/imprint | `TS6-front-003`, `TS6-front-004` | Government/edition attribution; read and viewed |
| 9 | vii, contents | `TS6-toc-009` | Chapter 2 and chapter 6 distinguished; read and viewed |
| 26 | 16, §§2.1-2.2 | `TS6-sets-026` | Natural/whole sets and predecessor/successor; read and viewed |
| 27 | 17, §2.3 | `TS6-sets-027` | Number line and whole-number addition; read and viewed |
| 28 | 18, continuation | `TS6-sets-028` | OCR generated; not used as a visual-verified exemplar |
| 83-84 | 73-74, §§6.1-6.3 | `TS6-sets-083`, `TS6-sets-084` | Integer chapter context; read and viewed |
| 85 | 75, definition and §6.4 | `TS6-sets-085` | Integer set and signed number line; read and viewed |

All basenames above are under `downloads/canon/ap/`; each selected mathematics
page has `.png` and `.txt` outputs. The preliminary front-matter OCR output uses
the generated suffix `..txt`, while contents and mathematics OCR use `.txt`.
Front pages 1-8 were rendered at 1400 pixels; pages 9-12 at 1800; the selected
mathematics pages at 2200. Only visually checked content is evidence below.

Raw OCR is not a quotation authority: it dropped `1` from the whole-number set,
damaged several letters in the whole-number term, and misread some signs. The
rendered PDF visibly resolves those errors. A second agent independently read
the OCR and viewed pages 26, 27, and 85, confirming the whole/integer distinction.

## Six bounded terminology exemplars

The mathematical restatements are review notes, not substituted textbook prose.
They retain the witnessed convention and its original symbols.

| ID | English concept | Telugu witness | Exact anchor and mathematical evidence | AP evidence |
| --- | --- | --- | --- | --- |
| TS6-NAT-016 | natural/counting numbers | సహజ సంఖ్యలు | PDF 26 / printed 16, §2.1: `N = {1, 2, 3, 4, ...}`; used for counting objects | Not acquired |
| TS6-WHOLE-016 | whole numbers | పూర్ణాంకాలు | PDF 26 / printed 16, §2.2: `W = {0, 1, 2, 3, ...}`; adds zero to the natural-number set | Not acquired |
| TS6-INT-075 | integers | పూర్ణసంఖ్యలు | PDF 85 / printed 75: `Z = {..., -3, -2, -1, 0, 1, 2, 3, ...}`; chapter heading at PDF 83 separates the words as `పూర్ణ సంఖ్యలు` | Not acquired |
| TS6-LINE-017 | number line | సంఖ్యా రేఖ | PDF 27 / printed 17, §2.3: equal intervals, larger whole numbers to the right, and `2 + 3 = 5` shown by three rightward unit steps | Not acquired |
| TS6-SUCC-016 | successor | ఉత్తర సంఖ్య | PDF 26 / printed 16, §2.1: successor of `9` is `10` | Not acquired |
| TS6-PRED-016 | predecessor | పూర్వ సంఖ్య | PDF 26 / printed 16, §2.1: predecessor of `9` is `8`; the natural-number boundary at `1` is discussed explicitly | Not acquired |

### Required integration decision

The draft mapping `whole numbers -> పూర్ణ సంఖ్యలు` and
`integers -> పూర్ణాంకాలు` reverses the distinction in this official Telangana
schoolbook. For a bridge using this canon, map whole numbers to `పూర్ణాంకాలు`
and integers to `పూర్ణసంఖ్యలు`, with parallel English labels and explicit sets
when the distinction is introduced. Update all connected reader, terminology,
diagnostic/solution, and QA expectations together; changing only the ledger would
leave learner-facing contradictions. Parent translation files were not edited by
this bounded investigation.

This finding is not an AP-versus-TS difference. Retain distinct AP/TS ledger
fields: Telangana verified by `TS6-2018`, Andhra Pradesh unverified. Do not infer
an AP term from this book's pre-2014 publication history or contributors' addresses.
Spacing of the integer term within one book is not evidence of a regional variant.

## Andhra Pradesh routes and limits

1. [Department of School Education Class 6 mathematics semester 1 PDF](https://cse.ap.gov.in/downloadBooks/Maths%20Books/6_Maths_SEM-1_Textbook.pdf/6):
   web fetch timed out; this attempt's shell connection also timed out after about
   10 seconds, without receiving a PDF. The parent had previously reported three
   failed connection attempts. Search-index text was used only to identify a
   question to investigate, not to establish any AP terminology in the ledger.
2. [Azim Premji University School Books Archive, item 11898](https://schoolbooksarchive.azimpremjiuniversity.edu.in/handle/20.500.12497/11898):
   web metadata page identified a Class 3 mathematics title, but no accessible
   attachment was returned. Shell request produced the 16-byte error body
   `error code: 522`, stored as `downloads/canon/ap/archive-11898.html`.
   It is an error receipt, not a book or canon witness.
3. [Bharatavani Class VI mathematics metadata](https://bharatavani.in/telugu/book?id=%E0%B0%97%E0%B0%A3%E0%B0%BF%E0%B0%A4%E0%B0%82,+6%E0%B0%B5+%E0%B0%A4%E0%B0%B0%E0%B0%97%E0%B0%A4%E0%B0%BF&post_category=text-book):
   the Ministry of Education/CIIL page identifies SCERT Andhra Pradesh as content
   partner, 2015, 4.2 MB, Class VI. Its reading link requires login. No login or
   access workaround was attempted, and no PDF was obtained from it.

Do not hash or inventory these failed paths as acquired AP books. A later,
bounded AP acquisition remains useful, particularly before claiming regional
equivalence. Until then, the honest output is a verified Telangana term set plus
an AP evidence gap.

## Decisions and next use

- AP-C01: Kept the investigation to government/institutional routes; did not
  replace the missing AP source with an unverified commercial mirror.
- AP-C02: Acquisition failure did not license invention of regional differences.
- AP-C03: Read the relevant PDF through OCR and visual checks before recommending
  a terminology change; treated the OCR errors as errors, not canon wording.
- AP-C04: Prioritized the whole/integer correction because the diagnostic bridge
  can otherwise teach exactly the wrong Telugu label for each set.
- AP-C05: Supplied six exemplars for recurring use, not a one-time inventory.
  Reopen `TS6-sets-026` and `TS6-sets-085` during the terminology correction, reread
  `TS6-sets-027` while checking the number-line explanation, and repeat these
  targeted checks against the final rendered unit. Do not loop over irrelevant
  front matter once provenance is recorded.
- AP-C06: Preserve the AP gap in the ledger and next-unit notes until an actual
  AP book can be OCRed and read. The pilot need not wait for an invented regional
  distinction or repeated unsuccessful download loop.
