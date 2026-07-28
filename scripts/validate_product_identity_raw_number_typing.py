#!/usr/bin/env python3
"""Validate the bounded PRQ-002C raw-number token observation.

The default path validates retained architecture evidence without executing a
child. ``--recompute-all`` additionally runs the exact selected CPython and
Node.js implementations with fresh challenges and requires their complete
staged projections to equal the retained results byte-for-byte.

A pass is not profile conformance, product identity, issuance, Gate A
acceptance, runtime authority, or publication authority.
"""

from __future__ import annotations

import argparse
import ast
import base64
import copy
import hashlib
import json
import math
import os
import platform
import re
import secrets
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def file_binding(path: Path) -> dict[str, Any] | None:
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


PARENT_INVOCATION = Path(getattr(sys, "_base_executable", sys.executable))
try:
    PARENT_EXECUTABLE = PARENT_INVOCATION.resolve(strict=True)
except OSError:
    PARENT_EXECUTABLE = PARENT_INVOCATION.absolute()
PARENT_EXECUTABLE_BINDING = file_binding(PARENT_EXECUTABLE)
PARENT_RUNTIME_VERSION = platform.python_version()

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_product_identity_raw_number_typing.py"
SUITE = ROOT / "tests/product-identity-raw-number-typing"
CONTRACT_SCHEMA = (
    ROOT / "architecture/canonicalization-raw-number-token-contract.schema.json"
)
CONTRACT = (
    ROOT
    / "architecture/canonicalization-raw-number-token-contract-v1-candidate.json"
)
PROFILE_CORE = ROOT / "architecture/canonicalization-profile-core-0.2-candidate.json"
PROFILE_EVIDENCE = (
    ROOT / "architecture/canonicalization-profile-0.2-candidate-evidence.json"
)
MANIFEST = SUITE / "manifest.json"
INPUT_MANIFEST = SUITE / "input-manifest.json"
VECTORS = SUITE / "vectors.json"
CASES = SUITE / "cases.json"
PYTHON_RUNNER = SUITE / "python/runner.py"
PYTHON_LOCK = SUITE / "python/dependency-lock.json"
PYTHON_SOURCE = SUITE / "python/source-manifest.json"
NODE_RUNNER = SUITE / "node/runner.mjs"
NODE_PACKAGE = SUITE / "node/package.json"
NODE_LOCK = SUITE / "node/package-lock.json"
NODE_SOURCE = SUITE / "node/source-manifest.json"
PYTHON_RESULT = SUITE / "results/python-stdlib.json"
NODE_RESULT = SUITE / "results/node-recursive-descent.json"
PYTHON_EXECUTION = SUITE / "results/python-execution-receipt.json"
NODE_EXECUTION = SUITE / "results/node-execution-receipt.json"
COMPARISON = SUITE / "results/comparison-receipt.json"
NODE_INSTALLER = ROOT / "scripts/ci/install-node.sh"

SUITE_ID = "prq-002c-raw-number-typing.0001"
VECTOR_SET_ID = "prq-002c-raw-number-vectors.synthetic.0003"
CONTRACT_ID = "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
PYTHON_ID = "python-stdlib-raw-lexeme-hooks.0003"
NODE_ID = "nodejs-recursive-descent-raw-lexeme.0003"
PYTHON_VERSION = "3.14.2"
NODE_VERSION = "24.18.0"
SOURCE_COMMIT = "a79d86b0a5e9581b3bacb57214cf180df3443566"
SOURCE_TREE = "d44e9eb4751b97871aa9c995664782a5d031fb48"
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
OBSERVED_AT_RE = re.compile(
    r"^2026-07-28T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"
)
OPAQUE_ID_RE = re.compile(r"^RN-[0-9]{4}$")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
JSON_NUMBER_TOKEN_RE = re.compile(
    r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$"
)
EXPECTED_RUNNER_BINDINGS = {
    "python": {
        "raw_sha256": (
            "sha256:70fdce9446fedddd1736fb938e29bba5400be877c8868e534a8f1a710d036d77"
        ),
        "byte_count": 19503,
    },
    "node": {
        "raw_sha256": (
            "sha256:272ddb8c81dd37cef84068621d60a9e0d00b6552c9955036942bb863daad879a"
        ),
        "byte_count": 22728,
    },
}

EXPECTED_SUITE_FILES = {
    "README.md",
    "manifest.json",
    "input-manifest.json",
    "vectors.json",
    "cases.json",
    "python/runner.py",
    "python/dependency-lock.json",
    "python/source-manifest.json",
    "node/runner.mjs",
    "node/package.json",
    "node/package-lock.json",
    "node/source-manifest.json",
    "results/python-stdlib.json",
    "results/node-recursive-descent.json",
    "results/python-execution-receipt.json",
    "results/node-execution-receipt.json",
    "results/comparison-receipt.json",
}
VECTOR_KEYS = {
    "sequence_index",
    "vector_id",
    "media_type",
    "decoded_raw_sha256",
    "decoded_byte_count",
    "input_base64",
}
RESULT_ROW_KEYS = {
    "sequence_index",
    "vector_id",
    "decoded_input_sha256",
    "decoded_byte_count",
    "lexical_disposition",
    "position_rule",
    "raw_number_token",
    "raw_number_token_byte_count",
    "token_class",
    "binary64_conversion_class",
    "integer_position_disposition",
    "final_disposition",
    "final_code",
    "integer_decimal",
}
EXPECTED_ATTESTATION_KEYS = {
    "schema_version",
    "artifact_class",
    "suite_id",
    "implementation_id",
    "challenge",
    "argv",
    "runtime",
    "runner_binding",
    "source_manifest_binding",
    "input_manifest_binding",
    "vector_set_binding",
    "token_contract_binding",
    "result_line_binding",
    "network_access_requested",
    "private_expectations_received",
    "peer_source_received",
    "peer_result_received",
    "product_identity_computed",
}
RAW_BINDING_KEYS = {"raw_sha256", "byte_count"}
REPOSITORY_BINDING_KEYS = {
    "repository_path",
    "raw_sha256",
    "byte_count",
}
EXECUTABLE_OBSERVATION_KEYS = {
    "invocation_path",
    "resolved_path",
    "raw_sha256",
    "byte_count",
    "pre_execution_binding",
    "post_execution_binding",
}
RUNTIME_ATTESTATION_KEYS = {"family", "version", "executable"}
CASES_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "expectation_set_id",
    "suite_id",
    "vector_set_id",
    "case_count",
    "safe_count",
    "known_bad_count",
    "cases",
    "gate_known_bads",
}
CASE_BASE_KEYS = {
    "sequence_index",
    "vector_id",
    "name",
    "kind",
    "expected_lexical_disposition",
    "expected_position_rule",
    "expected_raw_number_token",
    "expected_raw_number_token_byte_count",
    "expected_token_class",
    "expected_binary64_conversion_class",
    "expected_integer_position_disposition",
    "expected_final_disposition",
    "expected_final_code",
    "expected_integer_decimal",
    "expected_errors",
}
GATE_KNOWN_BAD_KEYS = {"id", "mutation", "expected_guard"}
EXPECTED_CLAIM_BOUNDARY = {
    "bounded_raw_number_observation_produced": True,
    "source_separated_agreement_observed": False,
    "generic_schema_path_evaluation_proved": False,
    "number_position_semantics_complete": False,
    "successor_profile_conformance_complete": False,
    "product_identity_computed": False,
    "profile_issued": False,
    "gate_a_complete": False,
    "runtime_authorized": False,
    "publication_authorized": False,
}
EXPECTED_GATE_ROWS = {
    "answer-field-leakage": (
        "vectors_add_expected_outcome",
        "answer_free_boundary",
    ),
    "outcome-bearing-id": (
        "replace_opaque_id_with_accept_label",
        "opaque_vector_id_boundary",
    ),
    "decoded-byte-substitution": (
        "change_base64_without_binding",
        "decoded_input_binding",
    ),
    "gate-a-claim": ("set_gate_a_complete_true", "authority_boundary"),
    "runtime-authority-claim": (
        "set_runtime_authorized_true",
        "authority_boundary",
    ),
    "publication-authority-claim": (
        "set_publication_authorized_true",
        "authority_boundary",
    ),
    "generic-schema-path-claim": (
        "set_generic_schema_path_evaluation_proved_true",
        "claim_scope_boundary",
    ),
    "number-position-complete-claim": (
        "set_number_position_semantics_complete_true",
        "claim_scope_boundary",
    ),
    "independence-claims": (
        "set_organizational_and_independent_host_claims_true",
        "independence_boundary",
    ),
    "fresh-attestation-claim-injection": (
        "add_profile_issued_to_child_runtime_attestation",
        "attestation_shape_boundary",
    ),
    "expectation-root-authority-injection": (
        "add_gate_a_complete_to_private_expectation_root",
        "private_expectation_shape_boundary",
    ),
    "suite-manifest-json-type-alias": (
        "replace_manifest_json_scalars_with_python_equal_aliases",
        "suite_manifest_exact_json_boundary",
    ),
    "dependency-control-authority-injection": (
        "add_runtime_authorized_to_python_dependency_lock",
        "dependency_control_exact_json_boundary",
    ),
    "case-stage-json-type-alias": (
        "replace_case_integer_byte_count_with_boolean_true",
        "private_expectation_type_boundary",
    ),
    "strict-json-nonfinite-number": (
        "present_nan_infinity_and_overflow_literals_to_strict_loader",
        "strict_json_parser_boundary",
    ),
    "suite-inventory-hidden-file": (
        "add_hidden_node_modules_file_to_suite_inventory",
        "exact_suite_inventory_boundary",
    ),
    "node-single-quoted-network-import": (
        "append_single_quoted_node_http_import",
        "source_import_boundary",
    ),
    "node-alternate-module-acquisition": (
        "append_side_effect_dynamic_bare_builtin_and_fetch_access",
        "source_import_boundary",
    ),
    "python-dynamic-network-import": (
        "append_python_dunder_import_socket_call",
        "source_import_boundary",
    ),
    "invalid-observation-timestamp": (
        "replace_observed_time_with_out_of_range_values",
        "execution_receipt_identity_boundary",
    ),
    "peer-source-import": (
        "python_source_names_node_runner",
        "source_separation_boundary",
    ),
    "peer-result-import": (
        "node_source_names_retained_python_result",
        "peer_result_boundary",
    ),
    "stale-implementation-causal-binding": (
        "relabel_copied_result_without_recomputing_causal_binding",
        "implementation_causal_binding_consistency",
    ),
    "missing-result": ("drop_last_vector_result", "complete_result_inventory"),
    "extra-result": (
        "duplicate_first_vector_result",
        "complete_result_inventory",
    ),
    "reordered-result": (
        "swap_first_two_vector_results",
        "ordered_result_inventory",
    ),
    "outcome-substitution": (
        "flip_one_final_disposition",
        "private_expectation_boundary",
    ),
    "reason-substitution": (
        "replace_one_final_code",
        "private_expectation_boundary",
    ),
    "stage-substitution": (
        "replace_one_binary64_class",
        "staged_projection_boundary",
    ),
    "source-manifest-drift": (
        "replace_runner_digest",
        "source_binding_boundary",
    ),
    "runtime-version-drift": (
        "replace_runtime_version",
        "runtime_binding_boundary",
    ),
    "challenge-replay": ("reuse_peer_challenge", "fresh_challenge_boundary"),
    "stdout-substitution": (
        "replace_stdout_digest",
        "stdout_binding_boundary",
    ),
    "comparison-substitution": (
        "replace_projection_digest",
        "complete_projection_comparison",
    ),
    "unclassified-crash": (
        "replace_refusal_with_crash",
        "classified_result_boundary",
    ),
    "product-identity-claim": (
        "set_product_identity_computed_true",
        "authority_boundary",
    ),
    "profile-conformance-claim": (
        "set_successor_profile_conformance_complete_true",
        "claim_scope_boundary",
    ),
    "issuance-claim": ("set_profile_issued_true", "authority_boundary"),
    "input-manifest-expectation-path-leak": (
        "add_private_expectation_path_to_child_manifest",
        "answer_free_input_manifest",
    ),
    "suite-manifest-binding-substitution": (
        "replace_suite_manifest_digest_in_comparison",
        "comparison_context_binding",
    ),
    "comparator-expectation-binding-substitution": (
        "replace_private_expectation_digest_in_comparison",
        "comparison_context_binding"
    ),
    "execution-receipt-binding-substitution": (
        "replace_execution_receipt_digest_in_comparison",
        "execution_receipt_binding",
    ),
    "validator-binding-substitution": (
        "replace_validator_digest_in_comparison",
        "validator_binding",
    ),
    "measured-census-substitution": (
        "claim_one_unclassified_error",
        "measured_census_boundary",
    ),
}


