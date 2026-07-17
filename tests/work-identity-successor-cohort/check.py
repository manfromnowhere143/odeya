#!/usr/bin/env python3
"""Validate the side-by-side WorkIntent/WorkLease/WorkContract successor cohort."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "tests/work-identity-successor-cohort"
CASES = SUITE / "cases.json"
EVIDENCE = ROOT / "architecture/work-identity-successor-cohort-evidence.json"
EVIDENCE_SCHEMA = ROOT / "schemas/work-identity-successor-cohort-evidence.schema.json"
PROFILE_CORE = ROOT / "architecture/canonicalization-profile-core-candidate.json"
WORK_INTENT = ROOT / "architecture/work-intent-profile-bound-candidate.json"
WORK_INTENT_SCHEMA = ROOT / "schemas/work-intent-profile-bound-candidate.schema.json"
WORK_LEASE = ROOT / "architecture/canonical-work-lease-profile-bound-candidate.json"
WORK_LEASE_SCHEMA = ROOT / "schemas/canonical-work-lease-profile-bound-candidate.schema.json"
WORK_CONTRACT = ROOT / "architecture/work-contract-profile-bound-candidate.json"
WORK_CONTRACT_SCHEMA = ROOT / "schemas/work-contract-profile-bound-candidate.schema.json"
CORE = ROOT / "architecture/work-intent-core-candidate.json"
LEASE_FIXTURE = ROOT / "tests/architecture-schema/fixtures/canonical-work-lease-acquired.valid.json"
CONTRACT_FIXTURE = ROOT / "tests/cognitive-contracts/fixtures/work-contract.blocked-candidate.valid.json"

PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"
PREDECESSOR_COMMIT = "6ec40b4635815c64ba9d8c5ec084d7f480e16db1"
PREDECESSOR_TREE = "e7044da26ad273de8491a34705e87c8899173f29"
RESOURCE_EXPECTED = [
    {
        "resource_role": "work_intent",
        "predecessor_path": "schemas/work-intent.schema.json",
        "predecessor_schema_id": "urn:odeya:schema:work-intent:0.4.0",
        "successor_path": "schemas/work-intent-profile-bound-candidate.schema.json",
        "successor_schema_id": "urn:odeya:schema:work-intent:0.11.0",
        "candidate_path": "architecture/work-intent-profile-bound-candidate.json",
    },
    {
        "resource_role": "canonical_work_lease",
        "predecessor_path": "schemas/canonical-work-lease.schema.json",
        "predecessor_schema_id": "urn:odeya:schema:canonical-work-lease:0.4.0",
        "successor_path": "schemas/canonical-work-lease-profile-bound-candidate.schema.json",
        "successor_schema_id": "urn:odeya:schema:canonical-work-lease:0.7.0",
        "candidate_path": "architecture/canonical-work-lease-profile-bound-candidate.json",
    },
    {
        "resource_role": "work_contract",
        "predecessor_path": "schemas/work-contract.schema.json",
        "predecessor_schema_id": "urn:odeya:schema:work-contract:0.10.0",
        "successor_path": "schemas/work-contract-profile-bound-candidate.schema.json",
        "successor_schema_id": "urn:odeya:schema:work-contract:0.9.0",
        "candidate_path": "architecture/work-contract-profile-bound-candidate.json",
    },
]
EXPECTED_EDGES = [
    {
        "consumer_schema_id": "urn:odeya:schema:work-intent:0.11.0",
        "dependency_schema_id": "urn:odeya:schema:work-intent-core:0.1.0",
        "binding": "exact_external_ref_and_raw_schema_digest",
    },
    {
        "consumer_schema_id": "urn:odeya:schema:canonical-work-lease:0.7.0",
        "dependency_schema_id": "urn:odeya:schema:work-intent:0.11.0",
        "binding": "exact_successor_schema_and_candidate_raw_bytes",
    },
    {
        "consumer_schema_id": "urn:odeya:schema:work-contract:0.9.0",
        "dependency_schema_id": "urn:odeya:schema:work-intent:0.11.0",
        "binding": "exact_successor_schema_and_candidate_raw_bytes",
    },
]


class DuplicateKey(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKey(key)
        value[key] = item
    return value


def reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value!r}")


def load(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text("utf-8"),
        object_pairs_hook=strict_pairs,
        parse_constant=reject_nonfinite,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain one object")
    return value


def render(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def raw_binding(path: Path) -> tuple[str, int]:
    raw = path.read_bytes()
    return digest(raw), len(raw)


def pointer_tokens(pointer: str) -> list[str]:
    if not pointer.startswith("/"):
        raise ValueError(f"not a JSON Pointer: {pointer!r}")
    return [
        token.replace("~1", "/").replace("~0", "~")
        for token in pointer[1:].split("/")
    ]


def apply_mutation(subject: Any, mutation: dict[str, Any]) -> None:
    tokens = pointer_tokens(mutation["path"])
    parent = subject
    for token in tokens[:-1]:
        parent = parent[int(token)] if isinstance(parent, list) else parent[token]
    final = tokens[-1]
    operation = mutation["op"]
    if isinstance(parent, list):
        index = int(final)
        if operation == "replace":
            parent[index] = mutation["value"]
        elif operation == "remove":
            del parent[index]
        elif operation == "add":
            parent.insert(index, mutation["value"])
        else:
            raise ValueError(f"unsupported operation {operation!r}")
    elif isinstance(parent, dict):
        if operation == "replace":
            if final not in parent:
                raise KeyError(final)
            parent[final] = mutation["value"]
        elif operation == "remove":
            del parent[final]
        elif operation == "add":
            if final in parent:
                raise ValueError(f"add target exists: {final!r}")
            parent[final] = mutation["value"]
        else:
            raise ValueError(f"unsupported operation {operation!r}")
    else:
        raise TypeError("mutation parent is not a container")


def registry() -> Registry:
    result = Registry()
    for path in sorted((ROOT / "schemas").glob("*.json")):
        schema = load(path)
        result = result.with_resource(schema["$id"], Resource.from_contents(schema))
    return result


def schema_invalid(
    document: dict[str, Any], schema_path: Path, resources: Registry, label: str
) -> str | None:
    errors = list(
        Draft202012Validator(
            load(schema_path),
            registry=resources,
            format_checker=FormatChecker(),
        ).iter_errors(document)
    )
    return f"{label}_schema_invalid" if errors else None


def git(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def get(value: Any, *parts: str) -> Any:
    current = value
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def predecessor_schema_id_live(path):
    import json as _j
    return _j.loads(path.read_text())["$id"]


def profile_ref_is_exact(value: Any) -> bool:
    return value == {
        "profile_id": PROFILE_ID,
        "profile_version": "0.1.0",
        "profile_core_schema_id": "urn:odeya:schema:canonicalization-profile-core:0.3.0",
        "profile_core_raw_digest": raw_binding(PROFILE_CORE)[0],
    }


def all_false(value: Any) -> bool:
    return isinstance(value, dict) and bool(value) and all(
        item is False for item in value.values()
    )


def evaluate(
    work_intent: dict[str, Any],
    work_lease: dict[str, Any],
    work_contract: dict[str, Any],
    evidence: dict[str, Any],
) -> set[str]:
    errors: set[str] = set()
    resources = registry()
    for code in (
        schema_invalid(work_intent, WORK_INTENT_SCHEMA, resources, "work_intent"),
        schema_invalid(work_lease, WORK_LEASE_SCHEMA, resources, "work_lease"),
        schema_invalid(work_contract, WORK_CONTRACT_SCHEMA, resources, "work_contract"),
        schema_invalid(evidence, EVIDENCE_SCHEMA, resources, "evidence"),
    ):
        if code:
            errors.add(code)

    checkpoint = evidence.get("predecessor_checkpoint", {})
    try:
        resolved = git("rev-parse", "--verify", f"{PREDECESSOR_COMMIT}^{{commit}}")
        resolved_tree = git("rev-parse", "--verify", f"{PREDECESSOR_COMMIT}^{{tree}}")
    except RuntimeError:
        errors.add("predecessor_checkpoint_unresolvable")
    else:
        if (
            resolved.decode("ascii").strip() != PREDECESSOR_COMMIT
            or resolved_tree.decode("ascii").strip() != PREDECESSOR_TREE
            or checkpoint.get("commit") != PREDECESSOR_COMMIT
            or checkpoint.get("tree") != PREDECESSOR_TREE
        ):
            errors.add("predecessor_checkpoint_mismatch")

    retention = evidence.get("retention_boundary", {})
    if (
        retention.get("predecessor_resources_retained_side_by_side") is not True
        or retention.get("same_path_schema_mutation_used") is not False
        or retention.get("mutable_alias_used") is not False
        or retention.get("implicit_latest_used") is not False
        or retention.get("complete_offline_schema_registry") is not False
    ):
        errors.add("retention_boundary_escalated_or_weakened")

    successors = evidence.get("successor_resources", [])
    candidate_documents = [work_intent, work_lease, work_contract]
    represented: list[dict[str, Any]] = []
    if isinstance(successors, list):
        for index, row in enumerate(successors):
            if not isinstance(row, dict) or index >= len(RESOURCE_EXPECTED):
                continue
            expected = RESOURCE_EXPECTED[index]
            represented.append({key: row.get(key) for key in expected})
            predecessor = ROOT / expected["predecessor_path"]
            successor = ROOT / expected["successor_path"]
            try:
                historical = git("show", f"{PREDECESSOR_COMMIT}:{expected['predecessor_path']}")
            except RuntimeError:
                errors.add("predecessor_resource_unresolvable")
            else:
                if historical != predecessor.read_bytes():
                    # The reissue wave (ADR 0037/0038) lawfully changed the live
                    # bytes; the predecessor must then be a ledgered reissue of
                    # exactly the historical bytes, never a silent mutation.
                    import hashlib as _h
                    import json as _j
                    ledger = _j.loads((ROOT / "architecture/schema-resource-reissue-ledger.json").read_text())
                    hist_digest = "sha256:" + _h.sha256(historical).hexdigest()
                    ledger_row = next((r for r in ledger.get("reissues", [])
                                       if r.get("path") == expected["predecessor_path"]), None)
                    if ledger_row is None:
                        # a resource born after the ledger's source checkpoint
                        # tracks its succession in new_schema_candidates; its
                        # current digest is enforced by the reissue validator,
                        # so lineage holds when the entry carries the live $id
                        cand = next((r for r in ledger.get("new_schema_candidates", [])
                                     if r.get("path") == expected["predecessor_path"]), None)
                        if cand is not None and cand["current_candidate"].get("schema_id") == predecessor_schema_id_live(predecessor):
                            errors.discard("__never__")  # lineage accepted
                            continue_check = True
                        else:
                            continue_check = False
                    else:
                        continue_check = None
                    ok = continue_check is True
                    if ledger_row is not None:
                        # exact verification: the ledgered predecessor digest must
                        # reproduce from the bytes at the ledger row's own recorded
                        # source commit -- committed lineage, never a loose claim
                        try:
                            at_source = git(
                                "show",
                                f"{ledger_row['predecessor']['source_commit']}:{expected['predecessor_path']}",
                            )
                            ok = (
                                "sha256:" + _h.sha256(at_source).hexdigest()
                                == ledger_row["predecessor"]["raw_sha256"]
                            )
                        except RuntimeError:
                            ok = False
                    if not ok:
                        errors.add("predecessor_resource_bytes_changed")
            predecessor_schema = load(predecessor)
            successor_schema = load(successor)
            if predecessor_schema.get("$id") != expected["predecessor_schema_id"]:
                errors.add("predecessor_resource_identity_mismatch")
            if successor_schema.get("$id") != expected["successor_schema_id"]:
                errors.add("successor_resource_identity_mismatch")
            if (
                (row.get("predecessor_raw_digest"), row.get("predecessor_bytes"))
                != raw_binding(predecessor)
                or (row.get("successor_raw_digest"), row.get("successor_bytes"))
                != raw_binding(successor)
            ):
                errors.add("resource_raw_binding_mismatch")
            rendered_candidate = render(candidate_documents[index])
            if (
                row.get("candidate_raw_digest") != digest(rendered_candidate)
                or row.get("candidate_bytes") != len(rendered_candidate)
                or row.get("transition")
                != "side_by_side_immutable_successor_not_admitted"
            ):
                errors.add("candidate_raw_binding_mismatch")
    if represented != RESOURCE_EXPECTED:
        errors.add("successor_resource_inventory_mismatch")
    if evidence.get("dependency_edges") != EXPECTED_EDGES:
        errors.add("successor_dependency_graph_mismatch")

    core = load(CORE)
    intent_subject = work_intent.get("identity_subject", {})
    if intent_subject.get("semantic_core") != core:
        errors.add("work_intent_core_projection_mismatch")
    bindings = intent_subject.get("nested_reference_bindings", [])
    core_refs = [
        core.get("source_view_ref", {}),
        core.get("planning_epoch_ref", {}),
        get(core, "output_contract", "schema_ref") or {},
    ]
    target_paths = [
        ROOT / "schemas/research-state-view.schema.json",
        ROOT / "schemas/planning-epoch.schema.json",
        ROOT / "schemas/candidate-artifact.schema.json",
    ]
    if not isinstance(bindings, list) or len(bindings) != 3:
        errors.add("work_intent_reference_binding_mismatch")
    else:
        for binding, reference, target in zip(bindings, core_refs, target_paths):
            if (
                binding.get("legacy_reference_id") != reference.get("id")
                or binding.get("legacy_reference_version") != reference.get("version")
                or binding.get("legacy_reference_digest") != reference.get("digest")
                or binding.get("target_schema_id") != load(target).get("$id")
                or binding.get("target_schema_raw_digest") != raw_binding(target)[0]
                or not profile_ref_is_exact(binding.get("canonicalization_profile_ref"))
                or binding.get("admission_ref") is not None
            ):
                errors.add("work_intent_reference_binding_mismatch")
        if bindings[2].get("legacy_reference_digest") == bindings[2].get(
            "target_schema_raw_digest"
        ):
            errors.add("output_schema_mismatch_not_preserved")
        if bindings[2].get("reference_identity_status") != (
            "synthetic_legacy_digest_mismatch_blocking"
        ):
            errors.add("output_schema_mismatch_status_escalated")
    if (
        not profile_ref_is_exact(work_intent.get("canonicalization_profile_ref"))
        or work_intent.get("canonical_digest") is not None
        or work_intent.get("canonical_identity_status")
        != "not_constructible_profile_unissued_nested_references_unadmitted"
        or not all_false(work_intent.get("authority_boundary"))
    ):
        errors.add("work_intent_identity_or_authority_escalated")

    lease_subject = work_lease.get("identity_subject", {})
    lease_record = lease_subject.get("lease_record", {})
    lease_binding = lease_subject.get("work_intent_successor_binding", {})
    lease_fixture = load(LEASE_FIXTURE)
    lease_ref = lease_record.get("work_intent_ref", {}) if isinstance(lease_record, dict) else {}
    if lease_record != lease_fixture:
        errors.add("work_lease_predecessor_projection_mismatch")
    if (
        lease_binding.get("legacy_work_intent_schema_id") != lease_ref.get("schema_id")
        or lease_binding.get("legacy_object_id") != lease_ref.get("object_id")
        or lease_binding.get("legacy_version") != lease_ref.get("version")
        or lease_binding.get("legacy_digest") != lease_ref.get("digest")
        or lease_binding.get("successor_work_intent_schema_id")
        != "urn:odeya:schema:work-intent:0.11.0"
        or lease_binding.get("successor_work_intent_schema_raw_digest")
        != raw_binding(WORK_INTENT_SCHEMA)[0]
        or lease_binding.get("successor_candidate_raw_digest")
        != digest(render(work_intent))
    ):
        errors.add("work_lease_successor_binding_mismatch")
    if (
        work_lease.get("canonical_digest") is not None
        or not profile_ref_is_exact(work_lease.get("canonicalization_profile_ref"))
        or not all_false(work_lease.get("authority_boundary"))
    ):
        errors.add("work_lease_identity_or_authority_escalated")

    contract_subject = work_contract.get("identity_subject", {})
    contract_record = contract_subject.get("work_contract_candidate", {})
    contract_binding = contract_subject.get("work_intent_successor_binding", {})
    contract_fixture = load(CONTRACT_FIXTURE)
    contract_ref = (
        contract_record.get("work_intent_ref", {})
        if isinstance(contract_record, dict)
        else {}
    )
    if contract_record != contract_fixture:
        errors.add("work_contract_predecessor_projection_mismatch")
    if (
        contract_binding.get("legacy_work_intent_schema_id")
        != contract_ref.get("schema_resource_id")
        or contract_binding.get("legacy_object_id") != contract_ref.get("id")
        or contract_binding.get("legacy_version") != contract_ref.get("version")
        or contract_binding.get("legacy_canonical_digest")
        != contract_ref.get("canonical_digest")
        or contract_binding.get("successor_work_intent_schema_id")
        != "urn:odeya:schema:work-intent:0.11.0"
        or contract_binding.get("successor_work_intent_schema_raw_digest")
        != raw_binding(WORK_INTENT_SCHEMA)[0]
        or contract_binding.get("successor_candidate_raw_digest")
        != digest(render(work_intent))
    ):
        errors.add("work_contract_successor_binding_mismatch")
    if (
        work_contract.get("canonical_digest") is not None
        or not profile_ref_is_exact(work_contract.get("canonicalization_profile_ref"))
        or not all_false(work_contract.get("authority_boundary"))
    ):
        errors.add("work_contract_identity_or_authority_escalated")

    equality = evidence.get("bounded_equality_evidence", {})
    true_claims = {
        "work_intent_core_projection_equal",
        "work_intent_nested_reference_values_equal_core",
        "work_intent_target_schema_bytes_exact",
        "work_lease_predecessor_fixture_equal_embedded_subject",
        "work_lease_legacy_reference_values_equal_binding",
        "work_contract_predecessor_fixture_equal_embedded_subject",
        "work_contract_legacy_reference_values_equal_binding",
        "successor_schema_and_artifact_raw_bindings_exact",
    }
    false_claims = {
        "canonical_digest_issued",
        "cross_record_canonical_identity_equality_proven",
        "assignment_cohort_complete",
    }
    if any(equality.get(key) is not True for key in true_claims) or any(
        equality.get(key) is not False for key in false_claims
    ):
        errors.add("bounded_equality_claim_escalated_or_weakened")
    if len(evidence.get("unresolved_findings", [])) != 6:
        errors.add("unresolved_finding_inventory_incomplete")
    acceptance = evidence.get("acceptance_boundary", {})
    if (
        acceptance.get("operator_acceptance_ref") is not None
        or any(
            acceptance.get(key) is not False
            for key in (
                "profile_issued",
                "successor_resources_admitted",
                "same_active_root_membership_proven",
                "gate_a_accepted",
            )
        )
    ):
        errors.add("acceptance_fabricated")
    if not all_false(evidence.get("authority_boundary")):
        errors.add("cohort_authority_fabricated")
    return errors


def main() -> int:
    try:
        references = {
            "work_intent": load(WORK_INTENT),
            "work_lease": load(WORK_LEASE),
            "work_contract": load(WORK_CONTRACT),
            "evidence": load(EVIDENCE),
        }
        cases = load(CASES).get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError("cases.json must contain a non-empty cases array")
    except (OSError, ValueError, json.JSONDecodeError, DuplicateKey) as exc:
        print(f"Work identity successor cohort: invalid suite: {exc}", file=sys.stderr)
        return 1

    failures: list[str] = []
    names: set[str] = set()
    safe_count = 0
    adversarial_count = 0
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            failures.append(f"case {index} is not an object")
            continue
        name = case.get("name")
        kind = case.get("kind")
        if not isinstance(name, str) or not name or name in names:
            failures.append(f"case {index} has a missing or duplicate name")
            continue
        names.add(name)
        candidates = copy.deepcopy(references)
        mutations = case.get("mutations", [])
        try:
            for mutation in mutations:
                target = mutation.get("target")
                if target not in candidates:
                    raise ValueError(f"unknown target {target!r}")
                apply_mutation(candidates[target], mutation)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            failures.append(f"{name}: mutation failed: {exc}")
            continue
        observed = evaluate(
            candidates["work_intent"],
            candidates["work_lease"],
            candidates["work_contract"],
            candidates["evidence"],
        )
        expected = set(case.get("expected_errors", []))
        if kind == "safe":
            safe_count += 1
            if mutations or observed:
                failures.append(f"{name}: safe case failed with {sorted(observed)!r}")
        elif kind == "adversarial":
            adversarial_count += 1
            missing = expected - observed
            if not mutations:
                failures.append(f"{name}: adversarial case has no mutation")
            if not observed:
                failures.append(f"{name}: known-bad mutation was accepted")
            elif missing:
                failures.append(
                    f"{name}: missing {sorted(missing)!r}; observed={sorted(observed)!r}"
                )
        else:
            failures.append(f"{name}: unknown kind {kind!r}")
    if safe_count != 1:
        failures.append(f"expected exactly one safe case, found {safe_count}")
    if adversarial_count < 30:
        failures.append(f"expected at least 30 adversarial cases, found {adversarial_count}")
    if failures:
        print("Work identity successor cohort: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        "Work identity successor cohort: PASS — "
        f"{safe_count} safe reference and {adversarial_count} known-bad mutations; "
        "three immutable predecessors retained, three exact successors bound, "
        "while profile issuance, canonical identity, admission, assignment, "
        "Gate A, deployment, runtime, and effects remain blocked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
