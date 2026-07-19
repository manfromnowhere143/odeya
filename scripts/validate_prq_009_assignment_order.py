#!/usr/bin/env python3
"""Validate the bounded PRQ-009 assignment-order consistency contract.

This is architecture validation only. It is not an Odeya command handler,
reducer, scheduler, assignment mechanism, dispatch path, or runtime authority.
"""

from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "architecture/prq-009-assignment-order-contract.json"
CASES_PATH = ROOT / "tests/prq-009-assignment-order/cases.json"

ROLE_ORDER = ["safety", "data_rights", "resource", "execution", "verification"]
EVENT_ORDER = [
    *(f"authority.grant_used({role})" for role in ROLE_ORDER),
    "resource.reservation_created",
    "work.lease_acquired",
    "verification.assigned",
    *(f"authority.grant_exhausted({role})" for role in ROLE_ORDER),
]
CANONICAL_ORDER = ["WorkIntent", "verification.assign", "WorkContract", "attempt.start"]
CREATES_OR_BINDS = [
    "selected_worker_principal",
    "five_ordered_assignment_grant_uses_and_exhaustions",
    "active_work_lease",
    "resource_reservation",
    "verification_assignment",
]

EXPECTED_ACTIVE_CONSUMERS = {
    "docs/TRANSACTION_MODEL.md": "corrected",
    "docs/SEMANTIC_VALIDATION.md": "corrected",
    "docs/VERIFICATION_PROTOCOL.md": "clarified",
    "docs/GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md": "consistent",
    "docs/COGNITIVE_CONTROL_CONTRACTS.md": "consistent",
    "docs/FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md": "consistent",
    "docs/decisions/0016-separate-work-intent-from-assigned-work-contract.md": "consistent",
    "architecture/first-slice-admission-resolution-candidate.json": "consistent",
    "architecture/gate-a-prerequisite-closure.json": "consistent",
    "schemas/work-intent.schema.json": "consistent",
    "schemas/work-contract.schema.json": "consistent",
    "schemas/canonical-work-lease.schema.json": "consistent",
    "docs/COMMAND_EVENT_CATALOG.md": "consistent",
    "docs/MATHEMATICAL_CONSTITUTION.md": "consistent",
}
EXPECTED_SUPERSEDED_CONSUMERS = {
    "docs/FIRST_SLICE_ADMISSION_CLOSURE_PLAN.md":
        "Status: superseded pre-resolution architecture-evidence hypothesis",
    "architecture/first-slice-admission-gap-inventory.json":
        "\"status\": \"non_authoritative_non_freezable_gap_hypothesis\"",
}
FORBIDDEN_FRAGMENTS = [
    "`verification.assign` atomically binds one exact local WorkContract",
    "`verification.assign` binds exact active DataUseDecisions, promoted input manifests, local WorkContract",
    "WorkContract -> verification.assign -> WorkIntent",
    "pre-existing WorkContract -> verification.assign",
]
EXPECTED_KNOWN_BAD_SPECS = {
    "legacy-preexisting-work-contract-prose-is-rejected": {
        "mutation": {
            "target": "consumer_text",
            "path": "docs/TRANSACTION_MODEL.md",
            "operation": "prepend",
            "value": "`verification.assign` atomically binds one exact local WorkContract",
        },
        "expected_refusal_contains":
            "docs/TRANSACTION_MODEL.md contains forbidden legacy assignment-order fragment",
    },
    "legacy-work-contract-as-prospective-input-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/assignment_commit/prospective_work_input",
            "value": "WorkContract",
        },
        "expected_refusal_contains":
            "assignment prospective work input is not WorkIntent",
    },
    "legacy-preexisting-work-contract-flag-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/assignment_commit/preexisting_work_contract_allowed",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment permits a pre-existing WorkContract",
    },
    "legacy-preexisting-active-lease-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/assignment_commit/preexisting_active_work_lease_allowed",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment permits a pre-existing active WorkLease",
    },
    "legacy-preexisting-reservation-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/assignment_commit/preexisting_resource_reservation_allowed",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment permits a pre-existing resource reservation",
    },
    "work-contract-inside-assignment-batch-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/work_contract_derivation/member_of_assignment_event_batch",
            "value": True,
        },
        "expected_refusal_contains":
            "WorkContract is not exclusively post-assignment",
    },
    "assignment-dispatch-claim-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/assignment_commit/dispatch_claim_created",
            "value": True,
        },
        "expected_refusal_contains": "assignment creates a dispatch claim",
    },
    "incomplete-assignment-cohort-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "remove",
            "pointer": "/assignment_commit/event_order_exact/12",
        },
        "expected_refusal_contains":
            "assignment event order is not the exact thirteen-event cohort",
    },
    "dispatch-before-derived-work-contract-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/dispatch_claim/phase",
            "value": "same_assignment_commit",
        },
        "expected_refusal_contains":
            "attempt.start is not a separate post-WorkContract commit",
    },
    "premature-prq-009-closure-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/current_evidence_boundary/status",
            "value": "resolved",
        },
        "expected_refusal_contains":
            "PRQ-009 evidence boundary is not unresolved_blocking",
    },
    "runtime-authority-from-order-contract-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "replace",
            "pointer": "/current_evidence_boundary/runtime_authorized",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment-order evidence claims runtime authority",
    },
    "unexpected-top-level-authority-member-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "add",
            "pointer": "/runtime_authorized",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment-order contract members are not closed and exact",
    },
    "unexpected-assignment-dispatch-member-is-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "add",
            "pointer": "/assignment_commit/unrestricted_dispatch_authorized",
            "value": True,
        },
        "expected_refusal_contains":
            "assignment_commit members are not closed and exact",
    },
    "weakened-active-consumer-fragments-are-rejected": {
        "mutation": {
            "target": "contract",
            "operation": "remove",
            "pointer": "/active_consumer_audit/0/required_fragments/0",
        },
        "expected_refusal_contains":
            "active consumer specifications drifted from the pinned exact "
            "path/disposition/fragment matrix",
    },
}
REQUIRED_KNOWN_BADS = frozenset(EXPECTED_KNOWN_BAD_SPECS)
CONTRACT_KEYS = {
    "contract_id",
    "version",
    "artifact_class",
    "status",
    "canonical_order",
    "assignment_commit",
    "work_contract_derivation",
    "dispatch_claim",
    "current_evidence_boundary",
    "consumer_census_scope",
    "active_consumer_audit",
    "superseded_consumer_audit",
    "forbidden_active_consumer_fragments",
}
ASSIGNMENT_COMMIT_KEYS = {
    "command_type",
    "prospective_work_input",
    "preexisting_work_contract_allowed",
    "preexisting_active_work_lease_allowed",
    "preexisting_resource_reservation_allowed",
    "atomic_commit",
    "intermediate_visibility",
    "role_slot_order",
    "event_order_exact",
    "creates_or_binds",
    "source_bytes_visible",
    "launch_outbox_created",
    "dispatch_claim_created",
}
DISPATCH_CLAIM_KEYS = {
    "command_type",
    "phase",
    "requires_derived_work_contract",
    "rechecks_current_assignment_facts",
    "claims_assignment_reservation",
    "may_cross_execution_boundary_only_after_commit",
}
EVIDENCE_BOUNDARY_KEYS = {
    "prerequisite_id",
    "status",
    "required_identities_and_members_exist",
    "command_or_event_admitted",
    "gate_a_accepted",
    "runtime_authorized",
}
EXPECTED_ACTIVE_CONSUMER_AUDIT_SHA256 = (
    "b009a66f82084a10e8ae4a10c80e1518ab8e69395c4ca7a09ac6a331d57a34c6"
)
EXPECTED_SUPERSEDED_CONSUMER_AUDIT_SHA256 = (
    "2b64ef7d3a64c8f33483221d5bf8e7254d702a5f086470b8b6673db64021fd10"
)


