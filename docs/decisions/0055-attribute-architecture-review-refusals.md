# ADR 0055: Attribute every architecture-review refusal to its intended constraint

- Status: Executed; first of the six unattributed suites, pattern for the
  remaining five
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: the architecture-review suite can now distinguish its
  intended constraint firing from an incidental refusal, with a
  fail-closed self-test proving the attribution check itself fires on
  every run

## The blindness

Six suites asserted refusal without attribution across 229 known-bad
cases. `architecture-review` counted any validation error as refusal:
a case corrupted in transit, or a schema edit that broke an unrelated
rule at the mutated location, would keep the suite green while the
constraint the case names — the implementation lock, the eight-lane
completeness rule, the high-severity disposition bans — silently
stopped firing. This is the exact condition that made lifecycle closure
blind before ADR 0024.

## The attribution

Each of the sixteen known-bad cases now declares `expected_refusal`:
the exact instance JSON Pointer and JSON Schema keyword that must
refuse it, chosen from the case's stated intent rather than copied from
observed behavior — every binding names the rule the case exists to
prove (the runtime-authorization ban binds
`/implementation_lock/runtime_product_implementation_authorized` by
`const`, the lane-count rule binds `/review_scope/required_lanes` by
`minItems`, and so on). The keyword is null where a boolean false
schema refuses, because the validator reports no keyword there. Pointer
and keyword are library-stable under the hash-locked jsonschema pin,
unlike message text.

The harness refuses a known-bad case that declares nothing, and refuses
one whose declared constraint is not among the errors that fired. Per
law 11 the gate carries its own known-bad proof: on every run, two
tampered copies of a real case — one misdeclared, one undeclared — must
each be refused by the attribution check, and the suite fails closed if
either sails through. An external negative control (a live tampered
binding failing the committed suite) was exercised before retention.

## Boundary

Attribution is per-case intent binding, not guard-statement or
condition mutation; the lifecycle-style coverage audits do not extend
here because the refusing engine is the pinned jsonschema library, not
model code this repository authors. Five suites remain unattributed —
`cognitive-contracts` (107), `projection-contracts` (37),
`constitutional-construction` (29), `first-slice-resolution` (21), and
`mathematical-contracts` (19), 213 cases — and are the continuation of
this unit, followed by converging the now-five attribution spellings on
one vocabulary. Nothing here is an independent review, Gate A
acceptance, or an operator decision.
