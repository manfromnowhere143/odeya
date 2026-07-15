# Semantic Validation Constitution

Status: proposed architecture, 2026-07-15. JSON Schema fixtures prove structural shape only. This document defines the relational and scientific rule layer that must be frozen and independently tested before Gate A.

## Validation pipeline

Validation is ordered and monotonic. A later layer may add failures or narrower conditions; it cannot erase an earlier failure.

```text
I0 generic frame/decompression/rate bounds
  -> I1 bounded selector + historical-receipt/active-member resolution
       -> pre-envelope refusal, or
       -> V0 admitted-envelope byte/parser safety
  -> V1 schema and format
  -> V2 canonical representation and digest
  -> V3 single-object semantic rules
  -> V4 reference and graph integrity
  -> V5 state-transition and transaction rules
  -> V6 authority, policy, rights, budget, and risk
  -> V7 scientific/method admissibility
  -> V8 verification, claim, and publication eligibility
  -> V9 projection/package conformance
```

I0/I1 follow [ADR 0013](decisions/0013-admitted-only-command-ingress.md). They cannot authorize or create a command. Unknown/reserved/unbindable ingress stops with no `CommandReceipt` or canonical cohort; exact historical retry returns its existing receipt. For a newly bound admitted envelope, each V-layer returns a retained `ValidationResult`; none mutates the submitted object. Repair creates a new candidate version and a new result.

## Rule registry contract

Every semantic rule version contains:

```text
rule_id + semantic version + immutable registry digest
validation layer and owning module
objects/events/commands and schema-version ranges supported
formal predicate or deterministic reference algorithm
required reference graph, controlled time, units, registries, or policy inputs
pass/fail/indeterminate output vocabulary and stable reason codes
severity and exact consequence by command/stage/claim/release context
assumptions, numerical tolerance, overflow/size/complexity bounds
positive, boundary, negative, metamorphic, race, and compatibility vectors
independent implementation/verifier requirement
supersession and backward-reading policy
owner, review evidence, effective/expiry dates
```

An absent rule, unresolved rule version, unsupported schema range, missing reference, missing controlled input, timeout, or internal error yields `indeterminate` and fails closed for consequential admission. It is never interpreted as pass.

## Validation result contract

A result records:

```text
validation_result_id
subject type/id/version/digest
validator code/environment identity
rule-set ID/version/digest
reference-set digest and ledger position
controlled-time value/source/uncertainty where used
per-rule verdict, reason code, evidence, and path
aggregate disposition: pass | fail | indeterminate
limitations and unsupported checks
known-bad fixture results
created time and accountable execution identity
```

The aggregate disposition is a deterministic fold: any required `fail` means fail; otherwise any required `indeterminate` means indeterminate; only all required passes mean pass. Severity controls consequence, not whether a failure disappears.

Candidate structural contracts now exist in
[`validation-rule-registry.schema.json`](../schemas/validation-rule-registry.schema.json)
and [`validation-result.schema.json`](../schemas/validation-result.schema.json).
Their fixtures prove only closed shape and the three-way aggregate fold. They do
not prove that a predicate is correct, that two implementations are independent,
that reference bytes match their digests, or that a registry was validly activated.

## Scientific object family and semantic boundary

The following immutable candidate contracts close the first structural inventory.
Mutable lifecycle state remains in events and projections; these records never
rewrite one another.

