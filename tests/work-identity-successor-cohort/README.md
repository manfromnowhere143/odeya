# Work identity successor cohort checks

Status: architecture-only evidence for one side-by-side immutable successor
cohort. It does not issue a canonical identity, admit a resource, construct an
assignment, or authorize runtime.

The cohort preserves all three predecessor schema resources at their original
paths and exact `$id` values, then adds:

```text
WorkIntent 0.2
  -> WorkIntent semantic core 0.1 + exact nested-reference bindings

canonical WorkLease 0.2
  -> canonical WorkLease 0.1 + exact WorkIntent 0.2 successor binding

WorkContract 0.3
  -> blocked WorkContract 0.2 + exact WorkIntent 0.2 successor binding
```

This is a migration bridge, not the final admitted shape. The source-view and
planning-epoch fixture values are explicitly synthetic, the retained output
schema digest differs from the exact current schema raw digest, and the
canonical profile is unissued. Those findings block all three canonical
digests and every authority flag.

`architecture/work-identity-successor-cohort-evidence.json` binds the exact
predecessor commit/tree, predecessor and successor schema bytes, candidate
artifact bytes, dependency edges, bounded cross-object equalities, retention
boundary, and unresolved findings. Predecessors remain resolvable side by side;
the package does not claim a complete offline schema registry.

The checker validates the four schemas with an exact local resource registry,
recomputes all raw bindings, compares predecessor bytes against the retained
Git checkpoint, proves each embedded predecessor fixture and nested reference
equality, and rejects authority or acceptance escalation. One safe reference
and 37 known-bad mutations cover self-digests, profile drift, reference
substitution, raw-byte drift, missing/reordered resources or edges, predecessor
mutation, false retention, fabricated equality/admission, and runtime claims.

Run:

```bash
python3 tests/work-identity-successor-cohort/check.py
```

A pass does not resolve the synthetic reference values, repair the output
schema digest mismatch, issue the canonical profile, compute canonical object
digests, admit registry members, complete the thirteen-event assignment
cohort, prove reducers/replay, accept Gate A, or authorize assignment, lease,
materialization, dispatch, deployment, runtime, spending, data exposure,
publication, or external effects.
