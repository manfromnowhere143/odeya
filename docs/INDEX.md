# Reviewer Reading Map

Status: navigation index for external reviewers, added 2026-07-24. This file
is a map, not evidence: every claim of record lives in the linked surface, and
where a count is validator-bound this index points at the surface that
recomputes it instead of restating the number. Nothing here is Gate A
acceptance, runtime authorization, or a scientific claim.

## Read in this order

1. [README](../README.md) — the honesty banner, the one-view system map, and
   the reviewer table separating what is proven from what is planned.
2. [Architecture status](ARCHITECTURE_STATUS.md) — the current machine
   evidence table, Gate A readiness by area, and the critical blocker list.
   This is the validator-bound current-state surface; prefer it over any
   number quoted in prose elsewhere.
3. [Session handoff](SESSION_HANDOFF.md) — the canonical operational baton:
   recovery identity, engineering laws, publication sequence, and the
   dependency-ordered next missions. It is written for the next working
   session, so it is dense; read it after the status file, not before.
4. Key decision records by theme (below) — why each boundary exists and which
   evidence could change it.
5. The machine evidence itself (locations below) — schemas, isolated suites,
   retained coverage records, and bounded formal models.

## Glossary

- **PRQ** — a Gate A prerequisite finding (PRQ-001 through PRQ-013), each a
  named contradiction or gap that must close before Gate A; recorded with its
  exact closure requirements in the
  [Gate A prerequisite closure plan](GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md).
- **T0 / T1 (and T2 / T3)** — the dependency-ordered closure stages in that
  same plan: T0 is identity and prerequisite closure that issues no immutable
  member, T1 is the smallest dependency-contained vertical contract, T2 builds
  the remaining exact members, and T3 is an inactive constitutional candidate.
- **Gate A / B / C** — the blocking sequence in the
  [pre-implementation gate](PRE_IMPLEMENTATION_GATE.md): Gate A is the
  operator's exact-byte architecture acceptance decision; Gate B permits only
  separately authorized disposable probes after Gate A; Gate C must separately
  authorize one bounded runtime increment. All three are currently open;
  Gate A is blocked.
- **ADR** — an architecture decision record under
  [`docs/decisions/`](decisions/); accepted decisions are superseded
  prospectively by a new record, never silently rewritten.
- **HDA** — human decision assurance, the PRQ-013 subject: evidence that a
  consequential human-only decision was actually made by a human, beyond a
  valid signature. The contract is
  [Human decision assurance](HUMAN_DECISION_ASSURANCE.md); `HDA-CTX-001`
  through `HDA-CTX-016` are its open findings pending accountable closure
  review.
- **Tranche** — one bounded, separately validated increment of architecture
  work, landed as a single scoped commit with its own evidence; the repository
  history is a sequence of tranches, not a continuous stream of edits.
- **Known-bad** — an adversarial fixture that a gate must refuse; the house
  rule is that a gate does not count as existing until a known-bad proves it
  fires. Known-bad corpora live beside each suite under
  [`tests/`](../tests/).

## Key decision records by theme

The [`docs/decisions/`](decisions/) directory holds the numbered records; the
directory listing is authoritative (the numbering has one gap that belongs to
a concurrent design lane). Entry points by theme:

- **Founding boundaries** —
  [0000](decisions/0000-adopt-odeya.md) adopt Odeya,
  [0002](decisions/0002-evidence-native-kernel.md) evidence-native kernel,
  [0006](decisions/0006-architecture-before-implementation.md) architecture
  before implementation.
- **First slice and identity** —
  [0013](decisions/0013-admitted-only-command-ingress.md) admitted-only
  ingress, [0014](decisions/0014-resolve-first-slice-atomic-admission.md)
  atomic admission,
  [0016](decisions/0016-separate-work-intent-from-assigned-work-contract.md)
  intent/contract separation,
  [0020](decisions/0020-freeze-nonrecursive-canonical-profile-candidate.md)
  canonical profile candidate.
- **Canonical migration wave** —
  [0032](decisions/0032-partition-the-canonical-migration-findings.md)
  partition the findings,
  [0037](decisions/0037-record-the-operator-delegation.md) operator
  delegation, [0050](decisions/0050-close-the-wave-at-audit-zero.md) wave
  closed at audit zero.
