#!/usr/bin/env python3
"""Adversarially validate the retained canonicalization comparator boundary.

This is a bounded architecture-evidence falsifier.  It deliberately preserves
the comparator defect it detects; a zero exit establishes only that the fixed
trials and the meta-gate reproduced their declared observations.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "architecture/canonicalization-evaluator-integrity-candidate.json"
CASES_PATH = ROOT / "tests/canonicalization-evaluator-integrity/cases.json"
COMPARATOR_PATH = ROOT / "tests/canonicalization/compare_results.py"
PYTHON_RESULT_PATH = ROOT / "tests/canonicalization/results/python-rfc8785-0.1.4.json"
NODE_RESULT_PATH = ROOT / "tests/canonicalization/results/node-canonicalize-3.0.0.json"
EXPECTATIONS_PATH = ROOT / "tests/canonicalization/expectations.json"
MANIFEST_PATH = ROOT / "tests/canonicalization/manifest.json"
TIMEOUT_SECONDS = 5
REPETITIONS = 2
SOURCE_COMMIT = "05c2c3b18a3987c337a8c76d8db55ea4eb72bfa9"
SOURCE_TREE = "35f3622e8c3b883f33b0e5761686f6972ec1f67e"
SOURCE_PARENT = "36d798e2cb7d22352ba62e4fc07106e685b87f9f"
TRACE_STAGES = [
    "subject_bindings_verified",
    "isolated_result_pair_materialized",
    "declared_mutation_applied",
    "unchanged_comparator_executed",
    "receipt_strictly_parsed",
    "full_observation_compared",
    "claim_boundary_checked",
]
ORACLE_STATES = ["pass", "fail", "indeterminate", "not_run"]
COMPARISON_STATES = ["exact", "disagree", "indeterminate", "not_run"]
SEPARATION_STATES = [
    "proven_within_declared_scope",
    "not_proven",
    "contradicted",
]
EXPECTED_ATTACK_IDS = [
    "copied_python_relabelled_node",
    "one_sided_answer_tamper",
    "identical_common_mode_wrong_answer",
    "coordinated_case_omission",
    "duplicate_case_identity",
    "infrastructure_error",
    "implementation_identity_substitution",
    "shared_false_input_digest",
    "shared_false_manifest_digest",
]
EXPECTED_GATE_IDS = [
    "contract_closed_shape",
    "binding_path_replacement",
    "binding_digest_replacement",
    "trace_stage_reorder",
    "private_holdout_claim",
    "human_calibration_claim",
    "profile_issuance_claim",
    "authority_claim",
    "prompt_injection_coverage_claim",
    "case_census_reduction",
    "expected_error_replacement",
    "candidate_binding_replacement",
    "case_disposition_weakening",
    "case_mutation_replacement",
    "clone_mutation_noop",
    "role_path_swap",
    "lexical_path_alias",
    "duplicate_json_key",
    "final_symlink_binding",
    "ancestor_symlink_binding",
    "timeout_configuration_weakening",
    "timeout_control",
    "meta_delegate_blindness",
    "gate_a_authority_claim",
    "runtime_authority_claim",
    "deployment_authority_claim",
    "publication_authority_claim",
    "credentials_authority_claim",
    "executes_canonicalizers_claim",
    "repairs_comparator_claim",
    "organizational_independence_claim",
    "blinded_gate",
    "duplicate_probe_subject",
]
EXPECTED_GATE_ERRORS = {
    "contract_closed_shape": "closed_shape:contract",
    "binding_path_replacement": "unsafe_binding_path",
    "binding_digest_replacement": "binding_digest:tests/canonicalization/compare_results.py",
    "trace_stage_reorder": "trace_stage_order",
    "private_holdout_claim": "boolean_boundary:declared_scope.claims_private_holdout",
    "human_calibration_claim": "boolean_boundary:declared_scope.claims_human_calibration",
    "profile_issuance_claim": "boolean_boundary:authority.profile_issuance",
    "authority_claim": "boolean_boundary:authority.external_effects",
    "prompt_injection_coverage_claim": "boolean_boundary:declared_scope.claims_prompt_injection_coverage",
    "case_census_reduction": "case_census",
    "expected_error_replacement": "gate_expected_error:contract_closed_shape",
    "candidate_binding_replacement": "candidate_binding_digest",
    "case_disposition_weakening": "case_contract:copied_python_relabelled_node",
    "case_mutation_replacement": "case_contract:one_sided_answer_tamper",
    "clone_mutation_noop": "mutation_postcondition:clone_python_and_relabel_node",
    "role_path_swap": "binding_path_for_role:comparator",
    "lexical_path_alias": "binding_path_for_role:comparator",
    "duplicate_json_key": "duplicate_json_key:a",
    "final_symlink_binding": "binding_symlink:link.json",
    "ancestor_symlink_binding": "binding_symlink:linked/data.json",
    "timeout_configuration_weakening": "trial_timeout",
    "timeout_control": "infrastructure_timeout",
    "meta_delegate_blindness": "known_bad_accepted:meta_delegate_blindness",
    "gate_a_authority_claim": "boolean_boundary:authority.gate_a_acceptance",
    "runtime_authority_claim": "boolean_boundary:authority.runtime",
    "deployment_authority_claim": "boolean_boundary:authority.deployment",
    "publication_authority_claim": "boolean_boundary:authority.publication",
    "credentials_authority_claim": "boolean_boundary:authority.credentials",
    "executes_canonicalizers_claim": "boolean_boundary:declared_scope.executes_canonicalizers",
    "repairs_comparator_claim": "boolean_boundary:declared_scope.repairs_comparator",
    "organizational_independence_claim": "boolean_boundary:declared_scope.claims_organizational_independence",
    "blinded_gate": "baseline_classification",
    "duplicate_probe_subject": "binding_path_for_role:manifest",
}
EXPECTED_SUBJECT_PATHS = {
    "comparator": "tests/canonicalization/compare_results.py",
    "manifest": "tests/canonicalization/manifest.json",
    "oracle_expectations": "tests/canonicalization/expectations.json",
    "source_lock": "tests/canonicalization/source-lock.json",
    "python_labelled_result": "tests/canonicalization/results/python-rfc8785-0.1.4.json",
    "node_labelled_result": "tests/canonicalization/results/node-canonicalize-3.0.0.json",
    "comparison_receipt": "tests/canonicalization/results/comparison-receipt.json",
}
EXPECTED_CASE_CONTRACTS = {
    "safe_control": {
        "kind": "control",
        "mutation": "none",
        "expected_returncode": 0,
        "expected_status": "pass",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "pass",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "unwitnessed_retained_artifact",
    },
    "copied_python_relabelled_node": {
        "kind": "attack",
        "mutation": "clone_python_and_relabel_node",
        "expected_returncode": 0,
        "expected_status": "pass",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "pass",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "contradicted",
        "expected_execution_origin": "synthetic_clone_with_relabelled_metadata",
    },
    "one_sided_answer_tamper": {
        "kind": "attack",
        "mutation": "tamper_node_answer",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": False,
        "expected_oracle_conformity": "fail",
        "expected_cross_implementation_comparison": "disagree",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_one_sided_mutation",
    },
    "identical_common_mode_wrong_answer": {
        "kind": "attack",
        "mutation": "tamper_both_answers_identically",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "fail",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_common_mode_mutation",
    },
    "coordinated_case_omission": {
        "kind": "attack",
        "mutation": "omit_same_case_from_both",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "fail",
        "expected_cross_implementation_comparison": "indeterminate",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_coordinated_omission",
    },
    "duplicate_case_identity": {
        "kind": "attack",
        "mutation": "duplicate_node_case_identity",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "indeterminate",
        "expected_cross_implementation_comparison": "indeterminate",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_duplicate_identity",
    },
    "infrastructure_error": {
        "kind": "attack",
        "mutation": "malform_node_json",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": False,
        "expected_oracle_conformity": "indeterminate",
        "expected_cross_implementation_comparison": "indeterminate",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_nonterminal_output",
    },
    "implementation_identity_substitution": {
        "kind": "attack",
        "mutation": "replace_node_runner_with_python",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "pass",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "contradicted",
        "expected_execution_origin": "synthetic_identity_substitution",
    },
    "shared_false_input_digest": {
        "kind": "attack",
        "mutation": "replace_shared_input_digest",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "fail",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_shared_binding_mutation",
    },
    "shared_false_manifest_digest": {
        "kind": "attack",
        "mutation": "replace_shared_manifest_digest",
        "expected_returncode": 1,
        "expected_status": "fail",
        "expected_implementation_agreement": True,
        "expected_oracle_conformity": "pass",
        "expected_cross_implementation_comparison": "exact",
        "expected_execution_source_separation": "not_proven",
        "expected_execution_origin": "synthetic_shared_binding_mutation",
    },
}


class EvidenceError(ValueError):
    """A deterministic integrity-gate refusal."""


class DuplicateKey(EvidenceError):
    """A JSON object contained a duplicate member."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(f"duplicate_json_key:{key}")
        value[key] = item
    return value


