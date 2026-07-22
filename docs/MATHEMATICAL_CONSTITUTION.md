# Mathematical Constitution

Status: proposed kernel semantics, 2026-07-15. No statistical method is admitted merely by appearing here; every method needs a versioned registry entry, assumptions, diagnostics, verifier, and conformance fixtures.

## First law: no universal confidence score

Odeya keeps separate mathematical currencies for:

- measurement and metrological uncertainty;
- sampling and parameter uncertainty;
- predictive distributions and calibration;
- inferential evidence against a specified hypothesis;
- causal identification and sensitivity;
- replication and transport;
- decision utility and harm;
- operational reliability;
- time, compute, money, and human cost.

None may be silently converted into another. A forecast probability is not a p-value; a p-value is not the probability a hypothesis is true; a posterior probability is conditional on its model and prior; an agent vote is none of these; a cryptographic signature establishes neither.

## Three levels

| Level | Frozen content |
|---|---|
| Engine constitution | Claim types, evidence semantics, separation rules, outcome states, authority, minimum controls |
| Mission seal | Estimand, endpoints, design, data roles, uncertainty regime, thresholds, stopping, multiplicity, budgets, verifier, claim consequences |
| Domain adapter | Valid domain method, measurement model, causal estimator, likelihood, safety rule, utility, specialist verifier |

A domain adapter can add stronger obligations but cannot weaken the constitution.

## Claim-type router

| Claim type | Minimum contract | Evidence that can support it | Forbidden shortcut |
|---|---|---|---|
| Descriptive | target population, sampling frame, unit, estimand | estimate plus sampling/design uncertainty | convenience sample generalized silently |
| Associational | exposure and outcome variables, adjustment set, temporal order, association measure | design-aligned association estimate with uncertainty and named adjustment scope | association phrased causally or absence inferred from a crossing interval |
| Predictive | target, horizon, information set, loss, split and shift scope | held-out/external proper score, calibration, uncertainty set | training score or model self-confidence |
| Causal | intervention, comparator, outcome, population, horizon, DAG/SCM, identification assumptions | randomized intervention or identified observational estimate with sensitivity analysis | correlation phrased causally |
| Equivalence | active comparator, prospectively frozen lower/upper margins, compatible design and two-sided interval rule | the complete method-valid interval lies inside both frozen margins | failure to reject, a small point estimate, or an interval crossing zero |
| Noninferiority | active comparator, prospective loss margin, benefit direction, one-sided compatible design | the correct one-sided bound clears the frozen margin | post-outcome margin choice or the wrong-sided bound |
| Safety | hazard, exposure denominator, operating domain, tolerated upper bound | upper risk bound, stress and negative controls, independent verification | zero observed failures called zero risk |
| Optimization | decision space, objective, constraints, baseline policy, feasibility and optimality rules | held-out feasible improvement under the exact constraint set | activity, search score, or infeasible objective gain called value |
| Physical validation | physical system/configuration/model, measurement plan, validation partition, discrepancy and acceptance rules | retained physical-world measurements with metrology and VVUQ provenance | simulation, calibration data, or code verification substituted for physical validation |

Atomic measurements remain typed evidence records rather than a tenth estimand
claim type. Agent comparison, value analysis, and evidence synthesis remain
important mission/domain profiles, but each output must compile into one or
more of the nine closed primitive claim types above. If a thesis cannot be
routed and operationalized, execution is refused or remains exploratory.

## Sealed statistical contract

Every confirmatory run freezes before affected outcome access:

- population, sampling unit, estimand, and effect scale;
- primary/secondary endpoints and smallest relevant effect or equivalence margin;
- sampling, allocation, randomization, blocking, and power/precision plan;
- model, transformations, estimator, and priors/sensitivity family if used;
- missing, exclusion, outlier, censoring, and protocol-deviation rules;
- multiplicity family and error criterion;
- fixed-horizon or sequential regime, stopping, futility, and adaptation;
- model-visible, calibration, test, transfer, and verifier-only data roles;
- baselines, ablations, negative controls, positive controls, and falsifiers;
- model, harness, tool, sandbox, infrastructure, and budget vector;
- causal identification assumptions where applicable;
- utility, cost, harm, and value horizon where applicable;
- verifier implementation, replication rule, and claim consequences.

