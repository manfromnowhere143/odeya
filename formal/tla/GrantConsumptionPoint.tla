-------------------------- MODULE GrantConsumptionPoint --------------------------
EXTENDS Naturals, TLC

(***************************************************************************)
(* Gate A resolution model for the previously ambiguous grant-consumption   *)
(* point. Ordinary in-ledger commands consume at their domain commit with   *)
(* no observable reservation window. Cross-boundary effects reserve at T1  *)
(* and consume only in the dispatch-claim commit after authority recheck.   *)
(***************************************************************************)

CONSTANTS ExpiresAt, MaxTime, FaultConsumeEffectGrantAtIntent

ASSUME /\ ExpiresAt \in Nat \ {0}
       /\ MaxTime \in Nat
       /\ MaxTime >= ExpiresAt
       /\ FaultConsumeEffectGrantAtIntent \in BOOLEAN

ReservationStates == {"none", "reserved", "released", "cancelled",
                      "expired", "consumed"}
EffectStates == {"not_intended", "authorized", "cancelled_before_dispatch",
                 "started"}

VARIABLES
    now,
    ordinaryGrantRevoked,
    ordinaryUseCount,
    ordinaryCommandCommitted,
    ordinaryReservation,
    effectGrantRevoked,
    effectGrantExpiryObserved,
    effectUseCount,
    effectReservation,
    effectState,
    dispatchCount,
    dispatchClaimRecheckedAuthority,
    revokedBeforeDispatch,
    expiredBeforeDispatch

vars == << now, ordinaryGrantRevoked, ordinaryUseCount,
           ordinaryCommandCommitted, ordinaryReservation,
           effectGrantRevoked, effectGrantExpiryObserved, effectUseCount,
           effectReservation, effectState, dispatchCount,
           dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
           expiredBeforeDispatch >>

Init ==
    /\ now = 0
    /\ ordinaryGrantRevoked = FALSE
    /\ ordinaryUseCount = 0
    /\ ordinaryCommandCommitted = FALSE
    /\ ordinaryReservation = "none"
    /\ effectGrantRevoked = FALSE
    /\ effectGrantExpiryObserved = FALSE
    /\ effectUseCount = 0
    /\ effectReservation = "none"
    /\ effectState = "not_intended"
    /\ dispatchCount = 0
    /\ dispatchClaimRecheckedAuthority = FALSE
    /\ revokedBeforeDispatch = FALSE
    /\ expiredBeforeDispatch = FALSE

CommitOrdinaryCommand ==
    /\ ~ordinaryCommandCommitted
    /\ ~ordinaryGrantRevoked
    /\ now < ExpiresAt
    /\ ordinaryUseCount = 0
    /\ ordinaryReservation = "none"
    /\ ordinaryCommandCommitted' = TRUE
    /\ ordinaryUseCount' = 1
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, effectReservation, effectState,
                    dispatchCount, dispatchClaimRecheckedAuthority,
                    revokedBeforeDispatch, expiredBeforeDispatch >>

RevokeOrdinaryGrant ==
    /\ ~ordinaryGrantRevoked
    /\ ordinaryGrantRevoked' = TRUE
    /\ UNCHANGED << now, ordinaryUseCount, ordinaryCommandCommitted,
                    ordinaryReservation, effectGrantRevoked,
                    effectGrantExpiryObserved, effectUseCount,
                    effectReservation, effectState, dispatchCount,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
                    expiredBeforeDispatch >>

ReserveEffectUse ==
    /\ effectState = "not_intended"
    /\ effectReservation = "none"
    /\ effectUseCount = 0
    /\ ~effectGrantRevoked
    /\ now < ExpiresAt
    /\ ~FaultConsumeEffectGrantAtIntent
    /\ effectReservation' = "reserved"
    /\ effectState' = "authorized"
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, dispatchCount,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
                    expiredBeforeDispatch >>

FaultReserveAndConsumeAtIntent ==
    /\ FaultConsumeEffectGrantAtIntent
    /\ effectState = "not_intended"
    /\ effectReservation = "none"
    /\ effectUseCount = 0
    /\ ~effectGrantRevoked
    /\ now < ExpiresAt
    /\ effectReservation' = "consumed"
    /\ effectUseCount' = 1
    /\ effectState' = "authorized"
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    dispatchCount, dispatchClaimRecheckedAuthority,
                    revokedBeforeDispatch, expiredBeforeDispatch >>

ReleaseReservation ==
    /\ effectState = "authorized"
    /\ effectReservation = "reserved"
    /\ effectReservation' = "released"
    /\ effectState' = "cancelled_before_dispatch"
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, dispatchCount,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
                    expiredBeforeDispatch >>

CancelReservation ==
    /\ effectState = "authorized"
    /\ effectReservation = "reserved"
    /\ effectReservation' = "cancelled"
    /\ effectState' = "cancelled_before_dispatch"
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, dispatchCount,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
                    expiredBeforeDispatch >>

