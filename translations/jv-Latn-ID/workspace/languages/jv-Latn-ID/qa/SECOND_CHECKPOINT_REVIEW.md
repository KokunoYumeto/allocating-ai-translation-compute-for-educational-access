# Four-unit checkpoint review

2026-08-30 · independent artifact review of the four currently built excerpts.
This review did not alter translation sources, builders, coverage, or generated
outputs. It is not a supply/license audit, native-language approval, or release
sign-off. The entire A00/A10/AX-2 assignment remains unfinished.

## Outcome and findings

No material numerical, operand-order, answer, or readout discrepancy was found
in these four units. The review read all twelve narration transcripts and the
four retained canonical English excerpts, including their MathML and image
descriptions; it did not infer correctness solely from a previous QA receipt.

Two non-mathematical observations were sent to the coordinating producer:

Both observations below were resolved and independently rechecked during the
same review. Their initial state is retained for decision history; see the
follow-up at the end of this document.

1. **Minor narration polish:** the conversational number-sense transcript at
   `m81243--fs-id2269442` says `Tandha “tandha telung titik” ...`. The generated
   glyph-name replacement repeats `tandha`. The meaning is intact, but a
   source-bound narration-only adjustment could avoid the repetition. Do not
   alter the written source ellipsis or turn it into an additional continuation.
2. **Checkpoint documentation reconciliation:** during the first read,
   `qa/STATUS.md`, `canon/README.md`, and `NEXT_UNIT.md` still described the
   earlier 18-entry/two-excerpt state. At the subsequent read, the producer had
   corrected `canon/README.md` to 23 entries and added the new consultation
   stages. `qa/STATUS.md` and `NEXT_UNIT.md` still pointed to the now-built
   place-value and operation-symbol excerpts. Updating those two documents is
   pending in this review snapshot. This is a stale-document observation, not
   an assertion that the source-bound outputs or the full coverage ledger are
   wrong. The producer's checkpoint-document update was already in progress.

## Exact reviewed scope

| Unit | Source boundary | Source IDs | MathML expressions | Narration blocks per track |
| --- | --- | ---: | ---: | ---: |
| `a00-number-sense` | `m81243/fs-id1830385`, complete selected subsection | 44 | 17 | 13 |
| `a10-variable-bridge` | `m82453/fs-id1170655150800`, first seven child nodes including title, through the constant definition | 13 | 9 | 7 |
| `a00-place-value` | `m81243/fs-id2340048`, complete selected subsection | 43 | 51 | 16 |
| `a10-operation-symbols` | `m82453/fs-id1170655150800`, title context plus source children `[7:13]`, through the multiplication-cross warning | 12 | 11 | 7 |

Every row has distinct Indonesian-source, provisional academic-Javanese, and
conversational-ngoko tracks. The ID counts sum to 112, but there are **111
distinct module-plus-ID anchors**: the A10 parent section is contextual overlap,
not newly translated twice. Neither A00 m81243 nor A10 m82453 is complete, and
the earlier collection modules have not thereby become translated.

## Mathematical and readout evidence

- Number sense preserves counting numbers starting at 1 and whole numbers also
  containing 0. The worked list `0, 1/4, 3, 5.2, 15, 105` and both practice lists
  retain their values and correct answer sets. Fraction numerator/denominator
  order, decimal readouts, zero inclusion/exclusion, the zero-to-six number
  line, and its increasing/decreasing directions agree with the canonical
  source. Both untitled practice answers have explicit `Wangsulan`/`Jawaban`
  cues in the appropriate tracks.
- The Greg/Alex table keeps `12 -> 15`, `20 -> 23`, `35 -> 38`, and `g -> g+3`.
  Each numeric age difference is 3; the prose maintains Alex as the older
  person. `g`, `x`, `y`, `a`, `b`, and `c` are identified as letters in narration,
  not silently read as words or changed to another variable.
