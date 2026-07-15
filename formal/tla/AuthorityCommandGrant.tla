-------------------------- MODULE AuthorityCommandGrant --------------------------
EXTENDS Naturals, FiniteSets, TLC

(***************************************************************************)
(* Bounded Gate A model of command identity, grant capacity, and quorum.   *)
(* The grant begins unissued and all transitions are canonical commits.     *)
(* Fault constants exist only so negative configs can prove that the        *)
(* invariants are capable of finding the intended defects.                  *)
(***************************************************************************)

CONSTANTS
    CommandIds,
    Digests,
    Principals,
    AliasA,
    AliasB,
    Independent,
    NoDigest,
    NoTime,
    MaxUses,
    RequiredQuorum,
    ExpiresAt,
    MaxTime,
    FaultWeakQuorum,
    FaultDigestRebind,
    FaultUseAfterRevocation

ASSUME /\ CommandIds # {}
       /\ Digests # {}
       /\ AliasA \in Principals
       /\ AliasB \in Principals
       /\ Independent \in Principals
       /\ AliasA # AliasB
       /\ Independent # AliasA
       /\ Independent # AliasB
       /\ NoDigest \notin Digests
       /\ MaxUses \in Nat \ {0}
       /\ RequiredQuorum \in Nat \ {0}
       /\ ExpiresAt \in Nat \ {0}
       /\ MaxTime \in Nat
       /\ MaxTime >= ExpiresAt
       /\ FaultWeakQuorum \in BOOLEAN
       /\ FaultDigestRebind \in BOOLEAN
       /\ FaultUseAfterRevocation \in BOOLEAN

GrantStates == {"not_issued", "issued", "active", "exhausted",
                "expired", "revoked"}
ReservationStates == {"none", "reserved", "released", "consumed"}
ReceiptResults == {"none", "accepted", "rejected"}

EffectivePrincipal(p) == IF p = AliasB THEN AliasA ELSE p

VARIABLES
    grantState,
    now,
    reservationState,
    reservationDigest,
    approvals,
    receiptDigest,
    receiptResult,
    executionCount,
    executedDigests,
    useTime,
    useGrantState,
    frozenEffectiveApprovers,
    conflicts,
    postTerminalUse

vars == << grantState, now, reservationState, reservationDigest, approvals,
           receiptDigest, receiptResult, executionCount, executedDigests,
           useTime, useGrantState, frozenEffectiveApprovers, conflicts,
           postTerminalUse >>

EffectiveApprovers(c) ==
    {EffectivePrincipal(p) : p \in approvals[c]}

RawQuorum(c) == Cardinality(approvals[c]) >= RequiredQuorum
EffectiveQuorum(c) ==
    Cardinality(EffectiveApprovers(c)) >= RequiredQuorum
QuorumPermits(c) ==
    IF FaultWeakQuorum THEN RawQuorum(c) ELSE EffectiveQuorum(c)

UsedCount ==
    Cardinality({c \in CommandIds : reservationState[c] = "consumed"})
ReservedCount ==
    Cardinality({c \in CommandIds : reservationState[c] = "reserved"})

Init ==
    /\ grantState = "not_issued"
    /\ now = 0
    /\ reservationState = [c \in CommandIds |-> "none"]
    /\ reservationDigest = [c \in CommandIds |-> NoDigest]
    /\ approvals = [c \in CommandIds |-> {}]
    /\ receiptDigest = [c \in CommandIds |-> NoDigest]
    /\ receiptResult = [c \in CommandIds |-> "none"]
    /\ executionCount = [c \in CommandIds |-> 0]
    /\ executedDigests = [c \in CommandIds |-> {}]
    /\ useTime = [c \in CommandIds |-> NoTime]
    /\ useGrantState = [c \in CommandIds |-> "not_issued"]
    /\ frozenEffectiveApprovers = [c \in CommandIds |-> {}]
    /\ conflicts = {}
    /\ postTerminalUse = FALSE

IssueGrant ==
    /\ grantState = "not_issued"
    /\ grantState' = "issued"
    /\ UNCHANGED << now, reservationState, reservationDigest, approvals,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

