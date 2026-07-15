# Orthogonal State Model

Status: architecture-closure candidate, 2026-07-15. Canonical events are facts; these states are deterministic projections at an exact stream position under a named reducer set.

The central rule is that operational progress, evidence validity, scientific outcome, claim maturity, replication, and publication are different axes. Odeya must never encode them in one status.

## Stream, aggregate, and reducer boundary

`research-event` 0.6.0 carries a general stream rather than requiring a mission on every fact. Portfolio, proposal, constitutional-authority, data-governance, and global recovery history may exist outside a mission; mission, incident, mission-derived learning, and mission-scoped data-governance facts require an exact mission scope. Recovery facts forbid a mission scope. A projection key is:

```text
stream_id + stream_position + aggregate_type + aggregate_id +
aggregate_version + reducer_name + reducer_version + reducer_digest
```

The catalog assigns every current event exactly one owning aggregate and one reducer name. Exact reducer contracts, versions, digests, and independent implementations remain Gate A work. A projector must reject an event with a wrong aggregate owner, unknown semantic major version, missing position, broken previous digest, or unresolvable reducer. Search indexes, vector stores, caches, workflow state, and UI views are disposable projections and never state authorities.

The default state of an aggregate is created only by its origin fact. Absence of an aggregate is not a hidden state. In particular, a declined pre-mission proposal does not create a mission with `phase=closed`.

## State axes

### Proposal aggregate

```text
admission: pending | admitted | deferred | declined | withdrawn
```

### Mission aggregate

```text
phase: intake | orient | contract | preregister | preflight | execute |
       verify | adversarial_review | adjudicate | handoff | learn | closed
control: open | paused | quarantined | closing | closed
```

`phase` describes scientific workflow position. `control` describes whether work may proceed. A paused mission does not move backward or acquire a scientific result.

### Protocol branch

```text
seal: draft | validated | frozen | superseded
confirmatory_integrity:
  clean | exploratory_only | compromised | unknown | not_applicable
exposure: outcome_blind | partial_outcome_exposure | full_outcome_exposure
```

Exposure is a monotonic event history, not a mutable flag that can be cleared. `protocol.integrity_determined` records the exact consequence of the frozen rule over the retained exposure history; an amendment never silently restores `clean`.

### Stage

```text
readiness: pending | ready | blocked | completed
authorization: not_required | missing | active | expired | revoked | exhausted
```

### Work item

```text
lease: unleased | active | stale | revoked | completed
```

One worker may hold a proposal lease; only the kernel application service writes canonical state.

### Attempt

```text
execution:
  not_started | running | interrupted | completion_unknown |
  completed | failed | cancelled
```

An attempt's `completed` state means the worker returned a result manifest. It does not imply artifact promotion, valid measurement, stage completion, verification, or external settlement.

### Resource budget and child reservations

`resource_budget` is the sole aggregate owner. Each `reservation_id` identifies one immutable child lifecycle inside that aggregate; it is not a second aggregate and never has an independently writable head.

```text
reservation:
  none -> active -> claimed -> settled

  active -> released
  active -> expired
```

Creation binds the exact budget head, subject, non-fungible unit profile, estimate vector, ceiling vector, expiry, and complete start cohort. Claim is legal only from `active` and commits atomically with every named work/effect/verification start fact. It moves the whole ceiling from an active hold to a claimed hold; it does not assert attempted, actual, billed, or refunded use. `released` and `expired` are pre-claim terminals. Worker death, callback loss, crash, recovery, timeout, and `completion_unknown` leave a claimed reservation and its entire ceiling held.

Usage observations retain separate `attempted`, `actual`, `billed`, and `refunded` axes. Each axis is `observed`, `missing`, or `unavailable`; only `observed` carries a vector. Missing and unavailable are not zero. Settlement is legal only from `claimed`, requires the exact retained observation set, and reduces the hold to zero. For every resource dimension `d`, the reducer enforces:

\[
\operatorname{net}_d=\operatorname{reservedConsumed}_d+\operatorname{overage}_d,
\qquad
\operatorname{ceiling}_d=\operatorname{reservedConsumed}_d+\operatorname{unused}_d.
\]

For money, `net = billed - refunded`; for non-money resources, `net = actual`. All terms are non-negative, and `refunded <= billed`. At reserve time, `available_before_d = available_after_d + ceiling_d`; at a pre-claim terminal, the exact ceiling returns; at settlement, only `unused_d` returns and `reservedConsumed_d` remains consumed. Overage is recorded as a separate budget breach/liability and is never hidden by another dimension.

