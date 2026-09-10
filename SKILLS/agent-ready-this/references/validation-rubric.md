# Readiness evidence

Readiness is a scoped conclusion about tasks agents can complete. File presence and a generated score do not establish it.

## What to check

Select the dimensions affected by the requested change:

- Setup and commands: authoritative package scope, prerequisites, execution result.
- Guidance: accurate ownership and instructions without material contradictions.
- Procedures: repeated tasks that justify skills and can be followed from their inputs.
- Interfaces: a justified contract with observed success and relevant rejection paths.
- Security: resource authorization, side-effect policy, secrets, and ownership.
- Maintenance: existing checks and a clear update path for changed generated content.

Use `passed`, `failed`, `unknown`, or `not-applicable`, with evidence and reasons. A missing JavaScript script alias does not mean a Rust, Python, or documentation project lacks its own checks.

## Evidence levels

- Static: file structure, references, metadata, schemas, and code inspection.
- Executed: actual project commands, runtime calls, and observed failures.
- Agent behavior: representative tasks completed in a controlled evaluation.

The bundled `validate_artifacts.py` performs lightweight structural checks. Its frontmatter inspection is a text heuristic, not a YAML parser; it does not validate complete JSON Schemas or security. Use the repository's real YAML/schema validator where required. Do not treat a successful lint of the assessment directory as proof that the target project was tested.

Inspect existing coverage before adding a test. Choose one case per changed failure class and reuse passed evidence. Test a live interface when lower layers cannot observe its behavior. Report native-browser and agent-evaluation gaps explicitly.

## Gates

A readiness claim is blocked for the affected scope when a required command is broken, guidance conflicts, authorization is unknown, a consequential operation lacks its required control, or generated updates can clobber manual work. Potential sensitive filenames are a prompt for private inspection, not proof that credentials were found.

Unknown required proof keeps that dimension unverified. Stating a reason for an unrun check explains the gap; it does not pass the gate. Block only dependent work and preserve evidence for completed work.

A numeric score is optional only when the user needs a comparison. Show the method, applicable denominator, and unknowns. Never use the total to hide a failed critical gate or penalize a project for correctly omitting runtime protocols.

## Closeout

Report delivered behavior, evidence, checks and outcomes, skips with reasons, and remaining decisions. Keep findings separate from planned remediation. A prototype, template, or passing helper test cannot establish production or end-to-end agent readiness.
