#!/usr/bin/env python3
"""Apply or restore project-local Claude Code invocation policy for installed Matt skills.

Claude Code blocks Skill-tool calls to skills whose frontmatter sets
`disable-model-invocation: true`, and `skillOverrides` cannot re-enable them.
This adapter flips only that frontmatter value for the downstream stages so the
coordinator can continue after an explicit Matt entry. Entry skills stay
user-only. Skill bodies, resources and runtime permissions are never changed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys


_SHARED = Path(__file__).resolve().with_name("configure_codex_matt.py")
_SPEC = importlib.util.spec_from_file_location("configure_codex_matt", _SHARED)
shared = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(shared)
ConfigurationError = shared.ConfigurationError
local_path, read_optional, atomic_write = shared.local_path, shared.read_optional, shared.atomic_write

# True: user-only (`/name`). False: the model may invoke it through the Skill tool.
POLICIES = {
    "grill-with-docs": True,
    "wayfinder": True,
    "to-spec": False,
    "to-tickets": False,
    "implement": False,
    "retro": False,
}
# Invoked by the stages above through the Skill tool; must stay model-invocable.
DEPENDENCIES = (
    "grilling", "domain-modeling", "tdd", "code-review", "writing-for-agents", "research",
)
BACKUP = Path(".trellis/.runtime/claude-matt-policy.json")
FIELD = "disable-model-invocation"


def skill_path(name: str) -> Path:
    return Path(".claude/skills") / name / "SKILL.md"


def frontmatter_bounds(lines: list[str]) -> int:
    """Return the index of the closing `---` line of a leading frontmatter block."""
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise ConfigurationError("Expected SKILL.md to start with YAML frontmatter")
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            return index
    raise ConfigurationError("Unterminated SKILL.md frontmatter")


def current_policy(text: str) -> bool:
    lines = text.splitlines(keepends=True)
    end = frontmatter_bounds(lines)
    values = [m[1] for line in lines[1:end]
              if (m := re.match(rf"{FIELD}:[ \t]*(true|false)[ \t]*(?:#[^\r\n]*)?\r?\n?$", line))]
    return values == ["true"]


def with_policy(text: str, disabled: bool) -> str:
    """Set the frontmatter field, preserving every other byte of the file."""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    end = frontmatter_bounds(lines)
    value = str(disabled).lower()
    keys = [i for i in range(1, end) if re.match(rf"\s*['\"]?{FIELD}['\"]?\s*:", lines[i])]
    if len(keys) > 1:
        raise ConfigurationError(f"Duplicate {FIELD} field")
    if keys:
        match = re.fullmatch(
            rf"({FIELD}:[ \t]*)(true|false)([ \t]*(?:#[^\r\n]*)?)(\r?\n)?", lines[keys[0]],
        )
        if not match:
            raise ConfigurationError(f"Expected an unquoted top-level boolean {FIELD}")
        lines[keys[0]] = match[1] + value + match[3] + (match[4] or "")
    else:
        lines.insert(end, f"{FIELD}: {value}{newline}")
    return "".join(lines)


def validate_installation(root: Path) -> None:
    lock = local_path(root, Path("skills-lock.json"))
    if not lock.is_file():
        raise ConfigurationError("Missing skills-lock.json; install the Matt skills first")
    skills = json.loads(lock.read_text()).get("skills", {})
    for name in (*POLICIES, *DEPENDENCIES):
        if skills.get(name, {}).get("source") != "mattpocock/skills":
            raise ConfigurationError(f"Missing Matt installer provenance or name collision: {name}")
        body = local_path(root, skill_path(name))
        if not body.is_file():
            raise ConfigurationError(f"Missing skill: {skill_path(name)}; install it first")
        text = read_optional(body)
        lines = text.splitlines(keepends=True)
        end = frontmatter_bounds(lines)
        if not any(re.fullmatch(rf"name:\s*['\"]?{re.escape(name)}['\"]?\s*", line.rstrip("\r\n"))
                   for line in lines[1:end]):
            raise ConfigurationError(f"Skill name collision or invalid frontmatter: {name}")
        if name in DEPENDENCIES and current_policy(text):
            raise ConfigurationError(f"Dependency {name} is user-only; Matt stages call it via the Skill tool")


def read_backup(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    saved = json.loads(path.read_text())
    files = saved.get("files")
    if saved.get("version") != 1 or not isinstance(files, dict) or not files:
        raise ConfigurationError("Invalid Claude Matt policy backup; preserve it for recovery")
    allowed = {str(skill_path(name)): disabled for name, disabled in POLICIES.items()}
    for relative, entry in files.items():
        if relative not in allowed or not isinstance(entry, dict) or set(entry) != {"before", "after"}:
            raise ConfigurationError("Invalid Claude Matt policy backup entry")
        before, after = entry["before"], entry["after"]
        if not isinstance(before, str) or not isinstance(after, str):
            raise ConfigurationError("Invalid Claude Matt policy backup contents")
        if with_policy(before, allowed[relative]) != after:
            raise ConfigurationError("Backup does not describe a frontmatter-only policy change")
    return files


def configure(root: Path, *, check: bool = False, restore: bool = False) -> list[str]:
    root = root.resolve()
    backup_path = local_path(root, BACKUP)
    saved = read_backup(backup_path)
    if restore:
        # Preflight every file before restoring any; allow recovery of a partial apply.
        for relative, entry in saved.items():
            if read_optional(local_path(root, Path(relative))) not in (entry["before"], entry["after"]):
                raise ConfigurationError(f"Skill changed after configuration: {relative}; reconcile it first")
        for relative, entry in saved.items():
            atomic_write(local_path(root, Path(relative)), entry["before"])
        if saved:
            backup_path.unlink()
        return ["Restored original Claude Matt frontmatter" if saved else "Nothing to restore"]

    validate_installation(root)
    changes = {}
    for name, disabled in POLICIES.items():
        relative = str(skill_path(name))
        current = read_optional(local_path(root, Path(relative)))
        if relative in saved and current not in (saved[relative]["before"], saved[relative]["after"]):
            raise ConfigurationError(f"Skill changed after configuration: {relative}; reconcile it first")
        desired = with_policy(current, disabled)
        if desired != current:
            changes[relative] = desired
            if relative not in saved:
                saved[relative] = {"before": current, "after": desired}
    if check:
        if changes:
            raise ConfigurationError("Policy adaptation needed: " + ", ".join(changes))
        return ["Claude Matt policy is configured; entry skills remain user-only"]
    if changes:
        # Store originals first so an interrupted write can be retried or restored.
        atomic_write(backup_path, json.dumps({"version": 1, "files": saved}, indent=2) + "\n")
        for relative, desired in changes.items():
            atomic_write(local_path(root, Path(relative)), desired)
    return [f"Configured {len(changes)} Claude skill frontmatter fields; bodies and Codex metadata unchanged"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Project root (defaults to this checkout)")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Validate installation and policy without writing")
    modes.add_argument("--restore", action="store_true", help="Restore exact original frontmatter from the local backup")
    args = parser.parse_args()
    try:
        for message in configure(args.root, check=args.check, restore=args.restore):
            print(message)
    except (ConfigurationError, OSError, ValueError, TypeError) as error:
        print(f"Claude Matt configuration: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