| Contract | Structural guarantee | Required semantic checks beyond JSON Schema |
|---|---|---|
| `ProtocolSnapshot` | Closed frozen bundle; confirmatory snapshots are outcome-blind; at least three falsifier specs and one control are named | Mission/reference identity, digest recomputation, exposure monotonicity, prospective meaning, statistical/method admissibility |
| `ProtocolAmendment` | Decision/effect/result combinations are closed; no retroactive effect value exists | Time order, patch application, affected-branch ancestry, exposure relevance, authority scope, downstream invalidation |
| `RunManifest` | Exact inputs, identities, budgets, controls, outputs, grants, and recovery policy; verification/replication name a source and independence profile | Artifact promotion/rights, grant validity, budget availability, source inequality, evaluator compatibility, digest and preflight freshness |
| `ArtifactManifest` | Exact bytes, origin, lineage, rights, sensitivity, retention, encryption, and storage binding are closed | Byte/digest recomputation, parent existence, provenance graph, rights compatibility, retention order, storage/object-lock evidence |
| `ArtifactCustodyObservation` | Custody actions are append-only observations; promotion requires a structurally passing integrity check and rights/grant references | Expected/observed digest equality, prior-chain continuity, actor authority, location reality, observation/recording order |
| `MetricResult` | Missingness cannot retain an estimate or threshold pass; invalid results cannot pass/fail a threshold | Estimator/protocol match, unit compatibility, sample arithmetic, interval ordering, multiplicity/stopping, evidence completeness |
| `FalsifierResult` | Executed/not-executed states are distinct; a missed known-bad control must fail its gate | Falsifier/spec identity, evaluator correctness, evidence authenticity, consequence-table application |
| `ClaimCorrection` | Correction and retraction shapes are distinct; prior claim versions remain referenced | Dependency closure, replacement/supersession consistency, visibility ordering, projection settlement |
| `Handoff` | Exact ledger checkpoint, state facts, dependencies, and legal next actions; close requires a clean terminal shape | Fresh fold from canonical events, head/checkpoint integrity, lease/effect state, recipient identity, action legality |
| `GroundedOutcome` | World-contact source, multidimensional observations, missingness, costs, applicability, and confounds remain separate | Source authenticity, verifier independence, causal/transport interpretation, temporal order, cross-mission applicability |
| `StrategyCandidate` | Candidate remains quarantined and has no production credential, write, or effect authority | Recurrence threshold, outcome independence, fixture validity, evaluation leakage, change-set applicability |
| `PromotionDecision` | A human decision preserves per-dimension observations; approvals require bounded scope, review, and grants | Review independence, grant scope/time, Pareto/acceptance rule, rollout preconditions, settlement and rollback readiness |
| ingress selector / `CommandEnvelope` / `CommandReceipt` | Bounded selector resolves historical settlement or one server-activated admitted member before envelope construction; closed exact-version envelope/settlement shapes require immutable registry snapshot, separate activation, member record, and non-recursive digest contracts | Frame limits; historical-before-active lookup; runtime-enabled envelope/registry/conforming-handler set equality; no reserved/null member; digest recomputation; registry bytes/membership; activation branch/scope/position/currentness; duplicated metadata equality; payload-schema validation; one immutable receipt and exact replay |
| `PolicyDecision` / `AdmissionEvidenceBundle` | Kernel-produced immutable policy result and closed evidence index retain exact request, frontier, policy/rule/engine/input identities, three-way disposition, obligations, per-stage results, and typed evidence refs without embedding mutable state | Caller exclusion; input/reference truth; bundle/rule activation; deterministic evaluation; obligation enforcement; CommandContractRecord evidence-profile completeness; stage order; receipt/event equality; checkpoint inclusion |
| `LedgerCheckpoint` | Exact EngineContractRoot, AggregateStateSubjectRegistry, C0 registry slots, and an explicit domain/profile/schema-bound, non-self-referential digest scope | Checkpoint digest/signatures; root/bundle/component compatibility and direction; set roots/cardinality/proofs; previous-checkpoint continuity; witness independence |
| `WorkContract` / governed-processing effect bindings | A work contract is a deterministic control artifact and governed dispatch has a distinct typed effect class with explicit data/exposure/provider/frontier inputs | Current rights/policy/authority/resource folds; scope and binding equality; checkpoint/source ordering; provider configuration truth; no bytes/spend before admitted dispatch claim |
| `RootAuthorityManifest` / `AuthorityAssignment` | Bootstrap is non-self-issued, architecture fixtures cannot authorize external effects, and assignments remain distinct from grants | Canonical digest/signature/checkpoint validity, role uniqueness, effective-control plurality, source chain, scope subset, time, rotation/recovery quorum |
| `DataAssetRecord` / `RightsAssertion` / `DataUseDecision` | Exact identity, evidence-only assertions, and executable decisions are separate; denied/indeterminate decisions contain no authorization scope | Byte/collection identity, assertion provenance, jurisdiction/policy interpretation, exact purpose/recipient/provider/region/time coverage, revocation and reuse |
| `DataExposureRecord` / `TransformationRecord` | Intent, observation, and settlement are distinct immutable facts; derived outputs retain explicit rights and quarantine consequences | Intent coverage, exact projection/configuration, external occurrence evidence, monotonic exposure, lineage, residual risk, rights non-widening, contamination fanout |
| `RetentionSchedule` / `DeletionCase` / `LegalHold` | Unknown capability blocks activation, deletion states remain distinct, and a hold grants no access | Duration/time order, storage-plane completeness, backup/provider reality, destruction evidence, minimal lawful tombstone, scientific invalidation, hold scope/release |
| `PublicationCandidate` / `PublicationDecision` | Candidate carries no authority; authorization structurally requires seven explicit check plus human dispositions over one exact candidate digest | Digest recomputation, claim eligibility, gate evidence authenticity, candidate/scope equality, conflicts/quorum, seal determinism, later grant/effect ordering |

