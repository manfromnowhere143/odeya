# Odeya

Odeya is the architecture foundation for a private research engine that turns a thesis into a governed, replayable chain from question to evidence to warranted claim.

> **Current state — 2026-07-30:** architecture foundation only. No executable research engine, autonomous-science capability, production deployment, or automatic publication is claimed. Gate A remains blocked; runtime stays prohibited until Gate A is accepted, any separately authorized Gate B probes are settled, and Gate C explicitly authorizes one bounded increment.

The provisional web address is `odeya.danielwahnich.dev`. The apex domain, company, trademark, and scientific-publication decisions remain separate.

## For reviewers: what is proven vs. planned

Much of this repository is written as an internal evidence trail. This table is the external entry point; the [reviewer reading map](docs/INDEX.md) gives the reading order, a glossary, and where each kind of evidence lives.

| Category | What it contains | Where to verify |
| --- | --- | --- |
| **Retained byte-bound release-engineering evidence** | Exact-commit fresh-clone rehearsals that rebuild their named subjects from clean clones; least-privilege CI workflows with full-SHA-pinned Actions; a hash- and integrity-locked toolchain; 7 bounded TLA+ models whose 30 intended counterexamples are retained in-tree; adversarial known-bad manifests beside every isolated suite. Resolve the current candidate and its own manifest before transferring any claim | [`scripts/ci/rehearse-fresh-clone.sh`](scripts/ci/rehearse-fresh-clone.sh), [`.github/workflows/`](.github/workflows/), [`tools/repository-release/`](tools/repository-release/), [`formal/tla/`](formal/tla/), [`tests/`](tests/), [repository release engineering](docs/REPOSITORY_RELEASE.md) |
| **In progress: architecture evidence** | A schema/fixture corpus with isolated contract suites, and a mutation audit that measures which refusal guards are proved to fire versus explicitly unproved — the split is retained honestly rather than rounded up. Counts drift as tranches land, so they are stated only in validator-bound surfaces, not in this summary row | [Current status and blockers](docs/ARCHITECTURE_STATUS.md), the validator-bound checkpoint section below, [`architecture/`](architecture/) machine records |
| **Not built, not claimed** | No engine runtime, services, deployment, or production UI exists; Gate A (architecture acceptance) remains blocked; no scientific result, autonomous-science capability, or model-performance claim is made | The banner above, [pre-implementation gate](docs/PRE_IMPLEMENTATION_GATE.md), [current status](docs/ARCHITECTURE_STATUS.md) |

A green check anywhere in this repository is evidence about these bytes, never scientific truth.

## The system in one view

Question → contract → evidence → separately assigned verification → bounded claim. Nothing jumps the chain.

