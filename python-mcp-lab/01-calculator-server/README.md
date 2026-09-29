# Calculator MCP Server

A beginner-friendly MCP (Model Context Protocol) server written in Python. It exposes basic math operations so an AI assistant (such as Claude) can call them as tools instead of guessing at arithmetic.

## Aim / Objective

- Learn the core concepts of MCP by building the smallest useful server.
- Understand the three MCP building blocks in one small file:
  - **Tools**: actions the AI can call (`add`, `divide`, ...)
  - **Resources**: read-only data (`calc://constants`)
  - **Prompts**: reusable prompt templates (`explain_calculation`)
- Learn how to test a server with the MCP Inspector and connect it to a real client.
- Build a foundation for larger projects (Notes server, database explorer, and so on).

## What's Included

| Type | Name | Description |
|---|---|---|
| Tool | `add` | Returns a + b |
| Tool | `subtract` | Returns a - b |
| Tool | `multiply` | Returns a * b |
| Tool | `divide` | Returns a / b (error if b is 0) |
| Tool | `power` | Returns base raised to exponent |
| Tool | `sqrt` | Square root (error if negative) |
| Resource | `calc://constants` | Values of pi, e and tau |
| Prompt | `explain_calculation` | Solve an expression step by step using the tools |

## Architecture

```
+-------------------------+
|         User            |
|  "What is (12+8)*3 ?"   |
+------------+------------+
             |
             v
+-------------------------+
|   MCP Client / Host     |
|  (Claude Desktop, or    |
|   MCP Inspector)        |
+------------+------------+
             |  MCP protocol (JSON-RPC)
             |  over stdio (standard input/output)
             v
+-------------------------+
|   calculator_server.py  |
|   FastMCP("calculator") |
|                         |
|   Tools:     add, subtract, multiply,
|              divide, power, sqrt
|   Resource:  calc://constants
|   Prompt:    explain_calculation
+------------+------------+
             |
             v
     Python `math` module
```

**Flow of one request**

1. The user asks a question that needs math.
2. The client asks the server which tools exist and reads their descriptions.
3. The AI decides to call a tool, for example `add(a=12, b=8)`.
4. The server runs the Python function and returns `20.0`.
5. The AI uses the result in its answer.

## Project Structure

```
mcp-calculator/
├── calculator_server.py   # the MCP server (all the code)
└── README.md              # this file
```

(If you use uv, it also creates `pyproject.toml` and a `.venv` folder. If you use plain Python, you create the `.venv` folder yourself.)

## What Each Tool Does (Quick Glossary)

| Tool | Job |
|---|---|
| `python` | Runs your `.py` file |
| `venv` | A private toolbox of libraries for one project |
| `pip` | Installs libraries into that toolbox (comes with Python) |
| `uv` | A faster, all-in-one alternative to `venv` + `pip` (optional) |
| `npx` | Launches the MCP Inspector testing website (needs Node.js) |

## Prerequisites

- **Python 3.10 or higher**: check with `python --version` (on Mac/Linux you may need `python3`)
- **Node.js** (only for the Inspector): check with `node --version`. Install the LTS version from nodejs.org if missing.
- **uv** (only for Option B): check with `uv --version`

## Setup: choose ONE option

Both options end up in the same place: a project folder with the MCP library installed. Option A needs nothing beyond Python. Option B is shorter but requires installing `uv` first.

### Option A: Plain Python (venv + pip)

**1. Create the project folder and move into it**

```bash
mkdir mcp-calculator
cd mcp-calculator
```

Save `calculator_server.py` in this folder.

**2. Create a virtual environment**

```bash
python -m venv .venv
```

This makes a hidden `.venv` folder: a private toolbox for this project, so libraries do not affect the rest of your computer.

**3. Activate it**

- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

You should see `(.venv)` at the start of your terminal line. Repeat this step every time you open a new terminal.

> Windows PowerShell says "running scripts is disabled"? Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.

**4. Install the MCP library**

```bash
pip install "mcp[cli]<2"
```

- `mcp` is the library your code imports.
- `[cli]` adds extra command-line tools.
- `<2` means "any version below 2". This is important: version 2 renamed `FastMCP`, which this code uses.

**5. Check that the server starts**

```bash
python calculator_server.py
```

It will appear to do nothing. That is correct: it is waiting for a client. Press `Ctrl+C` to stop.

**6. Test with the Inspector**

```bash
npx @modelcontextprotocol/inspector python calculator_server.py
```

### Option B: uv

**1. Install uv (one time only)**

- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Mac/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Then **close the terminal and open a new one**, and confirm with `uv --version`. If you skip the new terminal, you will get the error `spawn uv ENOENT`.

**2. Create the project and install the library**

```bash
mkdir mcp-calculator
cd mcp-calculator
uv init
uv add "mcp[cli]<2"
```

