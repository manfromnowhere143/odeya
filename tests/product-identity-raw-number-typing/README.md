# PRQ-002C raw-number token typing observation

This architecture-only suite observes one prerequisite for a future
raw-token-aware product-identity profile. It does not amend or issue the frozen
`odeya-jcs-0.2` candidate, create `odeya-jcs-0.3`, validate a product member,
compute a product digest, admit a registry resource, bind a root, accept Gate
A, or authorize runtime or publication.

The child-visible `vectors.json` contains 61 opaque-ID raw-byte frames and no
expected disposition, reason code, or descriptive case name. Each decoded
input is bound by SHA-256 and byte count. Comparator-only `cases.json` retains
9 accepted expectations, 52 intent-bound refusals, and 44 gate attacks.
Those 44 attacks exercise exact JSON types and shapes, non-finite parsing,
suite inventory, dependency and source-import boundaries, timestamps,
comparison, and explicit nonclaims; they are not evaluator-source ablations
of every semantic branch. The 61 outcomes plus fresh recomputation are bounded
observations of the semantic behavior.

The two children do not share evaluator source:

- CPython 3.14.2 uses standard-library `parse_int` and `parse_float` hooks to
  retain numeric lexemes before mapping.
- Node.js 24.18.0 uses a source-distinct recursive-descent JSON parser.

Both emit the complete ordered staged projection: decoded-input binding,
lexical disposition, raw token and byte count, token class, binary64 conversion
class, integer-position disposition, final disposition, final code, and
admitted decimal integer. A later stage is `null` when an earlier refusal wins.
Compound inputs verify UTF-8 before BOM, complete JSON grammar before duplicate
name and unpaired-surrogate restrictions, and duplicate decoded names before
unpaired surrogates. A prototype-named extra member verifies classified frame
refusal instead of a native runtime crash.

The children receive no comparator expectation or peer path in argv or the
declared input manifest. Their retained source declares no such read. This is
not an OS-level filesystem-isolation observation, and the literal/static
source scan does not exclude dynamically constructed paths or filesystem
discovery.

The fixed microframes associate the observed token with one known
`integer_value` position. They do not prove retention or resolution of a
generic unique instance pointer. The retained execution receipts are
self-attested byte-consistency records, not independently witnessed historical
process captures; the recomputation mode executes both current children with
fresh challenges and requires byte-for-byte result equality.

The stale implementation-causal-binding known-bad copies one result and
relabels its implementation metadata without recomputing the public binding.
It proves refusal of that inconsistent binding, not refusal of a coherently
relabelled copy. Retained-output origin and the historical processes remain
unwitnessed; fresh recomputation establishes only what the two current
executions emitted.

## Validate retained evidence

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv-architecture/bin/python -B \
  scripts/validate_product_identity_raw_number_typing.py
```

The default check validates the contract schema, exact frozen `0.2`
predecessor inventory, answer-free boundary, source manifests, retained
results, self-attested retained execution receipts, complete projection
comparison, and all gate known-bads without executing either child.
It also pins the exact runner byte surfaces and rejects every unexpected file
or symlink in the suite, including hidden dependency trees. Those checks do not
constitute an OS-level sandbox or an independently witnessed execution.

## Recompute both children

```bash
ODEYA_PRQ002C_NODE="$(bash scripts/ci/install-node.sh)"
ODEYA_PRQ002C_PYTHON="$(
  .venv-architecture/bin/python -I -S -B \
    -c 'import sys; print(sys.executable)'
)"

PYTHONDONTWRITEBYTECODE=1 \
  "$ODEYA_PRQ002C_PYTHON" -B \
  scripts/validate_product_identity_raw_number_typing.py \
  --recompute-all \
  --python-executable "$ODEYA_PRQ002C_PYTHON" \
  --node-executable "$ODEYA_PRQ002C_NODE"
```

A green run is bounded agreement across two fixed synthetic integer-position
frame profiles. Generic schema-path applicability, the full nine-domain framing
contract, generic instance-pointer retention, ordered-map laws, cross-object
replay, number-position completion, offline historical resolution, dynamic
path-discovery exclusion, independently witnessed historical execution,
organizational independence, accountable review, and operator acceptance
remain unproved.
