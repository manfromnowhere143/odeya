# Odeya canonical identity conformance suite

Status: architecture-only evidence for proposed profile `odeya-jcs-0.1`.
This directory is not Odeya runtime or product code. It exists to make the
identity contract reviewable before Gate A.

## What this suite proves

Two separately implemented paths consume the same immutable vector manifest:

- Python 3.14 with Trail of Bits `rfc8785==0.1.4`; and
- Node.js 20 with `canonicalize==3.0.0` by Samuel Erdtman/Anders Rundgren.

Each path independently performs raw-byte admission, strict JSON parsing,
Odeya semantic admission/normalization, RFC 8785 serialization, envelope
construction, and SHA-256 calculation. Neither runner invokes or imports the
other. `compare_results.py` checks each result against the manifest and then
checks the two retained result documents against one another.

The suite covers the upstream author vectors, parser refusals, the verified
RFC 8785 negative-zero erratum, UTF-16 ordering, IEEE-754 serialization edges,
typed scientific values, fixed UTC microsecond timestamps, ordered and
set-normalized collections, exact references, self-reference refusal, and
profile/schema domain separation.

Passing these vectors proves byte agreement only within the declared
environment, dependency, limit, schema-registry, and vector bounds. It does
not prove scientific equivalence, schema correctness, collision resistance
beyond SHA-256's stated assumption, artifact existence, registry authority,
runtime safety, or implementation independence in an organizational sense.

## Reproduce without network access

Install dependencies once from verified package artifacts, then execute the
suite with networking disabled. Package artifacts themselves are not vendored.

```bash
python3 -m venv /tmp/odeya-canonicalization-python
/tmp/odeya-canonicalization-python/bin/python -m pip install \
  --no-index --find-links /approved/package-cache --require-hashes \
  -r tests/canonicalization/requirements.txt
npm ci --offline --ignore-scripts --prefix tests/canonicalization/node

/tmp/odeya-canonicalization-python/bin/python \
  tests/canonicalization/runner_python.py > /tmp/odeya-python-result.json
node tests/canonicalization/runner_node.mjs > /tmp/odeya-node-result.json
python3 tests/canonicalization/compare_results.py \
  /tmp/odeya-python-result.json /tmp/odeya-node-result.json
```

Replace `/approved/package-cache` with the directory containing the exact wheel
named in `source-lock.json`; prime the npm cache with the exact locked tarball
before disconnecting. An approved registry may be used in a separately recorded
provisioning step, but not by the commands above. The three execution commands
perform no network operation. The checked-in result files are evidence from the
environment named inside them; they are not a substitute for rerunning on an
independently controlled host.

## File contract

- `manifest.json` is the shared vector and trial-limit contract.
- `schemas/` is a fixture-only, digest-pinned schema registry for envelope
  domain-separation tests; it is not the Odeya production schema registry.
- `official/` retains Apache-2.0 author vectors at one exact upstream commit.
- `source-lock.json`, `requirements.txt`, and `node/package-lock.json` pin
  provenance and distributable package bytes.
- `results/` retains normalized, deterministic result evidence. Volatile host
  facts are confined to the separate environment section.
- `SCHEMA_AUDIT.json` is the machine-readable migration/blocker inventory for
  the current top-level architecture schemas and retained architecture-schema,
  architecture-review, cognitive, projection, physical, and mathematical
  contract fixtures. Missing optional fixture directories contribute no files;
  every included path and byte is bound into the reported fixture-corpus hash.

Regenerate and then verify that report deterministically with:

```bash
python3 tests/canonicalization/audit_schemas.py --write
python3 tests/canonicalization/audit_schemas.py --check
```

## Refusal vocabulary

Refusals are stable architectural reason codes, not exception strings:

```text
ODEYA_LIMIT_BYTES
ODEYA_LIMIT_DEPTH
ODEYA_LIMIT_OBJECT_MEMBERS
ODEYA_LIMIT_ARRAY_ITEMS
ODEYA_LIMIT_STRING
ODEYA_LIMIT_NUMBER_TOKEN
ODEYA_LIMIT_TOTAL_NODES
ODEYA_PARSE_BOM
ODEYA_PARSE_UTF8
ODEYA_PARSE_DUPLICATE_KEY
ODEYA_PARSE_UNPAIRED_SURROGATE
ODEYA_PARSE_SYNTAX
ODEYA_NUMBER_NEGATIVE_ZERO
ODEYA_NUMBER_NONFINITE
ODEYA_NUMBER_UNDERFLOW
ODEYA_NUMBER_DOMAIN
ODEYA_PROFILE_UNKNOWN
ODEYA_SCHEMA_UNREGISTERED
ODEYA_SCHEMA_ID_MISMATCH
ODEYA_SUBJECT_SELF_REFERENCE
ODEYA_TIMESTAMP_PROFILE
ODEYA_DECIMAL_LEXICAL
ODEYA_DECIMAL_NEGATIVE_ZERO
ODEYA_QUANTITY_SHAPE
ODEYA_PRECISION_MISMATCH
ODEYA_MISSINGNESS_SHAPE
ODEYA_SET_DUPLICATE
ODEYA_REFERENCE_SHAPE
ODEYA_REFERENCE_MUTABLE
ODEYA_REFERENCE_DIGEST
```

Any unclassified crash is a suite failure; it is never converted to admission.
