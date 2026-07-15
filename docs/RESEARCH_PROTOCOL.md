# Research Protocol

Status: founding protocol design, 2026-07-15.

Odeya's research protocol turns rigor from prompt advice into executable state. A mission cannot advance because an agent says it is complete; it advances when typed outputs satisfy the frozen contract and the correct authority records the transition.

## Orthogonal result vocabulary

Operational state, validity, measurement, adjudication, verification, replication, transport, and claim revision are separate axes:

- operational: `interrupted`, `blocked`, `rights_blocked`, or `infrastructure_failure` describes why work did not proceed or settle;
- validity: `invalid` forbids scientific interpretation of the affected run;
- measurement: `no_valid_measurement` means the protocol did not obtain an admissible observation;
- scientific outcome: `supported_within_scope`, `contradicted`, `falsified`, `null_result`, or `inconclusive` can be derived only from a valid run under the frozen consequence rule;
- verification: `confirmed`, `rejected`, `inconclusive`, `invalid`, `blocked`, or `disputed` describes a named verification run and its observed independence;
- replication and transport: `independently_replicated` and `transported` require separate prospective work and cannot be inferred from replay;
- revision: `correction` and `retraction_notice` create new immutable claim versions and dependent publication actions.

“Infrastructure null” and “rights blocked” may be presentation labels derived from operational axes, but neither is stored as a scientific outcome. A valid `null_result` requires a valid measurement. These labels must never collapse into success/failure telemetry.

## Canonical mission contract

One `ResearchMissionSpec` is the source of truth. At minimum it contains:

- identity, version, ownership, contributors, conflicts, and source lineage;
- the real-world question, decision consequence, scope, and non-goals;
- current prior, competing hypotheses, assumptions, and residual uncertainty;
- novelty map, occupied alternatives, and why this mission is discriminating;
- source roles and data rights before acquisition;
- frozen datasets, splits, sampling rules, exclusions, and denominators;
- baseline ladder and ablations;
- typed metrics, estimators, units, comparators, thresholds, intervals, and missing-data policy;
- at least three named falsifiers where the domain allows them;
- deliberately broken positive controls for every consequential gate;
- expected observations under competing hypotheses;
- analysis plan, multiplicity policy, stop rules, and correction policy;
- planned compute, time, cost, network, credentials, and approval requirements;
- safety classification and prohibited actions;
- exact proof artifacts, replay commands, verifier requirements, and CI checks;
- eligible and forbidden claim language for every terminal outcome;
- authorship, licensing, disclosure, embargo, and release policy;
- handoff and grounded-learning requirements.

Free-form context may accompany these fields, but it cannot replace them. Numeric bars are machine-evaluable objects, not prose strings.

## Lifecycle gates

### 1. Intake

**Input:** thesis proposal.
**Required output:** provenance, rights declaration, risk screen, conflict record, admit/defer/decline decision.
**Stop:** no mission begins without an explicit decision and accountable principal.

### 2. Orient

**Input:** admitted proposal.
**Required output:** source-of-truth map, literature and baseline map, rejected alternatives, unknowns, domain constraints, and evidence-access plan.
**Stop:** sources do not enter the evidence graph until a role and rights basis are recorded.

### 3. Contract

**Input:** orientation record.
**Required output:** validated `ResearchMissionSpec`, authority assignments, resource envelope, and claim surface.
**Stop:** no planning against an unvalidated or ambiguous contract.

### 4. Preregister

**Input:** validated mission.
**Required output:** immutable `ProtocolSnapshot` covering hypotheses, splits, metrics, falsifiers, controls, analysis, stop rules, and claim consequences.
**Stop:** confirmatory data exposure or execution is forbidden before freeze.

Exploration remains allowed only in an explicitly exploratory branch. Findings from that branch become a new prospective protocol, never a retroactive edit.

### 5. Preflight

**Input:** frozen protocol.
**Required output:** executable manifest, dataset and environment digests, tool versions, negative-fixture results, cost estimate, authority grants, and recovery checkpoint.
**Stop:** a failing offline gate, missing resource, unclear permission, or positive control that does not fire blocks execution.

### 6. Execute

**Input:** authorized immutable run manifest.
**Required output:** attempt records, exact actual resource use, raw artifacts, logs, errors, and content digests.
**Stop:** circuit breakers enforce time, cost, rate, safety, and data boundaries. Retry exhaustion records a blocked or infrastructure outcome; it does not create acceptance.

### 7. Verify

