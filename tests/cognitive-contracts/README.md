# Cognitive control contract cases

This isolated package exercises the proposed logical records in
[`docs/COGNITIVE_CONTROL_CONTRACTS.md`](../../docs/COGNITIVE_CONTROL_CONTRACTS.md).
It introduces no command/event discriminator, runtime, product surface,
canonical aggregate, publication authority, or Gate A acceptance.

Run:

```bash
python3 tests/cognitive-contracts/check.py
```

Every fixture is synthetic and explicitly `proposed_non_authoritative`,
`derived_non_authoritative`, `deterministic_control_artifact`, or
`untrusted_candidate`. The model-configuration fixture is an
`immutable_non_authoritative_observation`; the routing fixture is a
`derived_non_authoritative_determination`. The `WorkContract` fixture is the deterministic control
artifact: it binds an exact canonical lease record, issuance event, reducer
frontier, and already-issued constraints but is never dispatch authority.
Fixture digests, identities, grants, receipts, reviews, experiments, evidence,
verifications, and adjudications are placeholders, not claims that those
activities occurred.

## Canonical construction order

The enclosing subjects contain no self digest. A `ResearchStateView` also has
no digest-bearing back-reference to its later compilation receipt. The required
construction order is:

1. produce schema-valid view bytes;
2. canonicalize those bytes and bind the resulting digest in an external
   identity registry;
3. produce a receipt that references the exact externally bound view identity
   and records compiler/input/index/cache/ranking/taint/selection facts,
   including explicit `pass`, `fail`, `indeterminate`, or `not_run` outcomes,
   while containing no receipt self digest or redundant output digest; and
4. later bind the view and receipt digests in an external sealed-root or bundle
   record whose construction and digest scope are separately defined.

The same external-binding rule applies to every proposed or derived subject in
this package, including a `WorkContract`. Adding an enclosing
`canonical_payload_digest`, self-reference, or mutual content-digest cycle is a
schema error.

A receipt is an observation, not an optimistic success certificate. Failed,
indeterminate, and not-run compilations remain retainable audit records. Only a
receipt whose compilation result, replay, coverage, contamination, clean-room,
negative-flow, and budget checks all pass is eligible for a `WorkContract`
state-compilation bundle.

## Logical ownership only

These records may eventually belong behind a state compiler, epistemic-state,
planning, or work-boundary owner. This package does not choose such a module or
declare any record canonical. A minimal canonical cognition slice may require
only one new aggregate, `epistemic_graph`; the view, receipt, planning,
experiment, work, candidate, and transition records remain derived or immutable
artifact lanes unless Gate A evidence proves another aggregate is irreducible.
Gate A scope review must decide ownership and whether existing artifact/work
boundaries are sufficient before command, event, reducer, or aggregate
vocabulary is added.

## Resource ontology

Execution and verification use different closed shapes. An execution budget
retains model-input tokens, model-output tokens, tool calls, CPU time, GPU time,
peak memory, storage, network egress, wall time, and spend as distinct limits
with immutable unit references. A verification-capacity vector separately
retains deterministic, typed compute, expert, physical, and safety demand.
Neither shape permits cross-resource conversion, and verification dimensions
cannot compensate for one another. The schemas do not claim that unlike units
are numerically comparable or that an estimate reserves real capacity.
`context_window_tokens` is a separate worker-input ceiling, not another
cumulative token budget. Worker checkpoints recover candidate progress only;
canonical epistemic state is reconstructed from the ledger, never from a
worker checkpoint.

## Epistemic graph boundary

An `EpistemicNodeVersion` is immutable proposition content plus lineage; it
does not carry mutable admission, validity, future-position, or superseded
state. Evidence support, contradiction, rivalry, compatibility, dependency,
prediction, and supersession are canonical only as typed graph edges proposed
by an `EpistemicGraphDelta`. Admission requirements derive from the delta's
closed admission class and are satisfied only by later governed verification,
adjudication, and event admission—not by the node or transition record itself.

An absent aggregate is `absent_genesis`, with frontier-bound absence evidence
and null graph version/root/head/origin. It is never a synthetic version-0
state. Proposed node lineage is descriptive only: a predecessor is canonically
superseded only by an explicit supersession edge after governed admission.
Correction fixtures retain non-resurrection and dependency-fanout obligations,
while their typed profile/rule may derive verification-only or verification-
plus-adjudication; adjudication is not universal merely because a change is a
correction.

Transition cases exercise both directions of the result/delta rule. `changed`
requires a nonempty closed typed-change set and a proposed delta; `no_change`
or `incomplete` requires an empty set and no proposed delta. Separate positive
cases retain edge-only, material-evidence-disposition-only, and contract-only
changes without inventing a hypothesis edit. Dereferencing the proposed delta
and proving that it actually realizes each declared class remains a semantic
compiler obligation.

## Cross-object semantic rules

JSON Schema enforces closed shapes and important local fail-closed states, but
a deterministic semantic compiler must additionally prove that:

- every reference resolves to immutable bytes and every declared digest matches;
- every legal-command entry's command type/version/member key and payload schema
  agree with the exact `CommandContractRegistry` bytes; its membership proof
  binds the same registry/member/`RegistryActivation` digests, and the
  activation scope includes the view mission and action at the source frontier;
- a view, its compilation receipt, work contract, candidate artifact, and
  transition bind the same exact view and checkpoint;
- graph aggregate, branch, predecessor root/head/reducer, and source-ledger
  positions agree exactly across views, deltas, transitions, and admitted
  events; JSON Schema cannot compare these values across objects;
- `absent_genesis` evidence proves no admitted graph delta exists through the
  bound frontier, while every existing graph has version at least one and an
  exact first-admitted-delta origin event;
- retrieval dispositions exactly partition the considered set, accounting
  totals reconcile, the dependency/input set, search-index snapshot, cache
  namespace/snapshot, embedding/ranker identity, taint labels, contamination
  frontier, retrieval candidate set, and every derived summary are exact,
  replay is deterministic, and no sealed or forbidden datum influenced ranking,
  summaries, caches, telemetry, or derived features;
- clean-room compilation resolves exact blocked-reference and
  blocked-derivative manifests and independently checks their absence from the
  index, cache, embeddings, and summaries;
- material evidence and contradictions in the source view appear exactly once
  with truthful dispositions in graph deltas, candidate artifacts, and
  transition records;
- graph predecessors exist at the expected versions and proposed additions and
  supersessions preserve all history;
- proposed successor lineage, correction predecessor/successor obligations,
  and explicit supersession-edge endpoints identify the same exact node bytes;
  the typed admission profile/rule and committed input recompute the declared
  verification/adjudication requirements, and correction fanout covers every
  affected dependent without resurrecting a superseded version;
- experiment predictions cover every material hypothesis, premise challenge
  evaluates admissible evidence, rivals, and falsifiers before `proceed`,
  feasibility and identifiability evidence are sound, and planner hard filters
  match the dereferenced candidate;
- Pareto bounds, sensitivity, best-of-N history, multiplicity accounting, and
  multidimensional verification-capacity packing are truthful and complete;
- capability handles resolve only through current canonical grants; the lease
  record, issuance event, scope, constraint snapshot, reducer frontier, and
  duplicate dispatch-recheck binding are byte-for-byte identical where
  required; leases and cancellations are current; and fallback identities
  differ from prior attempts;
- every work dispatch rechecks the exact current authority/policy/frontier,
  active `DataUseDecision` records, exposure intent, provider configuration,
  resource/spend reservation, canonical lease record/frontier, lease state, and
  controlled time; stale, expired, revoked, mismatched, or indeterminate state refuses, and a
  separately admitted work-dispatch/external-effect claim exists before any
  bytes cross a provider boundary or provider spend is incurred;
- observable tool/effect receipts are authentic canonical observations rather
  than producer-generated logs, and artifact custody/settlement is complete;
- transition graph-delta proposals bind the exact predecessor graph and are
  admitted only after the required evidence, rules, verification, and
  adjudication dispositions are satisfied; proposed-delta status is equivalent
  to a `changed` result with a nonempty closed typed-change set, while
  `no_change` and `incomplete` carry no proposed delta or typed change; and
- private chain-of-thought, self-confidence, narrative, ranking, debate, votes,
  and consensus never satisfy evidence or independent-verification obligations.

A passing checker run is predominantly structural evidence. The
model-configuration and routing vectors additionally execute bounded local
semantic checks for interval order, controlled-time validity, capability/task
coverage, data-class conflict, candidate counts, exact hard-rule binding,
selected-reference equality, unresolved selected dimensions, and fallback
identity. Their estimates, bounds, and resource amounts use canonical exact-
decimal strings; the cases reject binary JSON numbers, exponent notation,
leading zeros, and lexical negative zero, and the checker compares them with
decimal arithmetic. They still do not prove external reference resolution, registry
completeness, noninterference, scientific validity, reviewer independence,
authority, operational behavior, or performance.

In particular, the schema cannot prove that a decision or grant is still active
at dispatch time. The dispatch admission path must dereference and re-evaluate
those facts atomically enough for its declared authority and spend model.

The model-configuration and routing cases additionally prove only local shape
constraints. A semantic validator must resolve the exact registry member,
recompute evidence validity and interval ordering, reconcile registry/considered
candidate counts, prove the constraint and dimension partitions, recompute the
Pareto frontier and sensitivity record, and establish that the selected
reference equals the sole selected candidate. Even after those checks, routing
remains a proposal: dispatch must re-admit current authority, policy, data,
provider, resource, exposure, and controlled-time facts.

The 2026 clean-room synthesis and premise-refusal results cited by the parent
architecture document are preprint evidence. They motivate these fail-closed
dimensions but do not establish universal model behavior, validate these
schemas, or prove that an implementation prevents contamination.

The view's compilation timestamp is controlled-source time with an immutable
source reference. Deterministic ordering and freshness must never be inferred
from an ungoverned compiler wall clock.
