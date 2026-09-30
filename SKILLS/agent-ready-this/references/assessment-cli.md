# Assessment CLI

Python 3.11+ standard library. Resolve `<skill-root>` to the installed skill; run from any working directory. Every stage writes only to the paths you give it.

## Full assessment

```text
python <skill-root>/scripts/assess_project.py --repo <project-root> --output-dir <new-assessment-dir>
```

Output, in a new directory outside the skill (existing directories are rejected):

- `audit.json`: heuristic inventory, source paths, and inspection limits.
- `recommendations.preliminary.json`: candidate changes and reasons.
- `grill-session.json`: unresolved decisions, known answers, gate, and next question.
- `assessment.md`: readable view of the same preliminary assessment.

A failed stage leaves partial output; keep it for diagnosis and retry in a new directory. `--help` lists options. Runtime-intent flags describe assessment scope, not authorization. `--known-context` follows [known-context.schema.json](../schemas/known-context.schema.json) and only suppresses settled questions. `--grill-mode off` hides questions but keeps unresolved decisions. The default next round holds one question.

## What the inspector reads

- Package scripts in every `package.json`, including scripts that run `tsc`, `vue-tsc`, `svelte-check`, or `astro check` as the typecheck gate.
- Root `Makefile` or `justfile` targets with gate names (`build`, `lint`, `test`, ...).
- Cargo, Go, and Python conventions from root manifests. Evidence marks them `convention`; they are unverified until run.
- Instruction files by case-insensitive name, CI under `.github/workflows/` and other common pipeline files.
- Server signals from web frameworks, API route paths, or server dependencies in manifests; public content only with a site generator.

It skips scratch and prior `.agent-ready` output. It does not run project commands, read secret values, or prove authorization.

## Separate stages

```text
python <skill-root>/scripts/inspect_repo.py --repo <project-root> --output <audit.json>
python <skill-root>/scripts/decide_integrations.py --audit <audit.json> --output <recommendations.preliminary.json>
python <skill-root>/scripts/build_grill_session.py --audit <audit.json> --recommendations <recommendations.preliminary.json> --known-context <known-context.json> --output <grill-session.json>
python <skill-root>/scripts/validate_artifacts.py --repo <artifact-directory> --report <validation.json>
```

Omit `--known-context` without reviewed answers. `validate_artifacts.py` is a lightweight lint, not a YAML parser, full schema validator, functional test, or security audit.

## Package tests

```text
python -B -m unittest discover -s <skill-root>/tests -v
```
