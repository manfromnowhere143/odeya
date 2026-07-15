# Architecture Candidate Status

Status timestamp: 2026-07-15. This is an honest readiness ledger, not a marketing score. The foundation is substantial; Gate A is not accepted and product implementation remains prohibited.

## Locked operator constraints

These constraints come directly from the current operator direction and are not product assumptions:

- the name is **Odeya**;
- Odeya is an independent private engine and company, not an Aweb or Maestro feature;
- Sentinel, Telos, and Inbar are proof missions and requirements sources, not repositories to merge;
- the working web address is `odeya.danielwahnich.dev`; domain acquisition is outside the engine critical path;
- the engine is designed before runtime, deployment, integrations, or production UI implementation;
- Daniel owns the visual/product design; engine documents define truthful state and accessibility contracts only;
- open research is selectively released from a private engine through explicit evidence, rights, safety, and publication authority.

## Candidate architecture verdict

The proposed core is a dual-loop research system:

1. a deterministic scientific kernel owns canonical state, protocol exposure, authority, resource commitments, evidence custody, verification requirements, and claim eligibility;
2. a replaceable epistemic model fabric proposes hypotheses, plans, experiments, code, analyses, critiques, and graph deltas through typed contracts;
3. independent verification and a pure adjudicator stand between generated work and an eligible claim;
4. release is a separate externally settled aggregate; no model or UI can publish by implication.

This verdict is the leading candidate because it matches the strongest current evidence while refusing unsupported assumptions about general autonomous science. It has not yet earned operator acceptance or empirical superiority.

## Readiness by Gate A area

| Gate | Draft evidence present | Current state | What still blocks acceptance |
|---|---|---|---|
| G0 mission/boundary | Charter, proof snapshot, non-goals, thesis intake | Partial | First wedge and exact pinned vertical-slice fixture not selected; company/user language needs operator sign-off |
| G1 scientific/mathematical | Mathematical, physical-science, and semantic-validation constitutions | Partial | Method/rule registry schemas and traces; domain expert review; first adapter profile; independent critical-rule implementation |
| G2 domain/lifecycle | Mission, claim proposal/version, adjudication, verification, blocker, grant, publication schemas; state model | Blocked | Event/command family incomplete; protocol/run/artifact/metric/falsifier/correction/handoff/learning objects not frozen; cross-schema semantic registry absent |
| G3 security/authority | Security architecture, threat model, authority matrix, grant schema, risk tiers | Partial | Operator acceptance of root/action/quorum contracts; data lifecycle; key/witness design; semantic race fixtures; independent security review |
| G4 evidence/memory | Evidence graph, canonical/derived split, provenance standards | Partial | Frozen canonicalization profile/vectors; PROV/RO-Crate mapping; checkpoint witness; deletion/legal-hold semantics |
| G5 evaluation/learning | Evaluation stack, ablations, improvement quarantine | Partial | Pinned task/holdout/known-bad suite; grader validation; matched-budget oracle; contamination process |
| G6 modules/interfaces | Modular-monolith boundary, ports, command catalog | Partial | Complete command/event schemas and reducer laws; module dependency manifest; product exit decisions |
| G7 reliability/operations | Transaction model, failure model, crash matrix | Partial | Isolation/lock order; RPO/RTO; restore/witness profile; semantic model checks; authorized product probes later |
| G8 UI/publication projections | Engine-facing UI truth/accessibility contract; publication manifest | Partial | Daniel’s accepted information architecture; projection schemas; state fixtures; release-channel contract |
| G9 implementation order | Dependency-ordered increments and rollback | Partial | Exact first fixture; platform/toolchain decision evidence; per-increment machine-readable test manifest |
| G10 red team | Frontier review, schema adversary, transaction/command audits | In progress | Close all critical/high findings, independent statistical/security/domain review, exact candidate manifest, operator signature |

No row is “passed.” Documents demonstrate design work, not implementation conformance.

## Critical architecture blockers

