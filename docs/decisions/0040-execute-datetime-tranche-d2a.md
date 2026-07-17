# ADR 0040: Execute datetime tranche D2a with full transitive closure

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: pins 102 of the 122 unprofiled datetime paths to the frozen UTC
  microsecond lexical profile, reissuing forty-five schemas and — through the
  no-same-ID-mutation law's transitive closure — fifty-nine resources in total;
  defers ResearchEvent's twenty paths to tranche D2b

## Context

The accepted D2 disposition pins every `format: date-time` node to the exact
pattern the canonicalization profile freezes. Forty-five schemas outside
ResearchEvent carried such paths. ResearchEvent's own twenty are deferred:
its identity is load-bearing in the sixty-event identity map, the lifecycle
suite's constants, and the event fixtures, and that web deserves its own
recorded tranche.

## Decision

Each affected schema was reissued at the same path with a bumped version under
the ledger's precedent: predecessor retained as a git object at the tranche's
checkpoint commit, ledger row appended, every consumer of the retired identity
repointed in the same tranche. The lineage validator then proved what the plan
had not priced in: repointing a reference changes the consumer's bytes, so
consumers holding versioned identities must themselves reissue. Following that
law to its fixed point took two closure waves and reissued fifty-nine
resources in total — ResearchEvent lawfully moved to 0.8.0 without any of its
datetime paths changing, and the sixty-event identity map rebound to its exact
new bytes.

The work-identity family's suites migrated to post-wave semantics rather than
being loosened: an immutable predecessor now verifies against the raw bytes at
its own recorded commit, never against a live file; a resource born after the
ledger checkpoint tracks succession in `new_schema_candidates`; the semantic
core stays identity-free with its version compared outside the semantic
projection; and the executed reissue order replaced the planned one in both
evidence and expectation.

## What the tranche caught

Three instrument failures, each found by a gate rather than by reading:

1. The migrator's first run forged duplicate `$id` values onto versions the
   side-by-side successors already occupied. A positional alignment against
   the predecessor commit's identities recovered the two poisoned families,
   and the migrator gained a collision-aware version picker.
2. Family-name repoints contaminated historical records — ledger predecessor
   identities, the identity suite's expected reissue order, frozen
   canonicalization vectors, the first-slice retention block. Each was
   restored from its recorded commit, never re-derived from live state.
3. The convergence engine twice rebound historical subtrees to live bytes,
   erasing exactly the history it existed to preserve. It now refuses to
   descend into predecessor and retention blocks.

Two known-bad traps whose wrong values the reissue made right were repointed
to permanently wrong values; the ADR 0024 binding — every gate must have a
known-bad proof — caught both drifts itself.

## Non-decisions

This tranche does not pin ResearchEvent's datetime paths, does not decide any
D3 through D9 class, does not admit a member, and does not accept Gate A.

## Consequences

The audit's unprofiled-datetime count outside ResearchEvent is zero. The
remaining wave tranches inherit a ledger whose fifty-nine rows all verify
against their recorded commits, a collision-aware migrator, and a convergence
engine that can no longer eat history. Guard coverage re-measured at 111 of
160 statement-reachability proofs.
