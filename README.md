# Odeya

Odeya is a private research engine that turns a thesis into a governed, replayable chain from question to evidence to warranted claim.

> **Current state — 2026-07-28:** architecture foundation only. No executable research engine, autonomous-science capability, production deployment, or automatic publication is claimed. Runtime work remains blocked until the architecture gates are accepted.

The provisional web address is `odeya.danielwahnich.dev`. The apex domain, company, trademark, and scientific-publication decisions remain separate.

## For reviewers: what is proven vs. planned

Much of this repository is written as an internal evidence trail. This table is the external entry point; the [reviewer reading map](docs/INDEX.md) gives the reading order, a glossary, and where each kind of evidence lives.

| Category | What it contains | Where to verify |
| --- | --- | --- |
| **Proven from bytes: release engineering** | An exact-commit fresh-clone rehearsal that rebuilds the checkpoint from a clean clone; least-privilege CI workflows with full-SHA-pinned Actions; a hash- and integrity-locked toolchain; 7 bounded TLA+ models whose 30 intended counterexamples are retained in-tree; adversarial known-bad manifests beside every isolated suite | [`scripts/ci/rehearse-fresh-clone.sh`](scripts/ci/rehearse-fresh-clone.sh), [`.github/workflows/`](.github/workflows/), [`tools/repository-release/`](tools/repository-release/), [`formal/tla/`](formal/tla/), [`tests/`](tests/), [repository release engineering](docs/REPOSITORY_RELEASE.md) |
| **In progress: architecture evidence** | A schema/fixture corpus with isolated contract suites, and a mutation audit that measures which refusal guards are proved to fire versus explicitly unproved — the split is retained honestly rather than rounded up. Counts drift as tranches land, so they are stated only in validator-bound surfaces, not here | [Current status and blockers](docs/ARCHITECTURE_STATUS.md), the validator-bound checkpoint section below, [`architecture/`](architecture/) machine records |
| **Not built, not claimed** | No engine runtime, services, deployment, or production UI exists; Gate A (architecture acceptance) remains blocked; no scientific result, autonomous-science capability, or model-performance claim is made | The banner above, [pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md), [current status](docs/ARCHITECTURE_STATUS.md) |

A green check anywhere in this repository is evidence about these bytes, never scientific truth.

## The system in one view

Question → contract → evidence → independent verification → bounded claim. Nothing jumps the chain.

