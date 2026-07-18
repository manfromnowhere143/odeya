# ADR 0071: Ablation-verified cases for unexercised cross-field rules

- Status: Executed; first reduction of the coverage gap ADR 0070 named
- Date: 2026-07-18
- Decision owners: architecture review, canonical identity
- Gate effect: 112 generated cases, each proven to isolate exactly one
  cross-field rule, plus an eighth architecture-evidence check and a
  rehearsal stage that re-prove every isolation claim

## The gap this begins to close

ADR 0070 recorded the review finding that mattered most: **210 of 286
root-level `if/then` cross-field rules could be deleted with the entire
457-case corpus still green**, overwhelmingly because no case exercised
them at all. Binding a case to a constraint says nothing about whether
any case would notice that constraint disappearing. Attribution was
complete; coverage was thin.

## The standard applied

Every case added here carries its own ablation proof, which is the
standard the review itself established: the case must be **refused with
its rule present and accepted with the rule deleted**. A case that stays
refused after deletion is not isolating that rule, whatever it declares,
and is not retained.

Generation is property-directed rather than hand-written: for each rule,
satisfy the `if` from its own const/enum discriminators, violate the
`then` by the first available constraint — a required field removed, a
const inverted, an enum falsified, a bounded array over- or under-filled
— and then run the two-sided ablation. 112 of 286 rules yielded an
isolable case. The remaining 174 did not: 143 could not be isolated
because satisfying their `if` also trips neighbouring rules, 17 produced
a still-valid instance, 9 could not have their mutation applied, and 5
offered no violable requirement my strategies recognize. Those counts are
reported here rather than rounded away, and closing them needs
instance-minimizing generation, which this tranche does not attempt.

## Enforcement

`scripts/audit_schema_rule_ablation.py` re-runs every declared isolation
— schema with the rule, schema without it — and retains
`architecture/schema-rule-ablation.json`. All 112 isolate.
`scripts/validate_schema_rule_ablation.py` joins the default validator as
the eighth architecture-evidence check, binding the record to exactly the
set of cases that declare a rule and refusing any retained non-isolating
entry; the exact-commit rehearsal re-measures with `--check`, since only
re-measurement binds a record to reality.

The corpus grows 662 to 774 cases, 457 to 569 adversarial. Both pinned
counts drifted and the local pin reader — the fix from this morning's
CI incident — caught them before a commit could form.

## Boundary

This reduces the coverage gap; it does not close it. 174 rules remain
without an isolating case, and rules outside the root-level `if/then`
shape were never in the 286 to begin with. These cases are
machine-generated: they prove a rule is noticed, not that the rule is
*right*, and their names describe the rule's position rather than its
meaning. Nothing here is an accountable review determination, an admitted
member, or Gate A acceptance.
