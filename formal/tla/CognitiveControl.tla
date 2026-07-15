---------------------------- MODULE CognitiveControl ----------------------------
EXTENDS Naturals, FiniteSets, TLC

(***************************************************************************)
(* Bounded Gate A model for cognitive-control admission.                   *)
(*                                                                         *)
(* The safe model permits real progress in four independent lanes:         *)
(* evidence may be dispositioned and qualified, verification capacity may  *)
(* be reserved and used, a producer-safe view may be compiled into an       *)
(* acyclic View -> Receipt -> Bundle identity chain, and a current bundle   *)
(* may be admitted for dispatch behind a separate data-access gate.         *)
(*                                                                         *)
(* View/Receipt/Bundle identities are abstract immutable tokens. The model  *)
(* checks their causal and reference order; it does not model hashing or    *)
(* claim cryptographic correctness. Fault constants are deliberate negative *)
(* controls only and are FALSE in the safe configuration.                  *)
(***************************************************************************)

CONSTANTS
    MaxPosition,
    FaultTruthLeak,
    FaultUndispositionedPromotion,
    FaultConsensusAsEvidence,
    FaultCapacityOvercommit,
    FaultStaleAdmission,
    FaultFailedCompilationAdmission,
    FaultNotRunCompilationAdmission,
    FaultMismatchedBundleAdmission,
    FaultUnissuedBundleAdmission,
    FaultDataAccessBypass

ASSUME /\ MaxPosition \in Nat \ {0}
       /\ FaultTruthLeak \in BOOLEAN
       /\ FaultUndispositionedPromotion \in BOOLEAN
       /\ FaultConsensusAsEvidence \in BOOLEAN
       /\ FaultCapacityOvercommit \in BOOLEAN
       /\ FaultStaleAdmission \in BOOLEAN
       /\ FaultFailedCompilationAdmission \in BOOLEAN
       /\ FaultNotRunCompilationAdmission \in BOOLEAN
       /\ FaultMismatchedBundleAdmission \in BOOLEAN
       /\ FaultUnissuedBundleAdmission \in BOOLEAN
       /\ FaultDataAccessBypass \in BOOLEAN

Evidence == {"primary", "counterevidence"}
MaterialEvidence == Evidence
DispositionStates == {"pending", "supports", "refutes",
                      "excluded_with_reason"}
ConsensusToken == "model_consensus"
EvidenceTokens == Evidence \cup {ConsensusToken}

(***************************************************************************)
(* These are the five non-fungible founding verification dimensions. Data  *)
(* access is intentionally absent: it is an admission gate, not capacity.  *)
(***************************************************************************)
Dimensions == {"deterministic", "compute", "expert", "physical", "safety"}
Capacity == [d \in Dimensions |-> 1]
VerificationDemand == [d \in Dimensions |-> 1]

Views == {"view_a", "view_b"}
Receipts == {"receipt_a", "receipt_b"}
NoView == "no_view"
NoReceipt == "no_receipt"
CompilationStates == {"absent", "pass", "failed", "not_run"}

ReceiptFor(v) == IF v = "view_a" THEN "receipt_a" ELSE "receipt_b"
OtherView(v) == IF v = "view_a" THEN "view_b" ELSE "view_a"
OtherReceipt(r) == IF r = "receipt_a" THEN "receipt_b" ELSE "receipt_a"

BindingNodes == {"view", "receipt", "bundle"}
BindingRank ==
    [n \in BindingNodes |->
        IF n = "view" THEN 0 ELSE IF n = "receipt" THEN 1 ELSE 2]
BindingEdges == {<<"receipt", "view">>,
                 <<"bundle", "view">>,
                 <<"bundle", "receipt">>}

