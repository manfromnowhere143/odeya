# Evidence and Memory

Odeya's durable memory is not a transcript and not a vector database. It is a typed, append-only record of what was proposed, authorized, performed, observed, verified, corrected, and released.

## Canonical versus derived state

Canonical state:

- immutable protocol and run manifests;
- stage and authority events;
- raw and derived artifact bytes with content digests;
- exact code, data, environment, model, tool, and evaluator identities;
- metric observations and falsifier verdicts;
- claims and claim-evidence edges;
- verification, adjudication, correction, and publication records;
- actual resource and approval records;
- handoffs and externally settled outcomes.

Derived state:

- relational read models;
- full-text and vector search;
- summaries and context packs;
- visualization layouts;
- cached rankings and recommendations;
- public projections.

Derived state can be deleted and rebuilt. It never becomes more authoritative because it is easier to retrieve.

## Event ledger

Each event includes:

```text
event_id
target stream + aggregate type/id
mission scope when one exists
monotonic stream sequence
event_type and schema version
occurred_at and recorded_at
actor and execution identity
authority grant or policy decision
causation and correlation IDs
prior event digest
input artifact references
payload digest and payload encoded under the pinned Odeya RFC 8785 canonicalization profile
code/environment/model/tool identities
```

The canonicalization profile rejects duplicate keys and non-finite numbers, defines Unicode handling, uses UTC `Z` timestamps with fixed precision, and represents exact scientific decimals as typed decimal strings rather than binary JSON numbers. Hash linking and signatures make deletion or mutation detectable within their trust assumptions. They do not establish that the payload is scientifically correct. Semantic validity comes from recomputation, controlled evidence exposure, and independent verification.

A per-mission chain alone cannot detect every suffix truncation or equivocation attack. Periodic checkpoint roots must be signed and witnessed or anchored outside the primary database under a separately versioned trust policy.

## Evidence and claim graph

The graph is aligned with W3C PROV concepts:

- **Entity:** source, dataset, protocol, code, environment, artifact, observation, claim, publication;
- **Activity:** acquisition, transformation, execution, analysis, verification, review, correction, release;
- **Agent:** human, model invocation, tool, organization, instrument, execution identity.

Odeya adds scientific relations such as:

```text
supports
contradicts
tests
falsifies
derived_from
generated_by
verified_by
replicates
supersedes
corrects
invalidates
bounded_to
withheld_by
```

Every edge names the activity, scope, confidence or decision rule, and evidence responsible for it. A graph path is inspectable; a similarity score is not a proof path.

## Claim objects and orthogonal projections

Claims are immutable semantic versions. They do not embed operational, verification, replication, transport, or publication state:

```text
ClaimProposal
  -> Adjudication(determined outcome | refusal)
  -> VerificationRun references
  -> ClaimVersion(eligible | ineligible, exact scope and language)

separate branches: replication · transport · value validation
revision edges: correction · supersession · retraction notice
publication aggregate: manifest · authorization · external settlement
```

`supported_within_scope` always carries protocol, scope, evidence, uncertainty, and verifier references. Replication requires new diagnostic data or measurement under a declared independence standard, not a second run by the same producer with shared hidden context. A correction adds a version and dependency edges; it never mutates the prior object.

## Artifact storage

Artifacts are stored by digest and media type with:

- original and normalized bytes kept distinct;
- producing activity and command;
- source, capture time, rights, sensitivity, and retention policy;
- code and environment digests;
- encryption and access classification;
- validation status and promotion history;
- links to every claim and publication that depends on them.

Large scientific tables use Arrow or Parquet where suitable. RO-Crate packages export the minimum coherent research object: protocol, code, data references, workflow, results, provenance, and license metadata.

## Research memory layers

### Constitutional memory

Stable principles, authority boundaries, terminology, architecture decisions, and release policy. Changes require explicit reviewed decisions.

### Mission memory

Questions, rejected alternatives, protocols, evidence lineage, costs, outcomes, corrections, and exact current state. It is event-derived and mission-scoped.

### Handoff memory

A compact, generated recovery packet pinned to an exact ledger position. It contains facts and next legal actions, not private reasoning.

### Operational learning

Verified patterns about tools, workflows, failure modes, costs, and conditions. Observations remain distinct from promoted policy.

### Retrieval memory

Search indexes and context packs derived from the above. Retrieval records why each item was selected and its canonical source.

## Context construction

Agents receive the minimum context needed for their role:

- the frozen slice of the mission contract;
- task-specific artifacts;
- applicable policy and budget;
- explicit unknowns and forbidden claims;
- a clean output schema.

Verifier context is controlled to reduce anchoring and leakage. It receives the protocol and necessary evidence, not automatically the producer's narrative or hidden deliberation.

Long missions reset model context at checkpoints. Continuity comes from canonical state, progress artifacts, and generated handoffs—not an ever-growing conversation.

## Data exposure and sealed truth

For blinded or benchmark work, distinguish:

- model-visible inputs;
- protocol-visible metadata;
- verifier-only truth;
- publication-visible projection.

Truth release is recipient-scoped, auditable, and least-privilege. A global answer-key file or shared agent memory defeats independence even if access is described in prose.

## Corrections and invalidation

Corrections append events and edges. When a source, evaluator, split, or protocol is invalidated, dependency traversal identifies affected claims, publications, benchmarks, and strategy lessons. Their projections become visibly stale or invalid until recomputed.

## What memory excludes

- secrets or reusable credentials;
- unrestricted private chain of thought;
- undigested logs presented as conclusions;
- model confidence presented as evidence;
- inferred personal data without a lawful research basis;
- hidden edits to prior mission state.

Sensitive prompts and raw outputs needed for audit live in a separately encrypted, access-controlled retention plane with explicit policy—not in broadly retrievable research memory.
