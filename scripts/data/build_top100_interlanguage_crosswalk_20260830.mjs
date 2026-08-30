import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const taskRoot = process.cwd();
const outCsv = path.join(taskRoot, "top100_interlanguage_overlap_crosswalk.csv");
const outMethod = path.join(taskRoot, "TOP100_INTERLANGUAGE_CROSSWALK_METHOD_20260830.md");
const outReceipt = path.join(taskRoot, "TOP100_INTERLANGUAGE_CROSSWALK_VALIDATION_RECEIPT_20260830.md");

const sourcePaths = {
  top100: path.join(taskRoot, "TOP_100.csv"),
  needs: path.join(taskRoot, "top100_needs_assignment_v2.csv"),
  summary: path.join(taskRoot, "appendix_f_interlanguage_matrix_summary.csv"),
  interventionMatrix: path.join(taskRoot, "staging", "interlanguage_bundle_model", "interlanguage_intervention_matrix.csv"),
  normalized: path.join(taskRoot, "staging", "interlanguage_matrix", "interlanguage_overlap_normalized.csv"),
};

const rel = (p) => path.relative(taskRoot, p).replaceAll("\\", "/");
const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        field += ch;
      }
    } else if (ch === '"' && field.length === 0) {
      quoted = true;
    } else if (ch === ",") {
      row.push(field);
      field = "";
    } else if (ch === "\r" && text[i + 1] === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
      i += 1;
    } else if (ch === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += ch;
    }
  }
  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

async function readCsvTable(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  const matrix = parseCsv(text);
  if (!Array.isArray(matrix) || matrix.length < 2) {
    throw new Error(`CSV is empty or unreadable: ${rel(filePath)}`);
  }
  const headers = matrix[0].map((v) => String(v ?? "").replace(/^\uFEFF/, ""));
  const rows = matrix.slice(1).map((row) => Object.fromEntries(headers.map((h, i) => [h, row[i] == null ? "" : String(row[i])])));
  return { text, headers, rows };
}

