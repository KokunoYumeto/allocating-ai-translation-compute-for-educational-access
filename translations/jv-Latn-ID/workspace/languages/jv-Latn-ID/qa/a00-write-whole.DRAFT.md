# A00 whole-number writing draft witness

Status: source-keyed translation draft only. This does not complete the section's
full workflow, module `m81243`, A00, A10, or AX-2. This handoff creates only
`translation/a00-write-whole.edits.json` and this witness. No shared descriptor,
builder, lock, asset, narration rule, reader, coverage ledger, or Git state was
changed. Human language review, visual review, screen-reader testing, voice
selection, pronunciation review, and listening review are not claimed.

## Complete source boundary

Read the complete pinned Indonesian and English A00 / `m81243` /
`fs-id1339359` subsection, including all text/tails, three how-to steps, two
worked examples, both parts of the first example, all three media alts, every
MathML tree, and four practice exercises with solutions. This is the entire
“Menggunakan Nilai Tempat untuk Menulis Bilangan Cacah” / “Use Place Value to
Write Whole Numbers” subsection, not a selected child slice.

- Previous sibling: `fs-id1321580`, using place value to name whole numbers.
- Included boundary ends with practice note `fs-id1397780`, solution
  `fs-id2262414`, and answer paragraph `fs-id1395137`.
- Next excluded sibling: `fs-id2472737`, “Membulatkan Bilangan Cacah” /
  “Round Whole Numbers.” Its opening paragraph `fs-id1333125` introduces the
  source's 2013 New York population example. No rounding text is translated
  by this handoff.
- Indonesian repository commit:
  `3de9207f56f8b5c57c017abf973fb04e00d740f1`; module Git blob
  `90def09ee1dbfdc66aa8bc910938ad7684668e97`; module SHA-256
  `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251`.
- English repository commit:
  `38cae454e644abf9f0a623e876994553881597c9`; module Git blob
  `612244f80ecb6bce0f811c9d99204ae2f9f7a4f5`; module SHA-256
  `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`.
- Raw selected-section byte basis begins at its exact opening `section` tag
  and ends immediately after its closing tag, excluding following whitespace.
  Indonesian: 6,845 bytes, SHA-256
  `49baf504da12da5fb93fd36a212ca69c990a2c9785c13f3bbf3c6c59fbca1229`.
  English: 6,639 bytes, SHA-256
  `ddfaa67e2fc8e2eca212b09fa13aaaa40aa836e8f8b585094445b9236e191a95`.
- These are exact pinned Git bytes, not Windows checkout newline-normalized
  substitutes. Namespace-aware canonical section SHA-256 using
  `ElementTree.canonicalize(..., strip_text=True, rewrite_prefixes=True)`:
  Indonesian
  `e72504d52e66936cbc0767daff582a4c2ccd673fd31ad5d801f37caed5fd7c12`;
  English
  `8e2b895dc38802c37ea93b0df725ae77f40fc6c033138bcf4de16d48dea764c9`.

After the title, the exact direct-child order is:

1. `fs-id2607182` — reverse-process introduction.
2. `fs-id2398163` — three-step how-to note, list `eip-100`.
3. `fs-id2376697` — worked example, parts `ⓐ` and `ⓑ`.
4. `fs-id1542693` — 53,809,051 practice.
5. `fs-id2437124` — 2,022,714,466 practice.
6. `fs-id3202693` — state-budget worked example.
7. `fs-id1805534` — Earth-to-Mars distance practice.
8. `fs-id1397780` — aircraft-carrier weight practice.

All 57 unique source IDs, in tree order:

