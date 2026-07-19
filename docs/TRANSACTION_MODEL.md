# Transaction and Recovery Model

Status: proposed architecture, 2026-07-15. This document defines the transaction semantics Odeya must preserve; it does not authorize implementation or select a final vendor configuration.

## Purpose

Odeya spans a relational ledger, immutable object storage, a durable scheduler, isolated workers, external providers, and rebuildable projections. Those systems cannot honestly be presented as one atomic database. The design therefore needs one explicit linearization point for scientific state and recoverable protocols everywhere else.

The governing rule is:

> A committed Odeya domain-event batch is the only way scientific or authority state changes. Bytes, workflow history, provider responses, messages, and UI state are evidence or mechanisms until a validated command records their meaning in that batch.

No cross-system “exactly once” guarantee is claimed. Odeya provides atomicity inside its canonical relational transaction, immutable identities for retained bytes, at-least-once delivery, idempotent command handling, and explicit reconciliation for effects outside that transaction.

## Ownership and sources of truth

| Plane | Owns | Does not own |
|---|---|---|
| Odeya domain ledger in PostgreSQL | ordered domain facts, aggregate heads, command decisions, authority use, artifact registrations, effect intent and settlement, claim and publication state | artifact bytes, scheduler mechanics, UI state |
| Content-addressed object store | immutable bytes at verified digest keys and their storage-level retention state | whether an artifact is scientifically admissible, promoted, valid, or publishable |
| Git | reviewed source history and authoring provenance | live mission state or the accepted protocol by itself |
| Durable scheduler, initially a Temporal-class candidate | timers, activity dispatch, operational replay, heartbeats, and workflow recovery | scientific lifecycle, authority, artifact promotion, verdicts, claims, or release completion |
| External provider or physical system | its own actual external outcome | Odeya's interpretation, claim state, or authority record |
| Projections, search, vector indexes, and cockpit | rebuildable views at a disclosed ledger position | canonical facts or transition authority |

PostgreSQL is the canonical coordination and semantic ledger, not the container for every byte. A promoted artifact is usable only when both conditions hold:

1. the immutable bytes exist at the registered digest in the object store; and
2. a committed Odeya event registers those exact bytes, media type, provenance, custody, rights, and policy state.

Object presence without ledger registration is an inert orphan. Ledger registration with missing or mismatched bytes is a corrupt or unavailable artifact and fails closed. Neither half alone can support a claim.

A Git commit may identify reviewed source or protocol authoring history. The accepted protocol is the canonicalized snapshot whose digest is sealed by the Odeya ledger and whose bytes are retained as an artifact; a branch name or mutable Git reference is never sufficient.

## Canonical transaction boundary

### Command linearization

Every accepted state-changing command executes through the Odeya kernel application service. Multiple service instances may exist, but PostgreSQL provides one logical writer for each owning aggregate through optimistic compare-and-set and uniqueness constraints.

One command transaction performs, in order:

1. decode the envelope under its exact pinned schema and resolve the immutable command-registry snapshot, separate activation proof, member record, payload schema bytes, and canonicalization profile—never `latest`;
2. verify membership, activation branch/scope/position, duplicated record/envelope metadata, and payload schema; recompute the domain-separated request digest and bind `command_id` to the entire canonical request identity;
3. load the owning aggregate at `expected_ledger_position` from canonical facts or a verified snapshot plus its event suffix;
4. evaluate the exact local policy bundle/rules over the controlled-time and locked reference frontier, producing an immutable `allow | deny | indeterminate` PolicyDecision; callers never supply this record;
5. validate semantic invariants, current state, referenced immutable identities, authority, replay rules, rights, risk, budget, and one-writer lease, retaining the CommandContractRecord-selected evidence records;
6. derive the complete event batch and closed AdmissionEvidenceBundle with no network, model, filesystem, scheduler, object-store, or provider call inside the transaction;
7. append the immutable event bytes and advance the aggregate head using compare-and-set;
8. record the admission evidence, authority consumption, resource reservation, command result, and any invariant-bearing canonical relational records implied by that event batch;
9. insert outbox records for required downstream delivery;
10. commit once; and
11. return the retained command result and committed ledger position.

The commit is the linearization point. Before it, no domain transition happened. After it, the transition happened even if the process dies before replying.

The PolicyDecision, AdmissionEvidenceBundle and referenced decision/result records, event batch, command receipt, aggregate-head advance, authority consumption, resource reservation, and causally required outbox records are one database transaction. A failure rolls them all back. Network calls and long computation never occur while this transaction is open.

