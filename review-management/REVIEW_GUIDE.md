# Review the additional translations on another PC

## Newly reported review erratum — Tamil

The Tamil owner reports on 2026-08-31 that a missing number-line arrowhead also affects historical U001 renditions included in checkpoint `6f86c768391dc52dfdbecaa843412772cfb0ba9c`. Treat these as known-erratum review copies, not production-cleared diagrams. The owner is repairing the full-module PDF/diagram workflow; those changing fixes are not included in this snapshot. The export preserves the original saved bytes and historical QA without asserting that earlier review found this later-discovered defect.


Use **one checkout** of `codex/additional-translations-review` in the allocation-report repository. It contains actual exported translation files for all nine locales; nine separate clones are unnecessary. This is a continuing **review branch**, not a production release or a claim that any whole assignment is finished.

## Download and verify the captured snapshot

Run these commands in a new, empty destination, not an active translation workspace:

```sh
git -c core.autocrlf=false clone --single-branch --branch codex/additional-translations-review https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access.git additional-translations-review
cd additional-translations-review
git config core.autocrlf false
git rev-parse HEAD
git status --short
python -m json.tool translations/EXPORT_MANIFEST.json
```

Compare HEAD with the coordinator's latest verified publication receipt. Read the [translation index](../translations/README.md) and [export manifest](../translations/EXPORT_MANIFEST.json). The manifest, not an earlier inventory or message, identifies the actual per-locale checkpoint and included files. Worker Git histories are not merged into this repository; the manifest preserves their original commit/blob identities while transferring the selected file content.

The following read-only check uses Python 3.9+ to verify every listed exported file against `export_sha256`, rejecting paths outside `translations`. It does not validate unlisted files, translation quality, authenticity of the manifest or build reproducibility:

```sh
python -c "import hashlib,json,pathlib,sys; root=pathlib.Path('translations').resolve(); manifest=json.loads((root/'EXPORT_MANIFEST.json').read_text(encoding='utf-8')); bad=[item['path'] for item in manifest['files'] if not (root/item['path']).resolve().is_relative_to(root) or not (root/item['path']).is_file() or hashlib.sha256((root/item['path']).read_bytes()).hexdigest()!=item['export_sha256']]; print('Export SHA-256 mismatches:',len(bad)); sys.exit(bool(bad))"
```

## Preserve the workspace nesting

Every locale is exported as `translations/<locale>/workspace/<original-prefix>/...`. Builders often derive a workspace root by parent-directory depth, so do not flatten the extra `languages/` level or remove workspace-level byte-preservation attributes.

| Locale | Original prefix inside its workspace | Review and rebuild limits from the initial inventory |
|---|---|---|
| `bn-Beng-BD` | `bn-Beng-BD` | Committed HTML/assets and historical offline ZIPs are reviewable; older ZIPs omit newer modules. Full rebuild needs pinned source/canon inputs plus the Python/font environment. PDF identity is environment-dependent. |
| `te-Telu-IN` | `te-Telu-IN` | Frozen-input HTML/CNXML builds use Python 3.10+ standard library. Acquisition/canon QA needs ignored inputs and document tools. Configure Playwright/browser paths for visual scripts; full clean-PC replay remains untested. |
| `bn-Beng-IN` | `languages/bn-Beng-IN` | Bounded frozen-module/media builds use Python 3.12+. Keep required `build_sections.py`; its donor fallback is for unfrozen media, not a reason to drop the builder. Acquisition needs exact inputs; transformed-builder hashes differ from original QA. |
| `vi-Latn-VN` | `vi-Latn-VN` | HTML reads offline. Builds use Python 3.12+/Pandoc 3.10; U006/U007 require pinned EN/ID module XML even for BUILD. U015 checking needs Pillow; exact image recreation also depends on recorded fonts/runtime. |
| `mr-Deva-IN` | `mr-Deva-IN` | HTML builds use Python 3.11+ standard library and committed witnesses/assets. Refreezing/full source QA needs pinned archives. PDF work needs ReportLab/pypdf/uharfbuzz and fonts; approved PDF scope does not certify separate HTML/accessibility issues. |
| `ta-Taml-IN` | `ta-Taml-IN` | Committed source/HTML/EPUB uses Python 3.11+ standard library. PDF production and QA need browser/document tools. Timestamp-bearing PDF regeneration is not promised byte-identical. |
| `pnb-Arab-PK` | `languages/pnb-Arab-PK` | PNB/A10 builds use Python 3.12 standard library; B10 additionally uses Git/lxml/Pillow. Full prepare/QA needs pinned ignored inputs; complete fresh-PC replay is not established. |
| `jv-Latn-ID` | `languages/jv-Latn-ID` | Saved readers/assets work offline; full draft/build/QA needs Python 3.12 and pinned inputs/canon. Sanitizing `sources.lock.json` changes its hash, so lock-bound validators need reviewed derivative rebinding. Register tracks and SSML/transcripts are not extra modules or recorded audio. |
| `gu-Gujr-IN` | `gu-Gujr-IN` | Offline library is present; full rebuilding needs four pinned repositories, release XML and canonical media. A two-release helper is not a complete bootstrap. PDF/visual QA has additional font, Python, Node/browser and document-tool dependencies. |

