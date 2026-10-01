# Local File Explorer MCP Server (Python)

A small, **read-only** [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that lets an AI app (like Claude Desktop) browse, read, and search files inside **one folder you choose**. Nothing outside that folder can be touched.

This is a learning project. It shows the two main things an MCP server can offer: **tools** and **resources**. It also shows how to keep file access **safe**.

---

## Table of Contents

1. [What is this?](#what-is-this)
2. [What you will learn](#what-you-will-learn)
3. [Features](#features)
4. [Project structure](#project-structure)
5. [Requirements](#requirements)
6. [Setup](#setup)
7. [Running and testing](#running-and-testing)
8. [Connecting to Claude Desktop](#connecting-to-claude-desktop)
9. [How it works](#how-it-works)
10. [Security notes](#security-notes)
11. [Troubleshooting](#troubleshooting)
12. [Ideas to extend](#ideas-to-extend)
13. [Glossary](#glossary)

---

## What is this?

MCP is a standard way for AI apps to connect to your data and tools. An **MCP server** is a small program that says: "Here is what I can do, and here is the data I can share."

This server exposes a folder on your computer in a **read-only** way. The AI can:

- list what is inside a folder
- read a text file
- search for text across files

It cannot write, delete, or rename anything.

## What you will learn

- The difference between **tools** and **resources** in MCP
- How to build an MCP server with Python's `FastMCP`
- How to prevent **path traversal** attacks (`../` escapes, symlink tricks)
- How to test a server with the **MCP Inspector**

## Features

| Type | Name | What it does |
|------|------|--------------|
| Tool | `list_dir` | Lists files and folders in a directory |
| Tool | `read_file` | Reads a text file (large files are truncated) |
| Tool | `search_files` | Searches file names and file contents (case-insensitive) |
| Resource | `file:///...` | Every text file under the root is listed as a resource |

**Tools vs resources, in one sentence:** tools are actions the *AI model* decides to call; resources are data the *app/user* picks to attach as context (like a file picker).

## Project structure

```
03-local-file-explorer-server/
├── server.py   # the whole server
└── README.md                 # this file
```

## Requirements

- Python **3.10 or newer**
- `pip`
- Node.js (only if you use the `npx` Inspector command)

Check your Python version:

```bash
python --version
```

## Setup

**1. Go to the project folder**

```bash
cd 03-local-file-explorer-server
```

**2. (Recommended) Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux / Codespaces
# .venv\Scripts\activate         # Windows
```

**3. Install the MCP SDK**

```bash
pip install "mcp[cli]>=2,<3"
```

> This project targets **mcp 2.x**, where `FastMCP` is called `MCPServer`. If you see `No module named 'mcp.server.fastmcp'`, see [Troubleshooting](#troubleshooting).

## Running and testing

The server needs to know **which folder is the root**. You can set it two ways:

- an environment variable: `EXPLORER_ROOT`
- a command-line argument: `python server.py /path/to/root`

If you set neither, the current folder is used.

### Option A: MCP Inspector (easiest for testing)

```bash
EXPLORER_ROOT=/path/to/some/folder mcp dev server.py
```

This opens the Inspector in your browser. Then:

1. Click **Connect**
2. Open the **Tools** tab and try `list_dir` with path `.`
3. Try `read_file` with a real file name
4. Try `search_files` with a word you know is in a file
5. Open the **Resources** tab to see the `file://` entries

### Option B: Run directly (stdio)

```bash
python server.py /path/to/some/folder
```

It will look like nothing happens. That is normal: the server is waiting for an MCP client to talk to it over stdin/stdout.

### Option C: Inspector with an argument

```bash
npx @modelcontextprotocol/inspector python server.py /path/to/some/folder
```

## Connecting to Claude Desktop

Add this to your Claude Desktop config file (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "files": {
      "command": "python",
      "args": [
        "/absolute/path/to/server.py",
        "/absolute/path/to/root/folder"
      ]
    }
  }
}
```

Use **absolute paths**, then fully restart Claude Desktop. If you use a virtual environment, set `"command"` to the full path of that venv's Python (for example `/path/to/.venv/bin/python`).

## How it works

```
 AI app (client)  <── stdio ──>  server.py  ──>  files under ROOT only
```

1. The client starts the server and asks what it offers.
2. The server replies with 3 tools and a list of resources.
3. When a tool is called, the server checks the path with `safe_path()`, then does the work.

Every request that includes a path goes through one function, `safe_path()`. This keeps the safety logic in one place.

## Security notes

`safe_path()` protects you by:

- **Rejecting absolute paths** like `/etc/passwd`
- **Resolving `..` and symlinks**, then checking the final path is still inside the root
- **Re-checking every file** during search and resource listing, so a symlink pointing outside the root is skipped

Other safeguards:

- Output size limits (200 KB per file read, 500 directory entries, 500 resources)
- Binary files are refused
- Noisy folders like `.git`, `node_modules`, and `.venv` are skipped during search

**Test it yourself.** In the Inspector, call `read_file` with:

- `../../etc/passwd` → should fail with "Path escapes the allowed root folder"
- `/etc/passwd` → should fail with "Absolute paths are not allowed"

> This is a learning project. Review and harden it before pointing it at sensitive data.

## Troubleshooting

### `Got unexpected extra argument(s) (/path/to/folder)`

**Cause:** `mcp dev` only accepts the server file, so an extra folder argument is rejected.

**Fix:** use the environment variable instead:

```bash
EXPLORER_ROOT=/path/to/folder mcp dev server.py
```

### `Root is not a directory: .../dev`

**Cause:** an older version of the script read the root from `sys.argv[1]`. Under `mcp dev`, that value is the CLI's own word `dev`.

**Fix:** use the latest `server.py`. It prefers the `EXPLORER_ROOT` environment variable and only accepts a command-line argument if it is a real directory.

### `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`

**Cause:** you have **mcp 2.x** installed, where `FastMCP` was renamed to `MCPServer` and moved to `mcp.server.mcpserver`. Older tutorials and code samples still use the 1.x names.

**Fix (this project already uses the 2.x names):**

```python
# mcp 1.x (old)
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("name")

# mcp 2.x (current)
from mcp.server.mcpserver import MCPServer
mcp = MCPServer("name")
```

Everything under `mcp.server.fastmcp.*` is now under `mcp.server.mcpserver.*`. The `@mcp.tool()` and `@mcp.resource()` decorators and `mcp.run()` work the same.

**Want to stay on 1.x instead?** Pin the version: `pip install "mcp[cli]<2"` and use the old imports.

Check which version you have with `pip show mcp`.

### `mcp: command not found`

**Cause:** the MCP CLI is not installed, or your virtual environment is not active.

**Fix:**

```bash
source .venv/bin/activate
pip install "mcp[cli]"
```

### `ModuleNotFoundError: No module named 'mcp'`

**Cause:** the package is installed in a different Python than the one running the script.

**Fix:** activate your venv and reinstall. Check with `which python` and `pip show mcp`.

### `Root is not a directory`

**Cause:** the root path is wrong or doesn't exist.

**Fix:** check the path with `ls /path/to/folder` and use the full path.

### Resources tab is empty or cluttered

- **Empty:** the root might contain only binary files, files larger than 200 KB, or no files at all.
- **Cluttered:** only the first 500 files are listed. Point the root at a smaller folder.

### `Path escapes the allowed root folder` for a normal file

**Cause:** the file is a symlink to somewhere outside the root, or your path has too many `..` parts.

**Fix:** use a path relative to the root, like `src/main.py`.

### Claude Desktop doesn't show the server

- Use absolute paths in the config
- Make sure the JSON is valid (no trailing commas)
- Fully quit and reopen Claude Desktop
- Use the venv's Python path as `"command"` if `mcp` is only installed there

### The server seems to hang when run directly

That is expected. stdio servers wait silently for a client. Use the Inspector to interact with it.

### Tip: don't `print()` in the server

With stdio transport, anything printed to stdout can corrupt the MCP messages. If you need debug output, print to stderr:

```python
import sys
print("debug message", file=sys.stderr)
```

## Ideas to extend

- Add a `file_info` tool (size, modified time, type)
- Let `read_file` take `start_line` and `end_line`
- Respect `.gitignore` in `search_files`
- Add a dynamic resource template instead of registering files at startup
- Add tests for `safe_path()` (traversal, symlinks, absolute paths)
- Add regex search

## Glossary

| Term | Meaning |
|------|---------|
| **MCP** | Model Context Protocol, a standard for connecting AI apps to tools and data |
| **Server** | The program that offers tools and resources (this project) |
| **Client** | The app that connects to the server (Claude Desktop, Inspector) |
| **Tool** | An action the AI can call, with arguments |
| **Resource** | Data identified by a URI that an app can read and attach as context |
| **stdio** | Communication through standard input/output, the default transport here |
| **Path traversal** | An attack that uses `../` or symlinks to reach files outside an allowed folder |
| **Inspector** | A browser-based tool for testing MCP servers |