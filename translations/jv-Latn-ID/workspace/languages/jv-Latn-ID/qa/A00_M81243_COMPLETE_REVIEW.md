# A00 `m81243` complete-source candidate — independent cross-component review

Review snapshot: 2026-09-01, workspace baseline
`1f451035ef797aed302d76fd98c9a249b72d12a9` (`Build source-positioned A00
summary components`). This report changes no source, translation, asset, rule,
builder, generated output, coverage record, or Git state.

## Verdict

**The automated independent cross-component review does not close on this
snapshot.** I found one material P2 integration defect: the complete reader and
complete Indonesian transcript/SSML silently omit the reviewed rounding
component's required accessibility/source-discrepancy notice, although the
complete Indonesian reader still embeds the three inherited image alts that
incorrectly describe the marked number-line points as orange. The bounded
rounding reader also has a second editorial sentence warning that its original
external destinations are not included offline; the complete reader drops that
sentence too.

All `183` aggregate source-marked blocks per track, their order, and their body
text are otherwise exact. The defect is outside those marks, which is why the
current `183`-mark assertions do not detect it. The repair should carry the
reviewed Indonesian accessibility notice exactly once into the complete reader,
Indonesian transcript, and Indonesian SSML outside the `183` source marks; it
should carry the offline-link sentence once in the complete reader; it should
bind and test both; and it should not add either notice to the two Javanese
tracks. The source CNXML and mark count need no change.

No other cross-component source, hierarchy, ID, MathML, exercise/answer,
asset-byte, reader, link, marked-narration, arithmetic, deterministic-product,
or prior-output defect was found. Coverage correctly leaves this as a pending
candidate and leaves the whole-module count unchanged. This report does **not**
mark `m81243`, A00, A10, AX-2, or the commissioned assignment complete.

## Binding scope and exact sources

I reread `AGENTS.md`, `USER_INSTRUCTIONS_VERBATIM.md`,
`FULL_ASSIGNMENT_USER_INSTRUCTION.md`, `COORDINATING_TASK.md`, the current
locale `GOAL.md`, and all `203` current lines of `DECISIONS.md` before review.
The full assignment remains all A00, all A10, and AX-2. A complete-source-scope
candidate for one module is not whole-module approval and is not assignment
completion.

Both source repositories are clean at the locked commit. `git rev-parse`,
`git cat-file`, and direct SHA-256 checks gave:

| Source | Commit | Tree | `modules/m81243/index.cnxml` blob | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| Indonesian A00 | `3de9207f56f8b5c57c017abf973fb04e00d740f1` | `12bfaf8b678cae9675bedf05fd12c58da2070b1e` | `90def09ee1dbfdc66aa8bc910938ad7684668e97` | 99,085 | `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251` |
| Canonical English | `38cae454e644abf9f0a623e876994553881597c9` | `7907e4c81d43de1c3b6da173f0eb273c01dc5b55` | `612244f80ecb6bce0f811c9d99204ae2f9f7a4f5` | 99,062 | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |

The saved complete English witness is byte-identical to the pinned English
blob. Indonesian and English have the same element-tag sequence, ordered ID
sequence, four document roots, eight content-section anchors, and exercise
solution-presence topology. The newline-delimited ordered `628`-ID digest is
`14400795b0ec9945c48a0af1e899e2ccbf8b9c50362bd58bfba2ce4f8c854564`.

The four root positions are exact:

| Original path | Root | IDs | MathML | Media | Exercises | Supplied / absent solutions | Tables | Definitions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `[0]` | `title` | 0 | 0 | 0 | 0 | 0 / 0 | 0 | 0 |
| `[1]` | `metadata` | 2 | 0 | 0 | 0 | 0 / 0 | 0 | 0 |
| `[2]` | `content` | 612 | 249 | 47 | 88 | 59 / 29 | 8 | 0 |
| `[3]` | `glossary` | 14 | 0 | 0 | 0 | 0 / 0 | 0 | 7 |

All seven definitions occur under the outer glossary and none under content.
All eight tables occur under content. Metadata remains at `[1]`; the glossary
remains at `[3]`. Content IDs are globally unique, not merely unique within a
component.

