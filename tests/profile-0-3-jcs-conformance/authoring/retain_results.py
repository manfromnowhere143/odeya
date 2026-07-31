"""Retain the PRQ-002G dual-implementation results and receipts.

Executes the CPython and Node.js serializers with explicitly selected
executables, verifies that the two emitted projections are byte-identical,
and retains the complete observation transaction: two result documents, two
execution receipts, and the comparison receipt installed last, staged and
fsynced in a same-filesystem directory so an interruption cannot leave a
partially-valid observation graph. The execution receipts are self-attested
byte-consistency records, deliberately free of wall-clock time.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SUITE = Path(__file__).resolve().parent.parent
ROOT = SUITE.parent.parent
SUITE_ID = "prq-002g-jcs-serialization-conformance.0001"
SUITE_PREFIX = "tests/profile-0-3-jcs-conformance"
VECTORS = ROOT / SUITE_PREFIX / "vectors.json"
RESULT_PATHS = {
    "python": f"{SUITE_PREFIX}/results/python-jcs-result.json",
    "node": f"{SUITE_PREFIX}/results/node-jcs-result.json",
}
RECEIPT_PATHS = {
    "python": f"{SUITE_PREFIX}/results/python-execution-receipt.json",
    "node": f"{SUITE_PREFIX}/results/node-execution-receipt.json",
}
COMPARISON_PATH = f"{SUITE_PREFIX}/results/comparison-receipt.json"
PREDECESSOR = {
    "commit": "741b7b6283eb17a3dfac2abed92e84344f20f19d",
    "tree": "407ab1ef25d088dff82034ec183b98323843a836",
}


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def binding(relative: str) -> dict[str, str]:
    raw = (ROOT / relative).read_bytes()
    return {
        "repository_path": relative,
        "raw_sha256": sha256(raw),
        "byte_count_decimal": str(len(raw)),
    }


def encode(document: dict) -> bytes:
    return (
        json.dumps(document, indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    ).encode("utf-8")


def executable_binding(executable: Path) -> dict[str, str]:
    resolved = executable.resolve(strict=True)
    raw = resolved.read_bytes()
    return {
        "invoked_path": executable.as_posix(),
        "resolved_path": resolved.as_posix(),
        "raw_sha256": sha256(raw),
        "byte_count_decimal": str(len(raw)),
    }


def run_runner(executable: Path, runner_relative: str, source_manifest_relative: str, *, node: bool):
    before = executable_binding(executable)
    command = [
        before["invoked_path"],
        *(["--disable-proto=throw"] if node else ["-I", "-B"]),
        (ROOT / runner_relative).as_posix(),
        "--vectors",
        VECTORS.as_posix(),
        "--source-manifest",
        (ROOT / source_manifest_relative).as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env={
            "PATH": Path(before["resolved_path"]).parent.as_posix(),
            "LANG": "C",
            "LC_ALL": "C",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
        },
        capture_output=True,
        timeout=120,
        check=False,
    )
    after = executable_binding(executable)
    if before != after:
        raise SystemExit("selected executable changed during child execution")
    if completed.returncode != 0 or completed.stderr:
        raise SystemExit(
            f"runner failed: exit={completed.returncode}, "
            f"stderr={completed.stderr[:400]!r}"
        )
    document = json.loads(completed.stdout)
    if document.get("artifact_class") != "prq_002g_jcs_conformance_result":
        raise SystemExit("runner did not emit a result document")
    return completed.stdout, {
        "before": before,
        "after": after,
        "argv_repository_relative": [
            *(["--disable-proto=throw"] if node else ["-I", "-B"]),
            runner_relative,
            "--vectors",
            f"{SUITE_PREFIX}/vectors.json",
            "--source-manifest",
            source_manifest_relative,
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--python-executable", required=True)
    parser.add_argument("--node-executable", required=True)
    arguments = parser.parse_args()

    python_stdout, python_execution = run_runner(
        Path(arguments.python_executable),
        f"{SUITE_PREFIX}/python/runner.py",
        f"{SUITE_PREFIX}/python/source-manifest.json",
        node=False,
    )
    node_stdout, node_execution = run_runner(
        Path(arguments.node_executable),
        f"{SUITE_PREFIX}/node/runner.mjs",
        f"{SUITE_PREFIX}/node/source-manifest.json",
        node=True,
    )
    python_document = json.loads(python_stdout)
    node_document = json.loads(node_stdout)
    if python_document["projection_sha256"] != node_document["projection_sha256"]:
        raise SystemExit("projection digests differ between implementations")

    def receipt(role: str, execution: dict, stdout: bytes, runtime: dict) -> dict:
        return {
            "schema_version": "0.1.0",
            "artifact_class": "prq_002g_jcs_conformance_execution_receipt",
            "receipt_id": f"prq-002g-{role}-execution.0001",
            "suite_id": SUITE_ID,
            "implementation_id": (
                "python-stdlib-jcs-serializer.0001"
                if role == "python"
                else "nodejs-native-jcs-serializer.0001"
            ),
            "predecessor_checkpoint": PREDECESSOR,
            "self_attested_byte_consistency_record": True,
            "independently_witnessed_process_evidence": False,
            "wall_clock_time_retained": False,
            "source_manifest_binding": binding(
                f"{SUITE_PREFIX}/{role}/source-manifest.json"
            ),
            "runner_binding": binding(
                f"{SUITE_PREFIX}/python/runner.py"
                if role == "python"
                else f"{SUITE_PREFIX}/node/runner.mjs"
            ),
            "vectors_binding": binding(f"{SUITE_PREFIX}/vectors.json"),
            "runtime": runtime,
            "invocation_argv_repository_relative": execution[
                "argv_repository_relative"
            ],
            "executable_binding_pre": execution["before"],
            "executable_binding_post": execution["after"],
            "result_binding": {
                "repository_path": RESULT_PATHS[role],
                "raw_sha256": sha256(stdout),
                "byte_count_decimal": str(len(stdout)),
            },
            "authority_claim": False,
        }

    python_receipt_bytes = encode(
        receipt(
            "python",
            python_execution,
            python_stdout,
            {"family": "CPython", "version": "3.14.2"},
        )
    )
    node_receipt_bytes = encode(
        receipt(
            "node",
            node_execution,
            node_stdout,
            {"family": "Node.js", "version": "24.18.0"},
        )
    )
    comparison = {
        "schema_version": "0.1.0",
        "artifact_class": "prq_002g_jcs_conformance_comparison_receipt",
        "comparison_id": "prq-002g-jcs-comparison.0001",
        "suite_id": SUITE_ID,
        "predecessor_checkpoint": PREDECESSOR,
        "suite_manifest_binding": binding(f"{SUITE_PREFIX}/manifest.json"),
        "vectors_binding": binding(f"{SUITE_PREFIX}/vectors.json"),
        "case_expectation_binding": binding(f"{SUITE_PREFIX}/cases.json"),
        "validator_binding": binding(
            "scripts/validate_profile_0_3_jcs_conformance.py"
        ),
        "source_manifest_bindings": [
            {
                "role": role,
                **binding(f"{SUITE_PREFIX}/{role}/source-manifest.json"),
            }
            for role in ("python", "node")
        ],
        "result_bindings": [
            {
                "role": "python",
                "repository_path": RESULT_PATHS["python"],
                "raw_sha256": sha256(python_stdout),
                "byte_count_decimal": str(len(python_stdout)),
            },
            {
                "role": "node",
                "repository_path": RESULT_PATHS["node"],
                "raw_sha256": sha256(node_stdout),
                "byte_count_decimal": str(len(node_stdout)),
            },
        ],
        "execution_receipt_bindings": [
            {
                "role": "python",
                "repository_path": RECEIPT_PATHS["python"],
                "raw_sha256": sha256(python_receipt_bytes),
                "byte_count_decimal": str(len(python_receipt_bytes)),
            },
            {
                "role": "node",
                "repository_path": RECEIPT_PATHS["node"],
                "raw_sha256": sha256(node_receipt_bytes),
                "byte_count_decimal": str(len(node_receipt_bytes)),
            },
        ],
        "projection_sha256": python_document["projection_sha256"],
        "projections_byte_identical": True,
        "comparison_method": "exact_projection_byte_equality",
        "self_attested_byte_consistency_record": True,
        "independently_witnessed_process_evidence": False,
        "canonical_scientific_evidence": False,
        "authority_claim": False,
    }
    comparison_bytes = encode(comparison)

    staged_files = [
        (RESULT_PATHS["python"], python_stdout),
        (RESULT_PATHS["node"], node_stdout),
        (RECEIPT_PATHS["python"], python_receipt_bytes),
        (RECEIPT_PATHS["node"], node_receipt_bytes),
        (COMPARISON_PATH, comparison_bytes),
    ]
    (SUITE / "results").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".prq002g-staging-", dir=SUITE
    ) as staging_name:
        staging = Path(staging_name)
        for relative, raw in staged_files:
            target = staging / Path(relative).name
            target.write_bytes(raw)
            with target.open("rb") as handle:
                os.fsync(handle.fileno())
        directory_handle = os.open(staging, os.O_RDONLY)
        try:
            os.fsync(directory_handle)
        finally:
            os.close(directory_handle)
        for relative, _ in staged_files[:-1]:
            os.replace(staging / Path(relative).name, ROOT / relative)
        os.replace(staging / Path(COMPARISON_PATH).name, ROOT / COMPARISON_PATH)
    print(
        "retained PRQ-002G observation transaction: "
        f"projection {python_document['projection_sha256']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
