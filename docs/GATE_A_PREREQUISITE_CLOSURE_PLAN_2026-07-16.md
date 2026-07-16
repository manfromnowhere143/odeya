# Gate A Prerequisite Closure Plan

Status: active architecture-only correction tranche, 2026-07-16. This plan is
not a Gate A acceptance record, immutable registry, constitutional admission,
runtime authorization, deployment plan, or claim that Odeya is state of the
art. It converts independent checkpoint audits into a dependency-ordered
closure program without fabricating evidence that does not exist.

## Verdict

The current first-slice scope is bounded and its primary content-digest
direction is correct:

```text
schema -> state -> reducer -> event -> command
```

The checkpoint is not yet constructible as one immutable root. Structural
fixtures currently demonstrate schema shape with synthetic identities; they do
not form one digest-coherent graph. Bulk-authoring 42 missing payload schemas
before resolving the contradictions below would multiply unstable identities
and make review less reliable.

The correct next move is a prerequisite-closure tranche. It preserves the
exact representational boundary of 43 commands, 60 event types, 25 canonical
aggregate/reducer families, 11 owner modules, and one external constitutional
prerequisite. It changes no runtime and admits no member.

## Hard construction law

Content identity and constitutional evidence use two related acyclic graphs.
This is a prospective replacement/integration law. The current
EngineContractRoot, C0RegistryBundle, RootAuthorityManifest, LedgerCheckpoint,
P0, and RegistryActivation schema bytes do not implement the two-digest
core/evidence/seal profile. New schema identities plus a complete transitive
consumer migration are prerequisites, not work silently performed by this
plan.

Registry graph:

```text
exact retained schema bytes
  -> aggregate-state member
  -> reducer member
  -> event member
  -> command member
  -> pure registry subjects
  -> EngineContractRoot core and seal
  -> C0 core and seal
```

Constitutional evidence graph:

```text
sealed root/C0
  -> signed ledger checkpoint
  -> inclusion and consistency proofs
  -> independent witness observations and quorum evaluation
  -> clear recovery-frontier core and verification
  -> P0 core and admission seal
  -> exact handler/equality evidence
  -> RegistryActivation core and seal
  -> later command admission binding both P0 and activation
```

A reverse semantic edge uses exact logical identity plus
`same_root_exact_member`; it never embeds a future member digest and never
creates a content-hash fixed point. P0 cannot contain the identity or digest of
the activation that will contain P0. The activation binds P0; P0 remains
activation-independent.

For every evidence-bearing constitutional subject:

```text
immutable core digest
  -> evidence or decision naming that core digest
  -> seal naming the core and exact evidence set
  -> external attestations naming the seal digest
```

Evidence and signatures never enter the preimage of the identity they attest.
Re-signing, timestamping, witnessing, or transparency inclusion can add
verification material without changing the core scientific subject.

## Immediate contradictions to close

### PRQ-001 — Candidate parameters frozen; canonical profile unissued

The two retained implementations agree on the bounded vector suite, but the
exact nonrecursive candidate core and evidence binding now freeze the parser,
RFC 8785 serialization, canonical envelope, digest framing, future reference
shape, 21 current domain names, and eight version axes for review. This is a
candidate-parameter freeze, not profile issuance or acceptance. The current
103-schema/200-fixture migration audit remains blocking: 122
unprofiled date-time paths, 61 number/decimal findings, 668 unscoped digest
fields, 56 divergent common definitions, 11 unpinned profile bindings, and
238 nonconformant fixture timestamps. No final member digest may be
represented as frozen while those identity inputs remain unresolved. The
machine inventory separately preserves the exact tranche-start audit and
counts rather than rewriting history.

### PRQ-002 — Member and snapshot identities are incomplete

Command envelopes, receipts, policy decisions, and admission evidence refer to
`command-contract-record:0.1.0` without a standalone record schema. Several
also refer to `command-registry-snapshot:0.1.0`, while the replacement registry
graph contract uses `command-contract-registry:0.2.0`. One exact subject name
and one exact reference shape must be selected; aliases and filename inference
are forbidden.

