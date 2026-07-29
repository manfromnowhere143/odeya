#!/usr/bin/env python3
"""Measure which guards fire in the declared generalized-audit suite census.

ADR 0025 established that an unexercised guard has no retained reachability
evidence, and ADRs 0026-0077 drove one suite to near-complete statement
and condition coverage. ADR 0078 then measured what that habit had never
been pointed at: of 717 refusal statements across thirteen suites, 169
were proved and **548 had never been measured at all**. Every one of
those sits in the state lifecycle-closure occupied before it was audited
— deletable with its suite green, and nothing noticing.

This tool generalizes `audit_lifecycle_guard_coverage.py` to any suite.
Each refusal construct is disabled one at a time in an isolated copy of
the tree. ADR 0104 requires a syntax-valid mutation to produce the same
nonempty exit-one/no-traceback framed refusal fingerprint on both sides of
a passing restored-control run before this generalized record calls the
guard proved. The retained proved row binds that fingerprint.

The mutation replaces only the refusal itself, leaving surrounding statements
intact. Suite-declared bindings to the checker bytes are refreshed inside the
isolated copy before execution; otherwise the changed checker digest would make
every removal look detected. A startup self-test proves that this normalization
is necessary and sufficient for the current self-binding suite. A proved
verdict still establishes only that the checker reported a stable refusal
around one recovery control after the isolated removal; exact case attribution,
masking, and discovery limitations remain open.

What a proved verdict does NOT mean, carried forward from ADR 0030: this
is statement reachability, not condition coverage, and never correctness.
A guard shown to fire is exercised, not shown to enforce the right rule.

Detection kind is recorded per guard. ADR 0104 corrects ADRs 0065 and 0079
for this generalized v0.2 record: empty output, a traceback, any exit other
than one, a signal, a failed recovery control, or an unstable repeat is
retained as crash-only and never credited as proof. Dedicated lifecycle
records retain their separately scoped historical semantics.

Suites run in a bounded parallel pool because their costs differ by two
orders of magnitude; the ABA confirmation reduces, but does not claim to
eliminate, non-traceback infrastructure masking. The predecessor profile
checker is quarantined to a serial phase because it invokes the successor
checker under a timeout and must not compete with that checker's own audit.

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
MAX_WORKERS = 4
SERIAL_SUITES = ("product-identity-profile-candidate",)

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
    "product-identity-profile-candidate",
    "product-identity-profile-0.3-candidate",
    "projection-contracts",
    "prq-002-identity-cohort",
    "work-identity-successor-cohort",
    "work-intent-identity-candidate",
    "work-intent-reference-resolution",
)
REFUSAL_NAMES = {"errors", "failures"}


def schedule_contract_errors(
    max_workers: object,
    audited_suites: tuple[str, ...],
    parallel_suites: tuple[str, ...],
    serial_suites: tuple[str, ...],
) -> list[str]:
    """Close the concurrency partition that prevents nested-checker masking."""

    errors: list[str] = []
    if type(max_workers) is not int or max_workers != 4:
        errors.append("parallel worker count must be the exact integer 4")
    if serial_suites != ("product-identity-profile-candidate",):
        errors.append("serial suite inventory must remain exact and ordered")
    if len(audited_suites) != len(set(audited_suites)):
        errors.append("audited suite inventory must be unique")
    if len(serial_suites) != len(set(serial_suites)):
        errors.append("serial suite inventory must be unique")
    if not set(serial_suites).issubset(audited_suites):
        errors.append("serial suite inventory must be a subset of audited suites")
    expected_parallel = tuple(
        suite for suite in audited_suites if suite not in serial_suites
    )
    if parallel_suites != expected_parallel:
        errors.append("parallel suite inventory must be the exact ordered complement")
    if len(parallel_suites) != len(set(parallel_suites)):
        errors.append("parallel suite inventory must be unique")
    if set(parallel_suites) & set(serial_suites):
        errors.append("parallel and serial suite partitions must be disjoint")
    if set(parallel_suites) | set(serial_suites) != set(audited_suites):
        errors.append("parallel and serial suites must cover the audited inventory")
    return errors


def parallel_suite_partition(
    audited_suites: tuple[str, ...], serial_suites: tuple[str, ...]
) -> tuple[str, ...]:
    return tuple(
        suite for suite in audited_suites if suite not in serial_suites
    )


def schedule_contract_self_test() -> bool:
    """Prove the exact safe schedule and reject each causal weakening."""

    parallel = parallel_suite_partition(AUDITED_SUITES, SERIAL_SUITES)
    safe = schedule_contract_errors(
        MAX_WORKERS, AUDITED_SUITES, parallel, SERIAL_SUITES
    )
    known_bad = (
        (6, AUDITED_SUITES, parallel, SERIAL_SUITES),
        (True, AUDITED_SUITES, parallel, SERIAL_SUITES),
        (MAX_WORKERS, AUDITED_SUITES, parallel, ()),
        (MAX_WORKERS, AUDITED_SUITES, parallel, ("architecture-review",)),
        (
            MAX_WORKERS,
            AUDITED_SUITES,
            parallel,
            ("product-identity-profile-candidate",) * 2,
        ),
        (
            MAX_WORKERS,
            AUDITED_SUITES,
            parallel,
            ("product-identity-profile-candidate", "not-a-declared-suite"),
        ),
        (
            MAX_WORKERS,
            AUDITED_SUITES + (AUDITED_SUITES[0],),
            parallel,
            SERIAL_SUITES,
        ),
        (MAX_WORKERS, AUDITED_SUITES, parallel[:-1], SERIAL_SUITES),
        (
            MAX_WORKERS,
            AUDITED_SUITES,
            parallel + SERIAL_SUITES,
            SERIAL_SUITES,
        ),
        (
            MAX_WORKERS,
            AUDITED_SUITES,
            parallel + (parallel[0],),
            SERIAL_SUITES,
        ),
    )
    return not safe and all(
        bool(schedule_contract_errors(*case)) for case in known_bad
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
        elif (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "add"
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "findings"
            and node.value.args
        ):
            guard = message_template_from(node.value.args[0])
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


def detector_self_test() -> bool:
    """Prove the narrow findings.add expression detector and its exclusion."""
    source = """
