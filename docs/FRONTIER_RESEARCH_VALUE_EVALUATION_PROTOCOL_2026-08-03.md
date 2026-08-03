# Frontier Research Value Evaluation Protocol Candidate

Status: proposed architecture-only comparison and preregistration packet; not
operator accepted, not preregistered, not executed, and not evidence that
Odeya is implemented or superior.

Date: 2026-08-03, Asia/Jerusalem.

Decision link: [ADR 0110](decisions/0110-require-matched-budget-frontier-value-evidence-before-superiority-claims.md).

## Honest starting verdict

Odeya currently has a substantial architecture corpus and bounded evidence for
parts of its architecture-validation machinery. It has no engine runtime, no
completed research mission executed by an Odeya engine, no matched-budget
comparison with a current research system, and no prospective evidence of
improved expert outcomes. The repository therefore does **not** support the
claims that Odeya is a frontier, state-of-the-art, advanced, generally useful,
or superior research engine.

The architecture's potential differentiator is a hypothesis, not a result:

> A durable research kernel that combines prospective protocols, typed
> scientific state, selective parallel work, isolated execution, separately
> isolated verification, claim-level evidence, correction-preserving replay,
> and explicit authority may produce more trustworthy research value per
> bounded resource than a strong durable agent, a strong multi-agent research
> scaffold, or current expert practice.

This packet defines what would have to be frozen, measured, refused, and
independently reviewed before any bounded version of that hypothesis could be
supported.

## Frontier comparison boundary at 2026-08-03

The earlier [frontier review](FRONTIER_REVIEW_2026-07-15.md) remains a dated
architecture survey. Since that review, public product and evaluation evidence
has made Odeya's comparison burden stricter:

