#!/usr/bin/env python3
"""Source-separated CPython observer for the bounded PRQ-002D replay.

The child consumes answer-free inputs only. It emits observations, never an
admission, identity, authority, or approval decision.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from importlib.metadata import version as distribution_version
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource


IMPLEMENTATION_ID = "python-jsonschema-closed-resolver.0001"
SUITE_ID = "prq-002d-schema-registry-prehash-replay.0001"
CONTRACT_ID = (
    "urn:odeya:architecture-test:prq-002d:"
    "schema-registry-prehash-contract:0.1.0"
)
VECTOR_CLASS = "prq_002d_schema_registry_prehash_vector_set"
BUNDLE_CLASS = "prq_002d_non_product_schema_registry_prehash_bundle"
OBSERVATION_CLASS = "prq_002d_schema_registry_prehash_observation"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
VECTOR_ID_RE = re.compile(r"^PH-[0-9]{4}$")
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
MEMBER_KEY_RE = re.compile(r"^[a-z0-9._:@-]+$")
INTEGER_TOKEN_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
SCHEMA_VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")

VECTOR_KEYS = {
    "sequence_index_decimal",
    "vector_id",
    "files",
}
FILE_KEYS = {
    "blob_id",
    "media_type",
    "raw_sha256",
    "byte_count_decimal",
    "content_base64",
}
BUNDLE_KEYS = {
    "schema_version",
    "artifact_class",
    "scope",
    "declared_member_count",
    "members",
    "resolver_catalog",
    "replay_requests",
    "authority_boundary",
}
MEMBER_KEYS = {
    "member_key",
    "schema_id",
    "semantic_version",
    "resource_raw_sha256",
    "resource_byte_count_decimal",
}
RESOLVER_KEYS = {
    "request_uri",
    "resource_blob_id",
    "resource_raw_sha256",
    "resource_byte_count_decimal",
}
REPLAY_KEYS = {"request_uri", "probe_blob_id"}
CONTRACT_KEYS = {
    "schema_version",
    "artifact_class",
    "contract_id",
    "suite_id",
    "status",
    "decision_ref",
    "predecessor_checkpoint",
    "predecessor_evidence_bindings",
    "expected_resource_count_decimal",
    "safe_bundle_binding",
    "expected_resources",
    "preparse_resource_binding_overrides",
    "preparse_probe_binding_overrides",
    "expected_replays",
    "expected_reference_edges",
    "evaluation_contract",
    "authority_boundary",
    "claim_boundary",
}
EXPECTED_RESOURCE_KEYS = {
    "schema_id",
    "semantic_version",
    "member_key",
    "resource_blob_id",
    "repository_path",
    "resource_raw_sha256",
    "resource_byte_count_decimal",
}
RESOURCE_OVERRIDE_KEYS = {
    "vector_id",
    "resource_blob_id",
    "resource_raw_sha256",
    "resource_byte_count_decimal",
}
PROBE_OVERRIDE_KEYS = {
    "vector_id",
    "probe_blob_id",
    "probe_raw_sha256",
    "probe_byte_count_decimal",
}
EXPECTED_REPLAY_KEYS = {
    "request_uri",
    "probe_blob_id",
    "repository_path",
    "probe_raw_sha256",
    "probe_byte_count_decimal",
}
REFERENCE_EDGE_KEYS = {
    "source_schema_id",
    "keyword_location",
    "target_schema_id",
}
EVALUATION_CONTRACT = {
    "json_dialect": "https://json-schema.org/draft/2020-12/schema",
    "member_key_expression": "schema_id@semantic_version",
    "member_key_pattern": "^[a-z0-9._:@-]+$",
    "ordering": "unsigned_lexicographic_utf8_byte_order",
    "duplicate_member_keys": "reject_before_ordering",
    "declared_member_count_raw_token": "exact_decimal_integer_token_2",
    "resolver_inventory": "exactly_two_preloaded_contract_pinned_resources",
    "resource_preparse_binding": (
        "contract_expected_resource_or_enumerated_semantic_fixture_override_"
        "before_parse"
    ),
    "probe_preparse_binding": (
        "contract_expected_probe_or_enumerated_semantic_fixture_override_"
        "before_parse"
    ),
    "resolver_catalog_ordering": "contract_expected_resource_order",
    "replay_request_ordering": "contract_expected_replay_order",
    "resource_retrieval": (
        "deny_all_network_file_search_environment_and_dynamic_fallback"
    ),
    "source_separated_implementation_count_decimal": "2",
}
RESOURCE_OVERRIDE_VECTOR_IDS = (
    "PH-0021",
    "PH-0022",
    "PH-0023",
    "PH-0024",
    "PH-0025",
    "PH-0026",
    "PH-0027",
    "PH-0028",
    "PH-0052",
    "PH-0055",
    "PH-0057",
    "PH-0064",
    "PH-0065",
)
PROBE_OVERRIDE_VECTOR_IDS = ("PH-0033",)
CLAIM_BOUNDARY = {
    "organizational_independence_proven": False,
    "independent_host_reproduction_complete": False,
    "historical_process_independently_witnessed": False,
    "undeclared_filesystem_read_excluded": False,
    "complete_offline_registry_proved": False,
    "product_identity_computed": False,
    "profile_issued": False,
    "gate_a_complete": False,
    "runtime_authorized": False,
    "publication_authorized": False,
}
AUTHORITY_BOUNDARY = {
    "profile_issued": False,
    "profile_conformance_proved": False,
    "product_schema_resource_admitted": False,
    "product_member_constructed": False,
    "product_digest_computed": False,
    "commitment_constructed": False,
    "registry_snapshot_constructed": False,
    "registry_digest_computed": False,
    "engine_contract_root_constructed": False,
    "activation_constructed": False,
    "gate_a_complete": False,
    "runtime_authorized": False,
    "publication_authorized": False,
}


class DuplicateKey(ValueError):
    """A decoded JSON object member occurred more than once."""


class Refusal(Exception):
    """One stable bounded-replay refusal."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class RawNumber:
    """One pointer-scoped JSON number spelling retained after strict parsing."""

    def __init__(self, token: str):
        self.token = token


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def has_unpaired_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    if isinstance(value, list):
        return any(has_unpaired_surrogate(item) for item in value)
    if isinstance(value, dict):
        return any(
            has_unpaired_surrogate(key) or has_unpaired_surrogate(item)
            for key, item in value.items()
        )
    return False


