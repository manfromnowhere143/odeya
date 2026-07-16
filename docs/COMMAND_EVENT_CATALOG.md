# Command and Event Catalog

Status: architecture-closure candidate, 2026-07-16. This contract is non-executable and does not authorize product implementation. It replaces the legacy single-status event draft with the orthogonal event algebra in `research-event` and adds language-neutral command/receipt envelopes. [ADR 0014](decisions/0014-resolve-first-slice-atomic-admission.md) fixes the bounded first-slice producer/reducer choices; exact prospective member versions remain to be frozen.

## Canonical contracts

- `schemas/command-envelope.schema.json` 0.4.0 currently binds the request identity and one of 121 declared design discriminators to its exact semantic version, payload-schema ID, immutable registry-snapshot reference, separate activation proof, exact contract-record reference, target stream family, aggregate owner, optimistic positions, actor, untrusted presented authority hints, causal inputs, payload, and a non-recursive request-digest contract. The hints are resolution inputs only: the caller cannot select an authority mode, derivation rule, or PolicyDecision. “Declared” does not mean admitted: under [ADR 0013](decisions/0013-admitted-only-command-ingress.md), this broad file is a red-team candidate and must be regenerated from the exact admitted registry so no discriminator lacks complete contract bytes.
- `schemas/command-receipt.schema.json` 0.3.0 begins only after exact registry-member resolution and immutably settles one idempotency-scope plus command-ID pair. It binds the result to the resolved registry snapshot/activation/member record, a closed admission-evidence bundle, exact policy/validation records, and non-recursive result/receipt digest contracts.
- `schemas/research-event.schema.json` currently defines 135 event discriminators after replacing generic `resource.observed` with typed `work.lease_expired`. Every discriminator fixes one payload-schema ID, one stream family, one aggregate owner, one fact-time basis, one closed payload shape, and explicit payload/event digest contracts. Every command-bound event also carries an exact AdmissionEvidenceBundle reference. This is still broad design vocabulary, not an admitted event registry.
- `schemas/research-event-trace.schema.json` 0.3.0 binds ordered event vectors and typed command-receipt observations to orthogonal scientific, authority, data-governance, governed-processing, recovery, and resource-accounting axes. It structurally forbids the founding invalid-run/null, disputed-verification/eligibility, grant-reservation/dispatch-claim, rejected-processing/cohort, deletion-resurrection, incomplete-frontier reopen, missing-artifact reopen, fork-selection, restore-report-as-authority, claimed-resource release, inferred usage, unknown-as-zero, and unobserved-settlement contradictions.
- [The state model](STATE_MODEL.md) defines the reducer axes and transition laws. Schema validity is necessary but never sufficient for transition legality.

A command is an untrusted request. A receipt is the durable admission result. An event is an immutable retained fact. A worker callback, model answer, provider receipt, UI action, timer, or human click changes no canonical state until admitted through a registered command.

## Stream and aggregate law

The founding ledger has eight stream classes:

| Stream | Mission scope | Purpose |
|---|---|---|
| `portfolio` | optional | company-level intake and proposal policy |
| `proposal` | optional | pre-mission proposal history, including decline and withdrawal |
| `mission` | required | one mission's scientific and operational facts |
| `authority_root` | optional | constitutional assignments and authority facts |
| `incident` | required | retained mission-scoped security/safety response history; company-wide incidents use a `portfolio` stream |
| `learning` | required for mission-derived learning | grounded outcomes and quarantined strategy candidates |
| `data_governance` | optional; required when the governed asset is mission-scoped | shared or mission-scoped rights and lifecycle facts that must not be forced into a synthetic mission |
| `recovery` | forbidden (`null`) | global checkpoint, witness, backup, restore, frontier, fork, epoch, and recovery-control facts |

A fake mission ID is forbidden. Proposal acceptance and mission-origin creation are two causal commits, not a cross-stream atomic transaction.

Every event owns exactly one aggregate and advances exactly one aggregate version. A multi-aggregate batch advances every named head atomically; no checkpoint, receipt, canonical read frontier, or current projection may end at an interior batch position. The founding aggregate vocabulary is:

`proposal`, `mission`, `protocol`, `work_graph`, `stage`, `work_item`, `attempt`, `resource_budget`, `blocker`, `artifact`, `run`, `measurement`, `metric`, `falsifier`, `verification`, `review`, `adjudication`, `claim_proposal`, `claim_version`, `dependency`, `external_effect`, `publication`, `authority_assignment`, `authority_grant`, `incident`, `handoff`, `grounded_outcome`, `strategy_candidate`, `data_asset`, `rights_assertion`, `data_use_decision`, `data_exposure`, `transformation`, `retention_schedule`, `deletion_case`, `legal_hold`, `ledger_checkpoint`, `backup`, `restore_case`, `recovery_decision`, `ledger_epoch`, and `recovery_control`.

A transaction may append a multi-aggregate batch to one stream. No event is reduced by two aggregates. Cross-stream and cross-mission atomic batches are forbidden.

## Command admission and immutable settlement

Admission order is normative:

