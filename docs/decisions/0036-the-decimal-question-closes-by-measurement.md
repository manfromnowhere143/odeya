# ADR 0036: The decimal question closes by measurement

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review
- Gate effect: records the empty termination sweep that closes the D3 decimal
  coverage question, applies the sweep's five residue prescriptions, and
  declares the disposition package ready for the operator sitting; accepts
  nothing itself

## Context

ADR 0035 refused to end the detector-correction loop by fatigue and defined a
termination criterion instead: an independent reviewer runs its own name-blind
sweep of every decimal-shaped leaf in every retained schema, and the decimal
question closes only when that sweep returns empty against the retained table.

## The measurement

The sweep ran at dbf7ef6 with a method independent by construction: a
probe-based classifier — a pattern counts as decimal only if its compiled
regex accepts decimal probe strings and rejects identifier, version, datetime,
digest, and URN probes — traversing every JSON Schema keyword position with
cycle-guarded reference resolution, sharing no code with the audit detector.
Its gate was proven live on positive controls: deleting one table row and
injecting one decimal field were both reported immediately, and the repo's own
checker failed the same mutations independently.

**Result: empty.** 192 decimal occurrence paths through 28 pattern positions
in 21 schemas, all governed; every one of the 127 table rows lies on a real
decimal occurrence path, so there are no phantom rows; the audit's decimal set
and the table's row set are equal in both directions. The reviewer also
mechanically compared all 24 base/twin row pairs (zero mismatches) and
confirmed the certain/likely split tracks the bounded-versus-generic pattern
distinction exactly.

## Residue, applied or recorded

The sweep reported five items, none reopening the question:

- **Applied — one precision vocabulary.** The external-cost twins carried two
  tokens for the same operator choice; unified to
  `operator_choice_currency_exponent_or_6`.
- **Applied — the bytes-versus-claim standard, symmetrically.** Byte-count
  rows claimed `certain` while their bytes permit fractional values, the exact
  situation that downgraded `model_tokens`; six rows are now `likely`.
- **Recorded for the reissue wave** in the candidate's
  `decimal_closure_residue`: the multiplicative conversion `offset` is a
  decimal-valued `const "0"` — a leaf class no pattern detector can see, and
  the concrete instance of ADR 0035's predicted fourth defect, self-
  canonicalizing today but bound to move in lockstep with any retyping;
  `physical-measurement-result` carries a dead `$defs/decimal` whose first
  future reference would inherit an ungoverned decimal; and correlation
  elements are not range-bounded to [-1, 1] by bytes, now noted on the row the
  operator signs.

## Non-decisions

This decision does not accept any class, row, or domain; does not change any
schema byte (the residue schema fixes belong to the reissue wave, where
no-same-ID-mutation law puts them); and does not claim the audit's other five
detectors have received the same treatment. It closes one question, by the
criterion set in advance, with the measurement retained.

## Consequences

The disposition package is ready for the operator sitting: nine classes over
1,222 recomputed findings, 127 decimal rows and 151 digest field groups fully
proposed, roughly fifty new-domain decisions with their consolidation levers,
every acceptance slot null and machine-refused if pre-filled.

The loop that ended here ran four corrections deep — 1,154, 1,150, 1,179,
1,222 — and ended because a criterion was written down before the answer was
known, not because anyone grew confident. That is the pattern this repository
exists to enforce, applied to its own tooling, and it is the standard the
reissue wave should be held to when it executes.
