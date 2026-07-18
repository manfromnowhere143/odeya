# ADR 0079: The mutation audit generalized; 161 of 579 guards proved

- Status: Executed; the measurement is published, the closing is not done
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: a suite-agnostic mutation audit, its retained record, a
  ninth architecture-evidence check, and a rehearsal re-measurement stage

## What ADR 0078 required

ADR 0078 measured that 548 of the repository's 717 refusal statements had
never been audited — every coverage number this repository had published
described one suite of thirteen. This tranche builds the instrument that
looks at the rest.

`scripts/audit_suite_guard_coverage.py` generalizes the lifecycle audit:
each refusal construct of a declared suite is disabled in an isolated
tree copy and that suite is re-run; a guard is proved only when disabling
it makes the suite fail. Suites run in parallel because their costs
differ by two orders of magnitude — 0.07s to 6.4s per run — so the
slowest dominates wall time rather than the sum. A full measurement takes
under seven minutes.

## The instrument was wrong twice before it was right

The first run reported 133 of 579 proved, **every one classified as a
crash**, and two suites whose unmutated controls failed. Both were
defects in the instrument, not findings about the suites:

- Suites report refusals on **stderr** as often as stdout, and the
  detector inspected stdout alone, so every genuine detection was
  mislabelled fragile. A crash is now identified by the interpreter's own
  traceback rather than by which stream carried the message.
- Two suites resolve predecessor schemas **against their ledgered
  commits** rather than live files, and the tree copy excluded git
  history, so their controls could not pass.

A third defect was found by the rehearsal rather than by any local run:
the audit was given a **relative** interpreter path, which resolves to
nothing inside a tree copy that deliberately excludes the virtual
environment. Every local invocation had used an absolute path and passed;
the fresh-clone rehearsal used the relative one the CI stage passes and
failed at the new stage. The path is now resolved absolutely. This is the
rehearsal doing precisely what it exists for — catching what a
convenient local environment hides.

Those numbers were never published. An instrument that has not been
shown to observe the system rather than itself is the
self-contamination failure the 2026 refutation literature documents, and
the first run exhibited it.

## The measurement

**161 of 579 guards proved; 418 with no known-bad proof; zero
crash-detections** — every proof is attributable to a retained case.

| suite | proved | guards |
|---|---|---|
| constitutional-construction | 31 | 86 |
| work-intent-reference-resolution | 28 | 48 |
| physical-contracts | 22 | 59 |
| mathematical-contracts | 21 | 76 |
| projection-contracts | 21 | 77 |
| first-slice-resolution | 20 | 125 |
| cognitive-contracts | 16 | 56 |
| architecture-review | 2 | 7 |
| canonical-profile-candidate | 0 | 10 |
| command-identity-contracts | 0 | 10 |
| work-identity-successor-cohort | 0 | 12 |
| work-intent-identity-candidate | 0 | 13 |

Four suites prove **nothing**: 45 guards where removing any single
refusal leaves the suite green. Three of those four are the suites whose
declared error inventories ADR 0067 made exact — the exactness binds what
a case *declares*, and this measurement shows it does not bind what the
checker *does*. That is a finding about the difference between the two,
and it was not visible until an instrument was pointed at it.

## What follows

418 unproved guards is the largest open evidence unit in the repository
and closing it is case-writing work at that scale, not another
instrument. The record enumerates every unproved guard by name so the
work is addressable rather than aggregate.

## Boundary

Statement reachability only: a proved guard is exercised, never shown to
enforce the right rule, and condition-level coverage exists for one suite
alone. The record is regenerable by `--write` and therefore not a gate
(ADR 0077); its summary is pinned so regeneration is a deliberate edit.
Nothing here is an accountable review determination, an admitted member,
or Gate A acceptance.
