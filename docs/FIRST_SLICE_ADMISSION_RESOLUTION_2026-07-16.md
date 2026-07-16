# First-Slice Admission Resolution Candidate

Status: bounded architecture-scope candidate with C5/PRQ-009 blocked; not
admitted, 2026-07-16.

Source checkpoint:
`f4429ce5ca71e58ebb5d65776a45ebb6a2a18889`.

This is candidate 0.2.0. It supersedes candidate 0.1.0 at that checkpoint
(Git blob `a7983e273d043966c93786f0edeb42bdf173d84a`, raw SHA-256
`sha256:83a16f9f6b2eff834f0bc7869fb6188e4ee04af7201a1338341a4ea2a1f508dc`).
No canonical predecessor digest is claimed because no frozen artifact
canonicalization profile exists.

The 121-name command vocabulary remains an immutable planning extraction from
the retained `CommandEnvelope` 0.4.0 Git bytes at this checkpoint (blob
`6e500377e176f686918390cfea63e165df0c6fcf`, raw SHA-256
`sha256:ad8b96a589051624dfc59d4a429a6529e3b91f7e18a9005cc615b9fa73dbbc30`,
103272 bytes). Retention through Git is architecture-only and blocking; those
bytes are not an admitted registry member. The current 0.5.0 envelope candidate
is not silently substituted as the vocabulary source.

Machine companion:
[`architecture/first-slice-admission-resolution-candidate.json`](../architecture/first-slice-admission-resolution-candidate.json).

Exact event/payload branch companion:
[`architecture/first-slice-event-identity-map.json`](../architecture/first-slice-event-identity-map.json).

Decision records:
[`ADR 0014`](decisions/0014-resolve-first-slice-atomic-admission.md) and
[`ADR 0017`](decisions/0017-close-first-slice-lifecycle-origins.md).

This document supersedes the unresolved scope hypothesis in
[`FIRST_SLICE_ADMISSION_CLOSURE_PLAN.md`](FIRST_SLICE_ADMISSION_CLOSURE_PLAN.md)
for candidate counts and the bounded C1-C4/C6-C8 decisions. C5 is reopened as
blocking because the retained evidence has no constructible resolved
WorkIntent or complete assignment cohort. The older plan remains retained as
the audit trail showing why those choices were refused. This resolution is not
an immutable registry, RegistryActivation, EngineContractRoot, proof-mission
trace, Gate A decision, runtime surface, or implementation authorization.

## Verdict

C1-C4 and C6-C8 now have bounded architectural resolutions. C5 and PRQ-009
remain explicitly unresolved. The resulting candidate scope is exact as a
representational set, but it is not construction-complete:

| Item | Exact candidate count | What it does and does not mean |
|---|---:|---|
| Design-vocabulary commands audited | 121 | exact current design surface; none is executable by this document |
| Commands required by the bounded slice | 43 | exact candidate set; 0 immutable CommandContractRecords exist |
| Commands outside the bounded slice | 78 | exact complement under this profile; they remain design vocabulary |
| Closed required command-payload candidates | 1 | `data_use.decide`; not enrolled |
| Missing required command-payload contracts | 42 | construction gap, not permission to use generic payloads |
| Required unique event discriminators | 60 | exact set, not event occurrence cardinality |
| Aggregate/state/reducer families | 25 | exact dependency set; 0 first-slice member records exist |
| Owner modules | 11 | exact logical ownership set; not runtime packages |
| Separately admitted prerequisites | 1 | P0 is required; 0 accepted P0/activation instances exist |
| Unresolved C1-C8 choices | 1 | C5/PRQ-009 lacks a constructible resolved WorkIntent and complete exact assignment binding |

The set is dependency-bounded only at the architecture-representation level.
It is not dependency-complete for activation until every exact member and the
P0 instance exist. Count equality therefore may be tested now; admission,
implementation, and scientific claims may not.

## Scope recomputation

Starting from the old 44-command hypothesis:

- remove `dependency.record_invalidation`; `claim.supersede` owns the complete
  correction cohort;
- remove `measurement.determine_disposition`; `run.determine_validity` owns the
  complete validity/measurement pair;
- remove `verification.start`; it is not a second execution-start authority;
- add `attempt.start`; it owns the atomic local attempt plus verification start;
- add `attempt.report`; it owns local execution observations and terminality.

