#!/usr/bin/env python3
"""Deterministic architecture-schema audit against proposed odeya-jcs-0.1."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
FIXTURE_DIRS = (
    ROOT / "tests/architecture-schema/fixtures",
    ROOT / "tests/architecture-review/fixtures",
    ROOT / "tests/cognitive-contracts/fixtures",
    ROOT / "tests/projection-contracts/fixtures",
    ROOT / "tests/physical-contracts/fixtures",
    ROOT / "tests/mathematical-contracts/fixtures",
)
OUTPUT = Path(__file__).resolve().parent / "SCHEMA_AUDIT.json"
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"
FIXED_TIME_PATTERN = (
    "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:"
    "[0-9]{2}\\.[0-9]{6}Z$"
)
FIXED_TIME_VALUE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"
)
RFC3339_LIKE_VALUE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
# The name filter is a heuristic and produced verified false negatives: fields
# with genuinely decimal shapes -- model_tokens beside seven governed siblings
# in the same resource budget, the affine conversion offset beside its governed
# scale, noninferiority margins, interval lower/upper beside their governed
# level, traffic_fraction, horizon, limit -- carried no finding because their
# names missed the list. Review verified at least twenty such fields. The shape
# test (a decimal $ref or decimal pattern) is the real discriminator; the name
# list exists only to skip identifier-like strings, so it must err wide.
SCIENTIFIC_FIELD = re.compile(
    r"(?:value|estimate|threshold|probability|confidence|cost|budget|duration|"
    r"seconds|hours|bytes|rate|ratio|level|bound|mean|variance|deviation|"
    r"uncertainty|precision|scale|amount|quantity|tokens|offset|margin|lower|"
    r"upper|fraction|horizon|limit|baseline|candidate|point|decimal|factor|"
    r"correlation|matrix)",
    re.IGNORECASE,
)


class DuplicateKey(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text("utf-8"), object_pairs_hook=strict_pairs)
    if not isinstance(value, dict):
        raise ValueError(f"schema root is not an object: {path}")
    return value


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return sha256(encoded)


def escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def pointer(parts: tuple[str, ...]) -> str:
    return "/" + "/".join(escape(part) for part in parts) if parts else ""


def walk(value: Any, parts: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    yield parts, value
    if isinstance(value, dict):
        for key in sorted(value):
            yield from walk(value[key], parts + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, parts + (str(index),))


def resolve_pointer(schema: dict[str, Any], reference: str) -> tuple[bool, Any]:
    current: Any = schema
    try:
        for raw in reference[2:].split("/"):
            token = raw.replace("~1", "/").replace("~0", "~")
            current = current[token]
    except (KeyError, TypeError):
        return False, None
    return True, current


def resolve_local(schema: dict[str, Any], node: Any) -> Any:
    if not isinstance(node, dict):
        return node
    reference = node.get("$ref")
    if not isinstance(reference, str) or not reference.startswith("#/"):
        return node
    resolved, current = resolve_pointer(schema, reference)
    return current if resolved else node


def dangling_local_refs(schema: dict[str, Any]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for parts, node in walk(schema):
        if not isinstance(node, dict):
            continue
        reference = node.get("$ref")
        if not isinstance(reference, str) or not reference.startswith("#/"):
            continue
        resolved, _ = resolve_pointer(schema, reference)
        if not resolved:
            results.append({"path": pointer(parts), "ref": reference})
    return results


def property_nodes(
    value: Any, parts: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], str, dict[str, Any]]]:
    if not isinstance(value, dict):
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from property_nodes(item, parts + (str(index),))
        return
    properties = value.get("properties")
    if isinstance(properties, dict):
        for name in sorted(properties):
            node = properties[name]
            if isinstance(node, dict):
                yield parts + ("properties", name), name, node
            yield from property_nodes(node, parts + ("properties", name))
    for key in sorted(value):
        if key == "properties":
            continue
        yield from property_nodes(value[key], parts + (key,))


def datetime_nodes(schema: dict[str, Any]) -> tuple[list[str], list[str]]:
    fixed: set[str] = set()
    unprofiled: set[str] = set()
    for parts, node in walk(schema):
        if not isinstance(node, dict):
            continue
        resolved = resolve_local(schema, node)
        if not isinstance(resolved, dict) or resolved.get("format") != "date-time":
            continue
        target = fixed if resolved.get("pattern") == FIXED_TIME_PATTERN else unprofiled
        target.add(pointer(parts))
    return sorted(fixed), sorted(unprofiled)


def number_nodes(schema: dict[str, Any]) -> list[str]:
    results: list[str] = []
    for parts, node in walk(schema):
        if not isinstance(node, dict):
            continue
        declared = node.get("type")
        if declared == "number" or (isinstance(declared, list) and "number" in declared):
            results.append(pointer(parts))
    return sorted(set(results))


DECIMAL_REF_NAMES = {
    "decimal",
    "decimal_string",
    "quantity",
    "exact_decimal",
    "nonnegative_decimal",
    "fraction",
}


def decimal_shape(schema: dict[str, Any], node: Any, depth: int = 0) -> bool:
    """Shape-first decimal detection, descending unions and array items.

    Two structural blind spots survived two corrections of this detector: a
    nullable decimal inside oneOf/anyOf was invisible, and an array of decimals
    -- a covariance matrix -- was invisible, because only the property node
    itself was tested. Review enumerated seventeen ungoverned decimal leaves
    across six schemas, two of them scientific schemas with zero findings. The
    shape test now recurses; a datetime branch is excluded at every level. A
    datetime is never a scientific decimal (ADR 0033); the frozen microsecond
    timestamp pattern contains digits and an escaped dot, so the pattern
    heuristic must test that exclusion wherever it tests the pattern.
    """
    if depth > 4 or not isinstance(node, dict):
        return False
    reference = node.get("$ref", "")
    if isinstance(reference, str) and reference.rsplit("/", 1)[-1] in DECIMAL_REF_NAMES:
        return True
    resolved = resolve_local(schema, node)
    if not isinstance(resolved, dict):
        return False
    if resolved.get("format") == "date-time":
        return False
    pattern = resolved.get("pattern")
    if isinstance(pattern, str) and "[0-9]" in pattern and (
        "\\." in pattern or "[.]" in pattern
    ):
        return True
    for key in ("oneOf", "anyOf"):
        branches = resolved.get(key)
        if isinstance(branches, list):
            for branch in branches:
                if decimal_shape(schema, branch, depth + 1):
                    return True
    items = resolved.get("items")
    if isinstance(items, dict) and decimal_shape(schema, items, depth + 1):
        return True
    return False


def generic_decimal_uses(schema: dict[str, Any]) -> list[str]:
    results: set[str] = set()
    for parts, name, node in property_nodes(schema):
        if decimal_shape(schema, node) and SCIENTIFIC_FIELD.search(name):
            results.add(pointer(parts))
    return sorted(results)


def digest_fields(schema: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for parts, name, node in property_nodes(schema):
        lowered = name.lower()
        if not (
            lowered == "digest"
            or lowered.endswith("_digest")
            or lowered.endswith("_digest_observed")
        ):
            continue
        resolved = resolve_local(schema, node)
        lexical = "unconstrained_or_union"
        if isinstance(resolved, dict):
            if resolved.get("pattern") == "^sha256:[a-f0-9]{64}$":
                lexical = "sha256_lowercase_hex"
            elif resolved.get("const") is not None:
                lexical = "constant"
        scope = node.get("x-odeya-digest-scope")
        if not isinstance(scope, dict) and isinstance(resolved, dict):
            scope = resolved.get("x-odeya-digest-scope")
        results.append(
            {
                "path": pointer(parts),
                "field": name,
                "lexical_constraint": lexical,
                "scope_annotation_present": isinstance(scope, dict),
            }
        )
    return results


def canonical_profile_bindings(schema: dict[str, Any]) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for parts, name, node in property_nodes(schema):
        if name not in {"canonicalization_profile", "canonicalization_profile_id"}:
            continue
        resolved = resolve_local(schema, node)
        constant = resolved.get("const") if isinstance(resolved, dict) else None
        bindings.append(
            {
                "path": pointer(parts),
                "const": constant,
                "pins_candidate_profile": constant == PROFILE_ID,
            }
        )
    return bindings


def main() -> int:
    schema_records: list[dict[str, Any]] = []
    definition_variants: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    corpus_payload = b""
    fixture_payload = b""

    for path in sorted(SCHEMA_DIR.glob("*.json")):
        raw = path.read_bytes()
        schema = load(path)
        relative = path.relative_to(ROOT).as_posix()
        corpus_payload += relative.encode("utf-8") + b"\0" + raw + b"\0"
        fixed_time, unprofiled_time = datetime_nodes(schema)
        numbers = number_nodes(schema)
        decimals = generic_decimal_uses(schema)
        digests = digest_fields(schema)
        profile_bindings = canonical_profile_bindings(schema)
        dangling_refs = dangling_local_refs(schema)
        schema_records.append(
            {
                "path": relative,
                "schema_id": schema.get("$id"),
                "schema_version": schema.get("properties", {})
                .get("schema_version", {})
                .get("const"),
                "byte_sha256": sha256(raw),
                "fixed_microsecond_datetime_paths": fixed_time,
                "unprofiled_datetime_paths": unprofiled_time,
                "generic_json_number_paths": numbers,
                "generic_scientific_decimal_paths": decimals,
                "digest_fields": digests,
                "canonical_profile_bindings": profile_bindings,
                "dangling_local_refs": dangling_refs,
            }
        )
        definitions = schema.get("$defs", {})
        if isinstance(definitions, dict):
            for name, definition in definitions.items():
                definition_variants[name][canonical_hash(definition)].append(
                    {"schema": relative, "path": f"/$defs/{escape(name)}"}
                )

    divergent: list[dict[str, Any]] = []
    for name in sorted(definition_variants):
        variants = definition_variants[name]
        occurrence_count = sum(len(items) for items in variants.values())
        if occurrence_count < 2 or len(variants) < 2:
            continue
        divergent.append(
            {
                "definition_name": name,
                "occurrence_count": occurrence_count,
                "variant_count": len(variants),
                "variants": [
                    {"canonical_definition_sha256": digest, "occurrences": items}
                    for digest, items in sorted(variants.items())
                ],
            }
        )

    fixture_records: list[dict[str, Any]] = []
    fixture_paths = sorted(
        path
        for directory in FIXTURE_DIRS
        for path in directory.glob("*.json")
    )
    for path in fixture_paths:
        raw = path.read_bytes()
        fixture = load(path)
        relative = path.relative_to(ROOT).as_posix()
        fixture_payload += relative.encode("utf-8") + b"\0" + raw + b"\0"
        canonical_times: list[str] = []
        noncanonical_times: list[dict[str, str]] = []
        for parts, value in walk(fixture):
            if not isinstance(value, str) or RFC3339_LIKE_VALUE.fullmatch(value) is None:
                continue
            if FIXED_TIME_VALUE.fullmatch(value) is not None:
                canonical_times.append(pointer(parts))
            else:
                noncanonical_times.append({"path": pointer(parts), "value": value})
        fixture_records.append(
            {
                "path": relative,
                "byte_sha256": sha256(raw),
                "fixed_microsecond_timestamp_paths": canonical_times,
                "nonconformant_timestamp_values": noncanonical_times,
            }
        )

    unprofiled_time_count = sum(
        len(record["unprofiled_datetime_paths"]) for record in schema_records
    )
    generic_number_count = sum(
        len(record["generic_json_number_paths"]) for record in schema_records
    )
    generic_decimal_count = sum(
        len(record["generic_scientific_decimal_paths"]) for record in schema_records
    )
    digest_count = sum(len(record["digest_fields"]) for record in schema_records)
    unscoped_digest_count = sum(
        not field["scope_annotation_present"]
        for record in schema_records
        for field in record["digest_fields"]
    )
    unpinned_profile_count = sum(
        not binding["pins_candidate_profile"]
        for record in schema_records
        for binding in record["canonical_profile_bindings"]
    )
    dangling_local_ref_count = sum(
        len(record["dangling_local_refs"]) for record in schema_records
    )
    nonconformant_fixture_time_count = sum(
        len(record["nonconformant_timestamp_values"]) for record in fixture_records
    )

    blockers = []
    for finding_id, severity, count, description in (
        (
            "CANON-SCHEMA-TIME-001",
            "high",
            unprofiled_time_count,
            "date-time schema nodes do not enforce the fixed UTC microsecond lexical profile",
        ),
        (
            "CANON-SCHEMA-NUMBER-001",
            "critical",
            generic_number_count + generic_decimal_count,
            "generic JSON numbers or untyped decimal quantity fields remain in scientific/control contracts",
        ),
        (
            "CANON-SCHEMA-DIGEST-001",
            "critical",
            unscoped_digest_count,
            "digest fields lack a machine-readable subject/profile/schema/algorithm scope annotation",
        ),
        (
            "CANON-SCHEMA-DEFS-001",
            "high",
            len(divergent),
            "repeated common $defs names have structurally divergent definitions across schemas",
        ),
        (
            "CANON-SCHEMA-PROFILE-001",
            "high",
            unpinned_profile_count,
            "canonicalization profile fields are not pinned to the candidate profile identifier",
        ),
        (
            "CANON-SCHEMA-REF-001",
            "critical",
            dangling_local_ref_count,
            "local JSON Schema references do not resolve within their owning schema",
        ),
        (
            "CANON-FIXTURE-TIME-001",
            "high",
            nonconformant_fixture_time_count,
            "architecture fixtures contain timestamps outside the fixed UTC microsecond lexical profile",
        ),
    ):
        if count:
            blockers.append(
                {
                    "finding_id": finding_id,
                    "severity": severity,
                    "count": count,
                    "description": description,
                    "disposition": "blocks_profile_freeze",
                }
            )

    report = {
        "audit_version": "0.2.0",
        "profile_id": PROFILE_ID,
        "audit_basis": "deterministic working-tree schema bytes; no wall-clock input",
        "schema_corpus_sha256": sha256(corpus_payload),
        "schema_count": len(schema_records),
        "fixture_corpus_sha256": sha256(fixture_payload),
        "fixture_count": len(fixture_records),
        "fixture_roots": [
            directory.relative_to(ROOT).as_posix() for directory in FIXTURE_DIRS
        ],
        "gate_a_disposition": "blocked" if blockers else "candidate_clear",
        "summary": {
            "fixed_microsecond_datetime_path_count": sum(
                len(record["fixed_microsecond_datetime_paths"])
                for record in schema_records
            ),
            "unprofiled_datetime_path_count": unprofiled_time_count,
            "generic_json_number_path_count": generic_number_count,
            "generic_scientific_decimal_path_count": generic_decimal_count,
            "digest_field_count": digest_count,
            "digest_field_without_scope_annotation_count": unscoped_digest_count,
            "divergent_common_definition_name_count": len(divergent),
            "unpinned_canonical_profile_binding_count": unpinned_profile_count,
            "dangling_local_reference_count": dangling_local_ref_count,
            "nonconformant_fixture_timestamp_value_count": nonconformant_fixture_time_count,
        },
        "blocking_findings": blockers,
        "divergent_common_definitions": divergent,
        "schemas": schema_records,
        "fixtures": fixture_records,
        "interpretation": [
            "This is a conservative representation audit, not proof that each flagged field is scientifically wrong.",
            "A digest regex proves lexical shape only; it does not identify the hashed subject, profile, schema, or recomputation rule.",
            "Definition-name divergence can be intentional, but it must be renamed, centralized, or explicitly justified before profile freeze.",
            "No scientific meaning was changed automatically; migrations require owned schema versions and fixture updates."
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if len(sys.argv) == 2 and sys.argv[1] == "--write":
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"wrote {OUTPUT.relative_to(ROOT).as_posix()}")
        return 0
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        if not OUTPUT.is_file() or OUTPUT.read_text("utf-8") != rendered:
            print("canonicalization schema audit is stale", file=sys.stderr)
            return 1
        print("canonicalization schema audit is current")
        return 0
    if len(sys.argv) != 1:
        print("usage: audit_schemas.py [--check|--write]", file=sys.stderr)
        return 2
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
