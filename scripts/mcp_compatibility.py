#!/usr/bin/env python3
"""Validate the reviewed MCP compatibility decision without starting servers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = Path(".agentic/mcp-compatibility.json")
PROJECT_MCP_PATH = Path(".mcp.json")
PORTABLE_MCP_PATH = Path("mcp.json")
CORE_SERVERS = {"perplexity", "firecrawl", "playwright"}
TRANSPORTS = {"stdio", "streamable-http", "sse"}
PORTABLE_STATES = {"blocked", "approved"}
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class MCPCompatibilityError(ValueError):
    """Raised when the compatibility decision or project configuration drifts."""


def _load_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise MCPCompatibilityError(f"Cannot read valid JSON from {path}: {error}") from error
    if not isinstance(payload, dict):
        raise MCPCompatibilityError(f"{path} must contain a JSON object")
    return payload


def _require_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    if missing:
        raise MCPCompatibilityError(f"{label} is missing: {', '.join(missing)}")


def _require_string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise MCPCompatibilityError(f"{label} must be a string array")
    if nonempty and not value:
        raise MCPCompatibilityError(f"{label} must not be empty")
    return value


def _package_arg_matches(package: str, argument: str) -> bool:
    return argument == package or argument.startswith(f"{package}@")


def _validate_project_config(
    root: Path,
    policy: dict[str, Any],
    *,
    allow_disabled: bool = False,
) -> list[str]:
    project_path = root / PROJECT_MCP_PATH
    project = _load_object(project_path)
    if set(project) != {"mcpServers"} or not isinstance(project["mcpServers"], dict):
        raise MCPCompatibilityError(".mcp.json must contain only an mcpServers object")

    configured = project["mcpServers"]
    if allow_disabled and not configured:
        return []
    if set(configured) != CORE_SERVERS:
        raise MCPCompatibilityError(
            ".mcp.json core servers drifted: expected "
            + ", ".join(sorted(CORE_SERVERS))
        )

    credential_names: list[str] = []
    for server_name in sorted(CORE_SERVERS):
        server_policy = policy["servers"][server_name]
        server = configured[server_name]
        if not isinstance(server, dict):
            raise MCPCompatibilityError(f".mcp.json {server_name} must be an object")
        runtime = server_policy["runtime"]
        if server.get("command") != runtime["command"]:
            raise MCPCompatibilityError(
                f".mcp.json {server_name} command does not match reviewed runtime"
            )
        args = _require_string_list(server.get("args"), f".mcp.json {server_name}.args", nonempty=True)
        package = server_policy["package"]
        if not any(_package_arg_matches(package, argument) for argument in args):
            raise MCPCompatibilityError(
                f".mcp.json {server_name} does not resolve reviewed package {package}"
            )

        env = server.get("env", {})
        if not isinstance(env, dict) or not all(
            isinstance(key, str) and isinstance(value, str) for key, value in env.items()
        ):
            raise MCPCompatibilityError(f".mcp.json {server_name}.env must contain strings")
        for key, value in env.items():
            if not value.startswith("$" + "{") or not value.endswith("}"):
                raise MCPCompatibilityError(
                    f".mcp.json {server_name}.{key} must use an environment reference"
                )

        expected_credentials = set(server_policy["credential_environment"])
        if not expected_credentials.issubset(env):
            missing = ", ".join(sorted(expected_credentials - set(env)))
            raise MCPCompatibilityError(
                f".mcp.json {server_name} is missing credential reference(s): {missing}"
            )
        credential_names.extend(sorted(expected_credentials))

    playwright_args = configured["playwright"]["args"]
    if "--isolated" not in playwright_args:
        raise MCPCompatibilityError(".mcp.json playwright must preserve isolated mode")
    return credential_names


def validate(root: Path = ROOT, *, allow_disabled: bool = False) -> dict[str, Any]:
    root = root.resolve()
    policy = _load_object(root / POLICY_PATH)
    _require_keys(
        policy,
        {
            "schema_version",
            "reviewed_at",
            "decision",
            "agent_plugins",
            "protocol",
            "clients",
            "servers",
            "reconsider_when",
        },
        "MCP compatibility policy",
    )
    if policy["schema_version"] != 1:
        raise MCPCompatibilityError("MCP compatibility schema_version must be 1")
    if not isinstance(policy["reviewed_at"], str) or not DATE_PATTERN.fullmatch(
        policy["reviewed_at"]
    ):
        raise MCPCompatibilityError("MCP compatibility reviewed_at must use YYYY-MM-DD")

    decision = policy["decision"]
    if not isinstance(decision, dict):
        raise MCPCompatibilityError("MCP compatibility decision must be an object")
    _require_keys(
        decision,
        {
            "portable_packaging",
            "root_mcp_manifest",
            "reason",
            "human_approval_required",
        },
        "MCP compatibility decision",
    )
    if decision["portable_packaging"] not in PORTABLE_STATES:
        raise MCPCompatibilityError("portable_packaging must be blocked or approved")
    if decision["human_approval_required"] is not True:
        raise MCPCompatibilityError("portable MCP packaging must remain human-gated")

    agent_plugins = policy["agent_plugins"]
    if not isinstance(agent_plugins, dict):
        raise MCPCompatibilityError("agent_plugins must be an object")
    if agent_plugins.get("version") != "1.0.0":
        raise MCPCompatibilityError("compatibility policy must target Agent Plugins 1.0.0")
    if agent_plugins.get("credential_reference_supported") is not False:
        raise MCPCompatibilityError(
            "Agent Plugins 1.0 must not claim a portable credential reference"
        )
    if agent_plugins.get("oauth_configuration_supported") is not False:
        raise MCPCompatibilityError(
            "Agent Plugins 1.0 must not claim portable OAuth configuration"
        )
    transports = set(
        _require_string_list(
            agent_plugins.get("portable_transports"),
            "agent_plugins.portable_transports",
            nonempty=True,
        )
    )
    if not transports.issubset(TRANSPORTS):
        raise MCPCompatibilityError("agent_plugins contains an unknown transport")
    if set(agent_plugins.get("allowed_placeholders", [])) != {
        "PLUGIN_ROOT",
        "PLUGIN_DATA",
    }:
        raise MCPCompatibilityError(
            "Agent Plugins 1.0 permits only PLUGIN_ROOT and PLUGIN_DATA placeholders"
        )

    protocol = policy["protocol"]
    if not isinstance(protocol, dict) or protocol.get("target_revision") != "2026-07-28":
        raise MCPCompatibilityError("protocol target_revision must be 2026-07-28")
    if protocol.get("adoption") != "human_gated":
        raise MCPCompatibilityError("MCP protocol adoption must remain human-gated")
    if protocol.get("runtime_availability_is_authority") is not False:
        raise MCPCompatibilityError("runtime availability must not imply authority")

    clients = policy["clients"]
    if not isinstance(clients, dict) or set(clients) != {"claude-code", "codex"}:
        raise MCPCompatibilityError("client matrix must cover Claude Code and Codex")
    for client_name, client in clients.items():
        if not isinstance(client, dict):
            raise MCPCompatibilityError(f"client {client_name} must be an object")
        client_transports = set(
            _require_string_list(
                client.get("transports"),
                f"clients.{client_name}.transports",
                nonempty=True,
            )
        )
        if not client_transports.issubset(TRANSPORTS):
            raise MCPCompatibilityError(f"client {client_name} has an unknown transport")
        if client.get("portable_plugin_mcp_verified") is not False:
            raise MCPCompatibilityError(
                f"client {client_name} portable MCP must remain unverified until tested"
            )

    servers = policy["servers"]
    if not isinstance(servers, dict) or set(servers) != CORE_SERVERS:
        raise MCPCompatibilityError(
            "server matrix must cover exactly: " + ", ".join(sorted(CORE_SERVERS))
        )
    for server_name, server in servers.items():
        if not isinstance(server, dict):
            raise MCPCompatibilityError(f"server {server_name} must be an object")
        _require_keys(
            server,
            {
                "official_source",
                "package",
                "observed_version",
                "source_blob",
                "runtime",
                "transports",
                "project_transport",
                "credential_environment",
                "credential_required_for_project_contract",
                "declared_protocol_revision",
                "sdk_evidence",
                "verified_target_revision",
                "portable_decision",
                "blockers",
            },
            f"server {server_name}",
        )
        if not server["official_source"].startswith("https://github.com/"):
            raise MCPCompatibilityError(f"server {server_name} requires an official source")
        if not isinstance(server["package"], str) or not server["package"]:
            raise MCPCompatibilityError(f"server {server_name} package must be a string")
        if not isinstance(server["observed_version"], str) or not SEMVER_PATTERN.fullmatch(
            server["observed_version"]
        ):
            raise MCPCompatibilityError(f"server {server_name} observed_version is invalid")
        if not isinstance(server["source_blob"], str) or not SHA_PATTERN.fullmatch(
            server["source_blob"]
        ):
            raise MCPCompatibilityError(f"server {server_name} source_blob must be 40 hex")
        runtime = server["runtime"]
        if not isinstance(runtime, dict) or runtime.get("package_bundled") is not False:
            raise MCPCompatibilityError(
                f"server {server_name} must record that its package is not bundled"
            )
        server_transports = set(
            _require_string_list(
                server["transports"], f"servers.{server_name}.transports", nonempty=True
            )
        )
        if not server_transports.issubset(TRANSPORTS):
            raise MCPCompatibilityError(f"server {server_name} has an unknown transport")
        if server["project_transport"] not in server_transports:
            raise MCPCompatibilityError(
                f"server {server_name} project transport is not supported"
            )
        _require_string_list(
            server["credential_environment"],
            f"servers.{server_name}.credential_environment",
        )
        if server["verified_target_revision"] is not False:
            raise MCPCompatibilityError(
                f"server {server_name} target revision is not yet verified"
            )
        if server["portable_decision"] not in PORTABLE_STATES:
            raise MCPCompatibilityError(
                f"server {server_name} portable_decision must be blocked or approved"
            )
        blockers = _require_string_list(
            server["blockers"], f"servers.{server_name}.blockers"
        )
        if server["portable_decision"] == "blocked" and not blockers:
            raise MCPCompatibilityError(f"blocked server {server_name} needs blockers")

    if decision["portable_packaging"] == "blocked":
        if any(server["portable_decision"] != "blocked" for server in servers.values()):
            raise MCPCompatibilityError("blocked package decision requires blocked servers")
        if (root / PORTABLE_MCP_PATH).exists():
            raise MCPCompatibilityError(
                "root mcp.json must remain absent while portable packaging is blocked"
            )
        if decision["root_mcp_manifest"] != "absent":
            raise MCPCompatibilityError("blocked package decision must record absent mcp.json")

    reconsider = _require_string_list(
        policy["reconsider_when"], "reconsider_when", nonempty=True
    )
    credential_names = _validate_project_config(
        root,
        policy,
        allow_disabled=allow_disabled,
    )
    return {
        "schema_version": 1,
        "verdict": "pass",
        "reviewed_at": policy["reviewed_at"],
        "portable_packaging": decision["portable_packaging"],
        "root_mcp_manifest": decision["root_mcp_manifest"],
        "target_protocol_revision": protocol["target_revision"],
        "servers": [
            {
                "name": name,
                "package": server["package"],
                "observed_version": server["observed_version"],
                "portable_decision": server["portable_decision"],
                "blocker_count": len(server["blockers"]),
            }
            for name, server in sorted(servers.items())
        ],
        "credential_references": sorted(set(credential_names)),
        "reconsider_trigger_count": len(reconsider),
        "server_execution_performed": False,
        "mutation_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--allow-disabled",
        action="store_true",
        help="Accept an empty MCP server map while still rejecting unreviewed entries",
    )
    args = parser.parse_args(argv)
    try:
        report = validate(args.root, allow_disabled=args.allow_disabled)
    except MCPCompatibilityError as error:
        if args.json:
            print(
                json.dumps(
                    {
                        "verdict": "fail",
                        "error": str(error),
                        "server_execution_performed": False,
                        "mutation_performed": False,
                    },
                    indent=2,
                )
            )
        else:
            print(f"MCP compatibility validation failed: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            "MCP compatibility policy valid "
            f"(reviewed {report['reviewed_at']}; protocol "
            f"{report['target_protocol_revision']})"
        )
        print(f"Portable packaging: {report['portable_packaging'].upper()}")
        for server in report["servers"]:
            print(
                f"- {server['name']}: {server['portable_decision'].upper()} "
                f"({server['package']} {server['observed_version']}; "
                f"{server['blocker_count']} blockers)"
            )
        print("PASS  Project .mcp.json remains separate and credential values were not read.")
        print("PASS  No MCP server was installed, started, connected, or authenticated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
