#!/usr/bin/env python3
"""Source-separated Python observer for PRQ-002C raw-number token typing.

The child receives only answer-free vectors and byte-bound normative inputs.
It never reads the private expectation manifest or a peer result.  Its output
is bounded architecture evidence over synthetic non-product frames.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import platform
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUITE_ID = "prq-002c-raw-number-typing.0001"
VECTOR_SET_ID = "prq-002c-raw-number-vectors.synthetic.0003"
CONTRACT_ID = "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
TYPE_FRAME_ID = "odeya.raw-number-integer-type-position.v1"
CONST_FRAME_ID = "odeya.raw-number-integer-const-position.v1"
IMPLEMENTATION_ID = "python-stdlib-raw-lexeme-hooks.0003"
EXPECTED_RUNTIME = "3.14.2"
MIN_INTEGER = -9007199254740991
MAX_INTEGER = 9007199254740991
MAX_NUMBER_TOKEN_BYTES = 128
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
OPAQUE_VECTOR_ID_RE = re.compile(r"^RN-[0-9]{4}$")
VECTOR_KEYS = {
    "sequence_index",
    "vector_id",
    "media_type",
    "decoded_raw_sha256",
    "decoded_byte_count",
    "input_base64",
}


class DuplicateObjectName(ValueError):
    pass


class InvalidJsonConstant(ValueError):
    pass


@dataclass(frozen=True)
class RawNumber:
    token_class: str
    lexeme: str


@dataclass(frozen=True)
class RawObject:
    pairs: tuple[tuple[str, Any], ...]


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "repository_path": path.as_posix(),
        "raw_sha256": sha256(raw),
        "byte_count": len(raw),
    }


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateObjectName(key)
        result[key] = value
    return result


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(
            InvalidJsonConstant(token)
        ),
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain one object")
    return value


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def contains_unpaired_surrogate(value: Any) -> bool:
    if isinstance(value, str):
        index = 0
        while index < len(value):
            code = ord(value[index])
            if 0xD800 <= code <= 0xDBFF:
                if index + 1 >= len(value):
                    return True
                following = ord(value[index + 1])
                if not 0xDC00 <= following <= 0xDFFF:
                    return True
                index += 2
                continue
            if 0xDC00 <= code <= 0xDFFF:
                return True
            index += 1
        return False
    if isinstance(value, RawObject):
        return any(
            contains_unpaired_surrogate(key)
            or contains_unpaired_surrogate(item)
            for key, item in value.pairs
        )
    if isinstance(value, list):
        return any(contains_unpaired_surrogate(item) for item in value)
    return False


def contains_duplicate_name(value: Any) -> bool:
    if isinstance(value, RawObject):
        seen: set[str] = set()
        for key, item in value.pairs:
            if key in seen or contains_duplicate_name(item):
                return True
            seen.add(key)
        return False
    if isinstance(value, list):
        return any(contains_duplicate_name(item) for item in value)
    return False


def materialize(value: Any) -> Any:
    if isinstance(value, RawObject):
        return {key: materialize(item) for key, item in value.pairs}
    if isinstance(value, list):
        return [materialize(item) for item in value]
    return value


def parse_frame(raw: bytes) -> tuple[Any | None, str | None]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return None, "ODEYA_PARSE_UTF8"
    if raw.startswith(b"\xef\xbb\xbf"):
        return None, "ODEYA_PARSE_BOM"

    def raw_integer(token: str) -> RawNumber:
        return RawNumber("integer_token", token)

    def raw_number(token: str) -> RawNumber:
        return RawNumber("number_token", token)

    try:
        value = json.loads(
            text,
            object_pairs_hook=lambda pairs: RawObject(tuple(pairs)),
            parse_int=raw_integer,
            parse_float=raw_number,
            parse_constant=lambda token: (_ for _ in ()).throw(
                InvalidJsonConstant(token)
            ),
        )
    except InvalidJsonConstant:
        return None, "ODEYA_PARSE_SYNTAX"
    except json.JSONDecodeError:
        return None, "ODEYA_PARSE_SYNTAX"
    if contains_duplicate_name(value):
        return None, "ODEYA_PARSE_DUPLICATE_KEY"
    if contains_unpaired_surrogate(value):
        return None, "ODEYA_PARSE_UNPAIRED_SURROGATE"
    return materialize(value), None


def significand_is_zero(lexeme: str) -> bool:
    body = lexeme[1:] if lexeme.startswith("-") else lexeme
    mantissa = re.split(r"[eE]", body, maxsplit=1)[0]
    digits = mantissa.replace(".", "")
    return bool(digits) and set(digits) == {"0"}


def staged_observation(
    sequence_index: int,
    vector_id: str,
    raw: bytes,
) -> dict[str, Any]:
    base = {
        "sequence_index": sequence_index,
        "vector_id": vector_id,
        "decoded_input_sha256": sha256(raw),
        "decoded_byte_count": len(raw),
        "lexical_disposition": "accepted",
        "position_rule": None,
        "raw_number_token": None,
        "raw_number_token_byte_count": None,
        "token_class": None,
        "binary64_conversion_class": None,
        "integer_position_disposition": None,
        "final_disposition": "refused",
        "final_code": None,
        "integer_decimal": None,
    }
    value, error = parse_frame(raw)
    if error is not None:
        base["lexical_disposition"] = "refused"
        base["final_code"] = error
        return base
    if (
        not isinstance(value, dict)
        or set(value) != {"frame_id", "integer_value"}
        or value.get("frame_id") not in {TYPE_FRAME_ID, CONST_FRAME_ID}
    ):
        base["final_code"] = "ODEYA_CONFORMANCE_FRAME_SHAPE"
        return base
    is_const = value["frame_id"] == CONST_FRAME_ID
    base["position_rule"] = (
        "integer_const_decimal_1" if is_const else "type_integer"
    )
    number = value["integer_value"]
    if not isinstance(number, RawNumber):
        base["integer_position_disposition"] = "refused"
        base["final_code"] = "ODEYA_SCHEMA_TYPE"
        return base
    token_class = number.token_class
    base["raw_number_token"] = number.lexeme
    base["raw_number_token_byte_count"] = len(number.lexeme.encode("ascii"))
    base["token_class"] = token_class
    if base["raw_number_token_byte_count"] > MAX_NUMBER_TOKEN_BYTES:
        base["final_code"] = "ODEYA_LIMIT_NUMBER_TOKEN"
        return base
    if number.lexeme.startswith("-") and significand_is_zero(number.lexeme):
        base["binary64_conversion_class"] = "negative_zero_exact_decimal"
        base["final_code"] = "ODEYA_NUMBER_NEGATIVE_ZERO"
        return base
    converted = float(number.lexeme)
    if not math.isfinite(converted):
        base["binary64_conversion_class"] = "nonfinite"
        base["final_code"] = "ODEYA_NUMBER_NONFINITE"
        return base
    if converted == 0.0 and not significand_is_zero(number.lexeme):
        base["binary64_conversion_class"] = (
            "underflow_to_negative_zero"
            if math.copysign(1.0, converted) < 0
            else "underflow_to_positive_zero"
        )
        base["final_code"] = "ODEYA_NUMBER_UNDERFLOW"
        return base
    base["binary64_conversion_class"] = (
        "positive_zero" if converted == 0.0 else "finite_nonzero"
    )
    if token_class == "number_token":
        base["integer_position_disposition"] = "refused"
        base["final_code"] = "ODEYA_NUMBER_INTEGER_TOKEN_REQUIRED"
        return base
    integer = int(number.lexeme, 10)
    if integer < MIN_INTEGER or integer > MAX_INTEGER:
        base["integer_position_disposition"] = "refused"
        base["final_code"] = "ODEYA_NUMBER_DOMAIN"
        return base
    if is_const and integer != 1:
        base["integer_position_disposition"] = "refused"
        base["final_code"] = "ODEYA_SCHEMA_CONST"
        return base
    base["integer_position_disposition"] = "accepted"
    base["final_disposition"] = "accepted"
    base["integer_decimal"] = number.lexeme
    return base


def validate_vectors(document: dict[str, Any]) -> list[dict[str, Any]]:
    if set(document) != {
        "schema_version",
        "artifact_class",
        "vector_set_id",
        "status",
        "answer_free",
        "opaque_vector_ids",
        "expected_outcomes_present",
        "decoded_input_bindings_present",
        "vector_count",
        "vectors",
    }:
        raise ValueError("vector root shape differs")
    if (
        document["schema_version"] != "0.3.0"
        or document["artifact_class"]
        != "prq_002c_answer_free_raw_number_vector_set"
        or document["vector_set_id"] != VECTOR_SET_ID
        or document["status"] != "synthetic_non_product_answer_free"
        or document["answer_free"] is not True
        or document["opaque_vector_ids"] is not True
        or document["expected_outcomes_present"] is not False
        or document["decoded_input_bindings_present"] is not True
    ):
        raise ValueError("vector identity or answer-free boundary differs")
    vectors = document["vectors"]
    if (
        not isinstance(vectors, list)
        or type(document["vector_count"]) is not int
        or len(vectors) != document["vector_count"]
    ):
        raise ValueError("vector count differs")
    seen: set[str] = set()
    for index, vector in enumerate(vectors):
        if not isinstance(vector, dict) or set(vector) != VECTOR_KEYS:
            raise ValueError(f"vector {index} shape differs")
        vector_id = vector["vector_id"]
        if (
            type(vector["sequence_index"]) is not int
            or vector["sequence_index"] != index
            or not isinstance(vector_id, str)
            or not OPAQUE_VECTOR_ID_RE.fullmatch(vector_id)
            or vector_id in seen
            or vector["media_type"] != "application/json"
            or not isinstance(vector["decoded_raw_sha256"], str)
            or type(vector["decoded_byte_count"]) is not int
            or not isinstance(vector["input_base64"], str)
        ):
            raise ValueError(f"vector {index} identity differs")
        seen.add(vector_id)
        raw = base64.b64decode(vector["input_base64"], validate=True)
        if (
            vector["decoded_raw_sha256"] != sha256(raw)
            or vector["decoded_byte_count"] != len(raw)
        ):
            raise ValueError(f"vector {index} decoded binding differs")
    return vectors


def verify_input_manifest(
    manifest: dict[str, Any],
    role_paths: dict[str, Path],
) -> None:
    if (
        set(manifest)
        != {
            "schema_version",
            "artifact_class",
            "manifest_id",
            "suite_id",
            "vector_set_id",
            "blocked_profile_predecessor_checkpoint",
            "answer_free_child_input",
            "binding_count",
            "bindings",
        }
        or manifest.get("schema_version") != "0.2.0"
        or manifest.get("artifact_class")
        != "prq_002c_raw_number_input_manifest"
        or manifest.get("manifest_id")
        != "prq-002c-raw-number-input-manifest.0003"
        or manifest.get("suite_id") != SUITE_ID
        or manifest.get("vector_set_id") != VECTOR_SET_ID
        or manifest.get("blocked_profile_predecessor_checkpoint")
        != {
            "commit": "a79d86b0a5e9581b3bacb57214cf180df3443566",
            "tree": "d44e9eb4751b97871aa9c995664782a5d031fb48",
        }
        or manifest.get("answer_free_child_input") is not True
        or manifest.get("binding_count") != len(role_paths)
    ):
        raise ValueError("input manifest identity differs")
    rows = manifest.get("bindings")
    if not isinstance(rows, list) or len(rows) != len(role_paths):
        raise ValueError("input manifest binding count differs")
    by_role = {
        row.get("role"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("role"), str)
    }
    if set(by_role) != set(role_paths):
        raise ValueError("input manifest roles differ")
    for role, path in role_paths.items():
        observed = binding(path)
        row = by_role[role]
        if (
            row.get("raw_sha256") != observed["raw_sha256"]
            or row.get("byte_count") != observed["byte_count"]
        ):
            raise ValueError(f"input binding differs for {role}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vectors", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--contract-schema", type=Path, required=True)
    parser.add_argument("--profile-core", type=Path, required=True)
    parser.add_argument("--profile-evidence", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--attestation-challenge", required=True)
    parser.add_argument("--emit-execution-attestation", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if platform.python_version() != EXPECTED_RUNTIME:
        raise SystemExit(
            f"runtime version differs: {platform.python_version()}"
        )
    if not (
        sys.flags.isolated == 1
        and sys.flags.no_site == 1
        and sys.dont_write_bytecode
    ):
        raise SystemExit("required isolated interpreter flags differ")
    if not CHALLENGE_RE.fullmatch(args.attestation_challenge):
        raise SystemExit("attestation challenge shape differs")
    manifest = strict_json(args.manifest)
    contract = strict_json(args.contract)
    source_manifest = strict_json(args.source_manifest)
    vectors_document = strict_json(args.vectors)
    if (
        contract.get("contract_id") != CONTRACT_ID
        or contract.get("status")
        != "proposed_architecture_only_non_product_contract"
    ):
        raise SystemExit("token contract identity differs")
    if (
        source_manifest.get("implementation_id") != IMPLEMENTATION_ID
        or source_manifest.get("peer_source_consumption_allowed") is not False
        or source_manifest.get("peer_result_consumption_allowed") is not False
        or source_manifest.get("private_expectation_consumption_allowed")
        is not False
    ):
        raise SystemExit("source manifest boundary differs")
    role_paths = {
        "vectors": args.vectors,
        "token_contract": args.contract,
        "token_contract_schema": args.contract_schema,
        "blocked_profile_core": args.profile_core,
        "blocked_profile_evidence": args.profile_evidence,
    }
    verify_input_manifest(manifest, role_paths)
    vectors = validate_vectors(vectors_document)
    results = [
        staged_observation(
            vector["sequence_index"],
            vector["vector_id"],
            base64.b64decode(vector["input_base64"], validate=True),
        )
        for vector in vectors
    ]
    projection = {
        "suite_id": SUITE_ID,
        "vector_set_id": VECTOR_SET_ID,
        "token_contract_id": CONTRACT_ID,
        "vector_count": len(results),
        "results": results,
        "claim_boundary": {
            "bounded_raw_number_observation_produced": True,
            "source_separated_agreement_observed": False,
            "generic_schema_path_evaluation_proved": False,
            "number_position_semantics_complete": False,
            "successor_profile_conformance_complete": False,
            "product_identity_computed": False,
            "profile_issued": False,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "publication_authorized": False,
        },
    }
    projection_binding = sha256(compact_json(projection))
    source_binding = binding(args.source_manifest)
    implementation_causal_binding = sha256(
        compact_json(
            {
                "implementation_id": IMPLEMENTATION_ID,
                "source_manifest_raw_sha256": source_binding["raw_sha256"],
                "projection_raw_sha256": projection_binding,
            }
        )
    )
    result = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002c_raw_number_observation_result",
        "implementation": {
            "role": "python",
            "implementation_id": IMPLEMENTATION_ID,
            "runtime": "CPython",
            "runtime_version": platform.python_version(),
            "parser_strategy": (
                "stdlib_json_raw_pairs_deferred_restriction_classification"
            ),
            "source_manifest_binding": source_binding,
        },
        "input_manifest_binding": binding(args.manifest),
        "implementation_causal_binding": implementation_causal_binding,
        "projection": projection,
    }
    result_line = compact_json(result)
    if not args.emit_execution_attestation:
        sys.stdout.buffer.write(result_line + b"\n")
        return 0
    executable = Path(sys.executable).resolve(strict=True)
    runner = Path(__file__).resolve(strict=True)
    attestation = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002c_child_execution_attestation",
        "suite_id": SUITE_ID,
        "implementation_id": IMPLEMENTATION_ID,
        "challenge": args.attestation_challenge,
        "argv": [
            sys.executable,
            "-I",
            "-S",
            "-B",
            runner.as_posix(),
            *sys.argv[1:],
        ],
        "runtime": {
            "family": "CPython",
            "version": platform.python_version(),
            "executable": binding(executable),
        },
        "runner_binding": binding(runner),
        "source_manifest_binding": binding(args.source_manifest),
        "input_manifest_binding": binding(args.manifest),
        "vector_set_binding": binding(args.vectors),
        "token_contract_binding": binding(args.contract),
        "result_line_binding": {
            "raw_sha256": sha256(result_line),
            "byte_count": len(result_line),
        },
        "network_access_requested": False,
        "private_expectations_received": False,
        "peer_source_received": False,
        "peer_result_received": False,
        "product_identity_computed": False,
    }
    sys.stdout.buffer.write(compact_json(attestation) + b"\n")
    sys.stdout.buffer.write(result_line + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
