# Engine Contract Root and Registry Topology

Status: proposed Gate A contract, 2026-07-15. This document defines the
acyclic identity and activation topology for Odeya's machine-interpretable
constitution. It does not activate a runtime, admit an unfinished command, or
authorize product implementation.

## Why one root is necessary

A schema digest alone does not establish a command's meaning. A command is
interpretable only with the exact payload schema, event alternatives, reducer,
aggregate-state subject, semantic and policy rules, resource/unit profile,
canonicalization profile, module owner, and method contracts that were
compatible at admission. Resolving any of those through `latest`, a mutable
URL, or a current deployment would make historical receipts change meaning.

Odeya therefore seals one `EngineContractRoot` over a compatible set of pure
registry snapshots. A ledger checkpoint commits that root and its component
digests. A later, separate activation record authorizes a root for a bounded
scope and position. The root describes meaning; the checkpoint witnesses
history; the activation makes a prospective selection. None is a substitute
for the others.

## Acyclic identity topology

```text
canonical member subjects (no parent/snapshot/activation/checkpoint refs)
                  |
                  v
independently hashed registry snapshot subjects
                  |
                  v
EngineContractRoot subject (compatible snapshot refs only)
                  |
                  v
C0RegistryBundle subject (root + trust/bootstrap commitments)
                  |
                  v
LedgerCheckpoint (commits exact C0 bundle and ledger frontier)
                  |
                  v
RegistryActivation (root/snapshot + checkpoint + bounded scope)
  + embedded P0 constitutional-recovery admission
```

An arrow means "may contain an exact reference to." No reverse arrow is
allowed. In particular:

- a member record never contains its parent registry digest or membership
  proof;
- a registry snapshot never contains its activation or future checkpoint;
- an engine root never contains an activation;
- a C0 bundle never contains an activation that points back to its checkpoint;
- a checkpoint may commit the root and snapshots, but those subjects cannot
  contain that checkpoint;
- an activation is created only after the checkpoint and may reference both;
  and
- an envelope or receipt may bind the immutable snapshot/member plus the
  later activation, without changing any of their identities.

Membership proofs, signatures, witness attestations, storage locations, and
activation evidence are external wrappers. Re-signing, relocating, witnessing,
or activating a subject cannot change its canonical digest.

## Registry families

The founding root binds exactly these semantic families:

| Family | Canonical subject | What it fixes | What it cannot prove |
|---|---|---|---|
| schema | schema member set | schema ID, semantic version, byte digest, dialect, root type, compatibility/read policy | that bytes are safe or semantically correct |
| command | admitted command records only | selector, payload, owner, target, authority mode, rules, legal event/cohort alternatives, limits, traces | handler existence or deployment conformance |
| event | admitted event records only | discriminator/version, payload branch, owner, producer commands, privacy/retention class | legal state consequence by itself |
| reducer | one reducer per aggregate type | origin, accepted events, total fold, state axes, transition/invariant rules, upcasts, traces | persistence isolation or a deployed implementation |
| aggregate-state subject | aggregate state records | exact state schema, origin/absence semantics, version/digest contract, reducer owner | current state without replay/checkpoint evidence |
| resource/unit profile | typed dimensions and units | quantities, currencies, physical dimensions, precision, conservation and non-conversion laws | capacity, permission, or observed use |
| semantic rule | pure predicates | exact inputs, tri-valued outcomes, consequences, complexity, vectors, implementations | scientific truth beyond its declared scope |
| policy | admission policy records | rule bundle, risk/data/action scopes, obligations, denial/indeterminate behavior | caller authority or external-world outcome |
| method | scientific methods | assumptions, estimands, guarantees, applicability, numerical profile, controls, independent implementations | that assumptions hold in a particular run |
| module dependency | logical ownership graph | one owner, dependency direction, aggregate ownership | future source-code import conformance |
| canonicalization | byte identity profile | parser, normalization, number/string/key rules, domain-separated digest projection | scientific equivalence or signature validity |
| trust/bootstrap | constitutional roots | accepted signing/witness roots and genesis procedure | an ordinary domain grant or scientific conclusion |

