# ADR 0062: The refusal-attribution standard, enforced by census

- Status: Decided and executed; closes the attribution family
- Date: 2026-07-18
- Decision owners: architecture review
- Gate effect: the attribution spellings are frozen as a standard, and a
  seventh architecture-evidence check enforces binding presence by
  sweeping every case manifest — an unknown suite carrying negatives
  fails closed

## The decision

The convergence question was whether the measured seven attribution
spellings should collapse into one vocabulary. Decided: no. The
spellings are domain-exact, not accidental — a jsonschema refusal is
bound by instance pointer plus keyword because those are stable under
the hash-locked validator while message text is not; an
authored-checker refusal is bound by its message because the message is
contract text this repository owns; and the three older spellings
(`expected_errors`, `required_errors`, `expected_reasons`) are retained
where their harnesses already enforce them exactly. Re-spelling
hundreds of proven bindings would churn retained evidence without
strengthening any gate. What was missing was not uniformity but
enforcement: nothing prevented a new suite from shipping unattributed
negatives, and nothing swept the whole tree — which is exactly how
`physical-contracts` stayed blind while a six-suite list was carried
as the frontier.

## The gate

`scripts/validate_refusal_attribution.py` joins the default validator
as the seventh architecture-evidence check. It carries the registry —
each suite's declared binding spelling per refusal domain — and audits
every `tests/*/cases.json` by census: a registered suite's negative
case without its binding fails; a negative case in a domain the
registry declares empty fails; a suite unknown to the registry that
carries negative-looking cases fails; a registered suite whose manifest
disappears fails. Its self-test proves on every run that a stripped
binding and an unregistered negative suite are both refused, and an
external negative control was exercised against the committed tree.
First census: 671 bound negative cases across 14 swept manifests.

The gate checks binding presence and shape only. Each suite's own
harness proves its bindings fire, with its own fail-closed self-test;
this separation is deliberate, so the cheap sweep stays cheap and the
firing proof stays where the refusal engine lives.

## Boundary

Attribution is intent binding, not weakening-mutation coverage; the
lifecycle-style audits remain unextended to schema-based suites. The
registry is a declared list inside a censusing gate: the census finds
unknown suites, but a registry entry pointing at the wrong spelling is
a review matter, as every denominator in this repository is. Nothing
here is admission, authority, or Gate A acceptance.
