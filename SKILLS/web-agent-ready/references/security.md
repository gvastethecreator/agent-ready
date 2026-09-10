# WebMCP Security

Tools run page JS with the user's cookies and UI. Treat every tool as a public method on the origin.

Spec privacy: https://webmachinelearning.github.io/webmcp/
Chrome: https://developer.chrome.com/docs/ai/webmcp

## Origin isolation

WebMCP requires an origin-keyed agent cluster (`document.domain` disabled).

- Do not set `Origin-Agent-Cluster: ?0`.
- Do not assign `document.domain`.
- `file:` is the documented exception for local files.

If isolation is off, `registerTool` rejects with `SecurityError`. Fix the document; do not catch-and-ignore.

## Permissions-Policy `tools`

Default allowlist `'self'`: top-level and same-origin frames may register. Cross-origin iframes are off.

- Enable a child: `<iframe src="https://agent.example/" allow="tools">` plus `exposedTo: ["https://agent.example"]` on tools that child may call.
- Disable on this origin: `Permissions-Policy: tools=()`. Use only when the product must not expose tools.

`registerTool` rejects with `NotAllowedError` when the policy denies the document.

## What a tool may do

A tool inherits the page's origin, storage, and network. It must not:

- Return API keys, session tokens, CSRF secrets, or password fields.
- Accept a credential from the model and store it. Credential design: `browser-secret-boundary-readiness`.
- Bypass the product's authz checks. Execute the same server path the UI uses.
- Perform money, delete, publish, or share without the existing human confirm step.

Purchases and irreversible jobs: omit `toolautosubmit`; `execute` should open or focus the confirm/checkout UI the human already has. Do not silently `fetch` a pay endpoint from the tool.

## Hints

- `readOnlyHint: true` only for getters. Name incidental effects explicitly; do not mark a tool read-only if it changes the cart or other application state.
- `untrustedContentHint: true` when returning other users' names, reviews, emails, or fetched third-party text so the agent does not treat it as site policy.

Hints describe behavior; they do not authenticate a caller, authorize an object, sanitize output, or enforce consent. The current draft also defines `consequentialHint`; verify target support and set it for consequential tools.

## Confirmation UX

Preserve the product's confirmation policy and established user authority. Do not add a second approval ritual for an already authorized reversible action. For a job that requires final review:

1. Tool prepares state (fill, preview, draft).
2. Visible confirm control stays human-gated.
3. Agent may call a separate read-only `get-order-preview` tool; it must not call `place-order` without the user completing confirm.

Do not hide the confirm behind CSS `display: none` while the tool clicks it.

## Output

Return the smallest JSON that proves the job. Return only data needed for the authorized task; being visible in the UI alone does not justify disclosing it to another caller. Errors: short machine-readable `code` plus a safe message; no stack traces, no SQL, no tokens.

## Mixed agents

In-page agents in iframes are not the browser agent. `exposedTo` is an allowlist, not a hide-from-browser switch. Do not put privileged admin tools on a document that ordinary users load.

Validate arguments at the domain boundary; a tool schema is not enforcement. For writes, retain the product's idempotency/retry policy and reconcile uncertain outcomes before retrying. Registration and cancellation details are in [webmcp.md](webmcp.md).
