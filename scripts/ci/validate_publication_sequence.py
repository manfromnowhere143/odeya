#!/usr/bin/env python3
"""Refuse any Odeya publication update that is not one exact candidate.

GitHub attaches required checks to the tip of a pushed range.  It does not
give every intermediate commit its own check suite.  Odeya therefore admits
one single-parent direct child of the observed remote ``main`` at a time.  The
same rehearsed SHA is first created at ``release/<sha>`` and can then
fast-forward ``main`` without a merge, squash, rebase, or reconstructed tree.

The local hook uses the update validator.  The push-only publication workflow
uses the CI-event validator.  The retained rehearsal loader is shared with the
local/remote comparison tool, so a plausible-looking manifest is not enough:
all retained files and the nested release manifest are rehashed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from compare_rehearsal_manifests import EvidenceError, load_manifest  # noqa: E402
from write_rehearsal_evidence_manifest import PROFILE_PATHS  # noqa: E402


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ZERO_SHA = "0" * 40
MAIN_REF = "refs/heads/main"
RELEASE_PREFIX = "refs/heads/release/"
CANONICAL_REPOSITORY = "manfromnowhere143/odeya"
CANONICAL_SOURCE = "https://github.com/manfromnowhere143/odeya"

# Git can redirect graph and object reads through both environment variables
# and replacement objects.  These variables are removed only for inspection
# subprocesses; the outer push retains its credential helper.
GIT_ENVIRONMENT_TO_REMOVE = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_ATTR_SOURCE",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
    "GIT_CURL_VERBOSE",
    "GIT_DIR",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_EXEC_PATH",
    "GIT_EXTERNAL_DIFF",
    "GIT_GRAFT_FILE",
    "GIT_IMPLICIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PAGER",
    "GIT_PREFIX",
    "GIT_QUARANTINE_PATH",
    "GIT_REPLACE_REF_BASE",
    "GIT_SHALLOW_FILE",
    "GIT_SSL_CAINFO",
    "GIT_SSL_CAPATH",
    "GIT_SSL_CERT",
    "GIT_SSL_CERT_PASSWORD_PROTECTED",
    "GIT_SSL_CIPHER_LIST",
    "GIT_SSL_KEY",
    "GIT_SSL_NO_VERIFY",
    "GIT_SSL_VERSION",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSH_VARIANT",
    "GIT_TRACE",
    "GIT_TRANSPORT_HELPER_DEBUG",
    "GIT_WORK_TREE",
)


class DuplicateKeyError(ValueError):
    """A JSON object contained a repeated member."""


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def decode_json(path: Path, description: str) -> dict[str, Any]:
    try:
        document = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise ValueError(f"cannot decode {description}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"{description} is not one JSON object")
    return document


def sanitized_git_environment(
    source: dict[str, str] | None = None,
) -> dict[str, str]:
    environment = dict(os.environ if source is None else source)
    for variable in GIT_ENVIRONMENT_TO_REMOVE:
        environment.pop(variable, None)
    for variable in tuple(environment):
        if variable.startswith(
            ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_", "GIT_TRACE_", "GIT_TRACE2")
        ):
            environment.pop(variable, None)
    environment["GIT_ATTR_NOSYSTEM"] = "1"
    environment["GIT_CONFIG_COUNT"] = "0"
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    environment["GIT_PAGER"] = "cat"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return environment


def git_result(
    repo: Path,
    *arguments: str,
    text: bool = True,
) -> subprocess.CompletedProcess[Any]:
    return subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *arguments],
        capture_output=True,
        text=text,
        check=False,
        env=sanitized_git_environment(),
    )


def git_output(repo: Path, *arguments: str) -> str:
    result = git_result(repo, *arguments)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git failure"
        raise RuntimeError(f"git {' '.join(arguments)}: {detail}")
    return result.stdout.strip()


def git_bytes(repo: Path, *arguments: str) -> bytes:
    result = git_result(repo, *arguments, text=False)
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        raise RuntimeError(
            f"git {' '.join(arguments)}: {stderr or stdout or 'unknown Git failure'}"
        )
    return result.stdout


def git_is_ancestor(repo: Path, older: str, newer: str) -> bool:
    result = git_result(repo, "merge-base", "--is-ancestor", older, newer)
    if result.returncode not in {0, 1}:
        raise RuntimeError("git merge-base --is-ancestor could not evaluate the range")
    return result.returncode == 0


def git_parent_shas(repo: Path, sha: str) -> list[str]:
    line = git_output(repo, "rev-list", "--parents", "-n", "1", sha).split()
    return line[1:] if line and line[0] == sha else []


def exact_remote_ref(source: str, ref: str) -> str | None:
    result = subprocess.run(
        [
            "git",
            "--no-replace-objects",
            "-c",
            "http.sslVerify=true",
            "ls-remote",
            "--refs",
            source,
            ref,
        ],
        capture_output=True,
        text=True,
        check=False,
        env=sanitized_git_environment(),
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown transport failure"
        raise RuntimeError(f"git ls-remote {ref}: {detail}")
    rows = [line.split() for line in result.stdout.splitlines() if line.strip()]
    if not rows:
        return None
    if len(rows) != 1 or len(rows[0]) != 2 or rows[0][1] != ref:
        raise RuntimeError(f"git ls-remote returned an ambiguous result for {ref}")
    return rows[0][0]


def local_evidence_errors(repo: Path, evidence_root: Path, sha: str) -> list[str]:
    evidence_directory = evidence_root / sha
    try:
        document, _payload = load_manifest(evidence_directory)
    except EvidenceError as exc:
        return [f"exact rehearsal evidence is invalid: {exc}"]
    errors: list[str] = []
    if document.get("subject_commit") != sha:
        errors.append("rehearsal evidence binds a different subject commit")
    if document.get("source_class") != "local":
        errors.append("candidate rehearsal evidence is not local-source evidence")
    if document.get("remote_main_commit") is not None:
        errors.append("candidate rehearsal evidence improperly claims remote-main identity")
    profile = document.get("profile_files")
    if not isinstance(profile, dict) or set(profile) != set(PROFILE_PATHS):
        errors.append("candidate rehearsal profile inventory is not exact")
        return errors
    for relative in PROFILE_PATHS:
        try:
            payload = git_bytes(repo, "cat-file", "blob", f"{sha}:{relative}")
        except RuntimeError as exc:
            errors.append(f"cannot read candidate profile {relative}: {exc}")
            continue
        digest = hashlib.sha256(payload).hexdigest()
        if profile.get(relative) != digest:
            errors.append(f"candidate profile digest differs from Git bytes: {relative}")
    return errors


def update_errors(
    *,
    remote_ref: str,
    remote_sha: str,
    local_sha: str,
    main_sha: str,
    range_shas: list[str],
    parent_shas: list[str],
    boundary_is_ancestor: bool,
    evidence_errors: list[str],
) -> list[str]:
    """Return fail-closed errors for one proposed governed ref update."""

    errors: list[str] = []
    governed = remote_ref == MAIN_REF or remote_ref.startswith(RELEASE_PREFIX)
    if not governed:
        return errors

    if not SHA_RE.fullmatch(remote_sha) or not SHA_RE.fullmatch(local_sha):
        return ["publication update SHAs must be lowercase forty-character values"]
    if not SHA_RE.fullmatch(main_sha) or main_sha == ZERO_SHA:
        return ["observed remote main must be one existing commit"]

    if local_sha == ZERO_SHA:
        if remote_ref == MAIN_REF:
            return ["deleting main is forbidden"]
        if remote_sha == ZERO_SHA:
            return ["deleting an absent release ref is invalid"]
        return ["deleting a retained release candidate ref is forbidden"]

    if remote_ref == MAIN_REF:
        if remote_sha == ZERO_SHA:
            errors.append("creating main through publication is forbidden")
        if remote_sha != main_sha:
            errors.append("pre-push main identity differs from observed remote main")
        boundary_sha = remote_sha
    else:
        expected_ref = f"{RELEASE_PREFIX}{local_sha}"
        if remote_ref != expected_ref:
            errors.append("release ref name must contain the exact candidate SHA")
        if remote_sha != ZERO_SHA:
            errors.append("a release candidate ref may be created exactly once")
        boundary_sha = main_sha

    if not boundary_is_ancestor:
        errors.append("candidate is not a descendant of the publication boundary")
    if range_shas != [local_sha]:
        errors.append("publication must contain exactly one new commit")
    if parent_shas != [boundary_sha]:
        errors.append("candidate must be one single-parent direct child of the boundary")
    errors.extend(evidence_errors)
    return errors


def inspect_update(
    *,
    repo: Path,
    remote_ref: str,
    remote_sha: str,
    local_sha: str,
    main_sha: str,
    evidence_root: Path,
) -> list[str]:
    governed = remote_ref == MAIN_REF or remote_ref.startswith(RELEASE_PREFIX)
    if not governed:
        return []

    if local_sha == ZERO_SHA:
        return update_errors(
            remote_ref=remote_ref,
            remote_sha=remote_sha,
            local_sha=local_sha,
            main_sha=main_sha,
            range_shas=[],
            parent_shas=[],
            boundary_is_ancestor=True,
            evidence_errors=[],
        )

    if not SHA_RE.fullmatch(local_sha):
        return ["local publication SHA is malformed"]
    boundary_sha = remote_sha if remote_ref == MAIN_REF else main_sha
    if not SHA_RE.fullmatch(boundary_sha) or boundary_sha == ZERO_SHA:
        return ["publication boundary SHA is malformed or absent"]

    boundary_is_ancestor = git_is_ancestor(repo, boundary_sha, local_sha)
    range_shas = (
        git_output(repo, "rev-list", "--reverse", f"{boundary_sha}..{local_sha}").splitlines()
        if boundary_is_ancestor
        else []
    )
    return update_errors(
        remote_ref=remote_ref,
        remote_sha=remote_sha,
        local_sha=local_sha,
        main_sha=main_sha,
        range_shas=range_shas,
        parent_shas=git_parent_shas(repo, local_sha),
        boundary_is_ancestor=boundary_is_ancestor,
        evidence_errors=local_evidence_errors(repo, evidence_root, local_sha),
    )


def ci_event_errors(
    *,
    event: dict[str, Any],
    github_sha: str,
    repo_head: str,
    parent_shas: list[str],
    range_shas: list[str],
    remote_main_sha: str | None,
    remote_release_sha: str | None,
) -> list[str]:
    """Pure push-event policy used by the live CI inspector and self-test."""

    errors: list[str] = []
    ref = event.get("ref")
    before = event.get("before")
    after = event.get("after")
    repository = event.get("repository")
    repository_name = repository.get("full_name") if isinstance(repository, dict) else None
    default_branch = (
        repository.get("default_branch") if isinstance(repository, dict) else None
    )
    if repository_name != CANONICAL_REPOSITORY or default_branch != "main":
        errors.append("push event repository identity is not canonical")
    if not SHA_RE.fullmatch(github_sha) or after != github_sha or repo_head != github_sha:
        errors.append("event, runner checkout, and GITHUB_SHA are not one exact commit")
    if event.get("deleted") is not False or event.get("forced") is not False:
        errors.append("publication push is deleted or forced")
    if range_shas != [github_sha]:
        errors.append("push event does not contain exactly one new commit")

    if ref == MAIN_REF:
        if parent_shas != [before]:
            errors.append(
                "push subject is not one single-parent direct child of event.before"
            )
        if event.get("created") is not False or not SHA_RE.fullmatch(str(before)):
            errors.append("main publication is not one update of an existing branch")
        if remote_main_sha != github_sha:
            errors.append("remote main does not equal the workflow subject")
        if remote_release_sha != github_sha:
            errors.append("exact candidate release ref is absent during main validation")
    elif ref == f"{RELEASE_PREFIX}{github_sha}":
        if (
            event.get("created") is not True
            or before != ZERO_SHA
            or remote_main_sha is None
            or parent_shas != [remote_main_sha]
        ):
            errors.append("release publication is not one direct-child branch creation")
        if remote_release_sha != github_sha:
            errors.append("remote release ref does not equal the workflow subject")
    else:
        errors.append("publication workflow ran for a noncanonical ref")
    return errors


def inspect_ci_event(repo: Path, event_path: Path, github_sha: str) -> list[str]:
    try:
        event = decode_json(event_path, "GitHub push event")
    except ValueError as exc:
        return [str(exc)]
    ref = event.get("ref")
    before = event.get("before")
    if not isinstance(ref, str) or not isinstance(before, str):
        return ["GitHub push event has no exact ref/before identity"]
    if not SHA_RE.fullmatch(github_sha):
        return ["GITHUB_SHA is not one lowercase forty-character commit"]
    repo_head = git_output(repo, "rev-parse", "HEAD")
    parent_shas = git_parent_shas(repo, github_sha)
    range_shas: list[str] = []
    if SHA_RE.fullmatch(before) and before != ZERO_SHA and git_is_ancestor(
        repo, before, github_sha
    ):
        range_shas = git_output(
            repo, "rev-list", "--reverse", f"{before}..{github_sha}"
        ).splitlines()
    elif before == ZERO_SHA and len(parent_shas) == 1:
        range_shas = [github_sha]

    remote_main_sha = exact_remote_ref(CANONICAL_SOURCE, MAIN_REF)
    remote_release_sha = exact_remote_ref(
        CANONICAL_SOURCE, f"{RELEASE_PREFIX}{github_sha}"
    )
    return ci_event_errors(
        event=event,
        github_sha=github_sha,
        repo_head=repo_head,
        parent_shas=parent_shas,
        range_shas=range_shas,
        remote_main_sha=remote_main_sha,
        remote_release_sha=remote_release_sha,
    )


def self_test() -> int:
    parent = "1" * 40
    candidate = "2" * 40
    other = "3" * 40
    baseline = {
        "remote_ref": MAIN_REF,
        "remote_sha": parent,
        "local_sha": candidate,
        "main_sha": parent,
        "range_shas": [candidate],
        "parent_shas": [parent],
        "boundary_is_ancestor": True,
        "evidence_errors": [],
    }
    release_baseline = {
        **baseline,
        "remote_ref": f"{RELEASE_PREFIX}{candidate}",
        "remote_sha": ZERO_SHA,
    }
    for label, subject in (("main", baseline), ("release", release_baseline)):
        errors = update_errors(**subject)
        if errors:
            print(
                f"publication sequence self-test: safe {label} refused: {errors}",
                file=sys.stderr,
            )
            return 1

    update_mutations: list[tuple[str, dict[str, Any], str]] = [
        ("multi-commit", {"range_shas": [other, candidate]}, "exactly one"),
        ("merge", {"parent_shas": [parent, other]}, "single-parent"),
        ("wrong-parent", {"parent_shas": [other]}, "single-parent"),
        ("non-ancestor", {"boundary_is_ancestor": False}, "not a descendant"),
        ("invalid-evidence", {"evidence_errors": ["forged manifest"]}, "forged"),
        (
            "wrong-release-name",
            {
                "remote_ref": f"{RELEASE_PREFIX}{other}",
                "remote_sha": ZERO_SHA,
            },
            "exact candidate SHA",
        ),
        (
            "release-recreation",
            {
                "remote_ref": f"{RELEASE_PREFIX}{candidate}",
                "remote_sha": candidate,
            },
            "created exactly once",
        ),
        (
            "stale-main",
            {"remote_sha": other},
            "differs from observed remote main",
        ),
        (
            "main-deletion",
            {
                "local_sha": ZERO_SHA,
                "range_shas": [],
                "parent_shas": [],
                "evidence_errors": [],
            },
            "deleting main",
        ),
        (
            "release-deletion",
            {
                "remote_ref": f"{RELEASE_PREFIX}{candidate}",
                "remote_sha": candidate,
                "local_sha": ZERO_SHA,
                "range_shas": [],
                "parent_shas": [],
                "evidence_errors": [],
            },
            "retained release candidate",
        ),
    ]
    rejected = 0
    for case_id, changes, expected in update_mutations:
        subject = dict(baseline)
        subject.update(changes)
        errors = update_errors(**subject)
        if not any(expected in error for error in errors):
            print(
                f"publication sequence self-test {case_id}: "
                f"expected {expected!r}, got {errors}",
                file=sys.stderr,
            )
            return 1
        rejected += 1

    safe_event = {
        "ref": MAIN_REF,
        "before": parent,
        "after": candidate,
        "created": False,
        "deleted": False,
        "forced": False,
        "repository": {
            "full_name": CANONICAL_REPOSITORY,
            "default_branch": "main",
        },
    }
    event_baseline = {
        "event": safe_event,
        "github_sha": candidate,
        "repo_head": candidate,
        "parent_shas": [parent],
        "range_shas": [candidate],
        "remote_main_sha": candidate,
        "remote_release_sha": candidate,
    }
    if ci_event_errors(**event_baseline):
        print("publication sequence self-test: safe CI event refused", file=sys.stderr)
        return 1
    release_event = copy.deepcopy(safe_event)
    release_event.update(
        ref=f"{RELEASE_PREFIX}{candidate}",
        before=ZERO_SHA,
        created=True,
    )
    release_event_baseline = {
        **event_baseline,
        "event": release_event,
        "parent_shas": [parent],
        "remote_main_sha": parent,
    }
    if ci_event_errors(**release_event_baseline):
        print(
            "publication sequence self-test: safe release CI event refused",
            file=sys.stderr,
        )
        return 1

    event_mutations: list[tuple[str, dict[str, Any], str]] = [
        ("wrong-checkout", {"repo_head": other}, "runner checkout"),
        ("missing-release", {"remote_release_sha": None}, "release ref"),
        ("moved-main", {"remote_main_sha": other}, "remote main"),
        ("multi-commit-event", {"range_shas": [other, candidate]}, "one new commit"),
        ("wrong-event-parent", {"parent_shas": [other]}, "single-parent"),
    ]
    for case_id, changes, expected in event_mutations:
        subject = dict(event_baseline)
        subject.update(changes)
        errors = ci_event_errors(**subject)
        if not any(expected in error for error in errors):
            print(
                f"publication sequence self-test {case_id}: "
                f"expected {expected!r}, got {errors}",
                file=sys.stderr,
            )
            return 1
        rejected += 1

    hostile_environment = {
        "PATH": os.environ.get("PATH", ""),
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "url.https://attacker.invalid/.insteadOf",
        "GIT_CONFIG_VALUE_0": "https://github.com/",
        "GIT_TRACE2_EVENT": "/tmp/exfiltrate",
        "GIT_SSL_NO_VERIFY": "1",
        "GIT_SSH_COMMAND": "attacker-command",
    }
    isolated_environment = sanitized_git_environment(hostile_environment)
    forbidden_environment = {
        "GIT_CONFIG_KEY_0",
        "GIT_CONFIG_VALUE_0",
        "GIT_TRACE2_EVENT",
        "GIT_SSL_NO_VERIFY",
        "GIT_SSH_COMMAND",
    }
    if forbidden_environment & set(isolated_environment) or {
        "GIT_CONFIG_COUNT": "0",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
    }.items() - isolated_environment.items():
        print(
            "publication sequence self-test: hostile Git environment survived",
            file=sys.stderr,
        )
        return 1
    rejected += 1

    print(
        "Publication sequence self-test PASSED — "
        f"{rejected} known-bad updates/events rejected"
    )
    return 0


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--ci-event", type=Path)
    parser.add_argument("--github-sha", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--remote-ref")
    parser.add_argument("--remote-sha")
    parser.add_argument("--local-sha")
    parser.add_argument("--main-sha")
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=Path(
            os.environ.get(
                "ODEYA_EVIDENCE_ROOT",
                "/Users/danielwahnich/workspace/odeya-release-evidence",
            )
        ),
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if arguments.self_test:
        return self_test()
    repo = arguments.repo.resolve()
    try:
        if arguments.ci_event is not None:
            if arguments.github_sha is None:
                print("--github-sha or GITHUB_SHA is required with --ci-event", file=sys.stderr)
                return 2
            errors = inspect_ci_event(
                repo, arguments.ci_event.resolve(), arguments.github_sha
            )
            subject = arguments.github_sha
            destination = "GitHub push event"
        else:
            required = (
                arguments.remote_ref,
                arguments.remote_sha,
                arguments.local_sha,
                arguments.main_sha,
            )
            if any(value is None for value in required):
                print(
                    "--remote-ref, --remote-sha, --local-sha, and --main-sha "
                    "are required",
                    file=sys.stderr,
                )
                return 2
            errors = inspect_update(
                repo=repo,
                remote_ref=arguments.remote_ref,
                remote_sha=arguments.remote_sha,
                local_sha=arguments.local_sha,
                main_sha=arguments.main_sha,
                # Preserve lexical path components so the shared evidence
                # loader can reject a symlinked configured evidence root.
                evidence_root=arguments.evidence_root.absolute(),
            )
            subject = arguments.local_sha
            destination = arguments.remote_ref
    except (RuntimeError, ValueError) as exc:
        print(f"publication sequence inspection failed: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(f"publication sequence: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"Publication sequence accepted: {subject} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