1. Authenticate the execution identity and establish controlled recorded time.
2. Resolve the exact immutable command-registry snapshot and contract record, then verify a separate activation proof whose checkpoint/position is admissible for this tenant, mission, and target ledger position. Registry bytes never embed the checkpoint that activates them, and `latest` resolution is forbidden.
3. Canonicalize the envelope and compute the request digest.
4. Look up `idempotency_scope + command_id` before testing caller positions.
5. Return the exact retained result for the same ID and digest. Changed-digest reuse is an ingress/idempotency conflict and cannot create a competing `CommandReceipt` under the same key.
6. Assert envelope and payload structure, formats, canonical numbers, media types, and size bounds.
7. Compare expected stream position and aggregate version.
8. Resolve every referenced artifact, event, protocol, manifest, assignment, grant, and rights record. Generate the PolicyDecision inside admission; a caller cannot submit its identity.
9. Evaluate custody, rights, classification, exposure, budget, risk, state, quorum, role separation, grant limits, controlled time, and revocation.
10. Generate the pure immutable PolicyDecision and the CommandContractRecord-selected validation/reference/authority/rights/resource/risk/transition records over the exact frontier.
11. Run the pure command decision and build one closed AdmissionEvidenceBundle. Generated prose and model/tool output may be referenced evidence but cannot alter this function.
12. Atomically persist the immutable admission evidence, receipt, grant-use/resource facts, domain-event batch, aggregate heads, and outbox.
13. Return the receipt. Projection freshness is separate.

The receipt has one of three canonical results:

| Result | Meaning | Event requirement |
|---|---|---|
| `accepted` | canonical state changed | at least one event reference and resulting stream head |
| `rejected` | admission failed | typed code and admission stage; no domain event merely to log an ordinary rejection |
| `noop` | request was legal but state already represented it | named no-op reason and unchanged heads |

The receipt's `result_digest` binds the entire result. The request, result, receipt, event payload, event, and checkpoint each use a distinct domain separator and an exact included/excluded JSON-Pointer set. Digest/signature values are outside their own hash scope; signatures are external attestations. Schema shape does not recompute a digest, prove a signature, prove snapshot activation/currentness, prove duplicated record metadata equal, or prove admission evidence complete. The replay contract is always `return_exact_bound_result`; a retry never reevaluates current state. A changed payload, target, actor binding, authority claim, registry binding, or input is a new command ID. A transport may mark a response as replayed, but it may not mutate the canonical receipt.

`CommandReceipt` is not a raw-ingress receipt. An unparseable envelope, unknown or unadmitted command, invalid membership, or changed-digest ID reuse has no truthful new member-bound receipt and is refused before receipt creation. Policy may route evidence-relevant abuse through a separate registered security-observation command. `schema_unresolvable` is legal only after member proof fixes the exact schema ID/digest but retained schema bytes cannot be loaded; `schema_invalid` requires those exact bytes to have resolved and rejected the payload.

Reservation-aware admission uses stable rejections: `grant_consumption_point_mismatch`, `grant_reservation_missing`, `grant_reservation_mismatch`, `grant_reservation_expired`, `grant_reservation_released`, `grant_reservation_cancelled`, and `dispatch_already_claimed`. An accepted authorize/start/cancel receipt must reference the complete required event cohort under one `commit_id`; the schema retains those event references, while semantic validation proves cohort completeness and equality.

## Authority evidence without recursion

Actor identity is not authority. A command carries only typed, untrusted references that may help the kernel resolve authority. It cannot declare the mode, derivation rule, PolicyDecision, validity, or result. The admission kernel derives one authority-evidence mode from current canonical records, and accepted events retain that derived basis:

| Mode | Required basis | Use |
|---|---|---|
| `constitutional_bootstrap` | reviewed constitutional artifact | initial root assignment only |
| `ingress_policy` | server-generated immutable PolicyDecision in the admission cohort | non-scientific intake; the caller supplies no policy-decision identity or result |
| `kernel_derivation` | versioned pure rule | mechanical consequences |
| `assigned_role` | one or more active assignments | role-owned decisions |
| `bounded_grants` | commands: grant refs; events: same-batch exact grant-use reservation or consumption refs | consequential bounded action |
| `external_observation` | retained source in fact time | provider/instrument observations; no inferred decision authority |

The first root assignment does not self-grant. For an ordinary in-ledger command, `authority.grant_used(consumption_point=domain_commit)` is a kernel-produced fact in the same batch as the authorized domain fact. For a cross-boundary effect, T1 emits `authority.grant_use_reserved` with `external_effect.authorized`; the dispatch claim later emits `authority.grant_used(consumption_point=dispatch_claim)` with `external_effect.started`. Callers can submit none of these facts directly. Revocation/release versus dispatch is decided by canonical commit order.

## Canonical producer and reducer registry

“Producer” names the closed command or kernel boundary allowed to derive an exact event member version. “Reducer” is the sole aggregate projection that consumes it. An event delivered to any other reducer is rejected as a contract defect. The table can show broad design producers; an activated slice narrows each exact member to its admitted producer set.

