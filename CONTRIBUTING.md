# Contributing to Odeya

Odeya is an architecture-first repository: every byte here is a contract, a
proof, or a decision record, and the validator is the referee. Contributions
are welcome under one discipline — nothing merges that the repository cannot
verify about itself.

## Before you change anything

1. Read [README.md](README.md), the twelve engineering laws in
   [docs/SESSION_HANDOFF.md](docs/SESSION_HANDOFF.md), and
   [docs/PRE_IMPLEMENTATION_GATE.md](docs/PRE_IMPLEMENTATION_GATE.md).
2. Reproduce the checkpoint locally:

   ```bash
   python3 -m venv .venv-architecture
   .venv-architecture/bin/python -m pip install \
     --require-hashes --only-binary=:all: \
     --requirement tools/repository-release/requirements-architecture.lock
   .venv-architecture/bin/python scripts/validate.py
   ```

   A change is not reviewable until this command passes on your branch.

## The rules that will actually affect your patch

- **No same-ID mutation.** Changing any byte of a schema requires bumping its
  `$id`, appending a reissue row to the ledger with the predecessor retained,
  and repointing every consumer in the same change.
- **Every gate needs a known-bad proof.** A new check must ship with at least
  one adversarial fixture that fails when the check is disabled. Passing
  prose is not evidence.
- **Missing is never zero.** Do not collapse `unknown`, `blocked`, `null`,
  or `inconclusive` into defaults or deletions.
- **Decisions are recorded.** Substantive changes carry an ADR in
  `docs/decisions/` explaining context, decision, non-decisions, and
  consequences — write it for the reviewer who was not in the room.
- **Bounded claims only.** Never introduce the words "safe", "solved",
  "production-ready", or "state of the art" without a named scope,
  comparator, and retained evidence.

## What is out of scope for contributions

Runtime or engine implementation is blocked until Gate A is accepted by the
repository owner; pull requests adding executable engine code will be
declined regardless of quality. Architecture corrections, adversarial
fixtures that expose a gate that cannot fire, documentation accuracy fixes,
and formal-model strengthening are the highest-value contributions.

## Licensing

By contributing you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
