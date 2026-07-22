#!/usr/bin/env python3
"""Validate Odeya's architecture-only repository release surface.

This checker is deliberately standard-library-only. It verifies retained bytes and
security-relevant workflow shape; Actionlint, Markdownlint, Mermaid, and the full
architecture/formal suites remain separate independent tools.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
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
    ".github/workflows/publication-sequence.yml": "Repository / Publication Sequence",
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
    ".github/workflows/publication-sequence.yml": ("Publication sequence",),
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
    ".github/workflows/publication-sequence.yml": ("publication-sequence",),
}
PUBLICATION_WORKFLOW = ".github/workflows/publication-sequence.yml"
STANDARD_TRIGGER_BLOCK = (
    "on:\n"
    "  pull_request:\n"
    "  push:\n"
    "    branches:\n"
    "      - main\n"
    '      - "release/**"\n'
    "  workflow_dispatch:\n\n"
)
PUBLICATION_TRIGGER_BLOCK = (
    "on:\n"
    "  push:\n"
    "    branches:\n"
    "      - main\n"
    '      - "release/**"\n\n'
)
STANDARD_CHECKOUT_REF = (
    "ref: ${{ github.event.pull_request.head.sha || github.sha }}"
)
PUBLICATION_CHECKOUT_REF = "ref: ${{ github.sha }}"
SHELL_SCRIPTS = (
    ".githooks/pre-push",
    "scripts/ci/install-java.sh",
    "scripts/ci/install-node.sh",
    "scripts/ci/install-actionlint.sh",
    "scripts/ci/install-zizmor.sh",
    "scripts/ci/install-shellcheck.sh",
    "scripts/ci/install-gitleaks.sh",
    "scripts/ci/sanitize-git-environment.sh",
    "scripts/ci/render-readme-architecture.sh",
    "scripts/ci/check-repository-release.sh",
    "scripts/ci/push-rehearsed-head.sh",
    "scripts/ci/rehearse-fresh-clone.sh",
)
EXPECTED_JAVA_TOOLCHAIN = {
    "version": "21.0.9",
    "version_file": ".java-version",
    "distribution": "temurin",
    "release_tag": "jdk-21.0.9+10",
    "release_base": (
        "https://github.com/adoptium/temurin21-binaries/releases/download/"
        "jdk-21.0.9%2B10"
    ),
    "archives": {
        "darwin_amd64": {
            "name": "OpenJDK21U-jdk_x64_mac_hotspot_21.0.9_10.tar.gz",
            "sha256": "f803a3f5bce141f23ac699dfcda06a721f4b74f53bacb0f4bbe9bfcad54427d8",
        },
        "darwin_arm64": {
            "name": "OpenJDK21U-jdk_aarch64_mac_hotspot_21.0.9_10.tar.gz",
            "sha256": "55a40abeb0e174fdc70f769b34b50b70c3967e0b12a643e6a3e23f9a582aac16",
        },
        "linux_amd64": {
            "name": "OpenJDK21U-jdk_x64_linux_hotspot_21.0.9_10.tar.gz",
            "sha256": "810d3773df7e0d6c4394e4e244b264c8b30e0b05a0acf542d065fd78a6b65c2f",
        },
        "linux_arm64": {
            "name": "OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.9_10.tar.gz",
            "sha256": "edf0da4debe7cf475dbe320d174d6eed81479eb363f41e38a2efb740428c603a",
        },
    },
}
EXECUTABLE_SCRIPTS = (
    *SHELL_SCRIPTS,
    "scripts/ci/verify_github_release.py",
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
    "architecture/architecture-surface-policy.json",
    "tools/repository-release/.node-version",
    "tools/repository-release/package.json",
    "tools/repository-release/package-lock.json",
    "tools/repository-release/requirements-architecture.lock",
    "tools/repository-release/toolchain.lock.json",
    "scripts/write_release_evidence_manifest.py",
    "scripts/write_rehearsal_evidence_manifest.py",
    "scripts/compare_rehearsal_manifests.py",
    "scripts/validate_architecture_surface.py",
    "scripts/validate_schema_contracts.py",
    "scripts/validate_contract_profiles.py",
    "scripts/ci/validate_publication_sequence.py",
    "scripts/ci/verify_github_release.py",
    "tests/architecture-surface/README.md",
    "tests/architecture-surface/cases.json",
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
DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS = (
    ("gate-a-prerequisites", "python scripts/validate_gate_a_prerequisites.py"),
    ("prq-009-order", "python scripts/validate_prq_009_assignment_order.py"),
    ("schema-reissue", "python scripts/validate_schema_resource_reissues.py"),
    ("module-manifest", "python scripts/validate_module_manifest.py"),
    ("first-slice-resolution", "python scripts/validate_first_slice_resolution.py"),
    (
        "hda-successor-recompute",
        "python scripts/validate_human_decision_assurance_successor.py --recompute-all",
    ),
)
INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS = (
    ("gate-a-prerequisites", "scripts/validate_gate_a_prerequisites.py"),
    ("prq-009-order", "scripts/validate_prq_009_assignment_order.py"),
    ("schema-reissue", "scripts/validate_schema_resource_reissues.py"),
    ("lifecycle-guard-coverage", "scripts/validate_lifecycle_guard_coverage.py"),
    (
        "lifecycle-condition-coverage",
        "scripts/validate_lifecycle_condition_coverage.py",
    ),
    (
        "canonicalization-dispositions",
        "scripts/validate_canonicalization_dispositions.py",
    ),
    (
        "canonicalization-evaluator-integrity",
        "scripts/validate_canonicalization_evaluator_integrity.py",
    ),
    ("contract-profiles", "scripts/validate_contract_profiles.py"),
    ("refusal-attribution", "scripts/validate_refusal_attribution.py"),
    ("schema-rule-ablation", "scripts/validate_schema_rule_ablation.py"),
    ("suite-guard-coverage", "scripts/validate_suite_guard_coverage.py"),
    (
        "hda-successor",
        "scripts/validate_human_decision_assurance_successor.py",
    ),
)
CARDINAL_WORDS = (
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
)
ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY = (
    f"Reproduce {CARDINAL_WORDS[len(DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS)]} "
    "dedicated prerequisite/member checks: Gate A prerequisites, PRQ-009 order, "
    "schema reissue, module manifest, first-slice scope, and human-decision-assurance "
    f"successor recomputation. `Foundation` separately runs the complete integrated "
    f"{CARDINAL_WORDS[len(INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS)]}-check census"
)
ARCHITECTURE_EVIDENCE_RUN_STEP_START = (
    "      - name: Reproduce architecture evidence checks\n"
    "        run: |\n"
)
ARCHITECTURE_EVIDENCE_RUN_STEP_END = (
    "\n\n      - name: Prove architecture checks did not mutate tracked evidence\n"
)
EXPECTED_ARCHITECTURE_EVIDENCE_RUN_BODY = (
    "          {\n"
    + "".join(
        f"            {command}\n"
        for _, command in DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS
    )
    + "          } 2>&1 | tee artifacts/ci/architecture-evidence.log"
)
EXPECTED_ARCHITECTURE_EVIDENCE_JOB_SHA256 = (
    "320ff9a1f7e9efb0e1247c91bf0aa01e5b5e45e64fcdf68e2fc51b2b3a2d33ef"
)
EXPECTED_INTEGRATED_VALIDATOR_SHA256 = (
    "a70af885d6a7383927401985faef7afd809c30bc9dd7f7b2b4c08b3d552cdf56"
)
ARCHITECTURE_EVIDENCE_KNOWN_BAD_MUTATION_COUNT = (
    len(DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS)
    + len(INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS)
    + 2
)
ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY = (
    "The exact inventory contains "
    f"{CARDINAL_WORDS[ARCHITECTURE_EVIDENCE_KNOWN_BAD_MUTATION_COUNT]} "
    "retained known-bad mutations"
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
    "github-candidate-governance-C.json",
    "github-candidate-checks-C.json",
    "github-promotion-governance-C.json",
    "github-main-checks-C.json",
    "github-governance-mutations-C1.json",
    "github-activation-C2.json",
    "github_repository_activation_receipt",
    "applied_outcome_unknown",
    "update_allows_fetch_and_merge=false",
    "does not authorize runtime",
    ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY,
    ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
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
EXPECTED_WORKFLOW_MUTATION_IDS = (
    "permission-expansion",
    "pull-request-target",
    "explicit-github-token",
    "deployment-environment",
    "missing-timeout",
    "persisted-checkout-credentials",
    "shallow-history",
    "self-hosted-runner",
    "scheduled-trigger",
    "repository-dispatch-trigger",
    "workflow-run-trigger",
    "unexpected-job",
    "missing-fast-architecture-surface-lock",
    "missing-hda-successor-recompute",
    "missing-release-branch-trigger",
    "missing-exact-checkout-ref",
    "publication-pull-request-trigger",
    "publication-workflow-dispatch-trigger",
    "publication-job-skip",
    "publication-continue-on-error",
    "publication-validator-no-op",
)
PUBLICATION_WORKFLOW_MUTATION_IDS = frozenset(
    {
        "publication-pull-request-trigger",
        "publication-workflow-dispatch-trigger",
        "publication-job-skip",
        "publication-continue-on-error",
        "publication-validator-no-op",
    }
)
EXPECTED_FAST_SURFACE_MUTATION = (
    "            python scripts/validate_architecture_surface.py\n",
    "",
    "fast policy architecture-surface/release validation",
)
EXPECTED_HDA_RECOMPUTE_MUTATION = (
    "            python scripts/validate_human_decision_assurance_successor.py --recompute-all\n",
    "",
    "architecture evidence exact toolchain/recomputation contract",
)
EXPECTED_ARCHITECTURE_EVIDENCE_INVENTORY_MUTATIONS = {
    **{
        f"missing-dedicated-{mutation_name}": (
            ".github/workflows/architecture.yml",
            f"            {command}\n",
            "",
            "architecture evidence exact command census",
        )
        for mutation_name, command in DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS
    },
    "unexpected-dedicated-execution-step": (
        ".github/workflows/architecture.yml",
        ARCHITECTURE_EVIDENCE_RUN_STEP_START,
        "      - name: Run a seventh dedicated architecture check\n"
        "        run: python scripts/validate_contract_profiles.py\n\n"
        + ARCHITECTURE_EVIDENCE_RUN_STEP_START,
        "architecture evidence executable job bytes must be exact",
    ),
    **{
        f"missing-integrated-{mutation_name}": (
            "scripts/validate.py",
            f'    "{relative}",\n',
            "",
            "integrated architecture evidence inventory must be exact",
        )
        for mutation_name, relative in INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS
    },
    "post-assignment-integrated-rebinding": (
        "scripts/validate.py",
        ")\nREPOSITORY_RELEASE_CHECKS = (\n",
        ")\n"
        'globals()["ARCHITECTURE_EVIDENCE_CHECKS"] = (\n'
        "    ARCHITECTURE_EVIDENCE_CHECKS[:-1]\n"
        '    + ("scripts/validate_repository_release.py",)\n'
        ")\n"
        "REPOSITORY_RELEASE_CHECKS = (\n",
        "integrated architecture evidence executable bytes must be exact",
    ),
}
REHEARSAL_TOOL_CACHE_BLOCK = (
    'ODEYA_TOOL_CACHE="$REHEARSAL_ROOT/tool-cache"\n'
    "readonly ODEYA_TOOL_CACHE\n"
    "export ODEYA_TOOL_CACHE\n"
)
REHEARSAL_TLA_BINDING_BLOCK = (
    'TLA2TOOLS_JAR="$TLA_JAR"\n'
    "readonly TLA2TOOLS_JAR\n"
    "export TLA2TOOLS_JAR\n"
    "bash formal/tla/check.sh"
)
STANDALONE_TOOL_CACHE_BLOCK = (
    "OWN_TOOL_CACHE=0\n"
    'if [[ -z "${ODEYA_TOOL_CACHE:-}" ]]; then\n'
    '  ODEYA_TOOL_CACHE="$(mktemp -d "${TMPDIR:-/tmp}/odeya-release-tools.XXXXXX")"\n'
    "  OWN_TOOL_CACHE=1\n"
    "fi\n"
    "readonly ODEYA_TOOL_CACHE\n"
    "readonly OWN_TOOL_CACHE\n"
    "export ODEYA_TOOL_CACHE\n"
)
EXPECTED_RELEASE_SCRIPT_MUTATIONS = {
    "shared-rehearsal-tool-cache": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_TOOL_CACHE_BLOCK,
        'ODEYA_TOOL_CACHE="${TMPDIR:-/tmp}/odeya-release-tools"\n'
        "readonly ODEYA_TOOL_CACHE\n"
        "export ODEYA_TOOL_CACHE\n",
        "fresh-clone rehearsal must allocate one per-rehearsal tool cache",
    ),
    "unbound-rehearsal-tla-jar": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_TLA_BINDING_BLOCK,
        "bash formal/tla/check.sh",
        "fresh-clone rehearsal must bind TLA2TOOLS_JAR to its verified jar",
    ),
    "shared-standalone-tool-cache": (
        "scripts/ci/check-repository-release.sh",
        STANDALONE_TOOL_CACHE_BLOCK,
        'ODEYA_TOOL_CACHE="${TMPDIR:-/tmp}/odeya-release-tools"\n'
        "readonly ODEYA_TOOL_CACHE\n"
        "export ODEYA_TOOL_CACHE\n",
        "standalone release check must allocate a unique tool cache",
    ),
}
EXPECTED_RELEASE_CONTRACT_MUTATIONS = {
    "stale-architecture-evidence-counts": (
        ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY,
        "Reproduce five dedicated prerequisite/member checks: Gate A prerequisites, "
        "PRQ-009 order, schema reissue, module manifest, first-slice scope, and "
        "human-decision-assurance successor recomputation. `Foundation` separately "
        "runs the complete integrated ten-check census",
        "Reproduce six dedicated prerequisite/member checks",
    ),
    "stale-architecture-evidence-mutation-count": (
        ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
        "The exact inventory contains seventeen retained known-bad mutations",
        ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
    ),
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
    if lock.get("java") != EXPECTED_JAVA_TOOLCHAIN:
        errors.append("toolchain lock: Java toolchain metadata is not the exact Temurin lock")
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


def integrated_architecture_evidence_assignment(
    text: str,
) -> tuple[ast.Module | None, ast.Assign | None, list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return None, None, [
            f"integrated architecture evidence inventory cannot be parsed: {exc}"
        ]

    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name)
            and target.id == "ARCHITECTURE_EVIDENCE_CHECKS"
            for target in node.targets
        )
    ]
    if len(assignments) != 1:
        return tree, None, [
            "integrated architecture evidence inventory assignment must exist exactly once"
        ]
    return tree, assignments[0], []


def integrated_architecture_evidence_inventory_errors(text: str) -> list[str]:
    """Bind Foundation's reported evidence-check count to its executable tuple."""

    errors: list[str] = []
    observed_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if observed_sha256 != EXPECTED_INTEGRATED_VALIDATOR_SHA256:
        errors.append(
            "integrated architecture evidence executable bytes must be exact: "
            f"expected {EXPECTED_INTEGRATED_VALIDATOR_SHA256}, got {observed_sha256}"
        )

    tree, assignment, assignment_errors = (
        integrated_architecture_evidence_assignment(text)
    )
    errors.extend(assignment_errors)
    if tree is None or assignment is None:
        return errors
    try:
        observed = ast.literal_eval(assignment.value)
    except (TypeError, ValueError, SyntaxError):
        errors.append(
            "integrated architecture evidence inventory must be a literal tuple"
        )
        return errors

    expected = tuple(
        relative for _, relative in INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS
    )
    if observed != expected:
        errors.append(
            "integrated architecture evidence inventory must be exact: "
            f"expected {expected}, got {observed!r}"
        )

    references = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "ARCHITECTURE_EVIDENCE_CHECKS"
    ]
    if (
        len(references) != 2
        or sum(isinstance(node.ctx, ast.Store) for node in references) != 1
        or sum(isinstance(node.ctx, ast.Load) for node in references) != 1
    ):
        errors.append(
            "integrated architecture evidence binding must have exactly one literal "
            "definition and one executable consumption"
        )

    consumers = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "validate_architecture_evidence_checks"
    ]
    consumption_loops = []
    if len(consumers) == 1:
        consumption_loops = [
            node
            for node in ast.walk(consumers[0])
            if isinstance(node, ast.For)
            and isinstance(node.target, ast.Name)
            and node.target.id == "relative"
            and isinstance(node.iter, ast.Name)
            and node.iter.id == "ARCHITECTURE_EVIDENCE_CHECKS"
        ]
    if len(consumers) != 1 or len(consumption_loops) != 1:
        errors.append(
            "integrated architecture evidence inventory must have one exact "
            "Foundation consumption loop"
        )
    return errors


