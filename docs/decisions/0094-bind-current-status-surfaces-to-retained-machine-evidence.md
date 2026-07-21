# ADR 0094: Bind current status surfaces to retained machine evidence

- Status: Accepted as an architecture-validation invariant; publication and
  Gate A acceptance remain separate
- Date: 2026-07-21
- Decision owners: architecture review, repository release, evidence integrity
- Gate effect: current status and recovery narratives fail validation when
  they disagree with retained machine evidence; grants no implementation,
  runtime, publication, scientific, or Gate A authority

## Context

The ADR 0093 adoption commit correctly moved the generalized guard record to
469/958 proved with 489 unproved and the assurance checker to 199/284. Several
current public narratives still reported predecessor values. Other current
surfaces still described the v1 receipt/authenticator limitation after the v2
frame had been adopted. The structural validator stayed green because it
validated the machine records and unrelated prose, not the named current
interpretations readers use to recover the mission.

The first repair added required substrings. Adversarial review then showed that
a stale current sentence plus the correct sentence in an HTML comment passed.
The same checker ignored a changed non-assurance table row and credited a
known-bad when any unrelated error mentioned the same file. Presence is not
agreement, and a self-test is not intent-bound merely because something
failed.

## Decision

Current status gates must derive expected values and boundaries from retained
machine records and parse only explicitly named current sections. They must:

1. ignore HTML comments and historical sections when establishing current
   truth;
2. require each governed heading, row, and current assertion exactly once;
3. reconcile every generalized-suite table row and total, not a selected
   favorable subset;
4. reject stale-plus-correct duplicates, relocated assertions, missing rows,
   duplicate rows, and contradictory current wording;
5. distinguish a construction property from an observed-ceremony fact for
   ADR 0093; and
6. credit a known-bad only when the exact intended refusal appears, with a
   safe control proving the unmodified current bytes pass.

The canonical machine evidence remains authoritative for measured counts and
structured Gate A boundaries. The handoff recovery section separately binds
the exact published baseline and tree while allowing only that baseline or one
direct child as the active candidate. Historical decisions and dated recovery
logs keep their original wording and measurements; they are not silently
rewritten into current claims.

## Consequences

A future measurement change now requires one coherent update to the retained
record and every governed current interpretation. Moving only a flattering
headline or one table total fails. This adds friction deliberately: public
presentation is part of the evidence surface, not a marketing layer exempt
from machine checking.

The gate still cannot prove that its parser or source evidence is correct, and
it does not turn narrative agreement into scientific truth, accountable
review, or Gate A acceptance. Exact-commit rehearsal, independent review, and
operator decision remain separate obligations.

## Known-bad obligation

The retained self-tests must reject at least: a hidden-comment correction over
stale visible text; stale and correct values in the same current section; a
correct assertion moved outside its governed section; a missing or duplicate
section/table row; a changed non-assurance suite row; a v1 co-binding
contradiction reintroduced beside the v2 sentence; a stale published baseline
or direct-child rule; and an intended mutation masked by an unrelated error in
the same file.
