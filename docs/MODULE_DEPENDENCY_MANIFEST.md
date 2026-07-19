# Module Ownership and Dependency Manifest

Status: proposed logical architecture, 2026-07-15. This document proposes the semantic ownership and dependency direction intended to be frozen only after Gate A acceptance, before language/package selection. It does not authorize creation of runtime modules.

## Dependency law

```text
constitutional profiles + closed contracts
                  ↓
          pure scientific domain
                  ↓
       command application services
                  ↓
                ports
                  ↓
      replaceable infrastructure adapters

epistemic workers -> proposals/artifacts -> command boundary
projections       <- events/snapshots    <- canonical ledger
```

All arrows mean “may depend on.” A lower layer cannot be imported by a higher one. Cross-domain coordination occurs through registered commands, immutable references, and committed events—not direct mutation of another module’s records.

## Logical modules

| ID | Module | Owns | May depend directly on | Must never own |
|---|---|---|---|---|
| `constitution` | Constitutional profiles | terminology, risk/data/action classes, accepted root/profile references | nothing mutable | mission state, product SDKs, discretionary model output |
| `contracts` | Closed data contracts | schema registry, typed identifiers/references, compatibility declarations | `constitution` | semantic admission or storage |
| `canonical` | Canonical identity | parser profile, canonical bytes, typed digests, package identities | `constitution`, `contracts` | scientific equivalence, signatures as truth, object storage |
| `semantic_rules` | Pure validation registry | registered cross-object predicates, deterministic results/refusals | `constitution`, `contracts`, `canonical` | network lookup, state mutation, model judgment |
| `methods` | Scientific method registry | exact method guarantees, assumptions, applicability, numerical profiles, vectors, implementation bindings, admission records | pure foundation | silently widening a guarantee, selecting “latest,” treating a proposed method as admitted |
| `mission` | Thesis/mission lifecycle | proposal/admission facts, mission contract, lifecycle stage, blocker ownership | pure foundation + referenced domain types | protocol meaning, artifact bytes, claim outcome, publication |
| `protocol` | Prospective scientific contract | protocol snapshots/amendments/forks, exposure consequences, estimands, metrics, falsifiers | pure foundation, `mission` identifiers | execution state, result interpretation outside registered rules |
| `authority` | Assignment and grant lifecycle | root/assignments, policy-decision refs, grants, reservation/use/revoke/expiry, quorum facts | pure foundation + risk/data types | authentication provider, credentials, scientific outcome |
| `incidents` | Incident and quarantine lifecycle | incident declarations, severity/state, containment observations, scope quarantine, resolution evidence | pure foundation, authority/data/effect references | silently changing another aggregate, treating incident closure as scientific or learning success |
| `resources` | Resource accounting | estimate, authorization, reservation, observed usage, bill/refund/settlement axes | pure foundation, `authority` refs | scientific value or permission to widen work |
| `data_governance` | Data asset lifecycle | asset/rights/use/exposure/retention/deletion/hold facts | pure foundation, `authority`, source/artifact refs | scientific validity, generic legal conclusion, publication authority |
| `work` | Work graph and attempts | work items, dependencies, lease proposal state, attempts, interruption, next legal work | pure foundation, mission/protocol refs, authority/resource refs | scheduler history as truth, artifact promotion |
| `artifact` | Evidence custody | staged/materialized/promoted identity, custody, provenance, validation/quarantine/availability | pure foundation, data-governance refs | storage bytes, scientific validity, claim eligibility |
| `measurement` | Scientific observations | measurement/run manifests, validity and measurement axes, metric/falsifier results | pure foundation, protocol, artifact refs | generic claim verdict or external outcome |
| `verification` | Verification facts | assignment, run, independence vector, discrepancies, verification dispute/settlement | pure foundation, protocol/measurement/artifact refs | producer mutation, publication, outcome by consensus |
| `adjudication` | Pure scientific consequence | deterministic outcome/refusal under exact rule and inputs | pure foundation, protocol, measurement, verification, semantic rules | discretionary approval, external effect |
| `claims` | Claim lifecycle | prospective proposals, immutable eligible/ineligible versions, corrections/supersession/dependencies | pure foundation, adjudication, artifact/verification refs | publication state, generic confidence |
| `effects` | Consequential external effects | intent, dispatch claim, observation, reconciliation, applied/not-applied/unknown settlement | pure foundation, authority/resources/data refs | scientific interpretation, provider response as automatic truth |
| `publication` | Release aggregate | candidate, decision, sealed manifest, publication grant use, channel effect refs, correction/withdrawal fanout | pure foundation, claims/artifacts/authority/data/effects refs | editing claim/evidence bytes, channel 2xx as release truth |
| `recovery` | Integrity frontier and recovery cases | checkpoints, witness observations, backup state, restore verification, current-policy fence, recovery decisions, epochs | pure foundation plus immutable authority/data/resource/effect/publication/incident refs | reconstructing missing history, choosing forks by time, reopening high-consequence scopes by implication |
| `learning` | Quarantined improvement lifecycle | grounded outcomes, strategy candidates, evaluations, promotion/rollback decisions | immutable refs from other domains, evaluation contracts | direct production mutation, unsupported cross-mission generalization |
| `commands` | Application admission | command envelope/receipt, load-validate-decide-commit orchestration, expected positions | pure domains + port interfaces | domain rules embedded in controllers, external calls in transaction |
| `ports` | Infrastructure abstractions | language-neutral persistence, clock, identity, policy, artifacts, workflow, sandbox, model, effect, witness, projection interfaces | foundation contracts only | vendor behavior in domain meaning |
| `adapters` | Product integrations | exact mapping to selected database/store/provider/tool under conformance profile | `ports`, transport contracts | importing pure domain internals to bypass commands |
| `workers` | Untrusted/isolated execution | proposal and candidate-artifact generation inside work contracts | SDK/output contracts only | canonical writes, authority, terminal verdict, verifier selection |
| `verifier_workers` | Separately isolated verification execution | verification artifacts and candidate findings | verifier SDK/output contracts only | direct verification settlement or producer repair |
| `projections` | Rebuildable views | private/public/thesis read models, freshness, redaction/localization/accessibility mapping | event/snapshot contracts, authorized artifact reads | commands, adjudication, publication completion |
| `review_tooling` | Architecture/evaluation evidence | offline validators, trace replay, model checks, candidate manifests/findings | frozen architecture artifacts | runtime product behavior or production authority |

