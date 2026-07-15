#!/usr/bin/env python3
"""Independent Python architecture-conformance path for odeya-jcs-0.1."""

from __future__ import annotations

import hashlib
import importlib.metadata
import inspect
import json
import math
import platform
import re
import sys
from copy import deepcopy
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import rfc8785


SUITE = Path(__file__).resolve().parent
ROOT = SUITE.parents[1]
MANIFEST_PATH = SUITE / "manifest.json"
SOURCE_LOCK_PATH = SUITE / "source-lock.json"
UPSTREAM_PATH = SUITE / "official/cyberphone/vectors.json"
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"
TIMESTAMP_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{6})Z$"
)
DECIMAL_RE = re.compile(
    r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:e-?(?:0|[1-9][0-9]*))?$"
)
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SCHEMA_ID_RE = re.compile(
    r"^urn:odeya:schema:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?:[0-9]+\.[0-9]+\.[0-9]+$"
)
NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
MISSING_REASONS = {"unknown", "unmeasured", "unavailable", "withheld", "not_applicable"}


class Refusal(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class DuplicateKey(Exception):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load_control(path: Path) -> Any:
    return json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)


def generate_recipe(recipe: dict[str, Any]) -> bytes:
    kind = recipe["kind"]
    if kind == "ascii_string":
        return ('{"x":"' + ("a" * int(recipe["length"])) + '"}').encode("utf-8")
    if kind == "nested_array":
        depth = int(recipe["depth"])
        return (("[" * depth) + "0" + ("]" * depth)).encode("utf-8")
    if kind == "object_members":
        count = int(recipe["count"])
        return ("{" + ",".join(f'"k{i}":0' for i in range(count)) + "}").encode("utf-8")
    if kind == "array_items":
        count = int(recipe["count"])
        return ("[" + ",".join("0" for _ in range(count)) + "]").encode("utf-8")
    if kind == "number_fraction_zeros":
        return ('{"x":1.' + ("0" * int(recipe["fraction_digits"])) + "}").encode("utf-8")
    if kind == "node_forest":
        branches = int(recipe["branches"])
        items = int(recipe["items_per_branch"])
        array = "[" + ",".join("0" for _ in range(items)) + "]"
        return ("{" + ",".join(f'"b{i}":{array}' for i in range(branches)) + "}").encode("utf-8")
    if kind == "temporal_measurement_decimal":
        value = "1" * int(recipe["decimal_length"])
        return (
            '{"observed_at":"2026-07-15T12:34:56.000000Z",'
            '"measurement":{"value":"'
            + value
            + '","semantic_type":"measured_quantity","unit":{"system":"SI",'
            '"code":"m"},"precision":{"kind":"significant_digits","value":64}}}'
        ).encode("utf-8")
    raise ValueError(f"unknown input recipe: {kind}")


def input_bytes(vector: dict[str, Any], upstream: dict[str, Any]) -> bytes:
    if "upstream_vector" in vector:
        return bytes.fromhex(upstream[vector["upstream_vector"]]["input_hex"])
    if "input_utf8" in vector:
        return vector["input_utf8"].encode("utf-8")
    if "input_hex" in vector:
        return bytes.fromhex(vector["input_hex"])
    if "input_recipe" in vector:
        return generate_recipe(vector["input_recipe"])
    raise ValueError(f"vector {vector.get('id')} has no input")


def scan_number_tokens(text: str, limits: dict[str, int]) -> None:
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == "-" or char.isdigit():
            match = NUMBER_RE.match(text, index)
            if match is None:
                index += 1
                continue
            token = match.group(0)
            if len(token.encode("ascii")) > limits["max_number_token_bytes"]:
                raise Refusal("ODEYA_LIMIT_NUMBER_TOKEN")
            try:
                exact = Decimal(token)
            except InvalidOperation:
                raise Refusal("ODEYA_PARSE_SYNTAX") from None
            if token.startswith("-") and exact.is_zero():
                raise Refusal("ODEYA_NUMBER_NEGATIVE_ZERO")
            parsed = float(token)
            if not math.isfinite(parsed):
                raise Refusal("ODEYA_NUMBER_NONFINITE")
            if parsed == 0.0 and not exact.is_zero():
                raise Refusal("ODEYA_NUMBER_UNDERFLOW")
            if "." not in token and "e" not in token.lower():
                if abs(int(token)) > limits["max_safe_integer"]:
                    raise Refusal("ODEYA_NUMBER_DOMAIN")
            index = match.end()
            continue
        index += 1


def reject_constants(_: str) -> None:
    raise Refusal("ODEYA_PARSE_SYNTAX")


