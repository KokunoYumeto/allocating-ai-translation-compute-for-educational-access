# m81295 `fs-id2471378` Divide peer review

**Disposition: CLOSED–PASS**

Date: 2026-09-02 (Europe/Amsterdam)  
Review class: independent model peer review of the complete Divide Decimals source block. This closes only `m81295` / `fs-id2471378`; it is not a publication, release, human-language approval, or assistive-technology approval.

## Final byte binding

| Artifact | SHA-256 |
|---|---|
| Frozen source module, `provenance/modules/m81295.source.cnxml` | `c22d14bb2b833ed20ea5a7aa95d0e50b7810e8930834bd61993b8431dcfd02c3` |
| Exact source subtree, SHA-256 of ElementTree UTF-8 serialization | `5fda597d153f9a78da39ac2063194a7dc584bb719afdb463ad1bfe4cebe46192` |
| Translation overlay | `297ede5c51bd1449b440fa6c462faf03386fbdcb0c1ee52c23716e9757c69602` |
| Generated section CNXML | `99abbfaff845f2062decc975e85817f002328e997f9cdf458f62c18faab2dddd` |
| Generated translated subtree, same serialization method | `f519a4eb7543676d2e0bc76f5eb20ca73ae6fee018fe3a6e9e2218241b840688` |
| Section reader HTML | `a3c3d6b6e8f99ca9d92950cdee534826aabfe59661cbadc3578d5be774f4cfb3` |
| Section QA receipt | `e4b308bd2a0326ed15ae76f8a883ea1a818983f7bc1dcf39e14d5ae9878ad1d5` |
| Section canon receipt | `550bd034fd7d772566a82bd54867c4fa2ce78bd5af7010c40d721b97c7bc3d50` |
| Section Chrome receipt | `abc3e8461f20d0590364bc01076b20884d1194249d6fe11417c3e969a275e81e` |
| `scripts/build.py` | `c4da8b071ff7e690ff8b530625ea3b33c53091631740cf1fa7e86977cb766451` |
| `scripts/build_sections.py` | `9448f28a30578e8ad9333d9580afcc8d99ea0a9df7fddfb3503030874f3e349d` |

The Chrome receipt's `input_sha256` is the reader hash above. Its 15 listed PNGs all exist. A deterministic manifest made by sorting them in receipt order and hashing lines of `name<TAB>sha256<TAB>bytes<LF>` is `3806e65aee7a9b9398c16f7ce73e28b88f681dd23e1c5b8e631e353200947d90`.

## Recurring canon consultation

The consultation was real and repeated before review, during the prose/arithmetic audit, and again immediately before final QA. At each stage I read OCR and inspected the actual rendered page image, rather than relying on ledger summaries.

- Tripura VI p.57: OCR `6a094d3c1d9f4001ef4f8b6f046ac87dc64956df181cfdb17ad6d58b1c73b6a0`; image `7e9e25e29ee2ab73f7306f2c114fb26f601085512a6cd4893b350dcf79e87e2d`. It supports `দশমিক সংখ্যা`, the decimal mark, `লব`/`হর`, and the explicit restriction `b ≠ 0`. The visibly incorrect 12.74 place-value row was excluded.
- Tripura VI p.58: OCR `ddd30a1e805d0f7b396a7adeb2bc0664e50764127c1c5d1c8171da948b120ac1`; image `246558790d2b90acaf4f266cc5da4a77fc85a82b5671903303337747adb53596`. It confirms digit-by-digit decimal reading and retaining spoken zeroes.
- Tripura VI p.50: OCR `8a8e70cfbe0533bec8b8cca32dceee07e4b8803bb842a7c74596dd96f002a2b6`; image `21aa1109491a09aeb6308ff2804af6e00eaf30a124edd19ba87b60107c5034df`. It directly witnesses `ভাগফল` and `ভাজক` in the mixed-fraction formula.
- West Bengal Class 7 Learning Bridge p.181: OCR `46a57a33d703368f69e2b6d0a70883970378ec941ac957ae5fe799c924a55972`; image `433b657f20d8367e5ccf9441383170140ff224a1bc942a4154cd04c91de9bb84`. It confirms dividing both terms by the same nonzero number and explicitly distinguishes `লব` and `হর`.

