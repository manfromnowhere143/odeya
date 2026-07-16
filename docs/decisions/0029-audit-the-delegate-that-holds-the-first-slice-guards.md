# ADR 0029: Audit the delegate that holds the first-slice boundary guards

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security, canonical
  identity
- Gate effect: retracts the 75/75 coverage headline, restates lifecycle guard
  coverage as 89 of 139, and establishes that the 43/60/25/11 first-slice
  boundary guards had no known-bad proof; closes no finding and accepts no
  Gate A row

## Context

ADR 0028 reported lifecycle guard coverage at 75 of 75 and called five of six
models guard-complete. `identity_map_mutation_errors` was recorded as
unmeasured, on the stated grounds that it returns refusals directly and
delegates to `schema_contract_errors`, which branch mutation "cannot attribute".

That reasoning was half right and the conclusion was wrong. This decision
originally added: "the model does hold no guard of its own." ADR 0031 retracts
that too — the model holds five `return`-guards, and this decision's own
eleventh case proves one of them, the unknown-target refusal it calls a hygiene
guard two sections later. The delegate meanwhile holds 64 guards, uses
`errors.append`, and is auditable by exactly the method already in use. It was never audited because it
was never named in `AUDITED_MODELS`. Declaring the caller unmeasured while
leaving the callee unmeasured too made 64 guards invisible, and 75/75 described
only what had been chosen to look at.

`schema_contract_errors` measured 4 of 64.

## Finding

The 60 unproved guards include the invariant the entire tranche rests on:

- `first-slice required event count is not preserved at exactly 60`
- `first-slice aggregate/reducer-family count is not preserved at exactly 25`
- `event identity map does not contain exactly 60 rows`
- `event identity map is not exactly the 60-event first-slice set`
- `ResearchEvent 0.7.0 does not fail closed on unresolved branch contracts`
- `ResearchEvent 0.7.0 permits a fabricated per-branch contract digest`
- `unresolved ResearchEvent candidates can claim event authority`
- `canonical WorkLease candidate can claim execution authority`

Every commit message, the closure plan, and the validator's own output recite
the exact 43/60/25/11 boundary. The suite prints "60 event identities, 25
aggregate/reducer families" on every run. Nothing proved that the guards
enforcing those numbers fire at all: each could be removed with the suite green.

The cause is the same defect ADR 0028 fixed one model earlier.
`identity_map_mutation_errors` loads schema, inventory and identity map, and
could mutate only the identity map. Every guard reading the other two inputs was
unprovable by construction, however a case was written. A closed mutation
vocabulary silently bounds what evidence can exist — twice now, in two models,
found only by pointing the audit somewhere new.

## Decision

- Add `schema_contract_errors` to `AUDITED_MODELS`, so the guards are measured
  where they live rather than scored through a caller that has none.
- Give the mutation an optional `target` of `identity`, `schema`, or
  `inventory`, defaulting to `identity` so all four retained cases are unchanged.
  `load_json` re-reads each call, so a mutated input cannot leak between cases.
- Add eleven known-bad cases covering the first-slice boundary counts, the
  ResearchEvent resource and instance identity, the identity-map source binding,
  the row set and its duplicates, and the unknown-target hygiene guard the
  extension introduces.
- Correct the `not_auditable` note: reporting `identity_map_mutation_errors` as
  unmeasured was right; leaving its delegate unaudited was not.

Coverage is now **89 of 139**, with `schema_contract_errors` at 14 of 64.

One case is deliberately blunt. Replacing the ResearchEvent `$id` cascades into
62 refusals, because every identity-map row binds that resource. It is retained
anyway: the case names its own guard, so deleting that guard fails the suite
even though 61 errors survive. The ADR 0024 binding is what makes a blunt
mutation acceptable evidence.

## Non-decisions

This decision does not:

- claim the denominator is now correct. 139 is what `discover()` currently sees
  across six functions. It was 69, then 71, then 75, then 139 — every previous
  figure was published as fact and every one was wrong. Treat it as a claim;
- prove any guard correct. 89 are exercised; none is shown to enforce the right
  rule;
- close the remaining 50 gaps in `schema_contract_errors`, which are the largest
  block left and include branch-level payload identity and the canonical
  WorkLease candidate's authority boundary;
- close PRQ-005 through PRQ-008, or supply an independently reproduced verdict;
  or
- change any contract, vocabulary, event identity, schema byte, or the
  43/60/25/11 boundary itself.

## Consequences

The 43/60/25/11 boundary now has known-bad proof for its count guards. Until
this decision it had none, through every tranche that cited it.

The lesson repeats and should be stated without softening. Three times now a
coverage figure was published as fact and was wrong: 69 omitted two `return`
guards, 75 omitted an entire delegate, and both were reported by the producing
agent as complete. The measurement is only ever as wide as where it was pointed,
and nothing in the tool, the gate, or the validator reveals where it was not
pointed. A coverage number is a claim about attention, not a property of the
repository, and it should be read that way here and everywhere else in this
mission.
