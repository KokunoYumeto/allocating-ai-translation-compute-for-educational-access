# Queued source-production discrepancies

These are narrow translation-production warnings, not a new license/supply audit.
Pinned archives and canonical files remain unchanged. A warning is not evidence
that the entire source module has been checked or translated.

## A20 m81373: three relation figures

Received2026-08-30 directly from coordinating task[local-task-id].
EN commit38cae454e644abf9f0a623e876994553881597c9; Indonesian comparisonv0.3.0-wip.
Files share prefix`CNX_IntAlg_Figure_03_05_` and suffix`_img_new.jpg`.

| Figure | Reported EN pixels | Conflicting alt/Indonesian redraw |
| --- | --- | --- |
| 202 | Amy → February24 | February14; Marathi reports EN/IDalt also14 |
| 205 | (-2,-1); supplied ENanswer reportedly agrees | (-3,-1) |
| 208 | (-1,-3) and(2,6) | (-2,-3) and(3,6) |

Reported complete EN208 set:
`{(-2,-6),(-1,-3),(0,0),(0.5,1.5),(1,3),(2,6)}`.
Its domain has six values`{-2,-1,0,0.5,1,2}`. The conflicting redraw repeats
x=-2 at different y-values and therefore changes the function classification.
Do not reconstruct this mathematics from the inconsistent alt/redraw.

The coordinator reports personally inspecting all six EN/IDrasters. Telugu main
has read the Marathi SOURCE_ERRORS.md and recorded the lock identity, but has
not yet independently inspected these rasters or the supplied solutions. This
distinction is deliberate: reinspection is a required gate when A20 reaches
m81373, not a reason to halt current A00 translation.

Evidence read:

- `[local-home]/.codex/worktrees/9286/LAN ALLOC/mr-Deva-IN/SOURCE_ERRORS.md`
- `[local-home]/.codex/worktrees/9286/LAN ALLOC/mr-Deva-IN/provenance/MR-BRIDGE-004.lock.json`
  SHA256`00948a46541ee46f257405aa1ec030187c5d8c2a4d6b2e7eed847cad65f3cd85`.
- ENrasters under that worktree's`mr-Deva-IN/assets/MR-BRIDGE-004/`.
- Side-by-side source copies under`downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-004/`.

Required before reuse: inspect exactsourcepixels, sourcealt and suppliedsolution;
record all sourcehashes; reconcile targetalt/answers/artwork explicitly; retain
the pinned originals and provenance. Do not silently normalize the input files.
The Marathi report also queues203sign/spacing and BMI-context cautions; read the
actual corresponding source and relevant primary health guidance before making
any Telugu contextual correction. No current medical guidance is asserted here.

No push, publication, upstream issue submission or deletion is authorized by this warning.

### Verification addendum received2026-08-30; read2026-08-31

Main read the complete external report at
`[local-home]/Documents/ChatGPT/LAN ALLOC/logs/A20_SOURCE_DISCREPANCY_VERIFICATION_2026-08-30.md`.
The coordinator's independent checker matched all six fragments to pinned archive
content and all six reviewed images to locked hashes/sizes. This is reported
verification, not a claim that Telugu main has inspected those future rasters.

- Figure205: both EN and ID supplied solutions`fs-id1167836448402` include
  `(-2,-1)` and domain`{-3,-2,0,2,4}`, despite both alt texts saying`(-3,-1)`.
- Figures202/208: neither selected fragment supplies a solution. Corrected
  answers derived from verified EN pixels must be labeled original work, not
  translations of supplied solutions.
- The unit-specific pixel/alt/answer gate above remains required before reuse.
  No broad audit, source edit, publication or pause of A00 is requested.
