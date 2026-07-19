# Odeya Session Handoff

Status: canonical recovery entrypoint for the current Odeya architecture and
repository-release mission. Last updated 2026-07-19, Asia/Jerusalem. This is a
handoff contract, not Gate A acceptance, implementation authorization, or
scientific evidence; repository-publication authority comes only from the
named decisions and release contract.

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
  leave the machine; it is finished when every remote workflow on the pushed
  commit is green, verified. Publish only through
  `scripts/ci/push-rehearsed-head.sh`, guarded by the `.githooks/pre-push`
  hook, and never with a plain `git push`. This rule was written, then broken
  the same day by its author reading a formal model's "Finished" line as the
  rehearsal's — so it is now a gate, not a memory (ADR 0072, 0075).

If a decision optimizes the number at the cost of the truth of the number,
you have already failed, no matter how green the check. Slow is smooth and
smooth is fast: land verified increments, prove each one, and let the
fresh-clone rehearsal catch what your convenient local environment hides — it
has caught fabricated evidence, bypassed gates, and three separate bugs in a
single audit instrument, every time before a number reached the record.

## What this lane established, and where to put pressure next

The migration wave is closed at audit zero and the profile is unissued by
design; the section below on the T0 descendant carries the exact history. The
evidence-quality lane is the live work, and its shape is now known:

- **Guard coverage has explicit denominators, not whole-repository coverage.**
  The lifecycle checker has dedicated statement (178/185) and condition
  (100/103) audits; the generalized `audit_suite_guard_coverage.py` measures
  twelve declared isolated contract-checker subjects, at 247 of 635 refusal
  statements proved. Central architecture/release gates—including the PRQ-009
  assignment-order checker—are outside that denominator and must carry their
  own pinned known-bad self-tests. The 388 open isolated-suite guards are
  categorized by exact closure method in
  `docs/GUARD_COVERAGE_CLOSURE_PLAN.md`. Three closure
  patterns are proven and mechanical: harness self-tests (ADR 0080/0081),
  meta-proofs for the attribution self-tests (ADR 0083, now complete across all
  six), and the artifact-mutation vocabulary for once-loaded records (ADR 0082,
  proven on the first-slice inventory).
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
- Active correction worktree:
  `/Users/danielwahnich/workspace/odeya-cross-program-evidence-extraction-20260719`
- Active correction branch:
  `agent/cross-program-evidence-extraction-20260719`
- Active correction-tranche base and current published checkpoint:
  `a363d535ef4371482e430935477258f1128d0960`
- Active correction-tranche base/published-checkpoint tree:
  `e6543c357b707c67cbc7b7e4ad70fd3c46d28eb3`
- Canonical remote: `https://github.com/manfromnowhere143/odeya` (public;
  created 2026-07-17 under ADR 0047; default branch `main`)
- Measured remote state on 2026-07-19: `main` resolved to
  `a363d535ef4371482e430935477258f1128d0960`; all three workflow families and
  all nine required jobs were green for that commit. Secret scanning and push
  protection were enabled; Dependabot security updates were disabled; no
  repository ruleset existed; and `main` was not protected.
- Retained remote-main evidence:
  `/Users/danielwahnich/workspace/odeya-release-evidence/remote-main-a363d535ef4371482e430935477258f1128d0960`;
  the local/remote invariant-profile comparison receipt is
  `/Users/danielwahnich/workspace/odeya-release-evidence/remote-main-comparison-a363d535ef4371482e430935477258f1128d0960.json`
  with SHA-256
  `3d1e9567aef28b46c9b717e281bf2286fa67fc865a12e92d52e1c3deaaf802fd`.
- Repository visibility, creation, and evidence-gated architecture-publication
  authority: granted under ADR 0045 and ADR 0047 and reconciled by ADR 0087.
- Runtime, deployment, external-effect, and Gate A authority: not granted