### Intake, mission, protocol, and work

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `proposal.submitted` | `proposal.submit` | proposal / Proposal |
| `proposal.decided` | `proposal.decide` | proposal / Proposal |
| `proposal.withdrawn` | `proposal.withdraw` | proposal / Proposal |
| `mission.origin_recorded` | `mission.create_origin` | mission / Mission |
| `mission.contract_compiled` | `mission.compile_contract` | mission / Mission |
| `mission.phase_advanced` | `mission.advance_phase` | mission / Mission |
| `mission.control_changed` | `mission.change_control` | mission / Mission |
| `handoff.recorded` | `mission.record_handoff` | handoff / Handoff |
| `mission.closed` | `mission.close` | mission / Mission |
| `protocol.exposure_recorded` | `protocol.record_exposure` | protocol / Protocol |
| `protocol.integrity_determined` | protocol consequence kernel in the same batch as the determining freeze, exposure, or amendment | protocol / Protocol |
| `protocol.frozen` | `protocol.freeze` | protocol / Protocol |
| `protocol.amended` | `protocol.amend` | protocol / Protocol |
| `protocol.forked` | `protocol.fork` | protocol / Protocol |
| `protocol.superseded` | `protocol.supersede` | protocol / Protocol |
| `work_graph.compiled` | `work_graph.compile` | work_graph / WorkGraph |
| `stage.readiness_changed` | `stage.set_readiness` | stage / StageReadiness |
| `stage.authorization_changed` | `stage.set_authorization` | stage / StageAuthorization |
| `work.lease_acquired` | `work.acquire_lease`; first-slice exact member: `verification.assign` | work_item / WorkLease |
| `work.lease_renewed` | `work.renew_lease` | work_item / WorkLease |
| `work.lease_released` | `work.release_lease`; first-slice exact member: `attempt.report` after observed terminal teardown | work_item / WorkLease |
| `work.lease_revoked` | `work.revoke_lease`; first-slice exact member: `attempt.report` or `verification.invalidate` under a closed branch | work_item / WorkLease |
| `work.lease_expired` | first-slice controlled-deadline branch of `verification.invalidate`; never caller-selectable | work_item / WorkLease |

### Attempts, resources, blockers, evidence, and science

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `attempt.started` | `attempt.start` | attempt / AttemptExecution |
| `attempt.interrupted` | `attempt.report` | attempt / AttemptExecution |
| `attempt.completion_unknown` | `attempt.report` | attempt / AttemptExecution |
| `attempt.completed` | `attempt.report` | attempt / AttemptExecution |
| `attempt.failed` | `attempt.report` | attempt / AttemptExecution |
| `attempt.cancelled` | `attempt.report`; outside the bounded first slice | attempt / AttemptExecution |
| `resource.reservation_created` | resource-accounting kernel in the exact admission/authorization cohort; first-slice caller command `verification.assign` | resource_budget / ResourceLedger |
| `resource.reservation_claimed` | resource-accounting kernel in the exact work/effect/verification start cohort; first-slice caller command `attempt.start` | resource_budget / ResourceLedger |
| `resource.reservation_released` | resource-accounting kernel in a winning pre-claim cancellation, rejection, revocation, or invalidation cohort | resource_budget / ResourceLedger |
| `resource.reservation_expired` | controlled-time resource-accounting kernel before any claim commits; first-slice controlled-deadline branch of `verification.invalidate` | resource_budget / ResourceLedger |
| `resource.usage_observed` | `resource.record_observation` after resolving exact retained meter/instrument/reviewed evidence | resource_budget / ResourceLedger |
| `resource.reservation_settled` | `resource.record_observation` only when the new typed observation completes the exact settlement profile and equations in the same batch | resource_budget / ResourceLedger |
| `budget.exhausted` | `budget.record_exhaustion` | resource_budget / ResourceLedger |
| `blocker.opened` | `blocker.open` | blocker / Blocker |
| `blocker.resolved` | `blocker.resolve` | blocker / Blocker |
| `blocker.superseded` | `blocker.supersede` | blocker / Blocker |
| `artifact.recorded` | `artifact.record` | artifact / ArtifactCustody |
| `artifact.validated` | `artifact.record_validation` | artifact / ArtifactCustody |
| `artifact.promoted` | `artifact.promote` | artifact / ArtifactCustody |
| `artifact.quarantined` | `artifact.quarantine` | artifact / ArtifactCustody |
| `artifact.corrupt_detected` | `artifact.record_corruption` | artifact / ArtifactCustody |
| `artifact.unavailable` | `artifact.record_unavailability` | artifact / ArtifactCustody |
| `artifact.tombstoned` | `artifact.tombstone` | artifact / ArtifactCustody |
| `run.validity_determined` | `run.determine_validity` | run / RunValidity |
| `measurement.disposition_determined` | broad vocabulary: `measurement.determine_disposition`; first-slice exact member: `run.determine_validity` in the atomic validity pair | measurement / MeasurementDisposition |
| `metric.observed` | `metric.record_observation` | metric / MetricObservation |
| `falsifier.adjudicated` | `falsifier.adjudicate` | falsifier / Falsifier |
| `review.recorded` | `review.record` | review / Review |

