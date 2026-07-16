# ADR 0027: Correct the guard-coverage denominator and its enforcement

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security
- Gate effect: corrects two false claims in ADR 0025, restates coverage as
  46 of 71, and wires the only real check into the exact-commit rehearsal;
  closes no finding, admits no member, and accepts no Gate A row

## Context

ADR 0025 built a tool to answer whether a lifecycle guard has a known-bad proof,
because reading the suite could not. An independent adversarial review then
attacked the tool. Its headline measurements reproduced exactly. Two of its
claims did not survive, and both failures are instances of the defect the tool
was built to find, committed by the tool itself.

## Finding 1 — the denominator was wrong

ADR 0025 reported 69 guards. That is the count of `errors.append` calls, not the
count of guards. `work_lease_record_candidate_errors` refuses twice through
`return [...]` — for a case naming no retained fixture, and for an unknown record
mutation — and `discover()` matched only `errors.append`. Both were invisible.
Both are unproved.

The true figures are **71 guards, 46 proved, 25 unproved**, and the model is
4 of 29 rather than 4 of 27. Every count published by ADR 0025 and ADR 0026, the
suite README, and the handoff was short by two, and the retained record's
enumeration of unproved guards omitted two by name.

The review demonstrated the general case end to end: a dormant guard injected
through `errors.extend` left the audit reporting a contented `11/11` and the gate
passing. ADR 0025's claim that a guard "cannot be silently omitted" was therefore
false when written, and the omission it disclaims had already happened, unnoticed,
in its own record.

## Finding 2 — the gate cannot detect a falsified record

ADR 0025 claimed that retaining unproved guards by name prevents one from quietly
losing its proof while the total stays flat. It does not. The cheap gate enforces
the checker digest and the record's internal arithmetic; nothing binds the
record's content to a measurement. The review passed two falsified records:

- a guard flipped to unproved with `proved_by` cleared and every count corrected;
  and
- an unproved guard deleted by name with every count corrected, after which the
  gate reports a contented `46/70`.

`audit_lifecycle_guard_coverage.py --check` catches both, because it re-measures.
ADR 0025 documented that mode and never wired it, so the only real check was
never run by anything.

## Decision

Correct both, and correct the record of both.

- Extend `discover()` to every construct that can produce a refusal:
  `errors.append`, `errors.extend`, `errors += [...]`, and an early
  `return [...]`. A return-guard is disabled by `return []`, which removes the
  refusal while preserving the early exit, so the soundness argument is
  unchanged.
- Restate coverage as 46 of 71 everywhere it was published, and re-measure the
  retained record so its enumeration names all 25 unproved guards.
- Wire `--check` into `scripts/ci/rehearse-fresh-clone.sh`, the exact-commit
  path every commit already passes. It re-measures from clean bytes and refuses
  a record that does not reproduce. The cheap gate stays in the default
  validator for fast feedback on checker drift; it is no longer described as
  detecting falsification.
- Retract the two false claims in ADR 0025 in place, naming this decision, rather
  than leaving a corrected count with an uncorrected argument beside it.

Both fixes were confirmed against the exact tamper the review used: the cheap
gate still passes it, and the wired `--check` exits non-zero.

## Non-decisions

This decision does not:

- close any PRQ finding, admit a member, or accept Gate A;
- claim `discover()` is now complete. It matches four constructs. A guard added
  through a fifth is still invisible, and no mechanism detects that — the
  denominator is a claim requiring review, not a self-defending measurement;
- make the cheap gate sufficient. A falsified record still passes it, and only
  the rehearsal catches that;
- change the 46 proved verdicts, which reproduced exactly under independent
  review, with none proved via crash and no substring matching more than one
  guard; or
- measure `identity_map_mutation_errors`, `schema_contract_errors`, or the six
  suites that assert refusal without attribution.

## Consequences

The lesson is narrower and worse than a wrong number. A tool built to prove that
green does not mean guarded was itself green and unguarded: its denominator was
inflated by a silent omission, and its gate accepted a falsified record. Neither
was found by the tool, by its validator, or by its author. Both were found by an
independent reviewer instructed to refute.

That is the argument for law 4 stated in evidence rather than in principle. The
producing agent verified its own measurement, reported both halves of the ratchet
as firing, and was wrong about both. No amount of care inside the producing lane
substitutes for a reviewer whose task is to break it, and this record should be
read that way by any future session tempted to accept its own audit.
