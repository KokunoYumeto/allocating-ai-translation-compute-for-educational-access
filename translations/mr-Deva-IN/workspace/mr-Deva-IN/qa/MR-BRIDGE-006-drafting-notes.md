# MR-BRIDGE-006 drafting and source-review notes

Date: 2026-08-31. This is an agent-authored production checkpoint, not a whole-module or whole-book completion record. It does not claim teacher, native-speaker or human editorial approval. Root owns freezing, build, browser QA and shared logs.

## Exact source boundary

Read the pinned module bytes directly from the two existing ZIPs, without extracting either corpus:

- EN: `A20-en`, member `osbooks-prealgebra-bundle-38cae454e644abf9f0a623e876994553881597c9/modules/m81373/index.cnxml`, module SHA-256 `2b606026c2b34cdf69acfa29bfe4b90abdb6961a322a78c7ec20107e0948b05c`.
- ID: `A20-id`, member `source/modules/m81373/index.cnxml`, module SHA-256 `e9e593b31587995170c520b9175f2e0c0cb335282c951bb1d769f775344311ee`.

The selected run begins with heading `fs-id1167836714017`, “Find the Value of a Function”, and continues to the end of its parent practice section, ending with exercise `fs-id1167829749356`. Both locales have the same structure and IDs: 31 top-level source blocks, comprising five heading/instruction paragraphs and 26 exercises. Thirteen exercises contain supplied solutions and thirteen omit them. The group contains 119 distinct source IDs and no source images. The translation preserves all 119 once, in source order, and adds no source-looking IDs. It translates all 26 exercises, every listed subpart and every supplied answer. The next topic lies outside this child run; no later source is silently included.

## EN/ID comparison and source correction

Compared all MathML-bearing blocks between EN and ID. The exercise mathematics agrees apart from Indonesian decimal commas. In printing-cost exercise `fs-id1167833380107`, the English supplied solution incorrectly labels the values `N(0)` and `N(1000)`, although the problem defines `C(x)`. The Indonesian solution has corrected `C(0)` and `C(1000)`. The Marathi reader uses `C` and explicitly records the correction; values 1500 and 4750 are unchanged and the original bytes remain in provenance.

No raster was read or embedded because neither locale contains a `cnxml:image` in this group. The equations were read from MathML, including the two rational functions and the absolute-value bars.

## Marathi canon: selection and drafting

Actually reread C12 and C13 from `downloads/mr-Deva-IN/canon/ocr/balbharati8-85.txt` and `balbharati8-86.txt`, then inspected the corresponding full rendered page images. The images govern where OCR damages fractions and symbols. C12 distinguishes an equation's **उकल** from the operations used to find it and states that equal operations are made on both sides. This unit therefore reserves **उकल** for solving an equation and calls the current task **फलनाचे मूल्य काढणे**. C13's explicit, line-by-line handling of fractions and signed terms informed the visible substitution chains; no “move it across and change the sign” shortcut is used.

Fresh official-domain search retrieval returned the actual readable Marathi Vishwakosh prose for C14-C17 at <https://marathivishwakosh.org/21979/>. Read the dependence example, exactly-one correspondence, domain/codomain paragraph, value-notation sentence and constant-function paragraph; image-only formulas were not treated as read. Concrete effects:

- C14 keeps each evaluation tied to exactly one output, while `g(x)+g(2)` is kept distinct from `g(x+2)`.
- C15 supplies **प्रांत/सहप्रांत** context but this exercise group does not ask for those sets, so no unnecessary domain lesson was inserted.
- C16 prevents implying that different inputs must produce different values; no such false condition is added.
- C17 supports the independent/dependent distinction in the four applications. The entry attests **स्वतंत्र** and **अवलंबित** as component descriptions; the established classroom phrase **अवलंबी चल** remains a documented provisional workflow choice, not falsely claimed as an exact quotation.

This source group also creates a narrow absolute-value terminology need. Direct open of <https://vishwakosh.marathi.gov.in/21279/> returned 502, but fresh search-reader text exposed the actual relevant table row. It gives `|क्ष|` as **क्ष चे केवल मूल्य** and also **क्ष चे चिन्ह निरपेक्ष मूल्य**. That actual C20 paragraph supports keeping the established short term **केवल मूल्य** in questions 19-20. The source's Latin variables and vertical-bar notation remain unchanged.

## Authored working and mathematical revision

The 13 source-supplied answers are labeled “स्रोतातील उत्तर”; additional calculation lines beside them are explicitly `data-kind="original"`. Each of the 13 source omissions has a separate `mr-answer-*` target labeled “नव्याने जोडलेले उत्तर” and says that the source contains no answer. These additions answer only existing source questions; no diagnostic or supplementary question was invented.

Recalculated every result independently while drafting. Key omitted results are:

- `f(x)=3x+4`: 10, 1, `3a+4`; `f(x)=−6x−3`: −15, 3, `−6a−3`.
- `f(x)=x²+x−2`: 4, −2, `a²+a−2`; `f(x)=3x²+x−2`: 12, 0, `3a²+a−2`.
- `g(x)=5x−8`: `5h²−8`, `5x+2`, `5x−6`; `g(x)=−8x+2`: `−8h²+2`, `−8x−14`, `−8x−12`; `g(x)=7−5x`: `7−5h²`, `−5x−3`, `4−5x`.
- `g(3)=27`, `G(−2)=24`, `h(−4)=12`, and `(4−2)/(4+2)=1/3`.
- Ken: `N(30)=73`; manufacturing: `C(0)=2500`, `C(1000)=9750`.

Revision reread the complete Marathi draft alongside the selected-source order and the relevant C12-C17/C20 effects. Negative inputs stay parenthesized before squaring; an expression input such as `h²` replaces the whole formal input; rational evaluations show nonzero denominators; application interpretations retain the source's units. All 107 `data-check` strings currently match the unit configuration exactly. A temporary-fixture check found 31 ordered source wrappers, all 119 source IDs exactly once, 138 total unique XML IDs, NFC text and no image references. These are drafting checks only; they do not replace the root's provenance freeze, generic build, mathematical regression or browser review.
