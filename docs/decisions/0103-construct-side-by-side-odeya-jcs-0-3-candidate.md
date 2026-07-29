# ADR 0103: Construct a side-by-side `odeya-jcs-0.3` candidate

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-29
- Decision owners: canonical identity, schema contracts, registries, replay,
  security
- Gate effect: freezes one bounded architecture-only `odeya-jcs-0.3`
  construction graph; does not establish conformance, compute a product
  identity, issue or admit a profile or resource, close PRQ-002, accept Gate A,
  or authorize runtime work

## Context

[ADR 0100](0100-introduce-an-unissued-scoped-product-identity-profile-successor.md)
retains an exact, unissued `urn:odeya:canonicalization:odeya-jcs-0.2`
candidate and twelve schema resources. [ADR
0101](0101-require-raw-number-token-provenance-before-profile-conformance.md)
then demonstrated that ordinary host parsing loses the lexical distinction
between an integer token and an integral fraction or exponent token. Its
bounded two-language evidence covers only integer-type and
integer-valued-`const` microframes. [ADR
0102](0102-prove-non-product-prehash-schema-registry-replay.md) separately
retains a two-member prehash replay before any structured or product identity.

Those prerequisites cannot amend `odeya-jcs-0.2` after its bytes were frozen.
The next profile-level unit therefore needs a new profile namespace, new
schema identities and product domains, an exact raw-octet input boundary, and
an acyclic finalization order. It must also preserve the distinction between
JSON Schema's arbitrary-precision mathematical number model and JCS's
IEEE-754 binary64 serialization model rather than letting a host parser choose
the answer implicitly.

This decision is an artifact-construction freeze only. The listed schemas and
records are candidates for later conformance and review; their existence
cannot establish that their rules are correct or that any product subject has
been identified.

## Decision

### Create one non-aliasing successor namespace

Reserve the unissued candidate profile
`urn:odeya:canonicalization:odeya-jcs-0.3`, version `0.3.0`. It is a
side-by-side successor to `odeya-jcs-0.2`, not an alias, patch, addendum,
redirect, implicit upcast, or reinterpretation of predecessor bytes.

The construction inventory is closed at the following twelve schema
resources. The nine product-domain rows receive both a new schema ID and a
domain disjoint from their `0.2` predecessor. The three profile-control
schemas declare no product digest domain.

| Repository path | Exact `$id` | Exact product domain or role |
|---|---|---|
| `schemas/schema-resource-record-v0-2.schema.json` | `urn:odeya:schema:schema-resource-record:0.2.0` | `odeya-schema-resource-record-v2` |
| `schemas/aggregate-state-subject-record-v0-2.schema.json` | `urn:odeya:schema:aggregate-state-subject-record:0.2.0` | `odeya-aggregate-state-subject-record-v2` |
| `schemas/reducer-contract-record-v0-2.schema.json` | `urn:odeya:schema:reducer-contract-record:0.2.0` | `odeya-reducer-contract-record-v2` |
| `schemas/event-contract-record-v0-2.schema.json` | `urn:odeya:schema:event-contract-record:0.2.0` | `odeya-event-contract-record-v2` |
| `schemas/ordered-member-map-commitment-v0-2.schema.json` | `urn:odeya:schema:ordered-member-map-commitment:0.2.0` | `odeya-ordered-member-map-commitment-v2` |
| `schemas/schema-registry-v0-9.schema.json` | `urn:odeya:schema:schema-registry:0.9.0` | `odeya-schema-registry-v3` |
| `schemas/aggregate-state-subject-registry-v0-8.schema.json` | `urn:odeya:schema:aggregate-state-subject-registry:0.8.0` | `odeya-aggregate-state-subject-registry-v3` |
| `schemas/reducer-registry-v0-8.schema.json` | `urn:odeya:schema:reducer-registry:0.8.0` | `odeya-reducer-registry-v3` |
| `schemas/event-contract-registry-v0-8.schema.json` | `urn:odeya:schema:event-contract-registry:0.8.0` | `odeya-event-contract-registry-v3` |
| `schemas/canonicalization-profile-core-v0-7.schema.json` | `urn:odeya:schema:canonicalization-profile-core:0.7.0` | final-only profile-core schema; no product domain |
| `schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json` | `urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0` | final-only external-evidence schema; no product domain |
| `schemas/canonicalization-profile-migration-v0-2.schema.json` | `urn:odeya:schema:canonicalization-profile-migration:0.2.0` | final-only migration schema; no product domain |

The corresponding architecture records are exactly:

- `architecture/canonicalization-profile-core-0.3-candidate.json`;
- `architecture/canonicalization-profile-0.3-candidate-evidence.json`; and
- `architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json`.

