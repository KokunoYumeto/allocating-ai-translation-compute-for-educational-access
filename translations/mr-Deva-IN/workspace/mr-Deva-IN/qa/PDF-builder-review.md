# Direct-XML PDF reading-copy review

Reviewed 2026-08-31 by the source_review worker. Status: PASS for the bounded PDF reading-copy checks described here. Parent integration remains separate. This is not a claim that the five-book assignment is complete.

## Boundary and method

The PDF skill was read completely. Its marker succeeded exactly once with `create`, expected output count `3`, format `pdf`, immediately before the first builder-authoring patch. Root did not invoke the marker. The only dependency installation was the 1.4 MB uharfbuzz 0.56.0 binary wheel, using `--no-cache-dir --only-binary=:all: --target mr-Deva-IN/tmp/pdfs/python-deps`. No global Python environment or shared translation/config was changed.

`tools/build_pdf.py` reads the three structured XML translations, their authored JSON configurations, provenance locks, and pinned source assets. It reuses read-only validation functions from `tools/build_unit.py`; it never calls that module's HTML build function. It does not read an HTML file or CSS, open a browser, start an HTTP server, use CDP, or obtain HTML geometry. The in-app browser policy block on the HTML reader remains unresolved. These PDFs are separately authored documents, not HTML conversions and not HTML QA evidence.

The builder uses ReportLab 4.4.9, Python 3.12.13, uharfbuzz 0.56.0, pypdf 6.14.2, and Windows Nirmala UI collection faces 0/1 (regular/bold). Cambria face 0 supplies only the missing white-square checkbox glyph. Both font collections have OS/2 fsType 8; restricted-license, no-subsetting, and bitmap-only flags are rejected. Font collections remain local rebuild dependencies, not committed standalone font assets. All PDF-used font subsets have FontFile2 streams and ToUnicode maps. Source and font hashes are in each PDF receipt.

ReportLab's HarfBuzz face constructor otherwise defaults to TTC face 0; the local subclass explicitly uses each selected collection index. Tests verify the selected index, nonzero shaped glyphs, and actual conjunct shaping differing from nominal Unicode glyph lookup. All Marathi/source mathematical codepoints were checked in regular and bold fonts. No fontTools dependency was required.

The output is PDF 1.7. Exact input XML bytes are attached to each PDF, every XML ID is a named PDF destination and appears in a printed identity index, and HTTPS/internal question-answer links are preserved. Paragraph ActualText carries logical Unicode because shaped glyph subsets can otherwise expose private-use/reordered text in extraction. This is not a tagged PDF/UA document and universal reader extraction is not asserted. The invariant PDF metadata date is intentionally 2000-01-01 for reproducibility; it is not the actual production/review date.

Original mathematical minus signs and source punctuation are preserved. New wrapper prose uses ASCII hyphens. The source's blank self-check is printed, not filled or converted into a submitted form. No AcroForm, widget, JavaScript, or launch action is present.

## Final outputs and checks

| Unit | Pages | Source blocks | Math checks | XML IDs | Pinned witnesses | Canonical rasters | Source links: internal / HTTPS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MR-BRIDGE-006 | 12 | 31 | 107 | 138 | 71 | 0 | 57 / 4 |
| MR-BRIDGE-007 | 5 | 9 | 6 | 33 | 28 | 1 | 12 / 3 |
| MR-BRIDGE-008 | 12 | 21 | 35 | 107 | 57 | 6 | 27 / 7 |

Final PDF SHA-256:

- 006: `68e5dd2cfde2629dca7b9177cdd5bd9e2a4986ab21ab63480ea00d61a9121729` (157411 bytes).
- 007: `122c4e96ac42d724ec1dd6eecdefbed1fa33416096cd9251354f207296bedf41` (202777 bytes).
- 008: `db6620fa37a3c5748db3612aff34ca6c6901e118ee4f7a2a06e6f782520e3551` (675383 bytes).

Builder SHA-256: `c54d8571feb262fcce90d37dbe9d02fcdf9b39246fbed739ce9992f1185afc90`.
Test SHA-256: `09cd31d9ddb4251e71a46db0d67d4e00bcc7b62b8186fc9f76e53ea5b69a7993`.
Input XML SHA-256 values:

- 006: `5538a28327ac72086ab4ab4d4054fe892ff78fb5a8864f1ada67871b93bc5fd0`.
- 007: `44593e8d688ad459ed2e72b1eac1293974cd3203661ff5df3b220d0815419e06`.
- 008: `418afc11f3b4c9c54176e4ddb0bab257ecc245101cc593b7904560c5d7eb4f66`.

