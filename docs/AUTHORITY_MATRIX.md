# Authority and Separation Matrix

Status: proposed constitutional contract, 2026-07-16. This matrix resolves role meanings and the leading human/service boundary. ADR 0014 additionally closes the first-slice authority alternatives and role-slot cardinality; the bounded composite model passes, while executable refinement, operator acceptance, root/P0 evidence, and independent race review remain blocked.

## First principle

Authentication answers who a principal is. An assignment answers which authority role that principal may hold. A policy decision answers whether a requested action fits current rules. A grant authorizes one bounded action class. A grant-use record proves that a specific command reserved or consumed it. None substitutes for another.

Successful signature verification proves only that exact bytes validate under
the referenced public key, algorithm, and trust profile; it does not identify
who caused the signing operation or controlled the private key. Successful
authentication proves only the accepted authentication ceremony. Neither
proves human review, understanding, or substantive decision intent.

Odeya has nine founding authority roles:

| Role | Owns | Does not own |
|---|---|---|
| Proposal | Admit, defer, decline, or withdraw a question for research | Truth of the thesis or authority to execute it |
| Protocol | Freeze prospective scientific meaning, amendment, fork, and supersession | Safety, data use, spend, execution, result, or release |
| Safety | Determine whether a bounded action is permitted under accepted controls | Scientific support, data rights, resource availability, or publication wording |
| Data rights | Acquisition, processing purpose, model exposure, retention, deletion/legal hold, training, and disclosure rights | Scientific validity or operational safety |
| Resource | Compute, human time, paid APIs, credentials, rate, quota, and spend envelope | Permission to perform an otherwise unsafe or unlawful action |
| Execution | Which identity may perform the exact authorized work/effect | Power to widen protocol, resources, or claim scope |
| Verification | What a named verification run establishes under its method and independence profile | External-world outcome, generic truth, or publication |
| Outcome | What occurred in an external provider, lab, testbed, recipient, or other world-facing system | Scientific interpretation beyond retained observation |
| Publication | Exact audience, channel, bytes, redaction, wording, embargo, correction, and withdrawal | Scientific validity or permission to alter private evidence |

The deterministic adjudicator applies a frozen consequence rule; it is not a tenth discretionary authority. If a rule cannot derive a determination, it refuses and escalates rather than asking a model to improvise.

## Principal classes

| Principal class | May propose | May hold assignment | May issue grant | May observe/report | May make human-only decision |
|---|---:|---:|---:|---:|---:|
| Human | yes | yes | yes, within issuer assignment | yes | yes |
| Organization/legal entity | yes | yes, with accountable human binding | via authorized service/human | yes | no direct session; accountable human signs |
| Deterministic service | yes | yes for mechanical roles/actions | yes only under preauthorized policy and delegable parent assignment | yes | no |
| Instrument/provider adapter | evidence only | no discretionary role | no | yes, as untrusted/qualified observation | no |
| Model run | proposal only | never for safety, rights, resource, verification, outcome, or publication | never | candidate observation only | no |
| Tool/workload | proposal/execution result only | execution identity under a grant, not authority assignment | never | candidate observation only | no |

Service automation may narrow and instantiate a preauthorized low-risk grant. It cannot create new constitutional authority, widen scope, change risk, or convert a missing human decision into approval.

## Human-decision assurance boundary

Every `H` slot remains unsatisfied until a future
`HumanDecisionAssurance` contract binds all of the following for one exact
decision:

- the exact candidate bytes, exact displayed material-set bytes, their digests,
  the explicit decision value, basis, limitations, and an admitted rule proving
  the displayed and decided subjects match;
- a protected explicit ceremony with a verifier- or relying-party-generated
  unpredictable challenge plus a separate human-initiated confirmation
  gesture, controlled time, expiry, and single-use replay protection;
- user presence and user verification results, principal identity-proofing and
  principal-to-authenticator binding, plus authenticator, signing-key, and
  session-custody evidence that excludes unattended agent, model, tool, or
  worker control;
- declared delegation source, scope, and depth; objections; conflicts;
  effective-control group; and distinct-principal quorum result; and
- sanitized ceremony evidence and independent verification that retain no
  reusable secret, signing material, raw private reasoning, or unrestricted
  prompt/model output.

