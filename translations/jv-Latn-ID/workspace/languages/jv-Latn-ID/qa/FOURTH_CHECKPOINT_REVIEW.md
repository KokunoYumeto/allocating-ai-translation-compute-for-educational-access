# Fourth checkpoint: naming whole numbers and grouping symbols

Reviewed 2026-08-31 against actual pinned sources, current phrase drafts,
generated CNXML, both HTML readers, all six transcripts, all six SSML files,
and exact source-bound MathML/media/table/prose fixtures. This task wrote only
this review. It did not rebuild or modify shared scripts, rules, source files,
translation drafts, assets, locks, or coverage.

Result: no current numerical, operand, delimiter, source-bound narration,
answer-leakage, or embedded-asset mismatch was found. **One current HTML list
semantics defect remains**, described below. The requested **25 naming tests
and 19 grouping tests passed, with no skips**. Passing those tests is not full
visual, hierarchy, native-language, provider, or listening approval.

## Current finding

**P2 — the naming how-to's numbered steps become an unordered HTML list.**
The actual source list `eip-375`, inside `fs-id1364640`, declares
`list-type="enumerated"`, `number-style="arabic"`, and `class="stepwise"`.
The three current reader instances are `<ul>` at
`review/units/a00-name-whole.html:46`, `:48`, and `:50`.
`scripts/build.py:192` maps every CNXML `list` to `ul` without considering its
list type. The two instructions and their order survive, as does the original
CNXML, but the HTML loses the numbered-step distinction for visual and semantic
list presentation. This affects the current naming unit; grouping has no
CNXML list in its selected span.

Root separately identified this limitation and confirmed it will be handled
as a shared-renderer follow-up with rebuilding. It is **not fixed in this
hash snapshot**, and the 44 passing tests do not currently detect it.

## Sources and exact scope

Read both actual complete naming sections and the entire selected grouping
slice in ID and EN, including adjacent boundary content. Naming's source
module was read from exact pinned Git bytes; grouping's existing release
source files were read and their hashes checked, without extraction/download.

| Unit | Exact boundary | Source content |
| --- | --- | --- |
| `a00-name-whole` | A00 `m81243`, whole `fs-id1321580`; 12 direct children including title; next `fs-id1339359` | 53 unique IDs, 9 MathML expressions, 3 media, one headerless explanatory table, two how-to steps, two worked solutions, four untitled practice answers |
| `a10-grouping-symbols` | A10 `m82453`, `fs-id1170655150800`, `[23:28]` plus shared context title; next `fs-id1170654957085` | 8 IDs including the shared section wrapper, 7 newly covered IDs, 2 MathML layout tables, no CNXML data tables/media/exercises/solutions |

Pinned module SHA-256 values:

```text
A00 ID 7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251
A00 EN 396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b
A10 ID 2c0b688d569044b128d589579e9ba7d871a0fb9ac7a670ac6f22d0ef2b66e635
A10 EN a8fdd235aa254c5a0a1248fa858e9b3579d9b40982bbc514cbe6a18c3e6fcbed
```

An independent element walk compared all 112 naming nodes and all 95 grouping
nodes in each CNXML track with the selected source: element order/hierarchy,
IDs, every non-language attribute, numeric/operator text, and text/tails
resolved through the exact phrase maps. No hidden source or mathematical
change was found. The grouping draft changes only its three linguistic
MathML `mtext` labels; all other mathematical text and attributes remain exact.

## Naming: readout and answer protection

The eight grouped `mn` occurrences now speak the **printed digit sequence**,
with an explicit `tandha koma` / `tanda koma` at every written comma. They do
not invoke a generic cardinal-number parser. The ungrouped source year `2014`
remains `rong éwu patbelas` / `dua ribu empat belas`, not four isolated digits.
The two sentence-final `mo` periods remain punctuation; neither becomes a
decimal point, a multiplication dot, or the spoken word `titik`.

