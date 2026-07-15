# Verification Protocol

Status: Gate A candidate contract. Architecture only; no verifier runtime, reducer, registry activation, or scientific acceptance is claimed.

## Purpose

`VerificationPackage` (`verification-run` schema `0.2.0`) is the immutable terminal scientific record for one verification run. It answers what exact subjects were checked, under which frozen plan and inputs, by whom, with what observed correlations and exposures, which controls and dimensions ran, what failed or remained unknown, and what terminal assessment was produced.

It does not grant claim, dispatch, spending, publication, correction, or dispute authority. Its `eligible_next_actions` are advisory outputs from an exact rule. A separate admitted command must authorize every consequential next action.

## Identity and causality

The construction order is acyclic:

```text
exact subject set + frozen plan/protocol/method/capacity/exposure/input/environment
  -> verification.assigned event
  -> optional verification.started and dimension observation events
  -> immutable VerificationPackage
  -> verification.completed event referencing the exact package
  -> optional monotonic dispute overlay events referencing the exact package
```

The package references the prior assignment and optional prior start event. It cannot contain the successor `verification.completed` event reference or event digest. The completion event binds the exact package schema, version, digest, and artifact reference. A dispute never rewrites the package or changes its terminal assessment.

The subject set is not a loose run ID. It carries a complete subject manifest, member root, canonicalization and selection rules, and at least one exact typed artifact, result, or claim reference. Digest equality, manifest membership, run-ID equality, and causal position are semantic checks in addition to structural schema validation.

## Terminal paths

| Execution path | Permitted terminal status | Required scientific meaning |
|---|---|---|
| `completed` | `confirmed`, `rejected`, `inconclusive`, `invalid` | Execution settled; terminal observations exist. |
| `failed` | `invalid`, `blocked` | Execution started and failed; the failure remains evidence, never a null result. |
| `not_started` | `blocked` | No verification result exists; controls and all dimensions are `not_run`. |
| `completion_unknown` | `blocked` | Dispatch began but settlement is unknown; dimensions remain `indeterminate` or `not_run`. |

`requested`, `running`, and `disputed` are not package statuses. Request/start are event-derived lifecycle facts. Dispute is a monotonic overlay with its own open/resolution events. The only terminal package statuses are `confirmed`, `rejected`, `inconclusive`, `invalid`, and `blocked`.

`confirmed` is relative to one exact assigned verification-requirement profile, never a universal claim. The run must complete, satisfy the profile's declared independence requirement, pass known-answer and known-bad controls, pass every dimension marked `required`, mark genuinely non-required dimensions as `not_applicable` or retain an optional pass, match the frozen execution plan, measure and reconcile actual use, and retain verification evidence. An `IV0_integrity` same-team package can therefore be confirmed without claiming independent science; it cannot satisfy a later claim gate that requires `IV3` or `IV4`. This structural gate still does not prove the evidence true or the science correct.

## Frozen assignment

`verification.assigned` and the package bind the exact:

- subject set and producer identity;
- verification plan, protocol snapshot, and method profile;
- verifier principal and independence profile;
- required `IV0_integrity`, `IV1_reexecution`, `IV2_clean_reproduction`, `IV3_independent_reimplementation`, or `IV4_independent_replication` class and required independence disposition;
- verification-capacity reservation and any operational resource reservations;
- exposure plan, input manifest, environment manifest, and control plan;
- assignment event, ledger position, and immutable content digests.

No later package may silently select `latest`, replace an input, or move a reservation. Cross-record equality and currentness are admission rules, not caller assertions.

## Independence and correlation

Independence is an observed vector, not a label inferred from role names, model consensus, or a different prompt. Every package records principal, organization, incentive, provider, model family, training lineage, tools, source corpus, implementation, data, context, and selection relations with retained evidence or an explicit unknown/not-applicable value. The package separately records the required verification class, observed class, required independence disposition, and rule/evidence-backed satisfaction result.

