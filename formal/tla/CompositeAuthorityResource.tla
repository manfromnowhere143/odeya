-------------------- MODULE CompositeAuthorityResource --------------------
EXTENDS Naturals, FiniteSets, TLC

(***************************************************************************)
(* Bounded architecture model for one verification run whose assignment    *)
(* atomically consumes an ordered cohort of distinct, action-bound,         *)
(* single-use role grants and creates one combined resource reservation.    *)
(* attempt.start, preclaim invalidation, and controlled deadline expiry are *)
(* serialized competitors. Exact retained resource evidence is required     *)
(* before settlement; missing or unavailable evidence is never numeric zero.*)
(***************************************************************************)

CONSTANTS
    FaultPartialGrantCohort,
    FaultReleaseAfterClaim,
    FaultInferZeroAndPartiallySettle,
    FaultStartAfterPreclaimTerminal

ASSUME /\ FaultPartialGrantCohort \in BOOLEAN
       /\ FaultReleaseAfterClaim \in BOOLEAN
       /\ FaultInferZeroAndPartiallySettle \in BOOLEAN
       /\ FaultStartAfterPreclaimTerminal \in BOOLEAN

RequiredSlots == 1..5
ProperSlotPrefix == 1..4

RoleForSlot ==
    [s \in RequiredSlots |->
        CASE s = 1 -> "safety"
          [] s = 2 -> "data_rights"
          [] s = 3 -> "resource"
          [] s = 4 -> "execution"
          [] OTHER -> "verification"]

AuthorityActions == {"assign", "start"}
ActionIdFor ==
    [action \in AuthorityActions |->
        CASE action = "assign" -> "verification.assign/run-1/request-1"
          [] OTHER -> "attempt.start/run-1/request-2"]
GrantForActionSlot ==
    [action \in AuthorityActions |->
        [slot \in RequiredSlots |-> <<action, slot>>]]
Grants ==
    {GrantForActionSlot[action][slot] :
        action \in AuthorityActions, slot \in RequiredSlots}
GrantActionBinding ==
    [grant \in Grants |-> ActionIdFor[grant[1]]]

NonMoneyAxes == {"execution", "verification"}
HoldAxes == NonMoneyAxes \cup {"money"}
MoneyEvidenceAxes == {"billed", "refunded"}
Ceiling == [a \in HoldAxes |-> 1]
ZeroHold == [a \in HoldAxes |-> 0]
(* Numeric sentinel outside every modeled exact-value range. *)
NoValue == 2
EvidenceStates == {"unknown", "exact", "missing", "unavailable"}

DecisionStates == {"pending", "accepted", "rejected"}
ReservationStates ==
    {"none", "active", "claimed", "released", "expired", "settled"}
LastAuthoritySteps == {"none", "accept", "reject", "replay"}

VARIABLES
    decision,
    lastAuthorityStep,
    lastUseDelta,
    lastExhaustDelta,
    grantUseCount,
    grantExhaustCount,
    grantState,
    replaySeen,
    reservationCount,
    reservationState,
    held,
    assignmentCommitted,
    startCommitted,
    claimEverCommitted,
    preclaimTerminalEverCommitted,
    controlledTick,
    nonMoneyStatus,
    nonMoneyActual,
    moneyStatus,
    moneyActual,
    inferredZeroFromAbsence

vars ==
    << decision, lastAuthorityStep, lastUseDelta, lastExhaustDelta,
       grantUseCount, grantExhaustCount, grantState, replaySeen,
       reservationCount, reservationState, held, assignmentCommitted,
       startCommitted, claimEverCommitted, preclaimTerminalEverCommitted,
       controlledTick, nonMoneyStatus, nonMoneyActual, moneyStatus,
       moneyActual, inferredZeroFromAbsence >>

