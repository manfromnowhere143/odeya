# Formal-model findings

Status: Gate A blocking findings, updated 2026-07-16. No finding authorizes implementation.

## FM-A-001 — grant reservation and consumption point candidate is canonicalized; acceptance remains open

Severity: **High safety finding; critical Gate A ambiguity if unresolved for external effects.**

Status: **machine-vocabulary resolution candidate integrated; independent semantic, recovery, registry-digest, and review closure still required.**

The finding originated because the prose contracts did not identify one canonical representation and one unambiguous consumption point:

- `AUTHORITY_MATRIX.md` specifies reserve, use, release, revoke, expiry, and maximum-use lifecycle facts.
- `TRANSACTION_MODEL.md` says T1 “consumes or reserves” authority and resource capacity.
- `PUBLICATION_PROTOCOL.md` binds release effects to grant-use reservations and says dispatch must be claimed before revocation/expiry.
- the earlier `COMMAND_EVENT_CATALOG.md` named `authority.grant_used`, exhaustion, expiry, and revocation, but no reservation or typed reservation-release facts.

If a single-use effect grant is consumed at T1, the grant can appear terminal before the external call and the dispatch claim has no clearly modeled live authority to recheck. If it remains merely active with no canonical reservation, another effect can race for the same use and recovery cannot prove which intent owns capacity. Both interpretations violate part of the constitutional contract.

### Leading resolution checked by TLC

1. Ordinary in-ledger commands reserve and consume atomically with the command receipt and domain-event batch; no durable intermediate reservation is exposed.
2. A cross-boundary `external_effect.authorized` commit creates one exact grant-use reservation and resource reservation. It does not consume the effect grant.
3. The dispatch-claim transaction rechecks current controlled time, revocation, correction, rights, policy, exact target/digest, reservation ownership, and capacity. It atomically records `authority.grant_used(consumption_point=dispatch_claim)` plus `external_effect.started` and marks the reservation consumed.
4. Revocation, expiry, cancellation, or correction first records `authority.grant_use_reservation_released` with a typed terminal state/reason and makes dispatch illegal. Dispatch claim first creates immutable in-flight history that later revocation cannot erase.
5. Reservation identity binds grant, effect, command/request digest, actor/execution identity, target/destination, payload/manifest digest, risk/data/purpose scope, reserved units, creation position, expiry/TTL, and release/consumption event.
6. Grant policy declares `consumption_point`; undefined values deny.

`GrantConsumptionPoint.safe.cfg` exhaustively passes the bounded safety invariants. `GrantConsumptionPoint.consume-at-intent.counterexample.cfg` enables the previous ambiguous interpretation and reaches dispatch without a current-authority recheck in three states.

### Candidate integration now present

- `research-event` 0.3.0 has closed payloads for `authority.grant_use_reserved`, `authority.grant_use_reservation_released`, dispatch-claim-aware `authority.grant_used`, and `external_effect.cancelled_before_dispatch`.
- `external_effect.authorize`, `external_effect.start`, and `external_effect.cancel` have exact closed command-payload candidates; there is deliberately no generic caller-facing reserve command.
- The catalog fixes T1 reservation, dispatch-claim consumption, and cancel-before-dispatch cohorts, producers, aggregate owners, and reducer axes.
- Valid event fixtures cover all three cohorts. Adversarial mutations reject consumption at the wrong point, missing reservation/use refs, mismatched release reason/state, and cancellation from `started`.
- Replay traces make `reservation=consumed <=> dispatch=claimed` and terminal-reservation-versus-claim incompatibility structurally testable.
- The authority-grant candidate declares `consumption_point` and the dispatch-claim reservation policy.

### Residual closure evidence required

- accepted immutable command-registry records and exact schema/event/reducer digests for all three cohorts;
- independent executable semantic validators that prove cross-event equality, batch membership, capacity conservation, and request/target/digest binding rather than only JSON shape;
- additional retained race/recovery vectors for reserve/reserve, reserve/expiry, reserve/correction, claim/revoke, crash before/after claim, and restore of a live reservation;
- expiry/TTL and orphan-reservation recovery rules integrated with the canonical recovery vocabulary;
- executable semantic rules linking maximum uses, concurrency, exact target binding, and consumption point; and
- independent architecture/security review of the exact candidate.

The original representational ambiguity is resolved in the current architecture candidate. FM-A-001 remains open because schema-local validity and bounded TLC evidence do not yet prove cross-record semantics, recovery behavior, accepted registry identity, or independent review.

## FM-A-002 — composite role-grant and verification-resource race is bounded-model resolved; acceptance remains open

Severity: **High safety finding if grant cohorts or reservation race outcomes are implemented non-atomically.**

Status: **bounded resolution candidate integrated and full-harness resealed; executable semantic validation, refinement evidence, and independent review still required.**

The individual authority and reservation models did not previously check their exact composition. The first-slice resolution requires both `verification.assign` and `attempt.start` to consume five distinct single-use grants in the global role order (`safety`, `data_rights`, `resource`, `execution`, `verification`), while those same commits respectively create and claim one combined reservation. It also requires a serializable winner between start, preclaim invalidation, and controlled deadline expiry, plus exact settlement evidence that never converts missing or unavailable measurements to zero.

`CompositeAuthorityResource.safe.cfg` checks the leading resolution over one bounded run:

1. assign and start have separate grant identities bound to their exact action instances;
2. an accepted action records one use and one exhaustion for every ordered slot in the same atomic transition as its domain/resource effects;
3. rejection and exact replay add no grant use or exhaustion;
4. assignment creates exactly one active combined hold, and start claims it without releasing the ceiling;
5. preclaim invalidation releases, controlled-time deadline observation expires, and either terminal outcome permanently blocks start;
6. if start wins first, release and expiry remain permanently illegal; and
7. settlement requires exact values for every modeled non-money actual axis and exact billed/refunded money axes, while `unknown`, `missing`, and `unavailable` retain an out-of-domain sentinel rather than zero.

The safe graph completed with 29,764 generated / 6,411 distinct states, zero left, and depth 11. Four one-fault controls produced the intended counterexamples: one missing role slot at depth 2, release after claim at depth 4, inferred-zero partial settlement at depth 4, and stale start after controlled deadline expiry at depth 5.

FM-A-002 remains open because this is a finite architecture abstraction, not database-isolation or implementation evidence. Closure still requires accepted registry/event/reducer identities, executable cross-event validators for exact slot coverage and cohort ordering, serializable concurrency and recovery tests for both race orders, accounting-unit and billing/refund semantics, implementation refinement traces, and independent architecture/security review.

## Other model outcomes

Within the explicit bounds, the safe models found no invariant violation in command idempotency, effective-principal quorum, capacity, effect ambiguity/retry, order-independent publication observation, exact manifest binding, single use, contradictory-observation dispute, sealed-truth producer isolation, material-evidence disposition, consensus/evidence separation, exact five-dimension verification reservation, separate data-access admission, the acyclic View→Receipt→Bundle dispatch boundary, one three-dimension resource reservation, or the fixed five-role assignment/start composition. Thirty deliberately weakened configs each produced the expected short counterexample, including visibility-only release, suppressed dispute, failed/not-run compilation, mismatched or unissued bundles, stale admission, data-access bypass, partial grant cohorts, cross-resource conversion, crash or post-claim release, evidence-free or partial settlement, stale start after expiry, and actual-use inference from claim or absence. This does not imply those contracts are complete outside the modeled state spaces.
