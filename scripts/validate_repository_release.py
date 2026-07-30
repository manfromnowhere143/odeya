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
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MERMAID_DOCUMENTS = {
    "README.md": 1,
    "docs/ARCHITECTURE.md": 3,
    "docs/COGNITIVE_ARCHITECTURE.md": 1,
    "docs/HUMAN_DECISION_ASSURANCE.md": 2,
}
MERMAID_UNSAFE_PATTERNS = (
    (
        "click directive",
        re.compile(r"(?im)(?:^|;)[ \t]*click(?:[ \t]|$)"),
    ),
    ("configuration directive", re.compile(r"%%[ \t]*\{")),
    (
        "YAML frontmatter",
        re.compile(r"\A(?:\ufeff)?[ \t]*---[ \t]*\r?\n"),
    ),
    ("javascript URI", re.compile(r"(?i)javascript[ \t]*:")),
    (
        "image asset property",
        re.compile(
            r"(?i)(?:^|[ \t\r\n,{])(?:img|\"img\"|'img')[ \t]*:"
        ),
    ),
    (
        "attribute object",
        re.compile(r"@[ \t]*\{"),
    ),
    (
        "HTML image element",
        re.compile(r"(?i)<[ \t]*img(?:[ \t/>])"),
    ),
    (
        "CSS resource URL",
        re.compile(r"(?i)\burl[ \t]*\("),
    ),
    (
        "Markdown image",
        re.compile(r"!\[[^\]\r\n]*\][ \t]*\("),
    ),
    (
        "resource URI scheme",
        re.compile(r"(?i)(?<![A-Za-z0-9_])(?:https?|file|data|blob|ftp)[ \t]*:"),
    ),
    (
        "protocol-relative resource location",
        re.compile(r"(?<![:/])//[A-Za-z0-9._~\-\[]"),
    ),
)
FENCED_CODE_OPEN = re.compile(
    r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)$"
)
MERMAID_FENCE_MARKER = re.compile(
    r"(?i)(?:`{3,}|~{3,})[ \t]*"
    r"(?:mermaid(?=[ \t]|$)|\{[ \t]*\.mermaid(?:[ \t}]|$))"
)
MERMAID_RENDERER_SHA256 = (
    "8e0f253fa055a17e5a1a83ac469d2e1d190505b91e4360b11f7bedf805746879"
)
TRACKED_PATH_CENSUS_COMMAND = ("git", "ls-files", "-z")
OPENING_SENTENCE = (
    "Odeya is the architecture foundation for a private research engine that "
    "turns a thesis into a governed, replayable chain from question to evidence "
    "to warranted claim."
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
    "scripts/validate_schema_registry_prehash_replay.py",
    "scripts/ci/validate_publication_sequence.py",
    "scripts/ci/verify_github_release.py",
    "tests/architecture-surface/README.md",
    "tests/architecture-surface/cases.json",
    "tests/repository-release/README.md",
    "tests/repository-release/cases.json",
    "tests/schema-registry-prehash-replay/node/package.json",
    "tests/schema-registry-prehash-replay/node/package-lock.json",
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
        "prq-002-identity-probe",
        "python tests/prq-002-identity-cohort/check.py --recompute-all "
        '--python-executable "$ODEYA_PRQ002_PYTHON" '
        '--node-executable "$ODEYA_PRQ002_NODE"',
    ),
    (
        "prq-002c-raw-number-typing",
        "python scripts/validate_product_identity_raw_number_typing.py "
        "--recompute-all "
        '--python-executable "$ODEYA_PRQ002_PYTHON" '
        '--node-executable "$ODEYA_PRQ002_NODE"',
    ),
    (
        "prq-002d-schema-registry-prehash-replay",
        "python scripts/validate_schema_registry_prehash_replay.py "
        "--recompute-all "
        '--python-executable "$ODEYA_PRQ002_PYTHON" '
        '--node-executable "$ODEYA_PRQ002_NODE"',
    ),
    (
        "prq-002e-profile-0.3-construction",
        "python tests/product-identity-profile-0.3-candidate/authoring/"
        "generate_candidate.py --check && "
        "python tests/product-identity-profile-0.3-candidate/check.py",
    ),
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
        "prq-002c-raw-number-typing",
        "scripts/validate_product_identity_raw_number_typing.py",
    ),
    (
        "prq-002d-schema-registry-prehash-replay",
        "scripts/validate_schema_registry_prehash_replay.py",
    ),
    (
        "prq-002e-profile-0.3-construction",
        "tests/product-identity-profile-0.3-candidate/check.py",
    ),
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
    "twenty-one",
    "twenty-two",
    "twenty-three",
    "twenty-four",
    "twenty-five",
    "twenty-six",
    "twenty-seven",
)
ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY = (
    f"Reproduce {CARDINAL_WORDS[len(DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS)]} "
    "dedicated prerequisite/member checks: Gate A prerequisites, PRQ-009 order, "
    "schema reissue, module manifest, first-slice scope, the PRQ-002A identity probe, "
    "the PRQ-002C raw-number prerequisite, the PRQ-002D prehash registry replay, "
    "the PRQ-002E profile-0.3 construction, and human-decision-assurance successor "
    "recomputation. `Foundation` separately "
    "runs the complete integrated "
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
    "68dd19753287f9e31354726b5e75ae597f68bcb1b1b32073a1285f2ce8fbb530"
)
EXPECTED_INTEGRATED_VALIDATOR_SHA256 = (
    "4d3fd376bc7e6f062efe9f7904d4902c790b8ec4500c98f54151a731077b7393"
)
FOUNDATION_TIMEOUT_MAP_ERROR = (
    "Foundation timeout policy must retain the exact 30-second default and "
    "path-specific 90/60-second overrides"
)
FOUNDATION_TIMEOUT_CONSUMER_ERROR = (
    "Foundation timeout consumers must use the exact path-specific bounded policy"
)
FOUNDATION_TIMEOUT_NESTED_ERROR = (
    "PRQ-002B nested successor timeout must remain exactly 60 seconds"
)
FOUNDATION_TIMEOUT_BINDING_ERROR = (
    "Foundation timeout policy bindings must remain immutable and have only "
    "their exact executable references"
)
FOUNDATION_TIMEOUT_NESTED_BINDING_ERROR = (
    "PRQ-002B nested successor timeout binding must remain immutable and have "
    "only its exact executable reference"
)
EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS = {
    "widen-default-foundation-timeout": (
        "scripts/validate.py",
        "DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS = 30\n",
        "DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS = 60\n",
        FOUNDATION_TIMEOUT_MAP_ERROR,
    ),
    "rebind-foundation-timeout-maps": (
        "scripts/validate.py",
        "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS = {\n"
        '    "tests/product-identity-profile-0.3-candidate/check.py": 60,\n'
        "}\n"
        "MARKDOWN_LINK =",
        "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS = {\n"
        '    "tests/product-identity-profile-0.3-candidate/check.py": 60,\n'
        "}\n"
        "ISOLATED_CONTRACT_SUITE_TIMEOUT_SECONDS[\n"
        '    "tests/product-identity-profile-candidate/check.py"\n'
        "] = 60\n"
        "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS[\n"
        '    "tests/product-identity-profile-0.3-candidate/check.py"\n'
        "] = 30\n"
        "MARKDOWN_LINK =",
        FOUNDATION_TIMEOUT_BINDING_ERROR,
    ),
    "bypass-prq-002e-timeout-policy": (
        "scripts/validate.py",
        "                timeout=ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS.get(\n"
        "                    relative, DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS\n"
        "                ),\n",
        "                timeout=30,\n",
        FOUNDATION_TIMEOUT_CONSUMER_ERROR,
    ),
    "rebind-nested-prq-002e-timeout": (
        "tests/product-identity-profile-candidate/check.py",
        "POST_PRQ_002B_CHECK_TIMEOUT_SECONDS = 60\n"
        "ALLOWED_SUITE_JSON_PATHS =",
        "POST_PRQ_002B_CHECK_TIMEOUT_SECONDS = 60\n"
        'globals()["POST_PRQ_002B_CHECK_TIMEOUT_SECONDS"] = 30\n'
        "ALLOWED_SUITE_JSON_PATHS =",
        FOUNDATION_TIMEOUT_NESTED_BINDING_ERROR,
    ),
    "decorate-foundation-timeout-consumer": (
        "scripts/validate.py",
        "def validate_isolated_contract_suites(errors: list[str]) -> int:\n",
        "@(lambda _original: (lambda errors: 17))\n"
        "def validate_isolated_contract_suites(errors: list[str]) -> int:\n",
        FOUNDATION_TIMEOUT_CONSUMER_ERROR,
    ),
    "rebind-predecessor-main-under-control-flow": (
        "tests/product-identity-profile-candidate/check.py",
        '\n\nif __name__ == "__main__":\n'
        "    raise SystemExit(main())\n",
        "\n\nif True:\n"
        "    def main() -> int:\n"
        "        return 0\n"
        '\n\nif __name__ == "__main__":\n'
        "    raise SystemExit(main())\n",
        FOUNDATION_TIMEOUT_NESTED_ERROR,
    ),
}
FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT = len(
    EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS
)
FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY = (
    f"{CARDINAL_WORDS[FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT].capitalize()} "
    "Foundation timeout-policy mutations"
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
ARCHITECTURE_EVIDENCE_RUN_COUNT_BOUNDARY = (
    "The release checker compares the dedicated "
    f"{CARDINAL_WORDS[len(DEDICATED_ARCHITECTURE_EVIDENCE_COMMANDS)]}-command "
    "run body and the\nintegrated "
    f"{CARDINAL_WORDS[len(INTEGRATED_ARCHITECTURE_EVIDENCE_CHECKS)]}-member "
    "Python tuple"
)
RELEASE_CONTRACT_KNOWN_BAD_MUTATION_COUNT = 10
RELEASE_SCRIPT_KNOWN_BAD_MUTATION_COUNT = 11
RELEASE_SCRIPT_MUTATION_COUNT_BOUNDARY = (
    f"{CARDINAL_WORDS[RELEASE_SCRIPT_KNOWN_BAD_MUTATION_COUNT].capitalize()} "
    "separately retained release-script isolation mutations"
)
REPOSITORY_RELEASE_FIXTURE_COUNT_BOUNDARIES = (
    f"{CARDINAL_WORDS[ARCHITECTURE_EVIDENCE_KNOWN_BAD_MUTATION_COUNT].capitalize()} "
    "architecture-evidence inventory mutations",
    FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY,
    f"{CARDINAL_WORDS[RELEASE_CONTRACT_KNOWN_BAD_MUTATION_COUNT].capitalize()} "
    "release-contract mutations",
    f"{CARDINAL_WORDS[RELEASE_SCRIPT_KNOWN_BAD_MUTATION_COUNT].capitalize()} "
    "release-script isolation mutations",
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
    FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY,
    "github-governance-mutations-C1.json",
    "github-activation-C2.json",
    "github_repository_activation_receipt",
    "applied_outcome_unknown",
    "update_allows_fetch_and_merge=false",
    "does not authorize runtime",
    ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY,
    ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
    ARCHITECTURE_EVIDENCE_RUN_COUNT_BOUNDARY,
    RELEASE_SCRIPT_MUTATION_COUNT_BOUNDARY,
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
    "missing-prq-evaluator-no-compile",
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
EXPECTED_PRQ_NO_COMPILE_MUTATION = (
    "              --no-compile \\\n",
    "",
    "architecture evidence executable job bytes must be exact",
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
        "      - name: Run an eleventh dedicated architecture check\n"
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
REHEARSAL_PYTHON_SELECTOR_BLOCK = (
    'PRQ002_PYTHON_BIN="$(\n'
    '  "$CLONE/.venv-architecture/bin/python" -I -S -B \\\n'
    "    -c 'import sys; print(sys.executable)'\n"
    ')"\n'
    "readonly PRQ002_PYTHON_BIN\n"
)
REHEARSAL_PRQ002C_RECOMPUTATION_BLOCK = (
    '\nCURRENT_STAGE="prq-002c-raw-number-typing"\n'
    ".venv-architecture/bin/python \\\n"
    "  scripts/validate_product_identity_raw_number_typing.py \\\n"
    "  --recompute-all \\\n"
    '  --python-executable "$PRQ002_PYTHON_BIN" \\\n'
    '  --node-executable "$PRQ002_NODE_BIN" \\\n'
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
)
REHEARSAL_PRQ002D_RECOMPUTATION_BLOCK = (
    '\nCURRENT_STAGE="prq-002d-schema-registry-prehash-replay"\n'
    '"$PRQ002_NODE_BIN" "$PRQ002_NPM_CLI" ci \\\n'
    "  --ignore-scripts \\\n"
    "  --no-audit \\\n"
    "  --no-fund \\\n"
    "  --prefix tests/schema-registry-prehash-replay/node \\\n"
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    ".venv-architecture/bin/python \\\n"
    "  scripts/validate_schema_registry_prehash_replay.py \\\n"
    "  --recompute-all \\\n"
    '  --python-executable "$PRQ002_PYTHON_BIN" \\\n'
    '  --node-executable "$PRQ002_NODE_BIN" \\\n'
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    'rm -rf -- "$CLONE/tests/schema-registry-prehash-replay/node/node_modules"\n'
)
REHEARSAL_PRQ002_RECOMPUTATION_BLOCK = (
    'CURRENT_STAGE="prq-002-identity-probe"\n'
    ".venv-architecture/bin/python -m pip install \\\n"
    "  --disable-pip-version-check \\\n"
    "  --no-input \\\n"
    "  --require-hashes \\\n"
    "  --only-binary=:all: \\\n"
    "  --no-compile \\\n"
    "  --requirement tests/prq-002-identity-cohort/python/requirements.lock \\\n"
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    ".venv-architecture/bin/python -m pip check \\\n"
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    + REHEARSAL_PYTHON_SELECTOR_BLOCK
    + 'PRQ002_NODE_BIN="$(bash scripts/ci/install-node.sh)"\n'
    "readonly PRQ002_NODE_BIN\n"
    'PRQ002_NODE_ROOT="${PRQ002_NODE_BIN%/bin/node}"\n'
    "readonly PRQ002_NODE_ROOT\n"
    'PRQ002_NPM_CLI="$PRQ002_NODE_ROOT/lib/node_modules/npm/bin/npm-cli.js"\n'
    "readonly PRQ002_NPM_CLI\n"
    '"$PRQ002_NODE_BIN" "$PRQ002_NPM_CLI" ci \\\n'
    "  --ignore-scripts \\\n"
    "  --no-audit \\\n"
    "  --no-fund \\\n"
    "  --prefix tests/prq-002-identity-cohort/node \\\n"
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    ".venv-architecture/bin/python \\\n"
    "  tests/prq-002-identity-cohort/check.py \\\n"
    "  --recompute-all \\\n"
    '  --python-executable "$PRQ002_PYTHON_BIN" \\\n'
    '  --node-executable "$PRQ002_NODE_BIN" \\\n'
    "  2>&1 | tee -a artifacts/rehearsal/foundation.log\n"
    'rm -rf -- "$CLONE/tests/prq-002-identity-cohort/node/node_modules"\n'
    + REHEARSAL_PRQ002C_RECOMPUTATION_BLOCK
    + REHEARSAL_PRQ002D_RECOMPUTATION_BLOCK
    + "record_stage foundation passed\n"
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
    "missing-rehearsal-prq-002-recomputation": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_PRQ002_RECOMPUTATION_BLOCK,
        'CURRENT_STAGE="prq-002-identity-probe"\n'
        "# PRQ-002 recomputation removed by known-bad fixture\n"
        "record_stage foundation passed\n",
        "fresh-clone rehearsal must retain the exact PRQ-002 recomputation block",
    ),
    "literal-rehearsal-python-selector": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_PYTHON_SELECTOR_BLOCK,
        'PRQ002_PYTHON_BIN="$CLONE/.venv-architecture/bin/python"\n'
        "readonly PRQ002_PYTHON_BIN\n",
        "fresh-clone rehearsal must retain the exact PRQ-002 recomputation block",
    ),
    "missing-rehearsal-prq-002c-recomputation": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_PRQ002C_RECOMPUTATION_BLOCK,
        '\nCURRENT_STAGE="prq-002c-raw-number-typing"\n'
        "# PRQ-002C recomputation removed by known-bad fixture\n",
        "fresh-clone rehearsal must retain the exact PRQ-002C recomputation block",
    ),
    "missing-rehearsal-prq-002d-recomputation": (
        "scripts/ci/rehearse-fresh-clone.sh",
        REHEARSAL_PRQ002D_RECOMPUTATION_BLOCK,
        '\nCURRENT_STAGE="prq-002d-schema-registry-prehash-replay"\n'
        "# PRQ-002D recomputation removed by known-bad fixture\n",
        "fresh-clone rehearsal must retain the exact PRQ-002D recomputation block",
    ),
    "shared-standalone-tool-cache": (
        "scripts/ci/check-repository-release.sh",
        STANDALONE_TOOL_CACHE_BLOCK,
        'ODEYA_TOOL_CACHE="${TMPDIR:-/tmp}/odeya-release-tools"\n'
        "readonly ODEYA_TOOL_CACHE\n"
        "export ODEYA_TOOL_CACHE\n",
        "standalone release check must allocate a unique tool cache",
    ),
    "weaken-mermaid-render-count": (
        "scripts/ci/render-readme-architecture.sh",
        'readonly EXPECTED_DIAGRAM_COUNT="7"',
        'readonly EXPECTED_DIAGRAM_COUNT="1"',
        "Mermaid renderer exact-byte contract drifted",
    ),
    "skip-non-readme-mermaid-renders": (
        "scripts/ci/render-readme-architecture.sh",
        "  rendered_count=$((rendered_count + 1))\n"
        "  printf 'Rendered governed Mermaid map: %s\\n' \"$base\"\n"
        "done",
        "  rendered_count=$((rendered_count + 1))\n"
        "  printf 'Rendered governed Mermaid map: %s\\n' \"$base\"\n"
        "  break\n"
        "done",
        "Mermaid renderer exact-byte contract drifted",
    ),
    "remove-mermaid-image-signature-assertion": (
        "scripts/ci/render-readme-architecture.sh",
        '  assert_image "$rendered"\n',
        '  test -s "$rendered"\n',
        "Mermaid renderer exact-byte contract drifted",
    ),
    "renderer-crlf-byte-substitution": (
        "scripts/ci/render-readme-architecture.sh",
        "#!/usr/bin/env bash\n",
        "#!/usr/bin/env bash\r\n",
        "Mermaid renderer exact-byte contract drifted",
    ),
}
EXPECTED_RELEASE_CONTRACT_MUTATIONS = {
    "stale-architecture-evidence-counts": (
        ARCHITECTURE_EVIDENCE_COUNT_BOUNDARY,
        "Reproduce five dedicated prerequisite/member checks: Gate A prerequisites, "
        "PRQ-009 order, schema reissue, module manifest, first-slice scope, and "
        "human-decision-assurance successor recomputation. `Foundation` separately "
        "runs the complete integrated ten-check census",
        "Reproduce ten dedicated prerequisite/member checks",
    ),
    "stale-architecture-evidence-mutation-count": (
        ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
        "The exact inventory contains seventeen retained known-bad mutations",
        ARCHITECTURE_EVIDENCE_MUTATION_COUNT_BOUNDARY,
    ),
    "stale-architecture-evidence-run-counts": (
        ARCHITECTURE_EVIDENCE_RUN_COUNT_BOUNDARY,
        "The release checker compares the dedicated eight-command run body and "
        "the\nintegrated fourteen-member Python tuple",
        "The release checker compares the dedicated ten-command run body",
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
    "stale-foundation-timeout-policy-mutation-count": (
        FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY,
        "Seven Foundation timeout-policy mutations",
        FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY,
    ),
    "stale-release-script-mutation-count": (
        RELEASE_SCRIPT_MUTATION_COUNT_BOUNDARY,
        "Seven separately retained release-script isolation mutations",
        RELEASE_SCRIPT_MUTATION_COUNT_BOUNDARY,
    ),
}
EXPECTED_RELEASE_CENSUS_MUTATIONS = {
    "coherent-release-script-growth-with-stale-prose": (
        "release_script_mutations",
        "synthetic-twelfth-release-script-mutation",
        "release-script expected and fixture censuses must each contain exactly 11 members",
    ),
    "coherent-release-contract-growth-with-stale-prose": (
        "release_contract_mutations",
        "synthetic-eleventh-release-contract-mutation",
        "release-contract expected and fixture censuses must each contain exactly 10 members",
    ),
    "coherent-foundation-timeout-growth-with-stale-prose": (
        "foundation_timeout_policy_mutations",
        "synthetic-seventh-foundation-timeout-policy-mutation",
        "foundation-timeout-policy expected and fixture censuses must each "
        "contain exactly 6 members",
    ),
}
EXPECTED_RELEASE_FIXTURE_README_MUTATIONS = {
    "stale-architecture-evidence-fixture-readme-count": (
        "Twenty-seven architecture-evidence inventory mutations",
        "Twenty-five architecture-evidence inventory mutations",
        "repository-release fixture README must carry exactly the "
        "executable-derived boundary 'Twenty-seven architecture-evidence "
        "inventory mutations'",
    ),
    "stale-release-contract-fixture-readme-count": (
        "Ten release-contract mutations",
        "Nine release-contract mutations",
        "repository-release fixture README must carry exactly the "
        "executable-derived boundary 'Ten release-contract mutations'",
    ),
    "stale-release-script-fixture-readme-count": (
        "Eleven release-script isolation mutations",
        "Seven release-script isolation mutations",
        "repository-release fixture README must carry exactly the "
        "executable-derived boundary 'Eleven release-script isolation mutations'",
    ),
    "stale-foundation-timeout-fixture-readme-count": (
        FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY,
        "Seven Foundation timeout-policy mutations",
        "repository-release fixture README must carry exactly the "
        "executable-derived boundary 'Six Foundation timeout-policy mutations'",
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
        return (ROOT / relative).read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{relative}: unreadable: {exc}")
        return ""


def is_markdown_path(relative: str) -> bool:
    return PurePosixPath(relative).suffix.casefold() == ".md"


def tracked_markdown_documents(
    errors: list[str],
    command: tuple[str, ...] = TRACKED_PATH_CENSUS_COMMAND,
) -> dict[str, str]:
    if command != TRACKED_PATH_CENSUS_COMMAND:
        errors.append(
            "tracked Markdown census command must list all tracked paths before "
            "case-insensitive extension filtering"
        )
        return {}
    environment = dict(os.environ)
    dynamic_prefixes = (
        "GIT_CONFIG_KEY_",
        "GIT_CONFIG_VALUE_",
        "GIT_TRACE",
        "GIT_TRACE2",
    )
    for name in tuple(environment):
        if name in GIT_ENVIRONMENT_TO_REMOVE or name.startswith(dynamic_prefixes):
            environment.pop(name)
    environment.update(GIT_ENVIRONMENT_TO_FIX)
    try:
        result = subprocess.run(
            list(command),
            cwd=ROOT,
            env=environment,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        errors.append(f"tracked Markdown census could not run: {exc}")
        return {}
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        errors.append(
            "tracked Markdown census failed: "
            + (detail or f"git exited {result.returncode}")
        )
        return {}
    try:
        encoded_paths = result.stdout.split(b"\0")
        if encoded_paths and encoded_paths[-1] == b"":
            encoded_paths.pop()
        paths = [
            item.decode("utf-8")
            for item in encoded_paths
            if is_markdown_path(item.decode("utf-8"))
        ]
    except UnicodeDecodeError as exc:
        errors.append(f"tracked Markdown census contains a non-UTF-8 path: {exc}")
        return {}
    documents: dict[str, str] = {}
    for relative in paths:
        path = Path(relative)
        if (
            path.is_absolute()
            or ".." in path.parts
            or path.as_posix() != relative
            or relative in documents
        ):
            errors.append(
                f"tracked Markdown census contains an unsafe or duplicate path: {relative!r}"
            )
            continue
        documents[relative] = read(relative, errors)
    if not documents:
        errors.append("tracked Markdown census is empty")
    return documents


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


def extract_mermaid_blocks(
    document: str,
    relative: str,
    expected_count: int,
    errors: list[str],
) -> tuple[str, ...]:
    candidates: list[tuple[str, bool]] = []
    lines = document.splitlines()
    cursor = 0
    while cursor < len(lines):
        opening = FENCED_CODE_OPEN.fullmatch(lines[cursor])
        if opening is None:
            cursor += 1
            continue

        fence = opening.group("fence")
        marker = fence[0]
        info = opening.group("info").strip()
        # A backtick fence whose info string contains a backtick is not a
        # CommonMark fenced-code opener.
        if marker == "`" and "`" in info:
            cursor += 1
            continue

        opening_indent = len(opening.group("indent"))
        closing = re.compile(
            rf"^ {{0,3}}{re.escape(marker)}{{{len(fence)},}}[ \t]*$"
        )
        body: list[str] = []
        closed = False
        cursor += 1
        while cursor < len(lines):
            line = lines[cursor]
            if closing.fullmatch(line):
                closed = True
                cursor += 1
                break
            removable = min(opening_indent, len(line) - len(line.lstrip(" ")))
            body.append(line[removable:])
            cursor += 1

        info_token = info.split(maxsplit=1)[0].casefold() if info else ""
        if info_token == "mermaid":
            candidates.append(("\n".join(body), closed))

    marker_count = sum(
        len(MERMAID_FENCE_MARKER.findall(line))
        for line in lines
    )
    if marker_count != len(candidates):
        errors.append(
            f"{relative}: found {marker_count} Mermaid fence marker(s) but parsed "
            f"{len(candidates)} top-level Mermaid block(s); container, nested, "
            "attribute-only, and indented-code Mermaid fences are forbidden"
        )
    if len(candidates) != expected_count:
        errors.append(
            f"{relative}: expected exactly {expected_count} Mermaid block(s), "
            f"found {len(candidates)}"
        )
        return ()
    diagrams: list[str] = []
    for index, (block, closed) in enumerate(candidates, start=1):
        if not closed:
            errors.append(f"{relative}: Mermaid block {index} is unclosed")
            continue
        diagram = block.strip()
        if not diagram:
            errors.append(f"{relative}: Mermaid block {index} is empty")
            continue
        for label, pattern in MERMAID_UNSAFE_PATTERNS:
            if pattern.search(diagram):
                errors.append(
                    f"{relative}: Mermaid block {index} contains forbidden "
                    f"{label}"
                )
                break
        diagrams.append(diagram + "\n")
    return tuple(diagrams)


def extract_mermaid(readme: str, errors: list[str]) -> str:
    blocks = extract_mermaid_blocks(readme, "README.md", 1, errors)
    if len(blocks) != 1:
        return ""
    diagram = blocks[0]
    required = (
        "1 · CONTRACT",
        "PRIVATE RESEARCH ENGINE",
        "RELEASE PATH · adjudicated candidate only",
        "Separately assigned verification role",
        "Human release decision",
        "Exact single-use grant",
        "Separately authorized observation + reconciliation role",
        "Grounded memory",
        "CANONICAL SCIENTIFIC STATE",
        "append-only event + evidence ledger",
    )
    for phrase in required:
        if phrase not in diagram:
            errors.append(f"README.md: Mermaid system map is missing {phrase!r}")
    if "R ~~~ X" not in diagram or re.search(r"\bD\s+[-.=~]+.*(?:RC|X)", diagram):
        errors.append(
            "README.md: scientific and release clusters need one invisible layout edge and no misleading cross-cluster claim edge"
        )
    return diagram


def validate_architecture_mermaids(
    errors: list[str],
) -> dict[str, tuple[str, ...]]:
    documents = tracked_markdown_documents(errors)
    missing = set(MERMAID_DOCUMENTS) - set(documents)
    if missing:
        errors.append(
            "governed Mermaid document census is not tracked and complete: "
            f"missing {sorted(missing)}"
        )
    diagrams: dict[str, tuple[str, ...]] = {}
    for relative, document in sorted(documents.items()):
        expected_count = MERMAID_DOCUMENTS.get(relative, 0)
        blocks = extract_mermaid_blocks(
            document,
            relative,
            expected_count,
            errors,
        )
        if relative != "README.md" and expected_count:
            diagrams[relative] = blocks
    return diagrams


def mermaid_inventory_self_tests(errors: list[str]) -> int:
    safe = "```mermaid\nflowchart LR\n    A --> B\n```"
    safe_controls = (
        ("backtick", safe, 1, ("flowchart LR\n    A --> B\n",)),
        (
            "tilde-spaced-info",
            "~~~ mermaid\nflowchart LR\n    A --> B\n~~~",
            1,
            ("flowchart LR\n    A --> B\n",),
        ),
        (
            "long-indented-casefolded",
            "   ````Mermaid rendered-map\n"
            "   flowchart LR\n"
            "       A --> B\n"
            "   ````",
            1,
            ("flowchart LR\n    A --> B\n",),
        ),
        (
            "non-mermaid",
            "```text\nnot a rendered diagram\n```",
            0,
            (),
        ),
    )
    for control_id, source, expected_count, expected_blocks in safe_controls:
        safe_errors: list[str] = []
        safe_blocks = extract_mermaid_blocks(
            source,
            f"safe-{control_id}.md",
            expected_count,
            safe_errors,
        )
        if safe_errors or safe_blocks != expected_blocks:
            errors.append(
                f"Mermaid inventory safe control {control_id} failed: "
                + " | ".join(safe_errors or [repr(safe_blocks)])
            )

    cases = (
        (
            "missing",
            "",
            1,
            "known-bad.md: expected exactly 1 Mermaid block(s), found 0",
        ),
        (
            "extra",
            safe + "\n" + safe,
            1,
            "known-bad.md: expected exactly 1 Mermaid block(s), found 2",
        ),
        (
            "empty",
            "```mermaid\n\n```",
            1,
            "known-bad.md: Mermaid block 1 is empty",
        ),
        (
            "unsafe",
            "```mermaid\nflowchart LR\n    click A href\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden click directive",
        ),
        (
            "unsafe-tab",
            "```mermaid\nflowchart LR\n    click\tA href\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden click directive",
        ),
        (
            "unsafe-configuration",
            "```mermaid\n%%{init: {'theme': 'dark'}}%%\nflowchart LR\nA --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden configuration directive",
        ),
        (
            "unsafe-yaml-frontmatter",
            "```mermaid\n---\ntitle: Hi\nconfig:\n  theme: dark\n---\n"
            "flowchart LR\nA --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden YAML frontmatter",
        ),
        (
            "unsafe-javascript-uri",
            "```mermaid\nflowchart LR\nA[\"javascript:alert\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden javascript URI",
        ),
        (
            "unsafe-image-asset",
            "```mermaid\nflowchart LR\n"
            "A@{ img: \"asset.png\", label: \"x\" } --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden image asset property",
        ),
        (
            "unsafe-attribute-object",
            "```mermaid\nflowchart LR\nA@{ shape: rect } --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden attribute object",
        ),
        (
            "unsafe-quoted-image-protocol-relative",
            "```mermaid\nflowchart LR\n"
            "A@{ \"img\": \"//example.invalid/x.png\", label: \"x\" } --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden image asset property",
        ),
        (
            "unsafe-protocol-relative-uri",
            "```mermaid\nflowchart LR\nA[\"//example.invalid/x\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden "
            "protocol-relative resource location",
        ),
        (
            "unsafe-http-uri",
            "```mermaid\nflowchart LR\nA[\"https://example.invalid/x\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden resource URI scheme",
        ),
        (
            "unsafe-file-uri",
            "```mermaid\nflowchart LR\nA[\"file:///tmp/x\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden resource URI scheme",
        ),
        (
            "unsafe-data-uri",
            "```mermaid\nflowchart LR\nA[\"data:image/png;base64,AA\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden resource URI scheme",
        ),
        (
            "unsafe-html-image",
            "```mermaid\nflowchart LR\nA[\"<img src='asset.png'>\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden HTML image element",
        ),
        (
            "unsafe-css-resource",
            "```mermaid\nflowchart LR\nA --> B\n"
            "style A background-image:url(asset.png)\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden CSS resource URL",
        ),
        (
            "unsafe-markdown-image",
            "```mermaid\nflowchart LR\nA[\"![x](asset.png)\"] --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 contains forbidden Markdown image",
        ),
        (
            "unclosed",
            "```mermaid\nflowchart LR\n    A --> B",
            1,
            "known-bad.md: Mermaid block 1 is unclosed",
        ),
        (
            "tilde-extra",
            safe + "\n~~~mermaid\nflowchart LR\n    C --> D\n~~~",
            1,
            "known-bad.md: expected exactly 1 Mermaid block(s), found 2",
        ),
        (
            "spaced-info-extra",
            safe + "\n``` mermaid\nflowchart LR\n    C --> D\n```",
            1,
            "known-bad.md: expected exactly 1 Mermaid block(s), found 2",
        ),
        (
            "long-fence-extra",
            safe + "\n````Mermaid map\nflowchart LR\n    C --> D\n````",
            1,
            "known-bad.md: expected exactly 1 Mermaid block(s), found 2",
        ),
        (
            "shorter-close",
            "````mermaid\nflowchart LR\n    A --> B\n```",
            1,
            "known-bad.md: Mermaid block 1 is unclosed",
        ),
        (
            "ungoverned-document",
            safe,
            0,
            "known-bad.md: expected exactly 0 Mermaid block(s), found 1",
        ),
        (
            "blockquote-container",
            "> ```mermaid\n> flowchart LR\n> A --> B\n> ```",
            0,
            "known-bad.md: found 1 Mermaid fence marker(s) but parsed 0 "
            "top-level Mermaid block(s); container, nested, attribute-only, "
            "and indented-code Mermaid fences are forbidden",
        ),
        (
            "list-container",
            "- ```mermaid\n  flowchart LR\n  A --> B\n  ```",
            0,
            "known-bad.md: found 1 Mermaid fence marker(s) but parsed 0 "
            "top-level Mermaid block(s); container, nested, attribute-only, "
            "and indented-code Mermaid fences are forbidden",
        ),
        (
            "list-indented-container",
            "- diagram\n    ```mermaid\n    flowchart LR\n    A --> B\n    ```",
            0,
            "known-bad.md: found 1 Mermaid fence marker(s) but parsed 0 "
            "top-level Mermaid block(s); container, nested, attribute-only, "
            "and indented-code Mermaid fences are forbidden",
        ),
        (
            "nested-decoy",
            "````text\n```mermaid\nflowchart LR\nA --> B\n```\n````",
            0,
            "known-bad.md: found 1 Mermaid fence marker(s) but parsed 0 "
            "top-level Mermaid block(s); container, nested, attribute-only, "
            "and indented-code Mermaid fences are forbidden",
        ),
        (
            "attribute-only-info",
            "```{.mermaid}\nflowchart LR\nA --> B\n```",
            0,
            "known-bad.md: found 1 Mermaid fence marker(s) but parsed 0 "
            "top-level Mermaid block(s); container, nested, attribute-only, "
            "and indented-code Mermaid fences are forbidden",
        ),
    )
    passed = 0
    for case_id, source, expected_count, expected in cases:
        observed: list[str] = []
        extract_mermaid_blocks(
            source,
            "known-bad.md",
            expected_count,
            observed,
        )
        if observed == [expected]:
            passed += 1
        else:
            errors.append(
                f"Mermaid inventory known-bad {case_id} expected "
                f"{expected!r}; got {observed!r}"
            )
    uppercase_expected = (
        "known-bad.MD: expected exactly 0 Mermaid block(s), found 1"
    )
    uppercase_observed: list[str] = []
    if is_markdown_path("known-bad.MD"):
        extract_mermaid_blocks(
            safe,
            "known-bad.MD",
            0,
            uppercase_observed,
        )
    if uppercase_observed == [uppercase_expected]:
        passed += 1
    else:
        errors.append(
            "Mermaid inventory known-bad uppercase-extension expected "
            f"{uppercase_expected!r}; got {uppercase_observed!r}"
        )
    discovery_expected = (
        "tracked Markdown census command must list all tracked paths before "
        "case-insensitive extension filtering"
    )
    discovery_observed: list[str] = []
    tracked_markdown_documents(
        discovery_observed,
        ("git", "ls-files", "-z", "--", "*.md"),
    )
    if discovery_observed == [discovery_expected]:
        passed += 1
    else:
        errors.append(
            "Mermaid inventory known-bad lowercase-only-discovery expected "
            f"{discovery_expected!r}; got {discovery_observed!r}"
        )
    return passed


def mermaid_filename(relative: str, index: int) -> str:
    stem = relative.removesuffix(".md").replace("/", "__")
    return f"{stem}-{index:02d}.mmd"


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


def literal_assignment_value(tree: ast.Module, name: str) -> Any | None:
    assignments = [
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == name
    ]
    if len(assignments) != 1:
        return None
    try:
        return ast.literal_eval(assignments[0].value)
    except (TypeError, ValueError, SyntaxError):
        return None


TIMEOUT_DYNAMIC_NAMESPACE_NAMES = frozenset(
    {
        "__import__",
        "compile",
        "delattr",
        "eval",
        "exec",
        "globals",
        "locals",
        "setattr",
        "vars",
    }
)
TIMEOUT_DYNAMIC_NAMESPACE_ATTRIBUTES = TIMEOUT_DYNAMIC_NAMESPACE_NAMES - {
    "compile"
}


def timeout_bindings_are_immutable(
    tree: ast.Module,
    expected_loads: dict[str, int],
) -> bool:
    """Refuse executable rebinding beyond each exact literal declaration.

    Missing consumer loads are classified by the exact consumer-expression
    checks below. Extra loads are unsafe because they enable aliases,
    subscript writes, and mutator calls after the literal declaration.
    Exact whole-file digests remain the boundary against arbitrarily
    obfuscated Python; this is a deliberately bounded static policy.
    """

    governed = frozenset(expected_loads)
    for name, expected_load_count in expected_loads.items():
        references = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and node.id == name
        ]
        stores = sum(isinstance(node.ctx, ast.Store) for node in references)
        loads = sum(isinstance(node.ctx, ast.Load) for node in references)
        deletes = sum(isinstance(node.ctx, ast.Del) for node in references)
        if stores != 1 or loads > expected_load_count or deletes != 0:
            return False

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value == "__dict__" or any(
                name in node.value for name in governed
            ):
                return False
        if isinstance(node, ast.Attribute) and (
            node.attr in governed
            or node.attr == "__dict__"
            or node.attr in TIMEOUT_DYNAMIC_NAMESPACE_ATTRIBUTES
        ):
            return False
        if isinstance(node, ast.Name) and node.id in TIMEOUT_DYNAMIC_NAMESPACE_NAMES:
            return False
        if isinstance(node, ast.arg) and node.arg in governed:
            return False
        if isinstance(node, ast.alias):
            bound_name = node.asname or node.name.split(".", 1)[0]
            if bound_name in governed:
                return False
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        ) and node.name in governed:
            return False
        if isinstance(node, ast.ExceptHandler) and node.name in governed:
            return False
        if isinstance(node, (ast.Global, ast.Nonlocal)) and governed.intersection(
            node.names
        ):
            return False
        if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name in governed:
            return False
        if isinstance(node, ast.MatchMapping) and node.rest in governed:
            return False
    return True


def executable_function_binding_is_exact(
    tree: ast.Module,
    name: str,
) -> bool:
    definitions = [
        node
        for node in ast.walk(tree)
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
        and node.name == name
    ]
    references = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id == name
    ]
    if (
        len(definitions) != 1
        or not isinstance(definitions[0], ast.FunctionDef)
        or definitions[0] not in tree.body
        or definitions[0].decorator_list
        or sum(isinstance(node.ctx, ast.Load) for node in references) != 1
        or any(isinstance(node.ctx, (ast.Store, ast.Del)) for node in references)
    ):
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == name:
            return False
        if isinstance(node, ast.Attribute) and node.attr == name:
            return False
        if isinstance(node, ast.arg) and node.arg == name:
            return False
        if isinstance(node, ast.alias):
            bound_name = node.asname or node.name.split(".", 1)[0]
            if bound_name == name:
                return False
        if isinstance(node, ast.ExceptHandler) and node.name == name:
            return False
        if isinstance(node, (ast.Global, ast.Nonlocal)) and name in node.names:
            return False
        if isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name == name:
            return False
        if isinstance(node, ast.MatchMapping) and node.rest == name:
            return False
    return True


def timeout_keyword_matches(
    function: ast.FunctionDef,
    expected_expression: str,
) -> bool:
    calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
        and node.func.attr == "run"
    ]
    if len(calls) != 1:
        return False
    timeout_keywords = [
        keyword for keyword in calls[0].keywords if keyword.arg == "timeout"
    ]
    if len(timeout_keywords) != 1:
        return False
    expected = ast.parse(expected_expression, mode="eval").body
    return ast.dump(timeout_keywords[0].value) == ast.dump(expected)