### Verification and scientific settlement

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `verification.requested` | `verification.request` | verification / Verification |
| `verification.assigned` | `verification.assign` | verification / Verification |
| `verification.started` | broad vocabulary: `verification.start`; first-slice exact member: `attempt.start` in the atomic local-start cohort | verification / Verification |
| `verification.completed` | `verification.complete` | verification / Verification |
| `verification.disputed` | `verification.dispute` | verification / Verification |
| `verification.dispute_resolved` | `verification.resolve_dispute` | verification / Verification |
| `verification.invalidated` | `verification.invalidate` | verification / Verification |
| `reproducibility.determined` | `reproducibility.determine` | verification / Verification |
| `replication.started` | `replication.start` | verification / Verification |
| `replication.determined` | `replication.determine` | verification / Verification |
| `transport.started` | `transport.start` | verification / Verification |
| `transport.determined` | `transport.determine` | verification / Verification |
| `adjudication.recorded` | `adjudication.record` | adjudication / Adjudication |
| `claim.proposed` | `claim.propose` | claim_proposal / ClaimProposal |
| `claim.disposition_recorded` | `claim.record_disposition` | claim_proposal / ClaimProposal |
| `claim.version_compiled` | `claim.compile_version`; immutable exact ClaimVersion references are the canonical dependency-edge source | claim_version / ClaimVersion |
| `claim.superseded` | `claim.supersede` | claim_version / ClaimVersion |
| `claim.retracted` | `claim.retract` | claim_version / ClaimVersion |
| `dependency.invalidation_recorded` | broad vocabulary: `dependency.record_invalidation`; first-slice exact member: `claim.supersede` in the atomic correction cohort | dependency / DependencyInvalidationFrontier |

### Authority, publication, effects, incidents, and learning

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `authority.assignment_recorded` | `authority.record_root_assignment` or `authority.record_assignment`; branch is fixed by authority mode | authority_assignment / AuthorityAssignment |
| `authority.grant_issued` | `authority.issue_grant` | authority_grant / AuthorityGrant |
| `authority.grant_activated` | `authority.observe_activation` | authority_grant / AuthorityGrant |
| `authority.grant_use_reserved` | admission kernel in the `external_effect.authorize` T1 cohort; never caller-facing | authority_grant / AuthorityGrant |
| `authority.grant_use_reservation_released` | admission kernel in the winning revoke/expiry/cancel/invalidation cohort; never caller-facing | authority_grant / AuthorityGrant |
| `authority.grant_used` | admission kernel in an ordinary domain-commit or external-effect dispatch-claim cohort; never caller-facing | authority_grant / AuthorityGrant |
| `authority.grant_exhausted` | admission kernel after the last legal use | authority_grant / AuthorityGrant |
| `authority.grant_expired` | `authority.observe_expiry` | authority_grant / AuthorityGrant |
| `authority.grant_revoked` | `authority.revoke_grant` | authority_grant / AuthorityGrant |
| `publication.candidate_compiled` | `publication.compile_candidate` | publication / Publication |
| `release.requested` | `release.request` | publication / Publication |
| `release.decided` | `release.decide` | publication / Publication |
| `publication.sealed` | `publication.seal` | publication / Publication |
| `publication.release_started` | `publication.start_release` | publication / Publication |
| `publication.release_settled` | `publication.record_release_settlement` | publication / Publication |
| `publication.corrected` | `publication.correct` | publication / Publication |
| `publication.withdrawn` | `publication.withdraw` | publication / Publication |
| `external_effect.authorized` | `external_effect.authorize` | external_effect / ExternalEffect |
| `external_effect.started` | `external_effect.start` | external_effect / ExternalEffect |
| `external_effect.cancelled_before_dispatch` | `external_effect.cancel` | external_effect / ExternalEffect |
| `external_effect.completion_reported` | `external_effect.report_completion` | external_effect / ExternalEffect |
| `external_effect.reconciliation_started` | `external_effect.start_reconciliation` | external_effect / ExternalEffect |
| `external_effect.reconciliation_completed` | `external_effect.complete_reconciliation` | external_effect / ExternalEffect |
| `external_effect.reconciliation_failed` | `external_effect.fail_reconciliation` | external_effect / ExternalEffect |
| `incident.opened` | `incident.open` | incident / Incident |
| `incident.transitioned` | `incident.transition` | incident / Incident |
| `grounded_outcome.recorded` | `grounded_outcome.record` | grounded_outcome / GroundedOutcome |
| `strategy.candidate_recorded` | `strategy.record_candidate` | strategy_candidate / StrategyCandidate |
| `strategy.shadow_authorized` | `strategy.authorize_shadow` | strategy_candidate / StrategyCandidate |
| `strategy.shadow_recorded` | `strategy.record_shadow` | strategy_candidate / StrategyCandidate |
| `strategy.canary_authorized` | `strategy.authorize_canary` | strategy_candidate / StrategyCandidate |
| `strategy.promotion_decided` | `strategy.decide_promotion` | strategy_candidate / StrategyCandidate |
| `strategy.rolled_back` | `strategy.rollback` | strategy_candidate / StrategyCandidate |