function csvCell(value) {
  const s = value == null ? "" : String(value);
  return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

function toCsv(matrix) {
  return matrix.map((row) => row.map(csvCell).join(",")).join("\r\n") + "\r\n";
}

function unique(values) {
  return [...new Set(values.filter(Boolean))];
}

function joinIds(...parts) {
  const ids = [];
  for (const part of parts) {
    for (const token of String(part ?? "").split(/\s*(?:;|\|\|)\s*/)) {
      const trimmed = token.trim();
      if (trimmed && !ids.includes(trimmed)) ids.push(trimmed);
    }
  }
  return ids.join(";");
}

function territoryCompatible(topTerritory, edgeTerritory) {
  const top = String(topTerritory ?? "").trim().toLowerCase();
  const edge = String(edgeTerritory ?? "").trim().toLowerCase();
  if (!top || !edge || edge.includes("pending")) return false;
  return edge.includes(top);
}

const sources = Object.fromEntries(await Promise.all(Object.entries(sourcePaths).map(async ([key, filePath]) => [key, await readCsvTable(filePath)])));
const topRows = sources.top100.rows;
const needsRows = sources.needs.rows;
const summaryRows = sources.summary.rows;
const interventionRows = sources.interventionMatrix.rows;
const edgeRows = sources.normalized.rows;

const failures = [];
const assert = (condition, message) => { if (!condition) failures.push(message); };

assert(topRows.length === 100, `TOP_100.csv must contain 100 rows; found ${topRows.length}`);
assert(needsRows.length === 100, `top100_needs_assignment_v2.csv must contain 100 rows; found ${needsRows.length}`);
assert(new Set(topRows.map((r) => r.portfolio_position)).size === 100, "TOP_100 portfolio positions are not unique");
assert(new Set(topRows.map((r) => r.intervention_id)).size === 100, "TOP_100 intervention IDs are not unique");
assert(topRows.map((r) => Number(r.portfolio_position)).sort((a, b) => a - b).every((v, i) => v === i + 1), "TOP_100 positions are not exactly 1 through 100");

const needsByKey = new Map(needsRows.map((r) => [`${r.portfolio_position}|${r.intervention_id}`, r]));
const summaryById = new Map(summaryRows.map((r) => [r.intervention_id, r]));
const interventionByEdge = new Map(interventionRows.map((r) => [r.matrix_row_id, r]));

const outputRows = [];

for (const top of topRows.sort((a, b) => Number(a.portfolio_position) - Number(b.portfolio_position))) {
  const needs = needsByKey.get(`${top.portfolio_position}|${top.intervention_id}`);
  assert(Boolean(needs), `No exact needs row for position ${top.portfolio_position} / ${top.intervention_id}`);

  const exact = edgeRows.filter((e) => e.language_tag === top.target_profiles);
  const scopedPrefix = edgeRows.filter((e) =>
    e.language_tag &&
    top.target_profiles.startsWith(`${e.language_tag}-`) &&
    territoryCompatible(top.territory_or_scope, e.territory)
  );
  const unresolvedPrefix = edgeRows.filter((e) =>
    e.language_tag &&
    top.target_profiles.startsWith(`${e.language_tag}-`) &&
    !territoryCompatible(top.territory_or_scope, e.territory)
  );

  let edge = null;
  let relationStatus = "no_exact_relation_in_current_matrix";
  let matchBasis = "none";
  let integrabilityStatus = "not_assessed_from_current_interlanguage_matrix";
  let integrabilityBasis = "No exact target-profile relation appears in the current normalized interlanguage matrix.";
  let computeReusePotential = "none_credited";
  let computeReuseBasis = "No exact shared-core or interlanguage edge is registered for this Top-100 profile.";

  if (exact.length === 1) {
    edge = exact[0];
    relationStatus = "exact_profile_match";
    matchBasis = "Exact target-profile tag equality.";
  } else if (exact.length === 0 && scopedPrefix.length === 1) {
    edge = scopedPrefix[0];
    relationStatus = "exact_language_script_and_target_country_cell";
    matchBasis = "The matrix tag omits the region suffix, while its named territory explicitly contains the Top-100 target country.";
  } else if (exact.length === 0 && scopedPrefix.length === 0 && unresolvedPrefix.length === 1) {
    edge = unresolvedPrefix[0];
    relationStatus = "hypothesis_only_language_script_match_territory_unresolved";
    matchBasis = "Language and script align, but the matrix territory is unresolved or differs; this is not an exact integrable coverage edge.";
  } else {
    assert(exact.length + scopedPrefix.length + unresolvedPrefix.length <= 1, `Ambiguous interlanguage edge join for ${top.intervention_id}`);
  }

  const summary = edge ? summaryById.get(edge.intervention_id) : null;
  const interventionEdge = edge ? interventionByEdge.get(edge.edge_id) : null;
  if (edge) {
    assert(Boolean(summary), `Missing appendix-F summary for ${edge.intervention_id}`);
    assert(Boolean(interventionEdge), `Missing intervention-matrix row for ${edge.edge_id}`);
  }

  const isIndonesian = top.intervention_id === "NAT-121";
  const isExactOrScoped = relationStatus === "exact_profile_match" || relationStatus === "exact_language_script_and_target_country_cell";
  if (isIndonesian) {
    integrabilityStatus = "complete_baseline_no_forward_translation";
    integrabilityBasis = "The exact id-Latn-ID component has a complete 722/722 Open Logic output; its forward Open Logic deficit is D=0.";
    computeReusePotential = "complete_output_available_as_reuse_source_but_no_forward_id_work";
    computeReuseBasis = "The complete Indonesian corpus may seed adjacent profile adaptation, but no Malay or other demographic reach is inferred and no savings coefficient is measured.";
  } else if (isExactOrScoped) {
    integrabilityStatus = "profile_present_in_shared_core_architecture";
    integrabilityBasis = "An exact language/script component is named in the current normalized architecture; this is an engineering relation, not a comprehension or reach claim.";
    computeReusePotential = "structural_reuse_plausible_unquantified";
    computeReuseBasis = "Shared source alignment, terminology, register, or script handling can plausibly reduce duplicated work, but the current evidence contains no measured token-savings coefficient.";
  } else if (edge) {
    integrabilityStatus = "hypothesis_only_not_integrable_on_current_exact_evidence";
    integrabilityBasis = "The matrix itself leaves the exact territory/profile join unresolved; the relation is retained only as a research hypothesis.";
    computeReusePotential = "none_credited_pending_exact_profile_evidence";
    computeReuseBasis = "No shared-core compute saving is credited until the exact target profile and territory are resolved.";
  }

  const namedOutputStatus = isIndonesian
    ? "yes_complete_722_of_722_open_logic"
    : edge
      ? "no_current_named_localized_output_established_for_this_component"
      : "not_applicable_no_matrix_relation";
  const directCompletionOverlap = edge ? edge.existing_edition_overlap : "not assessed in this crosswalk";
  const forwardDeficit = isIndonesian ? "0" : edge ? "unknown" : "not_applicable";
  const reachBasis = isIndonesian
    ? "The named Indonesian output is the own-language baseline and is excluded from forward reach; no Malaysian or other cross-language credit is awarded."
    : edge
      ? "No named localized output for this exact component is registered here; named-output-only and no-cross-language-credit rules therefore yield zero current demographic reach credit."
      : "No exact current matrix relation exists, so no cross-language demographic reach can be credited.";

  const topSourceIds = joinIds(top.population_source_ids, top.profile_authority_source_ids);
  const edgeSourceIds = edge ? joinIds(edge.source_ids, interventionEdge?.source_ids, summary?.all_source_ids) : "";

  outputRows.push({
    portfolio_position: top.portfolio_position,
    intervention_id: top.intervention_id,
    intervention_name: top.intervention_name,
    target_profile: top.target_profiles,
    territory_or_scope: top.territory_or_scope,
    population_source_ids: topSourceIds,
    needs_assignment_status: needs?.needs_assignment_status ?? "",
    learner_stage: needs?.learner_stage ?? "",
    need_class: needs?.need_class ?? "",
    first_open_package_or_sequence: needs?.first_open_package_or_sequence ?? "",
    overlap_relation_status: relationStatus,
    interlanguage_intervention_id: edge?.intervention_id ?? "",
    interlanguage_edge_id: edge?.edge_id ?? "",
    interlanguage_mechanism: edge?.mechanism ?? "",
    interlanguage_edge_role: edge?.edge_role ?? "",
    matched_matrix_profile_tag: edge?.language_tag ?? "",
    profile_match_basis: matchBasis,
    matrix_script: edge?.script ?? "",
    matrix_territory_scope: edge?.territory ?? "",
    coverage_mode: edge?.coverage_mode ?? "",
    integrability_status: integrabilityStatus,
    integrability_basis: integrabilityBasis,
    shared_core_compute_reuse_potential: computeReusePotential,
    shared_core_compute_reuse_basis: computeReuseBasis,
    named_localized_output_status: namedOutputStatus,
    current_direct_component_completion_overlap: directCompletionOverlap,
    forward_component_deficit_D: forwardDeficit,
    current_cross_language_demographic_reach_credit: "0",
    demographic_reach_credit_basis: reachBasis,
    double_count_rule: edge?.double_count_rule ?? "No family or interlanguage multiplier is applied.",
    exclusions: edge?.exclusions ?? "No matrix relation; no inferred family coverage.",
    interlanguage_source_ids: edgeSourceIds,
    matrix_confidence: edge?.confidence ?? "",
    rankable_under_current_evidence: edge?.rankable ?? "false",
    crosswalk_note: isIndonesian
      ? "Complete Indonesian Open Logic is retained as D=0 overlap control, not as new work or cross-language reach."
      : edge?.notes ?? "No exact relation in the current normalized matrices.",
  });
}

const expectedExactPairs = [
  ["NAT-121", "IL-IDMS"],
  ["NAT-015", "IL-PUNJABI"], ["NAT-014", "IL-PUNJABI"],
  ["NAT-013", "IL-HU"], ["NAT-012", "IL-HU"],
  ["EXP-003", "IL-TURKIC"], ["NAT-055", "IL-TURKIC"], ["NAT-047", "IL-TURKIC"], ["NAT-048", "IL-TURKIC"],
  ["NAT-058", "IL-PDT"], ["NAT-049", "IL-PDT"],
  ["NAT-073", "IL-NGUNI"], ["NAT-074", "IL-NGUNI"], ["EXP-025", "IL-NGUNI"],
  ["EXP-018", "IL-MANDING"], ["EXP-019", "IL-SOTHO"],
];
for (const [topId, ilId] of expectedExactPairs) {
  const row = outputRows.find((r) => r.intervention_id === topId);
  assert(Boolean(row), `Expected Top-100 intervention missing: ${topId}`);
  assert(row?.interlanguage_intervention_id === ilId, `Expected ${topId} -> ${ilId}; found ${row?.interlanguage_intervention_id || "blank"}`);
  assert(row?.overlap_relation_status === "exact_profile_match", `${topId} must be an exact profile match`);
}

const exactCount = outputRows.filter((r) => r.overlap_relation_status === "exact_profile_match").length;
const scopedCount = outputRows.filter((r) => r.overlap_relation_status === "exact_language_script_and_target_country_cell").length;
const hypothesisOnlyCount = outputRows.filter((r) => r.overlap_relation_status === "hypothesis_only_language_script_match_territory_unresolved").length;
const unmappedCount = outputRows.filter((r) => r.overlap_relation_status === "no_exact_relation_in_current_matrix").length;

assert(outputRows.length === 100, `Crosswalk row count must be 100; found ${outputRows.length}`);
assert(new Set(outputRows.map((r) => r.portfolio_position)).size === 100, "Crosswalk portfolio positions are not unique");
assert(new Set(outputRows.map((r) => r.intervention_id)).size === 100, "Crosswalk intervention IDs are not unique");
assert(exactCount === 16, `Expected 16 exact profile matches; found ${exactCount}`);
assert(scopedCount === 4, `Expected 4 exact language/script + target-country matches; found ${scopedCount}`);
assert(hypothesisOnlyCount === 1, `Expected 1 hypothesis-only unresolved-territory relation; found ${hypothesisOnlyCount}`);
assert(unmappedCount === 79, `Expected 79 unmapped rows; found ${unmappedCount}`);
assert(outputRows.every((r) => r.current_cross_language_demographic_reach_credit === "0"), "Every current cross-language demographic reach credit must be zero");
assert(outputRows.filter((r) => r.named_localized_output_status.startsWith("yes_")).length === 1, "Only the Indonesian row may carry a named localized output in this crosswalk");
const Indonesian = outputRows.find((r) => r.intervention_id === "NAT-121");
assert(Indonesian?.forward_component_deficit_D === "0", "Indonesian Open Logic forward deficit must be D=0");
assert(Indonesian?.current_direct_component_completion_overlap === "722 of 722 Open Logic units complete", "Indonesian completion overlap must be 722 of 722 Open Logic units complete");
assert(outputRows.filter((r) => r.forward_component_deficit_D === "0").length === 1, "Only the Indonesian exact completed baseline may have D=0");
assert(outputRows.filter((r) => r.interlanguage_intervention_id).every((r) => r.interlanguage_source_ids), "Every linked interlanguage row must contain source IDs");

if (failures.length) {
  throw new Error(`Crosswalk validation failed:\n- ${failures.join("\n- ")}`);
}

const headers = Object.keys(outputRows[0]);
const matrix = [headers, ...outputRows.map((row) => headers.map((h) => row[h]))];

const csvText = toCsv(matrix);
await fs.writeFile(outCsv, csvText, "utf8");

const reparsed = parseCsv(await fs.readFile(outCsv, "utf8"));
assert(reparsed.length === 101, `Serialized CSV must reparse to 101 rows including header; found ${reparsed.length}`);
assert(reparsed[0].length === headers.length, `Serialized CSV header width must be ${headers.length}; found ${reparsed[0].length}`);
assert(reparsed.slice(1).every((row) => row.length === headers.length), "Serialized CSV contains a row with the wrong field count");
assert(reparsed[0].every((value, i) => value === headers[i]), "Serialized CSV headers changed on round trip");
assert(reparsed.slice(1).every((row, i) => row.every((value, j) => value === matrix[i + 1][j])), "Serialized CSV values changed on round trip");
if (failures.length) {
  throw new Error(`Post-serialization validation failed:\n- ${failures.join("\n- ")}`);
}

const mappedCounts = Object.entries(outputRows.filter((r) => ["exact_profile_match", "exact_language_script_and_target_country_cell"].includes(r.overlap_relation_status)).reduce((acc, r) => {
  acc[r.interlanguage_intervention_id] = (acc[r.interlanguage_intervention_id] ?? 0) + 1;
  return acc;
}, {})).sort(([a], [b]) => a.localeCompare(b));

const methodText = `# Top-100 interlanguage-overlap crosswalk method

Date: 2026-08-30

## Purpose and boundary

This crosswalk connects every natural-language row in \`TOP_100.csv\` to an existing interlanguage, shared-core, dual-script, or natural-intercomprehension architecture only when the current normalized matrices expose a specific language/profile relation. It is a compute-reuse and overlap-control layer. It is not a family-level demographic multiplier and it does not convert an architecture row into a comprehension claim.

## Authority order

1. \`TOP_100.csv\` fixes the 100 ordered natural-language interventions and exact target-profile tags.
2. \`top100_needs_assignment_v2.csv\` supplies the current needs/program assignment for the same position and intervention ID.
3. \`staging/interlanguage_matrix/interlanguage_overlap_normalized.csv\` supplies the exact edge, language/profile tag, script, territory, exclusions, double-count rule, source IDs, confidence, and current rankability.
4. \`staging/interlanguage_bundle_model/interlanguage_intervention_matrix.csv\` and \`appendix_f_interlanguage_matrix_summary.csv\` provide corroborating architecture and source-ID context.

## Matching rule

- **Exact profile match:** the Top-100 target tag equals the normalized edge tag.
- **Exact language/script and target-country cell:** the edge tag omits only the region suffix and its named territory explicitly contains the Top-100 target country. This adds four relations already represented by named matrix cells: South African Setswana, South African Sesotho, South African siSwati, and Pennsylvania German in exact United States communities.
- **Hypothesis only:** a language/script prefix aligns but the matrix territory is unresolved or incompatible. Official-standard Belarusian is retained in this category because the Interslavic edge says \`exact territory pending\`; it receives no integrability or reach credit.
- **No match:** no fuzzy family-name, typological, regional, or macro-language join is made. Explicit exclusions in the source matrices remain exclusions.

## Three separate quantities

1. **Integrability** records whether an exact component is already named in a reusable engineering architecture. It does not assert that another language's readers understand the output.
2. **Shared-core compute-reuse potential** records plausible reuse of aligned source structure, term graphs, register work, or script handling. No source supplies an empirical token-savings coefficient, so every positive reuse entry is explicitly unquantified.
3. **Current cross-language demographic reach credit** is numeric and equals **0 for all 100 rows**. No blanket family multiplier is applied. A current localized output may establish its own component baseline, but it creates no cross-language demographic credit without an exact named output and a defensible overlap rule.

## Indonesian overlap control

The Indonesian component has a complete named Open Logic output: 722 of 722 units. Its forward Open Logic deficit is therefore \(D=0\). The complete output can be a reusable source asset, but it is existing own-language coverage, not new work, and it provides no automatic Malaysian, Bruneian, Javanese, Sundanese, or other cross-language reach.

## Result counts

- Exact profile matches: ${exactCount}
- Exact language/script plus named target-country matches: ${scopedCount}
- Hypothesis-only unresolved-territory relations: ${hypothesisOnlyCount}
- No exact current matrix relation: ${unmappedCount}
- Total rows: ${outputRows.length}

Mapped exact/country-compatible components by architecture:

${mappedCounts.map(([id, count]) => `- ${id}: ${count}`).join("\n")}

## Interpretation limit

The crosswalk is suitable for portfolio bookkeeping, avoiding duplicate translation, and identifying where shared engineering may save compute. It is not suitable for claiming family-wide comprehension, calculating a demographic reach bonus, or replacing exact language, script, territory, and product outputs.
`;
await fs.writeFile(outMethod, methodText, "utf8");

const sourceInventory = await Promise.all(Object.values(sourcePaths).map(async (p) => {
  const bytes = await fs.readFile(p);
  const stat = await fs.stat(p);
  return { file: rel(p), bytes: stat.size, sha: sha256(bytes) };
}));
const csvBytes = await fs.readFile(outCsv);
const methodBytes = await fs.readFile(outMethod);

const checks = [
  ["Top-100 source rows", topRows.length === 100, `${topRows.length}`],
  ["Needs rows", needsRows.length === 100, `${needsRows.length}`],
  ["Output rows", outputRows.length === 100, `${outputRows.length}`],
  ["Unique portfolio positions", new Set(outputRows.map((r) => r.portfolio_position)).size === 100, "100"],
  ["Unique intervention IDs", new Set(outputRows.map((r) => r.intervention_id)).size === 100, "100"],
  ["Exact positions 1-100", outputRows.map((r) => Number(r.portfolio_position)).sort((a, b) => a - b).every((v, i) => v === i + 1), "pass"],
  ["Exact expected mappings", expectedExactPairs.every(([topId, ilId]) => outputRows.some((r) => r.intervention_id === topId && r.interlanguage_intervention_id === ilId && r.overlap_relation_status === "exact_profile_match")), `${expectedExactPairs.length}/${expectedExactPairs.length}`],
  ["All demographic reach credits zero", outputRows.every((r) => r.current_cross_language_demographic_reach_credit === "0"), "100/100"],
  ["Indonesian completion overlap", Indonesian.current_direct_component_completion_overlap === "722 of 722 Open Logic units complete", Indonesian.current_direct_component_completion_overlap],
  ["Indonesian forward deficit", Indonesian.forward_component_deficit_D === "0", "D=0"],
  ["RFC 4180 round-trip row count", reparsed.length === 101, `${reparsed.length} including header`],
  ["RFC 4180 round-trip field widths", reparsed.every((row) => row.length === headers.length), `${headers.length} fields in every row`],
  ["RFC 4180 round-trip value identity", reparsed.slice(1).every((row, i) => row.every((value, j) => value === matrix[i + 1][j])), "pass"],
];

const receiptText = `# Top-100 interlanguage crosswalk validation receipt

Date: 2026-08-30

## Source inventory

| Task-root-relative file | Bytes | SHA-256 |
|---|---:|---|
${sourceInventory.map((x) => `| \`${x.file}\` | ${x.bytes} | \`${x.sha}\` |`).join("\n")}

