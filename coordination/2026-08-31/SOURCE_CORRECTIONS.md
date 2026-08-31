# A20 m81373: three verified figure discrepancies

Consolidated 2026-08-31. Verification recorded 2026-08-30. Scope is only figures **202, 205 and 208** in Intermediate Algebra module `m81373`, comparing the pinned English source with the Indonesian v0.3.0-wip editable-source release. This is a narrow production correction note, not a full-module correctness certification, new source/license audit, or claim that upstream has been changed.

## Status and verification boundary

Marathi translation production reported the discrepancies and retained both source variants in its unit provenance. The coordinator independently inspected the six affected English/Indonesian raster images. A separate text/hash check compared all six selected CNXML fragments with their locks and module content inside the pinned archives, verified the two module hashes, and matched the six reviewed image copies to their recorded hashes and sizes.

Thus the three discrepancies below are independently corroborated, not merely repeated reports. The selected-member verification did not repeat a full-archive audit. No original source archive was changed. This handoff contains correction instructions and identifiers only; implementation and review in each language remain separate work, and no upstream issue submission or published fix is asserted.

## Exact source witnesses

English upstream repository: [OpenStax osbooks-prealgebra-bundle at commit 38cae454e644abf9f0a623e876994553881597c9](https://github.com/openstax/osbooks-prealgebra-bundle/tree/38cae454e644abf9f0a623e876994553881597c9).

- [Pinned canonical ZIP](https://codeload.github.com/openstax/osbooks-prealgebra-bundle/zip/38cae454e644abf9f0a623e876994553881597c9): observed SHA-256 `effdf2dbb6dfd9cab771b568c6575d8074be4a1f9565f1fedbd54f621e138917`.
- CNXML archive member: `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`.
- [Upstream CNXML](https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml): SHA-256 `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.

Indonesian comparison: [Intermediate Algebra v0.3.0-wip](https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/tag/v0.3.0-wip).

- [Editable-source ZIP](https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id/releases/download/v0.3.0-wip/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-editable-source.zip): SHA-256 `a9c53c328be944e12b707d5cb16e289755eff0c603d1652bfca13dd572e780d7`.
- CNXML archive member: `source/modules/m81373/index.cnxml`.
- Member SHA-256: `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

Use this exact released asset for the Indonesian witness: the recorded repository main/tag tree was not interchangeable with the released editable-source payload. Archive sizes, verification qualifications and other source pins are in [SOURCES.md](SOURCES.md).

## Corrections and answer provenance

| Figure | Exercise / media IDs | Verified English image | Conflicting source text and Indonesian image | Treatment |
|---|---|---|---|---|
| 202 | Exercise `fs-id1167836600990`; media `fs-id1167829614618` | Amy maps to **February 24**. | Both English and Indonesian alt texts, and the Indonesian redraw, say February 14. | Preserve the English image; correct localized alt text to February 24. Any answer supplied by the translation is **original work inferred from the image**, not a translated supplied answer. |
| 205 | Exercise `fs-id1167836621459`; media `fs-id1167836623119` | Includes **(-2,-1)**. | Both alt texts and the Indonesian redraw instead use (-3,-1). | Preserve the English image and the already supplied correct answer; correct localized alt text. |
| 208 | Exercise `fs-id1167836509162`; media `fs-id1167836546296` | Includes **(-1,-3)** and **(2,6)**, with six distinct inputs. | Both alt texts and the Indonesian redraw substitute (-2,-3) and (3,6). | Preserve the English image; correct localized alt and derive any new answer from its six points. Explicitly label that answer **original work**. |

### Figure 202: no supplied solution

Neither selected English nor Indonesian exercise fragment supplies a solution. The correction from February 14 to February 24 follows the English pixels. Do not attribute an image-derived answer to a nonexistent source solution.

### Figure 205: the supplied solution agrees with the English pixels

Both source variants contain solution `fs-id1167836448402` (paragraph `fs-id1167836448404`). They supply:

- Points: `{(2,3),(4,-3),(-2,-1),(-3,4),(4,-1),(0,-3)}`.
- Domain: `{-3,-2,0,2,4}`.
- Range: `{-3,-1,3,4}`.

These agree with the English raster. The error is in the alt texts and Indonesian redraw, not in these supplied answers. Retain supplied-answer attribution when translating them. The English image's axis labels run from -5 to 5; the conflicting alt description's -6 to 6 extents must not be copied as a pixel description.

### Figure 208: preserve all six inputs and the function result

The English image has the relation:

`{(-2,-6),(-1,-3),(0,0),(0.5,1.5),(1,3),(2,6)}`.

Its domain is **`{-2,-1,0,0.5,1,2}`**, its range is `{-6,-3,0,1.5,3,6}`, and it **is a function** because every input has one output. Keep both the fractional input `0.5` and output `1.5`.

Both source alt texts instead describe:

`{(-2,-6),(-2,-3),(0,0),(0.5,1.5),(1,3),(3,6)}`.

The Indonesian redraw follows that conflicting set. It repeats input `-2` with two outputs, reduces the domain to five values, and changes the relation to a non-function. Do not reconstruct the correct domain or function status from those alt texts. Neither selected source exercise supplies a solution; the six-value domain, range and function answer above are explicitly image-derived mathematical conclusions, not translations of a supplied answer.

## Exact image members and byte identities

All filenames have the form `CNX_IntAlg_Figure_03_05_NNN_img_new.jpg`, where `NNN` is the figure number. For each row below, the exact archive member is the applicable prefix plus that filename:

- English prefix: `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/media/`.
- Indonesian prefix: `source/media/`.

The links identify the English image at the pinned upstream commit. Indonesian images are members of the exact editable-source ZIP linked above; a similarly named image in another release is not this witness.

| Figure / witness | Bytes | SHA-256 |
|---|---:|---|
| [202 English](https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/media/CNX_IntAlg_Figure_03_05_202_img_new.jpg) | 87,595 | `c374c8edb5c175f0919dd49695c40c0ef1b14266c9ae7919c80091a1f612a3bf` |
| 202 Indonesian | 330,031 | `09099c441dfeb3f0de1bb0ec2b4f407a9462ddac5deda66ff7f59273fe1dc275` |
| [205 English](https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/media/CNX_IntAlg_Figure_03_05_205_img_new.jpg) | 78,811 | `904bf393939f9ba87479847d835cae3f2fdd9ec680b094a04ec6099f8ac43d02` |
| 205 Indonesian | 283,303 | `9b1d1decfec0fc446cba8689ea675c749f6a037d7fd64bfabd95c23ba4b00ac4` |
| [208 English](https://github.com/openstax/osbooks-prealgebra-bundle/blob/38cae454e644abf9f0a623e876994553881597c9/media/CNX_IntAlg_Figure_03_05_208_img_new.jpg) | 20,645 | `7d86642fff819ff6419b0f786494458b3f5b5144f48011fade0866b3e4201d05` |
| 208 Indonesian | 374,702 | `f252e5ffd283b8ab11f3cdd9096fac359d2922c96254ca64c10ea7c529f825f1` |

Different hashes alone do not establish a mathematical discrepancy. The claims above rest on the selected visual and CNXML comparisons; no conclusion is extended to other figures or modules.
