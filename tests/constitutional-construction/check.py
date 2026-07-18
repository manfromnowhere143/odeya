#!/usr/bin/env python3
"""Check Odeya's nonrecursive constitutional construction contracts.

This suite evaluates synthetic architecture fixtures only. A pass cannot create
or attest a real root, C0 bundle, checkpoint, P0, RegistryActivation, Gate A
acceptance, handler deployment, or runtime authority.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests/constitutional-construction/cases.json"
SCHEMA_PATHS = {
    "construction_order": ROOT / "architecture/constitutional-construction-order.schema.json",
    "blocked_receipt": ROOT / "architecture/blocked-construction-receipt.schema.json",
}

EXPECTED_PHASE_ORDER = [
    "canonicalize_core_projection",
    "compute_core_digest",
    "produce_evidence_over_core_digest",
    "assemble_seal_subject_from_unchanged_core_and_ordered_evidence_refs",
    "compute_seal_digest",
    "produce_external_attestations_over_seal_digest",
]
EXPECTED_RESERVED_DOMAINS = {
    "engine_contract_root": (
        "odeya-engine-contract-root-core-v1",
        "odeya-engine-contract-root-seal-v1",
    ),
    "c0_registry_bundle": (
        "odeya-c0-registry-bundle-core-v1",
        "odeya-c0-registry-bundle-seal-v1",
    ),
    "ledger_checkpoint": (
        "odeya-ledger-checkpoint-core-v1",
        "odeya-ledger-checkpoint-seal-v1",
    ),
    "p0_constitutional_recovery_admission": (
        "odeya-p0-constitutional-recovery-admission-core-v1",
        "odeya-p0-constitutional-recovery-admission-seal-v1",
    ),
    "registry_activation": (
        "odeya-registry-activation-core-v1",
        "odeya-registry-activation-seal-v1",
    ),
}
EXPECTED_P0_BOUNDARY = {
    "activation_reference_permitted": False,
    "activation_identity_included": False,
    "activation_sequence_included": False,
    "parent_activation_digest_included": False,
    "outer_activation_must_bind_exact_p0_digest": True,
    "self_issued_root_authority_permitted": False,
    "parent_root_and_c0_equality_required": True,
}
FORBIDDEN_P0_PARENT_FIELDS = {
    "activation_id",
    "activation_sequence",
    "activation_ref",
    "previous_activation_ref",
    "activation_digest",
}
LOCAL_ACTION_CLASSES = {
    "local_read",
    "local_compute",
    "local_artifact_write",
    "local_verification",
}


class DuplicateKeyError(ValueError):
    """Reject JSON whose meaning would depend on a permissive duplicate-key parser."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def load_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_keys,
    )


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def mutated_copy(instance: Any, mutations: list[dict[str, Any]]) -> Any:
    result = deepcopy(instance)
    for mutation in mutations:
        operation = mutation.get("op")
        tokens = pointer_tokens(str(mutation.get("path")))
        parent = result
        for token in tokens[:-1]:
            parent = parent[int(token)] if isinstance(parent, list) else parent[token]
        final = tokens[-1]
        if isinstance(parent, list):
            index = int(final)
            if operation == "add":
                parent.insert(index, deepcopy(mutation.get("value")))
            elif operation == "replace":
                parent[index] = deepcopy(mutation.get("value"))
            elif operation == "remove":
                del parent[index]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        elif isinstance(parent, dict):
            if operation == "add":
                if final in parent:
                    raise ValueError(f"add target already exists: {mutation.get('path')!r}")
                parent[final] = deepcopy(mutation.get("value"))
            elif operation == "replace":
                if final not in parent:
                    raise KeyError(mutation.get("path"))
                parent[final] = deepcopy(mutation.get("value"))
            elif operation == "remove":
                del parent[final]
            else:
                raise ValueError(f"unsupported mutation operation: {operation!r}")
        else:
            raise TypeError(f"mutation parent is not a container: {mutation.get('path')!r}")
    return result


