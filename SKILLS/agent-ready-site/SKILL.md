---
name: agent-ready-site
description: "Live site or web app agent readiness. Use to audit how crawlers, fetch agents, browser agents, and API or MCP agents access, read, and operate a URL."
compatibility: "The probe helper needs Python 3.11+ (standard library) and network access. The operate test needs a controllable browser."
metadata:
  version: "0.1.0"
---

# Agent Ready Site

Audit a live website or web app the way agents meet it: over HTTP, in a browser, and through its APIs. A site is agent-ready when named **jobs** succeed for the agent classes the owner wants, at acceptable cost, within the owner's policy. File presence, scanner points, and registry entries are supporting evidence only.

## Scope and authority

- `audit` (default): read-only findings and a ranked fix plan.
- `audit and fix`: also apply clear local fixes in the site's source when the repo is available: robots rules, headers, link tags, labels, server rendering of key facts. Interface builds go to their owners.
- Traffic: the probe sends bounded GET requests only. In the browser, navigate and fill test inputs; stop before any consequential action. Sign in only with a test account on the user's own app. For third-party sites, audit public pages with the default budget.
- CDN, WAF, and DNS dashboard changes need their own authority, even in `audit and fix`.
- Owners, loaded only for requested work: coding-agent guidance and interface builds (llms.txt, OpenAPI, MCP) → `agent-ready-this`; in-page WebMCP tools → `web-agent-ready`; accessibility repair depth → `better-accessibility`; AI citation strategy → `ai-seo`; classic SEO → `seo-audit`; launch hygiene → `site-go-live`.

## Agent classes

| Class | Reaches the site as | Needs |
|---|---|---|
| crawler | GPTBot, ClaudeBot, OAI-SearchBot, PerplexityBot; robots-governed, raw HTML, usually no JS | access, server-rendered facts, sitemap |
| fetch | ChatGPT-User, Claude-User, coding-agent fetch tools; one URL for one user, usually no JS, may send `Accept: text/markdown`, truncates long pages | no WAF block, markdown or clean HTML, low token cost |
| browser | computer-use and browser agents; rendered DOM, accessibility tree, screenshots, the user's session | names and roles, labeled forms, state in URL, no blockers |
| programmatic | API or MCP clients, headless | discovery, delegated auth, contracts, machine-readable errors |

## Process

1. **Frame the jobs.**
   - Establish origin, site type (content, docs, commerce, SaaS app, API product), owner intent toward each class (welcome, selective, restrict), source repo, and test account.
   - Pick 3–5 jobs: read jobs ("find the Pro plan price") and do jobs ("filter shoes to size 42", "book a demo up to the confirm step"). Take them from the user; otherwise derive them from navigation, sitemap, and primary calls to action, and label them as assumptions.
   - When intent is unknown, audit for "welcome" and report policy choices as owner decisions, not defects.
   - Done when each job has start URL, agent classes, success signal (fact string or end state), and a stop point before any consequential effect.

2. **Probe over HTTP.**
   - Run `python <skill-root>/scripts/probe_site.py <url> --out <new-dir>/probe.json`, with `--page` for each job start URL and `--expect "<path>::<fact>"` for each read-job fact. Add `--ua-matrix` for the user's own site or when the tool user agent is challenged. Write evidence to the project's scratch area or the session scratchpad, never inside the skill.
   - Pass `--page` and `--expect` targets as full URLs in Git Bash or MSYS shells, which rewrite arguments that start with `/`.
   - A challenged or soft-404 result invalidates presence checks: rerun with `--ua browser` to separate access from read.
   - Judge results with [checks.md](references/checks.md) layers A, B, D, and E.
   - Done when every job start URL has probe evidence or a recorded reason (network, challenge, auth).

3. **Verify reads.**
   - Each read-job fact must appear in visible raw text, with its label and unit, and in the markdown variant when one exists. A fact present only in script payloads counts as missing for crawlers and fetch agents.
   - Confirm a missing fact in the rendered page before calling it JS-only. Check that markdown carries the same content as HTML.
   - Done when each read job has `pass | degraded | fail | unknown` for the crawler and fetch classes, with evidence.

4. **Run the operate test.**
   - Follow [operate-test.md](references/operate-test.md): one browser surface, one desktop viewport, and navigation by accessibility-tree names and roles. Evaluate `scripts/dom_probe.js` on each job's start view.
   - Done when each do job has a browser-class outcome, the step where it failed, and the blocking element.

5. **Check programmatic and policy surfaces.**
   - Apply layer D where programmatic agents fit the site type or jobs. Apply layer E on every audit: robots, Content Signals, WAF behavior, and terms must agree with owner intent.
   - Classify speculative formats with [standards.json](references/standards.json) `policy: avoid` as "not recommended", never as gaps. Recheck an entry's source before it drives a recommendation.
   - Done when each applicable D and E check is `pass | fail | unknown | not-applicable` with a reason.

6. **Report.**
   - Follow [report.md](references/report.md): job × class matrix first, then findings ranked by blocked jobs, each with evidence level, fix, owner, and acceptance check.
   - In `audit and fix`, apply clear fixes, then rerun only the affected probe or operate checks.
   - Done when every matrix cell has an outcome and evidence level, every fail has a fix and owner, and each unknown names the evidence that would resolve it.

## Evidence levels

`probed` (HTTP observed) · `rendered` (DOM or accessibility tree observed) · `task` (job attempted end to end up to the stop point) · `source` (code, config, or dashboard read) · `inferred` (docs or convention; always labeled). A claim is bounded by the highest level actually observed.

## Resources

- [references/checks.md](references/checks.md): check catalog by layer with pass criteria and owners.
- [references/operate-test.md](references/operate-test.md): browser protocol, C checks, outcome rules.
- [references/report.md](references/report.md): report template, ranking, optional score, scanner crosswalk.
- [references/standards.json](references/standards.json): dated capability and agent-token registry; the probe reads its paths and tokens.
- `scripts/probe_site.py`: bounded HTTP probe; `--help` for options.
- `scripts/dom_probe.js`: rendered-page snapshot for the operate test.
