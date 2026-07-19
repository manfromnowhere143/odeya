#!/usr/bin/env python3
"""Verify Odeya's exact GitHub publication checks and repository governance.

The checks verifier accepts only the four expected GitHub Actions push runs for
one exact commit and branch. The governance verifier accepts only the pinned
main and immutable-candidate rulesets plus the exact public repository and
Actions settings. Neither verifier changes GitHub.
"""

from __future__ import annotations

import argparse
import copy
import contextlib
import hashlib
import io
import json
import math
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote


REPOSITORY = "manfromnowhere143/odeya"
REPOSITORY_OWNER = "manfromnowhere143"
REPOSITORY_NAME = "odeya"
REPOSITORY_NODE_ID = "R_kgDOTbjMZA"
API_VERSION = "2026-03-10"
GITHUB_ACTIONS_APP_ID = 15368
CANONICAL_SOURCE_SHA256 = (
    "2d03b3f64ff40b9d376b227d8d67dc13c549c14b526ffb735f78f013d98f4924"
)
RULESET_NAME = "main exact-SHA fast-forward"
RELEASE_RULESET_NAME = "immutable publication candidates"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

WORKFLOWS: dict[str, tuple[str, tuple[str, ...]]] = {
    ".github/workflows/architecture.yml": (
        "Architecture / Foundation",
        (
            "Fast policy",
            "Foundation",
            "Schema contracts",
            "Semantic contracts",
            "Adversarial controls",
            "Canonical identity",
            "Architecture evidence",
        ),
    ),
    ".github/workflows/formal.yml": (
        "Architecture / Bounded Formal Models",
        ("Bounded formal models",),
    ),
    ".github/workflows/release-surface.yml": (
        "Repository / Release Surface",
        ("Release surface",),
    ),
    ".github/workflows/publication-sequence.yml": (
        "Repository / Publication Sequence",
        ("Publication sequence",),
    ),
}
REQUIRED_CONTEXTS = frozenset(
    job_name
    for _, job_names in WORKFLOWS.values()
    for job_name in job_names
)
PENDING_RUN_STATUSES = frozenset(
    {"queued", "in_progress", "pending", "requested", "waiting"}
)
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9:._-]{1,160}$")
PR_CLOSURE_COMMENT = (
    "Closing this stale automated update before ADR 0091 disables pull "
    "requests for Odeya's exact-SHA publication lane. This isolated bot "
    "change cannot be represented as accepted independently of the pinned "
    "release-tool lock and current repository base."
)
REPOSITORY_POLICY_QUERY = (
    "query OdeyaRepositoryPolicy($owner:String!,$name:String!){"
    "repository(owner:$owner,name:$name){"
    "id nameWithOwner hasPullRequestsEnabled mergeCommitAllowed "
    "squashMergeAllowed rebaseMergeAllowed autoMergeAllowed "
    "deleteBranchOnMerge allowUpdateBranch"
    "}}"
)


def repository_settings_request() -> dict[str, Any]:
    return {
        "has_pull_requests": False,
        "allow_merge_commit": False,
        "allow_squash_merge": False,
        "allow_rebase_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": False,
        "allow_update_branch": False,
    }


def actions_pinning_request() -> dict[str, Any]:
    return {
        "enabled": True,
        "allowed_actions": "all",
        "sha_pinning_required": True,
    }


def actions_selection_request() -> dict[str, Any]:
    return {
        "enabled": True,
        "allowed_actions": "selected",
        "sha_pinning_required": True,
    }


def selected_actions_request() -> dict[str, Any]:
    return {
        "github_owned_allowed": True,
        "verified_allowed": False,
        "patterns_allowed": [],
    }


def workflow_permissions_request() -> dict[str, Any]:
    return {
        "default_workflow_permissions": "read",
        "can_approve_pull_request_reviews": False,
    }


def release_ruleset_request() -> dict[str, Any]:
    return {
        "name": RELEASE_RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {
            "ref_name": {
                "include": ["refs/heads/release/*"],
                "exclude": [],
            }
        },
        "rules": [
            {"type": "deletion"},
            {
                "type": "update",
                "parameters": {
                    "update_allows_fetch_and_merge": False,
                },
            },
            {"type": "non_fast_forward"},
            {"type": "required_linear_history"},
        ],
    }


def main_ruleset_request() -> dict[str, Any]:
    return {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {
            "ref_name": {
                "include": ["refs/heads/main"],
                "exclude": [],
            }
        },
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {"type": "required_linear_history"},
            {
                "type": "required_status_checks",
                "parameters": {
                    "do_not_enforce_on_create": False,
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": [
                        {
                            "context": context,
                            "integration_id": GITHUB_ACTIONS_APP_ID,
                        }
                        for context in sorted(REQUIRED_CONTEXTS)
                    ],
                },
            },
        ],
    }


