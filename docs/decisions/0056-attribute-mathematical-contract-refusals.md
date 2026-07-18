# ADR 0056: Attribute every mathematical-contract refusal to its intended constraint

- Status: Executed; second of the six unattributed suites
- Date: 2026-07-18
- Decision owners: architecture review, statistical/scientific contracts
- Gate effect: both refusal domains of the mathematical-contract suite —
  structural schema validation and the bounded semantic checkers — now
  bind every known-bad case to the exact constraint that must refuse it,
  with a four-way fail-closed self-test on every run

## The measure, corrected

The handoff carried this suite as 19 unattributed cases. The measured
truth is larger: 20 structurally known-bad cases and 17 semantically
known-bad cases, 37 in all, because a case whose subject is structurally
valid but semantically forbidden is its own refusal domain. The stale
count is corrected rather than preserved.

## The attribution

Structural known-bad cases declare `expected_refusal` — instance JSON
Pointer plus schema keyword, the ADR 0055 spelling: the unknown-as-zero
ban binds `/decision_rule/unknown_treated_as_zero` by `const`, the
timestamp profile binds its exact path by `pattern`, the
affirmative-recomputation rule binds `/recomputation/status` by `const`.
Semantic known-bad cases declare `expected_semantic_refusal_contains` —
a message substring, the lifecycle suite's spelling, because the bounded
semantic checkers are authored in this repository and their messages are
part of the contract: reversed intervals, p-values outside the unit
interval, missingness arithmetic, sequential-look overruns, mission and
protocol chain mismatches, and the crossing-zero sentinels each bind
their own message.

Every binding was chosen from the case's stated intent, not copied from
observed behavior. The harness refuses an undeclared or misdeclared
case in either domain; the self-test tampers a real case four ways
(structural misdeclared/undeclared, semantic misdeclared/undeclared) on
every run and fails closed; external negative controls exercised both
domains against the committed suite before retention.

## Boundary

Four suites and roughly 194 known-bad cases remain unattributed —
`cognitive-contracts` (107), `projection-contracts` (37),
`constitutional-construction` (29), `first-slice-resolution` (21) — with
their per-suite counts to be re-measured, not trusted, when each is
attributed. The vocabulary convergence follows. Nothing here is
scientific authority, an independent review, or Gate A acceptance.
