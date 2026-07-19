#!/usr/bin/env python3
"""Isolated structural and local-semantic checks for Odeya physical contracts.

This is deliberately architecture evidence rather than runtime. It validates
the candidate schema family, bounded fixtures, local algebraic invariants, the
acyclic physical-contract dependency order, and one resolver-backed physical
verification scope without claiming registry, reducer, metrology, VVUQ,
domain, or safety approval.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/physical-contracts/fixtures"
CASE_MANIFEST = ROOT / "tests/physical-contracts/cases.json"
VERIFICATION_FIXTURE = (
    ROOT / "tests/architecture-schema/fixtures/verification-run-physical.valid.json"
)
SCHEMAS = {
    "quantity": "schemas/physical-quantity.schema.json",
    "uncertainty": "schemas/uncertainty-budget.schema.json",
    "asset": "schemas/asset-configuration-snapshot.schema.json",
    "measurement": "schemas/physical-measurement-result.schema.json",
    "model": "schemas/physical-model-record.schema.json",
    "evidence": "schemas/physical-evidence-vector.schema.json",
    "safety": "schemas/safety-envelope.schema.json",
    "experiment": "schemas/physical-experiment-contract.schema.json",
    "verification": "schemas/verification-run.schema.json",
}
DEPENDENCY_ORDER = list(SCHEMAS)
# identities follow the live schema bytes: a reissue wave bumps versions and
# the factories must construct records against the identity that governs now
SCHEMA_URNS = {
    key: json.loads((ROOT / path).read_text("utf-8"))["$id"]
    for key, path in SCHEMAS.items()
}
SCHEMA_VERSIONS = {
    key: urn.rsplit(":", 1)[1] for key, urn in SCHEMA_URNS.items()
}
EXPECTED_DECIMAL_PATTERN = (
    r"^(0(?:\.[0-9]+)?|[1-9][0-9]*(?:\.[0-9]+)?|"
    r"-(?:[1-9][0-9]*(?:\.[0-9]+)?|0\.[0-9]*[1-9][0-9]*))$"
)
EXPECTED_UTC_PATTERN = (
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}\.[0-9]{6}Z$"
)



def governed_decimal(value: object) -> object:
    """Unwrap a frozen typed scientific-decimal object to its lexical string.

    The D3 wave migrated decimal leaves to closed objects carrying `decimal`
    (or `elements`), `semantic_type`, `unit`, and `precision`. Semantic checks
    must keep firing on the lexical value inside, never silently skip.
    """
    if isinstance(value, dict) and "decimal" in value and "semantic_type" in value:
        return value["decimal"]
    return value

def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=reject_duplicate_keys)


def digest(nibble: str) -> str:
    return "sha256:" + nibble * 64


def artifact(name: str, nibble: str = "a") -> dict[str, object]:
    return {"artifact_id": name, "digest": digest(nibble), "media_type": "application/json"}


def record(name: str, schema_id: str, nibble: str = "b") -> dict[str, object]:
    return {"record_id": name, "version": 1, "schema_id": schema_id, "digest": digest(nibble)}


def method(name: str, nibble: str = "c") -> dict[str, object]:
    return {"method_id": name, "version": "1.0.0", "registry_digest": digest(nibble)}


def quantity_ref(name: str = "quantity.force") -> dict[str, object]:
    return record(name, SCHEMA_URNS["quantity"], "1")


def measurement_ref(name: str) -> dict[str, object]:
    return record(name, SCHEMA_URNS["measurement"], "2")


def quantity() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSIONS["quantity"],
        "quantity_id": "quantity.force",
        "version": 1,
        "quantity_kind": "force",
        "value": {"representation": "exact_decimal", "exact_decimal": {"decimal": "12.5", "semantic_type": "measured_quantity", "unit": "dimensionless", "precision": "exact_lexical"}},
        "unit": {
            "unit_id": "si:newton",
            "registry_ref": record("unit-registry.si", "urn:odeya:registry:unit-registry:1.0.0", "3"),
            "symbol": "N",
            "dimension_vector": {
                "length": 1,
                "mass": 1,
                "time": -2,
                "electric_current": 0,
                "thermodynamic_temperature": 0,
                "amount_of_substance": 0,
                "luminous_intensity": 0,
            },
            "semantic_kind": {
                "kind": "ordinary_physical",
                "semantic_definition_ref": record(
                    "quantity-kind.force", "urn:odeya:registry:quantity-kind:1.0.0", "4"
                ),
            },
            "conversion_to_si": {
                "conversion_class": "multiplicative",
                "scale": {"decimal": "1", "semantic_type": "unit_conversion_factor", "unit": "dimensionless", "precision": "exact_lexical"},
                "offset": "0",
                "ordinary_multiplication_permitted": True,
                "conversion_method_ref": record(
                    "conversion.newton-si", "urn:odeya:profile:unit-conversion:1.0.0", "5"
                ),
            },
        },
        "support": {
            "frame": {
                "applicability": "required",
                "frame": {
                    "frame_ref": record("frame.test-rig", "urn:odeya:profile:reference-frame:1.0.0", "6"),
                    "origin_ref": artifact("frame-origin.test-rig", "6"),
                    "axes_convention_ref": artifact("axes.test-rig", "7"),
                    "handedness": "right_handed",
                    "epoch": "2026-07-16T08:00:00.000000Z",
                    "time_scale": "tai",
                    "transform_uncertainty_ref": record(
                        "uncertainty.frame-transform", SCHEMA_URNS["uncertainty"], "8"
                    ),
                },
            },
            "time": {
                "kind": "instant",
                "start": "2026-07-16T08:00:00.000000Z",
                "end": None,
                "clock_ref": record("clock.lab", "urn:odeya:profile:controlled-clock:1.0.0", "9"),
                "time_scale": "tai",
            },
            "spatial": {
                "kind": "point",
                "support_ref": artifact("support.load-cell", "a"),
                "resolution_ref": artifact("resolution.load-cell", "b"),
            },
        },
        "correlation_group_ids": ["correlation.load-chain"],
        "provenance_ref": artifact("provenance.quantity-force", "c"),
        "quantity_digest": digest("d"),
    }


def contribution(name: str, source: str, nibble: str) -> dict[str, object]:
    return {
        "contribution_id": name,
        "source_kind": source,
        "standard_uncertainty_ref": quantity_ref(f"quantity.u-{name}"),
        "degrees_of_freedom": 30,
        "sensitivity_coefficient_ref": quantity_ref(f"quantity.sensitivity-{name}"),
        "source_provenance_ref": artifact(f"provenance.{name}", nibble),
        "calibration_chain_member_refs": [artifact(f"calibration-chain.{name}", nibble)],
    }


def uncertainty() -> dict[str, object]:
    a = contribution("u-repeatability", "repeatability", "1")
    b = contribution("u-calibration", "calibration", "2")
    return {
        "schema_version": SCHEMA_VERSIONS["uncertainty"],
        "uncertainty_budget_id": "uncertainty.force",
        "version": 1,
        "subject_quantity_refs": [quantity_ref()],
        "evaluation_method_ref": method("gum-linear-propagation"),
        "evaluation_origin": {"type_a": [a], "type_b": [b]},
        "nature_classification": [
            {
                "contribution_id": "u-repeatability",
                "nature": "aleatory",
                "classification_method_ref": method("uncertainty-nature-classification"),
                "classification_evidence_ref": artifact("classification.repeatability", "3"),
            },
            {
                "contribution_id": "u-calibration",
                "nature": "epistemic",
                "classification_method_ref": method("uncertainty-nature-classification"),
                "classification_evidence_ref": artifact("classification.calibration", "4"),
            },
        ],
        "dependence_model": {
            "representation": "covariance_and_correlation",
            "variable_quantity_refs": [quantity_ref("quantity.u-repeatability"), quantity_ref("quantity.u-calibration")],
            "covariance_matrix": {"elements": [["0.04", "0.01"], ["0.01", "0.09"]], "semantic_type": "covariance_element", "unit": "pairwise_unit_product", "precision": "exact_lexical"},
            "correlation_matrix": {"elements": [["1", "0.1666666667"], ["0.1666666667", "1"]], "semantic_type": "correlation_coefficient", "unit": "dimensionless", "precision": "exact_lexical"},
            "matrix_unit_rule_ref": artifact("matrix-unit-rule.force", "5"),
            "shared_source_groups": [
                {
                    "group_id": "shared.load-chain",
                    "contribution_ids": ["u-repeatability", "u-calibration"],
                    "source_provenance_ref": artifact("shared-source.load-chain", "6"),
                    "calibration_provenance_refs": [artifact("calibration-provenance.load-chain", "7")],
                }
            ],
            "provenance_ref": artifact("dependence-model.provenance", "8"),
        },
        "calibration_traceability": {
            "status": "complete",
            "certificate_refs": [artifact("certificate.load-cell", "9")],
            "chain_refs": [artifact("traceability-chain.load-cell", "a")],
            "root_standard_ref": artifact("root-standard.force", "b"),
            "uncertainty_contribution_ids": ["u-calibration"],
            "reason_codes": [],
        },
        "propagation": {
            "method_ref": method("gum-linear-propagation"),
            "regime": "linear_first_order",
            "linearization_used": True,
            "jacobian_ref": artifact("jacobian.force", "c"),
            "distribution_propagation_ref": None,
            "assumption_refs": [artifact("assumption.local-linearity", "d")],
        },
        "combined_result": {
            "status": "computed",
            "combined_standard_uncertainty_ref": quantity_ref("quantity.u-combined"),
            "expanded_uncertainty_ref": quantity_ref("quantity.u-expanded"),
            "coverage_factor": {"decimal": "2", "semantic_type": "coverage_factor", "unit": "dimensionless", "precision": "exact_lexical"},
            "coverage_probability": {"decimal": "0.95", "semantic_type": "interval_confidence_level", "unit": "dimensionless", "precision": "6"},
            "distribution_ref": record("distribution.force", "urn:odeya:schema:distribution-record:1.0.0", "e"),
            "reason_codes": [],
        },
        "disposition": "pass",
        "reason_codes": [],
        "evidence_refs": [artifact("uncertainty-evidence.force", "f")],
        "budget_digest": digest("1"),
    }


def firmware(status: str = "known") -> dict[str, object]:
    if status == "known":
        return {
            "status": "known",
            "version": "3.2.1",
            "image_ref": artifact("firmware.image", "2"),
            "reason_codes": [],
        }
    return {"status": status, "version": None, "image_ref": None, "reason_codes": [f"firmware-{status}"]}


def hardware_component(name: str, nibble: str) -> dict[str, object]:
    return {
        "component_id": name,
        "component_class": "load-cell",
        "manufacturer": "Odeya Test Metrology",
        "model": "LC-100",
        "serial_status": "known",
        "serial_number": f"SN-{name.upper()}",
        "hardware_manifest_ref": artifact(f"hardware-manifest.{name}", nibble),
        "firmware": firmware(),
        "reason_codes": [],
    }


def state(name: str, nibble: str) -> dict[str, object]:
    return {
        "status": "known_nominal",
        "evidence_refs": [artifact(f"state.{name}", nibble)],
        "reason_codes": [],
    }


def asset() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSIONS["asset"],
        "asset_configuration_snapshot_id": "asset-snapshot.inbar-rig",
        "version": 1,
        "asset_ref": record("asset.inbar-rig", "urn:odeya:schema:physical-asset:1.0.0", "3"),
        "effective_interval": {
            "effective_from": "2026-07-16T07:00:00.000000Z",
            "effective_until": "2026-08-16T07:00:00.000000Z",
            "controlled_time_source_ref": artifact("clock-observation.asset", "4"),
        },
        "geometry_ref": artifact("geometry.inbar-rig", "5"),
        "material_manifest_ref": artifact("materials.inbar-rig", "6"),
        "topology_ref": artifact("topology.inbar-rig", "7"),
        "hardware_identity_coverage": {
            "status": "complete",
            "expected_component_count": 2,
            "observed_component_count": 2,
            "expected_component_ids": ["load-cell-a", "load-cell-b"],
            "components": [hardware_component("load-cell-a", "8"), hardware_component("load-cell-b", "9")],
            "coverage_evidence_ref": artifact("coverage.inbar-rig", "a"),
            "reason_codes": [],
        },
        "software_components": [
            {
                "component_id": "acquisition-stack",
                "version": "1.4.0",
                "artifact_ref": artifact("software.acquisition", "b"),
                "role": "acquisition",
            }
        ],
        "boundary_condition_refs": [quantity_ref("quantity.boundary-load")],
        "initial_condition_refs": [quantity_ref("quantity.initial-load")],
        "maintenance_state": state("maintenance", "c"),
        "damage_state": state("damage", "d"),
        "modification_state": state("modification", "e"),
        "sensor_topology_ref": artifact("sensor-topology.inbar-rig", "f"),
        "sensor_calibration_state_ref": artifact("sensor-calibration.inbar-rig", "1"),
        "applicability_disposition": "in_force",
        "reason_codes": [],
        "invalidation_triggers": [
            "geometry_change",
            "material_change",
            "hardware_identity_change",
            "software_or_firmware_change",
            "damage_change",
            "calibration_change",
            "effective_interval_expiry",
        ],
        "snapshot_digest": digest("2"),
    }


def quality_flag(name: str) -> dict[str, object]:
    return {"disposition": "clear", "evidence_ref": artifact(f"quality.{name}", "3"), "reason_codes": []}


def measurement() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSIONS["measurement"],
        "physical_measurement_result_id": "measurement.inbar.validation",
        "version": 1,
        "mission_id": "mission.inbar",
        "measurand_definition_ref": artifact("measurand.force", "4"),
        "result_status": "measured",
        "measured_quantity_ref": quantity_ref(),
        "uncertainty_budget_ref": record("uncertainty.force", SCHEMA_URNS["uncertainty"], "5"),
        "asset_configuration_snapshot_ref": record("asset-snapshot.inbar-rig", SCHEMA_URNS["asset"], "6"),
        "raw_signal": {
            "status": "available",
            "artifact_ref": artifact("raw-signal.inbar-run", "7"),
            "byte_digest": digest("8"),
            "sample_count": 4096,
            "reason_codes": [],
        },
        "acquisition": {
            "procedure_ref": artifact("procedure.force-acquisition", "9"),
            "sampling_method_ref": method("uniform-sampling"),
            "sample_rate_ref": quantity_ref("quantity.sample-rate"),
            "filter_ref": artifact("filter.anti-alias", "a"),
            "latency_ref": quantity_ref("quantity.acquisition-latency"),
            "synchronization_ref": artifact("synchronization.lab", "b"),
            "clock_ref": record("clock.lab", "urn:odeya:schema:controlled-clock:1.0.0", "c"),
            "time_scale": "tai",
            "acquisition_interval_ref": artifact("interval.inbar-run", "d"),
        },
        "instrument": {
            "instrument_ref": record("instrument.load-cell-a", "urn:odeya:schema:instrument:1.0.0", "e"),
            "identity_status": "known",
            "manufacturer": "Odeya Test Metrology",
            "model": "LC-100",
            "serial_number": "SN-LOAD-CELL-A",
            "firmware": firmware(),
            "range_min_ref": quantity_ref("quantity.force-min"),
            "range_max_ref": quantity_ref("quantity.force-max"),
            "configuration_ref": artifact("instrument-config.load-cell-a", "f"),
            "reason_codes": [],
        },
        "environment_quantity_refs": [quantity_ref("quantity.ambient-temperature")],
        "calibration_traceability": {
            "status": "complete",
            "certificate_ref": artifact("certificate.load-cell-a", "1"),
            "chain_refs": [artifact("calibration-chain.load-cell-a", "2")],
            "root_standard_ref": artifact("root-standard.force", "3"),
            "effective_at": "2026-07-01T00:00:00.000000Z",
            "expires_at": "2027-07-01T00:00:00.000000Z",
            "uncertainty_budget_binding": record("uncertainty.force", SCHEMA_URNS["uncertainty"], "4"),
            "evidence_role": "measurement_traceability_not_physical_validation",
            "reason_codes": [],
        },
        "correction_model_ref": record("correction.load-cell", "urn:odeya:schema:correction-model:1.0.0", "5"),
        "quality_flags": {
            name: quality_flag(name) for name in ("saturation", "clipping", "aliasing", "dropout", "synchronization")
        },
        "scientific_validity": "valid",
        "reason_codes": [],
        "operator_ref": record("principal.lab-operator", "urn:odeya:schema:principal:1.0.0", "6"),
        "transformation_provenance_refs": [artifact("transformation.raw-to-force", "7")],
        "recorded_at": "2026-07-16T08:05:00.000000Z",
        "measurement_digest": digest("8"),
    }


def verification_result(origin: str, name: str) -> dict[str, object]:
    return {
        "disposition": "pass",
        "method_ref": method(f"method.{name}"),
        "evidence_refs": [artifact(f"evidence.{name}", "9")],
        "evidence_origin": origin,
        "reason_codes": [],
    }


def model() -> dict[str, object]:
    calibration_measurement = measurement_ref("measurement.inbar.calibration")
    validation_measurement = measurement_ref("measurement.inbar.validation")
    return {
        "schema_version": SCHEMA_VERSIONS["model"],
        "physical_model_record_id": "physical-model.inbar-load-response",
        "version": 1,
        "mission_id": "mission.inbar",
        "model_class": "hybrid_physics_ml",
        "asset_configuration_snapshot_refs": [record("asset-snapshot.inbar-rig", SCHEMA_URNS["asset"], "a")],
        "conceptual_model": {
            "conceptual_model_ref": artifact("conceptual-model.inbar", "b"),
            "governing_equations_ref": artifact("equations.inbar", "c"),
            "constitutive_law_refs": [artifact("constitutive-law.elastic", "d")],
            "omitted_physics_refs": [artifact("omitted-physics.temperature-drift", "e")],
            "conservation_check_refs": [artifact("conservation-check.energy", "f")],
            "conceptual_adequacy_disposition": "pass",
        },
        "code_model": {
            "code_ref": artifact("code.inbar-model", "1"),
            "environment_ref": artifact("environment.inbar-model", "2"),
            "dependency_manifest_ref": artifact("dependencies.inbar-model", "3"),
            "implementation_identity_ref": record("implementation.inbar-model", "urn:odeya:schema:implementation:1.0.0", "4"),
            "compiler_or_interpreter_ref": artifact("interpreter.python", "5"),
        },
        "numerical_model": {
            "method_ref": method("solver.newmark"),
            "solver_ref": artifact("solver.inbar", "6"),
            "mesh_or_discretization_ref": artifact("mesh.inbar", "7"),
            "time_step_rule_ref": artifact("time-step-rule.inbar", "8"),
            "tolerance_profile_ref": artifact("tolerance.inbar", "9"),
            "numerical_error_model_ref": artifact("numerical-error.inbar", "a"),
        },
        "parameter_and_prior_refs": [artifact("parameters.inbar", "b")],
        "initial_condition_refs": [quantity_ref("quantity.initial-load")],
        "boundary_condition_refs": [quantity_ref("quantity.boundary-load")],
        "quantity_of_interest_refs": [quantity_ref()],
        "context_of_use": {
            "decision_ref": artifact("decision.inbar-research", "c"),
            "configuration_scope_ref": artifact("configuration-scope.inbar", "d"),
            "operational_domain_ref": artifact("operational-domain.inbar", "e"),
            "horizon_ref": quantity_ref("quantity.horizon"),
            "consequence_class": "high",
            "model_influence": "control_recommendation",
            "tolerance_profile_ref": artifact("tolerance.inbar", "f"),
        },
        "assumption_refs": [artifact("assumption.inbar", "1")],
        "exclusion_refs": [artifact("exclusion.inbar", "2")],
        "discrepancy_model": {
            "status": "modeled",
            "model_ref": artifact("discrepancy-model.inbar", "3"),
            "parameter_discrepancy_confounding_assessment_ref": artifact("confounding.inbar", "4"),
            "evidence_refs": [artifact("evidence.discrepancy", "5")],
            "reason_codes": [],
        },
        "calibration_partition": {
            "partition_id": "partition.calibration",
            "dataset_manifest_ref": artifact("dataset.calibration", "6"),
            "measurement_refs": [calibration_measurement],
            "selection_rule_ref": artifact("selection.calibration", "7"),
            "independence_group_id": "independence.calibration",
            "data_origin": "physical_world_measurement",
            "purpose": "parameter_calibration",
        },
        "validation_partition": {
            "partition_id": "partition.validation",
            "dataset_manifest_ref": artifact("dataset.validation", "8"),
            "measurement_refs": [validation_measurement],
            "selection_rule_ref": artifact("selection.validation", "9"),
            "independence_group_id": "independence.validation",
            "data_origin": "physical_world_measurement",
            "purpose": "physical_validation",
        },
        "code_verification": verification_result("analytic_manufactured_regression_or_independent_code", "code-verification"),
        "solution_verification": verification_result("mesh_time_step_tolerance_or_numerical_error", "solution-verification"),
        "physical_validation": {
            "disposition": "pass",
            "method_ref": method("method.physical-validation"),
            "measurement_refs": [validation_measurement],
            "validation_partition_id": "partition.validation",
            "evidence_origin": "independent_physical_world_measurement",
            "calibration_or_simulation_substitution_permitted": False,
            "reason_codes": [],
        },
        "applicability_disposition": "supported_under_scope",
        "reason_codes": [],
        "model_digest": digest("a"),
    }


def verifier() -> dict[str, object]:
    return {
        "principal_ref": record("principal.verifier", "urn:odeya:schema:principal:1.0.0", "b"),
        "organization_ref": record("organization.independent-lab", "urn:odeya:schema:organization:1.0.0", "c"),
        "execution_identity_ref": record("execution.verifier", "urn:odeya:schema:execution-identity:1.0.0", "d"),
        "independence_evidence_ref": artifact("independence.verifier", "e"),
    }


COMPONENT_ORIGINS = {
    "code_verification": "code_or_analytic",
    "solution_verification": "numerical_convergence",
    "measurement_traceability": "measurement_traceability",
    "identifiability": "identifiability_analysis",
    "calibration": "calibration_partition",
    "uncertainty_quantification": "uncertainty_analysis",
    "applicability": "applicability_analysis",
    "causal_support": "causal_experiment",
    "safety_case": "safety_analysis",
}


def component(name: str) -> dict[str, object]:
    return {
        "component_id": name,
        "disposition": "pass",
        "scope_ref": artifact(f"scope.{name}", "f"),
        "method_ref": method(f"method.{name}"),
        "evidence_refs": [artifact(f"component-evidence.{name}", "1")],
        "assumption_refs": [artifact(f"component-assumption.{name}", "2")],
        "verifier": verifier(),
        "evidence_origin": COMPONENT_ORIGINS[name],
        "reason_codes": [],
    }


def gate(index: int) -> dict[str, object]:
    return {
        "gate_id": f"p{index}",
        "disposition": "pass",
        "evidence_refs": [artifact(f"gate-evidence.p{index}", "3")],
        "reason_codes": [],
        "verifier_ref": record("principal.gate-verifier", "urn:odeya:schema:principal:1.0.0", "4"),
    }


def evidence() -> dict[str, object]:
    vector = {name: component(name) for name in COMPONENT_ORIGINS}
    vector["physical_validation"] = {
        "component_id": "physical_validation",
        "disposition": "pass",
        "scope_ref": artifact("scope.physical-validation", "5"),
        "method_ref": method("method.physical-validation"),
        "evidence_refs": [artifact("component-evidence.physical-validation", "6")],
        "assumption_refs": [artifact("component-assumption.physical-validation", "7")],
        "verifier": verifier(),
        "evidence_origin": "independent_physical_world_measurement",
        "physical_measurement_refs": [measurement_ref("measurement.inbar.validation")],
        "calibration_or_simulation_substitution_permitted": False,
        "reason_codes": [],
    }
    gate_names = [
        "p0_decision_context",
        "p1_measurement",
        "p2_conceptual_adequacy",
        "p3_observability_identifiability",
        "p4_code_verification",
        "p5_solution_verification",
        "p6_calibration",
        "p7_physical_validation",
        "p8_uncertainty_sensitivity",
        "p9_applicability",
        "p10_causal",
        "p11_safety_authority",
        "p12_release",
    ]
    return {
        "schema_version": SCHEMA_VERSIONS["evidence"],
        "physical_evidence_vector_id": "physical-evidence.inbar",
        "version": 1,
        "mission_id": "mission.inbar",
        "physical_model_ref": record("physical-model.inbar-load-response", SCHEMA_URNS["model"], "8"),
        "asset_configuration_snapshot_refs": [record("asset-snapshot.inbar-rig", SCHEMA_URNS["asset"], "9")],
        "measurement_result_refs": [measurement_ref("measurement.inbar.validation")],
        "credibility_vector": vector,
        "vvuq_gates": {name: gate(index) for index, name in enumerate(gate_names)},
        "credibility_disposition": "eligible_under_scope",
        "permitted_claim_language": [
            "computationally_verified",
            "calibrated_on_named_evidence",
            "physically_validated_under_scope",
            "recommendation_inside_safety_envelope",
        ],
        "forbidden_claim_language": [
            "universally_validated",
            "simulation_proves_world",
            "calibration_is_validation",
            "recommendation_is_actuator_authority",
        ],
        "reason_codes": [],
        "independent_review_refs": [artifact("review.physical-evidence", "a")],
        "evidence_vector_digest": digest("b"),
    }


def failure_behavior(kind: str) -> dict[str, object]:
    return {
        "behavior": kind,
        "fallback_ref": artifact(f"fallback.{kind}", "c"),
        "operator_alert_required": True,
        "evidence_ref": artifact(f"failure-evidence.{kind}", "d"),
    }


def safety() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSIONS["safety"],
        "safety_envelope_id": "safety-envelope.inbar",
        "version": 1,
        "mission_id": "mission.inbar",
        "asset_configuration_snapshot_ref": record("asset-snapshot.inbar-rig", SCHEMA_URNS["asset"], "e"),
        "asset_hardware_coverage_observation": "complete",
        "physical_model_ref": record("physical-model.inbar-load-response", SCHEMA_URNS["model"], "f"),
        "physical_evidence_vector_ref": record("physical-evidence.inbar", SCHEMA_URNS["evidence"], "1"),
        "operational_domain_ref": artifact("operational-domain.inbar", "2"),
        "safe_set": {
            "definition_ref": artifact("safe-set.inbar", "3"),
            "state_quantity_refs": [quantity_ref("quantity.force-state")],
            "constraint_method_ref": record("constraint.robust", "urn:odeya:schema:constraint-method:1.0.0", "4"),
            "robustness_margin_ref": quantity_ref("quantity.robustness-margin"),
            "chance_constraint_used": True,
            "hard_guarantee_claimed": False,
        },
        "disturbance_set_ref": artifact("disturbance-set.inbar", "5"),
        "state_estimation_error_ref": artifact("estimation-error.inbar", "6"),
        "actuator_limits": [
            {
                "actuator_id": "actuator.test-load",
                "minimum_ref": quantity_ref("quantity.actuator-min"),
                "maximum_ref": quantity_ref("quantity.actuator-max"),
                "rate_limit_ref": quantity_ref("quantity.actuator-rate"),
                "evidence_ref": artifact("actuator-limit-evidence", "7"),
            }
        ],
        "latency_limit_ref": quantity_ref("quantity.latency-limit"),
        "barrier_or_invariance_evidence_refs": [artifact("barrier-evidence.inbar", "8")],
        "stability_evidence_refs": [artifact("stability-evidence.inbar", "9")],
        "runtime_assurance": {
            "advanced_controller_ref": artifact("controller.advanced", "a"),
            "trusted_fallback_ref": artifact("controller.fallback", "b"),
            "independent_monitor_ref": artifact("monitor.independent", "c"),
            "switching_horizon_ref": quantity_ref("quantity.switching-horizon"),
            "common_mode_analysis_ref": artifact("common-mode-analysis", "d"),
            "monitor_independence_disposition": "independent_under_profile",
        },
        "infeasibility_behavior": failure_behavior("transition_to_trusted_fallback"),
        "saturation_behavior": failure_behavior("safe_stop"),
        "hazard_analysis_ref": artifact("hazard-analysis.inbar", "e"),
        "risk_assessment_ref": artifact("risk-assessment.inbar", "f"),
        "validity": {
            "status": "current",
            "valid_from": "2026-07-16T00:00:00.000000Z",
            "expires_at": "2026-08-16T00:00:00.000000Z",
            "invalidation_trigger_refs": [artifact("invalidation-trigger.asset-change", "1")],
            "controlled_time_source_ref": artifact("clock-observation.safety", "2"),
        },
        "envelope_disposition": "recommendation_supported",
        "reason_codes": [],
        "actuator_boundary": {
            "output_class": "control_recommendation",
            "recommendation_only": True,
            "direct_actuation_permitted": False,
            "actuator_authority_granted": False,
            "execution_authority_ref": None,
            "actuator_gateway_command_ref": None,
            "authority_separation": "required",
            "execution_requires_separate_authority_service": True,
        },
        "independent_safety_review_refs": [artifact("review.safety", "3")],
        "safety_envelope_digest": digest("4"),
    }


def preflight(name: str) -> dict[str, object]:
    return {
        "check_id": name,
        "applicability": "required",
        "disposition": "pass",
        "method_ref": method(f"preflight.{name}"),
        "evidence_refs": [artifact(f"preflight-evidence.{name}", "5")],
        "reason_codes": [],
    }


def experiment() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSIONS["experiment"],
        "physical_experiment_contract_id": "experiment.inbar-load-excitation",
        "version": 1,
        "mission_id": "mission.inbar",
        "hypothesis_ref": artifact("hypothesis.load-response", "6"),
        "rival_hypothesis_refs": [artifact("hypothesis.rival-drift", "7")],
        "target_quantity_refs": [quantity_ref()],
        "causal_estimand_ref": artifact("estimand.load-response", "8"),
        "intervention_policy_ref": artifact("intervention.load-profile", "9"),
        "design": {
            "randomization": "required",
            "control_plan_ref": artifact("control-plan.inbar", "a"),
            "blinding": "not_possible",
            "sampling_plan_ref": artifact("sampling-plan.inbar", "b"),
            "feedback_policy_ref": artifact("feedback-policy.inbar", "c"),
            "intervention_fidelity_ref": artifact("intervention-fidelity.inbar", "d"),
            "manipulation_check_ref": artifact("manipulation-check.inbar", "e"),
        },
        "measurement_plan": {
            "sensor_refs": [record("instrument.load-cell-a", "urn:odeya:schema:instrument:1.0.0", "f")],
            "calibration_requirement_refs": [artifact("calibration-requirement.load-cell", "1")],
            "sampling_ref": artifact("sampling-requirement.inbar", "2"),
            "synchronization_ref": artifact("synchronization-requirement.inbar", "3"),
            "bandwidth_requirement_refs": [quantity_ref("quantity.bandwidth-min")],
            "resolution_requirement_refs": [quantity_ref("quantity.resolution-max")],
            "measurement_method_refs": [method("measurement.force")],
        },
        "asset_binding": {
            "asset_configuration_snapshot_ref": record("asset-snapshot.inbar-rig", SCHEMA_URNS["asset"], "4"),
            "hardware_identity_coverage_observation": "complete",
            "configuration_currentness": "current",
            "observation_evidence_ref": artifact("asset-observation.inbar", "5"),
            "reason_codes": [],
        },
        "physical_model_ref": record("physical-model.inbar-load-response", SCHEMA_URNS["model"], "6"),
        "baseline_physical_evidence_vector_ref": record("physical-evidence.inbar", SCHEMA_URNS["evidence"], "7"),
        "context_ref": artifact("experiment-context.inbar", "8"),
        "expected_information_ref": artifact("expected-information.inbar", "9"),
        "decision_value_ref": artifact("decision-value.inbar", "a"),
        "cost_ref": artifact("cost.inbar", "b"),
        "harm_assessment_ref": artifact("harm-assessment.inbar", "c"),
        "reversibility": "reversible",
        "safety_envelope_ref": record("safety-envelope.inbar", SCHEMA_URNS["safety"], "d"),
        "abort_condition_refs": [artifact("abort-condition.force-limit", "e")],
        "stop_rule_ref": artifact("stop-rule.inbar", "f"),
        "preregistered_analysis_ref": artifact("analysis-plan.inbar", "1"),
        "independent_validation_partition": {
            "partition_id": "partition.experiment-validation",
            "data_manifest_ref": artifact("future-data-manifest.validation", "2"),
            "selection_rule_ref": artifact("selection-rule.validation", "3"),
            "independence_group_id": "independence.experiment-validation",
            "data_origin": "physical_world_measurement",
            "independent_from_calibration": True,
            "simulation_substitution_permitted": False,
        },
        "preflight": {
            name: preflight(name)
            for name in (
                "observability",
                "identifiability",
                "excitation",
                "measurement_capability",
                "causal_identification",
                "safety",
            )
        },
        "planning_disposition": "eligible_for_planning",
        "reason_codes": [],
        "authority_boundary": {
            "proposal_only": True,
            "recommendation_only": True,
            "execution_authorized": False,
            "direct_actuation_permitted": False,
            "authority_self_issued": False,
            "execution_authority_ref": None,
            "actuator_gateway_command_ref": None,
            "separate_authority_service_required": True,
        },
        "experiment_contract_digest": digest("4"),
    }


def verification() -> dict[str, object]:
    """Load the shared physical VerificationPackage architecture fixture.

    Its selected subject resolves below to the exact bounded
    PhysicalEvidenceVector constructor. This is a synthetic contract example,
    never retained real-world verification evidence.
    """
    value = load(VERIFICATION_FIXTURE)
    if not isinstance(value, dict):
        raise TypeError("physical verification fixture must be an object")
    return value


FACTORIES: dict[str, Callable[[], dict[str, object]]] = {
    "quantity": quantity,
    "uncertainty": uncertainty,
    "asset": asset,
    "measurement": measurement,
    "model": model,
    "evidence": evidence,
    "safety": safety,
    "experiment": experiment,
    "verification": verification,
}


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ref_identity(value: dict[str, object]) -> tuple[object, ...]:
    return (value.get("record_id"), value.get("version"), value.get("schema_id"), value.get("digest"))


def quantity_semantics(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    known_units = {
        "si:newton": {
            "symbol": "N",
            "dimension_vector": (1, 1, -2, 0, 0, 0, 0),
            "semantic_kind": "ordinary_physical",
            "conversion_class": "multiplicative",
        }
    }
    unit = value["unit"]
    registered = known_units.get(unit["unit_id"])
    if registered is None:
        errors.append("unit.unit_id: not resolved by bounded test registry")
    else:
        dimensions = unit["dimension_vector"]
        actual_dimensions = tuple(
            dimensions[name]
            for name in (
                "length",
                "mass",
                "time",
                "electric_current",
                "thermodynamic_temperature",
                "amount_of_substance",
                "luminous_intensity",
            )
        )
        if unit["symbol"] != registered["symbol"]:
            errors.append("unit.symbol: does not match registered unit")
        if actual_dimensions != registered["dimension_vector"]:
            errors.append("unit.dimension_vector: does not match registered unit")
        if unit["semantic_kind"]["kind"] != registered["semantic_kind"]:
            errors.append("unit.semantic_kind: does not match registered unit")
        if unit["conversion_to_si"]["conversion_class"] != registered["conversion_class"]:
            errors.append("unit.conversion_to_si: does not match registered unit")
    time_support = value["support"]["time"]
    if time_support["kind"] == "interval" and parse_time(time_support["start"]) >= parse_time(time_support["end"]):
        errors.append("support.time: interval start must precede end")
    return errors


def decimal_matrix(matrix: list[list[str]], name: str, errors: list[str]) -> list[list[Decimal]] | None:
    try:
        return [[Decimal(governed_decimal(cell)) for cell in row] for row in matrix]
    except InvalidOperation:
        errors.append(f"{name}: invalid decimal")
        return None


def uncertainty_semantics(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    type_a = [item["contribution_id"] for item in value["evaluation_origin"]["type_a"]]
    type_b = [item["contribution_id"] for item in value["evaluation_origin"]["type_b"]]
    all_ids = type_a + type_b
    if len(all_ids) != len(set(all_ids)):
        errors.append("evaluation_origin: Type A and Type B contribution identities must be unique and disjoint")
    nature_ids = [item["contribution_id"] for item in value["nature_classification"]]
    if len(nature_ids) != len(set(nature_ids)) or set(nature_ids) != set(all_ids):
        errors.append("nature_classification: must classify every contribution exactly once")
    variables = value["dependence_model"]["variable_quantity_refs"]
    n = len(variables)
    for matrix_name in ("covariance_matrix", "correlation_matrix"):
        raw = value["dependence_model"][matrix_name]
        if isinstance(raw, dict) and "elements" in raw and "semantic_type" in raw:
            raw = raw["elements"]
        if len(raw) != n or any(len(row) != n for row in raw):
            errors.append(f"dependence_model.{matrix_name}: must be square and match variable count")
            continue
        matrix = decimal_matrix(raw, matrix_name, errors)
        if matrix is None:
            continue
        for row in range(n):
            for column in range(n):
                if matrix[row][column] != matrix[column][row]:
                    errors.append(f"dependence_model.{matrix_name}: must be symmetric")
                    break
            if matrix_name == "covariance_matrix" and matrix[row][row] < 0:
                errors.append("dependence_model.covariance_matrix: diagonal variances must be nonnegative")
            if matrix_name == "correlation_matrix":
                if matrix[row][row] != 1:
                    errors.append("dependence_model.correlation_matrix: diagonal must equal one")
                if any(cell < -1 or cell > 1 for cell in matrix[row]):
                    errors.append("dependence_model.correlation_matrix: entries must lie in [-1, 1]")
    for group in value["dependence_model"]["shared_source_groups"]:
        if not set(group["contribution_ids"]).issubset(set(all_ids)):
            errors.append("dependence_model.shared_source_groups: unresolved contribution identity")
    trace_ids = value["calibration_traceability"]["uncertainty_contribution_ids"]
    if not set(trace_ids).issubset(set(all_ids)):
        errors.append("calibration_traceability: unresolved uncertainty contribution identity")
    if value["combined_result"]["status"] == "computed":
        probability = Decimal(governed_decimal(value["combined_result"]["coverage_probability"]))
        factor = Decimal(governed_decimal(value["combined_result"]["coverage_factor"]))
        if not Decimal("0") < probability <= Decimal("1"):
            errors.append("combined_result.coverage_probability: must lie in (0, 1]")
        if factor <= 0:
            errors.append("combined_result.coverage_factor: must be positive")
    return errors


def asset_semantics(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    interval = value["effective_interval"]
    if interval["effective_until"] is not None and parse_time(interval["effective_from"]) >= parse_time(interval["effective_until"]):
        errors.append("effective_interval: effective_from must precede effective_until")
    coverage = value["hardware_identity_coverage"]
    components = coverage["components"]
    component_ids = [component["component_id"] for component in components]
    if coverage["observed_component_count"] != len(components):
        errors.append("hardware_identity_coverage: observed count must equal enumerated components")
    if len(component_ids) != len(set(component_ids)):
        errors.append("hardware_identity_coverage: duplicate component identity")
    if coverage["status"] == "complete":
        if coverage["expected_component_count"] != len(components):
            errors.append("hardware_identity_coverage: complete expected count must equal enumerated components")
        if set(coverage["expected_component_ids"]) != set(component_ids):
            errors.append("hardware_identity_coverage: complete expected identities must equal observed identities")
    return errors


def measurement_semantics(value: dict[str, object]) -> list[str]:
    calibration = value["calibration_traceability"]
    if calibration["status"] == "complete" and parse_time(calibration["effective_at"]) >= parse_time(calibration["expires_at"]):
        return ["calibration_traceability: effective_at must precede expires_at"]
    return []


def model_semantics(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    calibration = value["calibration_partition"]
    validation = value["validation_partition"]
    if calibration["partition_id"] == validation["partition_id"]:
        errors.append("calibration_partition and validation_partition require distinct identities")
    if calibration["independence_group_id"] == validation["independence_group_id"]:
        errors.append("calibration and validation partitions require distinct independence groups")
    calibration_refs = {ref_identity(ref) for ref in calibration["measurement_refs"]}
    validation_refs = {ref_identity(ref) for ref in validation["measurement_refs"]}
    if calibration_refs & validation_refs:
        errors.append("calibration and validation measurement partitions must be disjoint")
    physical_validation = value["physical_validation"]
    if physical_validation["validation_partition_id"] != validation["partition_id"]:
        errors.append("physical_validation: validation_partition_id mismatch")
    if {ref_identity(ref) for ref in physical_validation["measurement_refs"]} != validation_refs:
        errors.append("physical_validation: measurement refs must equal independent validation partition")
    return errors


def evidence_semantics(value: dict[str, object]) -> list[str]:
    physical_refs = {
        ref_identity(ref) for ref in value["credibility_vector"]["physical_validation"]["physical_measurement_refs"]
    }
    top_refs = {ref_identity(ref) for ref in value["measurement_result_refs"]}
    if not physical_refs.issubset(top_refs):
        return ["credibility_vector.physical_validation: physical measurements must be declared at record scope"]
    return []


def safety_semantics(value: dict[str, object]) -> list[str]:
    validity = value["validity"]
    if parse_time(validity["valid_from"]) >= parse_time(validity["expires_at"]):
        return ["validity: valid_from must precede expires_at"]
    return []


def experiment_semantics(value: dict[str, object]) -> list[str]:
    errors: list[str] = []
    if value["planning_disposition"] == "eligible_for_planning":
        if value["reversibility"] == "unknown":
            errors.append("eligible experiment cannot have unknown reversibility")
        if value["independent_validation_partition"]["independence_group_id"] == "independence.calibration":
            errors.append("experiment validation partition cannot reuse calibration independence group")
    return errors


def verification_semantics(value: dict[str, object]) -> list[str]:
    """Resolve a physical verification scope to its exact typed subject.

    VerificationRun intentionally keeps generic subject references. This
    bounded architecture-time resolver joins the retained package to the exact
    PhysicalEvidenceVector fixture and derives class, dimension applicability,
    and terminal language from that typed subject. It does not validate the
    physical world or confer any authority.
    """
    errors: list[str] = []
    target = evidence()
    expected_subject = {
        "subject_type": "result",
        "subject_id": target["physical_evidence_vector_id"],
        "version": target["version"],
        "schema_id": SCHEMA_URNS["evidence"],
        "digest": target["evidence_vector_digest"],
    }
    if value["subject_set"]["subjects"] != [expected_subject]:
        errors.append(
            "verification.subject_set: subject must resolve to the exact typed physical evidence vector"
        )
    if value["mission_id"] != target["mission_id"]:
        errors.append("verification.mission_id: must equal the resolved physical subject mission")
    selection_rule = value["subject_set"]["selection_rule_ref"]
    if selection_rule["record_id"] != "subject-selection-rule.physical-validity-and-safety":
        errors.append(
            "verification.selection_rule: must select the physical-validity and safety predicates"
        )
    if value["frozen_assignment"]["required_verification_class"] != "IV4_independent_replication":
        errors.append(
            "verification.required_verification_class: resolved physical replication scope requires IV4"
        )

    physical = value["dimensions"]["physical_validity"]
    physical_component = target["credibility_vector"]["physical_validation"]
    physical_signature = (
        physical["requirement"],
        physical["verdict"],
        physical["scope"],
        physical["evidence_refs"],
    )
    expected_physical_signature = (
        "required",
        "pass",
        "physically_validated_under_scope",
        physical_component["evidence_refs"],
    )
    if physical_signature != expected_physical_signature:
        errors.append(
            "verification.physical_validity: must be required/pass for the resolved physical predicate"
        )

    safety = value["dimensions"]["safety"]
    safety_component = target["credibility_vector"]["safety_case"]
    safety_signature = (
        safety["requirement"],
        safety["verdict"],
        safety["scope"],
        safety["evidence_refs"],
    )
    expected_safety_signature = (
        "required",
        "pass",
        "recommendation_inside_safety_envelope",
        safety_component["evidence_refs"],
    )
    if safety_signature != expected_safety_signature:
        errors.append(
            "verification.safety: selected safety-bound recommendation requires an applicable passing safety dimension"
        )

    expected_scope_statement = (
        "Synthetic architecture example confirms physically_validated_under_scope and "
        "recommendation_inside_safety_envelope for physical-evidence.inbar under "
        "IV4_independent_replication; advisory only, with no action, dispatch, "
        "publication, or Gate A authority."
    )
    if value["terminal_assessment"]["scope_statement"] != expected_scope_statement:
        errors.append(
            "verification.terminal_assessment: confirmation language must equal the resolver-derived bounded statement"
        )
    if (
        "synthetic_architecture_fixture_not_real_physical_evidence"
        not in value["terminal_assessment"]["reason_codes"]
    ):
        errors.append(
            "verification.terminal_assessment: synthetic evidence boundary must remain explicit"
        )
    return errors


SEMANTIC_CHECKERS = {
    "quantity": quantity_semantics,
    "uncertainty": uncertainty_semantics,
    "asset": asset_semantics,
    "measurement": measurement_semantics,
    "model": model_semantics,
    "evidence": evidence_semantics,
    "safety": safety_semantics,
    "experiment": experiment_semantics,
    "verification": verification_semantics,
}


Mutator = Callable[[dict[str, object]], None]


@dataclass(frozen=True)
class Case:
    name: str
    kind: str
    structural: str = "valid"
    semantic: str | None = None
    mutate: Mutator | None = None
    fixture: str | None = None
    # Refusal attribution (ADR 0055-0061): a structurally known-bad case
    # declares the exact instance pointer and schema keyword that must refuse
    # it; a semantically known-bad case declares a substring of the authored
    # checker message. Refusal for an incidental reason is not proof.
    expected_refusal: tuple[str, str] | None = None
    expected_semantic: str | None = None


def set_path(path: str, value: object) -> Mutator:
    parts = path.split(".")

    def mutate(subject: dict[str, object]) -> None:
        parent: object = subject
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        final = parts[-1]
        if isinstance(parent, list):
            parent[int(final)] = value
        else:
            parent[final] = value

    return mutate


def delete_path(path: str) -> Mutator:
    parts = path.split(".")

    def mutate(subject: dict[str, object]) -> None:
        parent: object = subject
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        final = parts[-1]
        if isinstance(parent, list):
            del parent[int(final)]
        else:
            del parent[final]

    return mutate


def compose(*mutators: Mutator) -> Mutator:
    def mutate(subject: dict[str, object]) -> None:
        for item in mutators:
            item(subject)

    return mutate


def distribution_quantity(subject: dict[str, object]) -> None:
    subject["value"] = {
        "representation": "distribution_reference",
        "distribution_ref": record("distribution.force", "urn:odeya:schema:distribution-record:1.0.0", "5"),
    }


def interval_reversed(subject: dict[str, object]) -> None:
    subject["support"]["time"] = {
        "kind": "interval",
        "start": "2026-07-17T00:00:00.000000Z",
        "end": "2026-07-16T00:00:00.000000Z",
        "clock_ref": record("clock.lab", "urn:odeya:profile:controlled-clock:1.0.0", "9"),
        "time_scale": "tai",
    }


def duplicate_value_alternatives(subject: dict[str, object]) -> None:
    subject["value"]["distribution_ref"] = record(
        "distribution.force", "urn:odeya:schema:distribution-record:1.0.0", "5"
    )


def type_partition_overlap(subject: dict[str, object]) -> None:
    subject["evaluation_origin"]["type_b"][0]["contribution_id"] = "u-repeatability"
    subject["nature_classification"][1]["contribution_id"] = "u-repeatability"


def noncomputed_pass(subject: dict[str, object]) -> None:
    subject["combined_result"] = {
        "status": "not_computed",
        "combined_standard_uncertainty_ref": None,
        "expanded_uncertainty_ref": None,
        "coverage_factor": None,
        "coverage_probability": None,
        "distribution_ref": None,
        "reason_codes": ["not-computed"],
    }


def inbar_asset_blocked() -> dict[str, object]:
    value = asset()
    value["hardware_identity_coverage"] = {
        "status": "unknown",
        "expected_component_count": None,
        "observed_component_count": 0,
        "expected_component_ids": [],
        "components": [],
        "coverage_evidence_ref": artifact("coverage.inbar-unavailable", "a"),
        "reason_codes": ["hardware-identity-observation-unavailable"],
    }
    value["applicability_disposition"] = "blocked"
    value["reason_codes"] = ["unknown-hardware-blocks-applicability"]
    return value


def measurement_unavailable_with_stale_refs(subject: dict[str, object]) -> None:
    subject["result_status"] = "unavailable"
    subject["scientific_validity"] = "indeterminate"
    subject["reason_codes"] = ["measurement-unavailable"]


def partition_overlap(subject: dict[str, object]) -> None:
    subject["validation_partition"]["measurement_refs"] = copy.deepcopy(
        subject["calibration_partition"]["measurement_refs"]
    )
    subject["physical_validation"]["measurement_refs"] = copy.deepcopy(
        subject["validation_partition"]["measurement_refs"]
    )


def evidence_ref_outside_scope(subject: dict[str, object]) -> None:
    subject["credibility_vector"]["physical_validation"]["physical_measurement_refs"] = [
        measurement_ref("measurement.outside-record-scope")
    ]


def inbar_experiment_refused() -> dict[str, object]:
    value = experiment()
    value["asset_binding"]["hardware_identity_coverage_observation"] = "unknown"
    value["asset_binding"]["configuration_currentness"] = "unknown"
    value["asset_binding"]["reason_codes"] = ["inbar-hardware-identity-unknown"]
    value["preflight"]["measurement_capability"]["disposition"] = "indeterminate"
    value["preflight"]["measurement_capability"]["evidence_refs"] = []
    value["preflight"]["measurement_capability"]["reason_codes"] = ["sensor-inventory-unresolved"]
    value["planning_disposition"] = "refused"
    value["reason_codes"] = ["unknown-hardware-cannot-be-treated-as-zero-or-success"]
    return value


CASES = [
    Case("quantity-valid-exact-decimal", "quantity", semantic="valid", fixture="physical-quantity.valid.json"),
    Case("quantity-valid-distribution-alternative", "quantity", semantic="valid", mutate=distribution_quantity),
    Case("quantity-rejects-both-value-alternatives", "quantity", structural="invalid", mutate=duplicate_value_alternatives, expected_refusal=("/value", "oneOf")),
    Case("quantity-rejects-incomplete-seven-base-vector", "quantity", structural="invalid", mutate=delete_path("unit.dimension_vector.luminous_intensity"), expected_refusal=("/unit/dimension_vector", "required")),
    Case("quantity-rejects-affine-ordinary-multiplication", "quantity", structural="invalid", mutate=compose(set_path("unit.conversion_to_si.conversion_class", "affine"), set_path("unit.conversion_to_si.offset", "273.15"), set_path("unit.conversion_to_si.ordinary_multiplication_permitted", True)), expected_refusal=("/unit/conversion_to_si", "oneOf")),
    Case("quantity-rejects-required-null-frame", "quantity", structural="invalid", mutate=set_path("support.frame.frame", None), expected_refusal=("/support/frame/frame", "type")),
    Case("quantity-rejects-instant-without-clock", "quantity", structural="invalid", mutate=set_path("support.time.clock_ref", None), expected_refusal=("/support/time/clock_ref", "type")),
    Case("quantity-rejects-spatial-point-without-support", "quantity", structural="invalid", mutate=set_path("support.spatial.support_ref", None), expected_refusal=("/support/spatial/support_ref", "type")),
    Case("quantity-detects-unit-symbol-masquerade", "quantity", semantic="invalid", mutate=set_path("unit.symbol", "kg"), expected_semantic="unit.symbol: does not match registered unit"),
    Case("quantity-detects-dimension-masquerade", "quantity", semantic="invalid", mutate=set_path("unit.dimension_vector.mass", 0), expected_semantic="unit.dimension_vector: does not match registered unit"),
    Case("quantity-detects-reversed-time-interval", "quantity", semantic="invalid", mutate=interval_reversed, expected_semantic="interval start must precede end"),
    Case("quantity-accepts-legitimate-negative-nonzero", "quantity", semantic="valid", mutate=set_path("value.exact_decimal.decimal", "-0.125")),
    Case("quantity-rejects-negative-zero-integer", "quantity", structural="invalid", mutate=set_path("value.exact_decimal.decimal", "-0"), expected_refusal=("/value", "oneOf")),
    Case("quantity-rejects-negative-zero-fraction", "quantity", structural="invalid", mutate=set_path("value.exact_decimal.decimal", "-0.0"), expected_refusal=("/value", "oneOf")),
    # the frozen scientific-decimal contract admits lowercase exponents and
    # rejects the uppercase form; the trap follows the profile, not the retired
    # local no-exponent rule
    Case("quantity-rejects-uppercase-exponent-decimal", "quantity", structural="invalid", mutate=set_path("value.exact_decimal.decimal", "1E3"), expected_refusal=("/value", "oneOf")),
    Case("quantity-rejects-leading-zero-decimal", "quantity", structural="invalid", mutate=set_path("value.exact_decimal.decimal", "01"), expected_refusal=("/value", "oneOf")),
    Case("quantity-rejects-offset-time", "quantity", structural="invalid", mutate=set_path("support.time.start", "2026-07-16T10:00:00.000000+02:00"), expected_refusal=("/support/time/start", "pattern")),
    Case("quantity-rejects-nonmicrosecond-time", "quantity", structural="invalid", mutate=set_path("support.time.start", "2026-07-16T08:00:00Z"), expected_refusal=("/support/time/start", "pattern")),
    Case("quantity-rejects-offset-frame-epoch", "quantity", structural="invalid", mutate=set_path("support.frame.frame.epoch", "2026-07-16T10:00:00.000000+02:00"), expected_refusal=("/support/frame/frame/epoch", "oneOf")),

    Case("uncertainty-valid-type-and-nature-partitions", "uncertainty", semantic="valid", fixture="uncertainty-budget.valid.json"),
    Case("uncertainty-detects-type-a-type-b-overlap", "uncertainty", semantic="invalid", mutate=type_partition_overlap, expected_semantic="Type A and Type B contribution identities must be unique and disjoint"),
    Case("uncertainty-detects-missing-nature-classification", "uncertainty", semantic="invalid", mutate=delete_path("nature_classification.1"), expected_semantic="must classify every contribution exactly once"),
    Case("uncertainty-detects-nonsquare-covariance", "uncertainty", semantic="invalid", mutate=delete_path("dependence_model.covariance_matrix.elements.1.1"), expected_semantic="must be square and match variable count"),
    Case("uncertainty-detects-asymmetric-covariance", "uncertainty", semantic="invalid", mutate=set_path("dependence_model.covariance_matrix.elements.0.1", "0.02"), expected_semantic="must be symmetric"),
    Case("uncertainty-detects-correlation-out-of-range", "uncertainty", semantic="invalid", mutate=compose(set_path("dependence_model.correlation_matrix.elements.0.1", "1.2"), set_path("dependence_model.correlation_matrix.elements.1.0", "1.2")), expected_semantic="entries must lie in [-1, 1]"),
    Case("uncertainty-detects-correlation-diagonal-not-one", "uncertainty", semantic="invalid", mutate=set_path("dependence_model.correlation_matrix.elements.0.0", "0.9"), expected_semantic="diagonal must equal one"),
    Case("uncertainty-detects-unresolved-shared-source", "uncertainty", semantic="invalid", mutate=set_path("dependence_model.shared_source_groups.0.contribution_ids.1", "u-unknown"), expected_semantic="shared_source_groups: unresolved contribution identity"),
    Case("uncertainty-rejects-unknown-traceability-pass", "uncertainty", structural="invalid", mutate=compose(set_path("calibration_traceability.status", "unknown"), set_path("calibration_traceability.reason_codes", ["traceability-unknown"])), expected_refusal=("/disposition", "enum")),
    Case("uncertainty-rejects-not-computed-pass", "uncertainty", structural="invalid", mutate=noncomputed_pass, expected_refusal=("/disposition", "enum")),
    Case("uncertainty-rejects-negative-zero-covariance", "uncertainty", structural="invalid", mutate=set_path("dependence_model.covariance_matrix.elements.0.0", "-0"), expected_refusal=("/dependence_model/covariance_matrix/elements/0/0", "pattern")),
    Case("uncertainty-accepts-negative-nonzero-covariance", "uncertainty", semantic="valid", mutate=compose(set_path("dependence_model.covariance_matrix.elements.0.1", "-0.01"), set_path("dependence_model.covariance_matrix.elements.1.0", "-0.01"))),

    Case("asset-valid-complete-hardware", "asset", semantic="valid"),
    Case("asset-valid-inbar-unknown-hardware-blocked", "asset", semantic="valid", fixture="asset-configuration-snapshot.inbar-blocked.valid.json"),
    Case("asset-rejects-complete-unknown-serial", "asset", structural="invalid", mutate=compose(set_path("hardware_identity_coverage.components.0.serial_status", "unknown"), set_path("hardware_identity_coverage.components.0.serial_number", None), set_path("hardware_identity_coverage.components.0.reason_codes", ["serial-unknown"])), expected_refusal=("/hardware_identity_coverage/components/0/serial_status", "const")),
    Case("asset-detects-complete-count-mismatch", "asset", semantic="invalid", mutate=set_path("hardware_identity_coverage.expected_component_count", 3), expected_semantic="complete expected count must equal enumerated components"),
    Case("asset-detects-complete-identity-mismatch", "asset", semantic="invalid", mutate=set_path("hardware_identity_coverage.expected_component_ids.1", "load-cell-c"), expected_semantic="complete expected identities must equal observed identities"),
    Case("asset-rejects-unknown-hardware-in-force", "asset", structural="invalid", mutate=compose(set_path("hardware_identity_coverage.status", "unknown"), set_path("hardware_identity_coverage.reason_codes", ["hardware-unknown"])), expected_refusal=("/applicability_disposition", "enum")),
    Case("asset-allows-zero-observed-only-while-blocked", "asset", semantic="valid", fixture="asset-configuration-snapshot.inbar-blocked.valid.json"),
    Case("asset-rejects-offset-effective-time", "asset", structural="invalid", mutate=set_path("effective_interval.effective_from", "2026-07-16T10:00:00.000000+03:00"), expected_refusal=("/effective_interval/effective_from", "pattern")),
    Case("asset-rejects-nonmicrosecond-effective-time", "asset", structural="invalid", mutate=set_path("effective_interval.effective_until", "2026-08-16T07:00:00Z"), expected_refusal=("/effective_interval/effective_until", "oneOf")),

    Case("measurement-valid-physical-world-result", "measurement", semantic="valid", fixture="physical-measurement-result.valid.json"),
    Case("measurement-rejects-measured-with-missing-raw-signal", "measurement", structural="invalid", mutate=set_path("raw_signal.status", "missing"), expected_refusal=("/raw_signal/artifact_ref", "type")),
    Case("measurement-rejects-valid-with-unknown-firmware", "measurement", structural="invalid", mutate=compose(set_path("instrument.firmware.status", "unknown"), set_path("instrument.firmware.version", None), set_path("instrument.firmware.image_ref", None), set_path("instrument.firmware.reason_codes", ["firmware-unknown"])), expected_refusal=("/instrument/firmware/status", "enum")),
    Case("measurement-rejects-calibration-relabeled-validation", "measurement", structural="invalid", mutate=set_path("calibration_traceability.evidence_role", "physical_validation"), expected_refusal=("/calibration_traceability/evidence_role", "const")),
    Case("measurement-rejects-valid-detected-saturation", "measurement", structural="invalid", mutate=set_path("quality_flags.saturation.disposition", "detected"), expected_refusal=("/quality_flags/saturation/disposition", "enum")),
    Case("measurement-detects-reversed-calibration-validity", "measurement", semantic="invalid", mutate=set_path("calibration_traceability.expires_at", "2026-06-01T00:00:00.000000Z"), expected_semantic="effective_at must precede expires_at"),
    Case("measurement-rejects-unavailable-result-with-stale-measured-refs", "measurement", structural="invalid", mutate=measurement_unavailable_with_stale_refs, expected_refusal=("/measured_quantity_ref", "type")),
    Case("measurement-rejects-offset-recorded-time", "measurement", structural="invalid", mutate=set_path("recorded_at", "2026-07-16T11:05:00.000000+03:00"), expected_refusal=("/recorded_at", "pattern")),
    Case("measurement-rejects-nonmicrosecond-calibration-time", "measurement", structural="invalid", mutate=set_path("calibration_traceability.effective_at", "2026-07-01T00:00:00Z"), expected_refusal=("/calibration_traceability/effective_at", "pattern")),

    Case("model-valid-independent-calibration-and-validation", "model", semantic="valid", fixture="physical-model-record.valid.json"),
    Case("model-detects-overlapping-calibration-validation-data", "model", semantic="invalid", mutate=partition_overlap, expected_semantic="calibration and validation measurement partitions must be disjoint"),
    Case("model-detects-shared-independence-group", "model", semantic="invalid", mutate=set_path("validation_partition.independence_group_id", "independence.calibration"), expected_semantic="require distinct independence groups"),
    Case("model-rejects-simulation-validation-partition", "model", structural="invalid", mutate=set_path("validation_partition.data_origin", "simulation"), expected_refusal=("/validation_partition/data_origin", "const")),
    Case("model-rejects-simulation-as-physical-validation", "model", structural="invalid", mutate=set_path("physical_validation.evidence_origin", "simulation"), expected_refusal=("/physical_validation/evidence_origin", "const")),
    Case("model-rejects-calibration-or-simulation-substitution", "model", structural="invalid", mutate=set_path("physical_validation.calibration_or_simulation_substitution_permitted", True), expected_refusal=("/physical_validation/calibration_or_simulation_substitution_permitted", "const")),
    Case("model-rejects-code-verification-as-physical-validation", "model", structural="invalid", mutate=set_path("code_verification.evidence_origin", "independent_physical_world_measurement"), expected_refusal=("/code_verification/evidence_origin", "const")),
    Case("model-detects-physical-validation-partition-ref-mismatch", "model", semantic="invalid", mutate=set_path("physical_validation.validation_partition_id", "partition.calibration"), expected_semantic="validation_partition_id mismatch"),

    Case("evidence-valid-exact-ten-vector-and-p0-p12", "evidence", semantic="valid", fixture="physical-evidence-vector.valid.json"),
    Case("evidence-rejects-missing-credibility-component", "evidence", structural="invalid", mutate=delete_path("credibility_vector.safety_case"), expected_refusal=("/credibility_vector", "required")),
    Case("evidence-rejects-missing-p12", "evidence", structural="invalid", mutate=delete_path("vvuq_gates.p12_release"), expected_refusal=("/vvuq_gates", "required")),
    Case("evidence-rejects-simulation-as-world", "evidence", structural="invalid", mutate=set_path("credibility_vector.physical_validation.evidence_origin", "simulation"), expected_refusal=("/credibility_vector/physical_validation/evidence_origin", "const")),
    Case("evidence-rejects-calibration-as-validation", "evidence", structural="invalid", mutate=set_path("credibility_vector.physical_validation.evidence_origin", "calibration_partition"), expected_refusal=("/credibility_vector/physical_validation/evidence_origin", "const")),
    Case("evidence-rejects-validation-substitution", "evidence", structural="invalid", mutate=set_path("credibility_vector.physical_validation.calibration_or_simulation_substitution_permitted", True), expected_refusal=("/credibility_vector/physical_validation/calibration_or_simulation_substitution_permitted", "const")),
    Case("evidence-rejects-eligible-vector-with-p7-fail", "evidence", structural="invalid", mutate=compose(set_path("vvuq_gates.p7_physical_validation.disposition", "fail"), set_path("vvuq_gates.p7_physical_validation.reason_codes", ["validation-failed"])), expected_refusal=("/vvuq_gates/p7_physical_validation/disposition", "const")),
    Case("evidence-rejects-scalar-confidence-collapse", "evidence", structural="invalid", mutate=set_path("scalar_confidence", "0.99"), expected_refusal=("/", "additionalProperties")),
    Case("evidence-detects-validation-measurement-outside-record-scope", "evidence", semantic="invalid", mutate=evidence_ref_outside_scope, expected_semantic="physical measurements must be declared at record scope"),

    Case("safety-valid-recommendation-only-envelope", "safety", semantic="valid", fixture="safety-envelope.valid.json"),
    Case("safety-rejects-unknown-hardware-as-supported", "safety", structural="invalid", mutate=set_path("asset_hardware_coverage_observation", "unknown"), expected_refusal=("/envelope_disposition", "enum")),
    Case("safety-rejects-direct-actuation", "safety", structural="invalid", mutate=set_path("actuator_boundary.direct_actuation_permitted", True), expected_refusal=("/actuator_boundary/direct_actuation_permitted", "const")),
    Case("safety-rejects-self-granted-actuator-authority", "safety", structural="invalid", mutate=set_path("actuator_boundary.actuator_authority_granted", True), expected_refusal=("/actuator_boundary/actuator_authority_granted", "const")),
    Case("safety-rejects-inline-execution-authority", "safety", structural="invalid", mutate=set_path("actuator_boundary.execution_authority_ref", record("authority.inline", "urn:odeya:schema:authority-grant:0.7.0", "5")), expected_refusal=("/actuator_boundary/execution_authority_ref", "type")),
    Case("safety-rejects-hard-guarantee-from-chance-constraint", "safety", structural="invalid", mutate=set_path("safe_set.hard_guarantee_claimed", True), expected_refusal=("/safe_set/hard_guarantee_claimed", "const")),
    Case("safety-detects-reversed-validity", "safety", semantic="invalid", mutate=set_path("validity.expires_at", "2026-07-15T00:00:00.000000Z"), expected_semantic="valid_from must precede expires_at"),
    Case("safety-rejects-offset-validity-time", "safety", structural="invalid", mutate=set_path("validity.valid_from", "2026-07-16T03:00:00.000000+03:00"), expected_refusal=("/validity/valid_from", "pattern")),
    Case("safety-rejects-nonmicrosecond-validity-time", "safety", structural="invalid", mutate=set_path("validity.expires_at", "2026-08-16T00:00:00Z"), expected_refusal=("/validity/expires_at", "pattern")),

    Case("experiment-valid-six-axis-preflight", "experiment", semantic="valid"),
    Case("experiment-valid-inbar-unknown-hardware-refusal", "experiment", semantic="valid", fixture="physical-experiment-contract.inbar-refused.valid.json"),
    Case("experiment-rejects-unknown-hardware-as-eligible", "experiment", structural="invalid", mutate=compose(set_path("asset_binding.hardware_identity_coverage_observation", "unknown"), set_path("asset_binding.reason_codes", ["hardware-unknown"])), expected_refusal=("/planning_disposition", "enum")),
    Case("experiment-rejects-indeterminate-measurement-preflight-as-eligible", "experiment", structural="invalid", mutate=compose(set_path("preflight.measurement_capability.disposition", "indeterminate"), set_path("preflight.measurement_capability.reason_codes", ["measurement-indeterminate"])), expected_refusal=("/preflight/measurement_capability/disposition", "const")),
    Case("experiment-rejects-failed-safety-preflight-as-eligible", "experiment", structural="invalid", mutate=compose(set_path("preflight.safety.disposition", "fail"), set_path("preflight.safety.reason_codes", ["safety-failed"])), expected_refusal=("/preflight/safety/disposition", "const")),
    Case("experiment-rejects-simulation-validation-partition", "experiment", structural="invalid", mutate=set_path("independent_validation_partition.data_origin", "simulation"), expected_refusal=("/independent_validation_partition/data_origin", "const")),
    Case("experiment-rejects-direct-actuation", "experiment", structural="invalid", mutate=set_path("authority_boundary.direct_actuation_permitted", True), expected_refusal=("/authority_boundary/direct_actuation_permitted", "const")),
    Case("experiment-rejects-self-issued-authority", "experiment", structural="invalid", mutate=set_path("authority_boundary.authority_self_issued", True), expected_refusal=("/authority_boundary/authority_self_issued", "const")),
    Case("experiment-rejects-inline-execution-authority", "experiment", structural="invalid", mutate=set_path("authority_boundary.execution_authority_ref", record("authority.inline", "urn:odeya:schema:authority-grant:0.7.0", "5")), expected_refusal=("/authority_boundary/execution_authority_ref", "type")),
    Case("experiment-rejects-required-causal-check-marked-na", "experiment", structural="invalid", mutate=set_path("preflight.causal_identification.disposition", "not_applicable"), expected_refusal=("/preflight/causal_identification/disposition", "enum")),

    Case("verification-valid-resolved-physical-iv4-scope", "verification", semantic="valid"),
    Case("verification-detects-unresolved-physical-subject", "verification", semantic="invalid", mutate=set_path("subject_set.subjects.0.subject_id", "physical-evidence.unresolved"), expected_semantic="subject must resolve to the exact typed physical evidence vector"),
    Case("verification-detects-subject-mission-mismatch", "verification", semantic="invalid", mutate=set_path("mission_id", "mission.other"), expected_semantic="must equal the resolved physical subject mission"),
    Case("verification-detects-untyped-selection-rule", "verification", semantic="invalid", mutate=set_path("subject_set.selection_rule_ref.record_id", "subject-selection-rule.generic"), expected_semantic="must select the physical-validity and safety predicates"),
    Case("verification-rejects-physical-scope-below-iv4", "verification", semantic="invalid", mutate=set_path("frozen_assignment.required_verification_class", "IV3_independent_reimplementation"), expected_semantic="resolved physical replication scope requires IV4"),
    Case("verification-rejects-iv4-paired-with-no-physical-assertion", "verification", semantic="invalid", mutate=set_path("dimensions.physical_validity.scope", "No physical-world assertion"), expected_semantic="must be required/pass for the resolved physical predicate"),
    Case("verification-rejects-physical-validity-not-required", "verification", semantic="invalid", mutate=compose(set_path("dimensions.physical_validity.requirement", "not_required"), set_path("dimensions.physical_validity.verdict", "not_applicable"), set_path("dimensions.physical_validity.evidence_refs", []), set_path("dimensions.physical_validity.limitation_codes", ["physical-validity-not-required"])), expected_semantic="must be required/pass for the resolved physical predicate"),
    Case("verification-rejects-safety-bound-scope-as-not-required", "verification", semantic="invalid", mutate=compose(set_path("dimensions.safety.requirement", "not_required"), set_path("dimensions.safety.verdict", "not_applicable"), set_path("dimensions.safety.evidence_refs", []), set_path("dimensions.safety.limitation_codes", ["safety-not-required"])), expected_semantic="selected safety-bound recommendation requires an applicable passing safety dimension"),
    Case("verification-rejects-overclaiming-terminal-language", "verification", semantic="invalid", mutate=set_path("terminal_assessment.scope_statement", "The synthetic fixture authorizes a physical action."), expected_semantic="confirmation language must equal the resolver-derived bounded statement"),
    Case("verification-requires-synthetic-evidence-boundary", "verification", semantic="invalid", mutate=set_path("terminal_assessment.reason_codes", ["required_dimensions_passed"]), expected_semantic="synthetic evidence boundary must remain explicit"),
]


def collect_schema_id_consts(node: object) -> set[str]:
    found: set[str] = set()
    if isinstance(node, dict):
        schema_id = node.get("schema_id")
        if isinstance(schema_id, dict) and isinstance(schema_id.get("const"), str):
            found.add(schema_id["const"])
        for value in node.values():
            found.update(collect_schema_id_consts(value))
    elif isinstance(node, list):
        for value in node:
            found.update(collect_schema_id_consts(value))
    return found


def collect_nodes(node: object) -> list[dict[str, object]]:
    found: list[dict[str, object]] = []
    if isinstance(node, dict):
        found.append(node)
        for value in node.values():
            found.extend(collect_nodes(value))
    elif isinstance(node, list):
        for value in node:
            found.extend(collect_nodes(value))
    return found


def check_lexical_profiles(schemas: dict[str, dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for kind, schema in schemas.items():
        definitions = schema.get("$defs", {})
        decimal = definitions.get("decimal") if isinstance(definitions, dict) else None
        if decimal is not None and decimal.get("pattern") != EXPECTED_DECIMAL_PATTERN:
            errors.append(f"{kind}: decimal definition diverges from no-negative-zero profile")
        for node in collect_nodes(schema):
            if node.get("format") == "date-time" and node.get("pattern") != EXPECTED_UTC_PATTERN:
                errors.append(f"{kind}: unprofiled date-time node")
    return errors


EXACT_FIXTURES: dict[str, tuple[str, Callable[[], dict[str, object]]]] = {
    "physical-quantity.valid.json": ("quantity", quantity),
    "uncertainty-budget.valid.json": ("uncertainty", uncertainty),
    "asset-configuration-snapshot.inbar-blocked.valid.json": ("asset", inbar_asset_blocked),
    "physical-measurement-result.valid.json": ("measurement", measurement),
    "physical-model-record.valid.json": ("model", model),
    "physical-evidence-vector.valid.json": ("evidence", evidence),
    "safety-envelope.valid.json": ("safety", safety),
    "physical-experiment-contract.inbar-refused.valid.json": ("experiment", inbar_experiment_refused),
}


def check_dependency_dag(schemas: dict[str, dict[str, object]]) -> list[str]:
    errors: list[str] = []
    urn_to_key = {urn: key for key, urn in SCHEMA_URNS.items()}
    positions = {key: index for index, key in enumerate(DEPENDENCY_ORDER)}
    for key, schema in schemas.items():
        dependencies = {urn_to_key[urn] for urn in collect_schema_id_consts(schema) if urn in urn_to_key}
        if key in dependencies:
            errors.append(f"{key}: self-dependency")
        for dependency in dependencies:
            if positions[dependency] >= positions[key]:
                errors.append(f"{key}: non-backward dependency on {dependency}")
    return errors


def structural_attribution_failures(case: "Case", errors: list) -> list[str]:
    if case.expected_refusal is None:
        return [f"{case.name}: known-bad case does not declare the constraint that must refuse it"]
    pointer, keyword = case.expected_refusal
    if not any(
        "/" + "/".join(str(part) for part in error.absolute_path) == pointer
        and error.validator == keyword
        for error in errors
    ):
        observed = [
            ("/" + "/".join(str(part) for part in error.absolute_path), error.validator)
            for error in errors
        ]
        return [
            f"{case.name}: refused, but not at its declared constraint "
            f"{pointer!r} by {keyword!r}; got {observed}"
        ]
    return []


def semantic_attribution_failures(case: "Case", semantic_errors: list[str]) -> list[str]:
    if not case.expected_semantic:
        return [f"{case.name}: semantic known-bad case does not declare the check that must refuse it"]
    if not any(case.expected_semantic in error for error in semantic_errors):
        return [
            f"{case.name}: semantically refused, but not by its declared check "
            f"{case.expected_semantic!r}; got {semantic_errors}"
        ]
    return []


def attribution_self_test_meta_proof(validators: dict[str, Draft202012Validator]) -> list[str]:
    """Prove the self-test's own refusals are load-bearing (ADR 0069/0080)."""
    blind = lambda *args, **kw: []  # noqa: E731 - a binding check that refuses nothing
    distinct = {f for f in attribution_self_test(validators, struct_check=blind, sem_check=blind)}
    if len(distinct) != 4:
        return [
            f"attribution meta self-test: blinding the binding checks produced {len(distinct)} "
            "distinct refusals, expected 4; a self-test refusal is not load-bearing"
        ]
    return []


