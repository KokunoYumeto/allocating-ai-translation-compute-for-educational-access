# A10 exponents — complete remaining-section text draft, 2026-08-31

Status: provisional academic Javanese and conversational ngoko source-keyed
text draft. Both diagrams' CNXML descriptions are translated; the image assets
themselves are not yet inspected or translated. No generated CNXML, reader,
narration, SSML, audio, visual, screen-reader, educator, pronunciation or
listening pass is claimed. All A00, all A10 and the complete AX-2 workflow remain
the assignment; this handoff does not mark a whole module complete.

## Exact complete boundary

Both pinned Indonesian and English `m82453` sources contain **53 direct element
children** in section `fs-id1170655150800`. Select **[40:53]**, zero-based and
end-exclusive, retaining child 0's original title as shared context. All thirteen
remaining children were read in full in both languages before drafting.

| Original child | Source ID | Included content |
| --- | --- | --- |
| 40 | `fs-id1170654982105` | Nine-factor motivation, three-factor example, base/exponent explanation |
| 41 | `fs-id1170655219218` | Entire numeric base/exponent diagram reference and description |
| 42 | `fs-id1166420392829` | Two-cubed reading alternatives |
| 43 | `fs-id1170654953415` | Power notation versus expanded notation |
| 44 | `fs-id1170655107718` | Entire definition note, positive-integer restriction, symbolic diagram and reading |
| 45 | `fs-id1170654937018` | General power-reading introduction |
| 46 | `fs-id1166424875923` | Both squared/cubed list entries |
| 47 | `fs-id1170655195218` | Promise of the later explanation for special names |
| 48 | `fs-id1170655112606` | Internal reference to the reading table |
| 49 | `fs-id1170654954100` | Entire two-column reading table, all four data rows |
| 50 | `fs-id1170655121051` | Complete worked simplification and five-row solution table |
| 51 | `fs-id1170655196165` | Both first-practice parts and both answers |
| 52 | `fs-id1170655102894` | Both second-practice parts and both answers |

This reaches the **end of section `fs-id1170655150800`**. Last included
descendant: `fs-id1170655114560`. The next content is sibling section
`fs-id1170654953465`, *Sederhanakan Ekspresi dengan Urutan Operasi Hitung*;
its first instructional paragraph is `fs-id1170655225397`. There is no child
53 to exclude from the current section, and no attached example or practice is
cut off. Later sibling sections and module-end exercises remain separate,
unfinished assigned content, not implicitly covered by this boundary.

Verified selected-source counts:

- **32 source IDs total: 31 new plus the shared parent section.**
- **32 top-level MathML occurrences**, including the plain `n` and `12` reading
  fragments and repeated worked formulas; **22 `msup` nodes** in the ID source.
- **2 tables**: header plus four two-cell data rows; a headerless five-row,
  two-cell worked-solution table with one genuine blank first cell.
- **2 media references**, **1 internal link**, **1 two-item bulleted list**,
  **3 exercises / 3 solutions**: one worked question and four practice parts.
- No linguistic `mtext`, no fraction, and no spacing-only source block.

Ordered source IDs:

```text
fs-id1170655150800
fs-id1170654982105
fs-id1170655219218
fs-id1166420392829
fs-id1170654953415
fs-id1170655107718
fs-id1170655213989
fs-id1170655111941
fs-id1170655228836
fs-id1170654937018
fs-id1166424875923
fs-id1170655195218
fs-id1170655112606
fs-id1170654954100
fs-id1170655121051
fs-id1170655121053
fs-id1170654954435
fs-id1170654954437
fs-id1170655003298
eip-958
fs-id1170655196165
fs-id1170655197165
fs-id1170655197167
fs-id1170655102365
fs-id1170654954209
fs-id1170654954211
fs-id1170655102894
fs-id1170655194687
fs-id1170655194690
fs-id1170655025314
fs-id1170655114557
fs-id1170655114560
```

## Source witnesses and inherited corrections

| Exact retained module | SHA-256 |
| --- | --- |
| `downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml` | `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635` |
| `downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml` | `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed` |

