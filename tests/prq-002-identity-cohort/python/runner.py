#!/usr/bin/env python3
"""Source-separated Python recomputer for the PRQ-002A identity probe.

The external entry point executes exact, pre-bound rfc8785 source bytes without
importing the installed package.  The repository checker may import the
structural evaluator and provide a bounded, standard-library canonicalizer on
its cheap/default path.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import platform
import re
import sys
from pathlib import Path
from typing import Any, Callable


SUITE = Path(__file__).resolve().parents[1]
ROOT = SUITE.parents[1]
PROFILE_ID = "urn:odeya:canonicalization:prq-002-identity-probe-jcs-0.1"
PROFILE_SCHEMA_ID = (
    "urn:odeya:architecture-schema:prq-002-identity-probe-profile:0.1.0"
)
IDENTITY_SCOPE = "prq_002_structural_probe_only"
PROBE_STATUS = "test_only_non_issuable_structural_probe"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
NUMBER_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_.])-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
    r"(?:[eE][+-]?[0-9]+)?"
)

SCHEMA_MEMBER_ROLES = (
    "aggregate_state_member_probe_schema",
    "event_member_probe_schema",
    "identity_probe_profile_schema",
    "ordered_commitment_probe_schema",
    "pure_snapshot_probe_schema",
    "reducer_member_probe_schema",
    "schema_member_probe_schema",
    "structural_event_schema",
    "structural_state_schema",
)
MEMBER_ROLES = (*SCHEMA_MEMBER_ROLES, "aggregate_state", "reducer", "event")
FAMILIES = (
    "schema_registry",
    "aggregate_state_subject_registry",
    "reducer_registry",
    "event_contract_registry",
)
FAMILY_MEMBER_ROLES = {
    "schema_registry": SCHEMA_MEMBER_ROLES,
    "aggregate_state_subject_registry": ("aggregate_state",),
    "reducer_registry": ("reducer",),
    "event_contract_registry": ("event",),
}
FAMILY_KEY_EXPRESSIONS = {
    "schema_registry": "schema_id@semantic_version",
    "aggregate_state_subject_registry": "aggregate_type",
    "reducer_registry": "aggregate_type",
    "event_contract_registry": "event_type@event_version",
}
SNAPSHOT_DOMAINS = {
    "schema_registry": "odeya-prq-002-schema-registry-snapshot-probe-v1",
    "aggregate_state_subject_registry": (
        "odeya-prq-002-aggregate-state-registry-snapshot-probe-v1"
    ),
    "reducer_registry": "odeya-prq-002-reducer-registry-snapshot-probe-v1",
    "event_contract_registry": "odeya-prq-002-event-registry-snapshot-probe-v1",
}
SNAPSHOT_REGISTRY_IDS = {
    "schema_registry": "schema-registry-probe",
    "aggregate_state_subject_registry": (
        "aggregate-state-subject-registry-probe"
    ),
    "reducer_registry": "reducer-registry-probe",
    "event_contract_registry": "event-contract-registry-probe",
}
COHORT_AUTHORITY_KEYS = {
    "canonical_identity_issued",
    "registry_admission",
    "engine_contract_root_binding",
    "gate_a_acceptance",
    "runtime_authority",
    "external_effect_authority",
    "publication_authority",
}
PROFILE_AUTHORITY_KEYS = {
    "canonical_identity_issued",
    "profile_registry_member_exists",
    "product_schema_domain_rebinding_authorized",
    "engine_contract_root_binding_exists",
    "gate_a_complete",
    "runtime_authorized",
    "deployment_authorized",
    "external_effects_authorized",
    "publication_authorized",
}
ROLE_SCHEMA_BINDINGS = {
    **{role: "schema_member_probe" for role in SCHEMA_MEMBER_ROLES},
    "aggregate_state": "aggregate_state_member_probe",
    "reducer": "reducer_member_probe",
    "event": "event_member_probe",
}
ROLE_DOMAINS = {
    **{
        role: "odeya-prq-002-schema-member-probe-v1"
        for role in SCHEMA_MEMBER_ROLES
    },
    "aggregate_state": "odeya-prq-002-aggregate-state-member-probe-v1",
    "reducer": "odeya-prq-002-reducer-member-probe-v1",
    "event": "odeya-prq-002-event-member-probe-v1",
}
EXPECTED_PARSER_SEMANTICS = {
    "positive_underflow": {
        "input": "1e-400",
        "outcome": "accepted",
        "ieee754_conversion": "positive_zero",
    },
    "negative_underflow": {
        "input": "-1e-400",
        "outcome": "accepted",
        "ieee754_conversion": "negative_zero",
    },
    "lexical_negative_zero": {
        "input": "-0",
        "outcome": "refused",
        "error": "strict_input_negative_zero",
    },
}
EXPECTED_RFC8785_SOURCE_BINDINGS = {
    "__init__.py": {
        "raw_sha256": (
            "sha256:"
            "fa44927afd547caf7547247078bcf28863d1e69caf116d258c532b3f20ffd154"
        ),
        "byte_count": 496,
    },
    "_impl.py": {
        "raw_sha256": (
            "sha256:"
            "c25bc3a046528482d53bee3487b837f31dd9c05f33e8f13288c7aab320932cec"
        ),
        "byte_count": 7251,
    },
    "py.typed": {
        "raw_sha256": (
            "sha256:"
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ),
        "byte_count": 0,
    },
}


class DuplicateKey(ValueError):
    """Raised when JSON mapping would otherwise hide a duplicate name."""


class StrictInputError(ValueError):
    """A strict parser refusal with a stable public error code."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"raw_sha256": sha256_bytes(raw), "byte_count": len(raw)}


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_constant(_: str) -> None:
    raise StrictInputError("strict_input_nonfinite")


def parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise StrictInputError("strict_input_nonfinite")
    return value


def _has_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    if isinstance(value, list):
        return any(_has_surrogate(item) for item in value)
    if isinstance(value, dict):
        return any(
            _has_surrogate(key) or _has_surrogate(item)
            for key, item in value.items()
        )
    return False


def _scan_negative_zero(text: str) -> None:
    in_string = False
    escaped = False
    outside = [" " if char == "\n" else char for char in text]
    for index, char in enumerate(text):
        if in_string:
            outside[index] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            outside[index] = " "
            in_string = True
    scanned = "".join(outside)
    for match in NUMBER_TOKEN_RE.finditer(scanned):
        token = match.group(0)
        if not token.startswith("-"):
            continue
        mantissa = re.split(r"[eE]", token[1:], maxsplit=1)[0]
        digits = mantissa.replace(".", "")
        if digits and all(digit == "0" for digit in digits):
            raise StrictInputError("strict_input_negative_zero")


