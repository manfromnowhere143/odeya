# Repository release policy mutations

These fixtures mutate one known-good architecture workflow in memory. Every mutation must be refused by the standard-library release checker before Actionlint or Zizmor runs.

The cases cover write permission expansion, trigger replacement and trigger
injection, explicit token plumbing, deployment environments, missing job
timeouts, persisted checkout credentials, shallow history, self-hosted
runners, undeclared job insertion, and removal of the default-deny
architecture-surface checker from the early Fast policy job. The exact
thirteen-case census and order are pinned by the standard-library release
checker. They are bounded regression controls, not a complete GitHub Actions
security proof.

The exact mutations are in [cases.json](cases.json).

Five release-contract mutations separately prove that the checker refuses a
return to the future-private-remote fiction, substitution of the exact public
remote identity, publication to `main` without exact evidence, and a claim
that the local hook is server-side protection. The fifth appends a contradictory
private/no-remote claim without removing any required positive sentence, so
positive-phrase stuffing cannot pass. They mutate the current contract in
memory and must fail for the named boundary.

Three release-script isolation mutations prove that a rehearsal cannot return
to one shared mutable tool cache, cannot run the formal suite without binding
`TLA2TOOLS_JAR` to the jar it just digest-verified, and cannot make a standalone
release check use a shared default tool directory. Their census and full
mutation specifications are pinned. These are structural controls over exact
scripts; the fresh-clone rehearsal remains the execution proof.

`scripts/compare_rehearsal_manifests.py --self-test` rejects nine drift classes, including shared-invalid manifest contracts, duplicate/missing paths, and a retained-file hash mismatch, before any local/remote rehearsal comparison is trusted.
