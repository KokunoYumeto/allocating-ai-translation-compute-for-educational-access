# A10 operation-symbols continuation — translation draft

Date: 2026-08-30. This is a reviewable continuation of the full A00/A10/AX-2
assignment, not its completion. AI-assisted Javanese educator/native-speaker
review is pending. No audio synthesis, listening review, or build is claimed.

## Exact source and boundary

Read the actual Indonesian and English module files from the already acquired
A10 v1.0.2 source package. Both physical files were byte-compared with the
corresponding members of `downloads/jv-Latn-ID/a10-source.zip`; no extraction,
download, or source rewrite was performed.

- Indonesian: `translated/modules/m82453/index.cnxml`, 186,219 bytes,
  SHA256 `2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635`.
- English: `authority/source/modules/m82453/index.cnxml`, 184,248 bytes,
  SHA256 `a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed`.
- Release source URL:
  https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/elementary-algebra-2e-id-ID-1.0.2-source.zip
- Indonesian release repository pin: `11754719d8eab8de63d5340ad35824e8be8d99e4`.
- Existing canonical upstream pin: `38cae454e644abf9f0a623e876994553881597c9`.

Parent section is `m82453/fs-id1170655150800`. Include its direct children
`[7:13]` using zero-based indexing with the existing section title counted as
child 0. These six consecutive children are:

1. `para fs-id1170655224522` — need for operation symbols.
2. `para fs-id1170654981807` — four arithmetic operations; contains
   `term-00005`, `term-00006`, `term-00007`, `term-00008`, `term-00009`.
3. `table fs-id1170655178881` — all four operation rows and all notation forms.
4. `para fs-id1170655126801` — symbolic/Indonesian language bridge.
5. `list fs-id1166424846753` — both difference/product examples.
6. `para fs-id1170655004454` — multiplication cross versus variable x warning.

Stop immediately after child 12. The exact next child is spacing-only
`para fs-id1171789687379` containing `newline`; next instructional anchor is
`para fs-id1170655208137`, the equality introduction. Do not silently mark the
spacing child or equality material as covered. The draft includes no exercise,
solution, added title, or new section ID. No source link is present in this span.

The complete included ID set is the six child IDs above plus `term-00005` through
`term-00009` (11 IDs). Preserve all source math, attributes, and hierarchy when
assembling CNXML; the JSON changes only source text/tails and the table's
`aria-label`. `a`, `b`, `x`, `y`, and the adjacent-variable token `xy` remain
unchanged identifiers.

## Canon consulted at drafting

Reread the existing readable KBJI entries, not merely their manifest records:

- C01 `downloads/jv-Latn-ID/canon/wilangan.txt`: `wilangan` for a number;
  retained consistently in introductory and dividend wording.
- C02 `downloads/jv-Latn-ID/canon/cacah.txt`: count/sum sense and `nacahaké`;
  this does not by itself attest every formal operation noun below.
- C04 `downloads/jv-Latn-ID/canon/loro.txt`: two; retain `rong wilangan` as a
  provisional attributive construction, not a quotation from that entry.
- C05 `downloads/jv-Latn-ID/canon/telu.txt`: three; preserve the spoken
  `telu` versus written mathematical `3` distinction.
- C06 `downloads/jv-Latn-ID/canon/papat.txt`: four; preserve four operations
  and four table columns.
- C07 `downloads/jv-Latn-ID/canon/lima.txt`: five; preserve five total table
  rows and five multiplication notation forms.
- C16 `downloads/jv-Latn-ID/canon/saka.txt`: source/from usage supports the
  explicitly labeled Indonesian `dari` → Javanese `saka` gloss.

Search of the currently acquired readable shelf did not yield dedicated
operation entries for `ping`/`para`/`gunggung`. No dictionary attestation is
claimed for those operation choices. Targeted further reference acquisition
and educator review are next linguistic work, not grounds to stop drafting.

## Material translation decisions

- Both tracks use an overt shared mathematical vocabulary. Academic prose uses
  `dibutuhake`, `ditindakake`, `kacathet`, `ateges`, and `kanthi tembung liya`;
  the conversational track uses `butuh`, `dienggo`, `kokweruhi`, `tegese`, and
  shorter sentences. This is ngoko/provisional academic Javanese, not krama.
- Provisional operation nouns: `panambahan`, `pangurangan`, `ping-pingan`, and
  `para-paran`. Keep them identical between the table headers, cells, and the
  accessible table description. They require dedicated mathematical-register
  confirmation; do not characterize them as canon-attested standards.
- Provisional readings: `a ditambah b`, `a dikurangi b`, `a ping b`, and
  `a dipara b`. These are read-aloud text choices only; written operators remain
  `+`, `−`, `·`, `÷`, slash, fraction, or juxtaposition exactly as sourced.
