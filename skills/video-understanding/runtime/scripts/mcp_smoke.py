from __future__ import annotations

import asyncio
import sys

from mcp import Client


async def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/mcp"
    async with Client(url) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        required = {
            "start_video_analysis",
            "wait_video_analysis",
            "get_video_manifest",
            "get_video_transcript",
            "inspect_video_window",
        }
        print(f"MCP protocol: {client.protocol_version}")
        print("Tools:")
        for name in sorted(names):
            print(f"  - {name}")
        missing = sorted(required - names)
        if missing:
            print("Missing required tools:", ", ".join(missing))
            return 1
        print("MCP smoke test passed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
