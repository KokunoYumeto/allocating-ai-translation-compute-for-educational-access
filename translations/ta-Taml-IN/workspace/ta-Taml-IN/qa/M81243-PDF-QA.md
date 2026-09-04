# Integrated m81243 PDF candidates - verification in progress

2026-08-31. These new module candidates do not overwrite the historical U001/U002 PDFs. The complete-assignment goal stays active. No module PDF release, PDF/UA, native-language or assistive-technology approval is claimed here.

## Newest repair state — supersedes current-candidate approval language below

The223/260-page candidates below are now superseded **inputs**, awaiting re-export. Fullreview found a missingupperright number-line arrowhead in the originalTamilSVG; root inspected the pinnedJPEG, split the two upperpaths so each gets its own marker-end, and visually confirmed botharrows in the actuallearningbrowser. The newsource-review checker rejects a deletedrightmarker and the oldcompoundpath. SourceCNXML/math/words did notchange. NewlearningHTMLSHA`8f424a0b8d31f472d1b82a5a2e36053b6c00d558d1c40aa8e80e782510be45f6`; EPUB`ced73e55085c0b6e6bf089ea28ff497d3c4b7da84735fcb9a990254e0b4213ad`; EPUBCheckzeroerrors/warnings/info. The historicalU001HTML/EPUB/PDFs share the oldarrowheaddefect, so their earlier blanketvisualapproval is now explicitlyqualified; they remain unchangedpendingseparaterepair, not production-ready.

PDFCSS was also revised after actualreview: keep headings internally intact; keep the four-rowcheckpointtable with itscaption/header; keep sourceexerciseIDs with theiractualquestions; keep the boundedU002problem/model groupfs-id2652455; prevent fragmentation inside longMathMLwrappers and the largeM4firstanswerparagraph; keep roundingD4with itsfollowingnavigation. CSSSHA`5319652599aa19298689edda569d1991fc45da61b8cd760eef2c24ac2162f952`. These are pendingrender fixes, not yetverifiedresolutions. OldPDFs/PNGs remainunchangedforreviewercompletion. Their oldexportreceipt cannot validate the changedreader/CSS and must fail currentinputchecks until re-export. No newauthoringmarker is needed for thisrevision of the same two-output operation.

Legacytext-regression afterthehelperrefactor independently passes all1,652U001and2,303U002Tamil tokens in bothprofiles; nooldPDF was modified. Thischeck doesnotdetectgraphicarrowheads. Retain historicalhashes/evidence below rather than relabeling them as the nextcandidate.

## Content and layout boundary

`scripts/render_m81243_pdf.py` constructs print-only temporary variants from the exact checked56-file learning reader. Its reverse-signature check verifies that adding wide-layout classes changes no source/companion content. It adds a plainly marked paper-format note and printed page references; source numbers, diagrams, wording, original59solutions and29omissions remain intact. HTML/EPUB outputs are unchanged and `build_m81243_learning.py --check` passes: HTML`cfe15686bb3e3cd2a2f428c7b1e2529553ad85326eeb9ee992db16a8184db7c2`, EPUB`c9c944533946c3720b36d36435b41a21e8f90bc0c2ddc0efede2a7d2f0da4d16`.

The PDF skill's create marker was run once for this two-output operation before first authoring. Revisions belong to that same operation; no repeated marker was run. Existing approved pilot PDFs were not exported or altered.

`assets/m81243-pdf.css` uses A4portrait body pages and A3landscape wide-figure sequences. The two sizes have the same page height. Both profiles retain22widepages. Print body is11pt; the larger-text profile is13pt. Tall models are bounded to170mm and kept intact. Wide source figures remain vector content rather than screenshots. Three fifteen-place charts retain their original rotated labels and separate horizontal semantic alternatives.

## Current exact candidates

| Profile | Pages | Bytes | PDF SHA256 |
|---|---:|---:|---|
| print | 223:201A4+22A3 | 5,011,799 | `88138014731b35f801b716ea214254c23b2b2fa7bc107b64d1a64e7eeac24a8b` |
| screen | 260:238A4+22A3 | 5,218,449 | `5e896bbb7593072ee1f094342d6b066f79a5cdaecd96ecaf241c00417a75bf18` |

TemporaryHTML: print`01cbe88854ad18b042af6f143158e6b4e72284cc7d050bc960ac70a95ec88850`; screen`ce0cb8ad0a8f781112b8b270ba38c189b5ed53c2a48856428865da2f997b77f6`. Exact export inputs, current CSS/renderer identities and both destination maps are in `M81243-pdf-export.json`. Do not infer total pages from the last named destination: printcreditsstart220butend223; screencreditsstart257butend260.

## Actual defects found and fixed

