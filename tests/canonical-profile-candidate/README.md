# Canonical profile candidate binding checks

Status: architecture-only evidence for the proposed `odeya-jcs-0.1`
parameter freeze. The profile remains unissued and Gate A remains blocked.

This suite checks a deliberately nonrecursive construction:

```text
profile core without a self-digest
  -> external raw-byte binding
  -> retained two-path conformance evidence
  -> current schema-domain and migration inventory
```

`architecture/canonicalization-profile-core-candidate.json` freezes the exact
candidate parser, RFC 8785 serialization, envelope, digest framing, future
profile-reference shape, timestamp, decimal, collection, digest-domain, and
version-axis parameters. It does not contain its own digest.

`architecture/canonicalization-profile-candidate-evidence.json` binds the
core and core-schema raw bytes, the nine retained conformance artifacts, the
21 digest-domain constants currently declared by schemas, and the current
blocking migration audit. Raw-byte binding bootstraps review of the profile;
it is not a canonical object digest and must not be relabeled as one.

The checker recomputes all bindings from local bytes, compares parser limits
with the vector manifest, compares the eight explicit version axes with the
Gate A inventory, extracts domain constants from every current schema, and
requires the profile, migration, acceptance, and authority boundaries to stay
fail-closed. One safe reference and 26 known-bad mutations exercise aliasing,
self-reference, parser ambiguity, unsafe numbers, serializer substitution,
envelope drift, fabricated digests or acceptance, incomplete domain/version
inventories, evidence-hash drift, and authority escalation.

Run:

```bash
python3 tests/canonical-profile-candidate/check.py
```

A pass establishes only that the candidate parameters and their bounded local
evidence agree. It does not prove organizational independence, independent-host
reproduction, complete migration, complete schema retention, cryptographic
admission, operator acceptance, Gate A completion, runtime safety, scientific
truth, deployment authority, or external-effect authority.
