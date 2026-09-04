# A10 expressions/equations text draft — 2026-08-31

Status: source-keyed provisional academic Javanese and conversational ngoko
edits, not an integrated unit. No CNXML file, reader, narration, SSML, synthesis,
visual, screen-reader, native-educator, pronunciation, or listening approval is
claimed by this handoff. The full A00/A10/AX-2 assignment remains unfinished.

## Exact coherent boundary

Select module `m82453`, section `fs-id1170655150800`, direct element children
**[28:40]**, zero-based and end-exclusive. Retain the original section title as
shared context. Both pinned Indonesian and English source versions of the
relevant section were read before fixing this boundary; the next exponent
introduction was also read to establish the topic change.

| Child | Source ID | Included content |
| --- | --- | --- |
| 28 | `fs-id1170654957085` | Complete phrase/sentence analogy and expression/equation introduction |
| 29 | `fs-id1170655102379` | Expression definition, paragraph and `term-00012` |
| 30 | `fs-id1170654988522` | Expression-table introduction |
| 31 | `fs-id1170655221887` | Three-column table: header plus all four expression rows |
| 32 | `fs-id1170655003585` | Source-language grammar comparison |
| 33 | `fs-id1170654938230` | Equation comparison and equals-sign `term-00013` |
| 34 | `fs-id1170655118064` | Equation definition, paragraph and `term-00014` |
| 35 | `fs-id1170655111405` | Equation-table introduction |
| 36 | `fs-id1170655090988` | Two-column table: header plus all five equation rows |
| 37 | `fs-id1170654953357` | Entire four-part worked example and four-row solution table `eip-10` |
| 38 | `fs-id1170655166808` | Entire first two-part practice and both answers |
| 39 | `fs-id1170655205588` | Entire second two-part practice and both answers |

Next excluded: **child 40, `fs-id1170654982105`**, the introduction to exponents.
No attached exercise, solution, table row, or answer is omitted. The selected
last practice already contains `y³ ÷ 14`; its superscript must be handled now,
even though the explanatory exponent lesson starts after this unit.

Counts verified independently against both language witnesses:

- **34 ordered source IDs: 33 new plus shared section `fs-id1170655150800`.**
- **21 top-level MathML expressions**, including the four repeated worked
  answers. There are no linguistic `mtext` nodes in this span.
- **3 CNXML tables**: a 3-column header plus 4 data rows; a 2-column header plus
  5 data rows; and a headerless 4-row, 2-column worked-solution table.
- **3 exercises / 3 solutions**: one worked example with 4 parts and two
  practices with 2 parts each, giving **8 classified items and all 8 answers**.
- **0 media, 0 links, 0 spacing-only source blocks.** No asset extraction or
  new nonspoken-source anchor is needed.

Ordered IDs:

```text
fs-id1170655150800
fs-id1170654957085
fs-id1170655102379
fs-id1170654958000
term-00012
fs-id1170654988522
fs-id1170655221887
fs-id1170655003585
fs-id1170654938230
term-00013
fs-id1170655118064
fs-id1170655170220
term-00014
fs-id1170655111405
fs-id1170655090988
fs-id1170654953357
fs-id1170654953360
fs-id1170655229951
fs-id1170655162511
fs-id1170655153999
fs-id1170655111791
eip-10
fs-id1170655166808
fs-id1170654924234
fs-id1170654924237
fs-id1170655124883
fs-id1170655226888
fs-id1170655120617
fs-id1170655205588
fs-id1170655022136
fs-id1170655027224
fs-id1170655027226
fs-id1170654959582
fs-id1170654959584
```

## Pinned source and canonical evidence

| Witness | SHA-256 |
| --- | --- |
| `downloads/jv-Latn-ID/a10-source/translated/modules/m82453/index.cnxml` | `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635` |
| `downloads/jv-Latn-ID/a10-source/authority/source/modules/m82453/index.cnxml` | `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed` |

The source lock contains these module witnesses. They are the same retained
A10 release/canonical texts used by the preceding units. No acquisition or
repeat general audit was performed.

