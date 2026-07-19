# Architecture review schema cases

This package exercises the structural contracts for the independent Gate A
review process described in
[`docs/ARCHITECTURE_REVIEW_PROTOCOL.md`](../../docs/ARCHITECTURE_REVIEW_PROTOCOL.md).

Run the isolated cases with:

```bash
python3 tests/architecture-review/check.py
```

The four base fixtures are deliberately non-accepted:

- the candidate manifest is a draft with incomplete evidence and no signature;
- the architecture finding is open and high severity;
- the lane determination is `unable_to_determine`, with unknown independence
  dimensions and missing evidence; and
- the operator decision is `not_accepted`, remains in architecture, and keeps
  every implementation and external-effect lock closed.

All people, signatures, digests, repositories, evidence, and review activity in
these fixtures are synthetic. They do not identify or impersonate Daniel, an
expert reviewer, an operator acceptance, or a real candidate.

## Structural boundary

JSON Schema can require closed shapes, lane completeness, bounded result
vocabularies, non-acceptance of critical/high limitations, carry-forward
identity fields, and a permanently false Gate A implementation authorization.
It cannot establish that referenced bytes exist, digests match those bytes,
signatures are authentic, a reviewer is competent or independent, eight
determinations actually bind the same manifest digest, finding counts are
truthful, a change-impact analysis is correct, or the operator is Daniel.

Those properties require a deterministic review compiler over dereferenced
artifacts plus accountable human verification. A passing test run is structural
evidence only and never Gate A acceptance.

The structural fixtures also cannot prove the future human-decision assurance
required by [ADR
0089](../../docs/decisions/0089-a-valid-human-signature-is-not-a-human-decision.md).
A declared human principal, valid signature, or well-formed review/approval
artifact remains insufficient while PRQ-013 is unresolved.

## Required semantic known-bad refinements

The [cross-program process-evidence
packet](../../docs/CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md)
adds four provenance-bound cases for the future deterministic review compiler:

- a sibling/source artifact validates while the exact reviewed or bundled
  member omits a required boundary;
- a historical ledger/pointer passes while the canonical current baton names a
  later state;
- a provider request is initiated and then interrupted, leaving completed
  requests and actual spend unknown; and
- session logs are offered as authorship, human intent, approval, independence,
  or scientific-validity evidence instead of bounded operational chronology.

Each case must remain non-accepted. These are refinements of existing identity,
current-state, missingness, authority, and evidence boundaries; the present
schema-only fixtures do not claim to execute them.
