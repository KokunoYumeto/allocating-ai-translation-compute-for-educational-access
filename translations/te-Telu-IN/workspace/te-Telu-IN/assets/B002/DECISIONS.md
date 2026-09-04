# TE-B002 asset decisions and reading receipt

2026-08-30. Scope: only the nine subsection images, nine new code-native SVGs,
their generator, this receipt, manifest and local QA preview. No source prose,
translation file, reader builder, source lock or corpus checkout changed.

- B002-A01: Read the complete frozen `sources/TE-B002.en.cnxml`, subsection
  `fs-id2340048`, before designing assets. It contains nine image nodes: 002-010,
  with `_img` on 003, 006, 007, 008, 009 and 010. Preserve every source media ID;
  preserve figure IDs where a source figure wrapper exists. Do not invent figure
  IDs for the six standalone media elements.
- B002-A02: Reread the terminology ledger and canon examples C03-C05/C10-C12;
  reread existing OCR for TS Class 2 PDF pages32,33,42,44 and inspected all four
  page images. The relevant effects are distinct groups/place contributions,
  witnessed వందలు/పదులు/ఒకట్లు, and expansion-to-compact correspondence. No AP
  variation or native-speaker approval is inferred.
- B002-A03: Read only the nine named JPEG members from the existing pinned
  prealgebra archive. ZIP CRC and each selected Git blob SHA-1 were checked;
  archive size, pinned metadata and commit comment were checked. No full archive
  extraction or additional download occurred. Preserved originals total970083
  bytes. The generator refuses to overwrite an original with different bytes.
- B002-A04: Individually viewed all nine preserved JPEGs before building SVGs.
  Confirmed the three/seven/four dollar-bill groups; one/ten/100 unit legend;
  138,215,176,237 grouping models; and the three significant-digit arrow diagrams.
  The original JPEGs have not been edited or raster-transformed.
- B002-A05: Diagram002 uses simple separated counting cards, not currency artwork.
  Keep explicit U.S. dollars, the $ sign, three100-dollar, seven10-dollar and
  four1-dollar units, and their300/70/4 subtotals. Do not convert dollars to rupees.
- B002-A06: Diagram004 preserves the source's unit-to-rod-to-square sequence;
  it is rearranged horizontally for the new layout. It is a legend of separate
  units, not a request to combine them into111. Every rod has exactly10 equal
  unit cells; every hundred square is a complete10-by-10 grid. The same unit-cell
  scale is used in all block diagrams.
- B002-A07: Diagrams005/007/009/010 preserve counts (1,3,8)/(2,1,5)/(1,7,6)/(2,3,7)
  in hundreds/tens/ones order.005 keeps source count labels as count-times-unit
  expressions.007/009/010 are counting questions: visible place headings are
  added, but visible counted quantities and result numerals are not printed.
  Accessible descriptions retain the source's count information.
- B002-A08: Diagrams003/006/008 preserve the red significant digits and three
  arrows linking each expanded term's leading digit to the corresponding compact
  numeral digit. Arrow colour is harmonized with red emphasis; source arrows were
  turquoise. Compact-form digits are also red in the redraw (black in the source)
  to reinforce correspondence. No mathematical value, digit order, dollar symbol or correspondence
  is changed. English source JPEGs remain available beside the localized version.
- B002-A09: Generated SVGs contain only text, paths, groups and rectangles, with
  Telugu-first place labels plus brief English glosses. No embedded raster image,
  script, external font download, or external asset dependency is introduced.
- B002-A10: Browser setup reported no available browser. Read the prescribed
  troubleshooting guidance and checked discovery once; it returned an empty list.
  The local preview and mathematical checks are supplied for the main task's
  established renderer. Do not treat these checks as completed visual review.

## Verification

```powershell
python -B te-Telu-IN/scripts/make_b002_assets.py --originals-only
python -B te-Telu-IN/scripts/make_b002_assets.py
python -B te-Telu-IN/scripts/make_b002_assets.py --verify
python -B te-Telu-IN/scripts/make_b002_assets.py --self-test
```

The first command only materializes the nine verified small originals. The second
generates the deterministic SVGs, manifest and preview. The last writes nothing:
it rechecks the selected source members, preserved originals, SVG bytes, every
group/cell count and grid, modeled values, significant-digit emphasis, arrow
endpoints and exact manifest. All originals, source members, media/figure IDs and
localized hashes are mapped in `manifest.json`.

The self-test writes no files: it validates all nine generated diagrams, rejects
nine deliberate missing-group/missing-cell/wrong-arrow fixtures, and checks every
rectangle fits inside its SVG canvas. This is geometry/count QA, not a browser
text-shaping or native-speaker test.

Main task: visually inspect `preview.html` or the final TE-B002 reader, including
the longest seven-rod model and both two-hundred-square models, and record the
rendered result in the main QA receipt. No build or translation completeness is
claimed by this asset-only deliverable.
