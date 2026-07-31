"""Validate the PRQ-002I offline-resolution and binding-replay suite.

Dedicated parent validator and third recomputation path: it regenerates the
universe manifest from the same explicit rules, loads every member under an
in-memory overlay, rebuilds the schema registry, re-walks every `$ref` and
every declared digest binding itself, and requires both retained projections
to equal that third derivation exactly — then verifies the execution and
comparison receipts, executes an embedded known-bad corpus in which every
mutation refuses with its declared singleton code, and supports
`--recompute-all` re-execution of both runners against the retained result
bytes.

Bounded architecture evidence only: the closure claim covers the declared
universe and binding shapes at the retaining commit; the four named
historical residue identities remain unresolved by design; no product
identity, issuance, PRQ-002 closure, Gate A acceptance, or
runtime/publication authority follows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SUITE_PREFIX = "tests/profile-0-3-offline-resolution"
SUITE = ROOT / SUITE_PREFIX
SUITE_ID = "prq-002i-offline-resolution.0001"
URN_PREFIX = "urn:odeya:schema:"
SKIP_WALK_KEYS = {"const", "enum", "examples", "default"}
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
SUITE_REFUSAL_CODES = (
    "authority_nonclaim_violation",
    "census_decimal_typing_violation",
    "digest_binding_mismatch",
    "execution_binding_mismatch",
    "offline_resolution_violation",
    "out_of_repository_target",
    "projection_comparison_mismatch",
    "retained_projection_mismatch",
    "source_separation_violation",
    "universe_census_mismatch",
    "universe_member_violation",
)
RETAINED_SUITE_PATHS = (
    f"{SUITE_PREFIX}/README.md",
    f"{SUITE_PREFIX}/manifest.json",
    f"{SUITE_PREFIX}/universe-manifest.json",
    f"{SUITE_PREFIX}/authoring/generate_universe.py",
    f"{SUITE_PREFIX}/authoring/generate_suite_metadata.py",
    f"{SUITE_PREFIX}/authoring/retain_results.py",
    f"{SUITE_PREFIX}/python/runner.py",
    f"{SUITE_PREFIX}/python/dependency-lock.json",
    f"{SUITE_PREFIX}/python/source-manifest.json",
    f"{SUITE_PREFIX}/node/runner.mjs",
    f"{SUITE_PREFIX}/node/package.json",
    f"{SUITE_PREFIX}/node/package-lock.json",
    f"{SUITE_PREFIX}/node/source-manifest.json",
    f"{SUITE_PREFIX}/results/python-resolution-result.json",
    f"{SUITE_PREFIX}/results/node-resolution-result.json",
    f"{SUITE_PREFIX}/results/python-execution-receipt.json",
    f"{SUITE_PREFIX}/results/node-execution-receipt.json",
    f"{SUITE_PREFIX}/results/comparison-receipt.json",
)


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


class RepositoryView:
    def __init__(self, overlay: dict[str, bytes] | None = None) -> None:
        self.overlay = overlay or {}

    def read_bytes(self, relative: str) -> bytes:
        if relative in self.overlay:
            return self.overlay[relative]
        if relative.startswith("/") or ".." in relative.split("/"):
            refuse(
                "out_of_repository_target",
                f"path escapes the repository: {relative!r}",
            )
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            refuse(
                "universe_member_violation",
                f"{relative}: not a regular non-symlink repository file",
            )
        return path.read_bytes()

    def parse(self, relative: str) -> Any:
        def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, value in items:
                if key in result:
                    refuse(
                        "universe_member_violation",
                        f"{relative}: duplicate member name {key!r}",
                    )
                result[key] = value
            return result

        try:
            return json.loads(
                self.read_bytes(relative).decode("utf-8"),
                object_pairs_hook=pairs,
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
            refuse(
                "universe_member_violation", f"{relative}: invalid JSON: {exc}"
            )


def require_decimal(value: Any, context: str) -> None:
    if not isinstance(value, str) or not DECIMAL_RE.fullmatch(value):
        refuse(
            "census_decimal_typing_violation",
            f"{context}: count is not a decimal string",
        )


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


def third_path_derive(view: RepositoryView) -> dict[str, Any]:
    universe_raw = view.read_bytes(f"{SUITE_PREFIX}/universe-manifest.json")
    universe = view.parse(f"{SUITE_PREFIX}/universe-manifest.json")
    if (
        universe.get("suite_id") != SUITE_ID
        or universe.get("answer_free") is not True
        or universe.get("verification_time_directory_discovery_allowed")
        is not False
        or universe.get("network_access_allowed") is not False
        or universe.get("authority_claim_allowed") is not False
    ):
        refuse("universe_census_mismatch", "universe identity flags differ")
    members = universe.get("members")
    require_decimal(
        universe.get("member_count_decimal"), "universe.member_count"
    )
    if not isinstance(members, list) or universe.get(
        "member_count_decimal"
    ) != str(len(members)):
        refuse("universe_census_mismatch", "universe member census differs")
    residue = universe.get("named_residue_identities_outside_universe")
    if residue != [
        "command-contract-registry:0.1.0",
        "command-receipt:0.3.0",
        "work-contract:0.1.0",
        "command-envelope:0.4.0",
    ]:
        refuse(
            "universe_census_mismatch",
            "named residue identities differ from the frozen declaration",
        )
    role_counts: dict[str, int] = {}
    loaded: list[tuple[str, str, bytes, Any]] = []
    seen: set[str] = set()
    for member in members:
        role = member.get("role")
        relative = member.get("repository_path")
        if not isinstance(role, str) or not isinstance(relative, str):
            refuse("universe_census_mismatch", "malformed universe member")
        if relative in seen:
            refuse("universe_census_mismatch", f"duplicate member {relative}")
        seen.add(relative)
        role_counts[role] = role_counts.get(role, 0) + 1
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        loaded.append((role, relative, raw, document))
    if universe.get("role_counts_decimal") != {
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
                f"{schema_id}#{pointer}: dynamic reference is not "
                "offline-resolvable",
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
    shape_counts = {"path": 0, "repository_path": 0, "schema_path": 0}

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
            return (
                "path",
                node["path"],
                node["raw_digest"],
                str(node["byte_count"]),
            )
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
            target_raw = view.read_bytes(relative)
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

    return {
        "universe_raw": universe_raw,
        "member_count": len(loaded),
        "registry_count": len(registry),
        "reference_edges": reference_edges,
        "binding_edges": binding_edges,
        "shape_counts": shape_counts,
    }


def results_validate(view: RepositoryView, derivation: dict[str, Any]) -> None:
    results: dict[str, tuple[bytes, Any]] = {}
    for role in ("python", "node"):
        relative = f"{SUITE_PREFIX}/results/{role}-resolution-result.json"
        document = view.parse(relative)
        if (
            document.get("artifact_class")
            != "prq_002i_offline_resolution_result"
            or document.get("suite_id") != SUITE_ID
            or document.get("implementation_role") != role
        ):
            refuse(
                "source_separation_violation",
                f"{relative}: implementation identity differs from its role",
            )
        expected_id = (
            "python-stdlib-offline-resolver.0001"
            if role == "python"
            else "nodejs-native-offline-resolver.0001"
        )
        if document.get("implementation_id") != expected_id:
            refuse(
                "source_separation_violation",
                f"{relative}: implementation id differs from its role",
            )
        projection = document.get("projection")
        if document.get("projection_sha256") != sha256(
            compact_bytes(projection)
        ):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: projection digest does not bind the projection",
            )
        results[role] = (view.read_bytes(relative), document)
    python_projection = compact_bytes(results["python"][1]["projection"])
    node_projection = compact_bytes(results["node"][1]["projection"])
    if python_projection != node_projection:
        refuse(
            "projection_comparison_mismatch",
            "retained projections are not byte-identical",
        )
    projection = results["python"][1]["projection"]
    binding = projection.get("universe_binding", {})
    require_decimal(
        binding.get("member_count_decimal"), "projection.universe.member_count"
    )
    if (
        binding.get("raw_sha256") != sha256(derivation["universe_raw"])
        or binding.get("member_count_decimal")
        != str(derivation["member_count"])
    ):
        refuse(
            "execution_binding_mismatch",
            "retained projection does not bind the exact universe bytes",
        )
    census = projection.get("census", {})
    for key, expected in (
        ("registry_count_decimal", str(derivation["registry_count"])),
        (
            "reference_edge_count_decimal",
            str(len(derivation["reference_edges"])),
        ),
        ("binding_edge_count_decimal", str(len(derivation["binding_edges"]))),
    ):
        require_decimal(census.get(key), f"projection.census.{key}")
        if census.get(key) != expected:
            refuse(
                "retained_projection_mismatch",
                f"retained census {key} differs from the third derivation",
            )
    shape_census = census.get("binding_shape_counts_decimal")
    if shape_census != {
        shape: str(count)
        for shape, count in sorted(derivation["shape_counts"].items())
    }:
        refuse(
            "retained_projection_mismatch",
            "retained binding-shape census differs from the third derivation",
        )
    if compact_bytes(projection.get("reference_edges")) != compact_bytes(
        derivation["reference_edges"]
    ):
        refuse(
            "retained_projection_mismatch",
            "retained reference edges differ from the third derivation",
        )
    if compact_bytes(projection.get("binding_edges")) != compact_bytes(
        derivation["binding_edges"]
    ):
        refuse(
            "retained_projection_mismatch",
            "retained binding edges differ from the third derivation",
        )
    boundary = projection.get("claim_boundary", {})
    if boundary.get("declared_universe_and_shapes_only") is not True:
        refuse(
            "authority_nonclaim_violation",
            "retained projection widens the declared closure scope",
        )
    for claim in (
        "historical_residue_identities_resolved",
        "product_identity_computed",
        "profile_issued",
        "prq_002_closed",
        "gate_a_complete",
        "publication_authorized",
    ):
        if boundary.get(claim) is not False:
            refuse(
                "authority_nonclaim_violation",
                f"retained projection flips nonclaim {claim}",
            )
    for role in ("python", "node"):
        source_manifest = view.parse(
            f"{SUITE_PREFIX}/{role}/source-manifest.json"
        )
        for source_row in source_manifest.get("source_files", []):
            bound_raw = view.read_bytes(source_row.get("repository_path"))
            if (
                source_row.get("raw_sha256") != sha256(bound_raw)
                or source_row.get("byte_count_decimal")
                != str(len(bound_raw))
            ):
                refuse(
                    "source_separation_violation",
                    f"{role} source manifest does not bind current source bytes",
                )
        for flag in (
            "private_expectation_consumption_allowed",
            "peer_source_consumption_allowed",
            "peer_result_consumption_allowed",
            "network_access_requested",
        ):
            if source_manifest.get(flag) is not False:
                refuse(
                    "source_separation_violation",
                    f"{role} source manifest flips separation flag {flag}",
                )
        relative = f"{SUITE_PREFIX}/results/{role}-execution-receipt.json"
        receipt = view.parse(relative)
        if (
            receipt.get("artifact_class")
            != "prq_002i_offline_resolution_execution_receipt"
            or receipt.get("suite_id") != SUITE_ID
            or receipt.get("self_attested_byte_consistency_record") is not True
            or receipt.get("independently_witnessed_process_evidence")
            is not False
        ):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: receipt identity or attestation class differs",
            )
        for binding_key, bound_relative in (
            (
                "source_manifest_binding",
                f"{SUITE_PREFIX}/{role}/source-manifest.json",
            ),
            (
                "runner_binding",
                f"{SUITE_PREFIX}/python/runner.py"
                if role == "python"
                else f"{SUITE_PREFIX}/node/runner.mjs",
            ),
            ("universe_binding", f"{SUITE_PREFIX}/universe-manifest.json"),
            (
                "result_binding",
                f"{SUITE_PREFIX}/results/{role}-resolution-result.json",
            ),
        ):
            bound_raw = view.read_bytes(bound_relative)
            entry = receipt.get(binding_key, {})
            if (
                entry.get("raw_sha256") != sha256(bound_raw)
                or entry.get("byte_count_decimal") != str(len(bound_raw))
            ):
                refuse(
                    "execution_binding_mismatch",
                    f"{relative}: {binding_key} does not bind current bytes",
                )
        if receipt.get("executable_binding_pre") != receipt.get(
            "executable_binding_post"
        ):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: executable changed between pre and post binding",
            )
    comparison = view.parse(f"{SUITE_PREFIX}/results/comparison-receipt.json")
    if (
        comparison.get("artifact_class")
        != "prq_002i_offline_resolution_comparison_receipt"
        or comparison.get("projections_byte_identical") is not True
        or comparison.get("comparison_method")
        != "exact_projection_byte_equality"
        or comparison.get("canonical_scientific_evidence") is not False
    ):
        refuse(
            "projection_comparison_mismatch",
            "comparison receipt identity or method differs",
        )
    if comparison.get("projection_sha256") != sha256(python_projection):
        refuse(
            "projection_comparison_mismatch",
            "comparison receipt does not bind the retained projection digest",
        )
    for binding_key, bound_relative in (
        ("suite_manifest_binding", f"{SUITE_PREFIX}/manifest.json"),
        ("universe_binding", f"{SUITE_PREFIX}/universe-manifest.json"),
        (
            "universe_generator_binding",
            f"{SUITE_PREFIX}/authoring/generate_universe.py",
        ),
        (
            "validator_binding",
            "scripts/validate_profile_0_3_offline_resolution.py",
        ),
    ):
        bound_raw = view.read_bytes(bound_relative)
        entry = comparison.get(binding_key, {})
        if (
            entry.get("raw_sha256") != sha256(bound_raw)
            or entry.get("byte_count_decimal") != str(len(bound_raw))
        ):
            refuse(
                "projection_comparison_mismatch",
                f"comparison receipt {binding_key} does not bind current bytes",
            )
    for group, expected_paths in (
        (
            "source_manifest_bindings",
            [
                f"{SUITE_PREFIX}/python/source-manifest.json",
                f"{SUITE_PREFIX}/node/source-manifest.json",
            ],
        ),
        (
            "result_bindings",
            [
                f"{SUITE_PREFIX}/results/python-resolution-result.json",
                f"{SUITE_PREFIX}/results/node-resolution-result.json",
            ],
        ),
        (
            "execution_receipt_bindings",
            [
                f"{SUITE_PREFIX}/results/python-execution-receipt.json",
                f"{SUITE_PREFIX}/results/node-execution-receipt.json",
            ],
        ),
    ):
        group_rows = comparison.get(group)
        if not isinstance(group_rows, list) or [
            row.get("repository_path") for row in group_rows
        ] != expected_paths:
            refuse(
                "projection_comparison_mismatch",
                f"comparison receipt {group} census differs",
            )
        for row in group_rows:
            bound_raw = view.read_bytes(row.get("repository_path"))
            if (
                row.get("raw_sha256") != sha256(bound_raw)
                or row.get("byte_count_decimal") != str(len(bound_raw))
            ):
                refuse(
                    "projection_comparison_mismatch",
                    f"comparison receipt {group} does not bind current bytes",
                )


def census_validate(view: RepositoryView, derivation: dict[str, Any]) -> None:
    manifest = view.parse(f"{SUITE_PREFIX}/manifest.json")
    census = manifest.get("census", {})
    for key, expected in (
        ("universe_member_count_decimal", str(derivation["member_count"])),
        ("registry_count_decimal", str(derivation["registry_count"])),
        (
            "reference_edge_count_decimal",
            str(len(derivation["reference_edges"])),
        ),
        ("binding_edge_count_decimal", str(len(derivation["binding_edges"]))),
        ("source_separated_implementation_count_decimal", "2"),
        ("gate_known_bad_count_decimal", str(len(KNOWN_BADS))),
    ):
        require_decimal(census.get(key), f"manifest.census.{key}")
        if census.get(key) != expected:
            refuse("universe_census_mismatch", f"manifest census {key} differs")
    if manifest.get("suite_refusal_codes") != list(SUITE_REFUSAL_CODES):
        refuse(
            "universe_census_mismatch",
            "manifest suite refusal-code vocabulary differs",
        )
    for claim, value in manifest.get("claim_boundary", {}).items():
        if value is not False:
            refuse(
                "authority_nonclaim_violation",
                f"manifest claim boundary flips nonclaim {claim}",
            )


def run_static(view: RepositoryView) -> dict[str, Any]:
    derivation = third_path_derive(view)
    census_validate(view, derivation)
    results_validate(view, derivation)
    return derivation


# --- known-bad corpus ---------------------------------------------------------


def mutate_json(relative: str, transform: Callable[[Any], Any]) -> dict[str, bytes]:
    document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    document = transform(document) or document
    raw = (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False)
        + "\n"
    ).encode("utf-8")
    return {relative: raw}


def mutate_bytes(relative: str, old: bytes, new: bytes) -> dict[str, bytes]:
    raw = (ROOT / relative).read_bytes()
    if raw.count(old) < 1:
        raise AssertionError(
            f"known-bad anchor missing in {relative}: {old[:60]!r}"
        )
    return {relative: raw.replace(old, new, 1)}


UNIVERSE = f"{SUITE_PREFIX}/universe-manifest.json"
MANIFEST = f"{SUITE_PREFIX}/manifest.json"
PY_RESULT = f"{SUITE_PREFIX}/results/python-resolution-result.json"
ND_RESULT = f"{SUITE_PREFIX}/results/node-resolution-result.json"
PY_RECEIPT = f"{SUITE_PREFIX}/results/python-execution-receipt.json"
COMPARISON = f"{SUITE_PREFIX}/results/comparison-receipt.json"
PY_SOURCE_MANIFEST = f"{SUITE_PREFIX}/python/source-manifest.json"
SAMPLE_SCHEMA = "schemas/adjudication.schema.json"


def _flip_digest(digest: str) -> str:
    return digest[:-1] + ("0" if digest[-1] != "0" else "1")


def coherent_result_mutation(transform: Callable[[Any], Any]) -> dict[str, bytes]:
    overlay: dict[str, bytes] = {}
    for relative in (PY_RESULT, ND_RESULT):
        document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        document = transform(document) or document
        document["projection_sha256"] = sha256(
            compact_bytes(document["projection"])
        )
        overlay[relative] = compact_bytes(document)
    return overlay


def _kb_universe_member_drop() -> dict[str, bytes]:
    return mutate_json(UNIVERSE, lambda d: (d["members"].pop(), d)[1])


def _kb_universe_member_duplicate() -> dict[str, bytes]:
    return mutate_json(
        UNIVERSE, lambda d: (d["members"].append(dict(d["members"][0])), d)[1]
    )


def _kb_universe_count_tamper() -> dict[str, bytes]:
    document = json.loads((ROOT / UNIVERSE).read_text(encoding="utf-8"))
    count = document["member_count_decimal"]
    return mutate_bytes(
        UNIVERSE,
        f'"member_count_decimal": "{count}"'.encode(),
        f'"member_count_decimal": "{int(count) + 1}"'.encode(),
    )


def _kb_universe_flag_flip() -> dict[str, bytes]:
    return mutate_bytes(
        UNIVERSE,
        b'"network_access_allowed": false',
        b'"network_access_allowed": true',
    )


def _kb_universe_residue_drop() -> dict[str, bytes]:
    return mutate_json(
        UNIVERSE,
        lambda d: (d["named_residue_identities_outside_universe"].pop(), d)[1],
    )


def _kb_schema_http_ref_injection() -> dict[str, bytes]:
    raw = (ROOT / SAMPLE_SCHEMA).read_bytes()
    anchor = b'"$defs": {'
    injected = b'"$defs": {"kb_injected": {"$ref": "https://example.com/x.json"},'
    if raw.count(anchor) != 1:
        raise AssertionError("schema $defs anchor missing")
    return {SAMPLE_SCHEMA: raw.replace(anchor, injected, 1)}


def _kb_schema_unknown_urn_ref() -> dict[str, bytes]:
    raw = (ROOT / SAMPLE_SCHEMA).read_bytes()
    anchor = b'"$defs": {'
    injected = (
        b'"$defs": {"kb_injected": '
        b'{"$ref": "urn:odeya:schema:not-a-real-schema:9.9.9"},'
    )
    if raw.count(anchor) != 1:
        raise AssertionError("schema $defs anchor missing")
    return {SAMPLE_SCHEMA: raw.replace(anchor, injected, 1)}


def _kb_bound_target_drift() -> dict[str, bytes]:
    # Mutate a file that retained bindings point at; every digest edge into it
    # must break.
    target = "tests/profile-0-3-jcs-conformance/vectors.json"
    raw = (ROOT / target).read_bytes()
    return {target: raw + b"\n"}


def _kb_manifest_census_tamper() -> dict[str, bytes]:
    document = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    count = document["census"]["reference_edge_count_decimal"]
    return mutate_bytes(
        MANIFEST,
        f'"reference_edge_count_decimal": "{count}"'.encode(),
        f'"reference_edge_count_decimal": "{int(count) + 1}"'.encode(),
    )


def _kb_manifest_known_bad_census() -> dict[str, bytes]:
    document = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    count = document["census"]["gate_known_bad_count_decimal"]
    return mutate_bytes(
        MANIFEST,
        f'"gate_known_bad_count_decimal": "{count}"'.encode(),
        f'"gate_known_bad_count_decimal": "{int(count) + 1}"'.encode(),
    )


def _kb_manifest_authority_flip() -> dict[str, bytes]:
    return mutate_bytes(
        MANIFEST, b'"gate_a_complete": false', b'"gate_a_complete": true'
    )


def _kb_result_ref_edge_drop() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["reference_edges"].pop()
        return document

    return coherent_result_mutation(transform)


def _kb_result_ref_digest_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        row = document["projection"]["reference_edges"][0]
        row["target_raw_sha256"] = _flip_digest(row["target_raw_sha256"])
        return document

    return coherent_result_mutation(transform)


def _kb_result_binding_edge_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        row = document["projection"]["binding_edges"][0]
        row["target_raw_sha256"] = _flip_digest(row["target_raw_sha256"])
        return document

    return coherent_result_mutation(transform)


def _kb_result_census_smuggle() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["census"]["registry_count_decimal"] = 144
        return document

    return coherent_result_mutation(transform)


def _kb_result_scope_flip() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["claim_boundary"][
            "historical_residue_identities_resolved"
        ] = True
        return document

    return coherent_result_mutation(transform)


def _kb_result_role_swap() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RESULT,
        b'"implementation_role":"python"',
        b'"implementation_role":"node"',
    )


def _kb_result_copy_across() -> dict[str, bytes]:
    return {ND_RESULT: (ROOT / PY_RESULT).read_bytes()}


def _kb_result_sha_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection_sha256"] = _flip_digest(
            document["projection_sha256"]
        )
        return document

    return mutate_json(PY_RESULT, transform)


def _kb_receipt_source_binding_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["source_manifest_binding"]["raw_sha256"] = _flip_digest(
            document["source_manifest_binding"]["raw_sha256"]
        )
        return document

    return mutate_json(PY_RECEIPT, transform)


def _kb_receipt_attestation_flip() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RECEIPT,
        b'"independently_witnessed_process_evidence": false',
        b'"independently_witnessed_process_evidence": true',
    )


def _kb_source_manifest_drift() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["source_files"][0]["raw_sha256"] = _flip_digest(
            document["source_files"][0]["raw_sha256"]
        )
        return document

    return mutate_json(PY_SOURCE_MANIFEST, transform)


def _kb_source_manifest_peer_flip() -> dict[str, bytes]:
    return mutate_bytes(
        PY_SOURCE_MANIFEST,
        b'"peer_result_consumption_allowed": false',
        b'"peer_result_consumption_allowed": true',
    )


def _kb_comparison_sha_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection_sha256"] = _flip_digest(
            document["projection_sha256"]
        )
        return document

    return mutate_json(COMPARISON, transform)


def _kb_comparison_validator_unbind() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["validator_binding"]["raw_sha256"] = _flip_digest(
            document["validator_binding"]["raw_sha256"]
        )
        return document

    return mutate_json(COMPARISON, transform)


def _kb_comparison_method_downgrade() -> dict[str, bytes]:
    return mutate_bytes(
        COMPARISON,
        b'"comparison_method": "exact_projection_byte_equality"',
        b'"comparison_method": "digest_only"',
    )


KNOWN_BADS: tuple[tuple[str, str, str, Callable[[], dict[str, bytes]]], ...] = (
    ("universe-member-drop", "universe", "universe_census_mismatch", _kb_universe_member_drop),
    ("universe-member-duplicate", "universe", "universe_census_mismatch", _kb_universe_member_duplicate),
    ("universe-count-tamper", "universe", "universe_census_mismatch", _kb_universe_count_tamper),
    ("universe-flag-flip", "universe", "universe_census_mismatch", _kb_universe_flag_flip),
    ("universe-residue-drop", "universe", "universe_census_mismatch", _kb_universe_residue_drop),
    ("schema-http-ref-injection", "resolution", "offline_resolution_violation", _kb_schema_http_ref_injection),
    ("schema-unknown-urn-ref", "resolution", "offline_resolution_violation", _kb_schema_unknown_urn_ref),
    ("bound-target-drift", "resolution", "digest_binding_mismatch", _kb_bound_target_drift),
    ("manifest-census-tamper", "census", "universe_census_mismatch", _kb_manifest_census_tamper),
    ("manifest-known-bad-census", "census", "universe_census_mismatch", _kb_manifest_known_bad_census),
    ("manifest-authority-flip", "census", "authority_nonclaim_violation", _kb_manifest_authority_flip),
    ("result-ref-edge-drop", "results", "retained_projection_mismatch", _kb_result_ref_edge_drop),
    ("result-ref-digest-tamper", "results", "retained_projection_mismatch", _kb_result_ref_digest_tamper),
    ("result-binding-edge-tamper", "results", "retained_projection_mismatch", _kb_result_binding_edge_tamper),
    ("result-census-smuggle", "results", "census_decimal_typing_violation", _kb_result_census_smuggle),
    ("result-scope-flip", "results", "authority_nonclaim_violation", _kb_result_scope_flip),
    ("result-role-swap", "results", "source_separation_violation", _kb_result_role_swap),
    ("result-copy-across", "results", "source_separation_violation", _kb_result_copy_across),
    ("result-sha-tamper", "results", "execution_binding_mismatch", _kb_result_sha_tamper),
    ("receipt-source-binding-tamper", "results", "execution_binding_mismatch", _kb_receipt_source_binding_tamper),
    ("receipt-attestation-flip", "results", "execution_binding_mismatch", _kb_receipt_attestation_flip),
    ("source-manifest-drift", "results", "source_separation_violation", _kb_source_manifest_drift),
    ("source-manifest-peer-flip", "results", "source_separation_violation", _kb_source_manifest_peer_flip),
    ("comparison-sha-tamper", "results", "projection_comparison_mismatch", _kb_comparison_sha_tamper),
    ("comparison-validator-unbind", "results", "projection_comparison_mismatch", _kb_comparison_validator_unbind),
    ("comparison-method-downgrade", "results", "projection_comparison_mismatch", _kb_comparison_method_downgrade),
)


def run_known_bads() -> int:
    failures: list[str] = []
    for name, _, expected_code, factory in KNOWN_BADS:
        overlay = factory()
        try:
            run_static(RepositoryView(overlay))
        except Refusal as refusal:
            if refusal.code != expected_code:
                failures.append(
                    f"{name}: refused with {refusal.code}, expected {expected_code}"
                )
        else:
            failures.append(f"{name}: mutation was accepted")
    for failure in failures:
        print(f"KNOWN-BAD FAILURE: {failure}")
    return len(failures)


def recompute_all(python_executable: str, node_executable: str) -> list[str]:
    errors: list[str] = []
    for role, executable, extra, runner in (
        ("python", python_executable, ["-I", "-B"], SUITE / "python/runner.py"),
        ("node", node_executable, ["--disable-proto=throw"], SUITE / "node/runner.mjs"),
    ):
        resolved = Path(executable).resolve(strict=True)
        completed = subprocess.run(
            [
                resolved.as_posix(),
                *extra,
                runner.as_posix(),
                "--repository-root",
                ROOT.as_posix(),
                "--universe",
                (SUITE / "universe-manifest.json").as_posix(),
                "--source-manifest",
                (SUITE / role / "source-manifest.json").as_posix(),
            ],
            cwd=ROOT,
            env={
                "PATH": resolved.parent.as_posix(),
                "LANG": "C",
                "LC_ALL": "C",
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            },
            capture_output=True,
            timeout=120,
            check=False,
        )
        retained = (SUITE / f"results/{role}-resolution-result.json").read_bytes()
        if completed.returncode != 0 or completed.stderr:
            errors.append(f"{role}: fresh execution failed")
        elif completed.stdout != retained:
            errors.append(
                f"{role}: fresh stdout differs from retained result bytes"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--recompute-all", action="store_true")
    parser.add_argument("--python-executable")
    parser.add_argument("--node-executable")
    arguments = parser.parse_args()

    for relative in RETAINED_SUITE_PATHS:
        target = ROOT / relative
        if target.is_symlink() or not target.is_file():
            print(f"PRQ-002I missing or non-regular retained path: {relative}")
            return 1
    generated = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            (SUITE / "authoring/generate_universe.py").as_posix(),
            "--check",
        ],
        cwd=ROOT,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if generated.returncode != 0:
        print("PRQ-002I universe differs from deterministic regeneration")
        return 1
    try:
        derivation = run_static(RepositoryView())
    except Refusal as refusal:
        print(f"PRQ-002I REFUSED [{refusal.code}]: {refusal.detail}")
        return 1
    if run_known_bads():
        return 1
    if arguments.recompute_all:
        if not arguments.python_executable or not arguments.node_executable:
            print(
                "--recompute-all requires --python-executable and "
                "--node-executable"
            )
            return 1
        errors = recompute_all(
            arguments.python_executable, arguments.node_executable
        )
        if errors:
            for error in errors:
                print(f"PRQ-002I RECOMPUTE FAILURE: {error}")
            return 1
    print(
        "PRQ-002I offline-resolution retained evidence passed: "
        f"universe={derivation['member_count']} members, "
        f"registry={derivation['registry_count']}, "
        f"reference_edges={len(derivation['reference_edges'])}, "
        f"binding_edges={len(derivation['binding_edges'])}, "
        f"known_bads={len(KNOWN_BADS)}; "
        "closure_scope=declared_universe_and_shapes_only; "
        "residue_identities=named_not_resolved; identity=false, "
        "issuance=false, gate_a=false, authority=false"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
