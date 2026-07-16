# Repository Release Engineering

Status: architecture-only release candidate. This document defines how the private Odeya repository is prepared and verified; it does not authorize remote creation, push, visibility change, product deployment, or Gate A acceptance.

## Release objective

The repository must make one promise and keep it: a reviewer can clone an exact commit, understand what Odeya is and is not, reproduce every retained architecture check, inspect failures, and verify that no workflow receives authority it does not need.

The release surface therefore optimizes for truth, reviewability, and failure evidence—not badges, workflow count, or the appearance of production maturity.

## Required checks

| Check | Purpose | Retained evidence | Explicit non-claim |
| --- | --- | --- | --- |
| `Fast policy` | Run the standard-library repository policy and release-contract checks before expensive suites | Policy log and exact workflow inventory | Not a substitute for exhaustive validation |
| `Foundation` | Run the complete integrated structural and bounded-semantic validator | Validator log and exact commit identity | Not Gate A acceptance or runtime evidence |
| `Schema contracts` | Validate all admitted schemas and every valid/adversarial schema fixture through the network-disabled registry | Exact schema and fixture counts | Not semantic or implementation conformance |
| `Semantic contracts` | Admit the safe semantic partition, then execute all eight complete paired contract harnesses | Profile inventory and per-suite output | Not proof beyond the retained bounded subjects |
| `Adversarial controls` | Admit the known-bad partition, then execute the same paired harnesses so negative controls cannot drift from their baselines | Profile inventory and expected-rejection output | Not an exhaustive threat proof |
| `Canonical identity` | Reconcile the two retained canonicalization implementations and verify the migration audit is current | Comparison receipt and audit check output | Not a frozen canonical profile; its blockers remain explicit |
| `Architecture evidence` | Reproduce Gate A prerequisite, schema-reissue, module-manifest, and first-slice evidence checks | Evidence-check logs | Not registry admission, activation, or an acceptance decision |
| `Repository / Release Surface` | Validate the README contract, action pins, least-privilege workflow shape, Dependabot scope, Markdown, Action syntax, and Mermaid rendering | Release-check log and rendered SVG | Not UI acceptance, deployment evidence, or a publication decision |
| `Architecture / Bounded Formal Models` | Reproduce seven safe TLA+ models, the alternate cognitive fingerprint run, and all thirty intended counterexamples | Full TLC log and pinned toolchain manifest | Bounded safety evidence only; not liveness, implementation conformance, or a physical safety case |

All checks run on pull requests, pushes to `main`, and manual dispatch. They use explicit timeouts, cancel superseded work, retain logs even on failure, and run with `contents: read` as the complete `GITHUB_TOKEN` permission set. They do not use `pull_request_target`, repository secrets, write permissions, deployment environments, cloud credentials, or self-hosted runners.

## Supply-chain boundary

- Every third-party GitHub Action is pinned to a full immutable commit SHA. Human-readable release versions remain beside the pins for review and Dependabot updates.
- Python architecture dependencies are exact and hash-locked for installation. The lock is generated from `requirements-architecture.txt`; the validator still checks the expected package versions at execution time.
- Node release-tool dependencies are exact in `package.json` and integrity-locked by `package-lock.json`. Installation disables lifecycle scripts; Mermaid uses an already installed browser.
- Actionlint is downloaded from one pinned upstream release, and the exact archive SHA-256 is selected by operating system and architecture before extraction.
- The TLA+ tools JAR is downloaded from the official pinned release and verified by SHA-256 before execution.
- Checkout fetches full history because the architecture evidence resolves predecessor Git objects. Workflow checkout credentials are not persisted.
- Gitleaks scans the complete commit history and the diagnostic artifact set with both ambient config variables removed and one exact tracked profile that extends the built-in defaults. The sole retained ignore is one exact founding-commit fingerprint for a reviewed synthetic session identity; broad path/rule suppression is forbidden. Zizmor likewise runs explicitly offline with all ambient/repository configuration disabled.
- CI artifacts are diagnostic evidence, not canonical scientific records. The repository commit and its retained architecture artifacts remain authoritative.

Hash locking establishes admitted bytes, not vulnerability absence. Dependabot tracks the pip, npm, and GitHub Actions manifests. `npm audit` is retained as a mutable advisory-freshness check whose answer may change without a repository-byte change; it is not part of canonical scientific identity. A Python advisory scanner is not yet admitted into the deterministic check because no pinned advisory snapshot/profile exists. Any remote release must enable plan-supported Dependabot security alerts, and an advisory update is reviewed as new evidence rather than silently rewriting a passed checkpoint.