The final pre-QA reread required no further prose change. `ভাজ্য` and `দীর্ঘ ভাগের পদ্ধতি` remain disclosed editorial forms without a direct local lexical witness; their referents are explicit, and independent West Bengal teacher/language review remains pending.

## Structural and language audit

Running the final overlay through `build.translated(...)` passed its exact tag-order, ID-order, nonlinguistic-attribute, reversible linguistic-`mtext`, MathML-signature, and English-prose assertions. I independently compared that generated target with the generated CNXML subtree; they are recursively identical after XML's equivalent `None`/empty-text normalization.

- 576 CNXML nodes; 137 unique preserved IDs; 54 MathML roots.
- 5 examples; 15 exercises; 15 solutions.
- 14 image occurrences, representing 13 unique source rasters.
- Zero unallowlisted English-prose matches under the `[A-Za-z]{3,}` gate outside MathML and the exact retained-credit exceptions.
- All 25 boundaries where a MathML child ends in `.`, `,`, `;`, `:`, `?`, or `!` were reread with their Bengali tails: zero doubled or conflicting punctuation.

I reread the five corrected paragraphs in final CNXML and reader context: `fs-id1795974`, `fs-id1884116`, `fs-id4153116`, `fs-id1374903`, and `fs-id3366685`. In particular, `fs-id4153116` now reads coherently as `... উত্তরও হয় 4, কারণ এখানে ভাজ্য পূর্ণসংখ্যা 8 এবং ভাজক পূর্ণসংখ্যা 2, তাই ...`. I also reread intentionally unchanged `fs-id2364168`; its generated link label supplies the antecedent that makes the following `-এ` grammatical.

## Arithmetic and domain audit

All 15 source-supplied answers were recomputed with exact rational arithmetic and checked against their matching exercise/solution IDs:

| # | Identity checked | Result |
|---:|---|---:|
| 1 | `0.12 ÷ 3` | `0.04` |
| 2 | `0.28 ÷ 4` | `0.07` |
| 3 | `0.56 ÷ 7` | `0.08` |
| 4 | `3.99 ÷ 24 = 133/800 = 0.16625` | `$0.17` |
| 5 | `6.99 ÷ 36 = 233/1200 = 0.194166…` | `$0.19` |
| 6 | `4.99 ÷ 12 = 499/1200 = 0.415833…` | `$0.42` |
| 7 | `−2.89 ÷ 3.4` | `−0.85` |
| 8 | `−1.989 ÷ 5.1` | `−0.39` |
| 9 | `−2.04 ÷ 5.1` | `−0.4` |
| 10 | `−25.65 ÷ (−0.06)` | `427.5` |
| 11 | `−23.492 ÷ (−0.04)` | `587.3` |
| 12 | `−4.11 ÷ (−0.12)` | `34.25` |
| 13 | `4 ÷ 0.05` | `80` |
| 14 | `6 ÷ 0.03` | `200` |
| 15 | `7 ÷ 0.02` | `350` |

The three currency answers use nearest-cent, half-up rounding and are correct. All 15 numeric divisors are nonzero; the other worked numeric divisors are also nonzero, and the general symbolic divisor/denominator is explicitly scoped as `অশূন্য ভাজক` / `অশূন্য হর`.

## Image, accessibility-text, and errata audit

I inspected the pixels of all 13 unique rasters and checked all 14 occurrences against the frozen media receipt: byte length, SHA-256, and pinned Git blob all match. Every one of the 14 enclosing media elements has a nonempty Bengali alternative, and the Chrome receipt confirms all 14 rendered images loaded with alternatives at both widths.