The result is 43 required commands and 78 outside commands. The exact lists are
machine-bound in the companion inventory.

The old 52-name conflict union becomes 60 exact event discriminators:

- remove `resource.observed` from resource truth;
- add `work.lease_acquired`, `work.lease_released`, `work.lease_revoked`, new
  `work.lease_expired`, `attempt.started`, `attempt.interrupted`,
  `attempt.completion_unknown`, `attempt.completed`, and `attempt.failed`;
- do not admit `attempt.cancelled`: before start there is no Attempt aggregate,
  and after start cancellation alone cannot prove no byte visibility or use.

The `work_item / WorkLease / work` and
`attempt / AttemptExecution / work` rows enter the aggregate dependency set,
raising it from 23 to 25 and owner modules from 10 to 11.

## Lifecycle prerequisite closure

ADR 0017 closes four construction prerequisites without adding or removing a
command, event discriminator, aggregate, reducer family, or owner module. The
candidate counts remain exactly 43 commands, 60 events, 25 families, and 11
owners.

- AuthorityGrant issue is `not_issued -> issued`; controlled activation is the
  separate `issued -> active` fact. Expiry/revocation are legal from issued or
  active, and a single-use grant's final use/exhaustion is atomic.
- `protocol.frozen` is the protocol aggregate's origin from absence, creating
  version 1 with the exact frozen snapshot and draft, validation, exposure,
  integrity, and bounded-protocol-grant evidence. There is no hidden canonical
  draft/version-zero state.
- `data_use.decided` consumes the exact `data_rights` bounded grant in the
  ordered atomic `grant_used -> decision -> grant_exhausted` cohort;
  assignment-only authority is rejected.
- WorkLease canonical state is exactly `unleased | active | released | revoked
  | expired`; stale/completed are projection-only work descriptions.

The identity companion binds every one of the 60 event types to its exact
event semantic version, logical payload type ID/version, owner, and exact
ResearchEvent resource bytes plus branch pointer. Event and logical payload
type versions are independent. The current map retains 60 event-v1 branches
and exactly four logical-payload-v2 branches
(`verification.assigned`, `verification.completed`,
`verification.disputed`, and `reproducibility.determined`). Immutable payload
contract resources, extraction/canonicalization, digest resolution,
EventContractRecords, and activation still do not exist; the mapping is
architecture evidence, not admission. It also records the referenced
`urn:odeya:schema:canonical-work-lease:0.1.0` resource as missing and blocking.

The containing ResearchEvent schema is reissued as 0.7.0 because the lifecycle
closure changes required bytes and meaning. The former 0.6.0 candidate is
historical Git evidence only and was never issued; it is not retained as a
current alias. This reissue changes neither the 135-branch global vocabulary
nor the exact 60-event first-slice set.

## C1 — one resource truth path

`ResourceLedger` reduces exactly six event types:

```text
resource.reservation_created
resource.reservation_claimed
resource.reservation_released
resource.reservation_expired
resource.usage_observed
resource.reservation_settled
```

`resource.record_observation` accepts one immutable raw observation artifact.
The kernel verifies its reservation, dimension, axis, unit profile, source,
time, and current observation frontier, then emits one typed
`resource.usage_observed`. If and only if that observation completes the
creation-bound settlement profile and equations, the same atomic batch also
emits `resource.reservation_settled`.

Settlement requires exact `actual_usage` over every non-money dimension and
exact `billed` plus `refunded` observations over every money dimension.
`attempted_usage` is retained diagnostic evidence but is not settlement
authority. Zero must be observed. For the no-money offline profile, the money
domain is explicitly empty/not-applicable; execution or verification units may
not be smuggled into billed/refunded money vectors. Missing, unavailable,
withheld, unmeasured, duplicate, conflicting, or dimension-incomplete evidence
keeps the full claimed ceiling held.

One VerificationRun owns one combined non-fungible reservation vector covering
its execution and IV0-IV4 capacity coordinates. A second clean replay is a
second VerificationRun and a second reservation; it is never another use of the
first run's hold.

## C2 — correction is one source-fence cohort

`claim.supersede@2` is the sole first-slice producer of:

```text
claim.superseded@2
dependency.invalidation_recorded@2
```

