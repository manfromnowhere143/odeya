#!/usr/bin/env bash
# Publish the current HEAD only if its own rehearsal evidence exists.
#
# The sequencing law -- rehearse the exact commit, then push, then watch the
# remote workflows to green -- was disciplinary until 2026-07-18, when the
# operator's own session pushed a commit while its rehearsal was still
# running. That rehearsal passed, so nothing broke; the sequence was still
# wrong, and a law that depends on remembering is not a gate. This script
# makes it mechanical: no evidence manifest bound to this exact commit, no
# push.
set -euo pipefail

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly SCRIPT_ROOT
# Deliberately NOT sourcing sanitize-git-environment.sh: that isolator strips
# credential helpers so a rehearsal clone can never authenticate anywhere, which
# is exactly right for reading and exactly wrong for publishing. Verification
# below reads only local state, and the push needs the operator's own
# credentials.

readonly EVIDENCE_ROOT="${ODEYA_EVIDENCE_ROOT:-/Users/danielwahnich/workspace/odeya-release-evidence}"
readonly REMOTE="${1:-origin}"
readonly BRANCH="${2:-main}"

cd "$SCRIPT_ROOT"
COMMIT="$(git rev-parse HEAD)"
readonly COMMIT

if [[ -n "$(git status --short)" ]]; then
  printf 'Refusing to publish: the worktree is not clean.\n' >&2
  exit 2
fi

readonly MANIFEST="$EVIDENCE_ROOT/$COMMIT/rehearsal-evidence-manifest.json"
if [[ ! -f "$MANIFEST" ]]; then
  printf 'Refusing to publish %s: no rehearsal evidence at %s\n' "$COMMIT" "$MANIFEST" >&2
  printf 'Run scripts/ci/rehearse-fresh-clone.sh for this exact commit first.\n' >&2
  exit 3
fi

python3 - "$MANIFEST" "$COMMIT" <<'PY'
import json, sys
document = json.loads(open(sys.argv[1], encoding="utf-8").read())
if document.get("subject_commit") != sys.argv[2]:
    print("Refusing to publish: retained evidence binds a different commit "
          f"({document.get('subject_commit')}).", file=sys.stderr)
    raise SystemExit(4)
if document.get("canonical_scientific_evidence") is not False:
    print("Refusing to publish: evidence claims canonical scientific status.", file=sys.stderr)
    raise SystemExit(4)
PY

if ! git merge-base --is-ancestor "$REMOTE/$BRANCH" HEAD 2>/dev/null; then
  git fetch --quiet "$REMOTE"
  if ! git merge-base --is-ancestor "$REMOTE/$BRANCH" HEAD; then
    printf 'Refusing to publish: HEAD is not a fast-forward of %s/%s.\n' "$REMOTE" "$BRANCH" >&2
    exit 5
  fi
fi

printf 'Rehearsal evidence verified for %s; publishing to %s/%s.\n' "$COMMIT" "$REMOTE" "$BRANCH"
git push "$REMOTE" "HEAD:$BRANCH"
printf 'Published. The push is NOT complete until every workflow on %s reports green.\n' "$COMMIT"