`fs-id1339359`, `fs-id2607182`, `fs-id2398163`, `eip-100`,
`fs-id2376697`, `fs-id1340436`, `fs-id845531`, `fs-id1576302`,
`fs-id2264653`, `fs-id1786412`, `fs-id3402446`, `fs-id2198541`,
`fs-id4300938`, `fs-id2668978`, `fs-id1726897`, `fs-id1683995`,
`fs-id2159900`, `fs-id3429801`, `fs-id2903601`, `fs-id1374355`,
`fs-id2880619`, `fs-id1542693`, `fs-id2646708`, `fs-id3436547`,
`fs-id2270159`, `fs-id2149876`, `fs-id998472`, `fs-id4163187`,
`fs-id2437124`, `fs-id2202956`, `fs-id1402052`, `fs-id1337332`,
`fs-id1792489`, `fs-id1330293`, `fs-id1885399`, `fs-id3202693`,
`fs-id1336757`, `fs-id1917299`, `fs-id2590590`, `fs-id1949045`,
`fs-id2634266`, `fs-id1345376`, `fs-id2319817`, `fs-id1805534`,
`fs-id1485641`, `fs-id1929413`, `fs-id2262938`, `fs-id1800228`,
`fs-id1779102`, `fs-id865214`, `fs-id1397780`, `fs-id2133886`,
`fs-id1781552`, `fs-id1515747`, `fs-id1586764`, `fs-id2262414`,
`fs-id1395137`.

There are no source links, cross-reference targets, tables, equation wrappers,
or MathML IDs. The three images are inline `media` elements, not numbered
`figure` wrappers. Retain the original source IDs and classes, the circled
`ⓐ`/`ⓑ` tokens, the three explicit `newline` elements, and both solution titles.

## Draft and read-only checks

The new ledger contains 33 unique exact trimmed Indonesian phrase keys with
separate `jv-academic` and `jv-conversation` target columns. Both tracks use
ngoko-derived instructional language; academic versus conversational register
is not presented as a ngoko/krama distinction. Cardinal names are deliberately
identical across registers.

Draft file at this checkpoint: 15,387 bytes; SHA-256
`16693129ef90fb6ae43c9a312a86daf650896f6572671933d09ee56129912a9f`.

Read-only checks actually run, without writing draft CNXML or invoking a build
CLI:

- Extracted the exact source phrase-key set from all text/tails and media
  accessibility text; it equals the ledger's 33-key set, with neither missing
  nor unused keys. The only overlap with the shared phrase map is
  `Penyelesaian`, and both target strings agree with the existing shared row.
- Translated the pinned source in memory through the production `translated`
  helper, replaying the shared-map merge. Ran `draft_units.validate` for both
  registers: source structure, all IDs, MathML attributes/non-prose tokens,
  all digit sequences in prose/alt text, and target language tag pass.
- Independently removed only each MathML root's external prose tail and
  compared complete serialized source/target trees. All six match in both
  tracks, including the entire two currency `mtext` nodes. This is stricter
  than a check that masks every `mtext` as freely translatable language.
- Repeated both translations in memory and obtained identical serialized
  outputs. This establishes deterministic translation for these inputs, not
  deterministic readers or audio products that do not exist yet.
- Recomputed the four complete word-form numbers from finite group-value
  witnesses in both Javanese tracks, and separately recomputed the three
  multiplier-and-unit quantities. All seven agree with their source answers.
- Inspected the reconstructed prompt/solution text, including the inline
  circled part marker, currency, units, and leading-zero explanation.

No numeric answer is newly invented by this draft. The two entirely numeric
practice answers already pass through unchanged; the two numeric-plus-unit
answers have explicit phrase rows so their unit treatment is reviewable.

## All six MathML trees and punctuation

Each MathML occurrence is ordinal 1 under its nearest enclosing ID below.
Every source formula is `math/mrow`; none has an ID or an `mstyle` wrapper.

| Anchor | Exact child tokens | Role |
| --- | --- | --- |
| `fs-id1726897` | `mn:53,401,742`, `mo:.` | Worked answer ⓐ |
| `fs-id1374355` | `mn:9,246,073,189`, `mo:.` | Worked answer ⓑ |
| `fs-id2590590` | `mtext:$77` | Budget prompt; external prose supplies billion |
| `fs-id2319817` | `mtext:$77,000,000,000.` | Complete budget answer |
| `fs-id1800228` | `mn:34` | Distance prompt; external prose supplies million miles |
| `fs-id1586764` | `mn:204` | Weight prompt; external prose supplies million pounds |