For a multi-aggregate batch, commit visibility is indivisible. The stream
allocator, every affected aggregate head, the receipt, checkpoint eligibility,
and current-serving frontier advance only to the complete batch boundary. No
reducer snapshot, checkpoint, receipt response, or projection advertised as
current may end between two events in the batch. Replay that finds a missing,
reordered, wrong-producer, or split mandatory cohort quarantines the affected
scope; reducers never synthesize the missing companion.

Two first-slice scientific consequences use this law directly:

- `claim.supersede` compare-and-sets ClaimVersion and
  DependencyInvalidationFrontier together, emitting supersession before the
  monotone transitive invalid-source fence. Exact dependencies live in
  immutable ClaimVersion references; reverse fanout is a rebuildable index.
- `run.determine_validity` originates RunValidity and MeasurementDisposition
  together. The only invalid branch is `invalid + no_valid_measurement`; a
  partial pair, or `invalid + valid_measurement`, is unrepresentable.

Any downstream eligibility or current-serving decision evaluates those exact
complete frontiers, never an asynchronously caught-up fanout or one half of a
scientific pair.

### Command idempotency

`command_id` is globally unique within the idempotency scope and binds to actor, mission or owning aggregate, command type/version/schema, exact registry snapshot/activation/member record, target positions, authority evidence, causal inputs, complete payload, and canonical request digest.

- Repeating the same ID with the same identity and digest returns the original accepted, rejected, or duplicate result.
- Reusing the ID with a different identity, aggregate, type, version, or request digest is a pre-receipt conflict and possible security incident; it never executes or creates a second CommandReceipt.
- A business retry after a genuine failed attempt receives a new `attempt_id`. It may reuse a provider idempotency key only when the external-effect contract explicitly permits it.
- Rejection is retained as a canonical event only when the rejection is itself evidence-relevant, as defined by the command catalog.

Command idempotency, worker-attempt identity, outbox delivery deduplication, provider idempotency, and charge deduplication are separate controls. Success in one does not imply success in another.

### Aggregate scope and cross-aggregate rules

A command names one owning aggregate. References to other aggregates target immutable versions or exact ledger positions. Most cross-aggregate work is a sequence of commands coordinated by retained events, not a hidden distributed transaction.

When an invariant genuinely requires simultaneous mutation of multiple Odeya-owned rows in the same PostgreSQL database—for example, consuming a single-use grant while authorizing its exact effect—the command declares that transaction cohort. It locks aggregate heads in canonical identifier order, applies compare-and-set to every member, and emits the causal events together. Such cohorts must be rare, enumerated, and model-checked.

No transaction cohort extends to object storage, Git, the scheduler, a model provider, a release channel, a laboratory, or a physical system. Compensation appends a correction, revocation, quarantine, withdrawal, or supersession fact; it never erases a committed event.

## What is canonical inside PostgreSQL

The immutable domain-event bytes are the replay source for scientific meaning. The following records participate in transaction safety without becoming a second scientific truth:

- aggregate heads and mission sequence allocation;
- unique command-to-result receipts;
- authority-grant use and replay counters;
- active lease and resource-reservation constraints;
- artifact identity/registration rows derived atomically from promotion events;
- external-effect identity and current settlement projection at an exact event position;
- transactional outbox and callback inbox deduplication records; and
- optional verified snapshots used only as event-fold accelerators.

An invariant-bearing relational row must name the event and ledger position that created or last advanced it. It must be reconstructible or consistency-checkable from retained event bytes. If it disagrees with the event fold, commands for the affected scope fail closed and open an integrity incident.

Read models, search indexes, context packs, graph layouts, rankings, summaries, and UI materializations are asynchronous projections. They may be deleted and rebuilt. A command may not authorize or adjudicate from a projection unless the contract requires an exact position and independently verifies that the projection represents that position.

## Transactional outbox and inbox

Every downstream action caused by a committed event receives an outbox record in the same transaction as that event. The record contains a stable message ID, causal event reference, destination class, schema/version, payload digest or immutable reference, availability time, and delivery policy.

Outbox delivery is at least once:

1. a dispatcher leases an available row;
2. it delivers the immutable envelope or invokes the appropriate adapter;
3. it records each delivery attempt and returned receipt; and
4. the receiver deduplicates by message ID and semantic idempotency key.

An outbox row marked delivered means only that the configured receiver acknowledged delivery. It does not mean a workflow completed, an external write occurred, a publication is visible, a charge settled, or a scientific result is valid.

