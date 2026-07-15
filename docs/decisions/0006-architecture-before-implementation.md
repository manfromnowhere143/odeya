# 0006: Freeze architecture before runtime implementation

- Status: Accepted
- Date: 2026-07-15
- Decider: Daniel Wahnich

## Context

Odeya's value depends on scientific and systems integrity. Premature runtime code would make accidental assumptions expensive, encourage the interface to outrun truth, and turn fashionable technology into architecture before mathematical semantics and authority are settled.

## Decision

Runtime, UI application, infrastructure, integration, and deployment implementation are blocked until `docs/PRE_IMPLEMENTATION_GATE.md` passes and the operator explicitly accepts the architecture baseline. Architecture work includes specifications, schemas, standards, mathematical definitions, evaluation design, threat models, and decision records.

## Consequences

- The current repository remains documentation and contract only.
- The first implementation authorization will be narrow and tied to a pinned proof-project replay.
- Unresolved but reversible details may remain only if their boundary, experiment, and migration path are accepted.
- Domain, branding, and investor tasks do not weaken or bypass the gate.
