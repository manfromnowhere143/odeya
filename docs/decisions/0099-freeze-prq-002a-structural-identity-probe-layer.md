# ADR 0099: Freeze a non-issuable PRQ-002A structural identity probe layer

- Status: Proposed architecture-only construction probe
- Date: 2026-07-27
- Gate: PRQ-002 candidate topology evidence only

## Context

PRQ-002 requires standalone schema, aggregate-state, reducer, and event member
records plus pure registry-snapshot identity. The current registry schemas
embed those member shapes inside parent registry resources. Their production
member domains are bound by the frozen-for-review canonicalization profile to
those parent schema IDs. A new standalone schema cannot truthfully reuse one of
those domain bindings without a successor profile, new schema identities, and
transitive consumer migration.

The smallest useful next construction is therefore a synthetic identity probe,
not a product registry or a first-slice member. Its profile parameters require
the same nonrecursive separation as ADR 0020: a schema defines the closed
shape, while a distinct exact profile-core document supplies the raw bytes
named by every four-field profile reference. It must exercise the exact
acyclic direction

```text
retained schema bytes -> exact schema-valid probe profile core
                      -> schema member -> state member -> reducer member
                      -> event member -> family commitment -> family snapshot
```

while requiring every retained object and result to carry a distinct probe
scope and while refusing the declared issuance and authority contaminations.
That is a bounded construction contract, not a claim of cryptographic
impossibility outside the retained checks.

The generic canonical-object profile describes an envelope
`{profile_id,schema_id,subject}`. Existing scoped member contracts separately
describe a candidate input
`{digest_contract,resolved_subject_schema,projection}`. Production framing is
not yet issued. This probe freezes the latter framing only inside its distinct
test profile; it does not settle or amend the production profile.

## Decision

### Scope and identity namespace

Add one closed, architecture-only probe-profile schema, four closed standalone
member-probe schemas, one closed ordered-map-commitment schema, one closed pure
snapshot schema, and two closed synthetic subject schemas:

| Path | Schema ID |
| --- | --- |
| `architecture/prq-002-identity-probe-profile.schema.json` | `urn:odeya:architecture-schema:prq-002-identity-probe-profile:0.1.0` |
| `architecture/prq-002-schema-member-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-schema-member-probe:0.1.0` |
| `architecture/prq-002-aggregate-state-member-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-aggregate-state-member-probe:0.1.0` |
| `architecture/prq-002-reducer-member-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-reducer-member-probe:0.1.0` |
| `architecture/prq-002-event-member-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-event-member-probe:0.1.0` |
| `architecture/prq-002-ordered-member-map-commitment-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-ordered-member-map-commitment-probe:0.1.0` |
| `architecture/prq-002-pure-registry-snapshot-probe.schema.json` | `urn:odeya:architecture-schema:prq-002-pure-registry-snapshot-probe:0.1.0` |
| `architecture/prq-002-structural-state.schema.json` | `urn:odeya:architecture-schema:prq-002-structural-state:0.1.0` |
| `architecture/prq-002-structural-event.schema.json` | `urn:odeya:architecture-schema:prq-002-structural-event:0.1.0` |

Retain the one exact profile instance separately as
`architecture/prq-002-identity-probe-profile-core.json`. It is validated by
`urn:odeya:architecture-schema:prq-002-identity-probe-profile:0.1.0`, contains
no self hash, and has exact raw-byte identity:

```text
sha256:8c51e7bbf9dbbc4a13813ef730fff40103120512ec595af8cf1bdb62f87fc546
8336 bytes
```

This document is the one logical profile instance counted in the 21-object
cohort. Any embedded cohort projection of the profile must equal the parsed
standalone core exactly; it is not a second profile instance. The core adds no
schema and does not change the nine-schema architecture set or the frozen
120-schema product census.

Every probe subject includes
`identity_scope=prq_002_structural_probe_only` inside its digest projection.
The profile is
`urn:odeya:canonicalization:prq-002-identity-probe-jcs-0.1`, version
`0.1.0`, with status `test_only_non_issuable_structural_probe`. It binds the
exact raw current `odeya-jcs-0.1` candidate core as a base but is not a
successor, registry member, alias, or issuable profile.

The probe domains are:

```text
odeya-prq-002-schema-member-probe-v1
odeya-prq-002-aggregate-state-member-probe-v1
odeya-prq-002-reducer-member-probe-v1
odeya-prq-002-event-member-probe-v1
odeya-prq-002-ordered-member-map-commitment-probe-v1
odeya-prq-002-schema-registry-snapshot-probe-v1
odeya-prq-002-aggregate-state-registry-snapshot-probe-v1
odeya-prq-002-reducer-registry-snapshot-probe-v1
odeya-prq-002-event-registry-snapshot-probe-v1
```

None is a production-domain reservation. Promotion requires new product schema
IDs, a reviewed profile successor, and complete digest recomputation.

### Digest construction

Raw schema identity is always
`sha256:` plus lowercase SHA-256 over exact retained bytes, accompanied by the
exact byte count. It is not a structured-object digest.

Every probe structured digest contract contains:

```text
algorithm
domain_separator
canonicalization_profile_ref
subject_schema_ref
included_json_pointers
excluded_json_pointers
```

`algorithm` is lexically `sha256`. The profile reference uses the prospective
four-field shape `profile_id`, `profile_version`, `profile_core_schema_id`, and
`profile_core_raw_digest`. For this probe, `profile_core_schema_id` is exactly
`urn:odeya:architecture-schema:prq-002-identity-probe-profile:0.1.0` and
`profile_core_raw_digest` is exactly the raw digest of the standalone
8336-byte profile-core document above. The raw digest of the profile schema is
a separate schema-resource identity used by its schema-member probe and
evidence binding; it must never occupy `profile_core_raw_digest`. The subject
schema reference carries the exact versioned subject-schema ID and raw schema
digest.

A probe evaluator must strictly parse and schema-validate the complete object,
construct the exact pointer-selected projection, and JCS-encode:

```json
{
  "digest_contract": {},
  "resolved_subject_schema": {
    "schema_id": "...",
    "schema_digest": "sha256:..."
  },
  "projection": {}
}
```

The resulting probe digest is `sha256:` plus lowercase SHA-256 over those exact
UTF-8 RFC 8785 bytes. The digest contract itself is present both as the
top-level `digest_contract` member and in the projection, matching the current
scoped-member convention. Only the resulting digest field is excluded.

This framing is local to the probe profile. It is not canonical profile
issuance or a decision that production identities will retain the same
framing.

### Parser and recomputation evidence

The retained parser observation distinguishes lexical refusal from finite
IEEE-754 conversion. Both evaluators accept `1e-400` and `-1e-400` as finite
underflows to positive and negative zero, respectively. The probe parser
refuses the lexical JSON number `-0` before conversion. These are bounded
observations over the retained inputs, not a general numeric-profile issuance
decision.

Each source manifest binds the exact evaluator source, dependency lock, and
complete immutable canonicalizer payload inventory. The Python child does not
import the installed `rfc8785` package: it rejects package-local import-cache
or extra payload bytes, then compiles and executes the exact bound
`rfc8785/_impl.py` source. The Node child imports the exact bound
`canonicalize` source from its lock-installed package directory.

Portable current recomputation and historical execution observations are
separate evidence:

- the selected Python child must resolve to the already-running checker's
  startup-bound CPython image, match its executable bytes before and after the
  child, and run with exact `-I -S -B` isolation flags whose six resulting
  runtime properties are attested;
- the selected Node child must be the exact platform product of the
  digest-verifying installer, whose pinned archive must contain a regular
  `bin/node` member byte-identical to the selected executable before and after
  execution; and
- each child receives a fresh challenge and emits exactly two canonical JSON
  lines: a complete execution attestation bound to the executable, argv,
  immutable inputs, evaluator and canonicalizer bytes, challenge, and exact
  result-line digest, followed by the deterministic result line that is
  compared byte-for-byte with retained evidence.

The retained Darwin/arm64 executable paths, hashes, argv, challenges,
attestations, and two-line stdout bindings are host-specific historical
observations. A different host must satisfy the portable contract above; it
does not need to reproduce the historical paths or executable bytes.

Dependency bootstrap and the Node installer may use a local cache or the
network before evaluator execution. No OS-level network sandbox or observed
network-non-use proof exists; the exact evaluator sources only declare that
they request no network access. The already-running parent interpreter and
standard library, OS kernel and process loader, filesystem and hardware
behavior, SHA-256, and absence of a hostile same-user race remain explicit
trusted preconditions.

### Member graph

The synthetic cohort uses:

```text
aggregate_type       structural-aggregate
owning_module        structural-module
state_subject_id     state.structural-aggregate
state version        0.1.0
reducer_id            reducer.structural-aggregate
reducer version       0.1.0
event                 structural.event_recorded@0.1.0
future command        structural.command_probe@0.1.0
payload pointer       /oneOf/0/properties/payload
```