Inbound workflow callbacks, provider webhooks, and reconciliation observations enter through a callback inbox keyed by adapter identity plus provider message or observation identity. The inbox prevents duplicate transport processing, then submits a normal validated command. A callback never writes domain tables directly.

Outbox and inbox payloads carry references to canonical objects wherever possible. Transport wrappers such as CloudEvents may be used, but their delivery metadata is not part of the scientific identity unless explicitly incorporated into a later observation event.

## Artifact staging and promotion

Object storage and PostgreSQL do not share an atomic transaction. Odeya uses a recoverable, one-way protocol.

### Storage protocol

1. **Stage.** A worker exports declared bytes to a mission-scoped, noncanonical staging key under a short retention policy. The worker cannot select the final digest key or claim promotion.
2. **Stream-validate.** A trusted promotion boundary reads the complete stream, enforces size and media constraints, computes the pinned digest over exact bytes, validates any declared structure, and writes a retained validation report.
3. **Materialize immutably.** The boundary creates the content-addressed object using conditional create at the digest key. If it already exists, exact byte identity and storage metadata are verified. Mutable overwrite is forbidden.
4. **Register canonically.** A `PromoteArtifact` command references the stage, validation report, expected digest, provenance, rights, sensitivity, and authority. Its PostgreSQL transaction appends the promotion event, registers metadata, advances state, and emits outbox work atomically.
5. **Reconcile.** A background process finds unregistered objects, registered-but-missing objects, digest mismatches, stale stages, and retention conflicts. It reports observations through commands and cannot silently repair canonical meaning.

“Materialized” is the storage-level state after step 3. Scientific custody becomes `promoted` only after step 4 commits. This vocabulary prevents an object-store success from masquerading as a domain transition.

### Identity and deduplication

The physical digest object may be deduplicated, but logical artifact records remain distinct when provenance, rights, sensitivity, retention, normalization, or role differs. Original and normalized bytes always have different identities when their bytes differ and are connected by an explicit transformation activity.

The promotion command is idempotent. A crash after immutable materialization but before the database commit leaves an inert orphan; retrying registration is safe after verifying the object. Orphan collection waits through the accepted grace period, checks every canonical reference and in-flight registration intent, and records deletion evidence. A storage object is never deleted merely because one process lacks a reference in its local view.

If canonical registration commits and bytes are subsequently missing or corrupt, the reconciler marks the artifact unavailable/corrupt through a command, quarantines dependent use, and triggers claim/publication dependency review. It does not synthesize replacement bytes under the old digest.

## Data-governance transaction boundaries

Data possession and rights evidence do not share a transaction with authority by implication. `rights_assertion.record` commits only `rights_assertion.recorded`; that fact is permanently evidence-only. `data_use.decide` or `data_use.revoke` is a separate command against the exact asset and decision aggregate, current policy/frontier, assignment, purpose, recipient, provider/model, operation, and time. Any dependent access or effect still performs its own current-state admission.

`data_exposure.record_intent` records a governed projection and stable external-effect identity but cannot dispatch. The command payload fixes `recording_intent_does_not_dispatch=true`. Actual disclosure follows the external-effect T1/dispatch/T2/T3 protocol. `data_exposure.observation_recorded` is an external observation; `data_exposure.settlement_recorded` is the admitted conclusion over one or more observations. A timeout, retry exhaustion, provider silence, or deletion never writes `confirmed_not_exposed`.

Deletion spans canonical metadata, storage planes, providers, indexes, backups, and publications, so it is not one cross-system transaction. `deletion.open_case` and `deletion.record_progress` retain scope, holds, external observations, residuals, and scientific consequences. `deletion.close_case(completed)` is admitted only after the accepted verification rule reports every covered plane verified, no residual copy, required tombstone facts, and claim/publication consequence facts. The same canonical command cohort may append data-asset tombstone and dependency-invalidation facts when their simultaneous mutation is required. Storage/provider calls remain outside the transaction and are observed through stable effect identities.

A legal hold command changes only the hold/destruction-pause aggregate. It never changes the data-use aggregate, creates a grant, or authorizes access. Release removes only the pause; any later processing still requires current data-use and action authority.

## Durable workflow substrate

A Temporal-class system is a replaceable scheduler beneath Odeya-owned semantics.

It may own:

- durable timers and backoff;
- operational workflow/activity history;
- dispatch of ready work;
- activity heartbeat and cancellation mechanics;
- recovery of scheduler-local progress; and
- deterministic replay of workflow code, with nondeterministic work isolated in activities.

It may not own or infer:

- mission phase, protocol validity, or claim eligibility;
- grant issuance, use, revocation, or budget truth;
- one-writer stage completion;
- artifact custody or scientific validity;
- verifier independence or adjudication;
- external settlement; or
- publication authorization or released status.

Scheduling starts from an outbox message with a stable workflow identity derived from the immutable run/work-graph version, not from an ad hoc callback. A duplicate start converges on the same scheduler identity. Before an activity performs work it acquires an Odeya lease and applicable capability grants through kernel commands. Activity completion returns an attempt manifest and staged artifact references as a command proposal. Only the resulting database commit advances Odeya state.

Workflow callbacks are untrusted transport inputs. They are schema-validated, deduplicated, and submitted as commands. Deleting or rebuilding scheduler history must not change a scientific verdict. If scheduler state and canonical state disagree, the kernel state wins; execution pauses while a reconciler determines whether to restart, cancel, or record an operational discrepancy.

The scheduler's internal retry policy may retry only activity classes that the Odeya work contract marks retryable. It cannot retry policy denial, protocol invalidity, suspected compromise, publication, irreversible physical action, or an ambiguous external write.

### Bounded local verification profile

The first proof slice does not import the general scheduler as scientific
authority. `verification.assign` accepts the exact admitted `WorkIntent`—not a
pre-existing `WorkContract`, active `WorkLease`, or resource reservation—as
its prospective work input. It rechecks the promoted input manifests, current
`DataUseDecision` set, `LocalMaterializationIntent`, zero-external-capability
sandbox policy and capability, candidate worker eligibility,
activation/frontier, budget, and five distinct assignment grants. Its one
atomic thirteen-event commit records, in order, the five
`authority.grant_used` events for safety/data-rights/resource/execution/
verification, `resource.reservation_created`, `work.lease_acquired`,
`verification.assigned`, and the matching five
`authority.grant_exhausted` events. That commit binds the selected worker and
establishes the active lease and reservation; it does not mount bytes, create
a launch outbox, or launch work.

Only after that exact assignment commit may deterministic derivation
materialize a `WorkContract` bound to the same `WorkIntent` and assignment
commit. The derived contract remains a non-authoritative control artifact.
`attempt.start` is the separate and sole local dispatch-claim command. It
rechecks the derived `WorkContract` and every current assignment fact,
consumes the five separate ordered start grants, claims the reservation,
records `attempt.started + verification.started`, and writes the stable
local-launch outbox in one commit. Only after that commit may the launcher
mount read-only inputs or spawn the sandbox.

The exact architecture-only order and its retained legacy-order known-bad are
machine-checked by the
[`PRQ-009 assignment-order contract`](../architecture/prq-009-assignment-order-contract.json).
PRQ-009 remains unresolved until the required exact identities and immutable
members exist; this text does not authorize assignment, dispatch, or runtime.

`attempt.report` records one terminal or completion-unknown execution fact plus
actual input/code/environment, visibility, negative-flow, teardown, and raw
resource-observation references. It neither settles ResourceLedger nor decides
scientific validity. `verification.complete` separately consumes the immutable
attempt/package evidence. Network, provider/model, ambient credential, external
write, cloud, GPU, and spend capability is exactly zero in this profile.

Assignment/start/invalidation/deadline lock verification, work-item, resource,
and grant heads in the global order. Invalidation/deadline first may revoke or
expire the lease and release/expire the active reservation. Start first makes
the hold claimed forever until exact observation and settlement; crash,
timeout, callback loss, revocation, invalidation, restore, or unknown visibility
cannot release it or justify a blind retry.

## Resource reservation and settlement protocol

A resource reservation is a child state machine owned by one `resource_budget` aggregate. Its vectors use a registered unit profile and are closed over non-fungible execution units, per-currency minor units, and five verification-capacity dimensions. Every transition is a canonical event cohort; a scheduler, worker, provider, or meter cannot mutate a hold directly.

**R0 — reserve.** The admitting transaction rechecks the exact budget head and componentwise availability, then records `resource.reservation_created` with one immutable `reservation_id`, subject binding, estimate, ceiling, expiry, and required future start cohort. The ceiling becomes an active hold in the same commit as the command result and any authorization/assignment/intention facts that depend on it. Estimate is not usage, reservation is not dispatch, and no dimension may fund another.