```mermaid
flowchart TB
    subgraph F["ARCHITECTURE EVIDENCE · PUBLIC LINEAGE + RETAINED FAILED CANDIDATE + CURRENT REPLACEMENT"]
        direction LR
        F4["CLOSED PUBLIC ANCESTOR<br/>d3ec64f3 · exact Git tree and cited blobs checked"]
        F3["SETTLED PUBLIC PRQ-002D PREDECESSOR<br/>617209ba · candidate + main checks passed<br/>remote replay compared equal"]
        F2["FAILED IMMUTABLE PRQ-002E CANDIDATE<br/>f1bb98d · 9/10 jobs passed · no promotion<br/>permanent failed ref and diagnostics retained"]
        F1["CURRENT PRQ-002E REPLACEMENT SIBLING<br/>resolve exact commit · rehearsal · publication · remote status<br/>from Git and subject-bound receipts<br/>no failed-candidate evidence transfers"]
        F4 --> F3
        F3 --> F2
        F3 --> F1
    end

    Q["OPEN ARCHITECTURE DEPENDENCIES<br/>PRQ-002 raw-aware traces + source-separated conformance<br/>PRQ-009 + PRQ-013 + accountable reviews<br/>operator exact-byte decision"]
    GA{"GATE A · BLOCKED<br/>operator architecture acceptance absent<br/>runtime · application · infrastructure<br/>and deployment unauthorized"}
    GB{"GATE B · NOT AUTHORIZED<br/>disposable probes only<br/>each requires separate scope and settlement"}
    GC{"GATE C · NOT REACHED<br/>one bounded implementation increment<br/>requires a separate explicit decision"}
    I["BOUNDED IMPLEMENTATION SLICE<br/>NOT BUILT"]
    F1 --> Q --> GA
    GA -.->|only if separately authorized| GB
    GA -.->|after acceptance + any authorized probes settled| GC
    GB -.->|findings integrated before Gate C| GC
    GC -.->|only after explicit authorization| I

    subgraph R["ODEYA · PRIVATE RESEARCH ENGINE · PROPOSED CONTROL ARCHITECTURE · NOT IMPLEMENTED"]
        direction TB
        C["1 · CONTRACT + 2 · COMPILE<br/>canonical ResearchMissionSpec<br/>thesis · protocol · falsifiers · authority<br/>immutable protocol + compiled run manifest"]
        K[("3 · ISOLATED EXECUTION + 4 · EVIDENCE<br/>search · plan · code · experiment<br/>content-addressed artifacts · claim provenance<br/>CANONICAL SCIENTIFIC STATE<br/>append-only event + evidence ledger · deterministic replay")]
        V["5 · VERIFY + 6 · ADJUDICATE + 7 · LEARN<br/>Separately assigned verification role<br/>separate isolation boundary · independence measured<br/>replication · falsifiers · replay · bounded outcome<br/>RESEARCH COCKPIT · disposable projections<br/>Grounded memory: failure · correction · unknowns<br/>never canonical authority"]
        C --> K --> V
    end

    subgraph X["RELEASE PATH · adjudicated candidate only · one governed external effect · separate from scientific truth"]
        direction LR
        RC["Release candidate"]
        H{"Human release decision<br/>assurance wrapper required<br/>PRQ-013 migration blocked"}
        M["Exact manifest sealed<br/>from candidate + decision"]
        G["Exact single-use grant"]
        E["Bounded external effect"]
        O["Separately authorized observation + reconciliation role<br/>independence measured<br/>reconcile applied · not applied · unknown"]
        N["Retained · not released"]
        RC --> H
        H -->|authorized exact candidate| M --> G --> E --> O
        H -->|denied or no valid decision| N
    end

    F ~~~ R
    R ~~~ X

    classDef retained fill:#ECFDF5,stroke:#047857,stroke-width:1.5px,color:#064E3B
    classDef blocked fill:#9F1239,stroke:#881337,stroke-width:2px,color:#FFFFFF
    classDef candidate fill:#E0F2FE,stroke:#0369A1,stroke-width:2px,color:#0C4A6E
    classDef core fill:#FFFFFF,stroke:#0F172A,stroke-width:1.5px,color:#0F172A
    classDef evidence fill:#E0F2FE,stroke:#0369A1,stroke-width:1.5px,color:#0C4A6E
    classDef state fill:#082F49,stroke:#0369A1,stroke-width:1.5px,color:#FFFFFF
    classDef decision fill:#0F172A,stroke:#0F172A,stroke-width:1.5px,color:#FFFFFF
    classDef release fill:#FFF7ED,stroke:#9A3412,stroke-width:1.5px,color:#7C2D12
    classDef releaseGate fill:#9F1239,stroke:#881337,stroke-width:1.5px,color:#FFFFFF
    classDef quiet fill:#F1F5F9,stroke:#64748B,stroke-width:1px,color:#334155
    class F3,F4 retained
    class F2 blocked
    class F1 candidate
    class GA blocked
    class GB,GC decision
    class Q,I quiet
    class C,V core
    class K state
    class RC,M,G,E,O release
    class H releaseGate
    class N quiet
    style F fill:#F0FDF4,stroke:#047857,stroke-width:2px
    style R fill:#F8FAFC,stroke:#0F172A,stroke-width:2px
    style X fill:#FFFBEB,stroke:#9A3412,stroke-width:2px
```