Each schema description repeats the relevant boundary so a structural validator
cannot be mistaken for a scientific or authorization oracle. Cross-object rules
must operate on exact object versions and a retained reference-set digest.

## Founding rule catalog

The IDs below are candidate stable meanings. Gate A freezes their exact predicates and fixtures.

### Representation and time

| Rule | Predicate |
|---|---|
| REP-001 | Input has valid UTF-8, no duplicate keys, no forbidden numeric form, and no silent Unicode normalization |
| REP-002 | Canonical bytes recompute to the declared digest under the named profile/schema namespace |
| REP-003 | Decimal strings, precision/scale, units, ratios, intervals, distributions, and missingness use registered semantic types |
| REP-004 | Every request/result/receipt/event/checkpoint digest is recomputed from its exact registered domain separator, canonicalization profile, schema binding, and included/excluded JSON-Pointer set; a digest or signature is never in its own hashed subject |
| TIME-001 | `issued_at <= not_before < expires_at` where all are required; equality is accepted only where explicitly specified |
| TIME-002 | Observation time, recorded time, controlled commit time, and uncertainty/source are distinguishable; impossible order is rejected or explicitly explained |
| TIME-003 | Publication expiry is null or later than sealing; embargo/review times satisfy the accepted order |
| TIME-004 | Exposure is monotonic and a later event cannot restore an earlier blind state |

### Quantities and statistical objects

| Rule | Predicate |
|---|---|
| QTY-001 | Compared/additive quantities are dimensionally compatible after an explicit registered conversion |
| QTY-002 | Interval lower bound is not greater than upper bound under the same semantic quantity/unit; level is in its valid open/closed range |
| QTY-003 | `between` has exactly two ordered thresholds; one-sided comparators have one; direction matches the frozen consequence rule |
| QTY-004 | Missing, unknown, unmeasured, unavailable, withheld, and not-applicable values carry no fabricated estimate/zero |
| STAT-001 | Estimator, interval, multiplicity, sequential regime, missingness, data role, and stopping policy resolve to one compatible method profile |
| STAT-002 | Fixed-horizon results reject unplanned optional stopping or post-exposure family changes |
| STAT-003 | Null/equivalence claims require the frozen null region, valid measurement, adequate method, and declared uncertainty—not failure to reject |
| STAT-004 | Selected/best-of-N results retain selection mechanism and multiplicity consequences |

### References, versions, and events

