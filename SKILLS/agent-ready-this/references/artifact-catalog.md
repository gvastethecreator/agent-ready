# Artifact catalog

## Assessment and decision plane

### `audit.json`

Read-only repository evidence: topology, commands, documentation, agent files, contracts, runtime signals, and risks. It records facts and warnings; it does not decide product intent.

### `recommendations.preliminary.json`

The first evidence-backed recommendation set. It must be produced before asking the user a Grill question.

### `grill-session.json`

Grill Gate result plus only the material questions that remain after repository and conversation-context suppression.

### Decision log, final recommendations, manifest

Not produced by the helper. Record resolved answers, defaults, and planned file operations in the project's existing task record; write a separate manifest only when an existing workflow requires one.

## Development-agent plane

### `AGENTS.md`

Canonical project instructions: overview, commands, boundaries, testing, security, and contribution expectations. Use nested files only for divergent subtrees.

### Agent Skills

Directories with `SKILL.md` and optional scripts, references, and assets. Use them for procedures that should load on demand, such as releases, migrations, visual regression review, or domain-specific changes.

### Vendor adapters

Thin client-specific configuration. They must reference or derive from canonical material and contain only deltas.

### Hooks

Deterministic processes that observe, block, or modify agent behavior. Keep shared logic in repository scripts so CI and multiple clients can invoke the same check.

## Web discoverability plane

### `llms.txt`

A proposed Markdown index for LLM-friendly site context and links. It is not authentication, authorization, crawler policy, or a guarantee that an agent will use it.

### Markdown alternates and HTTP `Link` headers

Clean text versions of public pages, linked through standard relations. They should be generated from the same content source to prevent drift.

### OpenAPI / JSON Schema / Arazzo / AsyncAPI

Machine-readable contracts for HTTP operations, data shapes, multi-step API workflows, and event-driven interfaces. Prefer generating or validating them from the implementation rather than maintaining unconnected copies.

## Runtime-agent plane

### WebMCP

Tools discoverable while an agent is visiting a page. Best for using the live page state and signed-in session. Must be progressive enhancement with human UI fallback.

### MCP

A local or remote server exposing tools, resources, and prompts independently of an open page. Best for reusable headless access and integration with multiple agent hosts.

### MCP Apps

Optional UI resources associated with MCP tools. Use only when visual interaction materially improves the workflow.

### A2A

A protocol for independent agent systems to discover capabilities and collaborate through task lifecycles. Do not use it as a generic replacement for a tool API.

### ARD

A discovery layer for publishing and finding agentic resources such as MCP servers, A2A agents, OpenAPI tools, skills, and nested catalogs. Treat it as an advanced public-discovery capability.

## Relationships

```text
audit -> preliminary recommendations -> Grill Gate/Session -> agent-reviewed plan in the task record
AGENTS.md + Skills       -> teach coding agents how to work on the repo
llms.txt + API schemas   -> help agents discover and understand public capabilities
WebMCP                   -> invoke capabilities inside the live page
MCP                      -> invoke capabilities outside the page
MCP Apps / A2UI          -> render richer agent-facing UI
A2A                      -> delegate tasks to an independent agent
ARD                      -> discover which resource/protocol exists before invocation
agent-ready-site         -> verify the deployed site from the outside
```
