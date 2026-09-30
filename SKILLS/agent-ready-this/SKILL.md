---
name: agent-ready-this
description: "Repository agent readiness. Use to audit or improve coding-agent guidance, project workflows, and justified runtime interfaces."
compatibility: "Optional assessment helpers require Python 3.11+ and the standard library. Git adds repository evidence; network access is needed to verify changing standards."
metadata:
  author: BlackFlagWorks
  version: "0.3.0-plan"
---

# Agent Ready This

Make an existing project easier for agents to understand, change, and verify. Start with evidence and add only the capabilities needed for the requested work.

## Scope and authority

Use the request to select the mode:

- `assess` or `audit`: inspect and recommend without changing product source.
- `plan`: define file changes, dependencies, decisions, and acceptance criteria.
- `apply-baseline`: improve project guidance and existing workflows within the authorized scope.
- `apply-runtime`: implement the requested agent interface with its access and side-effect boundaries.
- `validate`: check the specified artifacts or behavior and report evidence limits.
- `refresh`: update authorized owned content while preserving manual changes.

When intent is unclear, use `assess`. A request to audit **and fix** authorizes the clear local fixes; show the material decision and continue. Ask only for missing information or authority that changes the proposed work. Reuse prior consent. Publishing, remote tracker changes, and consequential external actions need their own authority.

This skill owns project readiness and interface selection. Use `agent-ready-site`, when available, to audit the live site or app from outside; `web-agent-ready` for implementation of tools in an open page; `experience-design` for human understanding and control; `brainstormer` for new product capabilities. Load only the missing capability.

## Process

### 1. Establish the current state

Read local instructions, relevant Git state, project docs, manifests, commands, callers, tests, and existing agent files. Identify ownership before editing. Scope inspection to the target packages; preserve unrelated work.

Verify facts that affect the recommendation directly in source. [project-profiles.md](references/project-profiles.md) helps classify the project. The optional inspector finds candidates; dependencies and file names do not prove an integration, authorization, working command, or missing feature.

**Done:** each material finding has a source and confidence. Missing access, truncated scans, and unsupported stacks remain explicit unknowns.

### 2. Select the smallest useful improvement

Use [decision-matrix.md](references/decision-matrix.md) for applicability and [artifact-catalog.md](references/artifact-catalog.md) for outputs. Prioritize task success, accurate commands, concise instructions, and repeated workflows. A skill needs a recurring procedure; a reminder belongs in existing guidance.

For each recommendation state the evidence, proposed change, benefit, cost, dependencies, and acceptance check. Separate work that can proceed from conditional, blocked, and rejected additions. Use machine fields only when generating a structured assessment.

Keep shared instructions agent- and model-agnostic. Add [vendor adapters](references/vendor-adapters.md) only for detected or requested client-specific differences. Reuse the current client's model, tools, and permissions.

**Done:** each addition solves an observed need. A web framework alone does not justify WebMCP, MCP, MCP Apps, A2A, or a discovery catalog.

### 3. Resolve only material unknowns

Use [grill-session-protocol.md](references/grill-session-protocol.md) when a missing answer changes scope, ownership, security, or architecture. The decision gate is:

- `skipped`: evidence and reversible defaults already settle the plan.
- `useful`: an answer helps prioritization; clear authorized work can proceed.
- `required`: only the affected work awaits a necessary answer.

Ask one question at a time by default, with evidence and a recommendation. An unanswered question grants no permission. A generated interview is a candidate list: inspect it before presenting it, remove questions already settled, and stop when answers no longer change the plan.

**Done:** active work has the decisions it needs, and blocked work names its unresolved dependency. Disabling questions does not resolve those dependencies.

### 4. Plan or implement within scope

For substantial work, reuse the project's durable task record. Apply `simple-english` before drafting task or plan text, preserving commands and identifiers. State file operations and acceptance checks; avoid a manifest for a small patch unless an existing workflow requires it.

In an apply mode, make the smallest coherent change. Direct edits to human-owned files are allowed within the user's requested scope; preserve unrelated content. Read [managed-files-policy.md](references/managed-files-policy.md) when introducing generated content or refresh ownership.

For runtime work, read [security-model.md](references/security-model.md). Define callers, resource authorization, inputs, side effects, retry behavior, cancellation, and results. Reuse the domain functions used by the product. Inspect the current official protocol and target implementation; [standards-registry.json](references/standards-registry.json) is a dated lookup index, not proof of current support. Keep an experimental surface optional to the existing working product path.

**Done:** requested changes are concrete and reviewable. Only a missing boundary blocks its affected operation; unrelated authorized work continues.

### 5. Verify and hand back

At the final boundary, run the smallest applicable project checks. For changed interfaces, cover an authorized call and the relevant rejection or failure path. Use existing coverage first. Observe live discovery, execution, UI state, and cleanup when a page tool's behavior cannot be proved at a lower layer. For a deployed public site, check live agent access and reads with `agent-ready-site`, when available.

Use [validation-rubric.md](references/validation-rubric.md) to separate structural, functional, and agent evidence. Report changed files, checks and results, skipped checks with reasons, unresolved decisions, and any limits on readiness. A score or generated receipt cannot replace missing proof.

**Done:** another maintainer can reproduce the evidence and distinguish delivered work from a proposal. Do not claim tests, security, or agent effectiveness from file presence.

## Optional assessment helper

Resolve `<skill-root>` to this installed package. The helper writes only assessment artifacts; it does not apply project changes. Use a **new output directory** outside the installed skill, preferably the project's existing scratch area:

```text
python <skill-root>/scripts/assess_project.py --repo <project-root> --output-dir <new-assessment-dir>
```

It emits `audit.json`, `recommendations.preliminary.json`, `grill-session.json`, and `assessment.md`. An existing output directory is rejected to preserve earlier work. On stage failure, retain partial outputs as incomplete evidence and retry in a new directory.

Read [assessment-cli.md](references/assessment-cli.md) for stage commands, options, and what the inspector reads. Commands inferred from stack conventions stay unverified until run. Templates are examples, not facts about the target.

Answer ingestion, final recommendation recomputation, file-operation manifests, managed refresh, and runtime generators are **not implemented by the scripts**. The acting agent performs authorized work using repository tools. `--known-context` only suppresses settled questions; it does not update recommendations or grant approval.