GitHub artifact attestations, CodeQL upload, dependency review enforcement, secret scanning, and push protection are enabled only when the selected private-repository owner and plan support them and the relevant subject exists. They are not silently granted broader token permissions or represented as active before remote verification.

## Local release check

Run from a clean committed tree with Python 3.14.2, a Chrome/Chromium 150 executable, `curl`, `tar`, and Git. The check bootstraps digest-verified Node, ShellCheck, Actionlint, Zizmor, and Gitleaks binaries from freshly verified archives. Java 21.0.9 is required by the separate formal suite, not this release-surface check:

```bash
bash scripts/ci/check-repository-release.sh
```

The script writes diagnostics outside the upload path, scans and manifests the exact allowlist, then publishes the complete success directory through a same-filesystem rename. A failure publishes only an atomic minimal receipt; an interruption can leave a hidden staging directory, never a partially valid upload directory.

The script:

1. validates the release contract and immutable pins;
2. installs the exact Node toolchain with lifecycle scripts disabled;
3. audits the npm release-tool dependency graph and lints the release Markdown;
4. installs and runs pinned ShellCheck, Actionlint, and Zizmor binaries, with Zizmor deliberately offline and uncredentialed;
5. renders the exact Mermaid block from `README.md` through the bounded Chrome major; and
6. leaves only ignored diagnostic output under `artifacts/repository-release/`.

The complete architecture validator is separate:

```bash
.venv-architecture/bin/python scripts/validate.py
```

The complete bounded formal suite is also separate:

```bash
bash formal/tla/check.sh
```

## Fresh-clone rehearsal

A release candidate is rehearsed from one exact forty-character commit, never from a dirty worktree. The source and an evidence directory outside the disposable clone are explicit:

```bash
bash scripts/ci/rehearse-fresh-clone.sh \
  <expected-commit> \
  <credential-free-source-path-or-url> \
  <retained-evidence-directory> \
  [local|remote-main] \
  [approved-canonical-source-sha256]
```

The rehearsal performs a non-local clone from outside every repository into an isolated temporary directory, with system/global Git configuration, injected config parameters, repository/object/index/shallow/attribute routing variables, replacement objects, custom SSH wrappers, and caller repository-discovery variables disabled for the complete process tree. Git/CURL trace destinations are removed so transport credentials and repository bytes cannot be emitted to an ambient file descriptor, file, or socket; ambient TLS overrides are removed and the clone command explicitly sets `http.sslVerify=true`; pagers are inert and terminal prompting is disabled. This prevents `url.*.insteadOf`, alternate object stores, an ambient worktree, or nested tools from substituting or leaking the approved source or history. Global HTTPS credential helpers are intentionally unavailable; private remote rehearsal uses an operator-controlled read-only SSH agent or explicit askpass transport. It verifies the exact non-shallow checkout (and, in `remote-main` mode, requires `refs/heads/main` to equal it), creates a fresh Python environment, installs the hash-locked architecture dependencies, runs the foundation and release-surface checks, scans the exact subject ancestry, fetches the pinned TLA+ JAR, runs the formal suite, rejects undeclared tracked, untracked, or ignored outputs, scans the retained evidence, and atomically renames a complete digest-manifested evidence directory outside the disposable clone. An interrupted copy never occupies the declared evidence destination. `remote-main` mode additionally requires the SHA-256 of the exact credential-free source string retained in the owner/repository approval; it cannot self-assert an arbitrary remote. Source credentials, query strings, and fragments are rejected rather than retained. “Credential-free source” means no credential material is accepted in the command argument or written into retained evidence.

Local and remote evidence are compared by invariant profile, not raw bytes:

```bash
python3 scripts/compare_rehearsal_manifests.py \
  --local <local-evidence-directory> \
  --remote <remote-main-evidence-directory> \
  --expected-remote-source-sha256 <approved-canonical-source-sha256> \
  --output <retained-comparison-receipt.json>
```