### Data governance

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `data_asset.recorded` | `data_asset.record` | data_asset / DataAsset |
| `data_asset.lifecycle_changed` | `data_asset.change_lifecycle` | data_asset / DataAsset |
| `rights_assertion.recorded` | `rights_assertion.record` | rights_assertion / RightsAssertion |
| `data_use.decided` | `data_use.decide` | data_use_decision / DataUseDecision |
| `data_use.revoked` | `data_use.revoke` | data_use_decision / DataUseDecision |
| `data_exposure.intent_recorded` | `data_exposure.record_intent` | data_exposure / DataExposure |
| `data_exposure.observation_recorded` | `data_exposure.record_observation` | data_exposure / DataExposure |
| `data_exposure.settlement_recorded` | `data_exposure.record_settlement` | data_exposure / DataExposure |
| `transformation.recorded` | `transformation.record` | transformation / Transformation |
| `retention.schedule_recorded` | `retention.record_schedule` | retention_schedule / RetentionSchedule |
| `deletion.case_opened` | `deletion.open_case` | deletion_case / DeletionCase |
| `deletion.progress_recorded` | `deletion.record_progress` | deletion_case / DeletionCase |
| `deletion.case_closed` | `deletion.close_case` | deletion_case / DeletionCase |
| `legal_hold.issued` | `legal_hold.issue` | legal_hold / LegalHold |
| `legal_hold.released` | `legal_hold.release` | legal_hold / LegalHold |
| `legal_hold.expired` | `legal_hold.observe_expiry` | legal_hold / LegalHold |

`rights_assertion.recorded` is an external evidence fact with `authority_effect=evidence_only_no_permission`; only `data_use.decided` can create bounded data-use authority. Exposure intent is also not dispatch: its closed high-consequence command payload requires `recording_intent_does_not_dispatch=true` and names the separate external-effect identity through which bytes may later cross a boundary. Observation and settlement remain distinct, and `completion_unknown` is never reduced to zero or `confirmed_not_exposed`.

### Ledger integrity and recovery

| Event | Sole producer | Aggregate / reducer |
|---|---|---|
| `ledger_checkpoint.proposed` | `ledger_checkpoint.propose` | ledger_checkpoint / LedgerCheckpoint |
| `ledger_checkpoint.sealed` | `ledger_checkpoint.seal` | ledger_checkpoint / LedgerCheckpoint |
| `ledger_checkpoint.witness_observed` | `ledger_checkpoint.record_witness_observation` | ledger_checkpoint / LedgerCheckpoint |
| `ledger_checkpoint.consistency_failed` | `ledger_checkpoint.record_consistency_failure` | ledger_checkpoint / LedgerCheckpoint |
| `backup.write_observed` | `backup.record_write_observation` | backup / Backup |
| `backup.verification_observed` | `backup.record_verification_observation` | backup / Backup |
| `backup.recoverability_observed` | `backup.record_recoverability_observation` | backup / Backup |
| `restore.case_opened` | `restore.open_case` | restore_case / RestoreCase |
| `restore.report_recorded` | `restore.record_report` | restore_case / RestoreCase |
| `restore.case_closed` | `restore.close_case` | restore_case / RestoreCase |
| `recovery.current_policy_frontier_recorded` | `recovery.record_current_policy_frontier` | recovery_control / RecoveryControl |
| `recovery.decision_recorded` | `recovery.record_decision` | recovery_decision / RecoveryDecision |
| `recovery.quarantine_entered` | `recovery.enter_quarantine` | recovery_control / RecoveryControl |
| `recovery.service_scope_changed` | `recovery.change_service_scope` | recovery_control / RecoveryControl |
| `ledger.fork_detected` | `ledger.record_fork` | ledger_epoch / LedgerEpoch |
| `ledger.epoch_started` | `ledger.begin_epoch` | ledger_epoch / LedgerEpoch |

Checkpoint proposal, signed seal, witness observation, and consistency failure are separate facts. Backup write, byte/manifest verification, and clean-room recoverability are three separate observations; no reducer promotes one into another. `restore.report_recorded` has `authority_effect=no_service_reopen`. Only a separate recovery-quorum decision followed by `recovery.service_scope_changed` can alter recovery control, and that command structurally keeps publication, spending, R2+ effects, and physical actions disabled. A fork enters quarantine; a new epoch requires a constitutional recovery decision, named prior heads, identity non-reuse evidence, and `wall_clock_branch_selection=false`.

The two root-assignment producers share one event only because the payload and authority mode make the branches disjoint: bootstrap requires a constitutional artifact; ordinary assignment requires an issuer assignment. Before Gate A, the registry must either preserve this explicit branch or split it into two event types.

## Batch and replay laws

