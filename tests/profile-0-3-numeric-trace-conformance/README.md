# PRQ-002F: raw-aware numeric trace conformance for the exact `odeya-jcs-0.3` cohort

This suite retains the bounded two-implementation evidence required by
[ADR 0106](../../docs/decisions/0106-prove-raw-aware-numeric-trace-conformance-for-the-0-3-cohort.md):
a complete recomputation of the static numeric-position inventory from the
twelve final `odeya-jcs-0.3` schema byte strings, an explicit typed
schema-document/metaschema settlement, complete raw-aware applicability
traces for the fifteen frozen construction subjects, and one complete
cross-object conformance pass over the exact cohort, executed through two
source- and language-separated zero-dependency implementations.

## Two implementations, three subject-census copies

`python/runner.py` (CPython 3.14.2) and `node/runner.mjs` (Node.js 24.18.0)
are source-separated: neither consumes the other's source or result, neither
reads any private expectation, and each hard-codes the complete fifteen-row
subject census — role, repository path, raw SHA-256, and decimal byte count —
independently of the shared answer-free `input-manifest.json`. A missing,
added, duplicated, reordered, or rebound subject row therefore cannot become
two-implementation consensus by mutating one shared file.

The Python path parses with the standard library under a strict
duplicate-refusing, float-refusing configuration and reconciles a separate
string-aware raw-octet number scan against the parsed document walk. The Node
path never calls `JSON.parse`; it parses every subject with its own
recursive-descent reader that refuses duplicate member names, non-integer
number lexemes, lexical negative zero, and out-of-range integers at the
token. Both emit one deterministic projection; agreement is exact-byte
equality of the two projections, bound by the external comparison receipt
written last.

## What the projection contains

- the recomputed static inventory comparison: per-schema token censuses,
  position digests, and cohort totals, recomputed from raw bytes and required
  to equal the retained inventory inside the final profile core;
- the metaschema settlement: every numeric literal in the twelve schema
  documents is `schema_definition_data_not_instance_position`, and metaschema
  evaluation is the explicit typed disposition
  `blocked_out_of_cohort_metaschema_not_retained` — blocked, never zero;
- fifteen raw-aware traces binding every raw number lexeme to its unique
  RFC 6901 pointer and, for the three record subjects, to exactly one final
  rule under the fixed precedence `recursive_integer_valued_const_leaf` over
  `integer_type`, with every applicable assertion row carrying the resolved
  schema `$id`, raw digest, and assertion location; and
- the cross-object conformance results: each record validates against its
  governing profile-control schema through a closed-vocabulary evaluator that
  refuses unknown keywords rather than ignoring them, and the retained
  fifteen-node, eighteen-edge digest dependency graph is re-verified with
  every byte citation recomputed from the exact cohort bytes.

## Validator and known-bads

`scripts/validate_profile_0_3_numeric_trace_conformance.py` is the dedicated
parent validator and a deliberate third implementation of the deep content
checks. Its static mode re-derives token policy, inventory recomputation,
record conformance, and citation closure from current repository bytes before
it checks any digest census, so a deep mutation trips the deep guard rather
than dying at a byte-binding comparison; it then verifies the retained
results, execution receipts, and comparison receipt, and finally executes its
embedded known-bad corpus, in which every mutation must return its declared
singleton refusal code. `--recompute-all` re-executes both runners with
explicitly selected executables and requires fresh stdout to equal the
retained result bytes exactly.

The runners' own hard-coded census guards fire before their deep guards, so a
subject mutation reaching a runner refuses at the byte binding first. The
deep-guard reachability proof for this suite therefore lives in the
validator's third path; this is a named design boundary, not an oversight.

## Claim boundary

The execution receipts are self-attested byte-consistency records, not
independently witnessed process evidence. This suite establishes no RFC 8785
serialization conformance, no generic `type: number` semantics, no
conformance for any resource outside the fifteen subjects, no complete
offline resolution beyond the exact cohort, no organizational independence,
no independent-host reproduction, no product identity, no profile issuance,
no admission, no PRQ-002 closure, no Gate A acceptance, and no runtime or
publication authority.
