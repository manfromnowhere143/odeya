# ADR 0102: Prove a non-product prehash schema-registry replay

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-29
- Decision owners: canonical identity, schema contracts, replay, security
- Gate effect: adds bounded PRQ-002D architecture evidence for raw-resource
  binding, two-member ordering, derived keys, and closed resolution; does not
  issue a profile, compute a product identity, close PRQ-002, accept Gate A,
  or authorize runtime work

## Context

ADR 0101 blocks conformance and issuance of the frozen
`urn:odeya:canonicalization:odeya-jcs-0.2` candidate because ordinary JSON
parsers do not preserve the number-token evidence needed by its integer rule.
Its two source-separated observers retain one bounded raw-number observation,
not complete profile conformance.

The next dependency is smaller than a new canonicalization profile. Before any
structured member, commitment, or registry digest can be meaningful, Odeya
must prove that a registry replay can:

- bind exact resource bytes before parsing;
- derive two distinct member keys from resource bodies;
- reject duplicate or noncanonical key order;
- preload one closed resolver inventory without fallback; and
- prove that a cross-resource validation request used the exact resolved
  bytes.

One member cannot falsify ordering or duplicate-key behavior. Product schemas
cannot be used because their current bytes const-bind the blocked `0.2`
profile, and computing their identities here would skip the unresolved
dependency.

## Decision

Create the architecture-only PRQ-002D contract and evidence suite:

- [`architecture/prq-002d-schema-registry-prehash-contract-v1-candidate.json`](../../architecture/prq-002d-schema-registry-prehash-contract-v1-candidate.json);
- [`architecture/prq-002d-schema-registry-prehash-contract.schema.json`](../../architecture/prq-002d-schema-registry-prehash-contract.schema.json);
- [`tests/schema-registry-prehash-replay/`](../../tests/schema-registry-prehash-replay/);
  and
- [`scripts/validate_schema_registry_prehash_replay.py`](../../scripts/validate_schema_registry_prehash_replay.py).

The suite uses exactly two synthetic schema resources under its own fixture
directory. They are not Odeya product schema resources and may never be copied
into `schemas/`, admitted to a product registry, or used as a profile/root
member.

### Define prehash narrowly

`prehash` means before every structured or product identity construction. The
suite may compute SHA-256 over exact raw evidence bytes to bind resources,
probes, inputs, sources, dependencies, results, projections, receipts,
validator bytes, and gate rows. Resource/probe observations are named
`resource_raw_sha256` or `probe_raw_sha256`; all other hashes remain explicitly
typed raw-byte evidence bindings. None is a structured member, commitment,
registry, canonical-object, or product identity.

The suite must not compute or expose:

- `member_digest`;
- an ordered-member commitment or commitment digest;
- a registry snapshot or registry digest;
- a canonical-object digest;
- a product domain separator;
- an issued canonicalization-profile reference;
- an `EngineContractRoot`, checkpoint, activation, admission, or authority
  identity.

### Freeze exact inputs independently of input-controlled descriptors

The contract binds the safe bundle, both safe schema-resource byte strings,
and both safe probe instances by repository path, raw SHA-256, and decimal
byte count. It also pins a closed, ordered exception map for 13 intentional
single-resource semantic-fixture variants and one invalid-probe semantic
fixture. Every exception binds one opaque vector ID, one exact blob ID, raw
SHA-256, and decimal byte count. No exception exists for the parse-equivalent
resource reencoding, coherent resource substitution, or parse-equivalent
probe reencoding vectors.

The answer-free vector set carries self-descriptors for every virtual file,
but those input-controlled descriptors are never treated as authority. Before
parsing each resource or probe, each child compares the observed raw digest
and byte count to the safe contract binding or that vector's exact enumerated
semantic-fixture exception. An unenumerated mismatch refuses as an exact
resolver-target or replay-request failure. The validator binds the vector set
from outside the child process and checks the safe vector against the
contract's independently frozen bytes.

Each child receives the vector set, contract, and its own source manifest. It
does not receive the private expectation manifest, the peer source, or the
peer result.

### Freeze evaluation order

The bounded evaluator applies these classes in order:

1. strict UTF-8, BOM, JSON syntax, duplicate decoded names, and unpaired
   surrogate checks;
2. exact frame shape and one pointer-scoped subset of ADR 0101 for the
   top-level `/declared_member_count`: retain its raw spelling, require a
   decimal integer token, reject negative zero and values outside the retained
   cross-runtime integer domain, then require the exact token value `2`;
3. the all-false authority boundary;
4. exact count, member shape, duplicate-key, and unsigned UTF-8 ordering
   laws;
5. exact resolver inventory and virtual-blob presence;
6. member/resolver self-binding followed by independent contract-authoritative
   resource byte-count and raw-digest binding before resource parsing;
7. exact Draft 2020-12 dialect, metaschema validity, resource `$id`, and
   body-derived semantic version;
