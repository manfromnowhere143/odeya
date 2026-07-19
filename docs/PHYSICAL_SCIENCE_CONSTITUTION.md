# Physical Science Constitution

Status: proposed kernel and adapter contract, 2026-07-15.

Odeya's physical-science layer is a proof-carrying inference system—not a simulator wrapper and not an LLM narrating engineering confidence.

```text
raw signal
  -> calibrated measurement
  -> state estimate
  -> model inference
  -> mechanistic/causal claim
  -> control recommendation
  -> separately authorized action
  -> independently measured outcome
```

These objects never collapse:

- simulation is not observation;
- parameter calibration is not validation;
- code correctness is not solution convergence;
- numerical convergence is not physical validation;
- predictive fit is not causation;
- recommendation is not actuator authority;
- zero observed failure is not zero risk;
- “validated” is always scoped to quantity, configuration, context, horizon, decision, and tolerance.

## Three levels

| Level | Responsibility |
|---|---|
| Physical kernel | Quantity algebra, units, frames, time, provenance, uncertainty types, evidence semantics, claim gates, invalidation, authority separation |
| Mission seal | Quantities of interest, context/ODD, decision, consequence, tolerances, experiments, evidence independence, applicable standards |
| Domain adapter | Equations, constitutive laws, solver, sensor/calibration model, frames, state estimator, experiment templates, hazard ontology, safety envelope, standards crosswalk |

A domain adapter cannot weaken measurement traceability or reinterpret calibration as validation.

Statistical, measurement, uncertainty-propagation, numerical-verification, physical-validation, identification, and control-safety procedures enter through the same closed [`MethodRegistry`](../schemas/method-registry.schema.json) contract. Domain adapters may narrow an admitted method's applicability but cannot widen its guarantee, omit its assumptions, replace an indeterminate result with a pass, or treat a proposed registry record as admitted.

## Machine contract closure candidate

The prose constitution now has an isolated, acyclic eight-schema candidate family:

1. [`PhysicalQuantity`](../schemas/physical-quantity.schema.json) has no physical-record dependency.
2. [`UncertaintyBudget`](../schemas/uncertainty-budget.schema.json) and [`AssetConfigurationSnapshot`](../schemas/asset-configuration-snapshot.schema.json) depend only on physical quantities.
3. [`PhysicalMeasurementResult`](../schemas/physical-measurement-result.schema.json) depends on quantities, an uncertainty budget, and the effective asset snapshot.
4. [`PhysicalModelRecord`](../schemas/physical-model-record.schema.json) depends on quantities, asset snapshots, and physical measurements.
5. [`PhysicalEvidenceVector`](../schemas/physical-evidence-vector.schema.json) depends on the model, asset snapshots, and measurements.
6. [`SafetyEnvelope`](../schemas/safety-envelope.schema.json) depends on quantities, the asset, model, and evidence vector.
7. [`PhysicalExperimentContract`](../schemas/physical-experiment-contract.schema.json) depends on quantities, the asset, model, evidence vector, and safety envelope.

The schemas close record shape and fail-closed alternatives: exact decimal or distribution reference; a registered unit binding with all seven SI base dimensions and semantic kind; fixed UTC-microsecond timestamps; affine/logarithmic conversion separation; conditional frame/time/spatial support; Type A/Type B evaluation origin distinct from aleatory/epistemic nature; covariance, correlation, calibration, raw-signal, instrument, firmware, environment, configuration, discrepancy, partition, VVUQ, preflight, and safety-boundary evidence. Exact decimals reject binary numbers, negative zero, exponent notation, and leading zeros while preserving legitimate negative nonzero values.

The evidence record contains exactly ten non-collapsible credibility components and P0–P12. Physical validation requires independent physical-world measurement identities; calibration, simulation, code verification, and numerical convergence cannot substitute. The experiment and safety contracts emit proposals or recommendations only and cannot issue execution or actuator authority. Missing or unknown hardware forces a blocked, refused, or indeterminate disposition; zero observed components remains an observation, never success.

