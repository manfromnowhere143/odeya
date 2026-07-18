# ADR 0081: The fourth zero-coverage suite, and naming the terminal turtles

- Status: Executed; closes the reachable harness layer, records the rest
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: command-identity-contracts proves its reachable hygiene
  guards; the deep residue is enumerated by class, not asserted

## The careful pass ADR 0080 deferred

ADR 0080 closed three of the four zero-coverage suites and deferred
command-identity-contracts as structurally different — manifest-level
guards, validator construction, comparison overrides. This is that pass,
done carefully rather than folded in under time pressure.

The suite was factored into `manifest_failures`, `baseline_failures`,
`build_context`, and `evaluate_cases`, so each layer can be driven
independently. A self-test constructs one synthetic case malformed in
exactly one way per reachable per-case guard — an unresolvable mutation
object, an unresolvable comparison override, a wrong expected status, an
expected reason the result never produces — and a meta proof blinds the
case evaluator and asserts the exact count of distinct refusals, making
those probes load-bearing.

Measured, 0/10 to **8/20**. The denominator grew because the self-test
and meta proof add guards of their own, which the audit then measures.

## The terminal turtles, named not hidden

Twelve guards remain unproved, and ADR 0069's standing rule governs them:
the proof-of-proof regress is unbounded, you stop where the next
injection buys less than it costs, and you say exactly where you stopped.
Three classes:

1. **Three domain guards** — the mismatch-reason-drift and
   unresolved-reason-drift guards, which fire only after the status and
   missing-reason checks pass with real evaluate semantics and a genuine
   drift; and the defensive `usable_for_admission` guard, unreachable
   while evaluate never admits. These need retained domain cases (the
   302-guard work ADR 0079 named) or are defensively unreachable. A
   synthetic probe was written and then removed when measurement showed it
   was a no-op for the first case — keeping dead conditional code would
   have been the fiction this suite exists to prevent.

2. **The self-test's own manifest and baseline assertions** — "an
   admittable manifest was not refused", "a structurally invalid baseline
   was not refused". These fire only when the function they test is
   broken, so in a correct suite they never fire and their removal is
   invisible. Closing them needs another meta level that blinds
   `manifest_failures`/`baseline_failures`, whose own refusals would then
   be the next turtle.

3. **The collection statements in main** — the `failures.extend(...)`
   calls, which add nothing on a clean tree (ADR 0066's clean-tree class).

Each is closable by one more injection level at rapidly diminishing
value. Stopping here is the decision, and it is recorded as a decision.

## Combined result

All four zero-coverage suites now prove guards (ADR 0080 + 0081), moving
the repository from 161/579 to **203/611**, every proof case-attributed,
zero crash-detections. The 302 domain guards across the twelve suites
remain the largest open evidence unit, and they are retained-case work,
not further instruments.

## Boundary

Harness-guard statement reachability only; not correctness, not the
domain guards. Nothing here is an accountable review determination, an
admitted member, or Gate A acceptance.