def finite_float(token: str) -> float:
    value = float(token)
    if value in (float("inf"), float("-inf")):
        raise ValueError("non-finite JSON number")
    return value


def top_level_number_token(text: str, key: str) -> str | None:
    value = json.loads(
        text,
        object_pairs_hook=strict_pairs,
        parse_int=RawNumber,
        parse_float=RawNumber,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite token {token}")
        ),
    )
    if not isinstance(value, dict):
        return None
    number = value.get(key)
    return number.token if isinstance(number, RawNumber) else None


def parse_strict(data: bytes, *, resource: bool = False) -> tuple[dict[str, Any], str]:
    prefix = "ODEYA_PREHASH_RESOURCE_PARSE" if resource else None
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise Refusal(prefix or "ODEYA_PARSE_UTF8") from exc
    if text.startswith("\ufeff"):
        raise Refusal(prefix or "ODEYA_PARSE_BOM")
    try:
        json.loads(
            text,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite token {token}")
            ),
            parse_float=finite_float,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise Refusal(prefix or "ODEYA_PARSE_SYNTAX") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=strict_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite token {token}")
            ),
            parse_float=finite_float,
        )
    except DuplicateKey as exc:
        raise Refusal(prefix or "ODEYA_PARSE_DUPLICATE_KEY") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise Refusal(prefix or "ODEYA_PARSE_SYNTAX") from exc
    if has_unpaired_surrogate(value):
        raise Refusal(prefix or "ODEYA_PARSE_UNPAIRED_SURROGATE")
    if not isinstance(value, dict):
        raise Refusal(prefix or "ODEYA_CONFORMANCE_FRAME_SHAPE")
    return value, text


def raw_binding(data: bytes) -> dict[str, str]:
    return {
        "raw_sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "byte_count_decimal": str(len(data)),
    }


def path_binding(path: Path) -> dict[str, str]:
    return raw_binding(path.read_bytes())


def exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def same_false_boundary(value: Any, expected: dict[str, bool]) -> bool:
    return (
        exact_keys(value, set(expected))
        and all(type(value[key]) is bool and value[key] is False for key in expected)
    )


