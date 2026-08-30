# Indonesian program compute and page reconciliation

## Scope

This public note reconciles three nonadditive compute counters and four different
page universes. It prevents cached, gross, fresh, and output tokens from being
conflated, and prevents a rendered-page inventory from being called a final
translated-page count.

## Compute views

### 1. Thirty-three user-visible roots

The boundary is the central manager plus the 32 owner roots in registry 152, with
root events from 2026-08-20T10:40:19Z through 2026-08-29T23:33:38.559Z.

| Field | Exact tokens | Treatment |
|---|---:|---|
| Gross input | 83,386,749,267 | Cached plus fresh plus cache-write input |
| Cached input | 81,480,422,656 | 97.713873% of gross input |
| Fresh/uncached input | 1,906,326,611 | 2.286127% of gross input |
| Cache-write input | 0 | Exact reported field at this boundary |
| Output | 251,883,504 | Includes 70,812,538 reasoning-output tokens |
| Reasoning output | 70,812,538 | Subset of output; never added again |
| Total | 83,638,632,771 | Gross input plus output |
| Fresh input plus output | 2,158,210,115 | Derived comparison only; 2.580399% of total |

All 33 final rollout totals matched the corresponding database counters; mismatch
count was zero.

### 2. Descendant-inclusive closure

The recursive spawn-edge closure contains 6,726 task records and an exact cumulative
total-token counter of 10,253,232,856,362 through 2026-08-29T23:34:32Z. The
sanitized audit receipt proves that this closure begins with and already contains the
33 roots. It is the inclusive total and must never be added to the root subtotal. It
may only be compared with that subtotal; no descendant-exclusive total is asserted.

Historical cached/fresh/cache-write/output/reasoning splits and the full request count
are unavailable for the closure. A bounded final-rollout scan found 7,970 distinct
cumulative-token progressions. That is a lower bound, not a complete request count.

### 3. Nine counter-backed pursuit phases

The task-goal audit records 88,493,496 pursuit-accounting tokens over nine
nonoverlapping phases: 87,035,193 for edition production, translation, mathematical
and terminological QA, build, and publication; and 1,458,303 for separately
identified deployment, maintenance, and durable-state support. This narrow workflow
attribution is neither the program total nor additive with either boundary above.

The pursuit implementation uses fresh input plus output and rolls descendant-agent
usage into the root pursuit. It cannot reconstruct gross input or API cost.

### Boundary exclusions

The 33-root measurement begins on 2026-08-20. Earlier Open Logic production is
excluded because registry 152 does not map it to a canonical task ID. Auxiliary
audit and research tasks outside the 33 selected roots are excluded. Requests without
surviving counters are also excluded. Consequently, none of the three views is a
complete historical invoice or a weekly-plan consumption figure.

## Page views

The central page ledger explicitly states that the full 40-course curriculum has no
final Indonesian page total.

| Page universe | Exact pages | Meaning |
|---|---:|---|
| Measured teaching package | 19,745 | Frozen/current upstream or source-native PDF pages |
| Selected-corpus working pages | 20,763 | Adds admitted stable or older working witnesses; not final Indonesian pagination |
| Documented rendered universe | 27,705 | 19,745 teaching-package + 306 donor + 7,654 Stacks reference pages |
| Public-artifact reconstruction | 26,031 | De-duplicated rendered public course/checkpoint PDF pages at a pinned public commit |

"About 25,000 pages" is therefore only an order-of-magnitude statement about the
documented rendered/corpus scale. It is not a certified final translated-page count.

## Reproducibility artifacts

- `compute_token_audit_33_roots_20260830.json` - 6,620 bytes - SHA-256
  `1dafeac9eb161204df470d247811f4e29415ee8ab3a297e412dbdd619cc0911c`.
- `INDONESIAN_TASK_TOKEN_AUDIT_20260830.md` - 9,863 bytes - SHA-256
  `6ea38c1684e3d2c9c1420dce1c67a90dccdbf6217d9503f2fa7d957cb87e5108`.
- `INDONESIAN_PUBLIC_PROGRAM_AUDIT_20260830.md` - 20,920 bytes - SHA-256
  `5c34c78e6e9bef9e7b75e9179dd31cde98995d70ceff7ddd82da98ecbfbb6e0d`.
- Registry 152 - 23,836 bytes - SHA-256
  `2c34301e5e77065336c5079b8787e15103bf97abe5458f71db92dfbda684ef2d`.
- Central page ledger - 18,639 bytes - SHA-256
  `254d8213bc217aacec088026ca05ea7b42bf94617aa941f6305c635cc352c194`.

The public package excludes private local witness paths and credentials. Public
repository, release, DOI, and artifact identities remain in the cited audit files.