Init ==
    /\ decision = [action \in AuthorityActions |-> "pending"]
    /\ lastAuthorityStep = "none"
    /\ lastUseDelta = {}
    /\ lastExhaustDelta = {}
    /\ grantUseCount =
           [action \in AuthorityActions |->
               [slot \in RequiredSlots |-> 0]]
    /\ grantExhaustCount =
           [action \in AuthorityActions |->
               [slot \in RequiredSlots |-> 0]]
    /\ grantState =
           [action \in AuthorityActions |->
               [slot \in RequiredSlots |-> "active"]]
    /\ replaySeen = [action \in AuthorityActions |-> FALSE]
    /\ reservationCount = 0
    /\ reservationState = "none"
    /\ held = ZeroHold
    /\ assignmentCommitted = FALSE
    /\ startCommitted = FALSE
    /\ claimEverCommitted = FALSE
    /\ preclaimTerminalEverCommitted = FALSE
    /\ controlledTick = 0
    /\ nonMoneyStatus = [a \in NonMoneyAxes |-> "unknown"]
    /\ nonMoneyActual = [a \in NonMoneyAxes |-> NoValue]
    /\ moneyStatus = [a \in MoneyEvidenceAxes |-> "unknown"]
    /\ moneyActual = [a \in MoneyEvidenceAxes |-> NoValue]
    /\ inferredZeroFromAbsence = FALSE

AllRequiredGrantsActive(action) ==
    /\ action \in AuthorityActions
    /\ \A slot \in RequiredSlots :
           /\ grantState[action][slot] = "active"
           /\ GrantActionBinding[GrantForActionSlot[action][slot]] =
                  ActionIdFor[action]

AcceptAssignment ==
    /\ decision["assign"] = "pending"
    /\ reservationState = "none"
    /\ AllRequiredGrantsActive("assign")
    /\ decision' = [decision EXCEPT !["assign"] = "accepted"]
    /\ lastAuthorityStep' = "accept"
    /\ lastUseDelta' = RequiredSlots
    /\ lastExhaustDelta' = RequiredSlots
    /\ grantUseCount' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |->
                           grantUseCount[action][slot] + 1]
                  ELSE grantUseCount[action]]
    /\ grantExhaustCount' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |->
                           grantExhaustCount[action][slot] + 1]
                  ELSE grantExhaustCount[action]]
    /\ grantState' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |-> "exhausted"]
                  ELSE grantState[action]]
    /\ UNCHANGED replaySeen
    /\ reservationCount' = 1
    /\ reservationState' = "active"
    /\ held' = Ceiling
    /\ assignmentCommitted' = TRUE
    /\ UNCHANGED << startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    nonMoneyStatus, nonMoneyActual, moneyStatus,
                    moneyActual, inferredZeroFromAbsence >>

RejectAction(action) ==
    /\ action \in AuthorityActions
    /\ decision[action] = "pending"
    /\ (action = "assign" \/ decision["assign"] = "accepted")
    /\ decision' = [decision EXCEPT ![action] = "rejected"]
    /\ lastAuthorityStep' = "reject"
    /\ lastUseDelta' = {}
    /\ lastExhaustDelta' = {}
    /\ UNCHANGED << grantUseCount, grantExhaustCount, grantState,
                    replaySeen, reservationCount, reservationState, held,
                    assignmentCommitted, startCommitted,
                    claimEverCommitted, preclaimTerminalEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

ReplayNoop(action) ==
    /\ action \in AuthorityActions
    /\ decision[action] \in {"accepted", "rejected"}
    /\ ~replaySeen[action]
    /\ replaySeen' = [replaySeen EXCEPT ![action] = TRUE]
    /\ lastAuthorityStep' = "replay"
    /\ lastUseDelta' = {}
    /\ lastExhaustDelta' = {}
    /\ UNCHANGED << decision, grantUseCount, grantExhaustCount, grantState,
                    reservationCount, reservationState, held,
                    assignmentCommitted, startCommitted,
                    claimEverCommitted, preclaimTerminalEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