def canonical_json_bytes(document: Any) -> bytes:
    return json.dumps(
        document,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def retained_json_bytes(document: Any) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


class DuplicateKeyError(ValueError):
    """Raised when a JSON response contains a duplicate object member."""


class GitHubApiError(RuntimeError):
    """Raised when a read-only GitHub API request cannot be completed."""


@dataclass(frozen=True)
class Evaluation:
    """One pure verification result."""

    state: str
    messages: tuple[str, ...]


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def load_strict_json_file(
    path: Path,
    description: str,
) -> tuple[dict[str, Any], bytes]:
    path = _absolute_without_symlink_resolution(path)
    _reject_symlink_components(path)
    _require_private_regular_file(path, description)
    try:
        payload = path.read_bytes()
        document = json.loads(payload, object_pairs_hook=unique_object)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise GitHubApiError(f"cannot decode {description}: {exc}") from exc
    if not isinstance(document, dict):
        raise GitHubApiError(f"{description} is not one JSON object")
    if payload != retained_json_bytes(document):
        raise GitHubApiError(
            f"{description} bytes are not the exact retained JSON encoding"
        )
    return document, payload


def expected_mutation_operations() -> list[dict[str, Any]]:
    base = f"/repos/{REPOSITORY}"
    operations: list[dict[str, Any]] = []
    sequence = 1
    for number in (1, 2):
        operations.append(
            {
                "sequence": sequence,
                "operation_id": f"pr-{number}-comment",
                "method": "POST",
                "endpoint": f"{base}/issues/{number}/comments",
                "body": {"body": PR_CLOSURE_COMMENT},
                "status_code": 201,
                "resource_required": True,
            }
        )
        sequence += 1
        operations.append(
            {
                "sequence": sequence,
                "operation_id": f"pr-{number}-close",
                "method": "PATCH",
                "endpoint": f"{base}/pulls/{number}",
                "body": {"state": "closed"},
                "status_code": 200,
                "resource_required": True,
            }
        )
        sequence += 1
    for operation_id, method, endpoint, body, status, resource_required in (
        (
            "repository-settings",
            "PATCH",
            base,
            repository_settings_request(),
            200,
            True,
        ),
        (
            "actions-sha-pinning",
            "PUT",
            f"{base}/actions/permissions",
            actions_pinning_request(),
            204,
            False,
        ),
        (
            "actions-selection",
            "PUT",
            f"{base}/actions/permissions",
            actions_selection_request(),
            204,
            False,
        ),
        (
            "selected-actions",
            "PUT",
            f"{base}/actions/permissions/selected-actions",
            selected_actions_request(),
            204,
            False,
        ),
        (
            "workflow-permissions",
            "PUT",
            f"{base}/actions/permissions/workflow",
            workflow_permissions_request(),
            204,
            False,
        ),
        (
            "release-ruleset",
            "POST",
            f"{base}/rulesets",
            release_ruleset_request(),
            201,
            True,
        ),
        (
            "main-ruleset",
            "POST",
            f"{base}/rulesets",
            main_ruleset_request(),
            201,
            True,
        ),
    ):
        operations.append(
            {
                "sequence": sequence,
                "operation_id": operation_id,
                "method": method,
                "endpoint": endpoint,
                "body": body,
                "status_code": status,
                "resource_required": resource_required,
            }
        )
        sequence += 1
    return operations


def mutation_journal_errors(
    document: Any,
    *,
    base_sha: str,
    bootstrap_sha: str,
) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    ruleset_ids: dict[str, int] = {}
    expected_top = {
        "schema_version",
        "artifact_class",
        "repository",
        "api_version",
        "base_commit",
        "bootstrap_candidate_commit",
        "operations",
        "canonical_scientific_evidence",
    }
    if not isinstance(document, dict) or set(document) != expected_top:
        return ["mutation journal top-level member census is not exact"], ruleset_ids
    expected_values = {
        "schema_version": "0.1.0",
        "artifact_class": "github_governance_mutation_journal",
        "repository": REPOSITORY,
        "api_version": API_VERSION,
        "base_commit": base_sha,
        "bootstrap_candidate_commit": bootstrap_sha,
        "canonical_scientific_evidence": False,
    }
    errors.extend(_require_exact_values(document, expected_values, "mutation journal"))
    operations = document.get("operations")
    expected_operations = expected_mutation_operations()
    if not isinstance(operations, list) or len(operations) != len(expected_operations):
        errors.append("mutation journal operation census is not exact")
        return errors, ruleset_ids
    for index, (operation, expected) in enumerate(
        zip(operations, expected_operations, strict=True)
    ):
        label = f"mutation journal operation {index + 1}"
        if not isinstance(operation, dict) or set(operation) != {
            "sequence",
            "operation_id",
            "request",
            "response",
        }:
            errors.append(f"{label} member census is not exact")
            continue
        if operation.get("sequence") != expected["sequence"]:
            errors.append(f"{label} sequence is not contiguous")
        if operation.get("operation_id") != expected["operation_id"]:
            errors.append(f"{label} operation identity is not exact")
        request = operation.get("request")
        if not isinstance(request, dict) or set(request) != {
            "method",
            "endpoint",
            "body",
            "canonical_body_sha256",
        }:
            errors.append(f"{label} request member census is not exact")
        else:
            for field in ("method", "endpoint", "body"):
                if request.get(field) != expected[field]:
                    errors.append(f"{label} request {field} is not exact")
            expected_digest = hashlib.sha256(
                canonical_json_bytes(expected["body"])
            ).hexdigest()
            if request.get("canonical_body_sha256") != expected_digest:
                errors.append(f"{label} canonical request digest differs")
        response = operation.get("response")
        if not isinstance(response, dict) or set(response) != {
            "status_code",
            "date",
            "github_request_id",
            "api_version_selected",
            "response_body_sha256",
            "resource_id",
        }:
            errors.append(f"{label} response member census is not exact")
            continue
        if response.get("status_code") != expected["status_code"]:
            errors.append(f"{label} HTTP status is not exact")
        if not isinstance(response.get("date"), str) or not response["date"].strip():
            errors.append(f"{label} response date is absent")
        request_id = response.get("github_request_id")
        if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
            errors.append(f"{label} GitHub request id is malformed")
        if response.get("api_version_selected") != API_VERSION:
            errors.append(f"{label} selected API version is not exact")
        body_digest = response.get("response_body_sha256")
        if not isinstance(body_digest, str) or not SHA256_RE.fullmatch(body_digest):
            errors.append(f"{label} response body digest is malformed")
        if expected["status_code"] == 204 and body_digest != EMPTY_SHA256:
            errors.append(f"{label} 204 response body is not empty")
        resource_id = response.get("resource_id")
        if expected["resource_required"]:
            if not is_integer(resource_id) or resource_id <= 0:
                errors.append(f"{label} response resource id is not positive")
        elif resource_id is not None:
            errors.append(f"{label} response resource id must be null")
        if expected["operation_id"] in {"release-ruleset", "main-ruleset"} and (
            is_integer(resource_id) and resource_id > 0
        ):
            ruleset_ids[expected["operation_id"]] = resource_id
    if set(ruleset_ids) != {"release-ruleset", "main-ruleset"}:
        errors.append("mutation journal does not retain both ruleset ids")
    elif len(set(ruleset_ids.values())) != 2:
        errors.append("mutation journal ruleset ids are not distinct")
    return errors, ruleset_ids


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def gh_json(endpoint: str, **fields: object) -> Any:
    """Read one GitHub REST endpoint through the authenticated gh client."""

    command = [
        "gh",
        "api",
        "--hostname",
        "github.com",
        endpoint,
        "--method",
        "GET",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version: {API_VERSION}",
        "-H",
        "Cache-Control: no-cache",
    ]
    for key, value in fields.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        else:
            rendered = str(value)
        command.extend(("-f", f"{key}={rendered}"))
    environment = dict(os.environ)
    environment["GH_PAGER"] = "cat"
    environment["PAGER"] = "cat"
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitHubApiError(f"GitHub API request could not run: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown failure"
        raise GitHubApiError(f"GitHub API request failed for {endpoint}: {detail}")
    try:
        return json.loads(result.stdout, object_pairs_hook=unique_object)
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        raise GitHubApiError(
            f"GitHub API returned invalid JSON for {endpoint}: {exc}"
        ) from exc


def gh_graphql_json(query: str, **variables: str) -> Any:
    """Read one fixed GitHub GraphQL query through the authenticated gh client."""

    if query != REPOSITORY_POLICY_QUERY or variables != {
        "owner": REPOSITORY_OWNER,
        "name": REPOSITORY_NAME,
    }:
        raise GitHubApiError(
            "GitHub GraphQL request is not the fixed repository-policy query"
        )
    command = [
        "gh",
        "api",
        "--hostname",
        "github.com",
        "graphql",
        "--method",
        "POST",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        f"X-GitHub-Api-Version: {API_VERSION}",
        "-H",
        "Cache-Control: no-cache",
        "-f",
        f"query={query}",
    ]
    for key, value in variables.items():
        command.extend(("-f", f"{key}={value}"))
    environment = dict(os.environ)
    environment["GH_PAGER"] = "cat"
    environment["PAGER"] = "cat"
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitHubApiError(
            f"GitHub GraphQL request could not run: {exc}"
        ) from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown failure"
        raise GitHubApiError(f"GitHub GraphQL request failed: {detail}")
    try:
        return json.loads(result.stdout, object_pairs_hook=unique_object)
    except (json.JSONDecodeError, DuplicateKeyError) as exc:
        raise GitHubApiError(
            f"GitHub GraphQL returned invalid JSON: {exc}"
        ) from exc


def repository_policy_from_graphql(document: Any) -> dict[str, Any]:
    """Bind the otherwise-hidden post-disable merge policy to one repository."""

    if not isinstance(document, dict) or set(document) != {"data"}:
        raise GitHubApiError("repository-policy GraphQL envelope is not exact")
    data = document.get("data")
    if not isinstance(data, dict) or set(data) != {"repository"}:
        raise GitHubApiError("repository-policy GraphQL data census is not exact")
    repository = data.get("repository")
    expected_fields = {
        "id",
        "nameWithOwner",
        "hasPullRequestsEnabled",
        "mergeCommitAllowed",
        "squashMergeAllowed",
        "rebaseMergeAllowed",
        "autoMergeAllowed",
        "deleteBranchOnMerge",
        "allowUpdateBranch",
    }
    if not isinstance(repository, dict) or set(repository) != expected_fields:
        raise GitHubApiError("repository-policy GraphQL field census is not exact")
    if (
        repository.get("id") != REPOSITORY_NODE_ID
        or repository.get("nameWithOwner") != REPOSITORY
    ):
        raise GitHubApiError("repository-policy GraphQL identity is not exact")
    boolean_fields = expected_fields - {"id", "nameWithOwner"}
    if any(type(repository.get(field)) is not bool for field in boolean_fields):
        raise GitHubApiError("repository-policy GraphQL boolean census is malformed")
    return {
        "read_surface": "github_graphql_v4",
        "node_id": repository["id"],
        "full_name": repository["nameWithOwner"],
        "has_pull_requests": repository["hasPullRequestsEnabled"],
        "allow_merge_commit": repository["mergeCommitAllowed"],
        "allow_squash_merge": repository["squashMergeAllowed"],
        "allow_rebase_merge": repository["rebaseMergeAllowed"],
        "allow_auto_merge": repository["autoMergeAllowed"],
        "delete_branch_on_merge": repository["deleteBranchOnMerge"],
        "allow_update_branch": repository["allowUpdateBranch"],
    }


def fetch_repository_policy() -> dict[str, Any]:
    return repository_policy_from_graphql(
        gh_graphql_json(
            REPOSITORY_POLICY_QUERY,
            owner=REPOSITORY_OWNER,
            name=REPOSITORY_NAME,
        )
    )


def fetch_check_snapshot(
    sha: str, branch: str, *, include_jobs: bool = True
) -> dict[str, Any]:
    """Fetch all run, job, and check-run records for one candidate."""

    document = gh_json(
        f"repos/{REPOSITORY}/actions/runs",
        event="push",
        branch=branch,
        head_sha=sha,
        per_page=100,
    )
    if not isinstance(document, dict):
        return {"total_count": None, "runs": document}
    raw_runs = document.get("workflow_runs")
    records: list[dict[str, Any]] = []
    if isinstance(raw_runs, list):
        for raw_run in raw_runs:
            record: dict[str, Any] = {
                "run": raw_run,
                "jobs_total_count": None,
                "jobs": [],
            }
            if not isinstance(raw_run, dict):
                records.append(record)
                continue
            run_id = raw_run.get("id")
            path = raw_run.get("path")
            if (
                not include_jobs
                or not is_integer(run_id)
                or path not in WORKFLOWS
            ):
                records.append(record)
                continue
            jobs_document = gh_json(
                f"repos/{REPOSITORY}/actions/runs/{run_id}/jobs",
                filter="all",
                per_page=100,
            )
            if not isinstance(jobs_document, dict):
                record["jobs"] = jobs_document
                records.append(record)
                continue
            record["jobs_total_count"] = jobs_document.get("total_count")
            raw_jobs = jobs_document.get("jobs")
            if not isinstance(raw_jobs, list):
                record["jobs"] = raw_jobs
                records.append(record)
                continue
            job_records: list[dict[str, Any]] = []
            for raw_job in raw_jobs:
                check_run = None
                if isinstance(raw_job, dict) and is_integer(raw_job.get("id")):
                    check_run = gh_json(
                        f"repos/{REPOSITORY}/check-runs/{raw_job['id']}"
                    )
                job_records.append({"job": raw_job, "check_run": check_run})
            record["jobs"] = job_records
            records.append(record)
    else:
        records = raw_runs
    return {"total_count": document.get("total_count"), "runs": records}


def _run_identity_errors(
    run: dict[str, Any],
    *,
    sha: str,
    branch: str,
    expected_path: str,
    expected_name: str,
) -> list[str]:
    errors: list[str] = []
    expected = {
        "path": expected_path,
        "name": expected_name,
        "event": "push",
        "head_sha": sha,
        "head_branch": branch,
        "run_attempt": 1,
    }
    for field, value in expected.items():
        if run.get(field) != value:
            errors.append(
                f"{expected_path}: run {field} is {run.get(field)!r}, expected {value!r}"
            )
    if not is_integer(run.get("id")) or run["id"] <= 0:
        errors.append(f"{expected_path}: run id is not one positive integer")
    return errors


def _completed_success_errors(
    subject: dict[str, Any],
    label: str,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    pending: list[str] = []
    status = subject.get("status")
    conclusion = subject.get("conclusion")
    if status == "completed":
        if conclusion != "success":
            errors.append(
                f"{label}: conclusion is {conclusion!r}, expected exact 'success'"
            )
    elif status in PENDING_RUN_STATUSES:
        pending.append(f"{label}: status is {status}")
    else:
        errors.append(f"{label}: status is {status!r}, not a recognized live status")
    return errors, pending


def evaluate_checks(snapshot: Any, *, sha: str, branch: str) -> Evaluation:
    """Purely evaluate one fetched checks snapshot."""

    errors: list[str] = []
    pending: list[str] = []
    if not isinstance(snapshot, dict):
        return Evaluation("terminal", ("checks response is not one object",))
    records = snapshot.get("runs")
    total_count = snapshot.get("total_count")
    if not isinstance(records, list):
        return Evaluation("terminal", ("workflow_runs is not one array",))
    if (
        not is_integer(total_count)
        or total_count < 0
        or total_count != len(records)
    ):
        errors.append(
            "workflow run total_count does not equal the returned exact run census"
        )

    by_path: dict[str, list[dict[str, Any]]] = {
        path: [] for path in WORKFLOWS
    }
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("run"), dict):
            errors.append(f"workflow run record {index} is malformed")
            continue
        run = record["run"]
        path = run.get("path")
        if path not in WORKFLOWS:
            errors.append(f"unexpected workflow path in candidate run: {path!r}")
            continue
        by_path[path].append(record)

    for path, matches in by_path.items():
        if len(matches) > 1:
            errors.append(f"{path}: duplicate push runs exist for the exact candidate")
        elif not matches:
            pending.append(f"{path}: expected push run has not appeared")
    if len(records) > len(WORKFLOWS):
        errors.append(
            f"candidate has {len(records)} push runs; expected exactly {len(WORKFLOWS)}"
        )

    for path, matches in by_path.items():
        if len(matches) != 1:
            continue
        record = matches[0]
        run = record["run"]
        expected_name, expected_jobs = WORKFLOWS[path]
        errors.extend(
            _run_identity_errors(
                run,
                sha=sha,
                branch=branch,
                expected_path=path,
                expected_name=expected_name,
            )
        )
        run_errors, run_pending = _completed_success_errors(run, f"{path}: run")
        errors.extend(run_errors)
        pending.extend(run_pending)
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            continue

        job_records = record.get("jobs")
        jobs_total_count = record.get("jobs_total_count")
        if not isinstance(job_records, list):
            errors.append(f"{path}: jobs response is not one array")
            continue
        if (
            not is_integer(jobs_total_count)
            or jobs_total_count != len(job_records)
        ):
            errors.append(f"{path}: job total_count does not equal returned jobs")

        by_name: dict[str, list[dict[str, Any]]] = {
            name: [] for name in expected_jobs
        }
        for job_index, job_record in enumerate(job_records):
            if (
                not isinstance(job_record, dict)
                or not isinstance(job_record.get("job"), dict)
            ):
                errors.append(f"{path}: job record {job_index} is malformed")
                continue
            job_name = job_record["job"].get("name")
            if job_name not in by_name:
                errors.append(f"{path}: unexpected job name {job_name!r}")
                continue
            by_name[job_name].append(job_record)
        for job_name, matches_for_name in by_name.items():
            if len(matches_for_name) != 1:
                errors.append(
                    f"{path}: job {job_name!r} occurs {len(matches_for_name)} times"
                )
                continue
            job_record = matches_for_name[0]
            job = job_record["job"]
            job_label = f"{path}: job {job_name!r}"
            expected_job_identity = {
                "name": job_name,
                "head_sha": sha,
                "head_branch": branch,
                "run_attempt": 1,
                "run_id": run.get("id"),
                "workflow_name": expected_name,
            }
            for field, value in expected_job_identity.items():
                if job.get(field) != value:
                    errors.append(
                        f"{job_label}: {field} is {job.get(field)!r}, "
                        f"expected {value!r}"
                    )
            if not is_integer(job.get("id")) or job["id"] <= 0:
                errors.append(f"{job_label}: id is not one positive integer")
            job_errors, job_pending = _completed_success_errors(job, job_label)
            errors.extend(job_errors)
            pending.extend(job_pending)

            check_run = job_record.get("check_run")
            if not isinstance(check_run, dict):
                errors.append(f"{job_label}: check-run response is absent or malformed")
                continue
            check_label = f"{job_label}: check run"
            expected_check_identity = {
                "id": job.get("id"),
                "name": job_name,
                "head_sha": sha,
                "status": "completed",
                "conclusion": "success",
            }
            for field, value in expected_check_identity.items():
                if check_run.get(field) != value:
                    errors.append(
                        f"{check_label}: {field} is {check_run.get(field)!r}, "
                        f"expected {value!r}"
                    )
            app = check_run.get("app")
            if not isinstance(app, dict) or app.get("id") != GITHUB_ACTIONS_APP_ID:
                observed = app.get("id") if isinstance(app, dict) else None
                errors.append(
                    f"{check_label}: app id is {observed!r}, "
                    f"expected {GITHUB_ACTIONS_APP_ID}"
                )

    if errors:
        return Evaluation("terminal", tuple(errors))
    if pending:
        return Evaluation("pending", tuple(pending))
    if len(records) != len(WORKFLOWS):
        return Evaluation(
            "pending",
            (
                f"candidate has {len(records)} push runs; "
                f"waiting for exactly {len(WORKFLOWS)}",
            ),
        )
    return Evaluation("success", ())


def evaluate_run_census(snapshot: Any, *, sha: str, branch: str) -> Evaluation:
    """Evaluate only four workflow runs while avoiding job/check API fan-out."""

    errors: list[str] = []
    pending: list[str] = []
    if not isinstance(snapshot, dict):
        return Evaluation("terminal", ("checks response is not one object",))
    records = snapshot.get("runs")
    total_count = snapshot.get("total_count")
    if not isinstance(records, list):
        return Evaluation("terminal", ("workflow_runs is not one array",))
    if not is_integer(total_count) or total_count != len(records):
        errors.append(
            "workflow run total_count does not equal the returned exact run census"
        )
    by_path: dict[str, list[dict[str, Any]]] = {
        path: [] for path in WORKFLOWS
    }
    for index, record in enumerate(records):
        if not isinstance(record, dict) or not isinstance(record.get("run"), dict):
            errors.append(f"workflow run record {index} is malformed")
            continue
        run = record["run"]
        path = run.get("path")
        if path not in WORKFLOWS:
            errors.append(f"unexpected workflow path in candidate run: {path!r}")
            continue
        by_path[path].append(record)
    if len(records) > len(WORKFLOWS):
        errors.append(
            f"candidate has {len(records)} push runs; expected exactly {len(WORKFLOWS)}"
        )
    for path, matches in by_path.items():
        if len(matches) > 1:
            errors.append(f"{path}: duplicate push runs exist for the exact candidate")
            continue
        if not matches:
            pending.append(f"{path}: expected push run has not appeared")
            continue
        run = matches[0]["run"]
        expected_name, _expected_jobs = WORKFLOWS[path]
        errors.extend(
            _run_identity_errors(
                run,
                sha=sha,
                branch=branch,
                expected_path=path,
                expected_name=expected_name,
            )
        )
        run_errors, run_pending = _completed_success_errors(run, f"{path}: run")
        errors.extend(run_errors)
        pending.extend(run_pending)
    if errors:
        return Evaluation("terminal", tuple(errors))
    if pending:
        return Evaluation("pending", tuple(pending))
    return Evaluation("success", ())


def fetch_governance_snapshot() -> dict[str, Any]:
    """Fetch all live repository-governance records used by the contract."""

    summaries = gh_json(f"repos/{REPOSITORY}/rulesets", per_page=100)
    rulesets: list[Any] = []
    if isinstance(summaries, list):
        for summary in summaries:
            if isinstance(summary, dict) and is_integer(summary.get("id")):
                detail = gh_json(f"repos/{REPOSITORY}/rulesets/{summary['id']}")
                rulesets.append(matched_ruleset_detail(summary, detail))
            else:
                rulesets.append(summary)
    else:
        rulesets = summaries

    actions = gh_json(f"repos/{REPOSITORY}/actions/permissions")
    selected_actions = None
    if isinstance(actions, dict) and actions.get("allowed_actions") == "selected":
        selected_actions = gh_json(
            f"repos/{REPOSITORY}/actions/permissions/selected-actions"
        )
    return {
        "rulesets": rulesets,
        "repository": gh_json(f"repos/{REPOSITORY}"),
        "repository_policy": fetch_repository_policy(),
        "actions": actions,
        "selected_actions": selected_actions,
        "workflow_permissions": gh_json(
            f"repos/{REPOSITORY}/actions/permissions/workflow"
        ),
    }


def matched_ruleset_detail(summary: dict[str, Any], detail: Any) -> dict[str, Any]:
    """Bind a detailed ruleset response to the summary identity requested."""

    identifier = summary.get("id")
    if (
        not is_integer(identifier)
        or identifier <= 0
        or not isinstance(detail, dict)
        or detail.get("id") != identifier
    ):
        raise GitHubApiError(
            "ruleset detail identity differs from its requested summary id "
            f"{identifier!r}"
        )
    return detail


def pull_requests_from_issue_page(items: Any) -> list[dict[str, int]]:
    """Normalize an exact open-PR census while repository PRs are disabled.

    GitHub returns 404 from the pulls endpoint after `has_pull_requests=false`.
    The repository-issues endpoint remains readable and marks every pull
    request with a `pull_request` member. Refuse a saturated single page rather
    than silently treating a possibly truncated response as a complete census.
    """

    if not isinstance(items, list):
        raise GitHubApiError("open issue/PR census is not one array")
    if len(items) >= 100:
        raise GitHubApiError(
            "open issue/PR census saturated its exact single-page bound"
        )
    pull_requests: list[dict[str, int]] = []
    observed_numbers: set[int] = set()
    for item in items:
        if not isinstance(item, dict):
            raise GitHubApiError("open issue/PR census contains a non-object")
        if "pull_request" not in item:
            continue
        number = item.get("number")
        if not is_integer(number) or number <= 0:
            raise GitHubApiError("open pull-request census has a malformed number")
        if number in observed_numbers:
            raise GitHubApiError("open pull-request census repeats a number")
        observed_numbers.add(number)
        pull_requests.append({"number": number})
    return sorted(pull_requests, key=lambda pull_request: pull_request["number"])


def fetch_activation_snapshot(sha: str, bootstrap_sha: str) -> dict[str, Any]:
    candidate_branch = f"release/{sha}"
    bootstrap_branch = f"release/{bootstrap_sha}"
    governance = fetch_governance_snapshot()
    branches: dict[str, dict[str, Any]] = {}
    for branch in ("main", candidate_branch):
        encoded_branch = quote(branch, safe="")
        branches[branch] = {
            "branch": gh_json(
                f"repos/{REPOSITORY}/branches/{encoded_branch}"
            ),
            "effective_rules": gh_json(
                f"repos/{REPOSITORY}/rules/branches/{encoded_branch}",
                per_page=100,
            ),
        }
    commits = {
        commit_sha: gh_json(
            f"repos/{REPOSITORY}/git/commits/{commit_sha}"
        )
        for commit_sha in (bootstrap_sha, sha)
    }
    open_pull_requests = pull_requests_from_issue_page(
        gh_json(
            f"repos/{REPOSITORY}/issues",
            state="open",
            per_page=100,
        )
    )
    check_subjects = (
        (bootstrap_branch, bootstrap_sha),
        (candidate_branch, sha),
        ("main", sha),
    )
    final_check_censuses = {
        branch: fetch_check_snapshot(
            subject_sha,
            branch,
            include_jobs=False,
        )
        for branch, subject_sha in check_subjects
    }
    refs: dict[str, Any] = {}
    # The critical mutable main ref is intentionally the final GitHub request
    # in the settlement snapshot. Permanent release refs are observed first.
    ref_names = [
        f"heads/{bootstrap_branch}",
        f"heads/{candidate_branch}",
        "heads/main",
    ]
    for ref in ref_names:
        refs[f"refs/{ref}"] = gh_json(
            f"repos/{REPOSITORY}/git/ref/{quote(ref, safe='')}"
        )
    return {
        "governance": governance,
        "branches": branches,
        "refs": refs,
        "commits": commits,
        "open_pull_requests": open_pull_requests,
        "final_check_censuses": final_check_censuses,
    }


def _effective_semantic_rule(
    rule: dict[str, Any],
    *,
    expected_ruleset_id: int,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    rule_type = rule.get("type")
    base_fields = {
        "ruleset_id",
        "ruleset_source",
        "ruleset_source_type",
        "type",
    }
    allowed_fields = set(base_fields)
    if "parameters" in rule:
        allowed_fields.add("parameters")
    if set(rule) != allowed_fields:
        errors.append("effective rule member census is not exact")
    if rule.get("ruleset_id") != expected_ruleset_id:
        errors.append("effective rule is linked to a different ruleset id")
    if rule.get("ruleset_source") != REPOSITORY:
        errors.append("effective rule source repository is not exact")
    if rule.get("ruleset_source_type") != "Repository":
        errors.append("effective rule source type is not Repository")
    if not isinstance(rule_type, str):
        errors.append("effective rule type is absent")
        return None, errors

    semantic: dict[str, Any] = {"type": rule_type}
    parameters = rule.get("parameters")
    if rule_type == "update":
        if parameters not in (
            None,
            {"update_allows_fetch_and_merge": False},
        ):
            errors.append("effective update rule is not omitted-or-explicit false")
        semantic["parameters"] = {"update_allows_fetch_and_merge": False}
    elif rule_type == "required_status_checks":
        if not isinstance(parameters, dict) or set(parameters) != {
            "do_not_enforce_on_create",
            "required_status_checks",
            "strict_required_status_checks_policy",
        }:
            errors.append("effective status-check parameters are not exact")
            return None, errors
        contexts = parameters.get("required_status_checks")
        if not isinstance(contexts, list):
            errors.append("effective status-check contexts are not one array")
            return None, errors
        normalized_contexts: list[dict[str, Any]] = []
        for context in contexts:
            if not isinstance(context, dict) or set(context) != {
                "context",
                "integration_id",
            }:
                errors.append("effective status-check context is not exact")
                continue
            normalized_contexts.append(
                {
                    "context": context.get("context"),
                    "integration_id": context.get("integration_id"),
                }
            )
        semantic["parameters"] = {
            "do_not_enforce_on_create": parameters.get(
                "do_not_enforce_on_create"
            ),
            "strict_required_status_checks_policy": parameters.get(
                "strict_required_status_checks_policy"
            ),
            "required_status_checks": sorted(
                normalized_contexts,
                key=lambda context: str(context["context"]),
            ),
        }
    elif parameters is not None:
        errors.append("effective simple rule contains unexpected parameters")
    normalized = {
        "ruleset_id": expected_ruleset_id,
        "ruleset_source": REPOSITORY,
        "ruleset_source_type": "Repository",
        **semantic,
    }
    return normalized, errors


def effective_branch_errors(
    observation: Any,
    *,
    branch_name: str,
    expected_sha: str,
    ruleset: dict[str, Any],
) -> tuple[list[str], dict[str, Any] | None]:
    errors: list[str] = []
    if not isinstance(observation, dict):
        return ["effective branch observation is not one object"], None
    branch = observation.get("branch")
    effective_rules = observation.get("effective_rules")
    if not isinstance(branch, dict):
        errors.append(f"{branch_name}: branch response is not one object")
    else:
        if branch.get("name") != branch_name:
            errors.append(f"{branch_name}: branch name is not exact")
        commit = branch.get("commit")
        if not isinstance(commit, dict) or commit.get("sha") != expected_sha:
            errors.append(f"{branch_name}: branch commit is not the expected SHA")
        if branch.get("protected") is not True:
            errors.append(f"{branch_name}: top-level protected is not true")
    ruleset_id = ruleset.get("id")
    if not is_integer(ruleset_id) or ruleset_id <= 0:
        errors.append(f"{branch_name}: configured ruleset id is not positive")
        return errors, None
    configured_rules = ruleset.get("rules")
    if not isinstance(configured_rules, list):
        errors.append(f"{branch_name}: configured rules are not one array")
        return errors, None
    expected_by_type = {
        rule["type"]: _normalized_ruleset_rule(rule)
        for rule in configured_rules
        if isinstance(rule, dict) and isinstance(rule.get("type"), str)
    }
    if not isinstance(effective_rules, list):
        errors.append(f"{branch_name}: effective rules are not one array")
        return errors, None
    normalized_rules: list[dict[str, Any]] = []
    observed_types: list[str] = []
    for index, rule in enumerate(effective_rules):
        if not isinstance(rule, dict):
            errors.append(f"{branch_name}: effective rule {index} is malformed")
            continue
        normalized, rule_errors = _effective_semantic_rule(
            rule,
            expected_ruleset_id=ruleset_id,
        )
        errors.extend(
            f"{branch_name}: effective rule {index}: {error}"
            for error in rule_errors
        )
        if normalized is None:
            continue
        rule_type = normalized["type"]
        observed_types.append(rule_type)
        expected_semantic = expected_by_type.get(rule_type)
        observed_semantic = {
            key: value
            for key, value in normalized.items()
            if key not in {
                "ruleset_id",
                "ruleset_source",
                "ruleset_source_type",
            }
        }
        if expected_semantic != observed_semantic:
            errors.append(
                f"{branch_name}: effective rule {rule_type!r} differs "
                "from configured semantics"
            )
        normalized_rules.append(normalized)
    if (
        set(observed_types) != set(expected_by_type)
        or len(observed_types) != len(expected_by_type)
    ):
        errors.append(f"{branch_name}: effective rule census is not exact")
    normalized_observation = {
        "branch": branch_name,
        "commit_sha": expected_sha,
        "protected": True,
        "ruleset_id": ruleset_id,
        "rules": sorted(normalized_rules, key=lambda rule: rule["type"]),
    }
    return errors, normalized_observation


def activation_snapshot_errors(
    snapshot: Any,
    *,
    base_sha: str,
    sha: str,
    bootstrap_sha: str,
    journal_ruleset_ids: dict[str, int],
) -> tuple[list[str], dict[str, Any] | None]:
    if not isinstance(snapshot, dict):
        return ["activation snapshot is not one object"], None
    governance = snapshot.get("governance")
    errors = evaluate_governance(governance)
    if not isinstance(governance, dict):
        return errors, None
    rulesets = governance.get("rulesets")
    if not isinstance(rulesets, list):
        return errors, None
    by_name = {
        rule.get("name"): rule
        for rule in rulesets
        if isinstance(rule, dict) and isinstance(rule.get("name"), str)
    }
    if set(by_name) != {RULESET_NAME, RELEASE_RULESET_NAME}:
        errors.append("activation ruleset name census is not exact")
        return errors, None
    expected_ids = {
        RELEASE_RULESET_NAME: journal_ruleset_ids.get("release-ruleset"),
        RULESET_NAME: journal_ruleset_ids.get("main-ruleset"),
    }
    for name, identifier in expected_ids.items():
        if by_name[name].get("id") != identifier:
            errors.append(f"live ruleset id for {name!r} differs from journal")

    open_pull_requests = snapshot.get("open_pull_requests")
    if open_pull_requests != []:
        errors.append("open pull-request census is not zero")

    refs = snapshot.get("refs")
    expected_refs = {
        "refs/heads/main": sha,
        f"refs/heads/release/{sha}": sha,
    }
    if bootstrap_sha != sha:
        expected_refs[f"refs/heads/release/{bootstrap_sha}"] = bootstrap_sha
    if not isinstance(refs, dict) or set(refs) != set(expected_refs):
        errors.append("activation ref observation census is not exact")
    else:
        for ref_name, expected_sha in expected_refs.items():
            ref = refs.get(ref_name)
            obj = ref.get("object") if isinstance(ref, dict) else None
            if (
                not isinstance(ref, dict)
                or ref.get("ref") != ref_name
                or not isinstance(obj, dict)
                or obj.get("type") != "commit"
                or obj.get("sha") != expected_sha
            ):
                errors.append(f"activation ref {ref_name} is not the exact commit")

    commits = snapshot.get("commits")
    expected_commits = {bootstrap_sha, sha}
    if not isinstance(commits, dict) or set(commits) != expected_commits:
        errors.append("activation commit observation census is not exact")
    else:
        for commit_sha in sorted(expected_commits):
            commit = commits.get(commit_sha)
            parents = commit.get("parents") if isinstance(commit, dict) else None
            if (
                not isinstance(commit, dict)
                or commit.get("sha") != commit_sha
                or not isinstance(parents, list)
                or len(parents) != 1
                or not isinstance(parents[0], dict)
                or parents[0].get("sha") != base_sha
            ):
                errors.append(
                    f"activation commit {commit_sha} is not one direct child "
                    "of the declared base"
                )

    branches = snapshot.get("branches")
    normalized_branches: list[dict[str, Any]] = []
    expected_branches = {
        "main": by_name[RULESET_NAME],
        f"release/{sha}": by_name[RELEASE_RULESET_NAME],
    }
    if not isinstance(branches, dict) or set(branches) != set(expected_branches):
        errors.append("effective branch observation census is not exact")
    else:
        for branch_name, ruleset in expected_branches.items():
            branch_errors, normalized = effective_branch_errors(
                branches[branch_name],
                branch_name=branch_name,
                expected_sha=sha,
                ruleset=ruleset,
            )
            errors.extend(branch_errors)
            if normalized is not None:
                normalized_branches.append(normalized)

    final_check_censuses = snapshot.get("final_check_censuses")
    expected_check_subjects = {
        f"release/{bootstrap_sha}": bootstrap_sha,
        f"release/{sha}": sha,
        "main": sha,
    }
    normalized_check_censuses: list[dict[str, Any]] = []
    if (
        not isinstance(final_check_censuses, dict)
        or set(final_check_censuses) != set(expected_check_subjects)
    ):
        errors.append("final check-run census subject inventory is not exact")
    else:
        for branch_name, subject_sha in expected_check_subjects.items():
            census = final_check_censuses[branch_name]
            evaluation = evaluate_run_census(
                census,
                sha=subject_sha,
                branch=branch_name,
            )
            if evaluation.state != "success":
                detail = "; ".join(evaluation.messages) or evaluation.state
                errors.append(
                    f"final check-run census for {branch_name} is not settled: "
                    f"{detail}"
                )
                continue
            normalized_check_censuses.append(
                {
                    "branch": branch_name,
                    "subject_commit": subject_sha,
                    "workflow_runs": sorted(
                        (
                            {
                                key: record["run"].get(key)
                                for key in (
                                    "id",
                                    "path",
                                    "name",
                                    "event",
                                    "head_sha",
                                    "head_branch",
                                    "run_attempt",
                                    "status",
                                    "conclusion",
                                )
                            }
                            for record in census["runs"]
                        ),
                        key=lambda run: run["path"],
                    ),
                }
            )
    normalized = {
        "ruleset_ids": {
            "immutable_publication_candidates": by_name[
                RELEASE_RULESET_NAME
            ].get("id"),
            "main_exact_sha_fast_forward": by_name[RULESET_NAME].get("id"),
        },
        "refs": expected_refs,
        "parent_bindings": {
            bootstrap_sha: base_sha,
            sha: base_sha,
        },
        "effective_branches": sorted(
            normalized_branches,
            key=lambda branch: branch["branch"],
        ),
        "final_check_censuses": sorted(
            normalized_check_censuses,
            key=lambda census: census["branch"],
        ),
        "open_pull_request_count": 0,
    }
    return errors, normalized


def _require_exact_values(
    subject: Any,
    expected: dict[str, Any],
    label: str,
) -> list[str]:
    if not isinstance(subject, dict):
        return [f"{label} is not one object"]
    errors: list[str] = []
    for field, value in expected.items():
        if subject.get(field) != value:
            errors.append(
                f"{label}.{field} is {subject.get(field)!r}, expected {value!r}"
            )
    return errors


def evaluate_governance(snapshot: Any) -> list[str]:
    """Purely evaluate the live ruleset and repository settings."""

    if not isinstance(snapshot, dict):
        return ["governance response is not one object"]
    errors: list[str] = []
    rulesets = snapshot.get("rulesets")
    if not isinstance(rulesets, list):
        errors.append("rulesets response is not one array")
        return errors
    if len(rulesets) != 2:
        errors.append(f"repository has {len(rulesets)} rulesets; expected exactly two")
        return errors
    ruleset_ids = [
        rule.get("id") if isinstance(rule, dict) else None
        for rule in rulesets
    ]
    if any(
        not is_integer(identifier) or identifier <= 0
        for identifier in ruleset_ids
    ):
        errors.append("ruleset ids must be positive integers")
    if len(set(ruleset_ids)) != len(ruleset_ids):
        errors.append("ruleset ids must be distinct")
    rulesets_by_name = {
        rule.get("name"): rule
        for rule in rulesets
        if isinstance(rule, dict) and isinstance(rule.get("name"), str)
    }
    if set(rulesets_by_name) != {RULESET_NAME, RELEASE_RULESET_NAME}:
        errors.append(
            "ruleset name census differs from the exact main/candidate contract"
        )
        return errors
    ruleset = rulesets_by_name[RULESET_NAME]
    errors.extend(
        _require_exact_values(
            ruleset,
            {
                "name": RULESET_NAME,
                "target": "branch",
                "source_type": "Repository",
                "source": REPOSITORY,
                "enforcement": "active",
                "bypass_actors": [],
                "conditions": {
                    "ref_name": {
                        "include": ["refs/heads/main"],
                        "exclude": [],
                    }
                },
            },
            "ruleset",
        )
    )
    if not isinstance(ruleset, dict):
        return errors
    rules = ruleset.get("rules")
    if not isinstance(rules, list):
        errors.append("ruleset.rules is not one array")
    else:
        by_type: dict[str, list[dict[str, Any]]] = {}
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict) or not isinstance(rule.get("type"), str):
                errors.append(f"ruleset rule {index} is malformed")
                continue
            by_type.setdefault(rule["type"], []).append(rule)
        expected_types = {
            "deletion",
            "non_fast_forward",
            "required_linear_history",
            "required_status_checks",
        }
        if set(by_type) != expected_types:
            errors.append(
                f"ruleset rule types are {sorted(by_type)}, "
                f"expected {sorted(expected_types)}"
            )
        for rule_type in expected_types:
            if len(by_type.get(rule_type, [])) != 1:
                errors.append(
                    f"ruleset rule {rule_type!r} occurs "
                    f"{len(by_type.get(rule_type, []))} times"
                )
        for rule_type in (
            "deletion",
            "non_fast_forward",
            "required_linear_history",
        ):
            matches = by_type.get(rule_type, [])
            if len(matches) == 1 and matches[0] != {"type": rule_type}:
                errors.append(
                    f"ruleset rule {rule_type!r} contains unexpected parameters"
                )
        status_rules = by_type.get("required_status_checks", [])
        if len(status_rules) == 1:
            parameters = status_rules[0].get("parameters")
            if not isinstance(parameters, dict):
                errors.append("required_status_checks.parameters is not one object")
            else:
                if set(parameters) != {
                    "do_not_enforce_on_create",
                    "required_status_checks",
                    "strict_required_status_checks_policy",
                }:
                    errors.append(
                        "required status check parameter census is not exact"
                    )
                if parameters.get("do_not_enforce_on_create") is not False:
                    errors.append(
                        "required status checks do_not_enforce_on_create is not false"
                    )
                if parameters.get("strict_required_status_checks_policy") is not True:
                    errors.append("required status checks strict policy is not true")
                contexts = parameters.get("required_status_checks")
                if not isinstance(contexts, list):
                    errors.append("required status check contexts are not one array")
                else:
                    observed: dict[str, list[Any]] = {}
                    for index, context in enumerate(contexts):
                        if not isinstance(context, dict):
                            errors.append(
                                f"required status check context {index} is malformed"
                            )
                            continue
                        if set(context) != {"context", "integration_id"}:
                            errors.append(
                                f"required status check context {index} "
                                "member census is not exact"
                            )
                        name = context.get("context")
                        integration = context.get("integration_id")
                        if not isinstance(name, str):
                            errors.append(
                                f"required status check context {index} has no name"
                            )
                            continue
                        observed.setdefault(name, []).append(integration)
                    if set(observed) != REQUIRED_CONTEXTS:
                        errors.append(
                            "required status check context census differs from "
                            "the exact ten-context contract"
                        )
                    for context_name in REQUIRED_CONTEXTS:
                        integrations = observed.get(context_name, [])
                        if integrations != [GITHUB_ACTIONS_APP_ID]:
                            errors.append(
                                f"required context {context_name!r} integrations are "
                                f"{integrations}, expected [{GITHUB_ACTIONS_APP_ID}]"
                            )

    release_ruleset = rulesets_by_name[RELEASE_RULESET_NAME]
    errors.extend(
        _require_exact_values(
            release_ruleset,
            {
                "name": RELEASE_RULESET_NAME,
                "target": "branch",
                "source_type": "Repository",
                "source": REPOSITORY,
                "enforcement": "active",
                "bypass_actors": [],
                "conditions": {
                    "ref_name": {
                        "include": ["refs/heads/release/*"],
                        "exclude": [],
                    }
                },
            },
            "release ruleset",
        )
    )
    release_rules = (
        release_ruleset.get("rules") if isinstance(release_ruleset, dict) else None
    )
    if not isinstance(release_rules, list):
        errors.append("release ruleset.rules is not one array")
    else:
        expected_release_rules = {
            "deletion": {"type": "deletion"},
            "non_fast_forward": {"type": "non_fast_forward"},
            "required_linear_history": {"type": "required_linear_history"},
        }
        release_by_type = {
            rule.get("type"): rule
            for rule in release_rules
            if isinstance(rule, dict) and isinstance(rule.get("type"), str)
        }
        if (
            set(release_by_type) != {*expected_release_rules, "update"}
            or len(release_rules) != len(expected_release_rules) + 1
        ):
            errors.append(
                "release ruleset rule census differs from exact immutable-ref contract"
            )
        else:
            for rule_type, expected_rule in expected_release_rules.items():
                if release_by_type[rule_type] != expected_rule:
                    errors.append(
                        f"release ruleset rule {rule_type!r} differs from "
                        "the exact immutable-ref contract"
                    )
            update_rule = release_by_type["update"]
            if update_rule not in (
                {"type": "update"},
                {
                    "type": "update",
                    "parameters": {
                        "update_allows_fetch_and_merge": False,
                    },
                },
            ):
                errors.append(
                    "release ruleset rule 'update' differs from the exact "
                    "immutable-ref contract"
                )

    repository = snapshot.get("repository")
    errors.extend(
        _require_exact_values(
            repository,
            {
                "full_name": REPOSITORY,
                "default_branch": "main",
                "private": False,
                "visibility": "public",
                "archived": False,
                "disabled": False,
                "has_pull_requests": False,
            },
            "repository REST readback",
        )
    )
    merge_policy = {
        "allow_merge_commit": False,
        "allow_squash_merge": False,
        "allow_rebase_merge": True,
        "allow_auto_merge": False,
        "delete_branch_on_merge": False,
        "allow_update_branch": False,
    }
    if isinstance(repository, dict):
        for field, expected_value in merge_policy.items():
            if field in repository and repository[field] != expected_value:
                errors.append(
                    f"repository REST readback.{field} is "
                    f"{repository[field]!r}, expected {expected_value!r}"
                )
    errors.extend(
        _require_exact_values(
            snapshot.get("repository_policy"),
            {
                "read_surface": "github_graphql_v4",
                "node_id": REPOSITORY_NODE_ID,
                "full_name": REPOSITORY,
                "has_pull_requests": False,
                **merge_policy,
            },
            "repository GraphQL policy readback",
        )
    )
    errors.extend(
        _require_exact_values(
            snapshot.get("actions"),
            {
                "enabled": True,
                "allowed_actions": "selected",
                "sha_pinning_required": True,
            },
            "actions",
        )
    )
    errors.extend(
        _require_exact_values(
            snapshot.get("selected_actions"),
            {
                "github_owned_allowed": True,
                "verified_allowed": False,
                "patterns_allowed": [],
            },
            "selected_actions",
        )
    )
    errors.extend(
        _require_exact_values(
            snapshot.get("workflow_permissions"),
            {
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
            "workflow_permissions",
        )
    )
    return errors


def evaluate_candidate_governance(snapshot: Any) -> list[str]:
    """Require immutable-candidate governance before a release ref exists.

    The first activation cycle cannot require the main ruleset until the new
    push-only context has run at least once.  Candidate creation nevertheless
    requires the permanent-ref ruleset and all repository/Actions settings.
    Once the main ruleset exists, this mode validates it too.
    """

    if not isinstance(snapshot, dict):
        return ["governance response is not one object"]
    rulesets = snapshot.get("rulesets")
    if not isinstance(rulesets, list):
        return ["rulesets response is not one array"]
    names = {
        rule.get("name")
        for rule in rulesets
        if isinstance(rule, dict) and isinstance(rule.get("name"), str)
    }
    allowed = {RULESET_NAME, RELEASE_RULESET_NAME}
    if RELEASE_RULESET_NAME not in names:
        return ["immutable publication candidate ruleset is absent"]
    if not names <= allowed or len(names) != len(rulesets):
        return ["candidate governance contains an unexpected or duplicate ruleset"]
    completed = copy.deepcopy(snapshot)
    if RULESET_NAME not in names:
        completed["rulesets"].append(
            copy.deepcopy(safe_governance_snapshot()["rulesets"][0])
        )
    return evaluate_governance(completed)


def checks_receipt(
    snapshot: dict[str, Any], *, sha: str, branch: str
) -> dict[str, Any]:
    """Build a stable, redacted receipt from an already accepted snapshot."""

    workflows: list[dict[str, Any]] = []
    records = snapshot["runs"]
    for path in sorted(WORKFLOWS):
        record = next(item for item in records if item["run"]["path"] == path)
        run = record["run"]
        jobs: list[dict[str, Any]] = []
        for item in sorted(record["jobs"], key=lambda entry: entry["job"]["name"]):
            job = item["job"]
            check_run = item["check_run"]
            jobs.append(
                {
                    "id": job["id"],
                    "name": job["name"],
                    "run_attempt": job["run_attempt"],
                    "status": job["status"],
                    "conclusion": job["conclusion"],
                    "started_at": job.get("started_at"),
                    "completed_at": job.get("completed_at"),
                    "check_run_app_id": check_run["app"]["id"],
                }
            )
        workflows.append(
            {
                "id": run["id"],
                "workflow_id": run.get("workflow_id"),
                "name": run["name"],
                "path": path,
                "event": run["event"],
                "head_branch": run["head_branch"],
                "head_sha": run["head_sha"],
                "run_attempt": run["run_attempt"],
                "status": run["status"],
                "conclusion": run["conclusion"],
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
                "jobs": jobs,
            }
        )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "github_actions_exact_sha_receipt",
        "repository": REPOSITORY,
        "subject_commit": sha,
        "branch": branch,
        "event": "push",
        "workflow_count": len(WORKFLOWS),
        "job_count": len(REQUIRED_CONTEXTS),
        "workflows": workflows,
        "canonical_scientific_evidence": False,
    }


def _normalized_ruleset_rule(rule: dict[str, Any]) -> dict[str, Any]:
    """Normalize only the rule fields accepted by the live evaluator."""

    normalized: dict[str, Any] = {"type": rule["type"]}
    if rule["type"] == "update":
        normalized["parameters"] = {
            "update_allows_fetch_and_merge": False
        }
    elif rule["type"] == "required_status_checks":
        parameters = rule["parameters"]
        normalized["parameters"] = {
            "do_not_enforce_on_create": parameters["do_not_enforce_on_create"],
            "strict_required_status_checks_policy": parameters[
                "strict_required_status_checks_policy"
            ],
            "required_status_checks": sorted(
                (
                    {
                        "context": context["context"],
                        "integration_id": context["integration_id"],
                    }
                    for context in parameters["required_status_checks"]
                ),
                key=lambda context: context["context"],
            ),
        }
    return normalized


def governance_receipt(
    snapshot: dict[str, Any],
    *,
    candidate_only: bool,
    sha: str,
    phase: str,
) -> dict[str, Any]:
    """Build a stable receipt from accepted governance read-back."""

    if phase not in {"candidate", "promotion", "settlement"} or not SHA_RE.fullmatch(
        sha
    ):
        raise GitHubApiError("governance receipt phase or subject SHA is invalid")
    rulesets = {
        item["name"]: item
        for item in snapshot["rulesets"]
        if isinstance(item, dict) and item.get("name") in {
            RULESET_NAME,
            RELEASE_RULESET_NAME,
        }
    }
    names = (
        (RELEASE_RULESET_NAME,)
        if candidate_only
        else (RULESET_NAME, RELEASE_RULESET_NAME)
    )
    normalized_rulesets: list[dict[str, Any]] = []
    for name in names:
        ruleset = rulesets[name]
        normalized_rulesets.append(
            {
                "id": ruleset.get("id"),
                "name": name,
                "target": ruleset.get("target"),
                "source_type": ruleset.get("source_type"),
                "source": ruleset.get("source"),
                "enforcement": ruleset.get("enforcement"),
                "bypass_actors": ruleset.get("bypass_actors"),
                "conditions": ruleset.get("conditions"),
                "rules": sorted(
                    (
                        _normalized_ruleset_rule(rule)
                        for rule in ruleset["rules"]
                    ),
                    key=lambda rule: rule["type"],
                ),
            }
        )
    repository = snapshot["repository"]
    repository_policy = snapshot["repository_policy"]
    return {
        "schema_version": "0.1.0",
        "artifact_class": {
            "candidate": "github_candidate_governance_receipt",
            "promotion": "github_promotion_governance_receipt",
            "settlement": "github_settlement_governance_snapshot",
        }[phase],
        "repository": REPOSITORY,
        "subject_commit": sha,
        "governance_phase": phase,
        "ruleset_scope": "candidate-bootstrap" if candidate_only else "full",
        "repository_settings": {
            key: repository.get(key)
            for key in (
                "full_name",
                "default_branch",
                "private",
                "visibility",
                "archived",
                "disabled",
                "has_pull_requests",
            )
        },
        "repository_policy": {
            key: repository_policy.get(key)
            for key in (
                "read_surface",
                "node_id",
                "full_name",
                "has_pull_requests",
                "allow_merge_commit",
                "allow_squash_merge",
                "allow_rebase_merge",
                "allow_auto_merge",
                "delete_branch_on_merge",
                "allow_update_branch",
            )
        },
        "rulesets": normalized_rulesets,
        "actions": {
            key: snapshot["actions"].get(key)
            for key in ("enabled", "allowed_actions", "sha_pinning_required")
        },
        "selected_actions": {
            key: snapshot["selected_actions"].get(key)
            for key in (
                "github_owned_allowed",
                "verified_allowed",
                "patterns_allowed",
            )
        },
        "workflow_permissions": {
            key: snapshot["workflow_permissions"].get(key)
            for key in (
                "default_workflow_permissions",
                "can_approve_pull_request_reviews",
            )
        },
        "canonical_scientific_evidence": False,
    }


def _absolute_without_symlink_resolution(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(path: Path) -> None:
    """Reject any existing symlink in an absolute receipt path."""

    cursor = Path(path.anchor)
    for component in path.parts[1:]:
        cursor /= component
        try:
            mode = cursor.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise GitHubApiError(
                f"retained receipt path contains a symlink: {cursor}"
            )


def _require_private_regular_file(path: Path, label: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise GitHubApiError(f"cannot inspect {label} at {path}: {exc}") from exc
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_uid != os.getuid()
    ):
        raise GitHubApiError(
            f"{label} is not one owner-held single-link regular file: {path}"
        )


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def retain_receipt(path: Path, receipt: dict[str, Any]) -> None:
    payload = retained_json_bytes(receipt)
    path = _absolute_without_symlink_resolution(path)
    _reject_symlink_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_components(path)
    if path.exists():
        _require_private_regular_file(path, "retained receipt")
        if path.read_bytes() != payload:
            raise GitHubApiError(
                f"existing retained receipt differs from live accepted state: {path}"
            )
        print(f"GitHub retained receipt revalidated: {path}")
        return
    partial = path.with_suffix(path.suffix + ".partial")
    _reject_symlink_components(partial)
    if partial.exists():
        _require_private_regular_file(partial, "partial receipt")
        if partial.read_bytes() != payload:
            raise GitHubApiError(
                f"existing partial receipt differs from live accepted state: {partial}"
            )
    else:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(partial, flags, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    try:
        os.link(partial, path, follow_symlinks=False)
    except FileExistsError as exc:
        raise GitHubApiError(
            f"retained receipt appeared during no-overwrite publication: {path}"
        ) from exc
    partial.unlink()
    _require_private_regular_file(path, "retained receipt")
    _fsync_directory(path.parent)
    print(f"GitHub retained receipt written: {path}")


def revalidate_checks_receipt(
    path: Path,
    *,
    sha: str,
    branch: str,
) -> bytes:
    document, payload = load_strict_json_file(path, f"checks receipt for {branch}")
    snapshot = fetch_check_snapshot(sha, branch, include_jobs=True)
    evaluation = evaluate_checks(snapshot, sha=sha, branch=branch)
    if evaluation.state != "success":
        detail = "; ".join(evaluation.messages) or evaluation.state
        raise GitHubApiError(
            f"retained checks receipt no longer has a live exact census: {detail}"
        )
    expected = checks_receipt(snapshot, sha=sha, branch=branch)
    if document != expected:
        raise GitHubApiError(
            f"retained checks receipt differs from live exact census: {path}"
        )
    return payload


def load_promotion_governance_receipt(
    path: Path,
) -> tuple[dict[str, Any], bytes]:
    return load_strict_json_file(
        path,
        "final promotion-governance receipt",
    )


def revalidate_comparison_receipt(
    path: Path,
    *,
    local_evidence: Path,
    remote_evidence: Path,
    sha: str,
) -> bytes:
    _document, payload = load_strict_json_file(
        path,
        "final rehearsal comparison receipt",
    )
    comparator = Path(__file__).resolve().parents[1] / "compare_rehearsal_manifests.py"
    command = [
        sys.executable,
        os.fspath(comparator),
        "--verify-existing",
        "--local",
        os.fspath(local_evidence),
        "--remote",
        os.fspath(remote_evidence),
        "--expected-remote-source-sha256",
        CANONICAL_SOURCE_SHA256,
        "--expected-subject-commit",
        sha,
        "--output",
        os.fspath(path),
    ]
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitHubApiError(
            f"final rehearsal comparison could not be revalidated: {exc}"
        ) from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or (
            f"exit {result.returncode}"
        )
        raise GitHubApiError(
            f"final rehearsal comparison did not revalidate: {detail}"
        )
    _reloaded, reloaded_payload = load_strict_json_file(
        path,
        "final rehearsal comparison receipt",
    )
    if reloaded_payload != payload:
        raise GitHubApiError(
            "final rehearsal comparison receipt changed during revalidation"
        )
    return payload


def verify_activation_evidence(
    *,
    base_sha: str,
    bootstrap_sha: str,
    sha: str,
    mutation_journal: Path,
    bootstrap_checks_receipt: Path,
    candidate_checks_receipt: Path,
    promotion_governance_receipt: Path,
    main_checks_receipt: Path,
    comparison_receipt: Path,
    local_evidence: Path,
    remote_evidence: Path,
    output: Path,
) -> int:
    try:
        journal, journal_payload = load_strict_json_file(
            mutation_journal,
            "GitHub mutation journal",
        )
        journal_errors, journal_ruleset_ids = mutation_journal_errors(
            journal,
            base_sha=base_sha,
            bootstrap_sha=bootstrap_sha,
        )
        if journal_errors:
            raise GitHubApiError("; ".join(journal_errors))
        (
            promotion_governance_document,
            promotion_governance_payload,
        ) = load_promotion_governance_receipt(promotion_governance_receipt)
        comparison_payload = revalidate_comparison_receipt(
            comparison_receipt,
            local_evidence=local_evidence,
            remote_evidence=remote_evidence,
            sha=sha,
        )
        bootstrap_checks_payload = revalidate_checks_receipt(
            bootstrap_checks_receipt,
            sha=bootstrap_sha,
            branch=f"release/{bootstrap_sha}",
        )
        candidate_checks_payload = revalidate_checks_receipt(
            candidate_checks_receipt,
            sha=sha,
            branch=f"release/{sha}",
        )
        main_checks_payload = revalidate_checks_receipt(
            main_checks_receipt,
            sha=sha,
            branch="main",
        )
        snapshot = fetch_activation_snapshot(sha, bootstrap_sha)
        snapshot_errors, normalized = activation_snapshot_errors(
            snapshot,
            base_sha=base_sha,
            sha=sha,
            bootstrap_sha=bootstrap_sha,
            journal_ruleset_ids=journal_ruleset_ids,
        )
        if snapshot_errors or normalized is None:
            raise GitHubApiError(
                "; ".join(snapshot_errors)
                or "activation snapshot could not be normalized"
            )
        governance = snapshot["governance"]
        expected_promotion_governance = governance_receipt(
            governance,
            candidate_only=False,
            sha=sha,
            phase="promotion",
        )
        if promotion_governance_document != expected_promotion_governance:
            raise GitHubApiError(
                "retained promotion-governance receipt differs from the final "
                f"accepted governance: {promotion_governance_receipt}"
            )
        receipt = {
            "schema_version": "0.1.0",
            "artifact_class": "github_repository_activation_receipt",
            "repository": REPOSITORY,
            "api_version": API_VERSION,
            "base_commit": base_sha,
            "bootstrap_candidate_commit": bootstrap_sha,
            "subject_commit": sha,
            "mutation_journal_sha256": hashlib.sha256(
                journal_payload
            ).hexdigest(),
            "bootstrap_candidate_checks_sha256": hashlib.sha256(
                bootstrap_checks_payload
            ).hexdigest(),
            "candidate_checks_sha256": hashlib.sha256(
                candidate_checks_payload
            ).hexdigest(),
            "promotion_governance_sha256": hashlib.sha256(
                promotion_governance_payload
            ).hexdigest(),
            "main_checks_sha256": hashlib.sha256(
                main_checks_payload
            ).hexdigest(),
            "comparison_receipt_sha256": hashlib.sha256(
                comparison_payload
            ).hexdigest(),
            **normalized,
            "governance": governance_receipt(
                governance,
                candidate_only=False,
                sha=sha,
                phase="settlement",
            ),
            "canonical_scientific_evidence": False,
        }
        retain_receipt(output, receipt)
    except (GitHubApiError, OSError) as exc:
        print(f"GitHub activation evidence FAILED: {exc}", file=sys.stderr)
        return 2
    print(
        "GitHub activation evidence PASSED: mutation journal, three exact "
        "check censuses, promotion governance, remote comparison, zero open "
        "pull requests, protected exact-SHA branches, and effective rules"
    )
    return 0


def safe_check_snapshot(sha: str, branch: str) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    run_id = 100
    job_id = 1000
    for path, (workflow_name, job_names) in WORKFLOWS.items():
        run = {
            "id": run_id,
            "name": workflow_name,
            "path": path,
            "event": "push",
            "head_sha": sha,
            "head_branch": branch,
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
        }
        jobs: list[dict[str, Any]] = []
        for job_name in job_names:
            job = {
                "id": job_id,
                "name": job_name,
                "head_sha": sha,
                "head_branch": branch,
                "run_attempt": 1,
                "run_id": run_id,
                "workflow_name": workflow_name,
                "status": "completed",
                "conclusion": "success",
            }
            check_run = {
                "id": job_id,
                "name": job_name,
                "head_sha": sha,
                "status": "completed",
                "conclusion": "success",
                "app": {"id": GITHUB_ACTIONS_APP_ID},
            }
            jobs.append({"job": job, "check_run": check_run})
            job_id += 1
        records.append(
            {
                "run": run,
                "jobs_total_count": len(jobs),
                "jobs": jobs,
            }
        )
        run_id += 1
    return {"total_count": len(records), "runs": records}


def safe_governance_snapshot() -> dict[str, Any]:
    contexts = [
        {"context": context, "integration_id": GITHUB_ACTIONS_APP_ID}
        for context in sorted(REQUIRED_CONTEXTS)
    ]
    return {
        "rulesets": [
            {
                "id": 42,
                "name": RULESET_NAME,
                "target": "branch",
                "source_type": "Repository",
                "source": REPOSITORY,
                "enforcement": "active",
                "bypass_actors": [],
                "conditions": {
                    "ref_name": {
                        "include": ["refs/heads/main"],
                        "exclude": [],
                    }
                },
                "rules": [
                    {"type": "deletion"},
                    {"type": "non_fast_forward"},
                    {"type": "required_linear_history"},
                    {
                        "type": "required_status_checks",
                        "parameters": {
                            "do_not_enforce_on_create": False,
                            "required_status_checks": contexts,
                            "strict_required_status_checks_policy": True,
                        },
                    },
                ],
            },
            {
                "id": 43,
                "name": RELEASE_RULESET_NAME,
                "target": "branch",
                "source_type": "Repository",
                "source": REPOSITORY,
                "enforcement": "active",
                "bypass_actors": [],
                "conditions": {
                    "ref_name": {
                        "include": ["refs/heads/release/*"],
                        "exclude": [],
                    }
                },
                "rules": [
                    {"type": "deletion"},
                    {"type": "non_fast_forward"},
                    {"type": "required_linear_history"},
                    {"type": "update"},
                ],
            },
        ],
        "repository": {
            "full_name": REPOSITORY,
            "default_branch": "main",
            "private": False,
            "visibility": "public",
            "archived": False,
            "disabled": False,
            "has_pull_requests": False,
        },
        "repository_policy": {
            "read_surface": "github_graphql_v4",
            "node_id": REPOSITORY_NODE_ID,
            "full_name": REPOSITORY,
            "has_pull_requests": False,
            "allow_merge_commit": False,
            "allow_squash_merge": False,
            "allow_rebase_merge": True,
            "allow_auto_merge": False,
            "delete_branch_on_merge": False,
            "allow_update_branch": False,
        },
        "actions": {
            "enabled": True,
            "allowed_actions": "selected",
            "sha_pinning_required": True,
        },
        "selected_actions": {
            "github_owned_allowed": True,
            "verified_allowed": False,
            "patterns_allowed": [],
        },
        "workflow_permissions": {
            "default_workflow_permissions": "read",
            "can_approve_pull_request_reviews": False,
        },
    }


def safe_mutation_journal(base_sha: str, bootstrap_sha: str) -> dict[str, Any]:
    operations: list[dict[str, Any]] = []
    for expected in expected_mutation_operations():
        operation_id = expected["operation_id"]
        if operation_id == "release-ruleset":
            resource_id: int | None = 43
        elif operation_id == "main-ruleset":
            resource_id = 42
        elif expected["resource_required"]:
            resource_id = 100 + expected["sequence"]
        else:
            resource_id = None
        operations.append(
            {
                "sequence": expected["sequence"],
                "operation_id": operation_id,
                "request": {
                    "method": expected["method"],
                    "endpoint": expected["endpoint"],
                    "body": copy.deepcopy(expected["body"]),
                    "canonical_body_sha256": hashlib.sha256(
                        canonical_json_bytes(expected["body"])
                    ).hexdigest(),
                },
                "response": {
                    "status_code": expected["status_code"],
                    "date": "Sun, 19 Jul 2026 00:00:00 GMT",
                    "github_request_id": f"SAFE:{expected['sequence']}",
                    "api_version_selected": API_VERSION,
                    "response_body_sha256": (
                        EMPTY_SHA256
                        if expected["status_code"] == 204
                        else "d" * 64
                    ),
                    "resource_id": resource_id,
                },
            }
        )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "github_governance_mutation_journal",
        "repository": REPOSITORY,
        "api_version": API_VERSION,
        "base_commit": base_sha,
        "bootstrap_candidate_commit": bootstrap_sha,
        "operations": operations,
        "canonical_scientific_evidence": False,
    }


def safe_effective_rules(ruleset: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rule in ruleset["rules"]:
        semantic = _normalized_ruleset_rule(rule)
        if semantic["type"] == "update":
            semantic = {"type": "update"}
        records.append(
            {
                "ruleset_id": ruleset["id"],
                "ruleset_source": REPOSITORY,
                "ruleset_source_type": "Repository",
                **semantic,
            }
        )
    return records


def safe_activation_snapshot(
    sha: str,
    bootstrap_sha: str,
    base_sha: str,
) -> dict[str, Any]:
    governance = safe_governance_snapshot()
    main_ruleset = governance["rulesets"][0]
    release_ruleset = governance["rulesets"][1]
    candidate_branch = f"release/{sha}"
    refs: dict[str, Any] = {}
    for ref_name, commit in (
        ("refs/heads/main", sha),
        (f"refs/heads/{candidate_branch}", sha),
        (f"refs/heads/release/{bootstrap_sha}", bootstrap_sha),
    ):
        refs[ref_name] = {
            "ref": ref_name,
            "object": {"type": "commit", "sha": commit},
        }
    return {
        "governance": governance,
        "branches": {
            "main": {
                "branch": {
                    "name": "main",
                    "commit": {"sha": sha},
                    "protected": True,
                },
                "effective_rules": safe_effective_rules(main_ruleset),
            },
            candidate_branch: {
                "branch": {
                    "name": candidate_branch,
                    "commit": {"sha": sha},
                    "protected": True,
                },
                "effective_rules": safe_effective_rules(release_ruleset),
            },
        },
        "refs": refs,
        "commits": {
            bootstrap_sha: {
                "sha": bootstrap_sha,
                "parents": [{"sha": base_sha}],
            },
            sha: {
                "sha": sha,
                "parents": [{"sha": base_sha}],
            },
        },
        "open_pull_requests": [],
        "final_check_censuses": {
            f"release/{bootstrap_sha}": safe_check_snapshot(
                bootstrap_sha,
                f"release/{bootstrap_sha}",
            ),
            f"release/{sha}": safe_check_snapshot(
                sha,
                f"release/{sha}",
            ),
            "main": safe_check_snapshot(sha, "main"),
        },
    }


def _status_rule(snapshot: dict[str, Any]) -> dict[str, Any]:
    rules = snapshot["rulesets"][0]["rules"]
    return next(rule for rule in rules if rule["type"] == "required_status_checks")


def self_test() -> int:
    sha = "a" * 40
    other_sha = "b" * 40
    branch = f"release/{sha}"
    safe_checks = safe_check_snapshot(sha, branch)
    if evaluate_checks(safe_checks, sha=sha, branch=branch).state != "success":
        print("GitHub release self-test rejected safe checks", file=sys.stderr)
        return 1
    if evaluate_run_census(safe_checks, sha=sha, branch=branch).state != "success":
        print("GitHub release self-test rejected safe run census", file=sys.stderr)
        return 1
    safe_checks_receipt = checks_receipt(safe_checks, sha=sha, branch=branch)
    if (
        safe_checks_receipt.get("subject_commit") != sha
        or safe_checks_receipt.get("workflow_count") != 4
        or safe_checks_receipt.get("job_count") != 10
    ):
        print("GitHub release self-test built an invalid checks receipt", file=sys.stderr)
        return 1

    check_mutations: list[tuple[str, dict[str, Any], str, str]] = []
    missing = copy.deepcopy(safe_checks)
    missing["runs"].pop()
    missing["total_count"] -= 1
    check_mutations.append(("missing", missing, "pending", "has not appeared"))
    if evaluate_run_census(missing, sha=sha, branch=branch).state != "pending":
        print("GitHub release self-test did not wait for a missing run", file=sys.stderr)
        return 1

    duplicate = copy.deepcopy(safe_checks)
    duplicate["runs"].append(copy.deepcopy(duplicate["runs"][0]))
    duplicate["total_count"] += 1
    check_mutations.append(("duplicate", duplicate, "terminal", "duplicate"))

    for case_id, field, value, expected in (
        ("wrong-event", "event", "workflow_dispatch", "event"),
        ("wrong-branch", "head_branch", "main", "head_branch"),
        ("wrong-sha", "head_sha", other_sha, "head_sha"),
        ("wrong-attempt", "run_attempt", 2, "run_attempt"),
    ):
        candidate = copy.deepcopy(safe_checks)
        candidate["runs"][0]["run"][field] = value
        check_mutations.append((case_id, candidate, "terminal", expected))
        if case_id == "wrong-event" and evaluate_run_census(
            candidate, sha=sha, branch=branch
        ).state != "terminal":
            print(
                "GitHub release self-test run census accepted wrong event",
                file=sys.stderr,
            )
            return 1

    skipped = copy.deepcopy(safe_checks)
    skipped["runs"][0]["run"]["conclusion"] = "skipped"
    check_mutations.append(("skipped", skipped, "terminal", "skipped"))

    neutral = copy.deepcopy(safe_checks)
    neutral["runs"][0]["jobs"][0]["job"]["conclusion"] = "neutral"
    check_mutations.append(("neutral", neutral, "terminal", "neutral"))

    failure = copy.deepcopy(safe_checks)
    failure["runs"][0]["jobs"][0]["check_run"]["conclusion"] = "failure"
    check_mutations.append(("failure", failure, "terminal", "failure"))

    wrong_app = copy.deepcopy(safe_checks)
    wrong_app["runs"][0]["jobs"][0]["check_run"]["app"]["id"] = 1
    check_mutations.append(("wrong-app", wrong_app, "terminal", "app id"))

    for case_id, candidate, expected_state, expected_text in check_mutations:
        evaluation = evaluate_checks(candidate, sha=sha, branch=branch)
        if evaluation.state != expected_state or not any(
            expected_text in message for message in evaluation.messages
        ):
            print(
                f"GitHub release self-test {case_id}: expected "
                f"{expected_state}/{expected_text!r}, got "
                f"{evaluation.state}/{evaluation.messages}",
                file=sys.stderr,
            )
            return 1

    safe_governance = safe_governance_snapshot()
    if evaluate_governance(safe_governance):
        print("GitHub release self-test rejected safe governance", file=sys.stderr)
        return 1
    explicit_false_governance = copy.deepcopy(safe_governance)
    explicit_false_governance["rulesets"][1]["rules"][3]["parameters"] = {
        "update_allows_fetch_and_merge": False,
    }
    if evaluate_governance(explicit_false_governance):
        print(
            "GitHub release self-test rejected explicit-false update governance",
            file=sys.stderr,
        )
        return 1
    candidate_governance = copy.deepcopy(safe_governance)
    candidate_governance["rulesets"] = [candidate_governance["rulesets"][1]]
    if evaluate_candidate_governance(candidate_governance):
        print(
            "GitHub release self-test rejected safe candidate governance",
            file=sys.stderr,
        )
        return 1
    safe_candidate_receipt = governance_receipt(
        candidate_governance,
        candidate_only=True,
        sha=sha,
        phase="candidate",
    )
    if (
        safe_candidate_receipt.get("artifact_class")
        != "github_candidate_governance_receipt"
        or safe_candidate_receipt.get("subject_commit") != sha
        or len(safe_candidate_receipt.get("rulesets", [])) != 1
    ):
        print(
            "GitHub release self-test built an invalid governance receipt",
            file=sys.stderr,
        )
        return 1
    safe_promotion_receipt = governance_receipt(
        safe_governance,
        candidate_only=False,
        sha=sha,
        phase="promotion",
    )
    if (
        safe_promotion_receipt.get("artifact_class")
        != "github_promotion_governance_receipt"
        or safe_promotion_receipt.get("governance_phase") != "promotion"
        or safe_promotion_receipt.get("ruleset_scope") != "full"
        or len(safe_promotion_receipt.get("rulesets", [])) != 2
    ):
        print(
            "GitHub release self-test built an invalid promotion receipt",
            file=sys.stderr,
        )
        return 1
    explicit_false_receipt = governance_receipt(
        explicit_false_governance,
        candidate_only=False,
        sha=sha,
        phase="promotion",
    )
    if explicit_false_receipt != safe_promotion_receipt:
        print(
            "GitHub release self-test did not normalize equivalent update rules",
            file=sys.stderr,
        )
        return 1

    governance_mutations: list[tuple[str, dict[str, Any], str]] = []
    absent = copy.deepcopy(safe_governance)
    absent["rulesets"] = []
    governance_mutations.append(("absent-ruleset", absent, "expected exactly two"))

    bypass = copy.deepcopy(safe_governance)
    bypass["rulesets"][0]["bypass_actors"] = [
        {"actor_id": 1, "actor_type": "User", "bypass_mode": "always"}
    ]
    governance_mutations.append(("bypass", bypass, "bypass_actors"))

    release_bypass = copy.deepcopy(safe_governance)
    release_bypass["rulesets"][1]["bypass_actors"] = [
        {"actor_id": 1, "actor_type": "User", "bypass_mode": "always"}
    ]
    governance_mutations.append(
        ("release-bypass", release_bypass, "release ruleset.bypass_actors")
    )

    release_rewrite = copy.deepcopy(safe_governance)
    release_rewrite["rulesets"][1]["rules"].pop()
    governance_mutations.append(
        ("release-rule-drift", release_rewrite, "release ruleset rule census")
    )

    missing_ruleset_id = copy.deepcopy(safe_governance)
    missing_ruleset_id["rulesets"][0].pop("id")
    governance_mutations.append(
        ("missing-ruleset-id", missing_ruleset_id, "positive integers")
    )

    duplicate_ruleset_id = copy.deepcopy(safe_governance)
    duplicate_ruleset_id["rulesets"][1]["id"] = duplicate_ruleset_id["rulesets"][
        0
    ]["id"]
    governance_mutations.append(
        ("duplicate-ruleset-id", duplicate_ruleset_id, "must be distinct")
    )

    release_fetch_merge = copy.deepcopy(safe_governance)
    release_fetch_merge["rulesets"][1]["rules"][3]["parameters"] = {
        "update_allows_fetch_and_merge": True,
    }
    governance_mutations.append(
        (
            "release-fetch-merge",
            release_fetch_merge,
            "release ruleset rule 'update' differs",
        )
    )

    candidate_absent = copy.deepcopy(candidate_governance)
    candidate_absent["rulesets"] = []
    governance_mutations.append(
        (
            "candidate-ruleset-absent",
            candidate_absent,
            "immutable publication candidate ruleset is absent",
        )
    )

    non_strict = copy.deepcopy(safe_governance)
    _status_rule(non_strict)["parameters"][
        "strict_required_status_checks_policy"
    ] = False
    governance_mutations.append(("strict-false", non_strict, "strict policy"))

    context_drift = copy.deepcopy(safe_governance)
    _status_rule(context_drift)["parameters"]["required_status_checks"].pop()
    governance_mutations.append(("context-drift", context_drift, "context census"))

    merge_drift = copy.deepcopy(safe_governance)
    merge_drift["repository_policy"]["allow_merge_commit"] = True
    governance_mutations.append(
        ("merge-settings-drift", merge_drift, "allow_merge_commit")
    )

    identity_drift = copy.deepcopy(safe_governance)
    identity_drift["repository"]["visibility"] = "private"
    governance_mutations.append(
        ("repository-identity-drift", identity_drift, "visibility")
    )

    pull_requests_enabled = copy.deepcopy(safe_governance)
    pull_requests_enabled["repository"]["has_pull_requests"] = True
    governance_mutations.append(
        (
            "pull-requests-enabled",
            pull_requests_enabled,
            "has_pull_requests",
        )
    )

    actions_drift = copy.deepcopy(safe_governance)
    actions_drift["actions"]["sha_pinning_required"] = False
    governance_mutations.append(
        ("actions-settings-drift", actions_drift, "sha_pinning_required")
    )

    selection_drift = copy.deepcopy(safe_governance)
    selection_drift["selected_actions"]["verified_allowed"] = True
    governance_mutations.append(
        ("selected-actions-drift", selection_drift, "verified_allowed")
    )

    token_drift = copy.deepcopy(safe_governance)
    token_drift["workflow_permissions"]["can_approve_pull_request_reviews"] = True
    governance_mutations.append(
        ("workflow-token-drift", token_drift, "can_approve_pull_request_reviews")
    )

    for case_id, candidate, expected_text in governance_mutations:
        errors = (
            evaluate_candidate_governance(candidate)
            if case_id == "candidate-ruleset-absent"
            else evaluate_governance(candidate)
        )
        if not any(expected_text in error for error in errors):
            print(
                f"GitHub release self-test {case_id}: expected {expected_text!r}, "
                f"got {errors}",
                file=sys.stderr,
            )
            return 1

    base_sha = "c" * 40
    bootstrap_sha = "b" * 40
    safe_journal = safe_mutation_journal(base_sha, bootstrap_sha)
    journal_errors, journal_ruleset_ids = mutation_journal_errors(
        safe_journal,
        base_sha=base_sha,
        bootstrap_sha=bootstrap_sha,
    )
    if journal_errors or journal_ruleset_ids != {
        "release-ruleset": 43,
        "main-ruleset": 42,
    }:
        print(
            f"GitHub release self-test rejected safe mutation journal: "
            f"{journal_errors}/{journal_ruleset_ids}",
            file=sys.stderr,
        )
        return 1
    journal_mutations: list[tuple[str, dict[str, Any], str]] = []
    wrong_sequence = copy.deepcopy(safe_journal)
    wrong_sequence["operations"][1]["sequence"] = 99
    journal_mutations.append(("sequence", wrong_sequence, "contiguous"))
    wrong_body = copy.deepcopy(safe_journal)
    wrong_body["operations"][4]["request"]["body"]["has_pull_requests"] = True
    journal_mutations.append(("request-body", wrong_body, "request body"))
    wrong_status = copy.deepcopy(safe_journal)
    wrong_status["operations"][5]["response"]["status_code"] = 200
    journal_mutations.append(("http-status", wrong_status, "HTTP status"))
    wrong_operation = copy.deepcopy(safe_journal)
    wrong_operation["operations"][0]["operation_id"] = "unknown"
    journal_mutations.append(
        ("operation-id", wrong_operation, "operation identity")
    )
    duplicate_journal_ids = copy.deepcopy(safe_journal)
    duplicate_journal_ids["operations"][-1]["response"]["resource_id"] = 43
    journal_mutations.append(
        ("ruleset-id", duplicate_journal_ids, "not distinct")
    )
    for case_id, candidate, expected_text in journal_mutations:
        errors, _identifiers = mutation_journal_errors(
            candidate,
            base_sha=base_sha,
            bootstrap_sha=bootstrap_sha,
        )
        if not any(expected_text in error for error in errors):
            print(
                f"GitHub release self-test journal {case_id}: expected "
                f"{expected_text!r}, got {errors}",
                file=sys.stderr,
            )
            return 1

    safe_activation = safe_activation_snapshot(sha, bootstrap_sha, base_sha)
    activation_errors, normalized_activation = activation_snapshot_errors(
        safe_activation,
        base_sha=base_sha,
        sha=sha,
        bootstrap_sha=bootstrap_sha,
        journal_ruleset_ids=journal_ruleset_ids,
    )
    if activation_errors or normalized_activation is None:
        print(
            f"GitHub release self-test rejected safe activation: "
            f"{activation_errors}",
            file=sys.stderr,
        )
        return 1
    activation_mutations: list[tuple[str, dict[str, Any], dict[str, int], str]] = []
    wrong_ref = copy.deepcopy(safe_activation)
    wrong_ref["refs"]["refs/heads/main"]["object"]["sha"] = other_sha
    activation_mutations.append(
        ("wrong-ref", wrong_ref, journal_ruleset_ids, "activation ref")
    )
    wrong_parent = copy.deepcopy(safe_activation)
    wrong_parent["commits"][sha]["parents"][0]["sha"] = other_sha
    activation_mutations.append(
        ("wrong-parent", wrong_parent, journal_ruleset_ids, "direct child")
    )
    extra_parent = copy.deepcopy(safe_activation)
    extra_parent["commits"][bootstrap_sha]["parents"].append(
        {"sha": other_sha}
    )
    activation_mutations.append(
        ("extra-parent", extra_parent, journal_ruleset_ids, "direct child")
    )
    unprotected = copy.deepcopy(safe_activation)
    unprotected["branches"]["main"]["branch"]["protected"] = False
    activation_mutations.append(
        ("unprotected", unprotected, journal_ruleset_ids, "protected")
    )
    extra_effective = copy.deepcopy(safe_activation)
    extra_effective["branches"]["main"]["effective_rules"].append(
        copy.deepcopy(
            extra_effective["branches"]["main"]["effective_rules"][0]
        )
    )
    activation_mutations.append(
        ("extra-effective", extra_effective, journal_ruleset_ids, "census")
    )
    wrong_effective_app = copy.deepcopy(safe_activation)
    status_rule = next(
        rule
        for rule in wrong_effective_app["branches"]["main"]["effective_rules"]
        if rule["type"] == "required_status_checks"
    )
    status_rule["parameters"]["required_status_checks"][0]["integration_id"] = 1
    activation_mutations.append(
        (
            "effective-app",
            wrong_effective_app,
            journal_ruleset_ids,
            "differs from configured",
        )
    )
    open_pr = copy.deepcopy(safe_activation)
    open_pr["open_pull_requests"] = [{"number": 1}]
    activation_mutations.append(
        ("open-pr", open_pr, journal_ruleset_ids, "not zero")
    )
    active_run = copy.deepcopy(safe_activation)
    active_run["final_check_censuses"]["main"]["runs"][0]["run"][
        "status"
    ] = "in_progress"
    active_run["final_check_censuses"]["main"]["runs"][0]["run"][
        "conclusion"
    ] = None
    activation_mutations.append(
        ("active-run", active_run, journal_ruleset_ids, "not settled")
    )
    wrong_live_id = dict(journal_ruleset_ids)
    wrong_live_id["main-ruleset"] = 99
    activation_mutations.append(
        ("live-id", safe_activation, wrong_live_id, "differs from journal")
    )
    for case_id, candidate, identifiers, expected_text in activation_mutations:
        errors, _normalized = activation_snapshot_errors(
            candidate,
            base_sha=base_sha,
            sha=sha,
            bootstrap_sha=bootstrap_sha,
            journal_ruleset_ids=identifiers,
        )
        if not any(expected_text in error for error in errors):
            print(
                f"GitHub release self-test activation {case_id}: expected "
                f"{expected_text!r}, got {errors}",
                file=sys.stderr,
            )
            return 1

    receipt_mutations = 0
    with tempfile.TemporaryDirectory(
        prefix=".odeya-github-receipt-self-test-",
        dir=Path.cwd(),
    ) as temp:
        root = Path(temp)
        receipt = checks_receipt(safe_checks, sha=sha, branch=branch)
        retained = root / "retained.json"
        with contextlib.redirect_stdout(io.StringIO()):
            retain_receipt(retained, receipt)
            retain_receipt(retained, receipt)

        drifted = copy.deepcopy(receipt)
        drifted["subject_commit"] = other_sha
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                retain_receipt(retained, drifted)
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a drifted retained receipt",
                file=sys.stderr,
            )
            return 1

        target = root / "target.json"
        target.write_text("{}\n", encoding="utf-8")
        symlink = root / "symlink.json"
        symlink.symlink_to(target)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                retain_receipt(symlink, receipt)
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a symlinked retained receipt",
                file=sys.stderr,
            )
            return 1

        symlink_parent = root / "symlink-parent"
        symlink_parent.symlink_to(root, target_is_directory=True)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                retain_receipt(symlink_parent / "nested.json", receipt)
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a symlinked receipt parent",
                file=sys.stderr,
            )
            return 1

        hardlink = root / "hardlink.json"
        os.link(target, hardlink)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                retain_receipt(hardlink, receipt)
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a hard-linked retained receipt",
                file=sys.stderr,
            )
            return 1

        try:
            load_strict_json_file(hardlink, "hard-linked input receipt")
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a hard-linked input receipt",
                file=sys.stderr,
            )
            return 1

        noncanonical = root / "noncanonical.json"
        noncanonical.write_text('{"value":1}\n', encoding="utf-8")
        try:
            load_strict_json_file(noncanonical, "noncanonical input receipt")
        except GitHubApiError:
            receipt_mutations += 1
        else:
            print(
                "GitHub release self-test accepted input receipt byte drift",
                file=sys.stderr,
            )
            return 1

    api_identity_mutations = 0
    if matched_ruleset_detail({"id": 42}, {"id": 42}) != {"id": 42}:
        print(
            "GitHub release self-test rejected a matching ruleset detail",
            file=sys.stderr,
        )
        return 1
    try:
        matched_ruleset_detail({"id": 42}, {"id": 43})
    except GitHubApiError:
        api_identity_mutations += 1
    else:
        print(
            "GitHub release self-test accepted a mismatched ruleset detail",
            file=sys.stderr,
        )
        return 1
    safe_policy_graphql = {
        "data": {
            "repository": {
                "id": REPOSITORY_NODE_ID,
                "nameWithOwner": REPOSITORY,
                "hasPullRequestsEnabled": False,
                "mergeCommitAllowed": False,
                "squashMergeAllowed": False,
                "rebaseMergeAllowed": True,
                "autoMergeAllowed": False,
                "deleteBranchOnMerge": False,
                "allowUpdateBranch": False,
            }
        }
    }
    if (
        repository_policy_from_graphql(safe_policy_graphql)
        != safe_governance["repository_policy"]
    ):
        print(
            "GitHub release self-test rejected a matching GraphQL policy",
            file=sys.stderr,
        )
        return 1
    for mutate_policy in (
        lambda document: document["data"]["repository"].__setitem__(
            "id", "wrong-node"
        ),
        lambda document: document["data"]["repository"].pop(
            "mergeCommitAllowed"
        ),
        lambda document: document["data"]["repository"].__setitem__(
            "allowUpdateBranch", None
        ),
    ):
        candidate_policy = copy.deepcopy(safe_policy_graphql)
        mutate_policy(candidate_policy)
        try:
            repository_policy_from_graphql(candidate_policy)
        except GitHubApiError:
            api_identity_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a malformed GraphQL policy",
                file=sys.stderr,
            )
            return 1
    for invalid_query, invalid_variables in (
        (
            "mutation Forbidden { __typename }",
            {"owner": REPOSITORY_OWNER, "name": REPOSITORY_NAME},
        ),
        (
            REPOSITORY_POLICY_QUERY,
            {"owner": "different-owner", "name": REPOSITORY_NAME},
        ),
    ):
        try:
            gh_graphql_json(invalid_query, **invalid_variables)
        except GitHubApiError:
            api_identity_mutations += 1
        else:
            print(
                "GitHub release self-test accepted a noncanonical GraphQL query",
                file=sys.stderr,
            )
            return 1

    pr_census_mutations = 0
    normalized_prs = pull_requests_from_issue_page(
        [
            {"number": 9, "pull_request": {"url": "ignored"}},
            {"number": 3},
            {"number": 2, "pull_request": {"url": "ignored"}},
        ]
    )
    if normalized_prs != [{"number": 2}, {"number": 9}]:
        print(
            "GitHub release self-test mis-normalized the issue-page PR census",
            file=sys.stderr,
        )
        return 1
    for malformed_page in (
        {},
        [None],
        [{"number": 0, "pull_request": {}}],
        [
            {"number": 1, "pull_request": {}},
            {"number": 1, "pull_request": {}},
        ],
        [{"number": number} for number in range(100)],
    ):
        try:
            pull_requests_from_issue_page(malformed_page)
        except GitHubApiError:
            pr_census_mutations += 1
        else:
            print(
                "GitHub release self-test accepted an inexact issue-page "
                "PR census",
                file=sys.stderr,
            )
            return 1

    cli_mutations = 0
    if not valid_activation_identities(base_sha, bootstrap_sha, sha):
        print(
            "GitHub release self-test rejected distinct activation identities",
            file=sys.stderr,
        )
        return 1
    for identities in (
        (base_sha, base_sha, sha),
        (base_sha, bootstrap_sha, bootstrap_sha),
    ):
        if valid_activation_identities(*identities):
            print(
                "GitHub release self-test accepted collapsed activation identities",
                file=sys.stderr,
            )
            return 1
        cli_mutations += 1
    if not valid_check_branch(sha, "main") or not valid_check_branch(sha, branch):
        print("GitHub release self-test rejected an exact check branch", file=sys.stderr)
        return 1
    for invalid_branch in (f"release/{other_sha}", "foo/.bar"):
        if valid_check_branch(sha, invalid_branch):
            print(
                f"GitHub release self-test accepted check branch {invalid_branch!r}",
                file=sys.stderr,
            )
            return 1
        cli_mutations += 1
    for timeout, poll in ((float("nan"), 5.0), (900.0, float("inf"))):
        if valid_polling_bounds(timeout, poll):
            print(
                "GitHub release self-test accepted non-finite polling bounds",
                file=sys.stderr,
            )
            return 1
        cli_mutations += 1

    print(
        "GitHub release verifier self-test PASSED — "
        f"{len(check_mutations)} check and "
        f"{len(governance_mutations)} governance and "
        f"{receipt_mutations} receipt, "
        f"{api_identity_mutations} API-identity, and "
        f"{pr_census_mutations} disabled-PR-census, {cli_mutations} CLI, "
        f"{len(journal_mutations)} journal, and "
        f"{len(activation_mutations)} activation mutations rejected"
    )
    return 0


