# Check catalog

Each check names its probe field or method, the pass target, and the owner for fixes. Severity comes from the jobs and classes a failure blocks, not from the check itself. `standards.json` holds maturity, consumers, and sources.

## A. Access: does the agent get real content?

- **A1 robots.txt** (`robots`). Target: 200 plain text; per-token verdicts on job paths match owner intent; no accidental `Disallow: /` under `*`; a `Sitemap:` line. RFC 9309 gotchas: a 5xx or unreachable robots.txt makes compliant crawlers assume complete disallow; a 4xx lets them fetch everything; HTML at `/robots.txt` means no rules. Robots is policy, not access control. Owner: this skill.
- **A2 edge response by class** (`pages[].challenge_suspected`, `ua_matrix`). Target: wanted classes get the same status and content as a browser. A challenge, 403, or thin body for `Claude-User` or `ChatGPT-User` while robots allows them is a contradiction. Spoofed user agents expose only user-agent rules; verified-bot allowlists (IP ranges, Web Bot Auth) need CDN or server evidence (`source`). Owner: CDN or WAF configuration, with authority.
- **A3 soft 404** (`soft_404`). A 200 for unknown paths turns every presence check into a content check; well-known entries serving HTML are fallbacks, not resources.
- **A4 walls.** Consent, login, paywall, interstitial, or geo redirect in front of job content. Target: public job content is readable before any consent choice; declining consent keeps it readable.
- **A5 rate limits.** Target: 429 with `Retry-After` or `RateLimit` headers, not silent drops or challenge pages. Do not load-test; use headers seen and source.
- **A6 Web Bot Auth.** The key directory matters only when the organization operates its own signing agent. For a receiving site, signature verification lives in CDN or server config (`source`). Scanners that score the directory on every site overstate it.

## B. Read: can the agent extract the right facts cheaply?

- **B1 server-rendered facts** (`facts[].visible_text`, `html.text_chars`, `html.js_shell_suspected`, dom_probe `rendered_text_chars`). Target: every read-job fact is in raw visible text. A raw/rendered text ratio below about 0.3 suggests JS-dependent content; confirm in the rendered page. Facts only in hydration JSON (`html_source` true, `visible_text` false) fail for crawlers and fetch agents.
- **B2 markdown** (`markdown_negotiation`, `markdown_alternate`, `link_header_rels`). Target for sites that want fetch agents: `Accept: text/markdown` returns `text/markdown` with `Vary: Accept`, or a declared alternate (`<link rel="alternate" type="text/markdown">` or `Link` header) resolves. Markdown must carry the same facts as HTML. A guessed `.md` route that works but is undeclared is `degraded`. Owner: this skill for headers and links; `agent-ready-this` for a generation pipeline.
- **B3 cost** (`approx_tokens_html`, `approx_tokens_text`, markdown `approx_tokens`). Fetch tools truncate. Target: job facts sit early in main content; boilerplate does not dominate. Report the token ratio between HTML and markdown.
- **B4 structure** (`html.*`). Target: title, `lang`, one `h1`, ordered headings, a `main` landmark, canonical, meta description, data in real `table` and list elements.
- **B5 URLs and index** (`sitemap`). Target: sitemap reachable with `lastmod`; job pages in it or linked from navigation; stable canonical URLs; pagination links rather than scroll-only loading; no hash-only routes for content.
- **B6 llms.txt** (`llms_txt`). Target when applicable (docs, developer, API products): H1, blockquote summary, sections, working links, preferably to markdown. Few crawlers fetch it unprompted; it helps when a user or doc points an agent at it. For other sites it is conditional, never a blocker. Owner: `agent-ready-this`.
- **B7 structured data** (`html.jsonld_types`, `jsonld_errors`). Target: valid JSON-LD whose types match the page (Organization, Product with Offer, Article with dates, SoftwareApplication). The same facts must be in visible text; JSON-LD alone is not extraction proof.
- **B8 media text.** Target: prices, specs, and instructions are text, not images; meaningful `alt`; transcripts for job-relevant video.

## C. Operate: can a browser agent finish the job?

C1 names and roles, C2 forms, C3 state in URL, C4 blockers, C5 feedback, C6 consequential gates, C7 in-page tools. Criteria and procedure: [operate-test.md](operate-test.md). Accessibility repair depth: `better-accessibility`; WebMCP: `web-agent-ready`.

## D. Integrate: can a headless agent do the job without the UI?

Apply only where programmatic agents fit the site type or a job.

- **D1 discovery** (`well_known` api-catalog). Target: `/.well-known/api-catalog` as `application/linkset+json` (RFC 9727) or a documented link to an OpenAPI description reachable from docs or llms.txt.
- **D2 MCP.** Target: a remote MCP server for page-independent jobs, with authorization per the current MCP spec. Server-card paths changed between drafts; report which path answered and the draft it follows.
- **D3 delegated auth** (`well_known` oauth and openid entries). Target: scoped, revocable tokens through OAuth metadata (RFC 8414) or protected-resource metadata (RFC 9728); no job that requires handing an agent the user's password.
- **D4 contract behavior** (`source`, docs). Target: Problem Details errors (RFC 9457), idempotency keys on writes, pagination, rate-limit headers, stable IDs, versioning.
- **D5 A2A agent card.** Only when the product is itself an agent with a task lifecycle.
- **D6 Agent Skills index.** Only for developer products that publish skills.
- **D7 commerce.** x402, ACP, UCP: report-only. Machine-readable price and availability in text come first.

Owner for D builds: `agent-ready-this`.

## E. Policy: do the signals agree?

- **E1 intent consistency.** Robots rules, Content Signals, WAF behavior, terms of service, and investments (llms.txt, markdown, MCP) point the same way. Examples: blocking `ClaudeBot` training is policy, but a WAF blocking `Claude-User` on docs meant for coding agents is a defect; `ai-train=no` with no stated preference is a decision to confirm, not an error.
- **E2 same content.** Markdown, JSON-LD, and HTML state the same facts. User-agent-sniffed variants, hidden agent-only text, or instructions addressed to agents are cloaking and injection risks.
- **E3 untrusted content.** Job pages dominated by user-generated content expose browser agents to injected instructions; note it, and mark such tool output `untrustedContentHint` when WebMCP exists.
- **E4 identity.** Who operates the site is reachable: Organization data, about, contact, support.