Standalone state, reducer, event, and command member schemas are required so a
member can be hashed and independently validated without extracting an
anonymous nested `$defs` branch from its parent registry.

### PRQ-003 — Logical payload identity is not bound to schema bytes

Every command contract needs both:

- a logical payload identity and version used by command semantics; and
- an exact retained schema artifact identity, semantic artifact version, byte
  digest, and closed resolution pointer.

These version axes are explicit and need not be equal. The registry must prove
their declared binding. It cannot infer a payload contract from a filename,
`$id`, command version, event version, or current schema catalog.

### PRQ-004 — Event payload branch identity is unchecked

`ResearchEvent` 0.7.0 now distinguishes the logical `payload_type_id` from the
enclosing schema resource. The retained identity map binds each event type to
the exact `ResearchEvent` resource ID, raw-byte digest, byte count, and payload
subschema pointer for its discriminator. The per-payload contract itself is
still `unresolved_blocking`: its digest is null and the event is neither
admitted, dispatchable, nor replay-authoritative. Independent validation must
reject same-ID/different-bytes, wrong-pointer, logical-type/resource
substitution, implicit upcast, raw-digest drift, and byte-count drift. A future
resolved payload-contract digest requires a newly identified `ResearchEvent`
resource with an exact extraction and canonicalization profile.

### PRQ-005 — AuthorityGrant has an unreachable state

Grant issue currently jumps from `not_issued` to `active` while activation
requires `issued`. Issue must produce `issued`; activation alone produces
`active`. Expiry and revocation are legal from both `issued` and `active`.
Known-bad traces must reject use before activation, double activation,
issued-as-active, and use after expiry or revocation.

### PRQ-006 — Protocol has no legal origin

The frozen 60-event set contains no separate protocol-record event. To preserve
that reviewed set, `protocol.frozen` is the first-slice origin from aggregate
absence and materializes version one from an exact frozen snapshot plus
retained draft/validation evidence. Draft and validated candidates remain
artifacts, not hidden canonical Protocol states.

### PRQ-007 — Data-use authority contradicts the command profile

`data_use.decide` requires a bounded `data_rights` grant, but the event branch
currently describes assigned-role authority. The exact successful atomic cohort
is:

```text
authority.grant_used(data_rights)
  -> data_use.decided
  -> authority.grant_exhausted(data_rights)
```

A reject, replay hit, or no-op emits none of those events.

### PRQ-008 — WorkLease state vocabularies diverge

The first-slice canonical vocabulary is
`unleased|active|released|revoked|expired`. Aggregate absence remains the state
before origin. `stale` and `completed`, if retained, are projection or derived
dispositions and cannot silently become canonical reducer states.

PRQ-008 remains `unresolved_blocking` even though the state algebra is now
coherent and the exact
`urn:odeya:schema:canonical-work-lease:0.1.0` resource exists as an unissued
candidate. [ADR 0019](decisions/0019-materialize-fail-closed-work-lease-candidate.md)
adds positive/adversarial schema cases, exact `work` ownership, raw-byte
lineage, and direct-consumer review. Every instance still fails closed with a
null profile and canonical digest and no execution authority. No trace may
treat schema presence as resolved record identity, reducer correctness,
assignment admission, registry membership, activation, or Gate A evidence.

### PRQ-009 — Assignment requires artifacts it is meant to create

The existing `WorkContract` requires an already-active lease, canonical lease
frontier, reservation-created evidence, and dispatch rechecks. It therefore
cannot also be the prospective input from which `verification.assign` creates
the lease and reservation. Split the meanings:

```text
WorkIntent
  = prospective objective, capability/data/isolation ceilings,
    materialization intent, requested lease/reservation constraints,
    output/evidence obligations, and no dispatch authority

verification.assign atomic commit
  = grant use/exhaustion + reservation creation + lease acquisition
    + verification assignment, all bound to the exact WorkIntent

WorkContract
  = deterministic post-assignment artifact derived from the committed events,
    active canonical lease/reservation frontier, and exact WorkIntent
```

