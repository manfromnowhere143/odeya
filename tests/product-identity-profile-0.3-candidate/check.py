#!/usr/bin/env python3
"""Fail-closed architecture evidence check for the odeya-jcs-0.3 candidate.

This checker verifies exact retained bytes and construction invariants.  It is
not a canonicalization implementation, a product-identity implementation, an
issuance mechanism, Gate A authority, or runtime authorization.
"""

from __future__ import annotations

import argparse
import copy
import decimal
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Protocol

from jsonschema import Draft202012Validator, FormatChecker, validators
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/product-identity-profile-0.3-candidate"
CASES_PATH = SUITE / "cases.json"
PREDECESSOR_PATH = SUITE / "predecessor-schemas.json"
INPUT_MANIFEST_PATH = SUITE / "input-manifest.json"
BASELINE_COMMIT = "617209ba480b854a00c6a15cd99ac1d5a18e90ad"
BASELINE_TREE = "67c38b895276bf2c804fe192339ce90a8c75ea97"
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.3"
PROFILE_VERSION = "0.3.0"
RAW_NUMBER_CONTRACT_ID = (
    "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
)
RAW_NUMBER_CONTRACT_PATH = (
    "architecture/canonicalization-raw-number-token-contract-v1-candidate.json"
)
RAW_NUMBER_CONTRACT_DIGEST = (
    "sha256:e2fcce22dc7570652f12e5dfb97860dcbe9b4af37bf56d810a5e499c3eddf6fc"
)
PROFILE_CORE_SCHEMA_ID = "urn:odeya:schema:canonicalization-profile-core:0.7.0"
JSON_SCHEMA_2020_12 = "https://json-schema.org/draft/2020-12/schema"
SUITE_ID = "prq-002e-profile-0.3-construction.0001"
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
CHALLENGE_RE = re.compile(r"^challenge-v1:[0-9a-f]{64}$")
OBSERVED_AT_RE = re.compile(
    r"^2026-07-29T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z$"
)
NUMBER_RE = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
)
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
DOMAIN_RE = re.compile(r"^odeya-[a-z0-9-]+-v[0-9]+$")
PROFILE_RE = re.compile(r"^urn:odeya:canonicalization:[a-z0-9.-]+$")

SCHEMA_ROWS = (
    (
        "schema_resource_record",
        "schemas/schema-resource-record-v0-2.schema.json",
        "urn:odeya:schema:schema-resource-record:0.2.0",
        "0.2.0",
        "product_member_schema",
        "odeya-schema-resource-record-v2",
    ),
    (
        "aggregate_state_subject_record",
        "schemas/aggregate-state-subject-record-v0-2.schema.json",
        "urn:odeya:schema:aggregate-state-subject-record:0.2.0",
        "0.2.0",
        "product_member_schema",
        "odeya-aggregate-state-subject-record-v2",
    ),
    (
        "reducer_contract_record",
        "schemas/reducer-contract-record-v0-2.schema.json",
        "urn:odeya:schema:reducer-contract-record:0.2.0",
        "0.2.0",
        "product_member_schema",
        "odeya-reducer-contract-record-v2",
    ),
    (
        "event_contract_record",
        "schemas/event-contract-record-v0-2.schema.json",
        "urn:odeya:schema:event-contract-record:0.2.0",
        "0.2.0",
        "product_member_schema",
        "odeya-event-contract-record-v2",
    ),
    (
        "ordered_member_map_commitment",
        "schemas/ordered-member-map-commitment-v0-2.schema.json",
        "urn:odeya:schema:ordered-member-map-commitment:0.2.0",
        "0.2.0",
        "product_commitment_schema",
        "odeya-ordered-member-map-commitment-v2",
    ),
    (
        "schema_registry_v0_9",
        "schemas/schema-registry-v0-9.schema.json",
        "urn:odeya:schema:schema-registry:0.9.0",
        "0.9.0",
        "product_registry_schema",
        "odeya-schema-registry-v3",
    ),
    (
        "aggregate_state_subject_registry_v0_8",
        "schemas/aggregate-state-subject-registry-v0-8.schema.json",
        "urn:odeya:schema:aggregate-state-subject-registry:0.8.0",
        "0.8.0",
        "product_registry_schema",
        "odeya-aggregate-state-subject-registry-v3",
    ),
    (
        "reducer_registry_v0_8",
        "schemas/reducer-registry-v0-8.schema.json",
        "urn:odeya:schema:reducer-registry:0.8.0",
        "0.8.0",
        "product_registry_schema",
        "odeya-reducer-registry-v3",
    ),
    (
        "event_contract_registry_v0_8",
        "schemas/event-contract-registry-v0-8.schema.json",
        "urn:odeya:schema:event-contract-registry:0.8.0",
        "0.8.0",
        "product_registry_schema",
        "odeya-event-contract-registry-v3",
    ),
    (
        "canonicalization_profile_core_v0_7",
        "schemas/canonicalization-profile-core-v0-7.schema.json",
        PROFILE_CORE_SCHEMA_ID,
        "0.7.0",
        "profile_core_schema",
        None,
    ),
    (
        "canonicalization_profile_candidate_evidence_v0_7",
        "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
        "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0",
        "0.7.0",
        "profile_evidence_schema",
        None,
    ),
    (
        "canonicalization_profile_migration_v0_2",
        "schemas/canonicalization-profile-migration-v0-2.schema.json",
        "urn:odeya:schema:canonicalization-profile-migration:0.2.0",
        "0.2.0",
        "profile_migration_schema",
        None,
    ),
)

CORE_PATH = "architecture/canonicalization-profile-core-0.3-candidate.json"
EVIDENCE_PATH = (
    "architecture/canonicalization-profile-0.3-candidate-evidence.json"
)
MIGRATION_PATH = (
    "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json"
)
RECORD_ROWS = (
    ("profile_core", CORE_PATH, SCHEMA_ROWS[9][1]),
    ("profile_evidence", EVIDENCE_PATH, SCHEMA_ROWS[10][1]),
    ("profile_migration", MIGRATION_PATH, SCHEMA_ROWS[11][1]),
)
EXPECTED_ARTIFACTS = (
    ("schema_resource_record_schema", SCHEMA_ROWS[0][1]),
    ("aggregate_state_subject_record_schema", SCHEMA_ROWS[1][1]),
    ("reducer_contract_record_schema", SCHEMA_ROWS[2][1]),
    ("event_contract_record_schema", SCHEMA_ROWS[3][1]),
    ("ordered_member_map_commitment_schema", SCHEMA_ROWS[4][1]),
    ("schema_registry_schema", SCHEMA_ROWS[5][1]),
    ("aggregate_state_subject_registry_schema", SCHEMA_ROWS[6][1]),
    ("reducer_registry_schema", SCHEMA_ROWS[7][1]),
    ("event_contract_registry_schema", SCHEMA_ROWS[8][1]),
    ("profile_core_schema", SCHEMA_ROWS[9][1]),
    ("profile_evidence_schema", SCHEMA_ROWS[10][1]),
    ("profile_migration_schema", SCHEMA_ROWS[11][1]),
    ("profile_core", CORE_PATH),
    ("profile_evidence", EVIDENCE_PATH),
    ("profile_migration", MIGRATION_PATH),
)
EXPECTED_DOMAINS = tuple(row[5] for row in SCHEMA_ROWS if row[5] is not None)
EXPECTED_GRAPH_NODES = tuple(
    [row[0] for row in SCHEMA_ROWS]
    + [
        "successor_profile_core_artifact",
        "successor_profile_evidence_artifact",
        "successor_profile_migration_artifact",
    ]
)
EXPECTED_GRAPH_EDGES = tuple(
    [
        ("schema_registry_v0_9", "ordered_member_map_commitment"),
        (
            "aggregate_state_subject_registry_v0_8",
            "ordered_member_map_commitment",
        ),
        ("reducer_registry_v0_8", "ordered_member_map_commitment"),
        ("event_contract_registry_v0_8", "ordered_member_map_commitment"),
    ]
    + [
        ("successor_profile_core_artifact", row[0])
        for row in SCHEMA_ROWS
    ]
    + [
        (
            "successor_profile_evidence_artifact",
            "successor_profile_core_artifact",
        ),
        (
            "successor_profile_migration_artifact",
            "successor_profile_evidence_artifact",
        ),
    ]
)
NUMBER_POLICY = {
    "contract_id": RAW_NUMBER_CONTRACT_ID,
    "contract_path": RAW_NUMBER_CONTRACT_PATH,
    "contract_raw_sha256": RAW_NUMBER_CONTRACT_DIGEST,
    "profile_id": PROFILE_ID,
    "profile_core_schema_id": PROFILE_CORE_SCHEMA_ID,
    "applicability": (
        "all resolved type-integer assertions and every recursively "
        "integer-valued const leaf"
    ),
    "integer_token_pattern": "^-?(?:0|[1-9][0-9]*)$",
    "integer_minimum_decimal": "-9007199254740991",
    "integer_maximum_decimal": "9007199254740991",
    "type_number_positions": "forbidden_in_exact_reissued_cohort",
    "unclassified_numeric_positions": "reject",
    "boolean_is_not_integer": True,
}

PYTHON_OBSERVER_ID = "python-stdlib-construction-observer.0001"
NODE_OBSERVER_ID = "nodejs-native-construction-observer.0001"
PYTHON_SOURCE_PATH = "tests/product-identity-profile-0.3-candidate/python/source-manifest.json"
NODE_SOURCE_PATH = "tests/product-identity-profile-0.3-candidate/node/source-manifest.json"
PYTHON_RESULT_PATH = "tests/product-identity-profile-0.3-candidate/results/python-construction-observation.json"
NODE_RESULT_PATH = "tests/product-identity-profile-0.3-candidate/results/node-construction-observation.json"
PYTHON_EXECUTION_PATH = "tests/product-identity-profile-0.3-candidate/results/python-execution-receipt.json"
NODE_EXECUTION_PATH = "tests/product-identity-profile-0.3-candidate/results/node-execution-receipt.json"
COMPARISON_PATH = "tests/product-identity-profile-0.3-candidate/results/comparison-receipt.json"
OBSERVER_EVIDENCE_PATHS = (
    PYTHON_SOURCE_PATH,
    NODE_SOURCE_PATH,
    PYTHON_RESULT_PATH,
    NODE_RESULT_PATH,
    PYTHON_EXECUTION_PATH,
    NODE_EXECUTION_PATH,
    COMPARISON_PATH,
)
PYTHON_SOURCE_INPUTS = (
    "tests/product-identity-profile-0.3-candidate/python/observer.py",
    "tests/product-identity-profile-0.3-candidate/python/dependency-lock.json",
)
NODE_SOURCE_INPUTS = (
    "tests/product-identity-profile-0.3-candidate/node/observer.mjs",
    "tests/product-identity-profile-0.3-candidate/node/package.json",
    "tests/product-identity-profile-0.3-candidate/node/package-lock.json",
)
PINNED_SOURCE_BINDINGS = {
    PYTHON_SOURCE_INPUTS[0]: {
        "repository_path": PYTHON_SOURCE_INPUTS[0],
        "raw_sha256": (
            "sha256:38db5ea3a2c4d111ce84b9013363de702c48336c7b328ca8c6e39f49259c6368"
        ),
        "byte_count": 12995,
    },
    PYTHON_SOURCE_INPUTS[1]: {
        "repository_path": PYTHON_SOURCE_INPUTS[1],
        "raw_sha256": (
            "sha256:15beef8354d29b2ef44cdb61706a148e54963fb043e686efb8ae3861829498ff"
        ),
        "byte_count": 367,
    },
    NODE_SOURCE_INPUTS[0]: {
        "repository_path": NODE_SOURCE_INPUTS[0],
        "raw_sha256": (
            "sha256:9189cefd44f6c4aa189a6aa30bcaa6ddeb2b71ea03edd5ad4f0c04256c01f42e"
        ),
        "byte_count": 15730,
    },
    NODE_SOURCE_INPUTS[1]: {
        "repository_path": NODE_SOURCE_INPUTS[1],
        "raw_sha256": (
            "sha256:11ab1e95acb1ff50d3df7c0851b9fbcc74f1b764fe92e0d481ccd3dffd59dec7"
        ),
        "byte_count": 231,
    },
    NODE_SOURCE_INPUTS[2]: {
        "repository_path": NODE_SOURCE_INPUTS[2],
        "raw_sha256": (
            "sha256:bbf630eb811f46bba3f2ea1c53aa34c7fc439cae2378f6d1d1d0cacaf819908f"
        ),
        "byte_count": 329,
    },
}
PINNED_RUNTIME = {
    PYTHON_OBSERVER_ID: {
        "family": "CPython",
        "version": "3.14.2",
        "resolved_executable_basename": "python3.14",
        "executable_binding": {
            "resolved_path_basename": "python3.14",
            "raw_sha256": (
                "sha256:3b6b69c61fd3765ab911d701cd17293b4a9154a0cb4973b546f05847f9a164c6"
            ),
            "byte_count": 52640,
        },
        "dependency_closure_complete": False,
    },
    NODE_OBSERVER_ID: {
        "family": "Node.js",
        "version": "24.18.0",
        "resolved_executable_basename": "node",
        "executable_binding": {
            "resolved_path_basename": "node",
            "raw_sha256": (
                "sha256:ee6fb0e015284d83a91e8ec5213f43a157f8a392b58555301682892ba928c04a"
            ),
            "byte_count": 120965360,
        },
        "dependency_closure_complete": False,
    },
}
EXPECTED_PYTHON_DEPENDENCY_LOCK = {
    "schema_version": "0.1.0",
    "artifact_class": "observer_dependency_lock",
    "suite_id": SUITE_ID,
    "observer_id": PYTHON_OBSERVER_ID,
    "runtime_family": "CPython",
    "runtime_version": "3.14.2",
    "third_party_dependency_count": 0,
    "third_party_dependencies": [],
    "network_install_required": False,
}
EXPECTED_NODE_PACKAGE = {
    "name": "odeya-prq-002e-profile-0-3-construction-observer",
    "version": "0.0.0-private",
    "private": True,
    "type": "module",
    "engines": {"node": "24.18.0"},
    "scripts": {"observe": "node observer.mjs"},
}
EXPECTED_NODE_LOCK = {
    "name": "odeya-prq-002e-profile-0-3-construction-observer",
    "version": "0.0.0-private",
    "lockfileVersion": 3,
    "requires": True,
    "packages": {
        "": {
            "name": "odeya-prq-002e-profile-0-3-construction-observer",
            "version": "0.0.0-private",
            "engines": {"node": "24.18.0"},
        }
    },
}

