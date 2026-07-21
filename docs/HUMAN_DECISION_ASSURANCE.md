# Human Decision Assurance

Status: unissued Gate A architecture candidate, 2026-07-21. The retained T0
byte-bound/recomputation tranche is candidate evidence, and ADR 0095 adoption
is still incomplete pending context-isolated technical review over the exact
candidate bytes. The contracts, fixtures, and checks described here are
architecture evidence only. They do not establish a real human ceremony,
satisfy a human-only authority slot, complete consumer migration, accept Gate
A, or authorize runtime, cloud, or deployment work.

## Why this contract exists

A valid signature proves only that a signature verified under a declared key
and algorithm. A principal labelled `human` does not prove that a natural
person controlled the key, initiated this act, reviewed these exact bytes, or
made the stated Odeya decision. Authentication intent is also narrower than
substantive decision intent.

PRQ-013 therefore separates two subjects that must not be conflated:

1. the source decision, whose own schema and policy retain authority over its
   meaning, authorship fields, decision time, expiry, supersession, and effect;
2. one later ratification act in which one declared principal is asked to
   confirm the exact raw decision and candidate bytes that were reviewed and
   displayed.

One `HumanDecisionAssuranceCore`, one `HumanDecisionAssuranceEvidence`, and one
`HumanDecisionAssuranceSeal` represent exactly one such later act. They do not
aggregate principals. A future, separately identified `AssuredDecision`
wrapper must combine individual seals and evaluate currentness, expiry,
withdrawal, revocation, contradiction, authority, separation, and aggregate
quorum at a controlled evaluation time.

Missing or unknown required evidence is `indeterminate`, never false and never
approval. A positive contradiction is `invalid`. Timeouts and silence do not
become decisions.

## Nonrecursive construction

The generated challenge and evidence remain outside the Core whose exact bytes
they bind. No artifact digests itself.

```mermaid
flowchart LR
    D["Exact source decision bytes<br/>source schema retains meaning"]
    M["Exact candidate bytes"]
    C["Assurance Core<br/>one later-ratification request<br/>no challenge output · no self-digest"]
    H["Two-phase challenge + receipt<br/>acyclic exact framing"]
    E["Evidence 0.2<br/>one participant observation<br/>closed 14-role inventory"]
    B["Backing-byte receipt<br/>14 retained preimages rederived"]
    R["Three recomputation results<br/>Python · Node · Java"]
    X["Comparison receipt<br/>exact six-field agreement"]
    S["Seal 0.2<br/>candidate eligibility only"]
    W["Future AssuredDecision wrapper<br/>identity not assigned"]
    P["Controlled policy evaluation<br/>currentness · authority · quorum"]

    D --> C
    M --> C
    C -->|raw SHA-256 + bytes| H
    H --> E
    C -->|raw SHA-256 + bytes| E
    E --> B
    E --> R
    B --> R
    R --> X
    C -->|unchanged binding| S
    E -->|one exact raw binding| S
    B --> S
    X --> S
    S --> W --> P

    classDef current fill:#E0F2FE,stroke:#0369A1,color:#0C4A6E
    classDef later fill:#F1F5F9,stroke:#64748B,color:#334155,stroke-dasharray: 5 5
    class D,M,C,H,E,B,R,X,S current
    class W,P later
```

The retained predecessor and successor candidates include:

- `HumanDecisionAssuranceCore` 0.1.0;
- immutable, unissued `HumanDecisionAssuranceEvidence` 0.1.0 and
  `HumanDecisionAssuranceSeal` 0.1.0 predecessors;
- five separately identified, unissued successor schemas: Evidence 0.2,
  BackingByteVerificationReceipt 0.1,
  EligibilityRecomputationResult 0.1,
  EligibilityComparisonReceipt 0.1, and Seal 0.2;
