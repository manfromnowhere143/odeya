#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="0.11.0"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM="darwin_amd64"
    readonly TARGET="darwin.x86_64"
    readonly EXPECTED_SHA256="c2c15e08df0e8fbc374c335b230a7ee958c313fa5714817a59aa59f1aa594f51"
    ;;
  Darwin:arm64)
    readonly PLATFORM="darwin_arm64"
    readonly TARGET="darwin.aarch64"
    readonly EXPECTED_SHA256="339b930feb1ea764467013cc1f72d09cd6b869ebf1013296ba9055ab2ffbd26f"
    ;;
  Linux:x86_64)
    readonly PLATFORM="linux_amd64"
    readonly TARGET="linux.x86_64"
    readonly EXPECTED_SHA256="b7af85e41cc99489dcc21d66c6d5f3685138f06d34651e6d34b42ec6d54fe6f6"
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM="linux_arm64"
    readonly TARGET="linux.aarch64"
    readonly EXPECTED_SHA256="68a8133197a50beb8803f8d42f9908d1af1c5540d4bb05fdfca8c1fa47decefc"
    ;;
  *)
    printf 'Unsupported ShellCheck platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_NAME="shellcheck-v${VERSION}.${TARGET}.tar.gz"
readonly ARCHIVE_URL="https://github.com/koalaman/shellcheck/releases/download/v${VERSION}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/shellcheck/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/shellcheck/v${VERSION}/${PLATFORM}"
readonly SHELLCHECK_BIN="${INSTALL_ROOT}/shellcheck"

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
    printf 'ShellCheck archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
    exit 3
  fi
  mv -- "$PARTIAL" "$ARCHIVE_PATH"
  trap - EXIT
fi

readonly STAGING="${INSTALL_ROOT}.staging.$$"
rm -rf -- "$STAGING"
mkdir -p "$STAGING"
tar -xzf "$ARCHIVE_PATH" --strip-components=1 -C "$STAGING"
chmod 0755 "$STAGING/shellcheck"
rm -rf -- "$INSTALL_ROOT"
mkdir -p "$(dirname "$INSTALL_ROOT")"
mv -- "$STAGING" "$INSTALL_ROOT"

if [[ "$($SHELLCHECK_BIN --version | awk '/^version:/ {print $2}')" != "$VERSION" ]]; then
  printf 'Installed ShellCheck version did not match %s.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$SHELLCHECK_BIN"