def attribution_self_test(validators: dict[str, Draft202012Validator],
                          struct_check=None, sem_check=None) -> list[str]:
    """Prove on every run that both binding checks fire (law 11)."""
    sc = struct_check or structural_attribution_failures
    mc = sem_check or semantic_attribution_failures
    failures: list[str] = []
    structural = next((c for c in CASES if c.structural == "invalid"), None)
    semantic = next((c for c in CASES if c.structural == "valid" and c.semantic == "invalid"), None)
    if structural is None or semantic is None:
        return ["attribution self-test found no known-bad case to tamper with"]
    subject = copy.deepcopy(load(FIXTURES / structural.fixture) if structural.fixture else FACTORIES[structural.kind]())
    if structural.mutate:
        structural.mutate(subject)
    errors = sorted(validators[structural.kind].iter_errors(subject), key=lambda item: list(item.path))
    misdeclared = dataclasses.replace(structural, expected_refusal=("/odeya-self-test/never-fires", "const"))
    if not any("refused, but not at its declared constraint" in f
               for f in sc(misdeclared, errors)):
        failures.append("attribution self-test: a misdeclared structural constraint was not detected")
    undeclared = dataclasses.replace(structural, expected_refusal=None)
    if not any("does not declare the constraint" in f
               for f in sc(undeclared, errors)):
        failures.append("attribution self-test: a missing structural declaration was not detected")
    subject = copy.deepcopy(load(FIXTURES / semantic.fixture) if semantic.fixture else FACTORIES[semantic.kind]())
    if semantic.mutate:
        semantic.mutate(subject)
    semantic_errors = SEMANTIC_CHECKERS[semantic.kind](subject)
    misdeclared = dataclasses.replace(semantic, expected_semantic="odeya-self-test-never-appears")
    if not any("not by its declared check" in f
               for f in mc(misdeclared, semantic_errors)):
        failures.append("attribution self-test: a misdeclared semantic check was not detected")
    undeclared = dataclasses.replace(semantic, expected_semantic=None)
    if not any("does not declare the check" in f
               for f in mc(undeclared, semantic_errors)):
        failures.append("attribution self-test: a missing semantic declaration was not detected")
    return failures