The two `mo` full stops are sentence punctuation. The final full stop in
`$77,000,000,000.` is inside the `mtext` and must remain there in the visible
source-preserving MathML; narration can treat it as sentence punctuation.
None is a decimal point or continuation ellipsis. No ellipsis or source
continuation wording occurs in this subsection. Source commas separate
three-digit groups; they are not decimal commas.

## Numbers, questions, and answers

All leading-zero group strings remain exact, notably `073`, `051`, `022`,
and every `000`. Do not flatten a group through integer parsing and then
reconstruct it without its width.

| Source prompt / context | Group decomposition and complete answer | Source answer location |
| --- | --- | --- |
| Worked ⓐ: 53 million; 401 thousand; 742 | `53 / 401 / 742` → `53,401,742` | `fs-id1726897` |
| Worked ⓑ: 9 billion; 246 million; 73 thousand; 189 | `9 / 246 / 073 / 189` → `9,246,073,189` | `fs-id1374355` |
| 53 million; 809 thousand; 51 | `53 / 809 / 051` → `53,809,051` | `fs-id4163187` under `fs-id998472` |
| 2 billion; 22 million; 714 thousand; 466 | `2 / 022 / 714 / 466` → `2,022,714,466` | `fs-id1885399` under `fs-id1330293` |
| Approximately 77 billion dollars | `77 / 000 / 000 / 000` → `$77,000,000,000.` | `fs-id2319817` |
| Approximately 34 million miles | `34 / 000 / 000` → `34,000,000 mil` | `fs-id865214` under `fs-id1779102` |
| 204 million pounds | `204 / 000 / 000` → `204,000,000 pound` in JV | `fs-id1395137` under `fs-id2262414` |

The finite cardinal group witness used in the checks includes `sèket telu`
= 53, `patang atus siji` = 401, `pitung atus patang puluh loro` = 742,
`rong atus patang puluh enem` = 246, `pitung puluh telu` = 73,
`satus wolung puluh sanga` = 189, `wolung atus sanga` = 809,
`sèket siji` = 51, `rolikur` = 22, `pitung atus patbelas` = 714, and
`patang atus sewidak enem` = 466. Scales are the source's thousand, million,
and billion groups. This is a finite arithmetic witness, not a certification
of a general Javanese number parser or of native idiomaticity.

The `ⓑ` explanation correctly places its required zero in the hundred-thousands
position: group `073` is 73 thousand, not 730 thousand. The how-to initially
says to draw three blank positions per period; the worked explanation later
excepts the first period, and the closing reminder says it may be excepted.
Both source stages remain in the target rather than silently reconciling them.

## Three media inputs and localization handoff

The actual Indonesian source references, all with `mime-type=image/svg+xml`,
are:

1. Media `fs-id2668978`, parent `fs-id4300938`:
   `../../media/CNX_BMath_Figure_01_01_016_img.jpg.id-ID.svg`.
   Three word blocks point to `53`, `401`, `742`, with labels millions,
   thousands, ones. Read SVG title/description and visible text: it stores
   digit strings `5 3`, `4 0 1`, `7 4 2`, separated by comma text nodes.
2. Media `fs-id2903601`, parent `fs-id3429801`:
   `../../media/CNX_BMath_Figure_01_01_017_img.jpg.id-ID.svg`.
   Four word blocks point to `9`, `246`, `073`, `189`. The inherited SVG
   expressly stores `0 7 3`, not `7 4 2`. Its description refers to Indonesian
   word groups and therefore also needs localization.
3. Media `fs-id1345376`, parent `fs-id2634266`:
   `../../media/CNX_BMath_Figure_01_01_018_img.jpg.id-ID.svg`.
   A `77 billion` word block is followed by three absent word blocks; the
   corresponding digit groups are `77`, `000`, `000`, `000`. Its stored
   digit text is `7 7` followed by three `0 0 0` groups.

The English source refers to corresponding
`../../media/CNX_BMath_Figure_01_01_016_img.jpg`, `017_img.jpg`, and
`018_img.jpg` JPEGs, with `mime-type=image/jpeg`. The complete names retain
the same `CNX_BMath_Figure_01_01_` prefix. No image was copied, acquired,
generated, edited, or raster-transformed by this draft handoff.

Exact inherited Indonesian SVG provenance:

| Suffix | Bytes | Git blob | SHA-256 |
| --- | ---: | --- | --- |
| `016_img.jpg.id-ID.svg` | 3,085 | `1795fe6706292a8f6135ca69f6b93dd17ffd7f03` | `187a8889ef732265940b2d9d891eb744e4340803fea68196fc6f70a60cf2262a` |
| `017_img.jpg.id-ID.svg` | 3,733 | `43a18f1878e533d55a3c8e6cda5fdd0b2748f77c` | `75634e60f0c1e113151d4a298d8d1c3b88466d78344459bd20fc195df5206a5a` |
| `018_img.jpg.id-ID.svg` | 3,405 | `67d92aa2732d4dc6326df7b92cdfe8c59e7d4e65` | `2967aa006d1b5c2892b6b71459745479ddc9c700e89e4ebac86bc76c8737f77b` |

Separately, read each JPEG already retained in the pinned Indonesian
repository and computed its Git-blob hash. Each equals the canonical English
commit's corresponding JPEG object reference. This is byte-identity evidence
for the JPEG source, not a claim that the inherited SVG geometry is identical
to the JPEG or that either has received visual review.

| JPEG suffix | Bytes | Git blob, equal to canonical EN reference | SHA-256 |
| --- | ---: | --- | --- |
| `016_img.jpg` | 63,713 | `03148c992db97ce26403f7694c09dbeb8e3066fd` | `663626cdecaa1658cf32b1d6f57b0720a8d221adf6db5651009ffda3e5952866` |
| `017_img.jpg` | 75,281 | `317ac5f4ae127c4e86fcf176b9f76992bdb0d904` | `cf74469454d25b38e1beecd91fb0b0c1e0b968dfb9fa7683f6602bb21c681b1b` |
| `018_img.jpg` | 52,776 | `4768b4edf20ccd0f899f5f2389dad8f72fcc7e8a` | `e9335d572b341614390c133ff913875580c15936f14833fc0577f287cbe1c6b2` |

Future assets should localize SVG title/description and linguistic labels in
the two registers using the inherited Indonesian geometry. Preserve numbers,
commas, paths, coordinates, IDs, group order, and arrows. Mathematical words
and labels can be the same across registers even when descriptive sentences
differ. Keep provenance and canonical JPEG identity separate from the geometry
comparison. No shared asset manifest has been changed at this checkpoint.

## Canon consultation and terminology decisions

Consulted actual readable local KBJI material while reading/drafting, then
revisited the relevant entry lines while reviewing the assembled draft. This
was not a substitution of a compacted summary for the canon. The consulted
readable paths are under `downloads/jv-Latn-ID/canon/`:

- C01 `wilangan.txt` and C02 `cacah.txt`: number/count sense, not the unrelated
  chopping sense. The complete mathematics label `wilangan cacah` remains a
  provisional compound rather than a claimed dictionary-standard phrase.
- C07 `lima.txt`: actual `sèket` at line 22 supports the fifty components in
  53 and 51. `salawé` at line 72 was also consulted; no 25 occurs in this
  section, so it is not introduced into the draft.
- C18 `likur.txt`: actual `rolikur` at line 4 directly supports 22. The
  complete 714/466 compounds remain a separate compositional judgment.
- C19 `atus.txt`: number sense `atus`, `satus`, and `rong atus` at lines
  1–5, plus actual `pitung`/`pitung puluh` at lines 41–44. Do not use the
  unrelated dry/finished sense of `atus`.
- C20 `enggon.txt`: ordinary place/location and `panggonan` senses at lines
  1–5. This does not attest the technical compound `nilai panggonan`.
- C24 `ewu.txt`: `éwu` and `éwuan` at lines 1–2; the distinct `éwuh` entry
  is not the numeral. Retain the accent consistently.
- C25 `yuta.txt`: `1yuta` = million at line 1, not the separate bewildered
  sense. Productive `yutanan` is a draft period label.
- C26 `wolu.txt`: eight at line 1. `wolung` before tens/hundreds is a
  compositional form requiring the ordinary native-language review.
- C27 `sanga.txt`: nine and explicit `sangang puluh`/`sangang atus` at lines
  1–2 support nine-related compounds; the whole `sangang milyar` phrase is
  not thereby independently standardized.