**R1 — claim at start.** The exact work, external-effect, or verification start transaction revalidates the reservation and atomically records `resource.reservation_claimed` with the complete named start cohort. The entire ceiling moves from active hold to claimed hold before work or exposure begins. Claim is a commitment boundary only: attempted, actual, billed, and refunded use remain unobserved. If cancellation, invalidation, revocation, or controlled-time expiry wins before R1, its cohort may record `resource.reservation_released` or `resource.reservation_expired` and return the exact ceiling. Nothing can claim that terminal reservation.

**R2 — observe.** Meters, providers, instruments, and reviewed operator evidence submit immutable observations that the kernel records as `resource.usage_observed`. Attempted, actual, billed, and refunded axes remain distinct, each with explicit observed/missing/unavailable state. A missing callback, unavailable meter, or provider silence is not zero.

**R3 — settle.** Only a claimed reservation with the required exact observations can record `resource.reservation_settled`. For each dimension, settlement proves `net = reserved_consumed + overage` and `ceiling = reserved_consumed + unused`; only `unused` returns to availability, `reserved_consumed` remains consumed, overage remains an explicit breach/liability, and the hold becomes zero. Money additionally proves `net = billed - refunded`; non-money uses actual use. Unknown usage cannot settle.

A crash or recovery after R1 never rewinds to R0 and never releases capacity. The full ceiling stays held until exact evidence supports R3. This conservative rule prevents a restarted worker or dispatcher from double-claiming budget while the first attempt may still have consumed resources. Verification uses the same lifecycle: assignment/reservation, `verification.started`/claim, observed IV0–IV4 capacity use, and settlement are exact cohorts rather than a separate trust-budget mechanism.

For the bounded local profile, one VerificationRun owns one combined vector
covering its operational and IV0-IV4 coordinates. A clean replay is a distinct
VerificationRun and reservation. `resource.record_observation` emits exactly one
typed `resource.usage_observed`; when that observation completes the frozen
profile, the same command batch may also emit settlement. Non-money dimensions
require exact actual usage. Money dimensions require exact billed and refunded
observations. Attempted use is diagnostic. An explicitly empty no-money domain
is not a fabricated zero vector.

## External-effect protocol

An external effect is any action whose truth cannot be committed atomically with the Odeya ledger: paid provider invocation, repository write, message, publication, transfer, laboratory action, or physical actuation. Model inference and read-only acquisition may still create charge, privacy, or rate effects and therefore use the same pattern when declared consequential.

### Effect identity

Every intended effect has an immutable `effect_id` bound to:

- exact operation and typed payload digest;
- target provider, account/resource, and adapter version;
- mission, work item, attempt, and causal command;
- authority grant, policy decision, risk class, and disclosure scope;
- reserved resource/spend ceiling;
- provider idempotency semantics and key, if supported;
- reconciliation capability and settlement evidence rule;
- retry class, expiry, and operator escalation rule.

### Three-boundary protocol

**T1 — authorize, reserve, and intend.** The `external_effect.authorize` command transaction validates the latest state, consumes any authority whose declared action ends at intent creation, records one or more exact `authority.grant_use_reserved` facts, reserves the resource/spend ceiling, records `external_effect.authorized`, and inserts a dispatch outbox record. The use reservation binds the grant, effect/request digest, destination, use count, expiry, and resource reservation. No external call occurs. This commit means “authorized and capacity reserved for a later dispatch claim,” never “grant consumed for dispatch” and never “applied.”

For `effect_class=governed_processing_dispatch`, T1 additionally resolves—not merely shape-checks—the exact WorkContract, current authorized DataUseDecision set, non-dispatching DataExposure intent, provider-configuration observation, source/checkpoint frontier, purpose/recipient/provider/model/region/payload binding, and current policy/authority/resource input digests. WorkContract is a deterministic control artifact, never authority. Missing, denied, indeterminate, expired, revoked, stale, scope-incompatible, future-checkpoint, or unverified input rejects the command with no reservation, use, effect, outbox, or spend cohort.

**Dispatch claim, then perform outside the database.** The `external_effect.start` dispatcher transaction claims an unstarted intent only while its exact reservation, assignment, grant, policy, expiry, budget, risk, and destination preconditions remain valid. It atomically records matching `authority.grant_used(consumption_point=dispatch_claim)` facts, marks the named reservations consumed, records `external_effect.started`, and commits before the network or physical call begins. A revocation, expiry, or other invalidation cohort that wins first records `authority.grant_use_reservation_released`, releases unused resource capacity, and prevents the claim; the effect may remain a retained but nondispatchable `authorized` intent until explicitly closed. An `external_effect.cancel` cohort additionally records `external_effect.cancelled_before_dispatch` in the same batch. A dispatch claim that wins first establishes an in-flight historical use; later revocation cannot retroactively unsend it, and the attempt remains subject to provider-native cancellation and reconciliation. A crash after claim but before a known call outcome is conservatively ambiguous.

