#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="1.7.12"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM="darwin_amd64"
    readonly EXPECTED_SHA256="5b44c3bc2255115c9b69e30efc0fecdf498fdb63c5d58e17084fd5f16324c644"
    ;;
  Darwin:arm64)
    readonly PLATFORM="darwin_arm64"
    readonly EXPECTED_SHA256="aba9ced2dee8d27fecca3dc7feb1a7f9a52caefa1eb46f3271ea66b6e0e6953f"
    ;;
  Linux:x86_64)
    readonly PLATFORM="linux_amd64"
    readonly EXPECTED_SHA256="8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8"
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM="linux_arm64"
    readonly EXPECTED_SHA256="325e971b6ba9bfa504672e29be93c24981eeb1c07576d730e9f7c8805afff0c6"
    ;;
  *)
    printf 'Unsupported Actionlint platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_NAME="actionlint_${VERSION}_${PLATFORM}.tar.gz"
readonly ARCHIVE_URL="https://github.com/rhysd/actionlint/releases/download/v${VERSION}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/actionlint/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/actionlint/v${VERSION}/${PLATFORM}"
readonly ACTIONLINT_BIN="${INSTALL_ROOT}/actionlint"

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
    printf 'Actionlint archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
    exit 3
  fi
  mv -- "$PARTIAL" "$ARCHIVE_PATH"
  trap - EXIT
fi

readonly STAGING="${INSTALL_ROOT}.staging.$$"
rm -rf -- "$STAGING"
mkdir -p "$STAGING"
tar -xzf "$ARCHIVE_PATH" -C "$STAGING" actionlint
chmod 0755 "$STAGING/actionlint"
rm -rf -- "$INSTALL_ROOT"
mkdir -p "$(dirname "$INSTALL_ROOT")"
mv -- "$STAGING" "$INSTALL_ROOT"

if [[ "$($ACTIONLINT_BIN -version | head -n 1)" != "$VERSION" ]]; then
  printf 'Installed Actionlint version did not match %s.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$ACTIONLINT_BIN"
