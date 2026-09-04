# U002 builder and offline QA checkpoint

Date: 2026-08-30. Scope: A00 `m81243#fs-id2340048`, draft version 0.1.0.
This checkpoint is not completion of the full Tamil numeracy-recovery product.

## Review changes and rationale

- The main task's independent content review found that “the rightmost digit is
  ones” needed a notation qualification, because a whole-number value can also
  be written as `2.0` or `4/2`. Companion R1 now explicitly limits this instruction
  to whole numbers written without decimal points or fraction notation. The
  reviewed sentence begins “இந்த அலகில், முழு எண்களைத் தசமப்புள்ளியோ பின்னக்
  குறியீடோ இல்லாமல் எழுதுகிறோம்.” The source-faithful CNXML was not changed by
  this companion clarification. `qa_u002.py` guards the qualification and the
  current question/answer fixtures.
- The main task reported that SVG labels became too small when the complete
  diagrams shrank to phone width. Each of the nine existing SVGs is now inside
  its own labeled, focusable horizontal-overflow region, with a visible Tamil
  scrolling hint. Screen SVGs have a minimum width of 34rem; the minimum and
  overflow are removed for print. Exact Tamil text alternatives remain outside
  the scrolling region. SVG geometry/assets were not edited for this fix.
- Actual figure numbers come from the full module's numbered-figure order,
  excluding `class="unnumbered"`: filenames ending 002, 004 and 005 correspond
  to figures 1.2, 1.3 and 1.4. Filename suffixes are not figure numbering.
- The two five-column source tables remain semantic tables. Each has five
  column headers and three place-value row headers, explicit `headers`
  associations, a labeled focusable overflow region and a visible scrolling
  hint. No table is replaced with an image.
- `screen.html` contains the same content as `index.html`, with only the
  `screen-profile` body class added. EPUB continues to package the ordinary
  reflowable book, not PDF page furniture.
- The actual companion has 13 sections. The source is inserted immediately
  before `ta2-source-help`; section order is read from that file rather than
  assumed from a fixed count.

## Executed checks

- Source: 310 elements, 43 source IDs, 51 MathML expressions, three source
  exercises with solutions, two tables and nine SVG media items preserved.
- Companion: 16 questions and 16 one-to-one answers; four each for diagnostic,
  practice, mastery and retry. All 16 answer/reasoning regression fixtures and
  corresponding remediation links pass. All 45 companion IDs are unique and
  use `ta2-`.
- Arithmetic: six MathML sums and all 15 detected additive equalities were
  independently evaluated. Numerical question fixtures also detect changed
  questions whose answers have not been updated.
- Rendered reader: 145 unique IDs and 84 resolved fragment references; all 13
  companion sections match their authored trees. All source MathML, figure
  numbers, source descriptions and SVG geometry match. Nine focusable diagram
  regions, ten table column headers and six row headers are present.
- Both HTML profiles and the EPUB have local CSS/font resource closure, with
  no remote runtime dependencies. EPUB embeds the Tamil font and its license,
  the source license, source credits, MathML/SVG and navigation. ZIP CRC and
  manifest/spine/resource checks pass.
- Repeated builds: all nine files, including `screen.html` and the manifest,
  are byte-identical between `reader-u002/` and `build/ta-u002-repeat/`. The
  manifests agree, and all 20 declared input hashes match current files.
- EPUBCheck 5.3.0: zero fatal errors, errors, warnings or usage errors. Its JSON
  report covers all ten ZIP entries, and the reported entry checksums were
  compared with the current archive. The installed reporter emits unpadded
  hexadecimal bytes for some checksums; QA accommodates that observed encoding
  while recording ordinary 64-digit SHA-256 hashes independently.
- In-memory negative checks rejected an incorrect answer, a missing answer,
  a duplicate companion ID, an incorrect MathML sum and a broken rendered link.
  Earlier renderer checks rejected unknown CNXML tags and unsupported table
  spans. No mutation-test files were created.

## Original checkpoint identities - superseded by final layout revision below

