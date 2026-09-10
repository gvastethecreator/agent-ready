// Wiring sketch: use the target browser's compatible WebMCP declarations.
// Supply a real tool that validates inputs and calls the existing product logic.
type PageTool = Parameters<Document["modelContext"]["registerTool"]>[0];

export async function registerAgentTool(
  tool: PageTool,
  lifetime: AbortController,
): Promise<void> {
  if (typeof document === "undefined" ||
      typeof document.modelContext?.registerTool !== "function") return;

  await document.modelContext.registerTool({
    ...tool,
    execute: async (input, options) => {
      const signal = AbortSignal.any([options.signal, lifetime.signal]);
      signal.throwIfAborted();
      const result = await tool.execute(input, { ...options, signal });
      signal.throwIfAborted();
      return result;
    },
  }, { signal: lifetime.signal });
}

// The view owns lifetime and aborts it on cleanup; observe registration rejection.
// Tool logic must check its signal before committing UI state.
// Aborting cannot undo a server write that already committed.
