#!/usr/bin/env python3
"""Retain two bounded fresh-install observations for the HDA context review.

This architecture-evidence generator creates two distinct fresh virtual
environments from an exact CPython 3.14.2 executable.  Each run installs the
hash-locked architecture requirements with pip's JSON report enabled, runs
``pip check``, and retains the actual subprocess argument vectors and raw
report bytes.  It proves only host-local two-run agreement for these retained
inputs.  It does not prove complete environment identity, cross-host
reproducibility, organizational independence, Gate A acceptance, or runtime
authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = Path(__file__).resolve()
REQUIREMENTS_SOURCE = ROOT / "requirements-architecture.txt"
REQUIREMENTS_LOCK = (
    ROOT / "tools/repository-release/requirements-architecture.lock"
)
REPORT_NAMES = (
    "human-decision-assurance-context-review-python-install-pip-report.json",
    "human-decision-assurance-context-review-python-install-pip-report-run-02.json",
)
OBSERVATION_NAME = (
    "human-decision-assurance-context-review-python-install-observation.json"
)
SCOPE_ID = "hda-successor-t0-technical-review-scope.0005"
RUN_IDS = ("fresh-install.run-01", "fresh-install.run-02")
REPORT_ARTIFACT_IDS = (
    "hda-context-review-python-install-pip-report.run-01.0002",
    "hda-context-review-python-install-pip-report.run-02.0002",
)


class DuplicateKey(ValueError):
    """Raised when supposedly strict JSON contains a duplicate member."""


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def strict_json_bytes(raw: bytes) -> Any:
    return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_object)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def bytes_binding(raw: bytes) -> dict[str, Any]:
    return {
        "byte_count": len(raw),
        "raw_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
    }


def raw_binding(path: Path, *, repository_path: str | None = None) -> dict[str, Any]:
    return {
        **bytes_binding(path.read_bytes()),
        "repository_path": (
            str(path.relative_to(ROOT))
            if repository_path is None
            else repository_path
        ),
    }


def artifact_binding(
    path: Path,
    *,
    artifact_id: str,
    repository_path: str | None = None,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        **raw_binding(path, repository_path=repository_path),
    }


def normalized_distribution_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def closed_environment() -> dict[str, str]:
    return {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_NO_COLOR": "1",
        "PYTHONHASHSEED": "0",
        "TZ": "UTC",
    }


def run_exact(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: Mapping[str, str],
    label: str,
) -> subprocess.CompletedProcess[bytes]:
    completed = subprocess.run(
        [str(item) for item in command],
        cwd=cwd,
        env=dict(environment),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{label} failed with exit {completed.returncode}: "
            + completed.stderr.decode("utf-8", errors="replace")
        )
    completed.stdout.decode("utf-8", errors="strict")
    completed.stderr.decode("utf-8", errors="strict")
    return completed


def command_observation(
    completed: subprocess.CompletedProcess[bytes],
) -> dict[str, Any]:
    if not isinstance(completed.args, (list, tuple)) or not all(
        isinstance(item, str) for item in completed.args
    ):
        raise TypeError("completed process did not retain a string argv")
    return {
        "argv": list(completed.args),
        "exit_code": completed.returncode,
        "stderr": completed.stderr.decode("utf-8"),
        "stdout": completed.stdout.decode("utf-8"),
    }


def selected_report_rows(report: Any) -> list[dict[str, Any]]:
    if not isinstance(report, dict) or not isinstance(report.get("install"), list):
        raise ValueError("pip report install inventory is unavailable")
    rows: list[dict[str, Any]] = []
    for item in report["install"]:
        if not isinstance(item, dict):
            raise ValueError("pip report install row is not an object")
        metadata = item.get("metadata")
        download = item.get("download_info")
        archive = download.get("archive_info") if isinstance(download, dict) else None
        hashes = archive.get("hashes") if isinstance(archive, dict) else None
        if (
            not isinstance(metadata, dict)
            or not isinstance(download, dict)
            or not isinstance(hashes, dict)
            or not isinstance(metadata.get("name"), str)
            or not isinstance(metadata.get("version"), str)
            or not isinstance(download.get("url"), str)
            or re.fullmatch(r"[0-9a-f]{64}", hashes.get("sha256", "")) is None
            or item.get("requested") is not True
        ):
            raise ValueError("pip report install row lacks an exact wheel binding")
        rows.append(
            {
                "normalized_name": normalized_distribution_name(metadata["name"]),
                "requested": True,
                "selected_archive_sha256": hashes["sha256"],
                "source_url": download["url"],
                "version": metadata["version"],
            }
        )
    rows.sort(key=lambda row: row["normalized_name"])
    if len({row["normalized_name"] for row in rows}) != len(rows):
        raise ValueError("pip report contains duplicate normalized distributions")
    return rows


def normalized_preinstall_inventory(raw: bytes) -> list[dict[str, str]]:
    value = strict_json_bytes(raw)
    if not isinstance(value, list):
        raise ValueError("preinstall inventory is not a list")
    rows = sorted(
        (
            {
                "normalized_name": normalized_distribution_name(item["name"]),
                "version": item["version"],
            }
            for item in value
            if isinstance(item, dict)
            and isinstance(item.get("name"), str)
            and isinstance(item.get("version"), str)
        ),
        key=lambda row: row["normalized_name"],
    )
    if len({row["normalized_name"] for row in rows}) != len(rows):
        raise ValueError("preinstall inventory contains duplicate distributions")
    return rows


def require_python_3_14_2(
    python: Path, environment: Mapping[str, str]
) -> subprocess.CompletedProcess[bytes]:
    completed = run_exact(
        [str(python), "--version"],
        cwd=ROOT,
        environment=environment,
        label="Python version probe",
    )
    if completed.stdout != b"Python 3.14.2\n" or completed.stderr:
        raise RuntimeError("observation generator requires exact Python 3.14.2")
    return completed


def run_fresh_install(
    python: Path,
    environment: Mapping[str, str],
    run_id: str,
) -> tuple[bytes, Any, list[dict[str, Any]], dict[str, Any]]:
    with tempfile.TemporaryDirectory(prefix="odeya-hda-fresh-install-") as raw_temp:
        working = Path(raw_temp)
        lock_copy = working / "requirements-architecture.lock"
        lock_raw = REQUIREMENTS_LOCK.read_bytes()
        lock_copy.write_bytes(lock_raw)
        if lock_copy.read_bytes() != lock_raw:
            raise RuntimeError("temporary requirements-lock copy changed")

        venv_create = run_exact(
            [str(python), "-m", "venv", "venv"],
            cwd=working,
            environment=environment,
            label=f"{run_id} virtual environment creation",
        )
        fresh_python = (
            "venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python"
        )
        preinstall = run_exact(
            [fresh_python, "-m", "pip", "list", "--format=json"],
            cwd=working,
            environment=environment,
            label=f"{run_id} preinstall inventory",
        )
        preinstall_packages = normalized_preinstall_inventory(preinstall.stdout)

        install = run_exact(
            [
                fresh_python,
                "-m",
                "pip",
                "install",
                "--isolated",
                "--disable-pip-version-check",
                "--no-input",
                "--require-hashes",
                "--only-binary=:all:",
                "--no-cache-dir",
                "--quiet",
                "--progress-bar=off",
                "--report",
                "pip-report.json",
                "--requirement=requirements-architecture.lock",
            ],
            cwd=working,
            environment=environment,
            label=f"{run_id} hash-locked dependency install",
        )
        report_path = working / "pip-report.json"
        report_raw = report_path.read_bytes()
        report = strict_json_bytes(report_raw)
        selected = selected_report_rows(report)

        pip_check = run_exact(
            [fresh_python, "-m", "pip", "check"],
            cwd=working,
            environment=environment,
            label=f"{run_id} pip check",
        )
        locked_names = {row["normalized_name"] for row in selected}
        preinstalled_locked = sorted(
            row["normalized_name"]
            for row in preinstall_packages
            if row["normalized_name"] in locked_names
        )
        if preinstalled_locked:
            raise RuntimeError(
                f"{run_id} already contained locked distributions: "
                + repr(preinstalled_locked)
            )

        install_observation = command_observation(install)
        report_indices = [
            index
            for index, item in enumerate(install_observation["argv"])
            if item == "--report"
        ]
        if report_indices != [12]:
            raise RuntimeError(f"{run_id} install has an ambiguous --report target")
        target_index = report_indices[0] + 1
        if install_observation["argv"][target_index] != "pip-report.json":
            raise RuntimeError(f"{run_id} report target is not the produced file")
        produced_binding = bytes_binding(report_raw)
        record = {
            "execution_sequence": [
                {"phase": "venv_create", **command_observation(venv_create)},
                {"phase": "preinstall", **command_observation(preinstall)},
                {"phase": "install", **install_observation},
                {"phase": "pip_check", **command_observation(pip_check)},
            ],
            "installer_metadata": {
                "network_resolution_required": True,
                "pip_report_format_version": (
                    report.get("version") if isinstance(report, dict) else None
                ),
                "pip_version": (
                    report.get("pip_version") if isinstance(report, dict) else None
                ),
                "pip_version_bound_by_reviewed_subject": False,
            },
            "preinstall_locked_distribution_count": 0,
            "preinstall_packages": preinstall_packages,
            "report_target_relation": {
                "flag_argv_index": report_indices[0],
                "produced_bytes_binding": produced_binding,
                "resolution_base": "ephemeral_run_working_directory",
                "target_argv_index": target_index,
                "target_argv_value": "pip-report.json",
            },
            "requirements_lock_copy_binding": {
                **bytes_binding(lock_copy.read_bytes()),
                "execution_target": "requirements-architecture.lock",
            },
            "run_id": run_id,
            "working_directory": {
                "absolute_path_retained": False,
                "distinct_fresh_directory": True,
                "semantics": "new_os_temporary_directory_removed_after_run",
            },
        }
    return report_raw, report, selected, record


def generate(python: Path, output_directory: Path) -> tuple[tuple[Path, Path], Path]:
    environment = closed_environment()
    python = python.resolve(strict=True)
    python_probe = require_python_3_14_2(python, environment)
    output_directory.mkdir(parents=True, exist_ok=True)
    report_outputs = tuple(output_directory / name for name in REPORT_NAMES)
    observation_output = output_directory / OBSERVATION_NAME

    run_results = [
        run_fresh_install(python, environment, run_id) for run_id in RUN_IDS
    ]
    report_raws = [item[0] for item in run_results]
    reports = [item[1] for item in run_results]
    selected_rows = [item[2] for item in run_results]
    run_records = [item[3] for item in run_results]
    if report_raws[0] != report_raws[1]:
        raise RuntimeError("two fresh installs produced different raw pip reports")
    if reports[0] != reports[1] or selected_rows[0] != selected_rows[1]:
        raise RuntimeError("two fresh pip reports produced different projections")

    for output, raw in zip(report_outputs, report_raws, strict=True):
        output.write_bytes(raw)
    for index, output in enumerate(report_outputs):
        retained = artifact_binding(
            output,
            artifact_id=REPORT_ARTIFACT_IDS[index],
            repository_path=f"architecture/{REPORT_NAMES[index]}",
        )
        run_records[index]["report_target_relation"][
            "retained_artifact_binding"
        ] = retained
        if output.read_bytes() != report_raws[index]:
            raise RuntimeError(f"retained report {index + 1} changed after write")

    common_report = reports[0]
    if not isinstance(common_report, dict):
        raise ValueError("pip report is not an object")
    common_selected = selected_rows[0]
    common_binding = bytes_binding(report_raws[0])
    observation = {
        "artifact_class": (
            "human_decision_assurance_context_review_python_install_observation"
        ),
        "authority_boundary": {
            "accountable_review_completed": False,
            "complete_environment_identity_proven": False,
            "cross_host_reproducibility_proven": False,
            "external_effects_authorized": False,
            "gate_a_accepted": False,
            "organizational_independence_proven": False,
            "runtime_authorized": False,
        },
        "candidate_status": (
            "host_bound_two_fresh_install_execution_observation_not_complete_"
            "environment_identity"
        ),
        "closed_subprocess_environment": environment,
        "fresh_environment": {
            "distinct_fresh_temporary_environment_count": 2,
            "existing_project_environment_reused": False,
            "temporary_absolute_paths_retained": False,
        },
        "generator_source_binding": artifact_binding(
            SOURCE_PATH,
            artifact_id=(
                "hda-context-review-python-install-observation-generator.0003"
            ),
        ),
        "host_observation": {
            "machine": platform.machine(),
            "system": platform.system(),
        },
        "observation_id": (
            "hda-context-review-python-install-observation.2026-07-21.0004"
        ),
        "pip_report_projection": {
            "environment": common_report.get("environment"),
            "selected_distributions": common_selected,
        },
        "python_observation": {
            "implementation_name": "cpython",
            "implementation_version": "3.14.2",
            "version_probe": command_observation(python_probe),
        },
        "raw_report_byte_identity": {
            "byte_identical": True,
            "common_byte_count": common_binding["byte_count"],
            "common_raw_sha256": common_binding["raw_sha256"],
            "comparison_method": "direct_raw_byte_equality_then_post_write_reread",
            "distinct_artifact_ids_and_repository_paths": True,
            "ordered_run_ids": list(RUN_IDS),
        },
        "requirements_lock_binding": artifact_binding(
            REQUIREMENTS_LOCK,
            artifact_id="architecture-python-requirements-lock.0001",
        ),
        "requirements_source_binding": artifact_binding(
            REQUIREMENTS_SOURCE,
            artifact_id="architecture-python-requirements-source.0001",
        ),
        "runs": run_records,
        "schema_version": "0.1.0",
        "selected_distributions": [
            {
                "normalized_name": row["normalized_name"],
                "selected_archive_sha256": row["selected_archive_sha256"],
                "version": row["version"],
            }
            for row in common_selected
        ],
        "subject_scope_id": SCOPE_ID,
        "summary": {
            "all_selected_archive_hashes_present_in_lock": True,
            "locked_distribution_set_exact_match": True,
            "pip_check_passed_for_both_runs": True,
            "raw_pip_reports_retained": 2,
            "selected_distribution_count": len(common_selected),
            "two_fresh_install_reports_byte_identical": True,
        },
    }
    observation_output.write_bytes(canonical_json_bytes(observation))
    return report_outputs, observation_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python-executable",
        type=Path,
        default=Path(os.environ.get("HDA_CONTEXT_REVIEW_PYTHON", "python3")),
        help="exact CPython 3.14.2 executable used to create both fresh venvs",
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=ROOT / "architecture",
        help="directory receiving the two retained reports and observation",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reports, observation = generate(
        args.python_executable,
        args.output_directory.resolve(),
    )
    for report in reports:
        print(f"retained fresh-install pip report: {report}")
    print(f"retained two-run fresh-install observation: {observation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
