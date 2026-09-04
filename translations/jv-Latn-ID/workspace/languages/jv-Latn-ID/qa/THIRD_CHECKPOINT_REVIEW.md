# Third checkpoint — two new built excerpts

2026-08-31 · independent artifact review of `a00-digit-place` and
`a10-equality-symbols`, after the producer's C24–C28 / `éwu`–`éwuan` revision
and regeneration. Only this review file was written by this review task.

## Outcome

No material numerical, operand-order, answer, scope, or written-readout defect
was found in the final reviewed artifacts. All six transcripts were read in
full; their corresponding SSML, both readers, six compiled CNXML tracks,
source-bound rules, and embedded assets were checked against actual pinned
Indonesian and English inputs. This conclusion is not based solely on receipts.

The producer announced a canon-driven revision during the review. The
intermediate A00 input/output spelling mismatch was an in-progress rebuild,
not a final-artifact finding. After regeneration, the review independently
rechecked the actual files: `éwu`/`éwuan` is consistent in the new A00 Javanese
targets, scripts' registered readings, and localized chart labels. Numeric
facts and Indonesian source SVG bytes did not change. No semantic objection
to that documented revision was found.

Both read-only test files were also run independently with `python -B`:

- `scripts/test_digit_place_workflow.py -v`: 18 passed, zero skipped.
- `scripts/test_equality_workflow.py -v`: 18 passed, zero skipped.

No build command, synthesized audio, provider call, or shared-file edit was
made by this review. The tests exercise in-memory reconstruction and mutation
rejection; passing them does not certify language, rendering, or listening.

## Exact reviewed scope

| Unit | Source boundary | IDs per track | MathML per track | Spoken blocks per track | Media per track |
| --- | --- | ---: | ---: | ---: | ---: |
| `a00-digit-place` | Full `m81243/fs-id1883656`; nine direct children including title; through top-level `fs-id1282619`, solution `fs-id2619544`, final descendant `fs-id1807276` | 31 | 40 | 9 | 2 |
| `a10-equality-symbols` | `m82453/fs-id1170655150800` title context plus original children `[13:23]`; spacing `fs-id1171789687379` through practice `fs-id1170655124058` | 36 total / 35 new | 23 | 10 | 2 |

A10's contextual parent-section ID is not newly translated again. Its
spacing-only source node is retained in CNXML and the HTML reader but produces
no empty spoken block. A00's next section remains `fs-id1321580`; A10's next
excluded child is grouping-symbol introduction `fs-id1170654957487`.

Each unit has an unchanged Indonesian pivot, a provisional academic Javanese
track, and a conversational-ngoko Javanese track. These are excerpts, not
completed modules. The actual coverage ledger still records **0 complete,
2 partial, and 155 untranslated modules**. This review covers these two
additions only; it does not reapprove the earlier four excerpts or finish any
remaining A00/A10/AX-2 obligation.

## Mathematical and source-fidelity evidence

### A00 digit and place value

- `5,278,194` retains the contributions `5,000,000 + 200,000 + 70,000 +
  8,000 + 100 + 90 + 4`. The seven-item source list keeps each digit, its
  named position, and its contribution associated.
- The first chart retains fifteen columns, five three-column period groups,
  the source's four-row description, eight leading empty digit cells, and
  filled digits `5,2,7,8,1,9,4`. The worked chart retains the source's two-row
  description, seven leading empty cells, and `6,3,4,0,7,2,1,8`. Its written
  zero occupies the ten-thousands column; it is not omitted or described as
  an empty cell. The column assignments reconstruct the complete integers.
- All fifteen requested digit positions were checked from the complete
  integers, not accepted solely from answer prose:
  `63,407,218`: `7→10^3`, `0→10^4`, `1→10^1`, `6→10^7`, `3→10^6`;
  `27,493,615`: `2→10^7`, `1→10^1`, `4→10^5`, `7→10^6`, `5→10^0`;
  `519,711,641,328`: `9→10^9`, `4→10^4`, `2→10^1`, `6→10^5`, `7→10^8`.
- The largest fixed reading follows the groups `519 | 711 | 641 | 328`
  at billion, million, thousand, and one scales. All comma-grouped values
  stay exact in source/target MathML and are read as whole integers, not
  decimals, individual digits, or lists of operands.
- Seven MathML periods and the semicolon after `63,407,218` remain
  sentence/clause punctuation. `basis-10` is read as a base-ten term, not
  subtraction. The literal source prose `dan seterusnya` becomes exactly one
  `lan sateruse` in each Javanese track; the source section has no ellipsis
  glyph, and no glyph-expansion rule is substituted for those words.
- The revised `sepuluh ping nilai` / `sepuluh ping nilaine` clause preserves
  ten times the value immediately to the right. Neither the multiplier nor
  the rightward reference is reversed.

### A10 equality and inequality