State binds the exact state-schema member digest. Reducer binds the exact state
member digest. Event binds the exact envelope-schema and reducer member
digests. State-to-reducer, state/reducer-to-event, and event-to-command reverse
references carry logical identity plus the future requirement
`future_same_root_exact_member`; they never contain a reverse member digest.
The command is outside PRQ-002A and no command member may be constructed.

### Member keys and commitment

Decoded member-key strings are restricted to ASCII. Duplicate logical keys are
rejected before ordering. Ordering is ascending unsigned lexicographic order
over exact UTF-8 bytes, with no locale, normalization, or case folding.

The family expressions are:

```text
schema registry                   schema_id@semantic_version
aggregate-state subject registry  aggregate_type
reducer registry                  aggregate_type
event-contract registry           event_type@event_version
```

`odeya-canonical-map-commitment-v1` is a flat canonical closed object. Its
ordered entries are exactly `{member_key,member_digest}`. No separate leaf
hash, Merkle tree, temporal append-only claim, inclusion receipt, or history
proof is part of this probe. The field is named
`ordered_member_pairs_digest`, not the ambiguous
`ordered_member_digests_digest`.

### Pure snapshots

One generic pure-snapshot schema has four family-specific instances:
`schema_registry`, `aggregate_state_subject_registry`, `reducer_registry`, and
`event_contract_registry`. A heterogeneous snapshot is forbidden.

The snapshot contains exact family/ID/version, a null or exact immutable
predecessor reference, exact probe-profile reference, the full leaf-only
commitment object, digest contract, and digest. It contains no full member
body, review or source evidence, currentness/admission claim, membership proof,
history, checkpoint, activation, signature, attestation, storage location, or
runtime binding.

## Consequences

- The schema layer can support a source-separated recomputed structural probe
  without changing any product schema or the frozen 120-schema product census.
- The probe cannot close PRQ-002 because it intentionally allocates no product
  member schema, production domain, admitted registry, or root-compatible
  identity.
- The bounded evidence tranche authorized by this decision contains exactly
  one probe-profile instance, 12 standalone member instances, four
  family-specific flat commitment instances, and four homogeneous pure-snapshot
  instances: 21 cohort objects in total. The 12 members are schema-member
  probes for all nine architecture schemas in this decision plus one state,
  reducer, and event member. The tranche must bind exact raw schema/profile
  bytes, require its profile projection to equal the standalone profile core,
  and enforce the complete cross-object graph.
- That tranche also contains an accepted case and a bounded set of
  single-mutation adversarial known-bads, two source-separated deterministic
  recomputation results, one exact comparison receipt, and two bounded
  historical-execution/current-attestation receipts. Those observations remain
  distinct from language/source separation and do not establish independent
  execution. Every instance, case, result, and receipt remains test-only and
  non-issuable.
- A future product tranche must reissue the member and registry schemas rather
  than renaming or promoting these architecture-schema resources.

## Alternatives rejected

- Reuse the current production member domains: their declaring schema IDs are
  the parent registry schemas, so reuse would create a false domain binding.
- Mutate the frozen profile core: its exact raw bytes are retained by existing
  evidence and cannot be silently amended.
- One heterogeneous snapshot: the engine root has distinct registry-family
  slots and no mixed-family registry identity.
- Digest-only leaves: they fail to bind the member key required by ADR 0018.
- Merkle or transparency semantics: snapshot membership and insertion-ordered
  history are separate subjects and proof profiles.
- A synthetic Blocker member: every real event payload contract remains
  unresolved and no Blocker reducer evidence exists.

## Acceptance boundary

This decision authorizes the nine closed architecture schemas listed above,
the exact standalone non-self-hashing profile-core document, and the bounded
architecture-only probe suite under
`tests/prq-002-identity-cohort/`: its manifest and case index, the exact
21-object candidate cohort described in Consequences, strict-parser and
single-mutation fixtures, two source-separated language runners and
their dependency/source manifests, two deterministic result artifacts, one
comparison receipt, and two execution-origin receipts.

That authorization creates only construction evidence about the candidate
topology. It does not create a command member, product schema, production
domain, canonical-profile successor, admitted registry or registry member,
EngineContractRoot, C0, checkpoint, P0, activation, reducer implementation,
runtime, deployment, external effect, publication authority, Gate A
acceptance, PRQ-002 closure, or operator decision. Passing both runners or
matching every retained digest cannot cross any of those boundaries.