def strict_load_bytes(raw: bytes) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise StrictInputError("strict_input_bom")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise StrictInputError("strict_input_utf8") from None
    _scan_negative_zero(text)
    decoder = json.JSONDecoder(
        object_pairs_hook=strict_pairs,
        parse_constant=reject_constant,
        parse_float=parse_finite_float,
    )
    try:
        value, end = decoder.raw_decode(text)
    except DuplicateKey:
        raise StrictInputError("strict_input_duplicate_key") from None
    except StrictInputError:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise StrictInputError("strict_input_syntax") from None
    if text[end:].strip():
        raise StrictInputError("strict_input_trailing_data")
    if _has_surrogate(value):
        raise StrictInputError("strict_input_unicode")
    return value


def strict_load_path(path: Path) -> Any:
    return strict_load_bytes(path.read_bytes())


def parser_semantics_observation() -> dict[str, Any]:
    """Exercise bounded IEEE-754 underflow and lexical -0 parser semantics."""

    observation: dict[str, Any] = {}
    for name, token in (
        ("positive_underflow", "1e-400"),
        ("negative_underflow", "-1e-400"),
    ):
        value = strict_load_bytes(token.encode("ascii"))
        sign = math.copysign(1.0, value)
        observation[name] = {
            "input": token,
            "outcome": "accepted",
            "ieee754_conversion": (
                "negative_zero" if value == 0.0 and sign < 0 else "positive_zero"
            ),
        }
    try:
        strict_load_bytes(b"-0")
    except StrictInputError as exc:
        observation["lexical_negative_zero"] = {
            "input": "-0",
            "outcome": "refused",
            "error": exc.code,
        }
    else:
        observation["lexical_negative_zero"] = {
            "input": "-0",
            "outcome": "accepted",
            "error": None,
        }
    return observation


def pointer_parts(pointer: str) -> list[str]:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("mutation path is not an absolute JSON pointer")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def resolve_pointer(document: Any, pointer: str) -> Any:
    current = document
    for token in pointer_parts(pointer):
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict):
            current = current[token]
        else:
            raise ValueError(f"pointer crosses scalar at {token!r}")
    return current


def apply_patch(document: Any, mutation: dict[str, Any]) -> None:
    operation = mutation.get("op")
    parts = pointer_parts(mutation.get("path"))
    if not parts:
        raise ValueError("root replacement is not allowed")
    parent = document
    for token in parts[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = parts[-1]
    if operation == "remove":
        if isinstance(parent, list):
            parent.pop(int(final))
        else:
            del parent[final]
        return
    if "value_from" in mutation:
        value = copy.deepcopy(resolve_pointer(document, mutation["value_from"]))
    else:
        value = copy.deepcopy(mutation.get("value"))
    if isinstance(parent, list):
        if operation == "add":
            if final == "-":
                parent.append(value)
            else:
                parent.insert(int(final), value)
        elif operation == "replace":
            parent[int(final)] = value
        elif operation == "swap":
            other = int(mutation["other_index"])
            index = int(final)
            parent[index], parent[other] = parent[other], parent[index]
        else:
            raise ValueError(f"unsupported list mutation: {operation!r}")
    elif isinstance(parent, dict):
        if operation == "add":
            if final in parent:
                raise ValueError("add target already exists")
            parent[final] = value
        elif operation == "replace":
            if final not in parent:
                raise ValueError("replace target does not exist")
            parent[final] = value
        else:
            raise ValueError(f"unsupported object mutation: {operation!r}")
    else:
        raise ValueError("mutation parent is not a container")


def apply_raw_mutation(raw: bytes, mutation: dict[str, Any]) -> bytes:
    operation = mutation.get("op")
    if operation == "prepend_bom":
        return b"\xef\xbb\xbf" + raw
    if operation == "append_trailing_object":
        return raw + b"\n{}\n"
    if operation == "inject_invalid_utf8":
        return raw[:1] + b"\xff" + raw[1:]
    if operation == "duplicate_top_level_status":
        needle = b'  "status": "test_only_non_issuable_structural_probe",'
        if needle not in raw:
            raise ValueError("status anchor is absent")
        duplicate = (
            b'  "status": "test_only_non_issuable_structural_probe",\n' + needle
        )
        return raw.replace(needle, duplicate, 1)
    if operation == "lexical_negative_zero":
        needle = b'"member_count": 9'
        if needle not in raw:
            raise ValueError("member-count anchor is absent")
        return raw.replace(needle, b'"member_count": -0', 1)
    if operation == "lexical_nonfinite":
        needle = b'"member_count": 9'
        if needle not in raw:
            raise ValueError("member-count anchor is absent")
        return raw.replace(needle, b'"member_count": NaN', 1)
    if operation == "numeric_overflow":
        needle = b'"member_count": 9'
        if needle not in raw:
            raise ValueError("member-count anchor is absent")
        return raw.replace(needle, b'"member_count": 1e400', 1)
    if operation == "escaped_lone_surrogate":
        needle = (
            b'"artifact_class": "prq_002_identity_probe_candidate_cohort"'
        )
        if needle not in raw:
            raise ValueError("artifact-class anchor is absent")
        return raw.replace(needle, b'"artifact_class": "\\ud800"', 1)
    raise ValueError(f"unsupported raw mutation: {operation!r}")


def unique_errors(errors: list[str]) -> list[str]:
    return sorted(set(errors))


def _schema_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    resources = manifest.get("schema_resources")
    if not isinstance(resources, list):
        return {}
    return {
        item.get("role"): item
        for item in resources
        if isinstance(item, dict) and isinstance(item.get("role"), str)
    }


def _schema_document(resource: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / resource["path"]
    value = strict_load_path(path)
    if not isinstance(value, dict):
        raise ValueError(f"{resource['path']} is not an object schema")
    return value


def _expected_profile_ref(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": PROFILE_ID,
        "profile_version": "0.1.0",
        "profile_core_schema_id": PROFILE_SCHEMA_ID,
        "profile_core_raw_digest": manifest["probe_profile_core"]["raw_sha256"],
    }


def _expected_contract(
    schema_index: dict[str, dict[str, Any]],
    manifest: dict[str, Any],
    schema_role: str,
    schema_document: dict[str, Any],
    result_field: str,
    contract_field: str,
    domain: str,
) -> dict[str, Any]:
    required = schema_document.get("required", [])
    included = [f"/{name}" for name in required if name != result_field]
    return {
        "algorithm": "sha256",
        "domain_separator": domain,
        "canonicalization_profile_ref": _expected_profile_ref(manifest),
        "subject_schema_ref": {
            "schema_id": schema_index[schema_role]["schema_id"],
            "schema_digest": schema_index[schema_role]["raw_sha256"],
        },
        "included_json_pointers": included,
        "excluded_json_pointers": [f"/{result_field}"],
    }


def scoped_digest(
    subject: dict[str, Any],
    contract_field: str,
    canonicalize: Callable[[Any], bytes],
) -> dict[str, Any]:
    contract = subject[contract_field]
    projection: dict[str, Any] = {}
    for pointer in contract["included_json_pointers"]:
        parts = pointer_parts(pointer)
        if len(parts) != 1:
            raise ValueError("probe digest pointers must select root members")
        projection[parts[0]] = copy.deepcopy(resolve_pointer(subject, pointer))
    scoped = {
        "digest_contract": copy.deepcopy(contract),
        "resolved_subject_schema": copy.deepcopy(contract["subject_schema_ref"]),
        "projection": projection,
    }
    canonical = canonicalize(scoped)
    digest = sha256_bytes(canonical)
    return {
        "digest": digest,
        "canonical_byte_count": len(canonical),
        "canonical_hex": canonical.hex(),
        "canonical_sha256": digest,
    }


def _exact_false_boundary(value: Any, exact_keys: set[str]) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == exact_keys
        and all(item is False for item in value.values())
    )


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and float(value).is_integer()
        )
    if expected == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        )
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _schema_pointer(document: Any, fragment: str) -> Any:
    if not fragment:
        return document
    if not fragment.startswith("/"):
        raise ValueError("only JSON Pointer schema fragments are supported")
    current = document
    for token in fragment[1:].split("/"):
        decoded = token.replace("~1", "/").replace("~0", "~")
        current = current[int(decoded)] if isinstance(current, list) else current[decoded]
    return current


