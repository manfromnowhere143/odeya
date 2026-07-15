# Orthogonal State Model

Status: proposed canonical vocabulary, 2026-07-15. Canonical events are facts; these states are deterministic projections at an exact ledger position.

The central rule is that operational progress, evidence validity, scientific outcome, claim maturity, replication, and publication are different axes. Odeya must never encode them in one status.

## State axes

### Mission aggregate

```text
admission: pending | admitted | deferred | declined | withdrawn
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

Exposure is an event history, not a mutable flag that can be cleared. An amendment derives its prospective consequence from exposure and method rules.

### Stage/work item

```text
readiness: pending | ready | blocked | completed
authorization: not_required | missing | active | expired | revoked | exhausted
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

### External effect

```text
settlement:
  not_intended | authorized | started | confirmed_applied |
  confirmed_not_applied | completion_unknown

reconciliation:
  not_required | pending | running | completed | failed | manual_review
```

Every externally consequential action, including publication, has an effect record and provider idempotency/reconciliation semantics.
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
status:
  not_requested | requested | running | confirmed | rejected |
  inconclusive | invalid | blocked | disputed
```

Verification status is attached to a verification run with an observed independence vector. Several runs can coexist; disagreement remains visible.

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
```

Grant state derives from immutable issue/use/revoke events and controlled time.

## Typed blockers

Do not turn `blocked` into a scientific state:

```text
Blocker {
  blocker_id
  mission_id
  scope_type: mission | protocol | stage | work_item | run |
              verification | claim | publication
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
| intake | proposal accepted by admission authority | orient | decision and origin record |
| intake | defer/decline/withdraw | closed | decision, reason, handoff if work exists |
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

## Stage transition algebra

```text
pending -> ready
pending -> blocked
ready -> blocked
blocked -> ready            only through a resolved blocker event
ready -> completed          only with required output and valid authority
```

Execution stages additionally require an active lease and attempt. A completed stage is immutable; correction or invalidation creates subsequent events and dependent-state changes.

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
- mission close versus active/ambiguous effects.

The model's counterexamples become transition fixtures. A model-check pass is not a proof of implementation correctness; it checks the frozen algebra.
