# First-Slice Admission Closure Plan

Status: superseded pre-resolution architecture-evidence hypothesis, retained for
audit, 2026-07-16. C1-C8 choices and recomputed candidate counts now live in
[`FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md`](FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md)
and its machine companion. This document remains the evidence of why the former
44/77/52/23 working hypothesis was refused; it is not a command registry,
RegistryActivation, EngineContractRoot, runtime surface, canonical mission
trace, or Gate A acceptance record.

## Verdict

Do **not** freeze, instantiate, or activate a first-slice command registry yet.

Only the 121-name design vocabulary is exact. The remaining numbers below are a
working classification retained so disputed assumptions stay auditable; none is
a frozen admission cardinality:

| Item | Working count | Count semantics / current closure |
|---|---:|---|
| Design-vocabulary command discriminators inspected | 121 | all remain `not_contract_admitted` |
| Provisionally required command hypotheses | 44 | may grow, shrink, or change after C1 and C5-C8; 0 immutable command-contract records exist |
| Provisionally outside command hypotheses | 77 | conditional on C5/C8 closure; all remain non-executable vocabulary |
| Closed payload candidates inside the provisional 44 | 1 | `data_use.decide`; candidate only, not enrolled; membership is provisional |
| Missing payload contracts inside the provisional 44 | 43 | working gap, not a final cardinality |
| Current primary-event name union | 43 | derived from the disputed 44-command classification |
| Current kernel-cohort event-name union | 9 | contains unresolved cohort alternatives |
| Current event conflict-union | 52 | upper-bound union across mutually exclusive C1 branches under the current scope, not an exact required set |
| Provisional aggregate/state/reducer rows | 23 | C5/C7/C8 can change the families; no real first-slice members exist |
| Provisional owner modules | 10 | C5/C8 can add execution/recovery ownership; no runtime evidence |
| Known blocking conflicts | 8 | C1-C8 must close before any count can freeze |

The hypothesis is neither dependency-bounded nor dependency-complete. In
particular, it omits the machine cohort that makes local bytes visible to an
isolated analyzer, treats multi-grant use as singular, contradicts the catalog's
reproducibility reducer ownership, unions incompatible resource event algebras,
and fails to bind the separately admitted recovery/checkpoint/activation
prerequisite. Publication, external effects, learning, incidents, deletion, and
legal hold remain terminally outside; execution and recovery may stay outside
only after C5 and C8 prove legal external dependencies.

## Closure rule

A command is inside only when at least one of these statements is true:

1. it originates or advances the bounded proposal/mission used to retain the
   proof-mission facts;
2. it creates the assignments or bounded grants required for command admission;
3. it establishes exact asset identity, rights, use, retention, transformation,
   or custody for source and derived bytes;
4. it records protocol exposure/freeze/integrity, resource evidence, scientific
   validity, measurement, metric, or falsifier state;
5. it records verification, reproducibility, dispute, review, or invalidation;
6. it records blocked/refused adjudication or bounded claim correction and
   dependency invalidation; or
7. it is a kernel-produced companion fact without which one included command
   cohort would be incomplete; or
8. it establishes the lease/materialization/sandbox/reservation/execution facts
   required before an offline analyzer can see admitted bytes, unless a reviewed
   specialized verifier-execution cohort proves those facts without importing
   the general work scheduler.

An item stays outside when the offline slice cannot reach it without violating
its own terminal boundary: no provider/model call, network, cloud job, external
write, simulator launch, training, physical action, publication, or strategy
promotion. Outside does not mean unnecessary globally; it means unavailable to
this prospective registry version.

This is a representational gap hypothesis, not closure. It does not authorize a
general worker scheduler. The mission phase contract must bind the specialized
offline fixture profile and its retained outputs; it may not silently treat an
absent work graph, lease, materialization intent, sandbox capability, reservation,
or execution record as settled. C5 must decide whether those facts are supplied
by a specialized verifier-execution cohort or by expanding into the general
work/attempt family. Either decision requires recomputing the working counts.

## Non-negotiable scope, cohort, ownership, and prerequisite conflicts

These are admission refusals, not documentation tasks.

### C1 — resource observation has two incompatible event algebras

The catalog maps `resource.record_observation` to `resource.observed`. The
resource-accounting law instead says retained meter/provider/operator evidence
is kernel-recorded as `resource.usage_observed`, and the ResourceLedger prose
calls only reservation-created/claimed/released/expired, usage-observed, and
reservation-settled its six closed events. An exact command alternative cannot
currently prove whether it emits:

```text
resource.observed
resource.observed + resource.usage_observed
resource.usage_observed
resource.usage_observed + resource.reservation_settled
```

The owner must choose one event algebra, one canonical reducer input set, and
one observation-to-settlement derivation. No registry record may preserve both
as independent resource truth unless their non-overlapping meanings and cohort
rule are explicit.

### C2 — correction atomicity conflicts with sole-producer ownership

Correction/replay law requires claim supersession and dependency invalidation
to be one complete correction cohort. The catalog assigns
`claim.superseded` solely to `claim.supersede` and
`dependency.invalidation_recorded` solely to
`dependency.record_invalidation`. One accepted command cannot presently emit
the required two-aggregate cohort without violating one of those producer
claims; two sequential commands cannot provide atomicity.

