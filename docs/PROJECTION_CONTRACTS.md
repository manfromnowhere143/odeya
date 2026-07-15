# Projection Contracts

Status: proposed Gate A engine contract, 2026-07-15; machine-schema candidate 0.1.0 added 2026-07-16. Daniel owns Odeya's visual and interaction design. This document defines the exact truth, freshness, disclosure, and authority boundary that any private cockpit, thesis intake, public research surface, export, or static design fixture must consume. It does not authorize UI/runtime implementation or public release. Passing the isolated schema package closes only the machine-shape portion of IRT-042; independent reducers, real fanout traces, information-flow evidence, exact release-settlement resolution, accessibility review, and operator acceptance remain open.

## First law

A projection is a rebuildable view over exact canonical facts. It is not canonical state, scientific evidence, authority, a publication decision, or proof that an external recipient can see anything.

```text
canonical event/checkpoint + immutable objects + current access/publication facts
  -> versioned pure reducers
  -> access/redaction compiler
  -> materialized projection snapshot with source position and omissions
  -> UI, API, export, or static renderer
```

The client may request a command, but it never derives permission or a scientific transition from displayed state. The server admits any request again against current canonical state, controlled time, policy, authority, data, and resource facts.

## Common projection envelope

Every projection type shares one closed envelope:

```text
projection ID, type, schema version, and semantic profile
projection subject and audience/purpose
source kind and exact typed source reference (type/ID/version/schema/profile/digest)
ledger epoch, stream, inclusive position, aggregate and version where applicable
checkpoint coverage and witness acknowledgement status
reducer name/version/build digest and compatibility range
one exact compatible C0 registry-snapshot reference binding canonicalization/schema/rule/reducer versions
generated-at controlled time and last canonical fact time
authoritative dependency frontier observation, checked-at/valid-until, freshness state/reason, required/current position, and age
completeness state and typed omission manifest
reconciliation/invalidation/correction frontier
access/redaction decision references
independent reducer-equivalence result or explicit `not_run`
serve-time rights/purpose/audience decision and cache/pointer invalidation frontier
```

The subject contains no self digest or enclosing-package digest. After schema validation, the canonicalization registry issues its canonical-object digest externally; a separate package manifest/root may then bind the projection digest and constituent byte digests. `source reference` identifies the canonical source object, not a claim that the projection itself is truth.

`current` is an earned serve-time state. Missing/expired frontier observation, unknown checkpoint lineage, unresolved fork, incompatible reader, missing/failed required reducer equivalence, required correction/rights/deletion fanout, or unavailable source produces `stale`, `partial`, `quarantined`, or `unavailable` as specified; it never defaults current. `not_run` can be current only for an explicitly non-live `static_architecture_fixture`; every canonical or recovered live projection fails non-current until required equivalence evidence passes.

The envelope distinguishes:

- a byte digest;
- a canonical-object digest under an exact profile and schema;
- a logical artifact identity;
- a Git commit/tree/blob identity;
- a ledger event/checkpoint identity; and
- a bounded semantic-equivalence determination.

None is silently substituted for another.

### Machine contract candidate (IRT-042)

The smallest closed candidate family is four acyclic subjects:

| Subject | Schema | Boundary |
|---|---|---|
| Projection snapshot and common envelope | [`projection-snapshot.schema.json`](../schemas/projection-snapshot.schema.json) | One exact envelope with closed `projection_type` discrimination for `private_cockpit`, `thesis_intake`, `public_research`, and `static_architecture_fixture`; no branch can carry another branch's payload |
| Redaction/omission manifest | [`projection-redaction-manifest.schema.json`](../schemas/projection-redaction-manifest.schema.json) | Included/withheld field-object partition, transformations, residual inference risk, provenance, limitation preservation, expiry/review, and correction/rights/deletion/recovery fanout |
| Reducer-equivalence result | [`reducer-equivalence-result.schema.json`](../schemas/reducer-equivalence-result.schema.json) | Two independently identified paths, order/duplicate/chunk/checkpoint perturbations, bounded semantic-vector comparison, fail-closed reader behavior, and the static-only `not_run` exception |
| Dependency/fanout impact record | [`projection-impact-record.schema.json`](../schemas/projection-impact-record.schema.json) | Monotone affected-set selection and mark-noncurrent/cache/pointer/rebuild/equivalence/retention obligations for correction, invalidation, retraction, rights, deletion, recovery, effect, and release facts |

