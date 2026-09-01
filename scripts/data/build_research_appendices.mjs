import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";

const OUT = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/, "$1"));
const ROOT = path.resolve(OUT, "..", "..");

const INPUTS = {
  candidates: path.join(ROOT, "candidate_interventions_master.csv"),
  cardinal: path.join(ROOT, "portfolio_linguistic_candidates.csv"),
  observations: path.join(ROOT, "population_observations_master.csv"),
  sourceRegister: path.join(ROOT, "population_source_register_public.csv"),
  accessibility: path.join(ROOT, "accessibility_priority_backlog.csv"),
  accessStrata: path.join(ROOT, "staging", "accessibility_recovery", "accessibility_population_strata.csv"),
  curricula: path.join(ROOT, "curriculum_portfolios.csv"),
  depths: path.join(ROOT, "adaptation_depths.csv"),
  top100: path.join(ROOT, "TOP_100.csv"),
  exclusions: path.join(ROOT, "negative_controls_and_profile_exclusions.csv"),
  expansionScores: path.join(ROOT, "candidate_expansion_scores.csv"),
  expansion: path.join(ROOT, "staging", "expand_rankable_candidates", "candidate_expansion.csv"),
  matrix: path.join(ROOT, "staging", "interlanguage_bundle_model", "interlanguage_intervention_matrix.csv"),
  overlap: path.join(ROOT, "staging", "interlanguage_matrix", "interlanguage_overlap_normalized.csv"),
};

function clean(v) {
  return v === null || v === undefined ? "" : String(v).replace(/^\uFEFF/, "");
}

function parseCsvValues(text) {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        cell += ch;
      }
    } else if (ch === '"') {
      quoted = true;
    } else if (ch === ',') {
      row.push(cell);
      cell = "";
    } else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i += 1;
      row.push(cell);
      cell = "";
      if (row.some(value => clean(value) !== "")) rows.push(row);
      row = [];
    } else {
      cell += ch;
    }
  }
  if (cell !== "" || row.length) {
    row.push(cell);
    if (row.some(value => clean(value) !== "")) rows.push(row);
  }
  if (quoted) throw new Error("Unterminated quoted CSV field");
  return rows;
}

async function readCsv(file) {
  const values = parseCsvValues(await fs.readFile(file, "utf8"));
  if (!values.length) return [];
  const headers = values[0].map(clean);
  return values.slice(1).filter(r => r.some(v => clean(v) !== "")).map(row =>
    Object.fromEntries(headers.map((h, i) => [h, clean(row[i])]))
  );
}

