"""Deterministically generate the PRQ-002I resolution universe manifest.

The universe is declared by explicit rules, never by verification-time
directory discovery: every retained schema under `schemas/` (sorted), the
canonicalization candidate records and raw-number contract under
`architecture/`, the nine frozen structural-nonidentity fixtures, and the
retained manifests, source manifests, results, and receipts of the
PRQ-002F, PRQ-002G, and PRQ-002H suites. `--check` verifies the retained
manifest equals deterministic regeneration without writing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
ROOT = SUITE.parent.parent
SUITE_ID = "prq-002i-offline-resolution.0001"

ARCHITECTURE_RECORDS = (
    "architecture/canonicalization-profile-core-0.2-candidate.json",
    "architecture/canonicalization-profile-candidate-evidence.json",
    "architecture/canonicalization-profile-0.1-to-0.2-migration-candidate.json",
    "architecture/canonicalization-profile-core-0.3-candidate.json",
    "architecture/canonicalization-profile-0.3-candidate-evidence.json",
    "architecture/canonicalization-profile-0.2-to-0.3-migration-candidate.json",
    "architecture/canonicalization-raw-number-token-contract-v1-candidate.json",
)
FIXTURE_DIR = "tests/architecture-schema/fixtures/prq-002e-structural-nonidentity"
FIXTURE_SLUGS = (
    "schema-resource-record-v0-2",
    "aggregate-state-subject-record-v0-2",
    "reducer-contract-record-v0-2",
    "event-contract-record-v0-2",
    "ordered-member-map-commitment-v0-2",
    "schema-registry-v0-9",
    "aggregate-state-subject-registry-v0-8",
    "reducer-registry-v0-8",
    "event-contract-registry-v0-8",
)
SUITE_PREFIXES = (
    "tests/profile-0-3-numeric-trace-conformance",
    "tests/profile-0-3-jcs-conformance",
    "tests/profile-0-3-product-domain-frames",
)
SUITE_JSON_MEMBERS = {
    "tests/profile-0-3-numeric-trace-conformance": (
        "manifest.json",
        "input-manifest.json",
        "cases.json",
        "python/dependency-lock.json",
        "python/source-manifest.json",
        "node/package.json",
        "node/package-lock.json",
        "node/source-manifest.json",
        "results/python-trace-result.json",
        "results/node-trace-result.json",
        "results/python-execution-receipt.json",
        "results/node-execution-receipt.json",
        "results/comparison-receipt.json",
    ),
    "tests/profile-0-3-jcs-conformance": (
        "manifest.json",
        "vectors.json",
        "cases.json",
        "python/dependency-lock.json",
        "python/source-manifest.json",
        "node/package.json",
        "node/package-lock.json",
        "node/source-manifest.json",
        "results/python-jcs-result.json",
        "results/node-jcs-result.json",
        "results/python-execution-receipt.json",
        "results/node-execution-receipt.json",
        "results/comparison-receipt.json",
    ),
    "tests/profile-0-3-product-domain-frames": (
        "manifest.json",
        "vectors.json",
        "cases.json",
        "python/dependency-lock.json",
        "python/source-manifest.json",
        "node/package.json",
        "node/package-lock.json",
        "node/source-manifest.json",
        "results/python-frames-result.json",
        "results/node-frames-result.json",
        "results/python-execution-receipt.json",
        "results/node-execution-receipt.json",
        "results/comparison-receipt.json",
    ),
}
NAMED_RESIDUE_IDENTITIES = (
    "command-contract-registry:0.1.0",
    "command-receipt:0.3.0",
    "work-contract:0.1.0",
    "command-envelope:0.4.0",
)


def members():
    rows = []
    schema_dir = ROOT / "schemas"
    for path in sorted(schema_dir.glob("*.json")):
        rows.append({"role": "schema", "repository_path": f"schemas/{path.name}"})
    for relative in ARCHITECTURE_RECORDS:
        rows.append({"role": "candidate_record", "repository_path": relative})
    for slug in FIXTURE_SLUGS:
        rows.append(
            {
                "role": "structural_nonidentity_fixture",
                "repository_path": (
                    f"{FIXTURE_DIR}/prq-002e-{slug}.structural-nonidentity.json"
                ),
            }
        )
    for prefix in SUITE_PREFIXES:
        for member in SUITE_JSON_MEMBERS[prefix]:
            rows.append(
                {"role": "suite_artifact", "repository_path": f"{prefix}/{member}"}
            )
    paths = [row["repository_path"] for row in rows]
    if len(set(paths)) != len(paths):
        raise SystemExit("duplicate universe member")
    for relative in paths:
        target = ROOT / relative
        if target.is_symlink() or not target.is_file():
            raise SystemExit(f"universe member missing or symlinked: {relative}")
    return rows


def encode(document) -> bytes:
    return (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    rows = members()
    role_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
    manifest = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002i_offline_resolution_universe",
        "suite_id": SUITE_ID,
        "answer_free": True,
        "expected_outcomes_included": False,
        "member_count_decimal": str(len(rows)),
        "role_counts_decimal": {
            role: str(count) for role, count in sorted(role_counts.items())
        },
        "members": rows,
        "named_residue_identities_outside_universe": list(
            NAMED_RESIDUE_IDENTITIES
        ),
        "verification_time_directory_discovery_allowed": False,
        "network_access_allowed": False,
        "environment_path_discovery_allowed": False,
        "authority_claim_allowed": False,
    }
    raw = encode(manifest)
    target = SUITE / "universe-manifest.json"
    if arguments.check:
        if not target.is_file() or target.read_bytes() != raw:
            print("PRQ-002I universe differs from deterministic regeneration")
            return 1
        print(f"verified PRQ-002I universe: {len(rows)} members")
        return 0
    target.write_bytes(raw)
    print(
        f"generated PRQ-002I universe: {len(rows)} members "
        + json.dumps(manifest["role_counts_decimal"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
