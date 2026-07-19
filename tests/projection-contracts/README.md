# Projection contract cases

This isolated package exercises the proposed machine-readable contracts in
[`docs/PROJECTION_CONTRACTS.md`](../../docs/PROJECTION_CONTRACTS.md). It adds no
runtime, command/event discriminator, canonical aggregate, product surface,
publication authority, or Gate A acceptance.

Run:

```bash
/tmp/odeya-architecture-venv/bin/python tests/projection-contracts/check.py
```

The checker validates four closed JSON Schemas and eight synthetic valid
fixtures: private cockpit, thesis intake, public research, static architecture
fixture, redaction manifest, live and static reducer-equivalence results, and a
deletion fanout/impact record. Its 63 cases include all 25 required adversarial
vectors, 37 schema-level rejections, 26 bounded local semantic cases, exact
root/C0/checkpoint package-binding checks, and the isolated schema-reference
closure audit. The synthetic current projection fixtures bind ResearchEvent
references to the live `0.18.0` schema identity and include an attributed
known-bad proving that a stale identity is refused. This bounded fixture check
does not migrate, invalidate, or reinterpret retained historical event records.

## Acyclic construction

The snapshot, redaction manifest, equivalence result, and impact record contain
no self digest or successor/enclosing projection content digest. Their order is:

1. compile redaction, equivalence, and impact subjects against exact canonical
   source, engine-root, C0, and checkpoint identities;
2. build the schema-valid projection snapshot using externally issued exact
   references to those subjects;
3. canonicalize each complete subject and issue its canonical-object identity
   externally; and
4. optionally bind those identities in a later package/root whose digest scope
   is separately defined and cannot point back into a constituent's digest
   input.

The equivalence record compares a normalized semantic vector whose domain
explicitly excludes the snapshot envelope and equivalence reference. It never
compares or embeds the whole projection digest. `not_run` is valid only for the
explicitly static, non-live, unreleased, non-authoritative fixture.

## Evidence boundary

The checker proves closed shapes and bounded local relations such as frontier
equality, controlled-time lease ordering, complete section coverage, canonical
exact-decimal lexical safety, `Decimal` interval semantics, exact public
release-chain equality inside one snapshot, independent
reducer identity, semantic-vector equality, impact count reconciliation, and
tombstone-only byte destruction.

It does not dereference or recompute canonical digests, prove registry
membership, execute independent reducers, observe a real cache/CDN/recipient,
prove thesis noninterference or timing bounds, execute correction/deletion/
rights/recovery fanout, prove publication settlement, establish accessibility,
or authorize release. Those remain cross-object, runtime, independent-review,
and operational evidence obligations.