def workflow_policy_errors(
    text: str,
    relative: str,
    expected_job_ids: tuple[str, ...] | None = None,
) -> list[str]:
    issues: list[str] = []
    publication = relative == PUBLICATION_WORKFLOW
    trigger_block = PUBLICATION_TRIGGER_BLOCK if publication else STANDARD_TRIGGER_BLOCK
    trigger_match = re.search(r"(?ms)^on:\n.*?(?=^permissions:\n)", text)
    if trigger_match is None or trigger_match.group(0) != trigger_block:
        if publication:
            issues.append(
                "trigger block must be exactly push main and release/** only"
            )
        else:
            issues.append(
                "trigger block must be exactly pull_request, push main and "
                "release/**, workflow_dispatch"
            )
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
    hosted_runner_count = len(
        re.findall(r"(?m)^\s+runs-on:\s*ubuntu-24\.04\s*$", text)
    )
    if runner_count < 1 or runner_count != hosted_runner_count:
        issues.append("runner must be the exact GitHub-hosted ubuntu-24.04 label")
    timeout_count = len(
        re.findall(r"(?m)^\s+timeout-minutes:\s*[0-9]+\s*$", text)
    )
    if timeout_count != runner_count:
        issues.append("timeout must exist for every job")

    checkout_count = text.count("uses: actions/checkout@")
    persisted_false = text.count("persist-credentials: false")
    full_history = text.count("fetch-depth: 0")
    if (
        checkout_count < 1
        or persisted_false != checkout_count
        or full_history != checkout_count
    ):
        issues.append("checkout must fetch full history without persisted credentials")
    expected_checkout_ref = (
        PUBLICATION_CHECKOUT_REF if publication else STANDARD_CHECKOUT_REF
    )
    if text.count(expected_checkout_ref) != checkout_count:
        issues.append(
            f"checkout must pin the exact ref expression {expected_checkout_ref!r}"
        )
    if "concurrency:" not in text or "cancel-in-progress: true" not in text:
        issues.append("concurrency cancellation is required")
    if "shell: bash" not in text:
        issues.append("explicit bash with GitHub pipefail defaults is required")
    jobs_marker = "\njobs:\n"
    if jobs_marker not in text:
        issues.append("job inventory is absent")
    elif expected_job_ids is not None:
        jobs_text = text.split(jobs_marker, 1)[1]
        observed_job_ids = tuple(
            re.findall(r"(?m)^  ([A-Za-z0-9_-]+):\s*$", jobs_text)
        )
        if observed_job_ids != expected_job_ids:
            issues.append(
                f"job inventory must be exact: expected {expected_job_ids}, "
                f"got {observed_job_ids}"
            )
    if relative == ".github/workflows/architecture.yml":
        fast_policy_marker = "  fast-policy:\n"
        foundation_marker = "\n  foundation:\n"
        if fast_policy_marker not in text or foundation_marker not in text:
            issues.append("fast policy job boundary is absent")
        else:
            fast_policy = text.split(fast_policy_marker, 1)[1].split(
                foundation_marker, 1
            )[0]
            required_fast_commands = (
                "python scripts/validate_architecture_surface.py",
                "python scripts/validate_repository_release.py",
            )
            for command in required_fast_commands:
                if fast_policy.count(command) != 1:
                    issues.append(
                        "fast policy architecture-surface/release validation "
                        f"must run exactly once: {command}"
                    )
        architecture_evidence_marker = "\n  architecture-evidence:\n"
        if text.count(architecture_evidence_marker) != 1:
            issues.append("architecture evidence job boundary is absent or duplicated")
        else:
            architecture_evidence = text.split(architecture_evidence_marker, 1)[1]
            architecture_evidence_job = (
                "  architecture-evidence:\n" + architecture_evidence
            )
            observed_job_sha256 = hashlib.sha256(
                architecture_evidence_job.encode("utf-8")
            ).hexdigest()
            if observed_job_sha256 != EXPECTED_ARCHITECTURE_EVIDENCE_JOB_SHA256:
                issues.append(
                    "architecture evidence executable job bytes must be exact: "
                    f"expected {EXPECTED_ARCHITECTURE_EVIDENCE_JOB_SHA256}, "
                    f"got {observed_job_sha256}"
                )
            if (
                architecture_evidence.count(ARCHITECTURE_EVIDENCE_RUN_STEP_START) != 1
                or architecture_evidence.count(ARCHITECTURE_EVIDENCE_RUN_STEP_END) != 1
            ):
                issues.append(
                    "architecture evidence exact command census boundary is absent or duplicated"
                )
            else:
                observed_run_body = architecture_evidence.split(
                    ARCHITECTURE_EVIDENCE_RUN_STEP_START, 1
                )[1].split(ARCHITECTURE_EVIDENCE_RUN_STEP_END, 1)[0]
                if observed_run_body != EXPECTED_ARCHITECTURE_EVIDENCE_RUN_BODY:
                    expected_commands = tuple(
                        command
                        for _, command in DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS
                    )
                    issues.append(
                        "architecture evidence exact command census must match the "
                        f"pinned inventory {expected_commands}"
                    )
            required_architecture_evidence_fragments = (
                "    timeout-minutes: 20\n",
                "        run: printf 'ODEYA_TOOL_CACHE=%s/odeya-release-tools\\n' \"$RUNNER_TEMP\" >> \"$GITHUB_ENV\"\n",
                "              --require-hashes \\\n",
                "              --only-binary=:all: \\\n",
                "              --report artifacts/ci/architecture-evidence-pip-install-report.json \\\n",
                "              --requirement tools/repository-release/requirements-architecture.lock\n",
                '            node_bin="$(bash scripts/ci/install-node.sh)"\n',
                '            java_bin="$(bash scripts/ci/install-java.sh)"\n',
                "            python scripts/validate_human_decision_assurance_successor.py --recompute-all\n",
                "          git diff --exit-code\n",
                "          git diff --cached --exit-code\n",
                "          path: artifacts/ci/\n",
                "          if-no-files-found: error\n",
            )
            for fragment in required_architecture_evidence_fragments:
                if architecture_evidence.count(fragment) != 1:
                    issues.append(
                        "architecture evidence exact toolchain/recomputation contract "
                        f"must retain exactly one {fragment.strip()!r}"
                    )
    if publication:
        if runner_count != 1 or text.count("    timeout-minutes: 5\n") != 1:
            issues.append("publication job must use exactly one five-minute timeout")
        conditionals = re.findall(r"(?m)^\s+if:\s*(.+?)\s*$", text)
        if conditionals != ["${{ always() }}"]:
            issues.append(
                "publication validation and clean-tree steps may not be "
                "conditional or skipped"
            )
        if "continue-on-error:" in text:
            issues.append("publication job may not continue on error")
        if "|| true" in text or re.search(r";\s*true\s*$", text, re.MULTILINE):
            issues.append("publication job may not suppress command failure")
        required_publication_steps = (
            'python scripts/ci/validate_publication_sequence.py --ci-event "$GITHUB_EVENT_PATH" --repo .',
            "2>&1 | tee artifacts/ci/publication-sequence.log",
            "run: git diff --exit-code",
            "if: ${{ always() }}",
            "path: artifacts/ci/publication-sequence.log",
            "if-no-files-found: error",
        )
        for required in required_publication_steps:
            if text.count(required) != 1:
                issues.append(
                    "publication job must retain the exact validator, clean-tree, "
                    f"and evidence steps; expected one {required!r}"
                )
    return issues


