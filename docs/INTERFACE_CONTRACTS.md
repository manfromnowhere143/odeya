# Interface Contracts

Status: language-neutral architecture. Concrete API syntax and product libraries remain subject to the pre-implementation gate.

## Dependency rule

```text
mathematics and schemas
        ↓
pure domain kernel
        ↓
application commands and ports
        ↓
adapters: storage · workflow · policy · sandbox · providers · UI
```

Dependencies point inward. The domain kernel imports no database, workflow engine, model SDK, MCP client, cloud SDK, web framework, clock, random generator, or filesystem. Those enter through explicit ports.

## Forbidden edges

- Models and tools cannot write the event store or projection database.
- Workflow callbacks cannot mutate mission state except by submitting a validated command.
- UI clients cannot derive a scientific verdict, approve an action, or mark a release complete.
- Retrieval indexes cannot create or update claims.
- Generating workers cannot choose their verifier identity or reveal sealed truth to themselves.
- Verifiers cannot repair producer artifacts in place.
- Publication cannot query arbitrary private state; it consumes an authorized sealed manifest.
- Learning cannot edit production code, prompts, policy, schemas, or memory directly.
- External adapters cannot redefine mission outcomes or claim semantics.

## Command envelope

Every state-changing request contains:

```text
command_id
command_type + command_version + exact payload-schema ID/digest
idempotency scope
target stream/type + expected stream position
target aggregate/type + expected aggregate version
mission scope when applicable
actor + execution identity
plural authority evidence: bootstrap | policy | derivation | assignments | grants | observation
correlation ID + typed causation references
exact input artifact references
closed payload validated separately under the referenced command-payload schema
canonical request digest
client-observed time (informational) + optional signature reference
```

The application boundary validates object bytes and retains a validation/materialization proof before opening the canonical transaction. Inside the transaction, the kernel validates schema, state, policy, authority, idempotency, and exact registered artifact identities or proof references without making a network or object-store call. It then appends zero or more events in one transaction. The authoritative recorded time comes from the controlled application boundary, not the worker.

## Result envelope

```text
command_id
accepted | rejected | noop
exact request + actor + target bindings
commit/event/stream-head references when accepted
typed rejection stage/code or named no-op reason
immutable result digest
exact-replay contract
```

A duplicate transport attempt returns the original retained receipt; `duplicate` is not a mutable domain result. Same-scope/same-command-ID with different canonical bytes is rejected as `command_id_reuse`. A rejection appends an event only when the attempt itself is evidence-relevant, such as suspected abuse or a consequential exposure; ordinary rejection has a receipt but no domain event.

## Core ports

Language-neutral signatures below show semantics, not implementation syntax.

### `MissionLedger`

```text
append(mission_id, expected_position, events) -> committed_position
read(mission_id, from_position) -> ordered events
verify_chain(mission_id, through_position) -> integrity verdict
subscribe(mission_id, after_position) -> at-least-once event stream
```

Append is transactional and optimistic. Subscriptions are delivery mechanisms; consumers remain idempotent.

### `ArtifactStore`

```text
stage(stream, declared_media_type, policy_context) -> staged_ref
validate(staged_ref, validator_set) -> validation report
materialize(staged_ref, expected_digest, storage_policy) -> immutable_byte_ref
open(artifact_ref, byte_range, authority) -> stream
quarantine(artifact_ref, reason, authority) -> event evidence
```

`materialize` establishes byte identity at a content-addressed key; it does not establish scientific custody. A separate kernel `PromoteArtifact` command canonically registers the byte reference, validation proof, provenance, rights, policy, and authority in the domain ledger. Staged or materialized-but-unregistered bytes cannot support a claim. Original and normalized artifacts have different identities.

### `WorkflowPort`

```text
schedule(run_manifest_ref, work_graph) -> workflow_ref
lease(work_item, capability_set, budget, ttl) -> lease
heartbeat(lease, observed_usage) -> lease state
complete(lease, attempt_manifest) -> completion proposal
cancel(workflow_ref, authority, reason) -> cancellation receipt
```

The workflow system schedules work; the Odeya kernel decides scientific stage and eligibility.

### `PolicyPort`

