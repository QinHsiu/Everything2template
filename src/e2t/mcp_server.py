"""Optional MCP stdio server (no heavy deps — JSON-RPC lite over stdin/stdout).

Compatible enough for simple agent wiring. For full MCP SDK, install `mcp` and
wrap these tool functions.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from e2t.adapt import PLATFORMS, build_writer_brief, skeleton_article
from e2t.compliance import check_compliance
from e2t.humanize import humanize
from e2t.ingest import ingest
from e2t.validate import validate_article


TOOLS = [
    {
        "name": "e2t_ingest",
        "description": "Ingest URL/file/project/text into CIR JSON",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "hint": {"type": "string"},
            },
            "required": ["source"],
        },
    },
    {
        "name": "e2t_adapt",
        "description": "Build platform skeleton + writer brief from CIR dict",
        "inputSchema": {
            "type": "object",
            "properties": {
                "cir": {"type": "object"},
                "platform": {"type": "string", "enum": list(PLATFORMS)},
                "voice": {"type": "string"},
            },
            "required": ["cir", "platform"],
        },
    },
    {
        "name": "e2t_humanize",
        "description": "Reduce Chinese AI-flavor phrases",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "e2t_validate",
        "description": "Validate platform draft + compliance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["platform", "text"],
        },
    },
    {
        "name": "e2t_list_platforms",
        "description": "List supported platforms",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _call_tool(name: str, arguments: dict[str, Any]) -> Any:
    if name == "e2t_ingest":
        cir = ingest(arguments["source"], hint=arguments.get("hint"))
        return cir.model_dump()
    if name == "e2t_adapt":
        from e2t.cir import CIR

        cir = CIR.model_validate(arguments["cir"])
        platform = arguments["platform"]
        return {
            "brief": build_writer_brief(cir, platform, voice=arguments.get("voice")),
            "draft": skeleton_article(cir, platform),
        }
    if name == "e2t_humanize":
        r = humanize(arguments["text"])
        return {
            "text": r.text,
            "replacements": r.replacements,
            "removed": r.removed,
        }
    if name == "e2t_validate":
        v = validate_article(arguments["platform"], arguments["text"])
        c = check_compliance(arguments["text"], platform=arguments["platform"])
        return {**v.to_dict(), "compliance": c.to_dict()}
    if name == "e2t_list_platforms":
        return {"platforms": list(PLATFORMS)}
    raise ValueError(f"Unknown tool: {name}")


def _reply(msg_id: Any, result: Any) -> None:
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": result}) + "\n")
    sys.stdout.flush()


def _error(msg_id: Any, code: int, message: str) -> None:
    sys.stdout.write(
        json.dumps(
            {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}
        )
        + "\n"
    )
    sys.stdout.flush()


def main() -> None:
    """Minimal JSON-RPC loop: tools/list, tools/call, initialize, ping."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method")
        msg_id = req.get("id")
        params = req.get("params") or {}
        try:
            if method in {"initialize", "notifications/initialized"}:
                if msg_id is not None:
                    _reply(
                        msg_id,
                        {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "everything2template", "version": "0.2.0"},
                        },
                    )
            elif method == "tools/list":
                _reply(msg_id, {"tools": TOOLS})
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments") or {}
                result = _call_tool(name, args)
                _reply(
                    msg_id,
                    {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    },
                )
            elif method == "ping":
                _reply(msg_id, {})
            elif msg_id is not None:
                _error(msg_id, -32601, f"Method not found: {method}")
        except Exception as exc:  # noqa: BLE001
            if msg_id is not None:
                _error(msg_id, -32000, str(exc))


if __name__ == "__main__":
    main()
