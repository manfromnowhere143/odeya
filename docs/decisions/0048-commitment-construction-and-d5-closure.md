# ADR 0048: The commitment construction decision closes class D5

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: decides the construction for every commitment-family digest,
  reserves twelve domains, annotates the final 45 digest occurrences, and
  closes class D5 at zero unscoped digest fields

## Context

Eighteen accepted rows deferred on one question the table refused to answer
per-field: how frontier, state-root, graph-root, and ordered-digest-list
subjects are constructed — as canonical closed objects under the frozen
profile, or as an incremental commitment scheme such as a Merkle tree.

## Decision

Every commitment subject is a canonical closed object under the frozen
profile: an explicit manifest carrying its members, digested under a
per-subject registered domain. Replayability and reviewability are the
architecture-stage requirements; incremental-proof machinery may be added
later only as a new domain and a new field, never by mutating these
identities. The decision is recorded in the acceptance record and twelve
domains are reserved through it: the ordered-digest-list commitment, five
frontier manifests (security, legal, evaluation, recovery, execution),
three state manifests (data-use, lease, resource), the epistemic-graph
manifest, and the module-dependency and data-asset-collection manifests
whose deferral D5a-3 recorded.

Per-field rulings under the same authority: `assignment_commit_digest` pins
to the assignment event under the research-event domain, because the
append-only event is the truth a commit binds; `recipient_digest` is a
privacy-preserving byte digest over the exact recipient identifier bytes;
`configuration_digest` is a byte digest over retained configuration bytes;
`tree_digest` is annotated as an external git identity that does not
replace a source-bundle digest; `weights_or_endpoint_digest` is split into
`weights_digest` and `endpoint_descriptor_digest` with exactly one
required, because one field must not admit two subjects; and
`payload_contract_digest` stays explicitly unresolved-blocking per the
profile document — annotated as unresolved, never inferred.

## What the tranche caught

The disposition validator's D5 known-bad proofs indexed a table the wave
had emptied; they migrated to the phantom-row form the D3 proofs already
use, so an empty table still refuses fabrication.

## Non-decisions

No commitment schema is constructed yet — the reservations name the
domains their declaring schemas will claim. D6 through D8 and the D9 pins
remain. No member is admitted and Gate A is not accepted.

## Consequences

Class D5 closes at zero: all 668 digest occurrences carry accepted scope
annotations or explicit unresolved markings. Five of the six blocking
classes measure zero; the recomputed partition holds 66 findings — the 55
divergent definition names and the 11 profile-binding pins — between the
audit and zero.