The resolution must either make one correction command the explicit producer
of both events, introduce an admitted transaction-coordinator command with
legal producer ownership, or replace atomicity with a formally reviewed fence
that makes the intermediate state ineligible everywhere. Merely documenting a
recommended second command is insufficient.

### C3 — invalid-run settlement conflicts with split command producers

The invalid Telos fixtures require the inseparable consequence
`run.validity_determined(invalid)` plus
`measurement.disposition_determined(no_valid_measurement)`; the reducer contract
also names validity plus measurement disposition as a cohort when inseparable.
The catalog assigns those events to two different commands and aggregates.

The contract must define an atomic producer/cohort or a fail-closed intermediate
state that can never compile a metric, null, adjudication, claim, or projection.
Until then an invalid run can be observed without its mandatory no-measurement
consequence.

### C4 — authority and reservation terminality is under-specified

Bootstrap cannot self-grant, grant maintenance cannot require the target grant
to authorize its own expiry/revocation, and an ordinary bounded command must
atomically retain `authority.grant_used` with its domain fact. Verification
assignment/start additionally creates and claims a resource reservation. The
current design does not yet fix:

- which authority-maintenance commands use assignment-only authority rather
  than recursive bounded grants;
- when final use emits `authority.grant_exhausted`;
- which accepted command produces pre-claim `resource.reservation_released` or
  controlled-time `resource.reservation_expired`;
- how revocation/expiry races with verification start; and
- which exact observation set permits `resource.reservation_settled` after a
  claim.

Every legal branch needs one ordered, finite event alternative. A crash,
timeout, missing callback, or expired clock window cannot release a claimed
ceiling or convert unknown usage to zero.

### C5 — local execution/materialization has no admitted producer cohort

The fixed fixture is not merely a static representation: it runs Sentinel
analyzers and Telos replay in isolated, network-denied environments. A
`DataUseDecision` and the absence of network egress are insufficient before
bytes become visible to that process. The data-governance path requires an
exposure/materialization intent plus any required safety, resource, and
execution grants; the cognitive execution contract additionally requires an
exact worker lease, data-materialization intent, sandbox capability, and
resource reservation.

The current 44-command hypothesis admits none of the general lease/attempt or
materialization-intent commands and names no equivalent specialized execution
record. Resolution must either define a closed verifier-execution cohort with
legal producers for lease-equivalent exclusivity, materialization, sandbox,
reservation/claim, start, completion, and retained observations, or expand the
command/aggregate surface. `DataUseDecision + local + network-denied` is not a
legal execution shortcut.

### C6 — bounded-grant cardinality was incorrectly singular

One `authority.grant_used` payload binds one `grant_id`, while several current
command hypotheses declare `bounded_grants`: `proposal.decide`,
`mission.create_origin`, `mission.advance_phase`, `protocol.freeze`,
`data_use.decide`, `verification.assign`, `verification.start`,
`verification.complete`, and `claim.supersede`. The former `G1/G2` shorthand
could retain only one use and at most one exhaustion event.

Every CommandContractRecord must instead fix a finite ordered grant requirement.
An accepted cohort emits exactly one `authority.grant_used` per consumed grant,
the domain facts, and `authority.grant_exhausted` for exactly the zero-or-more
used grants whose final legal use occurred. No duplicate use/exhaustion, missing
required grant, or exhaustion of an unconsumed grant is legal. The exact event
occurrence alternatives cannot freeze until every command fixes cardinality,
identity roles, order, and final-use predicates.

### C7 — reproducibility reducer ownership contradicts the catalog

The catalog maps `reproducibility.determined` to aggregate `verification` and
reducer family `Reproducibility`. This plan and its inventory instead folded the
event into reducer family `Verification`, while also requiring exactly one
canonical reducer per aggregate.

The owner must choose one coherent model: make `Verification` the sole reducer
and correct the catalog, split reproducibility into a separately owned aggregate,
or define and formally justify a deterministic reducer-composition rule. Until
then the verification row and the 23 reducer/state count are provisional.

### C8 — recovery/checkpoint/activation is an unbound prerequisite

Recovery commands are not proof-mission actions, but that fact alone does not
make them safely excludable. Every first-slice command must resolve through a
separately admitted schema/state/reducer/event/command registry graph, exact
`EngineContractRoot`/C0 bundle, witnessed checkpoint, and current
`RegistryActivation`; recovery/fork/quarantine evidence must prove which ledger
frontier is legal after restart or ambiguity. MAE-003 also requires context-loss
reconstruction from canonical state rather than a handoff packet.

These commands may remain outside only if a machine-bound constitutional and
recovery prerequisite record supplies those exact identities and evidence before
the first mission command. The inventory names this missing dependency
`P0.constitutional-recovery-admission`. If that separately admitted surface
cannot supply the proof, the necessary checkpoint/witness/recovery commands and
aggregates enter scope. The prerequisite is currently absent, so 44/77/23 cannot
freeze.

## Candidate command set

`Payload` means a separate closed command-payload schema whose logical command
URN can be enrolled. An object schema or the generic `CommandEnvelope.payload`
shape does not count. `G(c)` is unresolved command-specific grant-cohort
shorthand blocked by C6; it is not one universal event alternative.
`A` is assignment/authority lifecycle; `P` is protocol-integrity;
`V` is verification/resource; `X` is one of the unresolved conflicts above.

