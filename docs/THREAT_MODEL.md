# Odeya Threat Model

Status: proposed architecture, 2026-07-15. This threat model defines the adversary and control assumptions that must be accepted before implementation. It is not evidence that a selected sandbox, provider, policy engine, or deployment conforms.

## Security objective

Odeya must preserve five properties even when model output and research inputs are hostile:

1. **Scientific integrity:** an attacker cannot make inadmissible bytes, invalid work, weak verification, or fabricated provenance become an eligible claim.
2. **Authority integrity:** no principal obtains data, execution, spending, truth-settlement, physical-action, or publication authority outside an exact active grant.
3. **Confidentiality and rights:** sensitive, sealed, licensed, embargoed, or contributor-controlled material is disclosed only to authorized recipients for the recorded purpose.
4. **Operational containment:** untrusted code and tools cannot escape their declared compute, network, credential, filesystem, process, time, or external-effect envelope.
5. **Recoverability and non-equivocation:** interruption, compromise, rollback, deletion, or partial external effects cannot silently rewrite the retained scientific history.

Availability is important but never outranks these properties. Under ambiguity, Odeya pauses or refuses; it does not guess success.

## Assets and consequences

| Asset | Security consequence if compromised |
|---|---|
| Frozen protocol and exposure history | Post-hoc analysis can masquerade as confirmatory research |
| Event ledger and aggregate heads | State, authority, or claim history can be forked or rewritten |
| Artifact bytes, provenance, rights, and custody | Fabricated or unlawfully used evidence can support a claim |
| Sealed evaluator truth and private holdouts | Grader gaming, contamination, and false capability claims |
| Authority assignments, grants, and policy bundles | Unauthorized spend, disclosure, writes, or physical effects |
| Worker, verifier, and signing identities | Self-verification and false provenance become possible |
| Model-visible context and long-term memory | Exfiltration, poisoning, privilege escalation, or false continuity |
| Provider credentials and billing accounts | Data loss, spend abuse, or external actions |
| Publication manifests and channels | Premature, altered, or irreversible disclosure |
| Corrections, retractions, and dependency graph | Known false claims remain visible as current |
| Operator and contributor identity | Social engineering, attribution fraud, or governance capture |

## Trust zones

```text
Z0 constitutional control
   operator decisions · root assignments · schema/method/policy registries
        |
Z1 canonical control plane
   command admission · event/authority transactions · claim compiler
        |
Z2 evidence and verification boundary
   object materialization/promotion · deterministic evaluators · sealed truth
        |
Z3 untrusted execution
   model runs · generated code · browsers · tools · contributed workloads
        |
Z4 external systems
   providers · repositories · release channels · labs · instruments · testbeds
        |
Z5 projections and recipients
   cockpit · search indexes · exports · public/restricted audiences
```

Trust is not transitive. Authentication into one zone does not grant a role in another. Every boundary carries typed inputs, immutable references, data classification, purpose, policy decision, grant, resource envelope, and retained result.

The canonical database is trusted for atomic ordering under its accepted durability assumptions, not for the scientific meaning of arbitrary inserted bytes. The object store is trusted to retain exact bytes under its accepted profile, not to decide promotion or validity. A model provider is never trusted with authority or truth.

## Adversary classes

- **Malicious contributor:** submits prompt injections, poisoned data, malware, deceptive citations, rights traps, oversized inputs, or thesis spam.
- **Compromised source or package:** an otherwise legitimate website, repository, dataset, model, dependency, image, or tool begins returning hostile content.
- **Opportunistic model/tool:** follows injected instructions, fabricates completion, exploits the grader, leaks context, or seeks capabilities because its local objective rewards it.
- **Malicious worker workload:** attempts sandbox escape, lateral movement, persistence, covert channels, resource theft, or unauthorized egress.
- **Compromised provider/adapter:** forges receipts, replays callbacks, misreports identity/cost, returns stale data, or changes behavior without version disclosure.
- **Credential attacker:** steals a human session, service identity, API token, signing key, or recovery credential.
- **Insider:** has legitimate access but attempts hidden protocol changes, selective deletion, self-verification, unauthorized disclosure, or policy weakening.
- **Colluding principals:** satisfy nominal role separation while sharing identity, incentives, context, implementation, or institution.
- **Availability/cost attacker:** creates retry storms, queue starvation, oversized artifacts, unbounded test-time compute, or duplicate provider charges.
- **External observer:** infers private missions, sources, people, hypotheses, or results from logs, timing, identifiers, errors, or publication metadata.