Every subject binds an exact engine-contract root, C0 bundle, canonicalization profile, and applicable checkpoint/frontier. The snapshot also retains exact audience, purpose, source, reducer, controlled-time lease, completeness, correction, rights, deletion, recovery, effect, release, redaction, equivalence, and impact references. For a static fixture, ledger/checkpoint and live governance facts use a closed `not_applicable_static` shape; that exception cannot validate for a live, pinned, private, thesis, or public projection.

Construction is deliberately non-recursive. Supporting subjects identify the target by logical projection ID/version/type but contain no target content digest. The snapshot contains exact externally issued references to completed supporting subjects but no self or package digest. Canonical-object digests are issued only after each complete subject validates; a later external package may bind those digests under a separately defined, acyclic digest scope. The equivalence record hashes a normalized semantic vector whose domain excludes the snapshot envelope and equivalence reference, never the enclosing snapshot bytes.

These schemas remain derived, non-authoritative records. Structural validity does not establish source availability, digest equality, registry membership, reducer independence, scientific validity, access, public eligibility, exact visibility, or a successful external effect.

## Orthogonal truth axes

A view never compresses research into one status. It carries only the axes relevant to its subject, preserving at least:

| Axis | Founding values |
|---|---|
| Source/fixture | `live_canonical`, `pinned_source_snapshot`, `static_architecture_fixture` |
| Operational | `not_started`, `running`, `interrupted`, `blocked`, `infrastructure_failure`, `closed`, `unknown` |
| Protocol | `not_frozen`, `frozen`, `amended_prospectively`, `forked`, `invalid`, `unknown` |
| Scientific validity | `not_assessed`, `valid`, `invalid`, `indeterminate` |
| Measurement | `measured`, `missing`, `unmeasured`, `unavailable`, `withheld`, `not_applicable` |
| Value origin | `observed`, `estimated`, `inferred`, `source_reported`, `derived_projection`, `unknown`, `not_applicable` |
| Scientific outcome | `not_adjudicated`, `supported_within_scope`, `contradicted`, `falsified`, `null_result`, `inconclusive`, `refused` |
| Verification | `not_requested`, `pending`, `confirmed`, `rejected`, `inconclusive`, `invalid`, `blocked`, `disputed` |
| Replication | `not_attempted`, `in_progress`, `independently_replicated`, `failed`, `inconclusive`, `invalid` |
| Transport | `not_attempted`, `in_progress`, `transported`, `not_transported`, `inconclusive`, `invalid` |
| Claim | `none`, `proposed`, `ineligible`, `eligible`, `superseded`, `corrected`, `retracted` |
| Publication | `not_requested`, `requested`, `denied`, `authorized`, `sealed`, `releasing`, `completion_unknown`, `released`, `corrected`, `withdrawn` |
| Rights/disclosure | `not_assessed`, `permitted_for_projection`, `denied`, `indeterminate`, `revoked`, `expired`, `withheld` |
| Integrity/recovery | `current_verified`, `stale`, `partial`, `quarantined`, `fork_suspected`, `restore_unverified`, `unavailable`, `not_applicable_static` |

Not every combination is legal. Cross-axis rules prohibit, for example, `null_result` without valid measurement, `eligible` after unresolved required verification, `released` without exact-visibility settlement, or `current_verified` on an unverified restored projection.

`zero` is a quantity value, never a state. `unknown`, `unmeasured`, `missing`, `withheld`, and `not_applicable` are never rendered as zero or as one another.

A displayed scientific quantity is never a generic JSON number. The machine contract uses canonical exact-decimal strings, rejects negative-zero spellings, exponents, and leading zeros, and binds every value/interval to an exact decimal profile, quantity kind, estimand/effect scale, registered unit, semantic kind, and semantic definition. Interval ordering and zero containment are evaluated with exact decimal arithmetic, never binary floating point. Missing, unavailable, withheld, unmeasured, or not-applicable values carry `null` plus their typed state, not a numeric sentinel.

## Projection types

### `private_cockpit`

Purpose: authorized mission/portfolio orientation, inspection, decision preparation, and recovery.

It may include, subject to access and purpose:

- mission/protocol/work/attempt state;
- evidence, measurements, uncertainty, falsifiers, and contradictions;
- verification, adjudication, claim, correction, and dependency state;
- data rights/exposure/retention/deletion/hold state;
- authority assignments/grants/reservations/uses and remaining resource envelope;
- effect ambiguity/reconciliation, incidents, checkpoint/recovery state; and
- exact next legal actions as a derived list.

It may not:

- expose sealed truth to a producer role;
- treat a derived next action as permission;
- silently omit rights, correction, blocker, stale, or dispute state;
- reveal secrets, private chain-of-thought, unrestricted raw prompts, or reusable credentials; or
- allow local/client state to alter canonical meaning.

