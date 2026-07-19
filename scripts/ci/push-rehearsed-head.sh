#!/usr/bin/env bash
# Publish one exact Odeya architecture commit through the governed two-ref lane.
#
# candidate:
#   create release/<HEAD>, then require four exact push runs / ten green jobs.
# promote:
#   recheck the frozen candidate and live governance, fast-forward the same SHA
#   to main, require the new main runs, replay public main, compare evidence,
#   and retain the immutable release ref as server-protected provenance.
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly SCRIPT_ROOT
readonly EVIDENCE_ROOT="${ODEYA_EVIDENCE_ROOT:-/Users/danielwahnich/workspace/odeya-release-evidence}"
readonly REMOTE="${ODEYA_PUBLICATION_REMOTE:-origin}"
readonly CANONICAL_REMOTE_URL="https://github.com/manfromnowhere143/odeya.git"
readonly CANONICAL_SOURCE="https://github.com/manfromnowhere143/odeya"
readonly CANONICAL_SOURCE_SHA256="2d03b3f64ff40b9d376b227d8d67dc13c549c14b526ffb735f78f013d98f4924"
readonly MAIN_REF="refs/heads/main"
readonly RELEASE_PREFIX="refs/heads/release/"
readonly ZERO_SHA="0000000000000000000000000000000000000000"
readonly ACTIVATION_BOOTSTRAP_SHA="${ODEYA_ACTIVATION_BOOTSTRAP_SHA:-}"

canonical_git_read() (
  # Keep the publishing process's credential configuration intact while every
  # public read runs with the same isolated Git environment as a rehearsal.
  # shellcheck source=scripts/ci/sanitize-git-environment.sh
  source "$SCRIPT_ROOT/scripts/ci/sanitize-git-environment.sh"
  git -c http.sslVerify=true "$@"
)

usage() {
  printf 'Usage: %s candidate|promote|status|--self-test\n' "$0" >&2
  exit 2
}

candidate_governance_scope() {
  local existing_release_sha="$1"
  local prior_release_refs="$2"
  local other_release_refs="$3"
  if [[ -n "$existing_release_sha" && -z "$other_release_refs" ]] ||
     [[ -z "$prior_release_refs" ]]; then
    printf 'candidate-bootstrap\n'
  else
    printf 'full\n'
  fi
}

state_machine_self_test() {
  local rejected=0
  local current_row="current"
  local other_row="other"
  local combined_rows="current-and-other"
  local observed
  while IFS='|' read -r label existing prior other expected; do
    observed="$(candidate_governance_scope "$existing" "$prior" "$other")"
    if [[ "$observed" != "$expected" ]]; then
      printf 'Publication helper self-test %s: got %s, expected %s.\n' \
        "$label" "$observed" "$expected" >&2
      return 1
    fi
    rejected=$((rejected + 1))
  done <<CASES
first-create||||candidate-bootstrap
first-resume|a|${current_row}||candidate-bootstrap
later-create||${other_row}|${other_row}|full
later-resume|a|${combined_rows}|${other_row}|full
CASES
  printf 'Publication helper state self-test PASSED — %s states checked.\n' \
    "$rejected"
}

[[ "$#" -eq 1 ]] || usage
readonly MODE="$1"
if [[ "$MODE" == "--self-test" ]]; then
  state_machine_self_test
  exit 0
fi
[[ "$MODE" == "candidate" || "$MODE" == "promote" || "$MODE" == "status" ]] || usage

cd "$SCRIPT_ROOT"
COMMIT="$(git rev-parse HEAD)"
readonly COMMIT
readonly RELEASE_BRANCH="release/$COMMIT"
readonly RELEASE_REF="refs/heads/$RELEASE_BRANCH"
readonly LOCAL_EVIDENCE="$EVIDENCE_ROOT/$COMMIT"
readonly REMOTE_EVIDENCE="$EVIDENCE_ROOT/remote-main-$COMMIT"
readonly COMPARISON_RECEIPT="$EVIDENCE_ROOT/remote-main-comparison-$COMMIT.json"
readonly CANDIDATE_GOVERNANCE_RECEIPT="$EVIDENCE_ROOT/github-candidate-governance-$COMMIT.json"
readonly CANDIDATE_CHECKS_RECEIPT="$EVIDENCE_ROOT/github-candidate-checks-$COMMIT.json"
readonly PROMOTION_GOVERNANCE_RECEIPT="$EVIDENCE_ROOT/github-promotion-governance-$COMMIT.json"
readonly MAIN_CHECKS_RECEIPT="$EVIDENCE_ROOT/github-main-checks-$COMMIT.json"

