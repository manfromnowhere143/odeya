# Cross-Program Process Evidence Absorption — 2026-07-19

Status: provenance-bound architecture evidence packet. The Gate A deltas below
are blocking or proposed obligations, not accepted contracts, implemented
runtime behavior, scientific results, superiority evidence, publication
authority, or permission to execute an external effect.

This packet records a bounded read-only extraction from Sentinel, Telos, and
Inbar. Those programs remain independent evidence sources. Odeya imports no
source code, active state, scientific result, provider authority, credential,
or runtime dependency from them.

The controlling Odeya boundaries remain the
[pre-implementation gate](PRE_IMPLEMENTATION_GATE.md), the
[Gate A prerequisite closure plan](GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md),
the [architecture status](ARCHITECTURE_STATUS.md), and the
[session handoff](SESSION_HANDOFF.md). This packet cannot close Gate A or
overrule those records.

## Evidence classes and interpretation

The audit used four evidence classes:

1. **Committed source evidence** is an exact Git commit, tree, or blob from the
   named source repository. A Git object ID identifies retained repository
   bytes under that repository's object format; it is not scientific,
   semantic, human-decision, or policy authority.
2. **Committed but source-rejected or noncanonical evidence** remains useful
   incident evidence but is not promoted to the source program's accepted
   state.
3. **Dirty or untracked source bytes** are excluded from the committed evidence
   set. Selected worktree blob IDs may be recorded solely to distinguish those
   bytes from committed subjects.
4. **Operational-log corroboration** establishes only a bounded sequence of
   tool calls and observed outcomes. It does not establish authorship, human
   intent, independent review, scientific validity, or the truth of generated
   prose.

No session identifier, absolute session-log path, raw private reasoning,
credential, or unrestricted prompt is retained here.

## Exact audited source identities

### Sentinel

The Sentinel audit deliberately distinguished three committed subjects:

| Classification | Commit | Tree | Meaning in this packet |
|---|---|---|---|
| Source-local accepted remote baseline | `69bd2e2face00ccabb426382347eb04e8a0dbe83` | `fb34eec73fd890440718ec60e1b53613690601b4` | Generation-fourteen B14 baseline; source-local acceptance is not Odeya acceptance |
| Local committed, failed, and not accepted on remote `master` | `4d8801605f1e285c5000b4220e965e97a8aff345` | `c9c9b8e9d3eef3277ca4544e944b49a4292eb358` | Generation-fifteen candidate retained as incident evidence |
| Retained host-evidence branch | `4bd0a23bfe675ecbfa6b14bd56062cb5d26879ac` | `80b6e343ab8793ea1e5267ec85bcc4877a9551de` | Host-evidence descendant retained after its premature `master` publication failed |

High-signal blobs from the accepted B14 subject are:

| Repository-relative artifact | Blob |
|---|---|
| `CONTINUITY.md` | `2b969a5008896ed758f9186ff384eec558774907` |
| `HANDOFF.md` | `5934735b018286b9425a505248e708f0b93d0bd5` |
| `MISSION_STATE.json` | `51fbf1f1679529f972bc17e93fab6f04387f75ed` |
| `experiments/iter134_neuroncap_placebo_semantics_execution/HYPOTHESIS.md` | `3f0b768f56c0d63af7acb8b093b4ea83c3ccf25a` |
| `experiments/iter134_neuroncap_placebo_semantics_execution/RESULT.md` | `183396a472442906db60dd3bb88644b7094bc99d` |
| `experiments/iter135_neuroncap_blind_braking_dose_response/HYPOTHESIS.md` | `adb1c7448f85396cde273ead452f27e3b0fca500` |
| `experiments/iter124_manuscript_report_freshness/verify_manuscript_report_freshness.py` | `37502c722efcf3d9c7c906c8cebee01d0cfcb2ed` |
| `experiments/iter124_manuscript_report_freshness/RESULT.md` | `6670b1c1a1a6983f6004e58586b9091a2ce9119d` |
| `docs/paper/MANUSCRIPT.md` | `5cdd3378e6e7d82596c9c8fc1cc6376770756336` |
| `docs/paper/paper.tex` | `37af11aa438282492bfe310562f1f553a3ec827a` |
| `docs/paper/sentinel-arxiv-submission.tar.gz` | `118a188537886c26b5812e4c99b8021bb2711bd6` |

