# Marathi STEM bridge — mr-Deva-IN

Commissioned Grade 8-to-first-year bridge from algebra diagnostics through functions, trigonometry, proof habits, calculus and linear algebra. Five assigned Indonesian repositories and all five pinned canonical upstreams are locally acquired. The historical rank label is no longer objective research evidence and is not used to justify priority; the user has explicitly continued the assignment. See sources.lock.json and SOURCE_MAP.md for exact scope; downloaded corpora are ignored and are translation inputs only.

## Reviewable checkpoints

`translations/MR-BRIDGE-001.xml` is the editable Marathi source. `output/MR-BRIDGE-001.html` is an offline, responsive reading document with visible source IDs, eight worked source examples, two definitions, six diagnostic questions, six practice questions and twelve full worked answers. It is a selected-source adaptation, not ten complete modules or a whole-book translation.

| Reader | Scope |
|---|---|
| MR-BRIDGE-001 | Fractions → equations → relation/function notation |
| MR-BRIDGE-002 | Email models; two source practice items; original table/domain explanation and four new questions |
| MR-BRIDGE-003 | Complete two-bullet Key Concepts recap from A20 m81373 |
| MR-BRIDGE-004 | Complete first twelve-question domain/range practice group, eight canonical diagrams and all answers |
| MR-BRIDGE-005 | Complete twelve-question function/nonfunction group, four canonical mappings, equation tests and all answers |
| MR-BRIDGE-006 (PDF) | Complete 26-question function-evaluation practice group, preserved supplied answers and separately marked supplementary working |
| MR-BRIDGE-007 (PDF) | Four writing exercises, four definitions and an unanswered self-check |
| MR-BRIDGE-008 (PDF) | Opening function/domain-range teaching, two worked examples, nine practice items and six canonical diagrams |
| A20-m81373 (PDF) | Complete source-ordered m81373 module:134 selectors,84 exercises,28 canonical images and64 reviewed pages |

Ready review drafts are **HTML001–005, PDF006–008 and the complete A20-m81373 PDF**. The formats are tracked separately:24 HTML artifacts are structurally built in the current working snapshot, but only the first five have accepted HTML visual review. Four independently authored PDFs live under `output/pdf/`; the primary agent inspected all93 rendered pages. PDF acceptance does not clear an HTML issue.

Ready coverage contains140 unique selected source blocks,14 worked examples,11 definitions,75 source practice items,1 resource note,39 other source blocks and28 canonical diagrams, deduplicated across overlapping formats. Existing original diagnostic/practice material and29 supplementary answers to source exercises are separately identified. The accepted module PDF contributes one complete source module, not a complete assigned book. These are review drafts, not human-approved editions; entire-assignment completion still means all five books and supporting workflow.

Frozen drafts009–012 add50 unique blocks awaiting individual-reader acceptance. Unit011 restores the full source rows and61 nested identities for four historical001 selections: it replaces their representation and contributes zero new unique blocks. The historical bounded build checkpoint therefore has162 selector occurrences but158 unique blocks. The current accepted working snapshot through025 has582 selector occurrences/578 unique selectors, of which140 are ready in at least one accepted format. Drafts013–025 remain structurally/source reviewed but reader-unreviewed; active026 is excluded until its source-image correction, rebuild and independent review pass.

The complete source-ordered `A20-m81374` XML is separately accepted as a second assembled source module:380 selectors,1,366 canonical IDs,255 exercises,141 supplied solutions/114 explicit omissions,481 source MathML objects and149 canonical assets. This source gate does not add ready coverage or a ready reader. Its independently authored PDF remains in production and must pass complete page rendering and visual inspection before any reader-ready claim.

Build from the repository root with Python 3.11 or newer, using only its standard library:

```powershell
python -B mr-Deva-IN/tools/build.py
python -B mr-Deva-IN/tools/build_unit.py MR-BRIDGE-005
```

The builds work without ignored corpora, using committed witnesses and selected binary assets. For units 002 onward, `tools/freeze_unit.py UNIT` freezes only their selected fragments/explicit assets from existing pinned archives; coordinate config ownership before running it. The original `freeze_sources.py` is the initial acquisition-evidence workflow, not a routine prerequisite for every unit. `sources.lock.json` gives restoration URLs and pins. B40 Indonesian uses the recorded filtered sparse checkout; no full-book build is claimed.

The PDF builder is a separate XML-to-ReportLab path, not HTML conversion. Its reviewed environment used Python3.12.13, ReportLab4.4.9, pypdf6.14.2, uharfbuzz0.56.0 and pinned Nirmala/Cambria font faces. HarfBuzz was installed only in the ignored task-local `tmp/pdfs/python-deps` directory, not globally. Rebuilding PDFs on another PC requires restoring the recorded dependencies/fonts; the embedded-font PDFs themselves are standalone. The earlier three-PDF evidence is `qa/PDF-builder-review.md` plus `qa/PDF-primary-review.md`; module-specific evidence is `qa/A20-m81373-pdf-builder-review.md`, `qa/A20-m81373-primary-source-review.md` and `qa/A20-m81373-primary-pdf-review.md`. PDF/UA, PDF/A and universal text-extraction accessibility are not claimed.

## Review and continuation

- `GOAL.md`, `WORKFLOW.md`, `DECISIONS.md`: durable objective, user instructions and external decisions.
- `canon/`:22 Marathi reference-example locators and actual consultation log. PDF OCR remains under ignored downloads. Read these references while translating, not just on intake.
- `terminology.csv`:54 English–Marathi correspondences; unverified choices remain provisional. C20 supports अंतराल; C18 supports असमा/छायांकित; C22 supports उतार, समांतर रेषा, छेदणाऱ्या रेषा and संपाती रेषा. Full system/classification compounds remain authored.
- `provenance/`: original notices, source/release metadata and exact selected English/Indonesian CNXML blocks.
- `qa/`, `STATUS.json`, `NEXT.md`: checks, limitations and next contiguous selected-source block.
- `SOURCE_ERRORS.md`: observed source/alt/redraw discrepancies and explicit treatments, with original witnesses retained.

The pilot's source-derived text and Marathi adaptation are CC BY-NC-SA 4.0, with original component notices preserved. B40's distinct CC BY-SA 2.5 pathway remains distinct; no B40 prose is in this pilot. Marathi canon sources are consultation witnesses, not relicensed or redistributed source chapters. Upstream author, organization and human-contributor credits remain intact. This is an unofficial Codex-assisted draft, not a native-speaker- or teacher-approved edition.

This lane does not push independently. The user authorizes coordinator-managed stable snapshot export to the shared review branch; that is not a main merge or production release. A durable goal persists the task objective; it does not promise computation while the host is powered off.

Later HTML visual QA is explicitly unresolved after a Browser URL-policy denial that also prohibits workarounds. Unit006's calculation line-break revision is `recheck_required`; unit007's clipped phone self-check table is a `known_issue`; HTML008 onward is `unreviewed`. Their automated build PASS receipts certify structure, not layout. `STATUS.json` records these states alongside separately accepted PDF006–008 and A20-m81373. Ready-format review receipts bind exact artifact/report bytes; the Git-index verifier rejects stale evidence or orphan outputs. The historical001–012 checkpoint has291 recorded regressions; primary additionally reran333 following-unit source/math checks through025,17 m81373 assembly checks and18 m81373 module-PDF checks without skips. The m81374 source integration separately has21 assembler-author and20 primary-rerun independent tests. The module-PDF suite uses the recorded Python3.12.13/ReportLab4.4.9 plus task-local uharfbuzz environment; a different system runtime is expected to reject the exact build receipt. No test count substitutes for visual or human review.
