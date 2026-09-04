# AX-2 formula, diagram, and voice handoff

Source contract: catalog `AX-2` (enhanced nonvisual access), derivative
`AX-AUDIO`; exact source rows and dossier hashes are retained in provenance.
The following operational conventions are this pilot's explicit implementation.

## Separate tracks, no hidden fallback

Each unit has independent `jv-conversation`, `jv-academic`, and `id-academic`
transcripts and SSML. The SSML root language is `jv-Latn-ID` or `id-ID`; each
file begins with its spoken register label. A provider must explicitly support
the requested locale, or return `unsupported_voice_locale`. It must not silently
speak Javanese text using an Indonesian voice or present Indonesian as Javanese.
No provider voice is selected, no external TTS call is made, and no audio quality
approval is claimed. Human recording is an equally valid next step.

## Reading rules

- Keep source mathematics visible as MathML. Narration is a separate derivative.
- Counting list: say each cardinal in order, with a pause at commas, and say
  `lan sateruse` / `dan seterusnya` for the ellipsis. When discussing the glyph
  itself, say `tandha telung titik` / `tanda tiga titik`. Do not double-read the
  source's ellipsis plus its adjacent “and so on” prose.
- A fraction has explicit boundaries: `pecahan: siji per papat, pungkasan pecahan`
  / `pecahan: satu per empat, akhir pecahan`. Numerator precedes denominator.
- Decimal 5.2 remains 5.2 in MathML; say `lima koma loro` / `lima koma dua`.
  Read each fractional digit; do not reinterpret the dot as a thousands separator.
- `g + 3`: `aksara ge ditambah telu` / `huruf ge ditambah tiga`.
  Written `g` must never become a numeric placeholder or a translated identifier.
- Tables: read each row using the column header with its value. The age pairs
  must remain 12→15, 20→23, 35→38, and g→g+3. Preserve Alex's greater age.
- Number line: name the range 0–6, equal one-unit spacing, increasing direction
  to the right, decreasing direction to the left, and origin zero. The script
  includes both figure description and surrounding explanatory paragraph; it
  does not require the listener to infer spatial structure from a silent image.
- Source exercise markers ⓐ/ⓑ are spoken as labeled parts, not mathematical
  variables. Every included source solution is in the transcript.
- Untitled practice solutions begin with `Wangsulan.` / `Jawaban.` so that
  answers do not run into the question. Existing worked-solution titles remain
  unchanged and receive no duplicate cue. This is a narration-only addition.
- The current narration grammar accepts only the eight MathML tags present in
  the pilot and the operators `+`, comma, period, and ellipsis. Unsupported
  structures/operators, malformed fractions, negative-number tokens, and
  cardinals outside the reviewed 0–999 range stop the build. Extend the explicit
  rules and fixtures before translating later material; do not flatten powers,
  subscripts, or radicals into misleading speech.

## Handoff QA

The XML parser checks well-formed SSML, root locale, nonempty paragraphs, and
unique source-linked marks. Marks identify the original top-level source block.
The offline QA checks selected cardinal/fraction/variable fixtures. These checks
do not certify a voice engine's SSML implementation, prosody, phonology, or
intelligibility. In particular, review `e/é/è`, cardinal irregularities, loan
terms, and consistent social register with a Javanese speaker before recording.

Narration-stage canon: C03–C08 for small cardinals, C09–C13 for spatial direction,
C14–C15 for variable/constant wording; C17–C18 were added when the age table
required irregular twelve and the twenties. Their readable entries must be
consulted, not merely listed. Non-attested compound narration remains a draft.

## Place-value and operation-symbol extensions

- Dollar amounts in the A00 banknote example are spoken as a cardinal followed
  by `dolar Amerika Serikat`; a bare `$` must never disappear. Multiplication,
  addition, and equality in that example are overtly read.
- A00 tables skip genuinely empty cells, name each nonempty cell with its column
  header, and read the total row. The build recomputes 138 and 215 from their
  hundreds/tens/ones rows and checks 176, 237, and 374 independently.
- A00 figure references are source-ID-specific: money, base-ten forms, and the
  138 model cannot silently receive the earlier number-line description.
- A source-inherited period embedded between the final digit 5 and `berbeda` is
  preserved visually. Only that exact source anchor suppresses the misleading
  spoken sentence break.
- A10 operation notation is not passed through a generic algebra reader. Eleven
  fixtures bind module, top-level anchor, one-based ordinal, exact MathML tree,
  attributes, operands, and all three readings. Unknown trees stop the build.
- Long division keeps `b` outside and `a` inside, spoken as `a` divided by `b`.
  Five multiplication and four division forms remain distinct. The cross glyph,
  variable `x`, and literal adjacent `3xy` are not conflated.
- The operation-result heading ellipsis is a pause/lead-in, never the counting
  phrase `lan sateruse`. Source final periods and alternative-separating commas
  are pauses, not decimal or multiplication operators.

Canon C19–C23 was reread during these extensions. Lexical support does not by
itself certify formula prosody. All new scripts remain provider-neutral and
unsynthesized; Javanese listening/pronunciation review is pending.

## Digit-place and equality/inequality extensions

