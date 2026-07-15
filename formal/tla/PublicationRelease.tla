---------------------------- MODULE PublicationRelease ----------------------------
EXTENDS Naturals, TLC

(***************************************************************************)
(* Bounded Gate A model of candidate -> human decision -> deterministic     *)
(* manifest -> exact single-use grant -> effect -> observation -> release.  *)
(* Candidate and manifest identities are model values, not mutable bytes.   *)
(***************************************************************************)

CONSTANTS
    CandidateA,
    CandidateB,
    ManifestA,
    ManifestB,
    NoValue,
    ExpiresAt,
    MaxTime,
    FaultSealWithoutDecision,
    FaultWrongManifestGrant,
    FaultReuseGrant,
    FaultReleaseOnTimeout,
    FaultReleaseOnVisibilityOnly,
    FaultSuppressDispute

Candidates == {CandidateA, CandidateB}
Manifests == {ManifestA, ManifestB}

ASSUME /\ CandidateA # CandidateB
       /\ ManifestA # ManifestB
       /\ NoValue \notin Candidates \cup Manifests
       /\ ExpiresAt \in Nat \ {0}
       /\ MaxTime \in Nat
       /\ MaxTime >= ExpiresAt
       /\ FaultSealWithoutDecision \in BOOLEAN
       /\ FaultWrongManifestGrant \in BOOLEAN
       /\ FaultReuseGrant \in BOOLEAN
       /\ FaultReleaseOnTimeout \in BOOLEAN
       /\ FaultReleaseOnVisibilityOnly \in BOOLEAN
       /\ FaultSuppressDispute \in BOOLEAN

ManifestFor(c) == IF c = CandidateA THEN ManifestA ELSE ManifestB

DecisionStates == {"none", "authorized", "denied", "superseded"}
ManifestStates == {"absent", "sealed"}
GrantStates == {"none", "active", "used", "revoked", "expired"}
EffectStates == {"not_intended", "authorized", "started",
                 "completion_unknown", "confirmed_applied",
                 "confirmed_not_applied"}
ReconciliationStates == {"not_required", "pending", "running", "completed"}
VisibilityStates == {"not_observed", "exact_visible", "visible_mismatch",
                     "not_visible", "indeterminate"}
DisputeStates == {"none", "required"}
ReleaseStates == {"not_requested", "requested", "denied", "authorized",
                  "sealed", "releasing", "completion_unknown", "released",
                  "confirmed_not_released", "withdrawn"}

VARIABLES
    now,
    compiledCandidates,
    currentCandidate,
    requestCandidate,
    decision,
    decisionCandidate,
    manifestState,
    sealedManifest,
    sealedCandidate,
    sealHadAuthorizedDecision,
    grantState,
    grantManifest,
    grantUseCount,
    effectState,
    effectManifest,
    reconciliation,
    visibility,
    observedManifest,
    dispute,
    releaseState,
    correctionRequired

vars == << now, compiledCandidates, currentCandidate, requestCandidate,
           decision, decisionCandidate, manifestState, sealedManifest,
           sealedCandidate, sealHadAuthorizedDecision, grantState,
           grantManifest, grantUseCount, effectState, effectManifest,
           reconciliation, visibility, observedManifest, dispute,
           releaseState, correctionRequired >>

Init ==
    /\ now = 0
    /\ compiledCandidates = {}
    /\ currentCandidate = NoValue
    /\ requestCandidate = NoValue
    /\ decision = "none"
    /\ decisionCandidate = NoValue
    /\ manifestState = "absent"
    /\ sealedManifest = NoValue
    /\ sealedCandidate = NoValue
    /\ sealHadAuthorizedDecision = FALSE
    /\ grantState = "none"
    /\ grantManifest = NoValue
    /\ grantUseCount = 0
    /\ effectState = "not_intended"
    /\ effectManifest = NoValue
    /\ reconciliation = "not_required"
    /\ visibility = "not_observed"
    /\ observedManifest = NoValue
    /\ dispute = "none"
    /\ releaseState = "not_requested"
    /\ correctionRequired = FALSE

CompileInitialCandidate(c) ==
    /\ c \in Candidates
    /\ currentCandidate = NoValue
    /\ compiledCandidates' = compiledCandidates \cup {c}
    /\ currentCandidate' = c
    /\ UNCHANGED << now, requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    releaseState, correctionRequired >>

