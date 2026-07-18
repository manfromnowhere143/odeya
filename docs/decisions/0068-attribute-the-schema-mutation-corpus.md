# ADR 0068: Attribute the schema mutation corpus; the census reaches zero

- Status: Executed; every known-bad case in the repository is now bound
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: all 457 architecture-schema known-bad cases declare the
  exact constraint that must refuse them and their refusal class; the
  default validator enforces it; the census reports zero unattributed
  negatives across 1,147 bound cases

## The gap

Independent review found this corpus outside the attribution census
entirely — the repository's largest adversarial set, two-thirds the size
of everything the census then certified, checking only refusal polarity.
Any validation error counted as proof, so a constraint could stop firing
while an incidental one kept the case red: the ADR 0024 failure mode at
the largest scale in the repository.

## The attribution

Every case's binding was derived by measurement rather than assertion:
each mutation was applied, the fired errors collected, and the binding
chosen as the most specific error at or under the mutated path.

The derivation surfaced a real distinction worth keeping. **417 cases
refuse at the mutated path.** The other **40 refuse away from it, by
implication**: the mutation flips a discriminator — a grant's role, a
claim's mode, a channel's missingness — and the refusal fires at the
consequence the discriminator implies, which is exactly what those cases
exist to prove. Rather than flatten this, each case declares a
`refusal_class` of `at_mutation` or `implication`, so a case that
silently changes category is visible.

The default validator now refuses a known-bad schema case that declares
no binding, declares no refusal class, or whose declared constraint is
not among the errors that fired. An external negative control was
exercised against the committed tree. The census registry promotes this
suite out of the known-unattributed list, and its output moves from
"457 negatives remain explicitly unattributed" to zero across 1,147
bound cases.

## Boundary

These bindings are observation-derived: they pin what does refuse each
case, and the mutation-path correlation makes them intent-correlated,
but they are not per-case intent statements hand-verified against each
case's name — that discipline was applied to the smaller suites, where
review could sample it. The distinction is recorded here rather than
implied away. Attribution remains binding, not weakening-mutation
coverage: nothing here proves a schema constraint could not be weakened
while still refusing at the declared location. Nothing here is an
accountable review determination, an admitted member, or Gate A
acceptance.
