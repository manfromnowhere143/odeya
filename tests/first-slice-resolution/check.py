#!/usr/bin/env python3
"""Check bounded C1-C8 first-slice resolution fixtures.

This is architecture test evidence, not an Odeya runtime, reducer, scheduler,
registry, activation mechanism, or authorization surface.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests/first-slice-resolution/cases.json"
EXPECTED_CONFLICTS = {f"C{index}" for index in range(1, 9)}
EXPECTED_P0 = "P0.constitutional-recovery-admission"
EXPECTED_AXES = ["reproducibility", "replication", "transport"]
VERIFICATION_ASSIGN_ROLES = ["safety", "data_rights", "resource", "execution", "verification"]
VERIFICATION_ASSIGN_EVENTS = [
    *(f"authority.grant_used({role})" for role in VERIFICATION_ASSIGN_ROLES),
    "resource.reservation_created",
    "work.lease_acquired",
    "verification.assigned",
    *(f"authority.grant_exhausted({role})" for role in VERIFICATION_ASSIGN_ROLES),
]
VERIFICATION_ASSIGN_BINDINGS = [
    "one resolved admitted assignable WorkIntent resource ID version canonical digest and exact retained bytes",
    "one post-assignment WorkContract whose source WorkIntent identity and assignment commit identity equal the command result",
    "the complete active current DataUseDecision set for every governed input at the assignment commit position",
    "the exact zero-external-capability sandbox profile and governing policy decision",
    "the exact resource reservation created in this commit",
    "the exact active WorkLease acquired in this commit",
    "five distinct action-instance-bound single-use grants in the declared global role-slot order",
    "one command ID request digest receipt ID admission evidence bundle registry activation and commit identity equal across the entire cohort",
]
NONNEGATIVE_DECIMAL = re.compile(r"^(0|[1-9][0-9]*)(\.[0-9]+)?$")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_json_digest(value: Any) -> str:
    """Identify retained fixtures; this is not the Odeya canonical profile."""

    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def exact_nonnegative_decimal(value: Any) -> bool:
    if not isinstance(value, str) or NONNEGATIVE_DECIMAL.fullmatch(value) is None:
        return False
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        return False
    return parsed.is_finite() and parsed >= 0


def inventory_errors(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if inventory.get("schema_version") != "0.2.0" or inventory.get("version") != "0.2.0":
        errors.append("materially changed inventory was not reissued as exact version 0.2.0")
    if inventory.get("status") != "bounded_scope_candidate_c5_blocked_not_admitted":
        errors.append("inventory status does not expose the blocking C5 boundary")

    scope = inventory.get("scope_verdict", {})
    required_scope = {
        "c1_through_c8_choices_resolved": False,
        "representational_member_sets_exact": True,
        "activation_dependency_complete": False,
        "immutable_registry_members_exist": False,
        "engine_contract_root_exists": False,
        "constitutional_prerequisite_instance_exists": False,
        "registry_activation_exists": False,
        "may_construct_verification_assignment_member": False,
        "may_freeze_registry_snapshot": False,
        "may_activate": False,
        "may_start_runtime_implementation": False,
    }
    for field, expected in required_scope.items():
        if scope.get(field) is not expected:
            errors.append(f"scope_verdict.{field} is not {expected!r}")

    counts = inventory.get("counts", {})
    commands = inventory.get("required_commands", [])
    outside = inventory.get("outside_commands", [])
    events = inventory.get("required_event_types", [])
    aggregates = inventory.get("aggregate_dependencies", [])
    owners = inventory.get("owner_modules", [])
    expected_counts = {
        "required_commands_exact": len(commands),
        "outside_commands_exact": len(outside),
        "required_event_types_exact": len(events),
        "aggregate_state_reducer_families_exact": len(aggregates),
        "owner_modules_exact": len(owners),
    }
    for field, actual_length in expected_counts.items():
        if counts.get(field) != actual_length:
            errors.append(f"counts.{field} does not equal represented length {actual_length}")
    if counts.get("design_commands_exact") != len(commands) + len(outside):
        errors.append("design command count does not equal required plus outside partition")
    if set(commands) & set(outside):
        errors.append("required and outside command partitions overlap")
    if len(commands) != len(set(commands)) or len(outside) != len(set(outside)):
        errors.append("command partition contains duplicate members")
    if len(events) != len(set(events)):
        errors.append("required event set contains duplicate members")
    if counts.get("unresolved_c1_through_c8_choices") != 1:
        errors.append("counts.unresolved_c1_through_c8_choices is not exactly one")

    required_events = {
        "resource.usage_observed",
        "resource.reservation_settled",
        "claim.superseded",
        "dependency.invalidation_recorded",
        "run.validity_determined",
        "measurement.disposition_determined",
        "resource.reservation_claimed",
        "attempt.started",
        "verification.started",
        "work.lease_expired",
    }
    missing_events = required_events - set(events)
    if missing_events:
        errors.append(f"inventory lacks required resolution events: {sorted(missing_events)}")
    if "resource.observed" in events:
        errors.append("resource.observed remains in required resource truth vocabulary")

    conflict_map = {
        item.get("conflict_id"): item
        for item in inventory.get("resolved_conflicts", [])
        if isinstance(item, dict)
    }
    if set(conflict_map) != EXPECTED_CONFLICTS:
        errors.append("resolved_conflicts is not exactly C1 through C8")
    for conflict_id in sorted(EXPECTED_CONFLICTS - {"C5"}):
        if conflict_map.get(conflict_id, {}).get("disposition") != "resolved":
            errors.append(f"{conflict_id} is not marked resolved")
    if conflict_map.get("C5", {}).get("disposition") != "unresolved_blocking":
        errors.append("C5 is not marked unresolved_blocking")

    aggregate_pairs = [
        (item.get("aggregate_type"), item.get("reducer_family"))
        for item in aggregates
        if isinstance(item, dict)
    ]
    if aggregate_pairs.count(("verification", "Verification")) != 1:
        errors.append("inventory does not contain exactly one verification/Verification reducer binding")
    forbidden_axis_reducers = {"Reproducibility", "Replication", "Transport"}
    if forbidden_axis_reducers & {pair[1] for pair in aggregate_pairs}:
        errors.append("an internal verification axis appears as a canonical reducer family")

    authority = inventory.get("authority_model", {})
    law = authority.get("bounded_grant_law", {})
    required_law = {
        "distinct_grant_per_slot": True,
        "action_instance_bound": True,
        "single_use": True,
        "max_uses": 1,
        "consumption_point": "domain_commit",
        "used_set_equals_exhausted_set": True,
        "rejection_noop_or_replay_emits_new_use": False,
        "caller_may_select_authority_path": False,
    }
    for field, expected in required_law.items():
        if law.get(field) != expected:
            errors.append(f"authority_model.bounded_grant_law.{field} is not {expected!r}")

    cohorts = inventory.get("atomic_cohorts", {})
    cohort_requirements = {
        "resource_observation_final": {"resource.usage_observed", "resource.reservation_settled"},
        "claim_correction": {"claim.superseded", "dependency.invalidation_recorded"},
        "run_validity_measurement": {"run.validity_determined", "measurement.disposition_determined"},
        "attempt_start_local": {"resource.reservation_claimed", "attempt.started", "verification.started"},
        "verification_controlled_deadline_preclaim": {
            "verification.invalidated",
            "work.lease_expired",
            "resource.reservation_expired",
        },
    }
    for name, required_members in cohort_requirements.items():
        represented = set(cohorts.get(name, []))
        if not required_members <= represented:
            errors.append(f"atomic_cohorts.{name} lacks {sorted(required_members - represented)}")
    if cohorts.get("verification_assign_local") != VERIFICATION_ASSIGN_EVENTS:
        errors.append("atomic_cohorts.verification_assign_local is not the exact ordered 13-event cohort")

    unresolved = inventory.get("unresolved_prerequisites", [])
    if not isinstance(unresolved, list) or len(unresolved) != 1:
        errors.append("inventory does not expose exactly one unresolved prerequisite")
    else:
        prq = unresolved[0]
        if prq.get("prerequisite_id") != "PRQ-009" or prq.get("status") != "unresolved_blocking":
            errors.append("the sole unresolved prerequisite is not blocking PRQ-009")
        contract = prq.get("prospective_assignment_contract", {})
        if contract.get("command_type") != "verification.assign" or contract.get("path_id") != "local_assignment":
            errors.append("PRQ-009 does not bind verification.assign/local_assignment")
        if contract.get("role_slot_order") != VERIFICATION_ASSIGN_ROLES:
            errors.append("PRQ-009 role-slot order is not exact")
        if contract.get("batch_size_exact") != len(VERIFICATION_ASSIGN_EVENTS):
            errors.append("PRQ-009 exact batch size is not 13")
        if contract.get("event_order_exact") != VERIFICATION_ASSIGN_EVENTS:
            errors.append("PRQ-009 event order is not the exact assignment cohort")
        if prq.get("required_exact_bindings") != VERIFICATION_ASSIGN_BINDINGS:
            errors.append("PRQ-009 exact binding obligations drifted")
        blockers = prq.get("current_blockers", [])
        required_blocker_terms = ("unresolved_blocking", "null canonical digest", "one-event sample batch")
        joined_blockers = " ".join(blockers)
        for term in required_blocker_terms:
            if term not in joined_blockers:
                errors.append(f"PRQ-009 current blockers omit {term!r}")

    prerequisites = inventory.get("external_prerequisites", [])
    if len(prerequisites) != 1 or prerequisites[0].get("prerequisite_id") != EXPECTED_P0:
        errors.append("inventory does not expose exactly the nonrecursive P0 prerequisite")
    elif not prerequisites[0].get("not_a_command_event_grant_aggregate_or_policy_result"):
        errors.append("P0 lost its non-command/event/grant/aggregate/policy boundary")
    if prerequisites:
        required_bindings = prerequisites[0].get("required_bindings", [])
        expected_independent_binding = (
            "activation_independent_subject_excluding_activation_identity_sequence_reference_and_digest"
        )
        if expected_independent_binding not in required_bindings:
            errors.append("P0 required bindings do not explicitly exclude activation identity")
        if "registry_activation_identity_sequence_and_digest" in required_bindings:
            errors.append("P0 recursively requires its parent activation identity/digest")
        expected_outer_requirements = [
            "constructed_after_p0_seal",
            "embeds_exact_p0_subject",
            "binds_exact_p0_digest",
            "binds_activation_identity_sequence_and_digest_for_later_commands",
        ]
        if prerequisites[0].get("outer_registry_activation_requirements") != expected_outer_requirements:
            errors.append("outer RegistryActivation requirements do not bind the already-sealed P0")
    if prerequisites and prerequisites[0].get("current_instance_status") != "missing":
        errors.append("candidate inventory incorrectly claims a current P0 instance")

    refusal = inventory.get("refusal", {})
    for field in (
        "gate_a_complete",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
        "public_repository_authorized",
    ):
        if refusal.get(field) is not False:
            errors.append(f"refusal.{field} is not false")
    return errors


def resource_settlement_errors(subject: dict[str, Any], _: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reservation = subject.get("reservation", {})
    observation = subject.get("observation", {})
    non_money = reservation.get("non_money_dimensions", [])
    money = reservation.get("money_dimensions", [])
    if len(non_money) != len(set(non_money)) or len(money) != len(set(money)):
        errors.append("reservation dimensions are not unique")
    if set(non_money) & set(money):
        errors.append("money and non-money dimensions overlap")
    actual = observation.get("actual_usage", {})
    billed = observation.get("billed_money", {})
    refunded = observation.get("refunded_money", {})
    if not set(actual) <= set(non_money):
        errors.append("actual usage names an unreserved non-money dimension")
    if not set(billed) <= set(money) or not set(refunded) <= set(money):
        errors.append("billed/refunded evidence names an unreserved money dimension")
    for label, values in (("actual_usage", actual), ("billed_money", billed), ("refunded_money", refunded)):
        for dimension, value in values.items():
            if not exact_nonnegative_decimal(value):
                errors.append(f"{label}.{dimension} is not an exact nonnegative decimal string")
    if observation.get("inferred_zero_dimensions"):
        errors.append("an unmeasured resource dimension was inferred as zero")
    if not observation.get("usage_event"):
        errors.append("typed resource.usage_observed event is absent")
    final = observation.get("final")
    settled = observation.get("settlement_event")
    complete = (
        set(actual) == set(non_money)
        and set(billed) == set(money)
        and set(refunded) == set(money)
    )
    if final is True and settled is not True:
        errors.append("final exact observation is not settled in the same batch")
    if final is True and not complete:
        errors.append("final observation lacks the complete money/non-money profile")
    if final is False and settled is not False:
        errors.append("nonfinal observation carries a settlement event")
    if final is False and complete:
        errors.append("a complete profile was marked nonfinal instead of settling atomically")
    if final not in (True, False):
        errors.append("observation finality is not explicit")
    explicit_empty = observation.get("explicit_empty_money_domain")
    if money and explicit_empty is not False:
        errors.append("nonempty money domain is marked explicitly empty")
    if not money and explicit_empty is not True:
        errors.append("empty money domain is not explicit")
    for dimension in set(billed) & set(refunded):
        if exact_nonnegative_decimal(billed[dimension]) and exact_nonnegative_decimal(refunded[dimension]):
            if Decimal(refunded[dimension]) > Decimal(billed[dimension]):
                errors.append(f"refunded_money.{dimension} exceeds billed_money.{dimension}")
    return errors


def claim_correction_errors(subject: dict[str, Any], _: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if subject.get("command_type") != "claim.supersede":
        errors.append("claim correction is not produced by claim.supersede")
    if subject.get("producer_count") != 1:
        errors.append("claim correction does not have exactly one producer")
    if subject.get("atomic_commit") is not True:
        errors.append("claim correction is not one atomic commit")
    if subject.get("intermediate_visibility") is not False:
        errors.append("claim correction exposes an interior batch state")
    batches = subject.get("batches", [])
    flattened = [event for batch in batches for event in batch]
    for event in ("claim.superseded", "dependency.invalidation_recorded"):
        if flattened.count(event) != 1:
            errors.append(f"{event} does not occur exactly once")
    containing = [index for index, batch in enumerate(batches) if "claim.superseded" in batch or "dependency.invalidation_recorded" in batch]
    if len(set(containing)) != 1:
        errors.append("supersession and invalidation are split across batches")
    if "dependency.edges_registered" in flattened:
        errors.append("derived dependency edges were promoted to canonical facts")
    return errors


def validity_measurement_errors(subject: dict[str, Any], _: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if subject.get("command_type") != "run.determine_validity":
        errors.append("validity pair is not produced by run.determine_validity")
    if subject.get("producer_count") != 1:
        errors.append("validity pair does not have exactly one producer")
    if subject.get("atomic_commit") is not True:
        errors.append("validity and measurement facts are not one atomic commit")
    batches = subject.get("batches", [])
    flattened = [event for batch in batches for event in batch]
    required = ("run.validity_determined", "measurement.disposition_determined")
    for event in required:
        if flattened.count(event) != 1:
            errors.append(f"{event} does not occur exactly once")
    containing = [index for index, batch in enumerate(batches) if any(event in batch for event in required)]
    if len(set(containing)) != 1:
        errors.append("validity and measurement disposition are split across batches")
    legal_pairs = {
        ("valid", "valid_measurement"),
        ("valid", "no_valid_measurement"),
        ("invalid", "no_valid_measurement"),
    }
    pair = (subject.get("run_validity"), subject.get("measurement_disposition"))
    if pair not in legal_pairs:
        errors.append(f"illegal run-validity/measurement-disposition pair: {pair!r}")
    return errors


def command_path(inventory: dict[str, Any], command_type: str, path_id: str) -> dict[str, Any] | None:
    for profile in inventory.get("authority_model", {}).get("command_profiles", []):
        if profile.get("command_type") != command_type:
            continue
        for path in profile.get("paths", []):
            if path.get("path_id") == path_id:
                return path
    return None


def grant_cohort_errors(subject: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    command_type = subject.get("command_type")
    path_id = subject.get("path_id")
    path = command_path(inventory, command_type, path_id)
    if path is None:
        return [f"unknown authority path {command_type!r}/{path_id!r}"]
    if path.get("mode") != "bounded_grants":
        errors.append("case does not bind a bounded-grants path")
    expected_roles = path.get("role_slots", [])
    global_order = inventory.get("authority_model", {}).get("role_slot_order", [])
    if expected_roles != sorted(expected_roles, key=global_order.index):
        errors.append("inventory authority path is not in global role-slot order")
    grants = subject.get("grants", [])
    actual_roles = [grant.get("role") for grant in grants]
    if actual_roles != expected_roles:
        errors.append(f"grant roles {actual_roles!r} do not equal exact path roles {expected_roles!r}")
    grant_ids = [grant.get("grant_id") for grant in grants]
    if len(grant_ids) != len(set(grant_ids)):
        errors.append("grant slots do not bind distinct grants")
    action_id = subject.get("action_instance_id")
    for index, grant in enumerate(grants):
        if grant.get("action_instance_id") != action_id:
            errors.append(f"grant[{index}] is not bound to the exact action instance")
        if grant.get("max_uses") != 1 or grant.get("uses") != 1:
            errors.append(f"grant[{index}] is not single-use and exactly consumed")
    if subject.get("outcome") != "committed" or subject.get("domain_commit") is not True:
        errors.append("grant use is not attached to a successful domain commit")
    used = subject.get("used_roles", [])
    exhausted = subject.get("exhausted_roles", [])
    if used != expected_roles:
        errors.append("grant-used cohort is partial, extra, duplicated, or out of order")
    if exhausted != expected_roles:
        errors.append("grant-exhausted cohort is partial, extra, duplicated, or out of order")
    if used != exhausted:
        errors.append("grant-used and grant-exhausted cohorts differ")
    return errors


def local_preclaim_race_errors(subject: dict[str, Any], _: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    initial = subject.get("initial", {})
    lease = initial.get("lease")
    reservation = initial.get("reservation")
    if lease != "active" or reservation != "reserved":
        return ["race model must start with one active lease and one reserved, unclaimed hold"]
    attempt_started = False
    invalidated = False

    for index, step in enumerate(subject.get("steps", [])):
        action = step.get("action")
        fencing = step.get("fencing_evidence") is True
        if action == "start":
            if lease == "active" and reservation == "reserved" and not invalidated and not attempt_started:
                expected_outcome = "committed"
                expected_events = ["resource.reservation_claimed", "attempt.started", "verification.started"]
                reservation = "claimed"
                attempt_started = True
            else:
                expected_outcome = "rejected"
                expected_events = []
        elif action == "invalidate":
            if attempt_started and reservation == "claimed" and not invalidated:
                expected_outcome = "committed"
                expected_events = ["verification.invalidated"]
                if fencing:
                    expected_events.append("work.lease_revoked")
                    lease = "revoked"
                invalidated = True
            elif not attempt_started and lease == "active" and reservation == "reserved" and not invalidated:
                expected_outcome = "committed"
                expected_events = ["verification.invalidated", "work.lease_revoked", "resource.reservation_released"]
                lease = "revoked"
                reservation = "released"
                invalidated = True
            else:
                expected_outcome = "noop"
                expected_events = []
        elif action == "deadline":
            if not attempt_started and lease == "active" and reservation == "reserved" and not invalidated:
                expected_outcome = "committed"
                expected_events = ["verification.invalidated", "work.lease_expired", "resource.reservation_expired"]
                lease = "expired"
                reservation = "expired"
                invalidated = True
            else:
                expected_outcome = "noop"
                expected_events = []
        else:
            errors.append(f"steps[{index}] has unknown race action {action!r}")
            continue
        if step.get("outcome") != expected_outcome:
            errors.append(
                f"steps[{index}] outcome {step.get('outcome')!r} does not equal serialized result {expected_outcome!r}"
            )
        if step.get("events") != expected_events:
            errors.append(
                f"steps[{index}] events {step.get('events')!r} do not equal serialized cohort {expected_events!r}"
            )
    return errors


def verification_assign_obligation_errors(subject: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    """Check a prospective obligation, never a currently constructible event."""

    if subject.get("fixture") == "canonical_prospective_assignment_obligation":
        mutation = subject.get("mutation")
        subject = canonical_verification_assign_obligation()
        bindings = subject["binding_obligations"]
        if mutation == "missing_work_intent_binding":
            bindings["resolved_admitted_assignable_work_intent_exact"] = False
        elif mutation == "unresolved_null_work_intent_used_as_assignable":
            bindings["resolved_admitted_assignable_work_intent_exact"] = False
            subject["claims_current_constructibility"] = True
        elif mutation == "missing_active_lease":
            bindings["acquired_active_lease_exact"] = False
        elif mutation == "stale_or_incomplete_data_use_decisions":
            bindings["active_current_data_use_decisions_complete"] = False
        elif mutation == "missing_zero_external_capability_sandbox":
            bindings["zero_external_capability_sandbox_and_policy_exact"] = False
        elif mutation == "batch_size_one":
            subject["batch_size"] = 1
            subject["event_order"] = ["verification.assigned"]
        elif mutation == "split_cohort":
            subject["event_order"] = [
                VERIFICATION_ASSIGN_EVENTS[:8],
                VERIFICATION_ASSIGN_EVENTS[8:],
            ]
        elif mutation == "wrong_event_order":
            subject["event_order"][5], subject["event_order"][6] = (
                subject["event_order"][6],
                subject["event_order"][5],
            )
        elif mutation == "partial_grant_cohort":
            subject["event_order"] = [
                event
                for event in subject["event_order"]
                if event not in {"authority.grant_used(data_rights)", "authority.grant_exhausted(data_rights)"}
            ]
            subject["batch_size"] = len(subject["event_order"])
        else:
            return [f"unknown canonical assignment mutation {mutation!r}"]

    errors: list[str] = []
    if subject.get("prospective_only") is not True:
        errors.append("assignment obligation is not explicitly prospective-only")
    if subject.get("claims_current_constructibility") is not False:
        errors.append("assignment obligation claims current constructibility")
    if subject.get("claims_current_admission") is not False:
        errors.append("assignment obligation claims current admission")
    if subject.get("command_type") != "verification.assign" or subject.get("path_id") != "local_assignment":
        errors.append("assignment obligation does not bind verification.assign/local_assignment")
    if subject.get("role_slot_order") != VERIFICATION_ASSIGN_ROLES:
        errors.append("assignment role slots are missing, extra, duplicated, or out of order")
    events = subject.get("event_order", [])
    if subject.get("batch_size") != len(VERIFICATION_ASSIGN_EVENTS):
        errors.append("assignment batch size is not exactly 13")
    if events != VERIFICATION_ASSIGN_EVENTS:
        errors.append("assignment events are missing, extra, split, duplicated, or out of order")
    if subject.get("atomic_commit") is not True or subject.get("intermediate_visibility") is not False:
        errors.append("assignment cohort is not one atomic commit without interior visibility")
    bindings = subject.get("binding_obligations", {})
    required_true = (
        "resolved_admitted_assignable_work_intent_exact",
        "work_contract_binds_work_intent_and_assignment_commit",
        "active_current_data_use_decisions_complete",
        "zero_external_capability_sandbox_and_policy_exact",
        "created_reservation_exact",
        "acquired_active_lease_exact",
        "five_distinct_single_use_action_bound_grants_exact",
        "command_receipt_activation_commit_equalities_exact",
    )
    for field in required_true:
        if bindings.get(field) is not True:
            errors.append(f"assignment binding obligation {field} is not true")
    if set(bindings) != set(required_true):
        errors.append("assignment binding obligation set is not closed and exact")
    unresolved = inventory.get("unresolved_prerequisites", [])
    if len(unresolved) != 1 or unresolved[0].get("prerequisite_id") != "PRQ-009":
        errors.append("assignment obligation is not anchored to blocking PRQ-009")
    elif unresolved[0].get("prospective_assignment_contract", {}).get("event_order_exact") != events:
        errors.append("assignment obligation event order disagrees with PRQ-009")
    return errors


def canonical_verification_assign_obligation() -> dict[str, Any]:
    return {
        "prospective_only": True,
        "claims_current_constructibility": False,
        "claims_current_admission": False,
        "command_type": "verification.assign",
        "path_id": "local_assignment",
        "role_slot_order": deepcopy(VERIFICATION_ASSIGN_ROLES),
        "batch_size": len(VERIFICATION_ASSIGN_EVENTS),
        "event_order": deepcopy(VERIFICATION_ASSIGN_EVENTS),
        "atomic_commit": True,
        "intermediate_visibility": False,
        "binding_obligations": {
            "resolved_admitted_assignable_work_intent_exact": True,
            "work_contract_binds_work_intent_and_assignment_commit": True,
            "active_current_data_use_decisions_complete": True,
            "zero_external_capability_sandbox_and_policy_exact": True,
            "created_reservation_exact": True,
            "acquired_active_lease_exact": True,
            "five_distinct_single_use_action_bound_grants_exact": True,
            "command_receipt_activation_commit_equalities_exact": True,
        },
    }


def verification_reducer_errors(subject: dict[str, Any], inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = [{"aggregate_type": "verification", "reducer_family": "Verification"}]
    if subject.get("canonical_reducers") != expected:
        errors.append("Verification is not the sole canonical reducer authority")
    if subject.get("internal_axes") != EXPECTED_AXES:
        errors.append("verification fold axes are not the exact orthogonal axis set")
    if subject.get("axes_are_internal") is not True:
        errors.append("a verification axis is represented as an independent reducer authority")
    inventory_reducers = [
        item
        for item in inventory.get("aggregate_dependencies", [])
        if item.get("aggregate_type") == "verification"
    ]
    if len(inventory_reducers) != 1 or inventory_reducers[0].get("reducer_family") != "Verification":
        errors.append("inventory verification reducer binding disagrees with C7")
    return errors


def p0_frontier_errors(subject: dict[str, Any], _: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_true = (
        "root_authority_non_self_issued",
        "exact_engine_contract_root_bound",
        "exact_c0_registry_bundle_bound",
        "witnessed_checkpoint",
        "controlled_time_current",
        "bounded_scope",
    )
    if subject.get("prerequisite_id") != EXPECTED_P0:
        errors.append("P0 prerequisite identity does not match the candidate")
    for field in required_true:
        if subject.get(field) is not True:
            errors.append(f"P0 {field} is not proven true")
    expected_boundary = {
        "activation_reference_permitted": False,
        "activation_identity_included": False,
        "activation_sequence_included": False,
        "parent_activation_digest_included": False,
        "outer_activation_must_bind_exact_p0_digest": True,
    }
    if subject.get("nonrecursive_boundary") != expected_boundary:
        errors.append("P0 is not exactly activation-independent")
    frontier = subject.get("recovery_frontier", {})
    for field in ("current", "ledger_epoch_matches", "root_matches"):
        if frontier.get(field) is not True:
            errors.append(f"recovery frontier {field} is not true")
    if frontier.get("unresolved_fork_count") != 0:
        errors.append("recovery frontier contains an unresolved fork")
    if frontier.get("quarantined") is not False:
        errors.append("recovery frontier is quarantined")
    if frontier.get("open_recovery_case_count") != 0:
        errors.append("recovery frontier contains an open recovery case")
    if frontier.get("ambiguous") is not False:
        errors.append("recovery frontier is ambiguous")
    outer_activation = subject.get("outer_activation_binding", {})
    if outer_activation.get("exact_p0_digest_bound") is not True:
        errors.append("outer activation does not bind the exact sealed P0 digest")
    if outer_activation.get("expired") is not False:
        errors.append("outer activation is expired")
    if outer_activation.get("superseded") is not False:
        errors.append("outer activation is superseded")
    return errors


CHECKERS: dict[str, Callable[[dict[str, Any], dict[str, Any]], list[str]]] = {
    "resource_settlement": resource_settlement_errors,
    "claim_correction": claim_correction_errors,
    "validity_measurement": validity_measurement_errors,
    "grant_cohort": grant_cohort_errors,
    "local_preclaim_race": local_preclaim_race_errors,
    "verification_assign_obligation": verification_assign_obligation_errors,
    "verification_reducer_authority": verification_reducer_errors,
    "p0_frontier": p0_frontier_errors,
}


def main() -> int:
    manifest = load_json(CASES_PATH)
    inventory_path = ROOT / manifest["inventory"]
    inventory = load_json(inventory_path)
    failures: list[str] = []

    inv_errors = inventory_errors(inventory)
    if inv_errors:
        failures.extend(f"inventory: {error}" for error in inv_errors)

    cases = manifest.get("cases", [])
    names = [case.get("name") for case in cases]
    if len(names) != len(set(names)):
        failures.append("case names are not unique")

    required_tags = set(manifest.get("required_adversarial_tags", []))
    actual_tags = {
        case.get("adversarial_tag")
        for case in cases
        if case.get("kind") == "adversarial"
    }
    missing_tags = required_tags - actual_tags
    if missing_tags:
        failures.append(f"missing required adversarial tags: {sorted(missing_tags)}")

    covered_conflicts: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    accepted_safe = 0
    rejected_adversarial = 0
    for case in cases:
        name = case.get("name", "<unnamed>")
        conflict_ids = set(case.get("conflict_ids", []))
        if not conflict_ids or not conflict_ids <= EXPECTED_CONFLICTS:
            failures.append(f"{name}: conflict_ids are missing or outside C1-C8")
        covered_conflicts.update(conflict_ids)
        kind = case.get("kind")
        expected = case.get("expect")
        if kind == "safe_reference":
            safe_count += 1
            if expected != "accept":
                failures.append(f"{name}: safe reference does not expect acceptance")
        elif kind == "adversarial":
            adversarial_count += 1
            if expected != "reject":
                failures.append(f"{name}: adversarial case does not expect rejection")
            if case.get("adversarial_tag") not in required_tags:
                failures.append(f"{name}: adversarial tag is not declared required")
        else:
            failures.append(f"{name}: unknown case kind {kind!r}")

        checker = CHECKERS.get(case.get("model"))
        if checker is None:
            failures.append(f"{name}: unknown model {case.get('model')!r}")
            continue
        subject = case.get("subject")
        if not isinstance(subject, dict):
            failures.append(f"{name}: subject is not an object")
            continue
        errors = checker(subject, inventory)
        actual = "reject" if errors else "accept"
        if kind == "safe_reference" and actual == "accept":
            accepted_safe += 1
        if kind == "adversarial" and actual == "reject":
            rejected_adversarial += 1
        if actual != expected:
            detail = "; ".join(errors) if errors else "no invariant violation detected"
            if kind == "adversarial" and actual == "accept":
                failures.append(f"KNOWN-BAD CASE ACCEPTED: {name}: {detail}")
            else:
                failures.append(f"{name}: expected {expected}, got {actual}: {detail}")

    if covered_conflicts != EXPECTED_CONFLICTS:
        failures.append(f"case coverage is not exactly C1-C8; covered {sorted(covered_conflicts)}")
    if not safe_count or not adversarial_count:
        failures.append("suite requires both safe references and adversarial cases")

    if failures:
        print("first-slice resolution adversarial check FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("first-slice resolution adversarial check passed")
    print(f"inventory: {manifest['inventory']}")
    print(f"inventory deterministic JSON digest (non-normative): {stable_json_digest(inventory)}")
    print(f"cases deterministic JSON digest (non-normative): {stable_json_digest(manifest)}")
    print(f"safe references accepted: {accepted_safe}/{safe_count}")
    print(f"known-bad cases rejected: {rejected_adversarial}/{adversarial_count}")
    print(f"conflicts covered: {','.join(sorted(covered_conflicts))}")
    print("boundary: architecture-only; no registry admission, activation, Gate A acceptance, or runtime authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