Amendments are append-only and prospective. Exposure-aware logic determines whether a branch remains confirmatory.

## Proof-carrying result envelope

A result includes estimand, estimate, unit, interval type and level, evidence-measure type, uncertainty decomposition, assumptions, diagnostics, multiplicity and sequential accounting, data/code/method/harness/environment identities, actual resource use, deviations, independent recomputation, and eligible/forbidden claim language.

A bare number, score, or prose conclusion is not a scientific result object.

### Candidate machine-record topology and Gate A boundary

The existing mission, protocol, atomic metric, and claim records cover
important common fields, but they must not be stretched until loose strings or
a single atomic metric silently carry every claim type. The candidate adds
[`EstimandContract` 0.8.0](../schemas/estimand-contract.schema.json) and
[`ScientificResultEnvelope` 0.9.0](../schemas/scientific-result-envelope.schema.json).
Optional strict bindings were added to
[`ProtocolSnapshot` 0.9.0](../schemas/protocol-snapshot.schema.json) and
[`MetricResult` 0.8.0](../schemas/metric-result.schema.json), so their legacy
records remain structurally valid while legacy loose fields cannot become
estimand or claim authority. No missing `ResearchMissionSpec` or `ClaimVersion`
path alias was invented. The dependency order is:

```text
ResearchMissionSpec
  -> immutable claim-type-specific EstimandContract
  -> ProtocolSnapshot freezes estimand + design/accounting rules
  -> RunManifest + atomic MetricResult records
  -> immutable ScientificResultEnvelope composes the exact result set
  -> VerificationPackage + governed adjudication
  -> ClaimVersion compiles only the eligible scoped language
```

References are one-way. The estimand and protocol cannot reference later runs,
results, verification, adjudication, or claims. Atomic metrics do not declare a
scientific outcome. A result envelope cannot reference its later verification,
adjudication, claim version, or publication event. Those later records bind the
result's externally issued immutable identity.

The estimand contract uses the closed discriminator `descriptive`,
`associational`, `predictive`, `causal`, `equivalence`, `noninferiority`,
`safety`, `optimization`, or `physical_validation`. Every branch fixes the
exact population, unit of analysis, exposure, comparator, outcome, time
horizon, intercurrent-event strategy, summary functional, contrast, and effect
scale, plus branch-specific elements:

| Claim branch | Irreducible typed content |
|---|---|
| Descriptive | target population, sampling frame/design, variable and summary functional |
| Associational | exposure/outcome variables, association measure, adjustment set and temporal ordering |
| Predictive | target, horizon, information set, loss, split/shift/calibration scope |
| Causal | intervention policy, comparator, outcome, population, horizon, intercurrent-event strategy, graph/SCM and identification argument |
| Equivalence | lower/upper margins, rationale, compatible design, test method and prospective freeze |
| Noninferiority | positive loss margin, benefit direction, rationale, compatible one-sided design and prospective freeze |
| Safety | hazard, exposure denominator, operating domain, risk functional, tolerated upper bound, stress and negative controls |
| Optimization | decision space, objective, constraint set, baseline policy, optimality criterion and feasibility rule |
| Physical validation | physical system and asset configuration, physical model, measurement/validation partitions, discrepancy and acceptance rules |

The result envelope retains completed, incomplete, invalid, indeterminate,
inconclusive, and blocked paths without manufacturing an estimate. A measured path binds exact
decimal/distribution representations, registered units, interval or set
semantics, evidence-measure semantics, uncertainty components and correlation,
diagnostics, controls, data roles, contamination assessment, sequential and
multiplicity accounting, deviations, actual configuration/resources, and
recomputation evidence. `unknown`, `unavailable`, and `withheld` remain typed
states and cannot carry a numeric zero.

Deterministic semantic validation must additionally establish:

- interval/set bounds, levels, sidedness, units, and simultaneous/time-uniform
  scope are internally and method-registry consistent;
