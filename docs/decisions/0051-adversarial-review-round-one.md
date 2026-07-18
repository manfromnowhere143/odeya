# ADR 0051: Independent adversarial review of the executed wave, round one

- Status: Review executed and responded; not Gate A acceptance
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity, security
- Gate effect: hardens four audit exemption surfaces with both-direction
  proofs, extends the frozen vocabularies to the measured truth, renames
  one vocabulary name collision, and completes five legacy annotations;
  the audit remains at zero under the strengthened gates

## The review

The wave's author is disqualified from certifying it (law 4). Four
independent fresh-context reviewers, each briefed to refute one surface
and to default to refuted under uncertainty, attacked the executed wave:

1. **Ledger lineage — survived.** All 98 reissue rows and 14 new-schema
   candidates verified byte-for-byte against the checkpoint commit; counts
   recomputed independently to exact agreement; zero same-identity
   mutations; zero deletions; zero duplicate identities. The reviewer
   proved its own verifier detects tampering before trusting its pass.
2. **Trap integrity — survived.** All 457 adversarial schema cases start
   from clean bases, apply cleanly, and refuse; for every disjoint-path
   refusal the error-path content was proven byte-identical to the clean
   base, eliminating incidental-corruption vacuousness; the lifecycle
   harness binds every reject to its declared guard, and ten sampled
   known-bads fire on exactly the declared wrongness.
3. **Detector exemptions — refuted, four counterexamples confirmed.** An
   empty or garbage digest-scope annotation silenced the unscoped finding;
   a governed decimal accepted contentless unit and precision members; a
   profile pin counted on a member no instance was required to carry, a
   blind spot baked into the self-test's own positive proof; and the
   vocabulary gate was dodged by renamed and inline enums.
4. **Wave semantics — four of five points survived; the vocabularies were
   refuted.** No annotation invents a domain (749 checked); every governed
   semantic type is registered (136 checked); the negative-zero pattern is
   byte-identical everywhere; and the acceptance record's nine original
   class decisions are bit-identical to their first commit, the only later
   change being the pure append of the construction decision. But the
   frozen vocabularies were not the true union: inline sites carried three
   more claim types and two more scientific outcomes — including
   `not_adjudicated`, exactly the state missing-is-never-zero demands —
   and one schema used `operation` for an unrelated graph vocabulary.

## The response

- The digest-scope gate validates content: a declared kind, a subject or
  domain or explicit resolution rule, and a status — an empty or garbage
  annotation counts as unscoped again. Five legacy annotations lacking a
  kind or status were completed, and one blanket completion was itself
  corrected when the lifecycle pins caught three semantically wrong kinds.
- Governed decimals require constraining unit and precision declarations;
  a contentless member keeps the leaf counting.
- A profile pin counts only when the pinning member is required; the
  self-test's positive proof now requires the member and a negative proof
  keeps optional-member pins unpinned. The engine-contract-root pin moved
  to the component's real identifying member after the first fix demanded
  a member the closed base forbids — caught by the schema cases in one run.
- The vocabulary gate covers definitions whose names carry the family
  token, family-named properties, inline enums, and consts, with proofs in
  both directions. The vocabularies extended to the measured truth
  (claim_type 17, scientific_outcome 28) and `epistemic-graph-delta`'s
  colliding field renamed to `graph_operation` so the family name stays
  unambiguous.

## Boundary

The reviewers were independent-context model sessions instructed to
refute, not human reviewers; their scripts and full verdicts are retained.
The profile remains unissued: the owner's exact-byte decision is still the
only act that can freeze it.
