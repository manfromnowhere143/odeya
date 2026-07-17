#!/usr/bin/env python3
"""Execute wave tranche D5a-1: annotate every mechanically resolvable digest
field with its accepted scope.

The accepted D5 table binds a digest kind and subject to each field name. The
rows executable without per-occurrence reading are the byte-digest rows (the
kind is the whole law; the subject is descriptive) and the canonical rows
naming exactly one domain -- an existing `odeya-*` domain or a `NEW:` name
reserved in the profile core's prospective registry by ADR 0039. Each such
occurrence gains an `x-odeya-digest-scope` annotation at its property node,
following the corpus's established annotation idiom.

Rows needing per-occurrence context (multi-domain subjects, target-resolved
scopes, the mixed `digest` family) and the eighteen needs-operator rows are
untouched here; they belong to their own recorded tranches.

Idempotent: an already-annotated occurrence is left alone.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = "urn:odeya:canonicalization:odeya-jcs-0.1"


def navigate(schema: dict[str, Any], pointer: str) -> Any:
    node: Any = schema
    for token in pointer.strip("/").split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def mechanical_rows() -> dict[str, dict[str, Any]]:
    table = json.loads(
        (ROOT / "architecture/canonicalization-migration-disposition-candidate.json").read_text()
    )["d5_field_table"]
    core = json.loads(
        (ROOT / "architecture/canonicalization-profile-core-candidate.json").read_text()
    )
    declared = {row["domain_separator"] for row in core["domain_registry"]}
    # a reservation is addressable by its separator or its subject class in
    # either kebab or snake form; the annotation always records the separator
    reserved: dict[str, str] = {}
    for row in core["prospective_domain_registry"]:
        sep = row["domain_separator"]
        reserved[sep] = sep
        reserved[row["subject_class"]] = sep
        reserved[row["subject_class"].replace("_", "-")] = sep
    out: dict[str, dict[str, Any]] = {}
    for row in table:
        kind = row["proposed_digest_kind"]
        subject = row["proposed_subject_class_or_domain"]
        if kind == "byte_digest":
            out[row["field_name"]] = {
                "kind": "byte_digest",
                "subject": subject,
                "algorithm": "sha-256",
                "profile": "not_a_canonical_object_digest",
                "status": "accepted_disposition_annotation",
            }
            continue
        if kind != "canonical_object_digest":
            continue
        multi = (
            ";" in subject
            or "," in subject
            or row["requires_new_domain_registration"] == "partial"
        )
        if multi:
            continue
        if subject.startswith("NEW: "):
            name = subject[len("NEW: "):].split(" (", 1)[0].strip()
            if name not in reserved:
                raise SystemExit(
                    f"{row['field_name']}: prospective domain {name!r} is not "
                    "reserved in the profile core; ADR 0039's registry is the law"
                )
            domain = reserved[name]
            status = "prospective_domain_reserved_not_declared"
        elif subject.startswith("odeya-"):
            # a parenthetical qualifier ("head event") annotates the subject
            # prose, not the domain name
            domain = subject.split(" (", 1)[0].strip()
            if domain not in declared:
                raise SystemExit(
                    f"{row['field_name']}: domain {domain!r} is not in the "
                    "declared registry"
                )
            status = "registered_domain"
        else:
            continue
        out[row["field_name"]] = {
            "kind": "canonical_object_digest",
            "domain": domain,
            "algorithm": "sha-256",
            "profile": PROFILE_ID,
            "status": status,
        }
    return out


def main() -> int:
    audit = json.loads((ROOT / "tests/canonicalization/SCHEMA_AUDIT.json").read_text())
    annotations = mechanical_rows()
    print(f"{len(annotations)} field names mechanically resolvable")
    total = 0
    for record in audit["schemas"]:
        pending = [
            f for f in record.get("digest_fields", [])
            if not f["scope_annotation_present"] and f["field"] in annotations
        ]
        if not pending:
            continue
        path = ROOT / record["path"]
        schema = json.loads(path.read_text())
        changed = 0
        for f in pending:
            node = navigate(schema, f["path"])
            if not isinstance(node, dict) or "x-odeya-digest-scope" in node:
                continue
            node["x-odeya-digest-scope"] = dict(annotations[f["field"]])
            changed += 1
        if changed:
            path.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n")
            total += changed
            print(f"{record['path'].rsplit('/', 1)[-1]:52s} {changed:3d} scopes annotated")
    print(f"total occurrences annotated: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
