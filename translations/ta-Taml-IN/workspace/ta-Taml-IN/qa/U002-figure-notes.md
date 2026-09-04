# U002 figure redraws — 2026-08-30

Status: nine authored SVG drafts, structurally checked; not yet admitted to a reader edition or visually checked after rendering. The current U001 edition is unchanged by this work. Only `assets/u002/` and this note were authored by the figure subtask. No download, source copy, cleanup, commit, builder change, or table rasterization was performed.

## Evidence consulted

- Read the actual English CNXML subsection `m81243#fs-id2340048`, including every image description and surrounding mathematical context, from `provenance/m81243.en.cnxml`.
- Viewed all nine original JPEGs in `downloads/osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`. The upstream source pin is `openstax/osbooks-prealgebra-bundle@38cae454e644abf9f0a623e876994553881597c9`.
- Read `canon/README.md`, `terminology.tsv`, and actual Tamil OCR `downloads/tamil-canon/ocr/page-020.txt`; then viewed `page-020.png` to resolve OCR noise. The SCERT 2018 reference (PDF page 20 / printed page 14) directly supports “இடமதிப்பு”, “இலக்கங்கள்”, and “ஒன்றுகள்”. Its table abbreviates the hundreds/tens/ones headings as நா / ப / ஒ; it is not claimed as direct evidence for every full phrase in these redraws.
- Rechecked those labels during final textual review. The translator's selected register is நூறுகள் / பத்துகள் / ஒன்றுகள். The visible label “1 நூறு” uses the grammatical singular, explicitly confirmed with the parent task; other count labels use “3 பத்துகள்” and “8 ஒன்றுகள்”. The initial provisional rod term was “சட்டம்”; the follow-up below replaces it with the translator/ledger's “பட்டை”.

## Design and fidelity decisions

- Each SVG has its own `u002-fNNN-` IDs, Tamil title/description, `role="img"`, `aria-labelledby`, and `lang`/`xml:lang="ta-Taml-IN"`. Visible drawing groups are hidden from accessibility traversal to avoid duplicate narration after the image description.
- The declared typeface is `TamilBook, 'Nirmala UI', sans-serif`. SVGs contain no embedded font and no remote resources. The integrating offline reader must retain its existing bundled TamilBook font and check font inheritance in its actual embedding mode.
- Money photographs were replaced by separate schematic denomination cards, all countable: 3 × $100, 7 × $10, 4 × $1. Dollar values were not converted to rupees. Card labels and the source equations remain explicit. The next diagram preserves $300 + $70 + $4 → $374.
- Base-ten diagrams preserve one unit as a square cell, each rod as 10 equal cells, and each hundred as a 10-by-10 grid. Outlines are dark against pale fill; shape boundaries do not rely on colour alone.
- Expansion diagrams preserve 100 + 30 + 8 → 138 and 200 + 10 + 5 → 215. Arrows connect each leading place-value digit with its corresponding digit below. Dark teal arrows and dark red digits replace the source's pale cyan/red; the same lower digits are also coloured. Explicit connections and descriptive text convey the mapping without colour perception.
- Exercise-model files `_007_img`, `_009_img`, and `_010_img` remain visibly unlabelled. Their titles/descriptions describe the countable objects but do not disclose the answer totals. Counts are accessible so a learner using the description can solve the same task. No hidden answer string was added to these files.
- Original tables remain the responsibility of the semantic CNXML/HTML translation. None was converted to an image.

## Checks actually completed

PowerShell XML parsing and explicit assertions passed for all nine files: unique IDs across the set, resolved local `use` references, resolved accessible label IDs, correct locale/role, zero visible text nodes in the three unlabelled exercises, and absence of the three answer totals from their titles/descriptions.

Geometry/count checks passed: `_004` contains 1 hundred grid / 1 rod / 1 unit; `_005` contains 1 / 3 / 8; `_007_img` contains 2 / 1 / 5; `_009_img` contains 1 / 7 / 6; `_010_img` contains 2 / 3 / 7. Reusable hundred definitions have nine interior vertical and nine interior horizontal divisions; reusable rod definitions have nine interior vertical divisions. The direct `_004` grid and direct rods were also read against the source geometry. The money diagram has 14 cards with exactly 3, 7, and 4 denomination labels. The initial nine SVGs totalled 17,989 bytes before the term-alignment edit.

