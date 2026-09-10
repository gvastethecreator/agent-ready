# Imperative WebMCP

## Check the target contract

Reviewed 2026-09-08 against the [community draft](https://webmachinelearning.github.io/webmcp/) dated 2026-09-04 and [Chrome's imperative guide](https://developer.chrome.com/docs/ai/webmcp/imperative-api) updated 2026-09-01. These sources differ:

- Chrome documents `executeTool(tool, JSON.stringify(args), options)`.
- The draft describes an object argument. Do not copy that signature into a Chrome integration without checking the target build.
- Chrome documents unregistering without cancelling in-flight execution from Chrome 153. Treat removal and cancellation as separate operations.

Record browser/build, enablement, API signatures, and source date. Recheck before implementation. Use one verified contract; do not try both signatures on a real action. If native access is unavailable, limit the evidence claim to the checks actually run.

## Registration sketch

Client-side JavaScript sketch; `parseFilterInput`, `applyVisibleFilter`, and `reportToolError` are existing application functions to supply, not bundled implementations:

```js
function mountFilterTool() {
  const lifetime = new AbortController();
  const cleanup = () => lifetime.abort();
  if (typeof document === "undefined" ||
      typeof document.modelContext?.registerTool !== "function") return cleanup;

  void document.modelContext.registerTool({
    name: "filter-results",
    description: "Filter the visible results by query and show the matches.",
    inputSchema: {
      type: "object",
      properties: { query: { type: "string", maxLength: 200 } },
      required: ["query"],
      additionalProperties: false,
    },
    annotations: { readOnlyHint: false, untrustedContentHint: false },
    async execute(input, { signal }) {
      const query = parseFilterInput(input);
      const workSignal = AbortSignal.any([signal, lifetime.signal]);
      workSignal.throwIfAborted();
      const items = await applyVisibleFilter(query, { signal: workSignal });
      workSignal.throwIfAborted();
      return { count: items.length, ids: items.map(item => item.id) };
    },
  }, { signal: lifetime.signal }).catch(error => {
    if (!lifetime.signal.aborted) reportToolError(error);
  });

  return cleanup;
}
```

The application function must check cancellation before committing visible state. Combining signals makes view leave cancel this example's work even where unregistering alone would let it finish. Cancellation cannot undo a server action that already committed; reconcile its actual status before retrying.

Mount once per owning view, clean up before replacement, and use current state rather than stale closures. On auth loss, remove the tool and stop unauthorized pending work. In React, return cleanup from the effect; ensure dependencies update the tool when its inputs or scope change. In SSR, run only on the client.

A rejected registration needs a reported cause, not a silent success: inspect duplicate names, inactive documents, origin isolation, and `tools` policy. Keep errors free of credentials or private payloads.

## Discovery and manual execution

For the Chrome contract documented above, in the live owner document:

```js
const tools = await document.modelContext.getTools();
const tool = tools.find(item => item.name === "filter-results");
if (!tool) throw new Error("Expected page tool is missing");
const stop = new AbortController();
const result = await document.modelContext.executeTool(
  tool, JSON.stringify({ query: "spring" }), { signal: stop.signal },
);
```

Use the discovered tool object. Interpret the result according to the tested contract; navigation can yield `null`, and a returned string is not necessarily JSON to parse. Inspect the new page when navigation is part of the job. Listen for `toolchange` only while the consumer is mounted.

## Types and enablement

Check the [Chrome setup guide](https://developer.chrome.com/docs/ai/webmcp) for current trial/flag requirements. Record actual enablement. Do not infer availability from a version number, enable flags, relaunch a user browser, or enroll an origin without the required authority.

Use the project's existing compatible types. If missing, inspect the documented `webmcp-types` package before adding it with the repo package manager. Preserve existing `compilerOptions.types` entries. Types describe a contract; they do not enable browser support.

For cross-origin tools, read [security.md](security.md). A backend MCP server and a production polyfill are separate interfaces, not evidence of native WebMCP support.
