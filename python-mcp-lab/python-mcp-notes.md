# MCP with Python — Must-Know Commands & Syntax

> Quick reference for learning and building **Model Context Protocol (MCP) servers with Python**.

---

## 1. Python Environment

### Check Python Version

```bash
python --version
```

**When to use:**
Check which Python version is installed.

---

### Create Virtual Environment

```bash
python -m venv .venv
```

**When to use:**
Create an isolated Python environment for the project.

### Activate — Linux/macOS

```bash
source .venv/bin/activate
```

### Activate — Windows

```powershell
.venv\Scripts\activate
```

---

# 2. `uv` — Python Project & Package Manager

`uv` is a fast Python package and project manager commonly used in modern Python projects.

### Check Installation

```bash
uv --version
```

### Create a Project

```bash
uv init mcp-calculator
```

Creates a Python project.

```text
mcp-calculator/
├── pyproject.toml
├── README.md
└── main.py
```

### Create Virtual Environment

```bash
uv venv
```

### Add MCP Dependency

```bash
uv add mcp
```

### Add Another Python Package

```bash
uv add requests
```

```bash
uv add boto3
```

```bash
uv add httpx
```

### Run Python File

```bash
uv run main.py
```

### Important Difference

```text
uv add mcp
     ↓
Adds MCP as a project dependency

uv run main.py
     ↓
Runs the application using the project environment
```

---

# 3. Import MCP

A typical MCP server starts with:

```python
from mcp.server.fastmcp import FastMCP
```

Then create the server:

```python
mcp = FastMCP("Calculator")
```

### What does this mean?

```python
mcp = FastMCP("Calculator")
```

Creates an MCP server/application named `Calculator`.

---

# 4. Create an MCP Tool

The most important MCP syntax:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

### Breakdown

```python
@mcp.tool()
```

Registers the Python function as an **MCP tool**.

```python
def add(...)
```

Defines the Python function.

```python
a: int
```

`a` should be an integer.

```python
-> int
```

The function returns an integer.

```python
return a + b
```

The actual business logic.

---

# 5. Tool Description / Docstring

Give MCP tools a clear description:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b
```

### Why?

The AI/client needs to understand:

* What the tool does
* What inputs it accepts
* What result it produces

A good MCP tool should have:

```text
Tool name
    ↓
Description
    ↓
Input parameters
    ↓
Input types
    ↓
Result
```

---

# 6. Multiple MCP Tools

One MCP server can expose multiple tools.

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

Conceptually:

```text
                 MCP Server
                     |
          +----------+----------+
          |          |          |
          ↓          ↓          ↓
         add      subtract   multiply
```

---

# 7. Python Type Hints

MCP development frequently uses Python type hints.

### Integer

```python
def add(a: int, b: int) -> int:
```

### String

```python
def greet(name: str) -> str:
```

### Float

```python
def calculate(price: float) -> float:
```

### Boolean

```python
def check_status(enabled: bool) -> str:
```

### Example

```python
@mcp.tool()
def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello {name}"
```

### Why type hints matter in MCP

They help describe the expected tool input/output and allow the MCP framework to build an appropriate schema.

---

# 8. `if __name__ == "__main__"`

Common Python pattern:

```python
if __name__ == "__main__":
    mcp.run()
```

This means:

> Run the MCP server when this file is executed directly.

For example:

```bash
uv run main.py
```

will execute:

```python
mcp.run()
```

But if another Python file imports `main.py`, the server won't automatically start.

---

# 9. Start the MCP Server

Typical structure:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


if __name__ == "__main__":
    mcp.run()
```

Run:

```bash
uv run main.py
```

---

# 10. Synchronous vs Asynchronous Tools

## Synchronous

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

Use for simple operations that don't involve waiting for external resources.

Examples:

* Calculations
* String processing
* Simple transformations
* Local logic

---

## Asynchronous

```python
@mcp.tool()
async def get_user(user_id: int) -> str:
    result = await fetch_user(user_id)
    return result
```

### Important keywords

```python
async def
```

Defines an asynchronous function.

```python
await
```

Waits for an asynchronous operation.

### When to use async?

Useful for I/O operations such as:

* REST API calls
* Database queries
* Network operations
* Async file operations

---

# 11. Environment Variables

Never hard-code secrets.

### Bad

```python
api_key = "my-secret-key"
```

### Better

```python
import os

api_key = os.getenv("API_KEY")
```

Set environment variable on Linux/macOS:

```bash
export API_KEY="my-secret-key"
```

Check:

```bash
echo $API_KEY
```

For Windows PowerShell:

```powershell
$env:API_KEY="my-secret-key"
```

---

# 12. JSON

MCP deals heavily with structured data, so basic JSON knowledge is useful.

```python
import json
```

### Python → JSON

```python
json.dumps(data)
```

### JSON → Python

```python
json.loads(data)
```

Example:

```python
data = {
    "name": "Deepa",
    "role": "DevOps"
}

json_data = json.dumps(data)
```

