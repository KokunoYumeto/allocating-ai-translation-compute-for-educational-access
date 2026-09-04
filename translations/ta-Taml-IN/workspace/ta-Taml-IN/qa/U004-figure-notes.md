# U004 number-name figures — 2026-08-30

Status: three Tamil SVG drafts with source, numeric-group, punctuation, arrow and shaped-font metric checks completed. Integrated visual and accessibility QA remains pending. This bounded figure subtask changed only `assets/u004/*.svg` and this note; it made no build, download, cleanup, commit, CNXML edit or shared-log change.

## Evidence actually read and viewed

- Read the complete English subsection `m81243#fs-id1321580` from `provenance/m81243.en.cnxml`. Derived the exact source filenames from its three image references: `CNX_BMath_Figure_01_01_013_img.jpg`, `CNX_BMath_Figure_01_01_014_img.jpg`, `CNX_BMath_Figure_01_01_015_img.jpg`.
- Viewed all three actual JPEGs from the canonical `openstax/osbooks-prealgebra-bundle@38cae454e644abf9f0a623e876994553881597c9` extraction. JPEGs, rather than the similarly named PNGs, are the images referenced by this CNXML.
- Read the complete existing Indonesian SVGs named `<original JPEG filename>.id-ID.svg` in `downloads/openstax-prealgebra-2e-id-ID/media/`. Verified that repository's HEAD as `3de9207f56f8b5c57c017abf973fb04e00d740f1`. These supply useful prior-localization context, not permission to overwrite the actual English image evidence.
- Initially read existing OCR page 16; it concerns a GeoGebra activity and was not used as evidence for number-name spelling. Then read actual OCR pages 11 and 12 and viewed both page PNGs, following the source translator's focused reference check. SCERT 2018 PDF pages 11–12 / printed pages 5–6 show the separated tens/unit style in Tamil number names and explicit place-value grouping. Their Indian lakh/crore grouping was not transferred into this international source.
- Coordinated every Tamil number phrase and period heading with the U004 source translator. Read the resulting actual CNXML media alternatives and confirmed the paths, counts and names match these SVGs. Also read `fs-id2566318` and `fs-id3400199`: the final `s` rule is explicitly attributed to English, and the `and` rule explicitly to the source book's English number names. Neither rule is presented as Tamil grammar in these diagrams.

## Mathematical and linguistic decisions

| Figure | Source media ID | Groups preserved verbatim | Tamil name rows |
|---|---|---|---|
| 013 | `fs-id1227744` | `37`, `519`, `248` | முப்பத்து ஏழு மில்லியன்; ஐந்நூற்றுப் பத்தொன்பது ஆயிரம்; இருநூற்று நாற்பத்து எட்டு |
| 014 | `fs-id1209906` | `8`, `165`, `432`, `098`, `710` | எட்டு டிரில்லியன்; நூற்று அறுபத்து ஐந்து பில்லியன்; நானூற்று முப்பத்து இரண்டு மில்லியன்; தொண்ணூற்று எட்டு ஆயிரம்; எழுநூற்றுப் பத்து |
| 015 | `fs-id2670483` | `327`, `577`, `529` | None: the source image only labels the three groups. |

- International period headings remain மில்லியன்கள் / ஆயிரங்கள் / ஒன்றுகள், with டிரில்லியன்கள் / பில்லியன்கள் added in 014. No lakh/crore conversion was made. Within Tamil word-name rows, the source's group count and scale are kept explicit. These international-scale compounds remain provisional for idiomatic/native-speaker review; the canon does not attest every complete phrase.
- Figure 013 retains the red “periods” annotation omitted from its English alternative: the Tamil label is “இடமதிப்புத் தொகுதிகள்”, split across two lines for fit, with a **left-pointing** arrow toward the period labels. The Indonesian SVG reverses that annotation arrow; this redraw follows the actual canonical JPEG's direction.
- Figure 014 preserves `098` **twice**: once in the top number, once in its word-name mapping row. Its word name represents ninety-eight thousand, without inventing a spoken leading zero. The first four word-name rows retain trailing commas, and the last does not.
- Figure 015 has exactly three numeric groups, two commas, three braces and three period labels. No word-name arrows or worked answer text were added to that group-only source figure.
- The first two drawings preserve the original staggered number-to-word mapping rows. All source values remain visible as groups; a total or generic caption was not substituted for the mappings. Arrows and braces carry the relation independently of colour.
- Visible labels are Tamil translations, not English examples of `s` or `and` rules. The source strand carries the explicit English-only convention qualifications; the figure does not generalize them to Tamil.

