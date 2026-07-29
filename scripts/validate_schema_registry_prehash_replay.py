#!/usr/bin/env python3
"""Validate the bounded non-product PRQ-002D prehash registry replay.

The default path validates retained evidence without executing either child.
``--recompute-all`` regenerates the answer-free vectors and executes the exact
selected CPython and Node.js observers. A pass proves only the declared
synthetic two-member replay proposition. It is not profile conformance,
product identity, admission, PRQ-002 closure, Gate A acceptance, runtime
authority, or publication authority.
"""

from __future__ import annotations

import argparse
import ast
import base64
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_schema_registry_prehash_replay.py"
SUITE = ROOT / "tests/schema-registry-prehash-replay"
CONTRACT_SCHEMA = (
    ROOT / "architecture/prq-002d-schema-registry-prehash-contract.schema.json"
)
CONTRACT = (
    ROOT
    / "architecture/prq-002d-schema-registry-prehash-contract-v1-candidate.json"
)
MANIFEST = SUITE / "manifest.json"
INPUT_MANIFEST = SUITE / "input-manifest.json"
VECTORS = SUITE / "vectors.json"
CASES = SUITE / "cases.json"
GENERATOR = SUITE / "authoring/generate_vectors.py"
SAFE_BUNDLE = SUITE / "fixtures/safe-bundle.json"
RESOURCE_1 = SUITE / "fixtures/resources/resource-001.schema.json"
RESOURCE_2 = SUITE / "fixtures/resources/resource-002.schema.json"
PROBE_1 = SUITE / "fixtures/probes/probe-001.valid.json"
PROBE_2 = SUITE / "fixtures/probes/probe-002.valid.json"
PYTHON_RUNNER = SUITE / "python/runner.py"
PYTHON_LOCK = SUITE / "python/dependency-lock.json"
PYTHON_SOURCE = SUITE / "python/source-manifest.json"
NODE_RUNNER = SUITE / "node/runner.mjs"
NODE_PACKAGE = SUITE / "node/package.json"
NODE_LOCK = SUITE / "node/package-lock.json"
NODE_SOURCE = SUITE / "node/source-manifest.json"
PYTHON_RESULT = SUITE / "results/python-jsonschema.json"
NODE_RESULT = SUITE / "results/node-ajv2020.json"
PYTHON_EXECUTION = SUITE / "results/python-execution-receipt.json"
NODE_EXECUTION = SUITE / "results/node-execution-receipt.json"
COMPARISON = SUITE / "results/comparison-receipt.json"
PREDECESSOR_DECISION = (
    ROOT
    / "docs/decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md"
)
PREDECESSOR_COMPARISON = (
    ROOT
    / "tests/product-identity-raw-number-typing/results/comparison-receipt.json"
)
PYTHON_INSTALLATION_LOCK = (
    ROOT / "tools/repository-release/requirements-architecture.lock"
)
NODE_INSTALLER = ROOT / "scripts/ci/install-node.sh"

SUITE_ID = "prq-002d-schema-registry-prehash-replay.0001"
CONTRACT_ID = (
    "urn:odeya:architecture-test:prq-002d:"
    "schema-registry-prehash-contract:0.1.0"
)
VECTOR_SET_ID = "prq-002d-schema-registry-prehash.synthetic.0001"
PYTHON_ID = "python-jsonschema-closed-resolver.0001"
NODE_ID = "nodejs-ajv2020-closed-resolver.0001"
PYTHON_VERSION = "3.14.2"
NODE_VERSION = "24.18.0"
NPM_VERSION = "11.16.0"
PARENT_EXECUTABLE = Path(sys.executable).resolve()
APPROVED_PYTHON_RUNNER_BINDING = {
    "raw_sha256": (
        "sha256:420cc562516cccd75d45e3c36c183280b8022dd8cb615e110a0a3ecd03597795"
    ),
    "byte_count_decimal": "39609",
}
APPROVED_NODE_RUNNER_BINDING = {
    "raw_sha256": (
        "sha256:ff5f1c13daa4d0aa146096650023494db630a75a9ff584253e6f0093659befdb"
    ),
    "byte_count_decimal": "47694",
}
APPROVED_CONTRACT_SCHEMA_RAW_BINDING = {
    "repository_path": (
        "architecture/prq-002d-schema-registry-prehash-contract.schema.json"
    ),
    "raw_sha256": (
        "sha256:25c708bd6fb9a2192454ea712163a0d3142e046cb04ec55ee4bb99d724cc8516"
    ),
    "byte_count_decimal": "18944",
}
APPROVED_CONTRACT_SCHEMA_SEMANTIC_BINDING = {
    "raw_sha256": (
        "sha256:4f22a5cf059160d86b4418458cbb1282827c83dba118b998504f1e736a8e795e"
    ),
    "byte_count_decimal": "11556",
}
PREDECESSOR = {
    "commit": "d3ec64f3abfc64467c0bc3bfae330d86e2af89b2",
    "tree": "69304534a61a7c5d085d183d847285a181eaabfc",
}
PREDECESSOR_EVIDENCE_BINDINGS = [
    {
        "role": "raw_number_decision",
        "repository_path": (
            "docs/decisions/"
            "0101-require-raw-number-token-provenance-before-profile-conformance.md"
        ),
        "raw_sha256": (
            "sha256:25ee74c285aa994f6af0f633c44de35c041c96efd9e5b2940d06e6ce3dba0cb4"
        ),
        "byte_count_decimal": "10315",
    },
    {
        "role": "raw_number_comparison",
        "repository_path": (
            "tests/product-identity-raw-number-typing/"
            "results/comparison-receipt.json"
        ),
        "raw_sha256": (
            "sha256:7ec936250fd74edfc70289b39f2a72b5f899959c777c49a392bb618460ea38f0"
        ),
        "byte_count_decimal": "3256",
    },
]
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
OPAQUE_ID_RE = re.compile(r"^PH-[0-9]{4}$")

CLAIM_BOUNDARY = {
    "organizational_independence_proven": False,
    "independent_host_reproduction_complete": False,
    "historical_process_independently_witnessed": False,
    "undeclared_filesystem_read_excluded": False,
    "complete_offline_registry_proved": False,
    "product_identity_computed": False,
    "profile_issued": False,
    "gate_a_complete": False,
    "runtime_authorized": False,
    "publication_authorized": False,
}
AUTHORITY_BOUNDARY = {
    "profile_issued": False,
    "profile_conformance_proved": False,
    "product_schema_resource_admitted": False,
    "product_member_constructed": False,
    "product_digest_computed": False,
    "commitment_constructed": False,
    "registry_snapshot_constructed": False,
    "registry_digest_computed": False,
    "engine_contract_root_constructed": False,
    "activation_constructed": False,
    "gate_a_complete": False,
    "runtime_authorized": False,
    "publication_authorized": False,
}
EVALUATION_CONTRACT = {
    "json_dialect": "https://json-schema.org/draft/2020-12/schema",
    "member_key_expression": "schema_id@semantic_version",
    "member_key_pattern": "^[a-z0-9._:@-]+$",
    "ordering": "unsigned_lexicographic_utf8_byte_order",
    "duplicate_member_keys": "reject_before_ordering",
    "declared_member_count_raw_token": "exact_decimal_integer_token_2",
    "resolver_inventory": "exactly_two_preloaded_contract_pinned_resources",
    "resource_preparse_binding": (
        "contract_expected_resource_or_enumerated_semantic_fixture_"
        "override_before_parse"
    ),
    "probe_preparse_binding": (
        "contract_expected_probe_or_enumerated_semantic_fixture_"
        "override_before_parse"
    ),
    "resolver_catalog_ordering": "contract_expected_resource_order",
    "replay_request_ordering": "contract_expected_replay_order",
    "resource_retrieval": (
        "deny_all_network_file_search_environment_and_dynamic_fallback"
    ),
    "source_separated_implementation_count_decimal": "2",
}
RESOURCE_OVERRIDE_VECTOR_IDS = (
    "PH-0021",
    "PH-0022",
    "PH-0023",
    "PH-0024",
    "PH-0025",
    "PH-0026",
    "PH-0027",
    "PH-0028",
    "PH-0052",
    "PH-0055",
    "PH-0057",
    "PH-0064",
    "PH-0065",
)
PROBE_OVERRIDE_VECTOR_IDS = ("PH-0033",)
RESOURCE_OVERRIDE_KEYS = {
    "vector_id",
    "resource_blob_id",
    "resource_raw_sha256",
    "resource_byte_count_decimal",
}
PROBE_OVERRIDE_KEYS = {
    "vector_id",
    "probe_blob_id",
    "probe_raw_sha256",
    "probe_byte_count_decimal",
}

EXPECTED_CODES = (
    "ODEYA_PREHASH_REPLAY_ACCEPTED",
    "ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED",
    "ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED",
    "ODEYA_NUMBER_NEGATIVE_ZERO",
    "ODEYA_PREHASH_COUNT",
    "ODEYA_PREHASH_MEMBER_SHAPE",
    "ODEYA_PREHASH_DUPLICATE_KEY",
    "ODEYA_PREHASH_ORDER",
    "ODEYA_PREHASH_MEMBER_SHAPE",
    "ODEYA_PREHASH_MEMBER_SHAPE",
    "ODEYA_PREHASH_KEY_BODY",
    "ODEYA_PREHASH_RESOURCE_VERSION",
    "ODEYA_PREHASH_RESOURCE_ID",
    "ODEYA_PREHASH_RESOURCE_BYTE_COUNT",
    "ODEYA_PREHASH_RESOURCE_RAW_DIGEST",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_RESOLVER_TARGET",
    "ODEYA_PREHASH_RESOURCE_RAW_DIGEST",
    "ODEYA_PREHASH_RESOURCE_DIALECT",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_ID",
    "ODEYA_PREHASH_RESOURCE_VERSION",
    "ODEYA_PREHASH_RESOLVER_TARGET",
    "ODEYA_PREHASH_RESOLVER_TARGET",
    "ODEYA_PREHASH_REPLAY_REQUEST",
    "ODEYA_PREHASH_REPLAY_REQUEST",
    "ODEYA_PREHASH_REPLAY_VALIDATION",
    "ODEYA_PREHASH_AUTHORITY_BOUNDARY",
    "ODEYA_CONFORMANCE_FRAME_SHAPE",
    "ODEYA_PARSE_DUPLICATE_KEY",
    "ODEYA_PARSE_UTF8",
    "ODEYA_PARSE_BOM",
    "ODEYA_PARSE_SYNTAX",
    "ODEYA_PARSE_UNPAIRED_SURROGATE",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_REPLAY_REQUEST",
    "ODEYA_PREHASH_REPLAY_REQUEST",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_DUPLICATE_KEY",
    "ODEYA_CONFORMANCE_FRAME_SHAPE",
    "ODEYA_CONFORMANCE_FRAME_SHAPE",
    "ODEYA_PREHASH_AUTHORITY_BOUNDARY",
    "ODEYA_PREHASH_AUTHORITY_BOUNDARY",
    "ODEYA_CONFORMANCE_FRAME_SHAPE",
    "ODEYA_PREHASH_RESOURCE_PARSE",
    "ODEYA_PREHASH_RESOLVER_INVENTORY",
    "ODEYA_PREHASH_REPLAY_REQUEST",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_AUTHORITY_BOUNDARY",
    "ODEYA_PREHASH_RESOURCE_PARSE",
    "ODEYA_PARSE_UTF8",
    "ODEYA_PARSE_SYNTAX",
    "ODEYA_PARSE_SYNTAX",
    "ODEYA_PARSE_DUPLICATE_KEY",
    "ODEYA_PREHASH_COUNT",
    "ODEYA_PREHASH_AUTHORITY_BOUNDARY",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PREHASH_RESOURCE_SCHEMA",
    "ODEYA_PARSE_SYNTAX",
    "ODEYA_NUMBER_DOMAIN",
    "ODEYA_CONFORMANCE_FRAME_SHAPE",
)

GATE_KNOWN_BADS = {
    "source-answer-leakage": (
        "name_private_expectation_path_in_source",
        "answer_free_input_boundary",
    ),
    "invocation-answer-leakage": (
        "pass_private_expectation_path_to_child",
        "answer_free_invocation_boundary",
    ),
    "peer-source-import": (
        "name_peer_runner_in_source",
        "source_separation_boundary",
    ),
    "peer-result-import": (
        "name_peer_result_in_source",
        "peer_result_boundary",
    ),
    "network-import": (
        "add_network_module_or_fetch",
        "closed_resolver_source_boundary",
    ),
    "dynamic-network-import": (
        "add_comment_separated_dynamic_network_import",
        "closed_resolver_source_boundary",
    ),
    "node-side-effect-import": (
        "add_node_side_effect_import",
        "source_capability_boundary",
    ),
    "node-comment-separated-require": (
        "add_comment_separated_node_require",
        "source_capability_boundary",
    ),
    "node-variable-require": (
        "add_node_variable_require",
        "source_capability_boundary",
    ),
    "node-comment-separated-import-call": (
        "add_comment_separated_node_import_call",
        "source_capability_boundary",
    ),
    "python-builtins-attribute-import": (
        "add_python_builtins_attribute_import",
        "closed_resolver_source_boundary",
    ),
    "python-builtins-subscript-import": (
        "add_python_builtins_subscript_import",
        "closed_resolver_source_boundary",
    ),
    "python-dynamic-import-alias": (
        "alias_python_dynamic_import",
        "closed_resolver_source_boundary",
    ),
    "python-importlib-dict-import": (
        "add_python_importlib_dict_import",
        "closed_resolver_source_boundary",
    ),
    "python-source-syntax": (
        "make_python_source_unparseable",
        "source_parse_boundary",
    ),
    "runner-newline-byte-substitution": (
        "replace_python_runner_lf_with_crlf",
        "approved_source_binding_boundary",
    ),
    "python-retrieval-deny-removal": (
        "remove_python_retrieval_deny",
        "closed_resolver_source_boundary",
    ),
    "node-strict-resolver-removal": (
        "remove_node_strict_resolver_control",
        "closed_resolver_source_boundary",
    ),
    "source-binding-drift": (
        "replace_runner_digest_in_source_manifest",
        "source_binding_boundary",
    ),
    "dependency-lock-drift": (
        "replace_pinned_dependency_version",
        "dependency_binding_boundary",
    ),
    "dependency-extra-node-package": (
        "add_unlocked_node_package",
        "dependency_binding_boundary",
    ),
    "result-root-authority-injection": (
        "add_authority_field_to_result_root",
        "result_root_shape_boundary",
    ),
    "result-metadata-drift": (
        "replace_result_vector_count",
        "result_metadata_boundary",
    ),
    "result-input-binding-drift": (
        "replace_result_contract_binding",
        "result_input_binding_boundary",
    ),
    "missing-result": (
        "drop_last_observation",
        "complete_result_inventory",
    ),
    "reordered-result": (
        "swap_first_two_observations",
        "ordered_result_inventory",
    ),
    "result-row-authority-injection": (
        "add_authority_field_to_result_row",
        "result_row_shape_boundary",
    ),
    "outcome-substitution": (
        "flip_one_final_code",
        "private_expectation_boundary",
    ),
    "result-bundle-digest-substitution": (
        "replace_result_bundle_raw_sha256",
        "bundle_raw_digest_projection_boundary",
    ),
    "result-bundle-byte-count-substitution": (
        "replace_result_bundle_byte_count_decimal",
        "bundle_byte_count_projection_boundary",
    ),
    "result-raw-count-token-substitution": (
        "replace_result_declared_member_count_raw_token",
        "declared_member_count_raw_token_projection_boundary",
    ),
    "accepted-member-order-substitution": (
        "replace_accepted_member_order",
        "accepted_member_order_projection_boundary",
    ),
    "accepted-replay-binding-substitution": (
        "replace_accepted_replay_binding",
        "accepted_resolved_replay_projection_boundary",
    ),
    "accepted-probe-count-substitution": (
        "replace_accepted_validated_probe_count",
        "validated_probe_count_projection_boundary",
    ),
    "refusal-observation-invention": (
        "invent_refused_observation",
        "refusal_nonobservation_boundary",
    ),
    "malformed-result-oracle-input": (
        "replace_vectors_with_malformed_oracle_input",
        "result_oracle_input_boundary",
    ),
    "comparison-substitution": (
        "replace_projection_digest",
        "complete_projection_comparison",
    ),
    "comparison-boolean-zero-alias": (
        "replace_projection_equal_true_with_zero",
        "complete_projection_comparison",
    ),
    "projection-type-divergence": (
        "replace_node_projection_false_with_zero",
        "source_projection_type_exactness_boundary",
    ),
    "authority-claim": (
        "set_gate_a_complete_true_in_result",
        "claim_scope_boundary",
    ),
    "product-identity-claim": (
        "set_product_identity_computed_true_in_result",
        "claim_scope_boundary",
    ),
    "numeric-zero-claim-alias": (
        "set_gate_a_complete_to_numeric_zero",
        "claim_scope_boundary",
    ),
    "safe-input-substitution": (
        "replace_contract_safe_bundle_digest",
        "independent_safe_input_binding",
    ),
    "predecessor-evidence-substitution": (
        "replace_predecessor_evidence_digest",
        "predecessor_evidence_boundary",
    ),
    "predecessor-git-tree-substitution": (
        "replace_observed_predecessor_tree",
        "predecessor_repository_boundary",
    ),
    "contract-schema-type-confusion": (
        "replace_safe_bundle_digest_with_null",
        "contract_schema_boundary",
    ),
    "contract-schema-root-closedness-removal": (
        "remove_contract_schema_root_closedness",
        "contract_schema_boundary",
    ),
    "contract-schema-nested-closedness-removal": (
        "remove_contract_schema_nested_closedness",
        "contract_schema_boundary",
    ),
    "contract-schema-object-type-array-closedness-bypass": (
        "replace_contract_schema_object_type_with_array_and_remove_closedness",
        "contract_schema_boundary",
    ),
    "contract-schema-object-type-omission-closedness-bypass": (
        "remove_contract_schema_object_type_and_closedness",
        "contract_schema_boundary",
    ),
    "contract-id-substitution": (
        "replace_contract_id",
        "contract_identity_boundary",
    ),
    "forbidden-structured-identity": (
        "add_forbidden_member_digest",
        "forbidden_structured_identity_boundary",
    ),
    "contract-fixture-binding-substitution": (
        "replace_contract_resource_fixture_digest",
        "contract_fixture_binding_boundary",
    ),
    "contract-preparse-resource-override-omission": (
        "remove_contract_resource_override",
        "contract_preparse_binding_boundary",
    ),
    "contract-preparse-override-extra-field": (
        "add_contract_resource_override_field",
        "contract_preparse_binding_boundary",
    ),
    "contract-preparse-resource-override-addition": (
        "add_contract_resource_override",
        "contract_preparse_binding_boundary",
    ),
    "contract-preparse-probe-override-substitution": (
        "replace_contract_probe_override_digest",
        "contract_preparse_binding_boundary",
    ),
    "contract-preparse-vector-byte-divergence": (
        "replace_override_vector_resource_bytes",
        "contract_preparse_binding_boundary",
    ),
    "contract-semantic-identity-alias": (
        "duplicate_contract_resource_id",
        "contract_semantic_boundary",
    ),
    "contract-authority-claim": (
        "set_contract_runtime_authorized_true",
        "contract_authority_boundary",
    ),
    "contract-claim-expansion": (
        "set_contract_gate_a_complete_true",
        "contract_claim_boundary",
    ),
    "contract-root-shape": (
        "replace_contract_with_non_object",
        "contract_shape_boundary",
    ),
    "input-manifest-substitution": (
        "replace_input_manifest_binding",
        "input_manifest_binding_boundary",
    ),
    "cases-authority-injection": (
        "add_authority_field_to_cases_root",
        "private_expectation_shape_boundary",
    ),
    "private-expectation-substitution": (
        "replace_private_expected_code",
        "private_expectation_inventory_boundary",
    ),
    "vector-root-authority-injection": (
        "add_authority_field_to_vector_root",
        "vector_inventory_boundary",
    ),
    "safe-vector-fixture-substitution": (
        "replace_safe_vector_fixture_digest",
        "safe_vector_binding_boundary",
    ),
    "manifest-authority-injection": (
        "add_authority_field_to_suite_manifest",
        "suite_manifest_boundary",
    ),
    "suite-inventory-extra": (
        "add_untracked_suite_file",
        "exact_suite_inventory_boundary",
    ),
    "suite-inventory-symlink": (
        "add_suite_symlink",
        "exact_suite_inventory_boundary",
    ),
    "unclassified-child-crash": (
        "replace_result_with_non_json_process_output",
        "classified_execution_boundary",
    ),
    "execution-receipt-root-shape": (
        "replace_execution_receipt_with_non_object",
        "execution_receipt_root_boundary",
    ),
    "execution-receipt-runtime-injection": (
        "add_execution_runtime_field",
        "execution_runtime_shape_boundary",
    ),
    "execution-receipt-runtime-type-confusion": (
        "replace_execution_runtime_digest_with_null",
        "execution_runtime_shape_boundary",
    ),
    "execution-receipt-stdout-substitution": (
        "replace_execution_stdout_digest",
        "execution_receipt_binding_boundary",
    ),
    "result-framing-substitution": (
        "append_blank_line_to_retained_result",
        "result_framing_boundary",
    ),
    "comparison-receipt-claim-substitution": (
        "set_comparison_organizational_independence_true",
        "comparison_receipt_binding_boundary",
    ),
}