The isolated checker at [`tests/physical-contracts`](../tests/physical-contracts/README.md) passes 95 structural expectations, 42 bounded local-semantic expectations, and a nine-schema dependency-DAG check over the eight physical schemas plus the generic verification-package schema. It pins and validates one exact fixture per physical schema; the Inbar fixtures preserve a valid measured result, an unknown-hardware asset block, and an experiment refusal. The additional synthetic verification fixture resolves exactly one typed `PhysicalEvidenceVector`, derives IV4, physical, and safety applicability from the joined evidence, and proves the former “No physical-world assertion” false positive is refused. It is architecture evidence, not a physical-world result. These checks do not resolve the unit/method registries, prove dimensional or frame-transform algebra, prove covariance positive semidefiniteness or propagation, reconcile general cross-record digests and effective times, execute reducers/traces, establish physical-world validity, or constitute metrology, VVUQ, safety, or accountable domain review.

## Quantity and frame kernel

No physical scalar enters Odeya as a bare number:

```text
PhysicalQuantity {
  quantity_kind
  exact decimal value or distribution reference
  unit and exact dimension vector
  semantic_kind
  reference_frame and coordinate convention
  timestamp, clock, and time scale
  spatial support
  uncertainty model and covariance group
  calibration chain
  provenance
}
```

Invariants:

- SI is the internal base; conversions are explicit retained transformations.
- Unit equality is insufficient: angle, strain, count, solid angle, and ratio can all be dimensionless and still incompatible.
- Absolute temperature and temperature interval are different types.
- Affine and logarithmic units cannot use ordinary multiplicative conversion.
- Frame, origin, axes, handedness, epoch, and time scale are mandatory when relevant.
- Transform uncertainty and cross-correlation propagate.
- Values sharing a calibration or systematic source remain correlated.

For `z = g(x)`, first-order covariance propagation is:

\[
\Sigma_z \approx J_g\Sigma_xJ_g^\top.
\]

For nonlinear, discontinuous, or non-Gaussian models, use an admitted numerical distribution-propagation method rather than silent linearization. Type A/Type B measurement evaluation must not be relabeled aleatory/epistemic uncertainty.