Execution units, each currency in minor units, and the five verification-capacity dimensions—deterministic replay, compute, expert, physical, and safety—are different basis elements. No reducer converts or compensates across them. Abundant compute therefore cannot satisfy absent expert, physical, or safety capacity.

### External effect

```text
settlement:
  not_intended | authorized | started | cancelled_before_dispatch | confirmed_applied |
  confirmed_not_applied | completion_unknown

reconciliation:
  not_required | pending | running | completed | failed | manual_review
```

Every externally consequential action, including publication, has an effect record and provider idempotency/reconciliation semantics.
`cancelled_before_dispatch` is reachable only from `authorized` in the same commit that terminally releases or invalidates every exact dispatch-bound grant/resource reservation. It proves that no canonical dispatch claim won; it does not assert a provider-side `confirmed_not_applied` observation.
Reconciliation records the process; it never erases settlement polarity. A completed reconciliation must leave settlement as `confirmed_applied` or `confirmed_not_applied` and retain the prior ambiguity history.

### Artifact

```text
custody:
  staged | validated | promoted | quarantined |
  corrupt | unavailable | tombstoned
```

Only promoted artifacts can support claims. Tombstone preserves identity and lawful-removal reason when bytes cannot remain.

### Run and measurement

```text
validity: pending | valid | invalid
measurement: not_observed | valid_measurement | no_valid_measurement
```

`invalid` answers whether scientific interpretation is allowed. `no_valid_measurement` answers whether the run produced a measurement under the protocol. Neither is a null result.

### Adjudication

```text
scientific_outcome:
  not_adjudicated | supported_within_scope | contradicted |
  falsified | null_result | inconclusive
```

Scientific outcome exists only for a valid run under a frozen consequence rule.

### Verification

```text
lifecycle projection:
  not_requested | requested | running | terminal

immutable terminal package:
  confirmed | rejected | inconclusive | invalid | blocked

dispute overlay:
  none | open | resolved
```

Request, assignment, start, and completion are event-derived lifecycle facts. `VerificationPackage` is an immutable terminal record for one run with an exact subject set, frozen IV0–IV4 and independence requirement, planned-versus-actual execution identity, execution path, observed correlation vector, controls, required dimensions, exposure audit, actual resource observations, typed outcome basis, discrepancies, counterexamples, and unknowns. `confirmed` means the exact assigned profile passed; a same-team IV0 confirmation is not an independent scientific confirmation. `requested`, `running`, and `disputed` are not terminal package values. Several packages can coexist; dispute events reference exact package bytes and never rewrite their assessment. See [Verification Protocol](VERIFICATION_PROTOCOL.md).

### Reproducibility, replication, and transport

```text
reproducibility:
  not_attempted | same_evidence_recomputed | clean_reproduction |
  not_reproduced | inconclusive | invalid

replication:
  not_required | not_attempted | running | independently_replicated |
  not_replicated | inconclusive | invalid

transport:
  not_required | not_attempted | running | transported |
  transfer_failed | inconclusive | invalid
```

Recomputing the same bytes is reproducibility. Replication requires new diagnostic data or measurement. Transport requires a predeclared external context.

### Claim proposal and immutable version

```text
proposal_disposition:
  proposed | admissible | preregistered | withdrawn | superseded

claim_version_projection:
  compiled_ineligible | compiled_eligible | superseded | retraction_notice
```

Adjudication and required verification runs are separate objects referenced by a compiled claim version. Claim bytes are immutable at creation; “sealed” belongs to the publication manifest, not the claim lifecycle. A correction creates a new claim version and supersession edge. It is not a terminal scientific verdict.

### Publication aggregate

```text
release:
  not_requested | requested | denied | authorized | sealed |
  releasing | completion_unknown | released | withdrawn

visibility: private | restricted | embargoed | public
```

Release is not a mission phase. A mission can hand off and learn without publication. A released result can later be corrected or withdrawn without rewriting the scientific lifecycle.

### Incident and authority

```text
incident: open | contained | investigating | resolved | superseded
grant: issued | active | exhausted | expired | revoked
grant-use reservation per reservation ID:
  active | released | expired | cancelled | consumed
```

