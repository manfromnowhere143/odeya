# Publication and External Release Protocol

Status: proposed architecture, 2026-07-15. This protocol removes circular grant/manifest dependencies and separates scientific eligibility, disclosure approval, byte sealing, dispatch, external settlement, correction, and withdrawal. It authorizes no release.

## Constitutional rule

Publication is a new consequential external effect over an exact bounded projection. It is never a property inherited from a mission, a supported result, a claim version, a repository setting, a successful channel request, or a missing objection.

```text
eligible ClaimVersion(s)
  -> PublicationCandidate
  -> ReleaseRequest
  -> PublicationDecision(authorized | denied)
  -> PublicationManifest sealed deterministically from exact candidate + decision
  -> single-use PublicationGrant bound to final manifest digest
  -> ExternalEffect intent + release dispatch
  -> external observation and settlement
  -> released | confirmed_not_released | completion_unknown
  -> correction / replacement / withdrawal when required
```

Every arrow is a distinct command/event fact. No arrow implies the next.

## Why ordering matters

The earlier draft made the manifest contain a publication grant while the grant had to contain the manifest digest. That creates an impossible cryptographic cycle. The corrected sequence is:

1. a candidate contains the proposed disclosure bytes and targets;
2. a human publication decision authorizes or denies that exact candidate digest;
3. a deterministic seal rule creates the final immutable manifest from the candidate and decision;
4. only then can a single-use grant bind the final manifest digest;
5. dispatch consumes that grant and records an external-effect intent before any channel call.

The final `PublicationManifest` therefore contains candidate and decision references but not its later grant. The grant points forward to the final manifest digest. Release effect records point to both.

## Objects

Closed structural candidates now exist for `PublicationCandidate` and
`PublicationDecision`; `PublicationManifest` 0.2.0 contains the candidate and
decision references but no future grant; and `AuthorityGrant` 0.2.0 makes a
publication grant single-use with an exact T1 reservation consumed only at the
dispatch claim. These schemas prove shape, not candidate-digest recomputation,
human identity or assignment validity, gate evidence truth, seal determinism,
current revocation/expiry, or atomic reservation ordering.

### PublicationCandidate

An immutable proposed disclosure:

```text
candidate ID/version/digest
mission and exact source ledger position
eligible claim-version references
evidence package and rendered byte artifacts
visibility, audience, embargo, destinations, and channel classes
proposed redactions and omitted/private dependency manifest
evidence, rights, privacy, safety, security, contributor, wording inputs
canonical release-payload digest
correction endpoint and withdrawal capabilities
compiler rule/code/environment identity
```

A candidate can be rejected, superseded, or expire. It carries no grant and gives no authority.

### ReleaseRequest

A request names the candidate digest, requester, purpose, intended timing, destinations, and urgency. It opens the publication aggregate but has no decision fields and requires no publication grant.

### PublicationDecision

A human decision binds:

```text
candidate ID/version/digest
authorized | denied
per-gate evidence/rights/privacy/safety/security/contributor/wording verdicts
allowed visibility, audience, channels, region, embargo, and expiry
required redactions and exact constraints
reason codes, conflicts, quorum, decision signature/evidence
decision time and human publication authority assignment
```

The decision event resolves that active human assignment directly. It neither
issues, reserves, references, nor consumes the later publication dispatch
grant. Odeya does not require a separate operational grant for this human
decision in the Gate A candidate; if policy later introduces one, it must use a
different role, identity, domain-commit consumption point, and causal record
from the manifest-bound dispatch grant.

Any changed candidate byte, claim version, audience, channel, destination, redaction, wording, or decision input requires a new candidate and decision. “Authorized with silent edits” is forbidden.

### PublicationManifest

The manifest is the immutable final release package at one ledger position. It contains:

- exact candidate digest and human publication-decision reference;
- claim versions and evidence package;
- exact rendered artifacts and canonical payload digest;
- visibility, audience, destinations, adapter versions, and idempotency keys;
- exact redactions and all decision evidence;
- deterministic seal rule and human sealing identity;
- expiry/embargo constraints and correction endpoint through referenced payload metadata.

Its digest is computed after sealing. The manifest has no mutable release state and no embedded grant.
The `publication.sealed` fact names the exact prior
`publication_decision_event_ref`; the deliberately narrower name cannot be
misread as a reference to later dispatch authorization.

### PublicationGrant

The ordinary `AuthorityGrant` publication profile requires:

- human issuer under an active publication assignment;
- exact final manifest digest, exact external-effect identity, mission,
  candidate/decision scope, destination/action class, and maximum risk;