The exact content order and independent per-section inventory are:

| # | Anchor / component | IDs | MathML | Media | Exercises | Supplied / absent | Tables |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `fs-id1830385` / `a00-number-sense` | 44 | 17 | 1 | 3 | 3 / 0 | 0 |
| 2 | `fs-id2340048` / `a00-place-value` | 43 | 51 | 9 | 3 | 3 / 0 | 2 |
| 3 | `fs-id1883656` / `a00-digit-place` | 31 | 40 | 2 | 3 | 3 / 0 | 0 |
| 4 | `fs-id1321580` / `a00-name-whole` | 53 | 9 | 3 | 6 | 6 / 0 | 1 |
| 5 | `fs-id1339359` / `a00-write-whole` | 57 | 6 | 3 | 6 | 6 / 0 | 0 |
| 6 | `fs-id2472737` / `a00-rounding` | 104 | 69 | 23 | 9 | 9 / 0 | 5 |
| 7 | `fs-id2296006` / summary recap | 7 | 0 | 1 | 0 | 0 / 0 | 0 |
| 8 | `fs-id2279009` / final exercises | 273 | 57 | 5 | 58 | 29 / 29 | 0 |
| **Total content** |  | **612** | **249** | **47** | **88** | **59 / 29** | **8** |

## Three complete CNXML assemblies

An independent standard-library tree walk compared each complete target with
the pinned Indonesian tree and with its actual saved component roots. It made
`33` exact semantic component-tree comparisons: eight sections plus title,
metadata, and glossary in each of three tracks. Each track has the same ordered
`628` IDs once, `249` MathML roots, `47` images, `88` exercises, the same
`59` supplied/`29` absent solution topology, eight tables, and seven glossary
definitions. The ID target is a semantic full-tree replay of the Indonesian
source. Javanese roots explicitly carry `jv-Latn-ID`; the ID source contract is
not given a fabricated root language attribute.

| Complete CNXML | Bytes | SHA-256 |
| --- | ---: | --- |
| `provenance/a00-m81243-complete.en.cnxml` | 99,062 | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |
| `translation/a00-m81243-complete.id-academic.cnxml` | 98,959 | `3c9702a09d30d98f8442ed887e611fcca1f80df42cfcd86ce62e20d42a7b86f9` |
| `translation/a00-m81243-complete.jv-academic.cnxml` | 99,866 | `d3c54ba1094123b60d6feb317f60fff511439da7dece2c6e516cfa6b923199b1` |
| `translation/a00-m81243-complete.jv-conversation.cnxml` | 97,791 | `933364162c2ec5a2bd45bf74b3ab161aaa5e9354be516a6139bcebaccdbd4882` |

For every one of the `249 × 3 = 747` target MathML roots, element order,
namespaced tag sequence, attributes, and every non-`mtext` token matched the
Indonesian source. The bounded linguistic `mtext` changes remain component
decisions; no numeric/operator mutation appeared at assembly.

Assembly receipt: 19,610 bytes,
`bb3f7406f842c4f4c56410b6c8b4e105e7a52a65d5ad0b26f6b55565318bcf85`.
Build receipt: 23,737 bytes,
`4251ae823cb2c86b4a2e07babc8137631644906189164f25d06a61f277e9b03e`.

## Assets and reader

The complete source has `47` unique image `src` keys. Seven manifests bind
`46` of them; the initial number-line SVG is the separately receipt-bound
first-section mapping. I verified all `46` declared ID source bytes plus that
special source byte against the clean pinned ID repository, including declared
Git-blob identities where present. I also read and verified all `42` declared
canonical witnesses directly from the existing pinned full archive; this was
asset verification, not a renewed supply/license audit.