RevokeEffectGrant ==
    /\ ~effectGrantRevoked
    /\ effectGrantRevoked' = TRUE
    /\ revokedBeforeDispatch' =
          (revokedBeforeDispatch \/ (dispatchCount = 0))
    /\ effectReservation' =
          IF effectReservation = "reserved" THEN "cancelled"
          ELSE effectReservation
    /\ effectState' =
          IF effectReservation = "reserved"
          THEN "cancelled_before_dispatch"
          ELSE effectState
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantExpiryObserved, effectUseCount, dispatchCount,
                    dispatchClaimRecheckedAuthority, expiredBeforeDispatch >>

ObserveEffectGrantExpiry ==
    /\ ~effectGrantExpiryObserved
    /\ now >= ExpiresAt
    /\ effectGrantExpiryObserved' = TRUE
    /\ expiredBeforeDispatch' =
          (expiredBeforeDispatch \/ (dispatchCount = 0))
    /\ effectReservation' =
          IF effectReservation = "reserved" THEN "expired"
          ELSE effectReservation
    /\ effectState' =
          IF effectReservation = "reserved"
          THEN "cancelled_before_dispatch"
          ELSE effectState
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectUseCount, dispatchCount,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch >>

DispatchClaim ==
    /\ effectState = "authorized"
    /\ effectReservation = "reserved"
    /\ effectUseCount = 0
    /\ dispatchCount = 0
    /\ ~effectGrantRevoked
    /\ now < ExpiresAt
    /\ effectReservation' = "consumed"
    /\ effectUseCount' = 1
    /\ effectState' = "started"
    /\ dispatchCount' = 1
    /\ dispatchClaimRecheckedAuthority' = TRUE
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    revokedBeforeDispatch, expiredBeforeDispatch >>

FaultDispatchWithoutRecheck ==
    /\ FaultConsumeEffectGrantAtIntent
    /\ effectState = "authorized"
    /\ effectReservation = "consumed"
    /\ effectUseCount = 1
    /\ dispatchCount = 0
    /\ effectState' = "started"
    /\ dispatchCount' = 1
    /\ UNCHANGED << now, ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, effectReservation,
                    dispatchClaimRecheckedAuthority, revokedBeforeDispatch,
                    expiredBeforeDispatch >>

Tick ==
    /\ now < MaxTime
    /\ now' = now + 1
    /\ UNCHANGED << ordinaryGrantRevoked, ordinaryUseCount,
                    ordinaryCommandCommitted, ordinaryReservation,
                    effectGrantRevoked, effectGrantExpiryObserved,
                    effectUseCount, effectReservation, effectState,
                    dispatchCount, dispatchClaimRecheckedAuthority,
                    revokedBeforeDispatch, expiredBeforeDispatch >>

Next ==
    \/ Tick
    \/ CommitOrdinaryCommand
    \/ RevokeOrdinaryGrant
    \/ ReserveEffectUse
    \/ FaultReserveAndConsumeAtIntent
    \/ ReleaseReservation
    \/ CancelReservation
    \/ RevokeEffectGrant
    \/ ObserveEffectGrantExpiry
    \/ DispatchClaim
    \/ FaultDispatchWithoutRecheck

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ now \in 0..MaxTime
    /\ ordinaryGrantRevoked \in BOOLEAN
    /\ ordinaryUseCount \in 0..1
    /\ ordinaryCommandCommitted \in BOOLEAN
    /\ ordinaryReservation \in ReservationStates
    /\ effectGrantRevoked \in BOOLEAN
    /\ effectGrantExpiryObserved \in BOOLEAN
    /\ effectUseCount \in 0..1
    /\ effectReservation \in ReservationStates
    /\ effectState \in EffectStates
    /\ dispatchCount \in 0..1
    /\ dispatchClaimRecheckedAuthority \in BOOLEAN
    /\ revokedBeforeDispatch \in BOOLEAN
    /\ expiredBeforeDispatch \in BOOLEAN

OrdinaryCommandConsumesAtomically ==
    /\ ordinaryReservation = "none"
    /\ (ordinaryCommandCommitted => ordinaryUseCount = 1)
    /\ (ordinaryUseCount = 1 => ordinaryCommandCommitted)

EffectIntentOnlyReserves ==
    effectState = "authorized" /\ ~FaultConsumeEffectGrantAtIntent =>
        /\ effectReservation = "reserved"
        /\ effectUseCount = 0

DispatchClaimRechecksAndConsumes ==
    dispatchCount = 1 =>
        /\ effectState = "started"
        /\ effectReservation = "consumed"
        /\ effectUseCount = 1
        /\ dispatchClaimRecheckedAuthority

RevokeOrExpiryFirstBlocksDispatch ==
    /\ (revokedBeforeDispatch => dispatchCount = 0)
    /\ (expiredBeforeDispatch => dispatchCount = 0)

NoGrantOveruse ==
    /\ ordinaryUseCount <= 1
    /\ effectUseCount <= 1

================================================================================