8. derived `schema_id@semantic_version` key/body equality;
9. registration under the exact contract URI;
10. exact replay-request inventory and independent contract-authoritative
    probe byte-count and raw-digest binding before probe parsing; and
11. validation of both fixed probes through the closed resolver.

Member keys are restricted to lowercase ASCII letters, digits, `.`, `_`, `:`,
`@`, and `-`. For that alphabet, unsigned UTF-8 byte ordering is
unambiguous. No locale, Unicode normalization, or case folding is allowed.

The schema resolver preloads exactly two digest-verified resources and exposes
no resource-loading fallback. An exact URI can resolve only to the safe
contract bytes or an exact contract-enumerated semantic-fixture variant for
that vector. The exception map permits a malformed fixture to reach its
declared semantic or parse guard; it does not authorize a new schema identity,
resolver target, or accepted replay. The retained vectors directly exercise
missing, additional, duplicated, reordered, aliased, relative, fragment,
network, dynamic-reference, and unenumerated substituted requests. The exact
reviewed source and contract exclude a schema-loading callback and
file/search/environment fallback; this is source-inventory evidence, not an
independently exercised vector claim or process sandbox. Both observers
necessarily read declared files and load dependencies, and
`undeclared_filesystem_read_excluded` remains `false`.

### Observe through source-separated implementations

One CPython observer uses five exact runtime-checked distributions in the
hash-locked architecture environment. One Node.js observer uses exact Node,
npm, Ajv, package, lock, and installer bindings. Their parsers, evaluators, and
source files are separate; neither may import the other. The parent requires
each runner's exact raw SHA-256 and byte count and separately performs strict
source inspection; accepted source must satisfy both controls. CPython source
is parsed with `ast`; Node source is admitted only under the exact reviewed
static-import/literal-require inventory because the locked Node closure
contains no ECMAScript parser. This is bounded source-inventory evidence, not a
general JavaScript analyzer, dependency-behavior proof, or information-flow
proof.

The retained corpus has 68 answer-free frames: one accepted safe frame and 67
single-attributed refusals. Some precedence frames contain more than one
defect by construction; “single-attributed” means the fixed oracle requires
one terminal code after the frozen evaluation order, not that every byte
mutation has exactly one possible defect. Both complete ordered projections
are compared against one fixed private oracle and against each other.

This is source and language separation, not organizational independence. The
retained execution receipts are self-attested byte-consistency records, not
independently witnessed historical process evidence. Agreement is
differential evidence and does not establish semantic truth.

The parent gate has 77 retained known-bad mutations. Each executes the same
named guard used on the unmodified graph and must return exactly its declared
singleton guard. The pure all-pass summary is derived from the declaration
inventory; observed mutation rows must match it exactly before the comparison
may bind it. This claim is limited to those 77 named suite guards, not every
possible source branch, generic parser behavior, dependency behavior, or
repository-wide gate. Missing observations remain `null`; they are never
converted to zero.

The parent also pins the contract schema's exact raw bytes and compact JSON
semantics. Retained mutations remove root and nested closedness directly and
attempt the same weakening through an object-capable type array and an omitted
object type; each must return `contract_schema_boundary`. This is an exact
fixed-schema control, not a general proof that arbitrary JSON Schemas are
closed.

The parent verifies the predecessor commit, tree, and both cited blobs through
Git object bytes rather than trusting editable labels. Evidence authoring
stages the complete generated graph outside the retained suite, validates it
before finalization, fsyncs candidate bytes, and replaces the comparison
receipt last. The comparison binds the other retained artifacts, so an
interrupted finalization cannot appear valid.

## Non-decisions

This decision does not:

- modify or issue `odeya-jcs-0.2`, create `odeya-jcs-0.3`, or prove profile
  conformance;
- construct a product member, commitment, registry, root, checkpoint, or
  activation;
- prove a complete offline product schema registry, archival retention,
  historical availability, causal execution origin, organizational
  independence, or independent-host reproduction;
- validate the nine product-domain framing contracts or cross-object product
  replay;
- admit any schema or close PRQ-002;
- accept Gate A or substitute for accountable review or Daniel's exact-byte
  decision; or
- authorize runtime, deployment, publication, spending, credentials, data
  access, or external effects.

## Consequences

A passing PRQ-002D suite establishes only that the exact retained synthetic
inputs satisfy the declared two-member prehash replay proposition under two
source-separated implementations. It makes count, ordering, unique-key,
key/body, digest/body, and exact resolver substitution failures falsifiable
without pretending that product identity already exists.

The next product-identity work remains dependency ordered: create a complete
side-by-side `odeya-jcs-0.3` core/evidence/migration and twelve-resource
successor cohort; then run full source-separated profile conformance, complete
offline resolution and historical-retention evidence, dependency-closed
product registries, cross-object replay, accountable review, and the
operator's exact-byte decision. None of those later steps is part of this
tranche.
