# ADR 0076: Rehearsal stage dispositions are derived, not asserted

- Status: Executed; removes a fabricated measurement from retained evidence
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: every manifest's `pass_dispositions` comes from a ledger the
  rehearsal appends to as each stage completes; a stage that did not run
  reports `not_run`

## A fabricated measurement inside the evidence

Independent review found that `PASS_DISPOSITIONS` in the manifest writer
was a module-level constant of six `"passed"` values, copied into every
manifest unconditionally, and that the comparator *required* exactly that
profile. The field was therefore structurally incapable of expressing a
failure or a skipped stage while presenting itself as a per-stage
measurement.

The values were not false — the rehearsal runs under `set -euo pipefail`,
so reaching the manifest step does imply the earlier stages exited zero —
but "the script got this far" is not what the field claims to say. A
retained artifact that asserts six passes it never observed is precisely
the shape of evidence this repository exists to make impossible, and it
sat inside the mechanism every other claim depends on.

## The correction

The rehearsal appends `stage=outcome` to a ledger as each of the six
stages completes. The writer derives every disposition from that ledger
and reports `not_run` for any stage absent from it. The comparator now
names which stages failed to pass instead of reporting a generic profile
mismatch, and its thirteen mutation self-tests still reject.

A rehearsal that skips a stage — the `else` branches that print "audit
tool absent" when replaying an older commit — now produces a manifest
recording that skip, and the comparator refuses it. That is stricter
than before and deliberately so: a rehearsal that did not run a check
must not produce evidence claiming the check passed.

## Boundary

Derivation makes the field honest about what ran; it does not verify what
ran was correct. The ledger is written by the same script whose stages it
records, so it attests sequence, not independent observation. Nothing
here is an accountable review determination, an admitted member, or Gate
A acceptance.
