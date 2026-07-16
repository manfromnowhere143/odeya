# Odeya Session Handoff

Status: canonical recovery entrypoint for the current Odeya architecture and
repository-release mission. Last updated 2026-07-16, Asia/Jerusalem. This is a
handoff contract, not Gate A acceptance, implementation authorization, remote
authority, or scientific evidence.

Read this file before changing repository bytes. Then read the detailed
[Gate A working packet](GATE_A_HANDOFF_WORKING_PACKET_2026-07-15.md), the
[charter](../CHARTER.md), the
[current architecture status](ARCHITECTURE_STATUS.md), the
[pre-implementation gate](PRE_IMPLEMENTATION_GATE.md), the
[prerequisite closure plan](GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md),
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

- Canonical workspace: `/Users/danielwahnich/workspace/odeya`
- Active release branch: `agent/repository-release`
- Isolated architecture candidate worktree:
  `/Users/danielwahnich/workspace/odeya-t0-work-lease`
- Isolated architecture branch: `agent/t0-work-lease-20260716`
- Validated immediate predecessor:
  `f79ce3cc7c1dd300e6f3c2c54a85b200c8ca119c`
- Validated immediate predecessor tree:
  `c49ba1ba485c08f1f230da9fb3522d526acaf513`
- Retained immediate-predecessor rehearsal evidence:
  `/Users/danielwahnich/workspace/odeya-release-evidence/f79ce3cc7c1dd300e6f3c2c54a85b200c8ca119c/rehearsal-evidence-manifest.json`
- Validated exact-reference predecessor:
  `45c1fd769a123a9bf03e8de93c2ecf127b254199`
- Validated exact-reference predecessor tree:
  `39111bfa595c8b12e28b0d8de309e0b5e2f6fc99`
- Retained exact-reference rehearsal evidence:
  `/Users/danielwahnich/workspace/odeya-release-evidence/45c1fd769a123a9bf03e8de93c2ecf127b254199/rehearsal-evidence-manifest.json`
- Validated WorkIntent-identity predecessor:
  `6ec40b4635815c64ba9d8c5ec084d7f480e16db1`
- Validated WorkIntent-identity predecessor tree:
  `e7044da26ad273de8491a34705e87c8899173f29`
- Retained WorkIntent-identity rehearsal evidence:
  `/Users/danielwahnich/workspace/odeya-release-evidence/6ec40b4635815c64ba9d8c5ec084d7f480e16db1/rehearsal-evidence-manifest.json`
- Validated canonical-profile predecessor:
  `c9ce09d49fa38e11eed4ff40ee484e6e0ed9593f`
- Validated canonical-profile predecessor tree:
  `ec170fa22f03108b914fa8c204fb13bb26f4bbd1`
- Retained predecessor rehearsal evidence:
  `/Users/danielwahnich/workspace/odeya-release-evidence/c9ce09d49fa38e11eed4ff40ee484e6e0ed9593f/rehearsal-evidence-manifest.json`
- Validated WorkLease predecessor:
  `763e7d48889265835c76ef66878515467cdf09b6`
- Unchanged local `main`: `f8c71c8e3174f07619e0bbd31cb3d6df5d848361`
- Validated repository-release predecessor:
  `ff512c5211f6ace0816e7991913234ce7cb72e25`
- Validated repository-release predecessor tree:
  `39c88d64a03c9227749d8aa045d57301e1f78997`
- Canonical remote: none
- Repository visibility, creation, push, publication, and deployment authority:
  not granted

This committed file cannot contain the hash of the commit that contains it
without recursion. The active branch `HEAD` is therefore the rehearsal subject
to resolve, never a hash copied from chat. It becomes a validated local
release-candidate subject only when the current `HEAD`, its tree, the checked-out
branch, and a fresh-clone evidence manifest agree.

Run first:

```bash
bash -euo pipefail <<'BASH'
cd /Users/danielwahnich/workspace/odeya-t0-work-lease
source scripts/ci/sanitize-git-environment.sh
git status --short --branch
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git symbolic-ref --short HEAD
git rev-parse main
git remote -v
git log --oneline --decorate -5
test "$(git symbolic-ref --short HEAD)" = agent/t0-work-lease-20260716
test "$(git rev-parse main)" = f8c71c8e3174f07619e0bbd31cb3d6df5d848361
test -z "$(git remote)"
git merge-base --is-ancestor \
  f79ce3cc7c1dd300e6f3c2c54a85b200c8ca119c HEAD
git diff --cached --name-only
git diff --check
test "$(git -C /Users/danielwahnich/workspace/odeya symbolic-ref --short HEAD)" = \
  agent/repository-release
git -C /Users/danielwahnich/workspace/odeya status --short --branch
BASH
```

Expected invariants:

- the active architecture branch is `agent/t0-work-lease-20260716`;
- the canonical worktree remains on `agent/repository-release` with Daniel's
  protected UI/UX changes untouched;
