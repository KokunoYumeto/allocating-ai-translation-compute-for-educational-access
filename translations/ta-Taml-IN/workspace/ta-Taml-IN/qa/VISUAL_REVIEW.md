# U001 visual and browser review - 2026-08-30

Scope: this exact first-unit edition only. Review by the main AI assistant, not a native-speaker, learner or accessibility certification.

**2026-08-31 newly discovered figure erratum:** the historicalU001numberline lacks itsupperrightdirectionarrowhead, although the pinnedsourceJPEG has it. The oldall-pagevisualreview missed this graphicfidelitydefect. CurrentU001HTML/EPUB/PDFbytes remainunchanged and are not production-ready; their validlogicalTamiltextchecks do not testarrowgeometry. The asset is nowcorrected and visuallychecked in the rebuiltfull-modulereader, with separatepath/marker regressiontests. Thatnewreaderdoesnot retroactivelyrepair theseolderfiles. See `M81243-LEARNING-INTEGRATION.md` and `NEXT_UNIT.md` for corrected-reader evidence and the still-uncommitted PDF re-review lane.

2026-08-31 correction: the earlier broad PDF-corruption diagnosis was retracted after controlled probes and direct marked-text inspection. Poppler recovers all 1,652 authored Tamil tokens from each unchanged U001 PDF with no NUL or replacement character; pypdf's extraction misses contextual `/ActualText`. The hashes below still match the all-page visual review. No production font correction or U001 re-export was needed. The refreshed `pdf-receipt.json` records the tested extraction engine and limits; see `PDF-font-investigation.md`. Visual review alone does not certify search/copy or PDF/UA.

| Output | SHA-256 | Pages |
|---|---|---:|
| Print PDF | `c99922ff245c20fa1fdb7c13c9ddd599ad99ba172f09b7e5baec582367e3e35b` | 20 |
| Screen PDF | `52949bdd151d2d5ae929c427efdde690483705e57504f49f844f5b70056fd557` | 20 |

Latest Poppler rasters for all 20 pages of each PDF were inspected through the five four-page contact sheets per edition. The final screen revision was rerendered after tightening only its mastery-answer page spacing. No clipped text, overlapping content, missing-glyph boxes or broken diagrams were found. Page numbers and source-credit continuation are legible. The full diagnostic and mastery routes now remain on their answer pages rather than spilling a few lines onto an otherwise blank page. Deliberate open space in short practice sections is retained.

Specific checks included Tamil shapes and punctuation, the 0-6 number line and directional labels, stacked source fractions, all source solution lists, six countable mastery circles and three retry seeds, and the full source-contributor credits. Source mathematical punctuation is preserved even where it is more widely spaced than ordinary Tamil prose.

The final HTML was also checked in the in-app browser. At 1265 CSS pixels, the document scroll width equalled its client width. At a 390px viewport override (375px document client width), scroll width remained 375px; the mastery SVG was about 343px wide and all six objects were visibly distinct. Tamil fonts reported loaded; the DOM contained exactly three real SVG elements, six mastery circles and three retry ellipses. Temporary viewport overrides were reset. Earlier number-line and navigation checks also passed.

The browser caught an XML-only namespace-prefix error that made added diagrams display as text in HTML; this was fixed before these final checks. The standalone EPUB passes EPUBCheck 5.3.0 with zero errors/warnings, but has not been tested in a dedicated EPUB reading application. No PDF/UA or screen-reader-user claim is made. Automated PDF checks log some missing FontBBox warnings from pdfplumber; actual extracted glyph boxes stayed within page bounds, Tamil text extraction passed, and raster inspection found no corresponding visible defect.

Regenerate and re-review after any content, stylesheet or export change. Do not use this note for U002 or future editions, and do not substitute file existence for a matching hash.
