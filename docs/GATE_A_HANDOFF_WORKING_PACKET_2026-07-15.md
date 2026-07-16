# Odeya Gate A — Working Handoff Packet

Status: handoff-ready scoped architecture checkpoint, not a frozen Gate A candidate, acceptance record, or implementation authorization. Last materially updated 2026-07-16, Asia/Jerusalem.

This packet lets a later Codex, Claude, or human reviewer recover the mission, current evidence, restart sequence, and known remaining work without guessing. Passing architecture checks does not remove the blockers recorded here, and later review can add findings.

## Mission and hard boundary

The mission is to close Odeya’s pre-implementation Gate A architecture into an immutable, independently reviewable candidate that absorbs the requirements learned from Sentinel, Telos, and Inbar and defines the scientific, mathematical, physical, cognitive, command/event, authority, evidence, verification, resource, recovery, publication, projection, and evaluation contracts.

The current checkpoint expressly does **not** authorize:

- runtime or product implementation;
- production UI implementation;
- deployment, DNS, providers, models, MCP, laboratories, external effects, data import, or publication;
- an admitted command/event set, active registry, engine root, checkpoint, or activation;
- treating synthetic fixtures as real scientific, reviewer, provider, or world evidence;
- investor outreach or public repository changes; or
- claiming Gate A acceptance before accountable review and Daniel’s exact-byte decision.

Daniel owns the UI/UX lane. Preserve concurrent work, especially:

- `docs/UI_UX_MOTHERSHIP_CANDIDATE.md`;
- `docs/design/`;
- `docs/UI_UX.md`;
- `docs/IMPLEMENTATION_ORDER.md`;
- `docs/decisions/0008-dual-surface-projection-boundaries.md`; and
- any corresponding index change in `docs/decisions/README.md`.

These paths are not part of the scoped architecture checkpoint merely because they appear in `git status`.

The final read-only integration audit found one known UI-lane drift that must
remain visible without crossing ownership boundaries: the untracked UI
mothership/fixture/handoff drafts still describe
`release_decision_payload.publication_grant_ref` as a current contradiction,
but `ResearchEvent` 0.7.0 removed that field when the publication cycle was
corrected. Those UI files were not edited or staged here; their owner must
reconcile the wording before a later UI checkpoint.

## Repository identity

- Workspace: `/Users/danielwahnich/workspace/odeya`
- Branch: `main`
- Source architecture checkpoint: `f4429ce5ca71e58ebb5d65776a45ebb6a2a18889`
- Source architecture tree: `029b5161f883de41e93565b29ba895ee492a7d47`
- Foundational local architecture checkpoint: `63212488b919b7d8fedce83bc3be344064d7cfe6`
- Foundational checkpoint tree: `979f5c46ec098fdb2e7598c6dc428ce45288788e`
- Current prerequisite-closure architecture checkpoint: `f8644edcd0a0217b2487f5e5ff218bd65dbe3bda`
- Current prerequisite-closure tree: `d6fce27d464bc16cfaeda7a4e194e8ef75aa4730`
- Remote: none at handoff anchoring time
- Pinned architecture environment: `/Users/danielwahnich/workspace/odeya/.venv-architecture`
- Product/runtime implementation lock: intact

The prerequisite-closure tranche is based on the exact source checkpoint above and remains a working-tree candidate until its architecture-only index is exported, replayed, and committed. The remaining UI/UX paths are Daniel's intentional concurrent lane and are not disposable. Never use destructive reset/checkout operations or indiscriminate staging.

## Proof-mission facts that must survive every handoff

### Sentinel

- proof revision `542b432...`;
- 799/800 accepted cases;
- score 2.12 to 2.91, delta +0.783 with interval [+0.605, +0.928];
- safe-progress delta -0.032 with interval [-0.127, +0.065]; and
- the HUGSIM transfer result is `inconclusive` because its interval crosses zero. It is not an affirmative null, equivalence, benefit, harm, or proof of no effect.

### Telos

- proof revision `fc955a...`;
- corrected 40-row framing plus later 22-case evidence;
- iterations 197 and 201 are invalid;
- the iteration-192 explicit-input core reproduces 40/40; and
- repository-wide scanning self-contaminates after correction, while the terminal pass is not replay-complete.

