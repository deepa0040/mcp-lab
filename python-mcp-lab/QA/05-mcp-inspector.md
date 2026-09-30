# MCP Inspector — Python Notes

## 1. What is MCP Inspector?

**MCP Inspector** is a developer tool used to **test, debug, and inspect an MCP server**.

Think of it as a **UI/API testing tool for your MCP server**.

Instead of asking an AI client to call your MCP server, you can use Inspector to manually check:

* What **tools** are available
* What **resources** are available
* What **prompts** are available
* What arguments a tool expects
* Whether a tool executes correctly
* What response the MCP server returns
* Whether your MCP server is actually connecting correctly

### Simple architecture

```text
                  MCP Inspector
                       |
                       | MCP protocol
                       ↓
                 Python MCP Server
                       |
              ┌────────┴────────┐
              ↓                 ↓
            Tools            Resources
              ↓
          Python code
```

---

# 2. Why use MCP Inspector?

Suppose you created this Python MCP server:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Before connecting it to an AI application, you can use **MCP Inspector** to verify:

```text
MCP Server
    ↓
Does it start?
    ↓
Can Inspector connect?
    ↓
Does Inspector discover `add`?
    ↓
Can I provide a = 10, b = 20?
    ↓
Does it return 30?
```

This makes debugging much easier.

---

# 3. What can MCP Inspector inspect?

| MCP component              | What you can check                      |
| -------------------------- | --------------------------------------- |
| **Tools**                  | Available tools and their input schemas |
| **Resources**              | Available resources                     |
| **Prompts**                | Available prompt templates              |
| **Tool arguments**         | Required/optional parameters            |
| **Tool execution**         | Whether the tool works                  |
| **Responses**              | Returned result                         |
| **Server connection**      | Whether MCP server starts/connects      |
| **Protocol communication** | MCP requests/responses                  |

---

# 4. MCP Inspector with Python

For a Python MCP server, the common pattern is:

```bash
npx @modelcontextprotocol/inspector
```

Inspector provides a UI from which you can connect to your MCP server.

For a Python server using `uv`, you can configure Inspector to launch something conceptually like:

```bash
uv run main.py
```

or, depending on your project:

```bash
uv run python main.py
```

The important idea is:

```text
Inspector
   ↓
starts/connects to
   ↓
Python MCP server
```

---

# 5. Example Python MCP Server

Let's create a simple calculator.

### `main.py`

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

The server exposes two tools:

```text
add
multiply
```

---

# 6. Start MCP Inspector

From your project directory:

```bash
npx @modelcontextprotocol/inspector
```

You should get an Inspector interface.

The exact UI/options can change between Inspector versions, but the workflow is generally:

```text
Start Inspector
      ↓
Select/configure MCP server
      ↓
Connect
      ↓
Discover capabilities
      ↓
Select tool
      ↓
Provide arguments
      ↓
Execute
      ↓
Inspect response
```

---

# 7. What happens when Inspector connects?

Your Python MCP server advertises its capabilities.

For example:

```text
Tools
├── add
│   ├── a: integer
│   └── b: integer
│
└── multiply
    ├── a: integer
    └── b: integer
```

Inspector can discover this information from the MCP server.

This is important because MCP is **schema-driven**.

Your Python type hints:

```python
def add(a: int, b: int) -> int:
```

help describe the tool's expected input/output.

---

# 8. Testing a Tool

Suppose Inspector shows:

```text
Tool: add

Arguments:
a: integer
b: integer
```

You provide:

```text
a = 10
b = 20
```

Inspector sends an MCP tool call to the server.

Conceptually:

```text
Inspector
    |
    | tools/call
    | add(a=10, b=20)
    ↓
Python MCP Server
    |
    | Python function
    ↓
10 + 20
    |
    ↓
30
    |
    ↓
Inspector
```

You should see the returned result.

---

# 9. Inspector vs running the Python file

This distinction is important.

### Running the server

```bash
uv run main.py
```

means:

> Start my MCP server.

It doesn't necessarily provide a convenient way to manually explore and test all MCP capabilities.

### Running Inspector

```bash
npx @modelcontextprotocol/inspector
```

means:

> Start a tool that lets me interact with and inspect an MCP server.

So:

| Command                               | Purpose                       |
| ------------------------------------- | ----------------------------- |
| `uv run main.py`                      | Run MCP server                |
| `npx @modelcontextprotocol/inspector` | Start Inspector               |
| Inspector UI                          | Connect/test/debug MCP server |

---

# 10. Why `npx` is used here?

This connects to question about **`uv` vs `npm`**.

**`uv` runs your Python MCP server; `npx MCP Inspector` gives you a UI to inspect and test that server.**