Grant state derives from immutable issue, controlled activation, use-reservation, reservation release/expiry/cancellation, use consumption, exhaustion, expiry-observation, and revoke events. The projection keeps authorized maximum uses, active reserved uses, and consumed uses separate; `available = maximum - reserved - consumed` only when every term is known and compatible. A reservation is bound to one exact command/effect and cannot migrate. Wall-clock time can deny admission before an expiry event is projected, but replay at a ledger position never invents expiry from the reader's current clock.

Ordinary in-ledger actions reserve and consume in one command transaction. Cross-boundary effects whose grant remains revocable before dispatch reserve at effect intent and consume only in the atomic dispatch-claim transaction. Revoke/expiry/cancel first releases or invalidates the reservation and blocks claim; claim/use first creates an in-flight historical fact.

The canonical reducers consume these exact facts:

- `authority.grant_use_reserved` creates `active` only for `consumption_point=dispatch_claim` and subtracts its exact count from available capacity.
- `authority.grant_used(consumption_point=dispatch_claim)` may move only its named active reservation to `consumed`, in the same batch as `external_effect.started`.
- `authority.grant_use_reservation_released` moves only `active -> released | expired | cancelled`; its closed reason must match the terminal class.
- `external_effect.cancelled_before_dispatch` moves only `authorized -> cancelled_before_dispatch`, in the same batch as terminal release/invalidation of every named reservation and without a grant-use event.

### Data governance

Data governance is not one sensitivity status. The owning reducers keep the following axes separate:

```text
data_asset.lifecycle:
  not_recorded | proposed | admitted | quarantined | held |
  deletion_pending | tombstoned | unavailable | prohibited | indeterminate

rights_assertion.status:
  asserted | disputed | withdrawn | basis_unavailable

data_use.authority:
  missing | authorized | denied | indeterminate | revoked | expired

data_exposure.settlement:
  not_intended | authorized | confirmed_exposed |
  confirmed_not_exposed | completion_unknown

retention.schedule:
  proposed | active | denied | indeterminate

deletion.case:
  requested | scoping | blocked_by_hold | authorized | in_progress |
  limited | completed | denied | indeterminate

legal_hold:
  not_active | active | released | expired | indeterminate
```

`rights_assertion.recorded` can change only the assertion axis and carries
`authority_effect=evidence_only_no_permission`. `data_use.decided` is the only
founding fact that can move data-use authority from `missing` to a bounded
decision. `data_use.revoked` is monotonic for that decision version; later use
requires a new decision identity, never resurrection.

Exposure intent, observation, and settlement are distinct facts. Intent does
not dispatch bytes. `completion_unknown` remains unknown until an admitted
settlement observation proves exposed or not exposed; a timeout, deletion, or
missing provider receipt cannot reduce it to zero. Historical recipient/model
exposure remains monotonic after deletion.

A completed deletion case requires exact verified plane results, zero declared
residual copies, at least one tombstone consequence, and all required scientific
invalidation/correction consequences. The data-asset reducer then moves the
affected asset to `tombstoned`; restore cannot move it back to `admitted` without
a new lawful byte identity and new decision. A legal hold pauses only covered
destruction and has no positive access-authority transition.

### Ledger integrity and recovery

```text
checkpoint:
  not_proposed | proposed | sealed | witnessed | consistency_failed

backup.write:          not_run | pass | fail | indeterminate
backup.verification:   not_run | pass | fail | indeterminate
backup.recoverability: not_run | pass | fail | indeterminate

restore_case:
  not_opened | isolated | report_recorded | decided | closed

security_frontier:
  missing | incomplete | indeterminate | proven_complete

recovery_control:
  isolated | quarantined | read_only |
  reconciliation_only | bounded_research_writes

ledger_integrity:
  continuous | fork_detected | quarantined | new_epoch
```

Checkpoint proposal, seal, witness observation, and consistency failure are
different facts. A sealed signature-bearing object is not `witnessed` until the
required external witness observation and consistency verification are retained.
Any consistency failure enters quarantine; no timestamp chooses a branch.

Backup write, verification, and clean-room recoverability are independent axes.
`backup.write_observed(pass)` changes neither verification nor recoverability.
Missing or corrupt C2 bytes remain missing/corrupt even when C0/C1 reduce cleanly.

`restore.report_recorded` has `authority_effect=no_service_reopen` and advances
only the restore-case axis. A separate `recovery.decision_recorded` binds the
exact report and current-security frontier. A further
`recovery.service_scope_changed` command is the only fact that changes recovery
control. Moving beyond quarantine requires `security_frontier=proven_complete`;
publication, spending, R2+ effects, and physical actions remain disabled under
the founding recovery command contract.