def validate_probe_schema(
    instance: Any,
    schema: Any,
    registry_by_id: dict[str, dict[str, Any]],
    root_schema: dict[str, Any] | None = None,
    path: str = "",
) -> list[str]:
    """Evaluate the complete JSON-Schema vocabulary used by the nine probes."""

    errors: list[str] = []
    if isinstance(schema, bool):
        return [] if schema else [f"{path}:false_schema"]
    if not isinstance(schema, dict):
        return [f"{path}:invalid_schema"]
    if root_schema is None:
        root_schema = schema
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str):
            return [f"{path}:invalid_ref"]
        if reference.startswith("#"):
            target_root = root_schema
            fragment = reference[1:]
        else:
            base, separator, fragment = reference.partition("#")
            target_root = registry_by_id.get(base)
            if target_root is None:
                return [f"{path}:unresolved_ref"]
            fragment = fragment if separator else ""
        try:
            target = _schema_pointer(target_root, fragment)
        except (KeyError, IndexError, TypeError, ValueError):
            return [f"{path}:unresolved_ref"]
        errors.extend(
            validate_probe_schema(
                instance,
                target,
                registry_by_id,
                target_root,
                path,
            )
        )
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _schema_type_matches(
        instance, expected_type
    ):
        errors.append(f"{path}:type")
        return errors
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}:const")
    if isinstance(schema.get("enum"), list) and instance not in schema["enum"]:
        errors.append(f"{path}:enum")
    all_of = schema.get("allOf")
    if isinstance(all_of, list):
        for index, child in enumerate(all_of):
            errors.extend(
                validate_probe_schema(
                    instance,
                    child,
                    registry_by_id,
                    root_schema,
                    f"{path}/allOf/{index}",
                )
            )
    one_of = schema.get("oneOf")
    if isinstance(one_of, list):
        matches = sum(
            not validate_probe_schema(
                instance, child, registry_by_id, root_schema, path
            )
            for child in one_of
        )
        if matches != 1:
            errors.append(f"{path}:oneOf")
    condition = schema.get("if")
    if isinstance(condition, (dict, bool)):
        condition_passed = not validate_probe_schema(
            instance, condition, registry_by_id, root_schema, path
        )
        branch = schema.get("then" if condition_passed else "else")
        if isinstance(branch, (dict, bool)):
            errors.extend(
                validate_probe_schema(
                    instance, branch, registry_by_id, root_schema, path
                )
            )
    if isinstance(instance, dict):
        required = schema.get("required")
        if isinstance(required, list):
            for name in required:
                if name not in instance:
                    errors.append(f"{path}/{name}:required")
        properties = schema.get("properties")
        if isinstance(properties, dict):
            for name, child in properties.items():
                if name in instance:
                    errors.extend(
                        validate_probe_schema(
                            instance[name],
                            child,
                            registry_by_id,
                            root_schema,
                            f"{path}/{name}",
                        )
                    )
            if schema.get("additionalProperties") is False:
                for name in set(instance) - set(properties):
                    errors.append(f"{path}/{name}:additionalProperties")
    if isinstance(instance, list):
        minimum = schema.get("minItems")
        maximum = schema.get("maxItems")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}:minItems")
        if isinstance(maximum, int) and len(instance) > maximum:
            errors.append(f"{path}:maxItems")
        if schema.get("uniqueItems") is True:
            serialized = [
                json.dumps(item, sort_keys=True, separators=(",", ":"))
                for item in instance
            ]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}:uniqueItems")
        prefix = schema.get("prefixItems")
        if isinstance(prefix, list):
            for index, child in enumerate(prefix[: len(instance)]):
                errors.extend(
                    validate_probe_schema(
                        instance[index],
                        child,
                        registry_by_id,
                        root_schema,
                        f"{path}/{index}",
                    )
                )
        items = schema.get("items")
        start = len(prefix) if isinstance(prefix, list) else 0
        if items is False and len(instance) > start:
            errors.append(f"{path}:items")
        elif isinstance(items, (dict, bool)):
            for index in range(start, len(instance)):
                errors.extend(
                    validate_probe_schema(
                        instance[index],
                        items,
                        registry_by_id,
                        root_schema,
                        f"{path}/{index}",
                    )
                )
    if isinstance(instance, str):
        minimum = schema.get("minLength")
        maximum = schema.get("maxLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}:minLength")
        if isinstance(maximum, int) and len(instance) > maximum:
            errors.append(f"{path}:maxLength")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"{path}:pattern")
    if (
        isinstance(instance, (int, float))
        and not isinstance(instance, bool)
        and math.isfinite(instance)
    ):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and instance < minimum:
            errors.append(f"{path}:minimum")
    return errors


def _expected_schema_member(
    schema_index: dict[str, dict[str, Any]], role: str
) -> dict[str, Any]:
    resource = schema_index[role.removesuffix("_schema")]
    return {
        "schema_id": resource["schema_id"],
        "semantic_version": "0.1.0",
        "byte_digest": resource["raw_sha256"],
        "byte_count": resource["byte_count"],
        "media_type": "application/schema+json",
        "encoding": "utf-8",
        "dialect": "https://json-schema.org/draft/2020-12/schema",
        "root_json_type": "object",
        "retrieval": "content_addressed_retained_raw_bytes",
    }


