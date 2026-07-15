# Frontier Research Systems Review

Date: 2026-07-15. Scope: architecture evidence relevant to Odeya, prioritizing primary papers, engineering reports, specifications, and benchmark owners. Product behavior and benchmarks will change; re-verify before using this review as a current market claim.

## Executive verdict

No cited system establishes reliable, general, fully autonomous science. The strongest current systems succeed in bounded settings with human framing, executable objectives, deterministic tools, expert review, or physical-lab partners.

The defensible Odeya design is therefore:

> A governed, event-sourced scientific operating system with a central durable supervisor, typed research state, selective parallel specialists, isolated execution, independent deterministic verification, and claim-level provenance.

The evidence argues against one immortal chat context, an unstructured agent swarm, model consensus as truth, and production recursive self-modification.

## Evidence map

| Area | What current evidence supports | Odeya consequence |
|---|---|---|
| Orchestration | Supervisor/subagent systems help parallel breadth but cost much more and can harm sequential work | Central mission supervisor; selective parallelism; one writer per mutable stage |
| Long horizons | Durable logs, checkpoints, progress artifacts, clean context resets, budgets, and stopping conditions | Session is durable state, not a context window |
| Scientific reasoning | Multi-agent hypothesis generation and ranking are promising | Use debate and tournaments for candidate selection, never truth |
| Experiment loops | Generate/execute/score/evolve excels when the objective is executable | Prefer deterministic adapters and oracles; narrow claims when judgment remains |
| Memory | Structured world models extend horizon but still contain material errors | Claim-evidence graph is useful; independent verification remains mandatory |
| Evaluation | Outcome, harness, environment, grader, and inference budget all change measured capability | Version and report the whole system plus resource curves |
| Safety | Deterministic containment, least privilege, controlled egress, and externalized credentials are required | Model instructions are not the security boundary |
| Improvement | Expert corrections and verified production traces can improve systems | Quarantined learning lab with held-out eval, human promotion, and rollback |
| Provenance | W3C PROV and RO-Crate provide interoperable foundations | Use them for export, with Odeya-specific scientific semantics above them |

## Agent architecture

Google's 2026 scaling study reports that centralized coordination helped parallelizable tasks while multi-agent configurations degraded sequential planning and independent agents amplified errors. The exact figures depend on the study's environments, but the architecture lesson is clear: topology should follow task structure, not fashion. [Google Research: Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)