| Manifest | Entries | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `a00-place-value.assets.json` | 9 | 31,035 | `dc5ce29974b18b890932c49fa2493a0cfafed2d6a07666e1ba0516e845fd9bea` |
| `a00-digit-place.assets.json` | 2 | 24,887 | `c977cfea69046afacb3da1ef62996f45d2cef80808f1d6f005556f1e9285dcfe` |
| `a00-name-whole.assets.json` | 3 | 34,923 | `f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26` |
| `a00-write-whole.assets.json` | 3 | 7,323 | `46a9f8144985444fd135148bac7733596fb8353f380de1f4e0abb15a0343bb29` |
| `a00-rounding.assets.json` | 23 | 91,524 | `ee409884dfe05113ce081ab155f0d531aa3ce1273582b3bd27640deb861d4e33` |
| `a00-whole-summary.assets.json` | 1 | 11,753 | `6ff6ff6b152575f9629caf7270ff0012dd721ae64ab4379df76e60a13713202b` |
| `a00-section-exercises.assets.json` | 5 | 7,609 | `2e0af9ba286a88d9b1a53605154a8b2598c367f5ac82aa5a97730a808c09eb11` |

All `141` track-output slots match declared SHA-256, byte length where
declared, and actual SVG/PNG/JPEG signature. They resolve to `95` unique output
paths and `84` unique byte hashes because unchanged assets and identical
register assets are intentionally shared. The only cross-source-key path reuse
is the three authorized summary/digit-chart outputs: the distinct
`011.jpg.id-ID.svg` and `011.png.id-ID.svg` source identities have the same
pinned ID SVG bytes, SHA-256
`139263ebfe895df0abcaf00fa63c949b38e5edc352239ed70ec42837625fee13`.
No other cross-source output-path collision was found.

Independent HTML parsing, without the project reader parser, gave:

- 7,830,803 bytes; SHA-256
  `db4d248c7f548457605c413ec4fdd2198f7709a1300647e1b4a22d205c348bb9`;
- `1,884` unique HTML IDs: the ordered `628` source IDs under each exact track
  prefix, with none missing or repeated;
- `747` MathML roots, `141` nonempty-alt embedded images, `24` rendered tables,
  and `33` track panels (`11` per track);
- every embedded data payload byte-identical to its registered track asset;
- `39` links: `24` resolving fragments, `9` resolving relative files, and the
  exact two allowed OpenStax URLs repeated in three tracks (`6` external
  links); and
- no script/iframe and no leaked metadata UUID.

The external destinations were not fetched and are not asserted available.
The missing offline-link notice is part of the defect above.

## Exact aggregate narration

I parsed the actual dependency receipts, component Markdown, component SSML,
aggregate Markdown, and aggregate SSML without calling `full_blocks()`. All
component transcript hashes match their receipts; every component transcript
block equals its corresponding parsed SSML paragraph. The component mark
counts are:

| Dependency | Marks per track |
| --- | ---: |
| summary title/metadata/recap/glossary | 14 (`1 + 1 + 5 + 7`) |
| number sense | 13 |
| place value | 16 |
| digit place | 9 |
| naming | 12 |
| writing | 9 |
| rounding | 30 |
| final exercises | 80 |
| **Aggregate** | **183** |

The aggregate sequence is source-monotone and has no duplicate mark. All
`183 × 3 = 549` aggregate `(mark, body)` pairs equal the reviewed component
dependency bodies exactly after only the declared generic section-title mark
renaming. Transcript bodies contain neither the metadata UUID nor raw content
ID `m81243`.

There are `16` derived structural marks, all bound to real source positions:

- outer title: `m81243--outer-title`;
- metadata objective list: `m81243--para-00001--objectives`;
- eleven anonymous titles:
  `m81243--fs-id1830385--title`,
  `m81243--fs-id2340048--title`,
  `m81243--fs-id1883656--title`,
  `m81243--fs-id1321580--title`,
  `m81243--fs-id1339359--title`,
  `m81243--fs-id2472737--title`,
  `m81243--fs-id2296006--title`,
  `m81243--fs-id2318815--title`,
  `m81243--fs-id1717629--title`,
  `m81243--fs-id1345943--title`, and
  `m81243--eip-823--title`; and
- three recap procedure lists:
  `m81243--eip-id1170195386307--procedure`,
  `m81243--eip-id1170195386319--procedure`, and
  `m81243--eip-id1170195386333--procedure`.

