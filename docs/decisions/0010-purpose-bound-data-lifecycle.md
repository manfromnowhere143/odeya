# 0010: Purpose-bound data authority and dependency-aware deletion

- Status: Proposed
- Date: 2026-07-15
- Gate: G3/G4/G5/G8; requires accountable data-rights review and operator acceptance

## Context

Frontier research combines public sources, contributed material, repositories, private plans, model providers, sealed evaluation truth, derived indexes, and publication packages. A single `public/private` or `sensitive` flag cannot express whether one exact use is permitted. It also cannot make deletion, correction, contamination, provider copies, and scientific lineage agree.

## Decision

Adopt the data lifecycle in `docs/DATA_GOVERNANCE.md`:

1. Possession or reachability grants no data authority.
2. Every admitted asset or canonical collection has exact identity, lineage, scientific role, and an active `DataUseDecision` over purpose, operation, recipient, provider/model, region, time, retention, deletion, and disclosure.
3. Processing, verification, retrieval, training, support, and publication are separate purposes. Reuse requires a new decision.
4. Transformations, embeddings, summaries, joins, synthetic outputs, and inferred data become governed assets with their own identities and dependency edges; restrictions cannot be silently downgraded.
5. Exposure history is monotonic. Deletion cannot unexpose a human/model or restore evaluation independence.
6. Rights revocation or deletion blocks access at the canonical boundary and fans out through artifacts, indexes, claims, learning records, and publications. Missing evidence narrows, invalidates, corrects, or withdraws claims rather than being hidden.
7. Legal hold prevents only covered destruction; it grants no new processing or disclosure.
8. Provider, cache, replica, backup, export, and restore behavior are explicit parts of the lifecycle.

The contract is jurisdiction-neutral and deliberately conservative. A mission-specific profile and accountable rights review must narrow it; this ADR is not legal compliance evidence.

## Consequences

- Data admission has more work up front, and some scientifically useful material must be refused.
- Reproducibility claims narrow when evidence cannot lawfully be retained or disclosed.
- Derived indexes and model-improvement inputs cannot hide outside the deletion graph.
- Publication requires a fresh exact-byte rights decision even when private processing was allowed.
- A restored historical backup cannot reactivate deleted data or old permissions.
- Odeya can explain precisely which fact was removed, which non-content audit fact remains, and what changed scientifically.

## Rejected alternatives

- **One sensitivity label:** collapses purpose, rights, residency, recipient, and retention semantics.
- **Ingest now, classify later:** makes the initial acquisition/exposure potentially unauthorized.
- **Public URL means permitted:** confuses technical access with license, privacy, and purpose authority.
- **Provider setting means provider behavior is proven:** configuration is evidence, not assurance by itself.
- **Derived or synthetic means unrestricted:** transformations can preserve, amplify, or leak protected information.
- **Delete raw bytes but retain embeddings/caches/backups indefinitely:** leaves recoverable or behaviorally useful copies.
- **Preserve every scientific byte despite revocation:** treats research integrity as authority to violate rights.
- **Erase history of deletion/exposure:** enables resurrection and false independence claims.

## Falsifiers and acceptance evidence

Keep this ADR `Proposed` if a trace can use inference permission for training, publish an unlisted attachment, omit a derivative from deletion fanout, treat a hold as access, restore a stale grant, or keep a claim eligible after required evidence becomes unavailable without an accepted exception.

Acceptance requires the lifecycle schemas and semantic rules, a rights-cleared first fixture, provider/data profile, adversarial traces, accountable rights/security review, and explicit operator acceptance. Storage/provider deletion claims remain unproven until implementation-specific tests settle them.