- compatible data/safety/resource/execution prerequisite grants;
- `single_use`, maximum one dispatch intent, short expiry, no delegation;
- explicit forbidden destinations/actions and cancellation/reconciliation policy;
- policy inputs and approval evidence retained.

The grant authorizes attempting the exact effect. It does not assert that release occurred.

### ReleaseEffect

One effect exists per exact manifest/channel/destination combination unless the channel contract proves an atomic multi-target effect. It binds:

```text
effect ID
manifest digest + payload digest
candidate and publication decision refs
channel, destination, account/resource, and adapter version
publication + execution + resource grant refs and use reservations
provider idempotency key and duplicate-charge behavior
visibility/read-back oracle and reconciliation capability
withdrawal/correction capability
```

## Publication state axes

```text
decision:
  not_requested | requested | authorized | denied | expired | superseded

manifest:
  absent | candidate | sealed | superseded

effect:
  not_intended | authorized | started | completion_unknown |
  confirmed_applied | confirmed_not_applied

visibility_observation:
  not_observed | exact_visible | visible_mismatch | not_visible |
  access_restricted | indeterminate

correction:
  current | correction_required | corrected | withdrawal_required | withdrawn
```

`released` is a derived presentation requiring `effect=confirmed_applied` and `visibility_observation=exact_visible` for the exact manifest/destination under the registered oracle. It is not stored from a 2xx response.

## Command sequence

| Command | Required predicate | Authority | Result |
|---|---|---|---|
| `publication.compile_candidate` | Claim versions eligible; projection complete; no hidden dependency; every proposed byte retained | Scoped preparation service; no publication authority | Candidate artifact/event |
| `release.request` | Candidate exists and requester/purpose/targets are valid | Authenticated request capability | Request event only |
| `release.decide` | Every decision gate and conflict/quorum rule settles on exact candidate | Human publication authority; dual control by policy | Authorized or denied decision event |
| `publication.seal` | Authorized decision active; candidate and decision constraints match; deterministic seal passes | Human publication authority invokes/accepts pure seal rule | Final manifest event/digest |
| `authority.issue_grant` with role `publication` | Final manifest digest exists; prerequisites active; policy permits exact effect | Human publication authority | Single-use dispatch-bound grant event |
| `external_effect.authorize` | Manifest/grant/rights/safety/resource/execution still active; channel profile adequate | Required grant quorum | Effect intent + exact grant-use/resource reservation + outbox commit |
| `external_effect.start` and `publication.start_release` | Intent and reservation atomically claimed and authority revalidated before expiry/revocation; no unresolved prior dispatch | Kernel dispatch claim for lease-bound release adapter | Grant use consumed + in-flight facts committed before external call; no release settlement yet |
| `external_effect.report_completion` | Receipt/timeout/read-back tied to exact effect/manifest | Adapter reports evidence only | Applied/not-applied/unknown observation |
| `external_effect.start_reconciliation` / `external_effect.complete_reconciliation` | Effect unknown or visibility insufficient; independent read-back retained | Separate outcome/reconciliation grant | Final settlement polarity or continued unknown |
| `publication.record_release_settlement` | Effect is confirmed applied and exact channel observation satisfies the registered visibility oracle, or confirmed not applied | Pure publication consequence over retained effect/observation facts | `released` or returned-to-sealed/failed projection without erasing attempts |
| `publication.correct` | Claim/evidence/rights/safety/wording dependency changed | Relevant scientific/rights authorities plus human publication authority | Replacement candidate/manifest/effect; correction linkage |
| `publication.withdraw` | Withdrawal required/authorized and channel supports effect | Human publication authority + execution grant | Withdrawal effect; external outcome independently settled |

Grant, policy, rights, decision, and manifest predicates are re-evaluated at the intent commit. A decision that was valid at sealing cannot bypass a later revocation, correction, embargo, or rights change.

## Sealing and byte identity

- Candidate, rendered artifacts, evidence package, decision, manifest, and channel payload each have distinct digests.
- The accepted seal rule is deterministic and versioned. It may assemble references and metadata but cannot rewrite approved prose or scientific values.
- Serialization, timestamp, ordering, Unicode, number, and media rules follow the Odeya canonicalization profile.
- If a channel transforms bytes, the manifest declares the permitted transformation and the read-back oracle compares the accepted semantic/byte identity profile. Undeclared transformation is a mismatch.
- A shortened URL, mutable web page, repository branch, latest-object key, or client-rendered DOM alone is not a stable publication identity.
- Public metadata never reveals private artifact identifiers, mission existence, people, embargoes, or hypotheses beyond the disclosure manifest.

