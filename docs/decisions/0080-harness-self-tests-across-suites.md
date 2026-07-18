# ADR 0080: The harness self-test pattern generalized to three suites

- Status: Executed; first closing of the ADR 0079 gap
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: three suites that proved zero guards now prove their harness
  hygiene by in-harness self-test; the generalized audit re-measures it

## The distinction ADR 0079 exposed

ADR 0079 measured 161 of 579 guards proved and named 418 open. Classifying
those 418 by how they close showed two populations: **116 harness-hygiene
guards** — "case is not an object", "mutation failed", "safe case failed",
the coverage floors — and 302 domain guards. The hygiene guards are
structurally unprovable by retained cases, because a malformed case cannot
live in a passing suite. That is the exact state lifecycle-closure's
harness occupied before ADR 0066, and it closes the same way: a self-test
that constructs the malformed thing in memory.

Four suites proved *nothing* because their guards are almost entirely
hygiene. This tranche closes three of them.

## What was done

`work-identity-successor-cohort`, `work-intent-identity-candidate`, and
`canonical-profile-candidate` each had their case loop factored out of
`main` into an `evaluate_cases` function, so a self-test can drive it with
malformed cases. Each self-test carries the ADR 0066/0069 discipline in
full: one synthetic case malformed in exactly one way per guard, floors
probed from both sides so their constants are load-bearing, probe subjects
required distinct so two identical probes cannot preserve a count while a
guard rots, and a meta proof that blinds the evaluator and asserts the
exact count of distinct refusals. The canonical-profile self-test also
drives its base-acceptance and tag-inventory guards, which sit outside the
per-case loop.

Measured by the generalized audit, not asserted:

| suite | before | after |
|---|---|---|
| work-identity-successor-cohort | 0/12 | 13/19 |
| work-intent-identity-candidate | 0/13 | 12/20 |
| canonical-profile-candidate | 0/10 | 9/18 |

Repository total moved 161/579 to **195/601**, every proof
case-attributed, zero crash-detections. The denominators grew because
each self-test adds guards of its own, which is honest: the audit now
measures the self-tests too, and it proves them.

## Deliberate scope

`command-identity-contracts`, the fourth zero-coverage suite, is
structurally different — manifest-level guards, validator construction,
comparison overrides — and is not forced into this tranche. Rushing a
refactor of the most complex of the four to bundle it here would trade
correctness for a rounder number. It is the named next unit and gets its
own careful pass.

## Boundary

Statement reachability of harness guards only. A proved hygiene guard
fires; it is not shown to enforce the right domain rule, and the 302
domain guards across the suites remain open. The record is regenerable by
`--write` and therefore not a gate (ADR 0077); its summary is pinned.
Nothing here is an accountable review determination, an admitted member,
or Gate A acceptance.
