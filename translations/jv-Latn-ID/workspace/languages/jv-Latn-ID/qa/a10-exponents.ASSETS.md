# Exponent diagram draft and static inspection — 2026-08-31

Root read both full pinned source slices [40:53], all 43 phrase rows, and the
complete C21 ping/C34 rambang extracts at this stage. The retained pangkat and
basis/eksponen terminology remains provisional. Rambang's actual mathematical
sense is distinguished from homonyms and its flattened extracted example.

Both exact canonical JPEGs were inspected from the pinned ZIP in memory; their
computed Git blob IDs matched the pinned tree. Only the two small source JPEGs
(72,570 bytes total) and four native Javanese SVGs were subsequently materialized.
No network acquisition, large archive extraction or archive-wide sweep occurred.

| Source | Git blob | SHA-256 |
| --- | --- | --- |
| 003_img_new.jpg | ed2cb8bf92e9a4ec9def4c206f288c874a00f12f | 5be6626600b25727b5a93b37e1c4cb45a82a3fe9cc1e91b4fc0888b804370ec7 |
| 004_img_new.jpg | a2b54ff7ab676ad2a2f99cf93fecc035d8ae4037 | fe978ddd3f9f8cb93b2402be5268888aa0f668ae5c2dd12032c7f16208ec2bbe |

003 has base→2³←exponent and a three-factor product 2·2·2. The Javanese text
follows the Indonesian clarification that there are three equal factors, not
three additional binary multiplications. 004 shows aⁿ=a·a·a·…·a: three visible
a factors before the ellipsis and one after. Both source alts omit one of those
pre-ellipsis factors. Root corrected only the Javanese alt and documented it in
the exact phrase ledger; source keys/pivot/MathML are unchanged. The brace means
n factors, not exactly four or an infinite product.

Native SVGs reflow the longer base labels while preserving arrow directions,
base/exponent placement, factor order and full-product brace. They are not
pixel-identical derivatives. Red/teal roles use darker colors; no formal contrast
or integrated browser pass is claimed. The unchanged Indonesian track will use
the exact source JPEG; Javanese tracks use SVG. Future reader integration must
consume per-output MIME types, not apply JPEG MIME to all three tracks.

All four SVGs were rendered with ImageMagick 7.1.2-26 Q16-HDRI and explicit RSVG,
density 96, white background and alpha removal. Initial inspection caught the
older renderer mishandling auto-start-reverse: an arrowhead covered the exponent.
Changed the end-arrow marker to ordinary orient=auto, rerendered and actually
viewed all four final PNGs. Both arrows now point to the intended base/exponent,
the superscripts are visible, and no label clipping/overlap was observed at the
940×100 (003) and 480×155 (004) standalone render sizes. Three asset tests pass.

Final SVG SHA-256, in translation/assets/a10-exponents/:

```text
003 jv-academic     3faf45b7e85725c211cd3f319a154347b3143749ed4752e79285f0f7eec324f9
003 jv-conversation 237e927996875182f862213df7d3cf0e9fe99369f4c67947873a7f1cb12eeefa
004 jv-academic     50ff5a0f927ed9fcc6e8eea2dc40e134c2d3c7645c7d574beb665304f2cbaea8
004 jv-conversation c795b0875286b75157c61136f068d0ec6339973dd87f39622d8a07024c3eb059
```

Final PNG SHA-256, in ignored downloads/jv-Latn-ID/qa-render-exponents/:

```text
003.jv-academic.png     3fea9a4feb20fa5df2738f393a5559b39b4e59e35a06b1f5fb20ea85687e9e1b
003.jv-conversation.png cc5dfb698322e05e3636d1dfcbff34fe6ab1e7c6e5d1f8e07128a48e55e8c4fe
004.jv-academic.png     92c4b3113640560e8499543e3f17583ad9afc181f19171e1ccf813db17442f9d
004.jv-conversation.png 0de3de9b72cff7f2992e3c44e940a8c7b4e336ffd5a6ab92a13c88a64973fa1f
```

This is source/asset preparation and renderer-specific static evidence, not
integrated CNXML/reader/SSML completion, native language approval, screen-reader
testing, listening review or a whole-module completion. The exponent narration
workflow and full A00/A10/AX-2 assignment continue.