Odeya therefore requires frozen input scope, correction supersession, contamination accounting, retained invalid attempts, discrepancy retention, and exact clean replay before a terminal claim.

### Inbar

- proof revision `b3cd...`;
- 16 sources, 0/30 dossiers, and 1/6 hardware identities; and
- current evidence supports a blocker/refusal, not a physical diagnosis, experiment result, causal claim, or action.

Unknown hardware, absent evidence, unavailable raw bytes, missing rights, and unsafe-to-infer states must never become zero, success, or narrative confidence.

Maestro remains a technical reference for agentic technique only. Its runtime-discipline failures are requirements sources, not Odeya authority.

## Candidate architectural decisions

1. The deterministic kernel owns admission, authority, state, resources, effects, recovery, and publication legality. Models produce proposals and artifacts only.
2. One mission/protocol branch has at most one canonical `epistemic_graph` aggregate. Views, plans, work/model/routing records, transitions, and verification packages are derived/control/artifact lanes unless an admitted contract says otherwise.
3. Command ingress is admitted-only. Unknown, reserved, inactive, or unresolvable selectors fail before a canonical envelope/receipt; exact historical retry resolves retained semantics.
4. Caller-supplied authority is untrusted resolution input. The kernel and active registry select authority mode, policy, and consumption point.
5. Registry digest dependencies are one-way: `schema -> state -> reducer -> event -> command`. Reverse semantic edges resolve exact type/version members inside one root and never create content-hash fixed points.
6. Pure registry snapshots precede one `EngineContractRoot`; a C0 bundle binds the same component set; checkpoint and activation are later, separate subjects.
7. Publication requires confirmed external application and exact-visible observation. Either arrival order is retained; contradiction creates a dispute overlay, never silent release.
8. A resource claim holds committed/in-flight capacity, not actual usage. Crash, expiry, or recovery cannot release a claimed ceiling; unknown settlement remains held.
9. Verification is one immutable terminal package over an exact assignment and actual execution identity. Same-team integrity, independent scientific replication, and physical verification are distinct profiles.
10. Model-configuration observations and routing decisions are non-authoritative evidence. Routing never authorizes dispatch, spend, data exposure, scientific admission, or verifier independence.
11. Private, thesis, public, and static surfaces are derived projections. No projection is canonical truth, evidence, authority, or a publication decision.
12. Physical simulation, calibration, code verification, and physical-world validation remain separate evidence origins.

## Exact working evidence at this checkpoint

### Foundation and ownership

- Full validator: **pass**.
- 100 JSON schemas.
- 588 shared valid/adversarial cases.
- 7 founding cross-field fixture groups.
- 8 mandatory isolated contract-family suites.
- 2 bounded architecture-evidence checks for Gate-prerequisite consistency and schema-resource reissue lineage.
- Logical manifest v2: 9 layers, 30 modules, 47 aggregates, 100 schemas, 121 command owners, and 135 event owners.
- Module manifest digest: `sha256:04fb8f17c0775b20dac3c328ca1c3831483a25581be38cc5f521e8898ac52b96`.

The 121/135 figures are design-vocabulary and ownership counts, not admitted contracts.

### Command, event, registry, and verification

