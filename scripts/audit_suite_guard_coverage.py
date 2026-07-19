#!/usr/bin/env python3
"""Measure, by mutation, which guards fire in every refusal-bearing suite.

ADR 0025 established that a guard without a known-bad proof has no
evidence, and ADRs 0026-0077 drove one suite to near-complete statement
and condition coverage. ADR 0078 then measured what that habit had never
been pointed at: of 717 refusal statements across thirteen suites, 169
were proved and **548 had never been measured at all**. Every one of
those sits in the state lifecycle-closure occupied before it was audited
— deletable with its suite green, and nothing noticing.

This tool generalizes `audit_lifecycle_guard_coverage.py` to any suite.
Each refusal construct is disabled one at a time in an isolated copy of
the tree and that suite is re-run; a guard is proved only when disabling
it makes the suite fail.

The mutation replaces only the refusal itself, leaving surrounding statements
intact. Suite-declared bindings to the checker bytes are refreshed inside the
isolated copy before execution; otherwise the changed checker digest would make
every removal look detected. A startup self-test proves that this normalization
is necessary and sufficient for the current self-binding suite. A proved
verdict still establishes only that the suite failed after the isolated
removal; masking and discovery limitations remain possible.

What a proved verdict does NOT mean, carried forward from ADR 0030: this
is statement reachability, not condition coverage, and never correctness.
A guard shown to fire is exercised, not shown to enforce the right rule.

Detection kind is recorded per guard (ADR 0065): a suite that crashes
after a removal has detected it, but fragilely — the proof rests on
adjacent code rather than on a retained case.

Suites run in parallel because their costs differ by two orders of
magnitude; the slowest dominates wall time rather than the sum.

Usage:
    python3 scripts/audit_suite_guard_coverage.py            # measure and report
    python3 scripts/audit_suite_guard_coverage.py --write    # retain the record
    python3 scripts/audit_suite_guard_coverage.py --check    # fail on drift

This is architecture evidence about retained bytes. It is not a runtime,
an admitted member, an independently reproduced verdict, or Gate A
acceptance.
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/suite-guard-coverage.json"

# lifecycle-closure is deliberately absent: it carries its own dedicated
# statement and condition audits, and duplicating it here would report the
# same guards under two records that could silently disagree.
AUDITED_SUITES = (
    "architecture-review",
    "canonical-profile-candidate",
    "challenge-frame",
    "cognitive-contracts",
    "command-identity-contracts",
    "constitutional-construction",
    "first-slice-resolution",
    "human-decision-assurance",
    "mathematical-contracts",
    "physical-contracts",
    "projection-contracts",
    "work-identity-successor-cohort",
    "work-intent-identity-candidate",
    "work-intent-reference-resolution",
)
REFUSAL_NAMES = {"errors", "failures"}


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


def discover(source: str) -> list[dict[str, Any]]:
    """Every construct that can put a refusal into a suite's report.

    Discovery is the weak point of this method, not mutation: a guard
    expressed through a construct not matched here is invisible, and this
    repository has found such a denominator wrong four times. Extend this
    before adding a new refusal construct.
    """
    tree = ast.parse(source)
    found: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        guard: str | None = None
        replacement: str | None = None
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"append", "extend"}
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in REFUSAL_NAMES
            and node.args
        ):
            guard = message_template_from(node.args[0])
            replacement = "pass"
        elif (
            isinstance(node, ast.AugAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id in REFUSAL_NAMES
        ):
            guard = f"{node.target.id} += {ast.unparse(node.value)}"
            replacement = "pass"
        elif isinstance(node, ast.Return) and isinstance(node.value, ast.List) and node.value.elts:
            elements = node.value.elts
            guard = (
                message_template_from(elements[0])
                if len(elements) == 1
                else ast.unparse(node.value)
            )
            replacement = "return []"
        if guard is not None and replacement is not None:
            found.append(
                {
                    "guard": guard,
                    "lineno": node.lineno,
                    "end_lineno": node.end_lineno,
                    "replacement": replacement,
                }
            )
    found.sort(key=lambda item: (item["lineno"], item["end_lineno"]))
    return found


def run_suite(tree: Path, relative: str, python: str) -> tuple[bool, bool]:
    """(passed, failure was suite-reported rather than a crash).

    Suites report their refusals on stderr as often as stdout; the first
    version of this tool inspected stdout alone and therefore classified
    every genuine detection as a crash. A crash is identified by the
    interpreter's own traceback, not by which stream carried the message.
    """
    proc = subprocess.run(
        [python, relative], cwd=tree, capture_output=True, text=True, timeout=900
    )
    passed = proc.returncode == 0
    output = proc.stdout + proc.stderr
    reported = (not passed) and "Traceback (most recent call last)" not in output
    return passed, reported


def refresh_declared_subject_binding(tree: Path, relative: str) -> None:
    """Keep an isolated mutation from failing on its own checker digest.

    HumanDecisionAssurance deliberately binds its checker bytes in candidate
    evidence. A guard-ablation copy must update only that binding after changing
    the checker; otherwise every mutation fails at the outer byte-binding gate
    and is falsely counted as evidence that the removed guard was exercised.
    The canonical tree and retained evidence are never changed.
    """
    if relative != "tests/human-decision-assurance/check.py":
        return
    evidence_path = (
        tree / "architecture/human-decision-assurance-candidate-evidence.json"
    )
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    bindings = evidence.get("ordered_artifact_bindings", [])
    matches = [
        binding
        for binding in bindings
        if binding.get("path") == relative
        and binding.get("role") == "semantic_checker"
    ]
    if len(matches) != 1:
        raise ValueError(
            "HumanDecisionAssurance candidate evidence must bind exactly one "
            "semantic checker"
        )
    raw = (tree / relative).read_bytes()
    matches[0]["raw_sha256"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    matches[0]["byte_count"] = len(raw)
    evidence_path.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def subject_binding_refresh_self_test(python: str) -> bool:
    """Prove the audit isolates semantic mutation from declared byte binding."""
    relative = "tests/human-decision-assurance/check.py"
    with tempfile.TemporaryDirectory(prefix="odeya-guard-binding-self-test-") as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(
            ROOT,
            work,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "node_modules",
                ".venv-architecture",
                "artifacts",
            ),
        )
        control_passed, _ = run_suite(work, relative, python)
        if not control_passed:
            return False
        target = work / relative
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\n# guard-audit subject-binding self-test\n",
            encoding="utf-8",
        )
        unrefreshed_passed, _ = run_suite(work, relative, python)
        refresh_declared_subject_binding(work, relative)
        refreshed_passed, _ = run_suite(work, relative, python)
        return not unrefreshed_passed and refreshed_passed


def audit_suite(suite: str, python: str) -> dict[str, Any]:
    relative = f"tests/{suite}/check.py"
    checker = ROOT / relative
    source = checker.read_text()
    lines = source.splitlines(keepends=True)
    guards = discover(source)

    with tempfile.TemporaryDirectory(prefix=f"odeya-{suite}-audit-") as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(
            # .git is copied deliberately: two suites resolve predecessor
            # schemas against their ledgered commits rather than live files,
            # and excluding history made their unmutated controls fail.
            ROOT, work, ignore=shutil.ignore_patterns("__pycache__", "node_modules",
                                                      ".venv-architecture", "artifacts")
        )
        target = work / relative
        passed, _ = run_suite(work, relative, python)
        if not passed:
            return {
                "suite": suite,
                "guard_count": len(guards),
                "proved_count": 0,
                "control": "failed",
                "guards": [],
            }

        results = []
        for guard in guards:
            indent = len(lines[guard["lineno"] - 1]) - len(lines[guard["lineno"] - 1].lstrip())
            mutated = lines[:]
            mutated[guard["lineno"] - 1 : guard["end_lineno"]] = [
                " " * indent + guard["replacement"] + "\n"
            ]
            target.write_text("".join(mutated))
            refresh_declared_subject_binding(work, relative)
            suite_passed, reported = run_suite(work, relative, python)
            target.write_text(source)
            results.append(
                {
                    "guard": guard["guard"][:160],
                    "proved": not suite_passed,
                    "detection": ("case_attributed" if reported else "crash")
                    if not suite_passed
                    else None,
                }
            )

    return {
        "suite": suite,
        "subject": relative,
        "subject_sha256": sha256_file(checker),
        "guard_count": len(results),
        "proved_count": sum(1 for r in results if r["proved"]),
        "control": "passed",
        "guards": results,
    }


def measure(python: str) -> dict[str, Any]:
    with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(audit_suite, suite, python): suite for suite in AUDITED_SUITES}
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    results.sort(key=lambda item: item["suite"])

    total = sum(item["guard_count"] for item in results)
    proved = sum(item["proved_count"] for item in results)
    crashes = sum(
        1 for item in results for guard in item["guards"] if guard.get("detection") == "crash"
    )
    return {
        "schema_version": "0.1.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.suite-guard-coverage",
        "version": "0.1.0",
        "status": "candidate_measurement_not_admitted",
        "method": (
            "each refusal construct of a declared suite is disabled one at a time "
            "in an isolated copy of the tree, any suite-declared checker-byte "
            "binding is refreshed only inside that copy, and that suite is re-run; "
            "a guard is proved only when disabling it makes the suite fail after "
            "that isolation"
        ),
        "suites": results,
        "summary": {
            "guard_count": total,
            "proved": proved,
            "unproved": total - proved,
            "crash_detected": crashes,
        },
        "boundary": (
            "statement reachability across the suites lifecycle-closure's dedicated "
            "audits do not cover; not condition coverage, not correctness, not an "
            "independently reproduced verdict, and not Gate A acceptance"
        ),
    }


def report(document: dict[str, Any]) -> None:
    for suite in document["suites"]:
        marker = "" if suite["control"] == "passed" else "  [CONTROL FAILED]"
        print(f"{suite['suite']}: {suite['proved_count']}/{suite['guard_count']}{marker}")
    summary = document["summary"]
    print(
        f"\n{summary['proved']}/{summary['guard_count']} guards proved "
        f"({summary['crash_detected']} by crash); {summary['unproved']} with no known-bad proof"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    # The interpreter must be an absolute path: each suite runs inside a copy
    # of the tree that deliberately excludes .venv-architecture, so a relative
    # interpreter resolves to nothing there. The rehearsal passes exactly such
    # a relative path, which is how this was found -- by the rehearsal failing,
    # not by the local runs that had always used an absolute one.
    python = str(Path(args.python).resolve()) if Path(args.python).exists() else args.python
    if not subject_binding_refresh_self_test(python):
        print(
            "subject-binding refresh self-test failed: the guard audit cannot "
            "separate a checker mutation from its declared raw-byte binding",
            file=sys.stderr,
        )
        return 1
    document = measure(python)
    report(document)
    serialized = json.dumps(document, indent=2, ensure_ascii=False) + "\n"

    if any(suite["control"] != "passed" for suite in document["suites"]):
        print("\na suite whose unmutated control fails cannot be audited", file=sys.stderr)
        return 1
    if args.write:
        RECORD.write_text(serialized)
        print(f"\nretained {RECORD.relative_to(ROOT)}")
        return 0
    if args.check:
        if not RECORD.exists():
            print("\nsuite guard-coverage record is absent", file=sys.stderr)
            return 1
        if RECORD.read_text() != serialized:
            print("\nsuite guard-coverage record does not reproduce", file=sys.stderr)
            return 1
        print("\nsuite guard-coverage record reproduces exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
