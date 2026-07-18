# ADR 0065: Coverage records declare their detection kind

- Status: Executed; closes the third of ADR 0063's surviving weaknesses
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: every proved guard and condition in the retained coverage
  records now declares whether its proof is case-attributed or a crash,
  and the cheap gates refuse a proof without its kind

## The weakness

Round-two review showed thirteen condition proofs rest on the
interpreter crashing in code adjacent to the removed member — and
demonstrated one flipping to silently-removable under a
behavior-preserving respelling of that adjacent code. A crash is real
detection, but it is fragile detection: it proves the removal was
noticed on today's exact bytes, not that any retained case owns the
condition. The records presented both kinds as the same strength.

## The correction

Both audits now record `detection` per proved item — `case_attributed`
when a suite-reported case failure established the proof, `crash` when
the checker died before reporting any — and both summaries carry the
crash count. Re-measurement confirms the review to the digit: the
condition record holds 88 of 89 proved with exactly 13 crash-detected;
the statement record holds 161 of 161 proved with zero. The cheap
gates refuse a proved item that does not declare its kind.

## Boundary

This tranche makes the fragility visible; it does not remove it. For
most of the thirteen, a non-crash proof is structurally impossible —
an `isinstance` conjunct that fails only for inputs the later conjuncts
would also reject cannot be made solely load-bearing without
restructuring the guard itself, which is contract text this tranche
does not touch. The thirteen are now individually inspectable in the
record; whether any guard should be restructured for durable proofs is
a separate decision. The remaining ADR 0063 weaknesses — the condition
denominator omissions and the subset-semantics rebindability — stay
open. Nothing here is an accountable review determination or Gate A
acceptance.