- `gunggung` is the proposed sum/result noun; `asil ping-pingan` and
  `asil para-paran` distinguish result names from operation names. `selisih`
  and `pembagi` are declared Indonesian mathematical loans, not concealed
  dictionary attestations. `operasi`, `aritmetika`, `simbol`, `notasi`,
  `ekspresi`, `variabel`, and `aljabar` are likewise retained/assimilated scaffold
  loans. Review whether the result-name compounds are idiomatic locally.
- The Indonesian pivot explicitly teaches translation into/from Indonesian.
  Preserve that setting: the Javanese prose names `basa Indonesia` and labels
  the Indonesian words `dari` and `dan`, then adds visibly labeled Javanese
  glosses `saka` and `lan`. This is a declared pedagogical addition, not an
  invisible register switch or a claim that the original discussed Javanese.
- Preserve the noncommutative subtraction order: the example is 9 minus 2,
  never 2 minus 9. Both tracks use `njupuk 2 saka 9` followed by
  `9 dikurangi 2`, preserving the source order of all written numerals while
  expressing removal of 2 from 9. The product remains 4 times 8, with all
  repeated written numerals retained. The removal verb is a pedagogical
  paraphrase rather than a dictionary-attested operation label.
- The Indonesian table description correctly lists five multiplication forms
  `a·b`, `ab`, `(a)(b)`, `(a)b`, `a(b)`. The English accessible description
  incorrectly says four and misdescribes the last form; the English MathML
  agrees with the Indonesian table. Follow the corrected Indonesian description
  and preserved MathML rather than reintroducing that English description bug.
- Added `data` to the table-description phrase `larik data kapisan` to
  distinguish the addition row from the header row. The source has five rows
  total, not five data rows. No counts or row order change.
- Preserve `3xy` and the distinct alternatives `3 × y` versus `3 · x · y`.
  The cross-symbol warning is inherited source wording; do not change it into
  the broader claim that the variable x itself is prohibited in algebra.
- The chosen boundary includes the table's explanation and multiplication
  warning, so the arithmetic-symbol unit is contiguous and coherent. Equality
  and inequality are subsequent work, not silently omitted completed material.

## Integration requirements and draft QA

This is an edits draft only. Do not count it as built CNXML/HTML/SSML yet.
Required integration work before a passing production receipt:

- Preserve all 11 source IDs and all formula trees/attributes.
- Explicitly support the new math forms: subtraction U+2212, multiplication
  dot U+00B7, division sign U+00F7, parentheses, cross U+00D7, slash stored as
  `mtext`, adjacent identifiers, and `menclose notation="longdiv"`.
- Long-division display is `b` outside and `a` inside: it means a divided by b,
  not b divided by a. Do not let tree-order speech reverse dividend/divisor.
- Distinguish written symbols from their operation meaning in the notation
  table. In particular, preserve all five multiplication forms and four
  division forms as separately identifiable alternatives.
- Define spoken `xy` as two variables, not an unknown word. This warning
  contrasts letter x with the multiplication cross; audio must identify both.
- The table heading's ellipsis in `Asile yaiku…` introduces a result, not an
  infinite counting sequence. Do not narrate this prose ellipsis as
  `lan sateruse` using the earlier number-list rule.
- Keep the source pivot untouched. Record any new phrase-mapping conflicts
  explicitly before merging with existing mappings; the fragment's `dan` and
  `, dan` mappings agree with the existing pilot.
- Native linguistic, mathematical-register, and spoken-form approval remain
  pending. No pronunciation/voice/SSML compatibility claim is made here.

Draft-only read-only QA completed after writing: JSON parses; all 43 phrase
rows contain one exact Indonesian key and two nonempty translations; keys are
unique; the rows cover every alphabetic source text/tail and accessible label
in children `[7:13]` except the five declared unchanged identifiers. All written
numeral sequences match the corresponding source strings. Shared phrase keys
have no conflicts with the current `translation/phrases.json`. Confirmed the
11 included IDs and reread the relevant KBJI number/source-syntax entry lines
against the draft. No production builder, lockfile, or generated output was
changed or executed by this drafting task.

## Superseding integration and lexical revision

The paragraph above is retained as drafting history. It is no longer the current
integration state: this exact slice now has source-bound three-track CNXML, an
offline reader, three narration transcripts, three SSML files, and structural
receipts. The files remain review drafts; zero synthesized audio and no native,
visual, screen-reader, or listening approval are claimed.

Topic-driven canon acquisition also supersedes the initial “not attested” note.
After fully reading C21 `ping`, C22 `para`, and C23 `gunggung`, the current draft
uses `ping-pingan`, `Paran`/`asil paran`, `para gapit`, and `gunggung`. These are
lexically supported senses, not proof that every composed mathematical phrase
or spoken formula is standardized. Exact source trees and local narration
fixtures still govern formula readings.