The local failed generation-fifteen commit carries
`CONTINUITY.md` blob `63902b3f2346171dba771b317df35c9eec8e58b5`,
`HANDOFF.md` blob `03427cbd0ad734d5029e4452fd7c218d33079c90`,
and `MISSION_STATE.json` blob
`bd1318471de2c336fdf7f79926cc62ca7012642b`. They are committed incident
evidence, not accepted source state.

At audit time the Sentinel worktree had 15 modified paths. It was excluded.
For nonconflation, its three dynamic worktree artifacts hashed to:

| Excluded worktree artifact | Worktree blob |
|---|---|
| `CONTINUITY.md` | `b9f5f372d4682b958f2eb787c0d1a1fa70699c72` |
| `HANDOFF.md` | `3ceee919ca4961be53e2b11627bb1ef6160c2a4a` |
| `MISSION_STATE.json` | `fed330af0eaa1c77f5ceef92d96408c5c2ad59dc` |

The audit therefore did not promote the dirty correction from static `IDLE` to
`UNKNOWN`, stricter nested-receipt validation, or later lifecycle stops into a
claim about accepted Sentinel behavior.

### Telos

The Telos audit used the following exact, distinct committed subjects:

| Classification | Commit | Tree | Meaning in this packet |
|---|---|---|---|
| Audited committed subject | `25b591d9522d7981dba6186d349e83778acd46d4` | `78300461eb4576ae7d5070f517789347b5ca1773` | Primary committed audit subject |
| Merged `master` observed by the audit | `7307e0c1c4083443698cfde8f0ab20a27518717c` | `08603ad9b7bb718dadbe40acefe173f56bf77f8a` | Distinct merged ref; no authority inferred from the ref name |
| Published branch tip observed by the audit | `bd5595fe03ee7784c8257205b1285eafc66b7584` | `723ab3c6df88481cd255cad9fcf666061b2f5514` | Distinct published branch subject |

High-signal blobs from the audited committed subject are:

| Repository-relative artifact | Blob |
|---|---|
| `CONTINUITY.md` | `747fcc985795ba7fb2b42572d7e77f517497dd95` |
| `docs/HANDOFF-2026-07-19-iter238.md` | `bbc5a7a98f60cbef88b24ba7a9cf3f0a2ae470c9` |
| `docs/TELOS-AUDIT-2026-07-19.md` | `2c78dffffc7910e80320bff8e77b4d02031f3cca` |
| `experiments/iter235_witness_recovery/RESULT.md` | `c6ebb1a188dfdafc9bfaf69518cb858095de243f` |
| `experiments/iter236_transfer_analysis_reconstruction/RESULT.md` | `e39e0f0083bff9f9c868c550d091ddba5b7296e2` |
| `experiments/iter237_truth_maintenance_gate/RESULT.md` | `31de061210b39557095dcdfd6a687f1cd7a2916f` |
| `experiments/iter238_claim_seal_workflow_controls/proof/workflow_retirement_receipt.json` | `aaf44eb4401d71691244ad4b8f5317af8133da9d` |
| `mission/current.json` | `cfcef17514acb860ca98497a1f11ac57cf7b3d46` |
| `mission/seal_registry.json` | `e0937a9f11f4b2a627f3ac08ea7d68d8cfada23f` |

The contemporaneous Telos worktree had 18 modified and 10 untracked paths,
with nothing staged. It was excluded. In that candidate tree, local
current/paper/seal/workflow/index checks passed, but an untracked claim
registry failed binding, digest, and coverage validation; a historical
learning guard also accepted a stale iteration-207 pointer while the current
baton was iteration 238. Neither the dirty registry nor its prose is evidence
of accepted Telos state.

### Inbar

The Inbar audit inspected the FieldTrue source repository. Its initial subject
was commit `e954b23688e324acf516871ea9029bdc371b754e`, tree
`042132ff294f03a04cc80890c791a14007c5220b`, with dirty memory/extraction
bytes; `HANDOFF.md` then became dirty concurrently. Those worktree bytes were
excluded.

A separate process later produced the clean subject used for exact committed
evidence:

| Classification | Commit | Tree | Meaning in this packet |
|---|---|---|---|
| Audited clean committed subject | `0f04aab32a64b7d7501aec1bf318270ef653d970` | `48a4e14bd978999f5b5c35c73c84c9f1a4baf418` | Clean when observed, three commits ahead of its upstream; upstream distance is not authority |

High-signal blobs from that subject are:

| Repository-relative artifact | Blob |
|---|---|
| `README.md` | `50fa073a4f21842d48aeff39105173c0b704c507` |
| `CONTINUITY.md` | `cb29dbde7bf21531e4ae926817047b5b708589f8` |
| `HANDOFF.md` | `014187c8431b47fed7fd1020d13d329b7b195660` |
| `memory/research_engine_extraction.jsonl` | `8b7b927969c732a99ce3ffba4835eb38b27cbfc0` |
| `claims/registry.jsonl` | `6ae7dab1d276e2b96d4d3d0755b3134935606181` |
| `docs/research/ITER001_SOURCE_ROLE_AUDIT.md` | `3329e4967a0f766d833ef15cf1e66de28ba532e1` |
| `experiments/iter001_physical_causal_evidence_acquisition/AMENDMENT_006.md` | `86ea17b82ebaf96839a8ff6a1faaa56a10fa9406` |
| `experiments/iter001_physical_causal_evidence_acquisition/AMENDMENT_006_APPROVAL_DEFECT.md` | `b51931098e8eacf6cc44fa3e0d1fff3e230004ca` |
| `experiments/iter001_physical_causal_evidence_acquisition/AMENDMENT_006_EVIDENCE_DEFECT.md` | `fc4f8698da4e73c0b51a5bea317ac4dcd89ad863` |
| `experiments/iter001_physical_causal_evidence_acquisition/RESULT_COMPENSATOR_FAMILY.md` | `76af6f191d126da2403992e53f0a2706942cfca8` |
| `experiments/iter001_physical_causal_evidence_acquisition/RESULT_MASKING.md` | `c6651d285c97de6cc3c88f818e0631fc4de39c56` |
| `experiments/iter001_physical_causal_evidence_acquisition/RESULT_SUSCEPTIBILITY.md` | `684e40c93231e97f40d76ab76254a34b4fc1d5a5` |
| `experiments/iter001_physical_causal_evidence_acquisition/RESULT_SUSCEPTIBILITY_CONFIRMATORY.md` | `e6c0795a69201eb590f68cff1afd0e9ef287e8e4` |

The retained version-22 receipt at
`evidence/validation/inbar-core-validation-20260719-v22/receipt.json`, blob
`6047b9cee3ae8a61062f9893b6393871f02b4fb9`, reported 1,504 passing checks,
but it is same-operator and non-independent. It is bounded integrity evidence
only, not scientific, human-decision, approval, or authority evidence. The
source's canonical control authority remained unsealed; its honest mission
state was one acquisition-contract blocker, not a physical diagnosis or causal
result.

## Bounded operational corroboration

The operational-log check was intentionally small and excluded private
reasoning.

### Sentinel

One operational record corroborates this order:

1. candidate `619083e41c89bdf7bc83fa7443116cf568053673` was committed
   and a disposable validation run failed with two synthetic-Git fixture
   errors;
2. the candidate was amended to `4d8801605f1e285c5000b4220e965e97a8aff345`;
3. a disposable-branch run passed, after which that commit was pushed to
   `master`;
4. the distinct `master` run failed because a reachable parent object was
   missing in a synthetic repository;
5. `master` was restored with an exact lease to B14
   `69bd2e2face00ccabb426382347eb04e8a0dbe83`; and
6. the restore run passed both configured lanes.

This corroborates commit/push/failure/restore order. It does not establish a
human decision, independent verification, the root cause of the filesystem
failure, or scientific validity.

### Telos

Local operational metadata corroborates the iteration-237
preregistration/correction/merge sequence and an iteration-238 dry run followed
by 29 disable requests, 29 read observations, zero observed forbidden
operations, and a receipt commit. It proves only the bounded command/outcome
order. It does not establish authorship, human intent, provider completeness,
semantic truth, independence, or scientific validity.

### Inbar

