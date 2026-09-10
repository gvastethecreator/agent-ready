# Vendor adapters

## Goal

Support many coding agents without making every client file a separate source of truth.

## Adapter contract

Each adapter definition contains:

```json
{
  "id": "example-client",
  "detect": ["paths or commands"],
  "instruction_paths": [],
  "skill_paths": [],
  "agent_paths": [],
  "hook_paths": [],
  "mcp_config_paths": [],
  "supports_agents_md": true,
  "supports_open_agent_skills": true,
  "last_verified": "YYYY-MM-DD",
  "sources": []
}
```

## Rendering policy

1. Prefer native support for root/nested `AGENTS.md`.
2. Prefer a shared `.agents/skills/` location when the detected client supports it.
3. Create client-specific files only for unsupported features or client-only metadata.
4. Never create symlinks by default.
5. Mark generated adapters and store their source hash in the manifest.
6. Warn when two clients would load contradictory rules.

## Initial support tiers

### Tier 1

- Codex/OpenAI
- Claude Code
- Cursor
- GitHub Copilot
- OpenCode

### Tier 2

- Windsurf/Devin Desktop
- Cline
- Kiro
- Aider
- additional clients registered through data, not conditionals scattered through code

## Separation of concerns

- Instructions answer “what constraints always apply?”
- Skills answer “how do I perform this workflow?”
- Subagents/custom agents answer “which isolated role should own this task?”
- Hooks answer “what deterministic event/check must run?”
- MCP answers “which external tools/data can the agent call?”

Do not collapse these into one giant prompt file.
