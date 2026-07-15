# Data Governance, Rights, and Lifecycle Contract

Status: proposed constitutional contract, 2026-07-15. This document defines deployment-neutral data invariants. It is not legal advice, does not select a jurisdiction, and does not authorize collection, model exposure, training, or release. A jurisdiction- and mission-specific policy profile must narrow it before data enters Odeya.

## Governing rule

Data possession is not data authority. A source being public, technically reachable, purchased, contributed, or accepted by a provider does not prove that Odeya may acquire it, process it for this purpose, expose it to a model, retain it, use it for training, or disclose it.

Every admitted data object therefore has a retained `DataUseDecision` over an exact byte or collection identity. The decision is made by data-rights authority and is independent of scientific usefulness, safety approval, resource approval, and publication approval.

If rights, identity, purpose, recipients, residency, retention, or required deletion behavior are unknown, the relevant use is denied. `unknown` never inherits the least restrictive value.

## Separate dimensions

No single sensitivity label controls the lifecycle. The canonical data record keeps these dimensions distinct:

| Dimension | Question answered |
|---|---|
| Byte identity | Which exact bytes or canonical collection are governed? |
| Source and custody | Where did they come from and through which transformations and holders? |
| Rights basis | What recorded permission, license, contract, consent, or other accepted basis permits a use? |
| Purpose | Which bounded research or operational purpose is allowed? |
| Scientific role | Input, calibration, training, validation, sealed truth, evidence, audit, or publication? |
| Sensitivity | What harm can access or disclosure create? |
| Subject class | Personal, confidential, security-sensitive, export-controlled, partner, employee, public, or other? |
| Recipients | Which humans, services, models, providers, regions, and audiences may receive it? |
| Operations | Acquire, inspect, transform, link, infer, execute on, train, evaluate, export, or publish? |
| Residency and transfer | Where may primary, replica, cache, log, backup, and support-access copies exist? |
| Retention | How long must or may each representation remain, and from which trigger? |
| Deletion and hold | What must be erased, what is held, and which minimal audit fact may lawfully remain? |
| Reuse | May a later mission or improvement process use it, under which new decision? |

These dimensions form an allowlist. A permissive value in one dimension never widens another.

## Data classes

The founding classes are consequences, not guesses about law:

| Class | Typical contents | Default consequence |
|---|---|---|
| D0 public-cleared | Public material with verified terms for the intended operation | Approved recipients only; provenance, license, purpose, and publication scope still required |
| D1 internal | Mission plans, unpublished work, ordinary internal telemetry | Private processing; provider training disabled; no public disclosure by default |
| D2 restricted | Licensed or partner data, private source code, contributor identity | Purpose-, provider-, region-, and recipient-specific grant; narrow derived-output review |
| D3 sensitive | Personal, safety/security relevant, sealed evaluation truth, high-value confidential data | Minimal recipients, strong isolation, independent disclosure review, explicit deletion/hold plan |
| D4 prohibited | Missing basis, forbidden terms, unsafe category, incompatible residency, or ungovernable deletion | No acquisition, processing, model exposure, training, or publication |

The maximum class of a compound object is not automatically sufficient policy. A dataset containing two rights regimes is either partitioned with exact membership or governed by the intersection of their restrictions.

## Canonical lifecycle objects

The architecture requires these immutable objects or facts:

### `DataAssetRecord`

Identifies exact bytes or a canonical collection manifest; source; acquisition activity; original and transformed identities; custody; scientific role; inferred-data status; and current lifecycle projection.

### `RightsAssertion`

Records a source-provided license, contract term, consent receipt, policy assertion, or public-domain claim as evidence. An assertion is not permission until evaluated.

### `DataUseDecision`

A human or qualified deterministic decision by data-rights authority that binds:

- exact asset or collection digest and schema/profile;
- allowed purpose and mission/stage;
- allowed operations and scientific roles;
- allowed recipient principals, principal classes, providers, model identities, and geographic zones;
- training, fine-tuning, embedding, caching, logging, human review, support access, and onward-transfer posture;
- retention trigger, period, deletion method class, backup treatment, and legal-hold precedence;
- disclosure/redaction constraints;
- decision evidence, policy and jurisdiction profile, effective interval, review date, and revocation route.

Silence means deny. Broad terms such as `research`, `AI use`, `internal`, or `anonymized` are not executable scopes unless the accepted policy profile defines their exact consequences.

### `ExposureIntent` and `ExposureObservation`

