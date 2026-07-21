#!/usr/bin/env python3
"""Gate the canonicalization-migration disposition partition.

The disposition candidate asserts that every finding of the six canonical
migration audit classes falls into exactly one of nine disposition classes, so
the operator can decide over classes instead of 1,154 raw findings. A stored
partition can drift from the audit it partitions, and this repository has
retired five coverage denominators for exactly that failure. So nothing here
trusts the stored numbers: this validator recomputes the entire partition from
the audit bytes on every run — class counts, the divergent-definition triage
under the exact comparator the candidate declares, the touched-schema union,
and both decision tables — and refuses any disagreement.

It also refuses a candidate that claims acceptance: every operator_acceptance
slot must be null and the status must remain candidate_partition_not_accepted
until Daniel decides. Acceptance is recorded by a separate explicit change,
never by a validator.

Run --self-test to prove the gate fires: each in-memory mutation of a correct
candidate must be refused.

This validates retained bytes. It does not resolve a finding, reissue a schema,
issue a canonical digest, or accept Gate A.
"""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "tests/canonicalization/SCHEMA_AUDIT.json"
CANDIDATE_PATH = ROOT / "architecture/canonicalization-migration-disposition-candidate.json"

PROSE = {"description", "title", "examples", "$comment"}
SCALARS = {"pattern", "minLength", "maxLength", "minimum", "maximum", "minItems",
           "maxItems", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
           "minProperties", "maxProperties", "format"}
SET_KEYS = {"required", "type"}
BRANCH_KEYS = {"oneOf", "anyOf", "allOf"}


def strip_prose(node):
    if isinstance(node, dict):
        return {k: strip_prose(v) for k, v in node.items() if k not in PROSE}
    if isinstance(node, list):
        return [strip_prose(v) for v in node]
    return node


def skeleton(node):
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if key in SCALARS:
                out[key] = "<scalar>"
            elif key in ("enum", "const"):
                out[key] = f"<{key}>"
            elif key in SET_KEYS and isinstance(value, list):
                out[key] = sorted(map(str, value))
            elif key in BRANCH_KEYS and isinstance(value, list):
                out[key] = sorted(json.dumps(skeleton(item), sort_keys=True) for item in value)
            else:
                out[key] = skeleton(value)
        return out
    if isinstance(node, list):
        return [skeleton(item) for item in node]
    return node


def enum_sets(node, acc):
    # const values participate as one-element vocabularies. Review found
    # signature_record misfiled as converge when its variants differ only in a
    # signature_purpose const -- deliberate domain separation, vocabulary policy.
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "enum" and isinstance(value, list):
                acc.append(tuple(sorted(map(str, value))))
            elif key == "const":
                acc.append((str(value),))
            else:
                enum_sets(value, acc)
    elif isinstance(node, list):
        for item in node:
            enum_sets(item, acc)


def recompute(audit: dict) -> dict:
    """Derive the full partition from audit bytes; the single source of truth."""
    counts = Counter()
    counts["D1"] = sum(len(f.get("nonconformant_timestamp_values", [])) for f in audit["fixtures"])
    counts["D2"] = sum(len(s.get("unprofiled_datetime_paths", [])) for s in audit["schemas"])
    counts["D3"] = sum(len(s.get("generic_scientific_decimal_paths", [])) for s in audit["schemas"])
    counts["D4"] = sum(len(s.get("generic_json_number_paths", [])) for s in audit["schemas"])
    counts["D5"] = sum(
        1 for s in audit["schemas"] for f in s.get("digest_fields", [])
        if f.get("scope_annotation_present") is False
    )
    # The audit's real field is pins_candidate_profile; an earlier version
    # tested a nonexistent "pinned" key and was correct only while zero
    # bindings were pinned. Absence still counts as unpinned: fail closed.
    counts["D9"] = sum(
        1 for s in audit["schemas"] for b in s.get("canonical_profile_bindings", [])
        if not isinstance(b, dict) or b.get("pins_candidate_profile") is not True
    )

    cache: dict[str, dict] = {}
    defs_assignments = {}
    for entry in audit["divergent_common_definitions"]:
        name = entry["definition_name"]
        bodies = []
        for variant in entry["variants"]:
            schema_path = variant["occurrences"][0]["schema"]
            if schema_path not in cache:
                cache[schema_path] = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
            bodies.append(strip_prose(cache[schema_path]["$defs"][name]))
        skels = {json.dumps(skeleton(b), sort_keys=True) for b in bodies}
        vocab = set()
        for body in bodies:
            acc: list = []
            enum_sets(body, acc)
            vocab.add(tuple(acc))
        if len(skels) == 1 and len(vocab) > 1:
            cls = "D8"
        elif len(skels) == 1:
            cls = "D6"
        else:
            cls = "D7"
        counts[cls] += 1
        defs_assignments[name] = {
            "class": cls,
            "occurrence_count": entry["occurrence_count"],
            "variant_count": entry["variant_count"],
            "variant_sha256": sorted(v["canonical_definition_sha256"] for v in entry["variants"]),
        }

    touched = set()
    for s in audit["schemas"]:
        if (s.get("unprofiled_datetime_paths") or s.get("generic_scientific_decimal_paths")
                or s.get("generic_json_number_paths")
                or any(f.get("scope_annotation_present") is False for f in s.get("digest_fields", []))
                or any(not isinstance(b, dict) or b.get("pins_candidate_profile") is not True
                       for b in s.get("canonical_profile_bindings", []))):
            touched.add(s["path"])
    for entry in audit["divergent_common_definitions"]:
        for variant in entry["variants"]:
            for occ in variant["occurrences"]:
                touched.add(occ["schema"])

    d3_pointers = sorted(
        (s["path"], p) for s in audit["schemas"]
        for p in s.get("generic_scientific_decimal_paths", [])
    )
    d5_groups: dict[str, int] = defaultdict(int)
    for s in audit["schemas"]:
        for f in s.get("digest_fields", []):
            if f.get("scope_annotation_present") is False:
                d5_groups[f["field"]] += 1

    return {
        "counts": counts,
        "defs_assignments": defs_assignments,
        "touched": touched,
        "d3_pointers": d3_pointers,
        "d5_groups": dict(d5_groups),
    }


