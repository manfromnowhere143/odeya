# ADR 0082: Inventory-mutation vocabulary closes the artifact-guard layer

- Status: Executed; proof-of-concept for the domain-guard closure, one suite
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: first-slice-resolution's inventory guards gain
  ablation-verified known-bad cases; the pattern is proven for the 302-guard
  domain layer ADR 0079 named

## The gap and the precedent

ADR 0079 measured 302 domain guards with no known-bad proof. Investigation
(ADR 0081's boundary) found a large fraction are guards on a static loaded
artifact: `inventory_errors(inventory)` runs once on the first-slice
inventory, so no retained case could reach any of its ~40 guards. This is
exactly the state lifecycle-closure was in before ADR 0028 added
`identity_map_mutation`, and it closes the same way.

## What was done

An `inventory_mutation` model applies one bounded replace or remove to a
deep copy of the inventory and runs `inventory_errors` on the copy — the
exact shape ADR 0028 established. Thirty-seven known-bad cases were
generated and **each verified to fire its own guard before retention**: the
version and status pins, all eleven scope-verdict flags, the five count
equalities and the design/unresolved counts, the eight bounded-grant-law
fields, the command/event duplicate and overlap guards, the conflict
completeness guard, and the four mutation-hygiene guards of the new model.

Measured by the generalized audit, not asserted: first-slice-resolution
moved 20/125 to **36/129**, repository 203/611 to **219/615**, every proof
case-attributed.

## An honest measurement note

The audit counts refusal *statements*. A loop such as
`for field in required_scope: errors.append(...)` is one statement that
emits eleven messages, so eleven field-cases prove one statement-guard while
giving eleven distinct per-field attributions. The +16 statement guards
therefore under-counts the 37 fields the cases actually bind; both numbers
are real and neither is inflated. One guard — `inventory lacks required
resolution events` — was not closed because triggering it needs a specific
list index the generator did not resolve, and it is left honestly open
rather than papered over.

## What this establishes

The pattern scales: every suite whose guards check a static loaded artifact
(the module manifest, the identity map, the disposition record) closes by
the same bounded-mutation vocabulary plus ablation-verified generation. The
genuinely per-case domain-logic guards remain targeted-case work. This
tranche proves the mechanical half on one suite before scaling, the same
one-suite-then-scale discipline used for the harness self-tests.

## Boundary

Statement reachability of artifact guards only; not correctness. The
generator's cases are machine-derived and verified to fire, not shown to
enforce the right rule. Nothing here is an accountable review determination,
an admitted member, or Gate A acceptance.