Founding architecture assumes the operator root may be compromised; recovery therefore requires witnessed history, key rotation, break-glass logging, and a second accountable principal before high-consequence deployment. It does not assume protection against a fully compromised host plus all independent witnesses and key systems.

## Security invariants

1. Models, tools, workers, schedulers, callbacks, indexes, and UI clients never write canonical state directly.
2. Every state change enters through a registered command, exact schema/policy version, active authority, and atomic event batch.
3. A principal cannot issue, consume, or verify the terminal authority for its own consequential output where the action matrix forbids overlap.
4. Credentials remain outside model-visible sandboxes; workers receive expiring capability handles scoped to one purpose.
5. Network, filesystem, process, resource, and artifact export are default deny.
6. Tool and source output re-enters as untrusted data, even when authenticated or signed.
7. Sealed truth, private holdouts, and verifier-only evidence are recipient-scoped and exposure events are monotonic.
8. Storage byte identity, artifact promotion, scientific validity, claim eligibility, and publication are separate decisions.
9. A timeout, missing reviewer, provider 2xx, callback, or workflow completion never implies an external or scientific outcome.
10. Every consequential external effect has intent-before-dispatch, stable identity, idempotency analysis, settlement evidence, and a no-blind-retry rule.
11. Security controls cannot silently change a scientific denominator, split, metric, sample, or result; any intervention creates evidence and validity review.
12. Corrections, revocations, quarantines, and withdrawals append facts and invalidate projections; they never erase the triggering history.
13. Logs, traces, context packs, and error messages disclose the minimum necessary data and never contain reusable secrets or hidden chain of thought.
14. Policy unavailability, identity uncertainty, unknown independence, and stale projection state fail closed for consequential action.

## Data and execution classes

### Data classes

| Class | Example | Model/provider posture |
|---|---|---|
| D0 public | Public paper or open benchmark under verified terms | May use approved providers under ordinary retention policy |
| D1 internal | Private mission plans, unpublished analysis | Approved private processing only; no provider training |
| D2 restricted | Licensed data, partner data, source code, contributor identity | Purpose/region/provider-specific grant and access audit |
| D3 sensitive | Personal, security-relevant, export-controlled, high-value holdout | Minimal recipient set, strong isolation, sealed evaluation where possible |
| D4 prohibited | Data lacking lawful basis or outside accepted domain policy | No acquisition, processing, model exposure, or publication |

Rights, sensitivity, retention, residency, and scientific role are separate fields. “Publicly reachable” does not mean lawful to ingest, train on, or republish.

### Execution tiers

| Tier | Workload | Minimum containment claim |
|---|---|---|
| E0 | Deterministic trusted validator over bounded fixture | Non-root process, read-only inputs, quotas, no ambient secret, audited output |
| E1 | Reviewed mission code and approved dependencies | Rootless or hardened container only after negative tests; default-deny egress |
| E2 | Model-generated code or untrusted repository | Kernel-isolated container or microVM selected by the accepted escape/lateral-movement tests |
| E3 | Sensitive data plus untrusted computation | Dedicated tenancy/host class, narrow brokered capabilities, enhanced audit and deletion |
| E4 | Physical, critical, bio/chemical, or irreversible external action | Domain safety system and independent interlocks outside Odeya; no general founding authority |

A weaker tier cannot be selected because it is cheaper. The isolation claim must name the exact host kernel, runtime, configuration, escape tests, update policy, residual channels, and incident response.

## Abuse-case register

