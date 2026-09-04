# Gujarati Elementary Algebra 2e: recovered A10 reader checkpoint

Open **index.html** after downloading/extracting the whole folder. The reader,
Gujarati font, mathematical notation and figures work offline. External source
hyperlinks are optional. No account, analytics or scripts are used by the reader.

This is **13 of 82 A10 modules, not a complete Gujarati book**: m82630 and
m82451–m82462. It includes 1,807 source exercises, 1,135 source-supplied
solutions, four recovered separate companions with 171 added answers, and a
new separate 41-answer m82456 fraction companion. A00 material is excluded.

The new companion contains all 41 source-omitted answers for m82456, four
countable diagrams, a short skill-based learning route and three diagnostic
questions with feedback. Open responses are labeled authored examples. The
original source XML, original figure identities and original supplied answers
are not overwritten. The recovery also preserves the previously localized
fraction figures; those are not claimed as newly authored work.

Use **PACKAGE.json** for bounded scope and next anchors,
**ANSWER_RECONCILIATION.json** for exercise/answer/figure identities,
**SOURCE_INVENTORY.json** for source/export hashes, and **QA.json** plus
**BROWSER_QA.json** for the actual checks and their limits.

Content is CC BY-NC-SA 4.0 subject to inherited component notices; the bundled
font is SIL OFL 1.1. See attribution.html and LICENSE.txt. Source and translation
inputs are not a model-training or fine-tuning dataset. No OpenStax endorsement,
native-speaker certification, recorded audio or PDF/UA certification is claimed.

## Rebuild

The standalone reader needs no build. To reconstruct this exact bounded input
selection, run `python -X utf8 scripts/build_package.py PATH_TO_RECOVERED_EXPORT`
with Python, BeautifulSoup4 and SymPy. The export must match the manifest hash
recorded in PACKAGE.json. Canonical XML is fetched only from the pinned OpenStax
commit and checked against the inherited authority manifest; existing valid
local copies are reused. No legacy full-lane builder, TeX or Lean is launched.

For browser checks, make Playwright available to Node and run
`node scripts/browser_qa.cjs` with Chrome installed. The script checks desktop
and phone geometry, local fonts and images, and records bounded screenshots.
Rebuilding resets visual QA until it is rerun and visually inspected.

Remaining book work: 69 A10 modules, additional omitted-answer companions and
book-local support. Next canonical module: m82463. Next support unit: m82457.
