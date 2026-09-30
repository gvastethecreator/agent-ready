# Project instructions

## Project overview

<!-- Explain the product, current architecture, and non-goals. Derive from evidence. -->

## Repository map

<!-- Point to the smallest useful set of directories and deeper docs. -->

## Setup and commands

<!-- agent-ready:start id=quality-commands source=detected-manifests-and-ci -->
<!-- Insert verified install, dev, build, lint, typecheck, and test commands. -->
<!-- agent-ready:end -->

## Change workflow

1. Inspect the relevant scope and its nearest `AGENTS.md`.
2. Make the smallest coherent change.
3. Reuse existing tests; add one only for an uncovered observable failure.
4. Run the scoped quality commands.
5. Report commands, results, risks, and unverified assumptions.

## Constraints

<!-- Add architectural boundaries and forbidden shortcuts. -->

## Security

- Never commit secrets.
- Preserve authentication, authorization, validation, and tenant boundaries.
- Do not introduce general-purpose shell, SQL, filesystem, or network execution.

## Further documentation

<!-- Link existing docs (architecture, contributing, security) instead of copying them. -->
