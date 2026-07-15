#!/usr/bin/env python3
"""Validate Odeya's machine-readable logical module/ownership manifest.

This is architecture assurance. It does not inspect or authorize runtime packages.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "architecture/module-dependency-manifest.json"
PURE_FORBIDDEN = {
    "network",
    "database",
    "object_store",
    "filesystem",
    "system_clock",
    "ambient_randomness",
    "environment_variables",
    "provider_sdk",
    "model_sdk",
    "secret_store",
    "external_dispatch",
}


class DuplicateKeyError(ValueError):
    pass


def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(key)
        result[key] = value
    return result


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def exact_safe_jcs_bytes(value: object) -> bytes:
    """Canonicalize this manifest's restricted integer/bool/string/null JSON subset.

    The general Odeya JCS implementation lives in tests/canonicalization. This local
    helper is intentionally rejected when a float appears, preventing accidental use
    as a second general-purpose canonicalizer.
    """

    def reject_float(node: object) -> None:
        if isinstance(node, float):
            raise ValueError("module manifest canonicalization forbids floating-point values")
        if isinstance(node, list):
            for item in node:
                reject_float(item)
        elif isinstance(node, dict):
            for item in node.values():
                reject_float(item)

    reject_float(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def collect_discriminator_aggregates(
    node: object,
    discriminator: str,
    aggregate_path: tuple[str, ...],
) -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}

    def visit(value: object) -> None:
        if isinstance(value, dict):
            properties = value.get("properties")
            if isinstance(properties, dict):
                discriminator_schema = properties.get(discriminator)
                name = discriminator_schema.get("const") if isinstance(discriminator_schema, dict) else None
                aggregate: object = properties
                for segment in aggregate_path:
                    if not isinstance(aggregate, dict):
                        aggregate = None
                        break
                    aggregate = aggregate.get(segment)
                if isinstance(name, str) and isinstance(aggregate, dict) and isinstance(aggregate.get("const"), str):
                    found.setdefault(name, set()).add(aggregate["const"])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(node)
    return found


def validate() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    manifest = load(MANIFEST_PATH)

    layers = manifest.get("layers", [])
    layer_map = {
        item.get("layer_id"): item
        for item in layers
        if isinstance(item, dict) and isinstance(item.get("layer_id"), str)
    }
    if len(layer_map) != len(layers):
        errors.append("layer identities must be present and unique")

    modules = manifest.get("modules", [])
    module_map = {
        item.get("module_id"): item
        for item in modules
        if isinstance(item, dict) and isinstance(item.get("module_id"), str)
    }
    if len(module_map) != len(modules):
        errors.append("module identities must be present and unique")

    for module_id, module in module_map.items():
        layer_id = module.get("layer_id")
        if layer_id not in layer_map:
            errors.append(f"module {module_id} names unknown layer {layer_id!r}")
            continue
        dependencies = module.get("direct_dependencies", [])
        if module_id in dependencies:
            errors.append(f"module {module_id} directly depends on itself")
        for dependency in dependencies:
            if dependency not in module_map:
                errors.append(f"module {module_id} names unknown dependency {dependency!r}")
                continue
            dependency_layer = module_map[dependency].get("layer_id")
            if dependency_layer not in layer_map[layer_id].get("may_depend_on_layers", []):
                errors.append(
                    f"module {module_id} layer {layer_id} may not depend on "
                    f"{dependency} layer {dependency_layer}"
                )
        if layer_id in {"constitutional", "foundation", "domain"}:
            forbidden = set(module.get("forbidden_capabilities", []))
            missing = sorted(PURE_FORBIDDEN - forbidden)
            if missing:
                errors.append(f"pure module {module_id} lacks forbidden ambient capabilities: {missing}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit_module(module_id: str, path: list[str]) -> None:
        if module_id in visiting:
            cycle_start = path.index(module_id) if module_id in path else 0
            errors.append("module dependency cycle: " + " -> ".join(path[cycle_start:] + [module_id]))
            return
        if module_id in visited:
            return
        visiting.add(module_id)
        for dependency in module_map[module_id].get("direct_dependencies", []):
            if dependency in module_map:
                visit_module(dependency, path + [module_id])
        visiting.remove(module_id)
        visited.add(module_id)

    for module_id in sorted(module_map):
        visit_module(module_id, [])

    owners = manifest.get("aggregate_owners", [])
    owner_map = {
        item.get("aggregate_type"): item.get("owner_module")
        for item in owners
        if isinstance(item, dict) and isinstance(item.get("aggregate_type"), str)
    }
    if len(owner_map) != len(owners):
        errors.append("aggregate types must each have exactly one owner record")
    for aggregate_type, owner in owner_map.items():
        if owner not in module_map:
            errors.append(f"aggregate {aggregate_type} names unknown owner module {owner!r}")

    schema_owner_records = manifest.get("schema_owners", [])
    schema_owner_map = {
        item.get("schema_path"): item
        for item in schema_owner_records
        if isinstance(item, dict) and isinstance(item.get("schema_path"), str)
    }
    if len(schema_owner_map) != len(schema_owner_records):
        errors.append("schema paths must each have exactly one owner record")
    actual_schema_paths = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "schemas").glob("*.schema.json")
    }
    if set(schema_owner_map) != actual_schema_paths:
        errors.append(
            "schema ownership inventory mismatch; "
            f"missing={sorted(actual_schema_paths - set(schema_owner_map))}, "
            f"unexpected={sorted(set(schema_owner_map) - actual_schema_paths)}"
        )
    for schema_path, record in schema_owner_map.items():
        owner = record.get("owner_module")
        if owner not in module_map:
            errors.append(f"schema {schema_path} names unknown owner module {owner!r}")
        path = ROOT / schema_path
        if path.is_file():
            schema = load(path)
            if schema.get("$id") != record.get("schema_id"):
                errors.append(f"schema ownership identity drift for {schema_path}")

    derived = manifest.get("derived_ownership", {})
    derived_counts: dict[str, int] = {}
    derivation_profiles = {
        "commands": ("command_type", ("target", "properties", "aggregate_type")),
        "events": ("event_type", ("aggregate", "properties", "aggregate_type")),
    }
    for registry_name, (discriminator, aggregate_path) in derivation_profiles.items():
        profile = derived.get(registry_name, {}) if isinstance(derived, dict) else {}
        source_path = profile.get("source_schema_path") if isinstance(profile, dict) else None
        if not isinstance(source_path, str) or not (ROOT / source_path).is_file():
            errors.append(f"{registry_name} ownership derivation source is missing")
            continue
        source = load(ROOT / source_path)
        mapping = collect_discriminator_aggregates(source, discriminator, aggregate_path)
        derived_counts[registry_name] = len(mapping)
        expected_minimum = profile.get("expected_minimum_count")
        if not isinstance(expected_minimum, int) or len(mapping) < expected_minimum:
            errors.append(
                f"{registry_name} discriminator count {len(mapping)} is below declared minimum {expected_minimum!r}"
            )
        for name, aggregates in mapping.items():
            if len(aggregates) != 1:
                errors.append(f"{registry_name} discriminator {name} resolves to aggregates {sorted(aggregates)}")
            for aggregate_type in aggregates:
                if aggregate_type not in owner_map:
                    errors.append(f"{registry_name} discriminator {name} has unowned aggregate {aggregate_type}")

    digest_view = dict(manifest)
    digest_view.pop("manifest_digest", None)
    calculated_digest = "sha256:" + hashlib.sha256(exact_safe_jcs_bytes(digest_view)).hexdigest()
    if manifest.get("manifest_digest") != calculated_digest:
        errors.append(
            "module manifest digest mismatch: "
            f"declared={manifest.get('manifest_digest')}, calculated={calculated_digest}"
        )

    counts = {
        "layers": len(layer_map),
        "modules": len(module_map),
        "aggregates": len(owner_map),
        "schemas": len(schema_owner_map),
        "commands": derived_counts.get("commands", 0),
        "events": derived_counts.get("events", 0),
    }
    return errors, counts


def main() -> int:
    try:
        errors, counts = validate()
    except (OSError, json.JSONDecodeError, DuplicateKeyError, ValueError) as exc:
        print(f"Odeya module manifest validation FAILED\n- {exc}")
        return 1
    if errors:
        print("Odeya module manifest validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Odeya module manifest validation PASSED")
    for name, count in counts.items():
        print(f"- {count} {name}")
    print("- logical architecture only; no runtime package conformance claimed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