## Follow-up: rod terminology and read-only CNXML review

On the parent task's request, replaced every SVG occurrence of the provisional “சட்டம்” family with “பட்டை” and its grammatical forms: பட்டையில், பட்டைகள், பட்டையும். The visible `_004` label is now “ஒரு பட்டை”. This aligns the drawings with ledger term “பத்துகள் பட்டை” and the Tamil subsection. No geometry, numerical content, IDs, or exercise-label policy changed. “1 நூறு” remains unchanged.

For this revision, actually read OCR page 175 and viewed its PNG: the glossary's Tamil entry for “Horizontal bars” supports the word பட்டைகள் as shape vocabulary. It does not establish the full compound பத்துகள் பட்டை as an official term for this manipulative, so that compound remains provisional. The existing ledger and actual U002 Tamil CNXML were read again.

Read-only comparison of the Tamil subsection with the nine original figures found no mismatched quantities or rod/place-value terminology after this SVG alignment. Money is 3 × $100 + 7 × $10 + 4 × $1 = $374; block examples are 1 / 3 / 8 and 2 / 1 / 5; practice diagrams are 1 / 7 / 6 and 2 / 3 / 7. The five-column table descriptions correctly describe the actual tables, unlike the stale three-column English descriptions.

Two adaptation-description issues remain for the integrating task (CNXML was not edited here): `fs-id1302206` still describes three stacks of American banknotes, whereas the redraw uses separate schematic denomination cards; `fs-id2438560`, `fs-id2387933`, and `fs-id2164193` still say all other parts are black, whereas the redraw also colours the lower matching digits dark red and uses dark teal arrows. Their quantities and mappings are correct. Update those media alternatives to describe the delivered redraw, retaining the original description in provenance and logging the adaptation.

After term alignment, repeated the XML, global-ID, internal-reference, accessible-label, answer-concealment, money-count, model-count, and reusable-grid-partition assertions: all passed. No “சட்ட” substring remains in the SVG text. The nine revised SVGs total 17,977 bytes. The reviewed Tamil CNXML SHA-256 was `a0d56878deb6f36694bf5c54a8aa12710166bbf9a36d758497ece0220360d80b`; its complete ordered sequence of 52 MathML number/operator tokens matched the English subsection. Dollar amounts and the two plain-text practice answers were also compared directly. This token check does not replace the pending rendering or linguistic review.

Pending: render and inspect every redraw in the integrated reader/PDF; check Tamil shaping, label fit, narrow-screen legibility/zoom, monochrome print, and EPUB reader compatibility for local SVG `href` references. No claim of native-speaker review, screen-reader testing, PDF/UA compliance, or completed visual QA is made here.

## Original JPEG SHA-256 witnesses

Basenames share the prefix `CNX_BMath_Figure_01_01_`; SVGs use the corresponding basename with the `.svg` extension.

| Original suffix | SHA-256 |
|---|---|
| `002.jpg` | `007532818bb67ba0754435efccaf5f480b91d6366cff2d07b820cc9186b2272d` |
| `003_img.jpg` | `0ed09418807f7a0778f07bd7491268e792ad8b0d9cc96f8ffe70e0e2dc1f2152` |
| `004.jpg` | `93336e96ea80a342a62263c3a942257a8c4d361fc05bbe7de3493f3e96bc84fa` |
| `005.jpg` | `44a3c6e2611521c0fb1883b1ee54173c3128c369d346068b9fe5d78819ce89a4` |
| `006_img.jpg` | `2d1a8d3d4fcb3903880593ce92b5506d9c273a0823966f2ce4da1c7da8d382d1` |
| `007_img.jpg` | `8ac7fcdff5bbb89eedc742e629ed0d57561610007aecf5f525f73d1656d3e95b` |
| `008_img.jpg` | `121065cc1a56bb8d97b45a4a75ad36819547ea50113552d42afd5601d4e907be` |
| `009_img.jpg` | `e33ca96ab80e2e9264b7ec44dcd24ffb2928352df334f85ba022f2590ed7d4d4` |
| `010_img.jpg` | `d00b417fbea7a63d71ad43fd4b7291e08610d1098885fd6ddc31494f7a99722c` |

The C: preflight reported 1,416,073,216 bytes free; the later check reported 1,312,911,360. No storage threshold failure occurred during this subtask. Existing sources were read in place.
