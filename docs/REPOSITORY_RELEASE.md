# Repository Release Engineering

Status: active architecture-only publication contract for the existing public
repository `https://github.com/manfromnowhere143/odeya`. ADR 0047 granted and
exercised architecture-repository publication authority, and
[ADR 0087](decisions/0087-reconcile-public-repository-operational-contract.md)
reconciles that executed fact with this ongoing contract. This contract
governs later architecture commits; it does not authorize engine runtime,
product deployment, research publication, mission data, credentials, paid
compute, or Gate A acceptance.

[ADR 0088](decisions/0088-isolate-release-rehearsal-tool-state.md) binds each
fresh-clone rehearsal to its own mutable tool cache and exact verified TLA+
jar after a parallel rehearsal exposed shared-cache races.

[ADR 0091](decisions/0091-exact-sha-two-ref-publication-sequence.md) accepts an
exact-SHA two-ref hardening: one locally rehearsed direct-child commit must
first pass the complete push check set at `release/<sha>`, then fast-forward
`main` without changing SHA, pass a new post-main check set, and reproduce from
remote `main`. The repository owner authorized the bounded hardening operation
on 2026-07-19. The account bootstrap is observed: pull requests are disabled,
the exact inert merge and Actions policies are active, and the no-bypass
release and `main` rulesets are IDs `19178198` and `19178503`. Bootstrap
candidate `a25d026bd7233dfc452accc6087ded0bf015d7b4`, whose sole parent is
historical public `main` checkpoint
`56e8062334fb81bba955ba137be690e085d4c88e`, remains at its permanent release
ref with four workflows and ten jobs successful on attempt 1. Distinct sibling
candidate `f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e` subsequently completed
the first candidate-to-main activation: permanent release checks, same-SHA
promotion, new post-main checks, remote replay/comparison, and the final
read-only activation receipt all settled for that exact subject. Every later
candidate must execute the ordinary two-ref sequence with new subject-bound
evidence.

## Release objective

The repository must make one promise and keep it: a reviewer can clone an exact commit, understand what Odeya is and is not, reproduce every retained architecture check, inspect failures, and verify that no workflow receives authority it does not need.

The release surface therefore optimizes for truth, reviewability, and failure evidence—not badges, workflow count, or the appearance of production maturity.

The [cross-program process-evidence
packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md) supplies
provenance-bound process observations only. It does not extend release
authority. In particular, a valid sibling/source file, local session record, or
historical pointer cannot substitute for the exact member and current subject
named by a release manifest.

## Required checks

| Check | Purpose | Retained evidence | Explicit non-claim |
| --- | --- | --- | --- |
| `Fast policy` | Run the default-deny architecture-surface policy and release-contract checks before expensive suites | Policy log, exact workflow inventory, and retained implementation-surface known-bads | Not a substitute for exhaustive validation |
| `Foundation` | Run the complete integrated structural and bounded-semantic validator | Validator log and exact commit identity | Not Gate A acceptance or runtime evidence |
| `Schema contracts` | Validate all admitted schemas and every valid/adversarial schema fixture through the network-disabled registry | Exact schema and fixture counts | Not semantic or implementation conformance |
| `Semantic contracts` | Admit the safe semantic partition, then execute all eight complete paired contract harnesses | Profile inventory and per-suite output | Not proof beyond the retained bounded subjects |
| `Adversarial controls` | Admit the known-bad partition, then execute the same paired harnesses so negative controls cannot drift from their baselines | Profile inventory and expected-rejection output | Not an exhaustive threat proof |
| `Canonical identity` | Reconcile the two retained canonicalization implementations and verify the migration audit is current | Comparison receipt and audit check output | Not a frozen canonical profile; its blockers remain explicit |
| `Architecture evidence` | Reproduce six dedicated prerequisite/member checks: Gate A prerequisites, PRQ-009 order, schema reissue, module manifest, first-slice scope, and human-decision-assurance successor recomputation. `Foundation` separately runs the complete integrated eleven-check census, including lifecycle/suite guard and condition audits, schema-rule ablation, refusal attribution, and the human-decision-assurance successor check | Dedicated evidence log plus the integrated Foundation log and pinned safe/known-bad inventories | Not registry admission, activation, or an acceptance decision |
| `Repository / Release Surface` | Validate the README contract, action pins, least-privilege workflow shape, Dependabot scope, Markdown, Action syntax, and Mermaid rendering | Release-check log and rendered SVG | Not UI acceptance, deployment evidence, or a publication decision |
| `Architecture / Bounded Formal Models` | Reproduce seven safe TLA+ models, the alternate cognitive fingerprint run, and all thirty intended counterexamples | Full TLC log and pinned toolchain manifest | Bounded safety evidence only; not liveness, implementation conformance, or a physical safety case |
| `Publication sequence` | On a governed push, verify the exact checked-out SHA, ref, single-parent/direct-child range, and event before/after boundary | Exact push log and remote run identity | Not a summary of the other checks, an independent verifier, or publication authority by itself |

