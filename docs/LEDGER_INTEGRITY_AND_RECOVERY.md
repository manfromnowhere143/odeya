# Ledger Integrity, Backup, and Recovery Contract

Status: proposed constitutional contract, 2026-07-15. This document freezes recovery semantics without pretending a database, cloud, key service, or workflow product has passed them. Product-specific durability and restore claims require an authorized Gate B probe and a signed deployment profile.

## Objective

Odeya must recover availability without inventing scientific history, erasing acknowledged ambiguity, resurrecting revoked authority, or silently serving a fork. Recovery is a scientific-integrity operation, not merely infrastructure restoration.

The design optimizes in this order:

1. prevent unauthorized external effects and disclosures;
2. detect equivocation, truncation, mutation, corruption, and resurrection;
3. preserve or explicitly account for every acknowledged canonical decision;
4. restore exact evidence and the ability to recompute projections;
5. resume bounded service only after invariants pass.

Under uncertainty Odeya enters read-only quarantine. Availability never authorizes choosing the most convenient ledger branch.

## Truth planes and recoverability classes

| Class | Contents | Recovery rule |
|---|---|---|
| C0 constitutional roots | EngineContractRoot, C0 bundle, aggregate-state subject/schema/command/event/reducer/policy/method registries, root-authority manifests, trust roots | Exact retained versions and witnessed digests required before any other state is interpreted |
| C1 canonical ledger | commands/receipts, event batches, aggregate heads, grants/use, resource/effect/publication facts | Ordered, append-only semantics; restore must prove continuity and cross-record invariants |
| C2 promoted artifact bytes | exact protocol, data, code, environment, result, evidence, publication packages | Restore exact bytes at registered identities or fail all dependents closed |
| C3 external-world evidence | provider/lab/channel receipts, observations, reconciliation evidence | Preserve ambiguity and reacquire observation only under a new retained activity |
| C4 scheduler/operational state | timers, leases, activity attempts, dispatch mechanics | Reconcile against C1; never becomes domain truth |
| C5 projections | cockpit/read models, search, vectors, caches, reports | Discardable and rebuilt from a named C0/C1/C2 position |
| C6 secrets and keys | signing, encryption, workload, provider credentials | Separate hierarchy and recovery; never restored from application backups in plaintext |

Recovery of a lower-numbered class does not prove a higher-numbered class exists. C1 metadata with missing C2 bytes yields unavailable/corrupt evidence, not a recovered claim.

## Integrity model

Odeya uses multiple independent mechanisms because each covers a different failure:

### Transaction integrity

The canonical relational commit atomically binds command receipt, event batch, aggregate-head advance, authority/resource changes, and required outbox rows. Database constraints and serializable/explicit-lock semantics prevent ordinary concurrent forks under the accepted profile.

### Content identity

Every canonical record and artifact uses its pinned canonical-object or raw-byte digest. A digest detects changed bytes under its algorithm/profile; it does not prove completeness, origin, correct meaning, or absence of an alternate history.

### Stream continuity

Each owning aggregate has a gap-free sequence and prior-event or prior-batch digest. A batch binds its command receipt, ordered event digests, pre/post aggregate position, and transaction cohort. A cross-aggregate transaction receives one commit identity and deterministic member order.

### Global checkpoints

A `LedgerCheckpoint` periodically binds:

- checkpoint ID/version and controlled commit time;
- database/ledger epoch and inclusive global commit position;
- Merkle or equivalently reviewed commitment to all canonical event batches through that position;
- aggregate-head-set commitment;
- command-receipt-set commitment;
- admission-evidence-set commitment covering PolicyDecision, AdmissionEvidenceBundle, and validation/reference/authority/resource decision records;
- active root-authority manifest and trust-root digests;
- the exact EngineContractRoot and AggregateStateSubjectRegistry subjects, each with version, exact schema identity, and digest;
- the exact C0 registry bundle and its root/trust/schema, command-contract, event-contract, reducer, module-dependency, resource/unit-profile, semantic-rule, policy, canonicalization, and method-registry component digests;
- promoted-artifact registry commitment and declared artifact verification coverage;
- unresolved external-effect/incident summaries by exact set commitment;
- previous checkpoint digest; and
- signer identities, algorithms, and signature-purpose context.

