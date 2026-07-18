# ADR 0063: Independent adversarial review of this tranche family, round two

- Status: Review executed and responded; not Gate A acceptance
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity, security
- Gate effect: closes the CI-only-gate failure class at three further
  live members, rewrites the attribution census fail-closed, corrects
  four misbound and one ambiguous binding, retracts half of ADR 0054's
  impossibility claim by retained counterexample (condition coverage now
  88 of 89), and records every surviving weakness explicitly

## The review

The producing session is disqualified from certifying its own tranches
(law 4). Four independent fresh-context reviewers attacked ADR
0052-0062, each briefed to refute one surface and to default to refuted
under uncertainty. Three surfaces were refuted; the strongest artifact
(physical-contracts, ADR 0061) survived its prescribed attack, as did
the projection and constitutional binding sets and the 87/89
reproducibility of the condition record.

## Confirmed refutations and the response

**1. The CI-only gate class was not closed — three further live members.**
`scripts/validate_schema_contracts.py` pinned 112 schemas and a
205/457 case split read by nothing local; three CI jobs run scripts on
a bare interpreter no local gate reproduces; the TLA jar identity lived
in five unreconciled copies. Response: the default validator now reads
the schema pins in-process (a partition change fails before a commit
forms); the release validator gains a bare-interpreter import audit
(every bare-job script and its local imports must be stdlib-only) and a
TLA pin-copy equality check against the lock file, each with an
exercised negative control.

**2. The attribution census was refutable on three fronts.** Its sweep
missed `tests/architecture-schema` — 457 adversarial cases, larger than
the entire certified census; five realistic negative spellings passed
silently and a sixth (a dict-shaped expectation the repository actually
uses elsewhere) crashed the gate; and it certified
`expected_reasons` for command-identity, a field its harness enforces
as a subset satisfiable by a reason that fires unconditionally.
Response: the census registry is now total over case-bearing manifests
— any unregistered manifest with cases fails closed regardless of
spelling; the known-unattributed corpora are registered with reasons
and their 457 negatives are printed, never implied covered;
command-identity is certified on `exact_mismatch_reason_sets`, the
field its harness checks by equality; the self-test covers all three.

**3. Four bindings named a co-fired side effect, not their intent; one
substring was ambiguous.** The active-authority fixture case bound an
incidental list corruption while every authority ban fired unbound —
proven blind by schema ablation; two mathematical cases bound the
near-miss branch's hygiene rule instead of the mutated constraint; one
bound a maximally generic `required`; one substring matched two
reachable guards. All five are rebound to their intent-central
constraint and verified firing.

**4. Half of ADR 0054's impossibility claim was false.** The claimed
invariant `pending_exhaustion ⟺ uses == max_uses` fails in the ⇐
direction at `max_uses: 0`, and the reviewer constructed the trace ADR
0054 demanded: issue, activate, exhaust a zero-use grant — exactly one
disjunct decides. The trace is retained as
`cond-grant-exhaust-zero-use-grant` and condition coverage is
re-measured at **88 of 89**. The ⇒ direction genuinely holds, so
`uses != max_uses` remains unprovable for the reason ADR 0054 gave;
its biconditional claim is corrected here, not silently.

## Surviving weaknesses, recorded rather than resolved

- Thirteen condition proofs rest on interpreter crashes adjacent to the
  removed member; one was shown to flip to silently-removable under a
  behavior-preserving respelling. Crash-detection is detection, but it
  is not durable attributable evidence; per-condition cases for the
  thirteen are open work.
- The condition denominator misses at least 22 boolean members —
  ternaries, guard-shaping `if` tests with no immediate refusal,
  comprehension filters, the `nested()` helper, and the suite harness's
  own failure guards, four of which were shown removable with the suite
  green. Extending discovery is open work, and the harness-guard class
  needs its own audit.
- Eight compound-name cases bind one prong of a multi-prong intent; the
  unbound prongs were shown deletable with the suite green. The proper
  dissolution — one case per prong, as the conjoined release/claim case
  was dissolved — is open work, as is the genericity of the first-slice
  catch-all messages.
- The `expected_errors`/`required_errors` suites enforce declared codes
  as subsets: 35 of 37 cohort bindings could be rebound to an
  incidental co-firing code with the suite green. Exact-set enforcement
  or observed-set inventories are open work; the census gate's output
  now states that binding semantics vary by suite.
- `architecture-schema`'s 457 negatives and the canonicalization
  vectors remain unattributed by design, counted in every census run.

## Boundary

The reviewers were independent-context model sessions instructed to
refute, not human reviewers, and — corrected 2026-07-18 — they shared
the producer's provider, model family, prompt family, harness and human
principal, so they were context-isolated but correlated on five of the
twelve axes `ModelConfigurationRecord` enumerates (see
../REVIEWER_AGENT_PROPOSAL.md), and this response was authored by the
session under review; the corrections are verified by re-run gates, not
by anyone's confidence. Nothing here is an accountable Gate A review
determination, an admitted member, or acceptance of any kind.
