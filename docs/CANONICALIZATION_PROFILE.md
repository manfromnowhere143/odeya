# Canonical Identity and Serialization Profile

Status: proposed Odeya profile `odeya-jcs-0.1`, 2026-07-15. A pinned
architecture-only suite now gives cross-runtime evidence for the bounded rules
identified below. The profile is not frozen: the production schema migration,
package/reference profiles, fuzzing, limit measurements, independent-host
reproduction, and operator acceptance remain blocking.

## Purpose

Odeya needs to answer three different questions without ambiguity:

1. Are these the exact same raw bytes?
2. Are these the exact same canonical structured object under one schema/profile?
3. Do these different objects express scientifically equivalent meaning?

Only the first two are digest questions. Scientific equivalence requires a registered semantic rule and never follows from hashing.

## Identity types

| Identity | Input | Digest meaning |
|---|---|---|
| `ByteDigest` | Exact raw byte stream | Byte-for-byte identity only |
| `CanonicalObjectDigest` | Canonical envelope encoded under `odeya-jcs-*` | Same profile, schema identity, and canonical object bytes |
| `ArtifactIdentity` | Logical record referring to bytes plus provenance/rights/custody | Distinct even when raw bytes deduplicate |
| `EnvironmentIdentity` | Complete admitted environment manifest | Identity of declared environment inputs, not proof runtime behaved correctly |
| `SemanticEquivalenceResult` | Two or more typed objects and a rule version | Bounded equivalence under named assumptions; not a digest |

Original and normalized/transcoded/redacted/derived bytes always receive different `ByteDigest` values and explicit transformation provenance.

## Canonical envelope

Canonical structured identities hash this logical envelope:

```json
{
  "profile_id": "urn:odeya:canonicalization:odeya-jcs-0.1",
  "schema_id": "urn:odeya:schema:<object>:<version>",
  "subject": { "...": "closed schema-valid object" }
}
```

The envelope itself is closed. `schema_id` resolves through the offline Odeya schema registry to exact retained schema bytes and digest. The subject cannot choose a mutable URL, “latest,” or an unregistered schema.

```text
canonical_bytes = UTF8(JCS(canonical_envelope))
canonical_digest = "sha256:" + lowercase_hex(SHA-256(canonical_bytes))
```

Including profile and schema identity in the hashed envelope provides domain separation without inventing a custom cryptographic construction. A future hash algorithm or profile creates a new typed digest namespace/field; old identities are never reinterpreted.

Self-digests are forbidden inside the hashed subject. An external registry record binds the resulting digest to storage, signatures, timestamps, and events.

## Scoped digest contracts

Command, receipt, event, and checkpoint records carry closed digest-contract objects rather than prose such as “hash everything except X.” A conforming implementation:

1. validates the complete record and resolves the exact retained schema/profile bytes;
2. rejects a missing pointer, overlapping included/excluded pointer, duplicate pointer, unknown property outside the declared partition, mutable schema/profile alias, or unregistered binding;
3. constructs a fresh projection by copying each included JSON-Pointer subtree at its original full path; a parent is created only as a path container and contributes no undeclared siblings;
4. verifies that any digest/signature field within the record occurs only in the exact excluded set and never within an included subtree;
5. constructs and JCS-encodes this closed logical input, where `digest_contract` is the exact contract object from the record and `resolved_subject_schema` is the immutable schema identity/digest resolved by the source named below:

```json
{
  "digest_contract": { "algorithm": "sha-256", "domain_separator": "...", "...": "exact contract" },
  "resolved_subject_schema": { "schema_id": "urn:odeya:schema:...", "schema_digest": "sha256:..." },
  "projection": { "...": "exact pointer-selected tree" }
}
```

6. computes lowercase `sha256:` identity over those JCS bytes, compares it in constant time, then verifies external signatures over the declared digest and purpose context.

This construction hashes the algorithm, domain, profile identity/digest, schema identity/digest, pointer contract, and selected data as one canonical object; it does not depend on the contract also appearing within its own projection. The current domains are distinct:

| Subject | Domain | Schema-binding source | Self/external fields excluded |
|---|---|---|---|
| command request | `odeya-command-request-v1` | exact `CommandEnvelope` schema plus bound payload contract | request digest, signature |
| command result | `odeya-command-result-v1` | exact `CommandReceipt` result contract | none; digest/signature fields are outside `/result` |
| command receipt | `odeya-command-receipt-v1` | exact `CommandReceipt` schema | receipt digest, signature |
| policy decision | `odeya-policy-decision-v1` | explicit exact `PolicyDecision` schema ID/digest | decision digest, signature |
| admission evidence bundle | `odeya-admission-evidence-bundle-v1` | explicit exact bundle schema ID/digest | bundle digest, signature |
| event payload | `odeya-event-payload-v1` | exact event `payload_schema_id` and digest | none; digest/attestation fields are outside `/payload` |
| research event | `odeya-research-event-v1` | exact `ResearchEvent` schema | event digest, signature |
| ledger checkpoint | `odeya-ledger-checkpoint-v1` | explicit exact checkpoint schema ID/digest | checkpoint digest, all signatures |

Signatures are external attestations: re-signing cannot alter subject identity. JSON Schema can require these fields and exact pointer arrays; it cannot construct the projection, recompute a digest, establish registry acceptance, perform constant-time comparison, or verify a signature. Those are independent semantic/conformance obligations.

## Parser safety before JCS

Before canonicalization, the parser must:

- accept only valid UTF-8 without byte-order mark;
- reject duplicate object names before any last-key-wins behavior;
- reject invalid Unicode, including unpaired surrogate code points;
- reject trailing data, comments, nonstandard escapes, and implementation extensions;
- reject `NaN`, infinities, negative-zero ambiguity, and numbers outside the admitted semantic profile;
- apply maximum total bytes, depth, object members, array items, string length, and numeric-token length;
- avoid regex/reference behavior with unbounded resource cost;
- retain parser/version/configuration identity in the validation result.

A parser error has no canonical object. It cannot be “repaired” silently.

The conformance candidate currently exercises these fail-closed structural
ceilings: 1,048,576 input bytes, depth 64, 4,096 members per object, 10,000
items per array, 262,144 Unicode code points per string, 128 bytes per numeric
token or exact scientific-decimal lexical value, 20,000 total parsed value nodes, and integers no larger in magnitude
than 9,007,199,254,740,991. These are testable candidate admission limits, not
performance claims. Gate A still requires security/resource measurement before
they can become production limits.

## RFC 8785 behavior

Odeya uses RFC 8785 JCS for JSON string escaping, primitive serialization, and object-member ordering. In particular:

- object properties are sorted by their raw UTF-16 code units as JCS specifies;
- arrays preserve order; JCS does not sort them;
- strings are not Unicode-normalized;
- JSON number serialization follows the JCS/ECMAScript rule and is therefore unsuitable for many exact scientific values.

Every supported runtime must match official JCS vectors plus Odeya’s adversarial vectors. A library’s “canonical JSON” label is insufficient without exact-vector agreement.

## Scientific numbers

Binary JSON numbers are allowed only for schema fields whose meaning is explicitly bounded integer or non-scientific control metadata and whose cross-runtime range is frozen. Scientific decimal values use typed objects:

```json
{
  "value": "-1.2500e-3",
  "semantic_type": "measured_quantity",
  "unit": { "system": "SI", "code": "m.s-2" },
  "precision": { "kind": "decimal_places", "value": 7 }
}
```

Rules:

- the candidate lexical grammar is
  `^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:e-?(?:0|[1-9][0-9]*))?$`;
- leading plus, leading zeros, whitespace, comma decimal, and undocumented alternate exponent forms are rejected;
- uppercase `E`, positive exponent signs, and every lexical negative zero are
  rejected in this profile version rather than normalized;
- whether trailing zeros are significant is expressed by semantic type/precision, not discarded casually;
- ratios, probabilities, p/e-values, interval levels, currency, resource measures, and physical quantities use distinct registered types;
- unit conversion is a semantic transformation producing a new object, not canonicalization;
- interval bounds must share compatible semantic type/unit and are ordered by semantic validation;
- missing, unknown, unmeasured, unavailable, withheld, and not-applicable carry no numeric placeholder.

