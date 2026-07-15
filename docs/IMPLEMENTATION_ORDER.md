# Implementation Order

Status: architecture plan only. This sequence does not authorize implementation. It begins only after the [pre-implementation gate](PRE_IMPLEMENTATION_GATE.md) passes and the operator authorizes Increment 0.

The order follows proof dependencies: scientific meaning before persistence, persistence before execution, execution before verification, verification before claims, and claims before interface or learning.

## Dependency spine

```text
mathematical constitution + schemas
  -> pure lifecycle and authority model
  -> canonical serialization and artifact identity
  -> append-only ledger and projections
  -> policy and capability grants
  -> durable work graph and resource accounting
  -> isolated execution
  -> independently isolated verification
  -> adjudication and claim compiler
  -> cockpit and sealed publication projection
  -> proof-mission adapters
  -> evaluated learning lab
  -> external thesis intake
```

No later layer may compensate for an unproven earlier one. In particular, a polished cockpit cannot repair ambiguous claim semantics, and more agents cannot repair weak verification.

## Increment 0 — Reproducible conformance skeleton

Begins only with explicit authorization.

Deliver:

- pinned language and toolchain versions;
- generated types from accepted schemas;
- local and CI architecture-conformance checks;
- deterministic test fixture packaging;
- dependency lock, SBOM, secret scanning, and minimal threat-model checks;
- no networked provider and no research execution.

Evidence:

- two clean machines reproduce the validation result;
- schema generators produce no unreviewed semantic drift;
- forbidden module dependencies and implementation-lock changes fail CI;
- the build produces a signed or attestable artifact without secrets.

Rollback: delete the skeleton without migrating research state.

## Increment 1 — Pure research algebra

Deliver a side-effect-free domain package for mission contracts, lifecycle transitions, authority predicates, terminal outcomes, protocol amendments, and claim eligibility.

Evidence:

- table-driven tests cover every legal and illegal transition;
- property-based tests preserve monotonic sequence, frozen protocol, authority separation, and append-only correction invariants;
- model checking covers lease/approval/publication races selected in the architecture gate;
- known-bad contracts and post-exposure mutations are rejected;
- no database, model, network, clock, or filesystem dependency exists in the core.

Rollback: replace the package while schemas and fixtures remain stable.

## Increment 2 — Canonical identity and artifact boundary

Deliver canonical serialization, digest envelopes, media typing, artifact manifests, environment identities, and a local content-addressed store adapter.

Evidence:

- semantically identical canonical objects hash identically across supported runtimes;
- number, Unicode, timestamp, ordering, and null/missing edge cases have conformance vectors;
- any byte mutation is detected;
- digest collision handling fails closed;
- signing proves origin while tests demonstrate it cannot substitute for semantic verification.

Rollback: migrate only through an explicit digest-version bridge; never reinterpret old digests.

## Increment 3 — Event ledger and deterministic projections

Deliver mission streams, optimistic concurrency, command idempotency, transactional outbox, reducer, snapshots as caches, and correction/invalidation projections.

Evidence:

- deleting every projection and replaying the ledger yields identical state;
- duplicate, reordered, missing, and corrupted events fail or recover exactly as specified;
- concurrent commands cannot create two legal owners or two publication transitions;
- backup/restore preserves digests and ledger position;
- interruption never requires chat history.

Rollback: restore the previous reader and rebuild projections from compatible events.

## Increment 4 — Policy and authority

Deliver identity adapters, capability grants, versioned policy decisions, approvals, revocation, dual-control hooks, and audit projection.

Evidence:

- every missing, expired, wrong-scope, replayed, or revoked grant fails closed;
- timeout never approves;
- generator cannot grant verification or publication authority to itself;
- policy-version changes are reproducible from retained inputs;
- simulated credential compromise is contained to the lease scope.

Rollback: revoke new grants and restore the prior policy bundle without rewriting history.

## Increment 5 — Durable work graph

Deliver DAG compilation, work items, attempts, leases, heartbeats, compare-and-set transitions, retry budgets, stale-work recovery, resource circuit breakers, and exact handoffs.

Evidence:

- worker death at every boundary creates neither lost state nor duplicate consequential action;
- retry creates a new attempt and preserves the failed attempt;
- estimated and actual costs never overwrite each other;
- budget exhaustion settles to the declared operational state;
- parallel branches cannot mutate one-writer state.

