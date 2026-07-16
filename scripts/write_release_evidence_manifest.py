#!/usr/bin/env python3
"""Write an allowlisted digest manifest for repository-release diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


EXPECTED_FILES = {
    "actionlint.log",
    "final-release-contract.log",
    "gitleaks-artifacts.log",
    "gitleaks-history.log",
    "markdownlint.log",
    "mermaid.log",
    "npm-audit.log",
    "npm-ci.log",
    "odeya-architecture.svg",
    "release-contract.log",
    "rehearsal-comparator-self-test.log",
    "shellcheck.log",
    "tool-versions.txt",
    "zizmor.log",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_root", type=Path)
    args = parser.parse_args()
    root = args.evidence_root.resolve()
    manifest_path = root / "evidence-manifest.json"

    if not root.is_dir():
        print(f"evidence root is absent: {root}", file=sys.stderr)
        return 2

    repository = Path(__file__).resolve().parents[1]
    for command in (
        ["git", "diff", "--quiet", "--"],
        ["git", "diff", "--cached", "--quiet", "--"],
    ):
        result = subprocess.run(command, cwd=repository, check=False)
        if result.returncode != 0:
            print(
                "release evidence cannot be bound to HEAD while tracked bytes differ",
                file=sys.stderr,
            )
            return 5

    actual = {
        path.name
        for path in root.iterdir()
        if path.name != manifest_path.name
    }
    if actual != EXPECTED_FILES:
        print(
            f"release evidence inventory mismatch: expected {sorted(EXPECTED_FILES)}, "
            f"found {sorted(actual)}",
            file=sys.stderr,
        )
        return 3

    entries: list[dict[str, object]] = []
    for name in sorted(EXPECTED_FILES):
        path = root / name
        if not path.is_file() or path.is_symlink():
            print(f"release evidence is not one regular file: {name}", file=sys.stderr)
            return 4
        content = path.read_bytes()
        entries.append(
            {
                "path": name,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    manifest = {
        "schema_version": "0.1.0",
        "artifact_class": "repository_release_diagnostic_manifest",
        "subject_commit": commit,
        "canonical_scientific_evidence": False,
        "files": entries,
    }
    temporary = manifest_path.with_suffix(".json.partial")
    temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(manifest_path)
    print(f"Release evidence manifest PASSED — {len(entries)} files for {commit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