For an accepted command `c`, the required shape is set-valued:

```text
G(c) = { one authority.grant_used(domain_commit, grant_id=g)
         for every g in required_consumed_grants(c) }
       + domain_event_set(c)
       + { one authority.grant_exhausted(grant_id=g)
           for exactly the final-use subset of required_consumed_grants(c) }
```

Every command record must freeze the finite grant cardinality and roles, and the
final registry must order all occurrences by the global aggregate lock/order
profile. It must also say whether a legal already-represented request is an
explicit zero-event `noop`. Rejection emits no domain event. There is no
universal singular-grant or noop assumption; every `+ G` in the tables below is
therefore a C6-marked design placeholder, not an exact cohort.

### Intake, mission, protocol, and authority

| Command | Payload | Domain event / exact cohort target | Aggregate · reducer family · module | Authority target | Obligations | Outside? |
|---|---|---|---|---|---|---|
| `proposal.submit` | missing | `proposal.submitted` + `G` | `proposal` · Proposal · `mission` | one proposal-scoped bounded grant; event basis `ingress_policy` | metadata only; no truth/execution status | no |
| `proposal.decide` | missing | `proposal.decided` + `G` | `proposal` · Proposal · `mission` | bounded proposal grant(s), with any safety/rights/resource screen explicit | admission is worth-testing only | no |
| `mission.create_origin` | missing | `mission.origin_recorded` + `G`; exact accepted-proposal causal ref | `mission` · Mission · `mission` | bounded grant(s); no proposal/mission cross-stream atomicity | no source bytes yet | no |
| `mission.compile_contract` | missing | `mission.contract_compiled` + `G` | `mission` · Mission · `mission` | bounded protocol/mission grant candidate | binds exact fixture/method/resource/rights profile refs | no |
| `mission.advance_phase` | missing | `mission.phase_advanced` + `G`; phase entry evidence required | `mission` · Mission · `mission` | bounded grant(s) for every affected phase gate | may not invent settled work or completed verification | no |
| `protocol.record_exposure` | missing | `protocol.exposure_recorded` + `G`; add `protocol.integrity_determined` when the exposure changes integrity | `protocol` · Protocol · `protocol` | protocol/data-rights bounded grant; event may carry external-observation basis | exposure is monotonic; exact source/configuration subject | no |
| `protocol.freeze` | missing | `protocol.frozen` + `protocol.integrity_determined` + `G` | `protocol` · Protocol · `protocol` | bounded protocol grant(s); post-exposure freeze cannot erase exposure | exact method, estimand, stop/consequence rules | no |
| `authority.record_root_assignment` | missing | `authority.assignment_recorded`; no grant-use recursion | `authority_assignment` · AuthorityAssignment · `authority` | constitutional bootstrap only | reviewed root manifest; architecture fixture grants no external action | no |
| `authority.record_assignment` | missing | `authority.assignment_recorded`; `A`, exact issuer branch unresolved | `authority_assignment` · AuthorityAssignment · `authority` | assignment-only issuer chain candidate | strict scope/delegation subset and role separation | no |
| `authority.issue_grant` | missing | `authority.grant_issued`; `A`, no self-issued target authority | `authority_grant` · AuthorityGrant · `authority` | active issuer assignment; exact parent-grant rule unresolved | exact command/purpose/target/time/use/resource ceiling | no |
| `authority.observe_activation` | missing | `authority.grant_activated`; `A` | `authority_grant` · AuthorityGrant · `authority` | assignment-only/kernel-witness candidate | controlled position and not-before evidence | no |
| `authority.observe_expiry` | missing | `authority.grant_expired`; add `resource.reservation_expired` for an exact active pre-claim reservation; `A/X` | `authority_grant` · AuthorityGrant · `authority` plus ResourceLedger | assignment-only/kernel-controlled-time candidate | never expire by ambient wall clock or release claimed use | no |
| `authority.revoke_grant` | missing | `authority.grant_revoked`; add `resource.reservation_released` only for a winning exact pre-claim reservation; `A/X` | `authority_grant` · AuthorityGrant · `authority` plus ResourceLedger | independent issuer/revoker assignment; target grant cannot self-authorize | ordered race; historical use remains | no |

### Data, retention, transformation, and artifact custody

