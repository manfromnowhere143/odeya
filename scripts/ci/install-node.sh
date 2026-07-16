#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="24.18.0"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM_KEY="darwin_amd64"
    readonly ARCHIVE_PLATFORM="darwin-x64"
    readonly EXPECTED_SHA256="dfd0dbd3e721503434df7b7205e719f61b3a3a31b2bcf9729b8b91fea240f080"
    ;;
  Darwin:arm64)
    readonly PLATFORM_KEY="darwin_arm64"
    readonly ARCHIVE_PLATFORM="darwin-arm64"
    readonly EXPECTED_SHA256="e1a97e14c99c803e96c7339403282ea05a499c32f8d83defe9ef5ec66f979ed1"
    ;;
  Linux:x86_64)
    readonly PLATFORM_KEY="linux_amd64"
    readonly ARCHIVE_PLATFORM="linux-x64"
    readonly EXPECTED_SHA256="783130984963db7ba9cbd01089eaf2c2efb055c7c1693c943174b967b3050cb8"
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM_KEY="linux_arm64"
    readonly ARCHIVE_PLATFORM="linux-arm64"
    readonly EXPECTED_SHA256="6b4484c2190274175df9aa8f28e2d758a819cb1c1fe6ab481e2f95b463ab8508"
    ;;
  *)
    printf 'Unsupported Node bootstrap platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_NAME="node-v${VERSION}-${ARCHIVE_PLATFORM}.tar.gz"
readonly ARCHIVE_URL="https://nodejs.org/dist/v${VERSION}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/node/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/node/v${VERSION}/${PLATFORM_KEY}"
readonly NODE_BIN="${INSTALL_ROOT}/bin/node"

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
    printf 'Node archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
    exit 3
  fi
  mv -- "$PARTIAL" "$ARCHIVE_PATH"
  trap - EXIT
fi

readonly STAGING="${INSTALL_ROOT}.staging.$$"
rm -rf -- "$STAGING"
mkdir -p "$STAGING"
tar -xzf "$ARCHIVE_PATH" --strip-components=1 -C "$STAGING"
rm -rf -- "$INSTALL_ROOT"
mkdir -p "$(dirname "$INSTALL_ROOT")"
mv -- "$STAGING" "$INSTALL_ROOT"

if [[ "$($NODE_BIN --version)" != "v${VERSION}" ]]; then
  printf 'Installed Node version did not match v%s.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$NODE_BIN"
