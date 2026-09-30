# MCP in Python — Quick Notes

These notes are designed for **beginner → hands-on → interview understanding**, especially if you're learning MCP by building small Python projects.

---

## 1. What is MCP?

**MCP = Model Context Protocol**

MCP is an open protocol that allows an AI application to connect with **external tools, data, and services** in a standardized way.

Think of it like:

```text
AI Application
      |
      | MCP
      |
+-----+----------+----------+
|                |          |
Calculator      Database   API
Tool            Tool       Tool
```

Instead of writing custom integration logic for every AI application, MCP provides a common way to expose capabilities.

### Simple example

Without MCP:

```text
LLM → custom Python code → Calculator API
```

With MCP:

```text
LLM
 |
MCP Client
 |
MCP Server
 |
Calculator Tool
```

---

# 2. MCP Architecture

The main components are:

| Component      | Meaning                                                    |
| -------------- | ---------------------------------------------------------- |
| **MCP Host**   | AI application such as Claude Desktop or another AI client |
| **MCP Client** | Component inside the host that connects to an MCP server   |
| **MCP Server** | Program that exposes tools/data to the client              |
| **Tool**       | Function the AI can invoke                                 |
| **Resource**   | Data/context exposed by the server                         |
| **Prompt**     | Reusable prompt template exposed by the server             |

Basic architecture:

```text
              MCP Host
          ┌───────────────┐
          │ AI Application│
          │               │
          │ MCP Client    │
          └───────┬───────┘
                  │
             MCP Protocol
                  │
          ┌───────▼───────┐
          │  MCP Server   │
          ├───────────────┤
          │ Tools         │
          │ Resources     │
          │ Prompts       │
          └───────────────┘
```

---

# 3. MCP Server in Python

A Python MCP server can expose Python functions as MCP tools.

A commonly used Python SDK is:

```text
mcp
```

You may see imports such as:

```python
from mcp.server.fastmcp import FastMCP
```

`FastMCP` provides a simpler way to create MCP servers.

---

# 4. Install MCP

Using normal `pip`:

```bash
pip install mcp
```

Using `uv`:

```bash
uv add mcp
```

For a project:

```bash
uv init
uv add mcp
```

Then:

```text
project/
├── pyproject.toml
├── uv.lock
└── main.py
```

---

# 5. What is `uv`?

`uv` is a **Python package and project manager**.

It can replace several traditional tools:

```text
pip
venv
pip-tools
virtualenv
```

For example:

```bash
uv init
```

creates a Python project.

```bash
uv add mcp
```

adds MCP as a dependency.

```bash
uv run main.py
```

runs the Python program using the project's environment.

Think:

```text
uv
│
├── Create project
├── Create/manage environment
├── Install dependencies
├── Lock dependencies
└── Run application
```

---

# 6. Your First MCP Server

Example:

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

The important parts are:

### Create server

```python
mcp = FastMCP("Calculator")
```

Creates an MCP server named `Calculator`.

### Create tool

```python
@mcp.tool()
```

This tells MCP:

> Expose this Python function as an MCP tool.

### Python function

```python
def add(a: int, b: int) -> int:
```

The function receives:

```text
a
b
```

and returns:

```text
a + b
```

---

# 7. What Does `@mcp.tool()` Do?

This is a **Python decorator**.

Normally:

```python
def add(a, b):
    return a + b
```

The function is only a normal Python function.

With:

```python
@mcp.tool()
def add(a, b):
    return a + b
```

the function becomes an **MCP tool** that the MCP client can discover and invoke.

Conceptually:

```text
Python function
      ↓
@mcp.tool()
      ↓
MCP Tool
      ↓
AI can discover/use it
```

---

# 8. Why Type Hints Matter

You will commonly see:

```python
def add(a: int, b: int) -> int:
```

Here:

```text
a: int
b: int
```

means inputs are integers.

```text
-> int
```

means the function returns an integer.

MCP can use this information when describing the tool's input/output schema.

For example, conceptually:

```json
{
  "name": "add",
  "input": {
    "a": "integer",
    "b": "integer"
  }
}
```

This helps the AI client understand how to call the tool.

---

# 9. Docstrings Matter Too

Example:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

The docstring helps describe the tool.

For a real project:

```python
@mcp.tool()
def get_weather(city: str) -> dict:
    """Get the current weather information for a city."""
```

The AI needs to understand **what the tool does**, not just its function name.

---

# 10. MCP Tools

A **Tool** is an action the AI can ask the MCP server to perform.

Examples:

```text
calculate_sum()
get_weather()
search_database()
create_ticket()
get_github_issue()
send_email()
query_metrics()
restart_service()
```

For your DevOps background, imagine:

```text
AI
 ↓
MCP
 ↓
AWS MCP Server
 ↓
get_ec2_status()
get_cloudwatch_metrics()
list_ecs_services()
```

---

# 11. Tools vs Resources vs Prompts

This is an important MCP concept.

| MCP Concept  | Purpose                       | Example                       |
| ------------ | ----------------------------- | ----------------------------- |
| **Tool**     | Perform an action             | `create_ticket()`             |
| **Resource** | Provide data/context          | `file://config.yaml`          |
| **Prompt**   | Provide reusable instructions | `generate_incident_summary()` |

Easy way to remember:

```text
Tool     → DO something
Resource → READ something
Prompt   → GUIDE the AI
```

