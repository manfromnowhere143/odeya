# Retained TLC result summary

Integrated suite run recorded: 2026-07-16. Toolchain, source hashes, exact command profile, and machine-readable counts are in [results-manifest.json](results-manifest.json).

The post-integration sequential harness completed SANY, seven distinct safe graphs, one supplemental CognitiveControl execution under a second fingerprint profile, and thirty expected counterexamples with exit code `0` on the retained host. The first TLC run started at `2026-07-16T00:08:01Z` and the last ended at `2026-07-16T00:09:53Z`; this whole-second 112-second observation excludes pre-run SANY time and is not a performance guarantee.

## Safe configurations

| Model | Invariants | Generated / distinct states | Depth | Result |
|---|---:|---:|---:|---|
| Authority and command/grant | 6 | 1,142,209 / 215,360 | 21 | Complete bounded graph; no error |
| Grant consumption point | 6 | 519 / 224 | 10 | Complete bounded graph; no error |
| External effects | 7 | 25,146 / 7,150 | 20 | Complete bounded graph; no error |
| Publication release | 9 | 2,884 / 924 | 19 | Complete bounded graph; no error |
| Cognitive control (primary fingerprint profile) | 14 | 11,957,345 / 1,569,152 | 22 | Complete bounded graph; no error |
| Resource reservation | 6 | 16 / 13 | 7 | Complete bounded graph; no error |
| Composite authority/resource race | 14 | 29,764 / 6,411 | 11 | Complete bounded graph; no error |

TLC reported zero states left on every safe execution. Across the seven distinct primary safe graphs it generated 13,157,883 states and found 1,799,234 distinct states. Those are arithmetic workload sums across separate complete graphs within one integrated sequential harness invocation, not one combined state space.

The cognitive-control run remains the largest. Under seed `20260715` and fingerprint polynomial `0`, TLC reported optimistic fingerprint-collision probability `8.8e-7` and actual-fingerprint estimate `3.5e-7`. The retained supplemental execution used seed `20260716` and polynomial `1`, traversed the same 11,957,345 generated / 1,569,152 distinct states to depth 22 with zero left, and reported the same optimistic estimate plus actual-fingerprint estimate `5.7e-8`. This is a robustness check against one fingerprint profile, not an independent model, checker, implementation, or proof; the two collision estimates are not multiplied. Including the supplemental execution, the eight safe executions generated 25,115,228 states and found 3,368,386 distinct states as arithmetic workload sums.

The authority run reported actual fingerprint-collision estimate `7.9e-10`, and the smaller runs reported optimistic estimates from `7.0e-12` through `3.6e-15`. These nonzero estimates are disclosed rather than described as mathematical certainty.

The expanded cognitive graph uses the exact five founding verification-capacity dimensions—`deterministic`, `compute`, `expert`, `physical`, and `safety`—and models data access as a separate admission gate. It also explores an acyclic View→Receipt→Bundle issuance chain, pass/fail/not-run compilation, bundle identity matching, stale position/authority, and dispatch admission. The publication graph permits exact visibility to arrive before or after application confirmation and forces contradictory exact-visible/confirmed-not-applied facts into a monotonic required-dispute axis with settlement left unknown.

## Counterexample controls

