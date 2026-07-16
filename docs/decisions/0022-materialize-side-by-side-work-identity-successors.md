# ADR 0022: Materialize side-by-side work identity successors

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-16
- Decision owners: work, canonical identity, contracts, security, recovery
- Gate effect: advances C5/PRQ-009 migration evidence; does not issue a
  canonical identity, close PRQ-009, accept Gate A, or authorize runtime work

## Context

ADR 0021 froze an identity-free WorkIntent semantic core and proved why
WorkIntent 0.1 cannot safely receive a digest over the complete object that
contains that digest. It also identified two exact schema consumers: canonical
WorkLease 0.1 and WorkContract 0.2.

Replacing those resources in place would preserve convenient filenames but
remove the old `$id` resources from the current resolver. Git history alone is
not a complete offline schema registry, and a same-path replacement would make
intermediate or historical references depend on repository history rather than
an exact present resource.

The stronger migration rule is immutability by resource identity: retain each
predecessor byte-for-byte and add its successor under a distinct path. This is
consistent with [JSON Schema 2020-12 Core](https://json-schema.org/draft/2020-12/json-schema-core.html),
where `$id` identifies a schema resource, and with content-addressed systems
that retain old objects while adding new descriptors rather than mutating an
old identity.

## Decision

Materialize one side-by-side architecture-time successor cohort:

- `work-intent:0.2.0` wraps the exact WorkIntent semantic core and adds exact
  profile/schema bindings for the retained source-view, planning-epoch, and
  output-schema references;
- `canonical-work-lease:0.2.0` wraps the exact canonical WorkLease 0.1
  candidate and binds its legacy WorkIntent reference to the WorkIntent 0.2
  successor schema and candidate bytes; and
- `work-contract:0.3.0` wraps the exact blocked WorkContract 0.2 candidate and
  binds its legacy WorkIntent reference to the same WorkIntent 0.2 successor.

Keep `work-intent:0.1.0`, `canonical-work-lease:0.1.0`, and
`work-contract:0.2.0` present at their existing paths with unchanged bytes.
No mutable alias, implicit `latest`, or same-path schema mutation participates
in the successor construction.

Bind the whole cohort from a separate evidence record to:

- predecessor commit `6ec40b4635815c64ba9d8c5ec084d7f480e16db1` and tree
  `e7044da26ad273de8491a34705e87c8899173f29`;
- exact predecessor, successor-schema, and successor-candidate raw bytes;
- the three explicit dependency edges;
- bounded equality checks between embedded predecessor subjects and retained
  fixtures; and
- all unresolved identity, assignment, retention, review, and authority
  boundaries.

The wrappers are migration bridges, not admitted final records. The source-view
and planning-epoch values remain synthetic architecture data. The legacy output
schema digest is intentionally shown to differ from the exact current schema
raw digest. Those findings prevent canonical digest construction and make an
authority escalation a test failure.

## Non-decisions

This decision does not:

- issue or accept the canonicalization profile;
- repair or relabel a synthetic reference digest;
- claim complete nested-reference admission;
- compute any of the three successor canonical digests;
- retire or redirect predecessor resource IDs;
- claim a complete offline schema registry;
- admit a schema/member/root/activation cohort;
- construct the thirteen-event verification assignment transaction;
- prove cross-record canonical identity equality, reducers, replay, recovery,
  independent implementation, or accountable review; or
- authorize assignment, lease, materialization, dispatch, deployment, runtime,
  spending, data exposure, publication, or an external effect.

## Consequences

The current resolver can now resolve both predecessor and successor schema
resources without repository-history lookup. WorkIntent's three ambiguous
legacy references are externally pinned to exact target schemas and the exact
candidate profile shape, while their still-synthetic identity status remains
visible rather than being fabricated away.

Thirty-seven known-bad mutations now reject subject drift, profile aliases,
schema substitution, missing or reordered resources and edges, predecessor
mutation, false retention, fabricated canonical equality or acceptance, and
authority escalation.

C5/PRQ-009 remains blocked. The next identity tranche must replace the
synthetic source-view and planning-epoch values with admitted exact resources,
repair the output-schema digest mismatch through a new immutable WorkIntent
successor, issue and admit the profile, and only then construct canonical
digests and registry memberships. The assignment cohort, WorkLease lifecycle
release correction, reducers/replay, review, and operator acceptance remain
separate later obligations.
