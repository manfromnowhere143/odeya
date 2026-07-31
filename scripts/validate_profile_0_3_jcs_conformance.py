"""Validate the PRQ-002G profile-bounded JCS serialization conformance suite.

Dedicated parent validator and deliberate third implementation of the pinned
`odeya-jcs-0.3` serialization interpretation. It re-derives every frame of
the answer-free corpus from raw bytes with its own serializer, requires the
private expectations and both retained projections to match that derivation
exactly, verifies the execution and comparison receipts, executes an
embedded known-bad corpus in which every mutation refuses with its declared
singleton code, and supports `--recompute-all` re-execution of both runners
against the retained result bytes.

Bounded architecture evidence only: no general binary64 serialization, no
product digest, no issuance, no PRQ-002 closure, no Gate A acceptance, and
no runtime or publication authority follows from a pass.
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
SUITE_PREFIX = "tests/profile-0-3-jcs-conformance"
SUITE = ROOT / SUITE_PREFIX
SUITE_ID = "prq-002g-jcs-serialization-conformance.0001"
MIN_SAFE_INTEGER = -9007199254740991
MAX_SAFE_INTEGER = 9007199254740991
INTEGER_RE = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
FRAME_REFUSAL_CODES = frozenset(
    {
        "non_integer_number_token",
        "lexical_negative_zero",
        "integer_outside_safe_range",
        "non_finite_literal",
        "duplicate_decoded_member_name",
        "leading_byte_order_mark",
        "trailing_content",
        "invalid_utf8_encoding",
        "unpaired_surrogate",
        "unicode_noncharacter",
        "malformed_json",
    }
)
SUITE_REFUSAL_CODES = (
    "authority_nonclaim_violation",
    "census_decimal_typing_violation",
    "corpus_census_mismatch",
    "execution_binding_mismatch",
    "expectation_disposition_mismatch",
    "projection_comparison_mismatch",
    "retained_projection_mismatch",
    "source_separation_violation",
)
RETAINED_SUITE_PATHS = (
    f"{SUITE_PREFIX}/README.md",
    f"{SUITE_PREFIX}/manifest.json",
    f"{SUITE_PREFIX}/vectors.json",
    f"{SUITE_PREFIX}/cases.json",
    f"{SUITE_PREFIX}/authoring/generate_vectors.py",
    f"{SUITE_PREFIX}/authoring/generate_suite_metadata.py",
    f"{SUITE_PREFIX}/authoring/retain_results.py",
    f"{SUITE_PREFIX}/python/runner.py",
    f"{SUITE_PREFIX}/python/dependency-lock.json",
    f"{SUITE_PREFIX}/python/source-manifest.json",
    f"{SUITE_PREFIX}/node/runner.mjs",
    f"{SUITE_PREFIX}/node/package.json",
    f"{SUITE_PREFIX}/node/package-lock.json",
    f"{SUITE_PREFIX}/node/source-manifest.json",
    f"{SUITE_PREFIX}/results/python-jcs-result.json",
    f"{SUITE_PREFIX}/results/node-jcs-result.json",
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


class FrameRefusal(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def frame_refuse(code: str) -> None:
    raise FrameRefusal(code)


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def compact_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


class RepositoryView:
    def __init__(self, overlay: dict[str, bytes] | None = None) -> None:
        self.overlay = overlay or {}

    def read_bytes(self, relative: str) -> bytes:
        if relative in self.overlay:
            return self.overlay[relative]
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            refuse(
                "corpus_census_mismatch",
                f"{relative}: not a regular non-symlink repository file",
            )
        return path.read_bytes()

    def parse(self, relative: str) -> Any:
        try:
            return json.loads(self.read_bytes(relative).decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            refuse("corpus_census_mismatch", f"{relative}: invalid JSON: {exc}")


# --- third-path serializer ----------------------------------------------------


def third_path_parse_integer(lexeme: str) -> int:
    if not INTEGER_RE.fullmatch(lexeme):
        frame_refuse("non_integer_number_token")
    if lexeme.startswith("-0"):
        frame_refuse("lexical_negative_zero")
    value = int(lexeme)
    if not MIN_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER:
        frame_refuse("integer_outside_safe_range")
    return value


def third_path_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            frame_refuse("duplicate_decoded_member_name")
        seen[key] = value
    return seen


def third_path_scan(value: Any) -> None:
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
            third_path_scan(key)
            third_path_scan(child)
    elif isinstance(value, list):
        for child in value:
            third_path_scan(child)


def third_path_escape(value: str) -> str:
    out = ['"']
    for character in value:
        code_point = ord(character)
        if character == '"':
            out.append('\\"')
        elif character == "\\":
            out.append("\\\\")
        elif code_point == 0x08:
            out.append("\\b")
        elif code_point == 0x09:
            out.append("\\t")
        elif code_point == 0x0A:
            out.append("\\n")
        elif code_point == 0x0C:
            out.append("\\f")
        elif code_point == 0x0D:
            out.append("\\r")
        elif code_point < 0x20:
            out.append(f"\\u{code_point:04x}")
        else:
            out.append(character)
    out.append('"')
    return "".join(out)


def third_path_serialize(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, str):
        return third_path_escape(value)
    if isinstance(value, list):
        return "[" + ",".join(third_path_serialize(child) for child in value) + "]"
    if isinstance(value, dict):
        ordered = sorted(value.keys(), key=lambda name: name.encode("utf-16-be"))
        return (
            "{"
            + ",".join(
                third_path_escape(name) + ":" + third_path_serialize(value[name])
                for name in ordered
            )
            + "}"
        )
    frame_refuse("malformed_json")


def third_path_frame(raw: bytes) -> dict[str, str]:
    try:
        if raw.startswith(b"\xef\xbb\xbf"):
            frame_refuse("leading_byte_order_mark")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            frame_refuse("invalid_utf8_encoding")
        decoder = json.JSONDecoder(
            object_pairs_hook=third_path_pairs,
            parse_int=third_path_parse_integer,
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
        third_path_scan(document)
        canonical = third_path_serialize(document).encode("utf-8")
        return {
            "disposition": "accepted",
            "canonical_hex": canonical.hex(),
            "canonical_sha256": sha256(canonical),
            "canonical_byte_count_decimal": str(len(canonical)),
        }
    except FrameRefusal as refusal:
        return {"disposition": "refused", "refusal_code": refusal.code}


# --- production pipeline ------------------------------------------------------


def require_decimal(value: Any, context: str) -> None:
    if not isinstance(value, str) or not DECIMAL_RE.fullmatch(value):
        refuse(
            "census_decimal_typing_violation",
            f"{context}: count is not a decimal string",
        )


def derive_and_check(view: RepositoryView) -> dict[str, Any]:
    vectors_raw = view.read_bytes(f"{SUITE_PREFIX}/vectors.json")
    vectors = view.parse(f"{SUITE_PREFIX}/vectors.json")
    if (
        vectors.get("suite_id") != SUITE_ID
        or vectors.get("answer_free") is not True
        or vectors.get("expected_outcomes_included") is not False
        or vectors.get("frame_encoding") != "raw_input_bytes_lowercase_hex"
    ):
        refuse("corpus_census_mismatch", "vectors identity flags differ")
    frames = vectors.get("frames")
    require_decimal(vectors.get("frame_count_decimal"), "vectors.frame_count")
    if not isinstance(frames, list) or vectors.get("frame_count_decimal") != str(
        len(frames)
    ):
        refuse("corpus_census_mismatch", "vectors frame census differs")
    identifiers = [frame.get("frame_id") for frame in frames]
    if len(set(identifiers)) != len(identifiers):
        refuse("corpus_census_mismatch", "duplicate frame identifiers")

    derived_rows = []
    for frame in frames:
        frame_id = frame.get("frame_id")
        raw_hex = frame.get("raw_hex")
        if not isinstance(frame_id, str) or not isinstance(raw_hex, str):
            refuse("corpus_census_mismatch", "malformed vector frame")
        try:
            raw = bytes.fromhex(raw_hex)
        except ValueError:
            refuse("corpus_census_mismatch", f"{frame_id}: invalid raw_hex")
        derived_rows.append({"frame_id": frame_id, **third_path_frame(raw)})
    derived_by_id = {row["frame_id"]: row for row in derived_rows}
    accepted = sum(1 for row in derived_rows if row["disposition"] == "accepted")
    refused_count = len(derived_rows) - accepted

    cases = view.parse(f"{SUITE_PREFIX}/cases.json")
    if (
        cases.get("suite_id") != SUITE_ID
        or cases.get("private_expectation_file") is not True
    ):
        refuse("corpus_census_mismatch", "case expectation identity differs")
    if cases.get("consumable_by_implementations") is not False:
        refuse(
            "source_separation_violation",
            "case expectations declare themselves consumable by implementations",
        )
    expectations = cases.get("expectations")
    if not isinstance(expectations, list) or [
        row.get("frame_id") for row in expectations
    ] != identifiers:
        refuse("corpus_census_mismatch", "expectation census differs from vectors")
    for row in expectations:
        derived = derived_by_id[row["frame_id"]]
        if row.get("expected_disposition") != derived["disposition"]:
            refuse(
                "expectation_disposition_mismatch",
                f"{row['frame_id']}: expected {row.get('expected_disposition')}, "
                f"derived {derived['disposition']}",
            )
        if derived["disposition"] == "refused":
            code = row.get("expected_refusal_code")
            if code not in FRAME_REFUSAL_CODES or code != derived["refusal_code"]:
                refuse(
                    "expectation_disposition_mismatch",
                    f"{row['frame_id']}: expected code {code}, derived "
                    f"{derived['refusal_code']}",
                )
    for key, expected in (
        ("frame_count_decimal", str(len(derived_rows))),
        ("accepted_count_decimal", str(accepted)),
        ("refused_count_decimal", str(refused_count)),
    ):
        require_decimal(cases.get(key), f"cases.{key}")
        if cases.get(key) != expected:
            refuse("corpus_census_mismatch", f"cases {key} differs from derivation")
    return {
        "vectors_raw": vectors_raw,
        "derived_rows": derived_rows,
        "accepted": accepted,
        "refused": refused_count,
    }


def census_validate(view: RepositoryView, derivation: dict[str, Any]) -> None:
    manifest = view.parse(f"{SUITE_PREFIX}/manifest.json")
    census = manifest.get("census", {})
    for key, expected in (
        ("frame_count_decimal", str(len(derivation["derived_rows"]))),
        ("accepted_count_decimal", str(derivation["accepted"])),
        ("refused_count_decimal", str(derivation["refused"])),
        ("source_separated_implementation_count_decimal", "2"),
        ("gate_known_bad_count_decimal", str(len(KNOWN_BADS))),
    ):
        require_decimal(census.get(key), f"manifest.census.{key}")
        if census.get(key) != expected:
            refuse("corpus_census_mismatch", f"manifest census {key} differs")
    for claim, value in manifest.get("claim_boundary", {}).items():
        if value is not False:
            refuse(
                "authority_nonclaim_violation",
                f"manifest claim boundary flips nonclaim {claim}",
            )
    declared_codes = manifest.get("suite_refusal_codes")
    if declared_codes != list(SUITE_REFUSAL_CODES):
        refuse(
            "corpus_census_mismatch",
            "manifest suite refusal-code vocabulary differs",
        )


def results_validate(view: RepositoryView, derivation: dict[str, Any]) -> None:
    results: dict[str, tuple[bytes, Any]] = {}
    for role in ("python", "node"):
        relative = f"{SUITE_PREFIX}/results/{role}-jcs-result.json"
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        if (
            document.get("artifact_class") != "prq_002g_jcs_conformance_result"
            or document.get("suite_id") != SUITE_ID
            or document.get("implementation_role") != role
        ):
            refuse(
                "source_separation_violation",
                f"{relative}: implementation identity differs from its role",
            )
        expected_id = (
            "python-stdlib-jcs-serializer.0001"
            if role == "python"
            else "nodejs-native-jcs-serializer.0001"
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
    binding = projection.get("vectors_binding", {})
    if binding.get("raw_sha256") != sha256(derivation["vectors_raw"]):
        refuse(
            "execution_binding_mismatch",
            "retained projection does not bind the exact vector bytes",
        )
    census = projection.get("census", {})
    for key, expected in (
        ("accepted_count_decimal", str(derivation["accepted"])),
        ("refused_count_decimal", str(derivation["refused"])),
    ):
        require_decimal(census.get(key), f"projection.census.{key}")
        if census.get(key) != expected:
            refuse(
                "retained_projection_mismatch",
                f"retained projection census {key} differs from derivation",
            )
    retained_frames = projection.get("frames")
    if compact_bytes(retained_frames) != compact_bytes(derivation["derived_rows"]):
        refuse(
            "retained_projection_mismatch",
            "retained frame rows differ from the third-path derivation",
        )
    boundary = projection.get("claim_boundary", {})
    if boundary.get("profile_bounded_integer_scope_only") is not True:
        refuse(
            "authority_nonclaim_violation",
            "retained projection widens the profile-bounded number scope",
        )
    for claim in (
        "general_binary64_serialization_proven",
        "product_digest_computed",
        "profile_issued",
        "gate_a_complete",
        "publication_authorized",
    ):
        if boundary.get(claim) is not False:
            refuse(
                "authority_nonclaim_violation",
                f"retained projection flips nonclaim {claim}",
            )
    for role in ("python", "node"):
        source_manifest = view.parse(f"{SUITE_PREFIX}/{role}/source-manifest.json")
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
        relative = f"{SUITE_PREFIX}/results/{role}-execution-receipt.json"
        receipt = view.parse(relative)
        if (
            receipt.get("artifact_class")
            != "prq_002g_jcs_conformance_execution_receipt"
            or receipt.get("suite_id") != SUITE_ID
            or receipt.get("self_attested_byte_consistency_record") is not True
            or receipt.get("independently_witnessed_process_evidence") is not False
        ):
            refuse(
                "execution_binding_mismatch",
                f"{relative}: receipt identity or attestation class differs",
            )
        for binding_key, bound_relative in (
            ("source_manifest_binding", f"{SUITE_PREFIX}/{role}/source-manifest.json"),
            (
                "runner_binding",
                f"{SUITE_PREFIX}/python/runner.py"
                if role == "python"
                else f"{SUITE_PREFIX}/node/runner.mjs",
            ),
            ("vectors_binding", f"{SUITE_PREFIX}/vectors.json"),
            ("result_binding", f"{SUITE_PREFIX}/results/{role}-jcs-result.json"),
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
        != "prq_002g_jcs_conformance_comparison_receipt"
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
        ("suite_manifest_binding", f"{SUITE_PREFIX}/manifest.json"),
        ("vectors_binding", f"{SUITE_PREFIX}/vectors.json"),
        ("case_expectation_binding", f"{SUITE_PREFIX}/cases.json"),
        ("validator_binding", "scripts/validate_profile_0_3_jcs_conformance.py"),
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
                f"{SUITE_PREFIX}/results/python-jcs-result.json",
                f"{SUITE_PREFIX}/results/node-jcs-result.json",
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


def run_static(view: RepositoryView) -> dict[str, Any]:
    derivation = derive_and_check(view)
    census_validate(view, derivation)
    results_validate(view, derivation)
    return derivation


# --- known-bad corpus ---------------------------------------------------------


def mutate_bytes(relative: str, old: bytes, new: bytes) -> dict[str, bytes]:
    raw = (ROOT / relative).read_bytes()
    if raw.count(old) < 1:
        raise AssertionError(f"known-bad anchor missing in {relative}: {old[:60]!r}")
    return {relative: raw.replace(old, new, 1)}


def mutate_json(relative: str, transform: Callable[[Any], Any]) -> dict[str, bytes]:
    document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    document = transform(document) or document
    raw = (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")
    return {relative: raw}


VECTORS = f"{SUITE_PREFIX}/vectors.json"
CASES = f"{SUITE_PREFIX}/cases.json"
MANIFEST = f"{SUITE_PREFIX}/manifest.json"
PY_RESULT = f"{SUITE_PREFIX}/results/python-jcs-result.json"
ND_RESULT = f"{SUITE_PREFIX}/results/node-jcs-result.json"
PY_RECEIPT = f"{SUITE_PREFIX}/results/python-execution-receipt.json"
COMPARISON = f"{SUITE_PREFIX}/results/comparison-receipt.json"
PY_SOURCE_MANIFEST = f"{SUITE_PREFIX}/python/source-manifest.json"


def _flip_digest(digest: str) -> str:
    return digest[:-1] + ("0" if digest[-1] != "0" else "1")


def _kb_vector_frame_drop() -> dict[str, bytes]:
    return mutate_json(VECTORS, lambda d: (d["frames"].pop(), d)[1])


def _kb_vector_frame_duplicate() -> dict[str, bytes]:
    return mutate_json(
        VECTORS, lambda d: (d["frames"].append(dict(d["frames"][0])), d)[1]
    )


def _kb_vector_raw_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for frame in document["frames"]:
            if frame["frame_id"] == "integer-zero":
                frame["raw_hex"] = "312e30"  # "1.0"
        return document

    return mutate_json(VECTORS, transform)


def _kb_vector_answer_flag_flip() -> dict[str, bytes]:
    return mutate_bytes(
        VECTORS, b'"answer_free": true', b'"answer_free": false'
    )


def _kb_cases_count_tamper() -> dict[str, bytes]:
    document = json.loads((ROOT / CASES).read_text(encoding="utf-8"))
    count = document["frame_count_decimal"]
    return mutate_bytes(
        CASES,
        f'"frame_count_decimal": "{count}"'.encode(),
        f'"frame_count_decimal": "{int(count) + 1}"'.encode(),
    )


def _kb_cases_disposition_swap() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'{\n   "frame_id": "empty-object",\n   "expected_disposition": "accepted"\n  }',
        b'{\n   "frame_id": "empty-object",\n   "expected_disposition": "refused",\n   "expected_refusal_code": "malformed_json"\n  }',
    )


def _kb_cases_refusal_code_swap() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'"expected_refusal_code": "lexical_negative_zero"',
        b'"expected_refusal_code": "malformed_json"',
    )


def _kb_cases_consumable_flip() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'"consumable_by_implementations": false',
        b'"consumable_by_implementations": true',
    )


def _kb_manifest_census_tamper() -> dict[str, bytes]:
    return mutate_bytes(
        MANIFEST, b'"frame_count_decimal": "61"', b'"frame_count_decimal": "60"'
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


def coherent_result_mutation(transform: Callable[[Any], Any]) -> dict[str, bytes]:
    """Mutate BOTH retained results identically while re-signing each
    projection digest, so the forgery is internally coherent, survives the
    cross-implementation byte-equality gate, and the deeper content guards —
    not the self-binding or comparison checks — must catch it."""
    overlay: dict[str, bytes] = {}
    for relative in (PY_RESULT, ND_RESULT):
        document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        document = transform(document) or document
        document["projection_sha256"] = sha256(
            compact_bytes(document["projection"])
        )
        overlay[relative] = compact_bytes(document)
    return overlay


def _kb_result_canonical_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["frame_id"] == "empty-object":
                row["canonical_hex"] = "7b207d"  # "{ }" — non-canonical
        return document

    return coherent_result_mutation(transform)


def _kb_result_ordering_downgrade() -> dict[str, bytes]:
    # Rewrite the discriminator frame's canonical output into Unicode
    # code-point member order — exactly what a naive sort would emit.
    wrong = '{"":1,"\U0001f600":2}'.encode("utf-8")

    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["frame_id"] == "utf16-unit-order-discriminator":
                row["canonical_hex"] = wrong.hex()
                row["canonical_sha256"] = sha256(wrong)
                row["canonical_byte_count_decimal"] = str(len(wrong))
        return document

    return coherent_result_mutation(transform)


def _kb_result_refusal_code_swap() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["frame_id"] == "negative-zero-refuses":
                row["refusal_code"] = "malformed_json"
        return document

    return coherent_result_mutation(transform)


def _kb_result_role_swap() -> dict[str, bytes]:
    return mutate_bytes(
        PY_RESULT, b'"implementation_role":"python"', b'"implementation_role":"node"'
    )


def _kb_result_copy_across() -> dict[str, bytes]:
    return {ND_RESULT: (ROOT / PY_RESULT).read_bytes()}


def _kb_result_sha_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection_sha256"] = _flip_digest(document["projection_sha256"])
        return document

    return mutate_json(PY_RESULT, transform)


def _kb_result_scope_flip() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["claim_boundary"][
            "general_binary64_serialization_proven"
        ] = True
        return document

    return coherent_result_mutation(transform)


def _kb_result_census_int_smuggle() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["census"]["accepted_count_decimal"] = 28
        return document

    return coherent_result_mutation(transform)


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


def _kb_receipt_result_binding_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["result_binding"]["raw_sha256"] = _flip_digest(
            document["result_binding"]["raw_sha256"]
        )
        return document

    return mutate_json(PY_RECEIPT, transform)


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
        document["projection_sha256"] = _flip_digest(document["projection_sha256"])
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
    ("vector-frame-drop", "corpus", "corpus_census_mismatch", _kb_vector_frame_drop),
    ("vector-frame-duplicate", "corpus", "corpus_census_mismatch", _kb_vector_frame_duplicate),
    ("vector-raw-tamper", "corpus", "expectation_disposition_mismatch", _kb_vector_raw_tamper),
    ("vector-answer-flag-flip", "corpus", "corpus_census_mismatch", _kb_vector_answer_flag_flip),
    ("cases-count-tamper", "corpus", "corpus_census_mismatch", _kb_cases_count_tamper),
    ("cases-disposition-swap", "corpus", "expectation_disposition_mismatch", _kb_cases_disposition_swap),
    ("cases-refusal-code-swap", "corpus", "expectation_disposition_mismatch", _kb_cases_refusal_code_swap),
    ("cases-consumable-flip", "corpus", "source_separation_violation", _kb_cases_consumable_flip),
    ("manifest-census-tamper", "census", "corpus_census_mismatch", _kb_manifest_census_tamper),
    ("manifest-known-bad-census", "census", "corpus_census_mismatch", _kb_manifest_known_bad_census),
    ("manifest-authority-flip", "census", "authority_nonclaim_violation", _kb_manifest_authority_flip),
    ("result-canonical-tamper", "results", "retained_projection_mismatch", _kb_result_canonical_tamper),
    ("result-ordering-downgrade", "results", "retained_projection_mismatch", _kb_result_ordering_downgrade),
    ("result-refusal-code-swap", "results", "retained_projection_mismatch", _kb_result_refusal_code_swap),
    ("result-role-swap", "results", "source_separation_violation", _kb_result_role_swap),
    ("result-copy-across", "results", "source_separation_violation", _kb_result_copy_across),
    ("result-sha-tamper", "results", "execution_binding_mismatch", _kb_result_sha_tamper),
    ("result-scope-flip", "results", "authority_nonclaim_violation", _kb_result_scope_flip),
    ("result-census-int-smuggle", "results", "census_decimal_typing_violation", _kb_result_census_int_smuggle),
    ("receipt-source-binding-tamper", "results", "execution_binding_mismatch", _kb_receipt_source_binding_tamper),
    ("receipt-attestation-flip", "results", "execution_binding_mismatch", _kb_receipt_attestation_flip),
    ("receipt-result-binding-tamper", "results", "execution_binding_mismatch", _kb_receipt_result_binding_tamper),
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
                "--vectors",
                (SUITE / "vectors.json").as_posix(),
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
        retained = (SUITE / f"results/{role}-jcs-result.json").read_bytes()
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

    for relative in RETAINED_SUITE_PATHS:
        target = ROOT / relative
        if target.is_symlink() or not target.is_file():
            print(f"PRQ-002G missing or non-regular retained path: {relative}")
            return 1
    try:
        derivation = run_static(RepositoryView())
    except Refusal as refusal:
        print(f"PRQ-002G REFUSED [{refusal.code}]: {refusal.detail}")
        return 1
    if run_known_bads():
        return 1
    if arguments.recompute_all:
        if not arguments.python_executable or not arguments.node_executable:
            print("--recompute-all requires --python-executable and --node-executable")
            return 1
        errors = recompute_all(arguments.python_executable, arguments.node_executable)
        if errors:
            for error in errors:
                print(f"PRQ-002G RECOMPUTE FAILURE: {error}")
            return 1
    print(
        "PRQ-002G profile-bounded JCS conformance retained evidence passed: "
        f"frames={len(derivation['derived_rows'])} "
        f"(accepted={derivation['accepted']}, refused={derivation['refused']}), "
        f"known_bads={len(KNOWN_BADS)}; "
        "scope=profile_bounded_integer_tokens_only; "
        "general_binary64=false, product_digest=false, issuance=false, "
        "gate_a=false, authority=false"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