- a fixed-horizon evidence measure is not reused after unprotected peeking, and
  a sequential result binds the exact process/look/stopping record;
- every selected or arriving hypothesis is assigned exactly once to its frozen
  multiplicity family and accounting state;
- calibration, test, transfer, verifier-only, and physical-validation evidence
  partitions do not overlap beyond an explicitly admitted dependency model;
- an interval crossing the directional null cannot satisfy a directional claim
  under an interval-based rule, and is never renamed a “null result”;
- equivalence requires a prospectively frozen margin and a method-valid result
  inside it; failure to reject, a small point estimate, or an interval merely
  crossing zero is not equivalence;
- p-values, e-values, confidence intervals/sequences, posterior probabilities,
  Bayes factors, predictive distributions, calibration scores, risk bounds,
  and utility estimates retain their distinct interpretations;
- comparison and value results bind the complete configuration/resource vector
  and cannot hide unequal budgets or convert activity into value;
- eligible and forbidden language is derived from the exact frozen consequence
  rule, verification package, and adjudication, never copied from a producer;
  and
- the result/claim path has no self digest, successor digest, or circular
  result-verification-claim identity.

Sentinel's HUGSIM transfer interval that crosses zero is a mandatory known-bad
vector: the machine path must retain it as inconclusive for the directional
claim under that frozen rule and must reject mutations labeling it `null`,
`equivalent`, zero effect, or supported improvement. This one case is necessary
but not sufficient evidence for the broader mathematical contract.

The candidate enforces exact decimal strings and fixed UTC timestamps with six
fractional digits. Its isolated suite currently passes **57 cases**: **38**
structurally valid, **19** structurally invalid, and **38** with bounded local
semantic expectations. The vectors cover all nine estimand branches, exact
mission/estimand/protocol/run/metric identity, typed unknowns, interval
ordering and null inclusion, equivalence and noninferiority margins,
multiplicity, missingness, fixed-horizon peeking, recomputation, and physical
provenance. These checks do not establish registry admission, digest/reference
resolution, method validity, scientific truth, physical validity, claim
authority, or Gate A acceptance.

Remaining work is explicit: enroll both schemas and compatibility bindings in
the governed registry/manifest; define migration from the retained legacy
mission and claim shapes; resolve cross-record identities and unit/method
records against retained bytes; add reducers, replay and runtime integration;
extend property-based and independent recomputation vectors; and obtain
accountable independent statistical and physical-science review.

## Prediction and calibration

For binary forecast `P` and outcome `Y`, calibration means:

\[
\Pr(Y=1\mid P=p)=p.
\]

Use strictly proper scoring rules. Common losses are:

\[
\mathrm{Brier}=\frac{1}{n}\sum_i(p_i-y_i)^2,
\]

\[
\mathrm{LogLoss}=-\frac{1}{n}\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)].
\]

Report calibration and sharpness/discrimination separately. Expected calibration error is insufficient alone because bins and sample size materially affect it. Evaluate temporal, subgroup, and shift calibration within the declared scope.

Under exchangeability, split conformal prediction can guarantee marginal coverage:

\[
\Pr\{Y_{n+1}\in C_\alpha(X_{n+1})\}\ge 1-\alpha.
\]

This is not automatic conditional coverage and does not survive arbitrary shift, contaminated splits, or adaptive calibration reuse. The claim compiler preserves these limits.

## Fixed and sequential inference

Type-I error and power are operating characteristics:

\[
\alpha=\Pr(\text{reject }H_0\mid H_0),\qquad
1-\beta=\Pr(\text{reject }H_0\mid\theta=\theta^*).
\]

A p-value is not `Pr(H0 | data)`. Failure to reject is not equivalence. Equivalence requires a frozen practically irrelevant region and a design valid for that question.

For anytime-valid inference, an e-value satisfies:

\[
E\ge0,\qquad \sup_{P\in H_0}\mathbb E_P[E]\le1.
\]

For a valid e-process `E_t`, Ville's inequality gives:

\[
\Pr_{H_0}\left(\sup_t E_t\ge\frac{1}{\alpha}\right)\le\alpha.
\]

