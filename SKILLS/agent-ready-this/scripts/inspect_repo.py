#!/usr/bin/env python3
"""Read-only repository inventory for the agent-ready-this assessment scaffold."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

SKIP_DIRS = {
    ".git",
    ".scratch",
    ".agent-ready",
    ".hg",
    ".svn",
    "node_modules",
    ".next",
    "dist",
    "build",
    "coverage",
    ".turbo",
    ".cache",
    ".venv",
    "venv",
    "__pycache__",
    "target",
    ".idea",
    ".gradle",
    ".parcel-cache",
}
MAX_FILES = 50_000
MAX_TEXT_SCAN_BYTES = 1_000_000
GENERATOR = "agent-ready-this@0.3.0-plan"

QUALITY_SCRIPT_ALIASES: dict[str, tuple[str, ...]] = {
    "build": ("build", "compile"),
    "lint": ("lint", "check:lint"),
    "typecheck": ("typecheck", "type-check", "check:types", "types"),
    "test": ("test", "test:unit", "test:ci", "check:test"),
    "e2e": ("test:e2e", "e2e", "playwright", "cypress"),
    "format": ("format", "format:check", "check:format"),
    "dev": ("dev", "start:dev"),
}
# Scripts that run a type checker satisfy the typecheck gate even under another name.
TYPECHECK_COMMAND = re.compile(r"(?<![\w-])(tsc|vue-tsc|svelte-check|astro check)(?![\w-])")
TASK_RUNNER_FILES = ("Makefile", "makefile", "GNUmakefile", "justfile", "Justfile")
TASK_TARGET = re.compile(r"^([A-Za-z0-9][\w.-]*)(?:\s+[^:=\n]*)?:(?!=)", re.M)
# Commands implied by a stack manifest; unverified until run.
STACK_CONVENTIONS: dict[str, list[tuple[str, str, str | None]]] = {
    "Cargo.toml": [
        ("build", "cargo build", None),
        ("typecheck", "cargo check", None),
        ("lint", "cargo clippy", None),
        ("test", "cargo test", None),
        ("format", "cargo fmt --check", None),
    ],
    "go.mod": [
        ("build", "go build ./...", None),
        ("typecheck", "go build ./...", None),
        ("lint", "go vet ./...", None),
        ("test", "go test ./...", None),
    ],
    "pyproject.toml": [
        ("build", "python -m build", "[build-system]"),
        ("test", "pytest", "pytest"),
        ("lint", "ruff check", "ruff"),
        ("format", "ruff format --check", "ruff"),
        ("typecheck", "mypy", "mypy"),
        ("typecheck", "pyright", "pyright"),
    ],
}
# A manifest alone does not make a server; look for a web framework dependency.
SERVER_MANIFEST_MARKERS: dict[str, tuple[str, ...]] = {
    "Cargo.toml": ("axum", "actix-web", "rocket", "warp", "poem", "salvo", "tide"),
    "pyproject.toml": ("fastapi", "flask", "django", "starlette", "aiohttp", "litestar", "sanic"),
    "requirements.txt": ("fastapi", "flask", "django", "starlette", "aiohttp", "litestar", "sanic"),
    "go.mod": ("gin-gonic/gin", "labstack/echo", "gofiber/fiber", "go-chi/chi", "gorilla/mux"),
    "pom.xml": ("spring-boot-starter-web", "quarkus", "micronaut"),
    "build.gradle": ("spring-boot-starter-web", "ktor-server"),
    "build.gradle.kts": ("spring-boot-starter-web", "ktor-server"),
}
SITE_DEPENDENCIES = {
    "astro", "@astrojs/starlight", "@docusaurus/core", "vitepress", "vuepress", "nextra", "fumadocs-core",
    "gatsby", "@11ty/eleventy", "hexo", "@next/mdx", "next-mdx-remote", "contentlayer",
}
SITE_CONFIG_FILES = {
    "mkdocs.yml", "mkdocs.yaml", "book.toml", "hugo.toml", "hugo.yaml", "_config.yml",
    "docusaurus.config.js", "docusaurus.config.ts", "astro.config.mjs", "astro.config.ts",
}

AUTH_DEPENDENCIES = {
    "next-auth",
    "@auth/core",
    "@auth/express",
    "better-auth",
    "@clerk/nextjs",
    "@clerk/backend",
    "passport",
    "passport-local",
    "firebase",
    "firebase-admin",
    "lucia",
    "@supabase/supabase-js",
    "@auth0/nextjs-auth0",
    "auth0",
    "jsonwebtoken",
    "jose",
}

DATABASE_DEPENDENCIES = {
    "prisma",
    "@prisma/client",
    "drizzle-orm",
    "mongoose",
    "mongodb",
    "pg",
    "postgres",
    "mysql2",
    "better-sqlite3",
    "sqlite3",
    "@supabase/supabase-js",
    "@neondatabase/serverless",
    "typeorm",
    "sequelize",
}

TEST_DEPENDENCIES = {
    "vitest",
    "jest",
    "@jest/core",
    "@playwright/test",
    "playwright",
    "cypress",
    "mocha",
    "ava",
    "pytest",
}

EVENT_DEPENDENCIES = {
    "kafkajs",
    "amqplib",
    "bullmq",
    "@aws-sdk/client-sqs",
    "@google-cloud/pubsub",
    "nats",
    "redis",
    "ioredis",
}

SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".npmrc",
    "service-account.json",
    "credentials.json",
}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def safe_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def walk_files(root: Path) -> list[Path]:
    result: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current)
        for name in files:
            result.append(base / name)
            if len(result) >= MAX_FILES:
                return result
    return result


def run_git(root: Path, *args: str, timeout: int = 10) -> str | None:
    try:
        cp = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return cp.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def git_info(root: Path) -> dict[str, Any]:
    top = run_git(root, "rev-parse", "--show-toplevel")
    status = run_git(root, "status", "--porcelain=v1") if top else None
    branch = run_git(root, "branch", "--show-current") if top else None
    tracked = run_git(root, "ls-files") if top else None
    tracked_sensitive: list[str] = []
    if tracked:
        for item in tracked.splitlines():
            path = Path(item)
            lower = item.lower()
            if path.name in SENSITIVE_FILENAMES or lower.endswith((".pem", ".p12", ".pfx", ".key")):
                tracked_sensitive.append(item)
    return {
        "is_git_repository": bool(top),
        "top_level": top,
        "branch": branch,
        "dirty": bool(status) if status is not None else None,
        "changed_entries": len(status.splitlines()) if status else 0,
        "tracked_sensitive_paths": tracked_sensitive[:100],
    }


def package_json_facts(files: Iterable[Path], root: Path) -> dict[str, Any]:
    packages: list[dict[str, Any]] = []
    dependency_names: set[str] = set()
    scripts: dict[str, list[dict[str, str]]] = {}
    workspace_evidence: list[str] = []

    for path in files:
        if path.name != "package.json":
            continue
        data = safe_json(path)
        if not data:
            continue
        package_scripts = data.get("scripts") if isinstance(data.get("scripts"), dict) else {}
        item = {
            "path": rel(path, root),
            "name": data.get("name"),
            "private": data.get("private"),
            "scripts": package_scripts,
        }
        packages.append(item)
        if data.get("workspaces"):
            workspace_evidence.append(rel(path, root) + "#workspaces")
        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            deps = data.get(section)
            if isinstance(deps, dict):
                dependency_names.update(str(k) for k in deps)
        for key, value in package_scripts.items():
            if isinstance(value, str):
                scripts.setdefault(str(key), []).append({"path": rel(path, root), "command": value})

    return {
        "packages": packages,
        "dependencies": sorted(dependency_names),
        "scripts": scripts,
        "workspace_evidence": workspace_evidence,
    }


def detect_frameworks(deps: set[str], names: set[str]) -> list[str]:
    candidates = {
        "next": "Next.js",
        "react": "React",
        "vue": "Vue",
        "nuxt": "Nuxt",
        "@angular/core": "Angular",
        "svelte": "Svelte",
        "@sveltejs/kit": "SvelteKit",
        "astro": "Astro",
        "gatsby": "Gatsby",
        "@remix-run/react": "Remix",
        "express": "Express",
        "fastify": "Fastify",
        "hono": "Hono",
        "@nestjs/core": "NestJS",
        "electron": "Electron",
        "@tauri-apps/api": "Tauri",
        "phaser": "Phaser",
        "three": "Three.js",
    }
    found = {label for dep, label in candidates.items() if dep in deps}
    if {"vite.config.ts", "vite.config.js", "vite.config.mjs"} & names:
        found.add("Vite")
    return sorted(found)


def select_dependencies(deps: set[str], known: set[str]) -> list[str]:
    return sorted(deps & known)


def capability_for(name: str) -> str | None:
    for capability, aliases in QUALITY_SCRIPT_ALIASES.items():
        if name in aliases or any(name.startswith(alias + ":") for alias in aliases):
            return capability
    return None


def task_runner_candidates(root: Path) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for filename in TASK_RUNNER_FILES:
        path = root / filename
        if not path.is_file() or path.stat().st_size > MAX_TEXT_SCAN_BYTES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for target in dict.fromkeys(TASK_TARGET.findall(text)):
            capability = capability_for(target)
            if capability:
                candidates.append({"capability": capability, "script": target, "path": filename,
                                   "command": f"{'make' if 'make' in filename.lower() else 'just'} {target}",
                                   "source": "task-runner", "evidence": f"{filename}#{target}"})
    return candidates


def stack_convention_candidates(root: Path) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for manifest, commands in STACK_CONVENTIONS.items():
        path = root / manifest
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore") if path.stat().st_size <= MAX_TEXT_SCAN_BYTES else ""
        for capability, command, marker in commands:
            if marker is None or marker in text:
                candidates.append({"capability": capability, "script": command, "path": manifest, "command": command,
                                   "source": "convention", "evidence": f"{manifest} (convention: {command})"})
    return candidates


def quality_command_facts(scripts: dict[str, list[dict[str, str]]], extra: list[dict[str, str]]) -> dict[str, Any]:
    found: dict[str, list[dict[str, str]]] = {}
    for name, items in scripts.items():
        capability = capability_for(name)
        for item in items:
            match = {"script": name, **item, "source": "package-script",
                     "evidence": f"{item['path']}#scripts.{name}"}
            if capability:
                found.setdefault(capability, []).append(match)
            if capability != "typecheck" and TYPECHECK_COMMAND.search(item["command"]):
                found.setdefault("typecheck", []).append({**match, "note": "type checker runs inside this script"})
    for candidate in extra:
        capability = candidate["capability"]
        found.setdefault(capability, []).append({k: v for k, v in candidate.items() if k != "capability"})
    core = ("build", "lint", "typecheck", "test")
    missing = [name for name in core if name not in found]
    convention_only = sorted(
        name for name in core
        if name in found and all(match["source"] == "convention" for match in found[name])
    )
    return {
        "found": found,
        "missing_core": missing,
        "convention_only": convention_only,
        "core_coverage": len(core) - len(missing),
        "core_total": len(core),
    }


def first_existing(rel_paths: set[str], candidates: tuple[str, ...]) -> str | None:
    return next((candidate for candidate in candidates if candidate in rel_paths), None)


def detect_vendor_paths(rel_paths: set[str]) -> dict[str, list[str]]:
    def named(p: str, filename: str) -> bool:
        return Path(p).name.lower() == filename

    rules = {
        "canonical": lambda p: named(p, "agents.md") or "/skills/" in f"/{p}",
        "claude": lambda p: named(p, "claude.md") or p.startswith(".claude/"),
        "cursor": lambda p: p.startswith(".cursor/") or p == ".cursorrules",
        "github-copilot": lambda p: p == ".github/copilot-instructions.md" or p.startswith(".github/instructions/") or p.startswith(".github/agents/"),
        "opencode": lambda p: p.startswith(".opencode/") or p in {"opencode.json", "opencode.jsonc"},
        "gemini": lambda p: named(p, "gemini.md") or p.startswith(".gemini/"),
        "windsurf": lambda p: p.startswith(".windsurf/") or p == ".windsurfrules",
        "cline": lambda p: p.startswith(".clinerules/") or p == ".clinerules",
        "aider": lambda p: p.startswith(".aider") or p == "CONVENTIONS.md",
    }
    return {
        vendor: sorted(p for p in rel_paths if predicate(p))
        for vendor, predicate in rules.items()
        if any(predicate(p) for p in rel_paths)
    }


def bounded_text_contains(path: Path, needles: tuple[str, ...]) -> bool:
    try:
        if path.stat().st_size > MAX_TEXT_SCAN_BYTES:
            return False
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return all(needle in text for needle in needles)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()

    root = Path(args.repo).resolve()
    if not root.is_dir():
        raise SystemExit(f"Repository path is not a directory: {root}")

    files = walk_files(root)
    names = {p.name for p in files}
    rel_paths = {rel(p, root) for p in files}
    pkg = package_json_facts(files, root)
    deps = set(pkg["dependencies"])
    git = git_info(root)

    lockfiles = sorted(
        n
        for n in names
        if n
        in {
            "pnpm-lock.yaml",
            "package-lock.json",
            "yarn.lock",
            "bun.lock",
            "bun.lockb",
            "uv.lock",
            "poetry.lock",
            "Pipfile.lock",
            "Cargo.lock",
            "go.sum",
            "composer.lock",
        }
    )

    ext_map = {
        "TypeScript": {".ts", ".tsx", ".mts", ".cts"},
        "JavaScript": {".js", ".jsx", ".mjs", ".cjs"},
        "Python": {".py"},
        "Rust": {".rs"},
        "Go": {".go"},
        "Java": {".java"},
        "Kotlin": {".kt", ".kts"},
        "C#": {".cs"},
        "Ruby": {".rb"},
        "PHP": {".php"},
        "Swift": {".swift"},
    }
    suffixes = {p.suffix.lower() for p in files}
    languages = sorted(language for language, exts in ext_map.items() if suffixes & exts)

    monorepo_evidence = list(pkg["workspace_evidence"])
    for candidate in (
        "pnpm-workspace.yaml",
        "turbo.json",
        "nx.json",
        "lerna.json",
        "WORKSPACE",
        "MODULE.bazel",
    ):
        if candidate in names:
            monorepo_evidence.append(candidate)

    docs = {
        "readme": first_existing(rel_paths, ("README.md", "README.mdx", "README.rst")),
        "contributing": first_existing(rel_paths, ("CONTRIBUTING.md", ".github/CONTRIBUTING.md")),
        "architecture": first_existing(rel_paths, ("ARCHITECTURE.md", "docs/ARCHITECTURE.md", "docs/architecture.md")),
        "security": first_existing(rel_paths, ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md")),
        "codeowners": first_existing(rel_paths, ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")),
        "license": first_existing(rel_paths, ("LICENSE", "LICENSE.md", "COPYING")),
        "env_example": first_existing(rel_paths, (".env.example", ".env.sample", ".env.template")),
    }

    frameworks = detect_frameworks(deps, names)
    web_frameworks = {
        "Next.js",
        "React",
        "Vue",
        "Nuxt",
        "Angular",
        "Svelte",
        "SvelteKit",
        "Astro",
        "Gatsby",
        "Remix",
        "Vite",
    }
    server_frameworks = {
        "Next.js",
        "Nuxt",
        "SvelteKit",
        "Remix",
        "Express",
        "Fastify",
        "Hono",
        "NestJS",
    }

    ci_paths = sorted(
        p
        for p in rel_paths
        if p.startswith(".github/workflows/")
        or p in {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml"}
    )

    api_route_paths = sorted(
        p
        for p in rel_paths
        if any(
            marker in f"/{p.lower()}"
            for marker in (
                "/app/api/",
                "/pages/api/",
                "/src/app/api/",
                "/routes/",
                "/controllers/",
                "/api/",
            )
        )
        and Path(p).suffix.lower() in {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java", ".cs"}
    )[:250]

    test_paths = sorted(
        p
        for p in rel_paths
        if (
            any(part in {"test", "tests", "__tests__", "e2e", "spec"} for part in Path(p).parts)
            or Path(p).name.lower().endswith((".test.ts", ".test.tsx", ".test.js", ".spec.ts", ".spec.js", "_test.py"))
        )
    )[:250]

    integration_signals = {
        "llms_txt": sorted(p for p in rel_paths if p.endswith("llms.txt")),
        "openapi": sorted(p for p in rel_paths if "openapi" in p.lower() and Path(p).suffix.lower() in {".json", ".yaml", ".yml"}),
        "arazzo": sorted(p for p in rel_paths if "arazzo" in p.lower() and Path(p).suffix.lower() in {".json", ".yaml", ".yml"}),
        "asyncapi": sorted(p for p in rel_paths if "asyncapi" in p.lower() and Path(p).suffix.lower() in {".json", ".yaml", ".yml"}),
        "a2a_agent_card": sorted(p for p in rel_paths if p.endswith(".well-known/agent-card.json") or p.endswith("agent-card.json")),
        "ard_catalog": sorted(p for p in rel_paths if p.endswith(".well-known/ai-catalog.json") or p.endswith("ai-catalog.json")),
        "mcp_dependencies": sorted(d for d in deps if "modelcontextprotocol" in d.lower() or d.lower() == "mcp"),
        "webmcp_code_mentions": [],
    }

    for path in files:
        if path.suffix.lower() not in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".html"}:
            continue
        if bounded_text_contains(path, ("modelContext", "registerTool")):
            integration_signals["webmcp_code_mentions"].append(rel(path, root))

    vendor_paths = detect_vendor_paths(rel_paths)
    agent_paths = sorted({path for paths in vendor_paths.values() for path in paths})
    quality = quality_command_facts(pkg["scripts"], task_runner_candidates(root) + stack_convention_candidates(root))
    auth_dependencies = select_dependencies(deps, AUTH_DEPENDENCIES)
    database_dependencies = select_dependencies(deps, DATABASE_DEPENDENCIES)
    test_dependencies = select_dependencies(deps, TEST_DEPENDENCIES)
    event_dependencies = select_dependencies(deps, EVENT_DEPENDENCIES)

    # Markdown under docs/ is often internal; require a site generator before assuming public content.
    site_generator_evidence = sorted((deps & SITE_DEPENDENCIES) | (names & SITE_CONFIG_FILES))
    public_content_candidate = bool(site_generator_evidence) and any(
        p.endswith((".md", ".mdx"))
        and any(part in {"docs", "content", "pages", "posts"} for part in Path(p).parts[:-1])
        for p in rel_paths
    )
    server_manifest_evidence = []
    for path in files:
        markers = SERVER_MANIFEST_MARKERS.get(path.name)
        if markers and any(bounded_text_contains(path, (marker,)) for marker in markers):
            server_manifest_evidence.append(rel(path, root))
    web_candidate = bool(set(frameworks) & web_frameworks)
    server_candidate = bool(set(frameworks) & server_frameworks or server_manifest_evidence or api_route_paths)

    warnings = [
        "Heuristic inventory only; verify high-impact findings in source files.",
        "Scratch and prior assessment directories are excluded. Commands come from package scripts, root Makefile or "
        "justfile targets, and Cargo, Go, or Python conventions; convention commands are unverified until run.",
        "The inspector does not execute commands, inspect secret values, or prove authorization behavior.",
    ]
    if git["tracked_sensitive_paths"]:
        warnings.append("Potentially sensitive filenames are tracked by Git; inspect them without copying values into reports.")
    if len(files) >= MAX_FILES:
        warnings.append("File scan reached the configured limit; inventory may be incomplete.")

    report = {
        "schema_version": 1,
        "generator": GENERATOR,
        "repository": {
            "path": str(root),
            "file_count_scanned": len(files),
            "scan_truncated": len(files) >= MAX_FILES,
            "git": git,
        },
        "signals": {
            "languages": languages,
            "frameworks": frameworks,
            "lockfiles": lockfiles,
            "package_managers": sorted(
                {
                    "pnpm" if "pnpm-lock.yaml" in names else "",
                    "npm" if "package-lock.json" in names else "",
                    "yarn" if "yarn.lock" in names else "",
                    "bun" if {"bun.lock", "bun.lockb"} & names else "",
                    "uv" if "uv.lock" in names else "",
                    "poetry" if "poetry.lock" in names else "",
                    "cargo" if "Cargo.lock" in names else "",
                    "go" if "go.mod" in names else "",
                }
                - {""}
            ),
            "monorepo_evidence": sorted(set(monorepo_evidence)),
            "web_candidate": web_candidate,
            "server_candidate": server_candidate,
            "public_content_candidate": public_content_candidate,
            "site_generator_evidence": site_generator_evidence,
            "server_manifest_evidence": sorted(server_manifest_evidence)[:20],
            "api_route_candidate": bool(api_route_paths),
            "event_driven_candidate": bool(event_dependencies or integration_signals["asyncapi"]),
            "auth_candidate": bool(auth_dependencies),
            "database_candidate": bool(database_dependencies),
            "test_candidate": bool(test_dependencies or test_paths or quality["found"].get("test")),
            "ci_candidate": bool(ci_paths),
            "quality_commands": quality,
            "auth_dependencies": auth_dependencies,
            "database_dependencies": database_dependencies,
            "test_dependencies": test_dependencies,
            "event_dependencies": event_dependencies,
            "vendor_clients_detected": sorted(k for k in vendor_paths if k != "canonical"),
            "runtime_risk_candidate": bool(server_candidate and (auth_dependencies or database_dependencies)),
        },
        "inventory": {
            "documentation": docs,
            "agent_paths": agent_paths,
            "vendor_paths": vendor_paths,
            "integrations": integration_signals,
            "package_json": pkg,
            "ci_paths": ci_paths,
            "api_route_paths": api_route_paths,
            "test_paths": test_paths,
        },
        "warnings": warnings,
    }

    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
