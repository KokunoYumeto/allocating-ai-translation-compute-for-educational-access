# Allocating AI Translation Compute for Marginal Educational Access

This standalone research package develops a reproducible portfolio model for
deciding where AI-assisted adaptation of open mathematics resources can create the
largest increase in *comfortable, usable educational access*. It evaluates exact
language, variety, script, territory, learner, curriculum, format, and overlap
profiles rather than treating speaker population or a language-family name as
sufficient evidence of reach.

The package is independent of the interlanguage-sidecar publication lineage. It
contains the report, frozen evidence tables, analysis scripts, model definitions,
validation receipts, and publication metadata needed to inspect or reproduce the
reported results.

- DOI: https://doi.org/10.5281/zenodo.22217113
- Repository: https://github.com/KokunoYumeto/allocating-ai-translation-compute-for-educational-access

## Headline results

- The source and supplemental population layers contain 477 observations registered
  through 83 source records.
- The operational Top 10 is: Bangla shared-source caregiver/ECE and Indian-TVET
  residuals; Telugu; Odia; Bhojpuri; Hausa; Bambara; Standard Hindi; Peru Ashaninka;
  Russian learned standard; and Dari.
- Bahasa Indonesia (position 32), Mainland Simplified Chinese (34), Japanese (37),
  and Indonesian-Malaysian Malay localization (31) are explicitly evaluated on the
  same basis. Their positions are policy-sequence results, not declarations of low
  educational value.
- The Top 100 includes a needs-specific first-product assignment for every
  position. Population rank is not treated as curriculum rank.
- The Top-100 interlanguage crosswalk grants no invented demographic reach, while
  retaining semantic-source, terminology, formula, script, and QA reuse and the
  mathematics-specific hypothesis that formal structure can improve receptive use.
- Translating the fixed 210-unit, 120,083-source-token Formal Reasoning Core for the
  100 selected positions yields low, base, and high gross-workload comparators of
  91.274 million, 407.305 million, and 1.866 billion tokens. These are scenario
  workloads, not prices, energy estimates, or needs-optimal curriculum plans.
- The Indonesian program audit reports several deliberately nonadditive accounting
  views. In particular, its 33-root total and its descendant-inclusive closure must
  never be summed.

## Package map

The exact release inventory and SHA-256 identities are recorded in the release
manifest. The principal file groups are:

- `PAPER.md`, `PAPER.docx`, and `PAPER.pdf`: source manuscript and reader formats;
- `MODEL_SPEC.md`, `FACTOR_POLICY.md`, `RANKING_METHOD.md`, and the needs,
  interlanguage, observation-use, search, source-reference, and evidence-register
  files: controlling methods and scope rules;
- `population_source_register_public.csv`, population observations, candidate
  interventions, score tables, Top 10/Top 100 tables, needs assignments, overlap
  crosswalks, curriculum mappings, and compute scenarios: frozen analysis inputs and
  outputs;
- `figure_1_rank_sensitivity.*` and `table*.csv`: report figures and result tables;
- `compute_token_audit_33_roots_20260830.json` and the public Indonesian
  reconciliation notes: sanitized compute and program evidence;
- `scripts/`: bounded analysis, manuscript-refresh, DOCX-build, PDF-audit, and
  validation tooling. The root-level data layout deliberately matches the scripts'
  repository-relative input contracts; selected derived model inputs remain under
  `staging/` at their original relative paths.

Private task transcripts, credentials, absolute local witness paths, unrelated
publication histories, and unpublished source documents are intentionally excluded.

## Rebuild from the frozen public inputs

Run all commands from the package root. The numerical and document builders read
only repository-relative paths.

Requirements:

- Python 3.11 or later;
- Node.js 20 or later for the included `.mjs` data builders;
- Python packages used by the included scripts: `matplotlib`, `openpyxl`,
  `python-docx`, `lxml`, `Pillow`, `pdfplumber`, and `pypdf`;
- LibreOffice for DOCX-to-PDF conversion;
- Poppler for rendered-page and PDF inspection.

