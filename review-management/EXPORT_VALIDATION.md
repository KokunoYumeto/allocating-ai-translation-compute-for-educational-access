# Translation review export: bounded validation

Date: 2026-08-31. This report describes the prepared review export, not a production release or a claim of linguistic approval. Publication and remote-branch verification are separate steps.

## Validated checkpoint

- Manifest: `translations/EXPORT_MANIFEST.json`.
- Manifest SHA-256: `21b4c59bd17e8c6d3e3f40036a0c3c19e22741602da10b11babbddecbb803265`.
- Scope: nine language lanes, 4,380 indexed files, 190,142,459 exported bytes.
- The manifest remained unchanged throughout the independent data scan and at the final write-guard check.

## Passed checks

- Every indexed file's byte count and SHA-256 matched the manifest. All 844 JSON files parsed successfully.
- UTF-8-decodable exported content contained no matches for the checked local-home path patterns, task-ID patterns, or the two known raw conversation passages, including whitespace-wrapped variants. Matching fragments intentionally present in the exporter's detection code are not exported conversation records. This is a bounded marker scan, not an exhaustive secrets audit.
- Six embedded archives were inspected: two Bangladesh Bengali offline ZIP packages and four Tamil EPUBs. No checked privacy markers were found in their inspected text members. Archive inspection found no nested archives or unsafe member paths in this checkpoint.
- Both Bengali ZIP packages' active manifests matched their current member bytes: 56 and 144 listed entries respectively. Their retained historical manifests matched the original-manifest hashes recorded in the repaired active manifests. The historical manifests are explicitly historical, not current integrity attestations.
- The exporter reports 197 HTML readers and 1,011 checked local image, script and stylesheet/link references. The coordinator independently confirmed that all 197 HTML readers are byte-identical to their pinned originals and that all 4,380 staged Git blobs match the export manifest.
- The known portable code transformations passed syntax and idempotence checks against ten pinned original scripts. Archive repair was also tested in memory against the two actual Bengali manifest schemas.

## Write-safety checks

Nine pure mocked cases passed against the final exporter. Known review edits, unregistered existing destination content, paths outside the output namespace, symbolic-link ancestors and Windows junction ancestors were rejected. Safe previous-hash updates and new files were allowed; identical bytes required no write. Explicitly designated generated management outputs remained writable by design.

These tests did not create fixtures, modify worker files or execute translation builders. Generated management files are exporter-owned: their explicit overwrite allowance is not protection for manually edited generated reports. The checks do not establish transactional or concurrent-writer safety.

## Remaining limits

- No complete clean-PC rebuild, browser run, native-language review, educator review or assistive-technology review was performed for this validation. Draft and ready-to-read distinctions in the lane records remain in force.
- The HTML resource check does not cover CSS `url()` references, `srcset`, all anchors, visual layout or accessibility. Binary metadata and arbitrary secret formats were not exhaustively audited.
- Ignored bulk source and canon inputs are intentionally absent. Full acquisition, PDF generation and some QA workflows still require the pinned inputs, fonts and runtimes documented by their lanes. Committed offline readers can have a narrower dependency boundary than full rebuilding.
- Portable code and provenance transformations change bytes. Original QA hashes attest the original checkpoint, not transformed derivatives. In particular, hash-bound Javanese source-lock validation still requires reviewed derivative rebinding before a full rebuild. The repaired ZIP manifests attest their exported member bytes; they do not imply translation QA was rerun.
- This result applies to the manifest digest above. Later lane commits or export changes require renewed checks. No production approval, merge or remote publication is asserted here.

No concrete blocker was found within this bounded export-integrity, known-marker and write-guard review.