def validate_policy_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict) or not isinstance(cases.get("mutations"), list):
        return 0
    if set(cases) != {
        "schema_version",
        "base_workflow",
        "mutations",
        "architecture_evidence_inventory_mutations",
        "release_contract",
        "release_contract_mutations",
        "release_script_mutations",
    }:
        errors.append("repository release mutations: top-level members are not exact")
    if cases.get("schema_version") != "0.1.0":
        errors.append("repository release mutations: schema_version is not exact")
    base_relative = cases.get("base_workflow")
    if base_relative != ".github/workflows/architecture.yml":
        errors.append("repository release mutations: base_workflow is not exact")
        return 0
    mutations = cases["mutations"]
    observed_ids = [
        case.get("id")
        for case in mutations
        if isinstance(case, dict)
    ]
    if (
        len(observed_ids) != len(mutations)
        or any(not isinstance(case_id, str) for case_id in observed_ids)
        or len(set(observed_ids)) != len(observed_ids)
        or tuple(observed_ids) != EXPECTED_WORKFLOW_MUTATION_IDS
    ):
        errors.append(
            "repository release mutations: workflow case census/order is not closed and exact"
        )
    workflow_texts = {
        base_relative: read(base_relative, errors),
        PUBLICATION_WORKFLOW: read(PUBLICATION_WORKFLOW, errors),
    }
    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append("repository release mutations: case is not an object")
            continue
        case_id = case.get("id")
        publication_case = case_id in PUBLICATION_WORKFLOW_MUTATION_IDS
        expected_members = {"id", "old", "new", "expected"}
        if publication_case:
            expected_members.add("workflow")
        if set(case) != expected_members:
            errors.append(
                "repository release mutations: case members are not closed and exact"
            )
            continue
        relative = case.get("workflow", base_relative)
        if publication_case and relative != PUBLICATION_WORKFLOW:
            errors.append(
                f"repository release mutation {case_id}: publication workflow is not exact"
            )
            continue
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if (
            not all(
                isinstance(value, str) and value
                for value in (case_id, relative, old, expected)
            )
            or not isinstance(new, str)
        ):
            errors.append("repository release mutations: malformed case")
            continue
        if (
            case_id == "missing-fast-architecture-surface-lock"
            and (old, new, expected) != EXPECTED_FAST_SURFACE_MUTATION
        ):
            errors.append(
                "repository release mutation missing-fast-architecture-surface-lock: "
                "specification drifted from the pinned matrix"
            )
            continue
        if (
            case_id == "missing-hda-successor-recompute"
            and (old, new, expected) != EXPECTED_HDA_RECOMPUTE_MUTATION
        ):
            errors.append(
                "repository release mutation missing-hda-successor-recompute: "
                "specification drifted from the pinned matrix"
            )
            continue
        base = workflow_texts[relative]
        if base.count(old) < 1:
            errors.append(f"repository release mutation {case_id}: source bytes are absent")
            continue
        mutated = base.replace(old, new, 1)
        mutation_issues = workflow_policy_errors(
            mutated, relative, REQUIRED_JOB_IDS.get(relative)
        )
        if not any(expected in issue for issue in mutation_issues):
            errors.append(
                f"repository release mutation {case_id}: expected {expected!r} refusal, "
                f"got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


def validate_architecture_evidence_inventory_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    mutations = cases.get("architecture_evidence_inventory_mutations")
    if not isinstance(mutations, list):
        errors.append(
            "architecture evidence inventory mutations: inventory is absent"
        )
        return 0
    if (
        len(EXPECTED_ARCHITECTURE_EVIDENCE_INVENTORY_MUTATIONS)
        != ARCHITECTURE_EVIDENCE_KNOWN_BAD_MUTATION_COUNT
    ):
        errors.append(
            "architecture evidence inventory mutations: executable census does not "
            "match the release-contract count boundary"
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
        or tuple(observed_ids)
        != tuple(EXPECTED_ARCHITECTURE_EVIDENCE_INVENTORY_MUTATIONS)
    ):
        errors.append(
            "architecture evidence inventory mutations: case census/order is not "
            "closed and exact"
        )

    base_documents = {
        ".github/workflows/architecture.yml": read(
            ".github/workflows/architecture.yml", errors
        ),
        "scripts/validate.py": read("scripts/validate.py", errors),
    }
    errors.extend(
        f"scripts/validate.py: {issue}"
        for issue in integrated_architecture_evidence_inventory_errors(
            base_documents["scripts/validate.py"]
        )
    )

    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append(
                "architecture evidence inventory mutations: case is not an object"
            )
            continue
        if set(case) != {"id", "subject", "old", "new", "expected"}:
            errors.append(
                "architecture evidence inventory mutations: case members are not "
                "closed and exact"
            )
            continue
        case_id = case.get("id")
        subject = case.get("subject")
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if not all(
            isinstance(value, str) and value
            for value in (case_id, subject, old, expected)
        ) or not isinstance(new, str):
            errors.append("architecture evidence inventory mutations: malformed case")
            continue
        expected_spec = EXPECTED_ARCHITECTURE_EVIDENCE_INVENTORY_MUTATIONS.get(
            case_id
        )
        if expected_spec != (subject, old, new, expected):
            errors.append(
                f"architecture evidence inventory mutation {case_id}: "
                "specification drifted from the executable inventory"
            )
            continue
        base = base_documents.get(subject)
        if base is None:
            errors.append(
                f"architecture evidence inventory mutation {case_id}: "
                "subject is not admitted"
            )
            continue
        if subject == ".github/workflows/architecture.yml":
            if base.count(old) != 1:
                errors.append(
                    f"architecture evidence inventory mutation {case_id}: expected "
                    f"one source occurrence, found {base.count(old)}"
                )
                continue
            mutated = base.replace(old, new, 1)
            mutation_issues = workflow_policy_errors(
                mutated,
                subject,
                REQUIRED_JOB_IDS[subject],
            )
        else:
            _, assignment, assignment_errors = (
                integrated_architecture_evidence_assignment(base)
            )
            if case_id == "post-assignment-integrated-rebinding":
                if base.count(old) != 1:
                    errors.append(
                        f"architecture evidence inventory mutation {case_id}: "
                        f"expected one source occurrence, found {base.count(old)}"
                    )
                    continue
                mutated = base.replace(old, new, 1)
            elif assignment is None or assignment.end_lineno is None:
                errors.extend(
                    f"architecture evidence inventory mutation {case_id}: {issue}"
                    for issue in assignment_errors
                )
                continue
            else:
                lines = base.splitlines(keepends=True)
                start = assignment.lineno - 1
                end = assignment.end_lineno
                assignment_text = "".join(lines[start:end])
                if assignment_text.count(old) != 1:
                    errors.append(
                        f"architecture evidence inventory mutation {case_id}: expected "
                        "one occurrence in ARCHITECTURE_EVIDENCE_CHECKS, found "
                        f"{assignment_text.count(old)}"
                    )
                    continue
                mutated_assignment = assignment_text.replace(old, new, 1)
                mutated = (
                    "".join(lines[:start])
                    + mutated_assignment
                    + "".join(lines[end:])
                )
            mutation_issues = integrated_architecture_evidence_inventory_errors(
                mutated
            )
        if not any(expected in issue for issue in mutation_issues):
            errors.append(
                f"architecture evidence inventory mutation {case_id}: expected "
                f"{expected!r} refusal, got {mutation_issues}"
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


def release_script_isolation_errors(rehearsal: str, release_check: str) -> list[str]:
    errors: list[str] = []
    if rehearsal.count(REHEARSAL_TOOL_CACHE_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must allocate one per-rehearsal tool cache"
        )
    if rehearsal.count(REHEARSAL_TLA_BINDING_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must bind TLA2TOOLS_JAR to its verified jar"
        )
    if release_check.count(STANDALONE_TOOL_CACHE_BLOCK) != 1:
        errors.append("standalone release check must allocate a unique tool cache")
    return errors


def validate_release_script_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    mutations = cases.get("release_script_mutations")
    if not isinstance(mutations, list):
        errors.append("repository release script mutations: inventory is absent")
        return 0
    observed_ids = [
        case.get("id")
        for case in mutations
        if isinstance(case, dict)
    ]
    if (
        len(observed_ids) != len(mutations)
        or any(not isinstance(case_id, str) for case_id in observed_ids)
        or len(set(observed_ids)) != len(observed_ids)
        or set(observed_ids) != set(EXPECTED_RELEASE_SCRIPT_MUTATIONS)
    ):
        errors.append(
            "repository release script mutations: case census is not closed and exact"
        )
    base_documents = {
        relative: read(relative, errors)
        for relative in {
            "scripts/ci/rehearse-fresh-clone.sh",
            "scripts/ci/check-repository-release.sh",
        }
    }
    errors.extend(
        release_script_isolation_errors(
            base_documents["scripts/ci/rehearse-fresh-clone.sh"],
            base_documents["scripts/ci/check-repository-release.sh"],
        )
    )
    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append(
                "repository release script mutations: case is not an object"
            )
            continue
        if set(case) != {"id", "subject", "old", "new", "expected"}:
            errors.append(
                "repository release script mutations: case members are not closed and exact"
            )
            continue
        case_id = case.get("id")
        subject = case.get("subject")
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if not all(
            isinstance(value, str) and value
            for value in (case_id, subject, old, new, expected)
        ):
            errors.append("repository release script mutations: malformed case")
            continue
        expected_spec = EXPECTED_RELEASE_SCRIPT_MUTATIONS.get(case_id)
        if expected_spec != (subject, old, new, expected):
            errors.append(
                f"repository release script mutation {case_id}: "
                "specification drifted from the pinned matrix"
            )
            continue
        base = base_documents.get(subject)
        if base is None:
            errors.append(
                f"repository release script mutation {case_id}: subject is not admitted"
            )
            continue
        if base.count(old) != 1:
            errors.append(
                f"repository release script mutation {case_id}: "
                f"expected one source occurrence, found {base.count(old)}"
            )
            continue
        mutated_documents = dict(base_documents)
        mutated_documents[subject] = base.replace(old, new, 1)
        mutation_issues = release_script_isolation_errors(
            mutated_documents["scripts/ci/rehearse-fresh-clone.sh"],
            mutated_documents["scripts/ci/check-repository-release.sh"],
        )
        if not any(expected in issue for issue in mutation_issues):
            errors.append(
                f"repository release script mutation {case_id}: expected "
                f"{expected!r} refusal, got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


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
        for issue in workflow_policy_errors(text, relative, REQUIRED_JOB_IDS[relative]):
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
    java_installer = read("scripts/ci/install-java.sh", errors)
    java = lock.get("java", {}) if isinstance(lock, dict) else {}
    java_version = str(java.get("version", ""))
    java_release_tag = str(java.get("release_tag", ""))
    java_release_base = str(java.get("release_base", ""))
    if f'readonly VERSION="{java_version}"' not in java_installer:
        errors.append("install-java.sh: version does not match toolchain lock")
    if f'readonly RELEASE_TAG="{java_release_tag}"' not in java_installer:
        errors.append("install-java.sh: release tag does not match toolchain lock")
    if f'readonly RELEASE_BASE="{java_release_base}"' not in java_installer:
        errors.append("install-java.sh: release base does not match toolchain lock")
    for platform, archive in java.get("archives", {}).items():
        if not isinstance(archive, dict):
            errors.append(f"install-java.sh: invalid locked archive {platform}")
            continue
        archive_name = archive.get("name")
        digest = archive.get("sha256")
        if (
            platform not in java_installer
            or not isinstance(archive_name, str)
            or archive_name not in java_installer
            or not isinstance(digest, str)
            or digest not in java_installer
        ):
            errors.append(f"install-java.sh: missing locked archive {platform}")

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
        'validate_publication_sequence.py" --self-test',
        'push-rehearsed-head.sh" --self-test',
        'verify_github_release.py" --self-test',
        'tee -a "$WORK_EVIDENCE_ROOT/final-release-contract.log"',
        'CURRENT_STAGE="publication-sequence-self-test"',
        'CURRENT_STAGE="github-release-verifier-self-test"',
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
        ".githooks/pre-push",
    ):
        if required not in release_check:
            errors.append(f"check-repository-release.sh: missing step {required!r}")
    retained_self_test_target = (
        'tee -a "$WORK_EVIDENCE_ROOT/final-release-contract.log"'
    )
    if release_check.count(retained_self_test_target) != 2:
        errors.append(
            "check-repository-release.sh: both publication self-tests must append "
            "to the existing final-release-contract log"
        )

    pre_push = read(".githooks/pre-push", errors)
    for required in (
        "a governed publication push must update exactly one ref",
        "validate_publication_sequence.py",
        "candidate-governance",
        "verify_github_release.py\" governance",
        'checks \\\n    --sha "$local_sha"',
        "exact release candidate ref is absent or moved",
        "compare_rehearsal_manifests.py",
        '--expected-subject-commit "$main_sha"',
        "url.*.insteadOf can redirect",
        "ODEYA_EXPECTED_PUBLICATION_SOURCE_REF",
        "ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA",
        "governed publication tuple does not match frozen helper source",
        "publication source must remain the attached worktree branch",
        "publishing worktree status could not be observed",
    ):
        if required not in pre_push:
            errors.append(f".githooks/pre-push: missing publication gate {required!r}")

    publication_helper = read("scripts/ci/push-rehearsed-head.sh", errors)
    for required in (
        "candidate|promote|status",
        "candidate-governance",
        "verify_github_release.py governance",
        'ls-remote --refs \\\n      "$CANONICAL_REMOTE_URL" "${RELEASE_PREFIX}*"',
        "Resuming immutable candidate",
        "Resuming post-main verification",
        "rehearse-fresh-clone.sh",
        "compare_rehearsal_manifests.py",
        "verify_completed_main",
        "--verify-existing",
        "first-create||||candidate-bootstrap",
        "first-resume|a|${current_row}||candidate-bootstrap",
        "later-create||${other_row}|${other_row}|full",
        "later-resume|a|${combined_rows}|${other_row}|full",
        "Publication helper state self-test PASSED",
        "Publication helper validator-scope self-test PASSED",
        "Publication helper source-ref self-test PASSED",
        "Publication helper clean-worktree self-test PASSED",
        "Publication helper pre-push binding self-test PASSED",
        "symbolic-ref --quiet HEAD",
        'git push "$REMOTE" "$SOURCE_REF:$destination_ref"',
        'ODEYA_EXPECTED_PUBLICATION_SOURCE_REF="$SOURCE_REF"',
        'ODEYA_EXPECTED_PUBLICATION_SOURCE_SHA="$COMMIT"',
        'push_governed_ref "$RELEASE_REF"',
        'push_governed_ref "$MAIN_REF"',
        "github-candidate-governance-$COMMIT.json",
        "github-candidate-checks-$COMMIT.json",
        "github-promotion-governance-$COMMIT.json",
        "github-main-checks-$COMMIT.json",
        "ODEYA_ACTIVATION_BOOTSTRAP_SHA",
        "github-governance-mutations-$ACTIVATION_BOOTSTRAP_SHA.json",
        "verify_github_release.py activation-evidence",
        "--candidate-checks-receipt \"$CANDIDATE_CHECKS_RECEIPT\"",
        "--promotion-governance-receipt \"$PROMOTION_GOVERNANCE_RECEIPT\"",
        "--comparison-receipt \"$COMPARISON_RECEIPT\"",
        "No one-time GitHub activation claim was requested",
        "--receipt-phase candidate",
        "--receipt-phase promotion",
        'candidate-governance \\\n'
        '      --sha "$COMMIT" \\\n'
        '      --output "$CANDIDATE_GOVERNANCE_RECEIPT"',
        'verify_github_release.py governance \\\n'
        '      --sha "$COMMIT" \\\n'
        '      --receipt-phase candidate \\\n'
        '      --output "$CANDIDATE_GOVERNANCE_RECEIPT"',
        'verify_github_release.py governance \\\n'
        '  --sha "$COMMIT" \\\n'
        '  --receipt-phase promotion \\\n'
        '  --output "$PROMOTION_GOVERNANCE_RECEIPT"',
        '--output "$CANDIDATE_CHECKS_RECEIPT"',
        '--output "$MAIN_CHECKS_RECEIPT"',
        "Existing comparison receipt revalidated for resume",
        "immutable candidate provenance moved",
        "canonical main moved before final settlement",
    ):
        if required not in publication_helper:
            errors.append(
                "push-rehearsed-head.sh: missing exact publication state "
                f"{required!r}"
            )

    github_verifier = read("scripts/ci/verify_github_release.py", errors)
    for required in (
        "activation-evidence",
        "--bootstrap-checks-receipt",
        "--candidate-checks-receipt",
        "--promotion-governance-receipt",
        "--main-checks-receipt",
        "--comparison-receipt",
        "--local-evidence",
        "--remote-evidence",
        "github_governance_mutation_journal",
        "github_repository_activation_receipt",
        "candidate_checks_sha256",
        "promotion_governance_sha256",
        "comparison_receipt_sha256",
        "parent_bindings",
        "final_check_censuses",
        "revalidate_comparison_receipt",
        "activation commit observation census is not exact",
        "The critical mutable main ref is intentionally the final GitHub request",
    ):
        if required not in github_verifier:
            errors.append(
                "verify_github_release.py: missing final activation contract "
                f"{required!r}"
            )

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

    for relative in EXECUTABLE_SCRIPTS:
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
        "build_comparison_receipt",
        "verify_comparison_receipt",
        "reject_symlink_components",
        "path contains a symlink",
        "comparison receipt is not one real regular file",
        "comparison evidence names a historical subject",
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
    "scripts/validate_architecture_surface.py",
    "scripts/validate_repository_release.py",
    "scripts/ci/validate_publication_sequence.py",
    "scripts/ci/verify_github_release.py",
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
                local_candidates = (
                    path.parent / f"{name}.py",
                    ROOT / "scripts" / f"{name}.py",
                )
                local_module = next(
                    (candidate for candidate in local_candidates if candidate.is_file()),
                    None,
                )
                if local_module is not None:
                    queue.append(str(local_module.relative_to(ROOT)))
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
    architecture_evidence_inventory_mutation_count = (
        validate_architecture_evidence_inventory_mutations(errors)
    )
    release_contract_mutation_count = validate_release_contract_mutations(errors)
    release_script_mutation_count = validate_release_script_mutations(errors)
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
        f"- {architecture_evidence_inventory_mutation_count} known-bad "
        "architecture-evidence inventory mutations rejected"
    )
    print(
        f"- {release_contract_mutation_count} known-bad release-contract "
        "mutations rejected"
    )
    print(
        f"- {release_script_mutation_count} known-bad release-script isolation "
        "mutations rejected"
    )
    print(f"- {python_lock_mutation_count} known-bad Python lock mutations rejected")
    print("- 1 exact README Mermaid architecture map")
    print("- Python, Node/npm, Java, ShellCheck, Actionlint, Zizmor, Gitleaks, Mermaid, Markdownlint, and TLA+ toolchains bounded")
    print("- architecture-only public-repository policy; no runtime or Gate A authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
