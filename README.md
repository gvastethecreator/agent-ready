# Agent Ready

Three Agent Skills for making products easier for agents to use.

- `$agent-ready-this` audits and improves coding-agent guidance, project workflows, and justified runtime interfaces.
- `$agent-ready-site` audits how crawlers, fetch agents, browser agents, and API agents access, read, and operate a live site or web app.
- `$web-agent-ready` adds or audits in-page tools (WebMCP, `document.modelContext`, agent-callable forms).

## Quick start

```text
npx skills add gvastethecreator/agent-ready
```

Copy `SKILLS/agent-ready-this`, `SKILLS/agent-ready-site`, and `SKILLS/web-agent-ready` into the skill directory your agent already loads.

Optional helpers for `agent-ready-this` and `agent-ready-site`: Python 3.11+ and the standard library. See [assessment-cli.md](SKILLS/agent-ready-this/references/assessment-cli.md). Maintainer notes live in [docs/](docs/).

- [agent-ready-this](SKILLS/agent-ready-this/SKILL.md)
- [agent-ready-site](SKILLS/agent-ready-site/SKILL.md)
- [web-agent-ready](SKILLS/web-agent-ready/SKILL.md)

Attribution: [NOTICE.md](NOTICE.md). License: [MIT](LICENSE).