FaultAcceptPartialGrantCohort ==
    /\ FaultPartialGrantCohort
    /\ decision["assign"] = "pending"
    /\ reservationState = "none"
    /\ \A slot \in ProperSlotPrefix :
           grantState["assign"][slot] = "active"
    /\ decision' = [decision EXCEPT !["assign"] = "accepted"]
    /\ lastAuthorityStep' = "accept"
    /\ lastUseDelta' = ProperSlotPrefix
    /\ lastExhaustDelta' = ProperSlotPrefix
    /\ grantUseCount' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |->
                           IF slot \in ProperSlotPrefix
                              THEN grantUseCount[action][slot] + 1
                              ELSE grantUseCount[action][slot]]
                  ELSE grantUseCount[action]]
    /\ grantExhaustCount' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |->
                           IF slot \in ProperSlotPrefix
                              THEN grantExhaustCount[action][slot] + 1
                              ELSE grantExhaustCount[action][slot]]
                  ELSE grantExhaustCount[action]]
    /\ grantState' =
           [action \in AuthorityActions |->
               IF action = "assign"
                  THEN [slot \in RequiredSlots |->
                           IF slot \in ProperSlotPrefix
                              THEN "exhausted"
                              ELSE grantState[action][slot]]
                  ELSE grantState[action]]
    /\ UNCHANGED replaySeen
    /\ reservationCount' = 1
    /\ reservationState' = "active"
    /\ held' = Ceiling
    /\ assignmentCommitted' = TRUE
    /\ UNCHANGED << startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    nonMoneyStatus, nonMoneyActual, moneyStatus,
                    moneyActual, inferredZeroFromAbsence >>

AttemptStart ==
    /\ decision["assign"] = "accepted"
    /\ decision["start"] = "pending"
    /\ reservationState = "active"
    /\ ~preclaimTerminalEverCommitted
    /\ AllRequiredGrantsActive("start")
    /\ decision' = [decision EXCEPT !["start"] = "accepted"]
    /\ lastAuthorityStep' = "accept"
    /\ lastUseDelta' = RequiredSlots
    /\ lastExhaustDelta' = RequiredSlots
    /\ grantUseCount' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |->
                           grantUseCount[action][slot] + 1]
                  ELSE grantUseCount[action]]
    /\ grantExhaustCount' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |->
                           grantExhaustCount[action][slot] + 1]
                  ELSE grantExhaustCount[action]]
    /\ grantState' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |-> "exhausted"]
                  ELSE grantState[action]]
    /\ reservationState' = "claimed"
    /\ startCommitted' = TRUE
    /\ claimEverCommitted' = TRUE
    /\ UNCHANGED << replaySeen, reservationCount, held,
                    assignmentCommitted, preclaimTerminalEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

PreclaimInvalidate ==
    /\ decision["assign"] = "accepted"
    /\ reservationState = "active"
    /\ ~startCommitted
    /\ reservationState' = "released"
    /\ held' = ZeroHold
    /\ preclaimTerminalEverCommitted' = TRUE
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    assignmentCommitted, startCommitted, claimEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

AdvanceControlledTime ==
    /\ controlledTick = 0
    /\ controlledTick' = 1
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    reservationState, held, assignmentCommitted,
                    startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, nonMoneyStatus,
                    nonMoneyActual, moneyStatus, moneyActual,
                    inferredZeroFromAbsence >>

ControlledDeadlineExpire ==
    /\ decision["assign"] = "accepted"
    /\ reservationState = "active"
    /\ ~startCommitted
    /\ controlledTick = 1
    /\ reservationState' = "expired"
    /\ held' = ZeroHold
    /\ preclaimTerminalEverCommitted' = TRUE
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    assignmentCommitted, startCommitted, claimEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

ObserveExactNonMoney(axis, value) ==
    /\ reservationState = "claimed"
    /\ axis \in NonMoneyAxes
    /\ nonMoneyStatus[axis] = "unknown"
    /\ value \in 0..Ceiling[axis]
    /\ nonMoneyStatus' = [nonMoneyStatus EXCEPT ![axis] = "exact"]
    /\ nonMoneyActual' = [nonMoneyActual EXCEPT ![axis] = value]
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    reservationState, held, assignmentCommitted,
                    startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

