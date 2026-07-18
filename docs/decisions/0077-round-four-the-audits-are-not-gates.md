# ADR 0077: Round four; the mutation audits are records, not gates

- Status: Review executed and responded; retracts a scoping claim in ADR
  0069
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: the meta proof detects duplicated probes, the schema
  refusal class requires genuine container membership, two
  refusal-determining functions enter the audited set, and both coverage
  gates pin their measured totals

## What review refuted

**The meta proof counted arity, not attribution.** Blinding a
collaborator makes every probe fail unconditionally, so the count `10`
counted call sites. Making two probes identical preserved the count while
one guard became removable — and the mechanism ADR 0069 built for exactly
this did not fire. Probe subjects must now be distinct, and the
reviewer's edit is refused by name.

**The refusal-class rule was vacuous at the root.** `pointer == "/"` was
dead code, subsumed by the prefix test it sat beside, and every
root-level container error classified as mutation-correlated whatever was
mutated: 260 of 609 classes were a function of `(pointer, keyword)`
alone. ADR 0070 said ancestor matching was allowed only for keywords
"genuinely about the container"; the code checked only set membership.
The container branch now requires the mutated path to be a **direct
member** of the container. Eighty-three cases reclassified honestly from
`container_of_mutation` to `implication`, and of the 368 cases still
claiming correlation, **zero** survive substituting a junk mutation path.

**Two refusal-determining functions were outside every audited tuple** —
`refusal_matches`, which decides whether a declared refusal counts at
all, and the meta proof itself. Both are now audited; the statement
denominator grew 183 to 185, and the two new guards are unproved, which
is the honest starting position rather than a hidden one.

**And the deepest finding: the audits are not gates.** `--check` is a
byte-identity comparison against a record that `--write` regenerates from
whatever the checker currently says, so any author can launder a
weakening by re-measuring. ADR 0069's "Surviving, recorded" section
confined coordinated-edit survival to the three exact-inventory suites on
the grounds that lifecycle-closure has a mutation audit; that reasoning
was wrong, because a regenerable record is not a gate. Review
demonstrated the consequence end to end: with the floors lowered and the
record regenerated, the case set was trimmed to one safe and one
adversarial trace with every check green.

Both coverage gates now pin their measured totals. This does not stop
laundering — nothing short of an independent re-measurement can — but it
converts a silent regeneration into a deliberate, reviewable edit of a
gate file, which is the same reason the CI pins exist.

## Boundary

The pins are a tripwire, not a proof. The audits remain records that
their own subject can regenerate, and closing that properly requires an
independent baseline no session can supply for itself. Nothing here is an
accountable review determination, an admitted member, or Gate A
acceptance.