Command, event, reducer, and aggregate-state registries form one closed graph.
A command record may reference only event, reducer, state, schema, and rule
members in the same compatible root. An event has one canonical aggregate
owner. That aggregate has exactly one admitted reducer. The reducer accepts the
event and emits exactly one state subject version or a typed reduction failure.
No registry may repair a missing edge by name convention.

## Registry subject contract

Every registry snapshot subject contains:

```text
registry kind, stable ID, semantic version
previous registry subject reference or null
canonicalization profile identity and digest
ordered canonical member subjects
compatibility and historical-read policy
source-manifest and generator identities, where generated
known limitations and review-evidence references
digest projection contract
```

The registry digest is outside the hashed subject or explicitly excluded by
the closed digest projection. Effective time, signatures, seal position,
storage, membership proofs, and activation are external records. A mutable
`status` field is not part of registry-subject meaning. Proposed, admitted,
active, suspended, and retired are decisions or activations about an immutable
subject, not lifecycle mutations to its bytes.

Members sort by the canonical tuple declared by that registry, normally
`logical_id + semantic_version`. Duplicates, aliases, case-fold collisions,
unbounded extension maps, unresolved references, or semantically unordered
sets fail root construction. Array order never acquires meaning accidentally:
each array is declared ordered, canonical-set-sorted, or multiset-forbidden.

## `EngineContractRoot`

The root subject contains exact subject references for every required registry
family, plus:

- a stable root ID and semantic version;
- the Gate A admitted command/event/reducer/state closure identifier;
- exact canonicalization and digest profiles used for every component;
- a compatibility matrix binding allowed component tuples;
- required reader capabilities and fail-closed behavior;
- a component-set Merkle or ordered-set commitment with cardinality;
- the generation/source manifest and toolchain identity;
- independent validation package references;
- the complete known-limitation set; and
- a digest projection that excludes only its external digest/attestations.

The root contains no tenant, mission, current time, checkpoint, activation,
handler deployment, database, provider, or product-UI state. Those facts are
prospective operational evidence and cannot redefine the root.

## C0 bundle and checkpoint

`C0RegistryBundle` binds the engine root, its component snapshots, the
root-authority/trust bootstrap manifests, and the exact schema needed to verify
the bundle. It is a pure immutable subject. Its ordered component commitment
must equal the engine root and must not silently add or omit a registry.

`LedgerCheckpoint` independently commits:

- the C0 bundle/root digest;
- the inclusive ledger position and epoch;
- canonical C1 event/receipt/admission-evidence and C2 artifact commitments;
- previous-checkpoint continuity;
- witness policy and observed signatures; and
- the exact checkpoint digest projection.

Bootstrapping does not permit self-certification. Genesis validation starts
from a separately distributed and operator-reviewed bootstrap manifest that
pins the schema/canonicalization bytes and expected first C0 bundle digest.
The first checkpoint can witness that bundle; it cannot create its meaning.

## Activation

`RegistryActivation` is an immutable prospective decision containing:

```text
activation ID and sequence
exact engine root and component snapshot refs
exact checkpoint/epoch/branch and activation position
non-self-issued root-authority manifest/bootstrap evidence
external checkpoint-witness set and consistency verdict
embedded P0 constitutional-recovery admission digest
clear current recovery/fork/quarantine frontier and digest
tenant/mission/namespace scope
admitted command subset and required handler-conformance set
not-before/not-after controlled-time bounds
root-authority and policy decision evidence; no self-issued operational grant
rollback/supersession target
```

`P0.constitutional-recovery-admission` is embedded in the activation but has no
back-reference to it, preserving acyclicity. P0 is not a command, event, grant,
aggregate, policy result, or handoff assertion. The constitutional
genesis/recovery ceremony creates it only after independently resolving the
RootAuthorityManifest, EngineContractRoot, C0 bundle, witnessed checkpoint, and
current recovery frontier. Its disposition is clear only when the selected
epoch/branch has no unresolved fork, quarantine, restore ambiguity, or
consistency failure. Fork detection, quarantine, recovery ambiguity, epoch or
root change, checkpoint witness failure, expiry, or supersession invalidates
the activation fail-closed.