function csvEscape(v) {
  const s = clean(v);
  return /[",\r\n]/.test(s) ? `"${s.replaceAll('"', '""')}"` : s;
}

function csvText(rows, columns = null) {
  const cols = columns ?? (rows[0] ? Object.keys(rows[0]) : []);
  return [cols.map(csvEscape).join(","), ...rows.map(r => cols.map(c => csvEscape(r[c])).join(","))].join("\r\n") + "\r\n";
}

function splitIds(value) {
  return clean(value).split(/[;|]/).map(s => s.trim()).filter(Boolean);
}

function unique(values) {
  return [...new Set(values.map(clean).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function joined(values) {
  return unique(values).join(" || ");
}

function md(v) {
  return clean(v).replaceAll("|", "\\|").replace(/[\r\n]+/g, " ");
}

function mdTable(rows, columns) {
  const header = `| ${columns.map(c => md(c.label)).join(" | ")} |`;
  const rule = `| ${columns.map(() => "---").join(" | ")} |`;
  return [header, rule, ...rows.map(r => `| ${columns.map(c => md(r[c.key])).join(" | ")} |`)].join("\n");
}

function indexBy(rows, key) {
  const out = new Map();
  for (const row of rows) {
    if (out.has(row[key])) throw new Error(`Duplicate ${key}: ${row[key]}`);
    out.set(row[key], row);
  }
  return out;
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex").toUpperCase();
}

function n(value) {
  return value === "" ? null : Number(value);
}

function roundPositive(value) {
  return String(Math.floor(value + 0.5));
}

function classifyExisting(status) {
  if (status === "complete_722_of_722_current_program" || status.startsWith("complete_722")) return "covered";
  if (status === "researched only") return "researched";
  if (
    status === "partial_321_of_722" || status === "7 of 722 units" ||
    status === "not systematic programme-wide" || status === "inconsistent across local corpus" ||
    status.startsWith("established Indonesian program") ||
    status.startsWith("complete Open Logic 722 of 722") ||
    status.startsWith("Indonesian Open Logic complete 722 of 722; Malaysian Malay unstarted") ||
    status.includes("complete locally") || status.startsWith("partial exact ") || status.includes("complete and publicly read back") ||
    status.includes("complete; ") || status.startsWith("Indonesian 321") ||
    status.startsWith("Spanish and Brazilian Portuguese")
  ) return "partial";
  if (
    status === "missing" || status === "not_found_in_bounded_local_census" ||
    status === "not present programme-wide" || status === "no local bridge surface" ||
    status.startsWith("missing;") || status.startsWith("unstarted;")
  ) return "missing";
  throw new Error(`Unclassified existing_local_status: ${status}`);
}

await fs.mkdir(OUT, { recursive: true });

const entries = await Promise.all(Object.entries(INPUTS).map(async ([k, p]) => [k, await readCsv(p)]));
const data = Object.fromEntries(entries);

const obsById = indexBy(data.observations, "observation_id");
const sourceById = indexBy(data.sourceRegister, "source_id");
const candidateById = indexBy(data.candidates, "intervention_id");
const strataById = indexBy(data.accessStrata, "stratum_id");
const curriculumById = indexBy(data.curricula, "portfolio_id");
const depthById = indexBy(data.depths, "depth_id");
const expansionScoreById = indexBy(data.expansionScores, "intervention_id");
const expansionById = indexBy(data.expansion, "candidate_id");
const overlapByEdge = indexBy(data.overlap, "edge_id");

// Appendix A: fail-closed reconciliation of registered local evidence.
const deficitRule = {
  covered: "D=0 only for the exact verified target × unit × format; any uncovered curriculum or format remains D=1.",
  partial: "D=0 only on verified covered units/components and D=1 on the residual; no scalar is assigned without a common exact denominator.",
  researched: "Research without delivered target bytes does not reduce the content deficit; D=1 for the missing comparator.",
  dormant: "A dormant item is not credited without verified usable current bytes and build identity; D=1 pending that registered evidence.",
  duplicated: "The canonical item counts once; a duplicate adds no marginal coverage and produces no further reduction in D.",
  missing: "No registered target coverage: D=1 for the declared target × unit × format.",
};

const appendixA = data.candidates.map(row => {
  const state = classifyExisting(row.existing_local_status);
  let verified = "";
  let total = "";
  let residual = "";
  let residualFraction = "";
  let deficit = deficitRule[state];
  if (row.intervention_id === "CMP-ID-ID") {
    verified = "722"; total = "722"; residual = "0"; residualFraction = (0).toFixed(10);
    deficit = "Exact completed baseline: D=0 for all 722 Open Logic units; residual deficit is zero and no forward translation gain may be claimed for this corpus.";
  } else if (row.intervention_id === "IL-ISV") {
    verified = "7"; total = "722"; residual = "715"; residualFraction = (715 / 722).toFixed(10);
    deficit = "Exact local-unit accounting only: D=0 for 7 units and D=1 for 715 remaining units; no demographic bridge credit follows.";
  } else if (row.intervention_id === "NAT-122") {
    verified = "29"; total = "55"; residual = "26"; residualFraction = (26 / 55).toFixed(10);
    deficit = "Mixed exact baseline: D=0 for complete Open Logic 722/722 and Algebra and Trigonometry 2e 94/94; Calculus Volume 1 has 29/55 covered and 26/55 residual. D=1 applies only to the ex-ante equal-basis comparison, never to already completed forward work.";
  }
  return {
    intervention_id: row.intervention_id,
    target_type: row.target_type,
    target_name: row.target_name,
    variety_or_register: row.variety_or_register,
    script: row.script,
    territory_scope: row.territory_scope,
    curriculum_work: row.curriculum_work,
    curriculum_unit: row.curriculum_unit,
    formats: row.formats,
    raw_existing_local_status: row.existing_local_status,
    reconciliation_state: state,
    verified_covered_units: verified,
    declared_total_units: total,
    residual_units: residual,
    residual_deficit_fraction: residualFraction,
    deficit_effect: deficit,
    registered_source_ids: row.source_ids,
    evidence_status: row.evidence_status,
    overlap_rule: row.overlap_rule,
    notes: row.notes,
  };
});

const stateOrder = ["covered", "partial", "researched", "dormant", "duplicated", "missing"];
const stateMeaning = {
  covered: "Exact declared target scope is registered as delivered and verifiable.",
  partial: "At least one exact unit/component is registered, but the declared target scope is incomplete or inconsistent.",
  researched: "Research exists, but no delivered target coverage is registered.",
  dormant: "A prior item is registered as dormant and lacks current usable/build evidence.",
  duplicated: "The same usable target coverage is registered more than once; only a canonical copy may count.",
  missing: "No exact target coverage is registered in the bounded local census.",
};
const appendixAStates = stateOrder.map(state => ({
  reconciliation_state: state,
  registered_row_count: String(appendixA.filter(r => r.reconciliation_state === state).length),
  definition: stateMeaning[state],
  deficit_effect: deficitRule[state],
  evidence_boundary: state === "dormant" || state === "duplicated"
    ? "No rows in the current 211-row register meet this state; retained as an explicit fail-closed rule."
    : "Classification uses only existing_local_status and the declared scope in candidate_interventions_master.csv.",
}));

// Appendix B: one exact observation and source lineage per cardinal row.
const appendixB = data.cardinal.map(c => {
  const obsIds = splitIds(c.population_observation_ids);
  assert(obsIds.length === 1, `${c.intervention_id}: expected one population observation, got ${obsIds.length}`);
  const o = obsById.get(obsIds[0]);
  assert(o, `${c.intervention_id}: missing observation ${obsIds[0]}`);
  const s = sourceById.get(o.source_id);
  assert(s, `${c.intervention_id}: missing source ${o.source_id}`);
  return {
    portfolio_position: c.portfolio_position,
    top100: Number(c.portfolio_position) <= 100 ? "true" : "false",
    intervention_id: c.intervention_id,
    intervention_name: c.intervention_name,
    target_profiles: c.target_profiles,
    territory_or_scope: c.territory_or_scope,
    portfolio_lane: c.portfolio_lane,
    region: o.region,
    subregion: o.subregion,
    observation_id: o.observation_id,
    observation_language_label: o.language_label,
    observation_edition_profile: o.edition_profile,
    observation_territory: o.territory,
    modality: o.modality,
    script_or_profile: o.script_or_profile,
    learner_stratum: o.learner_stratum,
    population_measure: o.measure_type,
    count_unit: o.count_unit,
    population_low: c.population_low,
    population_base: c.population_base,
    population_high: c.population_high,
    source_reported_low: c.source_population_low_reported,
    source_reported_high: c.source_population_high_reported,
    population_interval_status: c.population_interval_status,
    reference_date_or_year: o.reference_date_or_year,
    source_id: o.source_id,
    source_locator: o.source_locator,
    source_observation_transcribed_exactly: o.source_observation_transcribed_exactly,
    source_title: s.title,
    source_authority: s.authority,
    source_type: s.source_type,
    source_tier: c.source_tier,
    source_confidence: c.source_confidence,
    marginal_access_low: c.marginal_access_low,
    marginal_access_base_sensitivity: c.marginal_access_base_sensitivity,
    marginal_access_high: c.marginal_access_high,
    source_limitations: s.limitations,
    local_witness_sha256: s.local_witness_sha256,
    target_mapping_status: o.target_mapping_status,
    overlap_group_id: o.overlap_group_id,
    alternative_measure_role: o.alternative_measure_role,
    existing_edition_overlap_status: o.existing_edition_overlap_status,
    access_factor_status: c.access_factor_status,
    evidence_caveat: c.evidence_caveat,
    observation_caveats: o.caveats,
    aggregation_rule: "Do not sum this row with heterogeneous or overlapping observations as unique people unless an explicit disjoint-universe rule exists.",
  };
});

const regionGroups = new Map();
for (const r of appendixB) {
  const key = `${r.region}\u0000${r.subregion}`;
  if (!regionGroups.has(key)) regionGroups.set(key, []);
  regionGroups.get(key).push(r);
}
const appendixBRegions = [...regionGroups.entries()].map(([key, rows]) => {
  const [region, subregion] = key.split("\u0000");
  return {
    region,
    subregion,
    cardinal_rows: String(rows.length),
    top100_rows: String(rows.filter(r => r.top100 === "true").length),
    portfolio_position_min: String(Math.min(...rows.map(r => Number(r.portfolio_position)))),
    portfolio_position_max: String(Math.max(...rows.map(r => Number(r.portfolio_position)))),
    distinct_source_count: String(unique(rows.map(r => r.source_id)).length),
    source_ids: joined(rows.map(r => r.source_id)),
    measure_types: joined(rows.map(r => r.population_measure)),
    high_confidence_rows: String(rows.filter(r => r.source_confidence === "high").length),
    medium_confidence_rows: String(rows.filter(r => r.source_confidence === "medium").length),
    low_confidence_rows: String(rows.filter(r => r.source_confidence === "low").length),
    tier_1_rows: String(rows.filter(r => r.source_tier === "1").length),
    tier_2_rows: String(rows.filter(r => r.source_tier === "2").length),
    zero_floor_rows: String(rows.filter(r => n(r.marginal_access_low) === 0).length),
    population_aggregation: "not summed: measures, years, territories, and overlap universes may differ",
  };
}).sort((a, b) => `${a.region}|${a.subregion}`.localeCompare(`${b.region}|${b.subregion}`));

const sourceMeasureGroups = new Map();
for (const r of appendixB) {
  const key = [r.region, r.subregion, r.source_id, r.population_measure, r.source_confidence, r.source_tier].join("\u0000");
  if (!sourceMeasureGroups.has(key)) sourceMeasureGroups.set(key, []);
  sourceMeasureGroups.get(key).push(r);
}
const appendixBSources = [...sourceMeasureGroups.entries()].map(([key, rows]) => {
  const [region, subregion, source_id, population_measure, source_confidence, source_tier] = key.split("\u0000");
  return {
    region, subregion, source_id, population_measure, source_confidence, source_tier,
    cardinal_rows: String(rows.length),
    top100_rows: String(rows.filter(r => r.top100 === "true").length),
    reference_dates_or_years: joined(rows.map(r => r.reference_date_or_year)),
    observation_ids: joined(rows.map(r => r.observation_id)),
    source_title: rows[0].source_title,
    source_authority: rows[0].source_authority,
    source_type: rows[0].source_type,
    source_limitations: rows[0].source_limitations,
    population_aggregation: "not summed across rows",
  };
}).sort((a, b) => `${a.region}|${a.subregion}|${a.source_id}|${a.population_measure}`.localeCompare(`${b.region}|${b.subregion}|${b.source_id}|${b.population_measure}`));

// Appendix C: accessibility remains a separate, non-cardinal safeguard portfolio.
const FR2_LOW = 912737;
const FR2_BASE = 4073049;
const FR2_HIGH = 18664571;
const appendixC = data.accessibility.map((a, i) => {
  const s = strataById.get(a.linked_stratum_id);
  assert(s, `${a.edge_id}: missing accessibility stratum ${a.linked_stratum_id}`);
  const hasCost = a.workload_increment_low !== "" && a.workload_increment_base !== "" && a.workload_increment_high !== "";
  return {
    safeguard_order: String(i + 1),
    order_interpretation: i === 0 ? "foundational horizontal requirement" : "deterministic registered backlog order; not an evidence-based cardinal rank",
    edge_id: a.edge_id,
    intervention_id: a.intervention_id,
    intervention_name: a.intervention_name,
    mechanism_class: a.mechanism_class,
    barrier_axis: s.barrier_axis,
    territory: s.territory,
    learner_stratum: s.learner_stratum,
    language_or_modality: s.language_or_modality,
    population_measure: s.measure_type,
    reference_year: s.reference_year,
    source_ceiling_low: s.population_low,
    source_ceiling_point: s.population_base,
    source_ceiling_high: s.population_high,
    ceiling_status: s.denominator_status,
    incremental_access_low: s.marginal_access_low,
    incremental_access_base: s.marginal_access_base,
    incremental_access_high_ceiling: s.marginal_access_high,
    marginal_range_status: s.marginal_range_status,
    overlap_group_id: s.overlap_group_id,
    do_not_sum_with: s.do_not_sum_with,
    existing_access_overlap: s.existing_access_overlap,
    curriculum_scope: a.curriculum_scope,
    adaptation_depth: a.adaptation_depth,
    product_specification: a.product_specification,
    workload_increment_low: a.workload_increment_low,
    workload_increment_base: a.workload_increment_base,
    workload_increment_high: a.workload_increment_high,
    fr2_reference_token_increment_low: hasCost ? roundPositive(FR2_LOW * Number(a.workload_increment_low)) : "",
    fr2_reference_token_increment_base: hasCost ? roundPositive(FR2_BASE * Number(a.workload_increment_base)) : "",
    fr2_reference_token_increment_high: hasCost ? roundPositive(FR2_HIGH * Number(a.workload_increment_high)) : "",
    cost_status: hasCost ? "planning sensitivity from FR-2 gross-token scenarios × registered workload increment; not observed tokens or programme cost" : "no registered workload coefficient; blank is unknown, not zero",
    standards_source_ids: a.standards_source_ids,
    population_source_ids: s.source_id,
    evidence_status: a.evidence_status,
    rank_ready: a.rank_ready,
    portfolio_slot_selected: a.portfolio_slot_selected,
    nonadditivity_caveat: `${a.caveats} ${s.caveats}`.trim(),
  };
});

// Appendix D: exact curriculum/depth definitions and mapping, without duplicating full Top100 scores.
const appendixDPortfolios = data.curricula.map(r => ({ ...r }));
const appendixDDepths = data.depths.map(r => ({ ...r }));
const appendixDMapping = data.top100.sort((a, b) => Number(a.portfolio_position) - Number(b.portfolio_position)).map(t => {
  const next = curriculumById.get(t.recommended_openstax_next_product);
  const depth = depthById.get(t.recommended_openstax_depth);
  assert(next, `${t.intervention_id}: unknown next portfolio ${t.recommended_openstax_next_product}`);
  assert(depth, `${t.intervention_id}: unknown depth ${t.recommended_openstax_depth}`);
  return {
    portfolio_position: t.portfolio_position,
    intervention_id: t.intervention_id,
    intervention_name: t.intervention_name,
    target_profiles: t.target_profiles,
    territory_or_scope: t.territory_or_scope,
    portfolio_lane: t.portfolio_lane,
    first_product_id: "FR-2",
    first_product: t.recommended_first_product,
    first_product_depth: "D2",
    first_product_gross_tokens_low: t.gross_tokens_low,
    first_product_gross_tokens_base: t.gross_tokens_base,
    first_product_gross_tokens_high: t.gross_tokens_high,
    first_product_source_ids: curriculumById.get("FR-2").source_ids,
    next_portfolio_id: next.portfolio_id,
    next_portfolio_name: next.portfolio_name,
    next_portfolio_exact_content: next.exact_content,
    next_depth_id: depth.depth_id,
    next_depth_name: depth.name,
    next_gross_tokens_low: t.openstax_next_gross_tokens_low,
    next_gross_tokens_base: t.openstax_next_gross_tokens_base,
    next_gross_tokens_high: t.openstax_next_gross_tokens_high,
    next_portfolio_source_ids: next.source_ids,
    population_source_ids: t.population_source_ids,
    profile_authority_source_ids: t.profile_authority_source_ids,
    mapping_caveat: "Legacy fixed-source workload comparator only; not a population-specific curriculum recommendation. Token values are gross planning sensitivities, not fresh-token billing or observed cost.",
  };
});

// Appendix E: exactly three unresolved profile rows plus two D0 mismatch rows.
const unresolvedControls = data.exclusions.filter(r => ["unresolved_localized_output_profile", "not_recommendation_eligible"].includes(r.control_or_exclusion));
const evidenceSought = {
  "OBS-GRG-US-004": "Community-specific Eastern Keres variety, script, orthography, educational-standard authority, and a nonmultiplying population-to-output join.",
  "OBS-GRG-US-012": "Pueblo-specific Tewa variety, script, orthography, educational-standard authority, and a nonmultiplying population-to-output join.",
  "OBS-GRG-US-027": "Exact institutional teaching orthography and an audience split between a shared core and localized profiles without multiplying GRG-US-027.",
  "EXP-002": "Exact production-variety/standard mapping within the PBS Pushto umbrella and a population-to-profile join that does not assign the whole category to one variety.",
  "EXP-012": "Exact production-variety/standard mapping within the CSA Oromigna category, with cross-border populations excluded unless separately and disjointly evidenced.",
};
const appendixE = unresolvedControls.map(r => {
  if (r.control_or_exclusion === "unresolved_localized_output_profile") {
    const c = candidateById.get(r.intervention_id);
    const o = obsById.get(r.population_observation_id);
    const s = sourceById.get(r.population_source_id);
    assert(c && o && s, `${r.intervention_id}: unresolved profile join failed`);
    return {
      intervention_id: r.intervention_id,
      issue_class: "unresolved_localized_output_profile",
      target_name: r.target_name,
      target_profile: r.target_profile,
      resolved_edition_name: c.resolved_edition_name,
      territory: r.territory,
      population_low: o.population_low,
      population_base: o.population_base,
      population_high: o.population_high,
      population_measure: o.measure_type,
      population_reference_year: o.reference_date_or_year,
      population_observation_id: o.observation_id,
      population_source_id: o.source_id,
      population_source_locator: o.source_locator,
      profile_source_ids: c.profile_source_ids,
      profile_resolution_status: c.profile_resolution_status,
      nonranking_reason: r.basis,
      evidence_sought: evidenceSought[r.intervention_id],
      rankability_status: c.rankability_status,
      confidence: s.confidence,
      caveat: `${c.evidence_status} ${c.overlap_rule}`,
    };
  }
  const e = expansionScoreById.get(r.intervention_id);
  const x = expansionById.get(r.intervention_id);
  assert(e && x, `${r.intervention_id}: D0 join failed`);
  return {
    intervention_id: r.intervention_id,
    issue_class: "D0_profile_population_mismatch",
    target_name: r.target_name,
    target_profile: r.target_profile,
    resolved_edition_name: e.resolved_edition_name,
    territory: r.territory,
    population_low: e.population_low,
    population_base: e.population_base,
    population_high: e.population_high,
    population_measure: e.population_measure,
    population_reference_year: e.population_reference_year,
    population_observation_id: e.observation_id,
    population_source_id: e.population_source_id,
    population_source_locator: e.population_source_locator,
    profile_source_ids: x.profile_source_ids,
    profile_resolution_status: e.profile_resolution_status,
    nonranking_reason: `${r.basis}; ${x.population_profile_fit}`,
    evidence_sought: evidenceSought[r.intervention_id],
    rankability_status: e.recommendation_eligibility,
    confidence: x.combined_confidence,
    caveat: `${x.additivity_rule} ${x.uncertainty}`,
  };
}).sort((a, b) => a.intervention_id.localeCompare(b.intervention_id));

// Appendix F: aggregate only the 80 interlanguage rows; the 24 accessibility rows remain separate.
const accessibilityMechanisms = new Set(["accessibility_derivative", "signed_language_access"]);
const ilRows = data.matrix.filter(r => !accessibilityMechanisms.has(r.mechanism_class));
const accessRows = data.matrix.filter(r => accessibilityMechanisms.has(r.mechanism_class));
const ilGroups = new Map();
for (const r of ilRows) {
  if (!ilGroups.has(r.intervention_id)) ilGroups.set(r.intervention_id, []);
  ilGroups.get(r.intervention_id).push(r);
}
const appendixF = [...ilGroups.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([id, rows]) => {
  const overlaps = rows.map(r => overlapByEdge.get(r.matrix_row_id));
  assert(overlaps.every(Boolean), `${id}: one or more matrix rows lack normalized overlap joins`);
  const taskBits = unique(rows.flatMap(r => {
    if (!r.tested_task && !r.observed_task_score && !r.observed_task_type) return [];
    return [`${r.tested_task || "task unspecified"}${r.observed_task_type ? ` [${r.observed_task_type}]` : ""}${r.observed_task_score ? ` score=${r.observed_task_score}` : ""}`];
  }));
  return {
    intervention_id: id,
    matrix_row_count: String(rows.length),
    mechanism_classes: joined(rows.map(r => r.mechanism_class)),
    exact_communities_or_varieties: joined(rows.map(r => r.target_community_or_variety)),
    language_or_profile_tags: joined(rows.map(r => r.language_or_profile_tag)),
    scripts: joined(rows.map(r => r.script)),
    territory_scopes: joined(rows.map(r => r.territory_scope)),
    coverage_modes: joined(rows.map(r => r.coverage_mode)),
    tested_task_evidence: taskBits.length ? taskBits.join(" || ") : "none registered for an exact sustained mathematical-comprehension task",
    observed_task_scores: joined(rows.map(r => r.observed_task_score)),
    prior_study_required_statements: joined(overlaps.map(r => r.prior_study_required)),
    receptive_or_productive_evidence: joined(overlaps.map(r => r.receptive_or_productive)),
    existing_edition_overlap: joined(rows.map(r => r.existing_edition_overlap)),
    exclusions: joined(rows.map(r => r.communities_excluded)),
    double_count_rules: joined(rows.map(r => r.double_count_rule)),
    direct_comprehension_source_ids: joined(rows.flatMap(r => splitIds(r.direct_comprehension_source_ids))),
    all_source_ids: joined(rows.flatMap(r => splitIds(r.source_ids))),
    confidence_values: joined(rows.map(r => r.confidence)),
    rankable_under_current_evidence: rows.every(r => r.rankable_under_current_evidence === "true") ? "true" : "false",
    scope_warning: "Component rows and population ceilings are nonadditive; no family reach is inferred from the intervention name.",
  };
});

const mechanismRows = [...new Set(data.matrix.map(r => r.mechanism_class))].sort().map(mechanism => {
  const rows = data.matrix.filter(r => r.mechanism_class === mechanism);
  return {
    scope: `mechanism:${mechanism}`,
    matrix_rows: String(rows.length),
    distinct_intervention_ids: String(unique(rows.map(r => r.intervention_id)).length),
    inclusion_rule: accessibilityMechanisms.has(mechanism) ? "accessibility appendix; excluded from interlanguage summary" : "included in interlanguage summary",
  };
});
const appendixFScope = [
  { scope: "all_registered_matrix_rows", matrix_rows: String(data.matrix.length), distinct_intervention_ids: String(unique(data.matrix.map(r => r.intervention_id)).length), inclusion_rule: "complete matrix identity" },
  { scope: "interlanguage_summary", matrix_rows: String(ilRows.length), distinct_intervention_ids: String(ilGroups.size), inclusion_rule: "constructed bridge, dual-script register, natural intercomprehension reuse, or pluricentric shared core" },
  { scope: "accessibility_separate", matrix_rows: String(accessRows.length), distinct_intervention_ids: String(unique(accessRows.map(r => r.intervention_id)).length), inclusion_rule: "accessibility derivative or signed-language access; handled in Appendix C" },
  ...mechanismRows,
];

const outputs = new Map();
function addCsv(name, rows) { outputs.set(name, csvText(rows)); }
addCsv("appendix_a_existing_work_reconciliation.csv", appendixA);
addCsv("appendix_a_state_definitions.csv", appendixAStates);
addCsv("appendix_b_global_gap_map.csv", appendixB);
addCsv("appendix_b_regional_gap_summary.csv", appendixBRegions);
addCsv("appendix_b_source_measure_confidence.csv", appendixBSources);
addCsv("appendix_c_accessibility_safeguards.csv", appendixC);
addCsv("appendix_d_curriculum_portfolios.csv", appendixDPortfolios);
addCsv("appendix_d_adaptation_depths.csv", appendixDDepths);
addCsv("appendix_d_top100_curriculum_mapping.csv", appendixDMapping);
addCsv("appendix_e_unresolved_profiles_and_d0.csv", appendixE);
addCsv("appendix_f_interlanguage_matrix_summary.csv", appendixF);
addCsv("appendix_f_matrix_scope_counts.csv", appendixFScope);

const mapCounts = Object.fromEntries(
  [...new Set(appendixDMapping.map(r => `${r.next_portfolio_id}|${r.next_depth_id}`))].sort().map(k => [k, appendixDMapping.filter(r => `${r.next_portfolio_id}|${r.next_depth_id}` === k).length])
);
const stateCounts = Object.fromEntries(appendixAStates.map(r => [r.reconciliation_state, Number(r.registered_row_count)]));

const validations = [
  [data.candidates.length === 211, `candidate register rows = ${data.candidates.length} (expected 211)`],
  [appendixA.length === 211, `Appendix A rows = ${appendixA.length}`],
  [JSON.stringify(stateCounts) === JSON.stringify({covered:1,partial:19,researched:2,dormant:0,duplicated:0,missing:189}), `Appendix A state counts = ${JSON.stringify(stateCounts)}`],
  [data.cardinal.length === 135, `cardinal natural-language rows = ${data.cardinal.length} (expected 135)`],
  [appendixB.length === 135, `global gap rows = ${appendixB.length}`],
  [appendixB.filter(r => r.top100 === "true").length === 100, `global gap Top100 rows = ${appendixB.filter(r => r.top100 === "true").length}`],
  [data.top100.length === 100, `TOP_100 rows = ${data.top100.length}`],
  [data.top100.every(r => r.intervention_type === "natural_language_edition"), "TOP_100 contains only natural-language editions"],
  [data.top100.every(r => r.output_count === "1"), "TOP_100 output_count is one for every target"],
  [data.top100.every((r, i) => Number(r.portfolio_position) === i + 1), "TOP_100 positions are exactly 1 through 100"],
  [JSON.stringify(mapCounts) === JSON.stringify({"MV-1|D2":36,"MV-1|D3":42,"SB-1|D3":22}), `curriculum mapping counts = ${JSON.stringify(mapCounts)}`],
  [appendixC.length === 11, `accessibility safeguard rows = ${appendixC.length}`],
  [appendixC.every(r => r.rank_ready === "false" && r.portfolio_slot_selected === "false"), "all accessibility safeguards remain non-cardinal and unselected"],
  [appendixE.length === 5, `unresolved/D0 rows = ${appendixE.length}`],
  [appendixE.filter(r => r.issue_class === "unresolved_localized_output_profile").length === 3, "three unresolved localized-output profiles"],
  [appendixE.filter(r => r.issue_class === "D0_profile_population_mismatch").length === 2, "two D0 profile/population mismatches"],
  [data.matrix.length === 104, `full intervention matrix rows = ${data.matrix.length}`],
  [ilRows.length === 80 && ilGroups.size === 15, `interlanguage subset = ${ilRows.length} rows / ${ilGroups.size} IDs`],
  [accessRows.length === 24 && unique(accessRows.map(r => r.intervention_id)).length === 18, `accessibility subset = ${accessRows.length} rows / ${unique(accessRows.map(r => r.intervention_id)).length} IDs (IL-AR occurs in both mechanism scopes)`],
  [ilRows.every(r => overlapByEdge.has(r.matrix_row_id)), "all 80 interlanguage rows join to normalized overlap evidence"],
  [ilRows.every(r => r.rankable_under_current_evidence === "false"), "all 80 interlanguage rows are non-rankable under current evidence"],
];
assert(validations.every(([ok]) => ok), `Validation failure:\n${validations.filter(([ok]) => !ok).map(([,m]) => m).join("\n")}`);

const manuscript = `# Research appendices: registered evidence, gaps, safeguards, curricula, exclusions, and interlanguage overlap

These appendices are a manuscript-ready view of the exact current local tables. They do not add unregistered population evidence. Population counts are preserved with their original measures, years, source IDs, and caveats. Heterogeneous or overlapping cells are not summed as unique people. Accessibility remains a separate, non-cardinal axis. Interlanguage components are never relabeled as family reach.

## Appendix A. Existing-work reconciliation and deficit effect

${mdTable(appendixAStates, [
  {key:"reconciliation_state",label:"State"},{key:"registered_row_count",label:"Rows"},{key:"definition",label:"Registered meaning"},{key:"deficit_effect",label:"Deficit effect"},{key:"evidence_boundary",label:"Boundary"}
])}

The exact unit-denominator cases include complete Indonesian Open Logic (722/722; zero residual), complete mainland Simplified Chinese Open Logic (722/722; zero residual), complete mainland Simplified Chinese Algebra and Trigonometry 2e (94/94; zero residual), partial mainland Simplified Chinese Calculus Volume 1 (29/55; 26-module residual), and Interslavic local production (7/722 covered; 715/722 residual, D = ${(715/722).toFixed(10)}). Indonesian and Chinese complete components are retained to prevent double counting, not as forward completion candidates. Interslavic unit coverage does not establish cross-language demographic reach. All other partial rows remain component-level because the register supplies no common scalar denominator. The detailed 211-row reconciliation is machine-readable in \`appendix_a_existing_work_reconciliation.csv\`.

## Appendix B. Global regional, source, measure, and confidence gap map

${mdTable(appendixBRegions, [
  {key:"region",label:"Region"},{key:"subregion",label:"Subregion"},{key:"cardinal_rows",label:"Cardinal rows"},{key:"top100_rows",label:"Top100"},{key:"distinct_source_count",label:"Sources"},{key:"measure_types",label:"Measures"},{key:"high_confidence_rows",label:"High"},{key:"medium_confidence_rows",label:"Medium"},{key:"population_aggregation",label:"Aggregation rule"}
])}

The global detail table has one row for each of the 135 cardinal natural-language interventions and an exact join to one population observation and its registered source. The source/measure/confidence table preserves source-level groupings. Counts in this appendix describe records and coverage strata; they are not summed population claims.

## Appendix C. Ordered accessibility safeguard portfolio

Only safeguard 1 has foundational priority. Items 2–11 retain the deterministic registered backlog order and are not evidence-based cardinal ranks. Every access-gain interval has a conservative zero floor or no defensible denominator. Token increments are FR-2 reference sensitivities, not observed usage, billing, or whole-programme cost.

${mdTable(appendixC, [
  {key:"safeguard_order",label:"Order"},{key:"intervention_name",label:"Safeguard"},{key:"barrier_axis",label:"Barrier"},{key:"territory",label:"Stratum"},{key:"source_ceiling_high",label:"Source ceiling"},{key:"marginal_range_status",label:"Gain status"},{key:"fr2_reference_token_increment_base",label:"FR-2 base-token increment"},{key:"product_specification",label:"Product"},{key:"do_not_sum_with",label:"Nonadditivity"},{key:"population_source_ids",label:"Population source"}
])}

## Appendix D. Curriculum portfolios, adaptation depths, and Top100 mapping

### D1. Exact curriculum portfolios

${mdTable(appendixDPortfolios, [
  {key:"portfolio_id",label:"ID"},{key:"portfolio_name",label:"Portfolio"},{key:"source_project",label:"Project"},{key:"exact_content",label:"Exact content"},{key:"raw_units",label:"Units"},{key:"source_alpha_tokens",label:"Source tokens"},{key:"preferred_depth",label:"Preferred depth"},{key:"prerequisite_portfolio",label:"Prerequisite"},{key:"source_ids",label:"Sources"},{key:"notes",label:"Caveat"}
])}

### D2. Exact adaptation depths

${mdTable(appendixDDepths, [
  {key:"depth_id",label:"ID"},{key:"name",label:"Depth"},{key:"included_components",label:"Included components"},{key:"workload_multiplier_low",label:"Low"},{key:"workload_multiplier_base",label:"Base"},{key:"workload_multiplier_high",label:"High"},{key:"educational_status",label:"Status"},{key:"notes",label:"Caveat"}
])}

### D3. Legacy fixed-source Top100 workload mapping

This mapping intentionally omits the full score fields already present in \`TOP_100.csv\`. It preserves the ordered target identity and the older uniform curriculum assignment solely as a reproducible compute sensitivity. It is not a claim that the named book is the first missing product in every population. The distribution is MV-1/D2 = 36, MV-1/D3 = 42, and SB-1/D3 = 22. SB-1 means **MV-1 plus Introductory Statistics 2e**. Commissioning decisions use \`top100_needs_assignment_v2.csv\` instead: all 100 rows now have a territory- and stage-specific first-product or bounded-audit assignment, with confidence and caveats preserved.

${mdTable(appendixDMapping, [
  {key:"portfolio_position",label:"Pos."},{key:"intervention_id",label:"ID"},{key:"intervention_name",label:"Target"},{key:"target_profiles",label:"Profile"},{key:"portfolio_lane",label:"Lane"},{key:"first_product_id",label:"First"},{key:"first_product_depth",label:"First depth"},{key:"next_portfolio_id",label:"Next"},{key:"next_depth_id",label:"Next depth"},{key:"next_portfolio_exact_content",label:"Next exact content"},{key:"population_source_ids",label:"Population source"}
])}

## Appendix E. Unresolved output profiles and D0 exclusions

${mdTable(appendixE, [
  {key:"intervention_id",label:"ID"},{key:"issue_class",label:"Issue"},{key:"target_name",label:"Target"},{key:"target_profile",label:"Profile"},{key:"population_base",label:"Source population"},{key:"population_measure",label:"Measure"},{key:"population_reference_year",label:"Year"},{key:"population_source_id",label:"Population source"},{key:"nonranking_reason",label:"Why excluded"},{key:"evidence_sought",label:"Evidence sought"}
])}

These are exclusions from recommendation ranking, not claims that the communities lack educational need. The two D0 rows retain source population cells but do not assign them to an exact production profile.

## Appendix F. Interlanguage overlap matrix summary

The complete registered matrix contains 104 rows: 80 interlanguage rows across 15 intervention IDs and 24 accessibility rows across 18 IDs. IL-AR occurs in both mechanism scopes, so those ID counts are nonadditive and reconcile to 32 distinct IDs overall. Appendix F summarizes only the 80 interlanguage rows; Appendix C handles accessibility. Every interlanguage component remains non-rankable under current evidence, and every demographic or component subtotal is nonadditive unless an explicit disjoint-universe rule says otherwise.

${mdTable(appendixF, [
  {key:"intervention_id",label:"ID"},{key:"mechanism_classes",label:"Mechanism"},{key:"matrix_row_count",label:"Rows"},{key:"exact_communities_or_varieties",label:"Exact communities/varieties"},{key:"scripts",label:"Scripts"},{key:"tested_task_evidence",label:"Task evidence"},{key:"prior_study_required_statements",label:"Prior-study evidence"},{key:"existing_edition_overlap",label:"Existing-edition overlap"},{key:"exclusions",label:"Exclusions"},{key:"double_count_rules",label:"Double-count rule"}
])}

The Interslavic short-cloze evidence remains a task-specific observed result; it is not a sustained mathematics-comprehension estimate and is never multiplied by a Slavic-family demographic total.
`;
outputs.set("MANUSCRIPT_APPENDICES.md", manuscript);

const validationObject = {
  generated_utc: new Date().toISOString(),
  scope: "bounded appendix completion from exact current local registered tables",
  central_files_modified: false,
  checks: validations.map(([passed, description]) => ({ passed, description })),
  counts: {
    existing_work_rows: appendixA.length,
    existing_work_states: stateCounts,
    cardinal_gap_rows: appendixB.length,
    top100_rows: appendixDMapping.length,
    accessibility_safeguards: appendixC.length,
    unresolved_profiles_and_d0: appendixE.length,
    full_matrix_rows: data.matrix.length,
    interlanguage_matrix_rows: ilRows.length,
    interlanguage_ids: ilGroups.size,
    accessibility_matrix_rows: accessRows.length,
    accessibility_matrix_ids: unique(accessRows.map(r => r.intervention_id)).length,
  },
  caveats: [
    "Population observations retain heterogeneous measures, years, source universes, and overlap rules; no regional population totals are calculated.",
    "Base, optimistic, scarcity-adjusted, and token values are sensitivities where labelled, not measured harmed-population counts or fresh-token billing.",
    "The conservative marginal-access floor is zero throughout the cardinal sensitivity model and is therefore globally degenerate.",
    "Accessibility is separate and non-cardinal; source ceilings do not identify newly served users.",
    "Constructed bridges and shared-core components are never counted as family reach without exact task and population joins.",
  ],
};
outputs.set("VALIDATION.json", JSON.stringify(validationObject, null, 2) + "\n");
outputs.set("VALIDATION.md", `# Validation report\n\n${validations.map(([ok, d]) => `- ${ok ? "PASS" : "FAIL"}: ${d}`).join("\n")}\n\nCentral files modified: **no**.\n\nThe build preserves source measures, years, IDs, and caveats; it does not sum heterogeneous population cells. Accessibility remains separate/non-cardinal, and interlanguage component reach remains nonadditive.\n`);

for (const [name, text] of outputs) await fs.writeFile(path.join(OUT, name), text, "utf8");

// Parse every generated CSV through the same RFC-4180-aware state machine as an
// independent structural check. This keeps the bounded appendix build independent of
// optional workspace-only JavaScript packages.
const csvValidation = [];
for (const [name, text] of outputs) {
  if (!name.endsWith(".csv")) continue;
  const values = parseCsvValues(text);
  csvValidation.push({ file: name, header_columns: values[0].length, data_rows: values.length - 1, parse_ok: true });
}
validationObject.csv_parse_validation = csvValidation;
outputs.set("VALIDATION.json", JSON.stringify(validationObject, null, 2) + "\n");
await fs.writeFile(path.join(OUT, "VALIDATION.json"), outputs.get("VALIDATION.json"), "utf8");

const inputManifest = [];
for (const [key, file] of Object.entries(INPUTS)) {
  const bytes = await fs.readFile(file);
  inputManifest.push({ key, absolute_path: file, bytes: bytes.length, sha256: sha256(bytes) });
}
const outputManifest = [];
for (const name of outputs.keys()) {
  const file = path.join(OUT, name);
  const bytes = await fs.readFile(file);
  outputManifest.push({ file: name, absolute_path: file, bytes: bytes.length, sha256: sha256(bytes) });
}
const manifest = {
  generated_utc: new Date().toISOString(),
  build_script: path.join(OUT, "build_research_appendices.mjs"),
  authority_boundary: "read exact registered local tables; write staging/research_appendices_completion only",
  inputs: inputManifest,
  outputs_excluding_this_manifest: outputManifest,
};
await fs.writeFile(path.join(OUT, "MANIFEST.sha256.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");

console.log(JSON.stringify({
  out: OUT,
  counts: validationObject.counts,
  csv_validation: csvValidation,
  output_hashes: outputManifest,
}, null, 2));
