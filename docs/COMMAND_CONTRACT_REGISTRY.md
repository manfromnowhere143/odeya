# Command Contract Registry

Status: proposed Gate A contract, 2026-07-15, governed by [ADR 0013](decisions/0013-admitted-only-command-ingress.md). The current envelope/receipt schemas are structurally present, but the envelope still exposes 121 command discriminators while only thirteen separate closed payload-schema candidates exist: `external_effect.authorize`, `external_effect.start`, `external_effect.cancel`, plus ten high-consequence data-governance/recovery commands. No immutable machine command registry is enrolled. The 121-discriminator file is therefore an architecture/red-team candidate that must be regenerated as an admitted-only surface; it does not claim A-002 closure or authorize handlers.

## Separation of concerns

Four different boundaries apply to a new command attempt:

1. a bounded ingress selector extracts only tenant, namespace, command ID, command type, and command version and resolves them against the server-selected active admitted registry;
2. `CommandEnvelope` validates stable transport/admission fields and binds one exact payload-schema and registry-member identity/digest;
3. the exact closed command-payload schema validates the command-specific request body; and
4. `CommandReceipt` validates the immutable result of one successfully bound admitted attempt, its exact admission-evidence bindings, and replay contract.

Generic frame, decompression, nesting, token/key, and rate limits run before selector extraction. The envelope’s generic `payload: object` is intentional only when step 3 is mandatory. A payload is inadmissible if its active registry record or exact schema bytes are unavailable. Metadata claiming a schema ID/digest is not validation.

## Admitted-only ingress and historical replay

For a command ID with an existing receipt, admission first resolves the receipt-bound historical registry, envelope, record, and payload schema. An exact request returns the same receipt even if that command is now retired. Changed bytes or binding under the same idempotency key return a non-canonical conflict response referencing the prior receipt; they cannot create a second receipt or execute.

For a new command ID, the bounded selector must resolve type/version to exactly one active admitted member before full envelope construction, payload validation, handler lookup, authority evaluation, or domain transaction. Unknown, reserved, inactive, superseded, unavailable-root, or invalid-membership selectors fail with stable ingress code `command_contract_not_admitted` where disclosure policy permits. They produce no `CommandReceipt`, domain event, grant use/reservation, resource commitment, outbox record, or fabricated schema/member reference. A future typed ingress-refusal observation is operational/security evidence, not a command settlement.

Once the selector resolves an admitted member and the envelope has all bindable required fields, payload-schema, state, reference, policy, authority, rights, resource, and semantic failures may settle as a rejected receipt bound to that exact member. `unknown_command` is not a legal `CommandReceipt` result; `schema_unresolvable` applies only when an admitted member exists and its named exact payload-schema bytes cannot be loaded after envelope binding.

Reserved design names live only in a separate non-executable vocabulary artifact. They have no active record, payload-schema reference, handler, authority/grant mode, event alternative, compatibility promise, or receipt address. Promotion is prospective: complete the contract evidence, generate a new admitted-only envelope, and activate a new sealed registry/root snapshot. Retired admitted contracts remain retained for historical replay but are absent from new-command admission.

## `CommandContractRecord`

Every admitted command type/version has one immutable record:

```text
command type + semantic version
command payload schema ID + byte digest
owning module
pure decider/handler port contract identity and runtime-conformance requirement
allowed stream families
owning aggregate type
creation versus existing-aggregate rule
expected-position policy
actor/principal classes
closed authority alternatives and non-caller-selectable invocation path
ordered assignment/grant role slots + use/exhaustion occurrence bindings
action-instance/request/target binding + use consumption point + reservation policy
risk/data/action ceiling
required immutable input/reference types
pure semantic rules and exact versions
legal source states / transition predicate
event batch alternatives and required transaction cohort
outbox/effect intents and dispatch prohibition inside transaction
idempotency scope and no-op rule
stable rejection codes and next legal actions
maximum payload/reference/complexity limits
compatibility/upcast policy
positive, negative, stale, authority, race, and replay trace IDs
owner, review, effective/expiry/supersession evidence
```

The admitted registry snapshot is canonicalized and sealed as one ordered set. It is the source set for generated envelope discriminator branches. Command admission binds the exact record and snapshot digest. `latest` resolution is forbidden. `CommandEnvelope` 0.4.0 and `CommandReceipt` 0.3.0 structurally require three distinct references: the immutable snapshot, the immutable member record, and a separate activation record/proof. Envelope authority fields are only typed `presented_authority_hints` with `trust_level=untrusted_resolve_only`; they cannot carry a caller-selected mode, derivation rule, PolicyDecision, or authorization verdict. The kernel derives the applicable authority basis from the exact contract record and current canonical state.

The separation is constitutional and non-circular:

1. snapshot and member-record canonical bytes are produced and digested without any checkpoint reference;
2. an activation record names the snapshot digest, tenant/mission scope, activation position, activation proof, and the checkpoint that seals the compatible C0 registry bundle;
3. the checkpoint commits the registry digest; the snapshot never embeds that checkpoint or activation; and
4. admission proves membership, exact duplicated metadata equality, activation scope, and `activation_position <= target/current ledger position` against the selected canonical branch.

Genesis uses a separately reviewed constitutional-bootstrap activation proof and first checkpoint procedure. The exact RegistryActivation embeds `P0.constitutional-recovery-admission`, binding the non-self-issued root, EngineContractRoot/C0, witnessed checkpoint, and clear recovery/fork/quarantine frontier. Envelope, receipt, and AdmissionEvidenceBundle carry the exact activation and P0 digests; an ordinary command cannot construct its own prerequisite. This does not solve the cycle by permitting a self-issued snapshot, a mutable alias, or a snapshot whose bytes contain its future checkpoint. Activation/P0 equality, position, branch, witness, and currentness predicates are semantic; JSON Schema only fixes their typed shape.

Request, result, and receipt identities use exact domain-separated digest contracts with explicit JSON-Pointer inclusion/exclusion sets. Each digest excludes itself and each signature is an external attestation. The current schemas constrain those shapes but do not recompute bytes, verify signatures, resolve registry membership, or prove that the profile/schema digest is the accepted one.

Every admitted CommandContractRecord also selects an exact AdmissionEvidenceProfile. That profile closes the required stage and evidence families by command/result: payload and reference validation, PolicyDecision, semantic-rule results, rights/data, authority/grant, resource/verification-capacity, risk, transition, and effect admission. A pure immutable [`AdmissionEvidenceBundle`](../schemas/admission-evidence-bundle.schema.json) indexes the exact records, controlled-time/reference frontier, and explicit `not_run_due_to_prior_failure` stages. The [`PolicyDecision`](../schemas/policy-decision.schema.json) is generated by the admission kernel over exact retained policy input/bundle/rule/engine/frontier bytes; it is a filter only, never an assignment or grant. Receipts bind the bundle and the important typed records. Mutable state snapshots and caller-supplied policy-decision IDs are forbidden.

The CommandReceipt boundary starts after exact member resolution. Unknown/unadmitted commands, malformed ingress, invalid membership, and changed-digest ID reuse are pre-receipt refusals because no truthful new member-bound receipt can exist. A `schema_unresolvable` receipt requires a resolved member and exact schema identity/digest whose bytes were unavailable; `schema_invalid` requires those bytes to have resolved and rejected the payload.

Allowed event alternatives must resolve through the separate [Reducer Registry](REDUCER_REGISTRY.md). A command record cannot invent a reducer or treat an event schema as proof that its state consequence is correct.

## Payload schema laws

Every command-payload schema:

- uses JSON Schema 2020-12, an Odeya-owned schema identity, an exact logical command-payload URN bound by the envelope/registry, a semantic version, and a closed root object;
- contains only the requested decision inputs, never caller-supplied recorded time, event ID/position/digest, grant-use fact, settlement, or derived scientific verdict;
- uses exact typed immutable references rather than mutable URLs, branches, filenames, or display IDs;
- distinguishes an object being proposed/observed from a decision to admit it;
- separates requested target state from evidence claimed to justify it;
- carries explicit missing/unknown states where allowed; absence cannot mean approval or zero;
- follows the accepted timestamp, decimal/quantity, unit, identifier, and canonicalization profile;
- cannot choose its event type, reducer, authority role, policy version, or consumption point;
- has bounded strings, arrays, references, and extension behavior; and
- has a valid fixture plus mutations that target the command’s actual invariant.

Payload structure cannot prove reference existence, current position, authority, grant freshness, state legality, scientific meaning, or event consequence. The registry names the pure rules that do.

## Decision and event derivation

The command decision is a pure total function over explicit inputs:

```text
decide(
  command contract record,
  schema-valid canonical payload,
  exact aggregate folds + declared reference snapshot,
  controlled time,
  authenticated actor,
  policy/assignment/grant/resource/data state,
  semantic rule results
) -> reject | noop | ordered event-batch proposal
```

It performs no network, model, filesystem, object-store, scheduler, clock, random, or provider call. Indeterminate required input fails closed with a stable reason.

The event-batch alternatives are closed in the registry. A handler cannot emit a convenient event absent from its record. Kernel-produced cohort facts—such as grant reservation/use, resource reservation creation/claim/release/expiry/settlement, aggregate head, receipt, and outbox—are added only by the admission transaction under named rules. There is no caller-facing generic resource-reserve, claim, release, expire, or settle command: callers submit the domain start/cancel/observation request, and the resource-accounting kernel derives the exact cohort fixed by that command record.

