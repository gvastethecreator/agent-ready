# Decision matrix

Structured assessment records use these fields; a small chat recommendation can state the same decision briefly:

- `applicability`;
- `action`;
- `priority`;
- `confidence`;
- `impact`, `effort`, and `risk`;
- repository `evidence`;
- `reason` and rejected alternatives;
- `unknowns` and prerequisites;
- expected artifacts;
- acceptance criteria;
- `grill_topics` only when user input can materially change the decision.

## Applicability states

- `required`: baseline needed for safe agent work.
- `recommended`: strong evidence, meaningful value, and acceptable implementation risk.
- `conditional`: useful only if a named product or operational condition is true.
- `report-only`: explain an emerging or high-risk capability without applying it.
- `not-applicable`: evidence says the capability does not fit the current project.
- `blocked`: applicable in principle, but unsafe or impossible to finalize until a material blocker is resolved.

## Action states

- `create`: artifact or implementation does not exist.
- `update`: existing artifact is valid but incomplete or stale.
- `repair`: existing artifact is contradictory, unsafe, or structurally broken.
- `validate`: existence is established, correctness is not.
- `investigate`: applicability remains conditional after the read-only pass.
- `skip`: no current implementation should be added.

## Rules

| ID | Capability | Include when | Exclude or defer when | Typical Grill trigger |
|---|---|---|---|---|
| `canonical-instructions` | Canonical coding-agent instructions | Any maintained code repository | No executable/maintained code | Existing human-owned instruction files conflict |
| `scoped-instructions` | Scoped instructions | Monorepo or subtree-specific commands/policies | Root guidance is sufficient | Scope ownership or commands remain ambiguous |
| `project-map` | Architecture and repository map | Project has more than trivial topology | Generated map would add no navigational value | Usually none; derive from source |
| `quality-command-contract` | Deterministic commands | Any maintained project | Never exclude; missing gates become blockers | Authoritative commands cannot be established from source/CI |
| `project-agent-skills` | Reusable procedures | Repeated multi-step workflows or domain knowledge | One-line convention or no repeatability evidence | Highest-value repeated workflows are unknown |
| `vendor-adapters` | Client-specific integration | Client config detected or requested | Would duplicate canonical instructions | First-class clients are unknown |
| `ci-readiness` | Independent quality enforcement | Project has executable quality gates | Tiny non-code content repository | Usually none; inspect CI first |
| `agentic-evals-and-drift` | Behavioral proof and synchronization | Canonical files or managed content exist | One-off archive with no maintenance | Success criteria may be useful, rarely blocking |
| `llms-txt` | Public content index | Public website/docs with stable useful pages | Private app, no public scope, or no useful content | Public base URL or intended content is unclear |
| `openapi-contract` | HTTP contract | Existing HTTP API with stable operations | No API or contract cannot be maintained | Stable supported route set is unclear |
| `arazzo-workflows` | API workflow contract | Important multi-step workflows over validated OpenAPI | Simple independent operations | High-value workflow set is unknown |
| `asyncapi-contract` | Event contract | Messaging/events form a durable interface | Internal incidental events only | Contractual channels/consumers are unclear |
| `webmcp` | Page-local browser tools | Existing UI actions should be invoked in an open signed-in page | Headless use required, no fallback, or unsupported security model | Page dependency, caller, authz, mutation, fallback |
| `mcp-server` | Page-independent tools/data | Reusable service actions or resources exist | Capability is purely visual or domain layer is not reusable | Caller, transport, authz, and write policy |
| `mcp-apps` | Interactive MCP UI | Tool result benefits materially from map/table/editor/comparison | Structured data is sufficient | Concrete visual workflow is unclear |
| `a2a-agent` | Agent-to-agent task delegation | Product is an independent agent with task lifecycle | It is only a tool/API/service | Task lifecycle, caller identity, cancellation, artifacts |
| `ard-catalog` | Federated public discovery | Multiple public agentic resources need discovery | Private/single resource or identity/trust not ready | Public resource scope and fallback |

## Default safety posture

- `llms.txt`: no publication until intentionally public scope is established.
- WebMCP: report-only unless explicitly requested; feature detection and human fallback required.
- MCP: conditional; runtime application requires caller, transport, authz, tool scope, and negative tests.
- MCP Apps: skip unless one concrete result needs an interactive surface.
- A2A: not applicable unless the product manages delegated task state.
- ARD: report-only unless public multi-resource discovery is an explicit product goal.
- Any mutating runtime capability: blocked only where its required authorization, confirmation, retry, or audit policy is unresolved. Preserve existing authority and the product policy; do not add a universal approval step to every state change.

## Grill relationship

The decision engine creates preliminary recommendations first. The Grill Session does not replace analysis; it resolves only high-materiality unknowns attached through `grill_topics`.

An unanswered Grill question may move only the affected recommendation to `blocked` or `report-only`, with any deferral recorded in the decision log. It must not block unrelated baseline work.
