# Agent Ready This

Audit and improve an existing project's guidance, workflows, and justified agent interfaces. Start with repository evidence, ask only for material missing decisions, and complete the work the user authorized. See [SKILL.md](SKILL.md) for the operating contract.

The package contains an assessment CLI and planning aids. It does not contain an automatic repository mutator, managed refresh engine, final recommendation engine, or runtime protocol generator.

## Assessment

The optional helper uses Python 3.11+ and its standard library. Resolve `<skill-root>` to this installed directory; run from any working directory:

```text
python <skill-root>/scripts/assess_project.py --repo <project-root> --output-dir <new-assessment-dir>
```

Use a new directory outside the installed skill, preferably in the project's scratch area. Existing directories are rejected. The result contains:

- `audit.json`: heuristic inventory, source paths, and inspection limits.
- `recommendations.preliminary.json`: candidate changes and reasons.
- `grill-session.json`: unresolved decisions, known answers, gate, and next question.
- `assessment.md`: a readable view of the same preliminary assessment.

A failed stage leaves partial output. Preserve it for diagnosis and retry in a new directory. The inspector skips scratch and prior `.agent-ready` output; it mainly recognizes JavaScript package commands. Verify important findings and commands for other stacks manually. It does not run target project commands or establish security.

Use `--help` for options. Runtime-intent flags describe the assessment scope, not authorization to expose an interface. `--known-context` uses [known-context.schema.json](schemas/known-context.schema.json) to suppress settled questions; it does not recompute recommendations. `--grill-mode off` suppresses presentation while retaining unresolved decisions. The default next round contains one question.

## Separate stages

Use fresh output paths; these individual commands write to the paths supplied:

```text
python <skill-root>/scripts/inspect_repo.py --repo <project-root> --output <audit.json>
python <skill-root>/scripts/decide_integrations.py --audit <audit.json> --output <recommendations.preliminary.json>
python <skill-root>/scripts/build_grill_session.py --audit <audit.json> --recommendations <recommendations.preliminary.json> --known-context <known-context.json> --output <grill-session.json>
python <skill-root>/scripts/validate_artifacts.py --repo <artifact-directory> --report <validation.json>
```

Omit `--known-context` when no reviewed answers are available. The artifact validator is a lightweight lint, not a YAML parser, full schema validator, functional test, or security audit. Run the project's own required checks separately.

## Package maintenance

```text
python -B -m unittest discover -s <skill-root>/tests -v
```

[evals/evals.json](evals/evals.json) contains behavior scenarios for isolated agent evaluations. Fixtures are not executed outcomes. [VALIDATION.md](VALIDATION.md) records the evidence available for the package.

The templates require actual project functions, paths, and current protocol contracts. The offline HTML planner demonstrates candidate decisions from manually supplied inputs; it does not inspect repositories or mirror every CLI rule. [BLUEPRINT.md](BLUEPRINT.md) preserves the original design proposal; the current operating contract is `SKILL.md`.
