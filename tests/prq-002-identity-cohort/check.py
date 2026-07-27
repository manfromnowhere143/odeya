#!/usr/bin/env python3
"""Validate the non-issuable PRQ-002A structural identity probe cohort.

The default path validates retained bytes, complete schema conformance, exact
digest preimages, the graph, one-mutation refusals, source bindings, comparison
evidence, and execution receipts without requiring the external canonicalizer
packages. ``--recompute-all`` additionally verifies exact installed dependency
payloads, executes explicitly selected locked Python and Node implementations,
and demands byte-identical retained output.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import secrets
import subprocess
import sys
import sysconfig
import tarfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


def startup_file_binding(path: Path) -> dict[str, Any] | None:
    """Bind the parent executable before any suite-controlled bytes are read."""
    digest = hashlib.sha256()
    count = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
                count += len(chunk)
    except OSError:
        return None
    return {
        "raw_sha256": f"sha256:{digest.hexdigest()}",
        "byte_count": count,
    }


PARENT_PYTHON_BASE_INVOCATION = Path(
    getattr(sys, "_base_executable", sys.executable)
)
try:
    PARENT_PYTHON_ANCHOR = PARENT_PYTHON_BASE_INVOCATION.resolve(strict=True)
except OSError:
    PARENT_PYTHON_ANCHOR = PARENT_PYTHON_BASE_INVOCATION.absolute()
PARENT_PYTHON_ANCHOR_BINDING = startup_file_binding(PARENT_PYTHON_ANCHOR)
PARENT_PYTHON_VERSION = platform.python_version()
PARENT_PYTHON_PREFIX = sys.prefix


SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
INPUT_MANIFEST_PATH = SUITE / "input-manifest.json"
SUITE_MANIFEST_PATH = SUITE / "manifest.json"
CASES_PATH = SUITE / "cases.json"
CANDIDATE_PATH = SUITE / "fixtures/candidate-cohort.probe.json"
PYTHON_RUNNER = SUITE / "python/runner.py"
PYTHON_LOCK = SUITE / "python/requirements.lock"
PYTHON_SOURCE_MANIFEST = SUITE / "python/source-manifest.json"
NODE_RUNNER = SUITE / "node/runner.mjs"
NODE_PACKAGE = SUITE / "node/package.json"
NODE_LOCK = SUITE / "node/package-lock.json"
NODE_SOURCE_MANIFEST = SUITE / "node/source-manifest.json"
PYTHON_RESULT = SUITE / "results/python-rfc8785-0.1.4.json"
NODE_RESULT = SUITE / "results/node-canonicalize-3.0.0.json"
COMPARISON = SUITE / "results/comparison-receipt.json"
PYTHON_EXECUTION = SUITE / "results/python-execution-receipt.json"
NODE_EXECUTION = SUITE / "results/node-execution-receipt.json"
PROFILE_CORE_PATH = ROOT / "architecture/prq-002-identity-probe-profile-core.json"
PYTHON_VERSION_DECLARATION = ROOT / ".python-version"
NODE_VERSION_DECLARATION = ROOT / "tools/repository-release/.node-version"
TOOLCHAIN_LOCK = ROOT / "tools/repository-release/toolchain.lock.json"
NODE_INSTALLER = ROOT / "scripts/ci/install-node.sh"
PROBE_STATUS = "test_only_non_issuable_structural_probe"
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_NODE_VERSION = "24.18.0"
EXPECTED_PYTHON_VERSION = "3.14.2"
EXPECTED_FILES = {
    "README.md",
    "check.py",
    "manifest.json",
    "input-manifest.json",
    "cases.json",
    "fixtures/candidate-cohort.probe.json",
    "python/runner.py",
    "python/requirements.lock",
    "python/source-manifest.json",
    "node/runner.mjs",
    "node/package.json",
    "node/package-lock.json",
    "node/source-manifest.json",
    "results/python-rfc8785-0.1.4.json",
    "results/node-canonicalize-3.0.0.json",
    "results/comparison-receipt.json",
    "results/python-execution-receipt.json",
    "results/node-execution-receipt.json",
}
SCHEMA_MEMBER_ROLES = (
    "aggregate_state_member_probe_schema",
    "event_member_probe_schema",
    "identity_probe_profile_schema",
    "ordered_commitment_probe_schema",
    "pure_snapshot_probe_schema",
    "reducer_member_probe_schema",
    "schema_member_probe_schema",
    "structural_event_schema",
    "structural_state_schema",
)
FAMILIES = (
    "schema_registry",
    "aggregate_state_subject_registry",
    "reducer_registry",
    "event_contract_registry",
)
FALSE_AUTHORITY_KEYS = {
    "canonical_identity_issued",
    "registry_admission",
    "engine_contract_root_binding",
    "gate_a_acceptance",
    "runtime_authority",
    "external_effect_authority",
    "publication_authority",
}
EXPECTED_PARSER_SEMANTICS = {
    "positive_underflow": {
        "input": "1e-400",
        "outcome": "accepted",
        "ieee754_conversion": "positive_zero",
    },
    "negative_underflow": {
        "input": "-1e-400",
        "outcome": "accepted",
        "ieee754_conversion": "negative_zero",
    },
    "lexical_negative_zero": {
        "input": "-0",
        "outcome": "refused",
        "error": "strict_input_negative_zero",
    },
}
EXPECTED_DEPENDENCY_PAYLOADS = {
    "python": {
        "package": "rfc8785",
        "version": "0.1.4",
        "path_basis": "distribution_root_relative",
        "inventory_policy": (
            "exact_immutable_wheel_payload_and_reject_package_import_cache"
        ),
        "file_count": 6,
        "files": [
            {
                "sequence_index": 0,
                "relative_path": "rfc8785/__init__.py",
                "raw_sha256": (
                    "sha256:"
                    "fa44927afd547caf7547247078bcf28863d1e69caf116d258c532b3f20ffd154"
                ),
                "byte_count": 496,
            },
            {
                "sequence_index": 1,
                "relative_path": "rfc8785/_impl.py",
                "raw_sha256": (
                    "sha256:"
                    "c25bc3a046528482d53bee3487b837f31dd9c05f33e8f13288c7aab320932cec"
                ),
                "byte_count": 7251,
            },
            {
                "sequence_index": 2,
                "relative_path": "rfc8785/py.typed",
                "raw_sha256": (
                    "sha256:"
                    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                ),
                "byte_count": 0,
            },
            {
                "sequence_index": 3,
                "relative_path": "rfc8785-0.1.4.dist-info/LICENSE",
                "raw_sha256": (
                    "sha256:"
                    "0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"
                ),
                "byte_count": 10174,
            },
            {
                "sequence_index": 4,
                "relative_path": "rfc8785-0.1.4.dist-info/METADATA",
                "raw_sha256": (
                    "sha256:"
                    "9dfbf420c8c18077dd7697ec12fe2838b5901683573ae128df2d3403330f7aa9"
                ),
                "byte_count": 3379,
            },
            {
                "sequence_index": 5,
                "relative_path": "rfc8785-0.1.4.dist-info/WHEEL",
                "raw_sha256": (
                    "sha256:"
                    "1196c6921ec87b83e865f450f08d19b8ff5592537f4ef719e83484e546abe33e"
                ),
                "byte_count": 81,
            },
        ],
    },
    "node": {
        "package": "canonicalize",
        "version": "3.0.0",
        "path_basis": "package_root_relative",
        "inventory_policy": "exact_package_directory",
        "file_count": 6,
        "files": [
            {
                "sequence_index": 0,
                "relative_path": "LICENSE",
                "raw_sha256": (
                    "sha256:"
                    "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"
                ),
                "byte_count": 11357,
            },
            {
                "sequence_index": 1,
                "relative_path": "README.md",
                "raw_sha256": (
                    "sha256:"
                    "bf7bb912972b2787b393d3618a965d742b26185200fabce330df9de02d607844"
                ),
                "byte_count": 1773,
            },
            {
                "sequence_index": 2,
                "relative_path": "bin/canonicalize.js",
                "raw_sha256": (
                    "sha256:"
                    "cf81826eee228ef4d56f14f2272e635f38bc262dd4d0faa0e2b1065a0ae388f0"
                ),
                "byte_count": 395,
            },
            {
                "sequence_index": 3,
                "relative_path": "lib/canonicalize.d.ts",
                "raw_sha256": (
                    "sha256:"
                    "5eba409e1fe34c86e46af829f1f236645b654e405e3377277b2baeb5e5352124"
                ),
                "byte_count": 90,
            },
            {
                "sequence_index": 4,
                "relative_path": "lib/canonicalize.js",
                "raw_sha256": (
                    "sha256:"
                    "c0fd652bd174455567dcbbbab0f306fe5d40a9fb13b0f184b46aca083b29546e"
                ),
                "byte_count": 1334,
            },
            {
                "sequence_index": 5,
                "relative_path": "package.json",
                "raw_sha256": (
                    "sha256:"
                    "c9bcb2590b7a2ded24ea63582f2a47cbafb934733ed9429cef120e8d6e55bea9"
                ),
                "byte_count": 1365,
            },
        ],
    },
}
HISTORICAL_WORKTREE = (
    "/Users/danielwahnich/workspace/"
    "odeya-prq-013-context-review-20260721"
)
HISTORICAL_EXECUTIONS = {
    "python": {
        "host": {"operating_system": "Darwin", "machine": "arm64"},
        "argv": [
            f"{HISTORICAL_WORKTREE}/.venv-architecture/bin/python",
            "-I",
            "-S",
            "-B",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "python/runner.py"
            ),
            "--input",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "fixtures/candidate-cohort.probe.json"
            ),
            "--manifest",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "input-manifest.json"
            ),
            "--cases",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "cases.json"
            ),
            "--rfc8785-package-root",
            (
                f"{HISTORICAL_WORKTREE}/.venv-architecture/lib/"
                "python3.14/site-packages/rfc8785"
            ),
            "--attestation-challenge",
            (
                "challenge-v1:"
                "0663f4444c5562db62ed3fc23a408b4f348b733a9dc4475ab39d0466328abcaa"
            ),
            "--emit-execution-attestation",
        ],
        "executable_observation": {
            "invocation_path": (
                f"{HISTORICAL_WORKTREE}/.venv-architecture/bin/python"
            ),
            "resolved_path": (
                "/opt/homebrew/Cellar/python@3.14/3.14.2_1/Frameworks/"
                "Python.framework/Versions/3.14/bin/python3.14"
            ),
            "raw_sha256": (
                "sha256:"
                "3b6b69c61fd3765ab911d701cd17293b4a9154a0cb4973b546f05847f9a164c6"
            ),
            "byte_count": 52640,
        },
        "observation_scope": (
            "historical_host_specific_not_a_cross_host_recomputation_"
            "requirement"
        ),
    },
    "node": {
        "host": {"operating_system": "Darwin", "machine": "arm64"},
        "argv": [
            (
                "/var/folders/fl/_txhnxc90xl00n3xtq0r4nq40000gn/T/"
                "odeya-release-tools/node/v24.18.0/darwin_arm64/bin/node"
            ),
            "--disable-proto=throw",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "node/runner.mjs"
            ),
            "--input",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "fixtures/candidate-cohort.probe.json"
            ),
            "--manifest",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "input-manifest.json"
            ),
            "--cases",
            (
                f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
                "cases.json"
            ),
            "--attestation-challenge",
            (
                "challenge-v1:"
                "6a8e844dfe83fa43955c19b9c10298454ac1f471e49ae47358dbcbde6841494a"
            ),
            "--emit-execution-attestation",
        ],
        "executable_observation": {
            "invocation_path": (
                "/var/folders/fl/_txhnxc90xl00n3xtq0r4nq40000gn/T/"
                "odeya-release-tools/node/v24.18.0/darwin_arm64/bin/node"
            ),
            "resolved_path": (
                "/private/var/folders/fl/_txhnxc90xl00n3xtq0r4nq40000gn/T/"
                "odeya-release-tools/node/v24.18.0/darwin_arm64/bin/node"
            ),
            "raw_sha256": (
                "sha256:"
                "ee6fb0e015284d83a91e8ec5213f43a157f8a392b58555301682892ba928c04a"
            ),
            "byte_count": 120965360,
        },
        "observation_scope": (
            "historical_host_specific_not_a_cross_host_recomputation_"
            "requirement"
        ),
    },
}
HISTORICAL_PROCESS_OUTPUTS = {
    "python": {
        "process_stdout_binding": {
            "raw_sha256": (
                "sha256:"
                "e4d37f58ed62463c55112b6737913ce5896421b6209d56f8ee226648aaeb9168"
            ),
            "byte_count": 147193,
            "line_count": 2,
            "framing": "rfc8785_attestation_line_then_rfc8785_result_line",
        },
        "attestation_line_binding": {
            "raw_sha256": (
                "sha256:"
                "b6f5bfa7e1a62dddb66eb38c7e81af3da7904573fe0e7a386d6e7e63f93bc460"
            ),
            "byte_count": 3539,
            "stdout_line": 1,
        },
    },
    "node": {
        "process_stdout_binding": {
            "raw_sha256": (
                "sha256:"
                "32673f59b553c57437f36f07f09e0099b2942f0955b1e7139f9ab9813afd0efe"
            ),
            "byte_count": 147094,
            "line_count": 2,
            "framing": "rfc8785_attestation_line_then_rfc8785_result_line",
        },
        "attestation_line_binding": {
            "raw_sha256": (
                "sha256:"
                "cff92b14969457c8f40d69a2b368de54dcf0250643ce369e0f685633b884b312"
            ),
            "byte_count": 3314,
            "stdout_line": 1,
        },
    },
}
PORTABLE_RECOMPUTATION_CONTRACT = {
    "checker_path": "tests/prq-002-identity-cohort/check.py",
    "mode_flag": "--recompute-all",
    "python_selector_flag": "--python-executable",
    "node_selector_flag": "--node-executable",
    "absolute_executable_paths_required": True,
    "selected_runtime_version_required": True,
    "selected_runtime_provenance_required": True,
    "runtime_executable_pre_and_post_binding_required": True,
    "installed_dependency_payload_bytes_required": True,
    "child_execution_attestation_required": True,
    "fresh_challenge_and_result_line_binding_required": True,
    "python_isolated_no_site_no_bytecode_mode_required": True,
    "node_archive_regular_member_binding_required": True,
    "python_site_initialization_disabled": True,
    "historical_executable_byte_identity_required": False,
}
EXPECTED_SUITE_MANIFEST = {
    "schema_version": "0.1.0",
    "artifact_class": "prq_002_identity_probe_suite_manifest",
    "suite_id": "prq-002-identity-cohort.0001",
    "status": PROBE_STATUS,
    "decision_ref": (
        "docs/decisions/"
        "0099-freeze-prq-002a-structural-identity-probe-layer.md"
    ),
    "profile_id": "urn:odeya:canonicalization:prq-002-identity-probe-jcs-0.1",
    "profile_version": "0.1.0",
    "digest_framing": {
        "scope": "probe_local_not_a_production_canonical_envelope",
        "exact_members": [
            "digest_contract",
            "resolved_subject_schema",
            "projection",
        ],
        "preimage": "utf8_rfc8785_bytes_of_exact_scoped_digest_input",
        "algorithm": "sha256",
        "result_lexical_form": "sha256_colon_64_lowercase_hex",
    },
    "cohort_census": {
        "profile_instances": 1,
        "schema_members": 9,
        "graph_members": 3,
        "members": 12,
        "commitments": 4,
        "snapshots": 4,
        "total_probe_objects": 21,
    },
    "retained_paths": {
        "input_manifest": "tests/prq-002-identity-cohort/input-manifest.json",
        "candidate_cohort": (
            "tests/prq-002-identity-cohort/fixtures/"
            "candidate-cohort.probe.json"
        ),
        "cases": "tests/prq-002-identity-cohort/cases.json",
        "python_result": (
            "tests/prq-002-identity-cohort/results/"
            "python-rfc8785-0.1.4.json"
        ),
        "node_result": (
            "tests/prq-002-identity-cohort/results/"
            "node-canonicalize-3.0.0.json"
        ),
        "comparison_receipt": (
            "tests/prq-002-identity-cohort/results/comparison-receipt.json"
        ),
        "python_execution_receipt": (
            "tests/prq-002-identity-cohort/results/"
            "python-execution-receipt.json"
        ),
        "node_execution_receipt": (
            "tests/prq-002-identity-cohort/results/"
            "node-execution-receipt.json"
        ),
    },
    "implementation_contract": {
        "roles": ["python", "node"],
        "shared_evaluator_source_allowed": False,
        "peer_result_consumption_allowed": False,
        "expected_result_fixture_consumption_allowed": False,
        "shared_inputs": [
            "nine exact architecture schema resources",
            "one exact standalone probe profile core",
            "one exact candidate cohort",
            "one expectation-bearing single-mutation case manifest",
            "this suite manifest",
            "the input manifest",
        ],
        "python": {
            "runtime": "CPython 3.14.2",
            "package": "rfc8785",
            "package_version": "0.1.4",
            "entrypoint": "verified_source_exec:rfc8785/_impl.py:dumps",
        },
        "node": {
            "runtime": "Node.js 24.18.0",
            "package": "canonicalize",
            "package_version": "3.0.0",
            "entrypoint": "canonicalize default export",
        },
    },
    "claims": {
        "strict_parser_exercised": True,
        "raw_schema_bytes_bound": True,
        "member_forward_edges_recomputed": True,
        "flat_ordered_member_map_recomputed": True,
        "pure_homogeneous_snapshots_recomputed": True,
        "selected_runtime_provenance_verified": True,
        "runtime_executable_pre_and_post_binding_verified": True,
        "child_execution_attestation_verified": True,
        "fresh_challenge_and_result_line_binding_verified": True,
        "python_isolated_mode_verified": True,
        "node_archive_regular_member_binding_verified": True,
        "python_site_initialization_disabled": True,
        "source_and_language_separation_observed": True,
        "organizational_independence_proven": False,
        "profile_issued": False,
        "canonical_identity_issued": False,
    },
    "authority_boundary": {
        "product_schema_created": False,
        "registry_admission": False,
        "engine_contract_root_binding": False,
        "gate_a_acceptance": False,
        "runtime_authority": False,
        "deployment_authority": False,
        "external_effect_authority": False,
        "publication_authority": False,
    },
}


class DuplicateKey(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def reject_constant(_: str) -> None:
    raise ValueError("non-finite JSON constant")


def parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("non-finite JSON number")
    return value


def load(path: Path) -> Any:
    return json.loads(
        path.read_text("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_constant,
        parse_float=parse_finite_float,
    )


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"raw_sha256": sha256(raw), "byte_count": len(raw)}


def repository_binding(role: str, path: Path) -> dict[str, Any]:
    return {
        "role": role,
        "repository_path": path.relative_to(ROOT).as_posix(),
        **binding(path),
    }


def expected_toolchain_bindings(role: str) -> list[dict[str, Any]]:
    rows = [
        repository_binding("repository_toolchain_lock", TOOLCHAIN_LOCK),
        repository_binding(
            "runtime_version_declaration",
            (
                PYTHON_VERSION_DECLARATION
                if role == "python"
                else NODE_VERSION_DECLARATION
            ),
        ),
    ]
    if role == "node":
        rows.append(repository_binding("digest_verifying_installer", NODE_INSTALLER))
    return rows


def exact_false_boundary(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == FALSE_AUTHORITY_KEYS
        and all(item is False for item in value.values())
    )


def load_python_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "odeya_prq002_python_runner", PYTHON_RUNNER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Python runner source")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        # Import the retained evaluator for a read-only bounded recomputation
        # without leaving repository bytecode behind.
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def bounded_jcs(value: Any) -> bytes:
    """Exact RFC 8785 result for the deliberately bounded probe value domain."""

    def visit(item: Any) -> None:
        if item is None or isinstance(item, (str, bool)):
            if isinstance(item, str) and any(
                0xD800 <= ord(char) <= 0xDFFF for char in item
            ):
                raise ValueError("surrogate in bounded JCS value")
            return
        if isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 9_007_199_254_740_991:
                raise ValueError("integer outside bounded JCS domain")
            return
        if isinstance(item, list):
            for child in item:
                visit(child)
            return
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str) or any(ord(char) > 0x7F for char in key):
                    raise ValueError("probe JCS keys must be ASCII")
                visit(child)
            return
        raise ValueError(f"unsupported bounded JCS value: {type(item).__name__}")

    visit(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def validate_file_inventory(errors: list[str]) -> None:
    observed = {
        path.relative_to(SUITE).as_posix()
        for path in SUITE.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and "node_modules" not in path.parts
    }
    if observed != EXPECTED_FILES:
        errors.append("suite_file_inventory_mismatch")
    residue = [
        path
        for path in SUITE.rglob("*")
        if path.is_file()
        and (
            "__pycache__" in path.parts
            or path.suffix == ".pyc"
            or path.name.startswith("author_")
        )
    ]
    if residue:
        errors.append("temporary_or_bytecode_residue_present")


def validate_input_manifest(
    manifest: dict[str, Any],
    candidate: dict[str, Any],
    cases: dict[str, Any],
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    expected_keys = {
        "schema_version",
        "artifact_class",
        "artifact_id",
        "status",
        "base_profile_core",
        "probe_profile_core",
        "schema_resources",
        "domain_bindings",
        "candidate_cohort_binding",
        "case_manifest_binding",
        "network_access",
        "manifest_self_digest_forbidden",
        "authority_boundary",
    }
    if set(manifest) != expected_keys:
        errors.append("input_manifest_shape_mismatch")
    if (
        manifest.get("schema_version") != "0.1.0"
        or manifest.get("artifact_class")
        != "prq_002_identity_probe_input_manifest"
        or manifest.get("artifact_id")
        != "prq-002-identity-input-manifest.synthetic.0001"
        or manifest.get("status") != PROBE_STATUS
        or manifest.get("network_access") != "disabled"
        or manifest.get("manifest_self_digest_forbidden") is not True
        or not exact_false_boundary(manifest.get("authority_boundary"))
    ):
        errors.append("input_manifest_contract_mismatch")
    for field, expected_path, schema_expected in (
        (
            "base_profile_core",
            "architecture/canonicalization-profile-core-candidate.json",
            "schemas/canonicalization-profile-core.schema.json",
        ),
        (
            "probe_profile_core",
            "architecture/prq-002-identity-probe-profile-core.json",
            "architecture/prq-002-identity-probe-profile.schema.json",
        ),
    ):
        item = manifest.get(field)
        if not isinstance(item, dict):
            errors.append(f"{field}_binding_missing")
            continue
        if item.get("path") != expected_path or item.get("schema_path") != schema_expected:
            errors.append(f"{field}_path_mismatch")
        for path_field, digest_field, count_field in (
            ("path", "raw_sha256", "byte_count"),
            ("schema_path", "schema_raw_sha256", "schema_byte_count"),
        ):
            try:
                observed = binding(ROOT / item[path_field])
            except (OSError, KeyError, TypeError):
                errors.append(f"{field}_{path_field}_unreadable")
                continue
            if (
                item.get(digest_field) != observed["raw_sha256"]
                or item.get(count_field) != observed["byte_count"]
            ):
                errors.append(f"{field}_{path_field}_binding_mismatch")
    if candidate.get("profile") != load(PROFILE_CORE_PATH):
        errors.append("candidate_profile_not_exact_retained_core")
    for field, path in (
        ("candidate_cohort_binding", CANDIDATE_PATH),
        ("case_manifest_binding", CASES_PATH),
    ):
        item = manifest.get(field)
        if not isinstance(item, dict) or item.get("path") != path.relative_to(
            ROOT
        ).as_posix():
            errors.append(f"{field}_path_mismatch")
            continue
        if {
            "raw_sha256": item.get("raw_sha256"),
            "byte_count": item.get("byte_count"),
        } != binding(path):
            errors.append(f"{field}_raw_binding_mismatch")
    resources = manifest.get("schema_resources")
    if not isinstance(resources, list) or len(resources) != 9:
        errors.append("schema_resource_census_mismatch")
        resources = []
    by_role: dict[str, dict[str, Any]] = {}
    schemas_by_id: dict[str, dict[str, Any]] = {}
    for item in resources:
        if not isinstance(item, dict) or set(item) != {
            "role",
            "path",
            "schema_id",
            "raw_sha256",
            "byte_count",
        }:
            errors.append("schema_resource_row_shape_mismatch")
            continue
        role = item["role"]
        if role in by_role:
            errors.append("schema_resource_role_duplicate")
        by_role[role] = item
        path = ROOT / item["path"]
        try:
            observed = binding(path)
            schema = load(path)
        except (OSError, ValueError, DuplicateKey):
            errors.append("schema_resource_unreadable")
            continue
        if observed != {
            "raw_sha256": item["raw_sha256"],
            "byte_count": item["byte_count"],
        }:
            errors.append("schema_resource_raw_binding_mismatch")
        if not isinstance(schema, dict) or schema.get("$id") != item["schema_id"]:
            errors.append("schema_resource_id_mismatch")
            continue
        if item["schema_id"] in schemas_by_id:
            errors.append("schema_resource_id_duplicate")
        schemas_by_id[item["schema_id"]] = schema
    expected_roles = {
        "identity_probe_profile",
        "schema_member_probe",
        "aggregate_state_member_probe",
        "reducer_member_probe",
        "event_member_probe",
        "ordered_commitment_probe",
        "pure_snapshot_probe",
        "structural_state",
        "structural_event",
    }
    if set(by_role) != expected_roles:
        errors.append("schema_resource_role_inventory_mismatch")
    domains = manifest.get("domain_bindings")
    if not isinstance(domains, list) or len(domains) != 9:
        errors.append("domain_binding_census_mismatch")
    else:
        values = [item.get("domain_separator") for item in domains]
        classes = [item.get("subject_class") for item in domains]
        if len(values) != len(set(values)) or len(classes) != len(set(classes)):
            errors.append("domain_binding_not_unique")
        if any(item.get("schema_role") not in by_role for item in domains):
            errors.append("domain_binding_schema_role_unresolved")
    return by_role, schemas_by_id


def schema_validator(
    schema: dict[str, Any], schemas_by_id: dict[str, dict[str, Any]]
) -> Draft202012Validator:
    registry = Registry()
    for schema_id, document in schemas_by_id.items():
        registry = registry.with_resource(
            schema_id, Resource.from_contents(document)
        )
    return Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def validate_candidate_schemas(
    candidate: dict[str, Any],
    resources: dict[str, dict[str, Any]],
    schemas: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    def validate(role: str, instance: Any, label: str) -> None:
        resource = resources.get(role)
        if resource is None:
            errors.append(f"{label}_schema_resource_missing")
            return
        schema = schemas.get(resource["schema_id"])
        if schema is None:
            errors.append(f"{label}_schema_unavailable")
            return
        if list(schema_validator(schema, schemas).iter_errors(instance)):
            errors.append(f"{label}_schema_invalid")

    validate("identity_probe_profile", candidate.get("profile"), "profile")
    members = candidate.get("members", {})
    if not isinstance(members, dict):
        errors.append("members_not_an_object")
        return
    for role in SCHEMA_MEMBER_ROLES:
        validate("schema_member_probe", members.get(role), f"{role}_member")
    validate(
        "aggregate_state_member_probe",
        members.get("aggregate_state"),
        "aggregate_state",
    )
    validate("reducer_member_probe", members.get("reducer"), "reducer")
    validate("event_member_probe", members.get("event"), "event")
    commitments = candidate.get("commitments", {})
    snapshots = candidate.get("snapshots", {})
    for family in FAMILIES:
        validate(
            "ordered_commitment_probe",
            commitments.get(family) if isinstance(commitments, dict) else None,
            f"{family}_commitment",
        )
        validate(
            "pure_snapshot_probe",
            snapshots.get(family) if isinstance(snapshots, dict) else None,
            f"{family}_snapshot",
        )


def validate_cases(
    runner: Any,
    manifest: dict[str, Any],
    cases: dict[str, Any],
    errors: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if set(cases) != {
        "schema_version",
        "artifact_class",
        "artifact_id",
        "status",
        "base_input_path",
        "safe_case_count",
        "minimum_adversarial_cases",
        "mutation_contract",
        "cases",
        "authority_boundary",
    }:
        errors.append("case_manifest_shape_mismatch")
    if (
        cases.get("schema_version") != "0.1.0"
        or cases.get("artifact_class")
        != "prq_002_identity_probe_case_manifest"
        or cases.get("artifact_id")
        != "prq-002-identity-case-manifest.synthetic.0001"
        or cases.get("status") != PROBE_STATUS
        or cases.get("base_input_path")
        != CANDIDATE_PATH.relative_to(ROOT).as_posix()
        or cases.get("safe_case_count") != 1
        or cases.get("mutation_contract")
        != "exactly_one_declared_raw_or_object_mutation_per_adversarial_case"
        or not exact_false_boundary(cases.get("authority_boundary"))
    ):
        errors.append("case_manifest_contract_mismatch")
    rows = cases.get("cases")
    if not isinstance(rows, list):
        errors.append("case_inventory_missing")
        return [], {}
    identifiers = [
        item.get("id") for item in rows if isinstance(item, dict)
    ]
    if (
        len(identifiers) != len(rows)
        or len(identifiers) != len(set(identifiers))
        or any(not isinstance(item, str) or not item for item in identifiers)
    ):
        errors.append("case_id_inventory_invalid")
    safe = [item for item in rows if item.get("kind") == "safe"]
    adversarial = [item for item in rows if item.get("kind") == "adversarial"]
    if (
        len(safe) != 1
        or set(safe[0]) != {
            "id",
            "kind",
            "mutation",
            "intent_errors",
            "expected_errors",
        }
        or safe[0].get("mutation") is not None
        or safe[0].get("intent_errors") != []
        or safe[0].get("expected_errors") != []
    ):
        errors.append("safe_case_contract_mismatch")
    floor = cases.get("minimum_adversarial_cases")
    if (
        not isinstance(floor, int)
        or len(adversarial) < floor
        or floor != len(adversarial)
    ):
        errors.append("adversarial_case_floor_mismatch")
    allowed_raw = {
        "prepend_bom",
        "duplicate_top_level_status",
        "append_trailing_object",
        "inject_invalid_utf8",
        "lexical_negative_zero",
        "lexical_nonfinite",
        "numeric_overflow",
        "escaped_lone_surrogate",
    }
    allowed_object = {"add", "remove", "replace", "swap"}
    for item in adversarial:
        if not isinstance(item, dict) or set(item) != {
            "id",
            "kind",
            "mutation",
            "intent_errors",
            "expected_errors",
        }:
            errors.append("adversarial_case_shape_mismatch")
            continue
        mutation = item.get("mutation")
        if not isinstance(mutation, dict):
            errors.append("adversarial_mutation_missing")
            continue
        layer = mutation.get("layer")
        operation = mutation.get("op")
        if (
            layer == "raw"
            and operation not in allowed_raw
            or layer == "object"
            and operation not in allowed_object
            or layer not in {"raw", "object"}
        ):
            errors.append("adversarial_mutation_contract_invalid")
        expected_mutation_keys: set[str] | None = None
        if layer == "raw":
            expected_mutation_keys = {"layer", "op"}
        elif operation in {"add", "replace"}:
            payload_keys = {"value", "value_from"} & set(mutation)
            if len(payload_keys) == 1:
                expected_mutation_keys = {"layer", "op", "path", *payload_keys}
        elif operation == "remove":
            expected_mutation_keys = {"layer", "op", "path"}
        elif operation == "swap":
            expected_mutation_keys = {"layer", "op", "path", "other_index"}
        if expected_mutation_keys is None or set(mutation) != expected_mutation_keys:
            errors.append("adversarial_mutation_shape_invalid")
        if layer == "object" and (
            not isinstance(mutation.get("path"), str)
            or not mutation["path"].startswith("/")
        ):
            errors.append("adversarial_mutation_path_invalid")
        if "value_from" in mutation and (
            not isinstance(mutation["value_from"], str)
            or not mutation["value_from"].startswith("/")
        ):
            errors.append("adversarial_mutation_value_from_invalid")
        if operation == "swap" and (
            not isinstance(mutation.get("other_index"), int)
            or isinstance(mutation["other_index"], bool)
            or mutation["other_index"] < 0
        ):
            errors.append("adversarial_mutation_other_index_invalid")
        intent = item.get("intent_errors")
        expected = item.get("expected_errors")
        if (
            not isinstance(intent, list)
            or not intent
            or len(intent) != len(set(intent))
            or not isinstance(expected, list)
            or not expected
            or len(expected) != len(set(expected))
            or not set(intent).issubset(expected)
        ):
            errors.append("adversarial_error_attribution_invalid")
    base_raw = CANDIDATE_PATH.read_bytes()
    observed, fold = runner.evaluate_cases(
        base_raw, manifest, cases, bounded_jcs
    )
    expected_index = {item["id"]: item for item in rows}
    for row in observed:
        expected = expected_index.get(row["id"], {})
        if row["errors"] != expected.get("expected_errors"):
            errors.append("case_observed_error_inventory_mismatch")
        if row["kind"] == "safe" and row["outcome"] != "accepted":
            errors.append("safe_case_not_accepted")
        if row["kind"] == "adversarial" and row["outcome"] != "refused":
            errors.append("adversarial_case_not_refused")
    summary = fold.get("summary", {})
    if summary != {
        "case_count": len(rows),
        "safe_count": 1,
        "adversarial_count": len(adversarial),
        "accepted_count": 1,
        "refused_count": len(adversarial),
    }:
        errors.append("case_summary_fold_mismatch")
    # Fail-closed harness self-tests: exact expected inventory, declared intent,
    # and the mutation itself must each remain load-bearing.
    probe = copy.deepcopy(observed[1])
    if probe["errors"] == expected_index[probe["id"]]["expected_errors"]:
        probe["errors"] = []
    if probe["errors"] == expected_index[probe["id"]]["expected_errors"]:
        errors.append("harness_expected_inventory_self_test_failed")
    intent = expected_index[observed[1]["id"]]["intent_errors"][0]
    if intent not in observed[1]["errors"]:
        errors.append("harness_intent_self_test_failed")
    mutated_case = copy.deepcopy(rows[1])
    mutated_case["mutation"] = None
    materialized, strict_error = runner._materialize_case(  # noqa: SLF001
        base_raw, mutated_case
    )
    if strict_error is not None:
        errors.append("harness_mutation_self_test_failed")
    else:
        no_mutation_errors, _ = runner.evaluate_candidate(
            materialized, manifest, bounded_jcs
        )
        if no_mutation_errors:
            errors.append("harness_mutation_self_test_failed")
    return observed, fold


def validate_source_manifest(
    path: Path,
    role: str,
    runner_path: Path,
    lock_path: Path,
    errors: list[str],
) -> dict[str, Any]:
    try:
        document = load(path)
    except (OSError, ValueError, DuplicateKey):
        errors.append(f"{role}_source_manifest_unreadable")
        return {}
    expected_keys = {
        "schema_version",
        "artifact_class",
        "artifact_id",
        "status",
        "implementation_role",
        "runtime",
        "canonicalizer",
        "source_file_count",
        "source_files",
        "dependency_lock",
        "installed_dependency_payload",
        "peer_implementation_source_consumed",
        "expected_result_fixture_consumed",
        "generated_source_consumed",
        "shared_source_files_with_peer_implementations",
        "network_access_requested_or_used_by_evaluator",
        "authority_boundary",
    }
    if role == "node":
        expected_keys.add("dependency_manifest")
    if set(document) != expected_keys:
        errors.append(f"{role}_source_manifest_shape_mismatch")
    if (
        document.get("schema_version") != "0.1.0"
        or document.get("artifact_class")
        != "prq_002_identity_probe_source_manifest"
        or document.get("artifact_id")
        != {
            "python": (
                "prq-002-identity-source.python-rfc8785-0_1_4.0001"
            ),
            "node": (
                "prq-002-identity-source.node-canonicalize-3_0_0.0001"
            ),
        }[role]
        or document.get("status") != PROBE_STATUS
        or document.get("implementation_role") != role
        or document.get("source_file_count") != 1
        or document.get("peer_implementation_source_consumed") is not False
        or document.get("expected_result_fixture_consumed") is not False
        or document.get("generated_source_consumed") is not False
        or document.get("shared_source_files_with_peer_implementations") != []
        or document.get("network_access_requested_or_used_by_evaluator")
        is not False
        or not exact_false_boundary(document.get("authority_boundary"))
    ):
        errors.append(f"{role}_source_manifest_contract_mismatch")
    expected_source = {
        "sequence_index": 0,
        "repository_path": runner_path.relative_to(ROOT).as_posix(),
        **binding(runner_path),
    }
    if document.get("source_files") != [expected_source]:
        errors.append(f"{role}_source_file_binding_mismatch")
    expected_lock = {
        "repository_path": lock_path.relative_to(ROOT).as_posix(),
        **binding(lock_path),
    }
    if document.get("dependency_lock") != expected_lock:
        errors.append(f"{role}_dependency_lock_binding_mismatch")
    if document.get("installed_dependency_payload") != (
        EXPECTED_DEPENDENCY_PAYLOADS[role]
    ):
        errors.append(f"{role}_installed_dependency_payload_manifest_mismatch")
    if role == "node":
        expected_manifest = {
            "repository_path": NODE_PACKAGE.relative_to(ROOT).as_posix(),
            **binding(NODE_PACKAGE),
        }
        if document.get("dependency_manifest") != expected_manifest:
            errors.append("node_dependency_manifest_binding_mismatch")
    expected_runtime = {
        "python": {
            "name": "CPython",
            "version": EXPECTED_PYTHON_VERSION,
        },
        "node": {
            "name": "Node.js",
            "version": EXPECTED_NODE_VERSION,
        },
    }[role]
    if document.get("runtime") != expected_runtime:
        errors.append(f"{role}_runtime_binding_mismatch")
    expected_canonicalizer = {
        "python": {
            "package": "rfc8785",
            "version": "0.1.4",
            "distribution": "rfc8785-0.1.4-py3-none-any.whl",
            "distribution_sha256": (
                "520d690b448ecf0703691c76e1a34a24ddcd4fc5bc41d589cb7c58ec651bcd48"
            ),
            "entrypoint": "verified_source_exec:rfc8785/_impl.py:dumps",
            "license": "Apache-2.0",
        },
        "node": {
            "package": "canonicalize",
            "version": "3.0.0",
            "distribution": "canonicalize-3.0.0.tgz",
            "distribution_sha512_sri": (
                "sha512-yYLfHyDMIXRyRqsKBRLX023riFLpXY2YOfdtqKXZRZy9qsfOJ9U+4F9YZL7MEzL5+"
                "ziN2x2nlBvY/Voi3EBljA=="
            ),
            "entrypoint": "canonicalize default export",
            "license": "Apache-2.0",
        },
    }[role]
    if document.get("canonicalizer") != expected_canonicalizer:
        errors.append(f"{role}_canonicalizer_binding_mismatch")
    return document


def normalize_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": result.get("status"),
        "evidence_status": result.get("evidence_status"),
        "input_bindings": result.get("input_bindings"),
        "safe_projection": result.get("safe_projection"),
        "parser_semantics": result.get("parser_semantics"),
        "cases": result.get("cases"),
        "summary": result.get("summary"),
        "authority_boundary": result.get("authority_boundary"),
    }


def validate_digest_records(projection: dict[str, Any], errors: list[str]) -> None:
    expected_census = {
        "profile_instances": 1,
        "schema_members": 9,
        "graph_members": 3,
        "members": 12,
        "commitments": 4,
        "snapshots": 4,
        "total_probe_objects": 21,
    }
    if projection.get("cohort_census") != expected_census:
        errors.append("result_cohort_census_mismatch")
    expected_sizes = {
        "member_digest_records": 12,
        "commitment_digest_records": 4,
        "snapshot_digest_records": 4,
    }
    for field, size in expected_sizes.items():
        rows = projection.get(field)
        if not isinstance(rows, dict) or len(rows) != size:
            errors.append(f"{field}_census_mismatch")
            continue
        for record in rows.values():
            if not isinstance(record, dict) or set(record) != {
                "digest",
                "canonical_byte_count",
                "canonical_hex",
                "canonical_sha256",
            }:
                errors.append("digest_record_shape_mismatch")
                continue
            try:
                raw = bytes.fromhex(record["canonical_hex"])
            except (ValueError, TypeError):
                errors.append("digest_record_canonical_hex_invalid")
                continue
            observed = sha256(raw)
            if (
                record.get("canonical_byte_count") != len(raw)
                or record.get("digest") != observed
                or record.get("canonical_sha256") != observed
            ):
                errors.append("digest_record_binding_mismatch")
            try:
                scoped = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError):
                errors.append("digest_record_canonical_bytes_invalid")
                continue
            if (
                not isinstance(scoped, dict)
                or set(scoped)
                != {"digest_contract", "resolved_subject_schema", "projection"}
                or scoped.get("resolved_subject_schema")
                != scoped.get("digest_contract", {}).get("subject_schema_ref")
            ):
                errors.append("digest_record_scoped_input_mismatch")


def validate_result(
    path: Path,
    role: str,
    source_manifest_path: Path,
    lock_path: Path,
    expected_cases: list[dict[str, Any]],
    expected_projection: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    try:
        result = load(path)
    except (OSError, ValueError, DuplicateKey):
        errors.append(f"{role}_result_unreadable")
        return {}
    try:
        if path.read_bytes() != bounded_jcs(result) + b"\n":
            errors.append(f"{role}_retained_result_not_canonical_json_line")
    except (OSError, TypeError, ValueError):
        errors.append(f"{role}_retained_result_not_canonical_json_line")
    expected_top = {
        "schema_version",
        "artifact_class",
        "result_id",
        "status",
        "evidence_status",
        "implementation",
        "input_bindings",
        "safe_projection",
        "parser_semantics",
        "cases",
        "summary",
        "authority_boundary",
    }
    if not isinstance(result, dict) or set(result) != expected_top:
        errors.append(f"{role}_result_shape_mismatch")
        return result if isinstance(result, dict) else {}
    if (
        result.get("schema_version") != "0.1.0"
        or result.get("artifact_class")
        != "prq_002_identity_probe_recomputation_result"
        or result.get("result_id")
        != {
            "python": (
                "prq-002-identity-result.python-rfc8785-0_1_4.0001"
            ),
            "node": (
                "prq-002-identity-result.node-canonicalize-3_0_0.0001"
            ),
        }[role]
        or result.get("status") != "pass"
        or result.get("evidence_status") != PROBE_STATUS
        or not exact_false_boundary(result.get("authority_boundary"))
    ):
        errors.append(f"{role}_result_contract_mismatch")
    implementation = result.get("implementation", {})
    expected_impl_common = {
        "source_manifest_binding": binding(source_manifest_path),
        "dependency_lock_binding": binding(lock_path),
        "peer_source_consumed": False,
        "generated_source_consumed": False,
        "expected_result_fixture_consumed": False,
    }
    expected_role = {
        "python": {
            "role": "python",
            "runtime": "CPython",
            "runtime_version": EXPECTED_PYTHON_VERSION,
            "package": "rfc8785",
            "package_version": "0.1.4",
            "canonicalization_entrypoint": (
                "verified_source_exec:rfc8785/_impl.py:dumps"
            ),
        },
        "node": {
            "role": "node",
            "runtime": "Node.js",
            "runtime_version": EXPECTED_NODE_VERSION,
            "package": "canonicalize",
            "package_version": "3.0.0",
            "canonicalization_entrypoint": "canonicalize default export",
        },
    }[role]
    source_manifest = load(source_manifest_path)
    expected_source_binding = source_manifest.get("source_files", [None])[0]
    expected_implementation = {
        **expected_role,
        "source_file_binding": expected_source_binding,
        **expected_impl_common,
    }
    if role == "node":
        expected_implementation["dependency_manifest_binding"] = binding(
            NODE_PACKAGE
        )
    if implementation != expected_implementation:
        errors.append(f"{role}_implementation_binding_mismatch")
    expected_inputs = {
        "suite_manifest": binding(SUITE_MANIFEST_PATH),
        "input_manifest": binding(INPUT_MANIFEST_PATH),
        "candidate_cohort": binding(CANDIDATE_PATH),
        "cases": binding(CASES_PATH),
    }
    if result.get("input_bindings") != expected_inputs:
        errors.append(f"{role}_input_binding_mismatch")
    if result.get("safe_projection") != expected_projection:
        errors.append(f"{role}_safe_projection_mismatch")
    if result.get("parser_semantics") != EXPECTED_PARSER_SEMANTICS:
        errors.append(f"{role}_parser_semantics_mismatch")
    if result.get("cases") != expected_cases:
        errors.append(f"{role}_case_projection_mismatch")
    summary = result.get("summary", {})
    if summary != {
        "case_count": len(expected_cases),
        "safe_count": 1,
        "adversarial_count": len(expected_cases) - 1,
        "accepted_count": 1,
        "refused_count": len(expected_cases) - 1,
    }:
        errors.append(f"{role}_summary_mismatch")
    validate_digest_records(result.get("safe_projection", {}), errors)
    return result


def expected_historical_execution_attestation(
    role: str,
) -> dict[str, Any]:
    execution = HISTORICAL_EXECUTIONS[role]
    argv = execution["argv"]
    runner = PYTHON_RUNNER if role == "python" else NODE_RUNNER
    source_manifest = (
        PYTHON_SOURCE_MANIFEST if role == "python" else NODE_SOURCE_MANIFEST
    )
    result = PYTHON_RESULT if role == "python" else NODE_RESULT
    runner_index = argv.index(
        f"{HISTORICAL_WORKTREE}/{runner.relative_to(ROOT).as_posix()}"
    )
    challenge_index = argv.index("--attestation-challenge") + 1

    def historical_repository_binding(path: Path) -> dict[str, Any]:
        return {
            "absolute_path": (
                f"{HISTORICAL_WORKTREE}/{path.relative_to(ROOT).as_posix()}"
            ),
            **binding(path),
        }

    payload_path = (
        "rfc8785/_impl.py"
        if role == "python"
        else "lib/canonicalize.js"
    )
    payload_row = next(
        row
        for row in EXPECTED_DEPENDENCY_PAYLOADS[role]["files"]
        if row["relative_path"] == payload_path
    )
    executable = execution["executable_observation"]
    executable_binding = {
        "raw_sha256": executable["raw_sha256"],
        "byte_count": executable["byte_count"],
    }
    if role == "python":
        runtime = {
            "name": "CPython",
            "version": EXPECTED_PYTHON_VERSION,
            "sys_executable": executable["invocation_path"],
            "resolved_executable": executable["resolved_path"],
            "executable_binding": executable_binding,
            "sys_prefix": f"{HISTORICAL_WORKTREE}/.venv-architecture",
            "base_prefix": str(
                Path(executable["resolved_path"]).parent.parent
            ),
            "isolated": True,
            "site_initialization_disabled": True,
            "environment_ignored": True,
            "user_site_disabled": True,
            "safe_path": True,
            "bytecode_writes_disabled": True,
        }
        process_argv = argv[runner_index:]
        canonicalizer_path = (
            f"{HISTORICAL_WORKTREE}/.venv-architecture/lib/"
            "python3.14/site-packages/rfc8785/_impl.py"
        )
    else:
        runtime = {
            "name": "Node.js",
            "version": EXPECTED_NODE_VERSION,
            "process_exec_path": executable["resolved_path"],
            "resolved_executable": executable["resolved_path"],
            "executable_binding": executable_binding,
            "process_argv0": executable["invocation_path"],
        }
        process_argv = [executable["resolved_path"], *argv[runner_index:]]
        canonicalizer_path = (
            f"{HISTORICAL_WORKTREE}/tests/prq-002-identity-cohort/"
            "node/node_modules/canonicalize/lib/canonicalize.js"
        )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002_identity_probe_execution_attestation",
        "implementation_role": role,
        "challenge": argv[challenge_index],
        "result_line_binding": binding(result),
        "runtime": runtime,
        "process_argv": process_argv,
        "bindings": {
            "runner": historical_repository_binding(runner),
            "input": historical_repository_binding(CANDIDATE_PATH),
            "input_manifest": historical_repository_binding(
                INPUT_MANIFEST_PATH
            ),
            "cases": historical_repository_binding(CASES_PATH),
            "source_manifest": historical_repository_binding(source_manifest),
            "canonicalizer_source": {
                "absolute_path": canonicalizer_path,
                "raw_sha256": payload_row["raw_sha256"],
                "byte_count": payload_row["byte_count"],
            },
        },
    }


def derived_historical_process_outputs(
    attestation: dict[str, Any], result: Path
) -> dict[str, dict[str, Any]]:
    attestation_line = bounded_jcs(attestation) + b"\n"
    full_stdout = attestation_line + result.read_bytes()
    return {
        "process_stdout_binding": {
            "raw_sha256": sha256(full_stdout),
            "byte_count": len(full_stdout),
            "line_count": 2,
            "framing": "rfc8785_attestation_line_then_rfc8785_result_line",
        },
        "attestation_line_binding": {
            "raw_sha256": sha256(attestation_line),
            "byte_count": len(attestation_line),
            "stdout_line": 1,
        },
    }


def validate_comparison_and_execution(
    python_result: dict[str, Any],
    node_result: dict[str, Any],
    errors: list[str],
) -> None:
    try:
        comparison = load(COMPARISON)
    except (OSError, ValueError, DuplicateKey):
        errors.append("comparison_receipt_unreadable")
        return
    expected_result_bindings = [
        {
            "role": "python",
            "path": PYTHON_RESULT.relative_to(ROOT).as_posix(),
            "result_id": python_result.get("result_id"),
            **binding(PYTHON_RESULT),
        },
        {
            "role": "node",
            "path": NODE_RESULT.relative_to(ROOT).as_posix(),
            "result_id": node_result.get("result_id"),
            **binding(NODE_RESULT),
        },
    ]
    expected_comparison = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002_identity_probe_comparison_receipt",
        "receipt_id": "prq-002-identity-comparison.synthetic.0001",
        "status": "pass",
        "evidence_status": PROBE_STATUS,
        "ordered_result_bindings": expected_result_bindings,
        "comparison": {
            "safe_projection": "exact_agreement",
            "parser_semantics": "exact_agreement",
            "case_outcomes_and_error_inventories": "exact_agreement",
            "cohort_census": "exact_agreement",
            "implementation_agreement": True,
        },
        "source_separation": {
            "roles": ["python", "node"],
            "languages": ["Python", "JavaScript"],
            "runtime_families": ["CPython", "Node.js"],
            "shared_evaluator_source_files": [],
            "peer_result_consumption": False,
            "organizational_independence_proven": False,
        },
        "summary": {
            "case_count": len(python_result.get("cases", [])),
            "safe_count": 1,
            "adversarial_count": len(python_result.get("cases", [])) - 1,
            "structured_digest_count": 20,
        },
        "authority_boundary": {
            key: False for key in sorted(FALSE_AUTHORITY_KEYS)
        },
    }
    if comparison != expected_comparison:
        errors.append("comparison_receipt_mismatch")
    if normalize_result(python_result) != normalize_result(node_result):
        errors.append("retained_implementation_disagreement")
    execution_contract = {
        "python": {
            "path": PYTHON_EXECUTION,
            "result": PYTHON_RESULT,
            "source": PYTHON_RUNNER,
            "source_manifest": PYTHON_SOURCE_MANIFEST,
            "lock": PYTHON_LOCK,
            "receipt_id": "prq-002-execution.python-rfc8785-0_1_4.0001",
            "runtime": {"name": "CPython", "version": EXPECTED_PYTHON_VERSION},
        },
        "node": {
            "path": NODE_EXECUTION,
            "result": NODE_RESULT,
            "source": NODE_RUNNER,
            "source_manifest": NODE_SOURCE_MANIFEST,
            "lock": NODE_LOCK,
            "receipt_id": "prq-002-execution.node-canonicalize-3_0_0.0001",
            "runtime": {"name": "Node.js", "version": EXPECTED_NODE_VERSION},
            "dependency_manifest": NODE_PACKAGE,
        },
    }
    empty_digest = sha256(b"")
    for role, contract in execution_contract.items():
        try:
            receipt = load(contract["path"])
        except (OSError, ValueError, DuplicateKey):
            errors.append(f"{role}_execution_receipt_unreadable")
            continue
        historical_attestation = expected_historical_execution_attestation(
            role
        )
        derived_outputs = derived_historical_process_outputs(
            historical_attestation, contract["result"]
        )
        if HISTORICAL_PROCESS_OUTPUTS[role] != derived_outputs:
            errors.append(f"{role}_historical_output_binding_inconsistent")
        expected = {
            "schema_version": "0.1.0",
            "artifact_class": "prq_002_identity_probe_execution_receipt",
            "receipt_id": contract["receipt_id"],
            "status": "observed_pass",
            "evidence_status": PROBE_STATUS,
            "implementation_role": role,
            "runtime": contract["runtime"],
            "historical_execution": HISTORICAL_EXECUTIONS[role],
            "portable_recomputation_contract": PORTABLE_RECOMPUTATION_CONTRACT,
            "historical_child_execution_attestation": historical_attestation,
            "repository_toolchain_bindings": expected_toolchain_bindings(role),
            "closed_environment": {
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "TZ": "UTC",
                "network_access": (
                    "not_os_sandboxed_evaluator_source_declares_no_requests"
                ),
            },
            "source_binding": binding(contract["source"]),
            "source_manifest_binding": binding(contract["source_manifest"]),
            "dependency_lock_binding": binding(contract["lock"]),
            "historical_process_stdout_binding": (
                derived_outputs["process_stdout_binding"]
            ),
            "historical_attestation_line_binding": (
                derived_outputs["attestation_line_binding"]
            ),
            "retained_result_line_binding": {
                "retained_path": contract["result"].relative_to(ROOT).as_posix(),
                "stdout_line": 2,
                **binding(contract["result"]),
            },
            "stderr_binding": {
                "raw_sha256": empty_digest,
                "byte_count": 0,
            },
            "exit_code": 0,
            "retained_result_status": "pass",
            "authority_boundary": {
                key: False for key in sorted(FALSE_AUTHORITY_KEYS)
            },
        }
        if "dependency_manifest" in contract:
            expected["dependency_manifest_binding"] = binding(
                contract["dependency_manifest"]
            )
        if receipt != expected:
            errors.append(f"{role}_execution_receipt_mismatch")


def closed_environment() -> dict[str, str]:
    return {
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
        "TZ": "UTC",
    }


def validate_selected_executable(
    selected: Path | None, role: str, errors: list[str]
) -> Path | None:
    if selected is None:
        errors.append(f"{role}_recomputation_executable_not_selected")
        return None
    if not selected.is_absolute():
        errors.append(f"{role}_recomputation_executable_not_absolute")
        return None
    try:
        is_file = selected.is_file()
        executable = os.access(selected, os.X_OK)
    except OSError:
        is_file = False
        executable = False
    if not is_file or not executable:
        errors.append(f"{role}_recomputation_executable_not_executable")
        return None
    if role == "python":
        try:
            resolved = selected.resolve(strict=True)
            same_parent_image = selected.samefile(PARENT_PYTHON_ANCHOR)
            selected_binding = stream_binding(resolved)
        except OSError:
            resolved = selected
            same_parent_image = False
            selected_binding = None
        if (
            PARENT_PYTHON_ANCHOR_BINDING is None
            or resolved != PARENT_PYTHON_ANCHOR
            or not same_parent_image
            or selected_binding != PARENT_PYTHON_ANCHOR_BINDING
        ):
            errors.append("python_recomputation_executable_provenance_mismatch")
            return None
    return selected


def python_environment_observation(errors: list[str]) -> dict[str, Any] | None:
    purelib = Path(sysconfig.get_path("purelib")).resolve()
    if PARENT_PYTHON_VERSION != EXPECTED_PYTHON_VERSION:
        errors.append("python_recomputation_runtime_mismatch")
    if not purelib.is_dir():
        errors.append("python_recomputation_distribution_root_invalid")
        return None
    return {
        "runtime_version": PARENT_PYTHON_VERSION,
        "package_version": "0.1.4",
        "distribution_root": str(purelib),
        "package_root": str(purelib / "rfc8785"),
    }


def stream_binding(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
    return {"raw_sha256": f"sha256:{digest.hexdigest()}", "byte_count": count}


def verify_node_installer_provenance(
    selected: Path, errors: list[str]
) -> tuple[Path, dict[str, Any]] | None:
    platform_contracts = {
        ("Darwin", "x86_64"): (
            "darwin_amd64",
            "darwin-x64",
        ),
        ("Darwin", "arm64"): (
            "darwin_arm64",
            "darwin-arm64",
        ),
        ("Linux", "x86_64"): (
            "linux_amd64",
            "linux-x64",
        ),
        ("Linux", "aarch64"): (
            "linux_arm64",
            "linux-arm64",
        ),
        ("Linux", "arm64"): (
            "linux_arm64",
            "linux-arm64",
        ),
    }
    contract = platform_contracts.get((platform.system(), platform.machine()))
    if contract is None:
        errors.append("node_recomputation_platform_unsupported")
        return None
    platform_key, archive_platform = contract
    try:
        node_directory = selected.parents[3]
    except IndexError:
        errors.append("node_recomputation_installer_product_path_mismatch")
        return None
    expected_product = (
        node_directory
        / f"v{EXPECTED_NODE_VERSION}"
        / platform_key
        / "bin/node"
    )
    if selected != expected_product:
        errors.append("node_recomputation_installer_product_path_mismatch")
        return None
    try:
        selected_resolved_before = selected.resolve(strict=True)
        selected_binding_before = stream_binding(selected_resolved_before)
    except OSError:
        errors.append("node_recomputation_installer_product_unreadable")
        return None
    try:
        toolchain = load(TOOLCHAIN_LOCK)
        archive_digest = toolchain["node"]["archives"][platform_key]
    except (OSError, KeyError, TypeError, ValueError, DuplicateKey):
        errors.append("node_recomputation_toolchain_lock_invalid")
        return None
    if (
        toolchain.get("node", {}).get("version") != EXPECTED_NODE_VERSION
        or (NODE_VERSION_DECLARATION.read_text("utf-8").strip())
        != EXPECTED_NODE_VERSION
    ):
        errors.append("node_recomputation_toolchain_lock_invalid")
        return None
    archive_name = (
        f"node-v{EXPECTED_NODE_VERSION}-{archive_platform}.tar.gz"
    )
    archive_path = node_directory / archive_name
    try:
        observed_archive = stream_binding(archive_path)
    except OSError:
        errors.append("node_recomputation_installer_archive_missing")
        return None
    if observed_archive["raw_sha256"] != f"sha256:{archive_digest}":
        errors.append("node_recomputation_installer_archive_digest_mismatch")
        return None
    installer_environment = {
        **closed_environment(),
        "ODEYA_TOOL_CACHE": str(node_directory.parent),
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    }
    completed = subprocess.run(
        ["/bin/bash", str(NODE_INSTALLER)],
        cwd=ROOT,
        env=installer_environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    if completed.returncode != 0 or completed.stderr:
        errors.append("node_recomputation_installer_reverification_failed")
        return None
    try:
        installed = Path(completed.stdout.strip())
    except TypeError:
        errors.append("node_recomputation_installer_output_invalid")
        return None
    if (
        not installed.is_absolute()
        or installed != selected
        or installed.resolve() != selected.resolve()
    ):
        errors.append("node_recomputation_installer_output_mismatch")
        return None
    member_name = (
        f"node-v{EXPECTED_NODE_VERSION}-{archive_platform}/bin/node"
    )
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            member = archive.getmember(member_name)
            if not member.isfile():
                errors.append(
                    "node_recomputation_installer_archive_member_not_regular"
                )
                return None
            extracted = archive.extractfile(member)
            if extracted is None:
                raise KeyError(member_name)
            digest = hashlib.sha256()
            count = 0
            while chunk := extracted.read(1024 * 1024):
                digest.update(chunk)
                count += len(chunk)
        archive_member_binding = {
            "raw_sha256": f"sha256:{digest.hexdigest()}",
            "byte_count": count,
        }
        installed_resolved = installed.resolve(strict=True)
        installed_binding = stream_binding(installed_resolved)
    except (OSError, KeyError, tarfile.TarError):
        errors.append("node_recomputation_installer_payload_unreadable")
        return None
    if (
        selected_binding_before != archive_member_binding
        or installed_binding != archive_member_binding
    ):
        errors.append("node_recomputation_installer_payload_mismatch")
        return None
    return installed, {
        "resolved_path": installed_resolved,
        "binding": installed_binding,
    }


def verify_installed_dependency_payload(
    role: str,
    package_root: Path,
    source_manifest: dict[str, Any],
    errors: list[str],
) -> None:
    expected = EXPECTED_DEPENDENCY_PAYLOADS[role]
    if source_manifest.get("installed_dependency_payload") != expected:
        errors.append(f"{role}_installed_dependency_payload_manifest_mismatch")
        return
    expected_paths = {
        row["relative_path"] for row in expected["files"]
    }
    if role == "python":
        search_roots = [
            package_root / "rfc8785",
            package_root / "rfc8785-0.1.4.dist-info",
        ]
        excluded = {
            "rfc8785-0.1.4.dist-info/INSTALLER",
            "rfc8785-0.1.4.dist-info/RECORD",
            "rfc8785-0.1.4.dist-info/REQUESTED",
            "rfc8785-0.1.4.dist-info/direct_url.json",
        }
    else:
        search_roots = [package_root]
        excluded = set()
    observed_paths: set[str] = set()
    for root in search_roots:
        if not root.is_dir():
            errors.append(f"{role}_installed_dependency_payload_root_missing")
            return
        for path in root.rglob("*"):
            if not path.is_file() and not path.is_symlink():
                continue
            relative = path.relative_to(package_root).as_posix()
            if role == "python" and (
                "__pycache__" in path.parts or path.suffix == ".pyc"
            ):
                errors.append("python_installed_dependency_import_cache_present")
                continue
            if relative in excluded:
                continue
            if path.is_symlink():
                errors.append(f"{role}_installed_dependency_payload_symlink")
            observed_paths.add(relative)
    if observed_paths != expected_paths:
        errors.append(f"{role}_installed_dependency_payload_inventory_mismatch")
    for row in expected["files"]:
        path = package_root / row["relative_path"]
        try:
            observed = binding(path)
        except OSError:
            errors.append(f"{role}_installed_dependency_payload_file_missing")
            continue
        if observed != {
            "raw_sha256": row["raw_sha256"],
            "byte_count": row["byte_count"],
        }:
            errors.append(f"{role}_installed_dependency_payload_binding_mismatch")


def node_runtime_observation(executable: Path, errors: list[str]) -> None:
    completed = subprocess.run(
        [str(executable), "--version"],
        cwd=ROOT,
        env=closed_environment(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        text=True,
    )
    if (
        completed.returncode != 0
        or completed.stderr
        or completed.stdout.strip() != f"v{EXPECTED_NODE_VERSION}"
    ):
        errors.append("node_recomputation_runtime_mismatch")


def recomputation_argv(
    python_executable: Path,
    node_executable: Path,
    python_package_root: Path,
    challenges: dict[str, str],
) -> dict[str, list[str]]:
    common = [
        "--input",
        str(CANDIDATE_PATH),
        "--manifest",
        str(INPUT_MANIFEST_PATH),
        "--cases",
        str(CASES_PATH),
    ]
    return {
        "python": [
            str(python_executable),
            "-I",
            "-S",
            "-B",
            str(PYTHON_RUNNER),
            *common,
            "--rfc8785-package-root",
            str(python_package_root),
            "--attestation-challenge",
            challenges["python"],
            "--emit-execution-attestation",
        ],
        "node": [
            str(node_executable),
            "--disable-proto=throw",
            str(NODE_RUNNER),
            *common,
            "--attestation-challenge",
            challenges["node"],
            "--emit-execution-attestation",
        ],
    }


def validate_recomputation_argv(
    commands: dict[str, list[str]],
    python_executable: Path,
    node_executable: Path,
    python_package_root: Path,
    challenges: dict[str, str],
    errors: list[str],
) -> None:
    expected = recomputation_argv(
        python_executable,
        node_executable,
        python_package_root,
        challenges,
    )
    if commands != expected:
        errors.append("recomputation_argv_contract_mismatch")
    for role, selected in (
        ("python", python_executable),
        ("node", node_executable),
    ):
        command = commands.get(role, [])
        if (
            not command
            or command[0] != str(selected)
            or not Path(command[0]).is_absolute()
            or str(CANDIDATE_PATH) not in command
            or str(INPUT_MANIFEST_PATH) not in command
            or str(CASES_PATH) not in command
            or "--attestation-challenge" not in command
            or challenges[role] not in command
            or "--emit-execution-attestation" not in command
        ):
            errors.append(f"{role}_recomputation_argv_selection_mismatch")
    if (
        "--rfc8785-package-root" not in commands.get("python", [])
        or str(python_package_root) not in commands.get("python", [])
        or commands.get("python", [])[1:4] != ["-I", "-S", "-B"]
        or "-S" not in commands.get("python", [])
    ):
        errors.append("python_recomputation_argv_isolation_mismatch")


def expected_execution_attestation(
    role: str,
    command: list[str],
    python_package_root: Path,
    challenge: str,
    result_line_binding: dict[str, Any],
    executable_binding: dict[str, Any],
) -> dict[str, Any]:
    if role == "python":
        runner_index = command.index(str(PYTHON_RUNNER))
        process_argv = command[runner_index:]
        runtime = {
            "name": "CPython",
            "version": EXPECTED_PYTHON_VERSION,
            "sys_executable": command[0],
            "resolved_executable": str(PARENT_PYTHON_ANCHOR),
            "executable_binding": executable_binding,
            "sys_prefix": PARENT_PYTHON_PREFIX,
            "base_prefix": str(PARENT_PYTHON_ANCHOR.parent.parent),
            "isolated": True,
            "site_initialization_disabled": True,
            "environment_ignored": True,
            "user_site_disabled": True,
            "safe_path": True,
            "bytecode_writes_disabled": True,
        }
        runner = PYTHON_RUNNER
        source_manifest = PYTHON_SOURCE_MANIFEST
        canonicalizer = python_package_root / "_impl.py"
    else:
        runner_index = command.index(str(NODE_RUNNER))
        process_argv = [
            str(Path(command[0]).resolve()),
            *command[runner_index:],
        ]
        runtime = {
            "name": "Node.js",
            "version": EXPECTED_NODE_VERSION,
            "process_exec_path": str(Path(command[0]).resolve()),
            "resolved_executable": str(Path(command[0]).resolve()),
            "executable_binding": executable_binding,
            "process_argv0": command[0],
        }
        runner = NODE_RUNNER
        source_manifest = NODE_SOURCE_MANIFEST
        canonicalizer = (
            SUITE / "node/node_modules/canonicalize/lib/canonicalize.js"
        )

    def attested(path: Path) -> dict[str, Any]:
        return {"absolute_path": str(path), **binding(path)}

    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002_identity_probe_execution_attestation",
        "implementation_role": role,
        "challenge": challenge,
        "result_line_binding": result_line_binding,
        "runtime": runtime,
        "process_argv": process_argv,
        "bindings": {
            "runner": attested(runner),
            "input": attested(CANDIDATE_PATH),
            "input_manifest": attested(INPUT_MANIFEST_PATH),
            "cases": attested(CASES_PATH),
            "source_manifest": attested(source_manifest),
            "canonicalizer_source": attested(canonicalizer),
        },
    }


def verify_executable_guard(
    selected: Path,
    resolved: Path,
    expected_binding: dict[str, Any],
    label: str,
    phase: str,
    errors: list[str],
) -> bool:
    try:
        observed_resolved = selected.resolve(strict=True)
        same_file = selected.samefile(resolved)
        observed_binding = stream_binding(observed_resolved)
    except OSError:
        observed_resolved = selected
        same_file = False
        observed_binding = None
    if (
        observed_resolved != resolved
        or not same_file
        or observed_binding != expected_binding
    ):
        errors.append(f"{label}_executable_{phase}_binding_mismatch")
        return False
    return True


def run_attested_exact(
    command: list[str],
    label: str,
    environment: dict[str, str],
    expected_attestation: dict[str, Any],
    executable_guard: dict[str, Any],
    errors: list[str],
) -> bytes:
    if not verify_executable_guard(
        Path(command[0]),
        executable_guard["resolved_path"],
        executable_guard["binding"],
        label,
        "pre_execution",
        errors,
    ):
        return b""
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    verify_executable_guard(
        Path(command[0]),
        executable_guard["resolved_path"],
        executable_guard["binding"],
        label,
        "post_execution",
        errors,
    )
    if completed.returncode != 0:
        errors.append(f"{label}_recomputation_exit_mismatch")
    if completed.stderr:
        errors.append(f"{label}_recomputation_stderr_not_empty")
    attestation_raw, separator, result_raw = completed.stdout.partition(b"\n")
    if (
        not separator
        or not result_raw
        or not result_raw.endswith(b"\n")
        or result_raw.count(b"\n") != 1
    ):
        errors.append(f"{label}_execution_attestation_framing_invalid")
        return b""
    try:
        attestation = json.loads(
            attestation_raw.decode("utf-8"),
            object_pairs_hook=strict_pairs,
            parse_constant=reject_constant,
            parse_float=parse_finite_float,
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKey,
        ValueError,
    ):
        errors.append(f"{label}_execution_attestation_invalid")
        return b""
    if attestation != expected_attestation:
        errors.append(f"{label}_execution_attestation_mismatch")
        return b""
    try:
        if attestation_raw != bounded_jcs(attestation):
            errors.append(f"{label}_execution_attestation_not_canonical_json")
            return b""
    except (TypeError, ValueError):
        errors.append(f"{label}_execution_attestation_not_canonical_json")
        return b""
    if attestation.get("result_line_binding") != {
        "raw_sha256": sha256(result_raw),
        "byte_count": len(result_raw),
    }:
        errors.append(f"{label}_execution_attestation_result_binding_mismatch")
        return b""
    return result_raw


def recompute_all(
    errors: list[str],
    python_selection: Path | None,
    node_selection: Path | None,
    python_source: dict[str, Any],
    node_source: dict[str, Any],
) -> int:
    prerequisites: list[str] = []
    python_executable = validate_selected_executable(
        python_selection, "python", prerequisites
    )
    node_executable = validate_selected_executable(
        node_selection, "node", prerequisites
    )
    python_observation: dict[str, Any] | None = None
    python_guard: dict[str, Any] | None = None
    node_guard: dict[str, Any] | None = None
    if python_executable is not None:
        python_observation = python_environment_observation(prerequisites)
        if PARENT_PYTHON_ANCHOR_BINDING is not None:
            python_guard = {
                "resolved_path": PARENT_PYTHON_ANCHOR,
                "binding": PARENT_PYTHON_ANCHOR_BINDING,
            }
    if node_executable is not None:
        node_verification = verify_node_installer_provenance(
            node_executable, prerequisites
        )
        if node_verification is None:
            node_executable = None
        else:
            node_executable, node_guard = node_verification
            node_runtime_observation(node_executable, prerequisites)
    if python_observation is not None:
        verify_installed_dependency_payload(
            "python",
            Path(python_observation["distribution_root"]),
            python_source,
            prerequisites,
        )
    node_package_root = SUITE / "node/node_modules/canonicalize"
    verify_installed_dependency_payload(
        "node", node_package_root, node_source, prerequisites
    )
    if node_package_root.is_dir():
        try:
            package_document = load(node_package_root / "package.json")
        except (OSError, ValueError, DuplicateKey):
            prerequisites.append("node_installed_package_manifest_invalid")
        else:
            if (
                not isinstance(package_document, dict)
                or package_document.get("name") != "canonicalize"
                or package_document.get("version") != "3.0.0"
            ):
                prerequisites.append("node_installed_package_manifest_invalid")
    if (
        python_executable is not None
        and node_executable is not None
        and python_observation is not None
        and python_guard is not None
        and node_guard is not None
    ):
        python_package_root = Path(python_observation["package_root"])
        challenges = {
            "python": f"challenge-v1:{secrets.token_hex(32)}",
            "node": f"challenge-v1:{secrets.token_hex(32)}",
        }
        commands = recomputation_argv(
            python_executable,
            node_executable,
            python_package_root,
            challenges,
        )
        validate_recomputation_argv(
            commands,
            python_executable,
            node_executable,
            python_package_root,
            challenges,
            prerequisites,
        )
    else:
        commands = {}
    if prerequisites:
        errors.extend(prerequisites)
        return 0
    python_attestation = expected_execution_attestation(
        "python",
        commands["python"],
        python_package_root,
        challenges["python"],
        binding(PYTHON_RESULT),
        python_guard["binding"],
    )
    node_attestation = expected_execution_attestation(
        "node",
        commands["node"],
        python_package_root,
        challenges["node"],
        binding(NODE_RESULT),
        node_guard["binding"],
    )
    python_raw = run_attested_exact(
        commands["python"],
        "python",
        closed_environment(),
        python_attestation,
        python_guard,
        errors,
    )
    node_raw = run_attested_exact(
        commands["node"],
        "node",
        closed_environment(),
        node_attestation,
        node_guard,
        errors,
    )
    if python_raw != PYTHON_RESULT.read_bytes():
        errors.append("python_retained_result_not_reproduced")
    if node_raw != NODE_RESULT.read_bytes():
        errors.append("node_retained_result_not_reproduced")
    return 2


def validate(
    recompute: bool,
    python_executable: Path | None,
    node_executable: Path | None,
) -> tuple[list[str], int]:
    errors: list[str] = []
    validate_file_inventory(errors)
    try:
        suite_manifest = load(SUITE_MANIFEST_PATH)
        manifest = load(INPUT_MANIFEST_PATH)
        cases = load(CASES_PATH)
        candidate = load(CANDIDATE_PATH)
    except (OSError, ValueError, DuplicateKey) as exc:
        return [f"suite_control_read_failure:{type(exc).__name__}"], 0
    if suite_manifest != EXPECTED_SUITE_MANIFEST:
        errors.append("suite_manifest_contract_mismatch")
    if not all(
        isinstance(item, dict) for item in (manifest, cases, candidate)
    ):
        return ["suite_control_shape_failure"], 0
    resources, schemas = validate_input_manifest(
        manifest, candidate, cases, errors
    )
    validate_candidate_schemas(candidate, resources, schemas, errors)
    runner = load_python_runner()
    if runner.parser_semantics_observation() != EXPECTED_PARSER_SEMANTICS:
        errors.append("bounded_parser_semantics_mismatch")
    observed_cases, fold = validate_cases(runner, manifest, cases, errors)
    python_source = validate_source_manifest(
        PYTHON_SOURCE_MANIFEST,
        "python",
        PYTHON_RUNNER,
        PYTHON_LOCK,
        errors,
    )
    node_source = validate_source_manifest(
        NODE_SOURCE_MANIFEST,
        "node",
        NODE_RUNNER,
        NODE_LOCK,
        errors,
    )
    if (
        python_source.get("source_files")
        == node_source.get("source_files")
        or binding(PYTHON_RUNNER)["raw_sha256"]
        == binding(NODE_RUNNER)["raw_sha256"]
    ):
        errors.append("runner_source_separation_mismatch")
    python_result = validate_result(
        PYTHON_RESULT,
        "python",
        PYTHON_SOURCE_MANIFEST,
        PYTHON_LOCK,
        observed_cases,
        fold.get("safe_projection", {}),
        errors,
    )
    node_result = validate_result(
        NODE_RESULT,
        "node",
        NODE_SOURCE_MANIFEST,
        NODE_LOCK,
        observed_cases,
        fold.get("safe_projection", {}),
        errors,
    )
    validate_comparison_and_execution(python_result, node_result, errors)
    recomputations = (
        recompute_all(
            errors,
            python_executable,
            node_executable,
            python_source,
            node_source,
        )
        if recompute
        else 0
    )
    return sorted(set(errors)), recomputations


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute-all", action="store_true")
    parser.add_argument("--python-executable", type=Path)
    parser.add_argument("--node-executable", type=Path)
    args = parser.parse_args(argv)
    selections = (args.python_executable, args.node_executable)
    if args.recompute_all and any(item is None for item in selections):
        parser.error(
            "--recompute-all requires both --python-executable and "
            "--node-executable"
        )
    if not args.recompute_all and any(item is not None for item in selections):
        parser.error("executable selectors require --recompute-all")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        errors, recomputations = validate(
            args.recompute_all,
            args.python_executable,
            args.node_executable,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [f"suite_check_crashed:{type(exc).__name__}"]
        recomputations = 0
    if errors:
        print("PRQ-002 identity cohort probe: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    cases = load(CASES_PATH)["cases"]
    print("PRQ-002 identity cohort probe: PASS")
    print("- 21 non-issuable probe objects")
    print(f"- {len(cases)} cases (1 safe, {len(cases) - 1} attributed known-bad)")
    print("- 20 structured digests (12 member, 4 commitment, 4 snapshot)")
    print("- two source- and language-separated retained recomputations")
    if args.recompute_all:
        print("- explicit Python and Node executable selections validated")
        print("- exact installed canonicalizer payload bytes verified")
        print(f"- {recomputations} exact runner outputs reproduced")
    print("- no profile issuance, registry admission, runtime, or Gate A authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