- `uv init` creates a `pyproject.toml` file that tracks your project.
- `uv add` creates the `.venv` for you and installs the library into it. There is no manual activation step.

Save `calculator_server.py` in this folder.

**3. Check that the server starts**

```bash
uv run calculator_server.py
```

It will appear to do nothing. That is correct. Press `Ctrl+C` to stop. (`uv run` automatically uses the project's environment.)

**4. Test with the Inspector**

```bash
npx @modelcontextprotocol/inspector uv run calculator_server.py
```

### Side-by-side comparison

| Step | Option A: Python | Option B: uv |
|---|---|---|
| Install extra tool | none | install `uv` once |
| Create environment | `python -m venv .venv` | done automatically by `uv add` |
| Activate it | `source .venv/bin/activate` (or Windows equivalent) | not needed |
| Install library | `pip install "mcp[cli]<2"` | `uv add "mcp[cli]<2"` |
| Run server | `python calculator_server.py` | `uv run calculator_server.py` |
| Inspector command | `npx @modelcontextprotocol/inspector python calculator_server.py` | `npx @modelcontextprotocol/inspector uv run calculator_server.py` |

## Using the MCP Inspector

After running the Inspector command for your option, a browser page opens.

1. Click the toggle on the server card until it shows **Connected**.
2. **Tools** tab: click *List Tools*, pick `add`, enter `a = 2`, `b = 3`, and run it.
3. Run `divide` with `a = 1`, `b = 0` to see the error handling.
4. **Resources** tab: open `calc://constants`.
5. **Prompts** tab: try `explain_calculation` with `(2 + 3) * 4`.

Keep the terminal open while testing (closing it stops the Inspector). Press `Ctrl+C` in it when finished.

## Connect to Claude Desktop (optional)

Add one of the following to `claude_desktop_config.json`. Use full absolute paths, and fully restart Claude Desktop afterwards.

**Option A (plain Python).** Claude Desktop does not activate your virtual environment, so point straight at the Python inside `.venv`:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "/abs/path/mcp-calculator/.venv/bin/python",
      "args": ["/abs/path/mcp-calculator/calculator_server.py"]
    }
  }
}
```

On Windows the command is `C:\\abs\\path\\mcp-calculator\\.venv\\Scripts\\python.exe` (double the backslashes).

**Option B (uv):**

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uv",
      "args": ["--directory", "/abs/path/mcp-calculator", "run", "calculator_server.py"]
    }
  }
}
```

If Claude Desktop cannot find `uv`, replace `"uv"` with the full path to the uv program (find it with `which uv` on Mac/Linux or `where uv` on Windows).

Then ask Claude: *"Use the calculator to compute (12 + 8) * 3, then take the square root of the result."*

## Daily Routine (after first setup)

**Option A:**
```bash
cd mcp-calculator
source .venv/bin/activate        # Windows: .venv\Scripts\activate
npx @modelcontextprotocol/inspector python calculator_server.py
```

**Option B:**
```bash
cd mcp-calculator
npx @modelcontextprotocol/inspector uv run calculator_server.py
```

## Results

The server was tested with an MCP client that connected over stdio and called the tools directly.

| Test | Input | Result |
|---|---|---|
| List tools | none | `add`, `subtract`, `multiply`, `divide`, `power`, `sqrt` |
| `add` | a = 2, b = 3 | `5.0` |
| `divide` | a = 1, b = 0 | Error returned: `Cannot divide by zero.` |

Key takeaways:

- Ordinary Python functions become AI-callable tools with one decorator (`@mcp.tool()`).
- The function's **type hints** define the inputs, and its **docstring** tells the AI when to use it.
- Raised exceptions are passed back to the AI as readable tool errors instead of crashing the server.

## Troubleshooting

| Problem | Fix |
|---|---|
| `spawn uv ENOENT` in the Inspector | `uv` is not installed or the terminal was not reopened after installing. Install it (Option B, step 1) or switch to Option A. |
| `No module named 'mcp.server.fastmcp'` | You installed mcp 2.x. Run `pip install "mcp[cli]<2"` (or `uv add "mcp[cli]<2"`). |
| `No module named 'mcp'` | The environment is not active or the library is not installed. Activate `.venv` (Option A) or run `uv add "mcp[cli]<2"` (Option B). |
| `python` not found | Try `python3`, or install Python 3.10+ from python.org. |
| `npx` not found | Install Node.js (LTS) from nodejs.org and open a new terminal. |
| Inspector shows *Failed* | Check you are in the project folder and, for Option A, that `.venv` is active. |
| Claude Desktop does not show the tools | Use absolute paths in the config and fully restart the app. |

## Exercise

- Add more tools (`modulo`, `percentage`, `average`).
- Write tests that call the functions directly with `pytest`.