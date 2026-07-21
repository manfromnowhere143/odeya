# HumanDecisionAssurance candidate semantic checks

Status: architecture-only evidence for an unissued, synthetic
HumanDecisionAssurance candidate. Passing this suite does not prove a human
decision, original authorship, independent review, consumer migration, an H
slot, aggregate quorum, currentness, authority, Gate A acceptance, runtime
safety, deployment authority, assurance-mediated scientific-results
publication authority, or any external effect. The architecture-repository
release path is governed separately.

## Construction under test

The suite checks the acyclic individual-assurance construction selected by
ADR 0092:

```text
exact source decision and candidate bytes
  -> one HumanDecisionAssuranceCore
  -> exact raw Core-byte binding
  -> one HumanDecisionAssuranceEvidence
  -> exact raw Evidence-byte binding
  -> one HumanDecisionAssuranceSeal
  -> future AssuredDecision wrapper contract (explicitly missing)
  -> future controlled currentness/authority/quorum evaluation
```

One Core, Evidence, and Seal chain represents one later ratification act by
one declared principal. It is not a multi-principal record. The Core contains
the exact source-decision and candidate bindings, exact requirements for what
must later be reviewed and displayed, their ID/version/raw-digest relationship,
the requested later-ratification relation, ceremony request, one principal,
and one verifier relation. It contains no self-digest, Evidence, Seal,
attestation, or aggregate
quorum result, and it does not claim that display, review, or confirmation
already occurred.

The source decision's schema and consuming policy remain authoritative for its
meaning. The Core repeats relationship metadata that must equal the exact
source record, but neither transfers nor reinterprets policy-bearing decision
value, effect, implementation lock, expiry, supersession, withdrawal, or
revocation authority.

The Evidence owns generated challenge output and exactly one participant
observation. It separately records the content-addressed protected application
confirmation, WebAuthn ceremony evidence, identity and authenticator binding,
custody, agent/tool exclusion, delegation, effective control, controlled time,
replay state, verifier relation, and sanitation. Missing or unknown required
evidence becomes `indeterminate`; contradiction, replay, agent initiation, or
collapsed verification becomes `invalid`.

The Seal binds exactly one Evidence record and one exact unissued
singleton-eligibility ruleset, then records a result deterministically
cross-checked by this candidate checker. There is no retained independent
implementation. The disposition law has two layers. Schema, exact-raw-byte,
and cross-record identity checks are verifier-integrity preconditions; their
failure makes the chain externally invalid and refused before the embedded
Seal disposition is interpreted, and rewriting that disposition cannot cure
the chain. Within an integrity-valid chain, contradiction or an
evidence-internal required categorical failure is `invalid` before any
missing, `unknown`, or `not_applicable` observation becomes `indeterminate`;
only all-supported and all-satisfied input is `eligible`. `eligible` means only that the
act may enter future `AssuredDecision` assembly. It never means approval, never
satisfies an H slot in this candidate, and never states that the source
decision is current, unexpired, unwithdrawn, unrevoked, authoritative, or part
of a satisfied aggregate quorum.

Fields named `quorum_rule` and `quorum_evaluation` are constrained to a
one-principal eligibility scope and explicitly marked as not aggregate quorum.
Multiple individual seals, source currentness, authority, expiry, withdrawal,
revocation, contradiction, and aggregate quorum are deferred to a future
wrapper at a controlled evaluation time.

No wrapper schema, identity, admission record, currentness rule, authority
rule, or aggregate-quorum rule exists in this T0 foundation. The checker
therefore refuses every present claim to supply an `AssuredDecision` wrapper;
it does not retain a synthetic positive wrapper control. Before any H slot can
be satisfied, T1/T2 must provide an admitted, current, nonexpired, nonreplayed
wrapper with authority and distinct-effective-principal quorum evaluated
against the exact displayed decision and candidate bytes at the consuming
transition.

The ruleset names every currently implemented categorical predicate. One pure
derivation computes the participant domains, categorical failures, and final
disposition; the Seal recomputation helper and checker both consume that same
result. The suite keeps admission-gate controls, where an ineligible act is
refused, separate from record-validity controls. A correctly sealed `invalid`
or `indeterminate` record is valid negative evidence and must pass the latter;
a stale `eligible` Seal over the same evidence is refused. This preserves
negative outcomes instead of treating them as malformed artifacts.

## Dedicated source-decision control

`tests/architecture-schema/fixtures/human-decision-assurance-decision-subject.valid.json`
is a dedicated, schema-valid
`operator-architecture-decision` control. It names the retained candidate's
exact manifest ID, version, and raw digest. The Core repeats that relationship,
binds a decision-subject artifact ID equal to the source `decision_id`, and
the checker rejects any disagreement among the source decision, Core, and
candidate fixture.

The source decision declares `fixture.operator-not-daniel`; the later
confirming principal is `human.synthetic.operator.0001`. This deliberate
separation proves that the checked relation is later ratification of exact
artifacts, not original authorship. The chain does not assure the source
operator or source `decided_at`; `confirmed_at` is a later assurance timestamp.

