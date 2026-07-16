# ADR 0019: Materialize a fail-closed WorkLease schema candidate

- Status: Proposed
- Date: 2026-07-16
- Gate: T0 / PRQ-008; architecture-only schema-resource decision

## Context

`ResearchEvent` 0.7.0 binds local attempt records to the exact resource ID
`urn:odeya:schema:canonical-work-lease:0.1.0`, but that resource did not exist
in the schema set. The lifecycle evidence had already fixed the first-slice
state algebra as `unleased | active | released | revoked | expired`, with
`stale` and `completed` restricted to projections. Leaving the resource absent
made every local-attempt WorkLease reference structurally unresolved.

Creating a permissive record would be worse than retaining the gap. The
canonicalization profile, resolved WorkIntent, exact thirteen-event assignment
cohort, immutable state/reducer members, registry membership, and activation
evidence do not yet exist. A schema candidate must expose those blockers and
must not become execution authority by implication.

## Decision

Add `schemas/canonical-work-lease.schema.json` with exact resource identity
`urn:odeya:schema:canonical-work-lease:0.1.0` and classify it as an unissued
`candidate_record` owned by the `work` module.

The candidate fixes these machine-readable laws:

- aggregate absence is `unleased`; records begin only with an acquisition;
- acquisition is `unleased -> active` and creates version one;
- release, revocation, and expiry are terminal transitions from `active`;
- renewal is recorded as `active -> active` global vocabulary but remains
  outside this bounded candidate and is not constructible through it;
- terminal records cannot permit a new start claim;
- `stale` and `completed` are projection-only labels; and
- terminal re-entry is forbidden.

The first-slice resource frontier is separate from lease state. Acquisition
and controlled pre-claim expiry retain an unclaimed reservation. Release after
an attempted execution retains `claimed` plus the exact claim event and cannot
change ResourceLedger state; separate settlement remains mandatory. Revocation
may occur before or after claim but likewise cannot release a claimed hold.

Every currently valid instance is explicitly
`blocked_canonical_record_candidate`, has
`identity_resolution_status = unresolved_blocking`, has null profile and
canonical digest fields, and has
`record_authority_status = not_admitted_not_execution_authority`. It binds the
prospective WorkIntent, worker identity, exact ordered five-role assignment
profile, reservation/assignment event references, controlled time, and latest
lease transition without claiming that the assignment cohort is resolved.

The first-slice event identity map advances to candidate 0.2.0. It removes the
false statement that the resource is absent and instead binds the candidate's
exact path, raw SHA-256, byte count, ownership, direct schema consumer, retained
fixture consumers, and remaining blockers. `ResearchEvent` is not reissued in
this tranche because its bytes and logical event branches do not change.

## Evidence boundary

The shared schema manifest contains positive acquisition and terminal-release
candidates and adversarial mutations for fabricated canonical identity,
authority escalation, projection-state promotion, illegal acquisition
ancestry/version, grant-role reordering, fabricated cohort resolution,
non-profiled time, event/state mismatch, terminal start claims, forgotten
claimed reservations, and unknown fields. The lifecycle checker independently
verifies the state-machine annotation, exact raw-byte identity-map binding,
single defining resource, module ownership, and unchanged
sixty-event/twenty-five-family surface.

That comparison exposes one blocking consumer mismatch rather than hiding it:
`ResearchEvent` 0.7.0 currently requires an unclaimed reservation for
`work.lease_released`. The first-slice flow has already claimed it at
`attempt.start`. Identity-map candidate 0.2.0 records the exact mismatch and
requires a prospective ResearchEvent/EventContractRecord reissue under
PRQ-009.

The canonical migration audit records no new profile blocker from this schema:
its timestamps use the fixed UTC microsecond shape, numeric control fields are
bounded integers, every digest field has a machine-readable scope annotation,
all local references resolve, and its definition names do not add divergence.

These are finite architecture checks. The retained semantic cases reject
reversed candidate bounds and one reference-digest mismatch, but they do not
recompute referenced digests, prove general runtime temporal ordering,
establish object existence, admit a WorkLease member, prove a reducer,
authorize assignment or execution, or complete Gate A.

## Consequences

- The missing-file portion of PRQ-008 is removed.
- PRQ-008 remains `unresolved_blocking`; schema presence is not canonical
  record identity or authority.
- PRQ-009 remains open: no complete assignment cohort or constructible admitted
  WorkIntent/WorkContract path exists, and the release/claimed-reservation
  mismatch must be reissued.
- A later profile or authority change requires a prospective resource reissue;
  bytes may not change beneath an admitted identity.
- No command, event discriminator, aggregate, reducer family, owner module,
  runtime package, external effect, or deployment surface is added.

## Alternatives rejected

- Keep the resource absent: preserves an avoidable dangling architecture
  dependency and prevents direct contract testing.
- Embed a lease record only inside `ResearchEvent`: conflates event payload and
  standalone state-resource identity.
- Mark the new candidate resolved or admitted: fabricates profile, registry,
  reducer, assignment, and activation evidence.
- Treat `stale` or `completed` as lease states: allows projection language to
  mutate the canonical fold.
- Import general scheduling into the first slice: broadens the dependency set
  without evidence that the bounded verification profile requires it.

## Acceptance boundary

This ADR is proposed architecture evidence only. Accountable reviewers and
Daniel have not accepted it. Gate A remains blocked until the canonical
profile and version axes are frozen, WorkIntent and the exact assignment cohort
are resolved, all transitive identities are reissued and retained, immutable
state/reducer/event/command members and activation evidence exist, independent
implementations reproduce the fold, known-bad traces fail, and the exact
candidate receives operator acceptance.
