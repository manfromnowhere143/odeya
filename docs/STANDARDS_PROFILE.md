# Odeya Standards Profile

Status: proposed baseline, checked 2026-07-15. This document distinguishes external semantic standards from replaceable product choices. Exact frozen copies, digests, validators, and conformance vectors remain blocking work under the pre-implementation gate.

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
| Signing bundle | [Sigstore Bundle 0.3.2](https://docs.sigstore.dev/about/bundle/) | Portable signature/verification material | G3 |
| SBOM | [SPDX 3.0.1](https://spdx.github.io/spdx-spec/v3.0.1/) or [CycloneDX 1.7](https://cyclonedx.org/specification/overview/) | Select exactly one canonical source; optionally export the other | G3 |
| Container artifacts | OCI Image/Distribution 1.1.1 and Runtime 1.3.0 | Portable worker image and runtime contracts | G3/G9 |
| Secure development | [NIST SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) | Development-control baseline | G3 |
| Zero trust | [NIST SP 800-207](https://csrc.nist.gov/pubs/sp/800/207/final) and 800-207A | Architecture guidance, not certification | G3 |
| Operational telemetry | OpenTelemetry Specification 1.59, Semantic Conventions 1.43, exact GenAI repository commit | Operations only; stable Odeya attributes wrap unstable GenAI fields | G7 |
| Trace propagation | [W3C Trace Context](https://www.w3.org/TR/trace-context/) | Correlation only, never evidence identity or authority | G7 |
| Authentication | [OIDC Core Errata 2](https://openid.net/specs/openid-connect-core-1_0-errata2.html), [OAuth Security BCP RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html) | Human/service authentication boundary | G3 |
| Authorization exchange | [AuthZEN Authorization API 1.0](https://openid.net/specs/authorization-api-1_0.html) | Candidate policy decision interface | G3/G6 |
| Workload identity | [SPIFFE specifications](https://spiffe.io/docs/latest/spiffe-specs/) | Candidate service/worker identity profile | G3 |
| Accessibility | [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/), WAI-ARIA 1.2, ACT Rules Format 1.1 | Complete private and public workflows | G8 |
| Publication metadata | DataCite 4.7, Crossref 5.5, CRediT, JATS 1.4, CodeMeta 3.1, Citation File Format 1.2 | Select profile by release type | G8 |

Version numbers above are a review baseline, not an instruction to follow “latest.” Each must be rechecked and frozen before implementation.

## Odeya canonical JSON profile

RFC 8785 is necessary but not sufficient. Odeya's profile must:

- reject duplicate object keys before parsing;
- allow only valid UTF-8 and declare that Unicode is not normalized silently;
- sort and encode exactly as JCS requires;
- reject `NaN`, positive/negative infinity, and negative zero ambiguity;
- represent exact scientific decimals as objects containing decimal string, unit, precision/scale, and semantic type;
- represent ratios, intervals, distributions, timestamps, and missingness with typed objects rather than overloaded numbers;
- require UTC timestamps ending in `Z` with an accepted fixed fractional precision;
- distinguish absent, `null`, `unknown`, `unmeasured`, `withheld`, and `not_applicable`;
- hash an envelope that names the profile and schema version;
- include cross-language conformance vectors for numbers, Unicode, key ordering, time, missingness, and nested references.

Changing the profile creates a new digest namespace. Existing bytes are never reinterpreted under a newer profile.

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
