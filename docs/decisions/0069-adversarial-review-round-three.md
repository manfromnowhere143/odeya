# ADR 0069: Independent adversarial review round three; the regress has no terminal turtle

- Status: Review executed and responded; retracts ADR 0066's
  impossibility claim by construction
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: five demonstrated silent weakenings closed, the condition
  audit extended to refusal-determining helpers, and the self-test's own
  refusals made load-bearing by injection

## What was refuted

Independent review attacked ADRs 0064-0068, which had passed every gate
but no outside refutation attempt. Three findings, each demonstrated by
running the suite rather than by argument:

**1. The floors were free.** ADR 0066 claimed the self-test made the
coverage floors load-bearing. It proved only that a floor exists:
probing `(0, 100)` and `(100, 0)` fires for any threshold at or above
one, so the constants 10 and 15 could be lowered to 1 and 1 with the
suite green — the suite shrinking to nothing, undetected, which is the
exact failure the floors exist to prevent. The tag-coverage guard was
proved in one direction only (extras), so its missing-tag half was
silently removable. And the self-test's own refusal matcher collapsed to
`if not observed` with the suite green: the ADR 0024 incidental-refusal
defect, live inside the mechanism built to prevent it.

Response: the floors are pinned at their exact thresholds from both
sides — nine safe cases must refuse and ten must not, fourteen
adversarial must refuse and fifteen must not — tag coverage is probed in
both directions, and the matcher is factored and proved to reject a
non-matching expectation. All four demonstrated weakenings were replayed
against the committed tree and are refused.

**2. A removable conjunct was invisible to both the numerator and the
residue.** The defensive `isinstance` filter on the repository walk that
feeds the canonical defining-path guard could be deleted with the suite
green, and neither audit counted it — including the "counted, not
audited" accounting that exists precisely so nothing is silent. The
condition audit now declares refusal-*determining* helpers (`nested`,
`scan_defining_paths`, `exact_value`, `transition_spec`) alongside the
refusal-*bearing* ones; the denominator grows 99 to 103.

**3. There is no terminal turtle.** ADR 0066 called the self-test's six
refusal statements structurally unprovable and named them the point
where the proof-of-proof regress terminates. Review disproved that by
construction: injecting a blinded collaborator is the same move the
self-test already makes one level down — construct the malformed thing
in memory — applied to a malformed *harness* instead of a malformed
*case*. The reviewer built it and showed the statement becoming
case-attributed.

That construction is now generalized: the self-test takes its evaluator,
coverage function, and collector as injection points, and a meta proof
blinds each in turn and asserts the exact number of refusals it must
produce, so removing any single self-test refusal lowers a count and
fails. Statement coverage moves 172/181 to **178/183**; condition
coverage 97/99 to **100/103**.

## The correction to the claim, not just the code

ADR 0066's error was not the residue; it was calling it impossible. The
regress is unbounded, and every level can be closed by one more
injection point. The honest statement is therefore about cost, not
possibility: **we stop where the next injection buys less than it
costs, and we say where we stopped.**

Where this tranche stops: five statements — the meta proof's own call,
three clean-tree assertions that fire only if a clean tree is dirty, and
the matcher check's refusal — and three conditions: the two ADR 0066
explained plus the newly visible `isinstance(candidate, dict)`, which
would need a deliberately malformed `*.schema.json` in the repository to
fire and cannot be closed without polluting the tree the rest of the
validator guards. Each has a known injection that would close it. None
is claimed impossible.

## Surviving, recorded

A *coordinated* edit still passes in the three exact-inventory suites:
weakening a guard and rebinding the affected case's declared inventory
in the same change is undetected, because no mutation audit exists for
those suites — only lifecycle-closure has one. ADR 0067 did not claim
otherwise; the scope is recorded here. Review also confirmed
`intent_errors` inherited its labels exactly and found no wrong intent
in its sample, with ten cases where the intent field adds nothing beyond
the equality check.

## Boundary

This response was authored by the session under review; the corrections
are verified by re-run gates and replayed attacks, not by confidence.
Coverage remains not correctness. Nothing here is an accountable Gate A
review determination, an admitted member, or acceptance.