- `main` remains the exact commit recorded above;
- the validated predecessor is an ancestor of `HEAD`;
- no remote is configured;
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
absent from its diff.

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

## Current isolated T0 architecture descendant

The isolated architecture lane descends from the exact validated immediate
predecessor named above. Its current candidate tree contains 112 schemas, 660
shared schema cases, twelve isolated contract suites, 64 canonical vectors,
four metamorphic relations, 23 architecture decisions, and the
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

An independent adversarial review reproduced both blindness claims on isolated
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
disabling every guard in turn and running the suite. Of 69 guards in the five
auditable lifecycle models, **24 are proved and 45 can be removed with the suite
green**. Only AuthorityGrant is complete, at 11 of 11, and only because ADR 0024
and this tranche completed it. `protocol_origin` is 3 of 12, `data_use_cohort` 4
of 11, `work_lease_trace` 2 of 8, `work_lease_record_candidate` 4 of 27.
`identity_map_mutation` is unmeasured rather than proved.

That was subtractive: **PRQ-006, PRQ-007, and PRQ-008 could not close on that
evidence.** Each named a property that no known-bad trace exercised — the
protocol origin materializing version 1 from absence, the data-use grant being
single-use at one atomic commit, and the exact five-state WorkLease vocabulary
that is law 40 of the state model. They were blocked on absent evidence, not on
a decision, which made them autonomous work rather than work waiting on Daniel.

ADR 0026 closed that gap in dependency order. Coverage is now **46 of 69** and
four of five auditable models are guard-complete: `authority_grant_trace` 11/11,
`protocol_origin` 12/12, `data_use_cohort` 11/11, `work_lease_trace` 8/8. Every
guard named by PRQ-006, PRQ-007, and PRQ-008 is proved, each by a retained trace
breaking exactly one field of its model's safe reference and probed to isolate
to a single error. Their closure records are corrected: a stale "blocked on
absent evidence" would mislead as much as the original silence did.

**23 guards remain unproved, all in `work_lease_record_candidate` (4 of 27).**
They are the most consequential left — blocked-candidate status, fabricated
identity, execution-authority claims, the five-role assignment order,
reservation claim/settlement separation, and the refusal to let a lease
transition claim ResourceLedger authority. Several are exactly the refusals that
keep the first slice fail-closed, and none is proved. That model validates a
retained fixture rather than a synthetic subject, so each variant must break a
real candidate record without making it structurally invalid for an unrelated
reason. That is the next lifecycle unit.

The measurement is retained at `architecture/lifecycle-guard-coverage.json`,
reproduced by `scripts/audit_lifecycle_guard_coverage.py` (~90s), and gated
cheaply by `scripts/validate_lifecycle_guard_coverage.py` in the default
validator. The record is pinned to the exact checker digest, so changing the
checker forces its guards to be re-proved. Both halves of the ratchet were
confirmed to fire. Do not hand-edit that record; regenerate it, and note that it
is untracked until committed, so `git checkout` cannot restore it.

Extend the same audit to `schema_contract_errors`, which the harness cannot
currently reach.

Three further follow-ons are open. Six suites still assert refusal
without attribution across 229 known-bad cases — `cognitive-contracts` (107),
`projection-contracts` (37), `constitutional-construction` (29),
`first-slice-resolution` (21), `mathematical-contracts` (19), and
`architecture-review` (16). They are not shown to be blind; they cannot
currently distinguish a guard firing from an incidental refusal, which is the
condition that made lifecycle closure blind, and they should be audited by
mutation rather than by inspection. Separately, refusal attribution now has five
spellings across the suites and should converge on one exact vocabulary.

Read the tranche's convergence honestly. Across this tranche the canonical
profile audit moved from 675 to 668 unscoped digest fields, 118 to 122
unprofiled date-time paths, 233 to 236 nonconformant fixture timestamps, 62 to
61 number findings, and left 56 divergent common definitions and 11 unpinned
profile bindings unchanged. Zero of the twelve PRQ findings are closed and
`profile_status` remains `blocked`, while the schema count grew from 100 to 112.
The added candidates are correctly evidenced and T0 issues no immutable member
by design, so this is not a discipline failure. It does mean the tranche is
additive and that PRQ-001 terminates in Daniel's profile decision, which no
session can self-close. The highest-value remaining autonomous work is
therefore the profile-independent findings and the evidence-quality audit above,
plus reducing the profile decision to an exact decidable package rather than
1,154 raw findings.

The next exact identity unit must disposition the retained canonical migration
findings into immutable legacy resources versus explicitly reissued candidate
resources, without same-ID mutation. Only after accountable review and Daniel's
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
cd /Users/danielwahnich/workspace/odeya-t0-work-lease
source scripts/ci/sanitize-git-environment.sh
commit="$(git rev-parse HEAD)"
evidence="/Users/danielwahnich/workspace/odeya-release-evidence/$commit"
test ! -e "$evidence"
bash scripts/ci/rehearse-fresh-clone.sh \
  "$commit" \
  /Users/danielwahnich/workspace/odeya-t0-work-lease \
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

