# ADR 0030: Statement coverage is not condition coverage

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security
- Gate effect: retracts ADR 0028's claim that a guard cannot be weakened without
  detection, and bounds every coverage figure this mission has published to
  statement reachability; closes no finding and accepts no Gate A row

## Context

ADR 0025 built a mutation audit to answer whether a lifecycle guard has a
known-bad proof, because reading could not. ADR 0028 reported 75 of 75 and
concluded that no guard among those models "can be removed, weakened, or
silently lost without the suite failing and the rehearsal refusing the record".

Independent adversarial review confirmed the arithmetic, confirmed every trace as
real and singly-attributed, and refuted the strength of the conclusion.

## Finding

The audit disables a guard by deleting its refusal **statement**. That is
equivalent to forcing the guard's condition to `False`. It establishes that the
statement is reachable by some retained case. It establishes nothing about
whether each **condition** inside that guard is exercised.

The demonstration is one line, reproduced against the exact committed bytes:

```text
-    if record.get("canonicalization_profile_ref") is not None
-            or record.get("canonical_digest") is not None:
+    if record.get("canonical_digest") is not None:
```

A fabricated canonicalization profile is now admitted — a fail-closed property
PRQ-008 turns on. The result: the suite passes, `--write` reports full coverage
unchanged, and `--check` reports "record reproduces exactly". The regenerated
record's complete diff against the retained one is a single line,
`subject_sha256`. Every guard still reports `proved: true`.

Across the five models, review measured **20 of 32 single-disjunct removals** and
**16 of 19 helper-predicate conjunct removals** surviving with the suite green —
including every `DIGEST.fullmatch` check and the entire nested `artifact_ref`
validation inside `valid_record_ref`, `valid_artifact_ref`, and
`valid_versioned_identity`. Thirty-six conditions can be deleted while the
apparatus reports success.

Two consequences follow, and both retract something this mission published.

The hash pin is a **change**-detector, not a **weakening**-detector. It fires on
any edit to the checker and is cleared by regenerating the record. ADR 0025
introduced it as forcing guards to be re-proved; re-proving a weakened guard
succeeds.

And the masking mechanism has a second form. ADR 0028 named the closed mutation
vocabulary: a case cannot reach a field the vocabulary does not touch. Review
found the dual. `first-slice WorkLease release forgets the claimed reservation`
has one naming case, and that case sets both of its disjuncts at once, so neither
is independently exercised. A **conjoined known-bad case** bounds what evidence
can exist exactly as silently as a closed vocabulary — the case looks like proof
of the guard, and is proof only of the guard's disjunction.

## Decision

Bound the claim to what was measured, everywhere it was published.

- Retract "weakened" from ADR 0028's consequence. Removal is caught; weakening
  is not.
- Restate every coverage figure this mission has produced — 24/71, 46/71, 75/75,
  89/139 — as **statement reachability**, not condition exercise. They are not
  wrong; they measure less than their wording implied.
- Correct ADR 0028's two counting errors found by review: six cases co-fire, not
  five; and twenty-three cases break exactly one field while six exercise the
  mutation vocabulary itself.
- Record condition-level coverage as the next lifecycle unit rather than claim it.
  The method exists — mutate each disjunct and each conjunct rather than the
  statement, which is the MC/DC question — and it is a strictly larger audit than
  the one built here.

No contract, vocabulary, event identity, schema byte, trace, or boundary changes.
The 89 proved verdicts stand; only their meaning is narrowed.

## Non-decisions

This decision does not:

- implement condition-level mutation, or claim any of the 36 conditions is wrong.
  It claims only that nothing would notice if they were deleted;
- weaken the existing audit, which remains sound for what it measures: removal
  and silent loss of a whole guard;
- close any PRQ finding or supply an independently reproduced verdict; or
- change the retained record, whose numbers are correct under the narrowed
  reading.

## Consequences

The honest summary of this mission's guard work is now: of 139 refusal statements
across six functions, 89 are reachable by a retained known-bad case, 50 are not,
and the conditions inside all 139 are unmeasured. That is materially less than
"75/75, guard-complete", which is what was published two commits ago.

The pattern is now four for four. Every coverage figure this lane published as
fact was wrong in the same direction: 69 omitted two `return` guards; 75 omitted
a 64-guard delegate; "guard-complete" omitted condition coverage entirely. Each
was found by an independent reviewer told to refute, never by the tool, the gate,
the validator, or the author. The tool built to prove that green does not mean
guarded has now been green and unguarded three separate ways.

The generalizable lesson is not about this suite. A measurement defends only the
question it was pointed at, and its wording will quietly promote itself to the
larger question nobody asked. `ARCHITECTURE_STATUS.md` says "No row is passed";
this work is a reminder of how much care that sentence is doing, and how easily a
confident number sitting beside it would undo it.