The digit-place unit binds 40 exact MathML trees to three-track readings,
including complete grouped integers through 519,711,641,328. No general large-
integer parser is enabled. Validation separately recomputes all fifteen
digit-position answers and four integer decompositions. Chart scripts state all
fifteen columns, preserve filled digit order, and distinguish blank leading cells
from the written zero. C24–C28 support the revised `éwu/éwuan` spelling and other
numeral components; complete large-number prosody remains provisional.

The equality slice binds 23 source MathML trees, including two explanatory
`mtable` layouts. Original Indonesian trees must match fixtures exactly; target
trees may differ only in registered linguistic `mtext`, after exact source-bound
draft replay. This does not authorize generic matrix narration. Plain comparison
glyphs, reversed operands, table letter names, point-order diagrams, and a–e
part labels receive explicit readings. Doubled glyph-name introductions are
removed only in their registered context. The source spacing node
`fs-id1171789687379` stays in CNXML/HTML but intentionally has no empty SSML
paragraph; its nonspoken status is declared and checked in the receipt.

## Naming whole numbers and grouping symbols

The naming unit has nine exact MathML fixtures. Eight grouped-numeral occurrences
are read as printed digits from left to right, with explicit comma separators;
the year 2014 is still read as a cardinal. Reading prompt numerals as their full
names would give away the exercise answers. Full names remain as separate
verification witnesses and in actual explanation/answer prose. Leading groups
098/061/004/000 stay intact; no decimal interpretation is permitted.

Three charts explicitly read printed digit groups and their actual arrow-linked
word labels (the third chart has no arrows). One source-bound headerless table
reads five two-entry rows once, despite its inherited three-column declaration;
no invented header or duplicate aria-label speech is added. A full-paragraph
fixture marks `lan`/`dan` as the quoted word being discussed. Four untitled
practice solutions have explicit answer cues. C07 supports sèket/salawé, while
C24–C28 support other numeral components; full prosody remains provisional.

Grouping uses two exact whole-tree fixtures for the three delimiter families
and all three nested expressions. Every opening/closing type and all five
source-implied multiplications are spoken, without evaluating the expressions.
C29–C30 support kurung/bukak/tutup components. The exact trailing layout node
fs-id1166424830424 remains visual/source content but has no empty SSML speech.
No general expression parser, voice fallback, or synthesis is authorized here.

## Expressions, equations and source text integrity

The complete [28:40] lesson uses 21 source-bound MathML fixtures and three exact
source/target table fixtures. A stacked fraction retains numerator/denominator
order and an audible end. The one power reads y cubed, ends the power, then
divides by fourteen. Nine implied multiplication sites receive spoken products
without inserting visible operators. No expression is evaluated or equation
solved. The eight classification labels remain in their source solutions;
each of two untitled practice solutions has one Wangsulan/Jawaban cue.

The two definition tables read their actual column headings and every row.
The worked-answer table reads its four pairs without invented headers. Each
fixed table is read once; its aria-label/summary is not repeated as a second
table narration. Source summary now translates and survives CNXML, with its
exact translated text used as an accessible reader label where needed.

Source-bound MathML dispatch compares exact registered target text, not merely
a shape with all mtext removed. Nonlinguistic currency mtext keeps its symbol
and digits; unknown replacements fail. This safeguard prepares the inverse
writing-numbers lesson but does not itself integrate that unit or synthesize
audio. C34 rambang is recorded as a mathematical alternative; the current
pangkat loan and all complete formula prosody remain provisional.

## Whole-number writing: representation and unit context

The full fs-id1339359 workflow reverses the preceding naming lesson. Word-form
prompts remain cardinal phrases; digit-form answers speak literal digits and
grouping commas, retaining 073/051/022/000. A finite verifier checks the seven
source values without authorizing a general runtime large-integer parser.
Empty chart word blocks are distinct from digit groups containing three zeroes.

Budget coefficient $77 cannot be spoken on its own: its full paragraph supplies
billion and the declared US-dollar context. The 204-million weight paragraph
and answer explicitly use the English-source pound loan in all audio tracks;
visible Indonesian pon remains unchanged. Neither unit is converted. The six
prose fixtures and three charts must match complete source/target trees before
being read once. Detached context-only formulas fail closed. The exact inline
part-b reference fs-id2880619 has no duplicated part label or list-item colon.
Four practice cues and two existing worked-solution headings separate questions
from literal answers. All pronunciations and listening outcomes remain unreviewed.

## Full exponent remainder [40:53]

All 32 exact source MathML expressions have finite registered readings. Seven
occurrences require their full definition/naming prose and reject detached,
empty or plain-dictionary mappings. Six whole-prose overrides run before their
children, spelling literal a/n and preserving the positive-integer condition.
No general power/caret/ellipsis parser or expression evaluation is authorized.

Both complete tables read once, preserving real headers, the first blank cell
of the worked table, all steps and plain-text 81. The real table link receives
one descriptive reference. Four practice results remain after two answer cues.
The two diagrams read every shown factor; three a glyphs before an ellipsis
plus one after do not assert n=4 or infinity. Indonesian retains the original
English-labelled JPEGs with honest spoken explanation; Javanese uses localized
SVGs with per-output MIME. No synthesized audio or listening approval is implied.
