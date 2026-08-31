# Initial upstream monitoring baseline — 2026-08-31

This is a bounded, read-only comparison with the source pins recorded on 2026-08-30. Default-branch metadata returned at 13:19 UTC; the observation pass closed at 13:25 UTC. Requests were not an atomic snapshot, so active repositories may advance afterward. [UPSTREAMS.json](UPSTREAMS.json) contains the exact commits, release URLs, asset sizes/digests, comparisons, ownership and query limits for 18 repositories.

No worker input was replaced, branch rebased, archive downloaded, source/license audit restarted, issue opened or remote state changed. A newly observed source is a candidate for review, not an instruction to migrate every translation.

## Actionable changes

### A30: a newer partial source release, 67/87 modules

[Precalculus v0.1.0-alpha.67-reader.1](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/tag/v0.1.0-alpha.67-reader.1) was published at **2026-08-31 03:01:19 UTC**, superseding the previously selected alpha.58 reader checkpoint as the newest observed release. Default `main` is `a16de3097f773ee880c75989773776c16cd77868`.

The [committed release manifest](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/blob/a16de3097f773ee880c75989773776c16cd77868/RELEASE_MANIFEST.json) reports 67/87 modules, contiguous through `m49436` (Cramer's rule), with `m49437` (Introduction to Analytic Geometry) next. It explicitly remains an incomplete edition. The canonical English authority remains `789b54099106b071d1d32bfcee454fed72eb4768`.

| Candidate asset | Bytes | GitHub API SHA-256, also matching the owner manifest |
|---|---:|---|
| [Source-core ZIP](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.67-reader.1/precalculus-2e-id-ID-0.1.0-alpha.67-reader.1-source-core.zip) | 74,521,202 | `0ed4c1997c0347ed17fa0ebf36f90a2f7eb321ead608b86285076e9f32334845` |
| [Backend-core ZIP](https://github.com/KokunoYumeto/openstax-precalculus-2e-id/releases/download/v0.1.0-alpha.67-reader.1/precalculus-2e-id-ID-0.1.0-alpha.67-reader.1-backend-core.zip) | 75,074,717 | `d109ee3a1fac0868f000fd86a4f3aea4d77f414f4697f9ca7c2855c5b13e4e4f` |

These are metadata/manifest checks, not independent ZIP CRC, member or byte verification in this pass. The old alpha.58 source asset remains available with the same size and digest as its prior lock. Route the update to Telugu, Indian Bengali, Vietnamese, Marathi and Western Punjabi: compare relevant added modules and existing selected witnesses, then record any deliberate source-pin migration. Do not overwrite their current inputs automatically.

### Program catalog: v0.62.13 plus newer live-source corrections

The catalog is **17 commits ahead** of prior pin `2f0e52280791854f904475e5f92392f52745ea24`, at live `main` commit `c9e4599866af2593799403c4a8ee6d616dbf5605`. The [published v0.62.13 release](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.13) was sealed at `4ab6eb6b270dc0a32512dad3f998653c336d8492`, published **2026-08-31 11:31:58 UTC**, with 100 returned assets. Its [source ZIP](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.62.13/program-matematika-indonesia-source-v0.62.13.zip) is 346,471,427 bytes, API SHA-256 `f4e20b66d773177908d704559600c2695a6a066678537357c345c07d5a837365`.

The [post-release correction note at live source](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/c9e4599866af2593799403c4a8ee6d616dbf5605/backend/course-capsule-v1/POST_RELEASE_CORRECTIONS_20260831.md) explicitly distinguishes that immutable archive from newer fixes. Those fixes preserve server-rendered course links during loading/filter failures, align summary counts with capsule data, classify unindexed capabilities as **unknown** rather than absent, distinguish partial resources from whole-course editions, and correct public routing/evidence labels. It also states remaining keyboard-validation and native-backend replay limits. Do not claim the published v0.62.13 ZIP contains this subsequent commit.

The new [modular-backend method and findings](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/c9e4599866af2593799403c4a8ee6d616dbf5605/MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md) are relevant to all nine translation workflows. They favor a small identity/provenance-bound common layer over preserved course-native backends, structured exercise components, explicit absent solutions, and readable learner surfaces. They distinguish historical comparison results from subsequent implementations. This monitor read relevant committed text; it did **not** rerun the producer's audits, adapter builds or learning-quality checks.

### A00: additive assessment capability, not a new textbook edition

The catalog now publishes a [contract-2.3.1 A00/O001 assessment adapter](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.62.13/program-matematika-indonesia-backend-v2.3.1-a00-o001-assessment-adapter-v0.1.0.zip): **8,634,922 bytes**, API SHA-256 `43e122a96cf2878764ff53148c9d2d247ccb0b661b563ae6c5f04f4cd000098b`.

Its [committed capability manifest](https://github.com/KokunoYumeto/program-matematika-indonesia/blob/c9e4599866af2593799403c4a8ee6d616dbf5605/backend/v2.3/extensions/a00-o001-assessments-v0.1.0/assessment-capability-v0.1.0.json) reports 75 modules, 8,105 assessments, 13,345 statement/solution components, 2,865 explicit solution gaps and 21,450 exact HTML-anchor routes. These are **producer-reported capability counts**, not independently recomputed here. The method specifies joining on **`(module, native_id)`**, because fragment identifiers recur across modules, and does not invent missing solutions or promote assessment components into curriculum units.

This is relevant to A00 diagnostics and original companion work in Bangladesh Bangla, Telugu, Indian Bengali, Tamil, Javanese and Gujarati. Preserve each lane's native content/provenance and distinguish translated supplied solutions from newly authored answers. Evaluating the adapter is optional scoped integration work, not a prerequisite that should stop current drafting.

The published [B10 adapter v0.2.0](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/v0.62.13/program-matematika-indonesia-backend-v2.3.1-b10-adapter-v0.2.0.zip) is also recorded: 656,874 bytes, API SHA-256 `c9a2f8a0307ec6fa6c5f3b03168760f0d8ed5a67e069b5afb592f905e12096b6`. This baseline does not establish that this adapter first appeared after the prior pin. Current method text distinguishes a verified course route from a reader actually consuming central adapter tables; only A00 is claimed there as directly consuming adapter-derived mappings.

## Allocation research: no new priority finding observed

The research repository's default `main` remains the already known handoff base **`975a3435f611792ef30a0908e0ba54b23a0e229a`**. [Comparison with the initial research pin](https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access/compare/2c9c129c3e693bec5a0e387c76b1c270fccf399c...975a3435f611792ef30a0908e0ba54b23a0e229a) shows exactly one commit adding `index.html`; it does not modify the existing paper/data source files. Release v1.0.0 remains the newest observed research release.

The complete returned branch list contained `main` and the existing coordinator-only handoff branch. There were **zero pull requests and zero issues**, with no further pages indicated. The handoff branch is coordination work, not evidence of changed language rankings. This observation does not claim that ongoing unpublished research elsewhere is complete or unchanged.

## Other source status

| Source | Newest observed publication / source state | Comparison with previous pin |
|---|---|---|
| A00 | `prealgebra-2e-id-ID-v0.2.7` | Default head and pinned source ZIP size/digest unchanged. Central assessment work above is separate. |
| A10 | `v1.0.2` | Default head and pinned source ZIP size/digest unchanged. |
| A20 | `v0.3.0-wip` | Default head and editable-source ZIP size/digest unchanged. Keep the release-asset-versus-old-checkout distinction and existing figure corrections. |
| A30 | `v0.1.0-alpha.67-reader.1` | New candidate release; old alpha.58 asset remains unchanged. |
| B10 Indonesian | `backend-v1` | Default head unchanged at `e94905932301e699b7c4d44e88ec54e972b886b6`. |
| B20 Indonesian | `v2026.08.14.1` | Default head unchanged at `59aaa2a6145eecd67680752c28ad4be7e43eff5e`. |
| B40 Indonesian | `v2026.08.22` | Default head unchanged at `e84ce2956a7304830c42eba70106f940fefee7c4`. |
| B60 Indonesian | No GitHub releases returned; embedded source/backend ZIP | Head unchanged at `3abfd2deb01e8ea005da8450ac3a2228410468d9`. Public checksum and 35,496,581-byte asset metadata agree with the prior lock; ZIP bytes were not downloaded. |
| B80 Indonesian | `v2026.08.22.1` | Default head unchanged at `403e93a6d8bdadbcd42385981bbe4b39577ca069`. |
| Open Logic Indonesian | `id-olp-0722-20260814` | Initial monitor pin `07b25e1329a95a0ace266533f32f3671c2cef95e`; no earlier exact pin in the compared handoff index. Not substituted for B10. |

Canonical English OpenStax A00/A10/A20 and A30, CLP-1, CLP-4 and Hefferon default heads all match their prior source locks. Exact refs and primary endpoints are in the registry.

One exception is [Discrete Mathematics upstream](https://github.com/oscarlevin/discrete-book): default `main` is `730e5e3b96094148818603041222df6f3d1d96ba`, whereas the Indonesian/translation witness is pinned to `82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799`. GitHub reports the comparison as **diverged: 23 ahead, 1 behind**, not a simple fast-forward. Those reported commits predate the 2026-08-30 baseline, so this is a historical edition/pin difference newly recorded by the monitor, not proof of an overnight update. The returned changed-file list reached the API's 300-file bound. Keep the selected edition pinned and review only relevant corrections when those units are translated.

## Monitoring boundary and next run

- The coordinator owns routing these findings; the language owner records any adoption, rejection or deferral. This monitoring pass did not send instructions to workers.
- Track research changes, published release identity changes and live-source backend changes separately. A tag with a changed digest must not silently replace the old asset identity.
- Reuse this registry as the next comparison baseline while preserving the workers' independent source locks. Do not confuse a monitoring pin with an adopted translation source.
- Indonesian release queries were limited to the first three entries, including prereleases but excluding drafts from the publishable baseline. Canonical-English release feeds were not exhaustively checked. No rate-limit error occurred; differing endpoint counters are recorded without treating them as cumulative accounting.
- AX-1/2/3 and MV-1/SB-1 remain program/crosswalk references. This pass does not invent separate repository mappings, claim public replay of every backend, or wait for all upstream production to finish.
