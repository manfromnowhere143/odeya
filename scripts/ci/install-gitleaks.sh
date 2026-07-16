#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="8.30.1"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM="darwin_amd64"
    readonly TARGET="darwin_x64"
    readonly EXPECTED_SHA256="dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709"
    ;;
  Darwin:arm64)
    readonly PLATFORM="darwin_arm64"
    readonly TARGET="darwin_arm64"
    readonly EXPECTED_SHA256="b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5"
    ;;
  Linux:x86_64)
    readonly PLATFORM="linux_amd64"
    readonly TARGET="linux_x64"
    readonly EXPECTED_SHA256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM="linux_arm64"
    readonly TARGET="linux_arm64"
    readonly EXPECTED_SHA256="e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080"
    ;;
  *)
    printf 'Unsupported Gitleaks platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_NAME="gitleaks_${VERSION}_${TARGET}.tar.gz"
readonly ARCHIVE_URL="https://github.com/gitleaks/gitleaks/releases/download/v${VERSION}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/gitleaks/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/gitleaks/v${VERSION}/${PLATFORM}"
readonly GITLEAKS_BIN="${INSTALL_ROOT}/gitleaks"

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

mkdir -p "$(dirname "$ARCHIVE_PATH")"
if [[ ! -f "$ARCHIVE_PATH" ]] || [[ "$(sha256_file "$ARCHIVE_PATH")" != "$EXPECTED_SHA256" ]]; then
  readonly PARTIAL="${ARCHIVE_PATH}.partial.$$"
  trap 'rm -f -- "$PARTIAL"' EXIT
  curl --fail --location --retry 3 --silent --show-error "$ARCHIVE_URL" --output "$PARTIAL"
  if [[ "$(sha256_file "$PARTIAL")" != "$EXPECTED_SHA256" ]]; then
    printf 'Gitleaks archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
    exit 3
  fi
  mv -- "$PARTIAL" "$ARCHIVE_PATH"
  trap - EXIT
fi

readonly STAGING="${INSTALL_ROOT}.staging.$$"
rm -rf -- "$STAGING"
mkdir -p "$STAGING"
tar -xzf "$ARCHIVE_PATH" -C "$STAGING" gitleaks
chmod 0755 "$STAGING/gitleaks"
rm -rf -- "$INSTALL_ROOT"
mkdir -p "$(dirname "$INSTALL_ROOT")"
mv -- "$STAGING" "$INSTALL_ROOT"

if [[ "$($GITLEAKS_BIN version)" != "$VERSION" ]]; then
  printf 'Installed Gitleaks version did not match %s.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$GITLEAKS_BIN"
