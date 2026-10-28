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
| crawler | automated retrieval under the client's documented crawl policy | allowed access, discoverable pages, facts in the representation it reads |
| fetch | user-directed URL retrieval, with client-specific headers, rendering and size limits | readable facts within those limits |
| browser | rendered page through the tested DOM, accessibility or screenshot interface | usable controls, feedback and required session state |
| programmatic | API or MCP client | a needed contract, discovery and authorization |

Name the actual client when known. A synthetic user-agent header does not establish that client's identity, capabilities or success.

## Process

1. **Frame the jobs.**
   - Establish origin, site type (content, docs, commerce, SaaS app, API product), owner intent toward each class (welcome, selective, restrict), source repo, and test account.
   - Pick a bounded sample of read jobs ("find the Pro plan price") and do jobs ("filter shoes to size 42", "book a demo up to the confirm step"). Use the user's jobs or label derived jobs as assumptions. State what the sample excludes.
   - Keep unknown owner intent explicit; policy choices need an owner decision before being called defects.
   - Done when each job has start URL, agent classes, success signal (fact string or end state), and a stop point before any consequential effect.

2. **Probe over HTTP.**
   - Run `python <skill-root>/scripts/probe_site.py <url> --out <new-dir>/probe.json`, with `--page` for each job start URL and `--expect "<path>::<fact>"` for each read-job fact. Use `--ua-matrix` only for an authorized, planned comparison of header-based rules on the user's site. Write evidence to the project's scratch area or the session scratchpad, never inside the skill.
   - Pass `--page` and `--expect` targets as full URLs in Git Bash or MSYS shells, which rewrite arguments that start with `/`.
   - Preserve denials, challenges and rate limits. Do not change user agent, browser, tool or identity to recover denied content. Inspect allowed source/config evidence instead. A soft 404 needs content checks; an allowed JS shell needs rendered verification, not a different header.
   - Judge results with [checks.md](references/checks.md) layers A, B, D, and E.
   - Done when every job start URL has probe evidence or a recorded reason (network, challenge, auth).

3. **Verify reads.**
   - Check each fact with its label and unit in the representation the named client reads. The helper's raw-text check cannot establish success for a rendering client. A fact found only in script payloads is missing from the helper's extracted text.
   - Confirm a missing fact in the rendered page before calling it JS-only. Check that markdown carries the same content as HTML.
   - Done when each read job has `pass | degraded | fail | unknown` for the crawler and fetch classes, with evidence.

4. **Run the operate test.**
   - Follow [operate-test.md](references/operate-test.md): one supported browser surface and one desktop viewport. Name the tested interaction mode. `scripts/dom_probe.js` is an approximate DOM diagnostic, not the browser's computed accessibility tree.
   - Done when each do job has a browser-class outcome, the step where it failed, and the blocking element.

5. **Check programmatic and policy surfaces.**
   - Apply layer D only for a concrete programmatic consumer and job. Optional surfaces are not missing requirements by default. In layer E compare observed policy signals with known owner intent.
   - Classify speculative formats with [standards.json](references/standards.json) `policy: avoid` as "not recommended", never as gaps. Recheck an entry's source before it drives a recommendation.
   - Done when each applicable D and E check is `pass | fail | unknown | not-applicable` with a reason.

6. **Report.**
   - Follow [report.md](references/report.md): job × class matrix first, then findings ranked by blocked jobs, each with evidence level, fix, owner, and acceptance check.
   - In `audit and fix`, apply clear fixes, then rerun only the affected probe or operate checks.
   - Done when every matrix cell has an outcome and evidence level, every fail has a fix and owner, and each unknown names the evidence that would resolve it.

## Evidence levels

`probed` (HTTP observed) · `rendered` (DOM or accessibility tree observed) · `task` (job attempted up to the stop point) · `source` (code, config, or dashboard read) · `inferred` (docs or convention; label it). These support different claims: source inspection does not prove runtime success, and a generic probe does not prove a named vendor client works.

## Resources

- [references/checks.md](references/checks.md): check catalog by layer with pass criteria and owners.
- [references/operate-test.md](references/operate-test.md): browser protocol, C checks, outcome rules.
- [references/report.md](references/report.md): report template, ranking, optional score, scanner crosswalk.
- [references/standards.json](references/standards.json): dated capability and agent-token registry; the probe reads its paths and tokens.
- `scripts/probe_site.py`: bounded HTTP probe; `--help` for options.
- `scripts/dom_probe.js`: rendered-page snapshot for the operate test.
