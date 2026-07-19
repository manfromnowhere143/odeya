# ADR 0090: Preserve the resource claim when a WorkLease ends

- Status: Executed as an architecture compatibility correction; C5 and
  PRQ-009 remain unresolved and blocking
- Date: 2026-07-19
- Decision owners: work lifecycle, resource accounting, canonical identity,
  architecture review
- Gate effect: reissues the affected unissued candidates under new immutable
  resource identities and corrects `C5-WORK-LEASE-RELEASE-CLAIM-001`; grants
  no canonical identity, admission, assignment, lease, settlement, runtime,
  publication, or Gate A authority

## The contradiction

The first-slice flow claims a ResourceLedger reservation at `attempt.start`.
The retained `ResearchEvent` 0.17.0 branch for `work.lease_released` then
required `reservation_claim_state=unclaimed` and a null claim reference. A
post-start lease could therefore terminate only by erasing the already
committed resource claim or by pretending that WorkLease owned ResourceLedger
settlement. Both interpretations violate the aggregate boundary:

- WorkLease owns `active -> released`;
- ResourceLedger owns `active -> claimed -> settled`; and
- termination, crash, timeout, or a missing callback cannot turn unknown usage
  into zero or release a claimed ceiling.

This is compatibility finding `C5-WORK-LEASE-RELEASE-CLAIM-001`. It is a
contract defect, not evidence that any runtime executed an invalid transition.

## Decision

1. Reissue the event envelope as
   `urn:odeya:schema:research-event:0.18.0`. Its
   `work.lease_released` branch requires:
   `reservation_claim_state=claimed`, the exact retained
   `resource.reservation_claimed` event reference,
   `crash_release_allowed=false`,
   `settlement_required_after_claim=true`, and
   `new_start_claims_allowed=false`.
2. Lease release changes only the WorkLease aggregate from `active` to
   `released`. It neither emits nor implies a ResourceLedger transition.
   A later `resource.reservation_settled` event is the sole retained
   `claimed -> settled` fact.
3. Reissue the blocked base WorkContract as
   `urn:odeya:schema:work-contract:0.19.0` so its prospective
   `verification.assigned` binding names ResearchEvent 0.18.0.
4. Reidentify the profile-bound WorkContract wrapper as
   `urn:odeya:schema:work-contract:0.20.0`. It binds the exact raw
   WorkContract 0.19.0 candidate and the current unissued WorkIntent 0.19.0
   successor candidate. Its canonical digest, member, admission, operator
   acceptance, and every authority field remain null or false.
5. These are side-by-side resource reissues, not mutable aliases. Exact
   predecessor bytes remain retained through the reissue ledger and Git
   objects. Their historical identities are not redirected to the successor
   bytes, and Git-only predecessor retention remains insufficient for a
   complete offline resolver.

## Bounded sequence evidence

The lifecycle checker dereferences seven retained synthetic ResearchEvent
fixtures, from lease acquisition through later resource settlement. It does
not dereference or rewrite either CanonicalWorkLease predecessor fixture;
those bytes remain separately identity-checked. The sequence checker compares
the event fixtures' declared reference identities and digest values but does
not recompute an event digest, canonical digest, or stream digest.

The retained start evidence is deliberately partial:

```text
commit.attempt-start.local.001, batch size 3
  0 resource.reservation_claimed
  1 attempt.started
  2 verification.started            # referenced, not dereferenced
```

Only positions 0 and 1 are dereferenced. The evidence therefore does not claim
a complete `attempt.start` cohort, and stream positions 15 through 19 are also
outside the dereferenced sequence.

The retained report evidence is one complete three-event cohort:

```text
commit.attempt-report.local.001, batch size 3
  0 attempt.completed
  1 resource.usage_observed
  2 work.lease_released
```

A later one-event commit contains `resource.reservation_settled`. Across those
retained subjects the checker requires one reservation identity, the exact
claim and usage references, causal links, controlled chronology, adjacent
declared stream-digest values, and one identical non-fungible dimension-key set.
For each dimension `d`, it checks:

```text
reserved_consumed[d] = min(ceiling[d], actual[d])
unused[d]            = max(ceiling[d] - actual[d], 0)
overage[d]           = max(actual[d] - ceiling[d], 0)
billed[d]            = actual[d]
refunded[d]          = 0
net[d]               = reserved_consumed[d] + overage[d] - refunded[d]
```

No execution, money, or verification-capacity dimension may compensate for
another. This is bounded retained-fixture dereference, not reducer replay,
cryptographic verification, external observation, billing evidence, or proof
of a complete stream.

## Retained refusal boundary

The candidate checks refuse, among other mutations:

- release reverting the reservation to `unclaimed` or dropping the exact claim
  reference;
- crash release or lease-owned resource settlement;
- a mismatched reservation, claim, usage, or settlement reference;
- a split or reordered three-event report cohort;
- a claimed reservation settled without the exact later ResourceLedger event;
- changed dimension keys, cross-dimension substitution, or incorrect
  per-dimension equations;
- stale ResearchEvent identity in a synthetic current projection; and
- promotion of the compatibility correction into C5, PRQ-009, admission,
  runtime, or Gate A closure.

The current working inventory is 112 schemas and 826 shared-manifest cases.
The lifecycle audit measures 222 of 229 refusal statements and 108 of 111
top-level boolean conditions; the first-slice suite retains 12 safe cases and
61 known-bads; the projection suite retains 63 cases. These are working-tree
architecture measurements pending exact-commit rehearsal. They are not
publication evidence.

## Consequences

`C5-WORK-LEASE-RELEASE-CLAIM-001` is corrected for the unissued ResearchEvent
0.18.0 candidate and its exact transitive WorkContract bindings. C5 itself is
not closed. ResearchEvent still has unresolved per-branch payload contracts and
is not admitted, dispatchable, or replay-authoritative. WorkIntent remains
unissued and unassignable; WorkContract remains unconstructible; the exact
thirteen-event assignment cohort, immutable members, reducers, registry/root,
checkpoint/witness/P0/activation chain, complete replay, accountable review,
and operator decision are absent.

PRQ-009 therefore remains `unresolved_blocking`, the canonical profile remains
unissued, and Gate A remains blocked. At decision-authoring time this tranche
had not been committed, rehearsed as an exact descendant, or published.
Repository-release status is not an architecture-decision conclusion and must
be resolved from exact Git state and retained release evidence.