The governed-processing dispatch claim repeats the complete current governance/frontier/provider/resource check inside its own transaction and proves the authorize/start effect class and all immutable bindings equal. Historical authorization does not freeze a mutable right, policy, provider configuration, resource ceiling, or source frontier. Only after the claim cohort commits may an adapter expose bytes or incur provider spend.

**T2 — record observation.** The adapter retains the provider response, error, charge observation, and receipt as evidence and submits a command. A positive synchronous receipt advances only as far as the provider-specific evidence rule permits. A timeout or lost response becomes `completion_unknown`; it never becomes `confirmed_not_applied`.

**T3 — reconcile settlement.** An independent read, provider query, callback, ledger check, or operator-reviewed observation determines `confirmed_applied` or `confirmed_not_applied`. Reconciliation evidence and identity are retained. If the provider cannot expose adequate idempotency or settlement evidence, the action cannot be automatically retried and may be ineligible for autonomous execution.

Reconciliation is a process axis, not a polarity-free scientific outcome. The final settlement must retain whether the effect was applied or not applied. Publication becomes `released` only from evidence that the exact sealed manifest is externally visible at the intended channel; a request, dispatch, 2xx response without the accepted evidence, or timeout is insufficient.

### Retry and duplicate-cost rules

- A pre-dispatch failure may be retried under the same intent while authority, expiry, lease, and budget remain valid.
- A failure before dispatch claim may reuse the still-active exact reservation; it cannot create a second reservation or change payload/destination. A reservation released, expired, cancelled, or covered by revocation cannot be revived.
- After a call may have crossed the provider boundary, automatic retry stops unless the accepted provider contract proves the same idempotency key converges on one effect and the reconciliation rule says replay is safe.
- A provider that deduplicates writes may still duplicate charges; charge settlement is observed separately.
- Every dispatch attempt and observed cost remains retained, including failed and duplicate attempts.
- An operator override creates a new authorized decision; it never edits the prior ambiguous attempt.

## Lease, revocation, and commit-point semantics

Leases grant temporary proposal/execution opportunity; they do not grant direct write authority. A stage completion command must prove the active lease, expected stage position, attempt identity, artifacts, and required grant state in its commit transaction.

Grant revocation and dispatch claiming race at a defined database commit point:

- revocation before the dispatch-bound use reservation is claimed releases/invalidates that reservation and prevents dispatch;
- a dispatch claim and `authority.grant_used(consumption_point=dispatch_claim)` fact commit together; a claim committed first establishes an in-flight attempt that revocation cannot erase;
- revocation still blocks subsequent attempts and triggers best-effort cancellation where supported;
- the actual external outcome remains unknown until observed or reconciled.

High-consequence domains must choose controls that bound the in-flight window, such as short dispatch leases, local interlocks, two-person authorization, provider-native cancellation, or no autonomous dispatch. The transaction model alone is not a physical safety case.

## Recovery-control transaction boundaries

Recovery facts use a dedicated global `recovery` stream and never borrow a mission ID. Checkpoint proposal, checkpoint seal, witness observation, and consistency failure are separate commands/facts. Backup write, verification, and recoverability are separate external observations; a successful earlier axis cannot be copied into a later one.

Restore preparation occurs in an isolated environment without production-effect credentials. `restore.record_report` commits only the immutable report reference and `authority_effect=no_service_reopen`. `recovery.record_decision` is a separate quorum-owned command over the exact report and independently established current-security frontier. Even that decision does not itself mutate service control: `recovery.change_service_scope` performs the current-state compare-and-set and keeps publication, spending, R2+ effects, and physical actions disabled.

If the frontier is incomplete/indeterminate, claim-bearing bytes are missing/corrupt, or checkpoint views diverge, the only legal control transition is isolation/quarantine. `ledger.record_fork` records every known branch without selection. `ledger.begin_epoch` requires a constitutional recovery decision and atomically records the new epoch identity plus non-reuse boundary; no wall clock, mutable alias, or restore-report recommendation participates in branch choice.

## Crash and ambiguity matrix

