# ADR 0043: Execute digest-scope tranche D5a-1

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: annotates 270 mechanically resolvable digest occurrences with
  their accepted scopes; the audit's unscoped-digest count falls from 668 to
  398

## Context

The accepted D5 table binds a digest kind and subject to each of 151 field
names. One hundred eighteen rows are executable without per-occurrence
reading: the byte-digest rows, whose kind is the whole law, and the canonical
rows naming exactly one domain — an existing registered domain or a name
reserved in the profile core's prospective registry by ADR 0039.

## Decision

Each such occurrence gains an `x-odeya-digest-scope` annotation at its
property node, following the corpus's established annotation idiom: kind,
subject or domain, algorithm, profile, and status. Prospective names resolve
through the reservation registry to their reserved domain separators — a name
with no reservation refuses the migrator, so ADR 0039's registry is the law
and the annotation can never invent a domain. Registered domains verify
against the declared registry the same way.

The reissue closure lawfully bumped eighty-five resources behind the
annotations; twenty-one schemas entered the ledger for the first time, each
with its predecessor pinned at the checkpoint. The lifecycle suite's version
pin was made self-deriving — the version const expectation now derives from
the URN the closure already repoints, so a reissue can never split the two
expectations again — and the command vocabulary's scoped self-digest rebound
over its repointed subject reference.

## Non-decisions

The twelve contextual rows (multi-domain subjects and target-resolved
scopes, 72 occurrences), the three mixed rows led by the generic `digest`
family (284 occurrences), and the eighteen needs-operator rows awaiting the
frontier and commitment construction decision (37 occurrences) are untouched
here; each belongs to its own recorded tranche. No member is admitted and
Gate A is not accepted.

## Consequences

Unscoped digest fields: 668 before, 398 after, every annotation traceable to
an accepted table row and a registered or reserved domain. The remaining D5a
work is per-occurrence classification, then the one construction decision
that unblocks the deferred families.
