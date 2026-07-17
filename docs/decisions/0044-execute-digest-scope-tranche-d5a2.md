# ADR 0044: Execute digest-scope tranche D5a-2

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: annotates the 72 context-dependent digest occurrences across
  the twelve contextual field-name rows; the audit's unscoped-digest count
  falls from 398 to 326

## Context

Twelve accepted rows name more than one domain or resolve their domain
through the record itself, so each occurrence had to be read in its schema
context: which registry owns the attestation, which member family the
contract belongs to, whether the reference resolves its target through a
sibling schema identity.

## Decision

Each occurrence was classified by its containing definition and schema:

- `registry_digest` inside a method, unit, or rule reference binds the
  method-registry, unit-registry, or validation-rule-registry domain; at a
  registry's own top level it binds that registry's declared or reserved
  domain.
- Attestation `subject_digest` and registry `member_digest` bind the owning
  registry's subject and member domains; the command-contract member binds
  the reserved command-contract-record domain.
- Generic reference definitions (`subject_reference`, `component_reference`,
  `exact_record_reference`, and kin) carry a target-resolved annotation: the
  domain is determined by the sibling schema identity at each use, and the
  annotation says so instead of inventing a domain.
- `candidate_digest` splits between the checkpoint domain and the reserved
  publication-candidate domain by context; `signed_digest`, `bundle_digest`,
  and `decision_digest` bind their per-schema domains; the reducer
  equivalence vectors carry an in-record-declared-separator annotation; the
  command envelope's `claimed_digest` is annotated as an untrusted client
  copy that must verify against the target's own domain.

## What the tranche caught

The version aligner's generic URN rewrite silently repaired the deliberately
wrong values inside eighteen known-bad traps — the D2a stale-trap failure
relearned from the other direction. The trap payloads were restored from
their recorded commit and the aligner is now trap-safe: in the lifecycle
case corpus it touches only declared guard text, never payload values. Two
cases needed the opposite: a category-confusion trap whose wrongness is
substituting the live schema URN for a logical type must track the live URN,
and a safe trace's exact frozen reference follows the reissued snapshot.

## Non-decisions

The mixed generic-digest family (284 occurrences) and the eighteen rows
awaiting the frontier/commitment construction decision (37 occurrences)
remain; no member is admitted and Gate A is not accepted.

## Consequences

Unscoped digest fields: 398 before, 326 after. Every annotation is traceable
to an accepted row and either a registered domain, a reserved domain, or an
explicit resolution rule that refuses to invent one.