```mermaid
flowchart TB
    subgraph F["ARCHITECTURE EVIDENCE · PUBLISHED PREDECESSOR + CURRENT RELEASE SUBJECT"]
        direction LR
        F4["PUBLISHED PREDECESSOR<br/>a79d86b release foundation<br/>remotely replayed"]
        F1["CURRENT PRQ-002C RELEASE SUBJECT<br/>one direct-child commit · locally rehearsed at closeout<br/>132 schemas · 884 cases<br/>16 suites · 13 evidence checks<br/>7 TLA+ models · 30 controls<br/>remote settlement resolved externally<br/>PRQ-009 / PRQ-013 blocked"]
        F4 --> F1
    end

    GA{"GATE A · BLOCKED<br/>operator architecture acceptance absent<br/>runtime · application · infrastructure<br/>and deployment unauthorized"}
    F1 --> GA

    subgraph R["ODEYA · PRIVATE RESEARCH ENGINE · PROPOSED CONTROL ARCHITECTURE · NOT IMPLEMENTED"]
        direction TB
        C["1 · CONTRACT + 2 · COMPILE<br/>canonical ResearchMissionSpec<br/>thesis · protocol · falsifiers · authority<br/>immutable protocol + compiled run manifest"]
        K[("3 · ISOLATED EXECUTION + 4 · EVIDENCE<br/>search · plan · code · experiment<br/>content-addressed artifacts · claim provenance<br/>CANONICAL SCIENTIFIC STATE<br/>append-only event + evidence ledger · deterministic replay")]
        V["5 · VERIFY + 6 · ADJUDICATE + 7 · LEARN<br/>Independent verification in a separate isolation boundary<br/>replication · falsifiers · replay · bounded outcome<br/>RESEARCH COCKPIT · disposable projections<br/>Grounded memory: failure · correction · unknowns<br/>never canonical authority"]
        C --> K --> V
    end

    subgraph X["RELEASE PATH · adjudicated candidate only · one governed external effect · separate from scientific truth"]
        direction LR
        RC["Release candidate"]
        H{"Human release decision<br/>assurance wrapper required<br/>PRQ-013 migration blocked"}
        G["Exact single-use grant<br/>→ bounded external effect<br/>→ Independent observation<br/>applied · not applied · unknown"]
        N["Retained · not released"]
        RC --> H
        H -->|authorized| G
        H -->|denied| N
    end

    GA -.-> C
    R ~~~ X

    classDef retained fill:#ECFDF5,stroke:#047857,stroke-width:1.5px,color:#064E3B
    classDef blocked fill:#9F1239,stroke:#881337,stroke-width:2px,color:#FFFFFF
    classDef core fill:#FFFFFF,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
    classDef evidence fill:#E0F2FE,stroke:#0369A1,stroke-width:1.5px,color:#0C4A6E
    classDef state fill:#082F49,stroke:#0369A1,stroke-width:1.5px,color:#FFFFFF
    classDef decision fill:#0F172A,stroke:#0F172A,stroke-width:1.5px,color:#FFFFFF
    classDef release fill:#FFF7ED,stroke:#9A3412,stroke-width:1.5px,color:#7C2D12
    classDef releaseGate fill:#9F1239,stroke:#881337,stroke-width:1.5px,color:#FFFFFF
    classDef quiet fill:#F1F5F9,stroke:#64748B,stroke-width:1px,color:#334155
    class F1,F4 retained
    class GA blocked
    class C,V core
    class K state
    class RC,G release
    class H releaseGate
    class N quiet
    style F fill:#F0FDF4,stroke:#047857,stroke-width:2px
    style R fill:#F8FAFC,stroke:#0F172A,stroke-width:2px
    style X fill:#FFFBEB,stroke:#9A3412,stroke-width:2px
```

The green band distinguishes the published `a79d86b` predecessor from the
current one-direct-child PRQ-002C release subject. At this 2026-07-28 closeout
the subject is committed and locally fresh-clone rehearsed. A tracked file
cannot contain the hash of the commit that contains it, and external settlement
can change after its bytes are fixed; resolve the exact `HEAD`, tree, local
evidence manifest, permanent release ref, public `main`, and remote replay from
Git and subject-bound external receipts before acting. The blocked gate
prevents architecture bytes from being mistaken for a built engine. The lower
engine is the proposed control architecture, not a runtime screenshot, and the
release path remains separately governed. Models may propose, search, code,
analyze, and criticize. They cannot grant themselves authority, verify their
own claims, convert consensus into evidence, or treat a provider response as
external truth.

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

The current retained foundation contains 132 Draft 2020-12 schemas, 884
shared-manifest cases (232 valid and 652 known-bad), 16 isolated contract
suites, 13 architecture-evidence checks, and 7 bounded safe TLA+ models with
30 mutation controls. These counts are bound to the validator run that
measures them; the README previously stated four of them as fact while all four
had drifted.