- **Evidence quality and guard coverage** —
  [0024](decisions/0024-bind-known-bad-traces-to-their-guards.md) bind traces
  to guards, [0025](decisions/0025-prove-lifecycle-guards-by-mutation.md)
  prove guards by mutation,
  [0030](decisions/0030-statement-coverage-is-not-condition-coverage.md)
  statement vs. condition coverage,
  [0079](decisions/0079-the-suite-guard-audit-generalized.md) the generalized
  suite audit,
  [0094](decisions/0094-bind-current-status-surfaces-to-retained-machine-evidence.md)
  bind status prose to machine evidence.
- **Adversarial review rounds** —
  [0051](decisions/0051-adversarial-review-round-one.md),
  [0063](decisions/0063-adversarial-review-round-two.md),
  [0069](decisions/0069-adversarial-review-round-three.md),
  [0077](decisions/0077-round-four-the-audits-are-not-gates.md). Each round
  was briefed to refute, each found real defects, and each correction is
  retained in place.
- **Repository publication** —
  [0045](decisions/0045-open-source-packaging.md) open-source packaging,
  [0047](decisions/0047-create-the-public-remote-and-publish.md) the public
  remote, [0087](decisions/0087-reconcile-public-repository-operational-contract.md)
  operational reconciliation,
  [0091](decisions/0091-exact-sha-two-ref-publication-sequence.md) the
  exact-SHA two-ref publication sequence.
