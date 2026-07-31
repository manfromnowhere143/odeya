"""Validate the PRQ-002H nine-product-domain frame governance suite.

Dedicated parent validator in the PRQ-002D style: the two source-separated
runners are themselves the dual semantic evaluation paths, and this parent
is the binding and consistency gate. It verifies the answer-free corpus
census; byte-binds every accepted frame to its retained frozen
structural-nonidentity fixture and its governing schema digest, recomputed
from current repository bytes; cross-checks the private expectations against
both retained projections; requires the two retained projections to be
byte-identical and self-bound; verifies the execution and comparison
receipts; executes an embedded known-bad corpus in which every mutation
refuses with its declared singleton code; and supports `--recompute-all`
re-execution of both runners against the retained result bytes.

Bounded architecture evidence only: the governed instances remain structural
nonidentity fixtures; no product identity, digest, membership, issuance,
PRQ-002 closure, Gate A acceptance, or runtime/publication authority follows.
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
SUITE_PREFIX = "tests/profile-0-3-product-domain-frames"
SUITE = ROOT / SUITE_PREFIX
SUITE_ID = "prq-002h-product-domain-frames.0001"
FIXTURE_DIR = "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity"
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")
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
SCHEMA_PATH_BY_ID = {
    governing_id: f"schemas/{slug}.schema.json"
    for _, slug, governing_id in DOMAIN_ROWS
}
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
        "record_schema_validation_failed",
        "unclassified_instance_numeric_position",
        "multiply_classified_instance_position",
        "out_of_cohort_reference",
        "closed_vocabulary_violation",
        "fixture_byte_binding_mismatch",
    }
)
SUITE_REFUSAL_CODES = (
    "authority_nonclaim_violation",
    "census_decimal_typing_violation",
    "corpus_census_mismatch",
    "execution_binding_mismatch",
    "expectation_disposition_mismatch",
    "fixture_byte_binding_mismatch",
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
    f"{SUITE_PREFIX}/results/python-frames-result.json",
    f"{SUITE_PREFIX}/results/node-frames-result.json",
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


def require_decimal(value: Any, context: str) -> None:
    if not isinstance(value, str) or not DECIMAL_RE.fullmatch(value):
        refuse(
            "census_decimal_typing_violation",
            f"{context}: count is not a decimal string",
        )


def corpus_validate(view: RepositoryView) -> dict[str, Any]:
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
    require_decimal(vectors.get("domain_count_decimal"), "vectors.domain_count")
    if (
        not isinstance(frames, list)
        or vectors.get("frame_count_decimal") != str(len(frames))
        or vectors.get("domain_count_decimal") != str(len(DOMAIN_ROWS))
    ):
        refuse("corpus_census_mismatch", "vectors frame census differs")
    identifiers = [frame.get("frame_id") for frame in frames]
    if len(set(identifiers)) != len(identifiers):
        refuse("corpus_census_mismatch", "duplicate frame identifiers")
    known_domains = {row[0] for row in DOMAIN_ROWS}
    frame_bytes: dict[str, bytes] = {}
    frame_domains: dict[str, str] = {}
    for frame in frames:
        frame_id = frame.get("frame_id")
        domain = frame.get("domain")
        raw_hex = frame.get("raw_hex")
        if (
            not isinstance(frame_id, str)
            or domain not in known_domains
            or not isinstance(raw_hex, str)
        ):
            refuse("corpus_census_mismatch", "malformed vector frame")
        try:
            frame_bytes[frame_id] = bytes.fromhex(raw_hex)
        except ValueError:
            refuse("corpus_census_mismatch", f"{frame_id}: invalid raw_hex")
        frame_domains[frame_id] = domain

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
    accepted_ids = [
        row["frame_id"]
        for row in expectations
        if row.get("expected_disposition") == "accepted"
    ]
    refused_ids = [
        row["frame_id"]
        for row in expectations
        if row.get("expected_disposition") == "refused"
    ]
    for key, expected in (
        ("frame_count_decimal", str(len(expectations))),
        ("accepted_count_decimal", str(len(accepted_ids))),
        ("refused_count_decimal", str(len(refused_ids))),
    ):
        require_decimal(cases.get(key), f"cases.{key}")
        if cases.get(key) != expected:
            refuse("corpus_census_mismatch", f"cases {key} differs")
    for row in expectations:
        if row.get("expected_disposition") == "refused" and (
            row.get("expected_refusal_code") not in FRAME_REFUSAL_CODES
        ):
            refuse(
                "expectation_disposition_mismatch",
                f"{row.get('frame_id')}: undeclared refusal code "
                f"{row.get('expected_refusal_code')!r}",
            )
    if len(accepted_ids) != len(DOMAIN_ROWS) or sorted(
        frame_domains[frame_id] for frame_id in accepted_ids
    ) != sorted(row[0] for row in DOMAIN_ROWS):
        refuse(
            "corpus_census_mismatch",
            "accepted census is not exactly one frame per domain",
        )
    # Every accepted frame must be byte-for-byte its domain's retained frozen
    # fixture, recomputed from current repository bytes.
    fixture_raw: dict[str, bytes] = {}
    for domain, slug, _ in DOMAIN_ROWS:
        fixture_raw[domain] = view.read_bytes(
            f"{FIXTURE_DIR}/prq-002e-{slug}.structural-nonidentity.json"
        )
    for frame_id in accepted_ids:
        domain = frame_domains[frame_id]
        if frame_bytes[frame_id] != fixture_raw[domain]:
            refuse(
                "fixture_byte_binding_mismatch",
                f"{frame_id}: accepted frame bytes differ from the retained "
                f"{domain} fixture",
            )
    return {
        "vectors_raw": vectors_raw,
        "expectations": expectations,
        "frame_domains": frame_domains,
        "fixture_raw": fixture_raw,
        "accepted_ids": set(accepted_ids),
    }


def results_validate(view: RepositoryView, corpus: dict[str, Any]) -> None:
    results: dict[str, tuple[bytes, Any]] = {}
    for role in ("python", "node"):
        relative = f"{SUITE_PREFIX}/results/{role}-frames-result.json"
        raw = view.read_bytes(relative)
        document = view.parse(relative)
        if (
            document.get("artifact_class") != "prq_002h_product_domain_frame_result"
            or document.get("suite_id") != SUITE_ID
            or document.get("implementation_role") != role
        ):
            refuse(
                "source_separation_violation",
                f"{relative}: implementation identity differs from its role",
            )
        expected_id = (
            "python-stdlib-domain-governor.0001"
            if role == "python"
            else "nodejs-native-domain-governor.0001"
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
    if binding.get("raw_sha256") != sha256(corpus["vectors_raw"]):
        refuse(
            "execution_binding_mismatch",
            "retained projection does not bind the exact vector bytes",
        )
    rows = projection.get("frames")
    expectations = corpus["expectations"]
    if not isinstance(rows, list) or [row.get("frame_id") for row in rows] != [
        row["frame_id"] for row in expectations
    ]:
        refuse(
            "retained_projection_mismatch",
            "retained frame census differs from the corpus",
        )
    accepted = 0
    refused_count = 0
    for retained, expected in zip(rows, expectations):
        frame_id = expected["frame_id"]
        if retained.get("domain") != corpus["frame_domains"][frame_id]:
            refuse(
                "retained_projection_mismatch",
                f"{frame_id}: retained domain differs from the corpus",
            )
        if retained.get("disposition") != expected["expected_disposition"]:
            refuse(
                "expectation_disposition_mismatch",
                f"{frame_id}: retained disposition "
                f"{retained.get('disposition')!r} differs from expectation",
            )
        if expected["expected_disposition"] == "refused":
            refused_count += 1
            if retained.get("refusal_code") != expected["expected_refusal_code"]:
                refuse(
                    "expectation_disposition_mismatch",
                    f"{frame_id}: retained code {retained.get('refusal_code')!r} "
                    f"differs from expected "
                    f"{expected['expected_refusal_code']!r}",
                )
        else:
            accepted += 1
            domain = corpus["frame_domains"][frame_id]
            fixture = corpus["fixture_raw"][domain]
            governing_id = next(
                row[2] for row in DOMAIN_ROWS if row[0] == domain
            )
            schema_raw = view.read_bytes(SCHEMA_PATH_BY_ID[governing_id])
            require_decimal(
                retained.get("byte_count_decimal"), f"{frame_id}.byte_count"
            )
            require_decimal(
                retained.get("token_count_decimal"), f"{frame_id}.token_count"
            )
            if (
                retained.get("raw_sha256") != sha256(fixture)
                or retained.get("byte_count_decimal") != str(len(fixture))
                or retained.get("governing_schema_id") != governing_id
                or retained.get("governing_schema_raw_digest")
                != sha256(schema_raw)
            ):
                refuse(
                    "fixture_byte_binding_mismatch",
                    f"{frame_id}: retained governance bindings differ from "
                    "recomputed repository bytes",
                )
            tokens = retained.get("tokens")
            if not isinstance(tokens, list) or retained.get(
                "token_count_decimal"
            ) != str(len(tokens)):
                refuse(
                    "retained_projection_mismatch",
                    f"{frame_id}: token census differs",
                )
            pointers = [token.get("instance_pointer") for token in tokens]
            if len(set(pointers)) != len(pointers):
                refuse(
                    "retained_projection_mismatch",
                    f"{frame_id}: duplicate instance pointer in trace",
                )
            for token in tokens:
                classification = token.get("classification", {})
                if not classification.get("applicable_assertions"):
                    refuse(
                        "retained_projection_mismatch",
                        f"{frame_id}: trace token lacks applicable assertions",
                    )
                if classification.get("final_rule") not in (
                    "recursive_integer_valued_const_leaf",
                    "integer_type",
                ):
                    refuse(
                        "retained_projection_mismatch",
                        f"{frame_id}: trace token carries an undeclared rule",
                    )
    census = projection.get("census", {})
    for key, expected_value in (
        ("domain_count_decimal", str(len(DOMAIN_ROWS))),
        ("accepted_count_decimal", str(accepted)),
        ("refused_count_decimal", str(refused_count)),
    ):
        require_decimal(census.get(key), f"projection.census.{key}")
        if census.get(key) != expected_value:
            refuse(
                "retained_projection_mismatch",
                f"retained projection census {key} differs",
            )
    boundary = projection.get("claim_boundary", {})
    if (
        boundary.get(
            "governed_instances_are_structural_nonidentity_fixtures_only"
        )
        is not True
    ):
        refuse(
            "authority_nonclaim_violation",
            "retained projection widens the governed-instance scope",
        )
    for claim in (
        "product_identity_computed",
        "product_digest_computed",
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
            != "prq_002h_product_domain_frame_execution_receipt"
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
            ("result_binding", f"{SUITE_PREFIX}/results/{role}-frames-result.json"),
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
        != "prq_002h_product_domain_frame_comparison_receipt"
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
        (
            "validator_binding",
            "scripts/validate_profile_0_3_product_domain_frames.py",
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
                f"{SUITE_PREFIX}/results/python-frames-result.json",
                f"{SUITE_PREFIX}/results/node-frames-result.json",
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


def census_validate(view: RepositoryView, corpus: dict[str, Any]) -> None:
    manifest = view.parse(f"{SUITE_PREFIX}/manifest.json")
    census = manifest.get("census", {})
    for key, expected in (
        ("frame_count_decimal", str(len(corpus["expectations"]))),
        ("domain_count_decimal", str(len(DOMAIN_ROWS))),
        ("accepted_count_decimal", str(len(corpus["accepted_ids"]))),
        (
            "refused_count_decimal",
            str(len(corpus["expectations"]) - len(corpus["accepted_ids"])),
        ),
        ("source_separated_implementation_count_decimal", "2"),
        ("gate_known_bad_count_decimal", str(len(KNOWN_BADS))),
    ):
        require_decimal(census.get(key), f"manifest.census.{key}")
        if census.get(key) != expected:
            refuse("corpus_census_mismatch", f"manifest census {key} differs")
    if manifest.get("suite_refusal_codes") != list(SUITE_REFUSAL_CODES):
        refuse(
            "corpus_census_mismatch",
            "manifest suite refusal-code vocabulary differs",
        )
    for claim, value in manifest.get("claim_boundary", {}).items():
        if value is not False:
            refuse(
                "authority_nonclaim_violation",
                f"manifest claim boundary flips nonclaim {claim}",
            )


def run_static(view: RepositoryView) -> dict[str, Any]:
    corpus = corpus_validate(view)
    census_validate(view, corpus)
    results_validate(view, corpus)
    return corpus


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
PY_RESULT = f"{SUITE_PREFIX}/results/python-frames-result.json"
ND_RESULT = f"{SUITE_PREFIX}/results/node-frames-result.json"
PY_RECEIPT = f"{SUITE_PREFIX}/results/python-execution-receipt.json"
COMPARISON = f"{SUITE_PREFIX}/results/comparison-receipt.json"
PY_SOURCE_MANIFEST = f"{SUITE_PREFIX}/python/source-manifest.json"
COMMITMENT_FIXTURE = (
    f"{FIXTURE_DIR}/prq-002e-ordered-member-map-commitment-v0-2."
    "structural-nonidentity.json"
)


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


def _kb_vector_frame_drop() -> dict[str, bytes]:
    return mutate_json(VECTORS, lambda d: (d["frames"].pop(), d)[1])


def _kb_vector_frame_duplicate() -> dict[str, bytes]:
    return mutate_json(
        VECTORS, lambda d: (d["frames"].append(dict(d["frames"][0])), d)[1]
    )


def _kb_vector_accepted_byte_drift() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for frame in document["frames"]:
            if frame["frame_id"] == "schema_resource_record-governed-fixture":
                raw = bytes.fromhex(frame["raw_hex"])
                frame["raw_hex"] = (raw[:-2] + b" }").hex()
        return document

    return mutate_json(VECTORS, transform)


def _kb_fixture_byte_drift() -> dict[str, bytes]:
    raw = (ROOT / COMMITMENT_FIXTURE).read_bytes()
    return {COMMITMENT_FIXTURE: raw.replace(b"{", b"{ ", 1)}


def _kb_vector_domain_swap() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for frame in document["frames"]:
            if frame["frame_id"] == "schema_registry-governed-fixture":
                frame["domain"] = "reducer_registry"
        return document

    return mutate_json(VECTORS, transform)


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
        b'"frame_id": "schema_resource_record-governed-fixture",\n   "expected_disposition": "accepted"',
        b'"frame_id": "schema_resource_record-governed-fixture",\n   "expected_disposition": "refused",\n   "expected_refusal_code": "malformed_json"',
    )


def _kb_cases_refusal_code_swap() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'"expected_refusal_code": "lexical_negative_zero"',
        b'"expected_refusal_code": "malformed_json"',
    )


def _kb_cases_undeclared_code() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'"expected_refusal_code": "integer_outside_safe_range"',
        b'"expected_refusal_code": "totally_novel_code"',
    )


def _kb_cases_consumable_flip() -> dict[str, bytes]:
    return mutate_bytes(
        CASES,
        b'"consumable_by_implementations": false',
        b'"consumable_by_implementations": true',
    )


def _kb_manifest_census_tamper() -> dict[str, bytes]:
    return mutate_bytes(
        MANIFEST, b'"frame_count_decimal": "54"', b'"frame_count_decimal": "53"'
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


def _kb_result_trace_pointer_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["disposition"] == "accepted" and row["tokens"]:
                row["tokens"][0]["instance_pointer"] = "/zz_not_a_pointer"
                break
        return document

    return coherent_result_mutation(transform)


def _kb_result_rule_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["disposition"] == "accepted" and row["tokens"]:
                row["tokens"][0]["classification"]["final_rule"] = "number_type"
                break
        return document

    return coherent_result_mutation(transform)


def _kb_result_governing_digest_tamper() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["disposition"] == "accepted":
                row["governing_schema_raw_digest"] = _flip_digest(
                    row["governing_schema_raw_digest"]
                )
                break
        return document

    return coherent_result_mutation(transform)


def _kb_result_refusal_code_swap() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        for row in document["projection"]["frames"]:
            if row["frame_id"] == "schema_registry-negative-zero-refuses":
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
        document["projection"]["claim_boundary"]["product_digest_computed"] = True
        return document

    return coherent_result_mutation(transform)


def _kb_result_census_int_smuggle() -> dict[str, bytes]:
    def transform(document: Any) -> Any:
        document["projection"]["census"]["accepted_count_decimal"] = 9
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
    ("vector-accepted-byte-drift", "corpus", "fixture_byte_binding_mismatch", _kb_vector_accepted_byte_drift),
    ("fixture-byte-drift", "corpus", "fixture_byte_binding_mismatch", _kb_fixture_byte_drift),
    ("vector-domain-swap", "corpus", "corpus_census_mismatch", _kb_vector_domain_swap),
    ("cases-count-tamper", "corpus", "corpus_census_mismatch", _kb_cases_count_tamper),
    ("cases-disposition-swap", "corpus", "corpus_census_mismatch", _kb_cases_disposition_swap),
    ("cases-refusal-code-swap", "corpus", "expectation_disposition_mismatch", _kb_cases_refusal_code_swap),
    ("cases-undeclared-code", "corpus", "expectation_disposition_mismatch", _kb_cases_undeclared_code),
    ("cases-consumable-flip", "corpus", "source_separation_violation", _kb_cases_consumable_flip),
    ("manifest-census-tamper", "census", "corpus_census_mismatch", _kb_manifest_census_tamper),
    ("manifest-known-bad-census", "census", "corpus_census_mismatch", _kb_manifest_known_bad_census),
    ("manifest-authority-flip", "census", "authority_nonclaim_violation", _kb_manifest_authority_flip),
    ("result-trace-pointer-tamper", "results", "execution_binding_mismatch", _kb_result_trace_pointer_tamper),
    ("result-rule-tamper", "results", "retained_projection_mismatch", _kb_result_rule_tamper),
    ("result-governing-digest-tamper", "results", "fixture_byte_binding_mismatch", _kb_result_governing_digest_tamper),
    ("result-refusal-code-swap", "results", "expectation_disposition_mismatch", _kb_result_refusal_code_swap),
    ("result-role-swap", "results", "source_separation_violation", _kb_result_role_swap),
    ("result-copy-across", "results", "source_separation_violation", _kb_result_copy_across),
    ("result-sha-tamper", "results", "execution_binding_mismatch", _kb_result_sha_tamper),
    ("result-scope-flip", "results", "authority_nonclaim_violation", _kb_result_scope_flip),
    ("result-census-int-smuggle", "results", "census_decimal_typing_violation", _kb_result_census_int_smuggle),
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
        retained = (SUITE / f"results/{role}-frames-result.json").read_bytes()
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
            print(f"PRQ-002H missing or non-regular retained path: {relative}")
            return 1
    try:
        corpus = run_static(RepositoryView())
    except Refusal as refusal:
        print(f"PRQ-002H REFUSED [{refusal.code}]: {refusal.detail}")
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
                print(f"PRQ-002H RECOMPUTE FAILURE: {error}")
            return 1
    total = len(corpus["expectations"])
    accepted = len(corpus["accepted_ids"])
    print(
        "PRQ-002H nine-domain frame governance retained evidence passed: "
        f"domains=9, frames={total} (accepted={accepted}, refused={total - accepted}), "
        f"known_bads={len(KNOWN_BADS)}; "
        "governed_instances=structural_nonidentity_fixtures_only; "
        "identity=false, digest=false, issuance=false, gate_a=false, "
        "authority=false"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