def candidate_errors(candidate: dict, audit: dict, derived: dict | None = None) -> list[str]:
    errors: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(candidate.get("status") == "candidate_partition_not_accepted",
            "status must remain candidate_partition_not_accepted until the operator decides")
    require(candidate.get("artifact_class") == "architecture_evidence",
            "candidate must declare itself architecture evidence")

    basis = candidate.get("partition_basis", {})
    require(basis.get("schema_corpus_sha256") == audit.get("schema_corpus_sha256"),
            "candidate does not describe the current audit schema corpus")
    require(basis.get("fixture_corpus_sha256") == audit.get("fixture_corpus_sha256"),
            "candidate does not describe the current audit fixture corpus")
    require(basis.get("schema_count") == audit.get("schema_count"),
            "candidate schema_count disagrees with the current audit")
    require(basis.get("fixture_count") == audit.get("fixture_count"),
            "candidate fixture_count disagrees with the current audit")
    require(basis.get("audit_version") == audit.get("audit_version"),
            "candidate audit_version disagrees with the audit")

    # The declared comparator must be the implemented one; an unbound
    # declaration let a gutted rule pass green under review.
    comparator = candidate.get("defs_comparator", {})
    require(set(comparator.get("prose_stripped_keys", [])) == PROSE,
            "declared prose-stripped keys disagree with the implemented comparator")
    require(set(comparator.get("scalar_constraint_keys_blanked", [])) == SCALARS,
            "declared scalar constraint keys disagree with the implemented comparator")
    require(set(comparator.get("set_semantic_keys_sorted", [])) == (SET_KEYS | BRANCH_KEYS),
            "declared set-semantic keys disagree with the implemented comparator")
    require(comparator.get("vocabulary_keys") == ["enum", "const"],
            "declared vocabulary keys disagree with the implemented comparator")

    if derived is None:
        derived = recompute(audit)
    class_rows = candidate.get("classes", [])
    class_ids = [c.get("class_id") for c in class_rows]
    require(len(class_ids) == len(set(class_ids)),
            "classes contains duplicate class_id rows; a lying first row would be "
            "invisible behind last-wins dict construction")
    defs_names = [a.get("definition_name") for a in candidate.get("defs_assignments", [])]
    require(len(defs_names) == len(set(defs_names)),
            "defs_assignments contains duplicate definition names")
    field_names = [r.get("field_name") for r in candidate.get("d5_field_table", [])]
    require(len(field_names) == len(set(field_names)),
            "d5_field_table contains duplicate field names")
    union_entries = candidate.get("touched_schema_union", [])
    require(len(union_entries) == len(set(union_entries)),
            "touched_schema_union contains duplicate entries")
    declared = {c["class_id"]: c["count"] for c in class_rows}
    require(set(declared) == {"D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"},
            "candidate must declare exactly the nine disposition classes")
    for class_id, count in derived["counts"].items():
        if declared.get(class_id) != count:
            errors.append(
                f"{class_id}: candidate declares {declared.get(class_id)} findings; "
                f"recomputation from audit bytes gives {count}"
            )

    audit_total = sum(f["count"] for f in audit["blocking_findings"])
    derived_total = sum(derived["counts"].values())
    require(derived_total == audit_total,
            f"partition recomputation ({derived_total}) does not equal the audit's own "
            f"blocking-finding total ({audit_total}); the selectors no longer partition")
    require(candidate.get("total_findings") == derived_total,
            "candidate total_findings disagrees with the recomputed partition")

    stored_defs = {a["definition_name"]: a for a in candidate.get("defs_assignments", [])}
    require(set(stored_defs) == set(derived["defs_assignments"]),
            "defs_assignments does not cover exactly the audit's divergent definitions")
    for name, expected in derived["defs_assignments"].items():
        stored = stored_defs.get(name)
        if stored is None:
            continue
        for key, value in expected.items():
            if stored.get(key) != value:
                errors.append(f"defs assignment {name}.{key} disagrees with recomputation")

    require(candidate.get("touched_schema_union_count") == len(derived["touched"]),
            "touched-schema union count disagrees with recomputation")
    require(set(candidate.get("touched_schema_union", [])) == derived["touched"],
            "touched-schema union membership disagrees with recomputation")

    stored_d3 = sorted((r["schema"], r["pointer"]) for r in candidate.get("d3_decimal_table", []))
    require(stored_d3 == derived["d3_pointers"],
            "d3 decimal table rows are not exactly the audit's decimal paths")
    stored_d5 = {r["field_name"]: r["occurrences"] for r in candidate.get("d5_field_table", [])}
    require(stored_d5 == derived["d5_groups"],
            "d5 field table does not match the recomputed field groups")

    # Proposal slots: the proposing tranche filled them; the operator has not
    # decided. Every row must carry a complete, well-formed proposal -- a half-
    # proposed table is not decidable -- and rows deferring to the operator must
    # say so explicitly rather than by leaving a slot null.
    # This is a SHAPE gate. It proves every row carries a complete, well-formed
    # proposal from the declared vocabulary; it cannot prove a proposal is
    # semantically right for its field -- review demonstrated that swapping two
    # rows' contents passes every check here. Content correctness is the
    # operator's judgment, informed by the retained adversarial review, and no
    # arithmetic can substitute for it.
    d3_confidences = {"certain", "likely", "needs_operator"}
    vocabulary = set(
        (candidate.get("proposal_provenance") or {}).get("d3_semantic_type_vocabulary", [])
    )
    require(bool(vocabulary), "proposal provenance declares no semantic-type vocabulary")
    for row in candidate.get("d3_decimal_table", []):
        if not all(isinstance(row.get(k), str) and row[k].strip() for k in
                   ("proposed_semantic_type", "proposed_unit", "proposed_precision")):
            errors.append(f"d3 row {row.get('pointer')} lacks a complete proposal")
        elif row["proposed_semantic_type"] not in vocabulary:
            errors.append(
                f"d3 row {row.get('pointer')} proposes {row['proposed_semantic_type']!r}, "
                "which is outside the declared semantic-type vocabulary"
            )
        if row.get("confidence") not in d3_confidences:
            errors.append(f"d3 row {row.get('pointer')} has no valid confidence")
    d5_kinds = {"byte_digest", "canonical_object_digest", "mixed_needs_split", "needs_operator"}
    for row in candidate.get("d5_field_table", []):
        if row.get("proposed_digest_kind") not in d5_kinds:
            errors.append(f"d5 field {row.get('field_name')} has no valid digest kind")
        subject = row.get("proposed_subject_class_or_domain")
        if not isinstance(subject, str) or len(subject.strip()) < 4:
            errors.append(f"d5 field {row.get('field_name')} lacks a substantive subject proposal")
        if row.get("requires_new_domain_registration") not in (True, False, "partial", "unknown"):
            errors.append(f"d5 field {row.get('field_name')} lacks a new-domain disposition")
        if row.get("proposed_digest_kind") in {"mixed_needs_split", "needs_operator"} and not (
            isinstance(row.get("note"), str) and row["note"].strip()
        ):
            # A deferring row must say why; a long subject string is not a reason.
            errors.append(
                f"d5 field {row.get('field_name')} defers to the operator without saying why"
            )

    acceptance = candidate.get("operator_acceptance", {})
    require(set(acceptance) == set(declared),
            "operator_acceptance must carry one slot per class")
    for class_id, decision in acceptance.items():
        require(decision is None,
                f"operator_acceptance[{class_id}] is set; acceptance is recorded by an "
                "explicit operator change, never pre-filled")
    return errors