class DuplicateKey(ValueError):
    """Raised when JSON would otherwise silently replace an earlier member."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_pairs,
    )


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_consumer_texts(contract: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    texts: dict[str, str] = {}
    errors: list[str] = []
    allowed = set(EXPECTED_ACTIVE_CONSUMERS) | set(EXPECTED_SUPERSEDED_CONSUMERS)
    entries = [
        *contract.get("active_consumer_audit", []),
        *contract.get("superseded_consumer_audit", []),
    ]
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            errors.append(f"consumer audit entry {index} lacks a string path")
            continue
        relative = entry["path"]
        if relative not in allowed:
            errors.append(f"consumer audit attempts to read unregistered path {relative}")
            continue
        path = ROOT / relative
        try:
            texts[relative] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read consumer {relative}: {exc}")
    return texts, errors


def consumer_errors(contract: dict[str, Any], texts: dict[str, str]) -> list[str]:
    errors: list[str] = []
    active = contract.get("active_consumer_audit")
    if not isinstance(active, list):
        return ["active_consumer_audit is not a list"]
    if canonical_json_sha256(active) != EXPECTED_ACTIVE_CONSUMER_AUDIT_SHA256:
        errors.append(
            "active consumer specifications drifted from the pinned exact "
            "path/disposition/fragment matrix"
        )

    observed: dict[str, str] = {}
    for index, entry in enumerate(active):
        if not isinstance(entry, dict):
            errors.append(f"active_consumer_audit[{index}] is not an object")
            continue
        if set(entry) != {"path", "disposition", "required_fragments"}:
            errors.append(
                f"active_consumer_audit[{index}] members are not closed and exact"
            )
            continue
        path = entry.get("path")
        disposition = entry.get("disposition")
        if not isinstance(path, str) or not isinstance(disposition, str):
            errors.append(f"active_consumer_audit[{index}] lacks path/disposition")
            continue
        if path in observed:
            errors.append(f"active consumer {path} is duplicated")
        observed[path] = disposition
        fragments = entry.get("required_fragments")
        if (
            not isinstance(fragments, list)
            or not fragments
            or any(not isinstance(fragment, str) or not fragment for fragment in fragments)
            or len(fragments) != len(set(fragments))
        ):
            errors.append(f"{path} required_fragments are not a nonempty unique string list")
            continue
        text = texts.get(path)
        if text is None:
            errors.append(f"{path} has no loaded consumer text")
            continue
        for fragment in fragments:
            if fragment not in text:
                errors.append(f"{path} lacks required assignment-order fragment: {fragment}")

    if observed != EXPECTED_ACTIVE_CONSUMERS:
        missing = sorted(set(EXPECTED_ACTIVE_CONSUMERS) - set(observed))
        extra = sorted(set(observed) - set(EXPECTED_ACTIVE_CONSUMERS))
        wrong = sorted(
            path
            for path in set(observed) & set(EXPECTED_ACTIVE_CONSUMERS)
            if observed[path] != EXPECTED_ACTIVE_CONSUMERS[path]
        )
        errors.append(
            "active assignment-order consumer census drifted: "
            f"missing={missing}, extra={extra}, wrong_disposition={wrong}"
        )

    forbidden = contract.get("forbidden_active_consumer_fragments")
    if forbidden != FORBIDDEN_FRAGMENTS:
        errors.append("forbidden active-consumer fragment set drifted")
    for path in EXPECTED_ACTIVE_CONSUMERS:
        text = texts.get(path, "")
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in text:
                errors.append(
                    f"{path} contains forbidden legacy assignment-order fragment: {fragment}"
                )

    superseded = contract.get("superseded_consumer_audit")
    if not isinstance(superseded, list):
        return [*errors, "superseded_consumer_audit is not a list"]
    if (
        canonical_json_sha256(superseded)
        != EXPECTED_SUPERSEDED_CONSUMER_AUDIT_SHA256
    ):
        errors.append(
            "superseded consumer specifications drifted from the pinned exact matrix"
        )
    observed_superseded: dict[str, str] = {}
    for index, entry in enumerate(superseded):
        if not isinstance(entry, dict):
            errors.append(f"superseded_consumer_audit[{index}] is not an object")
            continue
        if set(entry) != {"path", "required_status_fragment", "reason"}:
            errors.append(
                f"superseded_consumer_audit[{index}] members are not closed and exact"
            )
            continue
        path = entry.get("path")
        status = entry.get("required_status_fragment")
        reason = entry.get("reason")
        if not all(isinstance(value, str) and value for value in (path, status, reason)):
            errors.append(f"superseded_consumer_audit[{index}] is incomplete")
            continue
        if path in observed_superseded:
            errors.append(f"superseded consumer {path} is duplicated")
        observed_superseded[path] = status
        if status not in texts.get(path, ""):
            errors.append(f"{path} lacks its required superseded status")
    if observed_superseded != EXPECTED_SUPERSEDED_CONSUMERS:
        errors.append("superseded assignment-order consumer census drifted")
    return errors


def structural_consumer_errors() -> list[str]:
    """Check the machine consumers whose exact semantics exceed text presence."""

    errors: list[str] = []
    first_slice = load_json(ROOT / "architecture/first-slice-admission-resolution-candidate.json")
    prqs = first_slice.get("unresolved_prerequisites", [])
    if len(prqs) != 1 or prqs[0].get("prerequisite_id") != "PRQ-009":
        errors.append("first-slice candidate does not expose exactly one PRQ-009 prerequisite")
    else:
        prq = prqs[0]
        if prq.get("status") != "unresolved_blocking":
            errors.append("first-slice PRQ-009 is not unresolved_blocking")
        assignment = prq.get("prospective_assignment_contract", {})
        if assignment.get("command_type") != "verification.assign":
            errors.append("first-slice PRQ-009 does not bind verification.assign")
        if assignment.get("role_slot_order") != ROLE_ORDER:
            errors.append("first-slice PRQ-009 role order drifted")
        if assignment.get("batch_size_exact") != 13:
            errors.append("first-slice PRQ-009 batch size is not thirteen")
        if assignment.get("event_order_exact") != EVENT_ORDER:
            errors.append("first-slice PRQ-009 event order drifted")
        bindings = prq.get("required_exact_bindings", [])
        if not any(
            isinstance(value, str) and value.startswith("one post-assignment WorkContract")
            for value in bindings
        ):
            errors.append("first-slice PRQ-009 lacks post-assignment WorkContract derivation")
        if not any(
            isinstance(value, str) and "reservation created in this commit" in value
            for value in bindings
        ):
            errors.append("first-slice PRQ-009 does not create the reservation in assignment")
        if not any(
            isinstance(value, str) and "WorkLease acquired in this commit" in value
            for value in bindings
        ):
            errors.append("first-slice PRQ-009 does not acquire the active lease in assignment")

    gate = load_json(ROOT / "architecture/gate-a-prerequisite-closure.json")
    gate_prqs = [
        finding
        for finding in gate.get("findings", [])
        if finding.get("finding_id") == "PRQ-009"
    ]
    if len(gate_prqs) != 1:
        errors.append("Gate A prerequisite record does not contain exactly one PRQ-009")
    elif gate_prqs[0].get("status") != "unresolved_blocking":
        errors.append("Gate A prerequisite PRQ-009 is not unresolved_blocking")
    elif "then derive a post-commit non-dispatch WorkContract" not in gate_prqs[0].get("closure", ""):
        errors.append("Gate A prerequisite PRQ-009 lost post-commit WorkContract derivation")

    lease = load_json(ROOT / "schemas/canonical-work-lease.schema.json")
    assignment_properties = (
        lease.get("properties", {})
        .get("assignment_binding", {})
        .get("properties", {})
    )
    if assignment_properties.get("assignment_command_type", {}).get("const") != "verification.assign":
        errors.append("canonical WorkLease assignment command is not verification.assign")
    if assignment_properties.get("source_bytes_visible_at_assignment_commit", {}).get("const") is not False:
        errors.append("canonical WorkLease permits source-byte visibility at assignment")
    if assignment_properties.get("launch_outbox_created_at_assignment_commit", {}).get("const") is not False:
        errors.append("canonical WorkLease permits a launch outbox at assignment")

    work_intent = load_json(ROOT / "schemas/work-intent.schema.json")
    if work_intent.get("properties", {}).get("record_authority_status", {}).get("const") != (
        "not_admitted_not_assignable"
    ):
        errors.append("WorkIntent schema no longer fails closed as unassignable")

    work_contract = load_json(ROOT / "schemas/work-contract.schema.json")
    if work_contract.get("properties", {}).get("construction_status", {}).get("const") != (
        "blocked_pending_resolved_work_intent_and_assignment_cohort"
    ):
        errors.append("WorkContract schema no longer blocks construction on assignment")
    if work_contract.get("properties", {}).get("dispatchability_status", {}).get("const") != (
        "non_dispatchable_non_authoritative"
    ):
        errors.append("WorkContract schema claims dispatch authority")
    return errors


def contract_errors(contract: dict[str, Any], texts: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if set(contract) != CONTRACT_KEYS:
        errors.append("assignment-order contract members are not closed and exact")
    if contract.get("contract_id") != "odeya.prq-009-assignment-order-consistency":
        errors.append("assignment-order contract ID drifted")
    if contract.get("version") != "1.0.0":
        errors.append("assignment-order contract version is not 1.0.0")
    if contract.get("artifact_class") != "architecture_consistency_evidence_only":
        errors.append("assignment-order artifact class overclaims its evidence")
    if contract.get("status") != "unresolved_blocking":
        errors.append("assignment-order contract does not keep PRQ-009 unresolved")
    if contract.get("canonical_order") != CANONICAL_ORDER:
        errors.append("canonical assignment order is not WorkIntent -> assign -> WorkContract -> start")
    if contract.get("consumer_census_scope") != (
        "active sources that directly assert the bounded local-assignment construction order, "
        "its event producers, or its fail-closed structural boundaries; enumeration-only "
        "fixtures and external-dispatch-only semantics are outside this census"
    ):
        errors.append("assignment-order consumer census scope drifted or overclaims completeness")

    assignment_value = contract.get("assignment_commit")
    if not isinstance(assignment_value, dict):
        errors.append("assignment_commit is not an object")
        assignment: dict[str, Any] = {}
    else:
        assignment = assignment_value
        if set(assignment) != ASSIGNMENT_COMMIT_KEYS:
            errors.append("assignment_commit members are not closed and exact")
    if assignment.get("command_type") != "verification.assign":
        errors.append("assignment command is not verification.assign")
    if assignment.get("prospective_work_input") != "WorkIntent":
        errors.append("assignment prospective work input is not WorkIntent")
    if assignment.get("preexisting_work_contract_allowed") is not False:
        errors.append("assignment permits a pre-existing WorkContract")
    if assignment.get("preexisting_active_work_lease_allowed") is not False:
        errors.append("assignment permits a pre-existing active WorkLease")
    if assignment.get("preexisting_resource_reservation_allowed") is not False:
        errors.append("assignment permits a pre-existing resource reservation")
    if assignment.get("atomic_commit") is not True or assignment.get("intermediate_visibility") is not False:
        errors.append("assignment is not one atomic commit with no interior visibility")
    if assignment.get("role_slot_order") != ROLE_ORDER:
        errors.append("assignment role order is not exact")
    if assignment.get("event_order_exact") != EVENT_ORDER:
        errors.append("assignment event order is not the exact thirteen-event cohort")
    if assignment.get("creates_or_binds") != CREATES_OR_BINDS:
        errors.append("assignment output/binding set drifted")
    if assignment.get("source_bytes_visible") is not False:
        errors.append("assignment exposes source bytes")
    if assignment.get("launch_outbox_created") is not False:
        errors.append("assignment creates a launch outbox")
    if assignment.get("dispatch_claim_created") is not False:
        errors.append("assignment creates a dispatch claim")

    derivation_value = contract.get("work_contract_derivation")
    if not isinstance(derivation_value, dict):
        errors.append("work_contract_derivation is not an object")
        derivation: dict[str, Any] = {}
    else:
        derivation = derivation_value
    expected_derivation = {
        "artifact_type": "WorkContract",
        "phase": "after_exact_successful_assignment_commit",
        "deterministic": True,
        "binds_exact_work_intent": True,
        "binds_exact_assignment_commit": True,
        "member_of_assignment_event_batch": False,
        "authorizes_dispatch": False,
    }
    if derivation != expected_derivation:
        errors.append("WorkContract is not exclusively post-assignment")

    dispatch_value = contract.get("dispatch_claim")
    if not isinstance(dispatch_value, dict):
        errors.append("dispatch_claim is not an object")
        dispatch: dict[str, Any] = {}
    else:
        dispatch = dispatch_value
        if set(dispatch) != DISPATCH_CLAIM_KEYS:
            errors.append("dispatch_claim members are not closed and exact")
    if dispatch.get("command_type") != "attempt.start":
        errors.append("dispatch claim command is not attempt.start")
    if dispatch.get("phase") != "separate_post_work_contract_commit":
        errors.append("attempt.start is not a separate post-WorkContract commit")
    if dispatch.get("requires_derived_work_contract") is not True:
        errors.append("attempt.start does not require the derived WorkContract")
    if dispatch.get("rechecks_current_assignment_facts") is not True:
        errors.append("attempt.start does not recheck current assignment facts")
    if dispatch.get("claims_assignment_reservation") is not True:
        errors.append("attempt.start does not claim the assignment reservation")
    if dispatch.get("may_cross_execution_boundary_only_after_commit") is not True:
        errors.append("execution may cross before the attempt.start commit")

    boundary_value = contract.get("current_evidence_boundary")
    if not isinstance(boundary_value, dict):
        errors.append("current_evidence_boundary is not an object")
        boundary: dict[str, Any] = {}
    else:
        boundary = boundary_value
        if set(boundary) != EVIDENCE_BOUNDARY_KEYS:
            errors.append(
                "current_evidence_boundary members are not closed and exact"
            )
    if boundary.get("prerequisite_id") != "PRQ-009":
        errors.append("evidence boundary is not PRQ-009")
    if boundary.get("status") != "unresolved_blocking":
        errors.append("PRQ-009 evidence boundary is not unresolved_blocking")
    if boundary.get("required_identities_and_members_exist") is not False:
        errors.append("assignment-order evidence fabricates identities or members")
    if boundary.get("command_or_event_admitted") is not False:
        errors.append("assignment-order evidence claims command/event admission")
    if boundary.get("gate_a_accepted") is not False:
        errors.append("assignment-order evidence claims Gate A acceptance")
    if boundary.get("runtime_authorized") is not False:
        errors.append("assignment-order evidence claims runtime authority")

    errors.extend(consumer_errors(contract, texts))
    return errors


def resolve_pointer(root: Any, pointer: str) -> tuple[Any, str]:
    if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
        raise ValueError("JSON pointer must be a non-root absolute pointer")
    parts = [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]
    current = root
    for token in parts[:-1]:
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise ValueError(f"cannot descend through {type(current).__name__}")
    return current, parts[-1]


def mutate_contract(contract: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    candidate = deepcopy(contract)
    parent, token = resolve_pointer(candidate, mutation.get("pointer"))
    operation = mutation.get("operation")
    if operation == "replace":
        if isinstance(parent, list):
            parent[int(token)] = deepcopy(mutation.get("value"))
        elif isinstance(parent, dict) and token in parent:
            parent[token] = deepcopy(mutation.get("value"))
        else:
            raise ValueError("replace target does not exist")
    elif operation == "remove":
        if isinstance(parent, list):
            del parent[int(token)]
        elif isinstance(parent, dict) and token in parent:
            del parent[token]
        else:
            raise ValueError("remove target does not exist")
    elif operation == "add":
        if not isinstance(parent, dict):
            raise ValueError("add target parent is not an object")
        if token in parent:
            raise ValueError("add target already exists")
        parent[token] = deepcopy(mutation.get("value"))
    else:
        raise ValueError(f"unsupported contract mutation operation {operation!r}")
    if candidate == contract:
        raise ValueError("contract mutation made no change")
    return candidate


def evaluate_known_bads(
    contract: dict[str, Any],
    baseline_texts: dict[str, str],
    cases_document: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if set(cases_document) != {
        "suite_id",
        "version",
        "evidence_class",
        "cases",
    }:
        errors.append("known-bad suite members are not closed and exact")
    if cases_document.get("suite_id") != "odeya.prq-009-assignment-order-known-bads":
        errors.append("known-bad suite ID drifted")
    if cases_document.get("version") != "1.0.0":
        errors.append("known-bad suite version is not 1.0.0")
    if cases_document.get("evidence_class") != "architecture_consistency_known_bad_only":
        errors.append("known-bad suite overclaims its evidence class")
    cases = cases_document.get("cases")
    if not isinstance(cases, list):
        return [*errors, "known-bad cases are not a list"]

    names = [case.get("name") for case in cases if isinstance(case, dict)]
    if len(names) != len(cases) or any(not isinstance(name, str) or not name for name in names):
        errors.append("known-bad cases do not all have string names")
    elif len(names) != len(set(names)):
        errors.append("known-bad case names are not unique")
    elif set(names) != REQUIRED_KNOWN_BADS:
        errors.append(
            "known-bad case census drifted: "
            f"missing={sorted(REQUIRED_KNOWN_BADS - set(names))}, "
            f"extra={sorted(set(names) - REQUIRED_KNOWN_BADS)}"
        )

    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"known-bad case {index} is not an object")
            continue
        name = case.get("name", f"case[{index}]")
        if set(case) != {
            "name",
            "kind",
            "mutation",
            "expected_refusal_contains",
        }:
            errors.append(f"{name}: known-bad case members are not closed and exact")
            continue
        if case.get("kind") != "known_bad":
            errors.append(f"{name}: kind is not known_bad")
            continue
        expected = case.get("expected_refusal_contains")
        mutation = case.get("mutation")
        if not isinstance(expected, str) or not expected:
            errors.append(f"{name}: expected_refusal_contains is absent")
            continue
        if not isinstance(mutation, dict):
            errors.append(f"{name}: mutation is not an object")
            continue
        expected_spec = EXPECTED_KNOWN_BAD_SPECS.get(name)
        observed_spec = {
            "mutation": mutation,
            "expected_refusal_contains": expected,
        }
        if expected_spec != observed_spec:
            errors.append(
                f"{name}: mutation/refusal specification drifted from the "
                "pinned known-bad matrix"
            )
            continue

        candidate = contract
        texts = dict(baseline_texts)
        try:
            if mutation.get("target") == "contract":
                candidate = mutate_contract(contract, mutation)
            elif mutation.get("target") == "consumer_text":
                path = mutation.get("path")
                if path not in EXPECTED_ACTIVE_CONSUMERS:
                    raise ValueError("consumer-text mutation targets an unregistered active consumer")
                if mutation.get("operation") != "prepend":
                    raise ValueError("consumer-text mutation operation is not prepend")
                value = mutation.get("value")
                if not isinstance(value, str) or not value:
                    raise ValueError("consumer-text mutation value is empty")
                texts[path] = value + "\n" + texts[path]
            else:
                raise ValueError(f"unknown mutation target {mutation.get('target')!r}")
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{name}: mutation failed: {exc}")
            continue

        refusals = contract_errors(candidate, texts)
        if not refusals:
            errors.append(f"{name}: known-bad mutation was accepted")
        elif not any(expected in refusal for refusal in refusals):
            errors.append(
                f"{name}: expected refusal {expected!r} absent; got {refusals!r}"
            )
    return errors


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    try:
        contract = load_json(CONTRACT_PATH)
        cases_document = load_json(CASES_PATH)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey) as exc:
        print(f"PRQ-009 assignment-order validation: FAIL — {exc}", file=sys.stderr)
        return 1
    if not isinstance(contract, dict) or not isinstance(cases_document, dict):
        print("PRQ-009 assignment-order validation: FAIL — roots must be objects", file=sys.stderr)
        return 1

    texts, errors = load_consumer_texts(contract)
    errors.extend(contract_errors(contract, texts))
    errors.extend(structural_consumer_errors())
    errors.extend(evaluate_known_bads(contract, texts, cases_document))

    if errors:
        print("PRQ-009 assignment-order validation: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "PRQ-009 assignment-order validation: PASS — "
        f"{len(EXPECTED_ACTIVE_CONSUMERS)} active consumers, "
        f"{len(EXPECTED_SUPERSEDED_CONSUMERS)} superseded consumers, "
        f"{len(REQUIRED_KNOWN_BADS)} retained known-bads"
    )
    print(
        "- architecture record raw SHA-256 "
        f"{raw_sha256(CONTRACT_PATH)} (file identity only; not canonical-profile evidence)"
    )
    print(
        "- known-bad record raw SHA-256 "
        f"{raw_sha256(CASES_PATH)} (file identity only; not canonical-profile evidence)"
    )
    print("- PRQ-009 remains unresolved_blocking; no member, Gate A, or runtime authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