- Place value distinguishes 537 from 735. The wallet calculation is
  `3*100 + 7*10 + 4*1 = 374` US dollars, not a currency conversion. The block
  models preserve `100+30+8=138`, `200+10+5=215`, and the practice answers
  `100+70+6=176` and `200+30+7=237`. Table headers and totals remain associated
  with their values. The nine image descriptions preserve the displayed
  counts, denomination labels, highlighted digits, and arrow relationships.
- Operation notation retains `a+b`, `a-b`, all five multiplication forms, and
  all four division forms. In long division, **b is outside and a inside**, so
  the readout remains a divided by b. The examples retain `9-2` and `4*8`.
  The `3xy` warning distinguishes a literal x from the multiplication cross:
  `3 times y` is not conflated with `3 times x times y`. The result-column
  heading's ellipsis is treated as a heading cue, not an infinite sequence.

## Actual canon consultation in this review

Read the local readable KBJI entries, not just their citations:

- C17 `rolas.txt`: confirms the irregular cardinal twelve used in the age table.
- C18 `likur.txt`: confirms the twenties family and the specifically recorded
  forms. It does **not** directly attest every productive member; `telulikur`
  remains appropriately marked as provisional in the terminology/consultation
  records rather than passed off as a verbatim dictionary example.
- C19 `atus.txt`: distinguishes the numerical hundred sense and confirms the
  recorded hundred-family evidence. The place-value examples are numerically
  consistent; that is not proof of universal regional phrasing or prosody.
- C21 `ping.txt`: supports the multiplication-related lexical choice,
  including `ping-pingan`.
- C22 `para.txt`: distinguishes the division sense from unrelated homographs
  and supplies the recorded `paran` / `para gapit` evidence.
- C23 `gunggung.txt`: supports sum/total, distinct from the unrelated coaxing
  sense. It does not certify every composed academic table sentence.

The current actual canon lock has 23 entries: 18 initial entries plus five
topic-driven extensions. This follows the user's instruction to begin with
10–20 readable examples and extend when a new topic needs evidence. These are
lexical/usage references, not 23 complete mathematics textbooks. Mathematical
compounds, borrowed terms, register composition, and pronunciation remain
explicitly provisional; no dictionary lookup implies educator approval.

## Independent non-mutating checks

Using a separate standard-library inspection, without calling the translation
or narration builders:

- Compared ordered `mn`, `mi`, and `mo` mathematical tokens and attributes in
  canonical English, Indonesian, and both Javanese CNXML tracks. They agree.
  This targeted check does not claim that every linguistic `mtext` string is
  invariant; those passages were reviewed for meaning separately.
- Compared all twelve Markdown transcript bodies with their SSML paragraphs,
  after whitespace normalization. All agree. Source-mark sequences and all
  `id-ID` / `jv-Latn-ID` root locales agree as well.
- Inspected the three HTML artifacts without rendering them. They contain
  78, 153, and 33 MathML instances respectively: 264 total. They contain 3,
  27, and 0 embedded described images: 30 total. IDs are unique per document,
  within-page links resolve, image sources are embedded data URLs, and no
  script or iframe tags occur. These are structural observations, not a
  visual layout or screen-reader pass.
- The reviewed audio directory contains `.md` and `.ssml` files only. The
  receipts report zero synthesized audio. Text inspection is not listening.
- `coverage.json` and the current canon lock both say 23 canon entries. The
  coverage totals remain zero complete modules, two partial modules, and 155
  wholly untranslated modules, with the two additional built drafts tracked
  separately. No whole-book or whole-module completion was inferred.

## Snapshot witnesses

These hashes identify the evidence read, not a claim that subsequent production
changes should retain the same bytes. A later narration edit needs rechecking.