### `thesis_intake`

Purpose: accept and track a contributed question/material package before mission admission.

It carries proposal identity, contributor-visible custody, declared rights, risk/quarantine state, review/admission state, withdrawal path, and bounded reasons. It never displays `accepted into research` as `true`, `supported`, or `absorbed into knowledge`.

The projection cannot expose another proposal, private mission, reviewer-only note, sealed evaluation, or internal source through identifiers, counts, timing, errors, retrieval suggestions, or cache leakage. Its contract binds leakage class, mission/proposal/role/purpose cache namespace, count-coarsening/suppression rule, normalized error surface, observable-response equivalence class, and timing-budget/padding policy. These controls bound rather than claim elimination of timing and aggregate side channels. Withdrawing a proposal does not rewrite prior custody or legal obligations.

### `public_research`

Purpose: show only an exact release-settled research package and its current correction/withdrawal state.

Eligibility requires all of:

```text
exact publication candidate
+ human publication decision over that candidate
+ deterministic final manifest
+ later single-use grant bound to that manifest
+ external-effect dispatch claim
+ exact effect state `confirmed_applied`
+ independent exact-visible observation for intended channel/audience
+ canonical `publication.release_settled(to=released)` consequence over both facts
+ disclosure-specific active DataUseDecision
+ serve-time rights/purpose/audience/expiry decision and current correction/withdrawal/deletion/quarantine/cache fanout
```

A seal, grant, dispatch, provider 2xx, callback, timeout, exact-visible observation without confirmed application, or UI cache cannot establish `released`. Public projection reads only the canonical release-settled package; it cannot reconstruct wording from private claims or query arbitrary private state.

On correction, withdrawal, rights revocation, quarantine, or integrity loss, the public view serves the required current notice or fails closed. A stale copy cannot remain current merely because a CDN or browser still has bytes.

### `static_architecture_fixture`

Purpose: evaluate design before any engine projection or public release exists.

It binds exact local fixture/source identities and states plainly that it is static, non-live, unreleased, non-authoritative, and possibly synthetic. Live-ledger/checkpoint/publication fields are `not_applicable`, never fabricated. A static design can demonstrate the visual grammar for supported, inconclusive, invalid, blocked, stale, corrected, or withheld states; it cannot imply Odeya already produced those mission events.

## Freshness and completeness

Freshness is a structured fact:

```text
state: current | stale | partial | quarantined | unavailable
authoritative dependency-scoped frontier observation reference
required ledger epoch/position
included ledger epoch/position
last canonical fact time
generated-at time
serve checked-at time and validity deadline under exact clock profile
maximum accepted age and clock profile
reason codes
affected sections/claims/actions
reconciliation and rebuild reference
```

Required reasons include `projection_lag`, `source_unavailable`, `reader_incompatible`, `checkpoint_unwitnessed`, `fork_suspected`, `restore_unverified`, `correction_pending`, `rights_changed`, `deletion_pending`, `effect_ambiguous`, `reducer_disagreement`, and `access_recompute_required`.

The `required` frontier is derived from an exact current-security/publication/rights/correction observation, not chosen by the projection. A serving decision rechecks that observation, its lease/expiry, and each affected dependency; a snapshot cannot self-certify freshness forever.

Completeness separately declares all expected sections/dependencies, present items, omitted items, redactions, unsupported versions, and unavailable artifacts. Empty omission lists require a completed registered coverage rule. Redaction is not completeness and withheld is not missing.

## Redaction and disclosure

Redaction compiles from an exact audience, purpose, policy, decision, data class, field/object set, and ledger position. It produces a retained manifest with:

- included exact objects/fields;
- withheld objects/fields and policy-safe reason codes;
- transformations and before/after identities;
- residual metadata and inference risk;
- citation/provenance preservation;
- expiry/review and correction/deletion fanout; and
- proof that no required scientific limitation was redacted from otherwise displayed evidence.

Redaction cannot widen rights, convert a denied decision to a public package, or make an incomplete claim appear fully supported.

## Correction, withdrawal, and recovery

Every projection retains a dependency index from displayed object to exact canonical sources and publication packages. A correction/invalidation/retraction/rights/deletion/recovery event computes affected projections monotonically.

Serving order is:

```text
observe invalidating fact
  -> mark affected current projections stale/quarantined
  -> rebuild under current policy and reader versions
  -> independently compare where required
  -> atomically advance projection pointer
  -> retain prior snapshot only when current rights/hold/retention policy permits;
     otherwise destroy covered bytes and retain the minimum lawful non-content tombstone
```

