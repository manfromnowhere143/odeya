"""Validate the PRQ-002F raw-aware numeric trace conformance suite.

This is the dedicated parent validator for
`tests/profile-0-3-numeric-trace-conformance/` and a deliberate third
implementation of the deep content checks. Static mode re-derives, from
current repository bytes: strict parsing and raw-number token policy for all
fifteen frozen subjects, the complete static numeric-position inventory of
the twelve final `odeya-jcs-0.3` schemas, closed-vocabulary conformance of
the three records against their governing schemas, and the digest dependency
citations — in that order, before any byte-census comparison, so a deep
mutation trips the deep guard rather than dying at a digest check. It then
verifies the retained results, execution receipts, and comparison receipt,
and finally executes the embedded known-bad corpus, in which every mutation
must refuse with its declared singleton code.

`--recompute-all` additionally re-executes both source-separated runners with
explicitly selected executables and requires fresh stdout to equal the
retained result bytes exactly.

Bounded architecture evidence only: passing establishes no conformance
outside the fifteen subjects, no product identity, no profile issuance, no
PRQ-002 closure, no Gate A acceptance, and no runtime or publication
authority.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
SUITE = ROOT / "tests/profile-0-3-numeric-trace-conformance"
SUITE_ID = "prq-002f-numeric-trace-conformance.0001"
CONTRACT_PATH = (
    "architecture/prq-002f-numeric-trace-conformance-contract-v1-candidate.json"
)
CONTRACT_SCHEMA_PATH = (
    "architecture/prq-002f-numeric-trace-conformance-contract.schema.json"
)
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.3"
RAW_NUMBER_CONTRACT_ID = (
    "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
)
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
DECIMAL_RE = re.compile(r"^(0|-?[1-9][0-9]*)$")
DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
SCHEMA_DOCUMENT_TOKEN_RULE = "schema_definition_data_not_instance_position"
METASCHEMA_DISPOSITION = "blocked_out_of_cohort_metaschema_not_retained"
FINAL_RULE_PRECEDENCE = ("recursive_integer_valued_const_leaf", "integer_type")

SUBJECT_ROWS: tuple[tuple[str, str, str | None, str | None], ...] = (
    ("schema_resource_record_schema", "schemas/schema-resource-record-v0-2.schema.json", "urn:odeya:schema:schema-resource-record:0.2.0", None),
    ("aggregate_state_subject_record_schema", "schemas/aggregate-state-subject-record-v0-2.schema.json", "urn:odeya:schema:aggregate-state-subject-record:0.2.0", None),
    ("reducer_contract_record_schema", "schemas/reducer-contract-record-v0-2.schema.json", "urn:odeya:schema:reducer-contract-record:0.2.0", None),
    ("event_contract_record_schema", "schemas/event-contract-record-v0-2.schema.json", "urn:odeya:schema:event-contract-record:0.2.0", None),
    ("ordered_member_map_commitment_schema", "schemas/ordered-member-map-commitment-v0-2.schema.json", "urn:odeya:schema:ordered-member-map-commitment:0.2.0", None),
    ("schema_registry_schema", "schemas/schema-registry-v0-9.schema.json", "urn:odeya:schema:schema-registry:0.9.0", None),
    ("aggregate_state_subject_registry_schema", "schemas/aggregate-state-subject-registry-v0-8.schema.json", "urn:odeya:schema:aggregate-state-subject-registry:0.8.0", None),
    ("reducer_registry_schema", "schemas/reducer-registry-v0-8.schema.json", "urn:odeya:schema:reducer-registry:0.8.0", None),
    ("event_contract_registry_schema", "schemas/event-contract-registry-v0-8.schema.json", "urn:odeya:schema:event-contract-registry:0.8.0", None),
    ("profile_core_schema", "schemas/canonicalization-profile-core-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-core:0.7.0", None),
    ("profile_evidence_schema", "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0", None),
    ("profile_migration_schema", "schemas/canonicalization-profile-migration-v0-2.schema.json", "urn:odeya:schema:canonicalization-profile-migration:0.2.0", None),
    ("profile_core", "architecture/canonicalization-profile-core-0.3-candidate.json", None, "profile_core_schema"),
    ("profile_evidence", "architecture/canonicalization-profile-0.3-candidate-evidence.json", None, "profile_evidence_schema"),
    ("profile_migration", "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json", None, "profile_migration_schema"),
)

SCHEMA_BINDING_IDS = (
    "schema_resource_record",
    "aggregate_state_subject_record",
    "reducer_contract_record",
    "event_contract_record",
    "ordered_member_map_commitment",
    "schema_registry_v0_9",
    "aggregate_state_subject_registry_v0_8",
    "reducer_registry_v0_8",
    "event_contract_registry_v0_8",
    "canonicalization_profile_core_v0_7",
    "canonicalization_profile_candidate_evidence_v0_7",
    "canonicalization_profile_migration_v0_2",
)
EXPECTED_GRAPH_NODES = SCHEMA_BINDING_IDS + (
    "successor_profile_core_artifact",
    "successor_profile_evidence_artifact",
    "successor_profile_migration_artifact",
)
EXPECTED_GRAPH_EDGES: tuple[tuple[str, str], ...] = (
    ("schema_registry_v0_9", "ordered_member_map_commitment"),
    ("aggregate_state_subject_registry_v0_8", "ordered_member_map_commitment"),
    ("reducer_registry_v0_8", "ordered_member_map_commitment"),
    ("event_contract_registry_v0_8", "ordered_member_map_commitment"),
    *[("successor_profile_core_artifact", node) for node in SCHEMA_BINDING_IDS],
    ("successor_profile_evidence_artifact", "successor_profile_core_artifact"),
    ("successor_profile_migration_artifact", "successor_profile_evidence_artifact"),
)

APPLICATOR_KEYWORDS = frozenset(
    {"$ref", "allOf", "if", "then", "else", "items", "prefixItems",
     "properties", "additionalProperties", "$defs"}
)
ASSERTION_KEYWORDS = frozenset(
    {"type", "const", "enum", "required", "pattern", "maximum", "minimum",
     "maxItems", "minItems", "maxLength", "minLength", "uniqueItems"}
)
ANNOTATION_KEYWORDS = frozenset(
    {"$schema", "$id", "title", "description", "format",
     "x-odeya-digest-scope", "x-odeya-number-token-policy"}
)
CLOSED_VOCABULARY = APPLICATOR_KEYWORDS | ASSERTION_KEYWORDS | ANNOTATION_KEYWORDS
REFUSAL_CODES = (
    "authority_nonclaim_violation",
    "census_decimal_typing_violation",
    "closed_vocabulary_violation",
    "digest_dependency_graph_mismatch",
    "duplicate_instance_pointer",
    "execution_binding_mismatch",
    "fallback_resolution_forbidden",
    "metaschema_disposition_mismatch",
    "multiply_classified_instance_position",
    "out_of_cohort_reference",
    "projection_comparison_mismatch",
    "raw_token_policy_violation",
    "raw_token_reconciliation_mismatch",
    "record_schema_validation_failed",
    "schema_id_mismatch",
    "source_separation_violation",
    "static_inventory_recomputation_mismatch",
    "subject_byte_binding_mismatch",
    "subject_census_mismatch",
    "unclassified_instance_numeric_position",
    "unclassified_numeric_position",
)

RETAINED_SUITE_PATHS = (
    "tests/profile-0-3-numeric-trace-conformance/README.md",
    "tests/profile-0-3-numeric-trace-conformance/manifest.json",
    "tests/profile-0-3-numeric-trace-conformance/input-manifest.json",
    "tests/profile-0-3-numeric-trace-conformance/cases.json",
    "tests/profile-0-3-numeric-trace-conformance/authoring/generate_suite_metadata.py",
    "tests/profile-0-3-numeric-trace-conformance/authoring/retain_results.py",
    "tests/profile-0-3-numeric-trace-conformance/python/runner.py",
    "tests/profile-0-3-numeric-trace-conformance/python/dependency-lock.json",
    "tests/profile-0-3-numeric-trace-conformance/python/source-manifest.json",
    "tests/profile-0-3-numeric-trace-conformance/node/runner.mjs",
    "tests/profile-0-3-numeric-trace-conformance/node/package.json",
    "tests/profile-0-3-numeric-trace-conformance/node/package-lock.json",
    "tests/profile-0-3-numeric-trace-conformance/node/source-manifest.json",
    "tests/profile-0-3-numeric-trace-conformance/results/python-trace-result.json",
    "tests/profile-0-3-numeric-trace-conformance/results/node-trace-result.json",
    "tests/profile-0-3-numeric-trace-conformance/results/python-execution-receipt.json",
    "tests/profile-0-3-numeric-trace-conformance/results/node-execution-receipt.json",
    "tests/profile-0-3-numeric-trace-conformance/results/comparison-receipt.json",
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
    """Read-only byte view over the repository with an in-memory overlay."""

    def __init__(self, overlay: dict[str, bytes] | None = None) -> None:
        self.overlay = overlay or {}
        self._parse_cache: dict[str, Any] = {}

    def read_bytes(self, relative: str) -> bytes:
        if relative in self.overlay:
            return self.overlay[relative]
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            refuse(
                "subject_byte_binding_mismatch",
                f"{relative}: not a regular non-symlink repository file",
            )
        return path.read_bytes()

    def parse(self, relative: str) -> Any:
        # The pipeline treats parsed documents as immutable reads, so the
        # cache returns the shared object; nothing downstream mutates it.
        raw = self.read_bytes(relative)
        key = f"{relative}:{sha256(raw)}"
        if key not in self._parse_cache:
            self._parse_cache[key] = strict_parse(raw, relative)
        return self._parse_cache[key]


def strict_object_pairs_factory(subject: str) -> Callable:
    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                refuse(
                    "raw_token_reconciliation_mismatch",
                    f"{subject}: duplicate decoded object member name: {key!r}",
                )
            result[key] = value
        return result

    return hook


def strict_parse(raw: bytes, subject: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        refuse("subject_byte_binding_mismatch", f"{subject}: leading BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        refuse("subject_byte_binding_mismatch", f"{subject}: invalid UTF-8: {exc}")
    def refuse_float(token: str) -> Any:
        refuse(
            "raw_token_policy_violation",
            f"{subject}: non-integer raw number token: {token}",
        )
    def refuse_constant(token: str) -> Any:
        refuse(
            "raw_token_policy_violation", f"{subject}: non-finite extension {token}"
        )
    try:
        return json.loads(
            text,
            object_pairs_hook=strict_object_pairs_factory(subject),
            parse_float=refuse_float,
            parse_constant=refuse_constant,
        )
    except Refusal:
        raise
    except ValueError as exc:
        refuse("subject_byte_binding_mismatch", f"{subject}: invalid JSON: {exc}")


def raw_number_tokens(raw: bytes, subject: str) -> list[str]:
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
                refuse(
                    "raw_token_policy_violation",
                    f"{subject}: unclassified numeric character at {index}",
                )
            tokens.append(match.group(0))
            index = match.end()
            continue
        index += 1
    if in_string or escaped:
        refuse(
            "raw_token_reconciliation_mismatch",
            f"{subject}: unterminated string during raw scan",
        )
    return tokens


def iter_locations(value: Any, pointer: str = ""):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_locations(child, f"{pointer}/{pointer_escape(key)}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_locations(child, f"{pointer}/{index}")


def integer_token_rows(document: Any, raw: bytes, subject: str) -> list[dict[str, str]]:
    tokens = raw_number_tokens(raw, subject)
    for token in tokens:
        if not INTEGER_RE.fullmatch(token):
            refuse(
                "raw_token_policy_violation",
                f"{subject}: non-integer raw token {token}",
            )
        if token.startswith("-0"):
            refuse(
                "raw_token_policy_violation",
                f"{subject}: lexical negative zero {token}",
            )
        if not MIN_SAFE_INTEGER <= int(token) <= MAX_SAFE_INTEGER:
            refuse(
                "raw_token_policy_violation",
                f"{subject}: raw integer outside safe range {token}",
            )
    located = [
        {"instance_pointer": pointer, "raw_lexeme": str(value)}
        for pointer, value in iter_locations(document)
        if type(value) is int
    ]
    if [row["raw_lexeme"] for row in located] != tokens:
        refuse(
            "raw_token_reconciliation_mismatch",
            f"{subject}: raw lexeme sequence differs from document walk",
        )
    pointers = [row["instance_pointer"] for row in located]
    if len(set(pointers)) != len(pointers):
        refuse(
            "duplicate_instance_pointer",
            f"{subject}: duplicate RFC 6901 instance pointer",
        )
    return located


def resolve_pointer(document: Any, fragment: str, subject: str) -> Any:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        refuse(
            "out_of_cohort_reference",
            f"{subject}: unsupported reference fragment {fragment}",
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
                    "out_of_cohort_reference",
                    f"{subject}: unresolved fragment {fragment}",
                )
        else:
            refuse(
                "out_of_cohort_reference",
                f"{subject}: unresolved fragment {fragment}",
            )
    return current


def require_decimal(value: Any, context: str) -> None:
    if not isinstance(value, str) or not DECIMAL_RE.fullmatch(value):
        refuse(
            "census_decimal_typing_violation",
            f"{context}: count is not a decimal string",
        )


# --- deep layer 2: static inventory recomputation (third path) --------------


def collect_integer_const_leaves(value: Any, schema_location: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_pointer, child in iter_locations(value):
        if type(child) is int:
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
    root_schema_id: str, by_id: dict[str, tuple[str, Any, bytes]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    integer_types: list[dict[str, Any]] = []
    integer_consts: list[dict[str, Any]] = []
    unclassified: list[str] = []

    def append_const_leaves(value, evaluation_path, schema_id, digest, location, relative=""):
        if type(value) is int:
            integer_consts.append(
                {
                    "evaluation_path": copy.deepcopy(evaluation_path),
                    "resolved_schema_id": schema_id,
                    "resolved_schema_raw_digest": digest,
                    "assertion_schema_location": location,
                    "position_rule": "recursive_integer_valued_const_leaf",
                    "const_leaf_pointer": relative,
                    "decimal_value": str(value),
                }
            )
            return
        if isinstance(value, dict):
            for key, child in value.items():
                append_const_leaves(
                    child,
                    [*evaluation_path, {"kind": "const_object_member", "token": key}],
                    schema_id,
                    digest,
                    location,
                    f"{relative}/{pointer_escape(key)}",
                )
        elif isinstance(value, list):
            for index, child in enumerate(value):
                append_const_leaves(
                    child,
                    [*evaluation_path, {"kind": "const_array_index", "token": str(index)}],
                    schema_id,
                    digest,
                    location,
                    f"{relative}/{index}",
                )

    def descend(schema_id, node, schema_pointer, evaluation_path, ref_stack):
        if node is True:
            unclassified.append(f"{schema_id}#{schema_pointer}:true_schema")
            return
        if node is False or not isinstance(node, dict):
            return
        digest = sha256(by_id[schema_id][2])
        node_type = node.get("type")
        if node_type == "integer" or (
            isinstance(node_type, list) and "integer" in node_type
        ):
            integer_types.append(
                {
                    "evaluation_path": copy.deepcopy(evaluation_path),
                    "resolved_schema_id": schema_id,
                    "resolved_schema_raw_digest": digest,
                    "assertion_schema_location": f"{schema_id}#{schema_pointer}/type",
                    "position_rule": "integer_type",
                }
            )
        if node_type == "number" or (
            isinstance(node_type, list) and "number" in node_type
        ):
            unclassified.append(f"{schema_id}#{schema_pointer}/type")
        if "const" in node:
            append_const_leaves(
                node["const"],
                evaluation_path,
                schema_id,
                digest,
                f"{schema_id}#{schema_pointer}/const",
            )
        if "enum" in node and any(type(item) is int for item in node["enum"]):
            if node_type != "integer":
                unclassified.append(f"{schema_id}#{schema_pointer}/enum")
        reference = node.get("$ref")
        if isinstance(reference, str):
            target_id, separator, suffix = reference.partition("#")
            target_id = target_id or schema_id
            if target_id not in by_id:
                refuse(
                    "out_of_cohort_reference",
                    f"unresolved exact-cohort reference: {reference}",
                )
            fragment = f"#{suffix}" if separator else ""
            ref_key = (target_id, fragment or "#")
            if ref_key in ref_stack:
                refuse(
                    "static_inventory_recomputation_mismatch",
                    f"numeric applicability reference cycle: {reference}",
                )
            descend(
                target_id,
                resolve_pointer(by_id[target_id][1], fragment, target_id),
                fragment[1:] if fragment else "",
                [*evaluation_path, {"kind": "ref", "token": reference}],
                (*ref_stack, ref_key),
            )
        for keyword, kind in (
            ("properties", "property"),
            ("patternProperties", "pattern_property"),
            ("dependentSchemas", "dependent_schema"),
        ):
            children = node.get(keyword)
            if isinstance(children, dict):
                for name, child in children.items():
                    descend(
                        schema_id,
                        child,
                        f"{schema_pointer}/{pointer_escape(keyword)}/{pointer_escape(name)}",
                        [*evaluation_path, {"kind": kind, "token": name}],
                        ref_stack,
                    )
        for keyword, kind in (
            ("allOf", "all_of_branch"),
            ("anyOf", "any_of_branch"),
            ("oneOf", "one_of_branch"),
            ("prefixItems", "prefix_item_index"),
        ):
            children = node.get(keyword)
            if isinstance(children, list):
                for index, child in enumerate(children):
                    descend(
                        schema_id,
                        child,
                        f"{schema_pointer}/{keyword}/{index}",
                        [*evaluation_path, {"kind": kind, "token": str(index)}],
                        ref_stack,
                    )
        for keyword, kind in (
            ("items", "items"),
            ("contains", "contains"),
            ("if", "if_branch"),
            ("then", "then_branch"),
            ("else", "else_branch"),
            ("not", "not_branch"),
            ("additionalProperties", "additional_property"),
            ("unevaluatedProperties", "unevaluated_property"),
            ("unevaluatedItems", "unevaluated_item"),
        ):
            child = node.get(keyword)
            if isinstance(child, (dict, bool)) and child is not False:
                descend(
                    schema_id,
                    child,
                    f"{schema_pointer}/{keyword}",
                    [*evaluation_path, {"kind": kind, "token": keyword}],
                    ref_stack,
                )

    descend(root_schema_id, by_id[root_schema_id][1], "", [], ((root_schema_id, "#"),))

    def deduplicate(rows):
        seen: set[bytes] = set()
        kept = []
        for row in rows:
            marker = compact_bytes(row)
            if marker not in seen:
                seen.add(marker)
                kept.append(row)
        return kept

    return deduplicate(integer_types), deduplicate(integer_consts), sorted(set(unclassified))


def recompute_static_inventory(view: RepositoryView) -> dict[str, Any]:
    schema_rows = [row for row in SUBJECT_ROWS if row[2] is not None]
    by_id: dict[str, tuple[str, Any, bytes]] = {}
    for _, relative, schema_id, _ in schema_rows:
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        if not isinstance(document, dict) or document.get("$id") != schema_id:
            refuse("schema_id_mismatch", f"{relative}: schema $id drift")
        by_id[schema_id] = (relative, document, raw)
    rows: list[dict[str, Any]] = []
    for _, relative, schema_id, _ in schema_rows:
        _, document, raw = by_id[schema_id]
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
            if "enum" in node and any(type(item) is int for item in node["enum"]):
                if node_type != "integer":
                    unclassified.append(f"{schema_id}#{pointer}/enum")
            if {
                "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
                "multipleOf",
            }.intersection(node) and node_type not in ("integer", "number"):
                unclassified.append(f"{schema_id}#{pointer}")
            if "$dynamicRef" in node or "$recursiveRef" in node:
                refuse(
                    "static_inventory_recomputation_mismatch",
                    f"{relative}: dynamic/recursive reference is outside this inventory",
                )
            reference = node.get("$ref")
            if isinstance(reference, str):
                target_id, separator, suffix = reference.partition("#")
                resolved_id = target_id or schema_id
                if resolved_id not in by_id:
                    refuse(
                        "out_of_cohort_reference",
                        f"{relative}: unresolved exact-cohort reference {reference}",
                    )
                target_path, target_document, target_raw = by_id[resolved_id]
                fragment = f"#{suffix}" if separator else ""
                resolve_pointer(target_document, fragment, resolved_id)
                reference_edges.append(
                    {
                        "source_schema_location": f"{schema_id}#{pointer}/$ref",
                        "target_schema_id": resolved_id,
                        "target_schema_raw_digest": sha256(target_raw),
                        "target_schema_path": target_path,
                        "target_fragment": fragment or "#",
                    }
                )
            for key, child in node.items():
                if key in {"const", "enum", "examples", "default"} or key.startswith("x-"):
                    continue
                if key in {
                    "$defs", "definitions", "properties", "patternProperties",
                    "dependentSchemas",
                } and isinstance(child, dict):
                    for name, subschema in child.items():
                        visit_schema(
                            subschema,
                            f"{pointer}/{pointer_escape(key)}/{pointer_escape(name)}",
                        )
                    continue
                if isinstance(child, (dict, list, bool)):
                    visit_schema(child, f"{pointer}/{pointer_escape(key)}")

        visit_schema(document, "")
        expanded_types, expanded_consts, expanded_unclassified = (
            expanded_numeric_positions(schema_id, by_id)
        )
        if type_numbers or number_unions or unclassified or expanded_unclassified:
            refuse(
                "unclassified_numeric_position",
                f"{relative}: unsupported numeric position: "
                f"type_number={type_numbers}, unions={number_unions}, "
                f"unclassified={unclassified + expanded_unclassified}",
            )
        located = integer_token_rows(document, raw, relative)
        document_tokens = [
            {
                "document_pointer": row["instance_pointer"],
                "raw_lexeme": row["raw_lexeme"],
                "decimal_value": row["raw_lexeme"],
            }
            for row in located
        ]
        position_projection = {
            "integer_type_assertions": integer_types,
            "integer_const_leaves": integer_consts,
            "expanded_instance_integer_type_positions": expanded_types,
            "expanded_instance_integer_const_positions": expanded_consts,
            "resolved_reference_edges": reference_edges,
        }
        rows.append(
            {
                "schema_path": relative,
                "schema_id": schema_id,
                "schema_raw_digest": sha256(raw),
                "schema_byte_count": len(raw),
                "schema_document_numeric_literals_are_instance_positions": False,
                "schema_document_numeric_token_count": len(document_tokens),
                "schema_document_number_tokens": document_tokens,
                "schema_document_numeric_token_inventory_sha256": sha256(
                    compact_bytes(document_tokens)
                ),
                "integer_type_assertion_count": len(integer_types),
                "integer_type_assertions": integer_types,
                "integer_const_leaf_count": len(integer_consts),
                "integer_const_leaves": integer_consts,
                "expanded_instance_integer_type_position_count": len(expanded_types),
                "expanded_instance_integer_type_positions": expanded_types,
                "expanded_instance_integer_const_position_count": len(expanded_consts),
                "expanded_instance_integer_const_positions": expanded_consts,
                "resolved_reference_edge_count": len(reference_edges),
                "resolved_reference_edges": reference_edges,
                "type_number_assertions": [],
                "number_admitting_unions": [],
                "unclassified_numeric_assertions": [],
                "position_inventory_sha256": sha256(compact_bytes(position_projection)),
            }
        )
    return {
        "inventory_kind": "static_exact_schema_position_inventory_without_subject_digest",
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


# --- deep layer 3: closed-vocabulary record conformance ----------------------


class ClosedEvaluator:
    def __init__(self, by_id: dict[str, tuple[str, Any, bytes]], subject: str) -> None:
        self.by_id = by_id
        self.subject = subject
        self.applicable: dict[str, list[dict[str, str]]] = {}

    def note(self, instance_pointer, schema_id, digest, location, rule) -> None:
        rows = self.applicable.setdefault(instance_pointer, [])
        row = {
            "resolved_schema_id": schema_id,
            "resolved_schema_raw_digest": digest,
            "assertion_schema_location": location,
            "position_rule": rule,
        }
        if row not in rows:
            rows.append(row)

    def const_matches(self, expected, instance, instance_pointer, schema_id, digest, location, relative=""):
        if type(expected) is int:
            if type(instance) is int and instance == expected:
                self.note(
                    instance_pointer, schema_id, digest,
                    f"{location}{relative}",
                    "recursive_integer_valued_const_leaf",
                )
                return True
            return False
        if type(expected) is bool or expected is None or isinstance(expected, str):
            return type(instance) is type(expected) and instance == expected
        if isinstance(expected, dict):
            if not isinstance(instance, dict) or set(instance) != set(expected):
                return False
            return all(
                self.const_matches(
                    child, instance[key],
                    f"{instance_pointer}/{pointer_escape(key)}",
                    schema_id, digest, location,
                    f"{relative}/{pointer_escape(key)}",
                )
                for key, child in expected.items()
            )
        if isinstance(expected, list):
            if not isinstance(instance, list) or len(instance) != len(expected):
                return False
            return all(
                self.const_matches(
                    child, instance[index], f"{instance_pointer}/{index}",
                    schema_id, digest, location, f"{relative}/{index}",
                )
                for index, child in enumerate(expected)
            )
        return False

    def evaluate(self, schema_id, node, schema_pointer, instance, instance_pointer, ref_stack, errors):
        if node is True:
            return True
        if node is False:
            errors.append(f"{instance_pointer}: false schema")
            return False
        if not isinstance(node, dict):
            errors.append(f"{instance_pointer}: non-schema node")
            return False
        location = f"{schema_id}#{schema_pointer}"
        for key in node:
            if key not in CLOSED_VOCABULARY:
                refuse(
                    "closed_vocabulary_violation",
                    f"{self.subject}: unimplemented schema keyword {key!r} at {location}",
                )
        digest = sha256(self.by_id[schema_id][2])
        valid = True
        reference = node.get("$ref")
        if isinstance(reference, str):
            target_base, separator, suffix = reference.partition("#")
            resolved_id = target_base or schema_id
            if resolved_id not in self.by_id:
                refuse(
                    "out_of_cohort_reference",
                    f"{self.subject}: reference outside exact cohort {reference}",
                )
            fragment = f"#{suffix}" if separator else ""
            ref_key = (resolved_id, fragment or "#", instance_pointer)
            if ref_key in ref_stack:
                refuse(
                    "fallback_resolution_forbidden",
                    f"{self.subject}: reference cycle at {reference}",
                )
            target_node = resolve_pointer(
                self.by_id[resolved_id][1], fragment, resolved_id
            )
            if not self.evaluate(
                resolved_id, target_node,
                fragment[1:] if fragment else "",
                instance, instance_pointer,
                (*ref_stack, ref_key), errors,
            ):
                valid = False
        node_type = node.get("type")
        if node_type is not None:
            allowed = node_type if isinstance(node_type, list) else [node_type]
            if "number" in allowed:
                refuse(
                    "unclassified_numeric_position",
                    f"{self.subject}: type admits number at {location}/type",
                )
            matched = (
                ("object" in allowed and isinstance(instance, dict))
                or ("array" in allowed and isinstance(instance, list))
                or ("string" in allowed and isinstance(instance, str))
                or ("boolean" in allowed and type(instance) is bool)
                or ("integer" in allowed and type(instance) is int)
                or ("null" in allowed and instance is None)
            )
            if not matched:
                errors.append(f"{instance_pointer}: type mismatch at {location}")
                valid = False
            if "integer" in allowed and type(instance) is int:
                self.note(
                    instance_pointer, schema_id, digest, f"{location}/type",
                    "integer_type",
                )
        if "const" in node:
            if not self.const_matches(
                node["const"], instance, instance_pointer, schema_id, digest,
                f"{location}/const",
            ):
                errors.append(f"{instance_pointer}: const mismatch at {location}")
                valid = False
        if "enum" in node:
            if any(type(item) is int for item in node["enum"]) and node_type != "integer":
                refuse(
                    "unclassified_numeric_position",
                    f"{self.subject}: integer enum outside integer type at {location}/enum",
                )
            if not any(
                type(member) is type(instance) and member == instance
                if not isinstance(member, (dict, list))
                else member == instance
                for member in node["enum"]
            ):
                errors.append(f"{instance_pointer}: enum mismatch at {location}")
                valid = False
        if isinstance(instance, str):
            if "minLength" in node and len(instance) < node["minLength"]:
                errors.append(f"{instance_pointer}: minLength at {location}")
                valid = False
            if "maxLength" in node and len(instance) > node["maxLength"]:
                errors.append(f"{instance_pointer}: maxLength at {location}")
                valid = False
            if "pattern" in node and re.search(node["pattern"], instance) is None:
                errors.append(f"{instance_pointer}: pattern at {location}")
                valid = False
        if type(instance) is int:
            if "minimum" in node and instance < node["minimum"]:
                errors.append(f"{instance_pointer}: minimum at {location}")
                valid = False
            if "maximum" in node and instance > node["maximum"]:
                errors.append(f"{instance_pointer}: maximum at {location}")
                valid = False
        if isinstance(instance, list):
            if "minItems" in node and len(instance) < node["minItems"]:
                errors.append(f"{instance_pointer}: minItems at {location}")
                valid = False
            if "maxItems" in node and len(instance) > node["maxItems"]:
                errors.append(f"{instance_pointer}: maxItems at {location}")
                valid = False
            if node.get("uniqueItems") is True:
                markers = [compact_bytes(item) for item in instance]
                if len(set(markers)) != len(markers):
                    errors.append(f"{instance_pointer}: uniqueItems at {location}")
                    valid = False
            prefix = node.get("prefixItems")
            prefix_length = len(prefix) if isinstance(prefix, list) else 0
            if isinstance(prefix, list):
                for index, subschema in enumerate(prefix):
                    if index >= len(instance):
                        break
                    if not self.evaluate(
                        schema_id, subschema,
                        f"{schema_pointer}/prefixItems/{index}",
                        instance[index], f"{instance_pointer}/{index}",
                        ref_stack, errors,
                    ):
                        valid = False
            if "items" in node:
                items = node["items"]
                if items is False:
                    if len(instance) > prefix_length:
                        errors.append(f"{instance_pointer}: items false at {location}")
                        valid = False
                else:
                    for index in range(prefix_length, len(instance)):
                        if not self.evaluate(
                            schema_id, items, f"{schema_pointer}/items",
                            instance[index], f"{instance_pointer}/{index}",
                            ref_stack, errors,
                        ):
                            valid = False
        if isinstance(instance, dict):
            required = node.get("required")
            if isinstance(required, list):
                for name in required:
                    if name not in instance:
                        errors.append(
                            f"{instance_pointer}: missing required {name!r} at {location}"
                        )
                        valid = False
            properties = node.get("properties")
            declared = set(properties) if isinstance(properties, dict) else set()
            if isinstance(properties, dict):
                for name, subschema in properties.items():
                    if name in instance:
                        if not self.evaluate(
                            schema_id, subschema,
                            f"{schema_pointer}/properties/{pointer_escape(name)}",
                            instance[name],
                            f"{instance_pointer}/{pointer_escape(name)}",
                            ref_stack, errors,
                        ):
                            valid = False
            if "additionalProperties" in node:
                additional = node["additionalProperties"]
                for name in instance:
                    if name in declared:
                        continue
                    if additional is False:
                        errors.append(
                            f"{instance_pointer}: additional property {name!r} at {location}"
                        )
                        valid = False
                    elif not self.evaluate(
                        schema_id, additional,
                        f"{schema_pointer}/additionalProperties",
                        instance[name],
                        f"{instance_pointer}/{pointer_escape(name)}",
                        ref_stack, errors,
                    ):
                        valid = False
        all_of = node.get("allOf")
        if isinstance(all_of, list):
            for index, subschema in enumerate(all_of):
                if not self.evaluate(
                    schema_id, subschema, f"{schema_pointer}/allOf/{index}",
                    instance, instance_pointer, ref_stack, errors,
                ):
                    valid = False
        if "if" in node:
            silent: list[str] = []
            condition = self.evaluate(
                schema_id, node["if"], f"{schema_pointer}/if",
                instance, instance_pointer, ref_stack, silent,
            )
            branch = "then" if condition else "else"
            if branch in node:
                if not self.evaluate(
                    schema_id, node[branch], f"{schema_pointer}/{branch}",
                    instance, instance_pointer, ref_stack, errors,
                ):
                    valid = False
        return valid


# --- production pipeline ------------------------------------------------------


def deep_validate(view: RepositoryView) -> dict[str, Any]:
    """Layers 1-4: parse/policy, inventory, conformance, graph citations."""
    parsed: dict[str, tuple[Any, bytes]] = {}
    for role, relative, _, _ in SUBJECT_ROWS:
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        integer_token_rows(document, raw, relative)
        parsed[role] = (document, raw)

    inventory = recompute_static_inventory(view)
    core, core_raw = parsed["profile_core"]
    retained = core.get("static_numeric_applicability_inventory")
    if compact_bytes(retained) != compact_bytes(inventory):
        refuse(
            "static_inventory_recomputation_mismatch",
            "retained core inventory differs from third-path recomputation",
        )
    if (
        core.get("static_numeric_applicability_inventory", {}).get(
            "schema_document_numeric_literals_are_future_instance_positions"
        )
        is not False
    ):
        refuse(
            "metaschema_disposition_mismatch",
            "core does not pin schema-document literals as non-instance positions",
        )

    by_id = {
        row[2]: (row[1], parsed[row[0]][0], parsed[row[0]][1])
        for row in SUBJECT_ROWS
        if row[2] is not None
    }
    governing_ids = {
        "profile_core": "urn:odeya:schema:canonicalization-profile-core:0.7.0",
        "profile_evidence": (
            "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0"
        ),
        "profile_migration": (
            "urn:odeya:schema:canonicalization-profile-migration:0.2.0"
        ),
    }
    trace_counts: dict[str, int] = {}
    for role, governing_id in governing_ids.items():
        record_document, record_raw = parsed[role]
        evaluator = ClosedEvaluator(by_id, role)
        errors: list[str] = []
        if not evaluator.evaluate(
            governing_id, by_id[governing_id][1], "", record_document, "",
            ((governing_id, "#", ""),), errors,
        ):
            refuse(
                "record_schema_validation_failed",
                f"{role}: {errors[0] if errors else 'schema validation failed'}",
            )
        located = integer_token_rows(record_document, record_raw, role)
        for row in located:
            applicable = evaluator.applicable.get(row["instance_pointer"], [])
            if not applicable:
                refuse(
                    "unclassified_instance_numeric_position",
                    f"{role}: token at {row['instance_pointer']} has no applicable rule",
                )
            rules = {entry["position_rule"] for entry in applicable}
            if rules - set(FINAL_RULE_PRECEDENCE):
                refuse(
                    "multiply_classified_instance_position",
                    f"{role}: unexpected rule set {sorted(rules)}",
                )
        trace_counts[role] = len(located)

    graph = core.get("digest_dependency_graph")
    graph_nodes = graph.get("nodes") if isinstance(graph, dict) else None
    graph_edges = [
        (edge.get("subject"), edge.get("dependency"))
        for edge in (graph.get("edges") if isinstance(graph, dict) else []) or []
        if isinstance(edge, dict)
    ]
    if graph_nodes != list(EXPECTED_GRAPH_NODES) or graph_edges != list(
        EXPECTED_GRAPH_EDGES
    ) or any(subject == dependency for subject, dependency in graph_edges):
        refuse(
            "digest_dependency_graph_mismatch",
            "retained digest dependency graph differs from expectation",
        )
    evidence, evidence_raw = parsed["profile_evidence"]
    core_binding = evidence.get("profile_core_binding")
    if not isinstance(core_binding, dict) or (
        core_binding.get("profile_core_raw_digest") != sha256(core_raw)
        or core_binding.get("profile_core_byte_count") != len(core_raw)
    ):
        refuse(
            "digest_dependency_graph_mismatch",
            "evidence core binding differs from recomputed core bytes",
        )
    schema_bindings = evidence.get("successor_schema_bindings")
    if not isinstance(schema_bindings, list) or len(schema_bindings) != 12:
        refuse(
            "digest_dependency_graph_mismatch",
            "evidence successor schema bindings are not twelve rows",
        )
    binding_by_path = {
        binding.get("path"): binding
        for binding in schema_bindings
        if isinstance(binding, dict)
    }
    for row in SUBJECT_ROWS:
        if row[2] is None:
            continue
        _, raw = parsed[row[0]]
        binding = binding_by_path.get(row[1])
        if not isinstance(binding, dict) or (
            binding.get("schema_id") != row[2]
            or binding.get("raw_digest") != sha256(raw)
            or binding.get("byte_count") != len(raw)
        ):
            refuse(
                "digest_dependency_graph_mismatch",
                f"evidence binding for {row[1]} differs from recomputed bytes",
            )
    migration, _ = parsed["profile_migration"]
    successor_binding = migration.get("successor_profile_binding")
    if not isinstance(successor_binding, dict) or (
        successor_binding.get("profile_evidence_raw_digest") != sha256(evidence_raw)
        or successor_binding.get("profile_evidence_byte_count") != len(evidence_raw)
        or successor_binding.get("profile_core_raw_digest") != sha256(core_raw)
        or successor_binding.get("profile_core_byte_count") != len(core_raw)
    ):
        refuse(
            "digest_dependency_graph_mismatch",
            "migration record does not bind the exact evidence and core bytes",
        )
    return {"inventory": inventory, "parsed": parsed, "trace_counts": trace_counts}


def census_validate(view: RepositoryView, parsed: dict[str, tuple[Any, bytes]]) -> None:
    """Layer 5: contract, input-manifest, and manifest byte census."""
    contract_raw = view.read_bytes(CONTRACT_PATH)
    contract = view.parse(CONTRACT_PATH)
    if contract.get("contract_id") != "prq-002f-numeric-trace-conformance-contract.0001":
        refuse("subject_census_mismatch", "unexpected contract identity")
    if contract.get("metaschema_evaluation_disposition") != METASCHEMA_DISPOSITION:
        refuse(
            "metaschema_disposition_mismatch",
            "contract metaschema disposition differs from the frozen settlement",
        )
    if contract.get("schema_document_token_rule") != SCHEMA_DOCUMENT_TOKEN_RULE:
        refuse(
            "metaschema_disposition_mismatch",
            "contract schema-document token rule differs from the frozen settlement",
        )
    vocabulary = contract.get("closed_schema_vocabulary", {})
    if (
        sorted(vocabulary.get("applicator_keywords", [])) != sorted(APPLICATOR_KEYWORDS)
        or sorted(vocabulary.get("assertion_keywords", [])) != sorted(ASSERTION_KEYWORDS)
        or sorted(vocabulary.get("annotation_keywords", [])) != sorted(ANNOTATION_KEYWORDS)
        or vocabulary.get("unknown_keyword_disposition") != "refuse_not_ignore"
    ):
        refuse(
            "closed_vocabulary_violation",
            "contract closed vocabulary differs from the frozen vocabulary",
        )
    if list(contract.get("final_position_rule_precedence", [])) != list(
        FINAL_RULE_PRECEDENCE
    ):
        refuse(
            "multiply_classified_instance_position",
            "contract final-rule precedence differs from the frozen precedence",
        )
    if sorted(contract.get("refusal_codes", [])) != sorted(REFUSAL_CODES):
        refuse(
            "subject_census_mismatch",
            "contract refusal-code vocabulary differs from the frozen vocabulary",
        )
    for key in (
        "subject_count_decimal",
        "schema_document_subject_count_decimal",
        "record_instance_subject_count_decimal",
    ):
        require_decimal(contract.get(key), f"contract.{key}")
    if (
        contract.get("subject_count_decimal") != "15"
        or contract.get("schema_document_subject_count_decimal") != "12"
        or contract.get("record_instance_subject_count_decimal") != "3"
    ):
        refuse("subject_census_mismatch", "contract subject counts differ")
    contract_subjects = contract.get("subjects")
    if not isinstance(contract_subjects, list) or len(contract_subjects) != 15:
        refuse("subject_census_mismatch", "contract subject census is not 15 rows")
    for index, (role, relative, schema_id, governing) in enumerate(SUBJECT_ROWS):
        _, raw = parsed[role]
        row = contract_subjects[index]
        require_decimal(row.get("byte_count_decimal"), f"contract subject {role}")
        if (
            row.get("role") != role
            or row.get("repository_path") != relative
            or row.get("raw_sha256") != sha256(raw)
            or row.get("byte_count_decimal") != str(len(raw))
            or row.get("subject_kind")
            != ("schema_document" if schema_id else "record_instance")
            or (schema_id is not None and row.get("schema_id") != schema_id)
            or (governing is not None and row.get("governing_schema_role") != governing)
        ):
            refuse(
                "subject_byte_binding_mismatch",
                f"contract subject row for {relative} differs from observed bytes",
            )
    boundary = contract.get("claim_boundary", {})
    for claim in (
        "product_identity_computed", "profile_issued", "resource_admitted",
        "prq_002_closed", "gate_a_complete", "runtime_authorized",
        "publication_authorized", "organizational_independence_proven",
        "independent_host_reproduction_complete",
        "historical_process_independently_witnessed",
        "rfc_8785_serialization_conformance_proven",
        "generic_number_semantics_established",
        "out_of_cohort_conformance_established",
        "complete_offline_resolution_proven",
    ):
        if boundary.get(claim) is not False:
            refuse(
                "authority_nonclaim_violation",
                f"contract claim boundary flips nonclaim {claim}",
            )

    input_manifest = view.parse(
        "tests/profile-0-3-numeric-trace-conformance/input-manifest.json"
    )
    require_decimal(
        input_manifest.get("subject_count_decimal"), "input-manifest.subject_count"
    )
    manifest_subjects = input_manifest.get("subjects")
    if (
        input_manifest.get("answer_free") is not True
        or input_manifest.get("subject_count_decimal") != "15"
        or not isinstance(manifest_subjects, list)
        or [
            (row.get("role"), row.get("repository_path"))
            for row in manifest_subjects
        ]
        != [(row[0], row[1]) for row in SUBJECT_ROWS]
    ):
        refuse(
            "subject_census_mismatch",
            "input manifest census differs from the frozen fifteen-row cohort",
        )
    for flag in (
        "network_access_allowed",
        "environment_path_discovery_allowed",
        "expectation_manifest_may_be_passed_to_runner",
        "peer_source_may_be_passed_to_runner",
        "peer_result_may_be_passed_to_runner",
    ):
        if input_manifest.get(flag) is not False:
            refuse(
                "fallback_resolution_forbidden",
                f"input manifest flips isolation flag {flag}",
            )
    if input_manifest.get("authority_claim_allowed") is not False:
        refuse(
            "authority_nonclaim_violation",
            "input manifest permits an authority claim",
        )

    manifest = view.parse("tests/profile-0-3-numeric-trace-conformance/manifest.json")
    census = manifest.get("census", {})
    for key, expected in (
        ("subject_count_decimal", "15"),
        ("schema_document_subject_count_decimal", "12"),
        ("record_instance_subject_count_decimal", "3"),
        ("source_separated_implementation_count_decimal", "2"),
    ):
        require_decimal(census.get(key), f"manifest.census.{key}")
        if census.get(key) != expected:
            refuse("subject_census_mismatch", f"manifest census {key} differs")
    require_decimal(
        census.get("gate_known_bad_count_decimal"), "manifest.census.known_bads"
    )
    if census.get("gate_known_bad_count_decimal") != str(len(KNOWN_BADS)):
        refuse(
            "subject_census_mismatch",
            "manifest known-bad census differs from the embedded corpus",
        )
    boundary = manifest.get("claim_boundary", {})
    for claim, value in boundary.items():
        if value is not False:
            refuse(
                "authority_nonclaim_violation",
                f"manifest claim boundary flips nonclaim {claim}",
            )
    cases = view.parse("tests/profile-0-3-numeric-trace-conformance/cases.json")
    require_decimal(
        cases.get("exact_known_bad_count_decimal"), "cases.known_bad_count"
    )
    if cases.get("exact_known_bad_count_decimal") != str(len(KNOWN_BADS)):
        refuse(
            "subject_census_mismatch",
            "case declaration count differs from the embedded corpus",
        )
    declared = [row.get("name") for row in cases.get("known_bads", [])]
    if declared != [name for name, _, _, _ in KNOWN_BADS]:
        refuse(
            "subject_census_mismatch",
            "case declaration names differ from the embedded corpus",
        )
    declared_residue = [row.get("name") for row in cases.get("declared_unreachable", [])]
    if declared_residue != list(DECLARED_UNREACHABLE):
        refuse(
            "subject_census_mismatch",
            "declared-unreachable residue differs from the frozen declaration",
        )


def results_validate(view: RepositoryView) -> None:
    """Layer 6: retained results, execution receipts, comparison receipt."""
    results: dict[str, tuple[bytes, Any]] = {}
    for role in ("python", "node"):
        relative = (
            f"tests/profile-0-3-numeric-trace-conformance/results/{role}-trace-result.json"
        )
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        if (
            document.get("artifact_class") != "prq_002f_numeric_trace_result"
            or document.get("suite_id") != SUITE_ID
            or document.get("implementation_role") != role
        ):
            refuse(
                "source_separation_violation",
                f"{relative}: implementation identity differs from its role",
            )
        expected_id = (
            "python-stdlib-numeric-trace.0001"
            if role == "python"
            else "nodejs-native-numeric-trace.0001"
        )
        if document.get("implementation_id") != expected_id:
            refuse(
                "source_separation_violation",
                f"{relative}: implementation id differs from its role",
            )
        projection = document.get("projection")
        if document.get("projection_sha256") != sha256(compact_bytes(projection)):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: projection digest does not bind the projection",
            )
        results[role] = (raw, document)
    python_projection = compact_bytes(results["python"][1]["projection"])
    node_projection = compact_bytes(results["node"][1]["projection"])
    if python_projection != node_projection:
        refuse(
            "projection_comparison_mismatch",
            "retained projections are not byte-identical",
        )
    projection = results["python"][1]["projection"]
    contract_raw = view.read_bytes(CONTRACT_PATH)
    binding = projection.get("contract_binding", {})
    if (
        binding.get("raw_sha256") != sha256(contract_raw)
        or binding.get("byte_count_decimal") != str(len(contract_raw))
    ):
        refuse(
            "execution_binding_mismatch",
            "retained projection does not bind the exact contract bytes",
        )
    settlement = projection.get("metaschema_settlement", {})
    if (
        settlement.get("schema_document_token_rule") != SCHEMA_DOCUMENT_TOKEN_RULE
        or settlement.get("metaschema_evaluation_disposition") != METASCHEMA_DISPOSITION
    ):
        refuse(
            "metaschema_disposition_mismatch",
            "retained projection metaschema settlement differs",
        )
    for claim, value in projection.get("claim_boundary", {}).items():
        if claim != "conformance_scope" and value is not False:
            refuse(
                "authority_nonclaim_violation",
                f"retained projection flips nonclaim {claim}",
            )
    if (
        projection.get("claim_boundary", {}).get("conformance_scope")
        != "exact_fifteen_subject_cohort_only"
    ):
        refuse(
            "authority_nonclaim_violation",
            "retained projection widens the conformance scope",
        )
    for role in ("python", "node"):
        source_manifest = view.parse(
            f"tests/profile-0-3-numeric-trace-conformance/{role}/source-manifest.json"
        )
        for source_row in source_manifest.get("source_files", []):
            bound_raw = view.read_bytes(source_row.get("repository_path"))
            if (
                source_row.get("raw_sha256") != sha256(bound_raw)
                or source_row.get("byte_count_decimal") != str(len(bound_raw))
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
        relative = (
            "tests/profile-0-3-numeric-trace-conformance/results/"
            f"{role}-execution-receipt.json"
        )
        receipt = view.parse(relative)
        if (
            receipt.get("artifact_class") != "prq_002f_numeric_trace_execution_receipt"
            or receipt.get("suite_id") != SUITE_ID
            or receipt.get("self_attested_byte_consistency_record") is not True
            or receipt.get("independently_witnessed_process_evidence") is not False
        ):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: receipt identity or attestation class differs",
            )
        for binding_key, bound_relative in (
            (
                "source_manifest_binding",
                f"tests/profile-0-3-numeric-trace-conformance/{role}/source-manifest.json",
            ),
            (
                "runner_binding",
                "tests/profile-0-3-numeric-trace-conformance/python/runner.py"
                if role == "python"
                else "tests/profile-0-3-numeric-trace-conformance/node/runner.mjs",
            ),
            ("contract_binding", CONTRACT_PATH),
            (
                "result_binding",
                "tests/profile-0-3-numeric-trace-conformance/results/"
                f"{role}-trace-result.json",
            ),
        ):
            bound_raw = view.read_bytes(bound_relative)
            entry = receipt.get(binding_key, {})
            require_decimal(
                entry.get("byte_count_decimal"), f"{relative}:{binding_key}"
            )
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
    comparison_relative = (
        "tests/profile-0-3-numeric-trace-conformance/results/comparison-receipt.json"
    )
    comparison = view.parse(comparison_relative)
    if (
        comparison.get("artifact_class") != "prq_002f_numeric_trace_comparison_receipt"
        or comparison.get("projections_byte_identical") is not True
        or comparison.get("comparison_method") != "exact_projection_byte_equality"
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
        ("suite_manifest_binding", "tests/profile-0-3-numeric-trace-conformance/manifest.json"),
        ("input_manifest_binding", "tests/profile-0-3-numeric-trace-conformance/input-manifest.json"),
        ("contract_binding", CONTRACT_PATH),
        ("contract_schema_binding", CONTRACT_SCHEMA_PATH),
        ("case_declaration_binding", "tests/profile-0-3-numeric-trace-conformance/cases.json"),
        ("validator_binding", "scripts/validate_profile_0_3_numeric_trace_conformance.py"),
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
                "tests/profile-0-3-numeric-trace-conformance/python/source-manifest.json",
                "tests/profile-0-3-numeric-trace-conformance/node/source-manifest.json",
            ],
        ),
        (
            "result_bindings",
            [
                "tests/profile-0-3-numeric-trace-conformance/results/python-trace-result.json",
                "tests/profile-0-3-numeric-trace-conformance/results/node-trace-result.json",
            ],
        ),
        (
            "execution_receipt_bindings",
            [
                "tests/profile-0-3-numeric-trace-conformance/results/python-execution-receipt.json",
                "tests/profile-0-3-numeric-trace-conformance/results/node-execution-receipt.json",
            ],
        ),
    ):
        rows = comparison.get(group)
        if not isinstance(rows, list) or [
            row.get("repository_path") for row in rows
        ] != expected_paths:
            refuse(
                "projection_comparison_mismatch",
                f"comparison receipt {group} census differs",
            )
        for row in rows:
            bound_raw = view.read_bytes(row.get("repository_path"))
            if (
                row.get("raw_sha256") != sha256(bound_raw)
                or row.get("byte_count_decimal") != str(len(bound_raw))
            ):
                refuse(
                    "projection_comparison_mismatch",
                    f"comparison receipt {group} does not bind current bytes",
                )


_BASE_DEEP_OUTCOME: dict[str, Any] | None = None
_SUBJECT_PATHS = frozenset(row[1] for row in SUBJECT_ROWS)


def run_static(view: RepositoryView) -> dict[str, Any]:
    # Deep layers 1-4 depend only on the fifteen subject byte strings. A
    # known-bad overlay that leaves every subject untouched reuses the base
    # deep outcome; any overlay touching a subject re-runs the deep layers.
    global _BASE_DEEP_OUTCOME
    touches_subjects = any(path in _SUBJECT_PATHS for path in view.overlay)
    if touches_subjects or _BASE_DEEP_OUTCOME is None:
        outcome = deep_validate(view)
        if not view.overlay:
            _BASE_DEEP_OUTCOME = outcome
    else:
        outcome = _BASE_DEEP_OUTCOME
    census_validate(view, outcome["parsed"])
    results_validate(view)
    return outcome


# --- known-bad corpus ---------------------------------------------------------


def mutate_bytes(relative: str, old: bytes, new: bytes) -> dict[str, bytes]:
    raw = (ROOT / relative).read_bytes()
    if raw.count(old) < 1:
        raise AssertionError(f"known-bad anchor missing in {relative}: {old[:60]!r}")
    return {relative: raw.replace(old, new, 1)}


def mutate_json(relative: str, transform: Callable[[Any], Any]) -> dict[str, bytes]:
    document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    document = transform(document) or document
    indent = 1 if not relative.startswith("schemas/") else 1
    raw = (
        json.dumps(document, indent=indent, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")
    return {relative: raw}


CORE = "architecture/canonicalization-profile-core-0.3-candidate.json"
EVIDENCE = "architecture/canonicalization-profile-0.3-candidate-evidence.json"
MIGRATION = "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json"
MIGRATION_SCHEMA = "schemas/canonicalization-profile-migration-v0-2.schema.json"
PY_RESULT = "tests/profile-0-3-numeric-trace-conformance/results/python-trace-result.json"
ND_RESULT = "tests/profile-0-3-numeric-trace-conformance/results/node-trace-result.json"
PY_RECEIPT = (
    "tests/profile-0-3-numeric-trace-conformance/results/python-execution-receipt.json"
)
COMPARISON = (
    "tests/profile-0-3-numeric-trace-conformance/results/comparison-receipt.json"
)
INPUT_MANIFEST = "tests/profile-0-3-numeric-trace-conformance/input-manifest.json"
MANIFEST = "tests/profile-0-3-numeric-trace-conformance/manifest.json"
CASES = "tests/profile-0-3-numeric-trace-conformance/cases.json"
PY_SOURCE_MANIFEST = (
    "tests/profile-0-3-numeric-trace-conformance/python/source-manifest.json"
)


def _kb_record_integral_float() -> dict[str, bytes]:
    return mutate_bytes(MIGRATION, b'"successor_resource_count": 12,', b'"successor_resource_count": 12.0,')


def _kb_record_exponent() -> dict[str, bytes]:
    return mutate_bytes(MIGRATION, b'"successor_resource_count": 12,', b'"successor_resource_count": 12e0,')


def _kb_record_negative_zero() -> dict[str, bytes]:
    return mutate_bytes(MIGRATION, b'"successor_resource_count": 12,', b'"successor_resource_count": -0,')


def _kb_record_unsafe_integer() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION,
        b'"successor_resource_count": 12,',
        b'"successor_resource_count": 9007199254740992,',
    )


def _kb_record_duplicate_member() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION,
        b'"schema_version": "0.2.0",',
        b'"schema_version": "0.2.0", "schema_version": "0.2.0",',
    )


def _kb_schema_type_number() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION_SCHEMA, b'"type": "integer"', b'"type": "number"'
    )


def _kb_schema_number_union() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION_SCHEMA, b'"type": "integer"', b'"type": ["integer", "number"]'
    )


def _kb_schema_boolean_swap() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION_SCHEMA, b'"type": "integer"', b'"type": "boolean"'
    )


def _kb_inventory_count_tamper() -> dict[str, bytes]:
    return mutate_bytes(
        CORE,
        b'"schema_document_numeric_token_count": 8,',
        b'"schema_document_numeric_token_count": 9,',
    )


def _kb_inventory_digest_tamper() -> dict[str, bytes]:
    core_raw = (ROOT / CORE).read_bytes()
    document = json.loads(core_raw)
    digest = document["static_numeric_applicability_inventory"]["schemas"][0][
        "position_inventory_sha256"
    ]
    flipped = digest[:-1] + ("0" if digest[-1] != "0" else "1")
    return mutate_bytes(CORE, digest.encode(), flipped.encode())


def _kb_inventory_flag_flip() -> dict[str, bytes]:
    return mutate_bytes(
        CORE,
        b'"schema_document_numeric_literals_are_future_instance_positions": false',
        b'"schema_document_numeric_literals_are_future_instance_positions": true',
    )


def _kb_out_of_cohort_ref() -> dict[str, bytes]:
    return mutate_bytes(
        "schemas/schema-registry-v0-9.schema.json",
        b'"$ref": "#/$defs/digest"',
        b'"$ref": "urn:odeya:schema:not-in-cohort:9.9.9#/$defs/digest"',
    )


def _kb_record_const_drift() -> dict[str, bytes]:
    return mutate_bytes(
        MIGRATION,
        b'"artifact_class": "canonicalization_profile_migration_candidate"',
        b'"artifact_class": "canonicalization_profile_migration_candidatex"',
    )


def _kb_graph_edge_swap() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        edges = document["digest_dependency_graph"]["edges"]
        edges[0], edges[1] = edges[1], edges[0]
        return document

    return mutate_json(CORE, transform)


def _kb_evidence_binding_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["successor_schema_bindings"][0]["byte_count"] += 1
        return document

    return mutate_json(EVIDENCE, transform)


def _kb_migration_binding_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        binding = document["successor_profile_binding"]
        digest = binding["profile_evidence_raw_digest"]
        binding["profile_evidence_raw_digest"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(MIGRATION, transform)


def _kb_contract_digest_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["subjects"][0]["raw_sha256"]
        document["subjects"][0]["raw_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_contract_row_drop() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["subjects"].pop()
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_contract_row_reorder() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        subjects = document["subjects"]
        subjects[0], subjects[1] = subjects[1], subjects[0]
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_contract_decimal_typing() -> dict[str, bytes]:
    return mutate_bytes(
        CONTRACT_PATH, b'"subject_count_decimal": "15"', b'"subject_count_decimal": 15'
    )


def _kb_contract_authority_flip() -> dict[str, bytes]:
    return mutate_bytes(
        CONTRACT_PATH,
        b'"publication_authorized": false',
        b'"publication_authorized": true',
    )


def _kb_contract_metaschema_flip() -> dict[str, bytes]:
    return mutate_bytes(
        CONTRACT_PATH,
        b'"metaschema_evaluation_disposition": "blocked_out_of_cohort_metaschema_not_retained"',
        b'"metaschema_evaluation_disposition": "evaluated_against_metaschema"',
    )


def _kb_contract_vocabulary_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["closed_schema_vocabulary"]["assertion_keywords"].append(
            "unevaluatedProperties"
        )
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_contract_precedence_swap() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["final_position_rule_precedence"].reverse()
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_contract_refusal_code_drop() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["refusal_codes"].pop()
        return document

    return mutate_json(CONTRACT_PATH, transform)


def _kb_input_manifest_row_drop() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["subjects"].pop()
        return document

    return mutate_json(INPUT_MANIFEST, transform)


def _kb_input_manifest_network_flip() -> dict[str, bytes]:
    return mutate_bytes(
        INPUT_MANIFEST,
        b'"network_access_allowed": false',
        b'"network_access_allowed": true',
    )


def _kb_input_manifest_authority_flip() -> dict[str, bytes]:
    return mutate_bytes(
        INPUT_MANIFEST,
        b'"authority_claim_allowed": false',
        b'"authority_claim_allowed": true',
    )


def _kb_manifest_census_tamper() -> dict[str, bytes]:
    return mutate_bytes(
        MANIFEST, b'"subject_count_decimal": "15"', b'"subject_count_decimal": "14"'
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


def _kb_cases_count_tamper() -> dict[str, bytes]:
    document = json.loads((ROOT / CASES).read_text(encoding="utf-8"))
    count = document["exact_known_bad_count_decimal"]
    return mutate_bytes(
        CASES,
        f'"exact_known_bad_count_decimal": "{count}"'.encode(),
        f'"exact_known_bad_count_decimal": "{int(count) + 1}"'.encode(),
    )


def _kb_result_projection_tamper() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RESULT,
        b'"schema_count_decimal":"12"',
        b'"schema_count_decimal":"13"',
    )


def _kb_result_role_swap() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RESULT, b'"implementation_role":"python"', b'"implementation_role":"node"'
    )


def _kb_result_copy_across() -> dict[str, bytes]:
    return {ND_RESULT: (ROOT / PY_RESULT).read_bytes()}


def _kb_result_scope_widen() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RESULT,
        b'"conformance_scope":"exact_fifteen_subject_cohort_only"',
        b'"conformance_scope":"all_resources"',
    )


def _kb_receipt_binding_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["source_manifest_binding"]["raw_sha256"]
        document["source_manifest_binding"]["raw_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(PY_RECEIPT, transform)


def _kb_receipt_attestation_flip() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RECEIPT,
        b'"independently_witnessed_process_evidence": false',
        b'"independently_witnessed_process_evidence": true',
    )


def _kb_receipt_executable_drift() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["executable_binding_post"]["raw_sha256"]
        document["executable_binding_post"]["raw_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(PY_RECEIPT, transform)


def _kb_source_manifest_drift() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["source_files"][0]["raw_sha256"]
        document["source_files"][0]["raw_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(PY_SOURCE_MANIFEST, transform)


def _kb_source_manifest_peer_flip() -> dict[str, bytes]:
    return mutate_bytes(
        PY_SOURCE_MANIFEST,
        b'"peer_result_consumption_allowed": false',
        b'"peer_result_consumption_allowed": true',
    )


def _kb_comparison_digest_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["projection_sha256"]
        document["projection_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
        )
        return document

    return mutate_json(COMPARISON, transform)


def _kb_comparison_validator_unbind() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        digest = document["validator_binding"]["raw_sha256"]
        document["validator_binding"]["raw_sha256"] = digest[:-1] + (
            "0" if digest[-1] != "0" else "1"
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
    ("record-integral-float", "raw_tokens", "raw_token_policy_violation", _kb_record_integral_float),
    ("record-exponent-token", "raw_tokens", "raw_token_policy_violation", _kb_record_exponent),
    ("record-negative-zero", "raw_tokens", "raw_token_policy_violation", _kb_record_negative_zero),
    ("record-unsafe-integer", "raw_tokens", "raw_token_policy_violation", _kb_record_unsafe_integer),
    ("record-duplicate-member", "raw_tokens", "raw_token_reconciliation_mismatch", _kb_record_duplicate_member),
    ("schema-type-number", "inventory", "unclassified_numeric_position", _kb_schema_type_number),
    ("schema-number-union", "inventory", "unclassified_numeric_position", _kb_schema_number_union),
    ("schema-boolean-swap", "inventory", "unclassified_numeric_position", _kb_schema_boolean_swap),
    ("inventory-count-tamper", "inventory", "static_inventory_recomputation_mismatch", _kb_inventory_count_tamper),
    ("inventory-digest-tamper", "inventory", "static_inventory_recomputation_mismatch", _kb_inventory_digest_tamper),
    ("inventory-flag-flip", "inventory", "static_inventory_recomputation_mismatch", _kb_inventory_flag_flip),
    ("schema-out-of-cohort-ref", "inventory", "out_of_cohort_reference", _kb_out_of_cohort_ref),
    ("record-const-drift", "conformance", "record_schema_validation_failed", _kb_record_const_drift),
    ("graph-edge-swap", "graph", "record_schema_validation_failed", _kb_graph_edge_swap),
    ("evidence-binding-tamper", "graph", "digest_dependency_graph_mismatch", _kb_evidence_binding_tamper),
    ("migration-binding-tamper", "graph", "digest_dependency_graph_mismatch", _kb_migration_binding_tamper),
    ("contract-digest-tamper", "census", "subject_byte_binding_mismatch", _kb_contract_digest_tamper),
    ("contract-row-drop", "census", "subject_census_mismatch", _kb_contract_row_drop),
    ("contract-row-reorder", "census", "subject_byte_binding_mismatch", _kb_contract_row_reorder),
    ("contract-decimal-typing", "census", "census_decimal_typing_violation", _kb_contract_decimal_typing),
    ("contract-authority-flip", "census", "authority_nonclaim_violation", _kb_contract_authority_flip),
    ("contract-metaschema-flip", "census", "metaschema_disposition_mismatch", _kb_contract_metaschema_flip),
    ("contract-vocabulary-tamper", "census", "closed_vocabulary_violation", _kb_contract_vocabulary_tamper),
    ("contract-precedence-swap", "census", "multiply_classified_instance_position", _kb_contract_precedence_swap),
    ("contract-refusal-code-drop", "census", "subject_census_mismatch", _kb_contract_refusal_code_drop),
    ("input-manifest-row-drop", "census", "subject_census_mismatch", _kb_input_manifest_row_drop),
    ("input-manifest-network-flip", "census", "fallback_resolution_forbidden", _kb_input_manifest_network_flip),
    ("input-manifest-authority-flip", "census", "authority_nonclaim_violation", _kb_input_manifest_authority_flip),
    ("manifest-census-tamper", "census", "subject_census_mismatch", _kb_manifest_census_tamper),
    ("manifest-known-bad-census", "census", "subject_census_mismatch", _kb_manifest_known_bad_census),
    ("manifest-authority-flip", "census", "authority_nonclaim_violation", _kb_manifest_authority_flip),
    ("cases-count-tamper", "census", "subject_census_mismatch", _kb_cases_count_tamper),
    ("result-projection-tamper", "results", "execution_binding_mismatch", _kb_result_projection_tamper),
    ("result-role-swap", "results", "source_separation_violation", _kb_result_role_swap),
    ("result-copy-across", "results", "source_separation_violation", _kb_result_copy_across),
    ("result-scope-widen", "results", "execution_binding_mismatch", _kb_result_scope_widen),
    ("receipt-binding-tamper", "results", "execution_binding_mismatch", _kb_receipt_binding_tamper),
    ("receipt-attestation-flip", "results", "execution_binding_mismatch", _kb_receipt_attestation_flip),
    ("receipt-executable-drift", "results", "execution_binding_mismatch", _kb_receipt_executable_drift),
    ("source-manifest-drift", "results", "source_separation_violation", _kb_source_manifest_drift),
    ("source-manifest-peer-flip", "results", "source_separation_violation", _kb_source_manifest_peer_flip),
    ("comparison-digest-tamper", "results", "projection_comparison_mismatch", _kb_comparison_digest_tamper),
    ("comparison-validator-unbind", "results", "projection_comparison_mismatch", _kb_comparison_validator_unbind),
    ("comparison-method-downgrade", "results", "projection_comparison_mismatch", _kb_comparison_method_downgrade),
)

# Two refusal codes are structurally unreachable by an isolated retained-byte
# mutation and are declared residue rather than silently omitted:
# `duplicate_instance_pointer` requires two identical RFC 6901 pointers, which
# valid JSON can only produce through a duplicate member name that the parser
# refuses first; `unclassified_instance_numeric_position` requires a governed
# record token with no applicable rule, which cannot be constructed without
# also breaking the schema-validation or byte-binding guards that fire first.
DECLARED_UNREACHABLE = (
    "duplicate-instance-pointer-distinct-from-duplicate-member",
    "unclassified-instance-token-with-valid-record",
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
    if failures:
        for failure in failures:
            print(f"KNOWN-BAD FAILURE: {failure}")
        return len(failures)
    return 0


# --- recompute mode -----------------------------------------------------------


def recompute_all(python_executable: str, node_executable: str) -> list[str]:
    errors: list[str] = []
    for role, executable, extra in (
        ("python", python_executable, ["-I", "-B"]),
        ("node", node_executable, ["--disable-proto=throw"]),
    ):
        runner = (
            SUITE / "python/runner.py" if role == "python" else SUITE / "node/runner.mjs"
        )
        resolved = Path(executable).resolve(strict=True)
        completed = subprocess.run(
            [
                resolved.as_posix(),
                *extra,
                runner.as_posix(),
                "--repository-root",
                ROOT.as_posix(),
                "--contract",
                (ROOT / CONTRACT_PATH).as_posix(),
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
            timeout=180,
            check=False,
        )
        retained = (
            SUITE / f"results/{role}-trace-result.json"
        ).read_bytes()
        if completed.returncode != 0 or completed.stderr:
            errors.append(f"{role}: fresh execution failed")
        elif completed.stdout != retained:
            errors.append(f"{role}: fresh stdout differs from retained result bytes")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--recompute-all", action="store_true")
    parser.add_argument("--python-executable")
    parser.add_argument("--node-executable")
    arguments = parser.parse_args()

    for relative in RETAINED_SUITE_PATHS + (CONTRACT_PATH, CONTRACT_SCHEMA_PATH):
        target = ROOT / relative
        if target.is_symlink() or not target.is_file():
            print(f"PRQ-002F missing or non-regular retained path: {relative}")
            return 1

    try:
        outcome = run_static(RepositoryView())
    except Refusal as refusal:
        print(f"PRQ-002F REFUSED [{refusal.code}]: {refusal.detail}")
        return 1
    failures = run_known_bads()
    if failures:
        return 1
    if arguments.recompute_all:
        if not arguments.python_executable or not arguments.node_executable:
            print("--recompute-all requires --python-executable and --node-executable")
            return 1
        errors = recompute_all(arguments.python_executable, arguments.node_executable)
        if errors:
            for error in errors:
                print(f"PRQ-002F RECOMPUTE FAILURE: {error}")
            return 1
    totals = outcome["inventory"]["schemas"]
    print(
        "PRQ-002F numeric trace conformance retained evidence passed: "
        f"subjects=15, schemas=12, records=3, "
        f"document_tokens={sum(row['schema_document_numeric_token_count'] for row in totals)}, "
        f"record_tokens={sum(outcome['trace_counts'].values())}, "
        f"known_bads={len(KNOWN_BADS)}, declared_unreachable={len(DECLARED_UNREACHABLE)}; "
        "conformance_scope=exact_fifteen_subject_cohort_only; "
        "identity=false, issuance=false, gate_a=false, authority=false"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