There is correctly no fabricated `fs-id2279009--title`: that source section
has no direct title. Every anonymous-title owner has an actual direct anonymous
source title; every procedure owner is an actual source list.

| Track | Marks | Exact answer cues | Transcript bytes / SHA-256 | SSML bytes / SHA-256 |
| --- | ---: | ---: | --- | --- |
| conversational Javanese | 183 | 49 `Wangsulan.` | 56,116 / `7f6b996afb19311b71058603c04f2a6682402b607ba46c9904b26ab38630ed3c` | 62,970 / `09e8e6a84686312198b5c37abcfde624fb6726d93efe25b604c20688c41a4fd9` |
| academic Javanese | 183 | 49 `Wangsulan.` | 57,840 / `570b8f86645459c9764ad29112cc78a6a2bc5c0892ac1526044225cb48ca6414` | 64,694 / `79054990a4456250ddb4ce75b48f2740c1daaa20499999d8d285288a5a9bab01` |
| Indonesian source | 183 | 49 `Jawaban.` | 57,394 / `eb4453db32f8ddabbae6c4a505bfca7731756500232d32185ab8286495aed89b` | 64,243 / `0853645d9f75f93113c91c49af13d5ea8687a1f5021d57df147c7e3c36de7bd2` |

The `49` editorial cues plus ten source-provided solution titles account for
all `59` supplied solutions. None is attached to the `29` source-absent
solutions. The aggregate SSML roots have the exact locale, one unmarked track
label, then `183` `mark/p/break` triples with 600 ms breaks. No audio element,
voice fallback, or synthesized product exists.

## Material defect: lost unmarked rounding notices

The bounded rounding artifacts preserve a required Indonesian notice beginning
`Catatan aksesibilitas editorial: beberapa panah, garis bawah, warna, dan tanda
coret ...`. Exact occurrence counts are:

| Artifact | Bounded rounding | Complete aggregate |
| --- | ---: | ---: |
| HTML reader | 1 | **0** |
| Indonesian Markdown transcript | 1 | **0** |
| Indonesian SSML | 1 | **0** |
| literal `oranye` in HTML | 3 | 3 |

The bounded HTML notice box also says once that original external links are
retained but their destination content is not included in the offline reader;
the complete HTML has no notice box. The loss is deterministic:
`full_blocks()` extracts only Markdown `##` blocks and SSML mark paragraphs,
so it drops the reviewed unmarked ID notice; the complete reader renders only
assembled CNXML and does not import the bounded reader's editorial notice box.

This is not a disagreement about whether all `183` source marks are present:
they are. It is an omitted reviewed accessibility dependency that matters
precisely because the unchanged Indonesian assets/alts remain misleading or
incomplete. Current complete-candidate tests assert marked bodies but do not
assert required pre-mark/editorial material. Automated cross-component review
therefore remains open until a repaired snapshot is independently rerun.

## Source discrepancies carried or exposed

The complete assembly otherwise retains the already reviewed, source-bound
handling rather than silently rewriting pinned sources:

- Writing: the English alt for the `073` thousand group incorrectly says
  `742`; actual English/ID math, ID alt, source SVG, and canonical JPEG show
  `073`. The targets retain the declared correction and do not change source.
- Rounding: three retained number-line points are teal/cyan, not the inherited
  orange/black alt description. Current Javanese alts and marked narration are
  location-focused. Some untouched ID redraw arrows, underlines, cross-outs,
  and group marks are misleading or incomplete; the Javanese derivatives carry
  the separately reviewed repairs. Three stage PNGs remain declared JPEG in
  source CNXML but are embedded with actual PNG MIME. English result alts for
  `3,978` and `29,504` name the wrong rounding place; the ID/Javanese content
  retains the correct hundred/thousand request. The missing aggregate notice
  is the defect above.
- Summary: the canonical `011.png` is actual PNG despite a JPEG declaration.
  Its localized ID SVG is byte-identical to the earlier JPEG-named localized
  SVG, but the canonical PNG and JPEG are not claimed identical. Source alt
  `seratus miliar`, observed ID SVG `Ratusan miliar`, and target SVG
  `Atusan milyar` remain explicitly distinguished; the value is still
  `10^11`.
