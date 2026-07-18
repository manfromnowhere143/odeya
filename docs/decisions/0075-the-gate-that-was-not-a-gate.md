# ADR 0075: The gate that was not a gate; round four responses

- Status: Executed; retracts ADR 0072's central claim
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: a real pre-push hook, a validated rule pointer, the
  ablation audit wired into remote CI, and nineteen dead mutations
  removed from the corpus

## The claim that was false

ADR 0072 said the sequencing law had been "made mechanical" by
`scripts/ci/push-rehearsed-head.sh`. Independent review refuted it in
one line: **plain `git push` ignores the helper entirely.** No hook was
installed, `core.hooksPath` was unset, and the script was referenced only
by the handoff and its own ADR. It was convention wearing a gate's name —
the precise failure ADR 0072 was written to end, reproduced inside the
fix for it.

`.githooks/pre-push` is the mechanism that claim required. It refuses any
push to `main` whose commit has no retained manifest binding that exact
SHA, rejecting a manifest that binds a different commit, claims canonical
scientific status, or carries no plausible file inventory. The reviewer's
exact bypass was replayed: a plain `git push` of an unrehearsed commit is
now refused at the hook.

Three residues stay explicit rather than implied away. The hook is local
configuration — a fresh clone without `core.hooksPath` set has no
protection. The reviewer's forged two-key manifest still satisfies the
shape check, because the hook trusts retained evidence rather than
re-deriving it. And `pass_dispositions` in the manifest writer is a
hardcoded constant, not a measurement, which the manifest presents as
though it were one. That last item is a defect in the evidence format
itself and is the next unit.

## The other three findings

**The rule pointer was decoration.** The audit read only the trailing
integer, so a case declaring `/this/pointer/is/not/a/rule/at/all/7`
passed. The pointer is now validated for shape, range, agreement with the
case's own name, and uniqueness per schema; the reviewer's forged pointer
is refused.

**The audit ran in no workflow.** Re-measurement existed only in the
operator-side rehearsal, so remote CI could not detect a shifted rule
index or a falsified record. It now runs in the schema-contracts job,
which has the hash-locked environment it needs.

**The corpus shipped generator residue.** Nineteen mutations across
sixteen cases were dead on arrival — overwritten by a later mutation on
the same path — and are removed; all 152 still isolate their rule. The
reviewer also measured that 42 cases have base fixtures already
satisfying their rule's `if`, so ADR 0071/0073's account of "satisfy the
`if` from its own discriminators" overstates what those cases do: they
test a consequent violated while the antecedent already holds, which is a
real test of the implication but exercises no cross-field transition.
That correction belongs to the record, not to a footnote.

What survived: the two-sided ablation test itself is structurally sound —
`refused_without == False` means every error under the full schema is
attributable to the deleted subschema, so a case cannot bind to an
unrelated error and still pass. The index misalignment hypothesis was
disproven empirically: inserting a rule makes all 152 cases fail loudly,
and no case false-passes by ablating a neighbour.

## Boundary

A hook is not a server-side rule; a repository-side protection would need
branch rules on the remote, which is publication authority this session
does not hold. Nothing here is an accountable review determination, an
admitted member, or Gate A acceptance.