At source reading/drafting, fully reread actual local C21 `ping`, C22 `para`,
and C23 `gunggung`. These support the existing operation/result vocabulary
`ping-pingan`, `paran`, `dipara`, and `gunggung`; none standardizes the new
expression/equation terminology. At revision, fully reread C18 `likur`, C26
`wolu`, and C27 `sanga` for the numbers in the examples and prospective speech,
plus newly pinned C29 `kurung` and C30 `tutup` for grouping descriptions. The
written-parenthesis sense and open/close components are lexical evidence, not
certified formula prosody. Exact readable-file hashes were checked against
the canonical lock during final validation.

The actual lock has **30 local records** at this handoff; its SHA-256 is
`c15629f66c2c3f04f3c64837165e22d07f80ee98b2d8bd1ec6b16c0049d9f4bf`.
This task did not change that shelf. C29/C30 were acquired separately by the
coordinator, so the earlier grouping draft's 28-entry snapshot remains history.

The grammar topic also prompted targeted official KBJI consultation. The full
retrieved [tembung entry](https://kbji.kemendikdasmen.go.id/kata/tembung) supports
`tembung`/`tetembungan` and includes a phrase sense under `pitembungan`. The
readable indexed [ukara entry](https://kbji.kemendikdasmen.go.id/kata/ukara)
supports its sentence sense, but the subsequent direct page fetch failed. The
indexed entry was read; a successful full direct-page retrieval is not claimed.
Neither web consultation is a newly acquired local canonical record. The
archaic matching sense of `anukara` in that search is **not** taken as evidence
for a school-mathematics equation term. No returned PDF was selected or relied
upon, and no PDF/OCR completion is claimed.

## Linguistic decisions and unresolved terms

The JSON supplies **38 exact trimmed source phrase keys**, each with separate
academic and conversational wording. All occur in this exact span. Three
additional linguistic keys resolve unchanged from the shared phrase ledger:
the section title, `dan`, and `Penyelesaian`. Identifiers `x` and `y` remain
shared exceptions; only `n` is newly declared. All 44 distinct alphabetic
source keys, including the table attributes and three identifiers, are covered.

| Source role/key | Decision and limits |
| --- | --- |
| `ekspresi` / `Ekspresi` | Academic `ekspresi`; conversational `wujud aljabar` / `Wujud Aljabar`, consistent with the preceding grouping prose. Both are explicitly defined here. The conversational label is descriptive and provisional, not a newly established technical standard; educator review should check that it does not encourage calling a whole equation an expression. |
| `persamaan` / `Persamaan` | Retain the school-term loan in both registers, with the full two-expressions-plus-equals-sign definition. Do not collapse the equation noun into the equality relation or use a newly invented native-looking term without evidence. |
| `frasa`, subjek, predikat | Retain declared school-grammar loans. `ukara`, `tetembungan` and conversational `tembung-tembung` have the consulted lexical evidence. The source analogy is not treated as a complete theory of Javanese sentence structure. |
| Opening running/player examples | Give explicit Javanese equivalents, introduced as equivalents of the Indonesian-source examples. `Wong sing dolanan bal-balan kuwi` retains the football-player role without adding age, gender, team, or a named person. The subject/predicate statement is scoped to this example, not every possible Javanese utterance. |
| `Frasa dalam Bahasa Indonesia` / `Kalimat Bahasa Indonesia` | Use `Padanan Frasa Basa Indonesia` / `Padanan Ukara Basa Indonesia`, with adjacent prose and full table descriptions explicitly saying the equivalents are in Javanese. Do not label the now-Javanese cells as literal Indonesian phrases/sentences. The independent Indonesian track retains its own source text. |
| Post-table grammar claim and equals-sign analogy | Attribute the original claim to the Indonesian source. Explain the equals sign's predicate role as the comparison made here (`Ing pepadhan iki`), not a universal rule that every sentence must contain a verb. `pepadhan` as an analogy label remains a provisional composed choice. The English original says verb; the Indonesian pivot says predicate. Neither difference is silently erased. |
| `jumlah tiga dan lima`, product/quotient phrases | Use `gunggung telu lan lima`, `asil ping-pingan enem lan pitu`, and `asil paran`. Retain prior-unit `selisih`, `ditambah`, and `dikurangi` as disclosed school-use wording; no new attestation is claimed for them. Preserve operand order. |
| Number words in equation rows | Preserve eight, fourteen, forty-two, fifty-three, nine, two and three as `wolu`, `patbelas`, `patang puluh loro`, `seket telu`, `sanga`, `loro`, `telu`. `seket` follows the project's existing spelling; this consultation does not pretend C18 directly attests fifty-three. |
| `Tentukan apakah ...` | Academic `Temtokake ...`; conversational question plus `Temtokna:`. Both request classification only, not evaluation or solving. All repeated prompts use the same pair. |
| Worked answer fragments | `Iki kalebu` / `Iki kuwi`, followed by the exact expression/equation classification and original equals-sign reason. Dash placement and inline emphasis structure remain source-owned. |
| `summary` on `eip-10` | A full exact-key translation is included. `required_linguistic_attributes` is handoff metadata, not a claim that the existing builder already honors it. |

### One explicit accessible-description correction

The expression table's Indonesian `aria-label` describes its final formula as
`x, garis miring, y`, but its actual MathML is a stacked `mfrac` with numerator
`x` and denominator `y`, not a slash token. The Javanese description explicitly
places `x` above and `y` below the fraction line, matching the formula. This is
a disclosed correction in the target accessible description only: the exact
Indonesian source key, Indonesian witness, MathML tree and fraction order remain
unchanged. The phrase-reading column still expresses division as `x dipara y`.
No numeric literal in either table description is added, dropped, or changed.

## Formula and answer inventory for the next integration stage

The following is a human-readable checklist, not a substitute for exact MathML
fixtures. `x/y` below denotes the source stacked fraction only in the first
table. Source U+2212 minus, U+00B7 multiplication dot and U+00F7 division sign
must remain unchanged; superscript notation must not be flattened.

| Anchor and ordinal(s) | Source mathematics / required classification |
| --- | --- |
| `fs-id1170655221887`, 1–4 | `3+5`; `n−1`; `6·7`; stacked `x/y` |
| `fs-id1170655090988`, 1–5 | `3+5=8`; `n−1=14`; `6·7=42`; `x=53`; `y+9=2y−3` |
| `fs-id1170655153999`, 1–4 | ⓐ `2(x+3)=10`: equation; ⓑ `4(y−1)+1`: expression; ⓒ `x÷25`: expression; ⓓ `y+8=40`: equation |
| `eip-10`, 1–4 | All four worked formulas repeated, with the same classifications and reasons |
| `fs-id1170655124883`, 1–2 | ⓐ `3(x−7)=27`: equation; ⓑ `5(4y−2)−7`: expression |
| `fs-id1170655027226`, 1–2 | ⓐ `y³÷14`: expression; ⓑ `4x−6=22`: equation |

Practice answer paragraph anchors are `fs-id1170655120617` and
`fs-id1170654959584`. Keep the explicit solution/answer cues before them. The
numeric identities `3+5=8` and `6·7=42` agree; variable equations are examples,
not an instruction to solve them at this stage.

New narration and reader requirements, all still pending:

- Bind all **21 exact source trees** to module, anchor and ordinal. The four
  worked formulas have an `mrow` wrapper in the question but no such wrapper
  in `eip-10`; identical text must not make these different trees interchangeable.
- Preserve the one `mfrac` and one `msup`. For the latter, read the power of
  `y` before division by fourteen: never `y times three`, `y thirty-one`, or
  `y` to the power `3 divided by 14`. Exact fixture support is required before
  any new superscript is admitted; this draft grants no generic parser authority.
- Preserve all **6 parenthesis pairs**, including `stretchy="false"`, and all
  **9 implicit multiplication sites** across table, worked questions, repeated
  answers, and practices. Narration may clarify multiplication source-bound;
  visible extra multiplication signs must not be inserted.
- Add explicit spoken `n` as a letter (`aksara en` / `huruf en`) in both MathML
  and emphasized table prose, alongside existing `x`/`y` readings. Distinguish
  circled part labels ⓐ–ⓓ from mathematical letters. In the equation wording
  row, `loro` followed by emphasized `y` means the coefficient product `2y`,
  not a two-digit number; source-bound speech needs to make that clear.
- `eip-10` has **no `thead`**. The existing generic table narrator expects
  headers, so it needs a registered headerless explanation-table convention.
  Do not invent visible source headers or silently drop the first row. Pair
  each formula with its classification and its reason in source order.
- The current `translated()` loop handles `alt` and `aria-label`, not `summary`.
  Reader rendering also draws its table label only from `aria-label`, so a
  summary-to-accessible-label policy is needed for `eip-10`. Preserve the original
  CNXML attribute while translating its linguistic value; do not silently emit
  an empty accessible label or discard the description.
- Ordinary table headers must retain scope. The first two tables need five
  actual source header cells per track; the third contributes none. Full prose
  descriptions and row speech must not produce contradictory header names.

There is no image/geometry blocker: this span has no media. A unit descriptor,
three-track generated sources, source-bound narration rules, scoped table/summary
support, regression tests, reader, transcripts, SSML, receipts and coverage
integration remain separate work. None was changed by this two-file task.

## In-memory verification result

**PASS with a separately disclosed summary-replay gap, 2026-08-31.** The two
full source-module hashes match the lock. Source selection gives identical
ordered ID lists in Indonesian and English, with the counts and table shapes
listed above. All 38 new phrase keys occur in the source and merge without a
shared-key conflict. Both registers pass the existing `draft_units.validate`
checks for identity, references, mathematical tokens/attributes and numeric
facts. An additional comparison preserves all nonlinguistic attributes and
all MathML text, tails, namespaces, child order and attributes exactly.

The ordinary translator demonstrably leaves `eip-10`'s `summary` unchanged.
For this review only, its supplied exact-key translation was then applied in
memory with the same phrase function. That explicit supplemental step is **not**
production support. The resulting complete target trees again pass structural
validation and a separate numeric-attribute check including `summary`.

Two consecutive in-memory replays produce identical bytes in each register.
All eight answer classifications agree with the source. An independent token
walk confirms six parenthesis pairs and nine implicit multiplication sites.
Seven deliberate target mutations per register are rejected: numeral change,
operator change, exponent change, fraction-operand reversal, `stretchy` change,
source-ID change, and removed worked-table cell. No writer, build command or
generated-output update was invoked.

| Checkpoint witness | SHA-256 |
| --- | --- |
| New edits file | `8305509cfd6146c9110a367acfc05fb856072a622a65db39c08e73a267e147b4` |
| Existing shared phrases used | `adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8` |
| Academic XML in memory, including explicit supplemental summary replay | `01c94becef8bc1cedb8caa88ef8282192db8fc20388a02cb1c1ee9d0fe9644ef` |
| Conversational XML in memory, including explicit supplemental summary replay | `f30c7272fc35fd31d0b74f3f8c72502cee6de576d6a9f62e76fd8ca2ba1f5b9d` |

XML byte witnesses use `ET.tostring(..., encoding='utf-8',
xml_declaration=True) + b'\n'`. They are prospective integration witnesses,
not file-output hashes or reader/narration completion claims. Changes to
translation decisions or serialization require new evidence.

## Finite narration-rule handoff — 2026-08-31

Added only `audio/a10-expressions-equations.rules.json` and this append-only
witness during the narration stage. The rule file has **21 source-exact MathML
fixtures / 63 register readings**, **3 complete source-table fixtures / 9 fixed
table readouts**, and **8 classification consistency records**. No shared
builder, descriptor, output, receipt, source lock or canon file was modified by
this rule task. Production integration and human review remain pending.

### Dispatch and source/target binding

Production MathML fixture keys use the **top-level selected child anchor**, not
the nearest descendant IDs in the human-readable checklist above:

| Top-level anchor | One-based MathML ordinals | Content |
| --- | --- | --- |
| `fs-id1170655221887` | 1–4 | Expression table |
| `fs-id1170655090988` | 1–5 | Equation table |
| `fs-id1170654953357` | 1–8 | Four worked questions, then their four repeated answer formulas |
| `fs-id1170655166808` | 1–2 | First practice |
| `fs-id1170655205588` | 1–2 | Second practice, including the power |

Every record also retains its nearest source ID as explanatory metadata.
Removing the worked solution's absent/present `mrow` distinction would change
the registered tree and fail dispatch. Source module/section/scope and source,
edits and shared-phrase hashes are explicit prerequisites; the existing
MathML matcher alone does not establish those external hash prerequisites.

All three table records reuse the established `source_cnxml`, `table_id`,
`source_shape` and `expected` pattern from name-whole. Complete source trees
include their original `aria-label` or `summary`, headers, body rows, cells,
emphasis and formulas. Exact canonical hashes bind all nine source-derived
target table trees, and separate registered target linguistic attributes make
the summary/aria obligation explicit. The hash algorithm is the existing
`build_units.tree_key` followed by UTF-8 SHA-256, not an ad hoc text flattening.

The headerless `eip-10` is an answer table, never a missing-header error to fix
by inventing visible labels. Its finite readout includes all four source part
markers, formulas, classifications and equals-sign reasons. The surrounding
worked-solution title remains the outer answer cue. The two other tables read
every actual header/body cell in row order. Table speech is emitted once, not
again as the full aria/summary text followed by a recursive duplicate.

### Narration choices and renewed canon consultation

Fully read the current local C29 `kurung`, C30 `tutup`, and C07 `lima` readable
entries at this stage. Their hashes, and the six relevant entries actually read
at the earlier source/revision stage, were checked against the locked copies:
nine consulted readable hashes total. Current local shelf remains **30**;
the online entries below are not silently added to that count.

- C29/C30 support the writing-sign and open/close components. All six source
  parenthesis pairs are spoken with `bukak/tutup kurung biasa` in Javanese and
  `buka/tutup kurung biasa` in Indonesian. This is finite provisional prosody.
- C07 directly supports **sèket** and **salawé**. The coordinator changed the
  earlier target `seket` fields to `sèket` before these rules were bound. The
  rules read 53 as `sèket telu`, and 25 as `salawé`; the old helper spellings are
  not reused. The earlier text-draft hash/XML witnesses above remain historical
  snapshots, not the current revised target witnesses.
- All nine implied products are explicitly spoken as `ping` / `kali`; no
  visible operator is inserted. Letter `n` is `aksara en` / `huruf en`, including
  prose cells. Existing `x` and `y` use explicit letter names too. The adjacent
  word-column coefficient `dua y` / `loro y` is spoken as two times the letter
  `y`, without counting it as another source MathML site.
- The stacked fraction is read with numerator `x`, denominator `y`, and an
  explicit end-of-fraction marker. Source Indonesian aria wording is retained
  as evidence, while finite mathematical speech describes the actual fraction
  in every track. The target Javanese description correction remains disclosed.
- The one superscript reads **`aksara ye pangkat telu, pungkasan pangkat,
  dipara patbelas`** in both Javanese registers; Indonesian uses `huruf ye
  pangkat tiga, akhir pangkat, dibagi empat belas`. The power ends before the
  division. No expansion, evaluation, result or solved variable is supplied.

The topic-driven official [pangkat lookup](https://kbji.kemendikdasmen.go.id/kata/pangkat)
was read in full, followed by the complete
[rambang entry](https://kbji.kemendikdasmen.go.id/kata/rambang). The latter
directly attests mathematical powers/repeated equal factors; ordinary pangkat
headwords on the former page concern departure/rank. This is new useful lexical
evidence, not proof that a particular `rambang telu` spoken construction is
standard or familiar to learners. In agreement with the coordinator, retain
**pangkat as an overt provisional school loan** in this first finite readout,
and record `rambang` as an attested alternative for educator review and future
topic-driven acquisition. Both full web pages were read but neither was acquired
locally in this task. The retrieved example's flattened `43` typography is not
copied into the unit's source or fixtures. `pungkasan pangkat` is a declared
auditory end marker, not a newly proven canonical compound or a source glyph.

The exercise task is classification. Every question formula is therefore read
as mathematics, with **no expression/equation label, computed answer or answer
cue** appended. Classifications are spoken only from the original solutions;
the eight consistency records are verification metadata, not prompt audio.
The ordinary two untitled practice solutions still require their source-bound
`Wangsulan` / `Jawaban` cues.

### Actual read-only checks

**PASS, with production integration still pending.**

1. Both pinned module hashes, exact [28:40] source selection, revised edits and
   shared-phrase hash match. All 21 formulas dispatch in all three tracks.
2. A separate finite test-only token walk validates every number, letter,
   arithmetic operator, implicit product, parenthesis, fraction order and power
   boundary across all **63** mathematical readings. It is not shipped as a
   general parser and performs no expression evaluation.
3. Complete source-table trees and all **9** target table bindings match,
   including summary/aria and the revised accent spelling. Translation of
   summary is applied explicitly in memory for this proof; it is not silently
   claimed as existing production support.
4. All eight classifications agree with the corresponding source formula's
   equals-sign presence; worked and practice answer order is preserved. All
   question-formula readings are free of classification/answer labels.
5. **23 deliberate mutations are rejected**: changed numeral/operator/letter;
   reversed or flattened fraction; flattened/changed power; division moved
   inside the power; changed delimiter/`stretchy`; fixture anchor/ordinal/
   namespace/operator changes; source aria/summary changes; removed table row
   or header; target summary/aria/classification changes; wrong spoken answer
   classification; and classification leakage into question audio.

These checks use current exact MathML dispatch plus independent table/target/
readout checks. They do **not** establish that the shared production dispatcher
already supports these three new table fixtures, summary replay, summary-to-label
rendering, or complete unit builds. No writer or production build was invoked.

| Current rule-stage witness | SHA-256 |
| --- | --- |
| `audio/a10-expressions-equations.rules.json` | `5a5f498d85de96315ddfc4dbb9e093a619dbd32e5574c431e07a2676a69d8495` |
| Coordinator-revised `translation/a10-expressions-equations.edits.json` | `37913876fb43a5c4f2aa7af304166e137702760cd5fafc86cf1758a2d35da0f9` |
| Shared phrases used | `adc145f5957bf18281cd737b9e1079af4d24f6d5505c9485138de3018b2ab5b8` |

Standalone reader/three transcripts/three SSML tracks, production receipts,
coverage updates, visual and native educator/register review, pronunciation,
screen-reader and listening checks remain pending for this unit. This is
additional full-workflow progress, not completion of either book or AX-2.

## Root production integration — 2026-08-31

The preceding pending states and hashes describe their original draft/rule
handoff. This unit is now registered and generated: three source-bound CNXML
tracks, an offline reader, three transcripts and three SSML files, plus exact
draft/build receipts and coverage. The 38 phrase rows are unchanged from the
revised sèket handoff. Summary is now a production translation surface and a
reader-label fallback; all three tables are gated by exact source and target
trees/hashes before fixed narration. All eight classifications and two answer
cues are explicitly checked. No answer classification is added to question
math, and no equation is solved.

Root read the full phrase map and all three generated transcripts, rechecked
fraction/power scope and table equivalents, and reread C07/C29/C30. C34 rambang
is now locally acquired/read with rounding entries C31-C33; keep the previous
canon snapshot as historical. Pangkat remains a declared provisional loan.
Nine production regression tests pass, including 63 independent finite formula
readings and deterministic replay. Human, browser/screen-reader, synthesis,
pronunciation and listening reviews remain pending. Current output hashes are
in `a10-expressions-equations.build-receipt.json`; whole assignment unfinished.