remote_ref_sha() {
  local ref="$1"
  local advertisement
  advertisement="$(
    canonical_git_read ls-remote --refs "$CANONICAL_REMOTE_URL" "$ref"
  )"
  awk -v expected="$ref" '$2 == expected {print $1}' <<<"$advertisement"
}

require_publication_clone() {
  local configured_url
  local push_url
  configured_url="$(git remote get-url "$REMOTE")"
  push_url="$(git remote get-url --push "$REMOTE")"
  if [[ "$REMOTE" != "origin" ||
        "$configured_url" != "$CANONICAL_REMOTE_URL" ||
        "$push_url" != "$CANONICAL_REMOTE_URL" ]]; then
    printf 'Refusing publication: canonical origin identity is not exact.\n' >&2
    exit 3
  fi
  if git config --show-origin --get-regexp '^url\..*\.insteadof$' >/dev/null 2>&1; then
    printf 'Refusing publication: url.*.insteadOf can redirect transport.\n' >&2
    exit 3
  fi
  if [[ "$(git config --get core.hooksPath || true)" != ".githooks" ]]; then
    printf 'Refusing publication: core.hooksPath must equal .githooks.\n' >&2
    exit 3
  fi
  if [[ -n "$(git status --porcelain --untracked-files=all)" ]]; then
    printf 'Refusing publication: the worktree is not clean.\n' >&2
    exit 3
  fi
}

observe_main() {
  local advertised
  advertised="$(remote_ref_sha "$MAIN_REF")"
  if [[ ! "$advertised" =~ ^[0-9a-f]{40}$ ]]; then
    printf 'Refusing publication: canonical main has no exact identity.\n' >&2
    exit 4
  fi
  canonical_git_read -C "$SCRIPT_ROOT" fetch --quiet --no-tags "$REMOTE" \
    "$MAIN_REF:refs/remotes/origin/main"
  if [[ "$(git rev-parse refs/remotes/origin/main)" != "$advertised" ]]; then
    printf 'Refusing publication: main moved while its boundary was observed.\n' >&2
    exit 4
  fi
  printf '%s\n' "$advertised"
}

validate_candidate_against() {
  local main_sha="$1"
  local remote_release_sha="$2"
  python3 scripts/ci/validate_publication_sequence.py \
    --repo "$SCRIPT_ROOT" \
    --remote-ref "$RELEASE_REF" \
    --remote-sha "$remote_release_sha" \
    --local-sha "$COMMIT" \
    --main-sha "$main_sha" \
    --evidence-root "$EVIDENCE_ROOT"
}

verify_completed_main() {
  local subject_sha="$1"
  python3 scripts/compare_rehearsal_manifests.py \
    --verify-existing \
    --local "$EVIDENCE_ROOT/$subject_sha" \
    --remote "$EVIDENCE_ROOT/remote-main-$subject_sha" \
    --expected-remote-source-sha256 "$CANONICAL_SOURCE_SHA256" \
    --expected-subject-commit "$subject_sha" \
    --output "$EVIDENCE_ROOT/remote-main-comparison-$subject_sha.json"
}

show_status() {
  local main_sha
  local release_sha
  main_sha="$(remote_ref_sha "$MAIN_REF")"
  release_sha="$(remote_ref_sha "$RELEASE_REF")"
  printf 'HEAD:        %s\n' "$COMMIT"
  printf 'remote main: %s\n' "${main_sha:-absent}"
  printf 'candidate:   %s\n' "${release_sha:-absent}"
  if [[ "$main_sha" == "$COMMIT" ]]; then
    python3 scripts/ci/verify_github_release.py checks \
      --sha "$COMMIT" --branch main --timeout-seconds 1 --poll-seconds 1
  elif [[ "$release_sha" == "$COMMIT" ]]; then
    python3 scripts/ci/verify_github_release.py checks \
      --sha "$COMMIT" --branch "$RELEASE_BRANCH" \
      --timeout-seconds 1 --poll-seconds 1
  fi
}

if [[ "$MODE" == "status" ]]; then
  show_status
  exit 0
fi

require_publication_clone
main_sha="$(observe_main)"
readonly main_sha