def valid_binding(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("raw_sha256"), str)
        and SHA256_RE.fullmatch(value["raw_sha256"]) is not None
        and isinstance(value.get("byte_count_decimal"), str)
        and DECIMAL_RE.fullmatch(value["byte_count_decimal"]) is not None
    )


def valid_contract(contract: Any) -> bool:
    if (
        not exact_keys(contract, CONTRACT_KEYS)
        or contract.get("schema_version") != "0.1.0"
        or contract.get("artifact_class")
        != "prq_002d_schema_registry_prehash_contract"
        or contract.get("contract_id") != CONTRACT_ID
        or contract.get("suite_id") != SUITE_ID
        or contract.get("status")
        != "architecture_only_non_product_nonidentity_candidate"
        or contract.get("decision_ref")
        != "docs/decisions/0102-prove-non-product-prehash-schema-registry-replay.md"
        or contract.get("predecessor_checkpoint")
        != {
            "commit": "d3ec64f3abfc64467c0bc3bfae330d86e2af89b2",
            "tree": "69304534a61a7c5d085d183d847285a181eaabfc",
        }
        or not isinstance(contract.get("predecessor_evidence_bindings"), list)
        or len(contract["predecessor_evidence_bindings"]) != 2
        or contract.get("expected_resource_count_decimal") != "2"
        or not valid_binding(contract.get("safe_bundle_binding"))
        or contract.get("evaluation_contract") != EVALUATION_CONTRACT
        or not same_false_boundary(
            contract.get("authority_boundary"), AUTHORITY_BOUNDARY
        )
        or not same_false_boundary(
            contract.get("claim_boundary"), CLAIM_BOUNDARY
        )
    ):
        return False
    resources = contract.get("expected_resources")
    resource_overrides = contract.get("preparse_resource_binding_overrides")
    probe_overrides = contract.get("preparse_probe_binding_overrides")
    replays = contract.get("expected_replays")
    edges = contract.get("expected_reference_edges")
    if (
        not isinstance(resources, list)
        or len(resources) != 2
        or not isinstance(resource_overrides, list)
        or len(resource_overrides) != len(RESOURCE_OVERRIDE_VECTOR_IDS)
        or not isinstance(probe_overrides, list)
        or len(probe_overrides) != len(PROBE_OVERRIDE_VECTOR_IDS)
        or not isinstance(replays, list)
        or len(replays) != 2
        or not isinstance(edges, list)
        or len(edges) != 1
    ):
        return False
    expected_predecessor_roles = (
        (
            "raw_number_decision",
            "docs/decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md",
        ),
        (
            "raw_number_comparison",
            "tests/product-identity-raw-number-typing/results/comparison-receipt.json",
        ),
    )
    for binding, (role, path) in zip(
        contract["predecessor_evidence_bindings"],
        expected_predecessor_roles,
        strict=True,
    ):
        if (
            not exact_keys(
                binding,
                {
                    "role",
                    "repository_path",
                    "raw_sha256",
                    "byte_count_decimal",
                },
            )
            or binding.get("role") != role
            or binding.get("repository_path") != path
            or not valid_binding(binding)
        ):
            return False
    resource_ids: list[str] = []
    resource_blobs: list[str] = []
    member_keys: list[str] = []
    for resource in resources:
        if (
            not exact_keys(resource, EXPECTED_RESOURCE_KEYS)
            or not isinstance(resource.get("schema_id"), str)
            or not resource["schema_id"].startswith(
                "urn:odeya:architecture-test:prq-002d:"
            )
            or not isinstance(resource.get("semantic_version"), str)
            or SCHEMA_VERSION_RE.fullmatch(resource["semantic_version"]) is None
            or resource.get("member_key")
            != f"{resource['schema_id']}@{resource['semantic_version']}"
            or MEMBER_KEY_RE.fullmatch(resource["member_key"]) is None
            or not isinstance(resource.get("resource_blob_id"), str)
            or not isinstance(resource.get("repository_path"), str)
            or not valid_binding(
                {
                    "raw_sha256": resource.get("resource_raw_sha256"),
                    "byte_count_decimal": resource.get(
                        "resource_byte_count_decimal"
                    ),
                }
            )
        ):
            return False
        resource_ids.append(resource["schema_id"])
        resource_blobs.append(resource["resource_blob_id"])
        member_keys.append(resource["member_key"])
    if (
        len(set(resource_ids)) != 2
        or len(set(resource_blobs)) != 2
        or len(set(member_keys)) != 2
        or member_keys != sorted(member_keys, key=lambda key: key.encode("utf-8"))
    ):
        return False
    safe_resource_bindings = {
        resource["resource_blob_id"]: {
            "raw_sha256": resource["resource_raw_sha256"],
            "byte_count_decimal": resource["resource_byte_count_decimal"],
        }
        for resource in resources
    }
    for override, vector_id in zip(
        resource_overrides,
        RESOURCE_OVERRIDE_VECTOR_IDS,
        strict=True,
    ):
        binding = {
            "raw_sha256": override.get("resource_raw_sha256")
            if isinstance(override, dict)
            else None,
            "byte_count_decimal": override.get("resource_byte_count_decimal")
            if isinstance(override, dict)
            else None,
        }
        if (
            not exact_keys(override, RESOURCE_OVERRIDE_KEYS)
            or override.get("vector_id") != vector_id
            or override.get("resource_blob_id") != "resource-001"
            or override.get("resource_blob_id") not in safe_resource_bindings
            or not valid_binding(binding)
            or binding
            == safe_resource_bindings.get(override.get("resource_blob_id"))
        ):
            return False
    for override, vector_id in zip(
        probe_overrides,
        PROBE_OVERRIDE_VECTOR_IDS,
        strict=True,
    ):
        binding = {
            "raw_sha256": override.get("probe_raw_sha256")
            if isinstance(override, dict)
            else None,
            "byte_count_decimal": override.get("probe_byte_count_decimal")
            if isinstance(override, dict)
            else None,
        }
        if (
            not exact_keys(override, PROBE_OVERRIDE_KEYS)
            or override.get("vector_id") != vector_id
            or override.get("probe_blob_id") != "probe-001"
            or not valid_binding(binding)
        ):
            return False
    replay_uris: list[str] = []
    probe_blobs: list[str] = []
    for replay in replays:
        if (
            not exact_keys(replay, EXPECTED_REPLAY_KEYS)
            or not isinstance(replay.get("request_uri"), str)
            or not isinstance(replay.get("probe_blob_id"), str)
            or not isinstance(replay.get("repository_path"), str)
            or not valid_binding(
                {
                    "raw_sha256": replay.get("probe_raw_sha256"),
                    "byte_count_decimal": replay.get(
                        "probe_byte_count_decimal"
                    ),
                }
            )
        ):
            return False
        replay_uris.append(replay["request_uri"])
        probe_blobs.append(replay["probe_blob_id"])
    safe_probe_bindings = {
        replay["probe_blob_id"]: {
            "raw_sha256": replay["probe_raw_sha256"],
            "byte_count_decimal": replay["probe_byte_count_decimal"],
        }
        for replay in replays
    }
    for override in probe_overrides:
        binding = {
            "raw_sha256": override["probe_raw_sha256"],
            "byte_count_decimal": override["probe_byte_count_decimal"],
        }
        if (
            override["probe_blob_id"] not in safe_probe_bindings
            or binding == safe_probe_bindings[override["probe_blob_id"]]
        ):
            return False
    edge = edges[0]
    return (
        replay_uris == resource_ids
        and len(set(probe_blobs)) == 2
        and exact_keys(edge, REFERENCE_EDGE_KEYS)
        and edge.get("source_schema_id") == resource_ids[0]
        and edge.get("keyword_location") == "/properties/peer/$ref"
        and edge.get("target_schema_id") == resource_ids[1]
    )


