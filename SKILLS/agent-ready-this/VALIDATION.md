# Package validation

## Local audit — 2026-09-08

- Canonical skill validation passed: YAML frontmatter, Codex metadata, linked resources, and behavior fixture structure. Advisory warnings identify the retained README and changelog.
- Python 3.13.15: all five helper scripts parse; six pipeline tests passed from a different working directory.
- Covered pipeline behavior: scratch exclusion, a single default question, known-topic suppression, schema-based settled answers, unresolved blockers with presentation disabled, and preservation of an existing output directory.
- A separate CLI smoke emitted audit, preliminary recommendations, and Grill JSON that passed their Draft 2020-12 schemas. The supplied known-context document passed its schema too.
- The TypeScript WebMCP template passed syntax transformation. This does not prove native browser behavior or compatibility with a particular installed declaration package.

Reproduce the pipeline suite with:

```text
python -B -m unittest discover -s <skill-root>/tests -v
```

## Evidence limits

The CLI is an assessment aid. It does not run the target project's commands, prove authorization, ingest answers into final recommendations, generate runtime implementations, or repair managed files automatically. The acting agent must perform the requested implementation and applicable checks.

The baseline HTML planner was not changed or rechecked in this audit. Its earlier browser receipt is not current runtime proof. Native WebMCP and clean-context agent comparisons were not run: this work changed the skill package, not a live product. The behavior cases are fixtures, not measured outcomes.

The declared minimum remains Python 3.11+; this audit ran on Python 3.13.15 and did not test every supported version. No readiness grade or improvement in agent success rate is inferred from these checks.
