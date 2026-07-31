# ADR 0107: Prove profile-bounded JCS serialization conformance for `odeya-jcs-0.3`

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-31
- Decision owners: canonical identity, schema contracts, replay, security
- Gate effect: retains one bounded two-implementation serialization
  conformance observation for the exact RFC 8785 interpretation that
  `odeya-jcs-0.3` pins, restricted to the profile's admitted token set; does
  not canonicalize any cohort subject, compute a product digest, issue or
  admit a profile, close PRQ-002, accept Gate A, or authorize runtime work

## Context

[ADR 0103](0103-construct-side-by-side-odeya-jcs-0-3-candidate.md) pinned the
`odeya-jcs-0.3` serialization interpretation exactly: RFC 8785 with verified
errata 6292 and 7920 only; ECMA-262 10th edition (2019) string output through
section 24.5.2.2; U+002F accepted escaped or unescaped and emitted unescaped;
recursive object-member ordering by unsigned UTF-16 code units over decoded
names; unchanged array order; no Unicode normalization of any kind; strict
I-JSON surrogate and noncharacter refusal; and a deterministic refusal for
every lexical negative zero. [ADR
0106](0106-prove-raw-aware-numeric-trace-conformance-for-the-0-3-cohort.md)
then proved raw-aware numeric applicability for the fifteen frozen
construction subjects. Neither decision retained executable evidence that two
independent implementations of the pinned serialization itself agree, or that
its refusal boundaries fire.

The profile's raw-number contract admits only integer tokens in the inclusive
safe range `[-9007199254740991, 9007199254740991]`. Every number the profile
can ever serialize is therefore an exact decimal integer string, and the
general ECMAScript binary64 shortest-round-trip serialization — including its
exponent thresholds and the double-precision vectors in RFC 8785's appendix —
is intentionally outside this tranche. That restriction is the profile
speaking, not a shortcut: a `type: number` position refuses before
serialization is ever reached.

## Decision

### Freeze one profile-bounded serialization conformance suite

Retain the suite `tests/profile-0-3-jcs-conformance/` with the dedicated
validator `scripts/validate_profile_0_3_jcs_conformance.py` and exactly two
zero-third-party-dependency, source- and language-separated implementations:
a CPython 3.14.2 serializer and a Node.js 24.18.0 serializer. Neither
consumes the other's source or result, and neither reads the suite's private
expectation file. Each implements the complete pinned pipeline: strict raw
UTF-8 decoding with BOM refusal; strict RFC 8259 grammar with duplicate
decoded-name refusal, including names equal only after escape processing;
I-JSON surrogate and noncharacter refusal; profile raw-number admission with
integral-fraction, exponent, lexical-negative-zero, and out-of-range refusal;
recursive member ordering by unsigned UTF-16 code units over decoded names;
ECMAScript-2019 string escaping with U+002F emitted unescaped; exact decimal
integer emission; and final UTF-8 canonical bytes.

The Python implementation must realize UTF-16 code-unit ordering explicitly
rather than by native code-point string comparison, because the two orders
disagree exactly where supplementary-plane names meet names in
`[U+E000, U+FFFF]`; the corpus makes that disagreement a discriminating
vector, so a naive code-point sort cannot pass.

### Drive an answer-free deterministic vector corpus

An authoring generator deterministically produces opaque, answer-free frames
in `vectors.json` and a private expectation file `cases.json` that no
implementation may read. Accepted frames cover at least: member ordering
across BMP, private-use, and supplementary-plane names, including the
UTF-16-versus-code-point discriminator; input escape forms that must decode
and re-serialize canonically, including `\u`-escaped ASCII, escaped and
unescaped U+002F, and paired UTF-16 escapes for supplementary characters;
literal non-ASCII passthrough without normalization, including canonically
equivalent but code-point-distinct spellings that must stay distinct; control
character short escapes and `\u00XX` fallbacks; empty objects and arrays,
nesting, and array-order preservation; and the exact safe-integer boundary
values. Refused frames cover at least: integral fraction and exponent
spellings, lexical negative zero, out-of-range integers, non-finite
literals, duplicate decoded names including escape-equal duplicates, a
leading BOM, trailing content, lone and unpaired surrogates, Unicode
noncharacters, invalid UTF-8 bytes, and unescaped control characters. Every
refusal returns a declared singleton code from a frozen vocabulary.

Each implementation emits one deterministic projection binding, per frame,
the frame identity, disposition, canonical output as lowercase hexadecimal
bytes with its SHA-256 and decimal byte count, or the exact refusal code.
Agreement is exact-byte equality of the two projections, bound by an
external comparison receipt written last, with execution receipts that remain
self-attested byte-consistency records.

### Validate with a third path and known-bads

The dedicated validator re-derives every expectation from the retained
vectors with its own implementation before checking any byte census,
verifies the retained results, receipts, and comparison receipt, executes an
embedded known-bad corpus in which every mutation refuses with its declared
singleton code, and supports `--recompute-all` re-execution of both runners
with explicitly selected executables against the retained result bytes.

## Required evidence before any broader claim

The suite retains known-bads that make at least these boundaries
load-bearing: vector or expectation tampering, dropped or duplicated frames,
canonical-output tampering, wrong-disposition substitution, ordering-rule
downgrade to code-point comparison, escape-policy drift, refusal-code
substitution, projection divergence, result cross-copying, receipt and
comparison binding drift, integral-float census smuggling, and any flip of a
false conformance, identity, issuance, or authority nonclaim.

Passing establishes only that the two retained implementations and the
validator's third path agree on the pinned interpretation for the exact
retained corpus, and that the retained refusal boundaries fire.

## Non-decisions

This decision does not:

- canonicalize, digest, or commit any of the fifteen frozen construction
  subjects or any product subject; no product digest, member, commitment,
  snapshot, root, or activation exists;
- establish general RFC 8785 conformance for non-integer numbers, ECMAScript
  binary64 serialization, or any token the profile refuses;
- amend, issue, admit, migrate, or reinterpret any frozen profile byte;
- establish organizational independence, independent-host reproduction,
  causal historical execution, accountable review, or operator acceptance;
- close PRQ-002 or any other prerequisite, accept Gate A, or authorize
  implementation; or
- authorize runtime, deployment, credentials, spending, data access,
  scientific or product publication, or any external effect beyond the
  separately governed architecture-repository publication of the retaining
  commit itself.

## Consequences

The pinned serialization stops being prose: both its acceptance surface and
its refusal surface now carry dual-implementation, byte-identical, replayable
evidence, and the classic JCS ordering trap is a retained discriminating
vector rather than a latent divergence. The deliberate cost is the
profile-bounded number scope. The next dependencies remain the nine
product-domain frames, dependency-closed offline resolution and cross-object
product replay, accountable review, and Daniel's exact-byte decision.