All 16 focused tests in `tools/test_build_pdf.py` passed after the final PDF-header correction, with zero skips. Tests independently check every source leaf and mathematical text in serialized ActualText, exact XML attachment bytes, all IDs, exact outgoing URLs and valid internal destinations, seven byte-identical embedded JPEG streams, nine empty rating cells, real shaping, font embedding/coverage, rejected overflow/unsafe paths/links, math and witness drift failures, source counts, both explicit 006 calculation breaks, and byte-identical repeated builds in this environment. These checks do not replace the separate mathematical/source translation review or page inspection.

## Visual inspection and retained evidence

Poppler 26.05.0 rendered all pages at 110 dpi using its native `pdftoppm.exe -r 110 -png` executable. Each of the 29 final-layout pages was opened individually through the permitted filesystem image viewer: 006 pages 1-12, 007 pages 1-5, and 008 pages 1-12. The initially observed orphaned headings/source labels and separated figure captions were fixed with small indivisible layout groups. Every final-layout page was then reread. No clipped content, missing glyph, collision, or unintentional filled rating was found. Larger answer groups may continue on the next page; headings retain their first substantive text and figure descriptions remain with their figure.

After this complete inspection of `final-v3`, pypdf's default 1.3 header was explicitly corrected to 1.7. All pages were freshly rendered into `final-v4`; every one of the 29 PNG byte sequences is identical to the corresponding inspected `final-v3` PNG. Thus the evidence below records the exact final output pixels, not an assumption that a header change is visually harmless. Earlier intermediate page sets are retained in ignored `tmp/pdfs/`, per the explicit parent instruction, and are not final review artifacts.

The evidence root is `mr-Deva-IN/tmp/pdfs/`. Paths below are relative to that root. All listed pages are retained locally and ignored by Git.

| Page file | SHA-256 |
| --- | --- |
| MR-BRIDGE-006/final-v4/page-01.png | aad065768a5c9f064f9814f71a0689c8f25302e1a1a078ec341295292f68ba51 |
| MR-BRIDGE-006/final-v4/page-02.png | 273aeac80c50d72273cbe4dd0257288cf436c8eeb14b6c68502d43b1b1413276 |
| MR-BRIDGE-006/final-v4/page-03.png | 44bdaf210b09104a39c5111984f755671553bd26746086719d800174f5f0d01e |
| MR-BRIDGE-006/final-v4/page-04.png | 3d14a937f28129bd699d81612077873b4f57b8a1b387736e6437e442d796b60e |
| MR-BRIDGE-006/final-v4/page-05.png | d7eb543c342946b4754d4893669e37b01fa70154c8a531266500a909a2d691bb |
| MR-BRIDGE-006/final-v4/page-06.png | 6ac88efbe5fb1322a9b15b8203795706f9391e7378bab30b87a724afd922cdb2 |
| MR-BRIDGE-006/final-v4/page-07.png | e07919bd7c45ee801613f03fef6c5a11d26a8d41b3e469097ec60397bf65672c |
| MR-BRIDGE-006/final-v4/page-08.png | 223d13d550715731d22e75ca6c9a42351f5205e36115d9f9faa942b079c68846 |
| MR-BRIDGE-006/final-v4/page-09.png | f9a9e64728fddd367edf73c34fffc3f749e66adeb2d55d347347116e001ca9a3 |
| MR-BRIDGE-006/final-v4/page-10.png | 146828d4be6476e206b010493461285c2cee279d84953d4750713973fe3785a6 |
| MR-BRIDGE-006/final-v4/page-11.png | f948763259c25704526c837822bee69aba163df7f0d5e65db0132de6f6805854 |
| MR-BRIDGE-006/final-v4/page-12.png | e686259443fbaa1facd738d8e4fd20a7c31f5a6605d54f3b04e461c538a59804 |
| MR-BRIDGE-007/final-v4/page-1.png | 4bf909138a7a7ef1adf3668d129c48f9b497dbbb132c1af967b7a865f1d07494 |
| MR-BRIDGE-007/final-v4/page-2.png | 644ccc87e4ded92f8b94d21cf05628abf32616c776786076ddf3aa1034f8ad30 |
| MR-BRIDGE-007/final-v4/page-3.png | 70b052be22263c9a62904ee854ad837cf266cdb628693d43681a3a7510947cd4 |
| MR-BRIDGE-007/final-v4/page-4.png | 836ad79c55c2b3fe16e8cbf83a71952f1ca23aa848ea5cfbb56ee4b4dc45ddc9 |
| MR-BRIDGE-007/final-v4/page-5.png | 98a725e8f897ff8dc4d250707f2023c3a34606eae5c783a8cc7348ed67e902e8 |
| MR-BRIDGE-008/final-v4/page-01.png | 6d3b81d8cd8b4601529095bad22d5888fccccf70e7d9b200d64547c7d50c25c2 |
| MR-BRIDGE-008/final-v4/page-02.png | 3a4e4a51f34769daff9f11915fd32ccadc60dc2494b8be7b231653262fbfac09 |
| MR-BRIDGE-008/final-v4/page-03.png | 9ec6618ca54b3b915f715bf61880ccf0052262f445b22e9dead6c835d1024429 |
| MR-BRIDGE-008/final-v4/page-04.png | 8b4333919d14a37ea0517dcde77db6e4c296e60db67dc2f580438032dd1abe84 |
| MR-BRIDGE-008/final-v4/page-05.png | a93c25efc4ab1e63f938105fdd658b61e16920cc0b89099f11e2a6dcff7a4b14 |
| MR-BRIDGE-008/final-v4/page-06.png | 361204103951d52777720903488903b75f78a72aaaf49d1360416b207508c173 |
| MR-BRIDGE-008/final-v4/page-07.png | adaa05e6feaead8a9cc06e172da14f3aa6ab301d974b2c4b96c2c8dbebf707e1 |
| MR-BRIDGE-008/final-v4/page-08.png | ec0009c1c3c59da6a2ed99ffad08fc20fb7a3d8220088c47d6af720758400216 |
| MR-BRIDGE-008/final-v4/page-09.png | 60e203415f279210c5b01e7ade5c6be82bf9a21693667935de0f5fb13e100dcb |
| MR-BRIDGE-008/final-v4/page-10.png | cb7441c8c17645618f5f99b86e4d20782a047292bebbac9469a5d8b97fccae4e |
| MR-BRIDGE-008/final-v4/page-11.png | 899c63eb591eb97d9858ae89c22902170e11e506c71b8abac84e1b9709bf2ed4 |
| MR-BRIDGE-008/final-v4/page-12.png | 8f376fdfe63074b34076c7a7038d1741e6bffdc850797fc866bec18c87ea800f |

