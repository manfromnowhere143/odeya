# ADR 0106: Prove raw-aware numeric trace conformance for the exact `odeya-jcs-0.3` cohort

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-31
- Decision owners: canonical identity, schema contracts, registries, replay,
  security
- Gate effect: retains one bounded two-implementation numeric-trace and
  cross-object conformance observation over the exact fifteen frozen
  `odeya-jcs-0.3` construction subjects; does not issue or admit a profile,
  compute a product identity, close PRQ-002, accept Gate A, or authorize
  runtime work

## Context

[ADR 0103](0103-construct-side-by-side-odeya-jcs-0-3-candidate.md) froze the
`odeya-jcs-0.3` construction graph: twelve final-only schema resources, nine
structural-nonidentity fixtures, and three ordered records, observed by two
source-separated observers whose seven-output transaction bound the fifteen
immutable schema-and-record subjects byte-for-byte. Its static numeric
applicability inventory is retained inside the final profile core, derived
from the twelve final schema byte strings only. ADR 0103 also named the two
evidence layers that construction deliberately left absent: complete
per-subject raw-aware applicability traces, and source-separated cross-object
conformance over the exact cohort.

The current session handoff names those absences as the sole next mission:
recompute and compare the complete static numeric-position inventory through
two source- and language-separated paths; settle schema-document and
metaschema treatment explicitly; construct complete raw-aware applicability
traces for exactly the fifteen immutable subjects; and execute two source- and
language-separated complete cross-object conformance paths over the exact
cohort.

This decision freezes that tranche as one bounded architecture-evidence suite.
It is trace and conformance evidence about exact frozen bytes. It cannot
amend those bytes, and its passing establishes neither profile issuance nor
product identity.

## Decision

### Freeze one raw-aware numeric-trace conformance suite

Retain the suite `tests/profile-0-3-numeric-trace-conformance/` with the
contract pair
`architecture/prq-002f-numeric-trace-conformance-contract.schema.json` and
`architecture/prq-002f-numeric-trace-conformance-contract-v1-candidate.json`,
the dedicated validator
`scripts/validate_profile_0_3_numeric_trace_conformance.py`, and exactly two
zero-third-party-dependency implementations: a CPython 3.14.2 runner and a
Node.js 24.18.0 runner. The implementations are source- and
language-separated: neither consumes the other's source, result, or any
private expectation, and each hard-codes the complete fifteen-row subject
census independently of the shared answer-free input manifest, so a missing,
added, duplicated, or reordered subject row cannot become consensus by
mutating one shared file.

The fifteen subjects are exactly ADR 0103's fifteen immutable
schema-and-record subjects — the twelve final `odeya-jcs-0.3` schema
resources and the three ordered candidate records — bound by repository path,
raw SHA-256, and decimal byte count. Every subject read verifies raw bytes
before decoding. No subject byte is written, and no retained artifact of this
suite enters any subject.

### Recompute the static inventory from bytes, not from the record

Each implementation independently recomputes the complete static
numeric-position inventory from the twelve final schema byte strings: the
ordered raw number-token census of each schema document, the integer-type
assertion rows, the recursive integer-valued-`const` leaf rows, the expanded
instance integer-type and integer-`const` position rows across applicable
`$ref`, `allOf`, conditional, array, and compound-`const` paths, and the
resolved in-cohort reference edges. Each implementation then compares its
recomputation against the retained inventory inside the final profile core,
field by field and count by count, including the per-schema token-inventory
and position-inventory digests. Any divergence between recomputation and the
retained inventory refuses. A `type: number` position, a union admitting
`number`, an integer-valued `enum` outside an integer-type position, or any
otherwise unclassified numeric position also refuses, independently of the
retained record's claims.

### Settle schema-document and metaschema treatment explicitly

Numeric literals inside a schema document are schema-definition data, not
governed instance positions. Every raw number token in each of the twelve
schema-document subjects is traced to its unique RFC 6901 document pointer
and classified `schema_definition_data_not_instance_position`, and each
schema-document trace must reconcile exactly — token for token, in document
order — with that schema's retained document-token census.

Evaluating a schema document as an instance against the JSON Schema Draft
2020-12 metaschema would require the metaschema itself as a retained,
digest-bound cohort resource. The metaschema is not in the cohort, and this
suite performs no network, file-search, environment, or fallback resolution.
Metaschema evaluation is therefore recorded as an explicit typed blocked
disposition, `blocked_out_of_cohort_metaschema_not_retained`, on every
schema-document trace. Blocked is not zero, not a pass, and not a claim that
metaschema validation happened. This settles the treatment: no schema-document
numeric literal can be silently promoted to a governed instance position, and
no absent metaschema evaluation can be silently rendered as evidence.

### Construct complete raw-aware traces for exactly fifteen subjects

