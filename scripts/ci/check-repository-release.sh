#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly ROOT
# shellcheck source=scripts/ci/sanitize-git-environment.sh
source "$ROOT/scripts/ci/sanitize-git-environment.sh"
readonly TOOL_ROOT="$ROOT/tools/repository-release"
EXPECTED_NODE="v$(tr -d '[:space:]' < "$TOOL_ROOT/.node-version")"
readonly EXPECTED_NODE
readonly EXPECTED_NPM="11.16.0"
EXPECTED_PYTHON="$(tr -d '[:space:]' < "$ROOT/.python-version")"
readonly EXPECTED_PYTHON
readonly EVIDENCE_ROOT="$ROOT/artifacts/repository-release"
readonly EVIDENCE_PARENT="$ROOT/artifacts"
OWN_TOOL_CACHE=0
if [[ -z "${ODEYA_TOOL_CACHE:-}" ]]; then
  ODEYA_TOOL_CACHE="$(mktemp -d "${TMPDIR:-/tmp}/odeya-release-tools.XXXXXX")"
  OWN_TOOL_CACHE=1
fi
readonly ODEYA_TOOL_CACHE
readonly OWN_TOOL_CACHE
export ODEYA_TOOL_CACHE
WORK_EVIDENCE_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/odeya-release-evidence.XXXXXX")"
readonly WORK_EVIDENCE_ROOT
SUBJECT_COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
readonly SUBJECT_COMMIT
CURRENT_STAGE="preflight"
SUCCESS=0
GITLEAKS_ARTIFACT_LOG=""
EVIDENCE_PUBLISH=""

mkdir -p "$EVIDENCE_PARENT"
rm -rf -- "$EVIDENCE_ROOT"

finalize() {
  local status="$?"
  local failure_publish=""
  trap - EXIT
  rm -f -- "$GITLEAKS_ARTIFACT_LOG"
  rm -rf -- "$WORK_EVIDENCE_ROOT"
  if [[ "$OWN_TOOL_CACHE" -eq 1 ]]; then
    rm -rf -- "$ODEYA_TOOL_CACHE"
  fi
  if [[ -n "$EVIDENCE_PUBLISH" ]]; then
    rm -rf -- "$EVIDENCE_PUBLISH"
  fi
  if [[ "$status" -ne 0 || "$SUCCESS" -ne 1 ]]; then
    failure_publish="$(mktemp -d "$EVIDENCE_PARENT/.repository-release.failure.XXXXXX")"
    {
      printf 'schema_version=0.1.0\n'
      printf 'status=failed\n'
      printf 'subject_commit=%s\n' "$SUBJECT_COMMIT"
      printf 'failed_stage=%s\n' "$CURRENT_STAGE"
      printf 'partial_diagnostics_retained=false\n'
      printf 'reason=unscanned partial diagnostics were destroyed\n'
    } > "$failure_publish/failure-receipt.txt"
    rm -rf -- "$EVIDENCE_ROOT"
    mv -- "$failure_publish" "$EVIDENCE_ROOT"
    if [[ "$status" -eq 0 ]]; then
      status=1
    fi
  fi
  exit "$status"
}
trap finalize EXIT

if ! git -C "$ROOT" diff --quiet -- || ! git -C "$ROOT" diff --cached --quiet --; then
  printf 'Repository release evidence requires a clean tracked tree at HEAD.\n' >&2
  exit 2
fi
if [[ -n "$(git -C "$ROOT" status --porcelain=v1 --untracked-files=all)" ]]; then
  printf 'Repository release evidence refuses nonignored untracked files.\n' >&2
  exit 2
fi
if [[ "$(git -C "$ROOT" rev-parse --is-shallow-repository)" != "false" ]]; then
  printf 'Repository release evidence requires the complete ancestry of HEAD.\n' >&2
  exit 2
fi
if [[ "$(python3 -c 'import platform; print(platform.python_version())')" != "$EXPECTED_PYTHON" ]]; then
  printf 'Python version mismatch: expected %s, got %s.\n' \
    "$EXPECTED_PYTHON" "$(python3 -c 'import platform; print(platform.python_version())')" >&2
  exit 3
fi

CURRENT_STAGE="release-contract"
python3 "$ROOT/scripts/validate_repository_release.py" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/release-contract.log"

CURRENT_STAGE="node-install"
NODE_BIN="$(bash "$ROOT/scripts/ci/install-node.sh")"
readonly NODE_BIN
PATH="$(dirname "$NODE_BIN"):$PATH"
export PATH

if [[ "$(node --version)" != "$EXPECTED_NODE" ]]; then
  printf 'Node version mismatch: expected %s, got %s.\n' "$EXPECTED_NODE" "$(node --version)" >&2
  exit 4
fi
if [[ "$(npm --version)" != "$EXPECTED_NPM" ]]; then
  printf 'npm version mismatch: expected %s, got %s.\n' "$EXPECTED_NPM" "$(npm --version)" >&2
  exit 5
fi

CURRENT_STAGE="npm-install"
(cd "$TOOL_ROOT" && npm ci --ignore-scripts --no-audit --no-fund) \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/npm-ci.log"
CURRENT_STAGE="npm-audit"
(cd "$TOOL_ROOT" && npm audit --audit-level=high) \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/npm-audit.log"
CURRENT_STAGE="markdownlint"
(cd "$TOOL_ROOT" && npm run lint:markdown) \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/markdownlint.log"