ActivateGrant ==
    /\ grantState = "issued"
    /\ now < ExpiresAt
    /\ grantState' = "active"
    /\ UNCHANGED << now, reservationState, reservationDigest, approvals,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

Approve(c, p) ==
    /\ c \in CommandIds
    /\ p \in Principals
    /\ receiptResult[c] = "none"
    /\ reservationState[c] # "consumed"
    /\ approvals' = [approvals EXCEPT ![c] = @ \cup {p}]
    /\ UNCHANGED << grantState, now, reservationState, reservationDigest,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

Reserve(c, d) ==
    /\ c \in CommandIds
    /\ d \in Digests
    /\ grantState = "active"
    /\ now < ExpiresAt
    /\ receiptResult[c] = "none"
    /\ reservationState[c] \in {"none", "released"}
    /\ (reservationState[c] = "released" => reservationDigest[c] = d)
    /\ UsedCount + ReservedCount < MaxUses
    /\ reservationState' = [reservationState EXCEPT ![c] = "reserved"]
    /\ reservationDigest' = [reservationDigest EXCEPT ![c] = d]
    /\ UNCHANGED << grantState, now, approvals, receiptDigest,
                    receiptResult, executionCount, executedDigests, useTime,
                    useGrantState, frozenEffectiveApprovers, conflicts,
                    postTerminalUse >>

Release(c) ==
    /\ c \in CommandIds
    /\ reservationState[c] = "reserved"
    /\ reservationState' = [reservationState EXCEPT ![c] = "released"]
    /\ UNCHANGED << grantState, now, reservationDigest, approvals,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

RejectNew(c, d) ==
    /\ c \in CommandIds
    /\ d \in Digests
    /\ receiptResult[c] = "none"
    /\ reservationState[c] \in {"none", "released"}
    /\ receiptDigest' = [receiptDigest EXCEPT ![c] = d]
    /\ receiptResult' = [receiptResult EXCEPT ![c] = "rejected"]
    /\ UNCHANGED << grantState, now, reservationState, reservationDigest,
                    approvals, executionCount, executedDigests, useTime,
                    useGrantState, frozenEffectiveApprovers, conflicts,
                    postTerminalUse >>

