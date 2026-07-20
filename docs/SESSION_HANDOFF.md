# Odeya Session Handoff

Status: canonical recovery entrypoint for the current Odeya architecture and
repository-release mission. Last updated 2026-07-20, Asia/Jerusalem. This is a
handoff contract, not Gate A acceptance, implementation authorization, or
scientific evidence; repository-publication authority comes only from the
named decisions and release contract. The exact-SHA two-ref publication
activation is complete at the exact public baseline named below, and the active
lane is the PRQ-013 human-decision-assurance architecture candidate described
below. This file cannot contain the commit that contains itself; resolve the
candidate's exact commit, rehearsal, publication, workflow, and remote replay
status from Git plus the external subject-bound receipts before acting.

Read this file before changing repository bytes. Then read the detailed
[Gate A working packet](GATE_A_HANDOFF_WORKING_PACKET_2026-07-15.md), the
[charter](../CHARTER.md), the
[current architecture status](ARCHITECTURE_STATUS.md), the
[pre-implementation gate](PRE_IMPLEMENTATION_GATE.md), the
[prerequisite closure plan](GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md),
the [cross-program process-evidence packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md),
the committed [implementation order](IMPLEMENTATION_ORDER.md), the
[standards profile](STANDARDS_PROFILE.md),
and the [repository release contract](REPOSITORY_RELEASE.md). Revalidate every
claim from repository bytes. A chat summary, model assertion, green check, or
prior audit cannot authorize a later commit.

When records differ, use this precedence: exact checked-out Git bytes and
machine-readable manifests; current architecture status and gate contracts;
this operational handoff; then dated historical packets and chat. A newer
document does not silently overrule an accepted decision, and an older count or
hash does not silently describe a descendant commit.

## Live GitHub activation checkpoint

The exact 2026-07-19 bootstrap boundary is:

- base/public `main`:
  `56e8062334fb81bba955ba137be690e085d4c88e`;
- permanent bootstrap candidate:
  `a25d026bd7233dfc452accc6087ded0bf015d7b4`, tree
  `8bfb4859a29bb1a9606dae59c168c64438cb6660`, whose sole parent is the
  base and whose exact ref is
  `refs/heads/release/a25d026bd7233dfc452accc6087ded0bf015d7b4`;
- active no-bypass candidate ruleset:
  `immutable publication candidates`, ID `19178198`;
- active no-bypass strict-status `main` ruleset:
  `main exact-SHA fast-forward`, ID `19178503`;
- pull requests 1 and 2 closed, `has_pull_requests=false`, merge/squash false,
  rebase true only as the inert linear-history prerequisite, auto-merge,
  delete-on-merge, and update-branch false;
- selected Actions with full-SHA pins required, GitHub-owned allowed,
  verified-creator admission false, no patterns, and read-only workflow tokens
  without pull-request approval; and
- four bootstrap push workflows and ten jobs all completed successfully on
  attempt 1 under GitHub Actions app ID `15368`.

Retained bootstrap evidence under
`/Users/danielwahnich/workspace/odeya-release-evidence/`:

- `a25d026bd7233dfc452accc6087ded0bf015d7b4/rehearsal-evidence-manifest.json`,
  SHA-256
  `722905919a9ca895152a941494e8c48b395f15fa5ff13046203eed5786fd7439`;
- `github-candidate-governance-a25d026bd7233dfc452accc6087ded0bf015d7b4.json`,
  SHA-256
  `518dd562d0a9be561e9d732d66778f2f034914980625a891e612e83ee2f49060`;
- `github-candidate-checks-a25d026bd7233dfc452accc6087ded0bf015d7b4.json`,
  SHA-256
  `e60cadf4823ef4a7f07123d47f68434f247ec53dab5dc89bf58d9fe1fac93652`;
  and
- `github-governance-mutations-a25d026bd7233dfc452accc6087ded0bf015d7b4.json`,
  the closed eleven-operation mutation journal, SHA-256
  `00b9661b0e4a316099c56432b99df6a3526382539ee01d15fe9ebe43e2d55827`.

Those bootstrap observations alone established the live account controls and
bootstrap census, not the first complete publication activation. Final
post-account-state candidate
`f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e`, tree
`a04586fd39c3a378b342f457a2fb105faf9de9b4`, later completed that activation:
at settlement its permanent release ref and public `main` were exact, its
separate candidate and post-main censuses passed, remote replay compared equal,
and
`github-activation-f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e.json` has
SHA-256
`2f9564a23bf3bde851244224eb5f69b5cfe881e39eec46b1387d5a34b85a1ab2`.

That activation also retained the corrected helper boundary discovered during
bootstrap: the attached frozen source ref and SHA are passed into `git push`;
the strict hook refuses missing, ref-mismatched, SHA-mismatched, detached, and
failed-cleanliness observations. These are historical facts about `f1f25fd`,
not evidence for the PRQ-013 descendant. The descendant must execute the
ordinary exact-SHA publication sequence from its own direct-child boundary and
must not rerun the one-time bootstrap.

## Public repository boundary

The architecture repository publishes in full at
`https://github.com/manfromnowhere143/odeya` (ADR 0047): every schema,
suite, validator, fixture, ADR, workflow, and this handoff — mission soul
included, because it is the soul of the project. The published history is
the complete owner-authored commit trail; nothing is squashed and nothing
is attributed to tools.

What stays local, by design, is evidence and tooling *about* the
repository rather than repository content: the fresh-clone rehearsal
evidence under `/Users/danielwahnich/workspace/odeya-release-evidence/`
(cited by commit hash, reproducible by anyone from the public bytes), the
session-scratch convergence tooling, and the operator's private session
memory. Sibling proof missions publish separately under the same owner:
`sentinel`, `telos`, and Inbar when its own lane completes.

## Mission soul

Odeya turns a thesis into a governed, replayable chain from question to
evidence to warranted claim. Its purpose is not to imitate research theater or
maximize model activity. Its purpose is to help people attack difficult
real-world scientific and engineering problems while preserving exactly what
was asked, tried, observed, contradicted, corrected, refused, and still remains
unknown.

For Daniel, the name carries a family dedication and the meaning “thank you,
God.” Honor that personal meaning through care, humility, intellectual honesty,
and useful work. Never convert it into marketing language or scientific
evidence.

The long vision is a private, provider-neutral cognitive research engine that
can evaluate a contributed thesis, accept or decline it through explicit
contracts, run admitted research missions, learn only from grounded outcomes,
and earn greater autonomy through replayable evidence. The immediate mission is
smaller and stricter: finish an exact, independently reviewable architecture
before any engine runtime is built.

Sentinel, Telos, and Inbar are proof missions and requirements sources. They are
not Odeya runtime dependencies and their results do not prove that Odeya is
implemented. Maestro and Aweb may be inspected as technical references only;
neither is Odeya authority, storage, namespace, runtime, or control plane.

## The standard — read this before you touch anything

You are inheriting a system built to one standard, and the standard is the
point. Hold it the way a launch-vehicle avionics team holds a flight rule and
the way a frontier-lab safety team holds an eval: **a claim does not exist
until its gate accepts it, and the gate must have a known-bad proof that it
fires.** Green is not truth. A passing suite is not correctness. A number you
did not measure this run is a rumor. Write nothing into the record that you
have not watched fail when it should fail.

The bar, stated concretely so it cannot be softened by fatigue or ambition:

- **Measure before you claim.** Every count in every document is bound to a
  gate that recomputes it. When you change a suite, the partition pins, the
  README checkpoint, and the coverage records will refuse the commit until you
  re-measure. That friction is the feature. Do not tune the pin to the number;
  re-run the audit and let the pin follow reality.
- **Refuse the flattering number.** Every coverage figure this repository has
  ever published — 69, 71, 75, 139, 161, "417 at the mutated path" — was wrong
  in the direction that flattered the author, and every one was caught by an
  outside attempt to break it, never by the author admiring the record. When a
  number pleases you, that is the moment to attack it.
- **Name the boundary; never paper over it.** The proof-of-proof regress is
  unbounded (ADR 0069): a self-test needs a self-test needs a self-test. You
  stop where the next injection buys less than it costs, and you *say where you
  stopped* and what the next step would cost. "Impossible" is almost always
  false and was disproved by construction once already. "We stopped here, on
  purpose, and here is the residue" is the honest sentence.
- **Production and verification are separate — including from yourself.** No
  session certifies its own work. A model cannot conclude its own independence:
  `ModelConfigurationRecord` fixes twelve correlation axes and pins
  `independence_conclusion_permitted` to false, and every review this project
  has run shared five of those axes with the producer. Run the reviews anyway —
  they find real defects — but label them context-isolated, not independent,
  and never let a model signature stand where the schema demands a human one
  (`review-determination` fixes `reviewer.principal_type` to `human`).
- **The published surface is evidence.** A push is not finished when the bytes
  leave the machine; it is finished when every exact remote workflow on the
  pushed commit is green and remote-main replay agrees. ADR 0091 accepts the
  stronger two-ref law: the freshly observed current-main completion triplet
  first revalidates, one rehearsed direct-child commit then passes four push
  workflows and ten jobs at `release/<sha>`, and the same SHA fast-forwards
  `main`, passes the new post-main runs, reproduces remotely, and survives a
  final exact-main/candidate-ref read-back.
  Its account barriers are active, and the first full candidate-to-main
  settlement is retained for `f1f25fd`; every descendant must execute the same
  ordinary sequence with new subject-bound evidence. This rule was written
  because earlier publication controls were repeatedly weaker than their prose
  (ADRs 0072, 0075, 0091).

If a decision optimizes the number at the cost of the truth of the number,
you have already failed, no matter how green the check. Slow is smooth and
smooth is fast: land verified increments, prove each one, and let the
fresh-clone rehearsal catch what your convenient local environment hides — it
has caught fabricated evidence, bypassed gates, and three separate bugs in a
single audit instrument, every time before a number reached the record.

## What this lane established, and where to put pressure next

The migration wave remains at audit zero and the profile remains unissued by
design. C5's WorkLease release-claim compatibility correction is the published
predecessor. The live work is the bounded PRQ-013 assurance candidate:

- **Guard coverage has explicit denominators, not whole-repository coverage.**
  The lifecycle checker has dedicated statement (222/229) and condition
  (108/111) audits. The retained generalized
  `audit_suite_guard_coverage.py` record measures fourteen declared isolated
  contract-checker subjects at 458 of 927 refusal statements proved, with 469
  explicitly unproved and zero crash-only detections. PRQ-013 contributes
  188/253, leaving 65 explicitly unproved. The former 431/820 result is
  retracted: its assurance-checker mutations tripped the unrefreshed outer
  checker-byte binding rather than the intended guards. Central
  architecture/release gates—including the PRQ-009
  assignment-order checker—are outside that denominator and must carry their
  own pinned known-bad self-tests. The 469 open isolated-suite guards are
  categorized by exact closure method in
  `docs/GUARD_COVERAGE_CLOSURE_PLAN.md`. Three closure
  patterns are proven and mechanical: harness self-tests (ADR 0080/0081),
  meta-proofs for the attribution self-tests (ADR 0083, now complete across all
  six), and the artifact-mutation vocabulary for once-loaded records (ADR 0082,
  proven on the first-slice inventory).
- **PRQ-013 now has a falsifiable candidate, not closure.** ADR 0092, three
  unissued Core/Evidence/Seal schema resource identities, a cycle-free static
  challenge frame plus separate deterministic vector, an exact unissued
  singleton-eligibility ruleset, a frozen-source consumer census, and a
  semantic suite exist. The Core expresses pre-ceremony requirements rather
  than completed observations. Evidence separates exact unmodified
  cryptographic inputs from sanitized derived records and retains direct
  challenge-lifecycle plus material-presentation/confirmation receipt
  provenance, but does not dereference the backing bytes. The signed challenge
  does not commit to the confirmation-receipt digest, so the application
  gesture and authenticator actor are not cryptographically co-bound and the
  profile is knowingly unissued. No independent ruleset implementation is
  retained. The census is complete only for the
  exact 112-schema predecessor tree: 19 direct or policy-conditional decision
  rows and 9 pending operator-acceptance rows. Zero current consumers are
  migrated. No admitted assurance record or `AssuredDecision` wrapper identity,
  real protected ceremony, end-to-end consumer refusal, accountable review,
  operator acceptance, or Gate A authority exists.
- **Where to put pressure.** The remaining bulk is the per-case domain-logic
  layer: guards inside per-case checkers that no retained case exercises. They
  close by targeted, ablation-verified cases in the ADR 0071 style — one
  mutation crafted to trip exactly that guard, proven to fire before retention.
  This is bespoke per-guard work, not another instrument, and some guards are
  genuinely unreachable by a candidate mutation without editing retained
  fixtures (which would corrupt the safe baseline); those are honest residue,
  named per suite, not oversights. **Do this work fresh and unhurried.** It is
  precisely the work where a rushed session produces a case that passes without
  proving anything, and a case that looks like proof and is not is worse than
  an open guard that is honestly counted.
- **Correctness is the frontier beyond coverage.** Everything measured so far
  is *statement reachability* — a guard is shown to fire, never shown to
  enforce the right rule. Condition-level (MC/DC) mutation exists for one suite;
  extending it, and moving from "the guard fires" to "the guard enforces the
  intended constraint," is the deep unit that outranks raw coverage percentage.

## The ambition, stated plainly so the standard has a reason

The immediate mission is small and strict on purpose: finish an exact,
independently reviewable architecture before any engine runtime exists. The
reason the bar is this high is the size of what it is a foundation for. Odeya
is meant to become a private, provider-neutral cognitive research engine that
can take a contributed thesis, accept or decline it through explicit contracts,
run admitted research missions against real scientific and engineering
problems, learn only from grounded outcomes, and earn greater autonomy one
replayable increment at a time — where every warranted claim traverses back to
exact inputs, methods, environment, cost, and provenance, and where a wrong
byte in the identity layer cannot silently poison every downstream claim.

That is why the profile decision is a human's and not a session's; why nulls
and failures are first-class; why negative evidence is never deleted; why the
kernel governs and the models only propose. The discipline is not bureaucracy
around a demo. It is the thing that will let this engine, if it is ever
allowed to run a real mission, be believed — and the only version worth
building is the one whose claims survive an adversary who wants them to be
false. Build to that. The next session that holds this standard is the one
that deserves to carry the mission forward.

## Non-negotiable engineering laws

1. Contract before cognition. Freeze scope, protocol, falsifiers, rights,
   resources, identities, and authority before consequential work.
2. Evidence before narrative. Every admitted claim must traverse to exact
   inputs, methods, artifacts, environment, cost, activity, and provenance.
3. Models propose; the deterministic kernel governs. No model, provider,
   consensus, signature, or generated prose is truth or policy authority.
4. Production and verification are separate. No agent verifies its own claim
   or approves its own consequential action.
5. Missing is never zero. Preserve `unknown`, `blocked`, `invalid`, `null`,
   `inconclusive`, `contradicted`, `corrected`, and `retracted` distinctly.
6. Negative evidence is first-class. Never delete a failed attempt, known-bad
   fixture, discrepancy, correction, or refusal to improve the story.
7. Event and evidence history is append-only; canonical state is reconstructible
   by deterministic replay. Search, vector indexes, UI views, and public
   surfaces are disposable projections, never truth.
8. Every external effect is separately governed. Repository writes,
   publication, messages, spending, data exposure, laboratory actions, and
   physical actions require exact authority and independent settlement.
9. Identity is immutable and explicit. Pin schemas, models, tools, runtimes,
   protocols, environments, and evaluation inputs; mutable aliases cannot
   support authoritative claims.
10. Claims stay bounded. Never write “safe,” “solved,” “autonomous,” “state of
    the art,” or “production-ready” without a named scope, comparator,
    benchmark, date, and retained evidence.
11. Every gate has a known-bad proof that it fires. Passing prose is never a
    substitute for adversarial fixtures, independent implementations, replay,
    and accountable review.
12. Start with the smallest dependency-complete vertical slice. Complexity is
    admitted only when evidence shows it is required.

## Current repository recovery identity

- Canonical workspace: `/Users/danielwahnich/workspace/odeya`; it is currently
  a protected concurrent-work lane on `agent/repository-release`.
- Active architecture worktree:
  `/Users/danielwahnich/workspace/odeya-prq-013-human-decision-assurance-20260719`
- Active architecture branch:
  `agent/t0-prq-013-assurance-candidate-20260719`
- Exact published baseline observed at recovery:
  `f4067b5d857e627aaf17a91a7a99239e815ed2a3`
- Exact published-baseline tree:
  `9aca5fe0e33ab8ff1fed29e8d308e0d008863644`
- Canonical remote: `https://github.com/manfromnowhere143/odeya` (public;
  created 2026-07-17 under ADR 0047; default branch `main`)
- Measured remote state on 2026-07-20: `origin/main` and permanent
  `release/f4067b5d857e627aaf17a91a7a99239e815ed2a3` both resolved to the
  exact published baseline. Four permanent release refs now exist —
  `a25d026`, `f1f25fd`, `8ed5d42`, `f4067b5` — and none is ever rewritten,
  deleted, or recreated, including for a candidate that fails. Its candidate and post-main workflow censuses,
  remote-main rehearsal/comparison, and final read-only activation receipt are
  retained under `/Users/danielwahnich/workspace/odeya-release-evidence/`.
  Resolve their current byte validity through the admitted verifiers; do not
  infer it from this prose.
- Pull requests are disabled; the exact inert merge configuration, Actions and
  workflow-token policies, no-bypass candidate ruleset `19178198`, and
  no-bypass strict-status `main` ruleset `19178503` were read back during that
  activation. Dependabot security updates remained disabled at the last
  observation.
- Repository visibility, creation, and evidence-gated architecture-publication
  authority: granted under ADR 0045 and ADR 0047 and reconciled by ADR 0087.
- Exact-SHA two-ref repository hardening authority: explicitly granted by the
  owner and bounded by ADR 0091. Account controls and the first end-to-end
  activation are complete for the published baseline; every descendant must
  execute its own exact-SHA sequence and inherits no evidence.
- Runtime, deployment, external-effect, and Gate A authority: not granted

This committed file cannot contain the hash of the commit that contains it
without recursion. The active branch `HEAD` is therefore the rehearsal subject
to resolve, never a hash copied from chat. It becomes a validated local
release-candidate subject only when the current `HEAD`, its tree, the checked-out
branch, and a fresh-clone evidence manifest agree.

Run first:

```bash
bash -euo pipefail <<'BASH'
cd /Users/danielwahnich/workspace/odeya-prq-013-human-decision-assurance-20260719
source scripts/ci/sanitize-git-environment.sh
git status --short --branch
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git symbolic-ref --short HEAD
git fetch --quiet origin main
git remote -v
git log --oneline --decorate -5
BASE_COMMIT=f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e
HEAD_COMMIT="$(git rev-parse HEAD)"
REMOTE_MAIN="$(git rev-parse origin/main)"
BASE_RELEASE="$(
  git ls-remote --refs origin \
    "refs/heads/release/$BASE_COMMIT" |
    awk '{print $1}'
)"
test "$(git symbolic-ref --short HEAD)" = \
  agent/t0-prq-013-assurance-candidate-20260719
test "$(git remote)" = origin
test "$(git remote get-url origin)" = \
  https://github.com/manfromnowhere143/odeya.git
test "$REMOTE_MAIN" = "$BASE_COMMIT" || test "$REMOTE_MAIN" = "$HEAD_COMMIT"
test "$BASE_RELEASE" = "$BASE_COMMIT"
test "$(git rev-parse HEAD^)" = "$BASE_COMMIT"
test "$HEAD_COMMIT" != "$BASE_COMMIT"
test "$(git rev-list --count "$BASE_COMMIT..$HEAD_COMMIT")" = 1
python3 scripts/ci/verify_github_release.py governance
git diff --cached --name-only
git diff --check
test "$(git -C /Users/danielwahnich/workspace/odeya symbolic-ref --short HEAD)" = \
  agent/repository-release
git -C /Users/danielwahnich/workspace/odeya status --short --branch
BASH
```

Expected invariants:

- the active architecture branch is
  `agent/t0-prq-013-assurance-candidate-20260719`;
- the canonical worktree remains on `agent/repository-release` with Daniel's
  protected UI/UX changes untouched;
- the exact baseline remains at its permanent `release/<sha>` ref, while public
  `origin/main` is either that baseline before publication or the exact active
  `HEAD` after same-SHA promotion;
- the active `HEAD` is one ordinary single-parent direct child of that baseline;
  an unexpected rewind, replacement, merge, or multi-commit range fails
  recovery;
- both no-bypass rulesets and the exact account policy pass live governance
  verification;
- the only remote is the canonical public `origin` created under ADR 0047;
- no unexpected worktree path is dirty; and
- Daniel's protected UI/UX lane remains outside architecture/release staging.

If any invariant differs, stop and establish ownership and lineage before
editing. Never use destructive reset, checkout, clean, or indiscriminate
staging to make the repository look tidy.

