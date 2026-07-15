#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly JAR="${TLA2TOOLS_JAR:-/tmp/odeya-tla/v1.7.4/tla2tools.jar}"
readonly EXPECTED_JAR_SHA256="936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
readonly RUN_ROOT="${TMPDIR:-/tmp}/odeya-tla-check-$$"

cleanup_run_root() {
  rm -rf -- "$RUN_ROOT"
}

trap cleanup_run_root EXIT

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

if [[ ! -f "$JAR" ]]; then
  printf 'Missing pinned TLC jar: %s\n' "$JAR" >&2
  printf 'Follow formal/tla/README.md; no binary is vendored.\n' >&2
  exit 2
fi

actual_sha256="$(sha256_file "$JAR")"
if [[ "$actual_sha256" != "$EXPECTED_JAR_SHA256" ]]; then
  printf 'TLC digest mismatch: expected %s, got %s\n' \
    "$EXPECTED_JAR_SHA256" "$actual_sha256" >&2
  exit 3
fi

mkdir -p "$RUN_ROOT"
cd "$ROOT"

java -cp "$JAR" tla2sany.SANY \
  AuthorityCommandGrant.tla \
  GrantConsumptionPoint.tla \
  ExternalEffects.tla \
  PublicationRelease.tla \
  CognitiveControl.tla \
  ResourceReservation.tla

run_tlc() {
  local expectation="$1"
  local name="$2"
  local module="$3"
  local config="$4"
  local invariant="${5:-}"
  local seed="${6:-20260715}"
  local fingerprint_polynomial="${7:-0}"
  local output
  local code

  set +e
  output="$(java -XX:+UseParallelGC -jar "$JAR" \
    -workers 1 \
    -seed "$seed" \
    -fp "$fingerprint_polynomial" \
    -cleanup \
    -metadir "$RUN_ROOT/$name" \
    -config "$config" \
    "$module" 2>&1)"
  code=$?
  set -e

  printf '\n===== %s (%s, exit %s) =====\n%s\n' \
    "$name" "$expectation" "$code" "$output"

  if [[ "$expectation" == "pass" ]]; then
    if [[ "$code" -ne 0 ]] ||
       [[ "$output" != *"Model checking completed. No error has been found."* ]]; then
      printf 'Unexpected safe-model result for %s.\n' "$name" >&2
      exit 10
    fi
  else
    if [[ "$code" -ne 12 ]] ||
       [[ "$output" != *"Invariant $invariant is violated."* ]]; then
      printf 'Expected counterexample %s was not reproduced for %s.\n' \
        "$invariant" "$name" >&2
      exit 11
    fi
  fi
}

run_tlc pass authority-safe \
  AuthorityCommandGrant.tla AuthorityCommandGrant.safe.cfg
run_tlc counterexample authority-weak-quorum \
  AuthorityCommandGrant.tla \
  AuthorityCommandGrant.weak-quorum.counterexample.cfg \
  EveryUseWasAuthorized
run_tlc counterexample authority-digest-rebind \
  AuthorityCommandGrant.tla \
  AuthorityCommandGrant.digest-rebind.counterexample.cfg \
  IdempotentCommandBinding
run_tlc counterexample authority-post-revoke-use \
  AuthorityCommandGrant.tla \
  AuthorityCommandGrant.post-revoke-use.counterexample.cfg \
  EveryUseWasAuthorized

run_tlc pass consumption-point-safe \
  GrantConsumptionPoint.tla GrantConsumptionPoint.safe.cfg
run_tlc counterexample consumption-at-intent \
  GrantConsumptionPoint.tla \
  GrantConsumptionPoint.consume-at-intent.counterexample.cfg \
  DispatchClaimRechecksAndConsumes

run_tlc pass effects-safe ExternalEffects.tla ExternalEffects.safe.cfg
run_tlc counterexample effects-post-revoke-dispatch \
  ExternalEffects.tla \
  ExternalEffects.post-revoke-dispatch.counterexample.cfg \
  NoDispatchAfterRevocationOrExpiry
run_tlc counterexample effects-blind-retry \
  ExternalEffects.tla ExternalEffects.blind-retry.counterexample.cfg \
  NoUnsafeRetry

run_tlc pass publication-safe \
  PublicationRelease.tla PublicationRelease.safe.cfg
run_tlc counterexample publication-no-decision-seal \
  PublicationRelease.tla \
  PublicationRelease.no-decision-seal.counterexample.cfg \
  ManifestWasSealedFromAuthorizedCandidate
