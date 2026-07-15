-------------------------- MODULE ResourceReservation --------------------------
EXTENDS Naturals, FiniteSets, TLC

(***************************************************************************)
(* Bounded Gate A model for one resource_budget child reservation.         *)
(* Dimensions represent non-fungible execution, money, and verification    *)
(* capacity. Claiming commits a ceiling but never invents actual use. A     *)
(* crash or unknown observation keeps that ceiling held until exact         *)
(* settlement evidence exists.                                              *)
(***************************************************************************)

CONSTANTS
    ExecutionCapacity,
    MoneyCapacity,
    VerificationCapacity,
    ExecutionDemand,
    MoneyDemand,
    VerificationDemand,
    FaultCrossResourceConversion,
    FaultReleaseClaimedOnCrash,
    FaultSettleWithoutObservation,
    FaultInferActualAtClaim

Dimensions == {"execution", "money", "verification"}
Capacity ==
    [d \in Dimensions |->
        CASE d = "execution" -> ExecutionCapacity
          [] d = "money" -> MoneyCapacity
          [] OTHER -> VerificationCapacity]
Demand ==
    [d \in Dimensions |->
        CASE d = "execution" -> ExecutionDemand
          [] d = "money" -> MoneyDemand
          [] OTHER -> VerificationDemand]

ASSUME /\ ExecutionCapacity \in Nat
       /\ MoneyCapacity \in Nat
       /\ VerificationCapacity \in Nat
       /\ ExecutionDemand \in Nat
       /\ MoneyDemand \in Nat
       /\ VerificationDemand \in Nat
       /\ \A d \in Dimensions : Demand[d] > 0
       /\ FaultCrossResourceConversion \in BOOLEAN
       /\ FaultReleaseClaimedOnCrash \in BOOLEAN
       /\ FaultSettleWithoutObservation \in BOOLEAN
       /\ FaultInferActualAtClaim \in BOOLEAN

ReservationStates ==
    {"none", "active", "claimed", "released", "expired", "settled"}
ActualStates == {"unknown", "observed"}

ZeroVector == [d \in Dimensions |-> 0]
ComponentwiseFits == \A d \in Dimensions : Demand[d] <= Capacity[d]

VARIABLES
    reservationState,
    held,
    claimCommitted,
    actualStatus,
    actualInferredAtClaim,
    settlementEvidence,
    crashObserved,
    recoveryObserved

vars == << reservationState, held, claimCommitted, actualStatus,
           actualInferredAtClaim, settlementEvidence, crashObserved,
           recoveryObserved >>

Init ==
    /\ reservationState = "none"
    /\ held = ZeroVector
    /\ claimCommitted = FALSE
    /\ actualStatus = "unknown"
    /\ actualInferredAtClaim = FALSE
    /\ settlementEvidence = FALSE
    /\ crashObserved = FALSE
    /\ recoveryObserved = FALSE

Reserve ==
    /\ reservationState = "none"
    /\ IF FaultCrossResourceConversion THEN TRUE ELSE ComponentwiseFits
    /\ reservationState' = "active"
    /\ held' = Demand
    /\ UNCHANGED << claimCommitted, actualStatus, actualInferredAtClaim,
                    settlementEvidence, crashObserved, recoveryObserved >>

Claim ==
    /\ reservationState = "active"
    /\ reservationState' = "claimed"
    /\ claimCommitted' = TRUE
    /\ IF FaultInferActualAtClaim
          THEN /\ actualStatus' = "observed"
               /\ actualInferredAtClaim' = TRUE
          ELSE /\ UNCHANGED actualStatus
               /\ UNCHANGED actualInferredAtClaim
    /\ UNCHANGED << held, settlementEvidence, crashObserved,
                    recoveryObserved >>

ReleaseBeforeClaim ==
    /\ reservationState = "active"
    /\ reservationState' = "released"
    /\ held' = ZeroVector
    /\ UNCHANGED << claimCommitted, actualStatus, actualInferredAtClaim,
                    settlementEvidence, crashObserved, recoveryObserved >>

ExpireBeforeClaim ==
    /\ reservationState = "active"
    /\ reservationState' = "expired"
    /\ held' = ZeroVector
    /\ UNCHANGED << claimCommitted, actualStatus, actualInferredAtClaim,
                    settlementEvidence, crashObserved, recoveryObserved >>

ObserveActualUse ==
    /\ reservationState = "claimed"
    /\ actualStatus = "unknown"
    /\ actualStatus' = "observed"
    /\ settlementEvidence' = TRUE
    /\ UNCHANGED << reservationState, held, claimCommitted,
                    actualInferredAtClaim, crashObserved, recoveryObserved >>

Settle ==
    /\ reservationState = "claimed"
    /\ (settlementEvidence \/ FaultSettleWithoutObservation)
    /\ reservationState' = "settled"
    /\ held' = ZeroVector
    /\ UNCHANGED << claimCommitted, actualStatus, actualInferredAtClaim,
                    settlementEvidence, crashObserved, recoveryObserved >>

CrashAfterClaim ==
    /\ reservationState = "claimed"
    /\ ~crashObserved
    /\ crashObserved' = TRUE
    /\ IF FaultReleaseClaimedOnCrash
          THEN /\ reservationState' = "released"
               /\ held' = ZeroVector
          ELSE /\ UNCHANGED reservationState
               /\ UNCHANGED held
    /\ UNCHANGED << claimCommitted, actualStatus, actualInferredAtClaim,
                    settlementEvidence, recoveryObserved >>

ObserveRecovery ==
    /\ crashObserved
    /\ ~recoveryObserved
    /\ recoveryObserved' = TRUE
    /\ UNCHANGED << reservationState, held, claimCommitted, actualStatus,
                    actualInferredAtClaim, settlementEvidence,
                    crashObserved >>

Next ==
    \/ Reserve
    \/ Claim
    \/ ReleaseBeforeClaim
    \/ ExpireBeforeClaim
    \/ ObserveActualUse
    \/ Settle
    \/ CrashAfterClaim
    \/ ObserveRecovery

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ reservationState \in ReservationStates
    /\ held \in [Dimensions -> Nat]
    /\ claimCommitted \in BOOLEAN
    /\ actualStatus \in ActualStates
    /\ actualInferredAtClaim \in BOOLEAN
    /\ settlementEvidence \in BOOLEAN
    /\ crashObserved \in BOOLEAN
    /\ recoveryObserved \in BOOLEAN

NoDimensionOvercommit ==
    \A d \in Dimensions : held[d] <= Capacity[d]

ClaimedCeilingRemainsHeld ==
    claimCommitted /\ reservationState = "claimed" => held = Demand

TerminalReleaseWasPreClaim ==
    reservationState \in {"released", "expired"} => ~claimCommitted

ClaimDoesNotInventActualUse == ~actualInferredAtClaim

SettlementRequiresObservation ==
    reservationState = "settled" =>
        settlementEvidence /\ actualStatus = "observed"

=============================================================================
