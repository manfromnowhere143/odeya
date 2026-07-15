# Registry Graph Contracts

Status: architecture-only structural candidate, 2026-07-16. These contracts
define the machine shape of Odeya's command/event/reducer/state graph. They do
not identify an accepted Gate A member set, activate a runtime, prove a
handler, prove a reducer implementation, or authorize product implementation.

## Closed graph

One compatible engine root must close this directed graph without inference by
name:

```text
exact retained schema bytes
          |
          v
admitted command member --> legal event alternatives
                                  |
                                  v
                         one aggregate owner
                                  |
                                  v
                    one reducer slot per aggregate
                                  |
                                  v
                    one state-subject slot per aggregate
```

Content-digest dependencies have one acyclic order:

```text
schema -> state -> reducer -> event -> command
```

A forward reference carries the exact target member digest. A necessary
back-reference carries exact logical type/version plus
`same_root_exact_member`, and the root graph validator resolves it against the
one snapshot already bound by the compatible root. For example, an event can
hash its reducer member; the reducer's accepted-event list cannot also hash the
event member without creating an impossible content-hash fixed point. The same
rule breaks state/reducer and event/producer-command cycles without permitting
`latest` or cross-root lookup.

The root builder must reject a missing, duplicated, ambiguous,
owner-inconsistent, version-incompatible, or back-reference/digest mismatch.
JSON Schema proves local shape; a separate pure graph-closure validator must
prove cross-registry equality, map-key/member-key agreement, cardinality
commitments, ordering, and digest resolution offline.

## Identity topology

Member records are immutable subjects. They do not contain their parent
registry snapshot, membership proof, activation, checkpoint, seal position,
storage location, or signature. A registry subject may refer to the exact pure
registry subject it supersedes; that is a historical edge, not an activation
or currentness claim.

Each member digest projection includes its digest contract and excludes only
the resulting member digest. Each registry digest projection includes its
digest contract and excludes only the resulting registry digest and external
attestations. Digest-bearing references must follow the acyclic dependency
order above; exact logical back-references are closed by the root and are not
silently promoted to cyclic member-digest fields. Moving, witnessing,
re-signing, checkpointing, or activating the same bytes cannot change their
identity.

The permitted direction remains:

```text
member subjects -> registry subjects -> EngineContractRoot -> C0 bundle
                -> checkpoint -> prospective activation
```

No reverse reference is valid. In particular, a member cannot hash a parent
snapshot or a future checkpoint, and C0 cannot embed an activation that points
back through a checkpoint.

## Schema registry

[`SchemaRegistry`](../schemas/schema-registry.schema.json) binds exact raw
schema bytes by `schema_id@semantic_version`, including byte digest, byte
count, UTF-8 encoding, media type, dialect, root JSON type, and
content-addressed retrieval policy. A mutable URL, `latest`, implicit upcast,
or canonical-byte rewrite is not a schema identity. Historical interpretation
requires the retained original bytes.

## Admitted-only command registry

[`CommandContractRegistry`](../schemas/command-contract-registry.schema.json)
contains only complete, contract-admitted command members. Presence does not
prove deployment or activation. Reserved design names are absent rather than
represented by nullable schemas or missing handlers.

The separate
[`command-design-vocabulary.json`](../architecture/command-design-vocabulary.json)
retains the 121 selectors extracted from the exact `CommandEnvelope` 0.4.0
candidate bytes for planning. Its schema forces every entry to
`not_contract_admitted` and forbids payload, handler, event, reducer,
authority/grant, compatibility, activation, and execution promises. It is not
a command registry, envelope surface, accepted set, or compatibility promise.

Every member fixes:

- an exact, non-nullable payload schema;
- owning module, target aggregate, allowed stream class, target existence, and
  origin permission;
- actor classes and the rule that model/tool output is not authority;
- authority mode, role, assignment requirement, and exact grant-consumption
  point;
- required admission-evidence families and pure semantic rules;
- closed atomic event/cohort alternatives plus event-free rejection;
- parser, payload, reference, and rule-evaluation limits;
- immutable idempotency and historical-retry behavior;
- a pure prospective handler/decider port that proves no runtime deployment;
  and
