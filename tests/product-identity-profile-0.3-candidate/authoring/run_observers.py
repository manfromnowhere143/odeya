#!/usr/bin/env python3
"""Author retained PRQ-002E construction-observation receipts.

This script is an evidence authoring aid, not a validator or authority. It
executes the two source-distinct observers with one answer-free manifest and
writes final receipts only after their complete artifact projections agree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SUITE = ROOT / "tests/product-identity-profile-0.3-candidate"
INPUT_MANIFEST = SUITE / "input-manifest.json"
PYTHON_OBSERVER = SUITE / "python/observer.py"
PYTHON_LOCK = SUITE / "python/dependency-lock.json"
NODE_OBSERVER = SUITE / "node/observer.mjs"
NODE_PACKAGE = SUITE / "node/package.json"
NODE_LOCK = SUITE / "node/package-lock.json"
PYTHON_SOURCE_MANIFEST = SUITE / "python/source-manifest.json"
NODE_SOURCE_MANIFEST = SUITE / "node/source-manifest.json"
RESULTS = SUITE / "results"
PYTHON_RESULT = RESULTS / "python-construction-observation.json"
NODE_RESULT = RESULTS / "node-construction-observation.json"
PYTHON_EXECUTION = RESULTS / "python-execution-receipt.json"
NODE_EXECUTION = RESULTS / "node-execution-receipt.json"
COMPARISON = RESULTS / "comparison-receipt.json"
SUITE_ID = "prq-002e-profile-0.3-construction.0001"
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
OBSERVED_AT_RE = re.compile(
    r"^2026-07-29T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z$"
)
EXPECTED_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "suite_id",
    "observer_id",
    "challenge",
    "artifact_count",
    "artifacts",
    "network_access_requested",
    "expectations_received",
    "peer_source_received",
    "peer_result_received",
    "canonicalization_conformance_claimed",
    "product_identity_computed",
    "authority_claimed",
}
EXPECTED_ROW_KEYS = {
    "sequence_index",
    "role",
    "repository_path",
    "raw_sha256",
    "byte_count",
    "declared_identity",
    "schema_version",
    "raw_number_token_count",
    "integer_token_count",
    "fraction_or_exponent_token_count",
    "negative_zero_token_count",
    "overlong_number_token_count",
    "out_of_safe_integer_domain_token_count",
    "ordered_number_token_sha256",
    "literal_type_number_occurrence_count",
    "domain_literals",
    "profile_literals",
}


def json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    ).encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"observer output contains duplicate key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(token: str) -> Any:
    raise ValueError(f"observer output contains non-finite constant {token}")


def binding(path: Path) -> dict[str, Any]:
    return binding_bytes(path, path.read_bytes())


def binding_bytes(path: Path, raw: bytes) -> dict[str, Any]:
    return {
        "repository_path": path.relative_to(ROOT).as_posix(),
        "raw_sha256": f"sha256:{hashlib.sha256(raw).hexdigest()}",
        "byte_count": len(raw),
    }


def executable_binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "resolved_path_basename": path.name,
        "raw_sha256": f"sha256:{hashlib.sha256(raw).hexdigest()}",
        "byte_count": len(raw),
    }


def source_manifest(
    observer_id: str,
    runtime_family: str,
    entries: list[Path],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_observer_source_manifest",
        "suite_id": SUITE_ID,
        "observer_id": observer_id,
        "runtime_family": runtime_family,
        "source_count": len(entries),
        "sources": [binding(path) for path in entries],
        "declared_source_inventory_closed": True,
        "declared_expectation_source_included": False,
        "declared_peer_source_included": False,
        "declared_peer_result_source_included": False,
        "declared_filesystem_discovery_source_included": False,
        "declared_network_source_included": False,
        "source_inspection_is_not_process_isolation": True,
    }


def run_projection(command: list[str]) -> tuple[dict[str, Any], bytes]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=30,
        check=False,
        env={
            "PATH": os.environ.get("PATH", ""),
            "LANG": "C",
            "LC_ALL": "C",
        },
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"observer failed with {completed.returncode}: "
            f"{completed.stderr.decode('utf-8', 'replace').strip()[:1000]}"
        )
    try:
        text = completed.stdout.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RuntimeError("observer stdout is not valid UTF-8") from exc
    value = json.loads(
        text,
        object_pairs_hook=strict_pairs,
        parse_constant=reject_nonfinite_constant,
    )
    if not isinstance(value, dict):
        raise RuntimeError("observer output root is not an object")
    if completed.stdout != compact_json_bytes(value):
        raise RuntimeError(
            "observer stdout is not the exact closed compact JSON serialization"
        )
    return value, completed.stdout


def comparable_projection(value: dict[str, Any]) -> dict[str, Any]:
    result = dict(value)
    result.pop("observer_id", None)
    return result


def json_type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            json_type_strict_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            json_type_strict_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    return left == right


def expected_inventory() -> list[tuple[str, str]]:
    manifest = json.loads(
        INPUT_MANIFEST.read_text(encoding="utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_nonfinite_constant,
    )
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if not isinstance(artifacts, list) or len(artifacts) != 15:
        raise RuntimeError("authoring input manifest is not the closed 15-row inventory")
    result: list[tuple[str, str]] = []
    for entry in artifacts:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"role", "repository_path"}
            or not isinstance(entry.get("role"), str)
            or not isinstance(entry.get("repository_path"), str)
        ):
            raise RuntimeError("authoring input manifest row shape drifted")
        result.append((entry["role"], entry["repository_path"]))
    if len(set(result)) != len(result):
        raise RuntimeError("authoring input manifest contains duplicate rows")
    return result


def validate_projection(
    value: dict[str, Any],
    observer_id: str,
    challenge: str,
) -> None:
    inventory = expected_inventory()
    if set(value) != EXPECTED_ROOT_KEYS:
        raise RuntimeError(f"{observer_id} result member inventory drifted")
    expected_scalars = {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_observation",
        "suite_id": SUITE_ID,
        "observer_id": observer_id,
        "challenge": challenge,
        "artifact_count": len(inventory),
        "network_access_requested": False,
        "expectations_received": False,
        "peer_source_received": False,
        "peer_result_received": False,
        "canonicalization_conformance_claimed": False,
        "product_identity_computed": False,
        "authority_claimed": False,
    }
    if any(
        type(value.get(key)) is not type(expected)
        or value.get(key) != expected
        for key, expected in expected_scalars.items()
    ):
        raise RuntimeError(f"{observer_id} result identity or nonclaim drifted")
    rows = value.get("artifacts")
    if not isinstance(rows, list) or len(rows) != len(inventory):
        raise RuntimeError(f"{observer_id} result row count drifted")
    for index, (row, expected_row) in enumerate(
        zip(rows, inventory, strict=True), start=1
    ):
        if not isinstance(row, dict) or set(row) != EXPECTED_ROW_KEYS:
            raise RuntimeError(f"{observer_id} row {index} shape drifted")
        role, repository_path = expected_row
        if (
            type(row.get("sequence_index")) is not int
            or row.get("sequence_index") != index
            or row.get("role") != role
            or row.get("repository_path") != repository_path
        ):
            raise RuntimeError(f"{observer_id} row {index} identity drifted")
        live_binding = binding(ROOT / repository_path)
        if (
            row.get("raw_sha256") != live_binding["raw_sha256"]
            or type(row.get("byte_count")) is not int
            or row.get("byte_count") != live_binding["byte_count"]
        ):
            raise RuntimeError(f"{observer_id} row {index} byte binding drifted")
        for count_key in (
            "raw_number_token_count",
            "integer_token_count",
            "fraction_or_exponent_token_count",
            "negative_zero_token_count",
            "overlong_number_token_count",
            "out_of_safe_integer_domain_token_count",
            "literal_type_number_occurrence_count",
        ):
            if type(row.get(count_key)) is not int or row[count_key] < 0:
                raise RuntimeError(
                    f"{observer_id} row {index} has invalid {count_key}"
                )
        if (
            row["raw_number_token_count"] != row["integer_token_count"]
            or row["fraction_or_exponent_token_count"] != 0
            or row["negative_zero_token_count"] != 0
            or row["overlong_number_token_count"] != 0
            or row["out_of_safe_integer_domain_token_count"] != 0
            or row["literal_type_number_occurrence_count"] != 0
        ):
            raise RuntimeError(
                f"{observer_id} row {index} violates the bounded integer-only "
                "construction observation"
            )
        if (
            not isinstance(row.get("domain_literals"), list)
            or not isinstance(row.get("profile_literals"), list)
            or not all(isinstance(item, str) for item in row["domain_literals"])
            or not all(isinstance(item, str) for item in row["profile_literals"])
        ):
            raise RuntimeError(f"{observer_id} row {index} literal census drifted")


def execution_receipt(
    observer_id: str,
    observed_at: str,
    challenge: str,
    runtime_family: str,
    runtime_version: str,
    executable: Path,
    observer: Path,
    executable_pre_binding: dict[str, Any],
    executable_post_binding: dict[str, Any],
    observer_pre_binding: dict[str, Any],
    observer_post_binding: dict[str, Any],
    input_pre_binding: dict[str, Any],
    input_post_binding: dict[str, Any],
    source_manifest_binding: dict[str, Any],
    result_binding: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_execution_receipt",
        "suite_id": SUITE_ID,
        "observer_id": observer_id,
        "observed_at": observed_at,
        "challenge": challenge,
        "argv_contract": [
            *(["-I"] if runtime_family == "CPython" else []),
            observer.relative_to(ROOT).as_posix(),
            "--root",
            "<repository-root>",
            "--manifest",
            INPUT_MANIFEST.relative_to(ROOT).as_posix(),
            "--challenge",
            challenge,
        ],
        "runtime": {
            "family": runtime_family,
            "version": runtime_version,
            "resolved_executable_basename": executable.name,
            "pre_execution_binding": executable_pre_binding,
            "post_execution_binding": executable_post_binding,
            "dependency_closure_complete": False,
        },
        "observer_binding": {
            "pre_execution": observer_pre_binding,
            "post_execution": observer_post_binding,
        },
        "source_manifest_binding": source_manifest_binding,
        "input_manifest_binding": {
            "pre_execution": input_pre_binding,
            "post_execution": input_post_binding,
        },
        "result_binding": result_binding,
        "environment_key_inventory": ["LANG", "LC_ALL", "PATH"],
        "stdin_received": False,
        "network_access_requested": False,
        "expectations_received": False,
        "peer_source_received": False,
        "peer_result_received": False,
        "filesystem_isolation_proven": False,
        "runtime_dependency_closure_complete": False,
        "observed_at_is_independently_witnessed": False,
        "historical_process_independently_witnessed": False,
        "canonicalization_conformance_claimed": False,
        "product_identity_computed": False,
        "authority_claimed": False,
    }


def comparison_receipt(
    observed_at: str,
    challenge: str,
    common_projection: dict[str, Any],
    python_source_raw: bytes,
    node_source_raw: bytes,
    python_result_raw: bytes,
    node_result_raw: bytes,
    python_execution_raw: bytes,
    node_execution_raw: bytes,
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_comparison_receipt",
        "suite_id": SUITE_ID,
        "observed_at": observed_at,
        "challenge": challenge,
        "observer_count": 2,
        "observer_ids": [
            "python-stdlib-construction-observer.0001",
            "nodejs-native-construction-observer.0001",
        ],
        "input_manifest_binding": binding(INPUT_MANIFEST),
        "python_source_manifest_binding": binding_bytes(
            PYTHON_SOURCE_MANIFEST, python_source_raw
        ),
        "node_source_manifest_binding": binding_bytes(
            NODE_SOURCE_MANIFEST, node_source_raw
        ),
        "python_result_binding": binding_bytes(PYTHON_RESULT, python_result_raw),
        "node_result_binding": binding_bytes(NODE_RESULT, node_result_raw),
        "python_execution_receipt_binding": binding_bytes(
            PYTHON_EXECUTION, python_execution_raw
        ),
        "node_execution_receipt_binding": binding_bytes(
            NODE_EXECUTION, node_execution_raw
        ),
        "complete_artifact_projection_hash_framing": (
            "sha256_over_utf8_ascii_json_sort_keys_compact_with_single_lf_v1"
        ),
        "complete_artifact_projection_sha256": (
            "sha256:"
            + hashlib.sha256(compact_json_bytes(common_projection)).hexdigest()
        ),
        "complete_projection_agreement": True,
        "artifact_count": common_projection.get("artifact_count"),
        "bounded_15_row_artifact_projection_observed": True,
        "strict_duplicate_detection_agreement_proven": False,
        "literal_type_number_occurrence_count_is_applicability_proof": False,
        "static_schema_position_inventory_proved_by_this_observation": False,
        "per_subject_raw_applicability_traces_complete": False,
        "generic_schema_path_evaluation_proven": False,
        "canonicalization_conformance_complete": False,
        "organizational_independence_proven": False,
        "independent_host_reproduction_complete": False,
        "historical_process_independently_witnessed": False,
        "coherent_peer_output_substitution_excluded": False,
        "product_identity_computed": False,
        "profile_issued": False,
        "schema_resources_admitted": False,
        "gate_a_complete": False,
        "runtime_authorized": False,
        "publication_authorized": False,
    }


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def ensure_safe_install_parent(path: Path) -> None:
    """Create only real, suite-contained destination directories."""

    try:
        relative = path.relative_to(SUITE)
    except ValueError as exc:
        raise RuntimeError(f"install target escapes suite: {path}") from exc
    if relative == Path(".") or len(relative.parts) < 2:
        raise RuntimeError(f"install target is not a suite child file: {path}")
    if SUITE.is_symlink() or not SUITE.is_dir():
        raise RuntimeError("suite root must be a real directory")

    current = SUITE
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise RuntimeError(
                f"install parent is a symlink: {current.relative_to(ROOT)}"
            )
        if current.exists():
            if not current.is_dir():
                raise RuntimeError(
                    f"install parent is not a directory: {current.relative_to(ROOT)}"
                )
        else:
            current.mkdir()
            fsync_directory(current.parent)
        if not current.resolve(strict=True).is_relative_to(
            SUITE.resolve(strict=True)
        ):
            raise RuntimeError(
                f"resolved install parent escapes suite: {current.relative_to(ROOT)}"
            )

    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise RuntimeError(
            f"install target is not absent or a regular file: "
            f"{path.relative_to(ROOT)}"
        )


def parse_planned_json(planned: dict[Path, bytes]) -> dict[Path, dict[str, Any]]:
    parsed: dict[Path, dict[str, Any]] = {}
    for path, raw in planned.items():
        try:
            text = raw.decode("utf-8", errors="strict")
            value = json.loads(
                text,
                object_pairs_hook=strict_pairs,
                parse_constant=reject_nonfinite_constant,
            )
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"planned retained JSON is invalid: {path.relative_to(ROOT)}"
            ) from exc
        if not isinstance(value, dict):
            raise RuntimeError(
                f"planned retained JSON root is not an object: "
                f"{path.relative_to(ROOT)}"
            )
        parsed[path] = value
    return parsed


def validate_planned_graph(
    planned: dict[Path, bytes],
    *,
    observed_at: str,
    challenge: str,
    python_executable: Path,
    node_executable: Path,
    node_version: str,
) -> None:
    """Recompute every retained edge and live subject binding."""

    expected_paths = {
        PYTHON_SOURCE_MANIFEST,
        NODE_SOURCE_MANIFEST,
        PYTHON_RESULT,
        NODE_RESULT,
        PYTHON_EXECUTION,
        NODE_EXECUTION,
        COMPARISON,
    }
    if set(planned) != expected_paths:
        missing = sorted(
            path.relative_to(ROOT).as_posix() for path in expected_paths - set(planned)
        )
        additional = sorted(
            path.relative_to(ROOT).as_posix() for path in set(planned) - expected_paths
        )
        raise RuntimeError(
            "planned retained graph inventory drifted: "
            f"missing={missing}, additional={additional}"
        )

    parsed = parse_planned_json(planned)
    python_source_expected = json_bytes(
        source_manifest(
            "python-stdlib-construction-observer.0001",
            "CPython",
            [PYTHON_OBSERVER, PYTHON_LOCK],
        )
    )
    node_source_expected = json_bytes(
        source_manifest(
            "nodejs-native-construction-observer.0001",
            "Node.js",
            [NODE_OBSERVER, NODE_PACKAGE, NODE_LOCK],
        )
    )
    if planned[PYTHON_SOURCE_MANIFEST] != python_source_expected:
        raise RuntimeError("Python source manifest has a stale or unexpected binding")
    if planned[NODE_SOURCE_MANIFEST] != node_source_expected:
        raise RuntimeError("Node source manifest has a stale or unexpected binding")

    python_projection = parsed[PYTHON_RESULT]
    node_projection = parsed[NODE_RESULT]
    if planned[PYTHON_RESULT] != compact_json_bytes(python_projection):
        raise RuntimeError("Python result framing drifted")
    if planned[NODE_RESULT] != compact_json_bytes(node_projection):
        raise RuntimeError("Node result framing drifted")
    validate_projection(
        python_projection,
        "python-stdlib-construction-observer.0001",
        challenge,
    )
    validate_projection(
        node_projection,
        "nodejs-native-construction-observer.0001",
        challenge,
    )
    common_projection = comparable_projection(python_projection)
    if not json_type_strict_equal(
        common_projection,
        comparable_projection(node_projection),
    ):
        raise RuntimeError("retained source-separated projections disagree")

    python_executable_live = executable_binding(python_executable)
    node_executable_live = executable_binding(node_executable)
    python_observer_live = binding(PYTHON_OBSERVER)
    node_observer_live = binding(NODE_OBSERVER)
    input_live = binding(INPUT_MANIFEST)
    expected_python_execution = json_bytes(
        execution_receipt(
            "python-stdlib-construction-observer.0001",
            observed_at,
            challenge,
            "CPython",
            platform.python_version(),
            python_executable,
            PYTHON_OBSERVER,
            python_executable_live,
            python_executable_live,
            python_observer_live,
            python_observer_live,
            input_live,
            input_live,
            binding_bytes(PYTHON_SOURCE_MANIFEST, planned[PYTHON_SOURCE_MANIFEST]),
            binding_bytes(PYTHON_RESULT, planned[PYTHON_RESULT]),
        )
    )
    expected_node_execution = json_bytes(
        execution_receipt(
            "nodejs-native-construction-observer.0001",
            observed_at,
            challenge,
            "Node.js",
            node_version.removeprefix("v"),
            node_executable,
            NODE_OBSERVER,
            node_executable_live,
            node_executable_live,
            node_observer_live,
            node_observer_live,
            input_live,
            input_live,
            binding_bytes(NODE_SOURCE_MANIFEST, planned[NODE_SOURCE_MANIFEST]),
            binding_bytes(NODE_RESULT, planned[NODE_RESULT]),
        )
    )
    if planned[PYTHON_EXECUTION] != expected_python_execution:
        raise RuntimeError("Python execution receipt edge or expected byte drifted")
    if planned[NODE_EXECUTION] != expected_node_execution:
        raise RuntimeError("Node execution receipt edge or expected byte drifted")

    expected_comparison = json_bytes(
        comparison_receipt(
            observed_at,
            challenge,
            common_projection,
            planned[PYTHON_SOURCE_MANIFEST],
            planned[NODE_SOURCE_MANIFEST],
            planned[PYTHON_RESULT],
            planned[NODE_RESULT],
            planned[PYTHON_EXECUTION],
            planned[NODE_EXECUTION],
        )
    )
    if planned[COMPARISON] != expected_comparison:
        raise RuntimeError("comparison receipt edge or expected byte drifted")


def stage_validate_install(
    planned: dict[Path, bytes],
    *,
    observed_at: str,
    challenge: str,
    python_executable: Path,
    node_executable: Path,
    node_version: str,
) -> None:
    """Install a validated graph from same-filesystem staging, receipt last."""

    if COMPARISON not in planned:
        raise RuntimeError("comparison receipt is absent from the planned graph")
    for final_path in planned:
        ensure_safe_install_parent(final_path)
    staging = Path(
        tempfile.mkdtemp(prefix=".prq-002e-observation-staging-", dir=SUITE)
    )
    try:
        staged_paths: dict[Path, Path] = {}
        for final_path, raw in planned.items():
            relative = final_path.relative_to(SUITE)
            staged = staging / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            with staged.open("xb") as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            staged_paths[final_path] = staged
        for directory in sorted(
            {path.parent for path in staged_paths.values()},
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            fsync_directory(directory)
        fsync_directory(staging)

        for final_path, staged in staged_paths.items():
            if staged.read_bytes() != planned[final_path]:
                raise RuntimeError(
                    f"staging readback mismatch: {final_path.relative_to(ROOT)}"
                )
        validate_planned_graph(
            planned,
            observed_at=observed_at,
            challenge=challenge,
            python_executable=python_executable,
            node_executable=node_executable,
            node_version=node_version,
        )

        install_order = sorted(
            (path for path in planned if path != COMPARISON),
            key=lambda item: item.relative_to(SUITE).as_posix(),
        )
        for final_path in install_order:
            ensure_safe_install_parent(final_path)
            os.replace(staged_paths[final_path], final_path)
            with final_path.open("rb") as handle:
                os.fsync(handle.fileno())
            fsync_directory(final_path.parent)

        # Rebind every live input and retained edge after the non-authoritative
        # artifacts are installed. Only then may the external receipt replace
        # its predecessor.
        live_before_receipt = {
            path: (
                planned[COMPARISON]
                if path == COMPARISON
                else path.read_bytes()
            )
            for path in planned
        }
        validate_planned_graph(
            live_before_receipt,
            observed_at=observed_at,
            challenge=challenge,
            python_executable=python_executable,
            node_executable=node_executable,
            node_version=node_version,
        )
        ensure_safe_install_parent(COMPARISON)
        os.replace(staged_paths[COMPARISON], COMPARISON)
        with COMPARISON.open("rb") as handle:
            os.fsync(handle.fileno())
        fsync_directory(COMPARISON.parent)

        live_installed = {
            path: path.read_bytes()
            for path in planned
        }
        for final_path, raw in live_installed.items():
            if raw != planned[final_path]:
                raise RuntimeError(
                    f"installed readback mismatch: {final_path.relative_to(ROOT)}"
                )
        validate_planned_graph(
            live_installed,
            observed_at=observed_at,
            challenge=challenge,
            python_executable=python_executable,
            node_executable=node_executable,
            node_version=node_version,
        )
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-bin", required=True)
    parser.add_argument("--challenge", required=True)
    parser.add_argument("--observed-at", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if CHALLENGE_RE.fullmatch(args.challenge) is None:
        raise ValueError("invalid challenge")
    if OBSERVED_AT_RE.fullmatch(args.observed_at) is None:
        raise ValueError("observed-at must be a 2026-07-29 UTC timestamp")
    try:
        parsed_observed_at = datetime.fromisoformat(
            args.observed_at.removesuffix("Z") + "+00:00"
        )
    except ValueError as exc:
        raise ValueError("observed-at is not a valid UTC datetime") from exc
    if (
        parsed_observed_at.tzinfo != timezone.utc
        or parsed_observed_at.date().isoformat() != "2026-07-29"
    ):
        raise ValueError("observed-at must be a valid 2026-07-29 UTC datetime")
    if platform.python_version() != "3.14.2":
        raise RuntimeError("authoring requires pinned CPython 3.14.2")
    python_executable = Path(getattr(sys, "_base_executable", sys.executable)).resolve(
        strict=True
    )
    node_executable = Path(args.node_bin).resolve(strict=True)
    node_version = subprocess.run(
        [str(node_executable), "--version"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    ).stdout.strip()
    if node_version != "v24.18.0":
        raise RuntimeError(f"authoring requires Node v24.18.0, got {node_version!r}")

    python_source_raw = json_bytes(
        source_manifest(
            "python-stdlib-construction-observer.0001",
            "CPython",
            [PYTHON_OBSERVER, PYTHON_LOCK],
        )
    )
    node_source_raw = json_bytes(
        source_manifest(
            "nodejs-native-construction-observer.0001",
            "Node.js",
            [NODE_OBSERVER, NODE_PACKAGE, NODE_LOCK],
        )
    )
    python_executable_pre = executable_binding(python_executable)
    node_executable_pre = executable_binding(node_executable)
    python_observer_pre = binding(PYTHON_OBSERVER)
    node_observer_pre = binding(NODE_OBSERVER)
    input_pre = binding(INPUT_MANIFEST)

    common_args = [
        "--root",
        str(ROOT),
        "--manifest",
        str(INPUT_MANIFEST),
        "--challenge",
        args.challenge,
    ]
    python_projection, python_stdout = run_projection(
        [str(python_executable), "-I", str(PYTHON_OBSERVER), *common_args]
    )
    node_projection, node_stdout = run_projection(
        [str(node_executable), str(NODE_OBSERVER), *common_args]
    )
    validate_projection(
        python_projection,
        "python-stdlib-construction-observer.0001",
        args.challenge,
    )
    validate_projection(
        node_projection,
        "nodejs-native-construction-observer.0001",
        args.challenge,
    )
    if not json_type_strict_equal(
        comparable_projection(python_projection),
        comparable_projection(node_projection),
    ):
        raise RuntimeError("source-separated complete artifact projections disagree")
    python_executable_post = executable_binding(python_executable)
    node_executable_post = executable_binding(node_executable)
    python_observer_post = binding(PYTHON_OBSERVER)
    node_observer_post = binding(NODE_OBSERVER)
    input_post = binding(INPUT_MANIFEST)
    if not all(
        json_type_strict_equal(before, after)
        for before, after in (
            (python_executable_pre, python_executable_post),
            (node_executable_pre, node_executable_post),
            (python_observer_pre, python_observer_post),
            (node_observer_pre, node_observer_post),
            (input_pre, input_post),
        )
    ):
        raise RuntimeError("executable, observer, or input bytes changed during execution")

    python_execution_document = execution_receipt(
        "python-stdlib-construction-observer.0001",
        args.observed_at,
        args.challenge,
        "CPython",
        platform.python_version(),
        python_executable,
        PYTHON_OBSERVER,
        python_executable_pre,
        python_executable_post,
        python_observer_pre,
        python_observer_post,
        input_pre,
        input_post,
        binding_bytes(PYTHON_SOURCE_MANIFEST, python_source_raw),
        binding_bytes(PYTHON_RESULT, python_stdout),
    )
    node_execution_document = execution_receipt(
        "nodejs-native-construction-observer.0001",
        args.observed_at,
        args.challenge,
        "Node.js",
        node_version.removeprefix("v"),
        node_executable,
        NODE_OBSERVER,
        node_executable_pre,
        node_executable_post,
        node_observer_pre,
        node_observer_post,
        input_pre,
        input_post,
        binding_bytes(NODE_SOURCE_MANIFEST, node_source_raw),
        binding_bytes(NODE_RESULT, node_stdout),
    )
    python_execution_raw = json_bytes(python_execution_document)
    node_execution_raw = json_bytes(node_execution_document)
    common = comparable_projection(python_projection)
    comparison = comparison_receipt(
        args.observed_at,
        args.challenge,
        common,
        python_source_raw,
        node_source_raw,
        python_stdout,
        node_stdout,
        python_execution_raw,
        node_execution_raw,
    )
    comparison_raw = json_bytes(comparison)
    planned = {
        PYTHON_SOURCE_MANIFEST: python_source_raw,
        NODE_SOURCE_MANIFEST: node_source_raw,
        PYTHON_RESULT: python_stdout,
        NODE_RESULT: node_stdout,
        PYTHON_EXECUTION: python_execution_raw,
        NODE_EXECUTION: node_execution_raw,
        COMPARISON: comparison_raw,
    }
    stage_validate_install(
        planned,
        observed_at=args.observed_at,
        challenge=args.challenge,
        python_executable=python_executable,
        node_executable=node_executable,
        node_version=node_version,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
