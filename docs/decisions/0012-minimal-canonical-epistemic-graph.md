# 0012: One minimal canonical epistemic graph

- Status: Proposed
- Date: 2026-07-15
- Gate: G1/G2/G5/G6; requires command/event/reducer closure, composite replay, independent scientific review, and operator acceptance

## Context

Odeya needs durable epistemic continuity across model, worker, provider, and process replacement. It must retain hypotheses, alternatives, contradictions, residual unknowns, experiment candidates, evidence relations, corrections, and the exact reasons a scientific transition was admitted.

Making every cognitive record a mutable aggregate would duplicate authority and create cyclic state: a compiled view would appear to own facts it merely projects; a work contract would look like scientific state; a candidate artifact could become canonical by existing; and node-level writers could race to manufacture incompatible graph truth. Treating every record as disposable would fail in the opposite direction by losing governed epistemic history.

The architecture therefore needs the smallest state authority that preserves scientific causality without allowing a model, worker, cache, index, or projection to become a second writer.

## Proposed decision

Odeya has exactly one canonical cognitive-state aggregate type: `epistemic_graph`. An aggregate instance is scoped to one mission and protocol branch. It is founded by its first admitted delta against the declared canonical empty-graph root and version `0`; there is no implicit default aggregate.

All other cognitive records have non-state roles:

- `ResearchStateView` and `ContextCompilationReceipt` are immutable derived records bound by an externally issued compilation bundle/root;
- `WorkContract` is an immutable deterministic control artifact and never data, effect, or claim authority;
- `ExperimentCandidate`, `PlanningEpoch`, `CandidateArtifact`, `EpistemicGraphDelta`, and `EpistemicTransitionRecord` are immutable proposal or audit artifacts;
- model context, scratchpads, retrieval indexes, embeddings, summaries, caches, queues, and UI state are replaceable projections or execution material, never canonical memory.

Only one command may change this aggregate:

```text
epistemic_graph.admit_delta
```

Only one event family records the accepted transition:

```text
epistemic_graph.delta_admitted
```

The command references the exact graph delta and transition record, predecessor graph version and root, applicable protocol/rule snapshots, source view and candidate artifact, evidence dispositions, and every required verification or adjudication result. Command admission revalidates current graph head, artifact custody and identity, data-use and exposure constraints, authority, scientific consequence rules, and the admission-class requirements. A stale, incomplete, indeterminate, unauthorized, or digest-mismatched proposal fails closed without a graph event.

The event references the exact admitted delta and transition record plus their immutable canonical identities, the predecessor version/root, the closed admission class, the decisive validation/verification/adjudication records, and the rules used. It does not embed a successor state digest. The registered pure reducer applies the referenced delta, advances the version exactly once, preserves all prior node and edge versions, and computes the successor projection externally. This avoids a digest cycle when projected state also records its head event.

Graph deltas are admitted under one closed class:

| Admission class | Permitted meaning | Mandatory checks |
|---|---|---|
| `exploratory_structure` | Add or relate hypotheses, rivals, contradictions, unknowns, predictions, or experiment candidates without implying support | provenance, scope, exposure, complete material-evidence disposition, premise consequence, and no claim-promotion semantics |
| `evidence_relation` | Relate governed evidence or observations to epistemic nodes | exact custody, rights/data-use, method, dependency/correlation, scope, validity, and disposition checks |
| `claim_bearing` | Add a scoped relation that could affect a later claim-eligibility computation | all evidence checks plus exact required verification, adjudication, uncertainty, falsifier, multiplicity, and claim-boundary checks |
| `correction_supersession` | Correct or supersede an existing node/relation while retaining history | exact predecessor, correction reason, dependency fan-out, affected-claim/publication consequences, and non-resurrection checks |

Admission to the graph is never claim promotion, method admission, publication authorization, or evidence validation. Those remain separate aggregates and decisions. A graph may record that a proposition is supported under a declared scope only when the class-specific evidence and verification contracts permit that relation; the publication and claim compilers independently decide eligibility from canonical inputs.

## Reducer and ownership invariants

The aggregate owner is the `epistemic_state` module. The application service is the sole command writer; the registered `epistemic_graph` reducer is the sole state transition function.

The reducer must enforce:

1. mission/branch identity cannot change;
2. command predecessor version/root equals the current graph head;
3. one admitted event advances one version, with no gaps or forks;
4. existing node and relation versions are immutable;
5. supersession adds explicit forward and backward references and never erases the superseded object;
6. every material evidence item has an allowed disposition, including incomplete or indeterminate coverage with a non-continue consequence;
7. admission class is closed and cannot be inferred from prose;
8. no graph edge can manufacture evidence validity, authority, verification independence, claim eligibility, or publication state;
9. canonical reconstruction depends only on the sealed event stream, exact referenced artifacts, and the named reducer snapshot; and
10. search, vector, cache, UI, and worker-private state can be destroyed and rebuilt without changing the graph.

Reducer output is checked by independent implementations against shared fixtures and composite traces. A mismatch, missing artifact, unknown reducer digest, broken predecessor, or incompatible semantic version quarantines the projection and blocks dependent writes.

## Rejected alternatives

### Per-node aggregates

Rejected because multi-node scientific transitions would require distributed commits or permit partially applied reasoning. Cross-node contradictions, evidence disposition, and correction fan-out must settle atomically as one graph delta.

### Candidate artifacts update the graph directly

Rejected because workers and models are untrusted proposal producers. Artifact creation proves custody of an output, not scientific admission.

### Views or retrieval memory as canonical state

Rejected because views are exposure-bounded derivatives and retrieval systems are incomplete, mutable, and implementation-specific. They may omit information by policy or budget and must be reproducible from stronger sources.

### One mutable agent memory

Rejected because it is difficult to audit, cannot preserve exact scientific causality, couples continuity to one model/context, and gives probabilistic text implicit authority.

### Separate aggregate for every cognitive record

Rejected because it multiplies writers, versions, and circular dependencies without adding independent truth. Immutable records remain addressable and reviewable without becoming state authorities.

## Falsifiers and acceptance evidence

Keep this decision proposed if any of the following remains true:

- the first proof-mission slice cannot be represented without hidden worker memory;
- one scientific transition cannot atomically preserve all material evidence dispositions, alternatives, contradictions, and correction fan-out;
- graph admission can change claim, publication, method, evidence-validity, or authority state by implication;
- the command, event, reducer, module, and canonicalization registries do not bind the exact contracts used;
- a stale proposal or missing/indeterminate verification can produce `delta_admitted`;
- two independent reducers disagree on the same sealed trace;
- deleting all projections changes replayed graph state; or
- a composite crash/recovery trace can expose a partial or forked graph transition.

Acceptance requires exact schemas, valid and adversarial fixtures for every admission class, a sealed command/event/reducer registry, independent reducer conformance, canonicalization agreement, proof-mission replay, crash/fork/recovery traces, scientific and distributed-systems review, and Daniel's signature on the exact Gate A candidate. It does not authorize runtime implementation.
