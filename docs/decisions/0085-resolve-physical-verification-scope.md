# ADR 0085: Resolve physical verification scope before confirmation

- Status: Executed; architecture evidence only
- Date: 2026-07-19
- Decision owners: physical/metrology contracts, verification architecture
- Gate effect: the retained physical `VerificationPackage` must resolve to one
  exact typed subject before its class, dimension applicability, or terminal
  confirmation is accepted

## The false positive

`verification-run-physical.valid.json` was structurally accepted while it
simultaneously:

- required and reported `IV4_independent_replication`;
- marked `physical_validity` required and passing;
- described that dimension as `No physical-world assertion`; and
- concluded that “the exact physical claim” passed.

The generic `VerificationPackage` schema correctly constrains terminal-state
shape, class ordering, required-dimension outcomes, and its advisory-only
authority boundary. It cannot, by itself, resolve a generic subject reference
and determine which scientific predicates that exact subject supports.
Free-form scope text therefore crossed the schema boundary without a
subject-aware semantic oracle.

## Decision

Keep `VerificationPackage` 0.6.0 generic and immutable rather than mutate a
live schema identity in place. Extend the physical-contract suite with one
bounded architecture-time resolver:

1. The package subject is the retained `PhysicalEvidenceVector`
   `physical-evidence.inbar`, including its exact type, ID, version, schema ID,
   and candidate digest tuple.
2. The package mission must equal the resolved subject mission.
3. The exact selection-rule identity selects
   `physically_validated_under_scope` and
   `recommendation_inside_safety_envelope`.
4. That selected scope requires `IV4_independent_replication`.
5. `physical_validity` and `safety` must both be required and passing, with
   scope tokens and evidence references equal to the corresponding typed
   subject components.
6. The confirmed scope statement is one deterministic bounded sentence
   derived from those identities and predicates. It states that this is a
   synthetic architecture example and grants no action, dispatch,
   publication, or Gate A authority.
7. The terminal reason codes must retain
   `synthetic_architecture_fixture_not_real_physical_evidence`.

The existing schema remains responsible for forcing every eligible next action
to be advisory only and for fixing authority, dispatch, and publication flags
to false. The resolver makes safety applicability follow the selected
safety-bound predicate rather than an untyped assertion that no consequential
action exists.

## Known-bad evidence

The physical suite retains cases that refuse:

- an unresolved subject tuple;
- a mission that differs from the resolved subject;
- a generic selection rule substituted for the typed selection rule;
- a physical replication scope assigned below IV4;
- IV4 paired with `No physical-world assertion`;
- a selected physical predicate marked not required;
- a selected safety-bound predicate marked not required;
- terminal prose that claims physical-action authority; and
- removal of the synthetic-evidence boundary.

Each semantic known-bad binds the exact authored refusal substring. The suite's
existing attribution self-test and meta-proof continue to reject missing or
misdeclared bindings. Mutation remeasurement proves all eight new resolver
guards case-attributed: physical-contract coverage moves from 26/61 to 34/69;
the combined twelve-suite record moves from 239/627 to 247/635, with zero
crash-detected proofs and the prior 388 unproved guards still explicit.

## Boundary

This is one exact resolver-backed architecture fixture, not a general subject
registry, claim compiler, canonical-digest verifier, physical experiment,
metrology determination, VVUQ acceptance, safety approval, or independent
review. The `PhysicalEvidenceVector` and `VerificationPackage` remain synthetic
examples. A future admitted verification path still requires a complete
registry-backed resolver, canonical identity, real retained evidence,
separately authorized execution, accountable review, and Gate A acceptance.
