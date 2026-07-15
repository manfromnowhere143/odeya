# Semantic Validation Constitution

Status: proposed architecture, 2026-07-15. JSON Schema fixtures prove structural shape only. This document defines the relational and scientific rule layer that must be frozen and independently tested before Gate A.

## Validation pipeline

Validation is ordered and monotonic. A later layer may add failures or narrower conditions; it cannot erase an earlier failure.

```text
V0 byte/parser safety
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

Each layer returns a retained `ValidationResult`; none mutates the submitted object. Repair creates a new candidate version and a new result.

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

## Founding rule catalog

The IDs below are candidate stable meanings. Gate A freezes their exact predicates and fixtures.

### Representation and time

| Rule | Predicate |
|---|---|
| REP-001 | Input has valid UTF-8, no duplicate keys, no forbidden numeric form, and no silent Unicode normalization |
| REP-002 | Canonical bytes recompute to the declared digest under the named profile/schema namespace |
| REP-003 | Decimal strings, precision/scale, units, ratios, intervals, distributions, and missingness use registered semantic types |
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

### Authority, rights, budget, and risk

| Rule | Predicate |
|---|---|
| AUTH-001 | Assignment/issuer chain is active and grants only the named role/action under the root manifest |
| AUTH-002 | Subject binding, command digest, target, protocol, manifest, purpose, data class, risk, resources, methods, destination, time, uses, and concurrency are within grant scope |
| AUTH-003 | Delegation is a strict subset on every scope dimension and remaining depth |
| AUTH-004 | Quorum contains the required number of distinct effective principals; aliases/shared credentials do not count twice |
| AUTH-005 | Producer/verifier/outcome/publication/safety/execution overlap obeys `AUTHORITY_MATRIX.md` and the mission independence profile |
| AUTH-006 | Reserve/use/release/exhaust/revoke facts are transactionally consistent; no command commits without consumption and no rollback leaks a reservation |
| RIGHTS-001 | Source license/basis permits the exact acquire/process/model-expose/retain/train/disclose purpose, recipient, region, and duration |
| RIGHTS-002 | Tombstone/deletion/legal hold preserves allowed lineage without retaining or exposing prohibited bytes |
| BUDGET-001 | Estimated, reserved, attempted, observed, billed, refunded, and settled amounts are separate and dimensionally compatible |
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
| PUB-004 | `released` requires independent observation that the exact sealed bytes are visible at the intended channel; timeout/2xx alone is insufficient |
| PROJ-001 | Projection declares exact source position/freshness and cannot authorize, adjudicate, or publish |
| PROJ-002 | Unknown/stale/unavailable/withheld/zero and supported/null/invalid/blocked/corrected/retracted remain distinguishable in every registered projection |
| PROJ-003 | Correction, retraction, quarantine, rights change, and invalidation reach every dependent view/package under the declared propagation objective |

## Evaluation order and atomicity

Pre-transaction checks may read external bytes only to produce an immutable validation/materialization proof. The canonical command transaction performs no network, model, filesystem, scheduler, or object-store operation. It rechecks exact registered identities, current state, grants, budgets, and the rule-set version before atomically committing the receipt, event batch, authority/resource changes, aggregate heads, and outbox.

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

Required trace families include the semantic gaps already demonstrated by structural fixtures: reversed time, reversed/unit-incompatible interval, event/payload mismatch, aggregate mismatch, invalid batch index, all roles assigned to one principal where separation is required, verifier identical to producer, impossible independence profile, publication expiry before seal, and null from no valid measurement.

## Acceptance rule

This constitution remains proposed until:

- rule registry and validation-result schemas are frozen;
- every founding rule has positive, negative, boundary, and metamorphic traces;
- command/event reducers reference the exact rules and consequences;
- two independent implementations agree on canonicalization and selected critical rule vectors;
- bounded concurrency models cover grant, lease, protocol-exposure, artifact, verifier, and publication races;
- statistical/security/domain reviewers close critical/high findings; and
- the operator accepts the exact candidate commit.

Passing the current 37 structural schema cases does not satisfy any of these semantic obligations.
