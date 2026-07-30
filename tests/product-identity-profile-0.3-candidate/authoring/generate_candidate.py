#!/usr/bin/env python3
"""Deterministically author the PRQ-002E odeya-jcs-0.3 product schemas.

This construction tool deliberately has no product-identity computation path.  It
reissues nine frozen 0.2 product schemas under new resource identities, binds the
0.3 profile and disjoint digest domains, and derives structural-nonidentity
fixtures.  Frozen inputs are checked by raw SHA-256 and byte count before parse.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.3"
PROFILE_VERSION = "0.3.0"
PROFILE_CORE_SCHEMA_ID = "urn:odeya:schema:canonicalization-profile-core:0.7.0"
RAW_NUMBER_CONTRACT_ID = (
    "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
)
RAW_NUMBER_CONTRACT_PATH = (
    "architecture/canonicalization-raw-number-token-contract-v1-candidate.json"
)
RAW_NUMBER_CONTRACT_SHA256 = (
    "e2fcce22dc7570652f12e5dfb97860dcbe9b4af37bf56d810a5e499c3eddf6fc"
)
RAW_NUMBER_CONTRACT_BYTE_COUNT = 7363
SAFE_INTEGER_MINIMUM = -9007199254740991
SAFE_INTEGER_MAXIMUM = 9007199254740991
INTEGER_TOKEN_PATTERN = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")


SCHEMA_SPECS = (
    {
        "binding_id": "schema_resource_record",
        "source": "schemas/schema-resource-record.schema.json",
        "source_id": "urn:odeya:schema:schema-resource-record:0.1.0",
        "source_sha256": "ea42d3ab19502cd0a4543ff597296c6c2d2b7aaf04427f4a44d8c874e76cbec1",
        "source_byte_count": 8509,
        "output": "schemas/schema-resource-record-v0-2.schema.json",
        "output_id": "urn:odeya:schema:schema-resource-record:0.2.0",
        "version": "0.2.0",
        "source_domain": "odeya-schema-resource-record-v1",
        "output_domain": "odeya-schema-resource-record-v2",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-schema-resource-record.structural-nonidentity.json",
        "fixture_source_sha256": "eacf68387cbc81f86b75e33873985cda38b3a7f067f9719e74db85779e662483",
        "fixture_source_byte_count": 2009,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-schema-resource-record-v0-2.structural-nonidentity.json",
    },
    {
        "binding_id": "aggregate_state_subject_record",
        "source": "schemas/aggregate-state-subject-record.schema.json",
        "source_id": "urn:odeya:schema:aggregate-state-subject-record:0.1.0",
        "source_sha256": "4778cc423dae5bcc9fc5aa2b7a4239576078ade56baedd47d83c7024cde377ef",
        "source_byte_count": 16626,
        "output": "schemas/aggregate-state-subject-record-v0-2.schema.json",
        "output_id": "urn:odeya:schema:aggregate-state-subject-record:0.2.0",
        "version": "0.2.0",
        "source_domain": "odeya-aggregate-state-subject-record-v1",
        "output_domain": "odeya-aggregate-state-subject-record-v2",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-aggregate-state-subject-record.structural-nonidentity.json",
        "fixture_source_sha256": "e82d1c2f5067148006f94fbe2391d1021fa73c776ccfa81e8fab47ac60b5379f",
        "fixture_source_byte_count": 4967,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-aggregate-state-subject-record-v0-2.structural-nonidentity.json",
    },
    {
        "binding_id": "reducer_contract_record",
        "source": "schemas/reducer-contract-record.schema.json",
        "source_id": "urn:odeya:schema:reducer-contract-record:0.1.0",
        "source_sha256": "a7051b82ac0e596eaf73b1c881628dec42bfd52478c40fe43e1f6f22b2f10eac",
        "source_byte_count": 18413,
        "output": "schemas/reducer-contract-record-v0-2.schema.json",
        "output_id": "urn:odeya:schema:reducer-contract-record:0.2.0",
        "version": "0.2.0",
        "source_domain": "odeya-reducer-contract-record-v1",
        "output_domain": "odeya-reducer-contract-record-v2",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-reducer-contract-record.structural-nonidentity.json",
        "fixture_source_sha256": "399bdbe34b57805645d7cf6544f86cfa4f0b73734fde3ed2d835919477886036",
        "fixture_source_byte_count": 7102,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-reducer-contract-record-v0-2.structural-nonidentity.json",
    },
    {
        "binding_id": "event_contract_record",
        "source": "schemas/event-contract-record.schema.json",
        "source_id": "urn:odeya:schema:event-contract-record:0.1.0",
        "source_sha256": "ef01757b7d1e799c6936d4365f26ce80cb9f969098e83e2e910eef5fae2d81fc",
        "source_byte_count": 13026,
        "output": "schemas/event-contract-record-v0-2.schema.json",
        "output_id": "urn:odeya:schema:event-contract-record:0.2.0",
        "version": "0.2.0",
        "source_domain": "odeya-event-contract-record-v1",
        "output_domain": "odeya-event-contract-record-v2",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-event-contract-record.structural-nonidentity.json",
        "fixture_source_sha256": "c3abab1c2943c5c08d046b8c26567a6ff527c1072804335b777e1ad603797777",
        "fixture_source_byte_count": 3461,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-event-contract-record-v0-2.structural-nonidentity.json",
    },
    {
        "binding_id": "ordered_member_map_commitment",
        "source": "schemas/ordered-member-map-commitment.schema.json",
        "source_id": "urn:odeya:schema:ordered-member-map-commitment:0.1.0",
        "source_sha256": "aea26065be3bcc91c29ff5a75adb8532bef142067a36b7ce2e895db93e2d5910",
        "source_byte_count": 9801,
        "output": "schemas/ordered-member-map-commitment-v0-2.schema.json",
        "output_id": "urn:odeya:schema:ordered-member-map-commitment:0.2.0",
        "version": "0.2.0",
        "source_domain": "odeya-ordered-member-map-commitment-v1",
        "output_domain": "odeya-ordered-member-map-commitment-v2",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-ordered-member-map-commitment.structural-nonidentity.json",
        "fixture_source_sha256": "e0dbc8e6e2350fcf4e0f533c84037ff45c4c7702d695e2d08849b55d002cb400",
        "fixture_source_byte_count": 1720,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-ordered-member-map-commitment-v0-2.structural-nonidentity.json",
    },
    {
        "binding_id": "schema_registry_v0_9",
        "source": "schemas/schema-registry-v0-8.schema.json",
        "source_id": "urn:odeya:schema:schema-registry:0.8.0",
        "source_sha256": "0e14e8bc67df473cde3febac0a48d59d36173c070501dbe9acd7225ea9ab5ed3",
        "source_byte_count": 6792,
        "output": "schemas/schema-registry-v0-9.schema.json",
        "output_id": "urn:odeya:schema:schema-registry:0.9.0",
        "version": "0.9.0",
        "source_domain": "odeya-schema-registry-v2",
        "output_domain": "odeya-schema-registry-v3",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-schema-registry-v0-8.structural-nonidentity.json",
        "fixture_source_sha256": "d0d6edd3f8dcf2c69698476ab2d384e1f5cd9fdbc95ae8eab5d70f9008d65dea",
        "fixture_source_byte_count": 3323,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-schema-registry-v0-9.structural-nonidentity.json",
    },
    {
        "binding_id": "aggregate_state_subject_registry_v0_8",
        "source": "schemas/aggregate-state-subject-registry-v0-7.schema.json",
        "source_id": "urn:odeya:schema:aggregate-state-subject-registry:0.7.0",
        "source_sha256": "ad4c92f810e813bde1bfbb34913fb1bae0c4910a7ddcbb7b802b99b95fce2f58",
        "source_byte_count": 7020,
        "output": "schemas/aggregate-state-subject-registry-v0-8.schema.json",
        "output_id": "urn:odeya:schema:aggregate-state-subject-registry:0.8.0",
        "version": "0.8.0",
        "source_domain": "odeya-aggregate-state-subject-registry-v2",
        "output_domain": "odeya-aggregate-state-subject-registry-v3",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-aggregate-state-subject-registry-v0-7.structural-nonidentity.json",
        "fixture_source_sha256": "8ea4944bff7e7ef6f217be09fc2f57691628602cf707ab68dc846ff6c32bb414",
        "fixture_source_byte_count": 3373,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-aggregate-state-subject-registry-v0-8.structural-nonidentity.json",
    },
    {
        "binding_id": "reducer_registry_v0_8",
        "source": "schemas/reducer-registry-v0-7.schema.json",
        "source_id": "urn:odeya:schema:reducer-registry:0.7.0",
        "source_sha256": "f8731454e56e80eaeacef07a1bab617a141b42da3a4b8cfbeb90daa9dd3c631b",
        "source_byte_count": 6805,
        "output": "schemas/reducer-registry-v0-8.schema.json",
        "output_id": "urn:odeya:schema:reducer-registry:0.8.0",
        "version": "0.8.0",
        "source_domain": "odeya-reducer-registry-v2",
        "output_domain": "odeya-reducer-registry-v3",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-reducer-registry-v0-7.structural-nonidentity.json",
        "fixture_source_sha256": "40b5874f81ff694986d8f4169894a4e69342eb4539c6a0d42c9e7627c42c0dec",
        "fixture_source_byte_count": 3286,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-reducer-registry-v0-8.structural-nonidentity.json",
    },
    {
        "binding_id": "event_contract_registry_v0_8",
        "source": "schemas/event-contract-registry-v0-7.schema.json",
        "source_id": "urn:odeya:schema:event-contract-registry:0.7.0",
        "source_sha256": "276d4dccec99613953d23c1a65c88c4cdc3e194eb309452cf7999ecaa8933a68",
        "source_byte_count": 6895,
        "output": "schemas/event-contract-registry-v0-8.schema.json",
        "output_id": "urn:odeya:schema:event-contract-registry:0.8.0",
        "version": "0.8.0",
        "source_domain": "odeya-event-contract-registry-v2",
        "output_domain": "odeya-event-contract-registry-v3",
        "fixture_source": "tests/architecture-schema/fixtures/prq-002b-structural-nonidentity/prq-002b-event-contract-registry-v0-7.structural-nonidentity.json",
        "fixture_source_sha256": "51026c9d5a52bd0b64f7d33700b1c17e415618368d0b8c216d5cfa5663e8a480",
        "fixture_source_byte_count": 3340,
        "fixture_output": "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity/prq-002e-event-contract-registry-v0-8.structural-nonidentity.json",
    },
)

CONTROL_SCHEMA_SPECS = (
    {
        "binding_id": "canonicalization_profile_core_v0_7",
        "source": "schemas/canonicalization-profile-core-v0-6.schema.json",
        "source_id": "urn:odeya:schema:canonicalization-profile-core:0.6.0",
        "source_sha256": "6998a185d2615ecf68f9fe97c2cd91e7abbc3ea7e6bcd66c1d9cf1507cf7e6e7",
        "source_byte_count": 67161,
        "output": "schemas/canonicalization-profile-core-v0-7.schema.json",
        "output_id": PROFILE_CORE_SCHEMA_ID,
        "version": "0.7.0",
        "resource_role": "profile_core_schema",
    },
    {
        "binding_id": "canonicalization_profile_candidate_evidence_v0_7",
        "source": "schemas/canonicalization-profile-candidate-evidence-v0-6.schema.json",
        "source_id": "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.6.0",
        "source_sha256": "db626f85e7d3ddf408e640f6d349c95ad80bb2c06c399db9aa6127dafc33bcf1",
        "source_byte_count": 51174,
        "output": "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
        "output_id": "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0",
        "version": "0.7.0",
        "resource_role": "profile_evidence_schema",
    },
    {
        "binding_id": "canonicalization_profile_migration_v0_2",
        "source": "schemas/canonicalization-profile-migration.schema.json",
        "source_id": "urn:odeya:schema:canonicalization-profile-migration:0.1.0",
        "source_sha256": "8505024453dec8dc594a82ecb1ed7398e5bbd84b690ed5aec877f3c9669bfe08",
        "source_byte_count": 74806,
        "output": "schemas/canonicalization-profile-migration-v0-2.schema.json",
        "output_id": "urn:odeya:schema:canonicalization-profile-migration:0.2.0",
        "version": "0.2.0",
        "resource_role": "profile_migration_schema",
    },
)

ALL_SCHEMA_SPECS = SCHEMA_SPECS + CONTROL_SCHEMA_SPECS
CORE_RECORD_PATH = "architecture/canonicalization-profile-core-0.3-candidate.json"
EVIDENCE_RECORD_PATH = (
    "architecture/canonicalization-profile-0.3-candidate-evidence.json"
)
MIGRATION_RECORD_PATH = (
    "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json"
)
BASELINE_COMMIT = "617209ba480b854a00c6a15cd99ac1d5a18e90ad"
BASELINE_TREE = "67c38b895276bf2c804fe192339ce90a8c75ea97"

FROZEN_CORE = {
    "path": "architecture/canonicalization-profile-core-0.2-candidate.json",
    "raw_digest": "sha256:deab395ca2ce5524ceb65bdd307a43b4dd4613b78c92b16d13e1a69cac683941",
    "byte_count": 25422,
}
FROZEN_EVIDENCE = {
    "path": "architecture/canonicalization-profile-0.2-candidate-evidence.json",
    "raw_digest": "sha256:9995e1e7621abe480db2659f441006cb2ea351072b96a6a4f667cba811892b14",
    "byte_count": 12043,
}
FROZEN_MIGRATION = {
    "path": "architecture/canonicalization-profile-0.1-to-0.2-migration-candidate.json",
    "raw_digest": "sha256:03e9aad2e40c328f80f2692f40c3d5c7ce23caeeddeb1749df0e1fe064302ed4",
    "byte_count": 25013,
}
RAW_NUMBER_CONTRACT_SCHEMA = {
    "path": "architecture/canonicalization-raw-number-token-contract.schema.json",
    "schema_id": "urn:odeya:schema:canonicalization-raw-number-token-contract:0.1.0",
    "raw_digest": "sha256:5d9bd071353a84181afb8d29165c5f6abf3b00e6dab4b9ec69f0308288e123d3",
    "byte_count": 14673,
}


class _DynamicDigest:
    pass


class _DynamicInteger:
    pass


DYNAMIC_DIGEST = _DynamicDigest()
DYNAMIC_INTEGER = _DynamicInteger()


def raw_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_repository_path(relative_path: str) -> str:
    candidate = Path(relative_path)
    if (
        not relative_path
        or candidate.is_absolute()
        or "\x00" in relative_path
        or "\\" in relative_path
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or candidate.as_posix() != relative_path
    ):
        raise ValueError(f"unsafe repository path: {relative_path!r}")
    return relative_path


def strict_regular_file_bytes(root: Path, relative_path: str) -> bytes:
    """Read one contained regular file without following symlinks."""

    relative_path = normalize_repository_path(relative_path)
    root_stat = root.lstat()
    if root.is_symlink() or not stat.S_ISDIR(root_stat.st_mode):
        raise ValueError("artifact root is not a non-symlink directory")
    root_resolved = root.resolve(strict=True)
    path = root.joinpath(*Path(relative_path).parts)
    current = root
    for part in Path(relative_path).parts[:-1]:
        current = current / part
        current_stat = current.lstat()
        if current.is_symlink() or not stat.S_ISDIR(current_stat.st_mode):
            raise ValueError(
                f"artifact parent is not a non-symlink directory: {relative_path}"
            )
    lexical_stat = path.lstat()
    if path.is_symlink() or not stat.S_ISREG(lexical_stat.st_mode):
        raise ValueError(
            f"artifact is not a non-symlink regular file: {relative_path}"
        )
    try:
        path.resolve(strict=True).relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(
            f"artifact resolves outside its root: {relative_path}"
        ) from exc
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        opened_stat = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened_stat.st_mode)
            or (opened_stat.st_dev, opened_stat.st_ino)
            != (lexical_stat.st_dev, lexical_stat.st_ino)
        ):
            raise ValueError(f"artifact changed before open: {relative_path}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        final_stat = os.fstat(descriptor)
        if (
            final_stat.st_size != opened_stat.st_size
            or final_stat.st_mtime_ns != opened_stat.st_mtime_ns
        ):
            raise ValueError(f"artifact changed during read: {relative_path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def ensure_safe_install_target(root: Path, relative_path: str) -> Path:
    """Create only missing directories and refuse every symlink component."""

    relative_path = normalize_repository_path(relative_path)
    root_resolved = root.resolve(strict=True)
    current = root
    for part in Path(relative_path).parts[:-1]:
        current = current / part
        if current.exists() or current.is_symlink():
            current_stat = current.lstat()
            if current.is_symlink() or not stat.S_ISDIR(current_stat.st_mode):
                raise ValueError(
                    f"install parent is not a non-symlink directory: "
                    f"{relative_path}"
                )
        else:
            current.mkdir()
            fsync_directory(current.parent)
    try:
        current.resolve(strict=True).relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(
            f"install parent resolves outside repository: {relative_path}"
        ) from exc
    target = root.joinpath(*Path(relative_path).parts)
    if target.exists() or target.is_symlink():
        target_stat = target.lstat()
        if target.is_symlink() or not stat.S_ISREG(target_stat.st_mode):
            raise ValueError(
                f"install target is not a non-symlink regular file: "
                f"{relative_path}"
            )
    return target


def parse_json_strict(raw: bytes, relative_path: str) -> Any:
    def reject_duplicate_names(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(
                    f"duplicate object name in frozen input {relative_path}: {key}"
                )
            result[key] = value
        return result

    def reject_nonfinite(token: str) -> Any:
        raise ValueError(
            f"non-finite number in frozen input {relative_path}: {token}"
        )

    return json.loads(
        raw,
        object_pairs_hook=reject_duplicate_names,
        parse_constant=reject_nonfinite,
    )


def read_frozen_json(relative_path: str, digest: str, byte_count: int) -> Any:
    raw = strict_regular_file_bytes(REPOSITORY_ROOT, relative_path)
    observed = (raw_sha256(raw), len(raw))
    expected = (digest, byte_count)
    if observed != expected:
        raise ValueError(
            f"frozen input drift: {relative_path}: expected {expected}, got {observed}"
        )
    return parse_json_strict(raw, relative_path)


def render_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def replace_exact_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, list):
        return [replace_exact_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {
            key: replace_exact_strings(item, replacements)
            for key, item in value.items()
        }
    return value


def replacement_map() -> dict[str, str]:
    replacements = {
        "urn:odeya:canonicalization:odeya-jcs-0.2": PROFILE_ID,
        "urn:odeya:schema:canonicalization-profile-core:0.6.0": (
            PROFILE_CORE_SCHEMA_ID
        ),
    }
    for spec in SCHEMA_SPECS:
        replacements[spec["source_id"]] = spec["output_id"]
        replacements[spec["source_domain"]] = spec["output_domain"]
    return replacements


def update_profile_versions(value: Any) -> None:
    if isinstance(value, dict):
        profile_id_contract = value.get("profile_id")
        profile_is_successor = profile_id_contract == PROFILE_ID or (
            isinstance(profile_id_contract, dict)
            and profile_id_contract.get("const") == PROFILE_ID
        )
        if profile_is_successor:
            if value.get("profile_version") == "0.2.0":
                value["profile_version"] = PROFILE_VERSION
            profile_version_schema = value.get("profile_version")
            if (
                isinstance(profile_version_schema, dict)
                and profile_version_schema.get("const") == "0.2.0"
            ):
                profile_version_schema["const"] = PROFILE_VERSION
        for child in value.values():
            update_profile_versions(child)
    elif isinstance(value, list):
        for child in value:
            update_profile_versions(child)


def number_policy_annotation() -> dict[str, Any]:
    return {
        "contract_id": RAW_NUMBER_CONTRACT_ID,
        "contract_path": RAW_NUMBER_CONTRACT_PATH,
        "contract_raw_sha256": f"sha256:{RAW_NUMBER_CONTRACT_SHA256}",
        "profile_id": PROFILE_ID,
        "profile_core_schema_id": PROFILE_CORE_SCHEMA_ID,
        "applicability": (
            "all resolved type-integer assertions and every recursively "
            "integer-valued const leaf"
        ),
        "integer_token_pattern": "^-?(?:0|[1-9][0-9]*)$",
        "integer_minimum_decimal": str(SAFE_INTEGER_MINIMUM),
        "integer_maximum_decimal": str(SAFE_INTEGER_MAXIMUM),
        "type_number_positions": "forbidden_in_exact_reissued_cohort",
        "unclassified_numeric_positions": "reject",
        "boolean_is_not_integer": True,
    }


def transform_schema(spec: dict[str, Any]) -> dict[str, Any]:
    source = read_frozen_json(
        spec["source"], spec["source_sha256"], spec["source_byte_count"]
    )
    result = replace_exact_strings(copy.deepcopy(source), replacement_map())
    result["$id"] = spec["output_id"]
    result["title"] = f'{result["title"]} — odeya-jcs-0.3 reissue'
    result["properties"]["schema_version"] = {"const": spec["version"]}
    result["x-odeya-number-token-policy"] = number_policy_annotation()
    update_profile_versions(result)
    return result


def transform_fixture(spec: dict[str, Any]) -> dict[str, Any]:
    source = read_frozen_json(
        spec["fixture_source"],
        spec["fixture_source_sha256"],
        spec["fixture_source_byte_count"],
    )
    result = replace_exact_strings(source, replacement_map())
    update_profile_versions(result)
    result["schema_version"] = spec["version"]
    if result.get("registry_kind") is not None:
        result["version"] = spec["version"]
    for node in walk(result):
        if (
            isinstance(node, dict)
            and node.get("commitment_kind") == "ordered_member_map_commitment"
        ):
            node["schema_version"] = "0.2.0"
    return result


def scan_raw_number_tokens(raw: bytes) -> list[str]:
    text = raw.decode("utf-8")
    tokens: list[str] = []
    index = 0
    in_string = False
    while index < len(text):
        char = text[index]
        if in_string:
            if char == "\\":
                index += 2
                continue
            if char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            index += 1
            continue
        if char == "-" or char.isdigit():
            match = re.match(
                r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?",
                text[index:],
            )
            if match is None:
                raise ValueError("invalid JSON number scan state")
            token = match.group(0)
            tokens.append(token)
            index += len(token)
            continue
        index += 1
    if in_string:
        raise ValueError("unterminated JSON string during raw-number scan")
    return tokens


def validate_schema(spec: dict[str, Any], schema: dict[str, Any], raw: bytes) -> None:
    if schema["$id"] != spec["output_id"]:
        raise ValueError(f'{spec["output"]}: wrong $id')
    if schema["properties"]["schema_version"] != {"const": spec["version"]}:
        raise ValueError(f'{spec["output"]}: wrong schema_version contract')
    if any(
        isinstance(node, dict)
        and (
            node.get("type") == "number"
            or (
                isinstance(node.get("type"), list)
                and "number" in node["type"]
            )
        )
        for node in walk(schema)
    ):
        raise ValueError(f'{spec["output"]}: type:number is forbidden')
    for node in walk(schema):
        if isinstance(node, float):
            raise ValueError(f'{spec["output"]}: floating numeric value is forbidden')
        if isinstance(node, int) and not isinstance(node, bool):
            if not SAFE_INTEGER_MINIMUM <= node <= SAFE_INTEGER_MAXIMUM:
                raise ValueError(f'{spec["output"]}: integer outside safe range')
    tokens = scan_raw_number_tokens(raw)
    if not all(INTEGER_TOKEN_PATTERN.fullmatch(token) for token in tokens):
        raise ValueError(f'{spec["output"]}: non-integer raw schema number token')
    rendered = raw.decode("utf-8")
    forbidden = (
        spec["source_id"],
        spec["source_domain"],
        "urn:odeya:canonicalization:odeya-jcs-0.2",
        "urn:odeya:schema:canonicalization-profile-core:0.6.0",
    )
    for literal in forbidden:
        if literal in rendered:
            raise ValueError(f'{spec["output"]}: stale literal {literal}')
    annotation = schema.get("x-odeya-number-token-policy")
    if annotation != number_policy_annotation():
        raise ValueError(f'{spec["output"]}: raw-number policy binding drift')


def pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def iter_locations(value: Any, pointer: str = ""):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_locations(child, f"{pointer}/{pointer_escape(key)}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_locations(child, f"{pointer}/{index}")


def numeric_document_tokens(value: Any, raw: bytes) -> list[dict[str, str]]:
    located = [
        {
            "document_pointer": pointer,
            "raw_lexeme": str(node),
            "decimal_value": str(node),
        }
        for pointer, node in iter_locations(value)
        if isinstance(node, int) and not isinstance(node, bool)
    ]
    scanned = scan_raw_number_tokens(raw)
    if [row["raw_lexeme"] for row in located] != scanned:
        raise ValueError("raw numeric token order differs from parsed document order")
    for row in located:
        integer = int(row["raw_lexeme"])
        if not INTEGER_TOKEN_PATTERN.fullmatch(row["raw_lexeme"]):
            raise ValueError("schema-document numeric token is not an integer lexeme")
        if not SAFE_INTEGER_MINIMUM <= integer <= SAFE_INTEGER_MAXIMUM:
            raise ValueError("schema-document numeric token is outside safe range")
    return located


def resolve_json_pointer(document: Any, fragment: str) -> Any:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        raise ValueError(f"unsupported non-pointer fragment: {fragment}")
    current = document
    for encoded in fragment[2:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            current = current[int(token)]
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise ValueError(f"unresolved JSON Pointer fragment: {fragment}")
    return current


def collect_integer_const_leaves(
    value: Any, schema_location: str
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_pointer, child in iter_locations(value):
        if isinstance(child, int) and not isinstance(child, bool):
            if not SAFE_INTEGER_MINIMUM <= child <= SAFE_INTEGER_MAXIMUM:
                raise ValueError(
                    f"integer-valued const outside safe range: {schema_location}"
                )
            rows.append(
                {
                    "schema_location": f"{schema_location}{relative_pointer}",
                    "assertion_keyword": "const",
                    "position_rule": "recursive_integer_valued_const_leaf",
                    "decimal_value": str(child),
                }
            )
    return rows


def expanded_instance_numeric_positions(
    root_schema_id: str,
    by_id: dict[str, tuple[str, dict[str, Any], bytes]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    integer_types: list[dict[str, Any]] = []
    integer_consts: list[dict[str, Any]] = []
    unclassified: list[str] = []

    def append_const_leaves(
        value: Any,
        evaluation_path: list[dict[str, str]],
        resolved_schema_id: str,
        resolved_digest: str,
        keyword_location: str,
        relative_pointer: str = "",
    ) -> None:
        if isinstance(value, int) and not isinstance(value, bool):
            if not SAFE_INTEGER_MINIMUM <= value <= SAFE_INTEGER_MAXIMUM:
                raise ValueError(
                    f"integer-valued const outside safe range: {keyword_location}"
                )
            integer_consts.append(
                {
                    "evaluation_path": copy.deepcopy(evaluation_path),
                    "resolved_schema_id": resolved_schema_id,
                    "resolved_schema_raw_digest": resolved_digest,
                    "assertion_schema_location": keyword_location,
                    "position_rule": "recursive_integer_valued_const_leaf",
                    "const_leaf_pointer": relative_pointer,
                    "decimal_value": str(value),
                }
            )
            return
        if isinstance(value, dict):
            for key, child in value.items():
                append_const_leaves(
                    child,
                    [
                        *evaluation_path,
                        {"kind": "const_object_member", "token": key},
                    ],
                    resolved_schema_id,
                    resolved_digest,
                    keyword_location,
                    f"{relative_pointer}/{pointer_escape(key)}",
                )
        elif isinstance(value, list):
            for index, child in enumerate(value):
                append_const_leaves(
                    child,
                    [
                        *evaluation_path,
                        {"kind": "const_array_index", "token": str(index)},
                    ],
                    resolved_schema_id,
                    resolved_digest,
                    keyword_location,
                    f"{relative_pointer}/{index}",
                )

    def descend(
        resolved_schema_id: str,
        node: Any,
        schema_pointer: str,
        evaluation_path: list[dict[str, str]],
        ref_stack: tuple[tuple[str, str], ...],
    ) -> None:
        if node is True:
            unclassified.append(
                f"{resolved_schema_id}#{schema_pointer}:true_schema"
            )
            return
        if node is False or not isinstance(node, dict):
            return
        _, _, resolved_raw = by_id[resolved_schema_id]
        resolved_digest = f"sha256:{raw_sha256(resolved_raw)}"
        node_type = node.get("type")
        if node_type == "integer" or (
            isinstance(node_type, list) and "integer" in node_type
        ):
            integer_types.append(
                {
                    "evaluation_path": copy.deepcopy(evaluation_path),
                    "resolved_schema_id": resolved_schema_id,
                    "resolved_schema_raw_digest": resolved_digest,
                    "assertion_schema_location": (
                        f"{resolved_schema_id}#{schema_pointer}/type"
                    ),
                    "position_rule": "integer_type",
                }
            )
        if node_type == "number" or (
            isinstance(node_type, list) and "number" in node_type
        ):
            unclassified.append(
                f"{resolved_schema_id}#{schema_pointer}/type"
            )
        if "const" in node:
            append_const_leaves(
                node["const"],
                evaluation_path,
                resolved_schema_id,
                resolved_digest,
                f"{resolved_schema_id}#{schema_pointer}/const",
            )
        if "enum" in node and any(
            isinstance(item, int) and not isinstance(item, bool)
            for item in node["enum"]
        ):
            if node_type != "integer":
                unclassified.append(
                    f"{resolved_schema_id}#{schema_pointer}/enum"
                )

        ref = node.get("$ref")
        if isinstance(ref, str):
            target_id, separator, suffix = ref.partition("#")
            target_id = target_id or resolved_schema_id
            if target_id not in by_id:
                raise ValueError(f"unresolved exact-cohort reference: {ref}")
            fragment = f"#{suffix}" if separator else ""
            ref_key = (target_id, fragment or "#")
            if ref_key in ref_stack:
                raise ValueError(f"numeric applicability reference cycle: {ref}")
            _, target_document, _ = by_id[target_id]
            target_node = resolve_json_pointer(target_document, fragment)
            descend(
                target_id,
                target_node,
                fragment[1:] if fragment else "",
                [*evaluation_path, {"kind": "ref", "token": ref}],
                (*ref_stack, ref_key),
            )

        mapping_keywords = {
            "properties": "property",
            "patternProperties": "pattern_property",
            "dependentSchemas": "dependent_schema",
        }
        for keyword, kind in mapping_keywords.items():
            child_map = node.get(keyword)
            if isinstance(child_map, dict):
                for name, child in child_map.items():
                    descend(
                        resolved_schema_id,
                        child,
                        (
                            f"{schema_pointer}/{pointer_escape(keyword)}/"
                            f"{pointer_escape(name)}"
                        ),
                        [*evaluation_path, {"kind": kind, "token": name}],
                        ref_stack,
                    )
        indexed_keywords = {
            "allOf": "all_of_branch",
            "anyOf": "any_of_branch",
            "oneOf": "one_of_branch",
            "prefixItems": "prefix_item_index",
        }
        for keyword, kind in indexed_keywords.items():
            children = node.get(keyword)
            if isinstance(children, list):
                for index, child in enumerate(children):
                    descend(
                        resolved_schema_id,
                        child,
                        f"{schema_pointer}/{keyword}/{index}",
                        [
                            *evaluation_path,
                            {"kind": kind, "token": str(index)},
                        ],
                        ref_stack,
                    )
        singleton_keywords = {
            "items": "items",
            "contains": "contains",
            "if": "if_branch",
            "then": "then_branch",
            "else": "else_branch",
            "not": "not_branch",
            "additionalProperties": "additional_property",
            "unevaluatedProperties": "unevaluated_property",
            "unevaluatedItems": "unevaluated_item",
        }
        for keyword, kind in singleton_keywords.items():
            child = node.get(keyword)
            if isinstance(child, (dict, bool)):
                if child is False:
                    continue
                descend(
                    resolved_schema_id,
                    child,
                    f"{schema_pointer}/{keyword}",
                    [*evaluation_path, {"kind": kind, "token": keyword}],
                    ref_stack,
                )

    _, root_document, _ = by_id[root_schema_id]
    descend(root_schema_id, root_document, "", [], ((root_schema_id, "#"),))

    def deduplicate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[bytes] = set()
        result: list[dict[str, Any]] = []
        for row in rows:
            key = json.dumps(
                row,
                ensure_ascii=False,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
            if key not in seen:
                seen.add(key)
                result.append(row)
        return result

    return deduplicate(integer_types), deduplicate(integer_consts), sorted(
        set(unclassified)
    )


def static_schema_position_inventory(
    schema_documents: dict[str, tuple[dict[str, Any], bytes]],
) -> dict[str, Any]:
    by_id = {
        document["$id"]: (path, document, raw)
        for path, (document, raw) in schema_documents.items()
    }
    expected_ids = {spec["output_id"] for spec in ALL_SCHEMA_SPECS}
    if set(by_id) != expected_ids:
        raise ValueError("static inventory schema-ID cohort mismatch")
    rows: list[dict[str, Any]] = []
    for spec in ALL_SCHEMA_SPECS:
        path = spec["output"]
        document, raw = schema_documents[path]
        schema_id = document["$id"]
        integer_types: list[dict[str, str]] = []
        integer_consts: list[dict[str, str]] = []
        reference_edges: list[dict[str, str]] = []
        type_numbers: list[str] = []
        number_unions: list[str] = []
        unclassified: list[str] = []

        def visit_schema(node: Any, pointer: str) -> None:
            if isinstance(node, bool):
                return
            if isinstance(node, list):
                for index, child in enumerate(node):
                    visit_schema(child, f"{pointer}/{index}")
                return
            if not isinstance(node, dict):
                return
            node_type = node.get("type")
            if node_type == "number":
                type_numbers.append(f"{schema_id}#{pointer}/type")
            elif isinstance(node_type, list) and "number" in node_type:
                number_unions.append(f"{schema_id}#{pointer}/type")
            if node_type == "integer" or (
                isinstance(node_type, list) and "integer" in node_type
            ):
                integer_types.append(
                    {
                        "schema_location": f"{schema_id}#{pointer}/type",
                        "assertion_keyword": "type",
                        "position_rule": "integer_type",
                    }
                )
            if "const" in node:
                integer_consts.extend(
                    collect_integer_const_leaves(
                        node["const"], f"{schema_id}#{pointer}/const"
                    )
                )
            if "enum" in node:
                enum_has_integer = any(
                    isinstance(item, int) and not isinstance(item, bool)
                    for item in node["enum"]
                )
                if enum_has_integer and node_type != "integer":
                    unclassified.append(f"{schema_id}#{pointer}/enum")
            numeric_assertion_keywords = {
                "minimum",
                "maximum",
                "exclusiveMinimum",
                "exclusiveMaximum",
                "multipleOf",
            }
            if (
                numeric_assertion_keywords.intersection(node)
                and node_type not in ("integer", "number")
            ):
                unclassified.append(f"{schema_id}#{pointer}")
            ref = node.get("$ref")
            if "$dynamicRef" in node or "$recursiveRef" in node:
                raise ValueError(
                    f"{path}: dynamic or recursive reference is outside the "
                    "exact static inventory contract"
                )
            if isinstance(ref, str):
                target_id, separator, suffix = ref.partition("#")
                resolved_id = target_id or schema_id
                if resolved_id not in by_id:
                    raise ValueError(
                        f"{path}: unresolved exact-cohort reference {ref}"
                    )
                target_path, target_document, target_raw = by_id[resolved_id]
                fragment = f"#{suffix}" if separator else ""
                resolve_json_pointer(target_document, fragment)
                reference_edges.append(
                    {
                        "source_schema_location": f"{schema_id}#{pointer}/$ref",
                        "target_schema_id": resolved_id,
                        "target_schema_raw_digest": (
                            f"sha256:{raw_sha256(target_raw)}"
                        ),
                        "target_schema_path": target_path,
                        "target_fragment": fragment or "#",
                    }
                )
            for key, child in node.items():
                if key in {"const", "enum", "examples", "default"} or key.startswith(
                    "x-"
                ):
                    continue
                if key in {
                    "$defs",
                    "definitions",
                    "properties",
                    "patternProperties",
                    "dependentSchemas",
                } and isinstance(child, dict):
                    for name, subschema in child.items():
                        visit_schema(
                            subschema,
                            (
                                f"{pointer}/{pointer_escape(key)}/"
                                f"{pointer_escape(name)}"
                            ),
                        )
                    continue
                if isinstance(child, (dict, list, bool)):
                    visit_schema(child, f"{pointer}/{pointer_escape(key)}")

        visit_schema(document, "")
        expanded_types, expanded_consts, expanded_unclassified = (
            expanded_instance_numeric_positions(schema_id, by_id)
        )
        if (
            type_numbers
            or number_unions
            or unclassified
            or expanded_unclassified
        ):
            raise ValueError(
                f"{path}: unsupported numeric applicability: "
                f"type_number={type_numbers}, unions={number_unions}, "
                f"unclassified={unclassified}, "
                f"expanded_unclassified={expanded_unclassified}"
            )
        document_tokens = numeric_document_tokens(document, raw)
        document_token_bytes = json.dumps(
            document_tokens,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        position_bytes = json.dumps(
            {
                "integer_type_assertions": integer_types,
                "integer_const_leaves": integer_consts,
                "expanded_instance_integer_type_positions": expanded_types,
                "expanded_instance_integer_const_positions": expanded_consts,
                "resolved_reference_edges": reference_edges,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        rows.append(
            {
                "schema_path": path,
                "schema_id": schema_id,
                "schema_raw_digest": f"sha256:{raw_sha256(raw)}",
                "schema_byte_count": len(raw),
                "schema_document_numeric_literals_are_instance_positions": False,
                "schema_document_numeric_token_count": len(document_tokens),
                "schema_document_number_tokens": document_tokens,
                "schema_document_numeric_token_inventory_sha256": (
                    f"sha256:{raw_sha256(document_token_bytes)}"
                ),
                "integer_type_assertion_count": len(integer_types),
                "integer_type_assertions": integer_types,
                "integer_const_leaf_count": len(integer_consts),
                "integer_const_leaves": integer_consts,
                "expanded_instance_integer_type_position_count": len(
                    expanded_types
                ),
                "expanded_instance_integer_type_positions": expanded_types,
                "expanded_instance_integer_const_position_count": len(
                    expanded_consts
                ),
                "expanded_instance_integer_const_positions": expanded_consts,
                "resolved_reference_edge_count": len(reference_edges),
                "resolved_reference_edges": reference_edges,
                "type_number_assertions": [],
                "number_admitting_unions": [],
                "unclassified_numeric_assertions": [],
                "position_inventory_sha256": (
                    f"sha256:{raw_sha256(position_bytes)}"
                ),
            }
        )
    return {
        "inventory_kind": (
            "static_exact_schema_position_inventory_without_subject_digest"
        ),
        "derivation_input": "twelve_final_schema_byte_strings_only",
        "schema_count": 12,
        "profile_id": PROFILE_ID,
        "raw_number_contract_id": RAW_NUMBER_CONTRACT_ID,
        "future_instance_pointers_included": False,
        "concrete_subject_digests_included": False,
        "schema_document_numeric_literals_are_future_instance_positions": False,
        "type_number_supported": False,
        "number_admitting_unions_supported": False,
        "unclassified_numeric_positions_permitted": False,
        "schemas": rows,
    }


def resource_role(spec: dict[str, Any]) -> str:
    if "resource_role" in spec:
        return spec["resource_role"]
    binding_id = spec["binding_id"]
    if binding_id == "ordered_member_map_commitment":
        return "product_commitment_schema"
    if "registry" in binding_id and binding_id != "schema_resource_record":
        return "product_registry_schema"
    return "product_member_schema"


def schema_bindings(
    schema_raw_by_path: dict[str, bytes] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in ALL_SCHEMA_SPECS:
        raw = None if schema_raw_by_path is None else schema_raw_by_path[spec["output"]]
        rows.append(
            {
                "binding_id": spec["binding_id"],
                "path": spec["output"],
                "schema_id": spec["output_id"],
                "raw_digest": (
                    DYNAMIC_DIGEST
                    if raw is None
                    else f"sha256:{raw_sha256(raw)}"
                ),
                "byte_count": DYNAMIC_INTEGER if raw is None else len(raw),
                "resource_role": resource_role(spec),
            }
        )
    return rows


def predecessor_binding() -> dict[str, Any]:
    return {
        "profile_id": "urn:odeya:canonicalization:odeya-jcs-0.2",
        "profile_version": "0.2.0",
        "profile_issued": False,
        "profile_core_path": FROZEN_CORE["path"],
        "profile_core_schema_path": CONTROL_SCHEMA_SPECS[0]["source"],
        "profile_core_schema_id": CONTROL_SCHEMA_SPECS[0]["source_id"],
        "profile_core_raw_digest": FROZEN_CORE["raw_digest"],
        "profile_core_byte_count": FROZEN_CORE["byte_count"],
        "profile_core_schema_raw_digest": (
            f'sha256:{CONTROL_SCHEMA_SPECS[0]["source_sha256"]}'
        ),
        "profile_core_schema_byte_count": CONTROL_SCHEMA_SPECS[0][
            "source_byte_count"
        ],
        "profile_evidence_path": FROZEN_EVIDENCE["path"],
        "profile_evidence_schema_path": CONTROL_SCHEMA_SPECS[1]["source"],
        "profile_evidence_schema_id": CONTROL_SCHEMA_SPECS[1]["source_id"],
        "profile_evidence_raw_digest": FROZEN_EVIDENCE["raw_digest"],
        "profile_evidence_byte_count": FROZEN_EVIDENCE["byte_count"],
        "profile_evidence_schema_raw_digest": (
            f'sha256:{CONTROL_SCHEMA_SPECS[1]["source_sha256"]}'
        ),
        "profile_evidence_schema_byte_count": CONTROL_SCHEMA_SPECS[1][
            "source_byte_count"
        ],
        "profile_migration_path": FROZEN_MIGRATION["path"],
        "profile_migration_schema_path": CONTROL_SCHEMA_SPECS[2]["source"],
        "profile_migration_schema_id": CONTROL_SCHEMA_SPECS[2]["source_id"],
        "profile_migration_raw_digest": FROZEN_MIGRATION["raw_digest"],
        "profile_migration_byte_count": FROZEN_MIGRATION["byte_count"],
        "profile_migration_schema_raw_digest": (
            f'sha256:{CONTROL_SCHEMA_SPECS[2]["source_sha256"]}'
        ),
        "profile_migration_schema_byte_count": CONTROL_SCHEMA_SPECS[2][
            "source_byte_count"
        ],
        "binding_status": "exact_retained_unissued_predecessor_bytes",
    }


def raw_number_binding() -> dict[str, Any]:
    return {
        "contract_id": RAW_NUMBER_CONTRACT_ID,
        "contract_path": RAW_NUMBER_CONTRACT_PATH,
        "contract_raw_digest": f"sha256:{RAW_NUMBER_CONTRACT_SHA256}",
        "contract_byte_count": RAW_NUMBER_CONTRACT_BYTE_COUNT,
        "contract_schema_path": RAW_NUMBER_CONTRACT_SCHEMA["path"],
        "contract_schema_id": RAW_NUMBER_CONTRACT_SCHEMA["schema_id"],
        "contract_schema_raw_digest": RAW_NUMBER_CONTRACT_SCHEMA["raw_digest"],
        "contract_schema_byte_count": RAW_NUMBER_CONTRACT_SCHEMA["byte_count"],
        "binding_status": "exact_retained_architecture_contract_bytes",
    }


def domain_registry() -> list[dict[str, str]]:
    return [
        {
            "domain_separator": spec["output_domain"],
            "subject_class": spec["binding_id"].removesuffix("_v0_9").removesuffix(
                "_v0_8"
            ),
            "declaring_schema_binding_id": spec["binding_id"],
            "registration_status": (
                "scoped_successor_candidate_unissued_unadmitted"
            ),
        }
        for spec in SCHEMA_SPECS
    ]


def empty_static_inventory() -> dict[str, Any]:
    rows = []
    for spec in ALL_SCHEMA_SPECS:
        rows.append(
            {
                "schema_path": spec["output"],
                "schema_id": spec["output_id"],
                "schema_raw_digest": DYNAMIC_DIGEST,
                "schema_byte_count": DYNAMIC_INTEGER,
                "schema_document_numeric_literals_are_instance_positions": False,
                "schema_document_numeric_token_count": DYNAMIC_INTEGER,
                "schema_document_number_tokens": [],
                "schema_document_numeric_token_inventory_sha256": DYNAMIC_DIGEST,
                "integer_type_assertion_count": DYNAMIC_INTEGER,
                "integer_type_assertions": [],
                "integer_const_leaf_count": DYNAMIC_INTEGER,
                "integer_const_leaves": [],
                "expanded_instance_integer_type_position_count": DYNAMIC_INTEGER,
                "expanded_instance_integer_type_positions": [],
                "expanded_instance_integer_const_position_count": DYNAMIC_INTEGER,
                "expanded_instance_integer_const_positions": [],
                "resolved_reference_edge_count": DYNAMIC_INTEGER,
                "resolved_reference_edges": [],
                "type_number_assertions": [],
                "number_admitting_unions": [],
                "unclassified_numeric_assertions": [],
                "position_inventory_sha256": DYNAMIC_DIGEST,
            }
        )
    return {
        "inventory_kind": (
            "static_exact_schema_position_inventory_without_subject_digest"
        ),
        "derivation_input": "twelve_final_schema_byte_strings_only",
        "schema_count": 12,
        "profile_id": PROFILE_ID,
        "raw_number_contract_id": RAW_NUMBER_CONTRACT_ID,
        "future_instance_pointers_included": False,
        "concrete_subject_digests_included": False,
        "schema_document_numeric_literals_are_future_instance_positions": False,
        "type_number_supported": False,
        "number_admitting_unions_supported": False,
        "unclassified_numeric_positions_permitted": False,
        "schemas": rows,
    }


def make_core(
    bindings: list[dict[str, Any]], inventory: dict[str, Any]
) -> dict[str, Any]:
    frozen = read_frozen_json(
        FROZEN_CORE["path"],
        FROZEN_CORE["raw_digest"].removeprefix("sha256:"),
        FROZEN_CORE["byte_count"],
    )
    parser_contract = copy.deepcopy(frozen["parser_contract"])
    parser_contract["schema_resolution"] = (
        "preloaded_exact_resource_id_raw_digest_and_byte_count"
    )
    parser_contract["network_access"] = "disabled"
    serialization_contract = copy.deepcopy(frozen["serialization_contract"])
    serialization_contract.update(
        {
            "rfc8785_verified_errata": ["EID-6292", "EID-7920"],
            "ecmascript_edition": "ECMA-262_10th_edition_2019",
            "ecmascript_number_serialization": "section_7.1.12.1_including_Note_2",
            "ecmascript_string_serialization": (
                "section_24.5.2.2_via_RFC8785_EID_6292"
            ),
            "rfc8259_eid_5318_applied_to_canonical_output": False,
            "solidus_output": "emit_unescaped",
        }
    )
    framing = copy.deepcopy(frozen["scoped_digest_framing_contract"])
    framing["product_digest_computation_blocker"] = (
        "full_conformance_complete_offline_resolution_accountable_review_and_"
        "operator_acceptance_absent"
    )
    profile_reference = copy.deepcopy(frozen["profile_reference_contract"])
    profile_reference.update(
        {
            "profile_id": PROFILE_ID,
            "profile_version": PROFILE_VERSION,
            "profile_core_schema_id": PROFILE_CORE_SCHEMA_ID,
            "profile_core_raw_digest_source": EVIDENCE_RECORD_PATH,
        }
    )
    nodes = [spec["binding_id"] for spec in ALL_SCHEMA_SPECS] + [
        "successor_profile_core_artifact",
        "successor_profile_evidence_artifact",
        "successor_profile_migration_artifact",
    ]
    edges = [
        {
            "subject": "schema_registry_v0_9",
            "dependency": "ordered_member_map_commitment",
        },
        {
            "subject": "aggregate_state_subject_registry_v0_8",
            "dependency": "ordered_member_map_commitment",
        },
        {
            "subject": "reducer_registry_v0_8",
            "dependency": "ordered_member_map_commitment",
        },
        {
            "subject": "event_contract_registry_v0_8",
            "dependency": "ordered_member_map_commitment",
        },
    ]
    edges.extend(
        {
            "subject": "successor_profile_core_artifact",
            "dependency": spec["binding_id"],
        }
        for spec in ALL_SCHEMA_SPECS
    )
    edges.extend(
        [
            {
                "subject": "successor_profile_evidence_artifact",
                "dependency": "successor_profile_core_artifact",
            },
            {
                "subject": "successor_profile_migration_artifact",
                "dependency": "successor_profile_evidence_artifact",
            },
        ]
    )
    return {
        "schema_version": "0.7.0",
        "artifact_class": "canonicalization_profile_core_candidate",
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "candidate_status": (
            "scoped_successor_candidate_unissued_unadmitted_no_product_digests"
        ),
        "decision_refs": [
            "docs/decisions/0101-require-raw-number-token-provenance-before-profile-conformance.md",
            "docs/decisions/0103-construct-side-by-side-odeya-jcs-0-3-candidate.md",
        ],
        "scope": {
            "scope_id": "prq-002e-product-identity-profile-0.3-construction",
            "scope_kind": "architecture_only_profile_and_schema_construction",
            "successor_of_profile_id": (
                "urn:odeya:canonicalization:odeya-jcs-0.2"
            ),
            "successor_of_profile_version": "0.2.0",
            "original_schema_resource_count": 120,
            "retained_predecessor_schema_resource_count": 12,
            "successor_schema_resource_count": 12,
            "side_by_side_schema_resource_count": 144,
            "product_identity_schema_count": 9,
            "retained_original_0_1_direct_consumer_count": 106,
            "all_predecessor_bytes_preserved": True,
            "global_profile_replacement_claimed": False,
            "profile_alias_declared": False,
            "implicit_consumer_migration_allowed": False,
        },
        "bootstrap_boundary": copy.deepcopy(frozen["bootstrap_boundary"]),
        "predecessor_binding": predecessor_binding(),
        "raw_octet_adapter_contract": {
            "adapter_precedes_host_value_materialization": True,
            "raw_sha256_and_byte_count_verified_before_decode_when_expected": True,
            "input_encoding": "strict_RFC3629_UTF-8",
            "byte_order_mark": "reject",
            "json_grammar": "RFC8259_exactly_one_value",
            "comments_trailing_commas_and_extensions": "reject",
            "duplicate_decoded_object_names": "reject_before_lossy_mapping",
            "surrogate_and_unicode_noncharacter_code_points": "reject",
            "raw_number_lexeme_and_unique_RFC6901_pointer_retained": True,
            "sidecar_in_product_digest_preimage": False,
        },
        "parser_contract": parser_contract,
        "raw_number_token_contract_binding": raw_number_binding(),
        "number_token_policy": {
            "normative_integration_status": (
                "embedded_exact_cohort_rule_not_delegated_to_host_parser"
            ),
            "classification_point": (
                "after_utf8_and_json_lexing_before_mapping_or_schema_evaluation"
            ),
            "integer_token_pattern": "^-?(?:0|[1-9][0-9]*)$",
            "integer_position_rule": "admit_integer_token_only",
            "integer_position_applies_when": (
                "static_inventory_resolves_type_integer_or_recursive_integer_"
                "valued_const_leaf"
            ),
            "integer_minimum_decimal": str(SAFE_INTEGER_MINIMUM),
            "integer_maximum_decimal": str(SAFE_INTEGER_MAXIMUM),
            "integral_fraction_or_exponent": "reject",
            "lexical_negative_zero": "reject",
            "boolean_is_not_integer": True,
            "decimal_to_binary64_rounding": "IEEE754-2019_roundTiesToEven",
            "safe_integer_conversion_exact": True,
            "type_number_positions": "forbidden_in_exact_cohort",
            "number_admitting_unions": "forbidden_in_exact_cohort",
            "unclassified_numeric_positions": "reject",
            "generic_number_semantics_claimed": False,
            "downstream_subject_trace_required_before_subject_identity": True,
            "downstream_subject_trace_bound_inside_its_subject": False,
        },
        "static_numeric_applicability_inventory": inventory,
        "serialization_contract": serialization_contract,
        "scoped_digest_framing_contract": framing,
        "profile_reference_contract": profile_reference,
        "member_key_profiles": copy.deepcopy(frozen["member_key_profiles"]),
        "successor_schema_bindings": bindings,
        "domain_registry": domain_registry(),
        "superseded_reservations": copy.deepcopy(
            frozen["superseded_reservations"]
        ),
        "digest_dependency_graph": {
            "edge_direction": "subject_to_exact_dependency",
            "node_ids_unique": True,
            "self_edges_allowed": False,
            "cycles_allowed": False,
            "nodes": nodes,
            "edges": edges,
            "core_raw_digest_inside_core": False,
            "evidence_depends_on_migration_record_digest": False,
            "migration_depends_on_evidence_record": True,
            "downstream_trace_inside_subject": False,
            "cross_resource_schema_reference_cycles_allowed": False,
        },
        "migration_boundary": {
            "migration_candidate_path": MIGRATION_RECORD_PATH,
            "migration_schema_id": CONTROL_SCHEMA_SPECS[2]["output_id"],
            "migration_kind": (
                "explicit_0.2_to_0.3_resource_successor_without_digest_inheritance"
            ),
            "predecessor_instances_claimed_issued": False,
            "probe_instances_in_scope": False,
            "retained_predecessor_consumers_rewritten": False,
            "current_consumer_migration_complete": False,
            "offline_resolver_complete": False,
        },
        "authority_boundary": copy.deepcopy(frozen["authority_boundary"]),
    }


def core_binding(core_raw: bytes | None, control_schema_raw: bytes | None) -> dict[str, Any]:
    return {
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "profile_core_path": CORE_RECORD_PATH,
        "profile_core_schema_path": CONTROL_SCHEMA_SPECS[0]["output"],
        "profile_core_schema_id": PROFILE_CORE_SCHEMA_ID,
        "profile_core_raw_digest": (
            DYNAMIC_DIGEST
            if core_raw is None
            else f"sha256:{raw_sha256(core_raw)}"
        ),
        "profile_core_byte_count": (
            DYNAMIC_INTEGER if core_raw is None else len(core_raw)
        ),
        "profile_core_schema_raw_digest": (
            DYNAMIC_DIGEST
            if control_schema_raw is None
            else f"sha256:{raw_sha256(control_schema_raw)}"
        ),
        "profile_core_schema_byte_count": (
            DYNAMIC_INTEGER
            if control_schema_raw is None
            else len(control_schema_raw)
        ),
        "core_contains_self_hash": False,
        "binding_is_external_to_core": True,
        "binding_status": "exact_candidate_bytes_unissued_unadmitted",
    }


def make_evidence(
    bindings: list[dict[str, Any]],
    inventory: dict[str, Any],
    core_raw: bytes | None,
    core_schema_raw: bytes | None,
) -> dict[str, Any]:
    return {
        "schema_version": "0.7.0",
        "artifact_class": "canonicalization_profile_candidate_evidence",
        "candidate_status": (
            "exact_candidate_bytes_bound_profile_unissued_gate_a_blocked"
        ),
        "recorded_at": "2026-07-29T00:00:00.000000Z",
        "profile_core_binding": core_binding(core_raw, core_schema_raw),
        "predecessor_binding": predecessor_binding(),
        "successor_schema_bindings": bindings,
        "raw_number_token_contract_binding": raw_number_binding(),
        "static_numeric_applicability_inventory": inventory,
        "declared_domain_inventory": {
            "declared_domain_count": 9,
            "domain_constants_unique": True,
            "domain_separators": [
                spec["output_domain"] for spec in SCHEMA_SPECS
            ],
            "domains_are_scoped_to_successor_resources": True,
            "current_consumers_admitted": False,
        },
        "construction_observation": {
            "retained_construction_order": [
                "verify_exact_frozen_0.2_inputs",
                "freeze_twelve_final_only_0.3_schemas",
                "derive_static_schema_position_inventory",
                "write_core_without_self_digest",
                "bind_core_externally_in_evidence",
                "write_0.2_to_0.3_migration_after_evidence",
            ],
            "later_required_order_not_executed_here": [
                "produce_per_subject_traces_downstream",
                "run_source_separated_full_profile_conformance",
                "obtain_accountable_review_and_operator_acceptance",
                "replace_external_receipt_last",
            ],
            "downstream_subject_traces_produced": False,
            "source_separated_full_profile_conformance_executed": False,
            "accountable_review_executed": False,
            "operator_acceptance_executed": False,
            "schema_count": 12,
            "static_inventory_schema_count": 12,
            "schema_meta_validation_complete": True,
            "structural_nonidentity_fixture_count": 9,
            "product_member_instance_count": 0,
            "product_snapshot_instance_count": 0,
            "product_root_instance_count": 0,
            "product_digest_count": 0,
            "profile_core_self_hash_observed": False,
            "evidence_self_hash_observed": False,
            "migration_record_is_dependency_of_this_evidence": False,
            "evidence_subject_trace_bound_here": False,
            "digest_inheritance_from_predecessor_allowed": False,
        },
        "consumer_census_summary": {
            "baseline_commit": BASELINE_COMMIT,
            "baseline_tree": BASELINE_TREE,
            "original_schema_resource_count": 120,
            "predecessor_0_2_schema_resource_count": 12,
            "successor_0_3_schema_resource_count": 12,
            "side_by_side_schema_resource_count": 144,
            "retained_original_0_1_direct_consumer_count": 106,
            "historical_and_probe_material_in_product_census": False,
            "census_detail_ref": MIGRATION_RECORD_PATH,
            "current_consumer_migration_complete": False,
        },
        "offline_resolver_observation": {
            "resolver_mode": (
                "repository_local_exact_id_raw_digest_and_byte_count_only"
            ),
            "predecessor_bytes_materialized": True,
            "successor_schema_bytes_materialized": True,
            "complete_offline_schema_registry": False,
            "historical_reissue_predecessor_bytes_materialized_in_current_tree": (
                False
            ),
            "git_object_reachability_is_durable_retention_proof": False,
            "external_content_addressed_archive_verified": False,
            "unresolved_historical_resource_count": None,
            "missing_count_must_not_be_interpreted_as_zero": True,
            "network_file_search_environment_or_mutable_fallback": "disabled",
            "resolution_status": (
                "incomplete_blocking_before_migration_admission_or_gate_a"
            ),
        },
        "migration_binding": {
            "migration_candidate_path": MIGRATION_RECORD_PATH,
            "migration_schema_path": CONTROL_SCHEMA_SPECS[2]["output"],
            "migration_schema_id": CONTROL_SCHEMA_SPECS[2]["output_id"],
            "migration_record_digest_intentionally_absent": True,
            "migration_record_is_dependency_of_this_evidence": False,
            "migration_complete": False,
        },
        "conformance_evidence": {
            "successor_suite_id": None,
            "case_count": None,
            "accepted_count": None,
            "refused_count": None,
            "unclassified_error_count": None,
            "source_separated_implementation_count": None,
            "implementation_agreement": None,
            "organizational_independence_proven": False,
            "independent_host_reproduction_complete": False,
            "successor_profile_conformance_complete": False,
            "known_bad_self_test_complete": False,
            "missing_values_must_not_be_interpreted_as_zero": True,
        },
        "review_boundary": {
            "accountable_canonicalization_review_complete": False,
            "accountable_security_review_complete": False,
            "accountable_distributed_systems_review_complete": False,
            "operator_acceptance_complete": False,
            "operator_acceptance_ref": None,
            "review_determination_ref": None,
        },
        "acceptance_boundary": {
            "profile_core_canonical_digest": None,
            "profile_registry_member_ref": None,
            "schema_registry_snapshot_ref": None,
            "engine_contract_root_ref": None,
            "activation_ref": None,
            "canonical_identity_may_be_issued": False,
            "schema_resources_admitted": False,
            "product_members_constructed": False,
            "product_snapshots_constructed": False,
            "product_root_constructed": False,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "deployment_authorized": False,
            "external_effects_authorized": False,
            "publication_authorized": False,
        },
    }


def make_migration(
    bindings: list[dict[str, Any]],
    core_raw: bytes | None,
    core_schema_raw: bytes | None,
    evidence_raw: bytes | None,
    evidence_schema_raw: bytes | None,
) -> dict[str, Any]:
    old_migration = read_frozen_json(
        FROZEN_MIGRATION["path"],
        FROZEN_MIGRATION["raw_digest"].removeprefix("sha256:"),
        FROZEN_MIGRATION["byte_count"],
    )
    predecessor_by_binding = {
        spec["binding_id"]: {
            "path": spec["source"],
            "schema_id": spec["source_id"],
            "raw_digest": f'sha256:{spec["source_sha256"]}',
            "byte_count": spec["source_byte_count"],
        }
        for spec in ALL_SCHEMA_SPECS
    }
    successor_by_binding = {row["binding_id"]: row for row in bindings}
    resource_dispositions = []
    for spec in ALL_SCHEMA_SPECS:
        predecessor = predecessor_by_binding[spec["binding_id"]]
        successor = successor_by_binding[spec["binding_id"]]
        resource_dispositions.append(
            {
                "resource_id": spec["binding_id"],
                "classification": resource_role(spec),
                "predecessor": predecessor,
                "successor": {
                    "path": successor["path"],
                    "schema_id": successor["schema_id"],
                    "raw_digest": successor["raw_digest"],
                    "byte_count": successor["byte_count"],
                },
                "action": "add_new_side_by_side_unissued_resource",
                "digest_or_identity_inheritance_allowed": False,
                "issued_predecessor_claimed_within_measured_input": False,
            }
        )
    return {
        "schema_version": "0.2.0",
        "artifact_class": "canonicalization_profile_migration_candidate",
        "migration_id": "urn:odeya:migration:canonicalization-profile:0.2-to-0.3",
        "version": "0.2.0",
        "status": (
            "explicit_scoped_candidate_migration_incomplete_unissued_unadmitted"
        ),
        "decision_ref": (
            "docs/decisions/0103-construct-side-by-side-odeya-jcs-0-3-candidate.md"
        ),
        "baseline_binding": {
            "commit": BASELINE_COMMIT,
            "tree": BASELINE_TREE,
            "original_schema_resource_count": 120,
            "frozen_0_2_schema_resource_count": 12,
            "candidate_0_3_schema_resource_count": 12,
            "side_by_side_schema_resource_count": 144,
        },
        "predecessor_profile_binding": predecessor_binding(),
        "successor_profile_binding": {
            **core_binding(core_raw, core_schema_raw),
            "profile_issued": False,
            "profile_evidence_path": EVIDENCE_RECORD_PATH,
            "profile_evidence_schema_path": CONTROL_SCHEMA_SPECS[1]["output"],
            "profile_evidence_schema_id": CONTROL_SCHEMA_SPECS[1]["output_id"],
            "profile_evidence_raw_digest": (
                DYNAMIC_DIGEST
                if evidence_raw is None
                else f"sha256:{raw_sha256(evidence_raw)}"
            ),
            "profile_evidence_byte_count": (
                DYNAMIC_INTEGER if evidence_raw is None else len(evidence_raw)
            ),
            "profile_evidence_schema_raw_digest": (
                DYNAMIC_DIGEST
                if evidence_schema_raw is None
                else f"sha256:{raw_sha256(evidence_schema_raw)}"
            ),
            "profile_evidence_schema_byte_count": (
                DYNAMIC_INTEGER
                if evidence_schema_raw is None
                else len(evidence_schema_raw)
            ),
            "binding_status": "exact_candidate_core_and_evidence_bytes",
        },
        "scope": {
            "scope_id": "prq-002e-product-identity-profile-0.3-construction",
            "migration_kind": (
                "side_by_side_exact_0.2_to_0.3_schema_resource_successor"
            ),
            "predecessor_profile_id": (
                "urn:odeya:canonicalization:odeya-jcs-0.2"
            ),
            "successor_profile_id": PROFILE_ID,
            "successor_schema_resource_count": 12,
            "retained_original_0_1_direct_consumer_count": 106,
            "global_consumer_migration_claimed": False,
            "global_absence_of_issued_predecessor_instances_claimed": False,
            "probe_promotion_or_migration_claimed": False,
        },
        "resource_dispositions": resource_dispositions,
        "retained_original_0_1_consumer_census": copy.deepcopy(
            old_migration["consumer_census"]
        ),
        "digest_migration_law": {
            "profile_namespaces_comparable_as_identity": False,
            "predecessor_digest_may_be_relabelled": False,
            "predecessor_digest_may_be_inherited": False,
            "successor_requires_new_schema_bytes_and_new_digest": True,
            "issued_predecessor_instances_observed_in_measured_input": 0,
            "global_zero_issued_instance_claim": False,
        },
        "offline_resolver_boundary": {
            "resolution_key": "expected_resource_id_raw_digest_and_byte_count",
            "verify_raw_bytes_before_utf8_decode_and_parse": True,
            "body_id_semantic_version_registry_key_and_dependency_agreement": (
                "required"
            ),
            "aliases_redirects_bare_id_or_latest": "reject",
            "network_file_search_environment_or_mutable_fallback": "disabled",
            "complete_offline_resolution": False,
            "unresolved_historical_resource_count": None,
            "missing_count_must_not_be_interpreted_as_zero": True,
        },
        "completion_boundary": {
            "all_schema_bindings_final_non_null": True,
            "successor_core_raw_binding_complete": True,
            "successor_evidence_raw_binding_complete": True,
            "successor_schema_validation_complete": True,
            "static_numeric_applicability_inventory_complete": True,
            "source_separated_conformance_complete": False,
            "known_bad_self_tests_complete": False,
            "offline_resolution_complete": False,
            "accountable_review_complete": False,
            "operator_acceptance_complete": False,
            "operator_acceptance_ref": None,
            "profile_issued": False,
            "schema_resources_admitted": False,
            "product_members_constructed": False,
            "product_snapshots_constructed": False,
            "product_digest_count": 0,
            "schema_registry_snapshot_ref": None,
            "engine_contract_root_ref": None,
            "activation_ref": None,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "deployment_authorized": False,
            "external_effects_authorized": False,
            "publication_authorized": False,
        },
    }


def schema_for_value(value: Any, path: tuple[str, ...] = ()) -> dict[str, Any]:
    if value is DYNAMIC_DIGEST:
        return {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"}
    if value is DYNAMIC_INTEGER:
        return {
            "type": "integer",
            "minimum": 0,
            "maximum": SAFE_INTEGER_MAXIMUM,
        }
    if isinstance(value, dict):
        properties = {
            key: schema_for_value(child, (*path, key))
            for key, child in value.items()
        }
        return {
            "type": "object",
            "additionalProperties": False,
            "required": list(value),
            "properties": properties,
        }
    if isinstance(value, list):
        terminal = path[-1] if path else ""
        nonempty_string = {"type": "string", "minLength": 1}
        evaluation_segment = {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind", "token"],
            "properties": {
                "kind": nonempty_string,
                "token": {"type": "string"},
            },
        }
        expanded_type_position = {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "evaluation_path",
                "resolved_schema_id",
                "resolved_schema_raw_digest",
                "assertion_schema_location",
                "position_rule",
            ],
            "properties": {
                "evaluation_path": {
                    "type": "array",
                    "items": evaluation_segment,
                },
                "resolved_schema_id": nonempty_string,
                "resolved_schema_raw_digest": {
                    "type": "string",
                    "pattern": "^sha256:[a-f0-9]{64}$",
                },
                "assertion_schema_location": nonempty_string,
                "position_rule": {"const": "integer_type"},
            },
        }
        expanded_const_position = copy.deepcopy(expanded_type_position)
        expanded_const_position["required"].extend(
            ["const_leaf_pointer", "decimal_value"]
        )
        expanded_const_position["properties"]["position_rule"] = {
            "const": "recursive_integer_valued_const_leaf"
        }
        expanded_const_position["properties"]["const_leaf_pointer"] = {
            "type": "string"
        }
        expanded_const_position["properties"]["decimal_value"] = {
            "type": "string",
            "pattern": "^-?(?:0|[1-9][0-9]*)$",
        }
        generic_items: dict[str, dict[str, Any]] = {
            "schema_document_number_tokens": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "document_pointer",
                    "raw_lexeme",
                    "decimal_value",
                ],
                "properties": {
                    "document_pointer": {"type": "string"},
                    "raw_lexeme": {
                        "type": "string",
                        "pattern": "^-?(?:0|[1-9][0-9]*)$",
                    },
                    "decimal_value": {
                        "type": "string",
                        "pattern": "^-?(?:0|[1-9][0-9]*)$",
                    },
                },
            },
            "integer_type_assertions": schema_for_value(
                {
                    "schema_location": "",
                    "assertion_keyword": "type",
                    "position_rule": "integer_type",
                }
            ),
            "integer_const_leaves": schema_for_value(
                {
                    "schema_location": "",
                    "assertion_keyword": "const",
                    "position_rule": "recursive_integer_valued_const_leaf",
                    "decimal_value": "",
                }
            ),
            "resolved_reference_edges": schema_for_value(
                {
                    "source_schema_location": "",
                    "target_schema_id": "",
                    "target_schema_raw_digest": DYNAMIC_DIGEST,
                    "target_schema_path": "",
                    "target_fragment": "",
                }
            ),
            "expanded_instance_integer_type_positions": expanded_type_position,
            "expanded_instance_integer_const_positions": (
                expanded_const_position
            ),
        }
        if terminal in generic_items:
            item_schema = generic_items[terminal]
            for key in (
                "schema_location",
                "decimal_value",
                "source_schema_location",
                "target_schema_id",
                "target_schema_path",
                "target_fragment",
            ):
                if key in item_schema.get("properties", {}):
                    item_schema["properties"][key] = (
                        {
                            "type": "string",
                            "pattern": "^-?(?:0|[1-9][0-9]*)$",
                        }
                        if key == "decimal_value"
                        else {"type": "string", "minLength": 1}
                    )
            return {"type": "array", "items": item_schema}
        if not value:
            return {"type": "array", "maxItems": 0}
        return {
            "type": "array",
            "prefixItems": [
                schema_for_value(child, (*path, str(index)))
                for index, child in enumerate(value)
            ],
            "items": False,
            "minItems": len(value),
            "maxItems": len(value),
        }
    if value is None or isinstance(value, (str, bool, int)):
        return {"const": value}
    raise TypeError(f"unsupported prototype value at {path}: {type(value)!r}")


def final_record_schema(
    schema_id: str, title: str, description: str, prototype: dict[str, Any]
) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "title": title,
        "description": description,
        **schema_for_value(prototype),
        "x-odeya-number-token-policy": number_policy_annotation(),
    }


def expected_outputs() -> dict[str, bytes]:
    raw_contract = strict_regular_file_bytes(
        REPOSITORY_ROOT, RAW_NUMBER_CONTRACT_PATH
    )
    observed_contract = (raw_sha256(raw_contract), len(raw_contract))
    expected_contract = (
        RAW_NUMBER_CONTRACT_SHA256,
        RAW_NUMBER_CONTRACT_BYTE_COUNT,
    )
    if observed_contract != expected_contract:
        raise ValueError(
            f"raw-number contract drift: expected {expected_contract}, "
            f"got {observed_contract}"
        )
    outputs: dict[str, bytes] = {}
    for spec in SCHEMA_SPECS:
        schema = transform_schema(spec)
        schema_raw = render_json(schema)
        validate_schema(spec, schema, schema_raw)
        outputs[spec["output"]] = schema_raw
        outputs[spec["fixture_output"]] = render_json(transform_fixture(spec))

    prototype_bindings = schema_bindings(None)
    prototype_inventory = empty_static_inventory()
    core_prototype = make_core(prototype_bindings, prototype_inventory)
    evidence_prototype = make_evidence(
        prototype_bindings, prototype_inventory, None, None
    )
    migration_prototype = make_migration(
        prototype_bindings, None, None, None, None
    )
    control_schemas = (
        final_record_schema(
            CONTROL_SCHEMA_SPECS[0]["output_id"],
            "Odeya canonicalization profile core 0.3 candidate",
            (
                "Closed final-only architecture schema for the unissued "
                "odeya-jcs-0.3 core. Raw bindings are non-null and the core "
                "contains no digest of itself."
            ),
            core_prototype,
        ),
        final_record_schema(
            CONTROL_SCHEMA_SPECS[1]["output_id"],
            "Odeya canonicalization profile 0.3 candidate evidence",
            (
                "Closed final-only architecture schema for external binding of "
                "the unissued odeya-jcs-0.3 core and exact schema cohort. It "
                "does not bind its own bytes or the later migration record."
            ),
            evidence_prototype,
        ),
        final_record_schema(
            CONTROL_SCHEMA_SPECS[2]["output_id"],
            "Odeya canonicalization profile 0.2 to 0.3 migration candidate",
            (
                "Closed final-only architecture schema for the exact unissued "
                "0.2-to-0.3 side-by-side resource migration candidate."
            ),
            migration_prototype,
        ),
    )
    for spec, schema in zip(CONTROL_SCHEMA_SPECS, control_schemas, strict=True):
        raw = render_json(schema)
        if any(
            isinstance(node, dict)
            and (
                node.get("type") == "number"
                or (
                    isinstance(node.get("type"), list)
                    and "number" in node["type"]
                )
            )
            for node in walk(schema)
        ):
            raise ValueError(f'{spec["output"]}: type:number is forbidden')
        numeric_document_tokens(schema, raw)
        outputs[spec["output"]] = raw

    schema_documents = {
        spec["output"]: (
            parse_json_strict(outputs[spec["output"]], spec["output"]),
            outputs[spec["output"]],
        )
        for spec in ALL_SCHEMA_SPECS
    }
    inventory = static_schema_position_inventory(schema_documents)
    final_bindings = schema_bindings(
        {spec["output"]: outputs[spec["output"]] for spec in ALL_SCHEMA_SPECS}
    )
    core = make_core(final_bindings, inventory)
    core_raw = render_json(core)
    evidence = make_evidence(
        final_bindings,
        inventory,
        core_raw,
        outputs[CONTROL_SCHEMA_SPECS[0]["output"]],
    )
    evidence_raw = render_json(evidence)
    migration = make_migration(
        final_bindings,
        core_raw,
        outputs[CONTROL_SCHEMA_SPECS[0]["output"]],
        evidence_raw,
        outputs[CONTROL_SCHEMA_SPECS[1]["output"]],
    )
    migration_raw = render_json(migration)
    outputs[CORE_RECORD_PATH] = core_raw
    outputs[EVIDENCE_RECORD_PATH] = evidence_raw
    outputs[MIGRATION_RECORD_PATH] = migration_raw
    return outputs


def verify_frozen_inputs() -> None:
    read_frozen_json(
        RAW_NUMBER_CONTRACT_PATH,
        RAW_NUMBER_CONTRACT_SHA256,
        RAW_NUMBER_CONTRACT_BYTE_COUNT,
    )
    read_frozen_json(
        RAW_NUMBER_CONTRACT_SCHEMA["path"],
        RAW_NUMBER_CONTRACT_SCHEMA["raw_digest"].removeprefix("sha256:"),
        RAW_NUMBER_CONTRACT_SCHEMA["byte_count"],
    )
    for spec in SCHEMA_SPECS:
        read_frozen_json(
            spec["source"], spec["source_sha256"], spec["source_byte_count"]
        )
        read_frozen_json(
            spec["fixture_source"],
            spec["fixture_source_sha256"],
            spec["fixture_source_byte_count"],
        )
    for spec in CONTROL_SCHEMA_SPECS:
        read_frozen_json(
            spec["source"], spec["source_sha256"], spec["source_byte_count"]
        )
    for binding in (FROZEN_CORE, FROZEN_EVIDENCE, FROZEN_MIGRATION):
        read_frozen_json(
            binding["path"],
            binding["raw_digest"].removeprefix("sha256:"),
            binding["byte_count"],
        )


def validate_binding_rows(
    rows: list[dict[str, Any]], schema_raw_by_path: dict[str, bytes]
) -> None:
    if [row["path"] for row in rows] != [
        spec["output"] for spec in ALL_SCHEMA_SPECS
    ]:
        raise ValueError("schema binding path order or membership drift")
    for spec, row in zip(ALL_SCHEMA_SPECS, rows, strict=True):
        raw = schema_raw_by_path[spec["output"]]
        expected = {
            "binding_id": spec["binding_id"],
            "path": spec["output"],
            "schema_id": spec["output_id"],
            "raw_digest": f"sha256:{raw_sha256(raw)}",
            "byte_count": len(raw),
            "resource_role": resource_role(spec),
        }
        if row != expected:
            raise ValueError(f'wrong exact binding for {spec["output"]}')


def validate_generated_graph_bytes(outputs: dict[str, bytes]) -> None:
    required = {
        spec["output"] for spec in ALL_SCHEMA_SPECS
    } | {
        spec["fixture_output"] for spec in SCHEMA_SPECS
    } | {CORE_RECORD_PATH, EVIDENCE_RECORD_PATH, MIGRATION_RECORD_PATH}
    if set(outputs) != required:
        raise ValueError(
            f"generated output inventory mismatch: "
            f"missing={sorted(required - set(outputs))}, "
            f"unexpected={sorted(set(outputs) - required)}"
        )
    documents = {
        path: parse_json_strict(raw, path) for path, raw in outputs.items()
    }
    schema_raw_by_path = {
        spec["output"]: outputs[spec["output"]] for spec in ALL_SCHEMA_SPECS
    }
    schema_ids = [documents[spec["output"]]["$id"] for spec in ALL_SCHEMA_SPECS]
    if schema_ids != [spec["output_id"] for spec in ALL_SCHEMA_SPECS]:
        raise ValueError("schema body ID order or membership drift")
    if len(schema_ids) != len(set(schema_ids)):
        raise ValueError("duplicate successor schema ID")

    core = documents[CORE_RECORD_PATH]
    evidence = documents[EVIDENCE_RECORD_PATH]
    migration = documents[MIGRATION_RECORD_PATH]
    validate_binding_rows(core["successor_schema_bindings"], schema_raw_by_path)
    validate_binding_rows(
        evidence["successor_schema_bindings"], schema_raw_by_path
    )
    inventory = core["static_numeric_applicability_inventory"]
    if inventory != evidence["static_numeric_applicability_inventory"]:
        raise ValueError("core/evidence static numeric inventory mismatch")
    if [row["schema_path"] for row in inventory["schemas"]] != [
        spec["output"] for spec in ALL_SCHEMA_SPECS
    ]:
        raise ValueError("static inventory membership or order drift")
    for row in inventory["schemas"]:
        raw = schema_raw_by_path[row["schema_path"]]
        if row["schema_raw_digest"] != f"sha256:{raw_sha256(raw)}":
            raise ValueError("static inventory raw digest mismatch")
        if row["schema_byte_count"] != len(raw):
            raise ValueError("static inventory byte count mismatch")
        if (
            row["type_number_assertions"]
            or row["number_admitting_unions"]
            or row["unclassified_numeric_assertions"]
        ):
            raise ValueError("static inventory contains unsupported numeric position")

    core_digest = f"sha256:{raw_sha256(outputs[CORE_RECORD_PATH])}"
    core_binding_observed = evidence["profile_core_binding"]
    if core_binding_observed["profile_core_raw_digest"] != core_digest:
        raise ValueError("evidence-to-core raw digest edge mismatch")
    if core_binding_observed["profile_core_byte_count"] != len(
        outputs[CORE_RECORD_PATH]
    ):
        raise ValueError("evidence-to-core byte-count edge mismatch")
    evidence_digest = f"sha256:{raw_sha256(outputs[EVIDENCE_RECORD_PATH])}"
    successor = migration["successor_profile_binding"]
    if successor["profile_core_raw_digest"] != core_digest:
        raise ValueError("migration-to-core raw digest edge mismatch")
    if successor["profile_evidence_raw_digest"] != evidence_digest:
        raise ValueError("migration-to-evidence raw digest edge mismatch")
    if successor["profile_evidence_byte_count"] != len(
        outputs[EVIDENCE_RECORD_PATH]
    ):
        raise ValueError("migration-to-evidence byte-count edge mismatch")
    if "migration_record_raw_digest" in evidence.get("migration_binding", {}):
        raise ValueError("evidence cannot bind downstream migration bytes")

    graph = core["digest_dependency_graph"]
    node_set = set(graph["nodes"])
    if len(node_set) != len(graph["nodes"]):
        raise ValueError("dependency graph node IDs are not unique")
    adjacency: dict[str, list[str]] = {node: [] for node in node_set}
    for edge in graph["edges"]:
        subject = edge["subject"]
        dependency = edge["dependency"]
        if subject not in node_set or dependency not in node_set:
            raise ValueError("dependency graph edge names an unknown node")
        if subject == dependency:
            raise ValueError("dependency graph contains a self edge")
        adjacency[subject].append(dependency)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise ValueError("dependency graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for dependency in adjacency[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in node_set:
        visit(node)
    if not {
        (
            "successor_profile_evidence_artifact",
            "successor_profile_core_artifact",
        ),
        (
            "successor_profile_migration_artifact",
            "successor_profile_evidence_artifact",
        ),
    }.issubset(
        {(edge["subject"], edge["dependency"]) for edge in graph["edges"]}
    ):
        raise ValueError("required core-to-evidence-to-migration edges absent")

    for path in (CORE_RECORD_PATH, EVIDENCE_RECORD_PATH, MIGRATION_RECORD_PATH):
        own_digest = f"sha256:{raw_sha256(outputs[path])}"
        if any(node == own_digest for node in walk(documents[path])):
            raise ValueError(f"{path}: artifact contains its own raw digest")
    if evidence["construction_observation"]["product_digest_count"] != 0:
        raise ValueError("evidence contains a product digest claim")
    if migration["completion_boundary"]["product_digest_count"] != 0:
        raise ValueError("migration contains a product digest claim")


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_staged_outputs(stage_root: Path, outputs: dict[str, bytes]) -> None:
    for relative_path, raw in outputs.items():
        path = stage_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    directories = sorted(
        {stage_root, *(path.parent for path in stage_root.rglob("*") if path.is_file())},
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        fsync_directory(directory)


def read_expected_tree(
    root: Path, expected_paths: set[str], exact_inventory: bool
) -> dict[str, bytes]:
    if exact_inventory:
        actual_paths: set[str] = set()
        for path in root.rglob("*"):
            relative_path = path.relative_to(root).as_posix()
            path_stat = path.lstat()
            if path.is_symlink():
                raise ValueError(
                    f"staged artifact is a symlink: {relative_path}"
                )
            if stat.S_ISREG(path_stat.st_mode):
                strict_regular_file_bytes(root, relative_path)
                actual_paths.add(relative_path)
            elif not stat.S_ISDIR(path_stat.st_mode):
                raise ValueError(
                    f"staged artifact has unsupported type: {relative_path}"
                )
        if actual_paths != expected_paths:
            raise ValueError(
                f"staged inventory mismatch: "
                f"missing={sorted(expected_paths - actual_paths)}, "
                f"unexpected={sorted(actual_paths - expected_paths)}"
            )
    observed: dict[str, bytes] = {}
    for relative_path in expected_paths:
        try:
            observed[relative_path] = strict_regular_file_bytes(
                root, relative_path
            )
        except FileNotFoundError as exc:
            raise ValueError(
                f"missing generated artifact: {relative_path}"
            ) from exc
    return observed


def validate_tree_readback(
    root: Path, outputs: dict[str, bytes], exact_inventory: bool
) -> None:
    observed = read_expected_tree(root, set(outputs), exact_inventory)
    drift = [
        relative_path
        for relative_path, expected in outputs.items()
        if observed[relative_path] != expected
    ]
    if drift:
        raise ValueError(f"generated byte drift: {sorted(drift)}")
    validate_generated_graph_bytes(observed)


def install_from_same_filesystem_stage(outputs: dict[str, bytes]) -> None:
    stage_root = Path(
        tempfile.mkdtemp(prefix=".prq002e-stage-", dir=REPOSITORY_ROOT)
    )
    try:
        write_staged_outputs(stage_root, outputs)
        validate_tree_readback(stage_root, outputs, exact_inventory=True)
        # Close the time-of-check/time-of-install gap for every retained source.
        verify_frozen_inputs()
        install_order = (
            [spec["output"] for spec in ALL_SCHEMA_SPECS]
            + [spec["fixture_output"] for spec in SCHEMA_SPECS]
            + [CORE_RECORD_PATH, EVIDENCE_RECORD_PATH, MIGRATION_RECORD_PATH]
        )
        if install_order[-1] != MIGRATION_RECORD_PATH:
            raise ValueError("migration record must install last")
        for relative_path in install_order:
            staged = stage_root / relative_path
            target = ensure_safe_install_target(
                REPOSITORY_ROOT, relative_path
            )
            os.replace(staged, target)
            with target.open("rb") as stream:
                os.fsync(stream.fileno())
            fsync_directory(target.parent)
        validate_tree_readback(REPOSITORY_ROOT, outputs, exact_inventory=False)
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="refuse drift; do not write generated artifacts",
    )
    args = parser.parse_args()
    verify_frozen_inputs()
    outputs = expected_outputs()
    validate_generated_graph_bytes(outputs)
    if args.check:
        try:
            validate_tree_readback(
                REPOSITORY_ROOT, outputs, exact_inventory=False
            )
        except ValueError as error:
            print(str(error), file=sys.stderr)
            return 1
    else:
        install_from_same_filesystem_stage(outputs)
    mode = "verified" if args.check else "wrote"
    print(f"{mode} {len(outputs)} deterministic PRQ-002E artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