Page-specific observations:

- 006 pages 1-8: all signed arithmetic, superscripts, absolute-value bars, fractions, source/new-answer labels, and question links are legible. Page 9 shows the complete q25 chain ending `=3250+1500=4750`; page 10 shows q26 ending `=7250+2500=9750`, with source correction and credits retained. Pages 11-12 contain the complete 138-ID index.
- 007 pages 1-2: four writing questions and explicitly new sample answers retain their source meaning and displayed formulas. Page 3 has the unchanged English raster, readable Marathi description/key, and exactly nine visibly empty squares. Page 4 retains remaining glossary and credits; page 5 has the full 33-ID index.
- 008 pages 1-3: readiness expressions, source answers, domain/range prose, definition, and the explicit reference to previously selected unit001 are legible. Pages 4-6 contain the three unchanged mapping rasters; Liz points to August 2, Khan spelling and Jose/Armando variant notes remain explicit. Pages 7-9 contain the three unchanged finite-point graphs, with visible signed axes and the bottom boundary point `(-3,-6)` preserved. No line was added between points. Page 10 contains credits; pages 11-12 contain all 107 IDs.

## Rebuild commands and limitations

From the workspace root, use the configured bundled Python executable (not an arbitrary system interpreter):

```powershell
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B mr-Deva-IN/tools/build_pdf.py MR-BRIDGE-006
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B mr-Deva-IN/tools/build_pdf.py MR-BRIDGE-007
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B mr-Deva-IN/tools/build_pdf.py MR-BRIDGE-008
& '[local-home]/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B mr-Deva-IN/tools/test_build_pdf.py
```

The builder is intentionally bounded to these three units and their currently used structured elements. It fails closed for unsupported units/markup, invalid pins, unsupported fonts/glyphs, and overwide or overheight indivisible content. It is not a general book-publishing engine. Building writes only each PDF and its separate PDF receipt, never HTML outputs or HTML receipts. Byte reproducibility was tested under the recorded local dependencies/fonts, not across arbitrary library versions or platforms. Every PDF receipt reports structural PASS while explicitly leaving visual review to this document; it does not silently convert a successful generation into a visual claim.

No PDF/UA, PDF/A, screen-reader certification, interactive self-check persistence, native Marathi mathematics-teacher approval, publication, or complete-module/book coverage is claimed. The browser's denied HTML inspection has not been bypassed or resolved.