No source acquisition, general audit or source mutation was performed.

The ID pivot already clarifies the English phrasing about repeated
multiplication: the exponent counts **equal factors**, not the number of
binary multiplication signs. It also explicitly restricts `n` in the elementary
definition to a **positive integer**. Both Javanese registers retain those
clarifications, including the literal plain-text `n`. Nine factors have eight
multiplication dots; three factors have two dots. The draft does not drift into
an instruction for nine additional multiplications.

In two reading explanations, the English source uses an `n` with superscript
letters `t`, `h` for the English ordinal suffix. The ID pivot already replaces
that linguistic ordinal MathML with plain `n`, making **24 English `msup`
nodes versus 22 Indonesian**. Preserve the two pinned witnesses separately;
Javanese follows the actual Indonesian MathML exactly. Do not restore English
`th`, confuse it with an exponent, or assert that ID and EN mathematical trees
are identical across these language-specific reading fragments.

## Canon consultation and provisional terminology

At source reading/drafting, fully read actual local C01 `wilangan`, C02 `cacah`,
C21 `ping`, C23 `gunggung`, and C09/C10 `kiwa`/`tengen`. C02's count sense is
important here: use `cacah faktor`, not language that confuses a sum with the
number of equal factors. C21 supports the multiplication family, while C09/C10
support the worked instruction's left-to-right direction. These lexical entries
do not by themselves standardize exponent terminology or complete formula
prosody.