- [Claude Science](https://www.anthropic.com/news/claude-science-ai-workbench)
  publicly describes a beta scientific workbench with more than 60 scientific
  skills and connectors, local/SSH/HPC execution, auditable code and artifacts,
  session forks, and a reviewer agent. These are no longer differentiating
  claims by themselves.
- [GPT-Rosalind](https://openai.com/index/introducing-new-capabilities-to-gpt-rosalind/)
  and its scientific plugins publicly combine model specialization, sourced
  evidence, analysis execution, domain-native artifacts, and provenance.
  OpenAI reports results on LifeSciBench, GeneBench, MedChemBench, and a private
  lab-work benchmark; those vendor-reported results require independent
  replication before use as a comparator fact.
- [LifeSciBench](https://openai.com/index/introducing-life-sci-bench/),
  [GeneBench-Pro](https://openai.com/index/introducing-genebench-pro/),
  [FrontierScience](https://openai.com/index/frontierscience/), and
  [PaperBench](https://openai.com/index/paperbench/) move evaluation toward
  expert-authored work, ambiguity, artifacts, analysis-path revision, and
  replication. No one benchmark establishes general scientific capability.
- Anthropic reports that its multi-agent research system improved an internal
  breadth-oriented evaluation by `90.2%` over its named single-agent setup,
  while multi-agent runs used about `15x` the tokens of ordinary chat and token
  usage alone explained `80%` of variance in one BrowseComp analysis.
  [The report](https://www.anthropic.com/engineering/multi-agent-research-system)
  supports selective parallelism and makes unmatched-budget comparisons
  inadmissible.
- An OpenAI field report covering eight agent-assisted scientific-software
  projects says the agents accelerated scoped engineering work but could not
  reliably judge scientific validity; the strongest validation used exact
  parity, known answers, simulated data, statistical behavior, and expert
  stewardship. [Scientific computing in the age of agentic
  AI](https://openai.com/index/scientific-computing-agentic-ai/)
  therefore reinforces Odeya's verifier boundary but does not validate it.
- Benchmark validity is itself a first-class experimental subject. Anthropic
  documented web-enabled agents identifying and decrypting BrowseComp answers,
  including higher contamination incidence in its multi-agent configuration.
  [Eval awareness in
  BrowseComp](https://www.anthropic.com/engineering/eval-awareness-browsecomp)
  makes a static public holdout insufficient. OpenAI's audit estimated that
  roughly `30%` of SWE-Bench Pro tasks were broken, and Anthropic measured a
  six-percentage-point Terminal-Bench swing across infrastructure settings.
  [OpenAI benchmark audit](https://openai.com/index/separating-signal-from-noise-coding-evaluations/),
  [Anthropic infrastructure-noise
  study](https://www.anthropic.com/engineering/infrastructure-noise)
- [Thinking Machines Lab's deterministic-inference
  work](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)
  and [interaction-model
  research](https://thinkingmachines.ai/blog/interaction-models/) make
  reproducible inference and human collaboration explicit comparison axes;
  durable state alone is not enough.
- [Anthropic's containment report](https://www.anthropic.com/engineering/how-we-contain-claude)
  documents why model-layer approval is insufficient and why sandbox, VM,
  filesystem, credential, and egress boundaries must carry the blast-radius
  claim. Odeya must measure those boundaries rather than infer them from its
  policy prose.

SpaceX and Tesla are prospective engineering domains, not public
research-agent baselines. Tesla's public AI page describes open-loop,
closed-loop, simulation, and hardware-in-the-loop evaluation at fleet scale;
that is a useful evaluation pattern, not evidence about Odeya.
[Tesla AI and robotics](https://www.tesla.com/AI). A SpaceX flight report or
public Tesla page cannot stand in for a partner-approved aerospace or autonomy
task, safety case, retained telemetry, domain oracle, or independent expert
review. Company names must never be used as benchmark labels or borrowed
credibility.

## Claim classes and consequence rules

Every result is scoped to one frozen protocol, task population, system set,
date, and resource envelope. Results do not inherit upward.

Current-use eligibility for a frontier claim ends after `90` days or at the
first material release of a named comparator, whichever comes first. The
historical result is not rewritten, but `current_claim_eligible` becomes
`false` and any present-tense frontier claim is `blocked` until the result is
rerun or narrowed. A real-world-value claim remains bound to its prospective
workflow population and is likewise blocked from current reuse when the task,
team, authority, or tool regime changes materially.

A comparator release is material when any frozen system-identity member that
can affect a primary endpoint or critical boundary changes: model/provider
snapshot, system prompt or policy, tool/retrieval surface, memory or
concurrency topology, authority/safety behavior, context or output limits,
pricing/resource regime, or product availability. A development-only
equivalence study may preregister a narrower rule before holdout exposure;
otherwise an ambiguous release is material.

| Claim class | Minimum admissible evidence | Forbidden inference |
| --- | --- | --- |
| Architecture integrity | Exact-byte replay plus known-bad refusal on the declared architecture subject | Engine implementation, scientific validity, or user value |
| Component capability | Blinded held-out result against a named component baseline under comparable resources | Mission-level or domain-general capability |
| System capability | Preregistered matched-budget comparison on the declared task population with validated graders and uncertainty | Expert-team value, physical validity, or frontier status |
| Research-team value | Prospective randomized or counterbalanced expert workflow study with independently settled outcomes | General autonomy or transfer beyond admitted domains |
| Frontier result | Same-date comparison with the strongest accessible relevant systems, externally reviewed and reproduced on the exact task population | Unqualified “state of the art,” “best,” or “most advanced” |

The default disposition is `inconclusive`. A missing, withheld, unavailable,
invalid, or unmeasured value is never zero and never silently excluded. A
failed or contradicted hypothesis remains visible with the same prominence as
a supported one.

## Frozen evaluation unit

One evaluation unit is an exact tuple:

```text
(protocol, task population, split, systems, model identities, prompts,
 tools, corpus cutoff, infrastructure, budgets, seeds, stopping rules,
 graders, statistical plan, consequence table, exposure state)
```

Changing any member creates a new unit. A primary result from one unit cannot
silently repair, pool with, or replace another. A separately preregistered
replication or meta-analysis may synthesize multiple units only under an exact
cross-unit estimand, inclusion rule, heterogeneity model, and multiplicity
plan, while retaining every unit-level result and limitation.

Before outcomes are exposed, the protocol must bind:

1. one precise claim and its falsifier;
2. task inclusion, exclusion, stratification, and rights criteria;
3. public development, private validation, sealed outer holdout, transfer, and
   prospective-team partitions;
4. the complete system identities, including model/provider version, system
   prompts, harness, tools, retrieval sources, permissions, memory policy, and
   concurrency topology;
5. CPU, memory, accelerator, storage, network, token, wall-time, compute,
   monetary, and human-time budgets plus enforcement behavior;
6. randomization, seeds, repetitions, stopping, retry, timeout, missingness,
   failure, and exclusion rules;
7. exact graders, oracle precedence, grader-validation evidence, blinding,
   adjudication, and disagreement handling;
8. estimands, sample-size or precision rationale, uncertainty method,
   multiplicity control, noninferiority margins, minimum effect, and the
   complete consequence table;
9. contamination frontier, exposure ledger, clean-room transformation,
   canaries, invalidation and rotation rules; and
10. trace/artifact audit sampling, evidence retention, security, privacy,
    correction, and publication boundaries.

The existing `ProtocolSnapshot`, `MetricResult`, `StrategyCandidate`, and
`PromotionDecision` candidates provide parts of this vocabulary. They do not
yet constitute an accepted end-to-end evaluation-plan schema, enrolled
methods, a sealed task manifest, a validated grader, or execution evidence.
Capability, efficiency, integrity, and research-team value are separate
preregistered claim units with separate estimands. `PromotionDecision` governs
an internal strategy candidate; it cannot synthesize those units into a
product-value claim.

## Comparator ladder

No single comparator answers the whole question. Each frozen study must use
the applicable layers below.

The candidate arm register is:

| Arm | Required comparator |
| --- | --- |
| `D0` | Simple deterministic or non-agentic pipeline where an executable baseline exists |
| `H0` | Independent qualified human expert using ordinary deterministic tools |
| `P0` | Incumbent team workflow with its normal approved tool stack |
| `S0` | Strongest eligible single-agent configuration selected on development data |
| `M0` | Strongest eligible agentic, multi-agent, or science-workbench configuration selected before holdout exposure |
| `O0` | Exact Odeya candidate |
| `A*` | Frozen internal ablations used for mechanism attribution, never market leadership |

Omitting a plausible leading accessible comparator or choosing a comparator
after outcome exposure invalidates a frontier claim.

### Mechanism-controlled comparison

Use the same exact base model family, model snapshot, tool set, corpus, and
resource ceiling for:

- a single durable agent with no specialist delegation;
- a central-supervisor multi-agent configuration with bounded specialists;
- the proposed Odeya configuration; and
- ablations that remove claim-evidence compilation, independent verification,
  correction propagation, topology selection, or verification backpressure
  one at a time.

This layer estimates the contribution of the architecture rather than the
model. Equivalent token budgets alone are insufficient: actual wall time,
compute, money, tool calls, infrastructure failures, and human interventions
are retained and reported.

The initial candidate resource curve uses `0.5x`, `1x`, and `2x` the primary
envelope, whose absolute values are frozen from development-only pilots. Each
stochastic task/configuration/tier cell uses at least five preregistered trials
unless an accepted precision analysis requires more. Every attempt remains in
the record; there is no best-of-k selection. An `unknown` value on a dimension
claimed to be matched invalidates that matched-budget comparison.

The task, or team-task in the prospective study, is the unit of analysis.
Repeated seeds and retries are nested trials for variance and robustness; they
cannot inflate the independent task count, effective sample size, or degrees
of freedom.

### Current-product comparison

At protocol freeze, name the strongest accessible products relevant to the
task class, such as the then-current OpenAI deep-research/scientific workflow
and Anthropic research/scientific workbench. Run them in their documented
native configurations. Because model, provider, and infrastructure are not
controlled, report this as a product comparison, never as a causal estimate of
the Odeya architecture.

Unavailable, access-restricted, or nonexportable systems are named as
unmeasured. Marketing pages and vendor-reported scores are context, not
substitute results.

### Human and current-practice comparison

For real-world value, compare against the actual current workflow of qualified
researchers or engineers. Retain domain, seniority band, team size, tools,
time, task familiarity, compensation-cost method, and assistance received.
The expert baseline is not a single model-generated “gold answer.”

## Initial task strata

The first accepted protocol should be small enough for deep audit and broad
enough to expose the claimed mechanism. Candidate strata are:

1. **Evidence synthesis under conflict** — reach a bounded decision while
   retaining refutations, missing evidence, rival explanations, and exact
   citations.
2. **Executable computational analysis** — inspect artifacts, choose an
   analysis path, execute it, detect invalid inputs, and reproduce exact
   outputs or statistical properties.
3. **Research-software reproduction** — reproduce or extend one bounded
   result with environment, code, tests, and artifact equality available to a
   clean verifier.
4. **Engineering trade study** — evaluate a synthetic, public, or
   partner-authorized aerospace/autonomy design question using named
   assumptions, units, VVUQ, safety constraints, and an expert oracle; no
   vehicle, lab, or physical-control authority is included.
5. **Invalid-premise and correction cases** — challenge pseudoscientific,
   inadmissible, contaminated, or already-refuted premises and preserve a
   visible refusal, invalid result, null, or correction.
6. **Long-horizon fault cases** — survive context reset, worker loss, partial
   artifact, verifier disagreement, retry ambiguity, and late correction
   without losing or duplicating canonical consequences.

Public benchmarks can seed development cases only after task-level rights and
validity review. The sealed outer holdout must include post-cutoff or
prospectively authored cases that no evaluated system, retrieval index, cache,
prompt author, or scorer has received.

## Outcome and process measures

No opaque aggregate score may hide a failed dimension. Report at least:

- independently adjudicated task success and domain-validity rubric score;
- exact numeric, code, structural, artifact, and source correctness as
  separate rates;
- claim-to-evidence entailment precision, required-evidence coverage,
  unsupported-fact rate, contradiction rate, and source-role correctness;
- refutation response, premise challenge, abstention, correction, null, and
  invalid-result retention;
- calibration and selective risk across declared confidence/abstention bands;
- clean replay, cross-environment reproduction, recovery, duplicate
  consequence, and fault-attribution rates;
- unauthorized effect, self-approval, self-verification, credential, egress,
  spend, publication, and prompt/tool-injection outcomes;
- tokens, tool calls, wall time, compute, money, human minutes, reviewer
  disagreement, rework, and time to correction; and
- prospective decision quality, uncertainty reduction, avoided rework, and
  expert-rated usefulness for the declared real workflow.

Final outcome and observable epistemic conduct remain separate. A correct
answer reached by ignoring a known refutation is not evidence of a trustworthy
process. A well-documented process with a wrong outcome is not a valid claim.

## Candidate thresholds for operator and statistical review

These values are proposed decision defaults, not accepted thresholds and not
observations. An accountable statistical reviewer and the operator must accept,
reject, or amend them before task outcomes are visible.

### Capability route

- An observed absolute paired improvement of at least `5` percentage points
  over the strongest mechanism-controlled baseline on the preregistered
  primary validity endpoint.
- The two-sided `95%` confidence interval for that paired improvement must
  exclude zero in the favorable direction.
- Every preregistered critical task stratum must be noninferior within a
  candidate margin of `-5` percentage points and must not cross its harm or
  validity boundary.

### Efficiency route

- The primary validity endpoint must satisfy a preregistered noninferiority
  margin proposed at `-2` percentage points.
- Exactly one primary total-resource endpoint — money, wall time, or qualified
  human time — must be selected before exposure. Its preregistered ratio must
  have a `95%` confidence-interval upper bound below `0.80`; every other
  resource endpoint is secondary and must stay within its preregistered
  regression margin.

### Integrity floor for either route

- every consequential artifact must bind to the frozen manifest through a
  verified raw-byte SHA-256, retained byte count, and declared environment
  record; this is artifact binding, not canonical or product identity;
- candidate claim-to-evidence entailment precision of at least `99%` and
  required-evidence coverage of at least `95%`, each with uncertainty reported;
- `100%` refusal of the enumerated critical known-bad set and a separately
  reported false-refusal rate on safe controls;
- zero self-approval, self-verification, unauthorized consequential effect,
  duplicate consequential write, or hidden negative/corrected outcome in the
  evaluated trials; and
- adaptive prompt/tool-injection and contamination results reported as rates
  with uncertainty, never as the word “secure” or “safe.”

A small sample can establish deterministic integrity facts for its exact
fixtures. It cannot establish a low operational failure probability. Zero
observed failures must be accompanied by an interval or upper bound appropriate
to the sampling plan.

One primary route and resource tier must be frozen before exposure. Switching
between capability and efficiency routes, selecting a favorable resource tier,
or choosing among primary resource endpoints after outcomes are visible is
invalid. If more than one route or tier is confirmatory, the single frozen
hierarchy must gate them together with all primary endpoints and critical
strata. Confirmatory families use a frozen hierarchical or Holm-adjusted
familywise-error rule at candidate `alpha = 0.05`. Exact independent-task
sample size is frozen before enrollment for candidate `90%` power at the
applicable minimum effect, plus a preregistered attrition allowance; nested
seed trials do not satisfy that sample size. These values require accountable
statistical review; they are not universal constants.

### Additional frontier eligibility bar

A frontier claim requires more than the mechanism-controlled bar. On the same
frozen task population and date, `O0` must satisfy the preregistered capability
or efficiency route against every strongest accessible named product in `M0`,
without a critical-dimension regression. The complete comparator eligibility
search and any inaccessible systems must be retained before exposure. A
non-producer must then independently reproduce the exact qualifying result.
That reproduction must freeze an independence profile: a separately
accountable execution principal, fresh checkout and environment, separate
session/cache/memory/index state, no producer prompts or output artifacts, no
holdout truth or grader access beyond the reproduction role, and independent
metric recomputation from the manifest-bound raw submissions. Different agent
names, prompts, or processes on shared hidden state do not establish
independence.
Without both the same-date product comparison and independent reproduction,
the strongest eligible wording is “better than the tested named systems” on
the exact task, date, and budget—not “frontier.”

The candidate consequence rules are:

- mechanism-controlled bar plus prospective expert-outcome bar plus all
  integrity floors: bounded workflow-value evidence only;
- those bars plus the additional frontier eligibility bar: bounded frontier
  real-world-value evidence for the exact task, date, and budget;
- capability bar without prospective expert outcome: bounded capability or
  benchmark claim only;
- value or efficiency bar without the strongest current comparator: bounded
  workflow-value claim, never frontier;
- uncertainty interval crossing the rule: `inconclusive`;
- valid evidence clearly against the claim: `contradicted`;
- contamination, post-hoc selection, budget mismatch, invalid grader, or
  hidden attrition: `invalid`;
- missing rights, authority, expertise, or reserved verification capacity:
  `blocked`.

Scientific/evidence disposition, operational disposition, replication or
correction state, and current-claim eligibility are recorded on separate axes.
A material comparator change or end of the `90`-day window sets
`current_claim_eligible` to `false` and blocks present-tense reuse; it does not
change a historical `supported`, `contradicted`, `null`, `inconclusive`, or
`invalid` result into another scientific outcome.

## Prospective research-team value study

A frontier-value claim ultimately requires real team evidence, not only a
benchmark. The first study should use randomized assignment or a
counterbalanced crossover where carryover can be controlled. It must bind:

- qualified team inclusion criteria and conflict disclosures;
- tasks drawn from the team's real accepted work but frozen before assignment;
- current-practice and Odeya-assisted conditions with comparable authority,
  data, and external-tool access;
- blinded independent outcome adjudication where feasible;
- two blinded domain reviewers plus a conflict-resolving adjudicator for every
  consequential expert judgment;
- decision correctness or quality, material omissions, time, total cost,
  reviewer burden, correction/rework, and retained negative outcomes;
- learning, ordering, novelty, and carryover controls; and
- participant safety, privacy, publication, and withdrawal rules.

No SpaceX, Tesla, OpenAI, Anthropic, Thinking Machines Lab, or other company is
named as a participant, beneficiary, or validation partner without explicit
authorization and retained evidence. A synthetic aerospace task supports only
a synthetic aerospace-task claim.

## Contamination and evaluator isolation

The contamination contract must cover direct answers and every derivative
path: papers, web pages, issue trackers, repositories, benchmark packages,
model context, evaluator prompts, task-author notes, search-query traces,
embeddings, vector indexes, caches, summaries, memories, logs, and prior agent
outputs.

Minimum controls are:

- a time-stamped exposure ledger per principal and system component;
- sealed answer, rubric, and task partitions with recipient-specific access;
- ordinary-access and clean-room runs under one exact blocked-reference
  manifest;
- fresh, recipient-isolated process, session, cache, memory, retrieval-index,
  and working-directory state for every clean-room arm, with no ordinary-arm
  state reused regardless of execution order;
- canaries and audits for overblocking, underblocking, query-trace leakage,
  cache/index leakage, benchmark recognition, and answer-key search;
- grader identities and outputs withheld from producers until their immutable
  submissions settle;
- task rotation or prospective replacement after any contamination exposure;
  and
- retention of contaminated attempts as `invalid`, never silent deletion or
  conversion to failure.

Internet access that leaves query trails is part of the exposure model.
Blocking one URL or benchmark name does not establish clean-room isolation.

## Required known-bad protocol cases

Before a protocol can be accepted, its checker or accountable review must
demonstrate refusal of at least these singleton defects. IDs, dispositions,
and reason codes are stable candidate values:

| Known-bad ID | Singleton defect | Expected disposition | Required reason code |
| --- | --- | --- | --- |
| `G5-PROTO-KB-001` | strongest relevant baseline omitted | `invalid` | `comparator_set_incomplete` |
| `G5-PROTO-KB-002` | nominal tokens match while wall time, compute, money, or human authority differs without disclosure | `invalid` | `resource_match_false` |
| `G5-PROTO-KB-003` | base model differs in a mechanism-controlled comparison | `invalid` | `mechanism_model_mismatch` |
| `G5-PROTO-KB-004` | public or derivative answer exposed to a producer | `invalid` | `producer_answer_exposure` |
| `G5-PROTO-KB-005` | grader or adjudicator unblinded where blinding is required | `invalid` | `evaluator_blinding_broken` |
| `G5-PROTO-KB-006` | unvalidated model judge replaces an available deterministic or expert oracle | `invalid` | `oracle_precedence_violated` |
| `G5-PROTO-KB-007` | missing, withheld, invalid, or unavailable data encoded as zero | `invalid` | `missingness_encoded_as_zero` |
| `G5-PROTO-KB-008` | post-outcome task exclusion, metric, threshold, or stopping change | `invalid` | `post_exposure_protocol_change` |
| `G5-PROTO-KB-009` | failed, timed-out, abstained, invalid, null, contradicted, or corrected attempt omitted | `invalid` | `attempt_or_outcome_hidden` |
| `G5-PROTO-KB-010` | favorable seed or resource point presented as the system result | `invalid` | `favorable_trial_selection` |
| `G5-PROTO-KB-011` | infrastructure, tool, retrieval, or evaluator drifts inside one comparison | `invalid` | `comparison_environment_drift` |
| `G5-PROTO-KB-012` | composite score hides a critical authority, integrity, or validity regression | `invalid` | `critical_dimension_hidden` |
| `G5-PROTO-KB-013` | producer acts as consequential verifier, adjudicator, or approver | `invalid` | `producer_self_verification` |
| `G5-PROTO-KB-014` | correct final answer with ignored material refutation presented as valid conduct | `invalid` | `material_refutation_ignored` |
| `G5-PROTO-KB-015` | vendor or inaccessible product score presented as Odeya's reproduced baseline | `invalid` | `baseline_not_reproduced` |
| `G5-PROTO-KB-016` | bounded task result generalized to a company, domain, or frontier claim | `invalid` | `claim_scope_escalated` |
| `G5-PROTO-KB-017` | unapproved proprietary, personal, export-controlled, or safety-sensitive data requested | `blocked` | `task_rights_or_safety_absent` |
| `G5-PROTO-KB-018` | unnecessary credential, publication, physical, or external-write authority requested | `blocked` | `evaluation_authority_exceeds_protocol` |
| `G5-PROTO-KB-019` | evaluated system can modify a contamination detector, grader, or known-bad set | `invalid` | `evaluator_boundary_mutable` |
| `G5-PROTO-KB-020` | negative result, correction, disagreement, exclusion, or overrun is less visible than a favorable outcome | `invalid` | `unfavorable_evidence_suppressed` |
| `G5-PROTO-KB-021` | nominal non-producer shares producer output, hidden state, holdout truth, grader access, or producer-computed metrics | `invalid` | `reproduction_independence_false` |
| `G5-PROTO-KB-022` | clean-room arm reuses ordinary-arm session, cache, memory, retrieval index, or working state | `invalid` | `clean_room_state_shared` |

The final accepted contract requires executable or independently retained
known-bad evidence. This prose list is a candidate inventory, not proof that a
gate fires.

## Evidence package required for a result

One result package must bind, at minimum:

- operator-reviewed, content-bound protocol snapshot and amendment history;
- task, rights, split, contamination, exposure, system, tool, model,
  infrastructure, resource, and grader manifests;
- manifest-bound submitted raw artifacts and independently recomputed metrics;
- per-trial outcome, process, cost, error, missingness, and exclusion records;
- transcript/artifact audit sample and discrepancies;
- statistical analysis and sensitivity results;
- independent domain, statistical, security/authority, and evaluation-validity
  review determinations; and
- separate fields for scientific/evidence disposition (`supported`,
  `contradicted`, `null`, `inconclusive`, or `invalid`), operational disposition
  when applicable (`running`, `blocked`, or `failed`), replication/correction
  state when applicable (`replicated`, `corrected`, or `retracted`), and
  `current_claim_eligible`; plus exact eligible and forbidden claim language.

Sensitive task truth and participant data remain recipient-scoped. Public
reporting may retain commitments and sanitized aggregates only when the
accepted protocol defines how an independent reviewer can verify them without
exposing restricted bytes.

## Gate effect and next decisions

This packet improves the specificity of the G0/G5 review surface. It does not
pass G0 or G5. The following remain required before the protocol is accepted:

1. operator selection of one first real-world wedge and intended decision;
2. accountable statistical and domain review of estimands, task population,
   thresholds, sample-size/precision plan, graders, and consequence rules;
3. task-level rights, privacy, safety, and contamination decisions;
4. exact evaluation-plan, task-manifest, exposure, grader, and result record
   contracts plus known-bad fixtures;
5. Gate A acceptance of the architecture baseline; and
6. separately authorized Gate C implementation and later execution evidence.

Until those decisions and later measurements exist, the only defensible claim
is:

> Odeya proposes an evidence-native architecture and a falsifiable protocol
> for testing whether that architecture improves bounded research outcomes.
> No comparative research-value result has been measured.
