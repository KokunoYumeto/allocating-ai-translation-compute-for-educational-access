# A10-002 parent integration review — 2026-08-31

Reviewed source boundaries, the CNXML-derived QA implementation, selected translation/number-name/rounding passages, the actual 009c/010a/022 source images, and the final browser views recorded in `visual-a10-002.json`. This is bounded review, not a second full native-language proofread.

The source section has 33 direct children counting its title; this reader retains children 13–32, all twenty, under the same source section ID. The standalone next paragraph `newelem_para01` is required and is not skipped. A10-001 and A10-002 jointly cover this first section, not the full module. Ninety-two translation keys include twenty table-cell scaffolds, three intentionally empty.

The 700px table minimum caused a real mobile clipping issue. The unit-only 660px revision was inspected at zero scroll and after pointer scrolling; the complete initial instruction and carry diagram are accessible locally without page overflow. Image bytes and source text remain unchanged.

The initial 1,364-check suite rejected a naive Latin-text injection because it lacked LTR isolation. A correctly isolated detached `<p dir="ltr">CONTRADICTORY 103978 = 999</p>` appended to `main` passed every DOM/image/rounding/notice/link validator. No reader file was mutated. Added exact body/main shape, child order, text/tail and source-label/continuation-text checks, plus five regression mutations. The first guard run used an incorrect expected CSS class (`source-section`); direct inspection showed the actual frozen class was `translated`, which was corrected in the test only.

Final suite: **1,368 checks, 34 detached mutations**, reader SHA-256 `6b9a1c45c521aa4d11502773c3327373fd1d4291ae4779a5a40e7579ce763a92`. The former 1,364/29 receipt is superseded. The reader and its browser evidence were unchanged by QA hardening.

Specialist Punjabi terminology and number-name spelling remain provisional; the translator's actual canon consultations and community number-list observation are recorded in `a10-unit-002-language-notes.md`. This parent pass did not invent an additional canon reading stage or certify native/educator/assistive-technology review.