The release checker compares the dedicated six-command run body and the
integrated eleven-member Python tuple to exact inventories, pins the complete
dedicated job and integrated-validator bytes, and binds the one executable
consumption loop.
The exact inventory contains nineteen retained known-bad mutations:
each member is removed once, then an out-of-body seventh workflow step and a
post-assignment same-cardinality Python rebinding are separately refused. The
counts above therefore cannot remain green after executable inventory drift.

At the completed first-activation checkpoint, public `main` carried the
four-workflow/ten-job inventory at
`f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e`: the existing nine contexts plus
the push-only `Publication sequence` context. Resolve the current `main` tip
from Git; every later promoted SHA must pass the same fresh inventory. Pull
requests are disabled at repository level, so retained `pull_request` triggers
are dormant;
no pull-request run is release evidence. Every workflow uses explicit
timeouts, cancels superseded work within its declared concurrency boundary,
retains logs even on failure, and runs with `contents: read` as the complete
`GITHUB_TOKEN` permission set. The workflows do not use
`pull_request_target`, repository secrets, write permissions, deployment
environments, cloud credentials, or self-hosted runners.

## Supply-chain boundary

- Every third-party GitHub Action is pinned to a full immutable commit SHA. Human-readable release versions remain beside the pins for review and Dependabot updates.
- Python architecture dependencies are exact and hash-locked for installation. The lock is generated from `requirements-architecture.txt`; the validator still checks the expected package versions at execution time.
- Node release-tool dependencies are exact in `package.json` and integrity-locked by `package-lock.json`. Installation disables lifecycle scripts; Mermaid uses an already installed browser.
- Actionlint is downloaded from one pinned upstream release, and the exact archive SHA-256 is selected by operating system and architecture before extraction.
- The TLA+ tools JAR is downloaded from the official pinned release and verified by SHA-256 before execution.
- Checkout fetches full history because the architecture evidence resolves predecessor Git objects. Workflow checkout credentials are not persisted.
- Gitleaks scans the complete commit history and the diagnostic artifact set with both ambient config variables removed and one exact tracked profile that extends the built-in defaults. The sole retained ignore is one exact founding-commit fingerprint for a reviewed synthetic session identity; broad path/rule suppression is forbidden. Zizmor likewise runs explicitly offline with all ambient/repository configuration disabled.
- CI artifacts are diagnostic evidence, not canonical scientific records. The repository commit and its retained architecture artifacts remain authoritative.
- A check that validates a sibling/source artifact does not validate the shipped
  member. The exact manifest member must be independently located, rehashed,
  loaded, and checked; a bundled copy that omits a required refusal or boundary
  fails even when its source sibling passes.

Hash locking establishes admitted bytes, not vulnerability absence. Dependabot
tracks the pip, npm, and GitHub Actions manifests. `npm audit` is retained as a
mutable advisory-freshness check whose answer may change without a
repository-byte change; it is not part of canonical scientific identity. A
Python advisory scanner is not yet admitted into the deterministic check
because no pinned advisory snapshot/profile exists. As observed on 2026-07-19,
secret scanning and secret-scanning push protection are enabled on the public
remote, while Dependabot security updates are disabled. That disabled state is
an open repository-governance finding, not an inferred vulnerability or a
property of the checked-in bytes.

