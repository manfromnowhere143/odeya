#!/usr/bin/env python3
"""Verify the bounded schema-resource reissue lineage ledger.

A successful check proves only byte-level lineage against one reachable Git
checkpoint.  It does not prove a complete offline schema registry, canonical
content identity, schema admission, Gate A acceptance, deployment, or runtime
authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "architecture/schema-resource-reissue-ledger.json"
SOURCE_CHECKPOINT = "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889"
SOURCE_TREE = "029b5161f883de41e93565b29ba895ee492a7d47"
RETENTION_MODE = "git_object_only_architecture_checkpoint_blocking"
SHA256_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
GIT_OBJECT_RE = re.compile(r"[0-9a-f]{40,64}\Z")
PINNED_VERSION_RE = re.compile(r"(?:^|[:/])\d+\.\d+\.\d+(?:\Z|[#?])")
LATEST_ALIAS_RE = re.compile(
    r"(?:^|[:/])latest(?:\.[a-z0-9._-]+)?(?:\Z|[:/#?])",
    re.IGNORECASE,
)


class DuplicateKeyError(ValueError):
    """Raised when JSON would otherwise silently overwrite a member."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def parse_json_bytes(raw: bytes, source: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=reject_duplicate_keys,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError, ValueError) as exc:
        raise ValueError(f"{source}: invalid strict JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{source}: root must be one JSON object")
    return value


def load_json(path: Path) -> dict[str, Any]:
    return parse_json_bytes(path.read_bytes(), path.relative_to(ROOT).as_posix())


