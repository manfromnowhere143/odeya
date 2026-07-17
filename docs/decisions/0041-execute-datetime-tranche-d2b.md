# ADR 0041: Execute datetime tranche D2b and close class D2

- Status: Executed under ADR 0037's delegated acceptance; not Gate A acceptance
- Date: 2026-07-17
- Decision owners: canonical identity, architecture review, security
- Gate effect: pins ResearchEvent's twenty remaining datetime paths, reissuing
  it to 0.9.0 and lawfully reissuing eight consumers behind it; the audit's
  unprofiled-datetime count is zero across all one hundred twelve schemas

## Context

Tranche D2a deferred ResearchEvent because its identity is load-bearing: the
sixty-event identity map binds its exact bytes per event, the lifecycle
suite's guards pin its identity and version, and seventy-eight fixture files
carry its instances. That web deserved its own tranche, executed with the
collision-aware migrator and the closure engine D2a hardened.

## Decision

ResearchEvent reissued 0.8.0 to 0.9.0 with all twenty paths pinned to the
frozen UTC microsecond profile. The transitive closure then reissued the
eight consumers whose bytes the repoint changed — the legacy work-contract,
the profile-bound candidates, the exact-reference candidate, and the three
evidence schemas — each collision-aware, each ledgered against the
checkpoint, each with its self-declared version aligned to its new identity.
The closure is now a reusable engine: exact full-URN repoints only (never
family-based, after D2a's poisoning), the ledger repointed JSON-aware so
predecessor blocks are structurally unreachable, and the frozen
canonicalization vectors excluded entirely.

Instances followed their schemas: sixty-two research-event records across the
fixture corpus moved to 0.9.0 by marker-checked walk (so work-intent's
legitimate 0.8.0 identity was untouchable), the identity map rebound its
sixty-two byte-bindings, the embedded work-contract subject and its fixture
stayed byte-identical to each other, and two known-bad traps whose declared
guard text named the retired version followed the guard's live message.

## What the tranche caught

The convergence engine hit a genuine oscillator: a version const reached
through a cross-schema reference cannot be fixed by writing the referencing
file, and the engine looped forever flipping an in-memory copy. The fix was
semantic, not mechanical — the embedded subject record tracks the live legacy
schema, so the instance moved, not the schema. The engine's per-stage
instrumentation found it in one round.

## Non-decisions

This tranche does not decide any D3 through D9 class, does not admit a
member, and does not accept Gate A.

## Consequences

Class D2 of the accepted disposition partition is closed by measurement: the
audit reports two hundred seventy-three profiled datetime paths and zero
unprofiled, alongside D1's zero nonconformant fixture timestamps. The
remaining wave is D3 (127 decimal migrations), D4 (2 binary numbers), D5a
(668 digest scope annotations), D6 through D8 (55 divergent definitions), and
D9's eleven profile-binding pins, strictly last.
