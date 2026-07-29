# PRQ-002D non-product schema-registry prehash replay

Status: architecture-only, synthetic, non-product, and nonidentity evidence.
The suite is proposed and not operator accepted.

This suite tests one dependency-bounded proposition: two exact synthetic JSON
Schema resources can be raw-byte bound, assigned body-derived keys, ordered by
unsigned UTF-8 bytes, preloaded into a closed resolver, and used for two fixed
validation requests without computing any structured or product identity.

The fixture resources live only under this suite. They are not Odeya product
schema resources and cannot be admitted, issued, copied into `schemas/`, or
used as a profile, member, commitment, registry, root, checkpoint, activation,
or authority input.

## Evidence shape

- One answer-free vector set contains 68 opaque virtual-file frames.
- One fixed private oracle expects one accepted replay and 67
  single-attributed refusals under the frozen precedence order.
- CPython 3.14.2 runtime-checks `attrs` 26.1.0, `jsonschema` 4.26.0,
  `jsonschema-specifications` 2025.9.1, `referencing` 0.37.0, and `rpds-py`
  2026.6.3 against the hash-locked architecture installation.
- Node.js 24.18.0 and npm 11.16.0 use the exact package/lock closure for Ajv
  8.20.0 in strict, noncoercing mode with only pre-added resources and no
  loading callback.
- The two child sources do not consume the expectation manifest, peer source,
  or peer result.
- The retained comparison requires complete ordered projection equality and
  binds a pure all-pass summary for 77 mutation-backed suite guards.

The raw numeric spellings `2.0`, `2e0`, and `-0` are refused before host-type
aliases can erase the lexical distinction. Missing observations are `null`,
not zero.

The member keys deliberately differ at `-` versus `.` so that two-member
ordering is discriminating. The safe resource with the `-` key contains one
absolute reference to the resource with the `.` key. Both resource and probe
bytes are pinned independently in the contract. A coherent input-controlled
digest relabel therefore cannot replace the trusted resolver target.

Before parsing any resource or probe, each observer compares its raw SHA-256
and decimal byte count to an independent contract binding. Safe/default bytes
come from `expected_resources` and `expected_replays`. A closed ordered map
authorizes only 13 single-resource semantic-fixture variants
(`PH-0021`–`PH-0028`, `PH-0052`, `PH-0055`, `PH-0057`, `PH-0064`, and
`PH-0065`) and the invalid-probe fixture `PH-0033`. The parse-equivalent
resource reencoding `PH-0029`, coherent resource substitution `PH-0030`, and
parse-equivalent probe reencoding `PH-0044` have no exception and refuse at
the resolver-target or replay-request boundary before parsing. These
exceptions preserve negative semantic-guard reachability; they do not admit
variant resources, probes, identities, or successful replays.

The schema resolver is in-memory and exact. The retained vectors directly
exercise missing/additional virtual blobs, network targets, mutable aliases,
relative or fragment requests, dynamic references, reordered
catalogs/requests, substitutions, and fallback retrieval. The parent requires
the retained suite inventory to contain no symlinks, and the exact reviewed
source exposes no schema-loading callback or file/search/environment fallback.
Those latter properties are source/inventory controls, not independently
exercised vector claims or process isolation: the observers read declared
inputs and load pinned dependencies, so `undeclared_filesystem_read_excluded`
and `filesystem_isolation_proven` remain `false`.

The parent binds the exact raw runner bytes, parses Python with the CPython AST,
and admits Node only under the reviewed static-import/literal-require inventory
plus an exact raw-byte pin. This is bounded source-inventory evidence, not a
general JavaScript static analysis, transitive dependency proof, process
sandbox, causal-execution witness, or organizational independence.

## What a pass means

A default pass establishes that the retained observations attributed to both
source-separated implementations match the fixed oracle for count, ordering,
unique-key, key/body, raw-digest/body, exact resolver, and fixed replay checks.
Fresh recomputation directly observes the same bounded match under the selected
executables. Neither path proves causal origin beyond its recorded process
boundary or semantic truth.

It does not prove:

- organizational independence, independent-host reproduction, or
  independently witnessed historical execution;
- generic JSON Schema implementation equivalence or semantic truth;
- a complete offline product schema registry, content-addressed archive, or
  historical-retention proof;
- `odeya-jcs-0.2` or prospective `odeya-jcs-0.3` conformance or issuance;
- a product member, commitment, registry digest, root, checkpoint, activation,
  admission, or PRQ-002 closure;
- accountable review, Gate A acceptance, or Daniel's exact-byte decision; or
- runtime, deployment, publication, credentials, spending, data access, or
  external-effect authority.

Run the retained-evidence check with:

```bash
.venv-architecture/bin/python \
  scripts/validate_schema_registry_prehash_replay.py
```

Fresh recomputation additionally requires exact CPython and Node selectors:

```bash
NODE_BIN="$(bash scripts/ci/install-node.sh)"
NODE_ROOT="${NODE_BIN%/bin/node}"
"$NODE_BIN" "$NODE_ROOT/lib/node_modules/npm/bin/npm-cli.js" ci \
  --ignore-scripts \
  --no-audit \
  --no-fund \
  --prefix tests/schema-registry-prehash-replay/node

.venv-architecture/bin/python \
  scripts/validate_schema_registry_prehash_replay.py \
  --recompute-all \
  --python-executable .venv-architecture/bin/python \
  --node-executable "$NODE_BIN"
```

The authoring-only `--refresh-retained-evidence` mode requires the same two
selectors. It stages and validates every generated artifact before
finalization, fsyncs staged bytes, and replaces the comparison receipt last.
It is not part of the default verifier and grants no authority.

The next dependency remains a complete side-by-side `odeya-jcs-0.3`
core/evidence/migration and twelve-resource successor cohort, followed by full
source-separated conformance, complete offline resolution and retention,
dependency-closed product registries, cross-object replay, accountable review,
and the operator decision. None of that later work is part of PRQ-002D.