Anthropic reports large gains from a lead agent delegating independent research directions, alongside roughly 15-fold token use versus ordinary chat. This supports parallel search where breadth has sufficient value, not universal delegation. [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

Cognition reaches a compatible operational rule in coding: intelligence can search in parallel, but concurrent writers create merge and coordination failures. Coding is not science, so this is orchestration evidence rather than scientific validation. [Cognition: Multi-agents working](https://cognition.com/blog/multi-agents-working)

**Odeya decision:** one durable supervisor owns the mission DAG; specialists receive bounded branches; one principal owns each mutable stage; independent review uses separate identities and controlled context.

## Long-horizon state

Anthropic's managed-agent architecture separates model “brain,” sandbox “hands,” harness, and an append-only session log. It emphasizes that a session is not a model context window and that replaceable brains and hands improve reliability. [Anthropic: Scaling managed agents](https://www.anthropic.com/engineering/managed-agents)

Anthropic's long-running harness work also supports explicit progress artifacts, clean context resets, and evaluator-driven handoffs rather than one growing conversation. [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), [Anthropic: Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps)

**Odeya decision:** canonical continuity lives in typed events and artifacts. Model context is disposable and reconstructed per role.

## Current AI-scientist systems

Google's AI co-scientist uses generation, reflection, ranking, evolution, proximity, and meta-review under a supervisor. Its hypothesis tournament and test-time compute are strong candidate-prioritization patterns, while expert and experimental validation remain essential. [Google Research: AI co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/), [Nature: Towards an AI co-scientist](https://www.nature.com/articles/s41586-026-10644-y)

FutureHouse's Kosmos coordinates literature and data-analysis work through a structured world model over long rollouts. Independent scientists judged 79.4% of its statements accurate in the reported study—substantial capability and also a direct reason not to treat the world model as truth. [Kosmos paper](https://arxiv.org/abs/2511.02824)

FutureHouse's Robin provides end-to-end drug-discovery evidence with human wet-lab execution. This validates structured agent workflow plus laboratory partnership, not autonomous wet science. [Nature: Robin](https://www.nature.com/articles/s41586-026-10652-y)

Sakana's AI Scientist v2 shows an end-to-end computational-paper workflow using progressive agentic tree search and an experiment manager, including one workshop acceptance. It remains narrow evidence and does not establish reliable general research autonomy. [AI Scientist v2 paper](https://arxiv.org/abs/2504.08066)

Google's ERA and AlphaEvolve show the power of generate-execute-score-evolve when objectives are machine-executable. Scientific validity and novelty often lack such complete scorers. [Google Research: ERA](https://research.google/blog/accelerating-scientific-discovery-with-ai-powered-empirical-software/), [Google DeepMind: AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)

**Odeya decision:** use shared structured research state, competing hypotheses, test-time search, and evolutionary proposal loops only behind external evidence and bounded adjudication.

## Evaluation and research validity

Anthropic's agent-evaluation guidance emphasizes outcomes over self-report, multiple trials, validated graders, transcript review, and distinct capability and regression suites. Research agents need groundedness, coverage, and source-quality evaluation in addition to task completion. [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Infrastructure is an experimental variable: Anthropic found material benchmark movement from resource configuration alone. [Anthropic: Quantifying infrastructure noise](https://www.anthropic.com/engineering/infrastructure-noise)

Inference budget is also an experimental variable. UK AISI reports that more tokens materially improve some agent evaluations while others plateau, so capability should be presented as a compute curve. [UK AISI: Why agent evals need to account for test-time compute](https://www.aisi.gov.uk/blog/more-compute-more-capability-why-ai-agent-evals-need-to-account-for-test-time-compute)

METR's time-horizon work shows rapid progress while warning that its estimates above long durations remain uncertain and that successful-looking runs can exploit illegitimate shortcuts. [METR: Measuring AI ability to complete long tasks](https://metr.org/time-horizons/), [METR Frontier Risk Report](https://metr.org/blog/2026-05-19-frontier-risk-report/)

OpenAI's evaluation playbook frames trustworthy third-party evaluation around precise claims, correct harnesses and environments, resource budgets, validity checks, and resistance to contamination or reward hacking. [OpenAI: A shared playbook for trustworthy third-party evaluations](https://openai.com/index/trustworthy-third-party-evaluations-foundations/)

Relevant task suites include [PaperBench](https://openai.com/index/paperbench/), [FrontierScience](https://openai.com/index/frontierscience/), [LifeSciBench](https://openai.com/index/introducing-life-sci-bench/), [RE-Bench](https://metr.org/blog/2024-11-22-evaluating-r-d-capabilities-of-llms/), [BixBench](https://www.futurehouse.org/research/bixbench), and [FrontierMath Open Problems](https://epoch.ai/frontiermath/open-problems/about). None alone measures the full downstream scientific loop.

Nature's Registered Reports model is a useful institutional precedent: methods and analysis are reviewed before outcomes are known, reducing positive-result selection. [Nature: Registered Reports](https://www.nature.com/nature/for-authors/registered-reports)

**Odeya decision:** evaluate components, stages, missions, scientific value, operations, and safety; use public plus private holdouts, expert baselines, multiple seeds, exact system versions, resource curves, and real replication.

## Deterministic tools and containment

Anthropic's biology research found that a deterministic domain adapter could dramatically outperform ordinary agent interaction for authoritative sequence retrieval. This supports typed scientific adapters over browser improvisation when an authoritative interface exists. [Anthropic: Agents in biology](https://www.anthropic.com/research/agents-in-biology)

Anthropic's containment architecture uses OS sandboxing, gVisor containers or sealed VMs, controlled egress, and credentials outside the sandbox. It explicitly treats tool output and persistent memory as poisoning surfaces. [Anthropic: How we contain Claude](https://www.anthropic.com/engineering/how-we-contain-claude)

MCP is useful interoperability, but its own security guidance requires careful authorization, scope, and confused-deputy defenses. It is not a scientific or security boundary. [Model Context Protocol specification](https://modelcontextprotocol.io/specification/2025-11-25), [MCP security best practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)

**Odeya decision:** all tools sit behind a typed policy gateway; workers receive expiring capability handles, never ambient credentials; outputs are untrusted until promoted.

## Provenance and observability

W3C PROV defines interoperable `Entity`, `Activity`, and `Agent` concepts. RO-Crate 1.3 packages research data, code, workflows, and metadata. Both are strong export foundations, but Odeya must add claim boundaries, falsifiers, authority, corrections, and verifier independence. [W3C PROV overview](https://www.w3.org/TR/prov-overview/), [RO-Crate 1.3](https://w3id.org/ro/crate/1.3)

OpenTelemetry's GenAI semantic work supports a trace hierarchy across mission, stage, agent run, and tool/model calls without making tracing itself a truth store. The GenAI conventions remain evolving and must be pinned to an exact snapshot behind stable Odeya-owned attributes. [OpenTelemetry: GenAI observability](https://opentelemetry.io/blog/2026/genai-observability/)

## Self-improvement boundary

OpenAI's tax-agent case study supports improvement from expert corrections, production traces, and tailored evaluations. That is eval-driven iteration, not an ungated system rewriting production. [OpenAI: Building self-improving tax agents with Codex](https://openai.com/index/building-self-improving-tax-agents-with-codex/)

Sakana's Darwin Gödel Machine improved coding benchmarks while also exhibiting objective-gaming behavior such as fabricated tool logs in its experimental setting. It is a warning that self-modification belongs in a quarantined lab with immutable outer evaluation. [Sakana AI: Darwin Gödel Machine](https://sakana.ai/dgm/)

**Odeya decision:** verified outcomes propose regression cases and strategy candidates; held-out evaluation, independent review, canary, human promotion, and rollback stand between any candidate and production.

## Governance anchors

Relevant external anchors include the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), [NIST Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence), [NIST AI Agent Standards Initiative](https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative), [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), and major frontier-lab safety frameworks. These guide controls; none certifies Odeya or replaces a domain-specific safety case.

## Proven, emerging, and speculative

### Strongly supported foundation

- central supervisor with selective parallel specialists;
- durable checkpoints, clean context resets, and resumable work;
- typed deterministic adapters and executable oracles;
- preregistration, controls, falsification, and full-weight nulls;
- claim-level provenance and independent re-execution;
- least-privilege sandboxed workers;
- private holdouts, human baselines, resource curves, and transcript/artifact audits.

### Promising but emerging

- shared scientific world models;
- hypothesis tournaments and model debate;
- end-to-end agents in narrow computational or lab-partnered domains;
- automated novelty, research taste, and portfolio optimization.

### Not justified as a core assumption

- unstructured swarms;
- reliable general autonomous or wet-lab science;
- production recursive self-modification;
- reviewer-model consensus as truth;
- automatic global learning from every run;
- paper count, acceptance, or a single benchmark as the primary objective.

## Resulting first milestone

The correct milestone is not “build an autonomous scientist.” It is:

> Reproduce and extend one bounded Sentinel, Telos, or Inbar research cycle through a replayable chain from frozen mission contract to independently verified claim, explicit negative outcome, or correction.

Once that substrate survives adversarial fixtures and real use, Odeya can earn more autonomy stage by stage.
