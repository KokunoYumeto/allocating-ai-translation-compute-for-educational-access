# A00 digit-place translation draft witness

Status: **source-keyed translation draft only**. This does not complete A00,
A10, AX-2, module `m81243`, narration, figures, or review. The section has not
been integrated into an offline reader. Native-language, visual, screen-reader,
pronunciation, and listening review remain pending.

## Source boundary read in full

- Program/module/section: A00 / `m81243` / `fs-id1883656`.
- Boundary: the entire “Mengidentifikasi Nilai Tempat Sebuah Digit” section,
  from its title through practice solution `fs-id2619544`; next section is not
  included.
- Read both actual Indonesian and English section trees, including every alt,
  exercise, answer, MathML expression, and figure reference. Inputs are the
  pinned Git blobs, not a summary or translated draft.
- Indonesian module: commit
  `3de9207f56f8b5c57c017abf973fb04e00d740f1`, Git blob
  `90def09ee1dbfdc66aa8bc910938ad7684668e97`, SHA-256
  `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251`.
- English module: commit
  `38cae454e644abf9f0a623e876994553881597c9`, Git blob
  `612244f80ecb6bce0f811c9d99204ae2f9f7a4f5`, SHA-256
  `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b`.
  A Windows checkout reads with normalized line endings; the recorded hash is
  the exact pinned Git blob basis used by the project source lock.
- Namespace-aware canonical section witnesses (whitespace stripped, prefixes
  rewritten): Indonesian SHA-256
  `8f47c9ff107409c34df0be8da83b2f509c08b8efe58f48b8899e7e6fe6fdac5f`;
  English SHA-256
  `422015a0646c5697ee25d56a9be5a96c325fcdf2b664edd98409914c5d9359f5`.

Direct-child order after the title:

1. `fs-id1795155`
2. `fs-id2825467`
3. `fs-id1408851`
4. `CNX_BMath_Figure_01_01_011`
5. `fs-id930962`
6. `fs-id1891091`
7. `fs-id2310429`
8. `fs-id1282619`

The section contains 31 unique source IDs and 40 MathML expressions. The full
ordered ID ledger is:

`fs-id1883656`, `fs-id1795155`, `term-00009`, `fs-id2825467`,
`fs-id1408851`, `CNX_BMath_Figure_01_01_011`, `fs-id1339846`,
`fs-id930962`, `fs-id1891091`, `fs-id1256900`, `fs-id1581177`,
`fs-id1738612`, `fs-id2218367`, `fs-id2851093`, `fs-id2281077`,
`fs-id2297687`, `eip-id1168898159450`, `fs-id2310429`,
`fs-id1573052`, `fs-id1607674`, `fs-id1816164`, `fs-id1386307`,
`fs-id2903653`, `fs-id1811287`, `fs-id1282619`, `fs-id1518735`,
`fs-id3013699`, `fs-id1778628`, `fs-id1508784`, `fs-id2619544`,
`fs-id1807276`.

## Exact draft and structural check

- Draft ledger: `translation/a00-digit-place.edits.json`, SHA-256
  `81b861d380faabfabdf7c700b5694f93988f2a2bbfb93707d4761bd37fc022d0`
  at this checkpoint.
- 40 unique Indonesian linguistic strings were extracted from element text,
  tails, `alt`, and `aria-label` fields. All 40 have explicit academic and
  conversational Javanese entries; even identical technical loans are recorded
  rather than allowed through an implicit fallback.
- Applied the project translation function in memory to both tracks, combined
  with the shared pilot phrase ledger. Both tracks passed the existing
  `draft_units.validate` source-identity, unique-ID, internal-reference,
  MathML-attribute/token, and numeric-fact checks: 31 IDs and 40 MathML
  expressions per track. No generated CNXML or reader was written here.
- MathML facts retained include `basis-10`; the chart number `5,278,194` and
  the seven values `5,000,000`, `200,000`, `70,000`, `8,000`, `100`, `90`,
  and `4`; worked number `63,407,218`; and practice numbers `27,493,615` and
  `519,711,641,328`. The source sentence-final periods and semicolon remain
  MathML operator tokens and must not be mistaken for decimal or arithmetic
  operators in narration.

Checked source answer facts:

- `63,407,218`: 7→thousands, 0→ten-thousands, 1→tens,
  6→ten-millions, 3→millions.
- `27,493,615`: 2→ten-millions, 1→tens, 4→hundred-thousands,
  7→millions, 5→ones.
- `519,711,641,328`: 9→billions, 4→ten-thousands, 2→tens,
  6→hundred-thousands, 7→hundred-millions.

The translations preserve these positions. They use `puluhan yuta`,
  `yutanan`, `milyaran`, `atusan ewu`, `puluhan ewu`, `ewonan`, `atusan`,
`puluhan`, and `satuan` as explicitly provisional draft labels.

## Canon consultations at drafting and review

Read the actual local readable entries, not search snippets:

- C01 `wilangan.txt`: `wilangan` includes count/number senses. Kept it for
  source numbers; this says nothing about the new place-name compounds.
- C16 `saka.txt`: retained `saka tengen` for starting from the right; the range
  example supports `saka`, not a mathematical place-value standard.