The [NASA Mars Climate Orbiter lesson](https://llis.nasa.gov/lesson/641) is the interface archetype: unit/frame mismatches must become unrepresentable contract violations.

## Measurement ledger

A measurement result requires:

- exact measurand definition;
- raw signal digest and acquisition procedure;
- instrument, firmware, range, and configuration;
- environmental conditions;
- calibration certificate and traceability chain;
- correction model;
- sampling, filtering, latency, synchronization, and time base;
- estimate plus uncertainty distribution/covariance and coverage method;
- saturation, clipping, aliasing, dropout, and validity indicators;
- operator and transformation provenance.

Traceability is an unbroken documented calibration chain with uncertainty contributions—not a boolean named `calibrated`.

## Asset and configuration ledger

Every physical result binds to an immutable effective-time snapshot:

```text
AssetSnapshot {
  asset identity
  geometry, material, and topology
  hardware serials
  software and firmware
  boundary and initial conditions
  maintenance, damage, and modification state
  sensor topology and calibration state
  effective interval
  configuration digest
}
```

Geometry, material, topology, firmware, maintenance, damage, sensor, or calibration change invalidates dependent applicability until re-established.

## Model ledger

```text
PhysicalModel {
  conceptual model
  equations and code
  numerical method
  parameters and priors
  initial/boundary conditions
  quantities of interest
  context of use
  assumptions, exclusions, and discrepancy model
  solver tolerances
  code/environment/dependency identities
  verification evidence
  calibration partition
  validation partition
}
```

The conceptual model and omitted physics are first-class evidence. A container image alone is not a credible physical model.

## Physical evidence vector

Never compress physical credibility into one confidence score. Adjudicate a vector:

\[
C=(V_{code},V_{solution},M_{trace},I_{ident},C_{cal},V_{physical},UQ,A_{app},C_{causal},S_{safety}).
\]

Each component is `pass`, `fail`, `indeterminate`, or `not_applicable` with scope, evidence, assumptions, and verifier identity.

Eligible language remains narrow:

- computationally verified;
- calibrated on named evidence;
- physically validated for quantity `Q` in context `D`;
- causally supported for intervention `I` under named assumptions;
- recommendation inside envelope `S`;
- authorized for bounded execution only through a separate authority service.

## Dynamics and hybrid systems

The common adapter contract supports stochastic and hybrid dynamics:

\[
x_{k+1}=F_{m_k}(x_k,u_k,\theta,w_k),\qquad
y_k=H_{m_k}(x_k,\theta,v_k),
\]

with explicit mode `m`, disturbance `w`, measurement error `v`, and parameter vector `θ`.

For linear systems, preflight observability and controllability:

\[
\mathcal O=
\begin{bmatrix}C\\CA\\\vdots\\CA^{n-1}\end{bmatrix},
\quad \operatorname{rank}\mathcal O=n,
\]

\[
\mathcal C=
\begin{bmatrix}B&AB&\cdots&A^{n-1}B\end{bmatrix},
\quad \operatorname{rank}\mathcal C=n.
\]

Nonlinear local observability uses differentials of `h, L_f h, L_f^2 h, ...`; parameters may be augmented as constant states for structural-identifiability analysis. These local/generic results do not prove global observability or practical estimability. [Hermann–Krener](https://doi.org/10.1109/TAC.1977.1101601), [identifiability through observability](https://pmc.ncbi.nlm.nih.gov/articles/PMC5085250/)

Experiments require adequate excitation. A useful condition is:

\[
\sum_{k=1}^{N}\phi_k\phi_k^\top\succeq\alpha I.
\]

Fisher information for design `d` is:

\[
\mathcal I(\theta;d)=\sum_k J_k^\top R_k^{-1}J_k.
\]

Report rank, singular directions, and conditioning—not only a determinant. D-, A-, and E-optimality are domain methods chosen for the estimand. Structural non-identifiability is a stop condition; more optimization cannot recover what the experiment cannot distinguish.

## Inverse problems and discrepancy

A regularized estimator may be:

\[
\hat\theta=\arg\min_\theta
\|y-G(\theta)\|_{\Sigma^{-1}}^2+\lambda R(\theta).
\]

A probabilistic model should expose discrepancy:

\[
y(x)=G(x,\theta)+\delta(x)+\epsilon,
\]

\[
p(\theta,\delta\mid y)\propto
p(y\mid G(\theta)+\delta)p(\theta)p(\delta).
\]

Diagnose parameter/discrepancy confounding; otherwise parameters absorb missing physics and become nonphysical. Calibration and validation use independent evidence. [Kennedy–O'Hagan](https://doi.org/10.1111/1467-9868.00294), [Brynjarsdóttir–O'Hagan](https://doi.org/10.1088/0266-5611/30/11/114007), [Stuart on Bayesian inverse problems](https://doi.org/10.1017/S0962492910000061)

Closed-loop identification records controller and reference policies because input is generally correlated with output noise. Use valid closed-loop methods, instruments, or independent excitation; ordinary open-loop regression can be biased.

## Physical experiment contract

```text
PhysicalExperimentContract {
  hypothesis and rivals
  causal estimand or target quantity
  measurement-dependence falsifier and entailed-effect rule
  intervention policy
  randomization, controls, and blinding
  sensors and calibration
  sampling and synchronization
  excitation and identifiability
  asset/configuration/context
  expected information and decision value
  cost, reversibility, and harm
  robust safety envelope
  permissions and actuator boundary
  abort and stop conditions
  preregistered analysis
  independent validation partition
}
```

Before an effect may be classified as empirically measured, preregister a
measurement-dependence falsifier. Its blinded input set may contain only
prospectively frozen, pre-outcome design inputs whose dependency/taint graph
shows they are not descendants or proxies of the measurement or outcome.
Control metadata, labels, censoring indicators, and denominators are withheld
when the measurement or intervention can affect them.

An exact rounded-value or coarse-label match by the blinded computation is a
screening failure: it blocks empirical promotion and requires adjudication, but
one match alone does not prove definitional entailment. An empirical
interpretation becomes `invalid` for circularity only after an analytic
derivation or preregistered counterfactual/permutation dependency test shows
that the reported effect is invariant to admissible changes in the withheld
measurements or is computed from outcome descendants. Otherwise the result
remains `blocked` or `inconclusive`. A demonstrated identity may support an
implementation-correctness or analytic-identity claim, but it cannot count as
an independent physical measurement or empirical effect. The
measurement-dependent residual information and its provenance must be
reported.

Reject before ranking when the target is unobservable/non-identifiable, sensor
capability cannot resolve it, a measurement-blind match is unresolved or
circularity is demonstrated, excitation is inadequate, the causal effect is
unidentified, authority/safety cannot be met, or validation cannot remain
independent.

For interventions, distinguish:

\[
P(Y\mid U=u)\quad\text{from}\quad P(Y\mid do(U=u)).
\]

The causal bundle includes an SCM, graph assumptions, estimand, intervention fidelity and manipulation checks, confounding strategy, overlap, time ordering, feedback policy, and sensitivity. Under feedback, the intervention may be `do(π)`, not a static input. [Pearl's causal calculus](https://proceedings.mlr.press/r0/pearl95a.html)

## VVUQ claim gates

Model credibility is context- and decision-dependent. [NASA-STD-7009B](https://standards.nasa.gov/standard/nasa/nasa-std-7009) and the [ASME VVUQ portfolio](https://www.asme.org/codes-standards/vvuq-standards) are core references.

| Gate | Evidence | Hard rejection example |
|---|---|---|
| P0 decision/context | decision, QoI, configuration, ODD/context, horizon, consequence, model influence | “generally accurate” |
| P1 measurement | units, frames, traceable instruments, bandwidth, resolution, uncertainty, measurement-dependence falsifier | bare value, expired calibration, or effect entailed without observations |
| P2 conceptual adequacy | governing assumptions, omitted effects, discrepancy, conservation, boundaries | dominant mechanism absent |
| P3 observability/identifiability | structural and practical analysis, excitation | unidentifiable requested parameter |
| P4 code verification | analytic/manufactured solutions, regression, independent implementation where warranted | only training-data comparison |
| P5 solution verification | mesh/time-step/tolerance convergence and numerical-error estimate | one grid/solver setting |
| P6 calibration | declared fit data, priors, residuals, parameter/discrepancy diagnostics | fit called validation |
| P7 physical validation | independent measurements, measurement-dependent residual information, uncertainty-aware metrics, intended regime/QoI | simulation compared with simulation or a definitionally entailed effect relabeled measured |
| P8 uncertainty/sensitivity | measurement, input, parameter, numerical, model-form, scenario, implementation | independence assumed for convenience |
| P9 applicability | domain distance, interpolation/extrapolation, robustness, abstention | claim outside envelope |
| P10 causal | identified intervention effect or controlled experiment | prediction called mechanism |
| P11 safety/authority | hazard analysis, fallback/invariant evidence, independent safety case, grant | researcher directly actuates |
| P12 release | scoped wording, evidence vector, verifier, expiry/invalidation triggers | universal validated/safe badge |

Residual diagnostics such as `rᵀΣ⁻¹r` can contribute, but thresholds come from the mission's decision and loss—not a universal Odeya number.

## Safety and control boundary

The engine defaults to recommendation-only:

1. research controller proposes;
2. independent state/validity monitor evaluates;
3. deterministic safety kernel filters;
4. mission safety/execution authority approves;
5. actuator gateway enforces hard limits;
6. outcome is measured independently.

For safe set `S = {x : h(x) ≥ 0}`, a robust control-barrier condition can be:

\[
\inf_{w\in W}
[L_fh(x)+L_gh(x)u+L_wh(x)w+\alpha(h(x))]\ge0.
\]

A Lyapunov certificate may support stability when:

\[
V(x)>0,\qquad \dot V(x)\le-\alpha(\|x\|).
\]

These hold only within verified dynamics, disturbance set, actuator limits, latency, and state-estimation error. Infeasibility and saturation need explicit behavior. Chance constraints are not hard guarantees unless their probability model is justified. Reachability needs conservative numerical/UQ treatment. [Control barrier functions](https://arxiv.org/abs/1903.11199), [Hamilton–Jacobi reachability](https://arxiv.org/abs/1709.07523)

Learned autonomy should use runtime-assurance/Simplex separation: advanced controller, trusted fallback, independent monitor, verified switching horizon, and common-mode analysis. [NASA autonomous-systems verification](https://ntrs.nasa.gov/api/citations/20250003529/downloads/Verification%20of%20Autonomous%20Systems_2.pdf)

## Digital twins and sim-to-real

Internal maturity classes:

- M0 offline virtual model;
- M1 one-way digital shadow;
- M2 synchronized twin with persistent asset/configuration/state;
- M3 scoped recommendation twin;
- M4 closed loop, requiring a separate safety and authority case.

State estimation follows a declared filter, for example:

\[
p(x_k,\theta_k\mid y_{1:k},u_{1:k})
\propto p(y_k\mid x_k,\theta_k)
\int p(x_k\mid x_{k-1},u_{k-1},\theta_k)
p(x_{k-1},\theta_{k-1}\mid D_{1:k-1})dx.
\]

Kalman, ensemble, particle, and variational filters are adapters. The kernel requires innovation logs, consistency diagnostics, age-of-information, and uncertainty inflation under staleness.

A twin degrades when configuration/firmware/calibration diverges, clock/latency exceeds contract, innovations drift, scope is exceeded, observability is lost, or a model/surrogate changes.

Sim-to-real evidence progresses:

```text
unit/numerical
  -> model-in-loop
  -> software-in-loop
  -> processor/hardware-in-loop
  -> physical testbed
  -> shadow operation
  -> bounded field/flight test
  -> staged ODD expansion
```

Each stage adds evidence. Simulated mileage cannot remove the need for world contact.

Real risk is:

\[
R_{real}=\mathbb E_{z\sim P_{real}}L(z),
\]

and simulation estimates it only under justified support/discrepancy assumptions. With zero failures in `n` genuinely independent representative trials, a one-sided approximate upper failure bound is `-log(α)/n`, about `3/n` at 95%; independence and representativeness are usually the hard part.

See [NIST digital-twin credibility](https://www.nist.gov/publications/credibility-consideration-digital-twins-manufacturing) and [ISO 23247-2](https://www.iso.org/standard/78743.html), noting that ISO 23247 is manufacturing-specific.

## Hybrid physics and machine learning

Preferred form:

\[
\dot x=f_{physics}(x,u,\theta)+\Delta_\phi(z),
\]

where the learned term has a declared role such as closure, residual correction, constitutive relation, or surrogate. It does not automatically have mechanistic meaning.

Promotion requires:

- dimensional correctness;
- hard constraints where feasible—soft residual penalties are not proofs;
- conservation, symmetry, boundary, and initial-condition checks;
- physics-only, data-only, and hybrid baselines;
- asset/regime/time-separated validation;
- numerical convergence and independent solver comparison;
- calibrated uncertainty and out-of-distribution abstention;
- stability and safety-envelope impact;
- external physical validation;
- surrogate-error propagation into downstream uncertainty/reachability;
- explicit scope, version, and expiry.

A low physics-informed neural-network residual is not a solution-error bound. [Physics-informed ML review](https://www.nature.com/articles/s42254-021-00314-5), [PINN failure modes](https://pmc.ncbi.nlm.nih.gov/articles/PMC10481851/)

As of 2026-07-15, ASME VVUQ 70 for machine learning is committee work, not a published compliance standard. Odeya must not claim conformance.

## Aerospace and autonomy adapters

Every external document is classified as normative standard, accepted means of compliance, recommended practice, guidance, draft, or research. A crosswalk is not certification.

Relevant aerospace references include [SAE ARP4754B](https://saemobilus.sae.org/standards/arp4754b-guidelines-development-civil-aircraft-systems), [SAE ARP4761A](https://saemobilus.sae.org/standards/arp4761a-guidelines-conducting-safety-assessment-process-civil-aircraft-systems-equipment), [FAA AC 20-115D](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_20-115D.pdf), [EASA AI Concept Paper Issue 2](https://www.easa.europa.eu/en/document-library/general-publications/easa-artificial-intelligence-concept-paper-issue-2), [FAA AI safety-assurance roadmap](https://www.faa.gov/aircraft/air_cert/step/roadmap_for_AI_safety_assurance), and [NASA software assurance](https://sma.nasa.gov/sma-disciplines/software-assurance-and-software-safety).

Road-autonomy references include [ISO 26262](https://www.iso.org/publication/PUB200262.html), [ISO 21448:2022 SOTIF](https://www.iso.org/standard/77490.html), [ISO 34502:2022 scenario evaluation](https://www.iso.org/standard/78951.html), and [UL 4600 Edition 3](https://www.ul.com/news/ul-4600-edition-3-updates-incorporate-autonomous-trucking).

## Physical architecture falsifiers

- Unit/frame/time mismatch survives schema or preflight.
- Shared systematic covariance is dropped.
- Calibration evidence is reused as independent validation without disclosure.
- An unresolved measurement-blind match is promoted, or a demonstrated
  analytic/dependency identity is still labeled an empirical measurement.
- Structural non-identifiability reaches parameter optimization.
- Code verification or one-grid output is labeled physical validation.
- A parameter absorbs model discrepancy without diagnosis.
- Random row splitting leaks trajectory, asset, or incident groups.
- Simulation or PINN residual promotes a physical/safety claim.
- A twin remains current after asset/configuration/calibration drift.
- Surrogate extrapolation proceeds without scope and abstention.
- Chance constraint is presented as hard safety.
- Runtime monitor shares an unexamined common-mode failure.
- Research recommendation acquires actuator authority.
- Zero simulated failures becomes a reliability claim.
- Checklist completion becomes “standards compliant.”

Any one is a critical architecture failure.

## Physical dependency order

1. Freeze quantity, unit, frame, time, uncertainty, covariance, and provenance contracts.
2. Define immutable measurement, asset, model, and evidence ledgers.
3. Define evidence-vector adjudication and bounded physical claim compiler.
4. Add observability, identifiability, excitation, and measurement-capability preflight.
5. Add code verification, solution verification, and VVUQ workflow contracts.
6. Add experiment planning in recommendation-only mode.
7. Add twin estimation in offline replay, then shadow mode.
8. Add learned/hybrid models only after physics-only baselines and VVUQ.
9. Add supervised execution through a separately authenticated safety/authority plane.
10. Consider bounded physical autonomy only after domain-specific evidence and external authorization.

## Foundational standards

- [BIPM SI Brochure, updated June 2026](https://www.bipm.org/en/publications/si-brochure)
- [JCGM GUM and VIM](https://www.bipm.org/en/committees/jc/jcgm/publications)
- [ISO 80000-1:2022](https://www.iso.org/standard/76921.html)
- [ISO/IEC 17025:2017](https://www.iso.org/standard/66912.html)
- [ASME VVUQ standards](https://www.asme.org/codes-standards/vvuq-standards)
- [NASA-STD-7009B](https://standards.nasa.gov/standard/nasa/nasa-std-7009)