Neither WorkIntent nor WorkContract authorizes dispatch. `attempt.start`
separately rechecks current authority, data use, lease, reservation, sandbox,
and materialization and commits the claim/start cohort before bytes become
visible.

PRQ-009 remains `unresolved_blocking`, and C5 must not be reported resolved.
The retained WorkIntent candidate has unresolved identity inputs, a null
canonicalization profile, a null canonical digest, and no assignable authority.
The identity construction in
[ADR 0021](decisions/0021-separate-work-intent-core-from-identity-binding.md)
separates an exact semantic core from its external binding. The side-by-side
successor cohort in
[ADR 0022](decisions/0022-materialize-side-by-side-work-identity-successors.md)
now retains WorkIntent 0.1, canonical WorkLease 0.1, and WorkContract 0.2 while
adding exact WorkIntent 0.2, WorkLease 0.2, and WorkContract 0.3 resources. The
cohort rejects 37 known-bad mutations and uses no same-path mutation, mutable
alias, or implicit latest. Its source-view and planning-epoch values remain
synthetic, its legacy output-schema digest mismatches the exact target schema
bytes, and every canonical digest/admission/authority field remains absent or
false. Raw-byte and successor-resource binding is not canonical identity,
admission, or assignment authority.
The current `ResearchEvent` 0.7.0 assignment payload intentionally does not
invent a WorkIntent reference. Closure requires a newly identified resolved
WorkIntent, a WorkContract bound to that exact intent and assignment commit,
and a reissued ResearchEvent/EventContractRecord covering one exact 13-event
assignment cohort: five ordered grant uses, reservation creation, lease
acquisition, assignment, then five matching ordered grant exhaustions. Exact
current DataUseDecision, zero-external-capability sandbox/policy, reservation,
lease, grant, command, receipt, activation, and commit equalities are mandatory.

Direct WorkLease consumer review adds one exact C5 blocker. `attempt.start`
claims the reservation and `attempt.report` may later terminate the lease after
observed teardown, but `ResearchEvent` 0.7.0 currently constrains
`work.lease_released` to an unclaimed reservation with no claim event. The
reissued event contract must retain the claimed reservation and claim-event
identity while the lease terminates; only ResourceLedger settlement may clear
the claimed hold. Lease release cannot silently settle resources.

### PRQ-010 — Version axes are implicit

Command version, logical command-payload version, schema-artifact version,
event version, event-payload version, state-member version, and reducer-member
version are independent typed axes. Legal differences must be enumerated in
the exact member record. Equality or conversion cannot be inferred from a
shared major number or from prose. No implicit upcast is permitted.

### PRQ-011 — Constitutional fixtures are not one chain

The current root, C0, checkpoint, P0/activation, registry, and recovery fixtures
are structural examples with mutually inconsistent synthetic digests. They
must never be assembled into an admitted-looking chain. Until exact subjects
exist, construction emits only a typed `blocked` receipt containing the
resolved dependency graph, missing subject identities, refusal codes, and
evidence used to establish absence.

### PRQ-012 — Integrated semantic equalities are unproved

Structural validation does not yet reject all of these mutations:

- outer activation root or checkpoint differs from embedded P0;
- P0 contains a parent activation digest;
- handler count/set/digest differs from the admitted command surface;
- recovery frontier is positioned after activation or has a mismatched digest;
- a second genesis has no predecessor;
- activation scope permits effects that P0 forbids;
- witness identities or failure domains are duplicated;
- an attestation signs the wrong core or seal digest;
- root roles collapse into one principal or an impossible quorum; or
- witness candidate, checkpoint reference, and checkpoint digest disagree.

One pure cross-object verifier and a separate independent implementation must
reject every mutation before any candidate can become immutable.

## Exact construction tranches

### T0 — Identity and prerequisite closure

1. Retain the frozen-for-review canonical profile core and external raw-byte
   evidence binding; migrate or explicitly version every current consumer and
   blocker before profile issuance. Freeze the remaining key purposes, witness
   policy, and trust-bootstrap semantics without fabricating acceptance.