run_tlc counterexample publication-wrong-manifest \
  PublicationRelease.tla \
  PublicationRelease.wrong-manifest-grant.counterexample.cfg \
  GrantBindsExactFinalManifest
run_tlc counterexample publication-grant-reuse \
  PublicationRelease.tla \
  PublicationRelease.grant-reuse.counterexample.cfg \
  PublicationGrantIsSingleUse
run_tlc counterexample publication-timeout-release \
  PublicationRelease.tla \
  PublicationRelease.timeout-release.counterexample.cfg \
  ReleasedRequiresExactExternalObservation
run_tlc counterexample publication-visibility-only-release \
  PublicationRelease.tla \
  PublicationRelease.visibility-only-release.counterexample.cfg \
  ReleasedRequiresExactExternalObservation
run_tlc counterexample publication-missing-dispute \
  PublicationRelease.tla \
  PublicationRelease.missing-dispute.counterexample.cfg \
  ContradictoryExternalFactsRequireDispute

run_tlc pass cognitive-control-safe \
  CognitiveControl.tla CognitiveControl.safe.cfg
run_tlc pass cognitive-control-safe-alternate-fingerprint \
  CognitiveControl.tla CognitiveControl.safe.cfg "" 20260716 1
run_tlc counterexample cognitive-control-truth-leak \
  CognitiveControl.tla \
  CognitiveControl.truth-leak.counterexample.cfg \
  SealedTruthHiddenFromProducer
run_tlc counterexample cognitive-control-undispositioned-promotion \
  CognitiveControl.tla \
  CognitiveControl.undispositioned-promotion.counterexample.cfg \
  PromotionRequiresMaterialDisposition
run_tlc counterexample cognitive-control-consensus-as-evidence \
  CognitiveControl.tla \
  CognitiveControl.consensus-as-evidence.counterexample.cfg \
  ConsensusIsNotEvidence
run_tlc counterexample cognitive-control-capacity-overcommit \
  CognitiveControl.tla \
  CognitiveControl.capacity-overcommit.counterexample.cfg \
  VerificationDemandWithinReservation
run_tlc counterexample cognitive-control-stale-view-admission \
  CognitiveControl.tla \
  CognitiveControl.stale-view-admission.counterexample.cfg \
  DispatchAdmissionUsesCurrentPositionAndAuthority
run_tlc counterexample cognitive-control-failed-compilation-admission \
  CognitiveControl.tla \
  CognitiveControl.failed-compilation-admission.counterexample.cfg \
  DispatchAdmissionBindsPassedIssuedBundle
run_tlc counterexample cognitive-control-not-run-compilation-admission \
  CognitiveControl.tla \
  CognitiveControl.not-run-compilation-admission.counterexample.cfg \
  DispatchAdmissionBindsPassedIssuedBundle
run_tlc counterexample cognitive-control-mismatched-bundle-admission \
  CognitiveControl.tla \
  CognitiveControl.mismatched-bundle-admission.counterexample.cfg \
  DispatchAdmissionBindsPassedIssuedBundle
run_tlc counterexample cognitive-control-unissued-bundle-admission \
  CognitiveControl.tla \
  CognitiveControl.unissued-bundle-admission.counterexample.cfg \
  DispatchAdmissionBindsPassedIssuedBundle
run_tlc counterexample cognitive-control-data-access-bypass \
  CognitiveControl.tla \
  CognitiveControl.data-access-bypass.counterexample.cfg \
  VerificationRequiresDataAccess

run_tlc pass resource-reservation-safe \
  ResourceReservation.tla ResourceReservation.safe.cfg
run_tlc counterexample resource-cross-resource-conversion \
  ResourceReservation.tla \
  ResourceReservation.cross-resource-conversion.counterexample.cfg \
  NoDimensionOvercommit
run_tlc counterexample resource-release-claimed-on-crash \
  ResourceReservation.tla \
  ResourceReservation.crash-release.counterexample.cfg \
  TerminalReleaseWasPreClaim
run_tlc counterexample resource-settle-without-observation \
  ResourceReservation.tla \
  ResourceReservation.settle-without-observation.counterexample.cfg \
  SettlementRequiresObservation
run_tlc counterexample resource-infer-actual-at-claim \
  ResourceReservation.tla \
  ResourceReservation.infer-actual-at-claim.counterexample.cfg \
  ClaimDoesNotInventActualUse

printf '\nAll six distinct safe models passed; the cognitive model also passed under the retained alternate fingerprint profile; all twenty-six negative controls produced the expected counterexample.\n'
