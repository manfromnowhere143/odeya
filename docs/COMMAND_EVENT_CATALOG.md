# Command and Event Catalog

Status: proposed architecture contract, 2026-07-15. This document is non-executable and does not authorize runtime implementation. It defines the registry that must be frozen for Gate A; it also names incompatibilities in the current draft schemas that must be resolved before G2, G6, and G7 can pass.

## Purpose

Odeya changes canonical state only by admitting a versioned command and atomically appending an immutable event batch. A command is a request that may be rejected. An event is a retained fact that already happened. A worker result, workflow callback, model answer, provider receipt, UI action, or clock tick has no direct write path: each must enter through a typed command.

This catalog is the semantic source for future command schemas, event payload schemas, transition reducers, policy rules, idempotency records, recovery tests, and projection fixtures. It is not an API description and does not select a framework.

Related contracts:

- [Architecture](ARCHITECTURE.md)
- [Orthogonal state model](STATE_MODEL.md)
- [Interface contracts](INTERFACE_CONTRACTS.md)
- [Failure model](FAILURE_MODEL.md)
- [Security and authority](SECURITY_AND_AUTHORITY.md)
- [Standards profile](STANDARDS_PROFILE.md)
- [Pre-implementation gate](PRE_IMPLEMENTATION_GATE.md)