The exact commitment structure must support inclusion and consistency proofs without requiring all data to be public. A custom unaudited Merkle design is forbidden; the accepted algorithm, leaf framing, domain separation, ordering, empty-tree behavior, proof format, and test vectors are versioned.

The closed structural record is [`ledger-checkpoint` 0.9.0](../schemas/ledger-checkpoint.schema.json). Its commitments include command receipts and the separate immutable admission-evidence set, so replay does not preserve only an outcome while losing why the pure admission decision chose it. `constitutional_snapshots` now requires exact EngineContractRoot and AggregateStateSubjectRegistry references in addition to the C0 component slots. The digest contract already includes the whole `/constitutional_snapshots` object, so those new bindings are covered without adding a competing child pointer. Its structured `checkpoint_digest_contract` fixes SHA-256, the `odeya-ledger-checkpoint-v1` domain, exact `odeya-jcs` profile identity, exact checkpoint schema identity/digest binding, and the complete included/excluded JSON-Pointer sets. The checkpoint digest and all signatures are outside the hashed subject; every signature separately names the exact checkpoint digest and purpose context. Digest recomputation, actual schema/profile digest equality, admission-evidence completeness, root/bundle/component compatibility, signature validity, set cardinality, inclusion/consistency proofs, and previous-checkpoint ordering remain semantic checks; JSON Schema cannot establish them. Dependency direction is checkpoint -> root/C0/component subjects; no root or registry subject may embed the activating/future checkpoint.

### Independent witnessing

At least one witness outside the primary database and ordinary application administration retains accepted checkpoint bytes/digest, position, observation time, signature verification result, and prior consistency proof. A high-consequence profile requires plural witnesses across an independently controlled failure domain.

Witnessing makes suffix truncation or split-view behavior detectable within the witness assumptions. It cannot recover missing private payload bytes by itself and does not establish scientific correctness.

## Canonical recovery command/event lifecycle

The 121-selector design vocabulary retained from exact historical `command-envelope` 0.4.0 bytes, its nonconstructible 0.5.0 structural candidate, and `research-event` 0.7.0 assign one owner/reducer to each founding recovery fact. This mapping is architecture evidence, not admission:

| Lifecycle | Commands | Canonical events | Owner |
|---|---|---|---|
| Checkpoint | propose, seal, record witness, record consistency failure | `ledger_checkpoint.proposed`, `.sealed`, `.witness_observed`, `.consistency_failed` | `ledger_checkpoint` |
| Backup | record write, verification, and recoverability observations | `backup.write_observed`, `.verification_observed`, `.recoverability_observed` | `backup` |
| Restore case | open, record report, close | `restore.case_opened`, `.report_recorded`, `.case_closed` | `restore_case` |
| Security frontier/control | record frontier, enter quarantine, change bounded service scope | `recovery.current_policy_frontier_recorded`, `.quarantine_entered`, `.service_scope_changed` | `recovery_control` |
| Recovery decision | record exact quorum decision | `recovery.decision_recorded` | `recovery_decision` |
| Fork/epoch | record fork, begin constitutional epoch | `ledger.fork_detected`, `ledger.epoch_started` | `ledger_epoch` |

The three backup events intentionally do not collapse: successful byte writing changes neither verification nor recoverability. Checkpoint proposal, signed seal, external witness observation, and consistency failure are also distinct facts. A witness observation is external evidence; it is not inferred from the checkpoint signature.

`restore.report_recorded` carries `authority_effect=no_service_reopen`. A passing report advances only the restore case. Reopening any bounded service scope requires a separate recovery-quorum decision and then `recovery.service_scope_changed` against a proven-complete current-security frontier. Its closed command candidate structurally keeps publication, spending, R2+ effects, and physical actions disabled. Structural validity does not prove the frontier complete, the quorum independent, or the restored system correct.

A fork observation records every known branch head and forces quarantine. `ledger.epoch_started` is admitted only against `constitutional_new_epoch`, named prior heads/checkpoints, unresolved receipts, identity non-reuse evidence, and `wall_clock_branch_selection=false`. It does not merge or rewrite prior history.

## Ledger epochs and forks

An epoch identifies one canonical continuity regime. A normal restore continues the same epoch and positions. A new epoch is allowed only for an explicit constitutional recovery when continuity cannot be proven; it references every known prior head/checkpoint, incident, recovery decision, and unresolved receipt.

