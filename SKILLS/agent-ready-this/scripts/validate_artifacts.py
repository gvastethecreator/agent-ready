#!/usr/bin/env python3
"""Structural validation for common agent-ready-this artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
QUESTION_ID_RE = re.compile(r"^G-[0-9]{2}$")


def issue(severity: str, path: Path | str, message: str) -> dict[str, Any]:
    return {"severity": severity, "path": str(path), "message": message}


def read_json(path: Path) -> tuple[Any | None, list[dict[str, Any]]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as exc:
        return None, [issue("error", path, f"Invalid JSON: {exc}")]


def check_skill(path: Path) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [issue("error", path, str(exc))]
    if not text.startswith("---\n"):
        issues.append(issue("error", path, "SKILL.md must start with YAML frontmatter."))
        return issues
    end = text.find("\n---\n", 4)
    if end < 0:
        issues.append(issue("error", path, "SKILL.md frontmatter is not closed."))
        return issues
    fm = text[4:end]
    fields: dict[str, str] = {}
    for line in fm.splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"\'')
    name = fields.get("name", "")
    desc = fields.get("description", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        issues.append(issue("error", path, f"Invalid skill name: {name!r}"))
    if path.parent.name != name:
        issues.append(issue("error", path, "Skill name must match parent directory."))
    if not desc or len(desc) > 1024:
        issues.append(issue("error", path, "Description is missing or exceeds 1024 characters."))
    return issues


def check_recommendations(path: Path) -> list[dict[str, Any]]:
    data, issues = read_json(path)
    if issues or not isinstance(data, dict):
        return issues
    for key in ("schema_version", "source_audit", "phase", "summary", "recommendations"):
        if key not in data:
            issues.append(issue("error", path, f"Missing recommendations field: {key}"))
    recs = data.get("recommendations", [])
    if not isinstance(recs, list):
        issues.append(issue("error", path, "recommendations must be an array."))
        return issues
    ids: set[str] = set()
    for index, item in enumerate(recs):
        if not isinstance(item, dict):
            issues.append(issue("error", path, f"Recommendation {index} is not an object."))
            continue
        rec_id = item.get("id")
        if not isinstance(rec_id, str) or not NAME_RE.fullmatch(rec_id):
            issues.append(issue("error", path, f"Recommendation {index} has invalid id: {rec_id!r}"))
        elif rec_id in ids:
            issues.append(issue("error", path, f"Duplicate recommendation id: {rec_id}"))
        else:
            ids.add(rec_id)
        for field in ("applicability", "action", "priority", "confidence", "reason", "acceptance_criteria"):
            if field not in item:
                issues.append(issue("error", path, f"Recommendation {rec_id or index} is missing {field}."))
    return issues


def check_grill(path: Path) -> list[dict[str, Any]]:
    data, issues = read_json(path)
    if issues or not isinstance(data, dict):
        return issues
    gate = data.get("gate")
    questions = data.get("questions")
    if not isinstance(gate, dict):
        issues.append(issue("error", path, "gate must be an object."))
    elif gate.get("status") not in {"skipped", "useful", "required", "completed"}:
        issues.append(issue("error", path, f"Invalid Grill Gate status: {gate.get('status')!r}"))
    if not isinstance(questions, list):
        issues.append(issue("error", path, "questions must be an array."))
        return issues
    ids: set[str] = set()
    for index, question in enumerate(questions):
        if not isinstance(question, dict):
            issues.append(issue("error", path, f"Question {index} is not an object."))
            continue
        question_id = question.get("id")
        if not isinstance(question_id, str) or not QUESTION_ID_RE.fullmatch(question_id):
            issues.append(issue("error", path, f"Question {index} has invalid id: {question_id!r}"))
        elif question_id in ids:
            issues.append(issue("error", path, f"Duplicate Grill question id: {question_id}"))
        else:
            ids.add(question_id)
        if question.get("severity") not in {"blocking", "major", "minor"}:
            issues.append(issue("error", path, f"Question {question_id or index} has invalid severity."))
        if not question.get("affects") and question.get("topic") != "success_criteria":
            issues.append(issue("warning", path, f"Question {question_id or index} does not identify an affected recommendation."))
    if isinstance(gate, dict) and gate.get("status") == "skipped" and questions:
        issues.append(issue("error", path, "A skipped Grill Gate must not contain pending questions."))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--report")
    args = parser.parse_args()
    root = Path(args.repo).resolve()
    issues: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    agents = sorted(root.rglob("AGENTS.md"))
    checks.append({"id": "agents-md-present", "passed": bool(agents), "paths": [str(p.relative_to(root)) for p in agents]})
    if not agents:
        issues.append(issue("warning", ".", "No AGENTS.md found."))

    skills = sorted(root.rglob("SKILL.md"))
    for skill in skills:
        if any(part in {"node_modules", ".git", "dist", "build"} for part in skill.parts):
            continue
        issues.extend(check_skill(skill))
    checks.append({"id": "skill-frontmatter", "passed": not any(i["severity"] == "error" and i["path"].endswith("SKILL.md") for i in issues), "count": len(skills)})

    llms_files = sorted(root.rglob("llms.txt"))
    for path in llms_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.lstrip().startswith("# "):
            issues.append(issue("error", path.relative_to(root), "llms.txt should start with one H1 title."))
        if "](http" not in text and "](/" not in text:
            issues.append(issue("warning", path.relative_to(root), "llms.txt contains no obvious links."))
    checks.append({"id": "llms-txt-structure", "passed": not any(i["severity"] == "error" and i["path"].endswith("llms.txt") for i in issues), "count": len(llms_files)})

    for candidate in list(root.rglob("agent-card.json")) + list(root.rglob("ai-catalog.json")):
        _, parse_issues = read_json(candidate)
        issues.extend(parse_issues)

    recommendation_files = sorted(
        path for path in root.rglob("recommendations*.json")
        if "schemas" not in path.parts and not path.name.endswith(".schema.json")
    )
    for path in recommendation_files:
        issues.extend(check_recommendations(path))
    checks.append({"id": "recommendation-structure", "passed": not any(i["severity"] == "error" and "recommendation" in i["message"].lower() for i in issues), "count": len(recommendation_files)})

    grill_files = sorted(
        path for path in root.rglob("grill-session.json")
        if "schemas" not in path.parts and not path.name.endswith(".schema.json")
    )
    for path in grill_files:
        issues.extend(check_grill(path))
    checks.append({"id": "grill-session-structure", "passed": not any(i["severity"] == "error" and ("grill" in i["message"].lower() or "question" in i["message"].lower()) for i in issues), "count": len(grill_files)})

    for path in root.rglob("*.ts"):
        try:
            if path.stat().st_size > 1_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "modelContext.registerTool" in text or "modelContext?.registerTool" in text:
            if "typeof document.modelContext" not in text:
                issues.append(issue("warning", path.relative_to(root), "WebMCP registration may lack explicit feature detection."))

    result = {
        "schema_version": 1,
        "generator": "agent-ready-this@0.3.0-plan",
        "repository": str(root),
        "checks": checks,
        "issues": issues,
        "passed": not any(i["severity"] == "error" for i in issues),
        "limitations": [
            "This validator performs structural checks only.",
            "Use official schemas and project-specific functional/security tests before runtime publication.",
        ],
    }
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
