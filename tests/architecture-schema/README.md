# Architecture schema conformance

This directory tests the architecture contracts only. It does not implement or
exercise an Odeya runtime, and a pass is not Gate A acceptance.

`manifest.json` registers immutable valid fixtures plus explicit JSON Pointer
mutations that must be rejected. The validator first proves every adversarial
case starts from a valid base; this prevents a broken base fixture from creating
a false-positive rejection. Every schema must have at least one valid and one
invalid case.

The harness asserts JSON Schema Draft 2020-12 meta-validity, rejects duplicate
JSON object members, enables RFC 3339 `date-time` format assertions, and refuses
dependency-version drift. Run it in an isolated environment:

```bash
python3 -m venv .venv-architecture
.venv-architecture/bin/python -m pip install -r requirements-architecture.txt
.venv-architecture/bin/python scripts/validate.py
```

These are structural tests. Ordering of timestamps, digest recomputation,
cross-record referential integrity, authority separation, unit compatibility,
transactional invariants, and scientific validity require semantic validators
and later Gate B probes; schema acceptance must never be presented as evidence
for those properties.

The fixture family now also exercises immutable protocol snapshots/amendments,
run manifests, artifact manifests and custody, metric/falsifier results,
validation registries/results, corrections, handoffs, grounded outcomes, and
quarantined strategy/promotion records. Each adversarial mutation targets a
substantive fail-closed invariant rather than merely adding an unknown field.

The governance family adds closed root-manifest and role-assignment records;
data asset, rights-assertion, use-decision, exposure, transformation,
retention, deletion, and legal-hold records; and the noncircular publication
candidate/decision/manifest/grant sequence. Its known-bad mutations prove only
structural refusal: a rights assertion cannot become permission, a hold cannot
become access authority, an indeterminate decision cannot retain executable
scope, publication authorization cannot retain an indeterminate gate, and a
dispatch-bound publication grant cannot consume at intent time. Exact digest
relations, decision/assignment validity, temporal order, scope subset,
reservation races, lineage completeness, and real deletion remain semantic or
implementation obligations.

The recovery/effect family also covers ordered data-governance,
recovery, governed-processing, and resource-accounting traces. It structurally rejects a stale or
revoked processing authorization that claims any reservation, grant use,
external-effect authorization/start, or spend cohort. Envelope/receipt cases
require exact-version registry snapshot, separate activation, and member-record
references, while checkpoint cases require the exact EngineContractRoot,
AggregateStateSubjectRegistry, complete C0 registry slots, and an exact
non-self-referential digest contract. These mutations do not verify
registry membership or activation, current ledger position, digest
recomputation, schema/profile bytes, signatures, reducer equivalence, or C0
bundle compatibility; the semantic validators and conformance vectors must do
that independently.

The admission family makes the future post-registry boundary explicit while
all current 0.4 receipt subjects remain nonconstructible and not admitted. The
schema-unresolvable structural fixture models the shape that would follow a
resolved member and exact payload-schema identity; mutating it to
`unknown_command` is rejected because no truthful member-bound receipt could
exist. CommandEnvelope 0.5.0 retains the exact 0.4.0 design vocabulary as
historical source evidence, exposes only typed `untrusted_resolve_only`
authority hints, and rejects caller-selected authority modes, derivation
rules, trusted-hint claims, loose assignment strings, and PolicyDecision
references. PolicyDecision fixtures keep
`allow | deny | indeterminate`, evaluation status, obligations, exact
policy/rule/engine/frontier inputs, and non-self-referential identity separate;
AdmissionEvidenceBundle fixtures bind the CommandContractRecord-selected exact
twelve-stage sequence and evidence index. The rejected-policy fixture proves
one decisive terminal stage plus a closed explicit not-run suffix; mutations
reject accepted-with-failure, suffix resumption, duplicated/out-of-order stages,
failure without evidence, and evidence on a not-applicable stage. Checkpoints
must commit the admission-evidence set. These
are still structural claims: they do not prove deterministic policy execution,
obligation enforcement, evidence completeness, or receipt/event causality.

The resource family covers all six lifecycle facts: reservation creation,
claim, pre-claim release, pre-claim expiry, usage observation, and settlement.
Five replay traces preserve a claimed ceiling across crash, prove release and
expiry are pre-claim only, settle the exact five-dimensional verification
capacity vector, and keep unavailable usage distinct from zero. Mutations reject
cross-resource conversion, incomplete start cohorts, actual-use inference at
claim, release after claim, missingness with a numeric vector, and settlement
without exact observations. These shapes do not prove meter truth, budget-head
currentness, vector arithmetic, or database transaction atomicity.
