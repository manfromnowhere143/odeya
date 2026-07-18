# ADR 0066: Audit the harness that audits, and name where the regress stops

- Status: Executed; closes the last of ADR 0063's surviving weaknesses
  and retracts both headline coverage numbers by measurement
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: the audits now see the suite harness and comprehension
  filters; the harness gains a self-test that makes its hygiene guards
  load-bearing; the residue is enumerated and structurally explained

## The weakness

Round-two review showed the condition denominator missed at least 22
boolean members and proved four of them silently removable — including
the floors that keep the suite from shrinking to nothing and the guards
that require every known-bad case to carry a tag and a declared refusal.
The audits had measured everything except the thing doing the measuring.

## Retraction by measurement

Both denominators were wrong and both headline numbers are retracted:

- statement coverage was published as 161 of 161; the true denominator
  is **181** and the measurement is **172 proved**;
- condition coverage was published as 88 of 89; the true denominator is
  **99** and the measurement is **97 proved**.

Discovery now matches the `failures` accumulator as well as `errors`,
audits `main` and the functions it delegates to, treats comprehension
filters as removable conditions, and counts ternary selectors
explicitly rather than passing over them. This is the fourth time a
denominator in this repository was found by review rather than by the
tool; the pattern is stable enough to state plainly: a denominator is a
claim, and only an outside attempt to break it is evidence.

## Closing what is closable

The harness's hygiene guards cannot be proved by a retained case,
because a malformed case in the retained set would fail the suite. They
are proved instead by a self-test inside the harness — the same pattern
every other suite received in ADR 0055-0061 — which constructs
malformed cases in memory and asserts each is refused by exactly the
guard that must refuse it: a non-string tag, an empty tag, a missing,
non-string, empty, or misdeclared expected refusal, an invalid
expectation, an unknown model, a rejected safe reference, an accepted
known-bad trace, both coverage floors independently, and the tag
mismatch. `main`'s collection path was factored into
`collect_case_failures` so the self-test can drive the whole pipeline,
not only the guards it delegates to.

One defect was committed and caught inside this tranche: the first
version of the collection self-test accepted *any* non-empty result as
evidence, so the coverage failure satisfied the check meant for the
case-failure path — an incidental refusal counted as proof, the exact
defect ADR 0024 named. It is now bound to the specific failure each
path must carry, and the audit confirms the difference.

## Where the regress stops

Nine statements and two conditions remain unproved, and each is
structurally so rather than merely unwritten:

- **Six self-test refusals.** They fire only when a hygiene guard is
  already broken, and a passing suite has none. A self-test of the
  self-test would have the same property one level up. Every gate needs
  a known-bad proof that it fires, and that requirement recurses; it
  must terminate somewhere, and this is the exact place it terminates
  in this suite. Naming the termination point is the honest resolution;
  claiming full coverage would not be.
- **Three clean-tree assertions** in `main` — the statements that
  collect schema, fixture, and case failures on a tree that is clean by
  definition. Their removal is invisible precisely because there is
  nothing to collect; the models they read are exercised through the
  mutation cases instead.
- **`uses != max_uses`**, retained and explained in ADR 0054/0063.
- **`isinstance(layer, dict)`**, a defensive comprehension filter whose
  removal is semantically inert: `nested()` already refuses non-dict
  input, so no reachable case can distinguish its presence.

## Boundary

Coverage is still not correctness. Fourteen condition proofs remain
crash-detected (ADR 0065), the four ternary selectors are counted and
unaudited, structural comparisons remain one condition regardless of
field count, and the subset-semantics rebindability in the
`expected_errors` suites is untouched by this tranche. Nothing here is
an accountable review determination, an admitted member, or Gate A
acceptance.