The evidence band distinguishes the green closed `d3ec64f3` ancestor and
settled public `617209ba` predecessor, the red immutable `f1bb98d` candidate
whose attempt-1 census stopped at 9/10 successful jobs, and the blue current
replacement sibling. A tracked file cannot contain the hash of the commit that
contains it, and rehearsal or external settlement can change after its bytes
are fixed; resolve the exact `HEAD`, tree, local evidence manifest, permanent
release ref, public `main`, and remote replay from Git and subject-bound
receipts before acting. Neither predecessor nor failed-candidate evidence
transfers. The blocked gate prevents architecture bytes from being mistaken
for a built engine. The lower engine is the proposed control architecture, not
a runtime screenshot, and the release path remains separately governed.
Models may propose, search, code, analyze, and criticize. They cannot grant
themselves authority, verify their own claims, convert consensus into evidence,
or treat a provider response as external truth.

## Five operating laws

1. **Contract before cognition.** Scope, protocol, falsifiers, resources, rights, and authority are explicit before consequential work.
2. **Evidence before narrative.** Every claim traverses to exact inputs, artifacts, environments, costs, methods, and producing activity.
3. **Verification is separately assigned.** Producing and verifying a scientific claim require separate roles, contexts, and retained records; organizational independence must be evidenced, never inferred from isolation or agreement.
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

The current retained foundation contains 144 Draft 2020-12 schemas, 908
shared-manifest cases (244 valid and 664 known-bad), 17 isolated contract
suites, 15 architecture-evidence checks, and 7 bounded TLA+ models with
30 mutation controls. These counts are bound to the validator run that
measures them; the README previously stated four of them as fact while all four
had drifted.

The integrated Foundation validator keeps a 30-second fail-fast default for
ordinary child checks. The measured PRQ-002E construction checker is bounded
to 60 seconds, while its predecessor wrapper receives 90 seconds so a nested
60-second child can still emit diagnostics. Six release-surface known-bads
prove those narrow exceptions and their executable function bindings cannot
be lowered, bypassed, rebound, decorated away, or widened into an unreviewed
global relaxation.

Those results establish structural and bounded semantic evidence only, and their
strength is measured by mutation rather than assumed. The lifecycle checker is
audited explicitly: 222 of 229 refusal statements are proved reachable by
disabling each in turn, and 108 of 111 removable guard conditions are proved
load-bearing (ADR 0052–0054, 0065–0066, 0090). Its named residue is retained
rather than converted into a flattering completeness claim.

The separately declared generalized-audit census excludes lifecycle and
central architecture/release gates. Under the retained v0.2 method, a guard is
proved only when a syntax-valid isolated mutation produces an exact
suite-reported refusal—exit 1, non-empty output, and no traceback—the restored
control passes, and an identical repeat produces the same framed SHA-256
fingerprint. In the current record, across 17 declared isolated checker subjects, 501 of 1260 refusal statements are proved to fire, with 759 retained explicitly as unproved and zero crash-only detections;
unstable repeats are also unproved (ADR 0079–0085,
0098–0100, 0103–0104). The `prq-002-identity-cohort` subject contributes 0/127,
`product-identity-profile-candidate` contributes 0/97 with all 97 open, and
`product-identity-profile-0.3-candidate` contributes 24/72 with 48 open.

The immediately preceding unpublished 502/1260 record is superseded: a
clean-clone run exposed a one-credit reproducibility mismatch, and a separate
exact but unretained ablation showed the locally credited predecessor-profile
row was false. The retained failure receipt proves only the failed stage, not
the count or cause. The former 16-subject 477/1184 measurement and its 0/93
`product-identity-profile-candidate` row are likewise superseded because the
registered subject census and checker bytes changed; they are not additional
current denominators. The earlier 431/820 result is retracted: mutation of the
self-bound assurance checker invalidated its outer evidence binding, so the
audit credited that binding failure rather than the intended guard. The
corrected harness refreshes the declared binding only inside each isolated
mutation copy and proves its own unrefreshed/refreshed behavior before
measuring.

