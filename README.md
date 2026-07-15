# Odeya

Odeya is a private, evidence-native operating system for frontier research. Its purpose is to turn a thesis into a bounded, replayable research mission whose claims can be traced to preregistered tests, exact artifacts, independent verification, and explicit authority.

> Current state, 2026-07-15: architecture foundation only. This repository does not yet contain an executable research engine and makes no claim of autonomous science.

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
  -> bounded publication or explicit null/failure
  -> grounded learning
```

The deterministic kernel owns state transitions, budgets, approvals, lineage, and claim eligibility. Models may propose, search, code, analyze, and criticize; they do not grant themselves authority or turn agreement into truth.

## Why Odeya exists

The engine is being extracted from three active research tracks:

- **Sentinel** tests runtime monitoring and failure localization around a frozen autonomous-driving stack. It contributes disciplined measurement, attribution, and bounded transfer claims.
- **Telos** tests whether benchmark success survives contact with the intended outcome. It contributes external verification, deliberately broken positive controls, and correction discipline.
- **Inbar** studies physical causal evidence and verified intervention. It contributes evidence admissibility, prospective tests, and strict separation of proposal, safety, execution, truth, outcome, and publication authority.

These projects are the proof layer and requirements source. They are not dependencies to merge into the engine, and their current limitations remain visible in [the proof-layer snapshot](docs/PROOF_LAYER.md).

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
- [Command and event catalog](docs/COMMAND_EVENT_CATALOG.md)
- [Research protocol](docs/RESEARCH_PROTOCOL.md)
- [Mathematical constitution](docs/MATHEMATICAL_CONSTITUTION.md)
- [Physical science constitution](docs/PHYSICAL_SCIENCE_CONSTITUTION.md)
- [Semantic validation constitution](docs/SEMANTIC_VALIDATION.md)
- [Evidence and memory](docs/EVIDENCE_AND_MEMORY.md)
- [Standards profile](docs/STANDARDS_PROFILE.md)
- [Evaluation and learning](docs/EVALUATION_AND_LEARNING.md)
- [Security and authority](docs/SECURITY_AND_AUTHORITY.md)
- [Authority and separation matrix](docs/AUTHORITY_MATRIX.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Interface contracts](docs/INTERFACE_CONTRACTS.md)
- [Transaction and recovery model](docs/TRANSACTION_MODEL.md)
- [Technology decisions and reversibility](docs/TECHNOLOGY_DECISIONS.md)
- [Orthogonal state model](docs/STATE_MODEL.md)
- [Failure model](docs/FAILURE_MODEL.md)
- [Thesis intake](docs/THESIS_INTAKE.md)
- [UI/UX system](docs/UI_UX.md)
- [Roadmap](docs/ROADMAP.md)
- [Implementation order](docs/IMPLEMENTATION_ORDER.md)
- [Pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md)
- [Frontier review, 2026-07-15](docs/FRONTIER_REVIEW_2026-07-15.md)
- [Architecture decisions](docs/decisions/README.md)

## Validate

```bash
python3 -m venv .venv-architecture
.venv-architecture/bin/python -m pip install -r requirements-architecture.txt
.venv-architecture/bin/python scripts/validate.py
```

The pinned architecture validator meta-validates every Draft 2020-12 schema, asserts RFC 3339 formats, rejects duplicate JSON members, runs registered valid/adversarial fixtures, checks local Markdown links, and enforces the implementation lock. A pass is structural evidence only; it is not Gate A acceptance.

## Near-term milestone

The current milestone is to close [the pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md). Only after that acceptance may the first executable milestone begin: one vertical slice that replays a settled research cycle from a proof project.

1. compile one canonical mission specification into an immutable run manifest;
2. execute a bounded experiment in an isolated worker;
3. retain exact inputs, environment, costs, and artifacts;
4. recompute its verdict in a separately isolated verifier;
5. render the claim, evidence, uncertainty, nulls, and corrections in a research-native cockpit.

Autonomy expands only after this chain survives negative fixtures, replay, interruption, and independent review.
