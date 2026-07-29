# PRQ-002E `odeya-jcs-0.3` construction evidence

Status: architecture-only evidence for a proposed, unissued, unadmitted
side-by-side candidate. A pass is not canonicalization conformance, product
identity, Gate A acceptance, runtime authority, or publication authority.

This suite answers one bounded question: do two source- and
language-separated observers agree on the complete exact-byte inventory of
the twelve new schema resources and three candidate records after the
final-only freeze DAG was constructed?

[`check.py`](check.py) independently checks the stronger retained
construction boundary around that observation. It verifies the exact
`617209ba480b854a00c6a15cd99ac1d5a18e90ad` /
`67c38b895276bf2c804fe192339ce90a8c75ea97` predecessor objects and live
132-row byte manifest; the disjoint twelve-resource successor cohort and
132 + 12 = 144 schema census; unique successor IDs, domains, profile
annotations, raw digests, and byte counts; closed Draft 2020-12 validation;
and the final-only schemas → core → evidence → migration dependency order.
Every repository read requires a lexically contained, non-symlink regular
file, and repository paths containing NUL are refused before filesystem
access; the deterministic generator applies the same boundary to frozen
inputs, readback, existing outputs, install parents, and install targets.
Those checks are bounded to this lane's exclusive-writer procedure. They are
not descriptor-relative process isolation against a hostile concurrent
ancestor-directory rename.

The checker also derives the complete static numeric-position inventory again
from the twelve raw schema byte strings. That derivation covers every
`type: integer` assertion, recursively integer-valued `const` leaf, and exact
resolved `$ref` edge, while refusing `type: number`, number-admitting unions,
fraction/exponent number tokens, boolean/integer confusion, unresolved
references, and unclassified numeric positions.

The answer-free [`input-manifest.json`](input-manifest.json) fixes exactly
fifteen ordered role/path pairs. Both observers also hard-code that inventory,
so a missing, added, duplicated, or reordered row cannot become consensus by
mutating only the shared manifest.

- [`python/observer.py`](python/observer.py) runs under pinned CPython 3.14.2
  with isolated mode (`-I`), rejects duplicate decoded object names and
  non-finite constants, and inventories exact bytes plus raw number lexemes.
- [`node/observer.mjs`](node/observer.mjs) runs under pinned Node.js 24.18.0,
  performs a source-distinct recursive syntax and duplicate-name walk before
  `JSON.parse`, and produces the same closed projection.

Ordinary validation pins the exact five observer/dependency source bindings,
the dependency-lock semantics, the distinct `.py`/`.mjs` primary subjects,
and the exact retained CPython and Node version, basename, executable digest,
and byte count. Execution receipt objects are closed recursively. Their UTC
timestamp must be a real calendar time, not merely a timestamp-shaped string.

The retained result files are the exact compact UTF-8 stdout bytes emitted by
each child. The authoring parent parses them with duplicate and non-finite
refusal, checks a closed result shape, independently rebinds every artifact
row to the live file, compares JSON with recursive type-strict equality, and
only then writes the execution and comparison receipts.

Ordinary validation rereads all seven retained observer artifacts, recomputes
their live source/input/result/execution/comparison edges and complete
15-artifact projection, and verifies the construction-only false/null claim
boundary. The declarative corpus contains one safe control and 45 attributed
single-fault known-bads. The exact 1 + 45 partition and every complete ordered
case row—including every mutation field and recursively type-strict JSON
value—are pinned in the checker and admitted before any production validator
runs. A built-in admission meta-proof swaps two distinct same-operation,
same-guard symlink payloads and requires the substituted corpus to be refused
before execution. The safe control executes the complete production validation
path. Each known-bad mutates actual retained JSON bytes, raw bytes, inventory
state, or file type inside an in-memory repository overlay, invokes the same
production validator used by the live path for that boundary, and must produce
exactly one named production guard code. The observer comparison receipt also
has production-path cases proving that integral float tokens `2.0` and `15.0`
cannot satisfy the exact integer `observer_count` and `artifact_count`
contracts. No self-test changes shared repository bytes.

The observed `literal_type_number_occurrence_count` is deliberately named as a
literal census. It is not generic JSON Schema applicability evidence. Static
schema-position inventory belongs upstream in the profile core; per-subject
raw evaluation traces belong to a later downstream evidence unit so neither
the core nor its evidence record can depend on a trace about its own final
bytes.

## Retained limits

The observers and receipts do not prove:

- complete RFC 8259, I-JSON, RFC 8785, or JSON Schema conformance;
- generic `$ref`, applicator, instance-pointer, or integer-position
  evaluation;
- OS-level filesystem or network isolation;
- organizational independence, independent-host reproduction, or causal
  historical execution origin;
- exclusion of coherently copied peer output;
- complete offline resolution or durable historical retention;
- any product digest, member, commitment, registry, root, activation, or
  issued identity.

Those values remain false or null in the comparison receipt and in the
profile evidence record.

## Reproduction

Bootstrap the repository's pinned architecture environment, obtain the pinned
Node executable through `scripts/ci/install-node.sh`, and then run:

```bash
node_bin="$(bash scripts/ci/install-node.sh)"
challenge="challenge-v1:<64 lowercase hexadecimal characters>"
observed_at="2026-07-29T<hh:mm:ss>Z"

.venv-architecture/bin/python \
  tests/product-identity-profile-0.3-candidate/authoring/run_observers.py \
  --node-bin "$node_bin" \
  --challenge "$challenge" \
  --observed-at "$observed_at"

.venv-architecture/bin/python \
  tests/product-identity-profile-0.3-candidate/check.py
```

The authoring command changes retained evidence and is not part of an ordinary
validation run. The checker validates retained bytes without executing either
observer. Therefore exact current source and receipt closure still does not
prove causal historical execution, process isolation, or independence. Its
production-path known-bad corpus can be exercised independently with:

```bash
.venv-architecture/bin/python \
  tests/product-identity-profile-0.3-candidate/check.py --self-test-only
```
