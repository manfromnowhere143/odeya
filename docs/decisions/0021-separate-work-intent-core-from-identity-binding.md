# ADR 0021: Separate the WorkIntent semantic core from identity binding

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-16
- Decision owners: work, canonical identity, contracts, security, recovery
- Gate effect: advances C5/PRQ-009 construction evidence; does not issue a
  profile or WorkIntent identity, close PRQ-009, accept Gate A, or authorize
  assignment or runtime work

## Context

The retained `work-intent:0.1.0` candidate places `canonical_digest` inside the
same object whose future canonical bytes that field would identify. Under the
candidate Odeya envelope, hashing that complete object would require the digest
to be known before its own preimage exists. The field is currently null, so the
resource correctly remains unresolved, but filling it in place would create a
recursive identity construction.

Replacing WorkIntent alone would also break the exact current resource graph.
`canonical-work-lease:0.1.0` and `work-contract:0.2.0` both name
`work-intent:0.1.0`, and the lifecycle checker enforces the same identity. This
repository does not yet contain a complete offline predecessor registry that
could make a missing intermediate resource safe.

The construction is informed by four primary specifications:

- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) supplies a repeatable
  JSON representation and preserves array order while rejecting ambiguous
  input classes required by the local profile.
- [JSON Schema 2020-12 Core](https://json-schema.org/draft/2020-12/json-schema-core.html)
  treats `$id` as the schema resource's canonical URI, so changed schema bytes
  require a new exact resource identity rather than a mutable alias.
- [SLSA provenance verification](https://slsa.dev/spec/v1.2/verifying-artifacts)
  verifies an external statement's subject against the artifact digest.
- The [OCI image manifest specification](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
  uses external descriptors to bind content digests and sizes and models
  subject relationships between separate content-addressed objects.

These specifications do not define Odeya's authority model. They support the
nonrecursive separation between subject bytes and the evidence that binds
those bytes.

## Decision

Freeze one prospective `work-intent-core:0.1.0` semantic subject and bind it
from a separate `work-intent-identity-candidate-evidence:0.1.0` record.

The semantic core:

- is the exact retained WorkIntent 0.1 safe-fixture projection after removing
  only `identity_resolution_status`, `canonicalization_profile_ref`, and
  `canonical_digest`;
- contains no profile binding or canonical self-digest;
- keeps every lease, grant, reservation, materialization, dispatch, spend, and
  external-effect authority false or absent;
- requires fixed six-digit UTC timestamps and safe-domain integers; and
- scopes all three retained digest fields while explicitly marking their
  legacy reference shapes as requiring reissue before admission.

The external evidence record binds:

- exact raw bytes and byte counts for the core and core schema;
- the exact frozen-but-unissued profile-core reference;
- the retained WorkIntent 0.1 schema and safe-fixture projection;
- exact current bytes for the two direct schema consumers; and
- the ordered prospective reissue set:
  `work-intent:0.2.0`, `canonical-work-lease:0.2.0`, then
  `work-contract:0.3.0`.

Raw-file SHA-256 values in this evidence are bootstrap review bindings. They
are not Odeya canonical object digests and may not be relabeled as admission,
registry membership, operator acceptance, or active-root proof.

Keep the three current schema resources byte-unchanged in this tranche. Their
future resource versions and all direct validation consumers must migrate in
one reviewed commit with immediate-predecessor lineage evidence. No
intermediate tree may leave a `$ref`, exact schema-ID check, or fixture pointed
at an absent resource.

## Non-decisions

This decision does not:

- issue or accept `odeya-jcs-0.1`;
- compute a WorkIntent canonical digest;
- replace or admit `work-intent:0.1.0`;
- claim that synthetic architecture fixture digests identify admitted records;
- complete profile-bound nested references;
- migrate WorkLease, WorkContract, lifecycle, cognitive, or fixture consumers;
- construct the thirteen-event verification assignment cohort;
- resolve the claimed-reservation release contradiction;
- prove complete predecessor retention, independent reproduction, or
  accountable review; or
- authorize assignment, lease, dispatch, deployment, runtime, data exposure,
  spending, publication, or any external effect.

## Consequences

WorkIntent identity now has a finite, testable construction target. Core
self-reference, timestamp or collection drift, raw-byte substitution, profile
or admission fabrication, consumer omission, mutable aliases, reissue-order
drift, and authority escalation are explicit known-bad failures.

C5/PRQ-009 remains blocked. The next migration tranche must first close the
three legacy nested-reference shapes, then reissue WorkIntent and both direct
schema consumers as one exact lineage-preserving unit. Only later profile
issuance, canonical digest construction, registry admission, active-root
membership, the complete assignment cohort, replay, independent review, and
operator acceptance can make a WorkIntent assignable.
