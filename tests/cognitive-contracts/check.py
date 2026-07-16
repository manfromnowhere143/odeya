#!/usr/bin/env python3
"""Run isolated structural checks for proposed cognitive-control records."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "tests/cognitive-contracts/cases.json"


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutated_copy(instance: object, mutations: list[dict[str, object]]) -> object:
    result = json.loads(json.dumps(instance))
    for mutation in mutations:
        operation = mutation["op"]
        path = tokens(str(mutation["path"]))
        parent = result
        for part in path[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        final = path[-1]
        if isinstance(parent, list):
            position = int(final)
            if operation == "add":
                parent.insert(position, mutation.get("value"))
            elif operation == "remove":
                del parent[position]
            elif operation == "replace":
                parent[position] = mutation["value"]
            else:
                raise ValueError(f"unsupported operation: {operation!r}")
        elif isinstance(parent, dict):
            if operation == "add":
                if final in parent:
                    raise ValueError(f"add target exists: {final!r}")
                parent[final] = mutation.get("value")
            elif operation == "remove":
                del parent[final]
            elif operation == "replace":
                if final not in parent:
                    raise KeyError(final)
                parent[final] = mutation["value"]
            else:
                raise ValueError(f"unsupported operation: {operation!r}")
        else:
            raise TypeError("mutation parent is not a container")
    return result


def ref_key(ref: object) -> tuple[object, ...]:
    if not isinstance(ref, dict):
        return (None,)
    if "digest" in ref:
        return (ref.get("id"), ref.get("version"), ref.get("digest"))
    return (ref.get("artifact_id"), ref.get("digest"), ref.get("media_type"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def check_estimate(estimate: object, path: str, errors: list[str]) -> None:
    if not isinstance(estimate, dict):
        return
    lower = estimate.get("lower")
    point = estimate.get("point")
    upper = estimate.get("upper")
    if all(isinstance(value, str) for value in (lower, point, upper)):
        try:
            lower_decimal, point_decimal, upper_decimal = (
                Decimal(value) for value in (lower, point, upper)
            )
        except InvalidOperation:
            errors.append(f"{path}: exact-decimal string could not be parsed")
            return
        if not lower_decimal <= point_decimal <= upper_decimal:
            errors.append(f"{path}: expected lower <= point <= upper")


def model_configuration_semantics(instance: dict[str, object]) -> list[str]:
    errors: list[str] = []

    generation_parameters = instance["invocation_configuration"]["generation_parameters"]
    parameter_names = [item["name"] for item in generation_parameters]
    if len(parameter_names) != len(set(parameter_names)):
        errors.append("invocation_configuration.generation_parameters: duplicate parameter name")

    metric_observations = instance["evaluation_evidence"]["metric_observations"]
    for index, observation in enumerate(metric_observations):
        check_estimate(observation.get("estimate"), f"evaluation_evidence.metric_observations[{index}].estimate", errors)

    curve_dimensions: list[str] = []
    for curve_index, curve in enumerate(instance["operational_observations"]):
        curve_dimensions.append(curve["dimension"])
        for point_index, point in enumerate(curve["points"]):
            check_estimate(point.get("estimate"), f"operational_observations[{curve_index}].points[{point_index}].estimate", errors)
    if len(curve_dimensions) != len(set(curve_dimensions)):
        errors.append("operational_observations: duplicate dimension")

    capability_keys = [
        (ref_key(item["task_family_ref"]), item["role"], tuple(item["modalities"]))
        for item in instance["capability_evidence"]
    ]
    if len(capability_keys) != len(set(capability_keys)):
        errors.append("capability_evidence: duplicate task/role/modality identity")

    capability_tasks = {ref_key(item["task_family_ref"]) for item in instance["capability_evidence"]}
    intended_tasks = {ref_key(item) for item in instance["eligibility_boundary"]["intended_task_family_refs"]}
    if not intended_tasks.issubset(capability_tasks):
        errors.append("eligibility_boundary: intended task lacks capability evidence")

    evaluation_task = ref_key(instance["evaluation_evidence"]["task_family_ref"])
    if instance["evaluation_evidence"]["disposition"] == "evaluated" and evaluation_task not in intended_tasks:
        errors.append("evaluation_evidence: evaluated task is outside intended task family set")

    permitted = set(instance["data_handling"]["permitted_data_classes"])
    disallowed = set(instance["limitations"]["disallowed_data_classes"])
    overlap = permitted & disallowed
    if overlap:
        errors.append(f"data class simultaneously permitted and disallowed: {sorted(overlap)}")

    validity = instance["validity"]
    valid_from = parse_time(validity["valid_from"])
    expires_at = parse_time(validity["expires_at"])
    observed_at = parse_time(instance["recorded_at"]["value"])
    if not valid_from < expires_at:
        errors.append("validity: valid_from must precede expires_at")
    disposition = validity["disposition"]
    if disposition == "current_at_observation" and not valid_from <= observed_at < expires_at:
        errors.append("validity: current disposition contradicts controlled observation time")
    if disposition == "expired" and observed_at < expires_at:
        errors.append("validity: expired disposition contradicts controlled observation time")
    if disposition == "not_yet_valid" and observed_at >= valid_from:
        errors.append("validity: not-yet-valid disposition contradicts controlled observation time")

    return errors


CONSTRAINT_RULE_FIELDS = {
    "task_family": "task_family_rule_ref",
    "capability": "capability_rule_ref",
    "modality": "modality_rule_ref",
    "data_governance": "data_governance_rule_ref",
    "residency": "residency_rule_ref",
    "retention": "retention_rule_ref",
    "risk": "risk_rule_ref",
    "evaluation_validity": "evaluation_validity_rule_ref",
    "budget": "budget_rule_ref",
    "latency": "latency_rule_ref",
    "correlation": "correlation_rule_ref",
}


def routing_decision_semantics(instance: dict[str, object]) -> list[str]:
    errors: list[str] = []
    search = instance["candidate_search"]
    candidates = instance["candidate_set"]
    if search["considered_count"] != len(candidates):
        errors.append("candidate_search: considered_count does not equal candidate_set length")
    if search["partition_complete"] and search["registry_member_count"] != len(candidates):
        errors.append("candidate_search: complete partition does not cover every registry member")
    if not search["partition_complete"] and search["registry_member_count"] != len(candidates) + len(search["omitted_candidate_refs"]):
        errors.append("candidate_search: incomplete partition counts do not reconcile")

    candidate_keys = [ref_key(candidate["configuration_ref"]) for candidate in candidates]
    if len(candidate_keys) != len(set(candidate_keys)):
        errors.append("candidate_set: duplicate configuration identity")

    hard_constraints = instance["hard_constraints"]
    selected_candidates: list[dict[str, object]] = []
    for candidate_index, candidate in enumerate(candidates):
        if candidate["selection_disposition"] == "selected":
            selected_candidates.append(candidate)
        for result in candidate["constraint_results"]:
            expected_ref = hard_constraints[CONSTRAINT_RULE_FIELDS[result["constraint"]]]
            if ref_key(result["rule_ref"]) != ref_key(expected_ref):
                errors.append(
                    f"candidate_set[{candidate_index}].constraint_results[{result['constraint']}]: rule reference mismatch"
                )
        for dimension_index, observation in enumerate(candidate["dimension_observations"]):
            lower = observation["lower_bound"]
            upper = observation["upper_bound"]
            if observation["disposition"] == "bounded":
                try:
                    reversed_bounds = Decimal(lower) > Decimal(upper)
                except (InvalidOperation, TypeError):
                    errors.append(
                        f"candidate_set[{candidate_index}].dimension_observations[{dimension_index}]: exact-decimal bound could not be parsed"
                    )
                    continue
                if reversed_bounds:
                    errors.append(
                        f"candidate_set[{candidate_index}].dimension_observations[{dimension_index}]: lower bound exceeds upper bound"
                    )

    decision = instance["decision"]
    if decision["result"] == "selected":
        if len(selected_candidates) != 1:
            errors.append("decision: selected result requires exactly one selected candidate")
        elif ref_key(decision["selected_configuration_ref"]) != ref_key(selected_candidates[0]["configuration_ref"]):
            errors.append("decision: selected reference does not equal selected candidate")
        if selected_candidates and any(
            item["disposition"] == "unknown" for item in selected_candidates[0]["dimension_observations"]
        ):
            errors.append("decision: selected candidate contains an unknown decision dimension")
    elif selected_candidates:
        errors.append("decision: non-selection result contains a selected candidate")

    eligible_count = sum(candidate["eligibility_disposition"] == "eligible" for candidate in candidates)
    if decision["result"] == "no_eligible_candidate" and eligible_count:
        errors.append("decision: no-eligible result contradicts eligible candidate")
    if decision["result"] == "no_candidate_discovered" and candidates:
        errors.append("decision: no-candidate result contradicts nonempty candidate set")
    if decision["result"] == "policy_refusal" and instance["policy_binding"]["result"] != "deny":
        errors.append("decision: policy-refusal result lacks deny policy result")

    fallback_keys = {ref_key(ref) for ref in instance["fallback"]["candidate_configuration_refs"]}
    if decision["result"] == "selected" and ref_key(decision["selected_configuration_ref"]) in fallback_keys:
        errors.append("fallback: selected configuration cannot be its own fallback")

    return errors


def work_intent_semantics(instance: dict[str, object]) -> list[str]:
    """Check the bounded prospective/assignment split without resolving state.

    These checks deliberately inspect only values inside one WorkIntent. They
    do not prove that a later assignment, lease, reservation, or dispatch
    exists. In particular, nonzero planning estimates remain estimates and are
    permitted only when the candidate boundary declares a future governed
    external-processing mode.
    """

    errors: list[str] = []
    if instance["identity_resolution_status"] != "unresolved_blocking":
        errors.append("identity_resolution_status: candidate must remain unresolved and blocking")
    if instance["canonicalization_profile_ref"] is not None or instance["canonical_digest"] is not None:
        errors.append("identity: unresolved WorkIntent cannot assert a profile or canonical digest")
    if instance["record_authority_status"] != "not_admitted_not_assignable":
        errors.append("record_authority_status: unresolved WorkIntent cannot be assignable")

    set_like_arrays = (
        ("permitted_deliverable_classes", instance["permitted_deliverable_classes"]),
        (
            "candidate_worker_requirements.capability_classes",
            instance["candidate_worker_requirements"]["capability_classes"],
        ),
        (
            "candidate_worker_requirements.execution_modes",
            instance["candidate_worker_requirements"]["execution_modes"],
        ),
        ("data_boundary.maximum_data_classes", instance["data_boundary"]["maximum_data_classes"]),
        ("data_boundary.allowed_residencies", instance["data_boundary"]["allowed_residencies"]),
    )
    for path, values in set_like_arrays:
        if values != sorted(values):
            errors.append(f"{path}: must use Unicode-codepoint ascending canonical order")

    authority = instance["prospective_authority_boundary"]
    forbidden_truthy_fields = (
        "active_lease_required_at_intent",
        "dispatch_authority_granted",
        "materialization_authority_granted",
        "external_effect_authority_granted",
        "bytes_may_cross_at_intent",
        "provider_spend_may_incur_at_intent",
    )
    for field in forbidden_truthy_fields:
        if authority[field] is not False:
            errors.append(f"prospective_authority_boundary.{field}: intent cannot confer authority")
    for field in ("active_lease_ref", "resource_reservation_ref", "dispatch_admission_ref"):
        if authority[field] is not None:
            errors.append(f"prospective_authority_boundary.{field}: intent cannot bind current authority")
    if authority["authority_grant_refs"]:
        errors.append("prospective_authority_boundary.authority_grant_refs: intent cannot bind grants")
    if authority["resource_reservation_required_at_intent"] is not False:
        errors.append("prospective_authority_boundary: intent cannot require an active reservation")

    assignment = instance["assignment_boundary"]
    expected_prerequisites = [
        "work_intent_canonical_identity",
        "worker_principal",
        "active_work_lease",
        "authority_grants",
        "active_data_use_decisions",
        "sandbox_capability",
        "resource_reservation",
        "passing_state_compilation_bundle",
    ]
    if assignment["prerequisites_to_resolve_at_assignment"] != expected_prerequisites:
        errors.append("assignment_boundary: current facts must be resolved only by verification.assign")
    if assignment["work_contract_materialization"] != "post_assignment_commit_derived":
        errors.append("assignment_boundary: WorkContract must be derived after assignment commit")

    estimates = instance["estimated_limits"]
    worker_modes = set(instance["candidate_worker_requirements"]["execution_modes"])
    maximum_egress = instance["data_boundary"]["maximum_egress"]
    anticipates_external_use = (
        estimates["network_egress_bytes"] > 0 or estimates["spend_minor_units"] > 0
    )
    if anticipates_external_use and (
        "governed_external_processing" not in worker_modes or maximum_egress == "none"
    ):
        errors.append(
            "estimated_limits: nonzero network/spend estimate requires a future governed external boundary"
        )

    return errors


def semantic_errors(schema_path: str, instance: object) -> list[str]:
    if not isinstance(instance, dict):
        return ["semantic subject must be an object"]
    if schema_path == "schemas/model-configuration-record.schema.json":
        return model_configuration_semantics(instance)
    if schema_path == "schemas/routing-decision.schema.json":
        return routing_decision_semantics(instance)
    if schema_path == "schemas/work-intent.schema.json":
        return work_intent_semantics(instance)
    return [f"no semantic checker registered for {schema_path}"]


def main() -> int:
    manifest = load(MANIFEST)
    failures: list[str] = []
    semantic_case_count = 0
    for case in manifest["cases"]:
        schema = load(ROOT / case["schema"])
        Draft202012Validator.check_schema(schema)
        try:
            instance = mutated_copy(load(ROOT / case["fixture"]), case.get("mutations", []))
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            failures.append(
                f"{case.get('name', '<unnamed-case>')}: mutation application failed: "
                f"{type(exc).__name__}: {exc}"
            )
            continue
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance))
        actual = "invalid" if errors else "valid"
        if actual != case["expect"]:
            detail = errors[0].message if errors else "mutation was unexpectedly accepted"
            failures.append(f"{case['name']}: expected {case['expect']}, got {actual}: {detail}")
            continue
        if "semantic_expect" in case:
            semantic_case_count += 1
            if errors:
                failures.append(f"{case['name']}: semantic check requires a structurally valid subject")
                continue
            semantic_failures = semantic_errors(str(case["schema"]), instance)
            semantic_actual = "invalid" if semantic_failures else "valid"
            if semantic_actual != case["semantic_expect"]:
                detail = semantic_failures[0] if semantic_failures else "semantic mutation was unexpectedly accepted"
                failures.append(
                    f"{case['name']}: expected semantic {case['semantic_expect']}, "
                    f"got {semantic_actual}: {detail}"
                )

    if failures:
        print("Cognitive contract schema cases failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Cognitive contract schema cases passed: {len(manifest['cases'])} "
        f"({semantic_case_count} include bounded local semantic checks; "
        "no authority or Gate A acceptance)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
