# ADR 0053: Mechanize condition-level lifecycle coverage; 48 of 87 conditions have no evidence

- Status: Measurement executed and retained; subtractive, not closure, not
  Gate A acceptance
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: adds the condition-level mutation audit, its retained
  record, a fifth cheap architecture-evidence gate, and a rehearsal
  re-measurement stage; publishes 48 conditions removable with the suite
  green

## Why this exists

ADR 0025 proved every guard statement reachable and ADR 0052 completed
that measurement at 160 of 160. ADR 0030 retracted the strength of both
in advance: statement mutation deletes a whole refusal, so it can never
see a weakened *part* of one. Deleting a single disjunct — admitting a
fabricated canonicalization profile — left the suite green and
regenerated a full-coverage record. Review measured that blindness by
hand across five models. Nothing mechanical measured it, which is the
same condition that let statement coverage sit unmeasured before ADR
0025.

## The measurement

`scripts/audit_lifecycle_condition_coverage.py` discovers, by AST, every
top-level member of a boolean chain that guards a refusal — `if` tests in
the ten audited models, boolean `return` chains in the three helper
predicates ADR 0030 measured by hand. Each member is removed one at a
time in an isolated copy and the suite runs; a condition is proved only
when its removal makes the suite fail. Detection is attributable in both
directions: a removed disjunct can only shrink the firing set (a
known-bad case is accepted or loses its declared guard), a removed
conjunct can only grow it (a case, including every safe reference,
collects a refusal it did not declare). A crash after removal is also
detection.

The result, measured in 28 seconds and retained at
`architecture/lifecycle-condition-coverage.json`: **39 of 87 conditions
proved; 48 removable with the suite green.** Among the unproved are
exactly the cases the handoff predicted: the fabricated-profile disjunct
in the WorkLease record fixture guard; both disjuncts of the conjoined
`first-slice WorkLease release forgets the claimed reservation` case,
which sets both at once and therefore proves only their disjunction; and
the helper predicates nearly whole — `valid_artifact_ref` 1/6,
`valid_record_ref` 1/8, `valid_versioned_identity` 1/5 — meaning almost
any structural field check inside a protocol reference could be deleted
undetected.

## What is counted but not audited, stated before the number is read

132 guarded tests have a single top-level condition: they have no member
to remove, their reachability is the statement audit's result, and their
false side is held by the safe references. Zero nested boolean groups
exist today; if one appears it is counted, not descended into. A
structural comparison over a dict is one condition regardless of field
count — field-level blindness inside structural expectations is real and
unmeasured. And the denominator is only as honest as discovery, the same
warning both prior audits carry.

## Enforcement

The record is pinned to the exact checker bytes.
`scripts/validate_lifecycle_condition_coverage.py` joins the default
validator as the fifth architecture-evidence check, enforcing digest and
arithmetic only — it cannot detect a consistently falsified record, and
says so. The exact-commit fresh-clone rehearsal gains a
`lifecycle-condition-coverage` stage that re-measures with `--check`,
which is the only real enforcement, mirroring ADR 0027. Coverage stage
logs are not evidence-manifest members — the guard-coverage log never
was either — so the manifest remains nineteen files; the re-measurement
is bound by the rehearsal passing as a whole. A draft of this ADR
asserted the manifest would grow to twenty files; the first rehearsal
measured nineteen and the claim is corrected here rather than silently,
because it was exactly the kind of unmeasured prediction this
repository forbids.

## Boundary

This tranche is subtractive: it closes nothing. The 48 unproved
conditions are the next lifecycle unit, closable the same way ADR 0026,
0028, and 0052 closed their predecessors — one case per condition, each
setting exactly the mutated part wrong while holding every sibling part
safe, which also dissolves the conjoined-case masking form. Condition
coverage is still not correctness; a proved condition is exercised, not
shown to enforce the right rule. The profile remains unissued, all
null/false authority boundaries hold, and Gate A acceptance remains
separate.