- **PRQ-013 human decision assurance** —
  [0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
  the founding finding,
  [0092](decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md)
  the assurance wrapper,
  [0093](decisions/0093-co-bind-the-confirmation-gesture-through-a-two-phase-challenge.md)
  the two-phase challenge,
  [0095](decisions/0095-reissue-human-decision-assurance-as-a-byte-bound-independently-recomputed-chain.md)
  the byte-bound recomputed chain,
  [0096](decisions/0096-reconstruct-the-successor-phase-two-binding-before-technical-review.md)
  the pre-review reconstruction.
- **Work-lease ownership correction** —
  [0090](decisions/0090-preserve-the-resource-claim-when-work-lease-ends.md)
  preserve the resource claim when a work lease ends.
- **Evaluator integrity** —
  [0097](decisions/0097-adversarially-validate-the-canonicalization-evaluator.md)
  adversarially validate the canonicalization evaluator.

## Where the machine evidence lives

- [`schemas/`](../schemas/) — the JSON Schema (Draft 2020-12) resource corpus.
  The current schema and case counts are measured by
  [`scripts/validate.py`](../scripts/validate.py) on every run and stated in
  the validator-bound checkpoint section of the README and in
  [Architecture status](ARCHITECTURE_STATUS.md).
- [`tests/`](../tests/) — the isolated contract suites. Each directory pairs a
  checker with a `cases.json` manifest of safe controls and known-bad
  fixtures, including the declared adversarial-tag requirements.
- [`architecture/`](../architecture/) — retained machine records: guard- and
  condition-coverage records, candidate evidence bindings, the consumer
  census, the surface policy, and the Gate A prerequisite closure record.
  These are regenerated by the audit scripts, never hand-edited.
- [`formal/tla/`](../formal/tla/) — the bounded TLA+ models with their safe
  configurations and retained intended-counterexample configurations, run by
  [`formal/tla/check.sh`](../formal/tla/check.sh).
- [`scripts/`](../scripts/) — the structural validator
  (`validate.py`), the per-concern validators it dispatches, and the mutation
  audits that re-measure coverage rather than trusting a record.
- [`.github/workflows/`](../.github/workflows/) — the least-privilege,
  full-SHA-pinned CI workflows, with the hash- and integrity-locked toolchain
  under [`tools/repository-release/`](../tools/repository-release/).
- [Repository release engineering](REPOSITORY_RELEASE.md) and
  [`scripts/ci/rehearse-fresh-clone.sh`](../scripts/ci/rehearse-fresh-clone.sh)
  — the exact-commit fresh-clone rehearsal that reproduces the checkpoint from
  bytes and writes an external evidence manifest.

## Map of `docs/`

Grouped one-line descriptions; every file is architecture evidence or contract
prose, none is runtime documentation.

### Current state and process

- [ARCHITECTURE_STATUS.md](ARCHITECTURE_STATUS.md) — validator-bound working
  checkpoint: machine evidence, gate readiness, blockers.
- [SESSION_HANDOFF.md](SESSION_HANDOFF.md) — canonical recovery baton for the
  active mission.
- [GATE_A_HANDOFF_WORKING_PACKET_2026-07-15.md](GATE_A_HANDOFF_WORKING_PACKET_2026-07-15.md)
  — dated detailed working packet behind the handoff.
- [GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md](GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md)
  — the PRQ findings and the T0–T3 closure order.
- [GUARD_COVERAGE_CLOSURE_PLAN.md](GUARD_COVERAGE_CLOSURE_PLAN.md) — roadmap
  for the unproved refusal statements, bound to the retained machine record.
- [PRE_IMPLEMENTATION_GATE.md](PRE_IMPLEMENTATION_GATE.md) — the blocking
  Gate A checklist and the Gate B/C sequence.
- [IMPLEMENTATION_ORDER.md](IMPLEMENTATION_ORDER.md) — post-gate build order;
  authorizes nothing by itself.
- [ROADMAP.md](ROADMAP.md) — evidence-gated phases, not calendar promises.
- [ARCHITECTURE_REVIEW_PROTOCOL.md](ARCHITECTURE_REVIEW_PROTOCOL.md) — how an
  exact candidate earns accountable review and acceptance.
- [REVIEWER_AGENT_PROPOSAL.md](REVIEWER_AGENT_PROPOSAL.md) — proposal for a
  contracted refutation worker; awaiting the operator's decision.
- [INTERNAL_RED_TEAM_FINDINGS_2026-07-15.md](INTERNAL_RED_TEAM_FINDINGS_2026-07-15.md)
  — retained internal finding ledger from pre-freeze review.
- [FRONTIER_REVIEW_2026-07-15.md](FRONTIER_REVIEW_2026-07-15.md) — dated
  survey of frontier research systems; re-verify before reuse.
- [CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md)
  — bounded audit of the sibling proof missions as requirements evidence.

The handoff's precedence rule applies throughout: exact Git bytes and machine
manifests outrank every prose surface, including this index.

### Core architecture and domain model

- [ARCHITECTURE.md](ARCHITECTURE.md) — the system design: deterministic
  kernel, cognitive workers, projections.
- [STATE_MODEL.md](STATE_MODEL.md) — events as facts, states as deterministic
  projections.
- [TRANSACTION_MODEL.md](TRANSACTION_MODEL.md) — transaction and recovery
  semantics the kernel must preserve.
- [COMMAND_EVENT_CATALOG.md](COMMAND_EVENT_CATALOG.md) — the command/event
  algebra and envelopes.
- [COMMAND_CONTRACT_REGISTRY.md](COMMAND_CONTRACT_REGISTRY.md) — structural
  command registry candidates; nothing enrolled.
- [REGISTRY_GRAPH_CONTRACTS.md](REGISTRY_GRAPH_CONTRACTS.md) — machine shape
  of the command/event/reducer/state graph.
- [REDUCER_REGISTRY.md](REDUCER_REGISTRY.md) — the only legal fold from
  events to canonical state.
- [ENGINE_CONTRACT_ROOT.md](ENGINE_CONTRACT_ROOT.md) — acyclic identity and
  activation topology.
- [CONSTITUTIONAL_CONSTRUCTION_AND_SEALING.md](CONSTITUTIONAL_CONSTRUCTION_AND_SEALING.md)
  — how a constitutional root may ever be constructed and sealed.
- [FIRST_VERTICAL_SLICE.md](FIRST_VERTICAL_SLICE.md) — the selected
  proof-mission truth-compiler slice.
- [FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md](FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md)
  — the bounded first-slice scope candidate (its predecessor
  [closure plan](FIRST_SLICE_ADMISSION_CLOSURE_PLAN.md) is retained as audit
  trail).
- [FIRST_SLICE_METHOD_PROFILE.md](FIRST_SLICE_METHOD_PROFILE.md) — maps the
  proof fixtures to the scientific constitutions.
- [MODULE_DEPENDENCY_MANIFEST.md](MODULE_DEPENDENCY_MANIFEST.md) — logical
  module ownership and dependency direction.
- [INTERFACE_CONTRACTS.md](INTERFACE_CONTRACTS.md) — language-neutral port
  contracts.
- [CANONICALIZATION_PROFILE.md](CANONICALIZATION_PROFILE.md) — the frozen
  canonical identity/serialization candidate `odeya-jcs-0.1`; unissued.
- [SCHEMA_RESOURCE_REISSUE_AND_RETENTION.md](SCHEMA_RESOURCE_REISSUE_AND_RETENTION.md)
  — how schema resources are reissued without mutating predecessors.

### Scientific constitutions and verification

- [RESEARCH_PROTOCOL.md](RESEARCH_PROTOCOL.md) — the founding
  question-to-claim protocol.
- [MATHEMATICAL_CONSTITUTION.md](MATHEMATICAL_CONSTITUTION.md) — statistical
  and inferential kernel semantics.
- [PHYSICAL_SCIENCE_CONSTITUTION.md](PHYSICAL_SCIENCE_CONSTITUTION.md) —
  quantities, units, uncertainty, metrology, VVUQ boundaries.
- [SEMANTIC_VALIDATION.md](SEMANTIC_VALIDATION.md) — the relational rule
  layer above structural schema validity.
- [VERIFICATION_PROTOCOL.md](VERIFICATION_PROTOCOL.md) — independent
  verification as a separate governed role.
- [EVALUATION_AND_LEARNING.md](EVALUATION_AND_LEARNING.md) — learning only
  from grounded outcomes.
- [EVIDENCE_AND_MEMORY.md](EVIDENCE_AND_MEMORY.md) — typed append-only memory
  instead of transcripts.
- [FAILURE_MODEL.md](FAILURE_MODEL.md) — separating scientific, operational,
  policy, and security failure.
- [PROOF_LAYER.md](PROOF_LAYER.md) — the Sentinel/Telos/Inbar snapshot and
  its bounded role.
- [PROOF_MISSION_REQUIREMENTS_TRACEABILITY.md](PROOF_MISSION_REQUIREMENTS_TRACEABILITY.md)
  — lesson-to-contract traceability ledger.

### Authority, security, and governance

- [SECURITY_AND_AUTHORITY.md](SECURITY_AND_AUTHORITY.md) — containment and
  authority as part of the scientific method.
- [AUTHORITY_MATRIX.md](AUTHORITY_MATRIX.md) — role separation and the
  human-only action matrix; an exact frozen input to the HDA consumer census.
- [HUMAN_DECISION_ASSURANCE.md](HUMAN_DECISION_ASSURANCE.md) — the PRQ-013
  assurance contract and its unissued candidate resources.
- [THREAT_MODEL.md](THREAT_MODEL.md) — adversary and control assumptions.
- [DATA_GOVERNANCE.md](DATA_GOVERNANCE.md) — rights, purpose binding, and
  lifecycle invariants.
- [LEDGER_INTEGRITY_AND_RECOVERY.md](LEDGER_INTEGRITY_AND_RECOVERY.md) —
  witnessed checkpoints and integrity-first recovery.
- [COGNITIVE_ARCHITECTURE.md](COGNITIVE_ARCHITECTURE.md) — the model-driven
  layer, with no truth or authority.
- [COGNITIVE_CONTROL_CONTRACTS.md](COGNITIVE_CONTROL_CONTRACTS.md) — the
  records and invariants that make that layer reviewable.
- [THESIS_INTAKE.md](THESIS_INTAKE.md) — untrusted-proposal intake for the
  long-term contributed-thesis vision.

### Publication, projection, and release

- [PUBLICATION_PROTOCOL.md](PUBLICATION_PROTOCOL.md) — scientific eligibility,
  sealing, dispatch, and settlement as separate acts.
- [PROJECTION_CONTRACTS.md](PROJECTION_CONTRACTS.md) — truth, freshness, and
  disclosure bounds for every surface; Daniel owns the visual design.
- [PROVENANCE_EXPORT_PROFILE.md](PROVENANCE_EXPORT_PROFILE.md) — W3C
  PROV / RO-Crate mapping without ceding canonicality.
- [UI_UX.md](UI_UX.md) — the engine-facing truth and accessibility contract
  for future surfaces.
- [REPOSITORY_RELEASE.md](REPOSITORY_RELEASE.md) — the evidence-gated
  publication contract for this public repository.
- [STANDARDS_PROFILE.md](STANDARDS_PROFILE.md) — external standards versus
  replaceable product choices.
- [TECHNOLOGY_DECISIONS.md](TECHNOLOGY_DECISIONS.md) — reversibility
  discipline for future product selections.
