# Repository release policy mutations

These fixtures mutate one known-good architecture workflow in memory. Every mutation must be refused by the standard-library release checker before Actionlint or Zizmor runs.

The cases cover write permission expansion, trigger replacement and trigger injection, explicit token plumbing, deployment environments, missing job timeouts, persisted checkout credentials, shallow history, self-hosted runners, and undeclared job insertion. They are bounded regression controls, not a complete GitHub Actions security proof.

The exact mutations are in [cases.json](cases.json).

`scripts/compare_rehearsal_manifests.py --self-test` rejects nine drift classes, including shared-invalid manifest contracts, duplicate/missing paths, and a retained-file hash mismatch, before any local/remote rehearsal comparison is trusted.
