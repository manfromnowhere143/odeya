# Proposal: a contracted refutation worker for every research mission

Status: proposal for the operator's decision. Not an accepted contract, not
an authority grant, not Gate A acceptance. Written 2026-07-18 after four
ad-hoc review rounds exposed both the value of the pattern and a defect in
how this session ran it.

## The question

Four times today an independent-context session was briefed to refute a
tranche of work, and four times it found real defects — a fabricated
`"passed"` inside the evidence writer, a publication gate that plain
`git push` ignored, a meta-proof that counted call sites instead of
guards, and the proof that the mutation audits cannot gate what they
measure. The pattern repeats in every mission. Should it be a contracted
worker rather than an improvisation?

Yes — with one boundary that is not negotiable, and one admission about
how this session ran it.

## The admission

Odeya's `ModelConfigurationRecord` already carries a twelve-axis
`correlation_profile`: provider, model family, weights lineage, training
data lineage, implementation harness, prompt family, toolchain, source
corpus, human principal, organization, incentive — with
`independence_conclusion_permitted` fixed to `false`.

Every reviewer this session was the same provider, same model family,
same prompt family, same harness, same human principal. They were
**context-isolated, not independent**, and the ADRs called them
"independent adversarial reviewers" without declaring a single
correlation axis. The architecture had already anticipated exactly this
error and the sessions did not honour it. Any contracted worker must emit
its correlation profile as evidence, and no report may describe itself as
independent along an axis it shares.

## The boundary

`review-determination.schema.json` fixes `reviewer.principal_type` to
`human`, alongside verified identity, a competence disposition, declared
conflicts, prior access, and an authentication binding. A refutation
worker therefore **produces evidence and never issues determinations**.
It can kill a claim — refutation is cheap to check and expensive to fake.
It cannot bless one. This is law 4 in the specific: no agent verifies its
own claim, and no model signs for a human.

## What the 2026 literature adds

Independent work converges on the same shape and supplies details worth
adopting.

**Falsification-first, never consensus.** Refute-or-Promote forbids
convergence-by-debate and gates candidates through stacked adversarial
stages with published kill rates (~63% at the first stage, ~42% of
survivors at the second, 79% aggregate). Promotion requires that *no*
adversary produce a grounded refutation — not that a majority approve.

**Unanimity is a low-signal event.** Their sharpest result: eighty
reviewers unanimously endorsed a Bleichenbacher padding oracle that did
not exist, killed only by one empirical test. Agents converge on shared
training priors, not on ground truth. A worker that reports agreement is
reporting correlation until an experiment says otherwise.

**Cross-family critique catches what same-family review cannot.** A
different model family found correctness defects in ~16% of fixes its own
family had approved. This is the axis this session omitted entirely.

**Empirical validation is mandatory, and can self-contaminate.** No
candidate advances on argument alone; but one of their proofs measured
its own nonce computation rather than the library, producing a false
confirmation. An experiment must be shown to observe the system, not the
harness.

**The pipeline is strong at killing and weak at resurrecting.** A real
integer overflow was unanimously killed and recovered only by human
override. False negatives are the residual risk and they land on the
operator.

**Reference-free judging measures plausibility, not correctness.**
Improvements measured by a judge with no independent signal are suspect
until checked against something the candidate's author cannot regenerate.
That is precisely this session's deepest finding, arrived at
independently: `--check` compares bytes against a record that `--write`
regenerates.

## Proposed shape, in Odeya's own terms

1. **A typed refutation contract.** The worker receives an exact subject
   (commit, artifact digests, claim under test), a kill mandate, and a
   bounded budget. It returns typed findings — each with the experiment
   run, the command, the observed output, and a verdict of refuted or
   survived — never a determination.
2. **Correlation disclosure as a precondition.** Every report carries the
   worker's `correlation_profile` against the producer's. A report that
   shares provider, family, prompt family and harness declares itself
   correlated on four axes and is weighted accordingly by the human, not
   by itself.
3. **A required cross-family stage** where a second family is available,
   because same-family agreement is the documented blind spot.
4. **Empirical gate with an anti-contamination check**: every claimed
   refutation must name what it observed and show the observation could
   fail — the same both-directions discipline the suites already use.
5. **Findings are events, not verdicts.** Retain refuted and survived
   alike; negative evidence is first-class (law 6). A surviving surface
   is recorded as surviving *that attack*, never as correct.
6. **The human signs, or nothing is signed.** The worker's output is an
   input to a determination whose reviewer is human by schema.

## What this does not solve

It does not close the independence problem — a worker under the same
operator, prompted by the same family, sharing an incentive, is
correlated no matter how isolated its context. It does not resurrect
false negatives; that has landed on the human in every published study
and it landed on the reviewers here too. And it cannot make a regenerable
record into a gate: an independent baseline requires someone outside the
producing loop, which is the same shape as the profile decision.

The honest claim is narrow and worth having: **contracted refutation
makes the cheap half of verification systematic and its correlation
visible, and leaves the accountable half exactly where the architecture
already put it.**

## Sources

- Refute-or-Promote: Adversarial Stage-Gated Multi-Agent Review —
  https://arxiv.org/html/2604.19049
- LLMs Gaming Verifiers: RLVR can Lead to Reward Hacking —
  https://arxiv.org/abs/2604.15149
- More Convincing, Not More Correct: Self-Play Reward Hacking of
  Reference-Free LLM Judges — https://arxiv.org/pdf/2607.05904
- Multi-LLM Agents Architecture for Claim Verification —
  https://ceur-ws.org/Vol-3962/paper20.pdf
