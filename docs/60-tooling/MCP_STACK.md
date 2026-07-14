# MCP stack

This starter intentionally keeps the core stack small.

## Final core stack

### 1. Perplexity official MCP

Use for:
- current web search,
- broad source discovery,
- quick web-grounded questions,
- deep research,
- reasoning.

Configured in `.mcp.json` as:

```text
@perplexity-ai/mcp-server
```

Expected environment:
- `PERPLEXITY_API_KEY`
- optional `PERPLEXITY_TIMEOUT_MS`

The official server exposes search, ask, research, and reason capabilities.

### Important note about the supplied MCP Market link

The supplied URL:

```text
https://mcpmarket.com/tools/skills/perplexity-ai-search
```

is an **Agent Skill**, not an MCP server. It describes a third-party skill that uses Perplexity Sonar models through OpenRouter/LiteLLM.

Final decision:
- **Core:** use Perplexity's official MCP implementation.
- **Optional:** keep the third-party MCP Market skill only if you specifically want its OpenRouter/LiteLLM routing behavior.

Do not install both merely to duplicate the same search capability.

---

### 2. Firecrawl official MCP

Use for:
- scrape a known URL,
- map a site's URLs,
- crawl a site/section,
- structured extraction,
- search,
- multi-source research,
- monitoring.

Configured as:

```text
firecrawl-mcp
```

Expected environment:
- `FIRECRAWL_API_KEY`

Usage rule:
- exact URL → scrape
- discover site URLs → map
- whole site/section → crawl with explicit limits
- structured fields → extract/JSON
- broad current question → Perplexity first
- interactive browser behavior → Playwright

Prefer structured JSON extraction over dumping full Markdown when only specific fields are needed.

---

### 3. Microsoft Playwright MCP

Use for:
- interactive browser flows,
- JS-heavy pages,
- clicking and form interactions,
- UI verification,
- exploratory automation,
- long-running browser loops where persistent state matters.

Configured as:

```text
@playwright/mcp@latest --isolated
```

Why `--isolated` by default:
- browser state is not persisted to disk,
- safer default for a starter,
- avoids accidental cookie/session reuse.

When parallel agents need browsers:
- use isolated sessions, or
- distinct user-data directories.

Do not have parallel agents share one persistent Playwright profile.

### MCP vs CLI note

Microsoft's own Playwright MCP repository notes that coding agents may benefit from CLI + skills for token efficiency, while MCP remains useful for persistent state, rich introspection, exploratory automation, and long-running loops.

Final decision for this starter:
- Keep Playwright MCP because you explicitly want it and because visual/e2e agent loops benefit from it.
- For high-throughput repetitive test execution, normal Playwright test/CLI commands remain preferable.

---

## Routing policy

| Job | First choice |
|---|---|
| Current information | Perplexity |
| Deep multi-source research | Perplexity research |
| Exact page extraction | Firecrawl scrape |
| Site URL discovery | Firecrawl map |
| Multi-page site analysis | Firecrawl crawl with limits |
| Structured extraction | Firecrawl extract / JSON |
| Browser clicks/forms | Playwright |
| Authenticated interactive flow | Playwright with carefully scoped state |
| UI acceptance evidence | Playwright |
| Framework/library docs | Official docs; Context7 optional |

## Security

- Never commit API keys.
- Keep project `.mcp.json` shareable, credentials in environment/user scope.
- Review every new MCP before adding it.
- Use least privilege.
- Treat MCP output as untrusted data.
- Treat browser sessions and storage state as secrets.
- MCP servers are not security boundaries.