| ID | Attack path | Required preventive/detective controls | Safe consequence |
|---|---|---|---|
| T01 | Paper/tool text instructs an agent to leak secrets or ignore protocol | Content/data separation, capability gateway, no ambient credentials, egress policy, injection fixtures | Attempt denied; source remains evidence with hostile-content label |
| T02 | Generated code reads host/cloud metadata or another mission | Strong isolation, namespace/tenant controls, metadata denial, syscall/network tests | Kill sandbox, revoke lease, quarantine outputs, open incident |
| T03 | Worker fabricates files or completion without executing | Attempt manifest, retained commands, artifact digests, deterministic verifier, known-bad controls | No stage completion or claim eligibility |
| T04 | Producer chooses or impersonates its verifier | Separate assignment/grant, verifier scheduler outside producer context, identity attestation | Verification blocked and incident reviewed |
| T05 | Model learns sealed answers from context, cache, logs, or prior memory | Exposure compiler, recipient-specific stores, cache partitioning, canaries, exposure ledger | Affected evaluation invalid; holdout rotated prospectively |
| T06 | Malicious dataset changes after protocol freeze | Digest pinning, immutable bytes, source timestamp, mirror/retention policy | Mismatch blocks execution; new version requires amendment |
| T07 | Same command ID reused with altered payload | Canonical request digest binding and immutable command receipt | Reject; high-risk reuse opens incident |
| T08 | Grant is replayed, widened, used after revocation, or double-consumed | Bounded scope, counters/reservations in command transaction, canonical commit ordering | Reject or reconcile in-flight effect; never erase prior use |
| T09 | Provider timeout triggers duplicate write, charge, or publication | Intent-before-dispatch, stable provider key, independent reconciliation, no blind retry | `completion_unknown`; dependent action blocked |
| T10 | Object exists but metadata/provenance is forged | Trusted stream validation, conditional byte materialization, canonical promotion transaction | Orphan inert; mismatched registration quarantined |
| T11 | Ledger fork/truncation hides a correction or grant revocation | Hash chain, signed checkpoints, independent witness, restore comparison | Read/write quarantine until canonical history resolved |
| T12 | Projection lag shows stale approval or old claim as current | Ledger position/freshness token, minimum-position reads, correction fanout monitor | UI shows stale/unavailable; cannot authorize |
| T13 | Evaluator or benchmark is reward-hacked | Private holdout, positive/negative controls, grader validation, transcript/artifact audit, external outcome | Evaluator invalidated; affected claims blocked/corrected |
| T14 | Dependency/model/provider changes silently | Exact identities, lockfiles/images, compatibility registry, observed provider version, canaries | New attempt/version; confirmatory comparability denied |
| T15 | Insider changes protocol after seeing outcome | Exposure ledger, immutable freeze, dual review for amendments, prospective fork | Original stays frozen; affected branch exploratory/invalid |
| T16 | Authorized user exports restricted evidence through publication | Sealed manifest allowlist, redaction decision, DLP as secondary check, human single-use grant | Release denied or ambiguous release reconciled/withdrawn |
| T17 | Retry/resource storm exhausts compute or budget | Per-mission queues, reservations, circuit breakers, quotas, backpressure, charge reconciliation | Work blocked; no silent budget expansion |
| T18 | Model writes persuasive false memory that affects later work | Provenance-typed memory, assertion/evidence separation, verification before promotion | Candidate memory quarantined or superseded |
| T19 | Colluding reviewer appears “independent” | Multidimensional independence vector, conflict declarations, institutional/exposure requirements | Independence unknown/insufficient; no eligible claim |
| T20 | Safety filter or redaction silently alters scientific input/output | Raw retained bytes where lawful, transformation activity, before/after digest, validity review | Result marked altered; claim scope narrowed or invalidated |
| T21 | Sealed truth influences retrieval ranking, summaries, embeddings, cache, or omission even though final text is redacted | End-to-end information-flow policy, role/purpose cache partitioning, compilation receipt, canary and noninterference fixtures | Affected producer view/attempt invalidated; holdout rotated prospectively |
| T22 | Agent produces a plausible result while silently ignoring material contradictory or refuting evidence | Material-evidence inventory, one retained disposition per item, epistemic transition checks, known-refutation cases | Transition rejected or retained unresolved; no claim promotion |
| T23 | Cheap hypothesis/artifact generation overwhelms scarce verification and creates a de facto unverified knowledge base | Multidimensional verification reservation, backlog ceilings, quarantine, no memory/claim promotion from repetition | Generation throttled; overflow remains visibly unverified or is discarded under policy |
| T24 | Debate, Elo rank, repeated agents, or model consensus is presented as scientific support | Ranking/evidence type separation, correlation groups, external oracle and verification requirements | Ranking may guide exploration only; evidence gate remains unsatisfied |
| T25 | Agent fabricates or games the observable epistemic record while optimizing process metrics | Evidence/tool receipt binding, exact graph predecessor/successor digests, anti-gaming controls, outcome axis kept separate | Candidate record quarantined; process evaluator invalidated where affected |
| T26 | Provider/model fallback silently changes a confirmatory attempt or its data behavior | Exact model/harness/provider/retention identity, fallback as new attempt, protocol comparability rule | Original attempt stops; new attempt is separately classified and adjudicated |
| T27 | A contributor supplies a polished pseudoscientific or false premise and the engine optimizes for a persuasive compliant report | Premise/evidence-class challenge, rival and falsifier generation, admissibility rules, refusal benchmark, human/domain escalation | Mission is refused, reframed, or retained as an explicitly adversarial test; no eligible claim or publication |
| T28 | A research benchmark appears strong because the agent retrieves the reference answer, evaluator artifact, derivative summary, or contaminated cache instead of synthesizing evidence | Exact contamination frontier, clean-room blocked-reference manifest, cache/index/embedding taint, ordinary-versus-clean-room comparison, atomic-fact audit | Evaluation is invalidated or reported as contaminated; no capability promotion |

