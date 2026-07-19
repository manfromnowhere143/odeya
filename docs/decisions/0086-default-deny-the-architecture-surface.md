# ADR 0086: Default-deny the architecture-only repository surface

- Status: Executed; implementation lock repaired
- Date: 2026-07-19
- Decision owners: architecture review, repository release
- Gate effect: the pre-implementation lock changes from five forbidden
  directory names to a fail-closed repository-surface policy with retained
  exact-refusal probes

## The defect

The foundation validator said `implementation lock intact` after checking only
that `apps/`, `packages/`, `services/`, `infrastructure/`, and `deploy/` did
not exist. Product code under `src/`, `engine/`, `lib/`, a top-level
executable, or an allowed root such as `scripts/` passed that lock. A symlink,
executable mode, or binary renamed as architecture data also passed. The green
sentence therefore claimed a boundary the checker did not enforce.

## Decision

`architecture/architecture-surface-policy.json` is a default-deny inventory
contract. It names the only top-level files and directories, file suffixes by
root, extensionless exceptions, executable-capable code paths, and paths
allowed to carry executable bits. `scripts/validate_architecture_surface.py`
checks that policy before the foundation validator may print the lock claim.

The checker inspects tracked, staged, and nonignored untracked candidate paths
when Git is present and walks a clean exported tree when it is not. Staged
regular-file prefixes are read from their exact Git blobs and checked
separately from worktree bytes, so a benign or absent worktree copy cannot
hide staged executable content. It also examines direct top-level entries so
an empty or ignored `src/`, `engine/`, or `lib/` cannot hide behind Git's
file-only inventory. Index and worktree modes are both considered; Git mode
`160000` and every mode outside regular `100644`/`100755` are refused.

The refusal order is deliberate:

1. symlink or special-file type;
2. top-level admission;
3. embedded executable suffix;
4. executable-capable code-path admission;
5. root-specific file type;
6. executable-bit admission; and
7. bounded executable content signatures.

One bad entry therefore produces one intended implementation-lock refusal
rather than a pile of incidental errors.

## Retained proof

`tests/architecture-surface/cases.json` retains five safe controls and fourteen
known-bad probes. The known-bads cover `src/`, `engine/`, `lib/`, an arbitrary
top-level file, code under `docs/` and unapproved code under `scripts/`, a
double-extension disguise, an unknown archive type, an executable bit on a
document, a symlink, staged executable content behind a benign worktree view,
a submodule gitlink, a shebang disguised as Markdown, and ELF bytes disguised
as JSON. Each case pins the complete expected error, and the self-test requires
the observed list to equal that one-element list. The checker also pins the
exact safe and known-bad case-ID inventories so silent case deletion is a gate
failure.

The policy also exact-lists every current Python, shell, Node, workflow, hook,
and TLA+ path so the existing architecture validators, release tooling,
canonicalization comparators, and bounded formal models remain available.

## Maintenance consequence

Adding a validator, formal model, workflow, or other executable-capable
architecture tool now requires an explicit policy edit. This friction is
intentional: without it, `scripts/runtime.py` is indistinguishable from a new
architecture checker by repository shape alone. Ordinary Markdown, schema,
fixture, and architecture-record additions remain admitted by their root and
suffix.

The allowlist is a governed artifact, not an immutable external oracle. An
author can still weaken the checker, policy, and cases together; review and
exact-commit rehearsal remain necessary. Workspace-only ignored environments
and generated output are outside repository-byte evidence. Content detection
is bounded to executable suffixes, shebangs, and common binary magic; this is
not a proof that every allowed text file is semantically non-executable.
Nothing here authorizes product code, accepts Gate A, or proves runtime safety.