- Final exercises: `fs-id2279009` has no direct source title. The complete
  reader's `Content section 8 of 8` heading remains explicitly editorial UI,
  not a source title/ID. The self-check SVG/CNXML wording distinction remains
  bounded by the existing component rules; no score or absent answer is
  inferred.

## Independent finite arithmetic

Using positive-integer arithmetic and digit extraction, not a production
number parser, I recomputed `86` bounded witnesses:

| Category | Checks |
| --- | ---: |
| number-sense age differences | 3 |
| place-value wallet/base-ten models | 5 |
| digit-place number decompositions | 4 |
| digit-place answer positions | 15 |
| naming number decompositions | 7 |
| writing number decompositions | 7 |
| complete rounding-section cases | 17 |
| recap chart reconstruction | 1 |
| final-exercise supplied rounding pairs | 15 |
| final-exercise supplied block models | 2 |
| final-exercise digit/place answers | 10 |
| **Total** | **86** |

Nearest-multiple cases used `((n + unit//2)//unit)*unit`, so ties select the
upper multiple without floating approximation. Group witnesses were recomputed
as `sum(group × scale)`. Digit answers were recomputed as
`(value // place) % 10`, including zero positions. These checks authorize
neither a generic runtime parser nor invention of any of the 29 absent answers.

## Independent rejection probes

Standalone exact-tree/list/byte validators, written for this review and not
importing the producer guards, rejected `9,073` mutations with eight intact
controls:

| Standalone category | Rejections |
| --- | ---: |
| complete targets: duplicate IDs | 1,884 |
| target MathML tokens | 747 |
| target media paths | 141 |
| remove supplied solutions | 177 |
| insert absent solutions | 87 |
| table kind | 24 |
| glossary-definition kind | 21 |
| adjacent content-section order | 21 |
| document-root order/metadata/glossary placement | 9 |
| aggregate duplicate marks | 549 |
| changed bodies | 549 |
| omitted blocks | 549 |
| repeated blocks | 549 |
| adjacent block order | 546 |
| SSML break changes | 549 |
| SSML locale changes | 3 |
| asset duplicate/missing source keys | 94 |
| declared output hash changes | 141 |
| output-byte corruption | 141 |
| output MIME changes | 141 |
| unauthorized output-path collisions | 47 |
| manifest identity changes | 7 |
| complete-reader duplicate IDs | 1,884 |
| embedded-image changes | 141 |
| bad links | 39 |
| wrong panel locales | 33 |
| **Standalone total** | **9,073** |

I then called the public producer guards with `91` additional mutations and
eleven intact controls: `27` target topology mutations, two pinned-source
changes, five saved-assembly changes, seven manifest changes, two special
number-line changes, and all `48` component transcript/SSML dependency-file
changes. All `91` were rejected. Combined review evidence is therefore
**9,164 rejections and 19 intact controls**. This count does not include
producer unit-test mutations and does not treat an assertion that merely ran as
independent evidence.

## Determinism, tests, coverage, and prior products

The assembly producer returned the same five in-memory products twice and all
five matched saved bytes: 415,288 bytes total, output-hash-map digest
`77f5aefca92728695248219e52dcdd85c38b54a5b71eab9738e4742d8a979dce`.
The complete build returned the same eight in-memory products twice and all
eight matched saved bytes: 8,217,797 bytes total, output-hash-map digest
`68cac2e7d0fb595f0eca2b5cbc73033d77726c1396ba543698d62b4e7cebf645`.

Read-only commands and outcomes:

```text
python -B -m unittest -v test_complete_a00_assembly.py test_complete_a00_workflow.py
Ran 8 tests in 22.532s — OK (shell 24.331s)

python -B draft_complete_a00_module.py --check
exit 0 — 8.710s

python -B build_complete_a00_module.py --check
exit 0 — 11.589s

python -B coverage.py --check
exit 0 — 44.404s

python -B build.py --check
exit 0 — 4.378s
```