Authority is also a closed alternative, not one ambiguous role string. Each
command record enumerates exact invocation paths (`caller`, deterministic
internal observation, ingress, or constitutional ceremony), and the kernel
selects exactly one from trusted context; the payload cannot select it. A
bounded-grant path contains an ordered finite role-slot array. Every slot binds
a distinct action-instance/request/target grant with `max_uses=1` in the first
slice. Its accepted event alternative contains one separately identified
`authority.grant_used` occurrence and one separately identified
`authority.grant_exhausted` occurrence for every slot. Non-grant domain events
cannot carry a grant-slot binding. Rejection, noop, and exact replay add no
occurrences. Cross-array equality, slot order, event counts, and same-commit
membership remain pure semantic checks over the structurally closed record.

## Command classes

The founding registry separates:

| Class | Typical commands | Payload character |
|---|---|---|
| Submit/observe | proposal submission, exposure, attempt report, resource observation, effect observation | exact untrusted observation plus provenance; no decision fields |
| Decide/admit | proposal, validity, measurement, verification, release, promotion | subject/reference set + human/rule decision evidence; no caller-derived event facts |
| Compile/seal | mission, protocol, work graph, claim version, publication manifest, handoff | exact source object refs + pure compiler/rule identity |
| Authorize/reserve | grant, stage, external effect, strategy shadow/canary | exact requested action/target/limits + prerequisite decision refs |
| Claim/dispatch | work lease, effect start | exact active reservation/lease + target identity; commit point precedes external work |
| Correct/invalidate | claim/publication/dependency/artifact/protocol corrections | prior and replacement refs + reason/evidence + fanout rule |
| Reconcile/settle | effect, publication, resource/outcome | exact observations and oracle/rule refs; ambiguity never coerced |
| Close/rollback | mission close, strategy rollback, cancellation/revoke | exact open dependency set + closure/rollback evidence |

One payload schema may be shared only when the semantic action, authority, aggregate, transition, and consequence are genuinely identical. Similar field shape is not sufficient.

## Grant reservation and consumption

The registry resolves the formal race finding for every grant-consuming command:

- `domain_commit`: reservation and consumption occur in the same canonical transaction as the domain fact; no durable intermediate reservation exists.
- `dispatch_claim`: T1 effect intent creates an exact durable use reservation; the later dispatch-claim transaction revalidates current authority and atomically consumes that reservation with the in-flight event.

The payload cannot override this choice. The record names required reservation fields, expiry, cancellation/release consequences, and the event cohort. Revoke/expiry/cancel first blocks claim and releases/invalidates; claim/use first remains an in-flight historical fact.

The founding external-effect trio makes the resolution concrete without exposing a generic reserve command:

| Command | Exact payload candidate | Required canonical cohort |
|---|---|---|
| `external_effect.authorize` | `external-effect-authorize-command` 0.1.0 | one or more exact `authority.grant_use_reserved` facts + `resource.reservation_created` + `external_effect.authorized` + dispatch outbox |
| `external_effect.start` | `external-effect-start-command` 0.1.0 | required effect class + matching `authority.grant_used(consumption_point=dispatch_claim)` + `resource.reservation_claimed` + `external_effect.started`; provider call only after commit |
| `external_effect.cancel` | `external-effect-cancel-command` 0.1.0 | required effect class + matching `authority.grant_use_reservation_released(to=cancelled)` + pre-claim `resource.reservation_released` + `external_effect.cancelled_before_dispatch`; no grant use, resource claim, or dispatch |

Grant reservation/use/release and all resource-reservation lifecycle facts are admission-kernel consequences, not caller commands. A caller cannot mint reservation identity, claim consumption or capacity, choose a consumption point, invent usage, release after claim, or cancel an effect once `started` is canonical. Resource usage observations remain untrusted typed evidence until the kernel admits them; settlement is derived only from the exact retained observation set.

`governed_processing_dispatch` is the distinct external-effect class for model, tool, data-processing, and paid-compute calls. It cannot be aliased to `message`. Authorize and start each require exact schema-typed WorkContract, DataUseDecision, DataExposure intent, and LedgerCheckpoint references; a typed provider-configuration observation; exact source/checkpoint positions and purpose/recipient/provider/region/payload bindings; and current policy, authority, and resource input digests. Start and cancel also require the effect class so omitting the discriminator cannot bypass the governed branch. Semantic admission must prove every reference exists, each digest matches, the decision/scope/configuration/frontier is current at that commit, the checkpoint does not lie ahead of the source position, and the authorize/start/cancel classes and bindings agree. JSON Schema establishes none of those cross-record or temporal facts.

## Initial closure scope and priority