For each subject, each implementation scans the raw octets for every JSON
number lexeme outside string context, walks the strictly parsed document for
every integer value position, and requires the two sequences to reconcile
one-to-one in document order. Each trace row binds the subject's repository
path, raw SHA-256, and decimal byte count; the token ordinal; the exact raw
lexeme and decimal value; and the unique RFC 6901 pointer. Every admitted
token satisfies ADR 0101's integer-token rule and safe range
`[-9007199254740991, 9007199254740991]`; integral fraction and exponent
spellings, lexical negative zero, overlength tokens, and out-of-range values
refuse.

For the three record subjects, each token's pointer is additionally resolved
through a closed applicability evaluation against the record's governing
profile-control schema, using only the exact twelve-schema cohort as the
reference universe. The applicable assertion rows bind the resolved schema
`$id`, the resolved schema's raw SHA-256, the assertion schema location, and
the position rule. Exactly one final rule per token is admitted under the
fixed precedence `recursive_integer_valued_const_leaf` over `integer_type`.
A token with no applicable rule, a pointer resolved through any alias,
bare-ID, `latest`, network, file-search, environment, or fallback mechanism, a
reference target outside the exact cohort, an omitted token, or a duplicated
pointer refuses the whole projection.

### Execute two complete cross-object conformance paths

Each implementation validates each of the three record subjects against its
governing profile-control schema with a closed-vocabulary evaluator that
implements exactly the assertion and applicator keywords present in the
twelve-schema cohort and refuses any schema keyword outside that closed
vocabulary rather than ignoring it. Each implementation also recomputes the
complete digest dependency graph over the fifteen subjects: every cited raw
digest and byte count in the three records is recomputed from the exact
cohort bytes; edges must match the retained fifteen-node graph exactly; and a
self edge, a downstream edge, an out-of-cohort target, or a placeholder
binding refuses.

Each implementation emits one complete deterministic projection containing
its recomputed inventory comparison, the fifteen subject traces, and the
cross-object conformance results. An external comparison receipt, written
last, binds both projections byte-for-byte along with the suite manifest,
input manifest, contract pair, both source manifests, both execution
receipts, and the dedicated validator. All retained counts are decimal
strings, so an integral float cannot satisfy a count field.

## Required evidence before any broader claim

The suite retains known-bad mutations that make at least these boundaries
load-bearing, each executing the production guard and returning its declared
refusal:

- subject census and binding: dropped, duplicated, reordered, added,
  digest-mismatched, and byte-count-mismatched subject rows;
- inventory recomputation: mutated schema bytes introducing `type: number`,
  a number-admitting union, or a stray integer `enum`; a tampered retained
  inventory row, count, or digest; and a stale retained inventory;
- raw tokens and pointers: integral fraction and exponent spellings, lexical
  negative zero, out-of-range integers, omitted tokens, duplicated pointers,
  and string-embedded digits that must not be counted;
- classification: a token with zero applicable rules, an out-of-cohort
  reference, a fallback-resolved pointer, a flipped metaschema disposition,
  and a final-rule ambiguity outside the fixed precedence;
- conformance: a schema-invalid record mutation, an unimplemented schema
  keyword, a broken digest-graph edge, a self edge, and a downstream edge;
- observation integrity: source-manifest drift, peer source or result
  consumption, execution-receipt binding mismatch, projection divergence
  between implementations, integral-float census smuggling, and a copied
  cross-labelled projection; and
- authority: any flip of a false conformance-completion, identity, issuance,
  admission, PRQ-002-closure, Gate A, runtime, or publication nonclaim.

Passing those cases establishes only that the named guards fire for the
retained mutations under this suite's execution.

## Non-decisions

This decision does not:

- amend, issue, admit, migrate, reinterpret, or retire any `odeya-jcs`
  profile, schema resource, record, or fixture, all of which remain frozen;
- establish generic `type: number` semantics, nine-domain product framing,
  ordered-map law conformance, complete offline resolution beyond the exact
  cohort, or conformance for any resource outside the fifteen subjects;
- prove RFC 8785 serialization conformance, compute or retain any product
  digest, member, commitment, snapshot, root, or activation;
- establish organizational independence, independent-host reproduction,
  causal historical execution, accountable review, or operator acceptance;
  the execution receipts remain self-attested byte-consistency records;
- close PRQ-002 or any other prerequisite, accept Gate A, or authorize
  implementation; or
- authorize runtime, deployment, credentials, spending, data access,
  scientific or product publication, or any external effect.

Architecture-repository publication remains a separately authorized
exact-commit process.

## Consequences

The `odeya-jcs-0.3` numeric boundary becomes end-to-end falsifiable for the
exact cohort: every raw number token in all fifteen frozen subjects now has a
dual-implementation chain from raw lexeme to digest-bound schema rule, the
schema-document/metaschema distinction is an explicit typed disposition
rather than an implicit convention, and cross-object record conformance is
recomputed rather than asserted. The cost is a deliberately narrow scope:
nothing outside the fifteen subjects gains any conformance status, and the
next dependencies — source-separated RFC 8785 conformance, product-domain
frames, dependency-closed product replay, accountable review, and Daniel's
exact-byte decision — remain open and unstarted.