| Rule | Predicate |
|---|---|
| REF-001 | Every referenced schema, rule, policy, protocol, manifest, grant, artifact, event, and claim version exists at the declared immutable identity |
| REF-002 | Reference subject/mission/branch/scope matches the owning object; cross-mission links use an explicitly admitted relation |
| REF-003 | Referenced artifact is promoted, available, digest-valid, rights-compatible, and non-quarantined for the requested role |
| REG-001 | Envelope and receipt snapshot/activation/member references resolve to retained immutable bytes; `latest`, mutable lookup, unavailable bytes, and unregistered schema identity fail closed |
| REG-002 | Member proof verifies against the named snapshot and every duplicated command type/version/schema ID/schema digest equals the envelope, payload bytes, and receipt |
| REG-003 | Activation names the same snapshot digest, compatible C0 checkpoint registry bundle, tenant/mission scope, and selected ledger branch; `activation_position` is not ahead of the command target/current position and is not superseded there |
| REG-004 | Registry snapshot/member canonical bytes contain no checkpoint or activation reference; genesis uses the reviewed external constitutional-bootstrap activation procedure, never self-activation |
| REG-005 | For a new command at any runtime activation, the server-selected enabled envelope discriminator set, enabled registry member set, and conforming handler map are exactly equal; reserved design-vocabulary names and nullable/fabricated records occur in none of them. Gate A contract admission alone does not claim handler implementation |
| REG-006 | Generic limits and bounded selector extraction are the only work before historical/active resolution; an unknown, reserved, inactive, invalid-member, or unavailable-root selector returns `command_contract_not_admitted` without envelope construction, payload validation, handler/authority evaluation, receipt, event, grant/resource consequence, or outbox |
| REG-007 | Existing `tenant + namespace + command_id` settlement resolves before active-new-command lookup; exact retry validates under retained historical semantics and returns the same receipt, while changed binding creates no second receipt and cannot execute |
| REG-008 | A new `CommandReceipt` is legal only after one exact admitted member and all required envelope bindings resolve; `unknown_command` is never a receipt result, while `schema_unresolvable` is legal only for an otherwise bound admitted member whose exact payload-schema bytes cannot be loaded |
| C0-001 | Checkpoint C0 references resolve to one mutually compatible schema/command/event/reducer/module/resource-unit/rule/policy/canonicalization/method bundle at its inclusive position, and its admission-evidence-set commitment covers every receipt-bound decision/evidence record |
| EVT-001 | `payload_schema_id`/digest exactly matches `event_type` and payload bytes under the event registry |
| EVT-002 | Aggregate type/id is allowed to own the event; reducer version supports the event version |
| EVT-003 | Sequence, previous digest, batch index/size, command ID, commit ID, and event positions are contiguous and internally consistent |
| EVT-004 | One batch is the complete pure result of its command receipt; no required authority/resource/outbox fact is absent |
| EVT-005 | Upcasting preserves scientific meaning and original bytes; unsupported events fail read rather than reinterpret silently |

### State, blockers, attempts, and effects

| Rule | Predicate |
|---|---|
| STATE-001 | Command edge is legal from the exact aggregate fold at `expected_position` |
| STATE-002 | One mutable stage has at most one active writer lease; renew/revoke/complete races follow canonical commit order |
| STATE-003 | Attempt completion cannot imply artifact promotion, stage completion, validity, verification, or effect settlement |
| STATE-004 | Open blockers prevent exactly the affected transitions and can clear only through their frozen resolution rule |
| STATE-005 | Mission close has no active lease, dispatchable intent, ambiguous effect, unsealed handoff, or unresolved integrity incident |
| EFFECT-001 | Effect identity binds exact payload, destination, adapter, grant, budget, idempotency, and reconciliation profile before dispatch |
| EFFECT-002 | `completion_unknown` cannot become not-applied or trigger retry without admissible independent reconciliation |
| EFFECT-003 | Reconciliation records process and leaves settlement polarity as applied/not-applied with evidence; ambiguity history remains |
| EFFECT-004 | `external_effect.authorized` has the same commit/command binding and exact reservation set as its `authority.grant_use_reserved` cohort; it carries no dispatch consumption |
| EFFECT-005 | `external_effect.started` has the same commit/command binding and exact reservation/use set as `authority.grant_used(consumption_point=dispatch_claim)`; no provider call precedes that commit |
| EFFECT-006 | `external_effect.cancelled_before_dispatch` is reachable only from `authorized` with the same-batch terminal release/invalidation of every exact reservation, no grant use, and no inferred provider settlement |
| EFFECT-007 | `governed_processing_dispatch` authorize and start independently resolve exact WorkContract, authorized and current DataUseDecision set, non-dispatching exposure intent, provider-configuration observation, source/checkpoint frontier, purpose/recipient/provider/model/region/payload binding, and current policy/authority/resource digests; WorkContract alone grants nothing, all bindings/classes agree, and rejection commits no reservation/use/effect/spend cohort |

