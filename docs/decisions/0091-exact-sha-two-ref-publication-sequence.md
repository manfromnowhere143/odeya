# ADR 0091: Promote one exact SHA through a two-ref publication sequence

- Status: Accepted for repository-release hardening; candidate implementation
  is present. Resolve exact-commit evidence from Git and external receipts;
  account activation remains `authorized, not active` until the final
  activation receipt exists
- Date: 2026-07-19
- Decision owners: repository owner (explicit hardening authority), repository
  release, architecture review
- Gate effect: requires one rehearsed direct-child commit to pass the exact
  remote check set on an immutable `release/<sha>` ref before the same SHA may
  fast-forward `main`; grants no runtime, deployment, scientific-publication,
  or Gate A authority

## The defect

At the pre-change checkpoint, the release contract correctly said that a push
was incomplete until the exact pushed commit was green, but its controls did
not enforce that sequence as one closed operation:

- the pre-push hook checked evidence for the pushed tip but did not prove that
  the update range contains exactly one commit, so a multi-commit fast-forward
  can carry unchecked intermediate commits;
- the guarded helper pushed the rehearsed tip directly to `main` and printed
  that remote checks still needed observation instead of waiting for and
  verifying them;
- the public remote had no server-side ruleset at the 2026-07-19 pre-change
  observation, so a fresh clone, `--no-verify`, or another caller could bypass
  every local publication control; and
- pull-request workflow metadata named the PR head while the default checkout
  executed GitHub's synthetic merge commit, so a green pull-request run did not
  prove that the exact candidate commit was executed.

These are measured control defects, not evidence that every historical commit
is wrong. The history nevertheless shows why the distinction matters. One
commit was pushed before its exact rehearsal completed after a formal-model
completion line was mistaken for the rehearsal's completion, and seven commits
were once left on public `main` with a red remote Foundation workflow while
their local rehearsals were green. ADRs 0072, 0074, and 0075 retain those
failures and corrections.

## Verified pre-change checkpoint

At the bounded observation used for this decision:

- public `main` resolved to
  `56e8062334fb81bba955ba137be690e085d4c88e`;
- the three existing workflow families and their nine jobs were green on that
  exact SHA;
- secret scanning and secret-scanning push protection were enabled;
- no repository ruleset or legacy `main` protection existed, and Dependabot
  security updates were disabled;
- a completed remote-main rehearsal bound the exact public SHA in manifest
  SHA-256
  `0f8b80572c2761436c0afe06660ce47a357bf17e718aa781328a8ffeacb5a47b`;
  and
- the local/remote invariant-profile comparison receipt had SHA-256
  `36046ac0bd2793f036024ac27b692b6e0884ca14a514e67dba879904abbd5cf2`
  and status `verified_evidence_and_invariant_profile_equal`.

Those manifests are noncanonical diagnostic evidence. They verify the bounded
release profile for `56e8062`; they do not establish Gate A, scientific
validity, or the controls decided here.

The historical top manifest is schema `0.1.0`, with nineteen retained files,
fourteen nested diagnostics, and eleven pinned profile files. This tranche
keeps the retained-file inventories unchanged by appending both new
publication self-tests to `final-release-contract.log`, but reissues the top
manifest as `0.2.0` with a twelfth profile file for the fourth workflow. The
comparator retains exact support for `0.1.0`, requires the matching profile
inventory for each version, and refuses cross-version comparison.

The repository owner explicitly authorized this repository-governance
hardening on 2026-07-19. That authority permits the bounded workflow, hook,
helper, ruleset, and Actions-policy changes needed to implement this decision.
It is not evidence that any account-side change has occurred. No document may
call either ruleset, the fourth workflow, ten-job inventory, or hardened
sequence active until exact implementation and live post-change observation
exist.

## Decision

Let:

- `B` be the freshly observed forty-character SHA at `refs/heads/main`;
- `C` be one clean, rehearsed candidate commit; and
- `R` be the exact ref `refs/heads/release/C`.

Every architecture publication after activation must preserve all of these
invariants:

1. `C` is one ordinary single-parent commit whose sole parent is `B`.
   `B..C` contains exactly `C`; merge commits and multi-commit ranges are
   invalid.
2. Before any remote candidate ref is created, the exact local rehearsal,
   remote-main rehearsal, and comparison receipt for the current `B` are
   revalidated as one completion triplet bound to `B`. A symlinked root,
   receipt, or configured parent, a missing or changed byte, or a valid
   historical triplet for any other subject refuses the new candidate. The
   complete local fresh-clone
   rehearsal, publication-history audit, and strict evidence-manifest
   verification then pass for `C`.
3. Every pre-existing open pull request is closed, then the repository
   pull-request feature is disabled
   (`has_pull_requests=false`). Repository settings disable merge commits and
   squash merges while retaining rebase merge only as GitHub's inert
   prerequisite for server linear history. Auto-merge, automatic branch
   deletion, and update-branch suggestions are disabled. Actions admission
   requires full-SHA pins and the default workflow token is read-only without
   pull-request approval authority. Exact live read-back is retained. Only
   after those controls are observed, and before `R` exists, a live no-bypass
   `immutable publication candidates` ruleset targets
   `refs/heads/release/*`, restricts updates, and blocks deletion,
   non-fast-forward changes, and nonlinear history. It does not restrict
   creation: `R` may be created once, after which every update or deletion is
   refused.
