# Marathi lane takeover and restart cursor

This document is a transcript-free restart path for the commissioned `mr-Deva-IN` lane. It is not a completion certificate. Read `GOAL.md` first (the durable roughly3,000-character objective), then `WORKFLOW.md`, `DECISIONS.md`, `STATUS.json`, `NEXT.md`, `SOURCE_MAP.md`, `SOURCE_ERRORS.md`, `canon/CONSULTATIONS.md`, `canon/witnesses.lock.json` and `terminology.csv`. The downloaded corpora are translation inputs only, never training or fine-tuning data.

## Assigned scope and current boundary

The assignment is the complete five-book sequence A20, A30, B10, B20 and B40 plus provenance, target-language canon consultation, deterministic builds, source/mathematical review and readable delivery artifacts. Checkpoints never end the goal. General acquisition/license/supply audits are already complete and must not be restarted without a concrete need.

Reader-ready work is HTML MR-BRIDGE-001–005, PDF MR-BRIDGE-006–008 and the complete source-ordered `A20-m81373` PDF. They cover140 unique source selections; one complete source module is reader-ready. HTML009–025 is structurally/source reviewed but has no accepted HTML visual review. The exact accepted working source snapshot is through MR-BRIDGE-025:582 selector occurrences,578 unique selectors,140 ready and438 pending. Complete source assemblies exist for m81373 and m81374; only m81373 has a reader-ready module PDF.

The next accepted source cursor is A20:m81427 wrapper `fs-id1167834233994`, MR-BRIDGE-026, “Solve a System of Equations by Substitution”. Its draft/freeze/build exists outside the checkpoint, but acceptance is stopped: both EN and ID figure010a rasters print the erroneous intermediate `15/4` before `16/2`; correct arithmetic is `15/2`. Revise the alt and drafting note to identify a bilingual source-image/accessibility correction, refreeze/build, then rerun the separate independent gate. MR027 elimination and MR028 method-selection drafts are also active outside the checkpoint. After MR028, the audited continuation is MR029 Key Concepts `fs-id1167835378580`, then MR030–036 as mapped in the latest durable decision/source notes. Earlier uncovered A20 content, the rest of A20/A30 and all B10/B20/B40 remain substantial unstarted obligations.

## Source, canon and bundle layout

In a takeover bundle, `repo/` is the exact Git checkpoint. Ignored but actually used original source archives, target-language PDF/OCR/page renders and other readable derivatives are restored beneath `repo/` at their original relative paths so archive-dependent checks can run without this laptop. `MANIFEST.sha256` covers every regular file except itself; `CHECKPOINT.json` records the exact HEAD/tree/parent/branch and manifest identity. `REMOTE_ONLY_SOURCES.tsv` records official Marathi web references that were read remotely but whose original page bytes were not acquired, including locator, access date, identity/hash availability and access limitation. Do not interpret a URL citation as locally preserved bytes.

The immutable acquisition authority is `repo/mr-Deva-IN/sources.lock.json`; later ordered selections are in `repo/mr-Deva-IN/provenance/MR-BRIDGE-*.lock.json`. Preserve original archive/member bytes beside serialized excerpts. Existing notices and audit references are authoritative; do not launch another general license audit. Canon use is stage-specific in `canon/CONSULTATIONS.md`; do not mark an unread source consulted or promote provisional compounds merely because component words are attested.

## Safe entry and verification

From the bundle root, use Python3.11+ standard library for the source/unit checks:

```powershell
python -B repo/mr-Deva-IN/tools/test_unit25_math.py
python -B repo/mr-Deva-IN/tools/test_assemble_m81374.py
python -B repo/mr-Deva-IN/tools/test_m81374_primary_source.py
python -B repo/mr-Deva-IN/tools/test_freeze_unit.py
python -B repo/mr-Deva-IN/tools/test_build_unit.py
```

The bundle builder tests the first three entry commands when created. Freeze/build commands require the exact ignored archives restored at their manifest paths. Build a stable unit only after coordinating ownership:

```powershell
python -B repo/mr-Deva-IN/tools/freeze_unit.py MR-BRIDGE-026
python -B repo/mr-Deva-IN/tools/build_unit.py MR-BRIDGE-026
```

Never refreeze while a writer edits its config. Never use a browser workaround for local HTML: the in-app Browser explicitly denied local-file navigation and prohibited alternate Edge/CDP/local-HTTP routes. Structural HTML PASS is not visual acceptance.

PDF generation is direct structured XML→ReportLab, not HTML conversion. The accepted module environment is Python3.12.13, ReportLab4.4.9, pypdf6.14.2 and uharfbuzz0.56.0 with Nirmala/Cambria faces recorded by hash in receipts. Restore those exact packages in a task-local environment; proprietary system fonts are not redistributed. A different runtime is expected to reject exact-receipt reproduction. Preserve accepted PDF bytes if exact dependencies are unavailable. Every new PDF must be rendered with Poppler and every page actually inspected before a ready claim.

## Known limits and excluded active work

No native Marathi mathematics-teacher review, production publication, main merge, PDF/UA, PDF/A or universal accessibility certification exists. HTML006 needs a visual recheck; HTML007 has a known clipped phone table; HTML008 onward is visually unreviewed. Source corrections, supplied answers, source omissions and authored explanations must remain visibly distinct.

The checkpoint deliberately excludes private `USER_UPDATES.md`, root/user instruction captures, raw chats, credentials, account/task/host records, ignored transient renders, broken outputs and live MR026/MR027/MR028/PDF work. Their safe resume facts are summarized above and in `CHECKPOINT.json`; do not copy their mutable files over the checkpoint until their own gates release. The lane never pushes, merges main or publishes a release; hand the verified checkpoint to the coordinator for sanitized capture, then continue the five-book assignment.

Exact checkpoint HEAD/tree/parent and takeover-manifest identities are generated after commit in the bundle-root `CHECKPOINT.json` and `MANIFEST.sha256`. Those files, not a conversational summary, are the identity authority.