The initial173-page print candidate`679422d965593ea3a682730af934423a005c8576627fafcb4659fd1138a66134` is superseded. Independent raster inspection found a clipped rounding instruction, the ones square of a561model severed onto the following page, a repeating semantic-table total after only blank rows, caption/table fragmentation and missing paper destination labels. The one was not deleted; it was misleadingly separated. These were actual layout faults, not text-extractor diagnoses.

The revised candidate overrides inherited SVG minimum widths, caps tall models and prevents diagram fragmentation, keeps semantic alternatives together, stops repeating tablefooters and includes containing captions in the wide sequence. Printed references are generated from real namedPDFdestinations. Fixed-width labels are rendered in successive passes; export succeeds only when the entire destination map stabilizes. Both current profiles stabilized on pass2. Every one of626non-skip internal links has an authored page label, and its destination/number agrees with the actual284-entryPDFmap. Paper references supplement rather than remove clickable links.

The independent print reviewer visually rechecked the complete model on152, full rounding instruction on138, all45rotatedchartlabels on101/104/147, allthree15-rowalternatives and the6-row/18-blank confidencealternative. Full-page overview/detail review continues; low-priority orphan headings/short continuation pages are being assessed. Screen layout is independently under review. Profile-specific reports own the exact viewed-page coverage; no initialcandidateview counts toward a changedcandidate's approval.

## Automated ink and navigation checks

`scripts/qa_m81243_pdf.py` binds checks to exactPDF/HTML/exportinput hashes and rejects changed inputs. Both current profiles pass at the identities above. All21,116authored visibleTamil tokens are accounted for; extra21,146print/21,145screen totals are repeated tableheader words. SVGtitle/desc and genuinely hidden screen-reader hints are not treated as visible ink.

Poppler's default geometric extraction reverses the grapheme order of the45verticalchartlabels. The verifier allows only the declared three15-labelSVGsequences: raw extraction must preserve every complete authored label sequence, and exact reversed-label occurrences must match before logical normalization. The PDFs are not modified to repair an extractor. The independent reviewer also visually confirmed all45labels. Horizontal semantic alternatives remain normal searchable text.

The independent reviewer demonstrated that a Tamil-only token checker could miss all deleted ASCII digits. The strengthened gate therefore also checks the complete visible ASCII-digit, arithmetic-sign, currency, percentage, comma and decimal-point inventories. It explicitly accounts for generated ordered-list markers and each physicalpagefooter. One repeated numericheader in the larger-text profile is allowed only because its entire exact header phrase repeats. All626renderedpage-reference fields are recovered in rawPDFcontent order and match the authored reference-number inventory; default geometric extraction sometimes collects right-aligned numbers as a separate column.

PDFlink closure validates named/direct destinations and GoTo actions. The reviewer demonstrated an uncheckedGoToaction in an in-memory mutation; this gap is fixed. Four executable negative fixtures now reject allASCII-digit removal, a changedroundingdigit, a groupingcomma changed to a decimalpoint, and a nonexistentGoTodestination. These checks prove inventories and closure, not arbitrary mathematical reading order or numeral placement. Fullvisualreview remains necessary.

Both PDFs declare `ta-Taml-IN`, tags and marked content. Print has19,788ActualText spans/27,794BDCmarkers; screen19,786/27,842. The pypdf diagnostic still reports6,781/6,784NULs because it misses contextualTamilActualText. NoNULor replacementcharacter appears in the ActualText-aware logical extraction. Do not stripNULs or replace the productionfont on the basis of that known diagnostic limitation.

Per-character physicalpagebounds report zero out-of-page boxes. The geometry parser emits102print/106screen missingFontBBox warnings, retained explicitly in the receipt; fallback glyph geometry is not certification of fontmetrics, nestedclipping or reading order. Rasterinspection is the independent check for those visible problems.

## Rasters, receipts and remaining release work

Print's223PNGs/56contacts are under `tmp/pdfs/ta-m81243/print-pages`; screen's260PNGs/65contacts under the matching `screen-pages`. Screenraster hashes are in the current automatedreceipt. Print's first allpage-raster run completed allPNG/contact outputs but its final receipt guard rejected a concurrent addition of the screenprofile to the exportJSON. The actualprintPDF/HTML/inputs did not change. Root reran print text/geometry checks against the final dual-profile export successfully, without overwriting the printreviewer's rasters. The independent print report records/checks those raster identities. No failed run is presented as a passing durable receipt.

`M81243-pdf-receipt.json` now contains both passing automatedprofile records. Its status intentionally says visualreviewseparate. Complete both profile reviews, address any meaning-changing layout fault, rerun hash-bound checks after any exportchange and record the finalallpagecoverage before delivering either modulePDF. Existing links to separate local license files are inherited from the reading edition; do not claim that these optional filelinks will work after moving a lonePDF away from its workspace. Sourceattribution/notices remain printed; standalonepackaging behavior is part of finalrelease review.