All nine exact fixture trees independently matched module, top-level anchor,
one-based ordinal, namespace-aware tags/attributes/tokens, including the bold
`mstyle` around the phone-user count. Full names remain in the written
explanations/answers and in `expected_cardinal` verification fields, rather
than leaking into naming prompts.

Checked the actual four practice blocks at `fs-id2774887`, `fs-id2136533`,
`fs-id1628781`, and `fs-id1808812`: each has exactly one `Wangsulan.` /
`Jawaban.` after its question. None speaks its full word-form answer before
that cue. The literal groups `061`, `004`, and `000` are fully audible in
the questions; the final `000` period is omitted only from the complete
31,536,000 cardinal answer, as in the source. Both worked examples use their
existing solution titles once and do not acquire an extra answer cue.

The three chart fixtures are in the correct source blocks and narrate each
diagram once. Group order is 37/519/248, 8/165/432/098/710, and 327/577/529.
The first two diagrams have three and five word-label arrows; the third has
none. The 098 chart group explicitly distinguishes a written leading zero
from an empty place, without changing its 98-thousand cardinal value.

The table reads its five actual two-entry rows once, in order. It does not
duplicate its complete aria-label as an extra narration, invent a header,
or infer an extra meaningful blank column from the inherited `cols="3"`.
The reader contains three ordinary HTML tables, each with five two-cell rows
and no invented header cells.

The source metalinguistic conjunction at `fs-id3400199` remains italic in
CNXML/HTML and is explicitly introduced once as quoted `“lan”` / `“dan”` in
speech. The instruction remains the textbook's scoped number-naming
convention, not a claim that ordinary Javanese universally prohibits `lan`.

Source-specific inherited/editorial distinctions remain visible and declared:
the historical phone example retains 2014 and April; one year remains the
source's 31,536,000 seconds; the English-specific plural-suffix instruction
is already adapted away in the Indonesian pivot; and restored Javanese
inter-period answer commas are documented target-only edits. No modernized
statistics, invented qualifications, or silent source answer repairs appeared.

## Grouping: full nested expressions

The three displayed expressions remain exactly:

```text
8(14−8)
21−3[2+4(9−8)]
24÷{13−2[1(6−5)+4]}
```

Each of the three tracks names parentheses, square brackets, and braces with
the correct opening/closing sequence. The three delimiter sequences are
`()`, `[()]`, and `{[()]}`. There are exactly five implied products, at the
source sites 8(…), 3[…], 4(…), 2[…], and 1(…). Speech supplies `ping` / `kali`
there without inserting new visible operators. Division still applies to the
whole outer brace group. No result, rearrangement, or evaluation is supplied.

The first MathML layout remains three four-cell rows with six empty separator
cells and three empty bracket groups. The second remains one seven-cell row
with four empty separators and three occupied expression cells. Alignment,
`stretchy="false"`, `mspace` widths, and empty nodes are intact. Empty cells
are not spoken as zeros or matrix entries.

The spacing-only paragraph `fs-id1166424830424` is retained in CNXML/HTML and
explicitly omitted from speech; it has no empty SSML mark/paragraph. No other
instructional block is omitted. Grouping produces no invented answer cues.
Its punctuation analogy deliberately retains the pivot's `basa Indonesia`
reference; this is a declared source-reference choice, not an untranslated
reader label or a false claim that the source text was Javanese.

## Reader, SSML, assets, and canon

Directly parsed both readers. Naming contains 27 MathML trees and nine SVG
images; grouping contains six MathML trees and no images. Every rendered
MathML tree matches its generated CNXML tree, in the actual conversation /
academic / Indonesian column order. All nine embedded SVG payloads decode
to the exact manifest/output bytes, not merely similarly named files.
Source IDs are unique and complete. The 33 naming and 15 grouping body-track
blocks carry their correct explicit language tags. This verifies structure
and bindings, not browser rendering or readable size in the three-column view.

