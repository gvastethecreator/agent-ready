# Operate test

Observe whether a browser agent can finish each do job from the accessibility tree alone. The tree is what browser agents plan from; screenshots and coordinates are the fallback that makes a job `degraded`.

## Setup

- One available browser surface (built-in browser pane, Claude in Chrome, or Playwright) and one desktop viewport. Record browser, viewport, signed-in state, and consent choice.
- Decline non-essential cookies. If declining blocks the job, that is an A4 finding.
- Public jobs start from a fresh session. Signed-in jobs use a test account on the user's own app only.

## Per job

1. Open the start URL. Evaluate `scripts/dom_probe.js`; save its JSON beside `probe.json`.
2. Read the interactive accessibility tree. Plan the path using role and name only.
3. Act by element reference or locator. When the next control has no unique role and name, record a C1 ambiguity with the candidates, resolve it from a screenshot, and continue; the job is then at best `degraded`.
4. Record the URL after every state change (C3) and each error, retry, or recovery.
5. Stop at the first consequential control: pay, place order, send, publish, delete, submit an application, or book. Confirm the review step is reachable and states the prepared result in text.

A CAPTCHA on the path ends the attempt. Record where it appears; the CAPTCHA is the finding.

## C checks

- **C1 names and roles.** Every control on the path has a role and a unique, descriptive name; no div or span buttons; custom widgets expose state (expanded, selected, checked). dom_probe: `unnamed`, `ambiguous_names`, `clickable_non_semantic`. Fix native elements first; use ARIA only to name or state a custom widget, never to contradict native semantics.
- **C2 forms.** A label per field, correct input types, `autocomplete` tokens for personal data, required fields marked, errors in text tied by `aria-describedby` with `aria-invalid`, entered values kept after an error. dom_probe: `unlabeled_fields`, `placeholder_only_fields`, `fields_without_autocomplete`.
- **C3 state in URL.** Search, filter, sort, page, tab, and selected item reproduce from the URL; Back restores the prior state. An agent that cannot deep-link must replay the whole path.
- **C4 blockers.** Consent wall before content, modal without a named close, hover-only menus, drag-only or canvas-only controls, scroll-only loading without a "load more" control or page links, session timeouts inside a multi-step job, core steps in cross-origin iframes (payment iframes are expected). dom_probe: `open_dialogs`, `canvas_large`, `cross_origin_iframes`.
- **C5 feedback.** Result counts, success, and error states appear as text, ideally in a live region; loading ends; disabled controls state why. dom_probe: `live_regions`.
- **C6 consequential gates.** A review step exists, shows totals or recipients in text, and the final control is clearly named. The agent should reach it, not pass it. A missing gate is a human-safety finding, not an agent-friendliness gain.
- **C7 in-page tools.** dom_probe `webmcp` reports `document.modelContext` and `form[toolname]`. Suggest WebMCP only for repeated, high-value do jobs where C1–C5 cannot be fixed cheaply; it is experimental. Implementation: `web-agent-ready`.

## Outcomes

- `pass`: finished from the tree alone.
- `degraded`: finished with a screenshot or coordinate fallback, a guess, or at least one recovery.
- `fail`: could not reach the success state or review step.
- `unknown`: stopped by missing authority (login, payment, CAPTCHA); record where.

Keep screenshots in the task's scratch folder; copy only what the report cites.