## Protected concurrent UI/UX lane

Daniel owns these current working paths:

- modified: `docs/IMPLEMENTATION_ORDER.md`
- modified: `docs/UI_UX.md`
- modified: `docs/decisions/README.md`
- untracked: `docs/UI_UX_MOTHERSHIP_CANDIDATE.md`
- untracked: `docs/decisions/0008-dual-surface-projection-boundaries.md`
- untracked: `docs/design/`

Their appearance in `git status` is intentional and does not authorize another
session to edit, stage, commit, normalize, discard, or describe them as Odeya's
accepted design. Before every architecture commit, prove that these paths are
absent from its diff. In particular,
`docs/decisions/README.md` is protected, so ADR 0092 is intentionally not
inserted into that index by this tranche. Do not mistake the absent index edit
for an absent ADR or silently take ownership of Daniel's bytes.

## Published C5 compatibility correction

[ADR 0090](decisions/0090-preserve-the-resource-claim-when-work-lease-ends.md)
records the published correction at `56e8062`. ResearchEvent 0.17.0 incorrectly required
`work.lease_released` to carry an unclaimed reservation even though
`attempt.start` had already committed the claim. The published tranche:

- reissues the unissued event envelope as ResearchEvent 0.18.0, where
  WorkLease release retains `reservation_claim_state=claimed`, the exact
  `resource.reservation_claimed` reference, the no-crash-release boundary, and
  the requirement for later separate settlement;
- reissues the blocked base WorkContract as 0.19.0 so its prospective
  assignment event binds ResearchEvent 0.18.0;
- reidentifies the profile-bound WorkContract wrapper as 0.20.0 and binds its
  exact 0.19.0 predecessor bytes without constructing or admitting either
  resource; and
- preserves every predecessor identity through the reissue ledger and exact
  Git objects rather than redirecting an old ID to new bytes.

The bounded sequence evidence is retained-fixture dereference without digest
recomputation. It observes only the first two members of the three-event
`attempt.start` commit—`resource.reservation_claimed` and `attempt.started`;
`verification.started` is referenced but not dereferenced. It observes the
complete three-event `attempt.report` commit—
`attempt.completed`, `resource.usage_observed`, then
`work.lease_released`—and a later, separate
`resource.reservation_settled`. The checker preserves one exact claim and usage
lineage, adjacent declared digest values, and identical non-fungible dimension
keys. Per dimension it checks:

```text
reserved_consumed = min(ceiling, actual)
unused            = max(ceiling - actual, 0)
overage           = max(actual - ceiling, 0)
billed            = actual
refunded          = 0
net               = reserved_consumed + overage - refunded
```

The exact published inventory is 112 schemas and 826 shared-manifest cases.
Lifecycle coverage is 222/229 refusal statements and 108/111 top-level
conditions; first-slice resolution retains 12 safe cases and 61 known-bads;
projection retains 63 cases. The local and remote rehearsals independently
verified the named checkpoint and compared equal by the retained invariant
profile. Never transfer those counts or evidence to a descendant from this
prose.

The compatibility finding `C5-WORK-LEASE-RELEASE-CLAIM-001` is corrected only
for these unissued candidate bytes. C5 and PRQ-009 remain
`unresolved_blocking`: the exact assignable WorkIntent, complete thirteen-event
assignment cohort, immutable members and reducers, registry/root,
checkpoint/witness/P0/activation chain, complete replay, accountable review,
and operator decision do not exist. The canonical profile is unissued and Gate
A remains blocked. The correction's publication and remote replay do not imply
admission, execution authority, Gate A acceptance, or runtime.

## Active PRQ-013 candidate — resolve release status from Git

[ADR 0092](decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md)
records the active architecture decision. It follows ADR 0089's finding that a
declared human principal and a valid signature do not establish a
human-controlled Odeya decision. The candidate keeps existing consumer schema
bytes unchanged and adds, side by side:

- unissued `HumanDecisionAssuranceCore`, `HumanDecisionAssuranceEvidence`, and
  `HumanDecisionAssuranceSeal` 0.1.0 schema resource identities;
- an exact, unissued singleton-eligibility ruleset with contradiction-first,
  fail-closed precedence and no retained independent implementation;
- a static, nonrecursive challenge-frame profile and a separately retained
  deterministic recomputation vector, avoiding a profile/Core digest cycle;
  the profile explicitly blocks issuance because it does not commit to the
  presentation/confirmation receipt digest and therefore does not
  cryptographically co-bind the application gesture and authenticator actor;
- synthetic valid Core/Evidence/Seal controls and
  `PRQ-013-KB-001`, the unattended agent-accessible-key known-bad;
- exact unmodified client data, authenticator data, signature, and credential
  public-key roles, plus eight sanitized derived-observation roles, direct
  challenge-lifecycle and presentation/confirmation provenance, and an
  explicit boundary that backing evidence bytes are not dereferenced;
- an exact census bound to predecessor commit
  `56e8062334fb81bba955ba137be690e085d4c88e` and tree
  `d90ed6dd8c54b91a1e503358f98ecaa08c766fa3`; and
- an isolated checker with 5 safe controls, 205 one-mutation intent-bound
  known-bads, and 145 distinct intent refusal rules.

The measured candidate inventory is 115 schemas and 848 shared-manifest cases,
with 14 isolated suites and 10 architecture-evidence checks. The current
canonical audit covers 115 schemas and 209 fixtures; all 158 retained
cross-field rule cases isolate their declared rule. The generalized guard
record is 458/927 proved across 14 suites, 469 explicitly unproved, and zero
crash-only detections. Its former 431/820 result is retracted because an
unrefreshed self-binding produced false-positive detections. The consumer census
partitions all 112 predecessor
schemas without changing one byte, inventories 121 command and 135 event
selectors, records 18 decision families, 9 pending operator-acceptance
consumers, 11 validators, and 33 explicit missing nodes.
The checker pins the exact family and validator inventories, every field of
the operator-consumer rows, every explicit missing-node identity/kind/status
tuple, and reconciles their coverage counts. Those semantic classifications
remain explicit census judgments rather than independently derived facts.
It also compares all current baseline-schema and Authority Matrix bytes with
the frozen Git source, requires the exact 115-schema union, resolves every
claim-bearing evidence reference to its required artifact role, and requires
direct decision-confirmation and delegation/effective-control provenance.

Those are structural and bounded-semantic candidate measurements, not
admission. The three schema IDs are unissued; no admitted assurance-record or
`AssuredDecision` wrapper identity exists; migrated consumer count is zero;
verified backing evidence bytes, independent eligibility recomputation,
cycle-free receipt/authenticator co-binding or an accepted transaction
confirmation trusted path, end-to-end consumer refusal, real protected
ceremony, accountable security and authority review, profile issuance, and
Daniel's exact-byte acceptance are all absent. PRQ-013, T1, Gate A, runtime,
deployment, scientific-results
publication, spending, data access, and external effects remain blocked.
Architecture-repository publication remains separately governed by the exact
release contract. Commit, rehearsal, repository-publication, and remote-check
status must always be resolved from the current exact Git subject and retained
release evidence rather than inferred from this prose.

## Historical recovery log — retained chronology, not current state

The dated tranche records below preserve how the architecture evidence evolved.
Their branch names, worktree paths, counts, blockers, and publication statements
are historical observations for their named bytes. They do not override the
current recovery identity, hard boundary, or next mission recorded above and
below.

## What the repository-release tranche established

The validated predecessor introduced the truthful README and Mermaid system
map, three least-privilege GitHub Actions workflows, immutable Action pins,
exact Python/Node/Java and toolchain identities, hash-locked dependencies,
workflow and dependency mutation tests, secret scanning, Git environment and
TLS isolation, fresh-clone reproduction, recursive evidence manifests, and a
comparator that rejects thirteen retained-evidence mutation classes.

Its clean-clone rehearsal established, for those exact bytes:

- 90 Markdown documents, 100 Draft 2020-12 schemas, and 588 valid/adversarial
  cases;
- eight isolated contract suites, 64 canonical identity cases, four
  metamorphic relations, 30 modules, 47 aggregates, 121 design commands, and
  135 event identities;
- seven distinct bounded safe TLA+ models, one alternate cognitive
  fingerprint execution, and all thirty expected negative counterexamples;
- a nine-commit exact-history secret scan with no findings;
- a nested fourteen-file repository-release manifest and nineteen-file
  fresh-clone manifest; and
- two non-authoritative adversarial review passes reporting no remaining P0,
  P1, or P2 release-scope finding. They are not retained accountable Gate A
  review determinations.

This is structural, bounded-semantic, release-engineering evidence only. It is
not engine runtime evidence, scientific superiority, Gate A acceptance, or
permission to push.

The predecessor evidence is retained at
`/private/tmp/odeya-rehearsal-evidence-ff512c5`. It belongs only to the exact
predecessor commit. A descendant never inherits it. Diagnostic evidence under
`/private/tmp` may disappear; absence requires reproduction, never invention.

## Historical isolated T0 architecture descendant at its checkpoint

The isolated architecture lane descends from the exact validated immediate
predecessor named above. Its current candidate tree contains 112 schemas, 660
shared schema cases, twelve isolated contract suites, 64 canonical vectors,
four metamorphic relations, 30 architecture decisions, and the
unchanged 43/60/25/11 first-slice boundary.

ADR 0020 adds a nonrecursive `odeya-jcs-0.1` profile core and an external
candidate-evidence binding. The core freezes exact candidate parser limits,
RFC 8785 serialization, canonical envelope, digest framing, future reference
shape, 21 current domain constants, and eight version axes for review. The
evidence binds exact raw bytes and retains one safe reference plus 26 known-bad
mutations. It issues no canonical digest, admits no profile member, and does
not close PRQ-001: the 112-schema/200-fixture migration audit remains blocked
at 122 unprofiled time paths, 61 number/decimal findings, 668 unscoped digest
fields, 56 divergent common-definition names, 11 unpinned profile bindings,
and 236 nonconformant fixture timestamps.

ADR 0021 adds an identity-free `work-intent-core:0.1.0` semantic subject and an
external `work-intent-identity-candidate-evidence:0.1.0` binding. The safe core
is exactly the retained WorkIntent 0.1 fixture after removing only its three
identity fields. Its schema contributes zero time/number/decimal/digest/profile
audit blockers, and the dedicated suite rejects 28 known-bad mutations. The
binding fixes exact current bytes for WorkIntent 0.1 and its two direct schema
consumers. It does not replace any of them, issue a canonical digest, or make a
WorkIntent assignable.

