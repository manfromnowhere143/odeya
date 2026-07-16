# Constitutional construction and sealing

Status: proposed replacement/integration architecture contract, 2026-07-16.
This document freezes how a future version of Odeya may construct
constitutional identity subjects without recursive hashes, self-attestation,
or placeholder promotion. The existing EngineContractRoot, C0RegistryBundle,
RootAuthorityManifest, LedgerCheckpoint, and RegistryActivation schema bytes do
not implement or conform to this two-digest profile. It creates no real root,
C0 bundle, checkpoint, P0 admission, RegistryActivation, Gate A acceptance, or
runtime authority.

The machine-readable contracts are
[`constitutional-construction-order.schema.json`](../architecture/constitutional-construction-order.schema.json)
and
[`blocked-construction-receipt.schema.json`](../architecture/blocked-construction-receipt.schema.json).
The finite adversarial suite is described in
[`tests/constitutional-construction`](../tests/constitutional-construction/README.md).

The identifiers ending in `-core-v1` and `-seal-v1` in the construction-order
fixture are domain reservations, not usable digest profiles. The canonical
profile, digest-input framing, and replacement digest-contract shapes remain
explicitly unresolved and blocking. Until all three are frozen under new
schema identities, no constitutional core or seal digest may be constructed.

## Frozen prospective construction order

Every replacement constitutional family must follow one directed construction
order after new schema identities and the complete consumer migration are
reviewed:

```text
canonical core projection
        |
        v
domain-separated core digest
        |
        v
independent evidence over that core digest
        |
        v
seal subject = unchanged core fields + ordered evidence references
        |
        v
domain-separated seal digest
        |
        v
external attestations over the seal digest
```

No edge may point upward. Evidence cannot bind a seal digest that does not yet
exist. A core cannot contain the evidence produced over its digest. An external
attestation cannot be included in the digest it signs. A child core cannot
contain the identity, sequence, reference, or digest of a later parent wrapper.

Let `C` be the canonical core projection, `E = (e_1, ..., e_n)` the canonically
ordered evidence-reference sequence, and `S(C,E)` the final seal projection.
Under the pinned canonicalization and hash profile:

```text
D_core = H(domain_core, canonical_bytes(C))
e_i.subject_digest = D_core
D_seal = H(domain_seal, canonical_bytes(S(C, E)))
attestation_j.signed_digest = D_seal
```

`H` is not ambiguous string concatenation. The replacement canonicalization
profile and domain separator must define exact bytes and framing. A future
schema version may retain names such as `root_digest`, `bundle_digest`,
`checkpoint_digest`, `p0_digest`, and `activation_digest` for final seal
digests, but this contract does not assert that the existing fields implement
this construction. `D_core` is a prospective intermediate evidence target and
never substitutes for the final subject identity.

## Family projections

The prospective excluded paths and reserved core/seal domain separators live
in the machine-readable construction-order contract. They cannot become
computable digest contracts until the canonical and framing profile closes.
Every profile names its current
0.1/0.2 source candidate only for migration analysis and fixes
`existing_schema_bytes_conform = false`. Replacement schema IDs are deliberately
unassigned. The intended semantic roles are:

| Family | Core excludes | Evidence target | Final seal excludes |
|---|---|---|---|
| `EngineContractRoot` | independent-validation refs, review refs, root digest contract, root digest | root core digest | any later external attestations |
| `C0RegistryBundle` | compatibility/review refs and bundle digest fields | C0 core digest | any later external attestations |
| `LedgerCheckpoint` | checkpoint digest fields and signatures | checkpoint core or pre-seal verification subjects | signatures |
| P0 constitutional recovery admission | admission-evidence refs and P0 digest fields | P0 core digest | parent RegistryActivation identity and attestations |
| `RegistryActivation` | review refs, activation digest fields, attestations | activation core digest | attestations |

The seal assembler must prove that the core projection used after evidence is
byte-identical to the core projection that produced `D_core`. Any changed core
field invalidates the evidence set and restarts construction from phase one.
Evidence references are ordered under an explicit canonical set rule; arrival
order, filesystem order, database order, and UI order are never identity.

A replacement `RootAuthorityManifest` contract must distinguish evidence that
signs a referenced decision artifact from final attestations over the enclosing
manifest. The current source candidate does not yet implement the prospective
core/seal profile; integration must prevent the bootstrap declaration from
self-signing its own bytes.