- The equality definition preserves `a=b`. The five-row relation table
  retains `a≠b`, `a<b`, `a≤b`, `a>b`, and `a≥b`, with the two column
  roles audible. The plain-text `<` and `>` rows are read even though they
  are not MathML.
- The two number-line descriptions retain a-left-of-b / `a<b` and
  b-left-of-a / `a>b`. The source JPEGs are embedded byte-for-byte; the
  localized alt and narration descriptions agree with the source point order.
- Reversal prose keeps both operands and the relation reversed:
  `a<b` corresponds to `b>a`, `7<11` to `11>7`, `a>b` to `b<a`, and
  `17>4` to `4<17`. Equivalence wording is not converted into a new
  written equality or an evaluated equation.
- The worked expressions stay `17≤26`, `8≠17−3`, `12>27÷3`, `y+7<19`;
  first practice stays `14≤27`, `19−2≠8`, `12>4÷2`, `x−7<1`;
  second practice stays `19≥15`, `7=12−5`, `15÷3<8`, `y+3>6`.
  Operand order and the associated source answers match throughout.
- The two source MathML layout trees retain their `mtable`/`mtr`/`mtd`
  structure, empty rows, `columnalign="left"`, and `mspace` attributes.
  Indonesian source fixtures match before translated linguistic `mtext`
  is compared through the explicit translation mapping. Native-language
  text inside MathML is not mistaken for an operand.
- Letter names and part labels are explicit. No raw comparison/operator
  glyph or circled a–d marker remains unspoken in the narration bodies.
  Equality-glyph naming no longer repeats `tandha tandha`. Formula-plus-prose
  repetitions in the worked solution are retained because both occur in the
  source; they are not accidental readout duplication.

## Cross-artifact checks

- Independently reconstructed the selected source trees and exact explicit
  phrase mappings in memory, without importing the production translator.
  All six compiled CNXML tracks matched, including IDs, hierarchy,
  attributes, numeric tokens, media references, and translated `mtext`.
- All 63 source MathML expressions across the two excerpts matched their
  declared top-level anchor and one-based ordinal, exact raw source
  substring, and namespace-aware tree. No missing, duplicate, or unused
  fixture was found; every fixture has all three expected-reading tracks.
- Both HTML readers preserve every source ID exactly once per track, all
  MathML trees, and both media alts. All twelve embedded image instances
  match the registered per-track files. Internal fragments and relative
  reader/audio links resolve.
- A00's Indonesian SVG outputs equal the pinned source bytes. Its Javanese
  SVGs preserve element structure, geometry/style attributes, and numeric
  text while changing registered linguistic labels. A10's JPEG outputs
  equal the two selected canonical archive members. These are structural
  and byte checks, not a rendered visual or clipping assessment.
- For all six tracks, every Markdown narration block equals the parsed
  SSML paragraph text and uses the same ordered source marks. SSML locales
  are `jv-Latn-ID` or `id-ID` as labeled. Each unit has exactly two spoken
  cues for untitled practice answers; explicit solution titles are read once.
- The post-revision chart/diagram expected readings occur in the correct
  blocks. Javanese large-number readings now contain `éwu`, with no stale
  unaccented `ewu` or `ewonan` in the new A00 transcripts.

## Actual canon consultation

The review read actual local readable KBJI entries, not just the registry:
`wilangan`, `kiwa`, `tengen`, `luwih`, `gedhé`, `cilik`, `saka`, `rolas`,
`likur`, `atus`, `enggon`, `ping`, `para`, and the new `ewu`, `yuta`,
`wolu`, `sanga`, and `sewidak` entries. The locked shelf contains 28 records
at this final checkpoint.

- C24 explicitly supplies `éwu` and `éwuan`. The revised target spelling
  follows that evidence; the ordinary thousands sense supports these uses,
  not every complete pedagogical phrase.
- C25 distinguishes numerical `yuta` from an archaic homograph. C26 directly
  supports `wolu`. C27 supports `sanga` and `sangang puluh` / `sangang atus`.
  C28 supports `sewidak` for sixty. Their evidence reduces the earlier
  component-level uncertainty, not the need to review full large-number
  constructions and pronunciation.
- C17 supplies `rolas`; C18 supplies specific twenties-family forms but does
  not directly attest every `-likur` form here. C19 supports `atusan`,
  `satus`, and `rong atus`. C20 gives ordinary place/location senses;
  `nilai panggonan` remains a provisional mathematical compound.
- C09–C13 support the left/right and larger/smaller components, not a
  standardized complete inequality terminology. C21/C22 support the
  multiplication/division choices; the exact composed formula prosody
  remains unreviewed. `milyar`/`trilyun` remain declared loans.

## Source identities

Hashes below refer to exact pinned module bytes, not Windows checkout
line-ending normalization. A00 was read with `git show` at the pinned
Indonesian and English commits; A10 was read from its exact release and
canonical source witnesses.