1. All events derived from one accepted command share command binding, commit ID, correlation ID, batch size, and request digest.
2. Batch indexes are zero-based, unique, and contiguous; stream positions and aggregate versions are allocated only at commit.
3. Every event's previous-stream digest names the immediately preceding event, including the prior member of the same batch.
4. Receipt, grant-use reservation/use/release facts, domain facts, heads, resource reservation facts, and causally required outbox records commit together or not at all.
5. A reservation is one child of its `resource_budget`, keyed by `reservation_id`. Creation binds an exact budget head, non-fungible unit profile, estimate, ceiling, subject, and start cohort; it cannot fabricate a second aggregate or spend one dimension as another.
6. Claim commits the entire ceiling at the exact work/effect/verification start cohort and does not infer attempted, actual, billed, or refunded use. Crash, recovery, lost callback, and `completion_unknown` retain the full claim hold.
7. Release and expiry are pre-claim terminals only. A claimed reservation can reach only observation and settlement; it cannot be released as unused because a process died or a response was missing.
8. Settlement requires exact retained observations. Componentwise, `net = reserved_consumed + overage` and `ceiling = reserved_consumed + unused`; holds fall to zero only at settlement. Unknown or missing usage remains unknown and retains the conservative hold.
9. Execution, per-currency money, and the five verification-capacity dimensions are non-fungible. Cross-resource conversion and dimension compensation are forbidden; work/effect/verification creation and claim bind the complete exact cohort.
10. `external_effect.authorize` commits exact active grant-use reservation fact(s), `resource.reservation_created`, and `external_effect.authorized`; it emits no grant-use or resource claim.
11. `external_effect.start` requires the effect class, revalidates it against the retained authorization, and atomically commits matching `authority.grant_used(consumption_point=dispatch_claim)`, `resource.reservation_claimed`, and `external_effect.started` facts before any provider call.
12. For `effect_class=governed_processing_dispatch`, both authorize and start carry exact schema-typed WorkContract, DataUseDecision, DataExposure intent, LedgerCheckpoint, and provider-configuration references; exact purpose, recipient, provider, region, payload, and frontier bindings; and current policy/authority/resource input digests. Each commit independently re-resolves and rechecks currentness. The shapes and digests do not prove that currentness or cross-record equality.
13. `external_effect.cancel` requires the effect class and is legal only from `authorized`; it atomically commits terminal grant-use and resource-reservation release facts plus `external_effect.cancelled_before_dispatch`, emits no use/claim fact, and cannot settle an in-flight effect.
14. At-least-once delivery begins after commit. Projection reducers deduplicate by event ID and reject gaps, reordering, unknown semantic versions, wrong aggregate ownership, and broken hashes.
15. Replaying event zero through position N with the frozen reducer set must reproduce identical axes, resource vectors, and aggregate-head digests.
16. Corrections append version and dependency-invalidation events. No prior bytes or outcomes are overwritten.
17. An upcaster changes only the reader view. It never rewrites retained bytes, event digest, or historical semantic meaning.

## External effects and publication

An external effect follows:

```text
not_intended -> authorized(reservation active) -> started(reservation consumed)
authorized -> cancelled_before_dispatch(reservation terminal)
started -> confirmed_applied | confirmed_not_applied | completion_unknown
completion_unknown -> reconciliation pending/running
reconciliation completed -> confirmed_applied | confirmed_not_applied
reconciliation failed -> failed | manual_review
```

The adapter call happens only after `external_effect.started` commits with a stable provider-key digest and exact dispatch-bound grant consumption. `cancelled_before_dispatch` is not an external observation and never means `confirmed_not_applied`; it proves only that the canonical dispatch claim did not win. `completion_unknown` forces `forbidden_until_reconciled`; blind retry is inadmissible.

Model, tool, data-processing, and paid-compute calls use the distinct `governed_processing_dispatch` effect class, never the ambiguous `message` class. A WorkContract is a bounded control artifact, not dispatch authority. Authorize and start each require the exact typed governance/frontier bindings above and must compare them with the current canonical fold at their own commit. A stale or revoked DataUseDecision produces a rejected CommandReceipt with no reservation, grant-use, effect-authorization/start, or spend cohort. JSON Schema proves only that the fields and typed references are present; reference resolution, digest equality, scope coverage, source/checkpoint ordering, currentness, and authorize-to-start equality remain semantic rules.

Publication is a separate aggregate. Provider application does not prove the approved bytes are visible. `publication.release_settled(to=released)` therefore requires an exact channel observation. The publication sequence is candidate compiled -> request -> human decision -> exact manifest sealed -> publication release started plus external effect started -> effect observation/reconciliation -> publication settlement. Correction or withdrawal is additive and causally invalidates dependent projections.

## Replay acceptance traces

These traces are normative examples; their cross-event predicates still require the semantic validator named below.
The first machine-readable vector is the [invalid-run/no-measurement refusal trace](../tests/architecture-schema/fixtures/research-event-trace-invalid-run.valid.json), backed by individually schema-valid run, measurement, and adjudication events.

