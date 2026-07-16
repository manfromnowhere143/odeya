# ADR 0026: Close the lifecycle guard evidence gaps in dependency order

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security, recovery
- Gate effect: removes the ADR 0025 evidence blocker from PRQ-006 and PRQ-007
  and from the vocabulary half of PRQ-008; closes no finding, admits no member,
  and accepts no Gate A row

## Context

ADR 0025 measured which lifecycle guards have a known-bad proof and found 24 of
69, a denominator ADR 0027 later corrected to 71. Three prerequisite findings
named properties among the unproved ones: the
protocol origin materializing version 1 from absence (PRQ-006), the data-use
grant being single-use at one atomic commit (PRQ-007), and the exact five-state
WorkLease vocabulary that is law 40 of the state model (PRQ-008).

Those findings were therefore blocked on evidence that did not exist, not on a
decision. That distinction matters: an evidence blocker is closable without the
operator, and leaving it uncorrected would have kept work queued behind a
profile decision it never actually depended on.

## Decision

Fill the gaps for the three named models, in the dependency order the closure
plan already fixes, without changing any contract.

Each known-bad trace breaks exactly one field of the retained safe reference for
its model, so the guard under test is the reason the trace is refused rather
than a side effect. Every variant was probed against the exact committed checker
before retention: a variant whose target refusal is absent proves nothing, and a
variant that co-fires cannot attribute the refusal to its guard. All 24 isolate
to exactly one error.

One trace is shaped deliberately. `work-lease-bad-does-not-start-unleased`
carries an empty step list, because a wrong start state otherwise cascades into
transition and declaration errors, and a trace refused three ways does not prove
which guard did the work.

Coverage after this decision, measured by mutation rather than asserted:

| model | before | after |
| --- | ---: | ---: |
| `authority_grant_trace_errors` | 4/11 | 11/11 |
| `protocol_origin_errors` | 3/12 | 12/12 |
| `data_use_cohort_errors` | 4/11 | 11/11 |
| `work_lease_trace_errors` | 2/8 | 8/8 |
| `work_lease_record_candidate_errors` | 4/29 | 4/29 |

Four of five auditable models are now guard-complete: 46 of 71, from 24.
The denominator is 71, not the 69 this decision originally reported; see
ADR 0027.

## Non-decisions

This decision does not:

- close PRQ-005, PRQ-006, PRQ-007, or PRQ-008. Each additionally requires an
  independently reproduced verdict that the producing agent cannot supply for
  its own change, and PRQ-008 retains its identity blockers — an unissued
  `canonical-work-lease` candidate, no admitted WorkIntent, and no assignment
  cohort — which no amount of guard coverage addresses;
- prove any guard is correct. A guard is now exercised; whether what it enforces
  is right is a separate question these traces cannot answer;
- close the 25 remaining `work_lease_record_candidate_errors` gaps, which are
  the largest single block of unproved guards left in this suite;
- measure `identity_map_mutation_errors`, `schema_contract_errors`, or the six
  suites that assert refusal without attribution across 229 known-bad cases; or
- change any transition table, state vocabulary, event identity, schema byte, or
  the 43/60/25/11 first-slice boundary.

## Consequences

PRQ-006 and PRQ-007 no longer carry an evidence blocker, and PRQ-008's
vocabulary claim is evidenced for the first time. Their closure records are
corrected to say so, because a stale "blocked on absent evidence" is as
misleading as the original silence.

The remaining 23 unproved guards are concentrated in one model, and they are the
most consequential ones left: they govern blocked-candidate status, fabricated
identity, execution-authority claims, the five-role assignment order, reservation
frontier claim/settlement separation, and the refusal to let a lease transition
claim ResourceLedger authority. Several are precisely the refusals that keep the
first slice fail-closed. None is proved today.

Filling them is the next lifecycle unit. It is larger than this one because that
model validates a retained fixture rather than a synthetic subject, so each
variant must break a real candidate record without making it structurally
invalid for an unrelated reason.