The new epoch must not reuse event, command, effect, grant, artifact, or publication identities. It cannot declare an unproven branch canonical by timestamp. The recovery quorum chooses a branch only under the frozen root policy and records dissent/unknowns. Scientific dependents remain blocked until their referenced history and bytes are proven present.

No automated merge of divergent canonical ledgers exists. Projections may compare branches; canonical state may not average or union incompatible histories.

## Acknowledgement levels

Success responses expose their durability level:

| Level | Meaning | Permitted use |
|---|---|---|
| `committed_local` | Canonical transaction committed under the active database durability profile; no independent checkpoint yet covers it | Ordinary continuation only within accepted loss window; never described as externally witnessed |
| `replicated_durable` | Commit is confirmed by the profile's independent synchronous replica set | Required for acknowledged high-consequence command under the founding target |
| `checkpointed` | A signed checkpoint covers the commit | Eligible for long-term evidentiary reference subject to artifact checks |
| `witnessed` | Required external witness set accepted the checkpoint and consistency proof | Required before irreversible publication or R2+ effect under the founding target |

A client timeout creates unknown acknowledgement, not rollback. Repeating the same command ID retrieves the retained receipt. A signed receipt outside the database that refers to a missing restored command is integrity evidence and forces quarantine; it is not silently discarded as a client artifact.

## Founding recovery objectives

These are service objectives and integrity consequences, not evidence a product currently meets them:

| Plane | Target | If target cannot be proven |
|---|---|---|
| Acknowledged C0/C1 high-consequence facts | RPO 0 within the declared supported failure model; zero undetected loss in every model | Global write/effect quarantine; compare receipts, replicas, backups, and witnesses; append recovery incident |
| Ordinary committed C1 research facts | Maximum data-loss point must be disclosed in each receipt/profile and never exceed the last valid durable copy; target RPO 0 after first production profile | Mission blocked/corrected from the last proven position; never reconstruct events from prose |
| C2 claim-bearing/publication artifacts | No substituted bytes; target at least two verified failure-domain copies before eligibility | Dependents become unavailable/ineligible until exact bytes return; permanent loss triggers correction/withdrawal |
| C3 effect evidence | No loss of ambiguity; reconciliation work queue recoverable from C1 | Effects remain `completion_unknown`; no blind retry or closure |
| C4 scheduler state | At-least-once operational recovery from C1; target 1 hour to resume reconciliation/control work | Recreate only next legal attempts with stable identities; no scientific inference |
| C5 projections | RPO equals named canonical position; target 4 hours for critical cockpit, 24 hours for full search/reporting | Serve explicit unavailable/stale state; never use old projection for authority |
| Control-plane recovery | Target 1 hour to verified read-only incident cockpit, 4 hours to canonical reads, 24 hours to reviewed bounded writes | Stay isolated/read-only; external effects and releases disabled |

The final deployment profile must replace qualitative failure domains with exact region/host/account/administrator/key/witness assumptions and demonstrate the target. `RPO 0` means zero loss within those named assumptions, not protection against every physical or institutional catastrophe.

## Backup contract

Every backup set has a signed `BackupManifest` binding:

- source ledger epoch and begin/end positions;
- base/snapshot and incremental dependency identities;
- database engine/logical-format versions and restore prerequisites;
- exact object/artifact set or shard commitments;
- scheduler/export components when retained;
- encryption key identifier and recovery policy, never key material;
- creation actor/activity, tool/image/config identities, times, and verification result;
- residency, classification, retention, hold, and destruction profile;
- prior checkpoint and first checkpoint expected after restore; and
- manifest digest/signature and independent catalog observation.

Backups are immutable against ordinary application credentials. Backup administration, application administration, witness administration, and key recovery are separated according to the accepted risk tier.

Backup completion means bytes were written. Backup verification means exact manifest/digest checks passed. Recoverability means a clean-room restore drill passed all semantic checks. These are separate retained states.

[`backup-manifest` 0.6.0](../schemas/backup-manifest.schema.json) represents those three states separately and makes embedded key material structurally impossible. Its deployment-neutral fixture intentionally leaves recoverability `not_run`; a completed and digest-verified backup must not be narrated as a proven restore.

## Restore procedure

A production restore follows a deterministic case, never an improvised operator checklist:

1. declare incident, freeze canonical writes, disable dispatch/publication, revoke or isolate relevant credentials, and preserve volatile evidence;
2. identify the latest mutually consistent root manifest, checkpoint, witness observation, database copy, backup chain, artifact copies, and client receipts;
3. provision an isolated recovery environment with independently verified tools and no production effects;
4. restore C0 first, verify exact schemas/rules/policies/trust roots, and reject `latest` aliases;
5. restore C1 to a named position; verify record syntax, canonical digests, batch/stream/global continuity, transaction cohorts, aggregate reduction, receipts, authority/resource invariants, and checkpoint consistency;
6. verify C2 bytes against the promoted-artifact registry using full reads according to coverage policy, not storage metadata alone;
7. enumerate unresolved effects, active grants, active and claimed resource reservations, leases, deletion/hold cases, incidents, publications, and pending corrections at the restored position; claimed reservations retain the full ceiling until exact observation-backed settlement;
8. apply all later accepted revocation/deletion/checkpoint facts found in independent receipts/witnesses before granting access;
9. rebuild C5 projections from zero or an independently verified projection snapshot, then replay to the named position;
10. run known-answer, known-bad, reducer-equivalence, authorization, publication, deletion-resurrection, and effect-retry tests;
11. obtain recovery-quorum review of an exact `RestoreVerificationReport`;
12. reopen canonical reads, then reconciliation/control commands, then ordinary research writes in bounded stages; and
13. keep publication, spending, R2+ effects, and physical actions disabled until their explicit higher-tier exit evidence passes.

Restored scheduler history is reconciled after C1. A scheduled activity that has no legal next action in canonical state is cancelled/quarantined even if the scheduler calls it running.

[`restore-verification-report` 0.5.0](../schemas/restore-verification-report.schema.json) binds the selected sources, isolated environment, all C0–C6 plane results, current-security frontier, the eleven founding invariants, known-answer/known-bad results, review determinations, and a fail-closed service recommendation. [`recovery-decision` 0.6.0](../schemas/recovery-decision.schema.json) is the separate recovery-quorum decision. Neither record is a publication, spending, R2+ effect, or physical-action grant.

## Restore verification invariants

A restore cannot be accepted unless it proves or explicitly blocks on:

1. every aggregate reduces to its stored head at the restored global position;
2. every command ID maps to one request digest and one immutable receipt outcome;
3. each committed event batch has its complete authority/resource/outbox transaction cohort;
4. grant issue/use/reservation/release/revoke/expiry ordering and balances reconcile;
5. every resource child follows `none -> active -> claimed -> settled` or pre-claim `active -> released|expired`; reserve/claim cohorts are complete, claimed ceilings survive crash/recovery, execution/currency/verification dimensions never compensate, and estimated/attempted/actual/billed/refunded/settled values satisfy componentwise conservation without unknown-to-zero conversion;
6. every eligible claim and sealed publication traverses to available exact protocol, evidence, code, environment, verification, decision, and manifest bytes;
7. every external effect is either never dispatched, confirmed applied, confirmed not applied, or visibly unknown with one legal next action;
8. every deletion, legal hold, revocation, correction, withdrawal, and incident observed beyond a backup's time prevents stale-state resurrection;
9. checkpoint inclusion/consistency and required witness observations verify through the chosen position;
10. projection rows expose the restored ledger position and cannot authorize commands from stale state; and
11. no key, credential, endpoint, provider alias, mutable branch, or wall clock is accepted only because the backup contained it.

If any proof is indeterminate, the affected scope remains quarantined. A partial mission may resume only if dependency and authority boundaries prove it independent of the fault.

## Key hierarchy and recovery

The founding logical hierarchy separates:

- constitutional/root-manifest signing;
- ledger-checkpoint signing;
- witness signing/observation;
- publication-manifest and publication-grant signing;
- service/workload identity;
- data-encryption keys by tenant/data class/retention domain;
- backup-encryption keys; and
- provider/operational credentials.

Key purpose is cryptographically/policy bound where the selected system permits it. A checkpoint key cannot issue an authority grant; an application service key cannot sign a root rotation; an encryption key cannot serve as evidence of publication approval.

The deployment profile specifies generation, hardware protection, exportability, quorum, activation, overlap, rotation, revocation, compromise, escrow/recovery, destruction, algorithm agility, and time trust for each class. Recovery shares are never colocated with the encrypted backup and ordinary application administrators cannot satisfy the full high-consequence recovery quorum.