The bounded claim is only that the accepted ceremony evidence is attributable
to the declared principal/authenticator under the named identity-proofing and
binding profile and includes an observed human-initiated confirmation gesture
over the exact bytes. It is never a claim about cognition, comprehension, or
mental state. No current schema is claimed to satisfy this contract; PRQ-013
remains blocking under
[ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
and the
[cross-program process-evidence packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md).

## Founding action matrix

Legend: `H` human decision required; `S` a deterministic service may decide under a human-approved policy/ceiling; `O` observation only; `—` role not sufficient. Multiple entries in one row are all required unless marked alternative.

| Action | Proposal | Protocol | Safety | Data rights | Resource | Execution | Verification | Outcome | Publication | Rule |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Submit thesis | S | — | — | — | — | — | — | — | — | Ingress grants no truth or execution status |
| Admit/defer/decline mission | H | — | H for R2+ screen | H if private/restricted data proposed | H if material allocation committed | — | — | — | — | Admission means worth testing only |
| Freeze confirmatory protocol | — | H | referenced | referenced | referenced | — | — | — | — | Exact digest and exposure history |
| Record exposure | — | S/O | — | S/O | — | — | — | — | — | Exposure is monotonic and cannot be suppressed |
| Amend/fork after exposure | — | H | H if safety affected | H if rights affected | H if resources affected | — | — | — | — | Always prospective; affected roles reapprove |
| Acquire/process D0 public data | — | — | S | S | S | S | — | — | — | Purpose and source role still recorded |
| Acquire/process D1–D3 data | — | — | H/S per tier | H | H/S per ceiling | S | — | — | — | D3 requires human rights decision and narrow recipient set |
| Issue ordinary R0/R1 worker lease | — | — | S | S | S | S | — | — | — | All upstream grants must bind exact manifest |
| Material spend or paid provider beyond ceiling | — | — | referenced | referenced | H | S | — | — | — | Reservation and command commit atomically |
| R2 external write | — | — | H | H if data disclosed | H | H | — | — | H if publication-like | Intent before dispatch; reconciliation required |
| R3/R4 or physical action | — | — | H + independent H | H where data involved | H | H + independent interlock | — | H for settlement | H if disclosed | General engine has no standing grant |
| Assign verifier | — | — | — | S/H for exposure | S | — | H/S under policy | — | — | Producer cannot choose terminal verifier |
| Run deterministic verification | — | — | — | active exposure grant | S | separate S | S | — | — | Known-bad controls and observed independence required |
| Settle model-assisted/expert verification | — | — | — | active exposure grant | referenced | — | H independent of producer | — | — | Model critic supplies finding, never settlement |
| Observe provider/lab outcome | — | — | — | applicable grant | — | O | — | O | — | Observation does not decide meaning |
| Settle ambiguous external outcome | — | — | H if consequential | H if disclosure/data effect | referenced | separate reconciliation grant | — | H or qualified S under exact oracle | — | Retains applied/not-applied polarity |
| Adjudicate scientific result | — | — | — | — | — | — | verified inputs | — | — | Pure registered rule; refusal if unresolved |
| Compile eligible claim version | — | — | — | disclosure not implied | — | — | required runs | — | — | Pure claim compiler at exact ledger position |
| Authorize private/restricted release | — | — | H | H | H if channel cost | — | referenced | referenced | H | Exact sealed manifest; single use |
| Authorize public release | — | — | H | H | H if material | — | independent verification required | external outcomes reconciled | H | Generator cannot be sole signer; no timeout approval |
| Correct/retract/withdraw | — | H if protocol meaning affected | H if safety reason | H if rights reason | — | — | H/S for evidence impact | H if outcome changed | H | Fanout to every dependent projection/publication |
| Promote strategy candidate | — | H | H | H if data/training affected | H | H | independent eval | grounded outcome referenced | — | Candidate generator excluded from final quorum |
| Break glass | — | — | H + second H | H if data affected | H if resource affected | bounded H | — | — | H if release affected | Cannot rewrite evidence, adjudication, or prior events |

Exact thresholds for “material,” risk tiers, and data classes belong to a versioned policy profile. Undefined thresholds deny rather than default low.

## Separation constraints

For the affected scope:

1. A model/tool/workload that produced a claim-bearing artifact cannot be its terminal verifier, outcome settler, or publication authority.
2. Verification requires a different execution identity and process. Additional principal, host, code, evaluator, model, data, operator, or institution separation follows the mission’s independence vector; `unknown` never satisfies `separate_required`.
3. R3/R4 safety approval and physical execution require distinct accountable humans or an external independent safety authority plus a physical interlock outside Odeya.
4. Public claim publication requires at least one verifier principal distinct from the producer and one human publication principal. The publication principal may also be protocol owner in a founding low-risk mission only when the conflict is disclosed and the accepted policy permits it.
5. A strategy candidate’s generator cannot supply the independent evaluation or final promotion quorum.
6. A rights decision cannot be inferred from possession, public reachability, a provider’s acceptance, or a source signature.
7. Root/constitutional assignment cannot be issued or rotated solely by the incoming assignee.
8. One human may hold multiple founding assignments for R0/R1 while staffing is small, but every decision remains a separate signed record. Where this matrix requires distinct principals, work blocks until an independent principal is available.

Role separation is evaluated over effective control, not display names. Shared credentials, employer direction, hidden context, common evaluator code, or undisclosed conflicts can defeat nominal separation and must be represented in the independence/conflict records.

## Root assignment and constitutional bootstrap

The first event cannot depend on a self-referential grant. Bootstrap uses a `RootAuthorityManifest`, retained outside and then anchored inside the ledger, containing:

```text
manifest ID/version and canonical digest
Odeya repository/candidate identity
founding operator principal and authentication binding
initial role assignments and explicit overlap disclosure
maximum risk/data/publication scope
prohibited self-approval combinations
recovery/rotation principals and quorum
effective time, review/expiry time, revocation path
policy/schema/checkpoint trust roots
signed decision evidence
```

For an architecture-only local fixture, Daniel may be the sole founding operator, but that fixture grants no external effect or public release. Before real capital, private customer data, public publication automation, or R2+ action, the root profile requires a second accountable recovery/review principal.

Bootstrap steps:

1. independently verify principal identity and manifest bytes;
2. canonicalize and sign the manifest under the accepted key profile;
3. create the genesis checkpoint binding manifest digest, schema/profile versions, and empty/initial stream heads;
4. record initial assignments, never operational grants, from the manifest;
5. issue bounded grants only through ordinary policy/command semantics;
6. witness the checkpoint outside the primary database;
7. test recovery and rotation before increasing risk.

Rotation adds a new root-manifest version and checkpoint. It cannot delete the prior root or re-sign old events.

The first mission command additionally requires the exact separately admitted
`P0.constitutional-recovery-admission` embedded in RegistryActivation. P0 binds
this non-self-issued root manifest, the EngineContractRoot/C0 bundle, witnessed
checkpoint, and a clear current recovery/fork/quarantine frontier. It is not an
assignment or grant and cannot be produced by an ordinary mission command.

## PolicyDecision admission record

[`PolicyDecision` 0.1.0](../schemas/policy-decision.schema.json) is a pure immutable admission-cohort record, not an authority aggregate and not a caller field. The deterministic kernel produces it from the canonical request digest; exact CommandContractRecord; controlled time; locked aggregate/reference frontier; root, checkpoint, and policy-registry snapshot; exact policy bundle/rules; retained policy-input bytes; and engine build/configuration identity. Its disposition is `allow | deny | indeterminate`; outage, timeout, unsupported input, engine error, or conflicting rules can never become allow. Typed obligations name their exact enforcement point.

The policy result is a filter only. It cannot create an assignment, issue a grant, satisfy quorum, reserve resources, widen data rights, or prove scientific validity. `CommandEnvelope` structurally carries no policy-decision reference. The kernel persists the PolicyDecision, CommandContractRecord-selected validation/reference/authority/resource records, [`AdmissionEvidenceBundle` 0.1.0](../schemas/admission-evidence-bundle.schema.json), receipt, and accepted event cohort in one transaction. Every checkpoint commits the separate admission-evidence set so replay retains why a result occurred. JSON Schema proves only shape; semantic validation must prove inputs, activation, deterministic evaluation, obligation enforcement, evidence-profile completeness, receipt/event equality, and digest/signature correctness.

## Grant lifecycle and time

```text
assignment recorded
  -> authorization request
  -> policy decision
  -> grant issued
  -> ordinary in-ledger command: reserve + commit + consume atomically
     OR
  -> cross-boundary effect: exact use reserved at intent commit
       -> dispatch claim revalidates grant + consumes use atomically
       | revoke / expiry / cancellation wins first -> reservation released, dispatch denied
  -> exhausted | expired | revoked
```

- Every grant declares its legal consumption point: `domain_commit` or `dispatch_claim`. A caller or adapter cannot choose it per attempt.
- Grant issue, `authority.grant_use_reserved`, `authority.grant_use_reservation_released`, `authority.grant_used`, exhaustion, expiry observation, and revocation are immutable facts.
- A reservation binds one reservation ID to the exact grant, command/effect, request/payload digest, target/destination, use count, resource reservation, not-after time, and causal intent. It reduces available use/concurrency while active but is not historical consumption.
- Ordinary commands with no cross-boundary effect reserve and consume in their one canonical transaction; no durable intermediate reservation exists.
- A cross-boundary effect that must remain revocable before dispatch creates `authority.grant_use_reserved` with `external_effect.authorized` in T1. The later dispatch-claim transaction rechecks assignment/grant/revocation/expiry and atomically records `authority.grant_used(consumption_point=dispatch_claim)` with `external_effect.started`. Network/physical dispatch begins only after that commit.
- Revocation, expiry, cancellation, or reservation expiry committed before dispatch claim prevents consumption and records `authority.grant_use_reservation_released` with its typed terminal state/reason. Effect cancellation closes `authorized -> cancelled_before_dispatch` in the same batch. A dispatch claim committed first remains an in-flight historical use; later revocation blocks subsequent attempts but cannot erase it.
- Releasing an unused reservation restores only the reserved capacity allowed by the original grant. It never authorizes a different payload, effect, destination, time, or command.
- Admission evaluates `not_before <= controlled_time < expires_at` from canonical grant bytes even if an expiry projection lags.
- `issued_at`, `not_before`, and `expires_at` order is a semantic invariant, not merely a timestamp format check.
- A revocation committed before dispatch claim prevents dispatch. A dispatch claim committed first remains an in-flight historical fact and must be cancelled/reconciled.
- Delegation can only produce a strict subset of role, action, resource, risk, data, time, use, concurrency, and target scope, with lower remaining depth.
- A new grant never retroactively authorizes a prior action.

### First-slice action-instance grants

The bounded first-slice profile narrows ordinary `domain_commit` grants further:

```text
proposal < protocol < safety < data_rights < resource
< execution < verification < outcome < publication
```

Every CommandContractRecord contains closed authority alternatives. Trusted
kernel context selects exactly one; a caller cannot request the internal,
ingress, bootstrap, or assignment-only path. A bounded alternative declares a
finite ordered role-slot array. Each slot resolves to a distinct grant bound to
the exact command ID, canonical request digest, target, role, and controlled
time with `max_uses=1`.

An accepted N-slot batch emits N separately identified
`authority.grant_used(domain_commit)` occurrences before the domain cohort and
N matching `authority.grant_exhausted` occurrences after it. Used and exhausted
sets are equal. Missing, duplicate, extra, reused, wrong-role, wrong-order, or
partially committed occurrences invalidate the whole batch. Rejection, noop,
and exact idempotent replay emit none. This first-slice law does not silently
change the separately modeled revocable `dispatch_claim` protocol for future
external effects.

## Required semantic checks

Before a command consumes authority, the validator must prove:

- assignment and issuer chain exist, are active, and permit the role/action;
- subject authentication/execution binding matches the command actor;
- command type/version, target stream/aggregate, protocol, manifest, stage, capability, purpose, data class, risk, and destination are within scope;
- controlled time, remaining uses, concurrency, resource/spend, egress, method, and sandbox limits pass;
- every dependency grant and policy decision is exact and active;
- quorum counts distinct effective principals where required;
- forbidden role overlap and producer/verifier/publication separation pass;
- every `H` slot resolves a nonexpired, nonreplayed PRQ-013 assurance record
  over the exact displayed and candidate bytes; a signature or authentication
  result alone is insufficient;
- delegation is a strict subset at every edge;
- command-request digest matches the grant’s authorization request;
- reserve/use/release/revoke ordering and the grant's declared consumption point are compatible with the command/effect transition; effect intent and its reservation commit together, and dispatch claim plus use consumption commit together.

JSON Schema cannot prove these relations. They require a pinned pure semantic rule registry, reference graph, controlled clock input, and race fixtures.

## Architecture falsifiers

This matrix fails Gate A if any trace can:

- create the initial root through a self-issued operational grant;
- use one grant for a different command, payload digest, protocol, target, purpose, data class, or destination;
- count aliases/shared credentials as distinct quorum principals;
- let a producer select or become its required independent verifier;
- let a timeout, policy outage, expiry projection lag, or missing human approve;
- revoke a grant while losing the retained fact that an effect was already in flight;
- consume a dispatch-bound grant at intent time, dispatch from an unconsumed/unrevalidated reservation, or release a reservation after its dispatch claim won;
- allow a service or model to widen a human-approved ceiling;
- accept `PRQ-013-KB-001`: an unattended agent can invoke a human-labelled
  signing key and produce a cryptographically valid signature over the exact
  candidate while the verifier-generated challenge, human-initiated
  confirmation gesture, identity/authenticator binding, user presence, and
  user verification are absent or `unknown`; the result must be
  `indeterminate` and cannot fill an `H` slot or quorum;
- publish bytes not identical to the human-approved manifest;
- apply a new policy or grant retroactively; or
- close a mission with active grants that can still dispatch consequential effects.

Acceptance requires non-executable adversarial traces for these cases, bounded model checking of reserve/use/revoke/quorum races, independent security review, and explicit operator approval. Runtime identity/policy conformance remains an implementation exit gate.