Every admitted CommandEnvelope, CommandReceipt, and AdmissionEvidenceBundle
must bind the same activation ID, sequence, digest, P0 digest, root, checkpoint,
scope, and recovery-frontier digest. JSON Schema can require those fields;
admission must still prove byte equality, currentness, branch ordering, and
scope coverage. No ordinary mission command may create or repair its own P0.

Activation requires `activation_position <= target/current_position` on the
selected clear branch and exact equality with the P0 recovery frontier. The
enabled envelope discriminator set, enabled command member set, and conforming
handler set must be exactly equal. Runtime handler evidence is intentionally
absent from Gate A; therefore a Gate A root can be contract-admitted and
checkpoint-ready while remaining operationally inactive.

Retirement is prospective. Historical receipt replay resolves the exact prior
activation, root, member, schema, event, reducer, and rules. It never replays
under the current root. Changed bytes under a settled command ID produce no new
receipt or execution.

## Aggregate origin and replay

Before an origin event, an aggregate is absent; there is no fabricated version
zero state record. An origin event creates version one under one reducer. Every
subsequent accepted event consumes the exact predecessor version/root and emits
the next version/root. Registry membership never embeds a changing aggregate
head.

Replay takes:

```text
engine root + reducer member + original event bytes
+ prior state subject (or explicit absence at origin)
-> next state subject | typed fail-closed reduction error
```

Unknown event versions, missing schemas/rules, incompatible roots, gaps,
duplicate positions, branch ambiguity, digest mismatch, or a reducer/state
identity mismatch block replay. A wall clock, current registry, database row,
projection, model answer, or UI state cannot choose a branch or fill a gap.

## Generation and independent conformance

Generated artifacts have one reviewed source manifest and a pinned generator
identity. At minimum the generator emits:

- admitted-only envelope branches;
- command/event/reducer/state registry subjects;
- design-vocabulary exclusions;
- membership and cross-registry edge tables;
- schema-resolution indexes;
- digest vectors and ordered roots; and
- human-readable catalog tables.

Two independently implemented validators, using different language/runtime
stacks, must reproduce canonical bytes, member ordering, every component
digest, the engine root, all graph edges, and the expected refusal corpus. One
implementation generating and validating its own output is not independent
evidence.

The conformance suite must include at least:

1. member embeds parent snapshot digest;
2. snapshot embeds activation/checkpoint;
3. activation points to a future or wrong-branch checkpoint;
4. schema ID matches while retained bytes differ;
5. command/event/reducer/state edge missing or duplicated;
6. reserved design name enters the admitted set;
7. extra handler, missing handler, or handler bound to another member;
8. event has zero or two aggregate owners;
9. aggregate has zero or two canonical reducers;
10. reducer accepts an undeclared event or silently ignores an unknown field;
11. origin starts from a fabricated version-zero state;
12. current root is used to replay a historical receipt;
13. array order or Unicode/number/parser differences change a component root;
14. component registry valid alone but incompatible with the root tuple;
15. C0 bundle/root component sets differ;
16. checkpoint commits one root while activation names another;
17. self-digest or signature bytes enter a subject digest; and
18. generator and independent validator agree only because they share code or
    fixtures generated by the implementation under test.

## Gate A acceptance boundary

This topology closes only when exact machine schemas and candidate instances
exist for every founding registry, the admitted first-slice graph is named and
dependency-closed, all referenced bytes are present, identities reproduce in
two independent validators, composite replay and expected-refusal traces pass,
critical/high review findings are closed, and Daniel signs the exact candidate
manifest.

Until then the engine-contract root is a precise candidate design. It is not a
runtime activation, autonomous-science claim, production recovery proof,
customer-readiness claim, or permission to build product code.