The initial draft schemas’ generic decimal strings are structural prototypes. Gate A requires migration to the accepted typed-number definitions where scientific meaning is present.

## Time

Odeya distinguishes:

- controlled canonical commit time;
- source-reported occurrence time;
- observation/capture time;
- effective/not-before/expiry interval;
- scientific measurement time and clock/frame;
- human display-localized time.

The leading canonical instant profile is UTC `Z` with exactly six fractional decimal digits:

```text
YYYY-MM-DDTHH:MM:SS.ffffffZ
```

The candidate calendar range is year 0001 through 9999 with Gregorian calendar
validity, hour `00`–`23`, minute/second `00`–`59`, and no leap-second lexical
form. Pre-epoch instants are therefore representable, but their admissibility
for a particular scientific field remains a schema/semantic rule. Clock source,
monotonic ordering, precision, and uncertainty remain explicit registry data.
External timestamps retain the original lexical value and source alongside a
normalized instant only when conversion is defined. User/local time zones exist
in projections, never canonical identity.

`format: date-time` is necessary structural validation but does not enforce this profile or temporal ordering. Semantic rules enforce issue/not-before/expiry, occurred/recorded, seal/expiry, exposure, and observation order.

## Collections and ordering

Canonicalization never guesses whether an array is a sequence or set.

- Sequence arrays preserve declared order, and order is scientifically meaningful.
- Set-like collections use a schema-specific normalization rule that rejects duplicates and sorts by a registered key or canonical element bytes before the enclosing object is admitted.
- Maps use stable identifiers as keys only when the schema defines that key space.
- A producer-supplied arbitrary order cannot produce multiple identities for one intended set.
- Sorting rules include null/missing behavior, Unicode/profile, numeric semantic comparison, and tie-breakers.

Every set-normalization is an explicit semantic transformation with a rule version. The raw submitted object and normalized candidate may both be retained; only the admitted normalized object receives canonical identity.

The fixture profile `conformance-collections:0.1.0` demonstrates one exact rule:
reject duplicate strings and sort the admitted `tags` set by the UTF-8 bytes of
each element's JCS serialization. Its `sequence` field remains in submitted
order. That fixture proves the distinction; it does not assign set semantics to
any production schema.

## References

A canonical reference contains exact type, identifier/version where applicable, digest, and media/schema identity. It never relies only on a filename, branch, URL, database row number, vector similarity, mutable object key, or provider alias.

Reference validation occurs offline against a registry snapshot or exact ledger position. It proves existence/identity and scope compatibility separately. Circular reference graphs use stable object IDs plus a sealed manifest/root digest; objects do not embed mutually recursive content digests.

## Artifacts and packages

- Raw artifacts hash exact streamed bytes before storage materialization.
- Multipart/provider checksum metadata is evidence but does not replace the Odeya byte digest.
- Directories, research packages, and environments use a canonical manifest of path, media type, length, byte digest, mode/role metadata, and stable ordering; archive-container bytes may additionally have their own digest.
- Symbolic links, hard links, device files, sparse files, executable bits, timestamps, ownership, extended attributes, path separators, case folding, and Unicode filenames must be explicitly admitted or refused by the package profile.
- Archive extraction rejects traversal, absolute paths, duplicate normalized paths, unsafe links, decompression bombs, and ambiguous encodings.
- Git commit identity is recorded but does not replace a clean-worktree/source-bundle digest and dependency/submodule identities.

## Signatures and attestations

Signatures bind the canonical digest plus purpose, identity, key, algorithm, trust root, and policy context. They establish origin/integrity within those assumptions, not scientific validity or independence.

The signature envelope is outside the hashed scientific subject to avoid self-reference. Re-signing or key rotation adds an attestation; it does not change the subject digest. Timestamp attestations retain the time authority and uncertainty/trust policy.

## Conformance vector families

Gate A vectors must cover:

