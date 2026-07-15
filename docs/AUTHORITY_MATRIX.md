# Authority and Separation Matrix

Status: proposed constitutional contract, 2026-07-15. This matrix resolves role meanings and the leading human/service boundary. It remains blocked on operator acceptance, root-assignment evidence, and adversarial race review.

## First principle

Authentication answers who a principal is. An assignment answers which authority role that principal may hold. A policy decision answers whether a requested action fits current rules. A grant authorizes one bounded action class. A grant-use record proves that a specific command reserved or consumed it. None substitutes for another.

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

## Grant lifecycle and time

```text
assignment recorded
  -> authorization request
  -> policy decision
  -> grant issued
  -> use reserved
  -> command/effect committed + use consumed
     | command rolled back -> reservation released
  -> exhausted | expired | revoked
```

- Grant issue, reserve/use, release, exhaustion, expiry observation, and revocation are immutable facts.
- Admission evaluates `not_before <= controlled_time < expires_at` from canonical grant bytes even if an expiry projection lags.
- `issued_at`, `not_before`, and `expires_at` order is a semantic invariant, not merely a timestamp format check.
- A revocation committed before dispatch claim prevents dispatch. A dispatch claim committed first remains an in-flight historical fact and must be cancelled/reconciled.
- Delegation can only produce a strict subset of role, action, resource, risk, data, time, use, concurrency, and target scope, with lower remaining depth.
- A new grant never retroactively authorizes a prior action.

## Required semantic checks

Before a command consumes authority, the validator must prove:

- assignment and issuer chain exist, are active, and permit the role/action;
- subject authentication/execution binding matches the command actor;
- command type/version, target stream/aggregate, protocol, manifest, stage, capability, purpose, data class, risk, and destination are within scope;
- controlled time, remaining uses, concurrency, resource/spend, egress, method, and sandbox limits pass;
- every dependency grant and policy decision is exact and active;
- quorum counts distinct effective principals where required;
- forbidden role overlap and producer/verifier/publication separation pass;
- delegation is a strict subset at every edge;
- command-request digest matches the grant’s authorization request;
- reserve/use/revoke ordering can commit atomically with the event/effect intent.

JSON Schema cannot prove these relations. They require a pinned pure semantic rule registry, reference graph, controlled clock input, and race fixtures.

## Architecture falsifiers

This matrix fails Gate A if any trace can:

- create the initial root through a self-issued operational grant;
- use one grant for a different command, payload digest, protocol, target, purpose, data class, or destination;
- count aliases/shared credentials as distinct quorum principals;
- let a producer select or become its required independent verifier;
- let a timeout, policy outage, expiry projection lag, or missing human approve;
- revoke a grant while losing the retained fact that an effect was already in flight;
- allow a service or model to widen a human-approved ceiling;
- publish bytes not identical to the human-approved manifest;
- apply a new policy or grant retroactively; or
- close a mission with active grants that can still dispatch consequential effects.

Acceptance requires non-executable adversarial traces for these cases, bounded model checking of reserve/use/revoke/quorum races, independent security review, and explicit operator approval. Runtime identity/policy conformance remains an implementation exit gate.
