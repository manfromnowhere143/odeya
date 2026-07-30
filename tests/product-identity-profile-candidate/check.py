#!/usr/bin/env python3
"""Adversarial integration contract for the unissued PRQ-002B profile.

The checker deliberately separates two questions:

* ``--self-test-only`` proves that the retained single-fault known-bads reach
  their attributed guards without requiring the product artifacts to exist.
* the default invocation additionally validates the live 12-resource product
  tranche, frozen 120-resource predecessor cohort, and three candidate records.

A pass is architecture evidence for an unissued candidate only.  It cannot
issue or admit a profile, bind a root, create an activation, accept Gate A, or
authorize runtime.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker, validators
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/product-identity-profile-candidate"
CASES_PATH = SUITE / "cases.json"
PREDECESSOR_PATH = SUITE / "predecessor-schemas.json"
POST_PRQ_002B_CHECK = (
    ROOT / "tests/product-identity-profile-0.3-candidate/check.py"
)
POST_PRQ_002B_CHECK_TIMEOUT_SECONDS = 60
ALLOWED_SUITE_JSON_PATHS = {"cases.json", "predecessor-schemas.json"}
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"
STRUCTURAL_VECTOR_GLOB = (
    "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/"
    "prq-002b-*.structural-nonidentity.json"
)
RESERVED_STRUCTURAL_SENTINELS = (
    "sha256:1111111111111111111111111111111111111111111111111111111111111111",
    "sha256:1212121212121212121212121212121212121212121212121212121212121212",
    "sha256:1313131313131313131313131313131313131313131313131313131313131313",
    "sha256:1414141414141414141414141414141414141414141414141414141414141414",
    "sha256:2222222222222222222222222222222222222222222222222222222222222222",
    "sha256:3333333333333333333333333333333333333333333333333333333333333333",
    "sha256:4444444444444444444444444444444444444444444444444444444444444444",
    "sha256:5555555555555555555555555555555555555555555555555555555555555555",
    "sha256:6666666666666666666666666666666666666666666666666666666666666666",
    "sha256:7777777777777777777777777777777777777777777777777777777777777777",
    "sha256:8888888888888888888888888888888888888888888888888888888888888888",
    "sha256:9999999999999999999999999999999999999999999999999999999999999999",
    "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
)
POST_PRQ_002B_SCHEMA_PATHS = (
    "schemas/aggregate-state-subject-record-v0-2.schema.json",
    "schemas/aggregate-state-subject-registry-v0-8.schema.json",
    "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
    "schemas/canonicalization-profile-core-v0-7.schema.json",
    "schemas/canonicalization-profile-migration-v0-2.schema.json",
    "schemas/event-contract-record-v0-2.schema.json",
    "schemas/event-contract-registry-v0-8.schema.json",
    "schemas/ordered-member-map-commitment-v0-2.schema.json",
    "schemas/reducer-contract-record-v0-2.schema.json",
    "schemas/reducer-registry-v0-8.schema.json",
    "schemas/schema-registry-v0-9.schema.json",
    "schemas/schema-resource-record-v0-2.schema.json",
)
STRUCTURAL_RESULT_BINDINGS = {
    "schema_resource_record": (
        "/member_digest",
        RESERVED_STRUCTURAL_SENTINELS[12],
    ),
    "aggregate_state_subject_record": (
        "/member_digest",
        RESERVED_STRUCTURAL_SENTINELS[13],
    ),
    "reducer_contract_record": (
        "/member_digest",
        RESERVED_STRUCTURAL_SENTINELS[14],
    ),
    "event_contract_record": (
        "/member_digest",
        RESERVED_STRUCTURAL_SENTINELS[15],
    ),
    "ordered_member_map_commitment": (
        "/ordered_member_pairs_digest",
        RESERVED_STRUCTURAL_SENTINELS[16],
    ),
    "schema_registry_v0_8": (
        "/registry_digest",
        RESERVED_STRUCTURAL_SENTINELS[17],
    ),
    "aggregate_state_subject_registry_v0_7": (
        "/registry_digest",
        RESERVED_STRUCTURAL_SENTINELS[17],
    ),
    "reducer_registry_v0_7": (
        "/registry_digest",
        RESERVED_STRUCTURAL_SENTINELS[17],
    ),
    "event_contract_registry_v0_7": (
        "/registry_digest",
        RESERVED_STRUCTURAL_SENTINELS[17],
    ),
}


class DuplicateKey(ValueError):
    """Raised before a JSON object can silently overwrite a member."""


class Findings:
    """Stable error-code inventory with useful, non-authoritative diagnostics."""

    def __init__(self) -> None:
        self._items: dict[str, list[str]] = {}

    def add(self, code: str, detail: str) -> None:
        self._items.setdefault(code, []).append(detail)

    def codes(self) -> set[str]:
        return set(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def lines(self) -> Iterable[str]:
        for code in sorted(self._items):
            for detail in sorted(set(self._items[code])):
                yield f"{code}: {detail}"


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError("expected one JSON object")
    return value


def raw_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def json_type_sensitive_equal(observed: Any, expected: Any) -> bool:
    """Compare parsed JSON without Python bool/int/float coercion."""
    if type(observed) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(observed) == set(expected) and all(
            json_type_sensitive_equal(observed[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, (list, tuple)):
        return len(observed) == len(expected) and all(
            json_type_sensitive_equal(left, right)
            for left, right in zip(observed, expected, strict=True)
        )
    return observed == expected


def exact_json_const(
    validator: Any,
    expected: Any,
    instance: Any,
    schema: dict[str, Any],
) -> Iterable[ValidationError]:
    del validator, schema
    if not json_type_sensitive_equal(instance, expected):
        yield ValidationError(
            f"{instance!r} is not the exact JSON-typed const {expected!r}"
        )


EXACT_JSON_TYPE_CHECKER = Draft202012Validator.TYPE_CHECKER.redefine(
    "integer",
    lambda _checker, instance: type(instance) is int,
)
ExactDraft202012Validator = validators.extend(
    Draft202012Validator,
    validators={"const": exact_json_const},
    type_checker=EXACT_JSON_TYPE_CHECKER,
)
STRICT_CONST_PROBE_SCHEMA = {
    "$schema": JSON_SCHEMA_2020_12,
    "type": "object",
    "additionalProperties": False,
    "required": ["profile_core_byte_count"],
    "properties": {
        "profile_core_byte_count": {
            "const": 1,
        }
    },
}
STRICT_INTEGER_PROBE_SCHEMA = {
    "$schema": JSON_SCHEMA_2020_12,
    "type": "object",
    "additionalProperties": False,
    "required": ["profile_core_byte_count"],
    "properties": {
        "profile_core_byte_count": {
            "type": "integer",
        }
    },
}
STRICT_INTEGER_PROBE_BASE = {"profile_core_byte_count": 1}
STRICT_PROBE_SCHEMAS = {
    "strict_const_record": (
        STRICT_CONST_PROBE_SCHEMA,
        "exact_json_type_mismatch",
    ),
    "strict_integer_record": (
        STRICT_INTEGER_PROBE_SCHEMA,
        "exact_json_integer_type_mismatch",
    ),
}


def path_binding(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return raw_digest(data), len(data)


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/") or pointer == "/":
        raise ValueError(f"invalid JSON Pointer {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def select(document: Any, pointer: str) -> Any:
    value = document
    for token in pointer_tokens(pointer):
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


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
            raise ValueError(f"unsupported operation {operation!r}")
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
            raise ValueError(f"unsupported operation {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def list_digest(paths: list[str]) -> str:
    return raw_digest(("\n".join(paths) + "\n").encode("utf-8"))


def recursive_string_count(value: Any, needle: str) -> int:
    if isinstance(value, str):
        return int(value == needle)
    if isinstance(value, list):
        return sum(recursive_string_count(item, needle) for item in value)
    if isinstance(value, dict):
        return sum(recursive_string_count(item, needle) for item in value.values())
    return 0


def recursive_digest_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if DIGEST_RE.fullmatch(value) else []
    if isinstance(value, list):
        return [
            digest
            for item in value
            for digest in recursive_digest_values(item)
        ]
    if isinstance(value, dict):
        return [
            digest
            for item in value.values()
            for digest in recursive_digest_values(item)
        ]
    return []


def recursive_values_for_key(value: Any, wanted: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key == wanted:
                found.append(item)
            found.extend(recursive_values_for_key(item, wanted))
    elif isinstance(value, list):
        for item in value:
            found.extend(recursive_values_for_key(item, wanted))
    return found


def collect_domain_contracts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            domain = properties.get("domain_separator")
            if isinstance(domain, dict) and isinstance(domain.get("const"), str):
                found.append(value)
        for item in value.values():
            found.extend(collect_domain_contracts(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_domain_contracts(item))
    return found


def collect_external_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        reference = value.get("$ref")
        if isinstance(reference, str) and not reference.startswith("#"):
            refs.add(reference.split("#", 1)[0])
        for item in value.values():
            refs.update(collect_external_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(collect_external_refs(item))
    return refs


def graph_has_cycle(nodes: list[str], edges: list[list[str]]) -> bool:
    adjacency = {node: [] for node in nodes}
    for subject, dependency in edges:
        adjacency.setdefault(subject, []).append(dependency)
        adjacency.setdefault(dependency, [])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(next_node) for next_node in adjacency.get(node, [])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in adjacency)


def contract_resources(contract: dict[str, Any]) -> list[dict[str, Any]]:
    resources = contract.get("resources")
    if not isinstance(resources, list):
        raise ValueError("contract.resources must be a list")
    return resources


def expected_resource_identities(contract: dict[str, Any]) -> list[list[Any]]:
    return [[row["path"], row["schema_id"]] for row in contract_resources(contract)]


def expected_domains(contract: dict[str, Any]) -> list[list[Any]]:
    return [
        [row["domain"], row["schema_id"]]
        for row in contract_resources(contract)
        if row["domain"] is not None
    ]


def expected_structural_vector_rows(
    contract: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_binding = {
        row["binding_id"]: row
        for row in contract_resources(contract)
    }
    for binding_id, (result_pointer, result_sentinel) in (
        STRUCTURAL_RESULT_BINDINGS.items()
    ):
        resource = by_binding[binding_id]
        filename_stem = Path(resource["path"]).name.removesuffix(
            ".schema.json"
        )
        rows.append(
            {
                "path": (
                    "tests/architecture-schema/fixtures/"
                    "prq-002b-structural-nonidentity/prq-002b-"
                    f"{filename_stem}.structural-nonidentity.json"
                ),
                "schema_path": resource["path"],
                "schema_id": resource["schema_id"],
                "result_digest_pointer": result_pointer,
                "result_digest_sentinel": result_sentinel,
            }
        )
    return rows


def validate_contract_exact_json_types(
    contract: dict[str, Any], findings: Findings
) -> None:
    framing = contract.get("framing")
    boundaries = contract.get("model_boundaries")
    migration = (
        boundaries.get("migration") if isinstance(boundaries, dict) else None
    )
    offline = (
        boundaries.get("offline_resolution")
        if isinstance(boundaries, dict)
        else None
    )
    authority = (
        boundaries.get("authority") if isinstance(boundaries, dict) else None
    )
    observed = {
        "predecessor_schema_path_count": contract.get(
            "predecessor_schema_path_count"
        ),
        "candidate_schema_path_count": contract.get(
            "candidate_schema_path_count"
        ),
        "framing_flags": {
            key: framing.get(key) if isinstance(framing, dict) else None
            for key in (
                "digest_contract_in_projection",
                "result_digest_in_projection",
                "product_digest_computation_permitted",
            )
        },
        "migration": migration,
        "offline_resolution": offline,
        "authority": authority,
    }
    expected = {
        "predecessor_schema_path_count": 120,
        "candidate_schema_path_count": 132,
        "framing_flags": {
            "digest_contract_in_projection": True,
            "result_digest_in_projection": False,
            "product_digest_computation_permitted": False,
        },
        "migration": {
            "status": (
                "explicit_scoped_candidate_migration_incomplete_unissued_"
                "unadmitted"
            ),
            "explicit": True,
            "current_consumer_migration_complete": False,
            "profile_final_acceptance_complete": False,
            "cross_profile_digest_equality_claimed": False,
            "probe_object_used_as_predecessor": False,
            "successor_resource_count": 12,
        },
        "offline_resolution": {
            "complete_offline_schema_registry": False,
            "historical_predecessor_bytes_complete": False,
            "git_reachability_is_durable_retention_proof": False,
            "network_or_mutable_fallback_allowed": False,
            "unresolved_historical_resource_count": None,
            "missing_count_must_not_be_interpreted_as_zero": True,
        },
        "authority": {
            "profile_issued": False,
            "schema_resources_admitted": False,
            "engine_contract_root_ref": None,
            "activation_ref": None,
            "gate_a_complete": False,
            "runtime_authorized": False,
        },
    }
    if not json_type_sensitive_equal(observed, expected):
        findings.add(
            "case_manifest_invalid",
            "contract count, framing, migration, resolver, or authority "
            "JSON types/values differ",
        )


def validate_structural_vector_contract_shape(
    contract: dict[str, Any], findings: Findings
) -> None:
    boundary = contract.get("structural_nonidentity_vectors")
    expected_keys = {
        "evidence_class",
        "path_glob",
        "vector_count",
        "identity_interpretation",
        "identity_recomputation_permitted",
        "product_identity_instance_count_delta",
        "dynamic_raw_digest_collision_scope",
        "profile_core_raw_digest_sentinel",
        "reserved_sentinel_digests",
        "vectors",
    }
    if not isinstance(boundary, dict) or set(boundary) != expected_keys:
        findings.add(
            "structural_nonidentity_vector_contract_mismatch",
            "closed structural-vector boundary is absent or has extra members",
        )
        return
    expected_rows = expected_structural_vector_rows(contract)
    if (
        not json_type_sensitive_equal(
            boundary.get("evidence_class"),
            "schema_valid_structural_nonidentity_vector_only",
        )
        or not json_type_sensitive_equal(
            boundary.get("path_glob"), STRUCTURAL_VECTOR_GLOB
        )
        or not json_type_sensitive_equal(boundary.get("vector_count"), 9)
        or not json_type_sensitive_equal(
            boundary.get("identity_interpretation"), "forbidden"
        )
        or boundary.get("identity_recomputation_permitted") is not False
        or not json_type_sensitive_equal(
            boundary.get("product_identity_instance_count_delta"), 0
        )
        or not json_type_sensitive_equal(
            boundary.get("dynamic_raw_digest_collision_scope"),
            ["schemas/*.json", "architecture/*.json"],
        )
        or not json_type_sensitive_equal(
            boundary.get("profile_core_raw_digest_sentinel"),
            RESERVED_STRUCTURAL_SENTINELS[0],
        )
        or not json_type_sensitive_equal(
            boundary.get("reserved_sentinel_digests"),
            list(RESERVED_STRUCTURAL_SENTINELS),
        )
        or not json_type_sensitive_equal(boundary.get("vectors"), expected_rows)
    ):
        findings.add(
            "structural_nonidentity_vector_contract_mismatch",
            "closed nine-vector mapping, sentinel set, or nonidentity law differs",
        )


def synthetic_successor_bindings(contract: dict[str, Any]) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for index, resource in enumerate(contract_resources(contract), start=1):
        digest = raw_digest(("synthetic:" + resource["path"]).encode("utf-8"))
        rows.append([resource["path"], resource["schema_id"], digest, 1000 + index])
    return rows


def safe_model(
    contract: dict[str, Any], predecessor: dict[str, Any]
) -> dict[str, Any]:
    bindings = synthetic_successor_bindings(contract)
    return {
        "resource_identities": expected_resource_identities(contract),
        "successor_bindings": copy.deepcopy(bindings),
        "actual_successor_bindings": copy.deepcopy(bindings),
        "predecessor_bindings": copy.deepcopy(predecessor["schemas"]),
        "domains": expected_domains(contract),
        "probe_hits": [],
        "product_instance_hits": [],
        "digest_graph": copy.deepcopy(contract["digest_graph"]),
        "framing": copy.deepcopy(contract["framing"]),
        "migration": copy.deepcopy(contract["model_boundaries"]["migration"]),
        "consumer_census": {
            "covered_paths": [row[0] for row in predecessor["schemas"]]
        },
        "offline_resolution": copy.deepcopy(
            contract["model_boundaries"]["offline_resolution"]
        ),
        "authority": copy.deepcopy(contract["model_boundaries"]["authority"]),
    }


def model_errors(
    model: dict[str, Any],
    contract: dict[str, Any],
    predecessor: dict[str, Any],
) -> set[str]:
    errors: set[str] = set()
    if not json_type_sensitive_equal(
        model.get("resource_identities"), expected_resource_identities(contract)
    ):
        errors.add("product_resource_identity_inventory_mismatch")
    if not json_type_sensitive_equal(
        model.get("successor_bindings"),
        model.get("actual_successor_bindings"),
    ):
        errors.add("successor_schema_binding_inventory_mismatch")
    if not json_type_sensitive_equal(
        model.get("predecessor_bindings"), predecessor.get("schemas")
    ):
        errors.add("predecessor_byte_binding_mismatch")
    if not json_type_sensitive_equal(
        model.get("domains"), expected_domains(contract)
    ):
        errors.add("product_domain_inventory_mismatch")
    if not json_type_sensitive_equal(model.get("probe_hits"), []):
        errors.add("probe_identity_contamination")
    if not json_type_sensitive_equal(model.get("product_instance_hits"), []):
        errors.add("product_instance_contamination")

    graph = model.get("digest_graph")
    if not isinstance(graph, dict):
        errors.add("digest_dependency_cycle")
    else:
        nodes = graph.get("nodes")
        edges = graph.get("edges")
        malformed = (
            not isinstance(nodes, list)
            or not all(isinstance(node, str) for node in nodes)
            or len(nodes) != len(set(nodes))
            or not isinstance(edges, list)
            or not all(
                isinstance(edge, list)
                and len(edge) == 2
                and all(isinstance(node, str) for node in edge)
                for edge in edges
            )
        )
        if malformed or graph_has_cycle(nodes, edges):
            errors.add("digest_dependency_cycle")

    if not json_type_sensitive_equal(
        model.get("framing"), contract.get("framing")
    ):
        errors.add("scoped_digest_framing_mismatch")

    migration = model.get("migration")
    expected_migration = contract["model_boundaries"]["migration"]
    if not isinstance(migration, dict):
        errors.add("migration_contract_incomplete")
    else:
        completion_keys = (
            "current_consumer_migration_complete",
            "profile_final_acceptance_complete",
        )
        if any(migration.get(key) is not False for key in completion_keys):
            errors.add("migration_completion_fabricated")
        structural = {
            key: value
            for key, value in migration.items()
            if key not in completion_keys
        }
        expected_structural = {
            key: value
            for key, value in expected_migration.items()
            if key not in completion_keys
        }
        if not json_type_sensitive_equal(structural, expected_structural):
            errors.add("migration_contract_incomplete")

    expected_paths = [row[0] for row in predecessor["schemas"]]
    census = model.get("consumer_census")
    if (
        not isinstance(census, dict)
        or not json_type_sensitive_equal(
            census.get("covered_paths"), expected_paths
        )
    ):
        errors.add("consumer_census_incomplete")

    if not json_type_sensitive_equal(
        model.get("offline_resolution"),
        contract["model_boundaries"]["offline_resolution"],
    ):
        errors.add("offline_resolution_boundary_mismatch")
    if not json_type_sensitive_equal(
        model.get("authority"), contract["model_boundaries"]["authority"]
    ):
        errors.add("authority_boundary_escalated")
    return errors


def validate_cases(
    cases_document: dict[str, Any],
    predecessor: dict[str, Any],
    findings: Findings,
) -> tuple[int, int]:
    contract = cases_document["contract"]
    expected_classes = set(cases_document.get("required_adversarial_classes", []))
    observed_classes: set[str] = set()
    mutation_witnesses: set[str] = set()
    safe_count = 0
    known_bad_count = 0

    for case in cases_document.get("cases", []):
        if not isinstance(case, dict):
            findings.add("case_manifest_invalid", "case is not an object")
            continue
        name = case.get("name", "<unnamed>")
        kind = case.get("kind")
        subject = case.get("subject", "model")
        base = (
            copy.deepcopy(STRICT_INTEGER_PROBE_BASE)
            if subject in STRICT_PROBE_SCHEMAS
            else safe_model(contract, predecessor)
        )
        if kind == "safe":
            safe_count += 1
            if set(case) != {"name", "kind"}:
                findings.add(
                    "case_manifest_invalid",
                    f"{name}: safe case carries mutation or attribution metadata",
                )
            errors = model_errors(base, contract, predecessor)
            if errors:
                findings.add(
                    "safe_model_rejected", f"{name}: observed {sorted(errors)}"
                )
            continue
        if kind != "known_bad":
            findings.add("case_manifest_invalid", f"{name}: unknown kind {kind!r}")
            continue
        if subject not in {"model", *STRICT_PROBE_SCHEMAS}:
            findings.add(
                "case_manifest_invalid",
                f"{name}: unknown mutation subject {subject!r}",
            )
            continue
        known_bad_count += 1
        adversarial_class = case.get("adversarial_class")
        if not isinstance(adversarial_class, str):
            findings.add(
                "case_manifest_invalid", f"{name}: missing adversarial_class"
            )
        else:
            observed_classes.add(adversarial_class)
        mutation = case.get("mutation")
        if not isinstance(mutation, dict):
            findings.add("case_manifest_invalid", f"{name}: no single mutation")
            continue
        witness = json.dumps(
            {"subject": subject, "mutation": mutation},
            sort_keys=True,
            separators=(",", ":"),
        )
        if witness in mutation_witnesses:
            findings.add(
                "case_manifest_invalid", f"{name}: duplicate mutation witness"
            )
        mutation_witnesses.add(witness)
        mutated = copy.deepcopy(base)
        try:
            apply_mutation(mutated, mutation)
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            findings.add("case_manifest_invalid", f"{name}: {exc}")
            continue
        if json_type_sensitive_equal(mutated, base):
            findings.add("case_manifest_invalid", f"{name}: mutation is a no-op")
            continue
        if subject in STRICT_PROBE_SCHEMAS:
            probe_schema, expected_probe_error = STRICT_PROBE_SCHEMAS[subject]
            stock_accepts_safe = Draft202012Validator(
                probe_schema
            ).is_valid(base)
            stock_accepts_mutation = Draft202012Validator(
                probe_schema
            ).is_valid(mutated)
            exact_accepts_safe = ExactDraft202012Validator(
                probe_schema
            ).is_valid(base)
            exact_accepts_mutation = ExactDraft202012Validator(
                probe_schema
            ).is_valid(mutated)
            observed = (
                {expected_probe_error}
                if (
                    stock_accepts_safe
                    and stock_accepts_mutation
                    and exact_accepts_safe
                    and not exact_accepts_mutation
                )
                else set()
            )
        else:
            observed = model_errors(mutated, contract, predecessor)
        expected = set(case.get("expected_errors", []))
        intended = case.get("intended_guard")
        if not isinstance(intended, str) or intended not in expected:
            findings.add(
                "case_attribution_invalid",
                f"{name}: intended guard must be one expected error",
            )
        if intended not in observed:
            findings.add(
                "case_intended_guard_did_not_fire",
                f"{name}: intended {intended!r}, observed {sorted(observed)}",
            )
        if observed != expected:
            findings.add(
                "case_error_inventory_mismatch",
                f"{name}: expected {sorted(expected)}, observed {sorted(observed)}",
            )

    if safe_count != 1:
        findings.add("case_manifest_invalid", f"safe count {safe_count}, expected 1")
    if observed_classes != expected_classes:
        findings.add(
            "case_class_inventory_mismatch",
            f"expected {sorted(expected_classes)}, observed {sorted(observed_classes)}",
        )
    return safe_count, known_bad_count


def validate_manifest_shape(
    predecessor: dict[str, Any],
    contract: dict[str, Any],
    findings: Findings,
) -> None:
    expected_keys = {
        "schema_version",
        "artifact_class",
        "source_commit",
        "source_tree",
        "row_shape",
        "schema_path_count",
        "schemas",
    }
    if set(predecessor) != expected_keys:
        findings.add(
            "predecessor_manifest_shape_mismatch",
            f"keys are {sorted(predecessor)}",
        )
    if predecessor.get("source_commit") != contract["predecessor_commit"]:
        findings.add("predecessor_manifest_identity_mismatch", "commit differs")
    if predecessor.get("source_tree") != contract["predecessor_tree"]:
        findings.add("predecessor_manifest_identity_mismatch", "tree differs")
    rows = predecessor.get("schemas")
    if not isinstance(rows, list):
        findings.add("predecessor_manifest_shape_mismatch", "schemas is not a list")
        return
    if (
        not json_type_sensitive_equal(
            predecessor.get("schema_path_count"),
            contract["predecessor_schema_path_count"],
        )
        or not json_type_sensitive_equal(
            len(rows), contract["predecessor_schema_path_count"]
        )
    ):
        findings.add(
            "predecessor_manifest_count_mismatch",
            f"declared {predecessor.get('schema_path_count')}, rows {len(rows)}",
        )
    if not all(
        isinstance(row, list)
        and len(row) == 4
        and isinstance(row[0], str)
        and isinstance(row[1], str)
        and isinstance(row[2], str)
        and type(row[3]) is int
        and row[3] > 0
        and DIGEST_RE.fullmatch(row[2])
        for row in rows
    ):
        findings.add(
            "predecessor_manifest_shape_mismatch",
            "every row must be [path,id,sha256 digest,positive byte count]",
        )
        return
    paths = [row[0] for row in rows]
    ids = [row[1] for row in rows]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        findings.add(
            "predecessor_manifest_path_inventory_mismatch",
            "paths are not sorted and unique",
        )
    if len(ids) != len(set(ids)):
        findings.add(
            "predecessor_manifest_identity_mismatch", "schema IDs are not unique"
        )


def load_candidate_file(
    path: Path, label: str, findings: Findings
) -> dict[str, Any] | None:
    relative = path.relative_to(ROOT).as_posix()
    if not path.is_file() or path.is_symlink():
        findings.add(f"{label}_missing_or_unsafe", relative)
        return None
    try:
        return load_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKey, ValueError) as exc:
        findings.add(f"{label}_invalid_json", f"{relative}: {exc}")
        return None


def declared_binding_rows(rows: Any) -> list[list[Any]] | None:
    if not isinstance(rows, list):
        return None
    result: list[list[Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            return None
        try:
            result.append(
                [
                    row["path"],
                    row["schema_id"],
                    row["raw_digest"],
                    row["byte_count"],
                ]
            )
        except KeyError:
            return None
    return result


def migration_binding_rows(rows: Any) -> list[list[Any]] | None:
    if not isinstance(rows, list):
        return None
    result: list[list[Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("successor"), dict):
            return None
        successor = row["successor"]
        try:
            result.append(
                [
                    successor["path"],
                    successor["schema_id"],
                    successor["raw_digest"],
                    successor["byte_count"],
                ]
            )
        except KeyError:
            return None
    return result


def binding_phase(rows: list[list[Any]] | None) -> str:
    if rows is None:
        return "invalid"
    states: set[str] = set()
    for _, _, digest, count in rows:
        if (
            isinstance(digest, str)
            and digest.startswith("__PRQ002B_FINAL_")
            and count is None
        ):
            states.add("placeholder")
        elif (
            isinstance(digest, str)
            and DIGEST_RE.fullmatch(digest)
            and type(count) is int
            and count > 0
        ):
            states.add("exact")
        else:
            states.add("invalid")
    return states.pop() if len(states) == 1 else "mixed"


def boundary_is_fail_closed(
    value: Any, expected_keys: list[str]
) -> tuple[bool, str]:
    if not isinstance(value, dict) or set(value) != set(expected_keys):
        return False, "key inventory differs"
    for key in expected_keys:
        observed = value[key]
        if key.endswith("_ref") or key.endswith("_digest"):
            if observed is not None:
                return False, f"{key} must be null"
        elif observed is not False:
            return False, f"{key} must be false"
    return True, ""


def validate_record_against_schema(
    document: dict[str, Any],
    schema: dict[str, Any],
    registry: Registry,
    label: str,
    findings: Findings,
) -> None:
    try:
        errors = sorted(
            ExactDraft202012Validator(
                schema, registry=registry, format_checker=FormatChecker()
            ).iter_errors(document),
            key=lambda error: list(error.absolute_path),
        )
    except Exception as exc:  # referencing exposes several resolution exceptions
        findings.add(f"{label}_schema_resolution_failed", str(exc))
        return
    if errors:
        sample = "; ".join(
            f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
            for error in errors[:5]
        )
        findings.add(f"{label}_schema_invalid", sample)


def validate_structural_nonidentity_vectors(
    contract: dict[str, Any],
    product_documents: dict[str, dict[str, Any]],
    registry: Registry,
    findings: Findings,
) -> None:
    boundary = contract.get("structural_nonidentity_vectors")
    if not isinstance(boundary, dict):
        return
    rows = boundary.get("vectors")
    if not isinstance(rows, list):
        return

    expected_paths = sorted(
        row.get("path")
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    )
    observed_paths = sorted(
        path.relative_to(ROOT).as_posix()
        for path in ROOT.glob(STRUCTURAL_VECTOR_GLOB)
        if path.is_file() or path.is_symlink()
    )
    if observed_paths != expected_paths or len(observed_paths) != 9:
        findings.add(
            "structural_nonidentity_vector_contract_mismatch",
            f"closed vector paths differ: expected={expected_paths}, "
            f"observed={observed_paths}",
        )

    raw_digest_scope: set[str] = set()
    for pattern in ("schemas/*.json", "architecture/*.json"):
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file() or path.is_symlink():
                continue
            raw_digest_scope.add(raw_digest(path.read_bytes()))
    reserved = set(RESERVED_STRUCTURAL_SENTINELS)
    collisions = sorted(reserved & raw_digest_scope)
    if collisions:
        findings.add(
            "product_instance_contamination",
            f"reserved vector sentinels collide with current raw bytes: {collisions}",
        )

    product_surface_paths = [
        row["path"] for row in contract_resources(contract)
    ] + [
        contract["records"][label]["path"]
        for label in ("core", "evidence", "migration")
    ]
    binding_tokens = [
        *expected_paths,
        *RESERVED_STRUCTURAL_SENTINELS,
    ]
    for path_text in product_surface_paths:
        path = ROOT / path_text
        if not path.is_file() or path.is_symlink():
            continue
        raw = path.read_bytes()
        hits = [
            token for token in binding_tokens if token.encode("utf-8") in raw
        ]
        if hits:
            findings.add(
                "product_instance_contamination",
                f"{path_text} binds structural-only vector material: {hits}",
            )

    observed_sentinels: set[str] = set()
    core_sentinel = RESERVED_STRUCTURAL_SENTINELS[0]
    for row in rows:
        if not isinstance(row, dict):
            continue
        path_text = row.get("path")
        schema_path_text = row.get("schema_path")
        if not isinstance(path_text, str) or not isinstance(
            schema_path_text, str
        ):
            continue
        path = ROOT / path_text
        if not path.is_file() or path.is_symlink():
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: missing, non-file, or symlink",
            )
            continue
        try:
            document = load_json(path)
        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
            DuplicateKey,
            ValueError,
        ) as exc:
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: {exc}",
            )
            continue

        digests = set(recursive_digest_values(document))
        observed_sentinels.update(digests)
        unknown_digests = sorted(digests - reserved)
        if not digests or unknown_digests:
            findings.add(
                "product_instance_contamination",
                f"{path_text}: digest values are not the closed sentinel set: "
                f"{unknown_digests}",
            )
        core_values = recursive_values_for_key(
            document, "profile_core_raw_digest"
        )
        if not core_values or any(value != core_sentinel for value in core_values):
            findings.add(
                "product_instance_contamination",
                f"{path_text}: profile core reference is not the reserved sentinel",
            )
        try:
            result_value = select(document, row["result_digest_pointer"])
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: result sentinel selector failed: {exc}",
            )
        else:
            if result_value != row.get("result_digest_sentinel"):
                findings.add(
                    "product_instance_contamination",
                    f"{path_text}: result digest is not its reserved sentinel",
                )

        schema = product_documents.get(schema_path_text)
        if schema is None or schema.get("$id") != row.get("schema_id"):
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: declaring schema identity differs",
            )
            continue
        try:
            validation_errors = sorted(
                ExactDraft202012Validator(
                    schema,
                    registry=registry,
                    format_checker=FormatChecker(),
                ).iter_errors(document),
                key=lambda error: list(error.absolute_path),
            )
        except Exception as exc:
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: offline schema resolution failed: {exc}",
            )
            continue
        if validation_errors:
            sample = "; ".join(
                f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
                for error in validation_errors[:5]
            )
            findings.add(
                "structural_nonidentity_vector_contract_mismatch",
                f"{path_text}: structurally invalid offline: {sample}",
            )

    if observed_sentinels != reserved:
        findings.add(
            "structural_nonidentity_vector_contract_mismatch",
            "observed digest sentinel union differs from the explicit reserved set",
        )


def repository_findings(
    cases_document: dict[str, Any],
    predecessor: dict[str, Any],
) -> Findings:
    findings = Findings()
    contract = cases_document["contract"]
    resources = contract_resources(contract)
    predecessor_rows = predecessor["schemas"]
    predecessor_paths = [row[0] for row in predecessor_rows]
    predecessor_ids = {row[1] for row in predecessor_rows}
    expected_product_paths = [row["path"] for row in resources]

    actual_schema_paths = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "schemas").glob("*.json")
    )
    post_prq_002b_paths = sorted(
        set(actual_schema_paths) & set(POST_PRQ_002B_SCHEMA_PATHS)
    )
    if post_prq_002b_paths and post_prq_002b_paths != sorted(
        POST_PRQ_002B_SCHEMA_PATHS
    ):
        findings.add(
            "post_prq_002b_schema_cohort_incomplete",
            "a later side-by-side cohort must be absent or present as its exact "
            f"12-resource inventory; observed={post_prq_002b_paths}",
        )
    prq_002b_schema_paths = sorted(
        set(actual_schema_paths) - set(POST_PRQ_002B_SCHEMA_PATHS)
    )
    expected_schema_paths = sorted(predecessor_paths + expected_product_paths)
    if prq_002b_schema_paths != expected_schema_paths:
        missing = sorted(set(expected_schema_paths) - set(prq_002b_schema_paths))
        extra = sorted(set(prq_002b_schema_paths) - set(expected_schema_paths))
        findings.add(
            "candidate_schema_path_inventory_mismatch",
            f"missing={missing}, extra={extra}",
        )
    if len(prq_002b_schema_paths) != contract["candidate_schema_path_count"]:
        findings.add(
            "candidate_schema_path_count_mismatch",
            f"observed {len(prq_002b_schema_paths)}, "
            f"expected {contract['candidate_schema_path_count']}",
        )

    predecessor_documents: dict[str, dict[str, Any]] = {}
    actual_predecessor_rows: list[list[Any]] = []
    for path_text, schema_id, digest, count in predecessor_rows:
        path = ROOT / path_text
        document = load_candidate_file(path, "predecessor_schema", findings)
        if document is None:
            continue
        predecessor_documents[path_text] = document
        observed_digest, observed_count = path_binding(path)
        actual_predecessor_rows.append(
            [path_text, document.get("$id"), observed_digest, observed_count]
        )
        if (
            document.get("$id") != schema_id
            or observed_digest != digest
            or observed_count != count
        ):
            findings.add(
                "predecessor_byte_binding_mismatch",
                f"{path_text} differs from frozen path/id/digest/count",
            )
    if actual_predecessor_rows != predecessor_rows:
        findings.add(
            "predecessor_byte_binding_mismatch",
            "current 120-path predecessor cohort is not byte-exact",
        )

    product_documents: dict[str, dict[str, Any]] = {}
    actual_product_bindings: list[list[Any]] = []
    resource_identities: list[list[Any]] = []
    schema_documents_by_id: dict[str, dict[str, Any]] = {}
    for path_text, document in predecessor_documents.items():
        schema_id = document.get("$id")
        if isinstance(schema_id, str):
            schema_documents_by_id[schema_id] = document

    for resource in resources:
        path_text = resource["path"]
        path = ROOT / path_text
        document = load_candidate_file(path, "successor_schema", findings)
        if document is None:
            continue
        product_documents[path_text] = document
        schema_id = document.get("$id")
        resource_identities.append([path_text, schema_id])
        digest, count = path_binding(path)
        actual_product_bindings.append([path_text, schema_id, digest, count])
        if document.get("$schema") != JSON_SCHEMA_2020_12:
            findings.add(
                "successor_schema_dialect_mismatch",
                f"{path_text}: $schema is {document.get('$schema')!r}",
            )
        try:
            Draft202012Validator.check_schema(document)
        except Exception as exc:
            findings.add("successor_schema_metaschema_invalid", f"{path_text}: {exc}")
        if isinstance(schema_id, str):
            if schema_id in schema_documents_by_id:
                findings.add(
                    "product_resource_identity_inventory_mismatch",
                    f"duplicate schema ID {schema_id}",
                )
            schema_documents_by_id[schema_id] = document

    # Load records through contract-owned selectors so integration field changes
    # are localized to cases.json rather than scattered through this checker.
    records: dict[str, dict[str, Any] | None] = {}
    for label, record_contract in contract["records"].items():
        records[label] = load_candidate_file(
            ROOT / record_contract["path"], f"{label}_record", findings
        )

    registry = Registry()
    for schema_id, schema in schema_documents_by_id.items():
        try:
            registry = registry.with_resource(
                schema_id, Resource.from_contents(schema)
            )
        except Exception as exc:
            findings.add(
                "schema_registry_construction_failed", f"{schema_id}: {exc}"
            )
    for label, document in records.items():
        if document is None:
            continue
        schema_path = ROOT / contract["records"][label]["schema_path"]
        schema = product_documents.get(
            schema_path.relative_to(ROOT).as_posix()
        )
        if schema is not None:
            validate_record_against_schema(
                document, schema, registry, label, findings
            )

    validate_structural_nonidentity_vectors(
        contract, product_documents, registry, findings
    )

    model = safe_model(contract, predecessor)
    model["resource_identities"] = resource_identities
    model["actual_successor_bindings"] = actual_product_bindings

    suite_json_paths = sorted(
        path.relative_to(SUITE).as_posix()
        for path in SUITE.rglob("*.json")
        if path.is_file() or path.is_symlink()
    )
    product_instance_hits = sorted(
        path
        for path in suite_json_paths
        if path not in ALLOWED_SUITE_JSON_PATHS
    )
    model["product_instance_hits"] = product_instance_hits
    if product_instance_hits:
        findings.add(
            "product_instance_contamination",
            "suite-local JSON inventory contains forbidden product-instance "
            f"artifacts: {product_instance_hits}",
        )

    core = records.get("core")
    evidence = records.get("evidence")
    migration = records.get("migration")
    selectors = {
        label: contract["records"][label]["selectors"]
        for label in contract["records"]
    }

    def selected(label: str, name: str, default: Any = None) -> Any:
        document = records.get(label)
        if document is None:
            return default
        try:
            return select(document, selectors[label][name])
        except (IndexError, KeyError, TypeError, ValueError) as exc:
            findings.add(
                f"{label}_record_shape_mismatch",
                f"{name} selector {selectors[label].get(name)!r}: {exc}",
            )
            return default

    core_bindings = declared_binding_rows(
        selected("core", "successor_schema_bindings")
    )
    evidence_bindings = declared_binding_rows(
        selected("evidence", "successor_schema_bindings")
    )
    migration_bindings = migration_binding_rows(
        selected("migration", "successor_resources")
    )
    model["successor_bindings"] = core_bindings
    phases = {
        binding_phase(core_bindings),
        binding_phase(evidence_bindings),
        binding_phase(migration_bindings),
    }
    if phases == {"placeholder"}:
        findings.add(
            "successor_schema_bindings_not_final",
            "all three records still carry placeholders; exact freeze is required",
        )
    elif phases != {"exact"}:
        findings.add(
            "successor_schema_binding_phase_mixed",
            f"core/evidence/migration phases are {sorted(phases)}",
        )
    if core_bindings != actual_product_bindings:
        findings.add(
            "successor_schema_binding_inventory_mismatch",
            "core bindings do not equal exact 12 local schema bytes",
        )
    if evidence_bindings != actual_product_bindings:
        findings.add(
            "successor_schema_binding_inventory_mismatch",
            "evidence bindings do not equal exact 12 local schema bytes",
        )
    if migration_bindings != actual_product_bindings:
        findings.add(
            "successor_schema_binding_inventory_mismatch",
            "migration dispositions do not equal exact 12 local schema bytes",
        )

    profile = contract["profile"]
    if (
        selected("core", "profile_id") != profile["successor_id"]
        or selected("core", "profile_version") != profile["successor_version"]
        or selected("core", "status") != profile["core_status"]
        or selected("evidence", "status") != profile["evidence_status"]
        or selected("migration", "status") != profile["migration_status"]
    ):
        findings.add(
            "profile_successor_identity_or_status_mismatch",
            "profile IDs, versions, or unissued candidate statuses differ",
        )

    # Every scoped product schema carries the exact four-field successor ref;
    # the raw core digest remains an instance value, never a schema const.
    expected_ref_members = [
        "profile_id",
        "profile_version",
        "profile_core_schema_id",
        "profile_core_raw_digest",
    ]
    for resource in resources:
        if resource["domain"] is None:
            continue
        document = product_documents.get(resource["path"])
        reference = (
            document.get("$defs", {}).get("profile_reference")
            if isinstance(document, dict)
            else None
        )
        properties = reference.get("properties") if isinstance(reference, dict) else None
        if (
            not isinstance(reference, dict)
            or reference.get("required") != expected_ref_members
            or not isinstance(properties, dict)
            or properties.get("profile_id", {}).get("const")
            != profile["successor_id"]
            or properties.get("profile_version", {}).get("const")
            != profile["successor_version"]
            or properties.get("profile_core_schema_id", {}).get("const")
            != profile["successor_core_schema_id"]
            or "const" in properties.get("profile_core_raw_digest", {})
        ):
            findings.add(
                "successor_profile_reference_contract_mismatch",
                resource["path"],
            )

    # Exact scoped domains are derived from product schema constants, then
    # compared with the core and evidence records.  Predecessor domains are
    # independently discovered from the frozen 120 documents.
    product_domains: list[list[Any]] = []
    domain_contracts: dict[str, dict[str, Any]] = {}
    for resource in resources:
        domain = resource["domain"]
        if domain is None:
            continue
        document = product_documents.get(resource["path"])
        contracts = collect_domain_contracts(document) if document else []
        matching = [
            item
            for item in contracts
            if item.get("properties", {})
            .get("domain_separator", {})
            .get("const")
            == domain
        ]
        if len(matching) != 1:
            findings.add(
                "product_domain_inventory_mismatch",
                f"{resource['path']}: expected one {domain!r} contract, got {len(matching)}",
            )
        else:
            product_domains.append([domain, resource["schema_id"]])
            domain_contracts[domain] = matching[0]
    model["domains"] = product_domains
    predecessor_domains: set[str] = set()
    for document in predecessor_documents.values():
        for item in collect_domain_contracts(document):
            domain = item.get("properties", {}).get("domain_separator", {}).get("const")
            if isinstance(domain, str):
                predecessor_domains.add(domain)
    overlap = set(row[0] for row in product_domains) & predecessor_domains
    if overlap:
        findings.add(
            "product_domain_inventory_mismatch",
            f"successor domains collide with predecessor constants: {sorted(overlap)}",
        )

    core_domain_rows = selected("core", "domain_registry", [])
    binding_id_to_resource = {row["binding_id"]: row for row in resources}
    normalized_core_domains: list[list[Any]] = []
    if isinstance(core_domain_rows, list):
        for row in core_domain_rows:
            if not isinstance(row, dict):
                continue
            resource = binding_id_to_resource.get(row.get("declaring_schema_binding_id"))
            normalized_core_domains.append(
                [
                    row.get("domain_separator"),
                    resource.get("schema_id") if resource else None,
                ]
            )
            if row.get("registration_status") != (
                "scoped_successor_candidate_unissued_unadmitted"
            ):
                findings.add(
                    "product_domain_inventory_mismatch",
                    f"{row.get('domain_separator')}: status escalated",
                )
    if normalized_core_domains != expected_domains(contract):
        findings.add(
            "product_domain_inventory_mismatch",
            "core domain registry differs from exact nine-domain contract",
        )
    evidence_domains = selected("evidence", "domain_inventory", {})
    if (
        not isinstance(evidence_domains, dict)
        or evidence_domains.get("declared_domain_count") != 9
        or evidence_domains.get("domain_constants_unique") is not True
        or evidence_domains.get("domain_separators")
        != [row[0] for row in expected_domains(contract)]
        or evidence_domains.get("domains_are_scoped_to_successor_resources") is not True
        or evidence_domains.get("current_consumers_admitted") is not False
    ):
        findings.add(
            "product_domain_inventory_mismatch",
            "evidence domain inventory differs from exact nine-domain contract",
        )

    framing = selected("core", "framing")
    if isinstance(framing, dict):
        observed_framing = {
            key: framing.get(key) for key in contract["framing"]
        }
    else:
        observed_framing = framing
    model["framing"] = observed_framing
    for domain, digest_schema in domain_contracts.items():
        properties = digest_schema.get("properties", {})
        required = digest_schema.get("required")
        algorithm = properties.get("algorithm", {}).get("const")
        included = [
            item.get("const") if isinstance(item, dict) else None
            for item in properties.get("included_json_pointers", {}).get(
                "prefixItems", []
            )
        ]
        excluded = [
            item.get("const") if isinstance(item, dict) else None
            for item in properties.get("excluded_json_pointers", {}).get(
                "prefixItems", []
            )
        ]
        if (
            required != contract["framing"]["digest_contract_exact_members"]
            or algorithm != contract["framing"]["algorithm"]
            or not included
            or not excluded
            or len(included) != len(set(included))
            or len(excluded) != len(set(excluded))
            or set(included) & set(excluded)
            or any(not isinstance(pointer, str) or not pointer.startswith("/") for pointer in included + excluded)
        ):
            findings.add(
                "scoped_digest_framing_mismatch",
                f"{domain}: schema-fixed framing is ambiguous or inconsistent",
            )

    graph = selected("core", "digest_graph")
    graph_model: dict[str, Any] = {}
    if isinstance(graph, dict):
        graph_model = {
            "edge_direction": graph.get("edge_direction"),
            "nodes": graph.get("nodes"),
            "edges": [
                [edge.get("subject"), edge.get("dependency")]
                for edge in graph.get("edges", [])
                if isinstance(edge, dict)
            ],
        }
        if (
            graph.get("node_ids_unique") is not True
            or graph.get("self_edges_allowed") is not False
            or graph.get("cycles_allowed") is not False
            or graph.get("core_raw_digest_inside_core") is not False
            or graph.get("successor_core_raw_digest_inside_successor_schema_bytes")
            is not False
            or graph.get("cross_resource_schema_reference_cycles_allowed") is not False
        ):
            findings.add(
                "digest_dependency_graph_inventory_mismatch",
                "graph nonclaim flags differ",
            )
    model["digest_graph"] = graph_model
    if graph_model != contract["digest_graph"]:
        findings.add(
            "digest_dependency_graph_inventory_mismatch",
            "declared nodes or edges differ from the complete contract graph",
        )

    # Independent JSON Schema dependency graph: external references must resolve
    # to exact local resources and the new 12-resource subgraph must be acyclic.
    schema_edges: list[list[str]] = []
    product_ids = {resource["schema_id"] for resource in resources}
    for resource in resources:
        document = product_documents.get(resource["path"])
        if document is None:
            continue
        for reference in collect_external_refs(document):
            if reference not in schema_documents_by_id:
                findings.add(
                    "offline_resolution_boundary_mismatch",
                    f"{resource['path']}: unresolved $ref {reference}",
                )
            if reference in product_ids:
                schema_edges.append([resource["schema_id"], reference])
    if graph_has_cycle(sorted(product_ids), schema_edges):
        findings.add(
            "digest_dependency_cycle",
            "successor schema reference subgraph contains a cycle",
        )

    # A schema may constrain a four-field reference but may not const-embed the
    # successor core digest: core->schema plus schema->core would be a raw-byte
    # dependency cycle.
    if core is not None:
        core_bytes = (ROOT / contract["records"]["core"]["path"]).read_bytes()
        core_digest = raw_digest(core_bytes)
        if core_digest.encode("ascii") in core_bytes:
            findings.add("digest_dependency_cycle", "core contains its own raw digest")
        for path_text in expected_product_paths:
            path = ROOT / path_text
            if path.is_file() and core_digest.encode("ascii") in path.read_bytes():
                findings.add(
                    "digest_dependency_cycle",
                    f"{path_text} const-embeds successor core digest",
                )
        if evidence is not None:
            core_binding = selected("evidence", "core_binding", {})
            core_schema_path = ROOT / contract["records"]["core"]["schema_path"]
            core_schema_digest, core_schema_count = (
                path_binding(core_schema_path)
                if core_schema_path.is_file()
                else (None, None)
            )
            if (
                not isinstance(core_binding, dict)
                or core_binding.get("profile_core_raw_digest") != core_digest
                or core_binding.get("profile_core_byte_count") != len(core_bytes)
                or core_binding.get("profile_core_schema_raw_digest")
                != core_schema_digest
                or core_binding.get("profile_core_schema_byte_count")
                != core_schema_count
                or core_binding.get("core_contains_self_hash") is not False
                or core_binding.get("binding_is_external_to_core") is not True
                or core_binding.get("binding_status")
                != "exact_retained_candidate_bytes"
            ):
                findings.add(
                    "profile_core_raw_binding_mismatch",
                    "evidence does not externally bind exact successor core/schema bytes",
                )
        if migration is not None:
            successor_profile = selected("migration", "successor_profile", {})
            evidence_path = ROOT / contract["records"]["evidence"]["path"]
            evidence_bytes = evidence_path.read_bytes() if evidence_path.is_file() else None
            evidence_digest = raw_digest(evidence_bytes) if evidence_bytes is not None else None
            if (
                not isinstance(successor_profile, dict)
                or successor_profile.get("profile_core_raw_digest") != core_digest
                or successor_profile.get("profile_core_byte_count") != len(core_bytes)
                or successor_profile.get("profile_evidence_raw_digest")
                != evidence_digest
                or successor_profile.get("profile_evidence_byte_count")
                != (len(evidence_bytes) if evidence_bytes is not None else None)
                or successor_profile.get("profile_issued") is not False
                or successor_profile.get("binding_status")
                != "exact_retained_candidate_core_bytes"
            ):
                findings.add(
                    "profile_core_raw_binding_mismatch",
                    "migration does not bind exact successor core/evidence bytes",
                )
        if evidence is not None and migration is not None:
            migration_binding = selected("evidence", "migration", {})
            migration_path = ROOT / contract["records"]["migration"]["path"]
            migration_digest = (
                raw_digest(migration_path.read_bytes())
                if migration_path.is_file()
                else None
            )
            if (
                isinstance(migration_binding, dict)
                and (
                    migration_binding.get("migration_record_is_dependency_of_this_evidence")
                    is not False
                    or migration_binding.get("migration_record_raw_digest") is not None
                    or (
                        migration_digest is not None
                        and migration_digest.encode("ascii")
                        in (ROOT / contract["records"]["evidence"]["path"]).read_bytes()
                    )
                )
            ):
                findings.add(
                    "digest_dependency_cycle",
                    "evidence depends on migration while migration depends on evidence",
                )

    # All three records must retain the exact predecessor profile/evidence bytes.
    predecessor_expected_paths = {
        "profile_core_path": "architecture/canonicalization-profile-core-candidate.json",
        "profile_core_schema_path": "schemas/canonicalization-profile-core.schema.json",
        "profile_evidence_path": "architecture/canonicalization-profile-candidate-evidence.json",
        "profile_evidence_schema_path": "schemas/canonicalization-profile-candidate-evidence.schema.json",
    }
    predecessor_expected: dict[str, Any] = {
        "profile_id": profile["predecessor_id"],
        "profile_version": profile["predecessor_version"],
        "profile_issued": False,
        **predecessor_expected_paths,
        "binding_status": "exact_retained_unissued_predecessor_bytes",
    }
    for prefix, path_text in (
        ("profile_core", predecessor_expected_paths["profile_core_path"]),
        ("profile_core_schema", predecessor_expected_paths["profile_core_schema_path"]),
        ("profile_evidence", predecessor_expected_paths["profile_evidence_path"]),
        ("profile_evidence_schema", predecessor_expected_paths["profile_evidence_schema_path"]),
    ):
        path = ROOT / path_text
        if path.is_file():
            digest, count = path_binding(path)
            predecessor_expected[f"{prefix}_raw_digest"] = digest
            predecessor_expected[f"{prefix}_byte_count"] = count
    predecessor_expected["profile_core_schema_id"] = (
        "urn:odeya:schema:canonicalization-profile-core:0.5.0"
    )
    predecessor_expected["profile_evidence_schema_id"] = (
        "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.5.0"
    )
    for label, selector_name in (
        ("core", "predecessor_binding"),
        ("evidence", "predecessor_binding"),
        ("migration", "predecessor_profile"),
    ):
        observed = selected(label, selector_name, {})
        if (
            not isinstance(observed, dict)
            or any(observed.get(key) != value for key, value in predecessor_expected.items())
        ):
            findings.add(
                "predecessor_byte_binding_mismatch",
                f"{label} predecessor binding differs from exact retained bytes",
            )

    # Direct-consumer census is independently derived from the exact frozen
    # predecessor paths, not from the new 132-path live glob.
    direct_paths: list[str] = []
    non_direct_paths: list[str] = []
    literal_count = 0
    for path_text in predecessor_paths:
        document = predecessor_documents.get(path_text)
        count = (
            recursive_string_count(document, profile["predecessor_id"])
            if document is not None
            else 0
        )
        literal_count += count
        (direct_paths if count else non_direct_paths).append(path_text)
    census = selected("migration", "consumer_census", {})
    covered_paths: list[str] = []
    if isinstance(census, dict):
        covered_paths = (
            census.get("retained_predecessor_direct_consumer_paths", [])
            + census.get("retained_non_direct_consumer_paths", [])
        )
    model["consumer_census"] = {"covered_paths": sorted(covered_paths)}
    if (
        not isinstance(census, dict)
        or census.get("baseline_product_schema_count") != 120
        or census.get("retained_predecessor_direct_consumer_count")
        != len(direct_paths)
        or census.get("retained_predecessor_literal_occurrence_count")
        != literal_count
        or census.get("retained_predecessor_direct_consumer_paths") != direct_paths
        or census.get("retained_predecessor_direct_consumer_path_list_sha256")
        != list_digest(direct_paths)
        or census.get("retained_non_direct_consumer_count") != len(non_direct_paths)
        or census.get("retained_non_direct_consumer_paths") != non_direct_paths
        or census.get("retained_non_direct_consumer_path_list_sha256")
        != list_digest(non_direct_paths)
        or census.get("successor_resource_count") != 12
        or census.get("successor_resource_paths") != expected_product_paths
        or census.get("retained_predecessor_consumers_rewritten") is not False
        or census.get("retained_predecessor_consumers_reinterpreted") is not False
        or census.get("current_consumer_migration_complete") is not False
    ):
        findings.add(
            "consumer_census_incomplete",
            "scoped 106/14/12 census does not independently reconcile to 132",
        )
    evidence_census = selected("evidence", "consumer_census", {})
    if (
        not isinstance(evidence_census, dict)
        or evidence_census.get("baseline_commit") != contract["predecessor_commit"]
        or evidence_census.get("baseline_tree") != contract["predecessor_tree"]
        or evidence_census.get("baseline_product_schema_count") != 120
        or evidence_census.get("successor_schema_resource_count") != 12
        or evidence_census.get("candidate_product_schema_count") != 132
        or evidence_census.get("retained_predecessor_direct_consumer_count") != 106
        or evidence_census.get("retained_predecessor_literal_occurrence_count") != 484
        or evidence_census.get("retained_non_direct_consumer_count") != 14
        or evidence_census.get("historical_and_probe_material_in_product_census")
        is not False
        or evidence_census.get("current_consumer_migration_complete") is not False
    ):
        findings.add(
            "consumer_census_incomplete",
            "evidence census summary differs from independently derived scope",
        )

    # Migration is explicit and deliberately incomplete.  New resources have no
    # predecessor object; six side-by-side successors bind exact unissued bytes.
    migration_abstract = copy.deepcopy(contract["model_boundaries"]["migration"])
    if isinstance(migration, dict):
        migration_abstract["status"] = migration.get("status")
        migration_abstract["current_consumer_migration_complete"] = (
            census.get("current_consumer_migration_complete")
            if isinstance(census, dict)
            else None
        )
        completion = selected("migration", "authority", {})
        migration_abstract["profile_final_acceptance_complete"] = (
            completion.get("operator_acceptance_complete")
            if isinstance(completion, dict)
            else None
        )
        law = selected("migration", "digest_migration_law", {})
        migration_abstract["cross_profile_digest_equality_claimed"] = (
            law.get("same_digest_means_same_identity_across_profiles")
            if isinstance(law, dict)
            else None
        )
        migration_abstract["probe_object_used_as_predecessor"] = (
            law.get("probe_instances_claimed") if isinstance(law, dict) else None
        )
        migration_abstract["successor_resource_count"] = (
            len(selected("migration", "successor_resources", []))
            if isinstance(selected("migration", "successor_resources", []), list)
            else None
        )
        migration_abstract["explicit"] = (
            isinstance(law, dict)
            and law.get("predecessor_digest_relabeling") == "forbidden"
            and law.get("predecessor_digest_inheritance") == "forbidden"
            and law.get("implicit_profile_upcast") == "forbidden"
            and law.get("issued_predecessor_instances_claimed") is False
            and law.get("probe_instances_claimed") is False
            and law.get("product_members_or_snapshots_exist") is False
            and law.get("migration_execution_complete") is False
        )
    model["migration"] = migration_abstract

    dispositions = selected("migration", "successor_resources", [])
    if isinstance(dispositions, list):
        by_id = {
            row.get("resource_id"): row
            for row in dispositions
            if isinstance(row, dict)
        }
        predecessor_by_id = {row[1]: row for row in predecessor_rows}
        if set(by_id) != {row["binding_id"] for row in resources}:
            findings.add(
                "migration_contract_incomplete",
                "resource disposition IDs do not cover exact 12 resources",
            )
        for resource in resources:
            row = by_id.get(resource["binding_id"], {})
            predecessor_id = resource["predecessor_schema_id"]
            observed_predecessor = row.get("predecessor") if isinstance(row, dict) else None
            if predecessor_id is None:
                if observed_predecessor is not None or row.get(
                    "issued_predecessor_claimed"
                ) is not False:
                    findings.add(
                        "migration_contract_incomplete",
                        f"{resource['binding_id']}: new resource claims a predecessor",
                    )
            else:
                frozen = predecessor_by_id.get(predecessor_id)
                if (
                    frozen is None
                    or not isinstance(observed_predecessor, dict)
                    or observed_predecessor.get("schema_id") != predecessor_id
                    or observed_predecessor.get("path") != frozen[0]
                    or observed_predecessor.get("raw_digest") != frozen[2]
                    or observed_predecessor.get("byte_count") != frozen[3]
                    or observed_predecessor.get("issued") is not False
                ):
                    findings.add(
                        "migration_contract_incomplete",
                        f"{resource['binding_id']}: predecessor lineage differs",
                    )
    else:
        findings.add(
            "migration_contract_incomplete", "resource dispositions are absent"
        )

    exclusions = selected("migration", "probe_exclusions", {})
    if (
        not isinstance(exclusions, dict)
        or exclusions.get("product_consumer_census_is_limited_to") != "schemas/*.json"
        or exclusions.get("probe_identifiers_domains_objects_digests_or_results_promoted")
        is not False
        or exclusions.get("historical_git_only_schema_resources_counted_as_current_consumers")
        is not False
        or exclusions.get("historical_evidence_rewritten") is not False
    ):
        findings.add(
            "probe_identity_contamination",
            "migration exclusions do not keep probe/history outside product identity",
        )

    # Scan identities, domains, retained probe scope, and the exact probe-core
    # digest.  Generic negative fields named "probe" remain permitted.
    probe_hits: list[str] = []
    scan_paths = expected_product_paths + [
        contract["records"][label]["path"] for label in ("core", "evidence", "migration")
    ]
    for path_text in scan_paths:
        path = ROOT / path_text
        if not path.is_file():
            continue
        text = path.read_text("utf-8")
        for token in contract["forbidden_probe_tokens"]:
            if token in text:
                probe_hits.append(f"{path_text}:{token}")
    model["probe_hits"] = probe_hits

    # Offline closure remains explicitly incomplete.  The exact current bytes
    # can resolve while the historical reissue archive remains absent.
    evidence_offline = selected("evidence", "offline_resolution", {})
    migration_offline = selected("migration", "offline_resolution", {})
    core_parser = core.get("parser_contract", {}) if isinstance(core, dict) else {}
    resolver_modes_exact = (
        isinstance(evidence_offline, dict)
        and evidence_offline.get("resolver_mode")
        == "repository_local_exact_bytes_and_reachable_git_objects_only"
        and isinstance(migration_offline, dict)
        and migration_offline.get("resolver_mode")
        == "repository_local_exact_bytes_and_reachable_git_objects_only"
        and isinstance(core_parser, dict)
        and core_parser.get("network_access") == "disabled"
        and core_parser.get("schema_resolution")
        == "preloaded_exact_resource_id_and_raw_digest"
    )
    offline_abstract = {
        "complete_offline_schema_registry": (
            migration_offline.get("complete_offline_schema_registry")
            if isinstance(migration_offline, dict)
            else None
        ),
        "historical_predecessor_bytes_complete": (
            migration_offline.get(
                "historical_reissue_predecessor_bytes_materialized_in_current_tree"
            )
            if isinstance(migration_offline, dict)
            else None
        ),
        "git_reachability_is_durable_retention_proof": (
            migration_offline.get("git_object_reachability_is_durable_retention_proof")
            if isinstance(migration_offline, dict)
            else None
        ),
        "network_or_mutable_fallback_allowed": not resolver_modes_exact,
        "unresolved_historical_resource_count": (
            migration_offline.get("unresolved_historical_resource_count")
            if isinstance(migration_offline, dict)
            else "missing"
        ),
        "missing_count_must_not_be_interpreted_as_zero": (
            migration_offline.get("missing_count_must_not_be_interpreted_as_zero")
            if isinstance(migration_offline, dict)
            else None
        ),
    }
    model["offline_resolution"] = offline_abstract
    if (
        not isinstance(evidence_offline, dict)
        or evidence_offline.get("complete_offline_schema_registry") is not False
        or evidence_offline.get(
            "historical_reissue_predecessor_bytes_materialized_in_current_tree"
        )
        is not False
        or evidence_offline.get("git_object_reachability_is_durable_retention_proof")
        is not False
        or evidence_offline.get("external_content_addressed_archive_verified")
        is not False
        or evidence_offline.get("unresolved_historical_resource_count") is not None
        or evidence_offline.get("missing_count_must_not_be_interpreted_as_zero")
        is not True
        or evidence_offline.get("resolution_status")
        != "incomplete_blocking_before_migration_admission_or_gate_a"
        or not resolver_modes_exact
        or not isinstance(migration_offline, dict)
        or migration_offline.get("current_predecessor_profile_resources_resolve")
        is not True
        or migration_offline.get("current_successor_resource_resolution_complete")
        is not True
        or migration_offline.get("migration_replay_complete") is not False
    ):
        findings.add(
            "offline_resolution_boundary_mismatch",
            "current bytes and unresolved historical archive boundary differ",
        )

    # Exact fail-closed authority dictionaries; missing keys cannot pass by
    # absence and unknown keys cannot smuggle another authority channel.
    authority_contract = contract["authority_boundary_keys"]
    core_authority = selected("core", "authority", {})
    evidence_review = selected("evidence", "review", {})
    evidence_authority = selected("evidence", "authority", {})
    migration_authority = selected("migration", "authority", {})
    for label, boundary, expected_keys in (
        ("core", core_authority, authority_contract["core"]),
        ("evidence_review", evidence_review, authority_contract["evidence_review"]),
        ("evidence", evidence_authority, authority_contract["evidence"]),
    ):
        ok, detail = boundary_is_fail_closed(boundary, expected_keys)
        if not ok:
            findings.add("authority_boundary_escalated", f"{label}: {detail}")
    if not isinstance(migration_authority, dict):
        findings.add("authority_boundary_escalated", "migration boundary absent")
    else:
        observed_migration_authority = {
            key: migration_authority.get(key)
            for key in authority_contract["migration"]
        }
        ok, detail = boundary_is_fail_closed(
            observed_migration_authority, authority_contract["migration"]
        )
        if not ok:
            findings.add("authority_boundary_escalated", f"migration: {detail}")
    model["authority"] = {
        "profile_issued": (
            core_authority.get("profile_issued")
            if isinstance(core_authority, dict)
            else None
        ),
        "schema_resources_admitted": (
            evidence_authority.get("schema_resources_admitted")
            if isinstance(evidence_authority, dict)
            else None
        ),
        "engine_contract_root_ref": (
            evidence_authority.get("engine_contract_root_ref")
            if isinstance(evidence_authority, dict)
            else "missing"
        ),
        "activation_ref": (
            evidence_authority.get("activation_ref")
            if isinstance(evidence_authority, dict)
            else "missing"
        ),
        "gate_a_complete": (
            evidence_authority.get("gate_a_complete")
            if isinstance(evidence_authority, dict)
            else None
        ),
        "runtime_authorized": (
            evidence_authority.get("runtime_authorized")
            if isinstance(evidence_authority, dict)
            else None
        ),
    }

    # Exact finalized candidate phase: local bytes are bound and schema-valid;
    # conformance, review, offline registry, issuance, and authority remain open.
    evidence_framing = selected("evidence", "framing", {})
    if (
        not isinstance(evidence_framing, dict)
        or evidence_framing.get("framing_precedes_product_digest_computation")
        is not True
        or any(
            evidence_framing.get(key) != 0
            for key in (
                "product_member_instance_count",
                "product_snapshot_instance_count",
                "product_root_instance_count",
                "product_digest_count",
            )
        )
        or evidence_framing.get("profile_core_self_hash_observed") is not False
        or evidence_framing.get(
            "schema_contains_successor_core_raw_digest_observed"
        )
        is not False
        or evidence_framing.get("digest_inheritance_from_predecessor_allowed")
        is not False
    ):
        findings.add(
            "scoped_digest_framing_mismatch",
            "evidence does not retain zero-product-digest framing boundary",
        )
    conformance = (
        evidence.get("conformance_evidence")
        if isinstance(evidence, dict)
        else None
    )
    if (
        not isinstance(conformance, dict)
        or any(
            conformance.get(key) is not None
            for key in (
                "successor_suite_id",
                "case_count",
                "accepted_count",
                "refused_count",
                "unclassified_error_count",
                "source_separated_implementation_count",
                "implementation_agreement",
            )
        )
        or conformance.get("organizational_independence_proven") is not False
        or conformance.get("independent_host_reproduction_complete") is not False
        or conformance.get("successor_profile_conformance_complete") is not False
        or conformance.get("known_bad_self_test_complete") is not False
        or conformance.get("missing_values_must_not_be_interpreted_as_zero")
        is not True
    ):
        findings.add(
            "profile_conformance_completion_fabricated",
            "isolated integration known-bads cannot be promoted to full profile conformance",
        )
    completion = migration_authority
    if (
        not isinstance(completion, dict)
        or completion.get("all_schema_placeholders_resolved") is not True
        or completion.get("successor_core_raw_binding_complete") is not True
        or completion.get("successor_schema_validation_complete") is not True
        or completion.get("source_separated_conformance_complete") is not False
        or completion.get("known_bad_self_tests_complete") is not False
        or completion.get("offline_resolution_complete") is not False
    ):
        findings.add(
            "candidate_binding_phase_incomplete",
            "schema/core freeze is not final or a later gate was fabricated",
        )

    # The abstract evaluator shares the live guard names used by retained
    # known-bads.  Repository-only checks above add byte- and shape-specific
    # detail without weakening those guards.
    for code in model_errors(model, contract, predecessor):
        findings.add(code, "normalized live observation violates contract")
    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="validate the frozen predecessor manifest shape and known-bad harness only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = Findings()
    try:
        cases_document = load_json(CASES_PATH)
        predecessor = load_json(PREDECESSOR_PATH)
        contract = cases_document["contract"]
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        DuplicateKey,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"PRQ-002B product identity contract: invalid suite input: {exc}", file=sys.stderr)
        return 1

    validate_manifest_shape(predecessor, contract, findings)
    validate_contract_exact_json_types(contract, findings)
    validate_structural_vector_contract_shape(contract, findings)
    safe_count, known_bad_count = validate_cases(
        cases_document, predecessor, findings
    )
    authority = cases_document.get("authority_boundary", {})
    if (
        not isinstance(authority, dict)
        or authority.get("passing_means_unissued_architecture_candidate_only")
        is not True
        or any(
            authority.get(key) is not False
            for key in (
                "prq_002_closed",
                "profile_issued",
                "schema_resources_admitted",
                "engine_contract_root_bound",
                "activation_constructed",
                "gate_a_complete",
                "runtime_authorized",
            )
        )
    ):
        findings.add(
            "suite_authority_boundary_invalid",
            "suite contract could imply issuance, PRQ-002 closure, Gate A, or runtime",
        )

    if not args.self_test_only:
        live = repository_findings(cases_document, predecessor)
        for line in live.lines():
            code, detail = line.split(": ", 1)
            findings.add(code, detail)
        if all((ROOT / path).is_file() for path in POST_PRQ_002B_SCHEMA_PATHS):
            if not POST_PRQ_002B_CHECK.is_file() or POST_PRQ_002B_CHECK.is_symlink():
                findings.add(
                    "post_prq_002b_checker_missing_or_unsafe",
                    POST_PRQ_002B_CHECK.relative_to(ROOT).as_posix(),
                )
            else:
                try:
                    successor_check = subprocess.run(
                        [sys.executable, str(POST_PRQ_002B_CHECK)],
                        cwd=ROOT,
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                        timeout=POST_PRQ_002B_CHECK_TIMEOUT_SECONDS,
                        check=False,
                    )
                except (OSError, subprocess.TimeoutExpired) as exc:
                    findings.add(
                        "post_prq_002b_checker_failed",
                        f"execution failed: {type(exc).__name__}",
                    )
                else:
                    if successor_check.returncode != 0:
                        detail = " | ".join(
                            line.strip()
                            for line in (
                                successor_check.stdout
                                + "\n"
                                + successor_check.stderr
                            ).splitlines()
                            if line.strip()
                        )
                        findings.add(
                            "post_prq_002b_checker_failed",
                            detail[:2000] or "nonzero exit without diagnostics",
                        )

    if findings:
        for line in findings.lines():
            print(f"ERROR: {line}", file=sys.stderr)
        print(
            "PRQ-002B product identity contract: FAIL — candidate remains "
            "unissued, unadmitted, Gate A blocked, runtime unauthorized",
            file=sys.stderr,
        )
        return 1
    mode = "self-test" if args.self_test_only else "full candidate"
    print(
        "PRQ-002B product identity contract: PASS "
        f"({mode}; {safe_count} safe control, {known_bad_count} attributed "
        "single-fault known-bads) — unissued architecture candidate only; "
        "PRQ-002 remains open, Gate A blocked, runtime unauthorized"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
