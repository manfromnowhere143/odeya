# Provenance and Research-Package Export Profile

Status: proposed Gate A interoperability profile, 2026-07-15. This profile maps Odeya records to W3C PROV and RO-Crate without making either external representation canonical. It does not authorize an export, release, DOI registration, or public package.

## Boundary

Odeya's canonical event/object bytes, scientific semantics, authority, rights, and publication settlement remain authoritative. PROV, JSON-LD, RO-Crate, Workflow Run RO-Crate, DataCite, Crossref, JATS, CRediT, and CodeMeta are recipient-specific projections.

```text
exact Odeya checkpoint + authorized object set
  -> deterministic provenance projection
  -> rights/redaction validation
  -> RO-Crate/PROV package
  -> independent semantic and byte validation
  -> optional publication candidate
```

Importing the package again creates a new validated import observation. It cannot recreate or overwrite canonical history by trusting its own claims.

## Identity rules

Every exported node carries:

- stable export URI scoped to the exact package;
- Odeya logical object type, ID, semantic version, and canonical digest;
- canonicalization profile and schema identity;
- source ledger epoch/position/checkpoint where applicable;
- visibility/redaction class;
- current/superseded/corrected/retracted relationship; and
- the exact exporter profile/version/build digest.

An HTTP identifier is a locator unless its contract explicitly makes it an immutable identifier. Git commits, artifact byte digests, canonical object digests, DOIs, URLs, PROV identifiers, and RO-Crate `@id` values remain different typed identities.

## Core mapping

| Odeya object | PROV class | RO-Crate representation | Odeya semantics that must be retained |
|---|---|---|---|
| Source, dataset, protocol snapshot, code, environment, model, artifact, metric/falsifier result, claim version, publication manifest | `prov:Entity` | `CreativeWork`, `Dataset`, `SoftwareSourceCode`, `MediaObject`, or Odeya contextual entity as applicable | exact identity, role, scope, version, validity, rights, sensitivity, uncertainty |
| Acquisition, transformation, run, analysis, verification, adjudication, correction, release, reconciliation | `prov:Activity` | `CreateAction`, `UpdateAction`, `OrganizeAction`, `HowTo`/workflow/run profile as applicable | exact protocol/method, controlled time, attempt, inputs/outputs, status, authority, resource use |
| Human, organization, execution identity, model invocation, tool, instrument, provider adapter | `prov:Agent` or qualified contextual entity | `Person`, `Organization`, `SoftwareApplication`, instrument/contextual entity | principal class, role, execution identity, model/tool version; never inferred personhood or authority |
| Claim-evidence dependency | qualified derivation/usage plus Odeya relation | Contextual edge/entity when relation metadata is required | `supports`, `contradicts`, `tests`, `falsifies`, shared-evidence group, scope, rule, activity |
| Correction/supersession/retraction | `prov:wasRevisionOf` plus Odeya typed edge | `isBasedOn`/version relations plus Odeya terms | correction versus supersession versus retraction; prior bytes remain visible |
| Verification | activity + generated verification entity + qualified association | run/action plus result entity | verifier identity, exposure, conflicts, independence vector, known-bad results, per-dimension disposition |
| Authority assignment/grant/use | Odeya contextual entities/activities; PROV association is insufficient | Odeya extension records referenced from actions | role, scope, quorum, time, consumption point, reservation/use/release; no generic `authorized` inference |
| Data-use/publication decision | Odeya contextual decision entity/activity | Odeya extension referenced by included objects/actions | exact purpose, recipient, provider, region, operation, time, human dispositions |
| Operational blocker/invalidity/null/inconclusive | Odeya status objects, not generic failed activity | Odeya extension fields with accessible labels | orthogonal operational, validity, measurement, adjudication axes |
| Checkpoint/witness/receipt | entity/activity with exact cryptographic profile refs | contextual entity in package manifest | byte/ordering evidence only; no scientific-truth implication |

PROV association never grants Odeya authority. `prov:wasGeneratedBy` does not prove correctness. `prov:wasAttributedTo` does not establish authorship, ownership, rights, independence, or endorsement.

## Required Odeya namespace

The export profile defines versioned terms for meanings not carried safely by generic vocabularies, including:

```text
mission and protocol identity
source role and exposure class
claim type, scope, estimand, eligible/forbidden language
scientific validity, measurement disposition, adjudication outcome
uncertainty/evidence-measure/method identity
falsifier and known-bad consequence
verification independence vector
blocker/refusal/dispute
correction/retraction/dependency invalidation
authority assignment/grant/reservation/use
data-use and publication decisions
effect/reconciliation/exact-visible settlement
ledger/checkpoint/profile identity
```

The namespace is versioned. An unknown required Odeya term makes the package semantically unsupported; a reader may still inspect generic metadata but cannot claim an Odeya-equivalent interpretation.

## RO-Crate package shape