No predecessor path, `$id`, domain, profile reference, raw digest, byte count,
or artifact byte may be overwritten or redirected. The exact `0.2` core,
evidence, migration, and twelve-schema cohort remain immutable and unissued.
The side-by-side census becomes 120 original resources, 12 frozen `0.2`
resources, and 12 new `0.3` resources: 144 product-schema resources in the
measured repository partition. This count is an inventory assertion, not an
admission or migration result.

The ordered-map algorithm identifier remains
`odeya-canonical-map-commitment-v1` intentionally. It identifies the
profile-independent construction over the canonical ordered sequence of UTF-8
member-key/member-digest pairs; it does not consume raw JSON or define JCS
semantics. The reissue changes the profile-bound member-digest inputs and the
commitment resource's product domain to
`odeya-ordered-member-map-commitment-v2`, not that map algorithm.

Five namespaces remain non-interchangeable: the map algorithm identifier, the
hash algorithm identifier `sha-256`, the lexical digest form
`sha256:<64 lowercase hexadecimal digits>`, the canonicalization profile ID,
and the product domain separator. Substitution among them refuses. If a future
map algorithm consumes canonicalization semantics, it requires a new
algorithm identifier and a separate invariant decision.

### Put an authoritative raw-octet adapter before the canonicalizer

The `0.3` candidate separates a strict raw-octet adapter from the RFC 8785
canonicalizer core. An ordinary host JSON parser is not authoritative for
duplicate-name detection, number-token classification, source position, or
decimal-to-binary64 conversion.

For each candidate subject, the adapter must:

1. retain the raw octets, decimal byte count, and SHA-256 raw-byte binding and,
   when an expected resource binding exists, compare it before decoding;
