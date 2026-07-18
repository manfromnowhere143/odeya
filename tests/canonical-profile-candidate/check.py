#!/usr/bin/env python3
"""Validate the nonrecursive odeya-jcs-0.1 candidate parameter freeze.

This architecture-time checker binds exact profile-core bytes to retained
conformance evidence, the current schema-domain inventory, the explicit
version axes, and the still-blocking migration audit. A pass cannot issue a
canonical identity, admit a registry member, accept Gate A, or authorize a
runtime.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/canonical-profile-candidate"
CORE = ROOT / "architecture/canonicalization-profile-core-candidate.json"
EVIDENCE = ROOT / "architecture/canonicalization-profile-candidate-evidence.json"
CORE_SCHEMA = ROOT / "schemas/canonicalization-profile-core.schema.json"
EVIDENCE_SCHEMA = (
    ROOT / "schemas/canonicalization-profile-candidate-evidence.schema.json"
)
CASES = SUITE / "cases.json"
CANONICAL_SUITE = ROOT / "tests/canonicalization"
CANONICAL_AUDIT = CANONICAL_SUITE / "SCHEMA_AUDIT.json"
GATE_INVENTORY = ROOT / "architecture/gate-a-prerequisite-closure.json"
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"
CORE_SCHEMA_ID = "urn:odeya:schema:canonicalization-profile-core:0.5.0"

EXPECTED_ARTIFACTS = {
    "docs/CANONICALIZATION_PROFILE.md": "profile_specification",
    "tests/canonicalization/manifest.json": "vector_manifest",
    "tests/canonicalization/expectations.json": "exact_expectations",
    "tests/canonicalization/source-lock.json": "dependency_and_source_lock",
    "tests/canonicalization/runner_python.py": "python_implementation",
    "tests/canonicalization/runner_node.mjs": "node_implementation",
    "tests/canonicalization/results/python-rfc8785-0.1.4.json": (
        "python_retained_result"
    ),
    "tests/canonicalization/results/node-canonicalize-3.0.0.json": (
        "node_retained_result"
    ),
    "tests/canonicalization/results/comparison-receipt.json": "comparison_receipt",
}


class DuplicateKey(ValueError):
    """Raised when JSON would otherwise silently overwrite a member."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one JSON object")
    return value


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


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
            raise ValueError(f"unsupported mutation operation {operation!r}")
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
            raise ValueError(f"unsupported mutation operation {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def schema_error_code(
    document: dict[str, Any], schema: dict[str, Any], label: str
) -> str | None:
    errors = list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(document)
    )
    return f"{label}_schema_invalid" if errors else None


def declared_domain_constants() -> dict[str, str]:
    observed: dict[str, str] = {}
    duplicates: set[str] = set()

    def visit(value: Any, schema_id: str) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "domain_separator" and isinstance(item, dict):
                    candidates: list[str] = []
                    if isinstance(item.get("const"), str):
                        candidates.append(item["const"])
                    if isinstance(item.get("enum"), list):
                        candidates.extend(
                            entry for entry in item["enum"] if isinstance(entry, str)
                        )
                    for domain in candidates:
                        if domain in observed:
                            duplicates.add(domain)
                        observed[domain] = schema_id
                visit(item, schema_id)
        elif isinstance(value, list):
            for item in value:
                visit(item, schema_id)

    for path in sorted((ROOT / "schemas").glob("*.json")):
        schema = load(path)
        schema_id = schema.get("$id")
        if not isinstance(schema_id, str):
            raise ValueError(f"{path.relative_to(ROOT)} has no string $id")
        visit(schema, schema_id)
    if duplicates:
        raise ValueError(f"duplicate declared digest domains: {sorted(duplicates)}")
    return observed


def migration_counts(audit: dict[str, Any]) -> dict[str, int]:
    summary = audit["summary"]
    return {
        "schema_count": audit["schema_count"],
        "fixture_count": audit["fixture_count"],
        "unprofiled_datetime_paths": summary[
            "unprofiled_datetime_path_count"
        ],
        "number_or_decimal_findings": (
            summary["generic_json_number_path_count"]
            + summary["generic_scientific_decimal_path_count"]
        ),
        "unscoped_digest_fields": summary[
            "digest_field_without_scope_annotation_count"
        ],
        "divergent_common_definition_names": summary[
            "divergent_common_definition_name_count"
        ],
        "unpinned_profile_bindings": summary[
            "unpinned_canonical_profile_binding_count"
        ],
        "nonconformant_fixture_timestamps": summary[
            "nonconformant_fixture_timestamp_value_count"
        ],
    }