| Unit | Indonesian source SHA-256 | English source SHA-256 |
| --- | --- | --- |
| `a00-digit-place` | `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251` | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |
| `a10-equality-symbols` | `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635` | `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed` |

## Final post-revision artifact snapshot

| Input | SHA-256 |
| --- | --- |
| `translation/a00-digit-place.edits.json` | `513133f004e7e9a54ce2b63324d5348f4e9474892b59522c9b3155d50f7c3188` |
| `audio/a00-digit-place.rules.json` | `f3e5d755b53d0ee0de57aa8d71b974f4a8bc50967db0c7c9eb5601c3a6079bbf` |
| `translation/a00-digit-place.assets.json` | `c977cfea69046afacb3da1ef62996f45d2cef80808f1d6f005556f1e9285dcfe` |
| `translation/a10-equality-symbols.edits.json` | `a22b31c73effba2eab6d980d67afc205a7e8649bed3352658ffa502b63957d7c` |
| `audio/a10-equality-symbols.rules.json` | `31777eadd034a130dd62920c8a99c0b466ae0e7da8ab46b5bad9b3dc5e14778b` |
| `translation/a10-equality-symbols.assets.json` | `5953073d3d8c4d77d7e9b2e16321c6447403fe81abd6aa35fbb86dd346923e14` |

| Generated artifact | SHA-256 |
| --- | --- |
| `review/units/a00-digit-place.html` | `a42d5b5196b2032cb93a25ab3104c9521a9e23c956c4819c5b9e807459fef1b8` |
| `review/audio/a00-digit-place.jv-academic.md` | `5d4cb25c26124881d4780db8df158c8c52673e93264e5d3a3ef41fcec0021627` |
| `review/audio/a00-digit-place.jv-academic.ssml` | `c84b3b23bbf74c859cfcbe1bcff0bff571201f4b5297b71022d22447fb81275d` |
| `review/audio/a00-digit-place.jv-conversation.md` | `0b8d3533adfbfccb7476c0e5dcd1afdcf086bbef3ef9010777d9b9bdb48f7135` |
| `review/audio/a00-digit-place.jv-conversation.ssml` | `40d67aa348e0f53ed119fec0063da81a2997978d458a104b91fdc2e42795e248` |
| `review/audio/a00-digit-place.id-academic.md` | `68c7720a1511edb439eb36fb10d1497a48bcbd41c9f61903c9738fc757a4f0c0` |
| `review/audio/a00-digit-place.id-academic.ssml` | `25f06fc3be8a2b83e1f1c2c40afd44e40b4515d0390a7bd8a2d337d36a427ac8` |
| `review/units/a10-equality-symbols.html` | `e681b61e58cf20803b7d7d9ed83c38b6a623de4f2bcd3e984d992a803495b027` |
| `review/audio/a10-equality-symbols.jv-academic.md` | `cef76e102e511ad68697d90d85059691333bfaf8601767e40301aded9d7d7ae7` |
| `review/audio/a10-equality-symbols.jv-academic.ssml` | `b6e0658a59b345106e74235e04b310172caab4e25fe55e8fcb33b99e433a2015` |
| `review/audio/a10-equality-symbols.jv-conversation.md` | `ca3473748805f0a96b2b48e7b4b3be10c2601aaec05e86c935909589fbd7667c` |
| `review/audio/a10-equality-symbols.jv-conversation.ssml` | `e2869713311c6a7c7fa0e26b1b6647d174b84eae5317345cec5f4443aae437eb` |
| `review/audio/a10-equality-symbols.id-academic.md` | `f525f5999c79b90cd505032a6768c609bffaabc5f50f33f76a4969b4d3780a80` |
| `review/audio/a10-equality-symbols.id-academic.ssml` | `22c8baf26c417259f92d24b875b7b8a54e4d677ff98804a6b93dc43a45552de7` |

## Limits and remaining work

This is a source-fidelity and written-readout checkpoint, not native-Javanese
certification, formal mathematical-register standardization, rendered visual
approval, screen-reader testing, listening review, voice compatibility, or
release sign-off. No audio was synthesized. Provider pronunciation, pauses,
and prosody still need actual review; text/SSML agreement does not establish
how a voice will sound. No license/supply audit was repeated.

The entire A00/A10/AX-2 assignment remains active and unfinished. Continue
from the exact next source boundaries above while keeping both Javanese
registers, Indonesian source fidelity, narration, assets, and review together.

## Producer whitespace-only follow-up

After this review snapshot, the staged diff check found trailing spaces on two
digit-place answer-list narration lines per track. The builder now strips only
line-final whitespace from spoken blocks; words, line breaks, source marks,
mathematics, and reader bytes are unchanged. Transcript/SSML and receipt hashes
therefore change; use the current build receipts for their current hashes.
The reviewed hashes above remain the historical snapshot, not a new review
claim. The complete regression suites and coverage check were rerun afterward.
