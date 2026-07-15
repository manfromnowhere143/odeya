# Technology Decisions and Reversibility

Status: proposed selection discipline, 2026-07-15. No product or version in this document is authorized for implementation. Odeya freezes scientific semantics first, then selects replaceable products against retained conformance evidence.

## Decision classes

| Class | Meaning | Examples |
|---|---|---|
| Constitutional | Changing it changes scientific, authority, or safety meaning and requires a superseding ADR | Orthogonal state, protocol freeze, claim eligibility, one-writer rule, authority separation |
| Architectural | Major boundary with meaningful migration cost; accepted only through Gate A | Modular monolith, canonical transaction owner, scheduler below the kernel, private-engine boundary |
| Product candidate | A plausible implementation behind an accepted port; remains replaceable and unproven | PostgreSQL, Temporal, S3 API, OPA/Cedar, gVisor/Kata/Firecracker |
| Deployment profile | Environment-specific configuration and exact version | Region, HA topology, isolation tier, RPO/RTO, key service, retention |
| Deferred | Deliberately absent until a measured need exists | Kubernetes, graph database, streaming lakehouse, WebGPU, many microservices |

An architecture document may recommend a candidate without accepting it. “State of the art” is never a selection criterion by itself.

## Selection law

For each product category:

1. Apply hard admissibility gates: semantic compatibility, security, data rights/residency, failure behavior, observability, export, and operational competence.
2. Test the accepted Odeya contract using positive, negative, crash, restore, compatibility, and migration vectors.
3. Compare surviving candidates on a visible vector: correctness evidence, operability, ecosystem maturity, performance, latency, cost, staffing, lock-in, and exit cost.
4. Select a Pareto candidate under a recorded decision rule. Do not hide tradeoffs in one weighted score unless the weights are themselves accepted.
5. Pin exact version/configuration only for the authorized increment. Record upgrade triggers and backward-reading policy.

A benchmark win cannot override a failed scientific, authority, recovery, or containment invariant.

## Candidate matrix

| Concern | Leading candidate | Why it fits | Acceptance evidence still required | Exit boundary |
|---|---|---|---|---|
| Canonical transaction/ledger | PostgreSQL | One local transaction can bind events, command receipts, grants, budgets, aggregate heads, and outbox | Isolation/lock-order model; append throughput; backup/restore; corruption drill; witness/checkpoint profile | SQL repository and event-byte export; no database-specific meaning in domain kernel |
| Durable scheduling | Temporal-class workflow engine | Durable timers, activity retries, heartbeat, cancellation, and replay without owning scientific state | Duplicate start/callback, history loss, long outage, versioning, cancellation, and rebuild probes | `WorkflowPort`; stable workflow IDs; canonical next actions remain in Odeya ledger |
| Artifact bytes | S3-compatible content-addressed store | Immutable digest keys, multipart objects, retention, replication, and broad provider support | Conditional-create semantics, checksum behavior, object-lock profile, missing/corrupt/orphan recovery, large-object cost | `ArtifactStore`; exact bytes and manifests exportable by digest |
| Source authoring | Git | Reviewable source/protocol history and ecosystem compatibility | Signed-source policy, submodule/LFS rules, archival mirror, exact worktree/environment identity | Commit/bundle export; accepted protocol remains a ledger-sealed artifact |
| Scientific runtime | Python candidate | Best scientific/statistical ecosystem and model/tool integration | Exact runtime/ABI; typing profile; deterministic serialization; numerical library/version policy; sandbox image | Domain schemas and language-neutral fixtures; workers replaceable per method |
| High-assurance/performance component | Rust only if measured | Memory safety and predictable binaries may fit canonicalization, gateways, or validators | Demonstrated need, cross-language conformance, operational ownership, FFI boundary | Narrow executable/port; never a second claim ontology |
| Cockpit | Daniel-owned product surface; TypeScript/web candidate | Typed projection client and mature accessibility/testing ecosystem | Accepted UI data contract, browser matrix, CSP/supply-chain profile, accessibility fixtures | Read-only `ProjectionPort`; no scientific or publication authority in client |
| Scientific tables | Arrow/Parquet with DuckDB candidate | Portable columnar artifacts and reproducible local analysis | Strict writer profile; decimal/time/null vectors; cross-version reads; logical/byte identity rules | Standardized artifact package plus CSV/other bounded export when lawful |
| Policy evaluation | OPA/Rego or Cedar adapter | Versionable, inspectable policy decisions behind a narrow interface | Expressiveness for grants/quorum/delegation; deterministic replay; bundle signing; denial behavior; admin usability | `PolicyPort`; retained input/output and Odeya-owned action vocabulary |
| Workload identity | SPIFFE/SPIRE-class candidate | Short-lived workload identity and service attestation | Bootstrap, rotation, revocation, federation, compromised-node behavior | Standard identity claims normalized into Odeya principal/execution identity |
| Secrets/keys | Cloud KMS/HSM + broker, Vault-class where needed | Keeps reusable secrets outside workers and supports rotation/audit | Key hierarchy, quorum, recovery, latency/outage, signing policy, region | `CredentialBroker`/signing ports; key references never become scientific identity |
| Trusted fixture isolation | Rootless/hardened container candidate | Low operational cost for reviewed deterministic fixtures | Exact kernel/runtime negative tests; no host socket/metadata/ambient credential | OCI image and command manifest |
| Untrusted generated-code isolation | gVisor, Kata, or microVM candidate | Stronger boundary for hostile model/contributor workloads | Escape/lateral-movement tests, image boot/IO profile, patch cadence, residual side channels | `SandboxPort`; tier selected per workload, not globally |
| Observability | OpenTelemetry | Vendor-neutral traces/metrics/log correlation | Exact stable Odeya attributes, redaction, sampling, cost, GenAI snapshot | OTLP/export adapters; ledger/evidence never depend on telemetry |
| Evidence graph | PostgreSQL relational edges initially | One transaction boundary and sufficient recursive/query semantics for the first slice | Query workload, dependency-invalidation latency, graph export, projection rebuild | Graph is a projection/export; migrate only after measured failure |
| Search/retrieval | Rebuildable lexical/vector indexes | Useful context construction without authority | Recall/contradiction-coverage eval, poisoning resistance, deletion/tenant isolation, replayable retrieval manifest | Delete and rebuild from canonical artifacts/edges |
| Models/providers | Evaluated provider-neutral configurations | Capability changes quickly and differs by role, data class, budget, and independence | Role-specific matched-budget surface, retention/residency, reliability, correlation, fallback semantics | `ModelPort`; exact provider/model/harness is retained per attempt |

