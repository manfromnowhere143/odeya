# ADR 0092: Bind human decisions through an external assurance wrapper

- Status: Accepted as an unissued T0 individual-assurance foundation
  candidate; T1/T2 dependencies, wrapper issuance, consumer migration,
  accountable review, and Gate A remain blocked
- Date: 2026-07-19
- Decision owners: constitutional authority, security, architecture review
- Gate effect: freezes the acyclic PRQ-013 individual-assurance candidate and
  the future wrapper boundary; grants no human-only slot, aggregate quorum,
  assignment, currentness, approval, scientific-results publication,
  recovery, promotion, runtime, external-effect, or Gate A authority

## Context

ADR 0089 established that a declared human principal and a cryptographically
valid signature do not establish a human-controlled Odeya decision. The
minimum nine affected decision schemas recorded there are not the whole
consumer surface. Human-only or conditionally human consequential acts also
appear in profile freezes, authority grants, corrections, retention and legal
holds, key approval and recovery, registry sealing, finding closure, recovery
verification, publication sealing, and operator-acceptance paths.

Changing those retained decision resources in place would violate their exact
schema identities and create a broad reissue cascade before the canonical
profile is issued. Adding an assurance reference inside the decision being
assured would also create a digest cycle:

```text
decision bytes -> assurance -> decision bytes
```

Authentication standards do not repair that cycle or supply Odeya's decision
meaning. NIST SP 800-63B-4 defines authentication intent as explicit
participation in an authentication request. The 26 May 2026 WebAuthn Level 3
Candidate Recommendation Snapshot supplies relying-party, origin, randomized
challenge, signature, user-presence, and user-verification ceremony
components. Neither establishes which Odeya material a natural person
reviewed, comprehension, cognition, substantive approval, exclusive custody,
delegation validity, current authority, effective-principal separation, or
aggregate quorum.

A second ambiguity must also be closed: assuring a later confirmation of exact
bytes is not the same claim as assuring the authorship or time of the source
decision. The assurance layer must not overwrite source-schema semantics or
launder one actor's earlier decision into another actor's authorship.

## Decision

Use a side-by-side, external, nonrecursive construction in which each candidate
chain represents one later ratification act by exactly one declared principal:

```text
unchanged exact source decision and candidate bytes
  -> one HumanDecisionAssuranceCore candidate
  -> exact raw Core-byte digest
  -> one HumanDecisionAssuranceEvidence candidate naming that digest
  -> exact raw Evidence-byte digest
  -> one HumanDecisionAssuranceSeal candidate naming that Core and Evidence
  -> future AssuredDecision wrapper over one or more individual seals
  -> controlled policy/currentness/authority/quorum evaluation
```

The Core binds:

- the exact source decision identity, schema resource, raw digest, byte count,
  and decision-value pointer, including equality between the Core artifact ID
  and the source record's `decision_id`;
- the exact candidate identity, version, schema resource, raw digest, and byte
  count;
- equality between the candidate ID, version, and raw digest named by the
  source decision and the candidate being ratified;
- exact decision and candidate bytes that the later ceremony is required to
  display and review;
- a later-ratification relationship, not an original-authorship relationship;
  and
- one principal, one verifier relation, one challenge request, and the
  singleton separation rule.

The source decision's own schema and consumer policy remain authoritative for
its meaning. The Core repeats relationship metadata that must equal the exact
source record, but does not transfer or reinterpret policy-bearing decision
value, effect, implementation lock, expiry, supersession, withdrawal, or
revocation authority.

The Core names both the source-decision actor and the later confirmer. The
retained positive fixture intentionally makes them distinct. It records the
source `decided_at` only to preserve the relationship, while explicitly
refusing to claim that the later ceremony proves original authorship or that
source timestamp. The later `confirmed_at` is an assurance timestamp.

The Core precedes the ceremony. Its material fields are exact display/review
requirements and its assurance relation is a requested later-ratification
relationship; neither is an observation that presentation, review, or
confirmation already occurred.

The Evidence record binds the exact raw Core bytes externally. It contains
exactly one participant observation and an ordered role-addressed set of
exact cryptographic inputs plus sanitized derived observation references. It
represents challenge, confirmation,
authentication, identity binding, custody, delegation, effective control,
controlled time, replay, sanitation, and verification observations with
explicit `supported`, `contradicted`, `unknown`, or `not_applicable` states.
Unknown never becomes false or approval.

The candidate does not dereference the backing evidence artifact bytes. It
checks the retained artifact IDs, roles, raw digests, byte counts, media types,
and reference relations. Assignment, natural-person identity, custody,
effective control, and verifier independence therefore remain synthetic
assertions under an unissued profile, not mechanically established facts.