def preparse_resource_binding(
    contract: dict[str, Any],
    vector_id: str,
    expected: dict[str, Any],
) -> dict[str, str]:
    for override in contract["preparse_resource_binding_overrides"]:
        if (
            override["vector_id"] == vector_id
            and override["resource_blob_id"] == expected["resource_blob_id"]
        ):
            return {
                "raw_sha256": override["resource_raw_sha256"],
                "byte_count_decimal": override[
                    "resource_byte_count_decimal"
                ],
            }
    return {
        "raw_sha256": expected["resource_raw_sha256"],
        "byte_count_decimal": expected["resource_byte_count_decimal"],
    }


def preparse_probe_binding(
    contract: dict[str, Any],
    vector_id: str,
    expected: dict[str, Any],
) -> dict[str, str]:
    for override in contract["preparse_probe_binding_overrides"]:
        if (
            override["vector_id"] == vector_id
            and override["probe_blob_id"] == expected["probe_blob_id"]
        ):
            return {
                "raw_sha256": override["probe_raw_sha256"],
                "byte_count_decimal": override["probe_byte_count_decimal"],
            }
    return {
        "raw_sha256": expected["probe_raw_sha256"],
        "byte_count_decimal": expected["probe_byte_count_decimal"],
    }


def deny_retrieve(uri: str) -> NoReturn:
    raise NoSuchResource(ref=uri)


