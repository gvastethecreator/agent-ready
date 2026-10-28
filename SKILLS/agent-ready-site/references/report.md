# Report

Write the report in the user's language. Lead with outcomes; keep layer tables as backing evidence.

## Template

```markdown
# Agent readiness: <origin> — <date>

Scope: <pages>, <jobs>, <classes and owner intent>, browser <name/viewport>, probe <file>.
Limits: <evidence not collected and why>.

## Verdict
<2–4 sentences: which classes can do which jobs today; the top blockers.>

## Job matrix
| Job | Crawler | Fetch | Browser | Programmatic |
|---|---|---|---|---|
| <job> | <outcome; observation> | <outcome; observation> | <outcome; tested mode> | <outcome or n/a> |

## Findings
### F1 <title> — <critical|high|medium|low>
- Blocks: <jobs × classes>
- Evidence (<level>): <observation, file, field>
- Fix: <change>
- Owner: <this skill | agent-ready-this | web-agent-ready | better-accessibility | CDN config | ...>
- Accept when: <check that proves the fix>

## Layer checks
| Check | Result | Evidence | Note |

## Scanner crosswalk
## Not recommended
## Unknowns and next evidence
```

## Ranking

- Use the project's severity rubric when one exists. Otherwise explain impact using the intended job, affected audience and available workaround.
- Rank observed blocked or incorrect outcomes ahead of speculative efficiency gains. An absent optional format or estimated token ratio does not establish severity.

Use remediation effort as a tie-breaker. Put unknown intent and owner-policy choices under decisions, not defects.

## Optional score

Only when the user asks. This is a local heuristic, not a standard or predictor: `pass` = 1, `degraded` = 0.5, `fail` = 0 across applicable job × class cells. Exclude and count `unknown` and `n/a`; show the denominator and material blockers beside the score.

## Scanner crosswalk

Use this topical crosswalk only when relevant. Read the actual scanner result and version/date before describing its coverage or score:

| Scanner category | Checks here |
|---|---|
| Discoverability: robots.txt, sitemap, Link headers | A1, B5, B2 |
| Content: markdown negotiation, llms.txt | B2, B6 |
| Bot access control: Content Signals, AI bot rules, Web Bot Auth | E1, A1, A6 |
| Capabilities: Agent Skills, API catalog, OAuth discovery, MCP server card, WebMCP | D6, D1, D3, D2, C7 |
| Commerce (non-scoring): x402, UCP, ACP | D7 |

Do not infer a scanner's blind spots or predict its grade from this list. A scanner result does not replace the requested job evidence. Recommend an item only for a concrete consumer and job.
