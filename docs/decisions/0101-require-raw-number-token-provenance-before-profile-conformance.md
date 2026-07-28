# ADR 0101: Require raw-number token provenance before profile conformance

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-28
- Decision owners: canonical identity, schema contracts, replay, security
- Gate effect: blocks conformance and issuance of the PRQ-002B profile
  candidate until a future side-by-side profile revision incorporates a
  source-separated observed raw-number rule; does not compute a product digest,
  close PRQ-002, accept Gate A, or authorize runtime work

## Context

ADR 0100 froze the exact bytes of the unissued
`urn:odeya:canonicalization:odeya-jcs-0.2` candidate before product identity
construction. Adversarial review then found that its prose and current Python
checker assume a distinction that its parser contract does not make portable.

Draft 2020-12 defines an integer by mathematical value, so `1`, `1.0`, and
`1e0` can all satisfy `type: integer`. Python's ordinary JSON parser retains an
`int`/`float` distinction for those tokens, while JavaScript's `JSON.parse`
maps all three to one `Number` value. RFC 8785 then serializes their binary64
value as `1`. A Python-only `type(value) is int` check therefore does not prove
a source-separated profile rule.

This is an interoperability blocker, not a reason to weaken retained
evidence. The `0.2.0` core, its external binding, all twelve successor schema
resources, the migration candidate, and the nine structural-nonidentity
fixtures remain byte-for-byte unchanged and unissued.

## Decision

### Preserve number-token provenance before mapping

Adopt the architecture-only candidate contract at
[`architecture/canonicalization-raw-number-token-contract-v1-candidate.json`](../../architecture/canonicalization-raw-number-token-contract-v1-candidate.json),
validated by
[`architecture/canonicalization-raw-number-token-contract.schema.json`](../../architecture/canonicalization-raw-number-token-contract.schema.json).
It is not a product schema resource or an addendum that silently changes the
frozen `0.2.0` profile.

The selected rule classifies every RFC 8259 number token immediately after
UTF-8 and JSON lexing and before mapping or schema type evaluation:

- an integer token matches `^-?(?:0|[1-9][0-9]*)$`;
- a number token is a valid JSON number containing a fraction or exponent;
- any token with a negative sign and an exactly zero decimal significand,
  including `-0`, `-0.0`, and `-0e+9`, is refused before host conversion;
- a token longer than 128 bytes is refused;
- a valid nonzero decimal token whose binary64 conversion underflows to
  positive or negative zero is refused;
- a token whose binary64 conversion is non-finite is refused;
- raw lexeme, token class, and unique instance pointer are retained in a
  validation sidecar until projection construction; and
- conversion for RFC 8785 serialization must produce a finite IEEE-754
  binary64 value.

The validation sidecar is never inserted into the projection or digest
preimage. It supplies type evidence; it does not create a new identity member.
The exact resolved applicable schema—not token metadata—determines which
position rule applies.

Where an applicable Odeya contract asserts `type: integer` or an
integer-valued `const`, only an integer token in the inclusive range
`[-9007199254740991, 9007199254740991]` is admitted. An integral fraction or
exponent such as `1.0` or `1e0` is refused at that position. An integer-valued
`const` then compares the exact decimal integer value. A Boolean is not an
integer.

The remaining semantics for positions that admit `type: number` are unresolved
by this unit, beyond the global length, negative-zero, non-finite, and underflow
refusals above. The fixed microframes exercise integer-type and integer-const
positions only; they cannot be cited as number-position evidence.

This is an explicit Odeya profile restriction stricter than Draft 2020-12's
mathematical integer semantics. A future profile core and its declaring
schemas must name and bind that restriction before any product identity is
computed. The current `0.2.0` candidate does not yet do so and cannot be called
conformant or issued.

### Observe the decision in two non-sharing implementations

The first evidence unit is intentionally smaller than full nine-domain
conformance. `tests/product-identity-raw-number-typing/` uses answer-free raw
byte vectors and two fixed two-member, synthetic, non-product frames. Its
child-visible vector IDs are opaque and every decoded input is bound by digest
and byte count. Descriptive names and outcomes exist only in the comparator
expectation manifest. The Python child uses standard-library JSON parse hooks
that retain raw numeric lexemes. The Node.js child uses a source-distinct
recursive-descent parser and a different runtime. Neither child receives the
expectation manifest or peer output in its argv or declared input manifest.

The executions do not establish an OS-level filesystem sandbox. The source
manifests and source inspection prove only that the retained child source
declares and requests no expectation or peer read; they do not exclude
dynamically constructed paths or filesystem discovery. The retained execution
receipts are self-attested byte-consistency records rather than independently
witnessed historical process captures. Current recomputation executes both
children with fresh challenges and requires byte-for-byte result equality.

