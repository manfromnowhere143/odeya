"""Deterministically generate the PRQ-002G JCS conformance corpus.

Emits the answer-free `vectors.json` (each frame is raw input bytes as
lowercase hexadecimal, so invalid-UTF-8 and byte-order-mark frames are
representable) and the private expectation file `cases.json` (per-frame
disposition and refusal code only; canonical outputs are never authored here
— they are computed independently by both runners and re-derived by the
validator's third path). `--check` verifies both files equal their retained
bytes without writing.

No implementation may read `cases.json`; the generator reads no
implementation. Architecture evidence only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
SUITE_ID = "prq-002g-jcs-serialization-conformance.0001"


def frame(frame_id: str, raw: bytes, disposition: str, code: str | None = None):
    entry = {"frame_id": frame_id, "raw_hex": raw.hex()}
    expectation = {"frame_id": frame_id, "expected_disposition": disposition}
    if code is not None:
        expectation["expected_refusal_code"] = code
    return entry, expectation


def accepted(frame_id: str, text: str):
    return frame(frame_id, text.encode("utf-8"), "accepted")


def accepted_bytes(frame_id: str, raw: bytes):
    return frame(frame_id, raw, "accepted")


def refused(frame_id: str, text: str, code: str):
    return frame(frame_id, text.encode("utf-8"), "refused", code)


def refused_bytes(frame_id: str, raw: bytes, code: str):
    return frame(frame_id, raw, "refused", code)


def corpus():
    rows = [
        # --- accepted: containers, ordering, arrays ---
        accepted("empty-object", "{}"),
        accepted("empty-array", "[]"),
        accepted("simple-member-ordering", '{"b": 1, "a": 2}'),
        accepted(
            "nested-recursive-ordering",
            '{"z": {"d": 1, "c": {"b": [], "a": {}}}, "y": [{"n": 2, "m": 3}]}',
        ),
        accepted("array-order-preserved", "[3, 1, 2, [true, null, false]]"),
        accepted("empty-name-orders-first", '{"a": 1, "": 2}'),
        accepted("prefix-name-ordering", '{"ab": 1, "aB": 2, "a": 3}'),
        # The discriminating vector: U+E000 is one UTF-16 unit 0xE000, while
        # U+1F600 encodes as the surrogate pair 0xD83D 0xDE00. Unsigned
        # UTF-16 code-unit order puts the supplementary name FIRST; Unicode
        # code-point order puts it LAST. A code-point sort cannot pass.
        accepted("utf16-unit-order-discriminator", '{"": 1, "\U0001F600": 2}'),
        accepted("bmp-vs-astral-values-preserved", '["", "\U0001F600"]'),
        accepted(
            "escaped-astral-name-decodes",
            '{"\\ud83d\\ude00": 1, "\\uE000": 2}',
        ),
        # --- accepted: escape handling ---
        accepted("escaped-ascii-name-canonicalizes", '{"\\u0061": 1}'),
        accepted("solidus-escaped-emits-plain", '"a\\/b"'),
        accepted("solidus-literal-emits-plain", '"a/b"'),
        accepted("short-escape-normal-forms", '"\\b\\f\\n\\r\\t\\"\\\\"'),
        accepted("control-chars-lowercase-u-escapes", '"\\u0000\\u0001\\u001f"'),
        accepted("delete-char-passes-literal", '"\\u007f"'),
        accepted("escaped-value-astral-emits-literal", '"\\ud83d\\ude00"'),
        # --- accepted: unicode passthrough without normalization ---
        accepted("latin-e-acute-precomposed", '"café"'),
        accepted("latin-e-combining-stays-distinct", '"café"'),
        accepted("mixed-scripts-literal", '{"ש": "ü", "中": "\U0001F680"}'),
        # --- accepted: profile-bounded integers ---
        accepted("integer-zero", "0"),
        accepted("integer-minus-one", "-1"),
        accepted("safe-integer-maximum", "9007199254740991"),
        accepted("safe-integer-minimum", "-9007199254740991"),
        accepted("integers-inside-structures", '{"n": [0, 42, -7]}'),
        # --- accepted: literals, strings, whitespace ---
        accepted("bare-literals", "[true, false, null]"),
        accepted("digit-strings-are-not-numbers", '{"v": "12.5", "e": "1e0"}'),
        accepted(
            "whitespace-heavy-input-compacts",
            '  {\n\t"b" :\r [ 1 ,  2 ] ,  "a" : { }  }  ',
        ),
        # --- refused: profile number boundary ---
        refused("integral-fraction-refuses", "1.0", "non_integer_number_token"),
        refused("integral-exponent-refuses", "1e0", "non_integer_number_token"),
        refused("plain-fraction-refuses", "1.5", "non_integer_number_token"),
        refused("nested-float-refuses", '{"a": [2.25]}', "non_integer_number_token"),
        refused("negative-zero-refuses", "-0", "lexical_negative_zero"),
        refused(
            "nested-negative-zero-refuses", '{"n": -0}', "lexical_negative_zero"
        ),
        refused(
            "above-safe-range-refuses",
            "9007199254740992",
            "integer_outside_safe_range",
        ),
        refused(
            "below-safe-range-refuses",
            "-9007199254740992",
            "integer_outside_safe_range",
        ),
        refused("nan-literal-refuses", '{"v": NaN}', "non_finite_literal"),
        refused("infinity-literal-refuses", "[Infinity]", "non_finite_literal"),
        refused(
            "negative-infinity-refuses", "[-Infinity]", "non_finite_literal"
        ),
        # --- refused: duplicate decoded names ---
        refused(
            "plain-duplicate-name-refuses",
            '{"a": 1, "a": 2}',
            "duplicate_decoded_member_name",
        ),
        refused(
            "escape-equal-duplicate-refuses",
            '{"a": 1, "\\u0061": 2}',
            "duplicate_decoded_member_name",
        ),
        refused(
            "astral-escape-equal-duplicate-refuses",
            '{"\U0001F600": 1, "\\ud83d\\ude00": 2}',
            "duplicate_decoded_member_name",
        ),
        # --- refused: encoding and framing ---
        refused_bytes(
            "leading-bom-refuses", b"\xef\xbb\xbf{}", "leading_byte_order_mark"
        ),
        refused("trailing-content-refuses", '{} x', "trailing_content"),
        refused_bytes(
            "invalid-utf8-refuses", b'"\xff"', "invalid_utf8_encoding"
        ),
        refused_bytes(
            "truncated-utf8-refuses", b'"\xe2\x82"', "invalid_utf8_encoding"
        ),
        # --- refused: surrogates and noncharacters ---
        refused("lone-high-surrogate-refuses", '"\\ud800"', "unpaired_surrogate"),
        refused("lone-low-surrogate-refuses", '"\\udc00"', "unpaired_surrogate"),
        refused(
            "high-surrogate-then-bmp-refuses",
            '"\\ud800\\u0041"',
            "unpaired_surrogate",
        ),
        refused(
            "bmp-noncharacter-fffe-refuses", '"\\ufffe"', "unicode_noncharacter"
        ),
        refused(
            "arena-noncharacter-fdd0-refuses", '"\\ufdd0"', "unicode_noncharacter"
        ),
        refused_bytes(
            "literal-noncharacter-ffff-refuses",
            '"￿"'.encode("utf-8"),
            "unicode_noncharacter",
        ),
        # --- refused: strict grammar ---
        refused("unterminated-string-refuses", '"abc', "malformed_json"),
        refused("trailing-comma-refuses", "[1, 2,]", "malformed_json"),
        refused("single-quotes-refuse", "{'a': 1}", "malformed_json"),
        refused("leading-plus-refuses", "+1", "malformed_json"),
        refused("bare-fraction-refuses", ".5", "malformed_json"),
        refused("leading-zero-refuses", "01", "trailing_content"),
        refused("hex-number-refuses", "0x10", "trailing_content"),
        refused_bytes(
            "raw-control-byte-refuses", b'"\x01"', "malformed_json"
        ),
        refused("empty-input-refuses", "", "malformed_json"),
    ]
    frames = [row[0] for row in rows]
    expectations = [row[1] for row in rows]
    identifiers = [entry["frame_id"] for entry in frames]
    if len(set(identifiers)) != len(identifiers):
        raise SystemExit("duplicate frame_id in corpus definition")
    return frames, expectations


def encode(document) -> bytes:
    return (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    frames, expectations = corpus()
    accepted_count = sum(
        1 for row in expectations if row["expected_disposition"] == "accepted"
    )
    refused_count = len(expectations) - accepted_count
    vectors = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002g_jcs_conformance_vectors",
        "suite_id": SUITE_ID,
        "answer_free": True,
        "expected_outcomes_included": False,
        "frame_count_decimal": str(len(frames)),
        "frame_encoding": "raw_input_bytes_lowercase_hex",
        "frames": frames,
    }
    cases = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002g_jcs_conformance_case_expectations",
        "suite_id": SUITE_ID,
        "private_expectation_file": True,
        "consumable_by_implementations": False,
        "frame_count_decimal": str(len(frames)),
        "accepted_count_decimal": str(accepted_count),
        "refused_count_decimal": str(refused_count),
        "expectations": expectations,
    }
    outputs = {
        "vectors.json": encode(vectors),
        "cases.json": encode(cases),
    }
    failures = []
    for relative, raw in outputs.items():
        target = SUITE / relative
        if arguments.check:
            if not target.is_file() or target.read_bytes() != raw:
                failures.append(relative)
        else:
            target.write_bytes(raw)
    if arguments.check and failures:
        print("PRQ-002G corpus differs from deterministic regeneration: " + ", ".join(failures))
        return 1
    print(
        ("verified" if arguments.check else "generated")
        + f" PRQ-002G corpus: {len(frames)} frames"
        + f" ({accepted_count} accepted, {refused_count} refused)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