def check(findings, unrelated, consume):
    findings.add("expected_finding", "detail")
    unrelated.add("unrelated_add", "detail")
    consume(findings.add("nested_findings_add", "detail"))
"""
    guards = discover(source)
    return (
        len(guards) == 1
        and guards[0]["guard"] == "expected_finding"
        and guards[0]["replacement"] == "pass"
    )


def suite_reported_refusal(returncode: int, output: str) -> bool:
    """Recognize a suite-declared refusal, never an infrastructure death."""

    return (
        returncode == 1
        and bool(output.strip())
        and "Traceback (most recent call last)" not in output
    )


def suite_reported_refusal_self_test() -> bool:
    return (
        suite_reported_refusal(1, "declared refusal\n")
        and not suite_reported_refusal(0, "PASS\n")
        and not suite_reported_refusal(1, "")
        and not suite_reported_refusal(
            1, "Traceback (most recent call last):\n"
        )
        and not suite_reported_refusal(2, "usage or infrastructure error\n")
        and not suite_reported_refusal(-9, "")
    )


def refusal_fingerprint(returncode: int, stdout: str, stderr: str) -> str:
    """Bind the exact return code and separate output streams without ambiguity."""

    framed = json.dumps(
        {
            "returncode": returncode,
            "stderr": stderr,
            "stdout": stdout,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(framed).hexdigest()


def refusal_fingerprint_self_test() -> bool:
    """Prove that stream-boundary drift changes the retained fingerprint."""

    return (
        refusal_fingerprint(1, "ab", "c") != refusal_fingerprint(1, "a", "bc")
        and refusal_fingerprint(1, "ab", "c") != refusal_fingerprint(2, "ab", "c")
        and refusal_fingerprint(1, "ab", "c")
        == refusal_fingerprint(1, "ab", "c")
    )


SuiteObservation = tuple[bool, bool, str]


def stable_refusal(
    first: SuiteObservation,
    recovery: SuiteObservation,
    repeat: SuiteObservation,
) -> bool:
    """Admit only an ABA-stable suite-reported refusal."""

    return (
        not first[0]
        and first[1]
        and recovery[0]
        and not repeat[0]
        and repeat[1]
        and repeat[2] == first[2]
    )


def stable_refusal_self_test() -> bool:
    """Prove the ABA predicate accepts its safe control and rejects each break."""

    fingerprint = "sha256:" + "a" * 64
    changed = "sha256:" + "b" * 64
    safe = (
        (False, True, fingerprint),
        (True, False, changed),
        (False, True, fingerprint),
    )
    known_bad = (
        ((True, False, changed), safe[1], safe[2]),
        ((False, False, fingerprint), safe[1], safe[2]),
        (safe[0], (False, True, changed), safe[2]),
        (safe[0], safe[1], (True, False, changed)),
        (safe[0], safe[1], (False, False, fingerprint)),
        (safe[0], safe[1], (False, True, changed)),
    )
    return stable_refusal(*safe) and all(
        not stable_refusal(*case) for case in known_bad
    )


def mutation_compiles(source: str, label: str) -> bool:
    """Refuse to execute a syntactically invalid guard mutation."""

    try:
        compile(source, label, "exec")
    except SyntaxError:
        return False
    return True


def mutation_compile_self_test() -> bool:
    return mutation_compiles("value = 1\n", "valid.py") and not mutation_compiles(
        "if True\n    value = 1\n", "invalid.py"
    )


def run_suite(
    tree: Path, relative: str, python: str
) -> SuiteObservation:
    """Return pass/refusal classification and an exact output fingerprint.

    Suites report their refusals on stderr as often as stdout; the first
    version of this tool inspected stdout alone and therefore classified
    every genuine detection as a crash. A declared refusal requires nonempty
    output, exit one, and no interpreter traceback; every other failure mode
    is crash-only.
    """
    proc = subprocess.run(
        [python, relative], cwd=tree, capture_output=True, text=True, timeout=900
    )
    passed = proc.returncode == 0
    output = proc.stdout + proc.stderr
    # This bounded classifier is not exact case attribution. A later record
    # version needs suite-specific machine-readable refusal envelopes to
    # exclude every non-traceback startup-failure mask.
    reported = suite_reported_refusal(proc.returncode, output)
    fingerprint = refusal_fingerprint(proc.returncode, proc.stdout, proc.stderr)
    return passed, reported, fingerprint


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
        control_passed, _, _ = run_suite(work, relative, python)
        if not control_passed:
            return False
        target = work / relative
        target.write_text(
            target.read_text(encoding="utf-8")
            + "\n# guard-audit subject-binding self-test\n",
            encoding="utf-8",
        )
        unrefreshed_passed, _, _ = run_suite(work, relative, python)
        refresh_declared_subject_binding(work, relative)
        refreshed_passed, _, _ = run_suite(work, relative, python)
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
        passed, _, _ = run_suite(work, relative, python)
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
            mutated_source = "".join(mutated)
            if not mutation_compiles(mutated_source, relative):
                results.append(
                    {
                        "guard": guard["guard"][:160],
                        "proved": False,
                        "detection": "crash",
                        "refusal_fingerprint": None,
                    }
                )
                continue
            target.write_text(mutated_source)
            refresh_declared_subject_binding(work, relative)
            first = run_suite(work, relative, python)
            suite_passed, reported, fingerprint = first
            target.write_text(source)
            detected = not suite_passed
            confirmed = False
            retained_fingerprint = None
            if detected and reported:
                refresh_declared_subject_binding(work, relative)
                recovery = run_suite(work, relative, python)
                if recovery[0]:
                    target.write_text(mutated_source)
                    refresh_declared_subject_binding(work, relative)
                    repeat = run_suite(work, relative, python)
                    confirmed = stable_refusal(first, recovery, repeat)
                    retained_fingerprint = fingerprint if confirmed else None
                    target.write_text(source)
            refresh_declared_subject_binding(work, relative)
            results.append(
                {
                    "guard": guard["guard"][:160],
                    "proved": confirmed,
                    "detection": (
                        "suite_reported_refusal" if confirmed else "crash"
                    )
                    if detected
                    else None,
                    "refusal_fingerprint": retained_fingerprint,
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
    parallel_suites = parallel_suite_partition(AUDITED_SUITES, SERIAL_SUITES)
    schedule_errors = schedule_contract_errors(
        MAX_WORKERS, AUDITED_SUITES, parallel_suites, SERIAL_SUITES
    )
    if schedule_errors:
        raise ValueError("; ".join(schedule_errors))
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(audit_suite, suite, python): suite
            for suite in parallel_suites
        }
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    results.extend(audit_suite(suite, python) for suite in SERIAL_SUITES)
    results.sort(key=lambda item: item["suite"])

    total = sum(item["guard_count"] for item in results)
    proved = sum(item["proved_count"] for item in results)
    crashes = sum(
        1 for item in results for guard in item["guards"] if guard.get("detection") == "crash"
    )
    return {
        "schema_version": "0.2.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.suite-guard-coverage",
        "version": "0.2.0",
        "status": "candidate_measurement_not_admitted",
        "execution_schedule": {
            "parallel_max_workers": MAX_WORKERS,
            "serial_suites": list(SERIAL_SUITES),
            "serial_after_parallel": True,
        },
        "method": (
            "each refusal construct of a declared suite is disabled one at a time "
            "in an isolated copy of the tree, any suite-declared checker-byte "
            "binding is refreshed only inside that copy, syntax-invalid mutations "
            "are refused before execution, and that suite is re-run; a guard is "
            "proved only when the syntax-valid mutation emits nonempty output, "
            "exits one without an interpreter traceback, the restored unmodified "
            "control then passes, and the identical mutation repeats the same "
            "SHA-256 fingerprint over an exact framed return-code/stdout/stderr "
            "object; that fingerprint is retained in the proved row; empty "
            "output, tracebacks, other exit codes, signals, failed recovery "
            "controls, and unstable repeats are crash-only detections retained "
            "as unproved; the predecessor profile checker runs after the bounded "
            "parallel pool so its nested successor check cannot compete with the "
            "successor audit"
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
            "exact case-ID attribution protocol, not exclusion of every "
            "non-traceback startup-failure mask, not hostile-concurrent-writer "
            "resistance or a process sandbox, not an independently reproduced "
            "verdict, and not Gate A acceptance"
        ),
    }


def report(document: dict[str, Any]) -> None:
    for suite in document["suites"]:
        marker = "" if suite["control"] == "passed" else "  [CONTROL FAILED]"
        print(f"{suite['suite']}: {suite['proved_count']}/{suite['guard_count']}{marker}")
    summary = document["summary"]
    print(
        f"\n{summary['proved']}/{summary['guard_count']} guards proved; "
        f"{summary['crash_detected']} crash-only detections retained within "
        f"{summary['unproved']} unproved guards"
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
    parallel_suites = parallel_suite_partition(AUDITED_SUITES, SERIAL_SUITES)
    schedule_errors = schedule_contract_errors(
        MAX_WORKERS, AUDITED_SUITES, parallel_suites, SERIAL_SUITES
    )
    if schedule_errors or not schedule_contract_self_test():
        detail = "; ".join(schedule_errors) if schedule_errors else "known-bad accepted"
        print(
            "execution-schedule self-test failed: " + detail,
            file=sys.stderr,
        )
        return 1
    if not detector_self_test():
        print(
            "refusal-detector self-test failed: findings.add expression discovery "
            "or unrelated .add exclusion is incorrect",
            file=sys.stderr,
        )
        return 1
    if not suite_reported_refusal_self_test():
        print(
            "suite-refusal classifier self-test failed: exit, empty-output, "
            "traceback, or signal handling is unsafe",
            file=sys.stderr,
        )
        return 1
    if not refusal_fingerprint_self_test():
        print(
            "refusal-fingerprint self-test failed: return code or stdout/stderr "
            "framing is ambiguous",
            file=sys.stderr,
        )
        return 1
    if not stable_refusal_self_test():
        print(
            "stable-refusal self-test failed: the ABA proof rule accepted a "
            "known-bad sequence or rejected its safe control",
            file=sys.stderr,
        )
        return 1
    if not mutation_compile_self_test():
        print(
            "mutation-compile self-test failed: syntax-invalid guard mutations "
            "could enter execution",
            file=sys.stderr,
        )
        return 1
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
