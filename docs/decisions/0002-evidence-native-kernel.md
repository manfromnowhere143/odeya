# 0002: Make typed evidence and durable state the kernel

- Status: Accepted
- Date: 2026-07-15

## Context

Long-context agents lose state, internal graders can be reward-hacked, signatures do not establish semantic truth, and corrections can drift across product surfaces. The proof projects repeatedly require preregistration, exact lineage, external verification, and explicit null or invalid outcomes.

## Decision

The authoritative system is a deterministic transition kernel over one canonical mission contract, immutable protocol versions, append-only events, content-addressed artifacts, claim-evidence edges, and separate authority records. Model context, summaries, embeddings, and UI are derived projections.

## Consequences

- Agents propose commands and artifacts but cannot directly mutate canonical state.
- Every claim traverses to exact evidence and verifier identity.
- Hashes and signatures protect integrity; independent recomputation establishes scientific validity.
- Corrections append and propagate rather than overwrite history.