Parsed all six actual SSML documents independently. Each has an intentional
unmarked register-label introduction matching the transcript heading, followed
by exactly matching source-marked transcript bodies and 600 ms inter-block
breaks. Naming has 12 marked blocks and 13 paragraphs per track; grouping has
five marked blocks and six paragraphs per track. All source-marked paragraphs
are nonempty, with correct `xml:lang` and no mismatched, duplicated, or
unexplained omitted source marks.

Read actual readable canon entries for C07 (`lima`, including `sèket` and
`salawé`), C18 (`likur`, including `selikur` and `patlikur`), C21 `ping`,
C22 `para`, C24 `éwu/éwuan`, C25 `yuta`, C26 `wolu`, C27 `sanga/sangang`,
C28 `sewidak`, C29 `kurung`, and C30 `tutup` with its `bukak/mbukak` entries.
The arithmetic/count, written-sign, and open/close senses support components
of the current readings. They do not certify complete mathematical compounds,
prosody, registers, or unquoted teen/twenties forms. `kurung siku`,
`kurung kurawal`, `panglumpukan`, `yutanan`, `milyar`, `trilyun`, and other
declared loans/productive compounds remain provisional choices, not defects
proved merely by lacking a dedicated headword.

The earlier asset checkpoint actually inspected the three canonical JPEGs and
rendered all six Javanese SVGs with ImageMagick 7.1.2-26 and explicit
librsvg 2.40.20. That hash-bound standalone clipping check remains valid for
the currently embedded bytes. It is **not** an integrated-reader visual pass,
three-column-scale legibility test, browser compatibility result, native
certification, or listening review. The documented inherited 013 annotation
arrow direction difference between JPEG and Indonesian SVG was not silently
changed here.

## Tests and snapshot

Commands were run with `python -B`, without rebuilding:

```text
python -B -m unittest -v test_name_whole_workflow   25 passed, 0 skipped
python -B -m unittest -v test_grouping_workflow     19 passed, 0 skipped
```

The suites test current saved products and read-only deterministic replay,
not just source drafts. The naming receipt now binds final asset-manifest
SHA-256 `f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26`.
The current build receipts truthfully leave integrated visual, human language,
and listening review false, with zero synthesized audio and no whole-module
completion. Module completion remains **0 complete / 2 partial / 155
untranslated**; this checkpoint does not advance a module to complete.

Exact reviewed SHA-256 snapshot; paths are relative to `languages/jv-Latn-ID`:

