# Pilot review receipt — 2026-08-30

Result: buildable review draft; not human/native-speaker approved.

- Five assigned Indonesian repositories and five canonical sources acquired. Nine Git checkouts and five source archives precisely locked; every archive passed complete CRC and SHA-256 checks. A20 canonical SHA-256 is observed; other archive hashes matched published evidence. B40 materialization counted physically, not inferred from clean status.
- XML parses; 44 unique IDs, ten selected source locators and 31 local links validated. No source-link element appears inside the selected canonical blocks. Original notices/metadata hashes verified.
- Eight source worked examples and two definitions translated/adapted. Six diagnostics and six practice questions have complete worked answers. No complete source module claimed.
- Twenty-three displayed mathematical chains checked against independently computed arithmetic and regression expectations. Expressions additionally checked on integers −20 through 20, not described as formal proof. All 61 source equation/working images read on nine QA contact sheets and compared with the Marathi working.
- Six automated tests pass: deterministic offline double-build with no downloads directory; rejection of wrong answer, broken link, wrong locale, source-locator drift and provenance-byte drift.
- Isolated Edge 152.0.4191.53 render: 1100px/420px widths, no horizontal document overflow, no page errors, question→answer→question navigation passes. Twelve section screenshots generated. Actual inspection covered desktop goals/fractions/equations/functions/answers/credits and phone fractions/functions/answers; remaining phone screenshots are automated evidence, not claimed manually inspected. Latest changed fraction wording passed desktop and phone reinspection after rebuilding.
- Marathi PDF canon OCR read; six source pages visually inspected; consultation/revision recorded. Domain/codomain and nonzero vocabulary revised with evidence. OCR formula errors were not used as mathematical authority.
- Original source steps include image/table layouts. Marathi re-expresses working as text and preserves mathematical meaning, not every display row. Source image hashes remain reviewable; no original binaries redistributed in the pilot.
- No PDF reader built. Deliverable is offline HTML; fonts may differ on other systems. Full upstream builds, external runtime exercises, native-speaker review and field testing not performed.

Reproduce: `python mr-Deva-IN/tools/build.py` and `python mr-Deva-IN/tools/test_build.py`. Source-image inspection needs Pillow; isolated HTML rendering needs Playwright and a browser executable. Core build/tests need only Python standard library.