Those results establish structural and bounded semantic evidence only, and their strength is measured by mutation rather than assumed. The lifecycle checker is audited explicitly: 222 of 229 refusal statements are proved reachable by disabling each in turn, and 108 of 111 removable guard conditions are proved load-bearing (ADR 0052–0054, 0065–0066, 0090); the named residue is retained rather than converted into a flattering completeness claim. That discipline was then generalized to every suite: across 16 declared isolated checker subjects, 477 of 1184 refusal statements are proved to fire, with 707 retained explicitly as unproved and zero crash-only detections (ADR 0079–0085, 0098–0100). The `prq-002-identity-cohort` subject contributes 0/127 and the new `product-identity-profile-candidate` subject contributes 0/93: both enumerated refusal denominators under the retained discovery grammar are measured, and none of those statements is yet credited with a retained mutation proof. The earlier 431/820 result is retracted: mutation of the self-bound assurance checker invalidated its outer evidence binding, so the audit credited that binding failure rather than the intended guard; the corrected harness refreshes the declared binding only inside each isolated mutation copy and proves its own unrefreshed/refreshed behavior before measuring. Every refusal-attribution claim is checked by a census that fails closed on any unattributed corpus (ADR 0062), and each of the 158 predecessor cross-field schema rules with a case is proven to notice its own deletion by two-sided ablation (ADR 0071–0073). Coverage is still not correctness: a proved guard is exercised, not shown to enforce the right rule, structural comparisons count as one condition regardless of field count, and [ADR 0030](docs/decisions/0030-statement-coverage-is-not-condition-coverage.md)'s caution stands — every coverage figure this repository ever published was wrong in the flattering direction until context-isolated adversarial review corrected it, and the corrections are retained.

[ADR 0099](docs/decisions/0099-freeze-prq-002a-structural-identity-probe-layer.md)
adds a bounded PRQ-002A structural probe without changing the 120-product-schema
census: nine architecture-only schemas describe 21 non-issuable probe objects
and 20 structured digests. Its isolated suite retains 47 cases—one safe and 46
known-bad—and two source- and language-separated result documents whose current
recomputation path is provenance-attested. This is not independence, issuance,
PRQ-002 closure, an `EngineContractRoot`, activation, runtime, or Gate A
evidence; the probe identifiers cannot be promoted into product identities.

[ADR 0100](docs/decisions/0100-introduce-an-unissued-scoped-product-identity-profile-successor.md)
adds a separate PRQ-002B successor candidate: four standalone product-member
schemas, one ordered-map commitment schema, four pure-registry successor
schemas, and three schemas for an explicitly scoped `odeya-jcs-0.2`
core/evidence/migration chain. The nine product-identity schemas have nine
distinct domain contracts. Exact current bytes and the frozen 120-schema
predecessor cohort reconcile to a disjoint 132-schema candidate union; the
predecessor audit remains frozen at 120 schemas and 216 fixtures. The retained
structural vectors are explicitly nonidentity fixtures. No product member,
commitment, snapshot, canonical digest, profile member, root, or activation was
constructed; both profiles remain unissued, PRQ-002 remains open, Gate A
remains blocked, and runtime remains unauthorized.

[ADR 0101](docs/decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md)
records the PRQ-002C interoperability blocker and one bounded observation of
the proposed raw-token rule. Two source- and language-separated implementations
agree on the complete staged projection for 61 opaque, answer-free synthetic
integer-position frames: 9 are accepted and 52 are refused, and 44
suite-gate known-bads fire. The input, implementation, and execution artifacts
are generation `.0003`; the corrected comparison is `.0004` and the corrected
expectation manifest is `.0005`. The execution receipts are fresh-challenge,
self-attested byte-consistency records, not independently witnessed historical
process captures. The stale implementation-causal-binding gate refuses an
inconsistent relabel only; it does not prove refusal of a coherently relabelled
copy or causal execution origin. The 44 gate attacks exercise exact JSON types
and shapes, strict parsing, suite inventory, dependency and source-import
boundaries, timestamps, comparison, scope, independence, attestation, and
authority; they are not semantic-branch source ablations. This is evidence
only for the fixed integer-type and
integer-valued-const microframes. It does not establish generic schema-path
evaluation, number-position semantics, unique instance-pointer retention,
exclusion of dynamically discovered paths, nine-domain framing, ordered-map
laws, cross-object replay, an offline registry, organizational independence,
independent-host reproduction, or full successor-profile conformance. The
frozen `odeya-jcs-0.2` bytes remain unissued and blocked from conformance and
issuance; the prospective `odeya-jcs-0.3` profile does not exist. No product
identity, PRQ-002 closure, Gate A acceptance, runtime authority, or publication
authority follows from this evidence. Architecture-repository publication
remains separately governed by the exact-commit release contract; profile
issuance and scientific-results publication remain unauthorized.

