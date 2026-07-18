# ADR 0078: The repository measures 23% of its own guards

- Status: Measurement executed and published; subtractive, closes nothing
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: none yet — this records the size of the gap and corrects
  three stale prerequisite blockers

## What was measured

Every refusal statement in every suite, counted by AST:

| suite | refusal statements | mutation audit |
|---|---|---|
| lifecycle-closure | 169 | yes |
| first-slice-resolution | 119 | none |
| constitutional-construction | 82 | none |
| projection-contracts | 74 | none |
| mathematical-contracts | 74 | none |
| physical-contracts | 51 | none |
| cognitive-contracts | 49 | none |
| work-intent-reference-resolution | 48 | none |
| nine smaller suites | 51 | none |

**717 refusal statements; 169 proved to fire; 548 never measured.**

ADR 0025 established that a guard without a known-bad proof has no
evidence, whatever any trace, tag, or document claims, and ADRs 0026
through 0077 drove one suite from that state to 178 of 185 with
condition-level coverage on top. That work is sound and it covers
**23% of the repository's refusals**. The remaining 548 are in exactly
the state lifecycle-closure was in before it was measured: every one
could be deleted with its suite green, and nothing would notice.

This is not a new defect. It is the same defect, never looked for outside
the one suite where looking became a habit — the fourth time this
repository has found a denominator that was only as wide as where it was
pointed.

## Three stale prerequisite blockers corrected

While reading the closure record, three findings still carried evidence
blockers that measurement closed long ago: PRQ-006 ("only three of twelve
protocol_origin guards proved"), PRQ-007 ("only four of eleven
data_use_cohort"), and PRQ-008 ("twenty-three of twenty-seven
work_lease_record_candidate"). The retained coverage record reports
12/12, 11/11 and 34/34. Each closure text is corrected by appending the
measured citation rather than editing the history away; a stale "still
blocked" misleads exactly as much as the original silence, which is ADR
0026's standing rule. Their identity blockers are untouched and still
terminate in the operator's profile decision.

## What follows

A suite-agnostic mutation audit — the discipline of
`audit_lifecycle_guard_coverage.py` generalized to any refusal-bearing
checker — is the next unit, and it is the largest piece of unblocked
evidence work in the repository. It will publish more blindness before it
closes any, which is the only order that has ever worked here.

## Boundary

Nothing is closed by this ADR. The 23% figure is a measurement of
coverage, not of correctness: a proved guard is exercised, never shown to
enforce the right rule. Nothing here is an accountable review
determination, an admitted member, or Gate A acceptance.
