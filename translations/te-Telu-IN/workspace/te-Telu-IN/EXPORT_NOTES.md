# Review-branch export and portability

The coordinator owns publication to the single ongoing
`codex/additional-translations-review` branch. No main merge, final production
release, native-speaker approval or whole-assignment completion is implied.

At this snapshot B001–B014 are editorially checked. B015 is a complete source
translation and generated reader with independent arithmetic checks, but main
full-content/final-visual approval is pending. `units.json` and per-unit final
receipts identify checked scope; an existing reader file alone is not approval.
Newer B016 work is outside this checkpoint and must not be captured mid-edit.

All offline readers and their linked frozen fragments, original/SVG assets,
catalogs, bridges, notices and review records are inside `te-Telu-IN`. Open the
HTML files directly with a Telugu-capable font; no server/account/network is
required. Keep the folder hierarchy and existing file bytes unchanged.

Ordinary unit generation uses Python's standard library, the checked-in source
fragments/catalogs/assets and source-lock records. It does not need the full
upstream archive. For example, from the containing project directory:

```powershell
python -B te-Telu-IN/scripts/build_unit.py TE-B014
```

Full source/asset provenance replay, additional source selection and actual
canon rereading also require ignored inputs under workspace-root `downloads/`,
not under this locale folder: pinned source checkouts/ZIPs, Telangana Class2
and Class6 PDFs, and the selected OCR/PNG records in `canon/lock.json`. Their
paths, hashes and sources are recorded; they are not secretly bundled here.
Do not claim a full archival/canon replay from the locale export alone.

`scripts/visual_unit.cjs`, older visual scripts and asset author-render helpers
contain this PC's absolute Playwright runtime path and use isolated headless
Edge. Screenshots/receipts bind the recorded bytes and local rendering, not
portable runtime discovery. Adapt a separate replay configuration and rerun QA
on another PC; do not silently rewrite a hash-bound script and reuse its old
receipt as proof of a fresh run. No signed-in browser profile is required.

Root raw user-instruction snapshots, chats, account/configuration files and
unrelated work are not part of the locale export. Local paths in provenance
and QA are historical technical records; no credentials are intentionally
included. Coordinator should retain its own exclusion/snapshot manifest.
