#!/usr/bin/env python3
"""Check command identity equality without pretending unresolved subjects are admitted."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests/command-identity-contracts/cases.json"
COMMAND_REGISTRY_ID = "urn:odeya:schema:command-contract-registry:0.4.0"
COMMAND_RECORD_ID = "urn:odeya:schema:command-contract-record:0.3.0"
EXACT_RESOLUTION_MODE = "preloaded_exact_resource_id"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def apply_mutation(subject: Any, mutation: dict[str, Any]) -> None:
    tokens = pointer_tokens(mutation["path"])
    parent = subject
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = tokens[-1]
    operation = mutation["op"]
    if isinstance(parent, list):
        index = int(final)
        if operation == "replace":
            parent[index] = mutation["value"]
        elif operation == "remove":
            del parent[index]
        elif operation == "add":
            parent.insert(index, mutation["value"])
        else:
            raise ValueError(f"unsupported mutation operation: {operation!r}")
    elif isinstance(parent, dict):
        if operation == "replace":
            if final not in parent:
                raise KeyError(final)
            parent[final] = mutation["value"]
        elif operation == "remove":
            del parent[final]
        elif operation == "add":
            if final in parent:
                raise ValueError(f"add target exists: {final!r}")
            parent[final] = mutation["value"]
        else:
            raise ValueError(f"unsupported mutation operation: {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def add_if_unequal(reasons: set[str], code: str, *values: Any) -> None:
    if len({json.dumps(value, sort_keys=True) for value in values}) != 1:
        reasons.add(code)


def semantic_version_from_resource_id(resource_id: str) -> str | None:
    candidate = resource_id.rsplit(":", 1)[-1]
    parts = candidate.split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        return candidate
    return None


def schema_refs(record: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    refs = [
        ("payload", record["payload_contract"]["schema_ref"]),
        ("handler_input", record["handler_port_contract"]["input_schema_ref"]),
    ]
    output_ref = record["handler_port_contract"]["decision_output_schema_ref"]
    if output_ref is not None:
        refs.append(("handler_output", output_ref))
    return refs


def evaluate(subjects: dict[str, dict[str, Any]], preloaded_ids: set[str]) -> dict[str, Any]:
    envelope = subjects["envelope"]
    receipt = subjects["receipt"]
    record = subjects["record"]
    registry = subjects["registry"]
    envelope_ref = envelope["command_contract_record_ref"]
    receipt_ref = receipt["command_contract_record_ref"]
    envelope_registry = envelope["command_registry_snapshot_ref"]
    receipt_registry = receipt["command_registry_snapshot_ref"]
    reasons: set[str] = set()

    add_if_unequal(reasons, "command_id_mismatch", envelope["command_id"], receipt["command_id"])
    add_if_unequal(
        reasons,
        "canonical_request_digest_mismatch",
        envelope["canonical_request_digest"],
        receipt["canonical_request_digest"],
    )
    add_if_unequal(
        reasons,
        "registry_activation_reference_mismatch",
        envelope["command_registry_activation_ref"],
        receipt["command_registry_activation_ref"],
    )
    add_if_unequal(
        reasons,
        "idempotency_scope_mismatch",
        envelope["idempotency_scope"],
        receipt["idempotency_scope"],
    )

    add_if_unequal(reasons, "envelope_receipt_command_type_mismatch", envelope["command_type"], receipt["command_type"])
    add_if_unequal(reasons, "envelope_nested_command_type_mismatch", envelope["command_type"], envelope_ref["command_type"])
    add_if_unequal(reasons, "receipt_nested_command_type_mismatch", receipt["command_type"], receipt_ref["command_type"])
    add_if_unequal(reasons, "record_command_type_mismatch", envelope["command_type"], record["command_type"])

    add_if_unequal(reasons, "envelope_receipt_command_version_mismatch", envelope["command_version"], receipt["command_version"])
    add_if_unequal(reasons, "envelope_nested_command_version_mismatch", envelope["command_version"], envelope_ref["command_version"])
    add_if_unequal(reasons, "receipt_nested_command_version_mismatch", receipt["command_version"], receipt_ref["command_version"])
    add_if_unequal(reasons, "record_command_version_mismatch", envelope["command_version"], record["command_version"])

    add_if_unequal(reasons, "envelope_receipt_payload_type_mismatch", envelope["payload_type_id"], receipt["payload_type_id"])
    add_if_unequal(reasons, "envelope_nested_payload_type_mismatch", envelope["payload_type_id"], envelope_ref["payload_type_id"])
    add_if_unequal(reasons, "receipt_nested_payload_type_mismatch", receipt["payload_type_id"], receipt_ref["payload_type_id"])
    add_if_unequal(reasons, "record_payload_type_mismatch", envelope["payload_type_id"], record["payload_type_id"])

    expected_member_key = f"{record['command_type']}@{record['command_version']}"
    if record["member_key"] != expected_member_key:
        reasons.add("record_member_key_mismatch")

    payload_schema_ref = record["payload_contract"]["schema_ref"]
    add_if_unequal(
        reasons,
        "envelope_receipt_payload_resource_mismatch",
        envelope["payload_schema_resource_id"],
        receipt["payload_schema_resource_id"],
    )
    add_if_unequal(
        reasons,
        "envelope_receipt_payload_canonical_digest_mismatch",
        envelope["payload_schema_canonical_digest"],
        receipt["payload_schema_canonical_digest"],
    )
    add_if_unequal(
        reasons,
        "envelope_receipt_payload_closure_digest_mismatch",
        envelope["payload_schema_closure_digest"],
        receipt["payload_schema_closure_digest"],
    )
    add_if_unequal(
        reasons,
        "envelope_nested_payload_resource_mismatch",
        envelope["payload_schema_resource_id"],
        envelope_ref["payload_schema_resource_id"],
    )
    add_if_unequal(
        reasons,
        "receipt_nested_payload_resource_mismatch",
        receipt["payload_schema_resource_id"],
        receipt_ref["payload_schema_resource_id"],
    )
    add_if_unequal(
        reasons,
        "record_payload_resource_mismatch",
        envelope["payload_schema_resource_id"],
        payload_schema_ref["resource_id"],
    )
    add_if_unequal(
        reasons,
        "envelope_nested_payload_canonical_digest_mismatch",
        envelope["payload_schema_canonical_digest"],
        envelope_ref["payload_schema_canonical_digest"],
    )
    add_if_unequal(
        reasons,
        "receipt_nested_payload_canonical_digest_mismatch",
        receipt["payload_schema_canonical_digest"],
        receipt_ref["payload_schema_canonical_digest"],
    )
    add_if_unequal(
        reasons,
        "envelope_nested_payload_closure_digest_mismatch",
        envelope["payload_schema_closure_digest"],
        envelope_ref["payload_schema_closure_digest"],
    )
    add_if_unequal(
        reasons,
        "receipt_nested_payload_closure_digest_mismatch",
        receipt["payload_schema_closure_digest"],
        receipt_ref["payload_schema_closure_digest"],
    )

    add_if_unequal(reasons, "record_reference_id_mismatch", envelope_ref["record_id"], receipt_ref["record_id"])
    add_if_unequal(reasons, "record_reference_version_mismatch", envelope_ref["version"], receipt_ref["version"])
    add_if_unequal(reasons, "record_reference_schema_id_mismatch", envelope_ref["schema_id"], receipt_ref["schema_id"])
    add_if_unequal(reasons, "record_reference_digest_mismatch", envelope_ref["digest"], receipt_ref["digest"])
    add_if_unequal(reasons, "record_reference_registry_digest_mismatch", envelope_ref["registry_snapshot_digest"], receipt_ref["registry_snapshot_digest"])
    add_if_unequal(reasons, "registry_reference_id_mismatch", envelope_registry["registry_id"], receipt_registry["registry_id"])
    add_if_unequal(reasons, "registry_reference_version_mismatch", envelope_registry["version"], receipt_registry["version"])
    add_if_unequal(reasons, "registry_reference_schema_id_mismatch", envelope_registry["schema_id"], receipt_registry["schema_id"])
    add_if_unequal(reasons, "registry_reference_digest_mismatch", envelope_registry["digest"], receipt_registry["digest"])
    add_if_unequal(reasons, "record_subject_id_mismatch", envelope_ref["record_id"], record["record_id"])
    add_if_unequal(reasons, "registry_subject_id_mismatch", envelope_registry["registry_id"], registry["registry_id"])
    add_if_unequal(reasons, "registry_subject_version_mismatch", envelope_registry["version"], registry["version"])
    add_if_unequal(reasons, "membership_proof_mismatch", envelope_ref["membership_proof_ref"], receipt_ref["membership_proof_ref"])
    add_if_unequal(
        reasons,
        "envelope_record_registry_digest_mismatch",
        envelope_registry["digest"],
        envelope_ref["registry_snapshot_digest"],
    )
    add_if_unequal(
        reasons,
        "receipt_record_registry_digest_mismatch",
        receipt_registry["digest"],
        receipt_ref["registry_snapshot_digest"],
    )
    if envelope_registry["schema_id"] != COMMAND_REGISTRY_ID or receipt_registry["schema_id"] != COMMAND_REGISTRY_ID:
        reasons.add("command_registry_resource_identity_mismatch")
    if envelope_ref["schema_id"] != COMMAND_RECORD_ID or receipt_ref["schema_id"] != COMMAND_RECORD_ID:
        reasons.add("command_record_resource_identity_mismatch")

    registry_member = registry["members"].get(expected_member_key)
    if registry_member is None:
        reasons.add("registry_member_missing")
    elif registry_member != record:
        reasons.add("registry_embedded_record_mismatch")

    canonical_profiles: list[Any] = [record["canonicalization_profile_ref"]]
    for _, ref in schema_refs(record):
        semantic_version = semantic_version_from_resource_id(ref["resource_id"])
        if semantic_version != ref["semantic_version"]:
            reasons.add("schema_resource_semantic_version_mismatch")
        if ref["schema_member_key"] != f"{ref['resource_id']}@{ref['semantic_version']}":
            reasons.add("schema_member_key_mismatch")
        closure = ref["closure_identity"]
        if closure["root_resource_id"] != ref["resource_id"]:
            reasons.add("closure_root_resource_mismatch")
        if (
            closure["resolution_mode"] != EXACT_RESOLUTION_MODE
            or closure["network_access"] != "disabled"
            or closure["unresolved_reference_disposition"] != "reject"
            or closure["reference_cycles"] != "forbidden"
        ):
            reasons.add("schema_resolution_contract_violation")
        canonical_profiles.append(ref["canonical_identity"]["canonicalization_profile_ref"])
    if len({json.dumps(value, sort_keys=True) for value in canonical_profiles}) != 1:
        reasons.add("canonicalization_profile_mismatch")

    unresolved: set[str] = set()
    for label, ref in schema_refs(record):
        if ref["resource_id"] not in preloaded_ids:
            unresolved.add(f"unresolved_{label}_schema_resource")
        if ref["blob_identity"]["blob_digest"] is None:
            unresolved.add(f"unresolved_{label}_blob_identity")
        if ref["canonical_identity"]["canonical_digest"] is None:
            unresolved.add(f"unresolved_{label}_canonical_identity")
        if ref["closure_identity"]["closure_digest"] is None:
            unresolved.add(f"unresolved_{label}_closure_identity")
    if record["identity_resolution_status"] != "resolved" or record["record_digest"] is None:
        unresolved.add("unresolved_record_identity")
    if registry["identity_resolution_status"] != "resolved" or registry["registry_digest"] is None:
        unresolved.add("unresolved_registry_identity")
    unresolved.add("unresolved_registry_membership_proof")
    unresolved.add("unresolved_registry_activation_proof")

    mismatch_reasons = sorted(reasons)
    all_reasons = sorted(reasons | unresolved)
    if mismatch_reasons:
        status = "invalid_identity_mismatch"
    elif unresolved:
        status = "blocked_unresolved_identity"
    else:
        status = "resolved_but_not_admitted"
    return {
        "status": status,
        "usable_for_admission": False,
        "mismatch_reasons": mismatch_reasons,
        "unresolved_reasons": sorted(unresolved),
        "reasons": all_reasons,
    }


def main() -> int:
    manifest = load(MANIFEST)
    failures: list[str] = []
    if manifest.get("contract_status") != "architecture_only_non_admitted" or manifest.get("usable_for_admission") is not False:
        failures.append("manifest must remain architecture-only and unusable for admission")
    case_names = {case["name"] for case in manifest["cases"]}
    exact_reason_sets = manifest.get("exact_mismatch_reason_sets", {})
    if set(exact_reason_sets) != case_names:
        failures.append("exact mismatch-reason inventory must cover every case exactly once")

    schemas_by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "schemas").glob("*.json")):
        schema = load(path)
        resource_id = schema.get("$id")
        if isinstance(resource_id, str):
            schemas_by_id[resource_id] = schema
    registry = Registry().with_resources(
        (resource_id, Resource.from_contents(schema))
        for resource_id, schema in schemas_by_id.items()
    )

    subjects = {name: load(ROOT / relative) for name, relative in manifest["fixtures"].items()}
    validators: dict[str, Draft202012Validator] = {}
    for name, relative in manifest["schemas"].items():
        schema = load(ROOT / relative)
        validators[name] = Draft202012Validator(
            schema,
            registry=registry,
            format_checker=FormatChecker(),
        )
        validation_errors = sorted(
            validators[name].iter_errors(subjects[name]),
            key=lambda error: list(error.absolute_path),
        )
        if validation_errors:
            failures.append(f"baseline {name} fixture is not structurally valid: {validation_errors[0].message}")

    passed = 0
    for case in manifest["cases"]:
        case_subjects = copy.deepcopy(subjects)
        try:
            for mutation in case.get("mutations", []):
                apply_mutation(case_subjects[mutation["object"]], mutation)
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            failures.append(f"{case['name']}: mutation failed: {type(exc).__name__}: {exc}")
            continue
        structural_reasons: list[str] = []
        for name, validator in validators.items():
            if next(validator.iter_errors(case_subjects[name]), None) is not None:
                structural_reasons.append(f"structural_schema_invalid:{name}")
        if structural_reasons:
            result = {
                "status": "invalid_structural_contract",
                "usable_for_admission": False,
                "mismatch_reasons": sorted(structural_reasons),
                "unresolved_reasons": [],
                "reasons": sorted(structural_reasons),
            }
        else:
            comparison_subjects = copy.deepcopy(case_subjects)
            try:
                for override in case.get("comparison_overrides", []):
                    apply_mutation(comparison_subjects[override["object"]], override)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                failures.append(f"{case['name']}: comparison override failed: {type(exc).__name__}: {exc}")
                continue
            result = evaluate(comparison_subjects, set(schemas_by_id))
        if result["usable_for_admission"] is not False:
            failures.append(f"{case['name']}: result became usable for admission")
            continue
        if result["status"] != case["expected_status"]:
            failures.append(f"{case['name']}: expected {case['expected_status']}, got {result['status']} ({result['reasons']})")
            continue
        missing = sorted(set(case["expected_reasons"]) - set(result["reasons"]))
        if missing:
            failures.append(f"{case['name']}: missing expected reasons {missing}; got {result['reasons']}")
            continue
        expected_mismatch = sorted(exact_reason_sets.get(case["name"], []))
        if expected_mismatch != result["mismatch_reasons"]:
            failures.append(
                f"{case['name']}: mismatch reasons drifted; expected {expected_mismatch}, "
                f"got {result['mismatch_reasons']}"
            )
            continue
        expected_unresolved = (
            []
            if result["status"] == "invalid_structural_contract"
            else sorted(manifest["exact_unresolved_reason_set"])
        )
        if expected_unresolved != result["unresolved_reasons"]:
            failures.append(
                f"{case['name']}: unresolved reasons drifted; expected {expected_unresolved}, "
                f"got {result['unresolved_reasons']}"
            )
            continue
        passed += 1

    if failures:
        print("Command identity contract validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Command identity contract validation passed: {passed} typed non-admission cases; no subject usable for admission.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
