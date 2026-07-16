# ADR 0028: Complete the auditable lifecycle guard coverage

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security, recovery
- Gate effect: every guard in the five auditable lifecycle models now has a
  known-bad proof; closes no finding, admits no member, and accepts no Gate A
  row

## Context

ADR 0025 measured lifecycle guard coverage at 24 of 71 and ADR 0026 raised it to
46 by filling the models named by PRQ-006, PRQ-007, and PRQ-008. The remainder
sat in `work_lease_record_candidate_errors` at 4 of 29 — the largest and most
consequential block, governing blocked-candidate status, fabricated identity,
execution-authority claims, the exact five-role assignment order, reservation
claim/settlement separation, and the refusal to let a lease transition claim
ResourceLedger authority. Several are precisely the refusals that keep the first
slice fail-closed, and none was proved.

They were unprovable by construction, not by neglect. That model validates a
retained fixture and accepts only four named string mutations. Twenty-three of
its guards sit behind fields no named mutation touches, so no known-bad case
could reach them however it was written. A closed mutation vocabulary silently
bounds what evidence can exist.

## Decision

Widen what a case may express, without weakening any guard.

`work_lease_record_candidate_errors` now also accepts one bounded replace
operation — `{"op": "replace", "path": [...], "value": ...}` — the exact shape
`identity_map_mutation_errors` already uses in the same checker. This is the
established idiom, not a new mechanism. The four named mutations are retained
byte-for-byte, so every previously retained case is unchanged.

Twenty-nine known-bad traces were added: twenty-four breaking exactly one field
of the retained fixture, and five entering branches the others never reach — the
released fixture's claimed frontier, the non-origin version rule, and the expiry
pre-claim branch that neither retained fixture reaches without changing its
transition event. Every variant was probed against the exact checker before
retention.

Five co-fire with a neighbouring guard, and that is handled rather than hidden:
each case names its own guard through `expected_refusal_contains`, so removing
that guard fails the suite even though a second error survives. This is the
ADR 0024 binding doing the work it was added for.

Coverage, re-measured by mutation:

| model | ADR 0025 | now |
| --- | ---: | ---: |
| `authority_grant_trace_errors` | 4/11 | 11/11 |
| `protocol_origin_errors` | 3/12 | 12/12 |
| `data_use_cohort_errors` | 4/11 | 11/11 |
| `work_lease_trace_errors` | 2/8 | 8/8 |
| `work_lease_record_candidate_errors` | 4/29 | 33/33 |
| **total** | **24/71** | **75/75** |

The denominator grew from 71 to 75 because the bounded replace introduces four
hygiene guards of its own — a non-replace operation, an absent path, an
unresolvable path, and a non-integer list index. All four are proved. Widening
the vocabulary without proving its own refusals would have reintroduced the
defect this work exists to remove.

## Non-decisions

This decision does not:

- make the suite guard-complete. Five of six models are.
  `identity_map_mutation_errors` remains unmeasured, because it returns refusals
  directly and delegates to `schema_contract_errors`, which the audit cannot
  attribute. Unmeasured is not proved and is not zero;
- prove any guard is correct. Seventy-five guards are exercised; whether each
  enforces the right rule is a separate question no known-bad trace answers;
- close PRQ-005, PRQ-006, PRQ-007, or PRQ-008. Each requires an independently
  reproduced verdict the producing agent cannot supply, and PRQ-008 retains its
  identity blockers — an unissued `canonical-work-lease` candidate, no admitted
  WorkIntent, no assignment cohort — which coverage does not touch;
- complete `discover()`. It matches four refusal constructs; a fifth stays
  invisible to the audit and to both gates;
- measure `schema_contract_errors` or the six suites that assert refusal without
  attribution across 229 known-bad cases; or
- change any contract, transition table, state vocabulary, event identity, schema
  byte, or the 43/60/25/11 first-slice boundary.

## Consequences

Law 11 holds for these five models as a measured fact rather than an assertion:
no guard among them can be removed, weakened, or silently lost without the suite
failing and the rehearsal refusing the record.

The result should be read against how it began. This suite passed green
throughout, at every commit, while forty-seven of its guards were removable
without consequence — including properties three prerequisite findings turn on
and properties its own README asserted as established. Nothing in the repository
distinguished that state from this one. Only mutation did, and only after an
independent reviewer corrected the measurement twice.

The remaining lifecycle work is `identity_map_mutation_errors` and
`schema_contract_errors`, which need a different method than branch mutation
because their refusals are not attributable to a local branch. Beyond this
suite, the same question is unanswered for 229 known-bad cases in six other
suites. Nothing here is evidence about them.