**Input:** promoted artifacts and frozen protocol.
**Required output:** clean-environment recomputation, metric observations, falsifier verdicts, integrity checks, and discrepancies from the producer.
**Stop:** the verifier must be a different execution identity. Missing evidence fails closed.

### 8. Adversarial review

**Input:** verification package and proposed claims.
**Required output:** confounds, leakage checks, alternative explanations, sensitivity analysis, claim-boundary violations, and disclosure risks.
**Stop:** unresolved material findings block sealing. Model reviewers may discover issues but cannot substitute for deterministic checks or independent domain review.

### 9. Adjudicate

**Input:** protocol, evidence, verifier results, and review findings.
**Required output:** typed outcome, reasons, eligible claims, unresolved uncertainty, and next legal action.
**Stop:** no claim can exceed the frozen consequence table or verifier evidence.

### Separate release workflow

**Input:** eligible claim package and publication authority.
**Required output:** sealed publication manifest, exact evidence projection, rights/safety decision, citations, limitations, and correction endpoint.
**Stop:** publication is optional and separately authorized. A passed scientific gate does not grant release permission.

Release is not a scientific lifecycle stage. After adjudication, a separate publication aggregate may request, deny, authorize, seal, release, reconcile, withdraw, or correct a public projection. Scientific eligibility never grants release authority, and release state never changes the underlying scientific outcome.

### 10. Handoff

**Input:** current ledger position.
**Required output:** factual mission state, exact revisions and artifacts, active leases, blockers, decisions, resource use, and next legal action.
**Stop:** every closed, paused, interrupted, or transferred mission receives a reconstructible handoff.

### 11. Learn

**Input:** terminal or externally settled outcomes.
**Required output:** grounded observations, candidate workflow changes, regression fixtures, and evaluation plan.
**Stop:** no production promotion from self-review, one anecdote, or positive-result preference.

## Baseline and falsification discipline

Each mission defines the smallest honest ladder needed to locate value:

1. no-action or existing-practice baseline;
2. simple deterministic baseline;
3. strong non-agentic or single-agent baseline;
4. proposed workflow;
5. ablations identifying which component mattered;
6. transfer or external-settlement test where the claim requires it.

Multi-agent architecture must beat a comparable single-agent baseline under reported resource budgets. More tokens or parallel workers are experimental variables, not free improvements.

For every consequential gate, the mission includes at least one deliberately broken artifact that should fail. A gate that cannot demonstrate this behavior is only an assertion.

## World contact

Internal consistency is a floor. Depending on the domain, world contact can mean:

- executable tests on retained inputs;
- recomputation from raw data;
- simulator or testbed outcomes;
- a deterministic authoritative API;
- a physical observation settled by an independent instrument;
- blinded expert review;
- independent replication.

The contract asks: **could this gate pass while the object it guards is actually broken?** If yes, another reality contact is required or the claim must narrow.

## Evidence admissibility

Evidence is admitted only when its role, origin, rights, capture method, integrity, and relation to a claim are explicit. Source roles include orientation, hypothesis generation, protocol design, evaluation, sealed truth, transfer, and publication support.

Model-generated summaries, inferred metadata, screenshots without recoverable context, and signatures without semantic recomputation cannot independently settle a claim.

## Claim compiler

The claim compiler derives allowed language from:

- frozen claim consequences;
- metric and uncertainty results;
- falsifier outcomes;
- baseline and ablation coverage;
- source and population scope;
- verifier independence;
- replication state;
- unresolved adversarial findings;
- rights, safety, and publication decisions.

It emits both eligible and forbidden claims. For example, a simulation improvement without external transfer may support “improved this pinned simulation metric” while forbidding “safer in deployment.”

## Corrections

A correction record names:

- the superseded claim and every known projection;
- the triggering evidence;
- whether the protocol, execution, analysis, verification, wording, or release failed;
- the minimally changed replacement claim;
- downstream datasets, papers, evaluations, and learning records that must be invalidated or recomputed.

Prior records remain addressable. The current projection makes the correction at least as visible as the original claim.

## Resource accounting

Estimated and actual resources are separate fields. Record model and harness versions, tokens, calls, wall time, retries, CPU, memory, accelerator type and time, storage, network, external API cost, human time, and approval latency where available. Missing usage remains `unknown`, never `0`.

Capability is reported as a curve across resource budgets when budget can materially change the result.

## Scientific authorship

The publication manifest records human and system contributions at the granularity supported by retained events. It never exposes private chain of thought. Authorship, acknowledgements, and disclosure follow venue and domain rules and remain human-authorized.