| Trace | Ordered facts | Required projection | Forbidden inference |
|---|---|---|---|
| Pre-mission decline | `proposal.submitted`, `proposal.decided(declined)` | proposal declined; no mission aggregate | synthetic mission ID or scientific verdict |
| Broken execution | `attempt.failed`, `run.validity_determined(invalid)`, `measurement.disposition_determined(no_valid_measurement)`, `adjudication.recorded(refused)` | invalid run, no measurement, not adjudicated | null result |
| Verifier disagreement | request, assignment, start, completion, `verification.disputed` | disputed remains visible | confirmed verification or claim eligibility |
| Grant race, use first | `authority.grant_used`, domain fact, then `authority.grant_revoked` | historical use valid; future use denied | retroactive erasure |
| Grant race, revoke first | `authority.grant_revoked`; attempted domain command rejected in receipt | no use/domain event | post-revocation authority |
| Effect dispatch claim wins | `authority.grant_use_reserved`, `external_effect.authorized`, then same-batch `authority.grant_used(dispatch_claim)` + `external_effect.started` | reservation consumed; immutable in-flight effect | release as unused or provider call before claim |
| Effect cancellation wins | reservation + authorized effect, then same-batch `authority.grant_use_reservation_released` + `external_effect.cancelled_before_dispatch` | terminal reservation; no dispatch claim/use | dispatch after terminal release or synthetic not-applied settlement |
| Effect revoke/expiry wins | reservation + authorized effect, then typed `authority.grant_use_reservation_released` in the revoke/expiry cohort | retained but nondispatchable intent until explicit closure; no claim/use | dispatch from a terminal reservation |
| Ambiguous publication | publication/effect started, `external_effect.completion_reported(completion_unknown)`, reconciliation started/completed, channel observation, publication settled | released only after channel observation | timeout equals release or safe blind retry |
| Correction | new adjudication, new claim version, supersession, dependency invalidation, publication correction/withdrawal | old bytes addressable with correction lineage | silent overwrite |
| Incident and learning | incident open/transition plus grounded outcome and candidate facts | response and learning histories remain separate | incident resolution promotes a strategy |
| Rights assertion | `rights_assertion.recorded` | evidence only; data-use authority missing | assertion or possession becomes permission |
| Exposure ambiguity | intent, `data_exposure.observation_recorded(completion_unknown)`, settlement unknown | exposure remains unknown and monotonic | timeout or missing receipt becomes zero/not exposed |
| Deletion anti-resurrection | `data_use.revoked`, `deletion.case_closed(completed)`, asset tombstone | permission revoked; data tombstoned; bytes unavailable | old digest, backup, or verification resurrects access |
| Stale-grant restore | restore case plus incomplete current-policy frontier and quarantine decision | isolated/quarantined | historical grant or credential re-enabled |
| Missing artifact restore | restore report records missing C2 bytes; recovery remains quarantined | exact bytes unavailable; dependent claims blocked | metadata or regeneration proves recovery |
| Fork detection | `ledger.fork_detected`, quarantine | no canonical branch selected | wall-clock/last-write-wins branch selection |
| Restore report | passing report without recovery decision | service remains isolated | report, recommendation, or signature reopens service |
| Stale processing dispatch | WorkContract + exposure intent, then data-use revocation and rejected `external_effect.authorize` receipt | no reservation/use/effect/spend cohort; dispatch refused | WorkContract alone, historical decision, or intent sends bytes or spends |
| [Claimed reservation survives crash](../tests/architecture-schema/fixtures/research-event-trace-resource-claimed-crash-holds.valid.json) | reservation create + exact start/claim, then process loss before usage observation | claimed; full ceiling held; actual usage unknown | crash releases capacity or proves zero use |
| [Pre-claim release](../tests/architecture-schema/fixtures/research-event-trace-resource-preclaim-release.valid.json) | reservation create, then exact cancellation/revocation cohort + release | released; zero hold; no actual-use claim | released reservation can later be claimed |
| [Pre-claim expiry](../tests/architecture-schema/fixtures/research-event-trace-resource-preclaim-expiry.valid.json) | reservation create, controlled-time expiry wins before start | expired; zero hold; no claim | expiry races past a committed claim |
| [Verification-capacity settlement](../tests/architecture-schema/fixtures/research-event-trace-verification-resource-settlement.valid.json) | verification assignment reserve + verification start claim + observed use + settlement | five-dimensional verification capacity reconciled without substitution | compute replaces absent expert/physical/safety capacity |
| [Unavailable usage is not zero](../tests/architecture-schema/fixtures/research-event-trace-resource-unavailable-not-zero.valid.json) | claimed reservation + unavailable meter observation | claimed; full hold; actual usage unavailable | missing measurement becomes zero or permits settlement |

## Compatibility policy

- The envelope schema version governs storage shape. Event semantic version governs one fact's meaning. Payload schema ID and digest bind its exact contract.
- Patch versions may clarify annotations only. Minor versions may add optional fields that old reducers safely ignore. New required fields, changed enum meaning, changed reducer effect, changed authority, or changed aggregate owner require a new major semantic version.
- Unknown event type, unknown major version, missing schema digest, or unavailable reducer stops canonical replay. It never becomes an ignored event.
- Upcasters are pure, versioned, fixture-tested reader functions. Downcasting canonical state is forbidden.
- Old bytes, digests, command receipt, registry entry, and reducer version remain retained for audit.
- New-command admission uses only the server-activated admitted registry/envelope. Retired commands remain readable for exact historical receipt replay; reserved design vocabulary has no envelope/member/receipt semantics until prospectively activated.
- The JCS profile string is still a draft. Cross-runtime number, timestamp, and digest vectors remain A-008 work; this catalog does not claim they are frozen.

## Rejections and evidence-relevant attempts

Generic limits and a bounded selector precede command-envelope processing. Unknown, reserved, inactive, invalid-member, or otherwise unbindable ingress produces `command_contract_not_admitted` operational/security refusal evidence and no `CommandReceipt` or canonical cohort. Changed bytes under a settled command ID likewise create no second receipt; exact historical retry returns the existing receipt under its retained contract.

