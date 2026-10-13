#!/usr/bin/env python3
"""Validate task plans and prepare isolated Git worktrees; no agent runs yet."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


class PlanError(ValueError):
    """Raised when a task plan is malformed or unsafe to prepare."""


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    description: str
    files: tuple[str, ...]
    depends_on: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]


TASK_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,39}$")
REQUIRED_FIELDS = {
    "id", "title", "description", "files", "depends_on", "acceptance_criteria"
}


def _safe_relative_path(raw: Any, *, task_id: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise PlanError(f"{task_id}: each files entry must be a non-empty relative path")
    if "\\" in raw or re.match(r"^[A-Za-z]:", raw):
        raise PlanError(f"{task_id}: allowed paths must use repository-relative POSIX syntax: {raw!r}")
    path = PurePosixPath(raw)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise PlanError(f"{task_id}: unsafe allowed path: {raw!r}")
    normalized = str(path).rstrip("/")
    if not normalized or normalized == ".":
        raise PlanError(f"{task_id}: allowed path cannot be the repository root")
    return normalized


def load_tasks(path: Path) -> list[Task]:
    try:
        raw_tasks = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"cannot read task JSON {path}: {exc}") from exc
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise PlanError("task file must contain a non-empty JSON array")
    if len(raw_tasks) > 3:
        raise PlanError("the initial team supports at most three worker tasks")

    tasks: list[Task] = []
    ids: set[str] = set()
    for index, item in enumerate(raw_tasks):
        if not isinstance(item, dict):
            raise PlanError(f"task #{index + 1} must be a JSON object")
        missing = REQUIRED_FIELDS - item.keys()
        extra = item.keys() - REQUIRED_FIELDS
        if missing or extra:
            parts = []
            if missing:
                parts.append(f"missing fields: {', '.join(sorted(missing))}")
            if extra:
                parts.append(f"unsupported fields: {', '.join(sorted(extra))}")
            raise PlanError(f"task #{index + 1}: {'; '.join(parts)}")

        task_id = item["id"]
        if not isinstance(task_id, str) or not TASK_ID_RE.fullmatch(task_id):
            raise PlanError(f"task #{index + 1}: id must match {TASK_ID_RE.pattern}")
        if task_id in ids:
            raise PlanError(f"duplicate task id: {task_id}")
        ids.add(task_id)

        for field in ("title", "description"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise PlanError(f"{task_id}: {field} must be a non-empty string")
        if not isinstance(item["files"], list) or not item["files"]:
            raise PlanError(f"{task_id}: files must be a non-empty array")
        if not isinstance(item["depends_on"], list) or not all(
            isinstance(dep, str) for dep in item["depends_on"]
        ):
            raise PlanError(f"{task_id}: depends_on must be an array of task ids")
        if not isinstance(item["acceptance_criteria"], list) or not item["acceptance_criteria"] or not all(
            isinstance(rule, str) and rule.strip() for rule in item["acceptance_criteria"]
        ):
            raise PlanError(f"{task_id}: acceptance_criteria must be non-empty strings")

        files = tuple(_safe_relative_path(value, task_id=task_id) for value in item["files"])
        if len(set(files)) != len(files):
            raise PlanError(f"{task_id}: duplicate allowed paths")
        if len(set(item["depends_on"])) != len(item["depends_on"]):
            raise PlanError(f"{task_id}: duplicate dependencies")
        if task_id in item["depends_on"]:
            raise PlanError(f"{task_id}: task cannot depend on itself")
        tasks.append(Task(
            id=task_id,
            title=item["title"].strip(),
            description=item["description"].strip(),
            files=files,
            depends_on=tuple(item["depends_on"]),
            acceptance_criteria=tuple(rule.strip() for rule in item["acceptance_criteria"]),
        ))

    validate_task_graph(tasks)
    validate_path_ownership(tasks)
    return tasks


def validate_task_graph(tasks: list[Task]) -> list[Task]:
    by_id = {task.id: task for task in tasks}
    for task in tasks:
        unknown = set(task.depends_on) - by_id.keys()
        if unknown:
            raise PlanError(f"{task.id}: unknown dependencies: {', '.join(sorted(unknown))}")

    ordered: list[Task] = []
    remaining = {task.id: set(task.depends_on) for task in tasks}
    while remaining:
        ready = [task.id for task in tasks if task.id in remaining and not remaining[task.id]]
        if not ready:
            raise PlanError("dependency cycle detected")
        for task_id in ready:
            ordered.append(by_id[task_id])
            del remaining[task_id]
            for deps in remaining.values():
                deps.discard(task_id)
    return ordered


def validate_path_ownership(tasks: list[Task]) -> None:
    owners: list[tuple[str, str]] = []
    for task in tasks:
        for path in task.files:
            for previous_path, previous_task in owners:
                if path == previous_path or path.startswith(previous_path + "/") or previous_path.startswith(path + "/"):
                    raise PlanError(
                        f"overlapping file ownership: {previous_task} ({previous_path}) and "
                        f"{task.id} ({path})"
                    )
            owners.append((path, task.id))


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PlanError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def resolve_clean_base(repo: Path, base: str) -> tuple[Path, str]:
    repo = repo.expanduser().resolve()
    root = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    if root != repo:
        raise PlanError(f"--repo must be the repository root, not a subdirectory: {root}")
    dirty = git(repo, "status", "--porcelain")
    if dirty:
        raise PlanError("repository has uncommitted changes; commit/stash them before preparing workers")
    sha = git(repo, "rev-parse", "--verify", f"{base}^{{commit}}")
    return repo, sha


def prepare_worktrees(repo: Path, tasks: list[Task], base: str, output_root: Path) -> list[dict[str, str]]:
    repo, base_sha = resolve_clean_base(repo, base)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output_root = output_root.expanduser().resolve()
    if output_root == repo or repo in output_root.parents:
        raise PlanError("worktree output must be outside the target repository")
    run_root = output_root / run_id
    run_root.mkdir(parents=True, exist_ok=False)
    created: list[dict[str, str]] = []
    for task in validate_task_graph(tasks):
        branch = f"openhands/{run_id}/{task.id}"
        worktree = run_root / task.id
        command = ["git", "-C", str(repo), "worktree", "add", "-b", branch, str(worktree), base_sha]
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        if result.returncode:
            details = result.stderr.strip() or result.stdout.strip()
            already = ", ".join(f"{item['id']}={item['worktree']} ({item['branch']})" for item in created)
            raise PlanError(
                f"worktree setup stopped at {task.id}: {details}. Previously created worktrees were preserved: "
                f"{already or 'none'}"
            )
        created.append({"id": task.id, "branch": branch, "worktree": str(worktree), "base_sha": base_sha})
    return created


def command_validate(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    ordered = validate_task_graph(tasks)
    print(f"Valid task plan: {len(tasks)} task(s); dependency order: {' -> '.join(t.id for t in ordered)}")
    print("File ownership is disjoint. No task-supplied shell commands are accepted.")
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    tasks = load_tasks(args.tasks)
    created = prepare_worktrees(args.repo, tasks, args.base, args.output)
    print(json.dumps({"base": args.base, "worktrees": created}, indent=2))
    print("Worktrees prepared only; no agents were launched and no branches were merged or pushed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a task plan without changing Git state")
    validate.add_argument("tasks", type=Path)
    validate.set_defaults(func=command_validate)
    prepare = sub.add_parser("prepare", help="create one branch and worktree per validated task")
    prepare.add_argument("--repo", type=Path, required=True, help="clean repository root")
    prepare.add_argument("--tasks", type=Path, required=True)
    prepare.add_argument("--base", required=True, help="base branch or commit")
    prepare.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "worktrees")
    prepare.set_defaults(func=command_prepare)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except PlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