### Authority, rights, budget, and risk

| Rule | Predicate |
|---|---|
| AUTH-001 | Assignment/issuer chain is active and grants only the named role/action under the root manifest |
| AUTH-002 | Subject binding, command digest, target, protocol, manifest, purpose, data class, risk, resources, methods, destination, time, uses, and concurrency are within grant scope |
| AUTH-003 | Delegation is a strict subset on every scope dimension and remaining depth |
| AUTH-004 | Quorum contains the required number of distinct effective principals; aliases/shared credentials do not count twice |
| AUTH-005 | Producer/verifier/outcome/publication/safety/execution overlap obeys `AUTHORITY_MATRIX.md` and the mission independence profile |
| AUTH-006 | `authority.grant_use_reserved`, typed `authority.grant_use_reservation_released`, `authority.grant_used`, exhaust, expiry, and revoke facts conserve bounded capacity; domain-commit uses are atomic, dispatch-claim uses consume one exact active reservation, and no terminal reservation is consumed or restored twice |
| POLICY-001 | PolicyDecision is generated by the deterministic admission kernel from the exact canonical request and retained policy input/frontier; caller-supplied policy-decision identity or result is rejected |
| POLICY-002 | Policy registry snapshot, bundle, rules, engine build/configuration, controlled time, root/checkpoint/aggregate frontier, input schema/bytes, and reference-set digests resolve and match; missing, timeout, engine error, conflict, or unsupported input is `indeterminate`, never allow |
| POLICY-003 | `allow` satisfies the exact rule semantics and every mandatory typed obligation is enforced at its named commit/dispatch/post-effect point; PolicyDecision itself is neither assignment nor grant |
| ADMISSION-001 | CommandContractRecord selects the exact evidence profile; the AdmissionEvidenceBundle contains every required stage/evidence family, exactly one terminal disposition, explicit later `not_run_due_to_prior_failure`, and no undeclared evidence that changes the decision |
| ADMISSION-002 | Receipt, event cohort, PolicyDecision, ValidationResults, reference/currentness results, authority/grant/resource decisions, controlled frontier, and final disposition bind one command/request/evidence-bundle identity; replay reproduces the decision or fails closed |
| ADMISSION-003 | The bundle's evidence index is unique by `record_id`; every stage `evidence_record_id` resolves to exactly one indexed record and digest, every decisive indexed record is cited by an applicable executed stage, and no unreferenced record can influence the disposition |
| ADMISSION-004 | The evidence profile fixes the canonical twelve-stage coverage and required evidence families for the exact command/result branch; `pass`, `fail`, `indeterminate`, `not_applicable`, and `not_run_due_to_prior_failure` satisfy the profile's applicability and requiredness rules without optional evidence laundering a required failure |
| ADMISSION-005 | The first fail/indeterminate stage is the terminal stage, every later stage is explicitly not-run, accepted/noop contains no failed/indeterminate/not-run stage, and receipt result, event cohort, PolicyDecision, bundle reason, and terminal disposition agree exactly |
| RIGHTS-001 | Source license/basis permits the exact acquire/process/model-expose/retain/train/disclose purpose, recipient, region, and duration |
| RIGHTS-002 | Tombstone/deletion/legal hold preserves allowed lineage without retaining or exposing prohibited bytes |
| BUDGET-001 | Estimated, reserved, attempted, observed, billed, refunded, and settled amounts are separate and dimensionally compatible |
| BUDGET-002 | Every resource vector has unique registered dimension keys; execution classes, each currency in minor units, and deterministic/compute/expert/physical/safety verification capacity are non-fungible, with cross-resource conversion and dimension compensation forbidden |
| BUDGET-003 | Reservation creation binds the exact current budget head, subject, unit profile, estimate, ceiling, expiry, and complete start cohort; componentwise estimate does not exceed ceiling, and ceiling does not exceed available capacity |
| BUDGET-004 | Claim is legal only from active and commits with the exact work/effect/verification start cohort; it moves the full ceiling to claimed hold and leaves attempted/actual/billed/refunded use unobserved |
| BUDGET-005 | Release and expiry are legal only before claim and return the exact ceiling. Crash, recovery, timeout, missing callback, `completion_unknown`, cancellation after claim, or absent usage evidence cannot reduce a claimed hold |
| BUDGET-006 | Usage observations keep attempted, actual, billed, and refunded axes separate; observed requires a vector, missing/unavailable forbids a vector, and neither missing nor unavailable is interpreted as zero |
| BUDGET-007 | Settlement is legal only from claimed and references the exact required observations. Money proves `net=billed-refunded` with `refunded<=billed`; non-money proves `net=actual`; every component proves `net=reserved_consumed+overage` and `ceiling=reserved_consumed+unused`, then and only then the hold becomes zero |
| BUDGET-008 | Global reducer conservation matches every child transition to the budget head: reserve removes the ceiling from availability, pre-claim terminal returns it once, settlement returns only unused capacity, committed use remains consumed, and overage remains an explicit breach/liability |
| BUDGET-009 | Verification assignment/reservation, `verification.started`/claim, observation, and settlement bind the same exact five-dimensional demand/capacity basis and cohort; no scalar trust score or compute surplus substitutes for a required dimension |
| RISK-001 | Required safety/data/resource/execution/publication gates and isolation tier meet or exceed the declared action/data risk; undefined classification denies |

