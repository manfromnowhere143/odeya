#!/usr/bin/env python3
"""Execute wave tranche D3+D4: migrate every generic scientific decimal to the
frozen typed scientific-decimal object, and retire research-mission's two
binary-number domains into the same governance.

Each of the 127 accepted D3 rows replaces its decimal leaf with the frozen
object: a closed structure carrying exactly one value member (`decimal` with
the frozen lexical pattern, or `elements` for matrices), plus `semantic_type`
(a const from the frozen registry), `unit`, and `precision` bound per row.
Nullable unions keep their non-decimal branches. D4's nine resource-budget
fields in research-mission migrate to per-type governed objects mirroring the
accepted authority-grant rows field by field, preserving `"unknown"` as a
first-class alternative (missing is never zero); the two binary-number
definitions are then unreferenced and removed.

Operator decisions executed under ADR 0037's delegation, recorded in ADR 0042:
instance-declared precision for monetary amounts (sub-cent exactness must
survive; a fixed currency exponent would destroy it), instance-declared unit
strings for the measure-type-dependent and instance-declared unit forms, and
the symbolic unit `pairwise_unit_product` for covariance elements.

Idempotent: a leaf already carrying the frozen object is left alone.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FROZEN_DECIMAL_PATTERN = (
    "^(?:(?:0|[1-9][0-9]*)(?:\\.[0-9]+)?|-(?:0\\.[0-9]*[1-9][0-9]*|[1-9][0-9]*(?:\\.[0-9]+)?))(?:e-?(?:0|[1-9][0-9]*))?$"
)
INSTANCE_PRECISION = {
    "type": "string",
    "pattern": "^(?:0|[1-9][0-9]{0,2}|exact_lexical)$",
}
INSTANCE_UNIT = {"type": "string", "minLength": 1}

# unit forms: concrete registered strings become consts; instance-declared
# forms stay a required nonempty string the instance must declare
UNIT_CONST = {
    "seconds", "hours", "bytes", "tokens", "GiB*s", "USD", "dimensionless",
    "capacity_slot", "iso4217_major_unit", "iso4217_minor_unit",
}
UNIT_DECIDED = {
    "operator_choice_pairwise_unit_product": {"const": "pairwise_unit_product"},
    "type_dependent_operator_choice": INSTANCE_UNIT,
    "instance_declared_free_string_unit_must_register": INSTANCE_UNIT,
    "instance_declared_target_unit": INSTANCE_UNIT,
    "instance_declared_unit_enum": INSTANCE_UNIT,
    "instance_declared_unit_object": INSTANCE_UNIT,
    "instance_declared_unit_ref": INSTANCE_UNIT,
}
PRECISION_DECIDED = {
    "0_exact": {"const": "0"},
    "2": {"const": "2"},
    "6": {"const": "6"},
    "exact_lexical": {"const": "exact_lexical"},
    "instance_declared": INSTANCE_PRECISION,
    "kind_dependent": INSTANCE_PRECISION,
    "operator_choice_currency_exponent_or_6": INSTANCE_PRECISION,
}

MATRIX_TYPES = {"covariance_element", "correlation_coefficient"}

# D4: research-mission resource-budget fields, mirroring the accepted
# authority-grant rows for identically named fields
RESEARCH_MISSION_BUDGET = {
    "wall_time_seconds": ("duration_seconds", "seconds", "6"),
    "model_tokens": ("resource_amount", "tokens", "0_exact"),
    "cpu_seconds": ("duration_seconds", "seconds", "6"),
    "memory_gib_seconds": ("memory_gib_seconds", "GiB*s", "6"),
    "accelerator_seconds": ("duration_seconds", "seconds", "6"),
    "storage_bytes": ("byte_count", "bytes", "0_exact"),
    "network_bytes": ("byte_count", "bytes", "0_exact"),
    "external_cost_usd": (
        "monetary_amount_usd", "USD", "operator_choice_currency_exponent_or_6",
    ),
    "human_hours": ("human_effort_hours", "hours", "2"),
}


def unit_schema(unit: str) -> dict[str, Any]:
    if unit in UNIT_CONST:
        return {"const": unit}
    if unit in UNIT_DECIDED:
        return dict(UNIT_DECIDED[unit])
    raise SystemExit(f"unmapped unit form: {unit}")


def precision_schema(precision: str) -> dict[str, Any]:
    if precision in PRECISION_DECIDED:
        return dict(PRECISION_DECIDED[precision])
    raise SystemExit(f"unmapped precision form: {precision}")


def governed(semantic_type: str, unit: str, precision: str, matrix: bool) -> dict[str, Any]:
    value_member = "elements" if matrix else "decimal"
    value_schema: dict[str, Any]
    if matrix:
        value_schema = {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "pattern": FROZEN_DECIMAL_PATTERN},
            },
        }
    else:
        value_schema = {"type": "string", "pattern": FROZEN_DECIMAL_PATTERN}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted([value_member, "precision", "semantic_type", "unit"]),
        "properties": {
            value_member: value_schema,
            "semantic_type": {"const": semantic_type},
            "unit": unit_schema(unit),
            "precision": precision_schema(precision),
        },
    }


def navigate(schema: dict[str, Any], pointer: str) -> tuple[Any, str]:
    """Return (parent container, final key) for a JSON pointer; int-aware."""
    tokens = [t.replace("~1", "/").replace("~0", "~") for t in pointer.strip("/").split("/")]
    node: Any = schema
    for token in tokens[:-1]:
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node, tokens[-1]


def is_governed(node: Any) -> bool:
    return (
        isinstance(node, dict)
        and node.get("type") == "object"
        and isinstance(node.get("properties"), dict)
        and {"semantic_type", "unit", "precision"} <= set(node["properties"])
    )


def replace_leaf(schema: dict[str, Any], pointer: str, target: dict[str, Any]) -> str:
    parent, key = navigate(schema, pointer)
    node = parent[int(key)] if isinstance(parent, list) else parent[key]
    if is_governed(node):
        return "already_governed"
    outcome = "replaced"
    if isinstance(node, dict):
        branches = node.get("oneOf") or node.get("anyOf")
        if isinstance(branches, list):
            # preserve every non-decimal alternative (null, "unknown", enums)
            keep = [
                b for b in branches
                if not (
                    isinstance(b, dict)
                    and (
                        "$ref" in b
                        or "pattern" in b
                        or b.get("type") == "number"
                        or (isinstance(b.get("type"), str) and b["type"] == "string" and "pattern" in b)
                    )
                )
            ]
            union_key = "oneOf" if "oneOf" in node else "anyOf"
            replacement = {union_key: [target] + keep} if keep else target
            outcome = f"union_replaced_keeping_{len(keep)}"
        else:
            replacement = target
    else:
        replacement = target
    description = node.get("description") if isinstance(node, dict) else None
    if isinstance(description, str) and isinstance(replacement, dict) and "description" not in replacement:
        replacement = {"description": description, **replacement}
    if isinstance(parent, list):
        parent[int(key)] = replacement
    else:
        parent[key] = replacement
    return outcome


def save(path: Path, schema: dict[str, Any]) -> None:
    path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")


def migrate_d3() -> int:
    table = json.loads(
        (ROOT / "architecture/canonicalization-migration-disposition-candidate.json").read_text()
    )["d3_decimal_table"]
    by_schema: dict[str, list[dict[str, Any]]] = {}
    for row in table:
        by_schema.setdefault(row["schema"], []).append(row)
    migrated = 0
    for schema_rel in sorted(by_schema):
        path = ROOT / schema_rel
        schema = json.loads(path.read_text())
        changed = 0
        # deepest pointers first so branch refinements are replaced before
        # their base property nodes rewrite the tree above them
        for row in sorted(by_schema[schema_rel], key=lambda r: -len(r["pointer"])):
            matrix = (
                row["proposed_semantic_type"] in MATRIX_TYPES
                and row["pointer"].rsplit("/", 1)[-1].endswith("matrix")
            )
            target = governed(
                row["proposed_semantic_type"], row["proposed_unit"],
                row["proposed_precision"], matrix,
            )
            outcome = replace_leaf(schema, row["pointer"], target)
            if outcome != "already_governed":
                changed += 1
        if changed:
            save(path, schema)
            migrated += changed
            print(f"{schema_rel.rsplit('/', 1)[-1]:44s} {changed:3d} leaves governed")
    return migrated


def migrate_d4() -> int:
    path = ROOT / "schemas/research-mission.schema.json"
    schema = json.loads(path.read_text())
    defs = schema["$defs"]
    if "nonnegative_number" not in defs:
        print("research-mission already migrated")
        return 0
    # one governed def per distinct row binding, named after the field family
    def_name = {}
    for field, (stype, unit, precision) in RESEARCH_MISSION_BUDGET.items():
        name = f"governed_{field}"
        defs[name] = governed(stype, unit, precision, matrix=False)
        def_name[field] = name
    changed = 0

    def repoint(node: Any) -> None:
        nonlocal changed
        if isinstance(node, dict):
            props = node.get("properties")
            if isinstance(props, dict):
                for field, sub in props.items():
                    if field in def_name and isinstance(sub, dict):
                        ref = sub.get("$ref", "")
                        if ref.endswith("/nonnegative_or_unknown"):
                            props[field] = {
                                "oneOf": [
                                    {"$ref": f"#/$defs/{def_name[field]}"},
                                    {"const": "unknown"},
                                ]
                            }
                            changed += 1
                        elif ref.endswith("/nonnegative_number"):
                            props[field] = {"$ref": f"#/$defs/{def_name[field]}"}
                            changed += 1
            for value in node.values():
                repoint(value)
        elif isinstance(node, list):
            for value in node:
                repoint(value)

    repoint(schema)
    remaining = json.dumps(schema).count("nonnegative_number") + json.dumps(schema).count(
        "nonnegative_or_unknown"
    )
    # the two binary-number domains must be fully unreferenced before removal
    del defs["nonnegative_number"]
    del defs["nonnegative_or_unknown"]
    still = json.dumps(schema)
    if "nonnegative_number" in still or "nonnegative_or_unknown" in still:
        raise SystemExit("binary-number definitions still referenced after repoint")
    save(path, schema)
    print(f"research-mission.schema.json                    {changed:3d} budget fields governed; 2 binary-number defs removed (was referenced {remaining} times pre-removal)")
    return changed


def main() -> int:
    d3 = migrate_d3()
    d4 = migrate_d4()
    print(f"total: {d3} D3 leaves + {d4} D4 fields")
    return 0


if __name__ == "__main__":
    sys.exit(main())