The fixture's decision is non-acceptance and its implementation lock authorizes
no runtime or external effect. It is a relational control, not Daniel's
decision or evidence that any person authored, saw, reviewed, or confirmed the
bytes.

## Exact-byte, challenge, and confirmation checks

The checker uses strict JSON loading with duplicate-name and non-finite-number
rejection. It verifies:

- the dedicated source decision and architecture-candidate fixture bytes, byte
  counts, raw SHA-256 values, schema resources, exact IDs and versions, and the
  source decision's `/decision` pointer;
- exact equality between the source decision's candidate relation and the
  Core's candidate subject;
- required-review and required-display decision equality,
  required-review and required-display candidate equality, and exact
  subject-leaf bindings, without treating Core requirements as ceremony
  observations;
- the exact supplied raw Core → Evidence → Seal chain, without re-rendering
  parsed objects or treating raw hashes as canonical object identities;
- strict equality between each supplied Core, Evidence, and ruleset mapping
  and the object parsed from its supplied raw bytes, preventing a caller from
  verifying one mapping while binding another byte sequence;
- expected-pass controls in which noncanonical-but-semantically-equivalent
  Core or Evidence bytes are accepted only after every downstream raw binding,
  challenge commitment, and protected confirmation relation is rebuilt from
  those exact bytes;
- the definition-only challenge-frame profile's exact raw binding from the
  Core and the external vector evidence's exact profile/Core bindings;
- the u16/u32 big-endian frame encoding, ordered fields, 32-byte nonce,
  maximum 300-second lifetime, SHA-256 commitment, 64-byte
  `nonce || commitment`, and unpadded base64url vector;
- `challenge_id` as the raw SHA-256 of the exact 64 challenge octets;
- the pinned relying-party ID `odeya.danielwahnich.dev`, expected origin
  `https://odeya.danielwahnich.dev`, `navigator.credentials.get`, and
  non-substitutable ES256/COSE `-7` policy;
- the 0.1 candidate's same-origin-only rule: exactly
  `same_origin_supported` plus a `supported` profile validation result in
  `top_origin_match`; `approved_cross_origin_profile_supported` is refused
  because no alternate-origin policy artifact is admitted;
- the half-open chronology
  `source-decision.decided_at = Core.source_declared_decided_at <=
  Core.created_at <= issued_at <= confirmed_at <= assertion_received_at <=
  consumed_at < expires_at`;
- a prior-consumption count of zero and result-consumption count of one in the
  same verifier-controlled atomic consumption action;
- the separate application confirmation gesture as the raw digest of its
  exact sanitized artifact;
- confirmation binding to assurance ID, entire exact Core digest, session,
  challenge request, content-derived challenge ID, relying party, origin,
  decision digest, and candidate digest;
- nonce recovery from the observed challenge rather than from the retained
  vector fixture, plus an independently recomputed second-nonce metamorphic
  expected-pass control; and
- raw-byte mutations, proving semantic JSON equality does not preserve an
  exact byte binding.

Ordinary semantic mutation rebinding updates mechanical downstream bindings
only. It does not rewrite the protected confirmation. The explicit
second-nonce expected-pass control represents a fresh synthetic confirmation, which
prevents Core mutations from passing merely because the harness silently
rewrote what it claims the principal confirmed.

The adopted v2 construction co-binds the two acts without a digest cycle. The
presentation challenge is created first; the confirmation receipt binds that
recomputed phase-one identity; and the authenticator-signed phase-two
challenge commits to the receipt digest. The suite re-derives that chain from
the Core and Evidence bytes and retains the v1 vector as superseded evidence.
This is a synthetic construction property only: no real ceremony establishes
that one natural person performed both acts, so the Evidence, Seal, and
candidate proof boundaries remain false for observed co-binding. Profile
issuance still requires backing-byte verification, independent eligibility
recomputation, end-to-end consumer refusal, accountable review, and the
operator's exact-byte decision.

## Evidence-reference and proof boundary

The ordered evidence set is role-addressed as well as ID-addressed. The checker
requires every expected role exactly once and resolves each
claim-bearing reference against that role. An existing client-data artifact
cannot stand in for challenge generation, signature, custody, controlled time,
verifier observation, decision confirmation, or
delegation/effective-control evidence.

Client data JSON, authenticator data, the WebAuthn signature, and the
credential public key are exact, unmodified cryptographic inputs. The other
eight entries are sanitized derived observation records. A sanitation status
on an exact input means retention/content review, never byte transformation.
The fixture does not dereference backing bytes, so the suite checks declared
fidelity and relations rather than proving real byte fidelity.

The current fixture does not dereference the backing artifact bytes. It checks
their retained IDs, roles, raw digests, byte counts, media types, and reference
relations. Assignment, natural-person identity, custody, effective control,
and verifier independence are synthetic assertions under an unissued profile,
not mechanically established facts. The suite can reject internal
contradictions or role substitution; it cannot prove those real-world
properties.

## Consumer census

The checker does not trust the census's summary booleans. It recomputes the
frozen source corpus from its exact Git commit and tree:

- every baseline schema row and the disjoint three candidate-mechanism rows;
- every row's path, observed `$id`, raw hash, byte length, and discovered
  marker pointer;