A confidence sequence satisfies simultaneous coverage over time:

\[
\inf_\theta\Pr_\theta\{\forall t,\theta\in C_t\}\ge1-\alpha.
\]

Therefore fixed-horizon p-values cannot be reused after unplanned peeking. Adaptive missions need preregistered group-sequential/alpha-spending methods, confidence sequences, e-processes, or another method with a proved adaptive guarantee. Operational safety stops and statistical stops remain separate events.

Bayesian updating is supported:

\[
p(\theta\mid D)\propto p(D\mid\theta)p(\theta),
\]

but priors, likelihood, decision loss, and sensitivity are sealed. Posterior coherence does not prove model adequacy, causal identification, calibration, or freedom from selection bias.

## Multiple testing and selection

With false rejections `V` and total rejections `R`:

\[
\mathrm{FWER}=\Pr(V\ge1),\qquad
\mathrm{FDR}=\mathbb E\left[\frac{V}{\max(R,1)}\right].
\]

Default policy:

- confirmatory primary families use strong family-wise control, ordinarily Holm or justified gatekeeping;
- exploratory families may use false-discovery control with dependency assumptions declared;
- BH requires independence or justified positive dependence; arbitrary dependence needs BY, valid resampling, or genuine e-value methods;
- arriving hypotheses need a registered online-FDR method whose assumptions hold;
- continuous monitoring uses an anytime-valid layer.

The family, ordering, reuse, and selection mechanism are frozen and ledgered. Correlated evidence is not double-counted.

## Causal identification

Prediction, association, intervention, and causation are different claim types. A basic causal estimand is:

\[
\mathrm{ATE}=\mathbb E[Y(1)-Y(0)].
\]

Every causal contract names population, intervention, comparator, outcome, horizon, summary, and intercurrent-event strategy. It includes a target-trial protocol or experimental design, causal graph/structural model, identification argument, consistency, exchangeability/randomization, positivity, interference, measurement and missingness assumptions, aligned estimator, overlap/balance diagnostics, negative controls/placebos, and sensitivity analysis.

Observational output is “causal conditional on named assumptions.” Simulation agreement is not physical intervention evidence.

## Information gain and decision value

For design `d`, expected information gain can be written:

\[
\mathrm{EIG}(d)=
\mathbb E_{Y\mid d}
\left[D_{KL}\big(p(\theta\mid Y,d)\Vert p(\theta)\big)\right]
=I(\Theta;Y\mid d).
\]

Information is not value. For action utility `U(a, θ)`:

\[
V_0=\max_a\mathbb E_\theta[U(a,\theta)],
\]

\[
\mathrm{EVSI}(d)=
\mathbb E_{Y\mid d}\left[\max_a\mathbb E_{\theta\mid Y,d}[U(a,\theta)]\right]-V_0.
\]

Net expected value of information is:

\[
\mathrm{NEVI}(d)=\mathrm{EVSI}(d)-C_{direct}(d)-C_{opportunity}(d)-\mathbb E[H(d)].
\]

Utility and harm weights are authority decisions, not facts discovered by an agent. EIG, EVSI, feasibility, safety, strategic fit, cost, and epistemic diversity remain a visible vector. Portfolio selection uses an explicit sensitivity-tested rule over the Pareto frontier, not one hidden reward.

For held-out unit `i`, incremental net benefit can be defined:

\[
B_i=U_i^{Odeya}-U_i^{baseline}
-(C_i^{Odeya}-C_i^{baseline})-H_i.
\]

A public positive-value claim requires a preregistered method whose 95% lower confidence bound for expected incremental net benefit is above zero on held-out or independently replicated units, with no violated primary safety boundary.

## Replication and synthesis

Reproducibility means recomputation from the same evidence and code. Replication means new data diagnostic of the original claim regardless of direction. Do not store one unqualified replication boolean.

For study `j`, a basic hierarchical synthesis is:

\[
\hat\theta_j\mid\theta_j\sim N(\theta_j,s_j^2),\qquad
\theta_j\sim N(\mu,\tau^2).
\]

