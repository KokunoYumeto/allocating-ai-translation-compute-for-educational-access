# A00 whole-number naming: asset checkpoint

2026-08-31. Prepared only the three source-bound diagrams for A00 / `m81243` /
`fs-id1321580`. This adds `scripts/prepare_name_whole_assets.py`,
`translation/a00-name-whole.assets.json`, nine SVGs under
`translation/assets/a00-name-whole/`, and this witness. No shared builder,
descriptor, source lock, translation ledger, narration rule, or other author's
DRAFT was edited. The parent independently owns subsequent integration.

This is a bounded asset handoff, not completion of the section workflow,
module, A00, A10, or AX-2. Human Javanese educator, integrated-reader layout,
screen-reader, pronunciation, and listening reviews remain pending. No audio
was synthesized. A limited static SVG rendering check is documented below;
it is not a general visual or native-language certification.

## Actual sources and boundary

Read the entire pinned Indonesian and English subsection, all 12 direct
children, 53 unique IDs, nine MathML expressions, the headerless explanatory
table, all three media alts/references, and the worked/practice answers.
Previous sibling: `fs-id1883656`; final included note: `fs-id1808812`;
next excluded sibling: `fs-id1339359`.

- Indonesian commit `3de9207f56f8b5c57c017abf973fb04e00d740f1`, module blob
  `90def09ee1dbfdc66aa8bc910938ad7684668e97`.
- English commit `38cae454e644abf9f0a623e876994553881597c9`, module blob
  `612244f80ecb6bce0f811c9d99204ae2f9f7a4f5`.
- Namespace-aware canonical section SHA-256: Indonesian
  `339b8559c18575e982cbafeadaa22c23e2c32c019458bdea46512f1f9b293f9f`;
  English `fa980c748e0d5989d073ad3b6c8cc6be0202f23337545b5b5973bc03ad8d847b`.
- Read the actual `a00-name-whole.edits.json` and its complete DRAFT witness.
  The ledger's current SHA-256 is
  `5eb1765402e494d95be2339d4c88b6b76bd19fe355fa2861d4325ad58579e6dc`.
  Asset replay checks quoted period/word labels against their exact positions
  in the translated source alts, not merely membership in the same alt.

The manifest retains both actual source alts and all module/blob hashes.
All byte hashes use pinned Git blobs, not Windows checkout newline variants.
The retained Indonesian SVG outputs are exact source bytes.

| Asset suffix | Top-level anchor | Media / immediate parent | Numeric groups | Word-arrow rows |
| --- | --- | --- | --- | --- |
| `013_img` | `eip-id1168289680652` | `fs-id1227744` / `eip-id1168289680652` | `37 / 519 / 248`, repeated below | 3 |
| `014_img` | `fs-id2326974` | `fs-id1209906` / `eip-id1168287499693` | `8 / 165 / 432 / 098 / 710`, repeated below | 5 |
| `015_img` | `fs-id1825910` | `fs-id2670483` / `fs-id1526255` | `327 / 577 / 529` only | 0 |

Both literal `098` cells retain their leading zero and exact coordinates.
Their word label is `Sangang puluh wolu éwu,` in both Javanese registers:
the group value is 98, but its written three-character form is not normalized.
The eight standalone comma nodes and the four trailing word-row commas in
014 retain their positions and roles. The first 013 group remains the actual
two-digit `37`; no padding is invented. No arrow or word row is added to 015.

## Canon and register decisions

At label drafting and source comparison, read the actual readable entries
under `downloads/jv-Latn-ID/canon/`, then reread their relevant entries against
the generated label text for final QA. The manifest records readable-file
hashes and the decisions; no canon registry was modified.

- C01 `wilangan.txt`: count/number sense supports `wilangan`.
- C05 `telu.txt`: three; `klompok telung digit` is a composed draft label,
  not a claimed quotation of a standardized mathematical compound.
- C07 `lima.txt`: `lima` and `limang atus`; teen/cardinal compounds such as
  `sangalas` remain subject to native review.
- C19 `atus.txt`: `atus`, `satus`, `rong atus`, and `pitung` counting examples.
- C24 `ewu.txt`: the dedicated entry supplies `éwu` and `éwuan`; use these
  accented forms consistently, not the unrelated `éwuh`/`èwuh` senses.
- C25 `yuta.txt`: use the million sense, not the archaic homograph meaning
  confused. The period label `yutanan` remains explicitly provisional.
- C26 `wolu.txt`: eight; `wolung trilyun` is a productive count compound,
  not an attested complete mathematics phrase.