def forbidden_schema_construct(value: Any, *, root: bool = True) -> bool:
    if isinstance(value, list):
        return any(forbidden_schema_construct(item, root=False) for item in value)
    if not isinstance(value, dict):
        return False
    for key, item in value.items():
        if key == "$id" and not root:
            return True
        if key in {"$dynamicRef", "$dynamicAnchor", "$anchor"}:
            return True
        if key == "$ref":
            if not (
                isinstance(item, str)
                and item.startswith("urn:odeya:architecture-test:prq-002d:")
                and "#" not in item
            ):
                return True
        if forbidden_schema_construct(item, root=False):
            return True
    return False


def pointer_segment(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def reference_edges(
    value: Any,
    *,
    source_schema_id: str,
    pointer: str = "",
) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value):
            edges.extend(
                reference_edges(
                    item,
                    source_schema_id=source_schema_id,
                    pointer=f"{pointer}/{index}",
                )
            )
        return edges
    if not isinstance(value, dict):
        return edges
    for key, item in value.items():
        location = f"{pointer}/{pointer_segment(key)}"
        if key == "$ref" and isinstance(item, str):
            edges.append(
                {
                    "source_schema_id": source_schema_id,
                    "keyword_location": location,
                    "target_schema_id": item,
                }
            )
        edges.extend(
            reference_edges(
                item,
                source_schema_id=source_schema_id,
                pointer=location,
            )
        )
    return edges


def derived_version(schema: dict[str, Any]) -> str | None:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return None
    schema_version = properties.get("schema_version")
    if not isinstance(schema_version, dict):
        return None
    value = schema_version.get("const")
    if not isinstance(value, str) or SCHEMA_VERSION_RE.fullmatch(value) is None:
        return None
    return value


def version_from_id(schema_id: str) -> str | None:
    tail = schema_id.rsplit(":", 1)[-1]
    return tail if SCHEMA_VERSION_RE.fullmatch(tail) else None


def parse_outer(path: Path, expected_class: str) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    value, _ = parse_strict(data)
    if value.get("artifact_class") != expected_class:
        raise ValueError(f"{path}: unexpected artifact_class")
    return value, data


