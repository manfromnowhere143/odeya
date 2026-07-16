# Odeya

Odeya is a private research engine that turns a thesis into a governed, replayable chain from question to evidence to warranted claim.

> **Current state — 2026-07-16:** architecture foundation only. No executable research engine, autonomous-science capability, production deployment, or automatic publication is claimed. Runtime work remains blocked until the architecture gates are accepted.

The provisional web address is `odeya.danielwahnich.dev`. The apex domain, company, trademark, and public-release decisions remain separate.

## The system in one view

Question → contract → evidence → independent verification → bounded claim. Nothing jumps the chain.

```mermaid
flowchart TB
    subgraph R["ODEYA · PRIVATE RESEARCH ENGINE"]
        direction LR
        C["1 · CONTRACT<br/>thesis · frozen protocol<br/>authority · rights · budget"]
        W["2 · EXPLORE<br/>search · plan · code<br/>experiment · critique"]
        E["3 · EVIDENCE<br/>inputs · artifacts<br/>environment · cost · lineage"]
        K[("CANONICAL SCIENTIFIC STATE<br/>append-only event + evidence ledger<br/>deterministic replay")]
        V["4 · VERIFY<br/>Independent verification<br/>replication · falsifiers · replay"]
        D["5 · ADJUDICATE<br/>rule-bound bounded outcome"]
        L["6 · LEARN<br/>Grounded memory<br/>transfer · failure · unknowns"]
        C --> W --> E --> K --> V --> D -->|every outcome| L
    end

    subgraph X["RELEASE PATH · adjudicated candidate only · one governed external effect · separate from scientific truth"]
        direction LR
        RC["Release candidate"]
        H{"Human release decision"}
        G["Exact single-use grant"]
        O["Bounded external effect"]
        S["Independent observation<br/>applied · not applied · unknown"]
        N["Retained · not released"]
        RC --> H
        H -->|authorized| G --> O --> S
        H -->|denied| N
    end

    R ~~~ X

    classDef core fill:#FFFFFF,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
    classDef evidence fill:#E0F2FE,stroke:#0369A1,stroke-width:1.5px,color:#0C4A6E
    classDef state fill:#082F49,stroke:#0369A1,stroke-width:1.5px,color:#FFFFFF
    classDef decision fill:#0F172A,stroke:#0F172A,stroke-width:1.5px,color:#FFFFFF
    classDef release fill:#FFF7ED,stroke:#9A3412,stroke-width:1.5px,color:#7C2D12
    classDef releaseGate fill:#9F1239,stroke:#881337,stroke-width:1.5px,color:#FFFFFF
    classDef quiet fill:#F1F5F9,stroke:#64748B,stroke-width:1px,color:#334155
    class C,W,V,L core
    class E evidence
    class K state
    class D decision
    class RC,G,O,S release
    class H releaseGate
    class N quiet
    style R fill:#F8FAFC,stroke:#0F172A,stroke-width:2px
    style X fill:#FFFBEB,stroke:#9A3412,stroke-width:2px
```

This is the intended control architecture, not a runtime screenshot. Models may propose, search, code, analyze, and criticize. They cannot grant themselves authority, verify their own claims, convert consensus into evidence, or treat a provider response as external truth.

## Five operating laws

1. **Contract before cognition.** Scope, protocol, falsifiers, resources, rights, and authority are explicit before consequential work.
2. **Evidence before narrative.** Every claim traverses to exact inputs, artifacts, environments, costs, methods, and producing activity.
3. **Verification is independent.** Producing and verifying a scientific claim are separate roles, contexts, and retained records.
4. **Nulls and failures are first-class results.** Missing is never zero; blocked, invalid, contradicted, and inconclusive outcomes remain visible.
5. **Every external effect is separately governed.** Publication, repository writes, paid compute, messages, lab actions, and physical actions require exact scoped authority and independent settlement.

## Proof layer

Odeya is being extracted from three active research tracks rather than invented from an abstract agent demo:

| Mission | What it contributes |
| --- | --- |
| **Sentinel** | Measurement discipline, runtime monitoring, failure localization, and bounded transfer claims around autonomous-driving systems |
| **Telos** | External verification, deliberately broken positive controls, correction discipline, and tests of whether benchmark success survives contact with the intended outcome |
| **Inbar** | Physical causal evidence, prospective intervention tests, evidence admissibility, and separation of proposal, safety, execution, truth, outcome, and publication authority |

They are requirements sources and bounded proof missions—not runtime dependencies and not proof that Odeya is already implemented. Their exact role and current limitations are retained in the [proof-layer snapshot](docs/PROOF_LAYER.md).

