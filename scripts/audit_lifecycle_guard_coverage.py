#!/usr/bin/env python3
"""Measure, by mutation, which lifecycle guards have a known-bad proof.

Law 11 requires every gate to have a known-bad proof that it fires. Nothing
mechanically enforced that. Reading the suite cannot establish it either: a
known-bad trace can be refused by an incidental error while the guard it names
is broken, and a required-tag list derived from existing coverage cannot detect
a missing class. ADR 0024 bound each trace to its own guard; this tool answers
the prior question of whether a guard is exercised at all.

Method. Every `errors.append(...)` inside a declared lifecycle model is one
guard. Each is discovered by AST rather than by hand, so a guard added later
cannot be silently omitted from the audit. Each is then disabled, one at a time,
in an isolated copy of the tree, and the suite is run. A guard is proved only
when disabling it makes the suite fail. A guard whose removal leaves the suite
green has no evidence, whatever any trace, tag, or document claims.

The measurement is expensive, so it is not part of the default validator. It is
retained as `architecture/lifecycle-guard-coverage.json` and pinned to the exact
checker bytes it describes. Changing the checker invalidates the record and
requires re-proving its guards; leaving it unchanged costs a hash.

Usage:
    python3 scripts/audit_lifecycle_guard_coverage.py            # measure and report
    python3 scripts/audit_lifecycle_guard_coverage.py --write    # retain the record
    python3 scripts/audit_lifecycle_guard_coverage.py --check    # fail on drift

This is architecture evidence about retained bytes. It is not a runtime, an
admitted member, an independently reproduced verdict, or Gate A acceptance.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tests/lifecycle-closure/check.py"
SUITE_REL = "tests/lifecycle-closure/check.py"
RECORD = ROOT / "architecture/lifecycle-guard-coverage.json"

# Models audited by branch mutation. A model that builds refusals another way is
# declared unauditable below rather than reported as zero, because a silent zero
# reads as clean.
AUDITED_MODELS = (
    "authority_grant_trace_errors",
    "protocol_origin_errors",
    "data_use_cohort_errors",
    "work_lease_trace_errors",
    "work_lease_record_candidate_errors",
)

NOT_AUDITABLE = (
    {
        "function": "identity_map_mutation_errors",
        "reason": (
            "returns refusal lists directly and delegates to schema_contract_errors "
            "instead of appending to a local errors list, so branch mutation cannot "
            "attribute its guards. Its coverage is unmeasured, not proved."
        ),
    },
)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def message_template(node: ast.Call) -> str:
    """Stable identity for a guard: its message shape, not its line number."""
    argument = node.args[0]
    if isinstance(argument, ast.Constant):
        return str(argument.value)
    if isinstance(argument, ast.JoinedStr):
        return "".join(
            part.value if isinstance(part, ast.Constant) else "{}" for part in argument.values
        )
    return ast.dump(argument)


def discover(source: str) -> dict[str, list[dict[str, Any]]]:
    tree = ast.parse(source)
    found: dict[str, list[dict[str, Any]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in AUDITED_MODELS:
            continue
        branches: list[dict[str, Any]] = []
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "append"
                and isinstance(inner.func.value, ast.Name)
                and inner.func.value.id == "errors"
            ):
                branches.append(
                    {
                        "guard": message_template(inner),
                        "lineno": inner.lineno,
                        "end_lineno": inner.end_lineno,
                    }
                )
        branches.sort(key=lambda b: b["lineno"])
        found[node.name] = branches
    missing = [m for m in AUDITED_MODELS if m not in found]
    if missing:
        raise SystemExit(f"declared model(s) absent from checker: {missing}")
    return found


def run_suite(tree: Path, python: str) -> tuple[bool, str]:
    proc = subprocess.run(
        [python, SUITE_REL], cwd=tree, capture_output=True, text=True
    )
    passed = proc.returncode == 0 and "passed" in proc.stdout
    first = next(
        (l.strip().removeprefix("- ") for l in proc.stdout.splitlines() if l.startswith("- ")),
        "",
    )
    return passed, first


def measure(python: str) -> dict[str, Any]:
    source = CHECKER.read_text()
    lines = source.splitlines(keepends=True)
    models = discover(source)

    with tempfile.TemporaryDirectory(prefix="odeya-guard-audit-") as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(
            ROOT, work, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules")
        )
        target = work / SUITE_REL

        passed, _ = run_suite(work, python)
        if not passed:
            raise SystemExit(
                "control failed: the unmutated copy must pass or the audit is meaningless"
            )

        results = []
        for name in AUDITED_MODELS:
            branches = []
            for branch in models[name]:
                indent = len(lines[branch["lineno"] - 1]) - len(
                    lines[branch["lineno"] - 1].lstrip()
                )
                mutated = lines[:]
                mutated[branch["lineno"] - 1 : branch["end_lineno"]] = [
                    " " * indent + "pass\n"
                ]
                target.write_text("".join(mutated))
                suite_passed, first = run_suite(work, python)
                target.write_text(source)
                branches.append(
                    {
                        "guard": branch["guard"],
                        "proved": not suite_passed,
                        "proved_by": first.split(":")[0] if not suite_passed else None,
                    }
                )
            results.append(
                {
                    "function": name,
                    "branch_count": len(branches),
                    "proved_count": sum(1 for b in branches if b["proved"]),
                    "branches": branches,
                }
            )

    total = sum(m["branch_count"] for m in results)
    proved = sum(m["proved_count"] for m in results)
    return {
        "schema_version": "0.1.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.lifecycle-guard-coverage",
        "version": "0.1.0",
        "status": "candidate_measurement_not_admitted",
        "method": (
            "each errors.append branch of a declared lifecycle model is disabled "
            "one at a time in an isolated copy; a guard is proved only when the "
            "suite fails without it"
        ),
        "subject": SUITE_REL,
        "subject_sha256": sha256_file(CHECKER),
        "models": results,
        "not_auditable": list(NOT_AUDITABLE),
        "summary": {
            "branch_count": total,
            "proved": proved,
            "unproved": total - proved,
        },
        "boundary": (
            "architecture evidence about retained bytes only; not a runtime, an "
            "admitted member, an independently reproduced verdict, or Gate A acceptance"
        ),
    }


def report(document: dict[str, Any]) -> None:
    for model in document["models"]:
        print(f"{model['function']}: {model['proved_count']}/{model['branch_count']}")
        for branch in model["branches"]:
            if not branch["proved"]:
                print(f"    NO EVIDENCE  {branch['guard'][:88]}")
    summary = document["summary"]
    print(
        f"\n{summary['proved']}/{summary['branch_count']} guards proved; "
        f"{summary['unproved']} with no known-bad proof"
    )
    for entry in document["not_auditable"]:
        print(f"unmeasured: {entry['function']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="retain the measured record")
    parser.add_argument("--check", action="store_true", help="fail if the record has drifted")
    parser.add_argument("--python", default=sys.executable, help="interpreter used to run the suite")
    args = parser.parse_args()

    document = measure(args.python)
    report(document)
    serialized = json.dumps(document, indent=2, ensure_ascii=False) + "\n"

    if args.write:
        RECORD.write_text(serialized)
        print(f"\nretained {RECORD.relative_to(ROOT)}")
        return 0

    if args.check:
        if not RECORD.exists():
            print("\nguard-coverage record is absent", file=sys.stderr)
            return 1
        if RECORD.read_text() != serialized:
            print(
                "\nguard-coverage record does not reproduce from the current checker bytes",
                file=sys.stderr,
            )
            return 1
        print("\nguard-coverage record reproduces exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