ADR 0022 materializes side-by-side WorkIntent 0.2, canonical WorkLease 0.2,
and WorkContract 0.3 successors while retaining all three predecessor resources
byte-for-byte. One exact cohort record binds the predecessor commit/tree,
successor schema/artifact bytes, and three dependency edges; its dedicated
suite rejects 37 known-bad mutations. No same-path schema mutation, mutable
alias, or implicit latest is used. The source-view and planning-epoch values
remain synthetic, the legacy output-schema digest mismatches the exact target
schema bytes, and all canonical identity/admission/authority fields remain
blocked.

ADR 0023 adds exact raw ResearchStateView and PlanningEpoch candidates,
WorkIntentCore 0.2, and side-by-side WorkIntent 0.3. It removes the three
placeholder reference values, binds the exact CandidateArtifact schema bytes,
and rejects 40 known-bad mutations. Raw candidate lineage is explicitly not
canonical object identity: both target canonical digests, the WorkIntent
digest, profile admission, registry membership, and all authority remain null
or false. The three new schemas add zero canonical-audit blockers.

ADR 0024 corrects a defect in the retained evidence itself rather than in a
contract. The lifecycle closure suite asserted only that a known-bad trace was
refused, never which guard refused it, and seven of its twenty-five traces
refuse with more than one error. Two guard weakenings were therefore confirmed
blind against the exact committed bytes: widening `authority.grant_activated` to accept `active`
made a second activation legal, and widening `authority.grant_used` to accept a
terminal state made use after revocation or expiry legal. Both left the suite
green at the same `cases` digest. PRQ-005 also enumerates four required
known-bad classes and only two had traces; `required_adversarial_tags` did not
detect this because it was derived from existing coverage rather than from the
PRQ. All twenty-eight adversarial cases now declare
`expected_refusal_contains`, each matching exactly one error of its own case,
and both mutations now fail closed. The AuthorityGrant state machine was already
correct; the defect was evidentiary. No transition table, state vocabulary,
event identity, schema byte, or first-slice boundary changed, and PRQ-005 is
not closed: closure additionally requires an independently reproduced verdict
that the producing agent cannot supply for its own change.

Context-isolated adversarial review reproduced both blindness claims on isolated
`git archive` trees, confirmed both halves of the change as load-bearing, and
corrected this handoff's own count from nine to seven by measuring the
pre-change tree rather than the post-change one. It also established that the
pre-existing `grant_use_before_active` trace was itself blind to its own guard,
and that seven AuthorityGrant guards remain weakenable with the suite green
because no trace exercises them at all — including the immediate-exhaustion rule
the README asserts, and the trailing-exhaustion rule that masked the
use-after-terminal guard. Those seven are the next lifecycle unit and are
smaller and more falsifiable than any new candidate resource. That review is one
non-authoritative pass, not a retained accountable Gate A review determination.

ADR 0025 answered the prior question — whether a guard is exercised at all — by
disabling every guard in turn and running the suite. Of 71 guards in the five
auditable lifecycle models, **24 were proved and 47 could be removed with the
suite green**. Only AuthorityGrant is complete, at 11 of 11, and only because ADR 0024
and this tranche completed it. `protocol_origin` is 3 of 12, `data_use_cohort` 4
of 11, `work_lease_trace` 2 of 8, `work_lease_record_candidate` 4 of 29.
`identity_map_mutation` is unmeasured rather than proved.

That was subtractive: **PRQ-006, PRQ-007, and PRQ-008 could not close on that
evidence.** Each named a property that no known-bad trace exercised — the
protocol origin materializing version 1 from absence, the data-use grant being
single-use at one atomic commit, and the exact five-state WorkLease vocabulary
that is law 40 of the state model. They were blocked on absent evidence, not on
a decision, which made them autonomous work rather than work waiting on Daniel.

ADR 0026 and ADR 0028 closed that gap in dependency order. Coverage is now
**75 of 75**: all five auditable models are guard-complete —
`authority_grant_trace` 11/11, `protocol_origin` 12/12, `data_use_cohort` 11/11,
`work_lease_trace` 8/8, `work_lease_record_candidate` 33/33. Every guard named by
PRQ-006, PRQ-007, and PRQ-008 is proved. Their closure records are corrected: a
stale "blocked on absent evidence" would mislead as much as the original silence.

ADR 0028 required widening what a known-bad case may express.
`work_lease_record_candidate` validates a retained fixture and accepted only four
named string mutations, so 23 of its guards were unprovable by construction — a
closed mutation vocabulary silently bounds what evidence can exist. It now also
accepts one bounded replace, the exact shape `identity_map_mutation` already
uses. The denominator grew 71 to 75 because that vocabulary carries four hygiene
guards of its own; all four are proved.

**ADR 0029 retracted the 75/75 headline; ADR 0031 corrected it again by
auditing every refusal-bearing function; coverage now stands at 111 of 160** —
including `identity_map_mutation_errors` (five return-guards, despite ADR
0029's claim it held none), `data_fixture_errors` (now 10/10: the
fixture-mutation vocabulary it needed exists, the same bounded replace the
other two models use, with its own wrapper hygiene guards audited 4/4), and
`branch_map` (2/2). The remaining 49 unproved statements are all in
`schema_contract_errors` (15/64). The 89-of-139 figure
had audited only the five models it named; `identity_map_mutation_errors` holds
no guard of its own and delegates to `schema_contract_errors`, which holds 64 and
was never in `AUDITED_MODELS`. It measured 4/64. Among the unproved were the
43/60/25/11 boundary guards themselves — the 60-event count, the 25-family count,
the exact identity-map set — which every tranche cites and the validator prints
on every run, with nothing proving they fire. Now 14/64 after eleven cases; the
mutation gained a `target` (identity|schema|inventory) because the model could
mutate only one of its three inputs, which is the same closed-vocabulary defect
ADR 0028 fixed one model earlier.

**ADR 0052 closed statement coverage at 160 of 160.** The forty-nine missing
proofs — branch-level payload identity, the canonical WorkLease candidate's
entire null/false authority boundary, the release/claimed-reservation blocker
PRQ-009 turns on, and the protocol and data-use cohort bindings — each gained
one adversarial case bound to its own guard. Twelve were unprovable by
construction because their guards read resources the model loads itself; the
mutation vocabulary gained `work_lease_schema`, `module_manifest`, and
`defining_paths` injection targets, the third recurrence of the
closed-vocabulary defect ADR 0028 and ADR 0031 fixed before. The suite now
caches file text per process (parse stays fresh per call, so case isolation
is unchanged): a run is 0.64s and the full audit re-measures in under a
minute. Coverage is still not correctness: every guard is shown to fire,
none is shown to enforce the right rule, and ADR 0030's condition-level
boundary below stands in full. ADR 0054 then closed the measured
condition blindness at **87 of 89** with 46 sharpened cases (one wrong
part, every sibling safe): helpers complete, the conjoined release/claim
case dissolved, the fabricated-profile disjunct proved, statement
coverage re-measured complete at 161/161 after the WorkLease harness
gained an ordered replace-list (fourth closed-vocabulary recurrence, own
hygiene guards proved). The two remaining disjuncts are
invariant-coupled (`pending_exhaustion ⟺ uses == max_uses` while
active) and retained deliberately as defense in depth — ADR 0054 is
their standing explanation, and a future full-coverage claim must
reproduce that argument or refute it with traces.

Read the denominator with suspicion. It has been 69, then 71, then 75, then 139;
every figure was published as fact and every one was wrong, because the
measurement is only as wide as where it was pointed and nothing reveals where it
was not.

**Read the numerator with suspicion too. ADR 0030 retracts the strength of every
coverage figure here.** The audit deletes a refusal *statement*, so a proved
verdict means that statement is reachable — never that the conditions inside it
are exercised. Deleting one disjunct (admitting a fabricated canonicalization
profile, a property PRQ-008 turns on) leaves the suite green and regenerates a
full-coverage record whose only diff is `subject_sha256`. Review measured 36 such
conditions across the five models. The digest pin is a change-detector, not a
weakening-detector. Condition-level mutation — each disjunct and conjunct, the
MC/DC question — is the next lifecycle unit and is a strictly larger audit than
the one built here.

There is a second masking form worth carrying forward. A closed mutation
vocabulary bounds what evidence can exist; so does a **conjoined known-bad case**.
`first-slice WorkLease release forgets the claimed reservation` has one naming
case that sets both of its disjuncts at once, so neither is independently
exercised. The case looks like proof of the guard and is proof only of its
disjunction.

The measurement is retained at `architecture/lifecycle-guard-coverage.json` and
reproduced by `scripts/audit_lifecycle_guard_coverage.py` (~90s). Do not
hand-edit that record; regenerate it.

Two enforcement facts matter, both established by context-isolated adversarial
review after this lane published the opposite. The cheap gate
(`scripts/validate_lifecycle_guard_coverage.py`, in the default validator)
enforces the checker digest and the record's arithmetic only. **It cannot detect
a falsified record**: flipping a guard to unproved, or deleting an unproved guard
by name, passes it once the counts are corrected. Only re-measurement catches
that, so ADR 0027 wires `--check` into `scripts/ci/rehearse-fresh-clone.sh`. Any
coverage claim must come from the rehearsal, never from `validate.py`.

And **the denominator is not self-defending**. `discover()` matches
`errors.append`, `errors.extend`, `errors += [...]`, and early `return [...]`. A
guard added through any other construct is invisible to the audit and to both
gates — exactly as two `return [...]` guards were, uncounted, until ADR 0027.
Extend `discover()` before adding a new refusal construct, and treat the guard
count as a claim requiring review rather than as a measurement.

ADR 0052 extended the harness to `schema_contract_errors` and closed it at
64/64; statement coverage stands complete at 160/160. ADR 0053 then
mechanized ADR 0030's condition-level boundary: every top-level member of a
guarded boolean chain is removed by mutation, in the ten models and the
three helper predicates. **The measurement is 39 of 87 conditions proved —
48 removable with the suite green**, including the fabricated-profile
disjunct ADR 0030 named, both halves of the conjoined release/claim case,
and the helper predicates almost whole (`valid_record_ref` 1/8). The record
is retained at `architecture/lifecycle-condition-coverage.json`, gated
cheaply in the default validator (fifth architecture-evidence check, digest
and arithmetic only — it cannot detect a falsified record and says so) and
re-measured for real by the rehearsal's new `lifecycle-condition-coverage`
stage. 132 single-condition tests and structural dict comparisons are
counted, not audited; field-level blindness inside structural expectations
remains unmeasured.

