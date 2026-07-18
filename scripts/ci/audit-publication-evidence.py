#!/usr/bin/env python3
"""Audit that a published range is rehearsed commit by commit.

The publication gate refuses an unrehearsed HEAD, one commit at a time.
It says nothing about history: a range published before the gate existed,
or through a bypass, can contain commits with no evidence at all. This
audit answers the whole-history question the gate cannot -- for every
commit in a range, is there a retained manifest bound to that exact SHA?

Usage:
    python3 scripts/ci/audit-publication-evidence.py <range>

The evidence lives outside the repository by design (ADR 0047), so this
is an operator-side check: it cannot run in CI, and a clean result is a
statement about this machine's retained evidence, not about the world.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

EVIDENCE_ROOT = Path(
    os.environ.get("ODEYA_EVIDENCE_ROOT", "/Users/danielwahnich/workspace/odeya-release-evidence")
)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    commit_range = sys.argv[1]
    log = subprocess.run(
        ["git", "log", "--format=%H %s", commit_range],
        capture_output=True, text=True, check=False,
    )
    if log.returncode != 0:
        print(f"cannot resolve range {commit_range!r}: {log.stderr.strip()}", file=sys.stderr)
        return 2

    missing, mismatched, verified = [], [], 0
    lines = [line for line in log.stdout.strip().splitlines() if line]
    for line in lines:
        sha, _, subject = line.partition(" ")
        manifest = EVIDENCE_ROOT / sha / "rehearsal-evidence-manifest.json"
        if not manifest.is_file():
            missing.append((sha, subject))
            continue
        try:
            document = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            mismatched.append((sha, f"manifest is not valid JSON: {exc}"))
            continue
        if document.get("subject_commit") != sha:
            mismatched.append((sha, f"binds {document.get('subject_commit')}"))
        elif document.get("canonical_scientific_evidence") is not False:
            mismatched.append((sha, "claims canonical scientific status"))
        else:
            verified += 1

    for sha, subject in missing:
        print(f"NO EVIDENCE   {sha[:9]}  {subject[:70]}")
    for sha, reason in mismatched:
        print(f"BAD EVIDENCE  {sha[:9]}  {reason}")
    print(f"{verified}/{len(lines)} commits in {commit_range} have evidence bound to their exact SHA")
    return 1 if (missing or mismatched) else 0


if __name__ == "__main__":
    sys.exit(main())
