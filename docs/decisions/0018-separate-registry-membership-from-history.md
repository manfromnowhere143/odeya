# ADR 0018: Separate registry snapshot membership from transparency history

- Status: Proposed
- Date: 2026-07-16
- Gate: G2/G3/G4/G6/G7; architecture-only identity and recovery decision

## Context

Odeya needs to prove two different facts:

1. an exact contract member belongs to one immutable registry snapshot; and
2. one immutable registry snapshot is part of an append-only, witnessed
   sequence of registry states.

Those facts have different ordering and proof semantics. A registry snapshot is
a deterministic map/set ordered by an admitted member-key profile. A
transparency history is ordered by insertion and checkpoint position. Sorting
the history destroys temporal meaning; making a member hash its registry or
membership proof creates a content-identity cycle.

The current structural schemas already intend the dependency direction
`schema -> state -> reducer -> event -> command -> registry -> root`, but some
fixtures and prose blur snapshot, membership, checkpoint, and activation
identities. That ambiguity must close before immutable members are constructed.

## Decision

Adopt two separate immutable structures.

### Registry snapshot

A pure registry snapshot contains:

- registry family ID and semantic version;
- exact canonicalization and commitment profiles;
- a closed, deterministically ordered map of
  `(member_key, member_digest)` pairs;
- exact member count and set commitment;
- optional reference to the exact prior registry subject it supersedes; and
- a digest over the snapshot core, excluding its digest, attestations,
  checkpoints, activation, storage location, and membership proofs.

Member keys use one frozen bytewise ordering profile. Member records never
contain their parent snapshot, membership position, proof path, history
checkpoint, activation, or signature.

A membership receipt is an external derived proof containing at least the
registry family and version, registry digest, member key and digest, commitment
profile/root, leaf index, tree size, and inclusion path. Creating another
receipt for the same member/snapshot does not change either identity.

### Transparency history

A separate append-only history log contains registry snapshot digests as
insertion-ordered leaves. Its signed checkpoints contain the log identity and
origin, tree size, root hash, signature purpose/key identity, and exact
checkpoint position. Consistency proofs link an older signed checkpoint to a
newer signed checkpoint. Independent witness observations and cosignatures are
external evidence over a checkpoint; they do not enter the checkpoint digest
they attest.

The history log cannot decide whether a registry member or snapshot is
scientifically, semantically, or constitutionally admissible. Odeya's
deterministic registry builder and admission verifier own those decisions. A
valid inclusion proof establishes bounded membership or history inclusion
under the selected commitment profile, not truth, completeness, currentness,
or a unique global view.

### Constitutional ordering

The only permitted order is:

```text
exact member subjects
  -> pure registry snapshots
  -> EngineContractRoot core/seal
  -> C0 core/seal
  -> signed history checkpoint
  -> inclusion/consistency evidence
  -> independent witness quorum
  -> recovery-frontier verification
  -> P0 core/admission seal
  -> handler equality evidence
  -> RegistryActivation core/seal
```

P0 is activation-independent. The later activation binds P0; P0 does not bind
its parent activation. Commands subsequently bind both exact identities and
re-evaluate currentness against retained history, controlled time, policy,
authority, and recovery state.

### Root succession

Registry and root replacement is prospective and rollback-resistant. A new
root does not reinterpret prior members or receipts. Root/key rotation must
retain an authenticated succession path with thresholds over the old and new
trust configurations, exact monotonically advancing versions, expiry/freeze
checks, and no skipped intermediate root state. Historical replay resolves the
exact prior root and schemas; it never uses `latest`.

## Standards comparison

This decision uses reviewed external designs as bounded comparison evidence:

- RFC 9162 supplies ordered Merkle inclusion and consistency constructions but
  does not establish statement correctness or prevent every split view alone.
- RFC 9942/9943 SCITT receipts keep registration evidence external to the signed
  statement and permit independent registrations.
- C2SP checkpoint and witness formats demonstrate checkpoint cosignatures
  without putting the cosignature into the tree head it signs.
- TUF 1.0.35 demonstrates rollback/freeze refusal, consistent snapshots,
  threshold roles, and old-plus-new authorization during root succession.
- Tessera distinguishes sequenced, integrated, and checkpoint-published log
  entries and leaves ecosystem admission to the log personality.

Odeya does not inherit certificate, package-manager, public-log, or service
availability assumptions from those systems. Exact profiles, privacy limits,
proof algorithms, witness policy, trust bootstrap, and failure consequences
remain Odeya-owned and must be frozen separately.

## Consequences

- Standalone member schemas are required; anonymous nested registry definitions
  are not sufficient final identities.
- Registry membership proofs, signatures, Sigstore/DSSE bundles, SCITT
  receipts, history checkpoints, and witness evidence remain outside members.
- Registry map ordering and history insertion ordering receive distinct profile
  identifiers and conformance vectors.
- A valid snapshot may be checkpoint-ready while remaining operationally
  inactive. No placeholder handler, external witness, or recovery verdict may
  be manufactured to cross that boundary.
- Cross-object validation must reject a parent snapshot embedded in a member,
  sorted history, mismatched member/root pair, wrong checkpoint/root pair,
  missing consistency path, duplicate witness identity or failure domain,
  future frontier, rollback, freeze, skipped root, or activation/P0 cycle.

## Alternatives rejected

- One sorted append-only structure for both membership and history: sorting
  erases insertion order and makes rollback/currentness semantics ambiguous.
- Member-embedded membership proofs: a proof depends on the parent set and
  creates identity recursion or re-identity on unrelated membership changes.
- Checkpoint or activation inside registry identity: witnessing and activation
  occur after the registry exists and would create a future back-reference.
- A mutable `current` registry alias for replay: it silently changes historical
  interpretation and defeats exact retry semantics.
- Transparency service admission as scientific admission: log integrity cannot
  decide evidence quality, authority, or claim validity.

## Acceptance boundary

This ADR fixes the topology only. Gate A remains blocked until the exact
snapshot, member, membership-receipt, history-checkpoint, consistency,
witness-quorum, recovery-frontier, P0, handler-equality, and activation schemas
and vectors exist; two non-sharing implementations reproduce all identities
and proofs; adversarial cases fail; and the exact candidate receives operator
acceptance. It authorizes no runtime, log deployment, external registration,
signature issuance, activation, or product implementation.