| Command | Payload | Domain event / cohort target | Aggregate · reducer family · module | Authority target | Obligations | Outside? |
|---|---|---|---|---|---|---|
| `data_asset.record` | missing | `data_asset.recorded` + `G` | `data_asset` · DataAsset · `data_governance` | bounded data-rights metadata grant | metadata discovery only before a use decision; exact byte/collection identity | no |
| `data_asset.change_lifecycle` | missing | `data_asset.lifecycle_changed` + `G` | `data_asset` · DataAsset · `data_governance` | bounded data-rights grant | deny/blocked/quarantined/admitted remain distinct | no |
| `rights_assertion.record` | missing | `rights_assertion.recorded` + `G` | `rights_assertion` · RightsAssertion · `data_governance` | bounded observation grant; event basis `external_observation` | evidence only; never permission | no |
| `data_use.decide` | closed candidate, not admitted | `data_use.decided` + `G` | `data_use_decision` · DataUseDecision · `data_governance` | data-rights assigned role plus bounded decision grant | exact asset, purpose, operation, recipient, provider/model, region, retention, interval; unknown denies | no |
| `retention.record_schedule` | missing | `retention.schedule_recorded` + `G` | `retention_schedule` · RetentionSchedule · `data_governance` | bounded data-rights grant | schedule attached at admission; backup/hold/deletion behavior explicit | no |
| `transformation.record` | missing | `transformation.recorded` + `G` | `transformation` · Transformation · `data_governance` | bounded processing grant | complete input/output lineage; derived output gets new asset identity and decision | no |
| `artifact.record` | missing | `artifact.recorded` + `G` | `artifact` · ArtifactCustody · `artifact` | bounded custody grant | active use decision for bytes; manifest/mode/blob/size/digest/source role | no |
| `artifact.record_validation` | missing | `artifact.validated` + `G` | `artifact` · ArtifactCustody · `artifact` | bounded validation grant | quarantine scan, archive path safety, exact environment/rule refs | no |
| `artifact.promote` | missing | `artifact.promoted` + `G` | `artifact` · ArtifactCustody · `artifact` | bounded promotion grant | rights, custody, validation, protocol role, and dependency checks | no |
| `artifact.quarantine` | missing | `artifact.quarantined` + `G` | `artifact` · ArtifactCustody · `artifact` | bounded custody/safety grant | invalid diagnostics may remain; no claim eligibility | no |
| `artifact.record_unavailability` | missing | `artifact.unavailable` + `G` | `artifact` · ArtifactCustody · `artifact` | bounded custody observation grant | unavailable/withheld/rights-forbidden never becomes zero or deleted | no |

The provisional 44-command classification creates no `data_exposure` event and
no work lease, attempt, sandbox, or distinct materialization fact. That is C5,
not evidence that local execution is legal. An exact `DataUseDecision` remains
necessary but is not sufficient: before either replay analyzer sees bytes, the
resolved design must retain the exact materialization intent, lease-equivalent
exclusivity, sandbox capability, safety/execution grants, resource reservation
and claim, and start/completion observations. Crossing a provider/model/network/
recipient boundary remains forbidden and would additionally require the full
external-effect lifecycle.

### Science, resource evidence, blockers, and verification

| Command | Payload | Domain event / cohort target | Aggregate · reducer family · module | Authority target | Obligations | Outside? |
|---|---|---|---|---|---|---|
| `run.determine_validity` | missing | `run.validity_determined` + `G`; invalid branch participates in `C3` | `run` · RunValidity · `measurement` | bounded verification/method grant; event basis may be kernel derivation | exact protocol/run/manifests/exposure/missingness | no |
| `measurement.determine_disposition` | missing | `measurement.disposition_determined` + `G`; no-valid-measurement branch participates in `C3` | `measurement` · MeasurementDisposition · `measurement` | bounded verification/method grant | invalid/unmeasured/exploratory/valid are orthogonal to null/support | no |
| `metric.record_observation` | missing | `metric.observed` + `G` | `metric` · MetricObservation · `measurement` | bounded observation grant; event basis `external_observation` or exact deterministic result | exact decimals/units/estimand scale, planned vs observed, missingness | no |
| `falsifier.adjudicate` | missing | `falsifier.adjudicated` + `G` | `falsifier` · Falsifier · `measurement` | bounded registered-rule grant; event basis kernel derivation or assigned review | each known-bad vector must fail at intended layer | no |
| `resource.record_observation` | missing | unresolved `resource.observed` versus `resource.usage_observed`/`resource.reservation_settled`; `C1/X` | `resource_budget` · ResourceLedger · `resources` | bounded observation grant; usage event basis external observation; settlement kernel derivation | exact CPU/time/memory/storage/process and IV0–IV4 axes; unknown is not zero | no |
| `blocker.open` | missing | `blocker.opened` + `G` | `blocker` · Blocker · `mission` | bounded role/rule grant | class/scope/reason/evidence/resolution requirement; blocker is not a scientific verdict | no |
| `verification.request` | missing | `verification.requested` + `G` | `verification` · Verification · `verification` | bounded verification request grant | frozen subject/method/independence/control/resource profile | no |
| `verification.assign` | missing | `authority.grant_used` + `resource.reservation_created` + `verification.assigned`; optional grant exhaustion is a separate exact alternative | `verification` plus `resource_budget` · Verification/ResourceLedger · `verification`/`resources` | bounded grants for verification, resource, execution, and exact data exposure | reserve complete IV0–IV4 and resource ceiling; producer cannot select terminal verifier | no |
| `verification.start` | missing | provisional grant-use set + `resource.reservation_claimed` + `verification.started`; C5 must add or bind the execution/materialization cohort | `verification` plus `resource_budget`; possible work/execution dependencies · Verification/ResourceLedger/C5 unresolved · `verification`/`resources` | active bounded execution/verification grants | claim before work; exact lease/materialization/sandbox/environment/input/control refs; zero network/provider/model | no |
| `verification.complete` | missing | `verification.completed` + `G(c)`; settlement is not inferred from completion; C5 execution evidence required | `verification` · Verification · `verification` | bounded independent-verifier grant(s) | exact immutable package; terminal `confirmed/rejected/inconclusive/invalid/blocked`; execution path retained | no |
| `verification.dispute` | missing | `verification.disputed` + `G` | `verification` · Verification · `verification` | assigned verification/review role plus bounded grant | immutable package status retained; open dispute blocks eligibility where required | no |
| `verification.invalidate` | missing | `verification.invalidated` + `G`; add `resource.reservation_released` only for a named pre-claim reservation; claimed use remains held | `verification` plus ResourceLedger · `verification`/`resources` | assigned verification role plus bounded grant | no crash-driven release; exact invalidation basis | no |
| `reproducibility.determine` | missing | `reproducibility.determined` + `G(c)`; `C7/X` | `verification` · **unresolved: catalog `Reproducibility` vs candidate `Verification`** · `verification` | bounded registered-rule/verification grant | `same_evidence_recomputed`, `clean_reproduction`, `not_reproduced`, `inconclusive`, or `invalid` | no |
| `review.record` | missing | `review.recorded` + `G` | `review` · Review · `verification` | assigned independent review role plus bounded grant | statistical/domain/security scope, conflicts, limitations, indeterminate retained | no |

