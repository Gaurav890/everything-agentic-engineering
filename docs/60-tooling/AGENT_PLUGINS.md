# Agent Plugins 1.0 packaging

The repository has an additive, skills-only portable package that follows the
[Agent Plugins Specification 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md).
It does not publish, install, enable, or execute the plugin automatically.

## Three separate contracts

| Surface | Purpose | Portable v1? |
|---|---|---|
| `plugin.json` | Closed Agent Plugins 1.0 manifest at the package root | Yes |
| `skills/` | Fixed portable skill-discovery location; resolves inside this repository to `.claude/skills/` | Yes |
| `.codex-plugin/plugin.json` | Existing Codex-native compatibility and interface metadata | No; maintained separately during the additive migration |
| `.mcp.json` | Claude/project-scoped MCP configuration with local environment-variable references | No |

The root manifest does not declare `skills`, hooks, commands, an interface, or
MCP servers inline. Agent Plugins v1 discovers skills from the fixed `skills/`
directory and portable MCP servers only from root `mcp.json`.

## Portable MCP decision

The project `.mcp.json` depends on local environment-variable placeholders and
client-specific launch behavior. Agent Plugins v1 only standardizes
`${PLUGIN_ROOT}` and `${PLUGIN_DATA}` expansion for portable stdio entries and
does not define a portable credential-reference or OAuth configuration field.
Copying `.mcp.json` would therefore create a misleading or unsafe package.

T-035 completed that compatibility review. Portable MCP packaging remains
blocked because no selected server currently satisfies all credential,
deterministic execution, protocol-evidence, and clean-client verification
gates. The plugin validator rejects root `mcp.json` while that decision is
blocked.

Run `./agentic doctor mcp` for the read-only machine decision. Read the complete
[MCP compatibility decision](MCP_COMPATIBILITY.md) before proposing any portable
server. Reconsideration requires new evidence and a separate human-approved PR;
do not copy project configuration into the package.

## Validation

Run the read-only package doctor:

```bash
./agentic doctor plugin
./agentic doctor plugin --json
```

It verifies:

- the canonical Agent Plugins 1.0 schema identifier;
- the closed root-manifest field set and plugin-name constraints;
- semantic package versioning required by this repository;
- skill discovery from immediate children of `skills/`;
- skill and symlink containment inside the plugin root;
- minimum skill frontmatter;
- the intentional absence of packaged MCP execution;
- the separate Codex-native compatibility surface.

The validator is offline. A client must select a locally supported schema and
must not fetch schemas while loading a plugin.

## Migration and release policy

This is an additive compatibility phase:

1. Keep the working Codex-native package while portable clients are tested.
2. Keep reusable skills canonical under `.claude/skills/` and expose them
   through the in-repository `skills/` link.
3. Test every supported client before removing a native compatibility surface.
4. Treat publishing, marketplace policy, installation, MCP execution, hooks,
   credentials, and runtime authority as separate human-reviewed decisions.

Do not claim a client is compatible merely because `plugin.json` parses. Test
that client's discovery, trust, permissions, and component behavior.

## Primary sources

- [Agent Plugins Specification 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md)
- [Canonical example and migration guide](https://github.com/agentplugins/agent-plugins-example)
- [Agent Skills specification](https://agentskills.io)