| Crash or ambiguity point | Retained/observable state | Recovery and next legal action | Forbidden inference |
|---|---|---|---|
| before staging completes | no complete staged manifest; partial upload may exist | abort/multipart cleanup after retention rule; new stage identity | artifact exists or attempt succeeded |
| after stage, before validation | staged bytes only | validate or expire stage | staged means promoted |
| during validation | stage plus incomplete validation attempt | rerun validator as a new observation or fail | partial validation passed |
| during conditional digest-key create | stage; final key may or may not exist | read final object, verify complete bytes/digest, then continue or quarantine | missing client response means create failed |
| after immutable materialization, before `PromoteArtifact` commit | unregistered digest object | retry same registration command or reclaim after grace and global reference scan | object may support a claim |
| during command transaction before commit | no event batch, receipt, authority use, or outbox from that transaction | retry same command ID | partial domain transition |
| after commit, before client response | complete event batch and retained command result | duplicate command returns original result | absent response means command failed |
| after event commit, before outbox lease | pending outbox row | dispatcher resumes | downstream action already happened |
| after outbox lease, before receiver accepts | delivery attempt may be ambiguous | lease expires; receiver/message idempotency determines redelivery | delivery or non-delivery without evidence |
| scheduler start accepted, before workflow reference observation | stable scheduler identity plus pending/attempted outbox | describe/query by stable identity; submit observation command | two scheduler workflows are acceptable |
| worker dies with active lease | canonical attempt running; lease eventually stale | revoke/stale lease, append interruption, create a new attempt if policy allows | worker death is a null result |
| worker completes but callback dies | staged outputs and/or scheduler history; no Odeya completion event | resend the same completion command; verify staged artifacts | scheduler completion advanced science |
| object missing after registration | canonical artifact identity but unavailable bytes | fail closed, record corruption/unavailability, inspect dependents, restore only exact verified bytes | metadata proves bytes exist |
| projection crashes or lags | canonical ledger intact; disclosed projection position stale | replay from checkpoint/event ledger and verify digest | stale UI state is current |
| reservation created, before its start claim | active reservation and exact ceiling hold; no start or usage evidence | claim only with the complete current start cohort, or release/expire pre-claim | reservation means work started or resources were used |
| after reservation claim, before worker/provider action | claimed reservation and full ceiling hold; actual use unobserved | preserve hold, inspect stable attempt/effect identity, then observe and settle | crash permits pre-claim release or actual use is zero |
| usage meter/callback unavailable | claimed reservation; explicit unavailable/missing observation axis; full hold | obtain admissible evidence or remain blocked/claimed | absent measurement is zero or enough to settle |
| usage observation committed, before settlement commit | claimed reservation plus immutable observation refs; full hold | retry the same settlement command against exact observations | observation alone released capacity or a partial settlement committed |
| effect authorized/reserved, before dispatch claim | committed intent, exact active use/resource reservations, and outbox; no dispatch/effect evidence | claim+consume only after current revalidation, or revoke/cancel/release reservation | authorization/reservation means grant consumed, dispatch started, or effect applied |
| after dispatch claim/use commit, before provider call or observable response | in-flight attempt and consumed grant use; call crossing is uncertain after crash | no blind retry; inspect adapter/provider evidence and reconcile by stable identity | process death means call definitely did or did not cross |
| provider accepts effect, adapter dies before receipt commit | in-flight/`completion_unknown`; provider may hold effect | stop unsafe retry; reconcile by stable effect/provider identity | timeout means not applied |
| response recorded, command acknowledgement lost | observation event and command receipt may already exist | repeat same observation command ID | a second effect is required |
| grant revokes while provider call is in flight | immutable dispatch-before-revoke ordering; outcome unsettled | cancel if possible, reconcile, block further attempts | revocation undid the call |
| publication channel times out | sealed manifest and `completion_unknown` effect | independently inspect exact channel/object; record applied or not applied | release succeeded or failed from timeout alone |
| reconciliation process crashes | unresolved effect plus partial reconciliation attempt | restart with same observation identities; retain each attempt | partial lookup settled the effect |
| PostgreSQL unavailable | no new canonical transition | pause writes/effects; read only from an accepted durable snapshot if policy permits | object store, scheduler, or UI becomes truth |
| scheduler unavailable | canonical mission and pending work retained | pause dispatch; rebuild/resume scheduler from next legal actions | mission state is lost |

Every row in this matrix becomes a transition trace and, after implementation authorization, a fault-injection test. Passing prose review is not evidence that a storage product or adapter satisfies it.

## Required invariants

