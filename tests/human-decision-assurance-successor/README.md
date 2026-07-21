# HumanDecisionAssurance successor conformance evidence

Status: retained architecture-only candidate evidence for the unissued PRQ-013
successor selected by ADR 0095. Nothing here is a real ceremony, an issued
profile or schema, an approval, accountable review, Gate A acceptance, runtime
authority, or evidence about a natural person. Fixed timestamps are
deterministic fixture times only; they are not observations or trusted time.

## Retained boundary

The candidate contains five successor schemas and seven schema-valid fixtures:
Evidence 0.2, one backing-byte verification receipt, three separately wrapped
eligibility recomputation results, one eligibility comparison receipt, and
Seal 0.2. The published 0.1 resources remain immutable and unissued; the new
resource identities are also unissued.

The backing inventory is closed over fourteen roles. Each synthetic preimage
is retained as actual bytes at its content-address-derived repository path.
Validation dereferences those bytes and independently rederives their raw
SHA-256 digest, byte count, descriptor relation, and receipt row; neither a
filename nor a recorded digest is accepted as proof of content. The exact
binary `ODEYA-HDA-CONFIRMATION-RECEIPT-V1` frame is one of those preimages.
Synthetic backing bytes are conformance inputs, not real-world evidence.

## Hard answer boundary

`vectors.json` is the only vector corpus an eligibility implementation may
read. It contains one synthetic evaluator input and deterministic RFC 6902
mutations. It contains no expected disposition, expected reason code,
expected error, implementation output, comparison receipt, Seal, or
placeholder result.

`cases.json` is the private conformance answer file. A runner applies a vector,
passes only the materialized input plus the exact ruleset and resolver profile
to an implementation, and compares the returned output to the corresponding
case afterward. An evaluator, input adapter, code generator, prompt, build
step, or fixture generator must never read `cases.json` or a value derived
from it. Every adversarial case names a safe control and records both the full
diagnostic set and the subset that proves the intended refusal.

Start from `base_input`. If a vector names `base_vector_id`, recursively apply
that base vector first. Reject cycles and unknown IDs. Apply mutations in
listed order using only `add`, `copy`, `move`, `remove`, and `replace` with
standard JSON Pointer escaping. Preserve array order, exact strings, nulls,
and raw Base64 text. Do not normalize input before hashing or evaluation.

The retained answer-free corpus contains 44 vectors. It covers contradiction
precedence, atomic-action identifier and backing-role rules, public verifier
inventory, sanitation and forbidden-content precedence, exact confirmation
receipt framing, and missing, mismatched, malformed, omitted-row, and
false-zero backing-byte conditions.

## Three recomputation paths

Three source-separated implementations consume only the allowed common
normative inputs:

- Python 3.14.2 under its exact dependency and runtime profile;
- Node.js 24.18.0 under its exact package lock and runtime profile; and
- Temurin Java 21.0.9 under separate source, configuration, adapter,
  dependency, and runtime profiles.

The architecture validator's Python evaluator subprocesses use the
interpreter-level `-B -E -s` isolation profile. A bounded validator self-test
proves that `-B` prevents bytecode writes while the environment-only
`PYTHONDONTWRITEBYTECODE=1` control is ignored by `-E` and does create the
known-bad cache in a disposable directory. This keeps validation recomputation
from mutating the retained evaluator source tree. The separately byte-bound
evidence generator uses another invocation path; this correction neither
changes that bound source nor claims its authoring path is clean-tree-safe.

They do not share Odeya evaluator source, generated evaluator code, parsing or
normalization helpers, intermediate state, answers, or each other's outputs.
Each implementation passed all 44 expectation-free vectors, for 132 exact
recomputations. The retained positive projections agree across the complete
six-field output: `participant_id`, `domain_results`,
`categorical_results`, `categorical_failures`, `final_disposition`, and
`reason_codes`. Deterministic wrapping binds, but does not reinterpret, each
direct evaluator projection.

This proves source separation, the declared non-sharing boundary, and bounded
agreement for these retained bytes. It does not prove organizationally
independent authorship or review. All three paths share the normative schemas,
ruleset, resolver profile, and input bytes, so a correlated specification
defect can survive exact agreement.

## Downstream chain refusals

`chain-cases.json` retains 48 intent-bound chain known-bads. They attack
backing truth, deterministic negative reasons, result/source identities,
complete projection comparison, acyclicity, receipt and Seal bindings,
runtime/dependency pins, source non-sharing, and immutability of the 0.1
resource identities. Each mutation is evaluated against its declared safe
control and intended diagnostic; an unrelated refusal does not earn credit.

The complete retained generation chain is therefore bounded by:

- 14 content-addressed synthetic backing preimages;
- 44 answer-free evaluator vectors and 132 exact cross-toolchain
  recomputations;
- exact six-field projection comparison;
- 48 downstream chain known-bads; and
- a generation manifest that records false authority boundaries and forbids a
  self-digest.

These counts describe the exact retained corpus, not general correctness,
standards conformance, a real ceremony, or consumer integration.

## Adoption and authority boundary

The T0 byte-bound/recomputation tranche is retained candidate evidence, but
ADR 0095 adoption remains incomplete until a context-isolated technical-review
determination is retained over the exact candidate bytes. That review must be
labelled correlated/non-accountable and cannot establish organizational
independence, accountable security or authority review, or Gate A acceptance.

No current consumer is migrated. T1 `AuthorityAssignment`, the required T2
command/event/state/reducer/currentness/quorum contracts, the
`AssuredDecision` wrapper, end-to-end consumer refusal, accountable review,
profile and schema issuance, and the operator's exact-byte Gate A decision all
remain open. Gate A remains blocked. This evidence authorizes no live ceremony,
cloud access, network service, runtime, deployment, spending, publication, or
external effect.
