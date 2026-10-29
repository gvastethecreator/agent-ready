# Operate test

Attempt each do job through the available browser interface. Record whether the tested mode uses the accessibility tree, DOM locators or screenshots; results apply to that mode and client. A screenshot-based client's normal interaction is not itself degradation.

## Setup

- One available browser surface (built-in browser pane, Claude in Chrome, or Playwright) and one desktop viewport. Record browser, viewport, signed-in state, and consent choice.
- Follow the user's consent choice. Record restrictions and compare them with known owner intent (A4).
- Public jobs start from a fresh session. Signed-in jobs use a test account on the user's own app only.

## Per job

1. Open the allowed start URL. If supported, evaluate `scripts/dom_probe.js` and save its JSON beside `probe.json`; otherwise name the missing diagnostic.
2. Inspect controls in the tested mode. For DOM/tree flows, prefer accessible role/name locators and context.
3. Attempt the path. Repeated names can be valid in separate groups; confirm an actual ambiguity before reporting C1. Record any guess or recovery and its effect on the job.
4. Record the URL after every state change (C3) and each error, retry, or recovery.
5. Stop at the first consequential control: pay, place order, send, publish, delete, submit an application, or book. Confirm the review step is reachable and states the prepared result in text.

A denial, CAPTCHA or missing login authority ends that access path. Preserve it; do not switch tools, identities or browser surfaces to bypass it.

## C checks

- **C1 names and roles.** Controls on the path have meaningful names, semantics and state in context. Prefer native elements; custom widgets need keyboard behavior and correct semantics. dom_probe's `unnamed`, `ambiguous_names` and `clickable_non_semantic` are candidates for inspection, not computed accessibility results.
- **C2 forms.** A label per field, correct input types, `autocomplete` tokens for personal data, required fields marked, errors in text tied by `aria-describedby` with `aria-invalid`, entered values kept after an error. dom_probe: `unlabeled_fields`, `placeholder_only_fields`, `fields_without_autocomplete`.
- **C3 navigation state.** Check Back and reproducibility of state needed by the job. Put shareable state in URLs when appropriate; not every transient tab or selection needs a URL.
- **C4 blockers.** Consent wall before content, modal without a named close, hover-only menus, drag-only or canvas-only controls, scroll-only loading without a "load more" control or page links, session timeouts inside a multi-step job, core steps in cross-origin iframes (payment iframes are expected). dom_probe: `open_dialogs`, `canvas_large`, `cross_origin_iframes`.
- **C5 feedback.** Result counts, success, and error states appear as text, ideally in a live region; loading ends; disabled controls state why. dom_probe: `live_regions`.
- **C6 consequential gates.** A review step exists, shows totals or recipients in text, and the final control is clearly named. The agent should reach it, not pass it. A missing gate is a human-safety finding, not an agent-friendliness gain.
- **C7 in-page tools.** dom_probe records API/form markers only. They do not prove tool registration, authorization or execution. Consider the proposed WebMCP surface for a concrete repeated job and supported client; verify current browser/spec support. For requested implementation, register tools only while the owning view and access are active, use the existing domain action, validate arguments and server permissions, preserve required confirmation, then observe discovery, execution, cleanup and the human path.

## Outcomes

- `pass`: reached the agreed success signal or review step in the tested mode.
- `degraded`: reached it with an observed limitation, guess or recovery; state the effect.
- `fail`: an observed blocker prevented the intended job under available authority, including a challenge on an intended public path.
- `unknown`: not attempted or not decidable because authority, account or required evidence is missing. Name the gap; do not label an observed denial as an untested success.

Keep screenshots in the task's scratch folder; copy only what the report cites.
