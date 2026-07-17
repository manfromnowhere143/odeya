# ADR 0032: Partition the canonical migration findings for one operator decision

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security, work
- Gate effect: converts PRQ-001's 1,154 raw migration findings into nine
  machine-verified disposition classes with null acceptance slots; resolves no
  finding, reissues no schema, issues no canonical digest, and accepts no
  Gate A row

## Context

PRQ-001 is the root Gate A blocker: the canonical profile cannot be frozen
while the migration audit shows 1,154 findings across six classes, and every
canonical digest — hence T1, T2, T3, and Gate A — waits on that freeze. The
finding terminates in the operator's profile decision, which no session can
self-close. It has therefore sat unmoved through every tranche, because no one
can responsibly decide over 1,154 raw findings, and the lane kept producing
adjacent candidates instead.

The decision surface is the problem, not the decision. Computed from the audit
bytes: 236 findings are one identical lexical rewrite; 122 are one shared
definition pin; 668 group into 151 digest field names, 485 of them inside
shared `$defs`; 59 are one typed-object migration behind a per-field table; 11
are mechanically pinnable only last. The genuine judgment is concentrated in
the divergent-definition vocabularies and any new digest domains.

Two structural facts shape the whole decision. First, the union of schemas
touched by any finding class is exactly 100 of 112 — the same 100 regardless of
which classes are accepted — so under the no-same-ID-mutation law the blast
radius is one coordinated reissue wave; per-class acceptance changes reissued
content, never wave size. The 12 untouched schemas are precisely the newest
candidates, so the target idiom already exists in-tree. Second, sequencing is
dictated: new-domain registrations and any profile-core edit first (they
re-freeze the core bytes), then the schema wave, then the profile-binding pins,
then the fixture wave, and the audit must regenerate to zero blocking findings
— refreshing the audit without resolving findings is not closure.

## Decision

Retain one machine-verified partition and gate it as the fourth
architecture-evidence check.

`architecture/canonicalization-migration-disposition-candidate.json` assigns
every finding of the six audit classes to exactly one of nine disposition
classes (D1 fixture timestamps, D2 datetime pins, D3 decimal typing, D4 binary
numbers, D5 digest scoping, D6/D7/D8 divergent definitions by comparator class,
D9 profile bindings), binds the exact audit corpus digests, embeds the two
proposal tables with null slots (59 decimal rows; 151 digest field groups), and
carries one null `operator_acceptance` slot per class.

The candidate's stored rows are never trusted, because stored copies drift —
this repository retired five coverage denominators for exactly that failure.
(An earlier wording here, "stores no partition rows", did not survive literal
reading: the candidate stores counts, assignments, tables, and the union; what
it never does is have them believed without recomputation.)
`scripts/validate_canonicalization_dispositions.py` recomputes the entire
partition from the audit bytes on every run: per-class counts, the
divergent-definition triage under the exact comparator the candidate declares,
the touched-schema union, and both tables. It refuses any disagreement, any
pre-filled acceptance, and any promoted status, and its self-test — run on every
gated invocation, not only by hand — proves the gate fires by refusing fourteen
known-bad mutations of a correct candidate, including contradictory duplicate
rows whose lying first copy would hide behind last-wins dictionary construction,
and a gutted comparator declaration.

The divergent-definition triage is rule-based and its sensitivity is recorded
rather than hidden: treating constraint-keyword presence as structure gives
5 converge / 47 structural / 4 enum-policy names. Independent review corrected
the comparator itself: const values now participate in the vocabulary check,
because `signature_record`'s variants differ only in a `signature_purpose`
const — deliberate domain separation — and the enum-only rule filed it as
converge, whose recommendation would have merged two signature-purpose domains.
The checker also binds the declared comparator to the implemented one, after
review showed the declaration was ornamental. An earlier analyst triage of
20/32/4 did not reproduce under any precisely-defined comparator and was
discarded.

## Non-decisions

This decision does not:

- accept any class. Every `operator_acceptance` slot is null and the validator
  refuses a pre-filled one; the operator's per-class decision is a separate
  explicit change to the candidate, after which the acceptance rule in the
  validator is amended in the same commit — deliberately, never silently;
- propose the table contents. The 59 decimal rows need semantic type, unit, and
  precision per field, and the 151 digest field groups need digest kind and
  subject class per name; both require reading each field's meaning and belong
  to a proposing tranche with its own review, not to a partition commit;
- decide which D5 rows require new digest domains beyond the frozen 21, which
  is the one sub-decision that re-freezes the profile core;
- resolve, normalize, converge, rename, reissue, or pin anything — no schema,
  fixture, or profile byte changes in this tranche; or
- close PRQ-001, whose closure additionally requires the executed wave, a
  regenerated zero-finding audit, transitive consumer reissue, independent
  review, and the operator's profile decision.

## Consequences

PRQ-001's decision surface drops from 1,154 findings to nine class decisions
plus two tables, with the partition's fidelity machine-enforced instead of
asserted. The operator can now decide in one sitting, and an accepted class
converts directly into a bounded, reviewable reissue tranche.

The remaining path to PRQ-001 closure, in order: the proposing tranche fills
the two tables and enumerates any D5b domain registrations; the operator
decides over classes and tables; the single reissue wave executes in the
dictated sequence; the audit regenerates to zero; and the transitive consumer
graph and accountable reviews follow. Only then can the profile freeze and the
first canonical digests exist.
