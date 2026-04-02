from __future__ import annotations

import httpx


class McpClient:
    def __init__(self, server_url: str, timeout: float = 20.0) -> None:
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout

    def list_tools(self) -> dict:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.server_url}/mcp/tools/list")
            response.raise_for_status()
            return response.json()

    def call_tool(self, name: str, arguments: dict) -> dict:
        payload = {"name": name, "arguments": arguments}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.server_url}/mcp/tools/call", json=payload)
            response.raise_for_status()
            return response.json()