This committed file cannot contain the hash of the commit that contains it
without recursion. The active branch `HEAD` is therefore the rehearsal subject
to resolve, never a hash copied from chat. It becomes a validated local
release-candidate subject only when the current `HEAD`, its tree, the checked-out
branch, and a fresh-clone evidence manifest agree.

Run first:

```bash
bash -euo pipefail <<'BASH'
cd /Users/danielwahnich/workspace/odeya-cross-program-evidence-extraction-20260719
source scripts/ci/sanitize-git-environment.sh
git status --short --branch
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git symbolic-ref --short HEAD
git fetch --quiet origin main
git rev-parse origin/main
git remote -v
git log --oneline --decorate -5
test "$(git symbolic-ref --short HEAD)" = \
  agent/cross-program-evidence-extraction-20260719
test "$(git remote)" = origin
test "$(git remote get-url origin)" = \
  https://github.com/manfromnowhere143/odeya.git
git merge-base --is-ancestor \
  a363d535ef4371482e430935477258f1128d0960 origin/main
git merge-base --is-ancestor origin/main HEAD
git diff --cached --name-only
git diff --check
test "$(git -C /Users/danielwahnich/workspace/odeya symbolic-ref --short HEAD)" = \
  agent/repository-release
git -C /Users/danielwahnich/workspace/odeya status --short --branch
BASH
```

Expected invariants:

- the active correction branch is
  `agent/cross-program-evidence-extraction-20260719`;
- the canonical worktree remains on `agent/repository-release` with Daniel's
  protected UI/UX changes untouched;
- the exact published correction checkpoint remains an ancestor of public
  `origin/main`; an unexpected rewind or replacement fails recovery;
- public `origin/main` remains an ancestor of the active `HEAD`, so any local
  candidate is a fast-forward rather than a divergent history;
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
absent from its diff.

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

Two enforcement facts matter, both established by independent review after this
lane published the opposite. The cheap gate
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

**DECLARED ISOLATED-SUITE GUARD COVERAGE IS 247/635, WITH 388
UNPROVED.** The physical-verification correction added eight measured guards
and eight proofs, so the open residue stayed 388. ADR 0080 closed three former
zero-coverage suites by in-harness self-test:
work-identity-successor-cohort 0→13/19, work-intent-identity-candidate
0→12/20, and canonical-profile-candidate 0→9/18. ADR 0081 moved
command-identity to 8/20; ADR 0082 proved the artifact-mutation vocabulary;
ADR 0083 made the six attribution meta-proofs load-bearing. The exact current
per-suite inventory is in `architecture/suite-guard-coverage.json`, and the
388-open closure strategy is in `docs/GUARD_COVERAGE_CLOSURE_PLAN.md`.
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
four independent fresh-context refuters attacked the wave; ledger lineage
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
cd /Users/danielwahnich/workspace/odeya-cross-program-evidence-extraction-20260719
source scripts/ci/sanitize-git-environment.sh
commit="$(git rev-parse HEAD)"
evidence="/Users/danielwahnich/workspace/odeya-release-evidence/$commit"
test ! -e "$evidence"
bash scripts/ci/rehearse-fresh-clone.sh \
  "$commit" \
  /Users/danielwahnich/workspace/odeya-cross-program-evidence-extraction-20260719 \
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

## Next architecture mission, in dependency order

1. Preserve the completed 2026-07-19 correction boundary before extending T0:
   public-repository operational truth is reconciled; the PRQ-009 contract now
   requires an atomic assignment to create the worker/grant/lease/reservation
   cohort before a derived WorkContract and a separate attempt start; the
   physical-verification semantic false positive is refused by typed known-bad
   cases; undeclared executable surfaces fail closed; and exact rehearsals use
   isolated mutable tool state with the formal checker bound to the jar that
   rehearsal verified. These corrections remain architecture evidence and do
   not resolve the underlying profile identities or accept Gate A.