| Deliberate defect | Violated invariant | Shortest retained action sequence | Trace depth | Expected result |
|---|---|---|---:|---|
| Count two aliases as quorum | `EveryUseWasAuthorized` | issue, activate, approve A, approve alias-A, reserve, use | 7 | TLC exit 12 |
| Rebind accepted command ID to new digest | `IdempotentCommandBinding` | issue, activate, approve A+B, reserve, use, fault rebind | 8 | TLC exit 12 |
| Consume after revocation | `EveryUseWasAuthorized` | issue, activate, approve A+B, reserve, revoke, fault use | 8 | TLC exit 12 |
| Consume effect grant at T1 and dispatch without recheck | `DispatchClaimRechecksAndConsumes` | faulty reserve-and-consume intent, faulty dispatch | 3 | TLC exit 12 |
| Dispatch after revocation/expiry | `NoDispatchAfterRevocationOrExpiry` | authorize intent, revoke, faulty dispatch | 4 | TLC exit 12 |
| Blind retry from unknown unsafe effect | `NoUnsafeRetry` | authorize, dispatch, timeout, faulty retry | 5 | TLC exit 12 |
| Seal without human authorization | `ManifestWasSealedFromAuthorizedCandidate` | compile candidate, faulty seal | 3 | TLC exit 12 |
| Issue grant for different final manifest | `GrantBindsExactFinalManifest` | compile, request, authorize, seal A, issue for B | 6 | TLC exit 12 |
| Reuse single-use publication grant | `PublicationGrantIsSingleUse` | compile through effect intent, dispatch claim, faulty reuse | 9 | TLC exit 12 |
| Mark timeout as released | `ReleasedRequiresExactExternalObservation` | compile through dispatch, timeout, faulty settlement | 10 | TLC exit 12 |
| Mark visibility-only observation as released | `ReleasedRequiresExactExternalObservation` | compile through dispatch, observe exact visibility first, faulty settlement | 10 | TLC exit 12 |
| Suppress dispute after exact-visible/confirmed-not-applied contradiction | `ContradictoryExternalFactsRequireDispute` | compile through dispatch, observe exact visibility, report definitely not applied without dispute | 10 | TLC exit 12 |
| Reveal sealed truth to producer | `SealedTruthHiddenFromProducer` | faulty producer reveal | 2 | TLC exit 12 |
| Promote while material counterevidence is pending | `PromotionRequiresMaterialDisposition` | disposition primary, qualify primary, faulty promotion | 4 | TLC exit 12 |
| Treat model consensus as qualifying evidence | `ConsensusIsNotEvidence` | faulty consensus recording | 2 | TLC exit 12 |
| Start verification before reserving every capacity dimension | `VerificationDemandWithinReservation` | admit data access, faulty verification start | 3 | TLC exit 12 |
| Admit a stale bundle without current-position/authority recheck | `DispatchAdmissionUsesCurrentPositionAndAuthority` | compile/pass/bundle, admit data, advance position, faulty dispatch admission | 8 | TLC exit 12 |
| Dispatch from failed compilation | `DispatchAdmissionBindsPassedIssuedBundle` | compile view, issue identity, record failed receipt, faulty admission | 5 | TLC exit 12 |
| Dispatch from not-run compilation | `DispatchAdmissionBindsPassedIssuedBundle` | compile view, issue identity, record not-run receipt, faulty admission | 5 | TLC exit 12 |
| Dispatch from mismatched bundle | `DispatchAdmissionBindsPassedIssuedBundle` | compile/pass, issue mismatched bundle, faulty admission | 6 | TLC exit 12 |
| Dispatch without issued bundle | `DispatchAdmissionBindsPassedIssuedBundle` | compile/pass, faulty admission before bundle issuance | 5 | TLC exit 12 |
| Treat data access as bypassable capacity | `VerificationRequiresDataAccess` | reserve all five dimensions, faulty verification start without data admission | 7 | TLC exit 12 |
| Compensate an overdrawn execution dimension with spare money/verification | `NoDimensionOvercommit` | faulty reserve with execution demand above its own capacity | 2 | TLC exit 12 |
| Release a claimed ceiling merely because the worker crashed | `TerminalReleaseWasPreClaim` | reserve, claim, faulty crash release | 4 | TLC exit 12 |
| Settle an unknown claimed reservation without usage evidence | `SettlementRequiresObservation` | reserve, claim, faulty settlement | 4 | TLC exit 12 |
| Treat claim commitment as observed actual use | `ClaimDoesNotInventActualUse` | reserve, faulty claim-and-infer | 3 | TLC exit 12 |
| Accept assignment with one required role-grant slot missing | `AcceptedCohortConsumesAndExhaustsExactlyAllSlots` | faulty partial assignment cohort | 2 | TLC exit 12 |
| Release the combined reservation after `attempt.start` claimed it | `NoReleaseOrExpiryAfterClaim` | assign, start, faulty release | 4 | TLC exit 12 |
| Infer missing non-money actual as zero and settle with other axes absent | `SettlementRequiresExactEvidenceWithoutZeroInference` | assign, start, faulty partial settlement | 4 | TLC exit 12 |
| Let a stale `attempt.start` claim after controlled deadline expiry won | `StartCannotFollowPreclaimTerminal` | assign, advance controlled time, expire, faulty start | 5 | TLC exit 12 |

The controls show that the named invariants are not vacuous: deliberate mutations produce short, reviewable counterexamples at the intended boundary. Across all thirty negative controls TLC generated 966,317 states and found 200,221 distinct states before the expected stops, as arithmetic sums across separate controls in the integrated invocation. Counterexample state dumps can be regenerated exactly with `bash formal/tla/check.sh`; bulky, machine-path-dependent logs are not committed.

## Verdict and limitation

No unexpected safety violation appeared in the seven distinct safe bounded models or the supplemental CognitiveControl fingerprint execution. The earlier grant-reservation/consumption ambiguity remains tracked as [FM-A-001](FINDINGS.md); the consumption-point model passes the leading resolution and rejects the ambiguous prior interpretation. The publication ordering closes the bounded visibility-first exploration gap, the cognitive model rejects failed/not-run compilation and capacity/data-access conflation, and the resource models reject partial role-grant acceptance, cross-dimension compensation, post-claim release, stale start after expiry, evidence-free or partial settlement, and claim-time or absence-derived actual-use inference.

This evidence does not close Gate A by itself. It does not prove liveness, cryptography, canonicalization, database isolation, adapter behavior, storage recovery, physical safety, provider/cache noninterference, evidence truth, compilation correctness, consensus quality, resource-accounting implementation, or conformity of future code. View, Receipt, and Bundle identities are uninterpreted tokens; their acyclic dependency order is modeled, but digest construction and signature validity are not. The composite model has one run, two fixed actions, five fixed role slots per action, one reservation, two abstract non-money axes, one money ceiling, and values in `0..1`; it does not prove variable command profiles, multi-run conservation, real unit semantics, billing/refund arithmetic, or reconciliation liveness. It must be reviewed with the prose contracts, exact schemas/events/registries, semantic traces, and later authorized refinement tests.
