# ADR 0033: A datetime is never a scientific decimal

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review
- Gate effect: corrects the canonical migration audit's decimal detector and
  every downstream count; the true migration total is 1,150, not 1,154;
  resolves no finding and accepts no Gate A row

## Context

The D3 proposing tranche read all 59 fields the audit classified as generic
scientific decimals in their schema context, to propose semantic types and
units. Four refused the frame: they are `$ref`s to each schema's frozen
`$defs/timestamp` — the profiled UTC-microsecond lexical form itself — in
`model-configuration-record` (`controlled_time.value`), `projection-snapshot`
(`controlled_time.generated_at`), `research-state-view`
(`compilation_time.value`), and `routing-decision` (`controlled_time.value`).

Verification against the audit bytes found it worse than a misclassification:
all four sat in the decimal list **and** in the conformant datetime inventory
simultaneously — double-counted, one impossible migration each. Migrating a
timestamp to a decimal object would have been wrong, and the partition
validator would have faithfully enforced the wrong count forever, because it
recomputes from the audit and the audit itself was wrong.

The defect: `generic_decimal_uses` falls back to "the resolved pattern
contains a digit class and an escaped dot". The frozen timestamp pattern
`^[0-9]{4}-…\.[0-9]{6}Z$` contains both, so any profiled timestamp behind a
field name matching the scientific-field heuristic (`value`, `generated_at`)
counted as a decimal.

## Decision

One discriminator, taken from the audit's own datetime classifier: a resolved
node with `format: date-time` is never a scientific decimal. Regenerate the
audit and correct every dependent record in the same tranche:

- audit: decimal paths 59 → 55, NUMBER-001 findings 61 → 57, total migration
  findings 1,154 → 1,150;
- the closure record's current-audit block (raw digest and count);
- the disposition candidate, regenerated (D3 count 55; total 1,150) — its
  validator recomputed and passed unchanged, which is the recomputation design
  doing exactly what it was built for; and
- ADR 0032, the closure plan, the status document, and the handoff, corrected
  in place naming this decision.

The four rescued paths do not become new work: they already sit, conformant,
in the fixed-microsecond datetime inventory. They simply stop being findings.

## Non-decisions

This decision does not:

- claim the audit's other five detectors are correct. This defect was found
  only because a proposing pass read every finding in context; the same
  reading discipline should apply to the D5 table before acceptance;
- change any schema, fixture, or profile byte — only the audit generator and
  the records that cite its output; or
- resolve any finding or close PRQ-001.

## Consequences

The decision surface Daniel signs shrinks by four rows, and the D3 table is
now 55 rows, all genuinely decimal.

The pattern is the session's lesson at the instrument layer: the partition
validator guaranteed fidelity to the audit, and fidelity to a wrong instrument
is wrong with perfect reproducibility. Recomputation catches drift between
records; only reading the findings in their semantic context catches an
instrument that was never right. Both disciplines are needed, and the second
cannot be automated away.