Both events share one command ID, receipt, canonical request digest,
correlation ID, commit ID, contiguous batch, and mission stream. The command
locks the mission allocator plus claim-version and dependency-frontier heads,
orders supersession before invalidation, compare-and-sets both heads, and
publishes no receipt, checkpoint, reducer state, or current projection at an
interior batch position.

Immutable ClaimVersion records are the canonical source of exact typed
dependency edges. The dependency event stores a monotone transitive invalid
source fence against an exact prior frontier. Reverse fanout and
ProjectionImpactRecord are rebuildable projections, not authority. Claim
compilation, eligibility, publication, and current serving recursively evaluate
exact ClaimVersion dependencies against the fence. Unknown targets, cycles,
traversal bounds, stale frontiers, or unavailable bytes fail ineligible.

## C3 — validity and measurement settle together

`run.determine_validity@2` is the sole first-slice producer of the atomic pair:

```text
run.validity_determined@2
measurement.disposition_determined@2
```

Its closed matrix is:

| Run validity | Measurement disposition | Result |
|---|---|---|
| `valid` | `valid_measurement` | legal |
| `valid` | `no_valid_measurement` | legal |
| `invalid` | `no_valid_measurement` | legal |
| `invalid` | `valid_measurement` | forbidden |

Indeterminate inputs reject before domain facts. Both aggregates originate in
the same batch; an absent aggregate is not a canonical pending fact. Downstream
metric, adjudication, claim, and current-projection admission requires the exact
conjunction `valid + valid_measurement`. Invalid diagnostics may remain visible
only as explicitly non-claim-bearing evidence.

## C4 and C6 — nonrecursive authority and exact grant slots

The authority modes are closed:

- `ingress_policy`: thesis submission only; no grant;
- `constitutional_bootstrap`: first root assignment only; no assignment or
  operational grant created by the target;
- `assignment_only`: authority maintenance and deterministic controlled-time or
  lease observations; the target grant never authorizes its own lifecycle;
- `bounded_grants`: ordinary consequential commands.

The AuthorityGrant lifecycle is also closed before member construction:

```text
not_issued -> issued
issued     -> active | expired | revoked
active     -> exhausted | expired | revoked
```

Issue never skips directly to active. Expiry and revocation accept only issued
or active source state; no terminal state can be reopened.

Every bounded grant is distinct, action-instance-bound, single-use, and bound
to the exact command ID, request digest, target, role slot, controlled-time
window, and `domain_commit` consumption point. The global role-slot order is:

```text
proposal < protocol < safety < data_rights < resource
< execution < verification < outcome < publication
```

For an accepted branch with N slots, the batch contains exactly N
`authority.grant_used` occurrences before the domain cohort and exactly N
`authority.grant_exhausted` occurrences after it, each bound to one slot in the
same order. Because first-slice operational grants have `max_uses=1`, the used
and exhausted sets are equal. Rejection, noop, and exact idempotent replay emit
zero new uses or exhaustions. One grant cannot fill two slots.

Important plural profiles are:

| Command branch | Ordered role slots |
|---|---|
| `proposal.decide(defer|decline)` | proposal |
| `proposal.decide(admit)` | proposal, safety, data_rights, resource |
| `verification.assign` | safety, data_rights, resource, execution, verification |
| `attempt.start` | safety, data_rights, resource, execution, verification |
| `claim.supersede` | protocol, verification |

Other ordinary commands have one exact role slot as enumerated in the machine
inventory. `attempt.report` and `verification.invalidate` each have a caller
bounded-grant branch and a non-caller-selectable deterministic-observation
branch under an active assignment. Command contract records must close those
alternatives; callers cannot choose `assignment_only` in their payload.

## C5 — local materialization and execution

The bounded slice uses a specialized local verification profile. It does not
import general work-graph/stage orchestration, provider/model dispatch,
data-exposure settlement, or external effects.

Its WorkLease fold has exactly five states: `unleased`, `active`, `released`,
`revoked`, and `expired`. Acquisition moves unleased to active; the other
three events terminate an active lease. Stale/completed labels may be derived
for UI or wider work projections but are never canonical lease facts.

Before assignment, the input artifacts, current DataUseDecisions, resolved
assignable WorkIntent, local materialization intent, sandbox
policy/capability, and resource profile must exist as exact immutable
candidates. The WorkContract is a post-assignment artifact and cannot be used
as the prospective input from which its own lease and reservation are created.
No source byte is mounted.