`ledger.fork_detected` forces quarantine. `ledger.epoch_started` requires a
constitutional recovery decision, every known prior head, an unresolved-receipt
set, identity non-reuse evidence, and `wall_clock_branch_selection=false`.

### Strategy candidate

```text
evaluation:
  proposed | shadow_authorized | shadow_recorded | canary_authorized |
  promoted | rejected | rolled_back
```

Learning state never mutates a production component. Promotion is a separate human-governed fact over an exact candidate digest.

## Typed blockers

Do not turn `blocked` into a scientific state:

```text
Blocker {
  blocker_id
  mission_id
  scope_type: mission | protocol | stage | work_item | run |
              verification | claim | publication | external_effect |
              data_asset | data_exposure | deletion_case | restore_case |
              recovery_control | ledger_epoch
  scope_id
  class: contract | protocol | rights | policy | budget |
         infrastructure | evidence | security | verification | publication
  reason_code
  opened_by_event
  evidence_refs
  resolution_requirement
  status: open | resolved | superseded
  resolved_by_event | null
}
```

UI labels such as `rights-blocked` or `infrastructure-null` are derived from axes plus blocker class. They are never stored as a scientific verdict.

## Mission phase transitions

| From | Command and entry predicate | To | Required retained output |
|---|---|---|---|
| no mission aggregate | accepted proposal plus authorized `mission.create_origin` | intake | proposal decision causal reference and mission origin record |
| intake | origin rights/safety screen and orientation entry predicate pass | orient | orientation-start checkpoint |
| orient | source roles, prior map, rights and unknowns complete | contract | orientation package |
| contract | mission spec passes schema and semantic validation | preregister | validated mission spec |
| preregister | protocol frozen before prohibited exposure | preflight | immutable protocol snapshot |
| preflight | fixtures, artifacts, resources, grants and recovery pass | execute | run manifest and authorization |
| execute | declared work graph settled and candidate artifacts recorded | verify | attempt/resource/artifact package |
| verify | required verifier packages settle | adversarial_review | verification package set |
| adversarial_review | findings recorded; critical unresolved findings block | adjudicate | review and discrepancy set |
| adjudicate | pure consequence rule derives result or refusal | handoff | adjudication and claim candidates |
| handoff | exact recovery/closure packet sealed | learn | handoff artifact |
| learn | grounded outcome harvested or explicitly unavailable | closed | learning records and closure |

`pause`, `quarantine`, and `resume` change mission control, not phase. A protocol fork creates a new branch; it does not reverse the old branch.

Proposal defer, decline, and withdrawal settle only the proposal aggregate unless an already-created mission needs an explicit, separately authorized control or closure transition.

## Stage transition algebra

```text
pending -> ready
pending -> blocked
ready -> blocked
blocked -> ready            only through a resolved blocker event
ready -> completed          only with required output and valid authority
```

Execution stages additionally require an active lease and attempt. A completed stage is immutable; correction or invalidation creates subsequent events and dependent-state changes.

Stage authorization has a separate transition algebra:

```text
not_required -> missing       when an authorization requirement is introduced
missing -> active             only with exact same-batch grant-use facts
active -> expired | revoked | exhausted
expired | revoked | exhausted -> active   only through a new grant, never resurrection
```

Readiness never implies authorization, and authorization never implies readiness.

## Non-negotiable laws