**HISTORICAL C5 CHECKPOINT: DECLARED ISOLATED-SUITE GUARD COVERAGE WAS
249/637, WITH 388 UNPROVED.** The C5 checker changes added two measured guards
and two proofs to the preceding 247/635 record, so that checkpoint's open
residue stayed 388. The
physical-verification correction had previously added eight measured guards
and eight proofs without increasing that residue. ADR 0080 closed three former
zero-coverage suites by in-harness self-test:
work-identity-successor-cohort 0→13/19, work-intent-identity-candidate
0→12/20, and canonical-profile-candidate 0→9/18. ADR 0081 moved
command-identity to 8/20; ADR 0082 proved the artifact-mutation vocabulary;
ADR 0083 made the six attribution meta-proofs load-bearing. The exact current
per-suite inventory is in `architecture/suite-guard-coverage.json`; do not
reuse this historical count as the current closure denominator.
Central evidence/release checkers are not in this denominator.

**THE GENERALIZED AUDIT MEASURED 161/579 AT FIRST (ADR 0079).**
The suite-agnostic mutation audit now measures twelve suites in under
seven minutes: 161 guards proved, **418 with no known-bad proof**, zero
crash-detections. Four suites prove nothing at all — 45 guards, including
three of the suites whose declared inventories ADR 0067 made exact, which
shows exactness binds what a case declares and not what the checker does.
Closing the 418 is case-writing at scale, not another instrument, and
every unproved guard is enumerated by name in the record.

**THE REPOSITORY MEASURED 23% OF ITS OWN GUARDS (ADR 0078).** 717 refusal
statements across thirteen suites; 169 proved to fire; **548 never
measured at all**. Every coverage number this session produced describes
lifecycle-closure alone. The other twelve suites are in the exact state
lifecycle-closure was in before ADR 0025: any guard deletable with its
suite green. A suite-agnostic mutation audit is the largest unblocked
evidence unit in the repository and is the next step.

**REVIEWERS THIS SESSION WERE CORRELATED, NOT INDEPENDENT.** All four
rounds shared the producer's provider, model family, prompt family,
harness and human principal — five of the twelve axes
`ModelConfigurationRecord` already enumerates, with
`independence_conclusion_permitted` fixed false. The ADRs called them
"independent"; that is corrected. A contracted refutation worker, the
cross-family stage this session omitted, and the boundary that
`review-determination` fixes `reviewer.principal_type` to `human` are
proposed in `docs/REVIEWER_AGENT_PROPOSAL.md` for the operator's
decision.

**THE MUTATION AUDITS ARE RECORDS, NOT GATES (ADR 0077).** `--check` is a
byte comparison against a record that `--write` regenerates from whatever
the checker currently says, so an author can launder a weakening by
re-measuring. Review demonstrated it end to end: floors lowered, record
regenerated, case set trimmed to one safe and one adversarial trace, every
check green. Both coverage gates now pin their measured totals, which
converts silent regeneration into a deliberate edit of a gate file but
does not close the hole. Closing it needs an independent baseline no
session can supply for itself — the same shape as the profile decision.

**EVIDENCE-QUALITY LANE STATUS, 2026-07-18.** ADRs 0052-0068 closed this
lane by measurement. Current retained numbers, all reproduced by the
exact-commit rehearsal: lifecycle statement coverage **172/181**,
condition coverage **97/99**, refusal attribution **1,147 bound negative
cases, zero unattributed** across every case-bearing manifest. Every
audit denominator is now itself audited, including the suite harness
(ADR 0066), and every proved item declares whether its detection was
case-attributed or a crash (ADR 0065).

What remains open in this lane, none of it silent: four ternary selectors
counted and unaudited; fourteen crash-detected condition proofs, fragile
by nature; nine statements and two conditions structurally unprovable and
individually explained (ADR 0066); the architecture-schema bindings are
observation-derived and mutation-correlated rather than hand-verified
against each case's intent (ADR 0068); and attribution everywhere is
binding, never weakening-mutation coverage — no schema-based suite is
proven unweakenable at its declared location.

**ROUND THREE (ADR 0069) reviewed ADRs 0064-0068 and refuted three
surfaces.** The coverage floors were free (probes fired for any threshold
>= 1, so 10/15 could become 1/1 with the suite green), tag coverage was
proved one-directionally, the self-test's own refusal matcher collapsed
to a polarity check, a removable conjunct in the repository walk was
invisible to both the numerator and the residue, and — most
importantly — ADR 0066's "structurally unprovable terminal turtle" was
disproved by construction. All are closed: floors pinned from both
sides, both tag directions probed, matcher factored and proved,
refusal-determining helpers audited, and the self-test's collaborators
made injectable with a meta proof asserting exact refusal counts.
Current: statements **178/183**, conditions **100/103**.

The standing correction from that round: the proof-of-proof regress is
UNBOUNDED, and every level can be closed by one more injection point.
Never claim a residue is impossible — state where you stopped and what
the next injection would cost. The current residue is five statements
and three conditions, each with a known injection named in ADR 0069.

Round three also refuted ALL FOUR surfaces of ADR 0068, and ADR 0070
retracts two published claims: `refusal_class` was decorative (inverting
all 457 produced zero failures; it is now recomputed and enforced, and
the replayed inversion produces 457 detections), and "417 refuse at the
mutated path" was wrong because the derivation treated `/` as an
ancestor of everything. Corrected: **232 at_mutation, 169
container_of_mutation, 56 implication**.

**CORPUS COVERAGE IS UNDER WAY (ADR 0071/0072/0073): 152 of the 286
cross-field rules now have an ablation-verified case** — refused with the rule
present, accepted with it deleted, re-proven by an eighth
architecture-evidence check and a rehearsal stage. 134 remain. Three
increments yielded 112, then 20, then 20; the profile is measured (ADR
0073) and the remainder resist because their `if` conditions entangle
neighbouring rules semantically, not syntactically. Further mechanical
generation looks unlikely to pay: the next real step is authored cases
from each rule's intent (~134 units) or a whole-schema constraint
solver. The original
finding stands as the reason:

**CORPUS COVERAGE, NOT ATTRIBUTION, IS THE MAJOR EVIDENCE UNIT.**
Review swept every root-level if/then cross-field rule in every schema
with invalid cases and deleted each in turn: **210 of 286 can be removed
with the entire 457-case corpus still green**, mostly because no case
exercises them at all. Attribution binds what a corpus exercises; this
corpus exercises well under half of the cross-field rules it exists to
protect. Two smaller open items from the same round: 100 cases bind at
the root (75 of 92 research-event cases share `('/', 'oneOf')`, because
a large oneOf yields only the branch failure and the informative
sub-errors live in its context), and conjunctive case names still bind
one conjunct at corpus scale.

Still unreviewed: the round-three responses themselves (ADR 0069, 0070).

With that boundary stated, the dependency-ordered mission below resumes:
the canonical profile decision remains the gating item, and it terminates
in Daniel's exact-byte review, which no session can grant itself. ADR 0054 closed the 48 (see above): 87/89 proved, two
invariant-coupled disjuncts retained deliberately. The evidence-quality
lane's next units are the six unattributed suites (229 known-bad cases
that cannot distinguish a guard firing from an incidental refusal) and the
five-spelling refusal-attribution convergence.

