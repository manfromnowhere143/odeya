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

validate_candidate_against() {
  local candidate_main_sha="$1"
  local candidate_remote_release_sha="$2"
  python3 scripts/ci/validate_publication_sequence.py \
    --repo "$SCRIPT_ROOT" \
    --remote-ref "$RELEASE_REF" \
    --remote-sha "$candidate_remote_release_sha" \
    --local-sha "$COMMIT" \
    --main-sha "$candidate_main_sha" \
    --evidence-root "$EVIDENCE_ROOT"
}

publication_source_ref() {
  local observed_source_ref
  local observed_source_sha
  if ! observed_source_ref="$(git symbolic-ref --quiet HEAD)"; then
    printf 'Refusing publication: HEAD must be attached to one local branch.\n' >&2
    return 1
  fi
  if [[ "$observed_source_ref" != refs/heads/* ]]; then
    printf 'Refusing publication: source is not an exact local branch ref.\n' >&2
    return 1
  fi
  if ! observed_source_sha="$(
    git rev-parse --verify "${observed_source_ref}^{commit}"
  )"; then
    printf 'Refusing publication: source branch has no exact commit.\n' >&2
    return 1
  fi
  if [[ "$observed_source_sha" != "$COMMIT" ]]; then
    printf 'Refusing publication: source branch no longer resolves to HEAD.\n' >&2
    return 1
  fi
  printf '%s\n' "$observed_source_ref"
}

require_publication_source_ref() {
  local observed_source_ref
  if ! observed_source_ref="$(publication_source_ref)"; then
    return 1
  fi
  if [[ "$observed_source_ref" != "$SOURCE_REF" ]]; then
    printf 'Refusing publication: attached source branch changed before push.\n' >&2
    return 1
  fi
}

push_governed_ref() {
  local destination_ref="$1"
  if ! require_publication_source_ref; then
    return 1
  fi
  ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="$SOURCE_REF" \
    ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="$COMMIT" \
    git push "$REMOTE" "$SOURCE_REF:$destination_ref"
}

require_clean_worktree() {
  local worktree_state
  if ! worktree_state="$(git status --porcelain --untracked-files=all)"; then
    printf 'Refusing publication: worktree status could not be observed.\n' >&2
    return 1
  fi
  if [[ -n "$worktree_state" ]]; then
    printf 'Refusing publication: the worktree is not clean.\n' >&2
    return 1
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

validator_scope_self_test() (
  local -r COMMIT="2222222222222222222222222222222222222222"
  local -r RELEASE_REF="refs/heads/release/$COMMIT"
  local -r main_sha="1111111111111111111111111111111111111111"
  local invocation_count=0

  python3() {
    local -a expected=(
      "scripts/ci/validate_publication_sequence.py"
      "--repo"
      "$SCRIPT_ROOT"
      "--remote-ref"
      "$RELEASE_REF"
      "--remote-sha"
      "$ZERO_SHA"
      "--local-sha"
      "$COMMIT"
      "--main-sha"
      "$main_sha"
      "--evidence-root"
      "$EVIDENCE_ROOT"
    )
    local -a observed=("$@")
    local index
    if [[ "${#observed[@]}" -ne "${#expected[@]}" ]]; then
      printf 'Publication helper validator-scope self-test: wrong argument count.\n' >&2
      return 1
    fi
    for index in "${!expected[@]}"; do
      if [[ "${observed[$index]}" != "${expected[$index]}" ]]; then
        printf 'Publication helper validator-scope self-test: argument %s drifted.\n' \
          "$index" >&2
        return 1
      fi
    done
    invocation_count=$((invocation_count + 1))
  }

  validate_candidate_against "$main_sha" "$ZERO_SHA"
  if [[ "$invocation_count" -ne 1 ]]; then
    printf 'Publication helper validator-scope self-test: validator call count drifted.\n' >&2
    return 1
  fi
  printf 'Publication helper validator-scope self-test PASSED — exact readonly caller scope exercised.\n'
)

source_ref_self_test() (
  local -r COMMIT="3333333333333333333333333333333333333333"
  local -r SOURCE_REF="refs/heads/fixture"
  local -r RELEASE_REF="refs/heads/release/$COMMIT"
  local observed_ref="$SOURCE_REF"
  local observed_sha="$COMMIT"
  local detached=0
  local push_count=0
  local push_arguments=""
  local push_expected_source_ref=""
  local push_expected_source_sha=""

  git() {
    local operation="$1"
    shift
    case "$operation" in
      symbolic-ref)
        if [[ "$#" -ne 2 || "$1" != "--quiet" || "$2" != "HEAD" ]]; then
          return 91
        fi
        if [[ "$detached" -eq 1 ]]; then
          return 1
        fi
        printf '%s\n' "$observed_ref"
        ;;
      rev-parse)
        if [[ "$#" -ne 2 || "$1" != "--verify" ||
              "$2" != "${observed_ref}^{commit}" ]]; then
          return 92
        fi
        printf '%s\n' "$observed_sha"
        ;;
      push)
        push_count=$((push_count + 1))
        push_arguments="$*"
        push_expected_source_ref="${ODEYA_EXPECTED_PUBLICATION_SOURCE_REF:-}"
        push_expected_source_sha="${ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA:-}"
        ;;
      *)
        return 93
        ;;
    esac
  }

  push_governed_ref "$RELEASE_REF"
  if [[ "$push_count" -ne 1 ||
        "$push_arguments" != "$REMOTE $SOURCE_REF:$RELEASE_REF" ||
        "$push_expected_source_ref" != "$SOURCE_REF" ||
        "$push_expected_source_sha" != "$COMMIT" ]]; then
    printf 'Publication helper source-ref self-test: frozen push tuple drifted.\n' >&2
    return 1
  fi

  detached=1
  if push_governed_ref "$RELEASE_REF" 2>/dev/null; then
    printf 'Publication helper source-ref self-test: detached HEAD was accepted.\n' >&2
    return 1
  fi
  detached=0
  if [[ "$push_count" -ne 1 ]]; then
    printf 'Publication helper source-ref self-test: detached HEAD reached push.\n' >&2
    return 1
  fi

  observed_ref="refs/heads/other"
  if push_governed_ref "$RELEASE_REF" 2>/dev/null; then
    printf 'Publication helper source-ref self-test: changed branch was accepted.\n' >&2
    return 1
  fi
  observed_ref="$SOURCE_REF"
  if [[ "$push_count" -ne 1 ]]; then
    printf 'Publication helper source-ref self-test: changed branch reached push.\n' >&2
    return 1
  fi

  observed_sha="4444444444444444444444444444444444444444"
  if push_governed_ref "$RELEASE_REF" 2>/dev/null; then
    printf 'Publication helper source-ref self-test: changed SHA was accepted.\n' >&2
    return 1
  fi
  if [[ "$push_count" -ne 1 ]]; then
    printf 'Publication helper source-ref self-test: changed SHA reached push.\n' >&2
    return 1
  fi

  printf 'Publication helper source-ref self-test PASSED — 4 source states checked.\n'
)

clean_worktree_self_test() (
  local status_mode="failed"

  git() {
    if [[ "$#" -ne 3 || "$1" != "status" || "$2" != "--porcelain" ||
          "$3" != "--untracked-files=all" ]]; then
      return 91
    fi
    case "$status_mode" in
      failed)
        return 1
        ;;
      dirty)
        printf ' M fixture\n'
        ;;
      clean)
        return 0
        ;;
      *)
        return 92
        ;;
    esac
  }

  if require_clean_worktree 2>/dev/null; then
    printf 'Publication helper clean-worktree self-test: failed status passed.\n' >&2
    return 1
  fi
  status_mode="dirty"
  if require_clean_worktree 2>/dev/null; then
    printf 'Publication helper clean-worktree self-test: dirty tree passed.\n' >&2
    return 1
  fi
  status_mode="clean"
  require_clean_worktree
  printf 'Publication helper clean-worktree self-test PASSED — 3 observation states checked.\n'
)

pre_push_binding_self_test() (
  local -r COMMIT="5555555555555555555555555555555555555555"
  local -r SOURCE_REF="refs/heads/fixture"
  local -r RELEASE_REF="refs/heads/release/$COMMIT"
  local -r INPUT_ROW="$SOURCE_REF $COMMIT $RELEASE_REF $ZERO_SHA"
  local -r BINDING_ERROR="pre-push: governed publication tuple does not match frozen helper source"
  local -r REMOTE_ERROR="pre-push: governed publication requires remote name origin"
  local -r STATUS_ERROR="pre-push: publishing worktree status could not be observed"
  local output

  if output="$(
    printf '%s\n' "$INPUT_ROW" |
      ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="" \
      bash "$SCRIPT_ROOT/.githooks/pre-push" not-origin ignored 2>&1
  )"; then
    printf 'Publication helper pre-push binding self-test: missing binding passed.\n' >&2
    return 1
  fi
  if [[ "$output" != "$BINDING_ERROR" ]]; then
    printf 'Publication helper pre-push binding self-test: missing-binding refusal drifted.\n' >&2
    return 1
  fi

  if output="$(
    printf '%s\n' "$INPUT_ROW" |
      ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="refs/heads/other" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="$COMMIT" \
      bash "$SCRIPT_ROOT/.githooks/pre-push" not-origin ignored 2>&1
  )"; then
    printf 'Publication helper pre-push binding self-test: ref mismatch passed.\n' >&2
    return 1
  fi
  if [[ "$output" != "$BINDING_ERROR" ]]; then
    printf 'Publication helper pre-push binding self-test: ref refusal drifted.\n' >&2
    return 1
  fi

  if output="$(
    printf '%s\n' "$INPUT_ROW" |
      ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="$SOURCE_REF" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="6666666666666666666666666666666666666666" \
      bash "$SCRIPT_ROOT/.githooks/pre-push" not-origin ignored 2>&1
  )"; then
    printf 'Publication helper pre-push binding self-test: SHA mismatch passed.\n' >&2
    return 1
  fi
  if [[ "$output" != "$BINDING_ERROR" ]]; then
    printf 'Publication helper pre-push binding self-test: SHA refusal drifted.\n' >&2
    return 1
  fi

  if output="$(
    printf '%s\n' "$INPUT_ROW" |
      ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="$SOURCE_REF" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="$COMMIT" \
      bash "$SCRIPT_ROOT/.githooks/pre-push" not-origin ignored 2>&1
  )"; then
    printf 'Publication helper pre-push binding self-test: invalid remote passed.\n' >&2
    return 1
  fi
  if [[ "$output" != "$REMOTE_ERROR" ]]; then
    printf 'Publication helper pre-push binding self-test: exact binding did not advance.\n' >&2
    return 1
  fi

  if output="$(
    printf '%s\n' "$INPUT_ROW" |
      GIT_INDEX_FILE="/dev/null" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="$SOURCE_REF" \
      ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="$COMMIT" \
      bash "$SCRIPT_ROOT/.githooks/pre-push" \
        origin "$CANONICAL_REMOTE_URL" 2>&1
  )"; then
    printf 'Publication helper pre-push binding self-test: failed status passed.\n' >&2
    return 1
  fi
  if [[ "$output" != *"$STATUS_ERROR" ]]; then
    printf 'Publication helper pre-push binding self-test: status refusal drifted.\n' >&2
    return 1
  fi

  printf 'Publication helper pre-push binding self-test PASSED — 5 hook protocol states checked.\n'
)

[[ "$#" -eq 1 ]] || usage
readonly MODE="$1"
if [[ "$MODE" == "--self-test" ]]; then
  state_machine_self_test
  validator_scope_self_test
  source_ref_self_test
  clean_worktree_self_test
  pre_push_binding_self_test
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
  if ! require_clean_worktree; then
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
  local status_main_sha
  local status_release_sha
  status_main_sha="$(remote_ref_sha "$MAIN_REF")"
  status_release_sha="$(remote_ref_sha "$RELEASE_REF")"
  printf 'HEAD:        %s\n' "$COMMIT"
  printf 'remote main: %s\n' "${status_main_sha:-absent}"
  printf 'candidate:   %s\n' "${status_release_sha:-absent}"
  if [[ "$status_main_sha" == "$COMMIT" ]]; then
    python3 scripts/ci/verify_github_release.py checks \
      --sha "$COMMIT" --branch main --timeout-seconds 1 --poll-seconds 1
  elif [[ "$status_release_sha" == "$COMMIT" ]]; then
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
SOURCE_REF="$(publication_source_ref)"
readonly SOURCE_REF
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
    push_governed_ref "$RELEASE_REF"
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
  push_governed_ref "$MAIN_REF"
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
