#!/usr/bin/env python3
"""Validate the nonrecursive WorkIntent identity candidate construction.

This architecture-time checker proves bounded agreement among an identity-free
semantic core, exact raw-byte bindings, the retained WorkIntent 0.1 projection,
the frozen-but-unissued canonicalization profile, and the exact direct-consumer
reissue boundary. A pass cannot issue a canonical identity, admit a WorkIntent,
authorize assignment, or authorize runtime effects.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/work-intent-identity-candidate"
CORE = ROOT / "architecture/work-intent-core-candidate.json"
EVIDENCE = ROOT / "architecture/work-intent-identity-candidate-evidence.json"
CORE_SCHEMA = ROOT / "schemas/work-intent-core.schema.json"
EVIDENCE_SCHEMA = (
    ROOT / "schemas/work-intent-identity-candidate-evidence.schema.json"
)
LEGACY_SCHEMA = ROOT / "schemas/work-intent.schema.json"
LEGACY_FIXTURE = (
    ROOT / "tests/cognitive-contracts/fixtures/work-intent.valid.json"
)
PROFILE_CORE = ROOT / "architecture/canonicalization-profile-core-candidate.json"
PROFILE_EVIDENCE = (
    ROOT / "architecture/canonicalization-profile-candidate-evidence.json"
)
CASES = SUITE / "cases.json"

PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"
PROFILE_SCHEMA_ID = "urn:odeya:schema:canonicalization-profile-core:0.5.0"
CORE_SCHEMA_ID = "urn:odeya:schema:work-intent-core:0.1.0"
LEGACY_SCHEMA_ID = "urn:odeya:schema:work-intent:0.7.0"
FIXED_TIMESTAMP = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    r"[0-9]{2}\.[0-9]{6}Z$"
)
REMOVED_IDENTITY_FIELDS = [
    "identity_resolution_status",
    "canonicalization_profile_ref",
    "canonical_digest",
]
EXPECTED_REISSUES = [
    {
        "path": "schemas/work-intent.schema.json",
        "from_schema_id": "urn:odeya:schema:work-intent:0.1.0",
        "to_schema_id": "urn:odeya:schema:work-intent:0.19.0"
    },
    {
        "path": "schemas/canonical-work-lease.schema.json",
        "from_schema_id": "urn:odeya:schema:canonical-work-lease:0.1.0",
        "to_schema_id": "urn:odeya:schema:canonical-work-lease:0.13.0"
    },
    {
        "path": "schemas/work-contract.schema.json",
        "from_schema_id": "urn:odeya:schema:work-contract:0.2.0",
        "to_schema_id": "urn:odeya:schema:work-contract:0.20.0"
    }
]
EXPECTED_CONSUMERS = [
    {
        "schema_path": "schemas/canonical-work-lease.schema.json",
        "current_schema_id": "urn:odeya:schema:canonical-work-lease:0.8.0",
        "prospective_schema_id": "urn:odeya:schema:canonical-work-lease:0.13.0",
    },
    {
        "schema_path": "schemas/work-contract.schema.json",
        "current_schema_id": "urn:odeya:schema:work-contract:0.19.0",
        "prospective_schema_id": "urn:odeya:schema:work-contract:0.20.0",
    },
]


class DuplicateKey(ValueError):
    """Raised before a JSON object with duplicate names can become a mapping."""


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one JSON object")
    return value


def render(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def raw_binding(path: Path) -> tuple[str, int]:
    raw = path.read_bytes()
    return sha256(raw), len(raw)


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def apply_mutation(subject: Any, mutation: dict[str, Any]) -> None:
    tokens = pointer_tokens(mutation["path"])
    parent = subject
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = tokens[-1]
    operation = mutation["op"]
    if isinstance(parent, list):
        index = int(final)
        if operation == "replace":
            parent[index] = mutation["value"]
        elif operation == "remove":
            del parent[index]
        elif operation == "add":
            parent.insert(index, mutation["value"])
        else:
            raise ValueError(f"unsupported mutation operation {operation!r}")
    elif isinstance(parent, dict):
        if operation == "replace":
            if final not in parent:
                raise KeyError(final)
            parent[final] = mutation["value"]
        elif operation == "remove":
            del parent[final]
        elif operation == "add":
            if final in parent:
                raise ValueError(f"add target already exists: {final!r}")
            parent[final] = mutation["value"]
        else:
            raise ValueError(f"unsupported mutation operation {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def schema_invalid(
    document: dict[str, Any], schema: dict[str, Any], label: str
) -> str | None:
    errors = list(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(document)
    )
    return f"{label}_schema_invalid" if errors else None


def audit_module() -> Any:
    path = ROOT / "tests/canonicalization/audit_schemas.py"
    spec = importlib.util.spec_from_file_location("odeya_schema_audit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the canonical schema audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def core_audit_snapshot(core_schema: dict[str, Any]) -> dict[str, int]:
    audit = audit_module()
    _, unprofiled = audit.datetime_nodes(core_schema)
    digest_rows = audit.digest_fields(core_schema)
    bindings = audit.canonical_profile_bindings(core_schema)
    return {
        "unprofiled_datetime_paths": len(unprofiled),
        "generic_json_number_paths": len(audit.number_nodes(core_schema)),
        "generic_scientific_decimal_paths": len(
            audit.generic_decimal_uses(core_schema)
        ),
        "unscoped_digest_fields": sum(
            not row["scope_annotation_present"] for row in digest_rows
        ),
        "unpinned_profile_bindings": sum(
            not row["pins_candidate_profile"] for row in bindings
        ),
        "dangling_local_refs": len(audit.dangling_local_refs(core_schema)),
    }


def sorted_unique(values: Any) -> bool:
    return (
        isinstance(values, list)
        and len(values) == len(set(values))
        and values == sorted(values)
    )


def evaluate(core: dict[str, Any], evidence: dict[str, Any]) -> set[str]:
    errors: set[str] = set()
    core_schema = load(CORE_SCHEMA)
    evidence_schema = load(EVIDENCE_SCHEMA)
    for code in (
        schema_invalid(core, core_schema, "core"),
        schema_invalid(evidence, evidence_schema, "evidence"),
    ):
        if code:
            errors.add(code)

    forbidden_identity = {
        "identity_resolution_status",
        "canonicalization_profile_ref",
        "canonical_digest",
    }
    if forbidden_identity & set(core):
        errors.add("core_contains_identity_binding")
    if (
        core.get("record_status") != "proposed_non_authoritative"
        or core.get("record_authority_status") != "not_admitted_not_assignable"
    ):
        errors.add("core_authority_boundary_invalid")
    prospective = core.get("prospective_authority_boundary", {})
    expected_false = {
        "active_lease_required_at_intent",
        "resource_reservation_required_at_intent",
        "dispatch_authority_granted",
        "materialization_authority_granted",
        "external_effect_authority_granted",
        "bytes_may_cross_at_intent",
        "provider_spend_may_incur_at_intent",
    }
    if (
        not isinstance(prospective, dict)
        or any(prospective.get(key) is not False for key in expected_false)
        or prospective.get("active_lease_ref") is not None
        or prospective.get("resource_reservation_ref") is not None
        or prospective.get("dispatch_admission_ref") is not None
        or prospective.get("authority_grant_refs") != []
    ):
        errors.add("core_authority_boundary_invalid")
    if not isinstance(core.get("created_at"), str) or not FIXED_TIMESTAMP.fullmatch(
        core["created_at"]
    ):
        errors.add("core_timestamp_not_profiled")

    set_paths = [
        core.get("permitted_deliverable_classes"),
        core.get("candidate_worker_requirements", {}).get("capability_classes"),
        core.get("candidate_worker_requirements", {}).get("execution_modes"),
        core.get("data_boundary", {}).get("maximum_data_classes"),
        core.get("data_boundary", {}).get("allowed_residencies"),
    ]
    if any(not sorted_unique(values) for values in set_paths):
        errors.add("core_set_order_invalid")

    profile_core = load(PROFILE_CORE)
    profile_evidence = load(PROFILE_EVIDENCE)
    profile = evidence.get("profile_candidate_binding", {})
    profile_evidence_binding = profile_evidence.get("profile_core_binding", {})
    expected_profile_digest, expected_profile_bytes = raw_binding(PROFILE_CORE)
    if (
        profile.get("profile_id") != PROFILE_ID
        or profile.get("profile_version") != profile_core.get("profile_version")
        or profile.get("profile_core_schema_id") != PROFILE_SCHEMA_ID
        or profile.get("profile_core_raw_digest") != expected_profile_digest
        or profile.get("profile_core_bytes") != expected_profile_bytes
        or profile.get("profile_core_raw_digest")
        != profile_evidence_binding.get("profile_core_raw_digest")
    ):
        errors.add("profile_candidate_binding_mismatch")
    if (
        profile.get("profile_status") != "candidate_unissued"
        or profile.get("same_active_root_membership_proven") is not False
        or profile.get("operator_acceptance_ref") is not None
    ):
        errors.add("profile_acceptance_fabricated")

    binding = evidence.get("work_intent_core_binding", {})
    rendered_core = render(core)
    if (
        binding.get("core_raw_digest") != sha256(rendered_core)
        or binding.get("core_bytes") != len(rendered_core)
    ):
        errors.add("core_raw_binding_mismatch")
    expected_schema_digest, expected_schema_bytes = raw_binding(CORE_SCHEMA)
    if (
        binding.get("core_schema_raw_digest") != expected_schema_digest
        or binding.get("core_schema_bytes") != expected_schema_bytes
        or binding.get("core_schema_id") != core_schema.get("$id")
    ):
        errors.add("core_schema_raw_binding_mismatch")
    if (
        binding.get("core_contains_self_hash") is not False
        or binding.get("identity_binding_external_to_core") is not True
    ):
        errors.add("external_binding_boundary_invalid")
    if binding.get("canonical_audit") != core_audit_snapshot(core_schema):
        errors.add("core_canonical_audit_mismatch")

    legacy_schema = load(LEGACY_SCHEMA)
    legacy_fixture = load(LEGACY_FIXTURE)
    legacy = evidence.get("legacy_projection_binding", {})
    projected = copy.deepcopy(legacy_fixture)
    for key in REMOVED_IDENTITY_FIELDS:
        projected.pop(key, None)
    core_semantic = {k: v for k, v in core.items() if k != "schema_version"}
    projected_semantic = {k: v for k, v in projected.items() if k != "schema_version"}
    if projected_semantic != core_semantic:
        errors.add("legacy_projection_mismatch")
    if (
        legacy.get("identity_fields_removed") != REMOVED_IDENTITY_FIELDS
        or legacy.get("semantic_projection_equal") is not True
    ):
        errors.add("legacy_projection_claim_invalid")
    expected_legacy_schema = raw_binding(LEGACY_SCHEMA)
    expected_legacy_fixture = raw_binding(LEGACY_FIXTURE)
    if (
        legacy_schema.get("$id") != LEGACY_SCHEMA_ID
        or (
            legacy.get("legacy_schema_raw_digest"),
            legacy.get("legacy_schema_bytes"),
        )
        != expected_legacy_schema
        or (
            legacy.get("legacy_fixture_raw_digest"),
            legacy.get("legacy_fixture_bytes"),
        )
        != expected_legacy_fixture
    ):
        errors.add("legacy_raw_binding_mismatch")
    if (
        legacy.get("legacy_schema_resource_replaced") is not False
        or legacy.get("legacy_fixture_is_architecture_only") is not True
        or legacy.get("legacy_reference_identity_status")
        != "synthetic_architecture_values_not_admitted"
    ):
        errors.add("legacy_status_escalated")

    transitive = evidence.get("transitive_reissue_boundary", {})
    consumers = transitive.get("direct_schema_consumers", [])
    represented_consumers: list[dict[str, str]] = []
    if isinstance(consumers, list):
        for row in consumers:
            if not isinstance(row, dict):
                continue
            represented_consumers.append(
                {
                    "schema_path": row.get("schema_path"),
                    "current_schema_id": row.get("current_schema_id"),
                    "prospective_schema_id": row.get("prospective_schema_id"),
                }
            )
            path_value = row.get("schema_path")
            if not isinstance(path_value, str) or not (ROOT / path_value).is_file():
                errors.add("direct_consumer_inventory_mismatch")
                continue
            consumer_schema = load(ROOT / path_value)
            expected_digest, expected_bytes = raw_binding(ROOT / path_value)
            if (
                consumer_schema.get("$id") != row.get("current_schema_id")
                or row.get("current_schema_raw_digest") != expected_digest
                or row.get("current_schema_bytes") != expected_bytes
            ):
                errors.add("direct_consumer_raw_binding_mismatch")
    if (
        transitive.get("direct_schema_consumer_count") != len(EXPECTED_CONSUMERS)
        or represented_consumers != EXPECTED_CONSUMERS
        or transitive.get("required_reissue_order") != EXPECTED_REISSUES
    ):
        errors.add("direct_consumer_inventory_mismatch")
    if transitive.get("reissue_unit") != (
        "single_reviewed_commit_without_missing_intermediate_schema_ids"
    ):
        errors.add("reissue_unit_weakened")
    false_boundaries = {
        "current_work_intent_resource_reissued",
        "current_direct_consumers_reissued",
        "complete_offline_predecessor_registry",
        "migration_evidence_complete",
        "assignment_construction_unblocked",
    }
    if any(transitive.get(key) is not False for key in false_boundaries):
        errors.add("transitive_reissue_boundary_escalated")

    identity = evidence.get("identity_construction_boundary", {})
    if (
        identity.get("canonical_envelope_exact_members")
        != ["profile_id", "schema_id", "subject"]
        or identity.get("canonical_envelope_profile_id") != PROFILE_ID
        or identity.get("canonical_envelope_schema_id") != CORE_SCHEMA_ID
        or identity.get("canonical_envelope_subject_path")
        != "architecture/work-intent-core-candidate.json"
    ):
        errors.add("canonical_envelope_mismatch")
    if identity.get("subject_contains_self_hash") is not False:
        errors.add("external_binding_boundary_invalid")
    if identity.get("raw_byte_binding_is_canonical_object_identity") is not False:
        errors.add("raw_binding_mislabeled_as_canonical_identity")
    if identity.get("canonical_digest") is not None:
        errors.add("canonical_digest_fabricated")
    if identity.get("canonical_identity_status") != (
        "not_constructible_profile_unissued_and_resource_not_admitted"
    ):
        errors.add("canonical_identity_status_escalated")
    if any(
        identity.get(key) is not None
        for key in ("registry_member_ref", "admission_ref", "operator_acceptance_ref")
    ):
        errors.add("canonical_admission_fabricated")

    authority = evidence.get("authority_boundary", {})
    if not isinstance(authority, dict) or any(
        value is not False for value in authority.values()
    ):
        errors.add("authority_boundary_fabricated")
    return errors


def main() -> int:
    try:
        core = load(CORE)
        evidence = load(EVIDENCE)
        cases_document = load(CASES)
        cases = cases_document.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("cases.json must contain a non-empty cases array")
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKey) as exc:
        print(f"WorkIntent identity candidate: invalid suite: {exc}", file=sys.stderr)
        return 1

    failures, safe_count, adversarial_count = evaluate_cases(cases, core, evidence)
    failures.extend(coverage_failures(safe_count, adversarial_count))
    failures.extend(harness_self_test(core, evidence))
    failures.extend(harness_self_test_meta_proof(core, evidence))
    if failures:
        print("WorkIntent identity candidate: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        "WorkIntent identity candidate: PASS — "
        f"{safe_count} safe reference and {adversarial_count} known-bad mutations; "
        "nonrecursive core/projection/raw-byte/consumer bindings agree, while "
        "profile issuance, transitive reissue, admission, assignment, Gate A, "
        "deployment, runtime, and external effects remain blocked."
    )
    return 0


def evaluate_cases(cases: list, core: dict, evidence: dict) -> tuple[list[str], int, int]:
    """Factored out of main so the harness's own hygiene guards can be
    exercised by a self-test (ADR 0080): a malformed case cannot live in the
    retained set, so before this every hygiene guard had no proof and the
    generalized audit measured this suite at 0 of 13."""
    failures: list[str] = []
    names: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failures.append(f"case {index} is not an object")
            continue
        name = case.get("name")
        kind = case.get("kind")
        if not isinstance(name, str) or not name or name in names:
            failures.append(f"case {index} has a missing or duplicate name")
            continue
        names.add(name)
        candidate_core = copy.deepcopy(core)
        candidate_evidence = copy.deepcopy(evidence)
        mutations = case.get("mutations", [])
        try:
            for mutation in mutations:
                target = mutation.get("target")
                if target == "core":
                    apply_mutation(candidate_core, mutation)
                elif target == "evidence":
                    apply_mutation(candidate_evidence, mutation)
                else:
                    raise ValueError(f"unknown mutation target {target!r}")
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            failures.append(f"{name}: mutation failed: {exc}")
            continue
        observed = evaluate(candidate_core, candidate_evidence)
        expected = set(case.get("expected_errors", []))
        if kind == "safe":
            safe_count += 1
            if mutations:
                failures.append(f"{name}: a safe case may not mutate the reference")
            if observed:
                failures.append(f"{name}: safe reference failed with {sorted(observed)!r}")
        elif kind == "adversarial":
            adversarial_count += 1
            if not mutations:
                failures.append(f"{name}: adversarial case has no mutation")
            # Exact inventory plus declared intent (ADR 0067): a subset check
            # cannot distinguish the intended code from any incidental
            # co-firing one, which independent review exploited.
            intent = set(case.get("intent_errors", []))
            if not intent:
                failures.append(f"{name}: adversarial case declares no intent error")
            elif intent - observed:
                failures.append(
                    f"{name}: intent {sorted(intent - observed)!r} did not fire; "
                    f"observed={sorted(observed)!r}"
                )
            if not observed:
                failures.append(f"{name}: known-bad mutation was accepted")
            elif expected != observed:
                failures.append(
                    f"{name}: declared {sorted(expected)!r} but observed {sorted(observed)!r}"
                )
        else:
            failures.append(f"{name}: unknown case kind {kind!r}")

    return failures, safe_count, adversarial_count


def coverage_failures(safe_count: int, adversarial_count: int) -> list[str]:
    failures: list[str] = []
    if safe_count != 1:
        failures.append(f"suite must contain exactly one safe case, found {safe_count}")
    if adversarial_count < 20:
        failures.append(
            f"suite must contain at least 20 adversarial cases, found {adversarial_count}"
        )
    return failures


def harness_self_test_meta_proof(core: dict, evidence: dict) -> list[str]:
    """Blinding the evaluator makes every probe fail unconditionally, so the
    exact count of DISTINCT refusals is the evidence a probe is load-bearing
    and not duplicated (ADR 0069/0080)."""
    blind = lambda cases, c, e: ([], 0, 0)  # noqa: E731
    distinct = {f for f in harness_self_test(core, evidence, evaluator=blind)}
    if len(distinct) != 9:
        return [
            f"harness meta self-test: blinding the evaluator produced {len(distinct)} distinct "
            "refusals, expected 9; a probe is duplicated or a refusal is not load-bearing"
        ]
    return []


def harness_self_test(core: dict, evidence: dict, evaluator=None) -> list[str]:
    """Each synthetic case is malformed in exactly one way and must be refused
    by exactly one guard; floors probed both sides; probe subjects distinct."""
    failures: list[str] = []
    probed: list = []

    def refuses(case, expected: str, label: str) -> None:
        if any(case == earlier for earlier in probed):
            failures.append(f"harness self-test: {label} duplicates an earlier probe subject")
        probed.append(copy.deepcopy(case))
        observed, _, _ = (evaluator or evaluate_cases)([case], core, evidence)
        if not any(expected in failure for failure in observed):
            failures.append(f"harness self-test: {label} was not refused; got {observed}")

    bad_mut = [{"target": "core", "op": "replace", "path": "/schema_version", "value": "0.0.0"}]
    refuses("not-an-object", "is not an object", "a non-object case")
    refuses({"kind": "safe"}, "missing or duplicate name", "a case without a name")
    refuses({"name": "odeya-self-test-1", "kind": "safe",
             "mutations": [{"target": "no-such", "op": "replace", "path": "/x", "value": 1}]},
            "mutation failed", "an unresolvable mutation target")
    refuses({"name": "odeya-self-test-2", "kind": "safe", "mutations": bad_mut},
            "a safe case may not mutate the reference", "a safe case carrying a mutation")
    refuses({"name": "odeya-self-test-3", "kind": "adversarial", "mutations": [],
             "intent_errors": ["x"], "expected_errors": ["x"]},
            "adversarial case has no mutation", "an adversarial case with no mutation")
    refuses({"name": "odeya-self-test-4", "kind": "adversarial", "mutations": bad_mut,
             "expected_errors": ["x"]},
            "declares no intent error", "an adversarial case with no declared intent")
    refuses({"name": "odeya-self-test-5", "kind": "adversarial", "mutations": bad_mut,
             "intent_errors": ["odeya-self-test-never-fires"], "expected_errors": ["x"]},
            "did not fire", "an intent error that never fires")
    refuses({"name": "odeya-self-test-6", "kind": "bogus"}, "unknown case kind", "an unknown case kind")
    refuses({"name": "odeya-self-test-7", "kind": "adversarial", "mutations": bad_mut,
             "intent_errors": sorted(evaluate(_mutated(core, bad_mut), evidence))[:1] or ["x"],
             "expected_errors": ["odeya-self-test-not-the-observed-set"]},
            "declared", "an inventory that does not equal the observed set")

    for safe_n, adversarial_n, should_refuse, label in (
        (0, 20, True, "no safe reference"),
        (1, 20, False, "the exact safe-reference count"),
        (1, 19, True, "one case below the adversarial floor"),
        (1, 20, False, "the exact adversarial floor"),
    ):
        if bool(coverage_failures(safe_n, adversarial_n)) != should_refuse:
            failures.append(
                f"harness self-test: {label} was "
                f"{'not refused' if should_refuse else 'refused'}"
            )
    return failures


def _mutated(core: dict, mutations: list) -> dict:
    candidate = copy.deepcopy(core)
    for mutation in mutations:
        if mutation.get("target") == "core":
            apply_mutation(candidate, mutation)
    return candidate


if __name__ == "__main__":
    raise SystemExit(main())
