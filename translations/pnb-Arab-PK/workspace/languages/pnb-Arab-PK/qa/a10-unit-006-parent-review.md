# A10-006 parent source and browser review

Reviewed reader SHA-256: `515ae99706a621c967c5f2b1d4c9e6562c78e34987072e86e122f5f2c4bf7860`.

The independent read-only source/DOM audit reproduced the exact canonical LF prefix `[0,42893)`, the boundary before `fs-id1170654953465`, all 187 translation owners, 134 IDs, 604 bound nodes, 98 MathML roots/737 MathML nodes, eight tables/97 cells/15 source headers, four byte-exact JPEGs and nine source exercise/solution pairs. It found no source-fidelity or structural blocker. The final structural receipt is `structural-a10-006.json`, SHA-256 `60f2881aba09829f631bfad01fe81a77e513cf7fe2868d99b3d59866735ecca9`.

The parent used the required in-app Browser at 1009px desktop content width and 375px mobile content width. No duplicate ID, broken asset or page-level overflow remained. At mobile width all eight source tables stay inside 340px `overflow-x:auto` wrappers; their source widths range from 660px to 1320px. An actual horizontal pointer-wheel pan moved the four-column operations table from `scrollLeft=0` to `600`, exposing the hidden Punjabi reading column without changing table direction or source cells.

All four images loaded. The 541px exponent image remains inside a 340px local scroller; its original English `base`/`exponent` labels and `2³ = 2·2·2` pixels were visibly reviewed. The second `aⁿ`/`n factors` image and both a/b number-line images were also checked through the final page. No mirror or RTL transform was present. The footer still labels source ambiguities/corrections separately and does not claim whole-module, native, educator or assistive-technology completion.

Bounded final screenshots and hashes are recorded in `visual-a10-006.json`. This review is a desktop/mobile rendering gate, not a full-page native-language proofread or assistive-technology certification.
