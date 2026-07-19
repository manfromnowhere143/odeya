# Independent Architecture Review Protocol

Status: proposed Gate A review contract, 2026-07-15. This protocol defines how an exact Odeya architecture candidate earns acceptance. It does not let the author, an AI agent, a passing schema validator, or an investor narrative certify the design.

## Acceptance theorem

Gate A is accepted only for one immutable candidate when all of the following are true:

```text
candidate identity frozen
AND required artifacts complete
AND structural + semantic + trace evidence passes
AND every required review lane has an accountable independent determination
AND no critical/high finding remains open or silently waived
AND limitations and deferred probes are explicit
AND Daniel signs the exact candidate decision
```

Acceptance means the architecture is coherent enough to authorize bounded product probes or, later, one Gate C increment. It does not prove Odeya is safe, scientifically superior, production ready, or generally autonomous.

## Exact candidate identity

The `ArchitectureCandidateManifest` binds:

- Odeya repository identity and clean commit;
- every reviewed file path, media type, byte length, and byte digest;
- schema registry and metaschema identities;
- canonicalization profile and conformance-vector package;
- semantic rule registry and trace package;
- formal models, configurations, tool versions, and result artifacts;
- first vertical-slice source snapshots and rights/settlement evidence;
- known-bad, correction, refusal, null, supported, and recovery fixtures;
- standards snapshots/profile records;
- architecture validator environment and dependency lock;
- open findings, accepted limitations, and deferred Gate B probes; and
- manifest canonicalization/signature profile.

A directory listing, branch name, mutable URL, or commit alone is insufficient. The source commit establishes authoring identity; the manifest establishes review scope. Generated diagrams and rendered documents are included when reviewers relied on them.

Every relied-on member is checked at its exact manifest path and digest. A
validator pass over a sibling/source artifact cannot cover a shipped or bundled
member that omits a required boundary.

## Review lanes

| Lane | Minimum accountable competence | Core questions |
|---|---|---|
| Mission and product boundary | Frontier-research/product architecture | Is the first wedge real, bounded, valuable, and distinct from general-autonomy claims? |
| Statistical and scientific | Statistician/methodologist relevant to the first slice | Are protocol, estimand, validity, uncertainty, null, adaptation, multiplicity, verification, and claim rules defensible? |
| Physical/domain | Relevant domain expert; physical systems expertise when applicable | Are units, frames, instruments, models, observability, VVUQ, sim-to-real, safety boundaries, and domain limits correct? |
| Distributed systems and recovery | Senior transactional/distributed-systems engineer | Are linearization, races, idempotency, effects, checkpoints, restores, and failure consequences coherent? |
| Security, authority, and cryptography | Security architect plus protocol/crypto competence for commitment/signature design | Are trust zones, capabilities, quorum, key/recovery, containment assumptions, receipts, and abuse cases falsifiable and safe? |
| Data rights and privacy | Accountable rights/privacy reviewer for the first jurisdiction/data profile | Are acquisition, purpose, model/provider exposure, retention, deletion, reuse, and publication scopes lawful/defensible? |
| Human factors and accessibility | Product/accessibility reviewer independent of visual authorship where possible | Can humans see true state, uncertainty, stale/blocked/corrected conditions, and authority consequences accessibly? |
| Adversarial scientific integrity | Reviewer rewarded for finding false-science paths | Can leakage, grader gaming, self-verification, unsupported language, missing evidence, or correction suppression reach publication? |

One person may cover multiple lanes only when competence and conflict are disclosed. Statistical/domain, security/crypto, and operator acceptance cannot be replaced by model-generated review. A model red team may expand coverage but is an untrusted finding generator.

## Independence record

Each reviewer record states:

- verified principal and organization;
- lane and claimed competence basis;
- employment, funding, authorship, family, investment, customer, and other conflicts;
- prior access to proof truth, producer narrative, or candidate construction;
- which artifacts and versions were reviewed;
- tools/models used and whether outputs were independently checked;
- review time window and compensation/incentive structure;
- independence dimensions satisfied, not satisfied, and unknown; and
- signature over the determination digest.

