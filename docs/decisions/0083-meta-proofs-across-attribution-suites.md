# ADR 0083: Meta-proofs make the attribution self-tests load-bearing

- Status: Executed; roadmap step 1 across four attribution suites
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: the attribution self-tests added in ADR 0055-0061 gain
  meta-proofs, so their own refusal statements are proved load-bearing

## The gap

ADR 0055-0061 gave six suites an attribution self-test that tampers a
retained case both ways and asserts the binding check refuses it. The
generalized audit (ADR 0079) then showed those self-tests' OWN refusal
statements unproved: in a passing suite a self-test refusal never fires,
so removing it is invisible. This is the exact situation the lifecycle
harness was in before ADR 0069's meta-proof.

## The correction

Four suites — projection-contracts, mathematical-contracts,
cognitive-contracts, physical-contracts — gain
`attribution_self_test_meta_proof`. Each blinds the self-test's evaluator
(or its two binding-check functions) so every tamper check fails
unconditionally, and asserts the exact count of distinct refusals, so a
dropped self-test refusal lowers the count and is caught. The self-test
signature gained an injection parameter defaulting to the real function,
the smallest change that makes the meta-proof possible.

Measured by the generalized audit, not asserted:

| suite | before | after |
|---|---|---|
| projection-contracts | 21/77 | 25/79 |
| mathematical-contracts | 21/76 | 25/78 |
| cognitive-contracts | 16/56 | 20/58 |
| physical-contracts | 22/59 | 26/61 |

Repository 219/615 to **235/623**, every proof case-attributed. Each
denominator grew by the meta-proof's own guard, which the audit measures.

## The terminal residue

The meta-proof's own refusal, and the collection `extend` statements,
remain unproved in each suite — the terminal turtles ADR 0069 named. They
close by one more injection level at diminishing value, and stopping here
is the recorded decision, per suite.

## Boundary

Statement reachability of harness guards only. constitutional-construction
and first-slice-resolution carry a differently-shaped invariant self-test
and are the next hygiene targets. Nothing here is an accountable review
determination, an admitted member, or Gate A acceptance.
