# Telugu–English mathematics mastery bridge

Open [the offline TE-B001 reader](reader/TE-B001.html). It needs no server, network,
external font or account. A Telugu-capable font such as Nirmala UI or Noto Sans
Telugu improves portability. For a teacher, start with the entry check, use the
skill-specific support, then ask for reasons on both recheck questions per skill.
The rule is editorial, not a validated grade-placement assessment.

## What this checkpoint contains

All source parts of OpenStax *Prealgebra 2e* modulem81243 across ten checked
readers: eight content subsections, glossary and module opening. The first,
`m81243#fs-id1830385`, “Identify Counting Numbers and Whole Numbers”, with
parallel canonical English. It preserves 44 source identifiers and 17 mathematical
expressions. Eight original entry questions, eight rechecks, four supports and
18 worked explanations are clearly separated from the source translation.
The number line is a credited Telugu–English SVG adaptation.

The [TE-B002 offline reader](reader/TE-B002.html), “Model Whole Numbers”, preserves
43 sourceIDs and51 mathematical expressions, with nine Telugu diagram adaptations
and nine retained originals. Its original bridge explains group counts/values,
US dollars, zero positions, and the complete176/237 solutions. Both units have
separate structural, content and rendered QA; see [unit progress](units.json).

[TE-B003](reader/TE-B003.html) covers digit positions and contributions, preserving
two15-column charts and explaining zero's position versus its value. [TE-B004](reader/TE-B004.html)
covers number names, international grouping and zero-filled groups. Each has
four entry items, four rechecks and complete sourceTryIt explanations. See their
[B003 finalcheck](qa/TE-B003.final-check.md) and [B004 finalcheck](qa/TE-B004.final-check.md).

[TE-B005](reader/TE-B005.html) covers writing numerals from names, including
missing groups, zero placeholders and unchangedUSD/miles/pounds. Its
[finalcheck](qa/TE-B005.final-check.md) records22tests and finalvisualinspection.

[TE-B006](reader/TE-B006.html) covers rounding with23adapted diagrams and carry
reasoning. [TE-B007](reader/TE-B007.html) connects the procedures.
[TE-B008](reader/TE-B008.html) covers all58practice exercises,94determined parts,
two open rubrics, five adapteddiagrams and blankself-check. Its
[finalcheck](qa/TE-B008.final-check.md) records195combined regression tests.

[TE-B009](reader/TE-B009.html) contains the glossary; [TE-B010](reader/TE-B010.html)
contains the opening objectives (production numbering is not teaching order).
[Module coverage](qa/m81243.coverage.md) checks2122elements628IDs1188slots.
This is not a single assembled module reader, complete book, validated test or
the entire A00→A10→A20→A30→B10 program.

[TE-B011](reader/TE-B011.html) and [TE-B012](reader/TE-B012.html) are the checked
addition readiness notes. [TE-B013](reader/TE-B013.html) covers addition notation,
including the distinction between reading an expression and finding its value.
[TE-B014](reader/TE-B014.html) covers addition models and value-preserving exchanges,
with19adapted diagrams and complete sourceTryIt reasoning. [TE-B015](reader/TE-B015.html)
is checked: addition properties, aligned column addition, carries and all source
TryIt explanations. [TE-B016](reader/TE-B016.html) covers phrase translation,
[TE-B017](reader/TE-B017.html) covers whole-number applications and perimeter,
and [TE-B018](reader/TE-B018.html) covers the addition recap. [TE-B019](reader/TE-B019.html)
covers all82 source practice exercises with22 adapted diagrams and complete
source/editorial answer classification; all four are editorially checked with
separate final receipts. B020's exact module opening/glossary remainder is the
active integration; see [NEXT_UNIT.json](NEXT_UNIT.json). Modulem81244, earlierPreface/
Introduction, and the full program remain incomplete. Full program translation
is the active goal.

## Source and canon evidence

- [Source lock](sources.lock.json), [course crosswalk](crosswalk/README.md) and
  preserved notices identify acquired repositories, release payloads, exact
  commits, trees and file hashes. A20's active Indonesian release is48/83, not
  the stale28/83 or41/83 checkpoints. B10 is Oscar Levin's DMOI4; Open Logic is
  supplemental and has not been silently substituted for B10.
- Complete pinned OpenStax archives include media and were checked against every
  Git blob. The separate Git checkouts are still sparse. Large inputs remain in
  ignored `downloads/`; use them read-only, without unnecessary copies/extraction.
