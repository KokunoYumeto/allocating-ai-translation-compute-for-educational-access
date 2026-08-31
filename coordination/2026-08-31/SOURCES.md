# Pinned sources and assignment reference

Consolidated 2026-08-31 from the existing 2026-08-30 source-update record and language acquisition locks. This is a portable source index, not a new release, source, or license audit. Versions below were observed on 2026-08-30; they are not asserted to remain the latest after that date. No source archives or media are bundled here.

## Authority and assignments

The [allocation report at its recorded commit](https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/tree/2c9c129c3e693bec5a0e387c76b1c270fccf399c) is v1.0.0. The existing update check recorded no Top-10 rank changes. The [Indonesian program catalog at its recorded commit](https://github.com/KokunoYumeto/program-matematika-indonesia/tree/2f0e52280791854f904475e5f92392f52745ea24) is v0.62.11; that update affected D110, not the materials assigned below.

These are source assignments, not claims of completed translation, acquisition, review, or publication. Indonesian rank 1 is outside this handoff.

| Rank | Target | Assigned program material |
|---:|---|---|
| 2 | Bangladesh Bangla `bn-Beng-BD` | A00, selected A10, AX-1, AX-3 |
| 3 | Telugu `te-Telu-IN` | A00–A30, then B10 reasoning |
| 4 | Indian Bengali `bn-Beng-IN` | A00–A20, selected A30, AX-3 |
| 5 | Vietnamese `vi-Latn-VN` | A30, B20, B40, B60, B80, MV-1/SB-1 crosswalk |
| 6 | Marathi `mr-Deva-IN` | A20, A30, B10, B20, B40 |
| 7 | Indian Tamil `ta-Taml-IN` | A00–A20, AX-1, AX-3 |
| 8 | Western Punjabi `pnb-Arab-PK` | A10–A30, B10, B40 |
| 9 | Javanese `jv-Latn-ID` | A00, A10, AX-2 audio/TTS layer |
| 10 | Gujarati `gu-Gujr-IN` | A00, A10, AX-1, AX-3 |

## Indonesian A00–A30 release freeze

Coverage is the source owner's admitted-module count, corroborated by the existing release/acquisition records. It is not an independent whole-book correctness judgment and says nothing about completion of the nine target-language products.

| Material | Pinned release | Recorded coverage | Repository commit observed in the update check |
|---|---|---|---|
| A00 Prealgebra | [prealgebra-2e-id-ID-v0.2.7](https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID/releases/tag/prealgebra-2e-id-ID-v0.2.7) | 75/75 | `3de9207f56f8b5c57c017abf973fb04e00d740f1` |
| A10 Elementary Algebra | [v1.0.2](https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/tag/v1.0.2) | 82/82 | `11754719d8eab8de63d5340ad35824e8be8d99e4` |
| A20 Intermediate Algebra | [v0.3.0-wip](https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/tag/v0.3.0-wip) | 48/83, through Chapter 7 | `b293e167477c8fe2e8885c6f6d79d12cbb2e0e89` |
| A30 Precalculus | [v0.1.0-alpha.58-reader.1](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/tag/v0.1.0-alpha.58-reader.1) | 58/87 | `3209a5a2dea18c2fc527c5ea41b7dd2195076e40` |

Important distinctions from the existing update check:

- A10's central catalog overlay still pointed to 1.0.0; the selected release is corrected 1.0.2.
- A20's recorded main/tag checkout has an older README/tree. Use the **editable-source release asset**, whose recorded coverage is 48/83, rather than substituting that checkout or an older 28/83 or 41/83 snapshot.
- A30's central overlay still pointed to alpha.49. The selected source-core asset is alpha.58-reader.1 and remains a partial edition.
- A20 and A30 are prereleases. An exact-tag URL is the reference; a failure of `/releases/latest` does not establish that no release exists.
- A repository commit and a packaged derivative commit are different provenance fields. For example, the [A00 release manifest](https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID/releases/download/prealgebra-2e-id-ID-v0.2.7/prealgebra-2e-id-ID-v0.2.7-release-manifest.json) records derivative commit `0a29778fcd4daa5f7a23c7cbf313fe755b8c24e6`; do not relabel the observed repository commit as that packaged derivative.

### Exact release assets

The 2026-08-30 Indian Bengali acquisition lock records observed and expected SHA-256 equality and passing ZIP CRC checks for all four assets. Its checksum authority is the release asset digest and retained release checksum files observed on that date. Marathi's separate acquisition lock also records SHA-256 and full ZIP CRC passes for A20 and A30. These are retained acquisition results, not checks rerun during this consolidation.

The coordinator additionally recorded an independent fresh A00 size/SHA-256 match on 2026-08-30. That complete-archive verification supersedes the earlier report of only a partial A00 download.

| Material / downloadable asset | Bytes | SHA-256 |
|---|---:|---|
| [A00: prealgebra-2e-id-ID-v0.2.7-source.zip](https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID/releases/download/prealgebra-2e-id-ID-v0.2.7/prealgebra-2e-id-ID-v0.2.7-source.zip) | 79,438,504 | `ec622c4b0be5693a798453ee6d1a6ae21cdf978f26852253b5cbb5d88a484fee` |
| [A10: elementary-algebra-2e-id-ID-1.0.2-source.zip](https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/elementary-algebra-2e-id-ID-1.0.2-source.zip) | 6,397,865 | `6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456` |
| [A20: openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip](https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.3.0-wip/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip) | 106,658,915 | `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7` |
| [A30: precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.58-reader.1/precalculus-2e-id-ID-0.1.0-alpha.58-reader.1-source-core.zip) | 69,355,910 | `9f8ba5e44bd4d4794c559de85a5449f3b4bd279d153801b94f3d39a471f5a0ca` |

The matching publisher checksum documents are [A00 SHA256SUMS](https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID/releases/download/prealgebra-2e-id-ID-v0.2.7/SHA256SUMS.txt), [A10 SHA256SUMS](https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id/releases/download/v1.0.2/SHA256SUMS.txt), [A20 SHA256SUMS](https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.3.0-wip/SHA256SUMS.txt), and [A30 SHA256SUMS](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.58-reader.1/SHA256SUMS.txt). The companion manifests remain on those exact release pages. Consult them without treating this handoff as a replacement source/license audit.

## Canonical English OpenStax witnesses

These pinned English sources provide the original mathematical/visual witnesses used alongside the Indonesian editions. They are distinct from target-language canon examples consulted for terminology and pedagogy.

| Assigned material | Canonical repository / pinned commit | Recorded archive bytes | Observed archive SHA-256 |
|---|---|---:|---|
| A00, A10, A20 | [osbooks-prealgebra-bundle](https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9), `38cae454e644abf9f0a623e876994553881597c9` | 537,455,794 | `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917` |
| A30 | [osbooks-college-algebra-bundle](https://github.com/openstax/osbooks-college-algebra-bundle/tree/789b54099106b071d1d32bfcee454fed72eb4768), `789b54099106b071d1d32bfcee454fed72eb4768` | 167,391,934 | `2fdf5495f5f11dbe3c8f6d4705a257a2ed7f13db1968cc6b2be409e0202a94f9` |

Archive endpoints: [A00/A10/A20 pinned ZIP](https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/38cae454e644abf9f0a623e876994553881597c9) and [A30 pinned ZIP](https://codeload.github.com/openstax/osbooks-college-algebra-bundle/zip/789b54099106b071d1d32bfcee454fed72eb4768). Existing language acquisition records report full ZIP CRC passes. This handoff treats the canonical ZIP hashes as **observed archive identities**, not independently established publisher-issued checksum assertions. The commit is the upstream source pin; a differently packaged download requires its own identity check.

Clean Git status and tracked-file counts did not prove complete offline availability: a previously shared sparse/promisor checkout lacked many physical media files. Reuse a verified complete archive where available, and verify that selected module and image members actually exist. Do not infer complete media from a text-only checkout. No second-PC download or extraction is asserted here.

The narrowly verified A20 figure discrepancies and exact selected-member hashes are in [SOURCE_CORRECTIONS.md](SOURCE_CORRECTIONS.md).

## Other existing program references

The existing Marathi source lock records the following additional assignment pins. They are copied as provenance references, not independently refreshed or completeness-certified in this consolidation.

| Program material | Indonesian source | Canonical source |
|---|---|---|
| B10 | [Discrete Mathematics: An Open Introduction Indonesian](https://github.com/KokunoYumeto/discrete-mathematics-open-introduction-id/tree/e94905932301e699b7c4d44e88ec54e972b886b6), `e94905932301e699b7c4d44e88ec54e972b886b6` | [oscarlevin/discrete-book](https://github.com/oscarlevin/discrete-book/tree/82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799), `82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799` |
| B20 | [CLP-1 Indonesian](https://github.com/KokunoYumeto/clp1-differential-calculus-id/tree/59aaa2a6145eecd67680752c28ad4be7e43eff5e), `59aaa2a6145eecd67680752c28ad4be7e43eff5e` | [arechnitzer/CLP1](https://github.com/arechnitzer/CLP1/tree/9f0295936d395bec68dab7915057135a2c7f0414), `9f0295936d395bec68dab7915057135a2c7f0414` |
| B40 | [Hefferon Linear Algebra Indonesian](https://github.com/KokunoYumeto/hefferon-linear-algebra-id/tree/e84ce2956a7304830c42eba70106f940fefee7c4), `e84ce2956a7304830c42eba70106f940fefee7c4` | [Jim Hefferon's Linear Algebra](https://gitlab.com/jim.hefferon/linear-algebra/-/tree/df2262e089a02651c127f1dd12649c4622ee1383), `df2262e089a02651c127f1dd12649c4622ee1383` |

[Open Logic Indonesian](https://github.com/KokunoYumeto/OpenLogic-id) is also an existing dispatch starting point; it is not substituted for the B10 source pinned above. For B60, B80, AX-1/2/3 and MV-1/SB-1 definitions, retain the [pinned program catalog](https://github.com/KokunoYumeto/program-matematika-indonesia/tree/2f0e52280791854f904475e5f92392f52745ea24) and each language's actual source lock as the assignment references. This index does not invent unverified repository mappings or declare those materials acquired.