Separately, the declared known-bad refusal corpora are checked by a census that
fails closed on any unattributed case (ADR 0062), and each of the 158
predecessor cross-field schema rules with a case is proven to notice its own
deletion by two-sided ablation (ADR 0071–0073). Coverage is still not
correctness: a proved guard is exercised, not shown to enforce the right rule;
the generalized harness does not prove exact case-to-guard causality; structural
comparisons count as one condition regardless of field count; and
[ADR 0030](docs/decisions/0030-statement-coverage-is-not-condition-coverage.md)'s
caution stands. Every coverage figure this repository previously published was
wrong in the flattering direction until context-isolated adversarial review
corrected it, and the corrections are retained.

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
issuance. The separate `odeya-jcs-0.3` construction candidate described below
does not amend or establish conformance for those bytes. No product
identity, PRQ-002 closure, Gate A acceptance, runtime authority, or publication
authority follows from this evidence. Architecture-repository publication
remains separately governed by the exact-commit release contract; profile
issuance and scientific-results publication remain unauthorized.

[ADR 0102](docs/decisions/0102-prove-non-product-prehash-schema-registry-replay.md)
adds a bounded, non-product PRQ-002D prehash replay before any structured or
product identity exists. Two source- and language-separated implementations
evaluate the complete ordered projection for 68 opaque virtual-file frames:
one is accepted and 67 are refused under one fixed private oracle. The parent
gate retains 77 known-bad mutations, each of which must produce its declared
singleton guard, and binds the predecessor commit, tree, cited blobs, runner
sources, locked dependencies, raw inputs, complete results, execution
receipts, and comparison projection by exact bytes. Evidence authoring stages
and validates the complete generated graph before replacing the comparison
receipt last. The receipts remain self-attested byte-consistency records, not
independently witnessed process evidence; the source controls are bounded
inventories, not process sandboxes or general static analyses. The proposition
does not establish canonicalization-profile conformance, complete offline
resolution, dependency-closed product registries, organizational
independence, product identity, admission, PRQ-002 closure, Gate A acceptance,
runtime authority, or publication authority. The frozen `odeya-jcs-0.2` bytes
remain unissued.

[ADR 0103](docs/decisions/0103-construct-side-by-side-odeya-jcs-0-3-candidate.md)
constructs the required side-by-side `odeya-jcs-0.3` architecture candidate:
twelve final-only successor schemas, nine structural-nonidentity fixtures,
three ordered candidate records, and a separate seven-output observation
transaction over the resulting fifteen immutable subjects. Two source- and
language-separated observers agree on the complete exact-byte fifteen-row
projection. That agreement is bounded construction evidence only. It does not
prove the static schema-position inventory, complete per-subject raw-number
applicability traces, canonicalization conformance, complete offline
resolution, organizational independence, product identity, profile or
resource issuance/admission, PRQ-002 closure, Gate A acceptance, runtime
authority, or publication authority.

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

Repository-release checks lint the workflows and Markdown, validate the README
contract, and render all seven governed Mermaid maps from the exact checked-in
blocks across the README and three architecture documents:

```bash
bash scripts/ci/check-repository-release.sh
```

After fetching the digest-verified JAR described in the [formal-model guide](formal/tla/README.md), the bounded models run:

```bash
bash formal/tla/check.sh
```

Which refusal statements have a retained mutation proof is measured rather than assumed. The lifecycle checker has its own dedicated statement and condition audits. The generalized v0.2 audit covers a separate declared checker census; lifecycle is excluded while the PRQ-002E checker is included. It requires a syntax-valid mutation, an exact suite-reported refusal, a passing restored control, and an identical repeated refusal fingerprint. It does not attribute the result to an exact case ID:

```bash
python3 scripts/audit_lifecycle_guard_coverage.py       # lifecycle statements, ~90s
python3 scripts/audit_suite_guard_coverage.py           # declared non-lifecycle checker census; duration varies
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

On 2026-07-30, direct child `617209ba` completed its own candidate and
post-main four-workflow/ten-job censuses, remote-main replay, comparison, and
final ref read-back. Its first PRQ-002E child `f1bb98d` then retained a
permanent candidate ref, but its attempt-1 census stopped at nine of ten
successful jobs. The Foundation job reported two internal child-process
`TimeoutExpired` diagnostics; the workflow and job were not reported as
GitHub timeouts. It was not promoted and has no successful candidate-checks or
remote-main evidence. The current replacement is a new sibling of that failed
candidate, not its descendant, and must generate every subject-bound artifact
again.

## Next

The immediate continuation is deliberately singular. First resolve and
reproduce, and fully settle the current PRQ-002E replacement direct child of
exact published predecessor `617209ba`; never inherit the predecessor's or
failed candidate's receipts. Closure requires its own clean rehearsal; four
attempt-1 candidate workflow runs with ten successful attempt-1 jobs; four
newly created attempt-1 post-main workflow runs with ten successful attempt-1
jobs; remote-main replay and comparison; and a separate final live exact-ref
read-back. Once that exact subject is settled, the next smallest PRQ-002
architecture unit is complete raw-aware, per-subject applicability traces plus
full source-separated cross-object conformance over the frozen
`odeya-jcs-0.3` bytes. Only then proceed to complete offline resolution,
dependency-closed product members and registries, accountable review, and the
operator's exact-byte decision. No observer agreement,
structural vector, or green validator may be promoted into conformance, product
identity, profile issuance, PRQ-002 closure, Gate A acceptance, or runtime
authority.

The canonical-migration wave is closed at audit zero (ADRs 0032–0050): all six blocking finding classes — 1,222 findings in total — now measure zero, every reissue ledgered so each reissued schema's predecessor verifies against its recorded checkpoint commit, and the audit reports `gate_a_disposition: candidate_clear`. The profile nevertheless remains **unissued**: freezing it requires independent review of the executed wave and the operator's exact-byte decision, which no session can grant itself. [ADR 0097](docs/decisions/0097-adversarially-validate-the-canonicalization-evaluator.md) adds a separate meta-evaluator after a copied Python result relabelled with Node metadata passed the existing comparator; retained oracle conformity and case-projection agreement therefore remain distinct from causal execution-origin evidence, which is still unwitnessed. That executed wave was attacked across four rounds of context-isolated adversarial review (ADRs 0051, 0063, 0069, 0077), each briefed to refute; each round found real defects — a fabricated disposition field in the evidence writer, a publication path a plain `git push` bypassed, coverage audits that could regenerate their own records — and each is retracted in place with corrected, re-measured figures. Those reviewers were context-isolated but not independent: they shared the producer's provider, model family, and prompt family, five of the twelve correlation axes `ModelConfigurationRecord` already enumerates, and that is recorded rather than glossed (see the [reviewer-agent proposal](docs/REVIEWER_AGENT_PROPOSAL.md)). The ADR 0095 refutation followed the same discipline. T1 `AuthorityAssignment` is the next PRQ-013 downstream tranche only after the four named T0 prerequisites—canonical schema-identity candidate closure, standalone member-record contracts, PRQ-005 through PRQ-010 candidate corrections, and PRQ-013 individual-assurance-foundation candidate closure—are satisfied. The constitutional root/checkpoint/activation chain, independent reducers and verifiers, replay/recovery/correction-fanout evidence, rights-settled proof import, accountable human reviews, an exact candidate manifest, and the owner's exact-byte decision all remain mandatory before Gate A. The [closure plan](docs/GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md) and [current handoff](docs/SESSION_HANDOFF.md) retain the dependency order and every open limitation.

Only after Gate A acceptance may the operator separately authorize a bounded
Gate B probe. One bounded replayable engine slice remains prohibited until any
authorized probes are settled and the operator makes a separate explicit Gate
C decision.

Any future authority expansion remains blocked until one full chain of custody
survives replay, interruption, negative fixtures, recovery, measured
independence, accountable review, and the operator's exact decision.