The unique raster SHA-256 values are:

- `05_02_001` `57e125f09fdaeab7d0c908d3e6eea9024258dc79a050e9ca332bcee3d7fe1a94`; `05_02_004` `869f20c830a67b98f82dfaa5a2efd829492b8bbdde72805a7c2992d90c84aef6`.
- `024-01` `df7232ad216c2106d8ad65304e82df703494b7da5b3f69d988d6921e7277a69e`; `024-02` `82048e2e68111b5e8c741851210a79f3877ac45793ccf4ef56e165bbd9c3f0c4`.
- `025-01` `d7061fd8dbce5114cc0d2cf12b8e994a7a89945a6117edc2452259a3d59d8c92`; `025-02` `74dc1e12b98eb4c74a7bf30f4578e8b1459e1cadc17311e682301153b0cdc9e5`.
- `026` `c30fadd562912d22cac1d7e2a6bc8af2e44064bab615d5f8070895f185bdbc78`.
- `027-01` `f9319a71cdbeee1d8449f2d8a6acb35f78352b561957f21a85cad5cd4c5921e9`; `027-02` `35a9cd13be962a0f978ced04d2f3593d2c4ac1e5a1b567774a1ca46148637f07`.
- `028-01` `2694ac1eabf26d913fafa2ca0c1572249ffa1e70b092e7185f100ec2aab24635`; `028-02` `02d84692ac5f33c50b13d50db352a53f880fafb263aa653373dfe4fbcc7a11e7`.
- `029-01` `f219a3771d68301f626d849c60b8792262fe9083f5ebf71c18b1ffcc093a7839`; `029-02` `3b5515257d9e254394691f86f9f26cdd61d66f4661d2050cf5880875ada82e24`.

Known-source finding dispositions are correct and bounded: the Bengali money-table ARIA text restores `$3.99` and the two `≈` relations; the 024/025 alternatives place the marker over the visible decimal point; the 026 alternative identifies `a` as dividend rather than the source typo “divided”; and the nonzero-divisor scope is made explicit. Raster pixels, source MathML, operations, IDs, and structure are unchanged.

## Chrome visual QA

The owning lane generated the final, hash-bound evidence with the repository's isolated Chrome + Playwright harness (`C:/Program Files/Google/Chrome/Application/chrome.exe`, no external requests). This reviewer did **not** launch Chrome: the browser-client surface was unavailable, so I independently inspected every owner-generated capture named in the final receipt.

- 1200 px: 13/13 desktop tiles inspected; document height 11,693 px; `scrollWidth = width = 1200`; 14/14 images loaded with alt; 54/54 MathML roots rendered; Bengali font detected; zero overflow and zero browser errors.
- 390 px: both narrow endpoint captures inspected; document height 15,540 px; `scrollWidth = width = 390`; 14/14 images loaded with alt; 54/54 MathML roots rendered; Bengali font detected; zero overflow and zero browser errors.
- The complete desktop sequence is readable and continuous. The narrow endpoints, automated element metrics, and exact width equality show no horizontal clipping. No capture shows overlap, clipped prose, broken Bengali shaping, unreadable math, missing raster, or footer failure.

## Finding dispositions

- `fs-id4153116` duplicate/clumsy clause-boundary punctuation: reported to the owner, fixed in the overlay, rebuilt, visually reread, and closed.
- Canon verification initially carried pre-fix artifact hashes: reported to the owner; all five artifact fields now bind the final bytes, including browser receipt `abc3e846…`; closed.
- `fs-id2364168`: investigated and retained unchanged because the generated link label makes the `-এ` tail grammatical; closed with no edit.
- Four declared source/accessibility errata groups: corrections match pixels/math and do not alter source structure; closed as documented transformations.
- Independent West Bengal teacher/language, learner, and assistive-technology review remains pending and is not represented as completed.

No open section-level blocker remains. **CLOSED–PASS.**