EXPECTED_ADVERSARIAL_CLASSES = (
    "predecessor_lineage",
    "successor_identity_and_census",
    "numeric_applicability",
    "digest_dependency_dag",
    "migration_and_resolver",
    "observer_graph",
    "authority_nonclaims",
)


class RepositoryPathError(ValueError):
    """Raised when a repository artifact is not a contained regular file."""


def normalize_repository_path(relative: str) -> str:
    """Return one closed POSIX repository-relative path."""

    if not isinstance(relative, str) or not relative:
        raise RepositoryPathError("repository path must be a nonempty string")
    candidate = Path(relative)
    if (
        candidate.is_absolute()
        or "\x00" in relative
        or "\\" in relative
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or candidate.as_posix() != relative
    ):
        raise RepositoryPathError(f"unsafe repository path: {relative!r}")
    return relative


def strict_repository_file_bytes(root: Path, relative: str) -> bytes:
    """Read a contained non-symlink regular file through a no-follow handle."""

    relative = normalize_repository_path(relative)
    root_stat = root.lstat()
    if root.is_symlink() or not stat.S_ISDIR(root_stat.st_mode):
        raise RepositoryPathError("repository root is not a non-symlink directory")
    root_resolved = root.resolve(strict=True)
    candidate = root.joinpath(*Path(relative).parts)
    current = root
    for part in Path(relative).parts[:-1]:
        current = current / part
        current_stat = current.lstat()
        if current.is_symlink() or not stat.S_ISDIR(current_stat.st_mode):
            raise RepositoryPathError(
                f"repository parent is not a non-symlink directory: {relative}"
            )
    lexical_stat = candidate.lstat()
    if candidate.is_symlink() or not stat.S_ISREG(lexical_stat.st_mode):
        raise RepositoryPathError(
            f"repository artifact is not a non-symlink regular file: {relative}"
        )
    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise RepositoryPathError(
            f"repository artifact resolves outside the repository: {relative}"
        ) from exc
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(candidate, flags)
    try:
        opened_stat = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened_stat.st_mode)
            or (opened_stat.st_dev, opened_stat.st_ino)
            != (lexical_stat.st_dev, lexical_stat.st_ino)
        ):
            raise RepositoryPathError(
                f"repository artifact changed before open: {relative}"
            )
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
            raise RepositoryPathError(
                f"repository artifact changed during read: {relative}"
            )
        return b"".join(chunks)
    finally:
        os.close(descriptor)


class RepositoryView(Protocol):
    """Read-only artifact view consumed by every production validator."""

    def read_bytes(self, relative: str) -> bytes: ...

    def is_regular_file(self, relative: str) -> bool: ...

    def list_regular_files(self, directory: str, suffix: str) -> list[str]: ...