"Pure foundation" means `constitution`, `contracts`, `canonical`, `semantic_rules`, and `methods` as applicable. Depending on an identifier type does not grant access to another module’s mutable state. Method admission and validation-rule admission remain distinct registries even when one references the other.

## Aggregate ownership

The machine manifest currently enumerates exactly 47 aggregate types and assigns
one owner module to each. The prose table below is a grouped, non-exhaustive
orientation; it is not the exact 47-type machine inventory and does not by
itself establish reducer identity or correctness.

| Aggregate | Owner | Cross-aggregate references allowed | Required transaction cohort |
|---|---|---|---|
| `ThesisProposal` | `mission` | source/data review refs | proposal admission receipt and required authority/resource facts |
| `ResearchMission` | `mission` | protocol/work/blocker/claim heads | stage transition plus owning blocker/close facts only when invariant demands |
| `Protocol` | `protocol` | mission, method/rule, exposure refs | snapshot/amendment plus affected-role approvals/exposure fact |
| `AuthorityRoot` / `Assignment` / `Grant` | `authority` | principal/policy/risk/data scope | command receipt and reserve/use/revoke facts |
| `Incident` | `incidents` | affected aggregate/evidence/quarantine refs | incident transition plus explicit cross-aggregate consequence commands |
| `ResourceAccount` / `Reservation` | `resources` | grant, attempt, effect | command receipt and exact reservation/settlement cohort |
| `DataAssetLifecycle` | `data_governance` | artifact/source/recipient/dependency refs | rights decision/exposure/deletion plus affected access fence |
| `WorkItem` / `Attempt` | `work` | protocol, lease, artifact candidates | lease/attempt transition plus resource/grant reservation where needed |
| `Artifact` | `artifact` | data, provenance, validation, custody refs | promotion plus authority/resource/command/outbox cohort |
| `ScientificRun` | `measurement` | protocol/run/artifact/metric/falsifier refs | validity and measurement facts in one legal batch where causally inseparable |
| `VerificationCase` | `verification` | producer/run/artifact/evaluator/independence refs | assignment/run/dispute settlement; never producer stage mutation directly |
| `Adjudication` | `adjudication` | exact protocol/results/verifications/rule refs | deterministic output/refusal and receipt |
| `Claim` | `claims` | proposal/adjudication/evidence/dependency refs | immutable version or correction plus invalidation outbox |
| `ExternalEffect` | `effects` | exact grant/resource/data/adapter/evidence refs | intent/reservation/outbox at T1; observation/settlement at later commits |
| `Publication` | `publication` | claim/artifact/rights/decision/effect refs | candidate/decision/seal/grant/use/effect steps defined by publication protocol |
| `LedgerCheckpoint` / `LedgerEpoch` / `RecoveryControl` / `Backup` / `RestoreCase` / `RecoveryDecision` | `recovery` | exact C0–C6, witness, receipt, artifact, incident, frontier refs | each recovery fact and receipt; no restore operation mutates historical domain events |
| `StrategyCandidate` | `learning` | grounded outcomes/evaluation/configuration refs | promotion decision and rollback readiness facts |

