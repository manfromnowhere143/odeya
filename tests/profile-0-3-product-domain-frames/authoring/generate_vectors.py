"""Deterministically generate the PRQ-002H nine-domain frame corpus.

Emits the answer-free `vectors.json` — nine accepted frames that are
byte-for-byte the nine frozen structural-nonidentity fixtures, plus five
deterministically derived refusal variants per domain — and the private
expectation file `cases.json` (dispositions and refusal codes only). The
variants are: an integral-fraction spelling of the fixture's first integer
token, a lexical negative zero, an out-of-safe-range integer, an undeclared
top-level member that `additionalProperties: false` must reject, and the
removal of the governing schema's first required member. `--check` verifies
both files equal their retained bytes without writing.

No implementation may read `cases.json`. Architecture evidence only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
ROOT = SUITE.parent.parent
SUITE_ID = "prq-002h-product-domain-frames.0001"
FIXTURE_DIR = "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity"

DOMAINS = (
    ("schema_resource_record", "schema-resource-record-v0-2"),
    ("aggregate_state_subject_record", "aggregate-state-subject-record-v0-2"),
    ("reducer_contract_record", "reducer-contract-record-v0-2"),
    ("event_contract_record", "event-contract-record-v0-2"),
    ("ordered_member_map_commitment", "ordered-member-map-commitment-v0-2"),
    ("schema_registry", "schema-registry-v0-9"),
    ("aggregate_state_subject_registry", "aggregate-state-subject-registry-v0-8"),
    ("reducer_registry", "reducer-registry-v0-8"),
    ("event_contract_registry", "event-contract-registry-v0-8"),
)
INTEGER_TOKEN = re.compile(r'(?<=[:\s\[,])(-?\d+)(?=[,\s}\]])')


def fixture_path(slug: str) -> Path:
    return ROOT / FIXTURE_DIR / f"prq-002e-{slug}.structural-nonidentity.json"


def schema_path(slug: str) -> Path:
    return ROOT / "schemas" / f"{slug}.schema.json"


def compact(document) -> str:
    return json.dumps(document, ensure_ascii=False, separators=(",", ":"))


def replace_first_integer(text: str, replacement: str) -> str:
    match = INTEGER_TOKEN.search(text)
    if match is None:
        raise SystemExit("fixture has no integer token to mutate")
    return text[: match.start()] + replacement + text[match.end() :]


def corpus():
    frames = []
    expectations = []

    def add(frame_id: str, domain: str, raw: bytes, disposition: str, code=None):
        frames.append({"frame_id": frame_id, "domain": domain, "raw_hex": raw.hex()})
        expectation = {"frame_id": frame_id, "expected_disposition": disposition}
        if code is not None:
            expectation["expected_refusal_code"] = code
        expectations.append(expectation)

    for domain, slug in DOMAINS:
        raw = fixture_path(slug).read_bytes()
        document = json.loads(raw)
        text = compact(document)
        add(f"{domain}-governed-fixture", domain, raw, "accepted")
        add(
            f"{domain}-integral-float-refuses",
            domain,
            replace_first_integer(text, "1.0").encode("utf-8"),
            "refused",
            "non_integer_number_token",
        )
        add(
            f"{domain}-negative-zero-refuses",
            domain,
            replace_first_integer(text, "-0").encode("utf-8"),
            "refused",
            "lexical_negative_zero",
        )
        add(
            f"{domain}-unsafe-range-refuses",
            domain,
            replace_first_integer(text, "9007199254740992").encode("utf-8"),
            "refused",
            "integer_outside_safe_range",
        )
        undeclared = dict(document)
        undeclared["zz_undeclared_member"] = True
        add(
            f"{domain}-undeclared-member-refuses",
            domain,
            compact(undeclared).encode("utf-8"),
            "refused",
            "record_schema_validation_failed",
        )
        schema = json.loads(schema_path(slug).read_bytes())
        required = schema.get("required")
        if not isinstance(required, list) or not required:
            raise SystemExit(f"{slug}: governing schema has no required members")
        first_required = required[0]
        if first_required not in document:
            raise SystemExit(f"{slug}: fixture lacks required member {first_required}")
        removed = {k: v for k, v in document.items() if k != first_required}
        add(
            f"{domain}-missing-required-refuses",
            domain,
            compact(removed).encode("utf-8"),
            "refused",
            "record_schema_validation_failed",
        )
    identifiers = [frame["frame_id"] for frame in frames]
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
    accepted = sum(
        1 for row in expectations if row["expected_disposition"] == "accepted"
    )
    refused = len(expectations) - accepted
    vectors = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002h_product_domain_frame_vectors",
        "suite_id": SUITE_ID,
        "answer_free": True,
        "expected_outcomes_included": False,
        "frame_count_decimal": str(len(frames)),
        "domain_count_decimal": str(len(DOMAINS)),
        "frame_encoding": "raw_input_bytes_lowercase_hex",
        "frames": frames,
    }
    cases = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002h_product_domain_frame_expectations",
        "suite_id": SUITE_ID,
        "private_expectation_file": True,
        "consumable_by_implementations": False,
        "frame_count_decimal": str(len(frames)),
        "accepted_count_decimal": str(accepted),
        "refused_count_decimal": str(refused),
        "expectations": expectations,
    }
    outputs = {"vectors.json": encode(vectors), "cases.json": encode(cases)}
    failures = []
    for relative, raw in outputs.items():
        target = SUITE / relative
        if arguments.check:
            if not target.is_file() or target.read_bytes() != raw:
                failures.append(relative)
        else:
            target.write_bytes(raw)
    if arguments.check and failures:
        print(
            "PRQ-002H corpus differs from deterministic regeneration: "
            + ", ".join(failures)
        )
        return 1
    print(
        ("verified" if arguments.check else "generated")
        + f" PRQ-002H corpus: {len(frames)} frames"
        + f" ({accepted} accepted, {refused} refused) across {len(DOMAINS)} domains"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