ObserveAbsentNonMoney(axis, absence) ==
    /\ reservationState = "claimed"
    /\ axis \in NonMoneyAxes
    /\ absence \in {"missing", "unavailable"}
    /\ nonMoneyStatus[axis] = "unknown"
    /\ nonMoneyStatus' = [nonMoneyStatus EXCEPT ![axis] = absence]
    /\ nonMoneyActual' = [nonMoneyActual EXCEPT ![axis] = NoValue]
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    reservationState, held, assignmentCommitted,
                    startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

ObserveExactMoney(axis, value) ==
    /\ reservationState = "claimed"
    /\ axis \in MoneyEvidenceAxes
    /\ moneyStatus[axis] = "unknown"
    /\ value \in 0..Ceiling["money"]
    /\ moneyStatus' = [moneyStatus EXCEPT ![axis] = "exact"]
    /\ moneyActual' = [moneyActual EXCEPT ![axis] = value]
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    reservationState, held, assignmentCommitted,
                    startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    nonMoneyStatus, nonMoneyActual,
                    inferredZeroFromAbsence >>

ObserveAbsentMoney(axis, absence) ==
    /\ reservationState = "claimed"
    /\ axis \in MoneyEvidenceAxes
    /\ absence \in {"missing", "unavailable"}
    /\ moneyStatus[axis] = "unknown"
    /\ moneyStatus' = [moneyStatus EXCEPT ![axis] = absence]
    /\ moneyActual' = [moneyActual EXCEPT ![axis] = NoValue]
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    reservationState, held, assignmentCommitted,
                    startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    nonMoneyStatus, nonMoneyActual,
                    inferredZeroFromAbsence >>

ExactNonMoneyEvidence ==
    \A axis \in NonMoneyAxes :
        /\ nonMoneyStatus[axis] = "exact"
        /\ nonMoneyActual[axis] \in 0..Ceiling[axis]

ExactMoneyEvidence ==
    /\ \A axis \in MoneyEvidenceAxes :
           /\ moneyStatus[axis] = "exact"
           /\ moneyActual[axis] \in 0..Ceiling["money"]
    /\ moneyActual["refunded"] <= moneyActual["billed"]

SettleReservation ==
    /\ reservationState = "claimed"
    /\ ExactNonMoneyEvidence
    /\ ExactMoneyEvidence
    /\ reservationState' = "settled"
    /\ held' = ZeroHold
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    assignmentCommitted, startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    nonMoneyStatus, nonMoneyActual, moneyStatus, moneyActual,
                    inferredZeroFromAbsence >>

FaultReleaseClaimedReservation ==
    /\ FaultReleaseAfterClaim
    /\ reservationState = "claimed"
    /\ reservationState' = "released"
    /\ held' = ZeroHold
    /\ preclaimTerminalEverCommitted' = TRUE
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    assignmentCommitted, startCommitted, claimEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

FaultInferZeroAndSettlePartial ==
    /\ FaultInferZeroAndPartiallySettle
    /\ reservationState = "claimed"
    /\ nonMoneyStatus["execution"] = "unknown"
    /\ reservationState' = "settled"
    /\ held' = ZeroHold
    /\ nonMoneyStatus' =
           [nonMoneyStatus EXCEPT !["execution"] = "missing"]
    /\ nonMoneyActual' = [nonMoneyActual EXCEPT !["execution"] = 0]
    /\ inferredZeroFromAbsence' = TRUE
    /\ UNCHANGED << decision, lastAuthorityStep, lastUseDelta,
                    lastExhaustDelta, grantUseCount, grantExhaustCount,
                    grantState, replaySeen, reservationCount,
                    assignmentCommitted, startCommitted, claimEverCommitted,
                    preclaimTerminalEverCommitted, controlledTick,
                    moneyStatus, moneyActual >>

