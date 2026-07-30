#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly ROOT
readonly OUTPUT="${1:-$ROOT/artifacts/repository-release/odeya-architecture.svg}"
SOURCE_DIRECTORY="$(mktemp -d "${TMPDIR:-/tmp}/odeya-mermaid-sources.XXXXXX")"
readonly SOURCE_DIRECTORY
readonly MMDC="$ROOT/tools/repository-release/node_modules/.bin/mmdc"
readonly EXPECTED_CHROME_MAJOR="150"
readonly EXPECTED_DIAGRAM_COUNT="7"

cleanup() {
  rm -rf -- "$SOURCE_DIRECTORY"
}
trap cleanup EXIT

if [[ ! -x "$MMDC" ]]; then
  printf 'Mermaid CLI is absent; run npm ci --ignore-scripts in tools/repository-release.\n' >&2
  exit 2
fi

if [[ -z "${PUPPETEER_EXECUTABLE_PATH:-}" ]]; then
  if command -v google-chrome-stable >/dev/null 2>&1; then
    PUPPETEER_EXECUTABLE_PATH="$(command -v google-chrome-stable)"
  elif command -v google-chrome >/dev/null 2>&1; then
    PUPPETEER_EXECUTABLE_PATH="$(command -v google-chrome)"
  elif command -v chromium >/dev/null 2>&1; then
    PUPPETEER_EXECUTABLE_PATH="$(command -v chromium)"
  elif [[ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
    PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  else
    printf 'No Chrome/Chromium executable found for Mermaid rendering.\n' >&2
    exit 3
  fi
fi
export PUPPETEER_EXECUTABLE_PATH

BROWSER_VERSION="$("$PUPPETEER_EXECUTABLE_PATH" --version)"
readonly BROWSER_VERSION
BROWSER_MAJOR="$(printf '%s\n' "$BROWSER_VERSION" | sed -E 's/^[^0-9]*([0-9]+).*/\1/')"
readonly BROWSER_MAJOR
if [[ "$BROWSER_MAJOR" != "$EXPECTED_CHROME_MAJOR" ]]; then
  printf 'Mermaid browser major mismatch: expected %s, got %s (%s).\n' \
    "$EXPECTED_CHROME_MAJOR" "$BROWSER_MAJOR" "$BROWSER_VERSION" >&2
  exit 4
fi
printf 'Mermaid browser: %s\n' "$BROWSER_VERSION"

mkdir -p "$(dirname "$OUTPUT")"
python3 "$ROOT/scripts/validate_repository_release.py" \
  --extract-mermaid-directory "$SOURCE_DIRECTORY"

assert_image() {
  local rendered="$1"
  if [[ ! -s "$rendered" ]]; then
    printf 'Mermaid did not produce a nonempty image: %s\n' "$rendered" >&2
    exit 5
  fi
  case "$rendered" in
    *.svg)
      if [[ "$(head -c 4 "$rendered")" != "<svg" ]]; then
        printf 'Mermaid output is not an SVG: %s\n' "$rendered" >&2
        exit 6
      fi
      ;;
    *.png)
      if [[ "$(od -An -tx1 -N8 "$rendered" | tr -d ' \n')" != "89504e470d0a1a0a" ]]; then
        printf 'Mermaid output is not a PNG: %s\n' "$rendered" >&2
        exit 7
      fi
      ;;
  esac
}

rendered_count=0
for source in "$SOURCE_DIRECTORY"/*.mmd; do
  base="$(basename "$source" .mmd)"
  if [[ "$base" == "README-01" ]]; then
    rendered="$OUTPUT"
  else
    rendered="$SOURCE_DIRECTORY/$base.svg"
  fi
  "$MMDC" \
    --input "$source" \
    --output "$rendered" \
    --backgroundColor transparent \
    --quiet
  assert_image "$rendered"
  rendered_count=$((rendered_count + 1))
  printf 'Rendered governed Mermaid map: %s\n' "$base"
done

if [[ "$rendered_count" -ne "$EXPECTED_DIAGRAM_COUNT" ]]; then
  printf 'Mermaid render census mismatch: expected %s, got %s.\n' \
    "$EXPECTED_DIAGRAM_COUNT" "$rendered_count" >&2
  exit 8
fi

printf 'Rendered %s governed Mermaid maps; retained README map: %s\n' \
  "$rendered_count" "$OUTPUT"
