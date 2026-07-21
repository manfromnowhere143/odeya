#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export LANG=C

readonly VERSION="21.0.9"
readonly RELEASE_TAG="jdk-21.0.9+10"
readonly RELEASE_BASE="https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.9%2B10"
readonly CACHE_ROOT="${ODEYA_TOOL_CACHE:-${TMPDIR:-/tmp}/odeya-release-tools}"

case "$(uname -s):$(uname -m)" in
  Darwin:x86_64)
    readonly PLATFORM_KEY="darwin_amd64"
    readonly ARCHIVE_NAME="OpenJDK21U-jdk_x64_mac_hotspot_21.0.9_10.tar.gz"
    readonly EXPECTED_SHA256="f803a3f5bce141f23ac699dfcda06a721f4b74f53bacb0f4bbe9bfcad54427d8"
    readonly JAVA_HOME_SUFFIX="Contents/Home"
    ;;
  Darwin:arm64)
    readonly PLATFORM_KEY="darwin_arm64"
    readonly ARCHIVE_NAME="OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.9_10.tar.gz"
    readonly EXPECTED_SHA256="55a40abeb0e174fdc70f769b34b50b70c3967e0b12a643e6a3e23f9a582aac16"
    readonly JAVA_HOME_SUFFIX="Contents/Home"
    ;;
  Linux:x86_64)
    readonly PLATFORM_KEY="linux_amd64"
    readonly ARCHIVE_NAME="OpenJDK21U-jdk_x64_linux_hotspot_21.0.9_10.tar.gz"
    readonly EXPECTED_SHA256="810d3773df7e0d6c4394e4e244b264c8b30e0b05a0acf542d065fd78a6b65c2f"
    readonly JAVA_HOME_SUFFIX=""
    ;;
  Linux:aarch64 | Linux:arm64)
    readonly PLATFORM_KEY="linux_arm64"
    readonly ARCHIVE_NAME="OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.9_10.tar.gz"
    readonly EXPECTED_SHA256="edf0da4debe7cf475dbe320d174d6eed81479eb363f41e38a2efb740428c603a"
    readonly JAVA_HOME_SUFFIX=""
    ;;
  *)
    printf 'Unsupported Java bootstrap platform: %s %s\n' "$(uname -s)" "$(uname -m)" >&2
    exit 2
    ;;
esac

readonly ARCHIVE_URL="${RELEASE_BASE}/${ARCHIVE_NAME}"
readonly ARCHIVE_PATH="${CACHE_ROOT}/java/${ARCHIVE_NAME}"
readonly INSTALL_ROOT="${CACHE_ROOT}/java/${RELEASE_TAG}/${PLATFORM_KEY}"
if [[ -n "$JAVA_HOME_SUFFIX" ]]; then
  readonly JAVA_HOME_PATH="${INSTALL_ROOT}/${JAVA_HOME_SUFFIX}"
else
  readonly JAVA_HOME_PATH="$INSTALL_ROOT"
fi
readonly JAVA_BIN="${JAVA_HOME_PATH}/bin/java"

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
    printf 'Java archive digest mismatch for %s.\n' "$ARCHIVE_NAME" >&2
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

if [[ "$("$JAVA_BIN" -XshowSettings:properties -version 2>&1)" != *"java.runtime.version = ${VERSION}+10-LTS"* ]]; then
  printf 'Installed Java runtime did not match Temurin %s+10.\n' "$VERSION" >&2
  exit 4
fi

printf '%s\n' "$JAVA_BIN"
