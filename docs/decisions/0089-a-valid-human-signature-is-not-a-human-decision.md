# ADR 0089: A valid human signature is not a human decision

- Status: Executed as a Gate A prerequisite correction; PRQ-013 remains
  unresolved
- Date: 2026-07-19
- Decision owners: constitutional authority, security, architecture review
- Gate effect: prevents a declared human principal or valid signature from
  satisfying a consequential human-only decision without separate
  decision-assurance evidence; grants no assignment, approval, publication,
  external effect, runtime, or Gate A authority

## The observed defect

Inbar retained a concrete failure at commit
`0f04aab32a64b7d7501aec1bf318270ef653d970`. Its README blob
`50fa073a4f21842d48aeff39105173c0b704c507` records that an automated agent
could read an unencrypted governance key, mint a cryptographically valid
receipt, and sign amendments that the named owner did not review. The machine
surface saw a valid owner signature while the approval-basis limitation lived
only in prose.

Odeya already states the cryptographic limit: successful signature verification
establishes that exact bytes validate under a referenced public key, algorithm,
and trust profile. It does not establish who caused the signing operation,
controlled the private key, reviewed the subject, acted independently, or
remained uncompromised. The current structural candidates nevertheless leave a
consequential gap:

- `RootAuthorityManifest` 0.4.0 accepts signed decision evidence;
- `AuthorityAssignment` 0.3.0 accepts a `signed_by` human principal;
- `ReviewDetermination` 0.3.0 accepts a human reviewer and signature; and
- `OperatorArchitectureDecision` 0.4.0 accepts an operator binding, decision
  basis, and signature.

Those shapes do not require separate evidence that the human controlled the
decision act, reviewed the exact material set, or kept the signing capability
outside agent/model/tool reach. Other human decision records have the same
possible defect. Structural validity can therefore look like human approval
while proving only that a key and declared principal fields were present.

## Decision

Add blocking prerequisite PRQ-013. Every policy-defined consequential
human-only decision must resolve a separate `HumanDecisionAssurance` contract
before it may satisfy an `H` slot, quorum, root/assignment decision, Gate A
review, public release, recovery, promotion, or other consequential authority
rule.

The future nonrecursive contract binds one exact decision subject and requires:

1. the exact decision/candidate digest and explicit decision value;
2. bounded reason codes, evidence basis, limitations, and the exact reviewed
   material-set digest;
3. a verifier- or relying-party-generated unpredictable challenge bound to that
   decision, session, and controlled time, plus a separate human-initiated
   confirmation gesture;
4. authentication-intent, phishing-resistant credential, user-presence,
   user-verification, principal identity-proofing, and
   principal-to-authenticator binding evidence as ceremony components;
5. signing-key and session-custody observations, including exclusion of
   unattended agent/model/tool signing capability;
6. delegation scope/depth, objections, effective-control, the required
   distinct-principal separation, conflict disclosures, and quorum evaluation;
7. expiry and replay protection; and
8. sanitized ceremony evidence plus independent verification.

Authentication intent is not decision intent. User presence, user
verification, a signature, or an authorization gesture cannot prove that a
person read, understood, or agreed with the decision. The assurance record
therefore makes a bounded evidentiary claim under one profile; it does not
claim access to mental state. Raw private reasoning, reusable secrets, signing
material, and unrestricted prompts/model output are forbidden evidence.

No current schema identity is mutated by this decision. The exact assurance
core/evidence/seal shape, complete affected-consumer census, replacement
identities or external wrapper, transitive migration, semantic equalities, and
accountable review remain open. T1 `AuthorityAssignment` cannot start until the
PRQ-013 candidate boundary is closed.

## Standards comparison

[NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
uses explicit claimant action to establish authentication intent and requires
phishing-resistant controls at higher assurance. [WebAuthn Level
3](https://www.w3.org/TR/webauthn-3/) distinguishes user presence, user
verification, authorization gestures, and consent, and explicitly notes the
limits of shared authenticators and user-presence tests. Odeya uses those
mechanisms as authentication/ceremony evidence only; neither standard supplies
Odeya's scientific, constitutional, approval, or publication meaning.

## Retained known-bad obligations

The Gate A prerequisite checker now rejects sixteen direct mutations:

- promote signature validity to proof of private-key or actor control;
- promote a valid signature to proof of human decision intent;
- promote authentication intent to substantive decision intent;
- promote a protected ceremony to proof of review, understanding, or cognition;
- promote a declared human principal to a completed decision;
- accept an unattended agent-accessible signing key;
- accept timeout or silence;
- promote missing assurance to approval;
- omit explicit decision basis and limitations;
- omit the human-initiated confirmation gesture;
- omit user-presence and user-verification evidence;
- omit principal identity-proofing and authenticator binding;
- omit delegation scope/depth, objections, and effective control;
- omit required distinct-principal quorum evaluation;
- retain raw private reasoning as ceremony evidence; or
- self-close the prerequisite.

The checker separately rejects a T1 dependency mutation that removes PRQ-013
from `next_dependency_contained_tranche.may_start_after`; documenting the
prerequisite without binding its consumer would leave the gate decorative.

Later semantic suites must additionally reject a correct signature over the
wrong decision digest, stale or replayed confirmation, a human who declined or
could not determine review, hidden shared effective control, an agent-triggered
remote authenticator, and any consumer that bypasses the assurance reference.

## Consequences

This correction makes constitutional progress slower when no accountable human
decision evidence exists. That is intentional. A missing human remains
`blocked` or `indeterminate`; an agent cannot repair the absence by using a
human-labeled key or writing stronger prose.

The retained checker is finite and author-correlated. It proves only that this
candidate inventory carries the refusal boundary and that its sixteen pinned
mutations fire. It does not produce the future assurance schema, verify a real
human ceremony, establish key custody, close PRQ-013, accept Gate A, or
authorize implementation.
