# ADR 0084: Freeze the PRQ-009 assignment order and reject its legacy cycle

- Status: Executed architecture consistency repair; PRQ-009 remains unresolved
- Date: 2026-07-19
- Decision owners: cognitive control, verification, work, resources
- Gate effect: removes one normative contradiction and makes its legacy form a
  retained known-bad; it admits no identity, member, command, event, or runtime

## The contradiction

ADR 0016, the Gate A prerequisite closure plan, the cognitive-control
contract, and the first-slice resolution already chose an acyclic order:

```text
WorkIntent
  -> verification.assign
  -> post-assignment WorkContract
  -> separate dispatch claim
```

Two active normative consumers retained the pre-decision order.
`TRANSACTION_MODEL.md` said that `verification.assign` atomically bound a
pre-existing local `WorkContract`, active lease, and reservation.
`SEMANTIC_VALIDATION.md` repeated those objects as assignment inputs. That is
not a harmless wording difference: the assignment transaction is the commit
that creates the active lease and reservation, and the `WorkContract` is
derived from that exact successful commit. Requiring any of them as
pre-existing assignment input forms a causal cycle and invites fabricated
current-state references.

The older first-slice closure plan and gap inventory also contain pre-resolution
alternatives. They already identify themselves as superseded/non-freezable and
remain retained as historical evidence; this decision does not rewrite them
into a false contemporary plan.

## Decision

The canonical architecture order is:

1. One exact admitted `WorkIntent` is the prospective work input. It grants no
   lease, reservation, materialization, dispatch, spend, or runtime authority.
2. `verification.assign` rechecks the exact current prerequisites and commits
   one ordered thirteen-event batch: five assignment-grant uses in
   safety/data-rights/resource/execution/verification order, reservation
   creation, lease acquisition, `verification.assigned`, then the matching
   five grant exhaustions. The batch binds the selected worker. It creates no
   source-byte visibility, launch outbox, or dispatch claim.
3. Only after that exact successful commit may a deterministic `WorkContract`
   be derived. It binds the same exact `WorkIntent` and assignment commit and
   is not a member of the assignment event batch or dispatch authority.
4. `attempt.start` is a separate post-contract dispatch-claim commit. It
   rechecks the derived `WorkContract` and every current assignment fact,
   consumes its separate start grants, claims the reservation, records the
   attempt/verification start, and creates the launch outbox before any
   execution boundary may be crossed.

The exact finite contract is retained at
[`architecture/prq-009-assignment-order-contract.json`](../../architecture/prq-009-assignment-order-contract.json).
Its consumer census distinguishes active normative consumers from the two
explicitly superseded pre-resolution artifacts. The census is deliberately
bounded to sources that directly assert the local-assignment construction
order, its event producers, or its fail-closed structural boundaries;
enumeration-only fixtures and external-dispatch-only semantics are not
misrepresented as independent statements of this order.

## Evidence

`scripts/validate_prq_009_assignment_order.py` validates the finite contract,
checks required and forbidden semantics across the enumerated consumers, and
runs the retained mutations in
[`tests/prq-009-assignment-order/cases.json`](../../tests/prq-009-assignment-order/cases.json).

The legacy defect has two direct known-bads:

- prepend the old statement that `verification.assign` binds a pre-existing
  local `WorkContract` to an active consumer; and
- replace the machine contract's prospective input `WorkIntent` with
  `WorkContract`.

Both must fail for the exact intended reason. Further mutations refuse a
pre-existing active lease, a pre-existing reservation, a WorkContract inside
the assignment batch, assignment-time dispatch, an incomplete thirteen-event
cohort, dispatch before contract derivation, premature PRQ closure, and runtime
authority.

This evidence is finite, author-correlated, and architecture-local. Text
presence does not prove semantic correctness, and the checker can be weakened
with its record unless an independent gate/reviewer catches the change. It is
stronger than ungated prose because the exact legacy order now has a retained
falsifier, but it is not independent review or implementation conformance.

## Boundary and remaining blockers

PRQ-009 remains `unresolved_blocking`. The repair does not create:

- an issued canonical profile or admitted canonical `WorkIntent`;
- immutable `verification.assign`, `verification.assigned`, WorkLease,
  WorkContract, state, reducer, registry, root, checkpoint, P0, or activation
  members;
- the complete replay/race/refinement package or independent implementations;
- accountable review or operator Gate A acceptance; or
- assignment, dispatch, product runtime, external effect, or deployment
  authority.

Those identities, members, proofs, reviews, and decisions remain prerequisites.