def strict_load_bytes(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"invalid_utf8:{label}") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"invalid_json:{label}") from exc


def strict_load(path: Path) -> Any:
    return strict_load_bytes(path.read_bytes(), path.relative_to(ROOT).as_posix())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def retained_json_bytes(value: Any) -> bytes:
    """Serialize while preserving the parsed retained member order."""

    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise EvidenceError(f"shape_not_object:{label}")
    actual = set(value)
    if actual != expected:
        raise EvidenceError(f"closed_shape:{label}")
    return value


def exact_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise EvidenceError(f"shape_not_array:{label}")
    return value


def exact_bool(value: Any, expected: bool, label: str) -> None:
    if value is not expected:
        raise EvidenceError(f"boolean_boundary:{label}")


def secure_regular_file(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise EvidenceError("unsafe_binding_path")
    relative_path = Path(relative)
    if (
        relative_path.is_absolute()
        or ".." in relative_path.parts
        or "\\" in relative
        or relative_path.as_posix() != relative
    ):
        raise EvidenceError("unsafe_binding_path")
    cursor = root
    if cursor.is_symlink():
        raise EvidenceError(f"binding_symlink:{relative}")
    for part in relative_path.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise EvidenceError(f"binding_symlink:{relative}")
    path = root / relative_path
    if not path.is_file():
        raise EvidenceError(f"binding_not_regular:{relative}")
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise EvidenceError(f"binding_outside_repository:{relative}") from exc
    return path


def secure_repo_file(relative: str) -> Path:
    return secure_regular_file(ROOT, relative)


def verify_binding(binding: Any, label: str) -> tuple[str, tuple[int, int]]:
    record = exact_keys(binding, {"role", "path", "sha256", "bytes"}, label)
    if not isinstance(record["role"], str) or not record["role"]:
        raise EvidenceError(f"binding_role:{label}")
    expected_path = EXPECTED_SUBJECT_PATHS.get(record["role"])
    if record["path"] != expected_path:
        raise EvidenceError(f"binding_path_for_role:{record['role']}")
    path = secure_repo_file(record["path"])
    raw = path.read_bytes()
    if record["sha256"] != sha256_bytes(raw):
        raise EvidenceError(f"binding_digest:{record['path']}")
    if record["bytes"] != len(raw):
        raise EvidenceError(f"binding_bytes:{record['path']}")
    stat = path.stat()
    return path.resolve().as_posix(), (stat.st_dev, stat.st_ino)


def verify_source_checkpoint(record: Any) -> None:
    checkpoint = exact_keys(record, {"commit", "tree", "sole_parent"}, "source_checkpoint")
    if checkpoint != {
        "commit": SOURCE_COMMIT,
        "tree": SOURCE_TREE,
        "sole_parent": SOURCE_PARENT,
    }:
        raise EvidenceError("source_checkpoint_identity")
    for expression, expected, label in (
        (f"{SOURCE_COMMIT}^{{tree}}", SOURCE_TREE, "tree"),
        (f"{SOURCE_COMMIT}^", SOURCE_PARENT, "parent"),
    ):
        try:
            result = subprocess.run(
                ["git", "rev-parse", expression],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise EvidenceError(f"source_checkpoint_git:{label}") from exc
        if result.returncode != 0 or result.stdout.strip() != expected:
            raise EvidenceError(f"source_checkpoint_{label}")


def validate_contract(contract: Any, *, verify_bytes: bool = True) -> None:
    value = exact_keys(
        contract,
        {
            "contract_version",
            "candidate_id",
            "status",
            "source_checkpoint",
            "checker_binding",
            "subject_bindings",
            "trace_stages",
            "disposition_vocabulary",
            "baseline_classification",
            "declared_scope",
            "attack_case_ids",
            "gate_known_bad_ids",
            "authority",
        },
        "contract",
    )
    if value["contract_version"] != "0.1.0":
        raise EvidenceError("contract_version")
    if value["candidate_id"] != "canonicalization-evaluator-integrity-2026-07-22":
        raise EvidenceError("candidate_id")
    if value["status"] != "blocking":
        raise EvidenceError("candidate_status")
    verify_source_checkpoint(value["source_checkpoint"])
    if value["trace_stages"] != TRACE_STAGES:
        raise EvidenceError("trace_stage_order")
    vocab = exact_keys(
        value["disposition_vocabulary"],
        {"oracle_conformity", "cross_implementation_comparison", "execution_source_separation"},
        "disposition_vocabulary",
    )
    if vocab["oracle_conformity"] != ORACLE_STATES:
        raise EvidenceError("oracle_vocabulary")
    if vocab["cross_implementation_comparison"] != COMPARISON_STATES:
        raise EvidenceError("comparison_vocabulary")
    if vocab["execution_source_separation"] != SEPARATION_STATES:
        raise EvidenceError("separation_vocabulary")
    baseline = exact_keys(
        value["baseline_classification"],
        {
            "oracle_conformity",
            "cross_implementation_comparison",
            "execution_source_separation",
            "execution_origin",
            "profile_issuance_blocking",
        },
        "baseline_classification",
    )
    if baseline != {
        "oracle_conformity": "pass",
        "cross_implementation_comparison": "exact",
        "execution_source_separation": "not_proven",
        "execution_origin": "unwitnessed_retained_artifact",
        "profile_issuance_blocking": True,
    }:
        raise EvidenceError("baseline_classification")
    scope = exact_keys(
        value["declared_scope"],
        {
            "executes_canonicalizers",
            "repairs_comparator",
            "claims_private_holdout",
            "claims_prompt_injection_coverage",
            "claims_human_calibration",
            "claims_organizational_independence",
        },
        "declared_scope",
    )
    for key in scope:
        exact_bool(scope[key], False, f"declared_scope.{key}")
    authority = exact_keys(
        value["authority"],
        {
            "profile_issuance",
            "gate_a_acceptance",
            "runtime",
            "deployment",
            "publication",
            "credentials",
            "external_effects",
        },
        "authority",
    )
    for key in authority:
        exact_bool(authority[key], False, f"authority.{key}")
    if value["attack_case_ids"] != EXPECTED_ATTACK_IDS:
        raise EvidenceError("attack_case_census")
    if value["gate_known_bad_ids"] != EXPECTED_GATE_IDS:
        raise EvidenceError("gate_case_census")
    checker = exact_keys(
        value["checker_binding"], {"path", "sha256", "bytes"}, "checker_binding"
    )
    if checker["path"] != "scripts/validate_canonicalization_evaluator_integrity.py":
        raise EvidenceError("checker_binding_path")
    if verify_bytes:
        checker_path = secure_repo_file(checker["path"])
        raw = checker_path.read_bytes()
        if checker["sha256"] != sha256_bytes(raw):
            raise EvidenceError("checker_binding_digest")
        if checker["bytes"] != len(raw):
            raise EvidenceError("checker_binding_bytes")
    bindings = exact_list(value["subject_bindings"], "subject_bindings")
    expected_roles = list(EXPECTED_SUBJECT_PATHS)
    roles: list[str] = []
    paths: list[str] = []
    file_identities: list[tuple[str, tuple[int, int]]] = []
    for index, binding in enumerate(bindings):
        label = f"subject_bindings[{index}]"
        record = exact_keys(binding, {"role", "path", "sha256", "bytes"}, label)
        if not isinstance(record["role"], str) or not record["role"]:
            raise EvidenceError(f"binding_role:{label}")
        expected_path = EXPECTED_SUBJECT_PATHS.get(record["role"])
        if record["path"] != expected_path:
            raise EvidenceError(f"binding_path_for_role:{record['role']}")
        if verify_bytes:
            file_identities.append(verify_binding(record, label))
        roles.append(binding["role"])
        paths.append(binding["path"])
    if roles != expected_roles:
        raise EvidenceError("binding_role_census")
    if len(paths) != len(set(paths)):
        raise EvidenceError("duplicate_binding_path")
    if verify_bytes and (
        len({resolved for resolved, _ in file_identities}) != len(file_identities)
        or len({identity for _, identity in file_identities}) != len(file_identities)
    ):
        raise EvidenceError("duplicate_binding_file_identity")


def validate_cases(corpus: Any, candidate_raw: bytes) -> None:
    value = exact_keys(
        corpus,
        {
            "case_corpus_version",
            "candidate_binding",
            "trial_repetitions",
            "timeout_seconds",
            "cases",
            "gate_known_bads",
        },
        "case_corpus",
    )
    if value["case_corpus_version"] != "0.1.0":
        raise EvidenceError("case_corpus_version")
    binding = exact_keys(value["candidate_binding"], {"path", "sha256", "bytes"}, "candidate_binding")
    if binding["path"] != "architecture/canonicalization-evaluator-integrity-candidate.json":
        raise EvidenceError("candidate_binding_path")
    if binding["sha256"] != sha256_bytes(candidate_raw):
        raise EvidenceError("candidate_binding_digest")
    if binding["bytes"] != len(candidate_raw):
        raise EvidenceError("candidate_binding_bytes")
    if value["trial_repetitions"] != REPETITIONS:
        raise EvidenceError("trial_repetitions")
    if value["timeout_seconds"] != TIMEOUT_SECONDS:
        raise EvidenceError("trial_timeout")
    cases = exact_list(value["cases"], "cases")
    case_ids: list[str] = []
    expected_ids = ["safe_control", *EXPECTED_ATTACK_IDS]
    for index, case in enumerate(cases):
        record = exact_keys(
            case,
            {
                "case_id",
                "kind",
                "mutation",
                "expected_returncode",
                "expected_status",
                "expected_implementation_agreement",
                "expected_oracle_conformity",
                "expected_cross_implementation_comparison",
                "expected_execution_source_separation",
                "expected_execution_origin",
                "expected_profile_issuance_blocking",
                "intended_falsifier",
            },
            f"cases[{index}]",
        )
        case_ids.append(record["case_id"])
        required = EXPECTED_CASE_CONTRACTS.get(record["case_id"])
        if required is None:
            raise EvidenceError(f"case_identity:{record['case_id']}")
        if any(record[key] != expected for key, expected in required.items()):
            raise EvidenceError(f"case_contract:{record['case_id']}")
        if record["kind"] not in {"control", "attack"}:
            raise EvidenceError(f"case_kind:{record['case_id']}")
        if not isinstance(record["mutation"], str):
            raise EvidenceError(f"case_mutation:{record['case_id']}")
        if record["expected_returncode"] not in {0, 1}:
            raise EvidenceError(f"case_returncode:{record['case_id']}")
        if record["expected_status"] != ("pass" if record["expected_returncode"] == 0 else "fail"):
            raise EvidenceError(f"case_status:{record['case_id']}")
        if not isinstance(record["expected_implementation_agreement"], bool):
            raise EvidenceError(f"case_agreement_boolean:{record['case_id']}")
        if record["expected_oracle_conformity"] not in ORACLE_STATES:
            raise EvidenceError(f"case_oracle:{record['case_id']}")
        if record["expected_cross_implementation_comparison"] not in COMPARISON_STATES:
            raise EvidenceError(f"case_comparison:{record['case_id']}")
        if record["expected_execution_source_separation"] not in SEPARATION_STATES:
            raise EvidenceError(f"case_separation:{record['case_id']}")
        exact_bool(record["expected_profile_issuance_blocking"], True, f"case_blocking:{record['case_id']}")
        if not isinstance(record["intended_falsifier"], str) or not record["intended_falsifier"]:
            raise EvidenceError(f"case_intent:{record['case_id']}")
    if case_ids != expected_ids or len(case_ids) != len(set(case_ids)):
        raise EvidenceError("case_census")
    gate_cases = exact_list(value["gate_known_bads"], "gate_known_bads")
    gate_ids: list[str] = []
    for index, case in enumerate(gate_cases):
        record = exact_keys(case, {"case_id", "mutation", "expected_error"}, f"gate_known_bads[{index}]")
        gate_ids.append(record["case_id"])
        if not isinstance(record["mutation"], str) or not record["mutation"]:
            raise EvidenceError(f"gate_mutation:{record['case_id']}")
        if not isinstance(record["expected_error"], str) or not record["expected_error"]:
            raise EvidenceError(f"gate_expected_error:{record['case_id']}")
        if record["expected_error"] != EXPECTED_GATE_ERRORS[record["case_id"]]:
            raise EvidenceError(f"gate_expected_error:{record['case_id']}")
    if gate_ids != EXPECTED_GATE_IDS or len(gate_ids) != len(set(gate_ids)):
        raise EvidenceError("gate_case_census")


def projection(case: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": case["id"],
        "input_length": case["input_length"],
        "input_sha256": case["input_sha256"],
        "outcome": case["outcome"],
    }
    if case["outcome"] == "accepted":
        result.update(
            {
                "canonical_length": case["canonical_length"],
                "canonical_hex": case["canonical_hex"],
                "canonical_sha256": case["canonical_sha256"],
            }
        )
    elif case["outcome"] == "refused":
        result["code"] = case["code"]
    else:
        result["error_type"] = case.get("error_type")
    return result


def unique_index(items: Any) -> tuple[dict[str, dict[str, Any]] | None, bool]:
    if not isinstance(items, list):
        return None, False
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            return None, False
        if item["id"] in indexed:
            return None, False
        indexed[item["id"]] = item
    return indexed, True


def classify_results(left_raw: bytes, right_raw: bytes) -> tuple[str, str]:
    try:
        left = strict_load_bytes(left_raw, "trial_left")
        right = strict_load_bytes(right_raw, "trial_right")
    except EvidenceError:
        return "indeterminate", "indeterminate"
    if not isinstance(left, dict) or not isinstance(right, dict):
        return "indeterminate", "indeterminate"
    left_index, left_unique = unique_index(left.get("cases"))
    right_index, right_unique = unique_index(right.get("cases"))
    if not left_unique or not right_unique or left_index is None or right_index is None:
        return "indeterminate", "indeterminate"
    expectations = strict_load(EXPECTATIONS_PATH)
    expected_index = {item["id"]: item for item in expectations["cases"]}
    complete = set(left_index) == set(expected_index) == set(right_index)
    oracle_pass = complete
    if complete:
        for identifier, expected in expected_index.items():
            try:
                if projection(left_index[identifier]) != expected or projection(right_index[identifier]) != expected:
                    oracle_pass = False
                    break
            except (KeyError, TypeError):
                oracle_pass = False
                break
    oracle = "pass" if oracle_pass else "fail"
    if not complete:
        comparison = "indeterminate"
    else:
        try:
            comparison = "exact" if all(
                projection(left_index[identifier]) == projection(right_index[identifier])
                for identifier in sorted(expected_index)
            ) else "disagree"
        except (KeyError, TypeError):
            comparison = "indeterminate"
    return oracle, comparison


def fold_summary(result: dict[str, Any]) -> None:
    indexed = {case["id"]: case for case in result["cases"]}
    result["summary"] = {
        "total": len(indexed),
        "accepted": sum(case.get("outcome") == "accepted" for case in indexed.values()),
        "refused": sum(case.get("outcome") == "refused" for case in indexed.values()),
        "errors": sum(case.get("outcome") == "error" for case in indexed.values()),
    }


def mutate_pair(
    mutation: str,
    left: dict[str, Any],
    right: dict[str, Any],
    source_left_raw: bytes,
    source_right_raw: bytes,
) -> tuple[bytes, bytes, dict[str, Any]]:
    witness = {
        "mutation": mutation,
        "source_left_raw_sha256": sha256_bytes(source_left_raw),
        "source_right_raw_sha256": sha256_bytes(source_right_raw),
        "source_left_object_sha256": sha256_bytes(canonical_bytes(left)),
        "source_right_object_sha256": sha256_bytes(canonical_bytes(right)),
        "intermediate_clone_object_sha256": None,
        "output_left_raw_sha256": None,
        "output_right_raw_sha256": None,
    }
    if mutation == "none":
        left_raw, right_raw = source_left_raw, source_right_raw
    elif mutation == "clone_python_and_relabel_node":
        right = copy.deepcopy(left)
        witness["intermediate_clone_object_sha256"] = sha256_bytes(
            canonical_bytes(right)
        )
        retained_node = strict_load(NODE_RESULT_PATH)
        right["implementation"] = retained_node["implementation"]
        left_raw, right_raw = source_left_raw, retained_json_bytes(right)
    elif mutation == "tamper_node_answer":
        right["cases"][0]["canonical_sha256"] = "0" * 64
        left_raw, right_raw = source_left_raw, retained_json_bytes(right)
    elif mutation == "tamper_both_answers_identically":
        left["cases"][0]["canonical_sha256"] = "0" * 64
        right["cases"][0]["canonical_sha256"] = "0" * 64
        left_raw, right_raw = retained_json_bytes(left), retained_json_bytes(right)
    elif mutation == "omit_same_case_from_both":
        omitted = left["cases"][0]["id"]
        left["cases"] = [case for case in left["cases"] if case["id"] != omitted]
        right["cases"] = [case for case in right["cases"] if case["id"] != omitted]
        fold_summary(left)
        fold_summary(right)
        left_raw, right_raw = retained_json_bytes(left), retained_json_bytes(right)
    elif mutation == "duplicate_node_case_identity":
        right["cases"].append(copy.deepcopy(right["cases"][0]))
        left_raw, right_raw = source_left_raw, retained_json_bytes(right)
    elif mutation == "malform_node_json":
        left_raw, right_raw = source_left_raw, b"{\"not\":\"terminal\""
    elif mutation == "replace_node_runner_with_python":
        right["implementation"] = copy.deepcopy(left["implementation"])
        left_raw, right_raw = source_left_raw, retained_json_bytes(right)
    elif mutation == "replace_shared_input_digest":
        left["cases"][0]["input_sha256"] = "0" * 64
        right["cases"][0]["input_sha256"] = "0" * 64
        left_raw, right_raw = retained_json_bytes(left), retained_json_bytes(right)
    elif mutation == "replace_shared_manifest_digest":
        left["manifest_sha256"] = "0" * 64
        right["manifest_sha256"] = "0" * 64
        left_raw, right_raw = retained_json_bytes(left), retained_json_bytes(right)
    else:
        raise EvidenceError(f"unknown_trial_mutation:{mutation}")
    witness["output_left_raw_sha256"] = sha256_bytes(left_raw)
    witness["output_right_raw_sha256"] = sha256_bytes(right_raw)
    return left_raw, right_raw, witness


def verify_mutation_postcondition(
    mutation: str,
    original_left: dict[str, Any],
    original_right: dict[str, Any],
    original_left_raw: bytes,
    original_right_raw: bytes,
    left_raw: bytes,
    right_raw: bytes,
    witness: dict[str, Any],
) -> None:
    """Prove the declared synthetic delta occurred and no sibling delta leaked."""

    exact_keys(
        witness,
        {
            "mutation",
            "source_left_raw_sha256",
            "source_right_raw_sha256",
            "source_left_object_sha256",
            "source_right_object_sha256",
            "intermediate_clone_object_sha256",
            "output_left_raw_sha256",
            "output_right_raw_sha256",
        },
        "mutation_witness",
    )
    left_source_sha = sha256_bytes(canonical_bytes(original_left))
    right_source_sha = sha256_bytes(canonical_bytes(original_right))
    if (
        witness["mutation"] != mutation
        or witness["source_left_raw_sha256"] != sha256_bytes(original_left_raw)
        or witness["source_right_raw_sha256"] != sha256_bytes(original_right_raw)
        or witness["source_left_object_sha256"] != left_source_sha
        or witness["source_right_object_sha256"] != right_source_sha
        or witness["output_left_raw_sha256"] != sha256_bytes(left_raw)
        or witness["output_right_raw_sha256"] != sha256_bytes(right_raw)
    ):
        raise EvidenceError(f"mutation_postcondition:{mutation}")
    if mutation == "clone_python_and_relabel_node":
        if (
            witness["intermediate_clone_object_sha256"] != left_source_sha
            or witness["intermediate_clone_object_sha256"] == right_source_sha
        ):
            raise EvidenceError(f"mutation_postcondition:{mutation}")
    elif witness["intermediate_clone_object_sha256"] is not None:
        raise EvidenceError(f"mutation_postcondition:{mutation}")
    if mutation == "malform_node_json":
        valid = left_raw == original_left_raw
        valid = valid and right_raw == b"{\"not\":\"terminal\""
        if not valid:
            raise EvidenceError(f"mutation_postcondition:{mutation}")
        return
    try:
        observed_left = strict_load_bytes(left_raw, "postcondition_left")
        observed_right = strict_load_bytes(right_raw, "postcondition_right")
    except EvidenceError as exc:
        raise EvidenceError(f"mutation_postcondition:{mutation}") from exc
    expected_left = copy.deepcopy(original_left)
    expected_right = copy.deepcopy(original_right)
    expected_left_raw = original_left_raw
    expected_right_raw = original_right_raw
    if mutation == "none":
        pass
    elif mutation == "clone_python_and_relabel_node":
        expected_right = copy.deepcopy(original_left)
        expected_right["implementation"] = copy.deepcopy(original_right["implementation"])
        expected_right_raw = retained_json_bytes(expected_right)
        if expected_right_raw == original_right_raw:
            raise EvidenceError(f"mutation_postcondition:{mutation}")
    elif mutation == "tamper_node_answer":
        expected_right["cases"][0]["canonical_sha256"] = "0" * 64
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "tamper_both_answers_identically":
        expected_left["cases"][0]["canonical_sha256"] = "0" * 64
        expected_right["cases"][0]["canonical_sha256"] = "0" * 64
        expected_left_raw = retained_json_bytes(expected_left)
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "omit_same_case_from_both":
        omitted = expected_left["cases"][0]["id"]
        expected_left["cases"] = [
            case for case in expected_left["cases"] if case["id"] != omitted
        ]
        expected_right["cases"] = [
            case for case in expected_right["cases"] if case["id"] != omitted
        ]
        fold_summary(expected_left)
        fold_summary(expected_right)
        expected_left_raw = retained_json_bytes(expected_left)
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "duplicate_node_case_identity":
        expected_right["cases"].append(copy.deepcopy(expected_right["cases"][0]))
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "replace_node_runner_with_python":
        expected_right["implementation"] = copy.deepcopy(expected_left["implementation"])
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "replace_shared_input_digest":
        expected_left["cases"][0]["input_sha256"] = "0" * 64
        expected_right["cases"][0]["input_sha256"] = "0" * 64
        expected_left_raw = retained_json_bytes(expected_left)
        expected_right_raw = retained_json_bytes(expected_right)
    elif mutation == "replace_shared_manifest_digest":
        expected_left["manifest_sha256"] = "0" * 64
        expected_right["manifest_sha256"] = "0" * 64
        expected_left_raw = retained_json_bytes(expected_left)
        expected_right_raw = retained_json_bytes(expected_right)
    else:
        raise EvidenceError(f"unknown_trial_mutation:{mutation}")
    if (
        observed_left != expected_left
        or observed_right != expected_right
        or left_raw != expected_left_raw
        or right_raw != expected_right_raw
    ):
        raise EvidenceError(f"mutation_postcondition:{mutation}")


def provenance_for_mutation(mutation: str) -> tuple[str, str]:
    matches = [
        record
        for record in EXPECTED_CASE_CONTRACTS.values()
        if record["mutation"] == mutation
    ]
    if len(matches) != 1:
        raise EvidenceError(f"mutation_provenance_census:{mutation}")
    return (
        matches[0]["expected_execution_source_separation"],
        matches[0]["expected_execution_origin"],
    )


def parse_receipt(stdout: str) -> dict[str, Any]:
    receipt = strict_load_bytes(stdout.encode("utf-8"), "comparator_stdout")
    if not isinstance(receipt, dict):
        raise EvidenceError("receipt_not_object")
    if set(receipt) == {"status", "errors"}:
        if receipt["status"] != "fail" or not isinstance(receipt["errors"], list):
            raise EvidenceError("receipt_control_shape")
        return receipt
    expected = {
        "receipt_version",
        "status",
        "suite_id",
        "profile_id",
        "case_count",
        "accepted_count",
        "refused_count",
        "metamorphic_relation_count",
        "implementation_agreement",
        "errors",
    }
    exact_keys(receipt, expected, "comparator_receipt")
    if receipt["status"] not in {"pass", "fail"}:
        raise EvidenceError("receipt_status")
    if not isinstance(receipt["implementation_agreement"], bool) or not isinstance(receipt["errors"], list):
        raise EvidenceError("receipt_field_type")
    return receipt


def run_fixed_process(command: list[str], cwd: Path, timeout: float) -> dict[str, Any]:
    """Run one fixed argv in its own process group and settle every timeout."""

    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (AttributeError, ProcessLookupError):
            process.kill()
        stdout, stderr = process.communicate()
    return {
        "returncode": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
    }


def run_trial(case: dict[str, Any]) -> dict[str, Any]:
    source_left_raw = PYTHON_RESULT_PATH.read_bytes()
    source_right_raw = NODE_RESULT_PATH.read_bytes()
    left = strict_load_bytes(source_left_raw, "python_labelled_result")
    right = strict_load_bytes(source_right_raw, "node_labelled_result")
    original_left = copy.deepcopy(left)
    original_right = copy.deepcopy(right)
    left_raw, right_raw, mutation_witness = mutate_pair(
        case["mutation"], left, right, source_left_raw, source_right_raw
    )
    verify_mutation_postcondition(
        case["mutation"],
        original_left,
        original_right,
        source_left_raw,
        source_right_raw,
        left_raw,
        right_raw,
        mutation_witness,
    )
    with tempfile.TemporaryDirectory(prefix="odeya-canonical-evaluator-") as temp_name:
        temp = Path(temp_name)
        left_path = temp / "left.json"
        right_path = temp / "right.json"
        left_path.write_bytes(left_raw)
        right_path.write_bytes(right_raw)
        result = run_fixed_process(
            [
                sys.executable,
                os.fspath(COMPARATOR_PATH),
                os.fspath(left_path),
                os.fspath(right_path),
            ],
            ROOT,
            TIMEOUT_SECONDS,
        )
    if result["timed_out"]:
        raise EvidenceError(f"comparator_timeout:{case['case_id']}")
    receipt = parse_receipt(result["stdout"])
    oracle, comparison = classify_results(left_raw, right_raw)
    separation, execution_origin = provenance_for_mutation(case["mutation"])
    observation = {
        "mutation": case["mutation"],
        "mutation_witness": mutation_witness,
        "input_pair_sha256": {
            "left": sha256_bytes(left_raw),
            "right": sha256_bytes(right_raw),
        },
        "returncode": result["returncode"],
        "stdout_sha256": sha256_bytes(result["stdout"].encode("utf-8")),
        "stderr": result["stderr"],
        "receipt": receipt,
        "oracle_conformity": oracle,
        "cross_implementation_comparison": comparison,
        "execution_source_separation": separation,
        "execution_origin": execution_origin,
        "profile_issuance_blocking": True,
        "trace": TRACE_STAGES,
    }
    agreement = receipt.get("implementation_agreement", False)
    expected = {
        "returncode": case["expected_returncode"],
        "status": case["expected_status"],
        "agreement": case["expected_implementation_agreement"],
        "oracle": case["expected_oracle_conformity"],
        "comparison": case["expected_cross_implementation_comparison"],
        "separation": case["expected_execution_source_separation"],
        "origin": case["expected_execution_origin"],
    }
    actual = {
        "returncode": observation["returncode"],
        "status": receipt["status"],
        "agreement": agreement,
        "oracle": oracle,
        "comparison": comparison,
        "separation": separation,
        "origin": execution_origin,
    }
    if actual != expected:
        raise EvidenceError(f"trial_observation:{case['case_id']}")
    return observation


def expect_error(expected: str, function: Any, *args: Any, **kwargs: Any) -> None:
    try:
        function(*args, **kwargs)
    except EvidenceError as exc:
        if str(exc) != expected:
            raise EvidenceError(f"known_bad_wrong_error:{expected}:{exc}") from exc
        return
    raise EvidenceError(f"known_bad_accepted:{expected}")


def run_meta_gate(contract: dict[str, Any], corpus: dict[str, Any], candidate_raw: bytes) -> int:
    gate_cases = {case["case_id"]: case for case in corpus["gate_known_bads"]}
    checks = 0

    def expected(case_id: str) -> str:
        return gate_cases[case_id]["expected_error"]

    try:
        expect_error("meta_delegate_blindness", lambda: None)
    except EvidenceError as exc:
        if str(exc) != expected("meta_delegate_blindness"):
            raise EvidenceError(f"meta_delegate_blindness_control:{exc}") from exc
        checks += 1
    else:
        raise EvidenceError("meta_delegate_blindness_control_failed")

    mutant = copy.deepcopy(contract)
    mutant["unexpected"] = True
    expect_error(expected("contract_closed_shape"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    expect_error(expected("binding_path_replacement"), secure_repo_file, "../outside")
    checks += 1
    mutant = copy.deepcopy(contract)
    mutant["subject_bindings"][0]["sha256"] = "0" * 64
    expect_error(expected("binding_digest_replacement"), validate_contract, mutant)
    checks += 1
    mutant = copy.deepcopy(contract)
    for key in ("path", "sha256", "bytes"):
        mutant["subject_bindings"][0][key] = contract["subject_bindings"][1][key]
    expect_error(expected("role_path_swap"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    mutant = copy.deepcopy(contract)
    mutant["subject_bindings"][0]["path"] = (
        "tests/canonicalization/./compare_results.py"
    )
    expect_error(expected("lexical_path_alias"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    mutant = copy.deepcopy(contract)
    mutant["trace_stages"][0], mutant["trace_stages"][1] = mutant["trace_stages"][1], mutant["trace_stages"][0]
    expect_error(expected("trace_stage_reorder"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    for case_id, field in (
        ("private_holdout_claim", "claims_private_holdout"),
        ("human_calibration_claim", "claims_human_calibration"),
        ("prompt_injection_coverage_claim", "claims_prompt_injection_coverage"),
        ("executes_canonicalizers_claim", "executes_canonicalizers"),
        ("repairs_comparator_claim", "repairs_comparator"),
        (
            "organizational_independence_claim",
            "claims_organizational_independence",
        ),
    ):
        mutant = copy.deepcopy(contract)
        mutant["declared_scope"][field] = True
        expect_error(expected(case_id), validate_contract, mutant, verify_bytes=False)
        checks += 1
    for case_id, field in (
        ("profile_issuance_claim", "profile_issuance"),
        ("gate_a_authority_claim", "gate_a_acceptance"),
        ("runtime_authority_claim", "runtime"),
        ("deployment_authority_claim", "deployment"),
        ("publication_authority_claim", "publication"),
        ("credentials_authority_claim", "credentials"),
        ("authority_claim", "external_effects"),
    ):
        mutant = copy.deepcopy(contract)
        mutant["authority"][field] = True
        expect_error(expected(case_id), validate_contract, mutant, verify_bytes=False)
        checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["cases"].pop()
    expect_error(expected("case_census_reduction"), validate_cases, mutant_corpus, candidate_raw)
    checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["gate_known_bads"][0]["expected_error"] = "always_pass"
    expect_error(expected("expected_error_replacement"), validate_cases, mutant_corpus, candidate_raw)
    checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["candidate_binding"]["sha256"] = "0" * 64
    expect_error(expected("candidate_binding_replacement"), validate_cases, mutant_corpus, candidate_raw)
    checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["cases"][1]["expected_execution_source_separation"] = "proven_within_declared_scope"
    expect_error(expected("case_disposition_weakening"), validate_cases, mutant_corpus, candidate_raw)
    checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["cases"][2]["mutation"] = "none"
    expect_error(expected("case_mutation_replacement"), validate_cases, mutant_corpus, candidate_raw)
    checks += 1
    original_left_raw = PYTHON_RESULT_PATH.read_bytes()
    original_right_raw = NODE_RESULT_PATH.read_bytes()
    original_left = strict_load_bytes(original_left_raw, "noop_left")
    original_right = strict_load_bytes(original_right_raw, "noop_right")
    expect_error(
        expected("clone_mutation_noop"),
        verify_mutation_postcondition,
        "clone_python_and_relabel_node",
        original_left,
        original_right,
        original_left_raw,
        original_right_raw,
        original_left_raw,
        original_right_raw,
        {
            "mutation": "clone_python_and_relabel_node",
            "source_left_raw_sha256": sha256_bytes(original_left_raw),
            "source_right_raw_sha256": sha256_bytes(original_right_raw),
            "source_left_object_sha256": sha256_bytes(canonical_bytes(original_left)),
            "source_right_object_sha256": sha256_bytes(canonical_bytes(original_right)),
            "intermediate_clone_object_sha256": sha256_bytes(
                canonical_bytes(original_left)
            ),
            "output_left_raw_sha256": sha256_bytes(original_left_raw),
            "output_right_raw_sha256": sha256_bytes(original_right_raw),
        },
    )
    checks += 1
    expect_error(
        expected("duplicate_json_key"),
        strict_load_bytes,
        b'{"a":1,"a":2}',
        "duplicate_key_probe",
    )
    checks += 1

    def final_symlink_probe() -> None:
        with tempfile.TemporaryDirectory(prefix="odeya-binding-symlink-") as name:
            root = Path(name)
            (root / "target.json").write_text("{}\n", encoding="utf-8")
            (root / "link.json").symlink_to("target.json")
            secure_regular_file(root, "link.json")

    expect_error(expected("final_symlink_binding"), final_symlink_probe)
    checks += 1

    def ancestor_symlink_probe() -> None:
        with tempfile.TemporaryDirectory(prefix="odeya-binding-ancestor-") as name:
            root = Path(name)
            (root / "real").mkdir()
            (root / "real/data.json").write_text("{}\n", encoding="utf-8")
            (root / "linked").symlink_to("real", target_is_directory=True)
            secure_regular_file(root, "linked/data.json")

    expect_error(expected("ancestor_symlink_binding"), ancestor_symlink_probe)
    checks += 1
    mutant_corpus = copy.deepcopy(corpus)
    mutant_corpus["timeout_seconds"] = TIMEOUT_SECONDS + 1
    expect_error(
        expected("timeout_configuration_weakening"),
        validate_cases,
        mutant_corpus,
        candidate_raw,
    )
    checks += 1

    def timeout_probe() -> None:
        result = run_fixed_process(
            [sys.executable, "-c", "import time; time.sleep(1)"],
            ROOT,
            0.01,
        )
        if result["timed_out"]:
            raise EvidenceError("infrastructure_timeout")

    expect_error(expected("timeout_control"), timeout_probe)
    checks += 1
    mutant = copy.deepcopy(contract)
    mutant["baseline_classification"]["profile_issuance_blocking"] = False
    expect_error(expected("blinded_gate"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    mutant = copy.deepcopy(contract)
    mutant["subject_bindings"][1]["path"] = mutant["subject_bindings"][0]["path"]
    expect_error(expected("duplicate_probe_subject"), validate_contract, mutant, verify_bytes=False)
    checks += 1
    return checks


def validate() -> dict[str, Any]:
    candidate_raw = CONTRACT_PATH.read_bytes()
    contract = strict_load_bytes(candidate_raw, CONTRACT_PATH.relative_to(ROOT).as_posix())
    corpus = strict_load(CASES_PATH)
    validate_contract(contract)
    validate_cases(corpus, candidate_raw)
    repeated_trials: list[dict[str, Any]] = []
    for case in corpus["cases"]:
        observations = [run_trial(case) for _ in range(REPETITIONS)]
        if canonical_bytes(observations[0]) != canonical_bytes(observations[1]):
            raise EvidenceError(f"trial_not_reproducible:{case['case_id']}")
        repeated_trials.append(
            {
                "case_id": case["case_id"],
                "repetitions": REPETITIONS,
                "observation_sha256": sha256_bytes(canonical_bytes(observations[0])),
                **observations[0],
            }
        )
    meta_checks = run_meta_gate(contract, corpus, candidate_raw)
    return {
        "status": "pass",
        "candidate_status": "blocking",
        "profile_issued": False,
        "trial_count": len(repeated_trials),
        "trial_repetitions": REPETITIONS,
        "meta_known_bad_count": meta_checks,
        "trials": repeated_trials,
        "baseline": repeated_trials[0],
        "copied_output_false_accept": repeated_trials[1],
        "nonclaims": {
            "comparator_repaired": False,
            "causal_execution_proven": False,
            "organizational_independence_proven": False,
            "gate_a_accepted": False,
            "runtime_authorized": False,
        },
    }


def main() -> int:
    if len(sys.argv) != 1:
        print(json.dumps({"status": "fail", "errors": ["usage:no_arguments"]}, sort_keys=True))
        return 2
    try:
        receipt = validate()
    except (OSError, EvidenceError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "errors": [str(exc)]}, indent=2, sort_keys=True))
        return 1
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