1. A scientific outcome other than `not_adjudicated` requires `validity=valid`.
2. `null_result` requires `measurement=valid_measurement` and a frozen null/equivalence rule.
3. `no_valid_measurement` can never derive `null_result`.
4. `invalid`, open blocker, or `completion_unknown` cannot derive an eligible scientific claim for the affected scope.
5. Attempt completion does not imply artifact promotion, stage completion, verification, or external settlement.
6. Artifact signature does not imply scientific validity.
7. Verification confirmation requires every mission-required independence predicate; `unknown` fails closed.
8. Same-evidence replay cannot derive independent replication.
9. Claim eligibility never implies release authorization.
10. Release request, intent, timeout, or missing receipt never implies `released`.
11. Correction adds a claim version and invalidates dependent projections; prior bytes remain.
12. Unknown, unmeasured, unavailable, withheld, and not-applicable are distinct from zero and from each other.
13. Mission close cannot leave an active lease, unresolved ambiguous external effect, or unsealed handoff.
14. Publication may occur after adjudication but never mutates the scientific phase history.
15. A proposal-stream fact with `mission_scope=null` cannot create or mutate a mission aggregate.
16. Each event type has one aggregate owner and one reducer; wrong-owner delivery fails closed.
17. `authority.grant_used(consumption_point=domain_commit)` and the consequential ordinary domain fact commit in one batch or neither exists.
18. `authority.grant_use_reserved` and `external_effect.authorized` commit in one T1 batch; `authority.grant_used(consumption_point=dispatch_claim)` and `external_effect.started` commit in a later claim batch. No released/expired/cancelled reservation can be consumed, and no consumed reservation can be released.
19. Grant activation and expiry are controlled-time facts; replay never consults the reader's wall clock for historical state.
20. `publication.release_settled(to=released)` requires an exact channel observation, not only a provider receipt.
21. An unknown event type or semantic major version stops canonical replay rather than being ignored.
22. A `RightsAssertion` is evidence only; it cannot derive `data_use.authorized` without a separate exact `DataUseDecision`.
23. Exposure intent does not dispatch. `completion_unknown` cannot derive zero, `confirmed_not_exposed`, or restored independence.
24. `deletion.completed` requires verified covered-plane settlement and zero residual copies; it cannot coexist with an admitted restored projection of the same asset identity.
25. A legal hold pauses covered destruction only and can never derive access, processing, training, verification, or publication authority.
26. Backup write, verification, and recoverability are independent axes; no axis is inferred from another.
27. A restore report changes no service scope. Only a separate recovery decision plus service-scope command can reopen a bounded scope.
28. An incomplete or indeterminate current-security frontier forces isolation or quarantine and prevents historical grants, credentials, and projections from becoming current.
29. Missing or corrupt claim-bearing artifact bytes remain unavailable even when ledger metadata, old digests, or old verification records restore successfully.
30. Fork detection forces quarantine. Wall clock, last-write-wins, or automatic branch union can never choose a canonical history.
31. A new ledger epoch requires a constitutional recovery decision and identity non-reuse; it does not rewrite or merge prior epochs.
32. A resource reservation is one child of `resource_budget`; creation and claim each bind the complete exact cohort and preserve one componentwise ceiling.
33. Claim does not invent actual use. Crash, recovery, timeout, and missing observation cannot release or reduce a claimed hold.
34. Release and expiry are legal only from `active`; settlement is legal only from `claimed` with exact observed usage/billing/refund evidence.
35. Execution, per-currency money, and verification-capacity dimensions are non-fungible; cross-resource conversion and dimension compensation are forbidden.
36. Resource settlement preserves both componentwise equations above, retains overage explicitly, and never coerces missing or unavailable use to zero.

## Derived terminal descriptions

Examples:

- **Valid null:** run valid + valid measurement + `null_result` + required verification confirmed.
- **Infrastructure-null presentation:** no valid measurement + open/resolved infrastructure blocker; scientific outcome remains `not_adjudicated`.
- **Rights-blocked presentation:** required evidence unavailable for rights reason; no scientific outcome.
- **Corrected result:** old claim version superseded + new adjudication/claim version + dependent publications corrected or withdrawn.
- **Transferred result:** independently verified scoped result + separate transport execution + `transported` under its frozen criterion.

## Model-checking target

Before Increment 1, model bounded races for:

- two workers claiming one writer lease;
- grant revocation versus use;
- dual-control grant consumption;
- attempt completion versus worker death;
- protocol freeze versus data exposure;
- storage materialization versus canonical artifact-promotion commit;
- verifier assignment versus sealed-truth exposure;
- release authorization versus correction;
- publication timeout versus reconciliation;
- mission close versus active/ambiguous effects;
- rights assertion versus data-use admission;
- exposure observation timeout versus settlement;
- deletion completion versus backup restore;
- legal-hold release versus deletion closure;
- reservation claim versus cancellation or expiry;
- claimed reservation versus worker crash and recovery;
- missing usage observation versus settlement;
- cross-resource conversion versus componentwise budget admission;
- verification start versus five-dimensional capacity claim;
- checkpoint seal versus witness consistency failure;
- restored stale grant versus current-security frontier;
- restore report versus recovery service-scope change; and
- fork detection versus constitutional epoch start.

The model's counterexamples become transition fixtures. A model-check pass is not a proof of implementation correctness; it checks the frozen algebra.
