# PNB-012 parent source and browser review

Reviewed reader SHA-256: `8d74a1f3351e051ad7f56cb5362d6ee7c85061d057a44e4f6b1d2f4f9cb32940`.

The frozen independent QA passed 35,449 checks and 28 detached mutations in two byte-identical full cycles. It binds all 376 translated source blocks, six separate source-link labels, 577 source IDs, 258 reversible canonical MathML trees, 44 exact JPEGs, 35 links, two footnotes, 82 exercises and 51 supplied solutions. Exactly 30 of the 61 Section Exercises have source solutions; the other 31 remain unanswered. Receipt `structural-012.json` has SHA-256 `8038d9b66e5339dfbe3439ba0beb251f44ea6027c69a716c42fc48c4c3079fe2`.

The parent used the required in-app Browser at 1009px desktop content width and 375px mobile content width. The final reader has no duplicate IDs or page-level overflow. All 44 images loaded on three repeated final desktop reloads and the final mobile load. One changing image request failed on two earlier local-server reloads, but every JPEG decoded locally, sequential HTTP responses matched all 44 local files byte-for-byte, and repeated final runs loaded all 44; this was treated as transient local serving rather than a file defect.

The corrected three-row source table was checked in DOM and pixels. Its Punjabi row names are `<th scope="row">`; formula cells are `<td>`. At 375px its 342px table stays in a 340px local scroller. The two longer piecewise formulas exceed only their immediate MathML boxes (342/304 and 350/340) and remain in parents with `overflow-x:auto`; document width remains 375px.

Footnote 1 was activated through the visible source reference: it reached `#fs-id1165137758551-text` at the viewport top, and its visible return link reached `#fs-id1165137758551` exactly. The final footer was visibly reviewed and retains complete-module scope, all source-solution gaps, component notices, comparison limits and the unfinished five-work assignment.

Bounded final screenshots and hashes are recorded in `visual-012.json`. This review does not certify native usage, mathematical pedagogy or assistive-technology behavior.