- `research-event` 0.7.0: 135 closed discriminators.
- 62 direct event fixtures and 16 adverse/recovery trace fixtures.
- 186 shared-manifest cases directly target `ResearchEvent` or `ResearchEventTrace`.
- Non-executable command design vocabulary: 121/121 members are `not_contract_admitted`.
- Historical command-envelope 0.4.0 vocabulary source identity: `sha256:ad8b96a589051624dfc59d4a429a6529e3b91f7e18a9005cc615b9fa73dbbc30`.
- `CommandEnvelope` 0.5.0 / `CommandReceipt` 0.4.0 are nonconstructible structural candidates; `CommandContractRecord` 0.1.0 and `CommandContractRegistry` 0.2.0 keep exact identity resolution blocked and confer no dispatch or settlement authority.
- Command cross-object identity: 19 typed non-admission cases pass. The checker deliberately does not claim complete dialect/blob equality, reference-version/digest-to-resolved-subject equality, actor/target projection, digest recomputation, cryptographic membership, activation, or EngineContractRoot proof; PRQ-012 remains open pending the complete corpus and a second independent implementation.
- Schema-resource lineage: 7 existing resources reissued, 2 new candidates inventoried, and 8 false-lineage mutations rejected; predecessor retention remains Git-object-only and blocking.
- Offline resolution/transitive migration remains incomplete: the current schema set references absent `canonical-work-lease:0.1.0`, historical `command-contract-registry:0.1.0`, historical `command-receipt:0.3.0`, historical `work-contract:0.1.0`, and the deliberately retained exact `command-envelope:0.4.0` vocabulary source. None may be aliased to a newer resource ID.
- Several retained structural fixtures still bind those historical IDs, including research-state/root/C0/activation, event-trace, candidate-artifact, and external-effect fixtures. The three “safe” constitutional-construction references prove only the prospective replacement shape; they are not a current digest-coherent root/checkpoint/P0/activation chain.
- Vocabulary scoped digest: `sha256:a480f0b28bb9a8106560f2cdb474e484f6cf2cda0104d4f81e3e7392af5d93e6`.
- Registry/root lane: 6/6 structural schema subjects and fixtures pass.
- Verification lane: eight terminal package fixtures, four verification-event fixtures, and 49 scoped shared-manifest cases.

No real registry member, root, checkpoint, activation, reducer, handler, or verifier execution is claimed.

### Cognitive, projection, physical, and mathematical contracts

- Cognitive: 150 cases pass; 18 have bounded local semantic checks.
- First-slice resolution: 12/12 safe references accepted and 21/21 known-bad cases rejected; the prospective C5 assignment reference specifies future obligations and does not claim current constructibility.
- Projection: 62 pass; 37 structural rejects and 25 bounded semantic vectors cover all 25 named adversarial vectors.
- Physical: 85 structural expectations and 32 bounded semantic expectations pass over an 8-schema DAG and 8 pinned fixtures.
- Mathematical: 57 pass; 38 structurally valid, 19 structurally invalid, and 38 bounded semantic checks.

Sentinel’s interval [-0.127, +0.065] is retained as `inconclusive` and rejected as directional support, effect absence, equivalence, or an affirmative null without the required prospective margin/design.

### First-slice resolution boundary

The foundational checkpoint retained a deliberately non-freezable 44/77/52/23 hypothesis.
The reissued 0.2 [First-Slice Admission Resolution Candidate](FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md), [ADR 0014](decisions/0014-resolve-first-slice-atomic-admission.md), and [machine inventory](../architecture/first-slice-admission-resolution-candidate.json) retain one exact representational scope while reopening C5/PRQ-009 as blocking:

- 43 required and 78 outside command names;
- 60 exact required event discriminators;
- 25 aggregate/state/reducer families across 11 owner modules; and
- one `P0.constitutional-recovery-admission` prerequisite that must be admitted separately.

Bounded decisions are one typed ResourceLedger path; atomic claim-correction and
run/measurement cohorts; nonrecursive authority with ordered action-instance
single-use grant slots; a prospective specialized local verification assignment plus
attempt start/report path; one canonical Verification reducer; and an embedded
P0 binding root/C0, witnessed checkpoint, and clear recovery/fork/quarantine
frontier.

These are exact representational sets, not admission. C5 has no constructible
resolved WorkIntent or complete exact 13-event assignment binding and therefore
remains blocked. The current additional construction
gaps are 42 payload schemas, 43 CommandContractRecords, 60 EventContractRecords,
25 state-subject records, 25 reducer records, and a real witnessed
root/checkpoint/P0/activation instance chain. A fixed-profile bounded composite
authority/resource/race model now passes; executable refinement, full bounded
replay, independent reducers, review, and operator acceptance remain absent.

### Canonical identity and migration audit