def evaluate(
    core: dict[str, Any],
    evidence: dict[str, Any],
    *,
    skip_core_raw_binding: bool = False,
) -> set[str]:
    errors: set[str] = set()
    core_schema = load(CORE_SCHEMA)
    evidence_schema = load(EVIDENCE_SCHEMA)
    for code in (
        schema_error_code(core, core_schema, "core"),
        schema_error_code(evidence, evidence_schema, "evidence"),
    ):
        if code:
            errors.add(code)

    if core.get("candidate_status") != (
        "candidate_parameters_frozen_for_review_profile_unissued"
    ):
        errors.add("candidate_status_not_frozen_for_review")
    if core.get("profile_id") != PROFILE_ID or core.get("profile_version") != "0.1.0":
        errors.add("profile_identity_mismatch")

    bootstrap = core.get("bootstrap_boundary", {})
    if (
        bootstrap.get("core_contains_self_hash") is not False
        or bootstrap.get("core_raw_bytes_bound_externally") is not True
    ):
        errors.add("nonrecursive_bootstrap_violation")
    if bootstrap.get("operator_acceptance_ref") is not None:
        errors.add("operator_acceptance_fabricated")
    if (
        bootstrap.get("profile_aliases_allowed") is not False
        or bootstrap.get("mutable_locator_identity_allowed") is not False
    ):
        errors.add("mutable_profile_identity_allowed")

    parser = core.get("parser_contract", {})
    if parser.get("byte_order_mark") != "reject":
        errors.add("bom_not_rejected")
    if parser.get("duplicate_object_names") != "reject_before_mapping":
        errors.add("duplicate_names_not_rejected_before_mapping")
    integer_domain = parser.get("integer_domain", {})
    if (
        integer_domain.get("minimum") != -9007199254740991
        or integer_domain.get("maximum") != 9007199254740991
        or integer_domain.get("outside_domain") != "reject"
    ):
        errors.add("unsafe_integer_domain")

    canonical_manifest = load(CANONICAL_SUITE / "manifest.json")
    manifest_limits = dict(canonical_manifest["limits"])
    max_safe_integer = manifest_limits.pop("max_safe_integer")
    if parser.get("limits") != manifest_limits or integer_domain.get("maximum") != max_safe_integer:
        errors.add("parser_limits_mismatch_retained_vectors")

    serialization = core.get("serialization_contract", {})
    if (
        serialization.get("standard") != "RFC8785_JSON_Canonicalization_Scheme"
        or serialization.get("unicode_normalization") != "none"
        or serialization.get("object_member_order")
        != "raw_utf16_code_unit_ascending"
    ):
        errors.add("serialization_contract_not_exact_rfc8785_profile")

    envelope = core.get("canonical_envelope_contract", {})
    if envelope.get("exact_members") != ["profile_id", "schema_id", "subject"]:
        errors.add("canonical_envelope_members_mismatch")
    if (
        envelope.get("schema_aliases_allowed") is not False
        or envelope.get("self_digest_inside_subject") != "forbidden"
    ):
        errors.add("canonical_envelope_fail_closed_boundary_lost")

    digest_contract = core.get("canonical_object_digest_contract", {})
    if digest_contract.get("canonical_digest") is not None:
        errors.add("canonical_digest_fabricated")
    if (
        digest_contract.get("algorithm") != "sha-256"
        or digest_contract.get("preimage")
        != "utf8_rfc8785_bytes_of_exact_canonical_envelope"
        or digest_contract.get("signatures_inside_preimage") is not False
    ):
        errors.add("canonical_digest_framing_mismatch")

    reference = core.get("prospective_profile_reference_contract", {})
    expected_reference_members = [
        "profile_id",
        "profile_version",
        "profile_core_schema_id",
        "profile_core_raw_digest",
    ]
    if (
        reference.get("exact_members") != expected_reference_members
        or reference.get("profile_id") != PROFILE_ID
        or reference.get("profile_core_schema_id") != CORE_SCHEMA_ID
        or reference.get("admission_rule") != "same_active_root_exact_member"
    ):
        errors.add("prospective_profile_reference_shape_mismatch")
    if reference.get("current_consumer_migration_complete") is not False:
        errors.add("current_consumer_migration_fabricated")

    gate_inventory = load(GATE_INVENTORY)
    expected_axes = gate_inventory["explicit_version_axes"]
    axes = core.get("version_axes", [])
    axis_ids = [item.get("axis_id") for item in axes if isinstance(item, dict)]
    if axis_ids != expected_axes or len(axis_ids) != len(set(axis_ids)):
        errors.add("explicit_version_axes_mismatch")
    if any(
        not isinstance(item, dict)
        or item.get("implicit_upcast") != "forbidden"
        or item.get("equality_policy") != "explicit_declared_binding_only"
        or item.get("conversion_policy")
        != "explicit_versioned_conversion_rule_only"
        for item in axes
    ):
        errors.add("implicit_version_conversion_allowed")

    observed_domains = declared_domain_constants()
    registrations = core.get("domain_registry", [])
    represented_domains = {
        item.get("domain_separator"): item.get("declaring_schema_id")
        for item in registrations
        if isinstance(item, dict)
    }
    domain_names = [
        item.get("domain_separator")
        for item in registrations
        if isinstance(item, dict)
    ]
    if (
        represented_domains != observed_domains
        or domain_names != sorted(domain_names)
        or len(domain_names) != len(set(domain_names))
    ):
        errors.add("declared_domain_registry_mismatch")

    # Prospective reservations: names accepted under the disposition record,
    # awaiting their declaring constants in the reissue wave. Reserved names
    # must be sorted, unique, disjoint from every declared constant, and carry
    # exactly the reservation status and source.
    prospective = core.get("prospective_domain_registry", [])
    prospective_names = [
        item.get("domain_separator") for item in prospective if isinstance(item, dict)
    ]
    if (
        prospective_names != sorted(prospective_names)
        or len(prospective_names) != len(set(prospective_names))
        or any(name in represented_domains for name in prospective_names)
        or any(
            not isinstance(item, dict)
            or item.get("registration_status") != "prospective_name_reserved_no_declaring_constant"
            or item.get("reservation_source")
            != "architecture/canonicalization-disposition-acceptance.json"
            for item in prospective
        )
    ):
        errors.add("prospective_domain_registry_invalid")

    authority = core.get("authority_boundary", {})
    if not isinstance(authority, dict) or any(value is not False for value in authority.values()):
        errors.add("profile_core_authority_fabricated")

    if evidence.get("candidate_status") != (
        "candidate_parameters_frozen_profile_unissued_gate_a_blocked"
    ):
        errors.add("candidate_evidence_status_mismatch")
    binding = evidence.get("profile_core_binding", {})
    if (
        binding.get("profile_id") != core.get("profile_id")
        or binding.get("profile_version") != core.get("profile_version")
        or binding.get("profile_core_schema_id") != CORE_SCHEMA_ID
        or binding.get("core_contains_self_hash") is not False
        or binding.get("binding_is_external_to_core") is not True
    ):
        errors.add("profile_core_binding_mismatch")
    if not skip_core_raw_binding:
        if (
            binding.get("profile_core_raw_digest") != sha256(CORE)
            or binding.get("profile_core_bytes") != len(CORE.read_bytes())
        ):
            errors.add("profile_core_raw_binding_mismatch")
    if (
        binding.get("profile_core_schema_raw_digest") != sha256(CORE_SCHEMA)
        or binding.get("profile_core_schema_bytes") != len(CORE_SCHEMA.read_bytes())
    ):
        errors.add("profile_core_schema_raw_binding_mismatch")

    conformance = evidence.get("conformance_evidence", {})
    artifact_rows = conformance.get("artifacts", [])
    artifact_map = {
        item.get("path"): item
        for item in artifact_rows
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    if (
        set(artifact_map) != set(EXPECTED_ARTIFACTS)
        or len(artifact_rows) != len(artifact_map)
        or any(
            artifact_map.get(path, {}).get("role") != role
            for path, role in EXPECTED_ARTIFACTS.items()
        )
    ):
        errors.add("conformance_artifact_inventory_mismatch")
    for path, row in artifact_map.items():
        target = ROOT / path
        if not target.is_file() or target.is_symlink():
            errors.add("conformance_artifact_missing_or_unsafe")
            continue
        if row.get("raw_digest") != sha256(target) or row.get("bytes") != len(
            target.read_bytes()
        ):
            errors.add("conformance_artifact_raw_binding_mismatch")

    receipt = load(CANONICAL_SUITE / "results/comparison-receipt.json")
    expected_summary = {
        "suite_id": canonical_manifest["suite_id"],
        "profile_id": canonical_manifest["profile_id"],
        "evidence_label": canonical_manifest["evidence_label"],
        "case_count": receipt["case_count"],
        "accepted_count": receipt["accepted_count"],
        "refused_count": receipt["refused_count"],
        "unclassified_error_count": 0,
        "metamorphic_relation_count": receipt["metamorphic_relation_count"],
        "implementation_agreement": receipt["implementation_agreement"],
    }
    if any(conformance.get(key) != value for key, value in expected_summary.items()):
        errors.add("conformance_summary_mismatch")
    if receipt.get("status") != "pass" or receipt.get("errors") != []:
        errors.add("retained_comparison_receipt_not_pass")
    if conformance.get("organizational_independence_proven") is not False:
        errors.add("organizational_independence_fabricated")
    if conformance.get("independent_host_reproduction_complete") is not False:
        errors.add("independent_host_reproduction_fabricated")

    domain_evidence = evidence.get("declared_domain_inventory", {})
    if (
        domain_evidence.get("declared_domain_count") != len(observed_domains)
        or domain_evidence.get("domain_constants_unique") is not True
        or domain_evidence.get("profile_core_matches_current_schema_constants")
        is not True
        or domain_evidence.get("current_consumers_admitted") is not False
    ):
        errors.add("declared_domain_evidence_mismatch")

    audit = load(CANONICAL_AUDIT)
    migration = evidence.get("migration_snapshot", {})
    if migration.get("audit_raw_digest") != sha256(CANONICAL_AUDIT):
        errors.add("canonical_audit_raw_binding_mismatch")
    if migration.get("audit_gate_a_disposition") != audit.get("gate_a_disposition"):
        errors.add("canonical_audit_disposition_mismatch")
    for key, expected in migration_counts(audit).items():
        if migration.get(key) != expected:
            errors.add("migration_snapshot_count_mismatch")
    if (
        migration.get("candidate_profile_parameters_frozen_for_review") is not True
        or migration.get("candidate_digest_framing_frozen_for_review") is not True
        or migration.get("candidate_profile_reference_shape_frozen_for_review")
        is not True
    ):
        errors.add("candidate_parameter_freeze_evidence_missing")
    if (
        migration.get("current_consumer_migration_complete") is not False
        or migration.get("all_blocking_findings_resolved_or_versioned") is not False
        or migration.get("profile_final_acceptance_complete") is not False
    ):
        errors.add("migration_or_acceptance_completion_fabricated")

    acceptance = evidence.get("acceptance_boundary", {})
    for key in (
        "profile_core_canonical_digest",
        "operator_acceptance_ref",
        "canonical_profile_registry_member_ref",
        "engine_contract_root_ref",
    ):
        if acceptance.get(key) is not None:
            errors.add("acceptance_subject_fabricated")
    for key in (
        "canonical_identity_may_be_issued",
        "gate_a_complete",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
    ):
        if acceptance.get(key) is not False:
            errors.add("acceptance_authority_fabricated")
    return errors


def main() -> int:
    try:
        core = load(CORE)
        evidence = load(EVIDENCE)
        cases = load(CASES)
    except (OSError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        print(f"Canonical profile candidate: invalid input: {exc}", file=sys.stderr)
        return 1

    failures: list[str] = []
    base_errors = evaluate(core, evidence)
    if base_errors:
        failures.append(f"base candidate rejected: {sorted(base_errors)}")

    observed_tags: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    for case in cases.get("cases", []):
        name = case.get("name", "<unnamed>")
        mutated_core = copy.deepcopy(core)
        mutated_evidence = copy.deepcopy(evidence)
        core_mutated = False
        try:
            for mutation in case.get("mutations", []):
                target = mutation.get("target")
                if target == "core":
                    apply_mutation(mutated_core, mutation)
                    core_mutated = True
                elif target == "evidence":
                    apply_mutation(mutated_evidence, mutation)
                else:
                    raise ValueError(f"unknown mutation target {target!r}")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            failures.append(f"{name}: invalid mutation: {exc}")
            continue

        result = evaluate(
            mutated_core,
            mutated_evidence,
            skip_core_raw_binding=core_mutated,
        )
        if case.get("kind") == "safe_reference":
            safe_count += 1
            if result:
                failures.append(f"{name}: expected accept, got {sorted(result)}")
        elif case.get("kind") == "adversarial":
            adversarial_count += 1
            tag = case.get("adversarial_tag")
            if not isinstance(tag, str):
                failures.append(f"{name}: missing adversarial_tag")
            else:
                observed_tags.add(tag)
            required = set(case.get("required_errors", []))
            # Exact inventory plus declared intent (ADR 0067).
            intent = set(case.get("intent_errors", []))
            if not intent:
                failures.append(f"{name}: adversarial case declares no intent error")
            elif intent - result:
                failures.append(
                    f"{name}: intent {sorted(intent - result)} did not fire; got {sorted(result)}"
                )
            if not result:
                failures.append(f"{name}: expected rejection, got accept")
            elif required != result:
                failures.append(
                    f"{name}: declared {sorted(required)} but observed {sorted(result)}"
                )
        else:
            failures.append(f"{name}: unknown case kind {case.get('kind')!r}")

    required_tags = set(cases.get("required_adversarial_tags", []))
    if observed_tags != required_tags:
        failures.append(
            "adversarial tag inventory mismatch: "
            f"required {sorted(required_tags)}, observed {sorted(observed_tags)}"
        )

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}", file=sys.stderr)
        print(
            f"Canonical profile candidate: FAIL ({len(failures)} failure(s)); "
            "profile remains unissued",
            file=sys.stderr,
        )
        return 1

    print(
        "Canonical profile candidate: PASS — exact nonrecursive core/evidence "
        f"binding; {safe_count} safe reference and {adversarial_count} known-bad "
        "mutations; profile remains unissued, Gate A blocked, runtime unauthorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