The resource ceiling is fixed by the first-slice profile: network, provider/model
calls, GPU, cloud jobs, external writes, and publication actions are zero; CPU
is 60 seconds per replay environment, elapsed time 120 seconds, peak resident
memory 512 MiB, admitted source bytes 64 MiB, scratch 512 MiB, and processes 4.
Two clean replay environments retain separate reservations and observations.

### Adjudication, claim compilation, and correction

| Command | Payload | Domain event / cohort target | Aggregate · reducer family · module | Authority target | Obligations | Outside? |
|---|---|---|---|---|---|---|
| `adjudication.record` | missing | `adjudication.recorded` + `G` | `adjudication` · Adjudication · `adjudication` | bounded registered consequence-rule grant; event basis kernel derivation | supported/inconclusive/corrected/refused/blocked remain distinct; unresolved input refuses | no |
| `claim.propose` | missing | `claim.proposed` + `G` | `claim_proposal` · ClaimProposal · `claims` | bounded proposal grant | source wording is evidence, never final truth | no |
| `claim.record_disposition` | missing | `claim.disposition_recorded` + `G` | `claim_proposal` · ClaimProposal · `claims` | bounded claim-review grant | eligible/rejected/deferred plus exact reasons and forbidden scopes | no |
| `claim.compile_version` | missing | `claim.version_compiled` + `G` | `claim_version` · ClaimVersion · `claims` | bounded deterministic compiler grant; event basis kernel derivation | exact adjudication/verification/dependency frontier and all mandatory limitations | no |
| `claim.supersede` | missing | `claim.superseded` plus mandatory invalidation cohort; `C2/X` | `claim_version` · ClaimVersion · `claims` | bounded correction grant(s), with affected role separation | replacement immutable; old facts retained; no publication correction in this slice | no |
| `dependency.record_invalidation` | missing | `dependency.invalidation_recorded`; must share the `C2` correction fence/cohort | `dependency` · Dependency · `claims` | bounded correction/kernel grant | complete fanout at exact frontier; no silent eligible dependent | no |

## Provisional event conflict-union

Under the current disputed 44-command classification, the catalog mappings have
43 unique primary event names because two assignment commands share
`authority.assignment_recorded`. Adding the nine currently named kernel-cohort
event names yields a 52-name **conflict union**. It is not an exact required event
set: C1's mutually exclusive branches contain different subsets of
`resource.observed`, `resource.usage_observed`, and
`resource.reservation_settled`; C5/C8 can add names, while C2/C3/C7 can change
producers or ownership. C6 changes occurrence cardinality even when the unique
event discriminator set is unchanged.

| Kernel event | Payload-schema ID in `ResearchEvent` | Aggregate | Required by |
|---|---|---|---|
| `protocol.integrity_determined` | `urn:odeya:event-payload:protocol.integrity_determined:1.0.0` | `protocol` | exposure/freeze consequence |
| `authority.grant_used` | `urn:odeya:event-payload:authority.grant_used:1.0.0` | `authority_grant` | every ordinary bounded domain commit |
| `authority.grant_exhausted` | `urn:odeya:event-payload:authority.grant_exhausted:1.0.0` | `authority_grant` | final legal bounded-grant use alternative |
| `resource.reservation_created` | `urn:odeya:event-payload:resource.reservation_created:1.0.0` | `resource_budget` | verification assignment |
| `resource.reservation_claimed` | `urn:odeya:event-payload:resource.reservation_claimed:1.0.0` | `resource_budget` | verification start |
| `resource.reservation_released` | `urn:odeya:event-payload:resource.reservation_released:1.0.0` | `resource_budget` | winning pre-claim invalidation/revocation |
| `resource.reservation_expired` | `urn:odeya:event-payload:resource.reservation_expired:1.0.0` | `resource_budget` | controlled-time pre-claim expiry |
| `resource.usage_observed` | `urn:odeya:event-payload:resource.usage_observed:1.0.0` | `resource_budget` | exact retained resource observation |
| `resource.reservation_settled` | `urn:odeya:event-payload:resource.reservation_settled:1.0.0` | `resource_budget` | complete exact usage/billing/refund reconciliation |

Every one of the 52 event discriminators in the current conflict union exists structurally in
`ResearchEvent`; none has a real immutable EventContractRecord in an activated
registry. Structural presence is not producer, reducer, retention, privacy, or
cohort admission. The final missing EventContractRecord count must be recomputed
from the resolved event set.

