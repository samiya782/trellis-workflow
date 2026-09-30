#!/usr/bin/env python3
"""Apply or restore project-local Codex invocation metadata for installed Matt skills.

Install the genuine skills first. This adapter changes only OpenAI policy metadata;
it never installs skills, edits their instructions, or changes runtime permissions.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


POLICIES = {
    "grill-with-docs": False,
    "wayfinder": False,
    "to-spec": True,
    "to-tickets": True,
    "implement": True,
    "retro": True,
}
DEPENDENCIES = (
    "grilling", "domain-modeling", "tdd", "code-review", "writing-for-agents", "research",
)
BACKUP = Path(".trellis/.runtime/matt-policy.json")


class ConfigurationError(Exception):
    """The local installation cannot safely receive the policy adaptation."""


def local_path(root: Path, relative: Path) -> Path:
    """Reject aliases that could share metadata with Claude or another project."""
    path = root
    for part in relative.parts:
        path /= part
        if path.is_symlink():
            raise ConfigurationError(f"Symlinked path is unsupported: {relative}")
    if path.exists() and path.is_file() and path.stat().st_nlink > 1:
        raise ConfigurationError(f"Hardlinked file is unsupported: {relative}")
    return path


def policy_path(name: str) -> Path:
    return Path(".agents/skills") / name / "agents/openai.yaml"


def with_policy(original: str | None, enabled: bool) -> str:
    """Edit the known upstream block-style field, preserving every other byte."""
    text = original or ""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    policies = [i for i, line in enumerate(lines) if re.match(r"^policy\s*:", line)]
    if len(policies) > 1:
        raise ConfigurationError("Duplicate policy mapping in openai.yaml")
    value = str(enabled).lower()
    if not policies:
        if re.search(r"(?m)^\s*['\"]?policy['\"]?\s*:", text):
            raise ConfigurationError("Expected an unquoted, top-level policy mapping")
        separator = "" if not text or text.endswith("\n") else newline
        return f"{text}{separator}policy:{newline}  allow_implicit_invocation: {value}{newline}"
    start = policies[0]
    if not re.fullmatch(r"policy:[ \t]*(?:#[^\r\n]*)?(?:\r?\n)?", lines[start]):
        raise ConfigurationError("Expected block-style policy mapping in openai.yaml")
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].strip() and not lines[i].startswith((" ", "\t", "#"))), len(lines))
    keys = [i for i in range(start + 1, end)
            if re.match(r"\s*allow_implicit_invocation\s*:", lines[i])]
    if len(keys) > 1:
        raise ConfigurationError("Duplicate allow_implicit_invocation policy")
    if keys:
        index = keys[0]
        match = re.fullmatch(
            r"(  allow_implicit_invocation:[ \t]*)(true|false)([ \t]*(?:#[^\r\n]*)?)(\r?\n)?",
            lines[index],
        )
        if not match:
            raise ConfigurationError("Expected a two-space-indented boolean invocation policy")
        lines[index] = match[1] + value + match[3] + (match[4] or "")
    else:
        if any("allow_implicit_invocation" in line and not line.lstrip().startswith("#")
               for line in lines[start + 1:end]):
            raise ConfigurationError("Unsupported invocation policy syntax")
        if not lines[start].endswith("\n"):
            lines[start] += newline
        lines.insert(start + 1, f"  allow_implicit_invocation: {value}{newline}")
    return "".join(lines)


def read_optional(path: Path) -> str | None:
    return path.read_bytes().decode("utf-8") if path.exists() else None


def validate_installation(root: Path) -> None:
    lock = local_path(root, Path("skills-lock.json"))
    if not lock.is_file():
        raise ConfigurationError("Missing skills-lock.json; install the Matt skills first")
    skills = json.loads(lock.read_text()).get("skills", {})
    for name in (*POLICIES, *DEPENDENCIES):
        if skills.get(name, {}).get("source") != "mattpocock/skills":
            raise ConfigurationError(f"Missing Matt installer provenance or name collision: {name}")
        body = local_path(root, Path(".agents/skills") / name / "SKILL.md")
        if not body.is_file():
            raise ConfigurationError(f"Missing skill: {body.relative_to(root)}; install it first")
        contents = body.read_text()
        frontmatter = contents.split("---", 2)
        if len(frontmatter) != 3 or frontmatter[0].strip() or not re.search(
            rf"(?m)^name:\s*['\"]?{re.escape(name)}['\"]?\s*$", frontmatter[1]
        ):
            raise ConfigurationError(f"Skill name collision or invalid frontmatter: {name}")
        local_path(root, policy_path(name))


def read_backup(path: Path) -> dict[str, dict[str, str | None]]:
    if not path.exists():
        return {}
    saved = json.loads(path.read_text())
    files = saved.get("files")
    if saved.get("version") != 1 or not isinstance(files, dict) or not files:
        raise ConfigurationError("Invalid Matt policy backup; preserve it for recovery")
    allowed = {str(policy_path(name)): enabled for name, enabled in POLICIES.items()}
    for relative, entry in files.items():
        if relative not in allowed or not isinstance(entry, dict) or set(entry) != {"before", "after"}:
            raise ConfigurationError("Invalid Matt policy backup entry")
        before, after = entry["before"], entry["after"]
        if (before is not None and not isinstance(before, str)) or not isinstance(after, str):
            raise ConfigurationError("Invalid Matt policy backup contents")
        if with_policy(before, allowed[relative]) != after:
            raise ConfigurationError("Backup does not describe a metadata-only policy change")
    return files


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(text.encode("utf-8"))
        os.chmod(temporary, previous_mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def configure(root: Path, *, check: bool = False, restore: bool = False) -> list[str]:
    root = root.resolve()
    backup_path = local_path(root, BACKUP)
    saved = read_backup(backup_path)
    if restore:
        # Preflight every file before restoring any; allow recovery of a partial apply.
        for relative, entry in saved.items():
            current = read_optional(local_path(root, Path(relative)))
            if current not in (entry["before"], entry["after"]):
                raise ConfigurationError(f"Metadata changed after configuration: {relative}; reconcile it first")
        for relative, entry in saved.items():
            path = local_path(root, Path(relative))
            if entry["before"] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, entry["before"])
        if saved:
            backup_path.unlink()
        return ["Restored original Codex Matt metadata" if saved else "Nothing to restore"]

    validate_installation(root)
    changes = {}
    for name, enabled in POLICIES.items():
        relative = str(policy_path(name))
        current = read_optional(local_path(root, Path(relative)))
        if relative in saved and current not in (saved[relative]["before"], saved[relative]["after"]):
            raise ConfigurationError(f"Metadata changed after configuration: {relative}; reconcile it first")
        desired = with_policy(current, enabled)
        if desired != current:
            changes[relative] = desired
            if relative not in saved:
                saved[relative] = {"before": current, "after": desired}
    if check:
        if changes:
            raise ConfigurationError("Policy adaptation needed: " + ", ".join(changes))
        return ["Codex Matt policy is configured; entry skills remain explicit"]
    if changes:
        # Store originals first so an interrupted write can be retried or restored.
        atomic_write(backup_path, json.dumps({"version": 1, "files": saved}, indent=2) + "\n")
        for relative, desired in changes.items():
            atomic_write(local_path(root, Path(relative)), desired)
    return [f"Configured {len(changes)} Codex metadata files; Claude and skill bodies unchanged"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Project root (defaults to this checkout)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Validate installation and policy without writing")
    modes.add_argument("--restore", action="store_true", help="Restore exact original metadata from the local backup")
    args = parser.parse_args()
    try:
        for message in configure(args.root, check=args.check, restore=args.restore):
            print(message)
    except (ConfigurationError, OSError, ValueError, TypeError) as error:
        print(f"Codex Matt configuration: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
