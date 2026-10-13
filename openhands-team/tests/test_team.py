from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from team import PlanError, load_tasks, prepare_worktrees, validate_task_graph  # noqa: E402


def task(task_id: str, files: list[str], depends_on: list[str] | None = None) -> dict[str, object]:
    return {
        "id": task_id,
        "title": f"Task {task_id}",
        "description": "Implement the scoped change.",
        "files": files,
        "depends_on": depends_on or [],
        "acceptance_criteria": ["Relevant tests pass", "Changes are committed"],
    }


class PlanValidationTests(unittest.TestCase):
    def load(self, tasks: list[dict[str, object]]) -> list:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.json"
            path.write_text(json.dumps(tasks), encoding="utf-8")
            return load_tasks(path)

    def test_valid_plan_and_dependency_order(self) -> None:
        tasks = self.load([
            task("second", ["src/b"], ["first"]),
            task("first", ["src/a"]),
        ])
        self.assertEqual([item.id for item in validate_task_graph(tasks)], ["first", "second"])

    def test_rejects_parent_child_path_overlap(self) -> None:
        with self.assertRaisesRegex(PlanError, "overlapping file ownership"):
            self.load([task("alpha", ["src"]), task("beta", ["src/ui"])])

    def test_rejects_path_traversal(self) -> None:
        with self.assertRaisesRegex(PlanError, "unsafe allowed path"):
            self.load([task("alpha", ["../outside"])])

    def test_rejects_windows_absolute_path(self) -> None:
        with self.assertRaisesRegex(PlanError, "repository-relative POSIX"):
            self.load([task("alpha", ["C:\\outside\\src"])])

    def test_rejects_unknown_dependency(self) -> None:
        with self.assertRaisesRegex(PlanError, "unknown dependencies"):
            self.load([task("alpha", ["src/a"], ["missing"])])

    def test_rejects_dependency_cycle(self) -> None:
        with self.assertRaisesRegex(PlanError, "dependency cycle"):
            self.load([task("alpha", ["src/a"], ["beta"]), task("beta", ["src/b"], ["alpha"])])

    def test_rejects_unrecognized_shell_command_field(self) -> None:
        bad = task("alpha", ["src/a"])
        bad["test_command"] = "rm -rf /"
        with self.assertRaisesRegex(PlanError, "unsupported fields"):
            self.load([bad])


class WorktreePreparationTests(unittest.TestCase):
    def test_prepares_distinct_worktrees_at_same_base(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            (repo / "README.md").write_text("fixture\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            base = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
            ).stdout.strip()
            tasks_path = root / "tasks.json"
            tasks_path.write_text(json.dumps([task("one", ["src/one"]), task("two", ["src/two"])]), encoding="utf-8")
            tasks = load_tasks(tasks_path)

            created = prepare_worktrees(repo, tasks, "HEAD", root / "worktrees")

            self.assertEqual(len(created), 2)
            self.assertEqual({item["base_sha"] for item in created}, {base})
            self.assertNotEqual(created[0]["branch"], created[1]["branch"])
            for item in created:
                self.assertTrue(Path(item["worktree"]).is_dir())
                head = subprocess.run(
                    ["git", "-C", item["worktree"], "rev-parse", "HEAD"], check=True, capture_output=True, text=True
                ).stdout.strip()
                self.assertEqual(head, base)

    def test_refuses_dirty_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            (repo / "tracked.txt").write_text("dirty\n", encoding="utf-8")
            tasks_path = Path(directory) / "tasks.json"
            tasks_path.write_text(json.dumps([task("one", ["src/one"])]), encoding="utf-8")
            with self.assertRaisesRegex(PlanError, "uncommitted changes"):
                prepare_worktrees(repo, load_tasks(tasks_path), "HEAD", Path(directory) / "worktrees")

    def test_refuses_worktree_directory_inside_target_repo(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            (repo / "tracked.txt").write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
            tasks_path = Path(directory) / "tasks.json"
            tasks_path.write_text(json.dumps([task("one", ["src/one"])]), encoding="utf-8")
            with self.assertRaisesRegex(PlanError, "outside the target repository"):
                prepare_worktrees(repo, load_tasks(tasks_path), "HEAD", repo / "openhands-team")


if __name__ == "__main__":
    unittest.main()
