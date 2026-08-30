# Population observation and reach rules

The population evidence layer answers, “What exact quantity did this source
report?” The intervention edge answers, “What fraction of that observation can
this exact educational edition newly serve?” These are deliberately separate.

## Population observation fields

- Source identity, year, territory, printed label, measure type, count unit,
  and low/base/high source interval.
- Whether the source label and count were transcribed exactly.
- Whether the observation is a person count, household count, ethnicity/tribe
  proxy, displacement proxy, oral-ability measure, home-use measure, or
  multiple-response measure.
- Nesting and alternative-measure groups so the same people are not summed.

## Intervention edge fields

- Exact language/variety/register, script/orthography, territory, modality,
  and curriculum portfolio.
- `target_fit`: the share of the source category addressed by that exact
  edition.
- `written_or_modality_access`: literacy, signed-video access, audio access, or
  another relevant delivery fit.
- `academic_nonoverlap`: the share not already comfortably served in an
  academic lingua franca.
- `edition_nonoverlap`: the share not already comfortably served by an
  existing local edition.
- `portfolio_residual`: the share not already claimed by another selected
  intervention on the same language × curriculum × accessibility axis.
- `comprehension`: direct comprehension for the exact natural-language or
  evidence-bounded bridge surface; unknown bridge comprehension is zero in the
  conservative scenario.

The marginal reach calculation uses the source observation only after these
edge terms are applied. Exact census precision is therefore preserved without
pretending that a census count is an exact count of newly comfortable readers.
