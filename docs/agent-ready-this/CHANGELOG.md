# Changelog

## 0.3.0-plan — 2026-09-30

- Inspector: stop skipping `.github` (CI, Copilot instructions, security and owner files were invisible); match instruction files case-insensitively; read root Makefile or justfile targets and Cargo, Go, and Python conventions; count `tsc`-style scripts as the typecheck gate; require a site generator before assuming public content; require a web-framework dependency before treating a manifest as a server.
- Recommendations: CI and agent evals are conditional unless CI already exists or a repeated costly task needs one; artifacts point to existing docs instead of new `docs/agent/*` files; the command gap question is `major`, not blocking.
- Package: moved the blueprint, changelog, validation record, and HTML planner to `docs/agent-ready-this/`; README became `references/assessment-cli.md`; removed the CI workflow template.
- Added a regression test for a Rust and Tauri repository.

## Unreleased (0.2.x)

- Clarify scope, reuse existing consent, separate implemented helpers from planned features, and align references and evaluation fixtures.
- Preserve existing assessment directories, exclude scratch inputs, honor schema-based answers, and retain blockers when questions are disabled.
- Default interviews to one question and require real tool behavior in the WebMCP template.

## 0.2.0-plan — 2026-09-04

- Renamed the skill from `agent-ready-tuneup` to `agent-ready-this`.
- Made `assess` the user-facing default: analyze, recommend, then decide whether questions are needed.
- Added the Grill Gate and adaptive Grill Session protocol.
- Added preliminary recommendation and Grill Session schemas.
- Added a complete assessment orchestrator and deterministic Grill planner.
- Expanded evaluation cases for analyze-first behavior, question suppression, and runtime blockers.

## 0.1.0-plan — 2026-09-04

- Initial planning scaffold.
- Added blueprint, draft skill, references, schemas, templates, inspector, recommendation helper, validator, and evaluation fixtures.
- No automatic repository mutation.