The fixed frames associate the token with one known `integer_value` position.
They do not prove the contract's generic unique-instance-pointer retention or
resolution rule.

The comparator must bind every vector and compare the complete ordered result
projection. Retained known-bads must demonstrate refusal of answer leakage,
undeclared peer-result path references, stale implementation-causal bindings,
incomplete or reordered results, outcome/code substitution, source or runtime
drift, stale challenges, evidence substitution, unclassified crashes, and any
authority or product-identity claim.

The stale-binding known-bad relabels a copied result without recomputing its
public causal-binding formula. It proves only that an internally inconsistent
binding is refused. A coherently relabelled copy can recompute that formula and
remain byte-identical to the peer result, so coherent peer-output substitution
refusal and causal execution origin remain unproved without an independent
execution witness. Fresh recomputation executes both current children; it does
not retroactively witness the retained historical processes.

These meta-attacks exercise the evidence, comparator, source-binding, and
explicit nonclaim gates. They are not evaluator-source ablations of each
semantic branch; the vector outcomes and current recomputation are bounded
behavioral observations.

A green micro-suite proves only bounded agreement on the selected raw-number
rule and fixed synthetic frames. It does not prove generic schema-path
evaluation, full RFC 8785 correctness, any of the nine product-domain framing
contracts, ordered-member-map laws, cross-object replay, a complete offline
schema registry, organizational independence, or independent-host
reproduction. It also does not prove generic instance-pointer retention,
exclude dynamic path discovery, or independently witness the historical
retained executions.

### Freeze refusal precedence

When more than one defect is present, evaluators use this precedence:

1. `ODEYA_PARSE_UTF8`;
2. `ODEYA_PARSE_BOM`;
3. `ODEYA_PARSE_SYNTAX`;
4. `ODEYA_PARSE_DUPLICATE_KEY`;
5. `ODEYA_PARSE_UNPAIRED_SURROGATE`;
6. `ODEYA_CONFORMANCE_FRAME_SHAPE`;
7. `ODEYA_SCHEMA_TYPE`;
8. `ODEYA_LIMIT_NUMBER_TOKEN`;
9. `ODEYA_NUMBER_NEGATIVE_ZERO`;
10. `ODEYA_NUMBER_NONFINITE`;
11. `ODEYA_NUMBER_UNDERFLOW`;
12. `ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED`;
13. `ODEYA_NUMBER_DOMAIN`;
14. `ODEYA_SCHEMA_CONST`; then
15. acceptance.

UTF-8 decoding therefore precedes BOM classification, and complete JSON
grammar validity precedes the two post-parse restrictions on duplicate decoded
object names and unpaired Unicode surrogates. This ordering makes every
retained refusal comparable across implementations and prevents an incidental
later guard from being credited for an earlier failure.

## Non-decisions

This decision does not:

- mutate or issue `odeya-jcs-0.2` or any predecessor;
- create, reissue, admit, or retire a product schema resource;
- canonicalize any retained structural-nonidentity fixture;
- compute or retain a product member, commitment, snapshot, root, or identity;
- prove full parser, JSON Schema, RFC 8785, domain-framing, migration, or replay
  conformance;
- resolve ordered-map counts, ordering, uniqueness, or derived-key laws;
- close the offline resolver or historical-retention blocker;
- provide accountable review or Daniel's exact-byte acceptance; or
- authorize runtime, deployment, external effects, publication, spending, or
  data access.

## Consequences

The candidate architecture now has a falsifiable answer to the cross-language
integer ambiguity without rewriting frozen evidence. The cost is explicit:
PRQ-002B cannot advance to broad successor-profile conformance until a new,
side-by-side profile revision and its dependent schema references integrate
the rule. That revision is reserved prospectively as
`urn:odeya:canonicalization:odeya-jcs-0.3`, version `0.3.0`; this decision does
not create it.

The future `0.3` tranche must create a complete new core, core schema, evidence
schema and record, migration schema and record, and twelve-resource successor
cohort. All nine product declaring schemas must receive new schema IDs and new
domains because their current bytes const-bind the `0.2` profile and `0.6`
core-schema ID. `0.2` and `0.3` identities may never be equated, inherited, or
implicitly upcast. The retained `0.2` bytes remain immutable, unissued
historical candidate evidence and may appear only as an exact predecessor.

After the raw-number observation, the next smallest vertical replay unit is a
non-product, prehash two-member schema-registry bundle that proves count,
ordering, unique-key, key/body, digest/body, and exact resolver substitutions.
Only after those prerequisites should the nine-domain framing suite and the
checkpoint-bound content-addressed offline archive be attempted.
