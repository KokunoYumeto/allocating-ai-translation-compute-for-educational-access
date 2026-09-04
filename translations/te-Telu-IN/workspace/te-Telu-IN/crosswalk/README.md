# Source-to-product crosswalk

All selected source-order modules are mapped, including front matter and material
beyond the Grades 3–10 core. These are editorial bridge lanes, **not** claims of
official AP/TS grade equivalence or full Telugu coverage.

| Program | Acquired canonical text | Indonesian reference | Telugu product lane |
|---|---|---|---|
| A00 | 75 collection modules | v0.2.7, 75/75 | Number sense → operations → fractions/decimals/percent → ratios, measurement and elementary equations. TE-B001–B010 cover allm81243sourceparts across checkedfragments; m81244addition is inproduction. EarlierPreface/Introduction remainpending. |
| A10 | 82 collection modules | v1.0.2, 82/82 | Arithmetic-to-symbol transition; equations, inequalities, graphs, systems, exponents, polynomials, factoring, rational expressions and roots. |
| A20 | 83 collection modules | v0.3.0-wip, 48/83 | Algebra consolidation, functions and quadratic/rational models. Complex numbers and advanced portions are optional later extensions, not assumed Grade 10 requirements. |
| A30 | 87 collection modules | alpha.58-reader.1, 58/87 | Functions and trigonometry extension after A20. Higher precalculus content stays in the source map without being called a Grades 3–10 entitlement. |
| B10 | 119 owner-frozen inclusion resources | Complete DMOI4 source checkout | Proof/discrete reasoning after A30: introduction, logic/proofs, graph theory, counting, sequences, discrete structures and further topics. Source closure includes exercises and support resources, not 119 equivalent lessons. |

`A00-modules.tsv` through `A30-modules.tsv` preserve every collection-order module,
chapter, title, English hash, Indonesian file or explicit missing-prefix marker,
and Telugu status. `B10-source-closure.tsv` follows the owner's exact depth-first
include manifest, with canonical paths, hashes, XML IDs and matched target files.
The 327 OpenStax modules plus 119 B10 resources are not interchangeable units.
Unit-level editorial status is recorded in `../units.json`; partial module rows
must never be interpreted as whole-module completion.

Dependency spine: A00 → A10 → A20 → A30 → B10. Within A00, remediation is
skill-based rather than age-based. Source order remains visible even when a bridge
uses a diagnostic preview of a later prerequisite. TE-B001's K4 preview does not
mark the next place-value subsection translated.

Open Logic is a supplemental acquisition from the dispatch reference list. It is
not the catalog's B10 corpus; no Open Logic material is translated in this pilot.

The two OpenStax English Git checkouts **remain sparse** and omit bulk `media/`
and `cover/` after network resets. Separately, complete pinned ZIP archives are
local under `downloads/canonical-archives/`: the prealgebra bundle contains all
13,738 Git blobs at `38cae454e644abf9f0a623e876994553881597c9`; the college-algebra
bundle contains all 3,202 at `789b54099106b071d1d32bfcee454fed72eb4768`.
Every archived file, including media and cover files, matches its pinned Git blob
hash and passes ZIP CRC validation. These complete archives have **not** been
extracted; their presence does not make either sparse checkout a full checkout.
Exact URLs, byte counts, SHA-256 hashes, trees and acquisition provenance are in
`sources.lock.json` under `canonical_archives`. The prealgebra archive was copied
from the Marathi task's existing pinned download before the storage alert; the
college-algebra archive was downloaded directly from the pinned codeload URL.

Read-only reproduction (no downloads, extraction, or corpus writes):

```powershell
python te-Telu-IN/scripts/seal_archives.py --verify
python te-Telu-IN/scripts/freeze_sources.py --verify
```

The default freeze operation also never extracts releases: it requires and
stream-verifies the existing materialized release files before writing the small
reviewable records. Missing or mismatched materialization is a hard failure, not
an instruction to repeat a large extraction. Untranslated modules and non-admitted
Indonesian images remain explicit; archive completeness is not translation or
publication completeness.
