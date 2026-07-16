#!/usr/bin/env python3
"""Verify and compare local and remote-main rehearsal evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from write_rehearsal_evidence_manifest import (
    PASS_DISPOSITIONS,
    PROFILE_PATHS,
    ROOT_FILES,
)
from write_release_evidence_manifest import EXPECTED_FILES as RELEASE_FILES


MANIFEST_NAME = "rehearsal-evidence-manifest.json"
RELEASE_MANIFEST_NAME = "evidence-manifest.json"
REHEARSAL_FIELDS = {
    "schema_version",
    "artifact_class",
    "subject_commit",
    "source_class",
    "source_identity_sha256",
    "remote_main_commit",
    "canonical_scientific_evidence",
    "profile_files",
    "pass_dispositions",
    "files",
}
RELEASE_FIELDS = {
    "schema_version",
    "artifact_class",
    "subject_commit",
    "canonical_scientific_evidence",
    "files",
}
EXPECTED_EVIDENCE_PATHS = set(ROOT_FILES) | {
    f"repository-release/{name}" for name in (set(RELEASE_FILES) | {RELEASE_MANIFEST_NAME})
}
EXACT_FIELDS = (
    "schema_version",
    "artifact_class",
    "subject_commit",
    "canonical_scientific_evidence",
    "profile_files",
    "pass_dispositions",
)
SHA256 = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")


class EvidenceError(ValueError):
    """One retained evidence directory does not satisfy its own manifest."""


class DuplicateKeyError(ValueError):
    """A JSON object contains a repeated member name."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def decode_manifest(payload: bytes, description: str) -> dict[str, Any]:
    try:
        document = json.loads(payload, object_pairs_hook=unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise EvidenceError(f"cannot decode {description}: {exc}") from exc
    if not isinstance(document, dict):
        raise EvidenceError(f"{description} is not an object")
    return document


def inventory(document: dict[str, Any]) -> set[str]:
    files = document.get("files")
    if not isinstance(files, list):
        return set()
    return {
        entry.get("path")
        for entry in files
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }


def digest_entry_errors(
    document: dict[str, Any], expected_paths: set[str]
) -> list[str]:
    errors: list[str] = []
    files = document.get("files")
    if not isinstance(files, list):
        return ["files must be an array"]
    observed: list[str] = []
    for index, entry in enumerate(files):
        if not isinstance(entry, dict) or set(entry) != {"path", "bytes", "sha256"}:
            errors.append(f"files[{index}] must contain exactly path, bytes, sha256")
            continue
        path = entry.get("path")
        size = entry.get("bytes")
        digest = entry.get("sha256")
        if not isinstance(path, str):
            errors.append(f"files[{index}].path must be a string")
            continue
        parsed = PurePosixPath(path)
        if (
            parsed.is_absolute()
            or path != parsed.as_posix()
            or any(part in {"", ".", ".."} for part in parsed.parts)
        ):
            errors.append(f"files[{index}].path is not one safe canonical relative path")
        observed.append(path)
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            errors.append(f"files[{index}].bytes must be a nonnegative integer")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            errors.append(f"files[{index}].sha256 must be one lowercase SHA-256")
    if len(observed) != len(set(observed)):
        errors.append("files contains a duplicate path")
    if set(observed) != expected_paths or len(observed) != len(expected_paths):
        errors.append(
            f"evidence inventory mismatch: expected {sorted(expected_paths)}, "
            f"got {sorted(observed)}"
        )
    return errors


def rehearsal_document_errors(document: dict[str, Any]) -> list[str]:
    errors = digest_entry_errors(document, EXPECTED_EVIDENCE_PATHS)
    if set(document) != REHEARSAL_FIELDS:
        errors.append("rehearsal manifest does not contain the exact top-level members")
    if document.get("schema_version") != "0.1.0":
        errors.append("schema_version is not 0.1.0")
    if document.get("artifact_class") != "fresh_clone_rehearsal_evidence_manifest":
        errors.append("artifact_class is not fresh-clone rehearsal evidence")
    if not isinstance(document.get("subject_commit"), str) or not COMMIT.fullmatch(
        document["subject_commit"]
    ):
        errors.append("subject_commit is not one lowercase forty-character SHA")
    if document.get("canonical_scientific_evidence") is not False:
        errors.append("rehearsal evidence must remain noncanonical diagnostic evidence")
    profile = document.get("profile_files")
    if not isinstance(profile, dict) or set(profile) != set(PROFILE_PATHS):
        errors.append("profile_files does not contain the exact pinned profile inventory")
    elif any(not isinstance(value, str) or not SHA256.fullmatch(value) for value in profile.values()):
        errors.append("profile_files contains a non-SHA-256 identity")
    if document.get("pass_dispositions") != PASS_DISPOSITIONS:
        errors.append("pass_dispositions is not the exact all-passed profile")
    source_identity = document.get("source_identity_sha256")
    if not isinstance(source_identity, str) or not SHA256.fullmatch(source_identity):
        errors.append("source_identity_sha256 is not one lowercase SHA-256")
    if document.get("source_class") not in {"local", "remote-main"}:
        errors.append("source_class is not local or remote-main")
    remote_main = document.get("remote_main_commit")
    if remote_main is not None and (
        not isinstance(remote_main, str) or not COMMIT.fullmatch(remote_main)
    ):
        errors.append("remote_main_commit is neither null nor one commit SHA")
    return errors


def release_document_errors(
    document: dict[str, Any], subject_commit: str
) -> list[str]:
    errors = digest_entry_errors(document, set(RELEASE_FILES))
    if set(document) != RELEASE_FIELDS:
        errors.append("nested release manifest does not contain the exact top-level members")
    if document.get("schema_version") != "0.1.0":
        errors.append("nested release schema_version is not 0.1.0")
    if document.get("artifact_class") != "repository_release_diagnostic_manifest":
        errors.append("nested release artifact_class is not exact")
    if document.get("subject_commit") != subject_commit:
        errors.append("nested release evidence names a different subject commit")
    if document.get("canonical_scientific_evidence") is not False:
        errors.append("nested release evidence must remain noncanonical")
    return errors


def verify_files(
    root: Path,
    document: dict[str, Any],
    manifest_name: str,
    expected_paths: set[str],
) -> list[str]:
    errors: list[str] = []
    if not root.is_dir() or root.is_symlink():
        return [f"evidence root is not one real directory: {root}"]
    manifest_path = root / manifest_name
    if not manifest_path.is_file() or manifest_path.is_symlink():
        errors.append(f"manifest is not one regular file: {manifest_path}")

    actual_files: set[str] = set()
    actual_dirs: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(f"evidence contains a symlink: {relative}")
        elif path.is_file() and relative != manifest_name:
            actual_files.add(relative)
        elif path.is_dir():
            actual_dirs.add(relative)
    expected_dirs = {
        parent.as_posix()
        for relative in expected_paths
        for parent in PurePosixPath(relative).parents
        if parent.as_posix() != "."
    }
    if actual_files != expected_paths:
        errors.append(
            f"on-disk evidence inventory mismatch: expected {sorted(expected_paths)}, "
            f"got {sorted(actual_files)}"
        )
    if actual_dirs != expected_dirs:
        errors.append(
            f"on-disk evidence directory inventory mismatch: expected {sorted(expected_dirs)}, "
            f"got {sorted(actual_dirs)}"
        )

    entries = {
        entry["path"]: entry
        for entry in document.get("files", [])
        if isinstance(entry, dict)
        and isinstance(entry.get("path"), str)
        and set(entry) == {"path", "bytes", "sha256"}
    }
    for relative in sorted(expected_paths & actual_files & set(entries)):
        path = root / relative
        payload = path.read_bytes()
        if entries[relative].get("bytes") != len(payload):
            errors.append(f"retained byte count differs: {relative}")
        if entries[relative].get("sha256") != hashlib.sha256(payload).hexdigest():
            errors.append(f"retained SHA-256 differs: {relative}")
    return errors


def load_manifest(root: Path) -> tuple[dict[str, Any], bytes]:
    root = root.resolve()
    manifest_path = root / MANIFEST_NAME
    try:
        payload = manifest_path.read_bytes()
    except OSError as exc:
        raise EvidenceError(f"cannot read rehearsal manifest at {manifest_path}: {exc}") from exc
    document = decode_manifest(payload, f"rehearsal manifest at {manifest_path}")

    errors = rehearsal_document_errors(document)
    errors.extend(verify_files(root, document, MANIFEST_NAME, EXPECTED_EVIDENCE_PATHS))
    release_root = root / "repository-release"
    release_path = release_root / RELEASE_MANIFEST_NAME
    try:
        release_payload = release_path.read_bytes()
        release_document = decode_manifest(release_payload, "nested release manifest")
    except (OSError, EvidenceError) as exc:
        errors.append(f"cannot read nested release manifest: {exc}")
        release_document = None
    if isinstance(release_document, dict):
        errors.extend(release_document_errors(release_document, document.get("subject_commit", "")))
        errors.extend(
            verify_files(
                release_root,
                release_document,
                RELEASE_MANIFEST_NAME,
                set(RELEASE_FILES),
            )
        )
    elif release_document is not None:
        errors.append("nested release manifest is not an object")
    if errors:
        raise EvidenceError("; ".join(errors))
    return document, payload


def comparison_errors(
    local: dict[str, Any],
    remote: dict[str, Any],
    expected_remote_source_sha256: str,
) -> list[str]:
    errors = [f"local: {error}" for error in rehearsal_document_errors(local)]
    errors.extend(f"remote: {error}" for error in rehearsal_document_errors(remote))
    for field in EXACT_FIELDS:
        if local.get(field) != remote.get(field):
            errors.append(f"invariant field differs: {field}")
    if inventory(local) != inventory(remote):
        errors.append("retained evidence path inventory differs")
    if local.get("source_class") != "local" or local.get("remote_main_commit") is not None:
        errors.append("local rehearsal has an invalid source role")
    if remote.get("source_class") != "remote-main":
        errors.append("remote rehearsal is not remote-main evidence")
    if remote.get("remote_main_commit") != remote.get("subject_commit"):
        errors.append("remote main does not equal the remote rehearsal subject")
    if remote.get("source_identity_sha256") != expected_remote_source_sha256:
        errors.append("remote source does not equal the approved canonical source identity")
    return errors


def safe_document(source_class: str) -> dict[str, Any]:
    subject = "a" * 40
    source_identity = "b" * 64 if source_class == "local" else "e" * 64
    return {
        "schema_version": "0.1.0",
        "artifact_class": "fresh_clone_rehearsal_evidence_manifest",
        "subject_commit": subject,
        "source_class": source_class,
        "source_identity_sha256": source_identity,
        "remote_main_commit": subject if source_class == "remote-main" else None,
        "canonical_scientific_evidence": False,
        "profile_files": {relative: "c" * 64 for relative in PROFILE_PATHS},
        "pass_dispositions": dict(PASS_DISPOSITIONS),
        "files": [
            {"path": relative, "bytes": 1, "sha256": "d" * 64}
            for relative in sorted(EXPECTED_EVIDENCE_PATHS)
        ],
    }


def digest_entries(root: Path, paths: set[str]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for relative in sorted(paths):
        payload = (root / relative).read_bytes()
        entries.append(
            {
                "path": relative,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return entries


def materialize_self_test_evidence(root: Path) -> None:
    release_root = root / "repository-release"
    release_root.mkdir(parents=True)
    for relative in sorted(RELEASE_FILES):
        (release_root / relative).write_text(f"{relative}\n", encoding="utf-8")
    subject = "a" * 40
    release_document = {
        "schema_version": "0.1.0",
        "artifact_class": "repository_release_diagnostic_manifest",
        "subject_commit": subject,
        "canonical_scientific_evidence": False,
        "files": digest_entries(release_root, set(RELEASE_FILES)),
    }
    (release_root / RELEASE_MANIFEST_NAME).write_text(
        json.dumps(release_document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    for relative in sorted(ROOT_FILES):
        (root / relative).write_text(f"{relative}\n", encoding="utf-8")
    document = safe_document("local")
    document["files"] = digest_entries(root, EXPECTED_EVIDENCE_PATHS)
    (root / MANIFEST_NAME).write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def self_test() -> int:
    local = safe_document("local")
    remote = safe_document("remote-main")
    expected_source = remote["source_identity_sha256"]
    if comparison_errors(local, remote, expected_source):
        raise SystemExit("rehearsal comparison self-test rejected the safe reference")

    rejected = 0
    mutations = {
        "subject": ("subject_commit", "f" * 40),
        "profile": ("profile_files", {}),
        "disposition": ("pass_dispositions", {"foundation": "failed"}),
        "source-role": ("source_class", "local"),
        "source-identity": ("source_identity_sha256", "0" * 64),
    }
    for field, value in mutations.values():
        candidate = copy.deepcopy(remote)
        candidate[field] = value
        if comparison_errors(local, candidate, expected_source):
            rejected += 1
    missing = copy.deepcopy(remote)
    missing["files"] = []
    if comparison_errors(local, missing, expected_source):
        rejected += 1
    duplicate = copy.deepcopy(remote)
    duplicate["files"].append(copy.deepcopy(duplicate["files"][0]))
    if comparison_errors(local, duplicate, expected_source):
        rejected += 1
    invalid_local = copy.deepcopy(local)
    invalid_remote = copy.deepcopy(remote)
    for document in (invalid_local, invalid_remote):
        document["schema_version"] = "invalid"
        document["artifact_class"] = "not-rehearsal-evidence"
        document["subject_commit"] = "not-a-commit"
        document["canonical_scientific_evidence"] = True
    if comparison_errors(invalid_local, invalid_remote, expected_source):
        rejected += 1

    with tempfile.TemporaryDirectory(prefix="odeya-rehearsal-comparator-") as temporary:
        root = Path(temporary)
        tamper_root = root / "retained-tamper"
        tamper_root.mkdir()
        materialize_self_test_evidence(tamper_root)
        load_manifest(tamper_root)
        (tamper_root / "foundation.log").write_text("tampered\n", encoding="utf-8")
        try:
            load_manifest(tamper_root)
        except EvidenceError:
            rejected += 1
        else:
            raise SystemExit("rehearsal comparator accepted tampered retained evidence")

        top_duplicate_root = root / "top-duplicate-member"
        top_duplicate_root.mkdir()
        materialize_self_test_evidence(top_duplicate_root)
        top_manifest = top_duplicate_root / MANIFEST_NAME
        top_payload = top_manifest.read_text(encoding="utf-8")
        top_manifest.write_text(
            top_payload.replace(
                '  "schema_version": "0.1.0",',
                '  "schema_version": "0.1.0",\n  "schema_version": "0.1.0",',
                1,
            ),
            encoding="utf-8",
        )
        try:
            load_manifest(top_duplicate_root)
        except EvidenceError:
            rejected += 1
        else:
            raise SystemExit("rehearsal comparator accepted a duplicate top-level JSON member")

        nested_duplicate_root = root / "nested-duplicate-member"
        nested_duplicate_root.mkdir()
        materialize_self_test_evidence(nested_duplicate_root)
        nested_manifest = (
            nested_duplicate_root / "repository-release" / RELEASE_MANIFEST_NAME
        )
        nested_payload = nested_manifest.read_text(encoding="utf-8")
        nested_manifest.write_text(
            nested_payload.replace(
                '  "schema_version": "0.1.0",',
                '  "schema_version": "0.1.0",\n  "schema_version": "0.1.0",',
                1,
            ),
            encoding="utf-8",
        )
        try:
            load_manifest(nested_duplicate_root)
        except EvidenceError:
            rejected += 1
        else:
            raise SystemExit("rehearsal comparator accepted a duplicate nested JSON member")

        top_extra_root = root / "top-extra-member"
        top_extra_root.mkdir()
        materialize_self_test_evidence(top_extra_root)
        top_extra_manifest = top_extra_root / MANIFEST_NAME
        top_extra_document = json.loads(top_extra_manifest.read_text(encoding="utf-8"))
        top_extra_document["unexpected"] = True
        top_extra_manifest.write_text(
            json.dumps(top_extra_document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        try:
            load_manifest(top_extra_root)
        except EvidenceError:
            rejected += 1
        else:
            raise SystemExit("rehearsal comparator accepted an extra top-level member")

        nested_extra_root = root / "nested-extra-member"
        nested_extra_root.mkdir()
        materialize_self_test_evidence(nested_extra_root)
        nested_extra_manifest = (
            nested_extra_root / "repository-release" / RELEASE_MANIFEST_NAME
        )
        nested_extra_document = json.loads(
            nested_extra_manifest.read_text(encoding="utf-8")
        )
        nested_extra_document["unexpected"] = True
        nested_extra_manifest.write_text(
            json.dumps(nested_extra_document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        try:
            load_manifest(nested_extra_root)
        except EvidenceError:
            rejected += 1
        else:
            raise SystemExit("rehearsal comparator accepted an extra nested member")

    if rejected != 13:
        raise SystemExit(f"rehearsal comparison self-test rejected {rejected}/13 mutations")
    print("Fresh-clone rehearsal comparison self-test PASSED — 13 mutations rejected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--local", type=Path)
    parser.add_argument("--remote", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-remote-source-sha256")
    args = parser.parse_args()
    if args.self_test:
        if any(
            (
                args.local,
                args.remote,
                args.output,
                args.expected_remote_source_sha256,
            )
        ):
            parser.error("--self-test cannot be combined with evidence arguments")
        return self_test()
    if not all(
        (
            args.local,
            args.remote,
            args.output,
            args.expected_remote_source_sha256,
        )
    ):
        parser.error(
            "--local, --remote, --output, and --expected-remote-source-sha256 are required"
        )
    if not SHA256.fullmatch(args.expected_remote_source_sha256):
        parser.error("approved remote source identity must be one lowercase SHA-256")

    try:
        local, local_payload = load_manifest(args.local)
        remote, remote_payload = load_manifest(args.remote)
    except EvidenceError as exc:
        print("Fresh-clone rehearsal comparison FAILED")
        print(f"- {exc}")
        return 1
    errors = comparison_errors(local, remote, args.expected_remote_source_sha256)
    if errors:
        print("Fresh-clone rehearsal comparison FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    receipt = {
        "schema_version": "0.1.0",
        "artifact_class": "fresh_clone_rehearsal_comparison_receipt",
        "subject_commit": local["subject_commit"],
        "status": "verified_evidence_and_invariant_profile_equal",
        "local_manifest_sha256": hashlib.sha256(local_payload).hexdigest(),
        "remote_manifest_sha256": hashlib.sha256(remote_payload).hexdigest(),
        "approved_remote_source_sha256": args.expected_remote_source_sha256,
        "verified_evidence_file_count_per_rehearsal": len(EXPECTED_EVIDENCE_PATHS),
        "compared_exactly": list(EXACT_FIELDS),
        "compared_as_set": "files[].path",
        "intentionally_not_compared": [
            "local source_identity_sha256",
            "files[].bytes after independent verification",
            "files[].sha256 after independent verification",
        ],
        "canonical_scientific_evidence": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_suffix(args.output.suffix + ".partial")
    partial.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    partial.replace(args.output)
    print(f"Fresh-clone rehearsal comparison PASSED for {local['subject_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
