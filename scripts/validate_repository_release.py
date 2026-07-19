#!/usr/bin/env python3
"""Validate Odeya's architecture-only repository release surface.

This checker is deliberately standard-library-only. It verifies retained bytes and
security-relevant workflow shape; Actionlint, Markdownlint, Mermaid, and the full
architecture/formal suites remain separate independent tools.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OPENING_SENTENCE = (
    "Odeya is a private research engine that turns a thesis into a governed, "
    "replayable chain from question to evidence to warranted claim."
)
WORKFLOWS = {
    ".github/workflows/architecture.yml": "Architecture / Foundation",
    ".github/workflows/release-surface.yml": "Repository / Release Surface",
    ".github/workflows/formal.yml": "Architecture / Bounded Formal Models",
}
REQUIRED_JOB_NAMES = {
    ".github/workflows/architecture.yml": (
        "Fast policy",
        "Foundation",
        "Schema contracts",
        "Semantic contracts",
        "Adversarial controls",
        "Canonical identity",
        "Architecture evidence",
    ),
    ".github/workflows/release-surface.yml": ("Release surface",),
    ".github/workflows/formal.yml": ("Bounded formal models",),
}
REQUIRED_JOB_IDS = {
    ".github/workflows/architecture.yml": (
        "fast-policy",
        "foundation",
        "schema-contracts",
        "semantic-contracts",
        "adversarial-controls",
        "canonical-identity",
        "architecture-evidence",
    ),
    ".github/workflows/release-surface.yml": ("release-surface",),
    ".github/workflows/formal.yml": ("bounded-models",),
}
SHELL_SCRIPTS = (
    "scripts/ci/install-node.sh",
    "scripts/ci/install-actionlint.sh",
    "scripts/ci/install-zizmor.sh",
    "scripts/ci/install-shellcheck.sh",
    "scripts/ci/install-gitleaks.sh",
    "scripts/ci/sanitize-git-environment.sh",
    "scripts/ci/render-readme-architecture.sh",
    "scripts/ci/check-repository-release.sh",
    "scripts/ci/rehearse-fresh-clone.sh",
)
REQUIRED_PATHS = (
    ".python-version",
    ".java-version",
    ".gitleaks.toml",
    ".gitleaksignore",
    ".markdownlint-cli2.jsonc",
    ".github/SECURITY.md",
    ".github/dependabot.yml",
    "docs/REPOSITORY_RELEASE.md",
    "tools/repository-release/.node-version",
    "tools/repository-release/package.json",
    "tools/repository-release/package-lock.json",
    "tools/repository-release/requirements-architecture.lock",
    "tools/repository-release/toolchain.lock.json",
    "scripts/write_release_evidence_manifest.py",
    "scripts/write_rehearsal_evidence_manifest.py",
    "scripts/compare_rehearsal_manifests.py",
    "scripts/validate_schema_contracts.py",
    "scripts/validate_contract_profiles.py",
    "tests/repository-release/README.md",
    "tests/repository-release/cases.json",
    *WORKFLOWS,
    *SHELL_SCRIPTS,
)
ACTION_LINE = re.compile(
    r"^\s*(?:-\s+)?uses:\s+(?P<action>[^@\s]+)@(?P<commit>[0-9a-f]{40})"
    r"\s+#\s+(?P<version>v[^\s]+)\s*$",
    re.MULTILINE,
)
ANY_ACTION_LINE = re.compile(r"^\s*(?:-\s+)?uses:\s+(.+?)\s*$", re.MULTILINE)
REQUIREMENT = re.compile(
    r"^(?P<name>[A-Za-z0-9_.-]+)(?:\[[^]]+\])?==(?P<version>[^\s\\]+)",
    re.MULTILINE,
)
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
    "GIT_TRACE_CURL",
    "GIT_TRACE_CURL_NO_DATA",
    "GIT_TRACE_PACKET",
    "GIT_TRACE_PACK_ACCESS",
    "GIT_TRACE_PERFORMANCE",
    "GIT_TRACE_REDACT",
    "GIT_TRACE_SETUP",
    "GIT_TRACE_SHALLOW",
    "GIT_TRACE2",
    "GIT_TRACE2_BRIEF",
    "GIT_TRACE2_CONFIG_PARAMS",
    "GIT_TRACE2_DST_DEBUG",
    "GIT_TRACE2_ENV_VARS",
    "GIT_TRACE2_EVENT",
    "GIT_TRACE2_PARENT_SID",
    "GIT_TRACE2_PERF",
    "GIT_TRANSPORT_HELPER_DEBUG",
    "GIT_WORK_TREE",
)
RELEASE_CONTRACT_REQUIRED = (
    "The public canonical remote already exists at\n"
    "`https://github.com/manfromnowhere143/odeya`; its default branch is `main`.",
    "No architecture commit may be pushed to `main`",
    "complete local fresh-clone rehearsal",
    "Workers do not receive repository credentials",
    "refs/heads/main",
    "CANDIDATE_COMMIT",
    "invariant-profile comparison receipt",
    "approved-canonical-source-sha256",
    "A local hook is not server-side branch protection",
    "no repository ruleset",
    "does not authorize runtime",
)
RELEASE_CONTRACT_FORBIDDEN = (
    "canonical repository is private",
    "canonical remote remains private",
    "no remote exists",
    "remote does not exist",
    "local hook is server-side branch protection",
    "architecture publication authorizes runtime",
    "repository release authorizes runtime",
)
EXPECTED_RELEASE_CONTRACT_MUTATIONS = {
    "future-private-remote-regression": (
        "The public canonical remote already exists at\n"
        "`https://github.com/manfromnowhere143/odeya`; its default branch is `main`.",
        "The canonical remote remains private and may later be created at\n"
        "`https://github.com/manfromnowhere143/odeya`; its default branch is `main`.",
        "The public canonical remote already exists",
    ),
    "wrong-public-remote-identity": (
        "The public canonical remote already exists at\n"
        "`https://github.com/manfromnowhere143/odeya`; its default branch is `main`.",
        "The public canonical remote already exists at\n"
        "`https://github.com/example/other`; its default branch is `main`.",
        "https://github.com/manfromnowhere143/odeya",
    ),
    "unbound-main-publication": (
        "No architecture commit may be pushed to `main`",
        "An architecture commit may be pushed to `main` without exact evidence",
        "No architecture commit may be pushed to `main`",
    ),
    "local-hook-claimed-as-server-protection": (
        "A local hook is not server-side branch protection.",
        "A local hook is server-side branch protection.",
        "A local hook is not server-side branch protection",
    ),
    "appended-private-remote-contradiction": (
        "It is\nhistory, not a procedure to rerun.",
        "It is\nhistory, not a procedure to rerun. The canonical repository is "
        "private and no remote exists.",
        "forbidden contradictory statement 'canonical repository is private'",
    ),
}
GIT_ENVIRONMENT_TO_FIX = {
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_CONFIG_COUNT": "0",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_NO_REPLACE_OBJECTS": "1",
    "GIT_PAGER": "cat",
    "GIT_TERMINAL_PROMPT": "0",
}


class DuplicateKeyError(ValueError):
    pass


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def load_json(relative: str, errors: list[str]) -> Any:
    path = ROOT / relative
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"{relative}: invalid JSON: {exc}")
        return None


def read(relative: str, errors: list[str]) -> str:
    try:
        return (ROOT / relative).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{relative}: unreadable: {exc}")
        return ""


def validate_git_environment_sanitizer(errors: list[str]) -> None:
    relative = "scripts/ci/sanitize-git-environment.sh"
    path = ROOT / relative
    sanitizer = read(relative, errors)
    for variable in GIT_ENVIRONMENT_TO_REMOVE:
        if variable.startswith("GIT_TRACE_") or variable.startswith("GIT_TRACE2_"):
            continue
        if variable not in sanitizer:
            errors.append(f"{relative}: missing ambient Git variable {variable}")
    for variable, value in GIT_ENVIRONMENT_TO_FIX.items():
        if f"export {variable}={value}" not in sanitizer:
            errors.append(f"{relative}: missing fixed Git environment {variable}={value}")
    for prefix in ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_", "GIT_TRACE_", "GIT_TRACE2"):
        if prefix not in sanitizer:
            errors.append(f"{relative}: ambient variable prefix {prefix} is not removed")

    probe_environment = dict(os.environ)
    for variable in GIT_ENVIRONMENT_TO_REMOVE:
        probe_environment[variable] = "/tmp/odeya-adversarial-git-routing"
    probe_environment["GIT_CONFIG_COUNT"] = "1"
    probe_environment["GIT_CONFIG_KEY_0"] = "url.file:///tmp/substitute/.insteadOf"
    probe_environment["GIT_CONFIG_VALUE_0"] = "https://approved.invalid/"
    probe = r'''
set -euo pipefail
source "$1"
for name in \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_ATTR_SOURCE GIT_CEILING_DIRECTORIES GIT_COMMON_DIR \
  GIT_CONFIG GIT_CONFIG_PARAMETERS GIT_CONFIG_SYSTEM GIT_DIR \
  GIT_DISCOVERY_ACROSS_FILESYSTEM GIT_EXEC_PATH GIT_EXTERNAL_DIFF \
  GIT_GRAFT_FILE GIT_IMPLICIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE \
  GIT_OBJECT_DIRECTORY GIT_PREFIX GIT_QUARANTINE_PATH GIT_REPLACE_REF_BASE \
  GIT_SHALLOW_FILE GIT_SSL_CAINFO GIT_SSL_CAPATH GIT_SSL_CERT \
  GIT_SSL_CERT_PASSWORD_PROTECTED GIT_SSL_CIPHER_LIST GIT_SSL_KEY \
  GIT_SSL_NO_VERIFY GIT_SSL_VERSION GIT_SSH GIT_SSH_COMMAND GIT_SSH_VARIANT GIT_TRACE \
  GIT_TRACE_CURL GIT_TRACE_CURL_NO_DATA GIT_TRACE_PACKET GIT_TRACE_PACK_ACCESS \
  GIT_TRACE_PERFORMANCE GIT_TRACE_REDACT GIT_TRACE_SETUP GIT_TRACE_SHALLOW \
  GIT_TRACE2 GIT_TRACE2_BRIEF GIT_TRACE2_CONFIG_PARAMS GIT_TRACE2_DST_DEBUG \
  GIT_TRACE2_ENV_VARS GIT_TRACE2_EVENT GIT_TRACE2_PARENT_SID GIT_TRACE2_PERF \
  GIT_TRANSPORT_HELPER_DEBUG GIT_CURL_VERBOSE GIT_WORK_TREE \
  GIT_CONFIG_KEY_0 GIT_CONFIG_VALUE_0; do
  if printenv "$name" >/dev/null 2>&1; then
    printf 'ambient Git variable survived: %s\n' "$name" >&2
    exit 20
  fi
done
[[ "$GIT_ATTR_NOSYSTEM" == "1" ]]
[[ "$GIT_CONFIG_COUNT" == "0" ]]
[[ "$GIT_CONFIG_GLOBAL" == "/dev/null" ]]
[[ "$GIT_CONFIG_NOSYSTEM" == "1" ]]
[[ "$GIT_NO_REPLACE_OBJECTS" == "1" ]]
[[ "$GIT_PAGER" == "cat" ]]
[[ "$GIT_TERMINAL_PROMPT" == "0" ]]
'''
    try:
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", probe, "odeya-git-probe", str(path)],
            cwd=ROOT,
            env=probe_environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"{relative}: isolation self-test could not run: {exc}")
        return
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip() or f"exit {result.returncode}"
        errors.append(f"{relative}: isolation self-test failed: {detail}")
        return

    trace_only_environment = dict(os.environ)
    for name in tuple(trace_only_environment):
        if name.startswith("GIT_CONFIG_KEY_") or name.startswith("GIT_CONFIG_VALUE_"):
            trace_only_environment.pop(name)
    trace_only_environment.update(
        {
            "GIT_TRACE_CURL": "/tmp/odeya-adversarial-curl-trace",
            "GIT_TRACE_REDACT": "0",
            "GIT_TRACE2_EVENT": "/tmp/odeya-adversarial-trace2",
            "GIT_SSL_NO_VERIFY": "1",
        }
    )
    try:
        trace_result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", probe, "odeya-git-trace-probe", str(path)],
            cwd=ROOT,
            env=trace_only_environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"{relative}: trace-only isolation self-test could not run: {exc}")
        return
    if trace_result.returncode != 0:
        detail = (trace_result.stderr or trace_result.stdout).strip() or (
            f"exit {trace_result.returncode}"
        )
        errors.append(f"{relative}: trace-only isolation self-test failed: {detail}")


def extract_mermaid(readme: str, errors: list[str]) -> str:
    blocks = re.findall(r"```mermaid\n(.*?)\n```", readme, flags=re.DOTALL)
    if len(blocks) != 1:
        errors.append(f"README.md: expected exactly one Mermaid block, found {len(blocks)}")
        return ""
    diagram = blocks[0].strip() + "\n"
    required = (
        "1 · CONTRACT",
        "PRIVATE RESEARCH ENGINE",
        "RELEASE PATH · adjudicated candidate only",
        "Independent verification",
        "Human release decision",
        "Exact single-use grant",
        "Independent observation",
        "Grounded memory",
        "CANONICAL SCIENTIFIC STATE",
        "append-only event + evidence ledger",
    )
    for phrase in required:
        if phrase not in diagram:
            errors.append(f"README.md: Mermaid system map is missing {phrase!r}")
    for unsafe in ("click ", "%%{", "javascript:"):
        if unsafe.lower() in diagram.lower():
            errors.append(f"README.md: Mermaid system map contains forbidden directive {unsafe!r}")
    if "R ~~~ X" not in diagram or re.search(r"\bD\s+[-.=~]+.*(?:RC|X)", diagram):
        errors.append(
            "README.md: scientific and release clusters need one invisible layout edge and no misleading cross-cluster claim edge"
        )
    return diagram


def validate_readme(errors: list[str]) -> str:
    readme = read("README.md", errors)
    lines = readme.splitlines()
    if len(lines) < 3 or lines[0] != "# Odeya" or lines[2] != OPENING_SENTENCE:
        errors.append("README.md: opening identity sentence is not exact")
    required = (
        "architecture foundation only",
        "No executable research engine",
        "Gate A remains blocked",
        "scripts/ci/check-repository-release.sh",
        "docs/REPOSITORY_RELEASE.md",
        "Workers do not receive repository credentials",
    )
    # The credential sentence belongs to the linked release contract, not the README.
    for phrase in required[:-1]:
        if phrase not in readme:
            errors.append(f"README.md: missing required release truth {phrase!r}")
    for unsupported in ("production-ready", "fully autonomous", "state of the art"):
        if unsupported in readme.lower():
            errors.append(f"README.md: unsupported maturity language {unsupported!r}")
    return extract_mermaid(readme, errors)


def validate_toolchain(errors: list[str]) -> dict[str, Any]:
    lock = load_json("tools/repository-release/toolchain.lock.json", errors)
    package = load_json("tools/repository-release/package.json", errors)
    package_lock = load_json("tools/repository-release/package-lock.json", errors)
    if not isinstance(lock, dict) or not isinstance(package, dict) or not isinstance(package_lock, dict):
        return {}

    python_version = read(".python-version", errors).strip()
    java_version = read(".java-version", errors).strip()
    node_version = read("tools/repository-release/.node-version", errors).strip()
    if lock.get("python", {}).get("version") != python_version:
        errors.append("toolchain lock: Python version does not match .python-version")
    if lock.get("node", {}).get("version") != node_version:
        errors.append("toolchain lock: Node version does not match .node-version")
    if lock.get("java", {}).get("version") != java_version:
        errors.append("toolchain lock: Java version does not match .java-version")
    if package.get("engines", {}).get("node") != node_version:
        errors.append("package.json: Node engine does not match the toolchain lock")
    expected_npm = lock.get("node", {}).get("npm_version")
    if package.get("packageManager") != f"npm@{expected_npm}":
        errors.append("package.json: packageManager does not match the toolchain lock")
    if package_lock.get("lockfileVersion") != 3:
        errors.append("package-lock.json: lockfileVersion must be 3")

    root_package = package_lock.get("packages", {}).get("", {})
    if root_package.get("devDependencies") != package.get("devDependencies"):
        errors.append("package-lock.json: root dependencies do not match package.json")
    if root_package.get("engines") != package.get("engines"):
        errors.append("package-lock.json: root engines do not match package.json")

    npm_locks = lock.get("npm_packages", {})
    for name, expected in npm_locks.items():
        declared = package.get("devDependencies", {}).get(name)
        installed = package_lock.get("packages", {}).get(f"node_modules/{name}", {})
        if declared != expected.get("version"):
            errors.append(f"package.json: {name} is not pinned to {expected.get('version')}")
        if installed.get("version") != expected.get("version"):
            errors.append(f"package-lock.json: {name} version does not match toolchain lock")
        if installed.get("integrity") != expected.get("integrity"):
            errors.append(f"package-lock.json: {name} integrity does not match toolchain lock")

    return lock


def python_lock_policy_errors(source: str, locked: str, expected_uv: object) -> list[str]:
    issues: list[str] = []
    source_requirements = {
        match.group("name").lower().replace("_", "-"): match.group("version")
        for match in REQUIREMENT.finditer(source)
    }
    locked_matches = list(REQUIREMENT.finditer(locked))
    locked_requirements = {
        match.group("name").lower().replace("_", "-"): match.group("version")
        for match in locked_matches
    }
    if locked_requirements != source_requirements:
        missing = sorted(set(source_requirements) - set(locked_requirements))
        extra = sorted(set(locked_requirements) - set(source_requirements))
        changed = sorted(
            name
            for name in set(source_requirements) & set(locked_requirements)
            if source_requirements[name] != locked_requirements[name]
        )
        issues.append(
            "Python lock: dependency closure differs from requirements-architecture.txt "
            f"(missing={missing}, extra={extra}, changed={changed})"
        )
    for index, match in enumerate(locked_matches):
        end = locked_matches[index + 1].start() if index + 1 < len(locked_matches) else len(locked)
        block = locked[match.start():end]
        if "--hash=sha256:" not in block:
            issues.append(f"Python lock: {match.group('name')} has no SHA-256 distribution hash")
    allowed_hash = re.compile(r"^--hash=sha256:[0-9a-f]{64}(?:\s+\\)?$")
    for line_number, line in enumerate(locked.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if REQUIREMENT.match(line):
            if not stripped.endswith("\\"):
                issues.append(f"Python lock:{line_number}: requirement line must open a hash block")
            continue
        if allowed_hash.fullmatch(stripped):
            continue
        issues.append(f"Python lock:{line_number}: forbidden requirement syntax {stripped!r}")
    for forbidden in (
        "--index-url",
        "--extra-index-url",
        "--find-links",
        "--trusted-host",
        "--no-index",
        "http://",
        "https://",
        " @ ",
    ):
        if any(
            forbidden in line
            for line in locked.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ):
            issues.append(f"Python lock: forbidden source or resolver directive {forbidden!r}")
    if "--generate-hashes" not in locked[:500]:
        issues.append("Python lock: generation command does not retain --generate-hashes")
    if f"# uv version: {expected_uv}" not in locked[:500]:
        issues.append("Python lock: uv generator version does not match toolchain lock")
    return issues


def validate_python_lock(errors: list[str]) -> int:
    source = read("requirements-architecture.txt", errors)
    locked = read("tools/repository-release/requirements-architecture.lock", errors)
    toolchain = load_json("tools/repository-release/toolchain.lock.json", errors)
    expected_uv = (
        toolchain.get("python", {}).get("lock_generator", {}).get("version")
        if isinstance(toolchain, dict)
        else None
    )
    errors.extend(python_lock_policy_errors(source, locked, expected_uv))

    mutations = {
        "extra-package": (
            locked
            + "\nrelease-injection==1.0.0 \\\n"
            + "    --hash=sha256:"
            + "0" * 64
            + "\n"
        ),
        "extra-index": locked + "\n--extra-index-url https://packages.invalid/simple\n",
        "direct-url": locked + "\nrelease-injection @ https://packages.invalid/release.whl\n",
        "unhashed-package": locked + "\nrelease-injection==1.0.0\n",
    }
    passed = 0
    for mutation_id, mutated in mutations.items():
        if not python_lock_policy_errors(source, mutated, expected_uv):
            errors.append(f"Python lock mutation {mutation_id}: unsafe lock was accepted")
            continue
        passed += 1
    return passed


def workflow_policy_errors(
    text: str, expected_job_ids: tuple[str, ...] | None = None
) -> list[str]:
    issues: list[str] = []
    trigger_block = (
        "on:\n"
        "  pull_request:\n"
        "  push:\n"
        "    branches:\n"
        "      - main\n"
        "  workflow_dispatch:\n\n"
    )
    trigger_match = re.search(r"(?ms)^on:\n.*?(?=^permissions:\n)", text)
    if trigger_match is None or trigger_match.group(0) != trigger_block:
        issues.append("trigger block must be exactly pull_request, push main, workflow_dispatch")
    if re.search(r"(?m)^(?:schedule|repository_dispatch|workflow_run):\s*$", text):
        issues.append("trigger inventory contains a forbidden top-level event")
    permission_block = "permissions:\n  contents: read\n\nconcurrency:"
    permission_declarations = re.findall(r"(?m)^\s*permissions:\s*$", text)
    if len(permission_declarations) != 1 or text.count(permission_block) != 1:
        issues.append("permissions must be the single exact contents-read block")
    if re.search(r"(?m)^\s+[A-Za-z0-9-]+:\s*write\s*$", text):
        issues.append("permissions may not contain any write scope")
    if re.search(r"(?m)^\s*environment:\s*", text):
        issues.append("environment deployment binding is forbidden")
    if re.search(r"(?i)(GITHUB_TOKEN|github\.token|secrets\.)", text):
        issues.append("explicit token or secret context is forbidden")

    runner_count = len(re.findall(r"(?m)^\s+runs-on:\s*", text))
    hosted_runner_count = len(re.findall(r"(?m)^\s+runs-on:\s*ubuntu-24\.04\s*$", text))
    if runner_count < 1 or runner_count != hosted_runner_count:
        issues.append("runner must be the exact GitHub-hosted ubuntu-24.04 label")
    timeout_count = len(re.findall(r"(?m)^\s+timeout-minutes:\s*[0-9]+\s*$", text))
    if timeout_count != runner_count:
        issues.append("timeout must exist for every job")

    checkout_count = text.count("uses: actions/checkout@")
    persisted_false = text.count("persist-credentials: false")
    full_history = text.count("fetch-depth: 0")
    if checkout_count < 1 or persisted_false != checkout_count or full_history != checkout_count:
        issues.append("checkout must fetch full history without persisted credentials")
    if "concurrency:" not in text or "cancel-in-progress: true" not in text:
        issues.append("concurrency cancellation is required")
    if "shell: bash" not in text:
        issues.append("explicit bash with GitHub pipefail defaults is required")
    jobs_marker = "\njobs:\n"
    if jobs_marker not in text:
        issues.append("job inventory is absent")
    elif expected_job_ids is not None:
        jobs_text = text.split(jobs_marker, 1)[1]
        observed_job_ids = tuple(re.findall(r"(?m)^  ([A-Za-z0-9_-]+):\s*$", jobs_text))
        if observed_job_ids != expected_job_ids:
            issues.append(
                f"job inventory must be exact: expected {expected_job_ids}, "
                f"got {observed_job_ids}"
            )
    return issues


def validate_policy_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict) or not isinstance(cases.get("mutations"), list):
        return 0
    base_relative = cases.get("base_workflow")
    if not isinstance(base_relative, str):
        errors.append("repository release mutations: base_workflow is absent")
        return 0
    base = read(base_relative, errors)
    passed = 0
    for case in cases["mutations"]:
        if not isinstance(case, dict):
            errors.append("repository release mutations: case is not an object")
            continue
        case_id = case.get("id")
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if not all(isinstance(value, str) and value for value in (case_id, old, expected)) or not isinstance(new, str):
            errors.append("repository release mutations: malformed case")
            continue
        if base.count(old) < 1:
            errors.append(f"repository release mutation {case_id}: source bytes are absent")
            continue
        mutated = base.replace(old, new, 1)
        mutation_issues = workflow_policy_errors(
            mutated, REQUIRED_JOB_IDS.get(base_relative)
        )
        if not any(expected in issue for issue in mutation_issues):
            errors.append(
                f"repository release mutation {case_id}: expected {expected!r} refusal, "
                f"got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


def release_contract_errors(text: str) -> list[str]:
    errors = [
        f"missing release authority boundary {required!r}"
        for required in RELEASE_CONTRACT_REQUIRED
        if required not in text
    ]
    lowered = text.lower()
    errors.extend(
        f"forbidden contradictory statement {forbidden!r}"
        for forbidden in RELEASE_CONTRACT_FORBIDDEN
        if forbidden in lowered
    )
    return errors


def validate_release_contract_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    relative = cases.get("release_contract")
    mutations = cases.get("release_contract_mutations")
    if not isinstance(relative, str) or not isinstance(mutations, list):
        errors.append("repository release contract mutations: inventory is absent")
        return 0
    if relative != "docs/REPOSITORY_RELEASE.md":
        errors.append(
            "repository release contract mutations: subject path is not exact"
        )
    observed_ids = [
        case.get("id")
        for case in mutations
        if isinstance(case, dict)
    ]
    if (
        len(observed_ids) != len(mutations)
        or any(not isinstance(case_id, str) for case_id in observed_ids)
        or len(set(observed_ids)) != len(observed_ids)
        or set(observed_ids) != set(EXPECTED_RELEASE_CONTRACT_MUTATIONS)
    ):
        errors.append(
            "repository release contract mutations: case census is not closed and exact"
        )
    base = read(relative, errors)
    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append("repository release contract mutations: case is not an object")
            continue
        if set(case) != {"id", "old", "new", "expected"}:
            errors.append(
                "repository release contract mutations: case members are not closed and exact"
            )
            continue
        case_id = case.get("id")
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if not all(
            isinstance(value, str) and value
            for value in (case_id, old, new, expected)
        ):
            errors.append("repository release contract mutations: malformed case")
            continue
        expected_spec = EXPECTED_RELEASE_CONTRACT_MUTATIONS.get(case_id)
        if expected_spec != (old, new, expected):
            errors.append(
                f"repository release contract mutation {case_id}: "
                "specification drifted from the pinned matrix"
            )
            continue
        if base.count(old) != 1:
            errors.append(
                f"repository release contract mutation {case_id}: "
                f"expected one source occurrence, found {base.count(old)}"
            )
            continue
        mutation_issues = release_contract_errors(base.replace(old, new, 1))
        if not any(expected in issue for issue in mutation_issues):
            errors.append(
                f"repository release contract mutation {case_id}: expected "
                f"{expected!r} refusal, got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


def validate_workflows(lock: dict[str, Any], errors: list[str]) -> tuple[int, int]:
    workflow_dir = ROOT / ".github/workflows"
    actual = {
        str(path.relative_to(ROOT))
        for path in workflow_dir.glob("*.y*ml")
        if path.is_file()
    }
    if actual != set(WORKFLOWS):
        errors.append(
            "workflow inventory mismatch: expected "
            f"{sorted(WORKFLOWS)}, found {sorted(actual)}"
        )

    action_count = 0
    used_actions: set[str] = set()
    allowed_actions = lock.get("github_actions", {}) if isinstance(lock, dict) else {}
    for relative, expected_name in WORKFLOWS.items():
        text = read(relative, errors)
        if f"name: {expected_name}" not in text:
            errors.append(f"{relative}: workflow name is not exact")
        observed_job_names = tuple(re.findall(r"(?m)^    name: ([^\n]+)$", text))
        if observed_job_names != REQUIRED_JOB_NAMES[relative]:
            errors.append(
                f"{relative}: job context inventory mismatch: expected "
                f"{REQUIRED_JOB_NAMES[relative]}, got {observed_job_names}"
            )
        for issue in workflow_policy_errors(text, REQUIRED_JOB_IDS[relative]):
            errors.append(f"{relative}: {issue}")
        for forbidden in (
            "pull_request_target",
            "secrets.",
            "contents: write",
            "actions: write",
            "packages: write",
            "id-token: write",
            "sudo ",
            "curl |",
            "wget |",
        ):
            if forbidden in text:
                errors.append(f"{relative}: forbidden workflow capability or construct {forbidden!r}")

        parsed_lines = list(ACTION_LINE.finditer(text))
        all_lines = [line.strip() for line in ANY_ACTION_LINE.findall(text)]
        if len(parsed_lines) != len(all_lines):
            errors.append(f"{relative}: every uses entry must be a full SHA plus version comment")
        for match in parsed_lines:
            action_count += 1
            action = match.group("action")
            used_actions.add(action)
            expected = allowed_actions.get(action)
            if not isinstance(expected, dict):
                errors.append(f"{relative}: action {action!r} is absent from the toolchain lock")
                continue
            if match.group("commit") != expected.get("commit"):
                errors.append(f"{relative}: {action} commit does not match the toolchain lock")
            if match.group("version") != expected.get("version"):
                errors.append(f"{relative}: {action} version comment does not match the toolchain lock")

    formal = read(".github/workflows/formal.yml", errors)
    java = lock.get("java", {}) if isinstance(lock, dict) else {}
    if f'java-version: "{java.get("version")}"' not in formal:
        errors.append("formal workflow: Java version does not match toolchain lock")
    if f'distribution: {java.get("distribution")}' not in formal:
        errors.append("formal workflow: Java distribution does not match toolchain lock")

    if used_actions != set(allowed_actions):
        errors.append(
            "GitHub Action inventory mismatch: expected "
            f"{sorted(allowed_actions)}, found {sorted(used_actions)}"
        )
    mutation_count = validate_policy_mutations(errors)
    return action_count, mutation_count


def validate_release_scripts(lock: dict[str, Any], errors: list[str]) -> None:
    node_installer = read("scripts/ci/install-node.sh", errors)
    node = lock.get("node", {}) if isinstance(lock, dict) else {}
    node_version = str(node.get("version", ""))
    if f'readonly VERSION="{node_version}"' not in node_installer:
        errors.append("install-node.sh: version does not match toolchain lock")
    for platform, digest in node.get("archives", {}).items():
        if platform not in node_installer or digest not in node_installer:
            errors.append(f"install-node.sh: missing locked archive {platform}")

    renderer = read("scripts/ci/render-readme-architecture.sh", errors)
    chrome_major = str(lock.get("chrome", {}).get("supported_major", ""))
    if f'readonly EXPECTED_CHROME_MAJOR="{chrome_major}"' not in renderer:
        errors.append("render-readme-architecture.sh: Chrome major does not match toolchain lock")

    installer = read("scripts/ci/install-actionlint.sh", errors)
    actionlint = lock.get("actionlint", {}) if isinstance(lock, dict) else {}
    version = str(actionlint.get("version", ""))
    if f'readonly VERSION="{version}"' not in installer:
        errors.append("install-actionlint.sh: version does not match toolchain lock")
    for platform, digest in actionlint.get("archives", {}).items():
        if platform not in installer or digest not in installer:
            errors.append(f"install-actionlint.sh: missing locked archive {platform}")

    zizmor_installer = read("scripts/ci/install-zizmor.sh", errors)
    zizmor = lock.get("zizmor", {}) if isinstance(lock, dict) else {}
    zizmor_version = str(zizmor.get("version", ""))
    if f'readonly VERSION="{zizmor_version}"' not in zizmor_installer:
        errors.append("install-zizmor.sh: version does not match toolchain lock")
    for platform, digest in zizmor.get("archives", {}).items():
        if platform not in zizmor_installer or digest not in zizmor_installer:
            errors.append(f"install-zizmor.sh: missing locked archive {platform}")

    shellcheck_installer = read("scripts/ci/install-shellcheck.sh", errors)
    shellcheck = lock.get("shellcheck", {}) if isinstance(lock, dict) else {}
    shellcheck_version = str(shellcheck.get("version", ""))
    if f'readonly VERSION="{shellcheck_version}"' not in shellcheck_installer:
        errors.append("install-shellcheck.sh: version does not match toolchain lock")
    for platform, digest in shellcheck.get("archives", {}).items():
        if platform not in shellcheck_installer or digest not in shellcheck_installer:
            errors.append(f"install-shellcheck.sh: missing locked archive {platform}")

    gitleaks_installer = read("scripts/ci/install-gitleaks.sh", errors)
    gitleaks = lock.get("gitleaks", {}) if isinstance(lock, dict) else {}
    gitleaks_version = str(gitleaks.get("version", ""))
    if f'readonly VERSION="{gitleaks_version}"' not in gitleaks_installer:
        errors.append("install-gitleaks.sh: version does not match toolchain lock")
    for platform, digest in gitleaks.get("archives", {}).items():
        if platform not in gitleaks_installer or digest not in gitleaks_installer:
            errors.append(f"install-gitleaks.sh: missing locked archive {platform}")

    release_check = read("scripts/ci/check-repository-release.sh", errors)
    for required in (
        "validate_repository_release.py",
        "install-node.sh",
        "ci --ignore-scripts",
        "lint:markdown",
        "install-actionlint.sh",
        "install-zizmor.sh",
        "install-shellcheck.sh",
        "install-gitleaks.sh",
        "render-readme-architecture.sh",
        "write_release_evidence_manifest.py",
        "WORK_EVIDENCE_ROOT",
        "clean tracked tree",
        "failure-receipt.txt",
        "compare_rehearsal_manifests.py",
        ".repository-release.publish.",
        "GITLEAKS_CONFIG_TOML",
        ".gitleaks.toml",
        "--no-config --offline --pedantic",
        "gitleaks-history.log",
        "audit --audit-level=high",
        "sanitize-git-environment.sh",
        "--log-opts=\"$SUBJECT_COMMIT\"",
        "rev-parse --is-shallow-repository",
        "Gitleaks did not attest the exact subject ancestry commit count",
    ):
        if required not in release_check:
            errors.append(f"check-repository-release.sh: missing step {required!r}")

    architecture_workflow = read(".github/workflows/architecture.yml", errors)
    if "--only-binary=:all:" not in architecture_workflow:
        errors.append("architecture workflow: Python installation does not forbid source builds")

    rehearsal = read("scripts/ci/rehearse-fresh-clone.sh", errors)
    for required in (
        "clone --no-local",
        "--require-hashes",
        "--only-binary=:all:",
        ".java-version",
        "scripts/validate.py",
        "check-repository-release.sh",
        "formal/tla/check.sh",
        "git diff --exit-code",
        "--untracked-files=all",
        "remote-main",
        "write_rehearsal_evidence_manifest.py",
        "gitleaks-evidence.log",
        ".odeya-rehearsal.publish.",
        "GITLEAKS_CONFIG_TOML",
        ".gitleaks.toml",
        "EXPECTED_SOURCE_IDENTITY_SHA256",
        "approved canonical source identity",
        "sanitize-git-environment.sh",
        "rev-parse --is-shallow-repository",
        "http.sslVerify=true",
    ):
        if required not in rehearsal:
            errors.append(f"rehearse-fresh-clone.sh: missing step {required!r}")

    for relative in SHELL_SCRIPTS:
        path = ROOT / relative
        try:
            mode = path.stat().st_mode
        except OSError:
            continue
        if not mode & stat.S_IXUSR:
            errors.append(f"{relative}: script is not executable")

    comparator = read("scripts/compare_rehearsal_manifests.py", errors)
    for required in (
        "EXPECTED_EVIDENCE_PATHS",
        "rehearsal_document_errors",
        "release_document_errors",
        "verify_files",
        "retained SHA-256 differs",
        "files contains a duplicate path",
        "verified_evidence_and_invariant_profile_equal",
        "DuplicateKeyError",
        "REHEARSAL_FIELDS",
        "RELEASE_FIELDS",
    ):
        if required not in comparator:
            errors.append(f"compare_rehearsal_manifests.py: missing {required!r}")


def validate_supporting_files(errors: list[str]) -> None:
    dependabot = read(".github/dependabot.yml", errors)
    for required in (
        'package-ecosystem: "github-actions"',
        'package-ecosystem: "npm"',
        'package-ecosystem: "pip"',
        'directory: "/tools/repository-release"',
        "open-pull-requests-limit:",
    ):
        if required not in dependabot:
            errors.append(f".github/dependabot.yml: missing {required!r}")
    security = read(".github/SECURITY.md", errors)
    for required in (
        "Do not open a public issue",
        "architecture-only",
        "credentials",
        "GitHub Security Advisory",
    ):
        if required not in security:
            errors.append(f".github/SECURITY.md: missing security boundary {required!r}")
    release_contract = read("docs/REPOSITORY_RELEASE.md", errors)
    for issue in release_contract_errors(release_contract):
        errors.append(f"docs/REPOSITORY_RELEASE.md: {issue}")
    gitleaks_ignore = [
        line.strip()
        for line in read(".gitleaksignore", errors).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    expected_false_positive = (
        "369bbb87f1e9bea05733df44d36bcf177451371f:"
        "tests/architecture-schema/fixtures/release-event.valid.json:generic-api-key:21"
    )
    if gitleaks_ignore != [expected_false_positive]:
        errors.append(".gitleaksignore: expected exactly one reviewed synthetic-fixture fingerprint")
    gitleaks_config = read(".gitleaks.toml", errors)
    if gitleaks_config != (
        'title = "Odeya repository release secret-scanning profile"\n\n'
        "[extend]\n"
        "useDefault = true\n"
    ):
        errors.append(".gitleaks.toml: exact default-extension profile is required")


# (path, carries_url): every copy carries the digest; only the two
# downloaders carry the URL — formal/tla/check.sh consumes a local jar.
TLA_PIN_SOURCES = (
    (".github/workflows/formal.yml", True),
    ("scripts/ci/rehearse-fresh-clone.sh", True),
    ("formal/tla/check.sh", False),
)


def validate_tla_pin_copies(errors: list[str]) -> None:
    """One TLA+ jar identity, however many copies carry it.

    The jar URL and sha256 exist in the formal workflow, the rehearsal
    script, the formal check script, and formal/tla/toolchain.lock.json. No
    gate bound the copies to each other, so a partial toolchain bump was
    local-green and remote-red — the incident's mechanism one file over
    (independent review, ADR 0063). The lock file is the reference; every
    text copy must carry exactly its URL and digest.
    """
    lock = load_json("formal/tla/toolchain.lock.json", errors)
    asset = lock.get("asset", {}) if isinstance(lock, dict) else {}
    url = asset.get("url")
    sha = asset.get("sha256")
    if not (isinstance(url, str) and url and isinstance(sha, str) and len(sha) == 64):
        errors.append("formal/tla/toolchain.lock.json: asset url/sha256 are absent or malformed")
        return
    for relative, carries_url in TLA_PIN_SOURCES:
        text = read(relative, errors)
        if carries_url and url not in text:
            errors.append(f"{relative}: TLA+ jar URL does not match formal/tla/toolchain.lock.json")
        if sha not in text:
            errors.append(f"{relative}: TLA+ jar sha256 does not match formal/tla/toolchain.lock.json")


# CI jobs that run scripts on a bare interpreter, with the exact scripts they
# invoke. A non-stdlib import added to any of these passes every local gate
# that runs inside an installed environment and fails only on the remote
# runner — the incident's mechanism one layer down (environment pin instead
# of count pin; independent review, ADR 0063).
BARE_INTERPRETER_SCRIPTS = (
    "scripts/validate_repository_release.py",
    "tests/canonicalization/compare_results.py",
    "tests/canonicalization/audit_schemas.py",
    "scripts/validate_gate_a_prerequisites.py",
    "scripts/validate_prq_009_assignment_order.py",
    "scripts/validate_schema_resource_reissues.py",
    "scripts/validate_lifecycle_guard_coverage.py",
    "scripts/validate_lifecycle_condition_coverage.py",
    "scripts/validate_canonicalization_dispositions.py",
    "scripts/validate_contract_profiles.py",
    "scripts/validate_refusal_attribution.py",
)


def validate_bare_interpreter_imports(errors: list[str]) -> None:
    """Every bare-job script must import only the standard library.

    Local-module imports are followed one level so a stdlib facade cannot
    hide a third-party import behind `import validate`.
    """
    import ast

    stdlib = set(sys.stdlib_module_names)
    seen: set[str] = set()
    queue = list(BARE_INTERPRETER_SCRIPTS)
    while queue:
        relative = queue.pop()
        if relative in seen:
            continue
        seen.add(relative)
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"bare-interpreter script is missing: {relative}")
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            errors.append(f"{relative}: does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                sibling = path.parent / f"{name}.py"
                if sibling.is_file():
                    queue.append(str(sibling.relative_to(ROOT)))
                elif name not in stdlib:
                    errors.append(
                        f"{relative}: imports non-stdlib module {name!r} but runs on a "
                        "bare CI interpreter; it would fail only on the remote runner"
                    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-mermaid", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required release file: {relative}")

    diagram = validate_readme(errors)
    lock = validate_toolchain(errors)
    validate_git_environment_sanitizer(errors)
    python_lock_mutation_count = validate_python_lock(errors)
    action_count, policy_mutation_count = validate_workflows(lock, errors)
    release_contract_mutation_count = validate_release_contract_mutations(errors)
    validate_release_scripts(lock, errors)
    validate_supporting_files(errors)
    validate_tla_pin_copies(errors)
    validate_bare_interpreter_imports(errors)

    if errors:
        print("Odeya repository release validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.extract_mermaid:
        args.extract_mermaid.parent.mkdir(parents=True, exist_ok=True)
        args.extract_mermaid.write_text(diagram, encoding="utf-8")

    print("Odeya repository release validation PASSED")
    print(f"- {len(WORKFLOWS)} least-privilege workflows")
    print(f"- {action_count} immutable GitHub Action references")
    print(f"- {policy_mutation_count} known-bad workflow policy mutations rejected")
    print(
        f"- {release_contract_mutation_count} known-bad release-contract "
        "mutations rejected"
    )
    print(f"- {python_lock_mutation_count} known-bad Python lock mutations rejected")
    print("- 1 exact README Mermaid architecture map")
    print("- Python, Node/npm, Java, ShellCheck, Actionlint, Zizmor, Gitleaks, Mermaid, Markdownlint, and TLA+ toolchains bounded")
    print("- architecture-only public-repository policy; no runtime or Gate A authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
