# weather-mcp

A small [Model Context Protocol](https://modelcontextprotocol.io) server that wraps the free [Open-Meteo](https://open-meteo.com) API. No API key required.

It's a learning project covering async tools with `httpx`, timeouts, and error handling in an MCP server.

## Tools

| Tool | Arguments | Description |
|------|-----------|-------------|
| `get_current_weather` | `city: str` | Current conditions, temperature, feels-like, humidity and wind |
| `get_forecast` | `city: str`, `days: int = 3` (1-7) | Daily conditions, min/max temperature and precipitation |

Both tools look up the city with Open-Meteo's geocoding API, then fetch the weather for the first match.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended), or pip

## Setup

```bash
cd weather-mcp
uv sync
uv add "mcp[cli]<2"
```

Without uv:

```bash
pip install "mcp[cli]<2" httpx
```

> **Note:** this project targets `mcp` 1.x. In 2.x, `FastMCP` was renamed to `MCPServer` (`from mcp.server.mcpserver import MCPServer`) and other APIs changed, so the dependency is pinned to `<2`.

## Run and test

Open the MCP Inspector in your browser and call the tools interactively:

```bash
uv run mcp dev server.py
```

Run the server directly over stdio:

```bash
uv run server.py
```

## Connect to a client

Use the **absolute path** to the project folder.

### Claude Desktop

Add this to `claude_desktop_config.json`, then restart Claude Desktop:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/ABSOLUTE/PATH/TO/weather-mcp", "run", "server.py"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add weather -- uv --directory /ABSOLUTE/PATH/TO/weather-mcp run server.py
```

Then ask something like *"What's the weather in Delhi?"* or *"Give me a 5-day forecast for Tokyo."*

## How it works

- **Async I/O:** tools are `async def` and use `httpx.AsyncClient`.
- **Timeouts:** `httpx.Timeout(10.0, connect=5.0)` fails fast on unreachable hosts and allows time to read.
- **Error handling:** `_get_json()` converts timeouts, HTTP status errors, network errors and bad JSON into readable messages. FastMCP returns exceptions raised in a tool to the model as an error result (`isError=True`), so the model can explain or retry.
- **Validation:** `days` is range-checked, and unknown cities give a clear "no location found" error.

## Gotcha: don't write to stdout

The stdio transport uses stdout for protocol messages. A stray `print()` will corrupt the stream and break the connection. This project logs to **stderr** only.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named 'mcp.server.fastmcp'` | You have mcp 2.x installed. Run `uv add "mcp[cli]<2"` (or `pip install "mcp[cli]<2"`) |
| Server doesn't show up in Claude Desktop | Check the path is absolute, the JSON is valid, and restart the app fully |
| `uv: command not found` | Install uv, or use the full path to `uv` in the config |
| "Could not reach the weather service" | Check your internet connection and any firewall or proxy settings |
| Wrong city returned | Use a more specific name, e.g. `"Paris, Texas"` |

## Ideas for next steps

- Share one `AsyncClient` via a FastMCP `lifespan` instead of one per call
- Retry with backoff for transient failures
- Cache geocoding results
- Add currency (Frankfurter API) or news tools
- Return structured output (Pydantic models) instead of formatted strings
- Add tests with `pytest` and `respx` to mock HTTP calls

## Data source

Weather data by [Open-Meteo](https://open-meteo.com) (free for non-commercial use; see their terms).