- the exact adopted `odeya-human-decision-challenge-frame-v2-candidate`
  two-phase binary framing profile and its deterministic recomputation vector,
  while retaining the v1 profile and vector as superseded evidence;
- exact, unissued singleton-eligibility ruleset 0.2 and a closed resolver
  profile;
- 14 content-addressed synthetic backing preimages, seven schema-valid
  successor fixtures, 44 expectation-free evaluator vectors, and 48
  downstream chain known-bads;
- 132 exact passing recomputations: 44 each through source-separated,
  non-sharing Python 3.14.2, Node.js 24.18.0, and Temurin Java 21.0.9
  implementations;
- a dedicated, schema-valid synthetic source decision whose exact candidate
  relation can be checked without reusing a historical operator decision; and
- a machine consumer census over the frozen pre-candidate schema corpus,
  command vocabulary, event vocabulary, decision families, and known missing
  contract nodes.

Raw SHA-256 is a T0 byte-binding mechanism, not canonical object identity. All
three 0.1 schema resources and all five successors remain unissued candidates.
The 0.1 identities and bytes remain immutable; no successor redirects them.
No admitted assurance-record or `AssuredDecision` wrapper identity exists, and
every migrated consumer requires a new identity behind the eventually accepted
canonical profile.

The framing and successor graph is deliberately acyclic. The static framing
profile contains no Core, vector, Evidence, receipt, result, Seal, or self
digest. The Core binds the profile's exact raw SHA-256 and byte count; the
separate vector evidence binds both profile and Core bytes; Evidence 0.2 binds
the Core and closed backing inventory; the backing receipt precedes three
recomputation results; their comparison precedes Seal 0.2; and the Seal binds
both receipts without either receipt naming or predicting the Seal. Moving a
downstream digest upstream would create a cycle and is forbidden.

The Core is created before the ceremony. Its material bindings are therefore
requirements for what a later ceremony must display and review, not
observations that display, review, or confirmation already occurred. Only
Evidence may record those later observations.

## Source decision and later-ratification boundary

The retained positive chain uses
`tests/architecture-schema/fixtures/human-decision-assurance-decision-subject.valid.json`,
a dedicated
synthetic `operator-architecture-decision` record. It is a non-acceptance
decision over the retained synthetic candidate. The checker requires the
Core decision-subject artifact ID to equal the source record's `decision_id`.
It also requires the source decision's candidate manifest ID, version, and raw
digest to equal the Core's candidate subject and explicit subject
relationship.

The source decision's schema remains the semantic authority. The Core repeats
only relationship metadata that the checker requires to equal the exact source
record. It does not transfer or reinterpret policy-bearing decision value,
effect, implementation lock, expiry, supersession, or other semantic
authority. It binds the exact source record and its `/decision` pointer.

The fixture deliberately declares a source operator distinct from the later
confirming principal. The later confirmation therefore does not prove who
authored the source decision or that the source `decided_at` is true. It binds
only the later principal's ratification of the exact displayed and reviewed
decision and candidate bytes. `confirmed_at` is an assurance-ceremony time,
not a rewritten source-decision time.

The dedicated source decision, candidate, Core, Evidence, and Seal are
relationally coherent synthetic controls. They are not Daniel's decision, a
real display, a real review, or authority.

## Challenge and confirmation boundary

The challenge framing profile commits, in exact order, the Core schema
resource ID and exact Core-record raw digest, decision schema resource ID and
exact decision-record raw digest, candidate schema resource ID and exact
candidate-record raw digest, session, issue and expiry times, relying-party
ID, expected origin, and a 32-byte nonce. Each entry is length-prefixed; text
is exact ASCII, digests are decoded to 32 raw octets, and integers are unsigned
big-endian.

The resulting WebAuthn challenge is:

```text
nonce32 || SHA-256(exact_binary_frame)
```

It contains 64 raw bytes and is encoded as 86 base64url characters without
padding. `challenge_id` is the raw SHA-256 of those exact 64 challenge octets,
so another label cannot alias the same challenge.

