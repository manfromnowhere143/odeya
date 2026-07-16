# ADR 0017: Close first-slice lifecycle prerequisites before member construction

- Status: Proposed
- Date: 2026-07-16
- Gate: architecture prerequisite closure only; no registry admission,
  activation, runtime, deployment, publication, or Gate A authority

## Context

ADR 0014 fixed the first-slice representational boundary at 60 event
discriminators and 25 aggregate/state/reducer families, but four lifecycle
contradictions still made prospective member construction unsafe:

1. `authority.grant_issued` skipped the retained `issued` state even though
   `authority.grant_activated` required it as its source.
2. `protocol.frozen` assumed a hidden draft/validated canonical aggregate,
   contradicting the origin law that absence is not state.
3. `data_use.decided` used assignment-only authority even though a
   consequential data-use decision consumes the `data_rights` bounded grant.
4. WorkLease prose named `stale` and `completed` as canonical states while the
   first-slice event algebra terminates leases as released, revoked, or
   expired.

The exact relationship between an event semantic version, its logical payload
type identity, the enclosing ResearchEvent schema resource, and the
corresponding branch was also only implicit. That ambiguity is unacceptable
before immutable per-payload contracts and EventContractRecords are
constructed.

## Decision

Close the candidate lifecycle algebra without changing the 60-event or
25-family member sets.

### AuthorityGrant

The legal candidate lifecycle is:

```text
not_issued --authority.grant_issued--> issued
issued     --authority.grant_activated--> active
issued     --authority.grant_expired|authority.grant_revoked--> terminal
active     --authority.grant_expired|authority.grant_revoked--> terminal
active     --authority.grant_used + authority.grant_exhausted--> exhausted
```

Operational first-slice grants are single-use. Their final use and exhaustion
are one commit; no globally visible state may expose a consumed active grant.
Issued, active, exhausted, expired, and revoked are retained facts, not wall
clock interpretations.

### Protocol origin

`protocol.frozen` is the origin fact for the canonical protocol aggregate in
this bounded slice. It materializes version 1 from aggregate absence and
requires all of the following exact evidence:

- no prior canonical protocol reference;
- one frozen `ProtocolSnapshot` reference with an exact schema identity,
  version, and digest;
- the source draft artifact, one or more validation artifacts, and the exact
  exposure-history digest;
- the exact versioned integrity rule; and
- one ordered atomic commit:
  `grant_used(protocol) -> protocol.frozen ->
  protocol.integrity_determined -> grant_exhausted(protocol)`.

Draft and validation are pre-origin evidence, not hidden reducer states. A
later amendment or fork requires a separately versioned prospective contract;
it cannot reuse this absence-origin branch.

### Data-use authority

`data_use.decided` requires `bounded_grants`, the exact `data_rights` role
slot, and one ordered three-event commit:

```text
authority.grant_used(data_rights)
data_use.decided
authority.grant_exhausted(data_rights)
```

The authority evidence and payload binding name the same grant and grant-use
event. The domain event is commit index 1 of size 3. Assigned role alone,
split commits, missing exhaustion, a different role slot, or a different order
are invalid candidates.

### WorkLease vocabulary

The canonical first-slice WorkLease states are exactly:

```text
unleased | active | released | revoked | expired
```

Acquisition is `unleased -> active`. Release, revocation, and expiry are
terminal transitions from active. `stale` and `completed` may be computed UI
or operational descriptions of wider work state, but they are not canonical
WorkLease states and cannot be reducer inputs or outputs.

### Event and payload identity

Retain
[`architecture/first-slice-event-identity-map.json`](../../architecture/first-slice-event-identity-map.json)
as architecture evidence binding each of the exact 60 event types to:

- its exact `event_version`;
- its exact logical `payload_type_id` and logical payload type version;
- its aggregate owner; and
- the exact `ResearchEvent` 0.7.0 resource ID, raw-byte digest, byte count,
  discriminator branch, and payload JSON Pointer in the retained source
  bytes.

