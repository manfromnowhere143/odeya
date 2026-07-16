# ADR 0015: Freeze nonrecursive constitutional construction

- Status: Proposed
- Date: 2026-07-16
- Gate: G2/G3/G5/G6/G7; construction contract only, no admission, activation, implementation authority, or Gate A acceptance

## Context

Several constitutional schemas contain review or validation evidence references
inside the subject's final digest projection. If evidence is expected to sign
that final digest, construction is recursive: the digest needs the evidence
reference while the evidence needs the digest. External signatures create the
same problem when included in the bytes they sign.

The abstract first-slice checker also required P0 to bind its parent activation
digest, while the concrete `RegistryActivation` schema correctly prohibited
that back-reference. That contradiction made the claimed P0 boundary
impossible despite local tests passing.

Finally, structural fixtures can look digest-complete while lacking real
resolved bytes, witnesses, signatures, handler conformance, equality proofs,
or independent review. No receipt contract prevented those placeholders from
being mislabeled as admitted P0 or activation.

## Decision

Adopt a prospective replacement/integration construction law defined in
[`CONSTITUTIONAL_CONSTRUCTION_AND_SEALING.md`](../CONSTITUTIONAL_CONSTRUCTION_AND_SEALING.md)
and freeze it in
[`constitutional-construction-order.schema.json`](../../architecture/constitutional-construction-order.schema.json):

1. canonicalize the core projection;
2. compute a domain-separated core digest;
3. produce independent evidence that binds that core digest;
4. assemble the seal subject from the byte-identical core plus canonically
   ordered evidence references;
5. compute the domain-separated seal digest; and
6. produce external attestations that bind the seal digest and are excluded
   from it.

The machine contract reserves distinct candidate core and seal domain names,
but it also fixes the current readiness facts to false: the canonicalization
profile, digest-input framing, and replacement digest-contract shapes are not
frozen. Those reservations therefore cannot be used to construct or label a
constitutional digest. Closing all three under new schema identities is a
prerequisite to applying the six-step law.

The current EngineContractRoot, C0RegistryBundle, RootAuthorityManifest,
LedgerCheckpoint, and RegistryActivation schema bytes do not conform to this
profile. Their existing IDs remain untouched. A future replacement version may
retain familiar final digest field names, but it must add the explicit
intermediate core-digest/evidence contract. Its seal assembler must re-project
the core from the final subject and prove byte equality with the evidenced core
before computing the seal digest.

P0 is explicitly activation-independent. It contains no activation identity,
sequence, reference, predecessor, or digest. The later RegistryActivation
embeds the exact P0 subject and binds its final `p0_digest`; commands bind the
later activation. This preserves the one-way topology.

Cross-object admission equality is mandatory and external to local JSON Schema
shape checks. The architecture checker rejects mismatched root/C0/checkpoint/P0
references, component sets, frontiers, witnesses, command/envelope/handler
sets, activation sequence, fail-closed scope, attestation digest, recovery
quorum, and critical role separation.

If construction cannot prove all required real inputs and equalities, it may
emit only the fail-closed receipt defined by
[`blocked-construction-receipt.schema.json`](../../architecture/blocked-construction-receipt.schema.json).
That receipt is necessarily blocked, non-admitted, non-activated,
non-Gate-A-accepted, and non-authoritative. Placeholder inputs are always
marked unusable for admission, and prohibited subject/authority outputs cannot
be added to the closed receipt.

## Consequences

- Once the blocked canonical/framing prerequisites and replacement schemas
  close, evidence generation will have a stable, computable subject identity
  without weakening the final seal; this ADR does not claim one exists now.
- Re-reviewing or re-attesting does not mutate the evidenced core. A changed
  core invalidates evidence and restarts construction.
- P0 can be sealed before RegistryActivation without a digest cycle.
- A structurally valid individual object is insufficient for admission;
  resolved cross-object semantic equality remains required.
- Synthetic fixtures may exercise the contracts but can never be promoted by
  relabeling their status.
- Implementations need explicit core-projection code, canonical evidence-set
  ordering, re-projection equality, and external attestation verification.
- Integration requires new schema identities for every changed family and a
  complete transitive consumer migration; a four-schema partial migration is
  prohibited.

## Alternatives rejected

- Have evidence sign the final subject digest: recursive when the final subject
  binds evidence references.
- Exclude all evidence references from final identity: permits evidence
  substitution without changing the sealed subject.
- Put the activation digest inside P0: creates a direct parent-child digest
  cycle.
- Treat JSON Schema validity as cross-object equality: schemas do not resolve
  and compare arbitrary referenced bytes.
- Reuse a partial candidate or fixture as an admitted subject: provenance and
  missing evidence would be hidden behind digest-shaped placeholders.

## Acceptance boundary

This decision, its schemas, fixtures, and tests are architecture evidence only.
They do not fabricate or admit a RootAuthorityManifest, EngineContractRoot, C0
bundle, checkpoint witness, P0, RegistryActivation, handler set, or runtime.
Gate A remains blocked until real subjects and evidence are constructed in this
order under replacement schemas, the canonicalization/framing/digest-contract
profiles are frozen, the complete consumer graph is migrated, independent
validators reconcile the results, and the exact candidate is accepted through
the existing review and operator gates. Nothing in this ADR claims that the
current core-family schemas conform to the prospective profile.