For an attributable whole regression, I ran the exact 20 test modules tracked
at baseline `1f4510...` plus the two candidate modules, explicitly excluding
concurrently introduced untracked next-module asset tests:

```text
python -B -m unittest <20 baseline modules> test_complete_a00_assembly test_complete_a00_workflow
Ran 202 tests in 981.575s — OK (22 modules; shell 997.506s)
```

This is the producer's prior `194`-test surface plus the eight candidate tests.
An earlier unrestricted discovery was started while unrelated untracked
subtraction/use-algebra asset files were actively changing; it emitted an
incomplete failure/error stream and entered a very slow new asset test, so I
interrupted it and do not count it as evidence. After stabilization the seven
subtraction asset tests passed separately; the use-algebra tests are outside
this candidate and were not used for this verdict.

Excluding the new candidate entry, recursive coverage-hash extraction found
`299` existing coverage-bound files on disk. Every stored SHA matched; every
file was byte-identical to `HEAD` at `1f451035ef797aed302d76fd98c9a249b72d12a9`.
They total 13,615,394 bytes and have path-plus-byte aggregate SHA-256
`074324741651cec0a806ee8d617eda02c56996fb6f2a6302d72ca1ba87e2f642`.
Two collection references are external source-repository paths, not missing
locale products, and were excluded from that on-disk locale-file comparison.

Coverage remains exactly `0 complete / 2 partial / 155 untranslated`. Its
candidate state is
`complete_source_scope_assembled_and_built_independent_cross_component_review_pending`,
`independent_cross_component_review` is `pending`, `whole_module_complete` is
false, and the effect on baseline module counts is
`none_pending_independent_cross_component_review`. That is the correct status
for this failed review snapshot. I did not edit coverage.

## Evidence limits

This review provides automated source/tree/hash/byte/link/narration/arithmetic
evidence. It does not provide native Javanese or Indonesian review, educator
approval, pronunciation/prosody review, synthesized speech, listening review,
provider/voice validation, publication approval, or assignment completion.

Existing component reports document standalone inspection of selected
derivative previews, including the rounding, writing, summary, and final
exercise assets. I verified the bound product bytes and all 299 prior
coverage-bound files remained unchanged; I did not rerender or visually
reinspect every asset in this pass. A static standalone preview cannot establish
legibility, reflow, zoom behavior, table navigation, or alt/visible agreement
inside the 7.83 MB three-column complete reader. I did not open the complete
reader in an integrated browser, run a keyboard or screen-reader pass, listen
to speech, select a supported voice, or synthesize audio. The missing notice
was found by exact artifact comparison, not by claiming any of those human or
integrated checks.

## Reviewed implementation snapshot

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `scripts/draft_complete_a00_module.py` | 7,309 | `4c5200fedf0a23a5be11de3bc87e5b86f53ce9ac4035701e476aa9b49faeb14b` |
| `scripts/complete_a00_checks.py` | 6,354 | `7e8a6880a1ad94fd7d40856447243fbea0ecc8e283bfc6f77efd826d613057eb` |
| `scripts/build_complete_a00_module.py` | 8,539 | `3996b35cf28ce3813f767bae7e2811ac04e683e15adf3759153d347cb704c2ea` |
| `scripts/test_complete_a00_assembly.py` | 3,092 | `f82e620e96034bd7d1d6da552c70ef1eb670cc50b56b9ef3ee17efb2359c128a` |
| `scripts/test_complete_a00_workflow.py` | 4,532 | `c275cb54e73674695443d19980ed4442dd515f22c50c595dce637b54ec6f3fb4` |
| `scripts/coverage.py` | 39,184 | `3c03b84386ffb0f7cf82c1c9b3d4fb96e8875fa570106b04f9b8aa117ba7652f` |
| `coverage.json` | 309,704 | `cbe1a0ba74f8fcfa187e64c07535b3e75d87b663247435f1e636a5bfe3281670` |

These hashes identify the failed candidate snapshot reviewed here. A notice
repair necessarily changes complete reader/audio/build receipt hashes and must
receive a fresh independent cross-component check; this report must not be
reinterpreted as approval of those future bytes.
