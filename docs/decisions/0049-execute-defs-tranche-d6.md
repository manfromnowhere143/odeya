# ADR 0049: Execute definition tranche D6 — constraint-only convergence

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: converges the five constraint-only divergent definition
  names; the audit's divergent-name count falls from 55 to 50

## Context

Five shared definition names diverged only in their constraints: the
decimal family (`decimal`, `decimal_string`, `exact_decimal`), the registry
`member_key`, and `semantic_version`. The accepted D6 rule: converge to one
canonical definition per name, and every narrowing carries a known-bad
vector proving the stricter form fires.

## Decision

Measurement decided most of it. All seventeen decimal-family definitions
and their two containers were dead text orphaned by the D3 wave — zero
references anywhere — so their convergence is deletion; the frozen typed
scientific-decimal object is the one canonical decimal now, and the
predecessors retain every deleted byte in the ledgered history. Nineteen
dead definitions were removed, with the migrator refusing deletion if any
live reference remained.

The two live names narrowed to one canonical form each. `member_key`
converges on the 127-character bound (the longest key in the retained
corpus is 45 characters); `semantic_version` converges on the
no-leading-zero pattern, consistent with the frozen decimal law. Both
narrowings ship with known-bad vectors proven to fire before commit: a
130-character member key refused by the schema registry, and `01.0.0`
refused as a semantic version.

## Non-decisions

The 47 structural names (D7) and the three enum vocabularies (D8) remain,
each judged per name over its retained variant diff in its own tranche.
No member is admitted and Gate A is not accepted.

## Consequences

Divergent common-definition names: 55 before, 50 after; the recomputed
partition holds 61 findings. The reusable version aligner now covers every
suite's fixture top-levels permanently, retiring the recurring
post-closure drift class instead of fixing it once more.
