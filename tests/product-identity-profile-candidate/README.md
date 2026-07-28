# PRQ-002B product identity profile candidate contract

Status: architecture-only adversarial contract for the scoped
`odeya-jcs-0.2` successor candidate. A pass means only that the exact candidate
bytes satisfy the bounded checks below. The profile remains unissued and
unadmitted; PRQ-002 and Gate A remain open; no runtime is authorized.

This suite is separate from the PRQ-002A structural probe. It refuses every
probe identity, domain, scope marker, member-key profile, retained probe-core
digest, or result status in the product tranche. Probe paths may appear only
as negative exclusion prefixes in the migration record. Nothing from the
probe is renamed, promoted, or treated as a predecessor product object.

## Exact candidate boundary

The full check requires exactly twelve side-by-side schema resources:

- four standalone member schemas;
- one ordered member-map commitment schema;
- four successor registry schemas;
- the successor profile-core and evidence schemas; and
- one explicit profile-migration schema.

Those resources declare exactly nine new product domains. Every path, `$id`,
domain-to-declaring-schema binding, raw SHA-256 digest, and byte count must
agree across the core, evidence, migration, and local schema bytes.

`predecessor-schemas.json` freezes the exact 120-path predecessor product
cohort at commit `5332239f84ff278815c25d888f115bce22919e34`. Each row binds the
path, schema `$id`, exact raw SHA-256 digest, and byte count. The checker
requires all 120 resources to remain byte-for-byte present and requires the
candidate schema glob to partition exactly as:

```text
106 retained direct predecessor-profile consumers
+ 14 retained non-direct predecessor resources
+ 12 successor resources
= 132 candidate schema paths
```

The 106/14 partition and all 484 exact predecessor-profile literal
occurrences are independently recomputed from the frozen paths. Architecture,
test, documentation, script, and historical Git material are outside that
product-consumer census.

## Structural nonidentity vectors

Nine schema-valid vectors live under
`tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/`
with filenames matching `prq-002b-*.structural-nonidentity.json`.
They are the closed accepted baselines needed to exercise the four member,
one commitment, and four registry schemas without constructing product
identity. They are not named `.valid.json`, are outside this suite's closed
local JSON inventory, and are not migration inputs, registry members,
commitments, snapshots, roots, or digest results.

`cases.json` binds every vector path to one exact schema path and `$id`, its
result-digest pointer, and one reserved sentinel result. Every digest-shaped
value must belong to the exact eighteen-value sentinel set. The full checker
loads the complete local schema registry with no retrieval callback, validates
all nine vectors offline, requires every `profile_core_raw_digest` to remain
the reserved sentinel, and dynamically proves that no sentinel equals the raw
SHA-256 of any current `schemas/*.json` or `architecture/*.json` artifact.
It also refuses a vector path or sentinel appearing in any of the twelve
successor schemas or three candidate records.

The checker never canonicalizes these vectors or recomputes their member,
commitment, or registry digests. Structural validity therefore contributes
zero product identity instances. Shared architecture-schema manifest
enrollment remains a separate integration step and cannot change that
boundary.

## What the full check attacks

The checker validates:

- the exact profile predecessor and successor identities;
- strict Draft 2020-12 schemas and schema-valid core, evidence, and migration
  records;
- exact four-field successor profile references without a const-embedded core
  digest;
- exact scoped framing, pointer separation, and the single algorithm spelling;
- the complete declared raw/digest dependency graph, independent schema
  `$ref` resolution, absence of self-edges and cycles, and the rule that no
  successor schema may embed the successor core raw digest;
- explicit new-resource versus side-by-side-successor dispositions;
- exact frozen predecessor raw-byte bindings;
- a closed suite-local JSON inventory containing only `cases.json` and
  `predecessor-schemas.json`, so a fixture or any other nested JSON product
  instance fails closed;
- the exact nine global structural-nonidentity vectors, their offline schema
  validity, closed sentinel set, dynamic raw-byte noncollision, and absence
  from product identity surfaces;
- an explicit, incomplete migration with no cross-profile digest equality,
  implicit upcast, predecessor erasure, or probe-object migration;
- the independently derived scoped consumer census;
- current-byte resolution while the complete historical offline registry
  remains explicitly absent; and
- false/null issuance, admission, member, snapshot, root, activation,
  accountable review, operator acceptance, Gate A, deployment, external
  effect, publication, and runtime authority.

The schema and core raw-byte cascade must be coherent. A wholly placeholder
phase is reported as unfinished, a mixed placeholder/exact phase is refused,
and a full pass requires all twelve schema bindings plus the external core and
evidence bindings to be exact. Source-separated full-profile conformance,
complete offline resolution, accountable review, and operator acceptance
remain false even after the local byte freeze succeeds.

## Run while the tranche is being built

The retained known-bads can be exercised before all product artifacts exist:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv-architecture/bin/python -B \
  tests/product-identity-profile-candidate/check.py --self-test-only
```

This validates one synthetic safe observation and nineteen direct,
single-fault known-bads across:

- identity laundering;
- digest cycles;
- framing ambiguity;
- incomplete migration;
- probe contamination;
- suite-local product-instance contamination;
- authority leakage;
- offline-resolution overclaim; and
- exact JSON-type substitution, including integral-float and bool/int
  equality plus Draft 2020-12-valid integral floats that cannot satisfy the
  candidate's stricter typed-`const` or bare-integer contract.

Every known-bad names one intended guard and an exact expected error
inventory. The self-test does not validate the live product artifacts.

## Run the full candidate contract

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv-architecture/bin/python -B \
  tests/product-identity-profile-candidate/check.py
```

Missing or partially rebound artifacts produce attributed diagnostics instead
of aborting the suite. A green result is not profile issuance, registry
admission, a product member or snapshot, a canonical product digest,
`EngineContractRoot`, activation, PRQ-002 closure, Gate A acceptance, or
runtime authority.
