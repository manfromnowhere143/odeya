# Node.js HDA successor evaluator

Status: architecture-only, independently authored conformance evaluator. It is
not a runtime resolver, policy authority, approval, or real-ceremony result.

The evaluator requires exactly Node.js 24.18.0, uses no network access or
third-party dependency, and reads only the expectation-free vector corpus,
the candidate ruleset, and the candidate resolver profile named on the
command line. It refuses `cases.json` and peer implementation paths.

```text
node --disable-proto=throw src/cli.mjs \
  --vectors ../vectors.json \
  --ruleset ../../../architecture/human-decision-assurance-individual-eligibility-ruleset-v2-candidate.json \
  --resolver ../../../architecture/human-decision-assurance-content-address-resolver-profile-v1-candidate.json \
  --vector-id safe-complete-eligible
```

One deterministic JSON document is written to standard output. Diagnostics
and refusals are written to standard error with a nonzero exit status.