VARIABLES
    truthVisibleToProducer,
    truthVisibleToVerifier,
    disposition,
    qualifyingEvidence,
    consensusRecorded,
    claimPromoted,
    reservedCapacity,
    verificationStarted,
    dataAccessAdmitted,
    canonicalPosition,
    authorityEpoch,
    viewCompiled,
    viewIdentityIssued,
    viewIdentity,
    viewPosition,
    viewAuthorityEpoch,
    compilationValidation,
    receiptIdentity,
    receiptViewIdentity,
    bundleIssued,
    bundleViewIdentity,
    bundleReceiptIdentity,
    dispatchAdmitted,
    admissionBundleViewIdentity,
    admissionBundleReceiptIdentity,
    admissionViewPosition,
    admissionViewAuthority,
    admissionCanonicalPosition,
    admissionCanonicalAuthority,
    admissionDataAccess

epistemicVars ==
    << truthVisibleToProducer, truthVisibleToVerifier, disposition,
       qualifyingEvidence, consensusRecorded, claimPromoted >>

capacityVars ==
    << reservedCapacity, verificationStarted, dataAccessAdmitted >>

positionVars == << canonicalPosition, authorityEpoch >>

compilationVars ==
    << viewCompiled, viewIdentityIssued, viewIdentity, viewPosition,
       viewAuthorityEpoch, compilationValidation, receiptIdentity,
       receiptViewIdentity, bundleIssued, bundleViewIdentity,
       bundleReceiptIdentity >>

admissionVars ==
    << dispatchAdmitted, admissionBundleViewIdentity,
       admissionBundleReceiptIdentity, admissionViewPosition,
       admissionViewAuthority, admissionCanonicalPosition,
       admissionCanonicalAuthority, admissionDataAccess >>

vars ==
    << epistemicVars, capacityVars, positionVars, compilationVars,
       admissionVars >>

Init ==
    /\ truthVisibleToProducer = FALSE
    /\ truthVisibleToVerifier = FALSE
    /\ disposition = [e \in Evidence |-> "pending"]
    /\ qualifyingEvidence = {}
    /\ consensusRecorded = FALSE
    /\ claimPromoted = FALSE
    /\ reservedCapacity = [d \in Dimensions |-> 0]
    /\ verificationStarted = FALSE
    /\ dataAccessAdmitted = FALSE
    /\ canonicalPosition = 0
    /\ authorityEpoch = 0
    /\ viewCompiled = FALSE
    /\ viewIdentityIssued = FALSE
    /\ viewIdentity = NoView
    /\ viewPosition = 0
    /\ viewAuthorityEpoch = 0
    /\ compilationValidation = "absent"
    /\ receiptIdentity = NoReceipt
    /\ receiptViewIdentity = NoView
    /\ bundleIssued = FALSE
    /\ bundleViewIdentity = NoView
    /\ bundleReceiptIdentity = NoReceipt
    /\ dispatchAdmitted = FALSE
    /\ admissionBundleViewIdentity = NoView
    /\ admissionBundleReceiptIdentity = NoReceipt
    /\ admissionViewPosition = 0
    /\ admissionViewAuthority = 0
    /\ admissionCanonicalPosition = 0
    /\ admissionCanonicalAuthority = 0
    /\ admissionDataAccess = FALSE

RevealTruthToVerifier ==
    /\ ~truthVisibleToVerifier
    /\ truthVisibleToVerifier' = TRUE
    /\ UNCHANGED
          << truthVisibleToProducer, disposition, qualifyingEvidence,
             consensusRecorded, claimPromoted, capacityVars, positionVars,
             compilationVars, admissionVars >>

LeakTruthToProducer ==
    /\ FaultTruthLeak
    /\ ~truthVisibleToProducer
    /\ truthVisibleToProducer' = TRUE
    /\ UNCHANGED
          << truthVisibleToVerifier, disposition, qualifyingEvidence,
             consensusRecorded, claimPromoted, capacityVars, positionVars,
             compilationVars, admissionVars >>

DispositionEvidence(e, outcome) ==
    /\ e \in Evidence
    /\ outcome \in DispositionStates \ {"pending"}
    /\ ~claimPromoted
    /\ disposition[e] = "pending"
    /\ disposition' = [disposition EXCEPT ![e] = outcome]
    /\ UNCHANGED
          << truthVisibleToProducer, truthVisibleToVerifier,
             qualifyingEvidence, consensusRecorded, claimPromoted,
             capacityVars, positionVars, compilationVars, admissionVars >>