The candidate pins all of the following:

- relying-party ID `odeya.danielwahnich.dev`;
- expected origin `https://odeya.danielwahnich.dev`;
- `navigator.credentials.get`;
- COSE algorithm `-7`, `ES256`, with substitution forbidden;
- at least 256 fresh random bits and a maximum 300-second lifetime;
- a half-open validity interval, issued-at inclusive and expires-at exclusive;
  and
- relying-party or independent-verifier generation with single, atomic
  consumption.

The checked chronology is:

```text
source-decision.decided_at = Core.source_declared_decided_at
  <= Core.created_at
  <= challenge.issued_at
  <= confirmation.confirmed_at
  <= challenge.assertion_received_at
  <= challenge.consumed_at
  < challenge.expires_at
```

An accepted assertion and the transition from prior-consumption count zero to
result-consumption count one must be one verifier-controlled atomic action.
An assertion observed exactly at expiry is late. Retry exhaustion, a timeout,
or a second consumer does not imply success.

The protected application confirmation is separate from the authenticator
gesture. Its `gesture_id` is the raw SHA-256 of the referenced exact sanitized
material-presentation and decision-confirmation receipt. That receipt asserts
the exact decision and candidate bindings and presentation identity; it is not
pixel evidence or proof of comprehension. The confirmation binds the assurance ID,
exact Core raw digest, session ID, challenge-request ID, content-derived
challenge ID, relying-party ID, expected origin, exact decision digest, and
exact candidate digest. Because it binds the whole Core, changing any Core
relationship or policy-request field requires a fresh confirmation; a checker
cannot silently rewrite the human act while rebinding test bytes.

This binding is no longer one-way. Under the
[ADR 0093](decisions/0093-co-bind-the-confirmation-gesture-through-a-two-phase-challenge.md)
two-phase construction, now adopted, the Core pins the v2 framing profile and
each participant observation carries a presentation challenge and a
confirmation receipt. The receipt commits backward to the presentation
challenge; the authentication challenge commits forward to the receipt digest
through three appended frame fields. The signature therefore covers the digest
of what was displayed and confirmed, and no artifact commits to a digest of
anything that commits to it.

The Gate A prerequisite
`confirmation_gesture_and_authenticator_actor_cryptographically_co_bound` is
therefore `true` — strictly as a property of the frame construction, re-derived
independently by the `challenge-frame` suite and re-checked against the Core
and Evidence bytes on every prerequisite run. It is not a measurement. No
ceremony occurred, so `material_presentation_receipt_verified_in_real_ceremony`
remains `false`, and the structured evidence, Seal, and candidate envelope
still retain
`confirmation_gesture_and_authenticator_actor_cryptographically_co_bound: false`
because those records state what an *observed* ceremony established, and this
fixture's ceremony is synthetic.

A presentation surface inside the trust boundary that fabricates its own
receipt is detected only when its receipt disagrees, never prevented. That
residue is the retained cost of declining the transaction-confirmation trusted
path at Gate A. The retained successor now supplies exact backing-byte
dereference and three source-separated, non-sharing ruleset implementations.
Profile and schema issuance remain blocked pending ADR 0095's context-isolated
technical review of the exact candidate bytes, the later T1/T2 and wrapper
dependencies, end-to-end consumer refusal, accountable review, and operator
acceptance.

The retained vector proves only deterministic framing and recomputation. A
metamorphic second-nonce expected-pass control proves that the checker is not
hard-coded to the retained nonce. Neither synthetic control proves fresh
randomness, atomic storage, or a real ceremony.

## Evidence semantics

Each required observation is explicit:

```mermaid
stateDiagram-v2
    [*] --> Supported: supported under applicable evidence profile
    [*] --> Unknown: missing / unavailable / not verified
    [*] --> NotApplicable: required support marked not applicable
    [*] --> Contradicted: positive conflict or failed check
    Supported --> IndividuallyEligible: all singleton rules supported
    Unknown --> Indeterminate
    NotApplicable --> Indeterminate
    Contradicted --> Invalid
    IndividuallyEligible --> WrapperAssembly: future only
    Indeterminate --> Blocked
    Invalid --> Blocked
    WrapperAssembly --> ControlledEvaluation: currentness + authority + quorum
    ControlledEvaluation --> NoAuthority: wrapper/profile unissued
```

The synthetic positive control exercises the `Supported` branch without
establishing real-world support.

The exact unissued ruleset applies a total precedence law. Any contradicted
required observation or failed required categorical condition is `invalid`.
Otherwise, any missing, `unknown`, or `not_applicable` required observation is
`indeterminate`; this candidate authorizes no `not_applicable` exception.
Only all-supported observations plus all-satisfied categorical conditions are
`eligible`.

`eligible` is not `approved`. It means only that this one synthetic act may
enter future `AssuredDecision` assembly. It does not state that the source
decision is current, unexpired, unwithdrawn, unrevoked, authoritative, or part
of a satisfied aggregate quorum.

The Core, Evidence, and Seal structurally require exactly one declared
principal act, one participant observation, one Evidence binding, and one
participant determination. Existing fields named `quorum_rule` and
`quorum_evaluation` are pinned to this singleton eligibility scope; they do
not perform aggregate quorum. More than one principal or Evidence record must
be represented by multiple individual chains and a future wrapper.

The Evidence schema deliberately admits `unknown`, `contradicted`, replayed,
and failed observations: those are facts that must remain representable. The
Seal schema is likewise a structural record, not a trusted evaluator. The
isolated semantic checker must dereference the exact bound candidate records,
recompute the singleton disposition, and reject an `eligible` seal whenever a
required observation is unknown, `not_applicable`, or contradicted. A
contradiction wins when it coexists with unknown support. Schema validity alone
is never eligibility.

The evidence set is role-addressed as well as ID-addressed. The checker
requires every expected role exactly once and resolves each
claim-bearing reference against that role. A client-data artifact therefore
cannot stand in for challenge generation, signature, custody, controlled time,
verifier, decision confirmation, or delegation/effective-control evidence.

The five exact unmodified inputs—client data JSON, authenticator data,
WebAuthn signature, credential public key, and displayed decision bytes—retain
their exact byte-fidelity classes. The exact binary confirmation-receipt frame
uses its own unmodified-binary-frame class. The other eight entries are
explicitly `sanitized_derived_observation_record` values. Sanitation metadata
records a retention/content-policy review only; it never authorizes
transformation of an exact input.

The successor fixture retains all fourteen synthetic preimages as actual
content-addressed repository bytes. The backing verifier independently
dereferences them and rederives each raw SHA-256, byte count, descriptor
relation, receipt row, and the confirmation-frame relation; a path or declared
digest is never trusted as its own proof. Missing is not represented as zero,
and readable mismatch remains `invalid` rather than being softened to
`unknown`.

That exact byte verification establishes only the synthetic preimages and
relations retained here. Assignment, natural-person identity, custody,
effective control, and verifier independence remain synthetic assertions under
an unissued profile. The validator can reject internal inconsistency and role
substitution, but it cannot upgrade those assertions into real-world facts.

### Non-sharing eligibility recomputation

Ruleset 0.2 publicly inventories every required domain and applies one total,
monotonic precedence law. Three source-separated implementations consume the
same allowed normative schemas, ruleset, resolver profile, and input bytes,
but do not share evaluator source, generated evaluator code, parsing or
normalization helpers, intermediate state, expected answers, or one another's
outputs. Python 3.14.2, Node.js 24.18.0, and Temurin Java 21.0.9 each pass all
44 expectation-free vectors: 132 exact recomputations in total.

