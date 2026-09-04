# MR-BRIDGE-014 independent source/mathematics review

2026-08-31. **PASS after one source-attribution correction by root.** Source-only mathematical/translation review readiness, not acceptance of an HTML or PDF reader. All19 tests pass with zero skips against the final frozen/built inputs below. The reviewer owned only this note and `tools/test_unit14_math.py`; no XML/config/asset edits, downloads, extraction, builds, browser operations, alternate HTML inspection, PDF creation, commits or publication.

## Independently read evidence and scope

Read the complete EN and Indonesian section `A20:m81374#fs-id1167836386547` from the pinned ZIPs in memory, using bounded untruncated CNXML reads. This included all prose, 58 MathML trees, six problem/solution pairs, all media descriptions and the resource note. Read the actual target XML in bounded parts, its config, and the author's drafting note as clues, not proof. Independently checked the surrounding tree: `fs-id1167836522816` precedes this section; `fs-id1167836597228` **Key Concepts** follows it. The 12 direct non-title source children, all54 contained IDs plus the section wrapper (55 source IDs), their complete preorder and ancestor relationships are preserved. Target has57 unique IDs including article and credits. Classification: five prose blocks, two worked examples, four source practices, one resource note, no new formal definition or original question.

Actual module pins verified by reading bytes:

| Locale | Archive and member | Module SHA-256 |
|---|---|---|
| EN | `downloads/mr-Deva-IN/releases/A20-canonical.zip` → `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81374/index.cnxml` | `021c29fa9a6ab3d5b06d2ef143a82d2ac818ed25fe6fd44ebf5d7a6be07a123a` |
| ID | `downloads/mr-Deva-IN/releases/A20-v0.3.0-source.zip` → `source/modules/m81374/index.cnxml` | `d89a74aef766afca6a4ac7e1ae720f120d22cc771c11dd7e025c55bca1fabb8e` |

Personally viewed all12 existing filesystem review copies under `downloads/mr-Deva-IN/source-image-qa/MR-BRIDGE-014/`: both `en-` and `id-` versions of `CNX_IntAlg_Figure_03_06_021_img_new.jpg` through `026_img_new.jpg`. Tests independently compare each member's bytes with its fixed reviewed hash and with the six committed canonical EN assets. Each locale pair is byte-identical; all12 were nevertheless directly viewed. No image conclusion relies solely on alt text or the author's note.

## Mathematics and pixels

| Figure | Independent observations and checked answers |
|---|---|
| 021 | Axes±6, closed endpoints (−3,−1)/(3,1), internal maximum (1.5,3), y-axis crossing2. Domain[−3,3], range[−1,3]; source alt's ±4 axes are wrong. |
| 022 | Axes±6, closed endpoints (−5,−4)/(1,2), crossing (0,−3). Domain[−5,1], range[−4,2]. |
| 023 | Axes±6, closed endpoints (−2,1)/(4,−5), internal maximum (0,3). Domain[−2,4], range[−5,3]; source axis descriptions differ from pixels. |
| 024 | x-window[−2π,2π], y-axis±6, peaks1/troughs−1. f(0)=0; f(3π/2)=f(−π/2)=−1. Five visible zero inputs −2π,−π,0,π,2π and corresponding intercept pairs. y-intercept(0,0), supplied full domain all reals, range[−1,1]. Source alt's y±4 is wrong. |
| 025 | Same x-window/y±6, peaks2/troughs−2. f(0)=0; f(π/2)=f(−3π/2)=2. Same five visible zeros/intercepts, y-intercept(0,0), supplied domain all reals/range[−2,2]. Global repeated-wave inference requires the corrected assumption described below. |
| 026 | Same window/y±6. f(0)=1; f(π)=f(−π)=−1. Four visible zero inputs −3π/2,−π/2,π/2,3π/2, all14 x-intercept pairs across024–026 checked; y-intercept(0,1), supplied domain all reals/range[−1,1]. Endpoints±2π are not zeros. |

No interpolation formula was fitted to the first three curves. Their complete visible arcs, endpoint inclusion and interior extrema were inspected. Axes/window extents are not substituted for domain/range. Nine explicit evaluations, six finite domain/range components and three eight-part groups total30 supplied answer components; all agree with the actual sources and diagrams. Source-declared or explicitly assumed continuation is kept separate from finite-window observations. All54 expected-math entries have category-specific checks against actual source expressions, exact rational π coefficients, manually inspected pixel witnesses, interval endpoints or explicitly declared continuation families; they are not validated only by equality to their own config strings.

### One corrective finding, now resolved

Initial target attributed an explicitly repeating pattern to all three wavy source diagrams. Independently read EN025 ending **“The line extends infinitely to the left and right.”** and ID025 ending **“Garis ini memanjang ke kiri dan kanan tanpa batas.”** Unlike024/026, neither explicitly says the pattern repeats. This matters to the added global `(nπ,0)` intercept family; an indefinite continuation alone does not prove periodicity.

