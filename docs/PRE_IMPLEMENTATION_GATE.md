# Pre-Implementation Architecture Gate

Status: blocking. Runtime implementation is not authorized until Gate A is accepted, any authorized Gate B probes are settled, and Gate C explicitly authorizes one bounded increment.

“One hundred percent architecture” does not mean pretending every future detail is knowable. It means every invariant, high-cost choice, safety boundary, scientific semantic, module contract, and implementation dependency needed for the first vertical slice is decided; remaining uncertainty is named, bounded, reversible, and assigned an experiment before it can affect production.

## Gate A — Architecture acceptance rule

Each gate item must have:

- an owner and decision record;
- the evidence and alternatives considered;
- a falsifier or failure test;
- a clear accepted/rejected/deferred state;
- downstream dependencies;
- reversal cost and migration path;
- explicit operator acceptance for constitutional or high-consequence choices.

No item passes because a document sounds complete. Gate A accepts meanings, contracts, threat assumptions, test oracles, dependency order, and reversibility. It does not pretend to have executed code that the implementation lock forbids.

## G0 — Mission and claim boundary

- [ ] Company mission, user, first wedge, and non-goals are unambiguous.
- [ ] Sentinel, Telos, and Inbar are represented with current corrections and bounded claims.
- [ ] “Research engine,” “autonomy,” “learning,” “verification,” and “value” have operational definitions.
- [ ] Private-engine/open-research boundary and publication authority are accepted.
- [ ] First vertical-slice mission and its settled evidence snapshot are selected.

## G1 — Scientific and mathematical constitution

- [ ] `MATHEMATICAL_CONSTITUTION.md` is reviewed by the relevant statistical/domain expertise and converted into versioned method-registry contracts.
- [ ] Exploratory, confirmatory, replication, invalid, null, inconclusive, and blocked semantics are formalized.
- [ ] Uncertainty representation, calibration, missingness, and interval policy are specified.
- [ ] Hypothesis, baseline, falsifier, control, ablation, and transfer requirements are typed.
- [ ] Sequential/adaptive testing, optional stopping, multiplicity, and protocol-amendment rules are specified.
- [ ] Causal claims require an explicit identification strategy and assumption audit.
- [ ] Information gain, decision consequence, cost, risk, and portfolio priority remain inspectable rather than one opaque reward.
- [ ] Replication independence and evidence-synthesis rules are specified.
- [ ] Resource-aware agent evaluation reports uncertainty and comparable compute curves.
- [ ] Domain-specific statistical adapters cannot weaken kernel-level evidence invariants.
- [ ] The layered rule registry, validation-result contract, and founding cross-object rules in `SEMANTIC_VALIDATION.md` are frozen with adversarial traces.
- [ ] Physical quantity, unit, frame, time, covariance, measurement, model, VVUQ, observability, identifiability, sim-to-real, and actuator-authority semantics in `PHYSICAL_SCIENCE_CONSTITUTION.md` are accepted for the first physical-domain adapter.

## G2 — Canonical domain model and lifecycle

- [ ] One `ResearchMissionSpec` and canonical serialization rule are frozen.
- [ ] Protocol snapshot, amendment, run manifest, event, artifact, metric, falsifier, claim, verification, correction, publication, handoff, and learning schemas are complete.
- [ ] Lifecycle transition table defines actor, input, output, invariant, stop rule, idempotency, and recovery for every edge.
- [ ] Terminal scientific outcomes and operational interruption states cannot be confused.
- [ ] Claim compiler maps each evidence outcome to eligible and forbidden language.
- [ ] Structural schema validity and semantic/state/authority/scientific admissibility are separate retained results; indeterminate fails closed.
- [ ] Corrections and dependency invalidation are replayable and visible.
- [ ] Research-state view, compilation receipt, epistemic graph delta, experiment candidate, planning epoch, work contract, candidate artifact, and epistemic-transition meanings are frozen without granting model authority.

## G3 — Authority, security, and privacy

