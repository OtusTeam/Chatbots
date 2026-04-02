from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from mcp_server.crm_gateway import CrmGateway


crm_gateway = CrmGateway()
mcp = FastMCP("lesson.29 MCP server")
app = FastAPI(title="lesson.29 MCP server")


TOOLS = [
    {
        "name": "create_lead",
        "description": "Create lead in CRM and return normalized result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "comment": {"type": "string"},
                "source": {"type": "string"},
            },
            "required": ["name", "phone", "email"],
        },
    }
]


@mcp.tool
def create_lead(
    name: str,
    phone: str,
    email: str,
    comment: str = "",
    source: str = "mcp-bot",
) -> dict[str, object]:
    return crm_gateway.create_lead(
        name=name,
        phone=phone,
        email=email,
        comment=comment,
        source=source,
    )


# Mount FastMCP HTTP app in SSE mode for MCP-native clients.
app.mount("/mcp-sse", mcp.http_app(transport="sse"))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/mcp/tools/list")
def list_tools() -> dict[str, Any]:
    return {"tools": TOOLS}


@app.post("/mcp/tools/call")
def call_tool(payload: dict[str, Any]) -> dict[str, Any]:
    tool_name = str(payload.get("name", "")).strip()
    tool_args = payload.get("arguments") or {}
    if not isinstance(tool_args, dict):
        raise HTTPException(status_code=400, detail="arguments must be an object")

    if tool_name != "create_lead":
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

    try:
        result = crm_gateway.create_lead(
            name=str(tool_args.get("name", "")),
            phone=str(tool_args.get("phone", "")),
            email=str(tool_args.get("email", "")),
            comment=str(tool_args.get("comment", "")),
            source=str(tool_args.get("source", "mcp-bot")),
        )
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
    except Exception as err:  # defensive boundary for tool callers
        raise HTTPException(status_code=500, detail=f"create_lead failed: {err}") from err

    return {"ok": True, "tool": tool_name, "result": result}


@app.get("/mcp/sse")
def sse_stream() -> StreamingResponse:
    def event_stream() -> Any:
        message = json.dumps({"status": "ready", "tools": [t["name"] for t in TOOLS]}, ensure_ascii=False)
        yield f"event: ready\ndata: {message}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