def foundation_timeout_policy_errors(
    validator_text: str,
    predecessor_text: str,
) -> list[str]:
    """Bind the two measured heavy children without widening every check.

    This policy is evaluated independently from the whole-file SHA binding so
    its known-bads cannot receive incidental credit from generic byte drift.
    """

    try:
        validator_tree = ast.parse(validator_text)
    except SyntaxError:
        return [FOUNDATION_TIMEOUT_MAP_ERROR]
    try:
        predecessor_tree = ast.parse(predecessor_text)
    except SyntaxError:
        return [FOUNDATION_TIMEOUT_NESTED_ERROR]

    default_timeout = literal_assignment_value(
        validator_tree, "DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS"
    )
    suite_timeouts = literal_assignment_value(
        validator_tree, "ISOLATED_CONTRACT_SUITE_TIMEOUT_SECONDS"
    )
    evidence_timeouts = literal_assignment_value(
        validator_tree, "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS"
    )
    exact_maps = (
        type(default_timeout) is int
        and default_timeout == 30
        and suite_timeouts
        == {"tests/product-identity-profile-candidate/check.py": 90}
        and evidence_timeouts
        == {"tests/product-identity-profile-0.3-candidate/check.py": 60}
        and all(
            type(value) is int
            for mapping in (suite_timeouts, evidence_timeouts)
            if isinstance(mapping, dict)
            for value in mapping.values()
        )
    )
    errors: list[str] = []
    if not exact_maps:
        errors.append(FOUNDATION_TIMEOUT_MAP_ERROR)
    validator_bindings_are_exact = timeout_bindings_are_immutable(
        validator_tree,
        {
            "DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS": 2,
            "ISOLATED_CONTRACT_SUITE_TIMEOUT_SECONDS": 1,
            "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS": 1,
        },
    )
    if not validator_bindings_are_exact:
        errors.append(FOUNDATION_TIMEOUT_BINDING_ERROR)

    isolated_functions = [
        node
        for node in validator_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "validate_isolated_contract_suites"
    ]
    evidence_functions = [
        node
        for node in validator_tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "validate_architecture_evidence_checks"
    ]
    consumers_are_exact = (
        len(isolated_functions) == 1
        and len(evidence_functions) == 1
        and executable_function_binding_is_exact(
            validator_tree, "validate_isolated_contract_suites"
        )
        and executable_function_binding_is_exact(
            validator_tree, "validate_architecture_evidence_checks"
        )
        and timeout_keyword_matches(
            isolated_functions[0],
            "ISOLATED_CONTRACT_SUITE_TIMEOUT_SECONDS.get("
            "relative, DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS)",
        )
        and timeout_keyword_matches(
            evidence_functions[0],
            "ARCHITECTURE_EVIDENCE_CHECK_TIMEOUT_SECONDS.get("
            "relative, DEFAULT_FOUNDATION_CHILD_TIMEOUT_SECONDS)",
        )
    )
    if not consumers_are_exact:
        errors.append(FOUNDATION_TIMEOUT_CONSUMER_ERROR)

    nested_timeout = literal_assignment_value(
        predecessor_tree, "POST_PRQ_002B_CHECK_TIMEOUT_SECONDS"
    )
    predecessor_main = [
        node
        for node in predecessor_tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    nested_is_exact = (
        type(nested_timeout) is int
        and nested_timeout == 60
        and len(predecessor_main) == 1
        and executable_function_binding_is_exact(predecessor_tree, "main")
        and timeout_keyword_matches(
            predecessor_main[0], "POST_PRQ_002B_CHECK_TIMEOUT_SECONDS"
        )
    )
    if not nested_is_exact:
        errors.append(FOUNDATION_TIMEOUT_NESTED_ERROR)
    nested_binding_is_exact = timeout_bindings_are_immutable(
        predecessor_tree,
        {"POST_PRQ_002B_CHECK_TIMEOUT_SECONDS": 1},
    )
    if not nested_binding_is_exact:
        errors.append(FOUNDATION_TIMEOUT_NESTED_BINDING_ERROR)

    if exact_maps and nested_is_exact and suite_timeouts is not None:
        parent_timeout = suite_timeouts[
            "tests/product-identity-profile-candidate/check.py"
        ]
        if parent_timeout <= nested_timeout:
            errors.append(FOUNDATION_TIMEOUT_MAP_ERROR)
    return errors


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
                "              --report artifacts/ci/architecture-evidence-pip-install-report.json \\\n",
                "              --requirement tools/repository-release/requirements-architecture.lock\n",
                "              --no-compile \\\n",
                "              --requirement tests/prq-002-identity-cohort/python/requirements.lock\n",
                '            node_bin="$(bash scripts/ci/install-node.sh)"\n',
                "              --prefix tests/prq-002-identity-cohort/node\n",
                "              --prefix tests/schema-registry-prehash-replay/node\n",
                "            printf 'ODEYA_PRQ002_PYTHON=%s\\n' \"$python_bin\" >> \"$GITHUB_ENV\"\n",
                "            printf 'ODEYA_PRQ002_NODE=%s\\n' \"$node_bin\" >> \"$GITHUB_ENV\"\n",
                '            java_bin="$(bash scripts/ci/install-java.sh)"\n',
                "            python tests/prq-002-identity-cohort/check.py --recompute-all --python-executable \"$ODEYA_PRQ002_PYTHON\" --node-executable \"$ODEYA_PRQ002_NODE\"\n",
                "            python scripts/validate_product_identity_raw_number_typing.py --recompute-all --python-executable \"$ODEYA_PRQ002_PYTHON\" --node-executable \"$ODEYA_PRQ002_NODE\"\n",
                "            python scripts/validate_schema_registry_prehash_replay.py --recompute-all --python-executable \"$ODEYA_PRQ002_PYTHON\" --node-executable \"$ODEYA_PRQ002_NODE\"\n",
                "            python tests/product-identity-profile-0.3-candidate/authoring/generate_candidate.py --check && python tests/product-identity-profile-0.3-candidate/check.py\n",
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
            for fragment in (
                "              --require-hashes \\\n",
                "              --only-binary=:all: \\\n",
            ):
                if architecture_evidence.count(fragment) != 2:
                    issues.append(
                        "architecture evidence exact toolchain/recomputation contract "
                        f"must retain exactly two {fragment.strip()!r}"
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
        "foundation_timeout_policy_mutations",
        "release_contract",
        "release_contract_mutations",
        "release_census_mutations",
        "release_fixture_readme_mutations",
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
        if (
            case_id == "missing-prq-evaluator-no-compile"
            and (old, new, expected) != EXPECTED_PRQ_NO_COMPILE_MUTATION
        ):
            errors.append(
                "repository release mutation missing-prq-evaluator-no-compile: "
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


def validate_foundation_timeout_policy_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    mutations = cases.get("foundation_timeout_policy_mutations")
    if not isinstance(mutations, list):
        errors.append("Foundation timeout policy mutations: inventory is absent")
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
        or tuple(observed_ids)
        != tuple(EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS)
    ):
        errors.append(
            "Foundation timeout policy mutations: case census/order is not "
            "closed and exact"
        )

    documents = {
        "scripts/validate.py": read("scripts/validate.py", errors),
        "tests/product-identity-profile-candidate/check.py": read(
            "tests/product-identity-profile-candidate/check.py", errors
        ),
    }
    base_issues = foundation_timeout_policy_errors(
        documents["scripts/validate.py"],
        documents["tests/product-identity-profile-candidate/check.py"],
    )
    errors.extend(f"Foundation timeout policy: {issue}" for issue in base_issues)

    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append(
                "Foundation timeout policy mutations: case is not an object"
            )
            continue
        if set(case) != {"id", "subject", "old", "new", "expected"}:
            errors.append(
                "Foundation timeout policy mutations: case members are not "
                "closed and exact"
            )
            continue
        case_id = case.get("id")
        subject = case.get("subject")
        old = case.get("old")
        new = case.get("new")
        expected = case.get("expected")
        if (
            not all(
                isinstance(value, str) and value
                for value in (case_id, subject, old, expected)
            )
            or not isinstance(new, str)
        ):
            errors.append("Foundation timeout policy mutations: malformed case")
            continue
        expected_spec = EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS.get(case_id)
        if expected_spec != (subject, old, new, expected):
            errors.append(
                f"Foundation timeout policy mutation {case_id}: "
                "specification drifted from the executable policy"
            )
            continue
        base = documents.get(subject)
        if base is None:
            errors.append(
                f"Foundation timeout policy mutation {case_id}: "
                "subject is not admitted"
            )
            continue
        if base.count(old) != 1:
            errors.append(
                f"Foundation timeout policy mutation {case_id}: expected one "
                f"source occurrence, found {base.count(old)}"
            )
            continue
        mutated_documents = dict(documents)
        mutated_documents[subject] = base.replace(old, new, 1)
        mutation_issues = foundation_timeout_policy_errors(
            mutated_documents["scripts/validate.py"],
            mutated_documents["tests/product-identity-profile-candidate/check.py"],
        )
        if mutation_issues != [expected]:
            errors.append(
                f"Foundation timeout policy mutation {case_id}: expected sole "
                f"{expected!r} refusal, got {mutation_issues}"
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


def release_census_errors(
    foundation_timeout_expected_ids: list[str],
    foundation_timeout_fixture_ids: list[str],
    release_script_expected_ids: list[str],
    release_script_fixture_ids: list[str],
    release_contract_expected_ids: list[str],
    release_contract_fixture_ids: list[str],
    release_contract: str,
    fixture_readme: str,
) -> list[str]:
    errors: list[str] = []
    censuses = (
        (
            "foundation-timeout-policy",
            foundation_timeout_expected_ids,
            foundation_timeout_fixture_ids,
            FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT,
        ),
        (
            "release-script",
            release_script_expected_ids,
            release_script_fixture_ids,
            RELEASE_SCRIPT_KNOWN_BAD_MUTATION_COUNT,
        ),
        (
            "release-contract",
            release_contract_expected_ids,
            release_contract_fixture_ids,
            RELEASE_CONTRACT_KNOWN_BAD_MUTATION_COUNT,
        ),
    )
    for label, expected_ids, fixture_ids, expected_count in censuses:
        if len(expected_ids) != expected_count or len(fixture_ids) != expected_count:
            errors.append(
                f"{label} expected and fixture censuses must each contain exactly "
                f"{expected_count} members"
            )
        if (
            len(set(expected_ids)) != len(expected_ids)
            or len(set(fixture_ids)) != len(fixture_ids)
            or set(expected_ids) != set(fixture_ids)
        ):
            errors.append(
                f"{label} expected and fixture censuses must be closed, unique, and equal"
            )

    if release_contract.count(RELEASE_SCRIPT_MUTATION_COUNT_BOUNDARY) != 1:
        errors.append(
            "release contract must carry exactly one executable-derived "
            "release-script mutation count boundary"
        )

    cardinal_pattern = "|".join(
        re.escape(word.capitalize()) for word in CARDINAL_WORDS
    )
    timeout_suffix = FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY.split(
        " ", 1
    )[1]
    timeout_pattern = re.compile(
        rf"(?m)^(?:{cardinal_pattern}) {re.escape(timeout_suffix)}"
    )
    release_contract_timeout_boundaries = timeout_pattern.findall(
        release_contract
    )
    if release_contract_timeout_boundaries != [
        FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY
    ]:
        errors.append(
            "release contract must carry exactly the executable-derived "
            f"boundary {FOUNDATION_TIMEOUT_POLICY_MUTATION_COUNT_BOUNDARY!r}; "
            f"found {release_contract_timeout_boundaries}"
        )

    for boundary in REPOSITORY_RELEASE_FIXTURE_COUNT_BOUNDARIES:
        suffix = boundary.split(" ", 1)[1]
        pattern = re.compile(
            rf"(?m)^(?:{cardinal_pattern}) {re.escape(suffix)}"
        )
        observed = pattern.findall(fixture_readme)
        if observed != [boundary]:
            errors.append(
                "repository-release fixture README must carry exactly the "
                f"executable-derived boundary {boundary!r}; found {observed}"
            )
    return errors


def validate_release_census_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    script_mutations = cases.get("release_script_mutations")
    contract_mutations = cases.get("release_contract_mutations")
    timeout_mutations = cases.get("foundation_timeout_policy_mutations")
    census_mutations = cases.get("release_census_mutations")
    if not all(
        isinstance(value, list)
        for value in (
            script_mutations,
            contract_mutations,
            timeout_mutations,
            census_mutations,
        )
    ):
        errors.append("repository release census mutations: inventory is absent")
        return 0

    def observed_ids(mutations: list[Any]) -> list[str]:
        return [
            case["id"]
            for case in mutations
            if isinstance(case, dict) and isinstance(case.get("id"), str)
        ]

    script_expected_ids = list(EXPECTED_RELEASE_SCRIPT_MUTATIONS)
    script_fixture_ids = observed_ids(script_mutations)
    contract_expected_ids = list(EXPECTED_RELEASE_CONTRACT_MUTATIONS)
    contract_fixture_ids = observed_ids(contract_mutations)
    timeout_expected_ids = list(EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS)
    timeout_fixture_ids = observed_ids(timeout_mutations)
    release_contract = read("docs/REPOSITORY_RELEASE.md", errors)
    fixture_readme = read("tests/repository-release/README.md", errors)
    errors.extend(
        release_census_errors(
            timeout_expected_ids,
            timeout_fixture_ids,
            script_expected_ids,
            script_fixture_ids,
            contract_expected_ids,
            contract_fixture_ids,
            release_contract,
            fixture_readme,
        )
    )

    mutation_ids = observed_ids(census_mutations)
    if (
        len(mutation_ids) != len(census_mutations)
        or len(set(mutation_ids)) != len(mutation_ids)
        or set(mutation_ids) != set(EXPECTED_RELEASE_CENSUS_MUTATIONS)
    ):
        errors.append(
            "repository release census mutations: case census is not closed and exact"
        )

    passed = 0
    for case in census_mutations:
        if not isinstance(case, dict):
            errors.append("repository release census mutations: case is not an object")
            continue
        if set(case) != {"id", "target", "synthetic_id", "expected"}:
            errors.append(
                "repository release census mutations: case members are not closed and exact"
            )
            continue
        case_id = case.get("id")
        target = case.get("target")
        synthetic_id = case.get("synthetic_id")
        expected = case.get("expected")
        if not all(
            isinstance(value, str) and value
            for value in (case_id, target, synthetic_id, expected)
        ):
            errors.append("repository release census mutations: malformed case")
            continue
        if EXPECTED_RELEASE_CENSUS_MUTATIONS.get(case_id) != (
            target,
            synthetic_id,
            expected,
        ):
            errors.append(
                f"repository release census mutation {case_id}: "
                "specification drifted from the pinned matrix"
            )
            continue

        mutated_script_expected = list(script_expected_ids)
        mutated_script_fixture = list(script_fixture_ids)
        mutated_contract_expected = list(contract_expected_ids)
        mutated_contract_fixture = list(contract_fixture_ids)
        mutated_timeout_expected = list(timeout_expected_ids)
        mutated_timeout_fixture = list(timeout_fixture_ids)
        if target == "release_script_mutations":
            mutated_script_expected.append(synthetic_id)
            mutated_script_fixture.append(synthetic_id)
        elif target == "release_contract_mutations":
            mutated_contract_expected.append(synthetic_id)
            mutated_contract_fixture.append(synthetic_id)
        elif target == "foundation_timeout_policy_mutations":
            mutated_timeout_expected.append(synthetic_id)
            mutated_timeout_fixture.append(synthetic_id)
        else:
            errors.append(
                f"repository release census mutation {case_id}: target is not admitted"
            )
            continue

        mutation_issues = release_census_errors(
            mutated_timeout_expected,
            mutated_timeout_fixture,
            mutated_script_expected,
            mutated_script_fixture,
            mutated_contract_expected,
            mutated_contract_fixture,
            release_contract,
            fixture_readme,
        )
        if mutation_issues != [expected]:
            errors.append(
                f"repository release census mutation {case_id}: expected sole "
                f"{expected!r} refusal, got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


def validate_release_fixture_readme_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    mutations = cases.get("release_fixture_readme_mutations")
    script_mutations = cases.get("release_script_mutations")
    contract_mutations = cases.get("release_contract_mutations")
    timeout_mutations = cases.get("foundation_timeout_policy_mutations")
    if not all(
        isinstance(value, list)
        for value in (
            mutations,
            script_mutations,
            contract_mutations,
            timeout_mutations,
        )
    ):
        errors.append(
            "repository release fixture README mutations: inventory is absent"
        )
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
        or set(observed_ids) != set(EXPECTED_RELEASE_FIXTURE_README_MUTATIONS)
    ):
        errors.append(
            "repository release fixture README mutations: "
            "case census is not closed and exact"
        )

    def fixture_ids(items: list[Any]) -> list[str]:
        return [
            case["id"]
            for case in items
            if isinstance(case, dict) and isinstance(case.get("id"), str)
        ]

    script_expected_ids = list(EXPECTED_RELEASE_SCRIPT_MUTATIONS)
    script_fixture_ids = fixture_ids(script_mutations)
    contract_expected_ids = list(EXPECTED_RELEASE_CONTRACT_MUTATIONS)
    contract_fixture_ids = fixture_ids(contract_mutations)
    timeout_expected_ids = list(EXPECTED_FOUNDATION_TIMEOUT_POLICY_MUTATIONS)
    timeout_fixture_ids = fixture_ids(timeout_mutations)
    release_contract = read("docs/REPOSITORY_RELEASE.md", errors)
    fixture_readme = read("tests/repository-release/README.md", errors)

    passed = 0
    for case in mutations:
        if not isinstance(case, dict):
            errors.append(
                "repository release fixture README mutations: case is not an object"
            )
            continue
        if set(case) != {"id", "old", "new", "expected"}:
            errors.append(
                "repository release fixture README mutations: "
                "case members are not closed and exact"
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
            errors.append(
                "repository release fixture README mutations: malformed case"
            )
            continue
        if EXPECTED_RELEASE_FIXTURE_README_MUTATIONS.get(case_id) != (
            old,
            new,
            expected,
        ):
            errors.append(
                f"repository release fixture README mutation {case_id}: "
                "specification drifted from the pinned matrix"
            )
            continue
        if fixture_readme.count(old) != 1:
            errors.append(
                f"repository release fixture README mutation {case_id}: "
                f"expected one source occurrence, found {fixture_readme.count(old)}"
            )
            continue
        mutation_issues = release_census_errors(
            timeout_expected_ids,
            timeout_fixture_ids,
            script_expected_ids,
            script_fixture_ids,
            contract_expected_ids,
            contract_fixture_ids,
            release_contract,
            fixture_readme.replace(old, new, 1),
        )
        if len(mutation_issues) != 1 or expected not in mutation_issues[0]:
            errors.append(
                f"repository release fixture README mutation {case_id}: expected "
                f"sole {expected!r} refusal, got {mutation_issues}"
            )
            continue
        passed += 1
    return passed


def release_script_isolation_errors(
    rehearsal: str,
    release_check: str,
    mermaid_renderer: str,
) -> list[str]:
    errors: list[str] = []
    if rehearsal.count(REHEARSAL_TOOL_CACHE_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must allocate one per-rehearsal tool cache"
        )
    if rehearsal.count(REHEARSAL_TLA_BINDING_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must bind TLA2TOOLS_JAR to its verified jar"
        )
    if rehearsal.count(REHEARSAL_PRQ002_RECOMPUTATION_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must retain the exact PRQ-002 recomputation block"
        )
    if rehearsal.count(REHEARSAL_PRQ002C_RECOMPUTATION_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must retain the exact PRQ-002C recomputation block"
        )
    if rehearsal.count(REHEARSAL_PRQ002D_RECOMPUTATION_BLOCK) != 1:
        errors.append(
            "fresh-clone rehearsal must retain the exact PRQ-002D recomputation block"
        )
    if release_check.count(STANDALONE_TOOL_CACHE_BLOCK) != 1:
        errors.append("standalone release check must allocate a unique tool cache")
    renderer_digest = hashlib.sha256(
        mermaid_renderer.encode("utf-8")
    ).hexdigest()
    if renderer_digest != MERMAID_RENDERER_SHA256:
        errors.append(
            "Mermaid renderer exact-byte contract drifted: expected "
            f"{MERMAID_RENDERER_SHA256}, got {renderer_digest}"
        )
    return errors


def validate_release_script_mutations(errors: list[str]) -> int:
    cases = load_json("tests/repository-release/cases.json", errors)
    if not isinstance(cases, dict):
        return 0
    mutations = cases.get("release_script_mutations")
    if not isinstance(mutations, list):
        errors.append("repository release script mutations: inventory is absent")
        return 0
    if (
        len(EXPECTED_RELEASE_SCRIPT_MUTATIONS)
        != RELEASE_SCRIPT_KNOWN_BAD_MUTATION_COUNT
    ):
        errors.append(
            "repository release script mutations: executable census does not "
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
            "scripts/ci/render-readme-architecture.sh",
        }
    }
    errors.extend(
        release_script_isolation_errors(
            base_documents["scripts/ci/rehearse-fresh-clone.sh"],
            base_documents["scripts/ci/check-repository-release.sh"],
            base_documents["scripts/ci/render-readme-architecture.sh"],
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
            mutated_documents["scripts/ci/render-readme-architecture.sh"],
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
    if (
        len(EXPECTED_RELEASE_CONTRACT_MUTATIONS)
        != RELEASE_CONTRACT_KNOWN_BAD_MUTATION_COUNT
    ):
        errors.append(
            "repository release contract mutations: executable census does not "
            "match the fixture-README count boundary"
        )
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
        "tests/prq-002-identity-cohort/check.py",
        "scripts/validate_product_identity_raw_number_typing.py",
        "scripts/validate_schema_registry_prehash_replay.py",
        "--recompute-all",
        "--python-executable",
        "--node-executable",
        "tests/prq-002-identity-cohort/python/requirements.lock",
        "--prefix tests/schema-registry-prehash-replay/node",
        "PRQ002_PYTHON_BIN",
        "PRQ002_NODE_BIN",
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
#
# `validate_gate_a_prerequisites.py` is intentionally absent: its only direct
# workflow invocation is in the architecture-evidence job, after that job's
# exact hash-locked architecture environment installation. The release
# contract separately pins that job's bytes, lock path, and command inventory.
BARE_INTERPRETER_SCRIPTS = (
    "scripts/validate_architecture_surface.py",
    "scripts/validate_repository_release.py",
    "scripts/ci/validate_publication_sequence.py",
    "scripts/ci/verify_github_release.py",
    "tests/canonicalization/compare_results.py",
    "tests/canonicalization/audit_schemas.py",
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
    extraction = parser.add_mutually_exclusive_group()
    extraction.add_argument("--extract-mermaid", type=Path)
    extraction.add_argument("--extract-mermaid-directory", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required release file: {relative}")

    diagram = validate_readme(errors)
    mermaid_documents = {"README.md": (diagram,)}
    mermaid_documents.update(validate_architecture_mermaids(errors))
    mermaid_inventory_mutation_count = mermaid_inventory_self_tests(errors)
    lock = validate_toolchain(errors)
    validate_git_environment_sanitizer(errors)
    python_lock_mutation_count = validate_python_lock(errors)
    action_count, policy_mutation_count = validate_workflows(lock, errors)
    foundation_timeout_policy_mutation_count = (
        validate_foundation_timeout_policy_mutations(errors)
    )
    architecture_evidence_inventory_mutation_count = (
        validate_architecture_evidence_inventory_mutations(errors)
    )
    release_census_mutation_count = validate_release_census_mutations(errors)
    release_fixture_readme_mutation_count = (
        validate_release_fixture_readme_mutations(errors)
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
    if args.extract_mermaid_directory:
        args.extract_mermaid_directory.mkdir(parents=True, exist_ok=True)
        for relative, diagrams in mermaid_documents.items():
            for index, source in enumerate(diagrams, start=1):
                destination = (
                    args.extract_mermaid_directory
                    / mermaid_filename(relative, index)
                )
                destination.write_text(source, encoding="utf-8")

    print("Odeya repository release validation PASSED")
    print(f"- {len(WORKFLOWS)} least-privilege workflows")
    print(f"- {action_count} immutable GitHub Action references")
    print(f"- {policy_mutation_count} known-bad workflow policy mutations rejected")
    print(
        f"- {foundation_timeout_policy_mutation_count} known-bad Foundation "
        "timeout-policy mutations rejected"
    )
    print(
        f"- {architecture_evidence_inventory_mutation_count} known-bad "
        "architecture-evidence inventory mutations rejected"
    )
    print(
        f"- {release_census_mutation_count} known-bad release-census "
        "coherence mutations rejected"
    )
    print(
        f"- {release_fixture_readme_mutation_count} known-bad release-fixture "
        "README cardinality mutations rejected"
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
    print(
        f"- {sum(MERMAID_DOCUMENTS.values())} exact Mermaid architecture maps "
        f"across {len(MERMAID_DOCUMENTS)} governed documents"
    )
    print(
        f"- {mermaid_inventory_mutation_count} known-bad Mermaid inventory "
        "mutations rejected"
    )
    print("- Python, Node/npm, Java, ShellCheck, Actionlint, Zizmor, Gitleaks, Mermaid, Markdownlint, and TLA+ toolchains bounded")
    print("- architecture-only public-repository policy; no runtime or Gate A authority")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
