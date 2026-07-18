# ADR 0070: Retract ADR 0068's attribution claims; the corpus gap is larger than the binding gap

- Status: Executed; retracts two published claims and names the
  repository's largest remaining evidence gap
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: `refusal_class` is recomputed and enforced instead of
  declared; the class taxonomy is corrected by measurement; the
  cross-field rule coverage gap is recorded as the next major unit

## Two published claims were false

Independent review (round three) refuted all four surfaces of ADR 0068,
and both of its headline claims are retracted.

**The classification was decorative.** The reviewer inverted the declared
`refusal_class` on all 457 cases and the validator reported zero
failures. The field was checked for membership in a two-element set and
otherwise unread. It is now recomputed on every run from the declared
pointer, the declared keyword, and the case's own mutation paths, and
must match; replaying the inversion now produces 457 detections.

**"417 cases refuse at the mutated path" was wrong.** The derivation
counted an error as mutation-correlated when its pointer was an
*ancestor* of the mutated path — and `/` is an ancestor of everything, so
every root-level error was silently classified as at-mutation. The
corrected measurement, with ancestor matching allowed only for
container-level keywords that are genuinely about the container:

- **232** refuse at or under the mutated path,
- **169** refuse at a container of it (`required`, `oneOf`,
  `additionalProperties` and kin), now a named class rather than
  hidden inside the first,
- **56** refuse by implication elsewhere.

## What review found that this tranche does not fix

**The bindings are weaker than a count suggests.** 100 cases bind at the
root, and 75 of the 92 `research-event` cases share the identical
`('/', 'oneOf')` binding — rebinding all 92 to that generic pair leaves
76 still passing. The cause is mechanical: for a large `oneOf` schema the
validator yields only the top-level branch failure, and the informative
sub-errors live in its context. Descending into that context in both the
derivation and the enforcement is a real unit and is not attempted here.

**Conjunctive case names still bind one conjunct.** A case named for
three requirements pins whichever error sorted first; the others fire
unbound and are deletable. This is exactly the compound-name defect ADR
0064 dissolved for eight cases, now visible across the corpus at a scale
prong-splitting cannot reach by hand.

**And the largest finding is not about attribution at all.** Sweeping
every root-level `if/then` cross-field rule in every schema with invalid
cases, the reviewer deleted each in turn: **210 of 286 can be removed
with the whole 457-case corpus still green.** Most of that is coverage
absence — no case exercises the rule at all — which no attribution scheme
can repair. Four targeted ablations were worse: a case *named after* the
deleted rule still passed, because its binding sat on a different
constraint that kept firing.

That is the honest state: the corpus binds what it exercises, and it
exercises well under half of the cross-field rules it is meant to
protect. **Closing that coverage gap is the next major evidence unit**,
and it is larger than everything the attribution family has done.

## Boundary

Nothing in this tranche adds coverage; it corrects claims and makes one
decorative field load-bearing. The census still counts 1,147 bound
negatives, and that number now carries an explicit caveat: binding is
not coverage, and for this corpus the coverage behind the bindings is
measured and thin. Nothing here is an accountable Gate A review
determination, an admitted member, or acceptance.
