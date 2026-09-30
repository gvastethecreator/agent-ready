---
name: web-agent-ready
description: "In-page agent tools. Use to add or audit WebMCP, document.modelContext, and agent-callable HTML forms in a running web product."
---

# Web Agent-Ready

Expose useful page actions to browser agents through the same logic and visible state that people use. This skill owns the **in-page agent surface**.

## Routing and scope

- Repository guidance and coding-agent workflows: `agent-ready-this`, when available.
- Whole-site readiness audit across crawlers, fetch, browser, and API agents: `agent-ready-site`, when available.
- Public search and citation content: `ai-seo`.
- Provider credentials or BYOK: `browser-secret-boundary-readiness`.
- Missing labels, roles, or keyboard paths: `better-accessibility`.
- Jobs that must work without an open page: assess the existing backend API or MCP surface.

For a mixed request, handle each authorized part with its owner. A routing decision does not end the user's broader task. An audit produces findings; an implementation request authorizes the scoped local changes.

WebMCP remains experimental. Before writing API code, read [webmcp.md](references/webmcp.md), check the target browser and current official documentation, and record the contract used. A draft signature is not proof of browser support. Feature detection preserves the existing human path; do not ship a fake platform API or retry mutations through guessed signatures.

## Process

1. **Map the requested journeys.**
   Inspect the owning routes, visible controls, client/domain functions, roles, and success or failure states. Select meaningful jobs such as search, filter, or prepare a booking; avoid a tool for every button.
   **Done:** each proposed tool has a job, owning view, valid state, caller, and side-effect boundary.

2. **Choose the smallest interface.**
   For an existing native form, read [declarative.md](references/declarative.md). For other page actions, use imperative registration. Keep one primary tool per operation; complementary filters and submission can be separate jobs.
   **Done:** tool names, inputs, outputs, and ownership are clear, with no duplicate operation under another name.

3. **Implement through existing product logic.**
   Detect the methods actually used, after the client document exists. Register only in the permitted document and live view. Validate input with the product's schema and retain server authorization. Update the same state and feedback as the human path. Use existing types; add a type package only if needed and compatible with the target API.
   **Done:** valid calls produce truthful results, invalid calls produce bounded errors, and unsupported browsers retain the working UI.

4. **Define registration and execution lifetimes.**
   Remove tools when their view or access ends. Separately cancel work that must stop on route leave, logout, or user cancellation; registration cleanup alone does not establish that behavior. Prevent stale async completions from updating a departed view.
   **Done:** discovery follows view ownership, execution follows the stated cancellation policy, and interrupted side effects are not reported as rolled back without proof.

5. **Preserve user control.**
   Read [security.md](references/security.md) for authorization, consequential actions, untrusted output, and cross-origin exposure. Preserve the product's confirmation policy and the user's existing authorization. Keep required review visible; hints and tool descriptions do not enforce permission.
   **Done:** each tool has bounded arguments and results, honest side effects, and the applicable confirmation, retry, and recovery behavior.

6. **Verify at closeout.**
   Follow [verify.md](references/verify.md). Observe discovery, one representative execution per changed risk, UI/result agreement, lifecycle, and the relevant failure path. Test the normal human path in the same desktop viewport. Add sizes only when responsive behavior changed.
   **Done:** the report distinguishes native execution, lifecycle tests, and markup inspection, with exact untested boundaries.

## References

- [webmcp.md](references/webmcp.md): API drift, registration, execution, cancellation, and types.
- [declarative.md](references/declarative.md): form annotations, submission, and result handling.
- [security.md](references/security.md): identity, effects, consent, origins, and output trust.
- [verify.md](references/verify.md): evidence levels and checks.