THE ATTRIBUTION BLINDNESS IS CLOSED BY CENSUS, NOT BY LIST (ADR
0055-0061): the six-suite frontier was itself an enumeration error — a
census found a seventh blind suite, `physical-contracts` (71 cases),
never on the list. All negative cases in all suites now bind the exact
constraint that must refuse them (384 across the seven attributed
suites; every carried count was an under-count: mathematical 19→37,
projection 37→54, cognitive 107→119, physical 0-listed→71), each suite
with a fail-closed self-test proving its attribution gate fires on
every run. Four further suites were already bound under earlier
spellings (`expected_errors`, `required_errors`,
`expected_status`/`expected_reasons`). They cannot currently distinguish a guard firing
from an incidental refusal, the condition that made lifecycle closure
blind. ADR 0055 attributed `architecture-review` (16 cases, exact
instance pointer + keyword, fail-closed self-test every run), ADR 0056
attributed `mathematical-contracts` (20 structural + 17 semantic, both
domains bound, four-way self-test), and ADR 0057 attributed
`first-slice-resolution` (21 C1-C8 cases bound to their invariants), and
ADR 0058 attributed `constitutional-construction` (29 cases), ADR 0059
attributed `projection-contracts` (37 structural + 17 semantic), and ADR
0060 attributed `cognitive-contracts` (107 structural + 12 semantic).
ADR 0062 closed the family: the domain-exact spellings are frozen as
the standard (no cosmetic re-spelling of proven bindings), and the
seventh architecture-evidence check enforces them by census — every
tests/*/cases.json is swept, a registered suite's unbound negative
fails, and an unknown suite carrying negatives fails closed. REVIEW ROUND
TWO (ADR 0063) then refuted three of four surfaces: the census itself was
rewritten fail-closed (total registry over case-bearing manifests, the architecture-schema
corpus attributed in full by ADR 0068 — 417 cases refusing at the mutated
path, 40 by implication, each declaring its refusal class — so the census
now reports 1,147 bound negatives and zero unattributed; command-identity
certified on its exact field), three further CI-only gates gained local
readers (schema pins, bare-interpreter imports, TLA pin copies), four
misbound and one ambiguous binding were rebound to intent, and ADR 0054's
impossibility claim was half-retracted by a retained zero-use-grant
counterexample — condition coverage now measures 88/89. Surviving
weaknesses are enumerated in ADR 0063, not resolved: (ADR 0067 closed the last one: the three subset suites now
declare intent plus an equality-enforced observed inventory, and the
reviewer's rebinding attack is refused in all three) (ADR 0066 closed the denominator omissions by auditing the harness
itself: both headline numbers retracted by measurement to statements
172/181 and conditions 97/99, the harness hygiene guards closed by an
in-harness self-test, and the residue structurally explained — six
self-test refusals are the terminal turtle of the proof-of-proof
regress, three are clean-tree assertions, two are semantically
unprovable) (the 8 compound-name under-bindings were dissolved by ADR 0064
with 18 ablation-controlled prong cases; the 13 crash-artifact proofs
are now declared as `detection: crash` in the retained records by ADR
0065, with the cheap gates refusing an undeclared proof kind). Any future frontier claim
must cite the census gate's output, not a carried list. Attribution is intent binding, not mutation coverage: no
schema-based suite is proven unweakenable at its declared location.

Read the tranche's convergence honestly. Across this tranche the canonical
profile audit moved from 675 to 668 unscoped digest fields, 118 to 122
unprofiled date-time paths, 233 to 236 nonconformant fixture timestamps, 62 to
61 number findings, and left 56 divergent common definitions and 11 unpinned
profile bindings unchanged. At that checkpoint, zero of the then-twelve PRQ
findings were closed and `profile_status` remained `blocked`, while the schema
count grew from 100 to 112. PRQ-013 was discovered later and is recorded below.
The added candidates are correctly evidenced and T0 issues no immutable member
by design, so this is not a discipline failure. It does mean the tranche is
additive and that PRQ-001 terminates in Daniel's profile decision, which no
session can self-close. The highest-value remaining autonomous work is
therefore the profile-independent findings and the evidence-quality audit above,
plus reducing the profile decision to an exact decidable package rather than
1,222 raw findings (originally 1,154; ADR 0033 removed four double-counted
timestamps, ADR 0034 rescued twenty-nine name-filter misses, ADR 0035 rescued
forty-three more by making the shape test descend unions and array items, and
ADR 0036 closed the loop by measurement: an independent name-blind termination
sweep returned empty -- 192 decimal occurrences across 112 schemas, all
governed, gate proven live on positive controls. **The operator delegated all
nine class decisions on 2026-07-17 (ADR 0037, acceptance record retained with
the exact audit digests), and the wave is executing: D1 is resolved — 236
fixture timestamps normalized, the audit's fixture blocker at zero, the live
candidate recomputing 986 findings (ADR 0038). Reaching zero exposed and fixed
two gates that could not observe success. D5b executed: all 49 accepted
domain names reserved in the profile core's new prospective_domain_registry,
core schema reissued 0.2.0, succession propagated through every consumer to a
fixed point (ADR 0039). D2a executed: 102 of 122 datetime paths
pinned across 45 reissued schemas; the transitive-consumer closure lawfully
reissued 59 resources in total (ResearchEvent moved to 0.8.0; the work-identity
family's checks migrated to post-wave semantics: predecessors verify against
their ledgered commits, never live files). D2b executed: ResearchEvent
reissued 0.9.0 with its 20 paths pinned, eight consumers lawfully reissued
behind it, 62 fixture instances and the identity map's 62 byte-bindings
migrated (ADR 0041). Class D2 is CLOSED by measurement: 273 profiled datetime
paths, zero unprofiled, alongside D1's zero. D3+D4 executed (ADR 0042): the
profile core freezes the typed scientific-decimal object (17-type registry,
negative-zero-free value pattern), the audit detector recognizes exactly that
shape with a fail-closed self-test, all 127 decimal leaves and both
binary-number domains migrated with union alternatives preserved, ~200
fixture values converted, four suites' semantic checkers unwrap the governed
object, and the ledger holds 69 reissues + 14 candidates. FOUR OF SIX classes
now measure zero. D5a-1 executed (ADR 0043): 270 mechanical digest scopes
annotated against the reservation registry, unscoped count 668 to 398, 85
reissues closed, lifecycle version pin now self-deriving. D5a-2 executed (ADR
0044): all 72 contextual occurrences classified by containing definition —
registry/member/attestation domains, target-resolved references,
in-record-declared separators, untrusted-copy marking; unscoped 398 to 326;
the version aligner is now trap-safe (guard text only, never payload values).
D5a-3 executed (ADR 0046): the mixed digest family classified per
containing reference family — byte for artifact/profile/candidate refs,
event/checkpoint/typed-record domains where declared or reserved,
target-resolved for generic reference defs; 281 annotated, 3 deferred by
design (set commitment + two unreserved manifests). Unscoped now 45 = exactly
the frontier/commitment construction-decision families. The construction decision
is DECIDED and executed (ADR 0048): canonical closed objects under the
frozen profile for every commitment subject, twelve domains reserved, the
two-subject field split, D5 CLOSED at zero. FIVE OF SIX classes measure
zero; 66 findings remain. D6 executed (ADR 0049): the
decimal family was dead text orphaned by D3 — 19 definitions deleted with
live-reference refusal; member_key and semantic_version narrowed to one
canonical form each with known-bad vectors proven to fire. Divergent names
55 to 50; 61 findings remain. D7+D8+D9 executed (ADR 0050): 201
rename-distinct moves to fixed point; three closed central vocabularies
frozen in the core with a fail-closed subset gate; all 11 profile bindings
pinned against the final core bytes (site-level refinements after
shared-def pins poisoned siblings and the gates caught it). THE AUDIT IS AT
ZERO ACROSS ALL SIX CLASSES — 1,222 findings to none, every reissue
ledgered, every gate migration recorded. The audit reports
gate_a_disposition candidate_clear. REVIEW ROUND ONE EXECUTED (ADR 0051):
four context-isolated fresh-context refuters attacked the wave; ledger lineage
and trap integrity survived byte-exact scrutiny; the detector's four
exemption surfaces and the vocabulary unions were refuted and hardened
with both-direction proofs — the audit holds zero under the strengthened
gates. The profile remains UNISSUED: the operator's exact-byte decision is
the only act that can freeze it.**
Residue for the reissue wave is recorded in the candidate's
decimal_closure_residue).

The canonical migration findings are now partitioned for decision. The
disposition candidate at
`architecture/canonicalization-migration-disposition-candidate.json` assigns all
1,222 findings of the six audit classes to exactly nine disposition classes; the
fourth architecture-evidence check recomputes that partition from the audit
bytes on every run and refuses drift, count tampering, duplicate rows,
pre-filled acceptance, a promoted status, a comparator declaration that
disagrees with the implemented rule, or an incomplete proposal row, with a
seventeen-mutation self-test that runs on every gated invocation. The D5
proposals surface the operator's hardest sub-decision honestly: roughly fifty
new digest-domain subject classes, with consolidation levers (one
reference-set-manifest domain collapses seventeen set-digest fields; the
command-registry pair is the most mechanical gap; the frontier/state-root
commitment family needs one construction decision before any naming). The
touched-schema union is exactly 100 of 112, so the blast radius is one
coordinated reissue wave regardless of which classes are accepted. 369 findings
are mechanical, 795 are table-driven behind two embedded proposal tables (127
decimal rows; 151 digest field groups — both fully proposed and bound by the
validator: every row carries a complete proposal from the declared vocabulary
or an explicit reason it defers to the operator; the gate is shape-completeness
only, and content correctness rests on the retained adversarial review plus the
operator), two are one binary-number judgment, and the remaining true
judgment sits in the divergent definition vocabularies. Physical coupling is
disclosed: roughly 312 D2/D3/D5 rows sit inside the divergent definitions
counted as D6-D8 units, so per-class acceptance changes reissued content
together, which the single wave absorbs. Every operator_acceptance slot is null: ADR 0032
records the partition; Daniel's per-class decision is a separate explicit
change. The next exact identity unit dispositions the retained canonical
migration findings per accepted class into immutable legacy resources versus
explicitly reissued candidate resources, without same-ID mutation. Only after accountable review and Daniel's
profile decision may profile-bound ResearchStateView/PlanningEpoch successors
receive canonical digests, followed by an admitted WorkIntent member and then
the exact thirteen-event assignment cohort. Preserve all null/false authority
boundaries until each separate prerequisite is evidenced.

Resolve the current isolated branch `HEAD` and tree from Git. A later handoff
message may name the resulting commit and retained fresh-clone evidence; this
file cannot recursively contain the commit that contains it.

## Reproduce the current exact `HEAD`

Reuse `.venv-architecture` only if its pinned dependencies are intact. The
following checks apply to the isolated architecture worktree. Daniel's
protected UI files remain in the separate canonical worktree and must never be
copied, staged, normalized, or removed. Pre-commit checks still cannot certify
a later commit; the definitive evidence is the exact-commit fresh clone:

```bash
.venv-architecture/bin/python scripts/validate.py
python3 scripts/validate_repository_release.py
python3 scripts/compare_rehearsal_manifests.py --self-test
bash -n scripts/ci/*.sh
```

Stage only an explicitly declared path list, inspect
`git diff --cached --name-only`, run `git diff --cached --check`, and prove that
no protected UI path is cached. The definitive validation is the fresh clone of
the resulting exact commit below.

Run the complete fresh-clone rehearsal after creating any scoped handoff or
architecture commit. Retain the new evidence in the private durable sibling
directory, outside both the Git worktree and temporary storage:

```bash
bash -euo pipefail <<'BASH'
cd /Users/danielwahnich/workspace/odeya-prq-013-human-decision-assurance-20260719
source scripts/ci/sanitize-git-environment.sh
commit="$(git rev-parse HEAD)"
evidence="/Users/danielwahnich/workspace/odeya-release-evidence/$commit"
test ! -e "$evidence"
bash scripts/ci/rehearse-fresh-clone.sh \
  "$commit" \
  /Users/danielwahnich/workspace/odeya-prq-013-human-decision-assurance-20260719 \
  "$evidence" \
  local
python3 - "$evidence" "$commit" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from compare_rehearsal_manifests import load_manifest

document, _ = load_manifest(Path(sys.argv[1]))
assert document["subject_commit"] == sys.argv[2]
assert document["source_class"] == "local"
assert document["remote_main_commit"] is None
assert document["canonical_scientific_evidence"] is False
PY
BASH
```

The rehearsal must end with a schema-`0.2.0`, nineteen-file manifest bound to
the exact `subject_commit`, with the twelve-file profile including the fourth
workflow. The nested repository-release manifest remains fourteen diagnostics;
the two new publication self-tests append to
`final-release-contract.log`. Inspect the nested manifest and Gitleaks logs.
Never reuse an earlier commit's evidence or treat a local source rehearsal as
remote-main proof.

## Current hard boundary

Gate A remains blocked. No executable research engine, production UI,
infrastructure, deployment, DNS change, domain purchase, provider or MCP
integration, paid compute, model admission, mission-data import, or
scientific-results publication is authorized. The public architecture
repository already exists under ADR 0047. Its only authorized repository
effect is an exact-commit, evidence-gated architecture publication performed
under `docs/REPOSITORY_RELEASE.md`; that authority does not imply runtime,
deployment, research-publication, external-service, or Gate A authority.

The allowed work is architecture evidence: schemas, contracts, decisions,
threat models, mathematical and physical specifications, adversarial fixtures,
bounded formal models, independent architecture-time implementations, review
records, and repository-release validation. Gate B permits only separately
authorized disposable probes after Gate A. Gate C is required before one
bounded runtime increment.

## Cross-program evidence absorbed on 2026-07-19

The retained
[cross-program packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md)
audits exact committed Sentinel, Telos, and Inbar snapshots as untrusted,
read-only requirements evidence. Dirty descendants and concurrent work are
excluded. Bounded session-log inspection corroborates command chronology and
exit status only; it does not establish authorship, human intent, scientific
validity, or authority, and raw session records are not imported into Odeya.

The audit does not establish that Odeya or any sibling programme is state of
the art. It sharpens five architecture obligations:

- PRQ-013 blocks every consequential human-only decision until a valid
  signature is separated from retained human-decision-assurance evidence over
  exact bytes;
- publication validation must inspect the exact shipped bundle and member,
  not a correct sibling source file;
- baton validation must reject a historical ledger or pointer that passes
  while the canonical current mission is later;
- interrupted provider contact preserves exact completion and spend as
  unknown when they cannot be reconstructed; and
- a measurement-blind match blocks empirical promotion pending adjudication;
  a demonstrated analytic/dependency identity is an analytic or implementation
  check, not an empirical measurement.

These are bounded corrections, not imported runtime, scientific results, or
sibling authority. The proposed Abstention Frontier (`AFT-001`) remains a
later preregistered research candidate only. It cannot begin before Gate A and
separate authorization, and it creates no fifth active mission.

## External-model decision: Inkling is frozen

Thinking Machines' Inkling model is watch-only. Do not download weights, call a
paid or authenticated endpoint, fine-tune, expose mission data, add an adapter,
change architecture around it, or claim affiliation.

Reopen evaluation only when all of the following exist:

1. meaningful independent evaluations rather than launch reporting alone;
2. stable serving support and an immutable model/runtime identity;
3. resolved license, acceptable-use, privacy, and evidence-rights review;
4. a preregistered mission-held-out comparator with cost and latency budgets;
5. adversarial long-context, multimodal, tool-authority, and safety tests; and
6. a measured advantage without a critical-stratum regression.

If Daniel separately authorizes that evaluation, Telos is the first isolated
shadow candidate because executable consequence tests can independently settle
bounded outputs. Inkling may only be an untrusted producer, extractor, coder,
critic, or adversary—never truth authority, sole verifier, adjudicator, safety
approver, publisher, or physical actor. Monitoring must not interrupt the Gate
A mission.

## Session record — 2026-07-20, three published increments

Published in order, each through the complete ADR 0091 sequence and each green
on attempt 1: `08dbad6` closed the interrupted bookkeeping tranche and added
ADR 0093; `8ed5d42` made the assurance encoder phase-aware; `f4067b5` recorded
the v2 adoption route. Public `main` is `f4067b5`.

The session opened on an interrupted tranche. A prior session had changed
subject bytes and stopped before re-declaring the records that bind them, so
the repository described bytes that no longer existed. Refreshing those records
cascaded into gates that refuse a moved number until it is re-pinned
deliberately, which is the intended behaviour and not an obstacle.

Four defects were found. Each is recorded because the correction is worth more
than the feature it interrupted:

1. A substitution hole in the new `challenge-frame` checker. The receipt was
   built from the recorded presentation challenge id rather than the
   recomputed one, so a session, origin, or decision-subject substitution
   would have changed the real challenge while the receipt kept validating
   against a stale identity. That is the exact presentation substitution ADR
   0093 exists to refuse. Found because three known-bads failed to produce the
   expected error; fixing the expectations instead of the checker would have
   buried it.
2. Silent registry drift. The isolated-suite list lives in `scripts/validate.py`
   and again in `scripts/audit_suite_guard_coverage.py`, and nothing compared
   them. A newly registered suite passed validation on every run while never
   being mutation-tested, and the coverage total did not move, so nothing
   complained. Coverage would have read as complete while one suite had zero.
   `scripts/validate_suite_guard_coverage.py` now compares the registries and
   carries `lifecycle-closure`'s exclusion with its justification, refusing a
   stale exclusion as well as a dropped suite.
3. A machine-generated commit author. The predecessor commit was authored
   `daniel wahnich <danielwahnich@10.25.100.12>`, exposing an internal address
   that would have entered public history permanently. It was unpublished and
   therefore still correctable.
4. Two nested-field edits written at the top level of a JSON record, leaving
   the real nested values stale. Both were caught by the byte-binding gates
   rather than by review. Verify nesting before writing, not after.

Guard coverage moved 373/853 to 458/927 across fourteen subjects, 469
explicitly unproved. The denominator grew because `challenge-frame` entered it
at 21/37; every other subject is unchanged and the deltas reconcile exactly.
The refusal added in `8ed5d42` is a `raise` and is therefore outside the
audit's discovery grammar, so it is guarded by a direct resolution check and
not by the mutation audit.

What is deliberately still false, and must not be flipped without the work:
`confirmation_gesture_and_authenticator_actor_cryptographically_co_bound`.
ADR 0093 supplies the construction and the `challenge-frame` suite re-derives
it independently, but the Core still pins the v1 profile and the Evidence
record carries no receipt. Adoption was attempted, hit a wall of coupled
binding errors, and was reverted rather than left half-applied. The route is
recorded above under the v2 adoption section.

## ADR 0093 v2 adoption — exact remaining increment

ADR 0093 closed the co-binding blocker in design and published at `08dbad6`.
`8ed5d42` then made the assurance encoder phase-aware. Neither adopted v2: the
Core still pins the v1 profile, the Evidence record carries no presentation
challenge or confirmation receipt, and
`confirmation_gesture_and_authenticator_actor_cryptographically_co_bound`
remains false. Adoption was attempted once and reverted deliberately rather
than left half-applied; what follows is the measured route, not a proposal.

Core adoption and the Evidence receipt must land as one atomic change. The
Core's raw digest is an input to the phase-one frame, so changing Core moves
the presentation challenge, which moves the receipt digest, which moves the
authentication challenge and its identity. Editing the fixtures first and
reconciling afterwards produces recorded digests describing a Core that no
longer exists.

Derive the chain in this order, once, after the Core bytes are final:

```text
Core bytes -> core_raw_sha256
           -> phase-one frame (12 fields, V2 magic) -> presentation_challenge_id
           -> confirmation receipt frame -> confirmation_receipt_raw_sha256
           -> phase-two frame (15 fields, 3 appended last) -> challenge_id
```

Exact edit points:

1. `schemas/human-decision-assurance-core.schema.json` —
   `ceremony_request.challenge_framing_profile` consts move to
   `odeya-human-decision-challenge-frame-v2-candidate`, `0.2.0`,
   `sha256:585952ace1c4e804c0443532ecb9fcc7eda6e7ce2cd1c18bfd459c0a14255273`,
   `5701`. Add `authentication_commitment_fields` (the exact 15-field list
   from the v2 profile), `two_phase_challenge_required`, and
   `confirmation_receipt_profile`. Keep `challenge_commitment_fields`
   unchanged; it is the presentation phase and its bytes do not move.
2. The matching Core fixture.
3. `schemas/human-decision-assurance-evidence.schema.json` — the participant
   observation's `challenge` gains `presentation_challenge` and
   `confirmation_receipt`. The receipt must not admit an
   `authentication_challenge_id` field; that omission is the acyclicity.
4. The Evidence fixture takes the derived values. Its `challenge_value`,
   `challenge_id`, `issued_at`, and `expires_at` become the phase-two values.
5. `tests/human-decision-assurance/check.py` — repoint the frame profile and
   frame evidence paths, move `evaluate_challenge_frame`'s pinned
   `profile_id`, `profile_version`, `issuance_disposition`, and `purpose` to
   the v2 strings, extend `chain_challenge_inputs` with the three appended
   fields sourced from the observation receipt, and verify the receipt against
   the **recomputed** presentation challenge id.

Two errors were made and corrected during the attempt; both are cheap to
repeat:

- Phase timestamps must sit inside the fixture's existing ceremony window
  (`2026-07-19T06:00:00Z`–`06:05:00Z`, assertion at `06:02:00.250000Z`).
  Inventing a fresh day produces
  `decision_confirmation_stale_or_out_of_window`. Retained values that work:
  phase one `06:00:00`–`06:05:00`, gesture `06:01:15`, phase two
  `06:01:30`–`06:04:00`.
- The receipt must bind the recomputed phase-one identity, never the recorded
  one. Building it from the recorded id lets a session, origin, or
  decision-subject substitution validate against a stale identity — the exact
  presentation substitution this construction exists to refuse. That defect
  was found and fixed in the `challenge-frame` suite and is easy to reproduce
  in the larger checker.

Do not repoint the frozen predecessor values. `tests/challenge-frame/check.py`
and `architecture/human-decision-challenge-frame-v1-candidate-evidence.json`
retain the v1 vector, and reproducing it exactly is what validates the encoder
against history rather than against itself.

After adoption: receipt-binding known-bads, refresh every record binding the
changed bytes, one generalized guard re-audit, exact-commit rehearsal, and the
ADR 0091 publication sequence. Only then may the co-binding prerequisite flip,
and only as a construction property — never as measured ceremony evidence.

## Next architecture mission, in dependency order

1. Resolve the active ADR 0092 PRQ-013 candidate from exact Git state. Its
   `HEAD` must be one clean direct child of fixed predecessor
   `f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e`; public `main` must equal that
   predecessor before promotion or exact `HEAD` afterward. If the candidate is
   not locally rehearsed, publication-audited, created once at its permanent
   `release/<sha>` ref, green in all ten exact-SHA GitHub contexts on that ref,
   same-SHA promoted, green in ten newly created post-main contexts, remotely
   rehearsed, and comparator-equal, finish that ADR 0091 sequence before adding
   bytes. If all evidence is already retained for exact `HEAD`, verify it
   byte-for-field; never redo a permanent release ref or let a descendant
   inherit its evidence.
2. Freeze the PRQ-013 individual-assurance foundation candidate: design either
   a cycle-free two-phase challenge that commits to an exact
   pre-confirmation/presentation receipt or an accepted
   transaction-confirmation trusted path; define exact evidence-store,
   backing-artifact, and byte-verification contracts; and retain independent
   architecture-time implementations of the singleton ruleset and verifier.
   Keep the profile and ruleset unissued pending Gate A. This is a T0
   prerequisite, not final PRQ-013 closure, consumer migration, or runtime.
3. Complete the remaining T0 closure without weakening PRQ-009 or the corrected
   C5 ownership semantics. Profile issuance, exact member/reducer/root
   identities, the assignable WorkIntent, thirteen-event assignment cohort,
   replay, registry/root, checkpoint/witness/P0/activation, and remaining
   prerequisite determinations stay open.
4. After T0 and the PRQ-013 foundation candidate—not final PRQ-013
   closure—construct and prove the T1 `AuthorityAssignment` vertical contract.
5. Complete the exact 42 payload schemas, 43 command records, 60 event records,
   25 state/aggregate subjects, and 25 reducer records without changing the
   retained first-slice boundary by implication.
6. Construct one digest-coherent registry/root/C0/checkpoint/witness/P0 and
   inactive activation-candidate chain.
7. Only after the T1/T2 authority, currentness, quorum, and consumer
   dependencies exist, define side-by-side unissued assurance-record,
   `AssuredDecision`, and successor-consumer identities plus the exact
   transitive migration map. Do not mutate retained identities or call a
   candidate admitted.
8. Prove end-to-end consumer refusal—not only standalone assurance refusal—for
   contradicted/`invalid` `PRQ-013-KB-001`, missing/unknown/`indeterminate`
   evidence, stale/withdrawn evidence, changed displayed or decided bytes,
   collapsed effective principals, invalid quorum, timeout, and silence.
   Recompute the census whenever a schema, command/event selector, decision
   family, or Authority Matrix byte changes.
9. Produce two non-sharing architecture-time reference reducer implementations,
   fixture harnesses, and two independently isolated scientific verifier paths.
   They are design evidence, not engine runtime.
10. Retain replay, interruption, recovery, correction fanout, resource and
   authority race, proof-mission refusal, and rights-settled import evidence.
11. Obtain accountable statistical,
   physical/metrology/VVUQ/safety, security/privacy, distributed-systems, and
   accessibility reviews, including accountable PRQ-013 security and authority
   review.
12. Produce one immutable candidate manifest and clean commit for Daniel's
   exact-byte Gate A accept, reject, or amend decision. Gate A evaluates the
   ceremony architecture and synthetic/independent conformance evidence; it
   does not require or authorize a live ceremony.
13. Only after Gate A and separate authority, run at most one bounded,
   disposable Gate B protected-ceremony probe under the accepted profile,
   alongside any other explicitly authorized probes. Agents receive no
   credential or approval authority.
14. Integrate the bounded Gate B findings, then request one separately
    authorized Gate C implementation increment with runtime conformance as its
    exit condition. The public architecture remote grants neither authority.

Every architecture publication must bind the operator-approved public
repository identity, exact base/candidate commit and tree, immutable
`release/<sha>` ref, expected `main` ref, canonical-source digest, retained
rehearsal evidence, and exact remote runs. The local pre-push hook is a
workstation control, not server-side branch protection. As measured at the
ADR 0091 pre-change boundary on 2026-07-19, the repository ruleset was absent
and Dependabot security updates were disabled. That ruleset finding is
historical: the two no-bypass rulesets and exact account configuration were
subsequently applied and read back under the owner's bounded authority.
Dependabot security updates remain disabled and visible as a separate
repository-governance finding.

Do not skip forward because a model appears capable, a domain becomes
available, an investor asks, or a deadline feels important. Pressure is handled
by making the next dependency smaller and more falsifiable, not by weakening
the gate.

## The published surface is part of the evidence

Published baseline `f1f25fd…` carries the ADR 0091 hook, verifier, fourth
workflow, two-ref helper, and completed first activation; both no-bypass
rulesets are observed. The hook and helper remain local workstation controls
alongside—not substitutes for—the server rulesets. Run
`git config core.hooksPath .githooks` in every clone, publish only through
`scripts/ci/push-rehearsed-head.sh`, and never call that local configuration
branch protection. Audit history with
`scripts/ci/audit-publication-evidence.py <range>`. ADR 0074 retains a dated,
explicitly historical range finding; resolve its exact range before
interpreting its counts and never reuse them as the current range audit. The
guarded helper refuses missing exact-SHA rehearsal evidence, a dirty worktree,
or an invalid base/candidate relationship.

ADR 0091 publication is one closed sequence: revalidation of
the current-main local/remote/comparison completion triplet; local rehearsal on
a single direct child; immutable `release/<sha>` push; four exact workflows and
ten successful jobs on that SHA; live no-bypass ruleset read-backs; same-SHA
fast-forward to `main`; ten newly created successful post-main jobs;
remote-main replay/comparison; and a final exact-main/candidate-ref read-back.
Every release ref is permanent candidate
evidence, including a failed candidate; it is never rewritten, deleted, or
recreated. The candidate ruleset permits the initial creation, then restricts
every update and blocks deletion/non-fast-forward and nonlinear changes. The
`main` ruleset also requires server linear history. Pull requests are disabled
after every pre-existing open PR is closed. Merge commits and squash merges are
disabled; rebase merge is enabled only as GitHub's required linear-history
prerequisite and is inert while `has_pull_requests=false`. The live verifier
refuses drift from that exact configuration. The push-only context, hook, and
helper enforce the stronger exact one-single-parent/direct-child transition
and remain a self-modifiable verification boundary.

For candidate `C`, retain `github-candidate-governance-C.json`,
`github-candidate-checks-C.json`, `github-promotion-governance-C.json`, and
`github-main-checks-C.json` outside the repository. They respectively bind the
pre-candidate repository/Actions/candidate-ruleset read-back, the exact
release-ref four-run/ten-job census, the full pre-promotion two-ruleset
read-back, and the separate post-main four-run/ten-job census to
`subject_commit=C`. They are normalized noncanonical diagnostic receipts, not
authority; an existing byte drift or symlinked path/parent refuses settlement.
The first activation also retains
`github-governance-mutations-C1.json` and `github-activation-C2.json`.
The former records the eleven exact REST exchanges without credentials. The
latter is read-only and binds that journal, bootstrap and final candidate
checks, final promotion governance, final `main` checks, the independently
revalidated remote-main comparison, zero open pull requests, both permanent
release refs, branch protection, and exact effective rules. REST supplies the
GET observations; one fixed GraphQL repository-policy query is transported by
POST because REST hides merge fields once pull requests are disabled. The
verifier rejects every GraphQL mutation or alternate query. A lost ruleset
`201` is `applied_outcome_unknown` and must never be reconstructed by retry.
The completed initial promotion invoked the helper with
`ODEYA_ACTIVATION_BOOTSTRAP_SHA="$BOOTSTRAP_COMMIT"` and ran the exact
settlement form below after the final remote comparison. This expanded form is
retained only for historical recovery and independent inspection. Ordinary
descendants, including PRQ-013, must leave
`ODEYA_ACTIVATION_BOOTSTRAP_SHA` unset and must not emit a new one-time
activation receipt:

```bash
python3 scripts/ci/verify_github_release.py activation-evidence \
  --base-sha "$BASE_COMMIT" \
  --bootstrap-sha "$BOOTSTRAP_COMMIT" \
  --sha "$FINAL_COMMIT" \
  --mutation-journal "$EVIDENCE_ROOT/github-governance-mutations-$BOOTSTRAP_COMMIT.json" \
  --bootstrap-checks-receipt "$EVIDENCE_ROOT/github-candidate-checks-$BOOTSTRAP_COMMIT.json" \
  --candidate-checks-receipt "$EVIDENCE_ROOT/github-candidate-checks-$FINAL_COMMIT.json" \
  --promotion-governance-receipt "$EVIDENCE_ROOT/github-promotion-governance-$FINAL_COMMIT.json" \
  --main-checks-receipt "$EVIDENCE_ROOT/github-main-checks-$FINAL_COMMIT.json" \
  --comparison-receipt "$EVIDENCE_ROOT/remote-main-comparison-$FINAL_COMMIT.json" \
  --local-evidence "$EVIDENCE_ROOT/$FINAL_COMMIT" \
  --remote-evidence "$EVIDENCE_ROOT/remote-main-$FINAL_COMMIT" \
  --output "$EVIDENCE_ROOT/github-activation-$FINAL_COMMIT.json"
```

The retained release-surface self-tests currently pin sixteen publication
update/event/environment refusals; all four helper governance-scope states; one
real readonly-caller validator invocation; four attached/detached/renamed/
wrong-SHA source-ref states; three clean-worktree observation states; five
real-hook frozen-binding/status protocol states; ten check-census mutations;
sixteen governance mutations; six GitHub receipt mutations; six
API-identity/query mutations; five disabled-PR-census mutations; six
CLI-boundary mutations; five mutation-journal mutations; nine final
activation-observation mutations; and nineteen rehearsal-comparison/evidence
mutations. The disabled-PR census reads the Issues endpoint and refuses a
saturated page because GitHub returns 404 from the pulls endpoint after
`has_pull_requests=false`.

The completed first-activation predecessor baseline is
`f1f25fd336daa1dd2707ba36b832e8d5c5e41d3e`. Its local rehearsal manifest
SHA-256 is
`d76decdfe700ad7b1a84a05985f965317230c012abc814d74f3354a45b978ad6`;
its remote-main manifest SHA-256 is
`7c95257080886dca91b282b27055279a4ab4697717491ac5fb9bab9138128b17`;
its comparison receipt SHA-256 is
`442ab446a1fad1a62ec6049b978b2af53fa1b67ccbd6acebf34619ff540ea625`;
and its final activation receipt SHA-256 is
`2f9564a23bf3bde851244224eb5f69b5cfe881e39eec46b1387d5a34b85a1ab2`.
Bootstrap `a25d026…` separately retains the evidence listed at the top of this
handoff. The older `56e8062` checkpoint remains the legitimate frozen source
for the PRQ-013 consumer census, not the current publication baseline. Resolve
the active descendant's own publication state from its exact external
receipts; never infer it from either historical subject.

Treat any red, missing, skipped, canceled, timed-out, stale, or unverified
remote job exactly like a failed local gate: stop, diagnose, and do not promote.
This law exists because seven commits were once published with the remote
Foundation workflow red while every local rehearsal was green. The partition
gate now runs locally too, but the broader lesson remains: no session may
leave public `main` red or unverified at handoff.

## Definition of a proper continuation handoff

Before ending a future session:

1. preserve all work owned by other lanes;
2. inspect the complete diff and stage only the declared scope;
3. validate the staged or committed exact tree, not a convenient mixed
   worktree;
4. create a scoped local commit with an intentional message;
5. rerun the exact-commit fresh-clone rehearsal when release bytes changed;
6. record the branch, commit, tree, evidence location, checks, open blockers,
   exact public-repository publication authority, absence of runtime and Gate A
   authority, and—if publication occurred—verify the pushed head's remote
   workflows are green;
7. update this handoff when mission state or decisions materially change; and
8. leave every unsupported claim and incomplete item explicit.

The standard is not that the next session feels confident. The standard is
that it can recover identity, reproduce evidence, see every boundary, and know
the next safe action without trusting the previous session's memory.