def self_test(candidate: dict, audit: dict, derived: dict | None = None) -> int:
    """Every mutation of a correct candidate must be refused."""
    if derived is None:
        derived = recompute(audit)
    if candidate_errors(copy.deepcopy(candidate), audit, derived):
        print("self-test control failed: the retained candidate itself is refused", file=sys.stderr)
        return 1

    def mutate(label, fn):
        broken = copy.deepcopy(candidate)
        fn(broken)
        if not candidate_errors(broken, audit, derived):
            print(f"self-test FAILED: mutation not refused: {label}", file=sys.stderr)
            return False
        return True

    checks = [
        ("class count tampered", lambda c: c["classes"][0].__setitem__("count", c["classes"][0]["count"] + 1)),
        ("total tampered consistently", lambda c: c.__setitem__("total_findings", c["total_findings"] - 1)),
        # the defs wave executed; the assignment table is empty by
        # measurement, so the known-bad proof is a fabricated assignment
        ("defs phantom assignment injected", lambda c: c["defs_assignments"].append({
            "definition_name": "fabricated_definition",
            "class": "D7",
            "occurrence_count": 1,
            "variant_count": 2,
            "variant_sha256": ["0" * 64, "1" * 64]})),
        # zero findings touch zero schemas; the fabrication proof appends
        ("touched schema fabricated", lambda c: (c["touched_schema_union"].append("schemas/fabricated.schema.json"), c.__setitem__("touched_schema_union_count", c["touched_schema_union_count"] + 1))),
        ("acceptance pre-filled", lambda c: c["operator_acceptance"].__setitem__("D1", "accepted")),
        ("status promoted", lambda c: c.__setitem__("status", "accepted_partition")),
        ("corpus digest swapped", lambda c: c["partition_basis"].__setitem__("schema_corpus_sha256", "0" * 64)),
        ("corpus count tampered", lambda c: c["partition_basis"].__setitem__("fixture_count", c["partition_basis"]["fixture_count"] - 1)),
        # the D3 tranche executed; the table is empty by measurement, so the
        # known-bad proof is now a fabricated row, not a dropped one
        ("d3 phantom row injected", lambda c: c["d3_decimal_table"].append({
            "schema": "schemas/authority-grant.schema.json",
            "pointer": "/$defs/resource_budget/properties/fabricated",
            "proposed_semantic_type": "duration_seconds",
            "proposed_unit": "seconds",
            "proposed_precision": "6",
            "confidence": "certain"})),
        ("d5 phantom row injected", lambda c: c["d5_field_table"].append({
            "field_name": "fabricated_digest",
            "occurrences": 1,
            "lexical_constraints": {"sha256_lowercase_hex": 1},
            "schema_count": 1,
            "proposed_digest_kind": "byte_digest",
            "proposed_subject_class_or_domain": "fabricated bytes",
            "requires_new_domain_registration": False})),
        ("duplicate class row prepended", lambda c: c["classes"].insert(0, dict(c["classes"][4], count=9999))),
        ("comparator declaration gutted", lambda c: c["defs_comparator"].__setitem__("vocabulary_keys", ["enum"])),
    ]
    if all(mutate(label, fn) for label, fn in checks):
        print(f"disposition self-test passed: {len(checks)} known-bad mutations refused")
        return 0
    return 1


def main() -> int:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    if not CANDIDATE_PATH.exists():
        print("canonicalization disposition candidate is absent", file=sys.stderr)
        return 1
    candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))

    derived = recompute(audit)
    if "--self-test" in sys.argv:
        return self_test(candidate, audit, derived)

    errors = candidate_errors(candidate, audit, derived)
    if errors:
        print("canonicalization disposition validation FAILED")
        for message in errors:
            print(f"- {message}")
        return 1

    # The gate proves itself on every run: an advertised self-test that only
    # runs when typed by hand is dead code waiting to rot.
    if self_test(candidate, audit, derived) != 0:
        return 1

    counts = derived["counts"]
    print(
        "canonicalization disposition partition checked: "
        f"{sum(counts.values())} findings recomputed into 9 classes from audit bytes; "
        f"touched-schema union {candidate['touched_schema_union_count']}; all acceptance slots null"
    )
    print(
        "Boundary: architecture evidence only; no finding is resolved, no schema reissued, "
        "no canonical digest issued, and Gate A acceptance remains separate."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
