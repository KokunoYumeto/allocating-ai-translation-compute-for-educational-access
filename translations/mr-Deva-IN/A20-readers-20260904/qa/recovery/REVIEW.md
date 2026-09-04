# Marathi A20:m81374 PDF recovery

Result: PASS for the bounded readable PDF and checks below. Date: 2026-09-04.

## Coverage

The final PDF is 178 A4 pages: 164 pages of source-ordered learning material,
one credits/status page, and 13 pages of preserved XML identity index. This
is the complete recovered m81374 module, including its chapter-review and
practice-test material, not the complete Intermediate Algebra book.

The unchanged source XML is 588,465 bytes, SHA-256
`c629adb12dd6381b9d219d783f4af055aa1a8c060a9b36dce3bfcb5a39c1172d`.
All 954 assembly input pins were verified and the archive-free assembly
reproduced exactly. Retained: 380 source selections, 1,366 canonical IDs plus
five assembly IDs, 481 source MathML trees represented by 685 checked target
math strings, 255 exercises, 141 source-supplied solutions, 114 explicitly
unanswered questions, 149 source images, all Marathi image descriptions,
nine tables, and nine blank learner-rating cells. No answer was invented or
reclassified. Original images still contain some English labels; Marathi
descriptions and explanation tables remain beside them.

## Recovered defects and changes

1. The recovered builder kept circled subpart labels with the next figure,
   but not plain `(a)` and `(b)` labels. The latter could remain alone at a
   page bottom. Both forms now stay with the next graph/calculation.
2. ReportLab 4.4.9 shapes a space-delimited word in its first font and then
   maps later glyph IDs through each fragment's font. In the recovered
   builder, punctuation outside a math-font closing tag became an unrelated
   glyph. High-resolution inspection exposed this in the final question's
   domain/range answer. The reader now carries adjacent punctuation inside
   the preceding font/style run. The regression audit changed from 87
   mixed-font shaping words to zero, without altering logical text.
3. The render-only closing paragraph no longer falsely says no PDF was
   produced or viewed. It describes the current reading copy, preserves
   scope and accessibility limitations, and credits PDF recovery to
   OpenAI Codex gpt-5.6-sol, Ultra, on the user's instructions. Original
   source/author/human-contributor credits remain unchanged. Both header and
   closing-status transforms are recorded; reversing them recovers the
   unchanged XML structure exactly. The exact original XML is attached.

No shared helper, intake, glossary, canon, translation, mathematical source,
figure byte, source-error note, answer or stable identifier was edited.

## Checks actually performed

- Two fresh-process builds produce identical final PDF and build-receipt
  bytes. The final PDF SHA-256 is
  `71cb67cadf6e4e13f8cf12b8d51e2b601fbbea23759ec87918a971a5cf91f411`;
  size 13,814,663 bytes.
- Independent recovered primary-source suite: 20/20 tests pass, including
  negative tests for source math, answer roles, ID ancestry, assets and pins.
- Every page has logical ActualText, embedded fonts and Unicode maps. All
  1,371 named destinations, 149 image placements and 298 links survive.
- All 685 mathematical strings, 1,622 complete leaf-text surfaces and 149
  image alternatives are present in PDF ActualText. The complete source XML
  attachment is byte-identical. This does not claim universal extractor
  behavior or tagged-PDF/PDF-UA compliance.
- All 178 pages were rendered by Poppler; the 12 contact sheets were checked
  across the revision sequence. Every final page was checked for off-page
  text/images and empty body text; zero failures. No bare subpart label ends
  a final page.
- Detailed visual samples: pages 1, 4, 39, 50, 81, 120, 149, 164, 165, 178.
  These cover Devanagari shaping, title and footer, three/four-column tables,
  graph/caption grouping, wave-function mathematics, shading, supplied and
  omitted answers, corrected punctuation, closing credits and identity index.
  The repaired p164 answer was additionally inspected at 240 dpi.

The recovered historical PDF has 176 pages, but its receipt names a builder
hash different from the recovered builder file. It is therefore not a byte
replay oracle for this recovered builder. An unchanged recovered-builder
run yielded 177 pages; the graph-label fix yields the final 178 pages. No
missing source content is inferred from these historical layout differences.

## Reproduction and integration

Use the complete m81374 source closure already retained by the owner. Copy
the modified `tools/build_m81374_pdf.py` into that closure's tools directory.
Keep its pinned `tools/build_pdf.py`, `tools/build_unit.py`,
`tools/assemble_m81374.py`, `tools/test_m81374_primary_source.py`, assembly
receipt, translation and the 954 receipt-listed inputs intact.

Install the exact Python requirements in `requirements-pdf.txt`. The pinned
Windows fonts are not redistributed. Their system filenames, face indices
and hashes are in `BUILD_RECEIPT_PUBLIC.json` and `DEPENDENCIES.json`.
From the language/source root run:

```text
python -B tools/build_m81374_pdf.py
python -B tools/audit_symbol_runs.py
python -B tools/verify_m81374_replay.py
```

The replay script also requires Poppler `pdftoppm` on PATH. TeX was not used.
Public integration should use `BUILD_RECEIPT_PUBLIC.json`, not the local
build receipt containing the runtime's machine-specific shaping-library path.
The current license remains CC BY-NC-SA 4.0 with the preserved component
notices. Publication and broader HTML/source integration are the owner's lane.

Remaining scope: native-language quality and universal accessibility are not
certified. The next A20 anchor is m81375; no additional module was translated
in this helper assignment. No full-book or wider-language completion is claimed.
