# A10 equality and inequality continuation — translation draft

Date: 2026-08-30. This is a bounded continuation of the still-active full
A00/A10/AX-2 assignment, not assignment completion. Javanese mathematical
register, educator, diagram-listening, and voice review remain pending.

## Actual source read and exact boundary

Read all 53 direct children of actual pinned Indonesian and English section
`m82453/fs-id1170655150800`, including all text, MathML-derived text, accessible
descriptions, exercises, and solutions, before choosing the boundary. The local
Indonesian file was byte-compared with its member in the existing A10 v1.0.2 ZIP.

- Indonesian file: `downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml`,
  SHA256 `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635`.
- English file: `downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml`,
  SHA256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`.
- Indonesian release commit: `11754719d8eab8de63d5340ad35824e8be8d99e4`;
  canonical upstream commit: `38cae454e644abf9f0a623e876994553881597c9`.

Include direct children `[13:23]`, zero-based with the section title as child 0:

1. spacing-only `para fs-id1171789687379`;
2. equality introduction `para fs-id1170655208137` (`term-00010`);
3. equality definition `note fs-id1170655025665`;
4. number-line comparison introduction `para fs-id1170655108736`;
5. inequality/number-line definition `note fs-id1170655207857`;
6. direction/reversal explanation `para fs-id1170655155145`;
7. five-relation table `table fs-id1170655178120`;
8. worked translation example `example fs-id1170655113222`;
9. first Try It `note fs-id1170654935250`;
10. second Try It `note fs-id1170655124058`.

This slice has 10 direct children, 35 IDs, and 23 MathML expressions. Stop after
`fs-id1170655124058`. The exact next child is grouping-symbol introduction
`para fs-id1170654957487`; no grouping/expression/equation/exponent material is
claimed complete. The selected span is coherent because it teaches all five
relations and includes the worked example plus both attached practice checks.

## Canon read during drafting

Reread actual readable entries C09 `kiwa`, C10 `tengen`, C11 `luwih`, C12
`gedhé`, C13 `cilik`, C15 `tetep`, and C16 `saka`. They directly support left,
right, more/greater, large, small, stable/equal-adjacent discussion, and
left-to-right source/direction syntax. They do not attest the full mathematical
compounds or comparison sentences below.

- Use `luwih cilik tinimbang` and `luwih gedhé tinimbang` to distinguish
  relations from arithmetic subtraction. `cilik`, `gedhé`, and `luwih` are
  attested; the whole comparison frames and `tinimbang` still require targeted
  confirmation.
- Use `padha karo` for equals and `ora padha karo` for not-equal. No dedicated
  equality entry exists on the current shelf; these are transparent provisional
  pedagogical phrases, not claimed standardized compounds.
- Keep academic title `Pertidaksamaan` as an overt Indonesian mathematical loan.
  The conversational `Bandhingan Ora Padha`/`Tandha Bandhingan` is a descriptive
  scaffold, not asserted canon terminology.
- Existing arithmetic reading decisions continue: `ditambah`, `dikurangi`, and
  division `dipara`; exact formula narration remains source-bound. The newly
  acquired official `para` entry supports the division family, not every sentence.

## Translation and source-fidelity decisions

- Academic prose uses `nduweni`, `disambungake`, `digunakake`, `njlentrehake`,
  `mapan`, `lumrahe`, and `padha tegese`; conversation uses `yen`, `jenenge`,
  `dienggo`, `ana`, `biasane`, and shorter labels. Both are Latin-script ngoko /
  provisional academic Javanese, not krama.
- Javanese exercise instructions explicitly request a Javanese sentence and say
  that the source is Indonesian. This is a declared bilingual pedagogical
  adaptation, not an invisible change to the retained Indonesian source track.
- The source differentiates mathematical equality (`padha karo`) from logical
  equivalence under reversing a comparison (`padha tegese karo`). Do not replace
  the latter with an equals glyph or claim that `a<b` and `b>a` are two separate
  facts. Preserve operand reversal exactly.
- Preserve the five relation symbols `≠`, `<`, `≤`, `>`, and `≥`; the two
  number-line diagrams preserve point order a-left-of-b and b-left-of-a.
- In exercises, translate expressions linearly without evaluating or altering
  them. Preserve all four parts, IDs, values, variables, operators, answers, and
  source hierarchy. Part markers are labels, not variables.
- Indonesian plain-text `<` and `>` occurrences and the table's plain emphasized
  `a < b`/`a > b` are source notation too, despite not being MathML. They require
  source-bound prose narration and structural/numeric checks.
- `Panyelesaian`/`Cara Ngrampungake` deliberately match the established pilot.
  Untitled Try It solutions need the existing explicit spoken answer cue only;
  do not add visible source titles.

## Integration requirements

- Preserve all 35 IDs, exact element hierarchy, 23 MathML trees and attributes,
  all plain comparison glyphs, two image sources/alts, the relation-table rows,
  all exercise/answer pairs, and the next-source boundary.
- Add explicit mappings for MathML `mtable`, `mtr`, `mtd columnalign="left"`,
  empty source rows, and operators `=`, `<`, `>`, `≠`, `≤`, `≥`, `−`, `÷`, `+`.
  Never flatten an unsupported tree. The large mtable fixtures include prose and
  spatial explanation; they are not generic matrix narration rules.
- Spoken number-line descriptions must not require inference from a silent image.
  Describe point order and its relation to less/greater, while preserving the
  visible source geometry. Actual visual/geometry review is separate.
- All source-derived narration needs finite exact fixtures in
  `audio/a10-equality-symbols.rules.json`. No generic inequality parser is
  authorized. No voice-provider, synthesis, listening, or WCAG claim is made.

## Revision-stage canon and draft QA

After drafting, reread the same C09–C13/C15–C16 entry lines against the Javanese
phrases. Confirmed that left/right and greater/smaller wording retains the
attested headword senses; no full mathematical-standard claim was added.

Read-only draft checks passed:

- 44 unique phrase rows exactly cover all 44 unique translatable source strings
  in the selected children, including `alt` and `aria-label`; there are no
  missing or extra keys. All five declared unchanged identifiers occur.
- Every phrase row has three nonempty fields. Source/academic/conversation
  numeric token sequences match. The two keys already present in the pilot,
  `disebut` and `Penyelesaian`, have identical existing translations; there are
  no shared-phrase conflicts.
- The selected source inventory is 35 unique IDs and 23 MathML expressions.
  All 23 fixtures cover exactly one `(anchor, one-based ordinal)` pair and match
  the actual namespace-aware source tree, including empty `mtr` elements and
  `mtd columnalign="left"` attributes.
- Every fixture has all three nonempty expected-reading tracks. Worked problem,
  repeated worked solution, Try It answer, number-line direction, reversed
  relation, symbol, value, and operand-order checks agree with the source.

These checks are evidence for draft structure only, never language approval or
full A10 completion. Production integration still needs the unit declared in
the shared configuration/builder, plus explicit support for the registered
`mtable`/`mtr`/`mtd` source layouts and relation operators. Those shared changes
are intentionally outside this draft.

## Superseding integration checkpoint — 2026-08-31

Production integration is now built, superseding the draft-only state above.
The slice contains 35 new IDs; including the retained shared section parent,
each compiled track has 36 IDs. All 23 exact Indonesian MathML fixture trees
are validated first; target narration accepts only registered linguistic mtext
translations after exact phrase-map replay, not a generic matrix parser.

Two unlabeled/numeric canonical JPEGs are retained byte-for-byte for all three
tracks with separate source/manifest hash witnesses. Point-order narration
names a/be (Javanese) and a/be letters (Indonesian) explicitly. Plain `<`/`>`
relations and reversed operands are spoken; c/d/e part markers receive spoken
labels. Contextual glyph-name duplication is removed only in narration.
Spacing-only `fs-id1171789687379` remains visible/source-preserved and is the
only declared nonspoken source block. Empty SSML is not fabricated for it.

Three CNXML tracks, one reader, and three transcript/SSML pairs are witnessed
by current draft/build receipts. Eighteen workflow regressions pass, including
source/fixture mutations and output determinism. Independent review is in
`THIRD_CHECKPOINT_REVIEW.md`. No human language, visual, screen-reader, listening,
or synthesis pass is claimed. Next is grouping `[23:28]`, not completion.
