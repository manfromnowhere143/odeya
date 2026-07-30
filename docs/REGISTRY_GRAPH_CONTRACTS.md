# Registry Graph Contracts

Status: architecture-only structural candidate, 2026-07-29. These contracts
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

## Snapshot membership is not transparency history

A registry snapshot and the history of registry snapshots are separate
subjects with separate orderings:

```text
registry snapshot
  = deterministic map ordered by the frozen member-key byte profile
  = commits exact (member_key, member_digest) leaves
  = produces external member-inclusion receipts

registry history
  = insertion-ordered append-only log of registry-snapshot digests
  = publishes signed checkpoints
  = produces inclusion and checkpoint-consistency proofs
  = receives external witness observations/cosignatures
```

The history must never be sorted into member-key order, and the registry must
never claim temporal append-only semantics merely because its members are
deterministically sorted. A member-inclusion receipt carries the exact registry
family/version/digest, member key/digest, commitment profile/root, leaf index,
tree size, and inclusion path. It is derived evidence and remains outside both
the member and registry digest.

A history checkpoint carries the log identity/origin, insertion-ordered tree
size/root, signing purpose and key identity, and exact prior-checkpoint
continuity. Consistency proofs and independent witness cosignatures remain
outside the checkpoint identity they verify. A proof establishes only the
bounded membership or append-only property of the selected construction. It
does not establish semantic admission, scientific validity, completeness,
currentness, witness independence, or a globally unique view.

Root succession is an authenticated historical path rather than a mutable
`current` alias. Every replacement retains monotonically advancing exact root
versions, old-plus-new threshold authorization, controlled-time expiry/freeze
checks, rollback refusal, and every intermediate root needed by an older
trusted reader. Historical replay resolves the exact prior root and never
silently migrates it.

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

## PRQ-002A non-issuable structural identity probe

[ADR 0099](decisions/0099-freeze-prq-002a-structural-identity-probe-layer.md)
adds a separate architecture-only construction probe for the forward identity
path that the embedded structural fixtures do not instantiate. The probe
retains one exact non-self-hashing profile core, nine architecture schemas,
12 standalone members, four flat ordered-map commitments, and four homogeneous
pure snapshots. Its synthetic graph is limited to
`structural-aggregate`; it creates no product registry member or production
domain.

The retained cohort contains 21 objects and 20 structured digests. Exact raw
schema/profile bytes feed the member graph, decoded ASCII member keys are
sorted by unsigned UTF-8 bytes before each family commitment, and each
snapshot binds one family-specific commitment without history, membership,
checkpoint, seal, or activation semantics. The retained Python- and
Node-labelled source- and language-separated results agree exactly for this
bounded cohort. Current recomputation additionally requires explicit
executable selectors, exact installed canonicalizer payloads, runtime
provenance checks, fresh challenges, and complete child attestations bound to
the exact result lines. The retained Darwin/arm64 execution observations are
host-specific and do not establish organizational independence.

Dependency bootstrap and the Node installer may use a local cache or the
network before evaluator execution. The evaluators are not OS-network
sandboxed; their exact source manifests declare no network request, which is
not an observation proving non-use.

The probe is explicitly `test_only_non_issuable_structural_probe`. Its
profile, domains, member digests, commitments, and snapshots are
non-promotable. Passing the suite does not issue the canonicalization profile,
close PRQ-002, allocate any product identity, admit a member, construct an
`EngineContractRoot`, or authorize Gate A or runtime work.

## PRQ-002B unissued scoped product-identity successor

[ADR 0100](decisions/0100-introduce-an-unissued-scoped-product-identity-profile-successor.md)
adds twelve side-by-side product schema resources under the scoped,
non-aliasing `odeya-jcs-0.2` successor candidate: four standalone member
schemas, one ordered-member-map commitment schema, four pure-registry
successors, and three profile core/evidence/migration schemas. Nine product
identity domains are declared before any product digest may be computed.

The predecessor stays byte-for-byte distinct. Its frozen canonicalization
audit remains exactly 120 schemas and 216 fixtures, while the scoped candidate
partition is:

```text
106 retained direct odeya-jcs-0.1 consumers
 14 retained non-direct predecessor resources
 12 side-by-side successor resources
---
132 current product schema resources
```

Nine structural-nonidentity fixtures satisfy the shared schema harness without
constructing identity. The dedicated candidate checker passes one safe control
and nineteen attributed single-fault known-bads. Generalized mutation evidence
is not inferred from those cases: resolve this checker's exact current row only
from `architecture/suite-guard-coverage.json`. Every unproved row is explicit
open evidence work, not positive coverage or correctness evidence.

The profile and every successor resource remain unissued and unadmitted.
Source-separated full-profile conformance, complete offline resolution,
accountable review, and operator acceptance remain false or absent. The
tranche constructs zero product identities, members, commitments, snapshots,
roots, or activations; it does not close PRQ-002, accept Gate A, or authorize
runtime work.

