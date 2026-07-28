# ADR 0100: Introduce an unissued scoped product-identity profile successor

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-28
- Decision owners: canonical identity, contracts, registries, replay, security
- Gate effect: advances PRQ-002B candidate identity construction only; does
  not issue a profile, admit a schema or member, construct a registry
  snapshot or root, close PRQ-002, accept Gate A, or authorize runtime work

## Context

The retained `odeya-jcs-0.1` profile candidate is broad, unissued, and bound to
exact core and schema bytes. At published baseline
`5332239f84ff278815c25d888f115bce22919e34`, 106 of the 120 product-schema
resources contain at least one exact `odeya-jcs-0.1` profile-ID literal. Fourteen
do not. Adding standalone product member records and pure registry identities
cannot silently rewrite those consumers, reinterpret their digests, or reuse a
domain that names a different declaring schema.

ADR 0099 answered a narrower topology question with architecture-only probe
material. That material remains non-issuable and outside the product-schema
corpus. Its schemas, objects, domains, digests, and results cannot be promoted
into a product identity. PRQ-002 therefore needs newly identified product
resources, a side-by-side profile successor, and an explicit migration record.

The profile core also has a nonrecursive bootstrap requirement. A profile
reference names the exact raw digest of the core, so the core cannot contain
that digest itself. The core schema and every declaring product schema must be
frozen first; an external evidence record then binds their exact raw bytes and
the resulting core bytes.

## Decision

### A scoped, side-by-side profile

Add the unissued candidate profile
`urn:odeya:canonicalization:odeya-jcs-0.2`, version `0.2.0`. Its scope is only
the PRQ-002B product member, commitment, and registry resources introduced by
this decision. It is not an alias for `odeya-jcs-0.1`, a global replacement,
or an implicit upcast path.

The profile core is
[`architecture/canonicalization-profile-core-0.2-candidate.json`](../../architecture/canonicalization-profile-core-0.2-candidate.json).
It is validated by
`urn:odeya:schema:canonicalization-profile-core:0.6.0`, contains no digest of
itself, and describes the four-field profile reference:

```text
profile_id
profile_version
profile_core_schema_id
profile_core_raw_digest
```

The raw core digest is supplied only by
[`architecture/canonicalization-profile-0.2-candidate-evidence.json`](../../architecture/canonicalization-profile-0.2-candidate-evidence.json)
after the twelve successor schema resources and the core bytes are final.

The profile has exactly nine product domains:

```text
odeya-schema-resource-record-v1
odeya-aggregate-state-subject-record-v1
odeya-reducer-contract-record-v1
odeya-event-contract-record-v1
odeya-ordered-member-map-commitment-v1
odeya-schema-registry-v2
odeya-aggregate-state-subject-registry-v2
odeya-reducer-registry-v2
odeya-event-contract-registry-v2
```

The twelve successor schema resources are four standalone member schemas, one
ordered-member-map commitment schema, four side-by-side registry successors,
and three profile core/evidence/migration schemas. Every resource has a new,
versioned schema ID. Existing schema IDs and files remain unchanged.

### Freeze framing before identity

The scoped digest framing is frozen before any product digest may be computed.
A candidate must first strictly parse and validate the complete subject against
the exact schema ID and raw schema digest. The schema fixes the exact included
and excluded JSON Pointers. The evaluator constructs the closed input:

```json
{
  "digest_contract": {},
  "resolved_subject_schema": {
    "schema_id": "...",
    "schema_digest": "sha256:..."
  },
  "projection": {}
}
```

It then applies RFC 8785 and SHA-256. The digest contract itself is in the
projection. The resulting digest is not. Exclusions are limited to the
schema-fixed result digest and external trace, review, or conformance evidence
members. Missing, duplicate, overlapping, or non-schema-fixed pointers refuse
identity.

The exact order is:

1. freeze all twelve successor schema resources;
2. bind their exact raw digests and byte counts;
3. validate and freeze the non-self-hashing profile core;
4. bind the exact raw core digest externally;
5. run source-separated conformance and known-bad checks;
6. obtain accountable review and the operator's exact-byte decision; and
7. only under a later, separate authorization compute any product identity.

This decision creates no product member, commitment instance, registry
snapshot, root, or activation.

### Retain structural vectors without constructing identity

The repository-wide schema contract requires one structurally accepted
baseline and at least one attributed refusal for every `schemas/*.schema.json`
resource. For the nine product member, commitment, and registry schemas, the
accepted baselines are exactly the files matching:

```text
tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-*.structural-nonidentity.json
```

There are exactly nine. Their closed path-to-schema mapping is retained in
`tests/product-identity-profile-candidate/cases.json`. The files deliberately
use the suffix `.structural-nonidentity.json`, never `.valid.json`, and remain
outside the product-identity suite's local JSON inventory.

