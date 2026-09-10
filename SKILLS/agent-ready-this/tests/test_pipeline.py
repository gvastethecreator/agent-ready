from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSESS = ROOT / "scripts" / "assess_project.py"


class AssessmentPipelineTests(unittest.TestCase):
    def run_assessment(self, repo: Path, output: Path, *extra: str) -> dict:
        subprocess.run(
            [sys.executable, str(ASSESS), "--repo", str(repo), "--output-dir", str(output), *extra],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads((output / "grill-session.json").read_text(encoding="utf-8"))

    def test_complete_simple_project_skips_grill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            out = base / "out"
            repo.mkdir()
            (repo / "README.md").write_text("# Fixture\n", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "fixture",
                        "private": True,
                        "scripts": {
                            "build": "echo build",
                            "lint": "echo lint",
                            "typecheck": "echo types",
                            "test": "echo test",
                        },
                    }
                ),
                encoding="utf-8",
            )
            for directory in (".scratch/brainstorming/demo", ".agent-ready/old"):
                artifact = repo / directory
                artifact.mkdir(parents=True)
                (artifact / "package.json").write_text(
                    json.dumps({"dependencies": {"next": "1.0.0", "better-auth": "1.0.0"}}),
                    encoding="utf-8",
                )
            grill = self.run_assessment(repo, out, "--target-vendor", "codex")
            audit = json.loads((out / "audit.json").read_text(encoding="utf-8"))
            self.assertEqual(len(audit["inventory"]["package_json"]["packages"]), 1)
            self.assertFalse(audit["signals"]["web_candidate"])
            self.assertEqual(grill["gate"]["status"], "skipped")
            self.assertEqual(grill["questions"], [])

    def test_sensitive_remote_runtime_requires_grill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            out = base / "out"
            route = repo / "src" / "app" / "api" / "projects"
            route.mkdir(parents=True)
            (route / "route.ts").write_text("export const POST = () => new Response('ok')\n", encoding="utf-8")
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "runtime-fixture",
                        "private": True,
                        "scripts": {
                            "build": "echo build",
                            "lint": "echo lint",
                            "typecheck": "echo types",
                            "test": "echo test",
                        },
                        "dependencies": {
                            "next": "1.0.0",
                            "react": "1.0.0",
                            "better-auth": "1.0.0",
                            "@prisma/client": "1.0.0",
                        },
                    }
                ),
                encoding="utf-8",
            )
            grill = self.run_assessment(repo, out, "--headless-actions", "--sensitive-actions")
            self.assertEqual(grill["gate"]["status"], "required")
            question_ids = {item["id"] for item in grill["questions"]}
            self.assertIn("G-12", question_ids)
            self.assertIn("G-13", question_ids)
            self.assertTrue(grill["gate"]["safe_work_can_proceed"])
            self.assertEqual(len(grill["next_round"]), 1)

    def test_known_topics_are_not_reasked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            out = base / "out"
            repo.mkdir()
            (repo / "package.json").write_text(
                json.dumps(
                    {
                        "name": "fixture",
                        "private": True,
                        "scripts": {
                            "build": "echo build",
                            "lint": "echo lint",
                            "typecheck": "echo types",
                            "test": "echo test",
                        },
                        "dependencies": {"next": "1.0.0", "better-auth": "1.0.0"},
                    }
                ),
                encoding="utf-8",
            )
            context = base / "known.json"
            context.write_text(
                json.dumps({"known_topics": ["authz_model", "mutation_policy"]}),
                encoding="utf-8",
            )
            grill = self.run_assessment(
                repo,
                out,
                "--headless-actions",
                "--sensitive-actions",
                "--known-context",
                str(context),
            )
            topics = {item["topic"] for item in grill["questions"]}
            self.assertNotIn("authz_model", topics)
            self.assertNotIn("mutation_policy", topics)
            self.assertEqual(set(grill["suppressed_topics"]), {"authz_model", "mutation_policy"})

    def test_schema_answers_suppress_only_settled_questions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            repo.mkdir()
            context = base / "known.json"
            context.write_text(json.dumps({"answers": [
                {"question_id": "G-12", "status": "answered", "value": "Resource authorization verified",
                 "source": "explicit-user-answer"},
                {"question_id": "G-13", "status": "deferred", "source": "deferred"},
            ]}), encoding="utf-8")
            grill = self.run_assessment(repo, base / "out", "--headless-actions",
                                        "--sensitive-actions", "--known-context", str(context))
            topics = {question["topic"] for question in grill["questions"]}
            self.assertNotIn("authz_model", topics)
            self.assertIn("mutation_policy", topics)
            self.assertEqual(grill["suppressed_topics"], ["authz_model"])
            self.assertEqual(grill["gate"]["status"], "required")

    def test_disabled_grill_keeps_blocking_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            repo.mkdir()
            out = base / "out"
            grill = self.run_assessment(repo, out, "--headless-actions",
                                        "--sensitive-actions", "--grill-mode", "off")
            self.assertEqual(grill["gate"]["status"], "required")
            self.assertIn("G-12", grill["gate"]["blocking_question_ids"])
            self.assertIn("G-13", grill["gate"]["blocking_question_ids"])
            self.assertEqual(grill["next_round"], [])
            report = (out / "assessment.md").read_text(encoding="utf-8")
            self.assertIn("unresolved decisions remain", report)
            self.assertNotIn("no unanswered material decision", report)

    def test_existing_assessment_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            repo.mkdir()
            out = base / "out"
            out.mkdir()
            original = b"Keep the prior audit and its evidence."
            (out / "audit.json").write_bytes(original)
            result = subprocess.run(
                [sys.executable, str(ASSESS), "--repo", str(repo), "--output-dir", str(out)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Cannot create a new assessment directory", result.stderr)
            self.assertEqual((out / "audit.json").read_bytes(), original)
            self.assertEqual([path.name for path in out.iterdir()], ["audit.json"])


if __name__ == "__main__":
    unittest.main()