## PRQ-002C bounded raw-number prerequisite

[ADR 0101](decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md)
records that the frozen `odeya-jcs-0.2` candidate cannot portably distinguish
integer tokens from integral fraction or exponent tokens after ordinary host
mapping. Its architecture-only token contract therefore retains raw number
lexemes and unique instance positions before schema type evaluation.

The bounded PRQ-002C suite retains 61 opaque, answer-free synthetic frames:
9 accepted and 52 refused. Python and Node implementations with separate
source and parser strategies agree on the complete ordered staged projection,
and 44 suite-gate known-bads fire. The two fixed frames exercise only an
integer-type position and an integer-valued-const position. No generic schema
resolver, product-domain frame, ordered member map, registry snapshot, member
digest, cross-object replay, or offline archive is constructed or proved.

This observation does not amend the frozen `odeya-jcs-0.2` core, evidence,
migration record, or twelve-resource cohort. Those bytes remain unissued and
blocked from conformance and issuance. ADR 0101 itself did not construct
`odeya-jcs-0.3` or its required reissued cohort. Source-separated full-profile
conformance, accountable review, operator acceptance, PRQ-002 closure, Gate A
acceptance, and runtime authority remain false or absent.

## PRQ-002D bounded non-product prehash replay

[ADR 0102](decisions/0102-prove-non-product-prehash-schema-registry-replay.md)
retains an exact-predecessor
[contract](../architecture/prq-002d-schema-registry-prehash-contract-v1-candidate.json)
and
[contract schema](../architecture/prq-002d-schema-registry-prehash-contract.schema.json)
for one synthetic two-member replay before any structured or product identity
is constructed. The two member keys differ at `-` versus `.`, the first member
contains one absolute reference to the second, and all resolution is limited
to the pre-added in-memory registry.

The retained suite contains 68 opaque virtual-file frames. One fixed private
oracle accepts one frame and refuses 67 under the frozen precedence order.
Source- and language-separated Python and Node implementations retain complete
ordered results, self-attested byte-consistency receipts, and one exact
comparison receipt. The parent gate retains 77 known-bad mutations, each of
which must execute the same production guard and return its declared singleton
code.

This is bounded differential replay evidence, not a process sandbox, general
static analysis, independently witnessed execution, complete offline
resolution, dependency-closed product registry, cross-object product replay,
canonicalization-profile conformance, product identity, member admission,
profile issuance, PRQ-002 closure, Gate A acceptance, or runtime authority.
The frozen `odeya-jcs-0.2` bytes remain unissued. ADR 0102 itself did not
construct or test the required side-by-side `odeya-jcs-0.3`
core/evidence/migration or its reissued twelve-resource cohort.

## PRQ-002E side-by-side `odeya-jcs-0.3` construction

[ADR 0103](decisions/0103-construct-side-by-side-odeya-jcs-0-3-candidate.md)
freezes one bounded architecture-only construction graph for
`urn:odeya:canonicalization:odeya-jcs-0.3`, version `0.3.0`. It preserves
every exact `odeya-jcs-0.2` byte and constructs no alias, redirect, implicit
upcast, digest equivalence, or predecessor reinterpretation.

The exact twelve-schema successor inventory is:

| Schema path | Exact `$id` | Exact domain or role |
| --- | --- | --- |
| `schemas/schema-resource-record-v0-2.schema.json` | `urn:odeya:schema:schema-resource-record:0.2.0` | `odeya-schema-resource-record-v2` |
| `schemas/aggregate-state-subject-record-v0-2.schema.json` | `urn:odeya:schema:aggregate-state-subject-record:0.2.0` | `odeya-aggregate-state-subject-record-v2` |
| `schemas/reducer-contract-record-v0-2.schema.json` | `urn:odeya:schema:reducer-contract-record:0.2.0` | `odeya-reducer-contract-record-v2` |
| `schemas/event-contract-record-v0-2.schema.json` | `urn:odeya:schema:event-contract-record:0.2.0` | `odeya-event-contract-record-v2` |
| `schemas/ordered-member-map-commitment-v0-2.schema.json` | `urn:odeya:schema:ordered-member-map-commitment:0.2.0` | `odeya-ordered-member-map-commitment-v2` |
| `schemas/schema-registry-v0-9.schema.json` | `urn:odeya:schema:schema-registry:0.9.0` | `odeya-schema-registry-v3` |
| `schemas/aggregate-state-subject-registry-v0-8.schema.json` | `urn:odeya:schema:aggregate-state-subject-registry:0.8.0` | `odeya-aggregate-state-subject-registry-v3` |
| `schemas/reducer-registry-v0-8.schema.json` | `urn:odeya:schema:reducer-registry:0.8.0` | `odeya-reducer-registry-v3` |
| `schemas/event-contract-registry-v0-8.schema.json` | `urn:odeya:schema:event-contract-registry:0.8.0` | `odeya-event-contract-registry-v3` |
| `schemas/canonicalization-profile-core-v0-7.schema.json` | `urn:odeya:schema:canonicalization-profile-core:0.7.0` | final-only core schema; no product domain |
| `schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json` | `urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0` | final-only evidence schema; no product domain |
| `schemas/canonicalization-profile-migration-v0-2.schema.json` | `urn:odeya:schema:canonicalization-profile-migration:0.2.0` | final-only migration schema; no product domain |