1. official RFC 8785 examples;
2. duplicate keys and parser differentials;
3. ASCII, control escapes, supplementary Unicode, combining forms, look-alike text, unpaired surrogates, and UTF-16 sort edge cases;
4. zero, negative zero, integer bounds, exponent thresholds, rounding, subnormal/overflow attempts, and forbidden non-finite values;
5. exact decimal lexical forms, precision, unit, interval, ratio, probability, and missingness;
6. timestamp precision, offset normalization refusal, invalid calendar values, leap-second policy, and temporal order;
7. ordered versus set-like arrays and duplicate elements;
8. reference cycles, missing schema/rule, wrong digest/type/scope, and mutable identifiers;
9. raw/normalized/transcoded/redacted artifacts and archive path attacks;
10. self-reference, algorithm/profile migration, and old-reader behavior.

Each vector contains input bytes, expected parse/admission result, expected canonical bytes or refusal code, expected digest when admitted, and rationale. Known-bad cases must fail in every supported implementation.

## Independent implementations

Before Gate A can freeze this profile:

- one minimal reference implementation and one independently implemented verifier in different runtime/library paths must agree on every vector;
- neither implementation may call the other or share canonicalization code;
- differential fuzzing must preserve minimized counterexamples;
- implementation/library/version/environment identities and limits are retained;
- disagreement blocks identity issuance and becomes a critical architecture finding.

These are architecture conformance tools, not the Odeya runtime. Their construction remains within the pre-implementation validator allowance only after the profile itself is accepted for testing.

## Retained conformance evidence

[`tests/canonicalization`](../tests/canonicalization/README.md) retains the
shared inputs, exact expected bytes/digests/refusal codes, dependency/source
locks, independently written runners, results, and comparison receipt.

| Evidence | Result |
|---|---|
| Python path | CPython 3.14.2 + Trail of Bits `rfc8785==0.1.4` |
| Node path | Node.js 20.18.3 + Erdtman/Rundgren `canonicalize==3.0.0` |
| Shared vectors | 64 total: 19 admissions, 45 fail-closed refusals |
| Upstream evidence | All six retained author vector families matched exact bytes |
| Metamorphic evidence | Four relations passed: no Unicode normalization, schema domain separation, set normalization, sequence preservation |
| Differential result | Zero disagreements and zero unclassified runner errors |

The paths use separate parsers, semantic admission code, runtimes, and RFC 8785
libraries. The comparison validates every input digest and every expected
canonical byte string or refusal code. This supports bounded cross-runtime
agreement; it does not establish organizational independence, source-to-package
reproducibility, package signatures, absence of shared conceptual lineage,
formal correctness, or behavior outside the retained vectors.

[`SCHEMA_AUDIT.json`](../tests/canonicalization/SCHEMA_AUDIT.json) is the
machine-readable migration inventory. It deliberately keeps profile-freeze
findings blocking while the underlying schema or fixture bytes remain
nonconformant; refreshing the file without resolving those findings is not
closure.

## Migration

Canonical identities are immutable within a profile. A new profile:

1. retains original bytes, old canonical bytes, schema/profile, and digest;
2. produces a new canonical object only through an explicit migration activity;
3. links old/new with rule, code, environment, and validation evidence;
4. never claims digests are equal across profiles;
5. preserves readers or exports for the accepted retention period;
6. triggers dependent signature, reference, package, and publication review.

## Acceptance blockers

The timestamp, exact-decimal, missingness, one string-set normalizer, exact
reference shape, self-reference refusal, and envelope domain separation now
have retained two-path evidence. The profile remains proposed until:

- every current architecture schema is migrated to or explicitly exempted from
  the timestamp, scientific-number, reference, and digest-scope rules;
- interval, ratio/probability, package/archive, graph-cycle, artifact
  transformation, profile migration, and old-reader vectors are complete;
- differential/property fuzzing is independently reviewed and its minimized
  counterexamples are retained;
- parser/resource limits are measured under adversarial inputs on independently
  controlled hosts;
- dependency provenance and source-to-distribution assumptions are resolved or
  accepted explicitly; and
- the operator signs the exact profile, vector, schema-registry, runner, and
  result digests.

Until then, draft `sha256:` fields establish intended shape but not a frozen
cross-runtime Odeya identity contract.