if [[ "$MODE" == "candidate" ]]; then
  existing_release_sha="$(remote_ref_sha "$RELEASE_REF")"
  if [[ -n "$existing_release_sha" && "$existing_release_sha" != "$COMMIT" ]]; then
    printf 'Refusing candidate: %s unexpectedly resolves to %s.\n' \
      "$RELEASE_REF" "$existing_release_sha" >&2
    exit 5
  fi
  prior_release_refs="$(
    canonical_git_read ls-remote --refs \
      "$CANONICAL_REMOTE_URL" "${RELEASE_PREFIX}*"
  )"
  other_release_refs="$(
    awk -v current="$RELEASE_REF" '$2 != current {print}' \
      <<<"$prior_release_refs"
  )"
  if [[ -z "$existing_release_sha" ]]; then
    # A later candidate cannot overtake an incomplete publication.  Recompute
    # the exact local/remote receipt for the current main; a historical triplet
    # for any other subject does not satisfy this baton.
    verify_completed_main "$main_sha"
  fi
  governance_scope="$(
    candidate_governance_scope \
      "$existing_release_sha" "$prior_release_refs" "$other_release_refs"
  )"
  if [[ "$governance_scope" == "candidate-bootstrap" ]]; then
    # A first-candidate process may be resuming before the main ruleset is
    # activated.  This scope still requires the immutable-ref ruleset and all
    # account settings; if main exists it must be exact too.
    python3 scripts/ci/verify_github_release.py candidate-governance \
      --sha "$COMMIT" \
      --output "$CANDIDATE_GOVERNANCE_RECEIPT"
  else
    # After the first immutable candidate exists, removing the main ruleset is
    # a downgrade and no new candidate may be created.
    python3 scripts/ci/verify_github_release.py governance \
      --sha "$COMMIT" \
      --receipt-phase candidate \
      --output "$CANDIDATE_GOVERNANCE_RECEIPT"
  fi
  validate_candidate_against "$main_sha" "$ZERO_SHA"
  if [[ -z "$existing_release_sha" ]]; then
    printf 'Creating immutable candidate %s from %s.\n' "$RELEASE_REF" "$main_sha"
    git push "$REMOTE" "HEAD:$RELEASE_REF"
  else
    printf 'Resuming immutable candidate %s at its exact SHA.\n' "$RELEASE_REF"
  fi
  if [[ "$(remote_ref_sha "$RELEASE_REF")" != "$COMMIT" ]]; then
    printf 'Candidate push did not retain the exact commit.\n' >&2
    exit 6
  fi
  python3 scripts/ci/verify_github_release.py checks \
    --sha "$COMMIT" \
    --branch "$RELEASE_BRANCH" \
    --timeout-seconds 3600 \
    --poll-seconds 5 \
    --output "$CANDIDATE_CHECKS_RECEIPT"
  printf 'Candidate ready: %s passed four exact workflows and ten jobs.\n' "$COMMIT"
  exit 0
fi

release_sha="$(remote_ref_sha "$RELEASE_REF")"
if [[ "$release_sha" != "$COMMIT" ]]; then
  printf 'Refusing promotion: exact release candidate is absent or moved.\n' >&2
  exit 7
fi
parent_sha="$(git rev-parse "$COMMIT^")"
if [[ "$(git rev-list --count "$parent_sha..$COMMIT")" != "1" ||
      "$(git rev-list --parents -n 1 "$COMMIT" | wc -w | tr -d ' ')" != "2" ]]; then
  printf 'Refusing promotion: candidate is not one single-parent commit.\n' >&2
  exit 7
fi
validate_candidate_against "$parent_sha" "$ZERO_SHA"
python3 scripts/ci/verify_github_release.py governance \
  --sha "$COMMIT" \
  --receipt-phase promotion \
  --output "$PROMOTION_GOVERNANCE_RECEIPT"
python3 scripts/ci/verify_github_release.py checks \
  --sha "$COMMIT" \
  --branch "$RELEASE_BRANCH" \
  --timeout-seconds 1 \
  --poll-seconds 1 \
  --output "$CANDIDATE_CHECKS_RECEIPT"

if [[ "$main_sha" == "$parent_sha" ]]; then
  printf 'Promoting the already-checked SHA by direct fast-forward to main.\n'
  git push "$REMOTE" "HEAD:$MAIN_REF"
elif [[ "$main_sha" == "$COMMIT" ]]; then
  printf 'Resuming post-main verification for the exact promoted SHA.\n'
else
  printf 'Refusing promotion: main is neither the candidate parent nor candidate.\n' >&2
  exit 7
fi
if [[ "$(remote_ref_sha "$MAIN_REF")" != "$COMMIT" ]]; then
  printf 'Promotion failed: remote main is not the candidate SHA.\n' >&2
  exit 8
fi
python3 scripts/ci/verify_github_release.py checks \
  --sha "$COMMIT" \
  --branch main \
  --timeout-seconds 3600 \
  --poll-seconds 5 \
  --output "$MAIN_CHECKS_RECEIPT"