- [Sixteen starter canon examples plus four topic-specific anchors](canon/examples.json) from two Telangana books have
  selected-page OCR, explicit page anchors and an [actual-use log](canon/CONSULTATIONS.md).
  The [terminology ledger](canon/TERMINOLOGY.tsv) separates TS evidence from the
  unresolved [AP acquisition gap](canon/ap-witness.md).
- Crucial witnessed convention: whole numbers = పూర్ణాంకాలు; integers =
  పూర్ణ సంఖ్యలు. Counting/natural numbers start at1 in this source. Origin and
  coordinate labels remain provisional. No AP–TS difference or state approval
  is invented.
- Read [attribution and adaptation disclosure](ATTRIBUTION.md). These are
  translation/reference inputs, never training or fine-tuning data.

## Build and verify

From the workspace root, Python3.10+ with its standard library is sufficient for
the pilot build and tests. No full corpus is needed for that bounded build.

```powershell
python -B te-Telu-IN/scripts/build.py
python -B -m unittest discover -s te-Telu-IN/scripts -p test_build.py
python -B te-Telu-IN/scripts/build_unit.py TE-B002
python -B -m unittest discover -s te-Telu-IN/scripts -p test_build_unit.py
python -B te-Telu-IN/scripts/build_unit.py TE-B003
python -B te-Telu-IN/scripts/build_unit.py TE-B004
python -B -m unittest discover -s te-Telu-IN/scripts -p test_b003.py
python -B -m unittest discover -s te-Telu-IN/scripts -p test_b004.py
python -B te-Telu-IN/scripts/build_unit.py TE-B005
python -B -m unittest discover -s te-Telu-IN/scripts -p test_b005.py
python -B te-Telu-IN/scripts/build_unit.py TE-B006
python -B te-Telu-IN/scripts/build_unit.py TE-B007
python -B te-Telu-IN/scripts/build_unit.py TE-B008
python -B te-Telu-IN/scripts/build_unit.py TE-B009
python -B te-Telu-IN/scripts/build_unit.py TE-B010
python -B -m unittest discover -s te-Telu-IN/scripts -p 'test_*.py'
```

With the acquired local inputs available:

```powershell
python -B te-Telu-IN/scripts/freeze_sources.py --verify
python -B te-Telu-IN/scripts/seal_archives.py --verify
python -B te-Telu-IN/scripts/seal_canon.py --verify
```

Do not treat a missing large input as permission to redownload every corpus.
`sources.lock.json` provides the exact identity to locate. Canon resealing uses
`pypdf`; OCR regeneration uses Tesseract Telugu+English and Poppler and is not
needed for an ordinary build. Visual QA uses the documented local Edge fallback
in `scripts/visual_qa.cjs`; it expects the reader served on127.0.0.1:8763 and the
existing bundled Playwright path. Per-unit QA uses an isolated local
Chromium-family executable (Edge when present, otherwise installed Chrome).
It is not a browser-portability certification.

## QA, limits and recovery

[Final checks](qa/FINAL_CHECK.md), [build receipt](qa/build-receipt.json),
[render receipt](qa/visual-render-receipt.json), and the
[independent AI-assisted review](qa/independent-review.md) distinguish measured
checks, manual inspection and remaining uncertainty. Fluent-Telugu/native-speaker
review and classroom testing remain open.

The second unit's [final check](qa/TE-B002.final-check.md) and
[independent content review](qa/TE-B002.independent-review.md) identify exact hashes
and scope. `scripts/visual_unit.cjs TE-B002` captures its local desktop/mobile
reader, diagrams, tables and bridge; the same server/runtime conditions apply.

Check disk space and nonempty source files before editing. A disk-full edit once
emptied `translations/bridge.xhtml`; the complete reader preserved it. Restoration
was proved by a byte-identical rebuild before further changes. Do not rebuild
from an empty source. The builder now validates before writes, refuses below32MiB
free and uses atomic per-file replacement for generated outputs; this does not
make the editor's source-file writes atomic.

After restart: read root instructions and the user's current coordinating-task
messages, then [GOAL.md](GOAL.md), [DECISIONS.md](DECISIONS.md),
[STATUS.md](STATUS.md), canon consultations and the next-unit cursor. Verify actual
files/hashes rather than treating a compaction summary as evidence. Keep the
full bridge goal active after this pilot checkpoint.