Report the pooled effect with uncertainty, heterogeneity `τ`, and predictive distribution for a new context. Model or disclose shared datasets, dependent estimates, missing evidence, small-study effects, and transport limits.

## Resource-aware agent evaluation

The evaluated configuration is the whole system:

\[
c=(model,harness,tools,context,sandbox,infrastructure),
\]

under budget vector:

\[
b=(tokens,calls,turns,wall\ time,money,retries,parallelism).
\]

Estimate a capability surface, not a leaderboard scalar:

\[
p_c(t,b)=\Pr(\text{externally verified success on task }t\mid c,b).
\]

Use paired tasks and environments, cluster uncertainty by task, and model task/infrastructure heterogeneity. Under independent identical attempts only:

\[
pass@k=1-(1-p)^k,\qquad pass^k=p^k.
\]

Actual attempts are often correlated, so bundled reliability is measured empirically. Report success-budget curve, repeat consistency, verified quality, latency, total cost, cost per verified success, safety-event upper bound and exposure, and recovery within a fixed total budget. Zero observed safety events never means zero risk.

## Resource reservation algebra

Let `D` be a closed basis of registered dimensions:

\[
D=D_{execution}\;\dot\cup\;D_{money}\;\dot\cup\;
\{v_{det},v_{compute},v_{expert},v_{physical},v_{safety}\}.
\]

Each currency is a distinct money basis element measured in minor units. A resource vector is an element of \(\mathbb R_{\ge0}^{D}\) with unique dimension keys. Admission is componentwise. If estimate \(e\), ceiling \(c\), and available capacity \(a\) describe a proposed reservation, then

\[
0\le e_d\le c_d\le a_d\quad\forall d\in D.
\]

No conversion matrix, exchange rate, scalar score, or surplus in one coordinate may establish feasibility in another. In particular, \(c_d>a_d\) is a rejection even when \(\sum_j c_j\le\sum_j a_j\); those sums are generally dimensionally meaningless.

Reservation creation moves \(c\) from available capacity to an active hold. Claim moves the same \(c\) from active hold to claimed hold without changing total held capacity and without assigning an actual-use value. A pre-claim release or expiry returns exactly \(c\). After claim, crash/recovery preserves \(c\) until retained observations permit settlement.

For settlement, let \(n\) be net use, \(q\) the ceiling-backed consumed vector, \(o\) overage, and \(u\) unused capacity. Componentwise:

\[
n=q+o,\qquad c=q+u,
\]

with all vectors non-negative. For money, \(n=billed-refunded\) and \(0\le refunded\le billed\); for non-money resources, \(n=actual\). Settlement returns only \(u\), retains \(q\) as consumed, and records \(o\) as an explicit breach/liability. Missing or unavailable usage is an epistemic state, not the numeric vector zero, so it cannot satisfy these equations or release a claimed hold.

## Verification-capacity constraint

Generation and verification are different resources. For a candidate class `r`, retain a conservative demand vector

\[
d_r=(d_{\mathrm{det}},d_{\mathrm{compute}},d_{\mathrm{expert}},d_{\mathrm{physical}},d_{\mathrm{safety}})
\]

and compare outstanding demand with separately reserved capacity in the same dimensions. Claim-bearing admission requires every required dimension to remain feasible under the registered packing rule. The vector is intentionally not reduced to one scalar: compute cannot substitute for absent domain expertise, a physical test, or a safety case. Unknown demand fails closed for confirmatory and high-consequence work.

Estimates and actual use remain separate and are reconciled. Verification assignment atomically creates the exact five-dimensional reservation, `verification.started` claims the same vector with the complete start cohort, and settlement requires exact retained observations in that basis. A missing required coordinate cannot be marked optional after outcome exposure or compensated by another coordinate. Exploratory overflow may be retained only as a bounded quarantined backlog with no claim, memory-promotion, or publication authority. The complete control contract is in [Cognitive Control Contracts](COGNITIVE_CONTROL_CONTRACTS.md).

## Claim progression without axis collapse

