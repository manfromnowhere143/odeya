#!/usr/bin/env python3
"""Deterministically build answer-free PRQ-002D virtual-file vectors.

This is an authoring tool, not an evaluator. It emits opaque vector IDs and
input bytes only. Expected outcomes remain in the private comparator manifest
and are never passed to either child observer.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
SUITE = ROOT / "tests/schema-registry-prehash-replay"
SAFE_BUNDLE_PATH = SUITE / "fixtures/safe-bundle.json"
RESOURCE_1_PATH = SUITE / "fixtures/resources/resource-001.schema.json"
RESOURCE_2_PATH = SUITE / "fixtures/resources/resource-002.schema.json"
PROBE_1_PATH = SUITE / "fixtures/probes/probe-001.valid.json"
PROBE_2_PATH = SUITE / "fixtures/probes/probe-002.valid.json"
DEFAULT_OUTPUT = SUITE / "vectors.json"

BASE_PATHS = {
    "bundle": SAFE_BUNDLE_PATH,
    "resource-001": RESOURCE_1_PATH,
    "resource-002": RESOURCE_2_PATH,
    "probe-001": PROBE_1_PATH,
    "probe-002": PROBE_2_PATH,
}


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def load_object(data: bytes) -> dict[str, Any]:
    value = json.loads(data.decode("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError("expected one JSON object")
    return value


def encode_object(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def set_resource(
    files: dict[str, bytes],
    blob_id: str,
    value: dict[str, Any],
    *,
    synchronize_member: bool = True,
    synchronize_resolver: bool = True,
) -> None:
    data = encode_object(value)
    files[blob_id] = data
    bundle = load_object(files["bundle"])
    resource_index = 0 if blob_id == "resource-001" else 1
    if synchronize_member:
        bundle["members"][resource_index]["resource_raw_sha256"] = digest(data)
        bundle["members"][resource_index]["resource_byte_count_decimal"] = str(
            len(data)
        )
    if synchronize_resolver:
        bundle["resolver_catalog"][resource_index]["resource_raw_sha256"] = digest(
            data
        )
        bundle["resolver_catalog"][resource_index][
            "resource_byte_count_decimal"
        ] = str(len(data))
    files["bundle"] = encode_object(bundle)


def set_resource_bytes(
    files: dict[str, bytes],
    blob_id: str,
    data: bytes,
) -> None:
    files[blob_id] = data
    bundle = load_object(files["bundle"])
    resource_index = 0 if blob_id == "resource-001" else 1
    bundle["members"][resource_index]["resource_raw_sha256"] = digest(data)
    bundle["members"][resource_index]["resource_byte_count_decimal"] = str(
        len(data)
    )
    bundle["resolver_catalog"][resource_index]["resource_raw_sha256"] = digest(
        data
    )
    bundle["resolver_catalog"][resource_index][
        "resource_byte_count_decimal"
    ] = str(len(data))
    files["bundle"] = encode_object(bundle)


def set_probe(
    files: dict[str, bytes],
    blob_id: str,
    value: dict[str, Any],
) -> None:
    files[blob_id] = encode_object(value)


def set_probe_bytes(
    files: dict[str, bytes],
    blob_id: str,
    data: bytes,
) -> None:
    files[blob_id] = data


def mutate_bundle(
    files: dict[str, bytes],
    mutation: Callable[[dict[str, Any]], None],
) -> None:
    bundle = load_object(files["bundle"])
    mutation(bundle)
    files["bundle"] = encode_object(bundle)


def replace_count_token(files: dict[str, bytes], replacement: bytes) -> None:
    before = b'"declared_member_count": 2,'
    after = b'"declared_member_count": ' + replacement + b","
    if files["bundle"].count(before) != 1:
        raise ValueError("safe bundle count token is not unique")
    files["bundle"] = files["bundle"].replace(before, after, 1)


def set_wrong_count_and_authority_claim(files: dict[str, bytes]) -> None:
    def mutation(bundle: dict[str, Any]) -> None:
        bundle["declared_member_count"] = 3
        bundle["authority_boundary"]["gate_a_complete"] = True

    mutate_bundle(files, mutation)


def set_invalid_schema_with_alternative_bytes(files: dict[str, bytes]) -> None:
    resource = load_object(files["resource-001"])
    resource["type"] = "not-a-json-schema-type"
    set_resource(files, "resource-001", resource)


def set_resource_number_overflow(files: dict[str, bytes]) -> None:
    before = b"\n}\n"
    after = b',\n  "examples": [1e400]\n}\n'
    data = files["resource-001"]
    if data.count(before) != 1:
        raise ValueError("resource closing object is not unique")
    set_resource_bytes(files, "resource-001", data.replace(before, after, 1))


def set_duplicate_key_then_truncated_syntax(files: dict[str, bytes]) -> None:
    data = files["bundle"].replace(
        b'  "scope":',
        b'  "schema_version": "0.1.0",\n  "scope":',
        1,
    )
    files["bundle"] = data[:-2]


def set_unpaired_surrogate_then_truncated_syntax(
    files: dict[str, bytes],
) -> None:
    mutate_bundle(files, lambda bundle: bundle.__setitem__("scope", "\ud800"))
    files["bundle"] = files["bundle"][:-2]


def set_duplicate_key_and_unpaired_surrogate(files: dict[str, bytes]) -> None:
    mutate_bundle(files, lambda bundle: bundle.__setitem__("scope", "\ud800"))
    files["bundle"] = files["bundle"].replace(
        b'  "scope":',
        b'  "schema_version": "0.1.0",\n  "scope":',
        1,
    )


def set_nested_duplicate_then_truncated_outer(files: dict[str, bytes]) -> None:
    before = b'    "profile_issued": false,'
    after = (
        b'    "profile_issued": false,\n'
        b'    "profile_issued": false,'
    )
    if files["bundle"].count(before) != 1:
        raise ValueError("profile_issued key is not unique")
    files["bundle"] = files["bundle"].replace(before, after, 1)[:-2]


def set_escaped_count_key_and_wrong_count(files: dict[str, bytes]) -> None:
    replace_count_token(files, b"3")
    before = b'"declared_member_count"'
    after = b'"\\u0064eclared_member_count"'
    if files["bundle"].count(before) != 1:
        raise ValueError("declared member count key is not unique")
    files["bundle"] = files["bundle"].replace(before, after, 1)


def set_reference_target(files: dict[str, bytes], target: str) -> None:
    resource = load_object(files["resource-001"])
    resource["properties"]["peer"]["$ref"] = target
    set_resource(files, "resource-001", resource)


def vector_file(blob_id: str, data: bytes) -> dict[str, str]:
    return {
        "blob_id": blob_id,
        "media_type": "application/json",
        "raw_sha256": digest(data),
        "byte_count_decimal": str(len(data)),
        "content_base64": base64.b64encode(data).decode("ascii"),
    }


def build_vector(
    index: int,
    mutation: Callable[[dict[str, bytes]], None] | None = None,
) -> dict[str, Any]:
    files = {key: path.read_bytes() for key, path in BASE_PATHS.items()}
    if mutation is not None:
        mutation(files)
    return {
        "sequence_index_decimal": str(index),
        "vector_id": f"PH-{index + 1:04d}",
        "files": [
            vector_file(blob_id, data)
            for blob_id, data in sorted(files.items())
        ],
    }


def build_noncanonical_base64_vector(index: int) -> dict[str, Any]:
    vector = build_vector(index)
    frame = next(
        row for row in vector["files"] if row["blob_id"] == "probe-001"
    )
    encoded = frame["content_base64"]
    if not encoded.endswith("=="):
        raise ValueError("probe-001 does not have the expected Base64 padding")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    position = len(encoded) - 3
    value = alphabet.index(encoded[position])
    if value % 16 != 0:
        raise ValueError("probe-001 Base64 is not canonical before mutation")
    replacement = alphabet[value + 1]
    mutated = encoded[:position] + replacement + encoded[position + 1 :]
    if (
        base64.b64decode(mutated, validate=True)
        != base64.b64decode(encoded, validate=True)
        or base64.b64encode(
            base64.b64decode(mutated, validate=True)
        ).decode("ascii")
        == mutated
    ):
        raise ValueError("failed to construct noncanonical Base64")
    frame["content_base64"] = mutated
    return vector


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mutations: list[Callable[[dict[str, bytes]], None] | None] = [
        None,
        lambda files: replace_count_token(files, b"2.0"),
        lambda files: replace_count_token(files, b"2e0"),
        lambda files: replace_count_token(files, b"-0"),
        lambda files: replace_count_token(files, b"3"),
        lambda files: mutate_bundle(files, lambda b: b["members"].pop()),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][1].__setitem__(
                "member_key", b["members"][0]["member_key"]
            ),
        ),
        lambda files: mutate_bundle(files, lambda b: b["members"].reverse()),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "member_key",
                "urn:odeya:architecture-test:prq-002d:résource-a:0.1.0@0.1.0",
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "member_key",
                "URN:odeya:architecture-test:prq-002d:resource-a:0.1.0@0.1.0",
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "member_key",
                "urn:odeya:architecture-test:prq-002d:resource-x:0.1.0@0.1.0",
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "semantic_version", "0.2.0"
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "schema_id",
                "urn:odeya:architecture-test:prq-002d:resource-x:0.1.0",
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "resource_byte_count_decimal", "455"
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][0].__setitem__(
                "resource_raw_sha256", "sha256:" + "0" * 64
            ),
        ),
        lambda files: mutate_bundle(
            files, lambda b: b["resolver_catalog"].pop()
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["resolver_catalog"].append(
                copy.deepcopy(b["resolver_catalog"][0])
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["resolver_catalog"][1].__setitem__(
                "request_uri", b["resolver_catalog"][0]["request_uri"]
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["resolver_catalog"][0].__setitem__(
                "resource_blob_id", "resource-002"
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["resolver_catalog"][0].__setitem__(
                "resource_raw_sha256", "sha256:" + "f" * 64
            ),
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "$schema": "https://json-schema.org/draft/2019-09/schema",
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "type": "not-a-json-schema-type",
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "properties": {
                    **load_object(files["resource-001"])["properties"],
                    "nested": {
                        "$id": "urn:odeya:architecture-test:prq-002d:nested:0.1.0"
                    },
                },
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "properties": {
                    **load_object(files["resource-001"])["properties"],
                    "peer": {"$ref": "resource.a.json"},
                },
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "properties": {
                    **load_object(files["resource-001"])["properties"],
                    "peer": {"$ref": "https://example.invalid/resource.json"},
                },
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "properties": {
                    **load_object(files["resource-001"])["properties"],
                    "peer": {
                        "$dynamicRef": (
                            "urn:odeya:architecture-test:prq-002d:"
                            "resource.a:0.1.0"
                        )
                    },
                },
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "$id": "urn:odeya:architecture-test:prq-002d:resource-x:0.1.0",
            },
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "properties": {
                    **load_object(files["resource-001"])["properties"],
                    "schema_version": {"const": "0.2.0"},
                },
            },
        ),
        lambda files: set_resource_bytes(
            files,
            "resource-001",
            files["resource-001"].replace(b'{\n  "$schema"', b'{"$schema"', 1),
        ),
        lambda files: set_resource(
            files,
            "resource-001",
            {
                **load_object(files["resource-001"]),
                "title": "Coherent alternative bytes with the same resource id",
            },
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["replay_requests"][0].__setitem__(
                "request_uri",
                b["replay_requests"][0]["request_uri"] + "#alias",
            ),
        ),
        lambda files: mutate_bundle(files, lambda b: b["replay_requests"].pop()),
        lambda files: set_probe(
            files,
            "probe-001",
            {"schema_version": "0.1.0", "peer": {"schema_version": "0.1.0"}},
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["authority_boundary"].__setitem__(
                "gate_a_complete", True
            ),
        ),
        lambda files: mutate_bundle(
            files, lambda b: b.__setitem__("member_digest", "sha256:" + "0" * 64)
        ),
        lambda files: files.__setitem__(
            "bundle",
            files["bundle"].replace(
                b'  "scope":',
                b'  "schema_version": "0.1.0",\n  "scope":',
                1,
            ),
        ),
        lambda files: files.__setitem__(
            "bundle", files["bundle"][:-2] + b"\xff}\n"
        ),
        lambda files: files.__setitem__("bundle", b"\xef\xbb\xbf" + files["bundle"]),
        lambda files: files.__setitem__("bundle", files["bundle"][:-2]),
        lambda files: mutate_bundle(
            files, lambda b: b.__setitem__("scope", "\ud800")
        ),
        lambda files: files.pop("resource-002"),
        lambda files: files.__setitem__(
            "resource-003", files["resource-002"]
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["replay_requests"][0].__setitem__(
                "probe_blob_id", "probe-002"
            ),
        ),
        lambda files: set_probe_bytes(
            files,
            "probe-001",
            files["probe-001"].replace(
                b'{\n  "schema_version"',
                b'{"schema_version"',
                1,
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["resolver_catalog"][0].__setitem__(
                "request_uri",
                "URN:odeya:architecture-test:prq-002d:resource-a:0.1.0",
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["members"][1].update(
                {
                    "member_key": b["members"][0]["member_key"],
                    "resource_raw_sha256": "sha256:" + "1" * 64,
                }
            ),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b.__setitem__("declared_member_count", True),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b.__setitem__("declared_member_count", None),
        ),
        lambda files: mutate_bundle(
            files,
            lambda b: b["authority_boundary"].__setitem__(
                "product_digest_computed", True
            ),
        ),
        set_wrong_count_and_authority_claim,
        lambda files: files.pop("bundle"),
        lambda files: set_resource_bytes(
            files,
            "resource-001",
            files["resource-001"][:-2] + b"\xff}\n",
        ),
        lambda files: mutate_bundle(
            files, lambda b: b["resolver_catalog"].reverse()
        ),
        lambda files: mutate_bundle(
            files, lambda b: b["replay_requests"].reverse()
        ),
        set_invalid_schema_with_alternative_bytes,
        lambda files: mutate_bundle(
            files,
            lambda b: b["authority_boundary"].__setitem__(
                "gate_a_complete", 0
            ),
        ),
        set_resource_number_overflow,
        lambda files: files.__setitem__(
            "bundle",
            b"\xef\xbb\xbf" + files["bundle"][:-2] + b"\xff}\n",
        ),
        set_duplicate_key_then_truncated_syntax,
        set_unpaired_surrogate_then_truncated_syntax,
        set_duplicate_key_and_unpaired_surrogate,
        set_escaped_count_key_and_wrong_count,
        lambda files: mutate_bundle(
            files,
            lambda b: b["authority_boundary"].__setitem__(
                "declared_member_count", 2
            ),
        ),
        lambda files: set_reference_target(
            files,
            "urn:odeya:architecture-test:prq-002d:missing:0.1.0",
        ),
        lambda files: set_reference_target(
            files,
            (
                "urn:odeya:architecture-test:prq-002d:"
                "resource.a:0.1.0#fragment"
            ),
        ),
        set_nested_duplicate_then_truncated_outer,
        lambda files: replace_count_token(files, b"9007199254740992"),
    ]

    vectors = [build_vector(index, mutation) for index, mutation in enumerate(mutations)]
    vectors.append(build_noncanonical_base64_vector(len(vectors)))
    document = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002d_schema_registry_prehash_vector_set",
        "vector_set_id": "prq-002d-schema-registry-prehash.synthetic.0001",
        "vector_count_decimal": str(len(vectors)),
        "vectors": vectors,
    }
    args.output.write_bytes(encode_object(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