GitHub artifact attestations, CodeQL upload, dependency-review enforcement,
rulesets, and other account-side controls are represented as active only after
remote observation. They are never inferred from workflow files and are not
silently granted broader token permissions.

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
6. runs the publication-sequence, live-GitHub-verifier, and rehearsal-comparator
   known-bad self-tests; and
7. leaves only ignored diagnostic output under `artifacts/repository-release/`.

The publication-sequence self-test (sixteen refused update/event/environment
classes) and publication-helper self-test share one append to
`final-release-contract.log`. The helper checks first/later candidate creation
and resume, executes its validator under the readonly caller scope that once
triggered Bash dynamic-scope shadowing, and tests one exact attached source ref
plus detached, renamed, and wrong-SHA refusals. A three-state clean-worktree
test refuses both dirty and unobservable status. It also executes the real hook
protocol for missing, ref-mismatched, SHA-mismatched, and exact frozen source
bindings plus failed status, closing substitution between helper recheck and
Git ref resolution. The live GitHub verifier self-test appends a second record
after refusing ten check, sixteen governance, six retained receipt, six
API-identity/query, five disabled-PR-census, six CLI, five mutation-journal,
and nine final activation-observation mutations. The
disabled-PR census uses the still-readable Issues endpoint, filters its
pull-request markers, and refuses a saturated page rather than accepting a
possibly truncated zero. The comparator separately refuses nineteen evidence
and receipt mutations. This retention keeps the nested manifest at exactly
fourteen diagnostics and the top rehearsal manifest at exactly nineteen
retained files. Fresh rehearsals reissue the top manifest as schema `0.2.0`:
its twelve profile files add the fourth workflow to the eleven-file `0.1.0`
profile. The comparator accepts each version only with its exact profile
inventory and refuses a mixed-version comparison.

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

The rehearsal performs a non-local clone from outside every repository into an isolated temporary directory, with system/global Git configuration, injected config parameters, repository/object/index/shallow/attribute routing variables, replacement objects, custom SSH wrappers, and caller repository-discovery variables disabled for the complete process tree. Git/CURL trace destinations are removed so transport credentials and repository bytes cannot be emitted to an ambient file descriptor, file, or socket; ambient TLS overrides are removed and the clone command explicitly sets `http.sslVerify=true`; pagers are inert and terminal prompting is disabled. This prevents `url.*.insteadOf`, alternate object stores, an ambient worktree, or nested tools from substituting or leaking the approved source or history. Global HTTPS credential helpers are intentionally unavailable; private remote rehearsal uses an operator-controlled read-only SSH agent or explicit askpass transport. Each rehearsal allocates its mutable release-tool installations below its own temporary root, downloads the pinned TLA+ JAR into that root, and explicitly binds the formal checker to that verified file; concurrent rehearsals therefore do not delete or substitute one another's Node or formal-tool installation. A standalone release-surface check likewise allocates a unique cache unless its caller explicitly supplies an isolated `ODEYA_TOOL_CACHE`. It verifies the exact non-shallow checkout (and, in `remote-main` mode, requires `refs/heads/main` to equal it), creates a fresh Python environment, installs the hash-locked architecture dependencies, runs the foundation and release-surface checks, scans the exact subject ancestry, runs the formal suite, rejects undeclared tracked, untracked, or ignored outputs, scans the retained evidence, and atomically renames a complete digest-manifested evidence directory outside the disposable clone. An interrupted copy never occupies the declared evidence destination. `remote-main` mode additionally requires the SHA-256 of the exact credential-free source string retained in the owner/repository approval; it cannot self-assert an arbitrary remote. Source credentials, query strings, and fragments are rejected rather than retained. “Credential-free source” means no credential material is accepted in the command argument or written into retained evidence.

The rehearsal must execute validators against the exact copied/bundled members
named in its manifests, not against convenient source siblings. A required
known-bad self-test must keep the source sibling valid while deleting a required
boundary from the shipped member. That self-test remains pending; until it is
retained and fires, no release evidence may claim this exact-member substitution
class is closed.

Local and remote evidence are compared by invariant profile, not raw bytes:

```bash
python3 scripts/compare_rehearsal_manifests.py \
  --local <local-evidence-directory> \
  --remote <remote-main-evidence-directory> \
  --expected-remote-source-sha256 <approved-canonical-source-sha256> \
  --expected-subject-commit <exact-commit> \
  --output <retained-comparison-receipt.json>
```