Recompute the result tables and figure, refresh the generated manuscript sections,
normalize display punctuation, and run the content validator:

```text
python scripts/build_results_tables.py
python scripts/build_rank_sensitivity_figure.py
python scripts/refresh_embedded_appendices_20260830.py
python scripts/normalize_ascii_dashes.py
python scripts/validate_final_publication_content.py
```

Build the editable report from the Markdown source:

```text
python scripts/document/build_report_docx.py --input PAPER.md --figure figure_1_rank_sensitivity.png --output PAPER.docx --report-json DOCX_BUILD_REPORT.json
```

Render `PAPER.docx` with LibreOffice, convert the resulting PDF to page PNGs with
Poppler, and then run the structural/accessibility and PDF audits. Equivalent shell
commands are:

```text
mkdir rendered_pdf
mkdir rendered_pages
libreoffice --headless --convert-to pdf --outdir rendered_pdf PAPER.docx
pdftoppm -png -r 144 rendered_pdf/PAPER.pdf rendered_pages/page
python scripts/document/qa_docx.py PAPER.docx --render-dir rendered_pages --source PAPER.md --model-spec MODEL_SPEC.md --out-json DOCX_QA_REPORT.json
python scripts/document/audit_final_pdf.py
```

The PDF audit reads the released root `PAPER.pdf`, not the newly converted comparison
PDF. The rendered PNGs are locators for all-page layout inspection; differences in
LibreOffice, font, or operating-system versions can change pagination and should be
reported rather than silently substituted for the released bytes.

The release manifest, validation JSON, DOCX QA receipt, PDF audit, and public-byte
receipts are the final authorities for a particular release. If any source table is
changed, rebuild all downstream tables and documents and regenerate those receipts;
do not retain a prior validation result.

## Frozen public-input boundary

The package freezes source identities and observations rather than silently updating
them to the latest web state. The public source register records source titles,
authorities, dates, definitions, URLs, locators, hashes where available, confidence,
and limitations. It replaces private local witness locations with an omission marker.

The empirical Indonesian evidence is also boundary-specific:

- the 33-root event window runs from 2026-08-20T10:40:19Z through
  2026-08-29T23:33:38.559Z;
- cached, fresh, cache-write, output, and reasoning fields follow the exact semantics
  in `compute_token_audit_33_roots_20260830.json`;
- the 6,726-thread closure contains the 33 roots and is therefore an inclusive
  comparison total, not an additive second workload;
- page inventories describe different source, teaching-package, rendered, and public
  artifact universes. None is asserted to be a final Indonesian pagination total.

## Interpretation limits

The model reports evidence-bounded opportunity and workload sensitivities. A zero
registered lower bound means that at least one required access or non-overlap factor
is unbounded; it does not mean zero educational value. A large speaker population is
not automatically a harmed population, a first-language population is not
automatically an academic-reading population, and one interlanguage name is not
automatically evidence of regional comprehension.

Token counters are accounting units exposed by the model workflow. They are not
FLOPs, GPU time, energy, monetary cost, or weekly-plan consumption. Model-generated
translation can combine mathematical reasoning, terminology constraints, source
checking, mechanical structure/formula checks, and independent model critique; the
paper evaluates that production architecture without requiring a human-dependent
publication hold.

## Model provenance

Research synthesis, analysis, drafting, and reproducibility work were performed with
**OpenAI Codex gpt-5.6-sol, Ultra**. The release preserves exact source citations,
public evidence identities, uncertainty labels, and deterministic validation
receipts. See `PROVENANCE.md` for the complete boundary.

## License and citation

The first-party paper, figures, first-party documentation, and first-party tabular
data are licensed under Creative Commons Attribution 4.0 International; see
`LICENSE`. The first-party code is licensed under the MIT License; see
`CODE_LICENSE`. Third-party source works, quoted material, names, marks, and linked
datasets retain their original rights and are not relicensed; see
`THIRD_PARTY_NOTICES.md`.

Citation metadata, the standalone DOI, and the repository URL are supplied in
`CITATION.cff`. Exact public-byte identities are recorded in the publication
receipts after release.
