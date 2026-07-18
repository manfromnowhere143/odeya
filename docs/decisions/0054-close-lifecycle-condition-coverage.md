# ADR 0054: Close lifecycle condition coverage at 87 of 89; two disjuncts are invariant-coupled

- Status: Executed by measurement; the residue is retained deliberately,
  not pending
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: every closable condition in the audited lifecycle models
  and helper predicates now has a known-bad proof; the two unprovable
  disjuncts are named, explained, and kept

## The closure

ADR 0053 measured 48 of 87 conditions removable with the suite green.
This tranche adds 46 condition-closure cases — each setting exactly the
mutated part wrong while holding every sibling part safe — plus two
statement proofs for the new vocabulary guards below. Every case was
dry-run against its real model checker before retention. The suite holds
230 cases: 14 safe references and 216 attributed known-bad.

Re-measurement: **87 of 89 conditions proved.** The helper predicates
are complete (`valid_artifact_ref` 6/6, `valid_record_ref` 8/8,
`valid_versioned_identity` 5/5), so every structural field check inside
protocol references now has a case that dies with it. The conjoined
release/claim case is dissolved: each disjunct of `first-slice WorkLease
release forgets the claimed reservation` has its own independent proof.
The fabricated-canonicalization-profile disjunct ADR 0030 first used to
demonstrate the blindness is proved. Statement coverage was re-measured
alongside and stands complete at 161 of 161.

## The fourth recurrence, and the widening

The expiry-branch conditions could not be reached: proving them needs a
fixture in the expiry branch with exactly one reservation field wrong,
and the retained fixtures are an acquisition and a release. One bounded
replace cannot both move the fixture into the branch and break the
field — a single replace is itself a closed vocabulary one level up.
This is the fourth recurrence of the defect ADR 0028, ADR 0031, and ADR
0052 each fixed one level down. The WorkLease harness now also accepts
an ordered list of bounded replaces; the single-replace form is
unchanged, the list form carries its own hygiene guards (empty list,
non-replace entry), and both new guards are proved — the statement
denominator grew 160 to 161 accordingly.

## The residue, kept on purpose

Two disjuncts of the exhaustion guard —
`uses != max_uses` and `not pending_exhaustion` in
`if state != "active" or uses != max_uses or not pending_exhaustion` —
remain unproved and cannot be proved by any JSON trace. The fold
maintains `pending_exhaustion ⟺ uses == max_uses` while the grant is
active: `pending_exhaustion` is set exactly when a use reaches
`max_uses` and cleared only by exhaustion, which leaves the active
state. Whenever the first disjunct is false the other two agree, so
removing either alone changes no reachable refusal. Each is redundant
given the other plus the invariant.

They are retained anyway, as deliberate defense in depth: the invariant
lives in the fold's assignments, and a future edit that breaks it would
make exactly one of these disjuncts load-bearing. Simplifying the guard
would shrink the denominator to 87 of 87 at the cost of that defense —
a prettier number bought with less protection, which is the wrong
trade. The record keeps them enumerated as unproved with this ADR as
their explanation; any future claim of full condition coverage must
either reproduce this argument or supply the traces it proves
impossible.

## Boundary

Condition coverage is still not correctness: a proved condition is
exercised, not shown to enforce the right rule. Structural dict
comparisons remain one condition regardless of field count; the six
suites holding 229 unattributed known-bad refusals remain unaudited;
the refusal-attribution vocabulary still has five spellings. The
canonicalization profile remains unissued, every null/false authority
boundary holds, and nothing here is Gate A acceptance, an admitted
member, or an independently reproduced verdict.
