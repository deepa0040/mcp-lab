"""Smoke test: launches server.py over stdio and calls every tool.

Run:  python test_client.py
Uses a throwaway database so your real notes.db is untouched.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

HERE = Path(__file__).parent


def show(label: str, result) -> None:
    print(f"\n--- {label}")
    if result.is_error:
        print("ERROR:", result.content[0].text)
    else:
        print(json.dumps(result.structured_content, indent=2))


async def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        params = StdioServerParameters(
            command=sys.executable,
            args=[str(HERE / "server.py")],
            env={**os.environ, "NOTES_DB": str(Path(tmp) / "test.db")},
        )
        async with Client(params) as client:
            tools = await client.list_tools()
            print("Tools:", [t.name for t in tools.tools])
            print("\nadd_note input schema:")
            add = next(t for t in tools.tools if t.name == "add_note")
            print(json.dumps(add.input_schema, indent=2))

            show("add_note", await client.call_tool("add_note", {"title": "Buy milk", "kind": "todo"}))
            show("add_note", await client.call_tool("add_note", {"title": "MCP ideas", "body": "Try resources next"}))
            show("list_notes", await client.call_tool("list_notes", {}))
            show("search_notes 'mcp'", await client.call_tool("search_notes", {"query": "mcp"}))
            show("delete_note 1", await client.call_tool("delete_note", {"note_id": 1}))
            show("delete_note 999 (expect error)", await client.call_tool("delete_note", {"note_id": 999}))
            show("add_note bad kind (expect error)", await client.call_tool("add_note", {"title": "x", "kind": "banana"}))


asyncio.run(main())