2. Add standalone member records and exact registry-snapshot identity.
3. Split core/evidence/seal/attestation subjects and add typed blocked
   construction receipts.
4. Close PRQ-005 through PRQ-010 without changing the 43/60/25/11 sets.
5. Retain positive, negative, and metamorphic vectors for every correction.

No immutable member is issued in T0.

### T1 — Smallest dependency-contained vertical contract

After T0 and exact schema-registry identities, construct only:

```text
AuthorityAssignment state schema/member
  -> AuthorityAssignment reducer member
  -> authority.assignment_recorded event member
  -> authority.record_root_assignment payload/command member
  -> authority.record_assignment payload/command member
```

Required traces cover constitutional origin, delegated assignment, duplicate
origin, self-issue, wrong owner, broken predecessor head, reorder, and a second
origin. This partial registry remains outside EngineContractRoot and C0.

### T2 — Remaining exact members in dependency order

1. Complete 25 state schemas and state-member records.
2. Complete 25 reducer records, rules, trace packages, and independent reducer
   evidence.
3. Complete 60 event records with exact payload-branch bindings and producer
   sets.
4. Complete 42 missing command payload schemas and all 43 command records.
5. Build pure registries and prove map key, ordering, count, commitment,
   ownership, version, schema, and cross-edge equality.

Every tranche is reviewable and reversible before a parent root is created.

### T3 — Inactive constitutional candidate

First assign and review replacement constitutional schema identities and
migrate their complete transitive consumer graph. Only after that migration and
T2 may the project construct exact root and C0 core/seal subjects. Then create
a checkpoint candidate, obtain independent inclusion/consistency and witness
evidence, resolve the recovery frontier, create P0, and prove exact handler-set
equality. Gate A has no runtime handlers, so the accepted architecture endpoint
is a checkpoint-ready but operationally inactive candidate. No activation may
pretend that absent handlers or external witnesses exist.

## Review and acceptance bars

This tranche closes only when:

- every PRQ finding has an owner, exact changed bytes, positive vector,
  known-bad vector, and independently reproduced verdict;
- all registry and constitutional digests reproduce from a clean clone in two
  non-sharing implementations;
- every forward digest edge and reverse logical edge resolves within the exact
  same root without cycles;
- all lifecycle families have a legal origin and total, fail-closed transition
  table for the admitted event set;
- missing, unknown, unavailable, unmeasured, invalid, inconclusive, disputed,
  blocked, and refused states remain distinct;
- independent scientific review, security review, recovery review, and
  architecture red-team findings are closed or explicitly accepted within the
  Gate A rule; and
- Daniel accepts the exact candidate bytes. That acceptance still does not
  authorize runtime implementation; Gate C remains separate.

## Current work inventory

At the start of this tranche:

- 98 schemas and 564 shared structural cases pass;
- 43 command names are exact, with one closed payload candidate and 42 missing;
- 60 event discriminators and 25 aggregate/reducer families are exact;
- 43 command records, 60 event records, 25 state records, and 25 reducer records
  are missing;
- 33 of the 60 event types have no fixture occurrence;
- the canonical profile migration audit remains blocked by the exact findings
  recorded in PRQ-001; and
- the prospective constitutional core/evidence/seal profile has no assigned
  replacement schema identities and no completed transitive consumer
  migration; and
- no real EngineContractRoot, C0, witnessed checkpoint, recovery frontier, P0,
  handler-equality report, or RegistryActivation exists.

Passing validators describes the retained bounded evidence. It does not erase
this inventory or convert a placeholder into an authority-bearing subject.

## Standards comparison

The current primary-source comparison and exact limits are retained in
[Odeya Standards Profile](STANDARDS_PROFILE.md). The architecture deliberately
combines reviewed primitives while keeping their claims separate: JSON Schema
for shape, JCS for bounded canonical bytes, DSSE/in-toto for typed attestations,
Sigstore bundles for portable verification material, SLSA for supply-chain
expectations, TUF for root-continuity comparison, and transparency
inclusion/consistency plus independent witnesses for anti-equivocation. None
of them supplies Odeya's scientific constitution or makes a result true.