For example, the Indian Bengali workspace is `translations/bn-Beng-IN/workspace`, with its lane README/tools under `languages/bn-Beng-IN`. Run a lane's documented commands from the directory its scripts expect, not automatically from the outer repository root. Read the exported README, current goal/cursor, source locks and scoped QA first; inspect any executable transformation in the manifest before rebuilding.

For optional local HTML review, serve only the export tree and choose a reader from the index:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory translations
```

Open `http://127.0.0.1:8000/` in your browser; stop the server with Ctrl+C when finished. A page loading successfully is not a linguistic, mathematical, native-educator or accessibility approval.

## What the hashes and readiness labels mean

The initial exporter captures immutable saved commits, which can themselves contain unfinished drafts. Newer dirty/untracked work is omitted until a consistent boundary is available; omitted work remains with its owner and is not lost. Consult `uncommitted_paths_not_exported`, exclusions and limitations rather than interpreting file counts as completed translation volume.

`source_commit`, `source_blob` and `source_sha256` identify original checkpoint bytes. `export_sha256` identifies delivered bytes. Privacy sanitization or executable parameterization creates a **derivative export** and is listed under transformations. Original QA may attest unchanged readers or original builders; it does not silently certify modified builders/locks. Preserve historical receipts and validate/rebind derivatives separately. Do not rewrite canonical source witnesses or erase genuine source UUIDs to make a check pass.

Ignored bulk source and target-language canon collections are intentionally not duplicated. Restore only inputs required by the selected lane's **exact source locks**, not whatever is currently `main` or “latest.” [Upstream findings](UPSTREAM_CHANGES.md) identify candidates; they are not adopted worker pins. Continue consulting readable target-language canon and mathematical witnesses during review, revision and further drafting. Review unfinished work honestly without treating pending human review as a requirement to stop useful drafting.

## Receive later updates safely

First inspect `git status --short`. If there are local edits, preserve them and coordinate ownership before updating; do not reset, overwrite or blindly stash them. In a clean review checkout:

```sh
git fetch origin codex/additional-translations-review
git log --oneline HEAD..origin/codex/additional-translations-review
git diff --stat HEAD..origin/codex/additional-translations-review
```

After reviewing the incoming scope, fast-forward only:

```sh
git merge --ff-only origin/codex/additional-translations-review
git rev-parse HEAD
```

If fast-forward fails, stop and resolve the divergence with the coordinator; do not force-push or merge unrelated histories. Recheck the manifest and selected readers, and record review findings against the exact exported commit. Agree which PC owns further edits to a locale. This review branch does not authorize a production release, a merge to `main`, or deletion of originating work.
