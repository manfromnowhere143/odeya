# Security and Authority

Odeya will handle hostile documents, generated code, private data, expensive compute, and potentially high-consequence domains. Deterministic containment and authority are therefore part of the scientific method, not an infrastructure afterthought.

## Threat model

Assume that any of the following can be malicious, compromised, misleading, or simply wrong:

- contributed theses and attachments;
- webpages, papers, repositories, datasets, and citations;
- tool and MCP output;
- generated code, shell commands, packages, and containers;
- models, prompts, context packs, and persistent memory;
- graders and benchmark fixtures;
- worker hosts and third-party providers;
- insiders or stolen credentials.

Principal risks include prompt injection, data poisoning, exfiltration, dependency compromise, fabricated evidence, grader manipulation, unauthorized spend, publication leakage, sandbox escape, and accidental authority escalation.

## Deterministic boundary first

Model behavior is not the primary security boundary. Workers run inside deterministic containment with the minimum capabilities needed for one work item.

Trusted low-risk fixture worker requirements:

- ephemeral rootless container;
- non-root process and read-only base image;
- read-only inputs where possible;
- writable scratch volume with quota;
- default-deny network and audited allowlisted egress;
- no host filesystem, Docker socket, cloud metadata, or ambient credentials;
- CPU, memory, process, file, time, token, and spend limits;
- signed or pinned environment manifest;
- complete command and artifact audit;
- artifact quarantine before promotion.

Rootless containers do not establish sufficient isolation for arbitrary contributed or model-generated code. Use a threat-model-selected stronger tier—gVisor, Kata, sealed VM, or microVM—before such code is admitted. Every tier has escape and cross-tenant negative tests.

## Credentials outside the sandbox

Workers receive capability handles, not reusable secrets. A policy gateway injects or uses credentials outside the sandbox for one authorized request, then returns a sanitized response. Grants are mission-scoped, method-scoped, resource-scoped, expiring, revocable, and logged.

Raw secrets must never appear in prompts, logs, artifacts, model-visible environment variables, or research memory.

## Tool gateway

Every native or MCP tool registers:

- versioned input and output schemas;
- read, write, execute, spend, publish, or physical-effect class;
- external systems and data classes touched;
- deterministic and idempotency properties;
- resource and rate limits;
- approval policy;
- credential boundary;
- expected evidence and failure behavior;
- a negative-fixture suite.

Tool output re-enters the system as untrusted evidence. The gateway strips active content where possible, preserves raw bytes separately, and records exact provenance.

## Authority grants

An authority grant contains principal, mission, capability, resource, action, constraints, issue and expiry time, revocation reference, approval evidence, and single-use or replay semantics.

High-consequence actions should use dual control. No grant is inferred from a successful previous call, model confidence, elapsed time, or a missing human response.

At minimum, separately record:

- protocol freeze and amendment approval;
- data-rights and sensitive-data access;
- compute and spend approval;
- external write or message approval;
- safety approval;
- physical execution approval;
- truth and outcome settlement;
- public release and claim wording.

## Human decision assurance

Successful signature verification establishes only that exact bytes validate
under a referenced public key, algorithm, and trust profile; it does not
establish who caused the signing operation or controlled the private key.
Successful authentication establishes only the accepted authentication
ceremony. Neither establishes that a human reviewed, understood, or
substantively intended an application decision.

For every human-only consequential action, the future PRQ-013
`HumanDecisionAssurance` contract must bind a protected explicit ceremony to
the exact displayed and candidate bytes. It must retain a verifier- or
relying-party-generated unpredictable challenge, a separate human-initiated
confirmation gesture, user-presence and user-verification results, principal
identity-proofing and authenticator binding, authenticator/key/session custody
with unattended agent/model/tool exclusion, declared delegation, objections,
conflicts and effective quorum, replay and expiry controls, and sanitized
independently verifiable evidence. The resulting claim is bounded to ceremony
evidence attributable to the declared principal/authenticator under the named
profile; it never claims cognition or comprehension.

No current schema is claimed compliant. Gate A remains blocked on PRQ-013 as
specified by [ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
and the
[cross-program process-evidence packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md).

## Risk tiers

| Tier | Typical scope | Default posture |
|---|---|---|
| R0 | Public literature, no external writes | Sandboxed read, bounded network |
| R1 | Licensed/private data, local code execution | Explicit data grant, stronger logging |
| R2 | Material compute, paid APIs, external repositories | Spend and write gates, isolated workers |
| R3 | External operational systems or human-facing actions | Human approval per action, canary, rollback |
| R4 | Physical testbeds, critical infrastructure, frontier bio/chemical work | Domain safety case, dual control, independent oversight |

The founding engine has no general authority for R3 or R4 actions. Domain-specific programs must build and validate their own safety case.

## Data security and rights

- Classify data by sensitivity, rights, residency, retention, and allowed purpose before use.
- Keep tenant and mission boundaries enforceable in storage and retrieval.
- Encrypt sensitive data in transit and at rest with access auditing.
- Separate model-visible data from verifier-only truth and publication-visible projections.
- Support deletion or legal hold without destroying the integrity of permitted ledger records; store tombstone and reason where content must be removed.
- Do not train or improve shared systems on private mission data without explicit authority.

## Supply chain

- Pin source, package, image, model, and dataset identities.
- Generate software bills of materials and provenance attestations for release artifacts.
- Scan dependencies and images, but validate scanners with known-bad fixtures.
- Build in isolated CI with least-privilege tokens.
- Require reviewed changes for kernel, policy, verifier, schema, and publication code.
- Keep signing keys in managed key infrastructure, outside workers.
- Target SLSA 1.2 Build L2 and Source L2 for the initial release pipeline, with L3 planned for the kernel, verifier, and publication path.
- Use a pinned in-toto attestation profile and Sigstore bundle format, with an explicitly selected canonical SPDX or CycloneDX SBOM source.

Build provenance and research provenance are linked but never conflated. Signatures and attestations prove origin and integrity within their trust roots; independent execution remains necessary for scientific claims.

## Observability without leakage

Trace:

```text
mission -> cycle -> stage -> agent run -> model/tool call
```

Record latency, retries, token and resource use, model/tool/harness versions, policy decisions, egress destinations, artifact references, and errors. Redact secrets at source. Store sensitive prompt/output audit data separately with narrow access and retention.

The product must not expose hidden chain of thought. Inspectable plans, actions, evidence, decisions, and concise rationales provide accountability without relying on private reasoning.

## Incident response

The control plane must support pause, kill, lease revocation, credential revocation, egress shutdown, artifact quarantine, claim invalidation, and publication withdrawal. An incident record preserves:

- detection and timeline;
- affected missions, artifacts, claims, and releases;
- containment actions and authority;
- evidence retained;
- root cause and uncertainty;
- corrections and required re-verification;
- regression fixtures and policy changes.

An incident is not silently recategorized as a scientific null.