- C28 `sewidak.txt`: sixty at line 1 supports the 466 word form. Do not
  mechanically replace it with a literal Indonesian-derived tens compound.

Keep the established provisional terminology `nilai panggonan`, `periode`,
`satuan`, `atusan éwu`, `yutanan`, `milyar`, `milyaran`, `digit pangisi`, and
`wujud standar`. The conversational standard-form prompt also says `nganggo
digit` to make its task explicit. `Lan` in diagram descriptions joins
description clauses; it is not inserted into any whole-number cardinal name.

Four word-form prompts restore inter-period commas in target text only:
both items in `fs-id2264653`, `fs-id2149876`, and `fs-id1792489`. The
Indonesian keys remain exact. This editorial choice follows the preceding
section's explicit naming convention and the actual English witness; no
comma is added to or removed from source MathML or digit strings.

Unit decision agreed with the coordinator: use overt `pound` in Javanese for
English `pounds` / Indonesian `pon`. This keeps the source English unit and
number without conversion. Do not assert any Indonesian unit equivalence,
conversion factor, or standardized Javanese unit terminology without an
independent authoritative unit witness. `Mil` remains the source mile unit.
`Pound` pronunciation and the final Javanese unit phrasing require review.

## Source discrepancy and narration blockers

Material discrepancy: the English alt at `fs-id2903601` says the
seventy-three-thousand block points to **742**. The Indonesian alt corrects
this to **073**, the inherited SVG explicitly contains `0 7 3`, and both
sources give the complete number `9,246,073,189`. The targets retain 073.
No pinned source is rewritten and no answer is inferred from the bad English
alt in isolation.

The budget image's English word blocks described as `null` correspond to the
Indonesian `kosong`: the word blocks are empty, while the digit groups really
contain three zeroes each. The target makes no blank-equals-zero substitution.

This lesson reverses naming: learners must write a digit representation from
a word-form input. A narration that reads both the question and its answer
only as the same cardinal name would obscure the assessed skill. Proposed
integration requirements, not implemented or certified in this handoff:

1. Keep complete word-form prompts as cardinal names. For the three mixed
   prompts, retain the existing 77-plus-billion, 34-plus-million-miles, and
   204-plus-million-pounds quantities without prematurely dictating the
   complete requested digit-form answer.
2. Read displayed digit answers literally, with audible comma boundaries,
   all leading and repeated zeroes, and units after the solution/answer cue.
   The four practice answers are plain CNXML paragraph text, not MathML,
   and therefore require source-bound answer handling too.
3. Budget speech must treat the prompt's `$77` and external `miliar` /
   `milyar` as one amount. State the US-dollar unit explicitly without reading
   77 dollars followed by a disconnected billion, duplicating the multiplier,
   or dropping the unit. For the digit-form solution, preserve all eleven
   digits and its three grouping commas before the spoken unit.
4. The two currency `mtext` nodes are nonlinguistic fixed notation. Exact
   target/source validation must reject `$` → `€`, removal of `$`, digit
   changes, comma changes, and the final-period change even when the sequence
   of digits happens to be unchanged. The coordinator identified the current
   blanket `mtext` masking in `narration_tree_key` as needing tightening for
   these nodes; this handoff does not edit that helper.
5. Narrate chart arrows from words to digit groups, not in the previous
   naming lesson's opposite direction. Make `073`'s initial zero and the
   budget chart's empty-word/`000` distinction audible. Bind fixture
   descriptions to exact source alt, media path, ID, and translated target.
6. No generic continuation phrase should be added for sentence-final periods.
   Fail closed on unrecognized grouped-number or currency spellings instead
   of guessing a full answer or swallowing punctuation.

The source's approximate Earth-to-Mars distance, approximate state budget,
and unqualified aircraft-carrier weight remain textbook inputs, not newly
researched current factual assertions. No modernization or conversion was
performed. Integration, localized assets, finite narration rules, deterministic
reader products, mutation tests, and the outstanding human checks remain work
to do before this section's workflow is complete.

## Later narration-input handoff: finite AX-2 rules