## Aggregate, reducer, and state closure

The current 23-row aggregate/state/reducer list is a provisional dependency
hypothesis. Exactly one canonical reducer and one closed state subject are
required for every resolved aggregate, but C5/C8 can add aggregates and C7 must
resolve whether reproducibility is folded, split, or composed. Names below are
reducer *families* from the catalog/state model, not existing reducer IDs.

| Aggregate | Owner module | Reducer family | Minimum non-collapsible state |
|---|---|---|---|
| `proposal` | `mission` | Proposal | submitted/decided/withdrawn and exact decision basis |
| `mission` | `mission` | Mission | origin, compiled contract, phase, control, closure frontier |
| `protocol` | `protocol` | Protocol | exposure, freeze, integrity, branch/supersession pointers |
| `authority_assignment` | `authority` | AuthorityAssignment | principal, role, issuer chain, scope, interval, active/revoked state |
| `authority_grant` | `authority` | AuthorityGrant | issued/active, reservation/use count, exhausted/expired/revoked |
| `data_asset` | `data_governance` | DataAsset | exact identity, lifecycle, classification, custody pointer |
| `rights_assertion` | `data_governance` | RightsAssertion | evidence-only assertion, source, scope, validity/unknowns |
| `data_use_decision` | `data_governance` | DataUseDecision | purpose/operations/recipients/providers/region/retention/interval/decision |
| `retention_schedule` | `data_governance` | RetentionSchedule | trigger, bounds, planes, hold precedence, terminal action |
| `transformation` | `data_governance` | Transformation | exact input/output lineage, rule/environment, loss/redaction, validation |
| `artifact` | `artifact` | ArtifactCustody | recorded/validated/promoted/quarantined/unavailable plus exact identity |
| `run` | `measurement` | RunValidity | valid/invalid/indeterminate and protocol/exposure/evidence basis |
| `measurement` | `measurement` | MeasurementDisposition | valid/exploratory/no-valid-measurement/withheld/unavailable |
| `metric` | `measurement` | MetricObservation | exact estimand/quantity/unit/value/uncertainty/missingness |
| `falsifier` | `measurement` | Falsifier | mutation identity, intended layer, pass/fail/indeterminate consequence |
| `resource_budget` | `resources` | ResourceLedger | reservation lifecycle and separate estimate/ceiling/actual/billed/refunded/missing axes |
| `blocker` | `mission` | Blocker | class/scope/reason/evidence/resolution requirement/open state |
| `verification` | `verification` | **C7 unresolved: Verification versus catalog Reproducibility** | request/assignment/run/terminal/dispute/invalidation/reproducibility and independence axes; no two independent canonical reducers by implication |
| `review` | `verification` | Review | scope, reviewer/conflict, findings, disposition, limitations |
| `adjudication` | `adjudication` | Adjudication | exact inputs/rule/outcome/reasons/eligibility/refusal |
| `claim_proposal` | `claims` | ClaimProposal | proposed language, scope, disposition, reason/limitation set |
| `claim_version` | `claims` | ClaimVersion | immutable version, eligibility, current/superseded/retracted pointer set |
| `dependency` | `claims` | Dependency | source/dependent edge, invalidation frontier/reason/fanout state |

Under the current hypothesis, 23 state-subject members, 23 reducer-contract
members, and every member of the 52-name event conflict union are absent. These
are working gap counts, not final cardinalities. The structural probe fixtures
in the registry test directory are not these records.

## Proof-mission coverage

| Fixture | Mandatory path | Required canonical distinction |
|---|---|---|
| `S-POS-001` | asset/rights/retention/custody → exposure/freeze/integrity → C5-complete materialization/execution → valid run/measurement/metric/falsifiers → two separately reserved/claimed/observed/settled verifications → review/adjudication → claim proposal/disposition/version | bounded `supported_within_scope`; simulation only; 799 observed remains distinct from 800 planned; limitations retained |
| `S-NULL-001` | same scientific and verification path | source label `TRANSFER_NULL` retained as provenance, Odeya adjudication `inconclusive`; no benefit/harm/equivalence/affirmative-null claim |
| `T-CORR-192` | exact Telos assets/custody → deterministic observations/review/adjudication → replacement claim version → supersession + dependency invalidation | obsolete framing superseded while independent 40/40 facts remain; `C2` must close first |
| `T-REPLAY-192` | committed receipt as source artifact plus clean verification request/assignment/start/completion → `not_reproduced` → open dispute/invalidation/blocker | committed `pass` and replay discrepancy both visible; sealing ineligible; correction core not erased |
| `T-INVALID-197` | exposure/integrity → invalid run + no-valid-measurement/exploratory diagnostics → quarantine/falsifier/review/refusal | invalid protocol never becomes a scientific null, pass, specificity, or complementarity claim; `C3` must close first |
| `T-INVALID-201` | same invalid path with missing/nondecision metric bounds | unparseable/absent outcomes remain missing; no detector-performance claim |
| `I-BLOCK-000` | admitted project-generated metadata/proof only → artifact validation/unavailability + rights/evidence blocker | `BLOCKED_EVIDENCE`; integrity/readiness does not authorize training or create a physical result |
| `I-REFUSE-001` | exact proposed contract/review/authority evidence → blocker + refused adjudication | no prospective run or measurement event is fabricated; recommendation is not action |
| `I-RIGHTS-001` | metadata-only asset → rights assertion → denied/indeterminate `data_use.decided` → rights blocker | raw NASA bytes stay absent; no artifact promotion, model exposure, training, or public release |

