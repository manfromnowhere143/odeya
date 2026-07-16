# WorkIntent reference-resolution suite

This isolated architecture suite checks the side-by-side WorkIntent 0.3
candidate and its exact reference targets. It proves raw-byte lineage and
structural validity only.

The suite deliberately separates three identities:

- exact raw bytes for the architecture candidate;
- an exact retained schema resource ID plus raw schema digest; and
- a canonical object digest, which remains null until the profile and target
  resources are admitted.

The PlanningEpoch 0.1 legacy input-view digest slot carries the exact raw source
candidate digest only as visible migration lineage. The evidence contract
forbids treating that value as canonical identity or admission. WorkIntent 0.3
therefore embeds explicit raw candidate bindings and null canonical digests
instead of laundering a file hash into an object identity.

Run with the pinned architecture interpreter:

```bash
/Users/danielwahnich/workspace/odeya/.venv-architecture/bin/python \
  tests/work-intent-reference-resolution/check.py
```

A pass does not issue the canonical profile, admit any target, create a
registry member, authorize assignment, close Gate A, or authorize runtime or
external effects.