Once an exact admitted member and all required envelope bindings resolve, payload-schema-invalid, stale, unauthorized, or illegal commands may produce a rejected receipt and no scientific event. `unknown_command` is not a legal receipt result. A separate domain command records an attempted action only when the attempt is itself consequential evidence: protocol exposure, suspected credential or command-ID abuse, a high-risk revoked-grant attempt, verifier disagreement, known-bad failure, evidence invalidation, or an ambiguous external effect. The event records an observation, never guessed intent.

## Structural audit and remaining gaps

The isolated architecture audit currently finds:

- 121 unique design discriminators in the current red-team envelope, each with one branch binding semantic version, payload-schema ID, stream family, and target aggregate; this count is not an admitted surface;
- 135 unique event discriminators, each with one payload branch, one payload-schema ID, one stream-family rule, one aggregate owner, and one named reducer in this catalog;
- no command or event discriminator missing from this catalog;
- 61 schema-valid event fixtures and 16 schema-valid replay traces, included within 166 direct `ResearchEvent`/`ResearchEventTrace` manifest cases and covering pre-mission, run-invalid, no-valid-measurement, adjudication-refusal, grant reservation/dispatch/cancel, verifier-dispute, publication, all 32 data/recovery branches, governed-processing refusal, and the typed local-attempt/resource lifecycle;
- adversarial rejection of rights assertion as permission, authorized use without exact scope, unknown-exposure laundering, completed deletion with residual copies, hold-as-access-authority, checkpoint seal without verification evidence, backup-axis aliasing, restore report as reopen authority, failed recovery quorum without limitation, wall-clock fork choice, new epoch without constitutional selection, and open recovery scope without a complete security frontier.

This resolves the original structural envelope/vocabulary inventory defects behind A-001 and demonstrates a candidate shape for the missing envelope/receipt portion of A-002:

- pre-mission streams no longer require fake missions;
- aggregate ownership covers every founding axis;
- run validity and measurement disposition are independent facts;
- authority basis is plural and non-recursive;
- grant use, exact reservation, typed reservation termination, activation, exhaustion, expiry, and revocation are replayable;
- blocker, verification dispute, claims, publication settlement, external effects, incidents, and learning have explicit producers, payloads, and reducers;
- command ID, exact request digest, actor/target/schema binding, settlement, event batch, stream heads, and exact replay policy have a language-neutral retained shape.

It does **not** close A-001 or A-002 as Gate A blockers yet. The remaining gaps are explicit:

1. Thirteen separate closed payload-schema candidates now exist: the three external-effect candidates plus ten high-consequence data/recovery candidates for data-use decide/revoke, exposure intent, deletion closure, hold issue/release, checkpoint seal, recovery decision, epoch start, and recovery scope change. Envelope/receipt references now require exact snapshot, activation, and contract-record identities, but the immutable registry/activation/record and bounded selector/refusal schemas/bytes do not yet exist, none of the thirteen candidates is enrolled, and the exact dependency-closed Gate A admitted set is not named. The other 108 of 121 design payload contracts do not exist. ADR 0013 therefore requires an admitted-only generated envelope and keeps all non-enrolled names outside executable ingress rather than treating missing contracts as reserved members.
2. Event payload contracts are embedded in the envelope candidate, but the separately addressed payload-schema bytes and accepted registry digests do not yet exist. An instance digest is format-checked, not recomputed or matched to a registry.
3. Reducer ownership is complete as a catalog mapping, but reducer input/output contracts, machine-readable transition tables, reducer versions/digests, and independent replay implementations remain absent.
4. `authority.assignment_recorded` still has two deliberately disjoint producer branches—constitutional root and ordinary assignment. Gate A should split the event or freeze a machine-readable branch registry so “one producer” is literal, not prose.
5. Data-governance and recovery vocabulary coverage is structurally complete for the founding lifecycles, but reference existence, rights-subset reasoning, lineage/deletion fanout, witness/signature verification, frontier completeness, branch selection, and service-scope legality remain semantic checks.
6. The replay-trace schema enforces important terminal combinations and a rejected governed-processing command's zero-effect cohort structurally, but ordinal/position contiguity, event and receipt digest chains, actual fixture-to-step/reference identity, event-cohort completeness, and reducer output equivalence remain semantic checks.
7. JSON Schema cannot establish request/result/receipt/event/checkpoint digest equality, signature validity, registry membership or activation, duplicated record equality, snapshot currentness, canonicalization, batch contiguity, time order, reference existence, source/checkpoint ordering, typed subject truth, authorize/start effect-class equality, binding equality, input currentness, scope coverage, role separation, quorum, grant accounting, legal transition pairs, scientific consequence rules, external truth, or reducer determinism.

Those items require bounded selector/refusal and registry/schema work, runtime-enabled envelope/registry/conforming-handler set-equality validation, historical replay and changed-ID-reuse vectors, two independent semantic-validator and replay implementations, race traces, and canonicalization vectors before Gate A. The current pass closes the explicit data/recovery vocabulary omission; it is strong structural evidence, not proof of an engine and not full A-001/A-002 closure.
