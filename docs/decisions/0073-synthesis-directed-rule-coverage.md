# ADR 0073: Synthesis-directed generation; 152 of 286 rules isolated

- Status: Executed; third increment of the coverage gap
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: twenty further cross-field rules gain ablation-verified
  cases; the residual profile is measured rather than guessed

## Measuring before generating

The first two increments improved yield by guessing at what blocked
generation. This one measured it. Two profiling passes over the rules
still without an isolating case established that every base fixture
validates cleanly against its ablated schema — so nothing was wrong with
the fixtures — and that the obstruction was entirely in the mutations
used to satisfy each rule's own `if`:

- 65 rules where satisfying the `if` left the schema clean, meaning the
  `then` needed a breaker the strategy could not find;
- 40 `const`, 16 `minItems`, 15 `type`, 8 `oneOf`, 6 `enum` and 4
  `minimum` residuals from collateral damage;
- 17 rules whose `if` is expressed through `required` rather than
  discriminating constants, so no mutation was derivable at all;
- 9 whose mutations could not be applied to the fixture's shape.

## What the increment adds

Generation v2 answers that profile directly: absent fields are
**synthesised** rather than skipped (`add` with a schema-satisfying or
schema-violating value as the role requires), `if` conditions expressed
through `required` now yield mutations, violations are enumerated
best-first across nested properties and `allOf` members rather than
stopping at the first candidate, and repair is typed — `type`,
`minItems`, `maxItems`, `minimum` and `required` residuals are each
repaired in their own terms instead of only `const` and `enum`.

Twenty more rules became isolable under the unchanged two-sided test:
refused with the rule, accepted without it. **Coverage is 152 of 286**,
corpus 814 cases, all 152 isolations re-proven by the retained audit.

## Honest diminishing returns

Three increments have produced 112, then 20, then 20. The remaining 134
rules resist because their `if` conditions entangle neighbouring rules
in ways local repair cannot untangle — the entanglement is semantic, not
syntactic, and further mechanical generation looks unlikely to pay. The
next real step for those is authored cases written from each rule's
intent, which is human-scale work at roughly 134 units, or a constraint
solver over the whole schema rather than local repair. Recorded as a
choice for whoever takes it, not as a promise.

## Boundary

Ablation proves a rule is noticed, never that it is correct, and these
cases are machine-generated with names describing position rather than
meaning. 134 rules remain unexercised, and rules outside the root-level
`if/then` shape were never counted. Nothing here is an accountable
review determination, an admitted member, or Gate A acceptance.