The application confirmation gesture is separate from the authenticator
gesture. Its identifier is the raw SHA-256 of the referenced exact sanitized
material-presentation and decision-confirmation receipt. The receipt asserts
presentation identity; it is not retained pixel evidence or proof of
comprehension. The confirmation binds the assurance ID,
entire exact Core digest, session ID, challenge-request ID, content-derived
challenge ID, relying-party ID, expected origin, decision digest, and candidate
digest. A changed Core requires a fresh confirmation; mechanical downstream
rebinding cannot silently rewrite the asserted human act.

The receipt-to-authenticator binding remains one-way: the receipt names the
challenge, but the authenticator-signed challenge does not commit to the
receipt digest. The candidate therefore does not claim that the authenticator
actor and application-gesture actor are cryptographically co-bound. Profile
issuance requires either a cycle-free two-phase construction whose final
challenge commits to an exact pre-confirmation/presentation receipt or an
accepted transaction-confirmation trusted path.

The Seal binds the unchanged Core, exactly one Evidence record, and the exact
raw bytes of an unissued singleton-eligibility ruleset. It records an
individual eligibility disposition deterministically cross-checked by the
retained candidate checker. No independent implementation is retained.
Contradiction or a failed required categorical condition takes precedence and
is `invalid`; otherwise missing, `unknown`, or `not_applicable` required
support is `indeterminate`; only all-supported and all-satisfied input is
`eligible`.
`eligible` means that one act may enter future `AssuredDecision` assembly; it
never means approved and it never establishes aggregate quorum, currentness,
or authority. The Seal has no self-digest or embedded external attestation.

Fields currently named `quorum_rule` and `quorum_evaluation` are constrained
to exactly one principal and explicitly identify their scope as
`single_individual_assurance_not_aggregate_quorum`. Multiple principals must
produce multiple individual chains. A future wrapper, whose identity has not
been assigned, is the only place that may aggregate them.

Current decision schemas remain byte-identical. Their future consumers must
migrate to a separately identified `AssuredDecision` wrapper. A bare decision,
human-labelled principal, signature, timeout, silence, authentication
ceremony, Core, Evidence, or individual Seal cannot satisfy an `H` slot or
aggregate quorum.

The current Authority Matrix candidate wording therefore names only an
admitted `AssuredDecision` wrapper at an `H` slot and explicitly refuses every
individual record. That prose correction does not issue the wrapper or migrate
a consumer; the consumer census retains the exact predecessor matrix and the
exact amended matrix bytes as separate evidence boundaries.

At one controlled evaluation time, the future wrapper must dereference the
source decision, selected individual seals, and accepted evidence; apply the
source schema and consumer policy; evaluate expiry, supersession, withdrawal,
revocation, contradiction, correction, profile and evidence currentness;
establish assignment, authority, authenticator, effective-control, and
verifier-separation facts; compute aggregate quorum over distinct effective
principals; and atomically bind the evaluated frontier to the consuming
transition.

The T0 bootstrap uses exact raw SHA-256 and byte-count bindings. Raw hashes are
not canonical object identity. Reissue behind the accepted canonical profile
remains mandatory before admission.

## Challenge and ceremony profile

The static challenge-framing profile is a root of the byte-binding graph. It
contains no Core or test vector. The Core binds its exact raw bytes, while a
separate deterministic vector binds both the profile and Core. This ordering
prevents a profile-to-Core-to-profile digest cycle without weakening the exact
profile binding.

The WebAuthn challenge is the 32-byte nonce followed by the SHA-256 commitment
to the exact binary frame. Its `challenge_id` is the raw SHA-256 of those exact
64 challenge octets. The candidate pins:

- relying-party ID `odeya.danielwahnich.dev`;
- expected origin `https://odeya.danielwahnich.dev`;
- `navigator.credentials.get`;
- COSE algorithm `-7`, `ES256`, with substitution forbidden;
- at least 256 fresh random bits;
- a maximum 300-second half-open lifetime, issued-at inclusive and expires-at
  exclusive; and
- relying-party or independent-verifier generation with single, atomic
  consumption.

The required chronology is:

```text
source-decision.decided_at = Core.source_declared_decided_at
  <= Core.created_at
  <= challenge.issued_at
  <= confirmation.confirmed_at
  <= challenge.assertion_received_at
  <= challenge.consumed_at
  < challenge.expires_at
```

Assertion acceptance and the state transition from unused to consumed must be
one controlled atomic action. Exact-expiry assertions, prior consumption,
duplicate consumption, stale confirmation, or mismatched session, request,
challenge, relying party, origin, Core, decision, or candidate fail closed.

## Synthetic relationship control

The positive chain uses a dedicated, schema-valid source decision at
`tests/architecture-schema/fixtures/human-decision-assurance-decision-subject.valid.json`.
It names the
same candidate ID, version, and raw digest as the Core. Its declared source
operator is `fixture.operator-not-daniel`; the later confirmer is
`human.synthetic.operator.0001`. Its result is non-acceptance and its
implementation lock authorizes no runtime or external effect.

