------------------------------ MODULE ExternalEffects ------------------------------
EXTENDS Naturals, FiniteSets, TLC

(***************************************************************************)
(* Bounded Gate A model of the T1 intent / dispatch / observation /         *)
(* reconciliation protocol. The provider boundary is outside the canonical  *)
(* transaction. Fault constants are enabled only by counterexample configs. *)
(***************************************************************************)

CONSTANTS
    Effects,
    RetrySafeEffects,
    ExpiresAt,
    MaxTime,
    FaultDispatchAfterRevocation,
    FaultBlindRetry

ASSUME /\ Effects # {}
       /\ RetrySafeEffects \subseteq Effects
       /\ ExpiresAt \in Nat \ {0}
       /\ MaxTime \in Nat
       /\ MaxTime >= ExpiresAt
       /\ FaultDispatchAfterRevocation \in BOOLEAN
       /\ FaultBlindRetry \in BOOLEAN

GrantStates == {"active", "revoked", "expired"}
SettlementStates == {"not_intended", "authorized", "started",
                     "completion_unknown", "confirmed_applied",
                     "confirmed_not_applied"}
ReconciliationStates == {"not_required", "pending", "running",
                          "completed", "failed", "manual_review"}

VARIABLES
    now,
    grantState,
    intentCommitted,
    settlement,
    reconciliation,
    dispatchCount,
    ambiguitySeen,
    notAppliedByReconciliation,
    postTerminalDispatch,
    unsafeRetryOccurred

vars == << now, grantState, intentCommitted, settlement, reconciliation,
           dispatchCount, ambiguitySeen, notAppliedByReconciliation,
           postTerminalDispatch, unsafeRetryOccurred >>

Init ==
    /\ now = 0
    /\ grantState = [e \in Effects |-> "active"]
    /\ intentCommitted = [e \in Effects |-> FALSE]
    /\ settlement = [e \in Effects |-> "not_intended"]
    /\ reconciliation = [e \in Effects |-> "not_required"]
    /\ dispatchCount = [e \in Effects |-> 0]
    /\ ambiguitySeen = [e \in Effects |-> FALSE]
    /\ notAppliedByReconciliation = [e \in Effects |-> FALSE]
    /\ postTerminalDispatch = [e \in Effects |-> FALSE]
    /\ unsafeRetryOccurred = [e \in Effects |-> FALSE]

AuthorizeIntent(e) ==
    /\ e \in Effects
    /\ settlement[e] = "not_intended"
    /\ grantState[e] = "active"
    /\ now < ExpiresAt
    /\ intentCommitted' = [intentCommitted EXCEPT ![e] = TRUE]
    /\ settlement' = [settlement EXCEPT ![e] = "authorized"]
    /\ UNCHANGED << now, grantState, reconciliation, dispatchCount,
                    ambiguitySeen, notAppliedByReconciliation,
                    postTerminalDispatch, unsafeRetryOccurred >>

RevokeGrant(e) ==
    /\ e \in Effects
    /\ grantState[e] = "active"
    /\ grantState' = [grantState EXCEPT ![e] = "revoked"]
    /\ UNCHANGED << now, intentCommitted, settlement, reconciliation,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

ObserveExpiry(e) ==
    /\ e \in Effects
    /\ grantState[e] = "active"
    /\ now >= ExpiresAt
    /\ grantState' = [grantState EXCEPT ![e] = "expired"]
    /\ UNCHANGED << now, intentCommitted, settlement, reconciliation,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

ClaimAndStartDispatch(e) ==
    /\ e \in Effects
    /\ settlement[e] = "authorized"
    /\ ( /\ grantState[e] = "active"
         /\ now < ExpiresAt
       \/ /\ FaultDispatchAfterRevocation
          /\ grantState[e] \in {"revoked", "expired"} )
    /\ settlement' = [settlement EXCEPT ![e] = "started"]
    /\ dispatchCount' = [dispatchCount EXCEPT ![e] = @ + 1]
    /\ postTerminalDispatch' =
          [postTerminalDispatch EXCEPT
              ![e] = @ \/ grantState[e] # "active" \/ now >= ExpiresAt]
    /\ UNCHANGED << now, grantState, intentCommitted, reconciliation,
                    ambiguitySeen, notAppliedByReconciliation,
                    unsafeRetryOccurred >>

ReportTimeout(e) ==
    /\ e \in Effects
    /\ settlement[e] = "started"
    /\ settlement' = [settlement EXCEPT ![e] = "completion_unknown"]
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "pending"]
    /\ ambiguitySeen' = [ambiguitySeen EXCEPT ![e] = TRUE]
    /\ UNCHANGED << now, grantState, intentCommitted, dispatchCount,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

ReportApplied(e) ==
    /\ e \in Effects
    /\ settlement[e] = "started"
    /\ settlement' = [settlement EXCEPT ![e] = "confirmed_applied"]
    /\ UNCHANGED << now, grantState, intentCommitted, reconciliation,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

ReportDefinitelyNotApplied(e) ==
    /\ e \in Effects
    /\ settlement[e] = "started"
    /\ ~ambiguitySeen[e]
    /\ settlement' = [settlement EXCEPT ![e] = "confirmed_not_applied"]
    /\ UNCHANGED << now, grantState, intentCommitted, reconciliation,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

