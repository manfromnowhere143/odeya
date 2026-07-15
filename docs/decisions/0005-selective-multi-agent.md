# 0005: Central supervisor and selective parallel specialists

- Status: Accepted
- Date: 2026-07-15

## Context

Current research systems show gains from parallel search and specialist decomposition, with much higher inference cost and degraded behavior on sequential or tightly coupled work. Agent consensus is also correlated evidence, not independent verification.

## Decision

One durable supervisor owns the mission DAG. Launch parallel specialists only for independent branches such as literature breadth, competing hypotheses, candidate implementations, and adversarial search. One writer owns each mutable stage. Verification uses a separate execution identity and stronger evidence than debate.

## Consequences

- Every multi-agent configuration is evaluated against a comparable single-agent baseline and resource budget.
- Specialist roles are versioned capabilities, not permanent personalities.
- Debate and ranking prioritize work but never grant claim eligibility.