The PRQ-013 T0 byte-bound/recomputation tranche now retains candidate evidence
under [ADR 0095](docs/decisions/0095-reissue-human-decision-assurance-as-a-byte-bound-independently-recomputed-chain.md):
five unissued successor schemas, seven schema-valid fixtures, 14
content-addressed synthetic backing preimages independently rederived from
their retained bytes, 44 expectation-free vectors, and 49 downstream chain
known-bads. Three
source-separated, non-sharing evaluators produced 132 exact recomputations
(44 each under Python 3.14.2, Node.js 24.18.0, and Temurin Java 21.0.9), and
the comparison binds all six output fields: `participant_id`,
`domain_results`, `categorical_results`, `categorical_failures`,
`final_disposition`, and `reason_codes`. Any fixed times in this evidence are
deterministic fixture times only.
This is stronger bounded defect-detection evidence, not organizational
independence: the implementations share the normative contracts and this work
has not proved organizationally independent authorship or review.

The 0.1 resources remain immutable and unissued, and every successor is also
unissued. The retained eleven-round, context-isolated technical-review report
records `no_grounded_refutation_observed_within_declared_attacks` for the exact
reissued scope only: round eleven reproduced the Gate and generator local Git
readers, corrected PRQ-013 truth bindings, closure, install, cross-runtime, and
full-integration controls. The reissued scope `.0005` is rooted
at `sha256:97062b38a14d5bdccf5ad87c547c62388e7cd82256a445f631856aecee54e1d9`;
closure observation `.0003`, install observation `.0004`, 25 context-review
known-bads including a live generator-path control, and two integration-truth
controls survived only the declared round-eleven checks. The report is
correlated, non-accountable model-worker evidence—not a
`ReviewDetermination`, organizational independence, or Gate A acceptance—and
all `HDA-CTX-001` through `HDA-CTX-016` findings remain pending accountable
closure review.
No real ceremony occurred, no current consumer is migrated, and no T1/T2,
wrapper, end-to-end consumer refusal, accountable review, or operator Gate A
decision is complete. [Gate A remains blocked](docs/ARCHITECTURE_STATUS.md),
with no runtime, cloud, or deployment authority.

The architecture is a modular scientific kernel with isolated cognitive workers around it:

- deterministic state, authority, budgets, lineage, and claim eligibility in the kernel;
- selective model and tool intelligence behind typed work contracts;
- content-addressed evidence and replayable event history;
- separately isolated verification and adversarial adjudication;
- explicit recovery, correction, publication, and external-effect protocols; and
- provider-neutral ports, with infrastructure kept outside scientific meaning.

## Repository boundary

Odeya is independent from Aweb and Maestro in runtime, storage, namespace, control, scientific authority, and release authority. The intended boundary is a private engine, private evaluation suites, and private operating knowledge. Papers, datasets, benchmarks, and mission code may be released mission by mission only through explicit rights, safety, evidence, and publication gates.

This architecture repository is licensed under the [Apache License 2.0](LICENSE); see [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md) for how to engage with it. No domain purchase, company filing, outreach, or product deployment is implied, and runtime, release, and Gate A authority remain exclusively with the repository owner.

## Read the architecture

- [Charter](CHARTER.md)
- [System architecture](docs/ARCHITECTURE.md)
- [Current status and blockers](docs/ARCHITECTURE_STATUS.md)
- [Pre-implementation gates](docs/PRE_IMPLEMENTATION_GATE.md)
- [Research protocol](docs/RESEARCH_PROTOCOL.md)
- [Mathematical constitution](docs/MATHEMATICAL_CONSTITUTION.md)
- [Physical-science constitution](docs/PHYSICAL_SCIENCE_CONSTITUTION.md)
- [Security and authority](docs/SECURITY_AND_AUTHORITY.md)
- [Human decision assurance](docs/HUMAN_DECISION_ASSURANCE.md)
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

