# Owner handoff — pnb-Arab-PK A10-009 m82453

Status: **sealed locally; not admitted**. Canonical ownership, integration and publication remain with the owner task.

This packet completes exactly one source-ordered section, `fs-id1170655163482` (“Identify and Combine Like Terms”), as a source-bound Shahmukhi Punjabi offline reader and source map. It does **not** contain a translated CNXML `target/` or modular `backend/`, and it must not be counted as CNXML/backend, whole-module or whole-book completion.

## Frozen authority and coverage

- Collection: `col31130`, 82 ordered modules; SHA-256 `5fdc03ab9e6ee7327be72f7e0a17c4d884e65f4a8081a0b2a06dbdb1392bda72`.
- Repository commit: `38cae454e644abf9f0a623e876994553881597c9`.
- Module `m82453`: 184,248 bytes; SHA-256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`.
- Raw section `[89018,108818)`: 19,800 bytes; SHA-256 `87fb85a59b7f6697d19e04c4e0b9e90aa2010d26aa3d8f8e66cc880025bcb147`.
- Wrapped excerpt: SHA-256 `157ce412088dd13ecf8f355ab216b824fa3a219145e10767cae6c060a6f55380`.
- Preserved: 108 source IDs, 253 source bindings, 66 source text/alt blocks, 62 MathML trees, 12 exercises, 12 source-supplied solutions and three byte-identical canonical JPEGs.
- Responsive repair: the page shell fills desktop width; each 594px JPEG fits wholly at 390px without sideways scrolling; three separately marked semantic reconstructions preserve the exact expressions and make them readable at narrow width.
- Expert-review ledger: 14 decisions—13 honest retrospective backfills and one contemporaneous responsive-layout decision.
- Actual audio: absent and not claimed.

## Deterministic QA

- Independent verifier: 1,329 passed checks plus four rejected mutation controls.
- Reader SHA-256: `a9c97aee386fc00bb75890af5760329782b02c63f06a25f3221af1635da4aaee`.
- Visual results SHA-256: `95259048bab8c2cafcbb6b8f3a5abe5a242946fd432a166ec005ed2f397e5989`.
- Visual inspection SHA-256: `d74081007fc1cc5f0942d3fc701b49453655ff00d6e5e26cd7992a5d5c763c80`.
- Payload manifest: 39 files, 3,485,891 bytes; SHA-256 `2d135b00811ed8a9e6969cba4c67b8eb5bf9e69ee5a1d910f2453941a45ace1f`.
- `CHECKSUMS.sha256` covers every payload file plus this handoff and `MANIFEST.json`; it conventionally excludes itself.

Replay from this directory:

```text
python build.py
python visual_check.py
# inspect and bind the regenerated PNGs in visual/INSPECTION.json
python verify.py
python seal.py
```

The next exact source anchor is `fs-id1170654942537` (“Translate an English Phrase to an Algebraic Expression”).