> When using the MCP SDK, you normally do **not** manually construct MCP protocol messages. The SDK handles the protocol details.

---

# 13. Error Handling

Use Python's `try/except` when a tool can fail.

```python
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    try:
        return a / b
    except ZeroDivisionError:
        raise ValueError("Cannot divide by zero")
```

Basic pattern:

```python
try:
    # code that may fail
except Exception as e:
    # handle error
```

This becomes particularly important when MCP tools interact with:

* APIs
* Databases
* AWS
* Files
* External systems

---

# 14. MCP Inspector

**MCP Inspector** is useful for manually testing and inspecting an MCP server.

Conceptually:

```text
       MCP Server
           ↑
           |
     MCP Inspector
           |
           ↓
   Test MCP Tools
```

You can inspect things such as:

```text
Tools
 ├── add
 ├── subtract
 └── multiply

Input
 ├── a = 10
 └── b = 20

Result
 └── 30
```

The exact Inspector command can vary by MCP SDK/Inspector version, so use the version-specific MCP documentation when configuring it.

---

# 15. Testing Python MCP Tools

You can test the underlying Python function separately.

Example:

```python
def test_add():
    assert add(2, 3) == 5
```

Run a test file:

```bash
uv run test_main.py
```

### Important concept

There are two different things to test:

```text
Python logic
     ↓
Unit testing

MCP server/tool interface
     ↓
MCP Inspector / MCP client testing
```

---

# 16. Git Commands for MCP Projects

### Initialize repository

```bash
git init
```

### Check changes

```bash
git status
```

### Stage files

```bash
git add .
```

### Commit

```bash
git commit -m "Add calculator MCP server"
```

### Push

```bash
git push
```

---

# 17. Complete Minimal MCP Example

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


if __name__ == "__main__":
    mcp.run()
```

Run:

```bash
uv run main.py
```

---

# 18. MCP Python Cheat Sheet

| Command / Syntax   | Purpose                   | When to use              |
| ------------------ | ------------------------- | ------------------------ |
| `python --version` | Check Python              | Environment setup        |
| `uv --version`     | Check uv                  | Environment setup        |
| `uv init`          | Create project            | Start project            |
| `uv venv`          | Create environment        | Isolate dependencies     |
| `uv add mcp`       | Install MCP               | MCP project setup        |
| `uv add <package>` | Install package           | Add dependency           |
| `uv run main.py`   | Run application           | Start MCP server         |
| `import ...`       | Import module             | Use Python/MCP libraries |
| `FastMCP()`        | Create MCP server         | Server setup             |
| `@mcp.tool()`      | Register tool             | Expose function to AI    |
| `def`              | Define function           | Synchronous tool         |
| `async def`        | Async function            | I/O-heavy tool           |
| `await`            | Wait for async operation  | Async code               |
| `: int`, `: str`   | Type hint                 | Define input type        |
| `-> int`           | Return type               | Define output type       |
| `"""..."""`        | Docstring                 | Describe tool            |
| `mcp.run()`        | Start server              | Run MCP server           |
| `os.getenv()`      | Read environment variable | Config/secrets           |
| `try/except`       | Error handling            | Handle failures          |
| `json.dumps()`     | Python → JSON             | JSON conversion          |
| `json.loads()`     | JSON → Python             | JSON conversion          |
| MCP Inspector      | Inspect/test server       | MCP testing              |
| `git`              | Version control           | Store/share project      |

---

# 19. What You Actually Need to Memorize

Don't try to memorize everything.

### Level 1 — Must Know

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer")


@mcp.tool()
def my_tool(value: str) -> str:
    """Describe what the tool does."""
    return value


if __name__ == "__main__":
    mcp.run()
```

And:

```bash
uv init
uv add mcp
uv run main.py
```

### Level 2 — Understand

```python
async def
await
try
except
os.getenv()
```

### Level 3 — Learn as needed

```text
JSON
Pydantic
asyncio
HTTP clients
database libraries
AWS SDK
authentication
testing frameworks
MCP resources
MCP prompts
```

---

## 20. Mental Model

The most important thing to remember is:

```text
                    AI Application
                          |
                          |
                    MCP Protocol
                          |
                          ↓
                    MCP Server
                          |
             +------------+------------+
             |            |            |
             ↓            ↓            ↓
          Tool 1       Tool 2       Tool 3
             |            |            |
             ↓            ↓            ↓
          Python       Python       Python
          function     function     function
             |            |            |
             ↓            ↓            ↓
           API        Database       AWS
```

**MCP does not replace Python.**

Python contains your actual logic. MCP provides a standardized way for an AI application to discover and invoke that logic.

### Core syntax to remember

```text
FastMCP()
    ↓
@mcp.tool()
    ↓
Python function
    ↓
type hints + description
    ↓
mcp.run()
```

That is the foundation. Once this is comfortable, move on to **MCP Resources, Prompts, tool testing, and connecting an MCP server to an AI client**.
