# A00 `m81243` complete-source candidate — independent repaired-snapshot rereview

Review snapshot: 2026-09-01, workspace baseline
`1f451035ef797aed302d76fd98c9a249b72d12a9` (`Build source-positioned A00
summary components`) plus the uncommitted complete-source candidate identified
by the exact hashes below. This report changes no source, translation, asset,
rule, producer, generated output, receipt, coverage record, Git index, or ref.

## Verdict

**The automated independent cross-component review closes on this exact
repaired snapshot.** The required Indonesian rounding accessibility notice now
occurs exactly once in the complete reader, Indonesian transcript, and
Indonesian SSML. The bounded offline-link sentence occurs exactly once in the
complete reader. Both notices remain outside all `183` source-marked narration
blocks, and neither Javanese transcript or SSML contains either notice. The
reader notice is one `lang="id-ID"` editorial box before the first complete
component and is not inside any track article.

The first failed review remains separately preserved at
`qa/A00_M81243_COMPLETE_REVIEW.md`, 23,552 bytes, SHA-256
`d80449f38d0844b73531e12adf247df05cc02289a294343be9275455b63d8e20`.
An intermediate repair had correct saved notice placement but trusted a
coherently edited bounded receipt and accepted three suffix mutations. That
intermediate state is not approved. The stable second repair pins all eight
reviewed audio/build receipts and all seven asset manifests before consuming
their contents; all four formerly relevant coherent notice mutations now fail
both the editorial guard and the downstream complete build.

This verdict is an automated structural/byte/dependency approval for the exact
candidate hashes in this report. It is not native-language, educator,
integrated-browser, screen-reader, pronunciation, listening, synthesis,
publication, whole-module, A00, A10, AX-2, or commissioned-assignment approval.
Coverage correctly remains pending until the coordinator incorporates this
verdict, and the whole-module flag remains false.

## Binding instructions and exact source pins

I reread the binding root/user/full-assignment/coordinator instructions, the
current locale goal and decision record, the complete producer/check/test
implementation, the bounded rounding reader and Indonesian transcript/SSML,
all regenerated complete reader/transcript/SSML/build-receipt bytes, and the
failed first review. The full assignment remains all A00, all A10, and AX-2;
this single complete-source candidate cannot complete that assignment.

Direct `git rev-parse`, `git cat-file`, clean-status, and SHA-256 checks against
the Git blob bytes gave:

| Source | Commit | Tree | `modules/m81243/index.cnxml` blob | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| Indonesian A00 | `3de9207f56f8b5c57c017abf973fb04e00d740f1` | `12bfaf8b678cae9675bedf05fd12c58da2070b1e` | `90def09ee1dbfdc66aa8bc910938ad7684668e97` | 99,085 | `7153ce88bcd4aea07fab4075bdb025884e07d534aafb6d06ff1bfbedbc46f251` |
| Canonical English | `38cae454e644abf9f0a623e876994553881597c9` | `7907e4c81d43de1c3b6da173f0eb273c01dc5b55` | `612244f80ecb6bce0f811c9d99204ae2f9f7a4f5` | 99,062 | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |

The English checkout applies a clean line-ending conversion, so its worktree
file hash is not used as the blob witness. The saved English assembly witness
is byte-identical to the pinned Git blob. Both repositories reported clean.
The newline-terminated ordered `628`-ID digest remains
`14400795b0ec9945c48a0af1e899e2ccbf8b9c50362bd58bfba2ce4f8c854564`.

## Exact source shape and three assemblies

All three target roots retain the four original direct children in exact order:
`title`, `metadata`, `content`, `glossary`. Metadata remains at `[1]`, content
at `[2]`, and the outer glossary at `[3]`. The seven definitions occur only in
the glossary; all eight tables occur only in content.

The eight content sections remain in exact source order, with independently
recomputed inventories:

| # | Anchor | IDs | MathML | Media | Exercises | Supplied / absent | Tables |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `fs-id1830385` | 44 | 17 | 1 | 3 | 3 / 0 | 0 |
| 2 | `fs-id2340048` | 43 | 51 | 9 | 3 | 3 / 0 | 2 |
| 3 | `fs-id1883656` | 31 | 40 | 2 | 3 | 3 / 0 | 0 |
| 4 | `fs-id1321580` | 53 | 9 | 3 | 6 | 6 / 0 | 1 |
| 5 | `fs-id1339359` | 57 | 6 | 3 | 6 | 6 / 0 | 0 |
| 6 | `fs-id2472737` | 104 | 69 | 23 | 9 | 9 / 0 | 5 |
| 7 | `fs-id2296006` | 7 | 0 | 1 | 0 | 0 / 0 | 0 |
| 8 | `fs-id2279009` | 273 | 57 | 5 | 58 | 29 / 29 | 0 |
| **Content total** |  | **612** | **249** | **47** | **88** | **59 / 29** | **8** |

Adding the two metadata IDs and fourteen glossary IDs gives `628` unique IDs.
Each track has `249` MathML roots, `47` unique image source keys, `88`
exercises with the same `59` supplied/`29` absent solution topology, eight
tables, and seven glossary definitions. All `747` target MathML roots retain
the Indonesian element/attribute shape and every non-`mtext` token; only the
reviewed linguistic `mtext` slots differ.

| Complete CNXML | Bytes | SHA-256 |
| --- | ---: | --- |
| `provenance/a00-m81243-complete.en.cnxml` | 99,062 | `396b0029798e054e5db6d7acde738cec9f9d8b86bc81da8cc3690d01ec07cf2b` |
| `translation/a00-m81243-complete.id-academic.cnxml` | 98,959 | `3c9702a09d30d98f8442ed887e611fcca1f80df42cfcd86ce62e20d42a7b86f9` |
| `translation/a00-m81243-complete.jv-academic.cnxml` | 99,866 | `d3c54ba1094123b60d6feb317f60fff511439da7dece2c6e516cfa6b923199b1` |
| `translation/a00-m81243-complete.jv-conversation.cnxml` | 97,791 | `933364162c2ec5a2bd45bf74b3ab161aaa5e9354be516a6139bcebaccdbd4882` |

The five-product assembly is unchanged: 415,288 bytes total. Two independent
in-memory generations were identical to one another and to saved bytes. Using
sorted `path + NUL + SHA-256(bytes) + NUL` records, its map digest is
`9091b80efee1a3ac8a0999e96655e18e06aef3f5649feb3f89046632ce7ab367`.
The unchanged assembly receipt is 19,610 bytes, SHA-256
`bb3f7406f842c4f4c56410b6c8b4e105e7a52a65d5ad0b26f6b55565318bcf85`.

## Exact notice repair

The complete artifacts now reproduce the reviewed bounded material as follows:

| Artifact | Accessibility notice | Offline-link notice | Position |
| --- | ---: | ---: | --- |
| bounded rounding HTML | 1 | 1 | one Indonesian editorial box |
| complete HTML | 1 | 1 | one `lang="id-ID"` box before the first component; outside all track articles |
| bounded Indonesian Markdown | 1 | 0 | preamble before first `##` |
| complete Indonesian Markdown | 1 | 0 | preamble before first `##`; absent from all marked bodies |
| bounded Indonesian SSML | 1 | 0 | exact paragraph child 1, before first mark |
| complete Indonesian SSML | 1 | 0 | exact paragraph child 1; first mark is child 2 |
| both bounded and complete Javanese Markdown/SSML tracks | 0 | 0 | first mark is child 1 in each SSML root |

The accessibility paragraph is exactly the bounded paragraph beginning
`Catatan aksesibilitas editorial: beberapa panah, garis bawah, warna, dan tanda
coret ...`. The link paragraph is exactly `Pranala luar asli dipertahankan; isi
tujuannya tidak disertakan dalam pembaca luring ini.` No marked body contains
either sentence. The complete Indonesian reader still contains the three
unchanged inherited `oranye` alts documented by the first review; the notice is
therefore material and is not treated as optional metadata.

Exact reviewed bounded dependencies are:

| Dependency | Bytes | SHA-256 |
| --- | ---: | --- |
| `qa/a00-rounding.build-receipt.json` | 2,295 | `7adfed7f384b80edaf1b6ecccd9d853e70c11c521bef33b3396cbdb013e11b57` |
| `review/units/a00-rounding.html` | 513,183 | `9eb50acdb173cd2abea0c39b546931e074db6ea63bc5402155f654da050ff017` |
| `review/audio/a00-rounding.id-academic.md` | 12,945 | `80022e2aa2b3e9788d16af4fca408d2bc4e6bc4c934247ede7371a76d3b02461` |
| `review/audio/a00-rounding.id-academic.ssml` | 14,161 | `bdc84882ed27d4ef9ef3591f62198c18b883ec1244658f612a4775d43a4d19dd` |

## Narration and answer boundaries

The independent composition used the actual component Markdown and SSML, the
summary mark groups, and the source section order, without treating the
complete producer's `full_blocks()` result as its own oracle. Component mark
counts remain `14 + 13 + 16 + 9 + 12 + 9 + 30 + 80 = 183` per track.

All `183 × 3 = 549` aggregate `(mark, body)` pairs equal both their component
Markdown and component SSML bodies, after only the declared generic
section-title mark renaming. All tracks have the same unique mark sequence,
from `m81243--outer-title` through `m81243--fs-id4338000`, in source-monotone
order. The sixteen previously reviewed derived structural marks are unchanged.
No source mark was added for either notice.

Each complete transcript still has exactly 49 explicit answer cues
(`Wangsulan.` or `Jawaban.`); with ten source-provided solution titles, these
cover all 59 supplied solutions and none of the 29 absent solutions.

| Track | Marks | Transcript bytes / SHA-256 | SSML bytes / SHA-256 |
| --- | ---: | --- | --- |
| conversational Javanese | 183 | 56,116 / `7f6b996afb19311b71058603c04f2a6682402b607ba46c9904b26ab38630ed3c` | 62,970 / `09e8e6a84686312198b5c37abcfde624fb6726d93efe25b604c20688c41a4fd9` |
| academic Javanese | 183 | 57,840 / `570b8f86645459c9764ad29112cc78a6a2bc5c0892ac1526044225cb48ca6414` | 64,694 / `79054990a4456250ddb4ce75b48f2740c1daaa20499999d8d285288a5a9bab01` |
| Indonesian source | 183 | 57,718 / `bb0822d2ecbd340623c2330066630fec047329f089b59cec7566c8d6d4bb2887` | 64,573 / `ad34c9aa5264bee5ecc3a5fcb88a2545656c60fbae24fce234db5380c8ec9f68` |

The four Javanese aggregate files are byte-identical to the failed snapshot.
Only the intended Indonesian pre-mark notice changed the two Indonesian audio
drafts. No audio element, voice fallback, or synthesized product exists.

## Assets and complete reader

All seven exact manifests remain pinned before parsing:

| Manifest | Entries | SHA-256 |
| --- | ---: | --- |
| `a00-place-value.assets.json` | 9 | `dc5ce29974b18b890932c49fa2493a0cfafed2d6a07666e1ba0516e845fd9bea` |
| `a00-digit-place.assets.json` | 2 | `c977cfea69046afacb3da1ef62996f45d2cef80808f1d6f005556f1e9285dcfe` |
| `a00-name-whole.assets.json` | 3 | `f7476bfa8211e8956ea89fcec6077e7bc3777190721cd29b673cd10fe0f77d26` |
| `a00-write-whole.assets.json` | 3 | `46a9f8144985444fd135148bac7733596fb8353f380de1f4e0abb15a0343bb29` |
| `a00-rounding.assets.json` | 23 | `ee409884dfe05113ce081ab155f0d531aa3ce1273582b3bd27640deb861d4e33` |
| `a00-whole-summary.assets.json` | 1 | `6ff6ff6b152575f9629caf7270ff0012dd721ae64ab4379df76e60a13713202b` |
| `a00-section-exercises.assets.json` | 5 | `2e0af9ba286a88d9b1a53605154a8b2598c367f5ac82aa5a97730a808c09eb11` |