def git(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def exact_keys(
    value: Any,
    expected: set[str],
    label: str,
    errors: list[str],
) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        errors.append(
            f"{label} members differ: missing={sorted(expected - actual)!r} "
            f"extra={sorted(actual - expected)!r}"
        )
        return False
    return True


def schema_id(document: dict[str, Any], source: str) -> str:
    value = document.get("$id")
    if not isinstance(value, str) or not value:
        raise ValueError(f"{source}: $id must be a non-empty string")
    return value


def is_version_pinned(resource_id: str) -> bool:
    return bool(PINNED_VERSION_RE.search(resource_id)) and not LATEST_ALIAS_RE.search(
        resource_id
    )


def latest_alias_locations(value: Any, pointer: str = "$") -> list[str]:
    """Return identity-like string locations that contain a mutable latest alias."""
    locations: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{pointer}/{key.replace('~', '~0').replace('/', '~1')}"
            if isinstance(item, str):
                identity_like = key in {"$id", "$ref", "$schema"} or item.startswith(
                    ("urn:", "http://", "https://")
                )
                external_or_absolute = not (key == "$ref" and item.startswith("#"))
                if identity_like and external_or_absolute and LATEST_ALIAS_RE.search(item):
                    locations.append(child)
            locations.extend(latest_alias_locations(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            locations.extend(latest_alias_locations(item, f"{pointer}/{index}"))
    return locations


def source_tree_entries() -> dict[str, str]:
    raw = git(
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        SOURCE_CHECKPOINT,
        "--",
        "schemas",
    )
    entries: dict[str, str] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_type, object_id = metadata.decode("ascii").split(" ")
        path = raw_path.decode("utf-8")
        if not path.endswith(".schema.json"):
            continue
        if mode not in {"100644", "100755"} or object_type != "blob":
            raise ValueError(f"{path}: source checkpoint entry is not a regular blob")
        if path in entries:
            raise ValueError(f"{path}: duplicate source checkpoint path")
        entries[path] = object_id
    return entries


def current_schema_paths() -> list[str]:
    paths: list[str] = []
    for path in sorted((ROOT / "schemas").rglob("*.schema.json")):
        if path.is_symlink():
            raise ValueError(f"{path.relative_to(ROOT)}: schema symlinks are forbidden")
        if not path.is_file():
            raise ValueError(f"{path.relative_to(ROOT)}: schema path is not a regular file")
        paths.append(path.relative_to(ROOT).as_posix())
    return paths


def read_source_blob(blob_id: str) -> bytes:
    if not GIT_OBJECT_RE.fullmatch(blob_id):
        raise ValueError(f"invalid Git object identity {blob_id!r}")
    object_type = git("cat-file", "-t", blob_id).decode("ascii").strip()
    if object_type != "blob":
        raise ValueError(f"Git object {blob_id} is {object_type!r}, not a blob")
    return git("cat-file", "blob", blob_id)


def inspect_resources() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
    list[str],
]:
    source_entries = source_tree_entries()
    current_paths = current_schema_paths()
    source: dict[str, dict[str, Any]] = {}
    current: dict[str, dict[str, Any]] = {}

    for path, blob_id in source_entries.items():
        raw = read_source_blob(blob_id)
        document = parse_json_bytes(raw, f"{SOURCE_CHECKPOINT}:{path}")
        source[path] = {
            "raw": raw,
            "document": document,
            "schema_id": schema_id(document, f"{SOURCE_CHECKPOINT}:{path}"),
            "blob": blob_id,
        }

    for path in current_paths:
        raw = (ROOT / path).read_bytes()
        document = parse_json_bytes(raw, path)
        current[path] = {
            "raw": raw,
            "document": document,
            "schema_id": schema_id(document, path),
        }

    return source, current, source_entries, current_paths


def exact_static_claims(ledger: dict[str, Any], errors: list[str]) -> None:
    root_keys = {
        "schema_version",
        "artifact_class",
        "ledger_id",
        "version",
        "status",
        "generated_at",
        "source_checkpoint",
        "source_checkpoint_tree",
        "comparison_scope",
        "canonical_profile",
        "retention_boundary",
        "proof_boundary",
        "reissues",
        "new_schema_candidates",
    }
    if not exact_keys(ledger, root_keys, "ledger", errors):
        return

    expected_scalars = {
        "schema_version": "0.1.0",
        "artifact_class": "architecture_evidence",
        "ledger_id": "odeya.schema-resource-reissue-ledger",
        "version": "0.1.0",
        "status": "candidate_lineage_evidence_only_not_admitted",
        "source_checkpoint": SOURCE_CHECKPOINT,
        "source_checkpoint_tree": SOURCE_TREE,
    }
    for key, expected in expected_scalars.items():
        require(ledger.get(key) == expected, f"ledger.{key} must equal {expected!r}", errors)
    require(
        isinstance(ledger.get("generated_at"), str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", ledger["generated_at"])
        is not None,
        "ledger.generated_at must be a six-digit UTC timestamp",
        errors,
    )

    comparison = ledger.get("comparison_scope")
    comparison_keys = {
        "path_glob",
        "source_schema_path_count",
        "current_schema_path_count",
        "reissued_existing_path_count",
        "new_schema_path_count",
        "reissue_definition",
        "same_id_byte_mutation",
        "source_path_deletion",
        "latest_aliases",
    }
    if exact_keys(comparison, comparison_keys, "comparison_scope", errors):
        expected = {
            "path_glob": "schemas/**/*.schema.json",
            "reissue_definition": "path_exists_at_source_and_current_schema_id_differs",
            "same_id_byte_mutation": "forbidden",
            "source_path_deletion": "blocking",
            "latest_aliases": "forbidden",
        }
        for key, value in expected.items():
            require(
                comparison.get(key) == value,
                f"comparison_scope.{key} must equal {value!r}",
                errors,
            )

    canonical = ledger.get("canonical_profile")
    canonical_keys = {
        "status",
        "raw_byte_digests_only",
        "canonical_content_digest_recorded",
        "canonical_content_digest_may_be_inferred",
    }
    if exact_keys(canonical, canonical_keys, "canonical_profile", errors):
        require(canonical.get("status") == "blocked", "canonical profile must remain blocked", errors)
        require(canonical.get("raw_byte_digests_only") is True, "only raw byte digests may be recorded", errors)
        require(
            canonical.get("canonical_content_digest_recorded") is False
            and canonical.get("canonical_content_digest_may_be_inferred") is False,
            "canonical content identity must remain absent and non-inferable",
            errors,
        )

    retention = ledger.get("retention_boundary")
    retention_keys = {
        "predecessor_retention_mode",
        "predecessor_bytes_materialized_in_current_tree",
        "complete_offline_schema_registry",
        "external_archive_verified",
        "git_reachability_is_durable_retention_proof",
        "source_repository_required_for_resolution",
        "disposition",
    }
    if exact_keys(retention, retention_keys, "retention_boundary", errors):
        expected = {
            "predecessor_retention_mode": RETENTION_MODE,
            "predecessor_bytes_materialized_in_current_tree": False,
            "complete_offline_schema_registry": False,
            "external_archive_verified": False,
            "git_reachability_is_durable_retention_proof": False,
            "source_repository_required_for_resolution": True,
            "disposition": "blocking_before_schema_admission_or_gate_a",
        }
        for key, value in expected.items():
            require(
                retention.get(key) == value,
                f"retention_boundary.{key} must equal {value!r}",
                errors,
            )

    proof = ledger.get("proof_boundary")
    proof_keys = {
        "lineage_evidence_only",
        "complete_offline_schema_registry",
        "canonical_content_identity",
        "schema_admission",
        "gate_a_acceptance",
        "deployment_authority",
        "runtime_authority",
    }
    if exact_keys(proof, proof_keys, "proof_boundary", errors):
        require(proof.get("lineage_evidence_only") is True, "proof must be lineage evidence only", errors)
        for key in proof_keys - {"lineage_evidence_only"}:
            require(proof.get(key) is False, f"proof_boundary.{key} must be false", errors)


def validate_ledger(
    ledger: dict[str, Any],
    source: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    source_entries: dict[str, str],
    errors: list[str],
) -> None:
    exact_static_claims(ledger, errors)

    source_paths = set(source)
    current_paths = set(current)
    deleted_paths = sorted(source_paths - current_paths)
    require(not deleted_paths, f"source schema paths were deleted: {deleted_paths!r}", errors)

    same_id_mutations: list[str] = []
    expected_reissues: list[str] = []
    for path in sorted(source_paths & current_paths):
        before = source[path]
        after = current[path]
        if before["schema_id"] == after["schema_id"]:
            if before["raw"] != after["raw"]:
                same_id_mutations.append(path)
        else:
            expected_reissues.append(path)
    require(
        not same_id_mutations,
        f"same-ID byte mutations are forbidden: {same_id_mutations!r}",
        errors,
    )
    expected_new = sorted(current_paths - source_paths)

    source_id_paths: dict[str, str] = {}
    for path, item in source.items():
        resource_id = item["schema_id"]
        require(
            is_version_pinned(resource_id),
            f"{SOURCE_CHECKPOINT}:{path}: source schema ID is not exact and version-pinned",
            errors,
        )
        if resource_id in source_id_paths:
            errors.append(
                f"duplicate source-checkpoint schema ID {resource_id!r}: "
                f"{source_id_paths[resource_id]} and {path}"
            )
        source_id_paths[resource_id] = path

    all_current_ids: dict[str, str] = {}
    for path, item in current.items():
        resource_id = item["schema_id"]
        require(
            is_version_pinned(resource_id),
            f"{path}: schema ID is not an exact version-pinned resource ID: {resource_id!r}",
            errors,
        )
        if resource_id in all_current_ids:
            errors.append(
                f"duplicate current schema ID {resource_id!r}: "
                f"{all_current_ids[resource_id]} and {path}"
            )
        all_current_ids[resource_id] = path
        latest_locations = latest_alias_locations(item["document"])
        require(
            not latest_locations,
            f"{path}: mutable latest aliases occur at {latest_locations!r}",
            errors,
        )

    for path in [*expected_reissues, *expected_new]:
        resource_id = current[path]["schema_id"]
        historical_owner = source_id_paths.get(resource_id)
        require(
            historical_owner is None,
            f"{path}: current candidate reuses source-checkpoint schema ID "
            f"{resource_id!r} owned by {historical_owner}",
            errors,
        )

    comparison = ledger.get("comparison_scope")
    if isinstance(comparison, dict):
        counts = {
            "source_schema_path_count": len(source_paths),
            "current_schema_path_count": len(current_paths),
            "reissued_existing_path_count": len(expected_reissues),
            "new_schema_path_count": len(expected_new),
        }
        for key, value in counts.items():
            require(
                comparison.get(key) == value,
                f"comparison_scope.{key} must equal dynamic count {value}",
                errors,
            )

    rows = ledger.get("reissues")
    if not isinstance(rows, list):
        errors.append("reissues must be an array")
        rows = []
    actual_reissue_paths = [
        row.get("path") if isinstance(row, dict) else None for row in rows
    ]
    require(
        actual_reissue_paths == expected_reissues,
        "reissues must be the sorted exact dynamic set of existing paths whose $id changed: "
        f"expected={expected_reissues!r} actual={actual_reissue_paths!r}",
        errors,
    )

    for index, row in enumerate(rows):
        label = f"reissues[{index}]"
        if not exact_keys(row, {"path", "predecessor", "current_candidate"}, label, errors):
            continue
        path = row.get("path")
        if path not in source or path not in current:
            errors.append(f"{label}.path is not an existing source/current schema path")
            continue
        predecessor = row.get("predecessor")
        predecessor_keys = {
            "schema_id",
            "source_commit",
            "git_blob",
            "raw_sha256",
            "byte_count",
            "retention_mode",
        }
        if exact_keys(predecessor, predecessor_keys, f"{label}.predecessor", errors):
            before = source[path]
            expected = {
                "schema_id": before["schema_id"],
                "source_commit": SOURCE_CHECKPOINT,
                "git_blob": source_entries[path],
                "raw_sha256": sha256(before["raw"]),
                "byte_count": len(before["raw"]),
                "retention_mode": RETENTION_MODE,
            }
            for key, value in expected.items():
                require(
                    predecessor.get(key) == value,
                    f"{label}.predecessor.{key} must equal {value!r}",
                    errors,
                )
            blob_id = predecessor.get("git_blob")
            if isinstance(blob_id, str) and GIT_OBJECT_RE.fullmatch(blob_id):
                try:
                    blob_bytes = read_source_blob(blob_id)
                    require(
                        blob_bytes == before["raw"],
                        f"{label}: predecessor blob bytes differ from source tree path",
                        errors,
                    )
                except (RuntimeError, ValueError) as exc:
                    errors.append(f"{label}: predecessor blob is not reachable: {exc}")
            resource_id = predecessor.get("schema_id")
            if isinstance(resource_id, str):
                require(
                    is_version_pinned(resource_id),
                    f"{label}: predecessor uses a latest or unpinned alias",
                    errors,
                )
        candidate = row.get("current_candidate")
        candidate_keys = {"schema_id", "raw_sha256", "byte_count", "status"}
        if exact_keys(candidate, candidate_keys, f"{label}.current_candidate", errors):
            after = current[path]
            expected = {
                "schema_id": after["schema_id"],
                "raw_sha256": sha256(after["raw"]),
                "byte_count": len(after["raw"]),
                "status": "unissued_candidate",
            }
            for key, value in expected.items():
                require(
                    candidate.get(key) == value,
                    f"{label}.current_candidate.{key} must equal {value!r}",
                    errors,
                )
            require(
                candidate.get("schema_id") != predecessor.get("schema_id")
                if isinstance(predecessor, dict)
                else False,
                f"{label}: a reissue must change the exact schema resource ID",
                errors,
            )
            resource_id = candidate.get("schema_id")
            if isinstance(resource_id, str):
                require(
                    is_version_pinned(resource_id),
                    f"{label}: candidate uses a latest or unpinned alias",
                    errors,
                )
            digest = candidate.get("raw_sha256")
            require(
                isinstance(digest, str) and SHA256_RE.fullmatch(digest) is not None,
                f"{label}: current raw SHA-256 is malformed",
                errors,
            )

    new_rows = ledger.get("new_schema_candidates")
    if not isinstance(new_rows, list):
        errors.append("new_schema_candidates must be an array")
        new_rows = []
    actual_new_paths = [
        row.get("path") if isinstance(row, dict) else None for row in new_rows
    ]
    require(
        actual_new_paths == expected_new,
        "new_schema_candidates must be the sorted exact dynamic set of paths absent at source: "
        f"expected={expected_new!r} actual={actual_new_paths!r}",
        errors,
    )
    for index, row in enumerate(new_rows):
        label = f"new_schema_candidates[{index}]"
        row_keys = {"path", "origin", "classification", "current_candidate"}
        if not exact_keys(row, row_keys, label, errors):
            continue
        path = row.get("path")
        require(
            row.get("origin") == "no_path_at_source_checkpoint",
            f"{label}.origin must deny a predecessor",
            errors,
        )
        require(
            row.get("classification") == "new_schema_not_reissue",
            f"{label}.classification must remain new_schema_not_reissue",
            errors,
        )
        if path not in current or path in source:
            errors.append(f"{label}.path is not a dynamic new schema path")
            continue
        candidate = row.get("current_candidate")
        if exact_keys(
            candidate,
            {"schema_id", "raw_sha256", "byte_count", "status"},
            f"{label}.current_candidate",
            errors,
        ):
            after = current[path]
            expected = {
                "schema_id": after["schema_id"],
                "raw_sha256": sha256(after["raw"]),
                "byte_count": len(after["raw"]),
                "status": "unissued_candidate",
            }
            for key, value in expected.items():
                require(
                    candidate.get(key) == value,
                    f"{label}.current_candidate.{key} must equal {value!r}",
                    errors,
                )
            resource_id = candidate.get("schema_id")
            if isinstance(resource_id, str):
                require(
                    is_version_pinned(resource_id),
                    f"{label}: candidate uses a latest or unpinned alias",
                    errors,
                )


def run_known_bad_self_checks(
    ledger: dict[str, Any],
    source: dict[str, dict[str, Any]],
    current: dict[str, dict[str, Any]],
    source_entries: dict[str, str],
) -> tuple[list[str], int]:
    checks: list[tuple[str, Any]] = []
    if ledger.get("reissues"):
        first_reissue_path = ledger["reissues"][0]["path"]
        historical_theft_id = next(
            item["schema_id"]
            for path, item in source.items()
            if path != first_reissue_path
        )
        checks.extend(
            [
                (
                    "missing reissue row",
                    lambda value: value["reissues"].pop(),
                ),
                (
                    "false materialized retention",
                    lambda value: value["reissues"][0]["predecessor"].__setitem__(
                        "retention_mode", "materialized_offline_registry"
                    ),
                ),
                (
                    "admitted candidate",
                    lambda value: value["reissues"][0]["current_candidate"].__setitem__(
                        "status", "admitted"
                    ),
                ),
                (
                    "latest resource alias",
                    lambda value: value["reissues"][0]["current_candidate"].__setitem__(
                        "schema_id", "urn:odeya:schema:latest"
                    ),
                ),
                (
                    "historical source ID theft",
                    lambda value: value["reissues"][0]["current_candidate"].__setitem__(
                        "schema_id", historical_theft_id
                    ),
                ),
            ]
        )
    checks.extend(
        [
            (
                "false complete offline registry",
                lambda value: value["retention_boundary"].__setitem__(
                    "complete_offline_schema_registry", True
                ),
            ),
            (
                "canonical digest while profile blocked",
                lambda value: value["canonical_profile"].__setitem__(
                    "canonical_content_digest", "sha256:" + "0" * 64
                ),
            ),
            (
                "runtime authority claim",
                lambda value: value["proof_boundary"].__setitem__(
                    "runtime_authority", True
                ),
            ),
        ]
    )

    failures: list[str] = []
    for name, mutate in checks:
        candidate = copy.deepcopy(ledger)
        mutate(candidate)
        mutation_errors: list[str] = []
        validate_ledger(candidate, source, current, source_entries, mutation_errors)
        if not mutation_errors:
            failures.append(f"known-bad self-check was accepted: {name}")
    return failures, len(checks)


def main() -> int:
    try:
        resolved_commit = git("rev-parse", "--verify", f"{SOURCE_CHECKPOINT}^{{commit}}")
        resolved_tree = git("rev-parse", "--verify", f"{SOURCE_CHECKPOINT}^{{tree}}")
        if resolved_commit.decode("ascii").strip() != SOURCE_CHECKPOINT:
            raise ValueError("source checkpoint does not resolve to its exact commit identity")
        if resolved_tree.decode("ascii").strip() != SOURCE_TREE:
            raise ValueError("source checkpoint tree identity drifted")
        git("merge-base", "--is-ancestor", SOURCE_CHECKPOINT, "HEAD")
        ledger = load_json(LEDGER_PATH)
        source, current, source_entries, _ = inspect_resources()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"Schema resource reissue lineage: invalid evidence: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    known_bad_count = 0
    validate_ledger(ledger, source, current, source_entries, errors)
    if not errors:
        self_check_errors, known_bad_count = run_known_bad_self_checks(
            ledger, source, current, source_entries
        )
        errors.extend(self_check_errors)

    if errors:
        print("Schema resource reissue lineage: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Schema resource reissue lineage: PASS — "
        f"{len(ledger['reissues'])} reissued existing resources, "
        f"{len(ledger['new_schema_candidates'])} new schema candidates, "
        f"{known_bad_count} known-bad claim mutations rejected; "
        "lineage evidence only, not a "
        "complete offline schema registry, canonical identity, schema admission, "
        "Gate A acceptance, deployment, or runtime authority."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
