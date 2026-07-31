"""PRQ-002G profile-bounded JCS serialization runner (CPython path).

Implements the exact `odeya-jcs-0.3` serialization interpretation pinned by
ADR 0103 and retained by ADR 0107, restricted to the profile's admitted
token set: strict UTF-8 with BOM refusal, strict RFC 8259 grammar with
duplicate decoded-name refusal, I-JSON surrogate and noncharacter refusal,
integer-only numbers in the inclusive safe range, recursive member ordering
by unsigned UTF-16 code units over decoded names (realized explicitly via
UTF-16BE byte comparison, never native code-point comparison), ECMAScript
2019 string escaping with U+002F emitted unescaped, and final UTF-8
canonical bytes.

Zero third-party dependencies. Source-separated from the Node.js peer; never
reads the private expectation file. Emits one deterministic result document
on stdout. Bounded architecture evidence only.
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
SUITE_ID = "prq-002g-jcs-serialization-conformance.0001"
IMPLEMENTATION_ID = "python-stdlib-jcs-serializer.0001"
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
SHORT_ESCAPES = {
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
    '"': '\\"',
    "\\": "\\\\",
}


class Refusal(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def refuse(code: str) -> None:
    raise Refusal(code)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def parse_integer(lexeme: str) -> int:
    if not INTEGER_RE.fullmatch(lexeme):
        refuse("non_integer_number_token")
    if lexeme.startswith("-0"):
        refuse("lexical_negative_zero")
    value = int(lexeme)
    if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        refuse("integer_outside_safe_range")
    return value


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            refuse("duplicate_decoded_member_name")
        result[key] = value
    return result


def scan_strings(value: Any) -> None:
    if isinstance(value, str):
        for character in value:
            code_point = ord(character)
            if 0xD800 <= code_point <= 0xDFFF:
                refuse("unpaired_surrogate")
            if 0xFDD0 <= code_point <= 0xFDEF or (code_point & 0xFFFF) in (
                0xFFFE,
                0xFFFF,
            ):
                refuse("unicode_noncharacter")
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
        refuse("leading_byte_order_mark")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        refuse("invalid_utf8_encoding")
    decoder = json.JSONDecoder(
        object_pairs_hook=strict_pairs,
        parse_int=parse_integer,
        parse_float=lambda lexeme: refuse("non_integer_number_token"),
        parse_constant=lambda lexeme: refuse("non_finite_literal"),
    )
    start = 0
    while start < len(text) and text[start] in " \t\n\r":
        start += 1
    try:
        document, end = decoder.raw_decode(text, start)
    except Refusal:
        raise
    except ValueError:
        refuse("malformed_json")
    if text[end:].strip(" \t\n\r"):
        refuse("trailing_content")
    scan_strings(document)
    return document


def escape_string(value: str) -> str:
    out = ['"']
    for character in value:
        if character in SHORT_ESCAPES:
            out.append(SHORT_ESCAPES[character])
        elif ord(character) < 0x20:
            out.append(f"\\u{ord(character):04x}")
        else:
            out.append(character)
    out.append('"')
    return "".join(out)


def utf16_key(name: str) -> bytes:
    return name.encode("utf-16-be")


def serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, str):
        return escape_string(value)
    if isinstance(value, list):
        return "[" + ",".join(serialize(child) for child in value) + "]"
    if isinstance(value, dict):
        ordered = sorted(value.keys(), key=utf16_key)
        return (
            "{"
            + ",".join(
                escape_string(name) + ":" + serialize(value[name])
                for name in ordered
            )
            + "}"
        )
    refuse("malformed_json")


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--vectors", required=True)
    parser.add_argument("--source-manifest", required=True)
    arguments = parser.parse_args()
    vectors = json.loads(Path(arguments.vectors).read_text(encoding="utf-8"))
    if vectors.get("suite_id") != SUITE_ID or vectors.get("answer_free") is not True:
        raise SystemExit("vector file identity is not the answer-free corpus")
    rows = []
    accepted = 0
    refused_count = 0
    for frame in vectors["frames"]:
        frame_id = frame["frame_id"]
        raw = bytes.fromhex(frame["raw_hex"])
        try:
            document = parse_frame(raw)
            canonical = serialize(document).encode("utf-8")
            accepted += 1
            rows.append(
                {
                    "frame_id": frame_id,
                    "disposition": "accepted",
                    "canonical_hex": canonical.hex(),
                    "canonical_sha256": sha256(canonical),
                    "canonical_byte_count_decimal": str(len(canonical)),
                }
            )
        except Refusal as refusal:
            refused_count += 1
            rows.append(
                {
                    "frame_id": frame_id,
                    "disposition": "refused",
                    "refusal_code": refusal.code,
                }
            )
    projection = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002g_jcs_conformance_projection",
        "suite_id": SUITE_ID,
        "vectors_binding": {
            "raw_sha256": sha256(Path(arguments.vectors).read_bytes()),
            "frame_count_decimal": str(len(rows)),
        },
        "census": {
            "accepted_count_decimal": str(accepted),
            "refused_count_decimal": str(refused_count),
        },
        "frames": rows,
        "claim_boundary": {
            "profile_bounded_integer_scope_only": True,
            "general_binary64_serialization_proven": False,
            "product_digest_computed": False,
            "profile_issued": False,
            "gate_a_complete": False,
            "publication_authorized": False,
        },
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "artifact_class": "prq_002g_jcs_conformance_result",
        "suite_id": SUITE_ID,
        "implementation_id": IMPLEMENTATION_ID,
        "implementation_role": "python",
        "projection_sha256": sha256(compact_bytes(projection)),
        "projection": projection,
    }
    sys.stdout.buffer.write(compact_bytes(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