```text
qa/receipt.json
502a38891d94cbfdf161c2bb12d5223e71c923e96b691d1f190f732cd6acd275
qa/a00-place-value.draft-receipt.json
e1cec145cd4b58dd1500aac4251115815abaa81cece75ddc3be34c7043176da6
qa/a00-place-value.build-receipt.json
246541a3ee6a5ed00522a8d14d4d08d5b4664ea79ef52e0af58bb4caaf54a8c6
qa/a10-operation-symbols.draft-receipt.json
fc2ea1fe45fba4c4cc7da7f99183281666a6de07cb5dee8814df4b01e3d94be2
qa/a10-operation-symbols.build-receipt.json
b2193620e7c3de2231ea54c7948b84851d6f992b1e5385cdc7e7a0897a5208d7
canon/sources.lock.json
5ce18e4bfa7e85d0f23da37cf6583fa844510ca44dd8edad7328d92edd801b28
coverage.json
23b8e111ee9e773a450738818fa2151a92e93781164af2cddde6100383fbd8f7
```

The reviewed 24 narration artifacts have a combined witness
`6d5bda8489d1386ebb4b76bf99145d76734894073884a7a7397355bf1ab7dd66`:
SHA-256 of Python `json.dumps(path_to_sha256, sort_keys=True).encode()` for
the twelve `.md` and twelve `.ssml` paths relative to the language directory.

## Still pending

Rendered desktop/mobile/zoom inspection; actual MathML screen-reader behavior;
native Javanese educator and social-register review; pronunciation/provider
compatibility and listening review; the rest of every assigned module and the
whole-assignment accessibility/publication workflow. The Browser runtime's
earlier initialization failure is not a visual pass. Continue production after
the checkpoint; this four-unit review is not assignment completion.

## Same-review follow-up — observations closed

The producer removed the redundant leading `Tandha` from the conversational
number-sense narration at `m81243--fs-id2269442`. The phrase now names the
three-dot sign once. The written CNXML/source notation was not changed by that
narration correction. Independently reran the ordered mathematical-token checks
and all twelve transcript/SSML body, source-mark, and locale comparisons after
the correction: all still agree.

Independently reread the revised `canon/README.md`, `canon/CONSULTATIONS.md`,
`qa/STATUS.md`, and `NEXT_UNIT.md`. The canon count is reconciled to 23, the new
production-stage consultations are recorded, and both additional review builds
are distinguished from unfinished modules. Continuation now points to A00
`fs-id1883656` and to A10 spacing child `fs-id1171789687379` followed by the
equality introduction `fs-id1170655208137`, rather than restarting the excerpts
already built. The next digit-place and equality work is not included in this
four-unit review or silently treated as completed.

Updated pilot receipt SHA-256:
`854203c7b5aaa61dca71196548dc1f6d29e948fe3cf3e0f53749f4e00484a859`.
Updated combined 24-artifact narration witness, using the same method above:
`19d48d9f0e1e84f652540d06497ed7b85e2e505ff015a0550ea538a7ecb11160`.
The earlier hashes remain initial-snapshot evidence, not current-output claims.

No material numerical, operand-order, or checkpoint-coverage defect remains in
the reviewed four-unit scope. All visual, native-language, social-register,
screen-reader, pronunciation/listening, and whole-assignment limitations above
remain open.

## Receipt-label refresh — current build witnesses

The producer regenerated the two unit build receipts to report explicit check
names for place-value table arithmetic, scoped headers, currency/figure speech,
exact source-tree fixtures, long-division order, and cross/ellipsis contexts.
The earlier build-receipt hashes above remain initial-snapshot history. The
current build-receipt SHA-256 values after this metadata refresh are:

```text
qa/a00-place-value.build-receipt.json
cf56640b820872cf705be7809f6737a7df5c75bad0017e01555e99cfcc9dfe4e
qa/a10-operation-symbols.build-receipt.json
8e3c92db4fb017e578703b74883fc55ecb90932f3b032f9cc8a0704186eb46ab
```

Independently confirmed that the pilot receipt still hashes to
`854203c7b5aaa61dca71196548dc1f6d29e948fe3cf3e0f53749f4e00484a859`
and all 24 reviewed narration artifacts retain the combined witness
`19d48d9f0e1e84f652540d06497ed7b85e2e505ff015a0550ea538a7ecb11160`.
No narration bytes changed in this receipt refresh. The read-only
`python -B -X utf8 languages/jv-Latn-ID/scripts/coverage.py --check` passes with
zero complete modules, two partial modules, and 155 untranslated modules.
