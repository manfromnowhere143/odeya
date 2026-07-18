# ADR 0061: A seventh blind suite; physical-contract refusals attributed

- Status: Executed; corrects the six-suite frontier claim by measurement
- Date: 2026-07-18
- Decision owners: architecture review, physical/metrology contracts
- Gate effect: every known-bad physical-contract case binds the exact
  constraint that must refuse it; the suite inventory now carries the
  bindings; four-way fail-closed self-test on every run

## The frontier itself was wrong

The handoff's attribution unit named six suites and 229 cases. A census
taken after closing those six found a seventh suite the list never
contained: `physical-contracts`, with 71 known-bad cases — 53 structural
and 18 semantic — and zero bindings. The six-suite claim was an
enumeration error of exactly the kind this repository's own audits keep
finding: the measurement was only as wide as where it was pointed. The
same census established the true refusal-attribution spelling count:
seven spellings across ten suites with negative cases, not five
(`expected_refusal_contains`, `expected_refusal` + two semantic
variants from ADR 0055-0060, and the pre-existing `expected_errors`,
`required_errors`, and `expected_status`/`expected_reasons` families —
the last three already enforced by their own harnesses).

## The attribution

This suite's cases are authored in code — a typed catalog with bounded
mutators, and a generated `cases.json` inventory the harness requires
to match exactly. The `Case` record gains `expected_refusal` (instance
pointer + keyword) and `expected_semantic` (authored message substring);
all 71 negative catalog entries are annotated from stated intent — the
actuation and self-issued-authority bans, the simulation-as-validation
bans, the VVUQ gate and credibility-vector rules, the metrology
partition laws, the profiled timestamp and decimal spellings — and the
inventory derivation publishes the bindings, so the retained
`cases.json` carries them and drift is refused by the existing
inventory equality gate. Shared binding predicates feed the live loop
and the four-way self-test; an external negative control was exercised
against the committed suite before retention.

## Boundary

With this ADR every suite carrying negative cases either binds each
case to its intended constraint (eight suites) or was already bound
under its own earlier spelling (`work-identity-successor-cohort`,
`work-intent-identity-candidate`, `canonical-profile-candidate`,
`command-identity-contracts`). The remaining follow-on is one recorded
convergence decision over the measured seven-spelling census — one
vocabulary, or an explicitly standardized set with a gate that refuses
a new suite shipping unattributed negatives. Any future claim that the
attribution frontier is closed must cite a census, not a list carried
forward. Nothing here is scientific authority, admission, or Gate A
acceptance.