EXPECTED_SUITE_FILES = {
    "README.md",
    "manifest.json",
    "input-manifest.json",
    "vectors.json",
    "cases.json",
    "authoring/generate_vectors.py",
    "fixtures/safe-bundle.json",
    "fixtures/resources/resource-001.schema.json",
    "fixtures/resources/resource-002.schema.json",
    "fixtures/probes/probe-001.valid.json",
    "fixtures/probes/probe-002.valid.json",
    "python/runner.py",
    "python/dependency-lock.json",
    "python/source-manifest.json",
    "node/runner.mjs",
    "node/package.json",
    "node/package-lock.json",
    "node/source-manifest.json",
    "results/python-jsonschema.json",
    "results/node-ajv2020.json",
    "results/python-execution-receipt.json",
    "results/node-execution-receipt.json",
    "results/comparison-receipt.json",
}

RESULT_ROW_KEYS = {
    "sequence_index_decimal",
    "vector_id",
    "bundle_raw_sha256",
    "bundle_byte_count_decimal",
    "declared_member_count_raw_token",
    "final_disposition",
    "final_code",
    "ordered_member_keys",
    "resolved_replay_bindings",
    "validated_probe_count_decimal",
}
RESULT_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "suite_id",
    "implementation_id",
    "vector_set_id",
    "vector_count_decimal",
    "input_bindings",
    "results",
    "claim_boundary",
}
VECTOR_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "vector_set_id",
    "vector_count_decimal",
    "vectors",
}
VECTOR_ROW_KEYS = {
    "sequence_index_decimal",
    "vector_id",
    "files",
}
VECTOR_FILE_KEYS = {
    "blob_id",
    "media_type",
    "raw_sha256",
    "byte_count_decimal",
    "content_base64",
}
CASES_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "expectation_set_id",
    "suite_id",
    "vector_set_id",
    "case_count_decimal",
    "safe_count_decimal",
    "known_bad_count_decimal",
    "cases",
    "gate_known_bads",
}
CASE_ROW_KEYS = {
    "sequence_index_decimal",
    "vector_id",
    "name",
    "kind",
    "expected_disposition",
    "expected_code",
    "intent_errors",
    "expected_errors",
}
GATE_ROW_KEYS = {"id", "mutation", "expected_guard"}
MANIFEST_ROOT_KEYS = {
    "schema_version",
    "artifact_class",
    "suite_id",
    "status",
    "decision_ref",
    "census",
    "retained_paths",
    "claim_boundary",
}
MANIFEST_CENSUS_KEYS = {
    "vector_count_decimal",
    "accepted_count_decimal",
    "refused_count_decimal",
    "source_separated_implementation_count_decimal",
    "gate_known_bad_count_decimal",
}
MANIFEST_PATH_KEYS = {
    "input_manifest",
    "vectors",
    "private_expectations",
    "contract",
    "contract_schema",
    "python_source_manifest",
    "node_source_manifest",
    "python_result",
    "node_result",
    "python_execution_receipt",
    "node_execution_receipt",
    "comparison_receipt",
    "validator",
}


