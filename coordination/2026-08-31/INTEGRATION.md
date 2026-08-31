# Receiving-PC integration

## 1. Obtain the coordinator packet

Use a **new, empty destination**. The branch is in the existing allocation-report repository:

```sh
git clone --single-branch --branch codex/language-allocation-handoff-2026-08-31 https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access.git language-allocation-handoff
cd language-allocation-handoff
git rev-parse HEAD
python coordination/2026-08-31/validate.py
```

Compare HEAD with the remote commit reported by the originating coordinator. A local hash manifest detects changed files but is not independent proof of authenticity. Python 3.9+ is sufficient for this packet's validator; no packages, credentials, downloads or source archives are used by it.

Read [README.md](README.md), then [CHECKPOINTS.json](CHECKPOINTS.json) and [ISSUES.md](ISSUES.md). The remote research base is `975a3435f611792ef30a0908e0ba54b23a0e229a`. This additive directory does not modify the original paper or its root release checksum inventory. If integrating into another checkout, first inspect its uncommitted work and review the coordination-only diff; do not overwrite existing files blindly.

## 2. Understand what is not transferred

The nine worker commits are **local-only checkpoints in separate worktrees**. This branch carries neither those Git objects nor their translations. Their relative evidence locators will not resolve in this coordinator checkout. An indexed SHA, lock filename or completed task message is not a transport mechanism.

Ignored canonical archives, extracted media, target-language canon corpora, private instructions and operational logs also remain outside this packet. The original working trees are dirty and may now be ahead of the snapshot. Do not try to fetch their SHAs from this public repository or claim that this checkout resumes translation by itself.

## 3. Later worker-content transfer

When the user selects worker-content transfer, agree on locale, checkpoint and destination with the owning task. Keep uncommitted work distinct. Two possible transports are a reviewed locale-owned file export with a checksum manifest, or a private Git bundle with its included history explicitly reviewed. Neither is created by this coordinator-only step.

Do not blindly publish the complete local worker branch: its history may include unrelated private coordination files. The local production history and this research repository have different roots; an unrelated-history merge is not a substitute for a scoped export.

Include the selected translation sources, readers/assets, build scripts, source/canon locks, provenance, QA receipts, goal, decisions and next cursor as appropriate. Handle the original private instructions through a private channel. Verify transferred bytes before using them. Preserve source notices and exact pins; do not start another general source/license audit.

## 4. Rebuild according to the actual checkpoint

| Locale | Bounded handoff expectation |
|---|---|
| bn-Beng-BD | Restore pinned ignored source inputs and documented Python/fonts. Existing offline reader/package is distinct from fresh buildability; PDF byte identity is environment-dependent. |
| te-Telu-IN | Main HTML/CNXML rebuilders use committed frozen inputs and relative paths; clean-PC replay is not yet tested. Full acquisition/canon QA needs ignored pinned downloads. Visual QA hardcodes a host Playwright path and Edge, requiring receiving-PC runtime configuration. |
| bn-Beng-IN | Lane reports an independent 87-output Git-archive replay of `35b8743` with donor/download roots absent. That bounded checkpoint is not the newer four-module working state. |
| vi-Latn-VN | Existing HTML works offline; Python/Pandoc builds and full U006/U007 source QA have separate requirements, including ignored pinned originals. |
| mr-Deva-IN | Committed HTML builds with standard-library Python. Source refreeze/archive checks require pinned inputs. PDFs additionally depend on ReportLab/HarfBuzz/Windows Nirmala; HTML access/QA remains separate. |
| ta-Taml-IN | Source/HTML/EPUB builds are self-contained with standard-library Python. PDF export needs Chromium/Poppler/documented libraries; timestamp-bearing PDFs are not promised byte-identical. |
| pnb-Arab-PK | Full clean-machine replay not established here; inspect the lane source/provenance locks and its selected reader before a broad rebuild. |
| jv-Latn-ID | Committed readers/assets are offline-viewable; full build needs restored pinned inputs and canon. No independent clean-machine replay yet. Historical donor metadata cleanup belongs to the lane. |
| gu-Gujr-IN | Offline output is self-contained. Full build needs four pinned repositories, release authority and canonical media; a complete one-step bootstrap is not yet available. PDF also needs ReportLab/uharfbuzz. |

[Sources](SOURCES.md) provides shared public source URLs, recorded sizes/hashes and version qualifications. Consult each transferred lane lock for further source/tool requirements. Restore only the inputs required for the chosen checkpoint. Keep this as acquisition/reproduction work, not an excuse to replace approved artifacts or rerender everything.

## 5. Verify and resume

Open a bounded known reader and compare its source boundary, output hashes and recorded checks. Distinguish exact unchanged artifact verification from a successful new structural/content build; use each lane's declared reproducibility standard.

Before editing, read the actual full goal, user direction, recent decisions, canon consultation records, source locks and next cursor. Verify that the cursor agrees with the transferred files and checkpoint. Apply [SOURCE_CORRECTIONS.md](SOURCE_CORRECTIONS.md) at the exact A20 witnesses when relevant. Assign future work explicitly to avoid two PCs editing the same locale files without coordination.

Record the chosen transfer method, received identity, missing inputs and first validated checkpoint in an external log on the receiving PC. No deletion of originating work is justified merely because the coordinator branch exists.
