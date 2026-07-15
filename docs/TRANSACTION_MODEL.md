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

1. decode the command under its pinned schema and canonicalization profile;
2. bind `command_id` to the canonical command-payload digest;
3. load the owning aggregate at `expected_ledger_position` from canonical facts or a verified snapshot plus its event suffix;
4. validate schema, semantic invariants, current state, referenced immutable identities, policy, authority, replay rules, budget, and one-writer lease;
5. derive the complete event batch with no network, model, filesystem, scheduler, object-store, or provider call inside the transaction;
6. append the immutable event bytes and advance the aggregate head using compare-and-set;
7. record authority consumption, resource reservation, command result, and any invariant-bearing canonical relational records implied by that event batch;
8. insert outbox records for required downstream delivery;
9. commit once; and
10. return the retained command result and committed ledger position.

The commit is the linearization point. Before it, no domain transition happened. After it, the transition happened even if the process dies before replying.

The event batch, command receipt, aggregate-head advance, authority consumption, resource reservation, and causally required outbox records are one database transaction. A failure rolls them all back. Network calls and long computation never occur while this transaction is open.

### Command idempotency

`command_id` is globally unique within the command namespace and binds to actor, mission or owning aggregate, command type and version, and canonical payload digest.

- Repeating the same ID with the same identity and digest returns the original accepted, rejected, or duplicate result.
- Reusing the ID with a different identity, aggregate, type, version, or payload digest is a conflict and possible security incident; it never executes as a new command.
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

**T1 — authorize and intend.** A PostgreSQL command transaction validates the latest state, consumes or reserves the necessary grant and budget, creates the effect intent, and inserts a dispatch outbox record. No external call occurs. This commit means “authorized to attempt,” never “applied.”

**Dispatch — perform outside the database.** A dispatcher atomically claims an unstarted intent only while its dispatch preconditions remain valid, records the dispatch attempt, and calls the provider with the stable effect identity/idempotency key. The database transaction is closed before the network or physical call begins. Revocation prevents an unclaimed intent from dispatching; it cannot retroactively unsend an in-flight call, which remains subject to cancellation and reconciliation.

**T2 — record observation.** The adapter retains the provider response, error, charge observation, and receipt as evidence and submits a command. A positive synchronous receipt advances only as far as the provider-specific evidence rule permits. A timeout or lost response becomes `completion_unknown`; it never becomes `confirmed_not_applied`.

**T3 — reconcile settlement.** An independent read, provider query, callback, ledger check, or operator-reviewed observation determines `confirmed_applied` or `confirmed_not_applied`. Reconciliation evidence and identity are retained. If the provider cannot expose adequate idempotency or settlement evidence, the action cannot be automatically retried and may be ineligible for autonomous execution.

Reconciliation is a process axis, not a polarity-free scientific outcome. The final settlement must retain whether the effect was applied or not applied. Publication becomes `released` only from evidence that the exact sealed manifest is externally visible at the intended channel; a request, dispatch, 2xx response without the accepted evidence, or timeout is insufficient.

### Retry and duplicate-cost rules

- A pre-dispatch failure may be retried under the same intent while authority, expiry, lease, and budget remain valid.
- After a call may have crossed the provider boundary, automatic retry stops unless the accepted provider contract proves the same idempotency key converges on one effect and the reconciliation rule says replay is safe.
- A provider that deduplicates writes may still duplicate charges; charge settlement is observed separately.
- Every dispatch attempt and observed cost remains retained, including failed and duplicate attempts.
- An operator override creates a new authorized decision; it never edits the prior ambiguous attempt.

## Lease, revocation, and commit-point semantics

Leases grant temporary proposal/execution opportunity; they do not grant direct write authority. A stage completion command must prove the active lease, expected stage position, attempt identity, artifacts, and required grant state in its commit transaction.

Grant revocation and dispatch claiming race at a defined database commit point:

- revocation before an intent is claimed prevents dispatch;
- a claim committed first establishes an in-flight attempt that revocation cannot erase;
- revocation still blocks subsequent attempts and triggers best-effort cancellation where supported;
- the actual external outcome remains unknown until observed or reconciled.

High-consequence domains must choose controls that bound the in-flight window, such as short dispatch leases, local interlocks, two-person authorization, provider-native cancellation, or no autonomous dispatch. The transaction model alone is not a physical safety case.

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
| effect authorized, before dispatch | committed intent and outbox; no effect evidence | dispatch if still claimable or revoke/cancel intent | authorization means applied |
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
