#!/usr/bin/env python3
"""Run isolated structural and bounded semantic checks for mathematical contracts."""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests/mathematical-contracts/cases.json"
FIXED_UTC_MICROSECOND = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"
)

AFFIRMATIVE_PREDICATE = {
    "estimate_reported": "descriptive_estimate_within_scope",
    "association_supported": "association_within_scope",
    "predictive_performance_supported": "predictive_performance_within_scope",
    "causal_effect_supported": "causal_effect_within_scope",
    "equivalent": "equivalence_within_margin",
    "noninferior": "noninferiority_within_margin",
    "safe_under_scope": "safety_bound_within_scope",
    "optimization_supported": "optimization_within_constraints",
    "physically_validated_under_scope": "physical_validation_within_scope",
}

NEGATIVE_OUTCOMES = {
    "association_not_supported", "predictive_performance_not_supported",
    "causal_effect_not_supported", "not_equivalent", "not_noninferior",
    "safety_bound_exceeded", "optimization_not_supported",
    "physical_validation_failed", "inconclusive", "invalid", "incomplete",
    "indeterminate", "blocked",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [item.replace("~1", "/").replace("~0", "~") for item in pointer[1:].split("/")]


def mutate(instance: Any, changes: list[dict[str, Any]]) -> Any:
    result = deepcopy(instance)
    for change in changes:
        operation = change["op"]
        path = pointer_tokens(change["path"])
        parent = result
        for token in path[:-1]:
            parent = parent[int(token)] if isinstance(parent, list) else parent[token]
        token = path[-1]
        if isinstance(parent, list):
            index = len(parent) if token == "-" else int(token)
            if operation == "add":
                parent.insert(index, deepcopy(change.get("value")))
            elif operation == "replace":
                parent[index] = deepcopy(change["value"])
            elif operation == "remove":
                del parent[index]
            else:
                raise ValueError(f"unsupported mutation operation {operation!r}")
        elif isinstance(parent, dict):
            if operation == "add":
                if token in parent:
                    raise ValueError(f"add target already exists: {change['path']}")
                parent[token] = deepcopy(change.get("value"))
            elif operation == "replace":
                if token not in parent:
                    raise KeyError(change["path"])
                parent[token] = deepcopy(change["value"])
            elif operation == "remove":
                del parent[token]
            else:
                raise ValueError(f"unsupported mutation operation {operation!r}")
        else:
            raise TypeError(f"mutation parent is not a container at {change['path']}")
    return result


def decimal(value: Any, path: str, errors: list[str]) -> Decimal | None:
    if not isinstance(value, str):
        errors.append(f"{path}: exact decimal must be a string")
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        errors.append(f"{path}: invalid exact decimal")
        return None


def quantity_value(quantity: Any, path: str, errors: list[str]) -> Decimal | None:
    if not isinstance(quantity, dict):
        errors.append(f"{path}: quantity missing")
        return None
    return decimal(quantity.get("value"), f"{path}.value", errors)


def quantity_unit(quantity: Any) -> Any:
    if not isinstance(quantity, dict):
        return None
    return quantity.get("unit_ref", quantity.get("unit"))


def same_quantity_unit(left: Any, right: Any) -> bool:
    return quantity_unit(left) == quantity_unit(right)


def artifact_key(reference: Any) -> tuple[Any, ...]:
    if not isinstance(reference, dict):
        return (None,)
    return (reference.get("artifact_id"), reference.get("digest"), reference.get("media_type"))


def fixed_timestamp_errors(instance: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(instance, dict):
        for key, value in instance.items():
            child = f"{path}.{key}"
            if isinstance(value, str) and (key.endswith("_at") or key == "cutoff_at"):
                if not FIXED_UTC_MICROSECOND.fullmatch(value):
                    errors.append(f"{child}: timestamp must be fixed UTC with six fractional digits")
                else:
                    try:
                        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        errors.append(f"{child}: timestamp is lexically profiled but not a calendar-valid instant")
            errors.extend(fixed_timestamp_errors(value, child))
    elif isinstance(instance, list):
        for index, value in enumerate(instance):
            errors.extend(fixed_timestamp_errors(value, f"{path}[{index}]"))
    return errors


def estimand_semantics(instance: dict[str, Any]) -> list[str]:
    errors = fixed_timestamp_errors(instance)
    if instance["mission_id"] != instance["mission_spec_ref"]["mission_id"]:
        errors.append("mission_spec_ref: mission identity mismatch")
    if instance["claim_type"] != instance["claim_contract"]["branch_type"]:
        errors.append("claim_contract: branch_type does not equal claim_type")

    horizon = quantity_value(instance["time"]["horizon"], "time.horizon", errors)
    if horizon is not None and horizon <= 0:
        errors.append("time.horizon: must be strictly positive")

    outcome_unit = instance["outcome"].get("unit_ref")
    scale_unit = instance["effect_scale"].get("unit_ref")
    if outcome_unit is not None and outcome_unit != scale_unit:
        errors.append("effect_scale.unit_ref: must equal outcome.unit_ref")

    reference = instance["contrast"].get("reference_value")
    null_reference = instance["decision_rule"].get("null_or_reference_value")
    for name, value in (("contrast.reference_value", reference), ("decision_rule.null_or_reference_value", null_reference)):
        if value is not None and quantity_unit(value) != scale_unit:
            errors.append(f"{name}: unit does not equal effect scale unit")

    partitions = instance["data_role_plan"]["partitions"]
    keys = [artifact_key(item["manifest_ref"]) for item in partitions]
    if len(keys) != len(set(keys)):
        errors.append("data_role_plan.partitions: one manifest cannot occupy multiple data roles")

    claim_type = instance["claim_type"]
    contract = instance["claim_contract"]
    if claim_type == "equivalence":
        lower = quantity_value(contract["lower_margin"], "claim_contract.lower_margin", errors)
        upper = quantity_value(contract["upper_margin"], "claim_contract.upper_margin", errors)
        ref = quantity_value(reference, "contrast.reference_value", errors)
        if not same_quantity_unit(contract["lower_margin"], contract["upper_margin"]):
            errors.append("claim_contract: equivalence margins have incompatible units")
        if not same_quantity_unit(contract["lower_margin"], reference):
            errors.append("claim_contract: equivalence margin and reference units differ")
        if None not in (lower, ref, upper) and not lower < ref < upper:
            errors.append("claim_contract: equivalence requires lower margin < reference < upper margin")
    elif claim_type == "noninferiority":
        margin = quantity_value(contract["margin"], "claim_contract.margin", errors)
        if margin is not None and margin <= 0:
            errors.append("claim_contract.margin: noninferiority margin must be strictly positive")
        if not same_quantity_unit(contract["margin"], reference):
            errors.append("claim_contract: noninferiority margin and reference units differ")
    elif claim_type == "physical_validation":
        if not contract["physical_world_measurement_required"]:
            errors.append("physical validation must require physical-world measurement")
        for field in ("simulation_sufficient", "calibration_sufficient", "code_verification_sufficient"):
            if contract[field]:
                errors.append(f"claim_contract.{field}: non-physical evidence cannot substitute")

    return errors


def protocol_semantics(instance: dict[str, Any]) -> list[str]:
    errors = fixed_timestamp_errors(instance)
    if instance["mission_id"] != instance["mission_spec"]["mission_id"]:
        errors.append("mission_spec: mission identity mismatch")
    binding = instance.get("mathematical_contract")
    if binding:
        ref = binding["estimand_contract_ref"]
        if instance["mission_id"] != ref["mission_id"]:
            errors.append("mathematical_contract.estimand_contract_ref: mission mismatch")
        if binding["claim_type"] != ref["claim_type"]:
            errors.append("mathematical_contract: claim_type mismatch")
    return errors


def metric_semantics(instance: dict[str, Any]) -> list[str]:
    errors = fixed_timestamp_errors(instance)
    binding = instance.get("mathematical_binding")
    if binding:
        ref = binding["estimand_contract_ref"]
        if instance["mission_id"] != ref["mission_id"]:
            errors.append("mathematical_binding.estimand_contract_ref: mission mismatch")
        if binding["claim_type"] != ref["claim_type"]:
            errors.append("mathematical_binding: claim_type mismatch")
        nonphysical = {"simulation", "synthetic_fixture", "calibration_data", "code_verification"}
        if binding["evidence_origin"] in nonphysical and binding["physical_validation_eligible"]:
            errors.append("mathematical_binding: non-physical evidence marked physical-validation eligible")
    if instance["measurement"]["status"] != "measured" and instance["measurement"]["estimate"] is not None:
        errors.append("measurement: unknown/missing status cannot carry a numeric estimate")
    return errors


def identity_chain_errors(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    chain = instance["identity_chain"]
    mission_id = instance["mission_id"]
    mission_refs = [
        chain["mission_spec_ref"], chain["estimand_contract_ref"],
        chain["protocol_snapshot_ref"], chain["run_manifest_ref"],
        *chain["metric_result_refs"],
    ]
    if any(ref["mission_id"] != mission_id for ref in mission_refs):
        errors.append("identity_chain: every record must bind the same mission_id")

    estimand = chain["estimand_contract_ref"]
    protocol = chain["protocol_snapshot_ref"]
    run = chain["run_manifest_ref"]
    if estimand["claim_type"] != instance["claim_type"]:
        errors.append("identity_chain.estimand_contract_ref: claim_type mismatch")
    if protocol["bound_estimand_id"] != estimand["estimand_id"] or protocol["bound_estimand_digest"] != estimand["digest"]:
        errors.append("identity_chain.protocol_snapshot_ref: estimand binding mismatch")
    if run["protocol_snapshot_id"] != protocol["protocol_snapshot_id"] or run["protocol_snapshot_digest"] != protocol["digest"]:
        errors.append("identity_chain.run_manifest_ref: protocol binding mismatch")
    for index, metric in enumerate(chain["metric_result_refs"]):
        if metric["protocol_snapshot_id"] != protocol["protocol_snapshot_id"] or metric["protocol_snapshot_digest"] != protocol["digest"]:
            errors.append(f"identity_chain.metric_result_refs[{index}]: protocol binding mismatch")
        if metric["run_manifest_id"] != run["run_manifest_id"] or metric["run_manifest_digest"] != run["digest"]:
            errors.append(f"identity_chain.metric_result_refs[{index}]: run binding mismatch")
        if metric["estimand_id"] != estimand["estimand_id"] or metric["estimand_digest"] != estimand["digest"]:
            errors.append(f"identity_chain.metric_result_refs[{index}]: estimand binding mismatch")
    return errors


def interval_semantics(instance: dict[str, Any], errors: list[str]) -> tuple[Decimal | None, Decimal | None, Decimal | None]:
    uncertainty = instance["uncertainty"]
    lower = upper = reference = None
    if uncertainty["lower"] is not None:
        lower = quantity_value(uncertainty["lower"], "uncertainty.lower", errors)
    if uncertainty["upper"] is not None:
        upper = quantity_value(uncertainty["upper"], "uncertainty.upper", errors)
    if uncertainty["null_reference"] is not None:
        reference = quantity_value(uncertainty["null_reference"], "uncertainty.null_reference", errors)

    quantities = [item for item in (uncertainty["lower"], uncertainty["upper"], uncertainty["null_reference"]) if item is not None]
    if quantities and any(not same_quantity_unit(quantities[0], item) for item in quantities[1:]):
        errors.append("uncertainty: bounds and reference must use one exact unit")
    if lower is not None and upper is not None and lower > upper:
        errors.append("uncertainty: lower bound exceeds upper bound")

    expected = "not_applicable"
    if reference is not None and (lower is not None or upper is not None):
        inside_lower = lower is None or lower <= reference
        inside_upper = upper is None or reference <= upper
        expected = "yes" if inside_lower and inside_upper else "no"
    if uncertainty["includes_null"] not in {expected, "indeterminate"}:
        errors.append(f"uncertainty.includes_null: declared {uncertainty['includes_null']!r}, recomputed {expected!r}")

    point = instance["result_value"].get("point_estimate")
    if point is not None:
        point_value = quantity_value(point, "result_value.point_estimate", errors)
        if quantities and not same_quantity_unit(point, quantities[0]):
            errors.append("result_value.point_estimate: unit differs from uncertainty")
        if point_value is not None and lower is not None and point_value < lower:
            errors.append("result_value.point_estimate: below uncertainty lower bound")
        if point_value is not None and upper is not None and point_value > upper:
            errors.append("result_value.point_estimate: above uncertainty upper bound")
    return lower, upper, reference


def result_semantics(instance: dict[str, Any]) -> list[str]:
    errors = fixed_timestamp_errors(instance) + identity_chain_errors(instance)
    lower, upper, reference = interval_semantics(instance, errors)
    decision = instance["decision"]
    outcome = decision["scientific_outcome"]
    consequence = instance["claim_consequence"]
    supported = consequence["supported_predicates"]

    expected_predicate = AFFIRMATIVE_PREDICATE.get(outcome)
    if expected_predicate is not None:
        if supported != [expected_predicate]:
            errors.append(f"claim_consequence: affirmative outcome requires exactly {expected_predicate!r}")
    elif outcome in NEGATIVE_OUTCOMES and supported:
        errors.append("claim_consequence: non-affirmative outcome cannot support a predicate")

    required_forbidden = {"effect_proven_absent", "claim_authority"}
    if not required_forbidden.issubset(set(consequence["forbidden_predicates"])):
        errors.append("claim_consequence: must explicitly forbid effect absence and claim authority")

    if outcome in {"association_supported", "causal_effect_supported"} and reference is not None:
        if lower is None or upper is None or lower <= reference <= upper:
            errors.append("decision: directional support is forbidden when the interval crosses the reference")

    margin = instance["margin_binding"]
    claim_type = instance["claim_type"]
    if claim_type not in {"equivalence", "noninferiority"} and margin["status"] != "not_applicable":
        errors.append("margin_binding: margins are permitted only for equivalence/noninferiority claims")

    if claim_type == "equivalence":
        if margin["status"] != "predeclared":
            errors.append("margin_binding: equivalence requires a predeclared margin")
        lo_margin = quantity_value(margin["lower_margin"], "margin_binding.lower_margin", errors)
        hi_margin = quantity_value(margin["upper_margin"], "margin_binding.upper_margin", errors)
        if not same_quantity_unit(margin["lower_margin"], margin["upper_margin"]):
            errors.append("margin_binding: equivalence margins have incompatible units")
        if margin["lower_margin"] is not None and instance["uncertainty"]["lower"] is not None and not same_quantity_unit(margin["lower_margin"], instance["uncertainty"]["lower"]):
            errors.append("margin_binding: equivalence margin unit differs from interval")
        inside = None not in (lo_margin, lower, upper, hi_margin) and lo_margin < lower <= upper < hi_margin
        if outcome == "equivalent" and not inside:
            errors.append("decision: equivalence interval is not strictly inside both predeclared margins")
        if outcome == "equivalent" and instance["uncertainty"]["margin_assessment"] != "inside_predeclared_equivalence_margin":
            errors.append("uncertainty.margin_assessment: does not record equivalence success")
    elif claim_type == "noninferiority":
        if margin["status"] != "predeclared":
            errors.append("margin_binding: noninferiority requires a predeclared margin")
        loss = quantity_value(margin["noninferiority_margin"], "margin_binding.noninferiority_margin", errors)
        if loss is not None and loss <= 0:
            errors.append("margin_binding.noninferiority_margin: must be strictly positive")
        meets = False
        if None not in (loss, reference):
            if margin["benefit_direction"] == "higher_is_better" and lower is not None:
                meets = lower > reference - loss
            elif margin["benefit_direction"] == "lower_is_better" and upper is not None:
                meets = upper < reference + loss
        if outcome == "noninferior" and not meets:
            errors.append("decision: one-sided interval does not meet the noninferiority boundary")

    physical = instance["physical_evidence"]
    if outcome == "physically_validated_under_scope":
        physical_origins = {"physical_world_measurement", "mixed_with_physical_world_measurement"}
        if physical["evidence_origin"] not in physical_origins or not physical["physical_measurement_refs"]:
            errors.append("physical_evidence: physical validation requires retained physical-world measurements")
    if physical["evidence_origin"] in {"simulation_only", "calibration_only", "code_verification_only"} and physical["physical_validation_claim_permitted"]:
        errors.append("physical_evidence: simulation/calibration/code cannot permit physical validation")

    sequential = instance["sequential_accounting"]
    planned, observed = sequential["planned_look_count"], sequential["observed_look_count"]
    if sequential["regime"] == "fixed_horizon" and planned != 1:
        errors.append("sequential_accounting: fixed-horizon plan must declare exactly one look")
    if isinstance(planned, int) and isinstance(observed, int) and observed > planned:
        errors.append("sequential_accounting: observed look count exceeds planned look count")
    if outcome in AFFIRMATIVE_PREDICATE and sequential["unplanned_peeking_detected"] != "no":
        errors.append("sequential_accounting: affirmative inference after unplanned peeking is forbidden")

    missing = instance["missingness_accounting"]
    if missing["unknown_count_status"] == "known":
        total = missing["observed_count"] + missing["missing_count"] + missing["excluded_count"]
        if missing["eligible_count"] != total:
            errors.append("missingness_accounting: eligible != observed + missing + excluded")

    partitions = instance["data_role_accounting"]["partitions"]
    keys = [artifact_key(item["manifest_ref"]) for item in partitions]
    if len(keys) != len(set(keys)):
        errors.append("data_role_accounting.partitions: one manifest cannot occupy multiple roles")

    if instance["evidence_measure"]["type"] == "p_value":
        p_value = decimal(instance["evidence_measure"]["value"], "evidence_measure.value", errors)
        if p_value is not None and not Decimal("0") <= p_value <= Decimal("1"):
            errors.append("evidence_measure.value: p-value must lie in [0,1]")

    if instance["analysis_mode"] == "confirmatory" and outcome in AFFIRMATIVE_PREDICATE:
        if any(item["effect"] == "invalidates_confirmatory" for item in instance["deviations"]):
            errors.append("deviations: affirmative confirmatory result has an invalidating deviation")
    return errors


def semantic_errors(schema_path: str, instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["semantic subject must be an object"]
    dispatch = {
        "schemas/estimand-contract.schema.json": estimand_semantics,
        "schemas/scientific-result-envelope.schema.json": result_semantics,
        "schemas/protocol-snapshot.schema.json": protocol_semantics,
        "schemas/metric-result.schema.json": metric_semantics,
    }
    return dispatch[schema_path](instance)


def main() -> int:
    manifest = load(CASES)
    failures: list[str] = []
    semantic_count = 0
    valid_count = 0
    invalid_count = 0

    for case in manifest["cases"]:
        schema_path = case["schema"]
        schema = load(ROOT / schema_path)
        Draft202012Validator.check_schema(schema)
        changes: list[dict[str, Any]] = []
        for set_name in case.get("use_mutation_sets", []):
            changes.extend(manifest["mutation_sets"][set_name])
        changes.extend(case.get("mutations", []))
        subject = mutate(load(ROOT / case["fixture"]), changes)
        schema_errors = sorted(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(subject),
            key=lambda error: list(error.absolute_path),
        )
        structural_actual = "invalid" if schema_errors else "valid"
        if structural_actual != case["expect"]:
            detail = schema_errors[0].message if schema_errors else "mutation was unexpectedly accepted"
            failures.append(f"{case['name']}: expected structural {case['expect']}, got {structural_actual}: {detail}")
            continue

        if case["expect"] == "valid":
            valid_count += 1
        else:
            invalid_count += 1

        if "semantic_expect" in case:
            semantic_count += 1
            if schema_errors:
                failures.append(f"{case['name']}: semantic check requires a structurally valid subject")
                continue
            bounded_errors = semantic_errors(schema_path, subject)
            semantic_actual = "invalid" if bounded_errors else "valid"
            if semantic_actual != case["semantic_expect"]:
                detail = bounded_errors[0] if bounded_errors else "semantic mutation was unexpectedly accepted"
                failures.append(f"{case['name']}: expected semantic {case['semantic_expect']}, got {semantic_actual}: {detail}")

    if failures:
        print("Mathematical contract cases failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Mathematical contract cases passed: {len(manifest['cases'])} "
        f"({valid_count} structurally valid, {invalid_count} structurally invalid, "
        f"{semantic_count} bounded semantic checks; no scientific authority or Gate A acceptance)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
