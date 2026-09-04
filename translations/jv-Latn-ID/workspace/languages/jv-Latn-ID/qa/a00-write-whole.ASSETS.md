# Writing whole numbers: asset handoff — 2026-08-31

Root read complete pinned ID/EN fs-id1339359, the phrase ledger, all three actual
Indonesian SVGs and relevant full canon extracts C07/C19/C24/C25/C27. The exact
source media are fs-id2668978 /016_img, fs-id2903601 /017_img and
fs-id1345376 /018_img. The manifest binds every source SVG and canonical JPEG
member to its pinned Git blob, and records all literal text replacements.
The canonical members are read from the existing read-only shared archive.

Generated three byte-exact ID SVGs and six Javanese SVGs. Short diagram labels
deliberately agree across the two target registers. Only registered linguistic
text and root xml:lang change; all geometry, styles, arrows, grouping commas,
numeric positions and zero-filled groups remain unchanged. The final groups
are 53/401/742, 9/246/073/189 and 77/000/000/000. Blank word blocks in 018 remain
blank while their printed digit groups remain zeros. The English 017 alt's
incorrect 742 is not propagated over the correct ID073; neither source is edited.

Root rendered and visually inspected all three distinct target SVG byte sets
using installed ImageMagick 7.1.2-26 Q16-HDRI, explicit RSVG delegate, density96,
white background and alpha removal. Academic/conversation files are byte-equal
for each diagram, so these three renders cover the six current target files.
At their standalone sizes (920×195,1120×195,900×195), labels and arrowheads are
visible without observed overlap/clipping. Numerals 073 and all nine zero
digits in the budget chart are present. This is renderer-specific static QA,
not integrated three-column legibility, browser, native or screen-reader review.
The canonical JPEGs have byte witnesses here, not a new visual-comparison pass.

| Target pair | SVG SHA-256 | Inspected PNG SHA-256 |
| --- | --- | --- |
| 016_img | e9e7ac52f72f2a8477150ee4ae3a8c65c301635b462a5d42e7c0df13474a1b95 | c1b41005b04b6ce3b119012bd5afe41bbb6e237ad405e5708da694a543ccefdd |
| 017_img | c15d2747d1f1a5ade046cb4a9280313e3d55d3e58c204da8e9f54c03085ecbd5 | c9f9179622107af7557d6ff16a6907939631cc9316a41f98b673a4b88f77aea0 |
| 018_img | 037c5dca1c756a3f0cea89965d4084583b306722a1eb9d85cfa094f4976a9297 | 3964447e43413e442778607fdad6f35c4f56b044820c2c1621bcef32c81e7774 |

Preview PNGs stay in ignored downloads/jv-Latn-ID/qa-render-writing. The SVGs
and manifest are deterministic products of prepare_write_whole_assets.py;
--check does not write. A future target-byte change invalidates this snapshot.
Full writing-unit reader/narration integration and human reviews remain pending.
