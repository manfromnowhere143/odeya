# ADR 0023: Separate raw reference lineage from canonical identity

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-16
- Decision owners: work, canonical identity, cognitive contracts, security,
  recovery
- Gate effect: advances C5/PRQ-009 reference resolution; does not issue a
  canonical identity, admit a resource, close PRQ-009, accept Gate A, or
  authorize runtime work

## Context

WorkIntent 0.2 exposed three exact blockers instead of hiding them: its
source-view and planning-epoch reference digests were synthetic architecture
values, and its output-schema digest differed from the retained
CandidateArtifact schema bytes.

Replacing those values with SHA-256 file hashes inside fields defined as
canonical object digests would make the JSON validate while changing the
meaning of identity. That would be a category error. A raw artifact digest
answers “which bytes were retained?” A canonical object digest answers “which
closed subject, schema resource, and accepted canonicalization profile produced
this identity?” They are not interchangeable.

This separation follows the bootstrap shape already adopted for the profile:
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) defines deterministic
JSON serialization but does not supply Odeya's schema/profile/admission
semantics; [JSON Schema 2020-12 Core](https://json-schema.org/draft/2020-12/json-schema-core.html)
gives each retained schema resource an exact identifier; and both
[SLSA artifact verification](https://slsa.dev/spec/v1.2/verifying-artifacts)
and the
[OCI image manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
keep external subject descriptors and digests separate from the subject bytes
they identify. These are design comparators, not evidence that Odeya is
state-of-the-art or implementation-ready.

## Decision

Materialize one side-by-side reference-resolution cohort:

- retain WorkIntent 0.2, WorkIntentCore 0.1, and all prior schemas and
  candidates byte-for-byte;
- add exact architecture candidates for
  research-state-view.sentinel.0042 and
  planning-epoch.sentinel.0017, each validated against its exact retained
  0.1 schema;
- add WorkIntentCore 0.2, replacing only schema_version, source_view_ref,
  planning_epoch_ref, and output_contract.schema_ref;
- represent source-view and planning-epoch identity as a typed tuple of exact
  schema resource ID/raw digest, exact candidate path/raw digest, the unissued
  profile reference, a null canonical digest, and a null admission reference;
- bind the output contract directly to the exact retained
  candidate-artifact:0.1.0 schema ID, raw digest, byte count, and dialect;
- add WorkIntent 0.3 as a side-by-side wrapper around the exact WorkIntentCore
  0.2 bytes; and
- bind the predecessor, targets, successor schemas/candidates, transformation,
  proof boundary, and authority boundary in one external evidence record.

The PlanningEpoch 0.1 candidate's legacy input-view digest slot carries the
exact raw ResearchStateView candidate digest only as visible migration
lineage. The evidence contract fixes
legacy_digest_slot_is_canonical_identity=false. It is not admission and must
not be consumed as canonical identity. A future admitted PlanningEpoch must be
reissued under a profile-bound reference shape rather than reinterpret that
legacy slot.

The successor contains none of the former 111…, 222…, or 333…
placeholder values. The source-view and planning-epoch canonical digests remain
null. Forty known-bad mutations reject predecessor drift, raw binding drift,
schema substitution, target reordering, raw-hash-as-canonical relabeling,
fabricated admission, profile issuance, canonical identity, assignment
completion, Gate A acceptance, and authority escalation.

## Non-decisions

This decision does not:

- issue or accept odeya-jcs-0.1;
- claim that raw candidate bytes are canonical object identity;
- close the nested identities inside ResearchStateView or PlanningEpoch;
- admit a schema, candidate, profile, registry member, reducer, root, or
  activation;
- compute a canonical digest for either target or WorkIntent;
- rebind WorkLease 0.2 or WorkContract 0.3 to WorkIntent 0.3;
- construct the thirteen-event verification assignment transaction;
- prove reducer equality, replay, recovery, independent implementation,
  accountable review, or operator acceptance; or
- authorize assignment, lease, materialization, dispatch, runtime,
  deployment, publication, spending, data exposure, or external effects.

## Consequences

The output-schema mismatch is removed without changing the old resource.
Source-view and planning-epoch references now resolve to exact retained
candidate bytes without pretending those bytes are admitted canonical objects.
The complete offline resolver can load both predecessor and successor schema
resources at once.

C5/PRQ-009 remains blocked. Next, close or explicitly version the profile
migration findings and obtain the required accountable/operator acceptance.
Then reissue ResearchStateView and PlanningEpoch with admitted profile-bound
reference shapes, compute canonical digests from their exact closed subjects,
and create exact schema/member/root admission evidence. Only after those
identities exist may WorkIntent be reissued with canonical references and feed
the separate thirteen-event assignment cohort.