def schema_errors(schema: dict[str, Any], instance: Any) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"schema {error.json_path}: {error.message}"
        for error in sorted(validator.iter_errors(instance), key=lambda item: str(item.json_path))
    ]


def construction_order_errors(instance: Any, schema: dict[str, Any]) -> list[str]:
    errors = schema_errors(schema, instance)
    if not isinstance(instance, dict):
        return errors
    if instance.get("phase_order") != EXPECTED_PHASE_ORDER:
        errors.append("phase order is not core -> core digest -> evidence -> seal -> seal digest -> attestation")

    readiness = instance.get("unresolved_profile_prerequisites")
    expected_readiness = {
        "canonicalization_profile_frozen": False,
        "digest_input_framing_frozen": False,
        "replacement_digest_contract_shapes_frozen": False,
        "disposition": "blocking_no_constitutional_digest_may_be_constructed",
    }
    if readiness != expected_readiness:
        errors.append("unfinished canonical/framing/digest-contract profiles are not exactly blocking")

    profiles = instance.get("family_profiles")
    if not isinstance(profiles, dict):
        errors.append("family_profiles is not an object")
        return errors
    for family, profile in profiles.items():
        if not isinstance(profile, dict):
            errors.append(f"family_profiles.{family} is not an object")
            continue
        excluded = set(profile.get("core_projection_excluded_json_pointers", []))
        evidence = set(profile.get("evidence_reference_json_pointers", []))
        attestations = set(profile.get("external_attestation_json_pointers", []))
        digest_pointer = profile.get("seal_digest_json_pointer")
        if not evidence <= excluded:
            errors.append(f"{family}: evidence references remain inside the core projection")
        if not attestations <= excluded:
            errors.append(f"{family}: external attestations remain inside the core projection")
        if digest_pointer not in excluded:
            errors.append(f"{family}: seal digest remains inside the core projection")
        if profile.get("evidence_binding_target") != "core_digest":
            errors.append(f"{family}: evidence does not bind the core digest")
        if profile.get("external_attestation_binding_target") != "seal_digest":
            errors.append(f"{family}: external attestation does not bind the seal digest")
        if profile.get("seal_uses_unchanged_core_projection") is not True:
            errors.append(f"{family}: seal may alter the evidenced core projection")
        if profile.get("replacement_schema_id_status") != "not_assigned":
            errors.append(f"{family}: prospective replacement schema identity is falsely assigned")
        if profile.get("existing_schema_bytes_conform") is not False:
            errors.append(f"{family}: existing source-candidate bytes are falsely claimed conforming")
        if profile.get("integration_disposition") != "blocking_transitive_version_migration_required":
            errors.append(f"{family}: transitive schema-version migration is not explicitly blocking")
        expected_domains = EXPECTED_RESERVED_DOMAINS.get(family)
        actual_domains = (
            profile.get("reserved_core_digest_domain_separator"),
            profile.get("reserved_seal_digest_domain_separator"),
        )
        if expected_domains is None or actual_domains != expected_domains:
            errors.append(f"{family}: reserved core/seal domain pair drifted")

    all_reserved_domains = [
        profile.get(key)
        for profile in profiles.values()
        if isinstance(profile, dict)
        for key in (
            "reserved_core_digest_domain_separator",
            "reserved_seal_digest_domain_separator",
        )
    ]
    if len(all_reserved_domains) != len(set(all_reserved_domains)):
        errors.append("constitutional core/seal domain reservations are not globally unique")

    p0_profile = profiles.get("p0_constitutional_recovery_admission", {})
    if isinstance(p0_profile, dict):
        forbidden = set(p0_profile.get("forbidden_parent_json_pointers", []))
        expected = {f"/{field}" for field in FORBIDDEN_P0_PARENT_FIELDS}
        if not expected <= forbidden:
            errors.append("P0 construction profile does not exclude every parent activation field")
    activation_profile = profiles.get("registry_activation", {})
    if isinstance(activation_profile, dict):
        if "/attestations" not in activation_profile.get("external_attestation_json_pointers", []):
            errors.append("RegistryActivation attestations are not explicitly external to its seal digest")
    return errors


