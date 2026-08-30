# Independent final PDF audit - authoritative v4

## Outcome

**PASS.** This report supersedes every earlier `FINAL_PDF_AUDIT.md` and
`FINAL_PDF_AUDIT.json` result. The only authoritative PDF audited here is:

`01_methodology/research_department/ai_compute_educational_access_20260825/staging/document_final_render_v4/PAPER.pdf`

- bytes: **2,089,824**
- SHA-256: **`74F2BC8AD9CBC2B7BFB9CFAF95D6162F38BBE35306B7909CA73A741E2565193B`**
- PDF version: **1.7**
- expected/actual pages: **87 / 87**
- strict parser result: **PASS**

## Structure, security, and active content

The PDF is unencrypted, tagged, and has a structure tree and trailer ID. It has
no AcroForm, canonical fields, widgets, annotations, OpenAction, catalog or
page additional actions, JavaScript name tree, embedded-file name tree,
associated files, XFA, or pages without content streams. It is not
linearized/optimized. Because it has zero annotations, printed URLs are not
interactive link annotations.

All six enumerated font subsets are embedded and have Unicode maps. `pdfinfo`
reports no suspects, no form, no JavaScript, 87 pages, and no encryption;
`pdffonts` independently reports all six font rows as embedded, subsetted, and
Unicode-mapped.

## Metadata

The Info dictionary and XMP agree on the principal identity:

- title: *Allocating AI Translation Compute for Marginal Educational Access*;
- author/model: **OpenAI Codex gpt-5.6-sol, Ultra**;
- subject: *A global language, interlanguage, accessibility, and
  open-curriculum portfolio model*;
- producer: LibreOffice 26.2.4.2 (X86_64);
- creation time: 2026-08-25 22:35:50 +02:00.

No personal-name metadata was detected.

## Page geometry and complete render review

Every page has an explicit MediaBox, zero rotation, and UserUnit 1. Crop,
bleed, trim, and art boxes are absent and therefore default to the MediaBox.

- 37 US Letter portrait pages (`612 x 792 pt`): PDF pages 1-13, 28-31,
  and 68-87;
- 50 US Letter landscape pages (`792 x 612 pt`): PDF pages 14-27 and
  32-67.

The v4 render directory contains exactly 87 sequential, decodable RGB PNGs,
with no missing, extra, duplicate, or raster-blank page. Portrait renders are
1547 x 2002 px and landscape renders are 2002 x 1547 px.

All 87 rendered pages were visually reviewed through ten contact sheets. The
repaired mathematics on PDF pages 4, 5, and 11 and the Appendix H transition
on PDF pages 64-65 were additionally reviewed at full resolution. No visible
clipping, overlap, broken glyph, row collision, truncated table content,
missing repeated header, page-bottom collision, or literal markup delimiter
was detected.

## Literal inline-mathematics delimiter gate

**PASS.** pypdf, pdfplumber, and pdftotext each return zero backslash-plus-
parenthesis delimiters, zero backslash-plus-bracket delimiters, zero double-
dollar delimiters, zero begin/end environment markers, and zero common TeX
control sequences. The generated DOCX text has the same zero counts.

The 15 single dollar signs in the PDF are legitimate currency markers: three
API-price values on PDF page 12 and 12 API-equivalent USD values in the table
on PDF page 24. None functions as a mathematics delimiter.

At full resolution, PDF page 4 shows italic `c`, `i`, and `k` in prose and a
centered formula with proper subscripts; PDF page 5 shows the variables `N`,
`D`, `C`, `P`, `U`, and `R` as typographic mathematics in prose; and PDF page
11 shows italic `D=1` and `C=1`. None is surrounded by literal markup.

## Critical Appendix H gate

**PASS.** The complete `IL-ISV` row is contained on PDF page 64 (printed page
63), including the final double-count text ending in "both Latin and Cyrillic
projection cells." The row begins below one repeated header and ends above the
page footer without clipping or collision. PDF page 65 begins with a fresh
header and the `IL-MANDING` row; it contains no continuation fragment from
`IL-ISV`.

## Text extraction and source identity

Three independent extraction paths passed:

| Extractor | Pages | Normalized characters | Empty pages | Replacement/NUL characters |
|---|---:|---:|---:|---:|
| pypdf | 87 | 184,183 | 0 | 0 / 0 |
| pdfplumber | 87 | 184,189 | 0 | 0 / 0 |
| pdftotext | 87 | 183,392 | 0 | 0 / 0 |

The shortest extracted page still contains 351 normalized characters. The
title, subtitle, date, exact model identity, population/authority counts,
eligibility count, and principal compute figures are extractable and match the
current Markdown and DOCX sources. All ten selected identifiers match across
Markdown, DOCX, pypdf, and pdfplumber after Unicode/punctuation-insensitive
canonicalization.

One benign extraction distinction remains: the visually correct `natural-`
line ending followed by `language/profile` on PDF page 2 is returned without
the hyphen by the text extractors. Canonical comparison matches the DOCX and
Markdown.

No TODO, TBD, PLACEHOLDER, internal file-citation token, tool-reference token,
double-brace token, or double-bracket token was found.

Current source identities used only for this mechanical cross-check:

- `PAPER.docx`: 415,615 bytes; SHA-256
  `A71BA85FA16A4A80C8B7015115DE3EA235357D92EC514B5112DDFBC04E133C39`;
  OOXML ZIP integrity passes and core title/subject/model metadata matches the
  PDF;
- `PAPER.md`: 186,340 bytes; SHA-256
  `FFBF91F3B19E3DF1966E71608DCF96356FF467E7F6C4D545ED3F16F41CF59749`.

The DOCX application-statistics cache remains stale (`Pages=1`, `Words=0`,
`Characters=0`) and is not used as the exported page-count authority. pypdf,
pdfplumber, and pdfinfo independently report the v4 PDF's 87-page count.

No final manuscript, DOCX, PDF, render, or central table was modified by this
audit.