2. decode only strict UTF-8 under [RFC
   3629](https://www.rfc-editor.org/rfc/rfc3629.html), reject a leading byte
   order mark, and parse exactly one complete JSON value with no trailing
   non-whitespace value or extension;
3. apply the published [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html)
   grammar without accepting comments, trailing commas, non-finite numbers, or
   host-language extensions;
4. detect duplicate decoded object names before materializing a lossy object
   map, including names that become equal only after JSON escape processing;
5. enforce [I-JSON RFC 7493 section
   2.1](https://www.rfc-editor.org/rfc/rfc7493.html#section-2.1): string
   values and decoded member names contain neither surrogate nor Unicode
   noncharacter code points; Odeya makes either violation a deterministic
   refusal, while a correctly paired UTF-16 escape is decoded to its scalar
   value; and
6. retain a lossless token tree or equivalent sidecar carrying every raw
   number lexeme and its unique [RFC
   6901](https://www.rfc-editor.org/rfc/rfc6901.html) instance pointer until
   applicability and projection checks complete.

The adapter passes only the validated value and bound sidecar to the pure
canonicalizer. The sidecar is evidence about parsing and applicability; it is
not inserted into a product digest preimage unless an exact declaring schema
and digest contract expressly place it there.

### Pin the JSON and JCS interpretation exactly

The candidate adopts [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)
as an exact canonicalization algorithm, including only its verified [Errata
ID 6292](https://www.rfc-editor.org/errata/eid6292) and [Errata ID
7920](https://www.rfc-editor.org/errata/eid7920). EID 6292 corrects the
ECMAScript string-serialization reference to section 24.5.2.2. EID 7920 makes
an error and stop the recommended parser behavior for negative-zero input;
Odeya strengthens that recommendation to a deterministic refusal for every
lexical negative zero covered by ADR 0101.

The ECMAScript dependency is frozen to [ECMA-262, 10th edition,
2019](https://tc39.es/ecma262/2019/), not a moving current
edition. Number output follows section 7.1.12.1 including Note 2; string output
follows section 24.5.2.2 through EID 6292.

RFC errata are not inherited as an undifferentiated set. In particular, the
candidate does not adopt [RFC 8259 EID
5318](https://www.rfc-editor.org/errata/eid5318) for canonical output. RFC
8785's more specific string rule and retained example control: U+002F `/` may
be accepted escaped or unescaped on input and is emitted unescaped. A
conformance vector must freeze that precedence. This is an explicit profile
decision, not a claim that unrelated RFC 8259 errata have been accepted or
rejected.

Canonical output otherwise follows RFC 8785 exactly: no inter-token
whitespace, fixed literal and string escaping, recursive object-property
ordering by unsigned UTF-16 code units over decoded names, unchanged array
order, ECMAScript-2019 number serialization, and final UTF-8 encoding.

Decoded Unicode scalar sequences are preserved exactly. No component may
apply NFC, NFD, NFKC, NFKD, case folding, locale transformation, or any other
normalization described by [Unicode Standard Annex
15](https://www.unicode.org/reports/tr15/). Canonically equivalent but
code-point-distinct strings remain distinct inputs and may produce distinct
canonical bytes.

### Close numeric applicability for this exact cohort only

[JSON Schema Draft
2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html) defines
numbers as arbitrary-precision base-10 mathematical values and does not retain
lexical distinctions. JCS serializes finite IEEE-754 binary64 values. The
`0.3` candidate therefore does not use JSON Schema validation alone as
numeric-type or conversion evidence.

Numeric applicability has two non-cyclic evidence layers.

First, the final profile core contains one closed static schema-position
inventory derived only from the exact final bytes of the twelve schemas. Each
row binds an exact schema `$id` and raw digest, resolved schema location or
assertion, and one permitted position rule. The inventory expands applicable
`$ref`, `allOf`, `oneOf`, conditional, array, escaped-pointer, and compound
`const` paths without a subject digest or a future instance pointer. It must
show that every numeric position exposed by the exact cohort is either an
integer-type position or a recursively identified integer-valued-`const`
position. A `type: number` position, a union that admits `number`, an
unresolved branch, or any otherwise unclassified numeric position refuses the
candidate.

Second, evaluation of any concrete instance produces a downstream raw-aware
trace. Each trace binds the subject's raw digest and byte count, every raw
numeric lexeme and token class, its exact RFC 6901 instance pointer, the exact
resolved schema `$id` and raw digest, the evaluated schema location or
assertion from the static inventory, and the final position rule. The complete
trace proves that no subject token is omitted, multiply classified, or
resolved through a mutable, network, file, search, environment, bare-ID,
`latest`, or fallback lookup.

These scopes are not interchangeable:

- the static inventory classifies positions that the twelve schemas apply to
  future record instances;
- numeric literals appearing inside a schema document are schema-definition
  data, not automatically instance positions; evaluating a schema document as
  an instance against a metaschema requires its own separately bound trace;
- the nine product schemas can govern later product subjects, while the three
  profile-control schemas govern the core, evidence, and migration records;
  neither role creates a product identity; and
- a trace is produced only after its subject bytes are final. It stays outside
  that subject and is never bound by an evidence record when the evidence
  record itself is the trace subject.

At every admitted integer position, ADR 0101's integer-token rule and inclusive
range `[-9007199254740991, 9007199254740991]` apply. Integral fraction and
exponent spellings such as `1.0` and `1e0`, Booleans, lexical negative zero,
overlength tokens, underflow, and non-finite conversion are refused. After
classification, decimal-to-IEEE-754 binary64 conversion is defined by [IEEE
754-2019](https://ieeexplore.ieee.org/document/8766229) using
`roundTiesToEven`. For the admitted safe-integer cohort that conversion is
exact; the explicit rounding rule prevents a host default from becoming an
unstated future policy.

The core raw binding makes the static inventory digest-bound. Each downstream
trace is retained by exact raw digest and byte count and is bound only by a
later external inventory/comparison receipt. A missing, stale, incomplete, or
mismatched inventory or trace refuses. This rule does not establish generic
`type: number` semantics or conformance for any resource outside the exact
cohort.

### Freeze a final-only, acyclic artifact graph

The one-way dependency order is:

```text
exact frozen odeya-jcs-0.2 bytes
  -> product-authoring transaction:
       twelve final-only odeya-jcs-0.3 schema resources
         -> exact schema raw digests and byte counts
         -> static schema-position inventory inside the final core
         -> final evidence record
         -> final migration record
       plus nine schema-valid structural-nonidentity fixtures
  -> observation-authoring transaction over the immutable 15 subjects:
       two source manifests
       + two exact observer stdout results
       + two execution receipts
       + external comparison receipt replaced last
  -> later conformance work, including downstream raw-number traces
```

Every retained schema and record must be in its final branch. Required
bindings cannot be placeholders, mixed placeholder/final states, or
authoring-time `null` values. A semantic `null` remains permitted only where a
closed contract explicitly means unknown or unmeasured; it cannot stand in for
a raw digest, byte count, resolved target, result, review, or authority
decision.

The profile core does not contain its own raw digest. The evidence record binds
the final core and twelve final schemas externally. Evidence may name the
migration schema and path, but cannot depend on the later migration-record
digest or on a trace whose subject is that evidence record. The migration
record may bind the exact evidence record. Downstream traces do not enter or
change their subjects. An external manifest or comparison receipt may bind all
retained predecessors, schemas, records, sources, results, traces, and
receipts, but no artifact may include its own digest or a digest of a
downstream artifact.

Receipt-last ordering alone is not interruption evidence. Authoring must build
each complete generated transaction in a same-filesystem isolated staging
directory, validate every edge and expected byte before installation, fsync
the candidate files and staging directory, and install only validated final
bytes. The product-authoring transaction contains exactly 24 outputs: twelve
schemas, nine structural-nonidentity fixtures, and the three ordered records;
the migration record is installed last within that transaction. Only after
those 15 schema-and-record subjects are final may the separate observation
transaction retain its seven outputs: two source manifests, two exact stdout
results, two execution receipts, and the comparison receipt replaced last.

The 15 observed subjects are immutable upstream inputs to the observation
transaction, not members of its staging set. No schema, core, evidence, or
migration artifact may bind a downstream observation artifact. A reader must
recompute the complete inventory and byte edges for each transaction and
refuse a missing, mixed-generation, stale, or mismatched subject. An
interruption can leave incomplete bytes; the retained guarantee is that those
bytes cannot validate as either complete graph, not that interruption is
impossible. Downstream per-subject applicability traces are a later
conformance dependency and are deliberately absent from this construction
slice.

The migration is exactly `odeya-jcs-0.2` to `odeya-jcs-0.3`. It preserves the
exact predecessor and all 106 retained direct `odeya-jcs-0.1` consumers,
enumerates twelve exact successor dispositions, and migrates zero issued
predecessor instances within its measured input. It does not assert that no
issued instance exists outside that input, globally migrate `0.1`, or make
identities comparable across profile namespaces.

Exact resource resolution is by resource ID plus expected raw digest and byte
count, never by ID alone. The resolver verifies raw bytes before decoding,
then requires body `$id`, semantic version, registry key, and declared
dependency agreement. It has no alias, redirect, network, file, search,
environment, or mutable fallback.

## Required evidence before any broader claim

The construction slice needs retained known-bads that make at least these
boundaries load-bearing:

- predecessor-byte drift, in-place overwrite, reused `$id`, reused domain, and
  wrong domain-to-schema binding;
- missing, added, duplicated, or reordered cohort members and the wrong
  144-resource census;
- raw-digest, byte-count, body-ID, semantic-version, core-schema, core-binding,
  profile-version, and downgrade substitution;
- parse-equivalent raw reencoding, duplicate decoded names, invalid Unicode,
  normalization, slash-output, and RFC 8785 string/number/order drift;
- missing or stale numeric applicability, integer-position `1.0`/`1e0`,
  compound-`const` substitution, Boolean/integer substitution, generic
  `type: number` acceptance, and unclassified numeric acceptance;
- self-edges, downstream edges, placeholders, mixed finalization, generated
  evidence self-binding, and interrupted finalization;
- resolver fallback, fabricated offline completeness, and unknown historical
  counts changed from `null` to zero; and
- any product identity, membership, conformance, issuance, admission, root,
  activation, Gate A, runtime, deployment, or publication escalation.

Passing those cases establishes only that the named construction guards fire
for the retained mutations. Full source-separated RFC 8785 and profile
conformance, all nine product-domain frames, complete offline and historical
resolution, dependency-closed product replay, cross-object equality,
independent reproduction, accountable review, and the operator's exact-byte
decision remain later work.

## Non-decisions

This decision does not:

- amend, issue, admit, migrate, reinterpret, or retire `odeya-jcs-0.2` or any
  earlier profile;
- claim that `odeya-jcs-0.3`, an adapter, canonicalizer, parser, resolver, or
  candidate record conforms to RFC 8259, RFC 7493, RFC 8785, ECMA-262, IEEE
  754, JSON Schema, or this Odeya profile;
- compute or retain a product digest, member, ordered commitment, registry
  snapshot, membership proof, root, C0 bundle, checkpoint, P0 admission, or
  activation;
- admit a schema resource or establish product identity, profile issuance,
  complete offline resolution, historical availability, organizational
  independence, independent-host reproduction, causal execution origin,
  accountable review, or operator acceptance;
- close PRQ-002 or any other prerequisite, accept Gate A, or authorize
  implementation; or
- authorize runtime, deployment, credentials, spending, data access,
  scientific or product publication, or any external effect.

Architecture-repository publication remains a separately authorized
exact-commit process and cannot turn this candidate into conformance,
acceptance, identity, admission, or authority.

## Consequences

Odeya gains a bounded, falsifiable construction target that integrates the
observed raw-number prerequisite without rewriting frozen history. The cost is
an intentionally narrow numeric scope and a larger side-by-side schema census.
Any future `type: number` semantics, profile issuance, product-digest
observation, or migration beyond the exact predecessor must be a separately
specified and reviewed decision.

The next dependency after construction is retained source-separated
conformance over the exact final bytes, followed by complete offline
resolution, dependency-closed product members and registries, cross-object
replay, accountable review, and Daniel's exact-byte decision. Until those
steps occur, every conformance, identity, admission, issuance, Gate A, runtime,
deployment, and scientific-publication claim remains false or absent.