## Normative language and notation

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` describe proposed Gate A requirements.

Event notation in the family tables is deliberate:

- `schema:event.name` exists in `research-event.schema.json` version `0.2.0`.
- `required:event.name` is required by the state, authority, or recovery model but is absent from that schema.
- A bracketed batch such as `[a, b]` is committed atomically and in the listed order.
- `none` means a valid no-op or rejection returns a result without adding a scientific fact. Evidence-relevant denials and security events are exceptions and require a named event.

The `required:` names are candidate vocabulary. They do not become canonical until their payload, aggregate owner, state effect, and compatibility policy are accepted.

## Registry record required for every command

Every command version MUST have one immutable registry record containing:

```text
command_type + semantic version
owning stream and aggregate
canonical payload schema ID + digest
allowed actors and execution identities
required authority roles, grants, quorum, and separation constraints
policy action and frozen policy-bundle compatibility range
state admission predicate
referential, artifact, rights, budget, and risk predicates
events emitted for every accepted branch
typed rejection codes and whether rejection itself is evidence-relevant
idempotency scope and canonical request digest rule
external-effect and provider-idempotency class
retry class, retry ceiling, and reconciliation procedure
projection invalidations and dependent aggregates
positive, negative, race, crash, replay, and compatibility fixtures
```

An unregistered command is inadmissible. A registered command whose schema or policy version cannot be resolved fails closed.

## Canonical command envelope

The conceptual envelope in `INTERFACE_CONTRACTS.md` is refined as follows:

```text
command_id
command_type + command_version
target_stream_id + target_aggregate_type + target_aggregate_id
expected_stream_position
actor_principal + authenticated_execution_identity
authority_assignment_refs[]
authority_grant_refs[]
policy_decision_refs[]
correlation_id + causation_id
input_artifact_refs[]
canonical_payload
canonical_request_digest
client_observed_time | null       informational only
```

Multiple authority references are necessary for dual control and cross-role approval. `mission_id` remains a required scope after a mission exists, but cannot replace `target_stream_id` for portfolio and pre-mission proposal commands. `canonical_request_digest` covers the command type/version, target, expected position, actor identity, authority references, input references, and canonical payload. It excludes server-assigned recorded time.

## Universal admission order

The application boundary processes a command in this order:

1. Authenticate the execution identity and establish the controlled recorded time.
2. Resolve the command registry entry and exact schema digest.
3. Canonicalize the request and compute `canonical_request_digest`.
4. Look up `command_id` in its idempotency scope before checking the caller's stale expected position.
5. If the same ID and digest were settled, return the original result. If the same ID has a different digest, reject with `CommandIdReuse` and open a security incident when policy requires.
6. Validate schema, size, media-type, canonical-number, and unknown-field rules.
7. Compare `expected_stream_position` and the aggregate version with canonical heads.
8. Resolve every referenced event, artifact, protocol, manifest, policy decision, assignment, and grant by immutable identity.
9. Verify artifact custody, rights, classification, exposure, and disclosure predicates.
10. Evaluate policy and all authority predicates at the controlled recorded time, including quorum, role separation, scope, remaining uses, resource limits, and revocation.
11. Check budget reservations, risk tier, lease ownership, blockers, and the exact state-transition predicate.
12. Run the pure command decision and event derivation. Model or tool output cannot participate in this function except as an untrusted referenced artifact.
13. Atomically persist the command receipt, grant reservations/uses, event batch, aggregate heads, and transactional outbox.
14. Return the committed stream position and event references. Projection freshness is reported separately.

Schema validation is only step 6. It cannot establish reference existence, authority separation, scientific validity, event ordering, or external settlement.

## Event-batch laws

For an accepted internal state change:

1. The batch has one `commit_id`, one `command_id`, one correlation chain, and a fixed `batch_size`.
2. `batch_index` is zero-based, unique, and contiguous through `batch_size - 1`.
3. Mission or stream sequence positions are contiguous and allocated only at commit.
4. Every event names exactly one owning aggregate; a batch MAY contain events for several aggregates in the same canonical stream.
5. Each event's previous digest points to the immediately preceding canonical event, including earlier events in the same batch.
6. The entire batch commits or none of it commits. Event delivery and projection updates after the outbox remain at-least-once.
7. Event time means one of two things: an internal decision's controlled commit time, or an externally observed time with retained source and uncertainty. Provider-reported time never becomes trusted merely by being recorded.
8. An event records the decision and retained references used at that moment. Later revocation, correction, or invalidation adds events; it never edits the batch.
9. An accepted command that changes canonical state MUST emit at least one event. A successful read, dry validation, duplicate, or genuine no-op MAY emit none.
10. Batch contiguity, referential integrity, digest chaining, grant accounting, time order, and cross-event invariants require semantic validation beyond JSON Schema.

Cross-mission atomic commits are forbidden in the founding design. A portfolio decision that creates a mission uses a retained causal link and an idempotent saga: settle the proposal decision first, then create the mission origin, with explicit recovery if the second command has not yet settled.

## Idempotency and recovery classes

The tables use these recovery classes:

| Class | Meaning | Duplicate and crash rule |
|---|---|---|
| `I` | Pure internal transition | Same command ID/digest returns the original batch. A new command ID reevaluates current state and cannot repeat an illegal edge. |
| `D` | Human or policy decision | The signed decision artifact is immutable. Retry resubmits the same command; changed wording, scope, or evidence requires a new command and usually a new decision. |
| `A` | Artifact/object transition | Bytes are staged, digest-verified, and immutably materialized first. Canonical artifact promotion occurs only in the metadata/event transaction; unregistered objects and missing committed objects are reconciled explicitly. |
| `L` | Lease, attempt, or budget transition | Compare-and-set on stage/work/lease version. Retry never erases an attempt or resource observation; a new execution is a new attempt ID. |
| `X` | External consequential effect | Commit authorization and intent before the call. Use a stable provider key. Timeout becomes `completion_unknown`; no retry until independent reconciliation. |
| `V` | Pure verification/adjudication derivation | Same sealed inputs and rule versions must derive the same event proposal. Changed evidence, evaluator, or rule creates a new run/version. |

A retry with changed payload is never a retry of the same command. Model sampling retries are additional attempts and retain their own identities, costs, and outputs.

## Command families

### 1. Intake, mission contract, and protocol

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `proposal.submit` | Identity/disclosure envelope valid; attachments quarantined; no duplicate proposal version | Authenticated ingress policy; no scientific authority implied | `schema:proposal.submitted` | `I`; same proposal version/digest is a no-op, different bytes require a new version |
| `proposal.decide` | Proposal exists; screening evidence retained; decision branch legal | Human proposal authority; rights/safety decisions separately referenced where relevant | `schema:proposal.decided`; acceptance causally schedules mission origin creation, never in a cross-stream atomic claim | `D`; signed decision is replay-safe, changed rationale is a new decision |
| `proposal.withdraw` | Requester owns withdrawal right; downstream mission consequences resolved | Contributor/owner plus policy; publication authority if already public | `required:proposal.withdrawn` | `D`; repeated withdrawal returns original result |
| `mission.create_origin` | Accepted proposal or operator-authored origin exists; target mission ID unused | Proposal authority and explicit mission owner assignment | `required:mission.origin_recorded` | `I`; saga resumes until mission origin exists exactly once |
| `mission.compile` | Orientation package and method registries resolve; output passes structural and semantic validation | Scoped execution grant; protocol authority is needed to accept, not to run the compiler | `schema:mission.compiled` | `V`; compiler/version/input digest fix the output; failed validation returns a report without advancing phase |
| `protocol.record_exposure` | Exposure is newly observed and scoped to data, role, actor, and time | Data-rights or protocol authority depending source; observation cannot be suppressed by producer | `required:protocol.exposure_recorded` | `I`; exposure history is monotonic and never cleared |
| `protocol.freeze` | Mission compiled and validated; forbidden exposure absent; consequence table, bars, controls, and amendment rules complete | Human protocol authority; safety/data/resource grants referenced but not inherited | `schema:protocol.frozen` | `D`; identical digest is duplicate, changed protocol requires amendment/fork |
| `protocol.amend` | Frozen branch exists; reason and complete exposure history retained; prospective consequence derived | Human protocol authority and every affected authority role | `[schema:protocol.amended, required:dependency.invalidation_recorded]` when dependencies change | `D`; never edits the prior snapshot |
| `protocol.fork` | Existing branch retained; new prospective scope and origin consequence explicit | Human protocol authority | `required:protocol.forked` | `I`; target branch ID and parent digest make creation idempotent |
| `protocol.supersede` | Replacement branch frozen; dependent run/claim effects enumerated | Human protocol authority | `[required:protocol.superseded, required:dependency.invalidation_recorded]` | `D`; supersession cannot delete prior use |
| `mission.advance_phase` | Exact phase entry predicate in `STATE_MODEL.md` passes; required checkpoint promoted; no affected open blocker | Role owning the boundary; pure phase derivation by kernel | `required:mission.phase_advanced` | `V`; stale position conflicts, duplicate returns original edge |

Proposal acceptance means worth testing, not true. Protocol authority can freeze what the experiment means; it cannot grant execution, verification, outcome, or publication authority.

The phase boundary consumes the following retained decisions; it does not mint them:

| Phase edge | Required authority/evidence lineage |
|---|---|
| `intake -> orient` | Proposal decision and origin rights/safety screen |
| `orient -> contract` | Protocol owner accepts orientation completeness; data-rights status resolves every admitted source |
| `contract -> preregister` | Protocol authority accepts the validated mission contract |
| `preregister -> preflight` | Human protocol freeze with recorded exposure state |
| `preflight -> execute` | Active safety, data-rights, resource, and execution grants for the exact run manifest |
| `execute -> verify` | Kernel proves the work graph settled; execution authority does not choose the verifier |
| `verify -> adversarial_review` | Required verification packages settled under the independence contract |
| `adversarial_review -> adjudicate` | Verification authority records disposition of every material finding |
| `adjudicate -> handoff` | Pure consequence rule settles or refuses adjudication; verification lineage is retained |
| `handoff -> learn` | Handoff sealed at an exact ledger position; no scientific authority is inferred |
| `learn -> closed` | `mission.close` separately checks leases, ambiguous effects, handoff, and policy obligations |

### 2. Authority assignments and grant accounting

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `authority.record_assignment` | Signed governing decision names principal, role, scope, conflicts, effective interval, and issuer chain | Founding constitutional authority or an active, delegable parent assignment; never the assignee alone | `required:authority.assignment_recorded` | `D`; assignment version is immutable and narrowing/supersession is additive |
| `authority.issue_grant` | Issuer assignment active; signed policy decision, request digest, subject binding, scope, limits, replay rule, dependencies, and quorum valid | Assigned issuer roles and human approval exactly where the frozen action matrix requires | `schema:authority.granted` after bootstrap semantics are resolved | `D`; grant ID/digest is immutable and cannot widen on retry |
| `authority.observe_expiry` | Controlled time is at/after expiry and no prior expiry observation exists | Kernel clock boundary under pinned time policy | `required:authority.expired` | `I`; admission denies expired grants even if projection delivery lags |
| `authority.revoke` | Grant/assignment active or issued; revocation issuer and reason are in scope | Authorized human/policy issuer under the frozen action matrix | `schema:authority.revoked` | `D`; canonical commit order settles use-versus-revoke races |

The initial root assignment is a reviewed constitutional artifact, not a self-issued grant. Its creation and rotation procedure must be accepted before the first authority command schema can freeze.

Grant use is not a caller-accessible command. Each admitted domain command appends `required:authority.grant_used` for every consumed grant in the same batch as the authorized fact; exhaustion may add `required:authority.exhausted`. Long-lived concurrency is owned by the lease/effect aggregate rather than a free-floating permission reservation. If the database transaction fails, neither the use nor the domain event exists.

### 3. Planning, control, work, and external effects

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `work_graph.compile` | Frozen protocol and registered stage templates resolve; graph is acyclic and outputs cover gates | Scoped execution grant; protocol digest fixes semantics | `required:work_graph.compiled` | `V`; graph digest identifies output |
| `stage.set_readiness` | Readiness edge is legal; required inputs or blocker resolution evidence retained | Kernel derivation under owning stage policy | `required:stage.readiness_changed` | `I`; never changes authorization or mission phase implicitly |
| `stage.authorize` | Stage ready; run manifest immutable; safety/resource/execution/data grants active and compatible | All declared grants; high consequence may require dual control | `schema:stage.authorized` | `D`; grant reservations commit with the event |
| `blocker.open` | Named dependency prevents a legal action; class, scope, evidence, and resolution rule valid | Any permitted detector; security/policy classes trigger their owning authority | `required:blocker.opened` | `I`; same blocker key coalesces only if evidence and requirement match |
| `blocker.resolve` | Blocker open; exact resolution requirement met by retained evidence | Authority owning blocker class; producer cannot self-resolve verification/security blockers | `required:blocker.resolved` | `D`; readiness changes only in a subsequent or same derived batch |
| `blocker.supersede` | Replacement blocker identifies why the prior formulation is obsolete | Same authority as original blocker | `[required:blocker.superseded, required:blocker.opened]` | `D`; prior blocker remains visible |
| `work.lease` | Work ready and authorized; no active writer lease; capability and budget subset valid | Execution grant bound to subject, stage, manifest, and resources | `[schema:work.leased, required:authority.grant_used]` | `L`; one lease ID, compare-and-set owner |
| `work.renew_lease` | Same subject and active lease; heartbeat and observed usage within limits | Existing execution grant; no implicit expansion | `required:work.lease_renewed` | `L`; renewal ID prevents extending twice |
| `work.revoke_lease` | Lease active/stale; revocation reason and authority valid | Execution, safety, or resource authority according to reason; incident policy maps containment to those roles | `required:work.lease_revoked` | `L`; revocation wins over later completion admission |
| `attempt.start` | Active lease; attempt ID unused; environment and input manifest digests resolve | Lease-bound execution grant | `schema:attempt.recorded(status=started)` | `L`; start commits before execution begins |
| `attempt.report` | Reporter matches lease/attempt identity; result manifest staged/promoted as required; status legal | Lease-bound execution identity | `schema:attempt.recorded` | `L`; completion does not promote artifacts or complete a stage |
| `attempt.mark_interrupted` | Worker loss/cancellation observed; no terminal attempt fact exists | Kernel/workflow observation; safety or execution authority when interruption is an incident action | `required:attempt.interrupted` | `L`; a replacement execution uses a new attempt ID |
| `work.complete_lease` | Terminal attempt fact and resource observations retained; no further worker mutation allowed | Kernel derivation under the original execution scope | `required:work.lease_completed` | `L`; completion releases concurrency but never refunds a consumed grant use |
| `resource.observe` | Observation source and unit registered; attempt exists; unknown remains typed unknown | Metering service or verified provider receipt | `schema:resource.observed` | `L`; append corrections, never overwrite estimates or prior readings |
| `budget.mark_exhausted` | Measured/reserved use reaches a frozen limit or becomes unsafe to estimate | Resource policy derivation | `[required:budget.exhausted, required:blocker.opened]` | `L`; more budget requires a new grant, not a retry |
| `effect.authorize` | Consequential effect fully specified; all safety/resource/write/publication grants active | Roles required by action class; R3/R4 use explicit human gates | `required:external_effect.authorized` | `D`; authorization binds exact effect digest and replay policy |
| `effect.start` | Effect authorized; no unresolved prior start; provider idempotency/reconciliation profile exists | Execution grant consuming effect authorization | `required:external_effect.started` | `X`; intent commits before provider invocation |
| `effect.report_result` | Provider response or timeout tied to effect/attempt identity | Adapter may report evidence but cannot choose scientific meaning | One of `required:external_effect.confirmed_applied`, `required:external_effect.confirmed_not_applied`, `required:external_effect.completion_unknown` | `X`; missing receipt means unknown, never not applied |
| `effect.reconcile` | Effect is unknown; independent read capability and evidence retained | Separate reconciliation execution grant; stronger approval if another write may be needed | `required:external_effect.reconciliation_completed` with observed applied/not-applied settlement | `X`; only a settled reconciliation can reopen a safe next action; it does not erase prior ambiguity |
| `stage.complete` | Required outputs promoted; attempts settled; no ambiguous effect; gate and authority predicates pass | Kernel derivation plus owning stage authority where specified | `[required:stage.readiness_changed(to=completed), required:mission.phase_advanced]` when phase boundary is reached | `V`; completion is immutable and later invalidation is additive |

Workflow history schedules these commands but is not the scientific ledger. A lease authorizes a bounded attempt; it is not a data-rights, scientific-verdict, or publication grant.

### 4. Evidence, measurement, verification, and review

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `artifact.record` | Staged bytes or lawful metadata tombstone exists; origin, media type, rights, and declared digest present | Execution/data-rights grants appropriate to custody | `schema:artifact.recorded` | `A`; a failed metadata commit leaves an orphan object for reconciliation |
| `artifact.validate` | Recorded artifact available; exact validator set and known-bad suite resolve | Execution or verification role according to artifact purpose | `required:artifact.validated` or `required:artifact.validation_failed` | `A`; validator change creates a new report, not a changed past verdict |
| `artifact.promote` | Streamed digest matches; validation and rights gates pass; immutable target condition succeeds | Execution plus data-rights/safety gates; verifier artifacts use verification authority | `schema:artifact.promoted` | `A`; digest-keyed conditional creation, then one metadata/event/outbox transaction |
| `artifact.quarantine` | Threat, rights, integrity, or provenance reason retained | Security, data-rights, or evidence policy | `schema:artifact.recorded(state=quarantined)` pending a dedicated event | `A`; dependent use fails closed immediately |
| `artifact.mark_corrupt` | Integrity check fails against committed identity | Evidence/security authority or deterministic check | `[required:artifact.corrupt, required:dependency.invalidation_recorded]` | `A`; bytes are never silently replaced under the same identity |
| `artifact.mark_unavailable` | Referenced bytes cannot be retrieved or lawfully accessed | Storage/data-rights observation | `[required:artifact.unavailable, required:blocker.opened]` | `A`; reacquisition is a new custody fact |
| `artifact.tombstone` | Lawful removal decision retained; identity/provenance retention allowed | Data-rights authority, with publication/correction review where affected | `[required:artifact.tombstoned, required:dependency.invalidation_recorded]` | `D`; tombstone is irreversible absent a new lawful artifact identity |
| `metric.record_observation` | Frozen metric method, population, denominator, unit, missingness, and run references resolve | Verifier or registered measurement process; producer output alone is candidate evidence | `schema:metric.observed` | `V`; corrected computation is a new observation/version |
| `falsifier.adjudicate` | Frozen falsifier and known-bad control evaluated from promoted evidence | Verification authority or pure registered adjudicator | `schema:falsifier.adjudicated` | `V`; unmeasured and inconclusive remain distinct |
| `run.determine_validity` | Protocol, attempt, artifact, leakage, control, and environment evidence complete | Independent verification plus pure validity rule | `required:run.validity_determined` | `V`; invalidity blocks scientific adjudication, not evidence retention |
| `run.record_measurement_status` | Measurement acceptance rule evaluated independently of hypothesis result | Registered measurement/verifier identity | `required:run.measurement_status_recorded` | `V`; `no_valid_measurement` cannot become a null result |
| `verification.request` | Frozen protocol, promoted evidence manifest, independence requirement, and sealed exposure policy exist | Kernel/mission owner may request; requester cannot choose itself as verifier | `schema:verification.requested` | `I`; request digest fixes the assignment constraints |
| `verification.assign` | Candidate satisfies every required independence and conflict predicate | Verification authority separate from producer | `required:verification.assigned` | `D`; reassignment preserves earlier exposure and conflicts |
| `verification.start` | Assignment active; verifier context manifest honors exposure policy | Assigned verifier execution grant | `required:verification.started` | `L`; retry is a new verification attempt, not erased work |
| `verification.complete` | Verification package promoted; known-bad controls and dimension results present | Assigned verifier submits; kernel validates requirement vector | `schema:verification.completed` | `V`; same sealed inputs/rule version reproduce the result |
| `verification.dispute` | Material producer-verifier or verifier-verifier mismatch retained | Verification authority or affected party through controlled challenge | `required:verification.disputed` | `D`; majority vote cannot close it |
| `verification.invalidate` | Contamination, conflict, evaluator defect, or missing evidence established | Independent verification/security authority | `[required:verification.invalidated, required:dependency.invalidation_recorded]` | `D`; prior package remains addressable |
| `replication.record` | New diagnostic data/measurement and required organizational independence established | Independent replication authority | `required:replication.recorded` | `V`; same-evidence replay is inadmissible here |
| `transport.record` | Predeclared external context and criterion evaluated | Independent verification/outcome authority as domain requires | `required:transport.recorded` | `V`; failed transfer narrows claims, not source evidence identity |
| `review.record` | Review assignment, exposure, conflicts, report, and finding severity present | Assigned domain/statistical/security/rights/publication reviewer | `schema:review.recorded` | `D`; changed report is a new review version |

Integrity, reproducibility, method validity, replication, and transport are separate dimensions. No command may collapse them into one verifier score.

### 5. Claims, correction, and publication

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `claim.propose` | Prospective proposition, type, scope, estimand/consequence rule, falsifiers, and exposure state are typed and within the mission claim surface | Proposal capability only; generator has no verdict authority | `schema:claim.proposed` after payload aligns to `ClaimProposal` | `I`; same proposal digest is duplicate, changed wording/scope is a new proposal version |
| `adjudication.determine` | Run validity, measurement disposition, frozen consequence rule, metrics, falsifiers, verifier packages, reviews, and blockers settle | Pure adjudicator using retained facts; never generator self-verdict | `schema:claim.adjudicated` after renaming/alignment to `Adjudication`; refusal may open or reference a blocker | `V`; rule/input changes create a new adjudication object |
| `claim.compile_version` | Proposal and adjudication resolve; every required verification profile and evidence edge settles; compiler rule/version fixed | Pure claim compiler; human/domain review only where mission requires it | `required:claim.version_compiled` with eligible or ineligible projection | `V`; immutable version bytes and ledger position identify result |
| `claim.correct` | New evidence identifies affected prior version and all known dependencies; replacement adjudication/version is complete | Verification/protocol authority for decision inputs; outcome authority for external-settlement changes; publication authority only for release effects | `[schema:claim.corrected, required:claim.version_compiled, required:claim.superseded, required:dependency.invalidation_recorded]` | `D`; correction is a new version, never an in-place edit |
| `claim.retract` | Claim is no longer supportable or lawful; reason, replacement/retraction-notice version, and dependency set retained | Verification/protocol or rights authority by reason; publication authority only for public effects | `[schema:claim.retracted, required:claim.version_compiled, required:dependency.invalidation_recorded]` | `D`; retraction notice remains at least as visible as prior release |
| `publication.compile_candidate` | Exact eligible claim versions, disclosure projection, rights/safety wording, citations, limitations, and correction endpoint resolve | Scoped publication preparation; no release authority yet | `required:publication.candidate_compiled` | `V`; candidate digest fixes exact proposed disclosure |
| `release.request` | Candidate digest exists; requestor and intended channels/scope recorded | Authenticated request capability; not publication approval | `schema:release.requested` after its payload is split from decision | `I`; duplicate request returns existing aggregate |
| `release.decide` | Candidate, claim state, rights, safety, embargo, contributor, wording, and channel risks evaluated | Human publication authority; dual control when policy requires | `schema:release.decided` | `D`; authorization binds the exact candidate/manifest digest |
| `publication.seal` | Release authorized; final projection exactly matches approved candidate; grant unused and active | Human publication authority | `schema:publication.sealed` | `D`; any byte change requires a new manifest and decision |
| `publication.start_release` | Manifest sealed; effect authorization active; channel idempotency/reconciliation profile exists | Single-use publication grant plus execution grant | `[required:external_effect.started, required:publication.release_started]` | `X`; commit before sending bytes |
| `publication.report_release` | Receipt or timeout tied to manifest, channel, and effect ID | Channel adapter reports only | One of `required:publication.released`, `required:publication.release_completion_unknown` | `X`; timeout forbids blind retry |
| `publication.reconcile_release` | Release completion unknown; independent channel observation retained | Publication/reconciliation authority | `[required:external_effect.reconciliation_completed, required:publication.release_reconciliation_completed]` | `X`; observed applied -> released, not applied -> sealed; reconciliation remains a separate process fact |
| `publication.withdraw` | Released manifest exists; correction/safety/rights reason retained; channel effect authorized | Human publication authority | `schema:publication.withdrawn` plus external-effect events | `X`; channel timeout remains unknown and visible |
| `publication.correct` | Replacement publication references superseded manifest and exact claim correction | Human publication authority | `[required:publication.corrected, required:dependency.invalidation_recorded]` plus release effect events | `X`; old projection remains addressable with correction banner |

Claim proposal, adjudication, claim-version eligibility, release request, release authorization, manifest sealing, channel intent, and observed release are distinct facts. None implies the next.

### 6. Mission control, incidents, handoff, and closure

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `mission.pause` | Mission open; reason, scope, and active-work handling declared | Execution, safety, or resource authority according to the stop reason | `required:mission.control_changed(to=paused)` plus lease/effect actions as needed | `D`; pause does not change scientific phase |
| `mission.quarantine` | Security/evidence condition requires containment | Safety authority or deterministic critical detector under a frozen incident policy | `[required:mission.control_changed(to=quarantined), required:incident.opened]` | `D`; no automatic resume |
| `mission.resume` | Pause/quarantine resolution evidence complete; grants and leases re-evaluated | Authority that owns the stop reason | `required:mission.control_changed(to=open)` | `D`; creates new leases, never resurrects stale ones |
| `incident.open` | Detection report identifies affected scope and containment requirement | Any trusted detector may submit; policy determines immediate controls | `schema:incident.recorded` pending typed lifecycle events | `I`; duplicate detector report links to the same incident only by exact key |
| `incident.transition` | Legal incident edge with evidence and accountable responder | Safety plus execution authority as required by the incident policy | One of `required:incident.contained`, `required:incident.investigating`, `required:incident.resolved`, `required:incident.superseded` | `D`; closure cannot erase affected-state consequences |
| `handoff.record` | Factual state generated at an exact ledger position; leases, blockers, effects, revisions, and next legal actions included | Kernel derivation; operator signs where transfer occurs | `schema:handoff.recorded` | `V`; stale handoff remains valid only for its named position |
| `mission.close` | Handoff sealed; no active lease; no unresolved ambiguous effect; closure dependencies enumerated | Mission owner and any authority required by unresolved policy | `schema:mission.closed` | `D`; close is not a scientific verdict |

### 7. Grounded learning and controlled promotion

| Command | Admission predicate | Authority | Committed event batch | Recovery |
|---|---|---|---|---|
| `grounded_outcome.record` | External outcome identity, observation method, time, applicability, uncertainty, and evidence retained | Outcome authority; instrument/service may observe but not broaden meaning | `schema:grounded_outcome.recorded` | `V`; later observations append versions/counterevidence |
| `strategy.propose_candidate` | Grounded observations, affected component, scope, regression fixture, and cost/risk are named | Learning lab proposal only; no production authority | `schema:strategy_candidate.recorded` | `I`; digest identifies candidate |
| `strategy.authorize_shadow` | Offline gates pass; no production writes/credentials; fixed evaluator and budget | Evaluation/resource authority | `required:strategy.shadow_authorized` | `D`; authorization is bounded and expiring |
| `strategy.record_shadow` | Held-out replay package and all negative fixtures settle | Independent evaluator | `required:strategy.shadow_recorded` | `V`; evaluator/version changes create a new result |
| `strategy.authorize_canary` | Shadow evidence accepted; rollback, blast radius, and monitoring frozen | Human safety/resource/production authority | `required:strategy.canary_authorized` | `D`; no implicit widening |
| `strategy.decide_promotion` | Independent review, canary outcome, regression suite, and rollback readiness complete | Human protocol, safety, resource, and execution quorum as required; all separated from the candidate generator | `schema:strategy.promoted` for promotion; `required:strategy.rejected` otherwise | `D`; decision binds exact strategy digest |
| `strategy.rollback` | Regression, safety, validity, or operational trigger fires | Human or preauthorized deterministic kill policy | `required:strategy.rolled_back` | `D`; rollback does not delete learning evidence |

Learning commands cannot edit production prompts, tools, schemas, policy, retrieval, or code directly. They can only create candidates and bounded promotion decisions.

### Current event type with no admissible producer

`schema:stage.transitioned` has no command in this catalog. Its payload collapses mission phase, stage readiness, authorization, lease, and attempt execution into one state. Admitting it would violate the orthogonal state model. It must be replaced by axis-specific facts or given a narrower, non-conflicting meaning before Gate A.

## External-effect protocol

No database transaction can make a provider write, physical action, payment, message, repository mutation, or public release exactly once. Every such action uses this state machine:

```text
not_intended
  -> authorized                 internal event committed
  -> started                    intent + stable provider key committed
  -> confirmed_applied          provider receipt independently attributable
  -> confirmed_not_applied      authoritative negative observation
  -> completion_unknown         timeout or ambiguous response
       -> reconciliation process
       -> confirmed_applied | confirmed_not_applied
