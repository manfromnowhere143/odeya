# WorkIntent identity candidate checks

Status: architecture-only evidence for a prospective nonrecursive WorkIntent
identity construction. The canonical profile remains unissued, WorkIntent 0.1
remains the current unresolved candidate, its consumers have not been reissued,
and Gate A remains blocked.

The construction is deliberately split:

```text
identity-free WorkIntent semantic core
  -> external exact raw-byte binding
  -> frozen-but-unissued profile candidate reference
  -> retained WorkIntent 0.1 semantic projection
  -> exact WorkIntent / WorkLease / WorkContract reissue boundary
```

`architecture/work-intent-core-candidate.json` contains only the semantic
subject. It has no profile binding or canonical self-digest. Its schema fixes
UTC timestamps to six fractional digits, bounds integers to the interoperable
safe domain, and gives every retained digest field an explicit scope. The
three retained reference shapes remain migration findings and are not claimed
as admitted identities.

`architecture/work-intent-identity-candidate-evidence.json` externally binds
the core, core schema, legacy schema/fixture projection, frozen profile core,
and two direct schema consumers. Its raw SHA-256 values identify local file
bytes for review; they are not canonical object digests.

This follows the same nonrecursive pattern used by content-addressed descriptor
and provenance formats: the subject is separate from the statement that names
its digest. RFC 8785 supplies deterministic JSON serialization, JSON Schema
2020-12 supplies exact schema-resource identifiers, and the local profile adds
Odeya's envelope, parser, domain, timestamp, and collection constraints.

The checker recomputes every raw-byte binding, validates both schemas, proves
the exact legacy semantic projection, derives the candidate core's canonical
audit result, and verifies the ordered direct-consumer reissue set. One safe
reference and 28 known-bad mutations exercise self-reference, timestamp and set
drift, byte substitution, profile or admission fabrication, consumer omission,
mutable aliases, reissue-order drift, and authority escalation.

Run:

```bash
python3 tests/work-intent-identity-candidate/check.py
```

A pass does not issue the profile or WorkIntent identity, replace WorkIntent
0.1, admit a registry member, prove a complete offline predecessor registry,
construct the thirteen-event assignment cohort, accept Gate A, or authorize
assignment, lease, dispatch, deployment, runtime, spending, data exposure, or
any external effect.