Reported the issue to root without editing the translation. Root corrected the intro,025 alt and TryIt3(g)/(h)/(e) added commentary. The reviewer then read the full changed intro and entire TryIt3 directly. They now distinguish025's indefinite line from024/026's source-stated repeating pattern, preserve the supplied all-real domain/[−2,2] range, and expressly condition the added global-family/range explanation on an authored repeated-wave assumption. A regression originally failed on the false attribution and now passes. No numerical source answer, source ID, config math or image was changed. No remaining correction is requested.

Both locales really contain malformed `f = (π/2) = 2` and `f = (−3π/2) = 2` in `fs-id1167836550513`. The target explicitly discloses removing the first equal sign to restore function application; argument and output values agree with pixels. Tests bind both the original malformed trees and corrected displayed answers. The worked example's unconstrained(d)/(e), versus the TryIts' explicitly closed-window(d), are preserved; finite source lists are not silently presented as complete infinite lists.

## Actual Marathi canon checks

Fresh readable source consultation occurred during this independent review, not merely inherited from the author:

- [C18, आलेख](https://vishwakosh.marathi.gov.in/24316/): read the horizontal/vertical-axis and coordinate-construction prose, and the equation-graph/zero-intersection discussion through fresh search-reader text. This supports the target's vertical x-tracing, horizontal y-tracing, ordered सहनिर्देशक and distinction between x-inputs and full intercept pairs. The continuous-curve assumption does not establish arbitrary periodic continuation, reinforcing the025 finding.
- [C19, फलन](https://vishwakosh.marathi.gov.in/27548/): freshly read the opening definition, domain/codomain and actual image-set paragraph. It confirms प्रांत and कक्षा as the output-set variant; target's consistent working मूल्यसंच is honestly marked as such. A targeted result also exposed the actual आवर्त फलने paragraph, defining repetition by equality after a fixed shift; it did not license attributing that condition to025 when its source does not state it.
- [C20, गणितीय संकेतने, चिन्हे व संज्ञा](https://vishwakosh.marathi.gov.in/21279/): read actual `( )`, `[ ]`, `[ )`, `( ]`, infinity and function-notation rows, then reread the closed/open interval rows during revision. These support अंतराल and closed endpoint brackets. The compound अंतराल-संकेतलेखन remains an authored classroom phrase, not a falsely attested full term. An incidental primary-source [Rolle-theorem passage](https://vishwakosh.marathi.gov.in/26597/) explicitly explained both endpoints included/excluded; only that readable parenthesis explanation was relevant, not advanced calculus content.

No failed web fetch occurred in this review's own successful search-reader passes. An oversized combined tool output was truncated; selected relevant text was reread in bounded calls before relying on it. The author's/root's earlier502 failures are not relabeled as this reviewer's successful reads. No fresh successful read of candidate32824 is claimed, and no global canon promotion or unrelated audit was performed. No new Marathi PDF reference or OCR step was used.

## Tests, links and limitations

Command: `python -B mr-Deva-IN/tools/test_unit14_math.py`. **19/19 PASS, zero skips**, final run after root's source-attribution repair and successful rebuilt receipt notification. The standard-library suite reads only; its exact-coefficient parser rejects arbitrary execution, bad grouping, omitted nonzero π, π in a denominator and duplicate π factors.

Tests verify ordered selectors, all55 source IDs and ancestry/preorder, 58 identical EN/ID MathML trees,30 answer components,54 displayed-math checks, six bidirectional original answer pairs,17 local links, five HTTPS links, source resource URL `https://openstax.org/l/37domainrange`, six image references and all12 original-image witnesses, current frozen fragments/assets and all39 pinned witnesses. The resource destination is retained but not fetched, translated or endorsed. Component credit language remains the settled **CC BY-NC-SA4.0** with OpenStax/Marecek/Mathis attribution and third-party-notice reservation; no new license audit.

The test of the existing HTML artifact reads its bytes solely to verify its receipt hash, not its DOM, geometry or visual appearance. No browser or alternate rendering surface was used. Current build receipt correctly leaves visual browser QA and independent mathematical proof unclaimed. This independent mathematical review does not alter the receipt's honest scope. Native-speaker/teacher review, HTML/PDF reading-copy acceptance and whole-module/book completion remain unclaimed; the five-book assignment continues.

| Final reviewed file | SHA-256 |
|---|---|
| `translations/MR-BRIDGE-014.xml` | `bcbf366d702bf38c7fd434da5ac8bb56183885962ae7eec2b7c62672c4a69885` |
| `units/MR-BRIDGE-014.json` | `ec8e6ed0bae4807c2aa36537456f6f07d4ec76259827c803b7b76c84b63cf38b` |
| `provenance/MR-BRIDGE-014.lock.json` | `3577b5536628c18d6485937f1b53be0b513162f0e46f79a719aeadbe05f7b92e` |
| `output/MR-BRIDGE-014.html` — hash/receipt only | `61870864ad97589ac8f357512f056e39b926c94e80da9eedc87ad227366280db` |
| `tools/test_unit14_math.py` | `0b94da014f668292f7477695484c8d3c908944175e09483add5601ec79e52594` |

Next unselected marker for this section: `A20:m81374#fs-id1167836597228` (Key Concepts). This review hands back both owned files to root; it does not end the full assignment.