After the translation handoff above, created
`audio/a00-write-whole.rules.json` and appended this narration-stage witness.
The earlier paragraphs describe the translation-only checkpoint; they do not
claim that narration inputs remain nonexistent after this addition. No shared
script, generated reader, source lock, asset, or Git state was changed by this
narration-rule handoff. The coordinator independently owns integration and
asset work. The full A00/A10/AX-2 assignment is still unfinished.

Rule-file checkpoint: 63,865 bytes, SHA-256
`a260ecac3bcfcbd2cd65d2a498d1648f1ab83778f69bfeb4fb4d1f6e48ee89dd`.
The rules bind the exact source section hash above, the current translation
ledger SHA-256, the shared phrase-map SHA-256, and registered per-track target
tree hashes for the six prose and three media fixtures. The file has three
tracks (`jv-academic`, `jv-conversation`, `id-academic`), six MathML fixtures,
six complete prose fixtures, three chart fixtures, seven finite number
decompositions, four practice-answer invariants, three quantity invariants,
and an explicitly empty table-fixture array because this section has no table.

No generic large-integer or currency parser is installed or authorized. Exact
source CNXML/MathML strings are stored as original source substrings; their
inherited default CNXML and `m` namespaces must be supplied when parsing.
Target hashes use `build_units.tree_key`, removing only the external element
tail and canonicalizing formatting whitespace/prefixes, not masking numbers,
units, punctuation, linguistic tokens, or media paths.

### Exact MathML dispatch anchors

The production dispatcher uses the section's **direct-child block** anchor
and its one-based descendant MathML ordinal. This differs from the
nearest-paragraph inventory earlier in the witness; both inventories refer
to the same unchanged six source trees.

| Fixture | Direct-child anchor / ordinal | Nearest paragraph | Speech role |
| --- | --- | --- | --- |
| `A00-WRITE-M01` | `fs-id2376697` / 1 | `fs-id1726897` | Literal `53,401,742` answer |
| `A00-WRITE-M02` | `fs-id2376697` / 2 | `fs-id1374355` | Literal `9,246,073,189` answer |
| `A00-WRITE-M03` | `fs-id3202693` / 1 | `fs-id2590590` | Cardinal coefficient 77, only inside required P03 full prompt |
| `A00-WRITE-M04` | `fs-id3202693` / 2 | `fs-id2319817` | Literal `$77,000,000,000.` answer with overt US-dollar unit |
| `A00-WRITE-M05` | `fs-id1805534` / 1 | `fs-id1800228` | Cardinal 34 followed by source million miles |
| `A00-WRITE-M06` | `fs-id1397780` / 1 | `fs-id1586764` | Cardinal coefficient 204, inside required P06 weight prompt |

M03 and M06 carry `requires_prose_fixture`, `requires_prose_element`, and
`standalone_readout_authorized: false`. All six MathML trees must bind before
any whole-paragraph override. A production path that emits the isolated
coefficient without its required complete prompt must fail closed, not
silently fall back to generic currency or unit speech.

### Six exact prose fixtures and source-unit clarification

| Fixture | Exact source element | Role |
| --- | --- | --- |
| `A00-WRITE-P01` | `fs-id4163187` | Literal practice answer `53,809,051` |
| `A00-WRITE-P02` | `fs-id1885399` | Literal practice answer `2,022,714,466` |
| `A00-WRITE-P03` | `fs-id2590590` | Full budget prompt with coherent amount/unit order |
| `A00-WRITE-P04` | `fs-id865214` | Literal practice answer `34,000,000 mil` |
| `A00-WRITE-P05` | `fs-id1395137` | Literal practice answer `204,000,000 pound` in audio |
| `A00-WRITE-P06` | `fs-id1586764` | Full weight prompt, still 204 plus million, with pound unit |

P03's Javanese amount is `pitung puluh pitu milyar dolar Amerika Serikat`;
Indonesian uses `tujuh puluh tujuh miliar dolar Amerika Serikat`. The exact
complete prompt retains its instruction to write the budget in standard
form. This scopes the source `$77` and external billion together, states the
unit once, and does not dictate the eleven-digit answer in the question.

