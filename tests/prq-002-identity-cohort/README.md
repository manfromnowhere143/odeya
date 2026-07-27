# PRQ-002A structural identity cohort probe

This architecture-only suite probes the proposed PRQ-002A identity structure.
It is deliberately `test_only_non_issuable_structural_probe` evidence. It does
not issue a canonical identity, admit anything to a registry, create a product
schema, bind an engine contract root, authorize runtime or external effects,
accept Gate A, or authorize publication.

The retained safe cohort contains 21 probe objects:

- one exact standalone probe-profile instance;
- nine schema members and three graph members;
- four flat ordered-member-map commitments; and
- four pure, homogeneous registry snapshots.

The suite recomputes 20 structured digests: 12 member digests, four commitment
digests, and four snapshot digests. Its digest framing is local to this probe:
RFC 8785 bytes of the exact object with the three members `digest_contract`,
`resolved_subject_schema`, and `projection`, followed by SHA-256. This is not a
production canonical envelope and it is not a Merkle construction.

## What is retained

`fixtures/candidate-cohort.probe.json` is checked against the nine
`architecture/prq-002-*` schemas and the exact standalone profile core at
`architecture/prq-002-identity-probe-profile-core.json`. The four-field
`canonicalization_profile_ref.profile_core_raw_digest` binds the raw digest of
that profile-core document. It does not bind the distinct raw digest of the
profile schema. A dedicated known-bad case substitutes the schema digest in a
snapshot digest contract and requires an attributed refusal.

`cases.json` contains 47 cases: one safe cohort and 46 exact, single-mutation
known-bads. They exercise strict JSON input handling, profile and raw-schema
byte bindings, digest contracts and results, graph directionality, flat-map
ordering and membership, snapshot purity, predecessor immutability, and
profile-core document binding. Every adversarial case declares an intent error
and an exact expected error inventory.

The Python and JavaScript evaluators are source- and language-separated. The
retained comparison establishes exact agreement for this bounded cohort; it
does not establish organizational independence. The source manifests declare
that the evaluator source requests no network access; that declaration is not
an OS-level network restriction or an observation proving non-use. They also
bind every immutable installed canonicalizer payload file and separately bind
the Node package manifest and lock. The retained parser observation confirms
that both runtimes accept positive and negative finite IEEE-754 underflow to
signed zero, while the probe's lexical `-0` refusal remains intact; this does
not add to or alter the 47-case evidence graph.

Execution receipts retain the actual observed Darwin/arm64 executable paths,
resolved executable byte digests and sizes, exact historical argv and
challenges, the child attestations, both complete two-line stdout bindings,
each attestation-line binding, each retained result-line binding, and
repository toolchain/installer bindings. Those executable observations are
historical evidence. Portable recomputation anchors Python to the already
running checker's startup-bound CPython image and Node to the current
platform's digest-verified installer product; it does not require another
host's executable bytes or paths to equal the historical host.

## Validate retained evidence

The default check uses the repository's existing architecture-validation
environment. It does not import or execute either external canonicalizer:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv-architecture/bin/python -B \
  tests/prq-002-identity-cohort/check.py
```

This validates exact file inventories and bindings, complete JSON Schema
conformance, the bounded local recomputation, all attributed known-bads,
retained result agreement, source separation, and receipt bindings.

## Recompute both implementations

Install the exact locked canonicalizers, using the repository's pinned Node.js
24.18.0 installer. Bootstrap installation may read a local cache or use the
network; it occurs before the evaluator processes:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  .venv-architecture/bin/python -m pip install \
  --disable-pip-version-check \
  --no-input \
  --require-hashes \
  --only-binary=:all: \
  --no-compile \
  --requirement \
  tests/prq-002-identity-cohort/python/requirements.lock

ODEYA_PRQ002_NODE="$(
  bash scripts/ci/install-node.sh
)"
ODEYA_PRQ002_PYTHON="$(
  .venv-architecture/bin/python -I -S -B \
    -c 'import sys; print(sys.executable)'
)"
PATH="$(dirname "$ODEYA_PRQ002_NODE"):$PATH" \
  "$(dirname "$ODEYA_PRQ002_NODE")/npm" ci \
  --ignore-scripts \
  --no-audit \
  --no-fund \
  --prefix tests/prq-002-identity-cohort/node

PYTHONDONTWRITEBYTECODE=1 \
  "$ODEYA_PRQ002_PYTHON" -B \
  tests/prq-002-identity-cohort/check.py \
  --recompute-all \
  --python-executable "$ODEYA_PRQ002_PYTHON" \
  --node-executable "$ODEYA_PRQ002_NODE"
```

The full check requires CPython 3.14.2 with `rfc8785==0.1.4`, Node.js 24.18.0,
and the lock-installed `canonicalize==3.0.0`. The selected Python must resolve
to the same executable image whose bytes the parent checker bound at startup.
The selection uses the interpreter's self-reported absolute executable path
so an operating-system path alias cannot make the child attest a different
string from the checker command.
The child runs with exact `-I -S -B` isolation flags and compiles the verified
`rfc8785/_impl.py` bytes from an explicit package root; it does not import the
installed package and rejects package-local bytecode/import caches. This does
not require a virtual environment, reject unrelated system `.pth` files, or
claim isolation of the already-running parent process. The clean bootstrap
uses pip's `--no-compile` option so the admitted wheel payload is not augmented
with derived bytecode; the option does not clean a contaminated environment,
which remains a refusal.

The selected Node must be the exact current-platform product of
`scripts/ci/install-node.sh`. The checker verifies the pinned archive digest,
requires its `bin/node` member to be a regular file, reruns the installer, and
requires archive-member and selected-binary bytes to agree before and after.
The Node evaluator rejects an ambient canonicalizer-module override.

Each child emits exactly two RFC 8785 JSON lines: a fresh-challenge execution
attestation bound to the actual executable, argv, immutable inputs, evaluator,
canonicalizer source, and exact result line; then the deterministic result.
The checker validates executable bytes before and after each child, validates
the complete attestation and its canonical bytes, and compares only the second
line byte-for-byte with the retained result.

No evaluator is run under an OS-level network sandbox. The evaluator source
manifests only declare that their source requests no network access. The
trusted preconditions remain the already-running parent CPython/stdlib, the
OS kernel and process loader, filesystem and hardware behavior, SHA-256, and
the absence of a hostile same-user race.

Green output remains structural probe evidence only. Architecture acceptance
still requires the separate retained-evidence and operator-acceptance process
defined by the pre-implementation gate.
