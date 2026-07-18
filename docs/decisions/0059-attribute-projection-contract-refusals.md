# ADR 0059: Attribute every projection-contract refusal to its intended constraint

- Status: Executed; fifth of the six unattributed suites
- Date: 2026-07-18
- Decision owners: architecture review, projection contracts
- Gate effect: both refusal domains of the projection suite bind every
  known-bad case to the exact constraint that must refuse it, with a
  four-way fail-closed self-test on every run

## The measure, corrected again

Carried as 37 unattributed cases; measured 54 — 37 structurally
known-bad and 17 semantically known-bad. Every attributed suite so far
has under-counted the same way, which is why the handoff now orders
counts re-measured rather than trusted.

## The attribution

Structural cases bind instance pointer plus keyword (ADR 0055/0056
spelling): the twenty-five adversarial vectors bind their defining
constraint — unmeasured-as-zero at its `oneOf`, the sealed-truth
exposure boundary, cross-proposal count leakage, the five canonical
decimal spellings, the projection self-digest ban at the root
`additionalProperties`. Semantic cases bind the authored checker
message: lease-time coverage, frontier equalities, reducer-path
distinctness, limitation preservation, and the reference-mismatch
family each bind their own text.

One latent harness fact is now stated rather than silent: a
`semantic_expect` declared on a structurally invalid case is never
evaluated, because the semantic layer requires a structurally valid
subject. Thirty-two cases carry such a declaration as documentation of
intent; the attribution binds what actually refuses them, and the
in-harness comment records the boundary.

The four-way self-test (structural and semantic, misdeclared and
undeclared) runs on every invocation and fails closed; external
negative controls exercised both domains against the committed suite
before retention.

## Boundary

One suite remains — `cognitive-contracts` (107 carried, to be
re-measured) — then the vocabulary convergence. Nothing here is
authority, release, runtime, a noninterference proof, or Gate A
acceptance.