P06's Javanese amount is `rong atus papat yuta pound`; Indonesian uses
`dua ratus empat juta pound`. The English source explicitly says pounds.
The coordinator approved this overt source-English loan in Indonesian audio
as well as Javanese, so both the ID prompt and answer speak `pound`
consistently. The visible Indonesian `pon` remains unchanged and source/target
CNXML is hash-bound. This is a declared **audio-only unit clarification**,
not a unit conversion, a claim of any Indonesian `pon` equivalence, or an
assertion that the loan's pronunciation is already tested. P06 is the sixth
fixture added specifically to avoid inconsistent unit wording between the
ID prompt and P05 answer.

No whole-prose override is needed for the 34-million-mile prompt: M05 reads
the fixed coefficient as `telung puluh papat` / `tiga puluh empat`, and
its existing source/translated tail supplies million miles. The complete
digit-form answer is confined to P04 after its answer cue.

### Preserving the inverse exercise in audio

The two worked word-form prompts and two word-form practice prompts retain
their cardinal words. The three mixed quantities retain cardinal coefficients
plus their source magnitudes and units. None is expanded into the requested
printed standard-form answer before a solution cue.

The three displayed MathML answers and four plain paragraph answers instead
say `digit saka kiwa menyang tengen` / `digit dari kiri ke kanan`, then
each printed digit separately, with explicit `tandha koma` / `tanda koma`
between groups. For example, P01's Javanese answer is:

> digit saka kiwa menyang tengen: lima, telu; tandha koma; wolu, nol, sanga; tandha koma; nol, lima, siji.

This retains the final `051`, not merely its integer value 51. M02 retains
`073`, P02 retains `022`, and the budget, distance, and weight answers retain
every repeated zero in all `000` groups. The budget answer names all eleven
digits and three grouping commas, followed by `dolar Amerika Serikat`.
Distance and weight answers likewise retain `mil` and `pound` after the
literal digit sequence. Final narration periods mark paragraph/sentence
pauses; no source punctuation or visible digit string is edited.

The four untitled practice solutions have exactly one required spoken
`Wangsulan.` / `Jawaban.` cue before their literal answers. The two worked
solutions retain their existing solution-title reading without an additional
duplicate cue. Complete generated cue placement has not yet been tested by
this rule author.

### Three chart descriptions

- C01 / `fs-id2668978`: three source word blocks map to `53 / 401 / 742`.
  Each block's cardinal wording and period label are spoken before its
  mapped literal digit sequence; comma boundaries remain explicit.
- C02 / `fs-id2903601`: four source word blocks map to
  `9 / 246 / 073 / 189`. The leading zero is explicitly retained, and
  the corrected Indonesian 073 is used rather than the English alt's
  erroneous 742. Direction is words → digit groups, not the earlier
  naming lesson's reverse direction.
- C03 / `fs-id1345376`: the first block names 77 billion and points to
  `77`. The remaining three **word blocks** have no words, while their
  **digit groups** each contain `000`. The narration explicitly
  distinguishes these facts and does not replace a zero group with
  “blank column.”

Each chart fixture contains the complete source media CNXML, exact source
alt/path, expected target alt and tree hash for all three tracks, group
strings/scales, period labels, finite printed-digit readings, word-label
readings, arrow direction/mappings, and empty-word-block indices. Source
geometry is not changed by these narration fixtures; asset derivative work
belongs to the coordinator's separate handoff.

### Actual narration-stage checks and limits

The following read-only checks were run on the new rule file:

1. Production `source_bound_math` successfully binds all six original
   source trees for `id-academic`, using their exact direct-child anchors
   and ordinals.
2. All six prose and three media source trees match the pinned Indonesian
   source. All 27 registered nonmath target-tree hashes match the freshly
   translated two Javanese tracks and original Indonesian track, including
   exact source/target accessibility text and media paths.
3. A finite verification-only digit decoder reconstructed all 21 literal
   answer readouts (seven values × three tracks), preserving exact comma
   groups, leading zeroes, and expected units. It was not installed as a
   runtime number parser.
4. All nine cardinal coefficient readouts (77, 34, 204 × three tracks)
   match the authored finite names. All 33 printed chart-group readouts
   match their exact group strings; every nonempty chart word label occurs
   in the matching chart's expected speech.