Before comparison, the comparator independently validates both manifest
contracts, rejects duplicate JSON members, extra top-level members,
duplicate/unsafe/missing paths, symlinked evidence roots, members, receipts, or
configured evidence/receipt parents,
requires the exact nineteen-file inventory and all-passed dispositions,
rehashes every retained file, and recursively verifies the nested
repository-release manifest against its fourteen diagnostics. Top manifest
`0.1.0` requires the historical eleven-file profile; `0.2.0` requires the
twelve-file profile including `.github/workflows/publication-sequence.yml`. It
then requires equality of schema version, subject commit,
schema/artifact class, canonical-evidence boundary, pinned profile-file
digests, pass dispositions, and relative evidence-path inventory. It
separately requires the local/remote source roles,
`remote main == subject commit`, the remote source identity to equal the
approved canonical-source digest, and the shared subject to equal the
caller-supplied current commit. Receipt creation and `--verify-existing`
resumption use the same canonical builder; an existing receipt must equal a
fresh recomputation byte-for-field. The local source identity,
environment-bearing log bytes, file sizes, and per-file diagnostic digests may
legitimately differ only after each side has independently verified them;
those fields are named as noncompared in the receipt.

The latest completed public checkpoint replay at this decision boundary is
`56e8062334fb81bba955ba137be690e085d4c88e`. Its remote-main rehearsal
manifest has SHA-256
`0f8b80572c2761436c0afe06660ce47a357bf17e718aa781328a8ffeacb5a47b`.
The comparison receipt has SHA-256
`36046ac0bd2793f036024ac27b692b6e0884ca14a514e67dba879904abbd5cf2`
and status `verified_evidence_and_invariant_profile_equal`. This closes the
remote replay/comparison obligation for that exact historical checkpoint; it
does not activate ADR 0091 for a descendant.

The account/bootstrap checkpoint followed without moving `main`.
`a25d026bd7233dfc452accc6087ded0bf015d7b4` is a sole child of that base,
has tree `8bfb4859a29bb1a9606dae59c168c64438cb6660`, and is retained at
`refs/heads/release/a25d026bd7233dfc452accc6087ded0bf015d7b4`. Its local
rehearsal-manifest SHA-256 is
`722905919a9ca895152a941494e8c48b395f15fa5ff13046203eed5786fd7439`;
its candidate-governance and candidate-checks receipt SHA-256 values are
`518dd562d0a9be561e9d732d66778f2f034914980625a891e612e83ee2f49060`
and `e60cadf4823ef4a7f07123d47f68434f247ec53dab5dc89bf58d9fe1fac93652`.
All four runs and ten jobs completed successfully on attempt 1 under GitHub
Actions app ID `15368`. The closed eleven-operation mutation journal has
SHA-256
`00b9661b0e4a316099c56432b99df6a3526382539ee01d15fe9ebe43e2d55827`.
Those owner-held external files are digest-bound diagnostic evidence; they are
not canonical scientific evidence or Gate A authority.

For each new candidate `C`, the guarded helper also retains four exact,
subject-bound GitHub observations outside the repository:

- `github-candidate-governance-C.json` records the accepted repository,
  Actions, workflow-token, and immutable-candidate ruleset state immediately
  before candidate creation. The first bootstrap may have
  `ruleset_scope=candidate-bootstrap`; later candidates require `full`.
- `github-candidate-checks-C.json` records the four exact push runs and ten
  successful GitHub Actions jobs on `release/C`, including run, job, attempt,
  branch, SHA, conclusion, and GitHub Actions app identities.
- `github-promotion-governance-C.json` records the full two-ruleset,
  repository, and Actions read-back immediately before promotion, with
  `governance_phase=promotion`.
- `github-main-checks-C.json` records the separately created four runs and ten
  successful jobs on `main` after the same-SHA fast-forward.

Each receipt names `subject_commit=C`, is noncanonical diagnostic evidence,
uses a stable normalized schema, and is atomically retained. An existing
receipt is accepted only when it exactly equals a fresh accepted observation;
a changed receipt, a symlink in its path or parent, or a multiply linked
retained file refuses publication.
GitHub's detailed ruleset read-back may omit the false-valued parameters of
the candidate `update` rule. The verifier accepts only that omission or the
exact explicit `update_allows_fetch_and_merge=false`, rejects true or
additional parameters, and always normalizes the retained receipt to explicit
false.

