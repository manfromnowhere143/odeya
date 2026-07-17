#!/usr/bin/env python3
"""Validate the architecture-only Gate A prerequisite closure inventory.

This checker proves cross-file inventory equality and nonrecursive dependency
intent only. A pass is not a frozen canonical profile, immutable registry,
constitutional admission, Gate A acceptance, or runtime authorization.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "architecture/gate-a-prerequisite-closure.json"
FIRST_SLICE = ROOT / "architecture/first-slice-admission-resolution-candidate.json"
CANONICAL_AUDIT = ROOT / "tests/canonicalization/SCHEMA_AUDIT.json"
CANONICAL_PROFILE_CORE = (
    ROOT / "architecture/canonicalization-profile-core-candidate.json"
)
CANONICAL_PROFILE_EVIDENCE = (
    ROOT / "architecture/canonicalization-profile-candidate-evidence.json"
)


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
        raise ValueError(f"{path.relative_to(ROOT)} must contain one JSON object")
    return value


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    try:
        inventory = load(INVENTORY)
        first_slice = load(FIRST_SLICE)
        canonical_audit = load(CANONICAL_AUDIT)
        canonical_profile_core = load(CANONICAL_PROFILE_CORE)
        canonical_profile_evidence = load(CANONICAL_PROFILE_EVIDENCE)
    except (OSError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        print(f"Gate A prerequisite closure: invalid evidence: {exc}", file=sys.stderr)
        return 1

    require(
        inventory.get("status") == "candidate_correction_in_progress_not_admitted",
        "inventory status must remain candidate_correction_in_progress_not_admitted",
        errors,
    )
    require(
        first_slice.get("schema_version") == "0.2.0"
        and first_slice.get("version") == "0.2.0"
        and first_slice.get("status")
        == "bounded_scope_candidate_c5_blocked_not_admitted",
        "first-slice source must be the honest 0.2 C5-blocked candidate",
        errors,
    )
    first_slice_verdict = first_slice.get("scope_verdict")
    require(
        isinstance(first_slice_verdict, dict)
        and first_slice_verdict.get("c1_through_c8_choices_resolved") is False
        and first_slice_verdict.get("may_construct_verification_assignment_member")
        is False,
        "first-slice source must keep C5/PRQ-009 unresolved and nonconstructible",
        errors,
    )
    conflict_rows = first_slice.get("resolved_conflicts")
    c5_rows = [
        row
        for row in conflict_rows
        if isinstance(row, dict) and row.get("conflict_id") == "C5"
    ] if isinstance(conflict_rows, list) else []
    require(
        len(c5_rows) == 1 and c5_rows[0].get("disposition") == "unresolved_blocking",
        "first-slice source must contain one unresolved_blocking C5 row",
        errors,
    )

    scope = inventory.get("exact_scope")
    counts = first_slice.get("counts")
    if not isinstance(scope, dict) or not isinstance(counts, dict):
        errors.append("exact_scope and first-slice counts must be objects")
    else:
        expected_scope = {
            "required_command_types": counts.get("required_commands_exact"),
            "outside_command_types": counts.get("outside_commands_exact"),
            "required_event_types": counts.get("required_event_types_exact"),
            "aggregate_state_reducer_families": counts.get(
                "aggregate_state_reducer_families_exact"
            ),
            "owner_modules": counts.get("owner_modules_exact"),
            "external_constitutional_prerequisites": counts.get(
                "external_constitutional_prerequisites_exact"
            ),
        }
        for key, expected in expected_scope.items():
            require(
                scope.get(key) == expected,
                f"exact_scope.{key} must equal first-slice count {expected!r}",
                errors,
            )
        require(
            scope.get("scope_change_requires_new_adversarial_review") is True,
            "scope changes must require a new adversarial review",
            errors,
        )

    expected_content_order = [
        "schema_resource_closure",
        "aggregate_state_member",
        "reducer_member",
        "event_member",
        "command_member",
        "pure_registry_snapshot",
        "engine_contract_root_core",
        "engine_contract_root_seal",
        "c0_core",
        "c0_seal",
    ]
    require(
        inventory.get("content_identity_order") == expected_content_order,
        "content identity order drifted",
        errors,
    )

    expected_constitutional_order = [
        "sealed_engine_root_and_c0",
        "signed_history_checkpoint",
        "inclusion_and_consistency_evidence",
        "independent_witness_observations",
        "witness_quorum_evaluation",
        "recovery_frontier_core",
        "recovery_frontier_verification",
        "p0_core",
        "p0_admission_seal",
        "handler_equality_evidence",
        "registry_activation_core",
        "registry_activation_seal",
        "later_command_admission",
    ]
    require(
        inventory.get("constitutional_evidence_order")
        == expected_constitutional_order,
        "constitutional evidence order drifted",
        errors,
    )

    integration = inventory.get("prospective_constitutional_profile_integration")
    require(
        isinstance(integration, dict)
        and integration.get("source_candidate_schema_bytes_conform") is False
        and integration.get("replacement_schema_identities_assigned") is False
        and integration.get("complete_transitive_consumer_migration") is False
        and integration.get("candidate_profile_parameters_frozen_for_review")
        is True
        and integration.get("candidate_digest_input_framing_frozen_for_review")
        is True
        and integration.get("candidate_profile_reference_shape_frozen_for_review")
        is True
        and integration.get("canonicalization_profile_frozen") is False
        and integration.get("digest_input_framing_frozen") is False
        and integration.get("replacement_digest_contract_shapes_frozen") is False
        and integration.get("disposition") == "blocking",
        "prospective constitutional profile must remain explicitly unintegrated and blocking",
        errors,
    )

    laws = inventory.get("identity_laws")
    if not isinstance(laws, dict):
        errors.append("identity_laws must be an object")
    else:
        required_false = [
            "member_embeds_parent_registry",
            "member_embeds_membership_proof",
            "member_embeds_checkpoint_or_activation",
            "p0_embeds_parent_activation",
            "evidence_enters_attested_core_preimage",
            "external_attestations_enter_seal_preimage",
            "re_signing_changes_core_identity",
            "currentness_is_content_identity",
            "historical_replay_uses_latest_root",
        ]
        for key in required_false:
            require(laws.get(key) is False, f"identity_laws.{key} must be false", errors)
        require(
            laws.get("activation_binds_exact_p0") is True,
            "activation must bind exact P0",
            errors,
        )
        require(
            laws.get("reverse_member_digest_edges") == "forbidden",
            "reverse member-digest edges must be forbidden",
            errors,
        )

    split = inventory.get("snapshot_history_split")
    if not isinstance(split, dict):
        errors.append("snapshot_history_split must be an object")
    else:
        snapshot = split.get("registry_snapshot")
        history = split.get("transparency_history")
        require(
            isinstance(snapshot, dict)
            and snapshot.get("temporal_append_only_claim") is False,
            "registry snapshot cannot claim temporal append-only ordering",
            errors,
        )
        require(
            isinstance(history, dict)
            and history.get("ordering") == "insertion_order"
            and history.get("sorted_by_member_key") is False,
            "transparency history must remain insertion ordered and unsorted",
            errors,
        )
        for key in (
            "membership_receipts_are_external",
            "history_checkpoints_are_external_to_registry_identity",
            "witness_cosignatures_are_external_to_checkpoint_identity",
        ):
            require(split.get(key) is True, f"{key} must remain true", errors)

    axes = inventory.get("explicit_version_axes")
    profile_axes = canonical_profile_core.get("version_axes")
    profile_axis_ids = [
        item.get("axis_id")
        for item in profile_axes
        if isinstance(item, dict)
    ] if isinstance(profile_axes, list) else []
    require(
        isinstance(axes, list)
        and len(axes) == 8
        and len(set(axes)) == len(axes)
        and profile_axis_ids == axes,
        "eight unique explicit version axes must equal the profile core",
        errors,
    )
    require(
        inventory.get("implicit_version_equality") == "forbidden"
        and inventory.get("implicit_upcast") == "forbidden",
        "implicit version equality and upcast must be forbidden",
        errors,
    )

    profile_candidate = inventory.get("canonical_profile_candidate")
    profile_binding = canonical_profile_evidence.get("profile_core_binding")
    migration_snapshot = canonical_profile_evidence.get("migration_snapshot")
    require(
        isinstance(profile_candidate, dict)
        and isinstance(profile_binding, dict)
        and isinstance(migration_snapshot, dict)
        and profile_candidate.get("profile_id")
        == "urn:odeya:canonicalization:odeya-jcs-0.1"
        == canonical_profile_core.get("profile_id")
        == profile_binding.get("profile_id")
        and profile_candidate.get("profile_version") == "0.1.0"
        == canonical_profile_core.get("profile_version")
        == profile_binding.get("profile_version")
        and profile_candidate.get("profile_core_ref")
        == "architecture/canonicalization-profile-core-candidate.json"
        and profile_candidate.get("profile_evidence_ref")
        == "architecture/canonicalization-profile-candidate-evidence.json"
        and profile_candidate.get("profile_core_schema_id")
        == "urn:odeya:schema:canonicalization-profile-core:0.1.0"
        and profile_candidate.get("parameter_status")
        == "candidate_parameters_frozen_for_review_profile_unissued"
        == canonical_profile_core.get("candidate_status")
        and profile_candidate.get("canonical_identity_issued") is False
        and profile_candidate.get("current_consumer_migration_complete") is False
        and migration_snapshot.get("current_consumer_migration_complete") is False
        and profile_candidate.get("operator_acceptance_ref") is None
        and profile_candidate.get("gate_a_disposition") == "blocked",
        "canonical profile candidate must bind the exact unissued core/evidence boundary",
        errors,
    )

    findings = inventory.get("findings")
    expected_ids = [f"PRQ-{index:03d}" for index in range(1, 13)]
    if not isinstance(findings, list):
        errors.append("findings must be an array")
    else:
        finding_ids = [
            item.get("finding_id") if isinstance(item, dict) else None
            for item in findings
        ]
        require(finding_ids == expected_ids, "findings must be exactly PRQ-001..012", errors)
        for item in findings:
            if isinstance(item, dict):
                require(
                    item.get("status")
                    in {
                        "blocking",
                        "unresolved_blocking",
                        "candidate_correction_in_progress",
                        "candidate_contract_in_progress",
                        "candidate_checker_in_progress",
                    },
                    f"{item.get('finding_id')} has an unrecognized status",
                    errors,
                )
                require(
                    isinstance(item.get("closure"), str) and bool(item["closure"]),
                    f"{item.get('finding_id')} needs a closure condition",
                    errors,
                )
        prq009 = findings[8] if len(findings) > 8 and isinstance(findings[8], dict) else {}
        prq008 = findings[7] if len(findings) > 7 and isinstance(findings[7], dict) else {}
        prq001 = findings[0] if findings and isinstance(findings[0], dict) else {}
        require(
            prq001.get("finding_id") == "PRQ-001"
            and prq001.get("status") == "candidate_correction_in_progress"
            and "nonrecursive core" in prq001.get("closure", "")
            and "remain open" in prq001.get("closure", ""),
            "PRQ-001 must expose the frozen-for-review but unissued profile boundary",
            errors,
        )
        require(
            prq008.get("finding_id") == "PRQ-008"
            and prq008.get("status") == "unresolved_blocking"
            and "urn:odeya:schema:canonical-work-lease:0.1.0" in prq008.get("closure", "")
            and "present_unissued_candidate" in prq008.get("closure", ""),
            "PRQ-008 must expose the present-but-unadmitted canonical WorkLease resource as unresolved_blocking",
            errors,
        )
        require(
            prq009.get("finding_id") == "PRQ-009"
            and prq009.get("status") == "unresolved_blocking"
            and "preserve the claimed reservation" in prq009.get("closure", ""),
            "PRQ-009 must remain unresolved_blocking while C5 is not constructible",
            errors,
        )
        first_slice_unresolved = first_slice.get("unresolved_prerequisites", [])
        require(
            isinstance(first_slice_unresolved, list)
            and len(first_slice_unresolved) == 1
            and first_slice_unresolved[0].get("prerequisite_id") == "PRQ-009"
            and first_slice_unresolved[0].get("status") == "unresolved_blocking",
            "Gate A PRQ-009 status must equal the first-slice blocking boundary",
            errors,
        )

    canonical_expected = {
        "CANON-SCHEMA-TIME-001": ("unprofiled_datetime_paths", 118),
        "CANON-SCHEMA-NUMBER-001": ("number_or_decimal_findings", 62),
        "CANON-SCHEMA-DIGEST-001": ("unscoped_digest_fields", 675),
        "CANON-SCHEMA-DEFS-001": ("divergent_common_definition_names", 56),
        "CANON-SCHEMA-PROFILE-001": ("unpinned_profile_bindings", 11),
        "CANON-FIXTURE-TIME-001": ("nonconformant_fixture_timestamps", 233),
    }
    canonical_start = inventory.get("canonical_profile_blockers_at_start")
    canonical_current = inventory.get("canonical_profile_current_audit")
    audit_findings = canonical_audit.get("blocking_findings")
    if (
        not isinstance(canonical_start, dict)
        or not isinstance(canonical_current, dict)
        or not isinstance(audit_findings, list)
    ):
        errors.append("canonical blocker evidence must be present")
    else:
        actual_by_id = {
            item.get("finding_id"): item.get("count")
            for item in audit_findings
            if isinstance(item, dict)
        }
        for finding_id, (inventory_key, frozen_start_count) in canonical_expected.items():
            require(
                canonical_start.get(inventory_key) == frozen_start_count,
                f"{inventory_key} must retain the tranche-start count {frozen_start_count}",
                errors,
            )
            # A resolved class vanishes from blocking_findings -- the audit
            # emits a finding only while its count is nonzero. Reading absence
            # as a mismatch made this a gate that could not observe success:
            # the accepted D1 disposition drove fixture timestamps to zero and
            # this check refused the truth. Absence is exactly count zero.
            require(
                actual_by_id.get(finding_id, 0) == canonical_current.get(inventory_key),
                f"{finding_id} current inventory count must match SCHEMA_AUDIT.json",
                errors,
            )
        require(
            canonical_start.get("source_checkpoint")
            == "f4429ce5ca71e58ebb5d65776a45ebb6a2a18889"
            and canonical_start.get("audit_raw_sha256")
            == "sha256:14e05ba802b032617c5567541c334d7a2e6f64397638ff6981394baec214688e",
            "canonical tranche-start checkpoint/audit identity drifted",
            errors,
        )
        current_audit_digest = "sha256:" + hashlib.sha256(
            CANONICAL_AUDIT.read_bytes()
        ).hexdigest()
        require(
            canonical_current.get("audit_raw_sha256") == current_audit_digest,
            "canonical current audit raw digest must match SCHEMA_AUDIT.json",
            errors,
        )
        require(
            canonical_start.get("profile_status") == "blocked"
            and canonical_current.get("profile_status") == "blocked"
            and canonical_audit.get("gate_a_disposition") == "blocked",
            "canonical profile must remain blocked in start, current, and audit evidence",
            errors,
        )
        require(
            canonical_current.get("schema_count")
            == canonical_audit.get("schema_count")
            == migration_snapshot.get("schema_count")
            and canonical_current.get("fixture_count")
            == canonical_audit.get("fixture_count")
            == migration_snapshot.get("fixture_count"),
            "canonical current audit corpus counts must equal profile evidence",
            errors,
        )

    construction = inventory.get("construction_inventory_at_start")
    if not isinstance(construction, dict) or not isinstance(counts, dict):
        errors.append("construction inventory must be present")
    else:
        count_map = {
            "closed_command_payload_candidates_not_admitted":
                "closed_required_payload_candidates_not_admitted",
            "missing_command_payload_schemas": "missing_required_payload_contracts",
            "missing_command_contract_records": "missing_command_contract_records",
            "missing_event_contract_records": "missing_event_contract_records",
            "missing_aggregate_state_records": "missing_state_subject_records",
            "missing_reducer_contract_records": "missing_reducer_contract_records",
        }
        for inventory_key, first_slice_key in count_map.items():
            require(
                construction.get(inventory_key) == counts.get(first_slice_key),
                f"construction_inventory_at_start.{inventory_key} must match first slice",
                errors,
            )
        for key in (
            "real_engine_contract_root",
            "real_c0_bundle",
            "real_witnessed_checkpoint",
            "real_recovery_frontier",
            "real_p0",
            "real_handler_equality_report",
            "real_registry_activation",
        ):
            require(construction.get(key) is False, f"{key} must remain false", errors)

    external = first_slice.get("external_prerequisites")
    if not isinstance(external, list) or len(external) != 1 or not isinstance(external[0], dict):
        errors.append("first slice must contain one exact external prerequisite")
    else:
        bindings = external[0].get("required_bindings")
        require(isinstance(bindings, list), "P0 required_bindings must be an array", errors)
        if isinstance(bindings, list):
            require(
                "registry_activation_identity_sequence_and_digest" not in bindings,
                "P0 required bindings cannot bind the parent activation",
                errors,
            )
            require(
                "activation_independent_subject_excluding_activation_identity_sequence_reference_and_digest"
                in bindings,
                "P0 must explicitly exclude activation identity, sequence, reference, and digest",
                errors,
            )
        require(
            external[0].get("current_instance_status") == "missing",
            "no real P0 instance may be claimed",
            errors,
        )

    for decision_ref in inventory.get("decision_refs", []):
        require(
            isinstance(decision_ref, str) and (ROOT / decision_ref).is_file(),
            f"missing decision record {decision_ref!r}",
            errors,
        )
    require(
        (ROOT / str(inventory.get("plan_ref", ""))).is_file(),
        "prerequisite closure plan is missing",
        errors,
    )

    standards_refs = inventory.get("standards_comparison_refs")
    require(
        isinstance(standards_refs, list)
        and len(standards_refs) >= 10
        and len(standards_refs) == len(set(standards_refs))
        and all(isinstance(ref, str) and ref.startswith("https://") for ref in standards_refs),
        "standards comparison refs must be unique HTTPS primary references",
        errors,
    )

    refusal = inventory.get("refusal")
    if not isinstance(refusal, dict):
        errors.append("refusal must be an object")
    else:
        for key, value in refusal.items():
            require(value is False, f"refusal.{key} must be false", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Gate A prerequisite closure: FAIL ({len(errors)} error(s)); "
            "candidate remains blocked",
            file=sys.stderr,
        )
        return 1

    print(
        "Gate A prerequisite closure: PASS; "
        "12 findings tracked; exact scope 43 commands / 60 events / "
        "25 families / 11 owners; candidate remains blocked and inactive"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