The rehearsal must end with a nineteen-file manifest bound to the exact
`subject_commit`. Inspect the nested manifest and Gitleaks logs. Never reuse an
earlier commit's evidence or treat a local source rehearsal as remote-main
proof.

## Current hard boundary

Gate A remains blocked. No executable research engine, production UI,
infrastructure, deployment, DNS change, domain purchase, provider or MCP
integration, paid compute, model admission, mission-data import, publication,
public repository, remote creation, or remote push is authorized.

The allowed work is architecture evidence: schemas, contracts, decisions,
threat models, mathematical and physical specifications, adversarial fixtures,
bounded formal models, independent architecture-time implementations, review
records, and repository-release validation. Gate B permits only separately
authorized disposable probes after Gate A. Gate C is required before one
bounded runtime increment.

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

## Next architecture mission, in dependency order

1. Complete T0 by closing PRQ-001–PRQ-010. ADR 0020 freezes the exact
   nonrecursive canonical-profile candidate parameters, 21 current digest
   domains, future profile-reference shape, and eight version axes for review,
   while ADR 0021 freezes the first nonrecursive WorkIntent semantic-core and
   external binding candidate. ADR 0022 retains the three immutable
   predecessors and adds exact side-by-side WorkIntent 0.2, canonical WorkLease
   0.2, and WorkContract 0.3 successor resources plus bounded lineage. None is
   admitted. ADR 0023 adds WorkIntent 0.3 with exact raw source/planning
   candidates and exact output-schema bytes while refusing to relabel raw
   hashes as canonical identity. Disposition the retained migration findings,
   obtain the required profile review/decision, and reissue profile-bound target
   resources before any canonical digest. Keep admission, assignment, lease,
   dispatch, and runtime blocked. Then resolve or explicitly version the retained
   migration findings; close grant lifecycle, protocol origin, and data-use
   authority contradictions; bind schema, payload, event, member, and snapshot
   identities; separate core/evidence/seal/attestation subjects; and retain
   typed blocked-construction receipts. The exact
   `canonical-work-lease:0.1.0` resource and its 0.2 successor are present only
   as unissued, identity-unresolved candidates; T0 must promote a later exact
   identity through canonical profile, member/reducer, and accountable-review evidence, then
   resolve C5/PRQ-009 through the prospective non-authoritative
   WorkIntent/WorkContract and complete assignment-cohort prerequisites.
   That reissue must also close `C5-WORK-LEASE-RELEASE-CLAIM-001`: release
   retains the reservation claimed at attempt start for separate ResourceLedger
   settlement; lease termination cannot erase or settle that claim.
2. Only after all T0 evidence and exact schema/registry identities pass,
   construct and prove the T1 AuthorityAssignment vertical contract.
3. Complete the exact 42 payload schemas, 43 command records, 60 event records,
   25 state/aggregate subjects, and 25 reducer records without changing the
   retained first-slice boundary by implication.
4. Construct one digest-coherent registry/root/C0/checkpoint/witness/P0 and
   inactive activation-candidate chain.
5. Produce two non-sharing architecture-time reference reducer implementations,
   fixture harnesses, and two independently isolated scientific verifier paths.
   They are design evidence, not engine runtime.
6. Retain replay, interruption, recovery, correction fanout, resource and
   authority race, proof-mission refusal, and rights-settled import evidence.
7. Close canonical migration findings and obtain accountable statistical,
   physical/metrology/VVUQ/safety, security/privacy, distributed-systems, and
   accessibility reviews.
8. Produce one immutable candidate manifest and clean commit for Daniel's
   exact-byte accept, reject, or amend decision.
9. Only after Gate A and separate authority: create the private canonical
   remote, reproduce remote `main`, authorize any Gate B probes, and later ask
   for one bounded Gate C implementation increment.

Remote activation additionally requires explicit operator-approved owner,
repository name, private visibility, credential-free canonical URL, exact
candidate commit, expected `main` ref, and canonical-source digest. Never infer
those values from domain ownership, a local directory name, an investor plan,
or an available GitHub account.

Do not skip forward because a model appears capable, a domain becomes
available, an investor asks, or a deadline feels important. Pressure is handled
by making the next dependency smaller and more falsifiable, not by weakening
the gate.

## Definition of a proper continuation handoff

Before ending a future session:

1. preserve all work owned by other lanes;
2. inspect the complete diff and stage only the declared scope;
3. validate the staged or committed exact tree, not a convenient mixed
   worktree;
4. create a scoped local commit with an intentional message;
5. rerun the exact-commit fresh-clone rehearsal when release bytes changed;
6. record the branch, commit, tree, evidence location, checks, open blockers,
   and absence of remote authority;
7. update this handoff when mission state or decisions materially change; and
8. leave every unsupported claim and incomplete item explicit.

The standard is not that the next session feels confident. The standard is
that it can recover identity, reproduce evidence, see every boundary, and know
the next safe action without trusting the previous session's memory.