QualifyGroundedEvidence(e) ==
    /\ e \in Evidence
    /\ ~claimPromoted
    /\ disposition[e] \in {"supports", "refutes"}
    /\ e \notin qualifyingEvidence
    /\ qualifyingEvidence' = qualifyingEvidence \cup {e}
    /\ UNCHANGED
          << truthVisibleToProducer, truthVisibleToVerifier, disposition,
             consensusRecorded, claimPromoted, capacityVars, positionVars,
             compilationVars, admissionVars >>

RecordConsensus ==
    /\ ~consensusRecorded
    /\ ~claimPromoted
    /\ consensusRecorded' = TRUE
    /\ qualifyingEvidence' =
          IF FaultConsensusAsEvidence
          THEN qualifyingEvidence \cup {ConsensusToken}
          ELSE qualifyingEvidence
    /\ UNCHANGED
          << truthVisibleToProducer, truthVisibleToVerifier, disposition,
             claimPromoted, capacityVars, positionVars, compilationVars,
             admissionVars >>

PromoteClaim ==
    /\ ~claimPromoted
    /\ qualifyingEvidence \cap Evidence # {}
    /\ IF FaultUndispositionedPromotion
          THEN \E e \in MaterialEvidence : disposition[e] = "pending"
          ELSE \A e \in MaterialEvidence : disposition[e] # "pending"
    /\ claimPromoted' = TRUE
    /\ UNCHANGED
          << truthVisibleToProducer, truthVisibleToVerifier, disposition,
             qualifyingEvidence, consensusRecorded, capacityVars,
             positionVars, compilationVars, admissionVars >>

ReserveDimension(d) ==
    /\ d \in Dimensions
    /\ ~verificationStarted
    /\ reservedCapacity[d] < Capacity[d]
    /\ reservedCapacity' = [reservedCapacity EXCEPT ![d] = @ + 1]
    /\ UNCHANGED
          << verificationStarted, dataAccessAdmitted, epistemicVars,
             positionVars, compilationVars, admissionVars >>

AdmitDataAccess ==
    /\ ~dataAccessAdmitted
    /\ ~dispatchAdmitted
    /\ dataAccessAdmitted' = TRUE
    /\ UNCHANGED
          << reservedCapacity, verificationStarted, epistemicVars,
             positionVars, compilationVars, admissionVars >>

BeginVerification ==
    /\ ~verificationStarted
    /\ dataAccessAdmitted
    /\ IF FaultCapacityOvercommit
          THEN \E d \in Dimensions :
                   VerificationDemand[d] > reservedCapacity[d]
          ELSE \A d \in Dimensions :
                   VerificationDemand[d] <= reservedCapacity[d]
    /\ verificationStarted' = TRUE
    /\ UNCHANGED
          << reservedCapacity, dataAccessAdmitted, epistemicVars,
             positionVars, compilationVars, admissionVars >>

BeginVerificationWithoutDataAccess ==
    /\ FaultDataAccessBypass
    /\ ~verificationStarted
    /\ ~dataAccessAdmitted
    /\ \A d \in Dimensions :
           VerificationDemand[d] <= reservedCapacity[d]
    /\ verificationStarted' = TRUE
    /\ UNCHANGED
          << reservedCapacity, dataAccessAdmitted, epistemicVars,
             positionVars, compilationVars, admissionVars >>

AdvanceCanonicalPosition ==
    /\ ~dispatchAdmitted
    /\ canonicalPosition < MaxPosition
    /\ canonicalPosition' = canonicalPosition + 1
    /\ UNCHANGED
          << authorityEpoch, epistemicVars, capacityVars, compilationVars,
             admissionVars >>

RotateAuthority ==
    /\ ~dispatchAdmitted
    /\ authorityEpoch < MaxPosition
    /\ authorityEpoch' = authorityEpoch + 1
    /\ UNCHANGED
          << canonicalPosition, epistemicVars, capacityVars, compilationVars,
             admissionVars >>