A restored database does not reopen a projection. The projection must catch up to the current-security frontier and pass restore verification before serving any affected scope.

## Client boundary

The client may preserve selection, focus, layout, acknowledgement cursor, and local presentation preferences. These never become scientific facts.

Every visible action distinguishes:

- `available_next_legal_action`: a derived suggestion at one source position;
- `command_draft`: untrusted user input;
- `submitted`: transport acknowledgement only;
- `accepted/rejected/noop`: exact retained command receipt; and
- `externally_settled`: later observation where the action crossed a boundary.

Optimistic UI may acknowledge local interaction but cannot optimistically show scientific, authority, spend, effect, deletion, or publication completion.

## Required adversarial fixtures

Before Gate A acceptance, machine schemas and reducer traces must reject or render correctly:

1. interval crossing zero shown as null/equivalent/supported;
2. invalid run shown as failed hypothesis or null result;
3. missing/unmeasured/withheld shown as zero;
4. source-reported label replacing Odeya adjudication;
5. eligible private claim shown as publicly released;
6. sealed manifest shown as exact-visible release;
7. provider timeout/2xx, exact-visible observation without confirmed effect, or confirmed effect without release settlement shown as release success;
8. correction hidden behind the original claim;
9. stale projection with no position/reason;
10. restored projection served before current-security frontier verification;
11. rights-revoked attachment remaining public while text is corrected;
12. redaction removing a limitation while retaining the favorable estimate;
13. sealed truth leaking into producer cockpit or thesis suggestions;
14. thesis admission rendered as scientific acceptance;
15. one proposal inferring another through counts, errors, timing, or identifiers;
16. client-cached grant/next action treated as current authority;
17. event delivery order changing the reducer result silently;
18. old reader ignoring an unknown safety-relevant enum;
19. static fixture presented as live engine state; and
20. color/motion/hover-only distinction with no text/table equivalent.
21. live projection marked current with reducer equivalence `not_run`;
22. once-current snapshot served after its frontier/rights lease expires;
23. prior projection bytes retained after a deletion decision permits only a tombstone;
24. projection/package self digest or mutually recursive content-digest references; and
25. thesis cache/count/error/timing path crosses its declared observable-equivalence policy.

The isolated checker at [`tests/projection-contracts/check.py`](../tests/projection-contracts/check.py) passes 62 cases: eight valid synthetic subjects, 37 schema-level rejection cases, 25 bounded local semantic cases, and explicit coverage of all 25 vectors above. It additionally checks exact in-package root/C0/checkpoint identity equality, controlled-time lease ordering, current required/included frontier equality, public effect/settlement/disclosure reference equality inside one snapshot, exact-decimal lexical safety and `Decimal` interval semantics, limitation-set coverage, reducer-path distinction, semantic-vector equality, impact-count reconciliation, deletion tombstone behavior, and isolated schema-reference closure. This is structural and bounded local evidence only; it is not a reducer trace, a leakage proof, an external-visibility observation, or Gate A acceptance.

## Gate A acceptance

This family remains open until:

- the exact closed envelope plus private/thesis/public/static machine shapes survive registry integration and independent review (the isolated 0.1.0 candidate exists);
- every displayed state maps to exact canonical fields and registered reducer versions;
- private, thesis, public, and static fixtures cover the full orthogonal vocabulary;
- two independent reducer paths agree on the first-slice projection vectors;
- correction, deletion, rights, recovery, and publication fanout traces pass;
- information-flow review closes cross-audience leaks;
- Daniel accepts the exact state language and surface contract;
- accessibility/human-factors reviewers confirm that distinctions survive nonvisual use; and
- critical/high findings are closed on the exact candidate.

Gate A accepts the data/authority contract, not a visual design. UI implementation, usability performance, browser behavior, and exact public-channel serving remain later authorized evidence.

Residual IRT-042 obligations are intentionally explicit: resolve every exact reference and digest against the admitted registry graph; implement and independently execute two reducer paths; prove delivery-order, duplicate, replay, and unknown-enum behavior over retained traces; execute monotone correction/deletion/rights/recovery/effect/release fanout against real cache and pointer stores; prove public output equality to the one exact release-settled manifest and current disclosure decision; run proposal-pair leakage, count, error, retrieval, cache, and timing experiments; and complete accessibility, human-factors, security, privacy, and operator review. Until those pass, no projection is canonical truth, evidence, authority, a publication decision, or proof that any recipient can see released bytes.