These are JSON Schema validation vectors, not product identity instances.
Every digest-shaped value belongs to one explicit reserved eighteen-value
sentinel set. Every profile reference uses the reserved core sentinel rather
than the exact raw digest of the current successor core, and every apparent
member, commitment, or registry result is a reserved sentinel rather than a
recomputed result. The dedicated checker validates all nine through a
network-disabled preloaded registry, dynamically refuses any sentinel equal to
the raw SHA-256 of a current schema or architecture artifact, and refuses any
vector path or sentinel bound by the twelve successor schemas or three
candidate records.

No checker canonicalizes these vectors or interprets, inherits, compares, or
recomputes their apparent result digests as identity. They add zero product
members, commitments, registry snapshots, migrations, roots, or activations.
Shared architecture-schema manifest integration may use them only as
structurally accepted baselines paired with attributed known-bad mutations;
that coverage classification cannot promote them into product identity.

### Replace one never-issued reservation prospectively

The `odeya-jcs-0.1` core reserved
`odeya-ordered-digest-list-commitment-v1` prospectively but never issued it and
never had a declaring schema constant. Retain that reservation as
superseded-but-never-issued. The new
`odeya-ordered-member-map-commitment-v1` domain is a distinct identity, not an
alias or a digest-equivalent rename. No predecessor instance or digest is
migrated.

### Preserve the predecessor and make the census explicit

The migration candidate is
[`architecture/canonicalization-profile-0.1-to-0.2-migration-candidate.json`](../../architecture/canonicalization-profile-0.1-to-0.2-migration-candidate.json).
It binds the exact predecessor core, evidence, and schema bytes; enumerates all
twelve successor resources; and freezes this scoped partition:

```text
106 retained direct odeya-jcs-0.1 consumers
 14 retained schemas that are not direct consumers
 12 new successor schema resources
---
132 candidate product-schema resources
```

The 106 direct consumers remain on `odeya-jcs-0.1`. They are neither rewritten
nor reinterpreted. A digest under one profile cannot be relabelled, inherited,
or compared as the same identity under the other. Any future instance
migration must resolve and validate the exact predecessor, apply one explicit
versioned transformation, validate the successor, recompute under the
successor profile/domain/schema, and retain bidirectional lineage.

The predecessor profile was never issued. Accordingly, this tranche migrates
zero issued predecessor instances and claims no such instances exist in its
migration input. It also migrates zero probe or product instances. The twelve
rows are candidate schema-resource dispositions, not instance migrations.

### Keep offline resolution incompleteness blocking

Current exact predecessor resources resolve from the repository, but the
schema-resource reissue ledger retains older predecessors only through
reachable Git objects. No complete offline schema registry or verified
external content-addressed archive exists. Git reachability is not durable
retention evidence, and the number of unresolved historical resources is
unknown rather than zero.

The migration therefore remains incomplete. This record cannot support
profile issuance, schema admission, historical replay completeness, root
construction, activation, or Gate A acceptance until the offline resolver
boundary is closed and independently checked.

## Non-decisions

This decision does not:

- issue or accept either canonicalization profile;
- mutate, redirect, admit, or retire a retained schema resource;
- promote any architecture-only probe identifier or evidence;
- construct a schema, state, reducer, or event member;
- construct a commitment, registry snapshot, membership proof, checkpoint,
  `EngineContractRoot`, constitutional admission, or activation;
- claim conformance, independent reproduction, accountable review, or operator
  acceptance;
- complete the 106-consumer migration;
- close PRQ-002 or any other Gate A prerequisite; or
- authorize runtime, deployment, scientific publication, spending, data
  access, or any new external effect.

## Consequences

PRQ-002B now has an explicit candidate identity boundary without contaminating
the retained profile or the architecture-only probe. The domain and member-key
rules are fixed before product digest construction, and the predecessor
consumer blast radius is measured rather than hidden.

The retained architecture slice mechanically finalizes the twelve schema bytes,
binds the exact core externally, and enrolls the nine structural-nonidentity
baselines with attributed known-bad mutations. The next evidence work is to
prove the remaining schema and migration guards, complete source-separated
recomputation, close the offline resolver, and obtain accountable review plus
Daniel's exact-byte decision. Until then every issuance, admission, root,
activation, runtime, scientific-publication, and Gate A claim remains false or
null.

The retained contract also treats parsed JSON type as part of candidate
exactness. An integral float cannot substitute for an integer byte or count
field, and `0` or `1` cannot substitute for a Boolean authority or nonclaim
field. The isolated product suite passes one safe control and nineteen
single-fault known-bads; the Gate cross-check rejects twenty-one mutations,
comprising sixteen exact-inventory or JSON-type attacks and five schema-valid
semantic downgrades. These bounded refusals do not establish profile
correctness, issuance, or Gate A acceptance.