Event semantic version and logical payload type version are independent
identities.
The current candidate has 60 event-v1 branches and four payload-v2 branches:
`verification.assigned`, `verification.completed`,
`verification.disputed`, and `reproducibility.determined`. A reader must select
the branch by exact event identity plus exact logical payload type identity; it may
not infer one version from the other or resolve a `latest` alias.

The logical payload type URN is not a JSON Schema `$id`. The map binds the
current event branch to the exact enclosing `ResearchEvent` resource bytes,
but it does not pretend that immutable per-payload contract members already
exist. In 0.7.0 every `payload_contract_resolution_status` is
`unresolved_blocking`, every `payload_contract_digest` is null, and every
event has `event_contract_authority_status` equal to
`not_admitted_not_dispatchable_not_replay_authoritative`. A future resolved
payload contract requires a new `ResearchEvent` resource identity that freezes
the exact extraction and canonicalization profile; no current logical URN,
branch pointer, or enclosing-schema digest may be substituted for that missing
contract digest.

Because this decision changes required ResearchEvent payload structure,
authority meaning, and reducer-transition meaning, the containing
`ResearchEvent` schema is prospectively reissued from 0.6.0 to 0.7.0. All
current exact references and retained fixtures migrate to 0.7.0. The 0.6.0
candidate remains available only through historical Git bytes; it was never
issued as an immutable registry member and is not a readable-current alias.
The reissue preserves all 135 global branches and the exact 60-event
first-slice set.

## Evidence

The finite checker in
[`tests/lifecycle-closure`](../../tests/lifecycle-closure/README.md) verifies:

- the exact schema transitions and atomic cohort constraints;
- positive issue/activate/use/exhaust, expiry, and revocation traces;
- adversarial skipped-state, pre-activation use, premature exhaustion, and
  post-terminal traces;
- safe and adversarial protocol-origin, data-use, and WorkLease traces;
- exact identity-map equality with the ResearchEvent branches; and
- preservation of 60 event discriminators and 25 families.

These traces are necessary finite architecture evidence, not a proof of
database isolation, reducer determinism, reference resolution, digest
correctness, or runtime behavior.

## Consequences

- Prospective AuthorityGrant, Protocol, DataUseDecision, and WorkLease member
  design may proceed against one coherent lifecycle algebra. This is not
  permission to construct or resolve the WorkLease member: the exact
  `urn:odeya:schema:canonical-work-lease:0.1.0` resource referenced by
  `ResearchEvent` does not exist and requires a separate reviewed
  schema/test/ownership tranche.
- No new event discriminator, aggregate, reducer family, command, or owner
  module is introduced.
- Protocol draft/validation remain immutable evidence outside canonical
  protocol state until the origin commit succeeds.
- Data-use decisions cannot be created through role assignment alone.
- UI projections must translate stale/completed work descriptions without
  writing those labels into the WorkLease fold.
- Any future change to a frozen event meaning or payload contract requires a
  prospective semantic/schema identity; bytes may never change beneath an
  admitted identity.

## Alternatives rejected

- Keeping issue as `not_issued -> active`: activation would be unreachable or
  duplicative.
- Treating draft as an implicit version-zero aggregate: absence would become
  hidden mutable state and replay origin would be ambiguous.
- Allowing assignment-only data-use decisions: a consequential permission
  boundary would bypass the action-bound data-rights grant.
- Exhausting the grant in a later commit: an active but already-consumed grant
  could become visible or race revocation/replay.
- Retaining stale/completed as lease states: they conflate lease authority with
  freshness and work outcome.
- Inferring payload version from event version: the existing four v1/v2
  mappings prove the axes are independent.

## Acceptance boundary

This ADR closes architecture prerequisites only. Gate A remains blocked on
immutable payload, event, state-subject, reducer, command, root, checkpoint,
P0, and activation members; exact digest resolution; independent semantic and
replay implementations; bounded concurrency evidence; and explicit operator
acceptance. No runtime work follows from this decision.
