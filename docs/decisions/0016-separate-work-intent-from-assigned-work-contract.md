# ADR 0016: Separate prospective work intent from assigned work contracts

- Status: Proposed
- Date: 2026-07-16
- Gate: G1/G2/G3/G6; requires identity, assignment, closure-resolution, replay, and independent review evidence

## Context

Two boundaries were previously conflated.

First, a logical command-payload type such as
`urn:odeya:command-payload:verification.assign:1.0.0` is not a JSON Schema
resource identifier. A validator also needs the exact schema dialect, source
blob, canonical form, and transitive schema-resource closure. Reusing one
field called `command_schema_id` or one undifferentiated digest for these
different identities makes replay ambiguous and permits the same logical type
to resolve through different bytes or different reference closures.

Second, a planning artifact that says work would be useful is not an
assignment. Requiring an active lease, capability grant, or capacity
reservation while the work is still only prospective either allocates scarce
authority too early or encourages callers to fabricate current-state
references. Treating that artifact as a `WorkContract` also obscures the
atomic point at which a verifier, lease, reservation, data boundary, sandbox,
and current authority are actually selected.

## Proposed decision

### Identity layers are distinct and immutable

Every admitted `CommandContractRecord` carries these independently named
identities:

1. `payload_type_id`: the language-neutral logical payload type and version;
2. `resource_id`: the immutable JSON Schema `$id` for the root resource;
3. `dialect_id`: the exact JSON Schema dialect declared by `$schema`;
4. `blob_identity`: digest and byte count of the retained source bytes;
5. `canonical_identity`: digest plus the exact canonicalization profile; and
6. `closure_identity`: a digest commitment to the exact root and transitive
   schema-resource set used for validation.

These fields are not aliases. Equality of two digest values does not collapse
their semantic roles. A changed schema resource, canonicalization profile, or
transitive closure requires a new immutable resource identity/version before
admission. Mutable aliases such as `latest`, implementation-default dialects,
network retrieval, and unresolved references are forbidden. Validation uses
only an explicitly preloaded resource registry; a missing resource, closure
mismatch, reference cycle, or attempted network resolution rejects before the
decider.

The standalone `CommandContractRecord` is the registry member subject. It does
not contain its parent registry digest, membership proof, activation proof, or
generated envelope identity. The parent `CommandContractRegistry` commits the
ordered record digests; an external membership proof binds a record to that
registry; `RegistryActivation` separately binds an eligible registry to an
active root. This keeps the content graph acyclic.

There is one command-registry subject type:
`urn:odeya:schema:command-contract-registry:*`. Names such as
`command-registry-snapshot` are not separate schema resources. Envelope,
receipt, policy, and admission-evidence references must identify an exact
`CommandContractRegistry` version and digest.

### WorkIntent precedes assignment

`WorkIntent` is a closed, immutable, prospective, non-authoritative planning
artifact. It may describe an objective, deliverable classes, candidate worker
requirements, data constraints, and bounded estimates. At intent creation:

- no active work lease is required or represented;
- no authority or capability grant is required, consumed, or conferred;
- no resource/spend reservation is required or claimed;
- no dispatch/effect admission exists;
- no bytes may be materialized or cross an execution boundary; and
- no provider spend may be incurred.

The construction order is:

```text
WorkIntent
  -> admitted verification.assign atomic commit
     (principal + lease + grants + data decisions + sandbox + reservation)
  -> post-assignment derived WorkContract
  -> separately admitted dispatch claim
  -> execution boundary may be crossed
```

The `verification.assign` commit references the exact intent and is the first
point at which current assignment facts may be established. A `WorkContract`
must bind that exact committed assignment and is derived only afterward. It is
still a deterministic control artifact, not dispatch authority. Dispatch
rechecks the current lease, grants, data decisions, policy, reservation,
controlled time, and revocation state and commits its own claim before any
materialization, external bytes, or spend.

## Consequences

- Planners can retain useful work proposals without acquiring short-lived
  authority or scarce capacity.
- Assignment races have one auditable commit point; stale prospective inputs
  cannot masquerade as current leases or reservations.
- Historical payload validation can be replayed against exact bytes and the
  exact preloaded schema closure, independent of local caches or the network.
- Registry membership and activation remain external bindings, avoiding
  record-to-parent digest recursion.
- Existing lifecycle artifacts that bind a pre-assignment `WorkContract`, or
  that use `command_schema_id` as if it were both a payload type and a schema
  resource, remain migration blockers rather than compatibility aliases.

The schemas introduced with this decision are not admitted identities. The
current `WorkIntent`, `WorkContract`, `CommandContractRecord`, and
`CommandContractRegistry` fixtures are closed structural candidates with
unresolved canonical identities. Therefore no current fixture proves an
assignable intent, a successful assignment commit, an assigned work contract,
an admitted command member, or an active command registry. Envelope, receipt,
policy-decision, and admission-evidence candidates that depend on that command
registry are likewise nonconstructible until those exact identities and
membership proofs exist. Reissuing a schema resource does not silently migrate
historical consumers; each consumer must name an exact retained predecessor or
be reissued after its dependency is admitted.

## Rejected alternatives

### Put lease and reservation references in WorkIntent

Rejected because prospective planning may outlive those mutable facts and
would allocate or fabricate authority before the assignment transaction.

### Let WorkContract be both proposal and assignment output

Rejected because the same bytes would have to mean both “desired work” and
“committed worker boundary,” making currentness, cancellation, and replay
ambiguous.

### Use one schema ID and one digest for every identity layer

Rejected because logical type, schema resource, source bytes, canonical bytes,
and transitive closure answer different verification questions. One value
cannot prove all five relations.

### Resolve `$ref` over the network

Rejected because validation would depend on mutable remote state, availability,
redirects, and retrieval policy. Network-disabled preloading is mandatory.

## Falsifiers and acceptance evidence

Keep this decision proposed if any of the following remains true:

- a logical payload type can be accepted without exact resource, dialect,
  blob, canonical, and closure identity;
- a schema reference can trigger network access or resolve outside the
  preloaded closure;
- changing schema bytes or closure preserves an already admitted resource ID;
- a record embeds its parent registry, membership proof, activation, or
  generated envelope digest;
- a WorkIntent requires or grants an active lease, reservation, grant,
  dispatch, materialization, or spend authority;
- a WorkContract can exist without the exact successful
  `verification.assign` commit; or
- work crosses an execution boundary from assignment or WorkContract alone.

Acceptance requires closed valid and adversarial schemas, two independent
closure/digest resolvers with network disabled, assignment/expiry/revocation
race traces, replay across retained historical schema closures, lifecycle
migration without digest cycles, independent security/distributed-systems
review, and Daniel's signature on the exact Gate A candidate. It authorizes no
runtime, external effect, spending, or scientific conclusion.
