#!/usr/bin/env python3
"""Fail closed when repository bytes leave Odeya's architecture-only surface.

The policy is intentionally standard-library-only so the implementation lock
runs before architecture dependencies are trusted. A pass is bounded
repository-shape evidence, not Gate A acceptance or runtime authorization.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "architecture/architecture-surface-policy.json"
CASES_PATH = ROOT / "tests/architecture-surface/cases.json"
POLICY_ID = "odeya-architecture-surface-policy"
POLICY_VERSION = "0.1.0"
REQUIRED_SAFE_CASE_IDS = {
    "approved-release-executable",
    "architecture-document",
    "architecture-java-evaluator",
    "bounded-formal-model",
    "nonexecutable-validator",
    "retained-extensionless-license",
}
REQUIRED_KNOWN_BAD_CASE_IDS = {
    "arbitrary-top-level-file",
    "code-under-document-root",
    "disguised-binary-content",
    "disguised-script-extension",
    "disguised-shebang-content",
    "repository-symlink",
    "runtime-under-engine",
    "runtime-under-lib",
    "runtime-under-src",
    "staged-content-differs-from-benign-worktree",
    "submodule-gitlink",
    "unauthorized-executable-mode",
    "unapproved-code-under-script-root",
    "unknown-archive-type",
    "unapproved-content-addressed-blob",
    "unapproved-java-under-test-root",
}
POLICY_KEYS = {
    "policy_id",
    "version",
    "default_action",
    "allowed_top_level_files",
    "allowed_top_level_directories",
    "allowed_suffixes_by_root",
    "extensionless_path_allowlist",
    "code_path_allowlist",
    "executable_path_allowlist",
}
MANDATORY_FORBIDDEN_TOP_LEVEL = {
    "apps",
    "deploy",
    "engine",
    "infrastructure",
    "lib",
    "packages",
    "services",
    "src",
}
WORKSPACE_ONLY_TOP_LEVEL = {
    ".DS_Store",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv-architecture",
    "artifacts",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "tmp",
}
WORKSPACE_ONLY_PREFIXES = (".env",)
EXECUTABLE_SUFFIXES = {
    ".apk",
    ".app",
    ".bash",
    ".bat",
    ".bin",
    ".c",
    ".cc",
    ".cjs",
    ".class",
    ".cmd",
    ".com",
    ".cpp",
    ".cs",
    ".deb",
    ".dll",
    ".dylib",
    ".exe",
    ".fs",
    ".fsx",
    ".go",
    ".h",
    ".hpp",
    ".ipa",
    ".java",
    ".jar",
    ".js",
    ".jsx",
    ".kt",
    ".kts",
    ".lua",
    ".m",
    ".mjs",
    ".mm",
    ".php",
    ".pl",
    ".ps1",
    ".py",
    ".pyz",
    ".rb",
    ".rpm",
    ".rs",
    ".scala",
    ".sh",
    ".so",
    ".swift",
    ".tla",
    ".ts",
    ".tsx",
    ".vb",
    ".wasm",
    ".whl",
    ".yaml",
    ".yml",
    ".zsh",
}
EXECUTABLE_SIGNATURES = (
    (b"#!", "a shebang"),
    (b"\x7fELF", "ELF magic"),
    (b"MZ", "PE magic"),
    (b"\xca\xfe\xba\xbe", "Java class magic"),
    (b"\x00asm", "WebAssembly magic"),
    (b"\xfe\xed\xfa\xce", "Mach-O magic"),
    (b"\xfe\xed\xfa\xcf", "Mach-O magic"),
    (b"\xce\xfa\xed\xfe", "Mach-O magic"),
    (b"\xcf\xfa\xed\xfe", "Mach-O magic"),
)


class DuplicateKeyError(ValueError):
    """Raised when JSON would otherwise overwrite a policy or case member."""


class InventoryError(RuntimeError):
    """Raised when a Git candidate inventory cannot be read completely."""


@dataclass(frozen=True)
class SurfaceEntry:
    path: str
    kind: str
    mode: int = 0
    content_prefixes: tuple[bytes, ...] = ()


@dataclass(frozen=True)
class SurfacePolicy:
    top_level_files: frozenset[str]
    top_level_directories: frozenset[str]
    suffixes_by_root: dict[str, frozenset[str]]
    extensionless_paths: frozenset[str]
    code_paths: frozenset[str]
    executable_paths: frozenset[str]


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise DuplicateKeyError(f"duplicate JSON member {key!r}")
        value[key] = item
    return value


def load_json(path: Path, errors: list[str], label: str) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
        )
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        errors.append(f"implementation lock {label} invalid: {exc}")
        return None


def normalized_relative_path(value: object) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        return None
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or candidate.as_posix() != value:
        return None
    if any(part in {"", ".", ".."} for part in candidate.parts):
        return None
    return value


def string_set(
    document: dict[str, Any],
    key: str,
    errors: list[str],
    *,
    paths: bool = False,
) -> frozenset[str]:
    value = document.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"implementation lock policy invalid: {key} must be a non-empty list")
        return frozenset()
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            errors.append(
                f"implementation lock policy invalid: {key}[{index}] must be a non-empty string"
            )
            continue
        if paths and normalized_relative_path(item) is None:
            errors.append(
                f"implementation lock policy invalid: {key}[{index}] is not a normalized path"
            )
            continue
        result.append(item)
    if len(set(result)) != len(result):
        errors.append(f"implementation lock policy invalid: {key} contains duplicates")
    return frozenset(result)


def load_policy(errors: list[str]) -> SurfacePolicy | None:
    document = load_json(POLICY_PATH, errors, "policy")
    if not isinstance(document, dict):
        if document is not None:
            errors.append("implementation lock policy invalid: root must be an object")
        return None
    if set(document) != POLICY_KEYS:
        errors.append(
            "implementation lock policy invalid: root keys differ from the closed policy vocabulary"
        )
    if document.get("policy_id") != POLICY_ID:
        errors.append(f"implementation lock policy invalid: policy_id must be {POLICY_ID!r}")
    if document.get("version") != POLICY_VERSION:
        errors.append(f"implementation lock policy invalid: version must be {POLICY_VERSION!r}")
    if document.get("default_action") != "deny":
        errors.append("implementation lock policy invalid: default_action must remain 'deny'")

    top_level_files = string_set(document, "allowed_top_level_files", errors)
    top_level_directories = string_set(
        document, "allowed_top_level_directories", errors
    )
    for value in top_level_files | top_level_directories:
        if "/" in value or normalized_relative_path(value) is None:
            errors.append(
                "implementation lock policy invalid: top-level allowlists may contain names only"
            )
    overlap = top_level_files & top_level_directories
    if overlap:
        errors.append(
            "implementation lock policy invalid: top-level file/directory overlap "
            + ", ".join(sorted(overlap))
        )
    forbidden_admitted = top_level_directories & MANDATORY_FORBIDDEN_TOP_LEVEL
    if forbidden_admitted:
        errors.append(
            "implementation lock policy invalid: runtime roots cannot be admitted: "
            + ", ".join(sorted(forbidden_admitted))
        )

    raw_suffixes = document.get("allowed_suffixes_by_root")
    suffixes_by_root: dict[str, frozenset[str]] = {}
    if not isinstance(raw_suffixes, dict):
        errors.append(
            "implementation lock policy invalid: allowed_suffixes_by_root must be an object"
        )
    else:
        if set(raw_suffixes) != set(top_level_directories):
            errors.append(
                "implementation lock policy invalid: suffix roots must equal the "
                "top-level directory allowlist"
            )
        for root, raw_values in raw_suffixes.items():
            if not isinstance(root, str) or not isinstance(raw_values, list):
                errors.append(
                    "implementation lock policy invalid: every suffix root must map to a list"
                )
                continue
            values: list[str] = []
            for index, item in enumerate(raw_values):
                if (
                    not isinstance(item, str)
                    or not item.startswith(".")
                    or item != item.lower()
                ):
                    errors.append(
                        "implementation lock policy invalid: "
                        f"{root} suffix {index} must be a lowercase dot-suffix"
                    )
                    continue
                values.append(item)
            if len(values) != len(set(values)):
                errors.append(
                    f"implementation lock policy invalid: {root} suffixes contain duplicates"
                )
            suffixes_by_root[root] = frozenset(values)

    extensionless_paths = string_set(
        document, "extensionless_path_allowlist", errors, paths=True
    )
    code_paths = string_set(document, "code_path_allowlist", errors, paths=True)
    executable_paths = string_set(
        document, "executable_path_allowlist", errors, paths=True
    )
    if not executable_paths <= code_paths:
        errors.append(
            "implementation lock policy invalid: executable paths must also be code paths"
        )

    policy = SurfacePolicy(
        top_level_files=top_level_files,
        top_level_directories=top_level_directories,
        suffixes_by_root=suffixes_by_root,
        extensionless_paths=extensionless_paths,
        code_paths=code_paths,
        executable_paths=executable_paths,
    )
    validate_policy_references(policy, errors)
    return policy


def path_type_authorized(path: str, policy: SurfacePolicy) -> bool:
    pure = PurePosixPath(path)
    if len(pure.parts) == 1:
        return path in policy.top_level_files
    root = pure.parts[0]
    if root not in policy.top_level_directories:
        return False
    if path in policy.extensionless_paths:
        return True
    return pure.suffix.lower() in policy.suffixes_by_root.get(root, frozenset())


def validate_policy_references(policy: SurfacePolicy, errors: list[str]) -> None:
    for name in sorted(policy.top_level_files | policy.top_level_directories):
        if not (ROOT / name).exists():
            errors.append(
                f"implementation lock policy invalid: allowlisted top-level entry is absent: {name}"
            )
    for path in sorted(
        policy.extensionless_paths | policy.code_paths | policy.executable_paths
    ):
        candidate = ROOT / path
        if not candidate.is_file() or candidate.is_symlink():
            errors.append(
                f"implementation lock policy invalid: allowlisted file is absent or not regular: {path}"
            )
        if not path_type_authorized(path, policy):
            errors.append(
                f"implementation lock policy invalid: allowlisted path has no authorized file type: {path}"
            )
    for path in sorted(policy.executable_paths):
        try:
            mode = (ROOT / path).stat().st_mode
        except OSError:
            continue
        if not mode & 0o111:
            errors.append(
                f"implementation lock policy invalid: approved executable lacks an executable bit: {path}"
            )


def executable_signature(prefix: bytes) -> str | None:
    for signature, label in EXECUTABLE_SIGNATURES:
        if prefix.startswith(signature):
            return label
    return None


def implementation_lock_errors(
    entry: SurfaceEntry,
    policy: SurfacePolicy,
) -> list[str]:
    path = normalized_relative_path(entry.path)
    if path is None:
        return [
            "implementation lock violation [invalid-path]: "
            f"{entry.path!r} is not a normalized repository-relative path"
        ]
    pure = PurePosixPath(path)
    root = pure.parts[0]

    if entry.kind == "symlink":
        return [
            f"implementation lock violation [symlink]: {path} is a symlink; "
            "repository symlinks are forbidden"
        ]
    if entry.kind == "gitlink":
        return [
            f"implementation lock violation [gitlink]: {path} uses Git mode 160000; "
            "submodules are outside the architecture surface"
        ]
    if entry.kind not in {"file", "directory"}:
        return [
            f"implementation lock violation [special-file]: {path} is a "
            f"{entry.kind}; only regular files and approved directories are allowed"
        ]
    if len(pure.parts) == 1 and entry.kind == "directory":
        if path not in policy.top_level_directories:
            return [
                f"implementation lock violation [forbidden-top-level]: {path}/ "
                "is outside the architecture surface"
            ]
        return []
    if len(pure.parts) == 1:
        if path not in policy.top_level_files:
            return [
                f"implementation lock violation [unauthorized-top-level-file]: {path} "
                "is not an approved top-level architecture file"
            ]
    elif root not in policy.top_level_directories:
        return [
            f"implementation lock violation [forbidden-top-level]: {root}/ "
            "is outside the architecture surface"
        ]
    if entry.kind == "directory":
        return []

    suffixes = [suffix.lower() for suffix in pure.suffixes]
    embedded_executable = next(
        (suffix for suffix in suffixes[:-1] if suffix in EXECUTABLE_SUFFIXES),
        None,
    )
    if embedded_executable is not None:
        return [
            f"implementation lock violation [disguised-executable-name]: {path} "
            f"embeds executable suffix {embedded_executable}"
        ]

    suffix = pure.suffix.lower()
    if suffix in EXECUTABLE_SUFFIXES and path not in policy.code_paths:
        return [
            f"implementation lock violation [unauthorized-code-path]: {path} "
            "is executable-capable code not named by the architecture policy"
        ]
    if not path_type_authorized(path, policy):
        return [
            f"implementation lock violation [unauthorized-file-type]: {path} "
            "has no architecture-authorized file type"
        ]
    if entry.mode & 0o111 and path not in policy.executable_paths:
        return [
            f"implementation lock violation [unauthorized-executable-bit]: {path} "
            "has an executable bit but is not an approved executable"
        ]

    if path not in policy.code_paths:
        for prefix in entry.content_prefixes:
            signature = executable_signature(prefix)
            if signature is not None:
                return [
                    f"implementation lock violation [disguised-executable-content]: {path} "
                    f"begins with {signature} but is not an approved code path"
                ]
    return []


def read_index_blob_prefixes(records: list[tuple[str, str]]) -> dict[str, bytes]:
    if not records:
        return {}
    request = "".join(f"{object_id}\n" for _path, object_id in records).encode("ascii")
    result = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=ROOT,
        input=request,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise InventoryError(f"git cat-file --batch failed: {detail}")

    prefixes: dict[str, bytes] = {}
    cursor = 0
    output = result.stdout
    for path, expected_object_id in records:
        header_end = output.find(b"\n", cursor)
        if header_end < 0:
            raise InventoryError(f"git cat-file output ended before the header for {path}")
        header = output[cursor:header_end].split()
        if len(header) != 3:
            raise InventoryError(f"git cat-file returned a malformed header for {path}")
        object_id, object_type, raw_size = header
        try:
            size = int(raw_size)
        except ValueError as exc:
            raise InventoryError(
                f"git cat-file returned an invalid size for {path}"
            ) from exc
        if (
            object_id.decode("ascii", errors="replace") != expected_object_id
            or object_type != b"blob"
            or size < 0
        ):
            raise InventoryError(f"git cat-file returned the wrong object for {path}")
        content_start = header_end + 1
        content_end = content_start + size
        if content_end >= len(output) or output[content_end : content_end + 1] != b"\n":
            raise InventoryError(f"git cat-file returned a truncated blob for {path}")
        prefixes[path] = output[content_start : min(content_start + 16, content_end)]
        cursor = content_end + 1
    if cursor != len(output):
        raise InventoryError("git cat-file returned unrequested trailing output")
    return prefixes


def git_inventory() -> tuple[list[str], dict[str, int], dict[str, bytes]] | None:
    if not (ROOT / ".git").exists():
        return None
    inventory = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if inventory.returncode != 0:
        detail = inventory.stderr.decode("utf-8", errors="replace").strip()
        raise InventoryError(f"git ls-files inventory failed: {detail}")
    paths = [
        os.fsdecode(item)
        for item in inventory.stdout.split(b"\0")
        if item
    ]
    staged = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if staged.returncode != 0:
        detail = staged.stderr.decode("utf-8", errors="replace").strip()
        raise InventoryError(f"git ls-files staged inventory failed: {detail}")
    modes: dict[str, int] = {}
    blob_records: list[tuple[str, str]] = []
    for item in staged.stdout.split(b"\0"):
        if not item:
            continue
        metadata, separator, raw_path = item.partition(b"\t")
        fields = metadata.split()
        if separator != b"\t" or len(fields) != 3:
            raise InventoryError("git ls-files returned a malformed staged entry")
        raw_mode, raw_object_id, stage = fields
        path = os.fsdecode(raw_path)
        if stage != b"0":
            raise InventoryError(f"unmerged index entry is not a valid candidate: {path}")
        if path in modes:
            raise InventoryError(f"git index returned a duplicate stage-zero path: {path}")
        try:
            mode = int(raw_mode, 8)
        except ValueError as exc:
            raise InventoryError(f"git index returned an invalid mode for {path}") from exc
        modes[path] = mode
        if mode in {0o100644, 0o100755}:
            blob_records.append((path, raw_object_id.decode("ascii")))
    return paths, modes, read_index_blob_prefixes(blob_records)


def workspace_only_name(name: str) -> bool:
    return name in WORKSPACE_ONLY_TOP_LEVEL or name.startswith(
        WORKSPACE_ONLY_PREFIXES
    )


def filesystem_inventory() -> list[str]:
    paths: list[str] = []
    for current, directories, filenames in os.walk(ROOT, followlinks=False):
        current_path = Path(current)
        if current_path == ROOT:
            directories[:] = [
                name
                for name in directories
                if not workspace_only_name(name)
            ]
        else:
            directories[:] = [
                name
                for name in directories
                if name
                not in {
                    "__pycache__",
                    ".mypy_cache",
                    ".pytest_cache",
                    ".ruff_cache",
                    "node_modules",
                }
            ]
        for name in filenames:
            candidate = current_path / name
            paths.append(candidate.relative_to(ROOT).as_posix())
        for name in directories:
            candidate = current_path / name
            if candidate.is_symlink():
                paths.append(candidate.relative_to(ROOT).as_posix())
    return paths


def read_prefix(path: Path) -> bytes:
    try:
        with path.open("rb") as stream:
            return stream.read(16)
    except OSError:
        return b""


def discover_entries(
    policy: SurfacePolicy,
    errors: list[str],
) -> list[SurfaceEntry]:
    entries: list[SurfaceEntry] = []
    forbidden_directories: set[str] = set()
    for candidate in ROOT.iterdir():
        name = candidate.name
        if workspace_only_name(name):
            continue
        if candidate.is_symlink():
            entries.append(
                SurfaceEntry(
                    path=name,
                    kind="symlink",
                    mode=candidate.lstat().st_mode,
                )
            )
        elif candidate.is_dir():
            if name not in policy.top_level_directories:
                forbidden_directories.add(name)
                entries.append(
                    SurfaceEntry(
                        path=name,
                        kind="directory",
                        mode=candidate.stat().st_mode,
                    )
                )
        elif name not in policy.top_level_files:
            mode = candidate.lstat().st_mode
            kind = "file" if stat.S_ISREG(mode) else "special"
            entries.append(
                SurfaceEntry(
                    path=name,
                    kind=kind,
                    mode=mode,
                    content_prefixes=(
                        (read_prefix(candidate),) if kind == "file" else ()
                    ),
                )
            )

    try:
        git_result = git_inventory()
    except InventoryError as exc:
        errors.append(f"implementation lock inventory invalid: {exc}")
        return entries
    if git_result is None:
        paths = filesystem_inventory()
        index_modes: dict[str, int] = {}
        index_prefixes: dict[str, bytes] = {}
    else:
        paths, index_modes, index_prefixes = git_result
    seen = {entry.path for entry in entries}
    for relative in sorted(set(paths)):
        normalized = normalized_relative_path(relative)
        if normalized is None:
            entries.append(SurfaceEntry(path=relative, kind="file"))
            continue
        if PurePosixPath(normalized).parts[0] in forbidden_directories:
            continue
        if normalized in seen:
            continue
        path = ROOT / normalized
        index_mode = index_modes.get(normalized, 0)
        try:
            worktree_mode = path.lstat().st_mode
        except OSError:
            worktree_mode = 0
        mode = index_mode | worktree_mode
        if index_mode == 0o120000:
            kind = "symlink"
        elif index_mode == 0o160000:
            kind = "gitlink"
        elif index_mode and index_mode not in {0o100644, 0o100755}:
            kind = "unsupported-index-mode"
        elif worktree_mode and stat.S_ISLNK(worktree_mode):
            kind = "symlink"
        elif index_mode in {0o100644, 0o100755}:
            kind = "file"
        elif worktree_mode and not stat.S_ISREG(worktree_mode):
            kind = "directory" if stat.S_ISDIR(worktree_mode) else "special"
        else:
            kind = "file"
        prefixes: list[bytes] = []
        if normalized in index_prefixes:
            prefixes.append(index_prefixes[normalized])
        if kind == "file" and worktree_mode and stat.S_ISREG(worktree_mode):
            worktree_prefix = read_prefix(path)
            if worktree_prefix not in prefixes:
                prefixes.append(worktree_prefix)
        entries.append(
            SurfaceEntry(
                path=normalized,
                kind=kind,
                mode=mode,
                content_prefixes=tuple(prefixes),
            )
        )
        seen.add(normalized)
    return entries


def parse_case_entry(document: object, case_id: str, errors: list[str]) -> SurfaceEntry | None:
    if not isinstance(document, dict) or set(document) - {
        "path",
        "kind",
        "mode",
        "content_prefix",
        "content_prefix_hex",
        "additional_content_prefix",
    }:
        errors.append(
            f"implementation lock self-test invalid: {case_id} entry has an invalid shape"
        )
        return None
    path = document.get("path")
    kind = document.get("kind")
    mode_text = document.get("mode", "100644")
    if not isinstance(path, str) or not isinstance(kind, str):
        errors.append(
            f"implementation lock self-test invalid: {case_id} entry needs path and kind"
        )
        return None
    if not isinstance(mode_text, str):
        errors.append(
            f"implementation lock self-test invalid: {case_id} mode must be an octal string"
        )
        return None
    try:
        mode = int(mode_text, 8)
    except ValueError:
        errors.append(
            f"implementation lock self-test invalid: {case_id} mode is not octal"
        )
        return None
    prefix_text = document.get("content_prefix")
    prefix_hex = document.get("content_prefix_hex")
    if prefix_text is not None and prefix_hex is not None:
        errors.append(
            f"implementation lock self-test invalid: {case_id} declares two content prefixes"
        )
        return None
    prefixes: list[bytes] = []
    if prefix_text is not None:
        if not isinstance(prefix_text, str):
            errors.append(
                f"implementation lock self-test invalid: {case_id} content_prefix must be text"
            )
            return None
        prefixes.append(prefix_text.encode("utf-8"))
    elif prefix_hex is not None:
        if not isinstance(prefix_hex, str):
            errors.append(
                f"implementation lock self-test invalid: {case_id} content_prefix_hex must be text"
            )
            return None
        try:
            prefixes.append(bytes.fromhex(prefix_hex))
        except ValueError:
            errors.append(
                f"implementation lock self-test invalid: {case_id} content_prefix_hex is invalid"
            )
            return None
    additional_prefix = document.get("additional_content_prefix")
    if additional_prefix is not None:
        if not isinstance(additional_prefix, str):
            errors.append(
                f"implementation lock self-test invalid: {case_id} "
                "additional_content_prefix must be text"
            )
            return None
        prefixes.append(additional_prefix.encode("utf-8"))
    return SurfaceEntry(
        path=path,
        kind=kind,
        mode=mode,
        content_prefixes=tuple(prefixes),
    )


def run_self_tests(policy: SurfacePolicy, errors: list[str]) -> tuple[int, int]:
    document = load_json(CASES_PATH, errors, "self-test corpus")
    if not isinstance(document, dict):
        if document is not None:
            errors.append("implementation lock self-test invalid: root must be an object")
        return 0, 0
    if set(document) != {
        "policy_id",
        "version",
        "safe_cases",
        "known_bad_cases",
    }:
        errors.append(
            "implementation lock self-test invalid: root keys differ from the closed corpus shape"
        )
    if document.get("policy_id") != POLICY_ID or document.get("version") != POLICY_VERSION:
        errors.append(
            "implementation lock self-test invalid: policy identity/version differs"
        )
    safe_cases = document.get("safe_cases")
    known_bad_cases = document.get("known_bad_cases")
    if not isinstance(safe_cases, list) or not safe_cases:
        errors.append("implementation lock self-test invalid: safe_cases must be non-empty")
        safe_cases = []
    if not isinstance(known_bad_cases, list) or not known_bad_cases:
        errors.append(
            "implementation lock self-test invalid: known_bad_cases must be non-empty"
        )
        known_bad_cases = []

    seen_ids: set[str] = set()
    observed_safe_ids: set[str] = set()
    observed_known_bad_ids: set[str] = set()
    for expected_safe, cases in ((True, safe_cases), (False, known_bad_cases)):
        for index, case in enumerate(cases):
            label = "safe_cases" if expected_safe else "known_bad_cases"
            if not isinstance(case, dict):
                errors.append(
                    f"implementation lock self-test invalid: {label}[{index}] must be an object"
                )
                continue
            expected_keys = {"id", "entry"}
            if not expected_safe:
                expected_keys.add("expected_error")
            if set(case) != expected_keys:
                errors.append(
                    f"implementation lock self-test invalid: {label}[{index}] has invalid keys"
                )
                continue
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id or case_id in seen_ids:
                errors.append(
                    f"implementation lock self-test invalid: {label}[{index}] id is absent or duplicate"
                )
                continue
            seen_ids.add(case_id)
            if expected_safe:
                observed_safe_ids.add(case_id)
            else:
                observed_known_bad_ids.add(case_id)
            entry = parse_case_entry(case.get("entry"), case_id, errors)
            if entry is None:
                continue
            observed = implementation_lock_errors(entry, policy)
            if expected_safe:
                if observed:
                    errors.append(
                        f"implementation lock self-test {case_id}: safe entry was refused: "
                        + " | ".join(observed)
                    )
            else:
                expected_error = case.get("expected_error")
                if not isinstance(expected_error, str) or observed != [expected_error]:
                    errors.append(
                        f"implementation lock self-test {case_id}: expected exactly "
                        f"{expected_error!r}, observed {observed!r}"
                    )
    if observed_safe_ids != REQUIRED_SAFE_CASE_IDS:
        errors.append(
            "implementation lock self-test invalid: safe case IDs differ from the "
            "required retained inventory"
        )
    if observed_known_bad_ids != REQUIRED_KNOWN_BAD_CASE_IDS:
        errors.append(
            "implementation lock self-test invalid: known-bad case IDs differ from "
            "the required retained inventory"
        )
    return len(safe_cases), len(known_bad_cases)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test-only",
        action="store_true",
        help="run retained safe and known-bad probes without inspecting the repository",
    )
    args = parser.parse_args()

    errors: list[str] = []
    policy = load_policy(errors)
    safe_count = 0
    known_bad_count = 0
    if policy is not None:
        safe_count, known_bad_count = run_self_tests(policy, errors)
        if not args.self_test_only:
            for entry in discover_entries(policy, errors):
                errors.extend(implementation_lock_errors(entry, policy))

    if errors:
        print("Odeya architecture-surface validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Odeya architecture-surface validation PASSED")
    print(f"- {safe_count} retained safe probes accepted")
    print(
        f"- {known_bad_count} retained known-bad implementation-lock probes "
        "refused for their exact reason"
    )
    if args.self_test_only:
        print("- repository inventory not inspected (--self-test-only)")
    else:
        print("- default-deny repository inventory inspected; Gate A remains blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
