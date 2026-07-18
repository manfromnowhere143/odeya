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
COMMAND_REGISTRY_ID = "urn:odeya:schema:command-contract-registry:0.7.0"
COMMAND_RECORD_ID = "urn:odeya:schema:command-contract-record:0.6.0"
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


def manifest_failures(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if manifest.get("contract_status") != "architecture_only_non_admitted" or manifest.get("usable_for_admission") is not False:
        failures.append("manifest must remain architecture-only and unusable for admission")
    case_names = {case["name"] for case in manifest["cases"]}
    if set(manifest.get("exact_mismatch_reason_sets", {})) != case_names:
        failures.append("exact mismatch-reason inventory must cover every case exactly once")
    return failures


def baseline_failures(validators: dict, subjects: dict) -> list[str]:
    failures: list[str] = []
    for name, validator in validators.items():
        validation_errors = sorted(
            validator.iter_errors(subjects[name]),
            key=lambda error: list(error.absolute_path),
        )
        if validation_errors:
            failures.append(f"baseline {name} fixture is not structurally valid: {validation_errors[0].message}")
    return failures


def evaluate_cases(cases: list, subjects: dict, validators: dict,
                   schemas_by_id: dict, manifest: dict) -> tuple[list[str], int]:
    """Run every case. Factored out of main so the harness's own hygiene
    guards can be exercised by a self-test (ADR 0080): a malformed case
    cannot live in the retained set, so before this every hygiene guard had
    no proof and the generalized audit measured this suite at 0 of 10."""
    failures: list[str] = []
    exact_reason_sets = manifest.get("exact_mismatch_reason_sets", {})
    passed = 0
    for case in cases:
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
    return failures, passed


def build_context(manifest: dict) -> tuple[dict, dict, dict]:
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
            schema, registry=registry, format_checker=FormatChecker()
        )
    return subjects, validators, schemas_by_id


def harness_self_test_meta_proof(subjects: dict, validators: dict,
                                 schemas_by_id: dict, manifest: dict) -> list[str]:
    """Prove the self-test's own refusal statements are load-bearing.

    Blinding the case evaluator makes every per-case probe fail
    unconditionally; the exact count of DISTINCT refusals is asserted, so a
    duplicated probe collapses the set and is caught (ADR 0069/0080).
    """
    blind = lambda cases, s, v, sb, mf: ([], 0)  # noqa: E731
    distinct = {
        f for f in harness_self_test(subjects, validators, schemas_by_id, manifest, evaluator=blind)
    }
    if len(distinct) != 4:
        return [
            f"harness meta self-test: blinding the evaluator produced {len(distinct)} distinct "
            "refusals, expected 4; a probe is duplicated or a refusal is not load-bearing"
        ]
    return []


def harness_self_test(subjects: dict, validators: dict, schemas_by_id: dict,
                      manifest: dict, evaluator=None) -> list[str]:
    """Prove the harness's hygiene guards fire (law 11, ADR 0066/0080).

    Each synthetic case is malformed in exactly one way and must be refused
    by exactly one guard; probe subjects are required distinct. The
    manifest-level and baseline guards, which sit outside the per-case loop,
    are driven with deliberately-broken inputs. The defensive
    usable-for-admission guard and the unresolved-reason-drift guard require
    real evaluate semantics that no synthetic case reaches without deep
    reconstruction, and are recorded as open in ADR 0081 rather than
    asserted here.
    """
    run = evaluator or evaluate_cases
    failures: list[str] = []
    probed: list = []
    ok_name = manifest["cases"][0]["name"]

    def refuses_case(case: dict, expected: str, label: str) -> None:
        if any(case == earlier for earlier in probed):
            failures.append(f"harness self-test: {label} duplicates an earlier probe subject")
        probed.append(copy.deepcopy(case))
        observed, _ = run([case], subjects, validators, schemas_by_id, manifest)
        if not any(expected in failure for failure in observed):
            failures.append(f"harness self-test: {label} was not refused; got {observed}")

    obj = next(iter(subjects))
    refuses_case(
        {"name": ok_name, "mutations": [{"object": "no-such-object", "op": "replace",
                                         "path": "/x", "value": 1}]},
        "mutation failed", "an unresolvable mutation object")
    refuses_case(
        {"name": ok_name, "mutations": [], "comparison_overrides": [
            {"object": "no-such-object", "op": "replace", "path": "/x", "value": 1}]},
        "comparison override failed", "an unresolvable comparison override")
    refuses_case(
        {"name": ok_name, "mutations": [], "expected_status": "odeya-self-test-wrong-status",
         "expected_reasons": []},
        "expected ", "a wrong expected status")
    # The clean baseline evaluates to blocked_unresolved_identity; declaring
    # that exact status passes the status guard so the missing-reasons guard
    # is the one this probe reaches.
    baseline_status = evaluate(copy.deepcopy(subjects), set(schemas_by_id))["status"]
    refuses_case(
        {"name": ok_name, "mutations": [], "expected_status": baseline_status,
         "expected_reasons": ["odeya-self-test-never-produced"]},
        "missing expected reasons", "an expected reason the result never produces")
    # The mismatch-reason-drift and unresolved-reason-drift guards fire only
    # after the status and missing-reason checks pass with real evaluate
    # semantics AND the exact retained set differs from what the case
    # produces. No synthetic case reaches that state without reconstructing a
    # full drift, and the defensive usable-for-admission guard is unreachable
    # while evaluate never admits. All three are recorded open in ADR 0081,
    # not asserted here -- claiming them would be the fiction this suite exists
    # to prevent.

    # Manifest-level guards, driven with broken manifests.
    if not manifest_failures({**manifest, "contract_status": "admitted"}):
        failures.append("harness self-test: an admittable manifest was not refused")
    if not manifest_failures({**manifest, "exact_mismatch_reason_sets": {}}):
        failures.append("harness self-test: an incomplete reason inventory was not refused")

    # Baseline guard, driven with a structurally-broken fixture.
    if validators:
        first = next(iter(validators))
        broken = {name: (copy.deepcopy(subj) if name != first else {"odeya": "broken"})
                  for name, subj in subjects.items()}
        if not baseline_failures(validators, broken):
            failures.append("harness self-test: a structurally invalid baseline was not refused")
    return failures


def main() -> int:
    manifest = load(MANIFEST)
    subjects, validators, schemas_by_id = build_context(manifest)
    failures: list[str] = manifest_failures(manifest)
    failures.extend(baseline_failures(validators, subjects))
    failures.extend(harness_self_test(subjects, validators, schemas_by_id, manifest))
    failures.extend(harness_self_test_meta_proof(subjects, validators, schemas_by_id, manifest))
    case_failures, passed = evaluate_cases(
        manifest["cases"], subjects, validators, schemas_by_id, manifest
    )
    failures.extend(case_failures)

    if failures:
        print("Command identity contract validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Command identity contract validation passed: {passed} typed non-admission cases; no subject usable for admission.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