2. Complete T0 by closing PRQ-001–PRQ-010 and PRQ-013. The
   canonical-profile migration audit is mechanically clear, but profile
   issuance, the HumanDecisionAssurance identity/wrapper and consumer
   migration, accountable independent review, exact member/reducer/root
   identities, and the remaining prerequisite determinations stay open. Keep
   admission, assignment, human-only approval, lease, dispatch, and runtime
   blocked. Resolve `C5-WORK-LEASE-RELEASE-CLAIM-001`: release retains the
   reservation claimed at attempt start for separate ResourceLedger
   settlement; lease termination cannot erase or settle that claim.
3. Only after all T0 evidence, PRQ-013, and exact schema/registry identities
   pass, construct and prove the T1 AuthorityAssignment vertical contract.
4. Complete the exact 42 payload schemas, 43 command records, 60 event records,
   25 state/aggregate subjects, and 25 reducer records without changing the
   retained first-slice boundary by implication.
5. Construct one digest-coherent registry/root/C0/checkpoint/witness/P0 and
   inactive activation-candidate chain.
6. Produce two non-sharing architecture-time reference reducer implementations,
   fixture harnesses, and two independently isolated scientific verifier paths.
   They are design evidence, not engine runtime.
7. Retain replay, interruption, recovery, correction fanout, resource and
   authority race, proof-mission refusal, and rights-settled import evidence.
8. Obtain accountable statistical,
   physical/metrology/VVUQ/safety, security/privacy, distributed-systems, and
   accessibility reviews.
9. Produce one immutable candidate manifest and clean commit for Daniel's
   exact-byte accept, reject, or amend decision.
10. Only after Gate A and separate authority: authorize any Gate B probes and
    later ask for one bounded Gate C implementation increment. The existing
    public architecture remote is not that authority.

Every architecture publication must bind the operator-approved public
repository identity, exact candidate commit and tree, expected `main` ref,
canonical-source digest, retained rehearsal evidence, and observed remote
checks. The local pre-push hook is a workstation control, not server-side
branch protection. As measured on 2026-07-19, the missing repository ruleset
and disabled Dependabot security updates remain explicit account-side
governance work; neither may be claimed complete without fresh observation.

Do not skip forward because a model appears capable, a domain becomes
available, an investor asks, or a deadline feels important. Pressure is handled
by making the next dependency smaller and more falsifiable, not by weakening
the gate.

## The published surface is part of the evidence

**A `.githooks/pre-push` hook refuses any push to `main` lacking evidence
bound to the pushed SHA; run `git config core.hooksPath .githooks` in
every clone, since the hook is local configuration and a fresh clone has
no protection without it (ADR 0075). Publish through
`scripts/ci/push-rehearsed-head.sh`**, and audit
history with `scripts/ci/audit-publication-evidence.py <range>`: this
session's 24 published commits all carry evidence bound to their exact
SHA, while nine older commits on the branch carry none (ADR 0074). It refuses
to push a commit that has no rehearsal evidence bound to its exact SHA, a
dirty worktree, or a non-fast-forward head. This exists because the law
below was broken the same day it was written: a session pushed while the
rehearsal was still running, mistaking a formal model's completion line
for the rehearsal's. That rehearsal passed, which is luck, not process
(ADR 0072).

A push is not complete when the bytes leave this machine. It is complete
when every remote workflow on the canonical repository reports green for
the pushed head. After every push, verify with `gh run list` (or watch
the head commit's checks) and treat a red remote check exactly like a
failed local gate: stop, diagnose from the workflow log, fix or re-pin
lawfully, and push the correction before any further work. This law
exists because seven commits were once published with the remote
Foundation workflow red while every local rehearsal was green — the
CI-only contract-profile pins had no local reader. The partition gate now
runs in the default validator and in the rehearsal, but tooling can only
cover known gaps: the operator's public surface shows the truth of the
head commit, and no session may leave it red, or unverified, at handoff.

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
