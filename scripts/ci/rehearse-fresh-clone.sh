#!/usr/bin/env bash
set -euo pipefail
umask 077

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly SCRIPT_ROOT
# shellcheck source=scripts/ci/sanitize-git-environment.sh
source "$SCRIPT_ROOT/scripts/ci/sanitize-git-environment.sh"

if [[ "$#" -lt 3 || "$#" -gt 5 ]]; then
  printf 'Usage: %s <expected-commit> <source> <evidence-directory> [local|remote-main] [approved-source-sha256]\n' \
    "$0" >&2
  exit 2
fi

readonly EXPECTED_COMMIT="$1"
readonly SOURCE="$2"
EVIDENCE_OUT="$(python3 -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())' "$3")"
readonly EVIDENCE_OUT
EVIDENCE_PARENT="$(dirname "$EVIDENCE_OUT")"
readonly EVIDENCE_PARENT
readonly SOURCE_CLASS="${4:-local}"
readonly EXPECTED_SOURCE_IDENTITY_SHA256="${5:-}"
SOURCE_IDENTITY_SHA256="$(python3 -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())' "$SOURCE")"
readonly SOURCE_IDENTITY_SHA256

if [[ ! "$EXPECTED_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  printf 'Expected commit must be one lowercase forty-character SHA.\n' >&2
  exit 3
fi
if [[ "$SOURCE_CLASS" != "local" && "$SOURCE_CLASS" != "remote-main" ]]; then
  printf 'Source class must be local or remote-main.\n' >&2
  exit 4
fi
if [[ "$SOURCE_CLASS" == "remote-main" ]]; then
  if [[ ! "$EXPECTED_SOURCE_IDENTITY_SHA256" =~ ^[0-9a-f]{64}$ ]]; then
    printf 'Remote-main rehearsal requires the approved canonical source SHA-256.\n' >&2
    exit 5
  fi
  if [[ "$SOURCE_IDENTITY_SHA256" != "$EXPECTED_SOURCE_IDENTITY_SHA256" ]]; then
    printf 'Remote source does not match the approved canonical source identity.\n' >&2
    exit 5
  fi
elif [[ -n "$EXPECTED_SOURCE_IDENTITY_SHA256" ]]; then
  printf 'Local rehearsal must not claim an approved remote source identity.\n' >&2
  exit 5
fi
if [[ "$SOURCE_CLASS" == "local" && "$SOURCE" != /* ]]; then
  printf 'Local rehearsal source must be one absolute path.\n' >&2
  exit 5
fi
if [[ "$SOURCE" == *"?"* || "$SOURCE" == *"#"* || "$SOURCE" =~ ://[^/]+@ ]]; then
  printf 'Source must not contain embedded credentials, a query string, or a fragment.\n' >&2
  exit 5
fi
if [[ -e "$EVIDENCE_OUT" ]]; then
  printf 'Evidence destination must not already exist: %s\n' "$EVIDENCE_OUT" >&2
  exit 6
fi
mkdir -p -- "$EVIDENCE_PARENT"

REHEARSAL_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/odeya-release-rehearsal.XXXXXX")"
readonly REHEARSAL_ROOT
readonly CLONE="$REHEARSAL_ROOT/odeya"
EVIDENCE_STAGING="$(mktemp -d "${TMPDIR:-/tmp}/odeya-rehearsal-evidence.XXXXXX")"
readonly EVIDENCE_STAGING
readonly TLA_ROOT="${TMPDIR:-/tmp}/odeya-tla/v1.7.4"
readonly TLA_JAR="$TLA_ROOT/tla2tools.jar"
readonly TLA_SHA256="936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
STAGE_LEDGER="$REHEARSAL_ROOT/stage-outcomes.txt"
readonly STAGE_LEDGER
# Every disposition the manifest reports must come from a stage that actually
# ran. Before ADR 0076 the manifest carried six hardcoded "passed" values that
# could not express a failure or a skip, which independent review identified as
# a fabricated measurement in retained evidence.
record_stage() {
  printf '%s=%s\n' "$1" "$2" >> "$STAGE_LEDGER"
}
CURRENT_STAGE="clone"
SUCCESS=0
REMOTE_MAIN_COMMIT=""
EVIDENCE_PUBLISH=""

cleanup() {
  local status="$?"
  local failure_publish=""
  trap - EXIT
  rm -rf -- "$REHEARSAL_ROOT" "$EVIDENCE_STAGING"
  if [[ -n "$EVIDENCE_PUBLISH" ]]; then
    rm -rf -- "$EVIDENCE_PUBLISH"
  fi
  if [[ "$status" -ne 0 || "$SUCCESS" -ne 1 ]]; then
    failure_publish="$(mktemp -d "$EVIDENCE_PARENT/.odeya-rehearsal.failure.XXXXXX")"
    {
      printf 'schema_version=0.1.0\n'
      printf 'status=failed\n'
      printf 'subject_commit=%s\n' "$EXPECTED_COMMIT"
      printf 'source_class=%s\n' "$SOURCE_CLASS"
      printf 'failed_stage=%s\n' "$CURRENT_STAGE"
      printf 'partial_diagnostics_retained=false\n'
    } > "$failure_publish/failure-receipt.txt"
    if [[ ! -e "$EVIDENCE_OUT" ]]; then
      mv -- "$failure_publish" "$EVIDENCE_OUT"
    else
      rm -rf -- "$failure_publish"
    fi
    if [[ "$status" -eq 0 ]]; then
      status=1
    fi
  fi
  exit "$status"
}
trap cleanup EXIT

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

isolated_git() {
  git -c http.sslVerify=true "$@"
}

isolated_git -C "$REHEARSAL_ROOT" clone --no-local --no-hardlinks --quiet -- "$SOURCE" "$CLONE"
isolated_git -C "$CLONE" checkout --detach --quiet "$EXPECTED_COMMIT"

if [[ "$(isolated_git -C "$CLONE" rev-parse HEAD)" != "$EXPECTED_COMMIT" ]]; then
  printf 'Fresh clone did not resolve the expected commit.\n' >&2
  exit 7
fi
if [[ "$(isolated_git -C "$CLONE" rev-parse --is-shallow-repository)" != "false" ]]; then
  printf 'Fresh clone does not contain the complete candidate ancestry.\n' >&2
  exit 7
fi
if [[ "$SOURCE_CLASS" == "remote-main" ]]; then
  CURRENT_STAGE="remote-main-identity"
  REMOTE_MAIN_COMMIT="$(isolated_git -C "$CLONE" rev-parse 'refs/remotes/origin/main^{commit}')"
  if [[ "$REMOTE_MAIN_COMMIT" != "$EXPECTED_COMMIT" ]]; then
    printf 'Remote main does not equal the accepted candidate commit.\n' >&2
    exit 8
  fi
fi

cd "$CLONE"
export PYTHONDONTWRITEBYTECODE=1
CURRENT_STAGE="toolchain-preflight"
if [[ "$(python3 -c 'import platform; print(platform.python_version())')" != "$(tr -d '[:space:]' < .python-version)" ]]; then
  printf 'Fresh-clone Python does not match .python-version.\n' >&2
  exit 9
fi
JAVA_VERSION="$(java -version 2>&1 | head -n 1 | sed -E 's/.*version "([^"]+)".*/\1/')"
readonly JAVA_VERSION
if [[ "$JAVA_VERSION" != "$(tr -d '[:space:]' < .java-version)" ]]; then
  printf 'Fresh-clone Java does not match .java-version.\n' >&2
  exit 10
fi

mkdir -p artifacts/rehearsal
CURRENT_STAGE="python-environment"
python3 -m venv .venv-architecture
.venv-architecture/bin/python -m pip install \
  --disable-pip-version-check \
  --no-input \
  --require-hashes \
  --only-binary=:all: \
  --report artifacts/rehearsal/pip-install-report.json \
  --requirement tools/repository-release/requirements-architecture.lock
.venv-architecture/bin/python -m pip check

CURRENT_STAGE="foundation"
.venv-architecture/bin/python scripts/validate.py \
  2>&1 | tee artifacts/rehearsal/foundation.log
record_stage foundation passed

# The cheap gate inside validate.py binds the guard-coverage record to the
# checker digest and to its own arithmetic. It cannot detect a record that was
# falsified consistently: flipping a guard to unproved, or deleting an unproved
# guard by name and correcting the counts, both survive it. Only re-measuring
# reproduces the record from the exact bytes, so the exact-commit rehearsal is
# where that must happen.
CURRENT_STAGE="lifecycle-guard-coverage"
if [[ -f scripts/audit_lifecycle_guard_coverage.py ]]; then
  .venv-architecture/bin/python scripts/audit_lifecycle_guard_coverage.py \
    --check --python .venv-architecture/bin/python \
    2>&1 | tee artifacts/rehearsal/lifecycle-guard-coverage.log
else
  # This commit predates the audit tool. Skipping is fail-closed, not fail-open:
  # validate.py above already refuses a retained coverage record whose audit
  # tool is absent, so a commit reaching this branch has no record to reproduce.
  # Without this branch the rehearsal cannot replay any commit older than the
  # tool, which is how this stage first failed.
  printf 'audit tool absent at %s; no retained coverage record to reproduce\n' \
    "$EXPECTED_COMMIT" 2>&1 | tee artifacts/rehearsal/lifecycle-guard-coverage.log
fi

# The CI-only contract-profile pins once diverged from the retained suites
# with every local rehearsal green: seven commits published with the remote
# Foundation workflow red because nothing local read the pins. The partition
# gate now runs in the default validator and, for the exact bytes, here.
CURRENT_STAGE="suite-guard-coverage"
if [[ -f scripts/audit_suite_guard_coverage.py ]]; then
  .venv-architecture/bin/python scripts/audit_suite_guard_coverage.py \
    --check --python .venv-architecture/bin/python \
    2>&1 | tee artifacts/rehearsal/suite-guard-coverage.log
else
  printf 'suite guard audit absent at %s; nothing to reproduce\n' \
    "$EXPECTED_COMMIT" 2>&1 | tee artifacts/rehearsal/suite-guard-coverage.log
fi

CURRENT_STAGE="schema-rule-ablation"
if [[ -f scripts/audit_schema_rule_ablation.py ]]; then
  .venv-architecture/bin/python scripts/audit_schema_rule_ablation.py \
    --check 2>&1 | tee artifacts/rehearsal/schema-rule-ablation.log
else
  printf 'ablation audit absent at %s; nothing to reproduce\n' \
    "$EXPECTED_COMMIT" 2>&1 | tee artifacts/rehearsal/schema-rule-ablation.log
fi

CURRENT_STAGE="contract-profile-partitions"
if [[ -f scripts/validate_contract_profiles.py ]]; then
  .venv-architecture/bin/python scripts/validate_contract_profiles.py \
    2>&1 | tee artifacts/rehearsal/contract-profile-partitions.log
else
  printf 'contract-profile gate absent at %s; nothing to reproduce\n' \
    "$EXPECTED_COMMIT" 2>&1 | tee artifacts/rehearsal/contract-profile-partitions.log
fi

# Same enforcement shape one level deeper: the condition-coverage record can
# be falsified consistently past its cheap gate, so only re-measurement here
# binds it to the exact bytes.
CURRENT_STAGE="lifecycle-condition-coverage"
if [[ -f scripts/audit_lifecycle_condition_coverage.py ]]; then
  .venv-architecture/bin/python scripts/audit_lifecycle_condition_coverage.py \
    --check --python .venv-architecture/bin/python \
    2>&1 | tee artifacts/rehearsal/lifecycle-condition-coverage.log
else
  # This commit predates the condition audit. Fail-closed for the same reason
  # as the stage above: validate.py refuses a retained condition record whose
  # audit tool is absent, so a commit reaching this branch has none.
  printf 'condition audit tool absent at %s; no retained condition record to reproduce\n' \
    "$EXPECTED_COMMIT" 2>&1 | tee artifacts/rehearsal/lifecycle-condition-coverage.log
fi

CURRENT_STAGE="release-surface"
bash scripts/ci/check-repository-release.sh
record_stage repository_release_surface passed

CURRENT_STAGE="tla-toolchain"
mkdir -p "$TLA_ROOT"
if [[ ! -f "$TLA_JAR" ]] || [[ "$(sha256_file "$TLA_JAR")" != "$TLA_SHA256" ]]; then
  TLA_PARTIAL="${TLA_JAR}.partial.$$"
  readonly TLA_PARTIAL
  curl --fail --location --retry 3 --silent --show-error \
    "https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar" \
    --output "$TLA_PARTIAL"
  if [[ "$(sha256_file "$TLA_PARTIAL")" != "$TLA_SHA256" ]]; then
    printf 'TLA+ tools digest mismatch.\n' >&2
    exit 11
  fi
  mv -- "$TLA_PARTIAL" "$TLA_JAR"
fi

CURRENT_STAGE="formal-models"
bash formal/tla/check.sh 2>&1 | tee artifacts/rehearsal/formal.log
record_stage bounded_formal_models passed

CURRENT_STAGE="mutation-audit"
isolated_git diff --exit-code
if [[ -n "$(isolated_git status --porcelain=v1 --untracked-files=all)" ]]; then
  printf 'Fresh-clone validation produced an unexpected tracked or nonignored file.\n' >&2
  isolated_git status --short --untracked-files=all >&2
  exit 12
fi

for expected_path in .venv-architecture artifacts tools/repository-release/node_modules; do
  if [[ ! -d "$expected_path" ]]; then
    printf 'Expected isolated output is absent: %s\n' "$expected_path" >&2
    exit 13
  fi
done
while IFS= read -r -d '' ignored; do
  case "$ignored" in
    "!! .venv-architecture/"*|"!! artifacts/"*|"!! tools/repository-release/node_modules/"*)
      ;;
    *)
      printf 'Fresh-clone validation touched a non-allowlisted ignored path: %s\n' \
        "$ignored" >&2
      exit 14
      ;;
  esac
done < <(isolated_git status --porcelain=v1 -z --ignored --untracked-files=all)

record_stage tracked_and_nonignored_mutation_audit passed
record_stage ignored_output_allowlist passed

CURRENT_STAGE="evidence-assembly"
cp -p artifacts/rehearsal/foundation.log "$EVIDENCE_STAGING"/
cp -p artifacts/rehearsal/formal.log "$EVIDENCE_STAGING"/
cp -p artifacts/rehearsal/pip-install-report.json "$EVIDENCE_STAGING"/
mkdir "$EVIDENCE_STAGING/repository-release"
cp -p artifacts/repository-release/* "$EVIDENCE_STAGING/repository-release"/

CURRENT_STAGE="evidence-secret-scan"
GITLEAKS_BIN="$(bash scripts/ci/install-gitleaks.sh)"
readonly GITLEAKS_BIN
GITLEAKS_REPORT="$REHEARSAL_ROOT/gitleaks-evidence.log"
readonly GITLEAKS_REPORT
env -u GITLEAKS_CONFIG -u GITLEAKS_CONFIG_TOML "$GITLEAKS_BIN" dir \
  --config "$CLONE/.gitleaks.toml" \
  --redact \
  --no-banner \
  --no-color \
  "$EVIDENCE_STAGING" \
  > "$GITLEAKS_REPORT" 2>&1
mv -- "$GITLEAKS_REPORT" "$EVIDENCE_STAGING/gitleaks-evidence.log"
record_stage retained_evidence_secret_scan passed

CURRENT_STAGE="evidence-manifest"
manifest_args=(
  --evidence-root "$EVIDENCE_STAGING"
  --subject-commit "$EXPECTED_COMMIT"
  --source-class "$SOURCE_CLASS"
  --source-identity-sha256 "$SOURCE_IDENTITY_SHA256"
  --stage-ledger "$STAGE_LEDGER"
)
if [[ "$SOURCE_CLASS" == "remote-main" ]]; then
  manifest_args+=(--remote-main-commit "$REMOTE_MAIN_COMMIT")
fi
python3 scripts/write_rehearsal_evidence_manifest.py "${manifest_args[@]}"

CURRENT_STAGE="evidence-retention"
EVIDENCE_PUBLISH="$(mktemp -d "$EVIDENCE_PARENT/.odeya-rehearsal.publish.XXXXXX")"
cp -R -p "$EVIDENCE_STAGING"/. "$EVIDENCE_PUBLISH"/
if [[ -e "$EVIDENCE_OUT" ]]; then
  printf 'Evidence destination appeared during rehearsal; refusing overwrite.\n' >&2
  exit 15
fi
mv -- "$EVIDENCE_PUBLISH" "$EVIDENCE_OUT"
EVIDENCE_PUBLISH=""
SUCCESS=1
printf 'Odeya fresh-clone release rehearsal PASSED at %s\n' "$EXPECTED_COMMIT"
printf 'Retained redacted evidence: %s\n' "$EVIDENCE_OUT"
