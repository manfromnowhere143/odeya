#!/usr/bin/env python3
"""Measure, by mutation, which lifecycle guards have a known-bad proof.

Law 11 requires every gate to have a known-bad proof that it fires. Nothing
mechanically enforced that. Reading the suite cannot establish it either: a
known-bad trace can be refused by an incidental error while the guard it names
is broken, and a required-tag list derived from existing coverage cannot detect
a missing class. ADR 0024 bound each trace to its own guard; this tool answers
the prior question of whether a guard is exercised at all.

Method. Every `errors.append(...)` inside a declared lifecycle model is one
guard. Each is discovered by AST, disabled one at a time in an isolated copy of
the tree, and the suite is run. A guard is proved only when disabling it makes
the suite fail. A guard whose removal leaves the suite green has no evidence,
whatever any trace, tag, or document claims.

Why a proved verdict here cannot be a false positive. The mutation replaces only
the refusal itself — an `errors.append(...)` span with `pass`, an early
`return [...]` with `return []` — leaving every surrounding statement intact,
including any `after = ...` assignment in the same block. It removes one refusal
and changes nothing else. Removing a refusal can only shrink the error list. A
safe reference expects an empty list and stays empty, so it cannot begin
failing. An adversarial case expects a non-empty list containing its declared
guard, so it can only fail by being accepted outright or by losing that guard,
and both outcomes are attributable to the guard just removed.

What a proved verdict does NOT mean. Disabling a guard deletes its refusal
statement, which is equivalent to forcing its condition to False. A proved
verdict therefore establishes that the statement is reachable by some retained
case. It establishes nothing about whether each condition inside the guard is
exercised. Deleting one disjunct from a guard's condition — admitting a
fabricated canonicalization profile, say — leaves the suite green and regenerates
a full-coverage record whose only diff is `subject_sha256`. Review measured 20 of
32 single-disjunct removals and 16 of 19 helper-predicate conjunct removals
surviving that way. This is statement coverage, not condition coverage; ADR 0030
records the retraction and names condition-level mutation as the next unit.

Relatedly, the digest pin below is a change-detector, not a weakening-detector.
It fires on any edit and is cleared by regenerating, and re-proving a weakened
guard succeeds.

Where this method is also weak: discovery. A proved verdict is trustworthy for
what it measures; the denominator is only as honest as `discover()`. An earlier
version of this tool matched only `errors.append` and therefore never saw two
`return [...]` guards, reporting a contented 69 when the count was 71 — both
missing guards were unproved, so the coverage claim was inflated by a silent
omission of exactly the kind this tool exists to catch. It was found by an
independent reviewer, not by the tool or its author. Adding a guard through a
construct `discover()` does not match still makes it invisible here. Treat the
denominator as a claim requiring review, never as a measurement that defends
itself, and extend `discover()` before adding a new refusal construct.

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
    "branch_map",
    "schema_contract_errors",
    "data_fixture_errors",
    "authority_grant_trace_errors",
    "protocol_origin_errors",
    "data_use_cohort_errors",
    "work_lease_trace_errors",
    "work_lease_claim_sequence_errors",
    "work_lease_record_candidate_errors",
    "identity_map_mutation_errors",
    "data_fixture_mutation_errors",
    # The suite harness refuses too: main() holds eleven `failures` sites that
    # decide whether a case is accepted, attributed, and counted. Independent
    # review showed four of its guards silently removable while the audit
    # reported full coverage of everything else (ADR 0066). A harness that can
    # be weakened invisibly is exactly the blindness this tool exists to find.
    "main",
    # main() delegates to these; the audited set must follow the guards, not
    # the function name they used to live in.
    "evaluate_cases",
    "coverage_failures",
    "harness_self_test",
    "harness_self_test_meta_proof",
    "collect_case_failures",
)

# Refusal accumulators. `errors` is the model convention; `failures` is the
# harness convention, invisible to two prior versions of this tool.
REFUSAL_NAMES = {"errors", "failures"}

# Every refusal-bearing function in the checker is audited. Two prior versions
# of this tuple made false exclusions, both caught by independent review:
# identity_map_mutation_errors was declared to "hold no guard of its own" while
# holding five return-guards (one of which a retained case already proved), and
# data_fixture_errors was in neither list at all -- the silent zero this file
# warns about, committed by this file.
NOT_AUDITABLE: tuple = ()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def message_template_from(argument: ast.expr) -> str:
    """Stable identity for a guard: its message shape, not its line number."""
    if isinstance(argument, ast.Constant):
        return str(argument.value)
    if isinstance(argument, ast.JoinedStr):
        return "".join(
            part.value if isinstance(part, ast.Constant) else "{}" for part in argument.values
        )
    return ast.unparse(argument)


def message_template(node: ast.Call) -> str:
    return message_template_from(node.args[0])


def discover(source: str) -> dict[str, list[dict[str, Any]]]:
    """Find every construct in a model that can produce a refusal.

    Discovery is the weak point of this method, not mutation. An earlier version
    matched only `errors.append` and therefore scored two `return [...]` guards
    out of existence, reporting a contented 69 when the real count was 71. A
    dormant guard added through `errors.extend` was likewise invisible to the
    audit and to the gate. Every construct that can put a refusal into the
    returned list must be matched here, and anything new must be added, or the
    denominator quietly lies.
    """
    tree = ast.parse(source)
    found: dict[str, list[dict[str, Any]]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in AUDITED_MODELS:
            continue
        branches: list[dict[str, Any]] = []
        for inner in ast.walk(node):
            guard: str | None = None
            replacement: str | None = None

            # errors.append(...) / errors.extend(...)
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr in {"append", "extend"}
                and isinstance(inner.func.value, ast.Name)
                and inner.func.value.id in REFUSAL_NAMES
            ):
                guard = message_template(inner)
                replacement = "pass"

            # errors += [...]
            elif (
                isinstance(inner, ast.AugAssign)
                and isinstance(inner.target, ast.Name)
                and inner.target.id in REFUSAL_NAMES
            ):
                guard = f"{inner.target.id} += {ast.unparse(inner.value)}"
                replacement = "pass"

            # return ["..."] — an early refusal that never touches `errors`
            elif (
                isinstance(inner, ast.Return)
                and isinstance(inner.value, ast.List)
                and inner.value.elts
            ):
                elements = inner.value.elts
                guard = (
                    message_template_from(elements[0])
                    if len(elements) == 1
                    else ast.unparse(inner.value)
                )
                replacement = "return []"

            if guard is not None and replacement is not None:
                branches.append(
                    {
                        "guard": guard,
                        "lineno": inner.lineno,
                        "end_lineno": inner.end_lineno,
                        "replacement": replacement,
                    }
                )
        branches.sort(key=lambda b: b["lineno"])
        found[node.name] = branches
    missing = [m for m in AUDITED_MODELS if m not in found]
    if missing:
        raise SystemExit(f"declared model(s) absent from checker: {missing}")
    return found


def run_suite(tree: Path, python: str) -> tuple[bool, str, bool]:
    # attributed distinguishes a suite-reported case failure from a checker
    # crash; a crash proves detection but is fragile to defensive respelling
    # of adjacent code (independent review, ADR 0065).
    proc = subprocess.run(
        [python, SUITE_REL], cwd=tree, capture_output=True, text=True
    )
    passed = proc.returncode == 0 and "passed" in proc.stdout
    first = next(
        (l.strip().removeprefix("- ") for l in proc.stdout.splitlines() if l.startswith("- ")),
        "",
    )
    return passed, first, bool(first)


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

        passed, _, _ = run_suite(work, python)
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
                    " " * indent + branch["replacement"] + "\n"
                ]
                target.write_text("".join(mutated))
                suite_passed, first, attributed = run_suite(work, python)
                target.write_text(source)
                branches.append(
                    {
                        "guard": branch["guard"],
                        "proved": not suite_passed,
                        "proved_by": first.split(":")[0] if not suite_passed else None,
                        "detection": (
                            ("case_attributed" if attributed else "crash")
                            if not suite_passed
                            else None
                        ),
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
            "crash_detected": sum(
                1
                for model in results
                for branch in model["branches"]
                if branch.get("detection") == "crash"
            ),
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