### Scientific validity and claims

| Rule | Predicate |
|---|---|
| SCI-001 | Confirmatory protocol was frozen before prohibited exposure; otherwise the affected branch is prospective exploratory/invalid according to the registered rule |
| SCI-002 | Required baselines, controls, falsifiers, denominators, splits, exclusions, and artifacts are present and valid |
| SCI-003 | A determined scientific outcome requires `scientific_validity=valid`, no affected operational blocker, a compatible measurement disposition, and the frozen consequence rule |
| SCI-004 | `null_result` specifically requires `valid_measurement`; `no_valid_measurement`, infrastructure failure, rights blocker, or invalidity cannot satisfy it |
| SCI-005 | Causal, safety, transport, replication, value, and physical claims satisfy their specialized method/adapter gate; a generic claim schema cannot waive it |
| VER-001 | Verification status, replay level, relation vector, identities, exposures, conflicts, known-bad results, and derived profile are mutually consistent |
| VER-002 | Every `separate_required` independence dimension is observed as sufficient under the mission profile; `unknown` fails |
| VER-003 | `confirmed` is forbidden when a required dimension fails/indeterminate or any known-bad fixture is accepted/errors under a fail-closed profile |
| CLAIM-001 | Claim type, scope, text, outcome, uncertainty, evidence, proposal, adjudication, and verifier refs cannot exceed the frozen mission surface |
| CLAIM-002 | Eligible claim requires a determined admissible adjudication and all mission-required verification runs; an ineligible/retraction version has no eligible language |
| CLAIM-003 | Correction/retraction has a valid supersession edge, reason evidence, dependency invalidation, and no mutation of earlier bytes |

### Publication and projections

| Rule | Predicate |
|---|---|
| PUB-001 | Manifest references exact eligible claim versions and a complete evidence package at one ledger position |
| PUB-002 | Rights, privacy, safety, security, contributor, wording, audience, channel, embargo, redaction, and grant decisions all bind the exact payload digest |
| PUB-003 | Claim-version compilation/eligibility, request, decision, manifest sealing, effect authorization, dispatch, receipt, settlement, correction, and withdrawal are distinct facts in legal order |
| PUB-004 | `released` requires both `external_effect=confirmed_applied` and an independent observation that the exact sealed bytes are visible at the intended channel, followed by the canonical release-settlement consequence over both; timeout, 2xx, visibility alone, or application alone is insufficient |
| PROJ-001 | Projection declares exact source position/freshness and cannot authorize, adjudicate, or publish |
| PROJ-002 | Unknown/stale/unavailable/withheld/zero and supported/null/invalid/blocked/corrected/retracted remain distinguishable in every registered projection |
| PROJ-003 | Correction, retraction, quarantine, rights change, and invalidation reach every dependent view/package under the declared propagation objective |

