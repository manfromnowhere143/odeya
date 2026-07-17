# ADR 0050: D7, D8, and D9 close the migration wave at audit zero

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: the regenerated audit reports zero across all six blocking
  classes; the recomputed disposition partition holds zero findings; the
  canonical profile is clear of migration blockers and remains unissued
  pending Gate A

## D7 — structural divergence, rename-distinct

The accepted default executed mechanically to a fixed point: for each of
the 47 structural names, the majority variant keeps the name and every
minority site takes a schema-scoped name, with internal references
following. Renames create second-order divergences in wrapper definitions
that reference renamed names, so the pass iterates until only the enum
vocabularies remain — 201 renames over three rounds. No convergence was
forced; renaming never precludes a later provably-safe superset merge.

## D8 — closed central vocabularies

The profile core freezes three enum vocabularies — claim_type (14 values),
operation (18), scientific_outcome (26) — as the unions of their measured
variants, pinned member by member in the core schema. Each context keeps a
declared subset under a scoped subset name, and the audit gains a
fail-closed subset gate: a definition in a vocabulary family whose enum
carries a value outside the closed vocabulary refuses the entire audit,
with self-test proofs in both directions on every run.

## D9 — the profile-binding pins, strictly last

All eleven bindings pin the candidate profile identity against the final
core bytes: string-form bindings by node const; object-form bindings
through their identifying member; reference-shaped bindings by an allOf
refinement at the use site, after the first attempt pinned members inside
shared definitions and poisoned sibling references — the schema-case gates
caught it within one run, and the pins moved to the sites where they
belong. The binding detector recognizes all three pin forms and proves, on
every run, that an object-shaped pin is recognized and that a free binding
still counts as unpinned.

## Gates that could not observe success, migrated

Reaching zero exposed the same defect class ADR 0038 first named, now at
wave scale: the profile evidence pinned the blocked disposition, the
Gate A prerequisite record pinned the blocked status, and the disposition
self-test indexed tables the wave had emptied. Each migrated to
disposition-consistent or phantom-row form — able to see both worlds while
keeping the profile unissued in each — and the audit itself now reports
`gate_a_disposition: candidate_clear`.

## Consequences

From 1,222 findings to zero across D1 through D9, every reissue ledgered
against the checkpoint, every gate that fired recorded, every commit
rehearsed from a fresh clone. PRQ-001's wave condition is satisfied: the
audit regenerated to zero with the findings resolved, not refreshed away.
What remains before the profile can freeze is exactly what the closure
plan always said comes next: independent review of the executed wave and
the operator's exact-byte profile decision — neither of which any session
can grant itself.