## Architecture checkpoint

The current retained foundation contains 103 Draft 2020-12 schemas, 620 valid/adversarial cases, nine isolated contract suites, two architecture-evidence checks, and seven bounded safe TLA+ models with thirty mutation controls. These results establish structural and bounded semantic evidence only. [Gate A remains blocked](docs/ARCHITECTURE_STATUS.md), and its accountable review and operator decision have not occurred.

The architecture is a modular scientific kernel with isolated cognitive workers around it:

- deterministic state, authority, budgets, lineage, and claim eligibility in the kernel;
- selective model and tool intelligence behind typed work contracts;
- content-addressed evidence and replayable event history;
- separately isolated verification and adversarial adjudication;
- explicit recovery, correction, publication, and external-effect protocols; and
- provider-neutral ports, with infrastructure kept outside scientific meaning.

## Repository boundary

Odeya is independent from Aweb and Maestro in runtime, storage, namespace, control, scientific authority, and release authority. The intended boundary is a private engine, private evaluation suites, and private operating knowledge. Papers, datasets, benchmarks, and mission code may be released mission by mission only through explicit rights, safety, evidence, and publication gates.

No license, domain purchase, company filing, outreach, product deployment, or public-repository decision is implied by this architecture repository.

## Read the architecture

- [Charter](CHARTER.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Current status and blockers](docs/ARCHITECTURE_STATUS.md)
- [Pre-implementation gates](docs/PRE_IMPLEMENTATION_GATE.md)
- [Research protocol](docs/RESEARCH_PROTOCOL.md)
- [Mathematical constitution](docs/MATHEMATICAL_CONSTITUTION.md)
- [Physical-science constitution](docs/PHYSICAL_SCIENCE_CONSTITUTION.md)
- [Security and authority](docs/SECURITY_AND_AUTHORITY.md)
- [Canonical identity and serialization profile](docs/CANONICALIZATION_PROFILE.md)
- [Module ownership and dependency manifest](docs/MODULE_DEPENDENCY_MANIFEST.md)
- [Architecture review protocol](docs/ARCHITECTURE_REVIEW_PROTOCOL.md)
- [Repository release engineering](docs/REPOSITORY_RELEASE.md)
- [Roadmap](docs/ROADMAP.md)

## Reproduce the checkpoint

The architecture validator runs without a development server:

```bash
python3 -m venv .venv-architecture
.venv-architecture/bin/python -m pip install \
  --require-hashes \
  --only-binary=:all: \
  --requirement tools/repository-release/requirements-architecture.lock
.venv-architecture/bin/python scripts/validate.py
```

Repository-release checks lint the workflows and Markdown, validate the README contract, and render the Mermaid map from the exact checked-in block:

```bash
bash scripts/ci/check-repository-release.sh
```

After fetching the digest-verified JAR described in the [formal-model guide](formal/tla/README.md), the bounded models run:

```bash
bash formal/tla/check.sh
```

See [repository release engineering](docs/REPOSITORY_RELEASE.md) for the exact CI jobs, threat boundary, toolchain pins, and fresh-clone rehearsal. A green check is evidence about this repository snapshot; it is never scientific truth or Gate A acceptance.

## Next

The exact canonical-profile parameters, nonrecursive WorkIntent core, and side-by-side WorkIntent 0.2 / canonical WorkLease 0.2 / WorkContract 0.3 successor cohort are machine-bound without issuing any canonical identity. WorkIntent 0.3 now replaces its three placeholder reference values with exact raw ResearchStateView/PlanningEpoch candidates and exact CandidateArtifact schema bytes, while explicitly keeping raw lineage distinct from canonical identity. Every predecessor remains resolvable; target and WorkIntent canonical digests, profile admission, and authority remain absent. The next architecture mission closes or versions the canonical migration findings, obtains profile acceptance, reissues profile-bound target identities, and only then constructs canonical members and the verification-assignment cohort. T1 AuthorityAssignment, the command/event/state/reducer graph, constitutional root/checkpoint/activation chain, independent reducers/verifiers, replay/recovery/correction-fanout evidence, rights-settled proof import, accountable reviews, exact candidate manifest, and Daniel’s exact-byte decision remain mandatory before Gate A. The [closure plan](docs/GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md) and [current handoff](docs/SESSION_HANDOFF.md) retain the dependency order and open limitations.

Only an accepted Gate A candidate can authorize disposable Gate B probes; one bounded replayable engine slice begins only after a separate Gate C decision.

Autonomy expands after one full chain of custody survives replay, interruption, negative fixtures, recovery, and independent review—not before.