FaultStartAfterTerminal ==
    /\ FaultStartAfterPreclaimTerminal
    /\ decision["assign"] = "accepted"
    /\ decision["start"] = "pending"
    /\ reservationState = "expired"
    /\ preclaimTerminalEverCommitted
    /\ AllRequiredGrantsActive("start")
    /\ decision' = [decision EXCEPT !["start"] = "accepted"]
    /\ lastAuthorityStep' = "accept"
    /\ lastUseDelta' = RequiredSlots
    /\ lastExhaustDelta' = RequiredSlots
    /\ grantUseCount' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |->
                           grantUseCount[action][slot] + 1]
                  ELSE grantUseCount[action]]
    /\ grantExhaustCount' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |->
                           grantExhaustCount[action][slot] + 1]
                  ELSE grantExhaustCount[action]]
    /\ grantState' =
           [action \in AuthorityActions |->
               IF action = "start"
                  THEN [slot \in RequiredSlots |-> "exhausted"]
                  ELSE grantState[action]]
    /\ reservationState' = "claimed"
    /\ startCommitted' = TRUE
    /\ claimEverCommitted' = TRUE
    /\ UNCHANGED << replaySeen, reservationCount, held,
                    assignmentCommitted, preclaimTerminalEverCommitted,
                    controlledTick, nonMoneyStatus, nonMoneyActual,
                    moneyStatus, moneyActual, inferredZeroFromAbsence >>

Next ==
    \/ AcceptAssignment
    \/ \E action \in AuthorityActions : RejectAction(action)
    \/ \E action \in AuthorityActions : ReplayNoop(action)
    \/ FaultAcceptPartialGrantCohort
    \/ AttemptStart
    \/ PreclaimInvalidate
    \/ AdvanceControlledTime
    \/ ControlledDeadlineExpire
    \/ \E axis \in NonMoneyAxes, value \in 0..1 :
           ObserveExactNonMoney(axis, value)
    \/ \E axis \in NonMoneyAxes,
          absence \in {"missing", "unavailable"} :
           ObserveAbsentNonMoney(axis, absence)
    \/ \E axis \in MoneyEvidenceAxes, value \in 0..1 :
           ObserveExactMoney(axis, value)
    \/ \E axis \in MoneyEvidenceAxes,
          absence \in {"missing", "unavailable"} :
           ObserveAbsentMoney(axis, absence)
    \/ SettleReservation
    \/ FaultReleaseClaimedReservation
    \/ FaultInferZeroAndSettlePartial
    \/ FaultStartAfterTerminal

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ decision \in [AuthorityActions -> DecisionStates]
    /\ lastAuthorityStep \in LastAuthoritySteps
    /\ lastUseDelta \subseteq RequiredSlots
    /\ lastExhaustDelta \subseteq RequiredSlots
    /\ grantUseCount \in
           [AuthorityActions -> [RequiredSlots -> Nat]]
    /\ grantExhaustCount \in
           [AuthorityActions -> [RequiredSlots -> Nat]]
    /\ grantState \in
           [AuthorityActions ->
               [RequiredSlots -> {"active", "exhausted"}]]
    /\ replaySeen \in [AuthorityActions -> BOOLEAN]
    /\ reservationCount \in 0..1
    /\ reservationState \in ReservationStates
    /\ held \in [HoldAxes -> Nat]
    /\ assignmentCommitted \in BOOLEAN
    /\ startCommitted \in BOOLEAN
    /\ claimEverCommitted \in BOOLEAN
    /\ preclaimTerminalEverCommitted \in BOOLEAN
    /\ controlledTick \in 0..1
    /\ nonMoneyStatus \in [NonMoneyAxes -> EvidenceStates]
    /\ \A axis \in NonMoneyAxes :
           nonMoneyActual[axis] = NoValue \/
               nonMoneyActual[axis] \in 0..Ceiling[axis]
    /\ moneyStatus \in [MoneyEvidenceAxes -> EvidenceStates]
    /\ \A axis \in MoneyEvidenceAxes :
           moneyActual[axis] = NoValue \/
               moneyActual[axis] \in 0..Ceiling["money"]
    /\ inferredZeroFromAbsence \in BOOLEAN