An intent authorizes a specific recipient to receive an exact data projection for one purpose. The observation records what was actually disclosed, when, through which adapter/provider, under which retention/training settings, and whether the outcome is confirmed or ambiguous. Exposure history is monotonic; deletion does not erase the fact that exposure occurred.

### `TransformationRecord`

Binds input identities, code/rule/environment, output identities, loss or redaction behavior, and validation results. Normalization, de-identification, aggregation, feature extraction, embedding, summarization, and synthetic generation produce new governed assets. They do not inherit `D0` or unrestricted rights merely because raw values disappeared.

### `RetentionSchedule`

Defines the trigger, minimum/maximum duration, authoritative clock, representation classes, legal-hold behavior, review, and terminal action. The schedule is attached at admission, not invented when storage is full.

### `DeletionCase`

Tracks a request or scheduled expiry through scope discovery, holds, authorization, execution per storage plane, verification, exceptions, residual copies, affected scientific objects, and closure. `DeletionRequested` is not `DeletionCompleted`.

### `LegalHold`

Names lawful/contractual basis, exact scope, issuer authority, effective interval, access restrictions, review, release route, and conflict handling. A hold pauses only the covered destruction; it does not grant new processing or disclosure rights.

## Canonical command/event lifecycle

`command-envelope` 0.4.0 and `research-event` 0.6.0 now assign each founding data fact one command, aggregate owner, and reducer:

| Lifecycle | Commands | Canonical events | Owner |
|---|---|---|---|
| Asset identity/lifecycle | `data_asset.record`, `data_asset.change_lifecycle` | `data_asset.recorded`, `data_asset.lifecycle_changed` | `data_asset` |
| Rights evidence | `rights_assertion.record` | `rights_assertion.recorded` | `rights_assertion` |
| Use authority | `data_use.decide`, `data_use.revoke` | `data_use.decided`, `data_use.revoked` | `data_use_decision` |
| Exposure | `data_exposure.record_intent`, `.record_observation`, `.record_settlement` | `data_exposure.intent_recorded`, `.observation_recorded`, `.settlement_recorded` | `data_exposure` |
| Transformation | `transformation.record` | `transformation.recorded` | `transformation` |
| Retention | `retention.record_schedule` | `retention.schedule_recorded` | `retention_schedule` |
| Deletion | `deletion.open_case`, `.record_progress`, `.close_case` | `deletion.case_opened`, `.progress_recorded`, `.case_closed` | `deletion_case` |
| Hold | `legal_hold.issue`, `.release`, `.observe_expiry` | `legal_hold.issued`, `.released`, `.expired` | `legal_hold` |

The event payloads are closed and the data/recovery trace set retains the founding known-bad cases. Ten high-consequence command-payload candidates close the exact shapes for data-use decision/revocation, exposure intent, deletion closure, and hold issue/release (plus four recovery commands). They are not yet immutable registry records, and the generic command envelope does not validate those payload bytes by itself.

An exposure intent records a proposed governed projection and a separate external-effect identity. It has `recording_intent_does_not_dispatch=true`; actual byte crossing still requires the external-effect authorization/reservation/dispatch protocol and an admitted observation. A completed deletion command requires verified plane results, no residual set, tombstone facts, and scientific consequence facts. These are structural preconditions; they do not prove a provider deleted bytes or that a legal conclusion is correct.

## Admission algorithm

Before acquisition or first processing, the deterministic policy path must establish:

1. exact source identity and intended acquisition method;
2. a supported rights assertion and jurisdiction/contract profile;
3. exact purpose, operations, scientific role, recipients, provider behavior, and residency;
4. sensitivity/subject classification and whether linking or inference can raise it;
5. retention, deletion, backup, incident, and withdrawal behavior;
6. separation from holdouts, verifier truth, and other missions;
7. data-rights decision plus any required safety, resource, and execution grants; and
8. an exposure/materialization intent before bytes cross the governed boundary.

The admitted projection must be the minimum necessary. A convenient whole repository, account, mailbox, bucket, or database is not admissible when the protocol needs a bounded subset.

Discovery may inspect only metadata authorized for discovery. It cannot ingest full contents first and ask for permission afterward.

## Purpose limitation and reuse

Purpose is a typed, versioned scope linked to a mission/protocol, not free text. Later use requires a new decision over the exact asset and proposed recipients/operations. The following are separate purposes:

- completing the originating research protocol;
- reproducing or independently verifying a result;
- debugging a failed execution;
- evaluating an engine component;
- improving prompts, routing, policies, models, or graders;
- training or fine-tuning a model;
- supporting a customer or investigating an incident;
- publishing a result or releasing a research package.

