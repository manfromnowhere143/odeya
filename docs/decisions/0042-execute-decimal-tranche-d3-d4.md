# ADR 0042: Execute decimal tranches D3 and D4 and freeze the typed object

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: migrates all 127 accepted scientific-decimal leaves and both
  binary-number domains to the frozen typed scientific-decimal object; the
  audit's generic-decimal and generic-number counts are zero across all one
  hundred twelve schemas

## Context

The accepted D3 table bound a semantic type, unit, and precision to every
generic decimal leaf, but no frozen object shape existed to migrate into, and
the audit detector had no concept of a governed decimal: even the corpus's
own typed `quantity` objects counted as findings at their inner value. The
binding gate is the detector itself — whatever shape it exempts is the de
facto contract — so the shape law and the detector had to be frozen together,
each provable against the other.

## Decision

The profile core's `scientific_decimal_contract` gains a
`typed_object_contract`: a closed object carrying exactly one value member —
`decimal` for scalars, `elements` for matrices — plus `semantic_type` (a
const from a seventeen-type frozen registry), `unit`, and `precision`, all
required, with `additionalProperties` rejected. The audit detector recognizes
exactly this shape, reads the registry from the frozen core bytes (failing
closed to "nothing is governed" when the core is absent), and proves itself
on every run: a governed scalar and matrix produce zero findings, a bare
lexical decimal stays a finding, and eight single-member near-misses each
keep counting. A self-test failure refuses the audit entirely (ADR 0024).

The migrator executed all 127 rows table-driven, preserving every non-decimal
union alternative — nine grounded-outcome fields' `"unknown"` and thirty-one
nullable branches, which the first pass dropped and the fixture gates caught
(missing is never zero). D4's nine research-mission budget fields migrated to
per-type governed objects mirroring the accepted authority-grant rows field
by field, `"unknown"` preserved as a first-class alternative, and the two
binary-number definitions were removed once fully unreferenced. Roughly two
hundred fixture values across six suite corpora converted by error-driven
migration; the semantic checkers in four suites unwrap the governed object
and keep firing on the lexical value inside rather than silently skipping;
the physical suite's bounded constructors now read schema identities from
live bytes instead of hardcoding versions.

## Operator decisions under ADR 0037

- Monetary precision is instance-declared, never a fixed currency exponent:
  sub-cent LLM spend must survive exactly (the review lesson that deferred
  the original "certain" precision-2 proposal).
- Instance-declared unit forms collapse to a required nonempty unit string;
  covariance elements carry the symbolic unit `pairwise_unit_product`; the
  evidence-measure unit stays instance-declared because the measure type
  determines it.
- The typed object's value pattern is the negative-zero-free refinement of
  the frozen lexical pattern. The contract always said
  `lexical_negative_zero: reject`, but the parse-level pattern admits `-0`,
  and a known-bad trap caught the migrated schemas accepting it. The core now
  freezes `value_lexical_pattern` alongside the contract, proven on positive
  and negative controls.
- Physical-quantity's exact-decimal representation follows the frozen
  contract's exponent law — lowercase admitted, uppercase rejected — retiring
  the legacy local no-exponent rule; the trap now attacks `1E3`.

## What the tranche caught

The fixture and trap gates caught four real defects in the migration itself:
the dropped `"unknown"`/null alternatives; the negative-zero admission; six
dimension vectors given the wrong union branch's constants; and known-bad
traps whose mutations still attacked the retired shape, which would have
passed vacuously — each was re-aimed at the governed member it must break.
The disposition validator's own self-test migrated to post-wave semantics:
with the D3 table empty by measurement, the dropped-row proof became a
phantom-row proof.

## Non-decisions

This tranche does not annotate any digest scope (D5a), converge any divergent
definition (D6-D8), pin any profile binding (D9), admit a member, or accept
Gate A.

## Consequences

Four of the six blocking classes are now closed by measurement: zero
nonconformant fixture timestamps, zero unprofiled datetime paths, zero
generic scientific decimals, zero generic JSON numbers. The ledger holds 69
reissued resources and 14 new-schema candidates, every predecessor verifying
against the checkpoint. What remains is D5a's 668 digest-scope annotations,
D6-D8's 55 definition convergences, and D9's 11 profile-binding pins.
