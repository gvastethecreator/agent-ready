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
| Find Pro price | pass (probed) | degraded: 41k tokens, no markdown (probed) | pass (task) | n/a |

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

- `critical`: blocks a job for a class the owner wants.
- `high`: completes only degraded for a wanted class (JS-only facts, triple token cost, ambiguous controls needing a guess), or a policy contradiction (E1, E2).
- `medium`: discoverability or efficiency losses without a blocked job.
- `low`: hygiene.

Order by severity, then by count of affected job × class cells, then lower effort first. Put unwanted classes and owner-policy choices under decisions, not findings.

## Optional score

Only when the user asks. Method: applicable job × class cells; `pass` = 1, `degraded` = 0.5, `fail` = 0; exclude `unknown` and `n/a` and state how many were excluded. Show the denominator. A critical finding is listed beside the score, never averaged away.

## Scanner crosswalk

Map public scanners such as Cloudflare's isitagentready.com so the user can predict their result without chasing points:

| Scanner category | Checks here |
|---|---|
| Discoverability: robots.txt, sitemap, Link headers | A1, B5, B2 |
| Content: markdown negotiation, llms.txt | B2, B6 |
| Bot access control: Content Signals, AI bot rules, Web Bot Auth | E1, A1, A6 |
| Capabilities: Agent Skills, API catalog, OAuth discovery, MCP server card, WebMCP | D6, D1, D3, D2, C7 |
| Commerce (non-scoring): x402, UCP, ACP | D7 |

Scanners do not see A2 edge behavior by class, A3 soft 404s, B1 JS-only facts, B3 cost, C operate results, or E contradictions. Recommend a scanner item only when a wanted class uses it for a job.
