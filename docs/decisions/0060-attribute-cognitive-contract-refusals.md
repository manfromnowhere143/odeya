# ADR 0060: Attribute every cognitive-contract refusal; the six-suite blindness is closed

- Status: Executed; last of the six unattributed suites
- Date: 2026-07-18
- Decision owners: architecture review, cognitive contracts
- Gate effect: every known-bad case in every isolated contract suite now
  binds the exact constraint that must refuse it; no suite in this
  repository can any longer count an incidental refusal as proof

## The measure, corrected a third time

Carried as 107 unattributed cases; measured 119 — 107 structurally
known-bad and 12 semantically known-bad. Every one of the six suites
under-counted between its first citation and its attribution
(mathematical 19→37, projection 37→54, cognitive 107→119), because the
carried figures counted cases, not refusal domains.

## The attribution

Structural cases bind instance pointer plus keyword: the sealed-truth
and self-digest bans, the epistemic-graph history-deletion and
version-zero fabrications, the planning-epoch selection laws, the
candidate-artifact evidence-eligibility rules, the model-configuration
authority and data-handling boundaries, the routing dispatch boundary,
the canonical decimal spellings, and the work-intent/work-contract
null-authority boundary each bind their own constraint. Semantic cases
bind the authored checker message. Bindings were chosen from stated
intent; where a mutation cascades (the unidentifiable-promotion and
packing-does-not-fit cases), the binding names the rule the case exists
to prove — the promotion ban, the proposal ban — not the incidental
co-firing.

The binding predicates are shared functions used by both the live loop
and the four-way fail-closed self-test; external negative controls
exercised both domains against the committed suite before retention.

## What this unit closed, and what it did not

With ADRs 0055–0060, all six formerly blind suites — 313 known-bad
cases as now measured — distinguish their intended constraint firing
from an incidental refusal, each with a self-test proving the
attribution gate itself fires on every run. What remains open from this
family: the refusal-attribution vocabulary now has exactly two
spellings — `expected_refusal` (pointer + keyword, jsonschema domains)
and `expected_refusal_contains` / `expected_semantic_refusal_contains`
(message substring, authored-checker domains) — and their convergence
decision is the follow-on unit. Attribution is intent binding, not
mutation coverage: nothing here proves a schema constraint could not be
weakened while still refusing at the declared location, which is the
lifecycle audits' territory and remains unextended to schema-based
suites. Nothing here is authority, admission, or Gate A acceptance.
