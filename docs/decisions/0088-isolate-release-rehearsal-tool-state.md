# ADR 0088: Isolate release-rehearsal tool state

- Status: Executed as a repository-release evidence correction
- Date: 2026-07-19
- Decision owners: repository release, architecture review
- Gate effect: removes shared mutable tool-installation state from exact
  rehearsals and binds the formal run to the jar verified by that rehearsal;
  grants no runtime, publication, or Gate A authority

## The defect

Four exact-commit rehearsals were started concurrently. Their architecture,
mutation, and release-contract stages passed, but two release-surface stages
failed while installing Node: every installer defaulted to one
`$TMPDIR/odeya-release-tools` tree and replaced the same versioned install
directory. One process could remove another process's executable between its
install and version check.

The same review found a second path defect. The rehearsal downloaded and
digest-verified TLA+ tools below `$TMPDIR`, while `formal/tla/check.sh` defaulted
to `/tmp/odeya-tla/...`; the formal run could therefore consume a pre-existing
digest-valid jar instead of the file that the current rehearsal had fetched.
The digest boundary still fired, but the claimed download-to-execution binding
did not exist.

## Decision

1. Every fresh-clone rehearsal exports `ODEYA_TOOL_CACHE` below its unique
   `REHEARSAL_ROOT`. All release-tool installers in that process use that root.
2. A standalone `check-repository-release.sh` allocates and later destroys one
   unique tool cache unless its caller explicitly supplies an isolated cache.
3. The rehearsal downloads the TLA+ jar below its unique root, verifies the
   pinned SHA-256, exports that exact path as `TLA2TOOLS_JAR`, and only then
   invokes the formal suite.
4. Failed parallel-run receipts are retained as negative operational evidence;
   they are not converted into passing manifests or silently overwritten.

## Retained proof

The standard-library release validator pins three exact known-bad mutations:

- replace the per-rehearsal cache with the former shared default;
- remove the binding from the verified TLA+ jar to the formal checker; and
- replace the standalone check's unique cache allocation with a shared path.

Each mutation must produce its named refusal. Exact fresh-clone execution,
including a digest check inside `formal/tla/check.sh`, remains the stronger
proof. These structural mutations do not prove every concurrent scheduler
interleaving or make arbitrary caller-provided cache paths safe.

## Consequences

Rehearsals may execute concurrently without sharing the mutable Node,
ShellCheck, Actionlint, Zizmor, Gitleaks, or TLA+ installation paths identified
in this incident. Each run downloads more data because isolation takes
precedence over cache reuse. A future shared cache would require immutable
content-addressed objects, atomic publication, locking, corruption recovery,
and its own adversarial evidence; a mutable version directory is not admitted.

This correction changes repository-release tooling only. It does not validate
scientific claims, accept the architecture, authorize product code, or make
the engine executable.
