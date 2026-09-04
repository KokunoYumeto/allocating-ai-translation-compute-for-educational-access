# B007 author handoff

2026-08-31. Complete frozen Key Concepts subsection translated:24 elements,
7 source IDs,14 text slots,all14 localized; no MathML in this subsection. This
is author verification, not independent review or native-speaker approval.
Full assignment continues beyond this recap. No B006 file changed.

## Read and consulted

Read complete English and Indonesian `m81243#fs-id2296006`, both14-slot
recaps. Reread actual TS6 OCR13/14/15, then inspected all three complete PNGs.
Page13's paired instructions preserve naming-versus-writing direction; page14
supports nearby-place rounding and the85→90 convention; page15's valid5078
expansion supports zero positions. Do not use its known21504 factor typo.
Referred to the existing B004–B006 catalog wording and actual prior bridge IDs.

Source naming conventions remain English-specific. Whole numbers use
`పూర్ణాంకాలు`; international grouping and editorial bilingual scale labels
remain unchanged. The rounding recap includes the immediate-right digit and
conditional carry. A separate original bridge connects the chart to its name,
a new zero-containing numeral, and two rounding targets; it adds no redundant
placement score. Readiness routes to the earlier units' own rules.

## Exact PNG and derivative reuse

Only selected member `media/CNX_BMath_Figure_01_01_011.png` was materialized,
28333 bytes. Archive SHA256, selected ZIP CRC and pinned Git blob were checked.
Full original B007 PNG and B003 JPEG were both viewed before reuse. They are
not byte/pixel-identical: the recap PNG has blue-gray/blue colors, the earlier
JPEG teal. Both have15 place columns grouped into five periods, eight initial
blank digit cells, then5,2,7,8,1,9,4 in the same positions. PNG signature also
confirms the frozen JPEG MIME attribute is wrong.

The B003 SVG's visible artwork is reused exactly after its pinned hash and
deterministic generator output were checked. Only the accessible provenance
sentence is updated for the B007 PNG. Manifest binds new media
`eip-id1170196618449` and figure `eip-id1170196618448`, and records both the
reused derivative and the correct unchanged recap original. Reusing artwork
does not mean reusing the earlier JPEG as the B007 source.

## Checks actually run

- `make_b007_assets.py --verify`:PASS archive/source/original identity,
  deterministic SVG/manifest and actual15-column/5-period/8-blank/5,278,194
  content. `--self-test`:7 corruptions rejected (digit, exponent, leading
  blank, label, period grouping, accessible provenance, digit alignment).
- Read-only localization check:all24 ordered elements and7 IDs preserved;
  all14 slots handled. Actual source numbers/rounding statements compared
  against catalog; no source question or answer omitted.
- Bridge:12 unique IDs,9 links checked against actual source or already-built
  prior reader IDs. One local chart link; eight prior support/recheck links.
- Independently evaluated both actual English names:5,278,194 and6,004,020.
  All7 actual numeric equality expressions pass, including both expansions,
  four distances and9+1=10. Integer half-up checks give5,278,200 at hundreds
  and5,278,000 at thousands; target/control pairs are1/9 and8/1.
- Naming/writing preserve value; rounding may change it, but exact multiples
  remain unchanged.004/020 retain three lower-period positions; first-period
 6 does not gain unnecessary leading zeros. Final prose was reread after
  clarifying that each of five groups—not each individual column—has3 places.

No new browser rendering is claimed. Main owns the integrated B007 reader,
horizontal scrolling, rendered chart, and independent prose review.

## Final input identities

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `sources/TE-B007.en.cnxml` | source freeze | `56a5347ea8916c1d263ccf643fd6fd64ad98a2fdc8dcce33e7e1917d6e8b4f10` |
| `translations/TE-B007.te.json` |6916| `405e4554bdd4d14124c7dfc05dbc992f48a6bf6f5a76e8eb96f5e73aa3f89ff9` |
| `translations/TE-B007.bridge.xhtml` |10208| `f5d75f6c87f904549da7b5cac467ca221dfafa27c9d994c23b6451c862dc4046` |
| `assets/B007/manifest.json` |4300| `8b05db493cd12312e572cef522932dc47f434c5e3a47f1f90c1e26e78065ba0e` |
| `scripts/make_b007_assets.py` |9858| `f70917c4675d26e90d9a1ed56cba8aad9176c4d1b4c6f1084518cd209000dfe3` |
| B007 original PNG |28333| `14458e7e7c27f39e009ba986d638ffcc461e96affee3ab50648df30567eb0915` |

In-memory target using only `build_unit` imports and
`ET.tostring(target,encoding="utf-8",xml_declaration=True)+b"\n"`:
5414 bytes,SHA256
`b12fd4e168604eb3e8b6b830cd4c1dbcf29a22707a1c38c93458a5a4c225b716`.
This is an input-localization receipt, not a claim that a generated B007 target
exists yet. SVG helper imports can change ElementTree's namespace prefix
registration; their differently prefixed serialization is not the receipt used
here and does not imply changed content.
