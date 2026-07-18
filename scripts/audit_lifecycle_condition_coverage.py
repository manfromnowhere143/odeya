#!/usr/bin/env python3
"""Measure, by mutation, which lifecycle guard *conditions* have evidence.

ADR 0025 proved every guard statement reachable; ADR 0030 retracted the
strength of that result: deleting one disjunct from a guard's condition —
admitting a fabricated canonicalization profile, say — left the suite green,
because statement mutation deletes the whole refusal and can never see a
weakened part of one. Review measured that blindness by hand across five
models. This tool mechanizes the measurement, exactly as the statement audit
mechanized reachability: measure first, publish the blindness honestly,
close it with cases afterward.

Method. Within every audited model, each `if` whose immediate body holds a
refusal construct is a guarded test; within every audited helper predicate,
each `return` whose value is a boolean chain is one too. Each top-level
member of such a boolean chain is one auditable condition. One at a time,
the member is removed from an isolated copy of the tree — an `or` loses one
way to fire, an `and` fires more often than it should — and the suite runs.
A condition is proved only when its removal makes the suite fail. A removal
that leaves the suite green is a weakening no retained case can see.

Why detection is attributable in both directions. Removing a disjunct can
only shrink a guard's firing set, so the suite can fail only by a known-bad
case being accepted or losing its declared guard. Removing a conjunct can
only grow it, so the suite can fail only by a case collecting a refusal it
did not declare — including the safe references, which expect none. A crash
after removal (a deleted `isinstance` that another part of the guard relied
on) is also detection: the weakened checker cannot run at all.

What this audit still cannot see, stated before anyone reads the number:

- A test with a single top-level condition has no part to remove here; its
  reachability is the statement audit's result and its false side is held
  by the safe references. It is counted explicitly below, never silently.
- A nested boolean group inside a removed member is exercised only as a
  whole; nesting is counted explicitly, not descended into.
- A structural comparison (`observed != expected` over a dict) is one
  condition here no matter how many fields it compares. Field-level
  blindness inside structural expectations is real and is not measured by
  this tool.
- The denominator is only as honest as `discover_conditions()`. A guard
  expressed through a construct it does not match is invisible, exactly as
  the statement audit's denominator was twice found wrong by review.

The measurement is expensive, so it is not part of the default validator.
It is retained as `architecture/lifecycle-condition-coverage.json`, pinned
to the exact checker bytes; the cheap gate in the default validator binds
digest and arithmetic only, and the exact-commit fresh-clone rehearsal
re-measures with `--check`, which is the only real enforcement.

Usage:
    python3 scripts/audit_lifecycle_condition_coverage.py            # measure and report
    python3 scripts/audit_lifecycle_condition_coverage.py --write    # retain the record
    python3 scripts/audit_lifecycle_condition_coverage.py --check    # fail on drift

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
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tests/lifecycle-closure/check.py"
SUITE_REL = "tests/lifecycle-closure/check.py"
RECORD = ROOT / "architecture/lifecycle-condition-coverage.json"

# The same ten models the statement audit declares, plus the helper
# predicates whose conjuncts ADR 0030 measured by hand. A helper is audited
# at its boolean returns; a model is audited at its guarded `if` tests.
AUDITED_MODELS = (
    "branch_map",
    "schema_contract_errors",
    "data_fixture_errors",
    "authority_grant_trace_errors",
    "protocol_origin_errors",
    "data_use_cohort_errors",
    "work_lease_trace_errors",
    "work_lease_record_candidate_errors",
    "identity_map_mutation_errors",
    "data_fixture_mutation_errors",
    # The suite harness refuses too, and independent review proved four of its
    # boolean members silently removable while this tool reported near-complete
    # coverage of everything else (ADR 0066).
    "main",
    # main() delegates to these; the audited set must follow the guards, not
    # the function name they used to live in.
    "evaluate_cases",
    "coverage_failures",
    "harness_self_test",
    "collect_case_failures",
)
REFUSAL_NAMES = {"errors", "failures"}
AUDITED_HELPERS = (
    "valid_artifact_ref",
    "valid_record_ref",
    "valid_versioned_identity",
)
# Refusal-DETERMINING helpers: they hold no refusal themselves, but their
# boolean tests decide what every guard downstream can see. Independent
# review found a removable conjunct here that was invisible to both the
# numerator and the not-audited residue -- the defensive filter on the
# repository walk feeding the canonical defining-path guard (ADR 0069).
AUDITED_VALUE_HELPERS = (
    # refusal_matches decides whether a declared refusal counts at all, and the
    # meta proof decides whether the self-test is load-bearing; review found
    # both outside every audited tuple, with weakenings surviving (ADR 0077).
    "refusal_matches",
    "harness_self_test_meta_proof",
    "nested",
    "scan_defining_paths",
    "exact_value",
    "transition_spec",
)


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def message_template_from(argument: ast.expr) -> str:
    if isinstance(argument, ast.Constant):
        return str(argument.value)
    if isinstance(argument, ast.JoinedStr):
        return "".join(
            part.value if isinstance(part, ast.Constant) else "{}" for part in argument.values
        )
    return ast.unparse(argument)


def holds_refusal(statements: list[ast.stmt]) -> str | None:
    """The guard message when this immediate body can produce a refusal."""
    for statement in statements:
        for inner in ast.walk(statement):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr in {"append", "extend"}
                and isinstance(inner.func.value, ast.Name)
                and inner.func.value.id in REFUSAL_NAMES
            ):
                return message_template_from(inner.args[0])
            if (
                isinstance(inner, ast.AugAssign)
                and isinstance(inner.target, ast.Name)
                and inner.target.id in REFUSAL_NAMES
            ):
                return f"{inner.target.id} += {ast.unparse(inner.value)}"
            if (
                isinstance(inner, ast.Return)
                and isinstance(inner.value, ast.List)
                and inner.value.elts
            ):
                elements = inner.value.elts
                return (
                    message_template_from(elements[0])
                    if len(elements) == 1
                    else ast.unparse(inner.value)
                )
    return None


def discover_conditions(source: str) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    """Every removable top-level member of a guarded boolean chain.

    Also counts, explicitly, what is present but not auditable here: tests
    with a single top-level condition, and nested boolean groups inside an
    audited member. A silent omission reads as clean; these must not.
    """
    tree = ast.parse(source)
    found: dict[str, list[dict[str, Any]]] = {}
    not_audited = {
        "single_condition_tests": 0,
        "nested_boolean_groups": 0,
        # A ternary shapes a value a later refusal reads. Removing it has two
        # non-equivalent forms (keep the true arm, keep the false arm), so it
        # is counted here rather than audited under one arbitrary choice.
        "ternary_selectors": 0,
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name in AUDITED_MODELS:
            units: list[dict[str, Any]] = []
            for inner in ast.walk(node):
                if not isinstance(inner, ast.If):
                    continue
                guard = holds_refusal(inner.body)
                if guard is None:
                    continue
                test = inner.test
                if not isinstance(test, ast.BoolOp):
                    not_audited["single_condition_tests"] += 1
                    continue
                role = "disjunct" if isinstance(test.op, ast.Or) else "conjunct"
                for index, member in enumerate(test.values):
                    if isinstance(member, ast.BoolOp):
                        not_audited["nested_boolean_groups"] += 1
                    units.append(
                        {
                            "guard": guard,
                            "role": role,
                            "index": index,
                            "condition": ast.unparse(member),
                            "lineno": inner.lineno,
                            "col_offset": inner.col_offset,
                            "site": "if",
                        }
                    )
            for inner in ast.walk(node):
                if isinstance(inner, ast.IfExp):
                    not_audited["ternary_selectors"] += 1
                if not isinstance(inner, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    continue
                for gen_index, generator in enumerate(inner.generators):
                    for if_index, condition in enumerate(generator.ifs):
                        units.append(
                            {
                                "guard": f"comprehension at line {inner.lineno}",
                                "role": "comprehension_filter",
                                "index": if_index,
                                "generator": gen_index,
                                "condition": ast.unparse(condition),
                                "lineno": inner.lineno,
                                "col_offset": inner.col_offset,
                                "site": "comprehension",
                            }
                        )
            found[node.name] = units
        elif node.name in AUDITED_VALUE_HELPERS:
            units = []
            for inner in ast.walk(node):
                if not (isinstance(inner, ast.If) and isinstance(inner.test, ast.BoolOp)):
                    continue
                role = "disjunct" if isinstance(inner.test.op, ast.Or) else "conjunct"
                for index, member in enumerate(inner.test.values):
                    if isinstance(member, ast.BoolOp):
                        not_audited["nested_boolean_groups"] += 1
                    units.append(
                        {
                            "guard": f"value helper {node.name}",
                            "role": role,
                            "index": index,
                            "condition": ast.unparse(member),
                            "lineno": inner.lineno,
                            "col_offset": inner.col_offset,
                            "site": "if",
                        }
                    )
            found[node.name] = units
        elif node.name in AUDITED_HELPERS:
            units = []
            for inner in ast.walk(node):
                if not (isinstance(inner, ast.Return) and isinstance(inner.value, ast.BoolOp)):
                    continue
                role = "disjunct" if isinstance(inner.value.op, ast.Or) else "conjunct"
                for index, member in enumerate(inner.value.values):
                    if isinstance(member, ast.BoolOp):
                        not_audited["nested_boolean_groups"] += 1
                    units.append(
                        {
                            "guard": f"return of {node.name}",
                            "role": role,
                            "index": index,
                            "condition": ast.unparse(member),
                            "lineno": inner.lineno,
                            "col_offset": inner.col_offset,
                            "site": "return",
                        }
                    )
            found[node.name] = units
    missing = [
        name
        for name in (*AUDITED_MODELS, *AUDITED_HELPERS, *AUDITED_VALUE_HELPERS)
        if name not in found
    ]
    if missing:
        raise SystemExit(f"declared function(s) absent from checker: {missing}")
    return found, not_audited


def mutated_source(tree: ast.Module, unit: dict[str, Any]) -> str:
    """The whole module with one boolean member removed, re-serialized."""
    work = deepcopy(tree)
    if unit["site"] == "comprehension":
        for node in ast.walk(work):
            if (
                isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp))
                and node.lineno == unit["lineno"]
                and node.col_offset == unit["col_offset"]
            ):
                generator = node.generators[unit["generator"]]
                generator.ifs = [
                    condition
                    for index, condition in enumerate(generator.ifs)
                    if index != unit["index"]
                ]
                ast.fix_missing_locations(work)
                return ast.unparse(work)
        raise SystemExit(
            f"comprehension site not found at {unit['lineno']}:{unit['col_offset']}; "
            "the checker bytes changed under the audit"
        )
    for node in ast.walk(work):
        if unit["site"] == "if":
            match = (
                isinstance(node, ast.If)
                and node.lineno == unit["lineno"]
                and node.col_offset == unit["col_offset"]
                and isinstance(node.test, ast.BoolOp)
            )
            target = node.test if match else None
        else:
            match = (
                isinstance(node, ast.Return)
                and node.lineno == unit["lineno"]
                and node.col_offset == unit["col_offset"]
                and isinstance(node.value, ast.BoolOp)
            )
            target = node.value if match else None
        if not match:
            continue
        remaining = [value for i, value in enumerate(target.values) if i != unit["index"]]
        replacement = remaining[0] if len(remaining) == 1 else ast.BoolOp(op=target.op, values=remaining)
        if unit["site"] == "if":
            node.test = replacement
        else:
            node.value = replacement
        ast.fix_missing_locations(work)
        return ast.unparse(work)
    raise SystemExit(
        f"condition site not found at {unit['lineno']}:{unit['col_offset']}; "
        "the checker bytes changed under the audit"
    )


def run_suite(tree_path: Path, python: str) -> tuple[bool, str, bool]:
    """(passed, first failure, attributed).

    attributed is True when the failure is a suite-reported case failure and
    False when the checker crashed before reporting any. Independent review
    showed the distinction matters: a crash proof establishes detection of
    the removal but is fragile to any defensive respelling of the adjacent
    code, so the record must not present the two as the same strength.
    """
    proc = subprocess.run([python, SUITE_REL], cwd=tree_path, capture_output=True, text=True)
    passed = proc.returncode == 0 and "passed" in proc.stdout
    first = next(
        (l.strip().removeprefix("- ") for l in proc.stdout.splitlines() if l.startswith("- ")),
        "",
    )
    attributed = bool(first)
    if not passed and not first:
        first = (proc.stderr.strip().splitlines() or ["checker crashed"])[-1][:200]
    return passed, first, attributed


def measure(python: str) -> dict[str, Any]:
    source = CHECKER.read_text()
    tree = ast.parse(source)
    units_by_function, not_audited = discover_conditions(source)

    with tempfile.TemporaryDirectory(prefix="odeya-condition-audit-") as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(
            ROOT, work, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules")
        )
        target = work / SUITE_REL

        # Control on the re-serialized baseline: pass/fail must be a property
        # of the removed condition, never of serialization itself.
        baseline = ast.unparse(deepcopy(tree))
        target.write_text(baseline)
        passed, _, _ = run_suite(work, python)
        if not passed:
            raise SystemExit(
                "control failed: the unmutated re-serialized copy must pass or the audit is meaningless"
            )

        results = []
        for name in (*AUDITED_MODELS, *AUDITED_HELPERS, *AUDITED_VALUE_HELPERS):
            conditions = []
            for unit in units_by_function[name]:
                target.write_text(mutated_source(tree, unit))
                suite_passed, first, attributed = run_suite(work, python)
                conditions.append(
                    {
                        "guard": unit["guard"],
                        "role": unit["role"],
                        "condition": unit["condition"],
                        "proved": not suite_passed,
                        "proved_by": first.split(":")[0] if not suite_passed else None,
                        "detection": (
                            ("case_attributed" if attributed else "crash")
                            if not suite_passed
                            else None
                        ),
                    }
                )
            target.write_text(baseline)
            results.append(
                {
                    "function": name,
                    "condition_count": len(conditions),
                    "proved_count": sum(1 for c in conditions if c["proved"]),
                    "conditions": conditions,
                }
            )

    total = sum(m["condition_count"] for m in results)
    proved = sum(m["proved_count"] for m in results)
    return {
        "schema_version": "0.1.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.lifecycle-condition-coverage",
        "version": "0.1.0",
        "status": "candidate_measurement_not_admitted",
        "method": (
            "each top-level member of a guarded boolean chain in a declared "
            "lifecycle model or helper predicate is removed one at a time in an "
            "isolated copy; a condition is proved only when the suite fails "
            "without it"
        ),
        "subject": SUITE_REL,
        "subject_sha256": sha256_file(CHECKER),
        "models": results,
        "not_audited": not_audited,
        "summary": {
            "condition_count": total,
            "proved": proved,
            "unproved": total - proved,
            "crash_detected": sum(
                1
                for model in results
                for condition in model["conditions"]
                if condition.get("detection") == "crash"
            ),
        },
        "boundary": (
            "condition-level architecture evidence about retained bytes only; "
            "single-condition tests and nested boolean groups are counted, not "
            "audited; structural comparisons are one condition regardless of "
            "field count; not a runtime, an admitted member, an independently "
            "reproduced verdict, or Gate A acceptance"
        ),
    }


def report(document: dict[str, Any]) -> None:
    for model in document["models"]:
        print(f"{model['function']}: {model['proved_count']}/{model['condition_count']}")
        for condition in model["conditions"]:
            if not condition["proved"]:
                print(
                    f"    NO EVIDENCE  [{condition['role']}] {condition['condition'][:70]}"
                    f"  in guard: {condition['guard'][:60]}"
                )
    summary = document["summary"]
    print(
        f"\n{summary['proved']}/{summary['condition_count']} conditions proved "
        f"({summary['crash_detected']} by crash, which is fragile detection, not "
        f"case-attributed evidence); {summary['unproved']} removable with the suite green"
    )
    not_audited = document["not_audited"]
    print(
        f"counted, not audited here: {not_audited['single_condition_tests']} single-condition "
        f"tests (statement audit + safe references), {not_audited['nested_boolean_groups']} "
        "nested boolean groups (exercised only as wholes)"
    )


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
            print("\ncondition-coverage record is absent", file=sys.stderr)
            return 1
        if RECORD.read_text() != serialized:
            print(
                "\ncondition-coverage record does not reproduce from the current checker bytes",
                file=sys.stderr,
            )
            return 1
        print("\ncondition-coverage record reproduces exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