The root data entity names:

- package/profile version and exact Odeya export profile;
- title, bounded description, license/disclosure state, creators/contributors/funders/conflicts where authorized;
- publication manifest and exact visible-settlement reference for a public crate, or explicit private/non-public status;
- source checkpoint and export manifest digest;
- constituent protocol, workflow/run, data/artifact, method, result, claim, verification, limitation, and correction entities;
- unavailable/withheld external references without fabricating included bytes;
- current correction/retraction/withdrawal endpoint; and
- package byte inventory with media type, size, digest, logical role, and rights decision.

Large or restricted evidence may be referenced rather than embedded only when the package states availability, access conditions, integrity identity, and resulting reproducibility limitation. A digest is not a substitute for access.

Workflow Run RO-Crate may express run topology and execution metadata after compatibility testing. It does not replace Odeya's protocol freeze, command receipt, event, attempt, authority, validity, or claim semantics.

## Claim-centered export

For every exported claim version, the package must allow a reviewer to traverse:

```text
claim version
  -> adjudication and frozen consequence rule
  -> verification packages and independence
  -> metric/falsifier/measurement results
  -> run/protocol/method/environment identities
  -> exact artifacts and transformations
  -> source/data role, rights, and exposure
  -> producing principals/activities and resources
  -> corrections, invalidations, and publication state
```

An incomplete traversal is allowed only when the missing/withheld/unavailable edge is explicit and the claim/export eligibility rule permits it. The exporter cannot repair a missing lineage edge by generating prose.

## Orthogonal status export

The package retains separate values for:

- operation/interruption/blocker;
- scientific validity;
- measurement disposition;
- scientific adjudication;
- verification/dispute;
- replication;
- transport;
- claim eligibility/revision;
- rights/disclosure; and
- publication/effect/visibility.

External consumers that support only one status receive a conservative display summary plus the complete Odeya axes. The lossy summary is never imported as canonical state.

## Rights, privacy, and sealed truth

Export selection occurs only after a disclosure-specific DataUseDecision over the exact final object/field/attachment set, audience, purpose, channel, region, and retention behavior.

The package cannot include or indirectly disclose:

- sealed evaluator truth outside the recipient scope;
- private mission existence through predictable identifiers or graph gaps;
- contributor identity or personal data outside the accepted basis;
- hidden chain-of-thought or reusable credentials;
- restricted bytes through thumbnails, embeddings, indexes, logs, error text, archive metadata, or checksums where the checksum itself is restricted; or
- a limitation removed solely because its supporting evidence is withheld.

Redaction emits exact transformation provenance and preserves the limitations necessary to interpret every retained result.

## Deterministic export

Given one exact object set, checkpoint, profile, policy decision, and exporter build, the semantic graph and file inventory must reproduce byte-for-byte except fields explicitly declared externally assigned. Externally assigned identifiers such as a DOI are later observations and create a new package version rather than mutating the sealed package.

The crate ZIP/tar container, if used, follows a pinned archive profile covering path encoding/order, timestamps, permissions, owners, compression, links, devices, duplicate paths, traversal, and size limits. Archive bytes and logical crate graph each have distinct identities.

## Adversarial vectors

Gate A requires at least:

1. supported claim missing its contradicting evidence edge;
2. interval crossing zero exported as a null/equivalence result;
3. invalid run represented only as a failed execution;
4. blocker or missing measurement coerced to a scientific outcome;
5. verifier association treated as sufficient independence;
6. PROV association treated as an executable grant;
7. public crate without exact-visible publication settlement;
8. corrected claim exported as current without correction edge;
9. withheld artifact presented as included/reproducible;
10. rights decision for analysis reused for disclosure;
11. two distinct canonical identities collapsed into one URL;
12. old reader ignores an unknown required Odeya term;
13. package self-import overwrites canonical history;
14. nondeterministic file order/timestamps alter bytes without declared profile change;
15. archive traversal/link/device/duplicate-path attack;
16. redaction removes a limitation or exposes sealed truth through derived metadata; and
17. DOI/venue acceptance imported as scientific validity.

## Gate A acceptance

This profile remains open until:

- an exact JSON-LD context and RO-Crate profile are frozen at immutable identities;
- every founding canonical object and edge has a tested mapping or explicit non-export rule;
- JSON-LD expansion/compaction and RO-Crate validation are pinned and tested across independent implementations;
- claim-centered completeness, correction, rights, redaction, archive, and old-reader vectors pass;
- the first-slice private package reproduces in a clean environment;
- a public fixture proves the complete noncircular publication chain without releasing anything;
- data-rights, scientific, provenance, and security reviewers close critical/high findings; and
- Daniel accepts the exact profile in the architecture candidate.

Passing a generic RO-Crate or PROV validator would prove only that generic structure. It cannot establish Odeya semantic completeness, lawful disclosure, scientific validity, or publication settlement.