| File | SHA-256 |
|---|---|
| `translation/m81243-fs-id2340048.cnxml` | `fbcfba620c006ba97bb90f15ee6e598ae65953bc7d29a0959b6d80c48e8e7caa` |
| `translation/recovery-u002.xhtml` | `b61edfe7fe1084267b322ae7d9c5bc10694f069e0557cf2f9906fe7b552da463` |
| `scripts/build_u002.py` | `7667dadd806d343413dbe0b9271324d834df841b40a48e242032150ccfc90da5` |
| `scripts/qa_u002.py` | `624d64a473cdbeefb7990168237c05fdb1eabf7e18184c0cc9587c096cff9e1c` |
| `assets/u002.css` | `3a00d2f8d967a32806864e56dac2c443ae0d7e53ae70eaf44e028fb0200aa46b` |
| `reader-u002/index.html` | `5231f5c9b793e0aabce9c69636d77d7ad83045cf2ffecc5e8496c989f602e9f5` |
| `reader-u002/screen.html` | `663465f67e4946a3c80de5cb351acb34caf88b8d3738d2807350a9f05c1ea5b5` |
| `reader-u002/ta-Taml-IN-A00-U002.epub` | `de5d9b5738e0c454f40eeb191711487118ff0347b3a144c944a595ccda89b294` |
| `reader-u002/build-manifest.json` | `6d5147998bdcf8dbc949453899107894b6ddd7574a311d25c109d4913cd4046b` |
| `qa/U002-epubcheck.json` | `ecfc1ee019fbe8193e62f64775e13b45e33d7a31d305a5888ef9e550f458ca80` |
| `qa/U002-structural-receipt.json` | `b7af9b0c9077d7c124e3822547fca0aaa36f241d3cac60297d1baa28713bf283` |

## Reproduce from the project root

```powershell
python -B -X utf8 ta-Taml-IN/scripts/build_u002.py
python -B -X utf8 ta-Taml-IN/scripts/build_u002.py --out build/ta-u002-repeat
java -jar downloads/qa-tools/epubcheck-5.3.0/epubcheck.jar ta-Taml-IN/reader-u002/ta-Taml-IN-A00-U002.epub -j ta-Taml-IN/qa/U002-epubcheck.json
python -B -X utf8 ta-Taml-IN/scripts/qa_u002.py
```

Do not run the verifier with Python `-O`: it refuses optimized execution because
its assertions must remain active. Builds and receipt writes stop below 100 MiB
free space. Approximately 6.64 GB was free during this checkpoint.

## Evidence limits

Answer fixtures protect already-reviewed content; they are not proof of
native-speaker approval, pedagogical efficacy or validated placement. Tamil
educator/native-speaker review and assistive-technology user testing remain
open. PDF export/rendering, PDF/UA and browser visual evidence belong to the
main task's separate checks, not this verifier.

The main task reported successful phone containment and legible independently
scrolling diagram panels, but synthetic ArrowRight/End tests did not change
`scrollLeft`. Accordingly, this checkpoint claims focusable, labeled overflow
regions, not verified keyboard panning. Read-only CSS inspection found no
scroll-blocking screen rule or event handler: overflow is `auto`, focus adds
only outlines, and the generated reader has no JavaScript. The cause of the
synthetic-key result is not established here.

No shared U001 builder, stylesheet or learner files were modified by this
bounded U002 builder/QA work. No commits, downloads, browser actions or PDF
exports were performed by this subtask.

## Final layout revision - 2026-08-31

The parent applied print-only keep-together/short-link rules and screen-profile spacing revisions after all-page review. No source, companion, SVGgeometry or ordinary screen HTML styling changed. Final inputs/outputs were rebuilt twice and `qa_u002.py` passed after a fresh zero-error/warning EPUBCheck report. Earlier stale repeat/report failures were expected and were not accepted as a pass.

| Final artifact | SHA-256 |
|---|---|
| assets/u002.css | `f67f3ab4a4c142573f20d52b6365b7f13e5246932dbe29dcef9a50efa889fdc3` |
| reader-u002/index.html | `5231f5c9b793e0aabce9c69636d77d7ad83045cf2ffecc5e8496c989f602e9f5` |
| reader-u002/ta-Taml-IN-A00-U002.epub | `ba0015bcfe79f13a58f63b70ac1c1a18defb3ab1b6da1867ba2e5d337c591134` |
| reader-u002/build-manifest.json | `148d8ca13a7ede3716d2c1b11dc6abc4fe6cc22c3274c5c14879421f4baf4c06` |
| qa/U002-epubcheck.json | `0bb43da403991f4d119447816532e3638716f71ea0e7514da2efaca78a2478a2` |
| qa/U002-structural-receipt.json | `ad785bb307fcc3fc185bf74303d4591cb92d00e0091cd7d8f1287a1533fb6170` |

Both final PDFs have24pages; exactPDFhashes and final all-page review are recorded in `U002-VISUAL_REVIEW.md`. Their logical Tamil passes Poppler /ActualText-aware extraction, including exact2,303-token coverage. Production fonts are unchanged; the separate investigation retracts the earlier broad font-corruption diagnosis.

Generated QA JSON receipts now have Git `-text` attributes, like products/witnesses, so recorded byte hashes survive checkout. Verbatim source-license whitespace and line endings are preserved, not stripped to satisfy a generic whitespace checker.