def blocked_receipt_errors(instance: Any, schema: dict[str, Any]) -> list[str]:
    errors = schema_errors(schema, instance)
    if not isinstance(instance, dict):
        return errors
    boundary = instance.get("construction_boundary", {})
    missing = instance.get("missing_real_subjects", [])
    if isinstance(boundary, dict) and isinstance(missing, list):
        if boundary.get("missing_real_subject_count") != len(missing):
            errors.append("missing_real_subject_count does not equal the exact missing subject inventory")
    observed = instance.get("observed_inputs", [])
    placeholder_present = any(
        isinstance(item, dict)
        and item.get("provenance") in {"synthetic_placeholder", "structural_fixture"}
        for item in observed
        if isinstance(observed, list)
    )
    if placeholder_present and isinstance(boundary, dict):
        if boundary.get("placeholder_or_synthetic_inputs_present") is not True:
            errors.append("synthetic/fixture input is present but the receipt hides that boundary")
    return errors


def constitutional_chain_errors(instance: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(instance, dict):
        return ["constitutional chain fixture is not an object"]
    if instance.get("evidence_class") != "synthetic_structure_only":
        errors.append("case is not explicitly synthetic structure-only evidence")
    if instance.get("candidate_status") != "blocked_not_admitted":
        errors.append("synthetic chain does not remain blocked and non-admitted")
    claims = instance.get("claims", {})
    if not isinstance(claims, dict) or any(value is not False for value in claims.values()):
        errors.append("synthetic chain makes a real checkpoint/P0/activation/Gate A/authority claim")

    root = instance.get("engine_contract_root", {})
    c0 = instance.get("c0_registry_bundle", {})
    checkpoint = instance.get("ledger_checkpoint", {})
    p0 = instance.get("p0", {})
    activation = instance.get("activation", {})
    if not all(isinstance(value, dict) for value in (root, c0, checkpoint, p0, activation)):
        return errors + ["constitutional chain subjects must be objects"]

    if c0.get("engine_contract_root_digest") != root.get("digest"):
        errors.append("C0 EngineContractRoot digest does not equal the root subject digest")
    if c0.get("component_digests") != root.get("component_digests"):
        errors.append("C0 component digest set does not equal the EngineContractRoot component set")
    if checkpoint.get("engine_contract_root_digest") != root.get("digest"):
        errors.append("checkpoint EngineContractRoot digest does not equal the root subject digest")
    if checkpoint.get("c0_registry_bundle_digest") != c0.get("digest"):
        errors.append("checkpoint C0 digest does not equal the C0 subject digest")

    if p0.get("nonrecursive_boundary") != EXPECTED_P0_BOUNDARY:
        errors.append("P0 nonrecursive boundary is not exactly activation-independent")
    leaked_parent_fields = sorted(FORBIDDEN_P0_PARENT_FIELDS & set(p0))
    if leaked_parent_fields:
        errors.append(f"P0 contains parent activation fields: {leaked_parent_fields}")
    if p0.get("engine_contract_root_digest") != root.get("digest"):
        errors.append("P0 EngineContractRoot digest does not equal the root subject digest")
    if p0.get("c0_registry_bundle_digest") != c0.get("digest"):
        errors.append("P0 C0 digest does not equal the C0 subject digest")
    if p0.get("checkpoint_digest") != checkpoint.get("digest"):
        errors.append("P0 checkpoint digest does not equal the checkpoint subject digest")

    if activation.get("engine_contract_root_digest") != p0.get("engine_contract_root_digest"):
        errors.append("outer activation root digest does not equal embedded P0 root digest")
    if activation.get("c0_registry_bundle_digest") != p0.get("c0_registry_bundle_digest"):
        errors.append("outer activation C0 digest does not equal embedded P0 C0 digest")
    if activation.get("checkpoint_digest") != p0.get("checkpoint_digest"):
        errors.append("outer activation checkpoint digest does not equal embedded P0 checkpoint digest")
    if activation.get("p0_digest") != p0.get("digest"):
        errors.append("outer activation does not bind the exact sealed P0 digest")

    frontier = p0.get("frontier", {})
    if not isinstance(frontier, dict):
        errors.append("P0 recovery frontier is not an object")
    else:
        if frontier.get("ref_digest") != frontier.get("digest"):
            errors.append("recovery frontier reference digest does not equal frontier digest")
        epoch = frontier.get("ledger_epoch")
        if epoch != checkpoint.get("ledger_epoch") or epoch != activation.get("ledger_epoch"):
            errors.append("recovery frontier epoch does not equal checkpoint and activation epochs")
        frontier_position = frontier.get("position")
        checkpoint_position = checkpoint.get("inclusive_global_position")
        activation_position = activation.get("global_position")
        if not all(isinstance(value, int) for value in (frontier_position, checkpoint_position, activation_position)):
            errors.append("checkpoint/frontier/activation positions are not integers")
        elif not checkpoint_position <= frontier_position < activation_position:
            errors.append("required order checkpoint <= recovery frontier < activation is violated")

    witnesses = p0.get("witnesses", [])
    if not isinstance(witnesses, list) or len(witnesses) < 2:
        errors.append("P0 lacks two structural witness observations")
    else:
        witness_ids = [item.get("witness_id") for item in witnesses if isinstance(item, dict)]
        failure_domains = [item.get("failure_domain_id") for item in witnesses if isinstance(item, dict)]
        if len(witness_ids) != len(witnesses) or len(witness_ids) != len(set(witness_ids)):
            errors.append("witness identities are missing or duplicated")
        if len(failure_domains) != len(witnesses) or len(failure_domains) != len(set(failure_domains)):
            errors.append("witness failure domains are missing or duplicated")
        for index, witness in enumerate(witnesses):
            if not isinstance(witness, dict) or witness.get("checkpoint_digest") != checkpoint.get("digest"):
                errors.append(f"witnesses[{index}] does not observe the bound checkpoint digest")

    command_surface = activation.get("command_surface", {})
    handlers = activation.get("handler_conformance", {})
    if not isinstance(command_surface, dict) or not isinstance(handlers, dict):
        errors.append("command surface or handler conformance is not an object")
    else:
        members = command_surface.get("registry_members", [])
        discriminators = command_surface.get("envelope_discriminators", [])
        handler_members = handlers.get("handler_members", [])
        if not all(isinstance(value, list) for value in (members, discriminators, handler_members)):
            errors.append("command/handler member sets are not arrays")
        else:
            if len(members) != len(set(members)) or members != discriminators:
                errors.append("generated envelope discriminator set does not equal the admitted command set")
            if handler_members != members or len(handler_members) != len(set(handler_members)):
                errors.append("handler member set does not equal the admitted command set")
            if command_surface.get("declared_member_count") != len(discriminators):
                errors.append("declared command count does not equal generated envelope discriminator count")
            if handlers.get("declared_member_count") != len(handler_members):
                errors.append("declared handler count does not equal the handler member set")
        if handlers.get("set_digest") != command_surface.get("set_digest"):
            errors.append("handler set digest does not equal the admitted command-set digest")

    sequence = activation.get("activation_sequence")
    effect = activation.get("effect")
    predecessor = activation.get("previous_activation_digest")
    if sequence == 1:
        if effect != "activate" or predecessor is not None:
            errors.append("initial activation must be sequence one with no predecessor")
    elif isinstance(sequence, int) and sequence > 1:
        if predecessor is None or effect not in {"supersede", "rollback"}:
            errors.append("later activation sequence requires an exact predecessor and maintenance effect")
    else:
        errors.append("activation sequence is not a positive integer")

    scope = activation.get("scope", {})
    if not isinstance(scope, dict):
        errors.append("activation scope is not an object")
    else:
        if scope.get("risk_ceiling") not in {"R0", "R1"}:
            errors.append("P0 recovery activation exceeds the R0/R1 risk ceiling")
        environments = scope.get("environment_classes", [])
        if not isinstance(environments, list) or not environments or set(environments) - {"local_isolated"}:
            errors.append("P0 recovery activation is not confined to local_isolated")
        actions = scope.get("permitted_action_classes", [])
        if not isinstance(actions, list) or not actions or set(actions) - LOCAL_ACTION_CLASSES:
            errors.append("P0 recovery activation admits an external or unknown action class")
        for flag in (
            "publication_enabled",
            "spending_enabled",
            "external_effects_enabled",
            "physical_actions_enabled",
        ):
            if scope.get(flag) is not False:
                errors.append(f"P0 recovery activation does not fail closed for {flag}")

    authority = instance.get("root_authority", {})
    if not isinstance(authority, dict):
        errors.append("root authority is not an object")
    else:
        if authority.get("root_profile") != "prospective_operational_root_shape_only":
            errors.append("root-authority case is not explicitly a prospective shape-only profile")
        recovery = authority.get("recovery", {})
        role_bindings = authority.get("role_bindings", {})
        principals = recovery.get("principals", []) if isinstance(recovery, dict) else []
        quorum = recovery.get("quorum") if isinstance(recovery, dict) else None
        if not isinstance(principals, list) or len(principals) != len(set(principals)):
            errors.append("root recovery principals are missing or duplicated")
        if authority.get("root_profile") == "prospective_operational_root_shape_only" and len(principals) < 2:
            errors.append("prospective operational-root shape has fewer than two recovery principals")
        if not isinstance(quorum, int) or quorum < 1 or quorum > len(principals):
            errors.append("root recovery quorum exceeds the distinct recovery principals")
        if not isinstance(role_bindings, dict) or set(role_bindings.values()) - set(principals):
            errors.append("root role binding names a principal outside the recovery set")
        elif authority.get("root_profile") == "prospective_operational_root_shape_only":
            for first, second in (
                ("execution", "safety"),
                ("execution", "verification"),
                ("proposal", "publication"),
            ):
                if role_bindings.get(first) == role_bindings.get(second):
                    errors.append(f"operational root collapses critical roles {first} and {second}")

    activation_digest = activation.get("digest")
    attestations = activation.get("attestations", [])
    if not isinstance(attestations, list) or not attestations:
        errors.append("activation has no external attestation")
    else:
        attestation_ids = [item.get("attestation_id") for item in attestations if isinstance(item, dict)]
        if len(attestation_ids) != len(attestations) or len(attestation_ids) != len(set(attestation_ids)):
            errors.append("activation attestation identities are missing or duplicated")
        for index, attestation in enumerate(attestations):
            if not isinstance(attestation, dict) or attestation.get("signed_digest") != activation_digest:
                errors.append(f"attestations[{index}] does not sign the activation seal digest")
    return errors


def attribution_failures(name: str, case: dict, errors: list[str]) -> list[str]:
    """Refusal for an incidental reason is not proof that the intended
    invariant fires. Bind each known-bad case to its own refusal, the
    lifecycle suite's spelling (ADR 0024, 0055-0057)."""
    expected_refusal = case.get("expected_refusal_contains")
    if not isinstance(expected_refusal, str) or not expected_refusal:
        return [f"{name}: known-bad case does not declare the invariant that must refuse it"]
    if not any(expected_refusal in error for error in errors):
        return [
            f"{name}: refused, but not by its declared invariant "
            f"{expected_refusal!r}; got {errors}"
        ]
    return []


def attribution_self_test_meta_proof(cases: list, evaluate) -> list[str]:
    """Prove the self-test's own refusals are load-bearing (ADR 0069/0080)."""
    blind = lambda name, case, errors: []  # noqa: E731 - a binder that refuses nothing
    distinct = {f for f in attribution_self_test(cases, evaluate, binder=blind)}
    if len(distinct) != 2:
        return [
            f"attribution meta self-test: blinding the binder produced {len(distinct)} distinct "
            "refusals, expected 2; a self-test refusal is not load-bearing"
        ]
    return []


def attribution_self_test(cases: list, evaluate, binder=None) -> list[str]:
    """Prove on every run that the binding check itself fires (law 11)."""
    bind = binder or attribution_failures
    template = next((c for c in cases if isinstance(c, dict) and c.get("expect") == "reject"), None)
    if template is None:
        return ["attribution self-test found no known-bad case to tamper with"]
    errors = evaluate(template)
    failures: list[str] = []
    misdeclared = dict(template, expected_refusal_contains="odeya-self-test-never-appears")
    if not any("not by its declared invariant" in f
               for f in bind(str(template.get("name")), misdeclared, errors)):
        failures.append("attribution self-test: a misdeclared invariant was not detected")
    undeclared = {k: v for k, v in template.items() if k != "expected_refusal_contains"}
    if not any("does not declare the invariant" in f
               for f in bind(str(template.get("name")), undeclared, errors)):
        failures.append("attribution self-test: a missing declaration was not detected")
    return failures


def main() -> int:
    manifest = load_json(CASES_PATH)
    schemas = {name: load_json(path) for name, path in SCHEMA_PATHS.items()}
    failures: list[str] = []
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # pragma: no cover - defensive reporting path
            failures.append(f"{name} schema is invalid: {exc}")

    cases = manifest.get("cases", [])
    names = [case.get("name") for case in cases if isinstance(case, dict)]
    if len(names) != len(cases) or len(names) != len(set(names)):
        failures.append("case names must be present and unique")
    required_tags = set(manifest.get("required_adversarial_tags", []))
    actual_tags = {
        case.get("adversarial_tag")
        for case in cases
        if isinstance(case, dict) and case.get("kind") == "adversarial"
    }
    if actual_tags != required_tags:
        failures.append(
            f"adversarial coverage mismatch: missing={sorted(required_tags - actual_tags)}, "
            f"unexpected={sorted(actual_tags - required_tags)}"
        )

    model_checkers: dict[str, Callable[[Any], list[str]]] = {
        "construction_order": lambda value: construction_order_errors(value, schemas["construction_order"]),
        "blocked_receipt": lambda value: blocked_receipt_errors(value, schemas["blocked_receipt"]),
        "constitutional_chain": constitutional_chain_errors,
    }
    def evaluate(case: dict) -> list[str]:
        instance = mutated_copy(load_json(ROOT / str(case.get("fixture"))), case.get("mutations", []))
        return model_checkers[str(case.get("model"))](instance)

    failures.extend(attribution_self_test(cases, evaluate))
    failures.extend(attribution_self_test_meta_proof(cases, evaluate))

    safe_count = 0
    rejected_count = 0
    for case in cases:
        if not isinstance(case, dict):
            failures.append("case is not an object")
            continue
        name = str(case.get("name"))
        fixture_path = ROOT / str(case.get("fixture"))
        try:
            instance = mutated_copy(load_json(fixture_path), case.get("mutations", []))
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, IndexError) as exc:
            failures.append(f"{name}: fixture/mutation failed: {type(exc).__name__}: {exc}")
            continue
        checker = model_checkers.get(str(case.get("model")))
        if checker is None:
            failures.append(f"{name}: unknown model {case.get('model')!r}")
            continue
        errors = checker(instance)
        accepted = not errors
        expectation = case.get("expect")
        if expectation == "accept":
            safe_count += 1
            if not accepted:
                failures.append(f"{name}: safe reference rejected: {'; '.join(errors[:5])}")
        elif expectation == "reject":
            if accepted:
                failures.append(f"{name}: known-bad mutation was accepted")
            else:
                rejected_count += 1
            failures.extend(attribution_failures(name, case, errors))
        else:
            failures.append(f"{name}: unknown expectation {expectation!r}")

    if failures:
        print("constitutional construction adversarial check FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("constitutional construction adversarial check passed")
    print(f"safe structural references accepted: {safe_count}")
    print(f"known-bad construction/equality mutations rejected: {rejected_count}")
    print(
        "boundary: prospective replacement/integration contract only; existing core schemas do not "
        "conform, and no P0, activation, Gate A, or runtime authority exists"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