| ID | Severity | Blocker | Required closure evidence |
|---|---|---|---|
| A-001 | Critical | Current `research-event` is an adversarial prototype with missing aggregate owners and lifecycle facts | Complete event vocabulary, typed payloads, one producer/reducer per event, replay traces, compatibility rule |
| A-002 | Critical | Command receipts and command schemas are not frozen | Immutable receipt contract binding ID, actor, target, schema, request digest, outcome, event batch, and replay result |
| A-003 | Critical | Authority bootstrap, plurality, grant-use/reservation, expiry, quorum, and overlap semantics are specified but unaccepted and lack semantic/race evidence | Accept `AUTHORITY_MATRIX.md`, then add semantic validator, bounded race model, and known-bad traces |
| A-004 | Critical | Scientific validity and measurement facts are not yet complete canonical event axes | Run/measurement schemas and events proving `no_valid_measurement` cannot compile into `null_result` |
| A-005 | Critical | Publication request/decision/seal/effect/settlement contracts are not a replay-complete chain | Noncircular manifest/grant sequence, channel effect identities, ambiguity/reconciliation traces, correction/withdrawal fanout |
| A-006 | High | Schema family is incomplete | Protocol snapshot/amendment, run manifest, artifact, metric/falsifier result, correction, handoff, grounded outcome, strategy objects |
| A-007 | High | Cross-object semantic rules are specified but the rule/result schemas, registry, independent implementations, and adversarial traces do not yet exist | Freeze `SEMANTIC_VALIDATION.md` contracts and execute its acceptance rule |
| A-008 | High | Canonical JSON, timestamps, decimal/quantity semantics, and digest namespace are not frozen across runtimes | Official profile snapshot and two independent conformance implementations/vectors before product commitment |
| A-009 | High | First vertical slice and settled proof snapshot are not selected | Rights-cleared immutable fixture with positive, null, invalid/broken, correction, cost, and expected-verdict artifacts |
| A-010 | High | Threat assumptions have not received independent review | Closed security review over trust zones, abuse cases, isolation claims, data lifecycle, root recovery, and external effects |
| A-011 | High | Mathematical/physical constitutions have not received relevant expert review | Named statistical/domain review, accepted limitations, method-admission rules, and simulation/known-effect vectors |
| A-012 | High | Ledger witness, backup/restore, key hierarchy, retention/deletion, and recovery objectives remain deployment decisions | Accepted deployment-neutral contracts plus exact first-profile decision records |
| A-013 | Medium | Product candidates are not proven | Gate A port contracts, then explicitly authorized disposable Gate B probes; no product choice promoted by reputation |
| A-014 | Medium | UI projections and state language are not accepted | Daniel-approved surface contract plus non-executable fixtures for all truth/unknown/correction/authority states |
| A-015 | Critical | Exact architecture candidate has not been independently reviewed and signed | Clean commit/manifest, closed findings, independent review records, and explicit operator acceptance |

The detailed event/command defects are enumerated in [the command and event catalog](COMMAND_EVENT_CATALOG.md). The cross-plane crash obligations are in [the transaction model](TRANSACTION_MODEL.md).

## Schema maturity

| Schema | Current role | Maturity |
|---|---|---|
| `research-mission` 0.2.0 | Pre-execution mission contract | Candidate; structural fixture only |
| `claim-proposal` 0.1.0 | Immutable prospective proposition | Candidate |
| `adjudication` 0.1.0 | Determination/refusal under frozen rule | Candidate |
| `claim-version` 0.3.0 | Immutable eligible/ineligible semantic version | Candidate |
| `verification-run` 0.1.0 | Observed multidimensional independence and verification dimensions | Candidate |
| `authority-grant` 0.1.0 | Bounded permission artifact | Candidate; semantic authority rules incomplete |
| `blocker` 0.1.0 | Operational blocker distinct from science | Candidate |
| `publication-manifest` 0.1.0 | Sealed exact disclosure package | Candidate; release chain incomplete |
| `research-event` 0.2.0 | Event-envelope prototype | Red-team target; explicitly not frozen |

Schema validation demonstrates only structural compatibility. It does not prove state legality, scientific validity, authority, independence, rights, or release settlement.

## What is deliberately not started

- no engine runtime or application modules;
- no production UI implementation;
- no database, workflow, object-store, policy, or sandbox provisioning;
- no provider, model, MCP, lab, repository, or publication integration;
- no DNS, domain, company, public-repository, or external-release action;
- no migration or import from active Sentinel, Telos, Inbar, Maestro, or Aweb state;
- no model training, fine-tuning, recursive self-modification, or physical authority.

Architecture validators and adversarial fixtures are allowed because they test the design artifacts and cannot perform research or external effects.

## Freeze path

1. Close A-001 through A-008 at the contract and adversarial-fixture level.
2. Select A-009 and use it to challenge every mathematical, physical, authority, recovery, and UI boundary.
3. Obtain independent reviews for A-010 and A-011.
4. Freeze deployment-neutral recovery/data/key contracts, then classify remaining product questions as authorized probes or reversible increment choices.
5. Produce an exact candidate commit and digest manifest; rerun structural, semantic, link, contradiction, and trace checks.
6. Close every critical/high finding on that commit.
7. Ask the operator to accept, reject, or amend the candidate. Acceptance still does not authorize product code.
8. Only after any authorized probes are integrated may the operator authorize one bounded implementation increment under Gate C.

This sequence is the operational meaning of “architecture first.” It protects the ambition by refusing to confuse a beautiful design document with a proven research engine.
