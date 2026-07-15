# Evaluation and Learning

Odeya improves by turning verified failures, corrections, costs, and outcomes into evaluation cases. It does not learn production policy from eloquent self-review or silently modify itself after every run.

## Evaluation question

The primary question is not “did the agent produce a convincing report?” It is:

> Under a declared resource budget, did this system produce a reproducible, correctly bounded reduction in uncertainty or a verified outcome without violating authority, safety, or evidence requirements?

## Evaluation stack

### Component evaluations

- source retrieval recall and precision;
- source-role and rights classification;
- citation entailment and attribution;
- structured extraction accuracy;
- tool schema adherence and functional correctness;
- calibration and abstention;
- data, code, and artifact integrity.

### Stage evaluations

- problem orientation and baseline coverage;
- novelty assessment against known work;
- competing-hypothesis diversity and quality;
- experiment design, controls, power, and falsifiers;
- implementation correctness;
- statistical analysis and uncertainty;
- adversarial review yield;
- claim-boundary compliance.

### Mission evaluations

- end-to-end replay from contract to verdict;
- recovery after context loss, worker death, and partial artifacts;
- result stability over multiple seeds and environments;
- cost, latency, and human-intervention burden;
- complete evidence and authority lineage;
- valid null, invalid, and blocked handling.

### Scientific evaluations

- blinded expert validity, novelty, and usefulness;
- comparison with expert and simple baselines under comparable budgets;
- external settlement or independent replication;
- downstream decision consequence;
- correction rate and time to correction.

### Safety and integrity evaluations

- prompt injection and tool-output poisoning;
- data exfiltration and over-broad retrieval;
- sandbox escape and unauthorized egress;
- fabricated tool use, evidence, citations, or receipts;
- reward hacking and grader manipulation;
- objective drift and unauthorized memory changes;
- approval, budget, and publication bypass;
- deliberately broken artifacts for every gate.

## Evaluation design

Every material score includes:

- exact task and reference version;
- public and private rotating holdouts where appropriate;
- multiple independent trials and uncertainty intervals;
- model, prompt, harness, tool, environment, and evaluator versions;
- token, wall-time, compute, money, and human-time budgets;
- failure taxonomy and transcript/artifact audit sample;
- grader validation and known blind spots;
- baseline results under comparable resources.

Report capability as a resource curve where additional inference budget changes success. A single score without its budget is incomplete.

`pass@k` and `pass^k` answer different questions: whether at least one of `k` attempts succeeds versus whether all `k` succeed. Research reliability needs both discovery and consistency views.

## Single-agent baseline before multi-agent claims

Parallel specialists are justified for breadth, independent hypothesis generation, and decomposable analysis. They are not the default for sequential planning or shared mutation.

Every multi-agent configuration is compared against:

- the same model in a single durable harness;
- equivalent total token and compute budgets;
- a central-supervisor configuration;
- ablations removing debate, ranking, or specialist roles;
- one-writer versus concurrent-writer variants where safe to test.

Agent consensus is measured as an orchestration behavior, not as accuracy evidence.

## Verification hierarchy

Prefer the strongest available oracle:

1. deterministic executable check;
2. exact clean-environment re-execution;
3. formal or statistical verifier;
4. sealed ground truth or external-system outcome;
5. clean-context model critic;
6. independent expert judgment.

The order is not universal—experts may be the only valid oracle for novelty or taste—but model review should not replace a deterministic or physical check that exists.

## Grounded learning record

A learning observation includes:

- source mission and exact ledger position;
- observed outcome and time;
- verifier identity and independence;
- applicability conditions and confidence;
- affected component or strategy;
- resource and human-intervention cost;
- counterevidence and known confounds;
- proposed regression fixture;
- whether the observation is isolated, repeated, or externally settled.

Reward is multidimensional. Preserve at least reproducibility, information gain, falsifier coverage, uncertainty reduction, claim validity, safety, time, cost, and downstream value. Do not collapse these into one opaque number for production decisions.

## Promotion pipeline

```text
verified observation
  -> candidate lesson
  -> recurrence threshold
  -> regression and negative fixtures
  -> offline evaluation
  -> shadow replay on held-out missions
  -> independent review
  -> canary with bounded authority
  -> promotion decision
  -> monitored rollout or rollback
```

A strategy candidate cannot alter production prompts, tools, policies, code, or memory retrieval until it passes this pipeline. High-risk or irreversible changes require human approval and, where specified, dual control.

## Improvement lab

Self-editing, architecture search, prompt evolution, tool synthesis, or policy learning may run only in a quarantined improvement lab with:

- no production credentials or write authority;
- fixed outer objective and immutable evaluator set;
- private anti-reward-hacking tests;
- immutable logs and environment snapshots;
- explicit resource ceiling and kill switch;
- human-reviewed diff and rationale;
- clean reproduction before promotion.

The production engine never accepts generated logs, modified detectors, or self-assigned scores as proof of improvement.

## Portfolio learning

Cross-mission learning is allowed only after sanitization and applicability review. A pattern from autonomous driving does not automatically govern biology or aerospace. The record names the source domains, evidence count, transfer assumptions, and counterexamples.

Failures and corrections should become regression tests quickly. Capabilities become reusable tools or skills only after repeated work demonstrates stable inputs, outputs, safety boundaries, and evaluation value.

## Initial scorecard

The first vertical slice should report:

| Dimension | Initial gate |
|---|---|
| Replay | Same verdict from sealed inputs in a clean verifier |
| Integrity | Any artifact mutation is detected |
| Gate sensitivity | Every known-bad fixture is rejected |
| Recovery | Worker death resumes without lost or duplicated state |
| Authority | Unauthorized execution, spend, and release fail closed |
| Claim precision | Generated wording stays within the frozen consequence table |
| Provenance | Claim traverses to all required artifacts and identities |
| Cost | Estimate and actual usage remain distinct and inspectable |
| UI truth | Null, unknown, stale, corrected, and blocked states render exactly |

Passing this scorecard establishes a trustworthy substrate for more autonomy. It does not establish general scientific capability.