BeginReconciliation(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ reconciliation[e] = "pending"
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "running"]
    /\ UNCHANGED << now, grantState, intentCommitted, settlement,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

ReconcileApplied(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ reconciliation[e] = "running"
    /\ settlement' = [settlement EXCEPT ![e] = "confirmed_applied"]
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "completed"]
    /\ UNCHANGED << now, grantState, intentCommitted, dispatchCount,
                    ambiguitySeen, notAppliedByReconciliation,
                    postTerminalDispatch, unsafeRetryOccurred >>

ReconcileNotApplied(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ reconciliation[e] = "running"
    /\ settlement' = [settlement EXCEPT ![e] = "confirmed_not_applied"]
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "completed"]
    /\ notAppliedByReconciliation' =
          [notAppliedByReconciliation EXCEPT ![e] = TRUE]
    /\ UNCHANGED << now, grantState, intentCommitted, dispatchCount,
                    ambiguitySeen, postTerminalDispatch,
                    unsafeRetryOccurred >>

ReconciliationFailed(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ reconciliation[e] = "running"
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "failed"]
    /\ UNCHANGED << now, grantState, intentCommitted, settlement,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

EscalateToManualReview(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ reconciliation[e] = "failed"
    /\ reconciliation' = [reconciliation EXCEPT ![e] = "manual_review"]
    /\ UNCHANGED << now, grantState, intentCommitted, settlement,
                    dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

RetryFromUnknown(e) ==
    /\ e \in Effects
    /\ settlement[e] = "completion_unknown"
    /\ dispatchCount[e] < 2
    /\ grantState[e] = "active"
    /\ now < ExpiresAt
    /\ (e \in RetrySafeEffects \/ FaultBlindRetry)
    /\ settlement' = [settlement EXCEPT ![e] = "started"]
    /\ dispatchCount' = [dispatchCount EXCEPT ![e] = @ + 1]
    /\ unsafeRetryOccurred' =
          [unsafeRetryOccurred EXCEPT ![e] = @ \/ e \notin RetrySafeEffects]
    /\ UNCHANGED << now, grantState, intentCommitted, reconciliation,
                    ambiguitySeen, notAppliedByReconciliation,
                    postTerminalDispatch >>

Tick ==
    /\ now < MaxTime
    /\ now' = now + 1
    /\ UNCHANGED << grantState, intentCommitted, settlement,
                    reconciliation, dispatchCount, ambiguitySeen,
                    notAppliedByReconciliation, postTerminalDispatch,
                    unsafeRetryOccurred >>

Next ==
    \/ Tick
    \/ \E e \in Effects : AuthorizeIntent(e)
    \/ \E e \in Effects : RevokeGrant(e)
    \/ \E e \in Effects : ObserveExpiry(e)
    \/ \E e \in Effects : ClaimAndStartDispatch(e)
    \/ \E e \in Effects : ReportTimeout(e)
    \/ \E e \in Effects : ReportApplied(e)
    \/ \E e \in Effects : ReportDefinitelyNotApplied(e)
    \/ \E e \in Effects : BeginReconciliation(e)
    \/ \E e \in Effects : ReconcileApplied(e)
    \/ \E e \in Effects : ReconcileNotApplied(e)
    \/ \E e \in Effects : ReconciliationFailed(e)
    \/ \E e \in Effects : EscalateToManualReview(e)
    \/ \E e \in Effects : RetryFromUnknown(e)

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ now \in 0..MaxTime
    /\ grantState \in [Effects -> GrantStates]
    /\ intentCommitted \in [Effects -> BOOLEAN]
    /\ settlement \in [Effects -> SettlementStates]
    /\ reconciliation \in [Effects -> ReconciliationStates]
    /\ dispatchCount \in [Effects -> 0..2]
    /\ ambiguitySeen \in [Effects -> BOOLEAN]
    /\ notAppliedByReconciliation \in [Effects -> BOOLEAN]
    /\ postTerminalDispatch \in [Effects -> BOOLEAN]
    /\ unsafeRetryOccurred \in [Effects -> BOOLEAN]

IntentAlwaysPrecedesDispatch ==
    \A e \in Effects : dispatchCount[e] > 0 => intentCommitted[e]

NoDispatchAfterRevocationOrExpiry ==
    \A e \in Effects : ~postTerminalDispatch[e]

NoUnsafeRetry ==
    \A e \in Effects :
        /\ dispatchCount[e] > 1 => e \in RetrySafeEffects
        /\ ~unsafeRetryOccurred[e]

AmbiguityRequiresReconciliationForNotApplied ==
    \A e \in Effects :
        ambiguitySeen[e] /\ settlement[e] = "confirmed_not_applied" =>
            /\ reconciliation[e] = "completed"
            /\ notAppliedByReconciliation[e]

CompletedReconciliationHasPolarity ==
    \A e \in Effects :
        reconciliation[e] = "completed" =>
            settlement[e] \in {"confirmed_applied", "confirmed_not_applied"}

UnknownRetainsAmbiguityAndRecoveryState ==
    \A e \in Effects :
        settlement[e] = "completion_unknown" =>
            /\ ambiguitySeen[e]
            /\ reconciliation[e] \in
                  {"pending", "running", "failed", "manual_review"}

================================================================================