Key loss and key compromise are distinct incidents. Loss may make bytes unrecoverable; compromise makes authenticity after a bounded time uncertain. Neither is repaired by re-signing old subjects. Old signatures/checkpoints retain original key/time/trust evidence plus the compromise assessment.

The deployment-neutral [`key-profile` 0.5.0](../schemas/key-profile.schema.json) requires all eight logical classes, explicit allowed and forbidden operations, activation and recovery quorums, separation constraints, lifecycle policies, algorithm agility, and a hard `key_material_embedded=false` boundary. Its proposed fixture is not evidence of a selected cryptographic product, protected key, or executable recovery setup.

## Restore resurrection and current-policy fence

A backup is historical and therefore contains permissions that may no longer be valid. Before any restored principal can read data or dispatch work, the recovery environment must ingest the latest independently witnessed security frontier containing at least:

- root/policy/schema changes;
- key and identity revocations;
- authority/grant revocations and expiries;
- data deletion, restriction, and legal-hold facts;
- incident quarantines;
- claim corrections/retractions; and
- publication withdrawals/channel settlements.

If the frontier cannot be proven complete, restored service remains isolated. Historical credentials and grants are never enabled merely to fetch the newer frontier.

## Projection and index recovery

Every projection declares reducer/code/schema identity, source ledger epoch and position, build time, and completeness/freshness. A projection snapshot is accepted only with a canonical checkpoint it exactly covers and an independent reducer-equivalence result.

After recovery:

- authority decisions read current canonical state, not the restored cache;
- retrieval results surface source identity and position;
- vector/full-text indexes purge tombstoned or access-revoked sources before becoming available;
- public projections replay correction/withdrawal fanout before serving old claims; and
- a failed or partial rebuild is visibly unavailable, never silently incomplete.

## Disaster and adversarial drills

The first profile must execute clean-room drills for:

- primary database loss after acknowledged commit but before client response;
- loss after checkpoint creation but before witness acknowledgement;
- a valid old backup plus a later grant revocation and data deletion;
- truncated event suffix with internally valid per-record hashes;
- two signed but inconsistent checkpoint views;
- corrupt or missing claim-bearing artifact bytes;
- object store rollback while ledger is current, and vice versa;
- lost checkpoint key, compromised application key, and unavailable recovery principal;
- scheduler replay attempting a duplicate external effect;
- publication timeout during disaster recovery;
- backup catalog compromise or ransomware deletion;
- incompatible database/tool version and partial incremental chain; and
- full projection rebuild with correction, rights, and sealed-truth boundaries.

Each drill retains environment, injected fault, observations, timing, resource cost, invariant results, residual risks, and corrective action. A scripted green check without artifact inspection is insufficient.

## Architecture falsifiers

This design fails if a supported trace can:

- return success for a high-consequence command that can be lost without detection inside the declared model;
- accept a locally consistent truncated ledger despite a later witnessed checkpoint or receipt;
- restore revoked access, deleted data, withdrawn publication, or expired authority;
- choose between ledger forks using last-write-wins or wall-clock order;
- regenerate missing scientific evidence and give it the old identity;
- retry an ambiguous external effect because scheduler history was lost;
- let backup/witness/application administration collapse into one unreviewed principal at a tier requiring separation;
- claim restoration while eligible evidence bytes remain unchecked or absent;
- expose a projection without its exact source position; or
- use unavailable recovery objectives as permission to lower scientific or authority invariants.

## Gate A and implementation evidence

The checkpoint, backup-manifest, restore-report, key-profile, recovery-decision, 16 recovery command discriminators, 16 typed recovery event branches, four high-consequence recovery command-payload candidates, and five recovery-focused replay traces now exist structurally. Gate A may accept this contract only when their semantic rules and known-bad traces execute independently, reducer equivalence is proven, canonicalization/commitment vectors are frozen, and independent architecture/security reviewers close critical/high findings. Schema presence alone closes none of those semantic obligations.

The exact first deployment profile must then pin database isolation/durability/replication, backup technology and cadence, object replication/scrubbing, key/witness topology, checkpoint cadence, acknowledgement policy, recovery objectives, and drill environment. Those product claims require authorized Gate B evidence before Gate C implementation relies on them.

Until that evidence exists Odeya may claim a recovery contract and test plan—not zero data loss, tamper proofness, disaster recovery readiness, or non-equivocation.
