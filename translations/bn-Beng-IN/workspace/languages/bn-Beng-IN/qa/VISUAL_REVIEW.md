# U01 visual review

Reviewed locally on 2026-08-30 using isolated headless Microsoft Edge. The in-app browser runtime failed before connection; fallback never attached to user browser sessions and blocked external requests. See browser-check.json for exact input hashes and machine measurements.

Inspected all desktop content in seven overlapping companion tiles and five source-faithful tiles (1200 × 1000 viewport), plus the top and bottom of both readers at 390 × 1000. Narrow-width checks also measured all page content for overflow. After the final alt-color correction, re-inspected affected source tiles 2 and 4 and the narrow source footer/solution tile. Companion output did not change during that correction.

Verified Bengali glyph shaping, line spacing, section/solution hierarchy, readable fraction notation, all five images, visible image descriptions, answer-key layout, wrapped long identifiers, and attribution/footer legibility. No horizontal overflow, unloaded image, zero-sized MathML, page JavaScript error, overlap or missing-glyph box observed. The first and last screenshot rows may cut text at the viewport edge because these are scrolling screenshots, not paginated documents.

Final reviewed SHA-256:

- U01-companion.html: `2202f8bcfb0044dc6d5e1e8291d189bcd491acde8e69e322ec5ffc8b30433c22`
- U01-source-faithful.html: `959c8999a283e2d9eac6f0f894fd21628b998cf20c4396aba04099c9825a3822`

The original formula artwork retains an embedded English “so”; its Bengali description supplies the meaning. Highlights described as red in original alt text are cyan in the actual images, so Bengali descriptions now say a distinct color. Original pixels are unchanged.

Limits: not a screen-reader test, human Bengali/teacher review, learner validation, PDF print-layout review or all-browser certification. Screenshots are reproducible scratch artifacts under ignored tmp/bn-Beng-IN-visual; they are not required to rebuild the reader.
