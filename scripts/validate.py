#!/usr/bin/env python3
"""Validate Odeya's architecture-only foundation and schema contract fixtures.

This is structural, architecture-time validation. A passing result is not Gate A
acceptance and is not evidence that an executable research engine exists.
"""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import unquote

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError:  # Reported as a validation error rather than a traceback.
    Draft202012Validator = None  # type: ignore[assignment]
    FormatChecker = None  # type: ignore[assignment]
    SchemaError = Exception  # type: ignore[assignment,misc]


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
    "schemas/research-mission.schema.json",
    "schemas/research-event.schema.json",
    "schemas/claim.schema.json",
    "schemas/claim-proposal.schema.json",
    "schemas/adjudication.schema.json",
    "schemas/publication-manifest.schema.json",
    "schemas/authority-grant.schema.json",
    "schemas/blocker.schema.json",
    "schemas/verification-run.schema.json",
    "requirements-architecture.txt",
    "tests/architecture-schema/manifest.json",
)
FORBIDDEN_IMPLEMENTATION_DIRS = (
    "apps",
    "packages",
    "services",
    "infrastructure",
    "deploy",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "urn:", "data:")
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

    if Draft202012Validator is None or FormatChecker is None:
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
        validator = Draft202012Validator(schemas[schema_name], format_checker=FormatChecker())
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
        if ".git" in path.parts:
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
        if ".git" not in path.parts
    )

    if "does not yet contain an executable research engine" not in readme:
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


def main() -> int:
    errors: list[str] = []
    validate_required(errors)
    schema_ready, fixture_ready = validate_jsonschema_dependencies(errors)
    schema_count, schemas = validate_schemas(errors, schema_ready)
    schema_case_count = validate_schema_fixtures(errors, schemas, fixture_ready)
    document_count, local_link_count = validate_markdown_links(errors)
    validate_foundation_invariants(errors)
    decision_count = validate_decisions(errors)

    if errors:
        print("Odeya foundation validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Odeya foundation validation PASSED")
    print(f"- {document_count} Markdown documents")
    print(f"- {schema_count} JSON schemas")
    print(f"- {schema_case_count} valid/adversarial schema cases")
    print(f"- {decision_count} architecture decisions")
    print(f"- {local_link_count} local Markdown links checked")
    print("- implementation lock intact")
    print("- structural architecture validation only; Gate A acceptance remains separate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