`uv` is commonly used for your **Python project**:

```bash
uv run main.py
```

MCP Inspector is distributed as an **npm package**, so you commonly start it with:

```bash
npx @modelcontextprotocol/inspector
```

So you can have:

```text
Python MCP Server
        │
        │ managed/run with
        ↓
       uv
        │
        │
        ↓
   MCP Inspector
        │
        │ managed/run with
        ↓
       npm/npx
```

They are serving different purposes.

---

# 11. Inspector in the MCP development workflow

A useful workflow is:

```text
1. Write Python MCP server
           ↓
2. Define tools/resources/prompts
           ↓
3. Run server
           ↓
4. Open MCP Inspector
           ↓
5. Connect Inspector
           ↓
6. Check discovered capabilities
           ↓
7. Execute tools
           ↓
8. Check responses/errors
           ↓
9. Fix Python code
           ↓
10. Test again
           ↓
11. Connect to actual MCP client
```

---

# 12. Debugging example

Suppose you write:

```python
@mcp.tool()
def divide(a: int, b: int) -> float:
    return a / b
```

You test:

```text
a = 10
b = 0
```

The tool fails with a division-by-zero error.

Inspector helps you determine:

```text
MCP server connection       ✓
Tool discovery              ✓
Tool schema                 ✓
Tool invocation             ✓
Python function execution  ✗
```

This is useful because you can identify **where the problem is**.

---

# 13. Inspector vs MCP Client

Don't confuse these.

### MCP Inspector

Primarily a **development/testing/debugging tool**.

```text
Developer
    ↓
Inspector
    ↓
MCP Server
```

### MCP Client

An application that actually uses MCP servers.

For example:

```text
AI Application
      ↓
   MCP Client
      ↓
   MCP Server
      ↓
     Tool
```

Therefore:

|                           | MCP Inspector     | MCP Client      |
| ------------------------- | ----------------- | --------------- |
| Main purpose              | Testing/debugging | Using MCP       |
| Usually developer-facing  | Yes               | Not necessarily |
| Manually test tools       | Yes               | Depends         |
| Production application    | Usually no        | Yes             |
| Discover MCP capabilities | Yes               | Yes             |
| Execute tools             | Yes               | Yes             |

---

# 14. Important debugging areas

When your Python MCP server doesn't work, check these in order:

### 1. Server starts

```bash
uv run main.py
```

Does the Python application start without an exception?

### 2. Correct transport

For a local Inspector setup, your server configuration needs to match the transport Inspector expects.

For example:

```python
mcp.run(transport="stdio")
```

### 3. Dependencies

Check that MCP is installed in your environment:

```bash
uv add "mcp[cli]"
```

### 4. Tool definition

Check:

```python
@mcp.tool()
def add(a: int, b: int):
    return a + b
```

### 5. Input schema

Make sure Inspector sees the expected parameters:

```text
a → integer
b → integer
```

### 6. Tool execution

Test the actual function through Inspector.

---

# 15. Common mistake

A common misunderstanding is:

```bash
npx @modelcontextprotocol/inspector
```

does **not** magically turn your Python file into an MCP server.

You still need your MCP server:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")
```

Inspector is the **testing/debugging layer**.

```text
                MCP Inspector
                     │
                     │
                     ▼
              Python MCP Server
                     │
                     ▼
              Your Python logic
```

---

# 16. MCP Inspector — interview definition

> **MCP Inspector is a developer tool for testing and debugging MCP servers. It allows developers to connect to an MCP server, inspect its available tools, resources, and prompts, execute tools with test inputs, and inspect the returned results and errors.**

### Short version

> **MCP Inspector is like a testing/debugging UI for MCP servers.**

---

# 17. MCP Inspector vs Postman analogy

If you know Postman, this analogy is useful:

```text
REST API world
      ↓
    Postman
      ↓
Test API endpoints
```

Similar idea:

```text
MCP world
      ↓
MCP Inspector
      ↓
Test MCP server capabilities
```

But Inspector understands **MCP concepts**, such as:

```text
Tools
Resources
Prompts
MCP protocol
Tool schemas
Tool calls
```

---

## Quick revision

```text
MCP Inspector
│
├── Purpose
│   └── Test/debug MCP servers
│
├── Can inspect
│   ├── Tools
│   ├── Resources
│   ├── Prompts
│   ├── Schemas
│   └── Responses/errors
│
├── Python server
│   └── FastMCP
│
├── Python package management
│   └── uv
│
└── Inspector startup
    └── npx @modelcontextprotocol/inspector
```

**One-line memory trick:**
**`uv` runs your Python MCP server; `npx MCP Inspector` gives you a UI to inspect and test that server.**