class FilesystemRepositoryView:
    """Strict live repository view."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def read_bytes(self, relative: str) -> bytes:
        return strict_repository_file_bytes(self.root, relative)

    def is_regular_file(self, relative: str) -> bool:
        try:
            self.read_bytes(relative)
        except (OSError, RepositoryPathError):
            return False
        return True

    def list_regular_files(self, directory: str, suffix: str) -> list[str]:
        directory = normalize_repository_path(directory)
        directory_path = self.root.joinpath(*Path(directory).parts)
        directory_stat = directory_path.lstat()
        if directory_path.is_symlink() or not stat.S_ISDIR(directory_stat.st_mode):
            raise RepositoryPathError(
                f"repository directory is not a non-symlink directory: {directory}"
            )
        rows: list[str] = []
        for path in directory_path.iterdir():
            if not path.name.endswith(suffix):
                continue
            relative = path.relative_to(self.root).as_posix()
            self.read_bytes(relative)
            rows.append(relative)
        return sorted(rows)


@dataclass(frozen=True)
class OverlayEntry:
    """One isolated artifact-byte or path-state replacement."""

    kind: str
    raw: bytes | None = None


class OverlayRepositoryView:
    """In-memory isolated view layered over the strict live repository."""

    def __init__(
        self,
        base: RepositoryView,
        entries: dict[str, OverlayEntry] | None = None,
    ) -> None:
        self.base = base
        self.entries = {
            normalize_repository_path(path): entry
            for path, entry in (entries or {}).items()
        }

    def clone(self) -> "OverlayRepositoryView":
        return OverlayRepositoryView(self.base, dict(self.entries))

    def replace_bytes(self, relative: str, raw: bytes) -> None:
        self.entries[normalize_repository_path(relative)] = OverlayEntry(
            "regular", raw
        )

    def mark_missing(self, relative: str) -> None:
        self.entries[normalize_repository_path(relative)] = OverlayEntry(
            "missing"
        )

    def mark_symlink(self, relative: str) -> None:
        self.entries[normalize_repository_path(relative)] = OverlayEntry(
            "symlink"
        )

    def read_bytes(self, relative: str) -> bytes:
        relative = normalize_repository_path(relative)
        entry = self.entries.get(relative)
        if entry is None:
            return self.base.read_bytes(relative)
        if entry.kind == "missing":
            raise FileNotFoundError(relative)
        if entry.kind == "symlink":
            raise RepositoryPathError(
                f"repository artifact is not a non-symlink regular file: {relative}"
            )
        if entry.kind != "regular" or entry.raw is None:
            raise RepositoryPathError(f"invalid overlay entry: {relative}")
        return entry.raw

    def is_regular_file(self, relative: str) -> bool:
        try:
            self.read_bytes(relative)
        except (OSError, RepositoryPathError):
            return False
        return True

    def list_regular_files(self, directory: str, suffix: str) -> list[str]:
        directory = normalize_repository_path(directory)
        rows = set(self.base.list_regular_files(directory, suffix))
        prefix = directory + "/"
        for relative, entry in self.entries.items():
            if (
                not relative.startswith(prefix)
                or "/" in relative[len(prefix) :]
                or not relative.endswith(suffix)
            ):
                continue
            if entry.kind == "missing":
                rows.discard(relative)
            elif entry.kind == "symlink":
                raise RepositoryPathError(
                    f"repository artifact is not a non-symlink regular file: "
                    f"{relative}"
                )
            elif entry.kind == "regular":
                rows.add(relative)
            else:
                raise RepositoryPathError(f"invalid overlay entry: {relative}")
        return sorted(rows)


LIVE_VIEW = FilesystemRepositoryView(ROOT)
ACTIVE_VIEW: RepositoryView = LIVE_VIEW


class DuplicateKey(ValueError):
    """Raised before mapping construction can erase a duplicate key."""


class Findings:
    """Stable guard codes with bounded diagnostics."""

    def __init__(self) -> None:
        self._items: dict[str, list[str]] = {}

    def add(self, code: str, detail: str) -> None:
        self._items.setdefault(code, []).append(detail)

    def codes(self) -> set[str]:
        return set(self._items)

    def merge(self, other: "Findings") -> None:
        for code, details in other._items.items():
            for detail in details:
                self.add(code, detail)

    def __bool__(self) -> bool:
        return bool(self._items)

    def lines(self) -> Iterable[str]:
        for code in sorted(self._items):
            for detail in sorted(set(self._items[code])):
                yield f"{code}: {detail}"


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_nonfinite(token: str) -> Any:
    raise ValueError(f"non-finite JSON token is forbidden: {token}")


def parse_decimal(token: str) -> decimal.Decimal:
    value = decimal.Decimal(token)
    if not value.is_finite():
        raise ValueError(f"non-finite JSON number is forbidden: {token}")
    return value


def parse_json(raw: bytes, label: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"{label}: UTF-8 BOM is forbidden")
    text = raw.decode("utf-8", errors="strict")
    return json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_float=parse_decimal,
        parse_constant=reject_nonfinite,
    )


def repository_relative(path: Path | str) -> str:
    if isinstance(path, str):
        return normalize_repository_path(path)
    try:
        relative = path.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise RepositoryPathError(
            f"path is outside the repository: {path}"
        ) from exc
    return normalize_repository_path(relative)


def load_object(path: Path | str) -> tuple[dict[str, Any], bytes]:
    relative = repository_relative(path)
    raw = ACTIVE_VIEW.read_bytes(relative)
    value = parse_json(raw, relative)
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: root must be an object")
    return value, raw


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(relative: str) -> dict[str, Any]:
    relative = normalize_repository_path(relative)
    raw = ACTIVE_VIEW.read_bytes(relative)
    return {
        "repository_path": relative,
        "raw_sha256": sha256(raw),
        "byte_count": len(raw),
    }


def compact_bytes(value: Any, *, ascii_only: bool = False, lf: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        ensure_ascii=ascii_only,
        separators=(",", ":"),
        sort_keys=ascii_only,
        allow_nan=False,
    ).encode("utf-8")
    return encoded + (b"\n" if lf else b"")


def json_type_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            json_type_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            json_type_equal(a, b)
            for a, b in zip(left, right, strict=True)
        )
    return left == right


def exact_const(
    validator: Any,
    expected: Any,
    instance: Any,
    schema: dict[str, Any],
) -> Iterable[ValidationError]:
    del validator, schema
    if not json_type_equal(instance, expected):
        yield ValidationError(
            f"{instance!r} is not the exact JSON-typed const {expected!r}"
        )


def exact_enum(
    validator: Any,
    options: list[Any],
    instance: Any,
    schema: dict[str, Any],
) -> Iterable[ValidationError]:
    del validator, schema
    if not any(json_type_equal(instance, option) for option in options):
        yield ValidationError(
            f"{instance!r} is not an exact JSON-typed enum member"
        )


EXACT_TYPE_CHECKER = Draft202012Validator.TYPE_CHECKER.redefine(
    "integer", lambda _checker, instance: type(instance) is int
).redefine(
    "number",
    lambda _checker, instance: (
        type(instance) is int or type(instance) is decimal.Decimal
    ),
)
ExactDraft202012Validator = validators.extend(
    Draft202012Validator,
    validators={"const": exact_const, "enum": exact_enum},
    type_checker=EXACT_TYPE_CHECKER,
)


def pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def iter_locations(value: Any, pointer: str = "") -> Iterable[tuple[str, Any]]:
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_locations(
                child, f"{pointer}/{pointer_escape(key)}"
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_locations(child, f"{pointer}/{index}")


def raw_number_tokens(raw: bytes) -> list[str]:
    text = raw.decode("utf-8", errors="strict")
    tokens: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        character = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            index += 1
            continue
        if character == "-" or character.isdigit():
            match = NUMBER_RE.match(text, index)
            if match is None:
                raise ValueError(
                    f"unclassified numeric-looking character at offset {index}"
                )
            tokens.append(match.group(0))
            index = match.end()
            continue
        index += 1
    if in_string or escaped:
        raise ValueError("unterminated JSON string during number scan")
    return tokens


def numeric_document_tokens(document: Any, raw: bytes) -> list[dict[str, str]]:
    tokens = raw_number_tokens(raw)
    located = [
        {
            "document_pointer": pointer,
            "raw_lexeme": str(value),
            "decimal_value": str(value),
        }
        for pointer, value in iter_locations(document)
        if type(value) is int
    ]
    if [row["raw_lexeme"] for row in located] != tokens:
        raise ValueError(
            "raw number lexemes are not all integer tokens in document order"
        )
    for token in tokens:
        if not INTEGER_RE.fullmatch(token):
            raise ValueError(f"non-integer raw number token: {token}")
        integer = int(token)
        if not MIN_SAFE_INTEGER <= integer <= MAX_SAFE_INTEGER:
            raise ValueError(f"raw integer is outside the safe domain: {token}")
    return located


def resolve_pointer(document: Any, fragment: str) -> Any:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        raise ValueError(f"unsupported reference fragment: {fragment}")
    current = document
    for encoded in fragment[2:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list):
            current = current[int(token)]
        else:
            raise ValueError(f"unresolved reference fragment: {fragment}")
    return current


def collect_integer_const_leaves(
    value: Any, schema_location: str
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_pointer, child in iter_locations(value):
        if type(child) is int:
            if not MIN_SAFE_INTEGER <= child <= MAX_SAFE_INTEGER:
                raise ValueError(
                    f"integer const outside safe domain: {schema_location}"
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


def expanded_numeric_positions(
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
        if type(value) is int:
            if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
                raise ValueError(
                    f"integer const outside safe domain: {keyword_location}"
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
        resolved_digest = sha256(resolved_raw)
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
        if "enum" in node and any(type(item) is int for item in node["enum"]):
            if node_type != "integer":
                unclassified.append(
                    f"{resolved_schema_id}#{schema_pointer}/enum"
                )

        reference = node.get("$ref")
        if isinstance(reference, str):
            target_id, separator, suffix = reference.partition("#")
            target_id = target_id or resolved_schema_id
            if target_id not in by_id:
                raise ValueError(
                    f"unresolved exact-cohort reference: {reference}"
                )
            fragment = f"#{suffix}" if separator else ""
            ref_key = (target_id, fragment or "#")
            if ref_key in ref_stack:
                raise ValueError(
                    f"numeric applicability reference cycle: {reference}"
                )
            _, target_document, _ = by_id[target_id]
            descend(
                target_id,
                resolve_pointer(target_document, fragment),
                fragment[1:] if fragment else "",
                [*evaluation_path, {"kind": "ref", "token": reference}],
                (*ref_stack, ref_key),
            )

        mapping_keywords = {
            "properties": "property",
            "patternProperties": "pattern_property",
            "dependentSchemas": "dependent_schema",
        }
        for keyword, kind in mapping_keywords.items():
            children = node.get(keyword)
            if isinstance(children, dict):
                for name, child in children.items():
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
            if isinstance(child, (dict, bool)) and child is not False:
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
            marker = compact_bytes(row)
            if marker not in seen:
                seen.add(marker)
                result.append(row)
        return result

    return (
        deduplicate(integer_types),
        deduplicate(integer_consts),
        sorted(set(unclassified)),
    )


def derive_static_inventory(
    schema_documents: dict[str, tuple[dict[str, Any], bytes]],
) -> dict[str, Any]:
    by_id = {
        document["$id"]: (path, document, raw)
        for path, (document, raw) in schema_documents.items()
    }
    expected_ids = {row[2] for row in SCHEMA_ROWS}
    if set(by_id) != expected_ids:
        raise ValueError("exact schema ID cohort differs")
    rows: list[dict[str, Any]] = []

    for _, path, expected_id, _, _, _ in SCHEMA_ROWS:
        document, raw = schema_documents[path]
        schema_id = document["$id"]
        if schema_id != expected_id:
            raise ValueError(f"{path}: schema ID drift")
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
            if "enum" in node and any(
                type(item) is int for item in node["enum"]
            ):
                if node_type != "integer":
                    unclassified.append(f"{schema_id}#{pointer}/enum")
            numeric_keywords = {
                "minimum",
                "maximum",
                "exclusiveMinimum",
                "exclusiveMaximum",
                "multipleOf",
            }
            if numeric_keywords.intersection(node) and node_type not in (
                "integer",
                "number",
            ):
                unclassified.append(f"{schema_id}#{pointer}")
            if "$dynamicRef" in node or "$recursiveRef" in node:
                raise ValueError(
                    f"{path}: dynamic/recursive reference is outside this inventory"
                )
            reference = node.get("$ref")
            if isinstance(reference, str):
                target_id, separator, suffix = reference.partition("#")
                resolved_id = target_id or schema_id
                if resolved_id not in by_id:
                    raise ValueError(
                        f"{path}: unresolved exact-cohort reference {reference}"
                    )
                target_path, target_document, target_raw = by_id[resolved_id]
                fragment = f"#{suffix}" if separator else ""
                resolve_pointer(target_document, fragment)
                reference_edges.append(
                    {
                        "source_schema_location": (
                            f"{schema_id}#{pointer}/$ref"
                        ),
                        "target_schema_id": resolved_id,
                        "target_schema_raw_digest": sha256(target_raw),
                        "target_schema_path": target_path,
                        "target_fragment": fragment or "#",
                    }
                )
            for key, child in node.items():
                if (
                    key in {"const", "enum", "examples", "default"}
                    or key.startswith("x-")
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
            expanded_numeric_positions(schema_id, by_id)
        )
        if (
            type_numbers
            or number_unions
            or unclassified
            or expanded_unclassified
        ):
            raise ValueError(
                f"{path}: unsupported numeric position: "
                f"type_number={type_numbers}, unions={number_unions}, "
                f"unclassified={unclassified + expanded_unclassified}"
            )
        document_tokens = numeric_document_tokens(document, raw)
        token_digest = sha256(compact_bytes(document_tokens))
        position_projection = {
            "integer_type_assertions": integer_types,
            "integer_const_leaves": integer_consts,
            "expanded_instance_integer_type_positions": expanded_types,
            "expanded_instance_integer_const_positions": expanded_consts,
            "resolved_reference_edges": reference_edges,
        }
        rows.append(
            {
                "schema_path": path,
                "schema_id": schema_id,
                "schema_raw_digest": sha256(raw),
                "schema_byte_count": len(raw),
                "schema_document_numeric_literals_are_instance_positions": False,
                "schema_document_numeric_token_count": len(document_tokens),
                "schema_document_number_tokens": document_tokens,
                "schema_document_numeric_token_inventory_sha256": token_digest,
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
                "position_inventory_sha256": sha256(
                    compact_bytes(position_projection)
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


def recursive_values_for_key(value: Any, wanted: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == wanted:
                found.append(child)
            found.extend(recursive_values_for_key(child, wanted))
    elif isinstance(value, list):
        for child in value:
            found.extend(recursive_values_for_key(child, wanted))
    return found


def recursive_string_values(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str):
        found.add(value)
    elif isinstance(value, dict):
        for child in value.values():
            found.update(recursive_string_values(child))
    elif isinstance(value, list):
        for child in value:
            found.update(recursive_string_values(child))
    return found


def declared_domain_separators(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            domain_contract = properties.get("domain_separator")
            if (
                isinstance(domain_contract, dict)
                and isinstance(domain_contract.get("const"), str)
                and DOMAIN_RE.fullmatch(domain_contract["const"])
            ):
                found.append(domain_contract["const"])
        for child in value.values():
            found.extend(declared_domain_separators(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(declared_domain_separators(child))
    return found


def schema_bindings() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for binding_id, path, schema_id, _, role, _ in SCHEMA_ROWS:
        raw = ACTIVE_VIEW.read_bytes(path)
        result.append(
            {
                "binding_id": binding_id,
                "path": path,
                "schema_id": schema_id,
                "raw_digest": sha256(raw),
                "byte_count": len(raw),
                "resource_role": role,
            }
        )
    return result


def graph_has_cycle(nodes: list[str], edges: list[tuple[str, str]]) -> bool:
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
        if any(visit(child) for child in adjacency[node]):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in adjacency)


def git_bytes(*arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(arguments)} failed: "
            f"{completed.stderr.decode('utf-8', 'replace')[:300]}"
        )
    return completed.stdout


def validate_predecessor(
    predecessor: dict[str, Any], findings: Findings
) -> list[list[Any]]:
    expected_keys = {
        "schema_version",
        "artifact_class",
        "source_commit",
        "source_tree",
        "row_shape",
        "schema_path_count",
        "ordered_row_corpus_sha256",
        "schemas",
    }
    if set(predecessor) != expected_keys:
        findings.add(
            "predecessor_byte_binding_mismatch",
            "predecessor manifest member inventory differs",
        )
        return []
    expected_scalars = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002e_frozen_predecessor_schema_manifest",
        "source_commit": BASELINE_COMMIT,
        "source_tree": BASELINE_TREE,
        "row_shape": ["path", "schema_id", "raw_digest", "byte_count"],
        "schema_path_count": 132,
    }
    if any(
        not json_type_equal(predecessor.get(key), value)
        for key, value in expected_scalars.items()
    ):
        findings.add(
            "predecessor_byte_binding_mismatch",
            "predecessor manifest identity/count contract differs",
        )
    rows = predecessor.get("schemas")
    if (
        not isinstance(rows, list)
        or len(rows) != 132
        or any(
            not isinstance(row, list)
            or len(row) != 4
            or not all(isinstance(item, str) for item in row[:3])
            or type(row[3]) is not int
            for row in rows
        )
    ):
        findings.add(
            "predecessor_byte_binding_mismatch",
            "predecessor row shape or 132-row count differs",
        )
        return []
    paths = [row[0] for row in rows]
    ids = [row[1] for row in rows]
    if paths != sorted(paths) or len(set(paths)) != 132 or len(set(ids)) != 132:
        findings.add(
            "predecessor_byte_binding_mismatch",
            "predecessor paths/IDs are not sorted and unique",
        )
    corpus = compact_bytes(rows) + b"\n"
    if predecessor.get("ordered_row_corpus_sha256") != sha256(corpus):
        findings.add(
            "predecessor_byte_binding_mismatch",
            "ordered predecessor row corpus digest differs",
        )
    try:
        commit = git_bytes("rev-parse", BASELINE_COMMIT).decode().strip()
        tree = git_bytes(
            "rev-parse", f"{BASELINE_COMMIT}^{{tree}}"
        ).decode().strip()
        baseline_paths = [
            line
            for line in git_bytes(
                "ls-tree",
                "-r",
                "--name-only",
                BASELINE_COMMIT,
                "--",
                "schemas",
            )
            .decode("utf-8")
            .splitlines()
            if line.endswith(".schema.json")
        ]
    except (RuntimeError, UnicodeError) as exc:
        findings.add("predecessor_byte_binding_mismatch", str(exc))
        return rows
    if (
        commit != BASELINE_COMMIT
        or tree != BASELINE_TREE
        or baseline_paths != paths
    ):
        findings.add(
            "predecessor_byte_binding_mismatch",
            "baseline commit/tree/schema path inventory differs",
        )
        return rows
    for path, schema_id, expected_digest, expected_count in rows:
        try:
            frozen = git_bytes("show", f"{BASELINE_COMMIT}:{path}")
            live = ACTIVE_VIEW.read_bytes(path)
            document = parse_json(frozen, f"{BASELINE_COMMIT}:{path}")
        except (RuntimeError, OSError, ValueError) as exc:
            findings.add(
                "predecessor_byte_binding_mismatch", f"{path}: {exc}"
            )
            continue
        if (
            sha256(frozen) != expected_digest
            or len(frozen) != expected_count
            or frozen != live
            or not isinstance(document, dict)
            or document.get("$id") != schema_id
        ):
            findings.add(
                "predecessor_byte_binding_mismatch",
                f"{path}: retained or live exact bytes differ",
            )
    return rows


def validate_schema_cohort(
    predecessor_rows: list[list[Any]], findings: Findings
) -> tuple[
    dict[str, tuple[dict[str, Any], bytes]],
    Registry[Any],
    dict[str, Any] | None,
]:
    entry_codes = findings.codes()
    schema_documents: dict[str, tuple[dict[str, Any], bytes]] = {}
    successor_paths = [row[1] for row in SCHEMA_ROWS]
    predecessor_paths = [row[0] for row in predecessor_rows]
    try:
        actual_paths = ACTIVE_VIEW.list_regular_files(
            "schemas", ".schema.json"
        )
    except (OSError, RepositoryPathError) as exc:
        findings.add("successor_schema_cohort_mismatch", str(exc))
        actual_paths = []
    if (
        len(predecessor_paths) != 132
        or set(predecessor_paths).intersection(successor_paths)
        or actual_paths != sorted([*predecessor_paths, *successor_paths])
        or len(actual_paths) != 144
    ):
        findings.add(
            "successor_schema_cohort_mismatch",
            "exact disjoint 132+12=144 schema census differs",
        )

    registry: Registry[Any] = Registry()
    ids: set[str] = set()
    for (
        _binding_id,
        path,
        expected_id,
        expected_version,
        _role,
        expected_domain,
    ) in SCHEMA_ROWS:
        try:
            document, raw = load_object(ROOT / path)
        except (OSError, ValueError) as exc:
            findings.add("successor_schema_cohort_mismatch", f"{path}: {exc}")
            continue
        schema_documents[path] = (document, raw)
        if (
            document.get("$schema") != JSON_SCHEMA_2020_12
            or document.get("$id") != expected_id
            or expected_id in ids
            or document.get("properties", {}).get("schema_version")
            != {"const": expected_version}
        ):
            findings.add(
                "successor_resource_identity_mismatch",
                f"{path}: $schema/$id/version identity differs",
            )
        ids.add(expected_id)
        if not json_type_equal(
            document.get("x-odeya-number-token-policy"), NUMBER_POLICY
        ):
            findings.add(
                "successor_profile_annotation_mismatch",
                f"{path}: raw-number/profile annotation differs",
            )
        declared_domains = declared_domain_separators(document)
        if expected_domain is not None and set(declared_domains) != {
            expected_domain
        }:
            findings.add(
                "successor_domain_inventory_mismatch",
                f"{path}: successor domain is absent or not exclusive",
            )
        for declared_type in recursive_values_for_key(document, "type"):
            if declared_type == "number":
                findings.add(
                    "type_number_position_forbidden",
                    f"{path}: literal type:number exists",
                )
            if (
                isinstance(declared_type, list)
                and "number" in declared_type
            ):
                findings.add(
                    "number_admitting_union_forbidden",
                    f"{path}: type union admits number",
                )
        integer_token_policy_failed = False
        try:
            numeric_document_tokens(document, raw)
        except ValueError as exc:
            integer_token_policy_failed = True
            findings.add(
                "integer_raw_token_policy_violation", f"{path}: {exc}"
            )
        try:
            Draft202012Validator.check_schema(document)
            registry = registry.with_resource(
                expected_id, Resource.from_contents(document)
            )
        except Exception as exc:
            if not integer_token_policy_failed:
                findings.add(
                    "closed_schema_validation_failed",
                    f"{path}: meta-schema validation failed: {exc}",
                )

    inventory: dict[str, Any] | None = None
    if len(schema_documents) == 12 and findings.codes() == entry_codes:
        try:
            inventory = derive_static_inventory(schema_documents)
        except Exception as exc:
            findings.add(
                "static_numeric_inventory_mismatch",
                f"independent static derivation failed: {exc}",
            )
    return schema_documents, registry, inventory


def validate_instance(
    instance: dict[str, Any],
    schema: dict[str, Any],
    registry: Registry[Any],
    label: str,
    findings: Findings,
) -> None:
    try:
        errors = sorted(
            ExactDraft202012Validator(
                schema,
                registry=registry,
                format_checker=FormatChecker(),
            ).iter_errors(instance),
            key=lambda error: [str(item) for item in error.absolute_path],
        )
    except Exception as exc:
        findings.add(
            "closed_schema_validation_failed",
            f"{label}: closed evaluation failed: {exc}",
        )
        return
    if errors:
        rendered = "; ".join(error.message for error in errors[:3])
        findings.add(
            "closed_schema_validation_failed", f"{label}: {rendered}"
        )


def validate_records(
    schema_documents: dict[str, tuple[dict[str, Any], bytes]],
    registry: Registry[Any],
    inventory: dict[str, Any] | None,
    predecessor_rows: list[list[Any]],
    findings: Findings,
) -> dict[str, tuple[dict[str, Any], bytes]]:
    records: dict[str, tuple[dict[str, Any], bytes]] = {}
    for _role, path, schema_path in RECORD_ROWS:
        try:
            document, raw = load_object(ROOT / path)
            numeric_document_tokens(document, raw)
        except (OSError, ValueError) as exc:
            findings.add("record_exact_byte_binding_mismatch", f"{path}: {exc}")
            continue
        records[path] = (document, raw)
        if schema_path in schema_documents:
            validate_instance(
                document,
                schema_documents[schema_path][0],
                registry,
                path,
                findings,
            )

    if len(records) != 3 or inventory is None:
        return records
    core, core_raw = records[CORE_PATH]
    evidence, evidence_raw = records[EVIDENCE_PATH]
    migration, migration_raw = records[MIGRATION_PATH]
    expected_bindings = schema_bindings()

    if (
        core.get("profile_id") != PROFILE_ID
        or core.get("profile_version") != PROFILE_VERSION
        or core.get("candidate_status")
        != "scoped_successor_candidate_unissued_unadmitted_no_product_digests"
        or not json_type_equal(
            core.get("successor_schema_bindings"), expected_bindings
        )
    ):
        findings.add(
            "record_exact_byte_binding_mismatch",
            "core identity/status/successor bindings differ",
        )
    if not json_type_equal(
        core.get("static_numeric_applicability_inventory"), inventory
    ):
        findings.add(
            "static_numeric_inventory_mismatch",
            "core static inventory differs from independent derivation",
        )
    expected_domain_registry = [
        {
            "domain_separator": domain,
            "subject_class": (
                row[0]
                if "registry" not in row[0]
                else row[0].removesuffix("_v0_9").removesuffix("_v0_8")
            ),
            "declaring_schema_binding_id": row[0],
            "registration_status": (
                "scoped_successor_candidate_unissued_unadmitted"
            ),
        }
        for row in SCHEMA_ROWS
        for domain in [row[5]]
        if domain is not None
    ]
    if not json_type_equal(
        core.get("domain_registry"), expected_domain_registry
    ):
        findings.add(
            "successor_domain_inventory_mismatch",
            "core nine-domain registry differs",
        )

    graph = core.get("digest_dependency_graph")
    graph_edges: list[tuple[str, str]] = []
    if isinstance(graph, dict) and isinstance(graph.get("edges"), list):
        graph_edges = [
            (edge.get("subject"), edge.get("dependency"))
            for edge in graph["edges"]
            if isinstance(edge, dict)
        ]
    expected_graph_flags = {
        "edge_direction": "subject_to_exact_dependency",
        "node_ids_unique": True,
        "self_edges_allowed": False,
        "cycles_allowed": False,
        "core_raw_digest_inside_core": False,
        "evidence_depends_on_migration_record_digest": False,
        "migration_depends_on_evidence_record": True,
        "downstream_trace_inside_subject": False,
        "cross_resource_schema_reference_cycles_allowed": False,
    }
    observed_graph_flags = {
        key: graph.get(key) if isinstance(graph, dict) else None
        for key in expected_graph_flags
    }
    nodes = graph.get("nodes") if isinstance(graph, dict) else None
    if (
        not isinstance(nodes, list)
        or not json_type_equal(nodes, list(EXPECTED_GRAPH_NODES))
        or not json_type_equal(
            graph_edges, list(EXPECTED_GRAPH_EDGES)
        )
        or not json_type_equal(observed_graph_flags, expected_graph_flags)
        or any(subject == dependency for subject, dependency in graph_edges)
        or graph_has_cycle(nodes, graph_edges)
    ):
        findings.add(
            "digest_dependency_dag_mismatch",
            "exact schemas→core→evidence→migration DAG differs",
        )

    evidence_expected_core = {
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "profile_core_path": CORE_PATH,
        "profile_core_schema_path": SCHEMA_ROWS[9][1],
        "profile_core_schema_id": SCHEMA_ROWS[9][2],
        "profile_core_raw_digest": sha256(core_raw),
        "profile_core_byte_count": len(core_raw),
        "profile_core_schema_raw_digest": sha256(
            schema_documents[SCHEMA_ROWS[9][1]][1]
        ),
        "profile_core_schema_byte_count": len(
            schema_documents[SCHEMA_ROWS[9][1]][1]
        ),
        "core_contains_self_hash": False,
        "binding_is_external_to_core": True,
        "binding_status": "exact_candidate_bytes_unissued_unadmitted",
    }
    if (
        not json_type_equal(
            evidence.get("profile_core_binding"), evidence_expected_core
        )
        or not json_type_equal(
            evidence.get("successor_schema_bindings"), expected_bindings
        )
        or not json_type_equal(
            evidence.get("static_numeric_applicability_inventory"), inventory
        )
    ):
        findings.add(
            "record_exact_byte_binding_mismatch",
            "evidence core/schema/static bindings differ",
        )
    expected_domains = {
        "declared_domain_count": 9,
        "domain_constants_unique": True,
        "domain_separators": list(EXPECTED_DOMAINS),
        "domains_are_scoped_to_successor_resources": True,
        "current_consumers_admitted": False,
    }
    if not json_type_equal(
        evidence.get("declared_domain_inventory"), expected_domains
    ):
        findings.add(
            "successor_domain_inventory_mismatch",
            "evidence domain inventory differs",
        )
    expected_offline = {
        "resolver_mode": (
            "repository_local_exact_id_raw_digest_and_byte_count_only"
        ),
        "predecessor_bytes_materialized": True,
        "successor_schema_bytes_materialized": True,
        "complete_offline_schema_registry": False,
        "historical_reissue_predecessor_bytes_materialized_in_current_tree": False,
        "git_object_reachability_is_durable_retention_proof": False,
        "external_content_addressed_archive_verified": False,
        "unresolved_historical_resource_count": None,
        "missing_count_must_not_be_interpreted_as_zero": True,
        "network_file_search_environment_or_mutable_fallback": "disabled",
        "resolution_status": (
            "incomplete_blocking_before_migration_admission_or_gate_a"
        ),
    }
    if not json_type_equal(
        evidence.get("offline_resolver_observation"), expected_offline
    ):
        findings.add(
            "offline_resolver_boundary_mismatch",
            "incomplete resolver/null boundary differs",
        )
    expected_conformance = {
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
    }
    if not json_type_equal(
        evidence.get("conformance_evidence"), expected_conformance
    ):
        findings.add(
            "conformance_claim_escalated",
            "null/false conformance boundary differs",
        )

    disposition_rows = migration.get("resource_dispositions")
    disposition_successors = (
        [row.get("successor") for row in disposition_rows]
        if isinstance(disposition_rows, list)
        and all(isinstance(row, dict) for row in disposition_rows)
        else []
    )
    expected_successors = [
        {
            "path": row["path"],
            "schema_id": row["schema_id"],
            "raw_digest": row["raw_digest"],
            "byte_count": row["byte_count"],
        }
        for row in expected_bindings
    ]
    if (
        not isinstance(disposition_rows, list)
        or len(disposition_rows) != 12
        or not json_type_equal(disposition_successors, expected_successors)
        or any(
            row.get("action")
            != "add_new_side_by_side_unissued_resource"
            or row.get("digest_or_identity_inheritance_allowed") is not False
            or row.get(
                "issued_predecessor_claimed_within_measured_input"
            )
            is not False
            for row in disposition_rows
        )
    ):
        findings.add(
            "migration_disposition_mismatch",
            "exact twelve successor dispositions or false inheritance differ",
        )
    predecessor_by_path = {
        row[0]: {
            "path": row[0],
            "schema_id": row[1],
            "raw_digest": row[2],
            "byte_count": row[3],
        }
        for row in predecessor_rows
    }
    if any(
        row.get("predecessor", {}).get("path") not in predecessor_by_path
        or not json_type_equal(
            row.get("predecessor"),
            predecessor_by_path.get(row.get("predecessor", {}).get("path")),
        )
        for row in disposition_rows
    ):
        findings.add(
            "migration_disposition_mismatch",
            "migration predecessor exact-byte binding differs",
        )
    successor_profile = migration.get("successor_profile_binding")
    expected_successor_profile_subset = {
        "profile_id": PROFILE_ID,
        "profile_version": PROFILE_VERSION,
        "profile_core_path": CORE_PATH,
        "profile_core_schema_path": SCHEMA_ROWS[9][1],
        "profile_core_schema_id": SCHEMA_ROWS[9][2],
        "profile_core_raw_digest": sha256(core_raw),
        "profile_core_byte_count": len(core_raw),
        "profile_core_schema_raw_digest": sha256(
            schema_documents[SCHEMA_ROWS[9][1]][1]
        ),
        "profile_core_schema_byte_count": len(
            schema_documents[SCHEMA_ROWS[9][1]][1]
        ),
        "core_contains_self_hash": False,
        "binding_is_external_to_core": True,
        "binding_status": "exact_candidate_core_and_evidence_bytes",
        "profile_issued": False,
        "profile_evidence_path": EVIDENCE_PATH,
        "profile_evidence_schema_path": SCHEMA_ROWS[10][1],
        "profile_evidence_schema_id": SCHEMA_ROWS[10][2],
        "profile_evidence_raw_digest": sha256(evidence_raw),
        "profile_evidence_byte_count": len(evidence_raw),
        "profile_evidence_schema_raw_digest": sha256(
            schema_documents[SCHEMA_ROWS[10][1]][1]
        ),
        "profile_evidence_schema_byte_count": len(
            schema_documents[SCHEMA_ROWS[10][1]][1]
        ),
    }
    if not json_type_equal(
        successor_profile, expected_successor_profile_subset
    ):
        findings.add(
            "record_exact_byte_binding_mismatch",
            "migration core/evidence live bindings differ",
        )
    expected_migration_offline = {
        "resolution_key": (
            "expected_resource_id_raw_digest_and_byte_count"
        ),
        "verify_raw_bytes_before_utf8_decode_and_parse": True,
        "body_id_semantic_version_registry_key_and_dependency_agreement": (
            "required"
        ),
        "aliases_redirects_bare_id_or_latest": "reject",
        "network_file_search_environment_or_mutable_fallback": "disabled",
        "complete_offline_resolution": False,
        "unresolved_historical_resource_count": None,
        "missing_count_must_not_be_interpreted_as_zero": True,
    }
    if not json_type_equal(
        migration.get("offline_resolver_boundary"),
        expected_migration_offline,
    ):
        findings.add(
            "offline_resolver_boundary_mismatch",
            "migration resolver/null boundary differs",
        )

    live_digests = {
        CORE_PATH: sha256(core_raw),
        EVIDENCE_PATH: sha256(evidence_raw),
        MIGRATION_PATH: sha256(migration_raw),
    }
    core_strings = recursive_string_values(core)
    evidence_strings = recursive_string_values(evidence)
    migration_strings = recursive_string_values(migration)
    if (
        live_digests[CORE_PATH] in core_strings
        or live_digests[EVIDENCE_PATH] in core_strings
        or live_digests[MIGRATION_PATH] in core_strings
        or live_digests[EVIDENCE_PATH] in evidence_strings
        or live_digests[MIGRATION_PATH] in evidence_strings
        or live_digests[MIGRATION_PATH] in migration_strings
    ):
        findings.add(
            "digest_dependency_self_or_downstream_binding",
            "core/evidence/migration contains a forbidden self/downstream digest",
        )

    core_authority = core.get("authority_boundary")
    evidence_authority = evidence.get("acceptance_boundary")
    migration_authority = migration.get("completion_boundary")
    false_keys = {
        "profile_issued",
        "canonical_identity_issued",
        "canonical_identity_may_be_issued",
        "schema_resources_admitted",
        "product_members_constructed",
        "product_snapshots_constructed",
        "product_digests_computed",
        "product_root_constructed",
        "gate_a_complete",
        "runtime_authorized",
        "deployment_authorized",
        "external_effects_authorized",
        "publication_authorized",
    }
    null_keys = {
        "profile_registry_member_ref",
        "schema_registry_snapshot_ref",
        "engine_contract_root_ref",
        "activation_ref",
        "operator_acceptance_ref",
        "profile_core_canonical_digest",
        "review_determination_ref",
    }
    for label, boundary in (
        ("core", core_authority),
        ("evidence", evidence_authority),
        ("migration", migration_authority),
    ):
        if not isinstance(boundary, dict):
            findings.add(
                "authority_boundary_escalated", f"{label}: boundary absent"
            )
            continue
        for key in false_keys.intersection(boundary):
            if boundary[key] is not False:
                findings.add(
                    "authority_boundary_escalated",
                    f"{label}: {key} is not false",
                )
        for key in null_keys.intersection(boundary):
            if boundary[key] is not None:
                findings.add(
                    "authority_boundary_escalated",
                    f"{label}: {key} is not null",
                )
    if (
        migration_authority.get("product_digest_count")
        if isinstance(migration_authority, dict)
        else None
    ) != 0:
        findings.add(
            "product_identity_escalated",
            "migration product digest count is not exact measured zero",
        )
    return records


def validate_structural_fixtures(
    schema_documents: dict[str, tuple[dict[str, Any], bytes]],
    registry: Registry[Any],
    findings: Findings,
) -> None:
    fixture_directory = (
        "tests/architecture-schema/fixtures/"
        "prq-002e-structural-nonidentity"
    )
    expected: list[tuple[str, str]] = []
    for row in SCHEMA_ROWS[:9]:
        stem = Path(row[1]).name.removesuffix(".schema.json")
        expected.append(
            (
                (
                    "tests/architecture-schema/fixtures/"
                    "prq-002e-structural-nonidentity/"
                    f"prq-002e-{stem}.structural-nonidentity.json"
                ),
                row[1],
            )
        )
    try:
        actual = ACTIVE_VIEW.list_regular_files(fixture_directory, ".json")
    except (OSError, RepositoryPathError) as exc:
        findings.add("closed_schema_validation_failed", str(exc))
        return
    if actual != sorted(path for path, _ in expected):
        findings.add(
            "closed_schema_validation_failed",
            "exact nine structural-nonidentity fixture paths differ",
        )
        return
    for fixture_path, schema_path in expected:
        try:
            fixture, raw = load_object(ROOT / fixture_path)
            numeric_document_tokens(fixture, raw)
        except (OSError, ValueError) as exc:
            findings.add(
                "closed_schema_validation_failed",
                f"{fixture_path}: {exc}",
            )
            continue
        validate_instance(
            fixture,
            schema_documents[schema_path][0],
            registry,
            fixture_path,
            findings,
        )


def declared_identity(document: dict[str, Any]) -> str | None:
    for key in ("$id", "profile_id", "migration_id"):
        if isinstance(document.get(key), str):
            return document[key]
    return None


def string_literal_census(value: Any) -> tuple[list[str], list[str]]:
    domains: set[str] = set()
    profiles: set[str] = set()
    for _pointer, child in iter_locations(value):
        if isinstance(child, str):
            if DOMAIN_RE.fullmatch(child):
                domains.add(child)
            if PROFILE_RE.fullmatch(child):
                profiles.add(child)
    return sorted(domains), sorted(profiles)


def type_number_count(value: Any) -> int:
    count = 0
    for _pointer, child in iter_locations(value):
        if isinstance(child, dict):
            declared_type = child.get("type")
            if declared_type == "number" or (
                isinstance(declared_type, list)
                and "number" in declared_type
            ):
                count += 1
    return count


def negative_zero(token: str) -> bool:
    if not token.startswith("-"):
        return False
    significand = re.split(r"[eE]", token[1:], maxsplit=1)[0].replace(".", "")
    return bool(significand) and set(significand) == {"0"}


def expected_observation_row(
    sequence_index: int, role: str, relative: str
) -> dict[str, Any]:
    document, raw = load_object(ROOT / relative)
    tokens = raw_number_tokens(raw)
    integer_tokens = [
        token for token in tokens if INTEGER_RE.fullmatch(token)
    ]
    domains, profiles = string_literal_census(document)
    return {
        "sequence_index": sequence_index,
        "role": role,
        "repository_path": relative,
        "raw_sha256": sha256(raw),
        "byte_count": len(raw),
        "declared_identity": declared_identity(document),
        "schema_version": document.get("schema_version"),
        "raw_number_token_count": len(tokens),
        "integer_token_count": len(integer_tokens),
        "fraction_or_exponent_token_count": len(tokens) - len(integer_tokens),
        "negative_zero_token_count": sum(negative_zero(token) for token in tokens),
        "overlong_number_token_count": sum(
            len(token.encode("ascii")) > 128 for token in tokens
        ),
        "out_of_safe_integer_domain_token_count": sum(
            not MIN_SAFE_INTEGER <= int(token) <= MAX_SAFE_INTEGER
            for token in integer_tokens
        ),
        "ordered_number_token_sha256": sha256(compact_bytes(tokens)),
        "literal_type_number_occurrence_count": type_number_count(document),
        "domain_literals": domains,
        "profile_literals": profiles,
    }


def expected_source_manifest(
    observer_id: str, runtime_family: str, sources: tuple[str, ...]
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "artifact_class": "profile_0_3_construction_observer_source_manifest",
        "suite_id": SUITE_ID,
        "observer_id": observer_id,
        "runtime_family": runtime_family,
        "source_count": len(sources),
        "sources": [PINNED_SOURCE_BINDINGS[path] for path in sources],
        "declared_source_inventory_closed": True,
        "declared_expectation_source_included": False,
        "declared_peer_source_included": False,
        "declared_peer_result_source_included": False,
        "declared_filesystem_discovery_source_included": False,
        "declared_network_source_included": False,
        "source_inspection_is_not_process_isolation": True,
    }


def valid_observed_at(value: Any) -> bool:
    if not isinstance(value, str) or OBSERVED_AT_RE.fullmatch(value) is None:
        return False
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return False
    return (
        parsed.tzinfo == timezone.utc
        and parsed.date().isoformat() == "2026-07-29"
    )


def validate_observer_evidence(findings: Findings) -> None:
    missing = [
        path
        for path in OBSERVER_EVIDENCE_PATHS
        if not ACTIVE_VIEW.is_regular_file(path)
    ]
    try:
        actual_results = ACTIVE_VIEW.list_regular_files(
            "tests/product-identity-profile-0.3-candidate/results", ".json"
        )
    except (OSError, RepositoryPathError) as exc:
        findings.add("observer_evidence_inventory_mismatch", str(exc))
        return
    expected_results = sorted(OBSERVER_EVIDENCE_PATHS[2:])
    if missing or actual_results != expected_results:
        findings.add(
            "observer_evidence_inventory_mismatch",
            f"missing={missing}, results={actual_results}",
        )
        return
    try:
        manifest, _ = load_object(INPUT_MANIFEST_PATH)
        loaded = {
            path: load_object(ROOT / path)
            for path in OBSERVER_EVIDENCE_PATHS
        }
    except (OSError, ValueError) as exc:
        findings.add("observer_evidence_inventory_mismatch", str(exc))
        return

    expected_manifest = {
        "schema_version": "0.1.0",
        "artifact_class": (
            "profile_0_3_construction_observer_input_manifest"
        ),
        "suite_id": SUITE_ID,
        "manifest_id": (
            "prq-002e-profile-0.3-construction-inputs.0001"
        ),
        "answer_free": True,
        "expected_outcomes_included": False,
        "peer_results_included": False,
        "artifact_count": 15,
        "artifacts": [
            {"role": role, "repository_path": path}
            for role, path in EXPECTED_ARTIFACTS
        ],
        "network_access_allowed": False,
        "environment_path_discovery_allowed": False,
        "expectation_manifest_may_be_passed_to_observer": False,
        "peer_source_may_be_passed_to_observer": False,
        "peer_result_may_be_passed_to_observer": False,
        "product_identity_computation_allowed": False,
        "authority_claim_allowed": False,
    }
    if not json_type_equal(manifest, expected_manifest):
        findings.add(
            "observer_input_manifest_mismatch",
            "answer-free exact ordered 15-row manifest differs",
        )

    python_source, _ = loaded[PYTHON_SOURCE_PATH]
    node_source, _ = loaded[NODE_SOURCE_PATH]
    try:
        python_lock, _ = load_object(PYTHON_SOURCE_INPUTS[1])
        node_package, _ = load_object(NODE_SOURCE_INPUTS[1])
        node_lock, _ = load_object(NODE_SOURCE_INPUTS[2])
        actual_source_bindings = {
            path: binding(path)
            for path in (*PYTHON_SOURCE_INPUTS, *NODE_SOURCE_INPUTS)
        }
    except (OSError, ValueError) as exc:
        findings.add("observer_source_binding_mismatch", str(exc))
        python_lock = {}
        node_package = {}
        node_lock = {}
        actual_source_bindings = {}
    source_semantics_match = (
        json_type_equal(python_lock, EXPECTED_PYTHON_DEPENDENCY_LOCK)
        and json_type_equal(node_package, EXPECTED_NODE_PACKAGE)
        and json_type_equal(node_lock, EXPECTED_NODE_LOCK)
    )
    source_bindings_match = json_type_equal(
        actual_source_bindings, PINNED_SOURCE_BINDINGS
    )
    source_languages_distinct = (
        actual_source_bindings.get(PYTHON_SOURCE_INPUTS[0], {}).get(
            "raw_sha256"
        )
        != actual_source_bindings.get(NODE_SOURCE_INPUTS[0], {}).get(
            "raw_sha256"
        )
        and PYTHON_SOURCE_INPUTS[0].endswith(".py")
        and NODE_SOURCE_INPUTS[0].endswith(".mjs")
    )
    source_binding_invalid = (
        not json_type_equal(
            python_source,
            expected_source_manifest(
                PYTHON_OBSERVER_ID, "CPython", PYTHON_SOURCE_INPUTS
            ),
        )
        or not json_type_equal(
            node_source,
            expected_source_manifest(
                NODE_OBSERVER_ID, "Node.js", NODE_SOURCE_INPUTS
            ),
        )
        or not source_semantics_match
        or not source_bindings_match
    )
    if source_binding_invalid and source_languages_distinct:
        findings.add(
            "observer_source_binding_mismatch",
            "closed pinned Python/Node source or dependency bindings differ",
        )
    if not source_languages_distinct:
        findings.add(
            "observer_source_separation_mismatch",
            "primary observer sources are not distinct pinned language subjects",
        )

    python_result, python_result_raw = loaded[PYTHON_RESULT_PATH]
    node_result, node_result_raw = loaded[NODE_RESULT_PATH]
    result_keys = {
        "schema_version",
        "artifact_class",
        "suite_id",
        "observer_id",
        "challenge",
        "artifact_count",
        "artifacts",
        "network_access_requested",
        "expectations_received",
        "peer_source_received",
        "peer_result_received",
        "canonicalization_conformance_claimed",
        "product_identity_computed",
        "authority_claimed",
    }
    try:
        expected_rows = [
            expected_observation_row(index, role, path)
            for index, (role, path) in enumerate(EXPECTED_ARTIFACTS, start=1)
        ]
    except (OSError, ValueError) as exc:
        findings.add(
            "observer_result_binding_mismatch",
            f"live observation subject cannot be rebound: {exc}",
        )
        return
    common_challenge = python_result.get("challenge")
    for observer_id, result, raw in (
        (PYTHON_OBSERVER_ID, python_result, python_result_raw),
        (NODE_OBSERVER_ID, node_result, node_result_raw),
    ):
        expected_scalars = {
            "schema_version": "0.1.0",
            "artifact_class": "profile_0_3_construction_observation",
            "suite_id": SUITE_ID,
            "observer_id": observer_id,
            "challenge": common_challenge,
            "artifact_count": 15,
            "network_access_requested": False,
            "expectations_received": False,
            "peer_source_received": False,
            "peer_result_received": False,
            "canonicalization_conformance_claimed": False,
            "product_identity_computed": False,
            "authority_claimed": False,
        }
        if (
            set(result) != result_keys
            or not CHALLENGE_RE.fullmatch(str(result.get("challenge")))
            or any(
                not json_type_equal(result.get(key), value)
                for key, value in expected_scalars.items()
            )
            or not json_type_equal(result.get("artifacts"), expected_rows)
            or raw != compact_bytes(result, ascii_only=True, lf=True)
        ):
            findings.add(
                "observer_result_binding_mismatch",
                f"{observer_id}: exact projection/framing/live rows differ",
            )
    python_projection = dict(python_result)
    node_projection = dict(node_result)
    python_projection.pop("observer_id", None)
    node_projection.pop("observer_id", None)
    if not json_type_equal(python_projection, node_projection):
        findings.add(
            "observer_type_strict_agreement_mismatch",
            "Python/Node projections differ under type-strict comparison",
        )
    if any(
        row["raw_number_token_count"] != row["integer_token_count"]
        or row["fraction_or_exponent_token_count"] != 0
        or row["negative_zero_token_count"] != 0
        or row["overlong_number_token_count"] != 0
        or row["out_of_safe_integer_domain_token_count"] != 0
        or row["literal_type_number_occurrence_count"] != 0
        for row in expected_rows
    ):
        findings.add(
            "observer_integer_only_observation_mismatch",
            "live 15-row construction projection is not integer-only",
        )

    python_execution, _ = loaded[PYTHON_EXECUTION_PATH]
    node_execution, _ = loaded[NODE_EXECUTION_PATH]
    execution_keys = {
        "schema_version",
        "artifact_class",
        "suite_id",
        "observer_id",
        "observed_at",
        "challenge",
        "argv_contract",
        "runtime",
        "observer_binding",
        "source_manifest_binding",
        "input_manifest_binding",
        "result_binding",
        "environment_key_inventory",
        "stdin_received",
        "network_access_requested",
        "expectations_received",
        "peer_source_received",
        "peer_result_received",
        "filesystem_isolation_proven",
        "runtime_dependency_closure_complete",
        "observed_at_is_independently_witnessed",
        "historical_process_independently_witnessed",
        "canonicalization_conformance_claimed",
        "product_identity_computed",
        "authority_claimed",
    }
    execution_specs = (
        (
            python_execution,
            PYTHON_OBSERVER_ID,
            "CPython",
            PYTHON_SOURCE_PATH,
            PYTHON_RESULT_PATH,
            PYTHON_SOURCE_INPUTS[0],
            True,
        ),
        (
            node_execution,
            NODE_OBSERVER_ID,
            "Node.js",
            NODE_SOURCE_PATH,
            NODE_RESULT_PATH,
            NODE_SOURCE_INPUTS[0],
            False,
        ),
    )
    common_observed_at = python_execution.get("observed_at")
    for (
        execution,
        observer_id,
        runtime_family,
        source_path,
        result_path,
        observer_path,
        isolated,
    ) in execution_specs:
        expected_argv = [
            *(["-I"] if isolated else []),
            observer_path,
            "--root",
            "<repository-root>",
            "--manifest",
            INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            "--challenge",
            common_challenge,
        ]
        runtime = execution.get("runtime")
        runtime_pin = PINNED_RUNTIME[observer_id]
        expected_runtime = {
            "family": runtime_pin["family"],
            "version": runtime_pin["version"],
            "resolved_executable_basename": (
                runtime_pin["resolved_executable_basename"]
            ),
            "pre_execution_binding": runtime_pin["executable_binding"],
            "post_execution_binding": runtime_pin["executable_binding"],
            "dependency_closure_complete": False,
        }
        expected_false_keys = {
            "stdin_received",
            "network_access_requested",
            "expectations_received",
            "peer_source_received",
            "peer_result_received",
            "filesystem_isolation_proven",
            "runtime_dependency_closure_complete",
            "observed_at_is_independently_witnessed",
            "historical_process_independently_witnessed",
            "canonicalization_conformance_claimed",
            "product_identity_computed",
            "authority_claimed",
        }
        if (
            set(execution) != execution_keys
            or execution.get("schema_version") != "0.1.0"
            or execution.get("artifact_class")
            != "profile_0_3_construction_execution_receipt"
            or execution.get("suite_id") != SUITE_ID
            or execution.get("observer_id") != observer_id
            or execution.get("challenge") != common_challenge
            or execution.get("observed_at") != common_observed_at
            or not valid_observed_at(common_observed_at)
            or not json_type_equal(execution.get("argv_contract"), expected_argv)
            or not json_type_equal(runtime, expected_runtime)
            or not json_type_equal(
                execution.get("observer_binding"),
                {
                    "pre_execution": binding(observer_path),
                    "post_execution": binding(observer_path),
                },
            )
            or not json_type_equal(
                execution.get("source_manifest_binding"),
                binding(source_path),
            )
            or not json_type_equal(
                execution.get("input_manifest_binding"),
                {
                    "pre_execution": binding(
                        INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix()
                    ),
                    "post_execution": binding(
                        INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix()
                    ),
                },
            )
            or not json_type_equal(
                execution.get("result_binding"), binding(result_path)
            )
            or not json_type_equal(
                execution.get("environment_key_inventory"),
                ["LANG", "LC_ALL", "PATH"],
            )
            or any(execution.get(key) is not False for key in expected_false_keys)
        ):
            findings.add(
                "observer_execution_binding_mismatch",
                f"{observer_id}: execution receipt edge/nonclaim differs",
            )

    comparison, _ = loaded[COMPARISON_PATH]
    expected_comparison_keys = {
        "schema_version",
        "artifact_class",
        "suite_id",
        "observed_at",
        "challenge",
        "observer_count",
        "observer_ids",
        "input_manifest_binding",
        "python_source_manifest_binding",
        "node_source_manifest_binding",
        "python_result_binding",
        "node_result_binding",
        "python_execution_receipt_binding",
        "node_execution_receipt_binding",
        "complete_artifact_projection_hash_framing",
        "complete_artifact_projection_sha256",
        "complete_projection_agreement",
        "artifact_count",
        "bounded_15_row_artifact_projection_observed",
        "strict_duplicate_detection_agreement_proven",
        "literal_type_number_occurrence_count_is_applicability_proof",
        "static_schema_position_inventory_proved_by_this_observation",
        "per_subject_raw_applicability_traces_complete",
        "generic_schema_path_evaluation_proven",
        "canonicalization_conformance_complete",
        "organizational_independence_proven",
        "independent_host_reproduction_complete",
        "historical_process_independently_witnessed",
        "coherent_peer_output_substitution_excluded",
        "product_identity_computed",
        "profile_issued",
        "schema_resources_admitted",
        "gate_a_complete",
        "runtime_authorized",
        "publication_authorized",
    }
    expected_true = {
        "complete_projection_agreement",
        "bounded_15_row_artifact_projection_observed",
    }
    expected_false = {
        "strict_duplicate_detection_agreement_proven",
        "literal_type_number_occurrence_count_is_applicability_proof",
        "static_schema_position_inventory_proved_by_this_observation",
        "per_subject_raw_applicability_traces_complete",
        "generic_schema_path_evaluation_proven",
        "canonicalization_conformance_complete",
        "organizational_independence_proven",
        "independent_host_reproduction_complete",
        "historical_process_independently_witnessed",
        "coherent_peer_output_substitution_excluded",
        "product_identity_computed",
        "profile_issued",
        "schema_resources_admitted",
        "gate_a_complete",
        "runtime_authorized",
        "publication_authorized",
    }
    comparison_bindings = {
        "input_manifest_binding": binding(
            INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix()
        ),
        "python_source_manifest_binding": binding(PYTHON_SOURCE_PATH),
        "node_source_manifest_binding": binding(NODE_SOURCE_PATH),
        "python_result_binding": binding(PYTHON_RESULT_PATH),
        "node_result_binding": binding(NODE_RESULT_PATH),
        "python_execution_receipt_binding": binding(PYTHON_EXECUTION_PATH),
        "node_execution_receipt_binding": binding(NODE_EXECUTION_PATH),
    }
    expected_projection_digest = sha256(
        compact_bytes(python_projection, ascii_only=True, lf=True)
    )
    if (
        set(comparison) != expected_comparison_keys
        or comparison.get("schema_version") != "0.1.0"
        or comparison.get("artifact_class")
        != "profile_0_3_construction_comparison_receipt"
        or comparison.get("suite_id") != SUITE_ID
        or comparison.get("observed_at") != common_observed_at
        or comparison.get("challenge") != common_challenge
        or not json_type_equal(comparison.get("observer_count"), 2)
        or not json_type_equal(
            comparison.get("observer_ids"),
            [PYTHON_OBSERVER_ID, NODE_OBSERVER_ID],
        )
        or any(
            not json_type_equal(comparison.get(key), value)
            for key, value in comparison_bindings.items()
        )
        or comparison.get("complete_artifact_projection_hash_framing")
        != "sha256_over_utf8_ascii_json_sort_keys_compact_with_single_lf_v1"
        or comparison.get("complete_artifact_projection_sha256")
        != expected_projection_digest
        or not json_type_equal(comparison.get("artifact_count"), 15)
        or any(comparison.get(key) is not True for key in expected_true)
        or any(comparison.get(key) is not False for key in expected_false)
    ):
        findings.add(
            "observer_comparison_binding_mismatch",
            "comparison receipt bindings/hash/nonclaims differ",
        )


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/") or pointer == "/":
        raise ValueError(f"invalid mutation pointer: {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def json_pointer_parent(
    subject: Any, pointer: str
) -> tuple[dict[str, Any] | list[Any], str]:
    tokens = pointer_tokens(pointer)
    parent = subject
    for token in tokens[:-1]:
        if isinstance(parent, list):
            parent = parent[int(token)]
        else:
            parent = parent[token]
    if not isinstance(parent, (dict, list)):
        raise ValueError(f"mutation parent is not a container: {pointer}")
    return parent, tokens[-1]


def render_pretty(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")


def overlay_object(
    view: OverlayRepositoryView, relative: str
) -> dict[str, Any]:
    raw = view.read_bytes(relative)
    value = parse_json(raw, relative)
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: root must be an object")
    return value


def overlay_write_object(
    view: OverlayRepositoryView,
    relative: str,
    value: dict[str, Any],
    *,
    compact: bool = False,
) -> None:
    raw = (
        compact_bytes(value, ascii_only=True, lf=True)
        if compact
        else render_pretty(value)
    )
    view.replace_bytes(relative, raw)


def overlay_binding(
    view: OverlayRepositoryView, relative: str
) -> dict[str, Any]:
    raw = view.read_bytes(relative)
    return {
        "repository_path": relative,
        "raw_sha256": sha256(raw),
        "byte_count": len(raw),
    }


def set_json_value(
    view: OverlayRepositoryView,
    relative: str,
    pointer: str,
    value: Any,
    *,
    add: bool = False,
) -> None:
    document = overlay_object(view, relative)
    parent, token = json_pointer_parent(document, pointer)
    if isinstance(parent, list):
        index = int(token)
        if not 0 <= index < len(parent):
            raise ValueError(f"mutation target is absent: {pointer}")
        parent[index] = value
    else:
        if not add and token not in parent:
            raise ValueError(f"mutation target is absent: {pointer}")
        if add and token in parent:
            raise ValueError(f"mutation add target already exists: {pointer}")
        parent[token] = value
    overlay_write_object(view, relative, document)


def refresh_comparison_execution_binding(
    view: OverlayRepositoryView, comparison: dict[str, Any], observer: str
) -> None:
    if observer == "python":
        key = "python_execution_receipt_binding"
        path = PYTHON_EXECUTION_PATH
    elif observer == "node":
        key = "node_execution_receipt_binding"
        path = NODE_EXECUTION_PATH
    else:
        raise ValueError(f"unknown observer: {observer}")
    comparison[key] = overlay_binding(view, path)


def apply_actual_mutation(
    view: OverlayRepositoryView, mutation: dict[str, Any]
) -> None:
    op = mutation.get("op")
    relative = mutation.get("repository_path")
    if not isinstance(op, str):
        raise ValueError("mutation op must be a string")
    if op in {
        "json_replace",
        "json_add",
        "raw_replace",
        "prepend_bom",
        "append_whitespace",
        "missing",
        "symlink",
    }:
        if not isinstance(relative, str):
            raise ValueError(f"{op} requires repository_path")
        normalize_repository_path(relative)
    if op in {"json_replace", "json_add"}:
        if set(mutation) != {
            "op",
            "repository_path",
            "pointer",
            "value",
        }:
            raise ValueError(f"{op} mutation shape differs")
        set_json_value(
            view,
            relative,
            mutation["pointer"],
            mutation["value"],
            add=op == "json_add",
        )
        return
    if op == "raw_replace":
        if set(mutation) != {
            "op",
            "repository_path",
            "old",
            "new",
        }:
            raise ValueError("raw_replace mutation shape differs")
        raw = view.read_bytes(relative)
        old = mutation["old"].encode("utf-8")
        if raw.count(old) != 1:
            raise ValueError(
                f"raw_replace requires one exact occurrence, got {raw.count(old)}"
            )
        view.replace_bytes(relative, raw.replace(old, mutation["new"].encode()))
        return
    if op == "prepend_bom":
        if set(mutation) != {"op", "repository_path"}:
            raise ValueError("prepend_bom mutation shape differs")
        view.replace_bytes(relative, b"\xef\xbb\xbf" + view.read_bytes(relative))
        return
    if op == "append_whitespace":
        if set(mutation) != {"op", "repository_path"}:
            raise ValueError("append_whitespace mutation shape differs")
        view.replace_bytes(relative, view.read_bytes(relative) + b"\n")
        return
    if op == "missing":
        if set(mutation) != {"op", "repository_path"}:
            raise ValueError("missing mutation shape differs")
        view.mark_missing(relative)
        return
    if op == "symlink":
        if set(mutation) != {"op", "repository_path"}:
            raise ValueError("symlink mutation shape differs")
        view.mark_symlink(relative)
        return
    if op == "add_schema":
        if set(mutation) != {"op", "repository_path"}:
            raise ValueError("add_schema mutation shape differs")
        view.replace_bytes(relative, b"{}\n")
        return
    if op == "coherent_observed_at":
        if set(mutation) != {"op", "value"}:
            raise ValueError("coherent_observed_at mutation shape differs")
        for path in (PYTHON_EXECUTION_PATH, NODE_EXECUTION_PATH):
            execution = overlay_object(view, path)
            execution["observed_at"] = mutation["value"]
            overlay_write_object(view, path, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        comparison["observed_at"] = mutation["value"]
        refresh_comparison_execution_binding(view, comparison, "python")
        refresh_comparison_execution_binding(view, comparison, "node")
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op in {"coherent_runtime_replace", "coherent_runtime_add"}:
        expected_keys = {"op", "observer", "pointer", "value"}
        if set(mutation) != expected_keys:
            raise ValueError(f"{op} mutation shape differs")
        observer = mutation["observer"]
        path = (
            PYTHON_EXECUTION_PATH
            if observer == "python"
            else NODE_EXECUTION_PATH
        )
        execution = overlay_object(view, path)
        parent, token = json_pointer_parent(
            execution, "/runtime" + mutation["pointer"]
        )
        if not isinstance(parent, dict):
            raise ValueError("runtime mutation parent must be an object")
        if op == "coherent_runtime_replace" and token not in parent:
            raise ValueError("runtime replace target is absent")
        if op == "coherent_runtime_add" and token in parent:
            raise ValueError("runtime add target already exists")
        parent[token] = mutation["value"]
        overlay_write_object(view, path, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        refresh_comparison_execution_binding(view, comparison, observer)
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op == "coherent_input_replace":
        if set(mutation) != {"op", "pointer", "value"}:
            raise ValueError("coherent_input_replace mutation shape differs")
        set_json_value(
            view,
            INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix(),
            mutation["pointer"],
            mutation["value"],
        )
        input_relative = INPUT_MANIFEST_PATH.relative_to(ROOT).as_posix()
        for path in (PYTHON_EXECUTION_PATH, NODE_EXECUTION_PATH):
            execution = overlay_object(view, path)
            live = overlay_binding(view, input_relative)
            execution["input_manifest_binding"] = {
                "pre_execution": live,
                "post_execution": live,
            }
            overlay_write_object(view, path, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        comparison["input_manifest_binding"] = overlay_binding(
            view, input_relative
        )
        refresh_comparison_execution_binding(view, comparison, "python")
        refresh_comparison_execution_binding(view, comparison, "node")
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op == "coherent_result_reencode":
        if set(mutation) != {"op"}:
            raise ValueError("coherent_result_reencode mutation shape differs")
        for result_path in (PYTHON_RESULT_PATH, NODE_RESULT_PATH):
            result = overlay_object(view, result_path)
            overlay_write_object(view, result_path, result)
        for observer, execution_path, result_path in (
            ("python", PYTHON_EXECUTION_PATH, PYTHON_RESULT_PATH),
            ("node", NODE_EXECUTION_PATH, NODE_RESULT_PATH),
        ):
            execution = overlay_object(view, execution_path)
            execution["result_binding"] = overlay_binding(view, result_path)
            overlay_write_object(view, execution_path, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        comparison["python_result_binding"] = overlay_binding(
            view, PYTHON_RESULT_PATH
        )
        comparison["node_result_binding"] = overlay_binding(
            view, NODE_RESULT_PATH
        )
        refresh_comparison_execution_binding(view, comparison, "python")
        refresh_comparison_execution_binding(view, comparison, "node")
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op == "coherent_python_lock_replace":
        if set(mutation) != {"op", "pointer", "value"}:
            raise ValueError("coherent_python_lock_replace shape differs")
        lock_path = PYTHON_SOURCE_INPUTS[1]
        set_json_value(view, lock_path, mutation["pointer"], mutation["value"])
        source = overlay_object(view, PYTHON_SOURCE_PATH)
        source["sources"][1] = overlay_binding(view, lock_path)
        overlay_write_object(view, PYTHON_SOURCE_PATH, source)
        execution = overlay_object(view, PYTHON_EXECUTION_PATH)
        execution["source_manifest_binding"] = overlay_binding(
            view, PYTHON_SOURCE_PATH
        )
        overlay_write_object(view, PYTHON_EXECUTION_PATH, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        comparison["python_source_manifest_binding"] = overlay_binding(
            view, PYTHON_SOURCE_PATH
        )
        refresh_comparison_execution_binding(view, comparison, "python")
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op == "coherent_source_copy":
        if set(mutation) != {"op"}:
            raise ValueError("coherent_source_copy mutation shape differs")
        view.replace_bytes(
            NODE_SOURCE_INPUTS[0], view.read_bytes(PYTHON_SOURCE_INPUTS[0])
        )
        source = overlay_object(view, NODE_SOURCE_PATH)
        source["sources"][0] = overlay_binding(view, NODE_SOURCE_INPUTS[0])
        overlay_write_object(view, NODE_SOURCE_PATH, source)
        execution = overlay_object(view, NODE_EXECUTION_PATH)
        live_observer = overlay_binding(view, NODE_SOURCE_INPUTS[0])
        execution["observer_binding"] = {
            "pre_execution": live_observer,
            "post_execution": live_observer,
        }
        execution["source_manifest_binding"] = overlay_binding(
            view, NODE_SOURCE_PATH
        )
        overlay_write_object(view, NODE_EXECUTION_PATH, execution)
        comparison = overlay_object(view, COMPARISON_PATH)
        comparison["node_source_manifest_binding"] = overlay_binding(
            view, NODE_SOURCE_PATH
        )
        refresh_comparison_execution_binding(view, comparison, "node")
        overlay_write_object(view, COMPARISON_PATH, comparison)
        return
    if op == "comparison_replace":
        if set(mutation) != {"op", "pointer", "value"}:
            raise ValueError("comparison_replace mutation shape differs")
        set_json_value(
            view, COMPARISON_PATH, mutation["pointer"], mutation["value"]
        )
        return
    raise ValueError(f"unknown actual-artifact mutation op: {op!r}")


EXPECTED_CASE_SPECS = (
    ("predecessor_manifest_tree_drift", "predecessor_lineage", "predecessor", "predecessor_byte_binding_mismatch", "json_replace"),
    ("predecessor_manifest_symlink", "predecessor_lineage", "predecessor", "predecessor_byte_binding_mismatch", "symlink"),
    ("predecessor_live_schema_symlink", "predecessor_lineage", "predecessor", "predecessor_byte_binding_mismatch", "symlink"),
    ("successor_missing_schema", "successor_identity_and_census", "cohort", "successor_schema_cohort_mismatch", "missing"),
    ("successor_additional_schema", "successor_identity_and_census", "cohort", "successor_schema_cohort_mismatch", "add_schema"),
    ("successor_schema_symlink", "successor_identity_and_census", "cohort", "successor_schema_cohort_mismatch", "symlink"),
    ("successor_schema_bom", "successor_identity_and_census", "cohort", "successor_schema_cohort_mismatch", "prepend_bom"),
    ("successor_resource_id_drift", "successor_identity_and_census", "cohort", "successor_resource_identity_mismatch", "json_replace"),
    ("successor_schema_version_drift", "successor_identity_and_census", "cohort", "successor_resource_identity_mismatch", "json_replace"),
    ("successor_profile_annotation_drift", "successor_identity_and_census", "cohort", "successor_profile_annotation_mismatch", "json_replace"),
    ("successor_domain_drift", "successor_identity_and_census", "cohort", "successor_domain_inventory_mismatch", "json_replace"),
    ("numeric_literal_type_number", "numeric_applicability", "cohort", "type_number_position_forbidden", "json_replace"),
    ("numeric_number_admitting_union", "numeric_applicability", "cohort", "number_admitting_union_forbidden", "json_replace"),
    ("numeric_integral_fraction_token", "numeric_applicability", "cohort", "integer_raw_token_policy_violation", "raw_replace"),
    ("numeric_integral_exponent_token", "numeric_applicability", "cohort", "integer_raw_token_policy_violation", "raw_replace"),
    ("numeric_unclassified_keyword", "numeric_applicability", "cohort", "static_numeric_inventory_mismatch", "json_add"),
    ("numeric_unresolved_reference", "numeric_applicability", "cohort", "static_numeric_inventory_mismatch", "json_replace"),
    ("numeric_boolean_keyword_confusion", "numeric_applicability", "cohort", "closed_schema_validation_failed", "json_replace"),
    ("dag_core_reencoding", "digest_dependency_dag", "records", "record_exact_byte_binding_mismatch", "append_whitespace"),
    ("dag_evidence_reencoding", "digest_dependency_dag", "records", "record_exact_byte_binding_mismatch", "append_whitespace"),
    ("dag_core_schema_binding_drift", "digest_dependency_dag", "records", "record_exact_byte_binding_mismatch", "json_replace"),
    ("dag_core_record_symlink", "digest_dependency_dag", "records", "record_exact_byte_binding_mismatch", "symlink"),
    ("migration_successor_digest_drift_1", "migration_and_resolver", "records", "migration_disposition_mismatch", "json_replace"),
    ("migration_successor_byte_count_drift", "migration_and_resolver", "records", "migration_disposition_mismatch", "json_replace"),
    ("structural_fixture_symlink", "successor_identity_and_census", "fixtures", "closed_schema_validation_failed", "symlink"),
    ("observer_count_integral_float", "observer_graph", "observer", "observer_comparison_binding_mismatch", "raw_replace"),
    ("artifact_count_integral_float", "observer_graph", "observer", "observer_comparison_binding_mismatch", "raw_replace"),
    ("observer_invalid_leap_second", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_observed_at"),
    ("observer_unpinned_runtime_version", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_runtime_replace"),
    ("observer_unpinned_runtime_basename", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_runtime_replace"),
    ("observer_unpinned_executable_digest", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_runtime_replace"),
    ("observer_unpinned_executable_byte_count", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_runtime_replace"),
    ("observer_extra_nested_claim", "observer_graph", "observer", "observer_execution_binding_mismatch", "coherent_runtime_add"),
    ("observer_input_manifest_drift", "observer_graph", "observer", "observer_input_manifest_mismatch", "coherent_input_replace"),
    ("observer_input_authority_escalation", "observer_graph", "observer", "observer_input_manifest_mismatch", "coherent_input_replace"),
    ("observer_result_reencoding", "observer_graph", "observer", "observer_result_binding_mismatch", "coherent_result_reencode"),
    ("observer_dependency_lock_drift", "observer_graph", "observer", "observer_source_binding_mismatch", "coherent_python_lock_replace"),
    ("observer_source_language_collapse", "observer_graph", "observer", "observer_source_separation_mismatch", "coherent_source_copy"),
    ("observer_source_manifest_symlink", "observer_graph", "observer", "observer_evidence_inventory_mismatch", "symlink"),
    ("authority_profile_issuance_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
    ("authority_schema_admission_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
    ("authority_product_identity_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
    ("authority_gate_a_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
    ("authority_runtime_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
    ("authority_publication_escalation", "authority_nonclaims", "observer", "observer_comparison_binding_mismatch", "comparison_replace"),
)

EXPECTED_CASE_MUTATIONS = (
    {
        "op": "json_replace",
        "repository_path": (
            "tests/product-identity-profile-0.3-candidate/"
            "predecessor-schemas.json"
        ),
        "pointer": "/source_tree",
        "value": "0000000000000000000000000000000000000000",
    },
    {
        "op": "symlink",
        "repository_path": (
            "tests/product-identity-profile-0.3-candidate/"
            "predecessor-schemas.json"
        ),
    },
    {
        "op": "symlink",
        "repository_path": "schemas/adjudication.schema.json",
    },
    {
        "op": "missing",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
    },
    {
        "op": "add_schema",
        "repository_path": "schemas/prq-002e-unexpected.schema.json",
    },
    {
        "op": "symlink",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
    },
    {
        "op": "prepend_bom",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/$id",
        "value": "urn:odeya:schema:schema-resource-record:9.9.9",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/properties/schema_version/const",
        "value": "9.9.9",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/x-odeya-number-token-policy/boolean_is_not_integer",
        "value": False,
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": (
            "/$defs/schema_member_digest_contract/properties/"
            "domain_separator/const"
        ),
        "value": "odeya-schema-resource-record-v999",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/$defs/schema_bytes_identity/properties/byte_count/type",
        "value": "number",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/$defs/schema_bytes_identity/properties/byte_count/type",
        "value": ["integer", "number"],
    },
    {
        "op": "raw_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "old": (
            '"minItems": 1,\n'
            '      "uniqueItems": true,\n'
            '      "items": {\n'
            '        "$ref": "#/$defs/schema_registry_artifact_reference"'
        ),
        "new": (
            '"minItems": 1.0,\n'
            '      "uniqueItems": true,\n'
            '      "items": {\n'
            '        "$ref": "#/$defs/schema_registry_artifact_reference"'
        ),
    },
    {
        "op": "raw_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "old": '"minItems": 5,\n          "maxItems": 5',
        "new": '"minItems": 5e0,\n          "maxItems": 5',
    },
    {
        "op": "json_add",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/maximum",
        "value": 1,
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": "/properties/member_key/$ref",
        "value": "urn:odeya:schema:missing:0.0.0",
    },
    {
        "op": "json_replace",
        "repository_path": "schemas/schema-resource-record-v0-2.schema.json",
        "pointer": (
            "/$defs/schema_registry_nonempty_artifact_array/minItems"
        ),
        "value": True,
    },
    {
        "op": "append_whitespace",
        "repository_path": (
            "architecture/canonicalization-profile-core-0.3-candidate.json"
        ),
    },
    {
        "op": "append_whitespace",
        "repository_path": (
            "architecture/"
            "canonicalization-profile-0.3-candidate-evidence.json"
        ),
    },
    {
        "op": "json_replace",
        "repository_path": (
            "architecture/canonicalization-profile-core-0.3-candidate.json"
        ),
        "pointer": "/successor_schema_bindings/0/raw_digest",
        "value": (
            "sha256:"
            "0000000000000000000000000000000000000000000000000000000000000000"
        ),
    },
    {
        "op": "symlink",
        "repository_path": (
            "architecture/canonicalization-profile-core-0.3-candidate.json"
        ),
    },
    {
        "op": "json_replace",
        "repository_path": (
            "architecture/"
            "canonicalization-profile-0.2-to-0.3-migration-candidate.json"
        ),
        "pointer": "/resource_dispositions/0/successor/raw_digest",
        "value": (
            "sha256:"
            "0000000000000000000000000000000000000000000000000000000000000000"
        ),
    },
    {
        "op": "json_replace",
        "repository_path": (
            "architecture/"
            "canonicalization-profile-0.2-to-0.3-migration-candidate.json"
        ),
        "pointer": "/resource_dispositions/0/successor/byte_count",
        "value": 9421,
    },
    {
        "op": "symlink",
        "repository_path": (
            "tests/architecture-schema/fixtures/"
            "prq-002e-structural-nonidentity/"
            "prq-002e-aggregate-state-subject-record-v0-2."
            "structural-nonidentity.json"
        ),
    },
    {
        "op": "raw_replace",
        "repository_path": (
            "tests/product-identity-profile-0.3-candidate/results/"
            "comparison-receipt.json"
        ),
        "old": '"observer_count": 2,',
        "new": '"observer_count": 2.0,',
    },
    {
        "op": "raw_replace",
        "repository_path": (
            "tests/product-identity-profile-0.3-candidate/results/"
            "comparison-receipt.json"
        ),
        "old": '"artifact_count": 15,',
        "new": '"artifact_count": 15.0,',
    },
    {
        "op": "coherent_observed_at",
        "value": "2026-07-29T23:59:60Z",
    },
    {
        "op": "coherent_runtime_replace",
        "observer": "python",
        "pointer": "/version",
        "value": "0.0.0-unpinned",
    },
    {
        "op": "coherent_runtime_replace",
        "observer": "node",
        "pointer": "/resolved_executable_basename",
        "value": "untrusted-node",
    },
    {
        "op": "coherent_runtime_replace",
        "observer": "python",
        "pointer": "/pre_execution_binding/raw_sha256",
        "value": (
            "sha256:"
            "0000000000000000000000000000000000000000000000000000000000000000"
        ),
    },
    {
        "op": "coherent_runtime_replace",
        "observer": "node",
        "pointer": "/pre_execution_binding/byte_count",
        "value": 1,
    },
    {
        "op": "coherent_runtime_add",
        "observer": "python",
        "pointer": "/organizational_independence_proven",
        "value": True,
    },
    {
        "op": "coherent_input_replace",
        "pointer": "/answer_free",
        "value": False,
    },
    {
        "op": "coherent_input_replace",
        "pointer": "/authority_claim_allowed",
        "value": True,
    },
    {"op": "coherent_result_reencode"},
    {
        "op": "coherent_python_lock_replace",
        "pointer": "/runtime_version",
        "value": "0.0.0-unpinned",
    },
    {"op": "coherent_source_copy"},
    {
        "op": "symlink",
        "repository_path": (
            "tests/product-identity-profile-0.3-candidate/node/"
            "source-manifest.json"
        ),
    },
    {
        "op": "comparison_replace",
        "pointer": "/profile_issued",
        "value": True,
    },
    {
        "op": "comparison_replace",
        "pointer": "/schema_resources_admitted",
        "value": True,
    },
    {
        "op": "comparison_replace",
        "pointer": "/product_identity_computed",
        "value": True,
    },
    {
        "op": "comparison_replace",
        "pointer": "/gate_a_complete",
        "value": True,
    },
    {
        "op": "comparison_replace",
        "pointer": "/runtime_authorized",
        "value": True,
    },
    {
        "op": "comparison_replace",
        "pointer": "/publication_authorized",
        "value": True,
    },
)
EXPECTED_SAFE_COUNT = 1
EXPECTED_KNOWN_BAD_COUNT = len(EXPECTED_CASE_SPECS)

if len(EXPECTED_CASE_MUTATIONS) != EXPECTED_KNOWN_BAD_COUNT:
    raise RuntimeError("pinned case metadata and mutation corpus lengths differ")
if any(
    mutation.get("op") != spec[4]
    for spec, mutation in zip(
        EXPECTED_CASE_SPECS, EXPECTED_CASE_MUTATIONS, strict=True
    )
):
    raise RuntimeError("pinned case operation metadata differs")


def expected_case_row(index: int) -> dict[str, Any]:
    """Return one complete pinned row from immutable in-code expectations."""

    if index == 0:
        return {
            "name": "safe_exact_construction_boundary",
            "kind": "safe",
        }
    name, adversarial_class, target, guard, _op = EXPECTED_CASE_SPECS[
        index - EXPECTED_SAFE_COUNT
    ]
    return {
        "name": name,
        "kind": "known_bad",
        "adversarial_class": adversarial_class,
        "validation_target": target,
        "expected_guard": guard,
        "mutation": EXPECTED_CASE_MUTATIONS[index - EXPECTED_SAFE_COUNT],
    }


def case_row_admission_errors(case_rows: Any) -> list[str]:
    """Type-strictly admit only the complete pinned ordered case corpus."""

    expected_count = EXPECTED_SAFE_COUNT + EXPECTED_KNOWN_BAD_COUNT
    if type(case_rows) is not list or len(case_rows) != expected_count:
        return [f"exact ordered case row count differs from {expected_count}"]
    errors: list[str] = []
    for index, observed in enumerate(case_rows):
        expected = expected_case_row(index)
        if not json_type_equal(observed, expected):
            errors.append(
                f"case row {index} complete pinned payload/metadata differs"
            )
    return errors


def case_payload_swap_meta_proof(case_rows: list[Any]) -> bool:
    """Prove same-guard payload substitution is refused before execution."""

    predecessor_manifest_index = 2
    predecessor_schema_index = 3
    left = case_rows[predecessor_manifest_index]
    right = case_rows[predecessor_schema_index]
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    shared_keys = (
        "kind",
        "adversarial_class",
        "validation_target",
        "expected_guard",
    )
    if any(
        not json_type_equal(left.get(key), right.get(key))
        for key in shared_keys
    ):
        return False
    if left.get("mutation", {}).get("op") != right.get("mutation", {}).get(
        "op"
    ):
        return False
    swapped = copy.deepcopy(case_rows)
    (
        swapped[predecessor_manifest_index]["mutation"],
        swapped[predecessor_schema_index]["mutation"],
    ) = (
        swapped[predecessor_schema_index]["mutation"],
        swapped[predecessor_manifest_index]["mutation"],
    )
    return bool(case_row_admission_errors(swapped))


def load_predecessor_for_validation(findings: Findings) -> list[list[Any]]:
    try:
        predecessor, _ = load_object(PREDECESSOR_PATH)
    except (OSError, ValueError) as exc:
        findings.add("predecessor_byte_binding_mismatch", str(exc))
        predecessor = {}
    return validate_predecessor(predecessor, findings)


def validate_retained_evidence() -> Findings:
    findings = Findings()
    predecessor_rows = load_predecessor_for_validation(findings)
    schema_documents, registry, inventory = validate_schema_cohort(
        predecessor_rows, findings
    )
    validate_records(
        schema_documents,
        registry,
        inventory,
        predecessor_rows,
        findings,
    )
    if len(schema_documents) == 12:
        validate_structural_fixtures(schema_documents, registry, findings)
    validate_observer_evidence(findings)
    return findings


def validate_mutated_target(
    target: str,
    *,
    baseline_predecessor_rows: list[list[Any]] | None = None,
    baseline_schema_bundle: tuple[
        dict[str, tuple[dict[str, Any], bytes]],
        Registry[Any],
        dict[str, Any] | None,
    ]
    | None = None,
) -> Findings:
    findings = Findings()
    if target == "retained":
        return validate_retained_evidence()
    if target == "predecessor":
        load_predecessor_for_validation(findings)
        return findings
    prerequisite_findings = Findings()
    predecessor_rows = (
        baseline_predecessor_rows
        if baseline_predecessor_rows is not None
        else load_predecessor_for_validation(prerequisite_findings)
    )
    if target == "cohort":
        validate_schema_cohort(predecessor_rows, findings)
        return findings
    if baseline_schema_bundle is None:
        schema_documents, registry, inventory = validate_schema_cohort(
            predecessor_rows, prerequisite_findings
        )
    else:
        schema_documents, registry, inventory = baseline_schema_bundle
    if prerequisite_findings:
        raise RuntimeError(
            "known-bad prerequisite baseline failed: "
            + ", ".join(sorted(prerequisite_findings.codes()))
        )
    if target == "records":
        validate_records(
            schema_documents,
            registry,
            inventory,
            predecessor_rows,
            findings,
        )
        return findings
    if target == "fixtures":
        validate_structural_fixtures(schema_documents, registry, findings)
        return findings
    if target == "observer":
        validate_observer_evidence(findings)
        return findings
    raise ValueError(f"unknown production validation target: {target}")


def validate_cases(cases: dict[str, Any], findings: Findings) -> tuple[int, int]:
    expected_root_keys = {
        "manifest_version",
        "artifact_class",
        "status",
        "description",
        "required_adversarial_classes",
        "exact_safe_control_count",
        "exact_known_bad_count",
        "cases",
    }
    if (
        set(cases) != expected_root_keys
        or cases.get("manifest_version") != "0.2.0"
        or cases.get("artifact_class")
        != "prq_002e_profile_0_3_construction_adversarial_contract"
        or cases.get("status")
        != "architecture_only_unissued_unadmitted_construction_evidence"
        or not json_type_equal(
            cases.get("exact_safe_control_count"), EXPECTED_SAFE_COUNT
        )
        or not json_type_equal(
            cases.get("exact_known_bad_count"), EXPECTED_KNOWN_BAD_COUNT
        )
    ):
        findings.add("case_manifest_invalid", "case manifest header/shape differs")
        return 0, 0
    required_classes = cases.get("required_adversarial_classes")
    case_rows = cases.get("cases")
    if (
        not isinstance(required_classes, list)
        or not all(isinstance(item, str) for item in required_classes)
        or not json_type_equal(
            required_classes, list(EXPECTED_ADVERSARIAL_CLASSES)
        )
        or not isinstance(case_rows, list)
        or len(case_rows)
        != EXPECTED_SAFE_COUNT + EXPECTED_KNOWN_BAD_COUNT
    ):
        findings.add(
            "case_manifest_invalid", "classes/cases must be unique arrays"
        )
        return 0, 0
    admission_errors = case_row_admission_errors(case_rows)
    if admission_errors:
        for detail in admission_errors:
            findings.add("case_manifest_invalid", detail)
        return 0, 0
    if not case_payload_swap_meta_proof(case_rows):
        findings.add(
            "case_manifest_invalid",
            "same-guard mutation-payload swap admission meta-proof failed",
        )
        return 0, 0

    witnesses: set[bytes] = set()
    safe_count = 0
    known_bad_count = 0
    global ACTIVE_VIEW
    previous_view = ACTIVE_VIEW
    ACTIVE_VIEW = LIVE_VIEW
    try:
        baseline_findings = Findings()
        baseline_predecessor_rows = load_predecessor_for_validation(
            baseline_findings
        )
        baseline_schema_bundle = validate_schema_cohort(
            baseline_predecessor_rows, baseline_findings
        )
    finally:
        ACTIVE_VIEW = previous_view
    if baseline_findings:
        findings.add(
            "safe_model_rejected",
            "known-bad prerequisites failed: "
            + ", ".join(sorted(baseline_findings.codes())),
        )
        return 0, 0

    for index, case in enumerate(case_rows):
        if not isinstance(case, dict):
            findings.add("case_manifest_invalid", "case row is malformed")
            continue
        name = case["name"]
        if case.get("kind") == "safe":
            safe_count += 1
            if set(case) != {"name", "kind"}:
                findings.add(
                    "case_manifest_invalid",
                    f"{name}: safe control carries mutation metadata",
                )
            previous_view = ACTIVE_VIEW
            ACTIVE_VIEW = LIVE_VIEW
            try:
                observed = validate_mutated_target("retained").codes()
            finally:
                ACTIVE_VIEW = previous_view
            if observed:
                findings.add(
                    "safe_model_rejected",
                    f"{name}: production guards fired: {sorted(observed)}",
                )
            continue
        known_bad_count += 1
        adversarial_class = case.get("adversarial_class")
        validation_target = case.get("validation_target")
        expected_guard = case.get("expected_guard")
        spec = EXPECTED_CASE_SPECS[index - EXPECTED_SAFE_COUNT]
        expected_metadata = (
            name,
            adversarial_class,
            validation_target,
            expected_guard,
        )
        expected_mutation = EXPECTED_CASE_MUTATIONS[
            index - EXPECTED_SAFE_COUNT
        ]
        if expected_metadata != spec[:4] or not json_type_equal(
            case["mutation"], expected_mutation
        ):
            findings.add(
                "case_manifest_invalid",
                f"{name}: complete pinned mutation/metadata differs",
            )
            continue
        marker = compact_bytes(case["mutation"], ascii_only=True)
        if marker in witnesses:
            findings.add(
                "case_manifest_invalid", f"{name}: duplicate mutation witness"
            )
        witnesses.add(marker)
        view = OverlayRepositoryView(LIVE_VIEW)
        previous_view = ACTIVE_VIEW
        ACTIVE_VIEW = view
        try:
            apply_actual_mutation(view, case["mutation"])
            observed = validate_mutated_target(
                validation_target,
                baseline_predecessor_rows=baseline_predecessor_rows,
                baseline_schema_bundle=baseline_schema_bundle,
            ).codes()
        except (KeyError, OSError, TypeError, ValueError, RuntimeError) as exc:
            findings.add("case_manifest_invalid", f"{name}: {exc}")
            continue
        finally:
            ACTIVE_VIEW = previous_view
        if observed != {expected_guard}:
            findings.add(
                "known_bad_guard_mismatch",
                f"{name}: expected {expected_guard}, observed {sorted(observed)}",
            )
    if (
        safe_count != EXPECTED_SAFE_COUNT
        or known_bad_count != EXPECTED_KNOWN_BAD_COUNT
    ):
        findings.add(
            "case_manifest_invalid",
            f"expected exact {EXPECTED_SAFE_COUNT}/{EXPECTED_KNOWN_BAD_COUNT}, "
            f"got {safe_count}/{known_bad_count}",
        )
    return safe_count, known_bad_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="exercise the declarative single-fault guard corpus only",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = Findings()
    try:
        cases, _ = load_object(CASES_PATH)
    except (OSError, ValueError) as exc:
        print(f"case_manifest_invalid: {exc}", file=sys.stderr)
        return 1
    safe_count, known_bad_count = validate_cases(cases, findings)
    if not args.self_test_only:
        findings.merge(validate_retained_evidence())
    if findings:
        for line in findings.lines():
            print(line, file=sys.stderr)
        return 1
    mode = "self-test" if args.self_test_only else "retained evidence"
    print(
        "odeya-jcs-0.3 construction "
        f"{mode} passed: safe_controls={safe_count}, "
        f"known_bads={known_bad_count}, schemas=12, "
        "side_by_side_schema_census=144, observer_artifacts=7; "
        "conformance=false, identity=false, authority=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
