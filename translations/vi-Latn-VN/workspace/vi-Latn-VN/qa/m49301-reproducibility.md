# m49301 reproducibility boundaries

Read-only inspection on 2026-08-31 of the current U000–U017 package, existing
scripts, locks and receipts. No downloads, rebuilds, source changes or new
license audit were performed. U018 and later work are outside this note.
Code locations below are relative to `vi-Latn-VN/` and describe the inspected
implementation, not a promise about future revisions.

## Reading, rebuilding and matching pixels are different

- **Offline reading:** the eighteen HTML readers embed CSS and image bytes and
  use native MathML. Keep the readers together for their same-directory links.
  No Python, Pandoc, Pillow or downloaded source corpus is needed to read them
  in a compatible browser. External links remain optional and unverified.
- **Rebuilding HTML from Git inputs:** Python 3.12+ and Pandoc 3.10 are the
  documented runtime. `tools/build.py:215–220` invokes `pandoc` from `PATH` and
  compares two runs on the same host; line 280 records its version, but does
  not enforce it or pin the Python/runtime/template environment. Equal local
  runs are not an independent cross-PC reproduction test.
- **Exact appearance:** identical HTML does not imply identical pixels.
  `reader.css:2` uses host font fallbacks; MathML layout also depends on the
  browser and its fonts. The current visual receipts record inspected output,
  not universal browser/font equivalence or native-speaker approval.

## Current Git-only build blockers and source paths

The common builder calls each checker without options (`tools/build.py:262–265`).
U006 unconditionally parses both full modules at
`computing/check_graph_tests.py:70–93`; U007 does likewise at
`computing/check_toolkit_functions.py:110–120`. Those files are under ignored
`downloads/`, so these two builds fail when only Git package inputs are present.
This is a checker dependency, not an offline-reading dependency.

The expected acquired inputs are workspace-relative, not absolute donor-PC paths:

- EN: `downloads/upstream-openstax/modules/m49301/index.cnxml`.
- ID: `downloads/a30-edition/source-core/repo/source/modules/m49301/index.cnxml`.

They agree with `sources.lock.json:96,231`; `tools/acquire.py:14–15,26–31`
resolves paths from the script location. No hard-coded donor workspace path was
found in the eighteen readers' execution scripts/locks. Replaying acquisition is
separate from a Git-only build; it is not necessary merely to open the readers.

U015 also has a third-party dependency in its **normal** build:
`computing/check_technology.py:108` imports `plot_technology.py`, whose line 11
imports Pillow at module scope. Checking the committed PNG hashes therefore
still requires Pillow today, although no font or PNG regeneration is required.

For an empty reader-output directory, build U001–U017 in order and U000 last.
`tools/build.py:157–174,249` requires existing sibling targets. Dependencies are
U008 → U001–U006; U009 → U001/U005/U006; U013 → U006; U014 → U001; and
U000 → all seventeen readers. Keeping the committed readers also supplies
these targets. Main-package `.gitattributes:1–3` preserves LF text and binary
assets across checkouts.

## Original-check modes and assertion counts

Current build receipts total **3,011 mixed assertions**, not mathematical
proofs. Merely having downloaded originals present changes these normal-run
counts. The absent-input figures below are derived from the inspected
conditional branches, not a newly executed Git-only or cross-PC test.

| Unit | No downloaded originals | Current receipt | Conditional code |
|---|---:|---:|---|
| U000 | 100 | 115 | `computing/check_module_guide.py:116–135` |
| U004 | 323 | 329 | `computing/check_input_output.py:135–151` |
| U005 | 13 | 16 | `computing/check_one_to_one.py:39–51` |
| U008 | 96 | 100 | `computing/check_key_summary.py:121–132` |
| U010 | 327 | 338 | `computing/check_algebraic_classification.py:168–200` |
| U012 | 276 | 304 | `computing/check_graphical_functions.py:270–321` |
| U015 | 327 | 343 | `computing/check_technology.py:222–256` |

These checks auto-run when their optional module/media/inherited-rights files
exist. Partial availability can produce intermediate counts. U006/U007 instead
require originals and currently report 111/132; there is no Git-only mode.
U011/U013/U014/U016/U017 use explicit `--originals` branches, respectively at
checker lines 328/145/262/172/148. Their normal builder calls do not enable those
branches. Recorded separate U011 and U013 runs report 445 versus 438, and 140
versus 117. U013's original mode additionally requires both source-media copies
and the inherited component CSV (`check_graphical_injectivity.py:90,158–168`).
No original checks fetch missing material. The full module coverage auditor
itself requires the pinned full EN source (`tools/audit_m49301.py:36–37,185–190`);
it is not a Git-only substitute for that original.

## Materialized CRLF hash profile — not a waiver

The existing EN checkout reports `i/lf w/crlf`, no file-specific EOL attribute,
and inherited `core.autocrlf=true`. Its m49301 file has 202,099 bytes and 4,801
CRLF pairs, with the currently required SHA-256:

`f35932b5b8107fd527d50547adf00d3981860be5d6e981c1238041369b207612`.

Replacing CRLF with LF **in memory only** gives 197,298 bytes and:

`81115d90dd1d9781e65844526bbbfbea638cc6fd515c623c4d535bf3bd0e37e3`.

This explains a possible same-commit failure on an LF host; it does not approve
the second hash, change any pin, or establish equivalence for arbitrary input.
`sources.lock.json:289` explicitly identifies inventory hashes as observed
checkout bytes. `tools/acquire.py:48–55` does not set an EOL profile, while
`tools/verify_sources.py:44–46` checks physical byte size even without `--full`
and hashes with it. The auditor and explicit-original checkers also require
the recorded materialized hash. Main-package attributes do not control the
nested acquired repository. A future repair must explicitly record/replay the
materialization profile or separately bind canonical Git bytes and their
reviewed materialization; silently ignoring mismatches is not acceptable.

## Plot reproduction and visual-QA runtime

Exact U015 PNG reproduction is a separate operation. The committed
`computing/generated-A30-U015/manifest.json:4–6` records Pillow **12.3.0**,
`arial.ttf`, and font SHA-256
`b3658eadae55e682b5f69eb64c439c1ecc8f196c0bb8d4756d145d13bc86476a`.
`plot_technology.py:31–36` falls back from Windows Arial to Linux DejaVu Sans;
that fallback cannot reproduce the recorded Arial bytes. The script accepts
`--font`, checks existing PNG/manifest bytes by default, and writes only with
`--write` (`:123–159`); it has no `--check` flag. FreeType, compression-library
and platform versions are not captured, so Pillow/font identity alone has not
been established as a sufficient cross-platform byte-reproduction guarantee.

`tools/visual_qa.cjs:3,16,20` requires Node and Playwright, hard-codes a Windows
Edge executable, and expects an already running HTTP server on localhost:8765.
It writes screenshots and a pending-inspection receipt (`:13–14,46–51`);
running it is not a read-only audit or automatic renewal of human/model review.
Browser executable/server configuration and runtime/font records would need
explicit treatment for cross-PC visual reproduction.

Small prospective improvements are explicit original-check modes for U006/U007,
lazy Pillow rendering imports, explicit tool/materialization profiles and
configurable visual-QA runtime. None is implemented by this note. Existing
source, semantic, canon and visual reviews remain separately bound evidence;
these reproducibility observations do not prove translation semantics, native
fluency, completion of the other A30 modules or the five-book assignment.
