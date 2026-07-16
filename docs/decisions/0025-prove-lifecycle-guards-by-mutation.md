# ADR 0025: Prove lifecycle guards by mutation and retain the coverage as evidence

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security, recovery,
  canonical identity
- Gate effect: measures and retains which lifecycle guards have a known-bad
  proof; establishes that PRQ-006, PRQ-007, and PRQ-008 cannot close on the
  current evidence; admits no member, closes no finding, and accepts no Gate A
  row

## Context

Law 11 requires every gate to have a known-bad proof that it fires. Nothing
mechanically enforced it, and no document measured it.

ADR 0024 established that a trace refused for an incidental reason proves
nothing about the guard it names, and bound each retained trace to its own
guard. That left a prior question unanswered: is a guard exercised by any trace
at all? A guard with no trace does not hide behind an incidental refusal. It has
no evidence whatsoever, which is the weaker position, and no amount of reading
the suite reveals it.

Reading cannot answer the question and neither can string matching. Refusal
messages interpolate their values, so a declared substring spans the
interpolation points, while a non-interpolated message is longer than the
substring that names it. A matcher inverts on one or the other. Three successive
matchers written for this audit each produced false results in different
directions before the approach was abandoned.

Mutation answers it directly. Disable exactly one guard and run the suite. If
the suite still passes, that guard has no evidence, whatever any trace, tag,
required-tag list, or document claims.

## Finding

Every `errors.append` branch of the five auditable lifecycle models was
disabled, one at a time, against an isolated copy. Of 69 guards, **24 are proved
and 45 have no known-bad proof**. ADR 0027 later corrected that denominator to
71: discovery matched only `errors.append` and never saw two `return [...]`
guards, both unproved. The corrected figures are 24 of 71 proved, 47 with no
proof:

| model | proved | guards |
| --- | ---: | ---: |
| `authority_grant_trace_errors` | 11 | 11 |
| `protocol_origin_errors` | 3 | 12 |
| `data_use_cohort_errors` | 4 | 11 |
| `work_lease_trace_errors` | 2 | 8 |
| `work_lease_record_candidate_errors` | 4 | 29 |

`identity_map_mutation_errors` returns refusal lists directly and delegates to
`schema_contract_errors`, so branch mutation cannot attribute its guards. Its
coverage is unmeasured, not proved, and is recorded as such rather than as zero,
because a silent zero reads as clean.

This lands on the prerequisite closure claims:

- PRQ-006 states that `protocol.frozen` creates version one from absence. Both
  `protocol origin is not explicitly from aggregate absence` and `protocol
  origin does not materialize version 1` have no known-bad proof.
- PRQ-007 states that a bounded `data_rights` grant use, decision, and
  exhaustion form one exact atomic cohort. `data-use decision must retain
  exactly one data_rights grant and use event` and `data-use grant is not
  single-use at domain commit` have no known-bad proof.
- PRQ-008 rests on the exact five-state WorkLease vocabulary, which is law 40 of
  the state model. `WorkLease canonical vocabulary is not the exact five-state
  sequence` has no known-bad proof.

Those three findings describe properties that no retained known-bad trace
exercises. They cannot be closed on this evidence.

## Decision

Retain the measurement as evidence and gate it:

- `scripts/audit_lifecycle_guard_coverage.py` discovers each guard by AST,
  disables each in an isolated copy, and records whether the suite fails without
  it. It refuses to report at all if the unmutated control does not pass. This
  decision originally claimed a guard therefore could not be silently omitted.
  That claim was false and ADR 0027 retracts it: discovery matched only
  `errors.append`, so two `return [...]` guards were never seen;
- `architecture/lifecycle-guard-coverage.json` retains every guard by name with
  its verdict and, where proved, the exact known-bad case that establishes it;
  and
- `scripts/validate_lifecycle_guard_coverage.py` gates the record in the default
  validator.

The measurement costs roughly ninety seconds and the gate costs one hash. The
record is therefore pinned to the exact checker digest: changing the checker
invalidates the record and forces its guards to be re-proved, while leaving the
checker alone is free. Appending one comment to the checker fails the gate, and
an arithmetically inconsistent record fails it.

This decision further claimed that retaining unproved guards by name stops one
from quietly losing its proof while the total stays flat. That is also false and
ADR 0027 retracts it: the cheap gate checks the checker digest and the record's
own arithmetic, and a consistently falsified record passes. Only re-measurement
detects it, which ADR 0027 wires into the exact-commit rehearsal.

The unproved guards are still retained by name rather than summarized, for
review rather than for enforcement.

## Non-decisions

This decision does not:

- close PRQ-005, PRQ-006, PRQ-007, PRQ-008, or any other finding;
- prove any guard is correct — coverage establishes only that a guard is
  exercised, never that what it enforces is right;
- measure `identity_map_mutation_errors`, `schema_contract_errors`, or the
  eleven other contract suites;
- claim the 45 unproved guards are wrong, only that nothing would notice if they
  were removed;
- supply an independently reproduced verdict for its own measurement; or
- admit a member, issue a digest, accept Gate A, or authorize runtime work.

## Consequences

Law 11 is now measured for one suite instead of asserted. A guard cannot be
added to a lifecycle model without the record showing whether anything proves
it, and a proof cannot be lost without the gate firing.

The immediate consequence is subtractive and should be read plainly: the
lifecycle closure suite has been passing green while 47 of its 71 guards were
unproved, and three prerequisite findings rest on properties among them. The
suite's own README asserts several of those properties as established. The
correct response is to fill the gaps in dependency order, beginning with the
guards named by PRQ-006, PRQ-007, and PRQ-008, and to state in the closure
record that those findings are blocked on evidence that does not exist yet
rather than on a decision.

The same audit should be extended to `schema_contract_errors` and to the six
suites that assert refusal without attribution across 229 known-bad cases. The
method generalizes; only the model list is suite-specific. Nothing here should
be read as evidence about those suites, which remain unmeasured.
