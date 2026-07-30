# Odeya Standards Profile

Status: proposed baseline. The canonical-JSON construction pin was added
2026-07-29; the remaining baseline was checked 2026-07-16. This document
distinguishes external semantic standards from replaceable product choices.
Exact frozen copies, digests, validators, and conformance vectors remain
blocking work under the pre-implementation gate.

## Conformance record

Every adopted standard receives a versioned record containing:

- standard identifier, exact version, official URL, retrieval time, and frozen-copy digest;
- `MUST`, `SHOULD`, and `MAY` scope inside Odeya;
- selected validator, version, and configuration;
- positive, negative, and cross-runtime conformance vectors;
- allowed deviations and rationale;
- migration, deprecation, and backward-reading policy;
- implementation adapter and replacement boundary;
- owner and next review date.

“Standards compliant” is forbidden without the named profile and retained conformance result.

## Normative baseline

| Concern | Baseline | Odeya use | Freeze gate |
|---|---|---|---|
| Data contracts | [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) | Canonical contract vocabulary and validation | G2 |
| Canonical JSON | [RFC 8785 JCS](https://www.rfc-editor.org/rfc/rfc8785.html) + Odeya profile | Exact evidence and event bytes | G2/G4 |
| HTTP descriptions | [OpenAPI 3.2.0](https://spec.openapis.org/oas/v3.2.0.html) | External synchronous API description | G6 |
| Event descriptions | [AsyncAPI 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) | Subscription and event-channel description | G6 |
| Transport envelope | [CloudEvents 1.0.2](https://github.com/cloudevents/spec/tree/ce@v1.0.2) | Delivery envelope only, never canonical scientific identity | G6 |
| Sortable identifiers | [RFC 9562 UUIDv7](https://www.rfc-editor.org/info/rfc9562/) | Optional opaque event/request IDs | G2 |
| Provenance | [PROV-O](https://www.w3.org/TR/prov-o/), [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/) | Interoperable entity/activity/agent export | G4 |
| Research package | [RO-Crate 1.3](https://w3id.org/ro/crate/1.3) | Evidence and publication package | G4/G8 |
| Workflow research package | [Workflow Run RO-Crate 0.5](https://w3id.org/ro/wfrun/workflow/0.5) | Optional execution-profile export after compatibility test | G4 |
| Supply-chain maturity | [SLSA 1.2](https://slsa.dev/spec/v1.2/) | Measurable source/build provenance target | G3/G9 |
| Attestation predicate | [in-toto Attestation 1.2.0](https://github.com/in-toto/attestation/tree/v1.2.0/spec) | Signed build and release statements | G3 |
| Attestation envelope | [DSSE 1.0.2](https://github.com/secure-systems-lab/dsse/blob/v1.0.2/protocol.md) | Authenticate exact payload bytes plus payload type; signatures remain external to the subject | G3/G4 |
| Signing bundle | [Sigstore Bundle 0.3.2](https://docs.sigstore.dev/about/bundle/) | Portable signature/verification material | G3 |
| Root succession comparison | [TUF 1.0.35](https://github.com/theupdateframework/specification/blob/v1.0.35/tuf-spec.md) | Threshold root rotation, rollback/freeze refusal, and consistent-snapshot comparison; not Odeya's registry format | G3/G7 |
| Transparency architecture | [RFC 9943 SCITT Architecture](https://www.rfc-editor.org/rfc/rfc9943.html) | Candidate architecture for independently receipted, replayable checkpoint statements; not a scientific-validity layer | G3/G4/G7 |
| Verifiable receipts | [RFC 9942 COSE Receipts](https://www.rfc-editor.org/rfc/rfc9942.html) with the selected VDS profile | Candidate portable inclusion/consistency receipt format | G3/G4/G7 |
| Append-only VDS | [RFC 9162 CT v2 Merkle construction](https://www.rfc-editor.org/rfc/rfc9162.html), only through an accepted Odeya/SCITT profile | Candidate inclusion and consistency proof construction; CT certificate semantics do not transfer | G4/G7 |
| Checkpoint witnessing | [C2SP checkpoint](https://c2sp.org/tlog-checkpoint), [cosignature](https://c2sp.org/tlog-cosignature), and [witness](https://c2sp.org/tlog-witness) formats | Maintained comparison profiles for signed checkpoints and independent witness cosignatures | G3/G7 |
| SBOM | [SPDX 3.0.1](https://spdx.github.io/spdx-spec/v3.0.1/) or [CycloneDX 1.7](https://cyclonedx.org/specification/overview/) | Select exactly one canonical source; optionally export the other | G3 |
| Container artifacts | OCI Image/Distribution 1.1.1 and Runtime 1.3.0 | Portable worker image and runtime contracts | G3/G9 |
| Secure development | [NIST SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | Development-control baseline | G3 |
| Zero trust | [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final) and 800-207A | Architecture guidance, not certification | G3 |
| Key management | [NIST SP 800-57 Part 1 Rev. 5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final) | Key-purpose, lifecycle, protection, recovery, and compromise profile guidance | G3/G7 |
| Media sanitization | [NIST SP 800-88 Rev. 2](https://csrc.nist.gov/pubs/sp/800/88/r2/final) | Storage-specific sanitization program baseline; not proof of provider or distributed deletion by itself | G3/G7 |
| Operational telemetry | OpenTelemetry Specification 1.59, Semantic Conventions 1.43, exact GenAI repository commit | Operations only; stable Odeya attributes wrap unstable GenAI fields | G7 |
| Trace propagation | [W3C Trace Context](https://www.w3.org/TR/trace-context/) | Correlation only, never evidence identity or authority | G7 |
| Authentication | [OIDC Core Errata 2](https://openid.net/specs/openid-connect-core-1_0-errata2.html), [OAuth Security BCP RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) | Human/service authentication boundary | G3 |
| Human authenticator assurance | [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/) | Primary profile for authenticator assurance, claimant-controlled authentication intent, phishing resistance, and session binding; not application decision intent | G3 |
| Protected human ceremony | [W3C WebAuthn Level 3](https://www.w3.org/TR/webauthn-3/) | Primary ceremony component for RP/origin-bound challenges, user presence, user verification, and authenticator evidence; not proof of review, understanding, or substantive decision intent | G3 |
| Authorization exchange | [AuthZEN Authorization API 1.0](https://openid.net/specs/authorization-api-1_0.html) | Candidate policy decision interface | G3/G6 |
| Workload identity | [SPIFFE specifications](https://spiffe.io/docs/latest/spiffe-specs/) | Candidate service/worker identity profile | G3 |
| Accessibility | [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/), WAI-ARIA 1.2, ACT Rules Format 1.1 | Complete private and public workflows | G8 |
| Publication metadata | DataCite 4.7, Crossref 5.5, CRediT, JATS 1.4, CodeMeta 3.1, Citation File Format 1.2 | Select profile by release type | G8 |

Version numbers above are a review baseline, not an instruction to follow “latest.” Each must be rechecked and frozen before implementation.

## 2026 constitutional-integrity alignment

The standards review fixes the following Odeya-owned architecture laws. The
external specifications are comparison evidence and interoperability profiles;
none is delegated authority over scientific meaning, admission, or recovery.

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) defines
  structural vocabularies, identifiers, and reference behavior. It cannot prove
  cross-object digest equality, registry membership, lifecycle reachability,
  witness independence, current authority, or scientific validity. Those remain
  separate fail-closed semantic checks.
- [RFC 8785 JCS](https://www.rfc-editor.org/info/rfc8785/) plus its
  [verified errata](https://www.rfc-editor.org/errata/rfc8785) is the bounded
  JSON canonicalization primitive. Odeya refuses negative-zero ambiguity and
  never treats JCS as a scientific-number, schema-resolution, or signature
  policy.
- [DSSE 1.0.2](https://github.com/secure-systems-lab/dsse/blob/v1.0.2/protocol.md) authenticates both payload
  bytes and payload type to resist type-confusion. Odeya attestations therefore
  sign an already-computed immutable core or seal identity; signatures and
  evidence that depend on that identity cannot be members of the same digest
  preimage.
- A [Sigstore Bundle 0.3.2](https://docs.sigstore.dev/about/bundle/) may retain
  a signature, certificate or key hint, transparency-log material, inclusion
  proof, and timestamp evidence for offline verification. The verifier must
  still obtain or recompute the subject artifact digest. Bundle presence alone
  never proves that the subject is the expected Odeya core, that a witness is
  independent, or that a scientific claim is sound.
- [SLSA 1.2 artifact verification](https://slsa.dev/spec/v1.2/verifying-artifacts)
  requires verification of the envelope, artifact subject, builder identity,
  build type, and external parameters against explicit expectations. Odeya
  therefore records provenance and a separate verification decision; the
  existence of provenance never promotes an artifact, reducer, verifier, or
  release.
- [The Update Framework 1.0.35](https://github.com/theupdateframework/specification/blob/v1.0.35/tuf-spec.md)
  provides the comparison model for root succession, threshold roles,
  rollback/freeze refusal, consistent snapshots, and old-plus-new root
  authorization during key rotation. Odeya applies those properties to
  retained root/C0/bootstrap history without copying TUF's package-distribution
  object model into the scientific ledger.
- [Tessera](https://pkg.go.dev/github.com/transparency-dev/tessera) distinguishes
  sequencing, integration, and publication by a checkpoint, and leaves
  ecosystem admission to the log personality. Odeya likewise keeps command and
  scientific admission in its deterministic kernel; a transparency substrate
  may commit accepted checkpoint statements but cannot decide what is eligible
  to enter them.
- [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162.html) supplies reviewed
  Merkle inclusion and consistency constructions. These prove bounded log
  properties under the selected profile, not statement correctness or a unique
  global view. Odeya additionally requires monitored checkpoint continuity and
  [C2SP witness cosignatures](https://c2sp.org/tlog-cosignature) from distinct,
  policy-qualified failure domains before P0 may call a checkpoint witnessed.
- [in-toto Attestation Framework](https://in-toto.io/docs/specs/) statements
  and envelopes are portable evidence carriers. Their predicates remain typed
  claims by identified issuers; they do not collapse generation, review,
  replication, adjudication, and publication into one signature.
- [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
  uses explicit claimant action to establish authentication intent, while
  [WebAuthn Level 3](https://www.w3.org/TR/webauthn-3/) supplies RP/origin-bound
  challenge, user-presence, user-verification, and authenticator evidence.
  Those are authentication-ceremony components, not proof that a person
  reviewed, understood, or substantively intended an Odeya decision.
  PRQ-013 therefore requires a separate protected decision ceremony over the
  exact displayed and candidate bytes, with custody, delegation, conflict,
  quorum, replay, expiry, and sanitized-evidence semantics owned by Odeya.

Three Core/Evidence/Seal schemas are unissued foundation candidates; no
consumer or `AssuredDecision` is claimed to conform to this
decision-assurance profile. PRQ-013 remains a Gate A blocker under
[ADR 0092](decisions/0092-bind-human-decisions-through-an-external-assurance-wrapper.md),
which extends [ADR 0089](decisions/0089-a-valid-human-signature-is-not-a-human-decision.md), and the
[cross-program process-evidence packet](CROSS_PROGRAM_PROCESS_EVIDENCE_ABSORPTION_2026-07-19.md).

These comparisons support one nonrecursive construction law:

```text
immutable core digest
  -> evidence and decisions that name the core digest
  -> immutable seal binding the core and exact evidence set
  -> external attestations, transparency inclusion, and witness observations
```

An attestation may sign the core or seal according to its declared purpose. It
never enters the preimage of the identity it signs. A later signature,
timestamp, witness, or inclusion proof can add verification material without
changing the scientific subject's identity. Any claim of currentness is a
separate policy decision over retained history, controlled time, and the exact
trusted root—not a field smuggled into a timeless content digest.

## Odeya canonical JSON profile

RFC 8785 is necessary but not sufficient. Odeya's profile must:

- reject duplicate decoded object names during the raw parse, before lossy
  object-map materialization;
- allow only valid UTF-8 and declare that Unicode is not normalized silently;
- retain raw number-token provenance and the unique instance position before
  host numeric conversion or schema type evaluation;
- sort and encode exactly as JCS requires;
- reject `NaN`, positive/negative infinity, and negative zero ambiguity;
- represent exact scientific decimals as objects containing decimal string, unit, precision/scale, and semantic type;
- represent ratios, intervals, distributions, timestamps, and missingness with typed objects rather than overloaded numbers;
- require UTC timestamps ending in `Z` with an accepted fixed fractional precision;
- distinguish absent, `null`, `unknown`, `unmeasured`, `withheld`, and `not_applicable`;
- hash an envelope that names the profile and schema version;
- include cross-language conformance vectors for numbers, Unicode, key ordering, time, missingness, and nested references.

Changing the profile creates a new digest namespace. Existing bytes are never reinterpreted under a newer profile.

Draft 2020-12 treats `integer` as a mathematical-value classification, so
integral fraction and exponent tokens can satisfy `type: integer`. RFC 8785
then serializes a finite binary64 value and cannot recover whether the input
token was `1`, `1.0`, or `1e0`. [ADR 0101](decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md)
therefore proposes an Odeya-owned lexical overlay before mapping: an
integer-type or integer-valued-const position admits only an integer token in
the exact admissible range, and every lexical negative zero is refused. This
is a declared Odeya restriction, not a claim that JSON Schema or JCS provides
it.

The retained PRQ-002C evidence is a bounded observation over 61 opaque,
answer-free synthetic integer-position frames: two source- and
language-separated implementations agree on 9 admissions and 52 refusals,
and 44 suite-gate known-bads fire. It does not establish generic schema-path
evaluation, number-position semantics, full RFC 8785 correctness, nine-domain
framing, organizational independence, or full successor-profile conformance.
The frozen `odeya-jcs-0.2` candidate remains unissued and blocked from
conformance and issuance. ADR 0101 itself did not create
`odeya-jcs-0.3`, and its bounded observations cannot be inherited as
successor-profile conformance.

[ADR 0102](decisions/0102-prove-non-product-prehash-schema-registry-replay.md)
retains the next bounded PRQ-002D prerequisite before any structured or product
identity: one synthetic two-member prehash schema-registry replay over 68
opaque virtual-file frames. Source- and language-separated Python and Node
implementations agree with one fixed private oracle and each other on one
accepted frame and 67 refused frames; 77 named parent-gate known-bads each
return their declared singleton guard. This does not amend `odeya-jcs-0.2` or
establish full RFC 8785 correctness, generic schema evaluation, complete
offline resolution, dependency-closed product registries, cross-object product
replay, organizational independence, profile conformance, product identity,
admission, issuance, PRQ-002 closure, Gate A acceptance, or runtime authority.
ADR 0102 itself did not create or test `odeya-jcs-0.3`; its bounded prehash
result cannot be promoted into product identity or successor-profile
conformance.

### `odeya-jcs-0.3` bounded construction pin

[ADR 0103](decisions/0103-construct-side-by-side-odeya-jcs-0-3-candidate.md)
freezes an architecture-only construction graph for the unissued
`urn:odeya:canonicalization:odeya-jcs-0.3`, version `0.3.0`. It is
side-by-side with the exact frozen `odeya-jcs-0.2` bytes. It is not an alias,
patch, redirect, implicit upcast, or authority to reinterpret a predecessor
digest.

The authoritative input boundary is a raw-octet adapter separate from the
canonicalizer core. It binds raw SHA-256 and byte count, decodes strict [RFC
3629 UTF-8](https://www.rfc-editor.org/rfc/rfc3629.html), rejects a byte order
mark, accepts exactly one [RFC
8259](https://www.rfc-editor.org/rfc/rfc8259.html) JSON value, detects
duplicate decoded names before lossy map construction, enforces [I-JSON RFC
7493 section
2.1](https://www.rfc-editor.org/rfc/rfc7493.html#section-2.1) by
deterministically refusing decoded surrogate or noncharacter code points, and
retains each raw number lexeme with its unique [RFC
6901](https://www.rfc-editor.org/rfc/rfc6901.html) instance pointer. A native
host parser cannot supply authoritative duplicate-name, token-class, or
numeric-conversion evidence.

The canonicalization algorithm is [RFC
8785](https://www.rfc-editor.org/rfc/rfc8785.html) with exactly verified [EID
6292](https://www.rfc-editor.org/errata/eid6292) and [EID
7920](https://www.rfc-editor.org/errata/eid7920). Its ECMAScript dependency is
pinned to [ECMA-262, 10th edition,
2019](https://tc39.es/ecma262/2019/): string serialization uses
section 24.5.2.2 through EID 6292, and number serialization uses section
7.1.12.1 including Note 2. Odeya makes every ADR 0101 lexical negative zero a
deterministic refusal.

RFC 8259 errata are selected individually, never inherited as a blanket set.
The candidate does not apply [RFC 8259 EID
5318](https://www.rfc-editor.org/errata/eid5318) to canonical output because
the more specific RFC 8785 string rule controls: U+002F `/` may arrive escaped
or unescaped and is always emitted unescaped. A retained slash vector must
make that precedence load-bearing.

Unicode scalar sequences are preserved exactly. No NFC, NFD, NFKC, NFKD,
case, or locale normalization is allowed; canonically equivalent but
code-point-distinct strings remain distinct. Object names sort recursively by
unsigned UTF-16 code units, arrays retain order, and the final encoding is
UTF-8 without inter-token whitespace.

[JSON Schema Draft
2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html) has an
arbitrary-precision base-10 mathematical number model; JCS emits IEEE-754
binary64. The exact `0.3` cohort therefore uses two non-cyclic layers. A
static schema-position inventory inside the final core is derived only from
the twelve final schema byte strings and binds schema IDs, raw digests,
resolved schema locations, and integer-type or recursively identified
integer-valued-`const` rules. It carries no concrete subject digest. A
downstream trace produced after each concrete subject is final binds the
subject raw digest/count, every numeric lexeme/class and instance pointer, and
the exact static schema rule that evaluated it.

Numeric literals inside a schema document are schema-definition data, not
automatically future instance positions; metaschema evaluation requires its
own trace. The nine product schemas may govern later product subjects, while
the three control schemas govern the core, evidence, and migration records.
A trace about the evidence record remains downstream and cannot be bound by
that same evidence record. A later conformance inventory/comparison receipt
must bind those traces; the retained construction-observation receipt does
not.

Any `type: number`, number-admitting union, unresolved branch, missing or
stale inventory/trace, or otherwise unclassified numeric position is refused.
Admitted integer tokens follow ADR 0101's lexical and safe-integer limits;
subsequent decimal-to-binary64 conversion uses [IEEE
754-2019](https://ieeexplore.ieee.org/document/8766229)
`roundTiesToEven`. This closes only the measured zero-`type:number` cohort,
not generic number semantics.

The exact product domains are:

```text
odeya-schema-resource-record-v2
odeya-aggregate-state-subject-record-v2
odeya-reducer-contract-record-v2
odeya-event-contract-record-v2
odeya-ordered-member-map-commitment-v2
odeya-schema-registry-v3
odeya-aggregate-state-subject-registry-v3
odeya-reducer-registry-v3
odeya-event-contract-registry-v3
```

The twelve exact schema paths and IDs are frozen in ADR 0103. The three
final-only architecture records are
`architecture/canonicalization-profile-core-0.3-candidate.json`,
`architecture/canonicalization-profile-0.3-candidate-evidence.json`, and
`architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json`.
Required raw bindings cannot be placeholders or authoring-time `null`s. The
acyclic order separates two retained transactions from later conformance. The
product-authoring transaction stages exactly twelve schemas, nine
structural-nonidentity fixtures, and three records; the migration record is
installed last. Only after the fifteen schema-and-record subjects are final
may the observation transaction stage two source manifests, two exact stdout
results, two execution receipts, and a comparison receipt replaced last.
Downstream per-subject traces follow in a later conformance unit; no artifact
binds itself or a downstream artifact. Receipt-last ordering is insufficient
alone: each authoring transaction must validate its complete graph in an
isolated same-filesystem staging directory, fsync the candidate files and
directory, install only validated final bytes, and make every missing,
mixed-generation, stale, or mismatched subject refuse on readback.

This construction pin establishes no RFC or Odeya-profile conformance,
product digest, product member, ordered commitment, registry snapshot,
identity, admission, profile or schema issuance, complete offline resolution,
independent reproduction, accountable review, operator acceptance, PRQ-002
closure, Gate A acceptance, runtime, deployment, publication, or external
authority.

## JSON Schema validation profile

JSON Schema `format` is annotation-only unless assertion behavior is enabled. Odeya must pin:

- validator and exact version in each supported language;
- format-assertion vocabulary and date/time checker;
- URI and reference resolution, allowed schemes, offline catalog, and recursion limits;
- unknown-key, integer/number, Unicode, and duplicate-key behavior;
- maximum depth, size, collection length, and regex execution limits;
- error-code normalization;
- metaschema validation and differential tests across validators;
- semantic checks that JSON Schema cannot express, such as reference existence, unique authority roles, independence, risk/publication consistency, and state/outcome compatibility.

Schema validity is necessary and never sufficient for mission admission.

## Event and workflow semantics

- CloudEvents may wrap delivery metadata but the immutable Odeya event is the canonical payload referenced by digest.
- Delivery is at least once. Consumers are idempotent. “Exactly once” is not claimed across external effects.
- A durable-workflow product schedules and recovers activities; its private history is not the scientific ledger.
- Workflow code must be deterministic under replay. Nondeterministic work, network, models, clocks, and randomness live in activities whose results are retained.
- Command idempotency, provider idempotency, attempt identity, reconciliation, and duplicate-charge handling are distinct.
- Event schemas, transition semantics, and compatibility remain Odeya-owned even if transports change.

## Cross-store materialization and promotion protocol

PostgreSQL and object storage do not share a natural atomic transaction. The required recoverable flow is:

```text
stage upload
  -> stream-verify bytes and digest
  -> conditional immutable byte materialization
  -> database transaction:
       artifact-promotion event + metadata + authority/resource effects + state + outbox
  -> asynchronous projections/subscriptions
  -> orphan and missing-object reconciliation
```

Byte materialization uses unique digest keys and conditional creation. It proves storage identity, not scientific promotion. If the database transaction fails, the object is an unregistered orphan reclaimed only after a retention and reconciliation rule. If an object is missing after the artifact-promotion commit, the artifact is corrupt/unavailable and dependent claims fail closed.

## Ledger anti-equivocation

A mission hash chain detects in-chain mutation but not every truncated or forked history. The standards profile must define:

- checkpoint interval and included mission heads;
- Merkle or equivalent checkpoint construction;
- signing identity and key rotation;
- external witness or anchor independent of the primary database;
- split-view detection and restore procedure;
- evidence required before a checkpoint is called witnessed.

This protects integrity, not scientific meaning.

The leading standards-aligned candidate is an Odeya-private SCITT profile: signed checkpoint statements are registered with one or more independently administered transparency services and return portable COSE receipts. RFC 9943 requires an append-only, non-equivocating, replayable verifiable data structure and makes registration policy/trust-anchor history auditable. RFC 9942 defines receipt structures, including RFC 9162 SHA-256 inclusion and consistency proofs. Odeya must still pin the statement content type, privacy boundary, issuer/trust model, registration policy, VDS identifier, proof limits, witness independence, receipt retention, and failure consequences. A valid receipt proves registration under that service/profile; it does not prove a checkpoint payload is complete, scientifically correct, or the only history unless the full witness/consistency assumptions pass.

The event ledger and the transparency service remain distinct. Private event payloads do not enter a public log. A checkpoint statement contains bounded commitments and non-sensitive policy/trust metadata; authorized auditors resolve private leaves through controlled proofs. Multiple receipts improve failure-domain evidence only when the services are actually independent.

## Data lifecycle and key profile

The requirements in `DATA_GOVERNANCE.md` and `LEDGER_INTEGRITY_AND_RECOVERY.md` are Odeya-owned. NIST SP 800-57 Part 1 Rev. 5 informs key types, protection, lifecycle, recovery, split knowledge, trust anchors, and compromise handling. NIST SP 800-88 Rev. 2 informs a media-sanitization program selected by information sensitivity and storage technology. Neither publication certifies an Odeya deployment.

The accepted profile must map every storage plane—including provider copies, caches, replicas, immutable object versions, logs, backups, exports, and encryption keys—to an exact deletion or bounded-expiry mechanism and verification evidence. Cryptographic erasure is accepted only when the data-encryption-key scope, copies, wrapping hierarchy, rotation, backups, residual plaintext, and destruction verification are established. Sanitized media does not erase prior recipient exposure, scientific contamination, or uncontrolled publications.

## Portable scientific tables

Arrow, Parquet, and DuckDB remain product choices beneath a strict writer profile:

- field IDs and stable semantic names;
- exact decimal precision/scale and unit metadata;
- UTC timestamp unit and timezone behavior;
- null, NaN, infinity, signed zero, and missingness semantics;
- dictionary, nested, categorical, binary, and large-object limits;
- row ordering and canonical sort requirements where order matters;
- schema evolution and unknown-field behavior;
- compression codec and statistics/page-index policy;
- conformance reads in the pinned DuckDB, PyArrow, and Arrow Rust versions;
- file digest over exact bytes plus logical-content test vectors where required.

“Parquet” alone is not a reproducibility guarantee.

## Provenance and publication profile

PROV and RO-Crate carry interoperable structure. Odeya's mapping adds:

- protocol freeze and amendment;
- hypothesis and falsifier;
- source role and data exposure;
- metric and uncertainty type;
- claim boundary and forbidden language;
- authority grants and policy decisions;
- independent verifier and exposure class;
- invalid, blocked, null, correction, retraction, and supersession;
- resource estimates and observations;
- release authority and sanitized projection.

Publication profiles must map author/contributor identities, CRediT roles, organizations, software, datasets, funding, conflicts, licenses, versions, citations, corrections, and evidence-package identifiers. Venue acceptance is metadata, not a truth state.

Odeya's exact PROV/RO-Crate mapping, namespace requirements, claim traversal, redaction, archive, and round-trip limits are specified in [Provenance and Research-Package Export Profile](PROVENANCE_EXPORT_PROFILE.md).

## Supply-chain target

Initial target:

- SLSA 1.2 Source L2 and Build L2;
- hermetic or substantially isolated build with pinned dependencies;
- in-toto predicates and a pinned Sigstore bundle verification policy;
- one canonical SBOM representation;
- reviewed provenance linkage between source, build, worker image, verifier, and release artifact;
- clean-clone and restore evidence.

Plan L3 for the kernel, verifier, and publication path after the first slice. SLSA attainment does not validate research results.

## Accessibility conformance

Target WCAG 2.2 AA for complete workflows, not isolated components. Required evidence includes automated checks plus manual keyboard, screen-reader, focus order, error recovery, forced-colors, reduced-motion, 200% text resize, 320-CSS-pixel/400%-equivalent reflow, small-screen, and print testing.

Scientific graphs require text alternatives, table access to exact values, pattern/shape redundancy, keyboard inspection, and uncertainty/missingness in accessible names.

## Replaceable product choices

These are not constitutional standards and stay behind ports until G9 chooses and pins them:

- PostgreSQL and S3-compatible storage;
- Temporal or another durable workflow substrate;
- Python, TypeScript, Next.js, and specific web/API libraries;
- DuckDB, PyArrow, Arrow Rust, and Parquet implementations;
- OPA, Cedar, or another policy engine;
- Vault, cloud KMS, or another key/secret system;
- gVisor, Kata, Firecracker, or other isolation products;
- Sigstore services and SPIRE deployment;
- model, inference, search, browser, and compute providers.

Replacing them may change performance and operations. It must not change lifecycle, claim ontology, evidence admissibility, risk, authority, correction, or publication semantics.
