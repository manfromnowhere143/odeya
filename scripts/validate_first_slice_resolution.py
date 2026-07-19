#!/usr/bin/env python3
"""Validate the exact architecture-only first-slice resolution candidate.

This checks representational closure and cross-file equality only. A pass is not
an immutable registry, RegistryActivation, Gate A acceptance, or runtime proof.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "architecture/first-slice-admission-resolution-candidate.json"
VOCABULARY = ROOT / "architecture/command-design-vocabulary.json"
EVENT_SCHEMA = ROOT / "schemas/research-event.schema.json"
MODULE_MANIFEST = ROOT / "architecture/module-dependency-manifest.json"
HISTORICAL_COMMAND_ENVELOPE_BLOB = "6e500377e176f686918390cfea63e165df0c6fcf"
HISTORICAL_COMMAND_ENVELOPE_ID = "urn:odeya:schema:command-envelope:0.4.0"


class DuplicateKey(ValueError):
    """Raised when JSON would otherwise silently overwrite a member."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root is not an object: {path.relative_to(ROOT)}")
    return value


def load_git_blob(blob_id: str) -> tuple[dict[str, Any], bytes]:
    completed = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    raw = completed.stdout
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"Git blob {blob_id} JSON root is not an object")
    return value, raw


def string_list(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{label} must be an array of strings")
        return []
    return value


def exact_sorted_unique(values: list[str], label: str, errors: list[str]) -> None:
    if values != sorted(values):
        errors.append(f"{label} must use canonical lexical order")
    if len(values) != len(set(values)):
        errors.append(f"{label} contains duplicates")


def collect_property_constants(node: Any, property_name: str) -> list[str]:
    found: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            properties = value.get("properties")
            if isinstance(properties, dict):
                candidate = properties.get(property_name)
                if isinstance(candidate, dict) and isinstance(candidate.get("const"), str):
                    found.add(candidate["const"])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(node)
    return sorted(found)


def expected_count(
    counts: dict[str, Any], key: str, actual: int, errors: list[str]
) -> None:
    if counts.get(key) != actual:
        errors.append(f"counts.{key}={counts.get(key)!r}, expected {actual}")


def restricted_jcs_bytes(value: Any) -> bytes:
    """JCS bytes for this ASCII/integer-only planning artifact.

    The vocabulary is deliberately restricted away from binary numbers and
    non-ASCII strings here. Under that checked subset, sorted compact JSON is
    byte-identical to RFC 8785 and avoids adding a second runtime dependency to
    the architecture validator.
    """

    def check(node: Any) -> None:
        if isinstance(node, float):
            raise ValueError("binary JSON number is outside restricted JCS subset")
        if isinstance(node, str) and not node.isascii():
            raise ValueError("non-ASCII string is outside restricted JCS subset")
        if isinstance(node, dict):
            for key, child in node.items():
                if not isinstance(key, str) or not key.isascii():
                    raise ValueError("non-ASCII/non-string object key is outside restricted JCS subset")
                check(child)
        elif isinstance(node, list):
            for child in node:
                check(child)

    check(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def main() -> int:
    errors: list[str] = []
    try:
        inventory = load(INVENTORY)
        vocabulary = load(VOCABULARY)
        event_schema = load(EVENT_SCHEMA)
        module_manifest = load(MODULE_MANIFEST)
        historical_command_schema, historical_command_schema_bytes = load_git_blob(
            HISTORICAL_COMMAND_ENVELOPE_BLOB
        )
    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        DuplicateKey,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"Odeya first-slice resolution validation FAILED\n- {exc}")
        return 1

    counts = inventory.get("counts")
    if not isinstance(counts, dict):
        errors.append("counts must be an object")
        counts = {}

    required = string_list(inventory.get("required_commands"), "required_commands", errors)
    outside = string_list(inventory.get("outside_commands"), "outside_commands", errors)
    events = string_list(inventory.get("required_event_types"), "required_event_types", errors)
    owners = string_list(inventory.get("owner_modules"), "owner_modules", errors)
    for values, label in (
        (required, "required_commands"),
        (outside, "outside_commands"),
        (events, "required_event_types"),
        (owners, "owner_modules"),
    ):
        exact_sorted_unique(values, label, errors)

    vocabulary_entries = vocabulary.get("entries")
    if not isinstance(vocabulary_entries, list):
        errors.append("command design vocabulary entries must be an array")
        vocabulary_commands: list[str] = []
    else:
        vocabulary_commands = [
            entry.get("command_type")
            for entry in vocabulary_entries
            if isinstance(entry, dict) and isinstance(entry.get("command_type"), str)
        ]
    if len(vocabulary_commands) != len(vocabulary_entries or []):
        errors.append("every command design vocabulary entry must name command_type")
    if set(required) & set(outside):
        errors.append("required_commands and outside_commands overlap")
    if set(required) | set(outside) != set(vocabulary_commands):
        missing = sorted(set(vocabulary_commands) - (set(required) | set(outside)))
        extra = sorted((set(required) | set(outside)) - set(vocabulary_commands))
        errors.append(f"command partition differs from design vocabulary: missing={missing}, extra={extra}")

    historical_command_enum = collect_property_constants(historical_command_schema, "command_type")
    if historical_command_enum != sorted(vocabulary_commands):
        errors.append("historical Envelope 0.4 extraction and command vocabulary are unequal")

    source_ref = vocabulary.get("source_envelope_candidate_ref")
    if not isinstance(source_ref, dict):
        errors.append("command vocabulary source_envelope_candidate_ref must be an object")
    else:
        expected_source_digest = "sha256:" + hashlib.sha256(historical_command_schema_bytes).hexdigest()
        if historical_command_schema.get("$id") != HISTORICAL_COMMAND_ENVELOPE_ID:
            errors.append("retained historical CommandEnvelope blob has the wrong schema ID")
        if source_ref.get("schema_id") != HISTORICAL_COMMAND_ENVELOPE_ID:
            errors.append("command vocabulary source schema ID differs from retained historical Envelope 0.4")
        if source_ref.get("semantic_version") != "0.4.0":
            errors.append("command vocabulary source semantic version is not historical 0.4.0")
        if source_ref.get("byte_digest") != expected_source_digest:
            errors.append("command vocabulary source byte digest is stale")
        if source_ref.get("byte_count") != len(historical_command_schema_bytes):
            errors.append("command vocabulary source byte count is stale")

    digest_contract = vocabulary.get("vocabulary_digest_contract")
    if not isinstance(digest_contract, dict):
        errors.append("command vocabulary digest contract must be an object")
    else:
        pointers = digest_contract.get("included_json_pointers")
        if not isinstance(pointers, list) or not all(
            isinstance(pointer, str) and pointer.startswith("/") and pointer.count("/") == 1
            for pointer in pointers
        ):
            errors.append("command vocabulary digest pointers must be top-level JSON Pointers")
        else:
            missing_pointer_fields = [pointer for pointer in pointers if pointer[1:] not in vocabulary]
            if missing_pointer_fields:
                errors.append(f"command vocabulary digest pointers are missing: {missing_pointer_fields}")
            else:
                projection = {pointer[1:]: vocabulary[pointer[1:]] for pointer in pointers}
                digest_subject = {
                    "digest_contract": digest_contract,
                    "resolved_subject_schema": digest_contract.get("subject_schema_ref"),
                    "projection": projection,
                }
                try:
                    computed_vocabulary_digest = (
                        "sha256:" + hashlib.sha256(restricted_jcs_bytes(digest_subject)).hexdigest()
                    )
                except ValueError as exc:
                    errors.append(f"command vocabulary scoped digest cannot be recomputed: {exc}")
                else:
                    if vocabulary.get("vocabulary_digest") != computed_vocabulary_digest:
                        errors.append("command vocabulary scoped digest is stale")

    event_enum = event_schema.get("properties", {}).get("event_type", {}).get("enum", [])
    if not isinstance(event_enum, list) or not all(isinstance(item, str) for item in event_enum):
        errors.append("ResearchEvent event_type enum is unavailable")
        event_enum = []
    event_missing = sorted(set(events) - set(event_enum))
    if event_missing:
        errors.append(f"required event types missing from ResearchEvent: {event_missing}")
    if "resource.observed" in event_enum:
        errors.append("ResearchEvent must remove the generic resource.observed discriminator")
    if "resource.observed" in events:
        errors.append("resource.observed may not enter the resolved resource truth set")
    if "work.lease_expired" not in events:
        errors.append("resolved local execution set must contain work.lease_expired")

    aggregates = inventory.get("aggregate_dependencies")
    if not isinstance(aggregates, list):
        errors.append("aggregate_dependencies must be an array")
        aggregates = []
    aggregate_types: list[str] = []
    aggregate_owner_modules: list[str] = []
    reducer_families: dict[str, str] = {}
    for index, record in enumerate(aggregates):
        if not isinstance(record, dict):
            errors.append(f"aggregate_dependencies[{index}] must be an object")
            continue
        aggregate_type = record.get("aggregate_type")
        owner_module = record.get("owner_module")
        reducer_family = record.get("reducer_family")
        if not all(isinstance(item, str) and item for item in (aggregate_type, owner_module, reducer_family)):
            errors.append(f"aggregate_dependencies[{index}] has an incomplete identity")
            continue
        if aggregate_type in reducer_families:
            errors.append(f"aggregate {aggregate_type} has more than one reducer row")
        reducer_families[aggregate_type] = reducer_family
        aggregate_types.append(aggregate_type)
        aggregate_owner_modules.append(owner_module)
    exact_sorted_unique(aggregate_types, "aggregate dependency identities", errors)
    if set(aggregate_owner_modules) != set(owners):
        errors.append("owner_modules differs from aggregate dependency owners")
    if reducer_families.get("verification") != "Verification":
        errors.append("verification must have exactly the Verification reducer family")
    if reducer_families.get("dependency") != "DependencyInvalidationFrontier":
        errors.append("dependency must use the DependencyInvalidationFrontier reducer family")

    manifest_owners: dict[str, str] = {}
    for record in module_manifest.get("aggregate_owners", []):
        if isinstance(record, dict):
            aggregate_type = record.get("aggregate_type")
            owner_module = record.get("owner_module")
            if isinstance(aggregate_type, str) and isinstance(owner_module, str):
                manifest_owners[aggregate_type] = owner_module
    for aggregate_type, owner_module in zip(aggregate_types, aggregate_owner_modules):
        if manifest_owners.get(aggregate_type) != owner_module:
            errors.append(
                f"aggregate owner mismatch for {aggregate_type}: "
                f"resolution={owner_module}, manifest={manifest_owners.get(aggregate_type)!r}"
            )

    authority = inventory.get("authority_model")
    if not isinstance(authority, dict):
        errors.append("authority_model must be an object")
        authority = {}
    modes = string_list(authority.get("modes"), "authority_model.modes", errors)
    if modes != [
        "ingress_policy",
        "constitutional_bootstrap",
        "assignment_only",
        "bounded_grants",
    ]:
        errors.append("authority modes differ from the closed constitutional order")
    role_order = string_list(
        authority.get("role_slot_order"), "authority_model.role_slot_order", errors
    )
    if len(role_order) != len(set(role_order)):
        errors.append("authority role-slot order contains duplicates")
    role_index = {role: index for index, role in enumerate(role_order)}
    profiles = authority.get("command_profiles")
    if not isinstance(profiles, list):
        errors.append("authority command_profiles must be an array")
        profiles = []
    profile_commands: list[str] = []
    for profile_index, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(f"authority command_profiles[{profile_index}] must be an object")
            continue
        command_type = profile.get("command_type")
        paths = profile.get("paths")
        if not isinstance(command_type, str) or not command_type:
            errors.append(f"authority command_profiles[{profile_index}] lacks command_type")
            continue
        profile_commands.append(command_type)
        if not isinstance(paths, list) or not paths:
            errors.append(f"authority profile {command_type} has no paths")
            continue
        path_ids: set[str] = set()
        for path_index, path in enumerate(paths):
            if not isinstance(path, dict):
                errors.append(f"authority profile {command_type} path {path_index} is not an object")
                continue
            path_id = path.get("path_id")
            mode = path.get("mode")
            slots = string_list(
                path.get("role_slots"),
                f"authority profile {command_type}/{path_id} role_slots",
                errors,
            )
            if not isinstance(path_id, str) or not path_id:
                errors.append(f"authority profile {command_type} has a path without path_id")
            elif path_id in path_ids:
                errors.append(f"authority profile {command_type} repeats path_id {path_id}")
            else:
                path_ids.add(path_id)
            if mode not in modes:
                errors.append(f"authority profile {command_type}/{path_id} has unknown mode {mode!r}")
            if len(slots) != len(set(slots)):
                errors.append(f"authority profile {command_type}/{path_id} repeats a role slot")
            unknown_roles = sorted(set(slots) - set(role_order))
            if unknown_roles:
                errors.append(f"authority profile {command_type}/{path_id} has unknown roles {unknown_roles}")
            slot_indexes = [role_index[slot] for slot in slots if slot in role_index]
            if slot_indexes != sorted(slot_indexes):
                errors.append(f"authority profile {command_type}/{path_id} violates role-slot order")
            if mode == "bounded_grants" and not slots:
                errors.append(f"bounded authority profile {command_type}/{path_id} has no grant slots")
            if mode != "bounded_grants" and slots:
                errors.append(f"non-grant authority profile {command_type}/{path_id} has grant slots")
            if mode == "assignment_only" and not isinstance(path.get("assignment_role"), str):
                errors.append(f"assignment-only profile {command_type}/{path_id} lacks assignment_role")
    exact_sorted_unique(profile_commands, "authority command profile identities", errors)
    if profile_commands != required:
        errors.append("authority command profiles must equal required_commands in canonical order")

    grant_law = authority.get("bounded_grant_law")
    if not isinstance(grant_law, dict):
        errors.append("bounded_grant_law must be an object")
    else:
        required_grant_law = {
            "distinct_grant_per_slot": True,
            "action_instance_bound": True,
            "single_use": True,
            "max_uses": 1,
            "consumption_point": "domain_commit",
            "used_set_equals_exhausted_set": True,
            "rejection_noop_or_replay_emits_new_use": False,
            "caller_may_select_authority_path": False,
        }
        for key, expected in required_grant_law.items():
            if grant_law.get(key) != expected:
                errors.append(f"bounded_grant_law.{key} must equal {expected!r}")

    conflicts = inventory.get("resolved_conflicts")
    if not isinstance(conflicts, list):
        errors.append("resolved_conflicts must be an array")
        conflicts = []
    conflict_ids = [record.get("conflict_id") for record in conflicts if isinstance(record, dict)]
    if conflict_ids != [f"C{index}" for index in range(1, 9)]:
        errors.append("resolved_conflicts must contain ordered C1 through C8")
    else:
        for record in conflicts:
            conflict_id = record.get("conflict_id")
            expected_disposition = "unresolved_blocking" if conflict_id == "C5" else "resolved"
            if record.get("disposition") != expected_disposition:
                errors.append(
                    f"{conflict_id} disposition must be {expected_disposition!r}, "
                    f"got {record.get('disposition')!r}"
                )

    unresolved = inventory.get("unresolved_prerequisites")
    if not isinstance(unresolved, list) or len(unresolved) != 1:
        errors.append("exactly one unresolved prerequisite is required")
    else:
        prq = unresolved[0]
        expected_roles = ["safety", "data_rights", "resource", "execution", "verification"]
        expected_assignment_events = [
            *(f"authority.grant_used({role})" for role in expected_roles),
            "resource.reservation_created",
            "work.lease_acquired",
            "verification.assigned",
            *(f"authority.grant_exhausted({role})" for role in expected_roles),
        ]
        if prq.get("prerequisite_id") != "PRQ-009" or prq.get("status") != "unresolved_blocking":
            errors.append("the sole unresolved prerequisite must be blocking PRQ-009")
        contract = prq.get("prospective_assignment_contract", {})
        if contract.get("role_slot_order") != expected_roles:
            errors.append("PRQ-009 assignment role-slot order is not exact")
        if contract.get("batch_size_exact") != len(expected_assignment_events):
            errors.append("PRQ-009 assignment batch size is not exactly 13")
        if contract.get("event_order_exact") != expected_assignment_events:
            errors.append("PRQ-009 assignment event order is not exact")
        if inventory.get("atomic_cohorts", {}).get("verification_assign_local") != expected_assignment_events:
            errors.append("verification_assign_local cohort differs from PRQ-009")
        expected_c5_status = {
            "current_blockers": [
                "the retained WorkIntent candidate is unresolved_blocking with null canonicalization profile and null canonical digest and is not admitted or assignable",
                "ResearchEvent 0.18.0 intentionally contains no fabricated resolved WorkIntent binding and remains not admitted, not dispatchable, and not replay-authoritative",
                "the verification.assigned architecture fixture is a one-event sample batch and does not prove the exact 13-event cohort",
                "the verification.assigned payload does not yet bind the exact WorkIntent WorkContract lease current data-use decisions sandbox policy and five-grant cohort",
            ],
            "corrected_compatibility_findings": [
                {
                    "finding_id": "C5-WORK-LEASE-RELEASE-CLAIM-001",
                    "status": "corrected",
                    "successor_schema_resource_id": "urn:odeya:schema:research-event:0.18.0",
                    "correction": "work.lease_released retains reservation_claim_state=claimed and the exact resource.reservation_claimed reference while terminating only WorkLease; a later resource.reservation_settled event alone performs claimed-to-settled under ResourceLedger ownership",
                    "retained_evidence_ref": "architecture/first-slice-event-identity-map.json#/required_schema_resource_candidates/0/transitive_consumer_review/resolved_compatibility_findings/0",
                    "bounded_evidence": "retained synthetic fixture dereference and exact reference, cohort, adjacent-digest-value, non-fungible dimension, and settlement-equation checks without digest recomputation or reducer replay",
                    "authority_effect": "none; C5 and PRQ-009 remain unresolved_blocking",
                }
            ],
        }
        observed_c5_status = {
            "current_blockers": prq.get("current_blockers"),
            "corrected_compatibility_findings": prq.get(
                "corrected_compatibility_findings"
            ),
        }
        if observed_c5_status != expected_c5_status:
            errors.append(
                "PRQ-009 does not retain the exact corrected C5 release-claim boundary"
            )

    prerequisites = inventory.get("external_prerequisites")
    if not isinstance(prerequisites, list) or len(prerequisites) != 1:
        errors.append("exactly one external constitutional prerequisite is required")
    elif prerequisites[0].get("prerequisite_id") != "P0.constitutional-recovery-admission":
        errors.append("the sole external prerequisite must be P0.constitutional-recovery-admission")

    expected_count(counts, "design_commands_exact", len(vocabulary_commands), errors)
    expected_count(counts, "required_commands_exact", len(required), errors)
    expected_count(counts, "outside_commands_exact", len(outside), errors)
    expected_count(counts, "required_event_types_exact", len(events), errors)
    expected_count(counts, "aggregate_state_reducer_families_exact", len(aggregates), errors)
    expected_count(counts, "owner_modules_exact", len(owners), errors)
    expected_count(counts, "external_constitutional_prerequisites_exact", len(prerequisites or []), errors)
    expected_count(counts, "unresolved_c1_through_c8_choices", 1, errors)
    expected_count(counts, "global_command_design_vocabulary_after_delta", len(vocabulary_commands), errors)
    expected_count(counts, "global_event_design_vocabulary_after_delta", len(event_enum), errors)

    if inventory.get("schema_version") != "0.2.0" or inventory.get("version") != "0.2.0":
        errors.append("materially changed inventory must be reissued as exact version 0.2.0")
    if inventory.get("status") != "bounded_scope_candidate_c5_blocked_not_admitted":
        errors.append("inventory status must expose the blocking C5 boundary")
    if inventory.get("source_checkpoint") != "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889":
        errors.append("inventory source checkpoint differs from the 0.2 tranche origin")
    predecessor = inventory.get("supersedes_candidate", {})
    expected_predecessor = {
        "inventory_id": "odeya.first-slice-admission-resolution-candidate",
        "version": "0.1.0",
        "source_commit": "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889",
        "git_blob": "a7983e273d043966c93786f0edeb42bdf173d84a",
        "raw_sha256": "sha256:83a16f9f6b2eff834f0bc7869fb6188e4ee04af7201a1338341a4ea2a1f508dc",
        "canonical_digest": None,
        "canonical_digest_status": "not_computed_no_frozen_artifact_profile",
    }
    if predecessor != expected_predecessor:
        errors.append("inventory 0.1 predecessor lineage is not exact")
    expected_vocabulary_retention = {
        "mode": "historical_git_blob_architecture_only",
        "status": "retained_not_registry_admitted_blocking",
        "source_commit": "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889",
        "source_path": "schemas/command-envelope.schema.json",
        "source_schema_id": HISTORICAL_COMMAND_ENVELOPE_ID,
        "source_git_blob": HISTORICAL_COMMAND_ENVELOPE_BLOB,
        "source_raw_sha256": "sha256:ad8b96a589051624dfc59d4a429a6529e3b91f7e18a9005cc615b9fa73dbbc30",
        "source_byte_count": 103272,
        "current_command_envelope_candidate_is_not_a_replacement_source": True,
    }
    if inventory.get("command_vocabulary_source_retention") != expected_vocabulary_retention:
        errors.append("historical command-vocabulary source retention boundary is not exact")
    sources = string_list(inventory.get("sources"), "sources", errors)
    if len(sources) != len(set(sources)):
        errors.append("sources contains duplicates")
    for source in sources:
        source_path = Path(source)
        if source_path.is_absolute() or ".." in source_path.parts:
            errors.append(f"sources contains non-repository path {source!r}")
        elif not (ROOT / source_path).is_file():
            errors.append(f"sources references missing file {source!r}")
    for required_source in (
        "formal/tla/CompositeAuthorityResource.tla",
        "formal/tla/results-manifest.json",
        "tests/first-slice-resolution/cases.json",
    ):
        if required_source not in sources:
            errors.append(f"sources must bind retained evidence {required_source}")
    scope = inventory.get("scope_verdict")
    if not isinstance(scope, dict):
        errors.append("scope_verdict must be an object")
    else:
        for key in (
            "c1_through_c8_choices_resolved",
            "immutable_registry_members_exist",
            "engine_contract_root_exists",
            "constitutional_prerequisite_instance_exists",
            "registry_activation_exists",
            "may_freeze_registry_snapshot",
            "may_activate",
            "may_start_runtime_implementation",
        ):
            if scope.get(key) is not False:
                errors.append(f"scope_verdict.{key} must remain false")
        if scope.get("may_construct_verification_assignment_member") is not False:
            errors.append("scope_verdict.may_construct_verification_assignment_member must remain false")

    if errors:
        print("Odeya first-slice resolution validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Odeya first-slice resolution validation PASSED")
    print(f"- {len(required)} required / {len(outside)} outside commands")
    print(f"- {len(events)} required event discriminators")
    print(f"- {len(aggregates)} aggregate/reducer families / {len(owners)} owner modules")
    print("- C1-C4/C6-C8 bounded; C5/PRQ-009, immutable records, P0 instance, complete replay/refinement proof, and review remain blocked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
