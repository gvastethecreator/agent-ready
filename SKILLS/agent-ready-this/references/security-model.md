# Security model

## Threats

- prompt or tool-description injection;
- over-broad tools and confused deputy behavior;
- missing per-user authorization;
- cross-tenant state handle access;
- secret leakage through metadata, errors, logs, or tool results;
- arbitrary code/shell execution;
- SSRF and unrestricted network access;
- unsafe local MCP startup commands;
- destructive retries without idempotency;
- hidden side effects or inadequate human confirmation;
- stale generated contracts that misrepresent real permissions.

## Mandatory controls

### Tool design

- one focused operation per tool;
- closed, narrow input schemas;
- semantic names and explicit side effects;
- read-only and mutating tools separated;
- structured, bounded outputs;
- no general-purpose shell, SQL, filesystem, or HTTP proxy tools by default.

### Identity and permission

- authenticate all private/user-specific remote calls;
- authorize every operation and object, not just the connection;
- derive user identity from verified credentials, never a caller-supplied field;
- bind state handles to the authenticated principal;
- use minimum scopes and short-lived credentials;
- preserve tenant boundaries.

### Consequential actions

- expose preview/dry-run where possible;
- describe effects before execution;
- require the applicable confirmation for irreversible, external, financial, destructive, or public actions; reuse existing authorization within its scope;
- use idempotency keys and deduplication;
- support cancellation and timeout.

### Local execution

- show exact startup commands;
- avoid remote package execution shortcuts in generated configs when a pinned local install is possible;
- prefer stdio for a single local client;
- sandbox filesystem/network/process access;
- never inherit more privileges than required.

### Observability

- log actor, tool, sanitized arguments, outcome, duration, correlation/idempotency ID;
- never log credentials or unnecessary personal data;
- add rate limits and anomaly alerts for expensive or externally visible tools.

## Runtime apply blockers

Keep only the affected runtime operation pending when:

- auth or ownership boundaries cannot be determined;
- a mutating tool has no confirmation and retry policy;
- implementation would duplicate/bypass the domain layer;
- tests cannot isolate the action;
- a local server requires opaque or unpinned startup code;
- secrets are present in tracked files or proposed metadata.
