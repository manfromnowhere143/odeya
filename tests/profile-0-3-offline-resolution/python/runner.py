"""PRQ-002I offline-resolution and binding-replay runner (CPython path).

Loads the declared universe, builds the schema registry solely from universe
members carrying a `urn:odeya:schema:` identifier, resolves every `$ref`
across the full registry offline — in-document fragments by exact RFC 6901
pointer, absolute URN references against the registry with recorded target
digests, everything else refusing — and replays every declared digest
binding in every JSON universe member by recomputing the referenced
repository file's raw SHA-256 and byte count from bytes. Consults nothing
but the repository: no network, no directory discovery, no environment, no
fallback. Zero third-party dependencies; source-separated from the Node.js
peer. Bounded architecture evidence only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
SUITE_ID = "prq-002i-offline-resolution.0001"
IMPLEMENTATION_ID = "python-stdlib-offline-resolver.0001"
URN_PREFIX = "urn:odeya:schema:"
SKIP_WALK_KEYS = {"const", "enum", "examples", "default"}


class Refusal(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def refuse(code: str, detail: str) -> None:
    raise Refusal(code, detail)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            refuse("universe_member_violation", f"duplicate member name {key!r}")
        result[key] = value
    return result


def load_member(root: Path, relative: str) -> tuple[bytes, Any]:
    if relative.startswith("/") or ".." in relative.split("/"):
        refuse("universe_member_violation", f"illegal member path {relative!r}")
    path = root / relative
    if path.is_symlink() or not path.is_file():
        refuse(
            "universe_member_violation",
            f"{relative}: not a regular non-symlink repository file",
        )
    raw = path.read_bytes()
    try:
        document = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=strict_pairs,
            parse_float=lambda lexeme: refuse(
                "universe_member_violation",
                f"{relative}: non-integer number token {lexeme}",
            ),
            parse_constant=lambda lexeme: refuse(
                "universe_member_violation",
                f"{relative}: non-finite literal {lexeme}",
            ),
        )
    except Refusal:
        raise
    except (UnicodeDecodeError, ValueError) as exc:
        refuse("universe_member_violation", f"{relative}: invalid JSON: {exc}")
    return raw, document


def resolve_pointer(document: Any, fragment: str, context: str) -> Any:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        refuse(
            "offline_resolution_violation",
            f"{context}: unsupported reference fragment {fragment}",
        )
    current = document
    for encoded in fragment[2:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError):
                refuse(
                    "offline_resolution_violation",
                    f"{context}: unresolvable fragment {fragment}",
                )
        else:
            refuse(
                "offline_resolution_violation",
                f"{context}: unresolvable fragment {fragment}",
            )
    return current


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--universe", required=True)
    parser.add_argument("--source-manifest", required=True)
    arguments = parser.parse_args()
    root = Path(arguments.repository_root)

    universe_raw = Path(arguments.universe).read_bytes()
    universe = json.loads(universe_raw.decode("utf-8"))
    if (
        universe.get("suite_id") != SUITE_ID
        or universe.get("answer_free") is not True
        or universe.get("verification_time_directory_discovery_allowed")
        is not False
        or universe.get("network_access_allowed") is not False
    ):
        refuse("universe_census_mismatch", "universe identity flags differ")
    members = universe.get("members")
    if not isinstance(members, list) or universe.get(
        "member_count_decimal"
    ) != str(len(members)):
        refuse("universe_census_mismatch", "universe member census differs")
    role_counts: dict[str, int] = {}
    loaded: list[tuple[str, str, bytes, Any]] = []
    seen_paths: set[str] = set()
    for member in members:
        role = member.get("role")
        relative = member.get("repository_path")
        if not isinstance(role, str) or not isinstance(relative, str):
            refuse("universe_census_mismatch", "malformed universe member")
        if relative in seen_paths:
            refuse("universe_census_mismatch", f"duplicate member {relative}")
        seen_paths.add(relative)
        role_counts[role] = role_counts.get(role, 0) + 1
        raw, document = load_member(root, relative)
        loaded.append((role, relative, raw, document))
    declared_counts = universe.get("role_counts_decimal")
    if declared_counts != {
        role: str(count) for role, count in sorted(role_counts.items())
    }:
        refuse("universe_census_mismatch", "universe role census differs")

    registry: dict[str, tuple[str, bytes, Any]] = {}
    for role, relative, raw, document in loaded:
        if (
            isinstance(document, dict)
            and isinstance(document.get("$id"), str)
            and document["$id"].startswith(URN_PREFIX)
        ):
            schema_id = document["$id"]
            if schema_id in registry:
                refuse(
                    "universe_census_mismatch",
                    f"duplicate schema identifier {schema_id}",
                )
            registry[schema_id] = (relative, raw, document)
    if str(len(registry)) != universe.get("role_counts_decimal", {}).get(
        "schema"
    ):
        refuse(
            "universe_census_mismatch",
            "registry census differs from declared schema role count",
        )

    reference_edges: list[dict[str, str]] = []

    def walk_schema(schema_id: str, node: Any, pointer: str) -> None:
        if isinstance(node, list):
            for index, child in enumerate(node):
                walk_schema(schema_id, child, f"{pointer}/{index}")
            return
        if not isinstance(node, dict):
            return
        if "$dynamicRef" in node or "$recursiveRef" in node:
            refuse(
                "offline_resolution_violation",
                f"{schema_id}#{pointer}: dynamic reference is not offline-resolvable",
            )
        reference = node.get("$ref")
        if isinstance(reference, str):
            context = f"{schema_id}#{pointer}/$ref"
            if reference.startswith("#"):
                resolve_pointer(registry[schema_id][2], reference, context)
                target_id = schema_id
                fragment = reference
            elif reference.startswith(URN_PREFIX):
                target_id, separator, suffix = reference.partition("#")
                if target_id not in registry:
                    refuse(
                        "offline_resolution_violation",
                        f"{context}: reference target outside the universe "
                        f"registry: {target_id}",
                    )
                fragment = f"#{suffix}" if separator else "#"
                resolve_pointer(registry[target_id][2], fragment, context)
            else:
                refuse(
                    "offline_resolution_violation",
                    f"{context}: non-URN, non-fragment reference {reference!r}",
                )
            target_path, target_raw, _ = registry[target_id]
            reference_edges.append(
                {
                    "source_schema_id": schema_id,
                    "source_pointer": pointer,
                    "reference": reference,
                    "target_schema_id": target_id,
                    "target_repository_path": target_path,
                    "target_raw_sha256": sha256(target_raw),
                    "fragment": fragment,
                }
            )
        for key, child in node.items():
            if key in SKIP_WALK_KEYS or key.startswith("x-"):
                continue
            walk_schema(schema_id, child, f"{pointer}/{pointer_escape(key)}")

    for schema_id in registry:
        walk_schema(schema_id, registry[schema_id][2], "")

    binding_edges: list[dict[str, str]] = []
    shape_counts = {"repository_path": 0, "path": 0, "schema_path": 0}

    def binding_target(node: dict[str, Any]):
        if isinstance(node.get("repository_path"), str) and isinstance(
            node.get("raw_sha256"), str
        ):
            count = node.get("byte_count_decimal")
            return (
                "repository_path",
                node["repository_path"],
                node["raw_sha256"],
                count if isinstance(count, str) else None,
            )
        if (
            isinstance(node.get("path"), str)
            and isinstance(node.get("raw_digest"), str)
            and type(node.get("byte_count")) is int
        ):
            return ("path", node["path"], node["raw_digest"], str(node["byte_count"]))
        if (
            isinstance(node.get("schema_path"), str)
            and isinstance(node.get("schema_raw_digest"), str)
            and type(node.get("schema_byte_count")) is int
        ):
            return (
                "schema_path",
                node["schema_path"],
                node["schema_raw_digest"],
                str(node["schema_byte_count"]),
            )
        return None

    def walk_bindings(member_path: str, node: Any, pointer: str) -> None:
        if isinstance(node, list):
            for index, child in enumerate(node):
                walk_bindings(member_path, child, f"{pointer}/{index}")
            return
        if not isinstance(node, dict):
            return
        target = binding_target(node)
        if target is not None:
            shape, relative, declared_digest, declared_count = target
            context = f"{member_path}#{pointer}"
            if relative.startswith("/") or ".." in relative.split("/"):
                refuse(
                    "out_of_repository_target",
                    f"{context}: binding escapes the repository: {relative!r}",
                )
            target_path = root / relative
            if target_path.is_symlink() or not target_path.is_file():
                refuse(
                    "digest_binding_mismatch",
                    f"{context}: binding target missing or symlinked: {relative}",
                )
            target_raw = target_path.read_bytes()
            if sha256(target_raw) != declared_digest:
                refuse(
                    "digest_binding_mismatch",
                    f"{context}: digest differs for {relative}",
                )
            if declared_count is not None and declared_count != str(
                len(target_raw)
            ):
                refuse(
                    "digest_binding_mismatch",
                    f"{context}: byte count differs for {relative}",
                )
            shape_counts[shape] += 1
            binding_edges.append(
                {
                    "member_path": member_path,
                    "member_pointer": pointer,
                    "shape": shape,
                    "target_repository_path": relative,
                    "target_raw_sha256": declared_digest,
                    "target_byte_count_decimal": (
                        declared_count if declared_count is not None else ""
                    ),
                }
            )
        for key, child in node.items():
            walk_bindings(member_path, child, f"{pointer}/{pointer_escape(key)}")

    for role, relative, raw, document in loaded:
        walk_bindings(relative, document, "")

    projection = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002i_offline_resolution_projection",
        "suite_id": SUITE_ID,
        "universe_binding": {
            "raw_sha256": sha256(universe_raw),
            "member_count_decimal": str(len(loaded)),
        },
        "census": {
            "registry_count_decimal": str(len(registry)),
            "reference_edge_count_decimal": str(len(reference_edges)),
            "binding_edge_count_decimal": str(len(binding_edges)),
            "binding_shape_counts_decimal": {
                shape: str(count) for shape, count in sorted(shape_counts.items())
            },
        },
        "reference_edges": reference_edges,
        "binding_edges": binding_edges,
        "claim_boundary": {
            "declared_universe_and_shapes_only": True,
            "historical_residue_identities_resolved": False,
            "product_identity_computed": False,
            "profile_issued": False,
            "prq_002_closed": False,
            "gate_a_complete": False,
            "publication_authorized": False,
        },
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002i_offline_resolution_result",
        "suite_id": SUITE_ID,
        "implementation_id": IMPLEMENTATION_ID,
        "implementation_role": "python",
        "projection_sha256": sha256(compact_bytes(projection)),
        "projection": projection,
    }
    sys.stdout.buffer.write(compact_bytes(result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as refusal:
        sys.stdout.buffer.write(
            compact_bytes(
                {
                    "schema_version": SCHEMA_VERSION,
                    "artifact_class": "prq_002i_offline_resolution_refusal",
                    "suite_id": SUITE_ID,
                    "implementation_id": IMPLEMENTATION_ID,
                    "refusal_code": refusal.code,
                    "detail": refusal.detail,
                }
            )
        )
        sys.exit(1)