## P0 is activation-independent

`P0.constitutional-recovery-admission` is complete before its parent activation
is assembled. Its nonrecursive boundary requires all of the following:

- activation references are forbidden;
- activation identity and sequence are absent;
- a parent activation digest is absent;
- self-issued root authority is forbidden;
- the P0 root and C0 references must equal the later activation's root and C0
  references; and
- the later activation must embed and bind the exact sealed `p0_digest`.

The last rule is a construction obligation on the outer wrapper, not a
back-reference from P0. Commands may later bind an activation identity,
sequence, and digest. That does not alter P0's bytes or identity.

## Cross-object admission equalities

JSON Schema can constrain each record's shape but cannot prove arbitrary
equality across separately resolved objects. Admission therefore requires a
closed semantic check over resolved bytes, not reference-shaped lookalikes.

The checker must reject at least these mutations:

- C0 root or component digests differ from the exact EngineContractRoot;
- checkpoint root or C0 digests differ from the resolved subjects;
- outer activation root, C0, checkpoint, or P0 digest differs from embedded
  P0;
- recovery-frontier reference digest, epoch, or position disagrees with the
  resolved frontier, checkpoint, or activation order;
- witness identities or failure domains repeat, or a witness observes another
  checkpoint digest;
- admitted command count/set differs from generated envelope discriminators or
  handler count/set/digest;
- an activation sequence after one lacks an exact predecessor;
- a recovery-bounded activation enables R2+ risk, production, external
  dispatch, publication, spending, or physical action;
- an activation attestation signs anything except the activation seal digest;
- a recovery quorum exceeds distinct principals; or
- an operational root collapses execution with safety/verification or proposal
  with publication.

These are required semantic failures even when every individual JSON document
passes its local schema.

## Blocked-construction receipts

When any required real subject, evidence package, equality proof, signature
verification, handler-conformance proof, or independent review is absent,
construction stops and may emit only a `BlockedConstructionReceipt`.

That receipt has constants, not optimistic status fields:

```text
construction_status = blocked
admission_claim = not_admitted
activation_claim = not_activated
gate_a_claim = not_accepted
runtime_authority = none
```

It inventories exact blockers, missing real subjects, and any synthetic,
structural-fixture, or unresolved inputs. Every observed placeholder has
`usable_for_admission = false`. The closed schema forbids extra `p0_digest`,
`activation_digest`, witness, handler-conformance, Gate A, or authority claims.
A blocked receipt is diagnostic evidence only; it is never an alternative
construction path and cannot be upgraded in place. After blockers resolve, a
new construction attempt begins from the frozen core.

## Required implementation sequence

Before executable construction code is authorized:

1. assign new schema identities for every changed constitutional family and
   migrate the complete transitive consumer graph without same-ID byte reuse;
2. freeze the canonical core projection and domain separator for each family;
3. implement two independently checked core-projection/digest paths;
4. define evidence schemas that name `D_core` as their exact subject;
5. define canonical evidence-set ordering and duplicate rejection;
6. assemble the seal only from the unchanged core and verified evidence refs;
7. recompute the core projection from the seal and require equality with the
   evidenced core bytes;
8. compute the final seal digest;
9. verify external attestations against only that seal digest;
10. resolve all referenced objects and run cross-object equalities; and
11. emit either a candidate construction result for independent admission
    review or a blocked-construction receipt—never a partial P0 or activation.

The architecture fixtures contain synthetic digest-shaped values solely to
exercise these predicates. They are not canonicalization evidence, real
witnesses, handler evidence, roots, C0, P0, or activation.

## Current disposition

The prospective construction order and adversarial obligations are now
explicit. Integration into replacement EngineContractRoot, C0RegistryBundle,
RootAuthorityManifest, LedgerCheckpoint, P0, RegistryActivation, and every
transitive consumer schema remains a blocker. The real constitutional chain is
also blocked: immutable real members, independently verified roots,
non-self-issued operational authority, checkpoint signatures and witnesses,
handler-conformance evidence, cross-object resolution, and independent review
have not been produced. Architecture validation must report both boundaries;
it must not materialize the missing subjects or claim the current schema bytes
conform.