The manifests bind 46 source keys; the separately pinned initial number line is
the 47th. All 141 track slots match their declared SHA-256, actual bytes, and
actual SVG/PNG/JPEG signature. They resolve to the unchanged 95 unique paths
and 84 unique byte hashes. The complete receipt has 160 exact dependency
entries: the assembly receipt, eight pinned reviewed audio/build receipts, 48
component audio files, the bounded editorial reader, seven pinned manifests,
and the registered output assets after intentional path deduplication. Every
dependency hash and all seven complete output hashes match actual bytes.

Independent standard-library HTML parsing gave:

- 7,831,274 bytes, SHA-256
  `78b514f82ab4756d910b5f52cb411abf8605f2126c888974b5239cfa4c3baea8`;
- `1,884` unique HTML IDs: the exact ordered `628` source IDs under each track;
- `747` MathML roots, `141` nonempty-alt embedded images, `24` rendered tables,
  and `33` track panels (`11` per track);
- every embedded data payload byte-identical to the manifest-selected asset;
- `39` links: `24` resolving fragments, `9` resolving relative files, and the
  two allowed OpenStax URLs repeated in three tracks (`6` external links); and
- no script, iframe, or leaked metadata UUID.

The external destinations were not fetched and are not asserted available.
The complete reader was not opened in an integrated browser for this rereview.

## Fail-closed mutation evidence

The intermediate repair accepted suffix mutations to the bounded reader
accessibility paragraph, bounded reader offline paragraph, and bounded
Indonesian Markdown paragraph when the mutable rounding receipt was coherently
changed. The stable repair closes that path by pinning the exact receipt before
using any of its output hashes.

I independently reran the four exact coherent mutations. Each was rejected by
both `rounding_editorial_material()` and the downstream complete
`build.products()` call with `Changed reviewed audio receipt: a00-rounding`:

| Coherent artifact + receipt mutation | Mutated artifact SHA-256 | Guard calls rejected |
| --- | --- | ---: |
| reader accessibility suffix | `5438fd73df6ce9a4a38df84f5c7bd8e53cde61fb6bdb079e7d4e9ee68d9bc2ee` | 2 / 2 |
| reader offline-link suffix | `1c77935c3d8f91d472c8a2827cc2f253f95c56f27c75d2caf436083bd8489d11` | 2 / 2 |
| Indonesian Markdown suffix | `ba80c97dfdcb2bf5ee1144cb3835b340e6e1d4009f381a685c399276e344a4a7` | 2 / 2 |
| Indonesian SSML suffix | `1cae869cb5722a5196e6733248b0777b7bbeec38999b8fa4c63ed97f213d570e` | 2 / 2 |

The same harness changed each of the eight pinned component receipts and each
of the seven pinned manifests independently: all `8 + 7` calls rejected, while
all sixteen intact controls passed. That harness therefore produced `23/23`
rejection calls and `16/16` controls; the count includes the two guard calls for
each of the four coherent notice cases.

A separate broad notice validator exercised removal, duplication, extension,
relocation/order, marked-body contamination, and Javanese contamination. It
rejected `24/24` mutations with the original receipt, `24/24` coherently
receipted variants, and all four formerly accepted variants again through the
cached downstream build: `52/52` rejection calls with `6/6` intact controls.
These 52 are reported separately and are not added to the overlapping 23-call
pin-boundary harness.

## Determinism, tests, coverage, and prior products

Two complete in-memory builds were identical to one another and all eight
saved products: 8,220,160 bytes total. Using the same sorted
`path + NUL + SHA-256(bytes) + NUL` scheme, the build map digest is
`6f3d23829bf329fa0e0ebda9a9d94108af7b01c042d5a3a5dfe97ac5c2107472`.
The complete build receipt is 24,975 bytes, SHA-256
`94f1f1f13f255a060ebdd4e1153f509f058a7be85a656f898f8bc153a4ee1099`.

Read-only commands and final outcomes:

```text
python -B -m unittest -v test_complete_a00_workflow.py
Ran 5 tests in 61.634s — OK

python -B -m unittest test_digit_place_workflow test_equality_workflow test_exponent_assets test_exponent_workflow test_expressions_workflow test_grouping_workflow test_name_whole_workflow test_qa test_reader_contract test_rounding_assets test_rounding_workflow test_section_exercise_assets test_section_exercise_workflow test_source_portability test_summary_components test_summary_workflow test_unit_workflow test_whole_summary_assets test_write_whole_assets test_write_whole_workflow test_complete_a00_assembly test_complete_a00_workflow
Ran 203 tests in 1153.532s — OK (22 modules)

python -B draft_complete_a00_module.py --check
exit 0

python -B build_complete_a00_module.py --check
exit 0

python -B coverage.py --check
exit 0 — Coverage matches: A00 75 + A10 82; 0 complete, 2 partial,
155 untranslated; all AX-2 module completions pending.

python -B build.py --check
exit 0
```

The exact 20 baseline modules were those tracked at `HEAD` under
`languages/jv-Latn-ID/scripts/test_*.py`; untracked in-progress next-module
asset tests were deliberately excluded. A first global coverage attempt during
concurrent addition/subtraction work encountered their provisional receipts as
unknown draft states. Those lanes preserved the same bytes under
non-discoverable `.in-progress.json` names and did not touch m81243 or coverage;
the final global check above then passed. The transient attempt is not counted
as candidate evidence or as a candidate defect.

Excluding the complete candidate, recursive coverage-hash extraction again
found exactly 299 prior coverage-bound locale files. All stored SHA-256 values
match, and every file is byte-identical to `HEAD` at the review baseline. They
total 13,615,394 bytes and retain path-plus-byte aggregate SHA-256
`074324741651cec0a806ee8d617eda02c56996fb6f2a6302d72ca1ba87e2f642`.
The same two collection references remain external source-repository paths and
were excluded from this locale-file comparison.

Coverage is still `0 complete / 2 partial / 155 untranslated`. The candidate
remains
`complete_source_scope_assembled_and_built_independent_cross_component_review_pending`,
with `independent_cross_component_review: pending`, the exact four-field
unmarked-notice contract, `whole_module_complete: false`, and no effect on
baseline module counts pending review. This is the correct pre-incorporation
state. I did not edit coverage.

## Evidence limits

This rereview supplies automated exact-source, tree, ID, MathML, solution
topology, asset-byte, reader, link, notice, marked-narration, dependency,
mutation, determinism, and prior-product evidence. It does not supply native
Javanese or Indonesian review, educator/register approval, integrated-browser
inspection, keyboard or screen-reader testing, pronunciation/prosody approval,
provider/voice validation, listening review, audio synthesis, publication
approval, or assignment completion.

Existing component reports retain standalone rendered-asset evidence. This
pass verified their bound bytes but did not rerender or visually reinspect all
assets, and it did not establish complete-reader legibility, reflow, zoom,
table navigation, or alt/visible agreement. Source discrepancies documented in
the failed report remain explicit; the repaired notice carries rather than
silently rewrites the unchanged Indonesian source artifacts.

## Reviewed implementation snapshot

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `scripts/draft_complete_a00_module.py` | 7,309 | `4c5200fedf0a23a5be11de3bc87e5b86f53ce9ac4035701e476aa9b49faeb14b` |
| `scripts/complete_a00_checks.py` | 10,112 | `9f372c84ad43fc4ddab7e3501d2960c929a8e000218bd0d6010a4931990b20b3` |
| `scripts/build_complete_a00_module.py` | 9,921 | `282a27351ca99e7064e1c1ba7e13ade23a0309481ddc2adb58debb58b4a1f610` |
| `scripts/test_complete_a00_assembly.py` | 3,092 | `f82e620e96034bd7d1d6da552c70ef1eb670cc50b56b9ef3ee17efb2359c128a` |
| `scripts/test_complete_a00_workflow.py` | 7,882 | `818510911bff0aeaa49de134c934986ce272b8f10d04d71faa81f90e173b9483` |
| `scripts/coverage.py` | 39,648 | `2209773fe0e471fe9728643e79caa7bc795548f3400a95632b00a1886f8af1f1` |
| `coverage.json` | 309,895 | `6104b19dc326bb78e9fa53521c4a5a77ebb94e1c5011fd492b8b58e636e086ea` |

Any later change to these implementations, the pinned receipts/manifests,
complete outputs, assembly, or coverage creates a new snapshot and requires
fresh evidence. This report does not authorize staging, committing, publishing,
or marking the module or assignment complete.