- the exact baseline primary-class partition;
- command and event types as source-ordered, disjoint, complete partitions;
- human-decision families, transitive-consumer families, pending
  operator-acceptance consumers, validator paths, and explicit missing HDA
  contract nodes;
- exact reconciliation of census coverage counts and all false completion
  flags against those inventories; and
- false migration, real-ceremony, accountable-review, Gate A, runtime,
  deployment, and production claims.

The census binds the baseline Authority Matrix bytes as historical provenance
and, separately, the amended current Authority Matrix bytes used by this
candidate wave. It does not require the current Matrix to equal the baseline;
it requires both named byte identities and refuses unexplained current drift.
The census is complete only for its named frozen source corpus. It is not
consumer migration and does not authorize mutation of retained schema
identities. Its family classifications are explicit census judgments under
ADR 0092; the checker pins and reconciles them but does not independently
derive their semantic classification.

`architecture/human-decision-assurance-candidate-evidence.json` is the external
evidence envelope for this candidate wave. The checker recomputes its ordered
bindings to ADR 0092, all three schemas and synthetic controls, KB001, the
frame profile and vector, the dedicated source decision, the census, and this
suite's exact eligibility ruleset, checker, cases, and contract. It also
recomputes suite and census
summaries and requires every open and proof boundary to remain false. The
envelope does not bind itself.

## Retained controls

`cases.json` contains expected-pass controls (encoded by the harness as
`kind: safe`) and one-mutation, intent-bound known-bads. The checker derives
and reconciles the current control, adversarial-case, and intent-rule counts
rather than relying on prose counts. Exact observed error sets must equal each
case's declared `expected_errors`; every adversarial case also names the
refusal it is meant to exercise in `intent_errors`.

The corpus covers:

- exact source-decision, candidate, displayed, reviewed, Core, Evidence,
  profile, session, request, relying-party, origin, and challenge equality;
- exact source candidate ID/version/raw-digest coherence;
- challenge framing, content-derived challenge identity, half-open chronology,
  atomic single consumption, replay, and raw-byte drift;
- a separately content-addressed application confirmation bound to the entire
  Core and ceremony context;
- one-principal, one-observation, one-Evidence, and one-determination
  cardinality;
- WebAuthn, identity, custody, agent/tool exclusion, delegation, objections,
  conflicts, effective control, verifier separation, and sanitation
  observations;
- refusal of unbound cross-origin profiles, ruleset raw/object substitution,
  Evidence/Seal class mismatch, assurance-identity mismatch, participant
  determination identity mismatch, root sanitation drift, algorithm
  substitution, non-external Core binding, and embedded Seal attestation;
- valid retained negative records for prior challenge consumption, an unknown
  required observation, an unbound cross-origin attempt, and a combined
  categorical failure plus unknown observation, including invalid-before-
  indeterminate precedence and stale-Seal refusal;
- attempts to turn individual eligibility into source currentness, authority,
  aggregate quorum, or approval;
- consumer bypass, timeout, silence, duplicate JSON names, harness hygiene,
  wrong-existing evidence-role substitution, and missing direct provenance;
  and
- retention of reusable secrets, private/signing keys, PIN or biometric
  material, or unrestricted prompts/model output.

It also refuses a substituted operator-consumer path or pointer and a
substituted missing-node identity or kind; inventory counts alone are not
accepted as census closure. The census checker compares each current baseline
schema to the frozen source bytes, verifies the separately bound current
Authority Matrix, requires the exact baseline-plus-three-candidate schema
union, and freezes
classification, family, validator, construction, migration, nonclaim, and
completeness judgments.

`PRQ-013-KB-001` retains the signature-valid but agent-accessible-key attack.
Because unattended agent invocation is supported and human initiation is
contradicted, its expected disposition is `invalid`; it cannot satisfy an H
slot or count toward future aggregate quorum.

The harness also self-tests its own refusal statements. A wrong exact error
inventory, missing mutation, missing intent, unknown target, unknown case
kind, or non-firing intent fails closed.

Run:

```bash
.venv-architecture/bin/python tests/human-decision-assurance/check.py
```

## Proof boundary

The profile comparison names NIST SP 800-63B-4 (final, July 2025) and the
26 May 2026 Web Authentication Level 3 Candidate Recommendation Snapshot.
Those sources describe authentication mechanisms and assurance properties;
they do not prove Odeya decision meaning, review, comprehension, cognition,
substantive consent, original authorship, source decision time, exclusive
custody, delegation validity, effective-control separation, current authority,
or aggregate quorum.

All fixtures and challenge values are synthetic. Backing evidence artifact
bytes are not dereferenced. Review performed by agents in this development
session is correlated and is not organizationally or accountably independent.
The canonical profile and assurance profile remain unissued. The
`AssuredDecision` wrapper is unidentified and unimplemented. Current consumers
remain unmigrated. This work is T0 architecture evidence only: Gate A remains
architecture acceptance, any real protected ceremony is a separately
authorized Gate B probe, and runtime conformance is a later Gate C exit
condition. PRQ-013 and Gate A remain blocked.