- Two pinned implementations agree on 64 vectors: 19 accepted, 45 refused, 0 errors.
- 4 metamorphic relations pass.
- Source-lock SHA-256: `9e203d9a5c96987aa3125e9d950509e663a8892227f491797549db3b6e8f55bb`.
- Audit-generator SHA-256: `0e0e93077756fe38de1e1b339af356cd0d8b7d273f315c3736c3d6a1dd6a7bcd`.
- `SCHEMA_AUDIT.json` SHA-256: `b1c201e31b87ea1af5b52fe88dd85b6b98fc190710b66d37012beb4bfbde6c6b`.
- The current audit covers all 100 schemas and 198 fixtures across architecture, review, cognitive, projection, physical, and mathematical roots.
- Disposition remains `blocked`: 122 unprofiled date-time paths, 61 number/decimal findings, 668 unscoped digest fields, 56 divergent common-definition names, 11 unpinned profile bindings, and 238 nonconformant fixture timestamps.

Cross-runtime vector agreement does not erase the migration blockers.

### Bounded formal evidence

- 7/7 distinct safe models.
- 8/8 safe executions, including one alternate CognitiveControl seed/fingerprint execution.
- 30/30 intended counterexamples.
- Seven primary models: 13,157,883 generated / 1,799,234 distinct states.
- All eight safe executions: 25,115,228 generated / 3,368,386 distinct states.
- Negatives: 966,317 generated / 200,221 distinct states.
- Retained integrated observation: first TLC start through final TLC completion was 112 whole seconds; pre-run SANY time and CPU totals were not retained at subsecond precision.
- Results-manifest SHA-256: `65981097cdb32847cf19eee16e393d1d2504b5dd6f3aaf143417a1adb2b5553d`.
- Harness SHA-256: `e2f6f752d77c61e4dbae1e2c11eacd3902b6a30a8530e72987381dd95c608bce`.
- ResourceReservation source SHA-256: `84e3b8be45c144d44fb68b14c79d88ec1b0e82d96914b0ec7073d844a5f0b324`.
- CompositeAuthorityResource source SHA-256: `028e29374e8cd5930c2fd0452c1962015ab1265cf4a616a76b09749d6e8910c5`.

The primary cognitive run’s reported collision estimate is `3.5e-7`; the alternate seed `20260716` / polynomial `1` run reports `5.7e-8`. They traverse the same bounded model with the same checker and host lineage. The estimates are disclosed, never multiplied, and the second run is not represented as an independent model or proof.

All fixtures and models are synthetic structural or bounded evidence. None proves a real mission, provider, reviewer, world result, external effect, or deployment.

## Required restart sequence

Run from `/Users/danielwahnich/workspace/odeya`:

```bash
git status --short --branch
git diff --check
.venv-architecture/bin/python tests/cognitive-contracts/check.py
.venv-architecture/bin/python tests/projection-contracts/check.py
.venv-architecture/bin/python tests/physical-contracts/check.py
.venv-architecture/bin/python tests/mathematical-contracts/check.py
.venv-architecture/bin/python tests/lifecycle-closure/check.py
.venv-architecture/bin/python tests/constitutional-construction/check.py
.venv-architecture/bin/python tests/command-identity-contracts/check.py
.venv-architecture/bin/python tests/canonicalization/audit_schemas.py --check
.venv-architecture/bin/python tests/canonicalization/compare_results.py
.venv-architecture/bin/python scripts/validate_schema_resource_reissues.py
.venv-architecture/bin/python scripts/validate_gate_a_prerequisites.py
.venv-architecture/bin/python scripts/validate_module_manifest.py
.venv-architecture/bin/python scripts/validate_first_slice_resolution.py
.venv-architecture/bin/python scripts/validate.py
bash formal/tla/check.sh
```

Before interpreting a failure, inspect whether any owner is actively editing the affected schema, fixture, manifest, audit, or result evidence. Never hide a failure by deleting a known-bad case or weakening a closed contract.

## Checkpoint and freeze discipline

1. Confirm every parallel lane is quiescent and record its exact file scope.
2. Inspect the complete diff, especially shared manifests, generated identities, and UI-owned paths.
3. Rerun all isolated suites, schema meta-validation, canonical evidence, module validation, the full validator, formal suite, link checks, and `git diff --check`.
4. Stage only reviewed architecture files. Keep UI/UX-owned paths outside the scoped checkpoint.
5. Export the staged index to a temporary directory and validate that tree so untracked UI files cannot mask a broken checkpoint.
6. Create one scoped local architecture checkpoint commit; do not push.
7. Record the resulting commit ID in a follow-up handoff-only record or the final handoff message. The scoped architecture commit cannot contain its own hash without recursion.
8. Continue from the checkpoint toward first-slice records, independent reducers/replays, reviews, and a later exact candidate.

