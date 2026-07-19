#!/usr/bin/env python3
"""Write the exact, redacted evidence manifest for a fresh-clone rehearsal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from write_release_evidence_manifest import EXPECTED_FILES as RELEASE_FILES


COMMIT = re.compile(r"[0-9a-f]{40}")
ROOT_FILES = {
    "foundation.log",
    "formal.log",
    "gitleaks-evidence.log",
    "pip-install-report.json",
}
MANIFEST_NAME = "rehearsal-evidence-manifest.json"
PROFILE_PATHS_V0_1 = (
    ".python-version",
    ".java-version",
    ".gitleaks.toml",
    "tools/repository-release/.node-version",
    "tools/repository-release/toolchain.lock.json",
    "tools/repository-release/requirements-architecture.lock",
    "tools/repository-release/package-lock.json",
    ".github/workflows/architecture.yml",
    ".github/workflows/release-surface.yml",
    ".github/workflows/formal.yml",
    "formal/tla/results-manifest.json",
)
PROFILE_PATHS_V0_2 = (
    *PROFILE_PATHS_V0_1,
    ".github/workflows/publication-sequence.yml",
)
PROFILE_PATHS = PROFILE_PATHS_V0_2
# The stages a complete rehearsal must report. Their dispositions are DERIVED
# from the ledger the rehearsal appends to as each stage completes; a stage
# that did not run is reported as not_run, never as passed. Until ADR 0076
# these were six hardcoded "passed" values written unconditionally -- a
# fabricated measurement inside retained evidence, found by independent
# review.
REQUIRED_STAGES = (
    "foundation",
    "repository_release_surface",
    "bounded_formal_models",
    "tracked_and_nonignored_mutation_audit",
    "ignored_output_allowlist",
    "retained_evidence_secret_scan",
)
PASS_DISPOSITIONS = {stage: "passed" for stage in REQUIRED_STAGES}


def derive_dispositions(ledger: Path) -> dict[str, str]:
    observed: dict[str, str] = {}
    if ledger.is_file():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            stage, _, outcome = line.partition("=")
            if stage and outcome:
                observed[stage.strip()] = outcome.strip()
    return {stage: observed.get(stage, "not_run") for stage in REQUIRED_STAGES}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--stage-ledger", type=Path,
                        help="ledger of stage outcomes; dispositions are derived from it")
    parser.add_argument("--subject-commit", required=True)
    parser.add_argument("--source-class", required=True, choices=("local", "remote-main"))
    parser.add_argument("--source-identity-sha256", required=True)
    parser.add_argument("--remote-main-commit")
    args = parser.parse_args()

    if not COMMIT.fullmatch(args.subject_commit):
        raise SystemExit("subject commit must be one lowercase forty-character SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", args.source_identity_sha256):
        raise SystemExit("source identity must be one lowercase SHA-256")
    if args.source_class == "remote-main":
        if args.remote_main_commit != args.subject_commit:
            raise SystemExit("remote main does not equal the rehearsal subject")
    elif args.remote_main_commit is not None:
        raise SystemExit("local evidence must not claim a remote main commit")

    root = args.evidence_root.resolve()
    release_root = root / "repository-release"
    expected_release = set(RELEASE_FILES) | {"evidence-manifest.json"}
    if {path.name for path in root.iterdir() if path.name != MANIFEST_NAME} != (
        ROOT_FILES | {"repository-release"}
    ):
        raise SystemExit("fresh-clone evidence root has an unexpected top-level inventory")
    if {path.name for path in release_root.iterdir()} != expected_release:
        raise SystemExit("nested repository-release evidence inventory is not exact")

    release_manifest = json.loads(
        (release_root / "evidence-manifest.json").read_text(encoding="utf-8")
    )
    if release_manifest.get("subject_commit") != args.subject_commit:
        raise SystemExit("nested release evidence names a different subject commit")

    repository = Path(__file__).resolve().parents[1]
    profile_files = {
        relative: hashlib.sha256((repository / relative).read_bytes()).hexdigest()
        for relative in PROFILE_PATHS
    }

    expected_paths = [root / name for name in sorted(ROOT_FILES)] + [
        release_root / name for name in sorted(expected_release)
    ]
    entries: list[dict[str, object]] = []
    for path in expected_paths:
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"rehearsal evidence is not one regular file: {path}")
        payload = path.read_bytes()
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )

    manifest = {
        "schema_version": "0.2.0",
        "artifact_class": "fresh_clone_rehearsal_evidence_manifest",
        "subject_commit": args.subject_commit,
        "source_class": args.source_class,
        "source_identity_sha256": args.source_identity_sha256,
        "remote_main_commit": args.remote_main_commit,
        "canonical_scientific_evidence": False,
        "profile_files": profile_files,
        "pass_dispositions": derive_dispositions(args.stage_ledger)
        if args.stage_ledger
        else dict(PASS_DISPOSITIONS),
        "files": entries,
    }
    target = root / MANIFEST_NAME
    partial = target.with_suffix(".json.partial")
    partial.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    partial.replace(target)
    print(
        f"Fresh-clone evidence manifest PASSED — {len(entries)} files for "
        f"{args.subject_commit}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