## Structural and font checks

Read-only assertions passed for XML parsing, unique IDs across all three SVGs, root language/role, accessible label references, marker references, exact top group strings, exact repeated mapping group strings, comma positions, approved Tamil phrases, and rightward mapping-arrow coordinates. The 013 annotation arrow was separately checked as leftward. Group values reconstruct **37,519,248**, **8,165,432,098,710** and **327,577,529** using successive powers of 1000. The 014 `098` strings are retained exactly, not normalized to `98` in the drawing.

Each root has unique `u004-f013-` / `u004-f014-` / `u004-f015-` IDs, Tamil language tags, `role="img"`, and a full Tamil description of its group mappings. Visible graphics are hidden from duplicate accessibility traversal. The declared font family is `TamilBook, 'Nirmala UI', sans-serif`; no font or remote asset is embedded or downloaded by an SVG.

Using the actual bundled `assets/fonts/NotoSansTamil.ttf` with Pillow/RAQM, weight 400 and width axis 100, every text glyph box was measured at its declared size and anchor. All text lies inside the canvas with at least an 8-unit margin; period labels fit their separate group widths. Longest word-name label widths were 421px in 013 and 499px in 014. This verifies shaped-font geometry, **not** rendered-browser/PDF visual approval.

## Integration requirements and remaining gaps

Intrinsic sizes are 1000×334, 1280×474 and 620×116. Main word rows are 24 units and period labels 22. The first two are dense diagrams: provide a horizontally scrollable/zoomable view and corresponding semantic text in the renderer. A phone-width fit would shrink 014 word labels to about 7px and is not an acceptable stand-alone reading mode. Full descriptions provide image alternatives but do not demonstrate screen-reader usability or replace navigable semantic text.

The parent task still needs to inspect final Tamil shaping, rendered crop/overflow, arrows, narrow-screen interaction, print legibility, source linkage and accessibility behaviour. No native-speaker, educator, EPUB-reader or PDF/UA approval is claimed.

## SHA-256 witnesses

All file basenames below begin `CNX_BMath_Figure_01_01_`.

| File suffix | Bytes for authored SVG | SHA-256 |
|---|---:|---|
| canonical `013_img.jpg` | — | `b08d422c5b0a11996f29fec0c2dad98109f1a5087b971692f6c7100789515add` |
| canonical `014_img.jpg` | — | `6f998cb6236e65638688578b3f92197b492cb0294c23e7bab04be88ff8be42dc` |
| canonical `015_img.jpg` | — | `6f44e42d7c908e579b10a9371dab52bd0cec89b9b24d4ab041c55878b9015e96` |
| Indonesian `013_img.jpg.id-ID.svg` | — | `dc7daac5f2b4dfd2ac4caa2e0a4932a5c69b56243653a861c6899f95f3ba8410` |
| Indonesian `014_img.jpg.id-ID.svg` | — | `f7fffee2f8cdbb4eec2e547860a9df7f028e25c193ee44cf05db21b5c73ab64e` |
| Indonesian `015_img.jpg.id-ID.svg` | — | `5dc38a4522845a6b875b72a1076ffa36870cd8e313124f08a0d157bde09671df` |
| Tamil `013_img.svg` | 4,955 | `eaae3f9a9e54ade3497e32446f7cefa0ac8b38aec088a414fb2b571a93f77a3d` |
| Tamil `014_img.svg` | 6,545 | `f1b2107e28960b1bfa8aa4438dfc43b7cbee2345f47a4ec9594236b3d16d7828` |
| Tamil `015_img.svg` | 2,661 | `d564db95469bd8b9a8932a93f3119805b2a8cb12f0f81ea8323d2b8a3e7ffd54` |

Storage preflight reported 6,732,062,720 bytes free on C:. Existing material was read in place; only these small authored assets and this note were written.
