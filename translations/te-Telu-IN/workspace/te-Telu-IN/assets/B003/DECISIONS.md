# B003 chart decisions and inspection record

2026-08-30. Only two selected original JPEGs and new code-native SVGs were
materialized. No full archive extraction or new download. Main translator is
responsible for final reader inspection; these tests are not native-speaker QA.

- BA003-01: Frozen source is `m81243#fs-id1883656`. The generator verifies its
  SHA-256, metadata and immutable commit. It hashes the already-present full
  archive, reads only the two source-named JPEG members, checks each member CRC,
  compares its Git blob SHA-1 to `git ls-tree` at the pin without lazy fetching,
  and preserves the original bytes. Existing differing originals cause failure,
  not silent replacement.
- BA003-02: Both JPEGs were viewed before drawing. `011.jpg` has four horizontal
  bands if the visible **Place Value** title is counted: title, five period
  headers, fifteen rotated place names, and digits. Thus the source alt's four
  rows is not necessarily erroneous; a precise accessibility description names
  the bands instead of calling all four ordinary data rows.
- BA003-03: `012_img.jpg` visibly has three bands: five period headers, fifteen
  rotated place names, and digits. It has no global **Place Values** title,
  although the source alt calls it titled. A corrected descriptive alt should
  omit that invented visible title and identify the actual three bands.
  The new SVG deliberately adds its own bilingual heading; this is an editorial
  redraw choice, not a claim about the original artwork.
- BA003-04: Source011 fills columns9-15 (one-based) with5,2,7,8,1,9,4 and leaves
  eight leading cells blank. Source012 fills columns8-15 with6,3,4,0,7,2,1,8 and
  leaves seven leading cells blank. The internal zero remains visible. Recomputed
  positional sums are5,278,194 and63,407,218. Leading blanks are not added zeros.
- BA003-05: Keep all fifteen positions from hundred trillions through ones, in
  five groups of three. Indian grouping and lakh/crore labels are not used in
  the faithful diagram adaptation. The distinct naming convention is covered by
  the separate canon witness and any explicitly original bridge commentary.
- BA003-06: Reread TS2 pages42/44 OCR and inspected both pages; read/inspected TS6
  pages15/18 in the preceding bounded canon investigation. Use వందలు, పదులు,
  ఒకట్లు, వేలు and పదివేలు consistently. Million/billion/trillion Telugu loanwords
  are editorial parallel labels; their official regional status is unverified.
- BA003-07: New diagrams replace cramped rotated English with horizontal
  multiline Telugu and English at a native2240x460 pixels. Each asset record
  supplies `recommended_min_width_px: 2240`. The reader should use an individually
  focusable horizontal-panning media wrapper and override generic max-width
  shrinking for these diagrams. Page-wide overflow is not an acceptable substitute.
- BA003-08: SVG title/description names all fifteen places and their digits or
  leading blanks. The reader's translated image alt remains necessary: an
  external SVG's own title/description does not automatically replace HTML img
  alt. A fully equivalent text mapping and an accessible pan label should remain
  available in the reader.
- BA003-09: Read-only `--verify` checks the archive, selected originals, SVG
  deterministic bytes, visible labels, digit geometry, positional sums and
  manifest. `--self-test` mutates in-memory fixtures only: wrong metadata digit,
  wrong visible digit, wrong Telugu label, wrong scale, two-digit period, and an
  added leading zero; all must be rejected for both charts. Tests do not establish
  actual font rendering or reader keyboard behavior.
- BA003-10: Retain the B002 manifest field schema (`te-b002-assets-v1`) so the
  existing bounded builder consumes it; `unit`, paths and generator identify B003.
  Source and localized hashes are separate. Asset credits/notices remain those
  of the project, with code-native redraw disclosure in each asset record.
