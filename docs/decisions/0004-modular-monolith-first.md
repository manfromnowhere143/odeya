# 0004: Modular monolith plus isolated workers first

- Status: Accepted
- Date: 2026-07-15

## Context

Odeya needs transactional scientific invariants, durable orchestration, untrusted execution, and independent verification. Premature microservices or infrastructure can obscure those invariants before a vertical slice proves them.

## Decision

Start with a modular control plane backed by PostgreSQL, content-addressed object storage, and a commodity durable workflow substrate. Run generation and verification in separately isolated worker processes. Preserve strict module ports so measured needs can split services later.

## Consequences

- The first implementation avoids Kubernetes, a graph database, many microservices, and prestige rendering without measured need.
- Workers remain a hard isolation boundary even while control-plane modules deploy together.
- Vendor choices remain replaceable beneath Odeya-owned scientific contracts.