RequestRelease ==
    /\ currentCandidate \in Candidates
    /\ currentCandidate \in compiledCandidates
    /\ releaseState = "not_requested"
    /\ requestCandidate' = currentCandidate
    /\ releaseState' = "requested"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate, decision,
                    decisionCandidate, manifestState, sealedManifest,
                    sealedCandidate, sealHadAuthorizedDecision, grantState,
                    grantManifest, grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

AuthorizeDecision ==
    /\ releaseState = "requested"
    /\ decision = "none"
    /\ requestCandidate = currentCandidate
    /\ decision' = "authorized"
    /\ decisionCandidate' = requestCandidate
    /\ releaseState' = "authorized"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, manifestState, sealedManifest,
                    sealedCandidate, sealHadAuthorizedDecision, grantState,
                    grantManifest, grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

DenyDecision ==
    /\ releaseState = "requested"
    /\ decision = "none"
    /\ decision' = "denied"
    /\ decisionCandidate' = requestCandidate
    /\ releaseState' = "denied"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, manifestState, sealedManifest,
                    sealedCandidate, sealHadAuthorizedDecision, grantState,
                    grantManifest, grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

SealManifest(m) ==
    /\ m \in Manifests
    /\ manifestState = "absent"
    /\ currentCandidate \in Candidates
    /\ m = ManifestFor(currentCandidate)
    /\ ( /\ decision = "authorized"
         /\ decisionCandidate = currentCandidate
         /\ ~correctionRequired
       \/ /\ FaultSealWithoutDecision
          /\ decision # "authorized" )
    /\ manifestState' = "sealed"
    /\ sealedManifest' = m
    /\ sealedCandidate' = currentCandidate
    /\ sealHadAuthorizedDecision' =
          (decision = "authorized" /\ decisionCandidate = currentCandidate)
    /\ releaseState' = "sealed"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate, grantState,
                    grantManifest, grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

IssuePublicationGrant(m) ==
    /\ manifestState = "sealed"
    /\ grantState = "none"
    /\ sealHadAuthorizedDecision
    /\ ~correctionRequired
    /\ now < ExpiresAt
    /\ (m = sealedManifest \/
        (FaultWrongManifestGrant /\ m # sealedManifest))
    /\ grantState' = "active"
    /\ grantManifest' = m
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantUseCount, effectState,
                    effectManifest, reconciliation, visibility,
                    observedManifest, releaseState, correctionRequired >>

RevokeGrant ==
    /\ grantState = "active"
    /\ grantState' = "revoked"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantManifest, grantUseCount,
                    effectState, effectManifest, reconciliation, visibility,
                    observedManifest, releaseState, correctionRequired >>

ObserveGrantExpiry ==
    /\ grantState = "active"
    /\ now >= ExpiresAt
    /\ grantState' = "expired"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantManifest, grantUseCount,
                    effectState, effectManifest, reconciliation, visibility,
                    observedManifest, releaseState, correctionRequired >>

AuthorizeEffect ==
    /\ effectState = "not_intended"
    /\ grantState = "active"
    /\ grantUseCount = 0
    /\ now < ExpiresAt
    /\ ~correctionRequired
    /\ (grantManifest = sealedManifest \/ FaultWrongManifestGrant)
    /\ effectState' = "authorized"
    /\ effectManifest' = grantManifest
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount,
                    reconciliation, visibility, observedManifest,
                    releaseState, correctionRequired >>

FaultReuseSingleUseGrant ==
    /\ FaultReuseGrant
    /\ grantState = "used"
    /\ grantUseCount = 1
    /\ grantUseCount' = 2
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    effectState, effectManifest, reconciliation, visibility,
                    observedManifest, releaseState, correctionRequired >>

StartDispatch ==
    /\ effectState = "authorized"
    /\ grantState = "active"
    /\ grantUseCount = 0
    /\ now < ExpiresAt
    /\ ~correctionRequired
    /\ effectState' = "started"
    /\ grantState' = "used"
    /\ grantUseCount' = 1
    /\ releaseState' = "releasing"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantManifest, effectManifest,
                    reconciliation, visibility,
                    observedManifest, correctionRequired >>

ReportTimeout ==
    /\ effectState = "started"
    /\ effectState' = "completion_unknown"
    /\ reconciliation' = "pending"
    /\ releaseState' = "completion_unknown"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectManifest, visibility,
                    observedManifest, correctionRequired >>

ReportApplied ==
    /\ effectState = "started"
    /\ effectState' = "confirmed_applied"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectManifest, reconciliation, visibility,
                    observedManifest, releaseState, correctionRequired >>

ReportDefinitelyNotApplied ==
    /\ effectState = "started"
    /\ effectState' = "confirmed_not_applied"
    /\ releaseState' =
          IF visibility = "exact_visible"
          THEN "completion_unknown"
          ELSE releaseState
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectManifest, reconciliation, visibility,
                    observedManifest, correctionRequired >>

BeginReconciliation ==
    /\ effectState = "completion_unknown"
    /\ reconciliation = "pending"
    /\ reconciliation' = "running"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest, visibility,
                    observedManifest, releaseState, correctionRequired >>

ReconcileApplied ==
    /\ effectState = "completion_unknown"
    /\ reconciliation = "running"
    /\ effectState' = "confirmed_applied"
    /\ reconciliation' = "completed"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectManifest, visibility,
                    observedManifest, releaseState, correctionRequired >>

ReconcileNotApplied ==
    /\ effectState = "completion_unknown"
    /\ reconciliation = "running"
    /\ effectState' = "confirmed_not_applied"
    /\ reconciliation' = "completed"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectManifest, visibility,
                    observedManifest, releaseState, correctionRequired >>

ObserveExactVisibility ==
    /\ effectState \in {"started", "completion_unknown",
                         "confirmed_applied", "confirmed_not_applied"}
    /\ grantUseCount = 1
    /\ visibility = "not_observed"
    /\ visibility' = "exact_visible"
    /\ observedManifest' = effectManifest
    /\ releaseState' =
          IF effectState = "confirmed_not_applied"
          THEN "completion_unknown"
          ELSE releaseState
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, correctionRequired >>

ObserveMismatch ==
    /\ effectState \in {"started", "completion_unknown",
                         "confirmed_applied", "confirmed_not_applied"}
    /\ grantUseCount = 1
    /\ visibility = "not_observed"
    /\ visibility' = "visible_mismatch"
    /\ observedManifest' =
          IF effectManifest = ManifestA THEN ManifestB ELSE ManifestA
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, releaseState, correctionRequired >>

SettleReleased ==
    /\ ( /\ effectState = "confirmed_applied"
         /\ visibility = "exact_visible"
         /\ observedManifest = effectManifest
         /\ effectManifest = sealedManifest
         /\ ~correctionRequired
       \/ /\ FaultReleaseOnTimeout
          /\ effectState = "completion_unknown"
       \/ /\ FaultReleaseOnVisibilityOnly
          /\ grantUseCount = 1
          /\ visibility = "exact_visible"
          /\ effectState # "confirmed_applied" )
    /\ releaseState' = "released"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

SettleConfirmedNotReleased ==
    /\ effectState = "confirmed_not_applied"
    /\ visibility # "exact_visible"
    /\ releaseState' = "confirmed_not_released"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

CompileCorrection(c) ==
    /\ c \in Candidates
    /\ currentCandidate \in Candidates
    /\ c # currentCandidate
    /\ compiledCandidates' = compiledCandidates \cup {c}
    /\ currentCandidate' = c
    /\ decision' = IF decision = "authorized" THEN "superseded" ELSE decision
    /\ correctionRequired' = TRUE
    /\ UNCHANGED << now, requestCandidate, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    releaseState >>

WithdrawCorrectedRelease ==
    /\ releaseState = "released"
    /\ correctionRequired
    /\ releaseState' = "withdrawn"
    /\ UNCHANGED << now, compiledCandidates, currentCandidate,
                    requestCandidate, decision, decisionCandidate,
                    manifestState, sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    correctionRequired >>

Tick ==
    /\ now < MaxTime
    /\ now' = now + 1
    /\ UNCHANGED << compiledCandidates, currentCandidate, requestCandidate,
                    decision, decisionCandidate, manifestState,
                    sealedManifest, sealedCandidate,
                    sealHadAuthorizedDecision, grantState, grantManifest,
                    grantUseCount, effectState, effectManifest,
                    reconciliation, visibility, observedManifest,
                    releaseState, correctionRequired >>

BaseNext ==
    \/ Tick
    \/ RequestRelease
    \/ AuthorizeDecision
    \/ DenyDecision
    \/ RevokeGrant
    \/ ObserveGrantExpiry
    \/ AuthorizeEffect
    \/ FaultReuseSingleUseGrant
    \/ StartDispatch
    \/ ReportTimeout
    \/ ReportApplied
    \/ ReportDefinitelyNotApplied
    \/ BeginReconciliation
    \/ ReconcileApplied
    \/ ReconcileNotApplied
    \/ ObserveExactVisibility
    \/ ObserveMismatch
    \/ SettleReleased
    \/ SettleConfirmedNotReleased
    \/ WithdrawCorrectedRelease
    \/ \E c \in Candidates : CompileInitialCandidate(c)
    \/ \E c \in Candidates : CompileCorrection(c)
    \/ \E m \in Manifests : SealManifest(m)
    \/ \E m \in Manifests : IssuePublicationGrant(m)

Next ==
    /\ BaseNext
    /\ dispute' =
          IF FaultSuppressDispute
          THEN dispute
          ELSE IF dispute = "required" \/
                  (effectState' = "confirmed_not_applied" /\
                   visibility' = "exact_visible")
               THEN "required"
               ELSE "none"

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ now \in 0..MaxTime
    /\ compiledCandidates \subseteq Candidates
    /\ currentCandidate \in Candidates \cup {NoValue}
    /\ requestCandidate \in Candidates \cup {NoValue}
    /\ decision \in DecisionStates
    /\ decisionCandidate \in Candidates \cup {NoValue}
    /\ manifestState \in ManifestStates
    /\ sealedManifest \in Manifests \cup {NoValue}
    /\ sealedCandidate \in Candidates \cup {NoValue}
    /\ sealHadAuthorizedDecision \in BOOLEAN
    /\ grantState \in GrantStates
    /\ grantManifest \in Manifests \cup {NoValue}
    /\ grantUseCount \in 0..2
    /\ effectState \in EffectStates
    /\ effectManifest \in Manifests \cup {NoValue}
    /\ reconciliation \in ReconciliationStates
    /\ visibility \in VisibilityStates
    /\ observedManifest \in Manifests \cup {NoValue}
    /\ dispute \in DisputeStates
    /\ releaseState \in ReleaseStates
    /\ correctionRequired \in BOOLEAN

ManifestWasSealedFromAuthorizedCandidate ==
    manifestState = "sealed" =>
        /\ sealHadAuthorizedDecision
        /\ sealedCandidate \in compiledCandidates
        /\ sealedManifest = ManifestFor(sealedCandidate)

GrantBindsExactFinalManifest ==
    grantState # "none" =>
        /\ manifestState = "sealed"
        /\ grantManifest = sealedManifest

PublicationGrantIsSingleUse == grantUseCount <= 1

EffectFollowsGrantAndExactManifest ==
    effectState # "not_intended" =>
        /\ manifestState = "sealed"
        /\ effectManifest = grantManifest
        /\ effectManifest = sealedManifest
        /\ (effectState = "authorized" =>
              /\ grantUseCount = 0
              /\ grantState \in {"active", "revoked", "expired"})
        /\ (effectState \in {"started", "completion_unknown",
                             "confirmed_applied", "confirmed_not_applied"} =>
              /\ grantUseCount = 1
              /\ grantState = "used")

ReleasedRequiresExactExternalObservation ==
    releaseState = "released" =>
        /\ effectState = "confirmed_applied"
        /\ visibility = "exact_visible"
        /\ observedManifest = effectManifest
        /\ effectManifest = sealedManifest

TimeoutNeverMeansReleased ==
    effectState = "completion_unknown" => releaseState # "released"

VisibilityObservationRequiresDispatch ==
    visibility # "not_observed" =>
        /\ grantUseCount = 1
        /\ effectManifest \in Manifests
        /\ effectState \in {"started", "completion_unknown",
                             "confirmed_applied", "confirmed_not_applied"}

ContradictoryExternalFacts ==
    /\ effectState = "confirmed_not_applied"
    /\ visibility = "exact_visible"

ContradictoryExternalFactsRequireDispute ==
    /\ (ContradictoryExternalFacts =>
          /\ dispute = "required"
          /\ releaseState = "completion_unknown")
    /\ (dispute = "required" => ContradictoryExternalFacts)

================================================================================
