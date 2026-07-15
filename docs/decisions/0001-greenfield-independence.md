# 0001: Build a greenfield independent engine

- Status: Accepted
- Date: 2026-07-15

## Context

Aweb and Maestro contain useful operational patterns, while Sentinel, Telos, and Inbar contain research requirements and evidence. They also carry product-specific routes, schemas, credentials, names, assumptions, and active work. Maestro's committed research trial does not establish a working research runtime.

## Decision

Odeya owns its runtime, storage, namespace, control, authority, evaluation, and release decisions. It studies and reimplements proven patterns through provider-neutral ports. Proof projects connect later through read-only or explicitly governed mission adapters; their codebases are not merged.

## Consequences

- No Aweb database, provider registry, route, credential boundary, or automatic approval behavior enters the core.
- Maestro is a protocol/reference surface, not Odeya's kernel.
- Duplicate implementation cost is accepted where independence preserves scientific or company authority.
