# ADR 0031: Audit every refusal-bearing function and harden the README gate

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-17
- Decision owners: lifecycle closure, architecture review, security
- Gate effect: restates guard coverage as 97 of 156 over all nine
  refusal-bearing checker functions, closes the tail-review findings, and
  hardens the README checkpoint gate; closes no PRQ finding and accepts no
  Gate A row

## Context

Independent review of this session's unreviewed tail confirmed the mechanics of
all four commits under attack and broke three published claims, every one in the
flattering direction. This decision closes all three, plus two smaller defects
the same review surfaced.

## Findings and corrections

**The README gate was silently defeatable.** It validated the first regex match
and never counted matches, so a second checkpoint sentence — or a correct decoy
placed before a corrupted real one — passed unnoticed. The gate now permits
exactly one checkpoint sentence and rejects on any other count; both
demonstrated bypasses were re-run and now fail. The same sentence's TLA-model
and mutation-control counts were unbound — the exact unbound-front-page-count
class the gate exists to remove — and are now bound to the counted `.tla` and
`*.counterexample.cfg` files. A missing README now produces an orderly refusal
rather than a traceback. The gate's word-number map ends at sixteen by design:
an unmapped word fails closed and self-announces, forcing digits.

**"identity_map_mutation_errors holds no guard of its own" was false.** The
function holds five `return`-guards, and one of ADR 0029's own eleven cases
proved one of them — the same decision called it a hygiene guard two sections
after declaring the function guardless. Worse, `data_fixture_errors` (ten
guards) sat in neither `AUDITED_MODELS` nor `NOT_AUDITABLE` — the silent zero
the audit tool's own docstring warns about, committed by that tool. And
`branch_map`'s two distinct refusals flowed through one `errors.extend`,
counted as a single guard.

All nine refusal-bearing functions are now audited and `NOT_AUDITABLE` is
empty. Four new cases prove the identity-map hygiene guards and two prove
`branch_map` through `target: schema` mutations. Measured coverage:

| function | proved |
| --- | ---: |
| `branch_map` | 2/2 |
| `schema_contract_errors` | 15/64 |
| `data_fixture_errors` | 0/10 |
| `authority_grant_trace_errors` | 11/11 |
| `protocol_origin_errors` | 12/12 |
| `data_use_cohort_errors` | 11/11 |
| `work_lease_trace_errors` | 8/8 |
| `work_lease_record_candidate_errors` | 33/33 |
| `identity_map_mutation_errors` | 5/5 |
| **total** | **97/156** |

`data_fixture_errors` is 0 of 10 honestly: it validates a fixture loaded from
disk and no case mechanism can mutate it, so its guards are unprovable until a
fixture-mutation vocabulary exists. Retained as explicit gaps, not hidden.

**The "full-mission sweep" missed live stale counts.** The closure plan — the
document the README's Next section links as current — said, present-tense,
"103-schema" and "238 nonconformant fixture timestamps" against a measured 112
and 236. Corrected.

**Two smaller defects.** The inventory-id guard's message was a strict prefix
of the inventory-version guard's, so a substring binding could not isolate it;
the version message is reworded so neither contains the other, and the bound
case follows. The README coverage sentence said "across the lifecycle checker"
while measuring six of its nine refusal-bearing functions; it now states the
measured scope.

## Non-decisions

This decision does not:

- claim 156 is final. It is what `discover()` sees across the nine functions
  the audit now names. The denominator has been 69, 71, 75, 139, and 156;
  every prior figure was published as fact and was wrong. It remains a claim
  about where the measurement was pointed;
- prove any guard's condition. Coverage remains statement reachability
  (ADR 0030); the conditions inside all 156 guards are unmeasured;
- supply the fixture-mutation vocabulary `data_fixture_errors` needs, close
  the 49 remaining `schema_contract_errors` gaps, or close any PRQ finding; or
- change any contract, schema byte, event identity, or the 43/60/25/11
  boundary.

## Consequences

The audit's exclusion list is now empty, which removes the mechanism by which
two false exclusions were made. What remains cannot hide behind scope: 59
unproved statements are enumerated by name in the retained record, 10 of them
provably unreachable until a new vocabulary exists.

The count of broken published claims from this lane stands at eleven, all
flattering, all caught by independent reviewers and none by the producing
agent. The working rule this history enforces: no strength word without a test
that fails when it is false, no denominator without naming where it was
pointed, and no self-verified verdict — which is law 4, learned the slow way.
