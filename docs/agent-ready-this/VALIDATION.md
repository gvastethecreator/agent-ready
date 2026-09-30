# Package validation

## Local audit — 2026-09-30

- Seven pipeline tests passed on Python 3.13.15, including a new Rust and Tauri fixture with lowercase `agents.md` and GitHub CI.
- Real repositories, read-only: `token-tray-meter` (Rust, Tauri, Vite) went from a `required` gate with false findings (missing instructions, missing typecheck, no CI, llms.txt, HTTP contract) to `skipped` with CI, commands, and instructions detected. `agents-matrix` keeps a `required` gate from its real MCP server authorization question.
- `writing-for-agents` structural validation passed; checksums regenerated for the published package.

Reproduce:

```text
python -B -m unittest discover -s SKILLS/agent-ready-this/tests -v
```

## Evidence limits

The CLI is an assessment aid. It does not run the target project's commands, prove authorization, ingest answers into final recommendations, or repair managed files. Convention commands (Cargo, Go, Python) are inferred, not executed. No clean-context agent comparison was run; behavior cases in `evals/` are fixtures, not measured outcomes. Python 3.11+ is the declared minimum; only 3.13.15 was tested.