```

The adapter call occurs only after `started` commits. If the process dies before the call, reconciliation checks the provider using the stable key before another call. If it dies after the call but before reporting, the same rule applies. A provider without idempotency and without authoritative reconciliation cannot receive automatic retry authority.

Publication uses this protocol but also maintains its own release aggregate because a provider write receipt does not prove the right bytes are public, correctly visible, indexed, or withdrawable.

## Artifact promotion transaction

Artifact commands follow the cross-store rule from `STANDARDS_PROFILE.md`:

```text
stage bytes
  -> stream-verify digest and declared format
  -> conditional immutable byte materialization
  -> one database transaction:
       command receipt
       artifact-promotion event + metadata
       grant reservation/use
       domain event batch
       aggregate heads/reducer state
       outbox
  -> asynchronous projection delivery
  -> orphan/missing-object reconciliation
```

An object materialized before a failed database commit is an unregistered orphan, not promoted evidence. Promotion metadata committed for missing bytes makes the artifact unavailable/corrupt and blocks dependent claims. Odeya makes no distributed-atomicity claim.

## Rejection semantics

Ordinary malformed, stale, unauthorized, or illegal-transition commands return a typed rejection and no scientific event. The command receipt MAY be retained in a security/audit plane under its own access and retention policy.

An immutable domain event is required when the attempted action is itself consequential evidence, including:

- policy or safety denial that opens a mission blocker;
- suspected command-ID reuse, credential misuse, injection, or authority escalation;
- attempted use of revoked or exhausted high-consequence authority;
- an ambiguous external effect;
- verifier disagreement or known-bad gate failure;
- protocol exposure, leakage, or evidence invalidation.

The event must describe the observed fact and retained evidence, not speculate about intent.

## Authority rules across commands

1. `actor` identifies who submitted the command. It is not proof of authority.
2. An assignment says a principal may hold a role. A grant authorizes a bounded action. A grant-use record proves a particular admission consumed or reserved that permission.
3. Every grant is checked against command type/version, mission/stream, aggregate, stage, protocol and manifest digests, capability, data class, risk tier, resource, purpose, time, use count, concurrency, delegation, and forbidden role overlap.
4. Grant reservations and event batches commit together. A crash cannot consume permission without a retained decision or commit a consequential event without consuming permission.
5. Revocation races are resolved by canonical commit order. A use committed before revocation remains historical; a command admitted after revocation fails.
6. Generator identity cannot issue or consume verification, outcome, or publication authority for its own output.
7. Policy availability is required for consequential admission. Cached decisions are usable only within their signed scope, version, expiry, and revocation policy.
8. Human approval is required where risk policy says so; it is not assumed for every low-risk mechanical grant. The exact human-only matrix must be frozen separately from schema syntax.

## Coverage required before Gate A acceptance

For every command branch and event type, the architecture candidate must provide:

### Contract coverage

- command, payload, event, and result schemas with exact IDs, versions, digests, format checking, and closed unknown-field behavior;
- one owning stream/aggregate and a complete field-to-provenance map;
- a state predicate and pure reducer law;
- an authority/policy row including quorum and separation;
- typed rejection and retry classifications;
- event upcast/downcast policy or an explicit refusal to downcast.

### Fixture coverage

- minimum valid command and event batch;
- every legal branch and transition edge;
- every required field missing, wrong type, boundary value, and forbidden extra field;
- stale position, duplicate same digest, duplicate changed digest, and concurrent owner cases;
- missing, expired, revoked, exhausted, wrong-purpose, wrong-risk, wrong-protocol, and overlapping-role grants;
- missing/corrupt/quarantined/rights-blocked artifacts;
- known-bad evidence that each consequential gate must reject;
- null, invalid, no-valid-measurement, blocked, disagreement, correction, and withdrawal paths;
- canonicalization and hash-chain vectors across at least two independent implementations before product commitment.

### Crash and race coverage

For each commit boundary, enumerate retained state and next legal command after process death:

- before and after command receipt lookup;
- before and after grant reservation;
- before and after event/outbox commit;
- before and after byte materialization and the separate canonical artifact-promotion commit;
- before and after lease acquisition, renewal, expiry, revocation, and attempt completion;
- before and after external-effect intent, call, receipt, and reconciliation;
- before and after publication authorization, seal, release, correction, and withdrawal.

The bounded model must cover the ten races named in `STATE_MODEL.md`. Every counterexample becomes a transition fixture.

### Replay and projection coverage

- rebuilding from event zero yields the same canonical aggregate axes at the same stream position;
- duplicate and reordered delivery does not change a projection twice;
- a projector discloses its exact source position and cannot invent freshness;
- corrections and invalidations reach every registered dependent projection;
- unknown, unmeasured, unavailable, withheld, stale, and zero remain distinguishable;
- old event bytes remain verifiable after an upcaster or reader changes.

Gate A cannot mark this catalog complete while any required command lacks a schema/event mapping, any event lacks a producer and reducer, or any critical transition relies on prose-only authority or recovery behavior.

## Blocking reconciliation findings

These are contradictions or omissions in the current drafts, not accepted design decisions:

1. **Pre-mission stream paradox.** `research-event.schema.json` requires `mission_id` for `proposal.submitted`, but a proposal precedes mission creation and may be declined. The envelope needs a general stream ID and an optional mission scope, or a separately typed portfolio/proposal event envelope.
2. **State-axis collapse.** `STATE_MODEL.md` separates mission phase, stage readiness, authorization, lease, and attempt execution. The current `stage.transitioned` payload instead uses one state enum containing `authorized`, `running`, `interrupted`, `blocked`, and `completed`, and has no `ready`. This would recreate the forbidden single-status model.
3. **Attempt mismatch.** The state model includes `running` and `interrupted`; the event payload uses `started` and omits `interrupted`. Exact transition facts and projection mapping are therefore incomplete.
4. **Missing aggregate owners.** The event envelope has no aggregate type for blocker, run/measurement, metric, falsifier, external effect, review, replication, transport, handoff, resource budget, or work graph even though several are canonical objects or required state axes.
5. **Authority bootstrap and plurality.** Every event requires one non-null `authority_ref`, including `authority.granted`; its meaning is undefined and can recurse unless it points to a separately modeled assignment/decision. The command envelope documents one grant while the event has multiple grant-use references and dual control requires several grants.
6. **Authority acceptance gap.** Mission, event, and grant candidates now name the same nine roles and the event envelope no longer forces all grant/revoke actors to be human. The proposed root bootstrap, human-only action matrix, service-ceiling rule, quorum, delegation, and overlap semantics in `AUTHORITY_MATRIX.md` still require semantic traces, independent review, and operator acceptance.
7. **Incomplete grant lifecycle.** Grant state is said to derive from issue, use, expiry, and revocation, but the event enum has only grant and revoke. There is no grant-use/reservation/exhaustion fact. Time-derived expiry also requires an explicit `as_of` value or expiry observation so a projection is not claimed to derive from ledger position alone.
8. **No blocker lifecycle events.** `blocker.schema.json` and the state model require open, resolve, and supersede facts, but none exist in the event catalog and `blocker` is not an aggregate type.
9. **Verification mismatch.** The verification object permits `disputed`, exposes detailed independence, and allows several runs, while the event catalog has only request/complete and its completion verdict omits `disputed`. Assignment, start, invalidation, disagreement, replication, and transport facts are missing.
10. **Publication circularity and incomplete settlement.** The shared release payload requires a non-null `publication_grant_id` even for `release.requested`, while publication grants require a publication-manifest digest and sealing follows authorization. Request and decision need different payloads. There are also no release-started, released, completion-unknown, reconciliation-completed, corrected, or channel-effect events, so the specified release state machine cannot be replayed safely.
11. **Artifact custody gaps.** Current events can record, quarantine, or promote, but cannot represent validated, corrupt, unavailable, or tombstoned states from `STATE_MODEL.md`. The shared artifact payload also requires a validation report for initial recording and quarantine, even though those facts may precede validation; the report's meaning is therefore ambiguous.
12. **Run/scientific admissibility gaps.** There are no canonical validity or measurement-status events. Without them, `null_result` versus `no_valid_measurement` is a prose invariant rather than replayable state.
13. **Claim lifecycle gaps.** The current object model separates proposal, adjudication, immutable claim version, revision edges, and publication, while current claim events cover only propose, adjudicate, correct, and retract through one legacy payload. Version compilation, eligibility, supersession, dependency invalidation, and object-specific payloads are missing.
14. **External-effect gap.** The state and failure models require authorized, started, applied, not-applied, completion-unknown, and reconciliation-process facts. None exist in the current event enum, making safe recovery from ambiguous writes impossible to express.
15. **Command-receipt gap.** Events retain `command_id` but not the canonical request digest or original result. Exact duplicate versus malicious/accidental command-ID reuse therefore requires a separate immutable command receipt contract that does not yet exist.
16. **Semantic validation gap.** JSON Schema cannot enforce batch contiguity, sequence allocation, digest chain, time ordering, referenced existence, grant quorum/use, independence, or reducer legality. Those validators and adversarial traces remain Gate A work.
17. **Learning-event aliasing.** `grounded_outcome.recorded`, `strategy_candidate.recorded`, and `strategy.promoted` share one payload schema without conditions tying event type to `record_type` and `promotion_state`. A syntactically valid `strategy.promoted` event can currently carry a grounded-outcome record or a rejected promotion state.
18. **Known-bad ambiguity.** The falsifier payload uses `known_bad_passed`, which can mean either that the gate correctly passed its negative-control test or that the deliberately broken object passed through the gate. The field must be renamed or represented as expected/observed verdicts before it can settle eligibility.
Until these findings are resolved, `research-event.schema.json` is a useful adversarial prototype, not the frozen canonical event model.

## Findings closed during this review

- **Event discriminator composition:** typed payload branches now form the root `oneOf`; cross-cutting guards are in `allOf`. Valid proposal and human release-decision fixtures pass, and wrong-actor/payload fixtures fail.
- **Format assertion:** the isolated architecture validator pins `jsonschema[format]` and `rfc3339-validator`, verifies dependency versions, and includes malformed-date-time adversarial cases. This closes structural format assertion only; relational time ordering remains a semantic blocker under `SEMANTIC_VALIDATION.md`.

## Freeze criteria for this catalog

This catalog is eligible for acceptance only when:

- every `required:` event is either added with a complete contract or deliberately removed with a proved replacement;
- every existing `schema:` event maps to exactly one fact meaning and one reducer effect;
- proposal/portfolio stream ownership is resolved without fake mission identities;
- orthogonal state axes remain orthogonal in payloads and projections;
- the authority bootstrap, grant-use transaction, and time semantics are explicit;
- the external-effect and publication crash matrix has no blind-retry path;
- command/event schemas and semantic fixtures reject attempts to turn invalid, missing, blocked, interrupted, or ambiguous evidence into a scientific or public success;
- the operator accepts the exact immutable architecture candidate.

Acceptance freezes semantics for the first bounded slice. It does not claim the engine exists, that faults have been injected, or that Odeya has demonstrated autonomous science.