The exact command/event catalog is authoritative when a name differs. This table is the ownership constraint it must satisfy.

Exact fold semantics, state-schema ownership, compatibility, and independent replay obligations are defined by the [Reducer Registry](REDUCER_REGISTRY.md). Aggregate ownership alone is not reducer correctness.

## Pure domain boundary

Pure domain modules may:

- accept immutable typed state and a command decision input;
- derive events, refusals, eligibility, and next legal actions;
- run bounded deterministic semantic rules;
- compare typed identities and controlled-time facts;
- expose reducer and invariant functions.

They may not:

- query a database, object store, scheduler, network, filesystem, model, system clock, random source, environment variable, or global singleton;
- deserialize unbounded/unvalidated transport bytes;
- issue authentication, policy, or storage requests;
- log sensitive content or emit telemetry directly;
- select “latest” schema/model/policy/provider;
- catch an invariant failure and continue with a default; or
- depend on UI/publication wording.

All nondeterministic observations enter as exact retained inputs through application commands.

## Application boundary

`commands` is the only runtime-shaped module allowed to coordinate a canonical state change. For one command it:

1. validates bounded bytes and exact schema/canonical identity;
2. resolves authentication, controlled time, immutable references, policy, and authority through ports;
3. loads all declared aggregate heads under the applicable declared provisional lock-order policy;
4. calls pure domain decision functions;
5. commits the complete event/receipt/authority/resource/outbox cohort once; and
6. returns the retained receipt.

It cannot call a provider, workflow engine, model, lab, object-store stream, or publication channel inside the canonical transaction. Long work is represented as intent/outbox/work; its observations re-enter through a new command.

## Partial lock-order proposal

Cross-aggregate transactions are rare and declare their full write set before
locking. The current proposal records this partial leading order:

```text
constitutional epoch
  -> authority root/assignment/grant
  -> data lifecycle
  -> resource account/reservation
  -> mission
  -> protocol
  -> work/attempt
  -> artifact
  -> scientific run/measurement
  -> verification
  -> adjudication
  -> claim
  -> external effect
  -> publication
  -> learning
  -> outbox
```

This is not a complete global lock order. It omits classes including incident
and recovery/control/epoch aggregates and does not expand every grouped
aggregate family into the exact 47 machine types. The machine manifest and its
current validator do not encode or verify lock ordering. Completing the class
inventory, transaction cohorts, database isolation profile, and adversarial
deadlock/serialization evidence remains an unresolved G7 reliability and
operations obligation.

Within a declared class, the intended rule is to sort locks by canonical
aggregate type then canonical ID bytes. The database profile must prove its
isolation/constraint behavior; this partial logical order alone is not a
concurrency guarantee. A command that discovers an undeclared lock dependency
aborts/retries rather than acquiring out of order.

Read dependencies are bound to expected aggregate/global positions. Predicate/range invariants use accepted uniqueness, exclusion, or serializable protections rather than wishful application checks.

## Event and projection boundary

Canonical events use Odeya domain contracts. Delivery may wrap them in CloudEvents or another transport envelope, but consumers verify the canonical event digest/reference. Transport retries do not create new domain facts.

Projection reducers:

- are deterministic over original canonical event bytes or tested upcasts;
- retain reducer/version/source checkpoint identity;
- are idempotent by canonical event identity;
- expose ledger position, completeness, freshness, and unavailable state;
- cannot call command handlers or produce authority decisions; and
- delete/rebuild rather than becoming an alternate truth source.

Private, thesis-intake, and public projections are different modules/data contracts. The public projection consumes only release-settled manifests and correction/withdrawal facts.

## Worker SDK boundary

Workers receive a `WorkContract` containing only:

- exact mission/protocol/work/context/artifact references;
- allowed capabilities, provider/model/environment identities, and egress;
- resource/expiry/attempt limits;
- output schema and declared artifact roles;
- exposure/rights policy and forbidden actions; and
- correlation, causation, and attempt identities.

