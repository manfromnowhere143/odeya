# ADR 0058: Attribute every constitutional-construction refusal to its intended invariant

- Status: Executed; fourth of the six unattributed suites
- Date: 2026-07-18
- Decision owners: architecture review, constitutional construction
- Gate effect: all 29 known-bad construction/equality cases bind the
  exact invariant that must refuse them, with a fail-closed self-test on
  every run

## What changed

Each reject case declares `expected_refusal_contains`, bound from
stated intent: the phase-order law, the core-digest evidence binding,
the P0/activation digest equalities, the witness distinctness rules,
the command-surface equalities, the R0/R1 recovery ceiling, the
recovery-quorum bound, and the critical-role separation each bind their
own authored message; the three cases whose only refusal is a schema
`const`/`additionalProperties` violation bind that violation's exact
location text. The binding function is shared by live evaluation and
the self-test, which tampers a real case both ways on every run and
fails closed; an external negative control was exercised against the
committed suite before retention.

## Boundary

Two suites remain unattributed — `cognitive-contracts` (107) and
`projection-contracts` (37), counts to be re-measured when attributed —
followed by the vocabulary convergence. Nothing here constructs P0,
activates anything, or accepts Gate A.
