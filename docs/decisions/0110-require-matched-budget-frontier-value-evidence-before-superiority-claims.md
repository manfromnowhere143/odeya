# ADR 0110: Require matched-budget frontier-value evidence before superiority claims

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-08-03
- Decision owners: mission, evaluation, scientific methods, evidence,
  authority, security, product
- Gate effect: proposes a G0/G5 claim and evaluation boundary; does not pass a
  gate, preregister or execute a study, authorize implementation, or establish
  that Odeya is implemented, useful, frontier, or superior

## Context

Odeya's architecture specifies durable state, typed evidence, independent
verification, explicit authority, replay, and correction retention. Those are
important design properties. They are not comparative outcome evidence.

By 2026-08-03, scientific workbenches and research-agent products publicly
describe many adjacent capabilities: long-running tool use, specialist agents,
scientific connectors, code and artifact provenance, remote compute, reviewer
agents, and expert-oriented benchmarks. Multi-agent gains can also be largely
resource-mediated, benchmark answers can leak or be deliberately recovered,
infrastructure can move scores by several percentage points, and agent-assisted
scientific software still requires external acceptance targets and expert
stewardship.

The repository therefore needs an explicit rule that distinguishes a strong
architecture proposal from evidence of real-world or frontier value.

## Decision

The proposed decision is to adopt the [Frontier Research Value Evaluation Protocol
Candidate](../FRONTIER_RESEARCH_VALUE_EVALUATION_PROTOCOL_2026-08-03.md) as
the proposed review packet for any future Odeya capability, value, superiority,
or frontier claim.

No such claim is eligible unless one exact accepted protocol:

1. names the task population, systems, date, resources, estimands, thresholds,
   oracles, contamination boundary, and consequence table before outcomes are
   exposed;
2. separates mechanism-controlled comparisons, current-product comparisons,
   and expert/current-practice comparisons;
3. includes the strongest relevant single-agent, multi-agent, deterministic,
   current-product, and qualified human baselines where applicable;
4. reports model, prompt, tools, infrastructure, token, compute, money,
   wall-time, and human-time differences rather than calling nominal token
   equality a matched budget;
5. retains final-outcome quality, observable epistemic conduct, integrity,
   authority, safety, calibration, cost, and downstream value as separate
   dimensions;
6. uses a private sealed outer holdout and exposure-aware clean-room variants,
   validates graders, and retains contaminated attempts as `invalid`;
7. refuses post-outcome exclusions, thresholds, metric changes, favorable-seed
   selection, missing-as-zero, hidden negatives, and self-verification; and
8. receives accountable domain, statistical, security/authority, and
   evaluation-validity review before an operator claim decision; and
9. for a frontier claim, qualifies against every strongest accessible named
   current product on the same task/date under its preregistered capability or
   efficiency route and is independently reproduced under the packet's frozen
   independence profile by a separately accountable non-producer using fresh,
   non-shared execution state and independently recomputed metrics.

Capability, efficiency, integrity, and research-team value remain separate
preregistered claim units. A `PromotionDecision` about an internal strategy
candidate cannot combine them into product-value evidence. Scientific/evidence
disposition, operational disposition, replication/correction state, and
current-claim eligibility are separate fields. Current-use eligibility for a
frontier claim ends after 90 days or a material named-comparator release,
whichever comes first; `current_claim_eligible` then becomes `false` and reuse
is `blocked` without rewriting the historical result. “Material release” uses
the packet's closed system-identity rule rather than post-outcome judgment.

An architectural invariant follows:

> Feature presence is never research-value evidence. A frontier claim requires
> a same-date, named-comparator, named-task, named-budget, independently
> reviewed and reproduced result whose exact limitations remain attached.

## Candidate effect thresholds

The packet proposes values for operator and statistical review: a capability
route whose observed paired improvement is at least five percentage points and
whose 95% confidence interval excludes zero, or an efficiency route based on a
two-percentage-point noninferiority margin plus at least a 20% improvement on
one preselected primary resource. Both routes carry explicit integrity floors
and critical-stratum nonregression. Task or team-task is the unit of analysis;
seed repetitions are nested trials, not independent sample-size inflation.
One primary route and tier must be frozen, or every confirmatory route, tier,
endpoint, and critical stratum must share one prespecified gatekeeping and
multiplicity plan.

These numbers are preregistration candidates, not accepted universal constants.
The operator and an accountable statistical reviewer must accept, reject, or
amend them on the exact first-wedge protocol before any outcome is visible.
Changing them after exposure invalidates the confirmatory comparison.

## Consequences

- “Odeya has X architectural feature” cannot be translated into “Odeya is more
  advanced” without outcome evidence.
- Company names, marketing pages, vendor scores, and inaccessible proprietary
  systems cannot be used as borrowed validation.
- Without same-date strongest-accessible-product comparison and independent
  reproduction, a favorable result can claim only that Odeya was better than
  the tested named systems on the exact task, date, and budget—not “frontier.”
- The first accepted study must be small, deeply auditable, and tied to one
  real decision; broad benchmark accumulation is not the objective.
- Negative, null, contradicted, invalid, and inconclusive results remain
  first-class outputs and may falsify the proposed architecture's value.
- A future engine may earn wider claims only through prospective task and
  domain transfer; no result inherits generality.

## Required follow-on architecture evidence

Before this decision can contribute to G5 acceptance, retain and review:

- exact evaluation-plan, task/split, system, resource, contamination/exposure,
  grader, statistical-analysis, and result contracts;
- known-bad fixtures for every stable protocol-defect ID, expected disposition,
  and reason code enumerated in the packet;
- one rights-cleared first-wedge task population and qualified human baseline;
- validated deterministic, statistical, sealed-truth, and expert oracle paths;
  and
- the exact operator consequence table and review assignments.

## Non-decisions

This ADR does not:

- accept the proposed thresholds or select the first domain wedge;
- validate any cited vendor claim or establish a competitor ranking;
- claim that Odeya is implemented or that any mission has run through it;
- pass G0, G5, Gate A, PRQ-002, or any A-001–A-016 finding;
- substitute model-worker analysis for accountable human review;
- authorize runtime, application, infrastructure, deployment, credentials,
  spending, private-data access, scientific publication, outreach, physical
  action, or repository publication; or
- create evidence by restating a desired result.
