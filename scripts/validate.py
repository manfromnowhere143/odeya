#!/usr/bin/env python3
"""Validate Odeya's architecture-only foundation and schema contract fixtures.

This is structural, architecture-time validation. A passing result is not Gate A
acceptance and is not evidence that an executable research engine exists.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from copy import deepcopy
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import unquote

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
    from referencing import Registry, Resource
except ImportError:  # Reported as a validation error rather than a traceback.
    Draft202012Validator = None  # type: ignore[assignment]
    FormatChecker = None  # type: ignore[assignment]
    SchemaError = Exception  # type: ignore[assignment,misc]
    Registry = None  # type: ignore[assignment,misc]
    Resource = None  # type: ignore[assignment,misc]


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_DEPENDENCIES = {
    "arrow": "1.4.0",
    "attrs": "26.1.0",
    "fqdn": "1.5.1",
    "idna": "3.18",
    "isoduration": "20.11.0",
    "jsonpointer": "3.1.1",
    "jsonschema": "4.26.0",
    "jsonschema-specifications": "2025.9.1",
    "python-dateutil": "2.9.0.post0",
    "referencing": "0.37.0",
    "rfc3339-validator": "0.1.4",
    "rfc3987": "1.3.8",
    "rpds-py": "2026.6.3",
    "six": "1.17.0",
    "tzdata": "2026.3",
    "uri-template": "1.3.0",
    "webcolors": "25.10.0",
}
JSONSCHEMA_VERSION = ARCHITECTURE_DEPENDENCIES["jsonschema"]
RFC3339_VALIDATOR_VERSION = ARCHITECTURE_DEPENDENCIES["rfc3339-validator"]
SCHEMA_TEST_MANIFEST = ROOT / "tests/architecture-schema/manifest.json"
REQUIRED_FILES = (
    "README.md",
    "CHARTER.md",
    "AGENTS.md",
    "docs/ARCHITECTURE.md",
    "docs/ARCHITECTURE_STATUS.md",
    "docs/COGNITIVE_ARCHITECTURE.md",
    "docs/COMMAND_EVENT_CATALOG.md",
    "docs/RESEARCH_PROTOCOL.md",
    "docs/MATHEMATICAL_CONSTITUTION.md",
    "docs/PHYSICAL_SCIENCE_CONSTITUTION.md",
    "docs/SEMANTIC_VALIDATION.md",
    "docs/EVIDENCE_AND_MEMORY.md",
    "docs/STANDARDS_PROFILE.md",
    "docs/EVALUATION_AND_LEARNING.md",
    "docs/SECURITY_AND_AUTHORITY.md",
    "docs/AUTHORITY_MATRIX.md",
    "docs/THREAT_MODEL.md",
    "docs/THESIS_INTAKE.md",
    "docs/UI_UX.md",
    "docs/ROADMAP.md",
    "docs/IMPLEMENTATION_ORDER.md",
    "docs/INTERFACE_CONTRACTS.md",
    "docs/TRANSACTION_MODEL.md",
    "docs/TECHNOLOGY_DECISIONS.md",
    "docs/STATE_MODEL.md",
    "docs/FAILURE_MODEL.md",
    "docs/PRE_IMPLEMENTATION_GATE.md",
    "docs/FRONTIER_REVIEW_2026-07-15.md",
    "docs/PROOF_LAYER.md",
    "docs/FIRST_VERTICAL_SLICE.md",
    "docs/FIRST_SLICE_METHOD_PROFILE.md",
    "docs/FIRST_SLICE_ADMISSION_RESOLUTION_2026-07-16.md",
    "docs/CANONICALIZATION_PROFILE.md",
    "docs/DATA_GOVERNANCE.md",
    "docs/PUBLICATION_PROTOCOL.md",
    "docs/LEDGER_INTEGRITY_AND_RECOVERY.md",
    "docs/MODULE_DEPENDENCY_MANIFEST.md",
    "docs/COMMAND_CONTRACT_REGISTRY.md",
    "docs/ARCHITECTURE_REVIEW_PROTOCOL.md",
    "docs/CONSTITUTIONAL_CONSTRUCTION_AND_SEALING.md",
    "docs/GATE_A_PREREQUISITE_CLOSURE_PLAN_2026-07-16.md",
    "docs/SCHEMA_RESOURCE_REISSUE_AND_RETENTION.md",
    "docs/decisions/0015-nonrecursive-constitutional-construction.md",
    "docs/decisions/0016-separate-work-intent-from-assigned-work-contract.md",
    "docs/decisions/0017-close-first-slice-lifecycle-origins.md",
    "docs/decisions/0018-separate-registry-membership-from-history.md",
    "docs/decisions/0019-materialize-fail-closed-work-lease-candidate.md",
    "docs/decisions/0020-freeze-nonrecursive-canonical-profile-candidate.md",
    "docs/decisions/0021-separate-work-intent-core-from-identity-binding.md",
    "docs/decisions/0022-materialize-side-by-side-work-identity-successors.md",
    "docs/decisions/0023-separate-raw-reference-lineage-from-canonical-identity.md",
    "architecture/module-dependency-manifest.json",
    "architecture/first-slice-admission-resolution-candidate.json",
    "architecture/first-slice-event-identity-map.json",
    "architecture/gate-a-prerequisite-closure.json",
    "architecture/schema-resource-reissue-ledger.json",
    "architecture/canonicalization-profile-core-candidate.json",
    "architecture/canonicalization-migration-disposition-candidate.json",
    "architecture/canonicalization-profile-candidate-evidence.json",
    "architecture/work-intent-core-candidate.json",
    "architecture/work-intent-identity-candidate-evidence.json",
    "architecture/work-intent-profile-bound-candidate.json",
    "architecture/canonical-work-lease-profile-bound-candidate.json",
    "architecture/work-contract-profile-bound-candidate.json",
    "architecture/work-identity-successor-cohort-evidence.json",
    "architecture/research-state-view-sentinel-candidate.json",
    "architecture/planning-epoch-sentinel-candidate.json",
    "architecture/work-intent-reference-resolved-core-candidate.json",
    "architecture/work-intent-exact-reference-candidate.json",
    "architecture/work-intent-reference-resolution-evidence.json",
    "architecture/constitutional-construction-order.schema.json",
    "architecture/blocked-construction-receipt.schema.json",
    "schemas/research-mission.schema.json",
    "schemas/protocol-snapshot.schema.json",
    "schemas/protocol-amendment.schema.json",
    "schemas/run-manifest.schema.json",
    "schemas/command-contract-record.schema.json",
    "schemas/command-envelope.schema.json",
    "schemas/command-receipt.schema.json",
    "schemas/research-event.schema.json",
    "schemas/research-event-trace.schema.json",
    "schemas/canonicalization-profile-core.schema.json",
    "schemas/canonicalization-profile-candidate-evidence.schema.json",
    "schemas/work-intent-core.schema.json",
    "schemas/work-intent-identity-candidate-evidence.schema.json",
    "schemas/work-intent-profile-bound-candidate.schema.json",
    "schemas/canonical-work-lease-profile-bound-candidate.schema.json",
    "schemas/work-contract-profile-bound-candidate.schema.json",
    "schemas/work-identity-successor-cohort-evidence.schema.json",
    "schemas/work-intent-reference-resolved-core.schema.json",
    "schemas/work-intent-exact-reference-candidate.schema.json",
    "schemas/work-intent-reference-resolution-evidence.schema.json",
    "schemas/artifact-manifest.schema.json",
    "schemas/artifact-custody-observation.schema.json",
    "schemas/metric-result.schema.json",
    "schemas/falsifier-result.schema.json",
    "schemas/claim.schema.json",
    "schemas/claim-proposal.schema.json",
    "schemas/adjudication.schema.json",
    "schemas/claim-correction.schema.json",
    "schemas/publication-manifest.schema.json",
    "schemas/publication-candidate.schema.json",
    "schemas/publication-decision.schema.json",
    "schemas/authority-grant.schema.json",
    "schemas/root-authority-manifest.schema.json",
    "schemas/authority-assignment.schema.json",
    "schemas/data-asset-record.schema.json",
    "schemas/rights-assertion.schema.json",
    "schemas/data-use-decision.schema.json",
    "schemas/data-exposure-record.schema.json",
    "schemas/transformation-record.schema.json",
    "schemas/retention-schedule.schema.json",
    "schemas/deletion-case.schema.json",
    "schemas/legal-hold.schema.json",
    "schemas/method-registry.schema.json",
    "schemas/ledger-checkpoint.schema.json",
    "schemas/backup-manifest.schema.json",
    "schemas/key-profile.schema.json",
    "schemas/restore-verification-report.schema.json",
    "schemas/recovery-decision.schema.json",
    "schemas/module-dependency-manifest.schema.json",
    "schemas/architecture-candidate-manifest.schema.json",
    "schemas/architecture-finding.schema.json",
    "schemas/review-determination.schema.json",
    "schemas/operator-architecture-decision.schema.json",
    "schemas/blocker.schema.json",
    "schemas/verification-run.schema.json",
    "schemas/validation-rule-registry.schema.json",
    "schemas/validation-result.schema.json",
    "schemas/handoff.schema.json",
    "schemas/grounded-outcome.schema.json",
    "schemas/strategy-candidate.schema.json",
    "schemas/promotion-decision.schema.json",
    "schemas/canonical-work-lease.schema.json",
    "schemas/work-intent.schema.json",
    ".python-version",
    ".java-version",
    ".gitleaks.toml",
    ".gitleaksignore",
    ".markdownlint-cli2.jsonc",
    ".github/SECURITY.md",
    ".github/dependabot.yml",
    ".github/workflows/architecture.yml",
    ".github/workflows/release-surface.yml",
    ".github/workflows/formal.yml",
    "requirements-architecture.txt",
    "docs/REPOSITORY_RELEASE.md",
    "tests/architecture-schema/manifest.json",
    "tests/architecture-schema/fixtures/canonical-work-lease-acquired.valid.json",
    "tests/architecture-schema/fixtures/canonical-work-lease-released.valid.json",
    "tests/cognitive-contracts/check.py",
    "tests/cognitive-contracts/cases.json",
    "tests/projection-contracts/check.py",
    "tests/projection-contracts/cases.json",
    "tests/physical-contracts/check.py",
    "tests/physical-contracts/cases.json",
    "tests/mathematical-contracts/check.py",
    "tests/mathematical-contracts/cases.json",
    "tests/first-slice-resolution/check.py",
    "tests/first-slice-resolution/cases.json",
    "tests/first-slice-resolution/README.md",
    "tests/lifecycle-closure/check.py",
    "tests/lifecycle-closure/cases.json",
    "tests/lifecycle-closure/README.md",
    "tests/constitutional-construction/check.py",
    "tests/constitutional-construction/cases.json",
    "tests/constitutional-construction/README.md",
    "tests/constitutional-construction/fixtures/construction-order.valid.json",
    "tests/constitutional-construction/fixtures/blocked-construction-receipt.valid.json",
    "tests/constitutional-construction/fixtures/constitutional-chain.safe.json",
    "tests/command-identity-contracts/check.py",
    "tests/command-identity-contracts/cases.json",
    "tests/canonical-profile-candidate/check.py",
    "tests/canonical-profile-candidate/cases.json",
    "tests/canonical-profile-candidate/README.md",
    "tests/work-intent-identity-candidate/check.py",
    "tests/work-intent-identity-candidate/cases.json",
    "tests/work-intent-identity-candidate/README.md",
    "tests/work-identity-successor-cohort/check.py",
    "tests/work-identity-successor-cohort/cases.json",
    "tests/work-identity-successor-cohort/README.md",
    "tests/work-intent-reference-resolution/check.py",
    "tests/work-intent-reference-resolution/cases.json",
    "tests/work-intent-reference-resolution/README.md",
    "tests/canonicalization/README.md",
    "tests/canonicalization/manifest.json",
    "tests/canonicalization/expectations.json",
    "tests/canonicalization/source-lock.json",
    "tests/canonicalization/requirements.txt",
    "tests/canonicalization/node/package.json",
    "tests/canonicalization/node/package-lock.json",
    "tests/canonicalization/runner_python.py",
    "tests/canonicalization/runner_node.mjs",
    "tests/canonicalization/compare_results.py",
    "tests/canonicalization/audit_schemas.py",
    "tests/canonicalization/SCHEMA_AUDIT.json",
    "tests/canonicalization/results/python-rfc8785-0.1.4.json",
    "tests/canonicalization/results/node-canonicalize-3.0.0.json",
    "tests/canonicalization/results/comparison-receipt.json",
    "scripts/validate_module_manifest.py",
    "scripts/validate_first_slice_resolution.py",
    "scripts/validate_gate_a_prerequisites.py",
    "scripts/validate_schema_resource_reissues.py",
    "scripts/validate_repository_release.py",
    "scripts/ci/install-node.sh",
    "scripts/ci/install-actionlint.sh",
    "scripts/ci/install-zizmor.sh",
    "scripts/ci/install-shellcheck.sh",
    "scripts/ci/install-gitleaks.sh",
    "scripts/ci/render-readme-architecture.sh",
    "scripts/ci/check-repository-release.sh",
    "scripts/ci/rehearse-fresh-clone.sh",
    "scripts/write_release_evidence_manifest.py",
    "scripts/write_rehearsal_evidence_manifest.py",
    "scripts/compare_rehearsal_manifests.py",
    "scripts/validate_schema_contracts.py",
    "scripts/validate_contract_profiles.py",
    "tests/repository-release/README.md",
    "tests/repository-release/cases.json",
    "tools/repository-release/.node-version",
    "tools/repository-release/package.json",
    "tools/repository-release/package-lock.json",
    "tools/repository-release/requirements-architecture.lock",
    "tools/repository-release/toolchain.lock.json",
)
FORBIDDEN_IMPLEMENTATION_DIRS = (
    "apps",
    "packages",
    "services",
    "infrastructure",
    "deploy",
)
ISOLATED_CONTRACT_SUITES = (
    "tests/cognitive-contracts/check.py",
    "tests/projection-contracts/check.py",
    "tests/physical-contracts/check.py",
    "tests/mathematical-contracts/check.py",
    "tests/first-slice-resolution/check.py",
    "tests/lifecycle-closure/check.py",
    "tests/constitutional-construction/check.py",
    "tests/command-identity-contracts/check.py",
    "tests/canonical-profile-candidate/check.py",
    "tests/work-intent-identity-candidate/check.py",
    "tests/work-identity-successor-cohort/check.py",
    "tests/work-intent-reference-resolution/check.py",
)
ARCHITECTURE_EVIDENCE_CHECKS = (
    "scripts/validate_gate_a_prerequisites.py",
    "scripts/validate_schema_resource_reissues.py",
    "scripts/validate_lifecycle_guard_coverage.py",
    "scripts/validate_lifecycle_condition_coverage.py",
    "scripts/validate_canonicalization_dispositions.py",
    "scripts/validate_contract_profiles.py",
    "scripts/validate_refusal_attribution.py",
)
REPOSITORY_RELEASE_CHECKS = (
    "scripts/validate_repository_release.py",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "urn:", "data:")
IGNORED_DISCOVERY_DIRS = {
    ".git",
    ".venv",
    ".venv-architecture",
    "artifacts",
    "node_modules",
}
SCHEMA_ID_VERSION = re.compile(r"^urn:odeya:schema:[a-z0-9-]+:(\d+\.\d+\.\d+)$")


class DuplicateKeyError(ValueError):
    """Raised when JSON would otherwise silently overwrite an object member."""


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object member {key!r}")
        result[key] = value
    return result


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_required(errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            add(errors, f"missing required file: {relative}")


def load_json(path: Path, errors: list[str], label: str) -> object | None:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        add(errors, f"invalid JSON in {label}: {exc}")
        return None


def validate_jsonschema_dependencies(errors: list[str]) -> tuple[bool, bool]:
    requirement = ROOT / "requirements-architecture.txt"
    if requirement.is_file():
        dependency_lines = {
            line.strip()
            for line in requirement.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        expected_lines = {
            (
                f"jsonschema[format]=={expected_version}"
                if package == "jsonschema"
                else f"{package}=={expected_version}"
            )
            for package, expected_version in ARCHITECTURE_DEPENDENCIES.items()
        }
        for expected in sorted(expected_lines - dependency_lines):
            add(errors, f"requirements-architecture.txt must pin {expected}")
        unexpected = dependency_lines - expected_lines
        for requirement_line in sorted(unexpected):
            add(
                errors,
                "requirements-architecture.txt contains an untracked dependency: "
                f"{requirement_line}",
            )

    if (
        Draft202012Validator is None
        or FormatChecker is None
        or Registry is None
        or Resource is None
    ):
        add(
            errors,
            "architecture validation dependency missing; run "
            "python3 -m pip install -r requirements-architecture.txt",
        )
        return False, False
    dependency_versions_ready = True
    for package, expected_version in ARCHITECTURE_DEPENDENCIES.items():
        try:
            installed = version(package)
        except PackageNotFoundError:
            add(errors, f"architecture dependency missing: {package}=={expected_version}")
            dependency_versions_ready = False
            continue
        if installed != expected_version:
            add(
                errors,
                f"architecture dependency drift for {package}: "
                f"expected {expected_version}, found {installed}",
            )
            dependency_versions_ready = False

    format_ready = True
    try:
        installed_rfc3339 = version("rfc3339-validator")
    except PackageNotFoundError:
        add(
            errors,
            "date-time format dependency missing; install requirements-architecture.txt "
            "inside a dedicated virtual environment",
        )
        format_ready = False
    else:
        if installed_rfc3339 != RFC3339_VALIDATOR_VERSION:
            add(
                errors,
                "rfc3339-validator version drift: expected "
                f"{RFC3339_VALIDATOR_VERSION}, found {installed_rfc3339}",
            )
            format_ready = False
    if "date-time" not in FormatChecker.checkers:
        add(errors, "jsonschema FormatChecker has no registered date-time assertion")
        format_ready = False
    return dependency_versions_ready, dependency_versions_ready and format_ready


def validate_schemas(errors: list[str], dependency_ready: bool) -> tuple[int, dict[str, dict]]:
    count = 0
    schemas: dict[str, dict] = {}
    schema_ids: set[str] = set()
    for path in sorted((ROOT / "schemas").glob("*.json")):
        count += 1
        relative = path.relative_to(ROOT).as_posix()
        loaded = load_json(path, errors, relative)
        if not isinstance(loaded, dict):
            if loaded is not None:
                add(errors, f"{relative} must contain a JSON object")
            continue
        schema = loaded
        schemas[relative] = schema
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            add(errors, f"{relative} must use JSON Schema 2020-12")
        if schema.get("type") != "object":
            add(errors, f"{relative} root must be an object")
        if schema.get("additionalProperties") is not False:
            add(errors, f"{relative} root must fail closed on unknown fields")
        if not schema.get("$id", "").startswith("urn:odeya:schema:"):
            add(errors, f"{relative} must use an Odeya URN, not an unowned domain")
        schema_id = schema.get("$id")
        if isinstance(schema_id, str):
            if schema_id in schema_ids:
                add(errors, f"duplicate schema $id: {schema_id}")
            schema_ids.add(schema_id)
            version_match = SCHEMA_ID_VERSION.fullmatch(schema_id)
            declared_version = schema.get("properties", {}).get("schema_version", {}).get("const")
            if version_match is None:
                add(errors, f"{relative} $id must end in a semantic version")
            elif declared_version != version_match.group(1):
                add(
                    errors,
                    f"{relative} schema_version const must match its $id version",
                )
        if "schema_version" not in schema.get("required", []):
            add(errors, f"{relative} must require schema_version")
        if dependency_ready:
            try:
                Draft202012Validator.check_schema(schema)
            except SchemaError as exc:
                add(errors, f"JSON Schema meta-validation failed for {relative}: {exc.message}")

    mission = schemas.get("schemas/research-mission.schema.json")
    if mission is not None:
        falsifier_minimum = mission["properties"]["falsifiers"].get("minItems", 0)
        authority_roles = set(mission["properties"]["authorities"].get("required", []))
        if falsifier_minimum < 3:
            add(errors, "mission schema must require at least three named falsifiers")
        expected_authorities = {
            "proposal",
            "protocol",
            "safety",
            "data_rights",
            "resource",
            "execution",
            "verification",
            "outcome",
            "publication",
        }
        if authority_roles != expected_authorities:
            add(errors, "mission schema must represent all nine founding authority roles")

    command_envelope = schemas.get("schemas/command-envelope.schema.json")
    command_receipt = schemas.get("schemas/command-receipt.schema.json")
    if command_envelope is not None and command_receipt is not None:
        envelope_namespaces = set(
            command_envelope["properties"]["idempotency_scope"]["properties"]["namespace"]["enum"]
        )
        receipt_namespaces = set(
            command_receipt["properties"]["idempotency_scope"]["properties"]["namespace"]["enum"]
        )
        if envelope_namespaces != receipt_namespaces:
            add(
                errors,
                "command envelope/receipt idempotency namespace vocabularies must match exactly",
            )
        envelope_stream_types = set(command_envelope["$defs"]["stream_type"]["enum"])
        receipt_stream_types = set(
            command_receipt["properties"]["target_binding"]["properties"]["stream_type"]["enum"]
        )
        if envelope_stream_types != receipt_stream_types:
            add(
                errors,
                "command envelope/receipt target stream vocabularies must match exactly",
            )
        registry_binding_fields = {
            "command_registry_snapshot_ref",
            "command_registry_activation_ref",
            "command_contract_record_ref",
        }
        for label, schema in (
            ("command envelope", command_envelope),
            ("command receipt", command_receipt),
        ):
            missing = registry_binding_fields - set(schema.get("required", []))
            if missing:
                add(errors, f"{label} must require exact registry bindings: {sorted(missing)}")
        if "presented_authority_hints" not in set(command_envelope.get("required", [])):
            add(errors, "command envelope must require explicitly untrusted presented authority hints")
        hint_properties = command_envelope["$defs"]["presented_authority_hints"]["properties"]
        prohibited_hint_fields = {"mode", "derivation_rule_ref", "policy_decision_refs"}
        leaked_hint_fields = prohibited_hint_fields & set(hint_properties)
        if leaked_hint_fields:
            add(
                errors,
                "command envelope authority hints expose kernel-owned fields: "
                f"{sorted(leaked_hint_fields)}",
            )
        if hint_properties.get("trust_level", {}).get("const") != "untrusted_resolve_only":
            add(errors, "command envelope authority hints must be untrusted resolve-only inputs")
        if "admission_evidence" not in set(command_receipt.get("required", [])):
            add(errors, "command receipt must bind the exact admission-evidence bundle")
        rejection_codes = set(
            command_receipt["$defs"]["rejected_result"]["properties"]["rejection_code"]["enum"]
        )
        impossible_receipt_codes = {"unknown_command", "command_id_reuse"}
        leaked = rejection_codes & impossible_receipt_codes
        if leaked:
            add(
                errors,
                f"post-registry command receipt contains pre-receipt ingress codes: {sorted(leaked)}",
            )
    return count, schemas


def resolve_repo_path(raw: object, errors: list[str], label: str) -> Path | None:
    if not isinstance(raw, str) or not raw:
        add(errors, f"{label} must be a non-empty repository-relative path")
        return None
    candidate = (ROOT / raw).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        add(errors, f"{label} escapes the repository: {raw}")
        return None
    return candidate


def pointer_tokens(pointer: object, errors: list[str], case_name: str) -> list[str] | None:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        add(errors, f"schema case {case_name}: mutation path must be a JSON Pointer")
        return None
    return [token.replace("~1", "/").replace("~0", "~") for token in pointer[1:].split("/")]


def apply_mutations(instance: object, mutations: object, errors: list[str], case_name: str) -> object:
    mutated = deepcopy(instance)
    if mutations is None:
        return mutated
    if not isinstance(mutations, list):
        add(errors, f"schema case {case_name}: mutations must be an array")
        return mutated
    for index, mutation in enumerate(mutations):
        if not isinstance(mutation, dict):
            add(errors, f"schema case {case_name}: mutation {index} must be an object")
            continue
        operation = mutation.get("op")
        if operation not in {"add", "remove", "replace"}:
            add(errors, f"schema case {case_name}: mutation {index} has unsupported op {operation!r}")
            continue
        tokens = pointer_tokens(mutation.get("path"), errors, case_name)
        if not tokens:
            continue
        parent = mutated
        try:
            for token in tokens[:-1]:
                parent = parent[int(token)] if isinstance(parent, list) else parent[token]
            final = tokens[-1]
            if isinstance(parent, list):
                position = int(final)
                if operation == "add":
                    parent.insert(position, deepcopy(mutation.get("value")))
                elif operation == "remove":
                    del parent[position]
                else:
                    parent[position] = deepcopy(mutation["value"])
            elif isinstance(parent, dict):
                if operation == "remove":
                    del parent[final]
                elif operation == "replace":
                    if final not in parent:
                        raise KeyError(final)
                    parent[final] = deepcopy(mutation["value"])
                else:
                    if final in parent:
                        raise KeyError(f"add target already exists: {final}")
                    parent[final] = deepcopy(mutation.get("value"))
            else:
                raise TypeError("mutation parent is not a container")
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            add(errors, f"schema case {case_name}: mutation {index} cannot be applied: {exc}")
    return mutated


def format_error_path(error: object) -> str:
    path = getattr(error, "absolute_path", ())
    if not path:
        return "/"
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in path]
    return "/" + "/".join(escaped)


def build_preloaded_schema_registry(
    schemas: dict[str, dict], errors: list[str]
) -> object | None:
    """Build the complete local schema registry without a retrieval callback.

    `referencing.Registry()` fails on a resource that was not explicitly
    preloaded. Supplying no retrieval function is intentional: fixture
    validation must never resolve an HTTP(S), file, or mutable external
    resource. Command-contract payload closure digests are separately recorded
    in their subjects; this registry supplies only the closed repository
    resource set needed to validate structural fixtures.
    """

    if Registry is None or Resource is None:
        return None
    registry = Registry()
    for schema_name, schema in sorted(schemas.items()):
        resource_id = schema.get("$id")
        if not isinstance(resource_id, str):
            add(errors, f"{schema_name} cannot be preloaded without a string $id")
            continue
        try:
            resource = Resource.from_contents(schema)
            registry = registry.with_resource(resource_id, resource)
        except Exception as exc:  # The precise referencing exception is version-owned.
            add(
                errors,
                f"{schema_name} could not be preloaded into the network-disabled "
                f"schema registry: {type(exc).__name__}",
            )
    return registry


def schema_case_attribution_errors(name: str, case: dict, validation_errors: list) -> list[str]:
    """Bind a known-bad schema case to the exact constraint that refuses it.

    `refusal_class` records whether the refusal fires at the mutated path
    (`at_mutation`) or at the consequence a mutated discriminator implies
    (`implication`); both are legitimate, and the distinction is retained
    rather than flattened.
    """
    declared = case.get("expected_refusal")
    if not isinstance(declared, dict) or not isinstance(declared.get("pointer"), str):
        return [f"schema case {name}: known-bad case does not declare the constraint that must refuse it"]
    if case.get("refusal_class") not in {"at_mutation", "implication"}:
        return [f"schema case {name}: known-bad case does not declare its refusal class"]
    for error in validation_errors:
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        if pointer == declared["pointer"] and error.validator == declared.get("keyword"):
            return []
    observed = [
        ("/" + "/".join(str(part) for part in error.absolute_path), error.validator)
        for error in validation_errors[:6]
    ]
    return [
        f"schema case {name}: refused, but not at its declared constraint "
        f"{declared['pointer']!r} by {declared.get('keyword')!r}; got {observed}"
    ]


def validate_schema_fixtures(
    errors: list[str], schemas: dict[str, dict], dependency_ready: bool
) -> int:
    if not dependency_ready or not SCHEMA_TEST_MANIFEST.is_file():
        return 0
    loaded = load_json(
        SCHEMA_TEST_MANIFEST,
        errors,
        SCHEMA_TEST_MANIFEST.relative_to(ROOT).as_posix(),
    )
    if not isinstance(loaded, dict) or not isinstance(loaded.get("cases"), list):
        add(errors, "architecture schema manifest must contain a cases array")
        return 0

    schema_registry = build_preloaded_schema_registry(schemas, errors)
    if schema_registry is None:
        return 0

    names: set[str] = set()
    coverage: dict[str, set[str]] = {schema: set() for schema in schemas}
    case_count = 0
    for raw_case in loaded["cases"]:
        case_count += 1
        if not isinstance(raw_case, dict):
            add(errors, f"schema case {case_count} must be an object")
            continue
        name = raw_case.get("name")
        schema_name = raw_case.get("schema")
        expectation = raw_case.get("expect")
        if not isinstance(name, str) or not name:
            add(errors, f"schema case {case_count} has no name")
            continue
        if name in names:
            add(errors, f"duplicate schema case name: {name}")
        names.add(name)
        if schema_name not in schemas:
            add(errors, f"schema case {name}: unknown schema {schema_name!r}")
            continue
        if expectation not in {"valid", "invalid"}:
            add(errors, f"schema case {name}: expect must be valid or invalid")
            continue
        fixture_path = resolve_repo_path(raw_case.get("fixture"), errors, f"schema case {name} fixture")
        if fixture_path is None or not fixture_path.is_file():
            if fixture_path is not None:
                add(errors, f"schema case {name}: missing fixture {fixture_path.relative_to(ROOT)}")
            continue
        instance = load_json(fixture_path, errors, fixture_path.relative_to(ROOT).as_posix())
        if instance is None:
            continue
        validator = Draft202012Validator(
            schemas[schema_name],
            format_checker=FormatChecker(),
            registry=schema_registry,
        )
        base_errors = list(validator.iter_errors(instance))
        mutations = raw_case.get("mutations")
        if expectation == "valid" and mutations is not None:
            add(errors, f"schema case {name}: valid fixtures must not be mutated")
        if expectation == "invalid" and not isinstance(mutations, list):
            add(errors, f"schema case {name}: adversarial cases must declare mutations")
        if expectation == "invalid" and base_errors:
            first = base_errors[0]
            add(
                errors,
                f"schema case {name}: adversarial base fixture is already invalid at "
                f"{format_error_path(first)}: {first.message}",
            )
            continue
        instance = apply_mutations(instance, mutations, errors, name)
        validation_errors = sorted(
            validator.iter_errors(instance),
            key=lambda item: (
                [str(part) for part in item.absolute_path],
                str(item.validator),
                item.message,
            ),
        )
        coverage[schema_name].add(expectation)
        if expectation == "valid" and validation_errors:
            first = validation_errors[0]
            add(errors, f"schema case {name}: expected valid, failed at {format_error_path(first)}: {first.message}")
        elif expectation == "invalid" and not validation_errors:
            add(errors, f"schema case {name}: expected invalid but schema accepted it")
        elif expectation == "invalid":
            # Polarity is not attribution: for 457 cases this suite counted any
            # validation error as proof, so a constraint could stop firing while
            # an incidental one kept the case red (independent review, ADR 0068).
            add_errors = schema_case_attribution_errors(name, raw_case, validation_errors)
            for message in add_errors:
                add(errors, message)

    for schema_name, expectations in coverage.items():
        missing = {"valid", "invalid"} - expectations
        if missing:
            add(
                errors,
                f"schema fixture coverage incomplete for {schema_name}: missing {', '.join(sorted(missing))}",
            )
    return case_count


def clean_link(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if " \"" in target:
        target = target.split(" \"", 1)[0]
    return unquote(target)


def validate_markdown_links(errors: list[str]) -> tuple[int, int]:
    document_count = 0
    local_link_count = 0
    for path in sorted(ROOT.rglob("*.md")):
        if any(part in IGNORED_DISCOVERY_DIRS for part in path.parts):
            continue
        document_count += 1
        text = path.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = clean_link(match.group(1))
            if not target or target.startswith("#") or target.startswith(EXTERNAL_PREFIXES):
                continue
            target_without_anchor = target.split("#", 1)[0]
            if not target_without_anchor:
                continue
            local_link_count += 1
            candidate = Path(target_without_anchor)
            if not candidate.is_absolute():
                candidate = (path.parent / candidate).resolve()
            if not candidate.exists():
                add(
                    errors,
                    f"broken local link in {path.relative_to(ROOT)}: {target}",
                )
    return document_count, local_link_count


def validate_foundation_invariants(errors: list[str]) -> None:
    readme_path = ROOT / "README.md"
    agents_path = ROOT / "AGENTS.md"
    if not readme_path.is_file() or not agents_path.is_file():
        return
    readme = readme_path.read_text(encoding="utf-8")
    agents = agents_path.read_text(encoding="utf-8")
    corpus = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*.md")
        if not any(part in IGNORED_DISCOVERY_DIRS for part in path.parts)
    )

    if (
        "architecture foundation only" not in readme
        or "No executable research engine" not in readme
    ):
        add(errors, "README must preserve the explicit unimplemented-engine boundary")
    if "PRE_IMPLEMENTATION_GATE.md" not in readme or "PRE_IMPLEMENTATION_GATE.md" not in agents:
        add(errors, "README and AGENTS must both enforce the pre-implementation gate")
    if "odeya.danielwahnich.dev" not in readme:
        add(errors, "README must name the approved provisional subdomain")
    if "odeya.danielwahnich.ai" in corpus:
        add(errors, "obsolete provisional domain found: odeya.danielwahnich.ai")

    for directory in FORBIDDEN_IMPLEMENTATION_DIRS:
        if (ROOT / directory).exists():
            add(errors, f"implementation lock violation: top-level {directory}/ exists")


def load_fixture_object(relative: str, errors: list[str]) -> dict | None:
    path = ROOT / relative
    loaded = load_json(path, errors, relative)
    if not isinstance(loaded, dict):
        if loaded is not None:
            add(errors, f"semantic fixture must contain an object: {relative}")
        return None
    return loaded


def validate_exact_record_keys(
    records: object,
    key: str,
    expected: set[str],
    errors: list[str],
    label: str,
) -> int:
    if not isinstance(records, list):
        add(errors, f"{label} must be an array")
        return 1
    values = [record.get(key) for record in records if isinstance(record, dict)]
    if len(values) != len(records) or any(not isinstance(value, str) for value in values):
        add(errors, f"{label} must contain an object with string {key} for every member")
        return 1
    if len(set(values)) != len(values):
        add(errors, f"{label} contains duplicate {key} values")
    if set(values) != expected:
        missing = sorted(expected - set(values))
        unexpected = sorted(set(values) - expected)
        add(errors, f"{label} exact vocabulary mismatch; missing={missing}, unexpected={unexpected}")
    return 1


def validate_architecture_semantic_fixtures(errors: list[str]) -> int:
    """Check founding cross-field laws that JSON Schema cannot express alone.

    These checks cover retained architecture fixtures, not arbitrary runtime state and
    not the independent implementation obligations in SEMANTIC_VALIDATION.md.
    """

    checks = 0
    fixture_root = "tests/architecture-schema/fixtures"

    method_registry = load_fixture_object(f"{fixture_root}/method-registry.valid.json", errors)
    if method_registry is not None:
        methods = method_registry.get("methods")
        if isinstance(methods, list):
            method_keys: list[tuple[object, object]] = []
            for method in methods:
                if not isinstance(method, dict):
                    continue
                method_keys.append((method.get("method_id"), method.get("version")))
                implementations = method.get("implementations")
                if isinstance(implementations, list):
                    implementation_ids = [
                        item.get("implementation_id")
                        for item in implementations
                        if isinstance(item, dict)
                    ]
                    if len(implementation_ids) != len(implementations) or len(set(implementation_ids)) != len(implementation_ids):
                        add(errors, "method registry implementation identities must be present and unique per method")
                    if method.get("status") == "admitted":
                        minimum = method.get("verification_contract", {}).get("minimum_independent_implementations")
                        roles = {item.get("role") for item in implementations if isinstance(item, dict)}
                        if not isinstance(minimum, int) or len(implementations) < minimum:
                            add(errors, "admitted method does not meet its independent implementation minimum")
                        if not {"reference", "independent_verifier"}.issubset(roles):
                            add(errors, "admitted method requires reference and independent-verifier roles")
            if len(set(method_keys)) != len(method_keys):
                add(errors, "method registry contains duplicate method_id/version records")
        checks += 1

    checkpoint = load_fixture_object(f"{fixture_root}/ledger-checkpoint.valid.json", errors)
    if checkpoint is not None:
        coverage = checkpoint.get("artifact_verification_coverage", {})
        if isinstance(coverage, dict):
            registered = coverage.get("registered_count")
            categories = [
                coverage.get("full_bytes_verified_count"),
                coverage.get("metadata_only_count"),
                coverage.get("missing_count"),
                coverage.get("corrupt_count"),
            ]
            if not isinstance(registered, int) or any(not isinstance(value, int) for value in categories) or sum(categories) != registered:
                add(errors, "ledger checkpoint artifact coverage categories must partition registered_count")
        checkpoint_digest = checkpoint.get("checkpoint_digest")
        for signature in checkpoint.get("signatures", []):
            if isinstance(signature, dict) and signature.get("signed_digest") != checkpoint_digest:
                add(errors, "ledger checkpoint signature must bind checkpoint_digest")
        previous = checkpoint.get("previous_checkpoint")
        if isinstance(previous, dict):
            if previous.get("ledger_epoch") != checkpoint.get("ledger_epoch"):
                add(errors, "ordinary checkpoint predecessor must remain in the same ledger epoch")
            if not isinstance(previous.get("inclusive_global_position"), int) or previous["inclusive_global_position"] >= checkpoint.get("inclusive_global_position", -1):
                add(errors, "ledger checkpoint predecessor position must be strictly earlier")
        checks += 1

    backup = load_fixture_object(f"{fixture_root}/backup-manifest.valid.json", errors)
    if backup is not None:
        source = backup.get("source_frontier", {})
        if isinstance(source, dict) and source.get("begin_global_position", 0) > source.get("end_global_position", -1):
            add(errors, "backup source frontier begins after it ends")
        manifest_digest = backup.get("manifest_digest")
        catalog = backup.get("catalog_observation", {})
        if isinstance(catalog, dict) and catalog.get("manifest_digest_observed") != manifest_digest:
            add(errors, "independent backup catalog observation must bind manifest_digest")
        for signature in backup.get("signatures", []):
            if isinstance(signature, dict) and signature.get("signed_digest") != manifest_digest:
                add(errors, "backup signature must bind manifest_digest")
        checks += 1

    key_profile = load_fixture_object(f"{fixture_root}/key-profile.valid.json", errors)
    if key_profile is not None:
        expected_key_classes = {
            "constitutional_root_signing",
            "ledger_checkpoint_signing",
            "witness_signing",
            "publication_signing",
            "service_workload_identity",
            "data_encryption",
            "backup_encryption",
            "provider_operational_credential",
        }
        checks += validate_exact_record_keys(
            key_profile.get("key_classes"),
            "key_class",
            expected_key_classes,
            errors,
            "founding key profile",
        )
        for record in key_profile.get("key_classes", []):
            if not isinstance(record, dict):
                continue
            for quorum_name in ("activation_quorum", "recovery_quorum"):
                quorum = record.get(quorum_name, {})
                if isinstance(quorum, dict) and quorum.get("threshold", 0) > quorum.get("eligible_principal_count", -1):
                    add(errors, f"key profile {record.get('key_class')} {quorum_name} threshold exceeds eligible principals")

    restore = load_fixture_object(f"{fixture_root}/restore-verification-report.valid.json", errors)
    service_scopes = {
        "incident_cockpit",
        "canonical_reads",
        "reconciliation_commands",
        "ordinary_research_writes",
        "publication",
        "spending",
        "r2_plus_effects",
        "physical_actions",
    }
    if restore is not None:
        checks += validate_exact_record_keys(
            restore.get("truth_plane_results"),
            "recoverability_class",
            {"C0", "C1", "C2", "C3", "C4", "C5", "C6"},
            errors,
            "restore truth-plane results",
        )
        expected_invariants = {
            "aggregate-head-reduction",
            "command-id-receipt-uniqueness",
            "transaction-cohort-completeness",
            "grant-lifecycle-reconciliation",
            "resource-lifecycle-reconciliation",
            "eligible-claim-evidence-traversal",
            "external-effect-next-action",
            "anti-resurrection-frontier",
            "checkpoint-witness-consistency",
            "projection-position-authority-fence",
            "no-mutable-or-secret-alias-trust",
        }
        checks += validate_exact_record_keys(
            restore.get("invariant_results"),
            "invariant_id",
            expected_invariants,
            errors,
            "restore invariant results",
        )
        dispositions = []
        service_state = restore.get("recommended_service_state", {})
        for result in restore.get("invariant_results", []):
            if not isinstance(result, dict):
                continue
            disposition = result.get("disposition")
            dispositions.append(disposition)
            if disposition in {"fail", "indeterminate"} and isinstance(service_state, dict):
                for scope in result.get("affected_scopes", []):
                    decision = service_state.get(scope, {})
                    if isinstance(decision, dict) and decision.get("state") != "disabled":
                        add(errors, f"restore invariant {result.get('invariant_id')} leaves affected scope {scope} enabled")
        frontier = restore.get("current_security_frontier", {})
        if (
            restore.get("overall_disposition") == "accepted_bounded"
            and (
                any(value in {"fail", "indeterminate"} for value in dispositions)
                or not isinstance(frontier, dict)
                or frontier.get("completeness") != "proven_complete"
            )
        ):
            add(errors, "bounded restore acceptance requires passing invariants and a proven-complete security frontier")
        report_digest = restore.get("report_digest")
        for determination in restore.get("review_determinations", []):
            if isinstance(determination, dict) and determination.get("reviewed_report_digest") != report_digest:
                add(errors, "restore review determination must bind report_digest")

    recovery = load_fixture_object(f"{fixture_root}/recovery-decision.valid.json", errors)
    if recovery is not None:
        allowed = set(recovery.get("allowed_service_scopes", []))
        prohibited = set(recovery.get("prohibited_service_scopes", []))
        if allowed & prohibited or allowed | prohibited != service_scopes:
            add(errors, "recovery decision allowed/prohibited scopes must be a disjoint complete partition")
        quorum = recovery.get("quorum", {})
        if isinstance(quorum, dict):
            threshold = quorum.get("threshold")
            eligible = quorum.get("eligible_principal_count")
            members = quorum.get("members", [])
            member_ids = [member.get("principal_id") for member in members if isinstance(member, dict)]
            approvals = sum(1 for member in members if isinstance(member, dict) and member.get("vote") == "approve")
            if not isinstance(threshold, int) or not isinstance(eligible, int) or threshold > eligible:
                add(errors, "recovery quorum threshold exceeds eligible principal count")
            if len(member_ids) != len(members) or len(set(member_ids)) != len(member_ids):
                add(errors, "recovery quorum member identities must be present and unique")
            if isinstance(threshold, int) and approvals < threshold:
                add(errors, "recovery decision lacks its approval threshold")
        if recovery.get("effective_at", "") >= recovery.get("expires_at", ""):
            add(errors, "recovery decision expiry must be after effective time")
        checks += 1

    return checks


def validate_canonical_identity_evidence(
    errors: list[str],
) -> tuple[int, int, int, int]:
    """Validate retained two-path identity evidence and audit freshness offline.

    This executes only standard-library evidence comparators. It does not install
    packages, invoke either canonicalizer, access the network, or claim that the
    proposed profile has passed Gate A.
    """

    compare_path = ROOT / "tests/canonicalization/compare_results.py"
    audit_path = ROOT / "tests/canonicalization/audit_schemas.py"
    if not compare_path.is_file() or not audit_path.is_file():
        return 0, 0, 0, 0

    try:
        comparison = subprocess.run(
            [sys.executable, str(compare_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        add(errors, f"canonical identity evidence comparator failed to execute: {type(exc).__name__}")
        return 0, 0, 0, 0

    receipt: object | None = None
    try:
        receipt = json.loads(comparison.stdout, object_pairs_hook=reject_duplicate_keys)
    except (json.JSONDecodeError, DuplicateKeyError):
        add(errors, "canonical identity comparator emitted an invalid receipt")
    case_count = 0
    relation_count = 0
    if isinstance(receipt, dict):
        case_count = receipt.get("case_count", 0)
        relation_count = receipt.get("metamorphic_relation_count", 0)
        if not isinstance(case_count, int) or case_count < 1:
            add(errors, "canonical identity receipt has no positive case count")
            case_count = 0
        if not isinstance(relation_count, int) or relation_count < 1:
            add(errors, "canonical identity receipt has no positive metamorphic relation count")
            relation_count = 0
        if comparison.returncode != 0 or receipt.get("status") != "pass":
            receipt_errors = receipt.get("errors", [])
            if isinstance(receipt_errors, list) and receipt_errors:
                for message in receipt_errors[:10]:
                    add(errors, f"canonical identity evidence: {message}")
            else:
                add(errors, "canonical identity evidence comparison failed")
    elif comparison.returncode != 0:
        add(errors, "canonical identity evidence comparison failed without a receipt")

    try:
        audit_check = subprocess.run(
            [sys.executable, str(audit_path), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        add(errors, f"canonical schema audit failed to execute: {type(exc).__name__}")
        return case_count, relation_count, 0, 0
    if audit_check.returncode != 0:
        add(errors, "canonical schema/fixture migration audit is stale")

    audit_document = load_json(
        ROOT / "tests/canonicalization/SCHEMA_AUDIT.json",
        errors,
        "tests/canonicalization/SCHEMA_AUDIT.json",
    )
    schema_audit_count = 0
    fixture_audit_count = 0
    if isinstance(audit_document, dict):
        schema_audit_count = audit_document.get("schema_count", 0)
        fixture_audit_count = audit_document.get("fixture_count", 0)
        if not isinstance(schema_audit_count, int) or schema_audit_count < 1:
            add(errors, "canonical audit has no positive schema count")
            schema_audit_count = 0
        if not isinstance(fixture_audit_count, int) or fixture_audit_count < 1:
            add(errors, "canonical audit has no positive fixture count")
            fixture_audit_count = 0
        if audit_document.get("gate_a_disposition") not in {"blocked", "candidate_clear"}:
            add(errors, "canonical audit has no recognized Gate A disposition")
    return case_count, relation_count, schema_audit_count, fixture_audit_count


def validate_module_dependency_evidence(errors: list[str]) -> dict[str, int]:
    validator_path = ROOT / "scripts/validate_module_manifest.py"
    manifest_path = ROOT / "architecture/module-dependency-manifest.json"
    empty = {"layers": 0, "modules": 0, "aggregates": 0, "schemas": 0, "commands": 0, "events": 0}
    if not validator_path.is_file() or not manifest_path.is_file():
        return empty
    try:
        result = subprocess.run(
            [sys.executable, str(validator_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        add(errors, f"module dependency manifest validator failed to execute: {type(exc).__name__}")
        return empty
    if result.returncode != 0:
        detail = [line[2:] for line in result.stdout.splitlines() if line.startswith("- ")]
        if detail:
            for message in detail[:20]:
                add(errors, f"module dependency manifest: {message}")
        else:
            add(errors, "module dependency manifest validation failed")
        return empty
    manifest = load_json(manifest_path, errors, "architecture/module-dependency-manifest.json")
    if not isinstance(manifest, dict):
        return empty
    return {
        "layers": len(manifest.get("layers", [])),
        "modules": len(manifest.get("modules", [])),
        "aggregates": len(manifest.get("aggregate_owners", [])),
        "schemas": len(manifest.get("schema_owners", [])),
        "commands": manifest.get("derived_ownership", {}).get("commands", {}).get("expected_minimum_count", 0),
        "events": manifest.get("derived_ownership", {}).get("events", {}).get("expected_minimum_count", 0),
    }


def validate_first_slice_resolution(errors: list[str]) -> dict[str, int]:
    validator_path = ROOT / "scripts/validate_first_slice_resolution.py"
    inventory_path = ROOT / "architecture/first-slice-admission-resolution-candidate.json"
    empty = {"required": 0, "outside": 0, "events": 0, "aggregates": 0, "owners": 0}
    if not validator_path.is_file() or not inventory_path.is_file():
        return empty
    try:
        result = subprocess.run(
            [sys.executable, str(validator_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        add(errors, f"first-slice resolution validator failed to execute: {type(exc).__name__}")
        return empty
    if result.returncode != 0:
        detail = [line[2:] for line in result.stdout.splitlines() if line.startswith("- ")]
        if detail:
            for message in detail[:20]:
                add(errors, f"first-slice resolution: {message}")
        else:
            add(errors, "first-slice resolution validation failed")
        return empty
    inventory = load_json(
        inventory_path,
        errors,
        "architecture/first-slice-admission-resolution-candidate.json",
    )
    if not isinstance(inventory, dict):
        return empty
    return {
        "required": len(inventory.get("required_commands", [])),
        "outside": len(inventory.get("outside_commands", [])),
        "events": len(inventory.get("required_event_types", [])),
        "aggregates": len(inventory.get("aggregate_dependencies", [])),
        "owners": len(inventory.get("owner_modules", [])),
    }


def validate_isolated_contract_suites(errors: list[str]) -> int:
    """Run every mandatory contract-family suite under the pinned interpreter.

    These suites contain local structural and bounded semantic checks that are
    intentionally richer than the shared mutation manifest. A missing, timed
    out, or nonzero suite is a foundation-validation failure; a pass remains
    architecture evidence only.
    """

    passed = 0
    for relative in ISOLATED_CONTRACT_SUITES:
        path = ROOT / relative
        if not path.is_file():
            add(errors, f"isolated contract suite is missing: {relative}")
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            add(
                errors,
                f"isolated contract suite {relative} failed to execute: "
                f"{type(exc).__name__}",
            )
            continue
        if result.returncode != 0:
            detail = [
                line.strip()
                for line in (result.stdout + "\n" + result.stderr).splitlines()
                if line.strip()
            ]
            if detail:
                for message in detail[:20]:
                    add(errors, f"isolated contract suite {relative}: {message}")
            else:
                add(errors, f"isolated contract suite failed without output: {relative}")
            continue
        passed += 1
    return passed


def validate_architecture_evidence_checks(errors: list[str]) -> int:
    """Run bounded lineage/prerequisite checks without calling them contracts.

    These checks verify internal evidence consistency and explicit blockers.
    Their success is neither Gate A acceptance nor runtime authority.
    """

    passed = 0
    for relative in ARCHITECTURE_EVIDENCE_CHECKS:
        path = ROOT / relative
        if not path.is_file():
            add(errors, f"architecture evidence check is missing: {relative}")
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            add(
                errors,
                f"architecture evidence check {relative} failed to execute: "
                f"{type(exc).__name__}",
            )
            continue
        if result.returncode != 0:
            detail = [
                line.strip()
                for line in (result.stdout + "\n" + result.stderr).splitlines()
                if line.strip()
            ]
            if detail:
                for message in detail[:20]:
                    add(errors, f"architecture evidence check {relative}: {message}")
            else:
                add(errors, f"architecture evidence check failed without output: {relative}")
            continue
        passed += 1
    return passed


def validate_repository_release_checks(errors: list[str]) -> int:
    """Run repository-surface checks without implying release authority."""

    passed = 0
    for relative in REPOSITORY_RELEASE_CHECKS:
        path = ROOT / relative
        if not path.is_file():
            add(errors, f"repository release check is missing: {relative}")
            continue
        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            add(
                errors,
                f"repository release check {relative} failed to execute: "
                f"{type(exc).__name__}",
            )
            continue
        if result.returncode != 0:
            detail = [
                line.strip()
                for line in (result.stdout + "\n" + result.stderr).splitlines()
                if line.strip()
            ]
            if detail:
                for message in detail[:20]:
                    add(errors, f"repository release check {relative}: {message}")
            else:
                add(errors, f"repository release check failed without output: {relative}")
            continue
        passed += 1
    return passed


def validate_decisions(errors: list[str]) -> int:
    decision_dir = ROOT / "docs/decisions"
    decisions = sorted(decision_dir.glob("[0-9][0-9][0-9][0-9]-*.md"))
    ids: set[str] = set()
    for path in decisions:
        decision_id = path.name[:4]
        if decision_id in ids:
            add(errors, f"duplicate architecture decision ID: {decision_id}")
        ids.add(decision_id)
        text = path.read_text(encoding="utf-8")
        if "- Status:" not in text or "- Date:" not in text:
            add(errors, f"decision lacks status or date: {path.relative_to(ROOT)}")
    return len(decisions)


README_CHECKPOINT = re.compile(
    r"The current retained foundation contains (\d+) Draft 2020-12 schemas, (\d+)\s+"
    r"valid/adversarial cases, (\w+) isolated contract suites, (\w+)\s+"
    r"architecture-evidence checks, and (\w+) bounded safe TLA\+ models with\s+"
    r"(\w+) mutation controls",
    re.MULTILINE,
)
WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
}


def readme_checkpoint_errors(
    schema_count: int,
    schema_case_count: int,
    suite_count: int,
    evidence_check_count: int,
) -> list[str]:
    """Refuse a README whose checkpoint disagrees with this run's measurements.

    The checkpoint sentence states counts as fact on the repository's front page.
    Nothing verified them and all four drifted. A number published without a
    check is a claim, not evidence, and the front door is the worst place to keep
    one.
    """

    readme_path = ROOT / "README.md"
    if not readme_path.exists():
        return ["README.md is absent; the checkpoint sentence cannot be verified"]
    readme = readme_path.read_text(encoding="utf-8")
    matches = list(README_CHECKPOINT.finditer(readme))
    if not matches:
        return [
            "README architecture checkpoint sentence is absent or reworded; it must "
            "state the exact schema, case, suite, evidence-check, TLA-model, and "
            "mutation-control counts so they can be bound to a measurement"
        ]
    if len(matches) > 1:
        # Independent review defeated the first-match version of this gate with a
        # second, differently-numbered checkpoint sentence. One sentence, exactly.
        return [
            f"README contains {len(matches)} checkpoint sentences; exactly one is "
            "permitted so the binding cannot be split across contradictory copies"
        ]
    match = matches[0]

    def resolve(token: str) -> int | None:
        if token.isdigit():
            return int(token)
        return WORD_NUMBERS.get(token.lower())

    tla_models = len(sorted((ROOT / "formal/tla").glob("*.tla")))
    mutation_controls = len(sorted((ROOT / "formal/tla").glob("*.counterexample.cfg")))
    errors: list[str] = []
    declared = (
        ("Draft 2020-12 schemas", resolve(match.group(1)), schema_count),
        ("valid/adversarial cases", resolve(match.group(2)), schema_case_count),
        ("isolated contract suites", resolve(match.group(3)), suite_count),
        ("architecture-evidence checks", resolve(match.group(4)), evidence_check_count),
        ("bounded safe TLA+ models", resolve(match.group(5)), tla_models),
        ("mutation controls", resolve(match.group(6)), mutation_controls),
    )
    for label, stated, actual in declared:
        if stated is None:
            errors.append(f"README checkpoint states an unreadable count for {label}")
        elif stated != actual:
            errors.append(
                f"README checkpoint claims {stated} {label}; this run measured {actual}"
            )
    return errors


def validate_schema_contract_pins(errors: list[str], schema_count: int) -> None:
    """Read the CI schema-contract pins locally.

    The pins in scripts/validate_schema_contracts.py were CI-only, the same
    failure class as the contract-profile incident: a schema or
    fixture-classification change passed every local gate and failed only
    the remote Schema contracts job, because the valid/invalid split was
    bound by no other artifact (found live by independent review, ADR
    0063). The import is lazy so the pin module's own import of this file
    resolves after this module is fully loaded.
    """
    import validate_schema_contracts as pins

    if schema_count != pins.EXPECTED_SCHEMAS:
        add(errors, f"CI schema pin drifted: workflow expects {pins.EXPECTED_SCHEMAS}, tree has {schema_count}")
    manifest = json.loads(SCHEMA_TEST_MANIFEST.read_text(encoding="utf-8"))
    observed = {"valid": 0, "invalid": 0}
    for case in manifest.get("cases", []):
        expectation = case.get("expect")
        if expectation in observed:
            observed[expectation] += 1
    if observed != pins.EXPECTED_CASES:
        add(
            errors,
            "CI schema case-partition pin drifted: workflow expects "
            f"{pins.EXPECTED_CASES}, manifest has {observed}",
        )


def main() -> int:
    errors: list[str] = []
    validate_required(errors)
    schema_ready, fixture_ready = validate_jsonschema_dependencies(errors)
    schema_count, schemas = validate_schemas(errors, schema_ready)
    schema_case_count = validate_schema_fixtures(errors, schemas, fixture_ready)
    validate_schema_contract_pins(errors, schema_count)
    document_count, local_link_count = validate_markdown_links(errors)
    validate_foundation_invariants(errors)
    semantic_fixture_check_count = validate_architecture_semantic_fixtures(errors)
    isolated_contract_suite_count = validate_isolated_contract_suites(errors)
    architecture_evidence_check_count = validate_architecture_evidence_checks(errors)
    repository_release_check_count = validate_repository_release_checks(errors)
    (
        canonical_case_count,
        canonical_relation_count,
        canonical_schema_audit_count,
        canonical_fixture_audit_count,
    ) = validate_canonical_identity_evidence(errors)
    module_counts = validate_module_dependency_evidence(errors)
    first_slice_counts = validate_first_slice_resolution(errors)
    decision_count = validate_decisions(errors)

    # The README publishes an architecture checkpoint as fact. Nothing checked it,
    # so it drifted: it advertised 103 schemas, 620 cases, nine suites and two
    # evidence checks against an actual 112/660/12/3. A count asserted on the
    # front door and proved nowhere is the same defect as a gate with no
    # known-bad proof, one layer up. Bind it to what this run measured.
    errors.extend(
        readme_checkpoint_errors(
            schema_count,
            schema_case_count,
            isolated_contract_suite_count,
            architecture_evidence_check_count,
        )
    )

    if errors:
        print("Odeya foundation validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Odeya foundation validation PASSED")
    print(f"- {document_count} Markdown documents")
    print(f"- {schema_count} JSON schemas")
    print(f"- {schema_case_count} valid/adversarial schema cases")
    print(f"- {semantic_fixture_check_count} founding cross-field fixture groups checked")
    print(f"- {isolated_contract_suite_count} isolated contract-family suites passed")
    print(
        f"- {architecture_evidence_check_count} architecture evidence checks passed; "
        "blockers remain explicit"
    )
    print(
        f"- {repository_release_check_count} static repository release-contract check passed; "
        "no remote or release authority implied"
    )
    print(
        f"- {canonical_case_count} canonical identity cases reconciled across "
        "two pinned implementations"
    )
    print(f"- {canonical_relation_count} canonical identity metamorphic relations checked")
    print(
        f"- canonical migration inventory current for {canonical_schema_audit_count} schemas "
        f"and {canonical_fixture_audit_count} fixtures; profile blockers remain explicit"
    )
    print(
        "- logical ownership manifest checked: "
        f"{module_counts['modules']} modules, {module_counts['aggregates']} aggregates, "
        f"{module_counts['schemas']} schemas, {module_counts['commands']} commands, "
        f"{module_counts['events']} events"
    )
    print(
        "- exact first-slice resolution checked: "
        f"{first_slice_counts['required']} required / {first_slice_counts['outside']} outside commands, "
        f"{first_slice_counts['events']} events, {first_slice_counts['aggregates']} aggregates, "
        f"{first_slice_counts['owners']} owners; activation remains blocked"
    )
    print(f"- {decision_count} architecture decisions")
    print(f"- {local_link_count} local Markdown links checked")
    print("- implementation lock intact")
    print("- structural architecture validation only; Gate A acceptance remains separate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