Scientific reproducibility does not override data rights. When raw data cannot be retained or disclosed, Odeya must record that limitation, publish only an authorized derived package, and narrow reproducibility/verification claims accordingly.

## Models, providers, and learning

Before any model or external provider sees governed data, the decision binds the exact provider/service class and verified configuration for:

- service-side retention and deletion;
- training or product-improvement use;
- abuse monitoring and human access;
- regional processing, subprocessors, and onward transfer;
- caching, batch storage, tool calls, connectors, and logs;
- account/tenant isolation and support access;
- output ownership and reuse restrictions;
- incident notification and evidence availability.

An API flag is an observed configuration input, not proof of provider behavior. Contract/version, request settings, provider receipt, and periodic verification are retained.

No mission data enters the improvement lab, training set, retrieval corpus, benchmark, or reusable prompt library without an explicit reuse decision. Synthetic or de-identified outputs remain governed until a recorded risk/rights decision establishes the permitted scope; a model’s assertion that content is anonymous is never sufficient.

## Derived, linked, and inferred data

Derived data receives its own identity, classification, rights decision, lineage, and retention schedule. The transformation can preserve or increase restrictions. It can decrease restrictions only under a named, reviewed rule with evidence and residual-risk bounds.

Joining two allowed datasets can create a disallowed one. Before linkage, policy evaluates:

- combined purpose and compatibility;
- membership and join-key disclosure;
- re-identification and sensitive-inference risk;
- changed residency/provider exposure;
- scientific leakage or holdout contamination; and
- whether deletion can propagate through the dependency graph.

Embeddings and indexes are derived assets, not harmless metadata. They carry source lineage and deletion fanout.

## Scientific truth, audit, and deletion

Odeya never solves the conflict between deletion and scientific integrity by pretending both bytes still exist and do not exist.

When a deletion or rights revocation affects evidence:

1. block new access, processing, and dependent grants at the canonical commit point;
2. identify raw, derived, cache, index, log, export, provider, replica, and backup copies through lineage;
3. append the rights/deletion fact and mark affected artifacts unavailable, tombstoned, or held;
4. recompute claim eligibility and invalidate, correct, withdraw, or narrow dependent claims/publications as required;
5. destroy covered bytes through the accepted storage-plane method;
6. verify destruction to the degree the selected profile can honestly establish; and
7. retain only the minimum lawful non-content tombstone needed to prevent resurrection and explain the scientific consequence.

The tombstone may retain a random identifier, digest/commitment only when policy permits, lifecycle events, decision basis, destruction evidence, dependency edges, and non-sensitive reason code. A digest of personal or proprietary content can itself be sensitive and is not automatically retained.

Backups are not exempt. The accepted profile must choose one of: selective deletion with verified rewrite; key-scoped cryptographic erasure; or expiry through a bounded, access-blocked backup lifecycle. Until every residual copy is handled, status is `deletion_in_progress` or `deletion_limited`, never `deleted`.

## Retention and storage-plane fanout

Every representation is assigned to a plane:

| Plane | Examples | Terminal behavior |
|---|---|---|
| Canonical metadata | rights decisions, lifecycle facts, dependency edges | Append correction/tombstone; retain minimum allowed audit fact |
| Primary artifact bytes | raw inputs, run outputs, evidence packages | Exact deletion/hold method under immutable-storage profile |
| Execution working set | sandbox disks, temporary downloads, memory snapshots | Short TTL, teardown verification, incident quarantine override |
| Derived retrieval | embeddings, search, summaries, feature stores | Dependency-driven purge and rebuild |
| Observability | logs, traces, errors, support captures | Redacted by construction; separate short schedule |
| Provider copies | prompts, files, batches, caches, logs | Provider deletion request/receipt plus declared residual limitation |
| Backups and replicas | database/object backups, disaster replicas | Profiled expiry, rewrite, or cryptographic erasure; inaccessible after revocation |
| Exports/publications | downloads, repositories, release channels | Cannot promise recall; issue withdrawal/correction and settle each controlled channel |

Storage TTL is enforcement evidence, not the governance decision. Clock failure, lifecycle-rule drift, replication lag, and restore resurrection are known-bad cases.

## Training and contamination boundary

Training authorization is distinct from ordinary inference, evaluation, and retrieval. It binds exact input manifest, target model/component, objective, environment, recipients, output/license posture, memorization/privacy tests, deletion feasibility, and promotion path.