One 2026-07-19 operational record corroborates evidence-correction patches, an
initial correction commit, a later amend, validation calls, and a push that
returned success. No matching 2026-07-18 operational record was found, so the
original defect actions and authorship cannot be inferred. The later clean
commit `0f04aab32a64b7d7501aec1bf318270ef653d970` appeared during the audit,
but its exact creation call was not mapped. The operational record therefore
does not prove who created the final subject or that any human reviewed it.

## Lessons absorbed into Gate A

| Source | Absorbed architecture lesson | Bound retained meaning |
|---|---|---|
| Sentinel | Freeze the estimand, independent unit, falsifier, verdict order, and claim boundary before data; commit raw proof before a single frozen analyzer; retain confounds, nulls, estimator disagreement, and analyzer defects | Scientific protocol discipline, not proof that Sentinel's result generalizes |
| Sentinel | Bind a gate to the exact released bundle and member bytes; make `unknown` and terminal proof explicit; reject Boolean/float impostors in exact integer receipt fields | Artifact/lifecycle/schema obligations, not publication or runtime authority |
| Telos | Use prospective seals, additive evidence windows, successor seals, explicit supersession, and typed provider `null`/`unknown` bounds | Append-only claim-control pattern, not truth conferred by a seal |
| Telos | Bind time-bounded remote-state receipts to exact operations and observations; default deny when settlement is incomplete | Operational observation pattern, not a perpetual provider lease |
| Inbar | Make the approval basis machine-visible; protect the human ceremony; separate proposer, decision maker, signer, verifier, and effective control; require rights before bytes | Bounded decision-assurance requirement, never evidence of cognition |
| Inbar | Run a measurement-free entailment/circularity falsifier before promoting an empirical effect; preserve correction edges and real unknowns | Refusal boundary distinguishing implementation correctness from empirical support |

These lessons refine existing Odeya laws. They do not make any source program a
scientific or policy authority for Odeya.

## Patterns explicitly rejected

| Rejected pattern | Reason for rejection |
|---|---|
| Green CI, a digest, a signature, consensus, or polished prose as truth | Each proves only a bounded mechanical or representational property |
| A sibling source file standing in for the shipped artifact | The checked bytes and released bytes can disagree while the gate remains green |
| Mutable handoff prose, a static `IDLE`, or absent containers/processes as terminal evidence | None proves completion, settlement, or authority |
| Same effective operator proposing, signing, approving, and semantically verifying | Role labels do not create principal independence |
| A human-readable or agent-readable governance key as proof of human intent | Key possession and a declared human principal do not prove review or decision |
| Historical and current pointers that can both pass | A stale baton can silently authorize obsolete state or overclaims |
| Provider initiation, timeout, retry exhaustion, or a successful transport return as completion or zero spend | External completion and spend settlement remain independently unknown until observed |
| Fragmented provider ledgers and retrospective ratification | They permit partial observation to be rewritten into a stronger story |
| Definition-derived geometry, hand-authored labels, or a predictor sharing outcome-generating geometry with its reference as empirical evidence | The reported effect can be entailed without claim-bearing measurement |
| Recursive hard-coding of campaign Git history as the lifecycle kernel | It is brittle campaign control, not a typed append-only canonical event model |

## Precise Gate A deltas

These are architecture obligations. They add no executable surface and do not
alter the retained 43-command, 60-event, 25-state/reducer-family, 11-owner, and
P0 first-slice boundary by implication.

### PRQ-013 — Human-decision assurance

[ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
adds PRQ-013 as `unresolved_blocking`. A declared human principal, user
presence, user verification, authorization gesture, or valid signature cannot
fill a policy-defined human-only slot without a separate,
nonrecursive `HumanDecisionAssurance` subject.

The candidate obligation must bind:

1. exact decision and displayed-material bytes, candidate digest, decision
   value, basis, limitations, delegation, objections, conflicts, and quorum;
2. distinct proposer, decision maker, signer, verifier, and effective-control
   identities required by policy;
3. a verifier- or relying-party-generated unpredictable challenge tied to the
   exact decision, ceremony session, and bounded time, plus a separate
   human-initiated confirmation gesture;
4. authentication-intent evidence, user presence, user verification,
   principal identity-proofing and principal-to-authenticator binding, and a
   phishing-resistant authenticator as ceremony components, without promoting
   any of them to proof of cognition or consent;
5. authenticator, key, and session custody plus explicit exclusion of
   unattended agent/model/tool signing reach;
6. delegation scope/depth, objections, effective control, distinct-principal
   separation, conflicts, and quorum evaluation;
7. replay, expiry, withdrawal, and contradiction handling; and
8. sanitized ceremony evidence and independent verification, excluding raw
   private reasoning, reusable secrets, signing material, and unrestricted
   prompts.

The strongest eligible claim is only that accepted ceremony evidence is
attributable to the declared principal/authenticator under the named
identity-proofing and binding profile and includes an observed human-initiated
confirmation gesture over exact bytes. It cannot claim what the person thought
or understood.

Known-bad fixtures must reject an agent-held or agent-reachable key, stale or
replayed challenge, changed decision/display bytes, hidden delegation,
objection mismatch, shared-credential quorum, omitted user-presence or
user-verification evidence, timeout/silence, raw private reasoning, and
self-closure. T1 `AuthorityAssignment` remains blocked until the T0
individual-assurance foundation candidate, exact census, profile/evidence
contracts, singleton-verifier design, and synthetic known-bads are complete.
The `AssuredDecision` wrapper, successor consumers, transitive migration,
end-to-end refusals, and accountable review follow their T1/T2 dependencies;
they are not a circular prerequisite for constructing those dependencies.

### Exact bundled-artifact fixture

Every release/publication gate must consume the exact release-manifest digest,
bundle identity, member path, member byte digest, and the extracted or rendered
claim-bearing artifact it purports to validate. A source-local sibling,
generated precursor, README, or editable manuscript is not a substitute.

The mandatory known-bad mutation keeps the required claim boundary in a sibling
source while removing it from the bundled member. The gate must fail. A passing
fixture proves only exact artifact binding and the declared checks; it does not
prove scientific truth or authorize publication.

### Stale canonical-baton fixture

Exactly one canonical current-state pointer must resolve to the current
terminal seal, handoff, and supersession frontier. Historical batons remain
retained as history but cannot satisfy a current-state gate.

The mandatory known-bad mutation points a historical learning/current record
to iteration 207 while the terminal baton is iteration 238. The gate must
reject the stale pointer, any simultaneous multiple-current condition, a
missing successor edge, and a current record whose bound result/seal digests do
not match the terminal frontier.

### Provider interruption and unknown completion/spend fixture

Provider request initiation, transport success, local timeout, interruption,
retry exhaustion, and external completion are separate observations. Completion
and spend settlement are also separate. If the response is lost after
initiation, both external completion and spend remain `unknown` unless
independently settled; the reservation remains held and retry remains denied
where duplication could be consequential.

The mandatory known-bad trace initiates one provider action, loses the terminal
response, and then attempts to mark the action complete, convert spend to zero,
release the reservation, or retry. Every promotion must fail. Later
contradictory settlement must append a discrepancy/correction rather than
rewrite the interruption.

### Measurement-dependence falsifier

Before an empirical or causal effect becomes claim-eligible, the protocol must
run a preregistered measurement-dependence screen:

- freeze an exclusion/taint graph and remove claim-bearing measurements,
  outcome descendants, proxies, affected denominators, censoring indicators,
  and labels before attempting to reproduce the reported effect; and
- test whether predictor and reference share command-window or
  outcome-generating geometry, including analytic derivation and
  counterfactual/permutation dependency checks.

One rounded-value or coarse-label match blocks empirical promotion pending
adjudication; it does not alone prove entailment. If analytic or dependency
evidence demonstrates that the effect is invariant to admissible changes in
the withheld measurements, or that predictor and reference are circularly
coupled, the empirical/causal interpretation is `invalid`
(`INVALID_CIRCULAR` in the source fixture vocabulary). Orthogonal
implementation or analytic-identity evidence may remain valid within its
declared scope, but it cannot settle the empirical or causal claim. Without
that demonstration the result remains `blocked` or `inconclusive`.

The companion closed-loop check must also measure whether the intervention
changes censoring, termination, observation opportunity, or realized exposure.
Scheduled equality is not realized equality when the intervention changes how
much of its own dose can be observed. Without a design or estimator that
identifies that dependence, the causal question remains `inconclusive`.

## AFT-001 — Later preregistered research candidate only

`AFT-001`, **Abstention Frontier**, is not a Gate A prerequisite, an active
mission, an Inbar artifact, or an implemented capability. It is a deferred
research candidate: preregister measurement of marginal assurance gained
against the cost and latency of independent-verification substitutes.

A later protocol would require:

- human-ground-truth adjudication;
- diverse, preregistered claim strata;
- a comparator ladder from deterministic checks through progressively more
  independent verification;
- held-out evaluation;
- calibrated residual-risk and abstention curves; and
- explicit compute, money, latency, human-effort, false-accept, and
  false-reject accounting.

It is deferred until Gate A is accepted and the operator grants separate
research authority. It creates no fifth active mission, no provider
authorization, no engine/runtime claim, and no reason to interrupt the Gate A
dependency order.

## Exact next mission order

1. Preserve this extraction as architecture evidence together with ADRs 0089
   and 0092 and the machine-visible PRQ-013 inventory/checker; validate their
   exact scoped tree and obtain context-isolated adversarial review. Do not
   represent retained mutations or model review as PRQ-013 closure.
2. Freeze only the T0 PRQ-013 individual-assurance foundation as unissued
   candidates: exact profile/evidence-store/backing-byte contracts, census,
   singleton-verifier designs, and synthetic conformance/refusal vectors.
3. Complete the remaining T0 prerequisite corrections, including
   `C5-WORK-LEASE-RELEASE-CLAIM-001` and exact profile/member/reducer identity
   work. Admission, assignment, lease, dispatch, and runtime remain blocked.
4. Construct and prove the T1 `AuthorityAssignment` vertical contract.
5. Complete the exact 42 payload schemas, 43 command records, 60 event records,
   25 state/aggregate subjects, and 25 reducer records without widening the
   retained first-slice boundary by implication.
6. Only after the required T1/T2 authority, currentness, quorum, and consumer
   dependencies exist, construct unissued `AssuredDecision` and
   successor-consumer candidates; prove the exact transitive migration and
   end-to-end refusal corpus without mutating retained identities.
7. Construct one digest-coherent registry/root/C0/checkpoint/witness/P0 and
   inactive activation-candidate chain.
8. Produce two non-sharing architecture-time reference reducer
   implementations, fixture harnesses, and two independently isolated
   scientific verifier paths. They remain design evidence, not runtime.
9. Retain replay, interruption, provider-unknown settlement, recovery,
   correction fanout, resource/authority race, bundled-artifact, stale-baton,
   measurement-dependence, proof-mission refusal, and rights-settled import
   evidence.
10. Obtain accountable statistical, physical/metrology/VVUQ/safety,
   security/privacy, distributed-systems, and accessibility reviews.
11. Produce one immutable candidate manifest and clean commit for Daniel's
    exact-byte Gate A accept, reject, or amend decision. Gate A evaluates
    ceremony architecture and independent/synthetic conformance evidence; it
    neither requires nor authorizes a live ceremony.
12. Only after Gate A and separate authority may a bounded Gate B protected
    ceremony or other probe be run. AFT-001 requires its own later
    preregistration and authority. Gate C remains required before one bounded
    runtime increment and owns runtime-conformance exit evidence.

The other four cross-program fixture refinements do not become T0 identity
prerequisites by implication. The exact-bundle fixture belongs to the
publication/repository-review contract before that substitution class can be
reported closed; the stale-baton fixture belongs to current-state,
handoff/recovery, and architecture-review closure; the provider-interruption
fixture belongs to external-effect/resource settlement before those contracts
can be accepted; and the measurement-dependence fixture belongs to the
scientific protocol and claim compiler before an affected empirical claim can
be accepted.

## Non-authorization and residual limits

This packet:

- does not accept Gate A or any PRQ;
- does not issue a canonicalization profile, registry member, root,
  checkpoint, P0, activation, grant, lease, assignment, or publication seal;
- does not establish independent scientific verification for Sentinel, Telos,
  Inbar, or Odeya;
- does not import active dirty trees or source-program scientific claims;
- does not authorize a provider call, credential use, data import, spend,
  external write, repository publication, scientific publication, deployment,
  physical action, model admission, or runtime implementation; and
- does not authorize AFT-001 or create another active mission.

The correct disposition remains `blocked` wherever evidence, settlement,
independence, rights, or accountable human decision is absent.