UseAndCommit(c, d) ==
    /\ c \in CommandIds
    /\ d \in Digests
    /\ reservationState[c] = "reserved"
    /\ reservationDigest[c] = d
    /\ receiptResult[c] = "none"
    /\ UsedCount < MaxUses
    /\ QuorumPermits(c)
    /\ (grantState = "active" \/
        (FaultUseAfterRevocation /\ grantState \in {"revoked", "expired"}))
    /\ (grantState # "active" \/ now < ExpiresAt)
    /\ reservationState' = [reservationState EXCEPT ![c] = "consumed"]
    /\ receiptDigest' = [receiptDigest EXCEPT ![c] = d]
    /\ receiptResult' = [receiptResult EXCEPT ![c] = "accepted"]
    /\ executionCount' = [executionCount EXCEPT ![c] = @ + 1]
    /\ executedDigests' = [executedDigests EXCEPT ![c] = @ \cup {d}]
    /\ useTime' = [useTime EXCEPT ![c] = now]
    /\ useGrantState' = [useGrantState EXCEPT ![c] = grantState]
    /\ frozenEffectiveApprovers' =
          [frozenEffectiveApprovers EXCEPT ![c] = EffectiveApprovers(c)]
    /\ grantState' =
          IF grantState = "active" /\ UsedCount + 1 = MaxUses
          THEN "exhausted"
          ELSE grantState
    /\ postTerminalUse' = postTerminalUse \/ grantState # "active"
    /\ UNCHANGED << now, reservationDigest, approvals, conflicts >>

RecordConflict(c, d) ==
    /\ c \in CommandIds
    /\ d \in Digests
    /\ receiptResult[c] # "none"
    /\ d # receiptDigest[c]
    /\ conflicts' = conflicts \cup {[command |-> c, digest |-> d]}
    /\ UNCHANGED << grantState, now, reservationState, reservationDigest,
                    approvals, receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, postTerminalUse >>

FaultRebind(c, d) ==
    /\ FaultDigestRebind
    /\ c \in CommandIds
    /\ d \in Digests
    /\ receiptResult[c] = "accepted"
    /\ d # receiptDigest[c]
    /\ receiptDigest' = [receiptDigest EXCEPT ![c] = d]
    /\ executionCount' = [executionCount EXCEPT ![c] = @ + 1]
    /\ executedDigests' = [executedDigests EXCEPT ![c] = @ \cup {d}]
    /\ UNCHANGED << grantState, now, reservationState, reservationDigest,
                    approvals, receiptResult, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

RevokeGrant ==
    /\ grantState \in {"issued", "active"}
    /\ grantState' = "revoked"
    /\ UNCHANGED << now, reservationState, reservationDigest, approvals,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

ObserveExpiry ==
    /\ grantState \in {"issued", "active"}
    /\ now >= ExpiresAt
    /\ grantState' = "expired"
    /\ UNCHANGED << now, reservationState, reservationDigest, approvals,
                    receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

Tick ==
    /\ now < MaxTime
    /\ now' = now + 1
    /\ UNCHANGED << grantState, reservationState, reservationDigest,
                    approvals, receiptDigest, receiptResult, executionCount,
                    executedDigests, useTime, useGrantState,
                    frozenEffectiveApprovers, conflicts, postTerminalUse >>

Next ==
    \/ IssueGrant
    \/ ActivateGrant
    \/ RevokeGrant
    \/ ObserveExpiry
    \/ Tick
    \/ \E c \in CommandIds, p \in Principals : Approve(c, p)
    \/ \E c \in CommandIds, d \in Digests : Reserve(c, d)
    \/ \E c \in CommandIds : Release(c)
    \/ \E c \in CommandIds, d \in Digests : RejectNew(c, d)
    \/ \E c \in CommandIds, d \in Digests : UseAndCommit(c, d)
    \/ \E c \in CommandIds, d \in Digests : RecordConflict(c, d)
    \/ \E c \in CommandIds, d \in Digests : FaultRebind(c, d)

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ grantState \in GrantStates
    /\ now \in 0..MaxTime
    /\ reservationState \in [CommandIds -> ReservationStates]
    /\ reservationDigest \in [CommandIds -> Digests \cup {NoDigest}]
    /\ approvals \in [CommandIds -> SUBSET Principals]
    /\ receiptDigest \in [CommandIds -> Digests \cup {NoDigest}]
    /\ receiptResult \in [CommandIds -> ReceiptResults]
    /\ executionCount \in [CommandIds -> 0..2]
    /\ executedDigests \in [CommandIds -> SUBSET Digests]
    /\ useTime \in [CommandIds -> (0..MaxTime) \cup {NoTime}]
    /\ useGrantState \in [CommandIds -> GrantStates]
    /\ frozenEffectiveApprovers \in
          [CommandIds -> SUBSET {EffectivePrincipal(p) : p \in Principals}]
    /\ conflicts \subseteq [command : CommandIds, digest : Digests]
    /\ postTerminalUse \in BOOLEAN

IdempotentCommandBinding ==
    \A c \in CommandIds :
        /\ (receiptResult[c] = "none") = (receiptDigest[c] = NoDigest)
        /\ (receiptResult[c] = "accepted") =>
              /\ executionCount[c] = 1
              /\ executedDigests[c] = {receiptDigest[c]}
        /\ (receiptResult[c] = "rejected") =>
              /\ executionCount[c] = 0
              /\ executedDigests[c] = {}

ConflictPreservesOriginalBinding ==
    \A x \in conflicts : x.digest # receiptDigest[x.command]

GrantCapacitySafe ==
    /\ UsedCount <= MaxUses
    /\ UsedCount + ReservedCount <= MaxUses

EveryUseWasAuthorized ==
    \A c \in CommandIds :
        reservationState[c] = "consumed" =>
            /\ useGrantState[c] = "active"
            /\ useTime[c] # NoTime
            /\ useTime[c] < ExpiresAt
            /\ Cardinality(frozenEffectiveApprovers[c]) >= RequiredQuorum

NoPostTerminalUse == ~postTerminalUse

================================================================================