Sealed truth and private holdouts are forbidden from candidate-generation, training, prompt optimization, retrieval memory, and producer-visible diagnostics unless the protocol explicitly ends the holdout and records the exposure. Exposure invalidates future independence claims for affected configurations; deletion cannot unexpose a model or human.

## Publication and export

Publication runs a fresh data-rights evaluation over the exact final manifest bytes and audience. Prior permission to process does not imply permission to disclose. The decision checks:

- source licenses and attribution;
- personal, confidential, security, export, embargo, and partner restrictions;
- whether transformed outputs leak restricted inputs;
- required redaction and its scientific consequence;
- accessible artifact metadata and download contents, not only visible prose;
- controlled-channel recall/withdrawal ability and uncontrolled replication risk.

The publication grant binds the sealed manifest digest. Any byte or metadata change requires a new candidate and rights decision.

## Incidents and subject/contributor requests

A suspected disclosure, rights mismatch, retention failure, or provider-policy change blocks affected uses and opens an incident without waiting for proof of harm. Incident access is itself purpose-limited and logged.

A request concerning access, correction, export, restriction, objection, or deletion becomes a typed case. Identity verification is proportional and does not collect excessive new data. Response deadlines and legal conclusions belong to the jurisdiction profile; Odeya records the authoritative due date and cannot silently close an overdue or indeterminate case.

## Semantic invariants

Closed structural candidates now exist for `DataAssetRecord`,
`RightsAssertion`, `DataUseDecision`, the discriminated immutable
`DataExposureRecord` intent/observation/settlement facts,
`TransformationRecord`, `RetentionSchedule`, `DeletionCase`, and `LegalHold`.
Their fixtures demonstrate fail-closed object shape only. They do not establish
that referenced bytes exist, an assertion is legally sufficient, a decision
covers an exposure, lineage is complete, a provider deleted data, or a hold or
deletion action is valid in a jurisdiction.

At minimum, independent validation must prove:

1. every exposure is covered by an active decision for the exact asset, operation, purpose, recipient, provider, region, and time;
2. transformations have complete input/output lineage and cannot silently downgrade restrictions;
3. a child decision is a strict subset unless a new authorized rights basis is recorded;
4. revoked, expired, tombstoned, deletion-pending, or held data follows its exact allowed-operation matrix;
5. training, retrieval, verification, publication, and support are never inferred from generic processing permission;
6. recipient/model/provider exposure is monotonic and affects independence/contamination even after deletion;
7. mission close cannot leave unowned data, expired decisions with active access, unresolved deletion cases, or unidentified provider copies;
8. restore cannot resurrect access or projections past the current rights/deletion ledger position;
9. an artifact missing due to deletion cannot remain claim-eligible merely because its digest or old verification remains; and
10. unknown jurisdiction, license, recipient behavior, deletion capability, or lineage fails closed.

## Adversarial fixtures

The machine-readable replay set now includes assertion-as-permission, exposure-unknown-to-zero, completed-deletion anti-resurrection, and stale-frontier recovery traces. Gate A still requires independent semantic execution of those traces and the following wider cases:

- a public URL with terms incompatible with model ingestion;
- a contributor offering data they do not control;
- a D1 prompt sent to a provider whose training setting is unknown;
- allowed inference incorrectly reused for training;
- a derived embedding omitted from deletion fanout;
- an allowed dataset joined into identifying D3 data;
- a legal hold incorrectly granting analysis access;
- a backup restore resurrecting a deleted artifact and stale grant;
- a deleted sealed answer still contaminating a producer/model;
- publication text cleared while a restricted attachment leaks;
- provider deletion returning no verifiable settlement; and
- a required evidence deletion forcing claim correction rather than silent preservation.

Each trace names the expected command rejection or event sequence, affected claims, residual limitation, and next legal action.

## Acceptance and deployment profile

This contract can enter a Gate A candidate only when:

- schemas exist for asset, assertion, decision, exposure, transformation, schedule, deletion, and hold objects;
- the command/event catalog owns every lifecycle transition (now structurally present for the founding vocabulary);
- the dependency graph and publication protocol consume the same identities;
- the first vertical slice declares exact source rights, provider posture, retention, and deletion behavior;
- jurisdiction/contract counsel or another accountable data-rights reviewer records limitations for that slice;
- known-bad traces pass the independent semantic rules; and
- the operator accepts the exact profile digest.

Implementation must then prove storage-, provider-, cache-, backup-, and restore-specific enforcement. Until that evidence exists, the architecture may say `designed for governed deletion`; it may not claim verified deletion, anonymity, legal compliance, or provider non-retention.
