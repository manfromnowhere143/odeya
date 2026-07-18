# ADR 0074: Publication evidence audited across history, not one commit at a time

- Status: Executed; records a measured gap in published history
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: an operator-side audit reports, for any commit range,
  which commits lack rehearsal evidence bound to their exact SHA

## The question the gate cannot answer

ADR 0072's publication gate refuses an unrehearsed `HEAD`. That is one
commit at a time and only from the moment it existed. It says nothing
about the history already published — commits released before the gate,
or through the plain `git push` that still exists beside it.

`scripts/ci/audit-publication-evidence.py` answers the whole-history
question: for every commit in a range, is there a retained manifest that
binds that exact SHA and claims no canonical scientific status?

## What it measured

Every commit this session published — **24 of 24** — has evidence bound
to its exact SHA, including the one published out of order, whose
rehearsal completed and passed afterward (ADR 0072).

Across the branch's full history the number is **67 of 76**. Nine
commits, all predating this session, have no retained evidence: the
Gate A contract-closure and checkpoint tranche, the recovery-bootstrap
and handoff-anchor commits, and the repository-release gating commit.
Their absence is not evidence of a defect in them — evidence lives
outside the repository by design (ADR 0047) and older rehearsals were
retained under different paths or not at all — but it is exactly the
kind of gap that goes unnoticed when each commit is checked alone.

The audit is operator-side and cannot run in CI, because the evidence it
reads is deliberately outside the published repository. A clean result
is a statement about this machine's retained evidence, not about the
world, and the tool says so.

## Boundary

The audit proves a manifest exists and binds the commit; it does not
re-run the rehearsal, so it cannot detect a manifest that was retained
without its checks passing — only re-measurement can, which is what the
rehearsal itself is. Nothing here is an accountable review
determination, an admitted member, or Gate A acceptance.
