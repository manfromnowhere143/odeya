# Roadmap

The roadmap is gated by retained evidence, not calendar optimism. Each phase earns the authority needed for the next.

## Phase 0 — Founding contract

**Status:** active.

Deliverables:

- independent public architecture repository, private engine boundary, and
  charter;
- architecture, research protocol, authority, memory, evaluation, UI/UX, and thesis-intake specifications;
- typed mission, event, and claim schemas;
- bounded proof-layer snapshot for Sentinel, Telos, and Inbar;
- current frontier research review and explicit architecture decisions;
- no-code mission cockpit information architecture;
- naming, company, trademark, domain, package, and public-release work tracked separately.

Exit evidence:

- documents and schemas validate;
- no project is misrepresented as an implemented engine capability;
- stale proof claims are identified before investor or public use;
- mathematical and statistical semantics are frozen at the kernel/domain boundary;
- the technology-standards matrix distinguishes normative standards from replaceable product choices;
- dependency order, interface contracts, threat model, failure semantics, and evaluation plan survive adversarial review;
- every blocking item in `PRE_IMPLEMENTATION_GATE.md` has retained evidence;
- founding invariants and architecture baseline have explicit operator acceptance.

No runtime, UI application, infrastructure, or deployment implementation begins before this exit gate. The provisional subdomain and optional apex-domain acquisition remain non-blocking company tasks.

## Phase 1 — Replayable evidence vertical slice

Implement the smallest end-to-end kernel on one settled, low-risk cycle from a proof project.

Deliverables:

- `ResearchMissionSpec` compiler and immutable protocol snapshot;
- append-only mission event ledger and reconstructible projections;
- work DAG, leases, attempts, budgets, interruption, and recovery;
- isolated worker and separately isolated verifier;
- content-addressed artifacts and claim-evidence lineage;
- typed adjudication and claim compiler;
- private cockpit rendering supported, null, invalid, blocked, and corrected states.

Exit evidence:

- clean replay reproduces the verdict;
- all known-bad fixtures fail;
- worker death causes neither state loss nor duplicate consequential action;
- unauthorized compute, egress, spend, and release fail closed;
- every rendered claim traverses to exact evidence and verifier identity.

## Phase 2 — Shadow the proof missions

Run Odeya alongside Sentinel, Telos, and Inbar without owning their scientific or execution authority.

Deliverables:

- read-only mission adapters that map committed project state into Odeya contracts;
- contract coverage and mismatch report for all three research styles;
- literature, code, data, simulation, and physical-evidence capability adapters;
- resource curves and comparable single-agent/multi-agent evaluations;
- generated factual handoffs and correction propagation;
- operator workflow study measuring manual toil and missing capabilities.

Exit evidence:

- Odeya reconstructs each mission's current bounded truth without losing its nulls, corrections, or authority distinctions;
- repeated workflows, not architectural preference, justify the first reusable skills;
- no shadow recommendation is mistaken for project authority.

## Phase 3 — Controlled active research

Authorize Odeya to execute bounded computational experiments under frozen protocols while humans retain admission, safety, high-cost, and publication decisions.

Deliverables:

- selective specialist orchestration and one-writer discipline;
- stronger sandboxing, policy gateway, credential broker, and resource circuit breakers;
- private rotating evaluation suites and adversarial integrity tests;
- protocol amendments, replication branches, and publication manifests;
- offline improvement lab with shadow/canary/rollback promotion;
- domain-specific scientific adapters with deterministic oracles where possible.

Exit evidence:

- active missions outperform simpler baselines on validity or information gained per comparable resource—not just output volume;
- independent reviewers reproduce a material sample;
- compute, infrastructure, and grader confounds are measured;
- incident, correction, pause, and revoke paths have been exercised.

## Phase 4 — Prospective testbeds and team scale

Expand to selected aerospace, autonomous-system, or other high-consequence partnerships only with domain-specific safety cases.

Deliverables:

- organization and tenant boundaries;
- external expert and lab/testbed interfaces;
- recipient-scoped sealed truth and independently settled outcomes;
- dual-control authority for irreversible or physical actions;
- reproducible research object export and partner audit;
- portfolio-level scheduling based on information value, cost, risk, and strategic relevance.

Exit evidence:

- at least one prospective outcome is independently settled in each admitted domain;
- safety and publication authorities remain separable under real operational pressure;
- partner value is measured net of compute, labor, delay, and review costs.

## Phase 5 — Human thesis network

Open a controlled contribution surface after the internal engine can reliably admit, replay, reject, correct, and preserve negative outcomes.

Deliverables:

- signed versioned thesis proposals;
- quarantine, prior-art, rights, conflict, safety, and feasibility review;
- transparent accept/defer/decline decisions and revision paths;
- forked mission contracts with contributor credit and access policy;
- reputation used for routing attention, never as a truth signal;
- optional public evidence and replication graph.

Exit evidence:

- contributed proposals cannot bypass evidence, safety, rights, or publication gates;
- acceptance is never presented as scientific endorsement;
- abuse, confidentiality, correction, and withdrawal controls survive adversarial testing.

## Parallel company track

Company building runs beside, not inside, the scientific kernel:

- recruit research engineering, domain science, evaluation, security, product design, and research-operations talent;
- budget both people and compute because reliable research needs expertise, testbeds, evaluation, and infrastructure—not GPU credits alone;
- maintain a corrected proof-layer packet and one-page company narrative;
- complete professional legal and naming clearance before relying on Odeya in a jurisdiction or purchasing identity assets;
- decide licensing mission by mission and keep engine IP/private evaluation assets separate.

The provisional address is `odeya.danielwahnich.dev`. `odeya.ai` was quoted by Vercel at USD 160 for two years on 2026-07-15 and was not purchased.

The public architecture repository was separately authorized and created under
ADR 0047. No outreach, purchase, engine publication, visibility change, or
legal filing is authorized merely by this roadmap.

## Public architecture publication — active and evidence-gated

The canonical public architecture remote already exists at
`https://github.com/manfromnowhere143/odeya`. It contains architecture evidence,
not an implemented engine and not private mission data. Every later
architecture publication remains an exact-commit external operation governed
by [Repository Release Engineering](REPOSITORY_RELEASE.md): clean scope,
fresh-clone rehearsal, retained evidence, guarded fast-forward publication,
observed remote checks, and remote-main reproduction.

The published architecture bytes must retain:

- a short README whose opening sentence says exactly what Odeya is, followed by its current state, explicit non-claims, and the bounded proof relationship to Sentinel, Telos, and Inbar;
- one memorable Mermaid architecture map derived from the accepted contracts and module manifest, with scientific state, authority, evidence, verification, and external-effect boundaries visible rather than decorative;
- required fast pull-request checks plus separately visible exhaustive schema, semantic, adversarial, canonicalization, architecture-evidence, and formal-model checks;
- GitHub Actions pinned to immutable revisions, least-privilege token
  permissions, explicit concurrency and timeout limits, retained failure
  evidence, and no secret-bearing untrusted execution; once separately
  authorized and configured, a server-side ruleset must require the observed
  check contexts before they may be called protected;
- security and supply-chain checks appropriate to the implemented stack, enabled when their subject actually exists rather than claimed in advance;
- a fresh-clone rehearsal proving that the README commands, Mermaid rendering, validation environment, and required checks reproduce without local hidden state.

The public remote currently has no server-side `main` ruleset, so the local
pre-push hook cannot be described as branch protection. A ruleset is the next
repository-governance operation and must be separately configured and observed.
A successful architecture publication does not authorize product deployment,
research publication, domain purchase, outreach, or runtime execution.

## What is deliberately deferred

- production recursive self-modification;
- an unstructured always-on swarm;
- automatic publication;
- general command authority over vehicles, labs, capital, or critical systems;
- a graph database, Kubernetes fleet, WebGPU interface, or many microservices without measured need;
- automatic global absorption of every accepted thesis.

The fastest credible path is depth first: one complete scientific chain of custody, then wider autonomy.
