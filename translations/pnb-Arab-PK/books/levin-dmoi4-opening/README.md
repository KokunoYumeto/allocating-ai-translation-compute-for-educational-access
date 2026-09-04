# ڈسکریٹ ریاضی — شاہ مکھی پنجابی مُڈھلا پیکج

**[پڑھنا شروع کرو — Start reading](index.html)**

Oscar Levin, *Discrete Mathematics: An Open Introduction*, exact fourth edition. Pakistani Punjabi in native Shahmukhi (`pnb-Arab-PK`), with separately marked English/Urdu bridges.

This **complete bounded opening package is not a complete textbook**. It contains the front matter, all of Chapter 0 (Sections 0.1–0.2), the Chapter 1 opening and complete Section 1.1. Next excluded anchor: `source/sec_logic-implications.ptx#sec_logic-implications`, Section 1.2, *Implications*.

## Read offline

Download the directory or [compact release ZIP](https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/raw/refs/heads/codex/additional-translations-review/translations/pnb-Arab-PK/books/levin-dmoi4-opening-pnb-Arab-PK-2026.09.04.zip), extract it and open `index.html`. The three readers use static HTML and native MathML, with local figures and no network scripts, analytics or grading service. A modern MathML-capable browser is needed; Shahmukhi uses the browser's installed Arabic-script fonts. There is no PDF edition in this package.

- [Front matter](reader/b10-frontmatter.html): 50 source-bound text/data slots.
- [Chapter 0](reader/b10-unit-001.html): 157 slots, six original exercises, two unchanged source graphs. No standalone `solution` elements occur; existing response answer conditions and feedback are preserved, not omitted or replaced by invented answers.
- [Chapter 1 opening and §1.1](reader/b10-unit-002.html): 559 slots, including 93 fixed-cache slots; 23 authored exercises, 12 supplied solutions and one hint, plus six separately identified cached WeBWorK snapshots. Snapshots do not exhaust randomized variants.
- [Six new supplementary exercises and worked explanations](support/practice.html): separately authored, never attributed to Levin or substituted for his source questions.
- [Native terminology evidence and bridges](canon/terminology.html): philosophical attestations for some lexical families; remaining formal terminology is explicitly provisional. Urdu is not relabeled Punjabi.

## Faithful source and separate improvements

Canonical English revision: `oscarlevin/discrete-book@82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799`. The recovered Indonesian comparison remains pinned at `e94905932301e699b7c4d44e88ec54e972b886b6`; it is not substituted for the English authority. No completed Indonesian work was restarted.

`frozen/` retains exact hash-verified source excerpts, translation dictionaries, original readers, finite mathematical renderers, selected PG/component witnesses and attribution records from public intake commit `ed6f2e2020118723c2a12fe3377d2273c3d8ec50`. `INTAKE_MANIFEST.json` binds those bytes. Historical descriptions inside those immutable witnesses keep their original scope; the current package status is defined here and in `COVERAGE.json`.

The portable `build.py` replaces obsolete local-checkout dependencies with a source-bound offline adapter. It does not edit frozen inputs. Current readers are checked against the original reader hashes. Source/provenance files are also copied to their reader-relative locations for offline links. These deliberate aliases are byte-identical, not competing editions.

The original source-error notes remain separate and visible: preserved source answer flags are not automatically correct grading keys. One explicitly identified raw-TeX fallback remains in §1.1; all other mapped formulas keep their exact TeX witnesses. This package does not claim universal LaTeX conversion, comprehensive native-reader validation or a settled mathematical terminology standard.

## Reproduce and inspect

Use Python 3.10+ with `lxml` and `Pillow`. Run `python build.py`, `python assemble_support.py`, and `python assemble_canon.py`. Run `python make_archive.py --inventory-only`, then `python validate_package.py` for package links, IDs, math/support checks, provenance separation and the checksum inventory. Finally, `python make_archive.py` reseals the final QA receipt and creates a deterministic ZIP in the sibling `release/` directory; run `python validate_package.py` once more to verify that final seal. It never overwrites a differing existing ZIP. The QA directory records actual checks and visual-inspection scope; inspect their limitations before interpreting a pass as a broader certificate.

## Local learning purpose

This package offers a Shahmukhi secondary-to-undergraduate bridge into the English/Urdu terminology learners may meet elsewhere. Short self-checks route back to the exact source topics. That purpose does not establish alignment with a specific examination board, promise learning outcomes, or complete the wider multi-book programme.

## Credits and rights

Original work: Oscar Levin; original contributor and institution credits are preserved in the front matter. Translation and explicitly new educational support: **OpenAI Codex gpt-5.6-sol, Ultra**, on instructions of the user. No author or institutional endorsement is implied.

See [LICENSE.md](LICENSE.md) and retained component notices. Active book/translation policy: CC BY-NC-SA 4.0, subject to preserved component-specific terms, including OPL notices. External linguistic articles/scans are cited, not republished in full. No author contact, tracking, account credentials or operational conversations are part of the package.
