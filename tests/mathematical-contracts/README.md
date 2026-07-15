# Mathematical contract vectors

Run from the repository root:

```bash
python3 tests/mathematical-contracts/check.py
```

The suite validates the two candidate contracts and the optional compatibility
bindings in `ProtocolSnapshot` and `MetricResult`. It then applies bounded local
semantic checks for exact identity equality, decimal interval algebra, null
inclusion, equivalence/noninferiority margins, sequential looks, missingness
counts, data-role separation, recomputation consequences, and physical-world
provenance.

Pinned shared-manifest probes:

- `EstimandContract`: fixture
  `tests/mathematical-contracts/fixtures/estimand.descriptive.valid.json`;
  minimal invalid mutation replaces `/decision_rule/unknown_treated_as_zero`
  with `true`.
- `ScientificResultEnvelope`: fixture
  `tests/mathematical-contracts/fixtures/scientific-result.sentinel-inconclusive.valid.json`;
  minimal invalid mutation replaces `/recorded_at` with
  `2026-07-15T12:30:00Z` (missing the required six fractional digits).

Passing is not registry admission, scientific truth, physical validation,
claim authority, or Gate A acceptance.