Rollback: stop leasing work; canonical mission state remains readable.

## Increment 6 — Isolated execution and capability gateway

Deliver one low-risk ephemeral worker, default-deny network, external credential broker, audited egress, quotas, deterministic environment capture, and quarantined artifact promotion.

Evidence:

- prompt-injected tool output cannot obtain undeclared capabilities;
- workers cannot read host secrets, other missions, or cloud metadata;
- unauthorized network, filesystem, process, spend, and external-write attempts fail;
- promotion rejects tampered or undeclared artifacts;
- one pinned proof-project task executes reproducibly.

Rollback: disable the worker adapter and revoke every capability grant.

## Increment 7 — Independent verification

Deliver a separate verifier process and identity, controlled evidence exposure, deterministic metric/falsifier evaluators, clean replay, discrepancy records, and positive-control fixtures.

Evidence:

- the verifier catches all declared broken artifacts;
- verifier false-accept and false-reject behavior is measured on a balanced fixture set;
- generator narrative cannot alter a deterministic verdict;
- disagreement remains explicit and blocks sealing where required;
- a different clean environment reproduces the selected result or its negative outcome.

Rollback: no claims become eligible; artifacts remain retained.

## Increment 8 — Adjudication and claim compiler

Deliver pure outcome derivation, claim-evidence traversal, eligible/forbidden wording, uncertainty rendering contract, corrections, retractions, and dependency invalidation.

Evidence:

- every proof-layer boundary has a regression fixture;
- simulation cannot compile into a deployment-safety claim;
- invalid and blocked runs cannot compile into nulls;
- a correction becomes at least as visible as its superseded claim in every projection;
- property tests show claims never widen beyond protocol and verifier scope.

Rollback: withdraw claim projection; the evidence ledger remains unchanged.

## Increment 9 — Observability and operator cockpit

Deliver read-only projections for mission, protocol, DAG, evidence, claims, authority, resources, freshness, and next legal action. Add redacted operational telemetry.

Evidence:

- supported, tight-null, invalid, blocked/unmeasured, and corrected fixtures are distinguishable without color;
- every displayed claim reaches exact provenance within two deliberate actions;
- stale state and projection position are visible;
- client code cannot authorize, adjudicate, or publish;
- accessibility and print tests pass the accepted matrix.

Rollback: remove the projection client without affecting canonical state.

## Increment 10 — Proof-mission shadow adapters

Deliver read-only, pinned adapters for settled Sentinel, Telos, and Inbar snapshots.

Evidence:

- Odeya reconstructs each project's current truth, including nulls, corrections, invalid runs, and blocked evidence;
- no adapter imports active dirty work as settled state;
- mismatch reports reveal where the canonical contract cannot represent a real workflow;
- the source projects remain scientifically and operationally authoritative.

Rollback: remove an adapter and its derived projection; never rewrite source projects.

## Increment 11 — Controlled active mission

Authorize one bounded computational experiment under human admission, safety, resource, and publication authority.

Evidence:

- end-to-end mission beats or complements the declared simple and single-agent baselines under comparable resources;
- independent review accepts the claim boundary and replay;
- pause, revoke, correction, and incident paths are exercised;
- value is measured net of compute, human effort, latency, and failure cost.

Rollback: revoke active execution authority and retain a complete handoff.

## Increment 12 — Improvement lab

Deliver quarantined strategy candidates, held-out evaluation, shadow replay, independent review, canary, rollback, and promotion records.

Evidence:

- generated code or prompts cannot change production directly;
- reward-hacking fixtures remain private and effective;
- promoted changes improve a declared Pareto dimension without hidden regressions;
- correction and rollback are faster than the accepted recovery objective.

## Increment 13 — External thesis intake and public projection

Only after internal admission, correction, evidence, and release workflows are stable.

Evidence:

- malicious proposals remain quarantined;
- accept/defer/decline reasons are auditable;
- acceptance cannot update shared claims;
- contributor rights, privacy, withdrawal, embargo, and credit survive end-to-end tests;
- public output is a sealed, bounded projection rather than direct database access.

## Rule for changing the order

An architecture decision may reorder increments only if it shows:

- which proof dependency no longer applies;
- how the new order avoids a circular trust assumption;
- the new negative fixtures and rollback;
- why the change reduces rather than hides scientific or operational risk.