The one-time ADR 0091 activation additionally retains an immutable mutation
journal and a fifth, final observation outside the repository:

- `github-governance-mutations-C1.json` binds the historical base and bootstrap
  candidate `C1` to the eleven exact REST exchanges: explanatory comment and
  close for each of pull requests 1 and 2; repository settings; the two-step
  Actions pinning/selection transition; selected-Action admission; workflow
  token policy; and creation of the release and `main` rulesets. Every entry
  retains the exact method, endpoint, parsed request body, canonical request
  SHA-256, expected HTTP status, response date, GitHub request ID, selected API
  version, response-body SHA-256, and response resource ID when one exists.
  Authorization and other credential-bearing headers are never retained.
- `github-activation-C2.json` is created only after the final same-SHA `main`
  checks and remote replay for the post-account-state candidate `C2`. It
  revalidates the mutation journal, the exact bootstrap and final candidate
  checks, the final pre-promotion governance receipt, the final `main` checks,
  and the remote-main comparison against both evidence directories; then it
  performs fresh read-only observations of both configured rulesets,
  repository and Actions policy, zero open pull requests, `main`, both
  permanent release refs, top-level branch protection, and the exact effective
  branch rules linked to the two journaled positive, distinct ruleset IDs.
  Those observations are REST GETs plus one fixed repository-policy GraphQL
  query transported by POST. The query is identity-bound to Odeya and the
  verifier rejects every GraphQL mutation or alternate query.

The final activation verifier never mutates GitHub. Ruleset creation is
non-idempotent: the mutating operator must persist request intent before each
POST and must never blindly retry if the `201` response was not durably
captured. A live ruleset that looks equal cannot reconstruct a lost historical
HTTP exchange; that outcome remains `applied_outcome_unknown` and blocks
activation. The journal and activation receipt are noncanonical diagnostic
evidence, not scientific evidence or self-approval.

The completed one-time activation promotion set
`ODEYA_ACTIVATION_BOOTSTRAP_SHA=C1` when invoking
`scripts/ci/push-rehearsed-head.sh promote`. The helper derived every exact
receipt/evidence path, ran `activation-evidence` after remote comparison and
final ref settlement, and printed the combined completion statement only after
the fifth receipt was retained. This is historical recovery information, not a
procedure to repeat. Every ordinary descendant must leave
`ODEYA_ACTIVATION_BOOTSTRAP_SHA` unset; the helper then completes ordinary
publication and states that no one-time GitHub activation claim was requested.

Local session logs may corroborate a bounded chronology of observed commands
and tool outcomes. They are mutable secondary evidence and never establish
authorship, human intent, accountable approval, reviewer independence, or
scientific validity. A structurally valid review or operator-decision artifact
is likewise insufficient for a human-only Gate A decision while PRQ-013 in
[ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md)
remains unresolved.

Passing locally does not predict every GitHub-hosted-runner or account-policy
behavior. The exact pushed commit must pass all remote checks before
publication is complete. A local hook is not server-side branch protection.

## Ongoing public-architecture publication checklist

The public canonical remote already exists at
`https://github.com/manfromnowhere143/odeya`; its default branch is `main`.
Define `CANDIDATE_COMMIT` as one immutable forty-character architecture commit.
Define `BASE_COMMIT` as the freshly observed `refs/heads/main`, and define
`RELEASE_REF` as `refs/heads/release/CANDIDATE_COMMIT`. The local rehearsal
subject, publication-history audit subject, release-ref tip, checked commit,
remote `main`, remote rehearsal subject, and invariant-profile comparison
subject MUST all equal `CANDIDATE_COMMIT`. No descendant, rebase, editorial
follow-up, or reconstructed tree inherits evidence implicitly.

No architecture commit may be pushed to `main` until every precondition below
is retained:

1. the exact candidate worktree is clean and contains no protected concurrent
   lane or unrelated byte;