def has_unpaired_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        return any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    if isinstance(value, list):
        return any(has_unpaired_surrogate(item) for item in value)
    if isinstance(value, dict):
        return any(
            has_unpaired_surrogate(key) or has_unpaired_surrogate(item)
            for key, item in value.items()
        )
    return False


def enforce_tree_limits(value: Any, limits: dict[str, int]) -> None:
    nodes = 0

    def visit(item: Any, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        if nodes > limits["max_total_nodes"]:
            raise Refusal("ODEYA_LIMIT_TOTAL_NODES")
        if depth > limits["max_depth"]:
            raise Refusal("ODEYA_LIMIT_DEPTH")
        if isinstance(item, str):
            if len(item) > limits["max_string_code_points"]:
                raise Refusal("ODEYA_LIMIT_STRING")
        elif isinstance(item, list):
            if len(item) > limits["max_array_items"]:
                raise Refusal("ODEYA_LIMIT_ARRAY_ITEMS")
            for child in item:
                visit(child, depth + 1)
        elif isinstance(item, dict):
            if len(item) > limits["max_object_members"]:
                raise Refusal("ODEYA_LIMIT_OBJECT_MEMBERS")
            for key, child in item.items():
                if len(key) > limits["max_string_code_points"]:
                    raise Refusal("ODEYA_LIMIT_STRING")
                visit(child, depth + 1)

    visit(value, 1)


def strict_parse(raw: bytes, limits: dict[str, int]) -> Any:
    if len(raw) > limits["max_bytes"]:
        raise Refusal("ODEYA_LIMIT_BYTES")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise Refusal("ODEYA_PARSE_BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise Refusal("ODEYA_PARSE_UTF8") from None
    scan_number_tokens(text, limits)
    try:
        value = json.loads(
            text,
            object_pairs_hook=strict_pairs,
            parse_constant=reject_constants,
        )
    except DuplicateKey:
        raise Refusal("ODEYA_PARSE_DUPLICATE_KEY") from None
    except Refusal:
        raise
    except (json.JSONDecodeError, ValueError, RecursionError):
        raise Refusal("ODEYA_PARSE_SYNTAX") from None
    if has_unpaired_surrogate(value):
        raise Refusal("ODEYA_PARSE_UNPAIRED_SURROGATE")
    enforce_tree_limits(value, limits)
    return value


def exact_keys(value: Any, required: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != required:
        raise Refusal(code)
    return value


def validate_timestamp(value: Any) -> None:
    if not isinstance(value, str):
        raise Refusal("ODEYA_TIMESTAMP_PROFILE")
    match = TIMESTAMP_RE.fullmatch(value)
    if match is None:
        raise Refusal("ODEYA_TIMESTAMP_PROFILE")
    year, month, day, hour, minute, second, micros = map(int, match.groups())
    try:
        datetime(year, month, day, hour, minute, second, micros)
    except ValueError:
        raise Refusal("ODEYA_TIMESTAMP_PROFILE") from None


def decimal_parts(value: str) -> tuple[str, str, int]:
    unsigned = value[1:] if value.startswith("-") else value
    if "e" in unsigned:
        mantissa, exponent_text = unsigned.split("e", 1)
        exponent = -int(exponent_text[1:]) if exponent_text.startswith("-") else int(exponent_text)
    else:
        mantissa, exponent = unsigned, 0
    integer, dot, fraction = mantissa.partition(".")
    return integer, fraction if dot else "", exponent


def validate_measurement(measurement: Any, limits: dict[str, int]) -> None:
    if not isinstance(measurement, dict):
        raise Refusal("ODEYA_QUANTITY_SHAPE")
    if measurement.get("semantic_type") == "missing":
        exact_keys(measurement, {"semantic_type", "reason"}, "ODEYA_MISSINGNESS_SHAPE")
        if measurement["reason"] not in MISSING_REASONS:
            raise Refusal("ODEYA_MISSINGNESS_SHAPE")
        return
    required = {"value", "semantic_type", "unit", "precision"}
    exact_keys(measurement, required, "ODEYA_QUANTITY_SHAPE")
    if measurement["semantic_type"] != "measured_quantity":
        raise Refusal("ODEYA_QUANTITY_SHAPE")
    value = measurement["value"]
    if not isinstance(value, str):
        raise Refusal("ODEYA_QUANTITY_SHAPE")
    if len(value.encode("utf-8")) > limits["max_scientific_decimal_bytes"]:
        raise Refusal("ODEYA_DECIMAL_LEXICAL")
    if DECIMAL_RE.fullmatch(value) is None:
        raise Refusal("ODEYA_DECIMAL_LEXICAL")
    try:
        exact = Decimal(value)
    except InvalidOperation:
        raise Refusal("ODEYA_DECIMAL_LEXICAL") from None
    if value.startswith("-") and exact.is_zero():
        raise Refusal("ODEYA_DECIMAL_NEGATIVE_ZERO")
    unit = exact_keys(measurement["unit"], {"system", "code"}, "ODEYA_QUANTITY_SHAPE")
    if unit["system"] != "SI" or not isinstance(unit["code"], str) or not unit["code"]:
        raise Refusal("ODEYA_QUANTITY_SHAPE")
    precision = exact_keys(
        measurement["precision"], {"kind", "value"}, "ODEYA_QUANTITY_SHAPE"
    )
    if (
        precision["kind"] not in {"significant_digits", "decimal_places"}
        or isinstance(precision["value"], bool)
        or not isinstance(precision["value"], int)
        or not 0 <= precision["value"] <= 64
    ):
        raise Refusal("ODEYA_QUANTITY_SHAPE")
    integer, fraction, exponent = decimal_parts(value)
    significant = len((integer + fraction).lstrip("0"))
    if significant == 0:
        significant = 1
    decimal_places = max(0, len(fraction) - exponent)
    observed = significant if precision["kind"] == "significant_digits" else decimal_places
    if precision["value"] != observed:
        raise Refusal("ODEYA_PRECISION_MISMATCH")


def canonical_string_bytes(value: str) -> bytes:
    return rfc8785.dumps(value)


def admit_subject(profile: str, subject: Any, limits: dict[str, int]) -> Any:
    if profile == "plain":
        plain = exact_keys(subject, {"payload"}, "ODEYA_SCHEMA_ID_MISMATCH")
        if not isinstance(plain["payload"], str):
            raise Refusal("ODEYA_SCHEMA_ID_MISMATCH")
        return deepcopy(subject)
    if profile == "temporal_measurement":
        temporal = exact_keys(
            subject, {"observed_at", "measurement"}, "ODEYA_QUANTITY_SHAPE"
        )
        validate_timestamp(temporal["observed_at"])
        validate_measurement(temporal["measurement"], limits)
        return deepcopy(subject)
    if profile == "collections":
        collection = exact_keys(subject, {"sequence", "tags"}, "ODEYA_SCHEMA_ID_MISMATCH")
        if (
            not isinstance(collection["sequence"], list)
            or not isinstance(collection["tags"], list)
            or any(not isinstance(item, str) for item in collection["sequence"])
            or any(not isinstance(item, str) for item in collection["tags"])
        ):
            raise Refusal("ODEYA_SCHEMA_ID_MISMATCH")
        if len(set(collection["tags"])) != len(collection["tags"]):
            raise Refusal("ODEYA_SET_DUPLICATE")
        normalized = deepcopy(subject)
        normalized["tags"] = sorted(normalized["tags"], key=canonical_string_bytes)
        return normalized
    if profile == "reference_holder":
        holder = exact_keys(subject, {"reference"}, "ODEYA_REFERENCE_SHAPE")
        required = {"type", "id", "version", "digest", "media_type", "schema_id"}
        reference = exact_keys(holder["reference"], required, "ODEYA_REFERENCE_SHAPE")
        if any(not isinstance(reference[key], str) or not reference[key] for key in required):
            raise Refusal("ODEYA_REFERENCE_SHAPE")
        if (
            "://" in reference["id"]
            or SEMVER_RE.fullmatch(reference["version"]) is None
        ):
            raise Refusal("ODEYA_REFERENCE_MUTABLE")
        if DIGEST_RE.fullmatch(reference["digest"]) is None:
            raise Refusal("ODEYA_REFERENCE_DIGEST")
        if SCHEMA_ID_RE.fullmatch(reference["schema_id"]) is None:
            raise Refusal("ODEYA_REFERENCE_SHAPE")
        return deepcopy(subject)
    raise ValueError(f"unknown admission profile: {profile}")


def contains_self_reference(value: Any) -> bool:
    if isinstance(value, list):
        return any(contains_self_reference(item) for item in value)
    if isinstance(value, dict):
        return "canonical_digest" in value or any(
            contains_self_reference(item) for item in value.values()
        )
    return False


def load_schema_registry(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for entry in manifest["schema_registry"]:
        path = ROOT / entry["path"]
        raw = path.read_bytes()
        if sha256(raw) != entry["byte_sha256"]:
            raise RuntimeError(f"schema byte digest drift: {entry['path']}")
        schema = load_control(path)
        if schema.get("$id") != entry["schema_id"]:
            raise RuntimeError(f"schema ID mismatch: {entry['path']}")
        if entry["schema_id"] in registry:
            raise RuntimeError(f"duplicate schema ID: {entry['schema_id']}")
        registry[entry["schema_id"]] = entry
    return registry


def evaluate_vector(
    vector: dict[str, Any],
    manifest: dict[str, Any],
    upstream: dict[str, Any],
    registry: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    raw = input_bytes(vector, upstream)
    record: dict[str, Any] = {
        "id": vector["id"],
        "family": vector["family"],
        "input_length": len(raw),
        "input_sha256": sha256(raw),
    }
    try:
        subject = strict_parse(raw, manifest["limits"])
        if vector["mode"] == "jcs":
            canonical = rfc8785.dumps(subject)
        elif vector["mode"] == "identity":
            profile_id = vector.get("profile_id", manifest["profile_id"])
            if profile_id != PROFILE_ID:
                raise Refusal("ODEYA_PROFILE_UNKNOWN")
            schema_id = vector["schema_id"]
            if schema_id not in registry:
                raise Refusal("ODEYA_SCHEMA_UNREGISTERED")
            if contains_self_reference(subject):
                raise Refusal("ODEYA_SUBJECT_SELF_REFERENCE")
            admitted = admit_subject(
                registry[schema_id]["admission_profile"], subject, manifest["limits"]
            )
            envelope = {
                "profile_id": profile_id,
                "schema_id": schema_id,
                "subject": admitted,
            }
            canonical = rfc8785.dumps(envelope)
        else:
            raise ValueError(f"unknown vector mode: {vector['mode']}")
        record.update(
            {
                "outcome": "accepted",
                "canonical_hex": canonical.hex(),
                "canonical_length": len(canonical),
                "canonical_sha256": sha256(canonical),
            }
        )
    except Refusal as refusal:
        record.update({"outcome": "refused", "code": refusal.code})
    except Exception as exc:  # retained as a hard, non-admitting suite failure
        record.update({"outcome": "error", "error_type": type(exc).__name__})
    return record


def code_digest() -> str:
    module_dir = Path(inspect.getfile(rfc8785)).resolve().parent
    payload = b""
    for path in sorted(module_dir.glob("*.py")):
        payload += path.name.encode("utf-8") + b"\0" + path.read_bytes() + b"\0"
    return sha256(payload)


def main() -> int:
    manifest_raw = MANIFEST_PATH.read_bytes()
    source_lock_raw = SOURCE_LOCK_PATH.read_bytes()
    upstream_raw = UPSTREAM_PATH.read_bytes()
    manifest = load_control(MANIFEST_PATH)
    source_lock = load_control(SOURCE_LOCK_PATH)
    upstream_document = load_control(UPSTREAM_PATH)
    upstream = {item["name"]: item for item in upstream_document["vectors"]}
    registry = load_schema_registry(manifest)
    version = importlib.metadata.version("rfc8785")
    if version != "0.1.4":
        raise RuntimeError(f"rfc8785 version drift: {version}")
    if source_lock["profile_id"] != manifest["profile_id"]:
        raise RuntimeError("source lock/profile mismatch")
    cases = [
        evaluate_vector(vector, manifest, upstream, registry)
        for vector in manifest["vectors"]
    ]
    result = {
        "result_version": "0.1.0",
        "suite_id": manifest["suite_id"],
        "profile_id": manifest["profile_id"],
        "evidence_label": manifest["evidence_label"],
        "manifest_sha256": sha256(manifest_raw),
        "source_lock_sha256": sha256(source_lock_raw),
        "upstream_vectors_sha256": sha256(upstream_raw),
        "implementation": {
            "runner": "python",
            "runner_sha256": sha256(Path(__file__).read_bytes()),
            "runtime": platform.python_implementation(),
            "runtime_version": platform.python_version(),
            "package": "rfc8785",
            "package_version": version,
            "package_code_sha256": code_digest(),
            "environment": {
                "operating_system": platform.system().lower(),
                "operating_system_release": platform.release(),
                "architecture": platform.machine(),
                "byte_order": sys.byteorder,
            },
        },
        "limits": manifest["limits"],
        "cases": cases,
        "summary": {
            "total": len(cases),
            "accepted": sum(case["outcome"] == "accepted" for case in cases),
            "refused": sum(case["outcome"] == "refused" for case in cases),
            "errors": sum(case["outcome"] == "error" for case in cases),
        },
    }
    json.dump(result, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result["summary"]["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
