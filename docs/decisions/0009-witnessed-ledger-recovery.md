# 0009: Witnessed ledger checkpoints and integrity-first recovery

- Status: Proposed
- Date: 2026-07-15
- Gate: G3/G4/G7; requires independent security review and operator acceptance

## Context

Per-stream hash links and database backups can detect some mutations and recover some failures, but neither detects every valid-looking suffix truncation or split view. A restored backup can also resurrect expired grants, revoked identities, deleted data, corrected claims, or already-dispatched effects unless current security facts fence it.

Odeya needs a product-neutral recovery meaning before choosing a database, object store, backup system, key service, or witness operator.

## Decision

Adopt the semantics in `docs/LEDGER_INTEGRITY_AND_RECOVERY.md`:

1. Canonical transactions remain the scientific linearization point; artifacts, workflow state, external systems, and projections have distinct recovery rules.
2. Versioned signed checkpoints commit to the ordered ledger, aggregate heads, receipts, active constitutional registries, promoted-artifact registry, and unresolved high-consequence sets.
3. Required independent witnesses retain checkpoint observations and consistency evidence outside ordinary application/database administration.
4. The leading interoperability candidate is an Odeya-private RFC 9943 SCITT profile with RFC 9942 receipts and a selected, tested verifiable-data-structure profile. This is not accepted until privacy, VDS, issuer, registration-policy, witness, and proof vectors are frozen.
5. Recovery begins isolated/read-only, restores constitutional roots before interpreting domain state, applies the latest independently witnessed revocation/deletion/correction frontier, verifies semantic invariants, and reopens effects in bounded stages.
6. A fork, missing artifact, ambiguous effect, or unproven current-policy frontier blocks the affected scope. Recovery never merges histories or recreates evidence under an old identity.

This decision freezes integrity semantics and the standards direction, not a transparency service, cloud topology, key product, or claimed RPO/RTO conformance.

## Consequences

- A locally committed receipt and an externally witnessed checkpoint expose different assurance levels.
- Private payloads remain private; witnesses receive bounded signed commitments and approved metadata.
- Backup completion, backup verification, and clean-room recoverability are separate facts.
- Recovery can deliberately remain unavailable when continuity or current authority cannot be proven.
- Product selection must demonstrate restore-resurrection, split-view, missing-object, key, and ambiguous-effect drills.
- Transparency proves registration/consistency within its assumptions, not scientific truth.

## Rejected alternatives

- **Per-mission hash chains only:** cannot by themselves reveal every truncated suffix or equivocation.
- **Database replication as non-equivocation:** replicas under one administrative/failure domain can share rollback or compromise.
- **Publicly logging private events:** violates data minimization and rights boundaries.
- **Backup timestamp as canonical branch choice:** clocks do not prove completeness or authority.
- **Last-write-wins ledger merge:** destroys causal and authority meaning.
- **Restore then reconcile later:** can dispatch stale grants or expose deleted data before the mismatch is found.
- **Custom, unreviewed Merkle/receipt cryptography:** creates avoidable proof ambiguity and implementation risk.

## Falsifiers and acceptance evidence

Keep this ADR `Proposed` if the checkpoint leaf framing/ordering/domain separation is unfrozen, a witness shares effective control with the primary failure domain where independence is required, restored permissions can activate before the current frontier is proven, or a valid-looking fork can be chosen without a retained constitutional recovery decision.

Acceptance requires checkpoint/receipt/backup/restore schemas, exact conformance vectors, adversarial recovery traces, independent security and cryptographic-protocol review, first-slice data classification, and explicit operator acceptance. Product conformance requires an authorized clean-room Gate B restore drill.