Their only outputs are candidate artifacts, attempt observations, candidate graph deltas, or typed failure. A worker SDK has no event-store, grant-issue, claim-compile, verifier-assign, publication, secret-store, or unrestricted artifact-read interface.

Verifier SDKs are separate packages and credentials. Sharing an interface definition does not satisfy scientific independence; the verification record declares the observed independence vector.

## Compatibility boundaries

- Every closed contract has a stable URN and semantic version.
- Writers emit one accepted version; readers state exact ranges.
- Event upcasts are pure projections that retain original bytes and transformation identity.
- A change that alters a scientific, authority, rights, recovery, or publication consequence creates a new event/command/rule version and prospective migration decision.
- Vendor adapter versions cannot change domain enums, missingness, time, units, decimal, identity, or error meaning.
- Unknown required event/field/rule blocks reduction; it is never ignored into an apparently current projection.

## Build and repository enforcement target

Once Gate C authorizes a language/package layout, architecture checks must prove:

- imports follow the dependency graph;
- each schema/event/command has one declared owner;
- domain packages have no forbidden SDK/runtime imports;
- workers and clients lack canonical persistence dependencies;
- adapter tests consume language-neutral fixtures;
- no package cycle crosses a domain boundary;
- public/thesis projections cannot import private repository implementations; and
- source ownership/review rules match high-consequence modules.

Those checks are implementation evidence. Gate A is intended to freeze this
logical manifest and its closed
[`module-dependency-manifest` 0.1.0](../schemas/module-dependency-manifest.schema.json)
machine contract only after acceptance; the current proposal does not create
empty package theater. The machine instance is intended to cover every schema
and derive every command/event owner through the single aggregate-owner
registry, so a new discriminator cannot enter without an owner.

The current proposed instance is [`architecture/module-dependency-manifest.json`](../architecture/module-dependency-manifest.json). Its offline [validator](../scripts/validate_module_manifest.py) presently proves the declared owner/module graph is acyclic, every declared dependency and layer edge resolves, all 30 logical modules obey the declared layer policy, all 47 machine aggregate types have one owner record, all 115 current schema files have one matching `$id`/owner record, and all 121 command plus 135 event discriminators derive one mapped aggregate owner. The instance is reissued as version 2 with digest `sha256:6e6506fc71db0432d67c3fe3ca072812240049982e2ca20e487bfa1460042b8e`; its validator retrieves the exact version-1 Git blob from checkpoint `f4429ce5ca71e58ebb5d65776a45ebb6a2a18889` and independently verifies the predecessor byte count, raw SHA-256, declared version, and scoped manifest digest. That Git-object reachability is lineage evidence, not durable offline retention. These are design-vocabulary, inventory, lineage, and owner/module-DAG checks, not an admitted command/event registry, a global-lock-order proof, or a reducer-correctness proof. [ADR 0014](decisions/0014-resolve-first-slice-atomic-admission.md) resolves the first-slice reducer identity: `Verification` is the sole canonical reducer for the `verification` aggregate, while reproducibility, replication, and transport are internal orthogonal fold axes. The exact 43-command/60-event/25-aggregate candidate is machine-bound separately in [`first-slice-admission-resolution-candidate.json`](../architecture/first-slice-admission-resolution-candidate.json); C5/PRQ-009 and its payload, state, reducer, event, command, root, checkpoint, P0, activation, composite proof, and review records remain blocked or missing. This is architecture evidence only; it cannot prove future source imports or runtime isolation until actual packages exist.

## Architecture falsifiers

The dependency design fails if any proposed implementation needs to:

- import PostgreSQL/Temporal/S3/model SDK types into pure domain semantics;
- let `publication` alter a claim or let `claims` infer release;
- let `verification` consume producer narrative by default or mutate producer artifacts;
- let `learning` write production policy/configuration directly;
- let a projection or UI authorize from cached state;
- let a worker hold unrestricted storage/database/provider credentials;
- make external network success part of the canonical transaction;
- duplicate one enum/rule in multiple modules with independent evolution;
- create a cross-domain cycle to finish the first slice; or
- choose a vendor because the semantic owner was left ambiguous.

Gate A acceptance requires a machine-readable module/edge/owner manifest, cycle and forbidden-edge validation, mapping of every command/event/schema to one owner, independent architecture review, and operator acceptance of the exact candidate.
