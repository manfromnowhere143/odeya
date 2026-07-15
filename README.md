# Odeya

Odeya is a private, evidence-native operating system for frontier research. Its purpose is to turn a thesis into a bounded, replayable research mission whose claims can be traced to preregistered tests, exact artifacts, independent verification, and explicit authority.

> Current state, 2026-07-16: architecture foundation only. This repository does not yet contain an executable research engine and makes no claim of autonomous science.

Runtime implementation is blocked until the pre-implementation architecture gate is accepted. The working web address will be `odeya.danielwahnich.dev`; `odeya.ai` is only a separately tracked apex-domain candidate.

## Architecture verdict

Build a governed scientific kernel with durable typed state and selective agentic intelligence around it—not one immortal agent, an unstructured swarm, or a production system that rewrites itself.

```text
thesis proposal
  -> mission contract
  -> frozen protocol
  -> planned work graph
  -> isolated execution
  -> evidence and artifacts
  -> independent verification
  -> adversarial adjudication
  -> bounded claim/release, valid null, invalidity, or explicit blocker
  -> grounded learning
```

The deterministic kernel owns state transitions, budgets, approvals, lineage, and claim eligibility. Models may propose, search, code, analyze, and criticize; they do not grant themselves authority or turn agreement into truth.

## Why Odeya exists

The engine is being extracted from three active research tracks:

- **Sentinel** tests runtime monitoring and failure localization around a frozen autonomous-driving stack. It contributes disciplined measurement, attribution, and bounded transfer claims.
- **Telos** tests whether benchmark success survives contact with the intended outcome. It contributes external verification, deliberately broken positive controls, and correction discipline.
- **Inbar** studies physical causal evidence and verified intervention. It contributes evidence admissibility, prospective tests, and strict separation of proposal, safety, execution, truth, outcome, and publication authority.

These projects are the proof layer and requirements source. They are not dependencies to merge into the engine, and their current limitations remain visible in [the proof-layer snapshot](docs/PROOF_LAYER.md) and [the exact first-slice fixture specification](docs/FIRST_VERTICAL_SLICE.md).

## Company and repository boundary

Odeya is a separate frontier-research company and product. This repository is independent from Aweb and Maestro in runtime, storage, namespace, control, scientific authority, and release authority. Maestro is a useful protocol and systems reference, but its own committed audit does not establish a working research engine.

The intended boundary is:

- private engine, evaluation suites, control plane, and operating knowledge;
- research papers, datasets, benchmarks, and mission code released only through explicit rights, safety, evidence, and publication gates;
- provider-neutral model, tool, compute, and storage adapters;
- no inherited credentials, databases, routes, or approval shortcuts.

No public repository, company registration, trademark conclusion, or domain acquisition is implied by this local foundation.

## Documents

- [Charter](CHARTER.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Architecture candidate status and blockers](docs/ARCHITECTURE_STATUS.md)
- [Cognitive architecture](docs/COGNITIVE_ARCHITECTURE.md)
- [Cognitive control contracts](docs/COGNITIVE_CONTROL_CONTRACTS.md)
- [Command and event catalog](docs/COMMAND_EVENT_CATALOG.md)
- [Command contract registry](docs/COMMAND_CONTRACT_REGISTRY.md)
- [Reducer registry](docs/REDUCER_REGISTRY.md)
- [Registry graph contracts](docs/REGISTRY_GRAPH_CONTRACTS.md)
- [Engine contract root](docs/ENGINE_CONTRACT_ROOT.md)
- [Research protocol](docs/RESEARCH_PROTOCOL.md)
- [Mathematical constitution](docs/MATHEMATICAL_CONSTITUTION.md)
- [Physical science constitution](docs/PHYSICAL_SCIENCE_CONSTITUTION.md)
- [First-slice scientific method profile](docs/FIRST_SLICE_METHOD_PROFILE.md)
- [First-slice admission closure plan](docs/FIRST_SLICE_ADMISSION_CLOSURE_PLAN.md)
- [Semantic validation constitution](docs/SEMANTIC_VALIDATION.md)
- [Evidence and memory](docs/EVIDENCE_AND_MEMORY.md)
- [Provenance and research-package export profile](docs/PROVENANCE_EXPORT_PROFILE.md)
- [Canonical identity and serialization profile](docs/CANONICALIZATION_PROFILE.md)
- [Standards profile](docs/STANDARDS_PROFILE.md)
- [Evaluation and learning](docs/EVALUATION_AND_LEARNING.md)
- [Security and authority](docs/SECURITY_AND_AUTHORITY.md)
- [Authority and separation matrix](docs/AUTHORITY_MATRIX.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Interface contracts](docs/INTERFACE_CONTRACTS.md)
- [Module ownership and dependency manifest](docs/MODULE_DEPENDENCY_MANIFEST.md)
- [Transaction and recovery model](docs/TRANSACTION_MODEL.md)
- [Ledger integrity, backup, and recovery contract](docs/LEDGER_INTEGRITY_AND_RECOVERY.md)
- [Data governance, rights, and lifecycle contract](docs/DATA_GOVERNANCE.md)
- [Publication protocol](docs/PUBLICATION_PROTOCOL.md)
- [Projection contracts](docs/PROJECTION_CONTRACTS.md)
- [Technology decisions and reversibility](docs/TECHNOLOGY_DECISIONS.md)
- [Orthogonal state model](docs/STATE_MODEL.md)
- [Failure model](docs/FAILURE_MODEL.md)
- [Thesis intake](docs/THESIS_INTAKE.md)
- [UI/UX system](docs/UI_UX.md)
- [Roadmap](docs/ROADMAP.md)
- [Implementation order](docs/IMPLEMENTATION_ORDER.md)
- [Pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md)
- [Independent architecture review protocol](docs/ARCHITECTURE_REVIEW_PROTOCOL.md)
- [Verification protocol](docs/VERIFICATION_PROTOCOL.md)
- [Proof-mission requirements traceability](docs/PROOF_MISSION_REQUIREMENTS_TRACEABILITY.md)
- [Internal architecture red-team findings](docs/INTERNAL_RED_TEAM_FINDINGS_2026-07-15.md)
- [Frontier review, 2026-07-15](docs/FRONTIER_REVIEW_2026-07-15.md)
- [Working Gate A handoff packet](docs/GATE_A_HANDOFF_WORKING_PACKET_2026-07-15.md)
- [Architecture decisions](docs/decisions/README.md)

## Validate

```bash
python3 -m venv .venv-architecture
.venv-architecture/bin/python -m pip install -r requirements-architecture.txt
.venv-architecture/bin/python scripts/validate.py
```

The pinned architecture validator meta-validates every Draft 2020-12 schema, asserts RFC 3339 formats, rejects duplicate JSON members, runs the shared fixture manifest plus the mandatory cognitive, projection, physical, and mathematical contract-family suites, checks local Markdown links, and enforces the implementation lock. A pass is structural and bounded semantic evidence only; it is not Gate A acceptance.

## Near-term milestone

The current milestone is to close [the pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md). Gate A acceptance may authorize only the exact Gate B probes named in the accepted candidate. Runtime product work still requires a later explicit Gate C decision for one bounded vertical slice that replays a settled research cycle from a proof project.

1. compile one canonical mission specification into an immutable run manifest;
2. execute a bounded experiment in an isolated worker;
3. retain exact inputs, environment, costs, and artifacts;
4. recompute its verdict in a separately isolated verifier;
5. render the claim, evidence, uncertainty, nulls, and corrections in a research-native cockpit.

Autonomy expands only after this chain survives negative fixtures, replay, interruption, and independent review.