```text
evaluate(subject, action, resource, mission_context, policy_version) -> decision
issue(decision, constraints, expiry, replay_policy) -> authority grant
revoke(grant, authority, reason) -> revocation receipt
```

Policy input and output are retained and replayable. Missing or unavailable policy evaluation denies consequential action.

### `CapabilityGateway`

```text
invoke(lease, capability_id, version, typed_input, idempotency_key) -> untrusted result
```

The gateway owns credentials, egress, rate/spend control, input/output size, and audit. The result enters quarantine as untrusted evidence.

### `SandboxPort`

```text
start(environment_ref, mounts, capabilities, resource_limits) -> sandbox
execute(sandbox, command_manifest) -> attempt observation
export(sandbox, declared_outputs) -> staged artifacts
terminate(sandbox, reason) -> termination receipt
```

No generic `execute(string)` is exposed across the scientific boundary. Commands are versioned manifests with declared inputs and outputs.

### `ModelPort`

```text
run(model_identity, harness_identity, context_manifest, output_schema, budget) -> model attempt
```

Provider response, token accounting, safety filters, and request identity are retained. A model attempt is never directly a claim verdict.

### `VerifierPort`

```text
verify(protocol_ref, evidence_manifest, exposure_policy, verifier_identity) -> verification package
```

The verifier declares independence class, environment, evaluator versions, known-bad fixture results, discrepancies, and verdict limits.

### `ProjectionPort`

```text
rebuild(stream_position) -> projection version
query(view, filters, authority, required_position) -> projection + freshness
```

Projection reads disclose their ledger position. If the required position is unavailable, the client sees stale or unavailable—not fabricated freshness.

### `PublicationPort`

```text
compile(claim_refs, evidence_projection, disclosure_policy) -> publication candidate
decide(candidate_digest, check_results, human_authority) -> publication decision
seal(candidate, approved_decision, seal_rule) -> publication manifest
authorize(manifest_digest, human_publication_authority) -> single-use grant
intend_release(manifest, grant, channel_profile) -> external-effect intent
dispatch(intent, channel_adapter) -> untrusted effect observation
reconcile(effect, channel_observation) -> applied | not_applied | completion_unknown
settle_publication(manifest, confirmed_applied_observation) -> released
withdraw(manifest, new_publication_grant, reason) -> withdrawal effect + settlement
```

The manifest cannot contain its future grant; the grant binds the final manifest digest. Release channels never receive arbitrary repository, database, or artifact-store access. A provider receipt or timeout cannot settle publication without exact channel observation under the accepted rule.

## Typed error families

- `ContractError`: schema, invariant, or protocol violation;
- `StateConflict`: stale position or illegal transition;
- `AuthorityDenied`: missing, expired, revoked, or wrong-scope authority;
- `PolicyUnavailable`: cannot safely decide;
- `ArtifactError`: missing, corrupt, quarantined, rights-blocked, or type-invalid artifact;
- `BudgetExceeded`: named resource circuit breaker;
- `InfrastructureFailure`: worker, provider, network, storage, or workflow failure;
- `VerificationDisagreement`: producer/verifier or verifier/verifier conflict;
- `ScientificInvalidity`: protocol, data, analysis, leakage, or evaluator invalidity;
- `ReleaseDenied`: evidence, rights, safety, contributor, embargo, or wording failure.

Errors carry stable codes, retry class, evidence references, and next legal actions. User-facing prose is derived and localizable.

## Versioning

- Schemas use explicit semantic versions and stable URNs.
- Events are immutable; readers upcast through tested pure transformations while retaining original bytes.
- Breaking command changes use a new command version.
- Artifact formats declare media type and format version.
- Port implementations declare supported contract ranges.
- Model, harness, tool, evaluator, policy, and environment versions are facts, not optional telemetry.
- A migration cannot change the scientific interpretation of an existing event or claim.

## Concurrency and delivery

- One mission stream has a monotonic position.
- One mutable stage has one writer lease.
- Event delivery is at least once; consumers are idempotent.
- External effects use idempotency keys and retained provider receipts.
- Where a provider cannot guarantee idempotency, the action requires a stricter approval/reconciliation design rather than an “exactly once” claim.
- Parallel workers return candidate artifacts; promotion and stage transition are serialized.