CompileView(v) ==
    /\ ~dispatchAdmitted
    /\ v \in Views
    /\ ( ~viewCompiled
         \/ viewPosition # canonicalPosition
         \/ viewAuthorityEpoch # authorityEpoch )
    /\ (~viewCompiled \/ v # viewIdentity)
    /\ viewCompiled' = TRUE
    /\ viewIdentityIssued' = FALSE
    /\ viewIdentity' = v
    /\ viewPosition' = canonicalPosition
    /\ viewAuthorityEpoch' = authorityEpoch
    /\ compilationValidation' = "absent"
    /\ receiptIdentity' = NoReceipt
    /\ receiptViewIdentity' = NoView
    /\ bundleIssued' = FALSE
    /\ bundleViewIdentity' = NoView
    /\ bundleReceiptIdentity' = NoReceipt
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, admissionVars >>

IssueViewIdentity ==
    /\ viewCompiled
    /\ ~viewIdentityIssued
    /\ viewIdentity \in Views
    /\ viewIdentityIssued' = TRUE
    /\ UNCHANGED
          << viewCompiled, viewIdentity, viewPosition, viewAuthorityEpoch,
             compilationValidation, receiptIdentity, receiptViewIdentity,
             bundleIssued, bundleViewIdentity, bundleReceiptIdentity,
             epistemicVars, capacityVars, positionVars, admissionVars >>

RecordCompilation(outcome) ==
    /\ outcome \in CompilationStates \ {"absent"}
    /\ viewIdentityIssued
    /\ compilationValidation = "absent"
    /\ compilationValidation' = outcome
    /\ receiptIdentity' = ReceiptFor(viewIdentity)
    /\ receiptViewIdentity' = viewIdentity
    /\ UNCHANGED
          << viewCompiled, viewIdentityIssued, viewIdentity, viewPosition,
             viewAuthorityEpoch, bundleIssued, bundleViewIdentity,
             bundleReceiptIdentity, epistemicVars, capacityVars,
             positionVars, admissionVars >>

IssueBundle ==
    /\ compilationValidation = "pass"
    /\ receiptIdentity \in Receipts
    /\ receiptViewIdentity = viewIdentity
    /\ ~bundleIssued
    /\ bundleIssued' = TRUE
    /\ bundleViewIdentity' = viewIdentity
    /\ bundleReceiptIdentity' = receiptIdentity
    /\ UNCHANGED
          << viewCompiled, viewIdentityIssued, viewIdentity, viewPosition,
             viewAuthorityEpoch, compilationValidation, receiptIdentity,
             receiptViewIdentity, epistemicVars, capacityVars, positionVars,
             dispatchAdmitted, admissionBundleViewIdentity,
             admissionBundleReceiptIdentity, admissionViewPosition,
             admissionViewAuthority, admissionCanonicalPosition,
             admissionCanonicalAuthority, admissionDataAccess >>

IssueMismatchedBundle ==
    /\ FaultMismatchedBundleAdmission
    /\ compilationValidation = "pass"
    /\ receiptIdentity \in Receipts
    /\ ~bundleIssued
    /\ bundleIssued' = TRUE
    /\ bundleViewIdentity' = OtherView(viewIdentity)
    /\ bundleReceiptIdentity' = OtherReceipt(receiptIdentity)
    /\ UNCHANGED
          << viewCompiled, viewIdentityIssued, viewIdentity, viewPosition,
             viewAuthorityEpoch, compilationValidation, receiptIdentity,
             receiptViewIdentity, epistemicVars, capacityVars, positionVars,
             admissionVars >>

CaptureAdmission ==
    /\ dispatchAdmitted' = TRUE
    /\ admissionBundleViewIdentity' = bundleViewIdentity
    /\ admissionBundleReceiptIdentity' = bundleReceiptIdentity
    /\ admissionViewPosition' = viewPosition
    /\ admissionViewAuthority' = viewAuthorityEpoch
    /\ admissionCanonicalPosition' = canonicalPosition
    /\ admissionCanonicalAuthority' = authorityEpoch
    /\ admissionDataAccess' = dataAccessAdmitted

AdmitDispatch ==
    /\ ~dispatchAdmitted
    /\ dataAccessAdmitted
    /\ viewCompiled
    /\ viewIdentityIssued
    /\ compilationValidation = "pass"
    /\ receiptIdentity \in Receipts
    /\ receiptViewIdentity = viewIdentity
    /\ bundleIssued
    /\ bundleViewIdentity = viewIdentity
    /\ bundleReceiptIdentity = receiptIdentity
    /\ viewPosition = canonicalPosition
    /\ viewAuthorityEpoch = authorityEpoch
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitStaleDispatch ==
    /\ FaultStaleAdmission
    /\ ~dispatchAdmitted
    /\ dataAccessAdmitted
    /\ compilationValidation = "pass"
    /\ bundleIssued
    /\ bundleViewIdentity = viewIdentity
    /\ bundleReceiptIdentity = receiptIdentity
    /\ (viewPosition # canonicalPosition \/
        viewAuthorityEpoch # authorityEpoch)
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitFailedCompilation ==
    /\ FaultFailedCompilationAdmission
    /\ ~dispatchAdmitted
    /\ compilationValidation = "failed"
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitNotRunCompilation ==
    /\ FaultNotRunCompilationAdmission
    /\ ~dispatchAdmitted
    /\ compilationValidation = "not_run"
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitWithoutBundle ==
    /\ FaultUnissuedBundleAdmission
    /\ ~dispatchAdmitted
    /\ compilationValidation = "pass"
    /\ ~bundleIssued
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitMismatchedBundle ==
    /\ FaultMismatchedBundleAdmission
    /\ ~dispatchAdmitted
    /\ compilationValidation = "pass"
    /\ bundleIssued
    /\ (bundleViewIdentity # viewIdentity \/
        bundleReceiptIdentity # receiptIdentity)
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

AdmitWithoutDataAccess ==
    /\ FaultDataAccessBypass
    /\ ~dispatchAdmitted
    /\ ~dataAccessAdmitted
    /\ compilationValidation = "pass"
    /\ bundleIssued
    /\ bundleViewIdentity = viewIdentity
    /\ bundleReceiptIdentity = receiptIdentity
    /\ viewPosition = canonicalPosition
    /\ viewAuthorityEpoch = authorityEpoch
    /\ CaptureAdmission
    /\ UNCHANGED << epistemicVars, capacityVars, positionVars, compilationVars >>

Next ==
    \/ RevealTruthToVerifier
    \/ LeakTruthToProducer
    \/ RecordConsensus
    \/ PromoteClaim
    \/ BeginVerification
    \/ BeginVerificationWithoutDataAccess
    \/ AdvanceCanonicalPosition
    \/ RotateAuthority
    \/ AdmitDataAccess
    \/ IssueViewIdentity
    \/ IssueBundle
    \/ IssueMismatchedBundle
    \/ AdmitDispatch
    \/ AdmitStaleDispatch
    \/ AdmitFailedCompilation
    \/ AdmitNotRunCompilation
    \/ AdmitWithoutBundle
    \/ AdmitMismatchedBundle
    \/ AdmitWithoutDataAccess
    \/ \E e \in Evidence,
          outcome \in DispositionStates \ {"pending"} :
             DispositionEvidence(e, outcome)
    \/ \E e \in Evidence : QualifyGroundedEvidence(e)
    \/ \E d \in Dimensions : ReserveDimension(d)
    \/ \E v \in Views : CompileView(v)
    \/ \E outcome \in CompilationStates \ {"absent"} :
             RecordCompilation(outcome)

Spec == Init /\ [][Next]_vars

TypeOK ==
    /\ truthVisibleToProducer \in BOOLEAN
    /\ truthVisibleToVerifier \in BOOLEAN
    /\ disposition \in [Evidence -> DispositionStates]
    /\ qualifyingEvidence \subseteq EvidenceTokens
    /\ consensusRecorded \in BOOLEAN
    /\ claimPromoted \in BOOLEAN
    /\ reservedCapacity \in [Dimensions -> 0..1]
    /\ verificationStarted \in BOOLEAN
    /\ dataAccessAdmitted \in BOOLEAN
    /\ canonicalPosition \in 0..MaxPosition
    /\ authorityEpoch \in 0..MaxPosition
    /\ viewCompiled \in BOOLEAN
    /\ viewIdentityIssued \in BOOLEAN
    /\ viewIdentity \in Views \cup {NoView}
    /\ viewPosition \in 0..MaxPosition
    /\ viewAuthorityEpoch \in 0..MaxPosition
    /\ compilationValidation \in CompilationStates
    /\ receiptIdentity \in Receipts \cup {NoReceipt}
    /\ receiptViewIdentity \in Views \cup {NoView}
    /\ bundleIssued \in BOOLEAN
    /\ bundleViewIdentity \in Views \cup {NoView}
    /\ bundleReceiptIdentity \in Receipts \cup {NoReceipt}
    /\ dispatchAdmitted \in BOOLEAN
    /\ admissionBundleViewIdentity \in Views \cup {NoView}
    /\ admissionBundleReceiptIdentity \in Receipts \cup {NoReceipt}
    /\ admissionViewPosition \in 0..MaxPosition
    /\ admissionViewAuthority \in 0..MaxPosition
    /\ admissionCanonicalPosition \in 0..MaxPosition
    /\ admissionCanonicalAuthority \in 0..MaxPosition
    /\ admissionDataAccess \in BOOLEAN

SealedTruthHiddenFromProducer ==
    ~truthVisibleToProducer

PromotionRequiresMaterialDisposition ==
    claimPromoted =>
        \A e \in MaterialEvidence : disposition[e] # "pending"

PromotionRequiresGroundedEvidence ==
    claimPromoted => qualifyingEvidence \cap Evidence # {}

ConsensusIsNotEvidence ==
    ConsensusToken \notin qualifyingEvidence

ReservedCapacityWithinLimits ==
    \A d \in Dimensions : reservedCapacity[d] <= Capacity[d]

VerificationDemandWithinReservation ==
    verificationStarted =>
        \A d \in Dimensions :
            VerificationDemand[d] <= reservedCapacity[d]

VerificationRequiresDataAccess ==
    verificationStarted => dataAccessAdmitted

ReceiptFollowsIssuedView ==
    receiptIdentity # NoReceipt =>
        /\ viewCompiled
        /\ viewIdentityIssued
        /\ receiptViewIdentity = viewIdentity
        /\ receiptIdentity = ReceiptFor(viewIdentity)

BundleRequiresPassedReceipt ==
    bundleIssued =>
        /\ compilationValidation = "pass"
        /\ receiptIdentity \in Receipts
        /\ bundleViewIdentity = viewIdentity
        /\ bundleReceiptIdentity = receiptIdentity

DispatchAdmissionBindsPassedIssuedBundle ==
    dispatchAdmitted =>
        /\ viewCompiled
        /\ viewIdentityIssued
        /\ compilationValidation = "pass"
        /\ receiptIdentity \in Receipts
        /\ receiptViewIdentity = viewIdentity
        /\ bundleIssued
        /\ bundleViewIdentity = viewIdentity
        /\ bundleReceiptIdentity = receiptIdentity
        /\ admissionBundleViewIdentity = bundleViewIdentity
        /\ admissionBundleReceiptIdentity = bundleReceiptIdentity

DispatchAdmissionUsesCurrentPositionAndAuthority ==
    dispatchAdmitted =>
        /\ admissionViewPosition = admissionCanonicalPosition
        /\ admissionViewAuthority = admissionCanonicalAuthority

DispatchAdmissionRequiresDataAccess ==
    dispatchAdmitted => admissionDataAccess

BindingDependencyGraphIsAcyclic ==
    /\ DOMAIN BindingRank = BindingNodes
    /\ \A edge \in BindingEdges :
           BindingRank[edge[2]] < BindingRank[edge[1]]

=============================================================================