## Explicit non-selections

- **No graph database initially:** graph semantics are required; a graph product is not. Add one only if measured relational queries or invalidation fail their SLO.
- **No microservice decomposition initially:** service count does not create correctness. Split only for an accepted isolation, scaling, ownership, or deployment reason.
- **No Kubernetes requirement initially:** adopt only when deployment topology, workload volume, or security controls justify its operational cost.
- **No custom cryptography or numerical statistics:** use reviewed libraries and standards under pinned profiles; Odeya owns contracts and verification.
- **No universal vector-database memory:** retrieval indexes are disposable projections and cannot promote assertions.
- **No foundation-model training on the critical path:** the initial research advantage is the scientific control/evidence architecture. Fine-tuning or training requires a separate value, rights, contamination, and safety case.
- **No automatic provider fallback in confirmatory work:** a fallback is a new attempt/configuration and can change comparability.

## Product-choice probes

The following questions cannot be settled honestly by prose and therefore remain Gate B candidates after Gate A semantics are accepted:

| Probe | Falsifiable question | Decision affected |
|---|---|---|
| Cross-store crash recovery | At every crash boundary, do bytes/ledger state converge without false promotion or loss? | Database/object-store profile |
| Scheduler loss and replay | Can scheduler state be rebuilt without changing mission phase, budget, claim, or external-effect truth? | Temporal-class choice and workflow port |
| Canonical JSON across languages | Do pinned implementations produce identical bytes/digests for every edge vector and reject every forbidden form? | Runtime languages and digest profile |
| Grant race model | Does use/reserve/revoke/quorum ordering prevent unauthorized or double use under bounded concurrency? | Transaction isolation and authority store |
| Isolation tier | Do representative hostile workloads fail every escape, metadata, secret, egress, persistence, and cross-mission test? | gVisor/Kata/microVM selection |
| Publication ambiguity | Does a timeout at every channel boundary yield a safe, independently reconcilable state with no blind duplicate? | Release adapter eligibility |
| Projection accessibility | Can all required scientific states be represented at the accepted browser/accessibility matrix without client authority? | Cockpit stack and projection contract |

Each probe is disposable, offline, bounded, and retained only as decision evidence. It cannot quietly become production code.

## Migration obligations

Every accepted product decision must include:

- canonical export format and completeness proof;
- dual-read or offline migration plan where semantics could drift;
- rollback point and maximum irreversible window;
- compatibility matrix for event/schema/artifact readers;
- secret/key and identity migration without rewriting provenance;
- cost and staffing assumptions with expiry date;
- trigger that forces reconsideration;
- evidence that the replacement preserves every constitutional invariant.

A vendor replacement may change latency, cost, throughput, or operational procedure. If it changes what a mission, grant, artifact, verification, claim, correction, or publication means, it is an architecture change rather than an adapter swap.