The canonical sequence is:

1. `verification.assign` must recheck the exact WorkIntent, rights, protocol,
   independence, resource, sandbox, and worker identities. Its prospective
   exact 13-event transaction is five ordered `authority.grant_used` events,
   `resource.reservation_created`, `work.lease_acquired(unleased -> active)`,
   `verification.assigned`, then the matching five ordered
   `authority.grant_exhausted` events. The resulting WorkContract must bind the
   exact WorkIntent and assignment commit. The transaction creates no launch
   outbox and permits no byte visibility.
2. `attempt.start` locks and rechecks the current activation/frontier, artifact
   digests, DataUseDecisions, WorkContract, local intent, sandbox capability,
   lease, reservation, controlled time, and five separate start grants. One
   transaction consumes the grants, claims the reservation, records
   `attempt.started` and `verification.started`, records the local-launch outbox,
   and exhausts the grants. Only after the whole commit may a deterministic
   launcher mount read-only bytes and spawn the process.
3. `attempt.report` records exactly one of completed, failed, interrupted, or
   completion-unknown together with actual input/code/environment manifests,
   visibility state, sandbox negative-flow audit, teardown/residual state, and
   raw resource observation references. It does not settle ResourceLedger and
   does not determine scientific validity. Clean observed teardown may release
   the lease; a controlled failure may revoke it; unknown execution cannot
   claim clean release.
4. `verification.complete` requires an immutable terminal attempt and exact
   verification package. Execution completion alone never implies confirmed,
   independently reproduced, or scientifically supported.

The local profile has exact zero ceilings for network egress, providers,
models, ambient credentials, external writes, cloud jobs, GPU use, and spend.
Unknown visibility, input identity, sandbox containment, or teardown fails
clean-room and independence claims; it never becomes `none_exposed`.

## Reservation, lease, and invalidation races

Assignment/start/invalidation/expiry lock the verification, work item,
resource budget, and required grant heads in canonical identifier order.

- Start wins: the reservation is permanently claimed; later invalidation,
  expiry, grant revocation, crash, timeout, callback loss, or restore cannot
  release or expire it.
- Explicit invalidation wins before start: the same cohort records verification
  invalidation, lease revocation, and reservation release; start rejects.
- Controlled deadline wins before start: an assignment-only deterministic
  branch records verification invalidation, lease expiry, and reservation
  expiry; start rejects.
- A prospective start-grant revocation by itself releases no independent
  resource hold. A new exact start grant may be issued before the reservation
  deadline; otherwise the deadline branch expires the reservation.
- Crash after the start commit leaves byte visibility, execution, and use at
  least unknown, fences the lease, retains the full claimed ceiling, and forbids
  blind retry. Only stable reconciliation may append a later attempt report.

## C7 — one Verification reducer

The aggregate owner is `verification / verification / Verification`.
Reproducibility, replication, transport, dispute, invalidation, independence,
and terminal assessment are orthogonal axes of that state. Their pure internal
fold functions may be separately tested, but no axis is registered as a second
canonical reducer and no event is reduced twice. Catalog rows that formerly
named `Reproducibility`, `Replication`, or `Transport` as reducer families must
name `Verification`.

## C8 — nonrecursive constitutional recovery admission

`P0.constitutional-recovery-admission` is not a command, event, grant,
aggregate, policy result, or handoff assertion. It is an immutable prospective
section of the separately admitted RegistryActivation created by the
constitutional genesis/recovery ceremony.

P0 binds:

- the non-self-issued RootAuthorityManifest/bootstrap evidence;
- exact EngineContractRoot and C0 registry bundle;
- exact root checkpoint plus external witness observations and a consistent
  witness verdict;
- exact ledger epoch/global position;
- a current recovery frontier proving no unresolved fork, no quarantine, no
  ambiguous restore/recovery case, and the permitted bounded service scope;
- controlled time, review evidence, and fail-closed invalidation triggers.

Every CommandEnvelope, CommandReceipt, and AdmissionEvidenceBundle binds the
same activation ID, sequence, digest, P0 digest, root, checkpoint, scope, and
recovery-frontier digest. Equality and currentness are semantic admission
checks. A fork, quarantine, recovery ambiguity, epoch change, root/C0 change,
or superseding activation invalidates P0; no mission command continues until a
separately reviewed new activation exists.