## The 77 commands provisionally classified outside

Every command below remains non-executable design vocabulary. The 77-name
classification is conditional: C5 can move lease/attempt/materialization commands
inside, and C8 can move checkpoint/witness/recovery commands inside unless their
machine-bound prerequisite is separately admitted. Only after C1/C5-C8 close and
the inventory is recomputed may the final outside names be required absent from
the first-slice envelope, registry, and handler map. Event names follow the
existing catalog; they are not admitted alternatives.

| Outside family | Commands | Why outside | Separate payload candidates already present |
|---|---|---|---|
| Proposal withdrawal | `proposal.withdraw` | no withdrawal fixture | none |
| Mission control/closure | `mission.change_control`, `mission.close`, `mission.record_handoff` | slice retains results and stops; it does not claim full mission closure/handoff | none |
| Protocol evolution | `protocol.amend`, `protocol.fork`, `protocol.supersede` | fixtures retain invalid/corrected facts without prospectively changing the protocol | none |
| General work execution | `work_graph.compile`, `stage.set_readiness`, `stage.set_authorization`, `work.acquire_lease`, `work.renew_lease`, `work.release_lease`, `work.revoke_lease`, `attempt.start`, `attempt.report` | **C5 conditional:** may stay outside only if a specialized verifier-execution cohort supplies the exact lease/materialization/sandbox/reservation/execution facts | none |
| Budget terminal event | `budget.record_exhaustion` | over-ceiling input rejects the slice; it is not a successful proof path | none |
| Blocker closing | `blocker.resolve`, `blocker.supersede` | named Inbar/Telos blockers intentionally remain open in the proof fixtures | none |
| Other artifact terminal facts | `artifact.record_corruption`, `artifact.tombstone` | mutations fail validation/quarantine; no deletion/tombstone mission | none |
| Verification resolution/extension | `verification.resolve_dispute`, `replication.start`, `replication.determine`, `transport.start`, `transport.determine` | replay discrepancy remains open; no external replication or transport claim | none |
| Retraction | `claim.retract` | Telos is an additive correction/supersession, not retraction | none |
| Publication/release | `publication.compile_candidate`, `release.request`, `release.decide`, `publication.seal`, `publication.start_release`, `publication.record_release_settlement`, `publication.correct`, `publication.withdraw` | terminal boundary is before publication | none |
| External effects | `external_effect.authorize`, `external_effect.start`, `external_effect.cancel`, `external_effect.report_completion`, `external_effect.start_reconciliation`, `external_effect.complete_reconciliation`, `external_effect.fail_reconciliation` | zero provider/network/physical/external dispatch | authorize/start/cancel only |
| Incidents | `incident.open`, `incident.transition` | ordinary fixture discrepancies/blockers are not operational incidents | none |
| Learning/strategy | `grounded_outcome.record`, `strategy.record_candidate`, `strategy.authorize_shadow`, `strategy.record_shadow`, `strategy.authorize_canary`, `strategy.decide_promotion`, `strategy.rollback` | no autonomous learning or promotion claim | none |
| Data-use revocation | `data_use.revoke` | first-slice rights-blocked state is an initial deny/indeterminate decision, not a later revocation | `data_use.revoke` |
| Governed exposure | `data_exposure.record_intent`, `data_exposure.record_observation`, `data_exposure.record_settlement` | **C5 conditional:** external crossing is forbidden, but a materialization-intent producer is still required before local bytes become visible | intent only |
| Deletion | `deletion.open_case`, `deletion.record_progress`, `deletion.close_case` | no deletion lifecycle is exercised | close only |
| Legal hold | `legal_hold.issue`, `legal_hold.release`, `legal_hold.observe_expiry` | no hold fixture | issue/release only |
| Checkpoint/recovery | `ledger_checkpoint.propose`, `ledger_checkpoint.seal`, `ledger_checkpoint.record_witness_observation`, `ledger_checkpoint.record_consistency_failure`, `backup.record_write_observation`, `backup.record_verification_observation`, `backup.record_recoverability_observation`, `restore.open_case`, `restore.record_report`, `restore.close_case`, `recovery.record_current_policy_frontier`, `recovery.record_decision`, `recovery.enter_quarantine`, `recovery.change_service_scope`, `ledger.record_fork`, `ledger.begin_epoch` | **C8 conditional:** may stay outside only behind a separately admitted, machine-bound root/C0/checkpoint/witness/activation/recovery prerequisite; otherwise necessary commands enter scope | checkpoint seal, recovery decision, service-scope change, begin epoch |

The table names the current 77-name outside hypothesis. Twelve account for the
remaining twelve of the repository's thirteen separate closed payload
candidates. Those files do not by themselves justify admission, but C5/C8—not
payload availability—must determine final scope.

## Construction order

The order follows the acyclic registry law: schema → state → reducer → event →
command. No later artifact may be used to hand-wave an earlier missing one.

1. **Resolve C1-C8 before freezing any scope.** Decide the resource algebra,
   correction/invalidity producers, authority races, local execution cohort,
   multi-grant cardinalities, reproducibility reducer ownership, and separately
   admitted recovery prerequisite. Do not select the numerically convenient
   branch.