Before comparison, the comparator independently validates both manifest contracts, rejects duplicate JSON members, extra top-level members, duplicate/unsafe/missing paths, and symlinks, requires the exact nineteen-file inventory and all-passed dispositions, rehashes every retained file, and recursively verifies the nested repository-release manifest against its fourteen diagnostics. It then requires equality of subject commit, schema/artifact class, canonical-evidence boundary, pinned profile-file digests, pass dispositions, and relative evidence-path inventory. It separately requires the local/remote source roles, `remote main == subject commit`, and the remote source identity to equal the approved canonical-source digest. The local source identity, environment-bearing log bytes, file sizes, and per-file diagnostic digests may legitimately differ only after each side has independently verified them; those fields are named as noncompared in the receipt.

Passing locally does not predict every GitHub-hosted-runner or account-policy behavior. After the first authorized private push, the same commit must pass all remote checks before branch protection is treated as operational.

## Remote activation checklist

The canonical remote remains private by default. Define `CANDIDATE_COMMIT` as one immutable forty-character commit. The accepted Gate A candidate-manifest commit, independently reviewed repository-release commit, local and remote rehearsal subject, and commit pushed to `refs/heads/main` MUST all equal `CANDIDATE_COMMIT`. No descendant, rebase, editorial follow-up, or reconstructed tree may inherit acceptance implicitly.

No remote may be created and no byte may be pushed until every precondition below is retained:

1. Gate A has an accepted immutable candidate manifest, accountable review record, and Daniel’s exact-byte decision over `CANDIDATE_COMMIT`;
2. Daniel has approved the exact GitHub owner, repository name, `private` visibility, credential-free canonical clone URL, and SHA-256 of that exact URL string;
3. the repository-release surface is already part of `CANDIDATE_COMMIT`, has been independently reviewed in the applicable Gate A lanes, and contains no unrelated worktree bytes;
4. the complete local fresh-clone rehearsal—including foundation, release, and formal checks—passes on `CANDIDATE_COMMIT` and retains its evidence manifest;
5. a pinned full-history secret scan has no unresolved finding and produces only redacted evidence; and
6. the separate publication/operations review confirms that creating the private remote discloses no research artifact or identity outside the approved scope.

Any byte change after acceptance creates a new candidate. It requires a new manifest and change-impact determination, every affected review lane to re-review or explicitly carry forward under the bounded rules in `ARCHITECTURE_REVIEW_PROTOCOL.md`, and Daniel to issue a new exact-byte decision. This includes README, workflow, validator, and rendered-content changes.

Only then perform the one-time bootstrap:

1. verify the target does not already exist and record the authenticated account;
2. create one empty private repository at that exact owner/name with no generated README, license, or `.gitignore` and record its immutable repository identity;
3. configure available secret scanning, push protection, default workflow-token permissions, allowed-Action policy, and fork-run approval before accepting history;
4. push `CANDIDATE_COMMIT` directly to `refs/heads/main`; this is the sole bootstrap exception to the later pull-request rule;
5. require the observed job contexts `Fast policy`, `Foundation`, `Schema contracts`, `Semantic contracts`, `Adversarial controls`, `Canonical identity`, `Architecture evidence`, `Release surface`, and `Bounded formal models`, after confirming GitHub reports those exact contexts for `CANDIDATE_COMMIT`;
6. configure the `main` ruleset to require those checks, resolved conversations, linear history, and to block force-push, deletion, and bypass except an explicitly retained break-glass role;
7. enable Dependabot and all plan-supported security controls without granting workflow write authority;
8. clone the credential-free canonical GitHub URL in `remote-main` mode, require remote `main == CANDIDATE_COMMIT`, retain the redacted rehearsal evidence outside the clone, and produce a passing invariant-profile comparison receipt against the local rehearsal; and
9. require every later change to enter through a reviewed branch and pull request.

Repository release is not research publication. It does not authorize runtime implementation, domain purchase, investor outreach, external data disclosure, paid compute, or any mission-level external effect.

## Future Odeya automation

A future worker may generate code, documentation, tests, or CI configuration as candidate artifacts inside an exact `WorkContract`. A GitHub operation remains a typed `repository_write` external effect. The kernel must bind the exact repository, ref, commit/object set, visibility, authority, resource policy, idempotency key, and reconciliation method before dispatch. Workers do not receive repository credentials and cannot authorize their own push.

Automatic execution means an already authorized dispatcher can perform one bounded effect and retain its dispatch receipt. Canonical completion still requires an independent observation that classifies the effect as applied, not applied, or unknown and closes any required reconciliation. It never means automatic authority, automatic publication, or an unrestricted repository per mission.