4. `R` is created once at exactly `C`. Its ref name contains the full lowercase
   SHA. It is permanent candidate evidence and may never be rewritten, deleted,
   or recreated.
5. A push to `R` starts four exact workflow families containing ten exact jobs.
   Every job must complete with conclusion `success` on `C`. Missing, queued at
   timeout, in-progress, canceled, skipped, neutral, stale, action-required,
   startup-failed, timed-out, or failed is not green.
6. A live no-bypass `main exact-SHA fast-forward` ruleset requires the exact
   ten GitHub Actions check contexts with strict current-base enforcement,
   deletion blocking, non-fast-forward blocking, and
   `required_linear_history`. The candidate ruleset requires the same server
   linear-history rule without status checks. The observed identities and
   effective rules for both rulesets are retained; prose or a submitted API
   request is not activation evidence.
7. Immediately before promotion, the publisher re-observes `main == B`,
   `R == C`, the local `HEAD == C`, a clean worktree, and the exact successful
   candidate runs. Any movement creates a new candidate boundary and requires
   new evidence; a descendant does not inherit `C`'s checks.
8. Promotion is one ordinary fast-forward update from `B` to `C`. Public
   `main`, the rehearsed candidate, and the checked release ref therefore carry
   the same commit SHA and tree.
9. The push to `main` starts the same four workflows and ten jobs on `C`.
   Publication remains incomplete until the newly created post-main runs—not a
   historical green run—are all successful and remote `main` still equals
   `C`.
10. A remote-main fresh-clone rehearsal of `C` then passes, and its independently
   verified manifest compares equal by the admitted invariant profile to the
   local rehearsal. The comparison receipt is retained outside the repository.
   The first activation additionally validates an immutable journal of the
   exact account mutations; revalidates bootstrap and final candidate checks,
   promotion governance, final `main` checks, and the remote comparison; proves
   both candidates are sole children of `B`; and read-only GitHub queries
   observe zero open pull requests, three settled four-run censuses, both
   protected exact-SHA branches, and the exact effective rules linked to the
   two journaled ruleset IDs. These are REST GETs plus one fixed
   repository-policy GraphQL query transported by POST; no GraphQL mutation or
   alternate query is admitted. The critical `main == C` ref read is the final
   GitHub request before receipt construction; a later candidate cannot
   overtake this settlement.

No later editorial commit, rebase, reconstructed tree, rerun on another event,
or matching short SHA inherits any part of this evidence.

The one-time activation requires two immutable alternative children of the
same base `B`, not a descendant chain. Bootstrap candidate `C1` carries the
pre-activation wording and creates the first ten-context census on
`release/C1`; only then can the strict `main` ruleset be created. The
post-account-state candidate `C2` has the same sole parent `B`, records the
already observed account state, receives its own local rehearsal and
`release/C2` checks under both rulesets, and is the sole SHA promoted to
`main`. `release/C1` and `release/C2` both remain permanent.

## Four workflows and ten contexts

The activated push inventory is exact:

| Workflow | Required successful job contexts |
| --- | --- |
| `Architecture / Foundation` | `Fast policy`, `Foundation`, `Schema contracts`, `Semantic contracts`, `Adversarial controls`, `Canonical identity`, `Architecture evidence` |
| `Repository / Release Surface` | `Release surface` |
| `Architecture / Bounded Formal Models` | `Bounded formal models` |
| `Repository / Publication Sequence` | `Publication sequence` |

The first three workflow definitions may retain explicit manual diagnostic
runs and dormant `pull_request` triggers. Repository-level pull requests are
disabled, so those triggers do not create an alternate review or promotion
path. The fourth workflow is push-only. On `release/<sha>`, `Publication
sequence` must prove that the checked-out SHA equals the SHA in the ref name,
is exactly one direct child of the freshly fetched `main`, and that the push
created the previously absent permanent release ref. On `main`, it must prove
that the event's before/after boundary is the same single-parent transition.
The other nine contexts remain necessary; the tenth does not summarize or
replace them.

## Disabled pull-request surface and promotion

Every pre-existing open pull request is closed before activation, after which
the repository exposes no pull-request feature. A historical pull-request run,
synthetic merge checkout, dormant workflow trigger, or `gh pr merge` is not
review, compatibility, or publication evidence for this sequence.

GitHub requires at least one compatible pull-request merge method to remain
enabled before it will enable `required_linear_history`. The exact repository
configuration therefore sets merge commits and squash merges false and rebase
merge true. Rebase merge is inert because `has_pull_requests=false`; the live
verifier rejects any drift that re-enables pull requests. The candidate is
promoted only by the guarded same-SHA fast-forward after the `main` ruleset
accepts the exact release-ref check contexts.