def _schema_member_role_to_resource(role: str) -> str:
    return role.removesuffix("_schema")


def _member_expected_pair(
    members: dict[str, Any], role: str
) -> dict[str, Any]:
    member = members[role]
    return {
        "member_key": member.get("member_key"),
        "member_digest": member.get("member_digest"),
    }


def _validate_profile(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    schema_index: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    profile = candidate.get("profile")
    if not isinstance(profile, dict):
        errors.append("profile_contract_mismatch")
        return
    if (
        profile.get("schema_version") != "0.1.0"
        or profile.get("artifact_class") != "prq_002_identity_probe_profile"
        or profile.get("profile_id") != PROFILE_ID
        or profile.get("profile_version") != "0.1.0"
        or profile.get("status") != PROBE_STATUS
    ):
        errors.append("profile_contract_mismatch")
    core = manifest.get("base_profile_core", {})
    expected_core_ref = {
        "profile_id": "urn:odeya:canonicalization:odeya-jcs-0.1",
        "profile_version": "0.1.0",
        "profile_core_schema_id": (
            "urn:odeya:schema:canonicalization-profile-core:0.5.0"
        ),
        "profile_core_raw_digest": core.get("raw_sha256"),
        "profile_core_byte_count": core.get("byte_count"),
        "profile_core_schema_raw_digest": core.get("schema_raw_sha256"),
        "profile_core_schema_byte_count": core.get("schema_byte_count"),
    }
    if profile.get("base_profile_core_ref") != expected_core_ref:
        errors.append("profile_base_core_binding_mismatch")
    expected_domains: list[dict[str, Any]] = []
    for domain in manifest.get("domain_bindings", []):
        if not isinstance(domain, dict):
            continue
        resource = schema_index.get(domain.get("schema_role"), {})
        expected_domains.append(
            {
                "domain_separator": domain.get("domain_separator"),
                "subject_class": domain.get("subject_class"),
                "declaring_schema_id": resource.get("schema_id"),
                "declaring_schema_raw_digest": resource.get("raw_sha256"),
                "declaring_schema_byte_count": resource.get("byte_count"),
                "binding_status": "probe_only_not_registered_not_issuable",
            }
        )
    if profile.get("domain_registry") != expected_domains:
        errors.append("profile_domain_registry_mismatch")
    if not _exact_false_boundary(
        profile.get("authority_boundary"), PROFILE_AUTHORITY_KEYS
    ):
        errors.append("profile_authority_boundary_mismatch")


def _validate_schema_members(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    schema_index: dict[str, dict[str, Any]],
    canonicalize: Callable[[Any], bytes],
    errors: list[str],
    records: dict[str, Any],
) -> None:
    members = candidate.get("members")
    if not isinstance(members, dict):
        errors.append("member_inventory_mismatch")
        return
    schema_member_schema = _schema_document(schema_index["schema_member_probe"])
    expected_contract = _expected_contract(
        schema_index,
        manifest,
        "schema_member_probe",
        schema_member_schema,
        "member_digest",
        "member_digest_contract",
        "odeya-prq-002-schema-member-probe-v1",
    )
    for role in SCHEMA_MEMBER_ROLES:
        member = members.get(role)
        if not isinstance(member, dict):
            errors.append("schema_member_inventory_mismatch")
            continue
        if set(member) != set(schema_member_schema.get("required", [])):
            errors.append("schema_member_shape_mismatch")
        expected_schema_bytes = _expected_schema_member(schema_index, role)
        if member.get("schema_bytes") != expected_schema_bytes:
            errors.append("schema_member_raw_binding_mismatch")
        expected_key = (
            f"{expected_schema_bytes['schema_id']}@"
            f"{expected_schema_bytes['semantic_version']}"
        )
        if member.get("member_key") != expected_key:
            errors.append("schema_member_key_mismatch")
        if member.get("member_digest_contract") != expected_contract:
            errors.append("schema_member_digest_contract_mismatch")
        try:
            record = scoped_digest(member, "member_digest_contract", canonicalize)
        except (KeyError, TypeError, ValueError):
            errors.append("schema_member_digest_construction_failed")
            continue
        records[role] = record
        if member.get("member_digest") != record["digest"]:
            errors.append("schema_member_digest_mismatch")


def _state_expected_schema_ref(
    members: dict[str, Any], schema_index: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    resource = schema_index["structural_state"]
    schema_member = members["structural_state_schema"]
    return {
        "schema_member_key": schema_member["member_key"],
        "schema_id": resource["schema_id"],
        "semantic_version": "0.1.0",
        "byte_digest": resource["raw_sha256"],
        "byte_count": resource["byte_count"],
        "dialect": "https://json-schema.org/draft/2020-12/schema",
        "root_json_type": "object",
        "schema_member_digest": schema_member["member_digest"],
    }


def _event_expected_schema_ref(
    members: dict[str, Any], schema_index: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    resource = schema_index["structural_event"]
    schema_member = members["structural_event_schema"]
    return {
        "schema_member_key": schema_member["member_key"],
        "schema_id": resource["schema_id"],
        "semantic_version": "0.1.0",
        "byte_digest": resource["raw_sha256"],
        "byte_count": resource["byte_count"],
        "dialect": "https://json-schema.org/draft/2020-12/schema",
        "root_json_type": "object",
        "schema_member_digest": schema_member["member_digest"],
    }


def _validate_graph_members(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    schema_index: dict[str, dict[str, Any]],
    canonicalize: Callable[[Any], bytes],
    errors: list[str],
    records: dict[str, Any],
) -> None:
    members = candidate.get("members")
    if not isinstance(members, dict):
        return
    expected_member_keys = set(MEMBER_ROLES)
    if set(members) != expected_member_keys:
        errors.append("member_inventory_mismatch")
    state = members.get("aggregate_state")
    reducer = members.get("reducer")
    event = members.get("event")
    if not all(isinstance(item, dict) for item in (state, reducer, event)):
        errors.append("graph_member_inventory_mismatch")
        return
    assert isinstance(state, dict)
    assert isinstance(reducer, dict)
    assert isinstance(event, dict)

    state_schema = _schema_document(schema_index["aggregate_state_member_probe"])
    state_contract = _expected_contract(
        schema_index,
        manifest,
        "aggregate_state_member_probe",
        state_schema,
        "member_digest",
        "member_digest_contract",
        ROLE_DOMAINS["aggregate_state"],
    )
    if (
        state.get("member_key") != "structural-aggregate"
        or state.get("aggregate_type") != "structural-aggregate"
        or state.get("state_subject_id") != "state.structural-aggregate"
        or state.get("state_subject_version") != "0.1.0"
        or state.get("owning_module") != "structural-module"
    ):
        errors.append("state_identity_mismatch")
    if state.get("state_schema_ref") != _state_expected_schema_ref(
        members, schema_index
    ):
        errors.append("state_schema_reference_mismatch")
    expected_reducer_reverse = {
        "aggregate_type": "structural-aggregate",
        "reducer_id": "reducer.structural-aggregate",
        "reducer_version": "0.1.0",
        "reference_kind": "logical_reverse_reference",
        "resolution_requirement": "future_same_root_exact_member",
    }
    expected_event_reverse = {
        "event_type": "structural.event_recorded",
        "event_version": "0.1.0",
        "reference_kind": "logical_reverse_reference",
        "resolution_requirement": "future_same_root_exact_member",
    }
    if (
        state.get("canonical_reducer_ref") != expected_reducer_reverse
        or state.get("origin_event_refs") != [expected_event_reverse]
    ):
        errors.append("state_reverse_reference_mismatch")
    if state.get("member_digest_contract") != state_contract:
        errors.append("state_digest_contract_mismatch")
    try:
        state_record = scoped_digest(
            state, "member_digest_contract", canonicalize
        )
        records["aggregate_state"] = state_record
        if state.get("member_digest") != state_record["digest"]:
            errors.append("state_member_digest_mismatch")
    except (KeyError, TypeError, ValueError):
        errors.append("state_digest_construction_failed")

    reducer_schema = _schema_document(schema_index["reducer_member_probe"])
    reducer_contract = _expected_contract(
        schema_index,
        manifest,
        "reducer_member_probe",
        reducer_schema,
        "member_digest",
        "member_digest_contract",
        ROLE_DOMAINS["reducer"],
    )
    if (
        reducer.get("member_key") != "structural-aggregate"
        or reducer.get("aggregate_type") != "structural-aggregate"
        or reducer.get("reducer_id") != "reducer.structural-aggregate"
        or reducer.get("reducer_version") != "0.1.0"
        or reducer.get("owning_module") != "structural-module"
    ):
        errors.append("reducer_identity_mismatch")
    expected_state_ref = {
        "aggregate_type": "structural-aggregate",
        "state_subject_id": "state.structural-aggregate",
        "state_subject_version": "0.1.0",
        "state_member_digest": state.get("member_digest"),
        "resolution": "exact_probe_member_digest",
    }
    if reducer.get("state_subject_ref") != expected_state_ref:
        errors.append("reducer_state_reference_mismatch")
    if reducer.get("accepted_event_refs") != [expected_event_reverse]:
        errors.append("reducer_reverse_reference_mismatch")
    if reducer.get("member_digest_contract") != reducer_contract:
        errors.append("reducer_digest_contract_mismatch")
    try:
        reducer_record = scoped_digest(
            reducer, "member_digest_contract", canonicalize
        )
        records["reducer"] = reducer_record
        if reducer.get("member_digest") != reducer_record["digest"]:
            errors.append("reducer_member_digest_mismatch")
    except (KeyError, TypeError, ValueError):
        errors.append("reducer_digest_construction_failed")

    event_schema = _schema_document(schema_index["event_member_probe"])
    event_contract = _expected_contract(
        schema_index,
        manifest,
        "event_member_probe",
        event_schema,
        "member_digest",
        "member_digest_contract",
        ROLE_DOMAINS["event"],
    )
    if (
        event.get("member_key") != "structural.event_recorded@0.1.0"
        or event.get("event_type") != "structural.event_recorded"
        or event.get("event_version") != "0.1.0"
        or event.get("payload_type_id")
        != "urn:odeya:architecture:event-payload:structural.event-recorded:0.1.0"
    ):
        errors.append("event_identity_mismatch")
    expected_payload = {
        "event_envelope_schema_ref": _event_expected_schema_ref(
            members, schema_index
        ),
        "payload_json_pointer": "/oneOf/0/properties/payload",
        "payload_required": True,
        "nullable": False,
        "exact_branch_required": True,
    }
    if event.get("payload_contract") != expected_payload:
        errors.append("event_schema_reference_mismatch")
    expected_owner = {
        "owning_module": "structural-module",
        "aggregate_type": "structural-aggregate",
        "ownership_cardinality": "exactly_one",
    }
    if event.get("aggregate_owner") != expected_owner:
        errors.append("event_aggregate_owner_mismatch")
    expected_command = {
        "command_type": "structural.command_probe",
        "command_version": "0.1.0",
        "reference_kind": "logical_reverse_reference",
        "resolution_requirement": "future_same_root_exact_member",
    }
    if event.get("producer_command_refs") != [expected_command]:
        errors.append("event_command_reference_mismatch")
    expected_reducer_ref = {
        "aggregate_type": "structural-aggregate",
        "reducer_id": "reducer.structural-aggregate",
        "reducer_version": "0.1.0",
        "reducer_member_digest": reducer.get("member_digest"),
        "resolution": "exact_probe_member_digest",
    }
    if event.get("canonical_reducer_ref") != expected_reducer_ref:
        errors.append("event_reducer_reference_mismatch")
    if event.get("member_digest_contract") != event_contract:
        errors.append("event_digest_contract_mismatch")
    try:
        event_record = scoped_digest(event, "member_digest_contract", canonicalize)
        records["event"] = event_record
        if event.get("member_digest") != event_record["digest"]:
            errors.append("event_member_digest_mismatch")
    except (KeyError, TypeError, ValueError):
        errors.append("event_digest_construction_failed")


def _validate_commitments(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    schema_index: dict[str, dict[str, Any]],
    canonicalize: Callable[[Any], bytes],
    errors: list[str],
    records: dict[str, Any],
) -> None:
    commitments = candidate.get("commitments")
    members = candidate.get("members")
    profile = candidate.get("profile")
    if (
        not isinstance(commitments, dict)
        or not isinstance(members, dict)
        or not isinstance(profile, dict)
    ):
        errors.append("commitment_inventory_mismatch")
        return
    if set(commitments) != set(FAMILIES):
        errors.append("commitment_inventory_mismatch")
    schema = _schema_document(schema_index["ordered_commitment_probe"])
    expected_contract = _expected_contract(
        schema_index,
        manifest,
        "ordered_commitment_probe",
        schema,
        "ordered_member_pairs_digest",
        "ordered_member_pairs_digest_contract",
        "odeya-prq-002-ordered-member-map-commitment-probe-v1",
    )
    for family in FAMILIES:
        commitment = commitments.get(family)
        if not isinstance(commitment, dict):
            errors.append("commitment_inventory_mismatch")
            continue
        expected_pairs = sorted(
            [
                _member_expected_pair(members, role)
                for role in FAMILY_MEMBER_ROLES[family]
            ],
            key=lambda item: item["member_key"].encode("utf-8"),
        )
        observed = commitment.get("ordered_members")
        if not isinstance(observed, list):
            errors.append("commitment_member_set_mismatch")
        else:
            keys = [
                item.get("member_key")
                for item in observed
                if isinstance(item, dict)
            ]
            if len(keys) != len(set(keys)):
                errors.append("commitment_member_keys_not_unique")
            if keys != sorted(keys, key=lambda item: item.encode("utf-8")):
                errors.append("commitment_order_mismatch")
            if observed != expected_pairs:
                errors.append("commitment_member_set_mismatch")
        if commitment.get("member_count") != len(expected_pairs):
            errors.append("commitment_count_mismatch")
        expected_key_contract = profile.get("member_key_profiles", {}).get(family)
        if (
            commitment.get("registry_family") != family
            or commitment.get("algorithm")
            != "odeya-canonical-map-commitment-v1"
            or commitment.get("member_key_contract") != expected_key_contract
            or expected_key_contract.get("member_key_expression")
            != FAMILY_KEY_EXPRESSIONS[family]
        ):
            errors.append("commitment_family_contract_mismatch")
        if commitment.get("ordered_member_pairs_digest_contract") != expected_contract:
            errors.append("commitment_digest_contract_mismatch")
        try:
            record = scoped_digest(
                commitment,
                "ordered_member_pairs_digest_contract",
                canonicalize,
            )
            records[family] = record
            if commitment.get("ordered_member_pairs_digest") != record["digest"]:
                errors.append("commitment_digest_mismatch")
        except (KeyError, TypeError, ValueError):
            errors.append("commitment_digest_construction_failed")


def _validate_snapshots(
    candidate: dict[str, Any],
    manifest: dict[str, Any],
    schema_index: dict[str, dict[str, Any]],
    canonicalize: Callable[[Any], bytes],
    errors: list[str],
    records: dict[str, Any],
) -> None:
    snapshots = candidate.get("snapshots")
    commitments = candidate.get("commitments")
    if not isinstance(snapshots, dict) or not isinstance(commitments, dict):
        errors.append("snapshot_inventory_mismatch")
        return
    if set(snapshots) != set(FAMILIES):
        errors.append("snapshot_inventory_mismatch")
    schema = _schema_document(schema_index["pure_snapshot_probe"])
    expected_top_keys = set(schema.get("required", []))
    for family in FAMILIES:
        snapshot = snapshots.get(family)
        if not isinstance(snapshot, dict):
            errors.append("snapshot_inventory_mismatch")
            continue
        if set(snapshot) != expected_top_keys:
            errors.append("snapshot_forbidden_member_present")
        expected_contract = _expected_contract(
            schema_index,
            manifest,
            "pure_snapshot_probe",
            schema,
            "snapshot_digest",
            "snapshot_digest_contract",
            SNAPSHOT_DOMAINS[family],
        )
        if (
            snapshot.get("registry_family") != family
            or snapshot.get("identity_scope") != IDENTITY_SCOPE
            or snapshot.get("version") != "0.1.0"
        ):
            errors.append("snapshot_identity_mismatch")
        if snapshot.get("registry_id") != SNAPSHOT_REGISTRY_IDS[family]:
            errors.append("snapshot_registry_id_mismatch")
        supersedes = snapshot.get("supersedes_snapshot_ref")
        if supersedes is not None:
            errors.append("snapshot_predecessor_reference_mismatch")
        if snapshot.get("canonicalization_profile_ref") != _expected_profile_ref(
            manifest
        ):
            errors.append("snapshot_profile_reference_mismatch")
        if snapshot.get("member_set_commitment") != commitments.get(family):
            errors.append("snapshot_commitment_binding_mismatch")
        if snapshot.get("snapshot_digest_contract") != expected_contract:
            errors.append("snapshot_digest_contract_mismatch")
        try:
            record = scoped_digest(
                snapshot, "snapshot_digest_contract", canonicalize
            )
            records[family] = record
            if snapshot.get("snapshot_digest") != record["digest"]:
                errors.append("snapshot_digest_mismatch")
        except (KeyError, TypeError, ValueError):
            errors.append("snapshot_digest_construction_failed")


def evaluate_candidate(
    candidate: Any,
    manifest: dict[str, Any],
    canonicalize: Callable[[Any], bytes],
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(candidate, dict):
        return ["cohort_shape_mismatch"], {}
    expected_top = {
        "schema_version",
        "artifact_class",
        "status",
        "profile",
        "members",
        "commitments",
        "snapshots",
        "authority_boundary",
    }
    if set(candidate) != expected_top:
        errors.append("cohort_shape_mismatch")
    if (
        candidate.get("schema_version") != "0.1.0"
        or candidate.get("artifact_class")
        != "prq_002_identity_probe_candidate_cohort"
        or candidate.get("status") != PROBE_STATUS
    ):
        errors.append("cohort_status_mismatch")
    if not _exact_false_boundary(
        candidate.get("authority_boundary"), COHORT_AUTHORITY_KEYS
    ):
        errors.append("cohort_authority_boundary_mismatch")
    schema_index = _schema_index(manifest)
    if set(schema_index) != {
        "identity_probe_profile",
        "schema_member_probe",
        "aggregate_state_member_probe",
        "reducer_member_probe",
        "event_member_probe",
        "ordered_commitment_probe",
        "pure_snapshot_probe",
        "structural_state",
        "structural_event",
    }:
        errors.append("schema_resource_inventory_mismatch")
        return unique_errors(errors), {}
    for field, code in (
        ("base_profile_core", "base_profile_core_raw_binding_mismatch"),
        ("probe_profile_core", "probe_profile_core_raw_binding_mismatch"),
    ):
        item = manifest.get(field)
        if not isinstance(item, dict):
            errors.append(code)
            continue
        try:
            observed = binding(ROOT / item["path"])
        except (OSError, KeyError, TypeError):
            errors.append(code)
            continue
        if (
            item.get("raw_sha256") != observed["raw_sha256"]
            or item.get("byte_count") != observed["byte_count"]
        ):
            errors.append(code)
        try:
            observed_schema = binding(ROOT / item["schema_path"])
        except (OSError, KeyError, TypeError):
            errors.append(f"{field}_schema_raw_binding_mismatch")
            continue
        if (
            item.get("schema_raw_sha256") != observed_schema["raw_sha256"]
            or item.get("schema_byte_count") != observed_schema["byte_count"]
        ):
            errors.append(f"{field}_schema_raw_binding_mismatch")
    try:
        retained_probe_core = strict_load_path(
            ROOT / manifest["probe_profile_core"]["path"]
        )
    except (OSError, KeyError, TypeError, StrictInputError):
        retained_probe_core = None
    if candidate.get("profile") != retained_probe_core:
        errors.append("probe_profile_core_instance_mismatch")
    schema_documents: dict[str, dict[str, Any]] = {}
    for role, resource in schema_index.items():
        path = ROOT / resource["path"]
        if not path.is_file():
            errors.append("schema_resource_missing")
            continue
        observed = binding(path)
        if (
            resource.get("raw_sha256") != observed["raw_sha256"]
            or resource.get("byte_count") != observed["byte_count"]
        ):
            errors.append("schema_resource_raw_binding_mismatch")
        try:
            schema = _schema_document(resource)
        except (OSError, ValueError, StrictInputError):
            errors.append("schema_resource_parse_failure")
            continue
        schema_documents[role] = schema
        if schema.get("$id") != resource.get("schema_id"):
            errors.append("schema_resource_id_mismatch")
    registry_by_id = {
        schema["$id"]: schema
        for schema in schema_documents.values()
        if isinstance(schema.get("$id"), str)
    }
    profile = candidate.get("profile")
    if (
        "identity_probe_profile" not in schema_documents
        or validate_probe_schema(
            profile,
            schema_documents["identity_probe_profile"],
            registry_by_id,
        )
    ):
        errors.append("profile_schema_invalid")
    members = candidate.get("members")
    if isinstance(members, dict):
        for role in SCHEMA_MEMBER_ROLES:
            if validate_probe_schema(
                members.get(role),
                schema_documents.get("schema_member_probe", {}),
                registry_by_id,
            ):
                errors.append("schema_member_schema_invalid")
        for role, schema_role in (
            ("aggregate_state", "aggregate_state_member_probe"),
            ("reducer", "reducer_member_probe"),
            ("event", "event_member_probe"),
        ):
            if validate_probe_schema(
                members.get(role),
                schema_documents.get(schema_role, {}),
                registry_by_id,
            ):
                errors.append(f"{role}_schema_invalid")
    commitments = candidate.get("commitments")
    if isinstance(commitments, dict):
        for family in FAMILIES:
            if validate_probe_schema(
                commitments.get(family),
                schema_documents.get("ordered_commitment_probe", {}),
                registry_by_id,
            ):
                errors.append("commitment_schema_invalid")
    snapshots = candidate.get("snapshots")
    if isinstance(snapshots, dict):
        for family in FAMILIES:
            if validate_probe_schema(
                snapshots.get(family),
                schema_documents.get("pure_snapshot_probe", {}),
                registry_by_id,
            ):
                errors.append("snapshot_schema_invalid")
    _validate_profile(candidate, manifest, schema_index, errors)
    member_records: dict[str, Any] = {}
    _validate_schema_members(
        candidate, manifest, schema_index, canonicalize, errors, member_records
    )
    _validate_graph_members(
        candidate, manifest, schema_index, canonicalize, errors, member_records
    )
    commitment_records: dict[str, Any] = {}
    _validate_commitments(
        candidate,
        manifest,
        schema_index,
        canonicalize,
        errors,
        commitment_records,
    )
    snapshot_records: dict[str, Any] = {}
    _validate_snapshots(
        candidate,
        manifest,
        schema_index,
        canonicalize,
        errors,
        snapshot_records,
    )
    projection = {
        "cohort_census": {
            "profile_instances": 1,
            "schema_members": len(SCHEMA_MEMBER_ROLES),
            "graph_members": 3,
            "members": len(MEMBER_ROLES),
            "commitments": len(FAMILIES),
            "snapshots": len(FAMILIES),
            "total_probe_objects": 21,
        },
        "member_digest_records": member_records,
        "commitment_digest_records": commitment_records,
        "snapshot_digest_records": snapshot_records,
    }
    return unique_errors(errors), projection


def _materialize_case(
    base_raw: bytes, case: dict[str, Any]
) -> tuple[Any | None, str | None]:
    mutation = case.get("mutation")
    if mutation is None:
        try:
            return strict_load_bytes(base_raw), None
        except StrictInputError as exc:
            return None, exc.code
    if not isinstance(mutation, dict):
        raise ValueError("case mutation must be an object")
    if mutation.get("layer") == "raw":
        try:
            mutated = apply_raw_mutation(base_raw, mutation)
            return strict_load_bytes(mutated), None
        except StrictInputError as exc:
            return None, exc.code
    if mutation.get("layer") != "object":
        raise ValueError("case mutation layer must be raw or object")
    try:
        candidate = strict_load_bytes(base_raw)
    except StrictInputError as exc:
        return None, exc.code
    apply_patch(candidate, mutation)
    return candidate, None


def evaluate_cases(
    base_raw: bytes,
    manifest: dict[str, Any],
    cases: dict[str, Any],
    canonicalize: Callable[[Any], bytes],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    case_rows: list[dict[str, Any]] = []
    safe_projection: dict[str, Any] = {}
    for case in cases.get("cases", []):
        candidate, strict_error = _materialize_case(base_raw, case)
        if strict_error is not None:
            errors = [strict_error]
            projection: dict[str, Any] = {}
        else:
            errors, projection = evaluate_candidate(
                candidate, manifest, canonicalize
            )
        if case.get("kind") == "safe":
            safe_projection = projection
        case_rows.append(
            {
                "id": case.get("id"),
                "kind": case.get("kind"),
                "outcome": "accepted" if not errors else "refused",
                "errors": errors,
            }
        )
    summary = {
        "case_count": len(case_rows),
        "safe_count": sum(row["kind"] == "safe" for row in case_rows),
        "adversarial_count": sum(
            row["kind"] == "adversarial" for row in case_rows
        ),
        "accepted_count": sum(row["outcome"] == "accepted" for row in case_rows),
        "refused_count": sum(row["outcome"] == "refused" for row in case_rows),
    }
    return case_rows, {"safe_projection": safe_projection, "summary": summary}


def _external_canonicalizer(package_root: Path) -> Callable[[Any], bytes]:
    if not package_root.is_absolute() or not package_root.is_dir():
        raise ValueError("rfc8785 package root must be an absolute directory")
    if any(
        path.name == "__pycache__" or path.suffix == ".pyc"
        for path in package_root.rglob("*")
    ):
        raise ValueError("rfc8785 package root contains import-cache residue")
    observed = {
        path.name: binding(path)
        for path in package_root.iterdir()
        if path.is_file()
    }
    if observed != EXPECTED_RFC8785_SOURCE_BINDINGS:
        raise ValueError("rfc8785 package source payload does not match")
    implementation_path = package_root / "_impl.py"
    namespace: dict[str, Any] = {
        "__builtins__": __builtins__,
        "__file__": str(implementation_path),
        "__name__": "odeya_prq002_verified_rfc8785_impl",
        "__package__": "",
    }
    source = implementation_path.read_bytes()
    exec(compile(source, str(implementation_path), "exec"), namespace)
    dumps = namespace.get("dumps")
    if not callable(dumps):
        raise ValueError("verified rfc8785 source has no dumps callable")

    def canonicalize(value: Any) -> bytes:
        rendered = dumps(value)
        if not isinstance(rendered, bytes):
            raise ValueError("verified rfc8785 dumps did not return bytes")
        return rendered

    return canonicalize


def _source_file_binding(source_manifest: dict[str, Any]) -> dict[str, Any]:
    rows = source_manifest.get("source_files", [])
    for row in rows:
        if row.get("repository_path", "").endswith("/python/runner.py"):
            return copy.deepcopy(row)
    raise ValueError("Python source manifest does not bind runner.py")


def build_result(
    input_path: Path,
    manifest_path: Path,
    cases_path: Path,
    canonicalize: Callable[[Any], bytes],
) -> dict[str, Any]:
    manifest = strict_load_path(manifest_path)
    cases = strict_load_path(cases_path)
    base_raw = input_path.read_bytes()
    case_rows, fold = evaluate_cases(
        base_raw,
        manifest,
        cases,
        canonicalize,
    )
    source_manifest_path = SUITE / "python/source-manifest.json"
    dependency_lock_path = SUITE / "python/requirements.lock"
    suite_manifest_path = SUITE / "manifest.json"
    source_manifest = strict_load_path(source_manifest_path)
    expected_rows = {
        item["id"]: item for item in cases.get("cases", [])
    }
    expectations_match = all(
        row["errors"] == expected_rows[row["id"]].get("expected_errors")
        and (
            row["kind"] != "adversarial"
            or set(expected_rows[row["id"]].get("intent_errors", []))
            .issubset(row["errors"])
        )
        for row in case_rows
    )
    safe_ok = (
        fold["summary"]["safe_count"] == 1
        and fold["summary"]["accepted_count"] == 1
        and fold["summary"]["refused_count"]
        == fold["summary"]["adversarial_count"]
    )
    parser_semantics = parser_semantics_observation()
    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002_identity_probe_recomputation_result",
        "result_id": "prq-002-identity-result.python-rfc8785-0_1_4.0001",
        "status": (
            "pass"
            if expectations_match
            and safe_ok
            and parser_semantics == EXPECTED_PARSER_SEMANTICS
            else "fail"
        ),
        "evidence_status": PROBE_STATUS,
        "implementation": {
            "role": "python",
            "runtime": "CPython",
            "runtime_version": platform.python_version(),
            "package": "rfc8785",
            "package_version": "0.1.4",
            "canonicalization_entrypoint": (
                "verified_source_exec:rfc8785/_impl.py:dumps"
            ),
            "source_file_binding": _source_file_binding(source_manifest),
            "source_manifest_binding": binding(source_manifest_path),
            "dependency_lock_binding": binding(dependency_lock_path),
            "peer_source_consumed": False,
            "generated_source_consumed": False,
            "expected_result_fixture_consumed": False,
        },
        "input_bindings": {
            "suite_manifest": binding(suite_manifest_path),
            "input_manifest": binding(manifest_path),
            "candidate_cohort": binding(input_path),
            "cases": binding(cases_path),
        },
        "safe_projection": fold["safe_projection"],
        "parser_semantics": parser_semantics,
        "cases": case_rows,
        "summary": fold["summary"],
        "authority_boundary": {
            "canonical_identity_issued": False,
            "registry_admission": False,
            "engine_contract_root_binding": False,
            "gate_a_acceptance": False,
            "runtime_authority": False,
            "external_effect_authority": False,
            "publication_authority": False,
        },
    }


def build_execution_attestation(
    input_path: Path,
    manifest_path: Path,
    cases_path: Path,
    package_root: Path,
    challenge: str,
    result_line_binding: dict[str, Any],
) -> dict[str, Any]:
    runner_path = Path(__file__).resolve()
    source_manifest_path = SUITE / "python/source-manifest.json"
    canonicalizer_path = package_root / "_impl.py"

    def attested(path: Path) -> dict[str, Any]:
        return {"absolute_path": str(path), **binding(path)}

    return {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002_identity_probe_execution_attestation",
        "implementation_role": "python",
        "challenge": challenge,
        "result_line_binding": result_line_binding,
        "runtime": {
            "name": "CPython",
            "version": platform.python_version(),
            "sys_executable": sys.executable,
            "resolved_executable": str(Path(sys.executable).resolve()),
            "executable_binding": binding(Path(sys.executable).resolve()),
            "sys_prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "isolated": sys.flags.isolated == 1,
            "site_initialization_disabled": sys.flags.no_site == 1,
            "environment_ignored": sys.flags.ignore_environment == 1,
            "user_site_disabled": sys.flags.no_user_site == 1,
            "safe_path": sys.flags.safe_path,
            "bytecode_writes_disabled": sys.flags.dont_write_bytecode == 1,
        },
        "process_argv": sys.argv,
        "bindings": {
            "runner": attested(runner_path),
            "input": attested(input_path),
            "input_manifest": attested(manifest_path),
            "cases": attested(cases_path),
            "source_manifest": attested(source_manifest_path),
            "canonicalizer_source": attested(canonicalizer_path),
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--rfc8785-package-root", type=Path, required=True)
    parser.add_argument("--attestation-challenge", required=True)
    parser.add_argument(
        "--emit-execution-attestation",
        action="store_true",
        required=True,
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        package_root = args.rfc8785_package_root.resolve()
        if not CHALLENGE_RE.fullmatch(args.attestation_challenge):
            raise ValueError("invalid execution-attestation challenge")
        required_flags = (
            sys.flags.isolated == 1
            and sys.flags.no_site == 1
            and sys.flags.ignore_environment == 1
            and sys.flags.no_user_site == 1
            and sys.flags.safe_path
            and sys.flags.dont_write_bytecode == 1
        )
        if not required_flags:
            raise ValueError("Python evaluator requires -I -S -B")
        canonicalize = _external_canonicalizer(package_root)
        result = build_result(
            args.input.resolve(),
            args.manifest.resolve(),
            args.cases.resolve(),
            canonicalize,
        )
        result_line = canonicalize(result) + b"\n"
        attestation = build_execution_attestation(
            args.input.resolve(),
            args.manifest.resolve(),
            args.cases.resolve(),
            package_root,
            args.attestation_challenge,
            {
                "raw_sha256": (
                    "sha256:" + hashlib.sha256(result_line).hexdigest()
                ),
                "byte_count": len(result_line),
            },
        )
        attestation_line = canonicalize(attestation) + b"\n"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(
            json.dumps(
                {
                    "schema_version": "0.1.0",
                    "artifact_class": (
                        "prq_002_identity_probe_recomputation_failure"
                    ),
                    "status": "fail",
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1
    sys.stdout.buffer.write(attestation_line)
    sys.stdout.buffer.write(result_line)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
