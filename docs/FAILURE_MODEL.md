# Failure Model

Odeya must identify what failed before deciding what the research means. Scientific outcomes, operational failures, policy denials, and security incidents have different recovery and claim consequences.

## Failure classes

| Class | Examples | Retry? | Scientific consequence |
|---|---|---:|---|
| Contract | missing falsifier, ambiguous denominator, invalid schema | after amendment | no run; no result |
| Protocol | data exposure before freeze, split leakage, post-hoc metric | prospective fork only | affected run `invalid` |
| Evidence | corrupt bytes, missing origin, rights absent, stale source | after reacquisition if legal | blocker or invalidity; no scientific outcome |
| Infrastructure | host loss, provider outage, OOM, network failure | bounded and idempotent | interruption or infrastructure-failure presentation; never a scientific null |
| Budget | token, time, accelerator, spend, rate limit exhausted | new authority required | blocked or predeclared truncated analysis |
| Policy | missing/expired/revoked grant, denied risk class | only after new decision | blocked; action not attempted |
| Security | injection, exfiltration attempt, sandbox escape, credential misuse | no automatic retry | pause, quarantine, incident, possible invalidation |
| Execution | command error, nonzero exit, partial artifact | bounded attempt retry | no claim until valid artifact |
| Verification | non-reproduction, evaluator failure, disagreement | investigate or independent verifier | claim blocked, contradicted, inconclusive, or invalid |
| Scientific | valid null, weak power, falsifier triggered, transfer failure | new prospective mission | null, inconclusive, or contradicted |
| Publication | rights, safety, embargo, wording, channel failure | after correction/authority | evidence retained; release withheld or withdrawn |

## Non-negotiable distinctions

- `interrupted` means resumable operational state, not a scientific finding.
- `infrastructure_failure` plus `no_valid_measurement` may be rendered as an infrastructure-null presentation, but scientific outcome remains unadjudicated.
- `null` requires the frozen design's null rule on a valid measurement.
- `inconclusive` means the valid evidence did not discriminate within declared power or equivalence bounds.
- `invalid` means scientific interpretation is disallowed.
- `blocked` names a dependency; it is not a euphemism for failure.
- `contradicted` requires a valid falsifying observation within scope.
- A rights blocker can preserve existence and provenance without disclosing or using content; `rights_blocked` is a derived presentation, not a scientific outcome.

## Retry semantics

Every work item declares:

- retryable error codes;
- maximum attempts and resource ceiling;
- whether the external action is idempotent;
- reconciliation procedure after ambiguous completion;
- backoff and provider-switch policy;
- state when the retry budget ends.

A retry creates a new `Attempt` linked to the prior attempt. It never deletes an error or changes the first attempt's measured cost. Model retries are additional samples, not silent replacements.

No automatic retry is allowed for policy denial, suspected compromise, protocol invalidity, irreversible physical action, ambiguous external write, or publication.

## Ambiguous external effects

If a timeout occurs after an external write may have happened:

1. stop retries;
2. mark the attempt `completion_unknown`;
3. use an independent read/reconciliation capability;
4. record external settlement evidence;
5. resume only when idempotency or operator authority makes the next action safe.

Never infer “did not happen” from a missing receipt.

## Verifier disagreement

Disagreement is retained as evidence. The adjudicator checks:

- exact input, environment, and evaluator version;
- sealed-truth exposure and contamination;
- stochastic variation and preregistered tolerance;
- data and artifact integrity;
- grader sensitivity and known-bad controls;
- whether the disagreement changes claim eligibility.

Material unresolved disagreement blocks sealing. Majority vote does not settle truth.

## Projection failure

If a projection, search index, or UI is stale or corrupt:

- canonical writes continue only if policy permits and the operator can inspect them safely;
- the projection displays last known ledger position and stale reason;
- scientific, approval, and publication actions that require a fresh projection fail closed;
- rebuild starts from the ledger and validates expected digests.

## Degraded modes

Allowed degraded modes are declared before an incident. Examples:

- read-only mission inspection;
- paused execution with intact handoff generation;
- local deterministic verification without model providers;
- artifact quarantine with metadata-only access.

There is no degraded mode that skips authority, invents missing data, or publishes from unverified state.

## Fault-injection matrix

Before the first active mission, test at every transition:

- process kill before and after commit;
- duplicate command and event delivery;
- reordered, missing, and corrupted event;
- stale lease and simultaneous workers;
- artifact upload truncated before promotion;
- policy engine unavailable or inconsistent version;
- credential revoked mid-call;
- egress denied and provider timeout;
- cost observation delayed or unknown;
- verifier returns disagreement or malformed evidence;
- projector lags or rebuilds;
- publication channel times out after possible release.

Each test must prove retained state, next legal action, no silent authority escalation, no duplicate consequential effect, and correct scientific status.

## Recovery objectives

Recovery point and time objectives are chosen per plane during the architecture gate:

- ledger and authority decisions require the strictest durability;
- immutable artifacts require verified replication and periodic restore drills;
- projections and indexes may be rebuilt;
- ephemeral workers have no recovery objective beyond retained attempts;
- public releases require independent manifests and withdrawal/correction paths.

An RPO/RTO number is not selected until data volume, partner obligations, cost, and first deployment environment are known. The decision must precede production use.