This fixture was created to test relational coherence without treating a
historical operator decision as ratification evidence. It is not Daniel's
decision, does not prove that either declared actor is real, and does not
establish authorship, display, review, decision time, authentication, or
authority.

## Standards profile

The candidate comparison pins:

- NIST SP 800-63B-4, final, July 2025:
  `https://csrc.nist.gov/pubs/sp/800/63/b/4/final`; and
- Web Authentication Level 3, Candidate Recommendation Snapshot,
  26 May 2026:
  `https://www.w3.org/TR/2026/CR-webauthn-3-20260526/`.

These are mechanism and assurance comparisons only. Exact frozen standard
copies, digests, conformance vectors, an accepted Odeya profile, and real
ceremony verification remain open.

## Required refusals

The isolated candidate suite must retain one-mutation, intent-bound known-bads
for:

- `PRQ-013-KB-001`, where a valid signature comes from an unattended
  agent-accessible human-labelled key, the claimed human-initiated remote
  operation is contradicted, and challenge, separate human gesture, identity
  binding, user presence, and user verification are absent or unknown; its
  contradiction-first disposition is `invalid`;
- wrong or changed source-decision ID, version, schema, raw bytes, decision
  pointer, candidate ID, candidate version, candidate raw bytes, displayed
  material, reviewed material, Core, Evidence, or framing-profile bindings;
- a source decision's candidate relation that disagrees with the exact
  candidate subject;
- any attempt to copy, rewrite, or treat Core fields as the semantic authority
  over the source decision;
- a confirmation transplanted across assurance, Core, session,
  challenge-request, content-derived challenge, relying party, origin,
  decision, or candidate;
- a gesture identifier that does not equal the exact referenced sanitized
  decision-confirmation artifact digest;
- any claim that the separate confirmation gesture and authenticator actor are
  cryptographically co-bound in this candidate;
- mutation or substitution of the exact unissued eligibility ruleset, or
  promotion of `not_applicable` required support to eligibility;
- an authenticator gesture counted as the separate application confirmation;
- challenge aliasing, malformed framing, replay, prior or duplicate
  consumption, non-atomic consumption, wrong chronology, or confirmation or
  assertion at or after expiry;
- more than one principal, participant observation, Evidence binding, or
  determination in an individual-assurance chain;
- unknown or contradicted authentication, custody, delegation, effective
  control, controlled time, sanitation, or verification observations promoted
  to individual eligibility;
- wrong-existing evidence-role substitution or missing direct confirmation
  and delegation/effective-control provenance;
- agent-triggered remote authentication, shared authenticators, hidden
  delegation, unresolved objections or conflicts, shared effective control,
  or producer/verifier collapse;
- retained raw private reasoning, reusable secrets, signing material,
  biometric/PIN material, or unrestricted prompts/model output;
- any claim that the individual Seal evaluated aggregate quorum, source
  currentness, expiry, withdrawal, revocation, contradiction, or authority;
- any consumer bypass, bare-signature acceptance, missing or indeterminate
  assurance promoted to authority, or eligibility compiled to approval; and
- self-digest, embedded-attestation recursion, or an annotation contradicting
  the structured no-authority boundary.

## Consequences and remaining blockers

The candidate schemas, consumer census, synthetic fixtures, and checker are
architecture evidence only. The synthetic source decision and ceremony
fixtures are not human decisions or real evidence. Their backing evidence
artifact bytes are not dereferenced. Assignment, identity, custody,
effective-control, and verifier-independence observations are asserted, not
mechanically established.

Context-isolated review by agents in this development session is correlated
review, not accountable or organizationally independent verification.

PRQ-013 closes in dependency order, not as one T0 step:

1. T0 may freeze only unissued candidates for the individual-assurance
   profile, exact evidence-store and backing-byte contracts, independently
   implemented singleton ruleset/verifiers, census, and synthetic
   conformance/refusal vectors. This is the PRQ-013 foundation prerequisite,
   not full closure or issuance.
2. T1 constructs the exact `AuthorityAssignment` vertical contract, and T2
   constructs the command, event, state, reducer, currentness, and quorum
   dependencies named by the census.
3. Only then may separately identified unissued `AssuredDecision` and
   successor-consumer candidates be constructed and their exact transitive
   migration and end-to-end refusal evidence be proved.
4. Gate A additionally requires independently reproduced architecture
   evidence, accountable security and authority review, and Daniel's exact-byte
   architecture decision. That decision governs issuance and admission; Gate A
   does not require or authorize a live protected ceremony.
5. One real protected ceremony under the accepted profile is a separately
   authorized, bounded Gate B probe. Runtime identity/policy conformance remains
   a Gate C implementation exit condition.

Profile issuance and admission, T1, Gate A, runtime, deployment, spending, data
access, scientific-results publication, and every external effect remain
blocked.
Architecture-repository publication is a separate exact-commit authority under
the repository release contract and is not conferred by this decision.
