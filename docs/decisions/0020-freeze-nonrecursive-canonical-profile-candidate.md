# ADR 0020: Freeze a nonrecursive canonical profile candidate

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-16
- Decision owners: architecture, canonical identity, security, recovery
- Gate effect: advances T0 review evidence; does not close PRQ-001, admit a
  profile, accept Gate A, or authorize runtime work

## Context

Odeya already retained two independently implemented runtime/library paths
that agree on 64 canonicalization vectors and four metamorphic relations. The
rules nevertheless existed across prose, vector manifests, schema constants,
and inconsistent consumer reference shapes. The prose domain table also still
named four `v1` domains after their declaring schemas had been reissued with
`v2` constants.

Calling the profile frozen in that state would be false. Refusing to assign any
exact candidate parameters would also leave every downstream digest, schema
member, event member, and registry identity unstable.

A profile cannot safely contain the digest that identifies its own complete
bytes. Such a self-reference has no ordinary finite construction. Bootstrap
identity and later acceptance evidence must remain outside the profile core.

## Decision

Freeze one exact architecture-time parameter core for review:

- profile ID `urn:odeya:canonicalization:odeya-jcs-0.1` and version `0.1.0`;
- strict UTF-8 parser refusals and exact structural limits;
- RFC 8785 serialization rules;
- the closed `profile_id`, `schema_id`, `subject` canonical envelope;
- SHA-256 framing and lowercase lexical output;
- the prospective four-field profile reference shape;
- fixed UTC microsecond timestamps and typed scientific decimals;
- explicit sequence/set behavior;
- the 21 domain constants currently declared by exact schema resources; and
- eight independent semantic/schema/member version axes with no implicit
  equality, conversion, or upcast.

The profile core contains no self-digest. A separate candidate-evidence record
binds the core and core-schema raw bytes, nine retained conformance artifacts,
the extracted domain inventory, and the current migration audit. The binding
uses explicit raw-byte SHA-256 identities and never relabels them as canonical
object digests.

The future consumer reference shape is exactly:

```text
profile_id
profile_version
profile_core_schema_id
profile_core_raw_digest
```

Admission remains a separate `same_active_root_exact_member` obligation.
Legacy `name`, `object_id`, bare identifier, mutable alias, and implicit
`latest` shapes are not prospective substitutes.

## Non-decisions

This decision does not:

- issue a canonical profile or canonical digest;
- migrate existing consumer schemas or fixtures;
- resolve the six current canonical migration findings;
- prove organizational independence or independent-host reproduction;
- create a profile registry member, EngineContractRoot, checkpoint, or
  activation;
- accept Gate A or authorize runtime, deployment, publication, spending, data
  exposure, or any other external effect; or
- constitute Daniel's exact-byte accept/reject/amend decision.

## Consequences

Downstream T0 work now has one exact prospective parameter set and one
machine-recomputed raw-byte evidence boundary. Digest-domain prose drift,
missing/duplicate domains, domain-to-schema substitution, parser ambiguity,
unsafe integer expansion, serializer substitution, profile-reference drift,
version-axis collapse, fabricated acceptance, and authority escalation become
known-bad test failures.

PRQ-001 remains open because the current schema/fixture corpus is not migrated.
PRQ-010 advances to a machine-bound candidate axis contract but remains open
until every member and consumer declares legal cross-axis mappings and all
implicit conversions fail in the complete corpus.

Changing any frozen candidate parameter requires a new profile version or a
formally reviewed amendment before issuance. It may not be changed silently
under the same accepted profile identity.