Independence is multidimensional. A different model name or employer is not automatically independent; shared data, evaluator, code, prompts, operator, incentives, or hidden context can correlate failure.

A declared human principal and valid signature are also insufficient to prove a
human-controlled determination. [ADR
0092](decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md),
extending [ADR
0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md), keeps
PRQ-013 unresolved until the staged individual-assurance foundation, T1/T2
dependencies, `AssuredDecision`/successor candidates, exact migration,
end-to-end refusals, and accountable review exist. Session logs may corroborate bounded operational
chronology only; they cannot establish authorship, human intent, accountable
approval, independence, or scientific validity.

## Reviewer packet

Every lane receives the same candidate manifest plus a role-specific packet compiled at one ledger/repository position:

1. charter, architecture/status, constitutions, state and authority contracts;
2. explicit operator constraints and implementation lock;
3. proof-mission source snapshots and corrections, not only favorable summaries;
4. threat/abuse/failure registers and known-bad traces;
5. exact schemas, semantic rules, formal models, and validator results;
6. current blockers and prior findings, including rejected architecture alternatives;
7. proposed deployment-neutral assumptions and unresolved product probes;
8. claim-language boundary—what Gate A acceptance may and may not say; and
9. a reproducible local/offline verification procedure; and
10. the canonical current baton plus any retained historical pointers needed to
    prove that no older passing ledger is being presented as current.

Reviewers may request additional evidence. Any new candidate artifact is added through a new manifest version; it cannot be passed privately to one reviewer and omitted from scope.

## Review method

Each lane must perform four distinct passes:

### 1. Completeness

Map required gates, commands, events, objects, invariants, failure cases, ownership, and acceptance evidence. Missing or circular ownership is a finding even if no contradiction is visible.

### 2. Internal consistency

Trace terms and identities across charter, state model, schemas, event catalog, authority, protocol, publication, UI, implementation order, and decisions. Conflicting state vocabularies, schema versions, digest profiles, or authority meanings are findings.

### 3. Adversarial execution on paper

Replay the positive and known-bad fixtures at exact source/candidate identities. Attempt stale-position writes, grant reuse/revocation races, leakage, optional stopping, missing measurement, artifact loss, restore resurrection, publication ambiguity, correction fanout failure, and false independence.

### 4. Claim-boundary review

For every claimed property, classify evidence as:

- `defined`: contract exists;
- `structurally_validated`: schemas/links pass;
- `semantically_traced`: pure rule/trace evidence passes;
- `bounded_model_checked`: stated finite model has no counterexample;
- `product_probed`: selected implementation passed an authorized probe;
- `independently_reproduced`: independent execution reproduced the result;
- `operationally_observed`: deployed behavior was measured; or
- `unproven`.

No lower class may be narrated as a higher one.

## Finding contract

An immutable `ArchitectureFinding` includes:

- finding ID/version and candidate manifest digest;
- lane, reviewer, discovery method, and affected artifacts;
- severity and confidence in the finding itself;
- exact violated requirement/invariant or missing proof;
- minimal reproducer/trace and observed versus required result;
- consequence: scientific, authority, confidentiality, safety, recovery, publication, cost, accessibility, or operability;
- scope and possible dependent findings;
- proposed remedies and how each could fail;
- disposition owner, due gate, and current state; and
- closure evidence and independent closure reviewer.

Severity is consequence-based:

| Severity | Meaning at Gate A |
|---|---|
| Critical | Can create false published science, unauthorized high-consequence action/disclosure, unrecoverable canonical fork, or collapse a constitutional boundary |
| High | Can invalidate a required scientific/authority/recovery property or first-slice claim under plausible conditions |
| Medium | Material ambiguity, operability, accessibility, performance, or bounded-risk defect with a safe refusal/containment path |
| Low | Local clarity, maintainability, or non-consequential consistency issue |
| Note | Observation or optional improvement with no demonstrated requirement violation |

Likelihood can be recorded separately; it cannot reduce a high consequence that lacks an enforced refusal.

## Finding states and disposition

Allowed states are:

```text
open -> remedy_proposed -> changed_candidate -> closure_reviewed -> closed
open -> duplicate_of:<id>
open -> invalid_with_evidence
open -> accepted_limitation   (medium/low only at Gate A)
open -> deferred_probe        (only when semantics are frozen and the uncertainty is product-empirical)
```

Critical/high findings cannot be risk-accepted into Gate A. A supposed “defer” that can change a scientific, authority, privacy, safety, recovery, or publication invariant is still open. `invalid_with_evidence` requires a reviewer other than the finding author or candidate author when consequence is critical/high.

Closing a finding records the exact changed candidate and reruns every impacted trace/review lane. Editing the prose of the finding is not closure.

## Change-impact and review validity

Any candidate change creates a new manifest digest. A deterministic impact map identifies changed objects, terms, schemas, rules, commands/events, fixtures, standards, and downstream documents.

Review determinations may be carried forward only when the reviewer signs that the changed digest set is outside their lane or has been rechecked. Constitutional, schema, semantic-rule, proof-fixture, canonicalization, authority, recovery, and publication changes invalidate all dependent sign-offs by default.

Editorial changes still receive a new candidate but may use a bounded editorial carry-forward rule when byte changes provably do not change meaning, links, identifiers, or rendered content relied on by the review.

## Final determination

Each lane issues exactly one result:

- `accept_for_gate_a` with limitations;
- `reject` with blocking findings; or
- `unable_to_determine` with missing evidence.

Timeout, absence, silence, partial review, or a prose compliment is not acceptance. The Gate A compiler fails closed unless every required lane has an accepted determination for the same manifest and all critical/high findings are closed.

Daniel then signs an `OperatorArchitectureDecision` that names:

- candidate manifest digest;
- accepted lane determinations and residual limitations;
- explicit constitutional decisions and role/root overlap;
- authorized next state (`gate_b_probes_only`, `remain_architecture`, or later separate Gate C consideration);
- prohibited actions that remain locked; and
- decision time, authentication/signature, review/expiry trigger, and supersession route.

Gate A acceptance alone never authorizes runtime product implementation.

## Review falsifiers

This protocol fails if Odeya can:

- review a branch or folder rather than exact bytes;
- hide proof-mission corrections or known-bad results from a reviewer;
- count AI self-review as the required independent expert determination;
- accept a critical/high finding by renaming it a limitation or future work;
- carry a sign-off across a semantic change without reviewer impact acceptance;
- let one universal score average away a security or scientific failure;
- infer acceptance from silence or schedule pressure;
- validate a sibling/source artifact while omitting a required boundary from
  the exact reviewed or bundled member;
- accept a passing historical ledger/pointer as current when the canonical
  baton names a later state;
- convert an initiated then interrupted provider request into zero completed
  requests, zero spend, applied, or not applied;
- infer authorship, human intent, approval, independence, or scientific
  validity from session logs;
- accept architecture while exact source rights or fixture identity is unsettled; or
- describe Gate A as product conformance or scientific superiority.

## Required architecture fixtures

Before review begins, retain at least:

- clean manifest/review/acceptance happy path;
- same commit with altered untracked file;
- changed schema with stale sign-off;
- critical finding mislabeled medium;
- reviewer conflict hidden behind a second identity;
- missing proof correction from a reviewer packet;
- validator pass with semantic known-bad failure;
- valid sibling/source file with the required boundary removed only from the
  exact reviewed/bundled member;
- passing historical ledger/pointer beside a later canonical current baton;
- initiated provider request interrupted before completion and cost settlement,
  with both values retained as unknown;
- session-log chronology offered as authorship, human decision, approval,
  independence, or scientific-validity evidence;
- product-dependent claim disguised as accepted architecture;
- timeout/missing reviewer; and
- accepted manifest with one publication byte changed.

Every known-bad case must prevent the Gate A compiler from producing `accepted`.
These refinements are provenance-bound in the
[cross-program process-evidence
packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md); they exercise
existing exact-identity, current-state, missingness, authority, and evidence
boundaries rather than adding a new top-level invariant.