def valid_check_branch(sha: str, branch: str) -> bool:
    return branch in {"main", f"release/{sha}"}


def valid_activation_identities(
    base_sha: str,
    bootstrap_sha: str,
    sha: str,
) -> bool:
    identities = (base_sha, bootstrap_sha, sha)
    return all(SHA_RE.fullmatch(identity) for identity in identities) and (
        len(set(identities)) == len(identities)
    )


def valid_polling_bounds(timeout_seconds: float, poll_seconds: float) -> bool:
    return (
        math.isfinite(timeout_seconds)
        and timeout_seconds > 0
        and math.isfinite(poll_seconds)
        and 0 < poll_seconds <= 60
    )


def verify_checks(
    *,
    sha: str,
    branch: str,
    timeout_seconds: float,
    poll_seconds: float,
    output: Path | None,
) -> int:
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            run_snapshot = fetch_check_snapshot(
                sha, branch, include_jobs=False
            )
        except GitHubApiError as exc:
            print(f"GitHub release checks FAILED: {exc}", file=sys.stderr)
            return 2
        run_evaluation = evaluate_run_census(
            run_snapshot, sha=sha, branch=branch
        )
        if run_evaluation.state == "terminal":
            print("GitHub release checks FAILED", file=sys.stderr)
            for message in run_evaluation.messages:
                print(f"- {message}", file=sys.stderr)
            return 1
        if run_evaluation.state == "success":
            try:
                snapshot = fetch_check_snapshot(sha, branch, include_jobs=True)
            except GitHubApiError as exc:
                print(f"GitHub release checks FAILED: {exc}", file=sys.stderr)
                return 2
            evaluation = evaluate_checks(snapshot, sha=sha, branch=branch)
        else:
            evaluation = run_evaluation
        if evaluation.state == "success":
            if output is not None:
                try:
                    retain_receipt(
                        output,
                        checks_receipt(snapshot, sha=sha, branch=branch),
                    )
                except (GitHubApiError, OSError) as exc:
                    print(f"GitHub release receipt FAILED: {exc}", file=sys.stderr)
                    return 2
            print(
                f"GitHub release checks PASSED for {sha} on {branch}: "
                f"{len(WORKFLOWS)} workflows, {len(REQUIRED_CONTEXTS)} jobs"
            )
            return 0
        if evaluation.state == "terminal":
            print("GitHub release checks FAILED", file=sys.stderr)
            for message in evaluation.messages:
                print(f"- {message}", file=sys.stderr)
            return 1
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print("GitHub release checks TIMED OUT", file=sys.stderr)
            for message in evaluation.messages:
                print(f"- {message}", file=sys.stderr)
            return 1
        time.sleep(min(poll_seconds, remaining, 60.0))


