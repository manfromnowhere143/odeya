# First-slice resolution adversarial checker

This directory contains a bounded, architecture-only checker for
`architecture/first-slice-admission-resolution-candidate.json`. It exercises
the prospective C1-C8 choices as abstract records and traces. It is not an
engine, scheduler, reducer implementation, registry activation, or runtime
authorization.

Run it from the repository root:

```bash
python3 tests/first-slice-resolution/check.py
```

The checker first verifies that the reissued 0.2 inventory exposes the bounded
candidate boundary: exact command/event/aggregate partitions, single-use
ordered authority slots, one `Verification` reducer, the nonrecursive P0
prerequisite, and C5/PRQ-009 as explicitly unresolved and blocking. It then
evaluates safe reference cases and known-bad cases for:

- C1 complete typed resource settlement without partial or inferred-zero
  accounting;
- C2 atomic claim supersession and dependency invalidation;
- C3 atomic legal run-validity and measurement-disposition pairs;
- C4/C6 exact ordered grant cohorts and the preclaim race;
- C5 local start, invalidation, release, and expiry transitions, plus the
  prospective exact 13-event `verification_assign_local` cohort and its
  WorkIntent, WorkContract, current-data-use, sandbox, reservation, lease,
  grant, command/receipt/activation/commit binding obligations;
- C7 sole canonical verification reducer authority; and
- C8 current, unambiguous, activation-independent P0 plus the later outer
  activation's exact P0-digest binding.

Every adversarial case is declared with an expected rejection. The process
exits nonzero if any known-bad case is accepted, any safe reference is
rejected, required coverage disappears, or the candidate inventory no longer
satisfies the bounded assumptions used by the cases.

Printed fixture digests use a deterministic, sorted Python JSON encoding only
to identify this retained test run. They are explicitly non-normative and are
not Odeya canonicalization-profile evidence.

A pass is only evidence that these finite fixtures agree with this checker. It
does not create immutable registry members, P0, an EngineContractRoot, an
activation, a proof of implementation, independent review, Gate A acceptance,
or permission to start runtime work. In particular, the accepted prospective
assignment case specifies what future closure must prove; it does not claim
that the current unresolved WorkIntent or one-event assignment fixture is
constructible, admitted, or dispatchable.
