# ADR 0034: The decimal detector missed in both directions

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review
- Gate effect: widens the audit's decimal detector, restates the migration
  total as 1,179, corrects four corrupting proposal rows, and bounds the
  proposal gate's claim to shape-completeness; resolves no finding and accepts
  no Gate A row

## Context

Adversarial review of the fully-proposed decision package confirmed its counts
and its D5 kind assignments against schema bytes, and refused to declare it
ready to sign on three grounds. All three were real.

**Four proposal rows would have corrupted meaning if accepted.** Three
`money_quantity.amount` rows and one `spend_observation.amount` row proposed
fixed precision 2 with confidence `certain`. The schema bytes allow any
ISO-4217 code and unbounded fractional digits: precision 2 corrupts exponent-0
and exponent-3 currencies and rounds sub-cent compute spend — routine for
model-API costs — to zero. A sibling row in the same table already hedged the
same question, so three `certain` labels contradicted the package's own
content. The `evidence_measure.value` row proposed `dimensionless, certain`
while the sibling type enum includes `utility_estimate`, which is generically
not dimensionless. All four are downgraded to operator-choice precision or
type-dependent unit with honest confidence.

**The detector missed at least twenty genuine decimals.** ADR 0033 fixed its
false positives; its false negatives remained. The name filter required a
match in a fixed word list, so `model_tokens` sat ungoverned beside seven
governed siblings in the same resource budget, the affine conversion `offset`
beside its governed `scale`, interval `lower`/`upper` beside their governed
`level`, plus noninferiority margins, `traffic_fraction`, `horizon`, and
`limit`. An operator signing "the decimal disposition" would not have been
deciding the decimal question. The widened filter captures twenty-nine
additional fields — every one verified against schema bytes as a genuine
decimal shape, none a version string or timestamp — and each received a
proposal read from its schema context, including two new vocabulary entries:
`unit_conversion_offset` (an offset is in target-unit terms, not
dimensionless) and `proportion`.

**The proposal gate was over-described.** Review defeated the earlier binding
five ways: whitespace passed truthiness, the declared vocabulary was
ornamental, a twenty-one-character meaningless subject satisfied a length
heuristic, swapped proposal contents were invisible, and a one-character
subject passed on non-deferring rows. The gate now strips whitespace, binds
every semantic type to the declared vocabulary, requires a substantive
subject, and requires every deferring row to carry a reason — with each defeat
added to the self-test. Its docstring states what remains true and what does
not: it is a shape gate; swapping two rows' contents still passes, and no
arithmetic can substitute for the operator's content judgment informed by the
retained review.

## Decision

Widen the detector's name filter (the shape test — a decimal reference or
decimal pattern — remains the real discriminator; the name list exists only to
skip identifier-like strings and must err wide). Regenerate the audit:
NUMBER-001 is 86, the migration total is 1,179, the D3 table is 84 rows. Walk
the deliberate-change cascade: closure record, disposition candidate, document
citations, source-lock repin, evidence rebind, and both canonicalizer
implementations re-run under the new lock, agreeing.

## Non-decisions

This decision does not claim the detector is now complete — its name list is
still a heuristic, and the third instrument defect will be found the same way
the first two were, by reading findings in context rather than trusting
counts. It does not accept any class or table row, does not register any
domain, and does not close PRQ-001.

## Consequences

The total has now been 1,154, 1,150, and 1,179. Each move was the instrument
getting closer to the schemas, not the schemas changing, and each was found by
a reviewer or a proposing pass that read the underlying bytes. The operator's
sitting decides over 84 decimal rows that are genuinely decimals, and four
rows that would have silently corrupted money and evidence semantics now defer
to the operator honestly.