## Remaining Gate A blockers

- the exact first-slice member construction gaps and composite C1-C8 replay/refinement/review evidence;
- no real immutable registry/root/C0/checkpoint/activation subjects;
- no independently authored dual reducers or composite replay/recovery/fanout package;
- no per-artifact rights settlement or sealed proof-mission import root;
- canonicalization migration blockers remain explicit;
- no accountable statistical, physical/metrology/VVUQ/safety, security/privacy, distributed-systems, or accessibility review;
- no exact first deployment/key/witness/storage/recovery profile;
- no demonstrated real scientific, external-effect, publication, or projection-settlement execution; and
- no Daniel accept/reject/amend decision over exact candidate bytes.

## Next safe work order

1. Preserve the exact 43/78/60/25/11/P0 construction boundary; any proposed scope change restarts the dependency audit.
2. Build the 42 payload schemas, 25 state subjects, 25 reducer records, 60 event records, and 43 command records in dependency order.
3. Construct and review exact registry/root/C0/checkpoint/witness/P0/activation subjects; prove member/handler equality.
4. Implement two independent architecture-time reducers and two clean scientific verifier paths over the composite fixture.
5. Run replay, recovery, correction fanout, resource/authority races, and all proof-mission refusal vectors.
6. Close canonical migration blockers and obtain accountable independent reviews.
7. Produce one immutable candidate manifest/commit for Daniel’s exact-byte decision.

## Handoff fields

- Frozen Gate A candidate manifest: **not created**
- Foundational architecture checkpoint: **`63212488b919b7d8fedce83bc3be344064d7cfe6`**
- Source architecture checkpoint/tree: **`f4429ce5ca71e58ebb5d65776a45ebb6a2a18889` / `029b5161f883de41e93565b29ba895ee492a7d47`**
- Current prerequisite-closure checkpoint/tree: **`f8644edcd0a0217b2487f5e5ff218bd65dbe3bda` / `d6fce27d464bc16cfaeda7a4e194e8ef75aa4730`**
- Full validator: **pass — 100 schemas, 588 shared cases, 7 founding semantic groups, 8 isolated suites, 2 architecture-evidence checks, 64 canonical cases, 4 metamorphic relations, 100-schema/198-fixture audit, 30 modules, 47 aggregates, 121 design commands, 135 events**
- Cognitive: **150 pass / 18 bounded semantic**
- Command identity: **19 typed non-admission cases; PRQ-012 remains open**
- Lifecycle closure: **60 event identities / 25 families; 11 safe / 21 adversarial traces**
- Constitutional construction: **3 safe structural references / 29 intended refusals**
- First-slice adversarial: **12/12 safe references / 21/21 intended refusals**
- Schema-resource lineage: **7 reissues / 2 new candidates / 8 intended false claims rejected; offline retention remains blocked**
- Projection: **62 pass / 25 bounded semantic vectors**
- Physical: **85 structural / 32 bounded semantic**
- Mathematical: **57 pass / 38 bounded semantic**
- Formal: **7/7 distinct models, 8/8 safe executions, 30/30 intended negatives**
- Canonical source lock: **`9e203d9a5c96987aa3125e9d950509e663a8892227f491797549db3b6e8f55bb`**
- Canonical audit: **current and blocked; `b1c201e31b87ea1af5b52fe88dd85b6b98fc190710b66d37012beb4bfbde6c6b`**
- Module manifest: **v2 pass; `sha256:04fb8f17c0775b20dac3c328ca1c3831483a25581be38cc5f521e8898ac52b96`; v1 predecessor replayed from exact Git bytes**
- Preserved UI/UX paths: **listed above; verify after staging**
- Independent review determinations: **pending**
- Daniel’s exact-byte decision: **not requested; pending**

This packet is a recovery aid for a revalidated scoped checkpoint. It must not be treated as self-proving, complete against future review, or represented as an immutable Gate A candidate while any blocker above remains.