The comparison receipt checks the complete projection, not only the final
disposition. It requires exact agreement on `participant_id`,
`domain_results`, `categorical_results`, `categorical_failures`,
`final_disposition`, and `reason_codes`. The 48 downstream chain known-bads
separately attack backing truth, deterministic negative reasons, result and
source identities, projection completeness, acyclicity, receipt/Seal
bindings, runtime and dependency pins, non-sharing, and preservation of the
0.1 identities.

The source separation and non-sharing controls are retained and machine
checked. Organizational independence is not proven: the implementations share
their normative contract and the retained work does not establish
organizationally independent authorship or review. Agreement can therefore
detect bounded implementation defects without proving that the common ruleset
is correct.

All fixed timestamps in the successor fixtures, results, receipts, and Seal
are deterministic fixture times only. They do not establish freshness,
trusted time, chronology in a real ceremony, or an observation about a person.

## Standards comparison

The candidate pins:

- [NIST SP 800-63B-4](https://csrc.nist.gov/pubs/sp/800/63/b/4/final),
  final July 2025, for authentication and authenticator assurance comparison;
  and
- [Web Authentication Level 3, Candidate Recommendation Snapshot,
  26 May 2026](https://www.w3.org/TR/2026/CR-webauthn-3-20260526/), for the
  relying-party ceremony comparison.

WebAuthn Level 3 is a Candidate Recommendation Snapshot, not a W3C
Recommendation. Neither source establishes Odeya decision meaning,
comprehension, cognition, natural-person identity by WebAuthn alone, exclusive
custody from a signature, delegation validity, effective-principal separation,
current authority, or aggregate quorum. Exact retained standard bytes,
conformance vectors, and an accepted Odeya profile remain open.

## Future `AssuredDecision` boundary

The individual Seal intentionally does not answer the consuming decision
question. A later wrapper must, at one controlled evaluation time:

1. resolve the exact source decision and all selected individual seals;
2. apply the source decision schema and consumer policy without copying or
   relabelling their semantics;
3. verify that each seal, its profile, and its supporting evidence remain
   current and applicable;
4. evaluate source expiry, supersession, withdrawal, revocation,
   contradiction, and correction state;
5. establish assignment, authority, authenticator, effective-control, and
   verifier-separation facts from accepted evidence rather than fixture
   assertions;
6. compute aggregate quorum over distinct authorized principals and effective
   control groups; and
7. atomically bind the evaluated frontier and resulting consuming transition.

That wrapper identity, schema, controlled-time policy, verifier substrate, and
consumer integration are not present in this tranche.

They also cannot precede their dependencies. T0 freezes only the
individual-assurance foundation candidate and exact census. T1 must construct
the `AuthorityAssignment` vertical contract, and T2 must construct the required
command, event, state, reducer, currentness, and quorum subjects before final
wrapper construction or consumer migration can claim dependency closure.

## Consumer migration boundary

The census found that the nine schemas originally named by ADR 0089 were only
a lower bound. The frozen source tree contains 19 direct or
policy-conditional decision-schema rows and nine pending
operator-acceptance-consumer rows, plus transitive command, event, registry,
projection, and constitutional consumers.

None is migrated in this tranche. Existing consumer schema bytes remain
unchanged. A later migration must:

1. assign new, separately identified, unissued consumer and `AssuredDecision`
   candidates without mutating retained IDs; only the exact Gate A operator
   decision can govern later issuance and admission;
2. require the exact wrapper at every applicable transition;
3. dereference the exact decision, candidate, individual seals, and accepted
   evidence;
4. evaluate currentness and authority at the consuming transition and fail
   closed for absent, stale, expired, withdrawn, revoked, contradicted,
   indeterminate, or invalid assurance;
5. reissue every command, event, persistence, and downstream contract that can
   admit or carry the decision; and
6. prove `PRQ-013-KB-001` is `invalid` at the consuming transition because its
   claimed human initiation is contradicted, not merely refused by the
   standalone assurance checker.

The current command and event catalogs still contain known missing typed
contract nodes. Those holes remain explicit census blockers and cannot be
interpreted as migration completion.

The checker pins the census inventories and reconciles their coverage counts.
Those classifications remain explicit ADR 0092 census judgments; this bounded
checker verifies their retention and arithmetic but does not independently
derive their semantic classification from source.

It additionally compares every baseline schema with the frozen Git checkpoint,
binds both the exact predecessor and deliberately amended
`docs/AUTHORITY_MATRIX.md` bytes, requires the current schema paths to equal the
exact 112-baseline-plus-eight-candidate disjoint union of 120 schemas, and pins the
judgment-bearing classification, command/event partition, family, validator,
construction, completeness, migration, and nonclaim sections. The amended
matrix names only a future admitted `AssuredDecision` wrapper at an `H` slot and
records the exact contradiction-first `PRQ-013-KB-001` disposition. Those checks
prevent a coordinated census/hash edit from silently converting a candidate or
missing contract into admitted authority.

## Gate staging

Gate A evaluates the architecture: exact ceremony protocol, evidence schemas
and backing-byte rules, profile candidates, synthetic conformance vectors,
source-separated, non-sharing architecture-time verifier implementations,
wrapper/consumer contracts after their T1/T2 dependencies, accountable review,
and the operator's exact-byte decision. It does not require or authorize a
live ceremony, and the operator's Gate A decision is not evidence that the
future engine ceremony works.

The current T0 byte-bound/recomputation tranche is retained candidate evidence,
not completed ADR adoption or PRQ-013 closure. ADR 0095 still requires a
context-isolated technical-review determination over the exact candidate bytes.
That determination is deliberately non-accountable and cannot substitute for
the later accountable security/authority review or the operator's Gate A
decision.

After Gate A, one real protected ceremony may be separately authorized as a
bounded, disposable Gate B probe under the accepted profile. Agents receive no
credential or approval authority. Gate C remains responsible for any
implementation increment and its runtime identity, policy, isolation, replay,
and failure evidence.

## Retained nonclaims

- Synthetic fixtures are not human decisions, authentication evidence, or
  evidence that a natural person saw any bytes.
- The dedicated source fixture is relationally coherent but does not prove its
  declared operator, authorship, `decided_at`, or decision truth.
- Fourteen content-addressed backing preimages are dereferenced and rederived,
  but they are synthetic conformance bytes rather than real-world evidence.
- The application confirmation receipt and authenticator actor are co-bound
  only as a synthetic construction property of the adopted two-phase frame.
  No real ceremony established that the same natural person performed both
  acts, and the observed-evidence proof boundaries therefore remain false.
- The exact singleton ruleset and every successor resource remain unissued.
  Three source-separated, non-sharing implementations agree on the retained
  vectors, but organizational independence is not proven.
- Assignment, custody, effective control, verifier independence, and
  natural-person identity are asserted, not mechanically established.
- The candidate performs no aggregate quorum or consumer-currentness
  evaluation.
- Context-isolated model review is correlated review, not accountable or
  organizationally independent verification.
- A passing checker proves bounded agreement among retained candidate bytes;
  it does not prove the standards are implemented correctly.
- No current consumer accepts the assurance candidate.
- PRQ-013, T1, Gate A, runtime, deployment, scientific-results publication,
  spending, data access, and external effects remain blocked.
- `publication_authorized` in the candidate-evidence boundary means
  assurance-mediated scientific or product publication; it does not describe
  the separately governed architecture-repository release path.

The governing decisions are
[ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md),
[ADR 0092](decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md),
[ADR 0093](decisions/0093-co-bind-the-confirmation-gesture-through-a-two-phase-challenge.md),
and
[ADR 0095](decisions/0095-reissue-human-decision-assurance-as-a-byte-bound-independently-recomputed-chain.md).
