# Project profiles

Use multi-label classification. A full-stack monorepo may be `web-app`, `api-service`, and `monorepo` simultaneously.

## Evidence sources

- root and nested manifests;
- lockfiles and workspace files;
- framework dependencies and config;
- source directory conventions;
- CI workflows;
- route/API definitions;
- auth middleware/providers;
- deployment config;
- documentation and public URLs;
- existing agent files and protocols.

## Profiles

### `static-site-or-docs`

Strong signals: content collections, Markdown/MDX, static-site generator, sitemap, documentation routes.

Likely modules: AGENTS, skills, llms.txt, Markdown alternates, link headers.

### `spa`

Strong signals: client-side framework without server routes, browser state, API client.

Likely modules: AGENTS, skills; WebMCP only for meaningful page-local actions; MCP belongs to the backend/API, not automatically to the SPA.

### `full-stack-web`

Strong signals: UI framework plus server routes/actions, auth, database.

Likely modules: baseline, contracts, WebMCP and/or MCP after capability review.

### `api-service`

Strong signals: HTTP/RPC server, controllers/routes, OpenAPI dependencies, service deployment.

Likely modules: baseline, OpenAPI/JSON Schema, MCP if reusable agent tools exist.

### `library-sdk`

Strong signals: publish config, public exports, examples, compatibility matrix.

Likely modules: baseline, API docs, task skills, machine-readable examples. Usually no WebMCP/MCP.

### `cli-tool`

Strong signals: bin entry, command parser, shell completion.

Likely modules: baseline, skills, `--json`, stable exit codes, non-interactive mode. MCP may wrap reusable functions but should not merely shell out unsafely.

### `monorepo`

Strong signals: workspaces, pnpm workspace, Nx, Turborepo, Bazel, Pants, multiple manifests.

Likely modules: root and nested AGENTS, scoped commands, package-specific skills.

### `agent-service`

Strong signals: task lifecycle, agent cards, model/tool orchestration, streaming, artifacts, delegation endpoints.

Likely modules: baseline, MCP for tools, A2A for agent collaboration, ARD for discovery, security/evals.

### `desktop-app`

Strong signals: Electron, Tauri, native packaging, IPC commands, filesystem access, auto-update, platform-specific build config.

Likely modules: baseline, platform-specific commands and security boundaries, packaging/release skills, local MCP only when it exposes narrow domain actions rather than arbitrary host access.

Typical Grill triggers: supported operating systems, privileged filesystem/process operations, signing/release ownership, and whether agent interfaces run inside or outside the desktop trust boundary.

### `game-or-visual-editor`

Strong signals: Phaser, Three.js, canvas/WebGL, asset pipelines, level/sprite/shader editors, deterministic export or preview workflows.

Likely modules: baseline, asset-processing and validation skills, visual regression/eval harnesses, project-specific viewers, MCP Apps only for a proven interactive inspection or approval workflow.

Typical Grill triggers: authoritative asset pipeline, generated-file ownership, acceptable visual-diff thresholds, and whether runtime agent actions modify source assets or only produce proposals.

## Confidence

- `high`: at least two independent strong signals.
- `medium`: one strong signal or several weak signals.
- `low`: naming/docs only, or conflicting evidence.

Do not promote a low-confidence runtime profile directly to `apply-runtime`.
