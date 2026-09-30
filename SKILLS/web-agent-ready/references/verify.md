# Verify Web Agent-Ready

## Evidence levels

- `native tools verified`: the target browser discovered and executed the changed jobs; results, UI, lifecycle, and relevant failure states were observed.
- `lifecycle verified`: tests exercised registration, cleanup, execution cancellation, and schemas; native execution remains untested.
- `markup only`: form annotations were inspected, but browser synthesis was not exercised.
- `not applicable`: no in-page agent job belongs to this scope.

A skipped feature-detection branch, type installation, or valid schema cannot prove native execution. A failing test is failure evidence, not a passing verdict.

## Live check

Reuse one supported browser surface and the available profile. Use focused script evaluation for discovery and accessibility locators for the user flow. Record browser build, origin, role, route, enablement, and the API signature tested.

1. Open the owning view and inspect the tools expected there.
2. Invoke a safe representative call; check arguments, result, visible state, and console errors.
3. Exercise each changed side-effect boundary with authorized fixture data. Verify input rejection and any applicable confirmation before the effect.
4. Remove the view or its access and confirm the tool disappears. Separately cancel a pending call and verify that late completion does not corrupt UI state.
5. For a form without `toolautosubmit`, verify populated fields and the visible submit/review step. Test human submission too, and observe `toolcancel` when the user cancels or resets.
6. Confirm that the normal job still works without WebMCP. Use one desktop viewport unless responsive changes require another size.

Unregistration and in-flight cancellation require separate observations. An aborted request does not prove a remote write was undone. For calls that navigate, inspect the destination instead of treating `null` as a failed action.

Use the current browser's verified `getTools`/`executeTool` contract from [webmcp.md](webmcp.md). An available inspector extension can help; it is not a required dependency.

## Existing automated coverage

Extend existing tests only for uncovered changed behavior: missing platform methods, route/auth lifecycle, stale completion, invalid input, bounded errors, or consequential-action enforcement. A mock belongs only in tests and must match the chosen contract. Schema serialization alone does not validate the input domain.

Gate native CI checks on real capability detection and report skips. Do not replace skipped native checks with a claim that the app is agent-ready.

## Handoff

Report jobs and tool names, implementation form, changed behavior, evidence level, checks and skips, and unresolved limits. Keep captures in `.scratch/screenshots/<task-slug>/`; copy required durable evidence to its owner before removing the task capture folder. Do not generate an unrelated readiness report or follow-up skill chain.
