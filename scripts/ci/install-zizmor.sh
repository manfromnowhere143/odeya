#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="1.27.0"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM="darwin_amd64"
    readonly TARGET="x86_64-apple-darwin"
    readonly EXPECTED_SHA256="51cd82d1f6914cbb7f4402dbdc19bd989a7599078e5ddeaf837d1ab901c97328"
    ;;
  Darwin:arm64)
    readonly PLATFORM="darwin_arm64"
    readonly TARGET="aarch64-apple-darwin"
    readonly EXPECTED_SHA256="81336423d1b280c5dd0cdd8644a1e5f3238ab3ceb8d6e4334dfd05dab95a8a86"
    ;;
  Linux:x86_64)
    readonly PLATFORM="linux_amd64"
    readonly TARGET="x86_64-unknown-linux-gnu"
    readonly EXPECTED_SHA256="277f2bd8fd37cf60c42ab7afca6faa884e65440fa31e02b44bdaae60f62a358f"
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM="linux_arm64"
    readonly TARGET="aarch64-unknown-linux-gnu"
    readonly EXPECTED_SHA256="46fceee9a8262dca0e61f8463204e1f0f3a63bf6c20fa3ef9a5c1b3cff7b17b0"
    ;;
  *)
    printf 'Unsupported Zizmor platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_NAME="zizmor-${TARGET}.tar.gz"
readonly ARCHIVE_URL="https://github.com/zizmorcore/zizmor/releases/download/v${VERSION}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/zizmor/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/zizmor/v${VERSION}/${PLATFORM}"
readonly ZIZMOR_BIN="${INSTALL_ROOT}/zizmor"

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
    printf 'Zizmor archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
    exit 3
  fi
  mv -- "$PARTIAL" "$ARCHIVE_PATH"
  trap - EXIT
fi

readonly STAGING="${INSTALL_ROOT}.staging.$$"
rm -rf -- "$STAGING"
mkdir -p "$STAGING"
tar -xzf "$ARCHIVE_PATH" -C "$STAGING" zizmor
chmod 0755 "$STAGING/zizmor"
rm -rf -- "$INSTALL_ROOT"
mkdir -p "$(dirname "$INSTALL_ROOT")"
mv -- "$STAGING" "$INSTALL_ROOT"

if [[ "$($ZIZMOR_BIN --version)" != "zizmor ${VERSION}" ]]; then
  printf 'Installed Zizmor version did not match %s.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$ZIZMOR_BIN"