## Deterministic validation

| Check | Result | Evidence |
|---|---|---|
${checks.map(([label, ok, evidence]) => `| ${label} | ${ok ? "PASS" : "FAIL"} | ${String(evidence).replaceAll("|", "\\|")} |`).join("\n")}

## Relation counts

| Relation status | Rows |
|---|---:|
| exact_profile_match | ${exactCount} |
| exact_language_script_and_target_country_cell | ${scopedCount} |
| hypothesis_only_language_script_match_territory_unresolved | ${hypothesisOnlyCount} |
| no_exact_relation_in_current_matrix | ${unmappedCount} |
| **Total** | **${outputRows.length}** |

## Output identities

| Task-root-relative file | Bytes | SHA-256 |
|---|---:|---|
| \`${rel(outCsv)}\` | ${csvBytes.length} | \`${sha256(csvBytes)}\` |
| \`${rel(outMethod)}\` | ${methodBytes.length} | \`${sha256(methodBytes)}\` |

The required bundled spreadsheet package was absent from the loader-provided runtime, so the requested CSV was generated with a deterministic RFC 4180 parser/serializer and fully reparsed for value identity. All linked interlanguage rows carry exact source IDs. Every current cross-language demographic reach credit is zero; no family-level multiplier was introduced.
`;
await fs.writeFile(outReceipt, receiptText, "utf8");

const receiptBytes = await fs.readFile(outReceipt);
console.log(JSON.stringify({
  outputs: [
    { file: rel(outCsv), bytes: csvBytes.length, sha256: sha256(csvBytes) },
    { file: rel(outMethod), bytes: methodBytes.length, sha256: sha256(methodBytes) },
    { file: rel(outReceipt), bytes: receiptBytes.length, sha256: sha256(receiptBytes) },
  ],
  counts: { exactCount, scopedCount, hypothesisOnlyCount, unmappedCount, total: outputRows.length },
}));