5. Seven group/scaling witnesses recompose their source integer values;
   the three quantities separately satisfy 77 × billion, 34 × million,
   and 204 × million. Cardinal witnesses verify value; they are not a
   substitute for literal answer speech.
6. The production Indonesian MathML matcher rejects five independent
   altered targets: `$77` → `€77`, removal of the final currency period,
   `073` → `73`, a changed top-level anchor, and `mrow` → `mstyle`.
7. Independent registered-target hash guards reject twelve nonmath
   mutations across the three tracks: missing answer zero, missing chart
   alt zero, changed chart image path, and changed weight unit. These are
   fixture-integrity probes, not a claim that future unit dispatch already
   enforces every field.
8. P03/P06 contain their overt unit once and contain neither an expanded
   literal-digit answer nor numeric glyphs. Source tables and table
   fixtures both number zero.

At the last check in this handoff, `a00-write-whole` was not yet present in
`draft_units.UNITS`. Therefore full Javanese production binding through the
descriptor-dependent registered-mtext path, whole-prose/chart dispatch,
complete transcript/SSML output, cue counts, reader determinism, and end-to-end
fail-closed behavior remain coordinator integration work. The successful
Indonesian matcher and independent three-track fixture checks are not
misrepresented as a full production pass.

Canon was revisited while creating and reviewing these rules: actual C07
`lima.txt` entries for `sèket` and `salawé`, C18 `likur.txt` for `rolikur`,
C19 `atus.txt` for `satus`, `rong atus`, and `pitung puluh`, C24 `ewu.txt`
for `éwu`/`éwuan`, C25 `yuta.txt`, C26 `wolu.txt`, C27 `sanga.txt`, and
C28 `sewidak.txt`. Bare `wolu`/`sanga` name printed digits; attributive
`wolung`/`sangang` remain within cardinal word labels. No unaccented generic
`seket`/`selawe` helper was used for these authored fixtures. All composed
cardinals, period labels, pound pronunciation, literal-digit prosody, and
both registers remain subject to human review.

No synthesized audio, chosen voice/provider, provider-locale compatibility,
native educator approval, visual pass, screen-reader pass, or listening pass
is claimed by this narration-input handoff.

## Root production integration after d0732f0 — 2026-08-31

The preceding source/phrase/rule handoffs are historical. The entire section
is now registered and generated as three CNXML, reader, transcript and SSML
tracks. Exact full source and target replay, six math, six prose and three chart
fixtures gate speech. M03/M06 cannot be narrated outside their required whole
budget/weight paragraph. All seven printed answers retain literal digits and
commas; four untitled practice solutions get exactly one answer cue each.

Root read the actual ID/EN section, all phrase rows, complete rules and all
three generated transcripts, revisiting C07/C19/C24/C25. Actual transcript
inspection exposed a duplicated part label at fs-id2880619. Its inline circled
b is now read as be after the already spoken bagean/bagian, without an extra
list-item colon; all visible source/target wording remains unchanged.

Eight writing-workflow tests and three writing-asset tests pass; the complete
136-test suite passed before metadata-only status/hash refresh. Current phrase
ledger SHA-256 is 278ca54fc22c725d55484ad6ab1e5e6fb5268bfd3362758efa3dedaacb2c68ad;
the difference from the rule-stage ledger is explicit integration-status
metadata, not phrase wording. Build receipt binds current rules/assets/outputs.
Three distinct SVG designs were statically rendered earlier (register pairs
are byte-identical); see ASSETS.md. No integrated browser, native educator,
screen-reader or listening approval is claimed. Independent unit review is
pending and the full A00/A10/AX-2 assignment remains unfinished.

## Independent integration review follow-up

WRITING_CHECKPOINT_REVIEW.md now records the completed post-fix review and its
140 passing tests. The plain-dictionary context-loss guard was repaired without
changing the saved writing outputs; all earlier reviewed output hashes remain
unchanged. This supersedes the earlier independent-review-pending status only.
It does not establish native language, integrated visual, screen-reader or
listening approval, and does not complete the full assignment.
