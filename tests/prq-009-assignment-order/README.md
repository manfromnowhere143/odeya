# PRQ-009 assignment-order consistency evidence

This bounded architecture-only suite checks the machine-readable
[`PRQ-009 assignment-order contract`](../../architecture/prq-009-assignment-order-contract.json)
against every active consumer named by that record.

Run it from the repository root:

```bash
python3 scripts/validate_prq_009_assignment_order.py
```

The checker freezes this order:

```text
WorkIntent
  -> one atomic verification.assign assignment commit
     (worker + five ordered grant uses/exhaustions + active lease + reservation)
  -> deterministic WorkContract derived from that exact commit
  -> separate attempt.start dispatch claim
```

It also executes every retained mutation in `cases.json`. The first two
known-bads restore the legacy error in two independent forms: prose that makes
a pre-existing `WorkContract` an assignment input, and a machine contract
whose prospective input is `WorkContract` instead of `WorkIntent`. Both must
be refused.

This is a textual and finite-record consistency check. It does not prove
canonical identities, command/event membership, reducer behavior, concurrency,
replay, assignment, dispatch, Gate A acceptance, or runtime. PRQ-009 remains
`unresolved_blocking`.
