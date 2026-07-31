#!/usr/bin/env python3
"""Bind suite-guard evidence and its four governed current narratives.
Comments/fences are excluded; coverage is not correctness or Gate A; exact
rehearsal, not this cheap gate, recomputes the record through the audit tool.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/suite-guard-coverage.json"
AUDIT = ROOT / "scripts/audit_suite_guard_coverage.py"
VALIDATOR = ROOT / "scripts/validate.py"
# Derived from the retained v0.2 authoring measurement, never preregistered.
PIN: dict[str, int] | None = {
    "guard_count": 1260,
    "proved": 501,
    "unproved": 759,
    "crash_detected": 0,
}
EXCLUDED = {"lifecycle-closure": "dedicated 222/229 statement and 108/111 condition audits"}
RECORD_KEYS = {
    "schema_version",
    "artifact_class",
    "inventory_id",
    "version",
    "status",
    "execution_schedule",
    "method",
    "suites",
    "summary",
    "boundary",
}
SUITE_KEYS = {
    "suite",
    "subject",
    "subject_sha256",
    "guard_count",
    "proved_count",
    "control",
    "guards",
}
GUARD_KEYS = {"guard", "proved", "detection", "refusal_fingerprint"}
SUMMARY_KEYS = {"guard_count", "proved", "unproved", "crash_detected"}
SCHEDULE_KEYS = {
    "parallel_max_workers",
    "serial_suites",
    "serial_after_parallel",
}
RECORD_METHOD = (
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
)
RECORD_BOUNDARY = (
    "statement reachability across the suites lifecycle-closure's dedicated "
    "audits do not cover; not condition coverage, not correctness, not an "
    "exact case-ID attribution protocol, not exclusion of every "
    "non-traceback startup-failure mask, not hostile-concurrent-writer "
    "resistance or a process sandbox, not an independently reproduced "
    "verdict, and not Gate A acceptance"
)
# SHA-256 binds normalized, comment/fence-cleaned current units: README's whole
# checkpoint, status/handoff row/bullet plus sections, and all current plan units.
# Numeric truth remains derived from RECORD; contradictory sibling prose cannot pass.
UNIT_SHA256 = {
    "readme.current-section": "51600ff28dda4e93c68c6b67a8a442f8de66dbba663baada450c52e79917fef9",
    "status.current-section": "37909eac05b20eb8f505029489792affab7d839d6484b46f440105c266f9b641",
    "status.guard-row": "9460c3e0541fde57fd350de923c76f40fe11bae99c5f1e82970e33c5f9a690fe",
    "handoff.current-section": "6feec9438ab393ff26f630b5ec4622608d321e8bd5666f6d3ce1ec84e4c39c7c",
    "handoff.guard-bullet": "9156fb3a41a695caac94eae7d4533a7de8def1abe56d131bcb6870047b39b70d",
    "plan.current-units": "732edac76e3f2ef88a484712470a806541ca551851dcaee1cb36994f666ac24a",
}
WORDS = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
WORD_VALUE = {word: index for index, word in enumerate(WORDS)}
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
ATX = re.compile(r"(?m)^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*$")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SUITE_NAME = re.compile(r"[a-z0-9]+(?:(?:-|\.)[a-z0-9]+)*\Z")

PATTERNS = {
    "readme": re.compile(
        r"across (?P<suites>\d+) declared isolated checker subjects, "
        r"(?P<proved>\d+) of (?P<total>\d+) refusal statements are proved to fire, "
        r"with (?P<unproved>\d+) retained explicitly as unproved and "
        r"(?P<crash>[a-z0-9-]+) crash-only detections"
    ),
    "status": re.compile(
        r"proves (?P<proved>\d+)/(?P<total>\d+) refusal statements across "
        r"(?P<suites>\d+) declared isolated checker subjects, with "
        r"(?P<unproved>\d+) explicitly unproved and (?P<crash>[a-z0-9-]+) "
        r"crash-only detections; the assurance checker accounts for "
        r"(?P<hda_proved>\d+)/(?P<hda_total>\d+) proved guards"
    ),
    "handoff": re.compile(
        r"record measures (?P<suites>[a-z0-9-]+) declared isolated "
        r"contract-checker subjects at (?P<proved>\d+) of (?P<total>\d+) refusal "
        r"statements proved, with (?P<unproved>\d+) explicitly unproved and "
        r"(?P<crash>[a-z0-9-]+) crash-only detections"
    ),
    "hda": re.compile(
        r"PRQ-013 contributes (?P<hda_proved>\d+)/(?P<hda_total>\d+), leaving "
        r"(?P<hda_unproved>\d+) explicitly unproved"
    ),
    "open": re.compile(r"The (?P<unproved>\d+) open isolated-suite guards are"),
    "plan_status": re.compile(
        r"Status: current roadmap for the (?P<unproved>\d+) unproved refusal statements\."
    ),
    "plan": re.compile(
        r"covers (?P<suites>[a-z0-9-]+) declared isolated contract-checker "
        r"subjects: (?P<proved>\d+) of (?P<total>\d+) refusal statements are "
        r"proved load-bearing by mutation, (?P<unproved>\d+) have no retained "
        r"proof, and (?P<crash>[a-z0-9-]+) crash-only detections are retained "
        r"as unproved"
    ),
}
UNITS = (
    ("README.md", "Architecture checkpoint", "readme"),
    ("docs/ARCHITECTURE_STATUS.md", "Current machine evidence", "status"),
    ("docs/SESSION_HANDOFF.md", "What this lane established, and where to put pressure next", "handoff"),
    ("docs/GUARD_COVERAGE_CLOSURE_PLAN.md", "Exact denominator", "plan"),
)


@dataclass(frozen=True)
class Suite:
    name: str
    proved: int
    total: int

    @property
    def open(self) -> int:
        return self.total - self.proved


@dataclass(frozen=True)
class Facts:
    suites: tuple[Suite, ...]
    proved: int
    total: int
    crash: int

    @property
    def open(self) -> int:
        return self.total - self.proved

    @property
    def hda(self) -> Suite:
        found = [suite for suite in self.suites if suite.name == "human-decision-assurance"]
        if len(found) != 1:
            raise ValueError("record must contain one human-decision-assurance suite")
        return found[0]


def norm(value: str) -> str:
    return " ".join(value.split())


def exact_unit(key: str, value: str, path: str, label: str) -> list[str]:
    observed = hashlib.sha256(norm(value).encode()).hexdigest()
    return [] if observed == UNIT_SHA256[key] else [f"{path}: normalized {label} differs from retained exact current unit"]


def numeric(value: str) -> int | None:
    return int(value) if value.isdigit() else WORD_VALUE.get(value.lower())


def word(value: int) -> str:
    return WORDS[value] if value < len(WORDS) else str(value)


def clean(value: str) -> str:
    output: list[str] = []
    opened: tuple[str, int] | None = None
    for line in value.splitlines(keepends=True):
        if opened is None:
            match = FENCE.match(line)
            if not match:
                output.append(line)
                continue
            token = match.group(1)
            opened = (token[0], len(token))
        elif re.match(
            rf"^ {{0,3}}{re.escape(opened[0])}{{{opened[1]},}}[ \t]*$",
            line.rstrip("\n"),
        ):
            opened = None
        output.append("\n" if line.endswith("\n") else "")
    return COMMENT.sub("", "".join(output))


def scan_headings(value: str) -> list[tuple[int, str, int, int]]:
    found = []
    for match in ATX.finditer(value):
        title = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(2)).strip()
        found.append((len(match.group(1)), title, match.start(), match.end()))
    return found


def section(value: str, path: str, title: str) -> tuple[tuple[str, int, int] | None, list[str]]:
    headings = scan_headings(value)
    matches = [heading for heading in headings if heading[1] == title]
    if len(matches) != 1:
        return None, [
            f"{path}: governed heading {title!r} must occur exactly once; found {len(matches)}"
        ]
    level, _, _, body_start = matches[0]
    if level != 2:
        return None, [
            f"{path}: governed heading {title!r} must be level 2; observed level {level}"
        ]
    later = [heading for heading in headings if heading[2] > matches[0][2] and heading[0] <= 2]
    end = later[0][2] if later else len(value)
    return (value[body_start:end], body_start, end), []


def general(match: re.Match[str]) -> tuple[int | None, int, int, int, int | None]:
    return (
        numeric(match.group("suites")),
        int(match.group("proved")),
        int(match.group("total")),
        int(match.group("unproved")),
        numeric(match.group("crash")),
    )


def expected(facts: Facts) -> tuple[int, int, int, int, int]:
    return len(facts.suites), facts.proved, facts.total, facts.open, facts.crash


def claim(
    scope: str,
    key: str,
    wanted: tuple[Any, ...],
    path: str,
    label: str,
    fields: tuple[str, ...] | None = None,
) -> list[str]:
    matches = list(PATTERNS[key].finditer(norm(scope)))
    if len(matches) != 1:
        return [f"{path}: {label} must occur exactly once; found {len(matches)}"]
    observed = (
        tuple(int(matches[0].group(field)) for field in fields)
        if fields is not None
        else general(matches[0])
    )
    return [] if observed == wanted else [
        f"{path}: {label} must equal {wanted!r}; observed {observed!r}"
    ]


def rows(value: str) -> list[tuple[str, ...]]:
    result = []
    for line in value.splitlines():
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            result.append(tuple(cell.strip() for cell in line[1:-1].split("|")))
    return result


def blocks(value: str) -> list[tuple[int, list[tuple[str, ...]]]]:
    result: list[tuple[int, list[tuple[str, ...]]]] = []
    current: list[tuple[str, ...]] = []
    start = offset = 0
    for line in value.splitlines(keepends=True):
        parsed = rows(line)
        if parsed:
            if not current:
                start = offset
            current += parsed
        elif current:
            result.append((start, current))
            current = []
        offset += len(line)
    if current:
        result.append((start, current))
    return result


def canonical(row: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cell[2:-2].strip() if cell.startswith("**") and cell.endswith("**") else cell for cell in row)


def plan_table(facts: Facts) -> list[tuple[str, ...]]:
    result = [("Generalized subject", "Proved", "Total", "Open"), ("---", "---:", "---:", "---:")]
    result += [
        (suite.name, str(suite.proved), str(suite.total), str(suite.open))
        for suite in facts.suites
    ]
    return result + [("Total", str(facts.proved), str(facts.total), str(facts.open))]


def numbered(value: str) -> dict[int, str]:
    steps: dict[int, list[str]] = {}
    active: int | None = None
    for line in value.splitlines():
        match = re.match(r"^(\d+)\.\s+(.*)$", line)
        if match:
            active = int(match.group(1))
            steps.setdefault(active, []).append(match.group(2))
        elif active is not None and (line.startswith("   ") or not line.strip()):
            steps[active].append(line.strip())
    return {key: norm(" ".join(parts)) for key, parts in steps.items()}


def plan_errors(
    whole: str, governed: tuple[str, int, int], facts: Facts, path: str
) -> list[str]:
    body, body_start, body_end = governed
    errors: list[str] = []
    exact_heading = next(
        heading for heading in scan_headings(whole) if heading[1] == "Exact denominator"
    )
    errors += claim(
        whole[: exact_heading[2]],
        "plan_status",
        (facts.open,),
        path,
        "exact roadmap status",
        ("unproved",),
    )
    errors += claim(body, "plan", expected(facts), path, "Exact denominator guard claim")
    tables = blocks(whole)
    if len(tables) != 1:
        errors.append(f"{path}: plan must contain exactly one contiguous table; found {len(tables)}")
    elif not (body_start <= tables[0][0] < body_end):
        errors.append(f"{path}: coverage table is relocated outside Exact denominator")
    elif [canonical(row) for row in tables[0][1]] != plan_table(facts):
        errors.append(f"{path}: coverage table must equal retained ordered rows and Total")
    governed_sections: dict[str, tuple[str, int, int]] = {}
    for title in ("Proven closure methods", "Order of work", "Boundary"):
        found, found_errors = section(whole, path, title)
        errors += found_errors
        if found is not None:
            governed_sections[title] = found
    if "Order of work" not in governed_sections:
        return errors
    steps = numbered(governed_sections["Order of work"][0])
    if list(steps) != [1, 2, 3, 4, 5]:
        errors.append(f"{path}: Order of work steps must be exactly [1, 2, 3, 4, 5]")
    four = norm(
        f"Treat the {facts.hda.open} unproved human-decision-assurance refusals as "
        "real open evidence work. Prioritize them by consequence, retain exact "
        "one-intent cases only where they prove the intended guard, and do not infer "
        "wrapper coverage from the underlying candidate-evidence evaluator."
    )
    five = norm(
        "Re-run the generalized mutation audit on every checker change; update this "
        "table only from the retained machine record."
    )
    if steps.get(4) != four:
        errors.append(f"{path}: Order of work step 4 must equal the exact HDA obligation")
    if steps.get(5) != five:
        errors.append(f"{path}: Order of work step 5 must equal the record-only update law")
    if errors:
        return errors
    current = [whole[: exact_heading[2]], body]
    current += [governed_sections[title][0] for title in ("Proven closure methods", "Order of work", "Boundary")]
    return exact_unit("plan.current-units", "\n".join(current), path, "current closure-plan surface")


def unit_errors(
    kind: str, whole: str, governed: tuple[str, int, int], facts: Facts, path: str
) -> list[str]:
    body = governed[0]
    if kind == "readme":
        errors = claim(
            body,
            "readme",
            expected(facts),
            path,
            "Architecture checkpoint guard claim",
        )
        return errors or exact_unit(
            "readme.current-section",
            body,
            path,
            "Architecture checkpoint section",
        )
    if kind == "status":
        guard_rows = [row for row in rows(body) if row and row[0] == "Guard evidence"]
        if len(guard_rows) != 1:
            return [f"{path}: Guard evidence row must occur exactly once; found {len(guard_rows)}"]
        wanted = expected(facts) + (facts.hda.proved, facts.hda.total)
        matches = list(PATTERNS["status"].finditer(norm(" ".join(guard_rows[0]))))
        if len(matches) != 1:
            return [f"{path}: Guard evidence claim must occur exactly once; found {len(matches)}"]
        observed = general(matches[0]) + (
            int(matches[0].group("hda_proved")),
            int(matches[0].group("hda_total")),
        )
        if observed != wanted:
            return [
                f"{path}: Guard evidence claim must equal {wanted!r}; observed {observed!r}"
            ]
        errors = exact_unit(
            "status.guard-row",
            " ".join(guard_rows[0]),
            path,
            "Guard evidence row",
        )
        return errors or exact_unit(
            "status.current-section",
            body,
            path,
            "Current machine evidence section",
        )
    if kind == "handoff":
        marker = re.compile(
            r"(?m)^- \*\*Guard coverage has explicit denominators, not "
            r"whole-repository coverage\.\*\*"
        )
        marks = list(marker.finditer(body))
        if len(marks) != 1:
            return [f"{path}: current Guard coverage bullet must occur exactly once; found {len(marks)}"]
        following = re.search(r"(?m)^- ", body[marks[0].end() :])
        end = marks[0].end() + following.start() if following else len(body)
        bullet = body[marks[0].start() : end]
        errors = claim(bullet, "handoff", expected(facts), path, "current Guard coverage claim")
        errors += claim(
            bullet,
            "hda",
            (facts.hda.proved, facts.hda.total, facts.hda.open),
            path,
            "current PRQ-013 subtotal",
            ("hda_proved", "hda_total", "hda_unproved"),
        )
        errors += claim(
            bullet, "open", (facts.open,), path, "current open-guard count", ("unproved",)
        )
        for key, label in (
            ("handoff", "current Guard coverage claim"),
            ("hda", "current PRQ-013 subtotal"),
            ("open", "current open-guard count"),
        ):
            count = len(list(PATTERNS[key].finditer(norm(body))))
            if count != 1:
                errors.append(f"{path}: {label} must be unique in its governed section; found {count}")
        if errors:
            return errors
        errors = exact_unit(
            "handoff.guard-bullet",
            bullet,
            path,
            "current Guard coverage bullet",
        )
        return errors or exact_unit(
            "handoff.current-section",
            body,
            path,
            "current lane section",
        )
    return plan_errors(whole, governed, facts, path)


def truth_errors(facts: Facts, overrides: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    for path, title, kind in UNITS:
        raw = overrides[path] if overrides and path in overrides else (ROOT / path).read_text()
        whole = clean(raw)
        governed, governed_errors = section(whole, path, title)
        errors += governed_errors
        if governed is not None:
            errors += unit_errors(kind, whole, governed, facts, path)
    return errors


def guard_state_error(guard: dict[str, Any]) -> str | None:
    """Admit only the closed v0.2 proof/detection state machine."""

    if set(guard) != GUARD_KEYS:
        return "guard result members must be closed and exact"
    if not isinstance(guard.get("guard"), str) or not guard["guard"]:
        return "guard identity must be a nonempty string"
    proved = guard.get("proved")
    detection = guard.get("detection")
    fingerprint = guard.get("refusal_fingerprint")
    if type(proved) is not bool:
        return "guard proved must be an exact JSON Boolean"
    if detection is not None and type(detection) is not str:
        return "guard detection must be a string or null"
    if fingerprint is not None and type(fingerprint) is not str:
        return "guard refusal_fingerprint must be a string or null"
    proved_fingerprint = (
        type(fingerprint) is str
        and re.fullmatch(r"sha256:[0-9a-f]{64}", fingerprint) is not None
    )
    if (
        proved is True
        and detection == "suite_reported_refusal"
        and proved_fingerprint
    ):
        return None
    if proved is False and detection in {"crash", None} and fingerprint is None:
        return None
    if (proved, detection) not in {
        (True, "suite_reported_refusal"),
        (False, "crash"),
        (False, None),
    }:
        return "guard proved/detection state is outside the closed v0.2 machine"
    return "guard fingerprint is outside the closed v0.2 machine"


def guard_state_self_tests(errors: list[str]) -> int:
    safe = (
        {
            "guard": "g",
            "proved": True,
            "detection": "suite_reported_refusal",
            "refusal_fingerprint": "sha256:" + "a" * 64,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": "crash",
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": None,
            "refusal_fingerprint": None,
        },
    )
    if any(guard_state_error(row) is not None for row in safe):
        errors.append("guard-state safe controls failed")
    known_bad = (
        {
            "guard": "g",
            "proved": True,
            "detection": "crash",
            "refusal_fingerprint": "sha256:" + "a" * 64,
        },
        {
            "guard": "g",
            "proved": True,
            "detection": None,
            "refusal_fingerprint": "sha256:" + "a" * 64,
        },
        {
            "guard": "g",
            "proved": True,
            "detection": "mystery",
            "refusal_fingerprint": "sha256:" + "a" * 64,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": "suite_reported_refusal",
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": "mystery",
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": "false",
            "detection": None,
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": 0,
            "detection": None,
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "detection": None,
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": False,
            "refusal_fingerprint": None,
        },
        {
            "proved": False,
            "detection": None,
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": None,
            "refusal_fingerprint": None,
            "extra": False,
        },
        {
            "guard": "g",
            "proved": True,
            "detection": "suite_reported_refusal",
            "refusal_fingerprint": None,
        },
        {
            "guard": "g",
            "proved": True,
            "detection": "suite_reported_refusal",
            "refusal_fingerprint": "a" * 64,
        },
        {
            "guard": "g",
            "proved": True,
            "detection": "suite_reported_refusal",
            "refusal_fingerprint": "sha256:" + "A" * 64,
        },
        {
            "guard": "g",
            "proved": False,
            "detection": None,
            "refusal_fingerprint": "sha256:" + "a" * 64,
        },
    )
    passed = 0
    for index, row in enumerate(known_bad):
        if guard_state_error(row) is None:
            errors.append(f"guard-state known-bad {index} was accepted")
        else:
            passed += 1
    return passed


def suite_census_errors(
    measured: set[str], declared: set[str]
) -> list[str]:
    """Require the exact registered census outside the one named exclusion."""

    expected = declared - EXCLUDED.keys()
    errors = [
        f"{name}: registered suite is absent from coverage record"
        for name in sorted(expected - measured)
    ]
    errors += [
        f"{name}: undeclared suite is present in coverage record"
        for name in sorted(measured - expected)
    ]
    return errors


def suite_census_self_tests(errors: list[str]) -> int:
    safe_names = (
        "architecture-review",
        "product-identity-profile-0.3-candidate",
        "x",
    )
    if any(SUITE_NAME.fullmatch(name) is None for name in safe_names):
        errors.append("suite-name safe controls failed")
    unsafe_names = (
        "",
        ".",
        "..",
        "../escape",
        "/absolute",
        "a/b",
        "a\\b",
        "Uppercase",
        "double--hyphen",
        "-leading",
        "trailing-",
    )
    passed = 0
    for index, name in enumerate(unsafe_names):
        if SUITE_NAME.fullmatch(name) is not None:
            errors.append(f"suite-name known-bad {index} was accepted")
        else:
            passed += 1
    declared = {"alpha", "beta", "lifecycle-closure"}
    safe = suite_census_errors({"alpha", "beta"}, declared)
    if safe:
        errors.append("suite-census safe control failed: " + " | ".join(safe))
    census_known_bad = (
        (
            {"alpha"},
            ["beta: registered suite is absent from coverage record"],
        ),
        (
            {"alpha", "beta", "gamma"},
            ["gamma: undeclared suite is present in coverage record"],
        ),
        (
            {"alpha", "gamma"},
            [
                "beta: registered suite is absent from coverage record",
                "gamma: undeclared suite is present in coverage record",
            ],
        ),
    )
    for index, (measured, wanted) in enumerate(census_known_bad):
        seen = suite_census_errors(measured, declared)
        if seen != wanted:
            errors.append(
                f"suite-census known-bad {index} expected {wanted!r}; got {seen!r}"
            )
        else:
            passed += 1
    return passed


def schedule_state_error(schedule: object) -> str | None:
    """Admit only the exact schedule that quarantines the nested checker."""

    if not isinstance(schedule, dict) or set(schedule) != SCHEDULE_KEYS:
        return "execution schedule members must be a closed exact object"
    if (
        type(schedule.get("parallel_max_workers")) is not int
        or schedule["parallel_max_workers"] != 4
    ):
        return "execution schedule parallel_max_workers must be the exact integer 4"
    if schedule.get("serial_suites") != [
        "product-identity-profile-candidate"
    ]:
        return "execution schedule serial_suites must remain exact and ordered"
    if schedule.get("serial_after_parallel") is not True:
        return "execution schedule must run the serial phase after the parallel pool"
    return None


def schedule_state_self_tests(errors: list[str]) -> int:
    safe = {
        "parallel_max_workers": 4,
        "serial_suites": ["product-identity-profile-candidate"],
        "serial_after_parallel": True,
    }
    if schedule_state_error(safe) is not None:
        errors.append("execution-schedule safe control failed")
    known_bad = (
        None,
        {},
        {
            "parallel_max_workers": 4,
            "serial_suites": ["product-identity-profile-candidate"],
            "serial_after_parallel": True,
            "extra": False,
        },
        {
            "parallel_max_workers": True,
            "serial_suites": ["product-identity-profile-candidate"],
            "serial_after_parallel": True,
        },
        {
            "parallel_max_workers": 6,
            "serial_suites": ["product-identity-profile-candidate"],
            "serial_after_parallel": True,
        },
        {
            "parallel_max_workers": 4,
            "serial_suites": [],
            "serial_after_parallel": True,
        },
        {
            "parallel_max_workers": 4,
            "serial_suites": ["architecture-review"],
            "serial_after_parallel": True,
        },
        {
            "parallel_max_workers": 4,
            "serial_suites": ["product-identity-profile-candidate"],
            "serial_after_parallel": False,
        },
        {
            "parallel_max_workers": 4,
            "serial_suites": ["product-identity-profile-candidate"],
            "serial_after_parallel": 1,
        },
    )
    passed = 0
    for index, row in enumerate(known_bad):
        if schedule_state_error(row) is None:
            errors.append(f"execution-schedule known-bad {index} was accepted")
        else:
            passed += 1
    return passed


def record_facts(document: dict[str, Any], errors: list[str]) -> Facts | None:
    if set(document) != RECORD_KEYS:
        errors.append("coverage record members must be closed and exact")
    expected_scalars = {
        "schema_version": "0.2.0",
        "artifact_class": "architecture_evidence",
        "inventory_id": "odeya.suite-guard-coverage",
        "version": "0.2.0",
        "status": "candidate_measurement_not_admitted",
        "method": RECORD_METHOD,
        "boundary": RECORD_BOUNDARY,
    }
    for field, value in expected_scalars.items():
        if document.get(field) != value:
            errors.append(f"coverage record {field} must remain exact")
    schedule_error = schedule_state_error(document.get("execution_schedule"))
    if schedule_error is not None:
        errors.append(schedule_error)
    source = document.get("suites")
    if not isinstance(source, list):
        errors.append("coverage record suites must be a list")
        return None
    suites: list[Suite] = []
    names: list[str] = []
    crash = 0
    for item in source:
        if not isinstance(item, dict) or not isinstance(item.get("suite"), str):
            errors.append("coverage record suite identities must be strings")
            continue
        name = item["suite"]
        names.append(name)
        if SUITE_NAME.fullmatch(name) is None:
            errors.append(f"{name!r}: suite identity is not a safe canonical name")
            continue
        if set(item) != SUITE_KEYS:
            errors.append(f"{name}: suite result members must be closed and exact")
        guards = item.get("guards")
        if not isinstance(guards, list) or not all(isinstance(g, dict) for g in guards):
            errors.append(f"{name}: guards must be an object list")
            continue
        proved = sum(guard.get("proved") is True for guard in guards)
        crash += sum(guard.get("detection") == "crash" for guard in guards)
        suites.append(Suite(name, proved, len(guards)))
        if item.get("control") != "passed":
            errors.append(f"{name}: unmutated control did not pass")
        expected_subject = f"tests/{name}/check.py"
        if item.get("subject") != expected_subject:
            errors.append(f"{name}: subject path must equal {expected_subject}")
        subject = ROOT / expected_subject
        actual = "sha256:" + hashlib.sha256(subject.read_bytes()).hexdigest() if subject.is_file() else None
        if actual is None:
            errors.append(f"{name}: subject is absent")
        elif item.get("subject_sha256") != actual:
            errors.append(f"{name}: record does not describe current checker bytes")
        if type(item.get("guard_count")) is not int or item.get("guard_count") != len(guards):
            errors.append(f"{name}: guard_count disagrees with enumeration")
        if type(item.get("proved_count")) is not int or item.get("proved_count") != proved:
            errors.append(f"{name}: proved_count disagrees with enumeration")
        for guard in guards:
            state_error = guard_state_error(guard)
            if state_error is not None:
                errors.append(f"{name}: {state_error}")
    if len(names) != len(set(names)):
        errors.append("coverage record suite identities must be unique")
    if names != sorted(names):
        errors.append("coverage record suite identities must remain sorted")
    declared = set(re.findall(r'"tests/([^/"]+)/check\.py"', VALIDATOR.read_text()))
    measured = set(names)
    errors += suite_census_errors(measured, declared)
    if schedule_error is None and not set(
        document["execution_schedule"]["serial_suites"]
    ).issubset(measured):
        errors.append("execution schedule serial suites must be measured subjects")
    for name, reason in EXCLUDED.items():
        if name in measured:
            errors.append(f"{name}: measured despite exclusion for {reason}")
        elif name not in declared:
            errors.append(f"{name}: stale exclusion for {reason}")
    facts = Facts(tuple(suites), sum(x.proved for x in suites), sum(x.total for x in suites), crash)
    try:
        facts.hda
    except ValueError as exc:
        errors.append(str(exc))
        return None
    calculated = {
        "guard_count": facts.total,
        "proved": facts.proved,
        "unproved": facts.open,
        "crash_detected": facts.crash,
    }
    summary = document.get("summary")
    if not isinstance(summary, dict) or set(summary) != SUMMARY_KEYS:
        errors.append("coverage record summary must be an object")
    else:
        for field, value in calculated.items():
            if type(summary.get(field)) is not int or summary.get(field) != value:
                errors.append(f"summary.{field} must equal enumerated value {value}")
        if PIN is None:
            errors.append(
                "coverage summary pin is unset; populate it from the retained "
                "v0.2 audit before validation"
            )
        else:
            for field, value in PIN.items():
                if summary.get(field) != value:
                    errors.append(
                        f"summary.{field} must retain pinned value {value}"
                    )
    return facts


def swap(value: str, old: str, new: str) -> str:
    return value.replace(old, new, 1) if value.count(old) == 1 else value


def self_tests(facts: Facts, errors: list[str]) -> int:
    kept = {path: (ROOT / path).read_text() for path, _, _ in UNITS}
    safe = truth_errors(facts, kept)
    if safe:
        errors.append("truth-surface safe control failed: " + " | ".join(safe))
    closing = dict(kept)
    titles = {path: [title] for path, title, _ in UNITS}
    titles["docs/GUARD_COVERAGE_CLOSURE_PLAN.md"] += ["Proven closure methods", "Order of work", "Boundary"]
    for path, names in titles.items():
        for name in names:
            closing[path] = swap(closing[path], f"## {name}\n", f"## {name} ##\n")
    alternate = truth_errors(facts, closing)
    if alternate:
        errors.append("closing-ATX safe control failed: " + " | ".join(alternate))

    correct = (
        f"across {len(facts.suites)} declared isolated checker subjects, {facts.proved} "
        f"of {facts.total} refusal statements are proved to fire, with {facts.open} "
        f"retained explicitly as unproved and {word(facts.crash)} crash-only detections"
    )
    stale = correct.replace(f"{facts.proved} of {facts.total}", "458 of 927")
    readme = kept["README.md"]
    plan_path = "docs/GUARD_COVERAGE_CLOSURE_PLAN.md"
    plan = kept[plan_path]
    suite_lines = [f"| {s.name} | {s.proved} | {s.total} | {s.open} |" for s in facts.suites]
    total = f"| **Total** | **{facts.proved}** | **{facts.total}** | **{facts.open}** |"
    cases: list[tuple[str, dict[str, str], str]] = []
    add = cases.append
    stale_observed = (len(facts.suites), 458, 927, facts.open, facts.crash)
    add(("comment", {"README.md": swap(readme, correct, stale + f" <!-- {correct} -->")}, f"README.md: Architecture checkpoint guard claim must equal {expected(facts)!r}; observed {stale_observed!r}"))
    add(("fence", {"README.md": swap(readme, correct, stale + f"\n```text\n{correct}\n```\n")}, f"README.md: Architecture checkpoint guard claim must equal {expected(facts)!r}; observed {stale_observed!r}"))
    add(("stale-plus-correct", {"README.md": swap(readme, "\n## Repository boundary", f"\n{stale}\n\n## Repository boundary")}, "README.md: Architecture checkpoint guard claim must occur exactly once; found 2"))
    add(("nested-heading", {"README.md": swap(readme, "\n## Repository boundary", "\n### Architecture checkpoint ###\n\n## Repository boundary")}, "README.md: governed heading 'Architecture checkpoint' must occur exactly once; found 2"))
    status = "docs/ARCHITECTURE_STATUS.md"
    status_wanted = expected(facts) + (facts.hda.proved, facts.hda.total)
    status_seen = (len(facts.suites), 458, 927, facts.open, facts.crash, facts.hda.proved, facts.hda.total)
    add(("status", {status: kept[status].replace(f"proves {facts.proved}/{facts.total}", "proves 458/927", 1)}, f"{status}: Guard evidence claim must equal {status_wanted!r}; observed {status_seen!r}"))
    handoff = "docs/SESSION_HANDOFF.md"
    old_hda = f"{facts.hda.proved}/{facts.hda.total}, leaving {facts.hda.open}"
    new_hda = f"{facts.hda.proved - 1}/{facts.hda.total}, leaving {facts.hda.open + 1}"
    add(("handoff", {handoff: kept[handoff].replace(old_hda, new_hda, 1)}, f"{handoff}: current PRQ-013 subtotal must equal {(facts.hda.proved, facts.hda.total, facts.hda.open)!r}; observed {(facts.hda.proved - 1, facts.hda.total, facts.hda.open + 1)!r}"))
    add(("plan-date", {plan_path: plan.replace("unproved refusal statements.", "unproved refusal statements measured on 2026-07-20.", 1)}, f"{plan_path}: exact roadmap status must occur exactly once; found 0"))
    add(("split-table", {plan_path: plan.replace(suite_lines[1] + "\n", suite_lines[1] + "\n\n", 1)}, f"{plan_path}: plan must contain exactly one contiguous table; found 2"))
    add(("duplicate-row", {plan_path: plan.replace(suite_lines[2], suite_lines[2] + "\n" + suite_lines[2], 1)}, f"{plan_path}: coverage table must equal retained ordered rows and Total"))
    add(("missing-row", {plan_path: plan.replace(suite_lines[3] + "\n", "", 1)}, f"{plan_path}: coverage table must equal retained ordered rows and Total"))
    relocated = plan.replace(suite_lines[4] + "\n", "", 1).replace("## Proven closure methods", f"## Proven closure methods\n\n{suite_lines[4]}", 1)
    add(("relocated-row", {plan_path: relocated}, f"{plan_path}: plan must contain exactly one contiguous table; found 2"))
    add(("total", {plan_path: plan.replace(total, total.replace(f"**{facts.proved}**", "**458**", 1), 1)}, f"{plan_path}: coverage table must equal retained ordered rows and Total"))
    tail = f" Treat the {facts.hda.open - 1} unproved human-decision-assurance refusals as real open evidence work."
    add(("step-four", {plan_path: plan.replace("from the underlying candidate-evidence evaluator.", "from the underlying candidate-evidence evaluator." + tail, 1)}, f"{plan_path}: Order of work step 4 must equal the exact HDA obligation"))
    readme_exact = "README.md: normalized Architecture checkpoint section differs from retained exact current unit"
    status_exact = f"{status}: normalized Current machine evidence section differs from retained exact current unit"
    status_row_exact = f"{status}: normalized Guard evidence row differs from retained exact current unit"
    handoff_exact = f"{handoff}: normalized current Guard coverage bullet differs from retained exact current unit"
    plan_exact = f"{plan_path}: normalized current closure-plan surface differs from retained exact current unit"
    visible_stale = "Current visible alternative: 458 of 927 checks are proved and 469 remain."
    boundary = "\n## Repository boundary"
    add(("alternate-prose", {"README.md": swap(readme, boundary, f"\n{visible_stale}\n{boundary}")}, readme_exact))
    add(("hidden-html", {"README.md": swap(readme, correct, f"<span hidden>{correct}</span> {visible_stale}")}, readme_exact))
    link_only = swap(swap(readme, correct, visible_stale), boundary, f'\n[guard-facts]: https://example.invalid "{correct}"\n{boundary}')
    add(("link-title", {"README.md": link_only}, readme_exact))
    indented = swap(swap(readme, correct, visible_stale), boundary, f"\n    {correct}\n{boundary}")
    add(("indented-code", {"README.md": indented}, readme_exact))
    nested = swap(swap(readme, correct, visible_stale), boundary, f"\n### Historical example\n\n{correct}\n{boundary}")
    add(("nested-history", {"README.md": nested}, readme_exact))
    unclosed = swap(swap(readme, correct, visible_stale), boundary, f"\n<!--\n{correct}\n{boundary}")
    add(("unclosed-comment", {"README.md": unclosed}, readme_exact))
    guard_line = next(line for line in kept[status].splitlines() if line.startswith("| Guard evidence |"))
    add(("whole-status-row", {status: kept[status].replace(guard_line, guard_line.replace("Coverage does not prove a guard enforces the right rule", "Coverage does not prove a guard enforces the right rule. Current fallback is 458/927", 1), 1)}, status_row_exact))
    add(("alternate-status-row", {status: kept[status].replace(guard_line, guard_line + "\n| Current alternate guard tally | 458/927 are proved and 469 are open | Current |", 1)}, status_exact))
    anchor = f"The {facts.open} open isolated-suite guards are"
    replacement = (
        "Current fallback: 458 of 927 are proved and 469 are open. "
        f"{anchor}"
    )
    add(
        (
            "alternate-handoff-prose",
            {handoff: swap(kept[handoff], anchor, replacement)},
            handoff_exact,
        )
    )
    add(("whole-plan-preamble", {plan_path: plan.replace("`scripts/audit_suite_guard_coverage.py`.", "`scripts/audit_suite_guard_coverage.py`. Current fallback is 458/927.", 1)}, plan_exact))
    add(("alternate-plan-prose", {plan_path: plan.replace("\nThe previously retained 431/820", "\nCurrent alternative denominator: 458 proved of 927, with 469 open.\n\nThe previously retained 431/820", 1)}, plan_exact))
    add(("alternate-plan-boundary", {plan_path: plan.replace("## Boundary\n", "## Boundary\n\nCurrent denominator is 458/927 with 469 open.\n", 1)}, plan_exact))
    pipe_less = "Alternative denominator | Proved | Total | Open\n--- | ---: | ---: | ---:\nContradictory current result | 458 | 927 | 469\n"
    add(("pipe-less-table", {plan_path: plan.replace("\n## Proven closure methods", "\n" + pipe_less + "\n## Proven closure methods", 1)}, plan_exact))
    changed = next(suite for suite in facts.suites if suite.name != facts.hda.name and suite.proved)
    old_row = f"| {changed.name} | {changed.proved} | {changed.total} | {changed.open} |"
    new_row = f"| {changed.name} | {changed.proved - 1} | {changed.total} | {changed.open + 1} |"
    add(("changed-non-hda-row", {plan_path: plan.replace(old_row, new_row, 1)}, f"{plan_path}: coverage table must equal retained ordered rows and Total"))
    passed = 0
    for case_id, overrides, wanted in cases:
        if all(overrides[path] == kept[path] for path in overrides):
            errors.append(f"truth-surface known-bad {case_id} did not mutate its subject")
            continue
        seen = truth_errors(facts, overrides)
        if seen == [wanted]:
            passed += 1
        else:
            errors.append(f"truth-surface known-bad {case_id} expected {wanted!r}; got {seen!r}")
    missing_target = "suite-guard intended mutation target that is absent"
    masked = swap(readme.replace(missing_target, "", 1), boundary, "\n### Architecture checkpoint ###\n" + boundary)
    masked_seen = truth_errors(facts, {"README.md": masked})
    unrelated, intended = "README.md: governed heading 'Architecture checkpoint' must occur exactly once; found 2", "README.md: Architecture checkpoint guard claim must occur exactly once; found 0"
    if missing_target in readme or masked_seen != [unrelated] or intended in masked_seen:
        errors.append(f"truth-surface masking meta-proof expected only {unrelated!r}; got {masked_seen!r}")
    else:
        passed += 1
    return passed


def main() -> int:
    errors: list[str] = []
    if not AUDIT.is_file():
        errors.append("suite guard audit tool is absent")
    try:
        document = json.loads(RECORD.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"suite guard coverage: invalid record: {exc}", file=sys.stderr)
        return 1
    if not isinstance(document, dict):
        print("suite guard coverage: record must be an object", file=sys.stderr)
        return 1
    facts = record_facts(document, errors)
    known_bads = guard_state_self_tests(errors)
    known_bads += suite_census_self_tests(errors)
    known_bads += schedule_state_self_tests(errors)
    if facts is not None:
        errors += truth_errors(facts)
        known_bads += self_tests(facts, errors)
    if errors:
        print("suite guard coverage: FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        f"suite guard-coverage record checked: {facts.proved}/{facts.total} guards proved "
        f"by mutation across {len(facts.suites)} suites, {facts.open} with no stable "
        f"suite-reported-refusal proof retained explicitly; {known_bads} exact "
        "guard-state/truth-surface known-bads "
        "rejected; coverage is not correctness and Gate A acceptance remains separate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