class DuplicateKey(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_non_json_constant(value: str) -> Any:
    raise ValueError(f"non-JSON numeric constant {value!r}")


def parse_finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON number {value!r}")
    return parsed


def loads_strict(raw: bytes) -> Any:
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_non_json_constant,
        parse_float=parse_finite_json_float,
    )


def load(path: Path) -> dict[str, Any]:
    value = loads_strict(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one object")
    return value


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def repository_binding(path: Path, *, role: str | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    result = {
        "repository_path": path.relative_to(ROOT).as_posix(),
        "raw_sha256": sha256(raw),
        "byte_count": len(raw),
    }
    if role is not None:
        result = {"role": role, **result}
    return result


def json_exact(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            json_exact(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            json_exact(a, b) for a, b in zip(left, right, strict=True)
        )
    return left == right


def exact_object_keys(value: Any, expected: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == expected


def child_attestation_shape_is_exact(value: Any) -> bool:
    if not exact_object_keys(value, EXPECTED_ATTESTATION_KEYS):
        return False
    runtime = value["runtime"]
    if not exact_object_keys(runtime, RUNTIME_ATTESTATION_KEYS):
        return False
    if not exact_object_keys(runtime["executable"], REPOSITORY_BINDING_KEYS):
        return False
    if not exact_object_keys(value["runner_binding"], REPOSITORY_BINDING_KEYS):
        return False
    for key in (
        "source_manifest_binding",
        "input_manifest_binding",
        "vector_set_binding",
        "token_contract_binding",
    ):
        if not exact_object_keys(value[key], REPOSITORY_BINDING_KEYS):
            return False
    return exact_object_keys(value["result_line_binding"], RAW_BINDING_KEYS)


def executable_observation_shape_is_exact(value: Any) -> bool:
    return (
        exact_object_keys(value, EXECUTABLE_OBSERVATION_KEYS)
        and exact_object_keys(value["pre_execution_binding"], RAW_BINDING_KEYS)
        and exact_object_keys(value["post_execution_binding"], RAW_BINDING_KEYS)
    )


def add(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def suite_inventory() -> set[str]:
    return {
        path.relative_to(SUITE).as_posix()
        for path in SUITE.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def suite_symlinks() -> set[str]:
    return {
        path.relative_to(SUITE).as_posix()
        for path in SUITE.rglob("*")
        if path.is_symlink()
    }


def inventory_guard_codes(
    paths: set[str],
    symlinks: set[str] | None = None,
) -> set[str]:
    if paths != EXPECTED_SUITE_FILES or symlinks:
        return {"exact_suite_inventory_boundary"}
    return set()


STRICT_JSON_KNOWN_BAD_PAYLOADS = (
    b'{"value":NaN}',
    b'{"value":Infinity}',
    b'{"value":-Infinity}',
    b'{"value":1e999}',
    b'{"value":-1e999}',
    b'{"value":1,"value":2}',
)


def strict_json_known_bads_fire() -> bool:
    for payload in STRICT_JSON_KNOWN_BAD_PAYLOADS:
        try:
            loads_strict(payload)
        except (
            UnicodeError,
            json.JSONDecodeError,
            DuplicateKey,
            ValueError,
        ):
            continue
        return False
    return True


def validate_strict_json_loader(errors: list[str]) -> None:
    try:
        control = loads_strict(b'{"value":1.25}')
    except (
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKey,
        ValueError,
    ) as exc:
        add(errors, f"strict JSON positive control failed: {exc}")
        return
    if not json_exact(control, {"value": 1.25}):
        add(errors, "strict JSON positive control differs")
    if not strict_json_known_bads_fire():
        add(errors, "strict JSON known-bad parser boundary did not fire")


def validate_contract(errors: list[str], contract: dict[str, Any]) -> None:
    try:
        schema = load(CONTRACT_SCHEMA)
        Draft202012Validator.check_schema(schema)
        validation_errors = sorted(
            Draft202012Validator(schema).iter_errors(contract),
            key=lambda item: list(item.absolute_path),
        )
    except Exception as exc:
        add(errors, f"raw-number contract schema could not be evaluated: {exc}")
        return
    for error in validation_errors:
        pointer = "/" + "/".join(map(str, error.absolute_path))
        add(errors, f"raw-number contract {pointer}: {error.message}")
    inventory = contract.get("blocked_candidate_binding", {}).get(
        "frozen_artifact_inventory"
    )
    if not isinstance(inventory, list):
        add(errors, "raw-number contract frozen inventory is absent")
        return
    for row in inventory:
        if not isinstance(row, dict):
            add(errors, "raw-number contract frozen inventory row is not an object")
            continue
        path_value = row.get("path")
        if not isinstance(path_value, str):
            add(errors, "raw-number contract frozen inventory path is invalid")
            continue
        path = ROOT / path_value
        if not path.is_file() or path.is_symlink():
            add(errors, f"raw-number frozen predecessor is absent: {path_value}")
            continue
        raw = path.read_bytes()
        if (
            row.get("raw_sha256") != sha256(raw)
            or row.get("byte_count_decimal") != str(len(raw))
        ):
            add(errors, f"raw-number frozen predecessor binding drifted: {path_value}")


def validate_profile_nonclaims(
    errors: list[str],
    profile_evidence: dict[str, Any],
) -> None:
    conformance = profile_evidence.get("conformance_evidence")
    if not isinstance(conformance, dict):
        add(errors, "0.2 conformance evidence is absent")
        return
    expected_conformance = {
        "successor_suite_id": None,
        "case_count": None,
        "accepted_count": None,
        "refused_count": None,
        "unclassified_error_count": None,
        "source_separated_implementation_count": None,
        "implementation_agreement": None,
        "organizational_independence_proven": False,
        "independent_host_reproduction_complete": False,
        "successor_profile_conformance_complete": False,
        "known_bad_self_test_complete": False,
        "missing_values_must_not_be_interpreted_as_zero": True,
    }
    if not json_exact(conformance, expected_conformance):
        add(errors, "0.2 conformance false/null boundary drifted")
    acceptance = profile_evidence.get("acceptance_boundary")
    if not isinstance(acceptance, dict):
        add(errors, "0.2 acceptance boundary is absent")
        return
    forbidden_true = {
        "canonical_identity_may_be_issued",
        "schema_resources_admitted",
        "product_members_constructed",
        "product_snapshots_constructed",
        "product_root_constructed",
        "gate_a_complete",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
    }
    forbidden_refs = {
        "profile_core_canonical_digest",
        "profile_registry_member_ref",
        "schema_registry_snapshot_ref",
        "engine_contract_root_ref",
        "activation_ref",
    }
    if any(acceptance.get(key) is not False for key in forbidden_true):
        add(errors, "0.2 acceptance authority boundary escalated")
    if any(acceptance.get(key) is not None for key in forbidden_refs):
        add(errors, "0.2 acceptance reference boundary escalated")


def expected_input_bindings() -> list[dict[str, Any]]:
    return [
        repository_binding(VECTORS, role="vectors"),
        repository_binding(CONTRACT, role="token_contract"),
        repository_binding(CONTRACT_SCHEMA, role="token_contract_schema"),
        repository_binding(PROFILE_CORE, role="blocked_profile_core"),
        repository_binding(PROFILE_EVIDENCE, role="blocked_profile_evidence"),
    ]


def expected_input_manifest() -> dict[str, Any]:
    return {
        "schema_version": "0.2.0",
        "artifact_class": "prq_002c_raw_number_input_manifest",
        "manifest_id": "prq-002c-raw-number-input-manifest.0003",
        "suite_id": SUITE_ID,
        "vector_set_id": VECTOR_SET_ID,
        "blocked_profile_predecessor_checkpoint": {
            "commit": SOURCE_COMMIT,
            "tree": SOURCE_TREE,
        },
        "answer_free_child_input": True,
        "binding_count": 5,
        "bindings": expected_input_bindings(),
    }


def validate_input_manifest(
    errors: list[str],
    document: dict[str, Any],
) -> None:
    expected = expected_input_manifest()
    if not json_exact(document, expected):
        add(errors, "answer-free input manifest differs from exact retained bindings")


def expected_suite_manifest() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002c_raw_number_typing_suite_manifest",
        "suite_id": SUITE_ID,
        "status": "architecture_only_non_product_observation",
        "decision_ref": (
            "docs/decisions/0101-require-raw-number-token-provenance-"
            "before-profile-conformance.md"
        ),
        "scope": {
            "contract_id": CONTRACT_ID,
            "blocked_profile_id": (
                "urn:odeya:canonicalization:odeya-jcs-0.2"
            ),
            "prospective_profile_id": (
                "urn:odeya:canonicalization:odeya-jcs-0.3"
            ),
            "input_class": "synthetic_non_product_raw_json_frames",
            "position_rules_observed": [
                "type_integer",
                "integer_const_decimal_1",
            ],
            "number_position_semantics_complete": False,
        },
        "census": {
            "vector_count": 61,
            "accepted_count": 9,
            "refused_count": 52,
            "source_separated_implementation_count": 2,
            "gate_known_bad_count": len(EXPECTED_GATE_ROWS),
        },
        "retained_paths": {
            "input_manifest": INPUT_MANIFEST.relative_to(ROOT).as_posix(),
            "vectors": VECTORS.relative_to(ROOT).as_posix(),
            "private_expectations": CASES.relative_to(ROOT).as_posix(),
            "python_source_manifest": PYTHON_SOURCE.relative_to(ROOT).as_posix(),
            "node_source_manifest": NODE_SOURCE.relative_to(ROOT).as_posix(),
            "python_result": PYTHON_RESULT.relative_to(ROOT).as_posix(),
            "node_result": NODE_RESULT.relative_to(ROOT).as_posix(),
            "python_execution_receipt": (
                PYTHON_EXECUTION.relative_to(ROOT).as_posix()
            ),
            "node_execution_receipt": (
                NODE_EXECUTION.relative_to(ROOT).as_posix()
            ),
            "comparison_receipt": COMPARISON.relative_to(ROOT).as_posix(),
            "validator": VALIDATOR.relative_to(ROOT).as_posix(),
        },
        "implementation_contract": {
            "roles": ["python", "node"],
            "shared_evaluator_source_allowed": False,
            "peer_source_consumption_allowed": False,
            "peer_result_consumption_allowed": False,
            "private_expectation_consumption_allowed": False,
            "private_expectations_passed_in_child_argv": False,
            "child_filesystem_isolation_proven": False,
            "complete_ordered_staged_projection_required": True,
            "fresh_challenge_self_attestation_required": True,
            "runtime_executable_pre_and_post_binding_required": True,
            "python": {
                "runtime": "CPython 3.14.2",
                "third_party_dependency_count": 0,
                "parser_strategy": (
                    "stdlib_json_raw_pairs_deferred_restriction_classification"
                ),
            },
            "node": {
                "runtime": "Node.js 24.18.0",
                "third_party_dependency_count": 0,
                "parser_strategy": (
                    "recursive_descent_deferred_restriction_classification"
                ),
            },
        },
        "claim_boundary": {
            "bounded_raw_number_observation_required": True,
            "source_separated_agreement_must_be_retained_externally": True,
            "organizational_independence_proven": False,
            "independent_host_reproduction_complete": False,
            "generic_schema_path_evaluation_proved": False,
            "unique_instance_pointer_retention_proved": False,
            "dynamic_path_discovery_excluded": False,
            "historical_process_independently_witnessed": False,
            "successor_profile_conformance_complete": False,
            "product_identity_computed": False,
            "profile_issued": False,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "publication_authorized": False,
        },
    }


def validate_manifest(errors: list[str], document: dict[str, Any]) -> None:
    if not json_exact(document, expected_suite_manifest()):
        add(errors, "suite manifest exact JSON or authority boundary differs")


def expected_dependency_controls() -> dict[str, dict[str, Any]]:
    node_name = "odeya-prq-002c-raw-number-node-observer"
    node_version = "0.3.0"
    node_engine = {"node": NODE_VERSION}
    return {
        "python": {
            "schema_version": "0.1.0",
            "implementation_id": PYTHON_ID,
            "runtime": f"CPython {PYTHON_VERSION}",
            "third_party_distribution_count": 0,
            "third_party_distributions": [],
            "stdlib_modules": [
                "argparse",
                "base64",
                "dataclasses",
                "hashlib",
                "json",
                "math",
                "pathlib",
                "platform",
                "re",
                "sys",
                "typing",
            ],
        },
        "node_package": {
            "name": node_name,
            "private": True,
            "version": node_version,
            "type": "module",
            "engines": node_engine,
        },
        "node_lock": {
            "name": node_name,
            "version": node_version,
            "lockfileVersion": 3,
            "requires": True,
            "packages": {
                "": {
                    "name": node_name,
                    "version": node_version,
                    "engines": node_engine,
                }
            },
        },
    }


def validate_dependency_controls(
    errors: list[str],
    *,
    python_lock: dict[str, Any],
    node_package: dict[str, Any],
    node_lock: dict[str, Any],
) -> None:
    expected = expected_dependency_controls()
    observed = {
        "python": python_lock,
        "node_package": node_package,
        "node_lock": node_lock,
    }
    if not json_exact(observed, expected):
        add(errors, "dependency controls differ from exact zero-third-party JSON")


def private_expectation_shape_is_exact(document: Any) -> bool:
    if not exact_object_keys(document, CASES_ROOT_KEYS):
        return False
    case_rows = document["cases"]
    gate_rows = document["gate_known_bads"]
    if not isinstance(case_rows, list) or not isinstance(gate_rows, list):
        return False
    for row in case_rows:
        if not isinstance(row, dict):
            return False
        expected = CASE_BASE_KEYS | (
            {"intent_errors"} if row.get("kind") == "known_bad" else set()
        )
        if set(row) != expected:
            return False
    return all(
        exact_object_keys(row, GATE_KNOWN_BAD_KEYS)
        for row in gate_rows
    )


def private_expectation_row_is_well_typed(row: Any) -> bool:
    if not isinstance(row, dict):
        return False
    nullable_enums = {
        "expected_position_rule": {
            None,
            "integer_const_decimal_1",
            "type_integer",
        },
        "expected_token_class": {None, "integer_token", "number_token"},
        "expected_binary64_conversion_class": {
            None,
            "finite_nonzero",
            "negative_zero_exact_decimal",
            "nonfinite",
            "positive_zero",
            "underflow_to_negative_zero",
            "underflow_to_positive_zero",
        },
        "expected_integer_position_disposition": {
            None,
            "accepted",
            "refused",
        },
    }
    if (
        not isinstance(row.get("expected_lexical_disposition"), str)
        or row.get("expected_lexical_disposition")
        not in {"accepted", "refused"}
        or not isinstance(row.get("expected_final_disposition"), str)
        or row.get("expected_final_disposition") not in {"accepted", "refused"}
        or any(
            (
                row.get(key) is not None
                and (
                    not isinstance(row.get(key), str)
                    or row.get(key) not in allowed
                )
            )
            for key, allowed in nullable_enums.items()
        )
    ):
        return False
    raw_token = row.get("expected_raw_number_token")
    token_byte_count = row.get("expected_raw_number_token_byte_count")
    if raw_token is None:
        if token_byte_count is not None:
            return False
    elif (
        not isinstance(raw_token, str)
        or not raw_token.isascii()
        or JSON_NUMBER_TOKEN_RE.fullmatch(raw_token) is None
        or type(token_byte_count) is not int
        or token_byte_count != len(raw_token)
    ):
        return False
    final_code = row.get("expected_final_code")
    allowed_final_codes = {
        None,
        "ODEYA_CONFORMANCE_FRAME_SHAPE",
        "ODEYA_LIMIT_NUMBER_TOKEN",
        "ODEYA_NUMBER_DOMAIN",
        "ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED",
        "ODEYA_NUMBER_NEGATIVE_ZERO",
        "ODEYA_NUMBER_NONFINITE",
        "ODEYA_NUMBER_UNDERFLOW",
        "ODEYA_PARSE_BOM",
        "ODEYA_PARSE_DUPLICATE_KEY",
        "ODEYA_PARSE_SYNTAX",
        "ODEYA_PARSE_UNPAIRED_SURROGATE",
        "ODEYA_PARSE_UTF8",
        "ODEYA_SCHEMA_CONST",
        "ODEYA_SCHEMA_TYPE",
    }
    integer_decimal = row.get("expected_integer_decimal")
    if (
        (
            final_code is not None
            and (
                not isinstance(final_code, str)
                or final_code not in allowed_final_codes
            )
        )
        or (
            integer_decimal is not None
            and (
                not isinstance(integer_decimal, str)
                or re.fullmatch(r"-?(?:0|[1-9][0-9]*)", integer_decimal)
                is None
            )
        )
    ):
        return False
    expected_errors = row.get("expected_errors")
    return isinstance(expected_errors, list) and all(
        isinstance(code, str) and code in allowed_final_codes - {None}
        for code in expected_errors
    )


def observed_at_output_close_is_exact(value: Any) -> bool:
    if not isinstance(value, str) or not OBSERVED_AT_RE.fullmatch(value):
        return False
    try:
        observed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return observed.strftime("%Y-%m-%dT%H:%M:%S.%fZ") == value


def validate_source_manifest(
    errors: list[str],
    *,
    role: str,
    document: dict[str, Any],
    expected_id: str,
    expected_runtime: str,
    expected_strategy: str,
    expected_files: list[tuple[str, Path]],
) -> None:
    expected_rows = [
        repository_binding(path, role=file_role)
        for file_role, path in expected_files
    ]
    expected = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002c_source_manifest",
        "suite_id": SUITE_ID,
        "role": role,
        "implementation_id": expected_id,
        "language": "Python" if role == "python" else "JavaScript",
        "runtime_version": expected_runtime,
        "parser_strategy": expected_strategy,
        "source_file_count": len(expected_files),
        "source_files": expected_rows,
        "allowed_input_roles": [
            "vectors",
            "input_manifest",
            "token_contract",
            "token_contract_schema",
            "blocked_profile_core",
            "blocked_profile_evidence",
            "source_manifest",
            "fresh_challenge",
        ],
        "private_expectation_consumption_allowed": False,
        "peer_source_consumption_allowed": False,
        "peer_result_consumption_allowed": False,
        "network_access_requested": False,
        "filesystem_isolation_proven": False,
        "third_party_dependency_count": 0,
    }
    if not json_exact(document, expected):
        add(errors, f"{role} source manifest identity, bytes, or nonclaim differs")


def source_import_boundary_findings(
    python_text: str,
    node_text: str,
) -> list[str]:
    findings: list[str] = []
    encoded_sources = {
        "python": python_text.encode("utf-8"),
        "node": node_text.encode("utf-8"),
    }
    for role, raw in encoded_sources.items():
        if not json_exact(
            {
                "raw_sha256": sha256(raw),
                "byte_count": len(raw),
            },
            EXPECTED_RUNNER_BINDINGS[role],
        ):
            findings.append(
                f"{role} source differs from the exact retained capability surface"
            )

    try:
        python_tree = ast.parse(python_text)
    except SyntaxError as exc:
        findings.append(f"python observer source is invalid: {exc}")
    else:
        imported: set[str] = set()
        forbidden_calls: set[str] = set()
        for node in ast.walk(python_tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                function = node.func
                if isinstance(function, ast.Name) and function.id in {
                    "__import__",
                    "compile",
                    "eval",
                    "exec",
                }:
                    forbidden_calls.add(function.id)
                elif isinstance(function, ast.Attribute) and function.attr in {
                    "__import__",
                    "import_module",
                }:
                    forbidden_calls.add(function.attr)
        declared = set(
            expected_dependency_controls()["python"]["stdlib_modules"]
        )
        if imported - {"__future__"} != declared:
            findings.append(
                "python declared standard-library dependency set differs"
            )
        if imported & {
            "ftplib",
            "http",
            "importlib",
            "requests",
            "socket",
            "urllib",
        }:
            findings.append(
                "python observer imports a network/module-acquisition capability"
            )
        if forbidden_calls:
            findings.append(
                "python observer uses forbidden dynamic code/module acquisition: "
                + ", ".join(sorted(forbidden_calls))
            )

    expected_node_import_lines = [
        'import { createHash } from "node:crypto";',
        'import { readFileSync, realpathSync } from "node:fs";',
        'import process from "node:process";',
    ]
    observed_node_import_lines = [
        line.strip()
        for line in node_text.splitlines()
        if re.match(r"^\s*import(?:\s|\{|\*)", line)
    ]
    if observed_node_import_lines != expected_node_import_lines:
        findings.append("node static import declarations differ")

    node_specifiers: list[str] = []
    for pattern in (
        r"""\bfrom\s*(["'])([^"'\r\n]+)\1""",
        r"""\bimport\s*\(\s*(["'])([^"'\r\n]+)\1""",
        r"""(?m)^\s*import\s+(["'])([^"'\r\n]+)\1""",
    ):
        node_specifiers.extend(
            match.group(2) for match in re.finditer(pattern, node_text)
        )
    expected_node_specifiers = ["node:crypto", "node:fs", "node:process"]
    if sorted(node_specifiers) != sorted(expected_node_specifiers):
        findings.append("node module specifier inventory differs")
    if any(
        specifier not in set(expected_node_specifiers)
        for specifier in node_specifiers
    ):
        findings.append("node observer acquires a module outside the exact allowlist")
    if re.search(
        r"\b(?:createRequire|getBuiltinModule|require)\s*\(",
        node_text,
    ) or re.search(
        r"\b(?:Module\s*\.\s*_load|process\s*\.\s*(?:_linkedBinding|binding))\s*\(",
        node_text,
    ):
        findings.append("node observer uses alternate module acquisition")
    if re.search(
        r"\b(?:EventSource|WebSocket|fetch)\s*\(",
        node_text,
    ):
        findings.append("node observer uses a global network capability")
    return findings


def validate_source_separation(
    errors: list[str],
    python_text: str,
    node_text: str,
) -> None:
    python_forbidden = {
        "nodejs-recursive-descent-raw-lexeme.0003",
        "node/runner.mjs",
        "cases.json",
        "results/node-recursive-descent.json",
    }
    node_forbidden = {
        "python-stdlib-raw-lexeme-hooks.0003",
        "python/runner.py",
        "cases.json",
        "results/python-stdlib.json",
    }
    for needle in sorted(python_forbidden):
        if needle in python_text:
            add(errors, f"python source separation boundary contains {needle!r}")
    for needle in sorted(node_forbidden):
        if needle in node_text:
            add(errors, f"node source separation boundary contains {needle!r}")
    for finding in source_import_boundary_findings(python_text, node_text):
        add(errors, finding)
    if PYTHON_RUNNER.read_bytes() == NODE_RUNNER.read_bytes():
        add(errors, "observer source bytes are not separated")


def validate_vectors_and_cases(
    errors: list[str],
    vectors: dict[str, Any],
    cases: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expected_vector_root = {
        "schema_version",
        "artifact_class",
        "vector_set_id",
        "status",
        "answer_free",
        "opaque_vector_ids",
        "expected_outcomes_present",
        "decoded_input_bindings_present",
        "vector_count",
        "vectors",
    }
    if set(vectors) != expected_vector_root or (
        vectors.get("schema_version") != "0.3.0"
        or vectors.get("artifact_class")
        != "prq_002c_answer_free_raw_number_vector_set"
        or vectors.get("vector_set_id") != VECTOR_SET_ID
        or vectors.get("status") != "synthetic_non_product_answer_free"
        or vectors.get("answer_free") is not True
        or vectors.get("opaque_vector_ids") is not True
        or vectors.get("expected_outcomes_present") is not False
        or vectors.get("decoded_input_bindings_present") is not True
    ):
        add(errors, "answer-free vector root differs")
    rows = vectors.get("vectors")
    if not isinstance(rows, list):
        add(errors, "answer-free vector rows are absent")
        rows = []
    if type(vectors.get("vector_count")) is not int or (
        vectors.get("vector_count") != len(rows)
    ):
        add(errors, "answer-free vector count differs")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != VECTOR_KEYS:
            add(errors, f"answer-free vector {index} shape differs")
            continue
        vector_id = row.get("vector_id")
        if (
            type(row.get("sequence_index")) is not int
            or row.get("sequence_index") != index
            or not isinstance(vector_id, str)
            or not OPAQUE_ID_RE.fullmatch(vector_id)
            or vector_id in seen
            or row.get("media_type") != "application/json"
            or not isinstance(row.get("input_base64"), str)
        ):
            add(errors, f"answer-free vector {index} identity differs")
            continue
        seen.add(vector_id)
        try:
            raw = base64.b64decode(row["input_base64"], validate=True)
        except (ValueError, TypeError):
            add(errors, f"answer-free vector {index} base64 is invalid")
            continue
        if (
            row.get("decoded_raw_sha256") != sha256(raw)
            or type(row.get("decoded_byte_count")) is not int
            or row.get("decoded_byte_count") != len(raw)
        ):
            add(errors, f"answer-free vector {index} decoded binding differs")

    case_rows = cases.get("cases")
    if (
        not private_expectation_shape_is_exact(cases)
        or cases.get("schema_version") != "0.3.0"
        or cases.get("artifact_class")
        != "prq_002c_private_raw_number_expectations"
        or cases.get("expectation_set_id")
        != "prq-002c-raw-number-cases.private.0005"
        or cases.get("suite_id") != SUITE_ID
        or cases.get("vector_set_id") != VECTOR_SET_ID
        or not isinstance(case_rows, list)
    ):
        add(errors, "private expectation identity differs")
        case_rows = [] if not isinstance(case_rows, list) else case_rows
    safe = sum(
        isinstance(row, dict) and row.get("kind") == "safe"
        for row in case_rows
    )
    bad = sum(
        isinstance(row, dict) and row.get("kind") == "known_bad"
        for row in case_rows
    )
    if (
        type(cases.get("case_count")) is not int
        or type(cases.get("safe_count")) is not int
        or type(cases.get("known_bad_count")) is not int
        or cases.get("case_count") != len(case_rows)
        or cases.get("safe_count") != safe
        or cases.get("known_bad_count") != bad
        or (len(case_rows), safe, bad) != (61, 9, 52)
    ):
        add(errors, "private expectation census differs")
    if len(rows) != len(case_rows):
        add(errors, "vector/expectation one-to-one inventory differs")
    for index, (vector, case) in enumerate(zip(rows, case_rows)):
        if not isinstance(vector, dict) or not isinstance(case, dict):
            continue
        kind = case.get("kind")
        expected_case_keys = CASE_BASE_KEYS | (
            {"intent_errors"} if kind == "known_bad" else set()
        )
        if set(case) != expected_case_keys:
            add(errors, f"private expectation {index} shape differs")
        if not private_expectation_row_is_well_typed(case):
            add(errors, f"private expectation {index} staged type/domain differs")
        if (
            type(case.get("sequence_index")) is not int
            or case.get("sequence_index") != index
            or case.get("vector_id") != vector.get("vector_id")
            or not isinstance(case.get("name"), str)
            or not case["name"]
        ):
            add(errors, f"private expectation {index} identity differs")
        if kind == "known_bad":
            code = case.get("expected_final_code")
            if (
                not isinstance(code, str)
                or not json_exact(case.get("intent_errors"), [code])
                or not json_exact(case.get("expected_errors"), [code])
                or case.get("expected_final_disposition") != "refused"
            ):
                add(errors, f"private expectation {index} attribution differs")
        elif kind == "safe":
            if (
                not json_exact(case.get("expected_errors"), [])
                or case.get("expected_final_code") is not None
                or case.get("expected_final_disposition") != "accepted"
            ):
                add(errors, f"private safe expectation {index} differs")
        else:
            add(errors, f"private expectation {index} kind differs")
    gate_rows = cases.get("gate_known_bads")
    if not isinstance(gate_rows, list):
        add(errors, "gate known-bad rows are absent")
    else:
        if any(
            not exact_object_keys(row, GATE_KNOWN_BAD_KEYS)
            or not all(isinstance(row[key], str) for key in GATE_KNOWN_BAD_KEYS)
            for row in gate_rows
        ):
            add(errors, "gate known-bad row shape differs")
        observed = {
            row.get("id"): (
                row.get("mutation"),
                row.get("expected_guard"),
            )
            for row in gate_rows
            if isinstance(row, dict)
        }
        if observed != EXPECTED_GATE_ROWS or len(gate_rows) != len(observed):
            add(errors, "gate known-bad inventory differs")
    return rows, case_rows


def expected_projection(
    vector_rows: list[dict[str, Any]],
    case_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    result_rows: list[dict[str, Any]] = []
    mapping = {
        "lexical_disposition": "expected_lexical_disposition",
        "position_rule": "expected_position_rule",
        "raw_number_token": "expected_raw_number_token",
        "raw_number_token_byte_count": (
            "expected_raw_number_token_byte_count"
        ),
        "token_class": "expected_token_class",
        "binary64_conversion_class": (
            "expected_binary64_conversion_class"
        ),
        "integer_position_disposition": (
            "expected_integer_position_disposition"
        ),
        "final_disposition": "expected_final_disposition",
        "final_code": "expected_final_code",
        "integer_decimal": "expected_integer_decimal",
    }
    for vector, case in zip(vector_rows, case_rows, strict=True):
        result_rows.append(
            {
                "sequence_index": vector["sequence_index"],
                "vector_id": vector["vector_id"],
                "decoded_input_sha256": vector["decoded_raw_sha256"],
                "decoded_byte_count": vector["decoded_byte_count"],
                **{
                    output_key: case[case_key]
                    for output_key, case_key in mapping.items()
                },
            }
        )
    return {
        "suite_id": SUITE_ID,
        "vector_set_id": VECTOR_SET_ID,
        "token_contract_id": CONTRACT_ID,
        "vector_count": len(result_rows),
        "results": result_rows,
        "claim_boundary": EXPECTED_CLAIM_BOUNDARY,
    }


def expected_implementation(role: str) -> dict[str, Any]:
    if role == "python":
        source = PYTHON_SOURCE
        return {
            "role": "python",
            "implementation_id": PYTHON_ID,
            "runtime": "CPython",
            "runtime_version": PYTHON_VERSION,
            "parser_strategy": (
                "stdlib_json_raw_pairs_deferred_restriction_classification"
            ),
            "source_manifest_binding": repository_binding(source),
        }
    source = NODE_SOURCE
    return {
        "role": "node",
        "implementation_id": NODE_ID,
        "runtime": "Node.js",
        "runtime_version": NODE_VERSION,
        "parser_strategy": (
            "recursive_descent_deferred_restriction_classification"
        ),
        "source_manifest_binding": repository_binding(source),
    }


def expected_causal_binding(
    implementation: dict[str, Any],
    projection: dict[str, Any],
) -> str:
    return sha256(
        compact_json(
            {
                "implementation_id": implementation["implementation_id"],
                "source_manifest_raw_sha256": (
                    implementation["source_manifest_binding"]["raw_sha256"]
                ),
                "projection_raw_sha256": sha256(compact_json(projection)),
            }
        )
    )


def validate_result(
    errors: list[str],
    *,
    role: str,
    document: dict[str, Any],
    path: Path,
    projection: dict[str, Any],
) -> None:
    implementation = expected_implementation(role)
    expected = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002c_raw_number_observation_result",
        "implementation": implementation,
        "input_manifest_binding": repository_binding(INPUT_MANIFEST),
        "implementation_causal_binding": expected_causal_binding(
            implementation, projection
        ),
        "projection": projection,
    }
    if not json_exact(document, expected):
        add(errors, f"{role} retained result differs from complete expected projection")
    raw = path.read_bytes()
    if raw != compact_json(document) + b"\n":
        add(errors, f"{role} retained result is not one exact compact JSON line")


def expected_comparison(
    python_result: dict[str, Any],
    node_result: dict[str, Any],
) -> dict[str, Any]:
    projection_bytes = compact_json(python_result["projection"])
    return {
        "schema_version": "0.3.0",
        "artifact_class": "prq_002c_projection_comparison_receipt",
        "comparison_id": "prq-002c-raw-number-comparison.0004",
        "suite_id": SUITE_ID,
        "suite_manifest_binding": repository_binding(MANIFEST),
        "comparator_expectation_binding": repository_binding(CASES),
        "execution_receipt_bindings": [
            repository_binding(PYTHON_EXECUTION, role="python"),
            repository_binding(NODE_EXECUTION, role="node"),
        ],
        "validator_binding": repository_binding(VALIDATOR),
        "compared_result_bindings": [
            repository_binding(PYTHON_RESULT, role="python"),
            repository_binding(NODE_RESULT, role="node"),
        ],
        "projection_serialization": "ascii_key_sorted_compact_json",
        "projection_raw_sha256": sha256(projection_bytes),
        "projection_byte_count": len(projection_bytes),
        "measured_census": {
            "vector_count": 61,
            "accepted_count": 9,
            "refused_count": 52,
            "unclassified_error_count": 0,
            "source_separated_implementation_count": 2,
            "gate_known_bad_count": len(EXPECTED_GATE_ROWS),
        },
        "complete_ordered_projection_equal": True,
        "source_and_language_separation_observed": True,
        "organizational_independence_proven": False,
        "independent_host_reproduction_complete": False,
        "bounded_suite_gate_known_bad_self_test_complete": True,
        "claim_boundary": {
            "bounded_source_separated_raw_number_agreement_observed": True,
            "generic_schema_path_evaluation_proved": False,
            "number_position_semantics_complete": False,
            "unique_instance_pointer_retention_proved": False,
            "dynamic_path_discovery_excluded": False,
            "historical_process_independently_witnessed": False,
            "successor_profile_conformance_complete": False,
            "product_identity_computed": False,
            "profile_issued": False,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "publication_authorized": False,
        },
    }


def expected_receipt_claim_boundary() -> dict[str, bool]:
    return {
        "historical_process_independently_witnessed": False,
        "product_identity_computed": False,
        "profile_issued": False,
        "successor_profile_conformance_complete": False,
        "gate_a_complete": False,
        "runtime_authorized": False,
        "publication_authorized": False,
    }


def validate_execution_receipt(
    errors: list[str],
    *,
    role: str,
    receipt: dict[str, Any],
    result_path: Path,
    expected_id: str,
    expected_runtime_family: str,
    expected_runtime_version: str,
) -> None:
    expected_keys = {
        "schema_version",
        "artifact_class",
        "receipt_id",
        "suite_id",
        "implementation_id",
        "observed_at_output_close_utc",
        "blocked_profile_predecessor_checkpoint",
        "host",
        "argv",
        "challenge",
        "executable_observation",
        "process_observation",
        "attestation",
        "portable_recomputation_contract",
        "claim_boundary",
    }
    expected_receipt_id = (
        "prq-002c-python-execution.0003"
        if role == "python"
        else "prq-002c-node-execution.0003"
    )
    if set(receipt) != expected_keys or (
        receipt.get("schema_version") != "0.3.0"
        or receipt.get("artifact_class")
        != "prq_002c_execution_receipt"
        or receipt.get("suite_id") != SUITE_ID
        or receipt.get("implementation_id") != expected_id
        or receipt.get("receipt_id") != expected_receipt_id
        or not observed_at_output_close_is_exact(
            receipt.get("observed_at_output_close_utc")
        )
        or not json_exact(
            receipt.get("blocked_profile_predecessor_checkpoint"),
            {"commit": SOURCE_COMMIT, "tree": SOURCE_TREE},
        )
        or not json_exact(
            receipt.get("host"),
            {
            "operating_system": "Darwin",
            "machine": "arm64",
            "hostname_retained": False,
            "independent_host_reproduction_complete": False,
            },
        )
        or not json_exact(
            receipt.get("claim_boundary"),
            expected_receipt_claim_boundary(),
        )
    ):
        add(errors, f"{role} execution receipt identity or authority differs")
        return
    challenge = receipt.get("challenge")
    if not isinstance(challenge, str) or not CHALLENGE_RE.fullmatch(challenge):
        add(errors, f"{role} execution challenge differs")
    argv = receipt.get("argv")
    if not isinstance(argv, list) or not all(
        isinstance(item, str) for item in argv
    ):
        add(errors, f"{role} execution argv differs")
        argv = []
    forbidden_argv = {
        "cases.json",
        "python-stdlib.json",
        "node-recursive-descent.json",
    }
    if any(
        any(forbidden in item for forbidden in forbidden_argv)
        for item in argv
    ):
        add(errors, f"{role} execution argv crosses the answer/peer boundary")
    attestation = receipt.get("attestation")
    if not isinstance(attestation, dict):
        add(errors, f"{role} execution attestation is absent")
        return
    result_raw = result_path.read_bytes()
    if not result_raw.endswith(b"\n") or result_raw.count(b"\n") != 1:
        add(errors, f"{role} result file framing differs")
        return
    result_line = result_raw[:-1]
    attestation_line = compact_json(attestation)
    stdout = attestation_line + b"\n" + result_line + b"\n"
    process_observation = receipt.get("process_observation")
    expected_process = {
        "exit_code": 0,
        "stdout_binding": {
            "raw_sha256": sha256(stdout),
            "byte_count": len(stdout),
            "line_count": 2,
            "framing": "compact_attestation_line_then_compact_result_line",
        },
        "stderr_binding": {
            "raw_sha256": sha256(b""),
            "byte_count": 0,
        },
        "attestation_line_binding": {
            "raw_sha256": sha256(attestation_line),
            "byte_count": len(attestation_line),
            "stdout_line": 1,
        },
        "result_line_binding": {
            "raw_sha256": sha256(result_line),
            "byte_count": len(result_line),
            "stdout_line": 2,
        },
    }
    if not json_exact(process_observation, expected_process):
        add(errors, f"{role} execution stdout/stderr binding differs")
    executable = receipt.get("executable_observation")
    if not executable_observation_shape_is_exact(executable) or (
        not json_exact(
            executable.get("pre_execution_binding"),
            executable.get("post_execution_binding"),
        )
        or not json_exact(
            executable.get("pre_execution_binding"),
            {
            "raw_sha256": executable.get("raw_sha256"),
            "byte_count": executable.get("byte_count"),
            },
        )
        or not isinstance(executable.get("invocation_path"), str)
        or not isinstance(executable.get("resolved_path"), str)
        or not SHA256_RE.fullmatch(str(executable.get("raw_sha256")))
        or type(executable.get("byte_count")) is not int
    ):
        add(errors, f"{role} executable pre/post binding differs")
        return
    runner_binding = attestation.get("runner_binding")
    historical_runner_path = (
        runner_binding.get("repository_path")
        if isinstance(runner_binding, dict)
        else None
    )
    expected_runner_suffix = "/" + (
        PYTHON_RUNNER if role == "python" else NODE_RUNNER
    ).relative_to(ROOT).as_posix()
    expected_argv = [
        executable["invocation_path"],
        *(["-I", "-S", "-B"] if role == "python" else ["--disable-proto=throw"]),
        historical_runner_path,
        *child_arguments(role, challenge),
    ]
    if (
        not isinstance(historical_runner_path, str)
        or not Path(historical_runner_path).is_absolute()
        or not historical_runner_path.endswith(expected_runner_suffix)
        or argv != expected_argv
    ):
        add(errors, f"{role} execution argv inventory differs")
    expected_result_binding = {
        key: value
        for key, value in expected_process["result_line_binding"].items()
        if key != "stdout_line"
    }
    if not child_attestation_shape_is_exact(attestation) or (
        attestation.get("schema_version") != "0.1.0"
        or attestation.get("artifact_class")
        != "prq_002c_child_execution_attestation"
        or attestation.get("suite_id") != SUITE_ID
        or attestation.get("implementation_id") != expected_id
        or attestation.get("challenge") != challenge
        or attestation.get("argv") != argv
        or attestation.get("network_access_requested") is not False
        or attestation.get("private_expectations_received") is not False
        or attestation.get("peer_source_received") is not False
        or attestation.get("peer_result_received") is not False
        or attestation.get("product_identity_computed") is not False
        or not json_exact(
            attestation.get("result_line_binding"),
            expected_result_binding,
        )
    ):
        add(errors, f"{role} child execution attestation differs")
    runtime = attestation.get("runtime")
    expected_runtime_binding = {
        "repository_path": executable["resolved_path"],
        "raw_sha256": executable["raw_sha256"],
        "byte_count": executable["byte_count"],
    }
    if not json_exact(
        runtime,
        {
            "family": expected_runtime_family,
            "version": expected_runtime_version,
            "executable": expected_runtime_binding,
        },
    ):
        add(errors, f"{role} attested runtime differs")
    expected_source = PYTHON_SOURCE if role == "python" else NODE_SOURCE
    expected_runner = PYTHON_RUNNER if role == "python" else NODE_RUNNER
    if not json_exact(
        attestation.get("source_manifest_binding"),
        repository_binding(expected_source),
    ):
        add(errors, f"{role} attested source manifest differs")
    current_runner_binding = repository_binding(expected_runner)
    if not json_exact(
        runner_binding,
        {
            "repository_path": historical_runner_path,
            "raw_sha256": current_runner_binding["raw_sha256"],
            "byte_count": current_runner_binding["byte_count"],
        },
    ):
        add(errors, f"{role} attested runner bytes differ")
    if (
        not json_exact(
            attestation.get("input_manifest_binding"),
            repository_binding(INPUT_MANIFEST),
        )
        or not json_exact(
            attestation.get("vector_set_binding"),
            repository_binding(VECTORS),
        )
        or not json_exact(
            attestation.get("token_contract_binding"),
            repository_binding(CONTRACT),
        )
    ):
        add(errors, f"{role} attested normative input binding differs")
    portable = receipt.get("portable_recomputation_contract")
    if not json_exact(
        portable,
        {
            "validator_path": (
                "scripts/validate_product_identity_raw_number_typing.py"
            ),
            "mode_flag": "--recompute-all",
            "selected_runtime_version_required": True,
            "runtime_executable_pre_and_post_binding_required": True,
            "fresh_challenge_required": True,
            "complete_result_line_equality_required": True,
            "historical_executable_path_identity_required": False,
            "historical_executable_byte_identity_required": False,
        },
    ):
        add(errors, f"{role} portable recomputation contract differs")


def state_guard_codes(state: dict[str, Any]) -> set[str]:
    guards: set[str] = set()
    if not json_exact(state["manifest"], expected_suite_manifest()):
        guards.add("suite_manifest_exact_json_boundary")
    if not private_expectation_shape_is_exact(state["cases"]):
        guards.add("private_expectation_shape_boundary")
    if any(
        not private_expectation_row_is_well_typed(row)
        for row in state["cases"].get("cases", [])
    ):
        guards.add("private_expectation_type_boundary")
    if not json_exact(
        state["dependency_controls"],
        expected_dependency_controls(),
    ):
        guards.add("dependency_control_exact_json_boundary")
    if not json_exact(
        state["input_manifest"],
        expected_input_manifest(),
    ):
        guards.add("answer_free_input_manifest")
    vectors = state["vectors"]
    vector_rows = vectors.get("vectors", [])
    expected_root = {
        "schema_version",
        "artifact_class",
        "vector_set_id",
        "status",
        "answer_free",
        "opaque_vector_ids",
        "expected_outcomes_present",
        "decoded_input_bindings_present",
        "vector_count",
        "vectors",
    }
    if set(vectors) != expected_root or any(
        not isinstance(row, dict) or set(row) != VECTOR_KEYS
        for row in vector_rows
    ):
        guards.add("answer_free_boundary")
    if any(
        not isinstance(row, dict)
        or not isinstance(row.get("vector_id"), str)
        or not OPAQUE_ID_RE.fullmatch(row["vector_id"])
        for row in vector_rows
    ):
        guards.add("opaque_vector_id_boundary")
    for row in vector_rows:
        if not isinstance(row, dict):
            continue
        try:
            raw = base64.b64decode(row.get("input_base64", ""), validate=True)
        except (ValueError, TypeError):
            guards.add("decoded_input_binding")
            continue
        if (
            row.get("decoded_raw_sha256") != sha256(raw)
            or row.get("decoded_byte_count") != len(raw)
        ):
            guards.add("decoded_input_binding")

    cases = state["cases"].get("cases", [])
    expected_by_id = {
        case.get("vector_id"): case
        for case in cases
        if isinstance(case, dict)
    }
    expected_ids = [
        row.get("vector_id") for row in vector_rows if isinstance(row, dict)
    ]
    for role, result in state["results"].items():
        projection = result.get("projection", {})
        rows = projection.get("results", [])
        observed_ids = [
            row.get("vector_id") for row in rows if isinstance(row, dict)
        ]
        if len(rows) != len(expected_ids):
            guards.add("complete_result_inventory")
        if observed_ids != expected_ids:
            guards.add("ordered_result_inventory")
        for row in rows:
            if not isinstance(row, dict):
                guards.add("classified_result_boundary")
                continue
            if set(row) != RESULT_ROW_KEYS:
                guards.add("staged_projection_boundary")
            if row.get("final_disposition") not in {"accepted", "refused"}:
                guards.add("classified_result_boundary")
            case = expected_by_id.get(row.get("vector_id"))
            if not isinstance(case, dict):
                continue
            final_mismatch = (
                row.get("final_disposition")
                != case.get("expected_final_disposition")
                or row.get("final_code") != case.get("expected_final_code")
            )
            if final_mismatch:
                guards.add("private_expectation_boundary")
            stage_map = {
                "lexical_disposition": "expected_lexical_disposition",
                "position_rule": "expected_position_rule",
                "raw_number_token": "expected_raw_number_token",
                "raw_number_token_byte_count": (
                    "expected_raw_number_token_byte_count"
                ),
                "token_class": "expected_token_class",
                "binary64_conversion_class": (
                    "expected_binary64_conversion_class"
                ),
                "integer_position_disposition": (
                    "expected_integer_position_disposition"
                ),
                "integer_decimal": "expected_integer_decimal",
            }
            if any(
                not json_exact(row.get(actual), case.get(expected))
                for actual, expected in stage_map.items()
            ):
                guards.add("staged_projection_boundary")
        implementation = result.get("implementation", {})
        expected_impl = expected_implementation(role)
        if implementation.get("runtime_version") != expected_impl[
            "runtime_version"
        ]:
            guards.add("runtime_binding_boundary")
        if (
            implementation.get("source_manifest_binding")
            != expected_impl["source_manifest_binding"]
        ):
            guards.add("source_binding_boundary")
        projection_value = result.get("projection")
        if isinstance(projection_value, dict):
            expected_causal = expected_causal_binding(
                expected_impl, projection_value
            )
            if result.get("implementation_causal_binding") != expected_causal:
                guards.add("implementation_causal_binding_consistency")
        claim = projection.get("claim_boundary", {})
        if any(
            claim.get(key) is not False
            for key in (
                "product_identity_computed",
                "profile_issued",
                "gate_a_complete",
                "runtime_authorized",
                "publication_authorized",
            )
        ):
            guards.add("authority_boundary")
        if any(
            claim.get(key) is not False
            for key in (
                "generic_schema_path_evaluation_proved",
                "number_position_semantics_complete",
                "successor_profile_conformance_complete",
            )
        ):
            guards.add("claim_scope_boundary")

    python_text = state["source_texts"]["python"]
    node_text = state["source_texts"]["node"]
    if source_import_boundary_findings(python_text, node_text):
        guards.add("source_import_boundary")
    if (
        "node/runner.mjs" in python_text
        or NODE_ID in python_text
    ):
        guards.add("source_separation_boundary")
    if (
        "results/python-stdlib.json" in node_text
        or PYTHON_ID in node_text
    ):
        guards.add("peer_result_boundary")

    for role, source in state["sources"].items():
        expected_files = (
            [("runner", PYTHON_RUNNER), ("dependency_lock", PYTHON_LOCK)]
            if role == "python"
            else [
                ("runner", NODE_RUNNER),
                ("package_manifest", NODE_PACKAGE),
                ("package_lock", NODE_LOCK),
            ]
        )
        expected_rows = [
            repository_binding(path, role=file_role)
            for file_role, path in expected_files
        ]
        if source.get("source_files") != expected_rows:
            guards.add("source_binding_boundary")

    receipts = state["receipts"]
    python_challenge = receipts["python"].get("challenge")
    node_challenge = receipts["node"].get("challenge")
    if python_challenge == node_challenge:
        guards.add("fresh_challenge_boundary")
    for role, receipt in receipts.items():
        if not observed_at_output_close_is_exact(
            receipt.get("observed_at_output_close_utc")
        ):
            guards.add("execution_receipt_identity_boundary")
        process_observation = receipt.get("process_observation", {})
        attestation = receipt.get("attestation")
        result_path = PYTHON_RESULT if role == "python" else NODE_RESULT
        if (
            not child_attestation_shape_is_exact(attestation)
            or attestation.get("schema_version") != "0.1.0"
        ):
            guards.add("attestation_shape_boundary")
        if isinstance(attestation, dict) and result_path.is_file():
            stdout = (
                compact_json(attestation)
                + b"\n"
                + result_path.read_bytes()
            )
            binding_value = process_observation.get("stdout_binding", {})
            if (
                binding_value.get("raw_sha256") != sha256(stdout)
                or binding_value.get("byte_count") != len(stdout)
            ):
                guards.add("stdout_binding_boundary")

    comparison = state["comparison"]
    if (
        comparison.get("suite_manifest_binding")
        != repository_binding(MANIFEST)
        or comparison.get("comparator_expectation_binding")
        != repository_binding(CASES)
        or comparison.get(
            "bounded_suite_gate_known_bad_self_test_complete"
        )
        is not True
    ):
        guards.add("comparison_context_binding")
    if comparison.get("execution_receipt_bindings") != [
        repository_binding(PYTHON_EXECUTION, role="python"),
        repository_binding(NODE_EXECUTION, role="node"),
    ]:
        guards.add("execution_receipt_binding")
    if comparison.get("validator_binding") != repository_binding(VALIDATOR):
        guards.add("validator_binding")
    if (
        comparison.get("organizational_independence_proven") is not False
        or comparison.get("independent_host_reproduction_complete") is not False
    ):
        guards.add("independence_boundary")
    comparison_claim = comparison.get("claim_boundary", {})
    if any(
        comparison_claim.get(key) is not False
        for key in (
            "generic_schema_path_evaluation_proved",
            "number_position_semantics_complete",
            "unique_instance_pointer_retention_proved",
            "dynamic_path_discovery_excluded",
            "historical_process_independently_witnessed",
            "successor_profile_conformance_complete",
        )
    ):
        guards.add("claim_scope_boundary")
    if not json_exact(
        comparison.get("measured_census"),
        {
            "vector_count": 61,
            "accepted_count": 9,
            "refused_count": 52,
            "unclassified_error_count": 0,
            "source_separated_implementation_count": 2,
            "gate_known_bad_count": len(EXPECTED_GATE_ROWS),
        },
    ):
        guards.add("measured_census_boundary")
    python_projection = state["results"]["python"].get("projection")
    node_projection = state["results"]["node"].get("projection")
    if not json_exact(python_projection, node_projection):
        guards.add("complete_projection_comparison")
    elif isinstance(python_projection, dict):
        projection_raw = compact_json(python_projection)
        if (
            comparison.get("projection_raw_sha256") != sha256(projection_raw)
            or comparison.get("projection_byte_count") != len(projection_raw)
            or comparison.get("complete_ordered_projection_equal") is not True
        ):
            guards.add("complete_projection_comparison")
    return guards


def mutate_state(base: dict[str, Any], mutation_id: str) -> dict[str, Any]:
    state = copy.deepcopy(base)
    results = state["results"]

    if mutation_id == "answer-field-leakage":
        state["vectors"]["vectors"][0]["expected_outcome"] = "accepted"
    elif mutation_id == "outcome-bearing-id":
        state["vectors"]["vectors"][0]["vector_id"] = "accept-zero"
    elif mutation_id == "decoded-byte-substitution":
        state["vectors"]["vectors"][0]["input_base64"] = base64.b64encode(
            b'{"frame_id":"changed","integer_value":0}'
        ).decode("ascii")
    elif mutation_id == "gate-a-claim":
        results["python"]["projection"]["claim_boundary"][
            "gate_a_complete"
        ] = True
    elif mutation_id == "runtime-authority-claim":
        results["node"]["projection"]["claim_boundary"][
            "runtime_authorized"
        ] = True
    elif mutation_id == "publication-authority-claim":
        results["python"]["projection"]["claim_boundary"][
            "publication_authorized"
        ] = True
    elif mutation_id == "generic-schema-path-claim":
        results["node"]["projection"]["claim_boundary"][
            "generic_schema_path_evaluation_proved"
        ] = True
    elif mutation_id == "number-position-complete-claim":
        results["python"]["projection"]["claim_boundary"][
            "number_position_semantics_complete"
        ] = True
    elif mutation_id == "independence-claims":
        state["comparison"]["organizational_independence_proven"] = True
        state["comparison"]["independent_host_reproduction_complete"] = True
    elif mutation_id == "fresh-attestation-claim-injection":
        attestation = state["receipts"]["python"]["attestation"]
        attestation["runtime"]["profile_issued"] = True
        attestation_line = compact_json(attestation)
        stdout = (
            attestation_line
            + b"\n"
            + PYTHON_RESULT.read_bytes()
        )
        process = state["receipts"]["python"]["process_observation"]
        binding = process["stdout_binding"]
        binding["raw_sha256"] = sha256(stdout)
        binding["byte_count"] = len(stdout)
        line_binding = process["attestation_line_binding"]
        line_binding["raw_sha256"] = sha256(attestation_line)
        line_binding["byte_count"] = len(attestation_line)
    elif mutation_id == "expectation-root-authority-injection":
        state["cases"]["gate_a_complete"] = True
    elif mutation_id == "suite-manifest-json-type-alias":
        manifest = state["manifest"]
        manifest["census"]["accepted_count"] = 9.0
        manifest["implementation_contract"][
            "fresh_challenge_self_attestation_required"
        ] = 1
        manifest["claim_boundary"]["gate_a_complete"] = 0
    elif mutation_id == "dependency-control-authority-injection":
        state["dependency_controls"]["python"]["runtime_authorized"] = True
    elif mutation_id == "case-stage-json-type-alias":
        state["cases"]["cases"][0][
            "expected_raw_number_token_byte_count"
        ] = True
    elif mutation_id == "node-single-quoted-network-import":
        state["source_texts"]["node"] += (
            "\nimport * as http from 'node:http';\n"
        )
    elif mutation_id == "node-alternate-module-acquisition":
        state["source_texts"]["node"] += (
            '\nimport "node:net";\n'
            'await import("node:https");\n'
            'import * as dns from "dns";\n'
            'process.getBuiltinModule("http");\n'
            'fetch("https://invalid.example");\n'
        )
    elif mutation_id == "python-dynamic-network-import":
        state["source_texts"]["python"] += '\n__import__("socket")\n'
    elif mutation_id == "invalid-observation-timestamp":
        state["receipts"]["python"][
            "observed_at_output_close_utc"
        ] = "2026-07-28T99:99:99.999999Z"
    elif mutation_id == "peer-source-import":
        state["source_texts"]["python"] += "\n# node/runner.mjs\n"
    elif mutation_id == "peer-result-import":
        state["source_texts"]["node"] += (
            "\n// results/python-stdlib.json\n"
        )
    elif mutation_id == "stale-implementation-causal-binding":
        copied = copy.deepcopy(results["python"])
        copied["implementation"] = copy.deepcopy(
            expected_implementation("node")
        )
        results["node"] = copied
    elif mutation_id == "missing-result":
        results["python"]["projection"]["results"].pop()
    elif mutation_id == "extra-result":
        results["node"]["projection"]["results"].append(
            copy.deepcopy(results["node"]["projection"]["results"][0])
        )
    elif mutation_id == "reordered-result":
        rows = results["python"]["projection"]["results"]
        rows[0], rows[1] = rows[1], rows[0]
    elif mutation_id == "outcome-substitution":
        results["node"]["projection"]["results"][0][
            "final_disposition"
        ] = "refused"
    elif mutation_id == "reason-substitution":
        results["python"]["projection"]["results"][9][
            "final_code"
        ] = "ODEYA_SCHEMA_TYPE"
    elif mutation_id == "stage-substitution":
        results["node"]["projection"]["results"][0][
            "binary64_conversion_class"
        ] = "finite_nonzero"
    elif mutation_id == "source-manifest-drift":
        state["sources"]["python"]["source_files"][0][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "runtime-version-drift":
        results["node"]["implementation"]["runtime_version"] = "24.17.0"
    elif mutation_id == "challenge-replay":
        state["receipts"]["node"]["challenge"] = state["receipts"]["python"][
            "challenge"
        ]
    elif mutation_id == "stdout-substitution":
        state["receipts"]["python"]["process_observation"]["stdout_binding"][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "comparison-substitution":
        state["comparison"]["projection_raw_sha256"] = "sha256:" + "0" * 64
    elif mutation_id == "unclassified-crash":
        results["node"]["projection"]["results"][1][
            "final_disposition"
        ] = "crash"
    elif mutation_id == "product-identity-claim":
        results["python"]["projection"]["claim_boundary"][
            "product_identity_computed"
        ] = True
    elif mutation_id == "profile-conformance-claim":
        results["node"]["projection"]["claim_boundary"][
            "successor_profile_conformance_complete"
        ] = True
    elif mutation_id == "issuance-claim":
        results["python"]["projection"]["claim_boundary"][
            "profile_issued"
        ] = True
    elif mutation_id == "input-manifest-expectation-path-leak":
        state["input_manifest"][
            "private_expectations_repository_path"
        ] = "tests/product-identity-raw-number-typing/cases.json"
    elif mutation_id == "suite-manifest-binding-substitution":
        state["comparison"]["suite_manifest_binding"][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "comparator-expectation-binding-substitution":
        state["comparison"]["comparator_expectation_binding"][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "execution-receipt-binding-substitution":
        state["comparison"]["execution_receipt_bindings"][0][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "validator-binding-substitution":
        state["comparison"]["validator_binding"][
            "raw_sha256"
        ] = "sha256:" + "0" * 64
    elif mutation_id == "measured-census-substitution":
        state["comparison"]["measured_census"][
            "unclassified_error_count"
        ] = 1
    else:
        raise ValueError(f"unknown gate mutation {mutation_id}")
    return state


def validate_gate_self_tests(
    errors: list[str],
    state: dict[str, Any],
    cases_document: dict[str, Any],
) -> None:
    actual_guards = state_guard_codes(state)
    if actual_guards:
        add(
            errors,
            "baseline gate control fired: " + ", ".join(sorted(actual_guards)),
        )
    rows = cases_document.get("gate_known_bads", [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        mutation_id = row.get("id")
        expected_guard = row.get("expected_guard")
        if not isinstance(mutation_id, str) or not isinstance(
            expected_guard, str
        ):
            continue
        if mutation_id == "strict-json-nonfinite-number":
            observed = (
                {"strict_json_parser_boundary"}
                if strict_json_known_bads_fire()
                else set()
            )
        elif mutation_id == "suite-inventory-hidden-file":
            observed = inventory_guard_codes(
                EXPECTED_SUITE_FILES
                | {"node_modules/evil/index.js"},
                set(),
            )
        else:
            mutated = mutate_state(state, mutation_id)
            observed = state_guard_codes(mutated)
        if expected_guard not in observed:
            add(
                errors,
                f"gate known-bad {mutation_id} did not fire "
                f"{expected_guard}; observed {sorted(observed)}",
            )


def executable_observation(path: Path) -> dict[str, Any]:
    invocation = path.absolute()
    resolved = invocation.resolve(strict=True)
    bound = file_binding(resolved)
    if bound is None:
        raise ValueError(f"cannot bind executable {resolved}")
    return {
        "invocation_path": invocation.as_posix(),
        "resolved_path": resolved.as_posix(),
        **bound,
    }


def child_arguments(role: str, challenge: str) -> list[str]:
    common = [
        "--vectors",
        VECTORS.relative_to(ROOT).as_posix(),
        "--manifest",
        INPUT_MANIFEST.relative_to(ROOT).as_posix(),
        "--contract",
        CONTRACT.relative_to(ROOT).as_posix(),
        "--contract-schema",
        CONTRACT_SCHEMA.relative_to(ROOT).as_posix(),
        "--profile-core",
        PROFILE_CORE.relative_to(ROOT).as_posix(),
        "--profile-evidence",
        PROFILE_EVIDENCE.relative_to(ROOT).as_posix(),
        "--source-manifest",
        (
            PYTHON_SOURCE if role == "python" else NODE_SOURCE
        ).relative_to(ROOT).as_posix(),
        "--attestation-challenge",
        challenge,
        "--emit-execution-attestation",
    ]
    return common


def validate_fresh_attestation(
    *,
    role: str,
    attestation: dict[str, Any],
    argv: list[str],
    challenge: str,
    executable: dict[str, Any],
    result_line: bytes,
) -> list[str]:
    errors: list[str] = []
    expected_id = PYTHON_ID if role == "python" else NODE_ID
    expected_family = "CPython" if role == "python" else "Node.js"
    expected_version = PYTHON_VERSION if role == "python" else NODE_VERSION
    expected_source = PYTHON_SOURCE if role == "python" else NODE_SOURCE
    expected_runner = PYTHON_RUNNER if role == "python" else NODE_RUNNER
    if (
        not child_attestation_shape_is_exact(attestation)
        or attestation.get("schema_version") != "0.1.0"
        or attestation.get("artifact_class")
        != "prq_002c_child_execution_attestation"
        or attestation.get("suite_id") != SUITE_ID
        or attestation.get("implementation_id") != expected_id
        or attestation.get("challenge") != challenge
        or attestation.get("argv") != argv
    ):
        errors.append(f"{role} fresh attestation identity differs")
    runtime = attestation.get("runtime")
    if not json_exact(
        runtime,
        {
            "family": expected_family,
            "version": expected_version,
            "executable": {
                "repository_path": executable["resolved_path"],
                "raw_sha256": executable["raw_sha256"],
                "byte_count": executable["byte_count"],
            },
        },
    ):
        errors.append(f"{role} fresh runtime attestation differs")
    runner = attestation.get("runner_binding")
    expected_runner_binding = repository_binding(expected_runner)
    if not json_exact(
        runner,
        {
            "repository_path": expected_runner.resolve(strict=True).as_posix(),
            "raw_sha256": expected_runner_binding["raw_sha256"],
            "byte_count": expected_runner_binding["byte_count"],
        },
    ):
        errors.append(f"{role} fresh runner binding differs")
    if (
        not json_exact(
            attestation.get("source_manifest_binding"),
            repository_binding(expected_source),
        )
        or not json_exact(
            attestation.get("input_manifest_binding"),
            repository_binding(INPUT_MANIFEST),
        )
        or not json_exact(
            attestation.get("vector_set_binding"),
            repository_binding(VECTORS),
        )
        or not json_exact(
            attestation.get("token_contract_binding"),
            repository_binding(CONTRACT),
        )
        or not json_exact(
            attestation.get("result_line_binding"),
            {
                "raw_sha256": sha256(result_line),
                "byte_count": len(result_line),
            },
        )
        or attestation.get("network_access_requested") is not False
        or attestation.get("private_expectations_received") is not False
        or attestation.get("peer_source_received") is not False
        or attestation.get("peer_result_received") is not False
        or attestation.get("product_identity_computed") is not False
    ):
        errors.append(f"{role} fresh causal input/nonclaim binding differs")
    return errors


def recompute_role(
    *,
    role: str,
    selected: Path,
    challenge: str,
    retained_result: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        before = executable_observation(selected)
    except (OSError, ValueError) as exc:
        return [f"{role} selected executable cannot be bound: {exc}"]
    if role == "python":
        if selected.resolve(strict=True) != PARENT_EXECUTABLE:
            return [
                "python selected executable must resolve to the "
                "startup-bound checker image"
            ]
        if PARENT_RUNTIME_VERSION != PYTHON_VERSION:
            return [
                f"python checker version differs: {PARENT_RUNTIME_VERSION}"
            ]
        argv = [
            selected.absolute().as_posix(),
            "-I",
            "-S",
            "-B",
            PYTHON_RUNNER.resolve(strict=True).as_posix(),
            *child_arguments(role, challenge),
        ]
    else:
        try:
            installed = subprocess.run(
                ["bash", NODE_INSTALLER.relative_to(ROOT).as_posix()],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return [f"node installer provenance check failed: {exc}"]
        if installed.returncode != 0:
            return ["node installer provenance check returned nonzero"]
        installer_path = Path(installed.stdout.strip())
        try:
            if (
                selected.resolve(strict=True)
                != installer_path.resolve(strict=True)
            ):
                return ["selected Node.js is not the pinned installer product"]
        except OSError as exc:
            return [f"node installer product cannot be resolved: {exc}"]
        version = subprocess.run(
            [selected.absolute().as_posix(), "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if version.returncode != 0 or version.stdout.strip() != f"v{NODE_VERSION}":
            return ["selected Node.js version differs"]
        argv = [
            selected.resolve(strict=True).as_posix(),
            "--disable-proto=throw",
            NODE_RUNNER.resolve(strict=True).as_posix(),
            *child_arguments(role, challenge),
        ]
    environment = {
        "PATH": os.path.dirname(selected.absolute().as_posix()),
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
    }
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            env=environment,
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return [f"{role} fresh child failed to execute: {exc}"]
    try:
        after = executable_observation(selected)
    except (OSError, ValueError) as exc:
        return [f"{role} selected executable post-binding failed: {exc}"]
    if before != after:
        errors.append(f"{role} executable changed during child execution")
    if completed.returncode != 0:
        errors.append(
            f"{role} fresh child returned {completed.returncode}: "
            + completed.stderr.decode("utf-8", "replace")[:500]
        )
        return errors
    if completed.stderr != b"":
        errors.append(f"{role} fresh child emitted stderr")
    if not completed.stdout.endswith(b"\n") or completed.stdout.count(b"\n") != 2:
        errors.append(f"{role} fresh child stdout framing differs")
        return errors
    attestation_line, result_line, terminal = completed.stdout.split(b"\n")
    if terminal != b"":
        errors.append(f"{role} fresh child terminal framing differs")
        return errors
    try:
        attestation = loads_strict(attestation_line)
        result = loads_strict(result_line)
    except (UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        errors.append(f"{role} fresh child JSON is invalid: {exc}")
        return errors
    if not isinstance(attestation, dict) or not isinstance(result, dict):
        errors.append(f"{role} fresh child lines are not objects")
        return errors
    errors.extend(
        validate_fresh_attestation(
            role=role,
            attestation=attestation,
            argv=argv,
            challenge=challenge,
            executable=before,
            result_line=result_line,
        )
    )
    retained = retained_result.read_bytes()
    if retained != result_line + b"\n":
        errors.append(f"{role} fresh result differs byte-for-byte from retained")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recompute-all", action="store_true")
    parser.add_argument("--python-executable", type=Path)
    parser.add_argument("--node-executable", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    inventory = suite_inventory()
    symlinks = suite_symlinks()
    if inventory_guard_codes(inventory, symlinks):
        missing = sorted(EXPECTED_SUITE_FILES - inventory)
        extra = sorted(inventory - EXPECTED_SUITE_FILES)
        add(
            errors,
            "raw-number suite inventory differs; "
            f"missing={missing}, extra={extra}, symlinks={sorted(symlinks)}",
        )
    validate_strict_json_loader(errors)
    required = [
        CONTRACT_SCHEMA,
        CONTRACT,
        PROFILE_CORE,
        PROFILE_EVIDENCE,
        MANIFEST,
        INPUT_MANIFEST,
        VECTORS,
        CASES,
        PYTHON_RUNNER,
        PYTHON_LOCK,
        PYTHON_SOURCE,
        NODE_RUNNER,
        NODE_PACKAGE,
        NODE_LOCK,
        NODE_SOURCE,
        PYTHON_RESULT,
        NODE_RESULT,
        PYTHON_EXECUTION,
        NODE_EXECUTION,
        COMPARISON,
    ]
    for path in required:
        if not path.is_file() or path.is_symlink():
            add(errors, f"required raw-number artifact is absent: {path.relative_to(ROOT)}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    try:
        contract = load(CONTRACT)
        profile_evidence = load(PROFILE_EVIDENCE)
        manifest = load(MANIFEST)
        input_manifest = load(INPUT_MANIFEST)
        vectors = load(VECTORS)
        cases = load(CASES)
        python_lock = load(PYTHON_LOCK)
        node_package = load(NODE_PACKAGE)
        node_lock = load(NODE_LOCK)
        python_source = load(PYTHON_SOURCE)
        node_source = load(NODE_SOURCE)
        python_result = load(PYTHON_RESULT)
        node_result = load(NODE_RESULT)
        python_execution = load(PYTHON_EXECUTION)
        node_execution = load(NODE_EXECUTION)
        comparison = load(COMPARISON)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        print(f"raw-number evidence could not be loaded: {exc}", file=sys.stderr)
        return 1

    validate_contract(errors, contract)
    validate_profile_nonclaims(errors, profile_evidence)
    validate_manifest(errors, manifest)
    validate_input_manifest(errors, input_manifest)
    validate_dependency_controls(
        errors,
        python_lock=python_lock,
        node_package=node_package,
        node_lock=node_lock,
    )
    validate_source_manifest(
        errors,
        role="python",
        document=python_source,
        expected_id=PYTHON_ID,
        expected_runtime=PYTHON_VERSION,
        expected_strategy=(
            "stdlib_json_raw_pairs_deferred_restriction_classification"
        ),
        expected_files=[
            ("runner", PYTHON_RUNNER),
            ("dependency_lock", PYTHON_LOCK),
        ],
    )
    validate_source_manifest(
        errors,
        role="node",
        document=node_source,
        expected_id=NODE_ID,
        expected_runtime=NODE_VERSION,
        expected_strategy=(
            "recursive_descent_deferred_restriction_classification"
        ),
        expected_files=[
            ("runner", NODE_RUNNER),
            ("package_manifest", NODE_PACKAGE),
            ("package_lock", NODE_LOCK),
        ],
    )
    try:
        python_text = PYTHON_RUNNER.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        add(errors, f"python observer source cannot be decoded as UTF-8: {exc}")
        python_text = ""
    try:
        node_text = NODE_RUNNER.read_text("utf-8")
    except (OSError, UnicodeError) as exc:
        add(errors, f"node observer source cannot be decoded as UTF-8: {exc}")
        node_text = ""
    validate_source_separation(errors, python_text, node_text)
    vector_rows, case_rows = validate_vectors_and_cases(
        errors, vectors, cases
    )
    projection: dict[str, Any] = {}
    if len(vector_rows) == len(case_rows) == 61:
        projection = expected_projection(vector_rows, case_rows)
        validate_result(
            errors,
            role="python",
            document=python_result,
            path=PYTHON_RESULT,
            projection=projection,
        )
        validate_result(
            errors,
            role="node",
            document=node_result,
            path=NODE_RESULT,
            projection=projection,
        )
    expected_comparison_value = expected_comparison(
        python_result, node_result
    )
    if not json_exact(comparison, expected_comparison_value):
        add(errors, "complete retained projection comparison differs")
    validate_execution_receipt(
        errors,
        role="python",
        receipt=python_execution,
        result_path=PYTHON_RESULT,
        expected_id=PYTHON_ID,
        expected_runtime_family="CPython",
        expected_runtime_version=PYTHON_VERSION,
    )
    validate_execution_receipt(
        errors,
        role="node",
        receipt=node_execution,
        result_path=NODE_RESULT,
        expected_id=NODE_ID,
        expected_runtime_family="Node.js",
        expected_runtime_version=NODE_VERSION,
    )
    state = {
        "manifest": manifest,
        "input_manifest": input_manifest,
        "vectors": vectors,
        "cases": cases,
        "dependency_controls": {
            "python": python_lock,
            "node_package": node_package,
            "node_lock": node_lock,
        },
        "sources": {
            "python": python_source,
            "node": node_source,
        },
        "source_texts": {
            "python": python_text,
            "node": node_text,
        },
        "results": {
            "python": python_result,
            "node": node_result,
        },
        "receipts": {
            "python": python_execution,
            "node": node_execution,
        },
        "comparison": comparison,
    }
    validate_gate_self_tests(errors, state, cases)

    if args.recompute_all:
        if args.python_executable is None or args.node_executable is None:
            add(
                errors,
                "--recompute-all requires --python-executable and --node-executable",
            )
        else:
            python_challenge = "challenge-v1:" + secrets.token_hex(32)
            node_challenge = "challenge-v1:" + secrets.token_hex(32)
            if python_challenge == node_challenge or {
                python_challenge,
                node_challenge,
            } & {
                python_execution.get("challenge"),
                node_execution.get("challenge"),
            }:
                add(errors, "fresh recomputation challenge collision")
            else:
                errors.extend(
                    recompute_role(
                        role="python",
                        selected=args.python_executable,
                        challenge=python_challenge,
                        retained_result=PYTHON_RESULT,
                    )
                )
                errors.extend(
                    recompute_role(
                        role="node",
                        selected=args.node_executable,
                        challenge=node_challenge,
                        retained_result=NODE_RESULT,
                    )
                )
    elif args.python_executable is not None or args.node_executable is not None:
        add(errors, "runtime selectors require --recompute-all")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(
            f"raw-number observation validation failed with {len(errors)} finding(s)",
            file=sys.stderr,
        )
        return 1
    print(
        "raw-number observation checked: 61 opaque answer-free vectors "
        "(9 accepted, 52 refused); 2 source-separated staged results; "
        f"{len(EXPECTED_GATE_ROWS)} gate known-bads; exact projection agreement; "
        "odeya-jcs-0.2 remains immutable, unissued, and blocked from "
        "conformance and issuance"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