def main() -> int:
    failures: list[str] = []
    manifest = load(CASE_MANIFEST)
    assert isinstance(manifest, dict)
    declared_cases = manifest.get("cases")
    expected_cases = [
        {
            "name": case.name,
            "schema": SCHEMAS[case.kind],
            "base": case.fixture or f"bounded_factory:{case.kind}",
            "structural_expect": case.structural,
            **({"semantic_expect": case.semantic} if case.semantic is not None else {}),
            **(
                {"expected_refusal": {"pointer": case.expected_refusal[0], "keyword": case.expected_refusal[1]}}
                if case.expected_refusal is not None
                else {}
            ),
            **(
                {"expected_semantic_refusal_contains": case.expected_semantic}
                if case.expected_semantic is not None
                else {}
            ),
        }
        for case in CASES
    ]
    if declared_cases != expected_cases:
        failures.append("cases.json does not exactly inventory the executable case catalog")
    if manifest.get("expected_case_count") != len(CASES):
        failures.append("cases.json expected_case_count does not match executable case count")
    schemas: dict[str, dict[str, object]] = {}
    validators: dict[str, Draft202012Validator] = {}
    for kind, relative_path in SCHEMAS.items():
        schema = load(ROOT / relative_path)
        assert isinstance(schema, dict)
        Draft202012Validator.check_schema(schema)
        schemas[kind] = schema
        validators[kind] = Draft202012Validator(schema, format_checker=FormatChecker())
    failures.extend(check_dependency_dag(schemas))
    failures.extend(check_lexical_profiles(schemas))
    for fixture_name, (kind, expected_factory) in EXACT_FIXTURES.items():
        exact_fixture = load(FIXTURES / fixture_name)
        if exact_fixture != expected_factory():
            failures.append(f"{fixture_name}: persisted fixture drifted from its bounded constructor")
            continue
        fixture_errors = list(validators[kind].iter_errors(exact_fixture))
        if fixture_errors:
            failures.append(f"{fixture_name}: persisted fixture is structurally invalid: {fixture_errors[0].message}")

    semantic_expectations = 0
    for case in CASES:
        if case.fixture:
            subject = load(FIXTURES / case.fixture)
            assert isinstance(subject, dict)
        else:
            subject = FACTORIES[case.kind]()
        subject = copy.deepcopy(subject)
        if case.mutate:
            try:
                case.mutate(subject)
            except (KeyError, IndexError, TypeError) as exc:
                failures.append(
                    f"{case.name}: mutation could not be applied to the current "
                    f"subject shape: {type(exc).__name__}: {exc}"
                )
                continue
        structural_errors = sorted(validators[case.kind].iter_errors(subject), key=lambda item: list(item.path))
        actual_structural = "invalid" if structural_errors else "valid"
        if actual_structural != case.structural:
            detail = structural_errors[0].message if structural_errors else "unexpectedly accepted"
            failures.append(
                f"{case.name}: expected structural {case.structural}, got {actual_structural}: {detail}"
            )
            continue
        if case.structural == "invalid":
            failures.extend(structural_attribution_failures(case, structural_errors))
        if case.semantic is not None:
            semantic_expectations += 1
            if structural_errors:
                failures.append(f"{case.name}: semantic expectation requires structural validity")
                continue
            semantic_errors = SEMANTIC_CHECKERS[case.kind](subject)
            actual_semantic = "invalid" if semantic_errors else "valid"
            if actual_semantic != case.semantic:
                detail = semantic_errors[0] if semantic_errors else "unexpectedly accepted"
                failures.append(
                    f"{case.name}: expected semantic {case.semantic}, got {actual_semantic}: {detail}"
                )
            if case.semantic == "invalid":
                failures.extend(semantic_attribution_failures(case, semantic_errors))

    failures.extend(attribution_self_test(validators))
    failures.extend(attribution_self_test_meta_proof(validators))

    if failures:
        print("physical-contract checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        f"physical-contract checks passed: {len(CASES)} structural expectations, "
        f"{semantic_expectations} local-semantic expectations, {len(SCHEMAS)}-schema DAG"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