def decoded_files(vector: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    if not exact_keys(vector, VECTOR_KEYS):
        raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
    sequence = vector.get("sequence_index_decimal")
    vector_id = vector.get("vector_id")
    rows = vector.get("files")
    if (
        not isinstance(sequence, str)
        or DECIMAL_RE.fullmatch(sequence) is None
        or not isinstance(vector_id, str)
        or VECTOR_ID_RE.fullmatch(vector_id) is None
        or not isinstance(rows, list)
    ):
        raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
    files: dict[str, bytes] = {}
    bundle_binding: dict[str, Any] | None = None
    for row in rows:
        if not exact_keys(row, FILE_KEYS):
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        blob_id = row.get("blob_id")
        if (
            not isinstance(blob_id, str)
            or not blob_id
            or blob_id in files
            or row.get("media_type") != "application/json"
            or not valid_binding(row)
            or not isinstance(row.get("content_base64"), str)
        ):
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        try:
            data = base64.b64decode(row["content_base64"], validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE") from exc
        if base64.b64encode(data).decode("ascii") != row["content_base64"]:
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        if raw_binding(data) != {
            "raw_sha256": row["raw_sha256"],
            "byte_count_decimal": row["byte_count_decimal"],
        }:
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        files[blob_id] = data
        if blob_id == "bundle":
            bundle_binding = raw_binding(data)
    if bundle_binding is None:
        raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
    return files, bundle_binding


def row_base(
    vector: dict[str, Any],
    bundle_binding: dict[str, Any] | None,
    token: str | None,
) -> dict[str, Any]:
    return {
        "sequence_index_decimal": vector["sequence_index_decimal"],
        "vector_id": vector["vector_id"],
        "bundle_raw_sha256": (
            bundle_binding["raw_sha256"] if bundle_binding is not None else None
        ),
        "bundle_byte_count_decimal": (
            bundle_binding["byte_count_decimal"]
            if bundle_binding is not None
            else None
        ),
        "declared_member_count_raw_token": token,
    }


def evaluate(
    vector: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    token: str | None = None
    binding: dict[str, Any] | None = None
    try:
        files, binding = decoded_files(vector)
        bundle_raw = files["bundle"]
        bundle, bundle_text = parse_strict(bundle_raw)
        token = top_level_number_token(bundle_text, "declared_member_count")
        if (
            not exact_keys(bundle, BUNDLE_KEYS)
            or bundle.get("schema_version") != "0.1.0"
            or bundle.get("artifact_class") != BUNDLE_CLASS
            or bundle.get("scope")
            != "architecture_test_only_non_product_nonidentity"
        ):
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        count = bundle.get("declared_member_count")
        if token is None:
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        if token.startswith("-") and re.fullmatch(
            r"-0(?:\.0+)?(?:[eE][+-]?[0-9]+)?", token
        ):
            raise Refusal("ODEYA_NUMBER_NEGATIVE_ZERO")
        if INTEGER_TOKEN_RE.fullmatch(token) is None:
            raise Refusal("ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED")
        if type(count) is not int:
            raise Refusal("ODEYA_CONFORMANCE_FRAME_SHAPE")
        if abs(count) > 9_007_199_254_740_991:
            raise Refusal("ODEYA_NUMBER_DOMAIN")
        if (
            not same_false_boundary(
                bundle.get("authority_boundary"), AUTHORITY_BOUNDARY
            )
            or not same_false_boundary(
                contract.get("authority_boundary"), AUTHORITY_BOUNDARY
            )
        ):
            raise Refusal("ODEYA_PREHASH_AUTHORITY_BOUNDARY")
        if token != "2" or count != 2:
            raise Refusal("ODEYA_PREHASH_COUNT")

        members = bundle.get("members")
        resolvers = bundle.get("resolver_catalog")
        replays = bundle.get("replay_requests")
        if (
            not isinstance(members, list)
            or len(members) != 2
            or not isinstance(resolvers, list)
            or not isinstance(replays, list)
        ):
            raise Refusal("ODEYA_PREHASH_MEMBER_SHAPE")
        for member in members:
            if (
                not exact_keys(member, MEMBER_KEYS)
                or not isinstance(member.get("member_key"), str)
                or MEMBER_KEY_RE.fullmatch(member["member_key"]) is None
                or not isinstance(member.get("schema_id"), str)
                or not isinstance(member.get("semantic_version"), str)
                or SCHEMA_VERSION_RE.fullmatch(member["semantic_version"]) is None
                or not valid_binding(
                    {
                        "raw_sha256": member.get("resource_raw_sha256"),
                        "byte_count_decimal": member.get(
                            "resource_byte_count_decimal"
                        ),
                    }
                )
            ):
                raise Refusal("ODEYA_PREHASH_MEMBER_SHAPE")
        member_keys = [member["member_key"] for member in members]
        if len(set(member_keys)) != len(member_keys):
            raise Refusal("ODEYA_PREHASH_DUPLICATE_KEY")
        if member_keys != sorted(member_keys, key=lambda key: key.encode("utf-8")):
            raise Refusal("ODEYA_PREHASH_ORDER")

        expected_resources = contract.get("expected_resources")
        expected_replays = contract.get("expected_replays")
        if (
            not isinstance(expected_resources, list)
            or len(expected_resources) != 2
            or not isinstance(expected_replays, list)
            or len(expected_replays) != 2
            or len(resolvers) != 2
            or any(not exact_keys(item, RESOLVER_KEYS) for item in resolvers)
        ):
            raise Refusal("ODEYA_PREHASH_RESOLVER_INVENTORY")
        resolver_uris = [item.get("request_uri") for item in resolvers]
        expected_uris = [item["schema_id"] for item in expected_resources]
        if (
            any(not isinstance(uri, str) for uri in resolver_uris)
            or len(set(resolver_uris)) != len(resolver_uris)
            or resolver_uris != expected_uris
        ):
            raise Refusal("ODEYA_PREHASH_RESOLVER_INVENTORY")
        expected_blob_ids = {
            "bundle",
            *(item["resource_blob_id"] for item in expected_resources),
            *(item["probe_blob_id"] for item in expected_replays),
        }
        if set(files) != expected_blob_ids:
            raise Refusal("ODEYA_PREHASH_RESOLVER_INVENTORY")

        parsed_resources: list[dict[str, Any]] = []
        resolved_replay_bindings: list[dict[str, str]] = []
        registry: Registry[Any] = Registry(retrieve=deny_retrieve)
        for index, expected in enumerate(expected_resources):
            member = members[index]
            resolver = resolvers[index]
            if resolver.get("resource_blob_id") != expected["resource_blob_id"]:
                raise Refusal("ODEYA_PREHASH_RESOLVER_TARGET")
            data = files[resolver["resource_blob_id"]]
            observed = raw_binding(data)
            if (
                member.get("resource_byte_count_decimal")
                != observed["byte_count_decimal"]
                or resolver.get("resource_byte_count_decimal")
                != observed["byte_count_decimal"]
            ):
                raise Refusal("ODEYA_PREHASH_RESOURCE_BYTE_COUNT")
            if (
                member.get("resource_raw_sha256") != observed["raw_sha256"]
                or resolver.get("resource_raw_sha256") != observed["raw_sha256"]
            ):
                raise Refusal("ODEYA_PREHASH_RESOURCE_RAW_DIGEST")
            if observed != preparse_resource_binding(
                contract,
                vector["vector_id"],
                expected,
            ):
                raise Refusal("ODEYA_PREHASH_RESOLVER_TARGET")
            schema, _ = parse_strict(data, resource=True)
            if schema.get("$schema") != DIALECT:
                raise Refusal("ODEYA_PREHASH_RESOURCE_DIALECT")
            if forbidden_schema_construct(schema):
                raise Refusal("ODEYA_PREHASH_RESOURCE_SCHEMA")
            expected_reference_edges = contract.get("expected_reference_edges")
            if (
                not isinstance(expected_reference_edges, list)
                or reference_edges(
                    schema,
                    source_schema_id=expected["schema_id"],
                )
                != [
                    edge
                    for edge in expected_reference_edges
                    if edge.get("source_schema_id") == expected["schema_id"]
                ]
            ):
                raise Refusal("ODEYA_PREHASH_RESOURCE_SCHEMA")
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                raise Refusal("ODEYA_PREHASH_RESOURCE_SCHEMA") from exc
            schema_id = schema.get("$id")
            if (
                not isinstance(schema_id, str)
                or schema_id != member.get("schema_id")
                or schema_id != resolver.get("request_uri")
                or schema_id != expected["schema_id"]
            ):
                raise Refusal("ODEYA_PREHASH_RESOURCE_ID")
            version = derived_version(schema)
            if (
                version is None
                or version != version_from_id(schema_id)
                or version != member.get("semantic_version")
                or version != expected["semantic_version"]
            ):
                raise Refusal("ODEYA_PREHASH_RESOURCE_VERSION")
            derived_key = f"{schema_id}@{version}"
            if derived_key != member.get("member_key"):
                raise Refusal("ODEYA_PREHASH_KEY_BODY")
            parsed_resources.append(schema)
            registry = registry.with_resource(
                schema_id,
                Resource.from_contents(schema),
            )
        expected_requests = [
            {
                "request_uri": item["request_uri"],
                "probe_blob_id": item["probe_blob_id"],
            }
            for item in expected_replays
        ]
        if (
            len(replays) != 2
            or any(not exact_keys(item, REPLAY_KEYS) for item in replays)
            or replays != expected_requests
        ):
            raise Refusal("ODEYA_PREHASH_REPLAY_REQUEST")
        for replay, expected in zip(replays, expected_replays, strict=True):
            probe_data = files[replay["probe_blob_id"]]
            observed_probe = raw_binding(probe_data)
            if observed_probe != preparse_probe_binding(
                contract,
                vector["vector_id"],
                expected,
            ):
                raise Refusal("ODEYA_PREHASH_REPLAY_REQUEST")
            try:
                probe, _ = parse_strict(probe_data)
            except Refusal as exc:
                raise Refusal("ODEYA_PREHASH_REPLAY_VALIDATION") from exc
            schema_index = expected_uris.index(replay["request_uri"])
            try:
                retrieved = registry.get_or_retrieve(replay["request_uri"])
            except NoSuchResource as exc:
                raise Refusal("ODEYA_PREHASH_REPLAY_VALIDATION") from exc
            if retrieved.value.contents is not parsed_resources[schema_index]:
                raise Refusal("ODEYA_PREHASH_REPLAY_VALIDATION")
            validator = Draft202012Validator(
                parsed_resources[schema_index],
                registry=registry,
            )
            try:
                if not validator.is_valid(probe):
                    raise Refusal("ODEYA_PREHASH_REPLAY_VALIDATION")
            except Refusal:
                raise
            except Exception as exc:
                raise Refusal("ODEYA_PREHASH_REPLAY_VALIDATION") from exc
            expected_resource = expected_resources[schema_index]
            resolved_replay_bindings.append(
                {
                    "request_uri": replay["request_uri"],
                    "resolved_schema_id": expected_resource["schema_id"],
                    "resource_blob_id": expected_resource["resource_blob_id"],
                    "resource_raw_sha256": expected_resource[
                        "resource_raw_sha256"
                    ],
                    "resource_byte_count_decimal": expected_resource[
                        "resource_byte_count_decimal"
                    ],
                }
            )

        result = row_base(vector, binding, token)
        result.update(
            {
                "final_disposition": "accepted",
                "final_code": "ODEYA_PREHASH_REPLAY_ACCEPTED",
                "ordered_member_keys": member_keys,
                "resolved_replay_bindings": resolved_replay_bindings,
                "validated_probe_count_decimal": "2",
            }
        )
        return result
    except Refusal as exc:
        result = row_base(vector, binding, token)
        result.update(
            {
                "final_disposition": "refused",
                "final_code": exc.code,
                "ordered_member_keys": [],
                "resolved_replay_bindings": [],
                "validated_probe_count_decimal": None,
            }
        )
        return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--source-manifest", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    vectors_path = Path(args.vectors)
    contract_path = Path(args.contract)
    source_manifest_path = Path(args.source_manifest)
    expected_distributions = {
        "attrs": "26.1.0",
        "jsonschema": "4.26.0",
        "jsonschema-specifications": "2025.9.1",
        "referencing": "0.37.0",
        "rpds-py": "2026.6.3",
    }
    try:
        dependency_versions_match = all(
            distribution_version(name) == version
            for name, version in expected_distributions.items()
        )
    except Exception:
        dependency_versions_match = False
    if sys.version.split()[0] != "3.14.2" or not dependency_versions_match:
        print("PRQ-002D observer runtime/dependency failure", file=sys.stderr)
        return 2
    try:
        vectors, vectors_raw = parse_outer(vectors_path, VECTOR_CLASS)
        contract, contract_raw = parse_outer(
            contract_path,
            "prq_002d_schema_registry_prehash_contract",
        )
        source_manifest, source_raw = parse_outer(
            source_manifest_path,
            "prq_002d_schema_registry_prehash_source_manifest",
        )
    except (OSError, ValueError, Refusal) as exc:
        print(f"PRQ-002D observer input failure: {exc}", file=sys.stderr)
        return 2
    rows = vectors.get("vectors")
    if (
        vectors.get("schema_version") != "0.1.0"
        or not isinstance(rows, list)
        or vectors.get("vector_count_decimal") != str(len(rows))
        or not valid_contract(contract)
        or source_manifest.get("role") != "python"
        or source_manifest.get("implementation_id") != IMPLEMENTATION_ID
        or source_manifest.get("runtime_version") != "3.14.2"
        or source_manifest.get("private_expectation_consumption_allowed")
        is not False
        or source_manifest.get("peer_source_consumption_allowed") is not False
        or source_manifest.get("peer_result_consumption_allowed") is not False
        or source_manifest.get("network_access_requested") is not False
    ):
        print("PRQ-002D observer manifest failure", file=sys.stderr)
        return 2
    results = [evaluate(vector, contract) for vector in rows]
    output = {
        "schema_version": "0.1.0",
        "artifact_class": OBSERVATION_CLASS,
        "suite_id": contract["suite_id"],
        "implementation_id": IMPLEMENTATION_ID,
        "vector_set_id": vectors["vector_set_id"],
        "vector_count_decimal": str(len(results)),
        "input_bindings": {
            "vectors": raw_binding(vectors_raw),
            "contract": raw_binding(contract_raw),
            "source_manifest": raw_binding(source_raw),
        },
        "results": results,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    print(
        json.dumps(
            output,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