- positive, negative, boundary, race, replay, compatibility, and review
  evidence references.

The enabled envelope set, admitted registry-member set, and conforming handler
set must eventually be exactly equal at activation. That equality is not
claimed by these structural fixtures.

## Event registry

[`EventContractRegistry`](../schemas/event-contract-registry.schema.json) binds
one exact event discriminator/version to one payload JSON Pointer inside exact
retained event-schema bytes. Each event has one canonical aggregate owner, a
closed producer-command set, a retention/privacy contract, and one canonical
reducer reference. Projections may consume the event, but they do not become a
second canonical owner.

An event record does not prove that a command may emit it or that the reducer
accepts it. Command alternative, event owner, reducer accepted-event set, and
state aggregate identities must all agree in the same root.

## Reducer registry

[`ReducerRegistry`](../schemas/reducer-registry.schema.json) uses one object map
slot per aggregate type, so one snapshot cannot structurally place two
canonical reducers in one aggregate slot. Strict duplicate-key rejection and a
pure key/member equality rule complete the map discipline.

Every reducer member fixes:

- an explicit absence sentinel and at least one origin event;
- first materialized aggregate version `1`, never a fabricated v0 state;
- a closed accepted-event set;
- a total result union of next state or typed reduction failure;
- fail-closed behavior for unknown versions, wrong owners, bad heads, invalid
  prior states, invariant failures, exceptions, and timeouts;
- orthogonal state axes;
- exact invariant, transition, and upcast policy references;
- positive, negative, boundary, metamorphic, race, replay, and compatibility
  trace packages;
- bounded deterministic resource limits with no clock or I/O input; and
- at least two language/runtime-separated implementation requirements, with
  shared code and copied logic forbidden.

Two requirement references are not two implementations. Gate A still needs
actual independently produced per-event state digests and retained disagreement
evidence.

## Aggregate-state subject registry

[`AggregateStateSubjectRegistry`](../schemas/aggregate-state-subject-registry.schema.json)
uses one state-subject slot per aggregate. Each member fixes exact state-schema
bytes, one reducer, explicit origin events, absence-before-origin, version/head
progression, a domain-separated state-root contract, invariant rules, and
failure behavior.

Absence is not an implicit state. A canonical state appears only when its
reducer consumes an admitted origin event and materializes version `1`.
Snapshots, checkpoints, activation references, signatures, storage locations,
and wall-clock values are excluded from state-root identity. A snapshot
mismatch causes replay or quarantine; it cannot redefine history.

## Structural conformance evidence

The five fixtures under `tests/architecture-schema/fixtures/` explicitly use
`conformance_scope=structural_fixture_only` and retain a critical
`structural-only` limitation. They are synthetic shape examples, not fake Gate
A instances. The architecture-schema manifest includes known-bad mutations for
parent/checkpoint cycles, missing exact bytes, reserved-command admission,
missing/nullable payloads, a second event owner, missing reducer origin, two
reducers in one aggregate slot, fabricated v0 state, insufficient independent
implementation requirements, digest-scope substitution, embedded signatures,
and mutable `latest` resolution.

Passing those cases establishes only that the current JSON Schemas reject the
named structural mutations. It does not establish semantic closure, digest
correctness, implementation independence, transaction isolation, replay
agreement, scientific validity, or architecture acceptance.

## Work still required before an immutable candidate

The following remain blocking:

- name the exact dependency-closed Gate A admitted command set;
- create real schema, command, event, reducer, and state member instances from
  the frozen source bytes;
- prove map-key/member-key equality, count commitments, ordering, and every
  cross-registry edge with two independent validators;
- generate the admitted-only command envelope and prove set equality;
- run complete command/cohort/reducer traces, including known-bad and recovery
  paths, in two independent reducer implementations;
- bind the exact compatible registry subjects into a resealed engine root, C0
  bundle, module manifest, and canonicalization audit;
- close independent security, distributed-systems, scientific, privacy, and
  architecture review findings; and
- obtain Daniel's decision over the exact frozen candidate bytes.

Until then, these files are architecture contracts under review, not an engine
implementation and not evidence that Gate A is closed.
