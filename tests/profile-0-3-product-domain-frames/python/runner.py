"""PRQ-002H nine-domain frame governance runner (CPython path).

For every frame of the answer-free corpus: strict raw-octet parsing with
duplicate-name, surrogate, noncharacter, and profile raw-number refusal;
closed-vocabulary evaluation against the frame's governing product schema
over the exact twelve-schema cohort; a per-token applicability trace binding
every raw number lexeme to its unique RFC 6901 pointer and exactly one final
rule; and, for any frame the schema accepts, a byte-identity requirement
against the retained frozen structural-nonidentity fixture — so only the
nine frozen fixtures can ever be accepted, and every accepted governance
claim is pinned to exact retained bytes.

Zero third-party dependencies. Source-separated from the Node.js peer; never
reads the private expectation file. Bounded architecture evidence only: no
product identity, digest, membership, issuance, or authority follows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
SUITE_ID = "prq-002h-product-domain-frames.0001"
IMPLEMENTATION_ID = "python-stdlib-domain-governor.0001"
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
FINAL_RULE_PRECEDENCE = ("recursive_integer_valued_const_leaf", "integer_type")
FIXTURE_DIR = "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity"

# The complete schema-reference census, hard-coded independently of every
# shared file and of the Node implementation.
SCHEMA_ROWS: tuple[tuple[str, str], ...] = (
    ("schemas/schema-resource-record-v0-2.schema.json", "urn:odeya:schema:schema-resource-record:0.2.0"),
    ("schemas/aggregate-state-subject-record-v0-2.schema.json", "urn:odeya:schema:aggregate-state-subject-record:0.2.0"),
    ("schemas/reducer-contract-record-v0-2.schema.json", "urn:odeya:schema:reducer-contract-record:0.2.0"),
    ("schemas/event-contract-record-v0-2.schema.json", "urn:odeya:schema:event-contract-record:0.2.0"),
    ("schemas/ordered-member-map-commitment-v0-2.schema.json", "urn:odeya:schema:ordered-member-map-commitment:0.2.0"),
    ("schemas/schema-registry-v0-9.schema.json", "urn:odeya:schema:schema-registry:0.9.0"),
    ("schemas/aggregate-state-subject-registry-v0-8.schema.json", "urn:odeya:schema:aggregate-state-subject-registry:0.8.0"),
    ("schemas/reducer-registry-v0-8.schema.json", "urn:odeya:schema:reducer-registry:0.8.0"),
    ("schemas/event-contract-registry-v0-8.schema.json", "urn:odeya:schema:event-contract-registry:0.8.0"),
    ("schemas/canonicalization-profile-core-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-core:0.7.0"),
    ("schemas/canonicalization-profile-candidate-evidence-v0-7.schema.json", "urn:odeya:schema:canonicalization-profile-candidate-evidence:0.7.0"),
    ("schemas/canonicalization-profile-migration-v0-2.schema.json", "urn:odeya:schema:canonicalization-profile-migration:0.2.0"),
)
# domain -> (fixture slug, governing schema $id)
DOMAIN_ROWS: tuple[tuple[str, str, str], ...] = (
    ("schema_resource_record", "schema-resource-record-v0-2", "urn:odeya:schema:schema-resource-record:0.2.0"),
    ("aggregate_state_subject_record", "aggregate-state-subject-record-v0-2", "urn:odeya:schema:aggregate-state-subject-record:0.2.0"),
    ("reducer_contract_record", "reducer-contract-record-v0-2", "urn:odeya:schema:reducer-contract-record:0.2.0"),
    ("event_contract_record", "event-contract-record-v0-2", "urn:odeya:schema:event-contract-record:0.2.0"),
    ("ordered_member_map_commitment", "ordered-member-map-commitment-v0-2", "urn:odeya:schema:ordered-member-map-commitment:0.2.0"),
    ("schema_registry", "schema-registry-v0-9", "urn:odeya:schema:schema-registry:0.9.0"),
    ("aggregate_state_subject_registry", "aggregate-state-subject-registry-v0-8", "urn:odeya:schema:aggregate-state-subject-registry:0.8.0"),
    ("reducer_registry", "reducer-registry-v0-8", "urn:odeya:schema:reducer-registry:0.8.0"),
    ("event_contract_registry", "event-contract-registry-v0-8", "urn:odeya:schema:event-contract-registry:0.8.0"),
)
APPLICATOR_KEYWORDS = {
    "$ref", "allOf", "if", "then", "else", "items", "prefixItems",
    "properties", "additionalProperties", "$defs",
}
ASSERTION_KEYWORDS = {
    "type", "const", "enum", "required", "pattern", "maximum", "minimum",
    "maxItems", "minItems", "maxLength", "minLength", "uniqueItems",
}
ANNOTATION_KEYWORDS = {
    "$schema", "$id", "title", "description", "format",
    "x-odeya-digest-scope", "x-odeya-number-token-policy",
}
CLOSED_VOCABULARY = APPLICATOR_KEYWORDS | ASSERTION_KEYWORDS | ANNOTATION_KEYWORDS


class Refusal(Exception):
    """Whole-projection refusal."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class FrameRefusal(Exception):
    """Per-frame refusal recorded as data."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def refuse(code: str, detail: str) -> None:
    raise Refusal(code, detail)


def frame_refuse(code: str) -> None:
    raise FrameRefusal(code)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def pointer_escape(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def parse_integer(lexeme: str) -> int:
    if not INTEGER_RE.fullmatch(lexeme):
        frame_refuse("non_integer_number_token")
    if lexeme.startswith("-0"):
        frame_refuse("lexical_negative_zero")
    value = int(lexeme)
    if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        frame_refuse("integer_outside_safe_range")
    return value


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            frame_refuse("duplicate_decoded_member_name")
        result[key] = value
    return result


def scan_strings(value: Any) -> None:
    if isinstance(value, str):
        for character in value:
            code_point = ord(character)
            if 0xD800 <= code_point <= 0xDFFF:
                frame_refuse("unpaired_surrogate")
            if 0xFDD0 <= code_point <= 0xFDEF or (code_point & 0xFFFF) in (
                0xFFFE,
                0xFFFF,
            ):
                frame_refuse("unicode_noncharacter")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            scan_strings(key)
            scan_strings(child)
    elif isinstance(value, list):
        for child in value:
            scan_strings(child)


def parse_frame(raw: bytes) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        frame_refuse("leading_byte_order_mark")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        frame_refuse("invalid_utf8_encoding")
    decoder = json.JSONDecoder(
        object_pairs_hook=strict_pairs,
        parse_int=parse_integer,
        parse_float=lambda lexeme: frame_refuse("non_integer_number_token"),
        parse_constant=lambda lexeme: frame_refuse("non_finite_literal"),
    )
    start = 0
    while start < len(text) and text[start] in " \t\n\r":
        start += 1
    try:
        document, end = decoder.raw_decode(text, start)
    except FrameRefusal:
        raise
    except ValueError:
        frame_refuse("malformed_json")
    if text[end:].strip(" \t\n\r"):
        frame_refuse("trailing_content")
    scan_strings(document)
    return document


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
                frame_refuse("malformed_json")
            tokens.append(match.group(0))
            index = match.end()
            continue
        index += 1
    return tokens


def iter_locations(value: Any, pointer: str = ""):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_locations(child, f"{pointer}/{pointer_escape(key)}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_locations(child, f"{pointer}/{index}")


def integer_token_rows(document: Any, raw: bytes) -> list[dict[str, str]]:
    tokens = raw_number_tokens(raw)
    located = [
        {"instance_pointer": pointer, "raw_lexeme": str(value)}
        for pointer, value in iter_locations(document)
        if type(value) is int
    ]
    if [row["raw_lexeme"] for row in located] != tokens:
        frame_refuse("malformed_json")
    pointers = [row["instance_pointer"] for row in located]
    if len(set(pointers)) != len(pointers):
        frame_refuse("malformed_json")
    return located


def resolve_pointer(document: Any, fragment: str) -> Any:
    if fragment in ("", "#"):
        return document
    if not fragment.startswith("#/"):
        frame_refuse("out_of_cohort_reference")
    current = document
    for encoded in fragment[2:].split("/"):
        token = encoded.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError):
                frame_refuse("out_of_cohort_reference")
        else:
            frame_refuse("out_of_cohort_reference")
    return current


class ClosedEvaluator:
    def __init__(self, by_id: dict[str, tuple[Any, bytes]]) -> None:
        self.by_id = by_id
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
                frame_refuse("closed_vocabulary_violation")
        digest = sha256(self.by_id[schema_id][1])
        valid = True
        reference = node.get("$ref")
        if isinstance(reference, str):
            target_base, separator, suffix = reference.partition("#")
            resolved_id = target_base or schema_id
            if resolved_id not in self.by_id:
                frame_refuse("out_of_cohort_reference")
            fragment = f"#{suffix}" if separator else ""
            ref_key = (resolved_id, fragment or "#", instance_pointer)
            if ref_key in ref_stack:
                frame_refuse("out_of_cohort_reference")
            target_node = resolve_pointer(self.by_id[resolved_id][0], fragment)
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


def load_repository_file(root: Path, relative: str) -> bytes:
    path = root / relative
    if path.is_symlink() or not path.is_file():
        refuse(
            "corpus_census_mismatch",
            f"{relative}: not a regular non-symlink repository file",
        )
    return path.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--vectors", required=True)
    parser.add_argument("--source-manifest", required=True)
    arguments = parser.parse_args()
    root = Path(arguments.repository_root)

    by_id: dict[str, tuple[Any, bytes]] = {}
    for relative, schema_id in SCHEMA_ROWS:
        raw = load_repository_file(root, relative)
        document = json.loads(raw)
        if document.get("$id") != schema_id:
            refuse("corpus_census_mismatch", f"{relative}: schema $id drift")
        by_id[schema_id] = (document, raw)
    fixtures: dict[str, tuple[bytes, str]] = {}
    for domain, slug, governing_id in DOMAIN_ROWS:
        relative = f"{FIXTURE_DIR}/prq-002e-{slug}.structural-nonidentity.json"
        raw = load_repository_file(root, relative)
        fixtures[domain] = (raw, governing_id)

    vectors_raw = Path(arguments.vectors).read_bytes()
    vectors = json.loads(vectors_raw)
    if vectors.get("suite_id") != SUITE_ID or vectors.get("answer_free") is not True:
        refuse("corpus_census_mismatch", "vector file identity differs")

    rows = []
    accepted = 0
    refused_count = 0
    for frame in vectors["frames"]:
        frame_id = frame["frame_id"]
        domain = frame["domain"]
        if domain not in fixtures:
            refuse("corpus_census_mismatch", f"{frame_id}: unknown domain")
        fixture_raw, governing_id = fixtures[domain]
        raw = bytes.fromhex(frame["raw_hex"])
        try:
            document = parse_frame(raw)
            evaluator = ClosedEvaluator(by_id)
            errors: list[str] = []
            if not evaluator.evaluate(
                governing_id, by_id[governing_id][0], "", document, "",
                ((governing_id, "#", ""),), errors,
            ):
                frame_refuse("record_schema_validation_failed")
            located = integer_token_rows(document, raw)
            tokens = []
            for token in located:
                applicable = evaluator.applicable.get(token["instance_pointer"], [])
                if not applicable:
                    frame_refuse("unclassified_instance_numeric_position")
                rules = {entry["position_rule"] for entry in applicable}
                if rules - set(FINAL_RULE_PRECEDENCE):
                    frame_refuse("multiply_classified_instance_position")
                final_rule = (
                    FINAL_RULE_PRECEDENCE[0]
                    if FINAL_RULE_PRECEDENCE[0] in rules
                    else FINAL_RULE_PRECEDENCE[1]
                )
                tokens.append(
                    {
                        "ordinal_decimal": str(len(tokens)),
                        "raw_lexeme": token["raw_lexeme"],
                        "decimal_value": token["raw_lexeme"],
                        "instance_pointer": token["instance_pointer"],
                        "classification": {
                            "final_rule": final_rule,
                            "applicable_assertions": applicable,
                        },
                    }
                )
            # Acceptance is reserved for the exact frozen fixture bytes: a
            # schema-valid instance that is not the retained fixture refuses.
            if raw != fixture_raw:
                frame_refuse("fixture_byte_binding_mismatch")
            accepted += 1
            rows.append(
                {
                    "frame_id": frame_id,
                    "domain": domain,
                    "disposition": "accepted",
                    "governing_schema_id": governing_id,
                    "governing_schema_raw_digest": sha256(by_id[governing_id][1]),
                    "raw_sha256": sha256(raw),
                    "byte_count_decimal": str(len(raw)),
                    "token_count_decimal": str(len(tokens)),
                    "tokens": tokens,
                }
            )
        except FrameRefusal as refusal:
            refused_count += 1
            rows.append(
                {
                    "frame_id": frame_id,
                    "domain": domain,
                    "disposition": "refused",
                    "refusal_code": refusal.code,
                }
            )
    projection = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002h_product_domain_frame_projection",
        "suite_id": SUITE_ID,
        "vectors_binding": {
            "raw_sha256": sha256(vectors_raw),
            "frame_count_decimal": str(len(rows)),
        },
        "census": {
            "domain_count_decimal": str(len(DOMAIN_ROWS)),
            "accepted_count_decimal": str(accepted),
            "refused_count_decimal": str(refused_count),
        },
        "frames": rows,
        "claim_boundary": {
            "governed_instances_are_structural_nonidentity_fixtures_only": True,
            "product_identity_computed": False,
            "product_digest_computed": False,
            "profile_issued": False,
            "prq_002_closed": False,
            "gate_a_complete": False,
            "publication_authorized": False,
        },
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002h_product_domain_frame_result",
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
                    "artifact_class": "prq_002h_product_domain_frame_refusal",
                    "suite_id": SUITE_ID,
                    "implementation_id": IMPLEMENTATION_ID,
                    "refusal_code": refusal.code,
                    "detail": refusal.detail,
                }
            )
        )
        sys.exit(1)