Which guards have a known-bad proof is measured rather than assumed. The lifecycle checker has its own dedicated statement and condition audits, and every other suite is measured by one generalized audit; both disable each refusal in turn and re-run:

```bash
python3 scripts/audit_lifecycle_guard_coverage.py       # lifecycle statements, ~90s
python3 scripts/audit_suite_guard_coverage.py           # every other suite; duration is machine- and corpus-dependent
```

See [repository release engineering](docs/REPOSITORY_RELEASE.md) for the exact CI jobs, threat boundary, toolchain pins, and fresh-clone rehearsal. A green check is evidence about this repository snapshot; it is never scientific truth or Gate A acceptance.

Repository-governance bootstrap and the first exact-SHA activation were
observed on 2026-07-19. Bootstrap candidate
`a25d026bd7233dfc452accc6087ded0bf015d7b4` remains at its permanent release
ref. Distinct post-account-state candidate
`f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e` then passed all four workflows
and ten jobs at its permanent release ref, was same-SHA promoted to `main`,
passed four new post-main workflows and ten jobs, reproduced from remote
`main`, compared equal by the admitted invariant profile, and settled the
read-only activation receipt. GitHub read-back observed active no-bypass
release and `main` rulesets (IDs `19178198` and `19178503`), disabled pull
requests, the inert rebase-only merge configuration, full-SHA Action admission,
and read-only workflow tokens. The controls remain active but must be freshly
read back for every publication; no descendant inherits `f1f25fd`'s
subject-bound checks, replay, comparison, or activation receipt. None grants
Gate A or runtime authority.

## Next

The canonical-migration wave is closed at audit zero (ADRs 0032–0050): all six blocking finding classes — 1,222 findings in total — now measure zero, every reissue ledgered so each reissued schema's predecessor verifies against its recorded checkpoint commit, and the audit reports `gate_a_disposition: candidate_clear`. The profile nevertheless remains **unissued**: freezing it requires independent review of the executed wave and the operator's exact-byte decision, which no session can grant itself. [ADR 0097](docs/decisions/0097-adversarially-validate-the-canonicalization-evaluator.md) adds a separate meta-evaluator after a copied Python result relabelled with Node metadata passed the existing comparator; retained oracle conformity and case-projection agreement therefore remain distinct from causal execution-origin evidence, which is still unwitnessed. That executed wave was attacked across four rounds of context-isolated adversarial review (ADRs 0051, 0063, 0069, 0077), each briefed to refute; each round found real defects — a fabricated disposition field in the evidence writer, a publication path a plain `git push` bypassed, coverage audits that could regenerate their own records — and each is retracted in place with corrected, re-measured figures. Those reviewers were context-isolated but not independent: they shared the producer's provider, model family, and prompt family, five of the twelve correlation axes `ModelConfigurationRecord` already enumerates, and that is recorded rather than glossed (see the [reviewer-agent proposal](docs/REVIEWER_AGENT_PROPOSAL.md)). The ADR 0095 refutation followed the same discipline. T1 `AuthorityAssignment` is the next PRQ-013 downstream tranche only after the four named T0 prerequisites—canonical schema-identity candidate closure, standalone member-record contracts, PRQ-005 through PRQ-010 candidate corrections, and PRQ-013 individual-assurance-foundation candidate closure—are satisfied. The constitutional root/checkpoint/activation chain, independent reducers and verifiers, replay/recovery/correction-fanout evidence, rights-settled proof import, accountable human reviews, an exact candidate manifest, and the owner's exact-byte decision all remain mandatory before Gate A. The [closure plan](docs/GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md) and [current handoff](docs/SESSION_HANDOFF.md) retain the dependency order and every open limitation.

Only an accepted Gate A candidate can authorize disposable Gate B probes; one bounded replayable engine slice begins only after a separate Gate C decision.

Autonomy expands after one full chain of custody survives replay, interruption, negative fixtures, recovery, and independent review—not before.