- [ ] Proposal, protocol, safety, data-rights, resource, execution, verification, outcome, and publication authorities are separate records.
- [ ] Root assignment, human-only action matrix, quorum, delegation, grant-use, expiry, revocation, and break-glass semantics in `AUTHORITY_MATRIX.md` are accepted.
- [ ] Risk tiers and domain-specific escalation criteria are accepted.
- [ ] Threat model covers contributed content, tools, memory, models, code, workers, providers, insiders, and supply chain.
- [ ] Capability grants, credentials, egress, sandbox, artifact promotion, and revocation semantics are defined.
- [ ] Data classification, rights, residency, retention, deletion, sealed truth, and model-training policy are defined.
- [ ] Pause, kill, revoke, incident, withdrawal, and correction paths have test plans.
- [ ] PRQ-013 `HumanDecisionAssurance` is accepted: a protected explicit
  ceremony binds the exact displayed and candidate bytes, decision basis and
  limitations, verifier-generated unpredictable challenge, separate
  human-initiated confirmation gesture, user presence and verification,
  principal identity-proofing and authenticator binding,
  authenticator/key/session custody and unattended-agent exclusion,
  delegation, objections, conflicts, effective quorum, replay/expiry controls,
  and sanitized independent evidence. Authentication intent or a valid
  signature never substitutes for human review, understanding, or substantive
  decision intent, and the bounded claim never asserts cognition.
- [ ] `PRQ-013-KB-001` is retained and rejects an unattended agent that can
  invoke a human-labelled signing key and produce a cryptographically valid
  signature over the exact candidate while the verifier-generated challenge,
  human-initiated confirmation gesture, identity/authenticator binding, user
  presence, and user verification are absent or `unknown`.