```text
ClaimProposal
  -> protocol admissibility and prospective freeze
  -> run validity + measurement disposition
  -> Adjudication(determined scientific outcome | refused with reason)
  -> VerificationRun(s) with observed independence
  -> ClaimVersion(ineligible | eligible within exact scope)

separate prospective branches:
  replication · transport · value validation

separate publication aggregate:
  request · authorization · sealed manifest · external settlement
```

`true`, `solved`, `safe`, `replicated`, `transported`, and `value_demonstrated` are not generic claim-lifecycle states. Each later assertion requires its own typed mission and evidence. Correction and retraction are append-only claim versions and events; they do not rewrite the earlier outcome.

## Statistical method registry

Each admitted method declares:

- stable identifier, implementation and verifier versions;
- claim and data types supported;
- formal guarantee and exact assumptions;
- required inputs and incompatible operations;
- diagnostics, sensitivity analyses, and failure states;
- fixed, simultaneous, or time-uniform interval semantics;
- multiplicity and adaptation behavior;
- numerical tolerances and reference implementation;
- synthetic-null, known-effect, dependence, leakage, optional-stopping, missingness, and broken-artifact conformance results.

Do not write custom statistical algorithms when mature audited libraries exist. Odeya owns the contract, evidence, authority, orchestration, verification, and learning semantics—not reinventions of numerical statistics.

The closed structural contract is [`method-registry` 0.7.0](../schemas/method-registry.schema.json). It deliberately distinguishes a proposed record from an admitted method. A structurally valid record remains unusable for claim-bearing work until its guarantee and assumptions are semantically reviewed, every applicable known-bad vector partition is populated, the required independent implementations agree under a frozen numerical profile, rights are settled, and an accountable admission decision is retained. A registry digest identifies those exact records; it is not an endorsement of every method it contains.

## Mathematical implementation dependency

Before runtime work:

1. freeze claim ontology, estimand schema, uncertainty types, result envelope, and progression states;
2. define the method-registry contract and simulation acceptance rule;
3. design synthetic nulls, known effects, dependence, leakage, optional-stopping, causal-confounding, and broken-verifier fixtures;
4. freeze data-role and sealed-truth authority;
5. admit descriptive, predictive-calibration, and paired agent-evaluation methods first;
6. require independent recomputation before autonomous execution;
7. add sequential and multiple-testing methods;
8. add causal methods only with explicit identification review;
9. add replication and synthesis;
10. add VOI portfolio allocation only after grounded outcome and cost data exist.

## Primary references

- [Strictly Proper Scoring Rules, Prediction, and Estimation](https://doi.org/10.1198/016214506000001437)
- [Probabilistic Forecasts, Calibration and Sharpness](https://doi.org/10.1111/j.1467-9868.2007.00587.x)
- [Conformal Prediction: A Gentle Introduction](https://doi.org/10.1561/2200000101)
- [Time-uniform confidence sequences](https://doi.org/10.1214/20-AOS1991)
- [Game-Theoretic Statistics and Safe Anytime-Valid Inference](https://doi.org/10.1214/23-STS894)
- [Benjamini–Hochberg false-discovery control](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)
- [False Discovery Rate Control with E-values](https://doi.org/10.1111/rssb.12489)
- [Causal Inference: What If](https://www.hsph.harvard.edu/miguel-hernan/wp-content/uploads/sites/1268/2024/04/hernanrobins_WhatIf_26apr24.pdf)
- [ICH E9(R1) estimands and sensitivity](https://www.ema.europa.eu/en/ich-e9-statistical-principles-clinical-trials-scientific-guideline)
- [NIST: Value of Information and Decision Pathways](https://www.nist.gov/publications/value-information-and-decision-pathways-concepts-and-case-studies)
- [What Is Replication?](https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.3000691)
- [Cochrane Handbook, Chapter 10](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-10)
- [BIPM/JCGM measurement guides](https://www.bipm.org/en/web/guest/publications/guides)
- [ASME verification, validation, and uncertainty quantification](https://www.asme.org/codes-standards/publications-information/verification-validation-uncertainty)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [UK AISI: Test-time compute in agent evaluations](https://www.aisi.gov.uk/blog/more-compute-more-capability-why-ai-agent-evals-need-to-account-for-test-time-compute)
