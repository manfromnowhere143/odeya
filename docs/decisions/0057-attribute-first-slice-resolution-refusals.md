# ADR 0057: Attribute every first-slice-resolution refusal to its intended invariant

- Status: Executed; third of the six unattributed suites
- Date: 2026-07-18
- Decision owners: architecture review, first-slice resolution
- Gate effect: the C1–C8 conflict suite binds each of its 21 known-bad
  cases to the exact invariant that must refuse it, with a fail-closed
  self-test on every run

## What changed

Each adversarial case declares `expected_refusal_contains` — the
lifecycle suite's spelling, since these checkers are authored here and
their messages are contract text. Every binding names the case's stated
intent: the C1 settlement cases bind their money/dimension invariants,
the C5 assignment cases bind their specific obligation or the
13-event-cohort law, the C7 case binds the sole-reducer-authority rule,
the C8 cases bind their recovery-frontier conditions. The binding check
is factored so the live evaluation and the self-test share one
function; the self-test tampers a real case both ways (misdeclared,
undeclared) on every run and fails closed, and an external negative
control was exercised against the committed suite before retention.

Where a case co-fires several invariants (the C5 cohort cases), the
declared binding is the intent-central one; the others remain exercised
but unbound. Statement- or condition-level mutation of these checkers,
in the lifecycle-audit style, is not extended here and remains open
work if these models graduate into the audited set.

## Boundary

Three suites remain unattributed — `cognitive-contracts` (107),
`projection-contracts` (37), `constitutional-construction` (29), counts
to be re-measured when attributed. The vocabulary convergence follows.
Nothing here is registry admission, activation, Gate A acceptance, or
runtime authority.