A-002 may close only for one explicitly named, dependency-closed Gate A admitted set. [The resolved first-slice candidate](FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md) now names the exact representational dependency set: 43 required commands, 60 event types, 25 aggregate/reducer families, 11 owner modules, and one separately admitted P0 prerequisite. Those counts are not registry admission: 42 payload contracts, all 43 command members, all 60 event members, all 25 state/reducer members, and the real root/checkpoint/P0/activation chain remain missing. Every required command needs complete record and exact payload bytes, while all 78 outside commands remain non-executable design vocabulary. Expanding the set requires a new prospective registry/root activation.

Payload schema work proceeds by constitutional consequence, not UI order:

1. root assignment, ordinary assignment, grant issue/reserve/use/release/revoke, policy/root changes;
2. protocol freeze/exposure/amend/fork and data rights/exposure/deletion;
3. artifact promotion/custody, run validity, measurement, verification, adjudication, claim correction;
4. publication candidate/decision/seal/grant/effect/reconciliation/settlement/withdrawal;
5. ledger checkpoint/recovery/incident and mission closure;
6. first-slice mission/work/metric/falsifier/handoff commands;
7. remaining learning/strategy and ordinary lifecycle design names, promoted only when their evidence is complete.

This ordering makes unsafe transitions unrepresentable before convenience commands. A future claim that the global 121-name vocabulary is frozen would still require complete records for every name; Gate A does not gain that claim by scoping A-002 honestly.

## Machine validation

The architecture validator must eventually prove:

- each command discriminator maps to exactly one record and exact payload-schema bytes;
- no registry record exists without an envelope discriminator, owner, reducer/event alternative, fixture, and semantic rule set;
- at runtime activation, enabled envelope discriminator, enabled registry member, and conforming handler-map sets are exactly equal;
- no reserved design-vocabulary entry appears in any of those three active sets;
- every emitted event names that command as an allowed producer;
- all command/event/aggregate/schema IDs are unique and version-consistent;
- cross-aggregate transaction cohorts use the global lock order;
- payload schemas are closed/meta-valid and referenced offline by digest;
- every grant-consuming action declares one legal consumption point;
- event and command compatibility changes cannot drift independently; and
- registry regeneration is byte-reproducible from one reviewed source manifest.

Generated envelope discriminator branches and documentation are derived from the contract-admitted registry and checked into the candidate with generator/tool identity and byte-reproducibility evidence. Contract admission freezes semantics and a prospective handler port; it does not prove runtime code exists. A later runtime activation additionally requires exact handler-conformance evidence and enabled-set equality. Registry record subjects never embed their parent snapshot/activation digest; external membership wrappers and one acyclic engine-contract root bind the compatible artifacts. Hand-maintaining thousands of duplicate conditional lines as independent sources of truth is forbidden.

## Adversarial fixtures

At minimum:

- unknown and reserved selectors stop before envelope/payload/handler processing and create no receipt or canonical cohort;
- a fake reserved member with null/missing schema or handler cannot activate;
- caller-supplied snapshot selection cannot bypass the server-selected active root;
- an exact retry of a retired command returns the historical receipt under historical semantics;
- changed bytes under a settled command ID create no second receipt and no execution;
- known command with missing/wrong payload schema bytes;
- correct payload shape under another command schema;
- same command ID with one payload byte changed;
- caller-supplied event ID, recorded time, grant-use, or scientific verdict;
- state-legal payload under stale aggregate position;
- model/tool actor requesting a human-only decision;
- grant scoped to another payload/target/purpose/destination;
- dispatch-bound grant consumed at intent or dispatch without reservation;
- revoke-first reservation still dispatched;
- claim-first reservation later released as unused;
- handler emits an event absent from its registry alternatives;
- unknown semantic rule treated as pass;
- noop used to hide an evidence-relevant change;
- old reader ignores an unknown major command/event version;
- snapshot embeds the checkpoint that purports to activate it, or activation refers to a future/wrong-branch position;
- snapshot digest, activation snapshot digest, member registry digest, or duplicated command metadata disagree;
- request/receipt hash scope includes its own digest or signature, omits a registry binding, or uses the wrong domain/profile/schema binding.

Each case must fail at the intended layer and retain the expected refusal, rejection, conflict, or incident consequence without promoting one boundary's record into another.

## Acceptance boundary

A-002 remains open even though the exact representational candidate is now named. It closes only when the immutable registry snapshot, contract records, selector/refusal bytes, witnessed root/checkpoint/P0/activation chain, and every exact payload/event/state/reducer member exist; active envelope/registry/handler equality and membership/activation proofs reproduce; historical replay and changed-reuse vectors pass; the command/event/reducer graph is machine-checked; composite semantic/race traces pass; and independent review closes critical/high findings. The remaining design vocabulary stays explicitly non-executable. Envelope and receipt validation alone establishes valuable structure, not executable command meaning.