def verify_governance(
    *,
    candidate_only: bool = False,
    output: Path | None = None,
    sha: str | None = None,
    receipt_phase: str | None = None,
) -> int:
    if output is not None and (sha is None or receipt_phase is None):
        print(
            "GitHub governance receipt FAILED: --sha and receipt phase "
            "are required with --output",
            file=sys.stderr,
        )
        return 2
    if candidate_only and receipt_phase not in {None, "candidate"}:
        print(
            "GitHub candidate governance receipt FAILED: phase must be candidate",
            file=sys.stderr,
        )
        return 2
    try:
        snapshot = fetch_governance_snapshot()
    except GitHubApiError as exc:
        print(f"GitHub governance verification FAILED: {exc}", file=sys.stderr)
        return 2
    errors = (
        evaluate_candidate_governance(snapshot)
        if candidate_only
        else evaluate_governance(snapshot)
    )
    if errors:
        print("GitHub governance verification FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if output is not None:
        try:
            retain_receipt(
                output,
                governance_receipt(
                    snapshot,
                    candidate_only=candidate_only,
                    sha=sha or "",
                    phase=receipt_phase or "",
                ),
            )
        except (GitHubApiError, OSError) as exc:
            print(f"GitHub governance receipt FAILED: {exc}", file=sys.stderr)
            return 2
    if candidate_only:
        print(
            "GitHub candidate governance verification PASSED: immutable "
            "no-bypass release refs and exact repository/Actions settings"
        )
    else:
        print(
            "GitHub governance verification PASSED: active no-bypass main and "
            "immutable-candidate rulesets with "
            f"{len(REQUIRED_CONTEXTS)} app-pinned checks"
        )
    return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run pure known-bad fixtures without GitHub access",
    )
    subparsers = parser.add_subparsers(dest="mode")
    checks = subparsers.add_parser("checks", help="poll exact GitHub Actions runs")
    checks.add_argument("--sha", required=True)
    checks.add_argument("--branch", required=True)
    checks.add_argument("--timeout-seconds", type=float, default=900.0)
    checks.add_argument("--poll-seconds", type=float, default=5.0)
    checks.add_argument("--output", type=Path)
    governance = subparsers.add_parser(
        "governance", help="verify live repository governance"
    )
    governance.add_argument("--output", type=Path)
    governance.add_argument("--sha")
    governance.add_argument(
        "--receipt-phase",
        choices=("candidate", "promotion"),
    )
    candidate_governance = subparsers.add_parser(
        "candidate-governance",
        help="verify pre-candidate immutable-ref and account governance",
    )
    candidate_governance.add_argument("--output", type=Path)
    candidate_governance.add_argument("--sha")
    activation = subparsers.add_parser(
        "activation-evidence",
        help="retain final effective GitHub activation evidence",
    )
    activation.add_argument("--base-sha", required=True)
    activation.add_argument("--bootstrap-sha", required=True)
    activation.add_argument("--sha", required=True)
    activation.add_argument("--mutation-journal", required=True, type=Path)
    activation.add_argument(
        "--bootstrap-checks-receipt",
        required=True,
        type=Path,
    )
    activation.add_argument(
        "--candidate-checks-receipt",
        required=True,
        type=Path,
    )
    activation.add_argument(
        "--promotion-governance-receipt",
        required=True,
        type=Path,
    )
    activation.add_argument("--main-checks-receipt", required=True, type=Path)
    activation.add_argument("--comparison-receipt", required=True, type=Path)
    activation.add_argument("--local-evidence", required=True, type=Path)
    activation.add_argument("--remote-evidence", required=True, type=Path)
    activation.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if arguments.self_test:
        if arguments.mode is not None:
            print("--self-test cannot be combined with a network mode", file=sys.stderr)
            return 2
        return self_test()
    if arguments.mode == "governance":
        if arguments.sha is not None and not SHA_RE.fullmatch(arguments.sha):
            print("--sha must be one lowercase forty-character SHA", file=sys.stderr)
            return 2
        return verify_governance(
            output=arguments.output,
            sha=arguments.sha,
            receipt_phase=arguments.receipt_phase,
        )
    if arguments.mode == "candidate-governance":
        if arguments.sha is not None and not SHA_RE.fullmatch(arguments.sha):
            print("--sha must be one lowercase forty-character SHA", file=sys.stderr)
            return 2
        return verify_governance(
            candidate_only=True,
            output=arguments.output,
            sha=arguments.sha,
            receipt_phase="candidate",
        )
    if arguments.mode == "activation-evidence":
        if not valid_activation_identities(
            arguments.base_sha,
            arguments.bootstrap_sha,
            arguments.sha,
        ):
            print(
                "activation base, bootstrap, and final SHAs must be pairwise "
                "distinct lowercase forty-character values",
                file=sys.stderr,
            )
            return 2
        return verify_activation_evidence(
            base_sha=arguments.base_sha,
            bootstrap_sha=arguments.bootstrap_sha,
            sha=arguments.sha,
            mutation_journal=arguments.mutation_journal,
            bootstrap_checks_receipt=arguments.bootstrap_checks_receipt,
            candidate_checks_receipt=arguments.candidate_checks_receipt,
            promotion_governance_receipt=arguments.promotion_governance_receipt,
            main_checks_receipt=arguments.main_checks_receipt,
            comparison_receipt=arguments.comparison_receipt,
            local_evidence=arguments.local_evidence,
            remote_evidence=arguments.remote_evidence,
            output=arguments.output,
        )
    if arguments.mode == "checks":
        if not SHA_RE.fullmatch(arguments.sha):
            print("--sha must be one lowercase forty-character SHA", file=sys.stderr)
            return 2
        if not valid_check_branch(arguments.sha, arguments.branch):
            print(
                "--branch must be main or release/<the exact --sha>",
                file=sys.stderr,
            )
            return 2
        if not valid_polling_bounds(
            arguments.timeout_seconds,
            arguments.poll_seconds,
        ):
            print(
                "polling bounds must be finite; timeout positive and poll in (0, 60]",
                file=sys.stderr,
            )
            return 2
        return verify_checks(
            sha=arguments.sha,
            branch=arguments.branch,
            timeout_seconds=arguments.timeout_seconds,
            poll_seconds=arguments.poll_seconds,
            output=arguments.output,
        )
    print(
        "choose --self-test, checks, candidate-governance, governance, "
        "or activation-evidence",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
