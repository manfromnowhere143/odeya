#!/usr/bin/env python3
"""Run isolated structural and bounded semantic projection-contract checks.

Passing this checker does not establish canonical truth, evidence, authority,
publication eligibility, external visibility, runtime correctness,
noninterference, or Gate A acceptance.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tests/projection-contracts/cases.json"
SCHEMAS = (
    "schemas/projection-snapshot.schema.json",
    "schemas/projection-redaction-manifest.schema.json",
    "schemas/reducer-equivalence-result.schema.json",
    "schemas/projection-impact-record.schema.json",
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

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutate(instance: Any, mutations: list[dict[str, Any]]) -> Any:
    result = json.loads(json.dumps(instance))
    for mutation in mutations:
        operation = mutation["op"]
        tokens = pointer_tokens(str(mutation["path"]))
        parent = result
        for token in tokens[:-1]:
            parent = parent[int(token)] if isinstance(parent, list) else parent[token]
        final = tokens[-1]
        if isinstance(parent, list):
            index = int(final)
            if operation == "add":
                parent.insert(index, mutation.get("value"))
            elif operation == "remove":
                del parent[index]
            elif operation == "replace":
                parent[index] = mutation["value"]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        elif isinstance(parent, dict):
            if operation == "add":
                if final in parent:
                    raise ValueError(f"add target already exists: {final!r}")
                parent[final] = mutation.get("value")
            elif operation == "remove":
                del parent[final]
            elif operation == "replace":
                if final not in parent:
                    raise KeyError(final)
                parent[final] = mutation["value"]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        else:
            raise TypeError("mutation parent is not a container")
    return result


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ref_key(ref: Any) -> tuple[Any, ...]:
    if not isinstance(ref, dict):
        return (None,)
    if "record_id" in ref:
        return (
            ref.get("record_type"),
            ref.get("record_id"),
            ref.get("version"),
            ref.get("schema_id"),
            ref.get("canonical_digest"),
        )
    if "artifact_id" in ref:
        return (ref.get("artifact_id"), ref.get("digest"), ref.get("media_type"))
    if "id" in ref:
        return (ref.get("id"), ref.get("version"), ref.get("digest"))
    return tuple(sorted(ref.items()))


def point_key(point: Any) -> tuple[Any, ...]:
    if not isinstance(point, dict):
        return (None,)
    return (
        point.get("ledger_epoch"),
        point.get("stream_id"),
        point.get("inclusive_global_position"),
        point.get("aggregate_id"),
        point.get("aggregate_version"),
    )


def snapshot_semantics(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    projection_type = instance["projection_type"]
    source_kind = instance["source"]["source_kind"]
    axes = instance["semantic_axes"]
    surface = instance["surface"]

    if surface["surface_type"] != projection_type:
        errors.append("surface type does not equal projection discriminator")
    if axes["source_fixture"] != source_kind:
        errors.append("source/fixture axis does not equal exact source kind")

    freshness = instance["freshness"]
    dependency = instance["dependency_frontier"]
    generated_at = parse_time(instance["controlled_time"]["generated_at"])
    if freshness["state"] == "current":
        if projection_type != "static_architecture_fixture":
            required = dependency["required_position"]
            included = dependency["included_position"]
            if point_key(required) != point_key(included):
                errors.append("current snapshot required and included frontiers differ")
            checkpoint = instance["canonical_bindings"]["ledger_checkpoint"]
            if point_key(checkpoint["ledger_point"]) != point_key(included):
                errors.append("current snapshot checkpoint and included frontier differ")
            if checkpoint["witness_status"] != "acknowledged":
                errors.append("current live snapshot checkpoint is not witness acknowledged")
            if dependency["age_seconds"] > dependency["maximum_age_seconds"]:
                errors.append("current dependency observation exceeds maximum age")
            checked_at = parse_time(dependency["checked_at"])
            valid_until = parse_time(dependency["valid_until"])
            if not checked_at <= generated_at < valid_until:
                errors.append("current dependency observation lease does not cover generation time")

            governance = instance["governance_frontier"]
            rights = governance["rights"]
            if not parse_time(rights["effective_at"]) <= generated_at < parse_time(rights["expires_at"]):
                errors.append("current rights lease does not cover generation time")
            serve = governance["serve_decision"]
            if not parse_time(serve["checked_at"]) <= generated_at < parse_time(serve["valid_until"]):
                errors.append("current serve lease does not cover generation time")
            if ref_key(serve["audience_scope_ref"]) != ref_key(instance["audience"]["audience_scope_ref"]):
                errors.append("serve audience reference differs from projection audience")
            if ref_key(serve["purpose_scope_ref"]) != ref_key(instance["purpose"]["purpose_scope_ref"]):
                errors.append("serve purpose reference differs from projection purpose")
        elif source_kind != "static_architecture_fixture":
            errors.append("static current exception used with a live source")

    completeness = instance["completeness"]
    if completeness["state"] == "complete":
        if set(completeness["expected_sections"]) != set(completeness["present_sections"]):
            errors.append("complete projection expected/present section sets differ")
        if (
            completeness["omitted_section_ids"]
            or completeness["unsupported_version_refs"]
            or completeness["unavailable_artifact_refs"]
        ):
            errors.append("complete projection carries omissions or unavailable dependencies")

    for index, quantity in enumerate(instance["quantitative_displays"]):
        numeric_value = quantity["numeric_value"]
        if numeric_value is not None:
            try:
                Decimal(governed_decimal(numeric_value))
            except (InvalidOperation, TypeError, ValueError):
                errors.append(f"quantitative_displays[{index}] numeric value is not an exact decimal string")
        interval = quantity["interval"]
        if interval is None:
            continue
        try:
            lower = Decimal(governed_decimal(interval["lower"]))
            upper = Decimal(governed_decimal(interval["upper"]))
        except (InvalidOperation, TypeError, ValueError):
            errors.append(f"quantitative_displays[{index}] interval is not exact decimal strings")
            continue
        if lower > upper:
            errors.append(f"quantitative_displays[{index}] interval lower exceeds upper")
            continue
        actual_contains_zero = lower <= Decimal("0") <= upper
        if interval["contains_zero"] != actual_contains_zero:
            errors.append(f"quantitative_displays[{index}] contains-zero flag disagrees with exact decimals")
        if actual_contains_zero and quantity["rendered_semantic"] != "range_includes_zero":
            errors.append(f"quantitative_displays[{index}] interval crossing zero loses neutral semantics")

    if projection_type == "thesis_intake":
        namespace = surface["noninterference"]["namespace"]
        if namespace["proposal_id"] != instance["subject"]["logical_subject_id"]:
            errors.append("thesis cache namespace proposal differs from projected proposal")
        if namespace["proposal_id"] != surface["proposal_ref"]["record_id"]:
            errors.append("thesis surface proposal reference differs from cache namespace")
        if namespace["purpose_id"] != instance["purpose"]["purpose_id"]:
            errors.append("thesis cache namespace purpose differs from projection purpose")

    if projection_type == "public_research":
        chain = surface["release_chain"]
        governance = instance["governance_frontier"]
        if ref_key(chain["effect_observation_ref"]) != ref_key(governance["external_effect"]["observation_ref"]):
            errors.append("public release chain effect observation differs from governance frontier")
        if ref_key(chain["release_settlement_event_ref"]) != ref_key(governance["release"]["settlement_event_ref"]):
            errors.append("public release settlement reference differs from governance frontier")
        if ref_key(chain["data_use_decision_ref"]) != ref_key(governance["rights"]["decision_ref"]):
            errors.append("public disclosure decision differs from serve-time rights frontier")
        if chain["effect_state"] != governance["external_effect"]["state"]:
            errors.append("public release effect state differs from governance frontier")
        expected_publication = {
            "release_settled": "released",
            "corrected": "corrected",
            "withdrawn": "withdrawn",
        }.get(governance["release"]["state"])
        if axes["publication"] != expected_publication:
            errors.append("public publication axis differs from release-settled state")

    return errors


def redaction_semantics(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expiry = instance["expiry_and_review"]
    compiled_at = parse_time(expiry["compiled_at"])
    if compiled_at != parse_time(instance["compiler"]["compiled_at"]):
        errors.append("redaction compiler and lease compilation times differ")
    if not compiled_at < parse_time(expiry["valid_until"]):
        errors.append("redaction lease is not valid after compilation")
    if not compiled_at <= parse_time(expiry["review_at"]) <= parse_time(expiry["valid_until"]):
        errors.append("redaction review time falls outside compilation lease")

    partition = instance["object_partition"]
    expected = {ref_key(ref) for ref in partition["expected_source_refs"]}
    covered = {ref_key(item["source_ref"]) for item in partition["included"]}
    covered.update(ref_key(item["source_ref"]) for item in partition["withheld"])
    if expected != covered:
        errors.append("redaction included/withheld source partition does not cover expected sources exactly")

    limitations = instance["scientific_limitation_preservation"]
    required = {ref_key(ref) for ref in limitations["required_limitation_refs"]}
    included = {ref_key(ref) for ref in limitations["included_limitation_refs"]}
    withheld = {ref_key(ref) for ref in limitations["withheld_required_limitation_refs"]}
    if not required.issubset(included) or required & withheld:
        errors.append("required scientific limitations are not fully and visibly preserved")
    return errors


def equivalence_semantics(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if ref_key(instance["path_a"]["implementation_ref"]) == ref_key(instance["path_b"]["implementation_ref"]):
        errors.append("reducer paths use the same implementation identity")
    if instance["path_a"]["build_digest"] == instance["path_b"]["build_digest"]:
        errors.append("reducer paths use the same build digest")
    if parse_time(instance["controlled_time"]["completed_at"]) < parse_time(instance["controlled_time"]["started_at"]):
        errors.append("reducer equivalence completed before it started")

    comparison = instance["comparison"]
    if comparison["disposition"] == "passed":
        if point_key(instance["source_binding"]["required_frontier"]) != point_key(instance["source_binding"]["included_frontier"]):
            errors.append("passing reducer comparison binds different required/included frontiers")
        if comparison["semantic_vector_a_digest"] != comparison["semantic_vector_b_digest"]:
            errors.append("passing reducer comparison has different semantic-vector digests")
        if any(item["result"] != "pass" for item in instance["perturbations"]):
            errors.append("passing reducer comparison contains a failed perturbation")
    if comparison["disposition"] == "not_run" and instance["projection_target"]["projection_type"] != "static_architecture_fixture":
        errors.append("not-run reducer comparison used by a live projection")
    return errors


def impact_semantics(instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    selection = instance["selection"]
    if selection["affected_projection_count"] != len(selection["affected"]):
        errors.append("impact affected count does not equal affected set length")
    if selection["unaffected_projection_count"] != len(selection["unaffected"]):
        errors.append("impact unaffected count does not equal unaffected set length")
    if selection["candidate_projection_count"] != len(selection["affected"]) + len(selection["unaffected"]):
        errors.append("impact candidate count does not reconcile")
    affected_ids = {(item["projection_id"], item["projection_version"]) for item in selection["affected"]}
    unaffected_ids = {(item["projection_id"], item["projection_version"]) for item in selection["unaffected"]}
    if affected_ids & unaffected_ids:
        errors.append("projection appears in both affected and unaffected sets")
    family_types = set(instance["projection_family"]["projection_types"])
    if any(item["projection_type"] not in family_types for item in selection["affected"] + selection["unaffected"]):
        errors.append("impact member falls outside declared projection family")
    trigger_position = instance["trigger"]["ledger_position"]["inclusive_global_position"]
    checkpoint_position = instance["source_binding"]["checkpoint_ledger_position"]["inclusive_global_position"]
    if trigger_position < checkpoint_position:
        errors.append("impact trigger predates the bound checkpoint frontier")
    if instance["trigger"]["deletion_retention_disposition"] == "minimum_noncontent_tombstone_only":
        for item in selection["affected"]:
            if item["prior_projection_bytes_retained"]:
                errors.append("tombstone-only deletion retains prior projection bytes")
            if item["retention_action"] != "destroy_prior_bytes_keep_minimum_noncontent_tombstone":
                errors.append("tombstone-only deletion lacks destructive retention action")
    return errors


def semantic_errors(schema_path: str, instance: Any) -> list[str]:
    if not isinstance(instance, dict):
        return ["semantic subject must be an object"]
    if schema_path == "schemas/projection-snapshot.schema.json":
        return snapshot_semantics(instance)
    if schema_path == "schemas/projection-redaction-manifest.schema.json":
        return redaction_semantics(instance)
    if schema_path == "schemas/reducer-equivalence-result.schema.json":
        return equivalence_semantics(instance)
    if schema_path == "schemas/projection-impact-record.schema.json":
        return impact_semantics(instance)
    return [f"no semantic checker registered for {schema_path}"]


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def schema_audit() -> list[str]:
    errors: list[str] = []
    expected_ids = {
        "schemas/projection-snapshot.schema.json": "urn:odeya:schema:projection-snapshot:0.3.0",
        "schemas/projection-redaction-manifest.schema.json": "urn:odeya:schema:projection-redaction-manifest:0.2.0",
        "schemas/reducer-equivalence-result.schema.json": "urn:odeya:schema:reducer-equivalence-result:0.2.0",
        "schemas/projection-impact-record.schema.json": "urn:odeya:schema:projection-impact-record:0.2.0",
    }
    forbidden_digest_properties = {
        "projection_digest",
        "snapshot_digest",
        "package_digest",
        "enclosing_digest",
        "canonical_projection_digest",
    }
    for schema_path in SCHEMAS:
        schema = load_json(ROOT / schema_path)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # pragma: no cover - printed as a checker failure
            errors.append(f"{schema_path}: invalid JSON Schema: {exc}")
            continue
        if schema.get("$id") != expected_ids[schema_path]:
            errors.append(f"{schema_path}: unexpected schema ID")
        for item in walk(schema):
            ref = item.get("$ref")
            if isinstance(ref, str) and not ref.startswith("#/"):
                errors.append(f"{schema_path}: external schema reference breaks isolated closure: {ref}")
            properties = item.get("properties")
            if isinstance(properties, dict):
                bad = forbidden_digest_properties & set(properties)
                if bad:
                    errors.append(f"{schema_path}: recursive/enclosing digest property declared: {sorted(bad)}")
    return errors


def package_semantics() -> list[str]:
    errors: list[str] = []
    fixtures = ROOT / "tests/projection-contracts/fixtures"
    snapshot = load_json(fixtures / "private-cockpit.valid.json")
    redaction = load_json(fixtures / "projection-redaction-manifest.valid.json")
    equivalence = load_json(fixtures / "reducer-equivalence-live.valid.json")
    impact = load_json(fixtures / "projection-impact-record.valid.json")
    static_snapshot = load_json(fixtures / "static-architecture-fixture.valid.json")
    static_equivalence = load_json(fixtures / "reducer-equivalence-static.valid.json")

    target = (snapshot["projection_id"], snapshot["version"], snapshot["projection_type"])
    if target != (
        redaction["projection_target"]["projection_id"],
        redaction["projection_target"]["projection_version"],
        redaction["projection_target"]["projection_type"],
    ):
        errors.append("private snapshot and redaction manifest target identities differ")
    if target != (
        equivalence["projection_target"]["projection_id"],
        equivalence["projection_target"]["projection_version"],
        equivalence["projection_target"]["projection_type"],
    ):
        errors.append("private snapshot and equivalence result target identities differ")
    if snapshot["redaction_manifest_ref"]["record_id"] != redaction["manifest_id"]:
        errors.append("private snapshot redaction reference does not identify fixture manifest")
    if snapshot["reducer_equivalence"]["result_ref"]["record_id"] != equivalence["result_id"]:
        errors.append("private snapshot equivalence reference does not identify fixture result")
    if snapshot["impact_index_ref"]["record_id"] != impact["impact_id"]:
        errors.append("private snapshot impact reference does not identify fixture result")

    root_refs = [
        snapshot["canonical_bindings"]["engine_contract_root_ref"],
        redaction["compiled_against"]["engine_contract_root_ref"],
        equivalence["source_binding"]["engine_contract_root_ref"],
        impact["source_binding"]["engine_contract_root_ref"],
    ]
    c0_refs = [
        snapshot["canonical_bindings"]["c0_registry_bundle_ref"],
        redaction["compiled_against"]["c0_registry_bundle_ref"],
        equivalence["source_binding"]["c0_registry_bundle_ref"],
        impact["source_binding"]["c0_registry_bundle_ref"],
    ]
    checkpoint_refs = [
        snapshot["canonical_bindings"]["ledger_checkpoint"]["checkpoint_ref"],
        redaction["compiled_against"]["ledger_checkpoint"]["checkpoint_ref"],
        equivalence["source_binding"]["ledger_checkpoint"]["checkpoint_ref"],
        impact["source_binding"]["checkpoint_ref"],
    ]
    for label, refs in (("engine root", root_refs), ("C0 bundle", c0_refs), ("checkpoint", checkpoint_refs)):
        if len({ref_key(ref) for ref in refs}) != 1:
            errors.append(f"projection package does not share one exact {label} binding")
    if redaction["audience"] != snapshot["audience"] or redaction["purpose"] != snapshot["purpose"]:
        errors.append("private snapshot and redaction manifest audience/purpose differ")

    static_target = (
        static_snapshot["projection_id"],
        static_snapshot["version"],
        static_snapshot["projection_type"],
    )
    if static_target != (
        static_equivalence["projection_target"]["projection_id"],
        static_equivalence["projection_target"]["projection_version"],
        static_equivalence["projection_target"]["projection_type"],
    ):
        errors.append("static snapshot and static equivalence exception target identities differ")
    if static_snapshot["reducer_equivalence"]["result_ref"]["record_id"] != static_equivalence["result_id"]:
        errors.append("static snapshot not-run reference does not identify fixture result")
    return errors


def main() -> int:
    failures = schema_audit()
    manifest = load_json(CASES)
    required_vectors = set(manifest["required_adversarial_vectors"])
    covered_vectors = {
        int(vector)
        for case in manifest["cases"]
        for vector in case.get("vectors", [])
    }
    if covered_vectors != required_vectors:
        failures.append(
            f"adversarial vector coverage mismatch: missing={sorted(required_vectors - covered_vectors)}, "
            f"unexpected={sorted(covered_vectors - required_vectors)}"
        )

    structural_invalid_count = 0
    semantic_case_count = 0
    for case in manifest["cases"]:
        schema_path = str(case["schema"])
        schema = load_json(ROOT / schema_path)
        instance = mutate(load_json(ROOT / case["fixture"]), case.get("mutations", []))
        structural_errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance)
        )
        actual = "invalid" if structural_errors else "valid"
        if actual != case["expect"]:
            detail = structural_errors[0].message if structural_errors else "mutation was unexpectedly accepted"
            failures.append(f"{case['name']}: expected structural {case['expect']}, got {actual}: {detail}")
            continue
        if structural_errors:
            structural_invalid_count += 1
            continue
        if "semantic_expect" in case:
            semantic_case_count += 1
            semantic_failures = semantic_errors(schema_path, instance)
            semantic_actual = "invalid" if semantic_failures else "valid"
            if semantic_actual != case["semantic_expect"]:
                detail = semantic_failures[0] if semantic_failures else "semantic mutation was unexpectedly accepted"
                failures.append(
                    f"{case['name']}: expected semantic {case['semantic_expect']}, "
                    f"got {semantic_actual}: {detail}"
                )

    package_failures = package_semantics()
    failures.extend(f"package: {failure}" for failure in package_failures)

    if failures:
        print("Projection contract cases failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        f"Projection contract cases passed: {len(manifest['cases'])} "
        f"({structural_invalid_count} structurally rejected, "
        f"{semantic_case_count} bounded semantic cases, "
        f"{len(required_vectors)} adversarial vectors covered; "
        "no authority, release, runtime, noninterference proof, or Gate A acceptance)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