```text
translation/a00-name-whole.edits.json 5eb1765402e494d95be2339d4c88b6b76bd19fe355fa2861d4325ad58579e6dc
audio/a00-name-whole.rules.json 0d1045c8ade187e40d39e14252511670f4f98ffb74be0257be4ca533b6b1b821
qa/a00-name-whole.draft-receipt.json 18e8793dc9ce1e33e8603a60737cc2fc972000b46ac08dfa1d3cd76d8c36ed3b
qa/a00-name-whole.build-receipt.json f0d739b5fd668fe14e835d0775d3d49627c4fb7121516a7b096c4ec9c4df4d95
provenance/a00-name-whole.en.cnxml b4f0a1d73243b8f923cb2ee15842b21235c24608c732b00929435ce8c9e55545
translation/a00-name-whole.jv-academic.cnxml 70c5aa4a996dd7a4e7518f39228c475684f53dad95a28cb2858b1a43712a4d07
translation/a00-name-whole.jv-conversation.cnxml 6b3cdcfdf58820dbf1e65c4512786ab2b2d2fd12fb988e737c3ae713a7f6f107
translation/a00-name-whole.id-academic.cnxml 696c8b62fdc1df1fd5e69665e12f034a16ba64e600c849a914a6c343b96f3194
translation/a00-name-whole.assets.json f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26
review/units/a00-name-whole.html fe33e0d6009d8c9b95dd7b015da43d35079aba278ae7ee133ded5215a4e90a1a
review/audio/a00-name-whole.jv-academic.md 2bb10f0d3c30de18eee8bac0ae50dfa3166121c3168cdac8e29ed285a623eeea
review/audio/a00-name-whole.jv-academic.ssml a24adf218380fe5bf833f0ba72591c0164fa557d0ceb4d4de724ed40bc1a4806
review/audio/a00-name-whole.jv-conversation.md 4ee54fab0d14327eac80a1915baa2688e749c782c3518f3d8cb97c4f2de57475
review/audio/a00-name-whole.jv-conversation.ssml b8183ce6231b11caf8108d4df09e8f150a6d47720143e6a1756a594e18d4ff68
review/audio/a00-name-whole.id-academic.md 0f252a495cf7e1aae2b22e399023db4473b6b1fda9a807625b197236f5413e26
review/audio/a00-name-whole.id-academic.ssml 922eade13439dc52bc79c656399db28299157d75a8805722bd37688f71477f00
translation/a10-grouping-symbols.edits.json 6318da4f3b856b80940aad157bbe38788dfd81c04edf814733bb999c9f0e7c47
audio/a10-grouping-symbols.rules.json 5ae090b824586378202e76c1f16fddc0dcb9c3b87c37e6900d72c3371679f772
qa/a10-grouping-symbols.draft-receipt.json cc3085d4c92ad2c08d9160aeadd808f4d3e1dd2a0ee83ee96c37aa7b86bec6a0
qa/a10-grouping-symbols.build-receipt.json a728b039b4de1460248ee46d980f4512781304cb2772c8fc796cd362ce99acf0
provenance/a10-grouping-symbols.en.cnxml be0da5c08fda7f7bfb1063be71a62317f00e3eb13c14239c7287dcc9acd4c550
translation/a10-grouping-symbols.jv-academic.cnxml 3886f30a33cf6c0f2bb194f92bea0fcf80a96604985ca896e7db735eca1f0eea
translation/a10-grouping-symbols.jv-conversation.cnxml 0b73a1a364196a02cb1804df5375fa6b120407d711dbd70cd67dfebc14555790
translation/a10-grouping-symbols.id-academic.cnxml 69a1ff4e4ceb95c05467206c059375ce6c613baeb269f0cb0faaa3c689585a3a
review/units/a10-grouping-symbols.html 8614d94d3ecb1d8ddbaea2ac93d3e62d8953328737ab7039ba9a81dbe2fa4bf8
review/audio/a10-grouping-symbols.jv-academic.md 532172080f58702a6ad4c11f543f1eb584badb7a554371b17d98a806f001e98a
review/audio/a10-grouping-symbols.jv-academic.ssml 6e3befc82b6138daab71e275b19c991deab10ca2480df3ef2f4f17b3368affae
review/audio/a10-grouping-symbols.jv-conversation.md c2a96475c0be390fbeb3a49c727593bad65b479fa85ac6a8eb12abd091ec4eed
review/audio/a10-grouping-symbols.jv-conversation.ssml 9562745e131f339bda57bd600251f5e08d3d9fba58e2566b3f1cf0ba2999d8d9
review/audio/a10-grouping-symbols.id-academic.md 99faa70a41a6a51b8baaef37e1cd0d3a76ed1cb86c0378c30acd78bb2d69dcda
review/audio/a10-grouping-symbols.id-academic.ssml 3e63a52b1199209963c9c5100c7f7c5be90ad2bc6218d6863e2b3da193f56001
```

Any later shared-renderer repair/rebuild supersedes these hashes and needs its
own verification. The current list finding must not disappear merely because
the source/narration checks pass. Full A00/A10/AX-2 work continues.

## Producer follow-up after c858dc5 — 2026-08-31

The shared renderer now outputs the source eip-375 as an ordered Arabic list
in all three tracks. Seven new shared reader-contract tests include this exact
saved-reader regression, alphabetic numbering, summary exposure and mtext
integrity. All earlier readers were rebuilt, so the HTML/build-receipt hashes
above are historical rather than the current-output hashes. The reviewed
translation, MathML, narration and asset bytes were not changed by this reader
repair. This producer note is not an independent browser or visual pass.