## Evaluation order and atomicity

Before semantic validation, generic ingress bounds and the minimal selector perform historical-receipt or active-admitted-member resolution. They do not parse an unbounded generic payload, accept caller-selected activation, resolve a handler for reserved vocabulary, or create canonical state. A pre-envelope refusal is operational/security evidence only. Exact historical retry returns its immutable receipt; changed reuse references but never replaces it.

Pre-transaction checks on a newly bound admitted envelope may read external bytes only to produce an immutable validation/materialization proof. The canonical command transaction performs no network, model, filesystem, scheduler, or object-store operation. It rechecks exact registered identities, current state, grants, budgets, and the rule-set version before atomically committing the one receipt, event batch, authority/resource changes, aggregate heads, and outbox.

Rules whose inputs can change between preflight and commit must run or be revalidated inside the transaction from canonical data. An external validation report never freezes a mutable grant, budget, blocker, or ledger position.

## Determinism, numerical methods, and disagreement

- Rule implementations receive explicit clock, randomness, locale, unit registry, numerical tolerance, and reference-set inputs.
- Floating-point-sensitive rules use a registered algorithm/tolerance and reference vectors; exact-decimal rules never coerce through binary float.
- A rule timeout, crash, unsupported method, or disagreement is `indeterminate`, not pass.
- Two independent implementations are required for canonicalization/digest and high-consequence claim rules before those paths are accepted.
- If implementations disagree, preserve both result packages, block the affected command, and invoke the registered resolution authority. Never majority-vote over validators.

## Adversarial trace format

Each semantic trace should contain:

```text
trace ID and purpose
initial event streams/heads and object/reference set
controlled time and policy/root/rule registry digests
command and expected canonical request digest
expected per-layer rule results
expected accepted/rejected/indeterminate command result
exact expected event batch or assertion that no domain event commits
expected authority/resource/lease/effect state
expected projection/claim/publication consequence
minimal mutation that turns the positive trace into the known-bad trace
```

Required trace families include the semantic gaps already demonstrated by structural fixtures: frame/decompression limit before selector; unknown/reserved selector with zero envelope/receipt/domain work; fake null-schema/null-handler member; caller-selected activation; exact retired-command replay under historical semantics; changed command-ID reuse with no second receipt; reversed time; reversed/unit-incompatible interval; event/payload mismatch; aggregate mismatch; invalid batch index; all roles assigned to one principal where separation is required; verifier identical to producer; impossible independence profile; publication expiry before seal; null from no valid measurement; wrong/future registry activation; registry/member metadata mismatch; digest-scope recursion; incompatible C0 bundle; and stale/revoked governed-processing data use with a zero-effect cohort.

## Acceptance rule

This constitution remains proposed. Candidate rule/result schemas and structural
known-bad fixtures now exist, but they are not frozen and do not satisfy the
remaining acceptance conditions:

- rule registry and validation-result schemas are independently reviewed and frozen;
- every founding rule has positive, negative, boundary, and metamorphic traces;
- the exact dependency-closed Gate A admitted command set, selector/refusal boundary, generated envelope, registry, and handler-set equality are independently reproduced;
- command/event reducers reference the exact rules and consequences;
- two independent implementations agree on canonicalization and selected critical rule vectors;
- bounded concurrency models cover grant, lease, protocol-exposure, artifact, verifier, and publication races;
- statistical/security/domain reviewers close critical/high findings; and
- the operator accepts the exact candidate commit.

Passing the current structural schema suite does not satisfy any of these semantic obligations.