if [[ -e "$REMOTE_EVIDENCE" ]]; then
  if [[ -f "$REMOTE_EVIDENCE/failure-receipt.txt" ]]; then
    failed_evidence="$REMOTE_EVIDENCE.failed-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    printf 'Preserving prior failed remote replay at %s.\n' "$failed_evidence"
    mv -- "$REMOTE_EVIDENCE" "$failed_evidence"
  else
    PYTHONDONTWRITEBYTECODE=1 python3 - "$REMOTE_EVIDENCE" "$COMMIT" <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from compare_rehearsal_manifests import load_manifest

document, _ = load_manifest(Path(sys.argv[1]))
if (
    document.get("subject_commit") != sys.argv[2]
    or document.get("source_class") != "remote-main"
    or document.get("remote_main_commit") != sys.argv[2]
):
    raise SystemExit("existing remote-main evidence has the wrong subject or role")
print("Existing remote-main evidence revalidated for resume.")
PY
  fi
fi
if [[ ! -e "$REMOTE_EVIDENCE" ]]; then
  bash scripts/ci/rehearse-fresh-clone.sh \
    "$COMMIT" \
    "$CANONICAL_SOURCE" \
    "$REMOTE_EVIDENCE" \
    remote-main \
    "$CANONICAL_SOURCE_SHA256"
fi

if [[ -e "$COMPARISON_RECEIPT" || -L "$COMPARISON_RECEIPT" ]]; then
  python3 scripts/compare_rehearsal_manifests.py \
    --verify-existing \
    --local "$LOCAL_EVIDENCE" \
    --remote "$REMOTE_EVIDENCE" \
    --expected-remote-source-sha256 "$CANONICAL_SOURCE_SHA256" \
    --expected-subject-commit "$COMMIT" \
    --output "$COMPARISON_RECEIPT"
  printf 'Existing comparison receipt revalidated for resume.\n'
else
  python3 scripts/compare_rehearsal_manifests.py \
    --local "$LOCAL_EVIDENCE" \
    --remote "$REMOTE_EVIDENCE" \
    --expected-remote-source-sha256 "$CANONICAL_SOURCE_SHA256" \
    --expected-subject-commit "$COMMIT" \
    --output "$COMPARISON_RECEIPT"
fi

if [[ "$(remote_ref_sha "$RELEASE_REF")" != "$COMMIT" ]]; then
  printf 'Publication cannot complete: immutable candidate provenance moved.\n' >&2
  exit 10
fi
if [[ "$(remote_ref_sha "$MAIN_REF")" != "$COMMIT" ]]; then
  printf 'Publication cannot complete: canonical main moved before final settlement.\n' >&2
  exit 11
fi
if [[ -n "$ACTIVATION_BOOTSTRAP_SHA" ]]; then
  if [[ ! "$ACTIVATION_BOOTSTRAP_SHA" =~ ^[0-9a-f]{40}$ ||
        "$ACTIVATION_BOOTSTRAP_SHA" == "$COMMIT" ||
        "$ACTIVATION_BOOTSTRAP_SHA" == "$parent_sha" ]]; then
    printf 'Publication cannot settle activation: bootstrap SHA is not one distinct exact identity.\n' >&2
    exit 12
  fi
  readonly ACTIVATION_MUTATION_JOURNAL="$EVIDENCE_ROOT/github-governance-mutations-$ACTIVATION_BOOTSTRAP_SHA.json"
  readonly ACTIVATION_RECEIPT="$EVIDENCE_ROOT/github-activation-$COMMIT.json"
  python3 scripts/ci/verify_github_release.py activation-evidence \
    --base-sha "$parent_sha" \
    --bootstrap-sha "$ACTIVATION_BOOTSTRAP_SHA" \
    --sha "$COMMIT" \
    --mutation-journal "$ACTIVATION_MUTATION_JOURNAL" \
    --bootstrap-checks-receipt "$EVIDENCE_ROOT/github-candidate-checks-$ACTIVATION_BOOTSTRAP_SHA.json" \
    --candidate-checks-receipt "$CANDIDATE_CHECKS_RECEIPT" \
    --promotion-governance-receipt "$PROMOTION_GOVERNANCE_RECEIPT" \
    --main-checks-receipt "$MAIN_CHECKS_RECEIPT" \
    --comparison-receipt "$COMPARISON_RECEIPT" \
    --local-evidence "$LOCAL_EVIDENCE" \
    --remote-evidence "$REMOTE_EVIDENCE" \
    --output "$ACTIVATION_RECEIPT"
  printf 'Publication and GitHub activation COMPLETE for %s: exact main, three settled check censuses, remote replay/comparison, effective rules, and retained candidate refs.\n' \
    "$COMMIT"
else
  printf 'Publication COMPLETE for %s: exact main, ten green jobs, remote replay, comparison, retained candidate ref. No one-time GitHub activation claim was requested.\n' \
    "$COMMIT"
fi