2. **Recompute the complete dependency inventory.** Repartition all 121 design
   commands, recompute payload/event/aggregate/reducer/module counts, and prove
   that every outside command is either terminally unreachable or supplied by a
   named separately admitted prerequisite. Any changed producer restarts this
   audit.
3. **Write and test every missing command-payload schema.** The current
   hypothesis has 43, but that is not the construction target until recomputed.
   Re-review the existing
   `data_use.decide` candidate against the exact first-slice role, recipient,
   provider/model, region, retention, and denied/indeterminate cases.
4. **Write every resolved aggregate-state schema and state-subject record.** The
   current hypothesis has 23. Define
   origins, unknown/missing defaults, axes, corrections, terminality, and exact
   historical read policy.
5. **Write every resolved reducer-contract record.** Close C7 first. Each accepts only its admitted event
   subset, has finite resource bounds, and passes positive, negative, boundary,
   race, replay, and independent-implementation vectors.
6. **Write the resolved event-contract set.** Do not use the current 52-name
   conflict union as the target. Bind each exact `ResearchEvent` branch,
   producer command(s) or kernel cohort, aggregate owner, reducer, retention,
   privacy, and trace evidence. Resolve the payload-version `2.0.0` branches for
   verification assignment/completion/dispute/reproducibility explicitly.
7. **Write the resolved command-contract set.** Do not use the provisional 44 as
   a target. Bind exact payload bytes, owning port,
   source-state predicate, authority mode/role, consumption point, required
   evidence families, closed event alternatives, limits, noop/rejection codes,
   and trace suite.
8. **Bind the C8 prerequisite and build immutable first-slice snapshots.** The
   separately admitted root/C0/checkpoint/witness/activation/recovery evidence
   must exist before the first mission command; the first-slice schema/state/
   reducer/event/command snapshots then bind that prerequisite. This document
   creates neither surface.
9. **Generate the admitted-only envelope and handler-port manifest from the
   registry source.** The active discriminator, registry-member, and conforming
   handler sets must be equal; the recomputed outside names must be absent.
10. **Execute two independent reducer runners and two clean scientific verifier
   paths.** Compare original event bytes, per-event state digests, final state,
   resources, and the nine fixture dispositions.
11. **Run the full refusal/falsifier suite and independent review.** Only an
    explicit later Gate A decision may call the bounded set admitted.

## Refusal criteria

Refuse registry construction, activation, or a “Gate A complete” claim if any
of these is true:

1. any of C1-C8 remains unresolved;
2. the 44/77 command partition, 52-name event conflict union, or 23 aggregate/
   reducer rows are represented as frozen or dependency-closed;
3. any command in the recomputed required set lacks a separate closed payload schema, exact command record,
   handler-port contract, authority role/mode, consumption point, finite event
   alternative, or adversarial trace;
4. any event in the resolved event set lacks an exact event record, sole aggregate owner, admitted
   producer/cohort, reducer, retention/privacy contract, or trace;
5. any resolved aggregate lacks a closed state subject, one canonical reducer, explicit
   unknown/missing defaults, correction behavior, and independent replay;
6. a generic object schema or broad envelope branch is counted as a command
   payload contract;
7. an inactive design-vocabulary name appears in the admitted envelope,
   registry, or handler map;
8. root/assignment/grant setup becomes self-authorizing, a caller chooses its
   authority mode, a required grant lacks one same-batch use, or the exhaustion
   set differs from the exact final-use subset;
9. local bytes become visible without exact materialization intent,
   lease-equivalent exclusivity, sandbox capability, safety/execution grants,
   and resource reservation/claim/start evidence;
10. a verification reservation can be orphaned, released after claim, settled
   without exact observations, or have unavailable use read as zero;
11. rights assertion or possession becomes permission, rights-blocked bytes are
   acquired/exposed, or a derived asset lacks decision/lineage/retention;
12. invalid run becomes scientific null, interval crossing zero becomes
    equivalence/support, committed `pass` overrides replay discrepancy, or
    missing detector output becomes a class;
13. correction permits a visible eligible interval between supersession and
    invalidation;
14. reproducibility has conflicting or composition-ambiguous reducer ownership;
15. the first mission command lacks a machine-bound separately admitted root,
    C0 bundle, witnessed checkpoint, current activation, and legal recovery/
    fork frontier;
16. any projection is needed to recover canonical truth, or deletion/rebuild
    does not reproduce exact semantic state;
17. the slice performs or authorizes a provider/model call, network access,
    cloud job, external write, simulator launch, training, publication, or
    physical action; or
18. the resulting claim exceeds the narrow statement that Odeya can represent
    and adjudicate these fixed historical distinctions under the accepted
    profiles.

## Handoff state

The plan now establishes an auditable refusal, not a bounded target or readiness.
The only frozen count is 121 design-vocabulary commands. The working hypothesis
is 44 required/77 outside, 43 missing payloads, a 52-name C1 conflict union, and
23 aggregate/state/reducer rows, but every one of those scope counts must be
recomputed after C1 and C5-C8. Eight known conflicts remain, alongside the
missing machine records and independent implementations/reviews. No
registry, root, activation, runtime, canonical proof trace, publication surface,
or Gate A completion is created or implied here.