The nine product domains are disjoint from `0.2` and bind only their exact
declaring schemas. A domain name, profile ID, or schema ID alone never resolves
a member. Resolution requires the expected resource ID, exact raw SHA-256, and
decimal byte count before UTF-8 decoding; after parsing, body `$id`, semantic
version, registry key, and dependency bindings must agree. Aliases, redirects,
bare-ID or `latest` lookups, and network, file, search, environment, or mutable
fallbacks refuse.

The map algorithm remains `odeya-canonical-map-commitment-v1`: it defines the
profile-independent ordered UTF-8 member-key/member-digest pair sequence. The
reissue changes its profile-bound member-digest inputs and product domain, not
that algorithm. The map algorithm, `sha-256` hash identifier,
`sha256:<64 lowercase hexadecimal digits>` lexical digest, profile ID, and
product domain are separate namespaces; none may substitute for another.

The exact retained architecture records are:

```text
architecture/canonicalization-profile-core-0.3-candidate.json
architecture/canonicalization-profile-0.3-candidate-evidence.json
architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json
```

Their only permitted finalization graph is:

```text
exact frozen odeya-jcs-0.2 bytes
  -> product-authoring transaction:
       twelve final-only odeya-jcs-0.3 schema resources
         -> exact schema raw digests and byte counts
         -> static schema-position inventory inside the final core
         -> final evidence record
         -> final migration record
       plus nine schema-valid structural-nonidentity fixtures
  -> observation-authoring transaction over the immutable 15 subjects:
       two source manifests
       + two exact observer stdout results
       + two execution receipts
       + external comparison receipt replaced last
  -> later conformance work, including downstream raw-number traces
```

Required bindings are final and non-null; retained schemas do not admit
placeholder, mixed authoring/final, or unresolved raw-binding branches. The
core does not hash itself. Evidence binds the core and schemas externally and
does not bind the later migration-record digest or a trace about its own final
bytes. Migration may bind the exact evidence record. Per-subject traces remain
downstream of their subjects. No artifact binds itself or a downstream
artifact.

Receipt-last ordering is not sufficient by itself. Product authoring must
build and validate exactly 24 outputs in an isolated same-filesystem staging
directory—twelve schemas, nine fixtures, and three records—fsync the candidate
files and directory, install only validated bytes, and install the migration
record last. Only after the twelve schemas and three records are final may the
separate observation transaction stage its seven outputs and replace the
comparison receipt last. Readback recomputes both transaction inventories and
refuses every missing, mixed-generation, stale, or mismatched subject.
Downstream per-subject traces are deliberately absent from this construction
slice and cannot be inferred from the observer results.

Before the canonicalizer sees a value, an authoritative raw-octet adapter
retains number lexemes and unique instance pointers, rejects malformed UTF-8,
BOM, JSON extensions, duplicate decoded names, decoded surrogate or
noncharacter code points, and preserves Unicode without normalization.

The final core contains a static position inventory derived only from the
twelve final schema byte strings. It binds exact schema IDs/digests and
resolved schema locations, but no concrete subject digest. A downstream trace
created after a subject is final binds that subject's raw digest/count, every
numeric token and instance pointer, and its exact static position rule.
Numeric literals in schema documents are schema-definition data, not
automatically future instance positions; metaschema evaluation is a separate
trace. A trace about the evidence record cannot be bound by that same record.

A `type: number`, a number-admitting union, an unresolved branch, a missing or
stale inventory/trace, or an unclassified numeric position refuses. Accepted
safe integers convert to IEEE-754 binary64 under `roundTiesToEven`; no generic
number-position policy is claimed.

This freeze makes a 144-resource side-by-side census measurable: 120 original
resources, 12 immutable `0.2` resources, and 12 new `0.3` resources. Two
source- and language-separated observers agree on the complete exact-byte
projection of the fifteen final schema-and-record subjects. That agreement
does not prove the static position inventory or complete raw-aware
applicability traces. The tranche constructs zero product digests, members,
commitments, snapshots, membership proofs, roots, C0 bundles, checkpoints, P0
admissions, or activations. It does not establish parser, JCS, schema, domain,
registry, migration, or profile conformance; complete offline resolution;
independent reproduction; accountable review; operator acceptance; issuance;
admission; PRQ-002 closure; Gate A acceptance; runtime; deployment;
publication; or external authority.

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