- C27 `sanga.txt`: nine and the explicit `sangang puluh` count pattern.
- C28 `sewidak.txt`: sixty; `Satus sewidak lima milyar,` agrees with the
  section's 165-group name.

The concise cardinal and period labels deliberately match across Javanese
registers. Accessibility descriptions use fuller academic clauses versus
conversational `iki`, `klompoke`, and `tulisane`; mathematical values do not
change. Both roots explicitly declare `jv-Latn-ID`. SVG-only titles,
descriptions, and `kelompok tiga digit` are translated as well as visible
number names. Descriptions referring to Indonesian word forms now explicitly
say `basa Jawa` in the Javanese assets.

`satuan`, `digit`, `label`, `milyar`, and `trilyun` are declared technical
loans, not accidental untranslated fallback or new canon attestations.
`satuan` remains the diagram's ones-period label; it is not appended to a
complete cardinal name. Productive compounds remain provisional.

## Canonical JPEG inspection versus derivative rendering

Inspected the three existing local canonical JPEGs directly, without any
archive extraction or download. Their local bytes equal the pinned Indonesian
repository JPEG blobs, whose identities also match the canonical English
tree. The manifest records exact JPEG SHA-1/SHA-256 and byte lengths.

The original JPEGs confirm the same numeric groups, both 098 occurrences,
the 3/5/0 word-arrow-row counts, and the word-form ordering. The inherited
Indonesian SVGs are redraws, not pixel-identical JPEG copies. In particular,
013's red annotation arrow points left in the canonical JPEG but right in
the inherited SVG. This handoff preserves that inherited SVG geometry and
explicitly records the distinction; it does not silently reverse an arrow.

For the separate derivative check, used the already-installed ImageMagick
7.1.2-26 Q16-HDRI x64 (`38ba210:20260621`) with explicit
`RSVG` / librsvg 2.40.20. Arguments were `-background white -density 96
RSVG:<absolute SVG path> png:-`. PNG bytes stayed in memory; Pillow decoded
RGBA pixels. No image file, library, or binary was downloaded or installed.

Rendered all six Javanese SVGs. Each academic/conversation pair had identical
dimensions and RGBA pixels, as their different descriptions are nonvisible.
Inspected the three distinct rendered images at their actual 900×210,
1000×280, and 350×90 dimensions. No clipping or overlap was observed; the
accented labels, leading zeros, and punctuation were visible. This check is
specific to that renderer and those exact source SVG hashes, not browser
compatibility or integrated-reader layout.

The manifest's render witnesses bind all six SVG SHA-256 values and each
pair's pixel hash. `visual_review_of_derivatives` is true only when all current
Javanese SVG bytes match those witnesses; future changes do not silently
inherit the positive clipping check. An in-memory changed-description probe
also correctly turned that review flag false, without writing any product.

## Replay and fail-closed checks

`products()` returns exactly ten products in memory: nine SVGs plus the
manifest. Two calls returned identical bytes, and all existing output sizes,
SHA-256 values, and modification times remained unchanged during pure replay.
`python -B languages/jv-Latn-ID/scripts/prepare_name_whole_assets.py --check`
passed. Normal generation validates every product and repeats the complete
in-memory pass before per-file atomic writes; this is not a multi-file
transaction. No network or lazy Git fetch is used.

Twelve bounded adversarial probes were run read-only: changed leading zero,
changed group order, source comma changed to period, changed coordinate,
unknown linguistic text, unknown register, changed numeric title, removed
word-row comma, nested text, nonwhitespace tail text, wrong cardinal label,
and a period-label swap. The last probe exposed an initial membership-only
alt comparison; the script was tightened to compare exact corresponding
quoted positions, then the swap was rejected. No generated label needed a
semantic correction. This is finite source validation, not a generic number
or language parser.

Final checkpoint:

- Nine SVGs: 29,879 bytes total; all geometry, non-language attributes,
  hierarchy, IDs, group-cell text/coordinates, and visible punctuation match
  the inherited SVGs.
- Manifest: 34,923 bytes; SHA-256
  `f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26`.
- Ten generated products: 64,802 bytes total.
- Preparation script SHA-256:
  `17994aaa32935a403770cd1e80e030f28819cf7627d28ffa4845fb9c573eb096`.

No current numerical, group-order, cardinal-label, or clipping defect was found
in these nine SVGs. Integration must still reference the correct three-track
outputs and handle narration/table/prose separately. The full A00/A10/AX-2
assignment remains unfinished.