CURRENT_STAGE="shellcheck-install"
SHELLCHECK_BIN="$(bash "$ROOT/scripts/ci/install-shellcheck.sh")"
readonly SHELLCHECK_BIN

CURRENT_STAGE="actionlint-install"
ACTIONLINT_BIN="$(bash "$ROOT/scripts/ci/install-actionlint.sh")"
readonly ACTIONLINT_BIN
CURRENT_STAGE="actionlint"
"$ACTIONLINT_BIN" -no-color -shellcheck "$SHELLCHECK_BIN" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/actionlint.log"

CURRENT_STAGE="zizmor-install"
ZIZMOR_BIN="$(bash "$ROOT/scripts/ci/install-zizmor.sh")"
readonly ZIZMOR_BIN
CURRENT_STAGE="zizmor"
"$ZIZMOR_BIN" --no-config --offline --pedantic "$ROOT/.github/workflows" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/zizmor.log"

CURRENT_STAGE="shellcheck"
"$SHELLCHECK_BIN" "$ROOT"/scripts/ci/*.sh "$ROOT/.githooks/pre-push" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/shellcheck.log"

CURRENT_STAGE="gitleaks-install"
GITLEAKS_BIN="$(bash "$ROOT/scripts/ci/install-gitleaks.sh")"
readonly GITLEAKS_BIN
CURRENT_STAGE="gitleaks-history"
env -u GITLEAKS_CONFIG -u GITLEAKS_CONFIG_TOML "$GITLEAKS_BIN" git \
  --config "$ROOT/.gitleaks.toml" \
  --redact \
  --no-banner \
  --no-color \
  --log-opts="$SUBJECT_COMMIT" \
  "$ROOT" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/gitleaks-history.log"
EXPECTED_HISTORY_COMMIT_COUNT="$(git -C "$ROOT" rev-list --count "$SUBJECT_COMMIT")"
readonly EXPECTED_HISTORY_COMMIT_COUNT
if ! grep -Eq \
  "[[:space:]]INF ${EXPECTED_HISTORY_COMMIT_COUNT} commits scanned\\.$" \
  "$WORK_EVIDENCE_ROOT/gitleaks-history.log"; then
  printf 'Gitleaks did not attest the exact subject ancestry commit count.\n' >&2
  exit 6
fi

CURRENT_STAGE="mermaid-render"
bash "$ROOT/scripts/ci/render-readme-architecture.sh" \
  "$WORK_EVIDENCE_ROOT/odeya-architecture.svg" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/mermaid.log"

CURRENT_STAGE="tool-identity"
{
  python3 --version
  node --version
  npm --version
  "$SHELLCHECK_BIN" --version
  "$ACTIONLINT_BIN" -version
  "$ZIZMOR_BIN" --version
  "$GITLEAKS_BIN" version
} > "$WORK_EVIDENCE_ROOT/tool-versions.txt"

CURRENT_STAGE="final-release-contract"
python3 "$ROOT/scripts/validate_repository_release.py" \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/final-release-contract.log"

CURRENT_STAGE="publication-sequence-self-test"
{
  python3 "$ROOT/scripts/ci/validate_publication_sequence.py" --self-test
  bash "$ROOT/scripts/ci/push-rehearsed-head.sh" --self-test
} 2>&1 | tee -a "$WORK_EVIDENCE_ROOT/final-release-contract.log"

CURRENT_STAGE="github-release-verifier-self-test"
python3 "$ROOT/scripts/ci/verify_github_release.py" --self-test \
  2>&1 | tee -a "$WORK_EVIDENCE_ROOT/final-release-contract.log"

CURRENT_STAGE="rehearsal-comparator-self-test"
python3 "$ROOT/scripts/compare_rehearsal_manifests.py" --self-test \
  2>&1 | tee "$WORK_EVIDENCE_ROOT/rehearsal-comparator-self-test.log"

CURRENT_STAGE="gitleaks-artifacts"
GITLEAKS_ARTIFACT_LOG="$(mktemp "${TMPDIR:-/tmp}/odeya-gitleaks-artifacts.XXXXXX")"
env -u GITLEAKS_CONFIG -u GITLEAKS_CONFIG_TOML "$GITLEAKS_BIN" dir \
  --config "$ROOT/.gitleaks.toml" \
  --redact \
  --no-banner \
  --no-color \
  "$WORK_EVIDENCE_ROOT" \
  > "$GITLEAKS_ARTIFACT_LOG" 2>&1
mv -- "$GITLEAKS_ARTIFACT_LOG" "$WORK_EVIDENCE_ROOT/gitleaks-artifacts.log"
GITLEAKS_ARTIFACT_LOG=""

CURRENT_STAGE="evidence-manifest"
python3 "$ROOT/scripts/write_release_evidence_manifest.py" "$WORK_EVIDENCE_ROOT"

CURRENT_STAGE="evidence-publish"
EVIDENCE_PUBLISH="$(mktemp -d "$EVIDENCE_PARENT/.repository-release.publish.XXXXXX")"
cp -p "$WORK_EVIDENCE_ROOT"/* "$EVIDENCE_PUBLISH"/
mv -- "$EVIDENCE_PUBLISH" "$EVIDENCE_ROOT"
EVIDENCE_PUBLISH=""
SUCCESS=1
printf 'Odeya repository release surface PASSED\n'
