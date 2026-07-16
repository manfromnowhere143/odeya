#!/usr/bin/env python3
"""Verify the exact WorkIntent reference-resolution successor cohort.

This suite proves architecture-time byte lineage, schema validity, and explicit
failure boundaries only. It issues no canonical identity, admission, Gate A
acceptance, assignment, lease, dispatch, runtime, or external-effect authority.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/work-intent-reference-resolution"
CASES = SUITE / "cases.json"
EVIDENCE = ROOT / "architecture/work-intent-reference-resolution-evidence.json"
EVIDENCE_SCHEMA = ROOT / "schemas/work-intent-reference-resolution-evidence.schema.json"
PLACEHOLDERS = {
    "sha256:" + "1" * 64,
    "sha256:" + "2" * 64,
    "sha256:" + "3" * 64,
}
_SCHEMA_CACHE: tuple[Registry, dict[str, dict[str, Any]]] | None = None


class DuplicateKeyError(ValueError):
    pass


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def repo_path(raw: Any, errors: list[str], code: str) -> Path | None:
    if not isinstance(raw, str):
        errors.append(code)
        return None
    path = (ROOT / raw).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        errors.append(code)
        return None
    if not path.is_file() or path.is_symlink():
        errors.append(code)
        return None
    return path


def check_raw_binding(
    row: dict[str, Any],
    path_key: str,
    digest_key: str,
    bytes_key: str,
    code: str,
    errors: list[str],
) -> bytes | None:
    path = repo_path(row.get(path_key), errors, code + "_path")
    if path is None:
        return None
    raw = path.read_bytes()
    if row.get(digest_key) != digest(raw):
        errors.append(code + "_digest")
    if row.get(bytes_key) != len(raw):
        errors.append(code + "_bytes")
    return raw


def schema_registry() -> tuple[Registry, dict[str, dict[str, Any]]]:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE
    registry = Registry()
    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = load(path)
        Draft202012Validator.check_schema(schema)
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
        schemas[path.relative_to(ROOT).as_posix()] = schema
    _SCHEMA_CACHE = (registry, schemas)
    return _SCHEMA_CACHE


def validate_instance(
    schema: dict[str, Any],
    instance: Any,
    registry: Registry,
    code: str,
    errors: list[str],
) -> None:
    if list(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
            registry=registry,
        ).iter_errors(instance)
    ):
        errors.append(code)


def walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip())
    return result.stdout.strip()


def validate(candidate: dict[str, Any], include_evidence_schema: bool = True) -> list[str]:
    errors: list[str] = []
    registry, schemas = schema_registry()

    if include_evidence_schema:
        validate_instance(
            load(EVIDENCE_SCHEMA),
            candidate,
            registry,
            "evidence_schema_invalid",
            errors,
        )

    predecessor = candidate.get("predecessor", {})
    if predecessor.get("commit") != "45c1fd769a123a9bf03e8de93c2ecf127b254199":
        errors.append("predecessor_commit_mismatch")
    if predecessor.get("tree") != "39111bfa595c8b12e28b0d8de309e0b5e2f6fc99":
        errors.append("predecessor_tree_mismatch")
    if predecessor.get("retention") != "present_byte_for_byte_immutable_predecessor":
        errors.append("predecessor_retention_escalated")
    try:
        if git("rev-parse", predecessor.get("commit", "") + "^{tree}") != predecessor.get("tree"):
            errors.append("predecessor_git_tree_mismatch")
        git("merge-base", "--is-ancestor", predecessor.get("commit", ""), "HEAD")
    except (TypeError, ValueError):
        errors.append("predecessor_git_lineage_invalid")
    check_raw_binding(predecessor, "schema_path", "schema_raw_digest", "schema_bytes", "predecessor_schema", errors)
    check_raw_binding(predecessor, "candidate_path", "candidate_raw_digest", "candidate_bytes", "predecessor_candidate", errors)

    profile = candidate.get("profile_binding", {})
    if profile.get("profile_status") != "candidate_parameters_frozen_profile_unissued":
        errors.append("profile_status_escalated")
    profile_path = repo_path(profile.get("profile_core_path"), errors, "profile_core_path")
    if profile_path and profile.get("profile_core_raw_digest") != digest(profile_path.read_bytes()):
        errors.append("profile_core_digest_mismatch")

    targets = candidate.get("reference_targets", [])
    roles = [row.get("role") for row in targets if isinstance(row, dict)]
    if roles != ["source_view", "planning_epoch", "output_schema"]:
        errors.append("target_order_or_membership_invalid")
    by_role = {
        row.get("role"): row
        for row in targets
        if isinstance(row, dict) and isinstance(row.get("role"), str)
    }

    source = by_role.get("source_view", {})
    source_schema_raw = check_raw_binding(source, "schema_path", "schema_raw_digest", "schema_bytes", "source_schema", errors)
    source_raw = check_raw_binding(source, "candidate_path", "candidate_raw_digest", "candidate_bytes", "source_candidate", errors)
    source_doc = None
    if source_raw is not None:
        source_doc = json.loads(source_raw, object_pairs_hook=reject_duplicates)
        if source_doc.get("view_id") != source.get("record_id"):
            errors.append("source_record_id_mismatch")
        if source_doc.get("version") != source.get("record_version"):
            errors.append("source_record_version_mismatch")
    if source_schema_raw is not None and source_doc is not None:
        validate_instance(
            json.loads(source_schema_raw, object_pairs_hook=reject_duplicates),
            source_doc,
            registry,
            "source_candidate_schema_invalid",
            errors,
        )
    if source.get("canonical_digest") is not None:
        errors.append("source_canonical_digest_invented")
    if source.get("admission_ref") is not None:
        errors.append("source_admission_invented")

    planning = by_role.get("planning_epoch", {})
    planning_schema_raw = check_raw_binding(planning, "schema_path", "schema_raw_digest", "schema_bytes", "planning_schema", errors)
    planning_raw = check_raw_binding(planning, "candidate_path", "candidate_raw_digest", "candidate_bytes", "planning_candidate", errors)
    planning_doc = None
    if planning_raw is not None:
        planning_doc = json.loads(planning_raw, object_pairs_hook=reject_duplicates)
        if planning_doc.get("planning_epoch_id") != planning.get("record_id"):
            errors.append("planning_record_id_mismatch")
        if planning_doc.get("version") != planning.get("record_version"):
            errors.append("planning_record_version_mismatch")
    if planning_schema_raw is not None and planning_doc is not None:
        validate_instance(
            json.loads(planning_schema_raw, object_pairs_hook=reject_duplicates),
            planning_doc,
            registry,
            "planning_candidate_schema_invalid",
            errors,
        )
    bridge = planning.get("input_view_bridge", {})
    if source_raw is not None:
        expected_source_digest = digest(source_raw)
        if bridge.get("source_candidate_raw_digest") != expected_source_digest:
            errors.append("planning_source_bridge_digest_mismatch")
        if planning_doc and planning_doc.get("input_view", {}).get("digest") != expected_source_digest:
            errors.append("planning_input_view_raw_lineage_mismatch")
    if bridge.get("legacy_digest_slot_value_equal_raw_candidate") is not True:
        errors.append("planning_raw_lineage_equality_removed")
    if bridge.get("legacy_digest_slot_is_canonical_identity") is not False:
        errors.append("planning_raw_lineage_mislabeled_canonical")
    if planning.get("canonical_digest") is not None:
        errors.append("planning_canonical_digest_invented")
    if planning.get("admission_ref") is not None:
        errors.append("planning_admission_invented")

    output = by_role.get("output_schema", {})
    check_raw_binding(output, "schema_path", "schema_raw_digest", "schema_bytes", "output_schema", errors)
    if output.get("binding_status") != "exact_retained_schema_resource_raw_bytes":
        errors.append("output_schema_binding_status_invalid")
    if output.get("admission_ref") is not None:
        errors.append("output_schema_admission_invented")

    successor = candidate.get("successor", {})
    check_raw_binding(successor, "core_schema_path", "core_schema_raw_digest", "core_schema_bytes", "successor_core_schema", errors)
    check_raw_binding(successor, "core_candidate_path", "core_candidate_raw_digest", "core_candidate_bytes", "successor_core_candidate", errors)
    check_raw_binding(successor, "work_intent_schema_path", "work_intent_schema_raw_digest", "work_intent_schema_bytes", "successor_work_intent_schema", errors)
    check_raw_binding(successor, "work_intent_candidate_path", "work_intent_candidate_raw_digest", "work_intent_candidate_bytes", "successor_work_intent_candidate", errors)

    core_path = repo_path(successor.get("core_candidate_path"), errors, "successor_core_candidate_path")
    wrapper_path = repo_path(successor.get("work_intent_candidate_path"), errors, "successor_work_intent_candidate_path")
    core_schema_path = repo_path(successor.get("core_schema_path"), errors, "successor_core_schema_path")
    wrapper_schema_path = repo_path(successor.get("work_intent_schema_path"), errors, "successor_work_intent_schema_path")
    core_doc = load(core_path) if core_path else {}
    wrapper_doc = load(wrapper_path) if wrapper_path else {}
    if core_schema_path:
        validate_instance(load(core_schema_path), core_doc, registry, "successor_core_schema_invalid", errors)
    if wrapper_schema_path:
        validate_instance(load(wrapper_schema_path), wrapper_doc, registry, "successor_work_intent_schema_invalid", errors)
    if wrapper_doc.get("identity_subject", {}).get("semantic_core") != core_doc:
        errors.append("wrapper_core_equality_mismatch")

    old_core = load(ROOT / "architecture/work-intent-core-candidate.json")
    expected_core = copy.deepcopy(old_core)
    expected_core["schema_version"] = "0.2.0"
    expected_core["source_view_ref"] = core_doc.get("source_view_ref")
    expected_core["planning_epoch_ref"] = core_doc.get("planning_epoch_ref")
    expected_core["output_contract"]["schema_ref"] = core_doc.get("output_contract", {}).get("schema_ref")
    if expected_core != core_doc:
        errors.append("semantic_projection_drift")

    transform = successor.get("transformation", {})
    if transform.get("changed_core_members") != [
        "schema_version",
        "source_view_ref",
        "planning_epoch_ref",
        "output_contract.schema_ref",
    ]:
        errors.append("transformation_member_set_drift")
    if transform.get("source_and_planning_placeholder_digests_absent") is not True:
        errors.append("placeholder_absence_claim_removed")
    if transform.get("exact_output_schema_digest_equal") is not True:
        errors.append("output_schema_equality_claim_removed")
    if transform.get("raw_candidate_digests_never_labeled_canonical") is not True:
        errors.append("raw_as_canonical_prohibition_removed")
    if PLACEHOLDERS & set(walk_strings(core_doc)):
        errors.append("placeholder_digest_present")
    if source_raw is not None and core_doc.get("source_view_ref", {}).get("candidate_raw_digest") != digest(source_raw):
        errors.append("core_source_binding_mismatch")
    if planning_raw is not None and core_doc.get("planning_epoch_ref", {}).get("candidate_raw_digest") != digest(planning_raw):
        errors.append("core_planning_binding_mismatch")
    if core_doc.get("output_contract", {}).get("schema_ref", {}).get("schema_raw_digest") != output.get("schema_raw_digest"):
        errors.append("core_output_schema_binding_mismatch")
    for role in ("source_view_ref", "planning_epoch_ref"):
        ref = core_doc.get(role, {})
        if ref.get("canonical_digest") is not None:
            errors.append("core_target_canonical_digest_invented")
        if ref.get("candidate_raw_digest") == ref.get("canonical_digest"):
            errors.append("raw_candidate_digest_reused_as_canonical")

    obligations = candidate.get("proof_obligations", {})
    expected_true = {
        "predecessor_retained_exact",
        "target_schema_and_candidate_raw_bindings_exact",
        "target_records_validate_against_exact_schemas",
        "source_planning_ids_equal_successor_references",
        "planning_source_raw_lineage_equal",
        "output_schema_mismatch_removed",
    }
    expected_false = {
        "profile_issued",
        "target_canonical_identities_constructed",
        "work_intent_canonical_digest_issued",
        "work_intent_registry_member_exists",
        "cross_record_canonical_identity_equality_proven",
        "assignment_cohort_complete",
    }
    if any(obligations.get(k) is not True for k in expected_true):
        errors.append("proven_obligation_removed")
    if any(obligations.get(k) is not False for k in expected_false):
        errors.append("unproven_obligation_escalated")

    acceptance = candidate.get("acceptance_boundary", {})
    if any(acceptance.get(k) is not False for k in [
        "profile_issued",
        "target_resources_admitted",
        "work_intent_admitted",
        "same_active_root_membership_proven",
        "gate_a_accepted",
    ]) or acceptance.get("operator_acceptance_ref") is not None:
        errors.append("acceptance_boundary_escalated")

    authority = candidate.get("authority_boundary", {})
    if any(value is not False for value in authority.values()):
        errors.append("authority_boundary_escalated")
    return sorted(set(errors))


def tokens(pointer: str) -> list[str]:
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutate(document: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(document)
    parts = tokens(case["path"])
    parent: Any = result
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = parts[-1]
    if case["op"] == "remove":
        if isinstance(parent, list):
            del parent[int(key)]
        else:
            del parent[key]
    elif case["op"] == "replace":
        if isinstance(parent, list):
            parent[int(key)] = copy.deepcopy(case["value"])
        else:
            parent[key] = copy.deepcopy(case["value"])
    else:
        raise ValueError("unsupported mutation")
    return result


def main() -> int:
    evidence = load(EVIDENCE)
    errors = validate(evidence)
    if errors:
        print("WorkIntent reference resolution: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- safe candidate: {error}", file=sys.stderr)
        return 1

    cases = load(CASES)
    failures: list[str] = []
    for case in cases["known_bad_mutations"]:
        candidate = mutate(evidence, case)
        observed = validate(candidate)
        if case["expected_error"] not in observed:
            failures.append(
                f"{case['name']}: expected {case['expected_error']!r}, observed {observed!r}"
            )
    if failures:
        print("WorkIntent reference resolution mutations: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "WorkIntent reference resolution: PASS — 1 exact raw-binding candidate and "
        f"{len(cases['known_bad_mutations'])} known-bad mutations rejected; "
        "canonical profile, target canonical identities, admission, assignment, "
        "Gate A, runtime, and external effects remain blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