2. before `RELEASE_REF` is created, the retained local rehearsal, remote-main
   rehearsal, and comparison receipt for `BASE_COMMIT` revalidate as one exact
   completion triplet bound to the freshly observed current main. A valid
   historical triplet for another SHA is not the current baton;
3. `CANDIDATE_COMMIT` is exactly one ordinary single-parent commit whose sole
   parent is `BASE_COMMIT`; the range contains no other commit;
4. the complete local fresh-clone rehearsal—including foundation, release,
   formal, mutation, secret-scan, and output-audit stages—passes on
   `CANDIDATE_COMMIT` and retains its evidence manifest;
5. `scripts/ci/audit-publication-evidence.py` accepts the exact publication
   range and the candidate carries rehearsal evidence bound to its own SHA;
6. `core.hooksPath=.githooks` is configured in the publishing clone and
   `scripts/ci/push-rehearsed-head.sh` is the only push path;
7. every pre-existing open pull request has been closed; pull requests are
   disabled (`has_pull_requests=false`); merge commits and squash merges are
   disabled; and rebase merge remains enabled only as GitHub's inert
   prerequisite for `required_linear_history`. Auto-merge, automatic branch
   deletion, and update-branch suggestions are disabled. Actions admission
   requires full-SHA pins and the default workflow token is read-only without
   pull-request approval authority. With those settings read back, the active
   no-bypass `immutable publication candidates` ruleset must target
   `refs/heads/release/*`, restrict updates, and block deletion,
   non-fast-forward changes, and nonlinear history without a status rule.
   Creation is allowed, but every later ref update is refused;
8. `RELEASE_REF` is created once at exactly `CANDIDATE_COMMIT`, remains as
   permanent candidate evidence, is never rewritten, deleted, or recreated,
   and its push starts the four exact workflow families;
9. the newly created release-ref runs—not a historical run for another ref,
   event, SHA, or attempt—show the contexts `Fast policy`, `Foundation`,
   `Schema contracts`, `Semantic contracts`, `Adversarial controls`,
   `Canonical identity`, `Architecture evidence`, `Release surface`, and
   `Bounded formal models`, plus the push-only `Publication sequence`, all
   completed with conclusion `success` on `CANDIDATE_COMMIT`;
10. a live read-back shows the active no-bypass `main exact-SHA fast-forward`
   ruleset blocks deletion and non-fast-forward updates and requires those ten
   exact GitHub Actions contexts with strict current-base enforcement and
   server linear history;
11. immediately before promotion, the observed remote identities remain
   `refs/heads/main == BASE_COMMIT` and
   `RELEASE_REF == CANDIDATE_COMMIT`;
12. promotion is one ordinary same-SHA fast-forward from `BASE_COMMIT` to
    `CANDIDATE_COMMIT`; no pull-request merge is a publication path;
13. the four newly created post-main workflow runs and all ten jobs complete
    successfully on `CANDIDATE_COMMIT`, and remote `main` still equals it; and
14. a remote-main fresh-clone rehearsal requires
   `refs/heads/main == CANDIDATE_COMMIT` and produces a passing
   invariant-profile comparison receipt against the local rehearsal; and
15. the first activation cycle additionally validates the immutable mutation
   journal and bootstrap checks, re-reads zero open pull requests, both
   configured rulesets, exact effective rules and protected branch state, and
   retains `github-activation-C2.json`. The helper then re-reads both
   `main == CANDIDATE_COMMIT` and
   `RELEASE_REF == CANDIDATE_COMMIT` before it records `COMPLETE`.

Both rulesets require GitHub's `required_linear_history` rule. GitHub requires
at least one compatible pull-request merge method to remain enabled before it
will enable that server rule, so the exact repository configuration retains
`allow_rebase_merge=true` while disabling merge commits and squash merges.
That rebase setting is inert because the repository pull-request feature is
disabled (`has_pull_requests=false`). REST omits the merge-policy fields after
that transition, so the live verifier requires a second, exact GraphQL
readback bound to Odeya's node ID; it admits only the fixed query and maps its
booleans explicitly. REST still proves repository identity and PR disablement.
Any contradiction or drift on either surface is a refusal. Server linear
history refuses merge commits, while the push-only `Publication sequence`
context, hook, and guarded helper add the stronger exact
one-single-parent/direct-child proof. The latter remains a named
self-modifiable-verifier residue.