Recovery commands stay outside this bounded mission slice only behind this
machine-bound prerequisite. P0 cannot be created, repaired, or selected by an
ordinary first-slice command.

## Exact aggregate dependency set

| Aggregate | Owner | Sole reducer family |
|---|---|---|
| proposal | mission | Proposal |
| mission | mission | Mission |
| protocol | protocol | Protocol |
| authority_assignment | authority | AuthorityAssignment |
| authority_grant | authority | AuthorityGrant |
| data_asset | data_governance | DataAsset |
| rights_assertion | data_governance | RightsAssertion |
| data_use_decision | data_governance | DataUseDecision |
| retention_schedule | data_governance | RetentionSchedule |
| transformation | data_governance | Transformation |
| artifact | artifact | ArtifactCustody |
| work_item | work | WorkLease |
| attempt | work | AttemptExecution |
| run | measurement | RunValidity |
| measurement | measurement | MeasurementDisposition |
| metric | measurement | MetricObservation |
| falsifier | measurement | Falsifier |
| resource_budget | resources | ResourceLedger |
| blocker | mission | Blocker |
| verification | verification | Verification |
| review | verification | Review |
| adjudication | adjudication | Adjudication |
| claim_proposal | claims | ClaimProposal |
| claim_version | claims | ClaimVersion |
| dependency | claims | DependencyInvalidationFrontier |

## Required adversarial evidence

At minimum the next contract tranche must retain known-bad cases for:

- generic or duplicate resource truth, partial settlement, wrong dimension,
  inferred zero, refunded-greater-than-billed, observation before claim, and
  release/expiry after claim;
- missing, extra, reused, wrong-role, wrong-order, partially committed, or
  twice-consumed grants;
- target grants self-issuing, self-revoking, or self-expiring;
- supersession without the dependency fence, split commits, delayed projection
  fanout served as current, and a new claim compiled from an invalid source;
- invalid run without no-valid-measurement, the forbidden invalid/valid pair,
  and any downstream null/support/eligibility claim from invalid evidence;
- missing lease/materialization/sandbox/reservation facts, nonzero external
  capability, stale DUD/input/activation, two starts, expiry-first/start-later,
  start-first/crash/release, unknown visibility represented as none, and
  execution completion represented as scientific confirmation;
- two canonical verification reducers or order-dependent axis composition; and
- missing/stale P0, unwitnessed checkpoint, unresolved fork/quarantine/recovery,
  or an ordinary command attempting to create its own prerequisite.

## What remains blocked

C5/PRQ-009 is unresolved and Gate A is not closeable. The current WorkIntent
candidate is `unresolved_blocking`, has null canonicalization profile and
canonical digest, and is not admitted or assignable. `ResearchEvent` 0.7.0
therefore does not fabricate a WorkIntent reference, and the retained
one-event `verification.assigned` fixture is not evidence of the required
13-event cohort. At least the following remain:

1. 42 exact command-payload schemas and 43 immutable command-contract members;
2. 60 immutable event-contract members and their exact payload-contract bytes;
   the 60-row logical-type/enclosing-schema branch mapping is architecture
   evidence, but payload-contract digest resolution and member admission remain
   unconstructed;
3. 25 state-subject and 25 reducer-contract members;
4. a newly identified resolved WorkIntent, a WorkContract binding that intent
   and assignment commit, a reissued ResearchEvent/EventContractRecord with the
   complete assignment bindings, and exact LocalMaterializationIntent,
   WorkLease, attempt, correction-fence, validity-pair, multi-grant, and
   resource-settlement vectors;
5. a real EngineContractRoot/C0/checkpoint/witness/P0/RegistryActivation chain;
6. bounded formal coverage still missing for correction/validity batch
   visibility, materialization visibility, P0 recovery currentness, and
   variable profiles; the retained composite model now covers the fixed
   five-role grant/resource/start-invalidation-expiry boundary;
7. two independent reducer implementations, two clean scientific verifier
   paths, composite context-loss recovery replay, and independent review; and
8. explicit operator acceptance of the later immutable candidate.

No runtime, application, deployment, external integration, publication, or UI
implementation follows from this resolution.
