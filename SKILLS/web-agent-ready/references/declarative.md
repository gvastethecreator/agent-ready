# Declarative WebMCP

Annotate a real `<form>` so the browser synthesizes a tool from its fields. Prefer this when the human path is already a form. Imperative tools stay for JS-only jobs.

Sources checked 2026-09-08: [Chrome declarative guide](https://developer.chrome.com/docs/ai/webmcp/declarative-api) and [explainer](https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md). Recheck against the target browser before implementation.

The community draft leaves parts of form synthesis unspecified. Chrome documents an experimental implementation. Keep markup valid HTML even if the agent never sees it.

## Form

```html
<form
  toolname="search-flights"
  tooldescription="Search flights by origin, destination, and date, then show matching results on this page."
>
  <label>
    From
    <input
      name="origin"
      required
      autocomplete="address-level2"
      toolparamdescription="IATA code or city of departure"
    />
  </label>
  <label>
    To
    <input
      name="destination"
      required
      toolparamdescription="IATA code or city of arrival"
    />
  </label>
  <label>
    Date
    <input
      type="date"
      name="date"
      required
      toolparamdescription="Departure date in the user's local calendar"
    />
  </label>
  <button type="submit">Search</button>
</form>
```

- `toolname`: same rules as imperative `name` (kebab-case job id).
- `tooldescription`: when to use the form-tool.
- `toolautosubmit`: boolean. Agent may submit after fill without a human click. Omit for money, legal, delete, or send-to-others.
- `toolparamdescription` on each named control: schema property description.
- Control `name` becomes the schema property key. `required`, `min`, `max`, `step`, `type` feed synthesis (exact mapping is still moving).

Use native controls (`input`, `select`, `textarea`, `button`). A custom combobox with no `name` will not appear in the tool schema.

## Human confirmation

Without `toolautosubmit`, the agent fills and the browser focuses submit. Style the waiting form:

```css
form:tool-form-active { outline: 2px solid var(--focus, Highlight); }
form:tool-form-active :tool-submit-active { /* submit waiting for the user */ }
```

`:tool-form-active` matches while the declarative tool is running. `:tool-submit-active` matches that form's submit control. Support may lag the attributes; visible focus on submit is the fallback.

## Response without navigation

```js
form.addEventListener("submit", (event) => {
  if (!event.agentInvoked || typeof event.respondWith !== "function") return;
  event.preventDefault();
  event.respondWith(
    (async () => {
      const results = await searchFromForm(new FormData(form));
      renderResults(results);
      return { count: results.length, ids: results.map((row) => row.id) };
    })(),
  );
});
```

This sketch covers the agent branch. Integrate it into the existing submit handler so both callers share validation, domain logic, error feedback, and rendering without double submission. Call `preventDefault()` before `respondWith()`; `agentInvoked` identifies an agent submission.

## Response with navigation

Navigation result handling is not an interoperable JSON-LD contract. Verify the target browser and inspect the destination state; do not add a fabricated `SearchResult` schema or assume the first JSON-LD block becomes a tool result. Use `respondWith` for a same-page result only where supported.

## Lifecycle

Keep tool attributes stable during form fill. Verify removal, reset, and user cancellation in the target browser; distinguish form cancellation from a server operation that already committed.

Inspect the synthesized tool and its required fields in the target browser. Verify discovery and execution rather than assuming parity with imperative tools.
