# ADR 0045: Open-source packaging under the owner's publication decision

- Status: Executed on the owner's explicit instruction of 2026-07-17
- Date: 2026-07-17
- Decision owners: repository owner (publication), architecture review (content)
- Gate effect: adds the public-release surface — license, contribution
  contract, security policy, and a current public narrative — without
  granting any remote, runtime, or Gate A authority

## Context

The owner decided to open-source the Odeya architecture as the governing
core of an ecosystem whose proof missions — Sentinel, Telos, and Inbar —
are published or being published, so that external reviewers can verify the
entire research chain. The repository was already shaped for this: the
README leads with the system diagram and the boundary statement, the
validator reproduces the checkpoint from a fresh clone in one command, and
three CI workflows exist. What was missing was the legal and social surface
every serious open-source release carries.

## Decision

- License: Apache License 2.0, copyright the owner. Chosen for its patent
  grant and organizational acceptability; contributions are inbound=outbound
  under the same license via CONTRIBUTING.md.
- CONTRIBUTING.md states the disciplines that actually govern a patch here:
  reproduce the checkpoint first, no same-ID mutation, every gate ships a
  known-bad proof, decisions carry ADRs, claims stay bounded, and runtime
  contributions are declined until Gate A.
- SECURITY.md defines the security surface honestly: there is no runtime;
  the valuable report is a demonstration that a green check coexists with a
  broken invariant, the class of finding that produced ADRs 0024, 0030, and
  0033.
- The README's stale narrative sections were brought current with the
  executing migration wave while preserving every machine-checked string:
  the boundary sentence, the gate references, the provisional domain, and
  the single checkpoint sentence whose six counts the validator measures.
- Authorship standard: every commit in this repository is authored and
  committed by the owner's identity with no tool attribution, matching the
  Sentinel and Telos publication standard.

## Non-decisions

No remote is created and nothing is pushed: the repository's release law
still requires the owner's explicit owner/name/visibility values, which are
never inferred. The "Mission soul" section of the session handoff carries a
personal dedication whose publication is the owner's separate, deliberate
choice. Gate A, runtime authority, and external effects remain blocked.

## Consequences

The repository is publish-ready: a reviewer who clones it finds the story,
the license, the contribution contract, the security posture, a one-command
verification, and a decision trail from ADR 0001 to this one. Publication
itself is a single push once the owner names the destination.
