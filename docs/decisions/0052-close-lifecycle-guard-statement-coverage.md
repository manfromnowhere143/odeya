# ADR 0052: Close lifecycle guard statement coverage at 160 of 160

- Status: Executed by measurement; not condition coverage, not Gate A
  acceptance
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: every guard in every auditable lifecycle model now has a
  known-bad proof that it fires; the guard-coverage record regenerates to
  full statement coverage from the exact suite bytes

## The gap

After ADR 0031 the coverage record stood at 111 of 160, with every
unproved guard in `schema_contract_errors` (15 of 64). The unproved set
was not peripheral: it included the WorkLease release/claimed-reservation
blocker that PRQ-009 turns on, the canonical WorkLease candidate's entire
null/false authority boundary (fabricated profile, fabricated digest,
claimed execution authority), the protocol absence-origin bindings, and
the data-use cohort order. Any of these could have been weakened to
`pass` with the suite green.

## The third recurrence of the closed-vocabulary defect

Thirty-seven of the forty-nine missing proofs needed only cases written
against the existing `identity|schema|inventory` mutation targets. The
remaining twelve were unprovable by construction: their guards read
resources the model loads itself — the canonical WorkLease schema bytes,
the module-dependency manifest, and the repository-wide defining-path
scan. A mutation vocabulary that cannot reach an input silently bounds
what evidence can exist; ADR 0028 fixed this for
`work_lease_record_candidate`, ADR 0031 for the audit targets, and this
is the same defect a third time.

The correction is the same shape: three new injection targets
(`work_lease_schema`, `module_manifest`, `defining_paths`) behind the
one bounded replace already in force. `schema_contract_errors` accepts
the three as optional inputs defaulting to the exact on-disk resources
and, for the paths, the real repository scan; only a case that mutates a
target injects a substitute, so the safe reference still exercises the
real scan and real bytes.

## The evidence

Forty-nine adversarial cases were added, exactly one per unproved guard,
each declaring `expected_refusal_contains` bound to its own guard's
message. Every case was dry-run against the pre-change bytes to confirm
it fires its declared guard before being retained. The suite holds 182
cases: 14 safe references and 168 known-bad, all attributed.

Re-measurement — never hand-editing — regenerated
`architecture/lifecycle-guard-coverage.json`: **160 of 160 guards
proved**, all ten auditable models complete, `schema_contract_errors` at
64 of 64. The denominator did not move: the suite changes add no new
refusal construct, and `discover()` was not extended because nothing new
requires it.

## Cost

The added cases made each suite run walk the repository and re-parse the
ResearchEvent schema once per mutation case — 7.8 seconds per run, which
the audit multiplies by 161. The suite now caches file text and bytes
per process and performs one defining-path scan per process; a mutation
mutates the parsed object, never the cached text, so case isolation is
unchanged. A suite run is 0.64 seconds with all 182 cases and the full
audit re-measures in under a minute — faster than before the tranche,
with 49 more cases.

## Boundary

This is statement coverage, and ADR 0030's retraction stands in full: a
proved verdict means the refusal statement is reachable, never that each
condition inside it is exercised. Condition-level mutation — the MC/DC
question — remains the next, strictly larger audit. Coverage is also not
correctness: every guard is shown to fire, none is shown to enforce the
right rule. The denominator remains only as honest as `discover()`, and
the six suites holding 229 unattributed known-bad refusals remain
unaudited. The canonicalization profile remains unissued, every
null/false authority boundary is retained, and nothing here is Gate A
acceptance, an admitted member, or an independently reproduced verdict.