class DuplicateKey(ValueError):
    """One JSON object member occurred more than once."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def load(path: Path, errors: list[str], label: str | None = None) -> Any:
    name = label or path.relative_to(ROOT).as_posix()
    try:
        return json.loads(
            path.read_text("utf-8"),
            object_pairs_hook=strict_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite token {token}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        add(errors, f"{name}: invalid strict JSON: {type(exc).__name__}")
        return None


def raw_binding(data: bytes) -> dict[str, str]:
    return {
        "raw_sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "byte_count_decimal": str(len(data)),
    }


def repository_binding(path: Path) -> dict[str, str]:
    return {
        "repository_path": path.relative_to(ROOT).as_posix(),
        **raw_binding(path.read_bytes()),
    }


def repository_binding_from_raw(path: Path, data: bytes) -> dict[str, str]:
    return {
        "repository_path": path.relative_to(ROOT).as_posix(),
        **raw_binding(data),
    }


def selected_repository_binding(
    path: Path,
    binding_overrides: dict[Path, bytes] | None = None,
) -> dict[str, str]:
    if binding_overrides is not None and path in binding_overrides:
        return repository_binding_from_raw(path, binding_overrides[path])
    return repository_binding(path)


def observe_predecessor_repository() -> dict[str, Any] | None:
    environment = {
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
    }

    def git_bytes(*arguments: str) -> bytes:
        result = subprocess.run(
            ["/usr/bin/git", *arguments],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            timeout=10,
            check=False,
        )
        if result.returncode != 0 or result.stderr:
            raise RuntimeError("Git object observation failed")
        return result.stdout

    try:
        commit = git_bytes(
            "rev-parse",
            "--verify",
            f"{PREDECESSOR['commit']}^{{commit}}",
        ).decode("ascii").strip()
        tree = git_bytes(
            "rev-parse",
            f"{PREDECESSOR['commit']}^{{tree}}",
        ).decode("ascii").strip()
        bindings = []
        for role, path in (
            ("raw_number_decision", PREDECESSOR_DECISION),
            ("raw_number_comparison", PREDECESSOR_COMPARISON),
        ):
            repository_path = path.relative_to(ROOT).as_posix()
            blob = git_bytes(
                "show",
                f"{PREDECESSOR['commit']}:{repository_path}",
            )
            bindings.append(
                {
                    "role": role,
                    "repository_path": repository_path,
                    **raw_binding(blob),
                }
            )
    except (OSError, UnicodeError, subprocess.SubprocessError, RuntimeError):
        return None
    return {
        "checkpoint": {"commit": commit, "tree": tree},
        "bindings": bindings,
    }


def predecessor_repository_guard_codes(observation: Any) -> set[str]:
    return (
        set()
        if isinstance(observation, dict)
        and json_exact(observation.get("checkpoint"), PREDECESSOR)
        and json_exact(
            observation.get("bindings"),
            PREDECESSOR_EVIDENCE_BINDINGS,
        )
        else {"predecessor_repository_boundary"}
    )


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


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def inventory() -> tuple[set[str], set[str]]:
    files: set[str] = set()
    symlinks: set[str] = set()
    for path in SUITE.rglob("*"):
        relative = path.relative_to(SUITE).as_posix()
        if path.is_symlink():
            symlinks.add(relative)
        elif path.is_file() and "node_modules/" not in relative:
            files.add(relative)
    return files, symlinks


def validate_inventory(errors: list[str]) -> None:
    files, symlinks = inventory()
    for guard in sorted(inventory_guard_codes(files, symlinks)):
        add(errors, f"PRQ-002D suite inventory guard fired: {guard}")
    if files != EXPECTED_SUITE_FILES:
        missing = sorted(EXPECTED_SUITE_FILES - files)
        extra = sorted(files - EXPECTED_SUITE_FILES)
        if missing:
            add(errors, f"suite inventory missing: {', '.join(missing)}")
        if extra:
            add(errors, f"suite inventory has untracked paths: {', '.join(extra)}")
    if symlinks:
        add(errors, f"suite inventory contains symlinks: {', '.join(sorted(symlinks))}")


def inventory_guard_codes(files: set[str], symlinks: set[str]) -> set[str]:
    return (
        set()
        if files == EXPECTED_SUITE_FILES and not symlinks
        else {"exact_suite_inventory_boundary"}
    )


def validate_contract(
    errors: list[str],
    contract_schema: Any,
    contract: Any,
) -> None:
    if not isinstance(contract_schema, dict) or not isinstance(contract, dict):
        return
    for guard in sorted(
        contract_schema_guard_codes(contract_schema, contract)
    ):
        add(errors, f"PRQ-002D contract/schema guard fired: {guard}")
    for guard in sorted(
        predecessor_repository_guard_codes(observe_predecessor_repository())
    ):
        add(errors, f"PRQ-002D predecessor Git-object guard fired: {guard}")
    try:
        Draft202012Validator.check_schema(contract_schema)
        schema_errors = sorted(
            Draft202012Validator(contract_schema).iter_errors(contract),
            key=lambda error: tuple(str(item) for item in error.absolute_path),
        )
    except Exception as exc:
        add(errors, f"PRQ-002D contract-schema failure: {type(exc).__name__}")
        return
    for error in schema_errors[:20]:
        pointer = "/" + "/".join(str(item) for item in error.absolute_path)
        add(errors, f"PRQ-002D contract {pointer}: {error.message}")
    if contract.get("contract_id") != CONTRACT_ID:
        add(errors, "PRQ-002D contract id drifted")
    if not json_exact(contract.get("authority_boundary"), AUTHORITY_BOUNDARY):
        add(errors, "PRQ-002D contract authority boundary drifted")
    if not json_exact(contract.get("claim_boundary"), CLAIM_BOUNDARY):
        add(errors, "PRQ-002D contract claim boundary drifted")
    if not json_exact(contract.get("predecessor_checkpoint"), PREDECESSOR):
        add(errors, "PRQ-002D contract predecessor checkpoint drifted")
    if not json_exact(
        contract.get("predecessor_evidence_bindings"),
        PREDECESSOR_EVIDENCE_BINDINGS,
    ):
        add(errors, "PRQ-002D contract predecessor evidence binding drifted")
    observed_predecessor_bindings = [
        {"role": "raw_number_decision", **repository_binding(PREDECESSOR_DECISION)},
        {
            "role": "raw_number_comparison",
            **repository_binding(PREDECESSOR_COMPARISON),
        },
    ]
    if not json_exact(
        observed_predecessor_bindings,
        PREDECESSOR_EVIDENCE_BINDINGS,
    ):
        add(errors, "PRQ-002D predecessor checkpoint bytes are not retained")
    if not json_exact(contract.get("evaluation_contract"), EVALUATION_CONTRACT):
        add(errors, "PRQ-002D contract evaluation law drifted")
    resources = contract.get("expected_resources")
    replays = contract.get("expected_replays")
    edges = contract.get("expected_reference_edges")
    if (
        not isinstance(resources, list)
        or len(resources) != 2
        or not all(isinstance(row, dict) for row in resources)
        or not isinstance(replays, list)
        or len(replays) != 2
        or not all(isinstance(row, dict) for row in replays)
        or not isinstance(edges, list)
        or len(edges) != 1
        or not all(isinstance(row, dict) for row in edges)
    ):
        add(errors, "PRQ-002D contract semantic inventory is incomplete")
    else:
        resource_ids = [row.get("schema_id") for row in resources]
        resource_blobs = [row.get("resource_blob_id") for row in resources]
        member_keys = [row.get("member_key") for row in resources]
        replay_uris = [row.get("request_uri") for row in replays]
        probe_blobs = [row.get("probe_blob_id") for row in replays]
        derived_keys = [
            (
                f"{row.get('schema_id')}@{row.get('semantic_version')}"
                if isinstance(row, dict)
                else None
            )
            for row in resources
        ]
        if (
            not all(isinstance(value, str) for value in resource_ids)
            or not all(isinstance(value, str) for value in resource_blobs)
            or not all(isinstance(value, str) for value in member_keys)
            or not all(isinstance(value, str) for value in replay_uris)
            or not all(isinstance(value, str) for value in probe_blobs)
            or len(set(resource_ids)) != 2
            or len(set(resource_blobs)) != 2
            or len(set(member_keys)) != 2
            or len(set(probe_blobs)) != 2
            or member_keys != derived_keys
            or member_keys
            != sorted(member_keys, key=lambda key: key.encode("utf-8"))
            or replay_uris != resource_ids
            or not json_exact(
                edges[0],
                {
                    "source_schema_id": resource_ids[0],
                    "keyword_location": "/properties/peer/$ref",
                    "target_schema_id": resource_ids[1],
                },
            )
        ):
            add(errors, "PRQ-002D contract semantic identity/order law drifted")
    if any(
        forbidden in CONTRACT.read_text("utf-8")
        for forbidden in (
            '"member_digest"',
            '"registry_digest"',
            '"ordered_member_pairs_digest"',
            '"canonicalization_profile_ref"',
        )
    ):
        add(errors, "PRQ-002D contract contains a forbidden structured identity field")
    for guard in sorted(contract_evidence_guard_codes(contract)):
        add(errors, f"PRQ-002D contract evidence guard fired: {guard}")


def contains_forbidden_structured_identity(value: Any) -> bool:
    forbidden = {
        "member_digest",
        "registry_digest",
        "ordered_member_pairs_digest",
        "canonicalization_profile_ref",
    }
    if isinstance(value, dict):
        return bool(set(value) & forbidden) or any(
            contains_forbidden_structured_identity(item)
            for item in value.values()
        )
    if isinstance(value, list):
        return any(contains_forbidden_structured_identity(item) for item in value)
    return False


def contract_schema_guard_codes(
    contract_schema: Any,
    contract: Any,
) -> set[str]:
    if contains_forbidden_structured_identity(contract):
        return {"forbidden_structured_identity_boundary"}
    if (
        not isinstance(contract, dict)
        or contract.get("contract_id") != CONTRACT_ID
    ):
        return {"contract_identity_boundary"}
    if not isinstance(contract_schema, dict):
        return {"contract_schema_boundary"}
    try:
        raw_schema_binding = repository_binding(CONTRACT_SCHEMA)
        semantic_schema_binding = raw_binding(compact_json(contract_schema))
    except (OSError, TypeError, ValueError):
        return {"contract_schema_boundary"}
    if (
        not json_exact(
            raw_schema_binding,
            APPROVED_CONTRACT_SCHEMA_RAW_BINDING,
        )
        or not json_exact(
            semantic_schema_binding,
            APPROVED_CONTRACT_SCHEMA_SEMANTIC_BINDING,
        )
    ):
        return {"contract_schema_boundary"}
    if not object_schema_nodes_are_closed(contract_schema):
        return {"contract_schema_boundary"}
    try:
        Draft202012Validator.check_schema(contract_schema)
        if any(Draft202012Validator(contract_schema).iter_errors(contract)):
            return {"contract_schema_boundary"}
    except Exception:
        return {"contract_schema_boundary"}
    return set()


def object_schema_nodes_are_closed(value: Any) -> bool:
    if isinstance(value, list):
        return all(object_schema_nodes_are_closed(item) for item in value)
    if not isinstance(value, dict):
        return True
    declared_type = value.get("type")
    object_asserting_keywords = {
        "required",
        "dependentRequired",
        "dependentSchemas",
        "minProperties",
        "maxProperties",
    }
    object_capable = (
        declared_type == "object"
        or (
            isinstance(declared_type, list)
            and "object" in declared_type
        )
        or (
            "type" not in value
            and bool(object_asserting_keywords.intersection(value))
        )
    )
    if object_capable and value.get("additionalProperties") is not False:
        return False
    return all(object_schema_nodes_are_closed(item) for item in value.values())


def contract_evidence_guard_codes(contract: Any) -> set[str]:
    if not isinstance(contract, dict):
        return {"contract_shape_boundary"}
    guards: set[str] = set()
    if not json_exact(
        contract.get("safe_bundle_binding"),
        repository_binding(SAFE_BUNDLE),
    ):
        guards.add("independent_safe_input_binding")
    if not (
        json_exact(contract.get("predecessor_checkpoint"), PREDECESSOR)
        and json_exact(
            contract.get("predecessor_evidence_bindings"),
            PREDECESSOR_EVIDENCE_BINDINGS,
        )
    ):
        guards.add("predecessor_evidence_boundary")
    resources = contract.get("expected_resources")
    replays = contract.get("expected_replays")
    edges = contract.get("expected_reference_edges")
    semantic_valid = (
        json_exact(contract.get("evaluation_contract"), EVALUATION_CONTRACT)
        and isinstance(resources, list)
        and len(resources) == 2
        and all(isinstance(row, dict) for row in resources)
        and isinstance(replays, list)
        and len(replays) == 2
        and all(isinstance(row, dict) for row in replays)
        and isinstance(edges, list)
        and len(edges) == 1
        and all(isinstance(row, dict) for row in edges)
    )
    if semantic_valid:
        try:
            resource_ids = [row["schema_id"] for row in resources]
            resource_blobs = [row["resource_blob_id"] for row in resources]
            member_keys = [row["member_key"] for row in resources]
            derived_keys = [
                f"{row['schema_id']}@{row['semantic_version']}"
                for row in resources
            ]
            replay_uris = [row["request_uri"] for row in replays]
            probe_blobs = [row["probe_blob_id"] for row in replays]
            semantic_valid = (
                all(
                    isinstance(value, str)
                    for value in (
                        resource_ids
                        + resource_blobs
                        + member_keys
                        + replay_uris
                        + probe_blobs
                    )
                )
                and len(set(resource_ids)) == 2
                and len(set(resource_blobs)) == 2
                and len(set(member_keys)) == 2
                and len(set(probe_blobs)) == 2
                and member_keys == derived_keys
                and member_keys
                == sorted(member_keys, key=lambda key: key.encode("utf-8"))
                and replay_uris == resource_ids
                and json_exact(
                    edges[0],
                    {
                        "source_schema_id": resource_ids[0],
                        "keyword_location": "/properties/peer/$ref",
                        "target_schema_id": resource_ids[1],
                    },
                )
            )
        except (KeyError, TypeError):
            semantic_valid = False
    if not semantic_valid:
        guards.add("contract_semantic_boundary")
    if not json_exact(contract.get("authority_boundary"), AUTHORITY_BOUNDARY):
        guards.add("contract_authority_boundary")
    if not json_exact(contract.get("claim_boundary"), CLAIM_BOUNDARY):
        guards.add("contract_claim_boundary")
    return guards


def expected_input_bindings() -> list[dict[str, str]]:
    rows = (
        ("contract_schema", CONTRACT_SCHEMA),
        ("contract", CONTRACT),
        ("safe_bundle", SAFE_BUNDLE),
        ("resource_001", RESOURCE_1),
        ("resource_002", RESOURCE_2),
        ("probe_001", PROBE_1),
        ("probe_002", PROBE_2),
        ("vectors", VECTORS),
        ("authoring_generator", GENERATOR),
    )
    return [{"role": role, **repository_binding(path)} for role, path in rows]


def expected_input_manifest() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_input_manifest",
        "manifest_id": "prq-002d-schema-registry-prehash-input.0001",
        "suite_id": SUITE_ID,
        "vector_set_id": VECTOR_SET_ID,
        "predecessor_checkpoint": PREDECESSOR,
        "answer_free_child_input": True,
        "binding_count_decimal": "9",
        "bindings": expected_input_bindings(),
    }


def input_manifest_guard_codes(document: Any) -> set[str]:
    return (
        set()
        if isinstance(document, dict)
        and json_exact(document, expected_input_manifest())
        else {"input_manifest_binding_boundary"}
    )


def validate_input_manifest(errors: list[str], document: Any) -> None:
    if input_manifest_guard_codes(document):
        add(errors, "PRQ-002D input manifest differs from exact repository bytes")


def validate_contract_pins(
    errors: list[str],
    contract: Any,
    vectors: Any,
) -> None:
    if not isinstance(contract, dict):
        return
    for guard in sorted(contract_fixture_guard_codes(contract)):
        add(errors, f"PRQ-002D contract fixture guard fired: {guard}")
    for guard in sorted(
        contract_preparse_binding_guard_codes(contract, vectors)
    ):
        add(errors, f"PRQ-002D contract preparse guard fired: {guard}")
    if not json_exact(
        contract.get("safe_bundle_binding"), repository_binding(SAFE_BUNDLE)
    ):
        add(errors, "PRQ-002D safe bundle lacks an independent exact-byte binding")
    expected_resources = contract.get("expected_resources")
    expected_replays = contract.get("expected_replays")
    if (
        not isinstance(expected_resources, list)
        or len(expected_resources) != 2
        or not all(isinstance(row, dict) for row in expected_resources)
        or not isinstance(expected_replays, list)
        or len(expected_replays) != 2
        or not all(isinstance(row, dict) for row in expected_replays)
    ):
        add(errors, "PRQ-002D contract pin inventory is incomplete")
        return
    for row, path in zip(expected_resources, (RESOURCE_1, RESOURCE_2), strict=True):
        expected = repository_binding(path)
        if (
            row.get("repository_path") != expected["repository_path"]
            or row.get("resource_raw_sha256") != expected["raw_sha256"]
            or row.get("resource_byte_count_decimal")
            != expected["byte_count_decimal"]
        ):
            add(errors, f"PRQ-002D resource pin drifted: {path.name}")
    for row, path in zip(expected_replays, (PROBE_1, PROBE_2), strict=True):
        expected = repository_binding(path)
        if (
            row.get("repository_path") != expected["repository_path"]
            or row.get("probe_raw_sha256") != expected["raw_sha256"]
            or row.get("probe_byte_count_decimal")
            != expected["byte_count_decimal"]
        ):
            add(errors, f"PRQ-002D probe pin drifted: {path.name}")


def contract_fixture_guard_codes(contract: Any) -> set[str]:
    if not isinstance(contract, dict):
        return {"contract_fixture_binding_boundary"}
    resources = contract.get("expected_resources")
    replays = contract.get("expected_replays")
    if (
        not json_exact(
            contract.get("safe_bundle_binding"),
            repository_binding(SAFE_BUNDLE),
        )
        or not isinstance(resources, list)
        or len(resources) != 2
        or not all(isinstance(row, dict) for row in resources)
        or not isinstance(replays, list)
        or len(replays) != 2
        or not all(isinstance(row, dict) for row in replays)
    ):
        return {"contract_fixture_binding_boundary"}
    for row, path in zip(resources, (RESOURCE_1, RESOURCE_2), strict=True):
        expected = repository_binding(path)
        if not (
            row.get("repository_path") == expected["repository_path"]
            and row.get("resource_raw_sha256") == expected["raw_sha256"]
            and row.get("resource_byte_count_decimal")
            == expected["byte_count_decimal"]
        ):
            return {"contract_fixture_binding_boundary"}
    for row, path in zip(replays, (PROBE_1, PROBE_2), strict=True):
        expected = repository_binding(path)
        if not (
            row.get("repository_path") == expected["repository_path"]
            and row.get("probe_raw_sha256") == expected["raw_sha256"]
            and row.get("probe_byte_count_decimal")
            == expected["byte_count_decimal"]
        ):
            return {"contract_fixture_binding_boundary"}
    return set()


def contract_preparse_binding_guard_codes(
    contract: Any,
    vectors: Any,
) -> set[str]:
    if not isinstance(contract, dict) or not isinstance(vectors, dict):
        return {"contract_preparse_binding_boundary"}
    vector_rows = vectors.get("vectors")
    resource_overrides = contract.get("preparse_resource_binding_overrides")
    probe_overrides = contract.get("preparse_probe_binding_overrides")
    if (
        not isinstance(vector_rows, list)
        or not isinstance(resource_overrides, list)
        or not isinstance(probe_overrides, list)
        or len(resource_overrides) != len(RESOURCE_OVERRIDE_VECTOR_IDS)
        or len(probe_overrides) != len(PROBE_OVERRIDE_VECTOR_IDS)
    ):
        return {"contract_preparse_binding_boundary"}
    vectors_by_id = {
        row.get("vector_id"): row
        for row in vector_rows
        if isinstance(row, dict) and isinstance(row.get("vector_id"), str)
    }
    if len(vectors_by_id) != len(vector_rows):
        return {"contract_preparse_binding_boundary"}

    safe_resource_binding = {
        "raw_sha256": repository_binding(RESOURCE_1)["raw_sha256"],
        "byte_count_decimal": repository_binding(RESOURCE_1)[
            "byte_count_decimal"
        ],
    }
    for override, vector_id in zip(
        resource_overrides,
        RESOURCE_OVERRIDE_VECTOR_IDS,
        strict=True,
    ):
        files = decoded_vector_files(vectors_by_id.get(vector_id))
        if (
            not isinstance(override, dict)
            or set(override) != RESOURCE_OVERRIDE_KEYS
            or override.get("vector_id") != vector_id
            or override.get("resource_blob_id") != "resource-001"
            or not isinstance(files, dict)
            or "resource-001" not in files
        ):
            return {"contract_preparse_binding_boundary"}
        expected = raw_binding(files["resource-001"])
        observed = {
            "raw_sha256": override.get("resource_raw_sha256"),
            "byte_count_decimal": override.get(
                "resource_byte_count_decimal"
            ),
        }
        if not json_exact(observed, expected) or json_exact(
            observed,
            safe_resource_binding,
        ):
            return {"contract_preparse_binding_boundary"}

    safe_probe_binding = {
        "raw_sha256": repository_binding(PROBE_1)["raw_sha256"],
        "byte_count_decimal": repository_binding(PROBE_1)[
            "byte_count_decimal"
        ],
    }
    for override, vector_id in zip(
        probe_overrides,
        PROBE_OVERRIDE_VECTOR_IDS,
        strict=True,
    ):
        files = decoded_vector_files(vectors_by_id.get(vector_id))
        if (
            not isinstance(override, dict)
            or set(override) != PROBE_OVERRIDE_KEYS
            or override.get("vector_id") != vector_id
            or override.get("probe_blob_id") != "probe-001"
            or not isinstance(files, dict)
            or "probe-001" not in files
        ):
            return {"contract_preparse_binding_boundary"}
        expected = raw_binding(files["probe-001"])
        observed = {
            "raw_sha256": override.get("probe_raw_sha256"),
            "byte_count_decimal": override.get("probe_byte_count_decimal"),
        }
        if not json_exact(observed, expected) or json_exact(
            observed,
            safe_probe_binding,
        ):
            return {"contract_preparse_binding_boundary"}
    return set()


class OracleRawNumber:
    """One JSON number token retained only by the private parent oracle."""

    def __init__(self, token: str):
        self.token = token


def oracle_finite_float(token: str) -> float:
    value = float(token)
    if value in (float("inf"), float("-inf")):
        raise ValueError("non-finite JSON number")
    return value


def inspect_vector_files(vector: Any) -> tuple[dict[str, bytes] | None, bool]:
    if not isinstance(vector, dict) or set(vector) != VECTOR_ROW_KEYS:
        return None, False
    rows = vector.get("files")
    if not isinstance(rows, list):
        return None, False
    result: dict[str, bytes] = {}
    frame_valid = True
    for row in rows:
        if not isinstance(row, dict) or set(row) != VECTOR_FILE_KEYS:
            return None, False
        blob_id = row.get("blob_id")
        if not isinstance(blob_id, str) or blob_id in result:
            return None, False
        try:
            data = base64.b64decode(row.get("content_base64", ""), validate=True)
        except (ValueError, TypeError):
            return None, False
        if (
            row.get("media_type") != "application/json"
            or raw_binding(data)
            != {
                "raw_sha256": row.get("raw_sha256"),
                "byte_count_decimal": row.get("byte_count_decimal"),
            }
        ):
            frame_valid = False
        if base64.b64encode(data).decode("ascii") != row.get("content_base64"):
            frame_valid = False
        result[blob_id] = data
    return result, frame_valid


def decoded_vector_files(vector: Any) -> dict[str, bytes] | None:
    files, frame_valid = inspect_vector_files(vector)
    return files if frame_valid else None


def oracle_bundle_token(data: bytes) -> str | None:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None
    if text.startswith("\ufeff"):
        return None
    parse_constant = lambda token: (_ for _ in ()).throw(
        ValueError(f"non-finite token {token}")
    )
    try:
        syntax_value = json.loads(
            text,
            parse_constant=parse_constant,
            parse_float=oracle_finite_float,
        )
    except (json.JSONDecodeError, ValueError):
        return None
    if has_unpaired_surrogate_oracle(syntax_value):
        return None
    try:
        value = json.loads(
            text,
            object_pairs_hook=strict_pairs,
            parse_int=OracleRawNumber,
            parse_float=OracleRawNumber,
            parse_constant=parse_constant,
        )
    except (json.JSONDecodeError, DuplicateKey, ValueError):
        return None
    if not isinstance(value, dict):
        return None
    number = value.get("declared_member_count")
    return number.token if isinstance(number, OracleRawNumber) else None


def has_unpaired_surrogate_oracle(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    if isinstance(value, list):
        return any(has_unpaired_surrogate_oracle(item) for item in value)
    if isinstance(value, dict):
        return any(
            has_unpaired_surrogate_oracle(key)
            or has_unpaired_surrogate_oracle(item)
            for key, item in value.items()
        )
    return False


def expected_bundle_projection(vector: Any) -> tuple[Any, Any, Any]:
    files, frame_valid = inspect_vector_files(vector)
    if not frame_valid or not isinstance(files, dict) or "bundle" not in files:
        return None, None, None
    data = files["bundle"]
    binding = raw_binding(data)
    return (
        binding["raw_sha256"],
        binding["byte_count_decimal"],
        oracle_bundle_token(data),
    )


def cases_shape_guard_codes(cases: Any) -> set[str]:
    if (
        not isinstance(cases, dict)
        or set(cases) != CASES_ROOT_KEYS
        or not isinstance(cases.get("cases"), list)
        or not all(
            isinstance(row, dict) and set(row) == CASE_ROW_KEYS
            for row in cases["cases"]
        )
        or not isinstance(cases.get("gate_known_bads"), list)
        or not all(
            isinstance(row, dict) and set(row) == GATE_ROW_KEYS
            for row in cases["gate_known_bads"]
        )
    ):
        return {"private_expectation_shape_boundary"}
    return set()


def vector_inventory_guard_codes(vectors: Any) -> set[str]:
    rows = vectors.get("vectors") if isinstance(vectors, dict) else None
    if (
        not isinstance(vectors, dict)
        or set(vectors) != VECTOR_ROOT_KEYS
        or vectors.get("schema_version") != "0.1.0"
        or vectors.get("artifact_class")
        != "prq_002d_schema_registry_prehash_vector_set"
        or vectors.get("vector_set_id") != VECTOR_SET_ID
        or vectors.get("vector_count_decimal") != str(len(EXPECTED_CODES))
        or not isinstance(rows, list)
        or len(rows) != len(EXPECTED_CODES)
    ):
        return {"vector_inventory_boundary"}
    for index, row in enumerate(rows):
        decoded, _ = inspect_vector_files(row)
        if (
            not isinstance(row, dict)
            or set(row) != VECTOR_ROW_KEYS
            or row.get("sequence_index_decimal") != str(index)
            or row.get("vector_id") != f"PH-{index + 1:04d}"
            or decoded is None
        ):
            return {"vector_inventory_boundary"}
    return set()


def safe_vector_binding_guard_codes(vectors: Any) -> set[str]:
    try:
        rows = vectors["vectors"]
        safe_files = decoded_vector_files(rows[0])
    except (KeyError, IndexError, TypeError, ValueError):
        return {"safe_vector_binding_boundary"}
    expected_safe = {
        "bundle": SAFE_BUNDLE.read_bytes(),
        "resource-001": RESOURCE_1.read_bytes(),
        "resource-002": RESOURCE_2.read_bytes(),
        "probe-001": PROBE_1.read_bytes(),
        "probe-002": PROBE_2.read_bytes(),
    }
    return (
        set()
        if safe_files == expected_safe
        else {"safe_vector_binding_boundary"}
    )


def private_expectation_inventory_guard_codes(cases: Any) -> set[str]:
    rows = cases.get("cases") if isinstance(cases, dict) else None
    if (
        not isinstance(cases, dict)
        or cases.get("schema_version") != "0.1.0"
        or cases.get("artifact_class")
        != "prq_002d_schema_registry_prehash_private_expectations"
        or cases.get("expectation_set_id")
        != "prq-002d-schema-registry-prehash-expectations.0001"
        or cases.get("suite_id") != SUITE_ID
        or cases.get("vector_set_id") != VECTOR_SET_ID
        or cases.get("case_count_decimal") != str(len(EXPECTED_CODES))
        or cases.get("safe_count_decimal") != "1"
        or cases.get("known_bad_count_decimal")
        != str(len(EXPECTED_CODES) - 1)
        or not isinstance(rows, list)
        or len(rows) != len(EXPECTED_CODES)
        or not json_exact(cases.get("gate_known_bads"), expected_gate_rows())
    ):
        return {"private_expectation_inventory_boundary"}
    for index, (row, code) in enumerate(
        zip(rows, EXPECTED_CODES, strict=True)
    ):
        expected_disposition = "accepted" if index == 0 else "refused"
        expected_errors = [] if index == 0 else [code]
        if (
            not isinstance(row, dict)
            or set(row) != CASE_ROW_KEYS
            or row.get("sequence_index_decimal") != str(index)
            or row.get("vector_id") != f"PH-{index + 1:04d}"
            or row.get("kind") != ("safe" if index == 0 else "known_bad")
            or row.get("expected_disposition") != expected_disposition
            or row.get("expected_code") != code
            or not json_exact(row.get("intent_errors"), expected_errors)
            or not json_exact(row.get("expected_errors"), expected_errors)
            or not isinstance(row.get("name"), str)
            or not row["name"]
        ):
            return {"private_expectation_inventory_boundary"}
    return set()


def validate_vectors_and_cases(
    errors: list[str],
    vectors: Any,
    cases: Any,
) -> None:
    if not isinstance(vectors, dict) or not isinstance(cases, dict):
        return
    for guard in sorted(vector_inventory_guard_codes(vectors)):
        add(errors, f"PRQ-002D vector inventory guard fired: {guard}")
    for guard in sorted(safe_vector_binding_guard_codes(vectors)):
        add(errors, f"PRQ-002D safe-vector guard fired: {guard}")
    for guard in sorted(cases_shape_guard_codes(cases)):
        add(errors, f"PRQ-002D private expectation guard fired: {guard}")
    for guard in sorted(private_expectation_inventory_guard_codes(cases)):
        add(errors, f"PRQ-002D private expectation inventory fired: {guard}")
    vector_rows = vectors.get("vectors")
    case_rows = cases.get("cases")
    if (
        set(vectors) != VECTOR_ROOT_KEYS
        or vectors.get("schema_version") != "0.1.0"
        or vectors.get("artifact_class")
        != "prq_002d_schema_registry_prehash_vector_set"
        or vectors.get("vector_set_id") != VECTOR_SET_ID
        or not isinstance(vector_rows, list)
        or vectors.get("vector_count_decimal") != str(len(EXPECTED_CODES))
        or len(vector_rows) != len(EXPECTED_CODES)
    ):
        add(errors, "PRQ-002D vector-set root or census drifted")
        return
    if (
        set(cases) != CASES_ROOT_KEYS
        or cases.get("schema_version") != "0.1.0"
        or cases.get("artifact_class")
        != "prq_002d_schema_registry_prehash_private_expectations"
        or cases.get("expectation_set_id")
        != "prq-002d-schema-registry-prehash-expectations.0001"
        or cases.get("suite_id") != SUITE_ID
        or cases.get("vector_set_id") != VECTOR_SET_ID
        or cases.get("case_count_decimal") != str(len(EXPECTED_CODES))
        or cases.get("safe_count_decimal") != "1"
        or cases.get("known_bad_count_decimal") != str(len(EXPECTED_CODES) - 1)
        or not isinstance(case_rows, list)
        or len(case_rows) != len(EXPECTED_CODES)
    ):
        add(errors, "PRQ-002D private expectation root or census drifted")
        return
    for index, (vector, case, code) in enumerate(
        zip(vector_rows, case_rows, EXPECTED_CODES, strict=True)
    ):
        expected_index = str(index)
        expected_id = f"PH-{index + 1:04d}"
        decoded, frame_valid = inspect_vector_files(vector)
        if (
            not isinstance(vector, dict)
            or set(vector) != VECTOR_ROW_KEYS
            or vector.get("sequence_index_decimal") != expected_index
            or vector.get("vector_id") != expected_id
            or OPAQUE_ID_RE.fullmatch(expected_id) is None
            or decoded is None
        ):
            add(errors, f"PRQ-002D malformed or misordered vector {expected_id}")
        expected_disposition = "accepted" if index == 0 else "refused"
        expected_errors = [] if index == 0 else [code]
        if (
            not frame_valid
            and code != "ODEYA_CONFORMANCE_FRAME_SHAPE"
        ):
            add(errors, f"PRQ-002D unexpected invalid virtual-file frame {expected_id}")
        if (
            not isinstance(case, dict)
            or set(case) != CASE_ROW_KEYS
            or case.get("sequence_index_decimal") != expected_index
            or case.get("vector_id") != expected_id
            or case.get("kind") != ("safe" if index == 0 else "known_bad")
            or case.get("expected_disposition") != expected_disposition
            or case.get("expected_code") != code
            or case.get("intent_errors") != expected_errors
            or case.get("expected_errors") != expected_errors
            or not isinstance(case.get("name"), str)
            or not case["name"]
        ):
            add(errors, f"PRQ-002D fixed oracle drifted at {expected_id}")
    if vector_rows:
        safe_files = decoded_vector_files(vector_rows[0])
        expected_safe = {
            "bundle": SAFE_BUNDLE.read_bytes(),
            "resource-001": RESOURCE_1.read_bytes(),
            "resource-002": RESOURCE_2.read_bytes(),
            "probe-001": PROBE_1.read_bytes(),
            "probe-002": PROBE_2.read_bytes(),
        }
        if safe_files != expected_safe:
            add(errors, "PRQ-002D safe vector differs from independently pinned fixtures")
    observed_gate_rows = cases.get("gate_known_bads")
    expected_gate_rows = [
        {"id": key, "mutation": mutation, "expected_guard": guard}
        for key, (mutation, guard) in GATE_KNOWN_BADS.items()
    ]
    if observed_gate_rows != expected_gate_rows:
        add(errors, "PRQ-002D gate known-bad inventory drifted")
    elif any(
        not isinstance(row, dict) or set(row) != GATE_ROW_KEYS
        for row in observed_gate_rows
    ):
        add(errors, "PRQ-002D gate known-bad row shape drifted")


def source_file_bindings(paths: Iterable[tuple[str, Path]]) -> list[dict[str, str]]:
    return [{"role": role, **repository_binding(path)} for role, path in paths]


def expected_source_manifest(role: str) -> dict[str, Any]:
    if role == "python":
        return {
            "schema_version": "0.1.0",
            "artifact_class": "prq_002d_schema_registry_prehash_source_manifest",
            "suite_id": SUITE_ID,
            "role": "python",
            "implementation_id": PYTHON_ID,
            "language": "Python",
            "runtime_version": PYTHON_VERSION,
            "parser_strategy": (
                "stdlib_strict_pairs_and_pointer_scoped_raw_number_sidecar"
            ),
            "schema_strategy": (
                "five_distribution_runtime_checked_jsonschema_closed_registry"
            ),
            "source_file_count_decimal": "2",
            "source_files": source_file_bindings(
                (
                    ("runner", PYTHON_RUNNER),
                    ("dependency_lock", PYTHON_LOCK),
                )
            ),
            "allowed_input_roles": ["vectors", "contract", "source_manifest"],
            "private_expectation_consumption_allowed": False,
            "peer_source_consumption_allowed": False,
            "peer_result_consumption_allowed": False,
            "network_access_requested": False,
            "filesystem_isolation_proven": False,
        }
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_source_manifest",
        "suite_id": SUITE_ID,
        "role": "node",
        "implementation_id": NODE_ID,
        "language": "JavaScript",
        "runtime_version": NODE_VERSION,
        "parser_strategy": "recursive_descent_strict_json_with_raw_count_token",
        "schema_strategy": "ajv_8_20_0_strict_preloaded_only",
        "source_file_count_decimal": "4",
        "source_files": source_file_bindings(
            (
                ("runner", NODE_RUNNER),
                ("package_manifest", NODE_PACKAGE),
                ("package_lock", NODE_LOCK),
                ("toolchain_installer", NODE_INSTALLER),
            )
        ),
        "allowed_input_roles": ["vectors", "contract", "source_manifest"],
        "private_expectation_consumption_allowed": False,
        "peer_source_consumption_allowed": False,
        "peer_result_consumption_allowed": False,
        "network_access_requested": False,
        "filesystem_isolation_proven": False,
    }


def python_imports(source: str) -> set[str]:
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return imports


def python_import_inventory(source: str) -> tuple[Any, ...]:
    tree = ast.parse(source)
    rows: list[Any] = []
    import_nodes = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ),
        key=lambda node: (node.lineno, node.col_offset),
    )
    for node in import_nodes:
        if isinstance(node, ast.Import):
            rows.append(
                (
                    "import",
                    None,
                    0,
                    tuple((alias.name, alias.asname) for alias in node.names),
                    node in tree.body,
                )
            )
        else:
            rows.append(
                (
                    "from",
                    node.module,
                    node.level,
                    tuple((alias.name, alias.asname) for alias in node.names),
                    node in tree.body,
                )
            )
    return tuple(rows)


def forbidden_python_dynamic_calls(source: str) -> set[str]:
    tree = ast.parse(source)
    forbidden: set[str] = set()
    denied_names = {
        "__import__",
        "__builtins__",
        "compile",
        "eval",
        "exec",
        "getattr",
        "globals",
        "locals",
        "vars",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in denied_names:
            forbidden.add(node.id)
        elif isinstance(node, ast.Attribute):
            if node.attr in {
                "__globals__",
                "__import__",
                "__subclasses__",
                "import_module",
                "exec_module",
            }:
                forbidden.add(node.attr)
            elif (
                isinstance(node.value, ast.Name)
                and node.value.id == "__builtins__"
                and node.attr in denied_names
            ):
                forbidden.add(node.attr)
        elif isinstance(node, ast.Subscript):
            selector = node.slice
            if (
                isinstance(selector, ast.Constant)
                and isinstance(selector.value, str)
                and selector.value
                in (
                    denied_names
                    | {
                        "__globals__",
                        "__subclasses__",
                        "import_module",
                        "exec_module",
                    }
                )
            ):
                forbidden.add(selector.value)
    return forbidden


def expected_node_package() -> dict[str, Any]:
    return {
        "name": "@odeya/schema-registry-prehash-replay-node",
        "version": "0.1.0",
        "private": True,
        "description": (
            "Source-separated Node.js observer for the non-product PRQ-002D "
            "schema-registry prehash replay."
        ),
        "type": "module",
        "packageManager": f"npm@{NPM_VERSION}",
        "engines": {"node": NODE_VERSION},
        "dependencies": {"ajv": "8.20.0"},
    }


def expected_node_lock() -> dict[str, Any]:
    return {
        "name": "@odeya/schema-registry-prehash-replay-node",
        "version": "0.1.0",
        "lockfileVersion": 3,
        "requires": True,
        "packages": {
            "": {
                "name": "@odeya/schema-registry-prehash-replay-node",
                "version": "0.1.0",
                "dependencies": {"ajv": "8.20.0"},
                "engines": {"node": NODE_VERSION},
            },
            "node_modules/ajv": {
                "version": "8.20.0",
                "resolved": "https://registry.npmjs.org/ajv/-/ajv-8.20.0.tgz",
                "integrity": (
                    "sha512-Thbli+OlOj+iMPYFBVBfJ3OmCAnaSyNn4M1vz9T6Gka5Jt9ba/"
                    "HIR56joy65tY6kx/FCF5VXNB819Y7/GUrBGA=="
                ),
                "license": "MIT",
                "dependencies": {
                    "fast-deep-equal": "^3.1.3",
                    "fast-uri": "^3.0.1",
                    "json-schema-traverse": "^1.0.0",
                    "require-from-string": "^2.0.2",
                },
                "funding": {
                    "type": "github",
                    "url": "https://github.com/sponsors/epoberezkin",
                },
            },
            "node_modules/fast-deep-equal": {
                "version": "3.1.3",
                "resolved": (
                    "https://registry.npmjs.org/fast-deep-equal/"
                    "-/fast-deep-equal-3.1.3.tgz"
                ),
                "integrity": (
                    "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5"
                    "HYNz9cGI++xlpDCIgDaitVs03ATR84Q=="
                ),
                "license": "MIT",
            },
            "node_modules/fast-uri": {
                "version": "3.1.0",
                "resolved": "https://registry.npmjs.org/fast-uri/-/fast-uri-3.1.0.tgz",
                "integrity": (
                    "sha512-iPeeDKJSWf4IEOasVVrknXpaBV0IApz/gp7S2bb7Z4Lljbl2MGJRqInZi"
                    "UrQwV16cpzw/D3S5j5Julj/gT52AA=="
                ),
                "license": "BSD-3-Clause",
            },
            "node_modules/json-schema-traverse": {
                "version": "1.0.0",
                "resolved": (
                    "https://registry.npmjs.org/json-schema-traverse/"
                    "-/json-schema-traverse-1.0.0.tgz"
                ),
                "integrity": (
                    "sha512-NM8/P9n3XjXhIZn1lLhkFaACTOURQXjWhV4BA/RnOv8xvgqtqpAX9IO4"
                    "mRQxSx1Rlo4tqzeqb0sOlruaOy3dug=="
                ),
                "license": "MIT",
            },
            "node_modules/require-from-string": {
                "version": "2.0.2",
                "resolved": (
                    "https://registry.npmjs.org/require-from-string/"
                    "-/require-from-string-2.0.2.tgz"
                ),
                "integrity": (
                    "sha512-Xf0nWe6RseziFMu+Ap9biiUbmplq6S9/p+7w7YXP/JBHhrUDDUhwa+vA"
                    "NyubuqfZWTveU//DYVGsDG7RKL/vEw=="
                ),
                "license": "MIT",
                "engines": {"node": ">=0.10.0"},
            },
        },
    }


def source_manifest_guard_codes(role: str, document: Any) -> set[str]:
    return (
        set()
        if isinstance(document, dict)
        and json_exact(document, expected_source_manifest(role))
        else {"source_binding_boundary"}
    )


def dependency_guard_codes(
    python_lock: Any,
    node_package: Any,
    node_lock: Any,
) -> set[str]:
    expected_python_lock = {
        "schema_version": "0.1.0",
        "implementation_id": PYTHON_ID,
        "runtime": f"CPython {PYTHON_VERSION}",
        "installation_lock_binding": repository_binding(
            PYTHON_INSTALLATION_LOCK
        ),
        "third_party_distributions": [
            {"name": "attrs", "version": "26.1.0"},
            {"name": "jsonschema", "version": "4.26.0"},
            {
                "name": "jsonschema-specifications",
                "version": "2025.9.1",
            },
            {"name": "referencing", "version": "0.37.0"},
            {"name": "rpds-py", "version": "2026.6.3"},
        ],
        "stdlib_modules": [
            "argparse",
            "base64",
            "hashlib",
            "importlib.metadata",
            "json",
            "pathlib",
            "re",
            "sys",
            "typing",
        ],
    }
    if not (
        json_exact(python_lock, expected_python_lock)
        and json_exact(node_package, expected_node_package())
        and json_exact(node_lock, expected_node_lock())
    ):
        return {"dependency_binding_boundary"}
    return set()


def source_text_guard_codes(
    python_source: bytes | str,
    node_source: bytes | str,
) -> set[str]:
    python_raw = (
        python_source.encode("utf-8")
        if isinstance(python_source, str)
        else python_source
    )
    node_raw = (
        node_source.encode("utf-8")
        if isinstance(node_source, str)
        else node_source
    )
    try:
        python_text = python_raw.decode("utf-8")
        node_text = node_raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"source_parse_boundary"}
    try:
        observed_python_inventory = python_import_inventory(python_text)
        dynamic_calls = forbidden_python_dynamic_calls(python_text)
    except SyntaxError:
        return {"source_parse_boundary"}
    expected_python_inventory = (
        ("from", "__future__", 0, (("annotations", None),), True),
        ("import", None, 0, (("argparse", None),), True),
        ("import", None, 0, (("base64", None),), True),
        ("import", None, 0, (("hashlib", None),), True),
        ("import", None, 0, (("json", None),), True),
        ("import", None, 0, (("re", None),), True),
        ("import", None, 0, (("sys", None),), True),
        (
            "from",
            "importlib.metadata",
            0,
            (("version", "distribution_version"),),
            True,
        ),
        ("from", "pathlib", 0, (("Path", None),), True),
        (
            "from",
            "typing",
            0,
            (("Any", None), ("NoReturn", None)),
            True,
        ),
        (
            "from",
            "jsonschema",
            0,
            (("Draft202012Validator", None),),
            True,
        ),
        (
            "from",
            "jsonschema.exceptions",
            0,
            (("SchemaError", None),),
            True,
        ),
        (
            "from",
            "referencing",
            0,
            (("Registry", None), ("Resource", None)),
            True,
        ),
        (
            "from",
            "referencing.exceptions",
            0,
            (("NoSuchResource", None),),
            True,
        ),
    )
    combined = python_text + "\n" + node_text
    if "schema-registry-prehash-replay/cases.json" in combined:
        return {"answer_free_input_boundary"}
    if "node/runner.mjs" in python_text or "python/runner.py" in node_text:
        return {"source_separation_boundary"}
    if (
        "results/python-jsonschema.json" in combined
        or "results/node-ajv2020.json" in combined
    ):
        return {"peer_result_boundary"}
    lowered_node = node_text.lower()
    expected_node_import_lines = [
        'import { createHash } from "node:crypto";',
        'import { createRequire } from "node:module";',
        'import { readFileSync } from "node:fs";',
        'import process from "node:process";',
        'import { TextDecoder } from "node:util";',
        'import Ajv2020 from "ajv/dist/2020.js";',
    ]
    observed_node_import_lines = [
        line.strip()
        for line in node_text.splitlines()
        if re.match(r"^\s*import\b", line)
    ]
    observed_node_requires = re.findall(
        r'\brequire(?:\s|/\*[\s\S]*?\*/|//[^\n]*(?:\n|$))*'
        r'\((?:\s|/\*[\s\S]*?\*/|//[^\n]*(?:\n|$))*'
        r'["\']([^"\']+)["\']',
        node_text,
    )
    observed_node_require_starts = re.findall(
        r'\brequire(?:\s|/\*[\s\S]*?\*/|//[^\n]*(?:\n|$))*\(',
        node_text,
    )
    dynamic_node_import = re.search(
        r'\bimport(?:\s|/\*[\s\S]*?\*/|//[^\n]*(?:\n|$))*\(',
        node_text,
    )
    if any(
        forbidden in lowered_node
        for forbidden in (
            "node:http",
            "node:https",
            "node:net",
            "node:tls",
            "node:dns",
            "fetch(",
            "xmlhttprequest",
        )
    ) or dynamic_calls or not all(
        marker in python_text
        for marker in ("Registry(retrieve=deny_retrieve)", "NoSuchResource")
    ) or not all(
        marker in node_text
        for marker in (
            "loadSchema: undefined",
            "coerceTypes: false",
            "useDefaults: false",
            "removeAdditional: false",
        )
    ):
        return {"closed_resolver_source_boundary"}
    python_binding = raw_binding(python_raw)
    node_binding = raw_binding(node_raw)
    if (
        observed_python_inventory != expected_python_inventory
        or observed_node_import_lines != expected_node_import_lines
        or observed_node_requires != ["ajv/package.json"]
        or len(observed_node_require_starts) != 1
        or dynamic_node_import is not None
    ):
        return {"source_capability_boundary"}
    if (
        not json_exact(python_binding, APPROVED_PYTHON_RUNNER_BINDING)
        or not json_exact(node_binding, APPROVED_NODE_RUNNER_BINDING)
    ):
        return {"approved_source_binding_boundary"}
    return set()


def validate_source_controls(
    errors: list[str],
    python_source: Any,
    node_source: Any,
) -> None:
    for guard in sorted(source_manifest_guard_codes("python", python_source)):
        add(errors, f"PRQ-002D Python source manifest guard fired: {guard}")
    for guard in sorted(source_manifest_guard_codes("node", node_source)):
        add(errors, f"PRQ-002D Node source manifest guard fired: {guard}")
    python_lock_for_guard = load(PYTHON_LOCK, errors)
    package_for_guard = load(NODE_PACKAGE, errors)
    lock_for_guard = load(NODE_LOCK, errors)
    for guard in sorted(
        dependency_guard_codes(
            python_lock_for_guard,
            package_for_guard,
            lock_for_guard,
        )
    ):
        add(errors, f"PRQ-002D dependency guard fired: {guard}")
    python_raw = PYTHON_RUNNER.read_bytes()
    node_raw = NODE_RUNNER.read_bytes()
    for guard in sorted(
        source_text_guard_codes(python_raw, node_raw)
    ):
        add(errors, f"PRQ-002D source guard fired: {guard}")
    if isinstance(python_source, dict) and not json_exact(
        python_source, expected_source_manifest("python")
    ):
        add(errors, "PRQ-002D Python source manifest differs from exact source bytes")
    if isinstance(node_source, dict) and not json_exact(
        node_source, expected_source_manifest("node")
    ):
        add(errors, "PRQ-002D Node source manifest differs from exact source bytes")
    python_lock = load(PYTHON_LOCK, errors)
    expected_python_lock = {
        "schema_version": "0.1.0",
        "implementation_id": PYTHON_ID,
        "runtime": f"CPython {PYTHON_VERSION}",
        "installation_lock_binding": repository_binding(
            PYTHON_INSTALLATION_LOCK
        ),
        "third_party_distributions": [
            {"name": "attrs", "version": "26.1.0"},
            {"name": "jsonschema", "version": "4.26.0"},
            {
                "name": "jsonschema-specifications",
                "version": "2025.9.1",
            },
            {"name": "referencing", "version": "0.37.0"},
            {"name": "rpds-py", "version": "2026.6.3"},
        ],
        "stdlib_modules": [
            "argparse",
            "base64",
            "hashlib",
            "importlib.metadata",
            "json",
            "pathlib",
            "re",
            "sys",
            "typing",
        ],
    }
    if not json_exact(python_lock, expected_python_lock):
        add(errors, "PRQ-002D Python dependency lock drifted")
    package = load(NODE_PACKAGE, errors)
    lock = load(NODE_LOCK, errors)
    if not json_exact(package, expected_node_package()):
        add(errors, "PRQ-002D Node package/installer contract drifted")
    if not json_exact(lock, expected_node_lock()):
        add(errors, "PRQ-002D Node dependency closure drifted")

    try:
        python_text = python_raw.decode("utf-8")
        node_text = node_raw.decode("utf-8")
    except UnicodeDecodeError:
        add(errors, "PRQ-002D observer source is not strict UTF-8")
        return
    allowed_python_imports = {
        "__future__",
        "argparse",
        "base64",
        "hashlib",
        "importlib",
        "json",
        "re",
        "sys",
        "pathlib",
        "typing",
        "jsonschema",
        "referencing",
    }
    try:
        observed_imports = python_imports(python_text)
        dynamic_calls = forbidden_python_dynamic_calls(python_text)
    except SyntaxError:
        observed_imports = set()
        dynamic_calls = set()
        add(errors, "PRQ-002D Python observer does not parse")
    if observed_imports - allowed_python_imports:
        add(
            errors,
            "PRQ-002D Python observer imports undeclared modules: "
            + ", ".join(sorted(observed_imports - allowed_python_imports)),
        )
    if dynamic_calls:
        add(
            errors,
            "PRQ-002D Python observer uses forbidden dynamic execution: "
            + ", ".join(sorted(dynamic_calls)),
        )
    combined = python_text + "\n" + node_text
    for forbidden in (
        "schema-registry-prehash-replay/cases.json",
        "results/python-jsonschema.json",
        "results/node-ajv2020.json",
    ):
        if forbidden in combined:
            add(errors, f"PRQ-002D child source names forbidden input {forbidden}")
    if "node/runner.mjs" in python_text or "python/runner.py" in node_text:
        add(errors, "PRQ-002D child source names its peer implementation")
    lowered_node = node_text.lower()
    for forbidden in (
        "node:http",
        "node:https",
        "node:net",
        "node:tls",
        "node:dns",
        "fetch(",
        "xmlhttprequest",
    ):
        if forbidden in lowered_node:
            add(errors, f"PRQ-002D Node observer requests forbidden network surface {forbidden}")
    if not all(
        marker in python_text
        for marker in ("Registry(retrieve=deny_retrieve)", "NoSuchResource")
    ):
        add(errors, "PRQ-002D Python observer lacks an explicit deny-all retrieval callback")
    if not all(
        marker in node_text
        for marker in (
            "loadSchema: undefined",
            "coerceTypes: false",
            "useDefaults: false",
            "removeAdditional: false",
        )
    ):
        add(errors, "PRQ-002D Node observer lacks strict closed Ajv controls")


def result_projection(document: dict[str, Any]) -> list[Any]:
    value = document.get("results")
    return value if isinstance(value, list) else []


def expected_resolved_replay_bindings(contract: dict[str, Any]) -> list[dict[str, str]]:
    resources = {
        item["schema_id"]: item for item in contract["expected_resources"]
    }
    return [
        {
            "request_uri": replay["request_uri"],
            "resolved_schema_id": resources[replay["request_uri"]]["schema_id"],
            "resource_blob_id": resources[replay["request_uri"]][
                "resource_blob_id"
            ],
            "resource_raw_sha256": resources[replay["request_uri"]][
                "resource_raw_sha256"
            ],
            "resource_byte_count_decimal": resources[replay["request_uri"]][
                "resource_byte_count_decimal"
            ],
        }
        for replay in contract["expected_replays"]
    ]


def result_guard_codes(
    document: Any,
    *,
    role: str,
    source_manifest: Path,
    vectors: Any,
    cases: Any,
    contract: Any,
    binding_overrides: dict[Path, bytes] | None = None,
) -> set[str]:
    if not isinstance(document, dict) or set(document) != RESULT_ROOT_KEYS:
        return {"result_root_shape_boundary"}
    implementation = PYTHON_ID if role == "python" else NODE_ID
    if (
        document.get("schema_version") != "0.1.0"
        or document.get("artifact_class")
        != "prq_002d_schema_registry_prehash_observation"
        or document.get("suite_id") != SUITE_ID
        or document.get("implementation_id") != implementation
        or document.get("vector_set_id") != VECTOR_SET_ID
        or document.get("vector_count_decimal") != str(len(EXPECTED_CODES))
    ):
        return {"result_metadata_boundary"}
    expected_bindings = {
        "vectors": raw_binding(
            (
                binding_overrides[VECTORS]
                if binding_overrides is not None
                and VECTORS in binding_overrides
                else VECTORS.read_bytes()
            )
        ),
        "contract": raw_binding(
            (
                binding_overrides[CONTRACT]
                if binding_overrides is not None
                and CONTRACT in binding_overrides
                else CONTRACT.read_bytes()
            )
        ),
        "source_manifest": raw_binding(
            (
                binding_overrides[source_manifest]
                if binding_overrides is not None
                and source_manifest in binding_overrides
                else source_manifest.read_bytes()
            )
        ),
    }
    if not json_exact(document.get("input_bindings"), expected_bindings):
        return {"result_input_binding_boundary"}
    rows = document.get("results")
    if not isinstance(rows, list) or len(rows) != len(EXPECTED_CODES):
        return {"complete_result_inventory"}
    if not (
        isinstance(vectors, dict)
        and isinstance(vectors.get("vectors"), list)
        and len(vectors["vectors"]) == len(rows)
        and all(isinstance(vector, dict) for vector in vectors["vectors"])
        and isinstance(cases, dict)
        and isinstance(cases.get("cases"), list)
        and len(cases["cases"]) == len(rows)
        and all(isinstance(case, dict) for case in cases["cases"])
        and isinstance(contract, dict)
        and isinstance(contract.get("expected_resources"), list)
        and len(contract["expected_resources"]) == 2
        and all(
            isinstance(resource, dict)
            for resource in contract["expected_resources"]
        )
        and isinstance(contract.get("expected_replays"), list)
        and len(contract["expected_replays"]) == 2
        and all(
            isinstance(replay, dict)
            for replay in contract["expected_replays"]
        )
    ):
        return {"result_oracle_input_boundary"}
    expected_order = [
        (str(index), f"PH-{index + 1:04d}") for index in range(len(rows))
    ]
    observed_order = [
        (
            row.get("sequence_index_decimal"),
            row.get("vector_id"),
        )
        if isinstance(row, dict)
        else (None, None)
        for row in rows
    ]
    if observed_order != expected_order:
        return {"ordered_result_inventory"}
    if any(
        not isinstance(row, dict) or set(row) != RESULT_ROW_KEYS
        for row in rows
    ):
        return {"result_row_shape_boundary"}
    for row, case, code in zip(
        rows,
        cases["cases"],
        EXPECTED_CODES,
        strict=True,
    ):
        if (
            row.get("final_disposition")
            != case.get("expected_disposition")
            or row.get("final_code") != code
        ):
            return {"private_expectation_boundary"}
    for row, vector in zip(rows, vectors["vectors"], strict=True):
        digest, count, token = expected_bundle_projection(vector)
        if not json_exact(row.get("bundle_raw_sha256"), digest):
            return {"bundle_raw_digest_projection_boundary"}
        if not json_exact(row.get("bundle_byte_count_decimal"), count):
            return {"bundle_byte_count_projection_boundary"}
        if not json_exact(row.get("declared_member_count_raw_token"), token):
            return {"declared_member_count_raw_token_projection_boundary"}
    try:
        accepted_keys = [
            resource["member_key"] for resource in contract["expected_resources"]
        ]
        resolved = expected_resolved_replay_bindings(contract)
    except (KeyError, TypeError):
        return {"result_oracle_input_boundary"}
    probe_count = str(len(contract["expected_replays"]))
    for row, case in zip(rows, cases["cases"], strict=True):
        if case.get("expected_disposition") == "accepted":
            if not json_exact(row.get("ordered_member_keys"), accepted_keys):
                return {"accepted_member_order_projection_boundary"}
            if not json_exact(row.get("resolved_replay_bindings"), resolved):
                return {"accepted_resolved_replay_projection_boundary"}
            if not json_exact(
                row.get("validated_probe_count_decimal"), probe_count
            ):
                return {"validated_probe_count_projection_boundary"}
        elif not (
            json_exact(row.get("ordered_member_keys"), [])
            and json_exact(row.get("resolved_replay_bindings"), [])
            and row.get("validated_probe_count_decimal") is None
        ):
            return {"refusal_nonobservation_boundary"}
    if not json_exact(document.get("claim_boundary"), CLAIM_BOUNDARY):
        return {"claim_scope_boundary"}
    return set()


def validate_result(
    errors: list[str],
    document: Any,
    *,
    role: str,
    source_manifest: Path,
    vectors: Any,
    cases: Any,
    contract: Any,
) -> None:
    guards = result_guard_codes(
        document,
        role=role,
        source_manifest=source_manifest,
        vectors=vectors,
        cases=cases,
        contract=contract,
    )
    for guard in sorted(guards):
        add(errors, f"PRQ-002D {role} retained result guard fired: {guard}")
    path = PYTHON_RESULT if role == "python" else NODE_RESULT
    for guard in sorted(
        result_framing_guard_codes(document, path.read_bytes())
    ):
        add(errors, f"PRQ-002D {role} retained result guard fired: {guard}")


def result_framing_guard_codes(
    document: Any,
    retained_raw: bytes,
) -> set[str]:
    if not isinstance(document, dict):
        return {"result_framing_boundary"}
    try:
        expected = compact_json(document) + b"\n"
    except (TypeError, ValueError):
        return {"result_framing_boundary"}
    return (
        set()
        if retained_raw == expected
        else {"result_framing_boundary"}
    )


def expected_execution_receipt(
    role: str,
    *,
    runtime: dict[str, Any],
    argv: list[str],
    binding_overrides: dict[Path, bytes] | None = None,
) -> dict[str, Any]:
    python = role == "python"
    result_path = PYTHON_RESULT if python else NODE_RESULT
    source_path = PYTHON_SOURCE if python else NODE_SOURCE
    runner_path = PYTHON_RUNNER if python else NODE_RUNNER
    controls = (
        [
            repository_binding(PYTHON_LOCK),
            repository_binding(PYTHON_INSTALLATION_LOCK),
        ]
        if python
        else [
            repository_binding(NODE_PACKAGE),
            repository_binding(NODE_LOCK),
            repository_binding(NODE_INSTALLER),
        ]
    )
    result_raw = (
        binding_overrides[result_path]
        if binding_overrides is not None and result_path in binding_overrides
        else result_path.read_bytes()
    )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_execution_receipt",
        "receipt_id": f"prq-002d-{role}-execution.0001",
        "suite_id": SUITE_ID,
        "implementation_id": PYTHON_ID if python else NODE_ID,
        "predecessor_checkpoint": PREDECESSOR,
        "source_manifest_binding": selected_repository_binding(
            source_path,
            binding_overrides,
        ),
        "runner_binding": repository_binding(runner_path),
        "dependency_control_bindings": controls,
        "runtime": runtime,
        "invocation": {
            "argv": argv,
            "working_directory": "repository_root",
            "environment": {
                "parent_environment_inherited": False,
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
                "PYTHONPATH_present": False,
                "NODE_OPTIONS_present": False,
            },
            "filesystem_isolation_proven": False,
        },
        "process_observation": {
            "exit_code": 0,
            "stdout_binding": {
                **raw_binding(result_raw),
                "line_count_decimal": "1",
                "framing": "single_compact_json_line_lf",
            },
            "stderr_binding": {
                "raw_sha256": "sha256:" + hashlib.sha256(b"").hexdigest(),
                "byte_count_decimal": "0",
            },
        },
        "retained_result_binding": selected_repository_binding(
            result_path,
            binding_overrides,
        ),
        "executable_unchanged_during_observation": True,
        "network_access_requested": False,
        "private_expectations_received": False,
        "peer_source_received": False,
        "peer_result_received": False,
        "self_attested_process_observation": True,
        "historical_process_independently_witnessed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def invocation_argv_valid(role: str, argv: Any, runtime_path: str) -> bool:
    if not isinstance(argv, list) or not all(
        isinstance(item, str) for item in argv
    ):
        return False
    runner = PYTHON_RUNNER if role == "python" else NODE_RUNNER
    prefix = [runtime_path, "-I", "-B"] if role == "python" else [
        runtime_path,
        "--disable-proto=throw",
    ]
    expected_suffixes = [
        runner.relative_to(ROOT).as_posix(),
        "--vectors",
        VECTORS.relative_to(ROOT).as_posix(),
        "--contract",
        CONTRACT.relative_to(ROOT).as_posix(),
        "--source-manifest",
        (
            PYTHON_SOURCE if role == "python" else NODE_SOURCE
        ).relative_to(ROOT).as_posix(),
    ]
    if len(argv) != len(prefix) + len(expected_suffixes):
        return False
    if argv[: len(prefix)] != prefix:
        return False
    observed = argv[len(prefix) :]
    for index, expected in enumerate(expected_suffixes):
        value = observed[index]
        if expected.startswith("--"):
            if value != expected:
                return False
        elif not value.endswith(expected):
            return False
    forbidden = ("cases.json", "results/python-", "results/node-")
    return not any(
        any(fragment in item for fragment in forbidden) for item in argv
    )


def execution_receipt_guard_codes(
    document: Any,
    *,
    role: str,
    binding_overrides: dict[Path, bytes] | None = None,
) -> set[str]:
    if not isinstance(document, dict):
        return {"execution_receipt_root_boundary"}
    runtime = document.get("runtime")
    family = "CPython" if role == "python" else "Node.js"
    version = PYTHON_VERSION if role == "python" else NODE_VERSION
    if (
        not isinstance(runtime, dict)
        or set(runtime) != {"family", "version", "executable"}
        or runtime.get("family") != family
        or runtime.get("version") != version
        or not isinstance(runtime.get("executable"), dict)
        or set(runtime["executable"])
        != {
            "invoked_path",
            "resolved_path",
            "raw_sha256",
            "byte_count_decimal",
        }
        or not isinstance(runtime["executable"].get("invoked_path"), str)
        or not runtime["executable"]["invoked_path"].startswith("/")
        or not isinstance(
            runtime["executable"].get("raw_sha256"),
            str,
        )
        or not SHA256_RE.fullmatch(runtime["executable"].get("raw_sha256", ""))
        or not isinstance(
            runtime["executable"].get("byte_count_decimal"),
            str,
        )
        or not DECIMAL_RE.fullmatch(
            runtime["executable"].get("byte_count_decimal", "")
        )
        or not isinstance(runtime["executable"].get("resolved_path"), str)
        or not runtime["executable"]["resolved_path"].startswith("/")
    ):
        return {"execution_runtime_shape_boundary"}
    invocation = document.get("invocation")
    if (
        not isinstance(invocation, dict)
        or set(invocation)
        != {
            "argv",
            "working_directory",
            "environment",
            "filesystem_isolation_proven",
        }
        or not invocation_argv_valid(
            role,
            invocation.get("argv"),
            runtime["executable"]["invoked_path"],
        )
    ):
        return {"answer_free_invocation_boundary"}
    expected = expected_execution_receipt(
        role,
        runtime=runtime,
        argv=invocation["argv"],
        binding_overrides=binding_overrides,
    )
    if not json_exact(document, expected):
        return {"execution_receipt_binding_boundary"}
    return set()


def validate_execution_receipt(
    errors: list[str],
    document: Any,
    *,
    role: str,
) -> None:
    for guard in sorted(execution_receipt_guard_codes(document, role=role)):
        add(errors, f"PRQ-002D {role} execution receipt guard fired: {guard}")


def expected_comparison(
    python_result: dict[str, Any],
    node_result: dict[str, Any],
    *,
    gate_summary: dict[str, str],
    fixed_private_oracle_satisfied: bool,
    source_and_language_separation_observed: bool,
    binding_overrides: dict[Path, bytes] | None = None,
) -> dict[str, Any]:
    projection = result_projection(python_result)
    node_projection = result_projection(node_result)
    projection_raw = compact_json(projection)
    accepted_count = sum(
        1
        for row in projection
        if isinstance(row, dict)
        and row.get("final_disposition") == "accepted"
    )
    refused_count = sum(
        1
        for row in projection
        if isinstance(row, dict)
        and row.get("final_disposition") == "refused"
    )
    unclassified_count = len(projection) - accepted_count - refused_count
    complete_equal = json_exact(projection, node_projection)
    gate_complete = (
        gate_summary.get("declared_count_decimal")
        == str(len(GATE_KNOWN_BADS))
        and gate_summary.get("executed_count_decimal")
        == str(len(GATE_KNOWN_BADS))
        and gate_summary.get("passed_count_decimal")
        == str(len(GATE_KNOWN_BADS))
        and gate_summary.get("failed_count_decimal") == "0"
    )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_comparison_receipt",
        "comparison_id": "prq-002d-schema-registry-prehash-comparison.0001",
        "suite_id": SUITE_ID,
        "predecessor_checkpoint": PREDECESSOR,
        "suite_manifest_binding": selected_repository_binding(
            MANIFEST,
            binding_overrides,
        ),
        "input_manifest_binding": selected_repository_binding(
            INPUT_MANIFEST,
            binding_overrides,
        ),
        "contract_binding": selected_repository_binding(
            CONTRACT,
            binding_overrides,
        ),
        "contract_schema_binding": selected_repository_binding(
            CONTRACT_SCHEMA,
            binding_overrides,
        ),
        "private_expectation_binding": selected_repository_binding(
            CASES,
            binding_overrides,
        ),
        "validator_binding": selected_repository_binding(
            VALIDATOR,
            binding_overrides,
        ),
        "execution_receipt_bindings": [
            {
                "role": "python",
                **selected_repository_binding(
                    PYTHON_EXECUTION,
                    binding_overrides,
                ),
            },
            {
                "role": "node",
                **selected_repository_binding(
                    NODE_EXECUTION,
                    binding_overrides,
                ),
            },
        ],
        "compared_result_bindings": [
            {
                "role": "python",
                **selected_repository_binding(
                    PYTHON_RESULT,
                    binding_overrides,
                ),
            },
            {
                "role": "node",
                **selected_repository_binding(
                    NODE_RESULT,
                    binding_overrides,
                ),
            },
        ],
        "projection_serialization": "ascii_key_sorted_compact_json",
        "projection_raw_sha256": raw_binding(projection_raw)["raw_sha256"],
        "projection_byte_count_decimal": str(len(projection_raw)),
        "measured_census": {
            "vector_count_decimal": str(len(projection)),
            "accepted_count_decimal": str(accepted_count),
            "refused_count_decimal": str(refused_count),
            "unclassified_error_count_decimal": str(unclassified_count),
            "source_separated_implementation_count_decimal": "2",
            "gate_known_bad_count_decimal": str(len(GATE_KNOWN_BADS)),
        },
        "complete_ordered_projection_equal": complete_equal,
        "fixed_private_oracle_satisfied": fixed_private_oracle_satisfied,
        "source_and_language_separation_observed": (
            source_and_language_separation_observed
        ),
        "organizational_independence_proven": False,
        "independent_host_reproduction_complete": False,
        "historical_process_independently_witnessed": False,
        "gate_self_test_summary": gate_summary,
        "bounded_gate_known_bad_self_test_complete": gate_complete,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def comparison_projection_guard_codes(
    comparison: Any,
    python_result: Any,
    node_result: Any,
) -> set[str]:
    if not all(
        isinstance(item, dict)
        for item in (comparison, python_result, node_result)
    ):
        return {"complete_projection_comparison"}
    python_projection = result_projection(python_result)
    node_projection = result_projection(node_result)
    raw = compact_json(python_projection)
    if not json_exact(python_projection, node_projection):
        return {"source_projection_type_exactness_boundary"}
    if (
        comparison.get("projection_raw_sha256")
        != raw_binding(raw)["raw_sha256"]
        or comparison.get("projection_byte_count_decimal") != str(len(raw))
        or comparison.get("complete_ordered_projection_equal") is not True
    ):
        return {"complete_projection_comparison"}
    return set()


def comparison_receipt_guard_codes(
    comparison: Any,
    python_result: Any,
    node_result: Any,
    *,
    gate_summary: dict[str, str],
    fixed_private_oracle_satisfied: bool,
    source_and_language_separation_observed: bool,
    binding_overrides: dict[Path, bytes] | None = None,
) -> set[str]:
    if not all(
        isinstance(item, dict)
        for item in (comparison, python_result, node_result)
    ):
        return {"comparison_receipt_binding_boundary"}
    try:
        expected = expected_comparison(
            python_result,
            node_result,
            gate_summary=gate_summary,
            fixed_private_oracle_satisfied=fixed_private_oracle_satisfied,
            source_and_language_separation_observed=(
                source_and_language_separation_observed
            ),
            binding_overrides=binding_overrides,
        )
    except (OSError, TypeError, ValueError):
        return {"comparison_receipt_binding_boundary"}
    return (
        set()
        if json_exact(comparison, expected)
        else {"comparison_receipt_binding_boundary"}
    )


def validate_comparison(
    errors: list[str],
    comparison: Any,
    python_result: Any,
    node_result: Any,
    *,
    gate_summary: dict[str, str],
    fixed_private_oracle_satisfied: bool,
    source_and_language_separation_observed: bool,
) -> None:
    if not all(
        isinstance(item, dict)
        for item in (comparison, python_result, node_result)
    ):
        return
    for guard in sorted(
        comparison_projection_guard_codes(
            comparison,
            python_result,
            node_result,
        )
    ):
        add(errors, f"PRQ-002D comparison guard fired: {guard}")
    for guard in sorted(
        comparison_receipt_guard_codes(
            comparison,
            python_result,
            node_result,
            gate_summary=gate_summary,
            fixed_private_oracle_satisfied=fixed_private_oracle_satisfied,
            source_and_language_separation_observed=(
                source_and_language_separation_observed
            ),
        )
    ):
        add(errors, f"PRQ-002D retained comparison guard fired: {guard}")


def expected_manifest() -> dict[str, Any]:
    expected_paths = {
        "input_manifest": INPUT_MANIFEST.relative_to(ROOT).as_posix(),
        "vectors": VECTORS.relative_to(ROOT).as_posix(),
        "private_expectations": CASES.relative_to(ROOT).as_posix(),
        "contract": CONTRACT.relative_to(ROOT).as_posix(),
        "contract_schema": CONTRACT_SCHEMA.relative_to(ROOT).as_posix(),
        "python_source_manifest": PYTHON_SOURCE.relative_to(ROOT).as_posix(),
        "node_source_manifest": NODE_SOURCE.relative_to(ROOT).as_posix(),
        "python_result": PYTHON_RESULT.relative_to(ROOT).as_posix(),
        "node_result": NODE_RESULT.relative_to(ROOT).as_posix(),
        "python_execution_receipt": PYTHON_EXECUTION.relative_to(ROOT).as_posix(),
        "node_execution_receipt": NODE_EXECUTION.relative_to(ROOT).as_posix(),
        "comparison_receipt": COMPARISON.relative_to(ROOT).as_posix(),
        "validator": VALIDATOR.relative_to(ROOT).as_posix(),
    }
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_suite_manifest",
        "suite_id": SUITE_ID,
        "status": "architecture_only_non_product_nonidentity_observation",
        "decision_ref": (
            "docs/decisions/"
            "0102-prove-non-product-prehash-schema-registry-replay.md"
        ),
        "census": {
            "vector_count_decimal": str(len(EXPECTED_CODES)),
            "accepted_count_decimal": "1",
            "refused_count_decimal": str(len(EXPECTED_CODES) - 1),
            "source_separated_implementation_count_decimal": "2",
            "gate_known_bad_count_decimal": str(len(GATE_KNOWN_BADS)),
        },
        "retained_paths": expected_paths,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def manifest_guard_codes(document: Any) -> set[str]:
    return (
        set()
        if isinstance(document, dict)
        and json_exact(document, expected_manifest())
        else {"suite_manifest_boundary"}
    )


def validate_manifest(errors: list[str], document: Any) -> None:
    if manifest_guard_codes(document):
        add(errors, "PRQ-002D suite manifest drifted")


def expected_gate_rows() -> list[dict[str, str]]:
    return [
        {"id": identifier, "mutation": mutation, "expected_guard": guard}
        for identifier, (mutation, guard) in GATE_KNOWN_BADS.items()
    ]


def build_gate_state(
    *,
    cases: Any,
    contract: Any,
    input_manifest: Any,
    manifest: Any,
    python_source: Any,
    node_source: Any,
    python_result: Any,
    node_result: Any,
    python_execution: Any,
    node_execution: Any,
    comparison: Any,
    binding_overrides: dict[Path, bytes] | None = None,
) -> dict[str, Any]:
    files, symlinks = inventory()
    return {
        "cases": cases,
        "contract": contract,
        "contract_schema": load(
            CONTRACT_SCHEMA,
            [],
            "PRQ-002D contract schema",
        ),
        "vectors": load(VECTORS, [], "PRQ-002D vectors"),
        "input_manifest": input_manifest,
        "manifest": manifest,
        "python_source_manifest": python_source,
        "node_source_manifest": node_source,
        "python_result": python_result,
        "node_result": node_result,
        "python_execution": python_execution,
        "node_execution": node_execution,
        "comparison": comparison,
        "binding_overrides": binding_overrides,
        "python_bytes": PYTHON_RUNNER.read_bytes(),
        "node_bytes": NODE_RUNNER.read_bytes(),
        "python_result_raw": (
            binding_overrides[PYTHON_RESULT]
            if binding_overrides is not None
            and PYTHON_RESULT in binding_overrides
            else PYTHON_RESULT.read_bytes()
        ),
        "node_result_raw": (
            binding_overrides[NODE_RESULT]
            if binding_overrides is not None
            and NODE_RESULT in binding_overrides
            else NODE_RESULT.read_bytes()
        ),
        "predecessor_repository": observe_predecessor_repository(),
        "python_lock": load(PYTHON_LOCK, [], "PRQ-002D Python lock"),
        "node_package": load(NODE_PACKAGE, [], "PRQ-002D Node package"),
        "node_lock": load(NODE_LOCK, [], "PRQ-002D Node lock"),
        "inventory_files": files,
        "inventory_symlinks": symlinks,
    }


def state_result_guard_codes(
    state: dict[str, Any],
    document: Any,
    *,
    role: str,
    vectors: Any | None = None,
) -> set[str]:
    return result_guard_codes(
        document,
        role=role,
        source_manifest=PYTHON_SOURCE if role == "python" else NODE_SOURCE,
        vectors=state["vectors"] if vectors is None else vectors,
        cases=state["cases"],
        contract=state["contract"],
        binding_overrides=state.get("binding_overrides"),
    )


def gate_baseline_guard_sets(state: dict[str, Any]) -> dict[str, set[str]]:
    python_result = state["python_result"]
    node_result = state["node_result"]
    guards = {
        "source_text": source_text_guard_codes(
            state["python_bytes"],
            state["node_bytes"],
        ),
        "python_source_manifest": source_manifest_guard_codes(
            "python",
            state["python_source_manifest"],
        ),
        "node_source_manifest": source_manifest_guard_codes(
            "node",
            state["node_source_manifest"],
        ),
        "dependency": dependency_guard_codes(
            state["python_lock"],
            state["node_package"],
            state["node_lock"],
        ),
        "contract": contract_evidence_guard_codes(state["contract"]),
        "contract_schema": contract_schema_guard_codes(
            state["contract_schema"],
            state["contract"],
        ),
        "contract_fixtures": contract_fixture_guard_codes(state["contract"]),
        "contract_preparse_bindings": contract_preparse_binding_guard_codes(
            state["contract"],
            state["vectors"],
        ),
        "predecessor_repository": predecessor_repository_guard_codes(
            state["predecessor_repository"]
        ),
        "input_manifest": input_manifest_guard_codes(state["input_manifest"]),
        "cases": cases_shape_guard_codes(state["cases"]),
        "private_expectations": private_expectation_inventory_guard_codes(
            state["cases"]
        ),
        "vectors": vector_inventory_guard_codes(state["vectors"]),
        "safe_vector": safe_vector_binding_guard_codes(state["vectors"]),
        "suite_manifest": manifest_guard_codes(state["manifest"]),
        "python_result": state_result_guard_codes(
            state,
            python_result,
            role="python",
        ),
        "node_result": state_result_guard_codes(
            state,
            node_result,
            role="node",
        ),
        "python_result_framing": result_framing_guard_codes(
            python_result,
            state["python_result_raw"],
        ),
        "node_result_framing": result_framing_guard_codes(
            node_result,
            state["node_result_raw"],
        ),
        "comparison_projection": comparison_projection_guard_codes(
            state["comparison"],
            python_result,
            node_result,
        ),
        "inventory": inventory_guard_codes(
            state["inventory_files"],
            state["inventory_symlinks"],
        ),
        "retained_python_process": child_process_guard_codes(
            0,
            PYTHON_RESULT.read_bytes(),
            b"",
        )[0],
        "python_execution": execution_receipt_guard_codes(
            state["python_execution"],
            role="python",
            binding_overrides=state.get("binding_overrides"),
        ),
        "node_execution": execution_receipt_guard_codes(
            state["node_execution"],
            role="node",
            binding_overrides=state.get("binding_overrides"),
        ),
    }
    gate_summary, _ = expected_gate_self_test(state["cases"])
    guards["comparison_receipt"] = comparison_receipt_guard_codes(
        state["comparison"],
        python_result,
        node_result,
        gate_summary=gate_summary,
        fixed_private_oracle_satisfied=fixed_private_oracle_satisfied(
            state,
            state["vectors"],
        ),
        source_and_language_separation_observed=(
            source_and_language_separation_observed(state)
        ),
        binding_overrides=state.get("binding_overrides"),
    )
    return guards


def execute_gate_mutation(
    mutation: str,
    state: dict[str, Any],
) -> set[str]:
    python_text = state["python_bytes"].decode("utf-8")
    node_text = state["node_bytes"].decode("utf-8")
    if mutation == "name_private_expectation_path_in_source":
        python_text += "\n# schema-registry-prehash-replay/cases.json\n"
        return source_text_guard_codes(python_text, node_text)
    if mutation == "pass_private_expectation_path_to_child":
        receipt = copy.deepcopy(state["python_execution"])
        receipt["invocation"]["argv"].append(CASES.resolve().as_posix())
        return execution_receipt_guard_codes(
            receipt,
            role="python",
            binding_overrides=state.get("binding_overrides"),
        )
    if mutation == "name_peer_runner_in_source":
        python_text += "\n# node/runner.mjs\n"
        return source_text_guard_codes(python_text, node_text)
    if mutation == "name_peer_result_in_source":
        python_text += "\n# results/node-ajv2020.json\n"
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_network_module_or_fetch":
        node_text += '\nimport { request } from "node:https";\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_comment_separated_dynamic_network_import":
        node_text += '\nimport /* capability gap */ ("node:https");\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_node_side_effect_import":
        node_text += '\nimport "unreviewed-capability";\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_comment_separated_node_require":
        node_text += '\nrequire /* capability gap */ ("unreviewed-capability");\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_node_variable_require":
        node_text += '\nconst capabilityName = "unreviewed"; require(capabilityName);\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_comment_separated_node_import_call":
        node_text += '\nimport /* capability gap */ ("unreviewed-capability");\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_python_builtins_attribute_import":
        python_text += '\n__builtins__.__import__("urllib.request")\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_python_builtins_subscript_import":
        python_text += '\n__builtins__["__import__"]("urllib.request")\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "alias_python_dynamic_import":
        python_text += '\nf = __import__\nf("urllib.request")\n'
        return source_text_guard_codes(python_text, node_text)
    if mutation == "add_python_importlib_dict_import":
        python_text += (
            '\nimportlib.__dict__["import_module"]("urllib.request")\n'
        )
        return source_text_guard_codes(python_text, node_text)
    if mutation == "make_python_source_unparseable":
        return source_text_guard_codes(python_text + "\n(\n", node_text)
    if mutation == "replace_python_runner_lf_with_crlf":
        return source_text_guard_codes(
            state["python_bytes"].replace(b"\n", b"\r\n"),
            state["node_bytes"],
        )
    if mutation == "remove_python_retrieval_deny":
        python_text = python_text.replace(
            "Registry(retrieve=deny_retrieve)",
            "Registry(retrieve=None)",
            1,
        )
        return source_text_guard_codes(python_text, node_text)
    if mutation == "remove_node_strict_resolver_control":
        node_text = node_text.replace(
            "loadSchema: undefined",
            "loadSchema: async () => ({})",
            1,
        )
        return source_text_guard_codes(python_text, node_text)
    if mutation == "replace_runner_digest_in_source_manifest":
        manifest = copy.deepcopy(state["python_source_manifest"])
        manifest["source_files"][0]["raw_sha256"] = "sha256:" + "0" * 64
        return source_manifest_guard_codes("python", manifest)
    if mutation == "replace_pinned_dependency_version":
        python_lock = copy.deepcopy(state["python_lock"])
        python_lock["third_party_distributions"][0]["version"] = "0.0.0"
        return dependency_guard_codes(
            python_lock,
            state["node_package"],
            state["node_lock"],
        )
    if mutation == "add_unlocked_node_package":
        package = copy.deepcopy(state["node_package"])
        package["dependencies"]["unreviewed-capability"] = "1.0.0"
        return dependency_guard_codes(
            state["python_lock"],
            package,
            state["node_lock"],
        )
    if mutation == "add_authority_field_to_result_root":
        result = copy.deepcopy(state["python_result"])
        result["authority"] = True
        return state_result_guard_codes(
            state,
            result,
            role="python",
        )
    if mutation == "replace_result_vector_count":
        result = copy.deepcopy(state["python_result"])
        result["vector_count_decimal"] = "0"
        return state_result_guard_codes(
            state,
            result,
            role="python",
        )
    if mutation == "replace_result_contract_binding":
        result = copy.deepcopy(state["python_result"])
        result["input_bindings"]["contract"]["raw_sha256"] = (
            "sha256:" + "0" * 64
        )
        return state_result_guard_codes(
            state,
            result,
            role="python",
        )
    if mutation in {
        "drop_last_observation",
        "swap_first_two_observations",
        "add_authority_field_to_result_row",
        "flip_one_final_code",
        "replace_result_bundle_raw_sha256",
        "replace_result_bundle_byte_count_decimal",
        "replace_result_declared_member_count_raw_token",
        "replace_accepted_member_order",
        "replace_accepted_replay_binding",
        "replace_accepted_validated_probe_count",
        "invent_refused_observation",
    }:
        result = copy.deepcopy(state["python_result"])
        rows = result["results"]
        if mutation == "drop_last_observation":
            rows.pop()
        elif mutation == "swap_first_two_observations":
            rows[0], rows[1] = rows[1], rows[0]
        elif mutation == "add_authority_field_to_result_row":
            rows[0]["authority"] = True
        elif mutation == "flip_one_final_code":
            rows[1]["final_code"] = "ODEYA_PREHASH_REPLAY_ACCEPTED"
        elif mutation == "replace_result_bundle_raw_sha256":
            rows[0]["bundle_raw_sha256"] = "sha256:" + "0" * 64
        elif mutation == "replace_result_bundle_byte_count_decimal":
            rows[1]["bundle_byte_count_decimal"] = "0"
        elif mutation == "replace_result_declared_member_count_raw_token":
            rows[1]["declared_member_count_raw_token"] = "999"
        elif mutation == "replace_accepted_member_order":
            rows[0]["ordered_member_keys"].reverse()
        elif mutation == "replace_accepted_replay_binding":
            rows[0]["resolved_replay_bindings"][0][
                "resource_raw_sha256"
            ] = "sha256:" + "0" * 64
        elif mutation == "replace_accepted_validated_probe_count":
            rows[0]["validated_probe_count_decimal"] = "3"
        else:
            rows[1]["ordered_member_keys"] = ["invented@0.0.0"]
        return state_result_guard_codes(
            state,
            result,
            role="python",
        )
    if mutation == "replace_vectors_with_malformed_oracle_input":
        return state_result_guard_codes(
            state,
            state["python_result"],
            role="python",
            vectors={},
        )
    if mutation == "append_blank_line_to_retained_result":
        return result_framing_guard_codes(
            state["python_result"],
            state["python_result_raw"] + b"\n",
        )
    if mutation in {
        "replace_projection_digest",
        "replace_projection_equal_true_with_zero",
    }:
        comparison = copy.deepcopy(state["comparison"])
        if mutation == "replace_projection_digest":
            comparison["projection_raw_sha256"] = "sha256:" + "0" * 64
        else:
            comparison["complete_ordered_projection_equal"] = 0
        return comparison_projection_guard_codes(
            comparison,
            state["python_result"],
            state["node_result"],
        )
    if mutation == "replace_node_projection_false_with_zero":
        node_result = copy.deepcopy(state["node_result"])
        node_result["results"][1]["validated_probe_count_decimal"] = 0
        return comparison_projection_guard_codes(
            state["comparison"],
            state["python_result"],
            node_result,
        )
    if mutation == "set_comparison_organizational_independence_true":
        comparison = copy.deepcopy(state["comparison"])
        comparison["organizational_independence_proven"] = True
        gate_summary, _ = expected_gate_self_test(state["cases"])
        return comparison_receipt_guard_codes(
            comparison,
            state["python_result"],
            state["node_result"],
            gate_summary=gate_summary,
            fixed_private_oracle_satisfied=fixed_private_oracle_satisfied(
                state,
                state["vectors"],
            ),
            source_and_language_separation_observed=(
                source_and_language_separation_observed(state)
            ),
            binding_overrides=state.get("binding_overrides"),
        )
    if mutation in {
        "set_gate_a_complete_true_in_result",
        "set_product_identity_computed_true_in_result",
        "set_gate_a_complete_to_numeric_zero",
    }:
        result = copy.deepcopy(state["python_result"])
        if mutation == "set_gate_a_complete_true_in_result":
            result["claim_boundary"]["gate_a_complete"] = True
        elif mutation == "set_product_identity_computed_true_in_result":
            result["claim_boundary"]["product_identity_computed"] = True
        else:
            result["claim_boundary"]["gate_a_complete"] = 0
        return state_result_guard_codes(
            state,
            result,
            role="python",
        )
    if mutation in {
        "replace_contract_safe_bundle_digest",
        "replace_predecessor_evidence_digest",
        "duplicate_contract_resource_id",
        "set_contract_runtime_authorized_true",
        "set_contract_gate_a_complete_true",
    }:
        contract = copy.deepcopy(state["contract"])
        if mutation == "replace_contract_safe_bundle_digest":
            contract["safe_bundle_binding"]["raw_sha256"] = (
                "sha256:" + "0" * 64
            )
        elif mutation == "replace_predecessor_evidence_digest":
            contract["predecessor_evidence_bindings"][0]["raw_sha256"] = (
                "sha256:" + "0" * 64
            )
        elif mutation == "duplicate_contract_resource_id":
            contract["expected_resources"][1]["schema_id"] = contract[
                "expected_resources"
            ][0]["schema_id"]
        elif mutation == "set_contract_runtime_authorized_true":
            contract["authority_boundary"]["runtime_authorized"] = True
        else:
            contract["claim_boundary"]["gate_a_complete"] = True
        return contract_evidence_guard_codes(contract)
    if mutation == "replace_observed_predecessor_tree":
        observation = copy.deepcopy(state["predecessor_repository"])
        observation["checkpoint"]["tree"] = "0" * 40
        return predecessor_repository_guard_codes(observation)
    if mutation in {
        "replace_safe_bundle_digest_with_null",
        "replace_contract_id",
        "add_forbidden_member_digest",
    }:
        contract = copy.deepcopy(state["contract"])
        if mutation == "replace_safe_bundle_digest_with_null":
            contract["safe_bundle_binding"]["raw_sha256"] = None
        elif mutation == "replace_contract_id":
            contract["contract_id"] = CONTRACT_ID + ":substituted"
        else:
            contract["member_digest"] = "sha256:" + "0" * 64
        return contract_schema_guard_codes(
            state["contract_schema"],
            contract,
        )
    if mutation in {
        "remove_contract_schema_root_closedness",
        "remove_contract_schema_nested_closedness",
        "replace_contract_schema_object_type_with_array_and_remove_closedness",
        "remove_contract_schema_object_type_and_closedness",
    }:
        contract_schema = copy.deepcopy(state["contract_schema"])
        if mutation == "remove_contract_schema_root_closedness":
            contract_schema.pop("additionalProperties", None)
        elif mutation == "remove_contract_schema_nested_closedness":
            contract_schema["$defs"]["resource_binding"].pop(
                "additionalProperties",
                None,
            )
        elif (
            mutation
            == "replace_contract_schema_object_type_with_array_and_remove_closedness"
        ):
            contract_schema["type"] = ["object"]
            contract_schema.pop("additionalProperties", None)
        else:
            contract_schema["$defs"]["resource_binding"].pop("type", None)
            contract_schema["$defs"]["resource_binding"].pop(
                "additionalProperties",
                None,
            )
        return contract_schema_guard_codes(
            contract_schema,
            state["contract"],
        )
    if mutation == "replace_contract_resource_fixture_digest":
        contract = copy.deepcopy(state["contract"])
        contract["expected_resources"][0]["resource_raw_sha256"] = (
            "sha256:" + "0" * 64
        )
        return contract_fixture_guard_codes(contract)
    if mutation in {
        "remove_contract_resource_override",
        "add_contract_resource_override_field",
        "add_contract_resource_override",
        "replace_contract_probe_override_digest",
        "replace_override_vector_resource_bytes",
    }:
        contract = copy.deepcopy(state["contract"])
        vectors = state["vectors"]
        if mutation == "remove_contract_resource_override":
            contract["preparse_resource_binding_overrides"].pop()
        elif mutation == "add_contract_resource_override_field":
            contract["preparse_resource_binding_overrides"][0][
                "authority"
            ] = True
        elif mutation == "add_contract_resource_override":
            contract["preparse_resource_binding_overrides"].append(
                copy.deepcopy(
                    contract["preparse_resource_binding_overrides"][-1]
                )
            )
        elif mutation == "replace_contract_probe_override_digest":
            contract["preparse_probe_binding_overrides"][0][
                "probe_raw_sha256"
            ] = "sha256:" + "0" * 64
        else:
            vectors = copy.deepcopy(state["vectors"])
            vector = next(
                row
                for row in vectors["vectors"]
                if row["vector_id"] == RESOURCE_OVERRIDE_VECTOR_IDS[0]
            )
            resource = next(
                row
                for row in vector["files"]
                if row["blob_id"] == "resource-001"
            )
            substituted = (
                base64.b64decode(resource["content_base64"], validate=True)
                + b" "
            )
            resource["content_base64"] = base64.b64encode(
                substituted
            ).decode("ascii")
            resource.update(raw_binding(substituted))
        return contract_preparse_binding_guard_codes(
            contract,
            vectors,
        )
    if mutation == "replace_contract_with_non_object":
        return contract_evidence_guard_codes(None)
    if mutation == "replace_input_manifest_binding":
        document = copy.deepcopy(state["input_manifest"])
        document["bindings"][0]["raw_sha256"] = "sha256:" + "0" * 64
        return input_manifest_guard_codes(document)
    if mutation == "add_authority_field_to_cases_root":
        document = copy.deepcopy(state["cases"])
        document["authority"] = True
        return cases_shape_guard_codes(document)
    if mutation == "replace_private_expected_code":
        document = copy.deepcopy(state["cases"])
        document["cases"][1]["expected_code"] = (
            "ODEYA_PREHASH_REPLAY_ACCEPTED"
        )
        return private_expectation_inventory_guard_codes(document)
    if mutation == "add_authority_field_to_vector_root":
        document = copy.deepcopy(state["vectors"])
        document["authority"] = True
        return vector_inventory_guard_codes(document)
    if mutation == "replace_safe_vector_fixture_digest":
        document = copy.deepcopy(state["vectors"])
        safe_bundle = next(
            row
            for row in document["vectors"][0]["files"]
            if row["blob_id"] == "bundle"
        )
        substituted = b"{}"
        safe_bundle["content_base64"] = base64.b64encode(
            substituted
        ).decode("ascii")
        safe_bundle.update(raw_binding(substituted))
        return safe_vector_binding_guard_codes(document)
    if mutation == "add_authority_field_to_suite_manifest":
        document = copy.deepcopy(state["manifest"])
        document["authority"] = True
        return manifest_guard_codes(document)
    if mutation == "add_untracked_suite_file":
        return inventory_guard_codes(
            state["inventory_files"] | {"unexpected.json"},
            state["inventory_symlinks"],
        )
    if mutation == "add_suite_symlink":
        return inventory_guard_codes(
            state["inventory_files"],
            state["inventory_symlinks"] | {"fixtures/symlink.json"},
        )
    if mutation == "replace_result_with_non_json_process_output":
        return child_process_guard_codes(0, b"not-json\n", b"")[0]
    if mutation == "replace_execution_receipt_with_non_object":
        return execution_receipt_guard_codes(
            None,
            role="python",
            binding_overrides=state.get("binding_overrides"),
        )
    if mutation == "add_execution_runtime_field":
        receipt = copy.deepcopy(state["python_execution"])
        receipt["runtime"]["authority"] = True
        return execution_receipt_guard_codes(
            receipt,
            role="python",
            binding_overrides=state.get("binding_overrides"),
        )
    if mutation == "replace_execution_runtime_digest_with_null":
        receipt = copy.deepcopy(state["python_execution"])
        receipt["runtime"]["executable"]["raw_sha256"] = None
        return execution_receipt_guard_codes(
            receipt,
            role="python",
            binding_overrides=state.get("binding_overrides"),
        )
    if mutation == "replace_execution_stdout_digest":
        receipt = copy.deepcopy(state["python_execution"])
        receipt["process_observation"]["stdout_binding"]["raw_sha256"] = (
            "sha256:" + "0" * 64
        )
        return execution_receipt_guard_codes(
            receipt,
            role="python",
            binding_overrides=state.get("binding_overrides"),
        )
    return {"unknown_gate_mutation_boundary"}


def summarize_gate_self_test_rows(
    declared_count: int,
    rows: list[dict[str, Any]],
) -> dict[str, str]:
    encoded = compact_json(rows)
    passed_count = sum(row["passed"] is True for row in rows)
    return {
        "declared_count_decimal": str(declared_count),
        "executed_count_decimal": str(len(rows)),
        "passed_count_decimal": str(passed_count),
        "failed_count_decimal": str(len(rows) - passed_count),
        "ordered_result_raw_sha256": raw_binding(encoded)["raw_sha256"],
        "ordered_result_byte_count_decimal": str(len(encoded)),
    }


def expected_gate_self_test(
    cases: Any,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    declared = (
        cases.get("gate_known_bads")
        if isinstance(cases, dict)
        and isinstance(cases.get("gate_known_bads"), list)
        else []
    )
    rows = [
        {
            "id": row.get("id") if isinstance(row, dict) else None,
            "mutation": row.get("mutation") if isinstance(row, dict) else None,
            "expected_guard": (
                row.get("expected_guard") if isinstance(row, dict) else None
            ),
            "observed_guards": (
                [row["expected_guard"]]
                if isinstance(row, dict)
                and isinstance(row.get("expected_guard"), str)
                else []
            ),
            "passed": (
                isinstance(row, dict)
                and isinstance(row.get("expected_guard"), str)
            ),
        }
        for row in declared
    ]
    return summarize_gate_self_test_rows(len(declared), rows), rows


def observed_gate_self_test(
    cases: Any,
    state: dict[str, Any],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    declared = (
        cases.get("gate_known_bads")
        if isinstance(cases, dict)
        and isinstance(cases.get("gate_known_bads"), list)
        else []
    )
    rows: list[dict[str, Any]] = []
    for row in declared:
        identifier = row.get("id") if isinstance(row, dict) else None
        mutation = row.get("mutation") if isinstance(row, dict) else None
        expected_guard = (
            row.get("expected_guard") if isinstance(row, dict) else None
        )
        try:
            observed = (
                execute_gate_mutation(mutation, state)
                if isinstance(mutation, str)
                else {"unknown_gate_mutation_boundary"}
            )
        except Exception:
            observed = {"gate_self_test_unhandled_exception_boundary"}
        passed = (
            isinstance(expected_guard, str)
            and observed == {expected_guard}
        )
        rows.append(
            {
                "id": identifier,
                "mutation": mutation,
                "expected_guard": expected_guard,
                "observed_guards": sorted(observed),
                "passed": passed,
            }
        )
    return summarize_gate_self_test_rows(len(declared), rows), rows


def validate_gate_self_tests(
    errors: list[str],
    state: dict[str, Any],
) -> dict[str, str]:
    observed_gate_rows = (
        state["cases"].get("gate_known_bads")
        if isinstance(state.get("cases"), dict)
        else None
    )
    if not json_exact(observed_gate_rows, expected_gate_rows()):
        add(errors, "PRQ-002D gate self-test declaration inventory drifted")
    for component, guards in gate_baseline_guard_sets(state).items():
        if guards:
            add(
                errors,
                "PRQ-002D gate self-test baseline is not clean for "
                f"{component}: {', '.join(sorted(guards))}",
            )
    expected_summary, expected_rows = expected_gate_self_test(state["cases"])
    observed_summary, observed_rows = observed_gate_self_test(
        state["cases"],
        state,
    )
    if not json_exact(observed_summary, expected_summary):
        add(errors, "PRQ-002D gate self-test summary differs from all-pass oracle")
    for row in observed_rows:
        if row["passed"] is not True:
            add(
                errors,
                "PRQ-002D gate self-test failed "
                f"{row['id']}: expected {row['expected_guard']}, observed "
                f"{','.join(row['observed_guards']) or '<none>'}",
            )
    if not json_exact(observed_rows, expected_rows):
        add(errors, "PRQ-002D gate self-test ordered rows differ from oracle")
    return expected_summary


def executable_observation(executable: Path) -> dict[str, str]:
    invoked = (
        executable
        if executable.is_absolute()
        else ROOT / executable
    ).absolute()
    resolved = invoked.resolve(strict=True)
    return {
        "invoked_path": invoked.as_posix(),
        "resolved_path": resolved.as_posix(),
        **raw_binding(resolved.read_bytes()),
    }


def child_process_guard_codes(
    returncode: int,
    stdout: bytes,
    stderr: bytes,
) -> tuple[set[str], Any]:
    if (
        returncode != 0
        or stderr != b""
        or not stdout.endswith(b"\n")
        or stdout.count(b"\n") != 1
    ):
        return {"classified_execution_boundary"}, None
    try:
        document = json.loads(
            stdout[:-1],
            object_pairs_hook=strict_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite token {token}")
            ),
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        DuplicateKey,
        ValueError,
    ):
        return {"classified_execution_boundary"}, None
    if not isinstance(document, dict):
        return {"classified_execution_boundary"}, None
    return set(), document


def execute_child(
    executable: Path,
    runner: Path,
    source_manifest: Path,
    *,
    node: bool,
) -> dict[str, Any]:
    before = executable_observation(executable)
    executable_path = before["invoked_path"]
    command = [
        executable_path,
        *(
            ["--disable-proto=throw"]
            if node
            else ["-I", "-B"]
        ),
        runner.resolve(strict=True).as_posix(),
        "--vectors",
        VECTORS.resolve(strict=True).as_posix(),
        "--contract",
        CONTRACT.resolve(strict=True).as_posix(),
        "--source-manifest",
        source_manifest.resolve(strict=True).as_posix(),
    ]
    environment = {
        "PATH": Path(executable_path).parent.as_posix(),
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONHASHSEED": "0",
    }
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        timeout=60,
    )
    after = executable_observation(executable)
    if before != after:
        raise RuntimeError("selected executable changed during child execution")
    guards, document = child_process_guard_codes(
        result.returncode,
        result.stdout,
        result.stderr,
    )
    if guards:
        raise RuntimeError(
            "child process boundary refused output "
            f"(exit={result.returncode}, stdout={len(result.stdout)}, "
            f"stderr={len(result.stderr)})"
        )
    return {
        "document": document,
        "stdout": result.stdout,
        "argv": command,
        "runtime": {
            "family": "Node.js" if node else "CPython",
            "version": NODE_VERSION if node else PYTHON_VERSION,
            "executable": before,
        },
    }


def run_child(
    executable: Path,
    runner: Path,
    source_manifest: Path,
    *,
    node: bool,
) -> dict[str, Any]:
    return execute_child(
        executable,
        runner,
        source_manifest,
        node=node,
    )["document"]


def validate_runtime_selection(
    python_executable: Path,
    node_executable: Path,
) -> list[str]:
    errors: list[str] = []
    try:
        if python_executable.resolve(strict=True) != PARENT_EXECUTABLE:
            errors.append(
                "selected CPython must resolve to the startup-bound checker image"
            )
        installed = subprocess.run(
            ["bash", NODE_INSTALLER.relative_to(ROOT).as_posix()],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if installed.returncode != 0:
            errors.append("pinned Node installer returned nonzero")
        else:
            installer_product = Path(installed.stdout.strip()).resolve(strict=True)
            if node_executable.resolve(strict=True) != installer_product:
                errors.append("selected Node.js is not the pinned installer product")
        python_version = subprocess.run(
            [
                python_executable.resolve(strict=True).as_posix(),
                "-I",
                "-B",
                "-c",
                "import platform; print(platform.python_version())",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env={
                "PATH": python_executable.resolve().parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        ).stdout.strip()
        node_path = node_executable.resolve(strict=True)
        node_version = subprocess.run(
            [node_path.as_posix(), "-p", "process.versions.node"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env={
                "PATH": node_path.parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        ).stdout.strip()
        npm_cli = (
            node_path.parent.parent
            / "lib/node_modules/npm/bin/npm-cli.js"
        )
        npm_version = subprocess.run(
            [node_path.as_posix(), npm_cli.as_posix(), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env={
                "PATH": node_path.parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return [f"runtime selection failed: {type(exc).__name__}: {exc}"]
    if python_version != PYTHON_VERSION:
        errors.append(
            f"requires CPython {PYTHON_VERSION}, received {python_version}"
        )
    if node_version != NODE_VERSION:
        errors.append(f"requires Node.js {NODE_VERSION}, received {node_version}")
    if npm_version != NPM_VERSION:
        errors.append(f"requires npm {NPM_VERSION}, received {npm_version}")
    return errors


def recompute(
    errors: list[str],
    python_executable: Path,
    node_executable: Path,
    python_result: Any,
    node_result: Any,
) -> None:
    for error in validate_runtime_selection(
        python_executable,
        node_executable,
    ):
        add(errors, f"PRQ-002D {error}")
    if errors:
        return
    with tempfile.TemporaryDirectory(prefix="odeya-prq002d-") as directory:
        regenerated = Path(directory) / "vectors.json"
        generated = subprocess.run(
            [
                python_executable.resolve(strict=True).as_posix(),
                "-I",
                "-B",
                str(GENERATOR),
                "--output",
                str(regenerated),
            ],
            cwd=ROOT,
            env={
                "PATH": python_executable.resolve().parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
            capture_output=True,
            timeout=30,
            check=False,
        )
        if (
            generated.returncode != 0
            or generated.stdout
            or generated.stderr
            or not regenerated.is_file()
            or regenerated.read_bytes() != VECTORS.read_bytes()
        ):
            add(errors, "PRQ-002D answer-free vector regeneration differs")
    try:
        fresh_python = run_child(
            python_executable,
            PYTHON_RUNNER,
            PYTHON_SOURCE,
            node=False,
        )
        fresh_node = run_child(
            node_executable,
            NODE_RUNNER,
            NODE_SOURCE,
            node=True,
        )
    except (OSError, subprocess.SubprocessError, RuntimeError, json.JSONDecodeError) as exc:
        add(errors, f"PRQ-002D fresh child execution failed: {type(exc).__name__}: {exc}")
        return
    if not isinstance(python_result, dict) or not isinstance(node_result, dict):
        return
    if fresh_python != python_result:
        add(errors, "PRQ-002D fresh Python observation differs from retained result")
    if fresh_node != node_result:
        add(errors, "PRQ-002D fresh Node observation differs from retained result")
    if fresh_python.get("results") != fresh_node.get("results"):
        add(errors, "PRQ-002D fresh source-separated projections disagree")


def fixed_private_oracle_satisfied(
    state: dict[str, Any],
    vectors: Any,
) -> bool:
    return not state_result_guard_codes(
        state,
        state["python_result"],
        role="python",
        vectors=vectors,
    ) and not state_result_guard_codes(
        state,
        state["node_result"],
        role="node",
        vectors=vectors,
    )


def source_and_language_separation_observed(
    state: dict[str, Any],
) -> bool:
    python_source = state["python_source_manifest"]
    node_source = state["node_source_manifest"]
    return (
        not source_text_guard_codes(
            state["python_bytes"],
            state["node_bytes"],
        )
        and not source_manifest_guard_codes("python", python_source)
        and not source_manifest_guard_codes("node", node_source)
        and isinstance(python_source, dict)
        and isinstance(node_source, dict)
        and python_source.get("implementation_id") == PYTHON_ID
        and node_source.get("implementation_id") == NODE_ID
        and python_source.get("language") == "Python"
        and node_source.get("language") == "JavaScript"
        and python_source.get("implementation_id")
        != node_source.get("implementation_id")
        and python_source.get("language") != node_source.get("language")
    )


def comparison_probe_document(
    python_result: dict[str, Any],
) -> dict[str, Any]:
    projection_raw = compact_json(result_projection(python_result))
    return {
        "projection_raw_sha256": raw_binding(projection_raw)["raw_sha256"],
        "projection_byte_count_decimal": str(len(projection_raw)),
        "complete_ordered_projection_equal": True,
    }


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=False,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def write_staged_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def refresh_retained_evidence(
    errors: list[str],
    python_executable: Path,
    node_executable: Path,
) -> None:
    for error in validate_runtime_selection(
        python_executable,
        node_executable,
    ):
        add(errors, f"PRQ-002D {error}")
    if errors:
        return
    cases = load(CASES, errors)
    contract = load(CONTRACT, errors)
    vectors = load(VECTORS, errors)
    if not all(isinstance(item, dict) for item in (cases, contract, vectors)):
        return
    if not (
        isinstance(cases.get("cases"), list)
        and len(cases["cases"]) == len(EXPECTED_CODES)
    ):
        add(errors, "PRQ-002D cannot refresh from an invalid case inventory")
        return
    cases["gate_known_bads"] = expected_gate_rows()

    with tempfile.TemporaryDirectory(
        prefix=".prq002d-evidence-staging-",
        dir=SUITE.parent,
    ) as directory:
        staging_root = Path(directory)
        staged_paths: dict[Path, Path] = {}
        binding_overrides: dict[Path, bytes] = {}

        def stage(target: Path, data: bytes) -> Path:
            staged = staging_root / target.relative_to(ROOT)
            write_staged_bytes(staged, data)
            staged_paths[target] = staged
            binding_overrides[target] = data
            return staged

        regenerated = staging_root / "authoring-check-vectors.json"
        generated = subprocess.run(
            [
                python_executable.resolve(strict=True).as_posix(),
                "-I",
                "-B",
                GENERATOR.resolve(strict=True).as_posix(),
                "--output",
                regenerated.as_posix(),
            ],
            cwd=ROOT,
            env={
                "PATH": python_executable.resolve().parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
            capture_output=True,
            timeout=30,
            check=False,
        )
        if (
            generated.returncode != 0
            or generated.stdout
            or generated.stderr
            or not regenerated.is_file()
            or regenerated.read_bytes() != VECTORS.read_bytes()
        ):
            add(errors, "PRQ-002D authoring vector regeneration differs")
            return

        input_manifest = expected_input_manifest()
        python_source = expected_source_manifest("python")
        node_source = expected_source_manifest("node")
        manifest = expected_manifest()
        stage(CASES, pretty_json_bytes(cases))
        stage(INPUT_MANIFEST, pretty_json_bytes(input_manifest))
        staged_python_source = stage(
            PYTHON_SOURCE,
            pretty_json_bytes(python_source),
        )
        staged_node_source = stage(
            NODE_SOURCE,
            pretty_json_bytes(node_source),
        )
        stage(MANIFEST, pretty_json_bytes(manifest))

        try:
            python_observation = execute_child(
                python_executable,
                PYTHON_RUNNER,
                staged_python_source,
                node=False,
            )
            node_observation = execute_child(
                node_executable,
                NODE_RUNNER,
                staged_node_source,
                node=True,
            )
        except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
            add(
                errors,
                "PRQ-002D retained-evidence execution failed: "
                f"{type(exc).__name__}: {exc}",
            )
            return
        for role, observation, path in (
            ("python", python_observation, PYTHON_RESULT),
            ("node", node_observation, NODE_RESULT),
        ):
            expected_stdout = compact_json(observation["document"]) + b"\n"
            if observation["stdout"] != expected_stdout:
                add(
                    errors,
                    f"PRQ-002D {role} observer stdout is not canonical "
                    "one-line JSON",
                )
                return
            stage(path, observation["stdout"])

        python_result = python_observation["document"]
        node_result = node_observation["document"]
        python_execution = expected_execution_receipt(
            "python",
            runtime=python_observation["runtime"],
            argv=python_observation["argv"],
            binding_overrides=binding_overrides,
        )
        node_execution = expected_execution_receipt(
            "node",
            runtime=node_observation["runtime"],
            argv=node_observation["argv"],
            binding_overrides=binding_overrides,
        )
        stage(PYTHON_EXECUTION, pretty_json_bytes(python_execution))
        stage(NODE_EXECUTION, pretty_json_bytes(node_execution))

        probe = comparison_probe_document(python_result)
        state = build_gate_state(
            cases=cases,
            contract=contract,
            input_manifest=input_manifest,
            manifest=manifest,
            python_source=python_source,
            node_source=node_source,
            python_result=python_result,
            node_result=node_result,
            python_execution=python_execution,
            node_execution=node_execution,
            comparison=probe,
            binding_overrides=binding_overrides,
        )
        fixed_oracle = fixed_private_oracle_satisfied(state, vectors)
        separation = source_and_language_separation_observed(state)
        expected_gate_summary, _ = expected_gate_self_test(cases)
        comparison = expected_comparison(
            python_result,
            node_result,
            gate_summary=expected_gate_summary,
            fixed_private_oracle_satisfied=fixed_oracle,
            source_and_language_separation_observed=separation,
            binding_overrides=binding_overrides,
        )
        state["comparison"] = comparison
        gate_summary = validate_gate_self_tests(errors, state)
        if not fixed_oracle:
            add(
                errors,
                "PRQ-002D refreshed observations do not satisfy the fixed oracle",
            )
        if not separation:
            add(
                errors,
                "PRQ-002D refreshed source/language separation is not retained",
            )
        if not json_exact(gate_summary, expected_gate_summary):
            add(
                errors,
                "PRQ-002D observed gate summary is not the pure oracle summary",
            )
        if errors:
            return
        stage(COMPARISON, pretty_json_bytes(comparison))

        # Every candidate byte is complete and guard-clean before finalization.
        # The comparison receipt is replaced last and binds the other targets,
        # so an interrupted multi-file replacement cannot appear valid.
        finalization_order = [
            CASES,
            INPUT_MANIFEST,
            PYTHON_SOURCE,
            NODE_SOURCE,
            MANIFEST,
            PYTHON_RESULT,
            NODE_RESULT,
            PYTHON_EXECUTION,
            NODE_EXECUTION,
            COMPARISON,
        ]
        try:
            for target in finalization_order:
                os.replace(staged_paths[target], target)
            for parent in sorted(
                {target.parent for target in finalization_order},
                key=lambda path: path.as_posix(),
            ):
                descriptor = os.open(parent, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        except OSError as exc:
            add(
                errors,
                "PRQ-002D staged evidence finalization failed: "
                f"{type(exc).__name__}: {exc}",
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--recompute-all", action="store_true")
    mode.add_argument("--refresh-retained-evidence", action="store_true")
    parser.add_argument("--python-executable", type=Path)
    parser.add_argument("--node-executable", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    selectors = (args.python_executable, args.node_executable)
    if args.refresh_retained_evidence:
        if any(value is None for value in selectors):
            add(
                errors,
                "--refresh-retained-evidence requires --python-executable "
                "and --node-executable",
            )
        else:
            refresh_retained_evidence(
                errors,
                args.python_executable,
                args.node_executable,
            )
        if errors:
            print("PRQ-002D schema-registry prehash replay: FAILED")
            for error in errors:
                print(f"- {error}")
            return 1
    required = {
        VALIDATOR,
        CONTRACT_SCHEMA,
        CONTRACT,
        MANIFEST,
        INPUT_MANIFEST,
        VECTORS,
        CASES,
        GENERATOR,
        SAFE_BUNDLE,
        RESOURCE_1,
        RESOURCE_2,
        PROBE_1,
        PROBE_2,
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
        PREDECESSOR_DECISION,
        PREDECESSOR_COMPARISON,
        PYTHON_INSTALLATION_LOCK,
        NODE_INSTALLER,
    }
    for path in sorted(required):
        if not path.is_file():
            add(errors, f"missing PRQ-002D artifact: {path.relative_to(ROOT)}")
    if errors:
        print("PRQ-002D schema-registry prehash replay: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    validate_inventory(errors)
    contract_schema = load(CONTRACT_SCHEMA, errors)
    contract = load(CONTRACT, errors)
    manifest = load(MANIFEST, errors)
    input_manifest = load(INPUT_MANIFEST, errors)
    vectors = load(VECTORS, errors)
    cases = load(CASES, errors)
    python_source = load(PYTHON_SOURCE, errors)
    node_source = load(NODE_SOURCE, errors)
    python_result = load(PYTHON_RESULT, errors)
    node_result = load(NODE_RESULT, errors)
    python_execution = load(PYTHON_EXECUTION, errors)
    node_execution = load(NODE_EXECUTION, errors)
    comparison = load(COMPARISON, errors)

    validate_contract(errors, contract_schema, contract)
    validate_contract_pins(errors, contract, vectors)
    validate_input_manifest(errors, input_manifest)
    validate_vectors_and_cases(errors, vectors, cases)
    validate_source_controls(errors, python_source, node_source)
    validate_manifest(errors, manifest)
    validate_result(
        errors,
        python_result,
        role="python",
        source_manifest=PYTHON_SOURCE,
        vectors=vectors,
        cases=cases,
        contract=contract,
    )
    validate_result(
        errors,
        node_result,
        role="node",
        source_manifest=NODE_SOURCE,
        vectors=vectors,
        cases=cases,
        contract=contract,
    )
    validate_execution_receipt(errors, python_execution, role="python")
    validate_execution_receipt(errors, node_execution, role="node")
    state = build_gate_state(
        cases=cases,
        contract=contract,
        input_manifest=input_manifest,
        manifest=manifest,
        python_source=python_source,
        node_source=node_source,
        python_result=python_result,
        node_result=node_result,
        python_execution=python_execution,
        node_execution=node_execution,
        comparison=comparison,
    )
    gate_summary = validate_gate_self_tests(errors, state)
    fixed_oracle = (
        fixed_private_oracle_satisfied(state, vectors)
        if isinstance(vectors, dict)
        else False
    )
    separation = source_and_language_separation_observed(state)
    validate_comparison(
        errors,
        comparison,
        python_result,
        node_result,
        gate_summary=gate_summary,
        fixed_private_oracle_satisfied=fixed_oracle,
        source_and_language_separation_observed=separation,
    )

    if args.recompute_all:
        if any(value is None for value in selectors):
            add(
                errors,
                "--recompute-all requires --python-executable and --node-executable",
            )
        else:
            recompute(
                errors,
                args.python_executable,
                args.node_executable,
                python_result,
                node_result,
            )
    elif (
        not args.refresh_retained_evidence
        and any(value is not None for value in selectors)
    ):
        add(
            errors,
            "runtime selectors require --recompute-all or "
            "--refresh-retained-evidence",
        )

    if errors:
        print("PRQ-002D schema-registry prehash replay: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "PRQ-002D schema-registry prehash replay: PASSED "
        f"({len(EXPECTED_CODES)} vectors: 1 accepted, "
        f"{len(EXPECTED_CODES) - 1} attributed refusals; "
        f"2 source-separated observers; {len(GATE_KNOWN_BADS)} gate known-bads)"
    )
    print(
        "- bounded architecture evidence only; no product/member/commitment/"
        "registry digest, profile conformance or issuance, admission, PRQ-002 "
        "closure, Gate A, runtime, or publication authority"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