- C19 `atus.txt`: directly contains `atusan ratusan`, `satus seratus (100)`,
  and `rong atus dua ratus (200)`. This supports `atusan`/`satus`; it does not
  by itself attest all productive combinations with ewon/yuta/milyar/trilyun.
- C20 `enggon.txt`: directly gives `enggon` as place/location and `panggonan`
  as a place to live. It supports the ordinary place sense used as a bridge,
  but **does not attest** `nilai panggonan` as standardized mathematics.
- C10 `tengen.txt`: distinguishes `tengen` (right) from `tengèn` (easy to
  awaken). The solution uses unaccented `tengen`.

At review, reread C19 and C20 against every `atusan` and `panggonan` draft
occurrence. Kept `nilai panggonan` openly provisional. No current shelf entry
was treated as authority for `digit`, `periode`, `ewonan`, `yutanan`,
`milyaran`, or `trilyunan`. The latter labels need targeted lexicographic and
native-educator review; their spelling and register must not be silently
promoted from draft status.

## Media handoff required

This section adds two source-bound SVGs; they are not covered by the preceding
place-value asset manifest:

1. `CNX_BMath_Figure_01_01_011` / media `fs-id1339846` /
   `../../media/CNX_BMath_Figure_01_01_011.jpg.id-ID.svg`.
   Indonesian Git blob `c7fd63689cb359befc7169687a4c205d116f6c86`,
   SHA-256 `139263ebfe895df0abcaf00fa63c949b38e5edc352239ed70ec42837625fee13`.
   Canonical English JPEG Git blob
   `6c112f73c84b2b70e17b537d87086bba8f729e82`.
2. media `fs-id2297687` /
   `../../media/CNX_BMath_Figure_01_01_012_img.jpg.id-ID.svg` inside the worked
   solution. Indonesian Git blob
   `023b6451c55ca24039a23c9fb26e4a8ba1fd5a76`, SHA-256
   `7ae0f6c74b0584cb2e3698964b08be046d2678e9475b32193283c3c906fe8a57`.
   Canonical English JPEG Git blob
   `b0367727073e7bb77665d0b2f88d304fd6af867c`.

Both original JPEGs and all Indonesian SVG text nodes were inspected. Geometry
fidelity for future localization must be compared against each inherited
Indonesian SVG; canonical English JPEG identity remains separate. The SVGs have
linguistic title, description, period, and place labels. They therefore need
explicit `id-ID`, `jv-academic`, and `jv-conversation` asset mappings. Do not
fall back to untranslated Indonesian labels or claim numeric-only reuse.

## Fail-closed integration issues

- The current A00 cardinal helper is intentionally bounded below 1,000 and does
  not accept comma-grouped tokens. This section contains values through
  `519,711,641,328`. Integration requires new source-bound large-number
  narration fixtures/rules and adversarial tests; removing commas or guessing a
  general parser is not authorized.
- Register the section's MathML `;` and sentence-final `.` as source-context
  punctuation pauses, not arithmetic or decimal readings.
- The source paragraph contains literal continuation words (`dan seterusnya`),
  translated as `lan sateruse`; it has no U+2026 ellipsis glyph. Keep those
  words distinct from both the pilot sequence glyph and A10's result-heading
  glyph.
- Narrate each chart by rows/groups with explicit empty-cell handling. Preserve
  all 15 columns, example digit order, figure IDs, alt facts, and the stated
  4-row/2-row descriptions. A rendered visual and clipping review is still
  required after SVG localization.
- Verify each digit-place answer computationally from the complete integer,
  not by trusting translated prose. Require exact comma-grouping, 31 source IDs,
  40 MathML expressions, two embedded media references per track, explicit
  answer cues for both untitled practice solutions, deterministic rebuilds,
  and locale-marked SSML. No provider voice fallback is authorized.

The next source boundary after completing this section remains a root workflow
decision; this draft neither advances a coverage ledger nor claims integration.

## Superseding integration checkpoint — 2026-08-31

The draft-only state and edit hash above describe the original snapshot, not
the current build. The entire subsection now has three verified CNXML tracks,
six source/target SVGs, an offline reader, and three transcript/SSML pairs.
Current draft/build receipts bind their hashes. Eighteen workflow regressions
pass without skips, including all fifteen recomputed digit-position answers,
exact large-number fixtures, chart geometry/digit order, blanks versus zero,
punctuation context, deterministic output, and explicit answer cues.

After reading new canon C24–C28, revised `ewu/ewonan` to `éwu/éwuan` consistently
in both Javanese text/audio and chart labels; Indonesian source bytes remain
unchanged. `yuta`, `wolu`, `sanga`, and `sewidak` now have direct lexical support,
while long numeral composition and place compounds remain provisional. Revised
the ten-times explanation to `sepuluh ping nilai/nilaine`, making the compared
value explicit. The source continuation remains literal `dan seterusnya` /
`lan sateruse`, not an ellipsis glyph. Next section is `fs-id1321580`.

Independent structural/text review is in `THIRD_CHECKPOINT_REVIEW.md`. Native,
visual, screen-reader, pronunciation, and listening review remain pending;
there is no synthesized audio or full-module completion claim.