`independent_under_profile` requires a different principal, a different or external organization, distinct incentives, independently compiled/blinded context, and preregistered/blinded/independent selection with evidence. `same_inputs_different_prompt` cannot satisfy this disposition. Shared provider, model family, training lineage, corpus, code, data, or incentives remain visible even when another axis is independent. Confirmation itself does not universally require that disposition: the frozen mission/claim profile decides which independence class is required.

## Controls and dimensions

Known-answer and known-bad controls are both mandatory planned sets. Each control records `pass`, `fail`, `indeterminate`, or `not_run`, exact fixture/report/evidence references, and reasons. A `confirmed` package cannot accept a known-bad fixture or miss either control class. A pre-execution blocker preserves planned controls as `not_run` without inventing reports or successful evidence.

Every package records these dimensions with `pass`, `fail`, `indeterminate`, `not_applicable`, or `not_run` semantics:

```text
artifact integrity; schema conformance; computational reproducibility;
code verification; method validity; statistical validity; calibration;
causal identification; physical validity; external validation;
transportability; claim boundary; safety
```

Every dimension also records `required` or `not_required` under the exact frozen profile. `pass` and `fail` require evidence. `indeterminate` and `not_applicable` require limitations. `not_run` requires a reason and prohibits dimension evidence. A typed assessment summary must agree with actual control/dimension/execution evidence: rejected requires a failure, inconclusive requires an indeterminate dimension and unknown finding, invalid requires a failed execution or non-pass scientific/control fact, and a failed blocked path cannot carry an all-pass vector. Discrepancies, counterexamples, and unknowns are first-class retained findings rather than prose hidden behind an aggregate score.

## Resource and exposure settlement

Reserved capacity and actual use are different facts. Reservation references are frozen in the assignment. The terminal package records measured, partially measured, unknown, or not-run actual-use observations and a separate reconciliation state. Unknown actual use is not zero and requires an exact reconciliation/uncertainty record while the reservation remains `unsettled_held`; only a never-claimed/not-required reservation may omit a reconciliation record. A not-started verification has no actual-use observations; completion uncertainty retains a conservative unknown or partial observation until the resource aggregate reconciles it.

The exposure plan is frozen before assignment. The package separately records observed exposure, no permitted exposure, unknown exposure, or not-started exposure with exact observation references and reasons. Every disposition requires an exposure-audit artifact; `none_permitted` is a negative-flow observation, never proof by an empty list. An exposure declaration is not evidence of isolation.

Completed, failed, and completion-unknown paths bind exact actual run, input, environment, and code manifests plus a plan-comparison report and any deviations. Only a not-started path may leave those actual manifests null. A frozen planned environment cannot lend its identity to work that actually ran elsewhere.

## Disputes

`verification.disputed:2.0.0` references the exact immutable package and opens one dispute ID over named dimensions or assessments. `verification.dispute_resolved:2.0.0` references the prior open event and an exact resolution artifact. Both assert that the package terminal status is unchanged. A resolution may lead to a new verification package, claim correction, or invalidation command, but cannot mutate historical package bytes.

## Gate A evidence and remaining work

Structural fixtures cover independent and same-team confirmation, physical verification with non-computational dimensions explicitly not required, rejection, inconclusive assessment, not-started blocking, failed invalidation, and completion-unknown conservative holding. Known-bad mutations reject lifecycle states in terminal bytes, unjustified all-pass outcomes, missing subjects/frozen or actual bindings, failed controls under confirmation, unsupported indeterminate controls, fabricated success on an early blocker, evidence-free exposure claims, erased unknown settlement cases, and prompt-only independence claims.

Gate A still requires admitted command/event/reducer registry entries, exact resource-reservation integration, cross-record semantic rules and independent implementations, replay traces for every terminal path and dispute ordering, canonical package vectors, and independent statistical/domain/security review. Passing JSON Schema tests is necessary evidence, not architecture acceptance.
