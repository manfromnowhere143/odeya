# ADR 0093: Co-bind the confirmation gesture and authenticator actor through a two-phase challenge

- Status: Accepted as an unissued architecture-time design candidate, and
  adopted: the Core pins the v2 framing profile and the Evidence record carries
  the presentation challenge and confirmation receipt. Profile issuance,
  independent implementation, real ceremony, accountable security review, and
  Gate A remain blocked
- Date: 2026-07-20
- Decision owners: constitutional authority, security, architecture review
- Gate effect: closes the ADR 0092 issuance blocker in design only; grants no
  human-only slot, quorum, currentness, approval, runtime, external-effect, or
  Gate A authority

## Context

ADR 0092 froze the PRQ-013 individual-assurance candidate and recorded one
explicit reason the challenge-frame profile blocks its own issuance: the
signed challenge does not commit to the presentation/confirmation receipt
digest, so the application gesture a natural person performed and the
authenticator actor that produced the signature are not cryptographically
co-bound.

The v1 candidate frame commits to the Core, decision, and candidate schema
resource identities and raw digests, the session, the validity interval, the
relying-party identity, the expected origin, and a 256-bit nonce. Those fields
bind *what material the ceremony was about*. They do not bind *what the person
was shown and what they confirmed*.

Without that binding, an authenticator signature proves a credential was
exercised against a fresh challenge for a named decision subject. It does not
refute a presentation substitution: displaying one set of bytes to the person
while the authenticator signs a challenge derived from another. The two acts
remain separately attested and independently replaceable.

The direct repair is circular. A confirmation receipt necessarily records the
challenge it belongs to, because the receipt is produced after the challenge
is issued and presented. If the challenge then commits to the receipt digest:

```text
challenge -> receipt digest -> challenge id -> challenge
```

That cycle is why the v1 profile was deliberately made static and
nonrecursive, and why it was left unissuable rather than issued with an
unstated weakness. Preserving the honest refusal was correct. It is not a
resting state.

## Considered options

### Option A — accepted transaction-confirmation trusted path

Require an authenticator that displays the transaction text itself and returns
a signature over what it displayed. This is the stronger guarantee: the
display and the signing occur inside one attested device boundary, so
presentation substitution is refused by the authenticator rather than detected
afterward by Odeya.

It is rejected as the Gate A design for three reasons. It depends on
authenticator display capability that Odeya cannot assume, cannot pin as an
immutable identity, and cannot exercise synthetically at architecture time —
Gate A evaluates ceremony architecture with synthetic and independent
conformance evidence, not a live ceremony. It narrows the admissible
authenticator population to devices with a trusted display, which is a
material and undeclared restriction on who may hold a human-only slot. And its
conformance evidence would be unreproducible from repository bytes, which
conflicts with replay as the settlement mechanism.

It is retained as the preferred Gate C runtime hardening once an authenticator
population is bounded and independently evaluated. This ADR does not close
that path; it declines it as the architecture-time answer.

### Option B — two-phase challenge with an exact pre-confirmation receipt

Split the ceremony into two ordered phases with distinct challenge subjects,
so the receipt commits backward and the authentication challenge commits
forward. The cycle is broken by ordering rather than by omission.

This is the accepted option.

## Decision

Adopt a two-phase challenge. Phase one binds presentation; phase two binds the
authenticator to the exact presentation that already occurred.

**Phase one — presentation binding.** The relying party or independent
verifier issues a presentation challenge over a frame containing the Core,
decision, and candidate schema resource identities and raw digests, the
session, the validity interval, the relying-party identity, the expected
origin, and a fresh 256-bit nonce. This is the v1 frame unchanged; its field
order and encoding are retained exactly. Its identity is the
`presentation_challenge_id`.

The presentation surface renders the decision subject and records a
**confirmation receipt** over exactly the bytes it displayed. The receipt
commits to the `presentation_challenge_id`, the exact displayed byte digest,
the rendering profile identity, the confirmation gesture kind, and the
gesture's recorded instant. The receipt never contains the phase-two
challenge, which does not yet exist. Its identity is the
`confirmation_receipt_raw_sha256`.

**Phase two — authenticator binding.** The authentication challenge is
computed over a frame that extends the phase-one field list with three
appended fields, in this exact order:

```text
presentation_challenge_id
confirmation_receipt_raw_sha256
confirmation_receipt_profile_id
```

The authenticator signs a challenge derived from that frame. The signature
therefore covers the digest of what was displayed and confirmed, and the
gesture is bound to the actor that signed.

The dependency graph is a strict order with no back edge:

```text
phase-one frame -> presentation_challenge_id
                -> confirmation receipt -> confirmation_receipt_raw_sha256
                -> phase-two frame -> authentication challenge -> signature
```

No artifact commits to a digest of anything that commits to it.

### Retained construction rules

The phase-two frame reuses the v1 binary encoding without modification: the
`ODEYA-HDA-CHALLENGE-FRAME-V2` magic, `u16be` field count, name/value length
framing, exact ASCII text bytes with no normalization, 32 raw octets for
digest values, and 32 raw octets for the nonce. The challenge remains
`nonce || sha-256(frame)`, 64 octets, base64url without padding.

Both phases are single-use. Both carry a maximum 300-second lifetime on a
half-open interval. The phase-two validity interval must be contained within
the phase-one interval, so an expired presentation cannot be revived by a
fresh authentication challenge. Client-generated challenges remain refused in
both phases.

The receipt's displayed-byte digest is taken over the exact rendered bytes,
not over a re-serialization of the decision object. A presentation surface
that cannot produce its exact displayed bytes cannot participate.

## Consequences

The v1 candidate profile is superseded by an unissued v2 candidate. Its
`confirmation_receipt_digest_committed` and
`confirmation_gesture_and_authenticator_actor_cryptographically_co_bound`
boundary flags become true as *design* properties of the frame construction.
Every other proof-boundary flag remains false.

This closes the ADR 0092 issuance blocker in design and does not issue the
profile. Issuance additionally requires an independent architecture-time
implementation of the frame and receipt construction, exact evidence-store and
backing-artifact byte-verification contracts, end-to-end consumer refusal
proof, accountable security and authority review, and Daniel's exact-byte
acceptance. None of those exist.

What this decision still does not establish, stated plainly: it does not prove
comprehension, review, or substantive agreement; it does not establish
exclusive credential custody; it does not establish delegation validity,
current authority, effective-principal separation, or aggregate quorum; and it
does not refute a compromised presentation surface that lies about its own
displayed bytes. A presentation surface inside the trust boundary that
fabricates its receipt is refused by Option A and only detected, not
prevented, by Option B. That residue is the explicit cost of declining the
trusted path at Gate A, and it is retained rather than argued away.

## Adoption

Adopted on 2026-07-20. `schemas/human-decision-assurance-core.schema.json` and
its fixture pin the v2 profile
(`sha256:585952ace1c4e804c0443532ecb9fcc7eda6e7ce2cd1c18bfd459c0a14255273`,
5701 bytes) and carry `two_phase_challenge_required`, the exact fifteen-field
`authentication_commitment_fields` list, and an exact mirror of the receipt
profile. `schemas/human-decision-assurance-evidence.schema.json` and its
fixture carry `presentation_challenge` and `confirmation_receipt` on each
participant observation; the receipt object refuses an
`authentication_challenge_id` member, and that refusal is the acyclicity.

The receipt's displayed bytes bind a retained
`exact_unmodified_displayed_decision_bytes` evidence artifact rather than a
digest that exists only inside the receipt, and the receipt's
`confirmation_gesture_at` must equal the confirmation record's `confirmed_at`,
so one human act cannot be recorded at two instants.

Both implementations recompute the chain from the subject bytes and refuse to
trust a recorded identity. The assurance checker binds the receipt to the
*recomputed* presentation challenge id, so a session, origin, or
decision-subject substitution moves the real challenge instead of validating
against a stale one.

## Known-bad proof obligation

The design is not accepted as fired until the isolated suite refuses each of:

- a phase-two frame omitting any of the three appended fields;
- a receipt whose `presentation_challenge_id` does not match the phase-one
  challenge that produced it;
- a receipt whose displayed-byte digest differs from the rendered bytes;
- a phase-two challenge whose validity interval is not contained within the
  phase-one interval;
- a reused presentation challenge or reused receipt;
- a receipt produced before its phase-one challenge was issued; and
- any attempt to reconstruct the phase-two frame from a re-serialized
  decision object rather than the exact displayed bytes.