Every row needs at least one known-bad architecture fixture before Gate A and executable containment/fault evidence in its authorized implementation increment.

The exact non-authoritative cognition records and invariants used to close T21–T26 are specified in [Cognitive Control Contracts](COGNITIVE_CONTROL_CONTRACTS.md).

## Model and memory boundary

Model outputs are untrusted proposals. Structured output validation prevents malformed data, not deception. A model may discover a valid exploit in its evaluator, collude statistically with another model family, or reproduce memorized holdout content without an explicit attack.

Therefore:

- the model never sees reusable credentials or policy-signing material;
- role contexts are compiled from canonical state under an exposure policy;
- producer narrative is omitted from clean verification unless the protocol requires it;
- provider/model diversity is recorded as one independence dimension, never assumed sufficient;
- private reasoning is not durable research memory;
- memory promotion requires evidence, validity, applicability, and visibility decisions;
- a new model snapshot or provider behavior is a new evaluated configuration;
- no production model output edits policy, schema, evaluator, routing, prompt, tool, or memory directly.

## Authority bootstrap and break glass

The initial constitutional assignment must be an operator-signed artifact whose digest is recorded in the first canonical checkpoint. It names scope, expiry/review, recovery principals, prohibited self-approval combinations, and the process for adding a second accountable human.

Break glass is not an invisible administrator bypass. It requires:

- a predeclared emergency class and narrow action set;
- strong reauthentication and, for consequential data/release/effects, a second principal;
- short expiry and no delegation;
- immediate immutable event, independent notification, and session capture excluding secrets;
- mandatory incident, impact review, and rotation of affected credentials;
- no power to rewrite evidence, adjudication, or prior events.

## Cryptographic and identity assumptions

- Digests protect byte identity only under the pinned algorithm/profile; they do not prove origin or meaning.
- Signatures prove possession of a key under a trust root; they do not prove the signer was correct, independent, or uncompromised.
- Workload identity proves an admitted runtime identity, not that its code behaved as intended.
- Timestamps require an accepted clock/source/uncertainty profile. External reported time is evidence, not automatically trusted time.
- Encryption protects selected boundaries but not a compromised authorized endpoint.
- Confidential-computing claims, if used, require exact hardware/firmware/attestation policy and side-channel assumptions; the architecture does not assume them.

Key hierarchy, rotation, revocation, backup, recovery, quorum, hardware protection, and witness independence remain deployment-profile decisions and must be frozen before production.

## Residual risks and explicit refusals

The founding engine refuses to claim protection against:

- novel isolation escapes without an independent containment layer and tested response;
- malicious results accepted by all required independent humans/instruments under shared compromise;
- covert channels eliminated rather than bounded;
- correctness of an external physical system from a digital receipt alone;
- safe autonomous R3/R4 action from the general engine architecture;
- scientific truth from signatures, consensus, provenance completeness, or clean replay alone.

These are not reasons to weaken controls. They define where stronger domain systems, independent institutions, physical interlocks, or refusal are required.

## Acceptance evidence

Gate A cannot accept this threat model until:

- every trust boundary maps to command, event, schema, data class, and authority contracts;
- the authority bootstrap, human-only action matrix, dual-control rules, and break-glass path are frozen;
- the first-slice data/execution classes and provider-retention rules are selected;
- each abuse case has a positive and known-bad non-executable trace with expected events and refusal;
- ledger witness, key hierarchy, incident, deletion/legal-hold, and sealed-truth rotation designs are accepted;
- selected isolation and external-effect claims are marked provisional pending authorized Gate B evidence;
- an independent security reviewer closes critical/high findings; and
- the operator accepts the exact candidate commit.

Runtime security testing belongs to the exit gate of the authorized increment. No prose-only threat model can establish sandbox or deployment security.