All pre-existing open pull requests must be closed before the pull-request
feature is disabled and activation evidence is captured. After account
bootstrap, there is no pull-request review, check, or merge path. A dormant
`pull_request` workflow trigger, a historical synthetic merge run, or
`gh pr merge` cannot satisfy or replace any publication step.

ADR 0091 and this checklist are requirements plus the bounded observations
recorded above. At the pre-change observation the fourth workflow did not exist
and no repository ruleset existed; the account/bootstrap checkpoint later
established both rulesets and retained the exact account journal plus
bootstrap candidate checks. Distinct final candidate
`f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e` later retained its candidate-ref
checks, same-SHA `main`, new post-main checks, remote replay, and final
`github_repository_activation_receipt`, completing the first activation
cycle. Those receipts bind only that exact subject; every descendant must
execute the ordinary sequence again.

The comparator's retained known-bad now presents a valid historical completion
triplet while the caller names a later current subject and requires rejection.
Only the freshly observed current-main subject can satisfy the predecessor
gate; historical evidence remains attributable to its own exact bytes.

Any byte change creates a new candidate and requires new exact-commit evidence.
Architecture publication does not require pretending Gate A has passed; it is
the separately authorized publication of architecture evidence. Gate A
acceptance, a Gate C implementation increment, research publication, and every
runtime or mission external effect remain separately operator-governed.

## Executed account bootstrap and completed first activation boundary

ADR 0047 records the one-time public repository bootstrap executed on
2026-07-17. It is
history, not a procedure to rerun. ADR 0091 account hardening was then applied
and read back on 2026-07-19 without moving public `main` from `56e8062`:

- pull requests 1 and 2 were explained and closed before
  `has_pull_requests=false` was applied;
- merge, squash, auto-merge, automatic branch deletion, and update-branch
  suggestions are false; rebase alone is true as GitHub's inert prerequisite
  for server linear history;
- Actions admit selected actions with full-SHA pinning required, GitHub-owned
  actions allowed, verified-creator admission false, no patterns, and a
  read-only workflow token without pull-request approval authority;
- `immutable publication candidates` is active with no bypass actors as
  ruleset ID `19178198`; and
- `main exact-SHA fast-forward` is active with no bypass actors as ruleset ID
  `19178503`, strict freshness, linear history, and the ten app-pinned
  contexts.

Bootstrap candidate `a25d026…` is permanently retained and its four
workflows/ten jobs are green on attempt 1. The eleven settled operations are
retained in
`github-governance-mutations-a25d026bd7233dfc452accc6087ded0bf015d7b4.json`.
This is active account-side control and bootstrap evidence. Distinct final
sibling candidate `f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e` then passed
release checks under both rulesets, fast-forwarded the same SHA to `main`,
passed four new post-main workflows and ten jobs, reproduced from remote
`main`, compared equal by the admitted profile, and emitted the final read-only
activation receipt. The comparison-receipt SHA-256 is
`442ab446a1fad1a62ec6049b978b2af53fa1b67ccbd6acebf34619ff540ea625`;
the activation-receipt SHA-256 is
`2f9564a23bf3bde851244224eb5f69b5cfe881e39eec46b1387d5a34b85a1ab2`.
A local hook remains a workstation control, not server-side branch protection;
the server rulesets are the independently observed remote barriers. This
completion does not transfer evidence to a descendant.

Repository release is not research publication. It does not authorize runtime
implementation, domain purchase, investor outreach, external data disclosure,
paid compute, or any mission-level external effect.

## Future Odeya automation

A future worker may generate code, documentation, tests, or CI configuration as candidate artifacts inside an exact `WorkContract`. A GitHub operation remains a typed `repository_write` external effect. The kernel must bind the exact repository, ref, commit/object set, visibility, authority, resource policy, idempotency key, and reconciliation method before dispatch. Workers do not receive repository credentials and cannot authorize their own push.

Automatic execution means an already authorized dispatcher can perform one bounded effect and retain its dispatch receipt. Canonical completion still requires an independent observation that classifies the effect as applied, not applied, or unknown and closes any required reconciliation. It never means automatic authority, automatic publication, or an unrestricted repository per mission.