During revision the coordinator acquired C34 `rambang`. Read its **entire actual
local extract**, `downloads/jv-Latn-ID/canon/rambang.txt`, rather than relying on
the coordinator's report. Its readable SHA-256 is
`a45727af8975350e044d15deff91892693b03a47f545e6f14d75182b9cf13bdc`.
The [official rambang entry](https://kbji.kemendikdasmen.go.id/kata/rambang)
directly gives a mathematical-power/repeated-equal-factors sense, separate from
its other homonyms. The earlier expression-rule stage also read this complete
web entry and the complete
[pangkat search page](https://kbji.kemendikdasmen.go.id/kata/pangkat).
The current stage now has a pinned local rambang witness; it is no longer only
an online suggestion. The flattened `43` in the readable dictionary example is
not a replacement for source MathML and is not copied into this translation.

The current lock has **34 records**: the initial 30 plus the coordinator's
separate rounding additions C31–C33 and C34. This task does not claim to have
read the unrelated rounding entries. Lock snapshot SHA-256:
`b803663cdb093658bdcf9815a53e2ba26f227e38296d3b2a840f55e8213590ac`.
No canon mutation, PDF selection or OCR was performed by this task.

| Source key or role | Draft decision and limits |
| --- | --- |
| `bilangan pokok (basis)` | Academic `wilangan pokok (basis)`; conversational `wilangan dhasar (basis)`. The full definition makes the repeated-factor role explicit. These are provisional school-term compounds, not newly attested canonical mathematical headwords. |
| `eksponen` | Retain the declared school loan in both registers, with the complete count-of-factors explanation. Do not collapse the exponent number into the base or whole resulting power. |
| `pangkat` / `notasi berpangkat` | Retain provisional `pangkat`, academic `notasi pangkat`, conversational `tulisan pangkat`. This preserves continuity with the preceding first-power readout. `rambang` is recorded as a genuinely attested alternative, not silently rejected as unavailable, but an unfamiliar complete `rambang n` usage/prosody is not declared standard without educator review. |
| `notasi panjang` | `notasi dawa` / `tulisan dawa`, a transparent literal naming choice tied to the shown full multiplication of factors. The English witness calls this expanded notation; “dawa” is not a rule that any lengthy expression is expanded notation. The worked instruction explicitly writes the factor product. Educator review may prefer a term emphasizing expansion. |
| `superskrip`, `faktor`, `kuadrat`, `kubik` | Declared school loans. Both alternative names for squared/cubed are retained. The prose describes the superscript's upper-right placement, without using the name of a geometric shape as a substitute for the power definition. |
| `wilangan bulat positif` | Retain this precise domain restriction as a declared school phrase in both tracks. Do not substitute the broader/ambiguous “whole shape” sense of `wutuh`, remove positivity, or introduce zero/negative exponents here. A zero **base** in the final practice remains legitimate and unchanged. |
| Opening factor description | Academic `Upamane dibutuhake...`; conversational `Upamane arep nggawe...`. Both preserve exactly nine factors equal to 2. `sebagai` is mapped to `bisa ditulis minangka` / `bisa ditulis dadi` so the restructured full paragraph remains grammatical across its separate MathML nodes. |
| Reading explanations | Restructure “we read” to “Wujud/Tulisan ... diwaca”; “although we read” becomes “Senajan ... diwaca”. This avoids an unreviewed `kita` pronoun/register choice without changing a formula, reading alternative or source example. |
| `Ekspresi` | Keep academic `Ekspresi`, conversational `Wujud Aljabar`, matching the immediately preceding expression/equation draft. It remains a provisional descriptive technical label. |
| `Sederhanakan:` | `Gawea luwih prasaja:` / `Gawe luwih prasaja:`. Preserve a simplification task, not a classification task or an instruction to read out the answer. |
| `Uraikan ekspresi.` | Academic `Tulisen ekspresi minangka ping-pingan faktor-faktore.`; conversational `Tulisen kabeh faktor sing dipingake.` These make the source expansion step explicit, without adding computed values. |
| `Kalikan dari kiri ke kanan.` / `Kalikan.` | `Pingake...` / `Pingna...`, preserving the source left-to-right direction and repeated step labels. These imperatives are productive applications of the consulted multiplication family, pending native review. |
| Worked table `summary` | Full exact-key translation supplied, preserving the source `3^4` character sequence. `required_linguistic_attributes` is a handoff requirement, not a claim that production already translates/render-labels it. |

There are **43 new exact trimmed phrase rows**, covering every linguistic
text/tail/`alt`/`aria-label`/`summary` surface in the selected CNXML. Together
with three shared rows (context title, `dan`, `Penyelesaian`) and the two
identifiers `a`/`n`, they cover all **48 alphabetic source keys**. Only `n` needs
a new unchanged-identifier declaration; `a` already belongs to the shared list.
No blanket passthrough is introduced for unexplained words or letters.

### Symbolic-diagram clarification

The inherited second diagram description says the repeated `a` factors have an
indeterminate count, but also explicitly labels the bracket `n faktor`. The
Javanese descriptions resolve the potential misunderstanding: their count is
**n**, while the numerical value of **n** has not been specified. That is a
disclosed explanatory clarification, not an infinite product, an unspecified
different count, or a new domain extension. The first description likewise
retains **three factors equal to 2**, never three extra applications of
multiplication.

## Complete mathematics and answer obligations

| Source role | Preserved forms and facts |
| --- | --- |
| Motivation | Both full nine-factor products of 2; the separate three-factor product; powers `2³`, `2⁹`; base 2 and exponent 3 identified |
| Definition/readings | `aⁿ`, separate reading-token `n`, `a²`, `a³`; no evaluation or invented value for `a`/`n` |
| Reading table | `7²`, `5³`, `9⁴`, `12⁵`, plus separate MathML `12` in the final word cell |
| Worked problem `fs-id1170654954437` | Simplify `3⁴` |
| Worked solution `eip-958` | Rows preserve `3⁴`; `3·3·3·3`; `9·3·3`; `27·3`; plain-text **81**, with all four source instructions |
| First practice `fs-id1170655102365` | ⓐ `5³`, ⓑ `1⁷`; answer paragraph `fs-id1170654954211`: **125**, **1** |
| Second practice `fs-id1170655025314` | ⓐ `7²`, ⓑ `0⁵`; answer paragraph `fs-id1170655114560`: **49**, **0** |

The last table cell and all practice answers are **plain text**, not MathML;
they must survive numeric-fact checks and receive proper spoken cardinal/answer
cues. Zero is an explicit answer, not an empty cell to omit. Simplification
results must not be inserted into the corresponding question narration.

Top-level MathML dispatch counts for later exact fixtures are:
`fs-id1170654982105` 6; `fs-id1166420392829` 1;
`fs-id1170654953415` 2; `fs-id1170655107718` 3;
`fs-id1170654937018` 2; `fs-id1166424875923` 2;
`fs-id1170655195218` 2; `fs-id1170654954100` 5;
`fs-id1170655121051` 5; `fs-id1170655196165` 2;
`fs-id1170655102894` 2. This totals 32. The five worked-example formulas use
their top-level example anchor, including four in the answer table.

## Pending AX-2 and image work

- Register exact source-bound powers, complete factor products and plain reading
  fragments, without widening a generic parser. Preserve the nested `mrow`
  around the **whole base 12** in `12⁵`, all repeated formulas, every attribute
  and the difference between bare and wrapped `msup` trees.
- MathML contains **26 U+00B7 multiplication dots**, **five ASCII full stops**
  and **one comma**. The latter six are source sentence punctuation inside
  formulas, not decimal markers or multiplication operators. Preserve them in
  the reader while handling their speech at exact anchors.
- Preserve the scalar variable exponent `n`, with explicit spoken letter names
  for both `a` and `n`, including plain-text `n` in the positive-integer clause.
  Read the squared/cubed naming alternatives without inferring or giving a
  numeric simplification where the source is explaining pronunciation.
- The diagram ellipsis represents a **finite n-factor pattern**, not unbounded
  continuation. Its bracket and label must establish that count. Do not import
  the pilot's infinite-sequence ellipsis convention or treat a three-factor
  sketch as the fixed value of `n`.
- Bind the full `eip-958` table and its target text/summary. Its first left cell
  is an actual single space; preserve it as blank, not zero, and do not omit the
  row's right-hand `3⁴`. No visible header may be invented. Narrate every step
  and the final plain-text 81 once, in order, with the outer solution cue.
- Translate and retain `summary`; use a declared source-bound reader label
  policy. Its `3^4` substring is a power description, not a request for generic
  caret parsing. Native/screen-reader interpretation remains untested.
- Keep link `fs-id1170655112606` → `fs-id1170654954100`, the source bulleted-list
  hierarchy, both untitled practice-solution cues and all circled a/b spans.
- Materialize and inspect **both exact pinned diagram references** before
  making source-bound text derivatives: media `fs-id1170655219218` uses
  `../../media/CNX_ElemAlg_Figure_01_02_003_img_new.jpg`; media
  `fs-id1170655111941` uses
  `../../media/CNX_ElemAlg_Figure_01_02_004_img_new.jpg`. Existing local file
  enumeration found neither standalone image in this task's downloads; no
  extraction, new acquisition or image edit was made. The pinned archive is a
  later source for these assets, not evidence of completed visual inspection.
- The target descriptions currently specify intended labels `wilangan pokok`
  / `wilangan dhasar`, `eksponen`, and `n faktor`. These must agree with the
  eventual track assets. Actual embedded English labels, arrow geometry, base/
  superscript positions and factor-bracket endpoints must be checked against
  the images; translated alt text alone is not complete diagram translation.

## Read-only verification

**PASS with explicit pending summary integration, 2026-08-31.** Both complete
module hashes match the source lock. Both section child counts are 53, selected
ID order agrees across ID/EN, and all counts/table shapes above were checked.
The only two ID/EN MathML subtree differences in the selected sequence are
occurrences 12 and 14, the documented English ordinal-suffix reading fragments.

All 43 unit phrase keys occur in the source and merge without conflicts with
the shared ledger; no alphabetic source key is unresolved. Both registers pass
`draft_units.validate` for source identity/IDs, in-unit references, mathematical
tokens/attributes and numeric facts. An additional comparison confirms every
complete target MathML subtree equals its ID source tree, including namespaces,
wrappers, attributes and punctuation. A top-level MathML element's external
prose tail is correctly treated as translatable CNXML prose, not as an unchanged
mathematical token. Nonlinguistic attributes and numeric literals in all three
linguistic attribute types were checked separately.

At this snapshot, the ordinary translator still leaves `summary` unchanged.
The supplied exact-key summary was explicitly replayed **in memory** for the
complete draft witness; this is not a claim that the production path supports
it. Two successive full replays produce identical bytes per register. The
positive-integer `n` restriction, blank first worked-table cell, final plain
81, all a/b answer spans and the explicit zero answer are preserved. Independently
checked the nine-/three-factor counts, worked chain ending at 81, and all four
practice results 125, 1, 49, 0.

Seven deliberate target mutations per register are rejected: changed power
base, reversed base/exponent, flattened `msup`, multiplication-dot substitution,
broken table link, blank cell changed to zero, and zero answer changed to one:
**14 rejection checks total**. All seven consulted local readable canon hashes
match the current lock. No writer, asset extraction, generated-source update,
reader build, voice service, or shared-code change was invoked.

| Checkpoint witness | SHA-256 |
| --- | --- |
| `translation/a10-exponents.edits.json` | `e79995cae61c03a08fb4481dd47e3dca74eb070ebf10c9e7e285012826df738d` |
| Shared phrases used | `adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8` |
| Academic XML in memory, including explicit summary replay | `dacb7f95a7adb5aa98a63387a91b82f225ec341e4e2fddacb047d9f492f7c976` |
| Conversational XML in memory, including explicit summary replay | `9761f171fb9749960ab3c95d0baa4ec19469e8fc36593bbddb37cea204c7f64f` |

XML serialization is `ET.tostring(..., encoding='utf-8',
xml_declaration=True) + b'\n'`. These prospective witnesses are not generated
file hashes or a reader/audio completion claim. The entire remaining-section
text draft is ready for review and integration; the two image derivatives and
all corresponding AX-2 work remain explicit unfinished obligations.


## AX-2 finite-rule checkpoint — 2026-08-31 (later than the text-only snapshot)

This appendix preserves the original text-stage record above. Its statements about uninspected images, unbuilt narration rules and pending summary replay are historical, not the current checkpoint state. Current contribution owns ONLY the new audio/a10-exponents.rules.json and this append-only QA extension. The existing exponent phrase edit was revised by root for the verified image discrepancy; this contribution did not edit phrases, production scripts, descriptors, locks or assets.

Current result: 32 exact MathML fixtures with 96 three-track readings; 2 whole-table fixtures with 6 readings; 6 whole-prose/answer fixtures with 18 readings; 2 diagram fixtures with 6 readings; and 1 explicit table-reference fixture with 3 readings. This is finite-rule and read-only component evidence, NOT a completed reader/transcript/SSML build, synthesis, native review, or module completion.

### Reread source and canon at the changed stage

Before authoring these rules, reread the ENTIRE actual ID and EN source [40:53], with child 0 retained as context. The full 53-child section still yields 14 selected children including context title, 32 source IDs and 32 MathML occurrences. This reaches the section end, not a pilot subset. The last source descendant remains fs-id1170655114560; the next sibling remains order-of-operations section fs-id1170654953465, first paragraph fs-id1170655225397.

Opened and fully read actual local C21 ping and C34 rambang at narration-stage start; then C07 lima, C17 rolas, C18 likur, C19 atus, C26 wolu and C27 sanga while choosing factor and answer cardinal readings. During rule revision, reopened the full C02 cacah, C09 kiwa and C10 tengen extracts together with the actual ID/EN definition fs-id1170655213989. These are eleven actual current-stage readings, not merely checked download names or inherited dictionary summaries.

- C21 grounds multiplication; C34 directly attests the mathematical-power/equal-factor sense. pangkat stays the declared provisional school loan. The flattened dictionary example 43 is not a formula witness.
- C02 was checked for number/count in cacah faktor, including its other senses, not claimed as a unique mathematical standard. The positive-integer n clause comes from actual pinned Indonesian source, not the dictionary.
- C09/C10 constrain left/right source arrow labels and the worked left-to-right instruction. Sleep-related tengèn is not the intended direction word.
- C17 supports rolas. C07 gives salawé; C19 gives satus. The full composed satus salawé reading of 125 is explicit and reviewable, not claimed as a quoted complete headword.
- C18 supports the likur family, but pitulikur for 27 remains a productive provisional composition. C26/C27 support the components used in wolung puluh siji (81) and patang puluh sanga (49). No native pronunciation certification is claimed.

The actual canon lock snapshot has 36 records, SHA-256 b791902da837966e351f72bd1ed112ee05831292fa658fcd3ef7ecbc9a8a3311. This is not a claim that all 36 were read, nor that later additions cannot occur. All eleven selected readable hashes were verified against their actual bytes; the rule file records each path, URL and hash. No new canon acquisition, selected PDF, OCR, license audit or broad source operation was performed.

### Exact dispatch and source-bound overrides

Math dispatch uses module, selected top-level source-child anchor, one-based descendant MathML ordinal, and exact complete source tree. nearest_source_id only explains nested ownership. For example, all five worked formulas belong to top-level fs-id1170655121051, even when their nearest ID is eip-958. Nonmath records likewise distinguish top-level anchor from the exact table/prose/media element ID.

Each fixture preserves namespaces, wrappers, every attribute, base/exponent order, numbers, source punctuation and factor order. All 22 Indonesian msup nodes are preserved, including the mrow around the entire base 12. English has two additional linguistic ordinal-th superscripts at overall math ordinals 12 and 14; these are not restored into the ID/JV trees. Neither generic powers nor generic caret or ellipsis parsing is authorized.

| Math fixture range | Source obligation and reading decision |
| --- | --- |
| M01–M06 | Full nine-factor products twice, the three-factor product, 2³/2⁹ and base/exponent explanation. Nine factors use eight dots; no compression or extra multiplication is inserted. |
| M07–M09 | Power-reading alternatives and comparison with the full three-factor notation; no evaluation to 8. |
| M10–M14 | aⁿ and the separate n pronunciation fragments, all with explicit letter names. The plain n in the positive-integer clause is covered by a whole-prose fixture too. |
| M15–M18 | a²/a³ and their special-name context. Retain kuadrat/kubik explanations; do not supply a numeric value for a. |
| M19–M23 | All reading-table powers, including the whole base 12 and separate final word-cell 12. Keep both squared/cubed naming alternatives, not the computed power values. |
| M24 | Worked QUESTION 3⁴ only; no 81 or answer cue in this fixture. |
| M25–M28 | Worked SOLUTION formulas 3⁴, 3·3·3·3, 9·3·3 and 27·3; final 81 is plain text in the fixed table, not a missing MathML fixture. |
| M29–M32 | Four practice QUESTION powers 5³, 1⁷, 7², 0⁵; answers remain in the two source solution paragraphs. |

The 26 U+00B7 dots are all spoken as multiplication. Five trailing ASCII full stops and one trailing comma are retained as sentence/clause punctuation in the exact readouts, not decimals or multiplication. pungkasan pangkat / akhir pangkat are provisional auditory end markers, not visible source operators.

Whole-prose fixtures are fs-id1170655213989, fs-id1170655228836, fs-id1170654937018, fs-id1166424875923, fs-id1170654954211 and fs-id1170655114560. They prevent bare a/n, a lost positive-integer restriction, misread English ordinal suffixes, and number-helper drift in plain-text answers. Seven mathematical occurrences M10–M16 are marked prose-only; the existing exact math dispatcher accepted this context binding in memory. Production must select the whole-prose override BEFORE descending to children; otherwise fail rather than narrate both versions.

The first table fixture reads its two real headings and all four data rows, once. The second preserves five rows, two cells per row, no header, the exact initial blank left cell, all four source instruction cells, and final plain-text 81 once. Fixed table readouts are independently reconstructed from the actual source-bound target cell order; long aria-label or summary must not be recited again as a duplicate table.

The source summary for eip-958 is now translated by the existing shared translation function during this in-memory replay; the earlier supplemental-summary note above is historical. Retain that exact registered summary in CNXML and use it as the reader's accessible label only when the source aria-label is absent. The literal summary substring 3^4 is not permission for generic caret narration.

Reference R01 binds actual paragraph fs-id1170655112606 and actual destination fs-id1170654954100, present once as a table in this selected unit. Its descriptive spoken table label supplies no invented number. Preserve the real reader link and existing paragraph tail; do not read the target table twice.

### Actual diagrams, current target correction and asset binding

This narration task independently viewed both original JPEGs directly from the pinned ZIP in memory, without extracting or altering images. Observed bytes matched root's pinned Git blob witnesses:

| Original JPEG | Dimensions | Bytes | SHA-256 |
| --- | --- | --- | --- |
| 003_img_new.jpg | 541 × 44 | 33650 | 5be6626600b25727b5a93b37e1c4cb45a82a3fe9cc1e91b4fc0888b804370ec7 |
| 004_img_new.jpg | 209 × 93 | 38920 | fe978ddd3f9f8cb93b2402be5268888aa0f668ae5c2dd12032c7f16208ec2bbe |

003 shows base→2³←exponent plus the three-factor English instruction/product. Rule speech follows the pinned Indonesian clarification: exactly three equal factors, not three additional binary multiplication operations. No computed value is supplied.

004 ACTUALLY shows aⁿ = a·a·a·…·a: three explicit a factors before the ellipsis and one after. Both inherited source alts omit one pre-ellipsis factor. Root revised only the Javanese target alt to match the observed four printed glyphs, while keeping exact Indonesian keys, pivot content, source MathML and positive-integer domain. The new phrase hash is 6d6348f558bfe5622511a978b148e8786e87df0a478465e7dff0b49fe358903a, and all rule target bindings use this hash, not the earlier e79995… snapshot.

All three diagram readouts preserve the actual four printed factors, ellipsis and brace; the brace labels n total factors, with n's numerical value unspecified. Four printed glyphs do NOT set n=4, and the ellipsis is NOT infinite repetition. The independent Indonesian narration describes the actual image even though the unchanged ID source alt has the documented omission.

Root separately prepared the exact two retained JPEGs and four native Javanese SVG derivatives. Read [the root asset review](a10-exponents.ASSETS.md), SHA-256 d38c615c05bffcdbe6ce99e0b2c846510b22906a26a972bf44b921bec1a98b24. Its four final RSVG render inspections are root's attributed observations; this narration task does not claim to have viewed those four renders. It did independently hash all six current output files against translation/a10-exponents.assets.json, SHA-256 f7a419b2c6a467a517fced8b7d3444dfb7ab19f87c3f79b27a49931ed95bb590, and read SVG text to verify the intended register-specific labels.

The Indonesian track retains the English-labelled source JPEG. Rule metadata correctly records printed base/exponent/n factors, while ID speech explains their Indonesian meanings; it does not pretend the source bitmap says bilangan pokok. Javanese SVG labels are wilangan pokok / wilangan dhasar, eksponen, and n faktor. Each output's actual MIME type is bound: image/jpeg for retained source, image/svg+xml for Javanese. Reader integration must not force JPEG MIME onto SVG.

### Answers, validation and honest remaining work

Independent arithmetic confirms the complete worked chain 3⁴ = 3·3·3·3 = 9·3·3 = 27·3 = 81, and all four practice results 125, 1, 49, 0. The equalities in this QA sentence are verification notation only; no new equals sign is inserted into the source worked table.

P05/P06 read the plain source answer paragraphs in exact part order, with satus salawé / siji and patang puluh sanga / nol (ID: seratus dua puluh lima / satu and empat puluh sembilan / nol). The existing untitled solution containers must supply exactly one Wangsulan / Jawaban cue before each fixed paragraph; the fixtures do not duplicate it. The worked source solution title remains its outer cue. Question fixtures contain no evaluated result, equality or answer cue; the zero base in 0⁵ is legitimate question content, not answer leakage.

Read-only checks passed:
- 96 exact mathematical readings via existing source_bound_math plus an independent finite test-only tree walk; 7 context-only mathematical readings per track bound to full prose.
- 6 source-bound table readouts and target trees, including headers, colspec/alignment, summary/aria, the real blank cell and the final plain-text 81.
- 18 prose, 6 chart and 3 reference bindings/readouts with explicit literal letters, source domain, answer order and finite factor pattern.
- Exact full source module/selection/edits/shared hashes, repeated deterministic in-memory translation, ID/EN source math differences limited to ordinals 12/14, and all source operator counts.
- Six actual asset output file hashes/MIME types, Javanese SVG text labels, and eleven actual readable canon hashes.
- 26 deliberately altered cases rejected: changed_power_base, changed_exponent, flattened_power, dot_to_plus, fixture_anchor, fixture_ordinal, fixture_tree, spoken_math_operand, question_answer_leak, table_blank_to_zero, table_summary, table_aria, table_final_81, spoken_table_result, dropped_domain, bare_n, wrong_answer_125, zero_answer_omitted, diagram_dropped_factor, diagram_infinite, source_diagram_alt, reference_target, scope_cut, fixed_four_factor_count, wrong_chart_anchor, wrong_prose_anchor.

The first harness run omitted the table-index argument while calling its local fixed-table checker. That harness-only mistake was corrected in memory before the complete passing rerun; it was not a production defect or a hidden failed output. No installed test script or generated source/reader/audio product was written by this contribution.

Current source/target canonical hashes use SHA-256 of UTF-8 build_units.tree_key (copy, root tail removed, ElementTree canonicalization with stripped formatting whitespace):
- Indonesian selected source: 98a02d384682f547090ab22173cf709d95a9336b7f5d749e98697e4d72ca041d.
- Javanese academic in memory: 4f395164b6efe9cc4f3e81eb2c32b74ae256e2db0c302b8895ac9a99376342d1.
- Javanese conversation in memory: 870d0859a5f3a1fe5a4c69152e065d6079536ae6616b072d15b5e09b90600cb4.
- Rule file: c32821a7521853fb01eb1a55008fac9f53d1087a625ba7296e4e7a82159af436 (98818 bytes).
- Asset manifest: f7a419b2c6a467a517fced8b7d3444dfb7ab19f87c3f79b27a49931ed95bb590.
- Shared phrase ledger: adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8.

Production registration and all table/prose/chart/reference override dispatch still need root integration. The existing exponents production reader/transcript/SSML path was NOT exercised here; no deterministic written-product receipt, integrated browser/screen-reader pass, native-language approval, synthesis, voice compatibility test or listening review is claimed. Exact source-image inspection and root's standalone SVG render review do not replace those later reviews. Full all-A00/all-A10/AX-2 assignment remains unfinished.

## Producer integration follow-up

Root subsequently registered the entire [40:53] remainder and generated all
three CNXML, transcript/SSML tracks and its offline reader. Existing phrase,
rule and asset files remain unchanged from the rule-stage hash snapshot.
The earlier pending-integration metadata describes its original draft stage;
qa/a10-exponents.build-receipt.json binds the new production draft outputs.

Full source/target replay and six prose/two table/two chart/one reference gates
run before fixed speech. Seven mathematical occurrences cannot be narrated
without their registered whole-prose context. Ten new workflow tests pass;
root read all three saved transcripts against source and canon. The reader
uses each output's real JPEG/SVG MIME. Independent integration review remains
pending, as do native, educator, integrated-browser, screen-reader and listening
reviews. Source images/MathML and all earlier generated unit outputs are unchanged.

## Independent integration follow-up

EXPONENT_CHECKPOINT_REVIEW.md now records the completed bounded review: all
154 tests, 204 independent rejection probes and 15 intact controls passed.
A direct fixed-context helper gap was corrected and independently retested;
the saved reader/CNXML/transcript/SSML bytes are unchanged. The review's exact
SHA-256 is 8d63bbf8222f68c6122347bbce8dcb2e70f3d3f1c59f50ff92a981017e9268dc.
Inherited Indonesian alt/image discrepancies remain explicitly disclosed.
Human/register/integrated-browser/screen-reader/listening review is still pending.
