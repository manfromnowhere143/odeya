# Cognitive Control Contracts

Status: proposed Gate A architecture contract, 2026-07-15. This document makes the model-driven layer in [Cognitive Architecture](COGNITIVE_ARCHITECTURE.md) reviewable. It defines records, invariants, and acceptance evidence; it does not authorize a runtime, choose a model provider, or claim autonomous scientific capability.

## Verdict

Odeya's cognition is not a privileged agent process. It is an untrusted, replaceable proposal fabric enclosed by a deterministic scientific control plane.

The irreducible boundary is:

```text
canonical facts + exact authority + exact exposure policy
  -> deterministic compiled view and legal frontier
  -> bounded model/tool work
  -> candidate artifacts and proposed epistemic changes
  -> independent verification
  -> deterministic adjudication
  -> canonical event batch or explicit refusal
```

The architecture must make every arrow inspectable without retaining or treating private chain-of-thought as evidence. A persuasive narrative can explain a result to a human; it cannot establish the result.

## Why outcome-only evaluation is insufficient

A 2026 preprint covering more than 25,000 scientific-agent runs reported that scaffold choice explained much less observed variation than the base model and that agents frequently failed to use contradictory evidence or revise after refutation. Its most important architecture lesson is not one exact percentage; it is that final-task success can hide a scientifically invalid process. [AI scientists produce results without reasoning scientifically](https://arxiv.org/abs/2604.18805)

Recent expert benchmarks likewise emphasize incomplete evidence, conflicting results, iterative analysis, consequential judgment, and uncertainty rather than clean one-answer tasks. [OpenAI LifeSciBench](https://openai.com/index/introducing-life-sci-bench/), [OpenAI GeneBench-Pro](https://openai.com/index/introducing-genebench-pro/)

Two additional 2026 preprints sharpen the refusal and contamination requirements. A clean-room scientific-synthesis evaluation reported a best factual F1 of `0.337` among the evaluated deep-research systems and material degradation when reference-like ground-truth artifacts were blocked. PseudoBench reported near-zero refusal for many pseudoscientific premises and a highest measured resistance of `27.4%` in its tested set. These are benchmark-specific, non-peer-reviewed results, not universal capability estimates; they nevertheless make leakage-controlled synthesis, atomic-fact coverage, premise challenge, and valid refusal mandatory Odeya eval dimensions. [Can AI Agents Synthesize Scientific Conclusions?](https://arxiv.org/abs/2606.11337), [PseudoBench](https://arxiv.org/abs/2606.18060)

Odeya therefore evaluates two separate things:

1. **grounded outcome:** whether the artifacts and eligible claim are correct under the declared oracle and scope;
2. **observable epistemic conduct:** whether the system exposed relevant alternatives, dispositioned material evidence, responded correctly to refutation, preserved contradictions, respected selection effects, and stopped when proof was unavailable.

Neither axis substitutes for the other. Observable conduct is reconstructed from typed actions, evidence dispositions, graph changes, tool receipts, and decisions—not from hidden model reasoning.

## Constitutional contract family

The names below are logical object names. Gate A requires exact schemas, identities, semantic rules, fixtures, ownership, and compatibility policy before implementation begins.

### 1. `ResearchStateView`

An immutable, exposure-bounded model input compiled at one canonical ledger position:

```text
view ID and schema/profile versions
mission, protocol, and exact ledger/checkpoint reference
compiler and compilation-policy identity
role, objective, attempt, and correlation-group identity
permitted claim and action surface
relevant evidence and epistemic subgraph references
competing hypotheses, contradictions, and model-incomplete state
required controls, falsifiers, and unresolved blockers
legal command frontier and remaining resource envelope
data sensitivity, purpose, residency, and exposure ceiling
freshness frontier and stale-source declarations
selected-context manifest and omission manifest
output contract and forbidden actions
stable view ID/version; canonical identity is issued externally after validation
```

The view is data, not authority. A listed legal command is only a candidate
action at that ledger position. Each frontier entry binds the exact immutable
`CommandContractRegistry` subject, exact member key/version/digest, exact
`RegistryActivation` sequence/digest, exact membership-proof artifact and
derivation profile, exact payload-schema bytes, and activation-scope evidence.
A mutable-looking label such as `active` is not a proof and is not permitted in
the view. Command admission dereferences those exact bytes and rechecks current
activation, scope, state, policy, and grants.

The graph binding distinguishes `absent_genesis` from `existing_aggregate`.
Absence carries frontier-bound absence evidence and null graph version, root,
head, and origin event. It is not a synthetic canonical version `0`. An
existing aggregate begins at version `1` only after a first admitted graph-
delta event and binds that origin event as well as its current head.

### 2. `ContextCompilationReceipt`

A reproducible account of how one view was formed:

```text
compilation result: pass, fail, indeterminate, or not_run, with reasons/evidence
compiler implementation and build identity
source checkpoint and policy digests
requested role/objective/context budget
dependency traversal and retrieval rule identities
candidate references considered
selected, omitted, redacted, and unavailable references with reason codes
required-evidence and contradiction coverage results
sealed-truth and forbidden-exposure negative checks
token/byte/count budget accounting
exact externally issued view identity and digest
```

Construction is acyclic:

```text
schema-valid ResearchStateView subject (no self digest or receipt reference)
  -> external canonicalization registry issues View canonical-object digest
  -> ContextCompilationReceipt references exact View ID/version/schema/digest
  -> external bundle/root record binds View digest + Receipt digest
```

The view does not point back to its digest-bearing receipt. Neither subject embeds its own digest. Stable IDs plus a separately sealed root are used if a reviewer needs bidirectional navigation.

The receipt must distinguish `omitted_by_budget`, `forbidden_by_policy`, `unavailable`, `stale`, `superseded`, and `not_relevant`. An empty omission list is a positive claim and requires a completed search/coverage rule; absence cannot imply completeness.

The receipt records failures instead of disappearing them. Only `pass` may be
named by a prospective `WorkIntent` and later included in the atomic assignment
cohort from which a future `WorkContract` is derived; `pass` requires complete evidence and
contradiction coverage, completed omission search, no unresolved taint or
contamination, passing negative and applicable clean-room checks, a satisfied
budget, and deterministic replay. `indeterminate` and `not_run` use reason
codes rather than fabricated missing references.

### 3. `EpistemicNodeVersion` and `EpistemicGraphDelta`

The graph stores scoped propositions about knowledge, not declarations of reality.

Node kinds include hypothesis, mechanism, variable, assumption, definition, prediction, expected observation, contradiction, residual unknown, and experiment candidate. Evidence, source, method, activity, environment, metric result, and verifier records remain separately governed canonical objects referenced by the graph.

Every proposition version carries:

```text
exact proposition and claim type
population, environment, time, and applicability scope
variables, dimensions, units, coordinate/reference frames
structural or causal interpretation, if any
assumptions and explicit model-discrepancy class
prior/likelihood family or `not_modeled`
model-incomplete flag
predictions and prospective falsifiers
uncertainty channels without one generic confidence number
origin, exposure, and immutable lineage to a superseded version, if any
```

A node contains no mutable admission, validity, future-position, or superseded
state. Supporting/contradicting evidence, rivals, compatible alternatives,
dependencies, predictions, and supersession are canonical only as closed typed
edges. A graph delta binds the exact aggregate, protocol branch, predecessor
root/head/reducer/ledger position, node additions, edge changes, admission
class, explicit evidence dispositions, and reason codes. It cannot delete
history, mutate an existing node version, or admit itself.

`proposed_lineage` on a new node version is descriptive proposal metadata. It
never supersedes the predecessor by itself. Canonical supersession occurs only
when the delta contains an explicit typed `supersession_relation` edge and a
later governed admission commits that edge. A correction delta also binds its
predecessor/successor pair, non-resurrection rule, affected-dependency
manifest, and mandatory monotone fanout rule.

Verification and adjudication requirements are outputs of an exact typed
admission profile and immutable rule over a committed input digest, with
retained derivation evidence; callers cannot select them. Claim-bearing work
still requires both. A correction is not universally adjudication-bearing:
the correction profile may derive verification-only or verification-plus-
adjudication, while the explicit supersession, non-resurrection, and fanout
obligations remain mandatory in either case.

### 4. `ExperimentCandidate`

An experiment, intervention, or analysis proposed for comparison before authorization:

```text
research objective and candidate estimand
intervention, comparator, and observational regime
predicted observation under every material hypothesis
discriminating evidence and falsification power
measurement model, uncertainty, observability, and identifiability
sampling, control, randomization/blinding, and analysis design
adaptation, stopping, multiplicity, and selection regime
required data, instruments, assets, environments, and authorities
verification oracle and independent reproduction plan
estimated resource vector and reserved verification demand
risk, harm, reversibility, and safe-stop contract
transport/external-validity boundary
```

`not_identifiable`, `not_observable`, `measurement_not_admitted`, `oracle_absent`, and `authority_absent` are first-class outcomes. A high model score cannot override them.

Execution demand and verification capacity use separate closed vectors and
cannot compensate for or consume one another. Indeterminate demand blocks
promotion rather than being coerced to zero.

### 5. `PlanningEpoch`

One bounded receding-horizon planning decision:

```text
input view and legal-frontier digest
explicit generation outcome, candidate set, and generation lineage
hard-filter results
Pareto dimensions and uncertainty bounds
declared decision rule and sensitivity analysis
selected, retained, rejected, and deferred candidates
best-of-N/adaptive-search multiplicity record
generation and verification resource allocation
stop/replan/escalate condition
human selection reference where the rule requires one
```

An Elo score, model vote, debate result, or scalar reward is a ranking signal only. It is never evidence for the hypothesis being ranked.

An empty candidate set is valid only with an explicit empty, failed, or
indeterminate generation outcome and stop, replan, or escalation. At most one
candidate is selected; selection requires a passing hard filter, complete
registered-unit objectives, Pareto-frontier status, and resource packing of
`fits`.

### 5a. `WorkIntent`

`WorkIntent` is the closed prospective planning record between selection and
assignment. It can bind the objective, permitted deliverable classes,
candidate-worker requirements, data constraints, output contract, and bounded
estimates. It is intentionally non-authoritative:

- no active lease or current worker is represented;
- authority grants and resource reservations are empty or null;
- it grants no dispatch, materialization, external-effect, or spend authority;
- no bytes may cross an execution boundary from the intent; and
- its current canonical identity is unresolved, so it is not admitted or
  assignable.

The required order is `WorkIntent -> admitted verification.assign atomic
commit -> post-assignment derived WorkContract -> separately admitted dispatch
claim`. The assignment commit must bind the exact canonical intent identity and
atomically establish the worker principal, active lease, authority grants,
active data-use decisions, sandbox capability, resource reservation, and
passing state-compilation bundle. A prospective planner cannot populate those
current facts early.

### 6. `WorkContract`

A future `WorkContract` is a post-assignment deterministic control artifact,
not a proposal and not dispatch authority. Its constructible form must be
derived from one exact successful `verification.assign` commit and bind that
commit's complete atomic cohort:

```text
exact canonical WorkIntent identity
exact verification.assigned event/commit identity
worker principal and active canonical lease
current authority grants and active data-use decisions
sandbox capability and resource reservation
passing state-compilation bundle
deterministic derivation rule and exact committed input set
```

The current `work-contract:0.2.0` resource is only a blocked candidate. It
contains no assignment facts, has a null canonical digest/profile, declares
itself nonconstructible and nondispatchable, and requires a future immutable
resource reissue after a canonical `WorkIntent` and exact assignment cohort
exist. Historical consumers that still name `work-contract:0.1.0` are explicit
migration blockers; they are not silently redirected to the blocked candidate.

A future constructed contract still provides capability handles, never ambient
credentials. Before any bytes or spend cross an execution boundary, a separate
dispatch admission must recheck the exact lease, grants, data decisions,
sandbox, policy, resource reservation, controlled time, positions, expiry, and
revocation, and atomically commit its own dispatch/exposure claim. Assignment or
WorkContract construction alone never starts work.

Calls to external model, tool, data, or paid-compute providers reuse Odeya's existing `external_effect.authorize -> external_effect.start -> observation/reconciliation` boundary with a work-dispatch effect class; they do not invent an agent-private network path. Fully local execution still requires the exact worker lease, data materialization intent, sandbox capability, and resource reservation before bytes become visible to the process.

The future work-contract canonical identity is issued externally; the contract
subject cannot embed its own payload/canonical digest.

### 7. `CandidateArtifact`

The worker's untrusted result package:

```text
work contract and view digest
producer/model/harness/tool/environment identities
input and output artifact manifests
observable action/tool/result receipts
methods and implementation identities
proposed graph delta and evidence dispositions
assumptions, limitations, unknowns, contradictions, and failure state
typed complete resource observations, including explicit unknown/missing states
retry/selection history
proposed next actions
```

Candidate artifacts are retained for audit but have no claim, publication, memory, method-admission, or policy authority.

### 8. `EpistemicTransitionRecord`

This is the process-level scientific record. It captures externally checkable changes without asking for hidden reasoning:

```text
graph aggregate and protocol branch
exact predecessor graph version/root/head/reducer/ledger position
proposed graph-delta identity or explicit not-produced/indeterminate result
material evidence available in the view
evidence consulted and exact artifact/result references
one disposition per material evidence item
hypotheses introduced, retained, revised, split, superseded, or rejected
new contradictions and residual unknowns
falsifier outcomes and consequence-table application
assumption, estimand, method, or scope changes
surprise, stop, replan, or escalation reason
rule/model/human identities responsible for each change
typed verification and adjudication requirements/dispositions
closed typed change classes
```

The transition is a non-authoritative process record, not admission authority.
`changed` requires at least one closed typed change class and a typed graph-
delta proposal. Node-lineage edits are not privileged: an edge-only,
material-evidence-disposition-only, or contract-only transition is representable
without fabricating a hypothesis edit. The graph-delta status is bidirectional:
`proposed` is permitted if and only if the result is `changed`; `no_change` and
`incomplete` require an empty typed-change set and `not_produced` or
`indeterminate`. Incomplete coverage/change or unsatisfied required controls
cannot continue.

Allowed evidence dispositions are closed and non-evaluative, for example `incorporated`, `contradicts`, `supports_under_scope`, `invalid_source`, `inadmissible_method`, `duplicate_dependency`, `not_applicable`, or `unresolved`. `ignored` is not an admissible disposition. A system may conclude that evidence is invalid or irrelevant, but it must retain the exact rule and evidence supporting that conclusion.

### 9. `VerificationPackage`

The `verification-run` `0.2.0` contract is an immutable terminal package containing:

```text
subject artifact/result/claim references
verifier identity and multidimensional independence vector
exposure and conflict declarations
schema/integrity checks
method/statistical/causal/physical checks
known-answer and known-bad controls
clean-environment replay and independent implementation results
claim-boundary, calibration, transport, and safety findings
disagreements, counterexamples, unresolved dimensions
verdict per dimension and eligible next action
```

One verifier cannot establish independence merely by using a different prompt. Shared provider, model family, training-data lineage, tools, source corpus, implementation, human principal, and organizational incentives are explicit correlation axes.

The package binds the exact subject set and prior assignment, including the frozen IV0–IV4 requirement class, independence requirement, plan, protocol, method, capacity reservation, exposure plan, inputs, environment, and controls. It separately binds actual run/input/environment/code manifests and plan comparison. It distinguishes `completed`, `failed`, `not_started`, and `completion_unknown`; only `confirmed`, `rejected`, `inconclusive`, `invalid`, and `blocked` are terminal package assessments. Confirmation means the exact assigned profile passed; it does not universally imply organizational independence or every scientific dimension. Request/running state remains event-derived and dispute is a monotonic overlay. The package cannot reference its successor completion event, and advisory next actions grant no authority. See [Verification Protocol](VERIFICATION_PROTOCOL.md).

### 10. `ModelConfigurationRecord` and `RoutingDecision`

Model and harness selection is evidence-governed and replaceable:

```text
provider/model/version/region and observed identity
harness/prompt/context/tool configuration digest
data handling and retention behavior
role and modality capability claims
evaluation-set and validity-window references
performance/cost/latency/failure curves with uncertainty
correlation-group and independence attributes
known limitations and disallowed risk/data classes
candidate set, hard exclusions, Pareto result, and selected configuration
fallback rule and new-attempt semantics
```

The machine contracts are
[`model-configuration-record.schema.json`](../schemas/model-configuration-record.schema.json)
and [`routing-decision.schema.json`](../schemas/routing-decision.schema.json).
A model-configuration record is an immutable observation, not a provider trust
certificate. Provider, model, weights, training-data, residency, retention, and
identity facts retain `observed`, attested, unverified, unknown, or
indeterminate distinctions instead of collapsing them into a model name. It
pins harness, prompts, context compiler, tools, generation controls, operating
conditions, uncertainty, all eleven correlation axes, limitations, and the
exact evidence frontier. It cannot establish scientific evidence,
independence, routing, dispatch, spend, exposure, or publication authority.
Every estimate, interval bound, and resource amount is a canonical exact-
decimal string. Binary JSON numbers, exponent notation, leading zeros, plus
signs, and every lexical negative zero are rejected; semantic comparison uses
decimal arithmetic and an exact unit reference.

A routing decision binds one exact request, checkpoint, engine root,
configuration-registry snapshot, policy result, task/evaluation profile,
resource vector, verification capacity, candidate partition, and controlled
time. Every considered configuration receives the complete eleven hard-
constraint dispositions and nine decision-dimension observations. A selected
configuration must be current at the decision, evidence-complete, pass every
hard constraint, and lie on the retained Pareto frontier. Empty, excluded, and
indeterminate candidate sets remain valid refusal outcomes; unknown values are
never coerced into scores or bounds. Any provider/model fallback requires a new
routing decision and a new attempt identity.

Selection is still not dispatch. Admission rechecks the configuration identity
and validity, authority, policy, data use, residency, retention, risk, resource
reservation, provider state, exposure intent, and controlled time before any
bytes cross a provider boundary or spend begins. Cross-object equality,
interval ordering, candidate-count reconciliation, Pareto recomputation, and
registry membership remain deterministic semantic obligations; boolean fields
inside the record do not prove them.

No routing rule may name “the strongest model” without a pinned task family,
resource budget, evaluation evidence, validity window, data/risk boundary, and
declared multidimensional selection rule.

## Kernel invariants

The following are safety properties, not aspirational behaviors:

| ID | Invariant |
|---|---|
| COG-001 | A model, worker, planner, router, or verifier cannot append canonical domain events directly. |
| COG-002 | Every model input binds one exact ledger/checkpoint position, compiler profile, role, exposure ceiling, and omission manifest. |
| COG-003 | A command proposed from a view is revalidated against current authority, state, policy, data, and resource facts at admission. |
| COG-004 | Sealed evaluator truth and forbidden data cannot influence a producer view, retrieval candidate set, cache, summary, embedding, or derived feature. |
| COG-005 | Every material evidence item exposed for an epistemic transition receives one explicit retained disposition. |
| COG-006 | Contradiction, model incompleteness, blocked, invalid, unknown, and interval-crossing-zero states cannot be coerced into support, equivalence, zero, or success. |
| COG-007 | Debate, ranking, self-critique, and agent consensus cannot satisfy an evidence or independent-verification requirement. |
| COG-008 | Adaptive search and best-of-N selection retain all attempted candidates needed for selection and multiplicity accounting. |
| COG-009 | Candidate generation cannot consume verification reserve or admit claim-bearing work beyond its declared verification-capacity ceiling. |
| COG-010 | A worker output cannot alter its own work contract, evaluator, scorer, authority, budget, exposure, or success definition. |
| COG-011 | Provider/model fallback is a new attempt with new identity; it cannot silently continue a confirmatory run. |
| COG-012 | Private chain-of-thought, self-reported confidence, and generated tool logs are never proof. |
| COG-013 | Context loss, worker death, or model replacement cannot lose canonical scientific state or duplicate a settled effect. |
| COG-014 | Cross-mission memory promotion requires evidence, applicability, independence, and contamination review; similarity alone cannot transfer a rule. |
| COG-015 | Claim eligibility is a pure consequence of frozen protocol, admitted evidence, verifier results, and adjudication—not model identity or narrative quality. |
| COG-016 | No model/tool/provider dispatch, data exposure, or spend begins from a WorkIntent, assignment commit, or WorkContract alone; a current dispatch-claim transaction rechecks exact rights, exposure intent, provider configuration, authority, policy, budget, position, revocation, and expiry. |
| COG-017 | A ModelConfigurationRecord or RoutingDecision cannot authorize dispatch, establish verifier independence, or turn provider claims, unknown identity, or expired evaluation evidence into eligibility. |
| COG-018 | Routing retains the exact candidate partition and hard exclusions; selection requires complete current evidence and a Pareto-eligible candidate, while fallback creates a new decision and attempt. |
| COG-019 | A nonexistent epistemic aggregate is represented by proven absence and null state identity; no canonical version-0 graph, root, head, or origin event may be fabricated. |
| COG-020 | Proposed node lineage has no canonical supersession effect; only an admitted explicit supersession edge may supersede, and correction admission preserves non-resurrection and dependency fanout. |
| COG-021 | A transition proposes a graph delta if and only if it reports at least one typed change; edge-only, evidence-disposition-only, and contract-only changes do not require a fabricated hypothesis edit. |
| COG-022 | A constructible WorkContract is derived only after one exact canonical WorkIntent and one exact successful assignment cohort bind the worker, canonical lease, grants, data decisions, sandbox, reservation, and passing compilation bundle; dispatch rechecks those facts against current state and controlled time. |

## Verification backpressure

Generation is cheaper than verification. Odeya must prevent an attractive backlog of plausible but unverified artifacts from becoming de facto knowledge.

For each candidate class `r`, define a conservative verification demand vector

\[
d_r=(d_{\text{det}},d_{\text{compute}},d_{\text{expert}},d_{\text{physical}},d_{\text{safety}})
\]

and available reserved capacity over the admissible horizon

\[
V=(V_{\text{det}},V_{\text{compute}},V_{\text{expert}},V_{\text{physical}},V_{\text{safety}}).
\]

Admission of new claim-bearing generation requires a declared packing rule showing that outstanding demand plus `d_r` fits each required capacity dimension. Unknown demand fails closed for confirmatory or high-consequence work. Estimates remain estimates; actual verification observations reconcile them.

This is not a universal scalar “trust budget.” Dimensions cannot compensate for each other: abundant compute cannot replace an absent domain expert, physical test, or safety case. Exploratory candidates may be retained beyond claim-bearing capacity only in a quarantined, visibly unverified backlog with bounded storage and no promotion path until capacity is reserved.

The shared `resource_budget` reducer enforces this backpressure. Verification assignment and `resource.reservation_created` commit one exact cohort over the five coordinates; `verification.started` and `resource.reservation_claimed` commit the exact start cohort before any verifier receives work. Claim commits the full ceiling but does not invent actual use. Crash, recovery, cancellation after start, missing callback, or unavailable metering keeps the ceiling held. Only exact `resource.usage_observed` evidence followed by `resource.reservation_settled` can reconcile actual use and release unused capacity. Pre-start cancellation or controlled-time expiry may instead release/expire the active reservation. None of these resource facts establishes verifier independence or scientific confirmation.

## Observable epistemic-conduct evaluation

The process scorecard is derived from retained records and reported with uncertainty and denominator definitions:

- material-evidence disposition completeness;
- correct response to known refutations;
- preservation of live rival hypotheses and model-incomplete state;
- convergent use of genuinely independent tests;
- contradiction discovery and unresolved-contradiction retention;
- assumption/estimand revision when diagnostics require it;
- prospective versus post-selection separation;
- calibrated abstention and valid stop/escalation;
- contamination, sealed-truth, and narrative-to-verdict bypass rates;
- correction latency after adverse evidence.
- atomic-fact precision, recall, contradiction, and unsupported-fact rates under both ordinary and clean-room retrieval;
- resistance to false or pseudoscientific premises, including correct refusal before persuasive report generation;

These measures are diagnostic, not a reward to maximize blindly. Each receives adversarial anti-gaming cases, and outcome validity remains separate.

## Information-flow proof obligations

Gate A does not pretend that one access-control list proves noninterference. The candidate must define and test information flow across:

```text
canonical objects
  -> dependency traversal
  -> search/retrieval candidate construction
  -> ranking and summarization
  -> compiled view
  -> model/tool call
  -> caches, telemetry, checkpoints, and candidate artifacts
  -> verifier and public projection
```

At minimum, adversarial fixtures cover:

- sealed truth present in canonical state but absent from producer view and every derived retrieval artifact;
- forbidden datum influencing ranking even when redacted from final text;
- stale summary overriding a corrected source;
- contradictory evidence omitted because of context budget;
- omission manifest falsely claiming complete coverage;
- producer narrative leaking into a blinded verifier;
- verifier result routed back into an active confirmatory producer;
- shared cache crossing mission, role, purpose, or data-class boundaries;
- invalid source labeled irrelevant without applying the registered rule;
- one-byte view mutation with unchanged claimed digest;
- replay at the same checkpoint producing a different selected reference set under a supposedly deterministic compiler; and
- old readers ignoring a new exposure or epistemic-state enum.
- a reference-like answer or evaluator artifact reachable through search, cache, citation graph, or provider memory in the ordinary condition but blocked in the clean-room condition;
- a polished pseudoscientific premise that receives a compliant experiment/report instead of an evidence-class challenge or refusal;

Compilation evidence binds the exact dependency/input-set digest, search-index snapshot, cache namespace and snapshot, embedding/model identity where used, taint/visibility labels, contamination frontier, retrieval candidates, and derived summary identities. A receipt that merely asserts negative checks is not proof of noninterference. Gate A may model the declared information-flow safety property, but real provider/cache noninterference remains implementation and independent-test evidence.

The bounded control model should prove at least that no forbidden producer-visible state is reachable through declared transitions. Product implementations later require taint/information-flow tests and independently reproduced compiler vectors; the formal abstraction does not prove a provider's hidden behavior.

## Reducer and compatibility laws

Every cognitive aggregate has one pure reducer and one machine registry entry. Reducers:

- consume only ordered schema-valid events;
- reject unknown major versions and unknown safety-relevant enum values;
- never call models, tools, clocks, randomness, filesystems, or networks;
- preserve prior immutable versions and explicit supersession;
- make correction fanout monotone and replayable;
- treat indeterminate semantic-rule results as fail-closed for promotion; and
- reproduce the same state digest in at least two independently implemented trace runners before Gate A acceptance.

Schema compatibility alone is insufficient. A change to omission semantics, evidence disposition, graph relation meaning, independence axes, or selection accounting is semantic and requires a new contract version, migration vectors, and old-reader tests.

## First-slice acceptance

The Sentinel/Telos/Inbar composite fixture must demonstrate all of the following before this family is accepted:

1. the same sealed inputs compile to the same role view and omission manifest in two independent implementations;
2. a producer never receives the HUGSIM transfer verdict or evaluator truth before its frozen work is complete;
3. the positive Sentinel simulation result remains positive only in its pinned scope;
4. the transfer interval crossing zero compiles to `inconclusive`, never equivalence or null;
5. Telos invalid iterations remain invalid even when their outputs look strong;
6. the Telos repository-wide scan discrepancy remains an unresolved contradiction rather than being repaired by narrative;
7. Inbar's absent dossiers/hardware evidence produces blocked/refusal, never a confident physical diagnosis;
8. every exposed material result receives an epistemic disposition and correct consequence;
9. a known-bad compiler that omits contradictory evidence is rejected;
10. a known-bad planner that uses debate rank as evidence is rejected;
11. a known-bad worker that fabricates a tool receipt is rejected; and
12. a verifier with shared identity/corpus/implementation cannot be labeled independent.

## Gate A closure evidence

This contract family is not frozen until:

- exact closed schemas, fixtures, semantic rules, owner modules, command/event producers, reducers, and compatibility policies exist;
- the command/event/reducer graph is machine checked with no orphan discriminator;
- context compilation, epistemic transition, and verification-backpressure traces include positive and deliberately broken cases;
- the information-flow model and reducer traces pass in the pinned toolchain;
- a statistical/domain reviewer evaluates the process metrics and false-science cases;
- a security/privacy reviewer evaluates sealed truth, data purpose, caches, telemetry, and provider boundaries;
- a distributed-systems reviewer evaluates leases, retries, cancellation, replay, and correlation identity;
- the composite first slice passes at an immutable commit; and
- every critical/high finding is closed before Daniel receives an exact candidate for acceptance.

Gate A acceptance would mean the architecture is coherent and reviewable. It would not prove that the cognitive architecture outperforms a single model, produce a scientific discovery, authorize Gate C implementation, or justify a claim that Odeya is the world's best research engine.

## Dependency order

1. Freeze canonicalization, identity, authority, event, reducer, and data-purpose primitives.
2. Freeze this contract family and its semantic-rule registry.
3. Prove the bounded exposure/state-transition model and known-bad traces.
4. Compile one exact first-slice view in two independent reference paths.
5. Establish the one-model, flat-memory, deterministic-verification baseline.
6. Admit the epistemic graph only if it beats flat memory on contradiction retention and verified value per cost.
7. Admit specialists only where matched-budget evaluation beats the one-model baseline.
8. Admit adaptive/tree/evolution search only behind a red-teamed executable scorer and complete selection accounting.
9. Admit quantitative VOI only after calibrated probability, utility, dependency, cost, and harm evidence exists.
10. Admit cross-mission learning only after repeated independently verified missions and contamination-safe holdouts exist.

This order keeps Odeya ambitious without making unverified autonomy a founding dependency.
