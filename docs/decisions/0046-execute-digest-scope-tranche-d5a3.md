# ADR 0046: Execute digest-scope tranche D5a-3 — the mixed digest family

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: annotates 281 occurrences of the mixed `digest`,
  `manifest_digest`, and `root_digest` family; the audit's unscoped-digest
  count falls from 326 to 45

## Context

The generic `digest` field is the one name spanning byte and canonical
digests inside shared reference definitions, 275 occurrences across 98
schemas. The accepted table dictated a four-way split; execution classified
each occurrence by its containing reference family, since the families —
not the occurrences — carry the semantics.

## Decision

- Artifact, profile, backup, and observation-profile reference families are
  byte digests over exact retained bytes, as are candidate references under
  the bootstrap raw-bytes identity law and dataset content digests.
- Event reference families bind the research-event domain; checkpoint
  references bind the ledger-checkpoint domain; typed record references
  whose subject class is declared or reserved bind that domain
  (estimand-contract, protocol-snapshot, run-manifest, work-contract,
  command-contract-record and registry, physical records, policy decisions,
  restore-verification-report, recovery-decision, reference-set-manifest,
  validation-rule-registry, admission-evidence-bundle).
- Generic reference families — immutable, versioned, record,
  canonical-record, versioned-identity, typed-record, schema-bound,
  subject — carry the target-resolved annotation: the sibling reference
  identity determines the domain at each use, and the annotation says so
  rather than inventing one.
- Twenty-two singleton occurrences were triaged individually; nineteen were
  annotated by the same rules, and three are deferred by design: the ledger
  checkpoint's set commitment belongs to the frontier/commitment
  construction decision, and the module-dependency and data-asset collection
  manifests have no accepted domain reservation, so annotating them would
  invent registry entries the acceptance never granted.

## Non-decisions

The remaining 45 unscoped occurrences are exactly the deferred families:
the eighteen needs-operator rows (frontier, state-root, digest-list,
commitment, and undecided-representation subjects) plus the three deferred
singletons and their kin. They await the one construction decision and its
registrations, recorded in their own tranche. No member is admitted and
Gate A is not accepted.

## Consequences

623 of 668 digest occurrences now carry accepted scope annotations. The
reissue closure lawfully moved 108 resources behind the annotations and
seven more schemas entered the ledger. D5a is complete except for the
construction-decision families; after that decision, D6-D8 and the D9 pins
are all that separate the audit from zero.