No current schema is claimed PRQ-013-compliant. Gate A remains blocked under
[ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
and the
[cross-program process-evidence packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md).

## G4 — Evidence, memory, and provenance

- [ ] Canonical events and artifacts are distinguished from all projections and indexes.
- [ ] Content digest, canonicalization, signature, attestation, and timestamp trust assumptions are explicit.
- [ ] Every claim can traverse to exact protocol, code, data, environment, command, resource, evaluator, and verifier.
- [ ] W3C PROV and RO-Crate mappings are defined without losing Odeya-specific semantics.
- [ ] Context packs, retrieval, summaries, and handoffs are reproducible and cannot silently promote assertions.
- [ ] The Research-State Compiler binds exact source position, policy, role, exposure, selected context, omissions, contradiction coverage, and sealed-truth noninterference evidence.
- [ ] Sensitive audit data and private reasoning are excluded or separately controlled.
- [ ] `STANDARDS_PROFILE.md` entries have exact frozen versions, official copies/digests, validators, conformance vectors, deviations, and migrations.

## G5 — Evaluation and improvement

- [ ] Component, stage, mission, scientific, operational, and safety evaluation suites are designed.
- [ ] Single-agent, deterministic, human-expert, and current-practice baselines are comparable by resource.
- [ ] Private holdout, contamination, grader-validation, and transcript/artifact audit policies are accepted.
- [ ] Known-bad fixtures exist on paper for every consequential gate.
- [ ] Learning records require independently verified outcomes and applicability conditions.
- [ ] Improvement-lab quarantine, promotion, canary, rollback, and human approval paths are specified.
- [ ] No production recursive self-modification path exists.
- [ ] Grounded outcome and observable epistemic conduct are evaluated separately; hidden chain-of-thought and self-report are never proof.
- [ ] Material evidence disposition, refutation response, contradiction retention, selection accounting, and valid stop/escalation have anti-gaming fixtures.
- [ ] Claim-bearing generation is constrained by separately reserved deterministic, compute, expert, physical, and safety verification capacity.

## G6 — Module and interface architecture

- [ ] Module ownership and allowed dependency graph are frozen.
- [ ] Commands, events, ports, errors, and compatibility/versioning policy are specified.
- [ ] Control plane, workflow substrate, workers, verifier, artifact store, policy, indexer, learning lab, and cockpit trust boundaries are explicit.
- [ ] One-writer and selective-parallelism rules are encoded in contracts.
- [ ] Vendor replacements cannot change mission or verdict semantics.
- [ ] Build-versus-adopt decisions include exit and migration plans.
- [ ] Epistemic state, deterministic state compilation, untrusted planning, verification backpressure, and claim adjudication have noncircular ownership and no ambient I/O path into pure reducers.

## G7 — Reliability and operations

- [ ] Transaction, outbox, lease, heartbeat, compare-and-set, retry, idempotency, and duplicate-cost semantics are frozen.
- [ ] Interruption, partial artifact, stale worker, provider outage, budget exhaustion, and verifier disagreement behavior are specified.
- [ ] Backup, restore, disaster recovery, retention, migration, and ledger-integrity procedures have recovery objectives.
- [ ] Observability hierarchy, redaction, sampling, and cost accounting are defined.
- [ ] Actual and estimated resource usage remain separate; unknown cannot become zero.

## G8 — UI/UX and publication projections

- [ ] Information architecture and exact state vocabulary are accepted.
- [ ] Supported, null, invalid, blocked, unknown, stale, withheld, corrected, and retracted states have specified representations and fixture-based acceptance plans.
- [ ] Every visual and motion source maps to canonical state.
- [ ] Keyboard, screen reader, forced colors, reduced motion, zoom, print, small-screen, and deep-link standards are specified.
- [ ] Private cockpit, thesis intake, and public research projection have separate data contracts and authority.
- [ ] No chain-of-thought, fake live telemetry, invented progress, or client-side scientific authority appears.

## G9 — Implementation order and proof plan

- [ ] Dependency-ordered implementation plan identifies the smallest coherent increments.
- [ ] Each increment has entry assumptions, executable acceptance tests, negative fixtures, evidence output, and rollback.
- [ ] First slice uses a pinned, settled proof-project snapshot and no active dirty worktree as truth.
- [ ] Technology versions and supported-platform matrix are pinned only after contracts are accepted.
- [ ] CI, reproducible local environment, security checks, and architecture-conformance tests are designed before feature work.
- [ ] Staffing and compute needs are derived from the plan rather than prestige choices.

## G10 — Final architecture red-team review

- [ ] Independent architecture review uses adversarial schema instances and transition traces to try to make false science pass every gate.
- [ ] Security review traces attempts to obtain data, spend, execution, verifier, and publication authority improperly through the specified contracts.
- [ ] Recovery review enumerates every crash point and expected retained state; executable fault injection belongs to increment exit gates.
- [ ] Scientific review identifies claim types the engine cannot validly adjudicate and converts them to explicit refusals or domain-adapter requirements.
- [ ] Product review uses non-executable fixtures and wire contracts to confirm that truth and limitations are representable without invention.
- [ ] Cognitive review attempts sealed-truth influence through retrieval/caches, ignored refutation, consensus-as-evidence, fabricated process records, stale-view admission, and verification-backlog overflow.
- [ ] All critical/high findings are closed; accepted medium findings have owners and bounded experiments.
- [ ] Operator signs the exact architecture candidate or requests changes; this does not itself authorize product implementation.

## Gate B — Disposable architecture probes

Some product choices cannot honestly be accepted from prose alone. After Gate A, the operator may authorize narrowly scoped, disposable, non-product probes for questions such as workflow replay, cross-store crash recovery, canonicalization across languages, sandbox escape assumptions, or accessibility behavior.

Each probe must have:

- one falsifiable architecture question;
- no production data, credentials, external side effects, or reusable product surface;
- fixed time/resource ceiling;
- retained inputs, outputs, environment, and result;
- a decision it will confirm, change, or leave provisional;
- automatic deletion or quarantine plan for everything not retained as evidence.

If the operator does not authorize a probe, the associated product choice remains provisional and cannot become a hidden implementation assumption.

## Gate C — Bounded implementation authorization

Only after Gate A decisions and authorized Gate B findings are integrated:

- [ ] architecture candidate has a clean immutable commit, manifest, and candidate tag;
- [ ] every critical/high finding is closed on that exact commit;
- [ ] medium findings have a non-impact argument, owner, expiry, and rollback;
- [ ] one offline, rights-cleared composite fixture pack is pinned with expected supported, interval-crossing-zero/inconclusive, invalid, discrepancy, correction, blocked, and refusal consequences;
- [ ] the operator explicitly authorizes exactly one implementation increment;
- [ ] the increment's executable tests, fault injection, UI tests, and recovery evidence become its exit gate—not a reason to bypass architecture.

## Implementation lock

Until Gate A passes:

- permitted: research, architecture, specifications, schemas, adversarial schema fixtures, decision records, threat models, mathematical definitions, paper plans, non-executable interface diagrams, and validation of those artifacts;
- prohibited: engine runtime code, production UI code, infrastructure provisioning, deployment, external integrations, DNS changes, data migration, autonomous execution, or public release.

After Gate A, only explicitly authorized Gate B probes are additionally permitted. Product implementation remains prohibited until Gate C.

An exception requires an explicit operator amendment naming the exact scope and why it does not compromise the architecture gate.
