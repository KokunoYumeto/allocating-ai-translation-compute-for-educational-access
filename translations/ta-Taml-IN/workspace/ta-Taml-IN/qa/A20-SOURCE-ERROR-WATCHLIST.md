# A20 source discrepancy notice - must check before reuse

Received2026-08-30 from coordinating task[local-task-id]. This is a narrow production warning, not a new supply/license audit and not a pause to current A00 translation. The Tamil task has not yet independently inspected these A20 pixels/answers; do not report the notice as our completed verification.

The coordinator reports independent visual confirmation of three differences between pinned EN bundle commit38cae454e644abf9f0a623e876994553881597c9 and Indonesian v0.3.0-wip, Intermediate Algebra modulem81373. Basename prefixCNX_IntAlg_Figure_03_05_; suffix_img_new.jpg:

-202: English image maps Amy toFebruary24; Indonesian redraw usesFebruary14. Marathi reports EN/ID alternatives say14.
-205: English image has(-2,-1), and Marathi reports the English supplied answer agrees; Indonesian redraw uses(-3,-1).
-208: English image has(-1,-3) and(2,6); Indonesian redraw uses(-2,-3) and(3,6). Reported full English set is{(-2,-6),(-1,-3),(0,0),(0.5,1.5),(1,3),(2,6)} with domain{-2,-1,0,0.5,1,2}. The Indonesian redraw repeats x=-2 at different y-values, changing the function decision. Do not derive mathematics from the inconsistent alternative/redraw.

Before translating/reusing these exact figures, the Tamil worker must inspect pinned English pixels, both alternatives and supplied solutions, reconcile the mathematics explicitly in a Tamil decision/QA note, and retain provenance. Do not modify pinned archives or silently substitute conflicting coordinates. No push, publication, deletion or source-archive replacement is authorized.

Reported evidence (paths may need revalidation after worktree cleanup):

-[local-home]/.codex/worktrees/9286/LAN ALLOC/mr-Deva-IN/SOURCE_ERRORS.md
-Same locale's provenance/MR-BRIDGE-004.lock.json
-EN raster copies under mr-Deva-IN/assets/MR-BRIDGE-004/
-Side-by-side originals under downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-004/ in that worktree.

The coordinator states all six rasters were inspected and its text/answer cross-check was still being verified when this notice arrived. Follow any newer evidence, but preserve this original report and record revisions. The current Tamil next work remains A00rounding/recovery integration, not an unrequested detour into an A20 audit.

## Received verification addendum - 2026-08-31

The coordinator now reports that all six EN/ID fragments were checked against the pinned archives and all six images against their locked hashes and sizes. For figure205, **both** supplied solutions contain `(-2,-1)` and domain `{-3,-2,0,2,4}`, even though both alternatives say `(-3,-1)`. Figures202 and208 have no supplied solution in the selected fragments; corrected answers must be labeled original derivations from verified pixels, not translated supplied answers. Coordinator evidence: `[local-home]/Documents/ChatGPT/LAN ALLOC/logs/A20_SOURCE_DISCREPANCY_VERIFICATION_2026-08-30.md`. This remains received evidence, not this Tamil task's own pixel verification, and must be checked when that material is reached.