RoleGrantSlotsAreOrderedDistinctAndActionBound ==
    /\ RequiredSlots = 1..Cardinality(RequiredSlots)
    /\ Cardinality(Grants) =
           Cardinality(AuthorityActions) * Cardinality(RequiredSlots)
    /\ Cardinality({RoleForSlot[s] : s \in RequiredSlots}) =
           Cardinality(RequiredSlots)
    /\ \A action \in AuthorityActions, slot \in RequiredSlots :
           GrantActionBinding[GrantForActionSlot[action][slot]] =
               ActionIdFor[action]

AcceptedCohortConsumesAndExhaustsExactlyAllSlots ==
    \A action \in AuthorityActions :
        decision[action] = "accepted" =>
            /\ \A slot \in RequiredSlots :
                   /\ grantUseCount[action][slot] = 1
                   /\ grantExhaustCount[action][slot] = 1
                   /\ grantState[action][slot] = "exhausted"

AuthorityStepDeltaIsAtomicOrNoop ==
    /\ (lastAuthorityStep = "accept" =>
           /\ lastUseDelta = RequiredSlots
           /\ lastExhaustDelta = RequiredSlots)
    /\ (lastAuthorityStep \in {"reject", "replay"} =>
           /\ lastUseDelta = {}
           /\ lastExhaustDelta = {})

GrantsAreSingleUse ==
    \A action \in AuthorityActions, slot \in RequiredSlots :
        /\ grantUseCount[action][slot] \leq 1
        /\ grantExhaustCount[action][slot] =
               grantUseCount[action][slot]

RejectedAndReplayStepsConsumeNothing ==
    /\ \A action \in AuthorityActions :
           decision[action] = "rejected" =>
               \A slot \in RequiredSlots :
                   grantUseCount[action][slot] = 0 /\
                       grantExhaustCount[action][slot] = 0
    /\ (lastAuthorityStep = "replay" =>
           lastUseDelta = {} /\ lastExhaustDelta = {})

OneCombinedReservationPerAcceptedRun ==
    /\ reservationCount \leq 1
    /\ (decision["assign"] = "accepted" => reservationCount = 1)
    /\ (decision["assign"] \in {"pending", "rejected"} =>
           reservationCount = 0)

AssignmentOwnsOneCombinedHoldUntilRace ==
    decision["assign"] = "accepted" /\
        ~startCommitted /\ ~preclaimTerminalEverCommitted =>
            /\ assignmentCommitted
            /\ reservationCount = 1
            /\ reservationState = "active"
            /\ held = Ceiling

AcceptedStartClaimsTheCombinedReservation ==
    decision["start"] = "accepted" =>
        /\ startCommitted
        /\ claimEverCommitted
        /\ reservationState \in {"claimed", "settled"}

ActiveOrClaimedReservationHoldsCombinedCeiling ==
    reservationState \in {"active", "claimed"} => held = Ceiling

TerminalReservationReleasesCombinedHold ==
    reservationState \in {"released", "expired", "settled"} =>
        held = ZeroHold

NoReleaseOrExpiryAfterClaim ==
    reservationState \in {"released", "expired"} => ~claimEverCommitted

StartCannotFollowPreclaimTerminal ==
    startCommitted => ~preclaimTerminalEverCommitted

ExactEvidenceOrExplicitAbsence ==
    /\ \A axis \in NonMoneyAxes :
           /\ (nonMoneyStatus[axis] = "exact" =>
                  nonMoneyActual[axis] \in 0..Ceiling[axis])
           /\ (nonMoneyStatus[axis] \in
                  {"unknown", "missing", "unavailable"} =>
                  nonMoneyActual[axis] = NoValue)
    /\ \A axis \in MoneyEvidenceAxes :
           /\ (moneyStatus[axis] = "exact" =>
                  moneyActual[axis] \in 0..Ceiling["money"])
           /\ (moneyStatus[axis] \in
                  {"unknown", "missing", "unavailable"} =>
                  moneyActual[axis] = NoValue)

SettlementRequiresExactEvidenceWithoutZeroInference ==
    /\ ~inferredZeroFromAbsence
    /\ ExactEvidenceOrExplicitAbsence
    /\ (reservationState = "settled" =>
           ExactNonMoneyEvidence /\ ExactMoneyEvidence)

=============================================================================
