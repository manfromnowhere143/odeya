"""PRQ-002F raw-aware numeric trace conformance runner (CPython path).

Recomputes the static numeric-position inventory of the twelve final
`odeya-jcs-0.3` schemas from raw bytes, settles schema-document versus
metaschema treatment as an explicit typed disposition, constructs complete
raw-aware applicability traces for the fifteen frozen construction subjects,
and executes one complete cross-object conformance path over the exact
cohort. Zero third-party dependencies. The peer Node.js implementation is
source-separated; neither consumes the other's source or result, and this
runner never reads the suite's private expectations.

Any violation refuses the whole projection with exactly one declared refusal
code on stdout and exit status 1. Success emits one deterministic result
document on stdout and exit status 0. This is bounded architecture evidence
about exact frozen bytes: no conformance beyond the fifteen subjects, no
product identity, no profile issuance, no PRQ-002 closure, no Gate A
acceptance, and no runtime or publication authority follows.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
SUITE_ID = "prq-002f-numeric-trace-conformance.0001"
IMPLEMENTATION_ID = "python-stdlib-numeric-trace.0001"
CONTRACT_PATH = (
    "architecture/prq-002f-numeric-trace-conformance-contract-v1-candidate.json"
)
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.3"
RAW_NUMBER_CONTRACT_ID = (
    "urn:odeya:canonicalization:raw-number-token-contract:0.1.0"
)
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
SCHEMA_DOCUMENT_TOKEN_RULE = "schema_definition_data_not_instance_position"
METASCHEMA_DISPOSITION = "blocked_out_of_cohort_metaschema_not_retained"
FINAL_RULE_PRECEDENCE = ("recursive_integer_valued_const_leaf", "integer_type")

# The complete fifteen-row subject census is hard-coded here, independently of
# the shared input manifest and of the Node implementation, so a mutation of
# one shared file cannot become two-implementation consensus.
SUBJECT_ROWS: tuple[tuple[str, str, str, str, str | None, str, str | None], ...] = (
    (
        "schema_resource_record_schema",
        "schemas/schema-resource-record-v0-2.schema.json",
        "sha256:9e7dc959e8d764e0665d36e8e45af9102cc837ebf35f87a5e3591766db0689a9",
        "9420",
        "urn:odeya:schema:schema-resource-record:0.2.0",
        "schema_document",
        None,
    ),
    (
        "aggregate_state_subject_record_schema",
        "schemas/aggregate-state-subject-record-v0-2.schema.json",
        "sha256:6e0b10755f32795cb71eebd4cd627921563bda8f333367a59b0ebb61723a73e0",
        "17537",
        "urn:odeya:schema:aggregate-state-subject-record:0.2.0",
        "schema_document",
        None,
    ),
    (
        "reducer_contract_record_schema",
        "schemas/reducer-contract-record-v0-2.schema.json",
        "sha256:18f5e6f866ac2add6d4620dd6f2a5473ca5b8d150f11d81e5ce6896c46639523",
        "19324",
        "urn:odeya:schema:reducer-contract-record:0.2.0",
        "schema_document",
        None,
    ),
    (
        "event_contract_record_schema",
        "schemas/event-contract-record-v0-2.schema.json",
        "sha256:3bae0e8f44e0b88b6e467c789db75aa1d4ddfbbb27aada9221d7b7cacc4c3d2c",
        "13937",
        "urn:odeya:schema:event-contract-record:0.2.0",
        "schema_document",
        None,
    ),
    (
        "ordered_member_map_commitment_schema",
        "schemas/ordered-member-map-commitment-v0-2.schema.json",
        "sha256:d672627e678ab5149bc27d2a2a6833823978975057a74593deb34775790a56ac",
        "10712",
        "urn:odeya:schema:ordered-member-map-commitment:0.2.0",
        "schema_document",
        None,
    ),
    (
        "schema_registry_schema",
        "schemas/schema-registry-v0-9.schema.json",
        "sha256:914dc00de6caad731b776eab7b99bfe573a8fab1211d12f366a986aff4acb4df",
        "7703",
        "urn:odeya:schema:schema-registry:0.9.0",
        "schema_document",
        None,
    ),
    (
        "aggregate_state_subject_registry_schema",
        "schemas/aggregate-state-subject-registry-v0-8.schema.json",
        "sha256:a04c6ea24414dcb6279d73b6583f45bab90c53264737d8a95e12afd227a7dc8c",
        "7931",
        "urn:odeya:schema:aggregate-state-subject-registry:0.8.0",
        "schema_document",
        None,
    ),
    (
        "reducer_registry_schema",
        "schemas/reducer-registry-v0-8.schema.json",
        "sha256:ca919c845a555c6e336d0f750038a7415e6d54c714c0374ebc31a75e172e36ce",
        "7716",
        "urn:odeya:schema:reducer-registry:0.8.0",
        "schema_document",
        None,
    ),
    (
        "event_contract_registry_schema",
        "schemas/event-contract-registry-v0-8.schema.json",
        "sha256:b2895f003ed4c56fe8cd4037386b343daabb91e46bf5b214912e3727ce39cafd",
        "7806",
        "urn:odeya:schema:event-contract-registry:0.8.0",
        "schema_document",
        None,
    ),
    (
        "profile_core_schema",
        "schemas/canonicalization-profile-core-v0-7.schema.json",
        "sha256:47b726f0c4a62870567a5c2228d7510e86fc3e28f100bdd62962f35d39b8e330",
        "219537",
        "urn:odeya:schema:canonicalization-profile-core:0.7.0",
        "schema_document",
        None,
    ),
    (
        "profile_evidence_schema",
        "schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json",
        "sha256:3f01f5902b6d0a52aa12dd638b225784559379dba3b64f65e97bd2f3fa7fbe64",
        "185844",
        "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0",
        "schema_document",
        None,
    ),
    (
        "profile_migration_schema",
        "schemas/canonicalization-profile-migration-v0-2.schema.json",
        "sha256:3573eba7ddd9209e9d3039282a8db41db031a267ea0b9003edd8ca7ddd5ab217",
        "64569",
        "urn:odeya:schema:canonicalization-profile-migration:0.2.0",
        "schema_document",
        None,
    ),
    (
        "profile_core",
        "architecture/canonicalization-profile-core-0.3-candidate.json",
        "sha256:d91a7e53b1f729c0750646c8131701187911e5ffbde03897ef81ba0197e31562",
        "790376",
        None,
        "record_instance",
        "profile_core_schema",
    ),
    (
        "profile_evidence",
        "architecture/canonicalization-profile-0.3-candidate-evidence.json",
        "sha256:e53d953481279368159499811e958756d5fa89479828b24a03fcbc0256b2ee4e",
        "778908",
        None,
        "record_instance",
        "profile_evidence_schema",
    ),
    (
        "profile_migration",
        "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json",
        "sha256:6ae5640d8b92b26038a1feb1772a615a476223f392e8f55595903f954eacab37",
        "25869",
        None,
        "record_instance",
        "profile_migration_schema",
    ),
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

APPLICATOR_KEYWORDS = {
    "$ref",
    "allOf",
    "if",
    "then",
    "else",
    "items",
    "prefixItems",
    "properties",
    "additionalProperties",
    "$defs",
}
ASSERTION_KEYWORDS = {
    "type",
    "const",
    "enum",
    "required",
    "pattern",
    "maximum",
    "minimum",
    "maxItems",
    "minItems",
    "maxLength",
    "minLength",
    "uniqueItems",
}
ANNOTATION_KEYWORDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "format",
    "x-odeya-digest-scope",
    "x-odeya-number-token-policy",
}
CLOSED_VOCABULARY = APPLICATOR_KEYWORDS | ASSERTION_KEYWORDS | ANNOTATION_KEYWORDS


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
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            refuse(
                "raw_token_reconciliation_mismatch",
                f"duplicate decoded object member name: {key!r}",
            )
        result[key] = value
    return result


def refuse_float(text: str) -> Any:
    refuse(
        "raw_token_policy_violation",
        f"non-integer raw number token: {text}",
    )


def refuse_constant(text: str) -> Any:
    refuse("raw_token_policy_violation", f"non-finite JSON extension: {text}")


def strict_parse(raw: bytes, subject: str) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        refuse("subject_byte_binding_mismatch", f"{subject}: leading BOM")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        refuse("subject_byte_binding_mismatch", f"{subject}: invalid UTF-8: {exc}")
    try:
        return json.loads(
            text,
            object_pairs_hook=strict_object_pairs,
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
    return [
        {
            "ordinal_decimal": str(ordinal),
            "raw_lexeme": row["raw_lexeme"],
            "decimal_value": row["raw_lexeme"],
            "instance_pointer": row["instance_pointer"],
        }
        for ordinal, row in enumerate(located)
    ]


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


def collect_integer_const_leaves(value: Any, schema_location: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative_pointer, child in iter_locations(value):
        if type(child) is int:
            if not MIN_SAFE_INTEGER <= child <= MAX_SAFE_INTEGER:
                refuse(
                    "raw_token_policy_violation",
                    f"integer const outside safe range: {schema_location}",
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
    by_id: dict[str, tuple[str, Any, bytes]],
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
                    [*evaluation_path, {"kind": "const_object_member", "token": key}],
                    resolved_schema_id,
                    resolved_digest,
                    keyword_location,
                    f"{relative_pointer}/{pointer_escape(key)}",
                )
        elif isinstance(value, list):
            for index, child in enumerate(value):
                append_const_leaves(
                    child,
                    [*evaluation_path, {"kind": "const_array_index", "token": str(index)}],
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
            unclassified.append(f"{resolved_schema_id}#{schema_pointer}:true_schema")
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
            unclassified.append(f"{resolved_schema_id}#{schema_pointer}/type")
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
                unclassified.append(f"{resolved_schema_id}#{schema_pointer}/enum")

        reference = node.get("$ref")
        if isinstance(reference, str):
            target_id, separator, suffix = reference.partition("#")
            target_id = target_id or resolved_schema_id
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
            _, target_document, _ = by_id[target_id]
            descend(
                target_id,
                resolve_pointer(target_document, fragment, target_id),
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
                        [*evaluation_path, {"kind": kind, "token": str(index)}],
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


def recompute_static_inventory(
    schema_documents: dict[str, tuple[Any, bytes]],
    schema_paths_in_order: list[str],
    path_to_id: dict[str, str],
) -> dict[str, Any]:
    by_id = {
        document["$id"]: (path, document, raw)
        for path, (document, raw) in schema_documents.items()
    }
    rows: list[dict[str, Any]] = []
    for path in schema_paths_in_order:
        document, raw = schema_documents[path]
        schema_id = document.get("$id")
        if schema_id != path_to_id[path]:
            refuse("schema_id_mismatch", f"{path}: schema $id drift")
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
                refuse(
                    "static_inventory_recomputation_mismatch",
                    f"{path}: dynamic/recursive reference is outside this inventory",
                )
            reference = node.get("$ref")
            if isinstance(reference, str):
                target_id, separator, suffix = reference.partition("#")
                resolved_id = target_id or schema_id
                if resolved_id not in by_id:
                    refuse(
                        "out_of_cohort_reference",
                        f"{path}: unresolved exact-cohort reference {reference}",
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
                f"{path}: unsupported numeric position: "
                f"type_number={type_numbers}, unions={number_unions}, "
                f"unclassified={unclassified + expanded_unclassified}",
            )
        token_rows = integer_token_rows(document, raw, path)
        document_tokens = [
            {
                "document_pointer": row["instance_pointer"],
                "raw_lexeme": row["raw_lexeme"],
                "decimal_value": row["decimal_value"],
            }
            for row in token_rows
        ]
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
                "expanded_instance_integer_type_position_count": len(expanded_types),
                "expanded_instance_integer_type_positions": expanded_types,
                "expanded_instance_integer_const_position_count": len(expanded_consts),
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


class ClosedEvaluator:
    """Closed-vocabulary Draft 2020-12 subset evaluator over the exact cohort.

    Validates a record instance against its governing schema and collects, for
    every integer-valued instance position, the applicable integer rules. Any
    schema keyword outside the frozen closed vocabulary refuses rather than
    being ignored.
    """

    def __init__(
        self,
        by_id: dict[str, tuple[str, Any, bytes]],
        subject: str,
    ) -> None:
        self.by_id = by_id
        self.subject = subject
        self.applicable: dict[str, list[dict[str, str]]] = {}

    def note(
        self,
        instance_pointer: str,
        schema_id: str,
        schema_digest: str,
        location: str,
        rule: str,
    ) -> None:
        rows = self.applicable.setdefault(instance_pointer, [])
        row = {
            "resolved_schema_id": schema_id,
            "resolved_schema_raw_digest": schema_digest,
            "assertion_schema_location": location,
            "position_rule": rule,
        }
        if row not in rows:
            rows.append(row)

    def check_vocabulary(self, node: dict[str, Any], location: str) -> None:
        for key in node:
            if key not in CLOSED_VOCABULARY:
                refuse(
                    "closed_vocabulary_violation",
                    f"{self.subject}: unimplemented schema keyword {key!r}"
                    f" at {location}",
                )

    def const_matches(
        self,
        expected: Any,
        instance: Any,
        instance_pointer: str,
        schema_id: str,
        schema_digest: str,
        location: str,
        relative: str = "",
    ) -> bool:
        if type(expected) is int:
            if type(instance) is int and instance == expected:
                self.note(
                    instance_pointer,
                    schema_id,
                    schema_digest,
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
                    child,
                    instance[key],
                    f"{instance_pointer}/{pointer_escape(key)}",
                    schema_id,
                    schema_digest,
                    location,
                    f"{relative}/{pointer_escape(key)}",
                )
                for key, child in expected.items()
            )
        if isinstance(expected, list):
            if not isinstance(instance, list) or len(instance) != len(expected):
                return False
            return all(
                self.const_matches(
                    child,
                    instance[index],
                    f"{instance_pointer}/{index}",
                    schema_id,
                    schema_digest,
                    location,
                    f"{relative}/{index}",
                )
                for index, child in enumerate(expected)
            )
        return False

    def evaluate(
        self,
        schema_id: str,
        node: Any,
        schema_pointer: str,
        instance: Any,
        instance_pointer: str,
        ref_stack: tuple[tuple[str, str, str], ...],
        errors: list[str],
    ) -> bool:
        if node is True:
            return True
        if node is False:
            errors.append(f"{instance_pointer}: false schema")
            return False
        if not isinstance(node, dict):
            errors.append(f"{instance_pointer}: non-schema node")
            return False
        location = f"{schema_id}#{schema_pointer}"
        self.check_vocabulary(node, location)
        _, _, schema_raw = self.by_id[schema_id]
        schema_digest = sha256(schema_raw)
        valid = True

        reference = node.get("$ref")
        if isinstance(reference, str):
            target_base, sep2, frag = reference.partition("#")
            resolved_id = target_base or schema_id
            if resolved_id not in self.by_id:
                refuse(
                    "out_of_cohort_reference",
                    f"{self.subject}: reference outside exact cohort {reference}",
                )
            fragment = f"#{frag}" if sep2 else ""
            ref_key = (resolved_id, fragment or "#", instance_pointer)
            if ref_key in ref_stack:
                refuse(
                    "fallback_resolution_forbidden",
                    f"{self.subject}: reference cycle at {reference}",
                )
            _, target_document, _ = self.by_id[resolved_id]
            target_node = resolve_pointer(target_document, fragment, resolved_id)
            if not self.evaluate(
                resolved_id,
                target_node,
                fragment[1:] if fragment else "",
                instance,
                instance_pointer,
                (*ref_stack, ref_key),
                errors,
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
            matched = False
            for type_name in allowed:
                if type_name == "object" and isinstance(instance, dict):
                    matched = True
                elif type_name == "array" and isinstance(instance, list):
                    matched = True
                elif type_name == "string" and isinstance(instance, str):
                    matched = True
                elif type_name == "boolean" and type(instance) is bool:
                    matched = True
                elif type_name == "integer" and type(instance) is int:
                    matched = True
                elif type_name == "null" and instance is None:
                    matched = True
            if not matched:
                errors.append(f"{instance_pointer}: type mismatch at {location}")
                valid = False
            if (
                ("integer" in allowed)
                and type(instance) is int
            ):
                self.note(
                    instance_pointer,
                    schema_id,
                    schema_digest,
                    f"{location}/type",
                    "integer_type",
                )

        if "const" in node:
            if not self.const_matches(
                node["const"],
                instance,
                instance_pointer,
                schema_id,
                schema_digest,
                f"{location}/const",
            ):
                errors.append(f"{instance_pointer}: const mismatch at {location}")
                valid = False
        if "enum" in node:
            if any(type(item) is int for item in node["enum"]) and (
                node_type != "integer"
            ):
                refuse(
                    "unclassified_numeric_position",
                    f"{self.subject}: integer enum outside integer type at "
                    f"{location}/enum",
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
            prefix_length = 0
            if isinstance(prefix, list):
                prefix_length = len(prefix)
                for index, subschema in enumerate(prefix):
                    if index >= len(instance):
                        break
                    if not self.evaluate(
                        schema_id,
                        subschema,
                        f"{schema_pointer}/prefixItems/{index}",
                        instance[index],
                        f"{instance_pointer}/{index}",
                        ref_stack,
                        errors,
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
                            schema_id,
                            items,
                            f"{schema_pointer}/items",
                            instance[index],
                            f"{instance_pointer}/{index}",
                            ref_stack,
                            errors,
                        ):
                            valid = False
        if isinstance(instance, dict):
            required = node.get("required")
            if isinstance(required, list):
                for name in required:
                    if name not in instance:
                        errors.append(
                            f"{instance_pointer}: missing required {name!r} at "
                            f"{location}"
                        )
                        valid = False
            properties = node.get("properties")
            declared: set[str] = set()
            if isinstance(properties, dict):
                declared = set(properties)
                for name, subschema in properties.items():
                    if name in instance:
                        if not self.evaluate(
                            schema_id,
                            subschema,
                            f"{schema_pointer}/properties/{pointer_escape(name)}",
                            instance[name],
                            f"{instance_pointer}/{pointer_escape(name)}",
                            ref_stack,
                            errors,
                        ):
                            valid = False
            if "additionalProperties" in node:
                additional = node["additionalProperties"]
                for name in instance:
                    if name in declared:
                        continue
                    if additional is False:
                        errors.append(
                            f"{instance_pointer}: additional property {name!r} at "
                            f"{location}"
                        )
                        valid = False
                    else:
                        if not self.evaluate(
                            schema_id,
                            additional,
                            f"{schema_pointer}/additionalProperties",
                            instance[name],
                            f"{instance_pointer}/{pointer_escape(name)}",
                            ref_stack,
                            errors,
                        ):
                            valid = False

        all_of = node.get("allOf")
        if isinstance(all_of, list):
            for index, subschema in enumerate(all_of):
                if not self.evaluate(
                    schema_id,
                    subschema,
                    f"{schema_pointer}/allOf/{index}",
                    instance,
                    instance_pointer,
                    ref_stack,
                    errors,
                ):
                    valid = False

        if "if" in node:
            silent: list[str] = []
            condition = self.evaluate(
                schema_id,
                node["if"],
                f"{schema_pointer}/if",
                instance,
                instance_pointer,
                ref_stack,
                silent,
            )
            branch_key = "then" if condition else "else"
            if branch_key in node:
                if not self.evaluate(
                    schema_id,
                    node[branch_key],
                    f"{schema_pointer}/{branch_key}",
                    instance,
                    instance_pointer,
                    ref_stack,
                    errors,
                ):
                    valid = False
        return valid


def load_subject(root: Path, relative: str) -> bytes:
    if "\x00" in relative or relative.startswith("/") or ".." in relative.split("/"):
        refuse("subject_byte_binding_mismatch", f"illegal subject path {relative!r}")
    path = root / relative
    if path.is_symlink() or not path.is_file():
        refuse(
            "subject_byte_binding_mismatch",
            f"{relative}: not a regular non-symlink file",
        )
    return path.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--contract", required=True)
    parser.add_argument("--source-manifest", required=True)
    arguments = parser.parse_args()
    root = Path(arguments.repository_root)

    contract_raw = Path(arguments.contract).read_bytes()
    contract = strict_parse(contract_raw, "contract")
    if contract.get("contract_id") != (
        "prq-002f-numeric-trace-conformance-contract.0001"
    ):
        refuse("subject_census_mismatch", "unexpected contract identity")
    contract_subjects = contract.get("subjects")
    if not isinstance(contract_subjects, list) or len(contract_subjects) != 15:
        refuse("subject_census_mismatch", "contract subject census is not 15 rows")

    subjects: list[dict[str, Any]] = []
    raw_by_role: dict[str, bytes] = {}
    document_by_role: dict[str, Any] = {}
    for index, row in enumerate(SUBJECT_ROWS):
        role, relative, expected_digest, expected_count, schema_id, kind, governing = row
        raw = load_subject(root, relative)
        digest = sha256(raw)
        if expected_digest != "*" and digest != expected_digest:
            refuse(
                "subject_byte_binding_mismatch",
                f"{relative}: raw digest differs from hard-coded census",
            )
        if expected_count != "*" and str(len(raw)) != expected_count:
            refuse(
                "subject_byte_binding_mismatch",
                f"{relative}: byte count differs from hard-coded census",
            )
        contract_row = contract_subjects[index]
        if (
            contract_row.get("role") != role
            or contract_row.get("repository_path") != relative
            or contract_row.get("raw_sha256") != digest
            or contract_row.get("byte_count_decimal") != str(len(raw))
            or contract_row.get("subject_kind") != kind
        ):
            refuse(
                "subject_census_mismatch",
                f"{relative}: contract subject row differs from observed bytes",
            )
        document = strict_parse(raw, relative)
        if kind == "schema_document":
            if document.get("$id") != schema_id or (
                contract_row.get("schema_id") != schema_id
            ):
                refuse("schema_id_mismatch", f"{relative}: schema $id drift")
        else:
            if contract_row.get("governing_schema_role") != governing:
                refuse(
                    "subject_census_mismatch",
                    f"{relative}: governing schema role drift",
                )
        raw_by_role[role] = raw
        document_by_role[role] = document
        subjects.append(
            {
                "role": role,
                "repository_path": relative,
                "raw_sha256": digest,
                "byte_count_decimal": str(len(raw)),
                "subject_kind": kind,
            }
        )

    schema_paths_in_order = [
        row[1] for row in SUBJECT_ROWS if row[5] == "schema_document"
    ]
    path_to_id = {
        row[1]: row[4] for row in SUBJECT_ROWS if row[5] == "schema_document"
    }
    schema_documents = {
        row[1]: (document_by_role[row[0]], raw_by_role[row[0]])
        for row in SUBJECT_ROWS
        if row[5] == "schema_document"
    }
    inventory = recompute_static_inventory(
        schema_documents, schema_paths_in_order, path_to_id
    )

    core = document_by_role["profile_core"]
    retained_inventory = core.get("static_numeric_applicability_inventory")
    if compact_bytes(retained_inventory) != compact_bytes(inventory):
        refuse(
            "static_inventory_recomputation_mismatch",
            "retained core inventory differs from independent recomputation",
        )

    graph = core.get("digest_dependency_graph")
    graph_nodes = graph.get("nodes") if isinstance(graph, dict) else None
    graph_edges = [
        (edge.get("subject"), edge.get("dependency"))
        for edge in (graph.get("edges") if isinstance(graph, dict) else []) or []
        if isinstance(edge, dict)
    ]
    if graph_nodes != list(EXPECTED_GRAPH_NODES) or graph_edges != list(
        EXPECTED_GRAPH_EDGES
    ):
        refuse(
            "digest_dependency_graph_mismatch",
            "retained digest dependency graph differs from expectation",
        )
    if any(subject == dependency for subject, dependency in graph_edges):
        refuse("digest_dependency_graph_mismatch", "self edge in dependency graph")

    evidence = document_by_role["profile_evidence"]
    core_binding = evidence.get("profile_core_binding")
    citation_count = 0
    if not isinstance(core_binding, dict) or (
        core_binding.get("profile_core_raw_digest")
        != sha256(raw_by_role["profile_core"])
        or core_binding.get("profile_core_byte_count")
        != len(raw_by_role["profile_core"])
    ):
        refuse(
            "digest_dependency_graph_mismatch",
            "evidence core binding differs from recomputed core bytes",
        )
    citation_count += 1
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
        if row[5] != "schema_document":
            continue
        binding = binding_by_path.get(row[1])
        if not isinstance(binding, dict) or (
            binding.get("schema_id") != row[4]
            or binding.get("raw_digest") != sha256(raw_by_role[row[0]])
            or binding.get("byte_count") != len(raw_by_role[row[0]])
        ):
            refuse(
                "digest_dependency_graph_mismatch",
                f"evidence binding for {row[1]} differs from recomputed bytes",
            )
        citation_count += 1
    migration = document_by_role["profile_migration"]
    successor_binding = migration.get("successor_profile_binding")
    if not isinstance(successor_binding, dict) or (
        successor_binding.get("profile_evidence_path")
        != "architecture/canonicalization-profile-0.3-candidate-evidence.json"
        or successor_binding.get("profile_evidence_raw_digest")
        != sha256(raw_by_role["profile_evidence"])
        or successor_binding.get("profile_evidence_byte_count")
        != len(raw_by_role["profile_evidence"])
        or successor_binding.get("profile_core_raw_digest")
        != sha256(raw_by_role["profile_core"])
        or successor_binding.get("profile_core_byte_count")
        != len(raw_by_role["profile_core"])
    ):
        refuse(
            "digest_dependency_graph_mismatch",
            "migration record does not bind the exact evidence and core bytes",
        )
    citation_count += 4

    traces: list[dict[str, Any]] = []
    for row in SUBJECT_ROWS:
        role, relative, _, _, schema_id, kind, governing = row
        raw = raw_by_role[role]
        document = document_by_role[role]
        token_rows = integer_token_rows(document, raw, relative)
        if kind == "schema_document":
            inventory_row = next(
                schema
                for schema in inventory["schemas"]
                if schema["schema_path"] == relative
            )
            if len(token_rows) != inventory_row["schema_document_numeric_token_count"]:
                refuse(
                    "raw_token_reconciliation_mismatch",
                    f"{relative}: trace token count differs from inventory",
                )
            tokens = [
                {
                    "ordinal_decimal": token["ordinal_decimal"],
                    "raw_lexeme": token["raw_lexeme"],
                    "decimal_value": token["decimal_value"],
                    "instance_pointer": token["instance_pointer"],
                    "classification": {
                        "final_rule": SCHEMA_DOCUMENT_TOKEN_RULE,
                        "metaschema_evaluation": METASCHEMA_DISPOSITION,
                    },
                }
                for token in token_rows
            ]
        else:
            by_id = {
                schema_row[4]: (
                    schema_row[1],
                    document_by_role[schema_row[0]],
                    raw_by_role[schema_row[0]],
                )
                for schema_row in SUBJECT_ROWS
                if schema_row[5] == "schema_document"
            }
            governing_id = next(
                schema_row[4]
                for schema_row in SUBJECT_ROWS
                if schema_row[0] == governing
            )
            evaluator = ClosedEvaluator(by_id, relative)
            errors: list[str] = []
            _, governing_document, _ = by_id[governing_id]
            if not evaluator.evaluate(
                governing_id,
                governing_document,
                "",
                document,
                "",
                ((governing_id, "#", ""),),
                errors,
            ):
                refuse(
                    "record_schema_validation_failed",
                    f"{relative}: {errors[0] if errors else 'schema validation failed'}",
                )
            tokens = []
            for token in token_rows:
                applicable = evaluator.applicable.get(token["instance_pointer"], [])
                if not applicable:
                    refuse(
                        "unclassified_instance_numeric_position",
                        f"{relative}: token at {token['instance_pointer']} has no "
                        "applicable integer rule",
                    )
                rules = {row_["position_rule"] for row_ in applicable}
                unexpected = rules - set(FINAL_RULE_PRECEDENCE)
                if unexpected:
                    refuse(
                        "multiply_classified_instance_position",
                        f"{relative}: unexpected rule set {sorted(unexpected)}",
                    )
                final_rule = (
                    FINAL_RULE_PRECEDENCE[0]
                    if FINAL_RULE_PRECEDENCE[0] in rules
                    else FINAL_RULE_PRECEDENCE[1]
                )
                tokens.append(
                    {
                        "ordinal_decimal": token["ordinal_decimal"],
                        "raw_lexeme": token["raw_lexeme"],
                        "decimal_value": token["decimal_value"],
                        "instance_pointer": token["instance_pointer"],
                        "classification": {
                            "final_rule": final_rule,
                            "applicable_assertions": applicable,
                        },
                    }
                )
        traces.append(
            {
                "role": role,
                "repository_path": relative,
                "raw_sha256": sha256(raw),
                "byte_count_decimal": str(len(raw)),
                "subject_kind": kind,
                "token_count_decimal": str(len(token_rows)),
                "tokens": tokens,
            }
        )

    totals = {
        "schema_document_numeric_token_count_decimal": str(
            sum(
                schema["schema_document_numeric_token_count"]
                for schema in inventory["schemas"]
            )
        ),
        "integer_type_assertion_count_decimal": str(
            sum(
                schema["integer_type_assertion_count"]
                for schema in inventory["schemas"]
            )
        ),
        "integer_const_leaf_count_decimal": str(
            sum(
                schema["integer_const_leaf_count"] for schema in inventory["schemas"]
            )
        ),
        "expanded_instance_integer_type_position_count_decimal": str(
            sum(
                schema["expanded_instance_integer_type_position_count"]
                for schema in inventory["schemas"]
            )
        ),
        "expanded_instance_integer_const_position_count_decimal": str(
            sum(
                schema["expanded_instance_integer_const_position_count"]
                for schema in inventory["schemas"]
            )
        ),
        "resolved_reference_edge_count_decimal": str(
            sum(
                schema["resolved_reference_edge_count"]
                for schema in inventory["schemas"]
            )
        ),
        "schema_byte_count_decimal": str(
            sum(schema["schema_byte_count"] for schema in inventory["schemas"])
        ),
    }
    projection = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002f_numeric_trace_projection",
        "suite_id": SUITE_ID,
        "profile_id": PROFILE_ID,
        "raw_number_contract_id": RAW_NUMBER_CONTRACT_ID,
        "contract_binding": {
            "repository_path": CONTRACT_PATH,
            "raw_sha256": sha256(contract_raw),
            "byte_count_decimal": str(len(contract_raw)),
        },
        "subject_census": subjects,
        "static_inventory_comparison": {
            "recomputed_matches_retained_core_inventory": True,
            "schema_count_decimal": "12",
            "totals": totals,
            "per_schema": [
                {
                    "schema_id": schema["schema_id"],
                    "schema_raw_digest": schema["schema_raw_digest"],
                    "schema_byte_count_decimal": str(schema["schema_byte_count"]),
                    "schema_document_numeric_token_count_decimal": str(
                        schema["schema_document_numeric_token_count"]
                    ),
                    "schema_document_numeric_token_inventory_sha256": schema[
                        "schema_document_numeric_token_inventory_sha256"
                    ],
                    "position_inventory_sha256": schema["position_inventory_sha256"],
                }
                for schema in inventory["schemas"]
            ],
        },
        "metaschema_settlement": {
            "schema_document_token_rule": SCHEMA_DOCUMENT_TOKEN_RULE,
            "metaschema_evaluation_disposition": METASCHEMA_DISPOSITION,
            "schema_document_subject_count_decimal": "12",
        },
        "traces": traces,
        "cross_object_conformance": {
            "record_validation": [
                {
                    "role": row[0],
                    "governing_schema_role": row[6],
                    "schema_valid": True,
                }
                for row in SUBJECT_ROWS
                if row[5] == "record_instance"
            ],
            "digest_dependency_graph": {
                "node_count_decimal": str(len(EXPECTED_GRAPH_NODES)),
                "edge_count_decimal": str(len(EXPECTED_GRAPH_EDGES)),
                "retained_graph_matches_expectation": True,
                "byte_citation_verified_count_decimal": str(citation_count),
            },
        },
        "claim_boundary": {
            "conformance_scope": "exact_fifteen_subject_cohort_only",
            "product_identity_computed": False,
            "profile_issued": False,
            "prq_002_closed": False,
            "gate_a_complete": False,
            "runtime_authorized": False,
            "publication_authorized": False,
        },
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002f_numeric_trace_result",
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
                    "artifact_class": "prq_002f_numeric_trace_refusal",
                    "suite_id": SUITE_ID,
                    "implementation_id": IMPLEMENTATION_ID,
                    "refusal_code": refusal.code,
                    "detail": refusal.detail,
                }
            )
        )
        sys.exit(1)