## Rights and privacy recheck

Release evaluates rights and privacy for disclosure—not merely for research processing. It verifies:

- license/lawful basis and allowed recipients/purpose/territory/duration;
- contributor attribution, consent, withdrawal, and embargo;
- personal/sensitive/security/export data and aggregation/reidentification risk;
- model/provider terms affecting generated or transformed material;
- third-party figures, datasets, code, quotations, and trademarks;
- private evidence retained but intentionally omitted;
- correction/withdrawal capability appropriate to the risk.

An evidence package may be complete for private verification and still be ineligible for public disclosure.

## External settlement

The release adapter runs outside the canonical transaction. It cannot set publication state directly.

1. **T1 intent:** commit exact effect identity, consume any intent-bound prerequisites, reserve the dispatch-bound single-use grant and resources, and insert outbox.
2. **Dispatch claim:** revalidate current rights/authority/grant/expiry/correction state and atomically consume the exact reservation with the `external_effect.started`/publication in-flight facts.
3. **Dispatch:** only after the claim commits, call the channel with the stable idempotency key.
4. **T2 observation:** retain response, charge, returned identity, and timeout/error.
5. **T3 reconciliation:** independently read the intended destination and compare exact manifest/payload visibility.

A timeout becomes `completion_unknown`. A provider response means only what the accepted channel evidence rule says. Automatic retry after a possibly crossed boundary is forbidden without proven idempotency and reconciliation. A provider may deduplicate writes while duplicating charges, so cost settlement stays separate.

## Correction, retraction, and withdrawal

A scientific correction does not mutate a publication. It:

1. creates a new adjudication/claim version and dependency invalidation;
2. marks affected manifests `correction_required` or `withdrawal_required` by event;
3. blocks new release of the old manifest;
4. compiles and authorizes an exact replacement/correction notice;
5. dispatches through the same external-effect protocol;
6. independently verifies that old public locations visibly link the correction or are withdrawn where possible.

If a channel cannot correct or withdraw, this limitation is part of the pre-release decision and may make the channel ineligible for consequential claims. The old bytes remain historically addressable when lawful, with a correction/retraction banner at least as visible as the original.

## Crash and adversarial cases

| Boundary | Safe retained state | Forbidden inference |
|---|---|---|
| Candidate compilation crashes | No candidate event; temporary artifact may be quarantined | Candidate exists or was approved |
| Decision commits, reply lost | Immutable decision retrievable by same command ID | Human must decide again |
| Manifest sealing crashes before commit | Candidate/decision remain; materialized bytes may be inert orphan | Manifest sealed |
| Manifest commits, grant issuance fails | Sealed manifest with no usable grant | Authorized for dispatch |
| Grant commits, effect intent fails | Active unused grant; retry same intent command if still valid | Release started |
| Intent/reservation commits, before dispatch claim | Authorized intent, active exact reservation, pending outbox; no in-flight fact | Grant consumed, dispatch started, or channel changed |
| Dispatch claim/use commits, dispatcher dies before known call outcome | In-flight fact and consumed single-use grant; crossing is uncertain, so reconcile/query with no blind retry | Process death proves the channel was or was not changed |
| Channel applies, adapter dies | Completion unknown | Not released or safe to resend |
| 2xx returned with wrong/missing bytes | Response evidence plus mismatch | Released |
| Correction lands during dispatch | In-flight fact retained; revoke/cancel if possible; reconcile then correct/withdraw | Correction erased the call |
| Withdrawal call times out | Withdrawal completion unknown | Content removed |

Known-bad fixtures must include candidate byte mutation after authorization, wrong claim version, expired/changed rights, service pretending to be human decision maker, grant for a different manifest/destination, duplicate dispatch, forged receipt, redirect to wrong bytes, stale cached page, partial multi-channel success, and channel refusing correction.

## Acceptance criteria

Gate A publication architecture cannot pass until:

- candidate, decision, manifest, grant, effect, observation, correction, and withdrawal schemas/events are complete and non-circular;
- reducer traces cover every state edge and crash row;
- canonical payload/seal rules have cross-runtime vectors;
- every channel class declares idempotency, read-back, cost, correction, and withdrawal evidence or is refused;
- authority/rights/security reviewers close critical/high findings;
- public/private projection fixtures prove no hidden data or claim widening;
- the first proof fixture demonstrates supported, null, invalid/blocked, correction, and ambiguous-release handling offline; and
- Daniel accepts the exact protocol candidate.

Passing these architecture criteria still does not authorize a real release or channel integration.
