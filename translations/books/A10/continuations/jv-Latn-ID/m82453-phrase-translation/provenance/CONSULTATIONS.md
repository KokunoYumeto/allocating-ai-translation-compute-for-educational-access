# Canon, terminology, and register decisions

## Evidence actually consulted

- The frozen English OpenStax subtree `source/en.cnxml`, SHA-256 `f8b281215e7630e8425e26bd28d54b26ed707fe9840bfb2edd417d40da666d9f`, from `openstax/osbooks-prealgebra-bundle` commit `38cae454e644abf9f0a623e876994553881597c9`, collection `col31130`, module `m82453`, section `fs-id1170654942537`.
- The pinned Indonesian v1.0.2 source ZIP `source/pivot-source.zip`, SHA-256 `6f04e88387e8d4e6e710dddcebb8d41e952a315231d7e203d62170c6ad9f3456`, and its exact extracted comparison subtree `source/id-pivot.cnxml`, SHA-256 `8acbc36596af0f7552f4b50268452c083137ba9b58979385511e4cc3f7b240e3`.
- The three unchanged canonical JPEGs listed in `source/BOUNDARY.json`, inspected at their actual pixels. Figure 015 colors the complete sequence “of a and” red, including the middle `a`; figure 018 shows division by `7`, not `v7`.
- The preserved MathML, table cells, worked solutions, and exercise answers in the frozen source. These are the decisive evidence for operand order and mathematical sense.

No Javanese-speaking human expert, classroom participant, language authority, or pronunciation assessor was consulted for this bounded packet. No external Javanese mathematical dictionary or representative field corpus is claimed as evidence here. Terminology and register choices therefore remain provisional and reversible; that absence is not treated as a release hold.

## Operand-order decision

In this section, English `b more than a` denotes the operation `a + b`, and `b less than a` denotes `a − b`. They are not rendered as free-standing comparative claims. The operational Javanese forms are `b ditambahaké marang a` / conversational `b ditambahké menyang a`, and `b dikurangaké saka a` / conversational `b dijupuk saka a`. The Indonesian bridge uses `b ditambahkan pada a` and `b dikurangkan dari a`. Worked rectangle and coin examples state the operation and resulting expression directly. English wording remains visible as a quoted language object or through the exact source link.

## Provisional terminology

- `gunggung` — sum
- `salisih` — difference
- `asil ping-pingan` — product; `ping-pingan` names multiplication
- `asil paran` — quotient; `paran` names division and `pambagi` names the divisor
- `pasagi dawa` — rectangle
- `ekspresi aljabar` — algebraic expression in the academic track; `wujud aljabar` is the plainer conversational equivalent

These choices are internally consistent with the formulas and the Indonesian comparison, but they are not presented as standardized Javanese mathematical terminology.

## Register decision

The academic track uses neutral explanatory prose, passive constructions such as `digunakaké`, explicit terms such as `operand`, and impersonal prompts. The conversational track uses direct ngoko prompts such as `delengen`, `nganggoa`, `jupuken`, and `owahana`, shorter clauses, and `wujud aljabar`. Mathematical content, IDs, formulas, examples, and answers are identical across the two tracks. The distinction is meaningful editorial register, not a claim of dialect certification.

## Recorded source corrections

- Canonical table `eip-72` has an accessibility summary that says width and `w−6`; the visible problem and table use length `l` and `l−6`. Target summaries follow the visible mathematics.
- Canonical prose split as `and t` / `o find` is joined coherently in the targets.
- Canonical `Translate the phase into algebra` is rendered with the intended sense `phrase` in the targets.
- Canonical eip-470 quotation punctuation is repaired at the third descendant MathML node, the quoted `q`, with a deterministic XPath assertion.
- Figure 015 target descriptions name the full red sequence `of a and`; figure 018 target descriptions correct the source-alt `v7` typo to the visible divisor `7`.

The canonical English witness remains unchanged so every correction is auditable.