## Account-side activation boundary

The two intended active rulesets have no bypass actors. `main exact-SHA
fast-forward` targets `main`, blocks deletion and non-fast-forward updates,
requires `required_linear_history` and the ten exact successful GitHub Actions
contexts with strict current-base enforcement. `immutable publication
candidates` targets `refs/heads/release/*`, requires linear history, and blocks
deletion and non-fast-forward updates without a status-check rule. It also
restricts updates while leaving creation allowed, so each candidate can be
created once and a failed candidate remains immutable evidence rather than
becoming an undeletable status-policy deadlock.

The exact repository settings are `has_pull_requests=false`,
`allow_merge_commit=false`, `allow_squash_merge=false`,
`allow_rebase_merge=true`, `allow_auto_merge=false`,
`delete_branch_on_merge=false`, and `allow_update_branch=false`. The sole true
merge setting satisfies GitHub's configuration prerequisite for server linear
history but cannot be exercised while pull requests are disabled. The
verifier refuses any drift in those fields, including pull-request
re-enablement. Server linear history rejects merge commits; the push-only
`Publication sequence` context, local hook, and guarded helper enforce the
stronger one-single-parent/direct-child transition. That verifier ships in the
candidate it evaluates and remains a named self-modifiable-control residue.
Actions policy must also be observed after change; the target is full-SHA
Action admission with read-only workflow tokens and no workflow approval
authority.

The exact API requests, HTTP successes, two ruleset identifiers, read-back
payloads, evaluated branch rules, `main` and candidate-ref protection
observations, Actions-policy read-back, and a successful candidate-to-main
cycle are required activation evidence. The mutation journal is closed to
eleven exact exchanges and binds canonical request-body digests plus safe
response metadata; it never retains authorization headers. A fifth
`github_repository_activation_receipt` hashes that journal, the bootstrap
and final candidate checks, final promotion governance, final `main` checks,
and the independently revalidated remote comparison. It records the two
candidate-to-base parent bindings, fresh configured and effective rule
observations, and the final settled run censuses. Until all are retained, the
truthful end-to-end status is `authorized, not active`.

The read-only settlement verifier does not submit or repair account changes.
It uses REST GETs and one identity-bound repository-policy GraphQL query
transported by POST; its executable guard refuses GraphQL mutations and every
alternate query. In particular, a ruleset POST whose `201` was not durably captured is
`applied_outcome_unknown`: the caller must not retry it, and a later equal live
ruleset cannot reconstruct the historical exchange.

GitHub's detailed ruleset read-back may represent the false-valued candidate
`update` parameter either by omitting its parameters or by returning the exact
explicit `update_allows_fetch_and_merge=false`. The verifier accepts only
those two representations, rejects true or any additional parameter, and
normalizes retained governance receipts to explicit false.

## Known-bad boundary and residual risk

The implementation must retain known-bad proofs for at least:

- a two-commit range even when the tip, or both commits, have rehearsal
  manifests;
- a merge commit, wrong parent, stale `main`, release-ref rewrite, deletion,
  recreation, force push, or mismatched ref-name/SHA;
- either missing `required_linear_history` rule, an enabled pull-request
  feature, or drift from the exact inert merge configuration;
- missing, mismatched, duplicate-key, incomplete, non-passing, symlinked, or
  hash-drifted rehearsal evidence or comparison receipt;
- a passing predecessor-completion triplet whose subject is historical rather
  than the freshly observed current `main`;
- a green run from another SHA, ref, event, workflow, job inventory, or older
  attempt;
- missing, pending, skipped, canceled, neutral, timed-out, or failed required
  jobs;
- a duplicate-key, extra-operation, reordered, body-drifted, digest-drifted, or
  wrong-status mutation journal; nonpositive or equal ruleset IDs; symlinked or
  multiply linked retained receipts; or an effective rule not linked to the
  exact journaled ruleset; and
- a candidate or `main` ref that moves while checks or final settlement are
  running.

Three important residues remain after those controls:

1. The workflows, their structural validator, and most check logic ship in the
   candidate they evaluate. Coordinated weakening is not ruled out by green
   self-tests.
2. The local hook and verifier remain workstation controls. The rulesets close
   important server-side bypasses, but local chronology and retained
   operator-side evidence are not independently signed.
3. All required remote contexts currently come from one GitHub Actions app and
   account. No independent GitHub App or separately administered publication
   controller verifies the candidate-to-main transition.

Those are named residual risks, not reasons to retain the weaker sequence.
Closing them would require a separately governed verifier identity, immutable
external policy, and retained independent settlement evidence.

## Authority boundary

This decision governs publication of architecture repository bytes only. A
green candidate, active rulesets, same-SHA `main`, remote-main replay, or
comparison receipt does not admit a schema, issue the canonical profile,
approve a human decision, validate a scientific claim, authorize runtime,
deploy a product, expose mission data, spend resources, or pass Gate A. Gate A
remains blocked on its existing evidence, review, and operator-decision
requirements.
