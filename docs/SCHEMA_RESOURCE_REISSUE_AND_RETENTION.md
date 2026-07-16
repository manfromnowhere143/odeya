# Schema Resource Reissue and Retention

Status: architecture evidence candidate; not admitted; Gate A remains blocked.

## Purpose

Odeya treats a JSON Schema resource as immutable bytes under one exact `$id`.
Changing those bytes requires a new exact resource identity and an auditable
predecessor edge. A filename is a workspace location, not a durable resource
identity, and a mutable alias such as `latest` is not admissible evidence.

The bounded ledger at
`architecture/schema-resource-reissue-ledger.json` records the schema paths
that existed at architecture checkpoint
`f4429ce5ca71e58ebb5d65776a45ebb6a2a18889` and whose current candidate `$id`
has changed. It inventories schema paths absent at that checkpoint separately;
those are new candidates, not reissues and not proof of a predecessor.

## Required reissue edge

Each reissued existing path binds:

- the exact predecessor schema resource `$id`;
- the source commit and exact Git blob reachable at that path from that commit;
- the predecessor raw SHA-256 and byte count recomputed from `git cat-file
  blob` output;
- the current candidate `$id`, raw SHA-256, byte count, and
  `unissued_candidate` status; and
- the explicit predecessor retention mode
  `git_object_only_architecture_checkpoint_blocking`.

The comparison is dynamic. Every schema path present at both the checkpoint
and the current working tree is parsed as strict UTF-8 JSON with duplicate
members and non-finite numbers rejected. A changed `$id` must appear exactly
once in sorted ledger order. Changed bytes under the same `$id` are refused.
Checkpoint paths may not disappear inside this bounded migration. Current
resource identities must be exact version-pinned identities, unique across the
current schema set, and neither identities nor resource references may use a
`latest` alias. Source-checkpoint
resource identities must also be unique, and a reissued or newly introduced
candidate may not reuse an identity historically owned by any source path.

## Raw bytes are not canonical content identity

The SHA-256 values in this ledger digest raw file bytes only. Odeya's canonical
profile remains blocked, so this artifact records no canonical content digest
and no digest may be inferred from its raw-byte fields. Raw bytes still provide
useful evidence: they make source-object retrieval and accidental mutation
testable without pretending the unresolved canonicalization contract is
closed.

## Retention boundary

The predecessor blobs are presently retrievable because the named Git commit
and tree are reachable in this repository. That is lineage evidence, not a
complete offline schema registry and not durable retention assurance. The old
resources have not been materialized as independently addressable local
versioned files in the current tree, no external archive is verified, and a
different clone, history rewrite, or loss of the source repository can remove
the resolution path.

Before schema admission or Gate A, a separate reviewed tranche must establish
the closed resolver and retention contract. It must materialize every retained
resource version, bind the resolver index to exact IDs and raw bytes, prove
offline resolution of the full transitive `$ref` closure, test rollback and
missing-object refusal, and define durable archival/recovery evidence. This
ledger deliberately does none of those things.

## Checker and refusal surface

Run:

```bash
python3 scripts/validate_schema_resource_reissues.py
```

The checker:

1. strictly parses the ledger and every source/current schema resource;
2. resolves the fixed commit and tree identities;
3. requires the source commit to remain an ancestor of `HEAD` and derives its
   source blob map from `git ls-tree`;
4. retrieves predecessor bytes with `git cat-file blob` and recomputes `$id`,
   raw SHA-256, and byte count;
5. compares the ledger with the exact dynamically derived reissue and new-path
   sets; and
6. rejects in-memory known-bad mutations covering an omitted reissue, false
   materialized/offline retention, an admitted candidate, a `latest` alias,
   theft of another historical resource's exact ID, a canonical digest while
   the profile is blocked, and runtime authority.

A pass means only that this bounded, working-tree candidate has internally
consistent byte-level lineage to the named reachable checkpoint. It does not
create or prove canonical content identity, a complete offline registry,
schema admission, constitutional admission, Gate A acceptance, deployment
authority, handler equality, or runtime authority.