---

# 12. Tool Example

```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

AI can conceptually request:

```text
multiply
a = 5
b = 10
```

Server executes:

```python
multiply(5, 10)
```

Result:

```text
50
```

---

# 13. Multiple Tools

One MCP server can expose multiple tools.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator")


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


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")

    return a / b


if __name__ == "__main__":
    mcp.run()
```

Architecture:

```text
Calculator MCP Server
│
├── add()
├── subtract()
├── multiply()
└── divide()
```

---

# 14. MCP Client vs MCP Server

This is one of the most important concepts.

### MCP Server

Provides capabilities.

```text
MCP Server
    ↓
Tools
Resources
Prompts
```

### MCP Client

Connects to the server.

```text
AI Application
      ↓
MCP Client
      ↓
MCP Server
```

For example:

```text
Claude Desktop
      │
      │ MCP Client
      ▼
Calculator MCP Server
      │
      ├── add
      ├── subtract
      └── multiply
```

---

# 15. MCP Transport

MCP needs a way for the client and server to communicate.

Common concepts you'll encounter include:

```text
stdio
Streamable HTTP
```

### stdio

Very useful for local MCP servers.

```text
MCP Client
   │
   │ stdin/stdout
   ▼
Python MCP Server
```

The client starts the Python process and communicates with it through standard input/output.

### HTTP

Useful when the MCP server is running as a network service.

```text
MCP Client
    |
 HTTP
    |
MCP Server
```

---

# 16. Running Your Python MCP Project

If your project uses `uv`:

```bash
uv run main.py
```

For example:

```text
mcp-calculator/
├── main.py
├── pyproject.toml
└── uv.lock
```

Run:

```bash
uv run main.py
```

---

# 17. Important Python Concepts for MCP

Before going deeper into MCP, understand these Python concepts:

| Python concept       | Why needed                           |
| -------------------- | ------------------------------------ |
| Functions            | MCP tools are functions              |
| Decorators           | `@mcp.tool()`                        |
| Type hints           | Tool input/output schema             |
| Docstrings           | Tool descriptions                    |
| Dictionaries         | Working with structured data         |
| JSON                 | MCP communication/data               |
| Exceptions           | Error handling                       |
| `async` / `await`    | Async MCP operations                 |
| Modules/imports      | Organizing MCP projects              |
| Virtual environments | Dependency isolation                 |
| `uv`                 | Python project/dependency management |

---

# 18. Synchronous vs Asynchronous Tools

Simple tool:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

For operations involving I/O, you may use asynchronous Python:

```python
@mcp.tool()
async def get_data() -> str:
    result = await some_operation()
    return result
```

Remember:

```text
def
 ↓
normal/synchronous function

async def
 ↓
asynchronous function

await
 ↓
wait for async operation
```

---

# 19. MCP + External API

One practical use case is exposing an API as an MCP tool.

Conceptually:

```text
AI
 ↓
MCP Client
 ↓
MCP Server
 ↓
Python Tool
 ↓
External API
```

Example:

```python
@mcp.tool()
def get_user(user_id: int):
    # call external API
    # return result
    ...
```

The AI doesn't need to understand how the API itself works.

It only needs to understand:

```text
get_user(user_id)
```

---

# 20. MCP + Database

Another common architecture:

```text
AI
 ↓
MCP
 ↓
Python MCP Server
 ↓
Database
```

Tools could be:

```python
search_customer()
get_order()
get_product()
```

For example:

```python
@mcp.tool()
def get_order(order_id: int):
    # query database
    ...
```

**Important:** In production, don't expose unrestricted SQL execution to an LLM without strong authorization, validation, and access controls.

---

# 21. MCP for DevOps

This is where MCP becomes particularly relevant to your background.

Imagine a DevOps MCP server:

```text
                    AI
                     |
                  MCP Client
                     |
             DevOps MCP Server
                     |
       +-------------+-------------+
       |             |             |
      AWS          Kubernetes     GitHub
       |             |             |
     EC2/ECS        EKS           Repo
    CloudWatch     Pods          Actions
```

Possible tools:

```text
get_ecs_service_status()
get_ecs_task_count()
get_cloudwatch_alarm()
list_kubernetes_pods()
get_pod_logs()
get_github_workflow_status()
```

Then an AI assistant could use these tools to investigate an incident.

---

# 22. MCP vs API

They are related but not identical.

| API                                     | MCP                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------ |
| General software-to-software interface  | Standardized interface for AI applications to interact with capabilities |
| Designed around application integration | Designed around AI context/tool interaction                              |
| Client must know API contract           | MCP provides standardized discovery/interaction                          |
| REST, GraphQL, gRPC etc.                | MCP protocol                                                             |

You can think of:

```text
REST API
    ↓
Python MCP Tool
    ↓
MCP
    ↓
AI application
```

MCP can therefore **wrap existing APIs and services**.

---

# 23. MCP Project Structure

For your calculator project, keep it simple:

```text
mcp-calculator/
│
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

As the project grows:

```text
mcp-calculator/
│
├── src/
│   └── calculator/
│       ├── __init__.py
│       ├── server.py
│       ├── tools.py
│       └── calculator.py
│
├── tests/
│   └── test_calculator.py
│
├── pyproject.toml
├── uv.lock
└── README.md
```

