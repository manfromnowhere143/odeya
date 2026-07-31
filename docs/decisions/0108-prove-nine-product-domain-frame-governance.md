# ADR 0108: Prove nine-product-domain frame governance for `odeya-jcs-0.3`

- Status: Proposed architecture candidate; not operator accepted
- Date: 2026-07-31
- Decision owners: canonical identity, schema contracts, registries, replay,
  security
- Gate effect: retains one bounded two-implementation governance observation
  over the nine frozen structural-nonidentity fixtures as instances of the
  nine `odeya-jcs-0.3` product-domain schemas, with per-domain refusal
  evidence exercised as data through both implementations; does not compute
  a product identity or digest, issue or admit anything, close PRQ-002,
  accept Gate A, or authorize runtime work

## Context

[ADR 0106](0106-prove-raw-aware-numeric-trace-conformance-for-the-0-3-cohort.md)
proved raw-aware numeric traces and cross-object conformance for the fifteen
frozen construction subjects — but its three governed record instances are
all profile-control records. The nine product-domain schemas' acceptance and
refusal surfaces have never been exercised as governed instances through the
dual-implementation chain: their only schema-valid instances, the nine
structural-nonidentity fixtures frozen by [ADR
0103](0103-construct-side-by-side-odeya-jcs-0-3-candidate.md), are validated
only by the shared schema suite, and no per-token applicability trace or
source-separated refusal evidence exists for any product domain.

The current session handoff names this gap as the sole next mission: the
nine product-domain frames, with dual-implementation raw trace and refusal
evidence extending the PRQ-002F chain beyond the three profile-control
records.

## Decision

### Freeze one nine-domain frame-governance suite

Retain the suite `tests/profile-0-3-product-domain-frames/` with the
dedicated validator
`scripts/validate_profile_0_3_product_domain_frames.py` and exactly two
zero-third-party-dependency, source- and language-separated implementations
(CPython 3.14.2; Node.js 24.18.0). Neither consumes the other's source or
result, neither reads the private expectation file, and each hard-codes the
complete twelve-row schema-reference census and the nine-row fixture census —
repository path, raw SHA-256, decimal byte count, and governing schema
identity — independently of the shared answer-free vector file.

The nine accepted frames are byte-for-byte the nine frozen
structural-nonidentity fixtures. Each implementation must verify that the
frame bytes equal the retained repository fixture bytes before evaluation, so
the corpus cannot drift from the frozen artifacts it claims to exercise.
The fixtures remain what ADR 0103 froze them as: schema-valid structural
nonidentity evidence. Governing them creates no member, commitment, snapshot,
digest, identity, or admission.

### Trace every governed token in every domain

For each accepted frame, each implementation executes the complete PRQ-002F
discipline against the frame's governing product schema, using only the
exact twelve-schema cohort as the reference universe: strict raw-octet
parsing with duplicate-name, surrogate, noncharacter, and profile
raw-number refusal; raw-scan-to-document-walk reconciliation; closed
vocabulary evaluation that refuses unknown keywords; and a per-token
applicability trace binding every raw number lexeme to its unique RFC 6901
pointer, the resolved schema `$id` and raw digest, the assertion location,
and exactly one final rule under the fixed
`recursive_integer_valued_const_leaf` over `integer_type` precedence. A
token with no applicable rule, an out-of-cohort reference, or any
fallback resolution refuses the whole projection.

### Exercise every domain's refusal surface as data

The corpus additionally retains, for every one of the nine domains,
deterministically generated mutated variants of that domain's fixture that
must refuse through BOTH implementations with a declared singleton code:
a profile raw-number violation (an integral-fraction spelling), a lexical
negative zero, an out-of-safe-range integer, an undeclared member name that
`additionalProperties: false` must reject, and a removed required member.
This is per-domain refusal evidence exercised through the production paths
themselves — not only through validator-level mutation — so the two
implementations must agree byte-for-byte on the refusal census as well as on
every accepted trace.

Each implementation emits one deterministic projection binding, per frame,
the frame identity, disposition, and for accepted frames the complete trace
with the frame's raw digest and byte count, or the exact refusal code.
Agreement is exact-byte projection equality, bound by an external comparison
receipt written last; execution receipts remain self-attested
byte-consistency records.

### Validate with a third path and known-bads

The dedicated validator re-derives every frame — including byte-binding the
nine accepted frames to the retained repository fixtures — with its own
implementation before checking any byte census, verifies the retained
results, receipts, and comparison receipt, executes an embedded known-bad
corpus in which every mutation refuses with its declared singleton code, and
supports `--recompute-all` re-execution of both runners against the retained
result bytes.

## Required evidence before any broader claim

The suite retains known-bads that make at least these boundaries
load-bearing: frame or expectation census tampering, a frame whose bytes
drift from its retained repository fixture, canonical trace tampering,
disposition and refusal-code substitution, governing-schema rebinding,
projection divergence, result cross-copying and coherent symmetric
forgeries, receipt and comparison binding drift, integral-float census
smuggling, and any flip of a false identity, issuance, or authority
nonclaim.

Passing establishes only that the nine frozen fixtures are governed
instances of their nine product domains under the retained rules, and that
each domain's named refusal boundaries fire through both implementations.

## Non-decisions

This decision does not:

- compute or retain any product digest, member, ordered commitment,
  snapshot, membership proof, root, checkpoint, or activation for any
  fixture or domain — the fixtures remain structural nonidentity evidence;
- establish conformance for any instance beyond the nine retained fixtures
  and their retained mutated variants, generic `type: number` semantics, or
  complete offline resolution beyond the exact cohort;
- amend, issue, admit, migrate, or reinterpret any frozen byte;
- establish organizational independence, independent-host reproduction,
  causal historical execution, accountable review, or operator acceptance;
- close PRQ-002 or any other prerequisite, accept Gate A, or authorize
  implementation; or
- authorize runtime, deployment, credentials, spending, data access,
  scientific or product publication, or any external effect beyond the
  separately governed architecture-repository publication of the retaining
  commit itself.

## Consequences

Every one of the nine product domains stops being a schema that has merely
existed and becomes a schema that has demonstrably governed: accepted its
one frozen instance with a complete dual-implementation token trace, and
refused its named attack classes through both production paths. The
remaining dependencies are dependency-closed offline resolution and
cross-object product replay, then the accountable-review and
operator-acceptance prerequisites no session can self-supply.
