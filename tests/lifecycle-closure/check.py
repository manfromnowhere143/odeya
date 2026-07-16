#!/usr/bin/env python3
"""Check architecture-only prerequisite lifecycle closure.

This checker proves finite candidate consistency only. It does not construct
registry members, activate contracts, authorize a runtime, or complete Gate A.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests/lifecycle-closure/cases.json"
SCHEMA_PATH = ROOT / "schemas/research-event.schema.json"
INVENTORY_PATH = ROOT / "architecture/first-slice-admission-resolution-candidate.json"
IDENTITY_MAP_PATH = ROOT / "architecture/first-slice-event-identity-map.json"
DATA_USE_FIXTURE_PATH = ROOT / "tests/architecture-schema/fixtures/data-use-decided-event.valid.json"
WORK_LEASE_SCHEMA_PATH = ROOT / "schemas/canonical-work-lease.schema.json"
MODULE_MANIFEST_PATH = ROOT / "architecture/module-dependency-manifest.json"
WORK_LEASE_FIXTURES = {
    "acquired": ROOT / "tests/architecture-schema/fixtures/canonical-work-lease-acquired.valid.json",
    "released": ROOT / "tests/architecture-schema/fixtures/canonical-work-lease-released.valid.json",
}
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
PAYLOAD_TYPE_VERSION = re.compile(r":(\d+\.\d+\.\d+)$")
EXPECTED_V2_PAYLOAD_TYPE_EVENTS = {
    "reproducibility.determined",
    "verification.assigned",
    "verification.completed",
    "verification.disputed",
}
CANONICAL_WORK_LEASE_ID = "urn:odeya:schema:canonical-work-lease:0.1.0"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_json_digest(value: Any) -> str:
    """Identify retained cases; this is not Odeya canonicalization evidence."""

    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def branch_map(schema: dict[str, Any]) -> tuple[dict[str, tuple[int, dict[str, Any]]], list[str]]:
    result: dict[str, tuple[int, dict[str, Any]]] = {}
    errors: list[str] = []
    for index, branch in enumerate(schema.get("oneOf", [])):
        event_type = branch.get("properties", {}).get("event_type", {}).get("const")
        if not isinstance(event_type, str):
            errors.append(f"ResearchEvent branch {index} lacks an exact event_type const")
            continue
        if event_type in result:
            errors.append(f"ResearchEvent event_type {event_type!r} has multiple branches")
            continue
        result[event_type] = (index, branch)
    return result, errors


def exact_value(fragment: dict[str, Any], key: str) -> Any:
    value = fragment.get(key, {})
    if "const" in value:
        return value["const"]
    if "enum" in value:
        return set(value["enum"])
    return None


def transition_spec(branch: dict[str, Any]) -> dict[str, Any]:
    payload = branch.get("properties", {}).get("payload", {})
    layers = payload.get("allOf", [])
    result: dict[str, Any] = {}
    for layer in layers:
        properties = layer.get("properties", {})
        for field in ("action", "from", "to"):
            candidate = exact_value(properties, field)
            if candidate is not None:
                result[field] = candidate
    return result


def nested(value: dict[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def schema_contract_errors(
    schema: dict[str, Any], inventory: dict[str, Any], identity: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    branches, branch_errors = branch_map(schema)
    errors.extend(branch_errors)
    if len(branches) != 135:
        errors.append(f"ResearchEvent global branch count changed from 135 to {len(branches)}")
    if schema.get("$id") != "urn:odeya:schema:research-event:0.7.0":
        errors.append("lifecycle closure is not carried by exact ResearchEvent 0.7.0")
    if nested(schema, "properties", "schema_version", "const") != "0.7.0":
        errors.append("ResearchEvent instance version is not exactly 0.7.0")
    required_envelope_fields = {
        "payload_type_id",
        "payload_contract_resolution_status",
        "payload_contract_digest",
        "event_contract_authority_status",
    }
    if not required_envelope_fields <= set(schema.get("required", [])):
        errors.append("ResearchEvent does not require the complete logical-type/unresolved-contract boundary")
    if nested(schema, "properties", "payload_contract_resolution_status", "const") != "unresolved_blocking":
        errors.append("ResearchEvent 0.7.0 does not fail closed on unresolved branch contracts")
    if nested(schema, "properties", "payload_contract_digest", "type") != "null":
        errors.append("ResearchEvent 0.7.0 permits a fabricated per-branch contract digest")
    if nested(schema, "properties", "event_contract_authority_status", "const") != "not_admitted_not_dispatchable_not_replay_authoritative":
        errors.append("unresolved ResearchEvent candidates can claim event authority")
    expected_binding_source = (
        "event.payload_type_id+event.payload_contract_resolution_status+"
        "event.payload_contract_digest"
    )
    if nested(schema, "$defs", "payload_digest_contract", "properties", "payload_contract_binding_source", "const") != expected_binding_source:
        errors.append("payload digest contract does not bind logical type plus unresolved contract state")
    for event_type, (_, branch) in branches.items():
        logical_type = nested(branch, "properties", "payload_type_id", "const")
        if not isinstance(logical_type, str) or not logical_type.startswith("urn:odeya:event-payload:"):
            errors.append(f"ResearchEvent branch {event_type} lacks an exact logical payload type ID")
        if logical_type == schema.get("$id"):
            errors.append(f"ResearchEvent branch {event_type} substitutes the schema resource ID for its logical payload type")

    counts = inventory.get("counts", {})
    required_events = inventory.get("required_event_types", [])
    if counts.get("required_event_types_exact") != 60 or len(required_events) != 60:
        errors.append("first-slice required event count is not preserved at exactly 60")
    if counts.get("aggregate_state_reducer_families_exact") != 25 or len(inventory.get("aggregate_dependencies", [])) != 25:
        errors.append("first-slice aggregate/reducer-family count is not preserved at exactly 25")

    mappings = identity.get("mappings", [])
    if len(mappings) != 60:
        errors.append("event identity map does not contain exactly 60 rows")
    mapped_types = [row.get("event_type") for row in mappings if isinstance(row, dict)]
    if len(mapped_types) != len(set(mapped_types)):
        errors.append("event identity map contains duplicate event types")
    if set(mapped_types) != set(required_events):
        errors.append("event identity map is not exactly the 60-event first-slice set")

    source = identity.get("source", {})
    raw = SCHEMA_PATH.read_bytes()
    raw_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if source.get("schema_resource_raw_sha256") != raw_digest:
        errors.append("identity map ResearchEvent raw-byte digest is stale")
    if source.get("schema_resource_byte_count") != len(raw):
        errors.append("identity map ResearchEvent byte count is stale")
    if source.get("schema_resource_id") != schema.get("$id"):
        errors.append("identity map ResearchEvent schema identity is stale")
    if source.get("schema_resource_version") != nested(schema, "properties", "schema_version", "const"):
        errors.append("identity map ResearchEvent instance version is stale")
    if source.get("required_event_inventory_id") != inventory.get("inventory_id"):
        errors.append("identity map points at the wrong first-slice inventory")
    if source.get("required_event_inventory_version") != inventory.get("version"):
        errors.append("identity map points at the wrong first-slice inventory version")

    if identity.get("version") != "0.2.0":
        errors.append("event identity map did not advance to the WorkLease-aware 0.2.0 candidate")
    if identity.get("missing_required_schema_resources") != []:
        errors.append("identity map still claims a required schema resource is absent")

    work_lease_raw = WORK_LEASE_SCHEMA_PATH.read_bytes()
    work_lease_schema = load_json(WORK_LEASE_SCHEMA_PATH)
    expected_work_lease_candidate = {
        "schema_resource_id": CANONICAL_WORK_LEASE_ID,
        "schema_path": "schemas/canonical-work-lease.schema.json",
        "resource_presence_status": "present_unissued_candidate",
        "schema_resource_raw_sha256": "sha256:" + hashlib.sha256(work_lease_raw).hexdigest(),
        "schema_resource_byte_count": len(work_lease_raw),
        "owner_module": "work",
        "contract_kind": "candidate_record",
        "scope_profile": "first_slice_local_verification_candidate",
        "record_identity_resolution_status": "unresolved_blocking",
        "record_authority_status": "not_admitted_not_execution_authority",
        "referenced_from": "schemas/research-event.schema.json#/$defs/canonical_work_lease_record_reference",
        "affected_first_slice_area": "local work-lease attempt and assignment payload references",
        "safe_trace_resolution_claimed": False,
        "transitive_consumer_review": {
            "schema_consumer_pointers": [
                "schemas/research-event.schema.json#/$defs/canonical_work_lease_record_reference"
            ],
            "fixture_consumers": [
                "tests/architecture-schema/fixtures/local-attempt-completed-event.valid.json",
                "tests/architecture-schema/fixtures/local-attempt-started-event.valid.json",
            ],
            "candidate_fixtures": [
                "tests/architecture-schema/fixtures/canonical-work-lease-acquired.valid.json",
                "tests/architecture-schema/fixtures/canonical-work-lease-released.valid.json",
            ],
            "compatibility_findings": [
                {
                    "finding_id": "C5-WORK-LEASE-RELEASE-CLAIM-001",
                    "status": "unresolved_blocking",
                    "consumer": "schemas/research-event.schema.json#/oneOf/21/properties/payload",
                    "current_consumer_contract": "work.lease_released requires reservation_claim_state=unclaimed and a null reservation_claim_event_ref",
                    "required_first_slice_contract": "after attempt.start claims the reservation, lease release retains claimed plus the exact claim event and does not mutate ResourceLedger; settlement remains separate",
                    "required_action": "reissue ResearchEvent and its EventContractRecord under PRQ-009 with exact release/claim/settlement vectors",
                }
            ],
        },
        "remaining_disposition": "schema resource absence is removed; canonical profile, record identity, assignment cohort, immutable registry membership, reducer evidence, and activation remain blocking",
    }
    if identity.get("required_schema_resource_candidates") != [expected_work_lease_candidate]:
        errors.append("identity map does not bind the exact present-but-unissued WorkLease candidate")
    if work_lease_schema.get("$id") != CANONICAL_WORK_LEASE_ID:
        errors.append("canonical WorkLease candidate has the wrong schema resource identity")
    if nested(work_lease_schema, "properties", "schema_version", "const") != "0.1.0":
        errors.append("canonical WorkLease candidate instance version is not 0.1.0")
    if nested(work_lease_schema, "properties", "scope_profile", "const") != "first_slice_local_verification_candidate":
        errors.append("canonical WorkLease candidate is not bounded to the first-slice local profile")
    if nested(work_lease_schema, "properties", "identity_resolution_status", "const") != "unresolved_blocking":
        errors.append("canonical WorkLease candidate does not fail closed on identity")
    if nested(work_lease_schema, "properties", "canonicalization_profile_ref", "type") != "null":
        errors.append("canonical WorkLease candidate fabricates a canonicalization profile")
    if nested(work_lease_schema, "properties", "canonical_digest", "type") != "null":
        errors.append("canonical WorkLease candidate fabricates a canonical digest")
    if nested(work_lease_schema, "properties", "record_authority_status", "const") != "not_admitted_not_execution_authority":
        errors.append("canonical WorkLease candidate can claim execution authority")
    expected_digest_scopes = {
        "canonical_digest": {
            "algorithm": "sha-256",
            "subject": "canonical WorkLease record under its future admitted schema and canonicalization profile",
            "profile_source": "/canonicalization_profile_ref",
            "schema_source": CANONICAL_WORK_LEASE_ID,
            "status": "not_computable_while_identity_resolution_status_is_unresolved_blocking",
        },
        "work_lease_record_digest": {
            "algorithm": "sha-256",
            "subject": "exact referenced canonical record bytes",
            "profile_source": "referenced record registry member",
            "schema_source": "schema_id sibling",
            "status": "requires_offline_registry_resolution",
        },
        "work_lease_event_digest": {
            "algorithm": "sha-256",
            "subject": "exact referenced ResearchEvent canonical bytes",
            "profile_source": "referenced event contract member",
            "schema_source": "event_type and event_version siblings",
            "status": "requires_offline_event_registry_resolution",
        },
        "work_lease_artifact_digest": {
            "algorithm": "sha-256",
            "subject": "exact artifact bytes",
            "profile_source": "raw_bytes",
            "schema_source": "media_type sibling",
            "status": "requires_artifact_store_resolution",
        },
    }
    observed_digest_scopes = {
        "canonical_digest": nested(
            work_lease_schema,
            "properties",
            "canonical_digest",
            "x-odeya-digest-scope",
        ),
        **{
            name: nested(
                work_lease_schema,
                "$defs",
                name,
                "x-odeya-digest-scope",
            )
            for name in (
                "work_lease_record_digest",
                "work_lease_event_digest",
                "work_lease_artifact_digest",
            )
        },
    }
    if observed_digest_scopes != expected_digest_scopes:
        errors.append("canonical WorkLease digest-scope annotations are absent or ambiguous")
    if nested(
        work_lease_schema,
        "$defs",
        "work_lease_timestamp",
        "pattern",
    ) != r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$":
        errors.append("canonical WorkLease timestamps do not pin UTC microseconds")
    expected_state_machine = {
        "aggregate_absence_state": "unleased",
        "canonical_states": ["unleased", "active", "released", "revoked", "expired"],
        "record_states": ["active", "released", "revoked", "expired"],
        "terminal_states": ["released", "revoked", "expired"],
        "projection_only_labels": ["stale", "completed"],
        "terminal_reentry_allowed": False,
        "first_slice_transitions": [
            {"event_type": "work.lease_acquired", "from": "unleased", "to": "active"},
            {"event_type": "work.lease_released", "from": "active", "to": "released"},
            {"event_type": "work.lease_revoked", "from": "active", "to": "revoked"},
            {"event_type": "work.lease_expired", "from": "active", "to": "expired"},
        ],
        "first_slice_reservation_frontier": {
            "work.lease_acquired": "unclaimed",
            "work.lease_released": "claimed_requires_separate_settlement",
            "work.lease_revoked": "unclaimed_or_claimed_requires_separate_settlement_if_claimed",
            "work.lease_expired": "unclaimed",
            "lease_transition_changes_resource_reservation_state": False,
        },
        "outside_first_slice_transition": {
            "event_type": "work.lease_renewed",
            "from": "active",
            "to": "active",
            "candidate_support_status": "outside_scope_not_constructible",
        },
    }
    if work_lease_schema.get("x-odeya-work-lease-state-machine") != expected_state_machine:
        errors.append("canonical WorkLease candidate state-machine annotation drifted")

    release_branch = branches.get("work.lease_released")
    release_layers = (
        nested(release_branch[1], "properties", "payload", "allOf")
        if release_branch is not None
        else None
    )
    current_release_claim_state = None
    current_release_claim_ref_type = None
    if isinstance(release_layers, list) and len(release_layers) > 1:
        current_release_claim_state = nested(
            release_layers[1],
            "properties",
            "reservation_claim_state",
            "const",
        )
        current_release_claim_ref_type = nested(
            release_layers[1],
            "properties",
            "binding",
            "properties",
            "reservation",
            "properties",
            "reservation_claim_event_ref",
            "type",
        )
    if current_release_claim_state != "unclaimed" or current_release_claim_ref_type != "null":
        errors.append("recorded ResearchEvent release/claimed-reservation blocker no longer matches exact bytes")

    module_manifest = load_json(MODULE_MANIFEST_PATH)
    matching_owners = [
        item
        for item in module_manifest.get("schema_owners", [])
        if isinstance(item, dict)
        and item.get("schema_path") == "schemas/canonical-work-lease.schema.json"
    ]
    if matching_owners != [
        {
            "schema_path": "schemas/canonical-work-lease.schema.json",
            "schema_id": CANONICAL_WORK_LEASE_ID,
            "owner_module": "work",
            "contract_kind": "candidate_record",
        }
    ]:
        errors.append("canonical WorkLease candidate does not have exact work-module ownership")
    if nested(
        schema,
        "$defs",
        "canonical_work_lease_record_reference",
        "allOf",
    ) is None:
        errors.append("ResearchEvent lost its declared canonical WorkLease reference")
    else:
        lease_reference_layers = nested(
            schema,
            "$defs",
            "canonical_work_lease_record_reference",
            "allOf",
        )
        lease_ids = {
            nested(layer, "properties", "schema_id", "const")
            for layer in lease_reference_layers
            if isinstance(layer, dict)
        }
        if CANONICAL_WORK_LEASE_ID not in lease_ids:
            errors.append("ResearchEvent canonical WorkLease reference ID drifted")
    defining_paths: list[str] = []
    for candidate_path in ROOT.rglob("*.schema.json"):
        try:
            candidate = load_json(candidate_path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(candidate, dict) and candidate.get("$id") == CANONICAL_WORK_LEASE_ID:
            defining_paths.append(str(candidate_path.relative_to(ROOT)))
    if defining_paths != ["schemas/canonical-work-lease.schema.json"]:
        errors.append(
            "canonical WorkLease resource identity must have one exact defining path: "
            f"{sorted(defining_paths)}"
        )

    payload_v2: set[str] = set()
    for row in mappings:
        if not isinstance(row, dict):
            errors.append("identity map row is not an object")
            continue
        event_type = row.get("event_type")
        mapped = branches.get(event_type)
        if mapped is None:
            errors.append(f"identity map event {event_type!r} has no ResearchEvent branch")
            continue
        index, branch = mapped
        properties = branch.get("properties", {})
        expected = {
            "event_version": nested(properties, "event_version", "const"),
            "payload_type_id": nested(properties, "payload_type_id", "const"),
            "aggregate_type": nested(properties, "aggregate", "properties", "aggregate_type", "const"),
            "branch_index": index,
            "payload_branch_pointer": f"/oneOf/{index}/properties/payload",
            "schema_resource_id": schema.get("$id"),
            "schema_resource_raw_sha256": raw_digest,
            "schema_resource_byte_count": len(raw),
            "payload_contract_resolution_status": "unresolved_blocking",
            "payload_contract_digest": None,
            "event_contract_authority_status": "not_admitted_not_dispatchable_not_replay_authoritative",
        }
        for field, expected_value in expected.items():
            if row.get(field) != expected_value:
                errors.append(f"identity map {event_type}.{field} does not match exact branch identity")
        match = PAYLOAD_TYPE_VERSION.search(str(row.get("payload_type_id", "")))
        payload_version = match.group(1) if match else None
        if row.get("payload_type_version") != payload_version:
            errors.append(f"identity map {event_type}.payload_type_version is not derived from its logical payload type ID")
        if not str(row.get("payload_type_id", "")).startswith("urn:odeya:event-payload:"):
            errors.append(f"identity map {event_type}.payload_type_id is not a logical event-payload URN")
        if row.get("payload_type_id") == row.get("schema_resource_id"):
            errors.append(f"identity map {event_type} conflates logical payload type and schema resource")
        if row.get("event_version") != "1.0.0":
            errors.append(f"first-slice event {event_type} is not frozen at event version 1.0.0")
        if payload_version and payload_version.startswith("2."):
            payload_v2.add(str(event_type))
    if payload_v2 != EXPECTED_V2_PAYLOAD_TYPE_EVENTS:
        errors.append(f"payload-type-v2 exception set changed: {sorted(payload_v2)}")

    semantics = identity.get("identity_semantics", {})
    required_semantics = {
        "event_version_and_payload_type_version_are_independent": True,
        "payload_branch_selected_by_exact_event_identity_and_logical_payload_type_id": True,
        "payload_type_id_is_logical_not_schema_resource_id": True,
        "payload_contract_resolution_status": "unresolved_blocking",
        "payload_contract_digest": None,
        "payload_contract_digest_is_null_iff_status_unresolved_blocking": True,
        "per_branch_contract_extraction_profile_status": "not_frozen_not_computable",
        "future_resolved_contract_requires_new_research_event_resource_id": True,
        "unresolved_event_authority_status": "not_admitted_not_dispatchable_not_replay_authoritative",
    }
    for field, expected in required_semantics.items():
        if semantics.get(field) != expected:
            errors.append(f"identity_semantics.{field} is not {expected!r}")
    if set(semantics.get("logical_payload_type_major_version_two_event_types", [])) != EXPECTED_V2_PAYLOAD_TYPE_EVENTS:
        errors.append("identity map does not explicitly retain the four payload-type-v2/event-v1 branches")

    transition_expectations = {
        "authority.grant_issued": {"action": "issued", "from": "not_issued", "to": "issued"},
        "authority.grant_activated": {"action": "activated", "from": "issued", "to": "active"},
        "authority.grant_exhausted": {"action": "exhausted", "from": "active", "to": "exhausted"},
        "authority.grant_expired": {"action": "expired", "from": {"issued", "active"}, "to": "expired"},
        "authority.grant_revoked": {"action": "revoked", "from": {"issued", "active"}, "to": "revoked"},
        "work.lease_acquired": {"from": "unleased", "to": "active"},
        "work.lease_released": {"from": "active", "to": "released"},
        "work.lease_revoked": {"from": "active", "to": "revoked"},
        "work.lease_expired": {"from": "active", "to": "expired"},
    }
    for event_type, expected in transition_expectations.items():
        actual = transition_spec(branches[event_type][1])
        for field, expected_value in expected.items():
            if actual.get(field) != expected_value:
                errors.append(f"{event_type} {field} is {actual.get(field)!r}, expected {expected_value!r}")

    protocol_branch = branches["protocol.frozen"][1]
    protocol_props = protocol_branch.get("properties", {})
    if nested(protocol_props, "payload", "$ref") != "#/$defs/protocol_frozen_origin_payload":
        errors.append("protocol.frozen is not bound to the exact absence-origin payload")
    if nested(protocol_props, "commit", "properties", "batch_index", "const") != 1:
        errors.append("protocol.frozen is not second in its exact commit cohort")
    if nested(protocol_props, "commit", "properties", "batch_size", "const") != 4:
        errors.append("protocol.frozen commit cohort is not exactly four events")
    if nested(protocol_props, "authority_evidence", "properties", "mode", "const") != "bounded_grants":
        errors.append("protocol.frozen does not require bounded grant authority")
    protocol_payload = schema.get("$defs", {}).get("protocol_frozen_origin_payload", {})
    required_protocol_fields = {
        "prior_canonical_protocol_ref",
        "origin_from_aggregate_absence",
        "first_materialized_version",
        "frozen_protocol_snapshot_ref",
        "source_draft_evidence_ref",
        "validation_evidence_refs",
        "exposure_history_digest",
        "integrity_rule_ref",
        "grant_commit_binding",
    }
    if not required_protocol_fields <= set(protocol_payload.get("required", [])):
        errors.append("protocol absence-origin payload lacks exact snapshot/evidence requirements")
    protocol_fields = protocol_payload.get("properties", {})
    if nested(protocol_fields, "prior_canonical_protocol_ref", "type") != "null":
        errors.append("protocol origin does not require absence of prior canonical protocol")
    if nested(protocol_fields, "origin_from_aggregate_absence", "const") is not True:
        errors.append("protocol origin does not assert aggregate absence")
    if nested(protocol_fields, "first_materialized_version", "const") != 1:
        errors.append("protocol origin does not materialize first version 1")
    protocol_binding = schema.get("$defs", {}).get("protocol_grant_commit_binding", {})
    expected_protocol_order = [
        "authority.grant_used(protocol)",
        "protocol.frozen",
        "protocol.integrity_determined",
        "authority.grant_exhausted(protocol)",
    ]
    if nested(protocol_binding, "properties", "batch_order", "const") != expected_protocol_order:
        errors.append("protocol freeze grant/integrity/exhaustion order is not exact")

    data_branch = branches["data_use.decided"][1]
    data_props = data_branch.get("properties", {})
    if nested(data_props, "authority_evidence", "properties", "mode", "const") != "bounded_grants":
        errors.append("data_use.decided still permits assigned_role authority")
    if nested(data_props, "commit", "properties", "batch_index", "const") != 1:
        errors.append("data_use.decided is not second in its exact commit cohort")
    if nested(data_props, "commit", "properties", "batch_size", "const") != 3:
        errors.append("data_use.decided commit cohort is not exactly three events")
    data_binding = schema.get("$defs", {}).get("data_rights_grant_commit_binding", {})
    expected_data_order = [
        "authority.grant_used(data_rights)",
        "data_use.decided",
        "authority.grant_exhausted(data_rights)",
    ]
    if nested(data_binding, "properties", "batch_order", "const") != expected_data_order:
        errors.append("data-use grant/domain/exhaustion order is not exact")
    return errors


def data_fixture_errors(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if fixture.get("payload_contract_resolution_status") != "unresolved_blocking":
        errors.append("data-use fixture does not retain unresolved payload-contract status")
    if fixture.get("payload_contract_digest") is not None:
        errors.append("data-use fixture fabricates a per-branch payload-contract digest")
    if fixture.get("event_contract_authority_status") != "not_admitted_not_dispatchable_not_replay_authoritative":
        errors.append("data-use fixture claims authority despite unresolved branch contract")
    authority = fixture.get("authority_evidence", {})
    binding = fixture.get("payload", {}).get("grant_commit_binding", {})
    if authority.get("mode") != "bounded_grants":
        errors.append("data-use fixture authority mode is not bounded_grants")
    if len(authority.get("assignment_refs", [])) < 1:
        errors.append("data-use fixture has no assignment evidence")
    if len(authority.get("grant_refs", [])) != 1 or len(authority.get("grant_use_event_refs", [])) != 1:
        errors.append("data-use fixture does not bind exactly one grant and use event")
    elif authority["grant_refs"][0] != binding.get("grant_id"):
        errors.append("data-use fixture authority grant and payload grant differ")
    elif authority["grant_use_event_refs"][0] != binding.get("grant_use_event_ref"):
        errors.append("data-use fixture authority and payload grant-use events differ")
    if fixture.get("commit", {}).get("batch_index") != 1 or fixture.get("commit", {}).get("batch_size") != 3:
        errors.append("data-use fixture does not retain the exact three-event commit position")
    if binding.get("grant_exhaustion_event_ref") is None:
        errors.append("data-use fixture lacks same-cohort final-use exhaustion")
    return errors


def authority_grant_trace_errors(subject: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    state = subject.get("initial_state")
    max_uses = subject.get("max_uses")
    uses = 0
    pending_exhaustion = False
    if state != "not_issued":
        errors.append("grant trace does not start from aggregate absence/not_issued")
    if max_uses != 1:
        errors.append("grant trace is not single-use")
    transitions = {
        "authority.grant_issued": ({"not_issued"}, "issued"),
        "authority.grant_activated": ({"issued"}, "active"),
        "authority.grant_expired": ({"issued", "active"}, "expired"),
        "authority.grant_revoked": ({"issued", "active"}, "revoked"),
    }
    steps = subject.get("steps", [])
    for index, step in enumerate(steps):
        event_type = step.get("event_type")
        before = state
        if pending_exhaustion and event_type != "authority.grant_exhausted":
            errors.append(f"step {index} exposes a final grant use without immediate exhaustion")
        if event_type == "authority.grant_used":
            if state != "active":
                errors.append(f"step {index} uses a grant while {state!r}")
            if uses >= max_uses:
                errors.append(f"step {index} exceeds max_uses")
            uses += 1
            pending_exhaustion = uses == max_uses
            after = state
        elif event_type == "authority.grant_exhausted":
            if state != "active" or uses != max_uses or not pending_exhaustion:
                errors.append(f"step {index} exhausts before the exact final legal use")
            after = "exhausted"
            pending_exhaustion = False
        elif event_type in transitions:
            allowed, after = transitions[event_type]
            if state not in allowed:
                errors.append(f"step {index} cannot apply {event_type} from {state!r}")
        else:
            errors.append(f"step {index} uses unknown grant event {event_type!r}")
            after = state
        if step.get("declared_from") != before:
            errors.append(f"step {index} declared_from does not equal folded state {before!r}")
        if step.get("declared_to") != after:
            errors.append(f"step {index} declared_to does not equal legal result {after!r}")
        state = after
    if pending_exhaustion:
        errors.append("grant trace ends with an unexhausted final use")
    return errors


def valid_artifact_ref(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("artifact_id"), str)
        and bool(value["artifact_id"])
        and DIGEST.fullmatch(str(value.get("digest", ""))) is not None
        and isinstance(value.get("media_type"), str)
        and bool(value["media_type"])
    )


def valid_record_ref(value: Any, *, schema_id: str) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("object_id"), str)
        and bool(value["object_id"])
        and isinstance(value.get("version"), int)
        and value["version"] >= 1
        and value.get("schema_id") == schema_id
        and DIGEST.fullmatch(str(value.get("digest", ""))) is not None
        and valid_artifact_ref(value.get("artifact_ref"))
    )


def valid_versioned_identity(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("name"), str)
        and bool(value["name"])
        and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(value.get("version", ""))) is not None
        and DIGEST.fullmatch(str(value.get("digest", ""))) is not None
    )


def protocol_origin_errors(subject: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if subject.get("prior_canonical_protocol_ref") is not None:
        errors.append("protocol origin fabricates or depends on a prior canonical state")
    if subject.get("origin_from_aggregate_absence") is not True:
        errors.append("protocol origin is not explicitly from aggregate absence")
    if subject.get("first_materialized_version") != 1:
        errors.append("protocol origin does not materialize version 1")
    if not valid_record_ref(subject.get("frozen_protocol_snapshot_ref"), schema_id="urn:odeya:schema:protocol-snapshot:0.1.0"):
        errors.append("protocol origin lacks an exact frozen ProtocolSnapshot reference")
    if not valid_artifact_ref(subject.get("source_draft_evidence_ref")):
        errors.append("protocol origin lacks exact source-draft evidence")
    evidence = subject.get("validation_evidence_refs")
    if not isinstance(evidence, list) or not evidence or not all(valid_artifact_ref(item) for item in evidence):
        errors.append("protocol origin lacks one or more exact validation evidence references")
    if not DIGEST.fullmatch(str(subject.get("exposure_history_digest", ""))):
        errors.append("protocol origin lacks an exact exposure-history digest")
    if not valid_versioned_identity(subject.get("integrity_rule_ref")):
        errors.append("protocol origin lacks an exact integrity rule identity")
    if subject.get("authority_mode") != "bounded_grants" or subject.get("role_slot") != "protocol":
        errors.append("protocol freeze lacks the bounded protocol grant")
    expected_order = [
        "authority.grant_used(protocol)",
        "protocol.frozen",
        "protocol.integrity_determined",
        "authority.grant_exhausted(protocol)",
    ]
    if subject.get("commit_batch_index") != 1 or subject.get("commit_batch_size") != 4:
        errors.append("protocol freeze is not at index 1 of one four-event commit")
    if subject.get("batch_order") != expected_order:
        errors.append("protocol grant-use/freeze/integrity/exhaustion order is not exact")
    for field in ("grant_use_event_ref", "integrity_event_ref", "grant_exhaustion_event_ref"):
        if not isinstance(subject.get(field), str) or not subject[field]:
            errors.append(f"protocol origin lacks {field}")
    return errors


def data_use_cohort_errors(subject: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if subject.get("authority_mode") != "bounded_grants":
        errors.append("data-use decision is not authorized through bounded_grants")
    if not subject.get("assignment_refs"):
        errors.append("data-use decision lacks assignment evidence")
    grant_refs = subject.get("grant_refs", [])
    use_refs = subject.get("grant_use_event_refs", [])
    if len(grant_refs) != 1 or len(use_refs) != 1:
        errors.append("data-use decision must retain exactly one data_rights grant and use event")
    if subject.get("role_slot") != "data_rights":
        errors.append("data-use decision consumes the wrong authority slot")
    if grant_refs and subject.get("grant_id") != grant_refs[0]:
        errors.append("data-use payload grant differs from authority evidence")
    if use_refs and subject.get("grant_use_event_ref") != use_refs[0]:
        errors.append("data-use payload use-event differs from authority evidence")
    if not subject.get("grant_exhaustion_event_ref"):
        errors.append("data-use final grant use is not exhausted in the cohort")
    if subject.get("consumption_point") != "domain_commit" or subject.get("max_uses") != 1:
        errors.append("data-use grant is not single-use at domain commit")
    if subject.get("atomic_commit") is not True:
        errors.append("data-use authority and decision are split across commits")
    if subject.get("commit_batch_index") != 1 or subject.get("commit_batch_size") != 3:
        errors.append("data-use decision is not index 1 of exactly three events")
    expected = [
        "authority.grant_used(data_rights)",
        "data_use.decided",
        "authority.grant_exhausted(data_rights)",
    ]
    if subject.get("batch_order") != expected:
        errors.append("data-use grant-use/decision/exhaustion order is not exact")
    return errors


def work_lease_trace_errors(subject: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    canonical = ["unleased", "active", "released", "revoked", "expired"]
    projection_only = {"stale", "completed"}
    if subject.get("canonical_states") != canonical:
        errors.append("WorkLease canonical vocabulary is not the exact five-state sequence")
    if set(subject.get("projection_only_labels", [])) != projection_only:
        errors.append("stale/completed are not explicitly projection-only labels")
    state = subject.get("initial_state")
    if state != "unleased":
        errors.append("WorkLease trace does not start unleased")
    transitions = {
        "work.lease_acquired": ("unleased", "active"),
        "work.lease_released": ("active", "released"),
        "work.lease_revoked": ("active", "revoked"),
        "work.lease_expired": ("active", "expired"),
    }
    for index, step in enumerate(subject.get("steps", [])):
        event_type = step.get("event_type")
        before = state
        if event_type not in transitions:
            errors.append(f"step {index} uses a projection label or unknown WorkLease event")
            after = step.get("declared_to")
        else:
            required_from, after = transitions[event_type]
            if state != required_from:
                errors.append(f"step {index} cannot apply {event_type} from {state!r}")
        if step.get("declared_from") != before:
            errors.append(f"step {index} declared_from does not equal folded WorkLease state")
        if step.get("declared_to") != after:
            errors.append(f"step {index} declared_to does not equal legal WorkLease result")
        if step.get("declared_to") in projection_only:
            errors.append(f"step {index} promotes a projection-only label to canonical WorkLease state")
        state = after
    return errors


def work_lease_record_candidate_errors(subject: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    fixture_name = subject.get("fixture")
    fixture_path = WORK_LEASE_FIXTURES.get(fixture_name)
    if fixture_path is None:
        return ["WorkLease record case does not name one retained fixture"]
    record = deepcopy(load_json(fixture_path))
    mutation = subject.get("mutation")
    if mutation == "reverse_temporal_bounds":
        record["temporal_bounds"]["not_before"], record["temporal_bounds"]["expires_at"] = (
            record["temporal_bounds"]["expires_at"],
            record["temporal_bounds"]["not_before"],
        )
    elif mutation == "mismatch_work_intent_artifact_digest":
        record["work_intent_ref"]["artifact_ref"]["digest"] = (
            "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
    elif mutation == "terminal_allows_new_start_claim":
        record["lease_allows_new_start_claims"] = True
    elif mutation == "release_forgets_claimed_reservation":
        record["reservation_frontier"]["claim_state_at_transition"] = "unclaimed"
        record["reservation_frontier"]["reservation_claim_event_ref"] = None
    elif isinstance(mutation, dict):
        # The named mutations above are a closed vocabulary, and every guard they
        # cannot reach was therefore unprovable by construction: ADR 0025 measured
        # 4 of 29 proved here for exactly that reason. One bounded replace, the
        # same shape identity_map_mutation already uses, lets a known-bad case
        # break exactly one field of the retained fixture. It widens what a case
        # may express; it does not weaken a guard.
        if mutation.get("op") != "replace":
            return ["WorkLease record mutation is not one bounded replace operation"]
        path = mutation.get("path")
        if not isinstance(path, list) or not path:
            return ["WorkLease record mutation path is absent"]
        cursor: Any = record
        try:
            for segment in path[:-1]:
                cursor = cursor[segment]
            final = path[-1]
            if isinstance(cursor, list) and not isinstance(final, int):
                return ["WorkLease record list mutation index is not an integer"]
            cursor[final] = mutation.get("value")
        except (KeyError, IndexError, TypeError):
            return ["WorkLease record mutation path does not resolve"]
    elif mutation is not None:
        return [f"unknown WorkLease record mutation {mutation!r}"]

    if record.get("record_status") != "blocked_canonical_record_candidate":
        errors.append("WorkLease record fixture is not a blocked candidate")
    if record.get("identity_resolution_status") != "unresolved_blocking":
        errors.append("WorkLease record fixture fabricates resolved identity")
    if record.get("canonicalization_profile_ref") is not None or record.get("canonical_digest") is not None:
        errors.append("WorkLease record fixture fabricates profile or canonical digest")
    if record.get("record_authority_status") != "not_admitted_not_execution_authority":
        errors.append("WorkLease record fixture claims execution authority")

    work_intent = record.get("work_intent_ref", {})
    if work_intent.get("schema_id") != "urn:odeya:schema:work-intent:0.1.0":
        errors.append("WorkLease record fixture binds the wrong WorkIntent resource")
    if work_intent.get("digest") != nested(work_intent, "artifact_ref", "digest"):
        errors.append("WorkLease WorkIntent record and artifact digests differ")

    assignment = record.get("assignment_binding", {})
    if assignment.get("ordered_grant_roles") != [
        "safety",
        "data_rights",
        "resource",
        "execution",
        "verification",
    ]:
        errors.append("WorkLease assignment binding does not retain the exact five-role order")
    if nested(assignment, "assignment_event_ref", "event_type") != "verification.assigned":
        errors.append("WorkLease assignment binding lacks the verification assignment event")
    if assignment.get("cohort_resolution_status") != "unresolved_blocking":
        errors.append("WorkLease assignment binding fabricates a resolved cohort")
    if assignment.get("source_bytes_visible_at_assignment_commit") is not False:
        errors.append("WorkLease assignment binding exposes source bytes at assignment")
    if assignment.get("launch_outbox_created_at_assignment_commit") is not False:
        errors.append("WorkLease assignment binding creates a launch outbox at assignment")

    reservation = record.get("reservation_frontier", {})
    if nested(reservation, "reservation_created_event_ref", "event_type") != "resource.reservation_created":
        errors.append("WorkLease reservation frontier lacks its origin event")
    claim_state = reservation.get("claim_state_at_transition")
    claim_event_type = nested(reservation, "reservation_claim_event_ref", "event_type")
    if claim_state == "unclaimed" and reservation.get("reservation_claim_event_ref") is not None:
        errors.append("unclaimed WorkLease reservation frontier retains a claim event")
    if claim_state == "claimed" and claim_event_type != "resource.reservation_claimed":
        errors.append("claimed WorkLease reservation frontier lacks the claim event")
    if reservation.get("lease_transition_changes_resource_reservation_state") is not False:
        errors.append("WorkLease transition claims authority over ResourceLedger state")
    if reservation.get("claimed_reservation_requires_separate_settlement") is not True:
        errors.append("WorkLease frontier does not preserve separate claimed-reservation settlement")

    bounds = record.get("temporal_bounds", {})
    try:
        not_before = datetime.fromisoformat(str(bounds.get("not_before", "")).replace("Z", "+00:00"))
        expires_at = datetime.fromisoformat(str(bounds.get("expires_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errors.append("WorkLease temporal bounds are not parseable fixed instants")
    else:
        if not not_before < expires_at:
            errors.append("WorkLease not_before must precede expires_at")

    transition = record.get("transition", {})
    event_type = nested(transition, "event_ref", "event_type")
    transitions = {
        "work.lease_acquired": ("unleased", "active"),
        "work.lease_released": ("active", "released"),
        "work.lease_revoked": ("active", "revoked"),
        "work.lease_expired": ("active", "expired"),
    }
    expected_transition = transitions.get(event_type)
    if expected_transition is None:
        errors.append("WorkLease record fixture uses an unknown transition event")
    else:
        if (transition.get("from"), transition.get("to")) != expected_transition:
            errors.append("WorkLease record event and declared transition differ")
        if record.get("lease_state") != expected_transition[1]:
            errors.append("WorkLease record state differs from its transition result")
    if event_type == "work.lease_acquired":
        if record.get("lease_version") != 1 or transition.get("prior_active_event_ref") is not None:
            errors.append("WorkLease acquisition is not version-one origin from aggregate absence")
    else:
        prior_type = nested(transition, "prior_active_event_ref", "event_type")
        if record.get("lease_version", 0) < 2 or prior_type not in {
            "work.lease_acquired",
        }:
            errors.append("non-origin WorkLease transition lacks an active predecessor")
    if event_type == "work.lease_acquired":
        if claim_state != "unclaimed" or reservation.get("reservation_claim_event_ref") is not None:
            errors.append("WorkLease acquisition does not begin with an unclaimed reservation")
    elif event_type == "work.lease_released":
        if claim_state != "claimed" or claim_event_type != "resource.reservation_claimed":
            errors.append("first-slice WorkLease release forgets the claimed reservation awaiting settlement")
    elif event_type == "work.lease_expired":
        if claim_state != "unclaimed" or reservation.get("reservation_claim_event_ref") is not None:
            errors.append("first-slice WorkLease expiry is not the pre-claim deadline branch")
    if record.get("lease_state") in {"released", "revoked", "expired"}:
        if record.get("lease_allows_new_start_claims") is not False:
            errors.append("terminal WorkLease record permits a new start claim")
    return errors


def identity_map_mutation_errors(subject: dict[str, Any]) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    inventory = load_json(INVENTORY_PATH)
    identity = deepcopy(load_json(IDENTITY_MAP_PATH))
    mutation = subject.get("mutation")
    if mutation is not None:
        if not isinstance(mutation, dict) or mutation.get("op") != "replace":
            return ["identity-map mutation is not one bounded replace operation"]
        path = mutation.get("path")
        if not isinstance(path, list) or not path:
            return ["identity-map mutation path is absent"]
        # This model loads three inputs but could mutate only the identity map,
        # so every guard reading the schema or the inventory was unprovable by
        # construction -- 4 of 64, including the 60-event and 25-family
        # first-slice boundary guards. Naming the target widens what a case may
        # express without weakening a guard. load_json re-reads each call, so a
        # mutated input cannot leak into another case.
        targets = {"identity": identity, "schema": schema, "inventory": inventory}
        target_name = mutation.get("target", "identity")
        if target_name not in targets:
            return [f"identity-map mutation names an unknown target {target_name!r}"]
        current: Any = targets[target_name]
        try:
            for segment in path[:-1]:
                current = current[segment]
            final = path[-1]
            if isinstance(current, list) and not isinstance(final, int):
                return ["identity-map list mutation index is not an integer"]
            current[final] = mutation.get("value")
        except (KeyError, IndexError, TypeError):
            return ["identity-map mutation path does not resolve"]
    return schema_contract_errors(schema, inventory, identity)


MODEL_CHECKERS: dict[str, Callable[[dict[str, Any]], list[str]]] = {
    "authority_grant_trace": authority_grant_trace_errors,
    "protocol_origin": protocol_origin_errors,
    "data_use_cohort": data_use_cohort_errors,
    "work_lease_trace": work_lease_trace_errors,
    "work_lease_record_candidate": work_lease_record_candidate_errors,
    "identity_map_mutation": identity_map_mutation_errors,
}


def main() -> int:
    cases = load_json(CASES_PATH)
    schema = load_json(SCHEMA_PATH)
    inventory = load_json(INVENTORY_PATH)
    identity = load_json(IDENTITY_MAP_PATH)
    data_fixture = load_json(DATA_USE_FIXTURE_PATH)

    failures: list[str] = []
    failures.extend(schema_contract_errors(schema, inventory, identity))
    failures.extend(data_fixture_errors(data_fixture))

    observed_tags: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    for case in cases.get("cases", []):
        name = case.get("name", "<unnamed>")
        checker = MODEL_CHECKERS.get(case.get("model"))
        if checker is None:
            failures.append(f"{name}: unknown model {case.get('model')!r}")
            continue
        errors = checker(case.get("subject", {}))
        expect = case.get("expect")
        if expect == "accept":
            safe_count += 1
            if errors:
                failures.append(f"{name}: safe reference rejected: {'; '.join(errors)}")
        elif expect == "reject":
            adversarial_count += 1
            tag = case.get("adversarial_tag")
            if not isinstance(tag, str) or not tag:
                failures.append(f"{name}: adversarial case lacks a tag")
            else:
                observed_tags.add(tag)
            if not errors:
                failures.append(f"{name}: known-bad trace was accepted")
            expected_refusal = case.get("expected_refusal_contains")
            if not isinstance(expected_refusal, str) or not expected_refusal:
                failures.append(f"{name}: adversarial case does not declare the guard that must refuse it")
            elif not any(expected_refusal in error for error in errors):
                # Refusal for an incidental reason is not proof that the named
                # guard fires. Bind each known-bad trace to its own guard.
                failures.append(
                    f"{name}: refused, but not by its declared guard {expected_refusal!r}; got {errors}"
                )
        else:
            failures.append(f"{name}: invalid expectation {expect!r}")

    required_tags = set(cases.get("required_adversarial_tags", []))
    if observed_tags != required_tags:
        failures.append(
            "adversarial coverage mismatch: "
            f"missing={sorted(required_tags - observed_tags)} extra={sorted(observed_tags - required_tags)}"
        )
    if safe_count < 10 or adversarial_count < 15:
        failures.append("lifecycle closure suite lost its minimum safe/adversarial coverage")

    if failures:
        print("Lifecycle closure validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "Lifecycle closure validation passed: "
        f"60 event identities, 25 aggregate/reducer families, {safe_count} safe traces, "
        f"{adversarial_count} adversarial traces; cases={stable_json_digest(cases)}"
    )
    print(
        "Boundary: architecture evidence only; no immutable members, activation, runtime authority, or Gate A acceptance."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