1. A domain transition exists if and only if its event batch committed.
2. An accepted command has exactly one immutable result; same-ID/different-payload reuse never executes.
3. A mission or owning aggregate has a monotonic, gap-free event position and one compare-and-set winner per position.
4. Event batch, aggregate head, authority use, resource reservation, command receipt, and causally required outbox rows commit or roll back together.
5. No network, model, object-store, scheduler, filesystem, or provider call occurs inside the canonical database transaction.
6. An immutable digest object without ledger registration is inert; registration without verified bytes fails closed.
7. Storage materialization and scientific artifact promotion are distinct states.
8. Staged, quarantined, corrupt, unavailable, or tombstoned artifacts cannot support a claim.
9. Workers, verifiers, schedulers, adapters, webhooks, indexers, and UIs submit commands; none directly mutate domain state.
10. Workflow history, outbox delivery, provider acceptance, and attempt completion cannot imply scientific completion or external settlement.
11. Every external effect has one stable effect identity, explicit authority, budget treatment, idempotency contract, and reconciliation rule before dispatch.
12. `completion_unknown` blocks unsafe retry and dependent sealing until resolved or explicitly left blocked.
13. External settlement retains applied/not-applied polarity and exact evidence; reconciliation never erases ambiguity history.
14. Estimated, reserved, authorized, attempted, billed, refunded, and settled resource values remain separate; missing values never become zero.
15. Retries preserve prior attempts and costs. A transport duplicate is not silently treated as a new scientific sample.
16. Projection position and freshness are visible. A stale projection cannot authorize a consequential command.
17. Compensation appends facts; committed events and prior publications are never rewritten.
18. Mission close cannot leave active leases, dispatchable intents, ambiguous external effects, unsealed handoff, or unresolved integrity failures.
19. A rights assertion changes no data-use authority; only an exact admitted data-use decision can authorize a bounded use.
20. Exposure intent changes no external world. Unknown exposure remains unknown until separately settled from retained evidence.
21. Completed deletion cannot retain residual copies or allow the same asset identity to reappear as admitted after restore.
22. A legal hold changes destruction permission only and never creates read, processing, training, verification, or disclosure authority.
23. Backup write, verification, and recoverability observations remain separate and cannot be transitively promoted.
24. A restore report changes no service scope; recovery decision and service-scope application are separate canonical commits.
25. Incomplete current-policy frontier, missing C2 bytes, or a ledger fork forces isolation/quarantine.
26. A new epoch is constitutional and identity-non-reusing; wall-clock branch selection and automatic history merge are forbidden.
27. Reservation creation and claim each bind one exact budget head, subject, ceiling, and complete cohort; neither implies actual use.
28. Release and expiry are pre-claim only. Crash, recovery, timeout, callback loss, and `completion_unknown` cannot release a claimed ceiling.
29. Settlement requires exact observations and preserves componentwise net/ceiling conservation; missing or unavailable values never become zero.
30. Execution units, currencies, and verification-capacity dimensions cannot convert, compensate, or silently net against one another.
31. A verification start claims the exact five-dimensional reservation selected at assignment; claim-bearing verification cannot begin on unreserved or mismatched capacity.

## Consistency, backup, and recovery obligations

The accepted deployment profile must define PostgreSQL durability, replication, backup, restore, and acknowledged-commit assumptions; object replication and checksum verification; checkpoint witnessing; staging and orphan retention; scheduler-history retention; and maximum tolerable projection lag. RPO/RTO values remain deployment decisions, but they must be accepted before production use.

A restore is successful only when it verifies:

- event-chain and witnessed-checkpoint continuity;
- aggregate-head and command-receipt consistency;
- authority-use and resource-reservation consistency;
- every live artifact reference against exact object bytes;
- unresolved external effects and their next legal reconciliation action;
- outbox/inbox replay without duplicate consequential effects; and
- projection rebuild to a named ledger position.

## Architecture acceptance evidence

Before this model can move from proposed to accepted, Gate A must include:

- a complete command/event catalog naming the owning aggregate and transaction cohort;
- state-machine model checks for the races listed in `STATE_MODEL.md`;
- adversarial traces for same-ID/different-payload, stale positions, grant revocation, dual control, object orphaning, and publication ambiguity;
- an accepted provider-effect classification table, including refusal where idempotency/reconciliation is inadequate;
- an accepted definition of storage materialization versus semantic promotion;
- a decision on transaction isolation, lock ordering, and checkpoint/witness policy; and
- an authorized Gate B crash-recovery probe before any selected storage/workflow product is treated as proven.

See [ADR 0007](decisions/0007-canonical-transaction-and-effects.md), [Interface contracts](INTERFACE_CONTRACTS.md), [State model](STATE_MODEL.md), [Failure model](FAILURE_MODEL.md), and [Standards profile](STANDARDS_PROFILE.md).
