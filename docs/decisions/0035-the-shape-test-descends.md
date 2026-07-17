# ADR 0035: The shape test descends

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review
- Gate effect: makes the decimal detector's shape test recurse through unions
  and array items, restates the migration total as 1,222 and the D3 table as
  127 fully-proposed rows, and corrects four proposal labels; resolves no
  finding and accepts no Gate A row

## Context

The delta review of the second detector correction confirmed the twenty-nine
rescued rows and the four honesty fixes, then found what ADR 0034's own
Non-decisions predicted: a third structural blind spot. The shape test
examined only the property node itself, so a nullable decimal inside
`oneOf`/`anyOf` was invisible, and an array of decimals was invisible.

The consequences were not marginal. `uncertainty-budget` — covariance and
correlation matrices up to 64×64, coverage factors, coverage probabilities —
carried **zero** findings. `grounded-outcome`'s nine-field resource
observation family, the exact family the previous correction proudly captured
in two other schemas, was missed in its third home. Four uncertainty `level`
fields and a displayed `numeric_value` were ungoverned. An operator signing
the 84-row table would still not have been deciding the decimal question.

The review also flagged two proposal-label defects of the class the previous
review had corrected: `model_tokens` proposed `0_exact, certain` while the
schema bytes permit fractional tokens (downgraded to `likely`, the same
bytes-versus-claim standard applied to the money rows), and two projection
interval rows described a referenced unit as an inline unit object.

## Decision

Replace the flat shape test with `decimal_shape`: a recursion that follows
`oneOf`/`anyOf` branches and array `items` to bounded depth, excludes datetime
at every level (ADR 0033's rule, enforced wherever the pattern heuristic
runs), and widens the reference whitelist to every decimal-family definition
name. Regenerate the audit: NUMBER-001 is 129, the migration total is 1,222,
and the D3 table is 127 rows.

All forty-three rescued rows were proposed from their schema context. Most are
base-property twins of rows already proposed through `allOf/then` branches and
mirror them exactly. The genuinely new content: the resource-observation
family mirrors the budget family as observations; `coverage_probability` is an
interval confidence level; `correlation_coefficient` and `coverage_factor`
join the vocabulary as dimensionless quantities; and `covariance_matrix`
defers to the operator, because a covariance element's unit is a pairwise
product of component units and that unit algebra is a real decision, not an
annotation.

## Non-decisions

This decision does not claim the detector is finished. Three corrections in
one day is evidence about the instrument class, not proof the fourth defect
does not exist; the recursion depth is bounded and the name filter is still a
heuristic. It does not accept any class or row, register any domain, or close
PRQ-001.

## Consequences

The migration total's full history is 1,154, 1,150, 1,179, 1,222 — every move
the instrument approaching the schemas, every one found by reading bytes in
context rather than trusting counts, two by independent reviewers and one by
a proposing pass. The D3 table now governs every decimal leaf the shape test
can reach, including the two scientific schemas that previously did not exist
to it.

The termination question is honest work, not optimism: the current test
descends unions and arrays because a reviewer enumerated what a name-blind
sweep found. The next reviewer should run the same sweep; when it returns
empty against the retained table, the decimal question is closed by
measurement rather than by fatigue.
